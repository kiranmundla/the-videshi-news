# HeyGen Portrait Reel Strategy — Definitive API Test Results

**Date:** 2026-06-08  
**Method:** Live API testing (7 generated videos + frame analysis) + API documentation research (v2 & v3 docs)  
**Account:** The Videshi production HeyGen account  

---

## Executive Summary

**BREAKTHROUGH FINDING:** HeyGen's v2 API supports `scale` (0.0–5.0), `offset` ({x,y} range -1.0 to 1.0), `avatar_style` ("closeUp"/"normal"), and `background` parameters on the character object. These enable **true full-frame 9:16 portrait video directly from HeyGen** — with zero letterboxing, no post-processing crop/scale needed.

The previous assumption that HeyGen can only produce letterboxed portrait video is **WRONG**.

**Additionally:** The v3 API (`POST /v3/videos`) has a `fit` parameter ("contain"/"cover") that may achieve similar results with cleaner semantics, but v3 does NOT support multi-scene (`video_inputs[]`) — only v2 does. Since our pipeline uses multi-scene, **v2 is the correct API for now**.

---

## API Versions

| API | Endpoint | Multi-Scene | Scale/Offset | Deprecation |
|---|---|---|---|---|
| **v2 (Studio)** | `POST /v2/video/generate` | ✅ `video_inputs[]` | ✅ `character.scale`, `character.offset` | Oct 31, 2026 |
| **v3 (Current)** | `POST /v3/videos` | ❌ Single scene only | ❌ No manual scale/offset | Active, recommended for single-scene |

**Our pipeline uses multi-scene → must use v2.** v3 has `fit: "cover"` which auto-scales to fill frame (worth testing when v3 gets multi-scene support).

---

## Kavya Avatar Inventory

7 Kavya looks found in HeyGen account (all stock avatars, 1280×720 source footage):

| Avatar ID | Name | Status |
|---|---|---|
| `Kavya_standing_indoor_front` | Indoor Front | **Active** |
| `Kavya_sitting_sofa_front` | Sofa Front | **Active** |
| `Kavya_standing_indoor_side` | Indoor Side | Inactive |
| `Kavya_standing_outdoor_side` | Outdoor Side | Inactive |
| `Kavya_standing_outdoorsport_front` | Outdoor Sport Front | Inactive |
| `Kavya_standing_outdoorsport_side` | Outdoor Sport Side | Inactive |
| `Kavya_sitting_sofa_side` | Sofa Side | Inactive |

**Source footage:** All 1280×720 (16:9). Total avatars in account: 1,281 (all stock library).

---

## Live API Test Results (7 Videos Generated)

### Test A — Default portrait (THE PROBLEM)
```json
{"dimension": {"width": 1080, "height": 1920}, "aspect_ratio": "9:16"}
```
- **Content fill: 29.6%** | Top padding: 675px | Bottom: 676px | White bars
- **VERDICT: Massive letterboxing — unusable**

### Test B — Portrait with conflicting aspect_ratio
```json
{"dimension": {"width": 1080, "height": 1920}, "aspect_ratio": "16:9"}
```
- **Content fill: 29.6%** — **IDENTICAL to Test A**
- **VERDICT: `aspect_ratio` parameter is COMPLETELY IGNORED when `dimension` is set**

### Test C — Landscape baseline (native format)
```json
{"dimension": {"width": 1920, "height": 1080}, "aspect_ratio": "16:9"}
```
- **Content fill: 93.8%** | Full-frame avatar
- **VERDICT: Perfect baseline**

### Test D — aspect_ratio only (no dimension)
```json
{"aspect_ratio": "9:16"}  // no dimension
```
- **Output: 1920×1080 LANDSCAPE** — HeyGen defaulted to landscape
- **VERDICT: `aspect_ratio` alone does NOTHING**

### Test E — Portrait + scale=2.0 ⭐
```json
{
  "dimension": {"width": 1080, "height": 1920},
  "character": {"scale": 2.0, "offset": {"x": 0, "y": 0}},
  "background": {"type": "color", "value": "#000000"}
}
```
- **Content fill: 59.3%** (1139px of 1920px) — exactly 2× baseline!
- Black bars instead of white (background param works)
- **VERDICT: `scale` WORKS! Linear scaling confirmed.**

### Test G — Portrait + scale=3.4 ⭐⭐⭐ BREAKTHROUGH
```json
{
  "dimension": {"width": 1080, "height": 1920},
  "character": {"scale": 3.4, "offset": {"x": 0, "y": 0}},
  "background": {"type": "color", "value": "#000000"}
}
```
- **Content fill: 99.9% — FULL FRAME!**
- Zoomed-in talking head: head to waist, centered, beautiful framing
- **VERDICT: TRUE FULL-FRAME PORTRAIT! No letterboxing whatsoever.**

### Test H — Portrait + scale + offset + navy bg ⭐⭐
```json
{
  "dimension": {"width": 1080, "height": 1920},
  "character": {"scale": 1.78, "offset": {"x": 0, "y": -0.3}},
  "background": {"type": "color", "value": "#0a1628"}
}
```
- **Content fill: 46.4%** from top (0 to row 891)
- Avatar shifted UP, navy background fills bottom 54%
- **VERDICT: `offset` WORKS! Can position avatar + use branded bg color below.**

### Scale Behavior (Empirically Measured)

| Scale | Content Fill | Content Height | Math |
|---|---|---|---|
| 1.0 (default) | 29.6% | 569px | Baseline |
| 2.0 | 59.3% | 1139px | 569 × 2.0 = 1138 ✓ |
| 3.4 | 99.9% | 1920px | 569 × 3.37 = 1918 ✓ |

**Formula:** `content_height ≈ 569 × scale` (at 1080×1920)  
**Full-frame scale:** `1920 / 569 ≈ 3.37` → use `3.4`

---

## All Confirmed API Parameters

### V2 Character Object (what we use)

| Parameter | Type | Range | Effect |
|---|---|---|---|
| `scale` | float | 0.0–5.0, default 1.0 | Avatar zoom/size in frame. Linear. |
| `offset` | object | `{x: -1..1, y: -1..1}` | Position shift. Negative y = up. |
| `avatar_style` | string | `"normal"`, `"closeUp"`, `"circle"` | Framing preset. **closeUp untested — may provide built-in zoom** |
| `fit` | string | `"contain"`, `"cover"` | How avatar fits scene. **Cover may auto-fill frame** |
| `matting` | boolean | | Remove avatar background (avatars created after May 2025) |

### V2 Background Object

| Parameter | Type | Effect |
|---|---|---|
| `type` | string | `"color"`, `"image"`, `"video"` |
| `value` | string | Hex color for color type (default `#f6f6fc`) |
| `url` | string | URL for image/video backgrounds |
| `fit` | string | `"cover"`, `"contain"`, `"crop"`, `"none"` |

### V3 API Parameters (for future reference when v3 gets multi-scene)

| Parameter | Type | Effect |
|---|---|---|
| `aspect_ratio` | string | `"9:16"` for portrait |
| `fit` | string | `"contain"` or `"cover"` — **cover should auto-fill frame** |
| `remove_background` | boolean | Remove avatar's original background |
| `background` | object | `{type: "color"/"image", value/url}` |
| `resolution` | string | `"4k"`, `"1080p"`, `"720p"` |

---

## Three Viable Architectures

### Option 1: Post-Process Pipeline (Original Plan)
```
HeyGen: 1920×1080 (16:9, no scale/offset)
  → Full-quality landscape video
  → portrait_fix.py crops/scales into branded 1080×1920 layout
  → Header + avatar + gold accent + captions + branding
```
- **Pros:** Highest quality (native resolution), full layout control
- **Cons:** Complex post-processing (373 lines), extra re-encoding pass

### Option 2: HeyGen Native News Layout ⭐ RECOMMENDED
```
HeyGen: 1080×1920 with scale=2.0-2.5, offset={y: -0.12}, background=#0a1628
  → Avatar fills upper ~50-70% of portrait frame
  → Navy branded background fills lower portion
  → Overlay: header bar at top, captions in navy zone, bottom branding
```
- **Pros:** HeyGen does heavy lifting, simple overlay post-processing, clean caption zone
- **Cons:** 2-2.5× upscaling from 720p source, per-avatar tuning needed

### Option 3: HeyGen Full Portrait (Social-First)
```
HeyGen: 1080×1920 with scale=3.4, background=#000000
  → Full-frame zoomed portrait (talking head selfie style)
  → Overlay captions at bottom over avatar content
```
- **Pros:** Simplest pipeline, most TikTok-native look
- **Cons:** 3.4× upscaling, captions overlap content, no branding space

---

## Recommended Implementation (Option 2)

### HeyGen API Payload
```python
payload = {
    "dimension": {"width": 1080, "height": 1920},
    "video_inputs": [{
        "character": {
            "type": "avatar",
            "avatar_id": avatar_id,
            "avatar_style": "normal",
            "scale": avatar_record.get("portrait_scale", 2.5),
            "offset": {
                "x": avatar_record.get("portrait_offset_x", 0),
                "y": avatar_record.get("portrait_offset_y", -0.12)
            }
        },
        "voice": {
            "type": "text",
            "input_text": script,
            "voice_id": voice_id
        },
        "background": {
            "type": "color",
            "value": avatar_record.get("portrait_bg_color", "#0a1628")
        }
    }]
}
```

### Database Schema Updates
```sql
ALTER TABLE reel_avatars ADD COLUMN portrait_scale FLOAT DEFAULT 2.5;
ALTER TABLE reel_avatars ADD COLUMN portrait_offset_x FLOAT DEFAULT 0;
ALTER TABLE reel_avatars ADD COLUMN portrait_offset_y FLOAT DEFAULT -0.12;
ALTER TABLE reel_avatars ADD COLUMN portrait_bg_color TEXT DEFAULT '#0a1628';
```

### Untested Parameters Worth Trying (next test batch)
1. `avatar_style: "closeUp"` — may provide built-in zoom without manual scale
2. `character.fit: "cover"` — may auto-scale to fill frame
3. `scale: 2.5` + `offset: {y: -0.12}` — the recommended combo (hit daily trial limit before testing)
4. `character.matting: true` + custom background image — could place avatar on any portrait backdrop

---

## Test Artifacts

All test videos and extracted frames saved to:
```
the-videshi-news/pipeline/heygen-tests/
├── kavya_indoor_preview.mp4     # Original preview (1280×720 source)
├── test_A.mp4 + test_A_frame.jpg   # Default portrait (letterboxed)
├── test_B.mp4 + test_B_frame.jpg   # Portrait + 16:9 aspect (identical to A)
├── test_C.mp4 + test_C_frame.jpg   # Landscape baseline (full frame)
├── test_D.mp4 + test_D_frame.jpg   # aspect_ratio only (defaulted landscape)
├── test_E.mp4 + test_E_frame.jpg   # scale=2.0 (59.3% fill)
├── test_G.mp4 + test_G_frame.jpg   # scale=3.4 (99.9% FULL FRAME!)
└── test_H.mp4 + test_H_frame.jpg   # scale=1.78 + offset (shifted up, navy bg)
```

### HeyGen Video IDs
| Test | Video ID | Config Summary |
|---|---|---|
| A | `8906278f16c448cf91dbb993d338def1` | Default portrait |
| B | `2a173019ad774538b85db85b686e1141` | Portrait + 16:9 ar |
| C | `c9272dae6d3f41298689846bca89a72e` | Landscape baseline |
| D | `079df35e521347bfb2c0a9f6e91b9a6c` | ar only (→ landscape) |
| E | `5da24b70b75547ffa2594f2ebaa74589` | scale=2.0 |
| G | `96d4fe2f746449878b9f39c4549b7b49` | scale=3.4 (FULL!) |
| H | `93bf7efde2b744efa75611b737e7c869` | scale=1.78 + offset |

**Daily trial limit:** 8 test videos/day (hit after 8 tests — Tests I & J were rejected).

---

## Critical Notes

1. **`scale` and `offset` ARE documented** in HeyGen's v2 API schema (found in v2 docs), but are not prominently featured in tutorials or help articles. They are stable, supported parameters.

2. **v2 API deprecation deadline: October 31, 2026.** Multi-scene (`video_inputs[]`) has NOT been ported to v3 yet, so v2 is required for our pipeline. When v3 gets multi-scene, test `fit: "cover"` + `aspect_ratio: "9:16"` as a cleaner alternative.

3. **Source quality:** Kavya's 1280×720 source at scale 2.5 means the avatar region is approximately 512×288 upscaled. Acceptable for mobile viewing. A custom portrait-shot avatar would eliminate this entirely.

4. **Per-avatar tuning:** Different Kavya looks need different scale/offset values. Store in DB per-look.

5. **`avatar_style: "closeUp"` is untested** — this built-in zoom preset might provide good framing without manual scale tuning. Priority for next test batch.
