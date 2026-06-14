#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-14 00:00 UTC batch"""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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


# --- Image helpers ---

def fetch_wikipedia_person_image(person_name):
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
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


def upload_to_supabase(img_url, filename):
    """Download image, compress, upload to Supabase storage bucket 'article-images'."""
    try:
        r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        r.raise_for_status()
        raw_bytes = r.content
        if len(raw_bytes) < 5000:
            print(f"  ⚠ Image too small ({len(raw_bytes)} bytes), skipping upload")
            return img_url

        compressed = compress_image(raw_bytes)
        print(f"  📦 Compressed: {len(raw_bytes)} → {len(compressed)} bytes")

        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        }
        ur = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
        if ur.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✅ Uploaded to Supabase: {public_url}")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({ur.status_code}): {ur.text[:200]}")
            return img_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return img_url


now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")


# ═══════════════════════════════════════════
# ARTICLE 1: NVIDIA Vera CPU — China backdoor
# ═══════════════════════════════════════════

print("\n📰 Article 1: NVIDIA Vera CPU / China")
art1_id = str(uuid.uuid4())
art1_slug = make_slug("nvidia-vera-cpu-china-agentic-ai-jensen-huang")

# Image: Jensen Huang from Wikipedia
img1_raw = "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg"
img1_url = upload_to_supabase(img1_raw, f"{art1_slug}.jpg")

art1_body = """Jensen Huang has found a door the American government forgot to lock.

While NVIDIA's most powerful AI training chips — the H200 and its successors — remain frozen in regulatory limbo, unable to ship to China, the company has begun pitching an entirely different product to Chinese cloud providers: the Vera CPU, a standalone processor built not for training AI models but for running them.

Reuters reported this week that NVIDIA has told Chinese clients Vera will be available as early as August 2026 and that orders are open. At least one major Chinese cloud company is planning to purchase more than 300 Vera-powered servers — each containing two chips — for initial deployment in overseas data centres.

The distinction matters. Vera is not a GPU. It is a central processing unit designed for agentic AI — the emerging class of systems that carry out tasks autonomously, from booking flights to writing code to managing supply chains. Because it falls outside the export controls that have effectively reduced NVIDIA's China GPU market share to zero, Vera represents a legal re-entry point into the world's second-largest AI hardware market.

## The $200 billion bet

Huang has been unambiguous about the scale of ambition. Speaking at Computex in Taipei, he projected a $200 billion addressable market for data centre CPUs and confirmed that this estimate includes China. NVIDIA expects Vera to generate $20 billion in revenue by the end of its current fiscal year in January 2027.

Each Vera chip will cost "north of $20,000," according to industry estimates. A full Vera MGX rack — housing up to 256 CPUs connected via NVLink — carries a price tag of roughly $10 million. The chip packs 88 Arm-based Olympus cores, 164 MB of L3 cache, and supports up to 1.5 TB of LPDDR5X memory per socket. NVIDIA claims it runs 1.8 times faster than comparable x86 processors from Intel and AMD.

## Why NRIs should watch this closely

For the estimated 300,000 Indian-origin engineers in the American semiconductor industry, the Vera launch reshapes the competitive landscape they work in every day. At Intel, the Clearwater Forest chips on the new 18A process node are the company's answer. At AMD, the EPYC line has published benchmarks claiming superiority over Vera. Both companies employ tens of thousands of Indian engineers in their design centres.

Then there is the India angle. NVIDIA signed an AI infrastructure agreement with Reliance Industries in March and has been quietly expanding its Bengaluru engineering presence. If Vera gains traction, India's own data centre buildout — projected to double to $13.1 billion by 2034 — could become a secondary market for the chip.

For NRI investors, NVIDIA stock has been in an unusual slump: four consecutive weeks of losses, with shares underperforming peers like AMD (+5.9%) and Micron (+10.1%) in recent trading. The Vera pitch to China may be the catalyst the stock has been waiting for — or a reminder that regulatory risk has not gone away.

## The geopolitical tightrope

The move is not without peril. Vera skirts current export rules, but the U.S. Commerce Department has tightened chip export controls three times in two years. If agentic AI CPUs are reclassified as controlled technology, NVIDIA's China re-entry could be cut short before it begins.

Alibaba and ByteDance are already collaborating with NVIDIA on Vera deployment. That two of China's most powerful technology companies are among the early adopters suggests the chip fills a real gap — and that the agentic AI infrastructure race is now truly global."""

art1 = {
    "id": art1_id,
    "headline": "NVIDIA's Vera CPU Finds a Backdoor Into China. Jensen Huang Is Betting $200 Billion on It.",
    "subheadline": "The chip giant's first standalone CPU, built for agentic AI, sidesteps export controls that have zeroed out its GPU sales to Chinese clients. Orders are open and one major cloud company is already in.",
    "slug": art1_slug,
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Hundreds of thousands of Indian semiconductor engineers at NVIDIA, Intel, and AMD are in the direct competitive crossfire as the CPU wars heat up, while NRI investors track a stock that has underperformed for four straight weeks.",
    "tags": ["nvidia", "vera-cpu", "agentic-ai", "china", "semiconductor", "jensen-huang"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/nvidia-begins-vera-cpu-sales-pitch-chinese-clients-sources-say-2026-06-12/"},
        {"name": "CoinCentral", "url": "https://coincentral.com/nvidia-nvda-stock-rises-as-vera-cpu-orders-open-in-china-for-august/"},
        {"name": "WCCFtech", "url": "https://wccftech.com/nvidia-pivots-to-cpus-to-salvage-china-revenue-after-gpu-restrictions/"},
        {"name": "Zacks", "url": "https://www.zacks.com/stock/news/2416508/nvidias-cpu-ambitions-expand-can-it-challenge-x86-giants-now"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": img1_url,
    "image_caption": "NVIDIA CEO Jensen Huang at an industry event in 2025",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body
}

# ═══════════════════════════════════════════
# ARTICLE 2: IN-SPACe funds space startups
# ═══════════════════════════════════════════

print("\n📰 Article 2: IN-SPACe space startup funding")
art2_id = str(uuid.uuid4())
art2_slug = make_slug("in-space-funds-first-private-spacetech-startups-india")

# Image: PSLV at launch pad from Wikimedia Commons
img2_raw = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/PSLV_C42_First_Launch_Pad_Panorama.jpg/1280px-PSLV_C42_First_Launch_Pad_Panorama.jpg"
img2_url = upload_to_supabase(img2_raw, f"{art2_slug}.jpg")

art2_body = """For the first time in its history, the Indian government has written cheques directly to private space startups. And the signal that sends is worth considerably more than the money itself.

The Indian National Space Promotion and Authorisation Centre, better known as IN-SPACe, has selected three startups under its Technology Adoption Fund for financial backing — Astrobase Space Technologies, SatSure Analytics, and TakeMe2Space Technologies. Each company can receive up to ₹25 crore (roughly $2.6 million), with funds tied to milestone-linked disbursement and technical oversight from an expert committee that includes ISRO scientists, DPIIT officials, and academic researchers.

The projects span the full arc of what India's private space sector is trying to build.

## Reusable rockets, AI earth observers, and satellite navigators

Bengaluru-based Astrobase Space Technologies, founded by former ISRO propulsion engineer Devakumar Thammisetty and CoinDCX co-founder Neeraj Khandelwal, will develop an 800 kilonewton closed-cycle LOX-LNG reusable liquid rocket engine. The specification is significant — engines at this thrust class power medium-lift launch vehicles capable of putting multi-tonne payloads into orbit.

SatSure Analytics, a geospatial AI firm founded in 2017, will build Dhaarini, a large Earth observation foundation model trained on Indian satellite and drone data. The aim is a sovereign AI platform that understands India's monsoon patterns, agricultural diversity, and infrastructure growth better than generic global models. A separate $2.6 million grant from India's space regulator, announced the same week, will support SatSure's broader Earth observation work.

Hyderabad-based TakeMe2Space Technologies will design AI-enabled star tracker systems for CubeSats and larger satellites — navigation instruments that determine a spacecraft's orientation by comparing star patterns against a catalogue. Accurate star tracking is essential for Earth observation, communication satellites, and deep-space missions.

## Why this matters beyond the money

The ₹25 crore cap is modest by global standards — SpaceX raises more than that in a single afternoon. But the precedent is what counts. IN-SPACe was created in 2020 to open India's historically state-run space sector to private companies. Until this week, it had authorised launches, shared ISRO test facilities, and streamlined regulatory approvals. It had never directly funded a startup.

That changes the risk calculus for every venture capital firm watching the sector. Skyroot Aerospace crossed the $1 billion valuation mark last month after a $60 million round backed by Singapore's GIC, BlackRock, and Sherpalo Ventures — the firm of Ram Shriram, the early Google investor who was one of the search company's first board members. Agnikul Cosmos has tested India's first single-piece 3D-printed rocket engine. Pixxel is building a hyperspectral satellite constellation.

## The NRI investment angle

For Indian Americans tracking the sector, the arithmetic is changing quickly. India's space economy is projected to reach $44 billion by 2033, up from roughly $8 billion today. The government has allocated ₹1,000 crore to a space startup fund, and private investment topped $400 million in the last two years.

The challenge remains execution. Skyroot's orbital Vikram-1 rocket has not yet flown. Agnikul's Agnibaan has completed suborbital tests but faces a crowded manifest at Sriharikota. And none of India's private firms have yet demonstrated the launch cadence that investors in SpaceX and Rocket Lab take for granted.

Still, with ISRO's own recent launch failures creating room for private alternatives, the door has never been wider. IN-SPACe's first cheques are a signal that the government is not just opening the door — it is pushing companies through it."""

art2 = {
    "id": art2_id,
    "headline": "India Just Wrote Its First Cheques to Private Space Startups. The Sector Will Never Be the Same.",
    "subheadline": "IN-SPACe has funded three companies building reusable rocket engines, AI-powered earth observation, and satellite navigation systems — the first direct government investment in India's private space sector.",
    "slug": art2_slug,
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "NRI investors and VCs are watching India's $44-billion-by-2033 space economy take shape, with Skyroot already at unicorn status backed by early Google investor Ram Shriram and BlackRock.",
    "tags": ["isro", "in-space", "space-tech", "indian-startups", "skyroot", "satsure"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/in-space-funds-3-startups-to-develop-reusable-rocket-engine-ai-space-model-and-star-tracker-technology/article69672433.ece"},
        {"name": "Inc42", "url": "https://inc42.com/buzz/in-space-funds-three-spacetech-startups-under-taf/"},
        {"name": "Reuters (Skyroot)", "url": "https://www.reuters.com/technology/space/indias-skyroot-becomes-first-1-bln-space-tech-startup-with-gic-sherpalo-blackrock-2026-05-08/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": img2_url,
    "image_caption": "A PSLV rocket at the first launch pad at ISRO's Satish Dhawan Space Centre in Sriharikota",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body
}

# ═══════════════════════════════════════════
# ARTICLE 3: TCS-Anthropic Claude partnership
# ═══════════════════════════════════════════

print("\n📰 Article 3: TCS-Anthropic Claude partnership")
art3_id = str(uuid.uuid4())
art3_slug = make_slug("tcs-anthropic-claude-premier-partner-50000-employees")

# Image: N. Chandrasekaran (TCS Chairman) from Wikipedia
img3_raw = "https://upload.wikimedia.org/wikipedia/commons/4/46/Natarajan_Chandrasekaran_-_India_Economic_Summit_2011.jpg"
img3_url = upload_to_supabase(img3_raw, f"{art3_slug}.jpg")

art3_body = """There is something deeply paradoxical about India's largest IT services company spending millions to arm its own workers with the technology that investors believe will destroy its business model.

Tata Consultancy Services announced this week that it has entered a global strategic partnership with Anthropic, the maker of Claude, and will deploy the AI assistant to 50,000 employees across engineering, finance, legal, marketing, and sales. TCS will also establish a dedicated Claude-focused business unit, gain early access to new model releases, and jointly go to market with Anthropic in sectors where AI adoption has stalled at the pilot stage — banking, healthcare, aviation, telecom, and public services.

The partnership makes TCS a Global Premier Partner in Anthropic's Claude Partner Network. Dario Amodei, Anthropic's co-founder and CEO, called the deal a deepening of Anthropic's commitment to India, which he described as the company's second-largest market.

## The embrace of the executioner

The timing is extraordinary. TCS shares have fallen 32 per cent in 2026. The broader Nifty IT index is down 25 per cent, making technology services India's worst-performing sector this year. In February, when Anthropic launched Claude Code — an AI agent capable of writing, debugging, and deploying software autonomously — Indian IT stocks lost over $62 billion in market capitalisation in a single week.

Now TCS is making Anthropic a partner. So is Infosys, which struck a similar deal in February. HCLTech has its own arrangement with NVIDIA. The entire industry is running toward the companies that investors say will render it obsolete.

The logic, from TCS's perspective, is straightforward. At the company's annual general meeting on June 10, Chairman N. Chandrasekaran made a statement that would have been unthinkable two years ago: TCS expects to have as many AI agents as human employees. With roughly 500,000 people on the payroll, that means 500,000 AI agents working alongside them.

"Some of the work being done will go to AI agents," Chandrasekaran said. "That will be the nature of the transition that we have to go through — not only as a company, as an industry, and as a country."

## What 50,000 Claude licences actually mean

The internal deployment is strategically important because TCS plans to use its own workforce as a large-scale testing ground. Insights from deploying Claude across its own operations — contract review in legal, proposal generation in sales, code generation in engineering — will feed directly into client engagements.

TCS's U.K.-based Diligenta division, which manages life and pensions for over 22 million customers, will use Claude for customer service and process automation. TCS iON, its digital learning platform, will offer Anthropic certification programs. The company will also contribute domain-specific tools to Anthropic's Claude Code ecosystem, including capabilities for claims adjudication and lending advisory.

CEO K. Krithivasan framed the partnership as a path from pilot to production. "Enterprise AI value comes from understanding business context, orchestrating complex systems, and applying deep AI engineering talent," he said.

## The NRI career question

For the hundreds of thousands of Indian professionals in the American and British IT services workforce — many of them employed by TCS, Infosys, Wipro, and HCLTech — the partnership raises an uncomfortable question: are they training their replacements?

The answer, for now, is nuanced. The first wave of AI adoption in IT services has not produced the mass layoffs that the stock market has priced in. TCS cut 23,000 jobs on a net basis in the last fiscal year, but the company says it will not downsize — it will simply hire fewer people going forward. Infosys added 5,000. Wipro added 6,500.

The real pressure is on the economics, not the headcount. Clients are asking for the same work with fewer billable hours. Revenue per employee is the metric that keeps IT CFOs awake at night, and Claude-class AI models are exactly the tool that can compress it.

For Indian engineers on H-1B visas at these firms, the calculus is more immediate. If their employer needs fewer people for the same project, visa renewals become harder to justify. If their role shifts from writing code to managing AI agents, the job title on the visa petition may no longer match the work being done.

None of this is settled. But TCS betting its future on Claude — and Anthropic calling India its second-largest market — suggests the transformation is no longer a forecast. It is a line item on the balance sheet."""

art3 = {
    "id": art3_id,
    "headline": "TCS Is Arming 50,000 Workers With Claude. The Company Threatening Its Business Is Now Its Partner.",
    "subheadline": "Tata Consultancy Services has become Anthropic's Global Premier Partner, rolling out Claude AI to tens of thousands of employees — even as the technology sends IT stocks to multi-year lows.",
    "slug": art3_slug,
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Indian IT professionals on H-1B visas at TCS, Infosys, and Wipro face an uncomfortable question as their employers partner with the very AI companies investors believe will disrupt the $315-billion IT services sector.",
    "tags": ["tcs", "anthropic", "claude", "india-it", "ai-disruption", "enterprise-ai"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-tcs-partners-with-anthropic-drive-enterprise-ai-scaling-2026-06-11/"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/11/anthropic-taps-tcs-to-scale-its-enterprise-ai-deployments/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/tcs-anthropic-partner-to-drive-enterprise-ai-scaling/article69671512.ece"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/tcs-anthropic-partner-to-scale-enterprise-ai-to-equip-50000-employees-with-claude-story-469519"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": img3_url,
    "image_caption": "TCS Chairman Natarajan Chandrasekaran at the India Economic Summit",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body
}


# ═══════════════════════════════════════════
# INSERT ALL ARTICLES
# ═══════════════════════════════════════════

articles = [art1, art2, art3]

print("\n" + "="*60)
print("INSERTING ARTICLES")
print("="*60)

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")
