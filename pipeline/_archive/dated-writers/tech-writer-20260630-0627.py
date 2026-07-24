#!/usr/bin/env python3
"""
Tech Writer — June 30, 2026 (06:27 UTC)
Two technology articles for The Videshi:
1. OpenAI hires Prabhjeet Singh as India MD (AI / Indian Tech Leaders)
2. Micron's monster $41.5B quarter under Sanjay Mehrotra (Semiconductors / Indian-Origin CEO)
"""

import json, os, uuid, re, requests
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

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")


# ── Article 1: OpenAI Hires Prabhjeet Singh as India MD ──

article1_body = """OpenAI has named Prabhjeet Singh, the man who ran Uber across India and South Asia for nearly 11 years, as its first Managing Director for the country. Singh will join in September and report to Kiran Mani, the company's Asia Pacific chief. The appointment makes him OpenAI's most senior leader in India — a market Sam Altman's company now calls its second-largest, with more than 100 million weekly ChatGPT users.

The hire is not a soft landing for a departing tech executive. It is a statement about where OpenAI sees its next phase of commercial growth.

## The Uber playbook, repurposed

Singh's mandate at OpenAI reads like a condensed version of what he spent a decade building at Uber: consumer growth, enterprise adoption, strategic partnerships, regulatory engagement, and day-to-day operations. At Uber, he took a ride-hailing startup and stretched it into auto-rickshaws, motorbikes, and shuttles — products designed for a market where a $10 ride is a luxury and a ₹30 auto ride is an everyday transaction.

OpenAI needs the same instinct. ChatGPT's free tier has made it ubiquitous in India, but converting 100 million weekly users into paying customers — or enterprise contracts — requires someone who understands Indian price sensitivity, regulatory caution, and the sheer diversity of use cases in a market where a Bengaluru AI startup and a Tier-3 accounting firm both use the same product.

Singh holds degrees from IIT Kharagpur and IIM Ahmedabad. Before Uber, he was an Associate Partner at McKinsey and began his career on the structured finance desk at Lehman Brothers in London. His path — IIT to global finance to Indian tech operations — mirrors the trajectory of thousands of Indian tech professionals who will be watching this appointment closely.

## Why India, why now

OpenAI opened its first office in New Delhi in November 2025. Mumbai and Bengaluru are next, with offices confirmed for 2026. The company has hired AI deployment engineers, partner directors, and solutions engineers on the ground. It has already struck partnerships with Reliance and Tata Group.

The timing matters. Anthropic's Fable models remain restricted in India, and Google's Gemini — while strong — carries the baggage of a company Indians associate more with search and YouTube than with cutting-edge AI tools. OpenAI's ChatGPT has, somewhat accidentally, become the default AI interface for millions of Indian developers, students, and small businesses. Singh's job is to make that accident intentional.

India also ranks among OpenAI's top five markets for API usage, which means Indian developers are building products on OpenAI's infrastructure at scale. The enterprise opportunity — selling to Indian IT companies, banks, and government bodies — is largely untapped.

## What NRIs should watch

For Indian Americans in tech, the appointment signals two things. First, OpenAI is serious about building a real business in India, not just collecting users. That means partnerships, hiring, and potentially India-specific products — all of which create opportunities for diaspora professionals who straddle both markets.

Second, Singh's appointment continues a pattern of Indian executives being recruited to build AI companies' most important international markets. Between Google, Microsoft, and now OpenAI, India's AI landscape is increasingly shaped by leaders who studied at IITs and IIMs before building careers in Silicon Valley and beyond. The bridge between the two ecosystems is getting shorter.

The deeper question is whether OpenAI will build *for* India or simply *sell to* it. Singh's Uber tenure suggests he understands the difference. At Uber, India wasn't a smaller version of the American product — it was a different product entirely. If he brings the same instinct to OpenAI, India's 100 million ChatGPT users might get something their American counterparts don't."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "OpenAI Just Hired Uber India's Boss to Run Its Second-Largest Market",
    "subheadline": "Prabhjeet Singh, an IIT-IIM alumnus who spent 11 years stretching Uber across auto-rickshaws and motorbikes, will lead OpenAI's India operations from September. The hire signals that India's 100 million ChatGPT users are about to become a real business.",
    "slug": make_slug("openai-prabhjeet-singh-india-md-uber-chatgpt"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "OpenAI's appointment of an IIT-IIM alumnus to lead its second-largest market signals growing opportunities for diaspora professionals who bridge Silicon Valley and India's AI ecosystem.",
    "tags": ["openai", "chatgpt", "india", "ai", "prabhjeet-singh", "uber", "silicon-valley"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/openai-taps-ex-uber-regional-chief-india-leadership-2026-06-27/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/openai-names-prabhjeet-singh-as-managing-director-for-its-india-ops"},
        {"name": "Techlusive", "url": "https://www.techlusive.in/news/openai-prabhjeet-singh-india-managing-director"},
        {"name": "The Bridge Chronicle", "url": "https://www.thebridgechronicle.com/technology/openai-appoints-former-uber-india-chief-prabhjeet-singh-as-its-first-india-managing-director"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Sam_Altman_CropEdit_James_Tamim.jpg/1280px-Sam_Altman_CropEdit_James_Tamim.jpg",
    "image_caption": "OpenAI CEO Sam Altman, whose company has named India its second-largest market",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip()
}


# ── Article 2: Micron's Monster Quarter Under Sanjay Mehrotra ──

article2_body = """Micron Technology just posted the kind of quarter that memory chipmakers have spent decades dreaming about — and that their investors have spent decades learning to distrust.

Revenue hit $41.5 billion for the three months ending May 28, a 346% increase from the same period last year. Earnings per share came in at $25.11, crushing Wall Street's estimate of $21.39 by a wide margin. Net income reached $28.2 billion, up from $1.9 billion a year ago. The net margin: 68%.

At the centre of all of this is Sanjay Mehrotra, the Kanpur-born CEO who co-founded SanDisk and has spent the last seven years turning Micron from a commodity chipmaker into the only American manufacturer of high-bandwidth memory (HBM) — the component that AI simply cannot function without.

## The HBM supercycle

The numbers are staggering because the market they reflect is structurally different from anything the memory industry has seen. NVIDIA's AI processors — the Blackwell generation shipping now and the Vera Rubin platform entering production this fall — require enormous quantities of HBM to function. Each NVIDIA Vera Rubin NVL72 rack system contains 72 GPUs, and each GPU needs multiple stacks of HBM. Micron, Samsung, and SK Hynix are the only three companies in the world that can make it.

Mehrotra told investors that demand "significantly exceeds industry supply" and that tight conditions will persist beyond 2027. AI-driven demand across data centres, consumer devices, and automotive chips is colliding with structural supply constraints that cannot be resolved quickly. Memory fabs take years to build and billions to equip.

The market's response was telling: a 12% after-hours surge on the earnings print, followed by a pullback as investors wrestled with the question that haunts every memory cycle — can numbers this good last?

## $22 billion in locked-in commitments

Micron's answer to the durability question was its most striking disclosure: 16 strategic customer agreements worth $22 billion, structured as take-or-pay commitments with cash deposits and pricing floors. Customers — including NVIDIA — must either buy the chips or hand over cash. Remaining performance obligations across these deals total roughly $100 billion.

This is new territory for memory. Historically, memory chips were commodities — interchangeable, ruthlessly price-competitive, and subject to savage boom-bust cycles. Mehrotra is trying to rewrite that script by turning Micron into a strategic partner whose factory expansions customers must underwrite to lock in supply.

The fourth-quarter guidance reinforced the thesis: revenue of $49–51 billion (against consensus of $41.6 billion) and gross margins approaching 81%. For a memory company, an 81% gross margin is not a data point. It is an identity crisis.

## The India connection that matters

Mehrotra was born in Kanpur and studied at the Birla Institute of Technology in Pilani before moving to the United States for graduate work at Stanford. He co-founded SanDisk in 1988 — the company that helped pioneer flash storage — and led it until its acquisition by Western Digital in 2016.

But his India story has a second chapter. Micron is building a $2.75 billion chip assembly and testing plant in Sanand, Gujarat — its first major facility in India. The plant, backed by India's Semiconductor Mission, is expected to create thousands of engineering jobs and serve as an entry point for India into the global semiconductor supply chain.

For the tens of thousands of Indian engineers working across the American semiconductor industry — at Micron, Intel, Qualcomm, Broadcom, and AMD — Mehrotra's quarter is a validation of a career bet. The AI boom has turned memory from a cyclical afterthought into the bottleneck of the entire AI stack. And the man running the only American company that can ease that bottleneck was born 500 kilometres from Delhi.

## What NRIs should watch

Apple just raised MacBook and iPad prices by as much as 42% because of memory costs, telling Reuters it had "never seen a component price increase this much, this quickly." That is the flip side of Micron's 68% margin: the memory shortage is real enough to reshape consumer prices.

NRI investors who hold Micron — the stock has tripled in 2026 — face the classic memory question: is this cycle different, or is it just bigger? Mehrotra's take-or-pay agreements suggest structural change. The $100 billion in remaining obligations is not a forecast; it is a contract. But even Mehrotra acknowledged that supply will "improve gradually" by 2028, and South Korea's SK Hynix has announced plans to raise $29 billion for a US listing and capacity expansion.

The memory industry's history is littered with cycles that felt permanent until they weren't. But Mehrotra has never had this hand before — a product that AI cannot do without, customers willing to pay for supply security, and a factory going up in Gujarat. For now, the house advantage belongs to the man from Kanpur."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Mehrotra's Micron Just Posted a $41.5 Billion Quarter. The Man from Kanpur Has Never Had a Hand This Good.",
    "subheadline": "Revenue up 346%, margins at 68%, and $22 billion in locked-in customer commitments. The Indian-American CEO who co-founded SanDisk is running the only American company that makes the memory chips AI cannot function without.",
    "slug": make_slug("micron-mehrotra-41-billion-quarter-hbm-ai-memory"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Indian-American CEO Sanjay Mehrotra, born in Kanpur and educated at BITS Pilani, runs the only US maker of the memory chips powering the AI boom. His company is also building a $2.75B plant in Gujarat — creating jobs and entry points for India's semiconductor ambitions.",
    "tags": ["micron", "sanjay-mehrotra", "semiconductors", "hbm", "ai-chips", "nvidia", "india-semiconductor", "nri-investors"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/micron-forecasts-strong-quarterly-results-soaring-memory-chip-demand-2026-06-25/"},
        {"name": "Reuters - Breakingviews", "url": "https://www.reuters.com/breakingviews/microns-rise-strains-tech-giants-credulity-2026-06-26/"},
        {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NASDAQ/MU/earnings/"},
        {"name": "TradingNews", "url": "https://www.tradingnews.com/news/micron-stock-price-forecast"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg",
    "image_caption": "Micron CEO Sanjay Mehrotra, the Kanpur-born co-founder of SanDisk",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip()
}


# ── Insert articles ──

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
