# Reel Pipeline Enhancement Research
**The Videshi — Shotstack Pipeline v2 Improvements**
*Research date: 2026-06-10*

---

## Table of Contents
1. [Current State Assessment](#current-state-assessment)
2. [High Impact Recommendations](#high-impact)
3. [Medium Impact Recommendations](#medium-impact)
4. [Low Impact Recommendations](#low-impact)
5. [Competitive Analysis](#competitive-analysis)
6. [Cost Analysis](#cost-analysis)

---

## Current State Assessment

### What the pipeline does well
- **Solid cloud architecture**: Shotstack production mode, no watermarks, async render+poll
- **Smart image sourcing**: 3-tier waterfall (article hero → AI-matched cross-category → Pexels last-resort) with curated-image preference and dedup log
- **Script generation**: GPT-4o with storyboard-driven scene planning, including search queries for B-roll
- **Word-level captions**: Whisper timestamps → HTML caption clips with proper timing (falls back to Shotstack `rich-caption`)
- **QA gate**: GPT-4o vision reviews 5 extracted frames, with non-negotiable checks for brand integrity
- **Two formats**: Anchor Reel (voice + B-roll) and Quick Pulse (music + text cards)
- **Category-aware**: Music, hashtags, and scoring all tuned per category

### Key gaps and limitations
| Area | Current State | Gap |
|------|--------------|-----|
| **Aspect ratio** | Code says 1080×1920 (9:16 portrait) but summary says switched to landscape due to HeyGen letterboxing | Need to confirm actual output and fix if landscape |
| **TTS voice** | HeyGen v2 preview — single "Indian Anchorwoman" voice | Limited expressiveness, no emotion control, no voice variety |
| **Transitions** | Only `fade` used between B-roll clips | 20+ transition types available in Shotstack unused |
| **Caption style** | Only `highlight` animation on rich-caption fallback | 7 animation styles available (pop, bounce, typewriter, etc.) |
| **Hook frame** | Static HTML overlay on darkened image for 3s | No motion, no animation — dead time for scroll-stopping |
| **Thumbnail/cover** | Not generated — relies on whatever frame IG/YT picks | Shotstack can auto-generate poster + thumbnail at render time |
| **HtmlAsset** | Used extensively for all overlays | **Deprecated** per Shotstack docs — should migrate to `TextAsset` |
| **Render callbacks** | Pipeline polls every 5s up to 60 times | Shotstack supports webhook `callback` URL for async notification |
| **Music library** | 4 tracks, hard-mapped to categories | Repetitive across reels; no dynamic selection |
| **Image-to-video** | Not used | Shotstack has `image-to-video` asset type — can animate stills into short video clips |
| **Text-to-image** | Not used | Shotstack can generate images from prompts inline — could replace Pexels fallback |
| **Sound effects** | None | No whoosh, ding, or breaking-news stinger |
| **CTA end card** | 4-second static HTML card | Long and static — could be shorter + animated |
| **Reel length** | ~30-40s (60-80 word script + 3s hook + 4s CTA) | Good for IG, but YT Shorts rewards 40s+ absolute watch time |

---

## High Impact Recommendations {#high-impact}

### 1. 🎯 Switch back to portrait (9:16) — CRITICAL
**Impact: Very High | Effort: Low**

Every platform penalizes non-native aspect ratios:
- **Instagram Reels**: 1080×1920 (9:16) is the native format. Landscape reels get letterboxed with ugly black bars and reduced feed visibility.
- **YouTube Shorts**: 9:16 required. Landscape content is literally excluded from the Shorts shelf.
- **TikTok/Threads**: Same 9:16 expectation.

**The HeyGen letterboxing problem**: If HeyGen's TTS returns audio only (WAV), there's no video frame to letterbox — the issue may have been from a different HeyGen product (talking avatar). Since the current pipeline uses HeyGen only for TTS audio, there should be no letterboxing concern.

**Implementation:**
```python
# In output config — confirm this is set correctly:
"output": {
    "format": "mp4",
    "size": {"width": 1080, "height": 1920},  # 9:16 portrait
    "fps": 30,
    "quality": "high",
}
```
Verify `build_anchor_reel_timeline()` sets 1080×1920. If the current live output is landscape, this is a one-line fix with massive reach impact.

---

### 2. 🎙️ Upgrade TTS to ElevenLabs (or Voxtral)
**Impact: Very High | Effort: Medium**

The voice is the soul of a news reel. HeyGen's TTS is functional but sounds noticeably synthetic compared to 2026 alternatives.

**Recommended: ElevenLabs v3** (if budget allows)
- Naturalness rating: 4.5/5 vs HeyGen ~3.5/5
- Emotion steering with inline tags: `[excited]`, `[serious]`, `[whispers]`
- 70+ languages with accent preservation
- Indian English voices available (multiple)
- Voice cloning: could clone a real Indian English newsreader with 60s of audio
- **Pricing**: Creator plan $22/mo (121k credits ≈ ~2hrs audio). At 1-2 reels/day × 30s each = ~30-60 min/month. Fits Creator plan.

**Budget alternative: Mistral Voxtral TTS**
- Beat ElevenLabs Flash v2.5 in blind tests (68.4% preference)
- $0.016 per 1,000 characters (~10x cheaper than ElevenLabs)
- Open-weight model available (self-hostable for $0)
- 9 languages including English
- Voice cloning from 3 seconds of audio
- **Catch**: Only 9 languages vs ElevenLabs' 70+, and less mature emotion control

**Another option: Resemble AI Chatterbox**
- MIT-licensed, fully free, outperformed ElevenLabs in blind tests (63.8%)
- 23 languages including Hindi
- Emotion intensity slider
- Requires 8GB+ VRAM GPU (would need a GPU server or cloud function)
- API also available if self-hosting isn't feasible

**Implementation approach for ElevenLabs:**
```python
def generate_tts_elevenlabs(text, voice_id="indian_newsreader"):
    """Generate TTS via ElevenLabs v3 API."""
    # Add emotion tags for news content
    tagged_text = text
    if any(kw in text.lower() for kw in ["breaking", "killed", "crash", "scandal"]):
        tagged_text = f"[serious] {text}"
    
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": ELEVENLABS_KEY},
        json={
            "text": tagged_text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.6,
                "similarity_boost": 0.8,
                "style": 0.4,  # More expressive
            }
        },
        timeout=30,
    )
    # Returns MP3 directly — no WAV→MP3 conversion needed
    mp3_path = BUILD_DIR / "ss-tts-voice.mp3"
    mp3_path.write_bytes(r.content)
    return str(mp3_path), get_audio_duration(mp3_path)
```

---

### 3. 🎬 Animated hook frame (first 1-3 seconds)
**Impact: High | Effort: Medium**

The first 3 seconds determine whether users swipe past. Currently, the hook is a static HTML overlay — no motion, no urgency.

**What top news reels do:**
- Text slams in with `zoom` or `carouselUp` transition (not just appears)
- Red "BREAKING" badge pulses or flashes
- Background image has a faster Ken Burns zoom or a slight shake
- Sound effect (whoosh or news stinger) at 0.0s

**Implementation using Shotstack tweening + transitions:**
```python
# Hook text: slam in from bottom with bounce
hook_clip = {
    "asset": {"type": "html", "html": hook_html, ...},
    "start": 0,
    "length": 3.0,
    "transition": {"in": "zoom"},  # Fast zoom in — grabs attention
    "offset": {
        "y": [  # Tween: slide up and settle
            {"from": -0.3, "to": 0, "start": 0, "length": 0.6,
             "interpolation": "bezier", "easing": "easeOutBack"}
        ]
    },
}

# Category badge: slide in separately with delay
badge_clip = {
    "asset": {"type": "html", "html": badge_html, ...},
    "start": 0.3,  # Staggered — badge appears after main text
    "length": 2.7,
    "transition": {"in": "slideUp"},
    "opacity": [
        {"from": 0, "to": 1, "start": 0, "length": 0.4}
    ],
}
```

**Sound effect layer** — add a 1-second news stinger at t=0:
```python
stinger_track = {
    "clips": [{
        "asset": {"type": "audio", "src": stinger_url, "volume": 0.3},
        "start": 0,
        "length": 1.5,
    }]
}
```

---

### 4. 📐 Platform-specific reel lengths
**Impact: High | Effort: Medium**

Research shows different platforms reward different lengths:

| Platform | Optimal Length | Algorithm Signal | Recommendation |
|----------|--------------|-----------------|----------------|
| **Instagram Reels** | 15-30 seconds | Completion rate (% watched) | Shorter = higher completion = more push |
| **YouTube Shorts** | 40-60 seconds | Total watch time (seconds) | Longer = more seconds watched = more push |
| **TikTok** | 31-60 seconds | Engagement rate | Mid-length sweet spot |
| **Threads** | 15-30 seconds | Shares | Short + shareable |

**Current pipeline**: ~33-40 seconds (3s hook + 25-35s voice + 4s CTA).

**Recommendation**: Generate TWO versions per article:
1. **Short cut (25-30s)**: For IG Reels and Threads — tighter script (40-50 words), 2s hook, 2s CTA
2. **Extended cut (45-55s)**: For YouTube Shorts — fuller script (80-100 words), 3s hook, 3s CTA, extra scene

This can be done by adjusting the GPT script prompt's word count target and rendering both. Cost = 2× Shotstack renders but dramatically better per-platform performance.

**Script prompt modification:**
```python
# For short version:
"LENGTH: 40-50 words. That's 15-22 seconds spoken."
# For extended version:  
"LENGTH: 80-100 words. That's 35-45 seconds spoken. Include one more detail or data point."
```

---

### 5. 📸 Auto-generate thumbnail/cover images
**Impact: High | Effort: Low**

Currently, platforms auto-select a random frame as the thumbnail. YouTube and Instagram both heavily weight click-through rate, and a custom thumbnail dramatically improves CTR.

**Shotstack supports this natively** — just add to the output config:
```python
"output": {
    "format": "mp4",
    "size": {"width": 1080, "height": 1920},
    "fps": 30,
    "quality": "high",
    "poster": {"capture": 1},         # Full-size poster at t=1s (hook frame)
    "thumbnail": {"capture": 1, "scale": 0.5},  # Half-size thumbnail
}
```

The poster and thumbnail are returned alongside the video in the render response. Upload them to Supabase and use them when posting to IG/YT.

**Better approach**: Render a separate thumbnail-specific image using Shotstack's image output:
```python
# Dedicated thumbnail render — bold text on dramatic image
thumb_edit = {
    "timeline": {
        "tracks": [
            {"clips": [hook_text_clip]},    # Big bold text
            {"clips": [hero_image_clip]},   # Dramatic B-roll, darkened
        ]
    },
    "output": {
        "format": "jpg",
        "size": {"width": 1080, "height": 1920},
        "quality": "high",
    }
}
```

---

## Medium Impact Recommendations {#medium-impact}

### 6. 🎨 Varied transitions between scenes
**Impact: Medium | Effort: Low**

Currently only `fade` is used. Shotstack offers 20+ transitions with Fast/Slow variants:

| Transition | Best For | Feel |
|-----------|---------|------|
| `fade` | Default, gentle | Calm |
| `wipeLeft` / `wipeRight` | News scene changes | Professional, TV-like |
| `carouselUp` | Vertical reveals | Energetic, modern |
| `zoom` | Dramatic moments | Impactful, breaking news |
| `reveal` | Uncovering information | Investigative feel |
| `slideUp` | Progressive information | Forward momentum |

**Implementation — category-aware transition sets:**
```python
CATEGORY_TRANSITIONS = {
    "news": ["wipeLeft", "wipeRight", "carouselUp", "zoom"],
    "entertainment": ["slideUp", "carouselLeft", "reveal", "fade"],
    "sports": ["zoom", "carouselUp", "wipeLeftFast", "slideUpFast"],
    "technology": ["fade", "reveal", "slideUp", "wipeRight"],
    "immigration": ["fade", "wipeLeft", "carouselUp", "reveal"],
    "default": ["fade", "wipeLeft", "slideUp", "carouselUp"],
}

# Rotate through transitions per scene
transitions = CATEGORY_TRANSITIONS.get(category, CATEGORY_TRANSITIONS["default"])
for i, url in enumerate(image_urls):
    clip["transition"] = {"in": transitions[i % len(transitions)]}
```

---

### 7. 💬 Rich caption style variety
**Impact: Medium | Effort: Low**

Shotstack's `rich-caption` supports 7 animation styles. Currently only `highlight` is used.

| Style | Effect | Best For |
|-------|--------|---------|
| `highlight` ✅ (current) | Active word changes color | Standard narration |
| `pop` | Active word scales up | Emphasis on key words |
| `bounce` | Spring animation on word | Energetic/entertainment |
| `karaoke` | Word-by-word color fill | Musical/rhythmic pacing |
| `typewriter` | Words appear one by one | Dramatic reveals |
| `fade` | Gradual opacity per word | Softer, emotional stories |
| `slide` | Words slide in from direction | Dynamic, fast-paced |

**Recommendation**: Map caption style to category mood:
```python
CATEGORY_CAPTION_STYLE = {
    "news": "pop",           # Punchy, emphasizes key words
    "entertainment": "bounce", # Energetic
    "sports": "slide",        # Fast-paced
    "technology": "typewriter", # Methodical reveal
    "travel": "fade",          # Softer, evocative
    "default": "highlight",    # Safe default
}
```

---

### 8. 🎵 Expand music library + dynamic selection
**Impact: Medium | Effort: Medium**

Currently 4 tracks mapped to categories. After a few reels, viewers recognize the same music.

**Recommendations:**
1. **Expand to 3-4 tracks per category** (12-16 total) and randomly select per reel
2. **Add a "breaking news" stinger** (2-3 second dramatic intro) for news/immigration categories
3. **Sound effects layer**: Subtle whoosh at transitions, notification ding for stats/numbers
4. **Dynamic music volume**: Use Shotstack's volume tweening to duck music during emphasis points

```python
CATEGORY_MUSIC = {
    "news": [
        "breaking-news-30s.mp3",
        "urgent-news-loop-30s.mp3",
        "investigation-tension-30s.mp3",
    ],
    "entertainment": [
        "chill-lifestyle-30s.mp3",
        "upbeat-pop-30s.mp3",
        "bollywood-fusion-30s.mp3",
    ],
    # ...
}

# Random selection
music_file = random.choice(CATEGORY_MUSIC.get(category, CATEGORY_MUSIC["news"]))
```

**Where to source royalty-free music:**
- [Pixabay Music](https://pixabay.com/music/) — free, no attribution needed
- [Uppbeat](https://uppbeat.io/) — free tier with attribution
- [Epidemic Sound](https://www.epidemicsound.com/) — paid ($15/mo) but excellent quality
- Upload to Supabase storage like the current tracks

---

### 9. 🔄 Use webhook callbacks instead of polling
**Impact: Medium | Effort: Medium**

The current pipeline polls Shotstack every 5 seconds for up to 5 minutes. This is wasteful and ties up the process.

**Shotstack supports webhook callbacks:**
```python
edit_json = {
    "timeline": {...},
    "output": {...},
    "callback": "https://thevideshi.com/api/shotstack-callback",
}
```

When the render completes, Shotstack POSTs to your callback URL with the render ID and status. This allows:
- Cron job submits render and exits immediately
- Callback endpoint handles download + registration
- No wasted polling time
- Can process more reels concurrently

**Implementation**: Add a Vercel serverless function at `/api/shotstack-callback` that:
1. Receives the webhook
2. Downloads the rendered video
3. Runs QA gate
4. Uploads to Supabase storage
5. Registers in `prebuilt_reels`

---

### 10. 🖼️ Use Shotstack's `image-to-video` for animated B-roll
**Impact: Medium | Effort: Medium**

Shotstack can convert still images into short video clips with motion, using AI:
```python
{
    "asset": {
        "type": "image-to-video",
        "src": "https://example.com/photo.jpg",
        "prompt": "Slowly zoom out and orbit left around the object.",
        "aspectRatio": "9:16",
    },
    "start": 3.0,
    "length": 5.0,
}
```

This would replace Ken Burns static zoom with **AI-generated motion** — much more engaging and cinematic. Imagine a still photo of the Taj Mahal slowly rotating to reveal the full building.

**Considerations:**
- Additional render time per clip (AI generation)
- May increase costs
- Quality varies — test with a few scenes first
- Use for hero/scene-1 image only to manage costs; keep Ken Burns for other scenes

---

### 11. 📝 Migrate from HtmlAsset to TextAsset
**Impact: Medium | Effort: Medium-High**

Shotstack's API docs state: **"Notice: The HtmlAsset is deprecated, use the TextAsset instead."**

The current pipeline uses `HtmlAsset` extensively for:
- Hook frame overlay
- Lower third headline
- Captions
- End card
- Logo/watermark text

While it still works, deprecated features can break without notice. Plan a migration.

**Note**: The `TextAsset` may not support the same complex layouts (flexbox, multi-element divs) that the current HTML uses. Test the most complex overlays (hook frame, end card) with TextAsset first before committing to full migration.

---

## Low Impact Recommendations {#low-impact}

### 12. 🧪 Use Shotstack's `text-to-image` as Pexels replacement
**Impact: Low-Medium | Effort: Low**

When Pexels fails to find a relevant image, Shotstack can generate one from a text prompt:
```python
{
    "asset": {
        "type": "text-to-image",
        "prompt": "Aerial view of Mumbai Marine Drive at sunset, cinematic photography",
        "width": 1080,
        "height": 1920,
    },
    "start": 5.0,
    "length": 5.0,
    "effect": "zoomIn",
}
```

This eliminates the "no image found" failure mode entirely. The storyboard already generates visual descriptions — feed them directly as prompts.

**Caveats:**
- AI-generated images may look inconsistent with real photos
- Quality varies — best as a fallback, not primary source
- May add rendering time

---

### 13. ⏱️ Shorter CTA end card
**Impact: Low | Effort: Low**

The current 4-second end card is long relative to a 30-second reel (13% of total time). Most viewers drop off during static end cards.

**Recommendation**: 
- Reduce to 2-2.5 seconds
- Add `slideUp` transition to social handles (staggered animation)
- Use tweening to animate the logo and text entrance

```python
CTA_DURATION = 2.5  # Down from 4.0

# Animate social handles in sequence
for i, (platform, handle) in enumerate(SOCIAL_HANDLES.items()):
    clip["offset"] = {
        "y": [{"from": -0.1, "to": 0, "start": i * 0.15, "length": 0.3,
               "interpolation": "bezier", "easing": "easeOutBack"}]
    }
```

---

### 14. 🔀 Luma matte transitions
**Impact: Low | Effort: Medium**

Shotstack supports luma matte transitions — grayscale video masks that create cinematic reveals. This could be used for:
- Ink-bleed reveals between scenes
- Circle-wipe transitions (like classic news broadcasts)
- Custom branded transition animations

**Implementation**: Requires creating or sourcing MP4 luma matte videos and uploading to Supabase storage. Low priority but adds polish.

---

### 15. 📊 Use Shotstack merge templates for consistency
**Impact: Low | Effort: Medium**

Instead of building the full JSON programmatically each time, save a reusable template to Shotstack with merge fields:

```python
# Template with placeholders
{
    "timeline": {
        "tracks": [...],
        # Use merge fields: {{HEADLINE}}, {{HOOK_LINE1}}, {{VOICE_URL}}, etc.
    }
}

# Render with just the data
{
    "id": "template-uuid",
    "merge": [
        {"find": "HEADLINE", "replace": "Modi announces new policy..."},
        {"find": "HOOK_LINE1", "replace": "GAME CHANGER"},
        {"find": "VOICE_URL", "replace": "https://...voice.mp3"},
    ]
}
```

Benefits: Faster iteration on design (edit template in Shotstack Studio), smaller API payloads, easier A/B testing of visual styles.

---

## Competitive Analysis {#competitive-analysis}

### How top Indian news accounts structure their reels

**WION (@waborionews, 4M+ followers):**
- Portrait 9:16, always
- Bold red/white text overlays
- Anchor-on-camera with B-roll cutaways
- 30-45 second typical length
- Strong hook: "THIS changes everything for India"
- Lower third with topic label

**Firstpost (@firstpost, 3M+ followers):**
- Mix of portrait and square (portrait performs better)
- Heavy use of data graphics and maps
- Quick-cut editing (2-3 second scenes)
- Text-heavy with animations
- Often repurposes TV segments

**The Print (@theprintindia, 2M+ followers):**
- Almost entirely portrait
- Simple text-on-image format
- Clean typography, minimal effects
- Short (15-25 seconds)
- High engagement through controversial takes in captions

**Al Jazeera (@aljazeera, 12M+ followers):**
- Professional B-roll with Ken Burns (similar to current pipeline)
- Lower thirds with their brand blue
- Word-by-word captions in white with black stroke
- Consistent 30-40 second length
- Strong CTAs: "Follow for more updates"

### Key takeaways for The Videshi:
1. **Portrait is non-negotiable** — every competitor uses 9:16
2. **Bold text hooks are standard** — The Videshi's hook frame approach is correct
3. **Data visualizations and maps** would differentiate from basic B-roll slideshows
4. **Shorter is trending** — 20-30 seconds seems to be the new standard for news
5. **Caption placement**: Bottom-center with stroke is the universal standard (current approach is correct)
6. **Color-coded categories**: Many outlets use category-specific color accents

---

## Cost Analysis {#cost-analysis}

### Current costs per reel (estimated)
| Component | Service | Cost |
|-----------|---------|------|
| Script generation | GPT-4o | ~$0.02-0.05 |
| TTS voice | HeyGen v2 | Included in plan |
| Whisper timestamps | OpenAI Whisper | ~$0.006/min |
| Image matching | GPT-4o-mini | ~$0.01 |
| QA gate | GPT-4o vision | ~$0.05 |
| Shotstack render | Production | ~$0.50-1.00 |
| **Total per reel** | | **~$0.60-1.15** |

### Proposed costs with enhancements
| Component | Service | Cost |
|-----------|---------|------|
| Script generation | GPT-4o | ~$0.02-0.05 |
| **TTS voice** | **ElevenLabs Creator** | **~$0.18/reel** ($22/mo ÷ ~120 reels) |
| Whisper timestamps | OpenAI Whisper | ~$0.006/min |
| Image matching | GPT-4o-mini | ~$0.01 |
| QA gate | GPT-4o vision | ~$0.05 |
| Shotstack render (×2 for dual length) | Production | ~$1.00-2.00 |
| Thumbnail render | Shotstack | ~$0.10 |
| **Total per reel** | | **~$1.35-2.35** |

### With budget alternative (Voxtral TTS)
| Component | Change | Cost |
|-----------|--------|------|
| TTS voice | Voxtral API | ~$0.01/reel |
| **Total per reel** | | **~$0.70-1.25** |

---

## Implementation Priority Roadmap

### Phase 1 — Quick wins (1-2 days)
- [ ] **Confirm portrait 9:16 output** — verify and fix if needed (#1)
- [ ] **Add poster/thumbnail to output config** (#5)
- [ ] **Diversify transitions** — category-aware rotation (#6)
- [ ] **Vary caption animation style** by category (#7)
- [ ] **Shorten CTA card** from 4s → 2.5s (#13)

### Phase 2 — Voice upgrade (3-5 days)
- [ ] **Set up ElevenLabs** (or Voxtral) TTS integration (#2)
- [ ] **A/B test voice quality** — render same script with HeyGen vs new TTS
- [ ] **Add emotion tags** for breaking/serious/entertainment scripts

### Phase 3 — Visual polish (1 week)
- [ ] **Animated hook frame** with tweening + transitions (#3)
- [ ] **Add sound effects** layer (news stinger, whoosh) (#8 sound effects)
- [ ] **Expand music library** to 3-4 tracks per category (#8)
- [ ] **Test image-to-video** for scene 1 animated B-roll (#10)

### Phase 4 — Platform optimization (1 week)
- [ ] **Dual-length rendering** — short (25s) + extended (50s) per article (#4)
- [ ] **Webhook callbacks** to replace polling (#9)
- [ ] **Register separate reels** in prebuilt_reels with platform tags

### Phase 5 — Architecture improvements (ongoing)
- [ ] **Migrate HtmlAsset → TextAsset** where possible (#11)
- [ ] **Shotstack templates** with merge fields (#15)
- [ ] **Text-to-image fallback** for missing B-roll (#12)
- [ ] **Luma matte transitions** for premium feel (#14)

---

## Reference Links

### Shotstack API Documentation
- API Reference: https://shotstack.io/docs/api/
- Core Concepts: https://shotstack.io/docs/guide/getting-started/core-concepts/
- Animations/Tweening: https://shotstack.io/docs/guide/architecting-an-application/animations/
- Templates: https://shotstack.io/docs/guide/architecting-an-application/templates/
- Transitions blog: https://shotstack.io/learn/new-slide-carousel-and-zoom-transitions/
- Luma Mattes: https://shotstack.io/learn/introducing-luma-mattes-thumbnails-and-render-scaling/
- Templates showcase: https://shotstack.io/templates/

### TTS Providers
- ElevenLabs: https://elevenlabs.io/ — pricing at https://elevenlabs.io/pricing
- Mistral Voxtral TTS: https://huggingface.co/mistralai/Voxtral-TTS-v1 — $0.016/1k chars
- Resemble AI Chatterbox: https://github.com/resemble-ai/chatterbox — MIT, free
- Fish Audio S2: https://fish.audio/ — top-ranked on ELO benchmarks
- Sarvam AI Bulbul v3: https://www.sarvam.ai/ — Indian languages specialist, ₹15-30/10k chars

### Platform Best Practices
- Instagram Reels: 1080×1920, 9:16, 15-30s optimal, completion rate is key signal
- YouTube Shorts: 1080×1920, 9:16, 40-60s optimal, total watch time is key signal
- TikTok: 1080×1920, 9:16, 31-60s sweet spot for engagement
- IG algorithm 2026: DM shares > saves > comments > likes (signal hierarchy)
- YT Shorts: 40s+ videos get 33% higher engagement than shorter clips

### Shotstack Available Transitions (full list)
`fade` | `reveal` | `wipeLeft` | `wipeRight` | `slideLeft` | `slideRight` | `slideUp` | `slideDown` | `carouselLeft` | `carouselRight` | `carouselUp` | `carouselDown` | `shuffleTopRight` | `shuffleRightTop` | `shuffleRightBottom` | `shuffleBottomRight` | `shuffleBottomLeft` | `shuffleLeftBottom` | `shuffleLeftTop` | `shuffleTopLeft` | `zoom`

Each also has `Slow` and `Fast` variants (e.g., `fadeSlow`, `zoomFast`).

### Shotstack Available Caption Animation Styles
`karaoke` | `highlight` | `pop` | `fade` | `slide` | `bounce` | `typewriter` | `none`

### Shotstack Available Motion Effects
`zoomIn` | `zoomOut` | `slideLeft` | `slideRight` | `slideUp` | `slideDown`

### Shotstack Available Filters
`greyscale` | `boost` | `contrast` | `darken` | `lighten` | `muted` | `negative` | `invert`

### Shotstack Tweening Easings
`ease` | `easeIn` | `easeOut` | `easeInOut` | `easeInQuad` | `easeOutQuad` | `easeInOutQuad` | `easeInCubic` | `easeOutCubic` | `easeInOutCubic` | `easeInQuart` | `easeOutQuart` | `easeInOutQuart` | `easeInQuint` | `easeOutQuint` | `easeInOutQuint` | `easeInSine` | `easeOutSine` | `easeInOutSine` | `easeInExpo` | `easeOutExpo` | `easeInOutExpo` | `easeInCirc` | `easeOutCirc` | `easeInOutCirc` | `easeInBack` | `easeOutBack` | `easeInOutBack`
