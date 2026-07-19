#!/usr/bin/env python3
"""
render-card.py — render a show-weather report as an HTML card.

VISUAL GRAMMAR is not invented here. It is lifted from Paul's own two codebases
per his brief ("look at Bolo Boys' website, look at Fernwood tracker... nice and
clean, but no bubbles, everything earns its place"). Spec + the grammar audit:
.ux-reviews/2026-07-19-show-weather-card-v2-visual-grammar.json

The rules that actually constrain this file:
  - ONE serif value per surface (Georgia), at a size nothing else approaches.
    Whatever wears it IS the headline. Bolo uses Georgia exactly once on the
    whole site (the band name); Fernwood uses Crimson Text on its header and the
    one lead number. It is scarce and high-voltage -- spending it on the wrong
    value crowns the wrong thing.
  - NO filled status chips. Bolo's only pill is an OUTLINE used for actions,
    never for state. Fernwood tried color-coded source blocks and RETREATED --
    viewer.html:1354 keeps the classes "for backwards compat but visually
    unified. Source identity is conveyed by ... not by color."
  - No traffic lights, no decorative icons, no color carrying a verdict.
    Color is one green family, spent on eyebrow labels and rules only.
  - Emphasis comes from POSITION, WEIGHT and SIZE. Nothing else.

CHECKPOINT FLEX: one layout, two axes -- not four layouts.
  Axis 1, confidence is typographic: the serif verdict GROWS as the show nears
    (T-7 none at all -> T-3 40px -> T-1/T-0 56px). A T-7 rain call is barely
    earned, so it does not get to wear the hero. The reader learns the
    confidence gradient by the fourth read without ever being taught it.
  Axis 2, which block leads: spread at distance, packing detail at T-1, safety
    at T-0.
  At T-0 WITH THUNDER the hero changes CATEGORY, not just value -- it becomes
    the power-down call and the rain bucket demotes to a sans line. Justified by
    the path doc: thunder is deliberately not proportionate.

NO DELTA LINE in v0. The spec's "T-3 read: LIKELY, trending drier" needs a cache
of the prior checkpoint, which reopens the no-persistence decision. Per the
spec's own zero-persistence fallback: drop it rather than approximate it, since
a half-remembered "it looked wetter yesterday" is the exact staleness failure
the whole design avoids.

USAGE
  python3 tools/render-card.py --event <id> [--checkpoint 0|1|3|7] [--out FILE]
  python3 tools/render-card.py --event <id> --demo-quiet   # also emit a DRY-night card
"""

import argparse, html, json, subprocess, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")

REPO = Path(__file__).resolve().parent.parent
OUT_DEFAULT = REPO / ".reminders" / "card.html"

CSS = """
:root{
  --green:#3A5F2A; --green-dark:#2D4B1E; --cream:#F8F4ED; --white:#FFFFFF;
  --charcoal:#2C2B28; --gray:#6B6560; --divider:#E5DDD0;
}
/* A local file opened in macOS dark mode must not get force-inverted --
   the whole grammar depends on a warm light ground. */
html{color-scheme:light;}
*{box-sizing:border-box;}
body{background:var(--cream);color:var(--charcoal);margin:0;padding:28px 16px 56px;
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  line-height:1.6;-webkit-font-smoothing:antialiased;}
.card{background:var(--white);border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.07);
  max-width:680px;margin:0 auto 28px;padding:26px 26px 22px;}
.eyebrow{font-size:.68rem;text-transform:uppercase;letter-spacing:.16em;
  font-weight:700;color:var(--green);margin:0 0 4px;}
.eyebrow.mute{color:var(--gray);}
.ident{font-size:.95rem;color:var(--charcoal);margin:0 0 2px;font-weight:600;}
.ident .sub{font-weight:400;color:var(--gray);}
hr{border:0;border-top:1px solid var(--divider);margin:18px 0;}
/* THE scarce serif. Exactly one per card. */
.verdict{font-family:Georgia,'Times New Roman',serif;color:var(--green-dark);
  line-height:1.02;margin:6px 0 2px;font-weight:400;}
.v-56{font-size:56px;} .v-40{font-size:40px;} .v-none{font-size:22px;font-weight:600;
  font-family:-apple-system,BlinkMacSystemFont,sans-serif;color:var(--charcoal);}
.consequence{font-size:1rem;color:var(--charcoal);margin:2px 0 0;max-width:46ch;}
.demoted{font-size:.95rem;color:var(--charcoal);margin:10px 0 0;}
.row{display:flex;gap:26px;flex-wrap:wrap;margin:14px 0 0;}
.metric .n{font-size:1.45rem;font-weight:600;line-height:1.15;}
.metric .l{font-size:.68rem;text-transform:uppercase;letter-spacing:.14em;
  color:var(--gray);font-weight:700;}
.note{font-size:.85rem;color:var(--gray);margin:8px 0 0;max-width:52ch;}
/* Quotation grammar: an NWS alert is an IMPORTED artifact, not authored here.
   Left rule + inset + attribution -- a grammar every reader already owns. */
.quote{border-left:3px solid var(--green);padding:2px 0 2px 14px;margin:16px 0 0;}
.quote .body{font-size:.95rem;color:var(--charcoal);}
.quote .attr{font-size:.72rem;color:var(--gray);margin-top:4px;}
table{width:100%;border-collapse:collapse;margin:10px 0 0;font-size:.86rem;
  font-variant-numeric:tabular-nums;}
th{text-align:left;font-size:.64rem;text-transform:uppercase;letter-spacing:.12em;
  color:var(--gray);font-weight:700;padding:0 0 6px;border-bottom:1px solid var(--divider);}
td{padding:6px 0;border-bottom:1px solid var(--divider);}
tr:last-child td{border-bottom:0;}
td.now{font-weight:600;}
details{margin:14px 0 0;} summary{cursor:pointer;font-size:.68rem;text-transform:uppercase;
  letter-spacing:.16em;font-weight:700;color:var(--green);list-style:none;}
summary::-webkit-details-marker{display:none;}
summary::after{content:" +";} details[open] summary::after{content:" \\2212";}
.foot{font-size:.72rem;color:var(--gray);margin:18px 0 0;}
@media(max-width:520px){.v-56{font-size:40px;}.v-40{font-size:32px;}.row{gap:18px;}}
"""

CONSEQUENCE = {
    "CALL IT": "Assume you will be interrupted. Have a plan for the gear.",
    "LIKELY":  "Bring cover for the gear. Ask the venue what happens if it opens up.",
    "WATCH":   "Keep an eye on it. Nothing to do yet.",
    "DRY":     "Nothing to plan around.",
}
FOCUS = {7: "Prep completeness — what still has a deadline.",
         3: "The venue conversation. Ask now; they need time to answer.",
         1: "What to pack.",
         0: "Show day. Safety, and the last look at the sky."}


def e(s):
    return html.escape(str(s))


def get_weather(event_id):
    r = subprocess.run([sys.executable, str(REPO / "tools" / "show-weather.py"),
                        "--event", event_id, "--json"],
                       capture_output=True, text=True, timeout=90)
    if r.returncode != 0:
        return None, (r.stderr.strip().splitlines() or ["unknown"])[0]
    return json.loads(r.stdout), None


def render_card(W, cp, ev):
    """One card. cp drives BOTH the serif size and which block leads."""
    thunder = W.get("thunder_nws") or W.get("thunder_om")
    bucket = W["bucket"]
    feels = W["feels_max"]
    hot = feels >= 95

    # --- Axis 1: the serif size IS the confidence claim -----------------
    vclass = {7: "v-none", 3: "v-40", 1: "v-56", 0: "v-56"}[cp]

    # --- Axis 2 + the category switch at T-0 with thunder ---------------
    if cp == 0 and thunder:
        hero, consequence = "Power-down plan", \
            "Thunder in the window. This is a call about powered gear on an open patio, not about getting wet."
        demoted = f"Rain: {bucket.title()} · peak feels-like {feels:.0f}°"
    elif hot and cp in (0, 1):
        hero, consequence = f"{feels:.0f}° and {'wet' if bucket in ('CALL IT','LIKELY') else 'dry'}", \
            ("Load-in is the hard part. Water before you play, and keep the amps out of direct sun."
             if bucket == "DRY" else CONSEQUENCE[bucket])
        demoted = f"Rain: {bucket.title()}" + ("  ·  thunder in the window" if thunder else "")
    else:
        hero = bucket.title() if bucket != "CALL IT" else "Call it"
        consequence = CONSEQUENCE[bucket]
        demoted = f"Peak feels-like {feels:.0f}°" + ("  ·  thunder in the window" if thunder else "")

    P = []
    P.append('<div class="card">')
    P.append(f'<p class="eyebrow">T&#8209;{cp} &nbsp;·&nbsp; {e(FOCUS[cp])}</p>')
    P.append(f'<p class="ident">{e(ev.get("venue_name",""))} '
             f'<span class="sub">— {e(ev.get("day_of_week",""))} {e(ev["date"])}, {e(ev.get("time",""))}</span></p>')
    P.append("<hr>")

    # verbatim alert sits ABOVE our own verdict: the authority outranks the house read
    for f in W.get("alerts", []):
        pr = f["properties"]
        P.append('<div class="quote"><div class="body">'
                 f'<strong>{e(pr["event"])}</strong><br>{e(pr.get("headline",""))}</div>'
                 f'<div class="attr">Issued by the National Weather Service · verbatim</div></div>')

    P.append(f'<p class="verdict {vclass}">{e(hero)}</p>')
    P.append(f'<p class="consequence">{e(consequence)}</p>')
    P.append(f'<p class="demoted">{e(demoted)}</p>')

    # metrics: feels-like only. Ambient temp is deliberately CUT -- showing both
    # invites a "which one is real" pause, and only one drives a decision.
    pn = [r["pop_nws"] for r in W["rows"] if r.get("pop_nws") is not None]
    po = [r["pop_om"] for r in W["rows"] if r.get("pop_om") is not None]
    a, b = (max(pn) if pn else None), (max(po) if po else None)
    P.append('<div class="row">')
    P.append(f'<div class="metric"><div class="n">{feels:.0f}°</div><div class="l">Feels like</div></div>')
    if a is not None and b is not None:
        P.append(f'<div class="metric"><div class="n">{a}% / {b}%</div>'
                 f'<div class="l">Rain odds · NWS / Open&#8209;Meteo</div></div>')
    P.append(f'<div class="metric"><div class="n">{W["qpf_total"]:.2f}&Prime;</div><div class="l">Total rain</div></div>')
    P.append("</div>")

    # The tie-break, in words. Without this the card shows 0.00" under a LIKELY
    # headline and reads as broken -- which is more damaging than the two numbers.
    if a is not None and b is not None and abs(a - b) >= 20:
        P.append(f'<p class="note">The two models disagree by {abs(a-b)} points. We take the wetter '
                 f'read — the {max(a,b)}% is what sets the call above. Re-run near load-in.</p>')
    elif thunder and not (W.get("thunder_nws") and W.get("thunder_om")):
        who = "NWS" if W.get("thunder_nws") else "Open-Meteo"
        P.append(f'<p class="note">Thunder comes from {who} only; the other source does not see it. '
                 f'The call fires on either, but know it is one source.</p>')

    wet = W.get("wettest") or {}
    if wet.get("qpf", 0) > 0:
        t = datetime.fromisoformat(wet["time"]).strftime("%-I%p").lower()
        loadin = " — that lands during load&#8209;in" if datetime.fromisoformat(wet["time"]) < datetime.fromisoformat(W["downbeat"]) else ""
        P.append(f'<p class="note">Wettest hour {t}, {wet["qpf"]:.2f}&Prime;{loadin}.</p>')

    # Open-Meteo returns a NAIVE local sunset; the window bounds were serialized
    # tz-aware. Attach the zone rather than stripping the offset -- the naive
    # side is the one missing information.
    sunset = datetime.fromisoformat(W["sunset"]).replace(tzinfo=ET)
    P.append(f'<p class="note">Sunset {sunset.strftime("%-I:%M %p")}'
             + (" — you lose light before load-out." if sunset < datetime.fromisoformat(W["window"][1]) else ".") + "</p>")

    # repository layer: the hourly table is LAST and folded away
    P.append("<details><summary>Hour by hour</summary>")
    P.append("<table><tr><th>Hour</th><th>Feels</th><th>Rain odds</th><th>Rain</th><th>Gusts</th></tr>")
    for r in W["rows"]:
        t = datetime.fromisoformat(r["time"]).strftime("%-I%p").lower()
        pn_ = f'{r["pop_nws"]}%' if r.get("pop_nws") is not None else "—"
        po_ = f'{r["pop_om"]}%' if r.get("pop_om") is not None else "—"
        P.append(f'<tr><td>{t}</td><td>{r["feels"]:.0f}°</td><td>{pn_} / {po_}</td>'
                 f'<td>{r["qpf"]:.2f}&Prime;</td><td>{r["gust"]:.0f}</td></tr>')
    P.append("</table></details>")

    P.append('<p class="foot">Rain call and the 103° heat line are Bolo thresholds, not NWS products. '
             'Official alerts, if any, are quoted above unaltered.<br>'
             f'Pulled {datetime.now().strftime("%-I:%M %p")} · forecasts move inside the hour.</p>')
    P.append("</div>")
    return "\n".join(P)


def page(cards, title):
    return (f"<!doctype html><html><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{e(title)}</title><style>{CSS}</style></head><body>\n"
            + "\n".join(cards) + "\n</body></html>\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--event", required=True)
    ap.add_argument("--checkpoint", type=int, default=None)
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--all-checkpoints", action="store_true",
                    help="render T-7/T-3/T-1/T-0 stacked, to compare the flex")
    a = ap.parse_args()

    d = json.loads((REPO / "data" / "events.json").read_text())
    evs = d if isinstance(d, list) else d.get("events", [])
    ev = next((x for x in evs if x["id"] == a.event), None)
    if not ev:
        print(f"no event {a.event}", file=sys.stderr); sys.exit(2)

    W, err = get_weather(a.event)
    if err:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(page([
            '<div class="card"><p class="eyebrow mute">Weather unavailable</p>'
            f'<p class="verdict v-none">Could not reach the forecast</p>'
            f'<p class="consequence">{e(err)}</p>'
            '<p class="note">Shown as a failure on purpose. A card that renders '
            'blank where the alert would be is indistinguishable from a card that '
            'checked and found nothing.</p></div>'], "Weather unavailable"))
        print(f"wrote failure card -> {a.out}"); sys.exit(1)

    cps = [7, 3, 1, 0] if a.all_checkpoints else [a.checkpoint if a.checkpoint is not None
                                                 else max(0, (datetime.strptime(ev["date"], "%Y-%m-%d").date()
                                                              - datetime.now().date()).days)]
    cps = [c if c in (0, 1, 3, 7) else min([x for x in (0, 1, 3, 7) if x >= c] or [7]) for c in cps]
    cards = [render_card(W, c, ev) for c in cps]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(page(cards, f"{ev.get('venue_name','')} — show weather"))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
