# Portrait Reel Strategy — Research Report
## The Videshi: Robust 9:16 Avatar Reel Pipeline

**Date:** 2026-06-08  
**Status:** Research complete, recommendations ready

---

## 1. The Root Cause (Confirmed)

### HeyGen's Portrait Behavior with Kavya

**Kavya's avatar looks were created from 16:9 (1280×720) source footage.** This was confirmed by:

1. **HeyGen avatar API** — preview videos for all Kavya looks are 1280×720 (16:9)
2. **Raw output analysis** — when requesting 1080×1920 from HeyGen:
   - Output file IS 1080×1920 (passes resolution checks)
   - But the actual avatar content occupies only **rows 674–1245** (572px of 1920px = **29.8%** of the frame)
   - Top/bottom padding: 674px each, brightness ~240 (near-white)
   - Content aspect ratio within the frame: **1.89:1** (≈16:9)
   - **HeyGen simply centers the 16:9 scene inside the 9:16 canvas and pads with white**

### Why This Keeps Breaking

The fundamental mismatch: **you can't get a true 9:16 full-frame video from 16:9 source footage** by changing API parameters. This is a physics/geometry problem, not a software bug. Every time we change `dimension` or `aspect_ratio` in the API payload, the same letterboxing occurs because the source footage hasn't changed.

---

## 2. HeyGen API Capabilities (Research Findings)

### What the API Offers

The v2 `POST /v2/video/generate` endpoint accepts:

```json
{
  "video_inputs": [{
    "character": {
      "type": "avatar",
      "avatar_id": "...",
      "avatar_style": "normal"
    },
    "voice": { ... },
    "background": {
      "type": "color",     // or "image"
      "value": "#0D1B2A"   // or URL for image
    }
  }],
  "dimension": {"width": 1080, "height": 1920},
  "aspect_ratio": "9:16"
}
```

Key parameters relevant to portrait:
- **`dimension`** — sets output resolution (can be 1080×1920)
- **`aspect_ratio`** — `"16:9"` or `"9:16"` (the Image-to-Video endpoint supports this explicitly)
- **`background`** — can be `{ "type": "color", "value": "#hex" }` or `{ "type": "image", "value": "url" }`
- **Background removal** — available for photo avatars and via HeyGen Studio UI; the v2 API's avatar `character` object doesn't expose a `remove_background` param directly for standard avatars

### What Does NOT Exist in the API

- No `scale`, `crop`, `zoom`, `framing`, or `layout` parameter for avatar video generation
- No way to tell HeyGen "crop the 16:9 content to fill 9:16"
- No way to force a look to render at a different native aspect ratio than its source footage
- The `background` param replaces the background for looks that support it (photo avatars, certain generated looks), but **does not change the framing** of the avatar within the scene

### How Other Workflows Handle It (n8n Community Patterns)

Reviewed 6+ n8n workflow templates that create 9:16 HeyGen avatar videos. They all use one of two approaches:

1. **Split-screen layout** — Avatar occupies the bottom portion, article/content imagery fills the top. The avatar is NOT full-frame.
2. **Background removal + custom background** — Remove the avatar's original background, then composite the avatar cutout over a 9:16 background. This requires HeyGen's paid background removal feature.
3. **Post-processing** — Generate 16:9 from HeyGen, then use ffmpeg to composite into a branded 9:16 layout with text, graphics, and the avatar band.

**No one gets true full-frame 9:16 from a 16:9 avatar look.** The platform's own documentation says "In HeyGen, you'll most likely want to select vertical orientation" for social media, but this assumes you're using avatar looks designed for that format, or using background removal + layout features.

---

## 3. Available Approaches (Ranked)

### Option A: Request 16:9 from HeyGen → Post-Process to 9:16 News Layout ⭐ RECOMMENDED

**How it works:**
1. Request HeyGen video at **1920×1080 (16:9)** — this is what the avatar source footage is natively
2. Use `portrait_fix.py`'s existing pipeline to compose into 9:16:
   - Branded header (THE VIDESHI logo, badge, headline)
   - Avatar content band (full-width, no letterboxing)
   - Caption zone (navy area for positioned captions)
   - Bottom branding bar (thevideshi.com)
3. Captions use ASS format with precise positioning in the caption zone

**Why this is the best approach:**
- The avatar renders at **native quality** — no upscaling, no padding, no artificial cropping
- The news layout looks **professional and intentional** — like a real TV news broadcast
- The branded zones add value — headline context, branding, call to action
- It's **deterministic** — no dependency on HeyGen's interpretation of portrait dimensions
- It works for ALL of Kavya's existing looks without any changes to HeyGen
- The `portrait_fix.py` module already implements this end-to-end

**Layout:**
```
┌────────────────────┐
│   THE VIDESHI       │  ← 30px from top
│   BREAKING          │  ← gold badge
│   Headline text     │  ← wrapped to 3 lines
│   (3 lines max)     │
├═════════════════════╡  ← gold accent line
│                     │
│   [Avatar 1080×607] │  ← full-width 16:9 content
│                     │
├═════════════════════╡  ← gold accent line
│                     │
│   [Caption zone]    │  ← navy, captions appear here
│                     │
├────────────────────┤
│  thevideshi.com     │  ← bottom branding bar
│  @thevideshi        │
└────────────────────┘
```
Final output: 1080×1920 (9:16), full-screen on mobile.

### Option B: Crop/Zoom 16:9 → 9:16 (Center-crop the avatar)

**How it works:**
1. Request 16:9 from HeyGen
2. Center-crop horizontally to 607×1080 → scale to 1080×1920

**Why NOT recommended:**
- Cropping cuts off the avatar's scene context (furniture, background, setting)
- For sitting avatars (Sofa Front), this might cut off hands/arms
- Standing avatars lose the "grounding" of their environment
- Significantly reduces visible area of the avatar
- The cropped portion may look awkward or unprofessional
- Quality loss from upscaling a 607px-wide crop to 1080px

### Option C: HeyGen Background Removal + Custom Background

**How it works:**
1. Use HeyGen's background removal to isolate Kavya
2. Composite her cutout over a custom 9:16 background

**Why NOT recommended for now:**
- Requires HeyGen's paid background removal feature
- Not reliably available via the v2 API for standard avatar types (only photo avatars and Studio UI)
- Background removal quality is inconsistent — artifacts at hair/clothing edges
- Loses the professional "set" that the avatar looks were designed with
- More API complexity and potential failure points

### Option D: Create New Avatar Looks in 9:16

**How it works:**
1. Upload new avatar footage shot in 9:16 (portrait) format
2. These would natively render full-frame in portrait

**Why NOT recommended for now:**
- Requires new source footage of the person behind Kavya
- Significant cost and time investment
- Worth exploring as a future enhancement once the pipeline is proven

---

## 4. Implementation Recommendations

### 4.1 The Pipeline Should ALWAYS Request 16:9 from HeyGen

**This is the single most important architectural decision.** The `aspect_ratio` and `dimension` in the HeyGen payload should ALWAYS be:

```python
"dimension": {"width": 1920, "height": 1080},
"aspect_ratio": "16:9"
```

**Never request 9:16 from HeyGen for these avatar looks.** This eliminates the root cause entirely — we get clean, native 16:9 footage every time, and our own pipeline handles the portrait conversion.

The DB `aspect_ratio` column on `reel_avatars` should store the **source footage native aspect ratio**, not the desired output format. All Kavya looks should be `"16:9"`.

### 4.2 Portrait Conversion is a Required Pipeline Step, Not Optional

The orchestrator should treat portrait conversion as a mandatory step, not a conditional fix:

```python
# ALWAYS: Request 16:9 from HeyGen
heygen_dimension = {"width": 1920, "height": 1080}
heygen_aspect = "16:9"

# ALWAYS: Convert to portrait news layout after download
portrait_output = portrait_fix.convert_to_news_layout(
    raw_avatar_path, 
    output_path, 
    headline,
    category
)
```

Remove the `detect_letterbox()` conditional. The conversion is always needed because we're always starting from 16:9 and need to end at 9:16.

### 4.3 Category-Aware Badge Text

The portrait layout should use category-appropriate badge text instead of always "BREAKING":

```python
CATEGORY_BADGES = {
    "news": "BREAKING",
    "nri-world": "NRI WORLD",
    "technology": "TECH",
    "markets-finance": "MARKETS",
    "sports": "SPORTS",
    "entertainment": "ENTERTAINMENT",
    "lifestyle-health": "LIFESTYLE",
    "food": "FOOD",
    "travel": "TRAVEL",
}
```

### 4.4 Hook Frame and End Card Must Match the Branded Layout

The hook frame and end card should use the same navy (`#0D1B2A`) background and branding style as the portrait layout, so the entire reel has visual consistency. Currently they're independent — they should share the same design language.

### 4.5 QA Gate Must Be Airtight

The QA gate needs these checks to never let a bad reel through:

| Check | Type | What It Catches |
|-------|------|-----------------|
| `resolution` | BLOCKING | Wrong output dimensions |
| `aspect_ratio` | BLOCKING | Wrong aspect ratio |
| `content_fill` | BLOCKING | Letterboxed/padded content that doesn't fill the frame |
| `audio_stream` | BLOCKING | Missing audio |
| `avatar_facing` | BLOCKING | Side-angle avatar looks |
| `letterboxing` | BLOCKING | Any-color letterbox bars (black, white, or uniform color) |
| `branded_layout` | NEW/BLOCKING | Verify the branded header zone exists (navy background, gold text) |
| `duration` | Warning | Too short or too long |
| `loudness` | Warning | Audio levels out of range |
| `content_alignment` | Warning | Script doesn't match headline |

**The `content_fill` check should use `portrait_fix.detect_letterbox()` as it does now, but it should be a BLOCKING check.** If the final output has letterboxing, the reel must not be published.

**The letterboxing check in `check_visual_quality()` should detect ANY uniform padding** — not just dark. The current code (as recently patched) checks for both dark (`< 15`) and light (`> 240`), which is correct.

**New check: `branded_layout`** — Extract a frame and verify that the top 15-20% of the frame has the expected navy background color (not white, not blank). This confirms the portrait conversion actually ran.

### 4.6 End-to-End Validation

After the full pipeline runs (including assembly, music, normalization), run a final ffprobe check:

```python
def validate_final_output(video_path):
    """Hard validation that final output is correct before any upload."""
    probe = ffprobe(video_path)
    w, h = probe.width, probe.height
    assert w == 1080 and h == 1920, f"Wrong resolution: {w}x{h}"
    assert probe.duration >= 8, f"Too short: {probe.duration}s"
    assert probe.has_audio, "No audio stream"
    assert os.path.getsize(video_path) > 500_000, "File too small"
    
    # Visual check: top band should be navy (~#0D1B2A), not white/blank
    frame = extract_frame(video_path, t=5)
    top_brightness = frame[:200].mean()
    assert top_brightness < 50, f"Top of frame is bright ({top_brightness}) — portrait layout not applied"
```

---

## 5. Summary: The Architecture

```
Article Selected
      │
      ▼
  Generate Script
      │
      ▼
  HeyGen API  ──────────  ALWAYS 1920×1080 (16:9)
      │                    Never request 9:16
      ▼
  Raw 16:9 Avatar Video
      │
      ▼
  Portrait Conversion  ──  ALWAYS runs (not conditional)
      │                    Branded news layout
      ▼                    Header + Avatar + Captions + Footer
  1080×1920 Portrait
      │
      ▼
  Burn Captions  ─────────  ASS format, positioned in caption zone
      │
      ▼
  Assemble  ──────────────  Hook + Avatar + End Card
      │                     All segments 1080×1920
      ▼
  Add Music + Normalize
      │
      ▼
  QA Gate  ───────────────  BLOCKING checks:
      │                     - Resolution 1080×1920
      │                     - Content fills frame
      │                     - No letterboxing
      │                     - Branded layout present
      │                     - Audio present
      ▼
  Upload (only if QA passes)
```

### Key Principles:
1. **Request what HeyGen can deliver natively (16:9)**
2. **Own the portrait conversion ourselves (deterministic, branded)**
3. **QA gate blocks anything that doesn't look right**
4. **Never assume — verify every step**

---

## 6. Database Changes Needed

Update all `reel_avatars` records to store the truth:

```sql
UPDATE reel_avatars SET aspect_ratio = '16:9';
-- aspect_ratio = source footage native format, NOT desired output
```

Add a column or config for desired output format:

```sql
ALTER TABLE reel_avatars ADD COLUMN output_format text DEFAULT '9:16';
-- output_format = what the pipeline produces after post-processing
```

---

## 7. Files That Need Changes

| File | Change |
|------|--------|
| `reel-orchestrator.py` | Request 16:9 from HeyGen. Always run portrait conversion. Use category-aware badges. |
| `portrait_fix.py` | Add `convert_to_news_layout()` wrapper that doesn't need letterbox detection (it's always needed). Add category badge mapping. |
| `reel_qa_gate.py` | Add `branded_layout` check. Make `content_fill` blocking. Ensure letterbox check catches all colors. |
| `reel_avatars` DB | Set all `aspect_ratio` to `16:9` (source native). |
| Hook frame / end card | Match navy branding style of portrait layout. |

---

## 8. Why This Won't Break Again

The previous approach was fragile because it depended on **HeyGen producing the right output directly**. The correct approach is:

1. **We control the output format** — HeyGen gives us raw footage, we shape it
2. **The pipeline is deterministic** — same input always produces same output
3. **The QA gate catches regressions** — if something goes wrong, the reel is blocked before anyone sees it
4. **No conditional logic** — portrait conversion always runs, not "if letterboxed"
5. **Single source of truth** — avatar DB says 16:9 (the truth), pipeline converts to 9:16 (the goal)

The root cause of the recurring breakage was treating the HeyGen dimension parameter as the solution. It's not. The solution is owning the portrait conversion ourselves.
