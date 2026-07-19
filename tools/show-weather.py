#!/usr/bin/env python3
"""
show-weather.py — outdoor-show weather report for a Bolo Boys gig.

WHY THIS EXISTS: most Bolo shows are outdoor patios. The band needs to know,
before load-in, three things a generic forecast app buries: how hot it will
actually feel while hauling gear, whether they'll get rained on during the set
specifically (not "today"), and whether there's lightning — which is a safety
call about powered gear, not a comfort call about getting wet.

DETERMINISTIC AND AI-FREE (per ~/.claude/CLAUDE.md: capture/log paths stay
deterministic; AI lives on the ask path). Every judgment here is a documented
threshold over fetched numbers. No model reads the weather.

TWO SOURCES, DELIBERATE DIVISION OF LABOR — see .engineering/2026-07-19-path-show-weather.md:
  - NWS (api.weather.gov)  : ALERTS ONLY are authoritative. NWS *issues* a Heat
                             Advisory; it does not forecast that someone else
                             will. Open-Meteo has no US alert product at all.
                             Also used for its plain-English thunder wording.
  - Open-Meteo             : hourly QPF (precip AMOUNT), apparent temperature,
                             sunset. NWS publishes QPF only in ragged 1-6 HOUR
                             BLOCKS in the raw gridpoint product -- misreading
                             those as hourly overstated a forecast by 4x on
                             2026-07-19, which is why amount comes from here.
  - BOTH                   : precipitation probability, reported side by side.
                             NEVER averaged -- averaging fabricates a number
                             neither model produced. Disagreement is information.

USAGE
  python3 tools/show-weather.py                       # next upcoming show
  python3 tools/show-weather.py --event side-saddle-2026-07-19
  python3 tools/show-weather.py --date 2026-07-19
  python3 tools/show-weather.py --json               # machine-readable

EXIT CODES
  0 ok · 1 fetch/parse failure (FAILS LOUD -- see below) · 2 bad args

FAILS LOUD ON PURPOSE: a partial report that silently dropped the alert check
is the dangerous output, because "no alerts" and "alert check failed" look
identical to a reader. If either source errors, this exits non-zero and says
which leg failed rather than printing a confident-looking half report.
"""

import argparse, json, sys, urllib.request, urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# NWS documents a User-Agent requirement (it wants a contact for abuse reports).
# Uses the BAND's published address, not Paul's personal one -- this file is in
# the public repo, and band.json already names this as the public contact.
UA = "bolo-boys-weather (boloboysband@gmail.com)"
ET = timezone(timedelta(hours=-4))  # America/New_York, EDT
FORECAST_HORIZON_DAYS = 7

# --- Thresholds. All rain/heat judgments live HERE, nowhere else. ------------
# Rain buckets evaluate over the SHOW WINDOW = load-in (t-1h) .. load-out
# (t + duration + 0.5h). Load-in matters as much as the set: that's when the
# gear is uncovered and moving.
RAIN_BUCKETS = [
    # (label, pop_max_min, qpf_total_min)  -- first match wins, OR semantics
    ("CALL IT", 71, 0.15),
    ("LIKELY",  41, 0.04),
    ("WATCH",   21, 0.01),
]
HEAT_SUPPLEMENT = 103   # our own read, NOT an NWS product. See print_heat().
HOT_SET = 95
COLD_SET = 50
GUST_WATCH = 20
# WMO codes: 95 thunderstorm, 96/99 thunderstorm with hail.
THUNDER_CODES = {95, 96, 99}


def die(msg, code=1):
    print(f"\nFAILED: {msg}", file=sys.stderr)
    print("No partial report printed -- a half report reads like a whole one.", file=sys.stderr)
    sys.exit(code)


def get(url, label):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/geo+json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except Exception as e:
        die(f"{label} fetch failed ({type(e).__name__}: {e})")


def load(name):
    try:
        return json.loads((REPO / "data" / name).read_text())
    except Exception as e:
        die(f"could not read data/{name}: {e}")


def pick_event(args):
    d = load("events.json")
    evs = d if isinstance(d, list) else d.get("events", [])
    if args.event:
        m = [e for e in evs if e.get("id") == args.event]
        if not m:
            die(f"no event with id '{args.event}'", 2)
        return m[0]
    if args.date:
        m = [e for e in evs if e.get("date") == args.date]
        if not m:
            die(f"no event on {args.date}", 2)
        return m[0]
    today = datetime.now(ET).strftime("%Y-%m-%d")
    up = sorted([e for e in evs if e.get("date", "") >= today], key=lambda e: e["date"])
    if not up:
        die("no upcoming events in events.json", 2)
    return up[0]


def venue_coords(vid):
    d = load("venues.json")
    vl = d if isinstance(d, list) else d.get("venues", [])
    m = [v for v in vl if v.get("id") == vid]
    if not m:
        die(f"venue '{vid}' not in venues.json")
    v = m[0]
    if v.get("lat") is None or v.get("lon") is None:
        die(f"venue '{vid}' has no lat/lon. Backfill it -- do NOT geocode at "
            f"runtime; a show forecast must not fail because a geocoder is down.")
    return v


def show_window(ev):
    """(start, end) datetimes in ET. Load-in t-1h .. load-out t+duration+0.5h."""
    t = (ev.get("time") or "6:00 PM").strip()
    try:
        hm = datetime.strptime(t, "%I:%M %p")
    except ValueError:
        hm = datetime.strptime("6:00 PM", "%I:%M %p")
    d = datetime.strptime(ev["date"], "%Y-%m-%d")
    start = datetime(d.year, d.month, d.day, hm.hour, hm.minute, tzinfo=ET)
    dur = ev.get("duration_hours") or 3
    return start - timedelta(hours=1), start + timedelta(hours=dur) + timedelta(minutes=30), start


def fetch_nws(lat, lon):
    pt = get(f"https://api.weather.gov/points/{lat},{lon}", "NWS points")
    props = pt.get("properties") or die("NWS points returned no properties")
    hourly = get(props["forecastHourly"], "NWS hourly")
    alerts = get(f"https://api.weather.gov/alerts/active?point={lat},{lon}", "NWS alerts")
    return props, hourly["properties"]["periods"], alerts.get("features", [])


def fetch_om(lat, lon, date):
    url = ("https://api.open-meteo.com/v1/forecast"
           f"?latitude={lat}&longitude={lon}"
           "&hourly=temperature_2m,apparent_temperature,precipitation_probability,"
           "precipitation,weather_code,wind_gusts_10m"
           "&daily=sunset&temperature_unit=fahrenheit&precipitation_unit=inch"
           "&wind_speed_unit=mph&timezone=America%2FNew_York"
           f"&start_date={date}&end_date={date}")
    return get(url, "Open-Meteo")


def rain_bucket(pop_max, qpf_total, thunder):
    if thunder:
        return "CALL IT", "thunder in the window (hard override -- not a wetness call)"
    for label, pmin, qmin in RAIN_BUCKETS:
        if (pop_max is not None and pop_max >= pmin) or qpf_total >= qmin:
            why = []
            if pop_max is not None and pop_max >= pmin:
                why.append(f"PoP {pop_max}% >= {pmin}%")
            if qpf_total >= qmin:
                why.append(f'QPF {qpf_total:.2f}" >= {qmin}"')
            return label, " or ".join(why)
    return "DRY", f'PoP <= 20% and QPF < 0.01" ({qpf_total:.2f}")'


def build(ev, args):
    v = venue_coords(ev["venue_id"])
    lat, lon = v["lat"], v["lon"]
    win_start, win_end, downbeat = show_window(ev)

    days_out = (datetime.strptime(ev["date"], "%Y-%m-%d").date() - datetime.now(ET).date()).days
    if days_out > FORECAST_HORIZON_DAYS:
        return {"too_early": True, "event": ev, "venue": v, "days_out": days_out}
    if days_out < 0:
        return {"past": True, "event": ev, "venue": v, "days_out": days_out}

    props, periods, alerts = fetch_nws(lat, lon)
    om = fetch_om(lat, lon, ev["date"])
    oh = om["hourly"]

    rows = []
    for i, tstr in enumerate(oh["time"]):
        t = datetime.fromisoformat(tstr).replace(tzinfo=ET)
        if not (win_start <= t < win_end):
            continue
        nws = next((p for p in periods
                    if datetime.fromisoformat(p["startTime"]).astimezone(ET).replace(minute=0) == t), None)
        rows.append({
            "time": t,
            "temp": oh["temperature_2m"][i],
            "feels": oh["apparent_temperature"][i],
            "pop_om": oh["precipitation_probability"][i],
            "pop_nws": (nws or {}).get("probabilityOfPrecipitation", {}).get("value"),
            "qpf": oh["precipitation"][i],
            "code": oh["weather_code"][i],
            "gust": oh["wind_gusts_10m"][i],
            "sky": (nws or {}).get("shortForecast", ""),
        })
    if not rows:
        die("no forecast hours overlap the show window -- check the event time/date")

    pops = [p for r in rows for p in (r["pop_om"], r["pop_nws"]) if p is not None]
    pop_max = max(pops) if pops else None
    qpf_total = sum(r["qpf"] for r in rows)
    thunder_om = any(r["code"] in THUNDER_CODES for r in rows)
    thunder_nws = any("thunder" in (r["sky"] or "").lower() for r in rows)
    bucket, why = rain_bucket(pop_max, qpf_total, thunder_om or thunder_nws)
    wettest = max(rows, key=lambda r: r["qpf"])

    return {
        "event": ev, "venue": v, "days_out": days_out,
        "window": (win_start, win_end), "downbeat": downbeat,
        "rows": rows, "alerts": alerts,
        "nws_updated": periods[0]["startTime"] if periods else None,
        "grid": f"{props['gridId']} {props['gridX']},{props['gridY']}",
        "sunset": om["daily"]["sunset"][0],
        "pop_max": pop_max, "qpf_total": qpf_total,
        "thunder_om": thunder_om, "thunder_nws": thunder_nws,
        "bucket": bucket, "bucket_why": why,
        "wettest": wettest,
        "feels_max": max(r["feels"] for r in rows),
        "gust_max": max(r["gust"] for r in rows),
    }


def render(R):
    ev, v = R["event"], R["venue"]
    head = f"{ev.get('venue_name', v['name'])} - {ev['date']} ({ev.get('day_of_week','')}) {ev.get('time','')}"
    print("=" * 68)
    print(f"  SHOW WEATHER - {head}")
    print("=" * 68)

    if R.get("too_early"):
        print(f"\n  T-{R['days_out']} days. No rain call past T-{FORECAST_HORIZON_DAYS}.")
        print("  A 14-day PoP has the authority of data without the accuracy.")
        print("  Re-run inside a week.\n")
        return
    if R.get("past"):
        print(f"\n  This show was {abs(R['days_out'])} days ago. For what they actually")
        print("  played through, backfill observed conditions from the ERA5 archive.\n")
        return

    ws, we = R["window"]
    print(f"  {v.get('neighborhood','')} | {v['lat']}, {v['lon']} | NWS grid {R['grid']}")
    print(f"  Window: {ws.strftime('%-I:%M %p')} load-in -> {we.strftime('%-I:%M %p')} load-out"
          f"  (downbeat {R['downbeat'].strftime('%-I:%M %p')})")
    if v.get("geo", {}).get("source", "").endswith("approx"):
        print(f"  NOTE: venue coords are APPROXIMATE ({v['geo']['note'][:60]}...)")

    # --- alerts: authoritative, verbatim, first ---
    print("\n  OFFICIAL NWS ALERTS")
    if not R["alerts"]:
        print("    none active for this point")
    for f in R["alerts"]:
        p = f["properties"]
        print(f"    [{p['severity']}] {p['event']}")
        print(f"      {p.get('headline','')}")
        print(f"      ends {p.get('ends') or p.get('expires')}")

    # --- hourly ---
    print(f"\n  {'ET':<8}{'temp':<7}{'feels':<7}{'PoP nws/om':<13}{'QPF':<8}{'gust':<7}sky")
    print("  " + "-" * 64)
    for r in R["rows"]:
        pn = f"{r['pop_nws']}%" if r["pop_nws"] is not None else "-"
        po = f"{r['pop_om']}%" if r["pop_om"] is not None else "-"
        mark = " <" if r is R["wettest"] and r["qpf"] > 0 else ""
        print(f"  {r['time'].strftime('%-I%p').lower():<8}{r['temp']:<7.0f}{r['feels']:<7.0f}"
              f"{pn+'/'+po:<13}{r['qpf']:<8.3f}{r['gust']:<7.0f}{r['sky'][:20]}{mark}")

    # --- rain verdict ---
    print(f"\n  RAIN: {R['bucket']}")
    print(f"    {R['bucket_why']}")
    print(f"    window total {R['qpf_total']:.2f}\" | peak hour "
          f"{R['wettest']['time'].strftime('%-I%p').lower()} at {R['wettest']['qpf']:.3f}\"")
    if R["wettest"]["time"] < R["downbeat"]:
        print("    ^ peak lands during LOAD-IN, not the set")
    if R["thunder_nws"] != R["thunder_om"]:
        src = "NWS only" if R["thunder_nws"] else "Open-Meteo only"
        print(f"    THUNDER DISAGREEMENT: {src}. Override fires on either -- but")
        print("    know it is one source, not two.")
    elif R["thunder_nws"]:
        print("    THUNDER: both sources. Powered gear on an open patio is the")
        print("    risk here, not getting wet. Have a power-down plan.")

    # --- heat ---
    print(f"\n  HEAT: peak feels-like {R['feels_max']:.0f}F")
    if R["feels_max"] >= HEAT_SUPPLEMENT:
        print(f"    >= {HEAT_SUPPLEMENT}F -- advisory territory. NOTE: this line is")
        print("    OUR read, not an NWS product. NWS heat criteria are county-")
        print("    specific; if they issued one it is printed above, verbatim.")
    elif R["feels_max"] >= HOT_SET:
        print(f"    >= {HOT_SET}F -- hot set. Water before you play. Keep amps out")
        print("    of direct sun.")
    elif R["feels_max"] <= COLD_SET:
        print(f"    <= {COLD_SET}F -- cold. Tuning drift, cold fingers.")
    if R["gust_max"] >= GUST_WATCH:
        print(f"\n  WIND: gusts to {R['gust_max']:.0f} mph -- mic stands, cymbals, banner.")

    print(f"\n  Sunset {datetime.fromisoformat(R['sunset']).strftime('%-I:%M %p')}", end="")
    if datetime.fromisoformat(R["sunset"]).replace(tzinfo=ET) < R["window"][1]:
        print(" -- you lose light before load-out.")
    else:
        print()
    print()


def main():
    ap = argparse.ArgumentParser(description="Weather report for a Bolo Boys show.")
    ap.add_argument("--event", help="event id from events.json")
    ap.add_argument("--date", help="YYYY-MM-DD")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()
    R = build(pick_event(args), args)
    if args.json:
        def enc(o):
            return o.isoformat() if isinstance(o, datetime) else str(o)
        print(json.dumps(R, default=enc, indent=2))
    else:
        render(R)


if __name__ == "__main__":
    main()
