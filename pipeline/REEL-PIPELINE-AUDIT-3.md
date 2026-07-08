# Reel Pipeline Audit #3 — 2026-07-08

## Round 2 Fix Verification

All 12 fixes from round 2 confirmed:

| # | Fix | Status |
|---|---|---|
| 1 | upload_youtube() privacy = "public" | ✅ Line 1763 |
| 2 | _check_yt_exists() per-variant exact path | ✅ Line 2328 |
| 3 | _save_yt_video_id() sets yt_posted_at | ✅ Line 2358 |
| 4 | YouTube titles 🎙️/🎵 differentiated | ✅ Lines 1742/1744 |
| 5 | distribute-reels variant_tag = 'music-only' | ✅ Line 231 |
| 6 | process_queue story_mood = None | ✅ Line 1960 |
| 7 | sys.exit(1) in TTS/Whisper → RuntimeError | ✅ Lines 886/890/999 |
| 8 | Variant labels 'music-only'/'voiceover' in process_queue | ✅ Lines 1984/1990 |
| 9 | Zero SQL LIKE patterns | ✅ grep confirms 0 |
| 10 | Visual QA disabled | ✅ Line 2251 |
| 11 | story_mood not in GPT prompt | ✅ Removed from prompt |
| 12 | _register_reel validates variant labels | ✅ Line 2375 |

## Additional Fixes Applied This Round

1. **Remaining sys.exit(1) in shared functions** — 6 more found in fetch_article, generate_storyboard, load_manual_images, build_reel (3). All replaced with RuntimeError. Only main()-only sys.exit calls remain (lines 2048, 2177).

2. **qa_check_reel variant labels** — was using old "music"/"voice" labels internally. Updated to "music-only"/"voiceover" and the voice-specific check condition (line 1244).

3. **5 legacy DB rows with old video_path labels** — verified videos are accessible (HTTP 200). Left as-is since they reference real storage objects; exact-path matching in new code ensures they're isolated from new rows.

## DB Health

- Duplicates: 0 ✅
- Null video_urls: 0 ✅
- Old variant labels in video_path: 5 (legacy, isolated)
- Full-URL yt_video_ids: 0 ✅

## Remaining Known Limitations

1. **No concurrency guard** — two overlapping cron runs could build the same article twice. Low probability since cron interval is 8h and builds take ~5 min. Mitigation: _register_reel upserts, so the second build just overwrites.

2. **Music-only render failure is silent** — returns (None, None) and pipeline continues with voiceover only. This is acceptable behavior: voiceover should still proceed.

3. **Legacy 5 DB rows** — old video_path labels. Functional but won't match new exact-path queries. Will age out naturally.

## Overall Assessment

**Production-ready.** All critical paths verified. No more sys.exit bombs in shared functions. Variant labels standardized end-to-end. YouTube uploads go public with timestamps. DB is clean. Distributor aligned.
