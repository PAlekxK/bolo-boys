# Bolo Boys — Changelog

Date-stamped one-line summaries of meaningful state changes. Newest first. Companion to the git log; `git log` has the full diff per commit.

---

## 2026-05-18 (latest) — Market in the Park Phase 5 cleanup + stale-events guard

- **Phase 5 transformation** for `gateway-park-grant-park-2026-05-17` (Grant Park Market in the Park, 2026-05-17). Moved from `events.json` to `past-shows.json` with lighter schema. `end_time: 1:00 PM` (matches the publicly advertised band slot of "11–1" in the invitation text). Ran propagators — JSON-LD now at 12 entries (was 13), BIT CSV regenerated without the past event.
- **Why it fell through:** Phase 5 was purely manual; nothing flagged the past-dated entry. No propagator runs between the show date and now, so no opportunity to catch it.
- **Added** `tools/check-stale-events.py` — scans `events.json` for past-dated entries and prints a Phase 5 reminder; exits non-zero if drift exists.
- **Wired** the check into `tools/run-propagators.sh` as a non-blocking warning at the end (catches drift any time propagators run, which happens on any events.json edit).
- **Added** a "Before working with shows" section to `CLAUDE.md` (local, gitignored) instructing Claude to run the same check at the start of any session that touches events, past-shows, or pipeline review (catches drift even when no events.json edit is happening).

Side-effects Paul confirmed: none — site/data changes only.

## 2026-05-18 (mid) — Poster wiring across Side Saddle + Wild Heaven shows

- **Added** `assets/posters/side-saddle-summer-series-2026.jpeg` — referenced by all 8 Side Saddle summer-series events in events.json (file was missing from a prior session's events.json update).
- **Added** `assets/posters/side-saddle-2026-02-27.png` and wired it into the Feb 27 Side Saddle past-show entry (only Side Saddle past show that had been missing a poster).
- **Added** `assets/posters/side-saddle-2025-12-19.png` and wired it into the Dec 19 Side Saddle past-show entry; also added Dirty Shame to that entry's `supporting_acts` (per the poster lineup).
- **Added** `assets/posters/wild-heaven.png` (Bolo Boys / Dirty Shame / Acoustic Station gig flyer, Avondale patio) and wired it into all six Wild Heaven entries — five past (`wild-heaven-toco-hills-2026-04-26`, `-04-12`, `-03-29`; `wild-heaven-avondale-2026-04-04`, `-03-20`) and one upcoming (`wild-heaven-avondale-2026-05-23`).
- **Ran** `tools/run-propagators.sh` after the events.json edit. Regenerated JSON-LD (13 entries), bumped sitemap `<lastmod>`, regenerated `bandsintown-upload.csv`.

Side-effects Paul confirmed: none — site/data changes only.

## 2026-05-18 (later) — Band update email + master song book audit

- **Drafted + sent** Bolo Boys update email to John + Nigel covering: 5/17 Grant Park recap (Skyler / Summer Shade gazebo opportunity / fall Market series / pending GPC post), Summer Shade prioritization + August Side Saddle reschedule (asks for everyone's August availability), 5/25 setlist build (Boys Don't Cry, Roadrunner, Muddy Knees, Glow as seeds), Side Saddle poster review with Drive link, and Ideal shows detail-confirmation ask for John's point of contact.
- **Audited** `Bolo Boys Master Song and Gig Book.xlsx` on `boloboysband@gmail.com` Drive (file ID `1NkTzrLHH9hzooOT7x8R-HZ0ZKwgGZgOg`). Cross-referenced against Nigel's tab-share emails and Paul's originals docs. Findings: 6 songs missing from the Song List sheet entirely (Boys Don't Cry, 21 Questions, Kids, Roadrunner, Glow, Muddy Knees); 1 row (TN Stud) in master but Tabs cell empty despite Nigel's PDF chart from 2025-11-13; 22 other rows have empty Tabs as a general gap.
- **Delivered** `~/Desktop/bolo-song-list-additions.csv` — 6 ready-to-paste rows matching the master sheet's column schema. Paul executes the paste; Drive MCP can't update xlsx in place.

Side-effects Paul confirmed: band update email sent to `jcwilber4340@gmail.com` + `nigelwrightmusic@gmail.com`.

## 2026-05-18 — GSC notifications triaged (no code changes)

- **Reviewed** three Google Search Console notifications for boloboys.band: welcome email (5/13), Events structured-data "missing fields" (5/14), and page-indexing reasons (5/18).
- **Verified** against live site (`curl https://www.boloboys.band`) that the JSON-LD already emits `description`, `organizer`, `endDate`, and `image` for every event — the 5/14 GSC report is a stale crawl from before the 5/06 restructure. No edits needed to `tools/events-to-jsonld.py`.
- **Confirmed** the 5/18 indexing reports cover only `http://boloboys.band/` and `http://www.boloboys.band/` — both correctly redirect/canonicalize to the HTTPS canonical via Cloudflare. Working as intended; validation already running in GSC.
- **Outstanding** (no action this session): the 11 events without `poster_url` still fall back to `band-photo.jpg` for `image` — see [[project_bolo_boys_open_threads]].

Side-effects Paul confirmed: none — diagnostic only.

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
