#!/usr/bin/env python3
"""
Tech Writer — 2026-06-11 09:00 UTC
Writes 2-3 technology articles for The Videshi, sources images, uploads to Supabase.
Topics:
  1. Microsoft's Agentic AI Blitz (Satya Nadella, MAI-Thinking-1, Agent 365)
  2. OpenAI + Anthropic Dual IPO Race ($1T + $965B)
  3. AI Layoffs Cross 100K in 2026
"""

import os, sys, json, uuid, re, io, time
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            line = line.removeprefix('export ')
            k, v = line.split('=', 1)
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k, v)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY   = os.environ.get('PEXELS_API_KEY', '')

import requests
from PIL import Image

HEADERS_SB = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
}
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

# ── helpers ──────────────────────────────────────────────────────────────

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


def upload_to_supabase_storage(img_bytes, filename, bucket='article-images'):
    """Upload image bytes to Supabase storage. Returns public URL."""
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'image/jpeg',
        'x-upsert': 'true',
    }
    r = requests.post(upload_url, headers=headers, data=img_bytes, timeout=30)
    if r.status_code not in (200, 201):
        # Try PUT (upsert)
        r = requests.put(upload_url, headers=headers, data=img_bytes, timeout=30)
    if r.status_code not in (200, 201):
        print(f"  ✗ Storage upload failed ({r.status_code}): {r.text[:200]}")
        return None
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
    print(f"  ✓ Uploaded to Supabase storage: {filename} ({len(img_bytes)//1024}KB)")
    return public_url


def download_image(url):
    """Download image, return bytes or None."""
    try:
        r = requests.get(url, headers=UA, timeout=20, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 5000:
            ct = r.headers.get('Content-Type', '')
            if 'image' in ct or url.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                return r.content
            # Check magic bytes
            if r.content[:3] in (b'\xff\xd8\xff', b'\x89PN', b'GIF', b'RIF'):
                return r.content
        print(f"  ✗ Download failed: status={r.status_code}, size={len(r.content)}")
    except Exception as e:
        print(f"  ✗ Download error: {e}")
    return None


def fetch_wikipedia_person_image(person_name):
    encoded = person_name.replace(' ', '_')
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
        print(f"  ⚠ Wikipedia API error: {e}")
    return None


def fetch_wikimedia_commons(query, limit=5):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json",
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
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": query, "per_page": 3, "orientation": "landscape"},
            timeout=10,
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{query}'")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def source_image(article_slug, person_name=None, wiki_queries=None, pexels_query=None):
    """Multi-source image pipeline. Returns (supabase_url, attribution) or (None, None)."""
    candidates = []

    # Source 1: Wikipedia person
    if person_name:
        url = fetch_wikipedia_person_image(person_name)
        if url:
            candidates.append({"url": url, "source": "wikipedia", "priority": 1})

    # Source 2: Wikimedia Commons
    for q in (wiki_queries or []):
        results = fetch_wikimedia_commons(q)
        for r in results[:2]:
            candidates.append({"url": r["url"], "source": "wikimedia_commons", "priority": 2})
        if results:
            break  # Got results from first query

    # Source 3: Pexels
    if pexels_query:
        url = fetch_pexels_image(pexels_query)
        if url:
            candidates.append({"url": url, "source": "pexels", "priority": 3})

    # Pick best
    candidates.sort(key=lambda c: c["priority"])
    for cand in candidates:
        print(f"  Trying {cand['source']}: {cand['url'][:80]}...")
        raw = download_image(cand["url"])
        if raw:
            compressed = compress_image(raw)
            if len(compressed) > 5000:
                filename = f"{article_slug}.jpg"
                final_url = upload_to_supabase_storage(compressed, filename)
                if final_url:
                    attr = "Wikimedia Commons" if cand["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
                    return final_url, attr
            else:
                print(f"  ✗ Compressed image too small ({len(compressed)} bytes)")

    print("  ✗ No suitable image found")
    return None, None


def sb_insert(table, data):
    """Insert a row into Supabase. Returns response data."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.post(url, headers=HEADERS_SB, json=data, timeout=30)
    if r.status_code in (200, 201):
        rows = r.json()
        if rows:
            print(f"  ✓ Inserted into {table}: {rows[0].get('id', 'ok')}")
            return rows[0]
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
    return None


def sb_patch(table, match, data):
    """Patch a row in Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = match
    headers = {**HEADERS_SB, 'Prefer': 'return=representation'}
    r = requests.patch(url, headers=headers, params=params, json=data, timeout=30)
    if r.status_code in (200, 201):
        print(f"  ✓ Patched {table}")
        return r.json()
    print(f"  ✗ Patch failed ({r.status_code}): {r.text[:300]}")
    return None


# ── articles ─────────────────────────────────────────────────────────────

TODAY = "2026-06-11"

ARTICLES = [
    {
        "headline": "Microsoft's Agentic AI Offensive Puts Indian IT on Notice",
        "subheadline": "Satya Nadella's new Agent 365 platform and frontier model MAI-Thinking-1 signal a fundamental shift — one that Indian engineers are building and Indian outsourcers may have to survive.",
        "slug": f"microsoft-agentic-ai-agent-365-indian-it-{TODAY.replace('-', '')}",
        "category": "technology",
        "tags": ["Microsoft", "Satya Nadella", "AI agents", "Agent 365", "Indian IT", "MAI-Thinking-1", "enterprise AI"],
        "diaspora_angle": "Indian engineers form the backbone of Microsoft's AI workforce, yet the very tools they build — autonomous agents that handle procurement, auditing, and customer service — threaten to displace the consulting and IT-services work that employs millions across TCS, Infosys, and Wipro. For NRI tech workers, the agentic shift is both career fuel and existential question.",
        "sources": [
            {"name": "Zacks Investment Research", "url": "https://www.zacks.com/stock/news/2432158/microsoft-msft-expands-ai-agent-capabilities"},
            {"name": "TheStreet", "url": "https://www.thestreet.com/technology/microsoft-unveils-mai-thinking-1-its-first-frontier-ai-model"},
            {"name": "Microsoft Official Blog", "url": "https://blogs.microsoft.com/blog/2026/05/19/https-blogs-microsoft-com-blog-2025-05-19-introducing-agent-365/"}
        ],
        "body": """Microsoft is no longer content to be the company that hosts other people's artificial intelligence. Over the past month, Satya Nadella has unveiled a cascade of announcements that collectively amount to the most aggressive enterprise AI play in the industry: a home-grown frontier model, an autonomous-agent platform priced to move, and a string of blockbuster consulting deals that rewrite the relationship between software vendor and customer. For the Indian diaspora — which fills corner offices in Redmond and call-centre floors in Bengaluru alike — the implications cut in two very different directions.

The centrepiece is **Agent 365**, a new platform layered atop Microsoft 365 that lets businesses deploy AI agents to handle tasks previously done by humans: processing invoices, triaging IT tickets, drafting compliance reports, scheduling meetings across time zones. Priced at roughly $15 per user per month, Agent 365 is designed not as a premium upsell but as an expectation — a baseline productivity layer for every enterprise seat. Early adopters include KPMG (276,000 employees), Atos (56,000 employees), and, most strikingly, NHS England, the health system that serves 56 million people with a workforce of over 500,000.

Powering much of this is **MAI-Thinking-1**, Microsoft's first in-house frontier reasoning model. Built by Microsoft's own research teams rather than licensed from OpenAI, it is a signal that Redmond intends to own its AI stack end to end. The model has already been integrated into Azure AI services and is available through the Azure Cobalt 200 chip infrastructure that Microsoft has been rolling out across its data centres.

The financial commitment behind all of this is staggering. Microsoft's capital expenditure on AI infrastructure is on track to approach $190 billion over the current cycle, a figure that dwarfs the GDP of several small nations and that the company justifies with a simple argument: enterprises will pay for agents that save them headcount.

## What It Means for Indian Tech Workers

That last phrase — "save them headcount" — is where the story becomes personal for the Indian diaspora. Tens of thousands of Indian-origin engineers work at Microsoft, many of them building the very agent frameworks now being deployed. Satya Nadella himself is the most prominent exemplar of the Indian talent pipeline that flows from IITs and NITs to the Pacific Northwest. These engineers are riding the wave: demand for AI-infrastructure and agent-development roles is surging, salaries are climbing, and H-1B holders with machine-learning expertise have rarely been more sought after.

But the downstream effects are less comfortable. The consulting and IT-services giants — TCS, Infosys, Wipro, HCLTech — have built their businesses on supplying human labour to do exactly the kind of structured, repetitive, rules-based work that Agent 365 is designed to automate. When KPMG deploys Microsoft agents across its global audit practice, the arithmetic is stark: fewer associate-level consultants will be needed to do the same volume of work. When NHS England automates appointment scheduling and referral processing, the outsourced service desks that Indian firms operate lose a reason to exist.

Indian IT firms are not blind to this. Infosys has partnered with NVIDIA to build its own AI-agent practice; TCS has expanded its Microsoft partnership specifically around Copilot integration. But the pivot is expensive and uncertain. Training a workforce of hundreds of thousands to build, manage, and customise AI agents — rather than perform the tasks those agents are replacing — is a generational challenge.

## The Bigger Picture

Microsoft's move also shifts the competitive landscape. By building MAI-Thinking-1, Nadella has signalled that Microsoft's $13 billion investment in OpenAI was a launchpad, not a dependency. Azure now offers models from OpenAI, Anthropic, Meta, Mistral, and Microsoft itself — a multi-model bazaar that lets enterprise customers avoid lock-in while keeping their spending within the Azure ecosystem.

For NRI investors watching the AI trade, the signal is clear: the next phase of value creation in AI is not in building models but in deploying them inside enterprise workflows. Microsoft is betting nearly $200 billion that the winners will be companies that turn research into revenue — and that the losers will be those who still sell human hours for tasks a $15-per-month agent can handle.

The Indian diaspora, straddling both sides of that divide, will feel the transformation more acutely than most.""",
        "person_name": "Satya Nadella",
        "wiki_queries": ["Microsoft artificial intelligence headquarters", "Microsoft Build 2025"],
        "pexels_query": "Microsoft headquarters technology",
        "image_caption": "Satya Nadella, CEO of Microsoft, has positioned the company at the centre of enterprise AI with Agent 365 and its first in-house frontier model",
    },
    {
        "headline": "OpenAI and Anthropic File Duelling IPOs, Opening a $2 Trillion AI Gold Rush",
        "subheadline": "Within a single week, the two leading AI labs filed confidential S-1 registrations targeting a combined valuation near $2 trillion — and Indian researchers, investors, and policymakers all have skin in the game.",
        "slug": f"openai-anthropic-dual-ipo-ai-valuation-{TODAY.replace('-', '')}",
        "category": "technology",
        "tags": ["OpenAI", "Anthropic", "IPO", "Sam Altman", "Dario Amodei", "AI valuation", "NRI investors"],
        "diaspora_angle": "Indian-origin ML researchers hold senior roles at both labs; Sriram Krishnan advises the White House on AI policy shaping how these IPOs will be regulated. For NRI investors, the dual listings represent the first chance to own equity in frontier AI — but at valuations that assume these companies will dominate a technology whose regulation is still being written.",
        "sources": [
            {"name": "Reuters", "url": "https://www.reuters.com/technology/artificial-intelligence/openai-files-confidential-ipo-registration-2026-06-08/"},
            {"name": "ITWeb", "url": "https://www.itweb.co.za/article/anthropic-files-for-ipo-amid-960bn-valuation/"},
            {"name": "TheStreet", "url": "https://www.thestreet.com/technology/openai-ipo-valuation-target-1-trillion"}
        ],
        "body": """The artificial-intelligence industry's two most consequential private companies have decided, almost simultaneously, that they are ready for the public markets. On June 1, Anthropic — maker of the Claude family of AI models — filed a confidential S-1 registration with the Securities and Exchange Commission, riding a recent funding round that valued it at roughly $965 billion. One week later, on June 8, OpenAI followed with its own confidential filing, targeting a valuation that people familiar with the matter say could exceed $1 trillion.

Together, the two IPOs would create nearly $2 trillion in newly listed AI market capitalisation — a figure that, for context, exceeds the combined value of every company on the Bombay Stock Exchange's Sensex-30 index. Add SpaceX's reported IPO preparations at a $1.75 trillion valuation, and the pipeline of private-to-public tech wealth transferring to retail and institutional investors in 2026-27 approaches $3.6 trillion.

## Two Labs, Two Philosophies

The duelling filings are especially striking because the two companies emerged from the same intellectual lineage but have diverged sharply in philosophy. OpenAI, founded as a non-profit in 2015, converted to a capped-profit structure and then to a full for-profit entity this year, drawing a lawsuit from co-founder Elon Musk and sharp criticism from AI-safety advocates. Under Sam Altman, OpenAI has prioritised speed: launching ChatGPT, building GPT-5, securing a $40 billion funding round, and expanding into hardware and consumer products.

Anthropic, founded in 2021 by former OpenAI researchers Dario and Daniela Amodei, has positioned itself as the "safety-first" alternative. Its Claude models are competitive with GPT-5 on most benchmarks, and the company has attracted major enterprise customers — including Amazon, which has invested heavily in Anthropic through its partnership with AWS. Anthropic's $65 billion fundraise earlier this year, led by a consortium that included Lightspeed and Spark Capital, valued it at $965 billion on an annualised revenue run-rate that sources estimate at $4-5 billion.

The question for public-market investors is whether either valuation makes sense. At $1 trillion, OpenAI would trade at roughly 50 times its estimated $20 billion annual revenue — a multiple that assumes years of hypergrowth in a market where competition from Google, Meta, and open-source alternatives is intensifying. Anthropic's implied multiple is even steeper.

## The Indian Thread

For the Indian diaspora, these IPOs are not abstract financial events. Indian-origin researchers hold senior positions at both labs: OpenAI's technical staff includes several IIT and IISc alumni who helped build the GPT architecture, while Anthropic's safety and alignment teams draw on Indian ML talent that has become the backbone of Silicon Valley's AI workforce.

At the policy level, **Sriram Krishnan** — the Indian-American technology executive who serves as the White House's senior advisor on AI — is helping shape the regulatory framework that will govern how these companies operate post-IPO. His role bridges two worlds: the diaspora's technology expertise and Washington's growing appetite to regulate an industry whose products can generate disinformation, displace workers, and concentrate economic power.

For NRI investors specifically, the IPOs present a familiar dilemma in unfamiliar territory. Indian retail investors have grown accustomed to buying US tech stocks through platforms like Vested and INDMoney; Nvidia, Apple, and Microsoft are already among the most popular holdings. But investing in pre-revenue-clarity AI companies at trillion-dollar valuations carries risks that blue-chip tech does not. The companies' S-1 filings, once made public, will reveal for the first time their actual cost structures — and the staggering compute bills (estimated at over $8 billion annually for OpenAI alone) that are the price of training frontier models.

## Regulation as Wildcard

The timing of these IPOs also intersects with an intensifying global debate about AI governance. The European Union's AI Act is already in force; India is finalising its own framework, which Sriram Krishnan has publicly said should balance innovation with safety. Both companies will need to disclose their compliance strategies — and their lobbying expenditures — in their public filings.

For investors, the regulatory question is not academic. A strict liability regime for AI-generated harms could materially alter the economics of deploying frontier models in healthcare, finance, and government. A permissive regime could accelerate adoption — and revenue — beyond current projections.

What is not in doubt is the magnitude of the moment. Two companies, born from the same research tradition, going public in the same quarter, at valuations that together rival the GDP of France. For Indian engineers building the models, Indian investors considering the stock, and Indian policymakers writing the rules, the dual IPO is a test of whether the AI boom's promise can survive contact with public-market discipline.""",
        "person_name": None,
        "wiki_queries": ["artificial intelligence company headquarters", "OpenAI logo office", "Initial public offering stock exchange"],
        "pexels_query": "stock market IPO technology investment",
        "image_caption": "OpenAI and Anthropic have filed duelling IPO registrations targeting a combined valuation near $2 trillion",
    },
    {
        "headline": "AI Has Now Killed 100,000 Tech Jobs in 2026 — and Indian Workers Are in the Crosshairs",
        "subheadline": "Over 100,000 technology positions have been eliminated in the first five months of this year, with artificial intelligence cited in a surging share of cuts. For H-1B holders, the 60-day clock is ticking.",
        "slug": f"ai-tech-layoffs-100k-h1b-impact-{TODAY.replace('-', '')}",
        "category": "technology",
        "tags": ["tech layoffs", "AI automation", "H-1B visa", "Indian workers", "Meta", "PayPal", "job market 2026"],
        "diaspora_angle": "Indian nationals hold the largest share of H-1B visas in the US technology sector. When layoffs hit, they face a brutal 60-day grace period to find new sponsorship or leave the country — a structural vulnerability that no other demographic in Silicon Valley shares. The surge in AI-driven layoffs is turning this from an individual hardship into a community-wide crisis.",
        "sources": [
            {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/artificial-intelligence/100000-tech-jobs-lost-in-2026-ai-blamed-for-growing-layoffs"},
            {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/policy/technology/3442100/ai-layoffs-2026-rising-share/"},
            {"name": "NDTV Profit", "url": "https://www.ndtvprofit.com/technology/tech-layoffs-surge-66-percent-2026-ai-automation"}
        ],
        "body": """The numbers have crossed a threshold that demands a different kind of conversation. According to data compiled by Layoffs.fyi and corroborated by multiple industry trackers, more than 100,000 technology jobs have been eliminated in the United States in the first five months of 2026. That figure is already two-thirds of the full-year total for 2025 — and the year is not yet half over.

What has changed is not the volume alone but the stated reason. In January, roughly 7 per cent of companies announcing layoffs cited artificial intelligence as a factor in their decision. By May, that figure had risen to nearly 40 per cent. The shift is no longer anecdotal; it is structural.

## The Biggest Cuts

The headline numbers come from companies whose names are familiar to every Indian household with a family member in American tech. **Meta** has cut approximately 8,000 positions this year, part of what Mark Zuckerberg has described as a "year of efficiency" sequel focused on replacing mid-level roles with AI tooling. **PayPal** has eliminated 4,700 jobs, consolidating customer-service and fraud-detection teams as automated systems handle an increasing share of the workload. **Cisco** has cut 4,000 positions, predominantly in its enterprise-networking division, as AI-driven network management reduces the need for human configuration specialists.

Across the sector, the Challenger, Gray & Christmas consultancy reports that technology-sector layoffs are up 66 per cent year-to-date, reaching 123,000 when including companies not captured by Layoffs.fyi's tracker. The acceleration is most pronounced in roles that involve structured, repetitive decision-making — precisely the kind of work that large language models and autonomous agents are increasingly capable of performing.

## The H-1B Trap

For the Indian diaspora, the layoff wave carries a uniquely punishing dimension. Indian nationals account for approximately 72 per cent of all H-1B visas issued in recent years, and they are disproportionately represented in the mid-level software engineering, quality assurance, and IT-services roles most vulnerable to AI-driven cuts.

When an H-1B holder loses their job, they enter a 60-day grace period — two months to find a new employer willing to sponsor their visa, or leave the country. For workers with children in American schools, mortgages on American homes, and spouses whose own work authorisation depends on the primary visa, those 60 days are not a bureaucratic inconvenience. They are a countdown to upheaval.

Immigration attorneys in the Bay Area and Seattle report a surge in consultations from Indian tech workers who have received layoff notices or expect them. The options are limited: find a new sponsor (in a market where many companies have frozen hiring), transfer to an L-1 intra-company visa (if the employer has an Indian office willing to absorb them), apply for "extraordinary ability" O-1 status (a high bar), or begin the process of departure.

The irony is sharp. Many of these workers were brought to the United States specifically to build the AI systems that are now eliminating roles like theirs. The engineer who spent three years training a document-processing model may find that the model's success is the very thing that makes their position redundant.

## The Indian IT Services Ripple

The layoff wave is also reshaping demand for the offshore IT-services sector. When American companies cut internal tech teams, they often simultaneously restructure their outsourcing contracts — sometimes expanding them (to backfill cheaply), sometimes shrinking them (because the AI that replaced the internal team also replaces the outsourced one). The net effect, according to analysts at Gartner and Everest Group, is a structural decline in demand for traditional "body shop" engagements and a simultaneous spike in demand for AI-implementation specialists.

For firms like TCS, Infosys, and Wipro, this is the same transformation-or-die pressure that Microsoft's Agent 365 represents from the vendor side. The companies that can retrain their workforces to build, deploy, and manage AI agents will survive; those that continue to sell human hours for automatable tasks will not.

## What Comes Next

Forecasters at Challenger expect the pace to accelerate in the third quarter, as companies that announced AI investments in early 2026 begin to realise the headcount savings those investments were meant to deliver. The 100,000 figure, sobering as it is, may prove to be a way station rather than a peak.

For Indian tech workers in America — and for the families, communities, and remittance flows that depend on them — the question is no longer whether AI will reshape the labour market. It is whether the institutions that brought them here have any plan for what happens when the work they were brought to do no longer requires a human being to do it.""",
        "person_name": None,
        "wiki_queries": ["H-1B visa United States immigration", "technology layoffs Silicon Valley", "artificial intelligence automation workplace"],
        "pexels_query": "technology workers office layoff corporate",
        "image_caption": "Over 100,000 tech jobs have been cut in 2026, with AI cited as a factor in a growing share of layoffs",
    },
]

# ── main ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print(f"Tech Writer — {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    results = []

    for i, art in enumerate(ARTICLES):
        print(f"\n{'─'*60}")
        print(f"Article {i+1}: {art['headline']}")
        print(f"{'─'*60}")

        # 1. Source image
        print("\n📸 Sourcing image...")
        img_url, img_attr = source_image(
            art["slug"],
            person_name=art.get("person_name"),
            wiki_queries=art.get("wiki_queries"),
            pexels_query=art.get("pexels_query"),
        )

        # 2. Insert article
        print("\n📝 Inserting article...")
        row = {
            "headline": art["headline"],
            "subheadline": art["subheadline"],
            "slug": art["slug"],
            "body": art["body"].strip(),
            "category": "technology",
            "tags": art["tags"],
            "sources": art["sources"],
            "diaspora_angle": art["diaspora_angle"],
            "is_editorial": False,
            "status": "review",
            "image_url": img_url,
            "image_caption": art["image_caption"],
            "image_attribution": img_attr,
            "published_at": f"{TODAY}T09:00:00Z",
        }

        result = sb_insert("p2_articles", row)
        if result:
            results.append({
                "id": result.get("id"),
                "headline": art["headline"],
                "slug": art["slug"],
                "has_image": bool(img_url),
            })
        else:
            results.append({
                "id": None,
                "headline": art["headline"],
                "slug": art["slug"],
                "has_image": False,
                "error": True,
            })

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    success = [r for r in results if r.get("id")]
    failed = [r for r in results if not r.get("id")]
    print(f"✓ Inserted: {len(success)}")
    print(f"✗ Failed:   {len(failed)}")
    for r in results:
        status = "✓" if r.get("id") else "✗"
        img = "📸" if r.get("has_image") else "🚫"
        print(f"  {status} {img} {r['headline'][:60]}...")
        if r.get("id"):
            print(f"       ID: {r['id']}")
            print(f"       Slug: {r['slug']}")

    return 0 if not failed else 1

if __name__ == "__main__":
    sys.exit(main())
