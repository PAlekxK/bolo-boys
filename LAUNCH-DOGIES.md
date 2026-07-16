# Dogies — launch runbook (Fri 2026-07-17)

Delete this file once the launch is done and the dust has settled.

**The shape:** song at 9 AM, video premiere at 7 PM. Two beats, not one — the
premiere is worth attending, and nobody attends anything at 9 AM on a workday.

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
- [ ] **Post the art reveal** → routes to www.boloboys.band.
- [ ] Merge `release/dogies` → `main` so the site's release block is live before
      the post points at it. **The post has nowhere to send people until this ships.**

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
   ```

   Cloudflare deploys in ~1 min. The block flips to "Out Now" with the Spotify
   player, the streaming row, and the video embedded underneath.

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
