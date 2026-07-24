#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-13 15:55 UTC batch"""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path

# ── Load env ──────────────────────────────────────────────────────────
for env_file in [Path.home() / ".env.supabase", Path.home() / "workspace/.env.pexels"]:
    if env_file.exists():
        for line in env_file.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

SB_URL  = os.environ["SUPABASE_URL"]
SB_KEY  = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS  = os.environ.get("PEXELS_API_KEY", "")
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

# ── Helpers ───────────────────────────────────────────────────────────
def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

# ── Image sourcing ───────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10
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
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers=UA, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []

def fetch_pexels_image(query):
    """Fetch a Pexels image via curl (urllib gets 403)."""
    if not PEXELS:
        return None
    import subprocess
    try:
        q = query.replace(' ', '+')
        r = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={q}&per_page=5",
             "-H", f"Authorization: {PEXELS}"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(r.stdout)
        photos = data.get("photos", [])
        if photos:
            url = photos[0]["src"]["large2x"]
            print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

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

def download_and_upload(image_url, slug):
    """Download image, compress, upload to Supabase article-images bucket."""
    try:
        r = requests.get(image_url, headers=UA, timeout=20)
        if r.status_code != 200 or not r.headers.get("Content-Type","").startswith("image"):
            print(f"  ⚠ Image download failed ({r.status_code}): {image_url[:60]}")
            return None
        raw = r.content
        if len(raw) < 5000:
            print(f"  ⚠ Image too small ({len(raw)} bytes), skipping")
            return None
        compressed = compress_image(raw)
        filename = f"{slug}.jpg"
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        }
        resp = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
        if resp.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            size_kb = len(compressed) / 1024
            print(f"  ✓ Uploaded {filename} ({size_kb:.0f} KB)")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({resp.status_code}): {resp.text[:100]}")
            return None
    except Exception as e:
        print(f"  ⚠ download_and_upload error: {e}")
        return None

def source_image(person_name=None, topic_terms=None, pexels_query=None, slug=""):
    """Multi-source image search: Wikipedia → Commons → Pexels. Returns (url, attribution, caption)."""
    candidates = []

    # Source 1: Wikipedia person image
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append((wiki_img, "Wikimedia Commons", f"{person_name}"))

    # Source 2: Wikimedia Commons
    if topic_terms:
        commons = fetch_wikimedia_commons_images(topic_terms)
        for c in commons[:2]:
            candidates.append((c["url"], "Wikimedia Commons", c["title"].replace("File:", "")))

    # Source 3: Pexels
    if pexels_query:
        pexels_img = fetch_pexels_image(pexels_query)
        if pexels_img:
            candidates.append((pexels_img, "Pexels", pexels_query))

    # Pick best and upload
    for url, attribution, desc in candidates:
        final_url = download_and_upload(url, slug)
        if final_url:
            return final_url, attribution, desc
    return None, None, None


# ══════════════════════════════════════════════════════════════════════
# ARTICLE 1: KPMG AI Report Hallucinations
# ══════════════════════════════════════════════════════════════════════
print("\n📰 Article 1: KPMG AI Report Hallucinations")

art1_slug = make_slug("kpmg-ai-report-hallucinations-vibe-citing-consulting")
art1_id = str(uuid.uuid4())

img1_url, img1_attr, img1_desc = source_image(
    topic_terms="KPMG office building",
    pexels_query="business consulting office meeting",
    slug=art1_slug
)

art1 = {
    "id": art1_id,
    "headline": "KPMG Pulled Its Own AI Report After It Turned Out to Be Full of Fabrications",
    "subheadline": "Only five of 45 citations were accurate. UBS, the NHS, and Swiss railways all denied the claims made about them. Welcome to 'vibe citing.'",
    "slug": art1_slug,
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Hundreds of thousands of Indians work at Big Four firms and IT consultancies now deploying AI in client work — this scandal is a warning about what happens when oversight fails.",
    "tags": ["ai-hallucinations", "kpmg", "consulting", "big-four", "indian-it"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Register", "url": "https://www.theregister.com/ai-and-ml/2026/06/12/kpmgs-ai-report-turns-into-a-demo-of-ai-hallucinations/5255029"},
        {"name": "Financial Times", "url": "https://www.ft.com"},
        {"name": "Finance Monthly", "url": "https://www.finance-monthly.com"},
        {"name": "GPTZero", "url": "https://gptzero.me"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": img1_url or "",
    "image_caption": "KPMG has withdrawn its agentic AI report pending investigation",
    "image_attribution": img1_attr or "",
    "body": """KPMG International has withdrawn a flagship report on artificial intelligence after an investigation found it riddled with fabricated case studies, false statistics, and citations that led nowhere. The episode is one of the most embarrassing corporate AI blunders to date — and it landed squarely in the lap of the very consultants who sell AI readiness to everyone else.

The report, titled *Redefining Excellence in the Age of Agentic AI*, was published in October 2025 and widely circulated as a guide for enterprises deploying autonomous AI agents. It looked authoritative. It was not.

## Five Out of Forty-Five

Research firm GPTZero conducted a forensic audit of the report's 45 citations and found that only five correctly pointed to the claimed source. The rest were mangled, misleading, partially fabricated, or too vague to verify. GPTZero coined a term for the phenomenon: "vibe citing" — the citation equivalent of vibe coding, where generative AI stitches together fragments of real sources and invents the rest.

Roughly half of the report's factual claims were false, unsupported, or attributed to the wrong source, according to GPTZero's analysis.

The case studies were particularly creative. The report claimed Swiss bank UBS had deployed AI agents across investment advisory, risk management, and compliance monitoring through a platform co-developed with Microsoft. A UBS spokesperson told the Financial Times the assertions were "factually incorrect."

Swiss Federal Railways was described as a "holistic mobility orchestrator" powered by AI agents optimising passenger travel and managing real-time carbon impact. The railway confirmed this was "not accurate." Transport for London said a claim about AI-driven congestion prediction was misleading. NHS Greater Manchester said assertions about AI-driven patient triage bore no relation to the press release cited in the footnotes.

## A Pattern, Not an Outlier

KPMG is not alone. EY retracted a study last month after GPTZero identified fake footnotes. Sullivan & Cromwell admitted in April that a bankruptcy court filing contained AI-generated inaccuracies. Deloitte refunded the Australian government last year after AI-generated content infiltrated a taxpayer-funded report.

GPTZero says it has now reviewed more than 3,000 consulting PDFs and found six reports from various firms full of fake citations, broken URLs, and contradictory statistics.

"It's very ironic that the biggest experts in AI technology in the world were generating AI-hallucinated citations," said Edward Tian, GPTZero's founder.

KPMG has removed the report from its websites. A spokesperson said the firm "takes the accuracy and integrity of its published content seriously" and expects all staff to follow guidelines on responsible AI use, "including human oversight to validate content and verify independent sources."

## Why This Matters to Indian Tech Workers

The Big Four consulting firms — KPMG, Deloitte, EY, and PwC — collectively employ hundreds of thousands of Indian professionals, both in India and across their global offices. These firms are also the largest buyers of Indian IT services. When KPMG, Deloitte, and EY deploy AI tools for research and client deliverables without adequate human review, it is often Indian associates and analysts who face the operational consequences: retractions, client complaints, and reputational damage that rolls downhill.

Indian IT services firms are now racing to integrate the same generative AI tools into their own workflows. TCS just partnered with Anthropic to equip 50,000 associates with Claude. Infosys struck a similar deal earlier this year. The KPMG debacle is a cautionary tale for every firm in Bengaluru, Hyderabad, and Pune that is building AI into client-facing work: the technology that was supposed to demonstrate competence can, without rigorous oversight, demonstrate precisely the opposite.

Sandra Wachter, professor of technology and regulation at the Oxford Internet Institute, put it bluntly: "I've described them as bullshitters. It's just not built for truth."

The firms selling AI transformation cannot afford to be its most visible casualties.
"""
}

# ══════════════════════════════════════════════════════════════════════
# ARTICLE 2: OpenAI / Anthropic AI Price War
# ══════════════════════════════════════════════════════════════════════
print("\n📰 Article 2: OpenAI vs Anthropic AI Price War")

art2_slug = make_slug("openai-anthropic-price-war-token-costs-indian-startups")
art2_id = str(uuid.uuid4())

img2_url, img2_attr, img2_desc = source_image(
    topic_terms="OpenAI artificial intelligence",
    pexels_query="artificial intelligence neural network server",
    slug=art2_slug
)

art2 = {
    "id": art2_id,
    "headline": "The AI Price War Has Begun. Indian Developers May Finally Catch a Break.",
    "subheadline": "OpenAI is weighing drastic token price cuts to compete with Anthropic. Meanwhile, open-source Chinese models are quietly eating into both their margins.",
    "slug": art2_slug,
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Indian AI startups and developers — from Sarvam AI to thousands of solo builders — spend heavily on API tokens. A price war between the frontier labs could reshape their economics overnight.",
    "tags": ["openai", "anthropic", "ai-pricing", "deepseek", "indian-startups"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Wall Street Journal (via Mint)", "url": "https://www.livemint.com/ai/the-ai-price-war-is-here-piling-pressure-on-openai-and-anthropic-11781229393891.html"},
        {"name": "Barron's (via Mint)", "url": "https://www.livemint.com/ai/openai-mulls-ai-price-war-with-anthropic-it-s-a-big-risk-for-tech-stocks-11781226747758.html"},
        {"name": "Geeky Gadgets", "url": "https://www.geeky-gadgets.com"},
        {"name": "Barron's", "url": "https://www.barrons.com"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": img2_url or "",
    "image_caption": "OpenAI and Anthropic are competing on price as enterprises seek cheaper AI alternatives",
    "image_attribution": img2_attr or "",
    "body": """OpenAI is considering significant cuts to the price it charges for AI tokens, the basic unit of consumption in the machine-learning economy. The move, reported by the Wall Street Journal, is aimed squarely at Anthropic, whose Claude models have been gaining ground in enterprise computing — but whose costs have also been giving customers sticker shock.

Sam Altman, OpenAI's chief executive, recently told a company event that costs had suddenly become "a huge issue." He was not being diplomatic. Multiple technology companies, including Uber, have faced unexpectedly large bills for AI usage, several of them traced to Anthropic's Claude and its resource-hungry agentic workflows.

## The Tokenmaxxing Trap

The AI industry has developed its own vocabulary for the problem. Neil Dhar, a senior vice president at IBM Consulting, calls it "tokenmaxxing" — the organisational push to use as much AI as possible, as fast as possible, driven by competitive anxiety rather than a clear return on investment.

The maths are stark. Anthropic's recently released Fable 5 model costs $10 per million input tokens and $50 per million output tokens — more than 50 times the price of DeepSeek's V4 Pro, the Chinese open-source model that has been surging in popularity across American businesses. On Vercel's developer platform, DeepSeek's share of AI usage rose from 1 per cent in April to 17 per cent in May.

OpenAI sees itself as having an advantage in a price war. It spent heavily over the past year to lock in computing resources at prices far below current market rates. It also has GPT-5.6, codenamed Kindle, in the pipeline, which is expected to deliver better performance at lower operational cost.

But Anthropic is not sitting still. Both companies have filed confidential paperwork for potential IPOs, and both are bleeding billions of dollars annually on compute. Cutting prices further would widen those losses at the worst possible moment.

## The Open-Source Squeeze

The real pressure, though, comes from below. Open-source models — DeepSeek, Meta's Llama, Alibaba's Qwen — are no longer just research curios. They are production-grade tools that handle the bread-and-butter tasks of inbox triage, document summarisation, and code generation at a fraction of the cost.

Flo Crivello, founder of AI assistant startup Lindy, said his team spent two months building tooling to test DeepSeek's V4 model. They found it handled everyday tasks as well as Anthropic's Sonnet — at one-tenth the price. The switch saved the company millions of dollars.

On OpenRouter, a platform that routes AI queries across providers, DeepSeek has been the most-used AI company since mid-May. More than 500 organisations have swapped from proprietary to open-source models on that platform alone.

"You don't need a model that knows quantum gravity," said Vishal Misra, vice dean of computing and AI at Columbia University. "These open-source models are very capable, and the ability to charge a big premium for AI is going to diminish."

## What This Means for Indian Builders

For Indian AI startups and developers, a price war among frontier labs is unambiguously good news. Indian companies tend to be more price-sensitive than their Silicon Valley counterparts — a function of smaller funding rounds, tighter margins, and the unfavourable dollar-to-rupee exchange rate that makes every API call costlier.

Sarvam AI, which just earned a seat at the G7 summit, builds multilingual models for Indian languages. Companies like it operate in a world where token costs can make or break unit economics. A meaningful drop in OpenAI or Anthropic pricing — or a viable open-source alternative like DeepSeek — changes the calculus for every Indian startup building on top of LLMs.

The thousands of Indian developers building AI-powered tools for global markets stand to benefit even more directly. Many of them use OpenAI or Anthropic APIs for coding assistants, chatbots, and document processing. Even a 30 per cent price cut would translate into significant savings across thousands of projects.

Andrew Moore, former head of Google Cloud AI and now founder of Lovelace AI, described the emerging dynamic: "Our AIs now, they are so stingy and parsimonious. They know exactly how to get something out of the cheapest models possible. When they get into trouble, they temporarily jump up to a higher price point with a fancier model."

That model — cheap by default, expensive only when necessary — is likely to become the standard. The question is whether OpenAI and Anthropic can survive the transition without destroying the economics of their own businesses. Both have filed for IPOs. Both are losing billions. And the margins they need to justify their valuations are precisely the margins that open-source competition and mutual price-cutting are eroding.

For Indian builders, the advice is simple: lock in no long-term commitments, build model-agnostic architectures, and let the giants fight. The tokens are about to get cheaper.
"""
}

# ══════════════════════════════════════════════════════════════════════
# ARTICLE 3: DRAM Memory Crisis
# ══════════════════════════════════════════════════════════════════════
print("\n📰 Article 3: DRAM Memory Crisis / Consumer Impact")

art3_slug = make_slug("dram-prices-doubled-memory-shortage-sanjay-mehrotra-micron")
art3_id = str(uuid.uuid4())

# Try Sanjay Mehrotra Wikipedia image first
img3_url, img3_attr, img3_desc = source_image(
    person_name="Sanjay Mehrotra",
    topic_terms="DRAM memory chip semiconductor",
    pexels_query="computer memory chip circuit board closeup",
    slug=art3_slug
)

art3 = {
    "id": art3_id,
    "headline": "DRAM Prices Have Doubled This Year. Sanjay Mehrotra's Micron Is Printing Money.",
    "subheadline": "The AI boom has created the worst memory chip shortage in a decade. Samsung engineers are getting $400,000 bonuses. Your next laptop will cost more.",
    "slug": art3_slug,
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Indian-origin Sanjay Mehrotra runs Micron, one of only three companies that control the global memory supply. His company is building India's first major semiconductor fab in Gujarat.",
    "tags": ["dram", "memory-chips", "sanjay-mehrotra", "micron", "samsung", "semiconductor"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Register", "url": "https://www.theregister.com/storage/2026/06/02/expect-more-of-those-dram-price-hikes-as-memory-shortage-continues-to-bite/5250049"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/south-korea-stocks-chips-6126199a"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com"},
        {"name": "TrendForce", "url": "https://www.trendforce.com"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": img3_url or "",
    "image_caption": img3_desc if img3_desc and "Sanjay" in str(img3_desc) else "The global memory chip shortage is driving up prices for consumer electronics",
    "image_attribution": img3_attr or "",
    "body": """The price of DRAM — the memory chips inside every laptop, phone, and server on Earth — doubled in the first quarter of 2026. It is going to rise again. TrendForce, the Taiwanese market research firm that tracks the industry, expects contract prices for conventional DRAM to climb another 58 to 63 per cent this quarter. The cause is straightforward: artificial intelligence is swallowing the world's memory supply, and there is not nearly enough to go around.

The three companies that control virtually the entire DRAM market — Samsung, SK Hynix, and Sanjay Mehrotra's Micron Technology — are prioritising production of high-bandwidth memory (HBM) for AI servers. Hyperscale customers like Microsoft, Google, and Amazon are paying whatever it takes. Everyone else — PC makers, phone manufacturers, console companies — is left fighting for whatever supply remains.

## The Numbers

Industry revenue for memory chips spiked 81 per cent in Q1 to $97 billion, according to TrendForce. Inventory levels at suppliers are "extremely low," and any incremental supply is being routed to AI servers first.

The downstream effects are already visible. The average price of laptops and desktops in Europe has risen by double-digit percentages. Micron shut its 29-year-old Crucial consumer memory brand in December to redirect supply to larger customers. Phison's chief executive has warned that the shortage could push some consumer-electronics companies out of business in 2026.

SK Hynix's chairman, Chey Tae-won, told reporters in Taipei that the company aims to double its wafer output — but only gradually, over the next five years. "The shortage could persist until 2030," he said.

## $400,000 Bonuses in Seoul

The windfall has created extraordinary wealth inside the two Korean giants. Faced with a strike last month, Samsung agreed to a profit-sharing deal that could see bonuses in its memory-chip division reach $400,000 per employee this year, according to Dalton Investments. SK Hynix quietly reached a similar settlement late last year.

Samsung's operating profit soared more than sevenfold year over year. The Kospi index, South Korea's benchmark, has surged 165 per cent in the past year, driven almost entirely by the two chipmakers.

But the boom has a turbulent edge. Foreign investors have sold more than $40 billion worth of Korean stocks in six months as allocation limits were reached. Local retail investors — many of them novices buying through leveraged instruments — have filled the gap. "A lot of 'ant investors' are borrowing money to get into the market," says Benjamin Engel, a Korean studies professor at Dankook University. "It's kind of scary."

Samsung shares dropped 16 per cent in the past week alone, paring their year-to-date gain to 150 per cent.

## Sanjay Mehrotra's Moment

For Micron, the shortage is a licence to print money — and its Indian-origin chief executive, Sanjay Mehrotra, is in the middle of the most consequential period of his tenure.

Mehrotra, who co-founded SanDisk in 1988 and took over Micron in 2017, now leads the only American company among the Big Three memory producers. Micron has started DRAM manufacturing at its Manassas, Virginia, fab and expects initial wafer output at its first Idaho facility by mid-2027.

More importantly for the Indian diaspora, Micron is building a major semiconductor fabrication plant in Sanand, Gujarat — one of the first large-scale chip fabs in India, supported by the Modi government's semiconductor mission. The $2.75 billion assembly and test facility is expected to begin operations in late 2025. If successful, it will create thousands of engineering jobs and position India as a node in the global memory supply chain for the first time.

## What NRIs Should Watch

The practical implications for Indian Americans are twofold. First, consumer technology is getting more expensive. If you are buying a laptop, phone, or gaming console in the second half of 2026, expect to pay meaningfully more than you did a year ago. The premium is a direct function of DRAM costs, and relief is unlikely before late 2027 at the earliest.

Second, for NRI investors, the memory sector is simultaneously the most profitable and most volatile corner of the semiconductor industry. Micron, Samsung, and SK Hynix are printing record earnings, but the stocks are already pricing in years of continued scarcity. When new capacity from all three producers comes online in 2028 — and when fixed-price agreements start to expire — the cycle will reassert itself.

"You're seeing tremendous volatility in Korean markets when sentiment weakens," warns James Lim of Dalton Investments. "That indicates leveraged investors getting a margin call."

Success, as they say in Seoul, can bring its own headaches.
"""
}

# ══════════════════════════════════════════════════════════════════════
# Insert all articles
# ══════════════════════════════════════════════════════════════════════
print("\n═══ Inserting articles ═══")
for art in [art1, art2, art3]:
    # Skip if no image
    if not art["image_url"]:
        print(f"⚠ No image for {art['slug']}, inserting without image")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print("\nDone.")
