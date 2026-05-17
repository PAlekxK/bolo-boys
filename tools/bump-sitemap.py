#!/usr/bin/env python3
"""Set <lastmod> in sitemap.xml to today's date.

Usage:
    python3 tools/bump-sitemap.py

Run from the public repo root.
"""
import re
import sys
from datetime import date
from pathlib import Path

SITEMAP = Path(__file__).resolve().parent.parent / "sitemap.xml"


def main():
    today = date.today().isoformat()
    text = SITEMAP.read_text()
    new_text, n = re.subn(r"<lastmod>[^<]+</lastmod>", f"<lastmod>{today}</lastmod>", text)
    if n == 0:
        raise SystemExit("No <lastmod> element found in sitemap.xml")
    if new_text == text:
        print(f"sitemap.xml already at {today}.")
        return 0
    SITEMAP.write_text(new_text)
    print(f"Bumped sitemap.xml <lastmod> to {today}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
