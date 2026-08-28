#!/usr/bin/env python3
"""
generated_views — is every checked-in file that is GENERATED still in step with its source?

Born 2026-08-28 in health-record, where `data/appointments.json` was updated and
`APPOINTMENTS.md` was never re-rendered: for a day the roster showed a superseded
appointment as *upcoming* and omitted the live one entirely. ⭐ The freshness check
already existed and had NO CALLER. This module is that caller, and it is deliberately
identical in every repo that has generated views — the ROSTER differs, the code does not.

    tools/generated-views.json   ← the roster (per repo, hand-maintained)
    tools/generated_views.py     ← this file (byte-identical across repos; diff it)

Roster entry:
    {"generator": "tools/x.py", "view": "X.md"}                  → runs `x.py --check`
    {"view": "sitemap.xml", "exempt": "why it cannot be checked"} → reported, never green-washed

    python3 tools/generated_views.py             # status; exit 1 unless all verified
    python3 tools/generated_views.py --render    # re-render the stale ones
    python3 tools/generated_views.py --selftest  # negative controls

⭐ WHY EXIT CODES ARE NOT TRUSTED. A generator handed an unrecognised flag commonly
PRINTS ITS OUTPUT AND EXITS 0 (health-record's appointments.py does exactly this). A
checker reading the return code alone would call that green for a check that never ran.
So a green verdict must be SPOKEN by the generator — it must print `ok:` — and anything
else is `unverifiable`, which FAILS. (memory: match the PAYLOAD, not the container.)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROSTER = Path(__file__).resolve().parent / "generated-views.json"

OK_TOKEN = "ok:"
STALE_TOKENS = ("STALE", "DRIFT", "would change", "out of date")
GLYPH = {"current": "✅", "stale": "🔴", "unverifiable": "⚠️", "exempt": "⚪"}


def roster() -> list[dict]:
    if not ROSTER.exists():
        return []
    return json.loads(ROSTER.read_text())["views"]


def check_one(entry: dict) -> dict:
    view, gen = entry.get("view", "?"), entry.get("generator")
    base = {"view": view, "generator": gen}
    if entry.get("exempt"):
        return {**base, "state": "exempt", "detail": entry["exempt"]}
    if not gen:
        return {**base, "state": "unverifiable", "detail": "roster row has no generator"}
    gen_path = ROOT / gen
    if not gen_path.exists():
        return {**base, "state": "unverifiable", "detail": f"generator missing: {gen}"}
    if not (ROOT / view).exists():
        return {**base, "state": "stale", "detail": f"{view} does not exist — run --render"}
    try:
        r = subprocess.run([sys.executable, str(gen_path), "--check"],
                           cwd=ROOT, capture_output=True, text=True, timeout=120)
    except Exception as e:  # noqa: BLE001 — a check that could not run is never green
        return {**base, "state": "unverifiable", "detail": f"could not run {gen} --check: {e}"}
    out = (r.stdout + r.stderr).strip()
    first = out.splitlines()[0] if out else f"exit {r.returncode}"
    if any(t in out for t in STALE_TOKENS) or r.returncode != 0:
        return {**base, "state": "stale", "detail": first}
    if OK_TOKEN not in out:
        return {**base, "state": "unverifiable",
                "detail": (f"{gen} --check exited 0 but printed no verdict ({out[:50]!r}) "
                           f"— it may not implement --check at all")}
    return {**base, "state": "current", "detail": first}


def check_all() -> list[dict]:
    return [check_one(e) for e in roster()]


def render(generator: str, args: list[str] | None = None) -> tuple[bool, str]:
    cmd = [sys.executable, str(ROOT / generator)] + (args or [])
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=120)
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def selftest() -> int:
    """NEGATIVE CONTROL. A check never seen going red is not a check.

    Fixtures live in a temp dir — no tracked file is ever mutated to prove this works.
    """
    import tempfile
    fails = []
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        (tdp / "loud.py").write_text("print('STALE: x does not match'); raise SystemExit(1)\n")
        (tdp / "quiet_exit1.py").write_text("raise SystemExit(1)\n")          # red, says nothing
        (tdp / "silent.py").write_text("print('2026-09-02  11:00  visit')\n")  # ⭐ THE TRAP
        (tdp / "good.py").write_text("print('ok: VIEW.md matches the source')\n")
        (tdp / "VIEW.md").write_text("x\n")

        global ROOT
        real, ROOT = ROOT, tdp
        try:
            cases = [
                ({"generator": "loud.py", "view": "VIEW.md"}, "stale", "says STALE"),
                ({"generator": "quiet_exit1.py", "view": "VIEW.md"}, "stale", "exit 1, silent"),
                ({"generator": "silent.py", "view": "VIEW.md"}, "unverifiable",
                 "⭐ exits 0 having checked NOTHING"),
                ({"generator": "good.py", "view": "VIEW.md"}, "current", "the correct idiom"),
                ({"generator": "gone.py", "view": "VIEW.md"}, "unverifiable", "generator missing"),
                ({"generator": "good.py", "view": "NOPE.md"}, "stale", "view missing"),
                ({"view": "x.xml", "exempt": "time-based"}, "exempt", "declared exempt"),
                ({"view": "y.md"}, "unverifiable", "no generator named"),
            ]
            for entry, want, why in cases:
                got = check_one(entry)["state"]
                ok = got == want
                print(f"  {GLYPH.get(got, '?')} {why:<34} -> {got:<13} "
                      f"({'correct' if ok else 'WRONG, wanted ' + want})")
                if not ok:
                    fails.append(f"{why}: got {got}, wanted {want}")
        finally:
            ROOT = real

    for f in fails:
        print(f"FAIL  {f}", file=sys.stderr)
    print(f"\n--selftest: {'FAILED' if fails else 'PASS'} — {len(fails)} failure(s); "
          f"the exit-0-without-checking trap is case 3")
    return 1 if fails else 0


def main() -> int:
    args = sys.argv[1:]
    if "--selftest" in args:
        return selftest()

    entries = roster()
    if not entries:
        print(f"no roster at {ROSTER.name} — nothing declared generated.")
        return 0

    results = check_all()
    if "--render" in args:
        for e, r in zip(entries, results):
            if r["state"] == "stale":
                ok, out = render(e["generator"], e.get("render_args"))
                print(f"  {'✅' if ok else '🔴'} {r['view']}: {out.splitlines()[-1] if out else ''}")
        results = check_all()

    for r in results:
        print(f"  {GLYPH[r['state']]} {r['view']:<28} {r['detail']}")

    bad = [r for r in results if r["state"] in ("stale", "unverifiable")]
    exempt = [r for r in results if r["state"] == "exempt"]
    if bad:
        print(f"\n🔴 {len(bad)} of {len(results)} generated view(s) NOT verified current."
              f"\n   fix: python3 tools/generated_views.py --render")
        return 1
    tail = f" ({len(exempt)} exempt, listed above)" if exempt else ""
    print(f"\n✅ {len(results) - len(exempt)} generated view(s) match their source{tail}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
