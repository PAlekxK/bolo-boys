# design/logo-brief.md — Bolo Boys logo & mark

Working brief for designing the real Bolo Boys brand mark. Feeds AI image tools
(Ideogram / Recraft) and hand-authored SVG. Sibling to `design/principles.md`
(which owns posters/flyers) — the logo must **harmonize with** that house style,
not invent a competing one.

Status: DRAFT 2026-06-28. Paul-driven; band (Nigel) brought in once a strong draft exists.
Not committed — working artifact.

---

## The job

There is no real logo today — `assets/favicon.svg` is an explicit placeholder
("cream-on-green B"). This is a first design, not an evolution. Clean slate.

Design a **two-part identity**:

1. **Emblem (the clasp).** A single bold mark that works as a **cast-metal bolo-tie
   slide**, AND doubles as favicon, sticker, and social avatar. Metal-first.
2. **Wordmark.** "Bolo Boys" lettering lockup for the site header, posters, shirts,
   QR cards.

The emblem can stand alone (tiny sizes, the clasp, the avatar). The wordmark + emblem
lock up together for the hero contexts.

## Who Bolo Boys are (anchor — source of truth: `data/band.json`)

Three/four guys, **family-close** (childhood friends + Paul's mom's cousin). Country,
folk, reggae, classic rock, throwback pop — all "Bolo-fied" so it sounds like one album.
Touchstones: **Tom Petty, Bob Marley, Doc Watson, Cat Stevens.** Atlanta **and** Macon.
The mission: **people dancing and singing along.** Warm, playful, unpretentious,
community-first. The bolo tie is the identity anchor.

## What the mark must NOT be (calibration)

- Not corporate / startup-slick / "tech."
- Not tortured-singer-songwriter moody.
- Not influencer-hype.
- Not a wedding band's tasteful script.
- Not a literal tribute-act / pastiche.
- Never "the Bolo Boys" if any text article appears — it's **Bolo Boys**.

## Aesthetic direction

**Western / bolo-tie, in the poster house language.** Old West "wanted poster" meets
1970s screen-print concert poster: flat, posterized, bold, **white outlines on key
forms, no gradients, no realistic shading.** Vintage and crafted, not clean-modern.

## The clasp constraint (HARD — emblem is designed metal-first)

Paul intends to actually cast these. The emblem must survive being a ~1.5–2" metal slide:

- **One bold silhouette.** Readable at arm's length and at 16px.
- **No thin lines or fragile counters** — they fill in / break when cast.
- **Reads in a single color** (it's metal: silver or antique brass). Color is a
  digital/print concern; the physical clasp is monochrome metal +/- one stone.
- **Near-symmetry helps** — casting, and the "slide" read.
- Reference logic: a **concho**, a belt-buckle, an actual bolo slide. Compact, contained,
  bordered.

## Surfaces & the formats each needs

| Surface | Needs |
|---|---|
| **Cast-metal clasp** | SVG master → single-color silhouette, ~1.5–2", castable |
| **Favicon** | Emblem only, legible at 16px |
| **Sticker / social avatar** | Emblem, one- and two-color |
| **Website header** | Horizontal wordmark+emblem lockup; light- and dark-bg |
| **Posters** | Lives inside the black-screenprint system (`principles.md`) |
| **Merch (shirts)** | One-color + bold; works on fabric, at distance |
| **QR card (at-show)** | Instant read, small |

Export the family from one vector master: full-color, one-color, horizontal, stacked,
favicon, knockout (white-on-dark).

## Palette tracks to explore (all three, per Paul)

1. **Poster house-style** — mustard yellow + teal/cyan on **black**. Maximizes coherence
   with existing equity (posters, QR cards).
2. **Earthy** — forest green (`#2D4B1E`) + cream (`#F8F4ED`), from the current favicon.
3. **Western metals (most literal)** — **silver + turquoise + leather-brown.** Mirrors
   real bolo hardware (silver slide, turquoise stone). Strongest fit for the physical
   clasp; the metals read as themselves in cast form.

Note: because the clasp is monochrome metal, palette mostly governs the **digital/print**
expression. Design the emblem silhouette palette-agnostic, then color it three ways to compare.

## Type direction (wordmark — test two)

- **A. Condensed display sans** — matches the poster headlines; modern-vintage, bold,
  stacked-left energy.
- **B. Western slab / woodtype** — more rodeo/wanted-poster flavor, slab serifs, slight
  distress.

The bolo hook in the letters: braided **cord underlining** the word with silver tips, or
an **O reworked as the slide** with cords dangling.

## Concept directions to prototype (the starting shots)

Five named directions, ranged from wordmark-led (I can hand-author as SVG) to
emblem-led (generate raster in Ideogram/Recraft, then vectorize):

- **A. "The Slide"** — an oval concho medallion: monogram **BB** or a small Western icon
  centered, bordered rope edge. *This IS the clasp.* (emblem-led)
- **B. "Bolo-O"** — wordmark where an **O becomes the bolo slide** with two cords + silver
  tips dangling below the word. (wordmark-led — SVG-able)
- **C. "Wanted-poster oval"** — "BOLO BOYS" arched around an oval badge ringing a central
  Western icon (guitar headstock + bolo, longhorn, cactus). (emblem-led)
- **D. "Cord underline"** — clean wordmark with a braided **bolo cord + silver tips**
  swooping beneath it. (wordmark-led — SVG-able)
- **E. "Monogram concho"** — interlocked **BB** designed as a silver concho, clasp-first;
  the most jewelry-like. (emblem-led)

## Prompt scaffolding (Ideogram / Recraft — emblem directions)

Adapted from `principles.md`. Recraft can output SVG; Ideogram is strongest on legible text.

> **Vintage Western emblem / belt-buckle logo of [SUBJECT].** Flat, posterized,
> single-subject, **bold silhouette suitable for casting in silver metal**, heavy outlines,
> no thin lines, no gradients, no realistic shading. Old West wanted-poster / concho /
> 1970s screen-print style. Centered, symmetrical, contained in an oval/round border.
> [COLOR treatment]. Transparent background.

Rules that matter: name the icon and the action; say "**castable / bold silhouette /
no thin lines**"; say "no gradients, no shading"; specify symmetry + the oval border;
keep it single-subject.

## Workflow

1. **This brief** → feed directions A–E to the right tool.
2. **Wordmark-led (B, D):** I hand-author first-pass **SVG** to react to — clean, editable,
   infinitely scalable, no tracing.
3. **Emblem-led (A, C, E):** generate raster explorations in Ideogram/Recraft → pick →
   **vectorize** (Illustrator Image Trace / vectorizer.ai / Recraft) → refine in
   Figma (free) or Affinity Designer (~$70 one-time).
4. **Color** the chosen emblem in all three palette tracks; compare.
5. **Export the family** + test the clasp silhouette at metal scale.
6. **Version** (`logo-v1`, `v2`…); bring a strong draft to the band.

## Open questions

- Which 1–2 concept directions to prototype first.
- Any Western icon you want centered in the emblem (guitar headstock, longhorn, the actual
  bolo tie, BB monogram)?
- Casting vendor / metal (silver vs antique brass) — informs the clasp spec later, not the design now.

## Tooling backlog — DesignSync (claude.ai/design)

Assessed 2026-06-28. Claude Code's DesignSync + `/design-sync` syncs on-disk static
design files (SVG/PNG, HTML/CSS) up to a claude.ai/design "Design System" project,
where each renders as a preview card grouped by labels (Brand, Type, Colors, Components).
It does **not** generate or iterate marks — storage/versioning/preview only.

- **Status: SET UP 2026-06-28** (Paul overrode the defer recommendation — "do it now").
  Project "Bolo Boys Brand" (claude.ai/design, id `b1730b0b-9380-47da-b0f2-63c574a6e454`),
  synced at **Paul's locked preset (below)**. Brand group = mark (two-tone / mono / on-dark) +
  favicon + stacked lockup; Type group = the B (scoop); Colors group = working palette +
  candidates. Raw SVGs under `brand/assets/`. Re-export + re-sync on any preset change.
  Local source: `design/exports/` (regenerated by the scratchpad export + wrap scripts).

## Locked spec (2026-06-28)

Paul-ratified preset for the mark (drives the guitar AND the derived B):

```json
{"spine":30,"neck":92,"hub":88,"hole":42,"arm":36,"upper":86,"lower":108,"height":236,"holepos":-19,
 "fret":false,"spineColor":"#7a5400","bowlColor":"#c89b4a","wmHole":"half","wfont":"Special Elite"}
```

- **Two-tone:** walnut/amber spine+neck `#7a5400`, brass bowls `#c89b4a`. Frets OFF.
- **B half-hole = LEFT-EDGE SCOOP, not a semicircle.** A full circle centered on the B's spine
  (left) edge at the waist, so the cut is a clean concave arc with NO straight chord line through
  the letter — "a scoop out of the B." Two mirrored scoops re-form the full sound hole. (Paul
  correction 2026-06-28; the earlier flat-chord semicircle is wrong.)
- **Wordmark B is TWO-TONE** — walnut spine (`#7a5400`, = the guitar neck/spine) + brass bowls
  (`#c89b4a`). Color carries the link to the mark. Stem drawn on top so the walnut reads as a
  clean vertical bar. (Paul direction 2026-06-28.)
- **Companion face: Bevan** (recommended — tightest weight match to the heavy B, verified in-browser
  with real fonts). Alfa Slab One = punchier alternative. Rye clashes (ornate vs geometric B);
  Special Elite too thin. The v11 tool exposes a **B-weight knob** + **companion-text color** to
  balance the wordmark without touching the mark.
- **Open:** lockup kerning/baseline still rough (heuristic, not designed). The custom B's *character*
  is intentionally distinct from the slab companions (it's the "special" glyph); only the weight is
  matched. Next: real lockup kerning + a clean production-union SVG of the mark.
- **Tool:** `~/Desktop/Claude/bolo-boys-logo-v12.html` (interactive). Controls grouped by **part**
  (Spine & Neck / Bowls / Sound hole / Wordmark), each with its own color(s). New colors: **fret
  color** + **sound-hole fill** — set the hole turquoise for the **bolo-tie stone** (looks like a
  silver/gold slide + turquoise on the cast clasp; verified in-browser). Wordmark B spine/bowls
  inherit the mark's colors. Exports via the scratchpad `export-logo-svgs.js` (`all <face>` |
  `compare`) + `wrap-cards.js`.
- **Best use here** isn't the logo alone — it's consolidating the whole Bolo Boys identity
  (logo variants + the 3 competing palettes + poster furniture from `principles.md`) into
  one glanceable surface, which would force the unresolved **palette decision** visually.
- **Prerequisites:** lock the preset → run the production union path → export ~7 clean SVG
  variants (primary lockup, on-dark, icon-only, mono/cast clasp, wordmark-only, stacked vs
  horizontal, favicon) → stand up a claude.ai/design project.
- **Caveat:** Nigel (band's visual hand) may not be in claude.ai, so it's not automatically a
  shared band canvas. If we'd rather keep everything in the repo `assets/`, skipping it costs
  nothing.
