# YouTube Shorts Safe Zone — Research & Solutions

**Date**: 2026-07-06  
**Problem**: GPT-generated reel images frequently place text/data in YouTube's UI overlay zones despite prompt instructions.

---

## 1. Definitive Safe Zone Dimensions (2026)

Based on multiple authoritative sources (PostPlanify, Hopper HQ, Kreatli, AdvertHunt):

| Zone | Pixels from edge | What's overlaid |
|------|-------------------|-----------------|
| **Top** | 120px (conservative: 180px) | Status bar, notch, Dynamic Island |
| **Bottom** | 300px normal / 360px expanded desc (conservative: 390px) | Channel name, title, CTA, subscribe, music ticker |
| **Right** | 96px (conservative: 120px) | Like, comment, share, subscribe buttons |
| **Left** | 0px (conservative: 60px) | Minimal overlap, but worth respecting |

### Computed safe zones on 1080×1920 canvas:

| Mode | Safe zone box (x1, y1, x2, y2) | Inner size |
|------|------|------------|
| **Normal view** | (0, 120, 984, 1620) | 984 × 1500 |
| **Expanded description** | (0, 120, 984, 1560) | 984 × 1440 |
| **Conservative (recommended)** | (60, 180, 960, 1530) | 900 × 1350 |
| **Current pipeline setting** | (55, 190, 920, 1440) | 865 × 1250 |

The current pipeline safe zone (x:55–920, y:190–1440) is actually **more conservative than necessary** at the bottom (1440 vs 1530 normal). This is good — provides extra margin.

---

## 2. Why Prompt Instructions Fail

GPT image generation models (gpt-image-1) fundamentally **do not follow pixel-level spatial constraints**. The model:
- Has no concept of "x:55" or "top 10%"
- Treats spatial instructions as loose suggestions at best
- Fills the entire canvas artistically, especially for infographic/data card content
- Tends to stack content top-to-bottom and center-distribute, naturally drifting into bottom margins

**Conclusion**: Prompt engineering alone will never solve this reliably. A **post-generation enforcement mechanism** is required.

---

## 3. Evaluated Approaches

### Approach A: Buffer Zone Compositing (PIL Post-Processing) ⭐ RECOMMENDED

**Concept**: Generate images at full size, then crop the content area to the safe zone and composite onto a 1080×1920 canvas with branded treatment in the margins. This **guarantees** nothing in the danger zones by construction.

**Dimensions**:
- Generate content at full size (1152×2048 or 1024×1536)
- Extract safe zone: **900 × 1350px** from the center
- Place on 1080×1920 canvas at: offset (90, 190) — centered horizontally, positioned in the safe region vertically
- Remaining margins: 90px left, 90px right, 190px top, 380px bottom

**Margin treatment** (best option — Extended Scene):
Scale the generated image to fill 1080×1920 (cover mode), blur and darken it, then paste the sharp content crop over the center. The background bleeds into margins but is covered by YouTube UI anyway. Image still looks full-bleed to viewers, but all actual text/data lives in the safe center.

#### Implementation (PIL):

```python
from PIL import Image, ImageFilter, ImageEnhance

def enforce_safe_zone(img_path):
    """Enforce YouTube Shorts safe zone via compositing.
    
    Crops the content area to the safe zone (900x1350), places it on a
    1080x1920 canvas with a blurred/darkened background extension.
    """
    CANVAS_W, CANVAS_H = 1080, 1920
    SAFE_X, SAFE_Y = 90, 190
    SAFE_W, SAFE_H = 900, 1350
    
    img = Image.open(img_path).convert("RGBA")
    orig_w, orig_h = img.size
    
    # Background: scale to fill, blur heavily, darken
    scale = max(CANVAS_W / orig_w, CANVAS_H / orig_h)
    bg = img.resize((int(orig_w * scale), int(orig_h * scale)), Image.LANCZOS)
    bx = (bg.width - CANVAS_W) // 2
    by = (bg.height - CANVAS_H) // 2
    bg = bg.crop((bx, by, bx + CANVAS_W, by + CANVAS_H))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=20))
    bg = ImageEnhance.Brightness(bg).enhance(0.5)
    
    # Content: extract the safe zone area proportionally
    fx = orig_w / CANVAS_W
    fy = orig_h / CANVAS_H
    content = img.crop((
        int(SAFE_X * fx), int(SAFE_Y * fy),
        int((SAFE_X + SAFE_W) * fx), int((SAFE_Y + SAFE_H) * fy)
    ))
    content = content.resize((SAFE_W, SAFE_H), Image.LANCZOS)
    
    # Composite: sharp content over blurred background
    canvas = bg.convert("RGBA")
    canvas.paste(content, (SAFE_X, SAFE_Y))
    
    out_path = os.path.splitext(img_path)[0] + ".png"
    canvas.convert("RGB").save(out_path, "PNG")
    if out_path != img_path and os.path.exists(img_path):
        os.remove(img_path)
    return out_path
```

**Pros**:
- 100% reliable — impossible for content to be in danger zones
- No OCR, no AI vision, no regeneration cost
- Fast (~0.1s per image in PIL)
- Works for BOTH infographic/data cards AND photographic scenes
- Full-bleed appearance preserved (blurred background fills margins)
- No additional API costs

**Cons**:
- Effective content area is reduced from 1080×1920 to 900×1350 (loses ~34% of pixels)
- If GPT generated something beautiful at full-bleed, we're cropping it
- The blurred/darkened margin is visible on platforms that DON'T have UI overlays

**Verdict**: **Best primary solution**.

---

### Approach B: Prompt-Only Generation at Safe Zone Size

**Concept**: Generate directly at a size matching the safe zone aspect ratio (1024×1536, which is 2:3 = same as 900:1350), then pad onto 1080×1920.

**Problem**: GPT image gen only supports specific sizes. The closest is 1024×1536 (same aspect ratio as 900×1350). Generate at that size, resize to 900×1350, composite onto canvas.

**Pros**: GPT uses full canvas for content, same safe zone guarantee.
**Cons**: Requires changing generation pipeline, fewer source pixels (1024×1536 vs 1152×2048).

**Verdict**: Good variant of A if generation size can be controlled.

---

### Approach C: Post-Generation OCR Detection + Reject/Regenerate

**Concept**: OCR the danger zone regions, reject if text detected.

**Problem**: `pytesseract` is NOT installed. Even if it were:
- OCR often misses stylized/infographic text (decorative fonts, colored text on colored backgrounds)
- Regeneration costs $0.02-0.08 per image per attempt
- No guarantee GPT fixes the violation on retry
- Adds 30-60s per scene retry

**Verdict**: **Not recommended**. Too unreliable and expensive.

---

### Approach D: Gradient Overlay / Vignette in Margins

**Concept**: Apply semi-transparent gradient darkening to danger zones. Content stays full-bleed but margin content becomes de-emphasized.

```python
from PIL import Image, ImageDraw

def apply_margin_gradient(img_path):
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Bottom gradient (25% of frame)
    for y in range(int(h * 0.70), h):
        progress = (y - int(h * 0.70)) / (h * 0.30)
        draw.line([(0, y), (w, y)], fill=(0, 0, 0, int(180 * progress)))
    
    # Top gradient (10%)
    for y in range(0, int(h * 0.12)):
        progress = 1 - (y / (h * 0.12))
        draw.line([(0, y), (w, y)], fill=(0, 0, 0, int(120 * progress)))
    
    # Right gradient (15%)
    for x in range(int(w * 0.85), w):
        progress = (x - int(w * 0.85)) / (w * 0.15)
        draw.line([(x, 0), (x, h)], fill=(0, 0, 0, int(140 * progress)))
    
    result = Image.alpha_composite(img, overlay)
    result.convert("RGB").save(img_path, "PNG")
```

**Pros**: Full-bleed preserved, fast, free, creates cinematic vignette effect.
**Cons**: Does NOT prevent text from being hidden — just makes it less visible. Important data in bottom 25% still obscured.

**Verdict**: **Good supplement**, not a primary fix.

---

### Approach E: Shotstack Frame Overlay Track ⭐ RECOMMENDED SUPPLEMENT

**Concept**: Create a 1080×1920 RGBA PNG frame with transparent center (safe zone) and semi-transparent gradient borders. Add as TOP track in Shotstack render — composited on top of scene images.

**Implementation**:
1. Create PNG: transparent center, soft 30-40% black gradient in margins
2. Upload to Supabase as `branding/safe-zone-frame.png`
3. Add top track in both `build_music_only_reel()` and `build_reel()`:

```python
SAFE_ZONE_FRAME_URL = f"{STORAGE_BASE}/branding/safe-zone-frame.png"

frame_clip = {
    "asset": {"type": "image", "src": SAFE_ZONE_FRAME_URL},
    "start": 0,
    "length": round(total_duration, 2),
    "fit": "cover", "position": "center"
}
timeline["tracks"].insert(0, {"clips": [frame_clip]})
```

**Pros**:
- Applied at render time — no PIL pre-processing needed
- One reusable asset
- Consistent branded look across all reels
- Belt-and-suspenders with Approach A

**Cons**:
- Gradient visible in the actual video (not just under YouTube UI)
- Content still there, just darkened

**Verdict**: **Best secondary layer** on top of Approach A.

---

### Approach F: GPT-4o Vision Gate + Regeneration Loop

**Concept**: Make existing `visual_qa_check()` a hard gate — if violations detected, regenerate scene.

**Problem**: Already have the vision check (line 964 in pipeline). But making it a gate means:
- $0.02-0.08 per regeneration × potential 2-3 retries × 5 scenes = up to $1.20 extra per reel
- Each retry adds 15-30s
- GPT may keep failing
- Vision model isn't perfectly reliable at detecting violations

**Verdict**: **Not recommended** as primary. Too costly and unreliable.

---

## 4. How Professional News Channels Handle It

### Al Jazeera / AJ+
- Design for vertical from the start — storyboard specifically for 9:16
- Use strong art direction: presenter-led with motion graphics
- Content naturally centered
- Branded frame with logo and lower-third well above YouTube UI

### CNN Digital
- Card-based design — each "card" has content in the center
- Text overlays composed in editing (not baked into generated images)
- Mobile-first: key elements in center vertical third

### General Industry Pattern
- **Professional channels never rely on the content generator to respect safe zones**
- They use **editing tools** with safe zone overlay templates
- Content is **composed within the safe zone**, with background extending to edges
- Many use a **branded frame/lower-third** system

**Key insight**: The universal approach is **"design within, extend beyond"** — create content for the safe zone, let background/atmosphere fill the margins. This is exactly Approach A.

---

## 5. Final Recommendation: A + E (Compositing + Frame Overlay)

### Primary: **Approach A — Buffer Zone Compositing**

After generating each scene image and before watermark/upload:

1. Scale original to fill 1080×1920 background (blurred + darkened to 50% brightness)
2. Crop the safe zone content from the original (proportionally mapped: 900×1350)
3. Paste sharp content over center at (90, 190)
4. Save as PNG

Wire into `load_manual_images()` and `generate_images_api()` as a post-processing step.

### Supplementary: **Approach E — Shotstack Frame Overlay**

Create branded frame PNG, upload once, add as top track in all renders. Provides:
- Extra visual separation
- Consistent brand look
- Belt-and-suspenders safety

### Keep existing: **Prompt instructions + GPT-4o-mini vision QA**

Don't remove — they catch other quality issues. But no longer the primary safe zone enforcement.

---

## 6. Cost & Performance Impact

| Item | Impact |
|------|--------|
| PIL compositing | ~0.1s per image, 5 images = 0.5s total |
| File size | PNG ~2-4MB vs JPEG 500KB — trivial |
| API costs | **$0 additional** |
| Content area | 900×1350 (still large enough for all infographic types) |
| Shotstack frame | One extra clip per render — negligible |

---

## 7. Decision Matrix

| Approach | Reliability | Cost | Speed | Recommended? |
|----------|------------|------|-------|-------------|
| A. Buffer compositing | ⭐⭐⭐⭐⭐ | Free | Fast | ✅ PRIMARY |
| B. Smaller generation | ⭐⭐⭐⭐⭐ | Free | Fast | ✅ VARIANT |
| C. OCR detection | ⭐⭐ | Moderate | Slow | ❌ Unreliable |
| D. Gradient overlay | ⭐⭐ | Free | Fast | ➕ SUPPLEMENT |
| E. Shotstack frame | ⭐⭐⭐ | Free | Fast | ✅ SUPPLEMENT |
| F. Vision gate + regen | ⭐⭐⭐ | Expensive | Slow | ❌ Too costly |
