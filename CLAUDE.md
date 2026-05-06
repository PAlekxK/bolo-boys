# CLAUDE.md — Bolo Boys Website

Context for any AI assistant working in this repo. Read this first.

## What this project is

Mobile-first single-page website for **Bolo Boys**, an Atlanta- and Macon-based three-piece live band. Static HTML + JSON data, hosted on GitHub Pages.

- **Site code:** `index.html` (single file — HTML, CSS, vanilla JS).
- **Band facts (source of truth):** `data/band.json`. Read this before writing any copy that mentions the band.
- **Event data:** `data/events.json` (rendered at runtime), `data/venues.json` (venue library).
- **Human onboarding:** `README.md`.

## Who Bolo Boys are (the short version)

Three guys — Paul (bass, vocals), Nigel (electric guitar, vocals), John (acoustic guitar, harmonies) — who are family-close (childhood friends + Paul's mom's cousin). Country, folk, reggae, classic rock, and throwback pop, all "Bolo-fied" so they sound like they're from the same album. Touchstones: Tom Petty, Bob Marley, Doc Watson, Cat Stevens. Four originals woven into sets so listeners don't notice. The mission: people dancing and singing along.

For full member bios, sound philosophy, scene affiliations, and originals roster, see `data/band.json`.

## Voice and tone

Write like a warm friend inviting you over, not a marketer selling tickets.

**Always:**
- Warm, playful, authentic, community-oriented
- Low-pressure ("come hang," "bring the crew") over urgent ("don't miss out!")
- Music-focused and venue-focused — celebrate the room and the night
- Short and scan-friendly — these are mobile reads

**Never:**
- Hype, urgency, or FOMO ("limited seating," "this is the one you can't miss")
- Corporate event copy ("we are pleased to announce")
- Influencer voice (no exclamation-heavy enthusiasm, no "let's gooo")
- Tortured singer-songwriter posturing ("emotional journey," "raw vulnerability")
- Emoji in body copy or in calendar icons

## Hard rules

1. **Never write "the Bolo Boys."** Always "Bolo Boys." This is a brand rule.
2. **The band is "Bolo Boys" — singular as a band entity, plural as members.** "Bolo Boys are playing" / "Bolo Boys is the trio of Paul, Nigel, and John" both work; pick whichever reads naturally.
3. **Every calendar invite goes to all three members** via the shared band calendar / `boloboysband@gmail.com`. Never invite a single member.
4. **Atlanta and Macon** — both cities. Don't reduce to Atlanta-only in bios.
5. **Calendar icons must be stroke-based outline icons** (lucide / feather / heroicons style). No emoji. No static date numbers inside the icon.
6. **Never commit to GitHub without Paul's explicit confirmation.** Draft → review → confirm → commit.
7. **No 30-minute-or-shorter gigs.** If you're drafting booker-facing copy, lead with the band's preference for full sets.

## What Bolo Boys are NOT

Use this list to calibrate copy that might drift in the wrong direction:

- Not THE Bolo Boys
- Not tortured singer-songwriters
- Not self-obsessed online influencers
- Not a 30-minute opener act
- Not a wedding band
- Not a tribute act — covers get Bolo-fied, not reproduced

## Event workflow

When Paul gives you raw event details:

1. **Capture** raw input — accept whatever Paul provides, however informal.
2. **Ask** for any missing fields needed to complete the entry (date, time, venue, supporting acts, etc.).
3. **Check** `data/venues.json` for existing venue data before treating it as new.
4. **Enhance** — fill obvious gaps (full address, Google Maps URL, neighborhood).
5. **Theme** — give the show a fun internal theme name (e.g., "The Wild Heaven Kickoff," "Last Call for Summer").
6. **Draft invitation** — warm, playful, low-pressure paragraph for the expanded card view.
7. **Teaser** — only if extremely short and clearly punchy. When in doubt, skip it.
8. **Build the Google Calendar URL** — pre-filled with title, date, location, details. Format matches existing entries in `events.json`.
9. **Review with Paul** — present the full draft for approval before any file changes.
10. **Update** `data/events.json` only after explicit approval.
11. **Update** `data/venues.json` if the venue is new.
12. **Commit** only after Paul confirms.

## Event card spec (for reference when editing index.html)

The collapsed card view must stay uncluttered. Date is the most prominent element. The expanded card holds the theme, invitation text, additional details, and calendar/maps actions. Full details and field-by-field rules are inside `index.html` and the existing `events.json` entries — match what's there.

## When in doubt

- **About a band fact:** check `data/band.json`.
- **About an event format:** look at recent entries in `data/events.json`.
- **About tone:** re-read the "Voice and tone" section above and check the existing `invitation_text` fields in `events.json` for examples that have already been approved.
- **About making a change:** ask Paul before editing — especially before committing.

## AI agent posture

You are a technical partner and creative collaborator. Default to consultant mode: ask clarifying questions before doing independent work, especially for anything that touches copy, events, or the live site. Present options (high-effort vs. low-effort) when the path forward isn't obvious. Match Paul's energy — direct, structured, unpretentious.
