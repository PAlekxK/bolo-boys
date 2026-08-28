#!/usr/bin/env python3
"""Regenerate each event's `google_calendar_url` from its canonical time.

WHY THIS EXISTS. `google_calendar_url` was hand-authored per event, while
`time` and `duration_hours` are canonical and every other time surface (.ics,
JSON-LD, the site card, the Bandsintown CSV) is *derived* from them. A
hand-authored copy of a derived value is a second source of truth, and it
drifted exactly as you would expect: measured 2026-08-02, six of ten events
carried an ALL-DAY link (`dates=20260829/20260830`, no time component) and five
of those said "Time TBD" in the description — while `time` said 6:00 PM and the
site card, the .ics and the 7/31 band email all agreed on 6:00 PM.

That is the same drift the 2026-08-01 three-way review found in the Google
Calendar invites (OPEN-THREADS GAP 2), in a surface the review did not check.

WHERE IT SHOWS UP — smaller than it first looks, and worth saying plainly so
nobody re-raises it as an emergency. `index.html` renders
`ev.ics_url || ev.google_calendar_url`, and .ics wins for every event that has
one, which is all ten public events. So the bad URLs were NOT being served to
fans. The live consumer is `bolo-private/tools/sync-band-sheet.py`, which
writes the field into the band's Google Sheet in a column next to Time — where
an all-day link sat beside a 6:00 PM time, for the band to read.

The fix is not to correct the six values. It is to stop storing an
independently-authored answer to a question `time` already answers.

Imports `event_window` / `event_summary` from events-to-ics.py rather than
recomputing the Eastern-offset math: two tools deriving one show's start time
from the same fields is how they come to disagree.

  python3 tools/events-to-gcal-urls.py --check   # exit 1 if out of date
  python3 tools/events-to-gcal-urls.py           # rewrite events.json
"""

import importlib.util
import json
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVENTS_PATH = ROOT / "data" / "events.json"
VENUES_PATH = ROOT / "data" / "venues.json"
GCAL_BASE = "https://calendar.google.com/calendar/render"


def _load_ics_module():
    spec = importlib.util.spec_from_file_location(
        "events_to_ics", Path(__file__).resolve().parent / "events-to-ics.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ics = _load_ics_module()


def build_url(event, venue):
    """Google Calendar TEMPLATE link, timed and absolute.

    UTC 'Z' stamps rather than a floating local time, for the same reason the
    .ics uses them: a fan who travels still gets the right moment, and an
    Eastern device still shows the intended wall clock.
    """
    dtstart, dtend = ics.event_window(event)
    params = {
        "action": "TEMPLATE",
        "text": ics.event_summary(event),
        "dates": f"{dtstart}/{dtend}",
        "location": venue["address"],
        "details": (event.get("invitation_text")
                    or f"Bolo Boys live at {event['venue_name']}."),
    }
    return f"{GCAL_BASE}?{urllib.parse.urlencode(params)}"


def main():
    check_only = "--check" in sys.argv

    events_data = json.loads(EVENTS_PATH.read_text())
    venues_by_id = {v["id"]: v
                    for v in json.loads(VENUES_PATH.read_text())["venues"]}
    events = events_data["events"]

    desired = {}
    for ev in events:
        # Unlisted cards get no public link, and an event with no time cannot
        # have a timed one. Both currently describe private-event-2026-10-08,
        # which carries null for both fields already.
        if ev.get("unlisted") or not ev.get("time"):
            desired[ev["id"]] = None
            continue
        venue = venues_by_id.get(ev["venue_id"])
        if not venue or not venue.get("address"):
            raise SystemExit(
                f"Event {ev['id']!r}: venue {ev['venue_id']!r} has no address")
        desired[ev["id"]] = build_url(ev, venue)

    changed = [ev["id"] for ev in events
               if ev.get("google_calendar_url") != desired[ev["id"]]]

    if check_only:
        if changed:
            print(f"google_calendar_url is out of date ({len(changed)}):")
            for eid in changed:
                print(f"  - {eid}")
            return 1
        print(f"ok: google_calendar_url already in sync ({len(events)} events).")
        return 0

    for ev in events:
        ev["google_calendar_url"] = desired[ev["id"]]

    # indent=2 + ensure_ascii=False: matches events-to-ics.py's write-back so
    # the file round-trips byte-identically, and so em-dashes in
    # invitation_text stay em-dashes instead of becoming —.
    EVENTS_PATH.write_text(
        json.dumps(events_data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    print(f"Rewrote google_calendar_url for {len(changed)} of {len(events)} "
          f"event(s) from canonical time + duration_hours.")
    for eid in changed:
        print(f"  - {eid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
