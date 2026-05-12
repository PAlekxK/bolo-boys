#!/usr/bin/env python3
"""Generate a Bandsintown bulk-upload CSV from data/events.json + data/venues.json."""
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EVENTS = REPO_ROOT / "data" / "events.json"
VENUES = REPO_ROOT / "data" / "venues.json"
SITE_URL = "https://www.boloboys.band"

# Column order matches Bandsintown's documented bulk-upload template.
COLUMNS = [
    "Venue", "Country", "Address", "City", "Region", "Postal Code",
    "Start Date", "End Date", "Start Time", "End Time",
    "Streaming Link",
    "Ticket Link", "Ticket Type", "Ticket Link 2", "Ticket Type 2",
    "On-Sale Date", "On-Sale Time",
    "Lineup", "Event Name", "Description",
    "Scheduled date", "Scheduled time",
    "Timezone", "Artist Name", "Event Image",
]


def parse_address(address_str):
    parts = [p.strip() for p in address_str.split(",")]
    street = parts[0] if parts else ""
    state, zipc = "", ""
    if len(parts) > 2:
        toks = parts[2].split()
        state = toks[0] if toks else ""
        zipc = toks[-1] if len(toks) > 1 else ""
    return street, state, zipc


def to_24h(time_str):
    if not time_str:
        return ""
    try:
        return datetime.strptime(time_str.strip(), "%I:%M %p").strftime("%H:%M")
    except ValueError:
        return time_str


def event_name(event):
    return event.get("theme") or f"Bolo Boys at {event['venue_name']}"


def event_image(event):
    return f"{SITE_URL}/{event['poster_url']}" if event.get("poster_url") else ""


def main():
    events_data = json.loads(EVENTS.read_text())
    venues_data = json.loads(VENUES.read_text())
    venues_by_id = {v["id"]: v for v in venues_data["venues"]}

    writer = csv.DictWriter(sys.stdout, fieldnames=COLUMNS, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()

    for event in events_data["events"]:
        venue = venues_by_id.get(event["venue_id"], {})
        street, state, zipc = parse_address(venue.get("address", ""))
        writer.writerow({
            "Venue": event["venue_name"],
            "Country": "United States",
            "Address": street,
            "City": venue.get("city") or event["venue_city"].split(",")[0].strip(),
            "Region": venue.get("state") or state,
            "Postal Code": zipc,
            "Start Date": event["date"],
            "End Date": "",
            "Start Time": to_24h(event["time"]),
            "End Time": "",
            "Streaming Link": "",
            "Ticket Link": SITE_URL,
            "Ticket Type": "Free",
            "Ticket Link 2": "",
            "Ticket Type 2": "",
            "On-Sale Date": "",
            "On-Sale Time": "",
            "Lineup": ", ".join(event.get("supporting_acts") or []),
            "Event Name": event_name(event),
            "Description": event.get("invitation_text") or "",
            "Scheduled date": "",
            "Scheduled time": "",
            "Timezone": "America/New_York",
            "Artist Name": "",
            "Event Image": event_image(event),
        })


if __name__ == "__main__":
    main()
