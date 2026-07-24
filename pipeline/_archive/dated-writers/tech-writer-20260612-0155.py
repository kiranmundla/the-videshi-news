#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-12 01:55 PDT run"""
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


# ──────────────────────────────────────────────
# ARTICLE 1: India AI Law
# ──────────────────────────────────────────────

art1_body = """India's IT minister Ashwini Vaishnaw has said the quiet part out loud: the country's existing digital laws were not built for AI, and a new legislative framework is now on the table.

Speaking at the India Global Innovation Connect 2026 in New Delhi this week, Vaishnaw acknowledged that the Information Technology Act — drafted in 2000 and amended most recently through rules changes — cannot adequately govern a world where generative models produce synthetic content at industrial scale. "The world of AI is very different from the IT Act era," he said. A dedicated AI law, he suggested, may be unavoidable.

## The patchwork so far

India does not yet have a standalone AI statute. What it has is a series of increasingly aggressive patches to the IT (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021.

The most recent amendments formally define "AI-generated" and "synthetically-generated information" for the first time in Indian law — covering any audio, visual, or audiovisual content created or altered by AI that appears authentic. Routine editing, accessibility improvements, and good-faith educational work are explicitly carved out.

Platforms including X and Instagram must now remove flagged deepfake content within three hours if directed by a court or competent authority. The government has also proposed continuous, visible labelling of AI-generated content throughout its display duration — a requirement that, if finalised, would go further than the EU AI Act's transparency mandates in some respects.

## Why the existing framework falls short

The Digital Personal Data Protection Act (DPDP), passed in 2023, addresses privacy and consent but says nothing about model accountability, training data governance, algorithmic bias, or AI-driven harms. That gap is widening as India becomes both a major AI deployment market and a significant hub for AI talent and development.

Sanjeev Sanyal, a member of the Prime Minister's Economic Advisory Council, framed the challenge at the same summit: "AI is a non-deterministic complex system — and we need to regulate it like one. What works is skin in the game: clear accountability, identifiable actors who bear the consequences of failure."

The challenge for New Delhi is drafting rules robust enough to matter without throttling the country's 2,200 Global Capability Centres and its $315-billion IT sector — both of which are racing to embed AI into everything from customer service to drug discovery.

## What this means for Indian tech professionals abroad

For the estimated 300,000-plus Indian tech workers in the United States alone, a new Indian AI law matters in ways that are easy to underestimate.

First, the compliance dimension. Engineers and product managers at Google, Microsoft, Meta, and Amazon who build products serving Indian users will need to navigate whatever accountability and labelling requirements New Delhi eventually codifies. India is already one of the largest user bases for virtually every major platform.

Second, the deepfake problem is personal. Diaspora communities have been disproportionately targeted by AI-generated scam videos featuring public figures — a trend the three-hour takedown mandate is specifically designed to combat. Vaishnaw defended the crackdown: "Wherever these fake videos are, it is a duty and responsibility for the government to ensure that any deepfake video propagating false information is removed."

Third, for NRIs considering return-to-India career moves or launching AI startups in Bengaluru or Hyderabad, the regulatory landscape will shape which business models are viable. A principles-based law could attract investment. An overly prescriptive one could push founders to Singapore or Dubai.

India is also set to host the AI Impact Summit 2026 — the Global South's first major AI governance event — bringing together 100-plus countries to discuss safety, ethics, and regulatory frameworks. The outcomes could influence India's own legislative direction.

The question is no longer whether India will regulate AI. It is whether the regulation will be written by people who understand the technology well enough to avoid killing the industry they are trying to govern."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "India Says Its Digital Laws Were Not Built for AI. A New Statute Is Coming.",
    "subheadline": "IT Minister Vaishnaw signals a standalone AI law as patchwork deepfake rules expose gaps in the 25-year-old IT Act framework.",
    "slug": make_slug("india-ai-law-vaishnaw-deepfake-regulation"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Indian tech workers at US firms building products for Indian users will face new AI compliance and labelling mandates, while NRI founders weigh whether India's regulatory direction helps or hinders AI startups.",
    "tags": ["ai-regulation", "india-policy", "deepfakes", "it-act", "diaspora-tech"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Exchange4Media", "url": "https://www.exchange4media.com/digital-news/ai-era-may-need-a-new-rulebook-says-vaishnaw-as-india-reassesses-digital-laws-141933.html"},
        {"name": "Inc42", "url": "https://inc42.com/buzz/ai-world-very-different-from-it-act-era-new-law-required-ashwini-vaishnaw/"},
        {"name": "LiveMint", "url": "https://www.livemint.com/news/india/world-of-ai-is-very-different-ashwini-vaishnaw-sees-need-for-new-ai-law-in-india-11749541380277.html"},
        {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/india-may-need-new-ai-law-as-technology-evolves/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/35/Ashwini_Vaishnaw_cropped.jpg",
    "image_caption": "India's IT Minister Ashwini Vaishnaw at a government event",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}


# ──────────────────────────────────────────────
# ARTICLE 2: IN-SPACe funds 3 space startups
# ──────────────────────────────────────────────

art2_body = """For the first time in its history, India's space regulator has put government money directly into private startups — and the bets it has chosen tell you exactly where New Delhi thinks the next frontier lies.

The Indian National Space Promotion and Authorisation Centre (IN-SPACe) announced this week that three companies have been selected under its new Technology Adoption Fund (TAF): Bengaluru-based Astrobase Space Technologies, which will develop an 800 kilonewton-class closed-cycle reusable liquid rocket engine; SatSure Analytics, also in Bengaluru, which will build an AI-powered large Earth observation model called Dhaarini; and Hyderabad's TM2SPACE Technologies (TakeMe2Space), which will design AI-enabled star tracker systems for CubeSats and larger satellites.

Each project is capped at ₹25 crore (roughly $2.6 million). That is modest by global space-venture standards, but the signal matters more than the cheque: India's government is no longer just opening the door for private space companies. It is now co-investing alongside them.

## The three bets

**Astrobase Space Technologies** is building a high-thrust reusable rocket engine that could power next-generation Indian launch vehicles. Co-founded by former ISRO propulsion engineer Devakumar Thammisetty and CoinDCX co-founder Neeraj Khandelwal in 2024, the company is targeting the segment of the market where SpaceX's Merlin engine dominates. An 800 kN-class engine in India would significantly expand the country's ability to launch heavier payloads — and do so at a fraction of the cost of disposable rockets.

**SatSure Analytics**, founded in 2017, is perhaps the most commercially advanced of the three. Its Dhaarini model will convert satellite and drone data into actionable intelligence tailored to Indian conditions — monsoon patterns, crop health, urban sprawl, infrastructure stress. "Earth observation is moving from project-specific analytics to reusable intelligence infrastructure," said co-founder Rashmit Singh Sukhmani. SatSure separately secured a 246 million rupee grant from India's space regulator this week, reinforcing its position as the country's leading geospatial AI play.

**TM2SPACE Technologies** is attacking a less glamorous but critical bottleneck: satellite navigation. Its AI-enabled star tracker systems will improve orbital positioning for small satellites, a capability gap that currently forces many Indian satellite operators to rely on imported hardware.

## Why it took this long

IN-SPACe was established in 2020 to authorise and promote private participation in India's space sector, which had been an ISRO monopoly for six decades. But for years, its role was largely regulatory — approving launch licences, clearing spectrum allocations. The TAF scheme, which was designed over the past year with investment caps and milestone-linked disbursements, represents the body's first direct financial intervention.

The expert committee that evaluated applications included representatives from ISRO, DPIIT, DST, academia, and industry. Pawan Goenka, IN-SPACe's chairman, said the programme aims to "bridge the gap between early-stage development and commercial deployment."

India has also launched a ₹1,000 crore ($105 million) fund to help space startups scale, and the broader policy environment has shifted decisively. Private companies can now build and launch rockets, operate satellite constellations, and sell Earth observation data commercially — activities that were unthinkable a decade ago.

## The diaspora connection

India's private space sector is increasingly powered by NRI talent and capital. Several founders in the ecosystem — including Skyroot Aerospace's team and Agnikul Cosmos' Srinath Ravichandran — have deep connections to the global Indian diaspora. Venture capital from US-based Indian investors has been flowing into the sector, and the startups themselves are building products with global customers in mind.

For NRIs in aerospace engineering, remote sensing, and AI, the TAF scheme creates a new incentive to engage with India's space economy — whether as founders, investors, or technical advisors. Astrobase's co-founder coming from ISRO, and another from crypto exchange CoinDCX, is itself a signal of how India's startup ecosystem is cross-pollinating in unexpected ways.

The ₹25 crore cap per project will not build a rocket. But it may build the confidence — and the track record — that attracts the next round of funding that does."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Space Regulator Puts Government Money Into Startups for the First Time",
    "subheadline": "IN-SPACe selects three companies — building reusable rockets, AI Earth observation, and satellite navigation — under its first-ever direct investment programme.",
    "slug": make_slug("in-space-taf-startups-satsure-astrobase-rockets"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "India's private space sector is increasingly powered by NRI talent and capital, with the government's first direct startup investment creating new opportunities for diaspora engineers and investors in aerospace and geospatial AI.",
    "tags": ["indian-space", "isro", "in-space", "satsure", "startups", "earth-observation"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-satsure-bags-26-million-grant-build-ai-powered-earth-observation-models-2026-06-11/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/in-space-funds-3-startups-to-develop-reusable-rocket-engine-ai-space-model-and-star-tracker-technology/article69677543.ece"},
        {"name": "Inc42", "url": "https://inc42.com/buzz/in-space-funds-three-spacetech-startups-under-taf/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/60132/pexels-photo-60132.jpeg",
    "image_caption": "A satellite in orbit above Earth's coastline, captured from space",
    "image_attribution": "Pexels",
    "body": art2_body.strip()
}


# ──────────────────────────────────────────────
# ARTICLE 3: AI Infrastructure $1 Trillion
# ──────────────────────────────────────────────

art3_body = """The world will spend more than one trillion dollars on data centre infrastructure this year. That is not a forecast from an enthusiastic startup founder. It is a revised estimate from Dell'Oro Group, the industry's most-cited research firm, and the number went up, not down, after first-quarter 2026 results came in.

Behind the headline figure: the four largest US cloud providers — Amazon, Google, Meta, and Microsoft — increased their data centre capital expenditure by 78 per cent year-on-year. Memory and storage costs surged, pushing server system prices higher across the board. And the second half of 2026 is expected to accelerate further as NVIDIA begins shipping its next-generation Rubin systems and hyperscalers refresh their custom accelerator platforms.

If you work in technology — and particularly if you are an Indian engineer at one of these companies — this spending wave is rewriting the job market, the investment landscape, and the geopolitics of compute in real time.

## The private equity flood

The most striking development this week was not in Silicon Valley but in the boardrooms of private equity. On Thursday, KKR announced the launch of Helix Digital Infrastructure, a new company backed by $10 billion in committed capital from KKR, NVIDIA, the Kuwait Investment Authority, and energy provider Vistra. Former Amazon Web Services CEO Adam Selipsky will lead the venture. NVIDIA is a "cornerstone strategic partner."

Two days earlier, Broadcom, Apollo Global Management, and Blackstone announced a $35 billion platform to deploy Broadcom chips across AI data centre fleets, with the initial investment facilitating Anthropic's planned expansion of more than 1 gigawatt of compute capacity this year.

The pattern is unmistakable. AI infrastructure has become too capital-intensive for even the largest tech companies to build alone. The hyperscalers need private capital. Private equity needs returns in an era when traditional real estate and retail are struggling. Data centres — with their long-term leases, predictable power draws, and insatiable demand — are the marriage of convenience.

## Where India fits

India has emerged as the breakout destination in this global buildout. This week alone, Meta signed its first AI data centre deal in the country — a 168-megawatt facility in Jamnagar, Gujarat, to be built and operated by Reliance Industries. The deal expands a relationship that began with a $5.7 billion investment in Jio Platforms in 2020 and a $100 million AI joint venture last year.

Reliance and Adani have committed roughly $210 billion combined to AI infrastructure over seven years. Blackstone-backed AirTrunk announced $30 billion for 5 gigawatts of capacity by 2030. Microsoft, Amazon, Google, and OpenAI have all announced India-specific cloud and AI infrastructure investments.

New Delhi is sweetening the pot with tax exemptions through 2047 for foreign cloud providers that run overseas workloads from Indian data centres. The country's data centre market is projected to nearly double to $13.1 billion by 2034, according to IMARC Group.

## Why Indian tech workers should pay attention

For the hundreds of thousands of Indian engineers at Amazon, Google, Microsoft, and Meta, this spending surge has direct implications.

On the upside, AI infrastructure is creating new roles — in hardware design, data centre operations, thermal management, power systems, and the networking that stitches it all together. The demand for engineers who understand both AI workloads and physical infrastructure is outstripping supply. Micron, led by Indian-American CEO Sanjay Mehrotra, is at the centre of this boom as the primary supplier of high-bandwidth memory for NVIDIA's Rubin platform.

On the risk side, the same companies pouring billions into data centres are simultaneously restructuring their workforces around AI. The question for every tech worker is whether the infrastructure buildout creates more jobs than AI automation eliminates — and on what timeline.

For NRI investors, the AI infrastructure trade is no longer just NVIDIA and a prayer. It now spans memory (Micron), networking (Arista, Broadcom), power (Vistra), private equity platforms (KKR, Blackstone), and India-specific plays like Reliance and Adani's infrastructure bets.

The trillion-dollar number is not the ceiling. Dell'Oro expects the four major hyperscalers' capital budgets to exceed $750 billion in 2026 alone, with the figure crossing $1 trillion in 2027. The infrastructure beneath every AI chatbot, coding assistant, and autonomous agent is being built right now — and an outsized share of the engineers, capital, and ambition behind it is Indian."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "The World Will Spend $1 Trillion on Data Centres This Year. The Real Story Is Who's Writing the Cheques.",
    "subheadline": "KKR and NVIDIA launch a $10 billion AI infrastructure venture as global data centre capex crosses the trillion-dollar mark — with India emerging as the breakout destination.",
    "slug": make_slug("data-center-capex-trillion-kkr-nvidia-helix-india"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Indian engineers at hyperscalers face both opportunity and disruption as $1T+ in data centre spending reshapes the tech job market, while NRI investors gain exposure through India's explosive infrastructure buildout via Reliance, Adani, and global PE platforms.",
    "tags": ["data-centers", "ai-infrastructure", "kkr", "nvidia", "india-tech", "investment"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Barron's", "url": "https://www.barrons.com/articles/kkr-nvidia-kuwait-ai-infrastructure-helix-data-centers-36b89c3d"},
        {"name": "Dell'Oro Group via Morningstar", "url": "https://www.morningstar.com/news/pr-newswire/20260610ny12769/ai-infrastructure-buildouts-and-memory-cost-inflation-drove-data-center-capex-higher-in-1q-2026-according-to-delloro-group"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/10/meta-signs-first-ai-data-center-deal-in-india-with-reliance/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/meta-deepens-partnership-with-ambanis-reliance-with-ai-data-centre-2026-06-11/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg",
    "image_caption": "Server racks inside a modern data centre facility",
    "image_attribution": "Pexels",
    "body": art3_body.strip()
}


# ──────────────────────────────────────────────
# Insert all articles
# ──────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
