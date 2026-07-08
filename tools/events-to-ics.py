#!/usr/bin/env python3
"""Generate a per-event .ics file from data/events.json + data/venues.json.

Why this exists: on an iPhone (the at-show QR-scan majority), tapping a served
.ics file opens the native Apple Calendar "Add Event" sheet in place — no Google
account, no browser detour, and it lands in the calendar the fan actually checks.
The Google Calendar template URL does none of those things for a non-Google user.
So each event gets a real static .ics served as text/calendar, and the event's
`ics_url` field (previously always null) is populated to point at it.

Writes:
  - assets/ics/<event-id>.ics for every current event
  - data/events.json with each event's `ics_url` set to "assets/ics/<id>.ics"
  - prunes orphaned assets/ics/*.ics files that no longer match a current event

Idempotent: DTSTAMP is derived deterministically from the event date (not the
wall clock), so re-running produces byte-identical files and no spurious diff.

Usage:
    python3 tools/events-to-ics.py         # writes .ics files + events.json in place
    python3 tools/events-to-ics.py --check # exits non-zero if anything would change

Run from the public repo root.

NOTE: the time/timezone/address helpers below intentionally mirror
tools/events-to-jsonld.py (the JSON-LD generator). Keep the two in step if the
Eastern-DST approximation or the address format ever changes.
"""
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EVENTS_PATH = REPO_ROOT / "data" / "events.json"
VENUES_PATH = REPO_ROOT / "data" / "venues.json"
ICS_DIR = REPO_ROOT / "assets" / "ics"
ICS_URL_PREFIX = "assets/ics"  # relative path stored in events.json (matches poster_url)
SITE_URL = "https://www.boloboys.band"
PRODID = "-//Bolo Boys//boloboys.band//EN"


def load_json(path):
    with path.open() as f:
        return json.load(f)


def parse_time(time_str):
    """'11:00 AM' -> (11, 0); '8:00 PM' -> (20, 0). Mirrors events-to-jsonld.py."""
    m = re.match(r"^(\d{1,2}):(\d{2})\s*(AM|PM)$", time_str.strip(), re.IGNORECASE)
    if not m:
        raise ValueError(f"Cannot parse time: {time_str!r}")
    hour = int(m.group(1)) % 12
    if m.group(3).upper() == "PM":
        hour += 12
    return hour, int(m.group(2))


def tz_offset_minutes(d):
    """US Eastern offset in minutes: EDT (-240) roughly Mar 8 – Nov 1, else EST (-300).

    Same approximation the JSON-LD generator uses (documented in CLAUDE.md) —
    close enough for the dates Bolo Boys actually plays.
    """
    if (d.month, d.day) >= (3, 8) and (d.month, d.day) < (11, 2):
        return -240
    return -300


def to_utc_stamp(d, hour, minute):
    """Eastern wall-clock -> absolute UTC 'YYYYMMDDTHHMMSSZ'.

    Absolute (UTC) rather than floating local time so a fan who travels still
    gets the correct moment; an Eastern device shows the intended wall-clock.
    """
    total = hour * 60 + minute - tz_offset_minutes(d)  # local -> UTC
    day = d
    while total >= 24 * 60:
        total -= 24 * 60
        day = day + timedelta(days=1)
    while total < 0:
        total += 24 * 60
        day = day - timedelta(days=1)
    uh, um = divmod(total, 60)
    return f"{day.strftime('%Y%m%d')}T{uh:02d}{um:02d}00Z"


def escape_text(value):
    """RFC 5545 TEXT escaping: backslash, semicolon, comma, newline."""
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
        .replace("\r", "\\n")
    )


def fold(line):
    """Fold a content line to <=75 octets per RFC 5545 (continuation = CRLF + space)."""
    raw = line.encode("utf-8")
    if len(raw) <= 75:
        return line
    out = []
    chunk = b""
    for ch in line:
        enc = ch.encode("utf-8")
        # 74 to leave room for the leading space on continuation lines
        if len(chunk) + len(enc) > 74:
            out.append(chunk.decode("utf-8"))
            chunk = enc
        else:
            chunk += enc
    out.append(chunk.decode("utf-8"))
    return "\r\n ".join(out)


def build_ics(event, venue):
    event_date = date.fromisoformat(event["date"])
    hour, minute = parse_time(event["time"])
    duration = event.get("duration_hours", 2)

    dtstart = to_utc_stamp(event_date, hour, minute)

    total_minutes = hour * 60 + minute + round(duration * 60)
    end_hour, end_minute = divmod(total_minutes, 60)
    end_date = event_date
    while end_hour >= 24:
        end_date = end_date + timedelta(days=1)
        end_hour -= 24
    dtend = to_utc_stamp(end_date, end_hour, end_minute)

    summary = f"Bolo Boys at {event['venue_name']}"
    if event.get("theme"):
        summary += f" — {event['theme']}"

    description = event.get("invitation_text") or f"Bolo Boys live at {event['venue_name']}."

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:{PRODID}",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:{event['id']}@boloboys.band",
        # Deterministic DTSTAMP (event-date midnight UTC) keeps the file idempotent.
        f"DTSTAMP:{event_date.strftime('%Y%m%d')}T000000Z",
        f"DTSTART:{dtstart}",
        f"DTEND:{dtend}",
        f"SUMMARY:{escape_text(summary)}",
        f"DESCRIPTION:{escape_text(description)}",
        f"LOCATION:{escape_text(venue['address'])}",
        f"URL:{SITE_URL}",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return "\r\n".join(fold(l) for l in lines) + "\r\n"


def main():
    check_only = "--check" in sys.argv

    events_data = load_json(EVENTS_PATH)
    venues_data = load_json(VENUES_PATH)
    venues_by_id = {v["id"]: v for v in venues_data["venues"]}

    events = events_data["events"]
    would_change = []

    # Build the target state: {filename: content} + the ics_url each event should carry.
    targets = {}
    for ev in events:
        venue = venues_by_id.get(ev["venue_id"])
        if not venue:
            raise SystemExit(f"Event {ev['id']!r} references unknown venue_id {ev['venue_id']!r}")
        if not venue.get("address"):
            raise SystemExit(f"Venue {ev['venue_id']!r} has no address — cannot build .ics LOCATION")
        filename = f"{ev['id']}.ics"
        targets[filename] = build_ics(ev, venue)
        desired_url = f"{ICS_URL_PREFIX}/{filename}"
        if ev.get("ics_url") != desired_url:
            would_change.append(f"events.json: {ev['id']} ics_url -> {desired_url}")

    # Detect .ics content drift. Read with newline="" so CRLF is preserved and
    # the comparison isn't defeated by universal-newline translation on read.
    for filename, content in targets.items():
        path = ICS_DIR / filename
        existing = path.open(encoding="utf-8", newline="").read() if path.exists() else None
        if existing != content:
            would_change.append(f"{ICS_URL_PREFIX}/{filename}")

    # Detect orphaned .ics files (events that left events.json, e.g. moved to past-shows).
    orphans = []
    if ICS_DIR.exists():
        for path in ICS_DIR.glob("*.ics"):
            if path.name not in targets:
                orphans.append(path)
                would_change.append(f"prune {ICS_URL_PREFIX}/{path.name}")

    if check_only:
        if would_change:
            print(f".ics is out of date ({len(would_change)} change(s) would be made):")
            for c in would_change:
                print(f"  - {c}")
            return 1
        print(f".ics already in sync ({len(targets)} events).")
        return 0

    # Write.
    ICS_DIR.mkdir(parents=True, exist_ok=True)
    for filename, content in targets.items():
        (ICS_DIR / filename).write_text(content, encoding="utf-8", newline="")
    for path in orphans:
        path.unlink()

    # Populate ics_url in events.json (round-trips byte-identically at indent=2).
    for ev in events:
        ev["ics_url"] = f"{ICS_URL_PREFIX}/{ev['id']}.ics"
    EVENTS_PATH.write_text(
        json.dumps(events_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(
        f"Wrote {len(targets)} .ics file(s) to {ICS_URL_PREFIX}/, "
        f"pruned {len(orphans)} orphan(s), populated ics_url in events.json."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
