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


def nth_object_span(src: str, array_span: tuple, n: int) -> tuple:
    """Span of the n-th (0-based) object inside the array at `array_span`.

    ⚠️ ADDED 2026-09-10 AFTER THIS TOOL CORRUPTED THE RECORD. Every edit used to be
    scoped to `block_span(src, "releases")` — the whole ARRAY — and `replace_scalar`
    then took the FIRST match inside it. With one release that is the right answer.
    With two it silently writes every field to releases[0]: run it for Dogies and
    Muddy Knees ends up carrying Dogies' Spotify id and Dogies' Amazon URL, while
    Dogies gets nothing. That is exactly what happened, on a file that feeds the
    public site's release JSON-LD.

    The bug was invisible for a month because the tool ALSO printed
    `data["releases"][0]["title"]` as confirmation — so it cheerfully said
    "✓ Muddy Knees → status: out" while being asked about Dogies. A confirmation line
    read from the same wrong index as the write cannot catch a wrong-index write.
    """
    lo, hi = array_span
    i = src.index("[", lo) + 1
    depth = 0
    in_str = esc = False
    start = None
    count = 0
    while i < hi:
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
        elif c == "{":
            if depth == 0:
                start = i
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                if count == n:
                    return start, i + 1
                count += 1
        i += 1
    raise SystemExit(f"ERROR: no object #{n} inside that array")


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
    ap.add_argument("--iheartradio", help="Full iHeartRadio album URL")
    ap.add_argument("--release", help="Release id or title to target. REQUIRED when "
                                      "band.json holds more than one release and the "
                                      "track id matches none of them.")
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
    # WHICH release? Never releases[0] by default — see nth_object_span's note.
    rels = data["releases"]
    if args.release:
        idx = [i for i, r in enumerate(rels)
               if args.release in (r.get("id"), r.get("title"))]
        if not idx:
            print(f"ERROR: no release with id/title {args.release!r}. Have: "
                  + ", ".join(r.get("id", "?") for r in rels), file=sys.stderr)
            return 1
        n = idx[0]
    else:
        # Infer from the track id when it already identifies exactly one release —
        # this makes re-runs (the documented "safe to re-run to add more links"
        # case) target correctly without a new flag.
        idx = [i for i, r in enumerate(rels) if r.get("spotify_track_id") == tid]
        if len(idx) == 1:
            n = idx[0]
        elif len(rels) == 1:
            n = 0
        else:
            # REFUSE rather than guess. Guessing is what corrupted the file.
            print("ERROR: --release is required when band.json has more than one "
                  "release and the track id matches none of them.\n  Have: "
                  + ", ".join(f"{r.get('id')} ({r.get('spotify_track_id')})" for r in rels),
                  file=sys.stderr)
            return 1
    rel_title = rels[n]["title"]

    def target_span(source):
        """Recomputed after every edit — offsets shift as values change length."""
        return nth_object_span(source, block_span(source, "releases"), n)

    src = replace_scalar(src, "spotify_track_id", tid, target_span(src))

    def stream_span(source):
        lo, hi = target_span(source)
        s_lo, s_hi = block_span(source[lo:hi], "streaming")
        return (lo + s_lo, lo + s_hi)

    src = replace_scalar(src, "spotify", f"https://open.spotify.com/track/{tid}",
                         stream_span(src))
    for key, val in (("apple_music", args.apple_music),
                     ("amazon_music", args.amazon_music),
                     ("youtube_music", args.youtube_music),
                     ("iheartradio", args.iheartradio)):
        if val:
            src = replace_scalar(src, key, val, stream_span(src))

    if not args.keep_upcoming:
        src = replace_scalar(src, "status", "out", target_span(src))

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
