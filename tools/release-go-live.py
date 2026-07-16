#!/usr/bin/env python3
"""Flip a release from 'upcoming' to 'out' on launch day.

Release morning is a bad time to hand-edit JSON. This does the whole flip
deterministically from the one fact you can't know until the release lands:
the Spotify track ID.

Usage:
    python3 tools/release-go-live.py --spotify-track-id 4cOdK2wGLETKBW3PvgPWqT
    python3 tools/release-go-live.py --spotify-track-id <id> --apple-music <url>

Then: bash tools/run-propagators.sh && git commit && git push

The Spotify track ID is the string after /track/ in the share URL:
    https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT?si=...
                                   ^^^^^^^^^^^^^^^^^^^^^^
Idempotent: safe to re-run to add more streaming links later.
"""

import argparse
import json
import re
import sys
from pathlib import Path

BAND = Path(__file__).resolve().parent.parent / "data" / "band.json"

# Spotify IDs are base62, always 22 chars. Catches a pasted full URL or a typo.
TRACK_ID_RE = re.compile(r"^[A-Za-z0-9]{22}$")


def block_span(src: str, key: str) -> tuple:
    """Return (start, end) character offsets of the value of `key`, by matching
    brackets. Necessary because band.json has more than one "streaming" block —
    originals[] has one too, and a naive search clobbers it."""
    m = re.search(rf'"{re.escape(key)}"\s*:\s*([\[{{])', src)
    if not m:
        raise SystemExit(f"ERROR: block {key!r} not found in band.json")
    open_ch = m.group(1)
    close_ch = "]" if open_ch == "[" else "}"
    i = m.end(1)
    depth = 1
    in_str = False
    esc = False
    while i < len(src) and depth:
        c = src[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
        i += 1
    if depth:
        raise SystemExit(f"ERROR: unbalanced brackets scanning {key!r}")
    return m.start(), i


def replace_scalar(src: str, key: str, value, span: tuple) -> str:
    """Replace one key's value within `span` only, preserving the file's hand
    formatting (json.dump would reflow every compact array)."""
    lo, hi = span
    pattern = re.compile(rf'("{re.escape(key)}"\s*:\s*)(null|"[^"]*")')
    m = pattern.search(src, lo, hi)
    if not m:
        raise SystemExit(f"ERROR: key {key!r} not found inside the target block")
    new = "null" if value is None else json.dumps(value, ensure_ascii=False)
    return src[: m.start(2)] + new + src[m.end(2) :]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spotify-track-id", required=True,
                    help="22-char ID from the Spotify share URL (not the whole URL)")
    ap.add_argument("--apple-music", help="Full Apple Music URL")
    ap.add_argument("--amazon-music", help="Full Amazon Music URL")
    ap.add_argument("--youtube-music", help="Full YouTube Music URL")
    ap.add_argument("--keep-upcoming", action="store_true",
                    help="Fill links but don't flip status to 'out' yet")
    args = ap.parse_args()

    tid = args.spotify_track_id.strip()
    if "/track/" in tid:  # tolerate a pasted URL
        tid = tid.split("/track/")[1].split("?")[0]
    if not TRACK_ID_RE.match(tid):
        print(f"ERROR: {tid!r} isn't a 22-char Spotify track ID.\n"
              f"       Paste the part after /track/ in the share URL.", file=sys.stderr)
        return 1

    src = BAND.read_text()
    data = json.loads(src)
    if not data.get("releases"):
        print("ERROR: no releases[] in band.json", file=sys.stderr)
        return 1
    rel_title = data["releases"][0]["title"]

    # Scope every edit to the releases[] block. band.json has a second
    # "streaming" object under originals[] (Nigel's "The Cowboy's Life") and an
    # unscoped search silently overwrites it.
    rel_span = block_span(src, "releases")
    src = replace_scalar(src, "spotify_track_id", tid, rel_span)

    rel_span = block_span(src, "releases")  # offsets shift after each edit
    lo, hi = rel_span
    stream_lo, stream_hi = block_span(src[lo:hi], "streaming")
    stream_span = (lo + stream_lo, lo + stream_hi)

    src = replace_scalar(src, "spotify", f"https://open.spotify.com/track/{tid}", stream_span)
    for key, val in (("apple_music", args.apple_music),
                     ("amazon_music", args.amazon_music),
                     ("youtube_music", args.youtube_music)):
        if val:
            lo, hi = block_span(src, "releases")
            s_lo, s_hi = block_span(src[lo:hi], "streaming")
            src = replace_scalar(src, key, val, (lo + s_lo, lo + s_hi))

    if not args.keep_upcoming:
        src = replace_scalar(src, "status", "out", block_span(src, "releases"))

    json.loads(src)  # fail loudly rather than write a broken file
    BAND.write_text(src)

    status = "upcoming (held)" if args.keep_upcoming else "out"
    print(f"✓ {rel_title} → status: {status}")
    print(f"  spotify_track_id: {tid}")
    print("\nNext:")
    print("  bash tools/run-propagators.sh")
    print("  git add -A && git commit -m 'Dogies is out' && git push")
    return 0


if __name__ == "__main__":
    sys.exit(main())
