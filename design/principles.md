# design/principles.md — Bolo Boys visual principles

Visual-language doc for **graphic / print / poster design** in this project. Read this when working on a show poster, a QR-code flyer, EPK graphics, social tiles, or any AI-generated illustration commissioned for Bolo Boys use.

**Scope and lane (important):**
- This doc owns: posters, flyers, social graphics, illustration prompts, color/type/composition rules.
- This doc does NOT own:
  - **Voice and copy on graphics** — that's content-steward + CLAUDE.md's "Voice and tone" section.
  - **Website UI** — that's `index.html` (single-file site).
  - **Cross-project design principles** — none exist yet (would live at `~/.claude/design-principles/` if they did).
- There is no project-wide "graphic designer" subagent yet. If poster work happens, the working session reads this doc, drafts in the established visual language, and surfaces to Paul for approval before any commit (hard rule #6 from CLAUDE.md still applies).

## The visual system (decoded from past posters)

Reference posters: `design/references/` has source examples labeled `band-authored` vs `venue-house`. The band's visual identity in 2026 is anchored most strongly by the **Side Saddle posters** Nigel produces — they're the closest thing Bolo Boys has to a house style. Five repeatable moves:

### 1. Two-color palette on pure black

- **Background:** solid black. Always.
- **Two ink colors:** one accent (headline + key text), one figure (the illustration).
- **White outlines** on the figure separate it from black and add the screen-print feel.
- **No gradients. No realistic shading. No drop shadows.**

Observed palettes in past posters:
- Summer Series: mustard yellow accent + teal/dark-cyan figure
- St. Paddy's: green-only (single color, no second ink)
- Older variants exist with red accents and orange-on-black

Pick the palette to fit the show's season or theme, not the venue's brand. (The Ideal Sports Bar logo, for example, is red+yellow varsity — do NOT match it. Use a contrasting palette and let the logo sit in its own corner.)

### 2. Single iconic illustration as the anchor

- One subject, occupying most of the visual real estate.
- **Flat, posterized, vector-feel** — like a 1970s concert poster or an Old West wanted poster.
- White outlines on key forms.
- Always **illustration, never photography**, for the hero slot. Band photos belong on the website and EPK, not on show posters.
- Subjects used so far: cowgirl on horseback (Side Saddle recurring). New shows generally need new subjects — don't reuse the same image across venues.

### 3. Bold display sans-serif headline

- Heavy condensed display face for the main "Live Music on the Beltline!" / "Bolo Boys" headline.
- Set tight, stacked left.
- In the accent color (not white).
- Secondary text (band lineup ticker, dates) in clean sans, all caps for ticker, mixed case for date labels.

### 4. Stacked date blocks

- For single-show posters: one prominent date.
- For multi-date runs: stacked columns, each with **day-of-week / date / time** in three vertical lines (e.g., "Sun / 5/31 / 11AM").
- Date labels use mixed case ("Sun" not "SUN"); date numerals are the heaviest weight in the block.

### 5. Fixed furniture (always in the same slots)

- **Venue logo:** top-right corner.
- **QR code → boloboys.band:** bottom-right corner. Use `assets/qr/` for the current QR PNG; never regenerate.
- **Lineup ticker:** all-caps band names hyphen-separated across the very bottom edge. Order = headliner first.
- **No additional URLs in body** — the QR is the URL; redundant text URLs add noise.

## Composition checklist

A poster should pass all of these before it ships:

- [ ] Pure black background
- [ ] Two-color palette (or single-color variant), screen-print feel, no gradients
- [ ] Single iconic illustrated subject, flat with white outlines
- [ ] Headline in display sans-serif, accent color, stacked left
- [ ] Date block(s) stacked with day/date/time
- [ ] Venue logo top-right
- [ ] QR code bottom-right
- [ ] Lineup ticker across bottom
- [ ] No emoji anywhere (matches CLAUDE.md hard rule on emoji)
- [ ] Copy passes content-steward voice rules (warm friend, not marketer)

## When to use AI generation

**Use AI generation for:**
- The single iconic illustration (the "hero subject" — the cowgirl-equivalent).
- Background textures (rare — most posters are flat black).
- Stylized object still-lifes when the subject is hard to find royalty-free (a specific bolo tie draped over a pool cue, etc.).

**Don't use AI generation for:**
- Band member portraits (uncanny-valley risk; we have real band photos for that).
- Type / typography (AI mangles letterforms).
- Composition / layout (do that in Photoshop or Figma, not in a prompt).
- Logos (use the provided venue logos in `assets/misc/` or wherever they live).

**Tooling, in preference order:**
1. **Photoshop Generative Fill / Generate Image** (powered by Firefly) — Paul's default. Outputs are commercially usable, integrates with the composite step.
2. **Firefly web** — same engine, browser-based fallback.
3. **Midjourney / DALL·E / etc.** — only if Firefly can't get the style. Check commercial-use terms.

### Prompt scaffolding for the hero illustration

The cowgirl-on-horseback is the gold standard. Any new hero illustration should be promptable in the same language. Template:

> Vintage screen-print poster illustration of **[SUBJECT, doing something specific]**. Flat color, posterized, **[FIGURE COLOR]** on solid black background, white outline accents on key forms. Bold graphic style, like a 1970s concert poster or Old West wanted poster. No gradients, no realistic shading, no photorealism. Single isolated subject, transparent background. Vector-graphic feel.

Specifics that matter in the prompt:
- **Name the action**, not just the subject. "A cowboy *breaking a rack of pool balls*" beats "a cowboy with a pool cue."
- **Name the period reference** — "1970s concert poster," "vintage rodeo flyer," "Saul Bass" all bias toward the right style; "modern" or "minimalist" do not.
- **Specify the figure color** in the prompt so it lands close to the target palette out of the box.
- **Always say "no gradients, no realistic shading"** — Firefly's default is photorealism.
- **Always say "single isolated subject, transparent background"** — saves the masking step.

Example prompts banked from the Ideal Sports Bar brainstorm (not yet executed):

> Vintage screen-print poster illustration of a cowboy breaking a rack of pool balls, leaning over a pool table mid-shot, cowboy hat low over his eyes. Flat color, posterized, teal figure on solid black background, white outline accents. Bold graphic style, like a 1970s concert poster or Old West wanted poster. No gradients, no realistic shading. Single isolated subject, transparent background.

> Vintage screen-print poster still-life of a bolo tie draped over a pool cue resting across an 8-ball. Flat color, posterized, mustard yellow on solid black background, white outline accents on key forms. Bold graphic style, like a 1970s concert poster. No gradients, no realistic shading. Single isolated subject, transparent background.

## Asset locations

- `assets/posters/` — historical poster output (PNG/JPG), sorted by venue+date. `assets/posters/sources/` for working files.
- `assets/posters/archive/` — superseded or alternate versions.
- `assets/pictures/` — band photos and live shots (for website / EPK use, NOT poster hero slot).
- `assets/qr/` — current QR code PNGs pointing to boloboys.band.
- `assets/misc/` — third-party venue logos and one-off assets. Current: `ideal-sports-bar-logo.png`.
- `design/references/` — labeled past posters for visual reference (`band-authored` vs `venue-house`).

## Tension to watch: venue logos vs. our system

Some venues have visual identities that fight the Side Saddle system:
- **Side Saddle Wine Bar** — already aligned (their logo is at home in our palette).
- **Ideal Sports Bar** — retro varsity, chunky red-outlined yellow block caps + yellow-outlined-red script. Will clash if we try to match palettes. **Resolution:** let the logo sit in its top-right corner in its own colors; pick our palette to contrast (avoid red+yellow accents on the same poster).
- **Other future venues** — same principle. Our system stays consistent; their logo lives in its assigned corner without us reformatting it.

## When to update this doc

- After a new poster ships and introduces a move worth codifying (new palette combo, new layout, etc.).
- After a brand decision that changes one of the rules (e.g., "we're moving off the all-black background for summer 2027").
- When AI tooling shifts meaningfully (new model, new feature in Photoshop, new prompt structure that works better).

Add a one-line note to `CHANGELOG.md` whenever this doc changes substantively, same as any other repo edit.

## Open threads (session 2026-05-19)

This doc was created in a session where Paul brainstormed an Ideal Sports Bar poster but **tabled the decision on whether to make one at all.** The state when we paused:

- **Ideal Sports Bar shows:** Fri 6/26/2026 and Sat 7/11/2026, both 8 PM, free, Lakewood Heights. Either gets a single dual-date poster or two separate posters — leaning dual-date.
- **Three design directions surfaced**, ranked closest-to-furthest from the current Side Saddle system:
  - **A.** Cowgirl-system reskin with a new iconic illustrated subject for Ideal — e.g., a cowboy breaking pool balls. *(Recommended.)*
  - **B.** Iconic still-life instead of a figure — e.g., a bolo tie draped over a pool cue. *(Safer prompt; avoids AI-people pitfalls.)*
  - **C.** Photoreal band-in-the-bar. *(Breaks the system; AI photoreal band shots usually look uncanny. Not recommended.)*
- **Logo aesthetic noted:** Ideal Sports Bar logo is retro varsity red+yellow. Don't match palettes; contrast.
- **Decision pending:** does this show actually need a poster? Or does it ship with just an IG announcement and the standing QR-code flyer (`assets/misc/` adjacent + `assets/posters/` archive has the recurring flyer format)?

**To pick this up next session:**
1. Confirm whether Ideal shows need a poster.
2. If yes, pick Direction A or B.
3. Draft the Firefly prompt using the scaffolding above, generate the hero illustration.
4. Composite in Photoshop: hero illustration centered, Ideal logo top-right, QR bottom-right, dual-date stack lower-left (Fri 6/26 8PM / Sat 7/11 8PM), lineup ticker across bottom (will be "BOLO BOYS" alone unless co-bills emerge).
5. Surface to Paul for approval before any commit or BIT upload reference.
