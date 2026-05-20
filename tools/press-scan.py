#!/usr/bin/env python3
"""Press-scan query generator for Bolo Boys.

Builds a list of targeted web-search queries from the band's canonical data
(band.json + events.json + past-shows.json) so the band can be discovered
on the open web without drowning in name-collision noise (Dierks Bentley's
prank "Bolo Boys Bluegrass Band", the German hip-hop collective Boloboys, etc.).

This script is the deterministic part of the press scanner — it produces the
query list (and, in implicit mode, a list of per-venue review targets). The
actual scan (running queries through WebSearch, fetching review pages,
filtering noise via tools/press-scan-excludes.json, writing the report) is
executed by Claude in a session. See the "Press scanner" section of CLAUDE.md
for the playbook.

Usage:
  python3 tools/press-scan.py                       # explicit (default), JSON
  python3 tools/press-scan.py --mode explicit       # press / aggregator / venue-review queries
  python3 tools/press-scan.py --mode implicit       # venue-review targets only (per-venue, requires verification)
  python3 tools/press-scan.py --mode all            # both
  python3 tools/press-scan.py --pretty              # human-readable one-per-line list

Output shape (all modes):
  {
    "queries": [ ... ],            # explicit / implicit modes both have this key
    "implicit_targets": [ ... ]    # implicit / all modes only
  }
"""
import argparse
import json
import sys
import datetime
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # Bolo Boys/

MIN_PLAYS_FOR_IMPLICIT = 2          # venues with >=2 past plays are implicit-scan candidates
IMPLICIT_MATCH_WINDOW_DAYS = 14     # review date allowed up to N days after show date

# Fallback if press-scan-excludes.json doesn't carry implicit_language_signals yet.
DEFAULT_LANGUAGE_SIGNALS = [
    "live music", "band", "trio", "guitar", "acoustic",
    "set", "playing", "musicians", "harmonies",
]


def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def build_queries(band, events, past, venues, mode):
    """Build the explicit-mode query list.

    Returns [] for mode == "implicit".
    """
    if mode == "implicit":
        return []

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

    # ── Venue-review (explicit Bolo Boys mention inside a venue review) ─
    queries.append({
        "query": '"Bolo Boys" site:yelp.com OR site:google.com/maps',
        "tag": "venue-review",
        "context": "Reviews on Yelp / Google Maps that name the band explicitly",
    })
    queries.append({
        "query": '"Bolo Boys" review',
        "tag": "venue-review",
        "context": "Broad review-language search across the open web",
    })

    recurring_names = recurring_venue_names(past)
    for name in recurring_names:
        queries.append({
            "query": f'"Bolo Boys" "{name}" review',
            "tag": "venue-review",
            "context": f"Explicit Bolo Boys mention in {name} reviews",
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


def recurring_venue_names(past):
    """Distinct venue_name values for venues with >=2 past plays.

    Returns a sorted list so query ordering is stable across runs.
    """
    venue_play_counts = Counter(s.get("venue_id") for s in past.get("past_shows", []) or [])
    recurring_ids = {vid for vid, count in venue_play_counts.items() if vid and count >= MIN_PLAYS_FOR_IMPLICIT}

    # venue_name is sometimes shared (Wild Heaven Avondale + Toco Hills both use "Wild Heaven Brewing").
    # Dedupe on venue_name — same explicit query covers both branches.
    names = set()
    for s in past.get("past_shows", []) or []:
        if s.get("venue_id") in recurring_ids and s.get("venue_name"):
            names.add(s["venue_name"])
    return sorted(names)


def build_implicit_targets(past, venues, language_signals):
    """For each venue with >=MIN_PLAYS_FOR_IMPLICIT past plays AND at least one review URL,
    emit a target object that Claude executes per the implicit-verification playbook.
    """
    venues_by_id = {v["id"]: v for v in venues.get("venues", []) or []}

    venue_play_counts = Counter(s.get("venue_id") for s in past.get("past_shows", []) or [])
    eligible_ids = sorted(
        vid for vid, count in venue_play_counts.items()
        if vid and count >= MIN_PLAYS_FOR_IMPLICIT
    )

    targets = []
    for vid in eligible_ids:
        venue = venues_by_id.get(vid)
        if not venue:
            continue

        review_urls = {}
        if venue.get("yelp_url"):
            review_urls["yelp"] = venue["yelp_url"]
        if venue.get("google_reviews_url"):
            review_urls["google"] = venue["google_reviews_url"]

        if not review_urls:
            # Skip venues with no review URLs — they need URLs added to venues.json before
            # the implicit scanner can execute against them.
            continue

        show_dates = sorted(
            [
                {
                    "date": s.get("date"),
                    "supporting_acts": s.get("supporting_acts", []) or [],
                }
                for s in past.get("past_shows", []) or []
                if s.get("venue_id") == vid and s.get("date")
            ],
            key=lambda d: d["date"],
        )

        targets.append({
            "venue_id": vid,
            "venue_name": venue.get("name"),
            "review_urls": review_urls,
            "show_dates": show_dates,
            "match_window_days": IMPLICIT_MATCH_WINDOW_DAYS,
            "language_signals": language_signals,
        })

    return targets


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


def parse_args():
    p = argparse.ArgumentParser(description="Press-scan query generator for Bolo Boys.")
    p.add_argument(
        "--mode",
        choices=["explicit", "implicit", "all"],
        default="explicit",
        help="explicit (default) = all press / aggregator / venue-review queries; "
             "implicit = per-venue review targets only (requires Paul verification); "
             "all = both.",
    )
    p.add_argument("--pretty", action="store_true", help="Human-readable rendering")
    return p.parse_args()


def main():
    args = parse_args()

    band = load_json(ROOT / "data" / "band.json")
    events = load_json(ROOT / "data" / "events.json")
    past = load_json(ROOT / "data" / "past-shows.json")
    venues = load_json(ROOT / "data" / "venues.json")

    try:
        excludes = load_json(ROOT / "tools" / "press-scan-excludes.json")
        language_signals = excludes.get("implicit_language_signals") or DEFAULT_LANGUAGE_SIGNALS
    except FileNotFoundError:
        language_signals = DEFAULT_LANGUAGE_SIGNALS

    queries = dedupe(build_queries(band, events, past, venues, args.mode))

    output = {"queries": queries}
    if args.mode in ("implicit", "all"):
        output["implicit_targets"] = build_implicit_targets(past, venues, language_signals)

    if args.pretty:
        if queries:
            print("=== Queries ===")
            for q in queries:
                print(f"[{q['tag']:13s}] {q['query']}")
                for ctx in q["contexts"]:
                    print(f"                ↪ {ctx}")
        targets = output.get("implicit_targets", [])
        if targets:
            print()
            print("=== Implicit venue-review targets ===")
            for t in targets:
                print(f"[{t['venue_id']}] {t['venue_name']} — {len(t['show_dates'])} past shows, "
                      f"±{t['match_window_days']}d match window")
                for url_kind, url in t["review_urls"].items():
                    print(f"                ↪ {url_kind}: {url}")
                for sd in t["show_dates"]:
                    sa = ", ".join(sd["supporting_acts"]) if sd["supporting_acts"] else "—"
                    print(f"                ↪ {sd['date']} (co-bills: {sa})")
    else:
        print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
