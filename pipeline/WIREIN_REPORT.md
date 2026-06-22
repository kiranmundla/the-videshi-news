# Wire-In Report: Animated Data Cards + Music Selector → shotstack-reel.py

Date: 2026-06-22
Test article: `a7752486-756c-489d-a414-cef31334ef52` — "Nikesh Arora Is Spending $28 Billion to Own the AI Security Stack"

## Status: COMPLETE — both features wired into production pipeline, validated end-to-end, nothing distributed.

---

## Part A — Animated Data Cards
- `_anim_card_for_scene()` detector wired into the reel build loop (shotstack-reel.py:73). Primary path reads GPT `card_style` + structured payload (`hero_stat`, `stat_grid`, `diaspora_panel`); secondary keyword fallback for older cached scripts. Each archetype used at most once/reel; scene 0 always skipped; falls back to static PIL card on malformed payload or render failure.
- `_used_archetypes` set tracks usage (line 4404); animated MP4 uploaded with `is_anim_card=True, trim=0` (plays from t0, line 4479-4483).
- GPT schema extended with `card_style` + `story_mood` fields; cache bumped `clean4`→`clean5`.
- `anim_cards.py` QA polish: hero count-up lands at 42% of clip, tighter grid count-up, darker grid labels, brighter diaspora bullets, dynamic panel label from title.

## Part B — Music Selector + CC-BY Auto-Credit
- `pick_music_for_article()` (line 1482) wraps the mood selector, falls back to legacy `CATEGORY_MUSIC` dict (kept, not deleted). Returns `(music_url, music_volume, attribution)`.
- Both call sites replaced: `run_anchor_reel` (uses `story_mood` from script_data, line 6137) and `run_quick_pulse` (story_mood=None, line 6297).
- CC-BY credit appended to caption as `\n\n🎵 {attribution}` before `register_reel()`, gated on non-empty attribution (lines 6256, 6333).
- `register_reel` extended with `music_attribution` kwarg; payload includes it with graceful 400-retry stripping if the column doesn't exist (lines 5589, 5619-5637).

---

## Validation evidence
- AST parse + module import clean; all new functions present in HEAD.
- Detector unit tests: 6/6 pass.
- E2E Run 1 (no card_style): QA **8**, music=tech-corporate mood=tech CC0, no-publish.
- E2E Run 2 (injected card_styles): all 3 cards rendered, QA **9**.
- Card frames visually confirmed with the article's REAL figures:
  - Hero @20.8s: **$28B** (article figure, not SpaceX).
  - Grid @25.4s: **$25B** CyberArk, **$3.35B** Chronosphere, **2018** Arora/Palo Alto, **CYBR** Tel Aviv listing.
  - Diaspora @16.2s: Nikesh Arora / Palo Alto / Indian engineers / dual-merger risk.
- CC-BY flow proven live: `pick_music_for_article` returns the Kevin MacLeod attribution for CC-BY moods (investigative/epic/tech/default) and empty string for CC0 (tense). Index has 13 CC-BY tracks across 13 mood profiles.

## Distribution-script edit needed? NO
The `caption` stored in `prebuilt_reels` is the authoritative source all distribution crons read for every platform; the credit is appended there, so no per-platform distributor edit is required.

## Safety / no side effects
- `prebuilt_reels` rows for test article: **0** (count */0) — nothing registered or distributed. Test runs were `--no-publish`.
- QA scoring logic unchanged; gate still ≥7.
- Backup intact: `/tmp/shotstack-reel.py.wirein.bak` (296KB).
- CATEGORY_MUSIC fallback dict retained.

## ⚠️ Git note (important)
During the session, automated data-refresh crons committed AND PUSHED to `origin/main`. The cron at 23:56 (`d7b006fc "live: data refresh 2026-06-21T23:56"`) ran `git add -A` and swept my uncommitted pipeline edits (shotstack-reel.py +335 lines, anim_cards.py +23 lines) into its commit alongside the JSON data refresh. That commit is now on `origin/main` (local even with remote, 0/0). The code is intact and correct, but the wire-in is **already live in production and pushed** — it was not held as a local-only change. No crons or distribution scripts were modified by me.
