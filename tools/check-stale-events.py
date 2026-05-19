#!/usr/bin/env python3
"""Flag past-dated entries in data/events.json that need Phase 5 cleanup.

events.json is for upcoming shows only. Once a show passes, the lifecycle
workflow (CLAUDE.md → Phase 5 — Post-show) transforms the entry and moves
it to past-shows.json. This check exists because that step is manual and
easy to forget — particularly when no other events.json edit happens
between the show and the cleanup window.

Exits non-zero if any drift is found. Called from tools/run-propagators.sh
as a non-blocking warning, and intended to be run at the start of any
session that touches events, past-shows, or pipeline review.
"""

import json
import sys
from datetime import date
from pathlib import Path

EVENTS_PATH = Path(__file__).resolve().parent.parent / "data" / "events.json"


def main() -> int:
    with EVENTS_PATH.open() as f:
        data = json.load(f)
    today = date.today().isoformat()
    stale = [e for e in data.get("events", []) if e.get("date", "") < today]
    if not stale:
        print("✓ events.json is clean — no past-dated entries.")
        return 0
    print(f"⚠  {len(stale)} past-dated entr{'y' if len(stale) == 1 else 'ies'} in events.json needs Phase 5 cleanup:")
    for e in stale:
        print(f"   - {e.get('id')} ({e.get('date')} — {e.get('venue_name', '?')})")
    print()
    print("See CLAUDE.md → Show lifecycle workflow → Phase 5 — Post-show.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
