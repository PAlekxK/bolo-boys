# Bolo Boys — Changelog

Date-stamped one-line summaries of meaningful state changes. Newest first. Companion to the git log; `git log` has the full diff per commit.

---

## 2026-05-17 — Tier 0/1 architecture: schema consolidation + propagator protocol

- **Promoted** venue contacts from prose to structured data: new `Bolo Boys - Private/data/venue-contacts.json` (15 venues, 17 contacts, 2 scene connectors) with a generator `Bolo Boys - Private/tools/contacts-to-markdown.py` that regenerates `docs/venue-contacts.md` as a view.
- **Retired** `Bolo Boys CRM.xlsx` to `Bolo Boys - Private/_archive/` (was unwired; venue-contacts.json now covers it).
- **Added** `duration_hours` field to every event in `data/events.json` (backfilled from the JSON-LD that was already in `index.html`).
- **Added** propagator scripts: `tools/events-to-jsonld.py` (regenerates the `MusicEvent` JSON-LD between markers in `index.html`), `tools/bump-sitemap.py` (sets `sitemap.xml <lastmod>` to today), and `tools/run-propagators.sh` (orchestrator that runs both plus the existing Bandsintown CSV regen).
- **Added** JSON-LD start/end marker comments in `index.html` so the generator can find the block.
- **Updated** `CLAUDE.md` lifecycle Phase 2 + Phase 5 to call `tools/run-propagators.sh` in place of the manual JSON-LD / sitemap / BIT steps. Added an "After editing `data/`" section and an "Audit trail" section.
- **Regenerated** `index.html` JSON-LD and `bandsintown-upload.csv` via the new propagator. Two intentional diffs from prior state: theme suffixes added to event `name` fields (matching the CLAUDE.md spec; prior state was the drift), and `offers.validFrom` bumped to today.

Side-effects Paul confirmed: none yet — this is the consolidation commit, no band-facing changes.

Research + engineering reports lived in `.research/paul-as-operator.md` and `.engineering/dashboard-path-evaluation.md` (both gitignored from the public repo).
