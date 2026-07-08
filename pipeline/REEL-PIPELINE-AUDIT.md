# Reel Pipeline — Deep Audit Report

**Date:** 2026-07-07  
**Scope:** `reel-pipeline.py`, `music_selector.py`, `distribute-reels.py`, `x-autopost.py`, cron definitions, DB state (`prebuilt_reels`), music library  
**Trigger:** Persistent bugs, distribution gaps, and general pipeline fragility

---

## Executive Summary

The reel pipeline works, but it's held together by duct tape. Five systemic problems stand out:

1. **QA is theater.** Visual safe-zone QA fails on every AI-generated infographic (text always lands in the safe zone). The cron worker — an AI agent — manually overrides it every single time. The check adds API cost, latency, and complexity for zero value.

2. **Variant labels are inconsistent across code paths.** `process_queue()` uses `"music"`/`"voice"`, `main()` uses `"music-only"`/`"voiceover"`. The DB has four different filename patterns (`reel-music.mp4`, `reel-music-only.mp4`, `reel-voice.mp4`, `reel-voiceover.mp4`). The SQL LIKE cleanup pattern in `_register_reel` can cross-match and silently delete the wrong variant.

3. **Music-only reels are second-class citizens.** 7 of the last 20 music-only reels have no `yt_video_id` — they were never distributed to YouTube. `main()` explicitly skips YouTube upload for non-voiceover variants, and `distribute-reels.py` is the only fallback path, but it's unreliable.

4. **The "automation" is really an AI doing manual work on a schedule.** The cron worker is a full AI agent session that generates images with `generate_media`, writes `scenes.json`, manually overrides QA, and then calls the Python pipeline. The pipeline's own `auto_pick_article()` and `generate_images_api()` are never used in cron mode. This is expensive, slow, and fragile.

5. **DB hygiene is poor.** Orphan rows with null slugs/headlines, local filesystem paths stored as `video_path`, duplicate registrations, and mixed `yt_video_id` formats (bare IDs vs. full URLs) all erode trust in the data.

---

## Strategy Critique

### The Two-Variant Approach

Every pipeline run builds two variants: music-only and voiceover. In theory this maximizes platform coverage (voiceover for YouTube/IG, music-only for X/Threads). In practice:

- Music-only reels are built but frequently never distributed — 35% of recent music-only reels (7/20) have no YouTube upload and unclear distribution to other platforms.
- Both variants share the same visuals, so the only difference is the audio track. Building both doubles Shotstack render costs.
- The voiceover variant gets priority everywhere: `main()` uploads only voiceover to YouTube, and the cron worker focuses on voiceover registration.

**Recommendation:** Pick one variant as the default and make the second opt-in. If voiceover performs better (it likely does on YouTube), make music-only a fallback for platforms where voiceover doesn't work well (X), not a mandatory second build.

### The Cron Worker Is an AI Agent

The `videshi-reel-pipeline` cron doesn't just run a Python script. It spawns a full AI agent that:
1. Decides which article to build a reel for
2. Generates 5 infographic images via `generate_media`
3. Writes `scenes.json` with captions and timings
4. Calls `reel-pipeline.py --manual-images --scenes scenes.json`
5. Manually overrides QA failures
6. Registers and uploads the result

This means the pipeline's own article selection (`auto_pick_article()`) and image generation (`generate_images_api()`) code paths are dead in production. The pipeline is just a TTS → Shotstack → registration tool. The AI agent is doing the creative work every time, which is:
- **Expensive** — a full agent session per reel
- **Non-deterministic** — the agent makes different choices each run
- **Fragile** — the agent has to "know" to override QA, handle errors, etc.

**Recommendation:** Either invest in making the pipeline's built-in article selection and image generation good enough to run autonomously (no agent), or accept the agent-driven model and strip out the dead code paths to reduce confusion.

### QA Adds Cost, Not Value

The visual safe-zone QA check (GPT-4o vision call) costs tokens and adds latency on every run. It was designed to catch text/logos bleeding into platform-cropped zones. But AI-generated infographics almost always have text in the safe zone — that's the point of an infographic. Every single recent cron run shows the pattern:

> "Visual safe-zone QA flagged... I manually registered and uploaded"

The QA gate is a speed bump the cron agent drives over every time. It protects against nothing.

**Recommendation:** Disable the visual QA check for AI-generated infographics. If you want QA, make it check something that actually varies (readability, brand consistency, aspect ratio correctness), not text-in-safe-zone on text-heavy images.

---

## Bug Inventory

### BUG-1: `story_mood` undefined in `process_queue()` — Latent crash

**Location:** `reel-pipeline.py`, line ~1958  
**Severity:** Low (dormant — mood override is disabled in the selector)  
**Details:** `process_queue()` passes `story_mood=story_mood` to `select_music()`, but `story_mood` is never defined in that scope. If the mood-override code path in `music_selector.py` were re-enabled, this would crash with `NameError`.  
**Fix:** Either define `story_mood` by calling the GPT mood extraction, or remove the parameter entirely since mood override is disabled.

---

### BUG-2: Variant label mismatch between `process_queue()` and `main()`

**Location:** `reel-pipeline.py`, lines ~1982–1988 vs. ~2280–2285  
**Severity:** High  
**Details:**  
- `process_queue()` uses labels `"music"` and `"voice"` → files become `reel-music.mp4`, `reel-voice.mp4`  
- `main()` uses labels `"music-only"` and `"voiceover"` → files become `reel-music-only.mp4`, `reel-voiceover.mp4`  
- The DB has all four patterns in `video_path`  

This means:
- Code that pattern-matches on filenames (distributor, dedup) has to handle four patterns instead of two
- Any new code that assumes one naming convention will silently miss half the reels

**Fix:** Standardize on one pair of labels. `"music-only"` and `"voiceover"` are more descriptive. Update `process_queue()` to match `main()`.

---

### BUG-3: SQL LIKE cross-match in `_register_reel()` — Silent data deletion

**Location:** `reel-pipeline.py`, line ~2406  
**Severity:** High  
**Details:** `_register_reel()` deletes existing rows matching:
```
video_path.like.*reel-{variant_label}.mp4
```
When `variant_label="music"`, the pattern `%reel-music.mp4` also matches `reel-music-only.mp4` (SQL `LIKE` with `%` wildcard). Registering a `"music"` variant could silently delete a `"music-only"` row for the same article.

**Fix:** Use an exact suffix match or anchor the pattern more tightly. For example:
```
video_path.like.*reel-music.mp4  →  video_path.eq.<exact_path>
```
Or use `ilike` with a more specific pattern that excludes `-only`.

---

### BUG-4: `yt_video_id` format inconsistency

**Location:** `prebuilt_reels` table  
**Severity:** Medium  
**Details:** Most rows store bare YouTube video IDs (`MYzKMO_j0T4`), but at least one stores a full URL (`https://youtube.com/shorts/Qv32AtPc_4Q`). The `_check_yt_exists()` function (line ~2340) checks for URL patterns, and `distribute-reels.py` stores bare IDs. Dedup logic comparing these will fail — a reel with a full-URL `yt_video_id` won't match a bare-ID check, potentially causing duplicate YouTube uploads.

**Fix:** Normalize to bare IDs on write. Add a migration to strip URL prefixes from existing rows.

---

### BUG-5: `main()` skips YouTube upload for music-only

**Location:** `reel-pipeline.py`, line ~2287  
**Severity:** Medium  
**Details:** In `main()`, the YouTube upload loop has:
```python
if variant != "voiceover":
    continue
```
This means music-only reels built via `main()` (i.e., the cron path) are never uploaded to YouTube inline. The only path to YouTube for music-only is `distribute-reels.py`, which runs on a separate cron. But `distribute-reels.py` has had infra failures (daemon shutdowns), and 7 of the last 20 music-only reels have `yt_video_id=null`.

**Fix:** Either upload music-only to YouTube in `main()` as well, or make `distribute-reels.py` more reliable and add monitoring for undistributed reels.

---

### BUG-6: Visual QA blocks pipeline, cron agent always overrides

**Location:** `reel-pipeline.py` (QA check) + cron worker behavior  
**Severity:** Medium (operational waste, not a crash)  
**Details:** The visual safe-zone QA check flags every AI-generated infographic (text in safe zone is expected for infographics). The cron worker — an AI agent — recognizes the failure and manually registers/uploads anyway, every single time. The last 5+ cron runs all show this pattern.  
**Impact:** Wasted GPT-4o vision API cost per run, added latency, and a false sense of quality gating.

**Fix:** Disable visual QA for infographic-style reels, or replace it with a check that adds actual value.

---

### BUG-7: `music_selector.py` field naming confusion

**Location:** `music_selector.py`, line ~54  
**Severity:** Low  
**Details:** `_tracks_in_family()` filters tracks by `category` field, but the concept being filtered is "music family" (e.g., `tech-corporate`, `emotional-inspiring`). Meanwhile, the pipeline uses `category` to mean "article category" (e.g., `business`, `politics`). The dual meaning of `category` across files is confusing and error-prone.

**Fix:** Rename the music index field from `category` to `family` for clarity, and update `_tracks_in_family()` accordingly.

---

### BUG-8: `sb-convergence.mp3` family/category mismatch

**Location:** Music index  
**Severity:** Low  
**Details:** `sb-convergence.mp3` is listed with `family=tech-corporate` but `category=emotional-inspiring`. Since the selector filters on `category`, this track appears in the `emotional-inspiring` pool but is tagged as belonging to the `tech-corporate` family. It may play on emotionally-toned articles when a tech-corporate track was intended, or vice versa.

**Fix:** Align the `category` to match the `family`, or update both to reflect the track's actual character.

---

### BUG-9: Orphan row in DB — null slug and headline

**Location:** `prebuilt_reels` table  
**Severity:** Low (data hygiene)  
**Details:** A row for the Diljit article (created 2026-07-06T21:05) has `article_slug=null` and `headline=null`. Likely a manually registered reel where metadata wasn't populated. The distributor should handle nulls gracefully, but this row pollutes queries and reporting.

**Fix:** Backfill the metadata or delete the orphan row. Add a NOT NULL constraint on `article_slug` to prevent recurrence.

---

### BUG-10: Local filesystem path stored as `video_path`

**Location:** `prebuilt_reels` table (EB-5 article row)  
**Severity:** Medium  
**Details:** One row's `video_path` is `/home/hatch/workspace/your_files/reel-voice-eb5...mp4` — a local filesystem path, not a Supabase storage URL. Any distributor or front-end trying to fetch this URL will get a 404. The video exists locally but was never uploaded to storage.

**Fix:** Upload the file to Supabase storage and update the row. Add validation in `_register_reel()` to reject non-URL paths.

---

### BUG-11: Dead code paths in production

**Location:** `reel-pipeline.py` — `auto_pick_article()`, `generate_images_api()`  
**Severity:** Low (not a bug per se, but a maintenance burden)  
**Details:** Since the cron worker is an AI agent that handles article selection and image generation externally, the pipeline's built-in `auto_pick_article()` and `generate_images_api()` functions are never called in production. They're maintained, tested against, and add complexity — but they're dead code in the current architecture.

**Fix:** Either invest in making these work autonomously (and remove the AI agent from the cron), or strip them out and document that the pipeline expects external article selection and image provision.

---

### BUG-12: `story_mood` GPT call is wasted tokens

**Location:** `reel-pipeline.py`, line ~790 (mood extraction) and ~2218 (passed to selector)  
**Severity:** Low  
**Details:** The pipeline still asks GPT for `story_mood` (a vision API call analyzing the article's emotional tone), and passes the result to `select_music()`. But mood override is disabled in the selector — `story_mood` is ignored. This wastes GPT tokens on every run.

**Fix:** Remove the mood extraction call until/unless mood-based music selection is re-enabled.

---

## Reliability Gaps

### Distribution Is Fire-and-Forget

`distribute-reels.py` runs on a cron, but:
- Most runs have `result_summary=null` — there's no way to verify what was actually distributed without checking each platform manually.
- The cron has had infra failures (daemon shutdown on Jul 7 16:00).
- There's no alerting for undistributed reels. 7 music-only reels silently fell through the cracks.

**Recommendation:** Add a summary output to each distribution run (reels attempted, succeeded, failed per platform). Add a monitoring query for reels where `qa_passed=true` but platform IDs are null after 24 hours.

### Duplicate Registration

The Persistent Systems article has two rows in `prebuilt_reels` with the same `video_path`. The dedup logic in `_register_reel()` uses a SQL LIKE match on `video_path`, but if the registration runs twice in quick succession (or with different variant labels), duplicates can slip through.

**Recommendation:** Add a unique constraint on `(article_slug, video_path)` or `(article_slug, variant_label)` to prevent duplicates at the DB level.

### No End-to-End Health Check

There's no single query or dashboard that answers: "Is the reel pipeline healthy?" You have to manually cross-reference cron run logs, DB rows, and platform uploads. When something breaks silently (like music-only YouTube uploads), it can go unnoticed for days.

**Recommendation:** Build a simple health-check query: for each of the last N reels, verify `qa_passed`, `video_path` is a valid URL, and all expected platform IDs are populated. Surface this in the pipeline's output or as a periodic audit.

---

## Music Library Audit

### Overview
- **Total tracks:** 52
- **Source:** Primarily Scott Buckley (royalty-free)
- **Families:** tech-corporate, emotional-inspiring, warm-hopeful, etc.
- **Index location:** `music/track_index.json`

### Issues Found

| # | Issue | Severity |
|---|-------|----------|
| 1 | `sb-convergence.mp3`: `family=tech-corporate` but `category=emotional-inspiring` — mismatch | Low |
| 2 | Orphan file: `test-scott-buckley-legions.mp3` exists on disk but is not in the index | Low |
| 3 | Field naming: `category` in the index means "music family," not article category — confusing | Low |

### Library Health

The library is otherwise clean. All 52 indexed tracks have consistent metadata (BPM, energy, tags). The selection algorithm (`music_selector.py`) maps article categories to music families sensibly. The main risk is the small library size — 52 tracks across ~6 families means heavy rotation and potential listener fatigue over time.

**Recommendation:** Expand the library to 80–100 tracks, focusing on underrepresented families. Fix the `sb-convergence.mp3` metadata. Remove or index the orphan test file. Rename the `category` field to `family` for clarity.

---

## Recommendations — Ranked by Impact

| Priority | Recommendation | Effort | Impact |
|----------|---------------|--------|--------|
| **P0** | Fix variant label mismatch (BUG-2) — standardize to `"music-only"`/`"voiceover"` in both code paths | Small | Prevents cross-match deletion (BUG-3) and simplifies all downstream pattern matching |
| **P0** | Fix SQL LIKE cross-match in `_register_reel` (BUG-3) — use exact path match instead of LIKE | Small | Prevents silent deletion of wrong variant rows |
| **P1** | Disable visual safe-zone QA for AI-generated infographics (BUG-6) | Small | Saves GPT-4o vision cost per run, removes the pointless override dance |
| **P1** | Add distribution monitoring — alert on reels undistributed after 24h | Medium | Catches the silent music-only YouTube gap (BUG-5) and any future distribution failures |
| **P1** | Normalize `yt_video_id` to bare IDs (BUG-4) + add validation on write | Small | Prevents duplicate YouTube uploads |
| **P2** | Clean up DB: fix orphan row (BUG-9), local path (BUG-10), duplicate registration | Small | Data hygiene — makes queries trustworthy |
| **P2** | Upload music-only to YouTube in `main()` or make `distribute-reels.py` reliable (BUG-5) | Medium | Ensures music-only reels actually reach YouTube |
| **P2** | Remove dead `story_mood` extraction (BUG-12) | Small | Saves GPT tokens every run |
| **P3** | Rename music index `category` → `family` (BUG-7) + fix `sb-convergence.mp3` (BUG-8) | Small | Reduces confusion, prevents wrong-family selection |
| **P3** | Decide on pipeline architecture: autonomous script vs. AI-agent-driven (BUG-11) | Large | Reduces cost and complexity long-term, but requires significant rearchitecture |
| **P3** | Expand music library to 80–100 tracks | Medium | Reduces listener fatigue over time |

---

## Appendix: File Naming Patterns in DB

```
reel-voiceover.mp4    ← from main()
reel-music-only.mp4   ← from main()
reel-voice.mp4        ← from process_queue()
reel-music.mp4        ← from process_queue()
```

The distributor handles both via `'voiceover' in vpath or 'voice' in vpath.split('/')[-1]` — this works by accident (both `reel-voiceover.mp4` and `reel-voice.mp4` contain "voice"), but it's fragile. Standardizing the labels eliminates this ambiguity.

---

*End of audit. All findings are based on code as of 2026-07-07 and the most recent 20 rows in `prebuilt_reels`.*
