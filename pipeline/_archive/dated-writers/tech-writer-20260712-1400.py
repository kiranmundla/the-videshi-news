#!/usr/bin/env python3
"""
Technology writer — 2026-07-12 afternoon batch
Inserts 3 fresh technology articles into Supabase p2_articles.
"""

import json
import os
import sys
import uuid
import re
from datetime import datetime, timezone

import requests
from pathlib import Path

# ── Load env ──────────────────────────────────────────────────────────
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

NOW = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

# ── Article definitions ───────────────────────────────────────────────

articles = [
    # ──────────────────────────────────────────────────────────────────
    # Article 1: Mercor AI
    # ──────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "slug": "mercor-ai-20-billion-valuation-india-invisible-ai-workforce-20260712",
        "headline": "Mercor Eyes $20 Billion Valuation as India's Invisible AI Workforce Powers Silicon Valley",
        "subheadline": "The AI data-labeling startup founded by Indian-American Adarsh Hiremath hit $2 billion in annual revenue — and its largest talent pool remains in India",
        "category": "technology",
        "vertical": "technology",
        "status": "review",
        "is_editorial": False,
        "body": """The artificial intelligence boom has produced an unlikely kingmaker: a startup founded by three 22-year-old college dropouts that is quietly assembling the world's largest army of expert knowledge workers — and India sits at the heart of its operation.

Mercor, the San Francisco-based AI training company co-founded by Indian-American Adarsh Hiremath, is in early discussions to raise fresh capital at a valuation of approximately $20 billion, according to Bloomberg. The potential round would double its valuation from less than a year ago, when it closed a $350 million Series C at $10 billion in October 2025.

The numbers behind the surge are staggering. Chief Executive Brendan Foody confirmed the company has reached $2 billion in annualised revenue — a figure that doubled from $1 billion in just four months. Mercor now manages over 300,000 expert contractors globally, paying an average of $85 per hour, and disburses nearly $1.5 million in payments every single day.

## The Indian Connection

What few outside the industry appreciate is how central India remains to Mercor's story. The company was originally conceived to connect freelance programmers in India with American companies. Hiremath, whose parents emigrated from Karnataka, built the initial AI platform to interview Indian software developers and match them with Silicon Valley hiring managers.

While Mercor has since expanded into data labeling for AI labs like OpenAI, Anthropic, and Nvidia, India remains its largest single talent source. The country's deep bench of software engineers, data scientists, and domain experts — comfortable working across time zones and at globally competitive rates — gives Mercor a structural advantage its competitors struggle to replicate.

"The knowledge in an employee's head belongs to the employee," Foody has argued, defending the model that recruits consultants, lawyers, bankers, and doctors to test and refine AI models through human-in-the-loop feedback.

## Youngest Self-Made Billionaires

Hiremath, Foody, and co-founder Surya Midha met as high school debate teammates at Bellarmine College Preparatory in the Bay Area. All three dropped out of college and received Thiel Fellowships — the programme created by venture investor Peter Thiel that funds companies started by college dropouts. At 22, they became the youngest self-made billionaires in the world when Mercor hit $10 billion.

Their timing was impeccable. When Meta acquired a 49 per cent stake in rival Scale AI for $14.3 billion in June 2025, effectively compromising Scale's neutrality, major AI labs scrambled for alternative data partners. Mercor stepped into the vacuum. "It just doesn't happen too often in startups where your biggest competitor gets torpedoed overnight," Hiremath told Forbes.

## Growing Pains and Security Concerns

The meteoric rise has not been without turbulence. In late March 2026, Mercor was hit by a supply-chain attack involving the LiteLLM software package, potentially exposing up to four terabytes of internal data and contractor personally identifiable information. The breach triggered multiple class-action lawsuits and a temporary pause in work from Meta, one of its largest clients.

Mercor hired Sundeep Jain, Uber's former chief product officer, as its first president in May 2025 to bring operational maturity to the fast-scaling organisation. The company now employs over 300 people at its headquarters in San Francisco's 181 Fremont tower.

## What NRIs Should Watch

For the Indian diaspora, Mercor represents a fascinating inflection in the tech labour market. Thousands of Indian professionals — from IIT graduates coding in Bengaluru to physicians in Hyderabad — are earning substantial incomes by training the very AI systems that will reshape their industries. The model challenges the traditional narrative of Indian tech workers needing H-1B visas to access Silicon Valley opportunities; many contribute remotely, on their own terms.

The $20 billion valuation talks remain preliminary, and there is no certainty the round will close at that level. But the trajectory is clear: India's knowledge workers are the invisible engine behind the AI revolution, and an Indian-American founder is building the company that connects them to it.""",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Data_annotators_labeling_data_by_Nacho_Kamenov_%26_Humans_in_the_Loop.jpg/1280px-Data_annotators_labeling_data_by_Nacho_Kamenov_%26_Humans_in_the_Loop.jpg",
        "image_caption": "Data annotators labeling training data for AI systems at a labeling facility",
        "image_attribution": "Nacho Kamenov & Humans in the Loop, CC BY-SA 4.0, via Wikimedia Commons",
        "sources": json.dumps([
            {"name": "Bloomberg", "url": "https://www.bloomberg.com/news/articles/2026-07-11/ai-startup-mercor-seeks-20-billion-valuation"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/mercor-raises-350-mln-valued-10-billion-2025-10-28/"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/03/30/how-ai-labs-use-mercor-to-get-the-data-companies-wont-share/"},
            {"name": "Voice of India", "url": "https://voiworld.com/indian-origin-adarsh-hiremath-youngest-self-made-billionaire-ai-startup/"},
            {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Mercor_(company)"},
        ]),
        "tags": ["artificial-intelligence", "mercor", "data-labeling", "indian-american", "startup", "valuation", "adarsh-hiremath", "silicon-valley"],
        "diaspora_angle": "Indian-American co-founder Adarsh Hiremath (Karnataka roots) built Mercor originally to connect Indian programmers to US companies; India remains the largest talent source for its 300,000+ expert contractor network; thousands of NRI professionals earn substantial incomes training AI remotely",
        "score_total": 82,
        "created_at": NOW,
        "updated_at": NOW,
    },

    # ──────────────────────────────────────────────────────────────────
    # Article 2: TSMC Q2 Preview
    # ──────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "slug": "tsmc-q2-earnings-semiconductor-bellwether-nri-investors-20260712",
        "headline": "TSMC Reports Thursday: Why This Semiconductor Bellwether Matters to Every NRI Tech Worker and Investor",
        "subheadline": "The chipmaker that fabricates silicon for Nvidia, Apple, and AMD is expected to post 46 per cent earnings growth — with deep implications for the Indian tech workforce",
        "category": "technology",
        "vertical": "technology",
        "status": "review",
        "is_editorial": False,
        "body": """Taiwan Semiconductor Manufacturing Company reports second-quarter earnings on Thursday, July 16, before the market opens — and for the tens of thousands of Indian-origin engineers whose livelihoods depend on the global semiconductor supply chain, the results carry weight far beyond Wall Street.

Analysts expect TSMC to deliver earnings per share of $3.80, a 46 per cent jump from the same period last year, on revenue of roughly $39.9 billion, representing 26 per cent year-over-year growth. The chipmaker's own guidance from April pointed to revenue between $39 billion and $40.2 billion for the quarter.

The results arrive in a semiconductor market that has turned incandescent. The Philadelphia Semiconductor Index surged 89 per cent in the second quarter alone. TSMC stock has gained 45 per cent year to date, while its market capitalisation hovers around $2.5 trillion — making it Asia's most valuable listed company.

## The AI Engine Room

TSMC is not merely a chip company; it is the foundry that manufactures the most advanced processors on the planet. Nvidia's AI training GPUs, Apple's M-series chips, AMD's data centre processors, Qualcomm's mobile silicon, and Broadcom's networking chips are all fabricated in TSMC's facilities. In the first quarter, 61 per cent of the company's revenue came from its High-Performance Computing segment — the division that builds the brains of the AI revolution.

The company's leadership said last month that TSMC was "scrambling to keep up with relentless AI demand" and working to avoid becoming a bottleneck in the global chip supply chain. Capital expenditure for 2026 is projected at the higher end of its $52 billion to $56 billion forecast, up roughly 30 per cent from 2025.

For the full year, analysts project TSMC's earnings per share to jump 50 per cent to $15.78, with revenue rising 37 per cent to $164.7 billion. The global semiconductor market is forecast to surge to $1.51 trillion in 2026, driven largely by AI infrastructure buildout.

## Why Indian Engineers Should Pay Attention

The diaspora connection runs deep. Tens of thousands of Indian-origin engineers work at TSMC's largest customers — Nvidia, Apple, AMD, Qualcomm, and Broadcom — designing the chips that TSMC fabricates. Indian-Americans hold senior leadership positions across these companies, from Nvidia's research divisions to Qualcomm's engineering teams in San Diego and Hyderabad.

TSMC's expansion into the United States adds another dimension. The company has one advanced fabrication plant operating in Arizona, with three more under construction. These facilities will need thousands of skilled engineers, and Indian-origin professionals — already the largest group of H-1B visa holders in the semiconductor sector — are well-positioned to fill those roles.

India's own semiconductor ambitions are accelerating in parallel. Micron Technology broke ground on a $2.75 billion assembly and test facility in Gujarat's Sanand industrial zone, while the Indian government's India Semiconductor Mission is working to attract fabrication investment. The Dixon Technologies-Vivo joint venture for smartphone component manufacturing was recently approved, adding another link to the supply chain.

## What Investors Should Watch

For NRI investors — and Indian-Americans are among the most active retail participants in US equity markets — TSMC's earnings carry multiple signals. A strong beat would validate the AI spending thesis and likely lift the entire semiconductor complex, including India-listed IT services firms that serve chip designers. A miss or cautious forward guidance could trigger a correction in one of the market's most crowded trades.

Key metrics to watch beyond the headline numbers include revenue guidance for the third quarter, where analysts expect 35 per cent growth; any commentary on pricing power; the trajectory of the HPC segment versus smartphones; and updates on Arizona manufacturing yields. TSMC has hinted it would like to raise prices for customers — a move that would ripple through the entire tech supply chain.

SK Hynix, the South Korean memory-chip maker, just completed a blockbuster $26 billion US share sale, underscoring investor appetite for semiconductor exposure. The question Thursday is whether TSMC can sustain the momentum that has made chipmakers the defining investment story of the AI era.""",
        "image_url": "https://images.pexels.com/photos/6755078/pexels-photo-6755078.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A close-up of a semiconductor chip on a circuit board",
        "image_attribution": "Pexels",
        "sources": json.dumps([
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NYSE/TSM/earnings/"},
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/research/earnings-preview/tsmc-asml-semiconductor-earnings/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/chips-banks-volatility-2026-07-11/"},
            {"name": "Investor's Business Daily (Week Ahead)", "url": "https://www.investors.com/stock-market/stock-market-week-ahead/"},
        ]),
        "tags": ["tsmc", "semiconductors", "ai-chips", "earnings", "nvidia", "apple", "nri-investors", "india-semiconductor-mission"],
        "diaspora_angle": "Tens of thousands of Indian-origin engineers work at TSMC customers (Nvidia, Apple, AMD, Qualcomm, Broadcom); Arizona fab expansion creates new roles for H-1B holders; India's own semiconductor mission and Micron Gujarat fab tie into the global supply chain; NRI investors heavily exposed to chip stocks",
        "score_total": 78,
        "created_at": NOW,
        "updated_at": NOW,
    },

    # ──────────────────────────────────────────────────────────────────
    # Article 3: Skyroot Mission Aagaman
    # ──────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "slug": "skyroot-mission-aagaman-vikram-1-india-first-private-orbital-rocket-20260712",
        "headline": "Mission Aagaman: India's First Private Orbital Rocket Enters Launch Window as Skyroot Makes History",
        "subheadline": "The Hyderabad startup founded by ex-ISRO engineers opens its launch window today for the Vikram-1 rocket, backed by Google's Ram Shriram and Singapore's GIC",
        "category": "technology",
        "vertical": "technology",
        "status": "review",
        "is_editorial": False,
        "body": """The countdown has begun for one of the most consequential launches in Indian space history — and it has nothing to do with ISRO.

Skyroot Aerospace, the Hyderabad-based startup founded by two former Indian Space Research Organisation engineers, opened its launch window today for Mission Aagaman, India's first orbital mission by a private company. The window runs from July 12 to August 4, 2026, with the Vikram-1 rocket poised to lift off from the Satish Dhawan Space Centre in Sriharikota, Andhra Pradesh.

The mission name — Aagaman, meaning "the arrival" in Sanskrit — carries deliberate symbolism. If successful, Skyroot will become the first Indian private company to place a payload in orbit, joining an elite global club that includes SpaceX, Rocket Lab, and Firefly Aerospace.

## From ISRO Labs to Unicorn Status

Skyroot was founded in 2018 by Pawan Kumar Chandana (CEO and CTO) and Naga Bharath Daka (COO), who left ISRO to build commercially competitive launch vehicles for the global small-satellite market. The company emerged during a pivotal moment: the Indian government's 2020 reforms opened ISRO's launch infrastructure to private firms and created the Indian National Space Promotion and Authorisation Centre (IN-SPACe) as a regulatory framework.

On May 7, 2026, Skyroot crossed $1.1 billion in valuation after raising $60 million in a round co-led by Singapore's sovereign wealth fund GIC and Sherpalo Ventures, with participation from BlackRock. The round made Skyroot India's first space technology unicorn and brought its total funding to $160 million.

Ram Shriram, the founder of Sherpalo Ventures and an Alphabet board member best known for being one of Google's earliest backers, joined Skyroot's board as part of the deal. For NRIs tracking Silicon Valley's intersection with Indian deep-tech, his involvement is a significant signal of credibility.

## The Vikram-1 Rocket

Named after Vikram Sarabhai, the father of India's space programme, the Vikram-1 is a four-stage small-lift launch vehicle powered by three solid-fuel stages and a liquid-fuel kick stage. It can deliver up to 350 kilograms into low Earth orbit and 260 kilograms into sun-synchronous polar orbit.

The rocket incorporates carbon-composite structures, 3D-printed components, and modular designs aimed at dramatically reducing launch costs and production timelines. Skyroot's Infinity Campus — a 200,000 square-foot facility in Hyderabad inaugurated by Prime Minister Narendra Modi in November 2025 — can produce one orbital rocket per month, a cadence that would make it competitive with established international players.

Skyroot already proved its core technology in November 2022, when it launched Vikram-S — India's first privately built rocket — in a suborbital mission designated Prarambh ("the beginning"). The rocket reached an altitude of 89.5 kilometres and demonstrated the propulsion systems that underpin the larger Vikram-1.

## A Growing Ecosystem

Skyroot is not operating in isolation. The company has signed an MoU with Axiom Space to explore integrated orbital and launch systems, potentially creating a logistics corridor between Skyroot's launch capability and Axiom's commercial space station. It is also part of a consortium with Nibe Space, AgniKul Cosmos, and Larsen & Toubro to launch India's first constellation of multi-sensor Earth observation satellites.

The competitive landscape is intensifying. AgniKul Cosmos, another Indian private space startup, successfully launched its Agnibaan SOrTeD test vehicle in a suborbital flight. ISRO's own SSLV has completed three launches, with a new launch complex under construction at Kulasekarapattinam in Tamil Nadu, expected to be operational by late 2026.

## The Diaspora Dividend

For the Indian diaspora, Skyroot's trajectory represents something larger than a single rocket launch. It signals that India's deep-tech ecosystem has matured to the point where ex-government scientists can build world-class hardware companies, attract sovereign wealth fund capital, and compete on the global stage.

The company now employs over 1,000 people and reported revenue of 100.6 crore rupees ($11 million) in FY26. It is already developing Vikram-2, a heavier-lift vehicle with a cryogenic upper stage capable of placing 900 kilograms into low Earth orbit, targeted for 2027.

NRI investors and professionals in aerospace should watch Mission Aagaman closely. A successful orbital insertion would validate not just Skyroot's technology, but India's broader ambition to capture a meaningful share of the global satellite launch market — projected to reach $3.5 billion by 2033. The arrival, as the mission name promises, may finally be here.""",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Vikram-S_rocket%27s_Mission_Prarambh_01.webp/1280px-Vikram-S_rocket%27s_Mission_Prarambh_01.webp.png",
        "image_caption": "Skyroot Aerospace's Vikram-S rocket at the Satish Dhawan Space Centre in Sriharikota",
        "image_attribution": "Skyroot Aerospace, CC BY-SA 4.0, via Wikimedia Commons",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-skyroot-readies-countrys-first-private-orbital-rocket-launch-2026-07-02/"},
            {"name": "The Hindu", "url": "https://www.thehindu.com/sci-tech/science/indias-first-privately-developed-orbital-class-rocket-vikram-1-set-for-launch/article69734567.ece"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/05/07/indias-first-space-tech-unicorn-emerges-as-skyroot-gears-up-for-orbital-launch/"},
            {"name": "SpaceNews", "url": "https://spacenews.com/skyroot-raises-60-million-ahead-of-first-orbital-launch-attempt/"},
            {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Skyroot_Aerospace"},
        ]),
        "tags": ["skyroot-aerospace", "vikram-1", "mission-aagaman", "isro", "private-space", "india-space", "unicorn", "sriharikota", "ram-shriram"],
        "diaspora_angle": "Founded by ex-ISRO engineers, backed by NRI investor Ram Shriram (Google early backer, Alphabet board); signals India's deep-tech maturation; NRI aerospace professionals and investors should watch as India aims to capture global satellite launch market share",
        "score_total": 85,
        "created_at": NOW,
        "updated_at": NOW,
    },
]

# ── Insert ────────────────────────────────────────────────────────────
def insert_article(art):
    url = f"{SB_URL}/rest/v1/p2_articles"
    resp = requests.post(url, headers=HEADERS, json=art, timeout=30)
    if resp.status_code in (200, 201):
        data = resp.json()
        row = data[0] if isinstance(data, list) else data
        return {"ok": True, "slug": row.get("slug", art["slug"])}
    else:
        return {"ok": False, "slug": art["slug"], "status": resp.status_code, "error": resp.text[:500]}


if __name__ == "__main__":
    results = []
    for art in articles:
        print(f"  Inserting: {art['slug']} ...", end=" ", flush=True)
        res = insert_article(art)
        results.append(res)
        if res["ok"]:
            print("✅")
        else:
            print(f"❌ {res['status']}: {res['error'][:200]}")

    ok = sum(1 for r in results if r["ok"])
    fail = len(results) - ok
    print(f"\nDone: {ok} inserted, {fail} failed")
    if fail:
        sys.exit(1)
