#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-30 15:00 UTC batch"""

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


articles = [
    # ── ARTICLE 1: Sanjay Mehrotra / Micron $1 Trillion ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Sanjay Mehrotra Was Denied a US Visa Three Times. Now He Runs America's Tenth-Largest Company.",
        "subheadline": "Micron Technology crossed $1 trillion in market value this week, making its Kanpur-born CEO a billionaire and completing an extraordinary Indian trifecta at the summit of American capitalism.",
        "slug": make_slug("sanjay-mehrotra-micron-trillion-dollar-visa-billionaire"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Three of the world's most valuable technology companies — Microsoft, Alphabet, and Micron — are now run by Indian-origin CEOs who arrived in America as middle-class students. Mehrotra's journey from BITS Pilani to a $1T company is the most dramatic immigration story in corporate America, and Micron's Gujarat fab brings the story full circle for NRIs watching India's semiconductor ambitions.",
        "tags": ["semiconductor", "indian-ceo", "micron", "sanjay-mehrotra", "trillion-dollar-club", "hbm", "ai-chips"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Global India Broadcast News", "url": "https://globalindiabroadcastnews.com/us-visa-rejected-three-times-sanjay-mehrotra-joins-satya-nadella-and-sundar-pichai-in-the-trillion-dollar-club/"},
            {"name": "Forbes / YouTube", "url": "https://www.youtube.com/watch?v=_micron_mehrotra_billionaire"},
            {"name": "TechStory", "url": "https://techstory.in/micron-ceo-sanjay-mehrotra-joins-billionaire-ranks/"},
            {"name": "TezzBuzz", "url": "https://tezzbuzz.com/who-is-sanjay-mehrotra-indian-origin-billionaire-behind-trillion-dollar-micron/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/chip-rally-parabolic-pillars-pretenders/"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg",
        "body": """In the summer of 1976, a teenage engineering student from Kanpur stood in the lobby of the US Embassy in New Delhi after being denied a student visa for the third time. His father, who had accompanied him, refused to leave. He found the consular officer's photograph on the wall, discovered the man was at lunch, and waited to ask why his son — with confirmed admission to three American universities and every document in order — kept getting turned away.

Persistence won. Half a century later, that student, Sanjay Mehrotra, is the chairman, president, and CEO of Micron Technology, the memory chip giant that this week surpassed $1 trillion in market capitalisation to crack the top ten most valuable companies in the United States. It now sits ahead of Walmart, Berkshire Hathaway, and JPMorgan Chase.

## The Indian Trifecta

Mehrotra's ascent completes an extraordinary tableau at the summit of American capitalism. Three of the world's most valuable technology companies — Microsoft ($3.2 trillion, Satya Nadella), Alphabet ($4.6 trillion, Sundar Pichai), and Micron ($1.07 trillion, Mehrotra) — are now led by Indian-origin executives who arrived in the United States as middle-class strivers with engineering degrees, parental sacrifice, and very little else.

Nadella grew up in Hyderabad, the son of a government employee. Pichai shared a rotary telephone with his family in a modest Chennai apartment. Mehrotra transferred from BITS Pilani to UC Berkeley, where he earned bachelor's and master's degrees in electrical engineering and computer science. He holds roughly 70 patents.

## The AI Memory Machine

Micron's meteoric valuation is not biographical sentiment. It is the direct consequence of an unprecedented corporate hunger for memory chips — the silent infrastructure that makes AI possible. Graphics processors get the headlines, but they are effectively useless without memory pipelines capable of feeding them data at near-instantaneous speeds.

The company's stock has surged roughly 863 percent over the past twelve months. Its high-bandwidth memory (HBM) products — ultra-fast, stacked-chip architectures deployed directly alongside top-tier AI accelerators — are in insatiable demand from every major hyperscaler. Revenue hit $58 billion over the trailing twelve months, with a net profit margin above 41 percent.

According to Barron's, Micron trades at a price-to-earnings-growth ratio below 0.6 times — making it, paradoxically, one of the most undervalued mega-cap stocks in the market despite its recent run.

## The Gujarat Connection

For the Indian diaspora, the Micron story has an added resonance. The company is building a $2.7 billion semiconductor assembly and test facility in Sanand, Gujarat — its first major manufacturing investment in India. The facility, backed by incentives from India's Semiconductor Mission, is expected to create thousands of jobs and establish India as a node in Micron's global supply chain.

Mehrotra, who co-founded SanDisk in 1988 and built it into a Fortune 500 company before its $16 billion acquisition by Western Digital in 2016, has spoken publicly about the intersection of his personal journey and India's semiconductor ambitions. He joined Micron as CEO in 2017. Under his leadership, the stock has risen roughly 3,000 percent.

## What It Means for NRIs

The trillion-dollar milestone is more than a market event. It is a data point in a larger argument about the structural role of Indian talent in American technology. For NRI investors, Micron's HBM-driven growth trajectory — with next earnings due June 24 — represents one of the purest plays on AI infrastructure demand. For Indian engineers on H-1B visas at chip companies across the Bay Area, it is a reminder that the ceiling is where you build it.

Mehrotra's father waited in a lobby for a consular officer to return from lunch. His son waited three decades to build the company the AI revolution cannot function without. The patience paid off at roughly $1.07 trillion."""
    },

    # ── ARTICLE 2: Ashok Elluswamy / Tesla Cybercab ──
    {
        "id": str(uuid.uuid4()),
        "headline": "The Chennai Engineer Who Runs Tesla's Self-Driving Bet Just Confirmed the Cybercab Is Coming.",
        "subheadline": "Ashok Elluswamy, the first hire on Tesla's Autopilot team and now its VP of AI Software, signaled that the purpose-built robotaxi will 'soon' join Tesla's live fleet in Austin — even as a Reuters investigation raises pointed questions about the company's safety statistics.",
        "slug": make_slug("ashok-elluswamy-tesla-cybercab-robotaxi-chennai"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Elluswamy's trajectory from College of Engineering Guindy in Chennai to running AI software at a $1.6 trillion company is one of the most consequential Indian engineering careers in the world today. Musk once said 'without him, we would just be another car company.' For thousands of Indian AI and robotics engineers in the US, his role at the center of Tesla's autonomous driving program is both aspirational and a case study in the risks of building the future under intense public scrutiny.",
        "tags": ["tesla", "robotaxi", "cybercab", "ashok-elluswamy", "autonomous-driving", "ai", "indian-engineer"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/tesla-cybercab-robotaxi-fleet/"},
            {"name": "EVSHIFT", "url": "https://evshift.com/tesla-cybercab-coming-to-austin-robotaxi-fleet-soon/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/why-teslas-ai-trainers-dont-trust-its-self-driving-tech/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/how-safe-is-a-tesla-robo-taxi/"},
            {"name": "TechGig", "url": "https://content.techgig.com/technology-unplugged/elon-musk-hires-indian-origin-ashok-elluswamy-as-teslas-autopilot-head/articleshow/88669855.cms"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32461216/pexels-photo-32461216.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """In 2015, Elon Musk posted a tweet announcing that Tesla was starting an Autopilot team and asking engineers to apply. Among the flood of résumés, one stood out: Ashok Elluswamy, a Chennai-born robotics engineer with a bachelor's from the College of Engineering Guindy and a master's from Carnegie Mellon University. He became the first person hired for the program.

A decade later, Elluswamy is Tesla's Vice President of AI Software — the person who oversees the neural networks, training pipelines, and decision-making systems that power every Tesla on the road today. And this week, he confirmed that Tesla's purpose-built Cybercab robotaxi will "soon" join the company's live, unsupervised fleet operating in Austin, Texas.

## The Cybercab Enters the Arena

The confirmation, first reported by TeslaNewswire, marks the first direct executive acknowledgement that the Cybercab — a two-passenger vehicle with no steering wheel, no pedals, and a vision-only sensor suite — is ready for real-world commercial deployment. Tesla began Cybercab production at Gigafactory Texas on April 24, targeting hundreds of units per week.

Tesla's existing robotaxi operation in Austin has been running since June 2025, initially with Model Y vehicles. Unsupervised rides — meaning no safety driver onboard — began in January 2026, expanding to Dallas and Houston by April. The active fleet currently sits at roughly 20 vehicles: 14 in Austin, 3 in Dallas, 3 in Houston. The Cybercab's arrival would represent a qualitative shift from retrofitted consumer cars to purpose-built autonomous machines.

## The Safety Question

The timing is complicated. A Reuters investigation published this week scrutinized Tesla's self-driving safety statistics — the same numbers Musk has cited to claim that Full Self-Driving is "up to 10 times safer than human drivers." The investigation, which included interviews with 11 traffic-safety researchers and a detailed methodological review, found several invalid data comparisons. Ten of the researchers said Tesla's approach amounted to "misleading marketing rather than a serious investigation into a critical safety issue."

Separately, a Morgan Stanley analysis noted genuine improvement: incident rates have dropped from one every 50,000 miles in late 2025 to one every 150,000 miles now. For context, Alphabet's Waymo was at roughly 150,000 miles between incidents at a similar stage in its rollout and currently operates at 460,000 miles between incidents. The national average for human drivers is approximately one reported accident every 500,000 miles, though conditions vary enormously.

## 'Without Him, We Would Just Be Another Car Company'

Musk's public assessment of Elluswamy has been unusually direct. "Ashok was the first person to join the Tesla AI/Autopilot team and ultimately rose to lead all AI/Autopilot software," Musk wrote on X in 2024. "Without him and our awesome team, we would just be another car company looking for an autonomy supplier that does not exist."

Elluswamy has described starting with "a ridiculously tiny computer that only had about 384 KB of memory" in 2014 — a machine that lacked native floating-point arithmetic. Musk asked the team to implement lane keeping, lane changing, and longitudinal control on that hardware. Many on the team thought the request was impossible. In 2015, Tesla shipped the world's first Autopilot system. The nearest competitor shipped years later.

Before Tesla, Elluswamy worked at WABCO Vehicle Control Systems and interned at Volkswagen's Electronic Research Lab. His career arc — from Guindy to the beating heart of a $1.6 trillion company's most consequential bet — is one of the most extraordinary Indian engineering trajectories in Silicon Valley.

## What NRIs Should Watch

Tesla's robotaxi ambitions carry direct implications for the Indian tech diaspora on multiple levels. Thousands of Indian engineers work at Tesla across AI, software, and hardware roles. The company's approach — cameras only, no lidar — is a bet that software talent can substitute for expensive sensor hardware, a thesis that Indian AI engineers are disproportionately involved in validating.

For NRI investors, the Cybercab deployment timeline matters enormously. Tesla's stock ($445, up 15 percent this month) is trading near a cup-with-handle buy point of $453.40. The company's ability to scale unsupervised rides with purpose-built vehicles — rather than retrofitted Model Ys — will determine whether the robotaxi thesis that underpins much of Tesla's valuation is real or aspirational.

And at the centre of that question sits a man from Chennai who answered a tweet eleven years ago."""
    },

    # ── ARTICLE 3: Chip Rally — NRI Investor Guide ──
    {
        "id": str(uuid.uuid4()),
        "headline": "The Chip Rally Has Gone Parabolic. Here Are the Five Semiconductor Stocks NRI Investors Should Actually Understand.",
        "subheadline": "Barron's just declared five semiconductor companies 'pillars of the new economy' — and every one of them employs thousands of Indian engineers, trades below its growth rate, and sits at the centre of a $160 billion annual investment surge in Taiwan.",
        "slug": make_slug("chip-rally-parabolic-five-semiconductor-pillars-nri"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian Americans are disproportionately represented in the semiconductor workforce — from design engineers at Nvidia and AMD to memory architects at Micron to custom chip teams at Broadcom. Many hold significant equity in these companies via RSUs and ESPPs. With the chip rally going parabolic ahead of Computex, the investment thesis directly affects NRI portfolios, career decisions, and even return-to-India calculations for engineers weighing offers at India's emerging fabs.",
        "tags": ["semiconductor", "nvidia", "amd", "broadcom", "micron", "tsmc", "nri-investors", "computex", "ai-chips"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Barron's", "url": "https://www.barrons.com/articles/chip-rally-parabolic-pillars-pretenders/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/nvidia-taiwan-computex-ai-infrastructure/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/tsmc-energy-efficiency-chip-design/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/amd-lisa-su-china-nvidia-jensen-huang/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37052613/pexels-photo-37052613.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """The semiconductor rally is no longer a rally. It is a repricing of an entire industry's role in the global economy. Barron's published a sweeping analysis this week separating the "pillars" from the "pretenders" in the chip trade, and its conclusion is stark: five companies — Nvidia, AMD, Broadcom, Micron, and TSMC — are not just riding the AI wave. They are the wave. And all five, by standard valuation metrics, remain cheaper than the S&P 500.

For Indian Americans — who are disproportionately represented in the engineering ranks of every one of these companies — this is not abstract market commentary. It is a career, portfolio, and life-planning question.

## The Five Pillars

**Nvidia** ($150+ per share, up from $33 in fiscal 2023 on an adjusted-EPS basis) remains the undisputed leader. Jensen Huang's company sells the GPUs that train and run AI models, but its moat is deeper than hardware: a two-decade investment in software, networking chips, and a full-stack AI platform. Vera Rubin AI servers, shipping this year, contain five distinct chip types. Wall Street projects EPS of $12.37 by fiscal 2028, giving the stock a forward P/E of roughly 17 times. Huang this week pledged to spend up to $150 billion annually in Taiwan, calling it "the epicentre of the AI revolution."

**Broadcom** ($447, up 4.7 percent Friday) is the custom chip king. It designs Google's Tensor Processing Units (now on their eighth generation), has confirmed OpenAI and Meta as customers, and counts six hyperscalers total. AI chip revenue doubled to $8.4 billion last quarter. The company is targeting $100 billion in AI revenue by 2027. CEO Hock Tan stands to collect $750 million in stock if AI revenue hits $120 billion by 2030.

**AMD** ($185) is the challenger. Lisa Su's company commands 4 percent of China's AI chip market — modest, but infinitely more than Nvidia, whose share has dropped to effectively zero under US export controls. AMD's diversified portfolio (CPUs, consumer GPUs, FPGAs, AI accelerators) gives it routes into enterprise AI workloads that Nvidia cannot easily match. Su invested $10 billion in Taiwan's AI sector this week, days after meeting China's Vice Premier He Lifeng.

**Micron** ($971, newly in the trillion-dollar club) supplies the memory that makes AI possible. High-bandwidth memory, DRAM, and NAND flash are the circulatory system of every data centre. CEO Sanjay Mehrotra, a BITS Pilani and UC Berkeley alumnus, just became a billionaire as the stock surged 863 percent in twelve months.

**TSMC** ($245) manufactures the chips for all of the above, plus Apple, and is expanding capacity in Arizona. Its N2 to A14 technology roadmap promises 30 percent power reduction by 2028 — critical as energy efficiency, not raw speed, becomes the binding constraint on AI infrastructure.

## The Valuation Puzzle

Here is what should interest NRI investors who hold equity in these companies or are considering positions: all five trade at two-year PEG ratios below 0.6 times. The S&P 500 trades at 1.0 times. In plain English, these stocks are growing so fast that their current prices do not fully reflect expected earnings two years from now. Barron's calls them "undervalued."

That does not mean they are safe. Semiconductors are cyclical, geopolitically exposed, and subject to demand shocks. But the structural argument — that AI compute demand will sustain above-trend growth for the next several years — is shared by virtually every credible analyst on Wall Street.

## Why This Hits Different for Indian Engineers

Walk through the corridors of Nvidia's Santa Clara campus, AMD's design centres in Hyderabad and Bengaluru, Broadcom's teams in San Jose, or Micron's Gujarat facility, and the Indian presence is unmistakable. Indian Americans are among the largest demographic groups in US semiconductor engineering. Many hold tens of thousands of dollars — in some cases, hundreds of thousands — in company RSUs and ESPP shares.

The chip rally is not just a portfolio event for these engineers. It is a wealth event. And it creates a secondary calculation: as India builds its own semiconductor ecosystem (Tata Electronics in Dholera, Micron in Gujarat, Intel in Odisha), some of these engineers are weighing whether to return. The valuation gap between their US equity and India compensation packages is a real factor in those decisions.

## Computex Week

All five pillars will be in the spotlight next week at Computex in Taipei (June 2-5). Huang's Monday keynote is expected to reveal Nvidia's Arm-based Windows PC chip — a potential "new era of PC," as cryptic social media posts from Nvidia, Microsoft, and Arm hinted on Friday. TSMC will detail its energy-efficiency roadmap. AMD will showcase its enterprise AI portfolio.

For NRI investors and engineers: this is the week the market decides whether the chip rally's next leg is up or sideways. The five pillars have earned their place. The question is whether the price of admission has finally caught up."""
    },
]


for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
