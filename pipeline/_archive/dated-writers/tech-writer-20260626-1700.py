#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-26 17:00 PT run"""
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

# ─────────────────────────────────────────────────
# Article 1: Oracle 21,000 AI Layoffs
# ─────────────────────────────────────────────────
art1_body = """Oracle just reported the most profitable year in its 47-year history. Revenue hit $67 billion. The stock rallied. Larry Ellison's net worth nudged past $200 billion. And then, in an SEC filing released on June 23, the company quietly disclosed that it had shed 21,000 employees over the past twelve months — roughly 13 per cent of its entire workforce — and that artificial intelligence was a primary driver.

"The adoption and deployment of AI technologies across our operations have resulted, and may continue to result, in reductions to our workforce," the filing reads. It is among the most explicit admissions any major technology company has made linking AI directly to mass layoffs.

## The Numbers Behind the Cuts

Oracle's headcount fell from 162,000 to 141,000 as of May 31, 2026. Of those who remain, about 49,000 are in the United States. The restructuring cost the company $1.84 billion in severance and exit charges — a fivefold increase from the $374 million spent the year before. Oracle has earmarked up to $2.1 billion for the full restructuring plan, signalling more cuts could follow.

The company acknowledged the risks openly: "shortages of sufficiently skilled employees in certain roles, loss of valuable institutional knowledge, and damage to employee morale and retention." It does not appear to believe those downsides outweigh the efficiency gains.

## Why Indian Tech Workers Should Pay Attention

Oracle has been one of the largest employers of Indian technology professionals in the United States for decades. The company's operations in Hyderabad, Bengaluru, and Pune collectively employ tens of thousands. Indians account for a disproportionate share of Oracle's global workforce — and of its H-1B visa holders in the US.

For those on employer-sponsored visas, a layoff is not just a career setback. It triggers a 60-day grace period to find a new sponsor, transfer the visa, or leave the country. With 119,800 tech workers laid off globally so far in 2026 — according to Layoffs.fyi — the competition for new sponsorship is fierce.

The damage extends beyond current employees. Reports from Indian campuses indicate that Oracle has begun rescinding offer letters to prospective hires across several colleges, freezing the entry pipeline at both ends.

## The Broader Pattern

Oracle is hardly alone. AI accounted for 40 per cent of all US job cuts announced in May 2026 — the highest monthly share ever recorded since Challenger, Gray & Christmas began tracking the category in 2023. The tech sector was responsible for more than a third of total cuts, with 123,653 tech jobs eliminated through the first five months of the year, a 66 per cent increase over the same period in 2025.

Meta cut 8,000 positions. Amazon continued rounds of reductions across multiple divisions. LinkedIn trimmed headcount. The pattern is consistent: companies are reporting record revenues while citing AI as the reason they need fewer people.

## What Comes Next

Oracle is simultaneously pouring cash into AI infrastructure. It expects net capital expenditure of about $70 billion this fiscal year, funded partly by $40 billion in new debt and equity. The company has signed massive data-centre deals with OpenAI and Meta to compete more aggressively with Amazon Web Services and Microsoft Azure.

The message to the diaspora is blunt: the same AI that Oracle is betting its future on is the reason 21,000 people lost their jobs. For Indian engineers in Austin, Redwood City, and Hyderabad alike, the restructuring raises a question that no quarterly earnings call can answer — whether the next round of efficiency gains will come for their desk, too."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Oracle Posted Record Profits and Then Fired 21,000 People. It Blamed AI.",
    "subheadline": "The database giant disclosed the biggest AI-attributed workforce reduction in corporate history. Indian engineers on H-1B visas and fresh graduates with rescinded offers are among the hardest hit.",
    "slug": make_slug("oracle-21000-layoffs-ai-record-revenue-indian-engineers-h1b"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Oracle is a major H-1B employer of Indian tech workers; layoffs trigger the 60-day visa clock, and rescinded campus offers in India freeze the entry pipeline for new graduates.",
    "tags": ["oracle", "layoffs", "ai", "h-1b", "indian-tech-workers"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/oracle-workforce-shrinks-by-about-21000-employees-amid-ai-adoption-2026-06-23/"},
        {"name": "TheStreet", "url": "https://www.thestreet.com/technology/oracle-blames-ai-for-21000-tech-layoffs"},
        {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/06/25/oracles-headcount-fell-by-21000-as-ai-reshapes-its/"},
        {"name": "Gulte", "url": "https://www.gulte.com/news/this-is-huge-oracle-fires-21000-employees-in-one-year/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/00/Larry_Ellison_picture.png",
    "image_caption": "Oracle co-founder and CTO Larry Ellison, whose company disclosed 21,000 AI-driven job cuts",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}

# ─────────────────────────────────────────────────
# Article 2: Alphabet Joins the Dow — Pichai angle
# ─────────────────────────────────────────────────
art2_body = """On Sunday, June 29, Sundar Pichai's Alphabet will be added to the Dow Jones Industrial Average, replacing Verizon in the 130-year-old, 30-stock benchmark. It is the latest sign of how thoroughly Indian-origin executives have reshaped the commanding heights of American business — and of how much turbulence still surrounds the company they lead.

S&P Dow Jones Indices announced the swap on June 23, citing Alphabet's "broad business mix" across AI, cloud computing, digital advertising, autonomous vehicles, and media. The company will join under its Class A ticker, GOOGL, becoming the fifth Magnificent Seven member in the index alongside Apple, Microsoft, Amazon, and Nvidia.

## The Pichai Factor

The Dow addition is, in effect, a blue-chip coronation for a company that Pichai — born in Madurai, educated at IIT Kharagpur, Stanford, and Wharton — has led since 2015. Under his watch, Google Cloud revenue surpassed $20 billion for the first time in Q1 2026, growing 63 per cent year over year. Alphabet's AI backlog nearly doubled to over $460 billion.

Pichai is not the only Indian-origin leader at the top: YouTube CEO Neal Mohan, also Indian-American, runs the world's largest video platform. Together, they oversee a company that employs tens of thousands of Indian engineers across Mountain View, Bengaluru, and Hyderabad.

## The Brain Drain Shadow

The index recognition arrives at an awkward moment. On June 22 — the day before the Dow announcement — Alphabet shares fell 5 per cent, their steepest single-day decline since May 2025, wiping more than $256 billion in market value.

The catalyst: two of Google's most prominent AI researchers announced departures in rapid succession. John Jumper, a senior Google DeepMind scientist and 2024 Nobel Prize winner in Chemistry for his work on protein structure prediction, said he would leave for Anthropic. Noam Shazeer, an engineering vice president and co-lead of Google's Gemini models, announced he was joining OpenAI.

These are not ordinary departures. Shazeer is a co-author of the 2017 "Attention Is All You Need" paper that invented the Transformer architecture — the foundation of every major AI model in existence. Losing him to OpenAI is the AI equivalent of losing your franchise quarterback to a division rival.

## The Spending Question

Alphabet's $180 billion to $190 billion capital expenditure plan for 2026 — more than double the $91 billion it spent last year — is the market's other worry. Most of that spending goes toward AI data centres and model training. Free cash flow is expected to drop from $73.3 billion last year to $20.5 billion this year.

For NRI investors who hold Alphabet stock directly or through index funds, the Dow addition will trigger automatic buying from funds that track the benchmark. But the elevated spending and AI talent losses mean the stock's near-term trajectory is anything but certain. If the Dow reshuffle pushes shares higher, the spending overhang and brain-drain risk may pull them back.

## What It Means for the Diaspora

Alphabet is one of the largest employers of Indians in Silicon Valley, and Google's Bengaluru and Hyderabad offices are among the biggest outside the US. For Indian engineers, Pichai's company joining the Dow is a milestone — the culmination of two decades of Indian leadership in American tech.

But it is also a reminder that prestige and stability are not the same thing. Capital spending of this scale compresses margins. Departures of this calibre reshape product roadmaps. And for NRI investors, the stock's inclusion in a price-weighted index like the Dow adds mechanical buying pressure that may not reflect the company's shifting fundamentals.

Sundar Pichai now leads one of only 30 companies in the Dow. The harder question is whether he can keep the researchers who make Alphabet worth being there."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Sundar Pichai's Alphabet Just Joined the Dow. It's Losing Nobel-Winning Researchers to Rivals.",
    "subheadline": "Google's parent replaces Verizon in the 30-stock benchmark on June 29 — days after a Nobel laureate defected to Anthropic and a Gemini co-lead left for OpenAI, wiping $256 billion in a single session.",
    "slug": make_slug("alphabet-dow-jones-pichai-brain-drain-deepmind-openai-nri"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Led by Indian-origin CEO Sundar Pichai, Alphabet's Dow inclusion is a milestone for diaspora tech leadership; NRI investors face both index-fund tailwinds and brain-drain headwinds.",
    "tags": ["alphabet", "google", "sundar-pichai", "dow-jones", "ai", "deepmind", "indian-ceo"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "S&P Dow Jones Indices via Investopedia", "url": "https://www.investopedia.com/changes-are-coming-to-the-big-indexes-11744891"},
        {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/news/google-parent-alphabet-to-join-dow-jones-industrial-average-as-verizon-exits-the-index"},
        {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/google-stock-googl-alphabet-dow-jones-verizon/"},
        {"name": "Investor's Business Daily (Yardeni analysis)", "url": "https://www.investors.com/news/technology/google-stock-googl-alphabet-june-swoon-yardeni/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
    "image_caption": "Alphabet CEO Sundar Pichai, whose company joins the Dow Jones Industrial Average on June 29",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}

# ─────────────────────────────────────────────────
# Article 3: India IT Services Identity Crisis
# ─────────────────────────────────────────────────
art3_body = """For three decades, India's IT services industry sold the world a straightforward proposition: smart engineers, rigorous process, lower cost. It worked brilliantly. TCS, Infosys, Wipro, HCL Tech, and Tech Mahindra collectively built a $315 billion sector that employs nearly six million people and accounts for the single largest source of white-collar employment in the country.

That proposition is now under existential pressure — and the numbers from fiscal year 2026, which closed in March, make the strain impossible to ignore.

## The Hard Data

Net headcount across India's five largest IT firms shrank by 7,389 employees in FY2026, reversing the modest gains of 12,718 recorded the previous year. TCS delivered the sharpest blow: 12,000 planned job cuts, the largest workforce reduction by an Indian corporate employer in recent memory. Tech Mahindra shed roughly 3,100. Infosys and Wipro bucked the trend by adding staff, but not enough to offset the industry-wide contraction.

Beyond existing employees, the pipeline is drying up. The Xpheno Tech Jobs Outlook for June 2026 projects active technology hiring demand at just 96,000 positions — a 28-month low and a 14 per cent decline from the previous month. Full-time technology jobs have dropped 24 per cent year over year. Entry-level demand has cratered 44 per cent. Senior-level openings have fallen 67 per cent.

Research firm UnearthInsight estimates that 400,000 to 500,000 IT professionals are at risk of layoffs over the next two to three years, with roughly 70 per cent of the impact concentrated among workers with four to twelve years of experience — precisely the mid-career backbone of the industry.

## The AI Squeeze

The crisis is not cyclical. It is structural. Generative AI is automating the routine coding, testing, bug-fixing, and maintenance work that Indian IT services firms have built their businesses on. Clients are now demanding "productivity benefits" in new contracts — code for doing the same work with fewer people, or more work with the same headcount.

"Indian IT companies built enormous scale, but they never quite built powerful global technology brands the way product companies did," marketing strategist Shubhranshu Singh observed. "Their reputation rested less on invention or intellectual property and more on reliability, process discipline, and cost efficiency. AI is now exposing the vulnerabilities of that model."

TCS reported its first annual revenue decline in more than two decades. Infosys, HCL Tech, and Wipro all trimmed their revenue forecasts for fiscal 2027. The Nifty IT index, which tracks the sector, has been the worst-performing sectoral index of 2026, shedding roughly $26 billion in market value after earnings disappoints.

## The NRI Dilemma

For the Indian diaspora, this is not an abstract industry story. It is personal in three distinct ways.

First, tens of thousands of Indians working in the US on H-1B and L-1 visas are employed by these firms' American operations. TCS, Infosys, and Wipro are among the largest H-1B sponsors in the country. A restructuring in Bengaluru often means a restructuring in New Jersey.

Second, NRI investment portfolios are heavily weighted toward Indian IT stocks. TCS alone has a market capitalisation exceeding ₹7.6 lakh crore. A sustained rerating of the sector's growth prospects directly erodes wealth.

Third, the "return to India" calculus shifts. For years, the IT services boom made Bengaluru, Hyderabad, and Pune attractive destinations for diaspora professionals considering a move back. If those cities can no longer guarantee the career trajectories that once lured talent home, the decision becomes harder.

## Not Dead Yet

Industry observers caution against writing the eulogy. "The slowdown is not destroying the employer brand of legacy IT companies, but it is changing what those brands stand for," said Shantanu Rooj, founder of TeamLease EdTech. Companies that reinvent themselves around AI consulting, cloud migration, and enterprise automation may find a second act.

But the window is narrow. The industry's identity was built on bodies — millions of engineers executing client projects at scale. If AI can replicate that execution at a fraction of the cost, then the value proposition that built modern India's largest private-sector employer will need to be rebuilt from scratch. That work has barely begun."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India's $315 Billion IT Industry Built Its Empire on Labour. AI Is Dissolving the Foundation.",
    "subheadline": "TCS is cutting 12,000 jobs. Entry-level tech hiring has crashed 44 per cent. And the sector that employs six million people is facing a question it spent three decades avoiding.",
    "slug": make_slug("india-it-services-ai-crisis-tcs-layoffs-entry-level-hiring"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "NRIs hold heavy positions in Indian IT stocks, work for TCS/Infosys/Wipro US operations on H-1B/L-1 visas, and factor IT sector health into return-to-India decisions.",
    "tags": ["indian-it", "tcs", "infosys", "wipro", "ai", "layoffs", "h-1b"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Storyboard18", "url": "https://www.storyboard18.com/brand-marketing/ai-shift-challenges-india-it-giants-as-hiring-slows-and-brands-evolve-ws-l-102123.htm"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-tcs-layoffs-herald-ai-shakeup-283-billion-outsourcing-sector-2025-08-08/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/indian-it-firms-near-term-outlook-muted-clients-cut-spending-ai-risks-mount-2026-04-24/"},
        {"name": "DQ India", "url": "https://www.dqindia.com/analysis/top-indian-it-firms-see-net-loss-of-nearly-3000-employees-in-q3-fy26-6831614"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/S3_and_S4_Building_SJP2_Wipro_Sarjapur_office_Photo_182805.jpg/1280px-S3_and_S4_Building_SJP2_Wipro_Sarjapur_office_Photo_182805.jpg",
    "image_caption": "The Wipro campus in Sarjapur, Bengaluru — one of many Indian IT campuses facing an AI-driven identity crisis",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip()
}

# ─────────────────────────────────────────────────
# Validate & Insert
# ─────────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    # Basic validations
    assert len(art["headline"]) >= 20, f"Headline too short: {art['headline']}"
    assert len(art["headline"]) <= 200, f"Headline too long: {art['headline']}"
    assert len(art["subheadline"]) >= 15, f"Subheadline too short"
    assert len(art["body"].split()) >= 400, f"Body too short: {len(art['body'].split())} words in {art['slug']}"
    assert art["category"] == "technology"
    assert art["status"] == "review"
    assert art.get("is_editorial") == False
    # Verify image URL is not from banned sources
    img = art["image_url"]
    assert "fbcdn.net" not in img and "cdninstagram.com" not in img, "Banned image source"

    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}  ({len(art['body'].split())} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
