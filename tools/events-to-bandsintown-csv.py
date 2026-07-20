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

# Column order matches Bandsintown's documented bulk-upload template
# (Bandsintown_Bulk_Upload_Artists_Template.csv). Asterisks mark required fields.
COLUMNS = [
    "Artist Name",
    "Venue*", "Country*", "Address", "City*", "Region*", "Postal Code",
    "Timezone*",
    "Start Date* (yyyy-mm-dd)", "Start Time* (HH:MM)",
    "End Date", "End Time",
    "Streaming Link",
    "Ticket Link", "Ticket Type", "Ticket Link 2", "Ticket Type 2",
    "On-Sale Date", "On-Sale Time",
    "Lineup",
    "Event Name", "Event Display Format", "Description",
    "Schedule Date", "Schedule Time",
    "Do Not Announce", "Setlist", "Event Image",
]

ARTIST_NAME = "Bolo Boys"


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
        if event.get("unlisted"):
            continue  # private/anonymized cards never go to Bandsintown
        venue = venues_by_id.get(event["venue_id"], {})
        street, state, zipc = parse_address(venue.get("address", ""))
        writer.writerow({
            "Artist Name": ARTIST_NAME,
            "Venue*": event["venue_name"],
            "Country*": "United States",
            "Address": street,
            "City*": venue.get("city") or event["venue_city"].split(",")[0].strip(),
            "Region*": venue.get("state") or state,
            "Postal Code": zipc,
            "Timezone*": "America/New_York",
            "Start Date* (yyyy-mm-dd)": event["date"],
            "Start Time* (HH:MM)": to_24h(event["time"]),
            "End Date": "",
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
            "Event Display Format": "",
            "Description": event.get("invitation_text") or "",
            "Schedule Date": "",
            "Schedule Time": "",
            "Do Not Announce": "",
            "Setlist": "",
            "Event Image": event_image(event),
        })


if __name__ == "__main__":
    main()
