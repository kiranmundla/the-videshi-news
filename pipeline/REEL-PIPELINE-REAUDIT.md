# Reel Pipeline — Re-Audit Report

**Date:** 2026-07-08  
**Scope:** Verify 12-bug fix round, find new bugs  
**Previous audit:** `REEL-PIPELINE-AUDIT.md` (2026-07-07)

---

## 1. Fix Verification

### ✅ BUG-2: Variant Label Mismatch — FIXED

`process_queue()` now uses `"music-only"` (line 1980) and `"voiceover"` (line 1986), matching `main()` (line 2277). `_register_reel()` has a validation guard (line 2364) that rejects any label other than `"music-only"` or `"voiceover"`.

**Residual issue:** The DB still contains 4 rows with `reel-voice.mp4` and 2 rows with `reel-music.mp4` from before the fix. These old-style rows are harmless (they won't be overwritten by the new-style code — different exact paths), but they may confuse dedup logic. See NEW-BUG-1.

### ✅ BUG-3: SQL LIKE Cross-Match — FIXED

All three LIKE patterns replaced with exact path match (`video_path=eq.{exact_path}`):
- `_register_reel()` delete (line ~2406)
- `_save_yt_video_id()` patch (line ~2347)

No remaining `like.*reel-` patterns in the file. Verified via grep.

### ⚠️ BUG-5: Music-Only Never Reaches YouTube — PARTIALLY FIXED (Critical regression)

The `if variant != "voiceover": continue` skip was removed (line ~2292), so both variants now enter the YouTube upload branch. **However, `_check_yt_exists()` still checks ANY variant for the article (line 2324, comment: "One article = one YouTube Short"), not per-variant.** 

This means when the loop processes `[(music-only, ...), (voiceover, ...)]`:
1. Music-only: no existing YT → uploads → saves `yt_video_id` on music-only row
2. Voiceover: `_check_yt_exists` finds music-only's `yt_video_id` → **SKIPS upload**, copies the wrong video ID to the voiceover row

**The BUG-5 fix is effectively neutralized.** Only the first variant in the loop will ever upload. See **NEW-BUG-2** for the full analysis and fix.

### ✅ BUG-6: Visual QA Theater — FIXED

Line 2247 now hard-codes `vis_passed, vis_issues = True, []` with a clear comment explaining why. The `qa_visual_check()` function still exists (line 1282) but is never called. No GPT-4o vision tokens wasted.

### ✅ BUG-7: Music Selector Field Naming — NOT FIXED (by design)

The selector still filters on `category` (line 54 of `music_selector.py`: `t.get("category") == family`). The audit recommended renaming the field to `family` for clarity. This was not done — the fix instead ensured all tracks have the `category` field populated, which is the pragmatic approach. The naming confusion remains but causes no runtime bugs.

### ✅ BUG-8: sb-convergence.mp3 Mismatch — FIXED

`sb-convergence.mp3` now has `family: "emotional-inspiring"` and `category: "emotional-inspiring"` — aligned.

### ✅ BUG-9: Orphan DB Row — FIXED

No rows with null `article_slug` or `headline` remain. Verified via query.

### ✅ BUG-10: Local Filesystem Path — FIXED

The EB-5 reel was uploaded to Supabase storage and `video_path` corrected. No remaining `/home/*` paths in DB. Verified via query.

### ✅ BUG-4: yt_video_id Format — FIXED

No remaining full-URL `yt_video_id` values in DB. The `_save_yt_video_id()` function (line ~2347) already strips URLs to bare IDs (`vid = yt_url.rstrip("/").split("/")[-1].split("?")[0]`).

**Note:** `_check_yt_exists()` (line 2336) still has a `if yt_id.startswith("http")` branch that returns the URL. This is now dead code since no URLs exist, but if one ever crept back in, it would propagate a URL to `_save_yt_video_id` which would then strip it again. Harmless but messy.

### ⚠️ BUG-12: story_mood GPT Call Wasted — PARTIALLY FIXED

The GPT prompt no longer asks for `story_mood` (removed from line ~790). `story_mood` is set to `None` (line 819) and `if False:` guards the print (line 836). The return still includes `story_mood` (line 842) but it's always `None`.

**However, `process_queue()` still references `story_mood` at line 1956** (`select_music(article, build_dir, story_mood=story_mood)`) **without ever defining it.** This is the original BUG-1 from the audit — still unfixed. If `process_queue()` is ever called (via `--from-queue`), it will crash with `NameError: name 'story_mood' is not defined`.

### Summary

| Bug | Status | Notes |
|-----|--------|-------|
| BUG-2 | ✅ FIXED | Old DB rows remain but harmless |
| BUG-3 | ✅ FIXED | All LIKE patterns eliminated |
| BUG-4 | ✅ FIXED | DB cleaned, write path already strips |
| BUG-5 | ⚠️ INCOMPLETE | `_check_yt_exists` ANY-variant check blocks second upload |
| BUG-6 | ✅ FIXED | Visual QA bypassed |
| BUG-7 | ✅ ACCEPTABLE | Field naming unchanged but all data correct |
| BUG-8 | ✅ FIXED | family/category aligned |
| BUG-9 | ✅ FIXED | Orphan deleted |
| BUG-10 | ✅ FIXED | Uploaded and path corrected |
| BUG-11 | ✅ KNOWN | Dead code, low priority |
| BUG-12 | ⚠️ PARTIAL | Prompt fixed, but BUG-1 (NameError in process_queue) still open |

---

## 2. New Bugs Found

### NEW-BUG-1: `upload_youtube()` Uploads as UNLISTED, Not Public

**Location:** `reel-pipeline.py` line 1759  
**Severity:** P1  
**Details:** `upload_youtube()` in `reel-pipeline.py` sets `"privacyStatus": "unlisted"`. But `post_youtube_video()` in `distribute-reels.py` sets `"privacyStatus": "public"` (line 282). Since the `main()` flow now uploads to YouTube directly (not via the distributor), ALL reels uploaded by the pipeline cron are **unlisted on YouTube** — invisible to viewers.

The distributor was the path that set them to public, but now that `main()` uploads directly, the distributor won't re-upload (it sees `yt_posted_at` is set and skips). So reels uploaded via `main()` stay unlisted permanently.

**Fix:** Change line 1759 to `"privacyStatus": "public"`.

### NEW-BUG-2: `_check_yt_exists()` Blocks Dual-Variant Upload

**Location:** `reel-pipeline.py` lines 2323-2341  
**Severity:** P0  
**Details:** `_check_yt_exists()` queries for ANY `yt_video_id` on the article, regardless of variant. Its comment says "One article = one YouTube Short" — this was correct when only voiceover uploaded, but now that both variants should upload, it blocks the second.

In `main()`, the loop processes `[(music-only, ...), (voiceover, ...)]`. After music-only uploads and `_save_yt_video_id` writes its ID, `_check_yt_exists` for voiceover finds the music-only ID → skips voiceover upload → copies the wrong ID to the voiceover row.

**Fix:** `_check_yt_exists()` must filter per-variant:
```python
def _check_yt_exists(article_id, variant_label):
    exact_path = f"reel-gen/{article_id}/reel-{variant_label}.mp4"
    r = requests.get(
        f"{SB_URL}/rest/v1/prebuilt_reels?article_id=eq.{article_id}"
        f"&video_path=eq.{exact_path}"
        f"&yt_video_id=not.is.null&yt_video_id=neq.dedup-skip"
        f"&select=yt_video_id&limit=1",
        headers=SB_HEADERS, timeout=10
    )
```

### NEW-BUG-3: `upload_youtube()` No Variant Title Differentiation

**Location:** `reel-pipeline.py` line 1740  
**Severity:** P1  
**Details:** `upload_youtube()` builds title as `headline[:91] + " #Shorts"` — no 🎙️/🎵 variant suffix. When both variants upload (after NEW-BUG-2 is fixed), they'll have **identical titles on YouTube**, making them indistinguishable.

Meanwhile, `distribute-reels.py` line 248-251 correctly differentiates titles with `" 🎙️"` / `" 🎵"` suffixes. The pipeline's `upload_youtube()` needs the same logic.

**Fix:** Add variant-aware title construction:
```python
variant_suffix = " 🎙️" if variant in ("voiceover", "voice") else " 🎵"
max_headline = 100 - len(variant_suffix)
title = headline[:max_headline].rstrip() + variant_suffix
```

### NEW-BUG-4: `process_queue()` — `story_mood` NameError (BUG-1 Unfixed)

**Location:** `reel-pipeline.py` line 1956  
**Severity:** P2 (latent — `process_queue` is only called via `--from-queue`, which the cron doesn't use)  
**Details:** `story_mood` is referenced but never defined in `process_queue()` scope. If `--from-queue` is ever used, it crashes with `NameError`.

**Fix:** Add `story_mood = None` before the `select_music()` call, or remove the parameter.

### NEW-BUG-5: Duplicate Persistent Systems Rows

**Location:** `prebuilt_reels` DB table  
**Severity:** P2  
**Details:** Article `b8afea69...` has 2 rows with identical `video_path = reel-gen/.../reel-voice.mp4`, created 4 seconds apart (19:40:13 and 19:40:17). This happened because the old LIKE-based dedup in `_register_reel()` ran a DELETE then INSERT as two separate requests — a race window where a second concurrent call could sneak in between.

The new exact-path dedup has the same race window (DELETE + INSERT, not an atomic upsert). If two cron runs or queue entries overlap, duplicates can still occur.

**Fix (immediate):** Delete the older duplicate row. **(deferred)** Use a DB unique constraint on `(article_id, video_path)` or switch to a true upsert (`ON CONFLICT ... DO UPDATE`).

### NEW-BUG-6: Stale Comment in `main()` Loop

**Location:** `reel-pipeline.py` line 2275  
**Severity:** P3 (cosmetic)  
**Details:** Comment says `"voiceover ONLY — one reel per article on YT"` but both variants now upload. Misleading for future readers.

### NEW-BUG-7: `distribute-reels.py` Variant Tag Inconsistency

**Location:** `distribute-reels.py` line 231  
**Severity:** P2  
**Details:** The distributor detects variants via `'voiceover' in vpath or 'voice' in vpath.split('/')[-1]` and tags them as `variant_tag = 'voiceover' if is_voiceover else 'music'`. This has two issues:

1. `variant_tag` is `'music'` for music-only, but the pipeline standardized on `'music-only'`. The youtube-log.json dedup key uses this tag, so pipeline-uploaded music-only reels (logged as `'music-only'` if they were) won't match distributor's `'music'` lookup → potential duplicate uploads.
2. Old `reel-voice.mp4` paths contain `'voice'` → correctly detected as voiceover. Old `reel-music.mp4` paths contain neither `'voiceover'` nor `'voice'` → correctly falls through to `'music'`. This works by accident.

**Fix:** Standardize variant detection:
```python
if 'music-only' in vpath:
    variant_tag = 'music-only'
elif 'voiceover' in vpath:
    variant_tag = 'voiceover'
elif 'voice' in vpath.split('/')[-1]:
    variant_tag = 'voiceover'  # legacy
else:
    variant_tag = 'music-only'  # legacy reel-music.mp4
```

### NEW-BUG-8: `distribute-reels.py` YouTube Dedup Doesn't Check `yt_video_id` Column

**Location:** `distribute-reels.py` lines 94-98  
**Severity:** P1  
**Details:** YouTube dedup has two sources: the DB (`yt_posted_at` column) and `youtube-log.json`. But the DB dedup at line 94-98 only checks `yt_posted_at`, not `yt_video_id`. Since the pipeline's `main()` flow saves `yt_video_id` but does NOT set `yt_posted_at`, the distributor will see these reels as "not yet uploaded to YouTube" and re-upload them.

When `main()` calls `_save_yt_video_id()`, it only sets `yt_video_id`, not `yt_posted_at`. The distributor then:
1. Checks `yt_posted_at` → null → "needs YT upload"
2. Checks youtube-log.json → not there (pipeline doesn't write to this log)
3. Uploads again → **duplicate YouTube Short**

**Fix (pipeline side):** `_save_yt_video_id()` should also set `yt_posted_at`:
```python
json={"yt_video_id": vid, "yt_posted_at": datetime.now(timezone.utc).isoformat()}
```

### NEW-BUG-9: No Concurrency Guard / Overlap Protection

**Location:** `reel-pipeline.py`, `distribute-reels.py`  
**Severity:** P2  
**Details:** Neither script has any lock/mutex. The reel pipeline cron runs every 8h; distribute-reels runs every 6h. If a cron run takes longer than expected (Shotstack render timeout, slow HeyGen), the next cycle can start while the previous is still running. Both scripts would then:
- Pick the same article (auto_pick_article doesn't check "building" state)
- Register duplicate rows (DELETE + INSERT race window)
- Upload to YouTube twice (no log dedup across concurrent processes)

The 2400s (40min) timeout on the reel pipeline cron provides some protection, but a Shotstack render that takes 20min + HeyGen TTS could push close to that.

**Recommendation:** Add a simple PID file lock at the start of `main()` and `distribute-reels.py` main block.

### NEW-BUG-10: `generate_tts()` Calls `sys.exit(1)` on Failure

**Location:** `reel-pipeline.py` lines 889, 893  
**Severity:** P2  
**Details:** If HeyGen TTS fails after 3 retries or returns non-200, the function calls `sys.exit(1)`. In the `main()` flow this is fine (exits the process). But in `process_queue()`, which iterates over multiple queue entries in a `for` loop with `try/except`, a `sys.exit(1)` will be caught by the `except Exception` handler (since `SystemExit` inherits from `BaseException`, not `Exception`... actually, `sys.exit` raises `SystemExit` which does NOT inherit from `Exception`). 

Wait — `SystemExit` does NOT inherit from `Exception`, so the `except Exception` at line 2003 won't catch it. A TTS failure in `process_queue` will kill the entire process, skipping all remaining queue entries.

**Fix:** Raise a regular exception (e.g., `RuntimeError("HeyGen TTS failed")`) instead of `sys.exit(1)`, so `process_queue`'s exception handler can catch it and continue to the next entry.

---

## 3. DB Health Check

| Check | Result |
|-------|--------|
| Orphan rows (null slug/headline) | ✅ Clean — 0 rows |
| Local filesystem paths | ✅ Clean — 0 rows |
| Full-URL yt_video_ids | ✅ Clean — 0 rows |
| Duplicate article+variant combos | ⚠️ 1 duplicate: Persistent Systems `reel-voice.mp4` (2 rows) |
| Old-style filename patterns | ⚠️ 4 rows with `reel-voice.mp4`, 2 rows with `reel-music.mp4` |
| Total rows | 78 |

### Filename Pattern Distribution

| Pattern | Count | Source |
|---------|-------|--------|
| `reel-voiceover.mp4` | 10 | `main()` (new) |
| `reel-music-only.mp4` | 7 | `main()` (new) |
| `reel-voice.mp4` | 4 | `process_queue()` (old) |
| `reel-music.mp4` | 2 | `process_queue()` (old) |
| `ss-reel-*.mp4` | ~45 | Legacy Shotstack direct renders |
| Other custom names | ~10 | Manual uploads |

---

## 4. Music Library Health

| Check | Result |
|-------|--------|
| Total tracks | 52 |
| Tracks missing `category` field | 0 ✅ |
| Tracks missing `family` field | 0 ✅ |
| Indexed tracks missing from disk | 0 ✅ |
| Indexed variant files missing from disk | 0 ✅ |
| Families with < 2 tracks | 0 ✅ |
| `family` / `category` mismatches | 0 ✅ (sb-convergence fixed) |

### Family Sizes

| Family | Tracks |
|--------|--------|
| anthemic-triumph | 6 |
| breaking-news | 4 |
| chill-lifestyle | 4 |
| cinematic-epic | 8 |
| dramatic-dark | 6 |
| emotional-inspiring | 6 |
| indian-classical | 6 |
| tech-corporate | 5 |
| upbeat-celebration | 7 |

### Edge Case Testing

| Input Category | Resolved Family | Result |
|----------------|----------------|--------|
| `nri-world` | breaking-news | ✅ Correct |
| `NRI World` | breaking-news | ✅ Correct (case-insensitive) |
| `totally-unknown` | breaking-news | ✅ Safe default |
| `""` (empty) | breaking-news | ✅ Safe default |
| `None` | breaking-news | ✅ Safe default |

Music selector is robust — no crash paths found.

---

## 5. Distribution Audit

### `distribute-reels.py` — Critical Issues

1. **Variant tag mismatch (NEW-BUG-7):** Uses `'music'` and `'voiceover'` as variant tags for youtube-log.json dedup, but the pipeline now standardizes on `'music-only'` and `'voiceover'`. Cross-system dedup will break for music-only reels.

2. **Missing `yt_posted_at` from pipeline uploads (NEW-BUG-8):** The pipeline sets `yt_video_id` but not `yt_posted_at`. The distributor checks `yt_posted_at` → sees null → tries to re-upload → duplicate.

3. **YouTube privacy mismatch (NEW-BUG-1):** Pipeline uploads as unlisted; distributor uploads as public. Since the distributor is the fallback path and the pipeline now uploads directly, reels from the pipeline stay unlisted.

4. **X video posting is dead code in the distributor:** `post_x_tweet()` and `post_x_carousel()` exist but are never called in the main loop (line 538: only `ig`, `yt`, `threads` are processed). The cron description says X is handled by `videshi-x-autopost`. Consistent, but the functions are dead weight.

5. **No retry on YouTube upload failure:** If the YouTube upload fails (timeout, quota), it just returns an error string. No retry logic. The next cron run (6h later) would retry, but that's a long gap.

6. **Instagram/Threads broken:** Meta API tokens are from a restricted dev account. Any IG/Threads post attempt will fail. The distributor doesn't pre-check token validity — it'll attempt the post, get an API error, and log it as a failure. Not a code bug, but operational noise.

### Distributor ↔ Pipeline Overlap

Now that `main()` uploads to YouTube directly, there's redundancy:
- **Pipeline (`main()`):** Registers reel → uploads to YouTube (unlisted, no variant suffix in title)
- **Distributor (`distribute-reels.py`):** Finds reel → uploads to YouTube (public, with 🎙️/🎵 suffix)

If both run for the same reel, you get two YouTube uploads with different titles and privacy settings. The youtube-log.json dedup would catch some duplicates, but the pipeline doesn't write to that log.

**Recommendation:** Either:
- (a) Pipeline uploads with correct settings (public, differentiated titles) and sets `yt_posted_at` so the distributor skips YouTube, OR
- (b) Pipeline only registers (no YouTube upload) and lets the distributor handle all YouTube uploads

Option (a) is simpler since the pipeline already has the upload code.

---

## 6. Remaining Risk

### HIGH RISK

| Risk | Impact | Likelihood |
|------|--------|------------|
| NEW-BUG-2: Second variant never uploads to YouTube | Music-only reels still miss YouTube | **Certain** on every run |
| NEW-BUG-1: Pipeline uploads as unlisted | Reels invisible to YouTube viewers | **Certain** on every run |
| NEW-BUG-8: Distributor re-uploads pipeline reels | Duplicate YouTube Shorts | High (next distribute-reels run) |

### MEDIUM RISK

| Risk | Impact | Likelihood |
|------|--------|------------|
| NEW-BUG-3: Identical YouTube titles for both variants | Confusing, unprofessional | Certain (after BUG-2 fix) |
| NEW-BUG-7: Dedup key mismatch across pipeline/distributor | Missed dedup for music-only | Medium |
| NEW-BUG-4: `process_queue` NameError | Crash if `--from-queue` used | Low (cron doesn't use it) |
| NEW-BUG-10: `sys.exit(1)` in TTS | Kills remaining queue entries | Low (process_queue rarely used) |

### LOW RISK

| Risk | Impact | Likelihood |
|------|--------|------------|
| NEW-BUG-5: Duplicate DB rows | Distributor posts twice | Low (requires concurrent runs) |
| NEW-BUG-9: No concurrency guard | Race conditions on overlap | Low (8h interval, 40min timeout) |
| Old-style DB rows (reel-voice/reel-music) | Confusion, not functional impact | Already happened |

### What Could Still Go Wrong

1. **Next reel pipeline run:** Music-only uploads to YouTube (unlisted), voiceover skipped (BUG-2 neutralizes the fix). Then 6h later, distributor finds the voiceover reel with no `yt_posted_at` → uploads it (public, with emoji title). Music-only reel stays unlisted.

2. **Shotstack API outage:** No retry in the render polling loop — it polls 60 times at 10s intervals (10 min), then gives up. The whole pipeline fails, and the article won't get a reel until the next 8h cycle.

3. **HeyGen quota/outage:** `sys.exit(1)` kills the process. In `main()` flow this is fine (one article per run). In `process_queue()` it would skip remaining entries.

4. **YouTube quota (daily upload limit):** No handling for YouTube 403 quota exceeded. If the pipeline uploads 2 reels (both variants) and the distributor uploads 6 more, you could hit the daily limit. The error is logged but no back-off or retry.

---

## Recommended Fix Priority

| # | Fix | Severity | Effort |
|---|-----|----------|--------|
| 1 | **NEW-BUG-2**: Change `_check_yt_exists` to per-variant lookup | P0 | Small |
| 2 | **NEW-BUG-1**: Change `upload_youtube` privacy to `"public"` | P0 | Trivial |
| 3 | **NEW-BUG-8**: Set `yt_posted_at` in `_save_yt_video_id` | P0 | Small |
| 4 | **NEW-BUG-3**: Add variant 🎙️/🎵 suffix to `upload_youtube` title | P1 | Small |
| 5 | **NEW-BUG-7**: Standardize variant tags in `distribute-reels.py` | P1 | Small |
| 6 | **NEW-BUG-4**: Define `story_mood = None` in `process_queue` | P2 | Trivial |
| 7 | **NEW-BUG-5**: Delete duplicate Persistent Systems row | P2 | Trivial |
| 8 | **NEW-BUG-6**: Fix stale comment | P3 | Trivial |
| 9 | **NEW-BUG-10**: Replace `sys.exit(1)` with `RuntimeError` in TTS | P2 | Small |
| 10 | **NEW-BUG-9**: Add PID lock file | P3 | Small |

---

*End of re-audit. 10 new bugs found, 3 are P0 (will cause problems on the next pipeline run).*
