# Bolo Boys Operations Dashboard — Advisor Briefing

**Date:** May 17, 2026  
**Prepared by:** Claude (Cowork)  
**For:** Advisor / expert agent review  
**Project:** Bolo Boys band operations dashboard

---

## What this is

This briefing summarizes a dashboard we're planning to build for Bolo Boys — an Atlanta- and Macon-based three-piece band. The goal is a single persistent view that gives Paul (the band's primary organizer) a clear picture of everything in flight: upcoming shows and their status, what needs to be done for each show, and a CRM-style view of venue contacts and co-bill relationships.

The core problem: Paul manages 13+ upcoming shows across multiple venues, a residency at Side Saddle, a full show lifecycle with 5 distinct phases, and a web of venue contacts — all without a single place to see what's done, what's pending, and what's about to fall through the cracks.

---

## The band

**Bolo Boys** — Paul (bass, vocals), Nigel (electric guitar, vocals), John (acoustic guitar, harmonies). Childhood friends + family. Country, folk, reggae, classic rock, and throwback pop, all "Bolo-fied." Based in Atlanta and Macon, GA. Playing regularly since late 2025.

**Active venues:** Side Saddle (monthly residency on the BeltLine), Wild Heaven Brewing (Avondale + Toco Hills), Grant Central Pizza East, Gateway Park at Grant Park, Ideal Sports Bar. Past shows at Cultivation Brewing, Echo Art Gallery, B Complex, Because Coffee.

**Co-bills:** Dirty Shame, Acoustic Station, Ante Up appear regularly. Adam Klein appeared on May 25.

**Web presence:** boloboys.band (live, Cloudflare Pages), Instagram @boloboysband, YouTube, Facebook, Bandsintown.

---

## Current data infrastructure

All data lives as JSON files in the project repo (`/Users/paulkirschenbauer/Documents/Claude/Projects/Bolo Boys/data/`):

- **`events.json`** — 13 upcoming shows through December 2026. Each event has: id, date, time, venue, supporting acts, theme, invitation text, teaser, additional details, Google Calendar URL, poster URL. As of today, a `phase` field has been added to each event.
- **`past-shows.json`** — 14 completed shows back to October 2025. Lighter schema: id, date, time, venue, supporting acts, notes.
- **`venues.json`** — 10 venues with rich data: address, phone, website, summary, what we love, menu highlights, live music context, crowd notes, practical notes.
- **`band.json`** — full member bios, sound philosophy, originals roster, scene affiliations.
- **`data/distribution-list.json`** — email contacts for band members, Acoustic Station / Dirty Shame crew.
- **`Bolo Boys CRM.xlsx`** — spreadsheet with Gig History, Venues & Contacts, and Outreach Pipeline tabs (built May 2026).

---

## The show lifecycle (5 phases)

Defined in `CLAUDE.md`. Each show moves through:

1. **Booked** — confirmed by venue, not yet public. Tasks: calendar invite to all 3 members, capture event details, research venue if new.
2. **Announced** — show goes public. Tasks: enhance with address/maps, theme the show, draft invitation text, build Google Calendar URL, update events.json, update JSON-LD in index.html, bump sitemap.xml, regenerate Bandsintown CSV, reach out to venue for collab IG post, announce on IG.
3. **Promote** — between announce and show day. Lead with collab opportunities; day-of solo post as fallback. No rigid cadence.
4. **Play** — day-of. Bring QR-code flyer. Live posts optional.
5. **Post-show** — thank the venue, pull highlight clips, move event from events.json to past-shows.json, remove from JSON-LD in index.html, re-generate Bandsintown CSV, bump sitemap.xml, commit.

**Phase is now a field in events.json** so status persists and can be updated as shows move through the lifecycle.

---

## Current show pipeline (as of May 17, 2026)

| Date | Venue | Phase | Notes |
|------|-------|-------|-------|
| May 17 (today) | Grant Park Market | play | Birthday party show, outdoors |
| May 23 | Wild Heaven Avondale | promote | 6 days out |
| May 25 | Grant Central Pizza East | promote | Grant Ole Opry series, w/ Adam Klein |
| May 31 | Side Saddle | promote | 1-year anniversary weekend |
| Jun 26 | Ideal Sports Bar | announced | First time at this venue; time needs confirmation |
| Jun 27 | Side Saddle | announced | World Cup group stage final day |
| Jul 11 | Ideal Sports Bar | announced | Second Ideal show; time needs confirmation |
| Jul 19 | Side Saddle | announced | World Cup Final after-party |
| Aug 29 | Side Saddle | announced | Last Call for Summer; weather-dependent |
| Sep 12 | Side Saddle | announced | Between DragonCon and Shaky Knees |
| Oct 31 | Side Saddle | announced | Halloween Bash; weather-dependent |
| Nov 21 | Side Saddle | announced | Pre-Thanksgiving; weather-dependent |
| Dec 19 | Side Saddle | announced | Christmas Party + 1-year series anniversary |

**Flags worth noting:**
- Ideal Sports Bar June 26 and July 11 still have start times listed as "subject to confirmation" — these need to be locked.
- Five Side Saddle shows are outdoor/patio and weather-dependent — weather monitoring matters for those.
- The Side Saddle shows through December represent a committed residency series, not one-offs.

---

## What we're building: the Operations Dashboard

A live, persistent HTML artifact (opens in Cowork) with three panes:

### 1. Shows view
All upcoming shows sorted by date. Each card shows phase badge, date, venue, co-bills, and an expandable checklist of what still needs to be done for that phase. Flags outdoor shows, unconfirmed times, and approaching dates where promo hasn't been done.

### 2. Venues & Contacts (CRM pane)
Pulls from venues.json and distribution-list.json. Shows venue name, contact info, relationship status (Regular / New / Prospecting), shows played count, and last known contact. Eventually could pull from Gmail for last thread date.

### 3. Flags / Action items panel
Auto-surfaced items: outdoor shows with weather checks due soon, shows where time is TBD, post-show cleanup overdue, upcoming shows with no IG post drafted.

---

## Open questions for the advisor

1. **Show lifecycle customization:** The CLAUDE.md lifecycle is generic. Some shows (e.g. Wild Heaven series where the venue handles most promo, vs. a first-time venue like Ideal where we're building the relationship from scratch) have meaningfully different task sets. Should the dashboard support venue-specific or show-type-specific checklist variants?

2. **CRM depth:** Right now the "CRM" is a venues list + a distribution list. Is there value in building out a proper booker contact record (name, email, last contacted, booking notes) for each venue? The xlsx has an Outreach Pipeline tab for prospecting but it's blank.

3. **Phase transitions:** Who triggers phase changes — Paul manually updating events.json, or the dashboard itself? If the dashboard, it needs write-back capability to events.json.

4. **Weather integration:** Several shows are weather-dependent. Should the dashboard pull a live weather forecast for those dates/venues and surface it automatically?

5. **Promotion tracking:** Right now there's no record of which promo tasks have actually been completed (IG posted, Bandsintown updated, collab outreach sent, etc.) for a given show. Should we add a `promo_checklist` object to each event in events.json, or track this only in the dashboard?

6. **Bandsintown sync:** The Bandsintown CSV is regenerated manually. Is there appetite for automating that step on phase transitions?

7. **Dashboard audience:** Is this a solo tool for Paul, or something Nigel and John might also glance at? That affects how much explanation vs. density is appropriate in the UI.

---

## Relevant files

- Project root: `/Users/paulkirschenbauer/Documents/Claude/Projects/Bolo Boys/`
- Site: https://boloboys.band
- Band email: boloboysband@gmail.com
- Paul's email: paul.kirschenbauer@gmail.com
- Nigel: nigelwrightmusic@gmail.com
- John: jcwilber4340@gmail.com
