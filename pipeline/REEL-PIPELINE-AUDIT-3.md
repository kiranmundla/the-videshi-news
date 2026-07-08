# Reel Pipeline — Third Audit Report

**Date:** 2026-07-08  
**Scope:** Verify all round-2 fixes, find remaining issues  
**Previous audits:** `REEL-PIPELINE-AUDIT.md` (round 1), `REEL-PIPELINE-REAUDIT.md` (round 2)

---

## 1. Round 2 Fix Verification

### ✅ 1. `upload_youtube()` privacy → "public"

**Line 1763:** `"privacyStatus": "public"` — confirmed. Was "unlisted".

### ✅ 2. `_check_yt_exists()` per-variant filter

**Lines 2327-2345:** Now builds `exact_path = f"reel-gen/{article_id}/reel-{variant_label}.mp4"` and filters with `video_path=eq.{exact_path}`. Each variant is checked independently. Fixed correctly.

### ✅ 3. `_save_yt_video_id()` sets `yt_posted_at`

**Lines 2349-2364:** Sets both `yt_video_id` and `yt_posted_at` via `datetime.datetime.utcnow().isoformat() + "Z"`. The `import datetime` is inside the function (line 2355) — works fine, just unconventional.

### ✅ 4. YouTube titles differentiated

**Lines 1741-1744:**
```python
if variant == "voiceover":
    title = headline[:89] + " 🎙️ #Shorts"
else:
    title = headline[:89] + " 🎵 #Shorts"
```
Fixed correctly. Both pipeline and distributor now produce differentiated titles.

### ✅ 5. `distribute-reels.py` variant_tag standardized

**Lines 230-231:**
```python
is_voiceover = 'voiceover' in vpath
variant_tag = 'voiceover' if is_voiceover else 'music-only'
```
Fixed — uses `'music-only'` instead of the old `'music'`.

### ✅ 6. `process_queue` story_mood

**Line 1960:** `select_music(article, build_dir, story_mood=None)` — hardcoded None. No NameError risk.

### ✅ 7. `sys.exit(1)` in TTS/Whisper → RuntimeError

**Line 886:** `raise RuntimeError("HeyGen TTS timed out after 3 attempts")` ✅  
**Line 890:** `raise RuntimeError(f"TTS failed: {r.status_code}")` ✅  
**Line 999:** `raise RuntimeError(f"Whisper transcription failed: {r.status_code}")` ✅  

All three helper functions now raise RuntimeError, which `process_queue`'s `except Exception` will catch.

### ✅ 8. Variant labels in `process_queue`

**Line 1984:** `_register_reel(music_reel_path, "music-only", ...)` ✅  
**Line 1990:** `_register_reel(vo_reel_path, "voiceover", ...)` ✅  

### ✅ 9. SQL LIKE patterns

Zero remaining. Verified via `grep -n "like\.\*reel" reel-pipeline.py` → no matches. All three call sites (`_register_reel` delete, `_save_yt_video_id` patch, `_check_yt_exists` query) use exact path match.

### ✅ 10. Visual QA disabled

**Line 2251:** `vis_passed, vis_issues = True, []` — hardcoded. `qa_visual_check()` function still exists (line 1282) but is never called. No GPT-4o vision tokens wasted.

### ✅ 11. `story_mood` removed from GPT prompt

**Lines 789-793:** The GPT prompt no longer mentions `story_mood`. The return JSON template is `{"voiceovers": [...]}` only. The extraction at line 819 is `story_mood = None` with a comment explaining why. The return value at line 842 still returns `story_mood` but it's always None.

### ✅ 12. `_register_reel` variant validation

**Lines 2367-2370:**
```python
if variant_label not in ("music-only", "voiceover"):
    print(f"  ⚠️ Invalid variant_label '{variant_label}' — must be 'music-only' or 'voiceover'")
    return
```
Guard in place. Invalid labels are rejected with a clear message.

### Summary: 12/12 verified ✅

All round-2 fixes landed correctly.

---

## 2. New Issues Found

### ISSUE-1: `sys.exit(1)` in `fetch_article()` and `build_reel()` kills `process_queue` loop

**Severity:** P1  
**Location:**
- `fetch_article()` line 144: `sys.exit(1)` if article not found
- `build_reel()` line 1579: `sys.exit(1)` if Shotstack render POST fails
- `build_reel()` line 1603: `sys.exit(1)` if Shotstack render status = "failed"
- `build_reel()` line 1606: `sys.exit(1)` if Shotstack render times out

**Impact:** `SystemExit` does NOT inherit from `Exception`. `process_queue`'s `except Exception` at line 2007 will not catch it. A single article failure (bad article ID, Shotstack outage) kills the entire queue loop, skipping all remaining entries.

**Note:** TTS (`generate_tts`) and Whisper (`get_word_timestamps`) were fixed to `RuntimeError` in round 2. But these four call sites were missed.

**Fix:** Replace all four `sys.exit(1)` calls with `raise RuntimeError(...)`. The ones inside `main()` flow (lines 268, 697, 2177) are fine as `sys.exit` since `main()` runs as a one-shot entrypoint.

---

### ISSUE-2: `qa_check_reel` called with legacy variant labels

**Severity:** P3 (cosmetic, no functional impact)  
**Location:**
- Line 2238: `qa_check_reel(music_reel_path, "music", ...)` — passes `"music"` not `"music-only"`
- Line 2244: `qa_check_reel(vo_reel_path, "voice", ...)` — passes `"voice"` not `"voiceover"`

**Impact:** None — the QA function uses `variant == "voice"` at line 1244 to gate voice-specific checks (duration mismatch, silence detection). Since it's called with `"voice"`, the gate works. `"music"` just means no voice-specific checks, which is correct.

But this is confusing: every other call site uses the standardized labels. Anyone reading the code will wonder why QA gets the old labels.

**Fix:** Change to `qa_check_reel(music_reel_path, "music-only", ...)` and `qa_check_reel(vo_reel_path, "voiceover", ...)`, and update the check at line 1244 to `if variant == "voiceover"`.

---

### ISSUE-3: Stale comments contradict actual behavior

**Severity:** P3 (cosmetic)  
**Location:**
- Line 2279: `# For each variant: register (upsert) + upload to YouTube (voiceover ONLY — one reel per article on YT)`  
  → Both variants upload now.
- Line 2286: `# Check ANY variant for this article — one article = one YouTube Short`  
  → Now checks per-variant.

**Fix:** Update comments to match reality.

---

### ISSUE-4: `main()` copy output uses inconsistent filenames

**Severity:** P3 (cosmetic — these are local workspace copies, not DB paths)  
**Location:**
- Line 2265: `reel-music-{slug_short}.mp4` — "reel-music" not "reel-music-only"
- Line 2269: `reel-voice-{slug_short}.mp4` — "reel-voice" not "reel-voiceover"

Meanwhile `process_queue` (line 1988) correctly uses `reel-voiceover-{slug_short}.mp4`.

**Impact:** Zero — these are only local copies in `~/workspace/your_files/`. But it's inconsistent.

---

### ISSUE-5: DB data inconsistency — 1 row will trigger duplicate YouTube upload

**Severity:** P1  
**Location:** `prebuilt_reels` table

The Diljit article row `14ecc7dc-593d-4166-a9ac-cc8e43b827e8` has `yt_video_id=4A3aUsXHtRA` but `yt_posted_at=null`. This was uploaded before the round-2 fix that added `yt_posted_at` to `_save_yt_video_id`.

The distributor checks `yt_posted_at` to decide if YouTube upload is needed (line 97: `if not reel.get('yt_posted_at')`). Since it's null, the distributor will try to re-upload this reel on the next run → **duplicate YouTube Short**.

**Fix:** Backfill `yt_posted_at` on this row:
```sql
UPDATE prebuilt_reels SET yt_posted_at = created_at
WHERE yt_video_id = '4A3aUsXHtRA' AND yt_posted_at IS NULL;
```

---

### ISSUE-6: DB data inconsistency — 6 rows with `yt_posted_at` set but `yt_video_id` null

**Severity:** P3 (no functional impact)  
**Location:** `prebuilt_reels` table — EB-5, Diaspora Seniors (×2), H1B Renewals, Global Talent, Diljit rows

These rows have `yt_posted_at` timestamps but null `yt_video_id`. This happened when Kiran deleted YouTube shorts and the `yt_video_id` was cleared, but `yt_posted_at` was left.

**Impact:** The distributor sees `yt_posted_at` as set → skips YouTube upload. So no duplicates. But the data is inconsistent — these rows claim "posted to YouTube" but have no video ID.

**Non-fix:** Leave as-is. The `yt_posted_at` prevents re-upload, which is correct since the originals were deleted intentionally. Clearing `yt_posted_at` would cause the distributor to re-upload them, which is not wanted.

---

### ISSUE-7: `distribute-reels.py` no video download error handling

**Severity:** P2  
**Location:** Lines 583-589

```python
vr = requests.get(video_url, stream=True)
for chunk in vr.iter_content(8192):
    tmp.write(chunk)
```

No status code check on the download response. If `video_url` returns 404/403 (Supabase storage TTL, deleted file), the script writes an error HTML page as the "video" and passes it to YouTube upload → YouTube rejects it, but with an opaque error.

**Fix:** Add `vr.raise_for_status()` after the GET.

---

### ISSUE-8: `distribute-reels.py` old-style variant detection fragile

**Severity:** P2  
**Location:** Line 230

```python
is_voiceover = 'voiceover' in vpath
```

This catches new-style `reel-voiceover.mp4` but NOT old-style `reel-voice.mp4`. The 3 remaining old-style `reel-voice.mp4` rows in DB will be tagged as `music-only` by the distributor → wrong variant suffix (🎵 instead of 🎙️), wrong dedup key.

**Fix:**
```python
is_voiceover = 'voiceover' in vpath or vpath.endswith('reel-voice.mp4')
```

---

### ISSUE-9: YouTube title may exceed 100 chars

**Severity:** P2  
**Location:** `reel-pipeline.py` line 1742

```python
title = headline[:89] + " 🎙️ #Shorts"
```

The suffix `" 🎙️ #Shorts"` is 11 Python characters (the emoji 🎙️ = U+1F399 + U+FE0F = 2 code points). Total: 89 + 11 = 100 Python chars, but **105 UTF-8 bytes**. YouTube's documentation says "100 characters" — if they measure characters (code points), then 🎙️ counts as 2, making the total 101. Some API implementations count bytes.

The distributor (`distribute-reels.py` line 250) computes `max_headline = 100 - len(variant_suffix)`, which is the same approach.

**Impact:** May fail on some titles with `invalidTitle` error (400). Borderline — needs testing.

**Fix (safe):** Use `headline[:87]` to leave room for multi-codepoint emoji:
```python
title = headline[:87] + " 🎙️ #Shorts"  # 87 + 2 (emoji codepoints) + 8 (" #Shorts") + space = 98
```

---

### ISSUE-10: 5 old-style variant rows in DB won't match new exact-path filters

**Severity:** P3 (harmless unless re-built)  
**Location:** `prebuilt_reels` table — 3 `reel-voice.mp4` + 2 `reel-music.mp4` rows

`_check_yt_exists()` now uses exact path `reel-gen/{id}/reel-{variant}.mp4` where variant is `music-only` or `voiceover`. Old rows with `reel-voice.mp4` or `reel-music.mp4` won't match.

**Impact:** If these articles are ever re-built, `_check_yt_exists` won't find the old YouTube ID → new YouTube upload. But since these are old articles, they're unlikely to be re-built.

**Fix:** Leave as-is. The old rows are harmless legacy data.

---

### ISSUE-11: `process_queue` doesn't upload to YouTube

**Severity:** P2 (only matters if `--from-queue` is used)  
**Location:** Lines 1976-1995

`process_queue` registers reels via `_register_reel()` but never calls `upload_youtube()`. The variables `youtube_music_url` and `youtube_voice_url` (lines 1978-1979) are set to `None` and never assigned. YouTube upload for queue-built reels relies entirely on the distributor.

**Impact:** Queue-built reels need to wait for the next distributor cycle (6h) to reach YouTube. Not a bug per se — the distributor handles it — but it's inconsistent with `main()` which uploads immediately.

---

### ISSUE-12: `distribute-reels.py` doesn't write `yt_posted_at` to youtube-log.json

**Severity:** P3  
**Location:** Lines 319-325

The distributor writes to both the DB (`yt_posted_at` via `patch_reel`) and `youtube-log.json`. But the pipeline's `_save_yt_video_id` only writes to the DB, not to `youtube-log.json`.

**Impact:** If the distributor runs and checks `youtube-log.json` for a pipeline-uploaded reel, it won't find it there. But the DB check (`yt_posted_at`) runs first and will catch it. So no functional issue — the log is a secondary dedup layer.

---

## 3. DB Health

| Check | Result |
|-------|--------|
| Orphan rows (null slug/headline) | ✅ 0 |
| Local filesystem paths in video_path | ✅ 0 |
| Full-URL yt_video_ids | ✅ 0 |
| Null video_url rows | ✅ 0 |
| Duplicate article+variant combos | ✅ 0 |
| yt_video_id set, yt_posted_at null | ⚠️ 1 row (Diljit — will cause duplicate) |
| yt_posted_at set, yt_video_id null | ℹ️ 6 rows (intentional — deleted shorts) |
| Old-style variant paths | ℹ️ 5 rows (legacy, harmless) |
| **Total rows** | **80** |

### Variant Distribution
| Pattern | Count |
|---------|-------|
| Other (legacy `ss-reel-*` etc.) | 58 |
| `reel-voiceover.mp4` (new standard) | 10 |
| `reel-music-only.mp4` (new standard) | 7 |
| `reel-voice.mp4` (old standard) | 3 |
| `reel-music.mp4` (old standard) | 2 |

### Music Library
| Check | Result |
|-------|--------|
| Total tracks | 52 |
| Missing `category` field | 0 ✅ |
| Missing `family` field | 0 ✅ |
| Category/family mismatches | 0 ✅ |
| Missing on disk | 0 ✅ |
| Families with < 2 tracks | 0 ✅ |
| Smallest family | breaking-news, chill-lifestyle (4 each) |

---

## 4. Overall Assessment

### What's fixed and solid
- ✅ Variant labels are standardized everywhere that matters
- ✅ SQL injection-style LIKE patterns eliminated
- ✅ Both variants upload to YouTube with differentiated titles
- ✅ YouTube uploads are public, not unlisted
- ✅ `yt_posted_at` is set on upload, preventing distributor re-uploads
- ✅ Visual QA theater eliminated (saves GPT-4o tokens)
- ✅ `story_mood` no longer asked for or used
- ✅ Music library is complete and consistent
- ✅ Music selector is robust with safe defaults
- ✅ DB is clean (no orphans, no bad paths, no duplicates)

### What still needs fixing (by priority)

| # | Issue | Severity | Effort |
|---|-------|----------|--------|
| 1 | ISSUE-1: `sys.exit(1)` in `fetch_article` + `build_reel` kills `process_queue` loop | P1 | Small — replace 4 `sys.exit(1)` with `raise RuntimeError(...)` |
| 2 | ISSUE-5: Diljit DB row missing `yt_posted_at` → distributor will re-upload | P1 | Trivial — one SQL UPDATE |
| 3 | ISSUE-7: Distributor doesn't check video download status | P2 | Trivial — add `raise_for_status()` |
| 4 | ISSUE-8: Old-style `reel-voice.mp4` detected as music-only in distributor | P2 | Trivial — add fallback check |
| 5 | ISSUE-9: YouTube title may exceed 100 chars with emoji | P2 | Trivial — reduce headline slice |
| 6 | ISSUE-2: QA called with legacy variant labels | P3 | Small |
| 7 | ISSUE-3: Stale comments | P3 | Trivial |
| 8 | ISSUE-4: Output copy filenames inconsistent | P3 | Trivial |

### Is this pipeline production-ready?

**Conditionally yes.** The `main()` flow (which is what the cron uses) is solid. The two P1 items:

1. **`sys.exit(1)` in helpers** — only matters for `process_queue` (`--from-queue` flag), which the cron doesn't use. If you only use the `main()` flow via cron, this won't bite you. But it's a landmine.

2. **Diljit DB row** — will cause one duplicate YouTube upload on the next distributor run. Fix with a single DB update.

The pipeline will produce correct reels with appropriate music, upload both variants to YouTube as public with differentiated titles, and avoid duplicates. The major failure modes from rounds 1 and 2 (wrong music, unlisted videos, cross-variant deletion, blocked dual upload, missing timestamps) are all resolved.

---

*End of third audit. 12/12 round-2 fixes verified. 12 new issues found: 2 P1, 4 P2, 6 P3. No P0s.*
