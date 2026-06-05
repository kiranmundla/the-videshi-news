#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-05 03:00 UTC run"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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

# ──────────────────────────────────────────────────────────────
# ARTICLE 1: Indian States at Computex
# ──────────────────────────────────────────────────────────────

art1_body = """Five of India's most industrialised states sent senior officials to Taipei this week with a single message: the next chapter of the global electronics supply chain should be written, at least partly, in India.

The pitch took place at the 2026 Taiwan–India Business Forum, held on the sidelines of Computex, the annual technology trade show that has become the world's most important stage for semiconductor and AI hardware announcements. Gujarat, Andhra Pradesh, Karnataka, Tamil Nadu, and Uttar Pradesh each made their case to Taiwanese manufacturers weighing where to diversify production as geopolitics reshuffles supply chains.

## Andhra Pradesh Goes After Packaging

The boldest move came from Andhra Pradesh. Speaking on the sidelines of Computex, state officials described a strategy that bypasses the multi-billion-dollar gamble of building a full fabrication plant and instead targets semiconductor packaging — the final, high-value step where chips are assembled, tested, and prepared for customers. It is the segment where India can enter the supply chain fastest, with the lowest barrier to entry, and where global demand is surging because of advanced packaging techniques like chiplets and fan-out embedded bridges that underpin every modern AI processor.

Andhra Pradesh is not alone in this calculation. Gujarat already hosts Micron's assembly, test, marking, and packaging (ATMP) facility in Sanand and the Tata-Powerchip fab project in Dholera. The pull of Micron's presence has begun to create its own gravity: South Korean IC substrate manufacturer Simmtech recently announced it would set up a facility in Gujarat, drawn specifically by the cluster forming around Micron's plant.

## From Design Houses to Pilot Lines

The timing of India's Computex offensive is not accidental. Back home, a new generation of Indian semiconductor startups is crossing the bridge from PowerPoint to silicon. Companies like Netrasemi, Mindgrove Technologies, and AGNIT Semiconductors have moved from research into customer sampling and pilot production — the stage where a design startup either proves it can ship or stalls in the lab.

Three of these startups — VerveSemi, AGNIT Semiconductors, and Netrasemi — have been selected to represent India at Bharat Innovates 2026, a deep-tech showcase running from June 14 to 16 in Nice, France. VerveSemi designs chips for AI edge inference. AGNIT works on gallium nitride (GaN) semiconductors for power electronics and defence. Netrasemi builds vision processors for autonomous systems.

## The $210 Billion Backdrop

India's states are pitching manufacturing at a moment when the domestic digital infrastructure story has turned genuinely big. Reliance Jio has committed $110 billion over seven years to AI-ready data centres. Adani Group has pledged $100 billion by 2035 for renewable-powered compute facilities. AWS is investing $7 billion in Telangana alone. India's total live data centre capacity has grown from 296 megawatts in 2016 to over 1.6 gigawatts in 2025, and the pipeline of committed projects now exceeds 8 gigawatts.

All of those data centres need chips. If India can package even a fraction of them domestically, the economics of the entire electronics value chain shift.

## Why NRIs Should Watch This

For Indian professionals in the semiconductor industry — and there are tens of thousands working at TSMC, Intel, Qualcomm, AMD, and Micron — the message is no longer aspirational. India is not merely talking about chips. States are competing for foundry business at the world's premier chip conference. Korean suppliers are setting up shop in Gujarat to be near Micron. Chip design startups are taping out their first silicon.

The return-to-India career calculus, once limited to software and fintech, now includes the full semiconductor stack. Whether you are an engineer at TSMC's Arizona fab wondering about Tata's Dholera timeline, or an NRI investor tracking where the next tranche of packaging contracts will land, the signal from Computex this week was unambiguous: India is no longer on the waiting list."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Five Indian States Crashed Computex. The Chip Supply Chain Noticed.",
    "subheadline": "Gujarat, Andhra Pradesh, Karnataka, Tamil Nadu, and Uttar Pradesh pitched Taiwanese chipmakers at the world's biggest tech expo. One state is betting everything on semiconductor packaging.",
    "slug": make_slug("five-indian-states-computex-semiconductor-packaging-pitch"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Tens of thousands of Indian semiconductor professionals work at TSMC, Intel, Qualcomm, AMD, and Micron. India's chip push is creating a realistic return-to-India career path beyond software for the first time, plus investment opportunities in semiconductor manufacturing.",
    "tags": ["semiconductor", "india-chip-mission", "computex-2026", "andhra-pradesh", "silicon-valley"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "DIGITIMES Asia", "url": "https://www.digitimes.com/news/a20260604PD203/india-semiconductor-computex-taiwan.html"},
        {"name": "DIGITIMES Asia", "url": "https://www.digitimes.com/news/a20260604PD205/andhra-pradesh-semiconductor-packaging.html"},
        {"name": "YourStory", "url": "https://yourstory.com/2026/06/3-indian-semiconductor-startups-france-chip-story"},
        {"name": "Knight Frank India / IANS", "url": "https://www.ianslive.in/news/ai-boom-drives-indias-data-centre-growth-leasing-crosses-2-gw-20260602"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/how-aws-microsoft-google-adani-and-reliance-are-driving-indias-data-centre-boom/article69508743.ece"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/5118462/pexels-photo-5118462.jpeg",
    "image_caption": "A semiconductor cleanroom, the kind of facility Indian states are competing to attract",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": art1_body.strip(),
}

# ──────────────────────────────────────────────────────────────
# ARTICLE 2: Palantir-Google Cloud Partnership
# ──────────────────────────────────────────────────────────────

art2_body = """Palantir Technologies walked into its tenth annual AIPCon developer conference on Thursday and walked out with its biggest platform partnership yet: a deep, multi-layered integration with Google Cloud that puts Palantir's Foundry and AIP tools directly onto Google Cloud Marketplace and wires them into BigQuery, Google's Knowledge Catalog, and the Gemini family of AI models.

The man who brokered the architecture is Akshay Krishnaswamy, Palantir's Chief Architect and one of the most senior Indian-origin technologists at a company valued at over $340 billion.

"Our partnership with Google Cloud marries the years of investments that customers have made into Google's Knowledge Catalog, BigQuery, and Cloud Storage with the operational force of Foundry and AIP," Krishnaswamy said in the official announcement. The goal, he added, is to let enterprises "unleash Gemini alongside their Ontology-powered AI strategy."

## What the Deal Actually Means

Strip away the jargon and this is a logistics story. Palantir's core product, Foundry, takes messy real-world data — supply chains, insurance claims, military logistics, factory floors — and organises it into an "Ontology," a live digital model of how an organisation's assets, people, and processes relate to each other. Google Cloud provides the raw storage, compute, and increasingly powerful AI models. Until now, enterprises had to choose between the two ecosystems or stitch them together manually.

The new deal creates two-way data federation between BigQuery and Foundry, two-way semantic exchange between Google's Knowledge Catalog and Foundry's Ontology, and deep connectivity between Gemini and Palantir's AIP — the layer that lets organisations deploy AI agents into actual business workflows, not just chatbots.

For an enterprise CIO, particularly at the kind of Fortune 500 company that already runs on Google Cloud, this removes a major integration headache and makes Palantir's tools a click away on the Marketplace.

## The Indian Leadership Layer

Krishnaswamy is not the only Indian-origin executive shaping Palantir's trajectory. Shyam Sankar, the company's Chief Technology Officer, has been a driving force behind Palantir's pivot from a government-intelligence contractor to one of the fastest-growing enterprise AI platforms in the world. Sankar, born to Indian immigrant parents, has been with Palantir for over 15 years and was instrumental in launching AIP — the product line that fuelled Palantir's 85 per cent year-over-year revenue growth in Q1 2026.

Together, Krishnaswamy and Sankar occupy the two most important technical roles at a company whose software now runs inside the US Department of Defence, the NHS, Airbus, and, as of Thursday, Kirkland & Ellis, the world's largest law firm by revenue, which announced a multi-year deal to build an AI-powered private equity fundraising platform on Palantir.

## The Numbers Are Hard to Ignore

Palantir reported $1.63 billion in Q1 revenue with a 60 per cent adjusted operating margin — a profitability figure that makes most enterprise software companies look bloated. US commercial revenue jumped 133 per cent to $595 million. Total remaining deal value sits at $11.8 billion. Management has guided for roughly $7.66 billion in full-year 2026 revenue.

Among the companies showcased at AIPCon 10 was Accenture, which employs more Indian-origin professionals than almost any other global consulting firm and has become one of Palantir's most visible implementation partners.

## Why This Matters for the Diaspora

For Indian tech professionals, Palantir represents a different kind of opportunity than the traditional FAANG path. It is smaller, more secretive, and pays extraordinarily well — but it also demands the kind of systems-thinking that Indian engineering graduates, particularly those with backgrounds in operations research and complex systems, tend to excel at.

More broadly, the Krishnaswamy-Sankar leadership axis at Palantir illustrates a pattern that extends well beyond the familiar Pichai-Nadella narrative. Indian-origin technologists are not merely running the companies that build AI. They are architecting the platforms that other companies use to deploy it. That is a distinction worth noting, because as AI moves from model training to enterprise operations, the architects matter more than the model makers."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Palantir's Google Cloud Deal Has an Indian Architect. So Does the Company.",
    "subheadline": "At AIPCon 10, Palantir's Indian-origin Chief Architect Akshay Krishnaswamy brokered the firm's deepest platform partnership yet. CTO Shyam Sankar built the AI engine behind it.",
    "slug": make_slug("palantir-google-cloud-aipcon-krishnaswamy-sankar-indian"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian-origin leaders hold the two most important technical roles at Palantir — Chief Architect Akshay Krishnaswamy and CTO Shyam Sankar — shaping AI infrastructure used by governments and enterprises worldwide. Accenture, a top Indian-professional employer, is a key Palantir partner.",
    "tags": ["palantir", "google-cloud", "ai-enterprise", "indian-tech-leaders", "aipcon"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "BusinessWire / Palantir", "url": "https://www.businesswire.com/news/home/20260604624637/en/Palantir-Announces-Availability-on-Google-Cloud-Marketplace"},
        {"name": "CoinCentral", "url": "https://coincentral.com/palantir-pltr-stock-google-cloud-partnership-aipcon-2026/"},
        {"name": "StockTwits", "url": "https://stocktwits.com/news/PLTR/why-is-pltr-stock-rising-today"},
        {"name": "Zacks Investment Research", "url": "https://www.zacks.com/stock/news/2468513/palantir-technologies-pltr-up-12-since-last-earnings-report"}
    ]),
    "score_total": 75,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg",
    "image_caption": "Server racks in a modern data centre — the infrastructure Palantir and Google Cloud aim to power with AI",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": art2_body.strip(),
}

# ──────────────────────────────────────────────────────────────
# PUBLISH
# ──────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted at {now}")
