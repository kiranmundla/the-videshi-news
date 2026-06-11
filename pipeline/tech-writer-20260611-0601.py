#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-11 06:01 UTC"""

import json, os, uuid, re, requests, io
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# ── Env ──
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

pexels_env = Path.home() / "workspace/.env.pexels"
for line in pexels_env.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
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

# ── Image helpers ──
def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def upload_to_supabase(img_bytes, filename):
    """Upload compressed image to Supabase storage bucket article-images."""
    compressed = compress_image(img_bytes)
    upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    h = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    r = requests.post(upload_url, headers=h, data=compressed, timeout=30)
    if r.status_code in (200, 201):
        public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
        size_kb = len(compressed) / 1024
        print(f"  ✓ Uploaded {filename} ({size_kb:.0f} KB)")
        return public_url
    else:
        print(f"  ✗ Upload failed ({r.status_code}): {r.text[:200]}")
        return None

def download_image(url):
    """Download image bytes from URL."""
    try:
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=15)
        if r.status_code == 200 and len(r.content) > 5000:
            ct = r.headers.get("Content-Type", "")
            if "image" in ct or url.endswith((".jpg", ".jpeg", ".png", ".webp")):
                print(f"  ✓ Downloaded {len(r.content)/1024:.0f} KB from {url[:80]}...")
                return r.content
        print(f"  ✗ Bad response: status={r.status_code}, len={len(r.content)}, ct={r.headers.get('Content-Type','')}")
    except Exception as e:
        print(f"  ✗ Download error: {e}")
    return None

def fetch_wikipedia_person_image(person_name):
    import urllib.parse
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

def source_image(article_slug, person_name=None, wiki_search=None, pexels_query=None):
    """Multi-source image sourcing. Returns (supabase_url, attribution) or (None, None)."""
    filename = f"{article_slug}.jpg"

    # Source 1: Wikipedia person image
    if person_name:
        url = fetch_wikipedia_person_image(person_name)
        if url:
            raw = download_image(url)
            if raw:
                sb_url = upload_to_supabase(raw, filename)
                if sb_url:
                    return sb_url, "Wikimedia Commons"

    # Source 2: Wikimedia Commons search
    if wiki_search:
        try:
            params = {
                "action": "query", "generator": "search",
                "gsrsearch": wiki_search, "gsrnamespace": "6", "gsrlimit": "5",
                "prop": "imageinfo", "iiprop": "url|size|mime",
                "iiurlwidth": "1200", "format": "json"
            }
            r = requests.get("https://commons.wikimedia.org/w/api.php",
                           params=params,
                           headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
                           timeout=15)
            if r.status_code == 200:
                pages = r.json().get("query", {}).get("pages", {})
                for pid, page in pages.items():
                    ii = page.get("imageinfo", [{}])[0]
                    mime = ii.get("mime", "")
                    if not mime.startswith("image/") or mime == "image/svg+xml":
                        continue
                    if ii.get("width", 0) < 300:
                        continue
                    img_url = ii.get("thumburl") or ii.get("url", "")
                    if img_url:
                        raw = download_image(img_url)
                        if raw:
                            sb_url = upload_to_supabase(raw, filename)
                            if sb_url:
                                return sb_url, "Wikimedia Commons"
        except Exception as e:
            print(f"  ⚠ Commons error: {e}")

    # Source 3: Pexels
    if pexels_query and PEXELS_KEY:
        try:
            import subprocess
            cmd = f'curl -sS "https://api.pexels.com/v1/search?query={requests.utils.quote(pexels_query)}&per_page=3" -H "Authorization: {PEXELS_KEY}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            for photo in data.get("photos", []):
                img_url = photo["src"]["large2x"]
                raw = download_image(img_url)
                if raw:
                    sb_url = upload_to_supabase(raw, filename)
                    if sb_url:
                        return sb_url, "Pexels"
        except Exception as e:
            print(f"  ⚠ Pexels error: {e}")

    return None, None


# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Meta-Reliance AI Data Center in Jamnagar
# ══════════════════════════════════════════════════════════════

art1_slug = make_slug("meta-reliance-jamnagar-ai-data-center-india-168mw")
art1_id = str(uuid.uuid4())

print(f"\n{'='*60}")
print(f"Article 1: Meta-Reliance Jamnagar Data Center")
print(f"{'='*60}")

art1_img, art1_attr = source_image(
    art1_slug,
    person_name="Mukesh Ambani",
    wiki_search="data center India server",
    pexels_query="data center server room AI infrastructure"
)

art1_body = """Mark Zuckerberg's Meta has a footprint problem. The company has committed $600 billion to AI data centres through 2028, with megaprojects sprawling across the American South and Midwest. But the fastest-growing slice of its user base — more than 500 million people across India — has been served from facilities thousands of miles away. That gap closed meaningfully this week.

Meta announced on Tuesday that it will lease capacity at a purpose-built, 168-megawatt AI-enabled data centre in Jamnagar, Gujarat, constructed by Mukesh Ambani's Reliance Industries. It is Meta's first custom-built AI facility in India, and the deal deepens a relationship that began with a $5.7 billion investment in Jio Platforms in 2020 and expanded last year into a joint venture building enterprise AI tools on Meta's open-source Llama models.

## Why Jamnagar, and Why Reliance

The choice of Jamnagar is no accident. The city is the nerve centre of Reliance's energy complex, which gives the data centre ready access to renewable power, desalinated seawater for cooling, and proximity to India's western submarine cable landing stations. Reliance will act as a single-window provider: design, construction, utility management, renewable energy supply, fibre connectivity, and fully managed operations.

Meta has separately contracted nearly 1 gigawatt of new clean energy in India — 837 MW of solar and wind from CleanMax and 88 MW from Fourth Partner Energy — to power its Indian operations. The company says it will cover the full cost of energy and water at the Jamnagar site.

## The Bigger Picture for India's Data Centre Boom

The deal arrives at an inflection point for Indian infrastructure. In February 2026, Reliance committed roughly $110 billion and Adani outlined $100 billion in investments to position India as a global AI hub. The central government has offered foreign companies a 20-year-plus tax break on using local data centres, and India's data centre market is projected to nearly double to $13.11 billion by 2034, according to IMARC Group.

Amazon, Microsoft, and Google have all expanded hyperscale capacity in India over the past year. Meta's move closes a conspicuous absence — the company has over half a billion Indian users across WhatsApp, Instagram, and Facebook, yet had no local AI compute until now.

## What NRIs Should Watch

For Indian Americans tracking Reliance stock (listed as RELIANCE on NSE), this deal signals that Ambani's digital infrastructure play is gaining serious Western anchor tenants. Jio Platforms is also approaching an IPO, and a deep partnership with Meta — now spanning telecom, AI software, and physical infrastructure — adds credibility to the listing narrative.

For Indian tech professionals in the Bay Area and beyond, the 168 MW facility will need skilled engineers to build and operate. Early data centre projects from AWS and Google in India have already triggered hiring surges for cloud architects, network engineers, and AI infrastructure specialists.

The timeline is aggressive: operational within two years, with options to scale. Whether Reliance can deliver on schedule while managing the complexity of a hyperscale AI facility will be the real test. Meta's willingness to bet on that outcome says something about where the AI infrastructure race is heading — and India's growing role in it."""

art1 = {
    "id": art1_id,
    "headline": "Meta's First India Data Centre Is a 168 MW AI Facility in Ambani's Backyard",
    "subheadline": "Mark Zuckerberg's company partners with Reliance Industries to build an AI-enabled data centre in Jamnagar, Gujarat — deepening a six-year alliance and closing a glaring infrastructure gap for 500 million Indian users.",
    "slug": art1_slug,
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Reliance-Meta partnership strengthens Jio IPO narrative for NRI investors; new AI data centre in Gujarat will drive hiring for Indian cloud and infrastructure engineers.",
    "tags": ["meta", "reliance", "data-center", "mukesh-ambani", "ai-infrastructure", "india-tech", "jamnagar"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/meta-deepens-partnership-ambanis-reliance-with-ai-data-centre-2026-06-10/"},
        {"name": "TechRepublic", "url": "https://www.techrepublic.com/article/meta-reliance-india-ai-data-center/"},
        {"name": "Inc42", "url": "https://inc42.com/buzz/meta-partners-reliance-to-set-up-first-data-centre-in-india/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art1_img or "",
    "image_caption": "Server racks inside a data centre facility — Meta's Jamnagar site will host AI workloads for over 500 million Indian users",
    "image_attribution": art1_attr or "",
    "body": art1_body.strip()
}


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: EU Orders Meta to Open WhatsApp to Rival AI Chatbots
# ══════════════════════════════════════════════════════════════

art2_slug = make_slug("eu-meta-whatsapp-rival-ai-chatbots-antitrust-order")
art2_id = str(uuid.uuid4())

print(f"\n{'='*60}")
print(f"Article 2: EU WhatsApp AI Chatbot Antitrust Order")
print(f"{'='*60}")

art2_img, art2_attr = source_image(
    art2_slug,
    wiki_search="WhatsApp application smartphone",
    pexels_query="WhatsApp messaging smartphone"
)

art2_body = """The European Commission dropped a rare interim order on Tuesday, directing Meta to immediately restore free access to WhatsApp for rival AI chatbot providers. It is only the second time in 17 years that Brussels has used this emergency enforcement tool — and the target is a messaging platform that 2.7 billion people, including virtually every NRI with a phone, treat as essential infrastructure.

The dispute centres on WhatsApp's Business API, which lets companies connect their software to the messaging platform for customer notifications, order alerts, and support conversations. In October 2025, Meta barred third-party AI chatbots from the API entirely, making Meta AI the sole chatbot available through the service. When rivals complained, Meta offered paid access in March 2026 — at rates that EU competition chief Teresa Ribera described as high enough to drive competitors out of the market.

## What Brussels Ordered

The Commission's interim measure requires Meta to reinstate pre-October 2025 terms: competing AI assistants must be allowed to use the WhatsApp Business API at no charge while the antitrust investigation continues. The order will remain in place for the duration of the probe.

"In rapidly evolving markets, competition can be lost long before a final decision is adopted," Ribera said in a statement. Three companies — California-based The Interaction Company (maker of the Poke.com assistant), French startup Agentik, and a Spanish rival — filed the complaints that triggered the investigation.

Meta pushed back sharply. "The European Commission has decided that OpenAI and some of the largest companies in the world can use the paid-for WhatsApp Business product for free," a company spokesperson said. "This is regulatory overreach subsidised by the many European companies that pay." Meta said it will appeal.

## Why This Matters for Indian Americans

WhatsApp is not merely a messaging app for the Indian diaspora — it is the connective tissue of transnational family life, remittance coordination, and increasingly, commerce. Indian small businesses have built entire customer-facing operations on WhatsApp Business, from neighbourhood kiranas to jewellers in Surat serving NRI buyers in New Jersey.

The EU's insistence that WhatsApp remain open to third-party AI assistants has ripple effects well beyond Europe. Regulatory precedent in Brussels often shapes global policy: Meta may eventually extend the same openness to other markets rather than maintain different access tiers across jurisdictions. That could mean Indian businesses — and the diaspora customers they serve — gain access to a richer ecosystem of AI tools on WhatsApp, not just Meta's own.

For NRI tech professionals, the ruling also signals growing regulatory friction for Big Tech's AI bundling strategies. Meta, Google, Apple, and Microsoft are all racing to make their AI assistants the default on every platform they control. Brussels just established a precedent that doing so on a dominant messaging platform crosses an antitrust line.

## The Broader AI Platform War

The case is part of a wider European campaign to prevent gatekeepers from leveraging platform dominance into adjacent AI markets. Apple's delay in launching Siri AI in the EU — announced the same week — reflects similar regulatory caution.

For Meta, the stakes are significant. WhatsApp Business generates meaningful revenue, and Meta AI is central to Zuckerberg's vision of an AI assistant embedded in every surface the company controls. Losing control of the WhatsApp channel in Europe dents that strategy and may embolden regulators elsewhere.

The Indian government has not signalled a similar intervention, but India's Competition Commission has grown more assertive with tech platforms in recent years. If the EU's approach works — protecting startup AI competitors without degrading the platform for users — New Delhi may take note."""

art2 = {
    "id": art2_id,
    "headline": "Brussels Just Forced WhatsApp Open for Rival AI Chatbots. The Indian Diaspora Should Pay Attention.",
    "subheadline": "The European Commission's rare emergency antitrust order against Meta could reshape how AI assistants reach the 2.7 billion people who depend on WhatsApp — starting with Indian businesses and the NRI families they serve.",
    "slug": art2_slug,
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "WhatsApp is the primary communication and commerce platform for NRIs and Indian small businesses; EU antitrust precedent could open the platform to better AI tools globally.",
    "tags": ["meta", "whatsapp", "eu-antitrust", "ai-regulation", "nri-tech", "ai-chatbots"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/eu-regulators-order-meta-allow-rival-ai-chatbots-free-access-whatsapp-2026-06-10/"},
        {"name": "Engadget", "url": "https://www.engadget.com/big-tech/eu-orders-meta-to-stop-blocking-rival-ai-chatbots-on-whatsapp-154536498.html"},
        {"name": "Morningstar / WSJ", "url": "https://www.morningstar.com/news/dow-jones/202606091012/meta-gets-eu-antitrust-order-to-open-whatsapp-to-rival-ai-chatbots"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art2_img or "",
    "image_caption": "WhatsApp on a smartphone — the EU has ordered Meta to restore third-party AI chatbot access to the platform",
    "image_attribution": art2_attr or "",
    "body": art2_body.strip()
}


# ══════════════════════════════════════════════════════════════
# ARTICLE 3: Sundar Pichai's Google Gemini Now Powers Apple's Siri AI
# ══════════════════════════════════════════════════════════════

art3_slug = make_slug("sundar-pichai-google-gemini-powers-apple-siri-ai")
art3_id = str(uuid.uuid4())

print(f"\n{'='*60}")
print(f"Article 3: Sundar Pichai / Google Gemini Powers Siri AI")
print(f"{'='*60}")

art3_img, art3_attr = source_image(
    art3_slug,
    person_name="Sundar Pichai",
    wiki_search="Google Gemini AI",
    pexels_query="artificial intelligence neural network"
)

art3_body = """A year ago, most of Silicon Valley assumed OpenAI would become Apple's AI partner. ChatGPT was integrated into iOS 18, the rumour mill was deafening, and the logic seemed airtight. Then Apple quietly pivoted — and on Monday, at WWDC 2026, the company confirmed that the new Siri AI is built on foundation models co-developed with Google using Gemini technologies.

The man on the other end of that deal is Sundar Pichai, the Madurai-born CEO of Alphabet and the most powerful Indian-origin executive in global technology.

## What Google Actually Provides

Apple's senior vice-president of software engineering, Craig Federighi, was unusually specific about the architecture in a post-keynote briefing. Apple does not use Google's Gemini models directly, nor Google Search, nor Google Assistant infrastructure. Instead, the companies co-developed new Apple Foundation Models using Gemini's underlying technologies — training methodologies, multimodal reasoning capabilities, and efficiency techniques that allow on-device processing with cloud fallback.

"The amount of the Google Assistant we use is none," Federighi said, drawing a sharp line between co-development and dependency. Cloud processing runs on Apple's servers using Google's infrastructure, but data remains inaccessible to both Apple and Google, the company claims.

The distinction matters commercially. Google gets a multi-year revenue stream from the collaboration (on top of the estimated $20 billion annual default search deal) without cannibalising its own Gemini consumer product. Apple gets frontier AI capabilities without the reputational risk of depending on OpenAI, whose leadership instability and regulatory entanglements have made enterprise partners nervous.

## Pichai's Quiet Empire

For Sundar Pichai, the Apple deal cements a strategic position that no other tech CEO — Indian-origin or otherwise — currently holds. Google's AI technology now underpins three of the four dominant computing platforms: Android (directly), Chrome/Search (natively), and now iOS (through Apple's foundation models). Only Microsoft's Windows ecosystem sits outside Pichai's sphere of influence.

This is a remarkable outcome for an executive who spent much of 2024-25 defending Google against charges that it had fallen behind in AI. The Gemini launch was rocky, the organisational restructuring was painful, and the stock took hits. Two years later, Pichai's bet on Gemini as a platform technology — not just a consumer product — has paid off in the most consequential partnership in the industry.

## The Indian Engineering Backbone

The deal also spotlights the Indian engineering talent that makes both companies run. Google DeepMind, which developed the core Gemini architecture, has significant Indian-origin research leadership. Apple's machine learning teams in Cupertino and Hyderabad employ thousands of Indian engineers who will be instrumental in adapting the foundation models to Apple's privacy-first architecture.

For Indian Americans working at either company, the partnership creates new career vectors. Engineers who understand both the Gemini stack and Apple's on-device ML framework will be among the most sought-after in the industry. Indian engineers on H-1B visas at Google or Apple now work on technology that touches every iPhone, iPad, and Mac shipped — a scale of impact that few positions anywhere can match.

## What NRIs Should Track

Alphabet stock (GOOGL) has been buoyant since the WWDC announcement, while Apple shares dipped — Wall Street wanted more from Siri AI's first public showing. For NRI investors holding either stock, the partnership is a medium-term positive for both: Google locks in recurring AI infrastructure revenue, and Apple accelerates its AI roadmap without the R&D timeline risk of building foundation models solo.

Siri AI launches in English only, with a waitlist, and will not be available in the EU or China at launch. India availability has not been confirmed, but the on-device processing architecture should make a global rollout feasible once the models are localised.

For the Indian diaspora, the deeper significance is representational. The technology that a billion iPhone users will interact with daily was shaped, in part, by an Indian-origin CEO's strategic vision and the Indian engineers who executed it. That is not a footnote. It is the headline."""

art3 = {
    "id": art3_id,
    "headline": "Sundar Pichai's Gemini Now Powers Every iPhone. The Indian Diaspora Built the Bridge.",
    "subheadline": "Apple's new Siri AI runs on foundation models co-developed with Google — a multi-year deal that puts the Madurai-born Alphabet CEO's technology inside a billion devices and creates new career vectors for Indian engineers at both companies.",
    "slug": art3_slug,
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Sundar Pichai (Indian-origin Alphabet CEO) and thousands of Indian engineers at Google/Apple are behind the technology powering every iPhone's new AI assistant; NRI investors benefit from the partnership's impact on both GOOGL and AAPL.",
    "tags": ["sundar-pichai", "google", "apple", "gemini", "siri-ai", "wwdc-2026", "indian-tech-leaders"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "MacObserver", "url": "https://www.macobserver.com/news/apple-confirms-google-isnt-running-siri/"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/09/wwdc-2026-everything-announced/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/apple-stock-price-wwdc-siri-ai/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art3_img or "",
    "image_caption": "Sundar Pichai, CEO of Alphabet — his company's Gemini technology now powers Apple's Siri AI across every iPhone",
    "image_attribution": art3_attr or "",
    "body": art3_body.strip()
}


# ══════════════════════════════════════════════════════════════
# INSERT ALL ARTICLES
# ══════════════════════════════════════════════════════════════

articles = [art1, art2, art3]

print(f"\n{'='*60}")
print("Inserting articles...")
print(f"{'='*60}")

for art in articles:
    # Validate
    if not art["image_url"]:
        print(f"⚠ {art['slug']}: No image sourced — inserting without image")
    if len(art["body"].split()) < 400:
        print(f"⚠ {art['slug']}: Body is short ({len(art['body'].split())} words)")

    try:
        sb_post("p2_articles", art)
        word_count = len(art["body"].split())
        print(f"✅ {art['slug']} ({word_count} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")
