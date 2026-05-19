#!/usr/bin/env python3
"""Press-scan query generator for Bolo Boys.

Builds a list of targeted web-search queries from the band's canonical data
(band.json + events.json + past-shows.json) so the band can be discovered
on the open web without drowning in name-collision noise (Dierks Bentley's
prank "Bolo Boys Bluegrass Band", the German hip-hop collective Boloboys, etc.).

This script is the deterministic part of the press scanner — it produces the
query list. The actual scan (running queries through WebSearch, filtering noise
via tools/press-scan-excludes.json, writing the report) is executed by Claude
in a session. See the "Press scanner" section of CLAUDE.md for the playbook.

Usage:
  python3 tools/press-scan.py            # JSON to stdout (default)
  python3 tools/press-scan.py --pretty   # human-readable one-per-line list
"""
import json
import sys
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # Bolo Boys/


def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def build_queries():
    band = load_json(ROOT / "data" / "band.json")
    events = load_json(ROOT / "data" / "events.json")
    past = load_json(ROOT / "data" / "past-shows.json")

    queries = []

    # ── Band-level (member + identity disambiguation) ──────────────
    queries.append({
        "query": '"Bolo Boys" "Nigel Wright"',
        "tag": "band-level",
        "context": "Member disambiguation — should surface only Paul's band",
    })
    queries.append({
        "query": '"Bolo Boys" "Paul Kirschenbauer"',
        "tag": "band-level",
        "context": "Member disambiguation",
    })
    queries.append({
        "query": '"Bolo Boys" "John Wilber"',
        "tag": "band-level",
        "context": "Member disambiguation",
    })
    queries.append({
        "query": '"boloboys.band"',
        "tag": "band-level",
        "context": "Inbound links to the canonical site",
    })
    queries.append({
        "query": '"Bolo Boys" Atlanta Macon band',
        "tag": "band-level",
        "context": "Geographic + role disambiguation",
    })

    # ── Scene collaborators (co-bill mentions) ─────────────────────
    for c in band.get("scene_collaborators", []) or []:
        name = c.get("name")
        if name and name.lower() != "ante up":  # Ante Up shows are still Bolo Boys, no separate co-bill press value
            queries.append({
                "query": f'"Bolo Boys" "{name}"',
                "tag": "scene",
                "context": f"Co-bill: {name}",
            })

    # ── Social platforms (public posts Google has indexed) ─────────
    queries.append({
        "query": '"Bolo Boys" site:instagram.com',
        "tag": "social-ig",
        "context": "Public IG posts/tags Google has indexed — venue promos, co-bill announcements, fan tags",
    })
    queries.append({
        "query": '"Bolo Boys" site:facebook.com',
        "tag": "social-fb",
        "context": "FB pages, posts, and events mentioning the band",
    })

    # ── Local event aggregators / calendars ────────────────────────
    queries.append({
        "query": '"Bolo Boys" Atlanta event calendar',
        "tag": "aggregator",
        "context": "Discover Atlanta, Patch, neighborhood blogs, GPC newsletter pickups",
    })
    queries.append({
        "query": '"Bolo Boys" site:eventbrite.com OR site:bandsintown.com OR site:songkick.com',
        "tag": "aggregator",
        "context": "Music-event aggregator listings (includes the band's own BIT page — filter as appropriate)",
    })

    # ── Local alt-press / show picks ───────────────────────────────
    queries.append({
        "query": '"Bolo Boys" Atlanta concert OR show OR "live music"',
        "tag": "local-press",
        "context": "Creative Loafing, AJC, Atlanta Magazine, Atlanta INtown show picks and listings",
    })

    # ── Per upcoming show ──────────────────────────────────────────
    today = datetime.date.today().isoformat()
    upcoming = sorted(
        [e for e in events.get("events", []) if (e.get("date") or "") >= today],
        key=lambda e: e["date"],
    )[:6]
    for e in upcoming:
        v = e.get("venue_name", "")
        if v:
            queries.append({
                "query": f'"Bolo Boys" "{v}"',
                "tag": "event",
                "context": f"{e.get('date')} — {v}",
                "event_id": e.get("id"),
            })

    # ── Per recent past show (last 8) ──────────────────────────────
    past_sorted = sorted(
        past.get("past_shows", []) or [],
        key=lambda s: s.get("date", ""),
        reverse=True,
    )[:8]
    for s in past_sorted:
        v = s.get("venue_name", "")
        if v:
            queries.append({
                "query": f'"Bolo Boys" "{v}"',
                "tag": "past-event",
                "context": f"{s.get('date')} — {v}",
                "event_id": s.get("id"),
            })

    return queries


def dedupe(queries):
    """Collapse identical queries into one entry, merging contexts and event_ids."""
    by_query = {}
    for q in queries:
        key = q["query"]
        if key not in by_query:
            merged = {"query": q["query"], "tag": q["tag"], "contexts": [], "event_ids": []}
            by_query[key] = merged
        merged = by_query[key]
        if q.get("context") and q["context"] not in merged["contexts"]:
            merged["contexts"].append(q["context"])
        if q.get("event_id") and q["event_id"] not in merged["event_ids"]:
            merged["event_ids"].append(q["event_id"])
    return list(by_query.values())


def main():
    queries = dedupe(build_queries())
    if "--pretty" in sys.argv:
        for q in queries:
            print(f"[{q['tag']:11s}] {q['query']}")
            for ctx in q["contexts"]:
                print(f"              ↪ {ctx}")
    else:
        print(json.dumps(queries, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
