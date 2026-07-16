# Bolo Boys Website

Mobile-first single-page website for [Bolo Boys](https://www.instagram.com/boloboysband/) — an Atlanta- and Macon-based four-piece live band. Live at [boloboys.band](https://boloboys.band).

## What this repo is

A static site (`index.html`) plus structured JSON data files. No build step. No framework. Deploy with `bash tools/deploy.sh` (pushing `main` does *not* publish — see [How the site deploys](#how-the-site-deploys)).

```
.
├── index.html              # The site (HTML + CSS + vanilla JS, single file)
├── README.md               # You are here
├── data/
│   ├── band.json           # Band facts: members, contacts, sound, scene
│   ├── events.json         # Upcoming shows (rendered by index.html)
│   ├── venues.json         # Venue library (referenced by events.json)
│   └── past-shows.json     # Past show archive
├── assets/
│   ├── hero.jpg            # Hero background
│   ├── band-photo.jpg      # About-section band photo
│   ├── live-1..7.jpg       # Carousel photos
│   ├── posters/            # Show flyers / posters (one per event, named <event-id>.jpeg)
│   └── pictures/           # Other show-specific photography
└── .gitignore              # Keeps private files and macOS junk out of the repo
```

## How to add or update a show

1. Edit `data/events.json` — add a new entry or modify an existing one. Schema example is at the top of the file under `_schema_example`.
2. If the venue isn't already in `data/venues.json`, add it there too.
3. Preview locally (see below).
4. Commit and push to `main`, then run `bash tools/deploy.sh` to publish. The push alone does not update the live site.

The site fetches `data/events.json` at runtime, so edits to event data take effect as soon as the deploy lands — no other files need to change.

## How to preview locally

The site fetches JSON files at runtime, which means **opening `index.html` directly with `file://` will not work** — the browser blocks `fetch` from local files for security reasons.

Run a tiny local server from the project root:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000` in your browser. Stop the server with `Ctrl+C`.

## How the site deploys

**Pushing `main` does not deploy anything.** Deploying is an explicit command:

```bash
bash tools/deploy.sh
```

It uploads the site and then verifies against production, so a deploy that didn't land fails loudly instead of silently.

The site is a Cloudflare **Worker** named `bolo-boys-band` that serves this repo as static assets (config in `wrangler.jsonc`; `.assetsignore` controls what's excluded). There is **no** Pages project and **no** GitHub integration — the repo was migrated off Pages on 2026-06-30 and the auto-deploy did not survive the move.

> **Why this warning exists:** the old "push and it deploys" instruction stayed in this README after the migration. The live site sat frozen at the 6/30 commit for 17 days while 11 commits piled up on `main`, and it was only caught on 7/16 because a record release depended on it. Commit and push as usual for version control — but the site is live only after `deploy.sh` says `✅ Deployed and verified`.

To check deploy status: Cloudflare dashboard → **Workers & Pages** → `bolo-boys-band` → **Deployments**.

## Asset conventions

- **`assets/`** — site-wide images that ship with every page load (hero, band photo, carousel).
- **`assets/posters/`** — show flyers and posters. One file per event, named after the event's `id` (e.g. `gateway-park-grant-park-2026-05-17.jpeg`). Referenced from `events.json` via the optional `poster_url` field. Build the archive over time so we always have a repository to draw from.
- **`assets/pictures/`** — other show-specific photography (not posters).
- **In-progress design files** (rough drafts, working PSDs, design experiments) should live outside the repo or in a folder added to `.gitignore`. Don't commit them — keep the repo lean.

## What's *not* in this repo

Private working files live in a sibling folder (`../Bolo Boys - Private/`), gitignored and never deployed:

- `Bolo Boys CRM.xlsx` — booking and contact spreadsheet.
- `data/distribution-list.json` — show announcement distribution list.
- `docs/promotion-research.md` — internal booking and promotion strategy.
- `CLAUDE.md` — AI assistant context (brand rules, tone, workflow).

Personal calendar / email integration is handled outside the site via the band's shared Gmail (`boloboysband@gmail.com`) and shared Google Calendar.

## Working with AI assistants

Structured band facts live in `data/band.json` — committed to the repo so anyone (human or AI) can pick up the project. Additional context (persona, tone, workflow rules) lives in `CLAUDE.md` in the sibling private folder; AI tools working in this repo should be pointed at both.

## Contact

boloboysband@gmail.com
