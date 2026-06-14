# Reel QA Findings — 2026-06-14 05:00 PDT

## What was tested
- Trigger: "Testing quality upgrades: caption pills, varied transitions, expanded image pool"
- 3 production renders attempted for article: EB-5 Investor Green Card cap
- All 3 failed QA (scores: 4, 0, 4)

## Bug fixed: Caption overlap ✅
- Root cause: `build_script_captions()` added +0.15s to each caption duration, causing 29/30 clips to overlap
- Fix: Removed padding, added gap enforcement (trim each clip to end ≥0.02s before next starts)
- Result: 0/30 overlaps after fix
- Also moved captions from `position: bottom` to `position: center, offset.y: 0.12` to clear lower-third

## Bug found (non-negotiable): Overlapping text
- Run 2 got score 0 for "overlapping_text" — two text layers rendered on top of each other
- Root cause: caption clips (Track 0) were at `position: bottom, offset.y: 0.18` — same zone as lower-third (Track 3, `position: bottom`, 500px tall)
- Fix: moved captions to center position with y-offset 0.12 (above lower-third)

## Persistent issue: Image sourcing quality
- `source_storyboard_images()` fills scenes from same-CATEGORY article pool, NOT by storyboard scene relevance
- For a visa policy article, it pulled: Flickr fashion show photo, Nifty IT chart, RBI FCNR article image, India-US relations image
- Storyboard describes specific scenes ("Closed sign on U.S. embassy", "worried businessman") but these are never used to SEARCH for images — they just grab whatever's available from other news articles
- This is the root cause of "image relevance is low" QA feedback (scored 4/10)

## Recommended fix for image sourcing
1. **Don't use same-category article images as B-roll** — category match ≠ topic match
2. **Use storyboard scene descriptions to search Pexels/Wikipedia FIRST** — reverse the priority order
3. **Validate hero image relevance** — the article's own hero may be from a stock photo pool and unrelated
4. **Consider CLIP/embedding matching** — compare scene description embeddings to candidate images

## Credits spent
- 3 production renders × ~$0.20 = ~$0.60 (all failed QA)
