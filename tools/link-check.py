#!/usr/bin/env python3
"""Are the links this site publishes still good? — and can we TELL?

⭐ WHY THIS EXISTS, and it is not "because links rot."

On 2026-09-10 a hand-rolled sweep of all 62 published URLs reported **59 of 62 returning
200** and read as a clean site. Then one negative control was run, and a Instagram post id
of `ZZZZZZZZZZZ` — eleven Z's, a post that cannot exist — also returned **200**. So did a
Spotify track id of twenty-two zeroes.

The 59/62 was worthless for **35 of those links**, including all 29 Instagram URLs, which
are the band's entire announce-post evidence trail under D6. A checker that cannot fail is
not a checker; `CYCLE-MAP.md` calls this signature **B9** — *can this check exit 0 tomorrow?*
— and the map's own instrument table has a column for exactly this: *"Control? asks whether
it has ever been SEEN TO FAIL. An instrument that runs clean and has never been proven able
to fire tells you nothing."*

**So this tool controls every single URL, not every host.** For each real URL it derives a
CONTROL TWIN by corrupting the identifying segment, fetches both, and compares:

    real 200 + twin 404  ->  ✅ VERIFIED   the host discriminates; 200 means something
    real 200 + twin 200  ->  ⚪ BLIND      the host answers 200 to anything; we learned nothing
    real 4xx + twin 4xx  ->  🔴 BROKEN     the host discriminates and our link failed
    real 403/429         ->  🚫 BLOCKED    bot wall; state UNKNOWN, never "broken"

The per-URL twin beats a per-host allowlist because a host can discriminate on one path
shape and not another, and because an allowlist is hand-maintained and goes stale silently
— the exact failure mode this repo keeps re-finding.

⚠️ BLOCKED IS NOT BROKEN, and the distinction is load-bearing. Bandsintown 403s on our own
artist page; the record spent a month unsure whether that was a block or a wrong URL that
somebody had guessed. Reporting a bot wall as a dead link would have sent someone to "fix" a
link that was never broken.

Usage:
  python3 tools/link-check.py                 # everything the site publishes
  python3 tools/link-check.py --only instagram.com
  python3 tools/link-check.py --json
  python3 tools/link-check.py --selftest
"""
import argparse
import concurrent.futures as cf
import json
import os
import re
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")
TIMEOUT = 15

VERIFIED, BLIND, BROKEN, BLOCKED = "VERIFIED", "BLIND", "BROKEN", "BLOCKED"
BLOCK_CODES = {401, 403, 405, 429, 400}


def collect(data_dir=None):
    """Every URL this site puts in front of a human. Sources named, so a reader can tell
    what was swept from what was merely not thought of."""
    d = data_dir or DATA
    out = []

    def add(u, where):
        if isinstance(u, str) and u.startswith("http"):
            out.append({"url": u, "where": where})

    band_path = os.path.join(d, "band.json")
    if os.path.exists(band_path):
        b = json.load(open(band_path))
        for k, v in (b.get("social") or {}).items():
            if not k.endswith("_note") and not k.endswith("_handle"):
                add(v, f"band.social.{k}")
        for group in ("releases", "originals"):
            for r in b.get(group) or []:
                add(r.get("hyperfollow"), f"{group}[{r.get('id')}].hyperfollow")
                for k, v in (r.get("streaming") or {}).items():
                    add(v, f"{group}[{r.get('id')}].streaming.{k}")
    for fname, key in (("events.json", "events"), ("past-shows.json", "past_shows")):
        p = os.path.join(d, fname)
        if not os.path.exists(p):
            continue
        raw = json.load(open(p))
        evs = raw if isinstance(raw, list) else raw.get(key, raw.get("events", []))
        for e in evs:
            for l in e.get("external_links") or []:
                add(l.get("url"), f"{e.get('id')}.external_links")
    return out


#: How to corrupt a URL so it CANNOT resolve, while keeping its shape. Shape matters: many
#: hosts 404 on a malformed path but 200 on a well-formed-but-absent id, and it is the
#: second case that fools a checker.
SENTINEL = "zzzzzzzzzzzzzzzzzzzzzz"


def control_twin(url):
    """A URL of the same shape that cannot exist.

    Strategy: corrupt the LAST meaningful path segment (or the `v=` query id for YouTube),
    preserving length where the host is known to validate it. Returns None when no sensible
    twin exists — a bare domain has no identifier to corrupt, so it cannot be controlled and
    is reported as such rather than guessed at.
    """
    m = re.match(r"^(https?://[^/]+)(/.*)?$", url)
    if not m:
        return None
    base, path = m.group(1), m.group(2) or ""
    if "v=" in url:  # youtube / youtube music watch links
        return re.sub(r"([?&]v=)[^&]+", r"\1" + SENTINEL[:11], url)
    segs = [s for s in path.split("/") if s]
    if not segs:
        return None  # bare domain: nothing to corrupt
    last = segs[-1].split("?")[0]
    if not last:
        return None
    # Preserve length: Spotify validates 22-char base62 ids and 404s on other lengths, so a
    # short sentinel would produce a FALSE "discriminates" reading.
    twin_last = (SENTINEL * 3)[:max(len(last), 4)]
    segs[-1] = twin_last
    return base + "/" + "/".join(segs) + ("/" if path.endswith("/") else "")


def fetch(url, opener=None):
    """Return an HTTP status int, or 0 when the request could not be made at all."""
    if opener is not None:
        return opener(url)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.getcode()
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def classify(real, twin):
    """The whole point of the tool, in five lines.

    `twin` is None when the URL could not be controlled — which is reported as BLIND, never
    as VERIFIED. An uncontrolled pass is the thing this file exists to stop being counted.
    """
    if real in BLOCK_CODES:
        return BLOCKED
    if twin is None:
        return BLIND
    if real == 200 and twin == 200:
        return BLIND
    if real == 200:
        return VERIFIED
    return BROKEN if twin != real else BLIND


def check(entries, opener=None, workers=8):
    def one(e):
        twin_url = control_twin(e["url"])
        real = fetch(e["url"], opener)
        twin = fetch(twin_url, opener) if twin_url else None
        return {**e, "twin_url": twin_url, "real": real, "twin": twin,
                "state": classify(real, twin)}
    if opener is not None:          # selftest path: deterministic order, no threads
        return [one(e) for e in entries]
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(one, entries))


def report(results):
    order = {BROKEN: 0, BLOCKED: 1, BLIND: 2, VERIFIED: 3}
    counts = {s: sum(1 for r in results if r["state"] == s)
              for s in (VERIFIED, BLIND, BLOCKED, BROKEN)}
    print("link-check — every published URL, each with its own control twin\n")
    for r in sorted(results, key=lambda r: (order[r["state"]], r["where"])):
        if r["state"] == VERIFIED:
            continue
        icon = {BROKEN: "🔴", BLOCKED: "🚫", BLIND: "⚪"}[r["state"]]
        why = {BROKEN: f"real {r['real']}, control {r['twin']} — the host discriminates and OURS FAILED",
               BLOCKED: f"HTTP {r['real']} — bot wall. State UNKNOWN; this is NOT proof the link is dead",
               BLIND: (f"real {r['real']}, control {r['twin']} — host answers the same to a URL that "
                       f"cannot exist" if r["twin"] is not None
                       else "no control twin derivable — an uncontrolled pass is not a pass")}[r["state"]]
        print(f"  {icon} {r['state']:<8} {r['where']}\n      {r['url']}\n      {why}")
    print(f"\n  ✅ VERIFIED {counts[VERIFIED]}   ⚪ BLIND {counts[BLIND]}   "
          f"🚫 BLOCKED {counts[BLOCKED]}   🔴 BROKEN {counts[BROKEN]}   "
          f"(total {len(results)})")
    print(f"\n  ⚠️ This check can speak for {counts[VERIFIED]} of {len(results)} links. "
          f"For the other {len(results) - counts[VERIFIED]} a 200 is NOT evidence —\n"
          f"     the host returns one for URLs that do not exist, or refuses robots outright. "
          f"Those need a human or a real browser.")
    return 1 if counts[BROKEN] else 0


def selftest():
    checks, failed = 0, []

    def ck(name, cond):
        nonlocal checks
        checks += 1
        if not cond:
            failed.append(name)

    # ---- control_twin ----
    ck("twin corrupts the last segment",
       control_twin("https://x.com/p/ABC123/") != "https://x.com/p/ABC123/")
    ck("twin preserves trailing slash",
       control_twin("https://x.com/p/ABC123/").endswith("/"))
    ck("twin preserves id LENGTH (spotify 22-char validation)",
       len(control_twin("https://open.spotify.com/track/" + "a" * 22).rstrip("/").split("/")[-1]) == 22)
    ck("twin handles ?v= query ids",
       "v=" + SENTINEL[:11] in control_twin("https://music.youtube.com/watch?v=abc123"))
    ck("bare domain has NO twin", control_twin("https://example.com") is None)
    ck("bare domain with slash has NO twin", control_twin("https://example.com/") is None)

    # ---- classify: the four states, each seen to fire ----
    ck("200 + 404 = VERIFIED", classify(200, 404) == VERIFIED)
    ck("200 + 200 = BLIND (the bug this tool exists for)", classify(200, 200) == BLIND)
    ck("404 + 200 = BROKEN", classify(404, 200) == BROKEN)
    ck("403 = BLOCKED, not broken", classify(403, 404) == BLOCKED)
    ck("429 = BLOCKED, not broken", classify(429, 404) == BLOCKED)
    ck("405 = BLOCKED (Shazam answers GET with 405)", classify(405, 404) == BLOCKED)
    ck("uncontrollable url is BLIND, never VERIFIED", classify(200, None) == BLIND)
    ck("BLOCKED outranks a missing twin", classify(403, None) == BLOCKED)

    # ---- end-to-end against a fake network ----
    world = {
        "https://good.com/p/real": 200,        # twin will 404 -> VERIFIED
        "https://blind.com/p/real": 200,       # twin also 200 -> BLIND
        "https://dead.com/p/real": 404,        # twin 200     -> BROKEN
        "https://walled.com/p/real": 403,      # -> BLOCKED
    }

    def opener(url):
        if url in world:
            return world[url]
        host = url.split("/")[2]
        return 200 if host == "blind.com" else (200 if host == "dead.com" else 404)

    entries = [{"url": u, "where": f"w{i}"} for i, u in enumerate(world)]
    res = {r["url"]: r["state"] for r in check(entries, opener=opener)}
    ck("e2e VERIFIED", res["https://good.com/p/real"] == VERIFIED)
    ck("e2e BLIND", res["https://blind.com/p/real"] == BLIND)
    ck("e2e BROKEN", res["https://dead.com/p/real"] == BROKEN)
    ck("e2e BLOCKED", res["https://walled.com/p/real"] == BLOCKED)
    # THE REGRESSION GUARD: the real-world case that motivated the tool.
    ck("a blind host never counts as verified",
       res["https://blind.com/p/real"] != VERIFIED)

    # ---- collect() reads the real shapes without crashing ----
    got = collect()
    ck("collect finds published urls", len(got) > 0)
    ck("every collected entry names its source", all(g["where"] for g in got))

    for f in failed:
        print(f"  FAIL {f}")
    print(f"{checks - len(failed)}/{checks} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="substring filter on host or source")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    entries = collect()
    if a.only:
        entries = [e for e in entries if a.only in e["url"] or a.only in e["where"]]
    results = check(entries)
    if a.json:
        print(json.dumps(results, indent=2))
        sys.exit(0)
    sys.exit(report(results))
