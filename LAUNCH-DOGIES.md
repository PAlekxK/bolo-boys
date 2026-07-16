# Dogies — launch runbook (Fri 2026-07-17)

Delete this file once the launch is done and the dust has settled.

**The shape:** song at 9 AM, video premiere at 7 PM. Two beats, not one — the
premiere is worth attending, and nobody attends anything at 9 AM on a workday.

---

## ✅ RESOLVED 2026-07-16 ~6:15 PM ET — the site is deployed

**Root cause was not Dogies.** On 2026-06-30 the site was migrated from Cloudflare
**Pages** to a **Worker** (`bolo-boys-band`). Cloudflare's bot opened
`cloudflare/workers-autoconfig` with the required `wrangler.jsonc` — **it was never
merged**, and no git integration was ever wired up. So `main` had no Worker config
and *nothing had deployed since 6/30*. The live site was frozen at commit `0781627`
(6/30 11:54 AM) for 17 days, with **11 unpublished commits** on `main`. The Pages
dashboard hunt below failed because there is no Pages project to find.

**Fix:** `wrangler.jsonc` + `.assetsignore` committed to `main`, and deploying is now
`bash tools/deploy.sh` — which deploys *and verifies against production*. Verified live:
cover art 200, `band.json` carries `releases[]`, `#release` renders (browser-checked at
390px), `og:image` is the Dogies cover, premiere ID in JSON-LD. The art-reveal post has
somewhere to land.

**Still Paul's to do:** reconnect Workers Builds to the repo in the Cloudflare dashboard
if you want pushes to auto-deploy again. Until then, `deploy.sh` is the only thing that
publishes — including tomorrow's 9 AM go-live.

<details>
<summary>Original blocker writeup (2026-07-16 ~1:10 PM) — kept for the record</summary>

## 🔴 BLOCKER as of 2026-07-16 ~1:10 PM ET — the site is NOT deployed

`main` is correct and pushed (merge `3c11081`, confirmed present on GitHub via
the API). **Cloudflare has not deployed it.** Verified against production with a
real browser, not inference:

| probe | result |
|---|---|
| `/assets/releases/dogies-cover.jpg` | **404** |
| `/LAUNCH-DOGIES.md` | **404** |
| `/data/band.json` | 200, but **no `releases` key** |
| `/assets/band-photo.jpg` (old) | 200 |
| `#release` section in DOM | **absent** |
| `og:image` | still `band-photo.jpg` |

Not a cache artifact: a never-before-requested, cache-busted path returned 404,
which the edge cannot manufacture. The origin genuinely lacks the files.

**This gates the Thursday art-reveal post** — that post routes to
boloboys.band, and the site currently has no Dogies on it.

**Check:** Cloudflare dashboard → Workers & Pages → the project → Deployments.
Look for a build against `3c11081`.
- *Queued/building* → just slow; re-verify.
- *Failed* → read the log. This is a static site with no build step, so it'll be
  something small.
- *No build triggered* → the GitHub integration is likely disconnected. Retry the
  deployment or reconnect the repo. **Corroborating hint:** `bolo-boys.pages.dev`
  and `release-dogies.bolo-boys.pages.dev` both fail DNS, so the Pages project
  name in `README.md` may be stale/wrong too — worth confirming while you're in
  there.

Re-verify after it deploys — don't assume:
```bash
# expect: 200, and band.json carrying releases[]
curl -sI https://www.boloboys.band/assets/releases/dogies-cover.jpg | head -1
curl -s  https://www.boloboys.band/data/band.json | grep -c '"releases"'
```

</details>

---

## Before you go to bed Thursday

- [ ] **Move the YouTube premiere to 7:00 PM ET.** YouTube Studio → the video →
      Premiere settings. *The site and its structured data already say 7 PM. If
      the premiere stays at 9 AM, both are lying — tell Claude to change them.*
- [ ] **Retitle the video.** It's currently just "Dogies," which nobody searches.
      → `Bolo Boys — Dogies (Whoopie Ti Yi Yo / Git Along, Little Dogies) — Official Music Video`
- [ ] **Paste the new description** (credits are the content, not a footer).
- [ ] **Warn the collaborators** — @dirty_shame_atl, @acousticstation,
      @nigelwrightmusic. A collab invite only lands on their grid **after they
      accept**, so an unaccepted invite is just a normal post. Tell them it's
      coming and to hit accept Friday evening.
      *(Ante Up has no Instagram — named in text, not tagged.)*
- [ ] **Check the IG link in bio points to boloboys.band.** Captions aren't
      clickable on Instagram — the bio link is the only real path. No change
      needed if it's already the site: the release block sits directly under the
      hero, so the bio link lands people on the record without a special link.
      (The `www.` in the caption still matters — it auto-links on the FB
      cross-post, where a bare domain renders as dead text.)
- [x] ~~Merge `release/dogies` → `main`~~ — merged *and now actually deployed*
      (7/16 ~6:15 PM). The release block is live; the post has somewhere to land.
- [ ] **Post the art reveal** → routes to www.boloboys.band.

---

## Friday 9:00 AM — the song

1. **Find the track on Spotify**, hit Share → Copy Song Link.

2. **Flip the site** (one command — the ID is the only thing you couldn't know
   until now; a pasted full URL works fine):

   ```bash
   cd ~/Developer/bolo-boys
   python3 tools/release-go-live.py --spotify-track-id '<paste the link>'
   bash tools/run-propagators.sh
   git add -A && git commit -m 'Dogies is out' && git push
   bash tools/deploy.sh          # ← the push does NOT deploy. This does.
   ```

   Wait for `✅ Deployed and verified` — it checks production for you. The block
   flips to "Out Now" with the Spotify player, the streaming row, and the video
   embedded underneath.

   Add `--apple-music '<url>'` etc. as those links appear. Safe to re-run.

3. **Claim Spotify for Artists — this is the one with lasting value.**
   → https://artists.spotify.com → request access for Bolo Boys.
   **Set the genre immediately.** Google currently confuses Bolo Boys with a
   German hip-hop group (Ideal's listing labeled the 6/26 show "German
   hip-hop/rap"). A distinct Spotify artist ID with a self-set genre is the
   highest-leverage fix available, and this release is the first time it's
   possible. It may resolve on its own once the entity exists.

4. **Once the artist page exists**, add its URL to `sameAs` in `data/band.json`
   → `social` and in the MusicGroup JSON-LD. That's the link that tells Google
   *this* Bolo Boys is *that* Spotify artist. Don't skip it — it's the actual
   disambiguation.

5. **Watch for a Content ID claim on the premiere.** If DistroKid's "YouTube
   Money" is on, DistroKid fingerprints your master and YouTube may auto-claim
   your own video. It won't block the premiere or take anything down — worst
   case is a claim banner and misrouted pennies. **You can't pre-empt it**:
   allowlisting only works per-video *after* a claim lands.
   → https://distrokid.com/youtubeAllowlist

6. **Post the 9 AM "it's out" post.** Solo, art, links home, teases 7 PM.

---

## Friday 7:00 PM — the video

- [ ] **Post the collab.** Send the invites a few minutes early so the
      co-authors can accept; the post is worth far less on one grid than four.
- [ ] Be in the live chat. It's a premiere — that's the whole point of moving it.

---

## Saturday-ish

- [ ] Fill in remaining streaming links as stores go live (re-run
      `release-go-live.py` with the extra flags).
- [ ] Consider reverting `og:image` to the band photo once the release stops
      being the headline — or leave it; it's the current single either way.
- [ ] Reconcile the private repo's OPEN-THREADS: it still says the video is
      **⏸️ ON HOLD (7/13)** and the unlisted-vs-public decision is open. Reality
      has moved past that.
- [ ] `data/songs.json` → `whoopie-ti-yi-yo` still has a *reference* YouTube
      link (`aseZBz7YUgU`). Swap in `sBt22_PZ6E4` — the band's own.

---

## Notes on decisions already made

- **Dogies lives in `band.json` → `releases[]`, not `originals[]`.** It's a
  Bolo-fied traditional, and `originals[]` renders under a heading that says
  "Original Music." The composition is public domain; the arrangement and master
  are yours. The JSON-LD says exactly that (`recordingOf` → MusicComposition /
  "Traditional"), which is both honest and a strong entity signal.
- **DistroKid's songwriter field is correct as filed.** DistroKid instructs you
  to select "I wrote this song" for public-domain works, because they can't
  license a PD cover. Listing yourselves as songwriters of your own arrangement
  is permitted. **The one place to stay careful is PRO registration** — if you
  register with ASCAP/BMI later, register the *arrangement*, not "Dogies" as an
  original composition.
- **No countdown timer on the site**, deliberately. The charter bans
  "don't-miss-this" urgency. HyperFollow shows no date at all, so the site's job
  is just to plainly say when.
