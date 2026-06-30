# Bolo Boys — Changelog

Date-stamped one-line summaries of meaningful state changes. Newest first. Companion to the git log; `git log` has the full diff per commit.

---

## For band emails

Rolling subsection: what's worth telling Nigel and John in the next band-update email. Distinct from the per-session changelog below (which is for the audit trail). Curate down to the items that matter to a touring trio reading on their phone — new shows, venue changes, press, ops-layer wins. Empty by default after each email goes out; refills as the next cycle's items accumulate.

*(No items queued for the next email as of 2026-05-21.)*

---

## 2026-06-30 — Per-show lineups recorded in events.json + JSON-LD/sitemap refresh

Triggered by Paul's scheduling updates from Jamey + a "schedule email with expected attendance" request.
- **data/events.json** — per-show lineup deviations recorded in `prep.logistics_notes`: 7/11 (Jamey out, no drums), 8/15 (John out), 9/12 (Bolo w/o John + Ante Up, Jamey on drums; replaced stale "Paul + Nigel duo" note), 10/31 (Jamey out).
- **index.html / sitemap.xml** — propagator refresh (JSON-LD `validFrom` 6/27→6/30; sitemap lastmod).
- Band-facing side effects (other surfaces): shared-calendar invites annotated with lineups; Jamey's 12 personal-copy duplicate events merged into the shared invites + deleted; "who's on for what" schedule email drafted in Gmail.
- **Phase 5 cleanup** — moved the two played shows (6/26 Ideal "First Night in Lakewood", 6/27 Side Saddle "World Cup Saturday") from events.json → past-shows.json (lighter schema; 6/26 end 10 PM, 6/27 end null pending Paul's actual). Upcoming 12→10; past 18→20. Regenerated JSON-LD/BIT CSV.

## 2026-06-27 — Summer Shade Festival booked + Grant Park Porchfest 2027 lead

Don booked Bolo Boys for the **Summer Shade Festival** gazebo stage — Sat **2026-08-22, 12:15–1:00 PM** in Grant Park, closing the gazebo pursuit open since May (Skyler → Don). Added new venue `summer-shade-festival` to `data/venues.json` and announced show `summer-shade-festival-2026-08-22` to `data/events.json` (phase `announced`, theme "Gazebo Stage", 0.75h festival set, poster null). `data/scene-events.json`: marked the 8/22 Summer Shade entry as now a Bolo Boys show (not just a competing event). Ran propagators — JSON-LD now 12 MusicEvents, sitemap bumped, Bandsintown CSV regenerated (**1 new row to upload — Summer Shade; BIT appends, so upload only that row**). Private repo: added contact `summer-shade-don` (last name/email/phone TBD — get from Paul), updated Skyler/Josh notes to close the Don thread, and recorded **Grant Park Porchfest** as a warm lead — Don's verbal invite for Sat **2027-03-20** (porch/time TBD); bumped the scene-events Porchfest entry to 2027-03-20; regenerated `docs/venue-contacts.md`. Calendar (done 2026-06-27): updated the shared-calendar Summer Shade hold → confirmed timed event (12:15–1:00 PM) and added the full core roster — Nigel, John, Paul, **Jamey** (drummer, core since 6/24) + band acct; created a tentative all-day Porchfest hold for 2027-03-20 with the same roster. BIT upload deliberately **held** per Paul ("hold off on BIT") — captured as a backlog item in the private OPEN-THREADS.md (1 new Summer Shade row to upload when ready). Still pending (Paul go): IG collab + announce. 6/26 Ideal held in events.json per Paul (will trip stale-check until moved).

## 2026-06-26 — Homepage restructure + new EPK page (ux-reviewed)

Landed the held website-enhancement build after a `ux-expert` review pass. `index.html` restructured: the hero now leads with a filled "Upcoming Shows" primary, then "Follow" / "EPK" (demoted to a small chip) / "Tip the Band"; the old About section merged into a single "The Band" (`#connect`) section nesting bio / photo / originals / follow / scene / Past Shows; Past Shows is an auto-cycling poster carousel (5.5s, pauses on touch/hover) + a "see all shows" dropdown. New standalone `epk.html` booker press kit (who / sound / proof / logistics / contact) with an embedded live video ("Tennessee Stud"), a 3-poster identity row (Side Saddle / Ideal Sports Bar / Grant Central East), and a Photos gallery. ux fixes from the review (consolidated findings in `.ux-reviews/2026-06-26-consolidated.json`): the hero follow CTA routes to the follow links instead of the bio, Instagram-led follow list with email set apart, honest Drive/gallery affordance labels, consistent mailto subjects. No `data/` changes, so no propagator run.

## 2026-06-25 — Themed Ideal shows + wired 6/27 World Cup IG post

Themed the two Ideal Sports Bar shows by populating their previously-null `theme`: `6/26` → "First Night in Lakewood" (debut) and `7/11` → "Round Two". `theme` flows into the JSON-LD event `name` (`"Bolo Boys at Ideal Sports Bar — {theme}"`) — the headline Google shows in event results — so the listings now read richer and more clearly Bolo Boys instead of a bare venue name. Also wired the `@boloboysband` World Cup Saturday IG post into the `6/27` Side Saddle show's `external_links` ("Around the web"). Ran propagators: JSON-LD regenerated (only content changes are the two Ideal names; the rest is `validFrom` ticking 6/21→6/25), sitemap `<lastmod>` bumped, Bandsintown CSV regenerated. BIT NOT re-uploaded (appends → dupes — edit the two Ideal events in the BIT UI if the themed names are wanted there). Companion rule codified in CLAUDE.md Phase 2: theme null only when there's genuinely no angle; `poster_url` strongly-preferred-not-a-blocker.

## 2026-06-21 — Google "hip-hop" mislabel fix + Ideal IG post wired

Ideal Sports Bar's Google listing was tagging Bolo Boys' shows as "Hip-hop/rap" — Google's Knowledge Graph conflating the band with the German hip-hop "Bolo Boys." Root cause is entity confusion, not a bad genre field (the Bandsintown genre was already correct). Fixed the signals we control: added the Bandsintown profile to the `MusicGroup` `sameAs` in `index.html` (mirrored canonically in `data/band.json`) so Google links the entity to the right profile. Separately, wired the `@boloboysband` IG announce post into both Ideal shows' (`6/26` + `7/11`) `external_links` — renders in the "Around the web" block. Paul also corrected/expanded the Bandsintown genres (fixed the "Raggae" typo) and added an honest similar-artists cluster in the BIT dashboard. No JSON-LD event drift (propagators clean). Remaining lever is Google's own re-crawl + a possible knowledge-panel "Suggest an edit" — logged as a Paul to-do for early July.

## 2026-05-29 — 9/12 Side Saddle lineup change

Updated the 2026-09-12 "Between the Festivals" Side Saddle show: co-bill reduced to Ante Up only (Dirty Shame + Acoustic Station off the bill); added an internal prep note that John is out and Bolo Boys plays the night as a Paul + Nigel duo. `supporting_acts` doesn't feed JSON-LD or the Bandsintown CSV, so no band-facing surface changed; propagators bumped `validFrom`/`<lastmod>` to today as a side effect. No BIT re-upload triggered by this change.

## 2026-05-29 — songs.json finalized (status → complete)

Flipped `data/songs.json` `_meta.status` from `backfilled-draft` to `complete`; Paul accepted the 64-song backfill as the canonical repertoire. The inferred genres + rotation flags stand as the backfill-time inferences (correctable in a later edit). Closes D-OPEN-3 item 2.

## 2026-05-28 — songs.json backfilled to full repertoire (D-OPEN-3 item 2)

- **`data/songs.json`** — expanded from the 8-song seed to **64 songs**, sourced from the Drive master songbook ("Bolo Boys Master Song and Gig Book.xlsx"), Nigel's tab emails (5/11 covers + 11/2025 Christmas), and Paul's 5/11 consolidated list. Each song carries tabs + YouTube links where available.
- Schema → v1.2: added a `holiday` genre for the Christmas set; `confidence` nulled and the songbook count-off column disregarded per Paul; `lead` field dropped.
- Genres and rotation flags are inferred (flagged in `_meta.status_note`) pending Paul's review; status is `backfilled-draft`.

No band-facing side effects (data-only; not rendered on the live site).

---

## 2026-05-26 — Phase 5 cleanup: Wild Heaven 5/23 + Grant Central 5/25 moved to past-shows

- **`data/events.json`** — removed `wild-heaven-avondale-2026-05-23` (Saturday Session at Wild Heaven, 4-hour run with Dirty Shame + Acoustic Station + Ante Up) and `grant-central-pizza-2026-05-25` (Memorial Day at the Grant Ole Opry with Adam Klein + Adam Poulin). 10 upcoming events remain. `_meta.last_updated` → 2026-05-26.
- **`data/past-shows.json`** — prepended both with the lighter Phase 5 schema. Wild Heaven entry captures the spring-run wrap and the multi-act rotation (end_time 8:00 PM); Grant Central captures the first-booking + Grant Ole Opry debut framing (end_time 9:15 PM). External_links preserved (Wild Heaven IG concert-series post + both Grant Central IG posts).
- **`index.html`** — JSON-LD regenerated, now lists 10 MusicEvent entries.
- **`sitemap.xml`** — `<lastmod>` bumped.
- **`bandsintown-upload.csv`** — regenerated (10 events + header).

Band-facing side effects:
- Bandsintown UI still shows the two played shows as live events — manual delete required in the BIT UI (CSV regen doesn't push deletes). After deleting, run `bash tools/mark-bit-upload.sh`.
- IG thank-yous to Wild Heaven, Grant Central, and Adam Klein still pending (deferred this session).
- Phase 5 step 6 press scans for both shows still pending.

---

## 2026-05-23 — Tip button polish: top of Connect, open-jar icon, hero CTA

- **`index.html`** — Gas Money card moved from last to first in the Connect list (more prominent than the soft-ask-at-end position). Swapped the mason-jar-with-`$` icon for an open jar with a coin floating above it (more active "tip going in" read). Added a smaller secondary `hero-cta-tip` button under the existing Upcoming Shows / Connect / About CTAs in the hero: same uppercase/border style, narrower padding, lighter border, jar+coin icon inline, text "Tip the Band," same Venmo destination.

No band-facing side effects beyond the new placement + button.

---

## 2026-05-23 — "Gas Money" Venmo tip button in Connect

- **`index.html`** — added new `social-item` after Bandsintown linking to `https://account.venmo.com/u/nigelwrightmusic` (Nigel's Venmo, used as the band tip handle). Stroke-outline mason-jar-with-`$` icon to match the rest of the Connect row. Name "Gas Money," handle `Venmo · @nigelwrightmusic` (Venmo prefixed so visitors know what the link will open).

No band-facing side effects beyond the new button.

---

## 2026-05-23 — `.gitignore` excludes `*.bak`

- **`.gitignore`** — added `*.bak` pattern; removed orphaned `data/events.json.bak` (yesterday-dated editor backup with a trivial `done` flag diff). Future editor/tool backups won't litter the working tree.

No band-facing side effects.

---

## 2026-05-23 — Bandsintown upload tracking hardened (md5 + dedup warning)

- **Discovered:** BIT appends on CSV upload and does NOT dedupe by event ID. Re-uploading the same CSV creates duplicates that must be manually deleted in the BIT UI. Paul did this manually on the 2026-05-23 re-upload before the warning existed.
- **`CLAUDE.md`** (private repo, mirrored to public via symlink) — Phase 2 step 9 now warns about the append-not-dedupe behavior and the "upload only new rows, or be ready to delete duplicates" workaround. Open backlog item logged in `project_bolo_boys_open_threads.md` for a smarter upload workflow.
- **`tools/mark-bit-upload.sh`** — sentinel now stores the **md5** of the CSV at upload time (not just a touch). Surfaces a "BIT appends" reminder before marking.
- **`tools/run-propagators.sh`** — upload-needed check switched from mtime comparison to md5 comparison. Idempotent reruns that don't change CSV content no longer trigger false "upload needed" warnings. Reminder now includes the dedup warning prominently.
- **`~/.claude/skills/bolo-status/SKILL.md`** — Bandsintown upload-status check updated to match (md5-based, with dedup warning baked into the "upload needed" flag).

No band-facing side effects beyond the manual BIT cleanup Paul already did.

---

## 2026-05-23 — Bandsintown upload tracking + propagator regen

- **`tools/mark-bit-upload.sh`** (new) — single-purpose script that touches `tools/.last-bit-upload` (gitignored local sentinel) to mark "I just uploaded the current CSV to Bandsintown." Run after every BIT upload.
- **`tools/run-propagators.sh`** — now prints a "⚠ Bandsintown CSV regenerated — upload to BIT" reminder at the end of every run, with instructions to mark via `mark-bit-upload.sh`. Catches the "regenerated but never uploaded" drift mode that surfaced this session (the audit found Paul had not uploaded yesterday's regen).
- **`.gitignore`** — excludes `tools/.last-bit-upload` (local-only state).
- **`index.html` + `sitemap.xml`** — propagator regen artifacts: JSON-LD `validFrom` bumped 2026-05-22 → 2026-05-23 across all 12 event entries; sitemap `<lastmod>` bumped to 2026-05-23. Pure date-stamp updates, no structural changes.
- **`~/.claude/skills/bolo-status/SKILL.md`** (user-skills, not in repo) — new Bandsintown freshness check uses the sentinel to detect upload drift, in addition to CSV-vs-events drift and content drift.

**Band-facing side effects:** Bandsintown CSV needs re-upload from `bandsintown-upload.csv` (Paul handling now). Two Ideal Sports Bar events (6/26, 7/11) still lack posters — known gap, not blocking.

---

## 2026-05-21 — Show-prep system sketched as D-OPEN-3 (design only, not built)

- **`Bolo Boys - Private/DECISIONS.md`** — added `D-OPEN-3. Show-prep system`. Three-piece design intent: (1) optional `prep` field on each event in `events.json` (band-facing prep state, distinct from `additional_details`); (2) new `data/songs.json` as canonical repertoire; (3) new `/show-prep` skill as read-only audit, sibling to `/bolo-status` Section 2. Build trigger: next time the prep gap bites (likely 5/23/5/25 Ante Up coordination).
- **Why now:** surfaced when computing "leftover songs for Ante Up to play 5/23" required a canonical repertoire that doesn't exist. Each show has unique prep dimensions (5/25 = no music stands; 5/31 = anniversary morning; 6/27 = World Cup weather contingency) and there's no single place that answers "is X ready?"
- **Held back per Paul's direction:** sketch only, don't build. Detailed shape + open design questions captured in DECISIONS.md for future-session pickup.

No band-facing side effects.

## 2026-05-21 — Summer Shade 2026 dates corrected in scene-events.json

Confirmed via web research that the 24th annual Summer Shade Festival is **2026-08-22 / 2026-08-23**, not the historical "last weekend of August" pattern. Previous scene-events.json entry had it on 2026-08-29 / 30 — wrong.

- **`data/scene-events.json`** — `summer-shade-festival` entry: `next_known_start` 2026-08-29 → 2026-08-22, `next_known_end` 2026-08-30 → 2026-08-23. `pattern` and `notes` updated to reflect the 2026-specific date and the verification path (Eventeny + Adventures in Atlanta, 2026-05-21).
- **Implication for the 2026-08-29 Side Saddle show:** no longer a Summer Shade conflict — it's the weekend AFTER Summer Shade. Future `/bolo-status` runs will no longer flag 8/29 in Section 4 conflicts.
- **Google Calendar (Bolo Boys shared) — 8/29 event:** title "Side Saddle Saturday Show - Last Saturday in August," description "Last Saturday in August. Hopefully gives us a break from July/August heat." No Summer Shade reference to remove — calendar invite is already clean.
- **Side observation surfaced:** `/bolo-status` Section 5 (Venues needing research refresh) reads `research_date` from `venue-contacts.json`, but actual venue research lives as `last_researched` in `venues.json`. All 11 active venues are fresh as of 2026-05-11 (or fresher) — no research actually needed. Skill edit to fix Section 5 + add Section 6 (Attractive open dates) was blocked by auto-mode permissions for self-modification; needs Paul's explicit approval to land.

No band-facing side effects.

## 2026-05-21 — Past-show + Avondale series IG URLs wired into external_links

Continuing the paste-and-wire batch. Paul pasted IG post URLs for past shows + the Wild Heaven Avondale concert series.

- **`data/past-shows.json`** — 9 new `external_links` entries appended across 7 past shows:
  - `gateway-park-grant-park-2026-05-17` (Market in the Park) — band's IG post joins existing Aha! Connection + Caren West PR coverage.
  - `side-saddle-2026-02-27` — patio show w/ Dirty Shame + Acoustic Station.
  - `side-saddle-2026-01-30` — monthly Atlanta showcase w/ Dirty Shame.
  - `side-saddle-2025-12-19` — holiday show w/ Dirty Shame.
  - `because-coffee-2025-12-13` — Christmas celebration in Dawsonville.
  - `cultivation-brewing-2025-12-12` — second annual Cultivation showcase w/ Dirty Shame.
  - `echo-art-gallery-2025-10-18` — Westside.
  - `wild-heaven-avondale-2026-03-20` + `wild-heaven-avondale-2026-04-04` — same Wild Heaven Avondale concert-series IG post wired to both past Avondale dates.
- **`data/events.json`** — same Avondale concert-series URL wired to the upcoming `wild-heaven-avondale-2026-05-23` (one URL spans the series across past + upcoming, similar to how the summer-series URL spans the three SS summer dates).
- **`_meta.last_updated`** bumped to 2026-05-21 on both files.
- **`bandsintown-upload.csv`** — regenerated. JSON-LD + sitemap already in sync (external_links isn't reflected in either).

Side-effect Paul flagged: the Avondale URL is plural ("avondale shows"). I interpreted as the concert series and wired it to all 3 Avondale dates (1 upcoming + 2 past). Worth verifying it actually covers the whole series vs. one specific date.

## 2026-05-21 — IG post URLs wired into events.json external_links

- **`data/events.json`** — 4 events gained an `external_links` entry via the paste-and-wire workflow:
  - `grant-central-pizza-2026-05-25` — appended the Bolo Boys' own Memorial Day announcement to the existing array (Adam Klein's promo was already there).
  - `side-saddle-2026-05-31`, `side-saddle-2026-06-27`, `side-saddle-2026-07-19` — same summer-series IG collab post wired into all three (announces three dates at once on the band's IG, co-published with @sidesaddlewine + @fincatofilter).
  - `_meta.last_updated` bumped to 2026-05-21.
- **`bandsintown-upload.csv`** — regenerated. JSON-LD + sitemap already in sync from earlier this session.
- Both posts went out from `@boloboysband` (Instagram); paste-and-wire titles match the band-voice tone established in the existing 5/25 external_link.

No band-facing side effects (the posts are already live; this only updates the "Around the web" rendering on boloboys.band).

## 2026-05-21 — Side Saddle + Finca to Filter IG handles captured in venues.json

- **`data/venues.json`** — added `instagram` + `instagram_handle` fields to `side-saddle` (`@sidesaddlewine`) and `finca-to-filter` (`@fincatofilter`). Source-of-truth for future captions that tag these venues; previously the handles lived only in Paul's head. `_meta.last_updated` bumped to 2026-05-21.
- **JSON-LD / sitemap / `bandsintown-upload.csv`** — regenerated via `tools/run-propagators.sh` (no functional change since IG handles aren't in event-level data, but propagators are idempotent and CLAUDE.md says "after any data/ change").
- **Side Saddle Summer Series IG caption** — drafted in conversation (warm-welcome + bridge-coming framing, three summer dates, four-band rotation, tags + hashtags). Saved to Drive as a working doc.

No band-facing side effects yet (caption pending Paul's post).

## 2026-05-21 — Operating-layer skill + DECISIONS.md

- **`Bolo Boys - Private/DECISIONS.md`** — new file. Captures the dashboard archival (2026-05-19), the Markdown pivot via `/bolo-status` Skill, and the load-bearing data-model invariants (`phase` field, `venue-contacts.json` canon, `scene-events.json` for conflicts). D1–D5 locked; D-OPEN-1 (citizen-science) + D-OPEN-2 (sync-band-sheet OAuth) captured as in-flight. Per the W1a portfolio audit's recommendation that Houseplants' DECISIONS.md is the model pattern; Bolo Boys is the second project to adopt it.
- **`~/.claude/skills/bolo-status/SKILL.md`** — new Claude Code Skill. Read-only Markdown digest with five sections: Pipeline by phase, Ownership flags, Open leads (with staleness flags), Calendar gaps + conflicts, Venues needing research refresh. Reads `data/events.json`, `data/past-shows.json`, `data/scene-events.json` (public repo) + `data/venue-contacts.json` (private repo). Invoke with `/bolo-status` anywhere Claude Code is running.
- **`CHANGELOG.md`** — new `## For band emails` subsection at the top of this file (above the per-date entries), feeding future "since last update" emails to Nigel and John.
- **Held back:** `sync-band-sheet.py` OAuth setup remains a Paul-only manual step (Google Cloud project + consent flow, ~30 min). Skill works against the JSON files in the meantime; switching to the sheet as the source-of-truth waits for OAuth to land.

## 2026-05-20 (latest) — Finca to Filter integration + Side Saddle 5/31 time locked

Cross-promo for Side Saddle's sister venue Finca to Filter (same owner Kayla Bellman, same address 680 Hamilton, shared patio). Lets boloboys.band, calendar invites, and the Bolo Boys IG audience all see both businesses surfaced as a single anniversary celebration on 5/31 and an ongoing patio identity for the rest of the SS series.

- **`data/venues.json`** — new `finca-to-filter` venue entry (coffee shop, 7 AM–3 PM, queer/woman-owned, sister to Side Saddle). New optional `sister_venue_id` field cross-links Side Saddle ↔ Finca to Filter both ways. Side Saddle's `notes` updated to reflect the sister relationship. `_meta.schema_notes` documents the new field.
- **`data/events.json`** — added `partner_venue` field (`{id, name, instagram}`) to all 8 upcoming Side Saddle events; consumed by the UI for the dual-venue card render (no propagator impact — JSON-LD/BIT CSV still use single `venue_name`). 5/31 specifically: `time` 11:30 AM → 11:00 AM, calendar URL timestamps 113000/133000 → 110000/130000, `invitation_text` fully rewritten for the dual-business anniversary, `additional_details` updated to reflect "Side Saddle + Finca to Filter shared 1-year anniversary weekend." 6/27, 7/19, 8/29 got light-touch invitation_text swaps ("Side Saddle patio" → "Side Saddle + Finca to Filter patio"). All 8 events' `google_calendar_url` details param now reads "Bolo Boys live at Side Saddle + Finca to Filter — ..."
- **`data/past-shows.json`** — backfilled `partner_venue` on 5 past Side Saddle shows so the historical block also renders the dual name.
- **`index.html`** — collapsed event card now appends `<span class="event-partner-venue">+ Finca to Filter</span>` inline after the `event-venue-name` when an event has a `partner_venue`. Same treatment in the past-shows row via `.past-show-partner-venue`. New CSS keeps the partner subtle (font-weight 500, slightly smaller, gray) so the primary venue stays dominant. `title` attribute carries the combined name for screen readers.
- **JSON-LD / sitemap / `bandsintown-upload.csv`** — regenerated via `tools/run-propagators.sh`. JSON-LD MusicEvent.location and BIT CSV stay correctly anchored on Side Saddle (the bookable venue); partner_venue is UI-only.
- **`Bolo Boys - Private/data/venue-contacts.json`** — new `finca-to-filter` venue_relationship (status: regular, summary explains the sister-venue dynamic). New parallel contact `finca-to-filter-kayla-bellman` so searches by FtF venue_id surface Kayla without schema-changing to multi-venue contacts. Side Saddle entry's notes updated to point to the parallel record. `last_compiled` 2026-05-20.
- **`Bolo Boys - Private/docs/venue-contacts.md`** — regenerated via `tools/contacts-to-markdown.py`.
- **Google Calendar (Bolo Boys shared)** — 5/31 event description rewritten with the locked 11 AM–1 PM time and the dual-business anniversary framing; event stayed all-day to match the other 7 SS events' established pattern (locked time lives in the description). 7 other SS events' descriptions updated with light FtF cross-references. Notifications silenced.
- **Held back:** sending Keith Ideal Sports Bar artwork for the venue-designed flyer (Keith offered to design + send for approval if Bolo Boys provides the art); IG post for the Side Saddle Summer Series (caption drafted, needs Paul's final approval); Side Saddle performer email (blockers cleared, ready to draft).

Side-effects Paul confirmed: GCal updates land silently (notificationLevel NONE on all 8 SS event updates). No band-facing IG post yet.

## 2026-05-20 — Ideal show details locked + venue contacts updated

- **`data/events.json`** — Ideal Sports Bar 6/26 + 7/11: `duration_hours` 3 → 2 (locked at 8–10 PM per Keith confirmation), dropped "subject to confirmation" language from `additional_details` and the calendar URL details param. `google_calendar_url` rewritten with proper `YYYYMMDDTHHmmSS/YYYYMMDDTHHmmSS` timestamp format (was date-only, which would have rendered as an all-day event).
- **`index.html` / `sitemap.xml` / `bandsintown-upload.csv`** — regenerated via `tools/run-propagators.sh`.
- **`Bolo Boys - Private/data/venue-contacts.json`**:
  - **Josh Peatross → Josh Patterson** — last name was transcribed wrong; contact card confirms Patterson. Added phone (770) 289-1521. ID renamed `gpc-josh-peatross` → `gpc-josh-patterson`. Last-contact updated for the 5/20 GPC email.
  - **Skyler Edwards** — added phone (678) 670-6256. Last-contact updated for the 5/20 GPC email.
  - **Added** Ceci Villanueva (GPC photographer / recap content, tertiary scope, phone (404) 698-7626, no email captured).
  - **Added** Keith (Ideal Sports Bar primary booking contact, phone (678) 633-4251, text preferred, designs venue flyers from band-supplied artwork). Ideal `venue_relationships` entry simplified — dropped the stale "no_direct_contact_note" now that Keith is logged.
  - `last_compiled` bumped to 2026-05-20.
- **`Bolo Boys - Private/docs/venue-contacts.md`** — regenerated via `tools/contacts-to-markdown.py`.
- **Google Calendar (Bolo Boys shared)** — both Ideal events updated: end time 11 PM → 10 PM, description rewritten with confirmed times + Keith's text contact. Notifications silenced (calendar UI shows the update; no email push).
- **Memory** — `feedback_paul_internal_voice.md` extended with patterns observed in Paul's edits to the GPC email (venue/partner register vs. bandmate register; PS-carries-relationship-ask; give-offers; date-prefix anchors; honest-tell humanizers).

Side-effects Paul confirmed: GPC email sent (Skyler + Josh; CC John + Nigel; subject "Bolo Boys — Summer Shade + Market in the Park"); Bolo Boys shared calendar events updated for 6/26 + 7/11.

## 2026-05-20 — Venue-review press scanner: explicit + implicit modes

- **`tools/press-scan.py`** — added `--mode {explicit,implicit,all}` flag (default `explicit`, so Phase 2 / Phase 5 cadence is unchanged). New `venue-review` tag adds two band-wide queries (`site:yelp.com OR site:google.com/maps`, broad `review`) plus per-recurring-venue queries (`"Bolo Boys" "<venue>" review`) for any venue with ≥2 past plays. New `implicit_targets` output (only emitted under `implicit` / `all`) ships per-venue review URLs, show dates with co-bills, a 14-day match window, and language signals so Claude can execute the implicit playbook per CLAUDE.md. Output shape changed from a bare array to `{"queries": [...], "implicit_targets": [...]}`.
- **`data/venues.json`** — new optional fields `yelp_url` and `google_reviews_url` on Side Saddle (5 past plays), Wild Heaven Avondale (2), and Wild Heaven Toco Hills (3). Yelp URLs populated; Google reviews URLs left null until next-touch research. Other venues unchanged.
- **`tools/press-scan-excludes.json`** — new `implicit_language_signals` key (15 live-music terms — "live music", "trio", "guitar", "acoustic", "harmonies", etc.) as the single source the script and playbook agree on for implicit-match scoring.
- **CLAUDE.md** — Press scanner section gained a **Modes** subsection (explicit default, implicit on-demand, never auto-wire) and a full **Implicit verification playbook** (date filter → language signal → different-band filter → confidence label → per-candidate Paul verification). Workflow step 6 updated to call for the two new scan-report sections in implicit/all runs.
- **No band-facing side effects yet.** No scan executed; no `external_links` wired. Pilot run on Side Saddle's Yelp reviews is the next step.

## 2026-05-19 — Mobile event cards: consistent height, time always-on, business-resolving maps links

- **Two-line collapsed card with fixed slots** — venue name (line 1, ellipsis if it overflows) + one secondary signal (line 2). Cards now stack at consistent height regardless of which optional fields a show has. `min-height: 80px` on mobile (<480px).
- **Secondary line always leads with the time** as a charcoal-bold prefix — `8 PM · w/ Adam Klein`, `11:30 AM · w/ Dirty Shame`, `8 PM · Lakewood Heights`. Time is never hidden. Trailing context follows precedence: **co-bill > theme > city**. `8:00 PM` collapses to `8 PM` for display; `11:30 AM` stays intact.
- **Maps icon restored** to the mobile collapsed-card action cluster. Mobile cluster now reads: location pin (directions) → calendar → chevron. Icons scale to 36×36 at <480px and 34×34 at <400px to keep the info column wide enough for the venue name.
- **Maps URLs now resolve to the business**, not just the address — every `?q=<address>` in `venues.json` and `events.json` was rewritten to `?q=<venue name>,<address>`. 9 venues + 12 events updated programmatically. Gateway Park's existing `maps.app.goo.gl` short link preserved (already place-pinned). Bandsintown CSV regenerated to stay in sync.
- **Expanded view backfills** time + neighborhood + supporting acts so nothing displaced from the collapsed line is lost. Theme still renders as the green-uppercase section header at the start of the expanded panel.
- **`.ux-reviews/2026-05-19-mobile-card-consistency.json`** — follow-up review from the ux-expert agent (re-engaged after Paul's reaction to the first iteration). Captures the "card-height was actually a composition problem" reframe.

## 2026-05-19 — Mobile UX polish for event cards + poster lightbox

- **Past-shows posters un-cropped** — `.past-show-poster` went from 40×40 square crop (which center-cut the hand-illustrated lettering on portrait posters) to 32px wide × auto height. Past Shows now actually surfaces the band's accumulated identity instead of indistinguishable colored chips.
- **Mobile collapsed cards tightened** — under 480px: poster thumb hidden, calendar icon hidden (redundant with the expanded-view pill), date block narrowed (42px → 36px), DOM dropped to 1.5rem, divider line removed. Chevron is the lone signifier on the right; venue info gets the breathing room.
- **Action button gap** bumped 2px → 8px universally — was tap-target-adjacent on mobile.
- **Poster lightbox modal:** 150ms fade-in on open/close via JS class toggle, hint caption added ("Pinch to zoom · tap outside to close"), and `margin: auto` restored on `#poster-modal` — the global `* { margin: 0 }` reset was zeroing the dialog's default auto-margin and pinning showModal() to the top-left corner.
- **`.ux-reviews/2026-05-19-mobile-poster-interaction-and-event-cards.json`** added — screen-component review from the ux-expert agent that drove these changes. Includes three candidate principles flagged for future Mode-2 distillation.
- **Deferred:** F4 (zoom-glyph overlay on expanded poster) — wait to see if it's still needed after this lands. F10 (pinch-zoom) — resolved, confirmed working natively. Card-height consistency on mobile — captured as the next iteration in a follow-up review at `.ux-reviews/2026-05-19-mobile-card-consistency.json` (will ship in the next commit).

## 2026-05-19 — Visual design principles doc + Ideal Sports Bar logo banked

- **`design/principles.md`** created — decodes the Side Saddle poster visual system (two-color on black, single iconic illustration, fixed furniture: logo TR / QR BR / lineup ticker bottom), names the rules, includes Firefly/Photoshop prompt scaffolding, and ends with the Ideal Sports Bar open thread for handoff to the next session.
- **`assets/misc/ideal-sports-bar-logo.png`** — third-party venue logo banked from a desktop drop; renamed to match the "Ideal Sports Bar" normalization. Logo is retro varsity red+yellow; future posters should contrast the palette, not match it.
- **CLAUDE.md** — one-line pointer added in the "When in doubt" section: "About visual design (posters, flyers, illustration prompts): see `design/principles.md`."
- **Memory** — open-threads entry for the Ideal poster gap updated with the tabled decision, the three design directions surfaced, and the pointer to `design/principles.md`.
- **Decision tabled:** whether to actually make Ideal Sports Bar posters (2026-06-26 + 2026-07-11). Three directions on the table; brainstorm captured in the principles doc.

## 2026-05-19 — "Who we play with" credibility panel (tier a) live

- **Permanent scene panel** added at the end of the About section (under Original Music). Shows the recurring collaborators from `band.json` `scene_collaborators` — Dirty Shame and Acoustic Station with linked IG handles, Ante Up with a one-line description (supergroup of the three bands). Adam Klein deliberately excluded — he's a one-time guest, captured in `guest_co_bills`, not the recurring scene.
- **Ante Up `note` shortened** to display-worthy content ("Supergroup of Bolo Boys + Dirty Shame + Acoustic Station.") — the prior version mixed display copy with implementation guidance ("render as plain text") that belongs in code.
- Sells the scene-hub angle to bookers without inflating relationships — small, contained, durable (per the tier-a design in the open-threads backlog).

## 2026-05-19 — Maintenance + small fixes

- **events.json** — fixed the DragonCon date typo on Side Saddle 9/12 `additional_details` ("9/4–9/7" → "9/3–9/7"; actual DragonCon 2026 runs Sep 3–7).
- **tools/run-propagators.sh** — clarified the Bandsintown CSV report line. Was `wrote bandsintown-upload.csv (N lines)` which conflated header + data rows. Now reads `(N events + 1 header row)`. Matches the JSON-LD line's reporting convention and removes the apparent JSON-LD (12) vs CSV (13) discrepancy seen earlier in the session — they always agreed; the count was just opaque.
- **PLACEHOLDER.md cleanup** — investigated and confirmed `assets/PLACEHOLDER.md` is already gone (was a stale memory entry, not actually present). Memory note updated.

## 2026-05-19 — Original Music section + click-to-expand posters

- **Original Music** sub-block added at the end of the About section. Spotify embed iframe (152px compact) for Nigel Wright's "The Cowboy's Life" (2026), plus an "Also on:" link row covering Spotify, Apple Music, Amazon Music, Bandcamp (4 platforms confirmed; YouTube Music / Tidal / Deezer captured as `null` placeholders in band.json).
- Credit line clarifies the recording is Nigel's solo recording while Bolo Boys play the song live (so visitors don't read "Bolo Boys play it live" as "the recording features the band").
- **Click-to-expand posters** via a native HTML `<dialog>` modal. All three poster img elements (collapsed-card thumb, expanded-card poster, past-show row poster) now open a centered modal on click. Backdrop / Escape / × button close. `cursor: zoom-in` on the imgs makes it discoverable. No library — ~50 lines of CSS, 8 of JS.
- **band.json loader** refactored: was a scoped `sceneCollaborators` map, now exposes the full `bandData` so the originals section reads from the same single fetch. No extra network round-trip.
- Press-scan excludes file got 4 more noise sources caught in Round 2 of the scanner: `boloboysmke`, `the.boloboys`, `investinlimbe`, `daniellamellodocaria`.

## 2026-05-19 — Press scanner expanded beyond editorial press

- **`tools/press-scan.py`** — 5 new query categories: `social-ig` (`site:instagram.com`), `social-fb` (`site:facebook.com`), `aggregator` ×2 (general Atlanta-calendar query + music-aggregator site-restricted query), and `local-press` (Creative Loafing / AJC / Atlanta Magazine / Atlanta INtown-style show picks). Total queries went 12 → 17 across 7 tags.
- **`tools/press-scan-excludes.json`** — added 6 noise URL substrings caught in the first scan: `boloboys.official`, `bolomusicgroup.com`, `bolobeer.com`, `bolapizza.com`, `bolothedjwebsite`, `michaelbolwaire`.
- **`CLAUDE.md` Press scanner section** — added a "Sources the scanner covers" subsection listing the 7 tag categories and the "Around the web" label. Added a "Paste-and-wire workflow" subsection documenting the manual path (when Paul sees a tag in the wild, paste the URL and we wire it the same way the Adam Klein 5/25 IG post was wired). Added an IG/FB caveat to workflow step 4 (those platforms aggressively block WebFetch — surface URLs for manual confirmation when verification fails).

## 2026-05-19 — Polish + operationalization: scope archive, guest co-bills, label rename

- **Archived `bolo-boys-dashboard-briefing.md`** — moved from public root to `Bolo Boys - Private/_archive/` with a header note explaining what's been absorbed (per-show phase tracking, venue+contact CRM, on-demand pipeline review pattern) vs. what's still gap (promo checklist, weather, BIT sync). Kept the original briefing intact for future reference.
- **`scans/README.md`** added to the private repo — orientation for the press-scan report directory: what scans are, how they flow (queries → filter → verify → group → report → promote to `external_links`), why reports stay as history, and cadence pointing back to the lifecycle phases.
- **Press scan wired into the show lifecycle** — Phase 2 (Announce) step 13 and Phase 5 (Post-show) step 6 now both close with a press scan. CLAUDE.md "Press scanner" Cadence section rewritten to lead with that standard practice.
- **`guest_co_bills` array added to `data/band.json`** — sibling to `scene_collaborators`, for one-time / occasional co-bills we still want to link to but don't want to elevate to the recurring-scene tier. **Adam Klein** is the first entry. `index.html` loader now merges both arrays into one lookup so supporting-acts linking works across both.
- **Label rename: "In the news" → "Around the web"** — better reflects that the field covers articles, listings, IG promo posts, etc. (not just editorial press). One-line CSS-adjacent change in `index.html`.
- **May 25 Grant Central Pizza event updated:**
  - `external_links` now carries Adam Klein's Grant Ole Opry debut IG post (linking back to Bolo Boys).
  - `additional_details` updated to reflect that Adam plays as a duo with Adam Poulin (fiddle) at 7 PM.
- **Memory** — `project_bolo_boys_open_threads.md` refreshed with shipped-this-session items and stale dates corrected (Halfway Crooks 25 days, Subrena Clark 33 days).

## 2026-05-19 — Press scanner built + first scan run

- **New** `tools/press-scan.py` — deterministic query generator. Reads `data/band.json`, `data/events.json`, `data/past-shows.json`. Builds disambiguated queries (band-member names, per-venue, per-co-bill). Dedupes identical queries while preserving associated `event_ids` and contexts. `--pretty` flag for human-readable output.
- **New** `tools/press-scan-excludes.json` — disambiguation filter: blocked domains, URL substrings, and title/snippet keywords for recurring noise (Dierks Bentley's prank "Bolo Boys Bluegrass Band", German hip-hop Boloboys, BOLO the DJ, Bolo's Sports Bar, etc.) plus positive-signal keywords.
- **New** `CLAUDE.md` "Press scanner" section — playbook: trigger patterns, 8-step workflow (generate queries → run searches → filter noise → verify candidates → group by event → write report → wire to site → surface for commit), disambiguation discipline, when-to-update excludes, cadence (on-demand, not scheduled).
- **First scan executed** — 12 unique queries via WebSearch, candidate hits verified via WebFetch. Report at `Bolo Boys - Private/scans/2026-05-19-press-scan.md`.
- **New verified mention** — Caren West PR's 2026-05-13 Market in the Park birthday-bash article quotes the band by name. Added to `gateway-park-grant-park-2026-05-17` past-show's `external_links` alongside the Aha! Connection entry.
- **Notable negatives** — AJC, The Atlanta 100, and ATLNCS all have Market in the Park articles but don't name the band (April-dated, predate the band's involvement). Captured in the scan report for memory.
- **Memory updated** — `project_bolo_boys_name_disambiguation.md` lives in auto-memory and is referenced from the CLAUDE.md playbook.

## 2026-05-19 — Supporting acts now link to co-bill bands' Instagrams

- **Canonical data home** — added `scene_collaborators` block to `data/band.json` (Dirty Shame, Acoustic Station, Ante Up). Ante Up captured with `instagram: null` and a note explaining it's a supergroup with no separate social presence — render-as-plain-text signal.
- **Site rendering** — `index.html` fetches `data/band.json` once on load, builds a name → IG-URL lookup, and `linkSupportingActs()` wraps known names in anchor tags. Unknown names stay plain text. CSS gives the anchor green color + italic inheritance to match the surrounding `.event-supporting` / `.past-show-supporting` styling.
- **Single source of truth cleanup** — removed the duplicate `co_bill_bands` block I'd briefly added to `Bolo Boys - Private/data/distribution-list.json`. Notes in the private file now point at the public band.json as the canonical home for co-bill IG handles.
- **Verified in a local browser session** — Wild Heaven 5/23 card renders "w/ Dirty Shame, Acoustic Station, Ante Up" with the first two linked and Ante Up in plain italic gray.

## 2026-05-19 — Per-event `external_links` ("In the news") on site cards

- **Schema** — added optional `external_links` array on event entries (`events.json` and `past-shows.json`). Each entry: `{title, source, url, date}`. Empty/missing renders nothing. Goal: contextual proof per show — articles, listings, mentions — embedded where bookers and visitors actually look.
- **Rendering** — `index.html` now renders the block in two places: expanded card view for upcoming events ("In the news" label + `Source — Title` list) and inline below each past-show row ("In the news: Source · Source").
- **Backfill** — Market in the Park (`gateway-park-grant-park-2026-05-17`) now links The Aha! Connection's 2026-05-12 birthday-bash coverage. Verified in a local browser session against `127.0.0.1:8765`.
- **Propagators** — ran cleanly; JSON-LD / sitemap / BIT CSV all rebuilt.

Side-effects Paul confirmed: none yet — pending Paul's approval to commit.

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
