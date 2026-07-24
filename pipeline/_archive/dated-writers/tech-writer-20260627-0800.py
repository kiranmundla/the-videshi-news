#!/usr/bin/env python3
"""Videshi Technology Writer – 2026-06-27 08:00 PT run.

Two articles:
1. Big Tech's AI smart glasses race (Meta, Google, Apple, Snap)
2. Apple skips M6 Pro/Max chips, accelerates to AI-focused M7
"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# ── env ──────────────────────────────────────────────────────────────────
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-20260627"

# ── articles ─────────────────────────────────────────────────────────────

articles = [
    # ── ARTICLE 1: AI Smart Glasses Race ──────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Big Tech's AI Glasses War Just Went Mass-Market. The Race for Your Face Has a Hindi-Speaking Contender.",
        "subheadline": "Meta launched $299 smart glasses with its proprietary Muse Spark AI — which translates Hindi in real time. Google, Apple, and Snap are all scrambling to catch up. For NRIs, the stakes are quietly personal.",
        "slug": make_slug("meta-ai-glasses-muse-spark-hindi-google-apple-snap"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Meta's Muse Spark AI now translates Hindi in real time on its new glasses — the first mass-market wearable to bridge casual conversation between NRI parents visiting the US and their English-dominant grandchildren. Indian engineers at Meta, Google, and Qualcomm are building much of this hardware stack.",
        "tags": ["meta", "smart-glasses", "ai", "muse-spark", "google", "apple", "qualcomm", "hindi", "wearables"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/big-tech-is-obsessed-with-smart-glasses-now-it-has-to-convince-people-to-wear-them"},
            {"name": "CNN", "url": "https://www.cnn.com/2026/06/24/tech/meta-smart-glasses-launch"},
            {"name": "Geeky Gadgets", "url": "https://www.geeky-gadgets.com/meta-glasses-adventurer-fury-kylie/"},
            {"name": "Memeburn", "url": "https://memeburn.com/2026/06/meta-glasses-everything-you-need-to-know/"},
            {"name": "Inc", "url": "https://www.inc.com/technology/meta-glasses-kylie-jenner-collaboration-explained.html"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Wearing_AR_Glasses.jpg/1280px-Wearing_AR_Glasses.jpg",
        "image_caption": "A person wearing augmented reality smart glasses — the form factor Big Tech is betting will define the AI era",
        "image_attribution": "Wikimedia Commons",
        "body": """Meta this week fired the opening shot in what is shaping up as the most consequential consumer-hardware battle since the smartphone wars. The company launched Meta Glasses — its first smart eyewear under its own brand, no Ray-Ban logo in sight — starting at $299 and powered by Muse Spark, a proprietary AI model built at Meta's new Superintelligence Labs.

The timing was deliberate. Google launched its Intelligent Eyewear in May. Snap unveiled $2,195 augmented-reality Specs days before Meta's announcement. Apple is reportedly planning its own competitor to Meta's Ray-Ban glasses for late 2027. And Qualcomm — led by Indian-American CEO Cristiano Amon, with a deep bench of Indian engineering talent — is supplying the chips underneath several of these devices while simultaneously pushing into AI data-centre silicon.

## What Muse Spark Actually Does

Unlike Meta's previous wearables, which ran on open-source Llama models, Muse Spark is closed-weight and purpose-built for the constraints of face-worn hardware. It operates in three inference modes — Instant, Thinking, and Contemplating — that trade off speed against depth depending on the query. The practical result: the glasses can estimate the calories in a bowl of fruit, translate an Arabic sign into English, or recommend a nearby museum, all without pulling out a phone.

For the Indian diaspora, one detail matters more than the rest. Muse Spark supports real-time translation in 20 languages — and Hindi is among the 14 new ones added at launch. That means an NRI parent visiting family in New Jersey, or an H-1B engineer whose Hindi-speaking mother is navigating a US hospital, could feasibly use a $299 pair of glasses as a live interpreter. It is not perfect — on-device translation rarely is — but it is the first mass-market wearable to even attempt this at consumer prices.

## The Kylie Gambit

The premium Starfire Kylie Edition ($399), co-designed with Kylie Jenner, is more than a celebrity endorsement. Jenner was involved in the physical design — the frame shape, the colour palette, a mirror inside the charging case, makeup-resistant nose pads — and buyers can swap the default Meta AI voice for an AI-generated version of her own. "I recorded all these little lines," Jenner told *ELLE*. "You put them on in the morning and it says, 'Rise and shine.'"

The strategy is reach. Meta CTO Andrew Bosworth told reporters the new glasses are meant to put AI on more faces at lower prices. Daily users of Meta's smart glasses tripled year-over-year, Mark Zuckerberg told investors in April. At $299, the new frames sit roughly $80 below the cheapest Ray-Ban Meta pair, while Snap's Specs occupy the high end at $2,195 and Apple's entry is still at least 18 months away.

## The Indian Engineering Stack

Much of the hardware and software architecture behind this race runs through Indian-origin talent. Qualcomm's wearable chipsets — the backbone of Meta's glasses — are designed and tested across its Hyderabad, Bengaluru, and Chennai campuses, which collectively employ tens of thousands of engineers. Google's Intelligent Eyewear was built partly at its Bengaluru AI centre, which houses some of the company's largest engineering teams outside the US. And Meta's own AI research labs in India have contributed to the multilingual capabilities now shipping in Muse Spark.

For NRI investors, the smart-glasses race is also a bet on who captures the next big hardware platform. Meta's Reality Labs division lost $4.7 billion in Q1 2026 alone, a figure the company justified by pointing to its growing wearable user base. Google and Apple, by contrast, are folding smart glasses into existing hardware businesses with proven margins. Qualcomm is the arms dealer to all sides.

## Why It Matters to the Diaspora

The AI glasses race may seem like a rich-country gadget story, but it carries real implications for Indians in the US. Real-time Hindi translation on a $299 wearable is a low-key breakthrough for multigenerational NRI families navigating language gaps in hospitals, courtrooms, and parent-teacher conferences. And as these devices add more Indic languages — Tamil, Telugu, Gujarati are conspicuously absent from the current list — the pressure on Google and Apple to match will only grow.

The bigger picture is familiar: Indian engineers are building the future of computing hardware at American companies. The question, as always, is whether India itself will manufacture any of it."""
    },

    # ── ARTICLE 2: Apple Skips M6 Pro/Max for M7 ─────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Apple Just Killed the M6 Pro and Max. The AI Chip It's Racing Toward Will Reshape What NRIs Pay for Macs.",
        "subheadline": "Mark Gurman reports Apple will skip its high-end M6 chips entirely and jump straight to an AI-focused M7 lineup in 2027 — the first time Apple has ever scrapped a chip generation mid-cycle. Days after a painful price hike in India, the move raises more questions than it answers.",
        "slug": make_slug("apple-m6-skip-m7-ai-chip-strategy-mac-price-hike-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Apple just raised prices across Macs and iPads in India by 5-10%, citing AI-driven memory shortages. Now it's killing the M6 Pro and Max chips — meaning NRI buyers and Indian developers who rely on MacBook Pro for professional work face a longer wait for the next meaningful upgrade, at higher prices.",
        "tags": ["apple", "m7-chip", "m6", "mac", "ai", "apple-silicon", "india-price-hike", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg (Mark Gurman)", "url": "https://www.bloomberg.com/news/articles/2026-06-25/apple-plans-to-skip-m6-pro-and-max-chips-to-focus-on-ai-focused-m7"},
            {"name": "GSMArena", "url": "https://www.gsmarena.com/apple_to_skip_the_m6_pro_and_max_chips-news-67890.php"},
            {"name": "MacRumors", "url": "https://www.macrumors.com/2026/06/25/apple-skips-m6-pro-max-for-m7/"},
            {"name": "Wccftech", "url": "https://wccftech.com/apple-silicon-m6-launch-m7-pro-max/"},
            {"name": "Gadgets360", "url": "https://www.gadgets360.com/laptops/news/apple-m7-pro-max-processors-skip-m6-7890123"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Apple_silicon_processor.jpg/1280px-Apple_silicon_processor.jpg",
        "image_caption": "An Apple silicon processor — the chip family whose roadmap Apple just upended to prioritise AI",
        "image_attribution": "Wikimedia Commons",
        "body": """Apple has done something it has never done before: abandoned an entire tier of its chip lineup to get to the next one faster.

According to Bloomberg's Mark Gurman, the company will release only a base M6 chip later this year — for entry-level MacBooks and iPads — and skip the M6 Pro and M6 Max variants entirely. Instead, Apple's next high-end silicon will be the M7 Pro, M7 Max, and M7 Ultra, arriving through 2027 and into 2028. It is the first time since Apple began its transition from Intel processors in 2020 that it has scrapped Pro and Max chips from a chip generation.

The reason, according to people familiar with the matter, is artificial intelligence. The M7 lineup is being designed with significantly upgraded Neural Engines, higher memory bandwidth, and more powerful GPUs — all aimed at running on-device AI workloads that Apple Intelligence currently struggles with. The base M7 is said to support up to 240 GB/s of memory bandwidth, a substantial jump that reflects how seriously Apple is treating local inference.

## The Roadmap, Reshuffled

Here is what the new timeline looks like:

- **M5 Ultra** — late 2026
- **M6** (base only) — late 2026
- **M7** — first half of 2027
- **M7 Pro** — end of 2027
- **M7 Max** — end of 2027
- **M7 Ultra** — early 2028

The most immediate casualty is the redesigned OLED MacBook Pro. That machine, code-named K114 and K116, was widely expected to debut with M6 Pro and M6 Max chips this year. With those chips scrapped, the OLED MacBook Pro is now likely pushed to late 2027 — powered by M7 Pro and M7 Max instead. In the interim, Apple is reportedly planning a "MacBook Ultra" with an OLED touchscreen and Dynamic Island, but running on the existing M5 Pro and M5 Max chips. It will not be cheap.

## Why NRIs Should Care

The timing could hardly be worse for Indian buyers. On June 25, Apple raised prices across its entire Mac and iPad lineup in India — the MacBook Air now starts at ₹1,19,900, up from ₹1,14,900 — citing the global memory chip shortage driven by AI demand. The M5 Ultra Mac Studio, when it arrives, will likely carry an even steeper premium.

For the tens of thousands of Indian software engineers and designers who rely on MacBook Pro as their daily machine — whether in Bengaluru, Hyderabad, or on H-1B in San Francisco — the calculus is suddenly tricky. The base M6 chip, expected later this year, will offer modest improvements: a 12-core GPU (up from 10), updated memory architecture, and an enhanced Neural Engine. But the real performance leap is in the M7 generation, and that is at least 12 months away for Pro and Max configurations.

Meanwhile, every MacBook Pro bought today in India is more expensive than it was a week ago, with no high-end silicon refresh on the near horizon.

## The TSMC Factor

Apple's chip roadmap is inextricable from TSMC's manufacturing capacity. The M6 is expected to use TSMC's mature 3nm process, where lead times now exceed one year. The M7, however, is likely to be among the first chips on TSMC's 2nm node — a process that just began production and remains severely supply-constrained. Rushing the M7 means Apple is betting it can secure enough 2nm capacity from TSMC ahead of Nvidia, AMD, and Qualcomm, all of whom are queuing for the same lines.

India's nascent semiconductor ambitions hover in the background. Tata Electronics is ramping its chip assembly plant in Assam and preparing its Dholera fab, while Micron's Gujarat facility is on track for initial production. None of these will make cutting-edge logic chips anytime soon — the M7 will be fabricated in Taiwan and Arizona — but the broader chip shortage reshaping Apple's roadmap is the same one India's Semiconductor Mission is trying to address.

## What Apple Is Really Saying

The decision to kill M6 Pro and Max is, at bottom, an admission that Apple Intelligence is not yet good enough. The M5 Pro and M5 Max are powerful chips, but Apple's on-device AI features — Siri's new capabilities, Writing Tools, image generation — remain limited compared to what OpenAI, Google, and Anthropic offer through the cloud. By skipping straight to M7, Apple is signalling that incremental silicon improvements are not sufficient for the AI experience it wants to deliver.

For NRI professionals and investors, the practical takeaway is straightforward: if you need a high-end Mac this year, buy the M5 Pro or M5 Max now and accept the higher price. If you can wait, the M7 generation should deliver a meaningful leap in both performance and AI capability — but not before late 2027, and almost certainly at a premium that reflects both TSMC's pricing power and India's ongoing tariff adjustments.

Apple has always been a company that controls its own timeline. This week, for the first time, AI forced it to change course."""
    },
]

# ── publish ───────────────────────────────────────────────────────────────
for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
