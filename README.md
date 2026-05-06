# Bolo Boys Website

Mobile-first single-page website for [Bolo Boys](https://www.instagram.com/boloboysband/) — an Atlanta- and Macon-based three-piece live band. Hosted on GitHub Pages.

## What this repo is

A static site (`index.html`) plus structured JSON data files. No build step. No framework. Push to `main`, GitHub Pages deploys.

```
.
├── index.html              # The site (HTML + CSS + vanilla JS, single file)
├── README.md               # You are here
├── CLAUDE.md               # Context for AI assistants working on this repo
├── data/
│   ├── band.json           # Band facts: members, contacts, sound, scene
│   ├── events.json         # Upcoming shows (rendered by index.html)
│   ├── venues.json         # Venue library (referenced by events.json)
│   ├── past-shows.json     # Past show archive
│   └── distribution-list.json  # Show announcement distribution list
├── assets/
│   ├── hero.jpg            # Hero background
│   ├── band-photo.jpg      # About-section band photo
│   ├── live-1..4.jpg       # Carousel photos
│   └── pictures/           # Show posters and other show-specific art
└── .gitignore              # Keeps CRM and macOS junk out of the repo
```

## How to add or update a show

1. Edit `data/events.json` — add a new entry or modify an existing one. Schema example is at the top of the file under `_schema_example`.
2. If the venue isn't already in `data/venues.json`, add it there too.
3. Preview locally (see below).
4. Commit and push to `main`. GitHub Pages will redeploy in ~1 minute.

The site fetches `data/events.json` at runtime, so edits to event data take effect as soon as the deploy lands — no other files need to change.

## How to preview locally

The site fetches JSON files at runtime, which means **opening `index.html` directly with `file://` will not work** — the browser blocks `fetch` from local files for security reasons.

Run a tiny local server from the project root:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000` in your browser. Stop the server with `Ctrl+C`.

## How the site deploys

GitHub Pages serves from the `main` branch. Every push to `main` triggers a redeploy (typically under a minute). There is no build step.

To check deploy status: GitHub repo → **Settings → Pages**.

## Asset conventions

- **`assets/`** — site-wide images that ship with every page load (hero, band photo, carousel).
- **`assets/pictures/`** — show-specific art (posters, flyers). Referenced from individual events in `events.json` via the optional `poster_url` field.
- **In-progress design files** (rough drafts, working PSDs, design experiments) should live outside the repo or in a folder added to `.gitignore`. Don't commit them — keep the repo lean.

## What's *not* in this repo

- The CRM spreadsheet (`Bolo Boys CRM.xlsx`) — gitignored, lives locally only.
- Personal calendar / email integration — handled outside the site via the band's shared Gmail (`boloboysband@gmail.com`) and shared Google Calendar.

## Working with AI assistants

Context for AI tools (persona, tone, workflow rules) lives in `CLAUDE.md`. Structured band facts live in `data/band.json`. Both are committed to the repo so anyone — human or AI — can pick up the project from a fresh clone.

## Contact

boloboysband@gmail.com
