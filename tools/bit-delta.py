#!/usr/bin/env python3
"""bit-delta.py — work out which Bandsintown rows are NEW since the last upload.

WHY THIS EXISTS
---------------
**BIT appends and does not dedupe by event ID** (discovered 2026-05-23, recorded in
CLAUDE.md Phase 2 step 9). Re-uploading the full CSV therefore creates a duplicate of
every event already on the profile, and each one has to be deleted by hand in the BIT
UI. So the safe upload is *only the rows new since last time* — and until now nothing
computed that.

`tools/mark-bit-upload.sh` stored the **md5 of the whole CSV**. That answers "has the
CSV changed?" and cannot answer "which rows changed?" — which is the question you
actually have standing in front of the upload form. This computes the second one by
diffing against a **snapshot of what was last uploaded**, not a hash of it.

IDENTITY
--------
A BIT row has no id column, so the natural key is `(Start Date, Venue, Event Name)`.
Date+venue alone would collide on a double-header; adding the event name is enough for
this band and is stable across propagator re-runs.

THREE STATES, NEVER ONE BLUR
----------------------------
  * **snapshot exists**      -> a real delta: NEW rows, CHANGED rows, unchanged rows.
  * **no snapshot**          -> UNKNOWN. Every row reads "new" because there is nothing
                               to compare against, and that is NOT evidence the profile
                               is empty. Says so loudly rather than emitting 10 rows as
                               if they were known-new.
  * **snapshot but no CSV**  -> error; run the propagators first.

A CHANGED row is the one case this tool cannot make safe on its own: BIT has no
update-by-key on CSV import, so re-uploading a changed row *adds a second copy* rather
than editing the first. Changed rows are therefore reported but held OUT of the delta by
default — edit those in the BIT UI. `--include-changed` overrides once you have decided.

Exit: 0 = delta written (or nothing to do) · 1 = usage/missing input.
Prove it: `python3 bit-delta.py --selftest`
"""

import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV_PATH = os.path.join(ROOT, "bandsintown-upload.csv")
SNAPSHOT = os.path.join(HERE, ".bit-last-uploaded.csv")
DELTA = os.path.join(ROOT, "bandsintown-delta.csv")

KEY_COLS = ("Start Date* (yyyy-mm-dd)", "Venue*", "Event Name")


def row_key(row):
    return tuple((row.get(c) or "").strip() for c in KEY_COLS)


def read_csv(path):
    if not os.path.exists(path):
        return None, None
    with open(path, newline="", encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        return r.fieldnames, list(r)


def compute(cur_rows, snap_rows):
    """Return (new, changed, unchanged). Pure — no I/O, so the selftest can drive it."""
    if snap_rows is None:
        return list(cur_rows), [], []
    snap = {row_key(r): r for r in snap_rows}
    new, changed, unchanged = [], [], []
    for r in cur_rows:
        k = row_key(r)
        if k not in snap:
            new.append(r)
        elif {c: (v or "") for c, v in r.items()} != {c: (v or "") for c, v in snap[k].items()}:
            changed.append(r)
        else:
            unchanged.append(r)
    return new, changed, unchanged


def main(argv):
    include_changed = "--include-changed" in argv
    fields, cur = read_csv(CSV_PATH)
    if cur is None:
        print(f"✗ {CSV_PATH} not found — run tools/run-propagators.sh first.")
        return 1
    _sf, snap = read_csv(SNAPSHOT)

    new, changed, unchanged = compute(cur, snap)

    print(f"bit-delta — {len(cur)} row(s) in the current CSV")
    if snap is None:
        print()
        print("  ⚠ NO SNAPSHOT of a previous upload exists, so this cannot compute a delta.")
        print("    Every row below is listed as new because there is nothing to compare")
        print("    against — that is NOT evidence the Bandsintown profile is empty.")
        print("    BIT APPENDS: if these events are already on the profile, uploading all")
        print("    of them creates duplicates you must delete by hand in the BIT UI.")
        print("    Check the live profile before uploading, then mark-bit-upload.sh will")
        print("    seed the snapshot so every future run is a real delta.")
    print()
    print(f"  NEW       {len(new)}")
    for r in new:
        print(f"      + {r[KEY_COLS[0]]}  {r[KEY_COLS[1]]}")
    print(f"  CHANGED   {len(changed)}   (held OUT of the delta{' — but --include-changed given' if include_changed else ''})")
    for r in changed:
        print(f"      ~ {r[KEY_COLS[0]]}  {r[KEY_COLS[1]]}")
    if changed and not include_changed:
        print("      BIT has no update-by-key on CSV import — re-uploading a changed row ADDS")
        print("      a second copy. Edit these in the BIT UI, or pass --include-changed.")
    print(f"  UNCHANGED {len(unchanged)}")

    out = new + (changed if include_changed else [])
    if not out:
        print("\n  nothing to upload.")
        if os.path.exists(DELTA):
            os.remove(DELTA)
        return 0

    with open(DELTA, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(out)
    print(f"\n  wrote {DELTA} — {len(out)} row(s)")
    if len(out) > 25:
        print("  ⚠ BIT accepts max 25 events per file; split before uploading.")
    return 0


def _selftest():
    F = {c: "" for c in KEY_COLS}
    def mk(date, venue, name="X", extra=""):
        r = dict(F); r.update({KEY_COLS[0]: date, KEY_COLS[1]: venue, KEY_COLS[2]: name,
                               "Description": extra})
        return r
    a, b = mk("2026-08-15", "Wild Heaven"), mk("2026-08-22", "Summer Shade")
    cases = []

    n, c, u = compute([a, b], None)
    cases.append((len(n) == 2 and not c and not u, "no snapshot -> everything reads new"))

    n, c, u = compute([a, b], [a])
    cases.append((len(n) == 1 and n[0] is b and len(u) == 1, "one new row detected"))

    n, c, u = compute([a], [a])
    cases.append((not n and not c and len(u) == 1, "identical -> nothing to upload"))

    a2 = mk("2026-08-15", "Wild Heaven", extra="new description")
    n, c, u = compute([a2], [a])
    cases.append((not n and len(c) == 1, "same key, changed content -> CHANGED not NEW"))

    dbl = mk("2026-08-15", "Wild Heaven", name="Late Set")
    n, c, u = compute([a, dbl], [a])
    cases.append((len(n) == 1 and n[0] is dbl, "same date+venue, different name -> distinct row"))

    bad = sum(1 for ok, _ in cases if not ok)
    for ok, label in cases:
        print(f"  {'ok  ' if ok else 'FAIL'}  {label}")
    print()
    print(f"{'all ' + str(len(cases)) + ' cases pass' if not bad else str(bad) + ' FAILURE(S)'}")
    return 1 if bad else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    sys.exit(main(sys.argv[1:]))
