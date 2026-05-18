# Bolo Boys — Changelog

Date-stamped one-line summaries of meaningful state changes. Newest first. Companion to the git log; `git log` has the full diff per commit.

---

## 2026-05-17 (latest) — Scene-events calendar + propose-dates workflow

- **Added** `data/scene-events.json` — Atlanta-area `competing_events` (Summer Shade, VHP, GP Porchfest, East Atlanta Strut, Inman Park Festival, DragonCon, Shaky Knees, Sweetwater 420, Atlanta Pride, Decatur Book Festival, Decatur Craft Beer Festival, Music Midtown hiatus) and `boost_windows` (Memorial Day, July 4th, Labor Day, Halloween-on-Saturday, Thanksgiving, holiday season, St. Patrick's, Cinco de Mayo, spring + fall patio sweet spots). Plus `venue_specific_notes` for Side Saddle, Wild Heaven Avondale, Grant Central Pizza East.
- **Updated** `CLAUDE.md` Pipeline status review:
  - Added scene-events.json as Step 1's 4th read and Step 2's 5th cross-check (scene-conflict detection).
  - Added a new "Proposing dates to a venue" workflow section — when the venue asks for 4 dates (or vice versa), Claude ranks candidates using events.json (hard avoid) + scene-events.json competing_events (scene-conflict avoid) + boost_windows (prefer) + venue_specific_notes (prefer).
- **Broadened** memory entry `feedback_lead_capture_conflict_check.md` — three layers of conflict (hard / scene-level / audience-overlap) plus positive boost-window signals when proposing dates.
- **Re-flagged** the Side Saddle 8/29 + Summer Shade 8/29 collision under the broader lens: it's not just a time-math conflict — same Saturday, same neighborhood (Grant Park / Beltline), same audience. Needs deconfliction before the Summer Shade gazebo booking is confirmed.

Side-effects Paul confirmed: none — this is a planning-infrastructure session.

## 2026-05-17 (later) — Pipeline status review workflow + post-Grant-Park leads

- **Added** "Pipeline status review (Tier 1 read-pattern)" section to `CLAUDE.md` — codifies the read-and-orient workflow Claude runs when Paul triggers a status check, including the cross-check against boloboys.band / Bandsintown / Gmail / Google Calendar to catch downstream drift. Jobs served: JTBD-01, JTBD-02, JTBD-05.
- **Updated** `venue-contacts.json` from the 5/17 Market in the Park show: Josh Peatross + Skyler Edwards last-contact bumped to 2026-05-17 with the **Summer Shade Festival gazebo-stage interest** captured; gateway-park-grant-park summary updated to note the open opportunity.
- **Added** `Grant Park Porchfest` as a new `prospecting` venue_relationship — watching for application window to open.
- **Added** Jasper booking contact **Angela Reinhart** (phone (678) 986-9872) as a new scene_connector for Jasper, GA.
- **Regenerated** `Bolo Boys - Private/docs/venue-contacts.md` via `tools/contacts-to-markdown.py`.
- **Created** placeholder calendar invite on the Bolo Boys Calendar for **Sat Aug 29 + Sun Aug 30, 2026** ("[PLACEHOLDER] Summer Shade Festival — Grant Park (gazebo stage interest)") with Paul, Nigel, and John invited so the band can confirm weekend availability before pursuing the gazebo booking. Description flags the potential conflict with the Side Saddle 8/29 evening show.

Side-effects Paul confirmed: calendar invite sent to all 3 members.

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
