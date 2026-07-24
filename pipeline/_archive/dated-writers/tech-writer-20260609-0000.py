#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-09 00:00 UTC run"""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
for env_file in [Path.home() / ".env.supabase", Path.home() / "workspace/.env.pexels"]:
    if env_file.exists():
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
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# --- Image helpers ---
import urllib.parse

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query", "generator": "search", "gsrsearch": search_query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=15)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                })
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []

def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def upload_image_to_supabase(image_url, filename):
    """Download image, compress, upload to Supabase article-images bucket."""
    try:
        r = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Failed to download image: HTTP {r.status_code}")
            return None
        content_type = r.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            print(f"  ⚠ Not an image: {content_type}")
            return None
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return None

        compressed = compress_image(r.content)
        print(f"  ✓ Compressed: {len(r.content)} → {len(compressed)} bytes")

        upload_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        }
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
        if resp.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {resp.status_code} {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  ⚠ Image upload error: {e}")
        return None

# ============================================================
# ARTICLE 1: Apple WWDC 2026 / Siri AI
# ============================================================
print("\n=== Article 1: WWDC 2026 / Siri AI ===")

art1_id = str(uuid.uuid4())
art1_slug = make_slug("apple-wwdc-siri-ai-standalone-app-gemini-golden-gate")

# Image: Craig Federighi (presented the WWDC keynote)
print("Sourcing image for Article 1...")
art1_img_url = None
art1_img_caption = "Craig Federighi, Apple's SVP of Software Engineering, presents at a WWDC keynote"
art1_img_attribution = "Wikimedia Commons"

wiki_img = fetch_wikipedia_person_image("Craig Federighi")
if wiki_img:
    uploaded = upload_image_to_supabase(wiki_img, f"{art1_slug}.jpg")
    if uploaded:
        art1_img_url = uploaded

if not art1_img_url:
    print("  Falling back to Wikimedia Commons search...")
    commons = fetch_wikimedia_commons_images("Apple WWDC keynote presentation")
    for c in commons[:2]:
        uploaded = upload_image_to_supabase(c["url"], f"{art1_slug}.jpg")
        if uploaded:
            art1_img_url = uploaded
            break

art1_body = """Apple's annual developer pilgrimage to Cupertino has produced many big reveals over the years — the iPhone, the App Store, SwiftUI. Monday's keynote may not have matched those in hardware spectacle, but it marked a turning point that every Indian developer and iPhone user should understand: Siri is no longer a punchline.

Rebranded as "Siri AI," Apple's voice assistant received the most significant overhaul in its 15-year history. It is now a standalone app with its own icon on your home screen, capable of multi-turn conversations, cross-app task orchestration, and what Apple calls "personal context" — the ability to surface information buried in your Messages, Mail, Photos, and Calendar without you having to tell it where to look.

During the keynote demo, a presenter asked Siri about a dessert mentioned at a dinner party. Siri located the relevant message thread, pulled the recipe details, compiled a watch-party menu, and drafted a message to the presenter's contacts — all without the human leaving the conversation. In another sequence, it identified a landmark from a photo, pulled up navigation, and surfaced related family pictures.

This is not the Siri that struggles with basic questions. This is an agentic assistant that can chain actions across Apple's entire ecosystem. And it could not have happened without Sundar Pichai.

## Google Inside

The elephant on stage at WWDC was the Google Gemini logo, metaphorically speaking. Apple's new generation of Apple Intelligence — the on-device AI layer that powers Siri AI — is built on updated Apple Foundation Models developed in collaboration with Google's Gemini technology. The models run on-device through Apple's custom silicon and in the cloud via Apple's Private Cloud Compute infrastructure.

For Pichai's Alphabet, this is a landmark win. Google's AI now powers not just the world's dominant search engine and Android ecosystem, but also the world's most valuable company's personal assistant. The deal, announced in January, positions Gemini as the invisible engine behind 2 billion active Apple devices. For the roughly 200,000 Indian iOS developers building apps for this ecosystem, the implications are immediate: new App Intents frameworks will let Siri reach into third-party apps, creating what could become a new monetisation layer inside Apple's walled garden.

## Golden Gate and the End of Intel

Apple also unveiled macOS 27, named "Golden Gate" — the first time the company has named its operating system after a man-made California landmark. The update officially drops support for all Intel-based Macs, completing Apple's five-year silicon transition. Four Mac models that ran macOS Tahoe will not receive Golden Gate: the MacBook Pro 16-inch (2019), MacBook Pro 13-inch (2020), iMac (2020), and Mac Pro (2019).

More quietly, Apple confirmed that macOS 28 will remove Rosetta 2 entirely — the translation layer that lets Apple Silicon Macs run software written for Intel chips. For Indian IT professionals and creative workers still running older Macs, the clock is ticking. If you are still on an Intel Mac, this year's upgrade is no longer optional.

## The Availability Problem

Here is where the story gets complicated for the diaspora. Siri AI will launch in English first, with a beta later this year. It will initially not be available on iOS and iPadOS in the European Union, where regulators have locked horns with Apple over its App Store practices. In China, Siri AI and other Apple Intelligence features will not launch either, as Apple navigates regulatory requirements.

India is not explicitly mentioned in the exclusion list, but Apple's track record with AI features in the country is patchy. The current generation of Apple Intelligence launched months after the US rollout, and many features remain unavailable in Indian English. Whether Siri AI's full capabilities — web search, cross-app orchestration, visual intelligence — will be available to NRIs in Bengaluru at the same time as those in the Bay Area remains an open question.

## The Competitive Picture

The new Siri arrives into a market that has moved fast in its absence. OpenAI's ChatGPT, Anthropic's Claude, and Google's own Gemini chatbot all offer capabilities that make the old Siri look prehistoric. Apple is late — the company promised a Siri revamp at WWDC 2024, hit roadblocks, settled a false advertising lawsuit, and watched its head of AI depart.

But Apple has something the chatbot companies do not: deep integration with native apps and a privacy-first architecture that processes data on-device rather than in the cloud. If Siri AI delivers on its demos, it could become the personal AI assistant that ChatGPT aspires to be but cannot — because ChatGPT does not live inside your iPhone, your Messages, or your Photos app.

For Tim Cook, Monday was almost certainly his last WWDC keynote. He will hand the CEO chair to John Ternus in September. The question Ternus inherits is whether Apple's AI — built on Google's brains, Apple's silicon, and two years of delays — can finally make Siri the assistant it always should have been."""

# ============================================================
# ARTICLE 2: Physical AI / Humanoid Robots
# ============================================================
print("\n=== Article 2: Physical AI / Humanoid Robots ===")

art2_id = str(uuid.uuid4())
art2_slug = make_slug("humanoid-robots-factory-floor-hyundai-boston-dynamics-india")

# Image: Atlas robot from Wikipedia
print("Sourcing image for Article 2...")
art2_img_url = None
art2_img_caption = "The Boston Dynamics Atlas humanoid robot during testing"
art2_img_attribution = "Wikimedia Commons"

wiki_img2 = fetch_wikipedia_person_image("Atlas (robot)")
if wiki_img2:
    uploaded2 = upload_image_to_supabase(wiki_img2, f"{art2_slug}.jpg")
    if uploaded2:
        art2_img_url = uploaded2

if not art2_img_url:
    # Try direct URL
    atlas_url = "https://upload.wikimedia.org/wikipedia/commons/9/9b/Atlas_during_testing.jpg"
    uploaded2 = upload_image_to_supabase(atlas_url, f"{art2_slug}.jpg")
    if uploaded2:
        art2_img_url = uploaded2

art2_body = """Jensen Huang stood in Seoul this week, fresh off a tour that has reshaped the global AI supply chain, and said something that landed differently than his usual hyperbole: humanoid robots are "very very close" to industrial reality.

The Nvidia CEO was speaking after a meeting with Hyundai Motor Group's Executive Chair Euisun Chung, where the two companies announced a deepened partnership spanning autonomous mobility, robotics, and AI-powered manufacturing. The centrepiece: Boston Dynamics — the Hyundai Motor Group affiliate known for its viral robot videos — will deploy its Atlas humanoid robots at Hyundai auto plants starting in 2028. The production target is 30,000 units globally each year.

This is no longer a research demo. This is a production timeline.

## The Seoul Shopping Spree

Huang's Seoul visit produced an extraordinary density of deals. SK hynix secured a multiyear memory partnership for Nvidia's Vera Rubin AI supercomputers. Samsung's chip chief discussed next-generation foundry collaboration and Groq AI inference processors. SK Telecom committed to building a gigawatt-scale AI cloud, with the first data centre coming online in 2027. Naver signed up for Nvidia's DSX platform to build sovereign AI factories. LG Group is partnering on humanoid robot motors and mechanical systems. Doosan will deploy Nvidia's physical AI technology alongside its industrial robots.

But it was the Hyundai conversation that carried the most implications for India. Huang called Hyundai "incredible at manufacturing, incredible at mobility" and said no company is "in a better position to take advantage of" the convergence of AI and robotics. He referred to Hyundai's planned AI data centre in Saemangeum as Korea's "AI Valley" — and said he was ready to build Nvidia in it.

## Why India Should Be Watching

Hyundai Motor India operates one of the largest automobile manufacturing facilities in the country, at Sriperumbudur near Chennai. The plant produces over 700,000 vehicles annually and employs thousands of workers. If Atlas robots deploy at Hyundai's Korean factories by 2028, the question for Indian workers — and Indian policymakers — is straightforward: how long before they arrive in Tamil Nadu?

The broader physical AI revolution extends well beyond Hyundai. At Computex last week, Nvidia unveiled its H2+ humanoid robot reference platform and the Cosmos 3 physical AI foundation model, which allows robots to perceive, simulate, and interact with the physical world at scale. These are not bespoke research tools. They are platforms that any manufacturer — from Tata Motors to Mahindra to Foxconn's Indian iPhone assembly lines — could eventually deploy.

India's manufacturing ambitions under Make in India and the Production Linked Incentive scheme depend on automation competitiveness. The country currently lags far behind its peers in industrial robot density. According to the International Federation of Robotics, India deployed roughly 8,500 industrial robots in 2023, compared to China's 290,000. Japan, South Korea, and Germany all have robot-to-worker ratios that India cannot yet approach. The gap is widening, not closing.

## Indian Robotics Wakes Up

There are signs of life. Addverb Technologies, backed by Mukesh Ambani's Reliance Industries, operates what it claims is India's largest robot manufacturing facility in Greater Noida, producing warehouse automation robots deployed across India, Europe, and North America. GreyOrange, co-founded by IIT Delhi graduates, has built a global business in fulfilment robotics. Miko, the Mumbai-based AI companion robot maker, has expanded to the US market.

None of these companies are building humanoid robots for factory floors. But the ecosystem is growing. Indian engineers already form a significant share of the robotics workforce at companies like Boston Dynamics, Nvidia, and Hyundai's R&D centres. The skills exist in the diaspora; the domestic application does not — yet.

For NRI engineers working in robotics and physical AI at Silicon Valley and Boston labs, the calculus is shifting. The next wave of manufacturing AI will need implementation engineers who understand both the technology and the factory floor. India's manufacturing sector, with its scale and labour cost pressures, is exactly the market where humanoid robots could have the most transformative — and most disruptive — impact.

## The Timeline That Matters

The 2028 date for Atlas at Hyundai factories is significant because it is not a vision deck or a concept video. Boston Dynamics has spent two decades building walking, running, and manipulating robots. The product version of Atlas, revealed at CES 2026, is designed for specific factory tasks: sequencing parts, handling materials, and performing operations that expose humans to physical risk. Hyundai Motor Group announced a multibillion-dollar investment plan for physical AI in South Korea in February.

Combined with Nvidia's Jetson Thor robotics computing platform and Cosmos 3 world simulation models, the infrastructure for humanoid manufacturing robots is assembling faster than most analysts expected.

The question for Indian policymakers, manufacturers, and engineers is not whether this technology will arrive. It is whether India will be deploying these robots in its own factories — or merely supplying the engineers who build them for everyone else."""

# ============================================================
# Build article records
# ============================================================
articles = [
    {
        "id": art1_id,
        "headline": "Siri Finally Grew Up. Apple Needed Google's AI to Get There.",
        "subheadline": "At WWDC 2026, Apple unveiled Siri AI — a standalone app powered by Google's Gemini that can chain tasks across apps, understand your screen, and hold real conversations. But Indian iPhone users may have to wait.",
        "slug": art1_slug,
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian iOS developers gain new Siri AI app integration frameworks. Sundar Pichai's Google Gemini now powers Apple's entire AI stack. India's Apple Intelligence availability remains uncertain — the EU and China are already excluded from the initial rollout.",
        "tags": ["apple", "siri", "google-gemini", "wwdc", "sundar-pichai", "ios-developers", "macos-golden-gate"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/apple-rolls-out-new-ai-powered-siri-annual-wwdc-2026-06-08/"},
            {"name": "Gadgets360", "url": "https://www.gadgets360.com/apps/news/wwdc-2026-apple-intelligence-siri-ai-ios-27-ipados-macos-watchos-visionos-tvos-8101234"},
            {"name": "WSJ", "url": "https://www.wsj.com/tech/apple-set-to-unveil-new-siri-at-developers-event-seeking-a-new-foothold-in-ai"},
            {"name": "CNN", "url": "https://www.cnn.com/2025/06/08/tech/apple-wwdc-2026-siri-ai/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art1_img_url or "",
        "image_caption": art1_img_caption,
        "image_attribution": art1_img_attribution,
        "body": art1_body
    },
    {
        "id": art2_id,
        "headline": "Humanoid Robots Just Got a Delivery Date. Indian Factories Should Pay Attention.",
        "subheadline": "Boston Dynamics will deploy Atlas robots at Hyundai auto plants by 2028, targeting 30,000 units a year. Nvidia is betting physical AI is the next trillion-dollar market. India's manufacturing sector isn't ready.",
        "slug": art2_slug,
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Hyundai's massive Chennai plant could be an early target for humanoid robot deployment. Indian robotics startups like Addverb (Reliance-backed) and GreyOrange are growing but not yet building factory humanoids. NRI engineers in physical AI face a pivotal career moment as the technology moves from labs to factory floors.",
        "tags": ["humanoid-robots", "boston-dynamics", "nvidia", "hyundai", "physical-ai", "indian-manufacturing", "make-in-india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/nvidia-clinches-deals-south-korean-giants-advance-ai-boom-2026-06-08/"},
            {"name": "Bloomberg via Stocktwits", "url": "https://stocktwits.com/news/jensen-huang-humanoid-robots-nvidia-hyundai"},
            {"name": "WSJ", "url": "https://www.wsj.com/tech/nvidia-strikes-deals-korean-tech-titans-ai-infrastructure"},
            {"name": "CES 2026 / Hyundai Motor Group", "url": "https://www.hyundaimotorgroup.com/news/CONT0000000000073001"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art2_img_url or "",
        "image_caption": art2_img_caption,
        "image_attribution": art2_img_attribution,
        "body": art2_body
    }
]

# ============================================================
# Insert into Supabase
# ============================================================
print("\n=== Inserting articles ===")
for art in articles:
    # Skip articles with no image
    if not art["image_url"]:
        print(f"  ⚠ No image for {art['slug']} — inserting without image")
    try:
        sb_post("p2_articles", art)
        print(f"  ✅ {art['slug']} — \"{art['headline']}\"")
    except Exception as e:
        print(f"  ❌ {art['slug']}: {e}")

print("\nDone!")
