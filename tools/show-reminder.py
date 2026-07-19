#!/usr/bin/env python3
"""
show-reminder.py — scheduled prep reminder for upcoming Bolo Boys shows.

WHAT IT IS: the scheduler in front of tools Paul already owns. `/show-prep` and
`show-weather.py` both answer questions well; both only fire when he remembers to
fire them. His words for the friction: "remove the friction of having to look this
stuff up always." This is that.

CHECKPOINTS: T-7, T-3, T-1, T-0 (morning of).
  T-7  prep completeness -- setlist still open? invite unsent? poster due?
  T-3  the venue conversation. The ONLY checkpoint bounded by another human's
       reply time, so the only one that is genuinely unrecoverable later.
  T-1  what to pack. Weather is the headline here.
  T-0  the power-down call. The only checkpoint where the forecast is reliable.
(T-2 was deliberately CUT: it named no decision T-3 or T-1 didn't serve better.)

DETERMINISTIC AND AI-FREE. No model composes this body. Nobody is awake at 08:00
to catch a bad model read, and this task already produced a 4x error once (a
6-hour QPF block read as hourly). Every line here is a rendering of JSON or of
show-weather.py's own thresholds.

THE TRIGGER IS INVERTED ON PURPOSE. It does NOT ask "is today T-7?" It asks "for
each show, what is the most urgent checkpoint that has been REACHED and not yet
SENT?" Same answer on a normal day; completely different when the Mac was closed.
The naive version loses a missed T-3 forever. This one sends it late, correctly
labelled. That inversion -- not a freshness check -- is what makes a missed run a
non-event.

IDEMPOTENCE keys on (event_id, checkpoint), never on a date. Date-keying re-fires
every reminder the moment a show is rescheduled.

FAILURE SURFACING: the invariant is UNMET OBLIGATION, not recency. Copying the
icloud-backup freshness check ("did it run in 2 days?") would scream constantly,
because between shows this job is CORRECTLY idle for weeks -- and a check that
false-alarms is a check you stop reading, which is how both the 17-day deploy
freeze and the 3-day backup gap survived. Heartbeat what the job OWES, not when
it last ran. See tools/check-show-reminders.sh.

USAGE
  python3 tools/show-reminder.py              # send anything owed, then exit
  python3 tools/show-reminder.py --dry-run    # show what WOULD send, record nothing
  python3 tools/show-reminder.py --owed       # list unmet obligations, exit 1 if any
  python3 tools/show-reminder.py --force T-3 --event <id>   # re-send one, ignores state

EXIT 0 nothing owed / all sent · 1 a send failed · 2 bad args
"""

import argparse, json, subprocess, sys, os
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parent.parent
ET = ZoneInfo("America/New_York")
STATE = REPO / "tools" / ".reminder-state.json"
OUTDIR = REPO / ".reminders"
CHECKPOINTS = [0, 1, 3, 7]          # days out; most urgent first
KEYCHAIN_SERVICE = "bolo-reminder-smtp"
MAILTO = "paul.kirschenbauer@gmail.com"
WEATHER_HORIZON = 7                  # show-weather.py refuses past this


# ---------------------------------------------------------------- state

def read_state():
    if not STATE.exists():
        return {"sent": [], "last_run": None}
    try:
        return json.loads(STATE.read_text())
    except Exception:
        # A corrupt state file must not wedge the job. Re-sending a reminder is a
        # far smaller harm than never sending one again.
        print("WARN: state file unreadable, treating as empty", file=sys.stderr)
        return {"sent": [], "last_run": None}


def write_state(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2) + "\n")


def key(event_id, cp):
    return f"{event_id}|T-{cp}"


# ---------------------------------------------------------------- data

def load_events():
    d = json.loads((REPO / "data" / "events.json").read_text())
    return d if isinstance(d, list) else d.get("events", [])


def load_venue(vid):
    d = json.loads((REPO / "data" / "venues.json").read_text())
    vl = d if isinstance(d, list) else d.get("venues", [])
    return next((v for v in vl if v.get("id") == vid), {})


def is_outdoor(ev, venue):
    """Outdoor-ish: a logistics note mentions patio/outdoor, or it's a festival."""
    if venue.get("type") == "festival":
        return True
    notes = " ".join(n.get("text", "") for n in ev.get("prep", {}).get("logistics_notes", []))
    return any(w in notes.lower() for w in ("patio", "outdoor", "outside", "weather"))


def days_out(ev, today):
    return (datetime.strptime(ev["date"], "%Y-%m-%d").date() - today).days


def owed(events, state, today):
    """[(event, checkpoint)] -- most urgent REACHED and UNSENT checkpoint per show.

    'Reached' means days_out <= cp, not == cp. That is the whole point: a T-3 that
    was missed because the Mac was closed is still owed at T-2, and gets sent then.
    """
    out = []
    for ev in events:
        d = days_out(ev, today)
        if d < 0:
            continue
        for cp in CHECKPOINTS:                    # 0,1,3,7 -- most urgent first
            if d <= cp and key(ev["id"], cp) not in state["sent"]:
                out.append((ev, cp, d))
                break                              # one reminder per show per run
    return out


# ---------------------------------------------------------------- content

def prep_block(ev):
    """Deterministic read of the prep object. Returns (lines, n_open)."""
    p = ev.get("prep") or {}
    lines, n = [], 0
    ss = p.get("setlist_status")
    if ss:
        url = p.get("setlist_url")
        mark = "OK " if ss == "locked" else "-> "
        lines.append(f"{mark}Setlist: {ss}" + (f" ({url})" if url else " - no link"))
        if ss != "locked":
            n += 1
    lg = p.get("logistics_notes") or []
    undone = [g for g in lg if not g.get("done")]
    if lg:
        lines.append(f"{'-> ' if undone else 'OK '}Logistics: {len(lg)-len(undone)}/{len(lg)} done")
        for g in undone:
            lines.append(f"     [ ] {g.get('text','')}")
        n += len(undone)
    oq = [q for q in (p.get("open_questions") or []) if not q.get("resolved")]
    for q in oq:
        lines.append(f"-> Open question ({q.get('for','?')}): {q.get('text','')}")
    n += len(oq)
    lm = p.get("lifecycle_markers") or {}
    miss = [k.replace("_", " ") for k, v in lm.items() if not v]
    if miss:
        lines.append(f"-> Not yet: {', '.join(miss)}")
        n += len(miss)
    sg = [s for s in (p.get("subgroups") or []) if not s.get("ready")]
    for s in sg:
        lines.append(f"-> Subgroup not ready: {s.get('name','')}")
        n += len(sg)
    return (lines or ["OK Nothing outstanding."], n)


def weather_block(ev, d):
    """(lines, ok). A failed weather leg must NEVER suppress the prep reminder --
    show-weather.py fails loud by design and that design must not cascade into
    silence one layer up."""
    if d > WEATHER_HORIZON:
        return ([f"   (no forecast past T-{WEATHER_HORIZON} -- too early to mean anything)"], True)
    try:
        r = subprocess.run([sys.executable, str(REPO / "tools" / "show-weather.py"),
                            "--event", ev["id"], "--json"],
                           capture_output=True, text=True, timeout=90)
        if r.returncode != 0:
            return ([f"   !! weather fetch failed (exit {r.returncode}) -- {r.stderr.strip().splitlines()[0] if r.stderr.strip() else 'unknown'}",
                     "   Run: python3 tools/show-weather.py --event " + ev["id"]], False)
        w = json.loads(r.stdout)
    except Exception as e:
        return ([f"   !! weather leg errored ({type(e).__name__}) -- prep reminder still valid"], False)

    if w.get("too_early") or w.get("past"):
        return (["   (outside forecast window)"], True)

    L = [f"   {w['bucket']} - {w['bucket_why']}"]
    pn = [r_["pop_nws"] for r_ in w.get("rows", []) if r_.get("pop_nws") is not None]
    po = [r_["pop_om"] for r_ in w.get("rows", []) if r_.get("pop_om") is not None]
    if pn and po:
        # Compare each source's PEAK to the other's peak. An earlier version showed
        # min(all)..max(all), which silently blended the HOURLY range with the MODEL
        # spread -- "14-43%" looked like disagreement when it was mostly just the
        # forecast falling across the evening. The spread that matters for a decision
        # is between the two models at their respective worst hour.
        a, b = max(pn), max(po)
        gap = abs(a - b)
        L.append(f"   Peak rain odds - NWS {a}% / Open-Meteo {b}%"
                 + ("  SPLIT" if gap >= 20 else "  AGREED"))
        if gap >= 20:
            L.append(f"   {gap}pt gap. We take the wetter read ({max(a,b)}%), which is what")
            L.append("   sets the call above. Re-run near load-in.")
    L.append(f"   Total rain {w['qpf_total']:.2f}\"  |  peak feels-like {w['feels_max']:.0f}F")
    if w.get("thunder_nws") or w.get("thunder_om"):
        who = "both sources" if (w["thunder_nws"] and w["thunder_om"]) else \
              ("NWS only" if w["thunder_nws"] else "Open-Meteo only")
        L.append(f"   THUNDER ({who}) - this is a powered-gear call, not a wetness call.")
    for f in w.get("alerts", []):
        pr = f["properties"]
        L.append(f"   NWS {pr['event']}: {pr.get('headline','')}")
    return (L, True)


def compose(ev, cp, d):
    venue = load_venue(ev.get("venue_id", ""))
    pl, n_open = prep_block(ev)
    outdoor = is_outdoor(ev, venue)
    wl, wok = weather_block(ev, d) if outdoor else ([], True)

    focus = {7: "Prep completeness - what still has a deadline.",
             3: "The venue conversation. Ask now; they need time to answer.",
             1: "What to pack. Weather is the headline.",
             0: "Show day. Safety and the last look at the sky."}[cp]

    when = "TODAY" if d == 0 else ("TOMORROW" if d == 1 else f"in {d} days")
    subject = f"T-{cp} - {ev['date']} {ev.get('venue_name','')} ({when})"
    if outdoor and wl:
        subject += f" - {wl[0].strip().split(' -')[0]}"

    B = [subject, "=" * len(subject), "",
         f"{ev.get('day_of_week','')} {ev['date']} - {ev.get('time','')} - "
         f"{ev.get('venue_name','')} ({ev.get('venue_neighborhood','')})"]
    if ev.get("supporting_acts"):
        B.append(f"With: {', '.join(ev['supporting_acts'])}")
    B += ["", f"WHY THIS CHECKPOINT: {focus}", ""]
    B += ["PREP", *[f"   {x}" for x in pl], ""]
    if outdoor:
        B += ["WEATHER (outdoor)", *wl, ""]
    if cp == 0:
        B += ["Forecast moves inside the hour. Re-run before you leave:",
              f"   cd ~/Developer/bolo-boys && python3 tools/show-weather.py --event {ev['id']}", ""]
    B += ["Full board:  /show-prep", f"Weather only: python3 tools/show-weather.py --event {ev['id']}"]
    return subject, "\n".join(B), n_open, wok


# ---------------------------------------------------------------- delivery

def keychain_password():
    try:
        r = subprocess.run(["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
                           capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None
    except Exception:
        return None


def send_email(subject, body):
    """Dormant until the Keychain entry exists. Returns (attempted, ok, note)."""
    pw = keychain_password()
    if not pw:
        return (False, True, "email skipped (no Keychain entry -- see --help)")
    try:
        import smtplib
        from email.message import EmailMessage
        m = EmailMessage()
        m["Subject"] = f"[Bolo] {subject}"
        m["From"] = MAILTO
        m["To"] = MAILTO
        m.set_content(body)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as s:
            s.login(MAILTO, pw)
            s.send_message(m)
        return (True, True, "emailed")
    except Exception as e:
        return (True, False, f"EMAIL FAILED: {type(e).__name__}: {e}")


def write_report(ev, cp, subject, body):
    OUTDIR.mkdir(parents=True, exist_ok=True)
    f = OUTDIR / f"{ev['date']}_{ev['id']}_T-{cp}.txt"
    f.write_text(body + "\n")
    latest = OUTDIR / "latest.txt"
    latest.write_text(body + "\n")
    return f


def notify(subject, has_open):
    """Local echo. Matches the osascript pattern already used by read-mom-funnel."""
    try:
        t = subject.replace('"', "'")
        subprocess.run(["osascript", "-e",
                        f'display notification "{t}" with title "Bolo Boys show prep"'],
                       capture_output=True, timeout=10)
    except Exception:
        pass


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--owed", action="store_true", help="list unmet obligations; exit 1 if any")
    ap.add_argument("--force", help="checkpoint to re-send, e.g. T-3")
    ap.add_argument("--event", help="event id (with --force)")
    a = ap.parse_args()

    today = datetime.now(ET).date()
    events, state = load_events(), read_state()

    if a.force:
        if not a.event:
            print("--force needs --event", file=sys.stderr); sys.exit(2)
        cp = int(a.force.lstrip("T-").lstrip("-"))
        ev = next((e for e in events if e["id"] == a.event), None)
        if not ev:
            print(f"no event {a.event}", file=sys.stderr); sys.exit(2)
        todo = [(ev, cp, days_out(ev, today))]
    else:
        todo = owed(events, state, today)

    if a.owed:
        if not todo:
            print("nothing owed")
            sys.exit(0)
        for ev, cp, d in todo:
            print(f"OWED  T-{cp}  {ev['date']}  {ev.get('venue_name','')}  (show is T-{d})")
        sys.exit(1)

    if not todo:
        state["last_run"] = datetime.now(ET).isoformat()
        if not a.dry_run:
            write_state(state)
        sys.exit(0)                      # silent: nothing owed is the normal case

    failed = False
    for ev, cp, d in todo:
        subject, body, n_open, wok = compose(ev, cp, d)
        if a.dry_run:
            print(body); print("\n" + "-" * 60 + "\n")
            continue
        path = write_report(ev, cp, subject, body)
        attempted, ok, note = send_email(subject, body)
        notify(subject, n_open > 0)
        if attempted and not ok:
            failed = True
            print(f"{note}", file=sys.stderr)
        # Record only when nothing hard-failed. A weather leg that failed still
        # counts as sent -- the prep reminder was the point and it went out.
        if not (attempted and not ok):
            # SUPERSEDE. Sending checkpoint `cp` also retires every LESS urgent
            # checkpoint for this show. Without this, a show at T-0 has all four
            # checkpoints simultaneously "reached", so the next run fires T-1,
            # then T-3, then T-7 -- four reminders for one show, arriving in
            # reverse order of usefulness. A T-3 "ask the venue" nudge is moot
            # once the T-0 has gone out.
            # This preserves the late-send property that motivated the whole
            # inverted trigger: a Mac closed through T-3 that wakes at T-2 still
            # has T-3 as its most-urgent REACHED checkpoint (2 <= 3, and T-1/T-0
            # are not yet reached), so it sends T-3 correctly, just late.
            for later in [c for c in CHECKPOINTS if c >= cp]:
                k = key(ev["id"], later)
                if k not in state["sent"]:
                    state["sent"].append(k)
        print(f"T-{cp} {ev['date']} {ev.get('venue_name','')} -> {path.name} ({note})")

    state["last_run"] = datetime.now(ET).isoformat()
    if not a.dry_run:
        write_state(state)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
