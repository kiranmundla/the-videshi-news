#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-27 21:00 UTC run."""

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

# Validate image URLs
def validate_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return url
    except:
        pass
    return None

# --- ARTICLE 1: Micron Hits $1 Trillion ---
art1_body = """Sanjay Mehrotra left India for the United States at eighteen with little more than an engineering degree and a conviction that memory chips would matter. Four decades later, the company he runs has become one of the most valuable on Earth.

Micron Technology's market capitalisation surged past one trillion dollars this week, propelled by a 20 per cent single-day rally that capped a year in which the stock has more than tripled. UBS promptly raised its price target to $1,625 — nearly double the current level — citing "structural changes driven by AI" and signals of relentless demand for Micron's high-bandwidth memory (HBM) chips, the specialised silicon that feeds data to Nvidia's GPU clusters.

## The Memory Kingmaker

The AI boom runs on two things: compute and memory. Nvidia gets the headlines, but every GPU training run or inference query needs vast quantities of fast DRAM and HBM to shuttle data back and forth. Micron, alongside Samsung and SK Hynix, controls virtually the entire global supply of both. Under Mehrotra, the company has pivoted hard into HBM, investing billions to ramp production at facilities in Idaho, Japan, and — critically for the diaspora — India.

CEO Sanjay Mehrotra has told analysts that supply constraints will persist through at least 2028, a forecast that underpins the bull case. Micron is effectively selling every chip it can manufacture, with AI labs and hyperscalers queuing for allocation.

## The Gujarat Connection

In Sanand, Gujarat, Micron's $2.75 billion semiconductor assembly and test facility is now operational — India's first chip plant of its kind. The facility, which houses one of the world's largest single-floor cleanrooms at over 500,000 square feet, assembles and tests the very memory modules powering AI workloads globally. The Indian government backed the project with substantial incentives under the India Semiconductor Mission.

Simultaneously, Mehrotra has committed $100 billion over twenty years to build a massive fabrication complex in Clay, New York, expected to create 50,000 American jobs. The dual investment — in both his adopted and ancestral homelands — mirrors the straddling act familiar to millions of Indian Americans.

## Why NRIs Should Pay Attention

For Indian-origin engineers and investors, Micron's trillion-dollar moment carries multiple signals. First, it cements yet another Indian-American at the helm of a company that reshapes global industry — Mehrotra now joins Satya Nadella and Sundar Pichai in the rarefied trillion-dollar CEO club. Second, the Gujarat plant represents India's first serious entry into the global semiconductor supply chain, a development that could create tens of thousands of high-skill jobs and potentially lure NRI chip engineers back home.

The broader semiconductor index rose 5 per cent on the same day, with AMD and Qualcomm each jumping over 5 per cent. The AI infrastructure buildout shows no sign of decelerating, and memory sits at its foundation.

For NRI investors who have watched India's semiconductor ambitions with cautious optimism, Micron's Gujarat bet is the first tangible proof that the dream of "Made in India" chips is becoming reality — funded, built, and led by one of their own."""

art1_image = validate_image("https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg")

# --- ARTICLE 2: Nvidia's $150B Taiwan Bet ---
art2_body = """Jensen Huang stood on a stage in Taipei on Wednesday and made a statement that will echo through boardrooms from Bengaluru to Boise: Nvidia will spend $150 billion a year in Taiwan. That figure, ten times what the company spent in the country five years ago, cements the island as the undisputed manufacturing heart of the AI revolution — and raises uncomfortable questions about where India fits in the picture.

## All Roads Lead to Taipei

The announcement came at the launch celebration for Nvidia's planned Taiwan headquarters, a campus that will break ground this year and aims to be operational by 2030, employing 4,000 people. The $5 trillion chipmaker's logic is straightforward: Taiwan is where TSMC makes the advanced chips that power Nvidia's GPUs, where Foxconn and Quanta assemble the servers, and where the entire AI hardware supply chain converges.

"Taiwan is the epicentre of the AI revolution," Huang declared. "This is where the chips come, packaging comes, this is where the systems are made."

Nvidia is not alone in its conviction. Last week, AMD announced it would invest more than $10 billion in Taiwan's AI sector to deepen partnerships and expand capacity for advanced chip assembly. The semiconductor industry's centre of gravity is pulling toward Taipei with the force of a black hole.

## India's Semiconductor Reality Check

The contrast with India's chip ambitions is instructive. While Taiwan processes the world's most advanced chips at the 2-nanometre node, India's semiconductor journey is just beginning. The Tata Electronics fab in Dholera, Gujarat, targets mature-node chips for automotive and industrial use. Micron's Sanand facility handles assembly and testing, not fabrication. India remains several technological generations behind the cutting edge.

This is not necessarily a failure. India's strategy focuses on the segments where it can compete now — legacy chips, packaging, and testing — while building capability for the future. But Nvidia's $150 billion annual Taiwan commitment makes clear that the advanced AI chip supply chain will remain concentrated in East Asia for the foreseeable future.

## What This Means for Indian Engineers

For the estimated 40,000-plus Indians working in the global semiconductor industry — many of them at Nvidia, AMD, Qualcomm, and Intel in the United States — the Taiwan consolidation creates both opportunity and risk. The opportunity: explosive demand for chip design talent, which remains heavily concentrated in the US and India. The risk: a supply chain so dependent on one island that a geopolitical disruption could freeze the entire AI industry.

Indian engineers are disproportionately represented in chip design roles at these companies. Nvidia's own workforce includes a substantial Indian-origin contingent, particularly in its Santa Clara and Hyderabad offices. As the company scales, this talent pipeline becomes even more critical.

## The Geopolitical Hedge

Huang was part of the delegation that accompanied President Trump to Beijing earlier this month for a summit with President Xi Jinping. The semiconductor industry remains the sharpest edge of US-China competition, and Taiwan sits directly in the middle.

For NRI professionals and investors, the message is nuanced: the AI boom is very real and accelerating, but its manufacturing base is geographically concentrated in ways that should give pause. India's chip ambitions are a long game — and the $150 billion pouring into Taiwan each year is a reminder of just how long that game will be."""

art2_image = validate_image("https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg")

# --- ARTICLE 3: India's GCC Model Shifting ---
art3_body = """For two decades, the pitch was simple: hire brilliant Indian engineers at a fraction of Silicon Valley salaries. That bargain powered the rise of more than 2,100 global capability centres across India, employing 2.36 million people and generating nearly $100 billion in annual revenue. Now the model that built India's tech services empire is being rewritten — and the implications ripple directly into the lives of millions of Indian Americans.

## From Back Office to Boardroom

At a Reuters summit in Bengaluru this week, executives from Microsoft, IBM, Target, and Kimberly-Clark described a transformation that would have been unthinkable a decade ago. Indian GCCs are no longer cost-saving outposts running routine IT operations. They are integrated hubs that own end-to-end product development, manage global R&D programmes, and in some cases lead work that once sat at corporate headquarters.

Microsoft India head Puneet Chandok pointed to the country's 27 million developers on GitHub and its digital public infrastructure — UPI, Aadhaar, DigiLocker — as advantages that no other country can replicate at scale. Target described its Bengaluru operation as an "integrated headquarters" aligned with global strategy, not a satellite office.

IBM's characterisation was perhaps the most telling: India is a "macrocosm" of the enterprise, not a microcosm.

## The Salary Shock

But capability comes at a price. Novo Nordisk executive John Dawber delivered the number that made the room shift: salaries in some Indian tech roles are rising 40 to 50 per cent annually. AI and machine learning specialists command premiums that rival mid-tier US markets. Target's Andrea Zimmerman called the battle for talent "unreal."

The cost arbitrage that launched India's GCC era is eroding. Not disappearing — India still offers significant savings compared to the US or UK — but narrowing enough that companies are hedging. Kimberly-Clark executive Deena Dayalan described an "India plus" strategy, with firms expanding backup operations into Poland, the Philippines, Brazil, and Costa Rica.

## AI: The Double-Edged Sword

The most disruptive force is artificial intelligence itself. GCCs are using AI to generate more output without adding headcount, breaking the traditional link between revenue growth and hiring. "In six to 12 months, we are nearing that inflection point," said Lalit Ahuja, CEO of ANSR, which helps global firms build and run GCCs.

Standard Chartered plans to cut more than 7,000 jobs while ramping AI investments. IBM India head Sandip Patel framed the opportunity more optimistically, predicting India could train a 350-million-strong AI workforce deployable worldwide. The reality will likely land somewhere between these poles.

## The NRI Calculus

For Indian Americans working in tech, this shift recalibrates the "return to India" equation. The old calculus was straightforward: take a salary cut but enjoy lower costs and family proximity. The new calculus is more complex. Senior roles at Indian GCCs now carry real authority and competitive compensation. An engineering director at a Bengaluru GCC might lead the same global programme they would in Cupertino — at lower total cost of living but increasingly comparable pay.

For those considering the reverse move, the window is widening. For NRI investors, India's GCC sector offers exposure to global tech spending without the concentration risk of US mega-caps.

The model is shifting, but the underlying engine — India's depth of technical talent — remains unmatched. The question is no longer whether Indian engineers can do the work. It is whether the economics and infrastructure can keep pace with their ambition."""

art3_image = validate_image("https://images.pexels.com/photos/31321061/pexels-photo-31321061.jpeg?auto=compress&cs=tinysrgb&h=650&w=940")

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Micron Crosses $1 Trillion as Sanjay Mehrotra Joins the Rarefied Club",
        "subheadline": "The Indian-American CEO's memory chip empire has tripled in value this year, fuelled by insatiable AI demand and a $2.75 billion Gujarat fab now in production.",
        "slug": make_slug("micron-trillion-sanjay-mehrotra-ai-memory"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian-American CEO leads memory chip giant to $1 trillion valuation; Gujarat semiconductor plant marks India's first real entry into the global chip supply chain, creating opportunities for NRI engineers and investors.",
        "tags": ["semiconductors", "micron", "sanjay-mehrotra", "ai-chips", "india-semiconductor-mission", "gujarat"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Investopedia", "url": "https://www.investopedia.com/micron-marvell-lead-the-ai-rally-to-start-a-short-week-here-is-what-wall-street-is-watching-next-mu-mrvl-11983712"},
            {"name": "Micron Investors", "url": "https://investors.micron.com"},
            {"name": "Forbes India", "url": "https://www.forbesindia.com"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "image_url": art1_image or "",
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Nvidia Will Spend $150 Billion a Year in Taiwan. Where Does That Leave India?",
        "subheadline": "Jensen Huang's massive bet on Taipei as the AI manufacturing capital underscores the distance India must travel in its own semiconductor ambitions.",
        "slug": make_slug("nvidia-150-billion-taiwan-india-chips"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Nvidia's Taiwan consolidation affects tens of thousands of Indian-origin chip engineers in the US while highlighting the gap between India's nascent fab ambitions and Taiwan's entrenched dominance.",
        "tags": ["nvidia", "semiconductors", "taiwan", "jensen-huang", "india-semiconductor-mission", "geopolitics"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/asia-pacific/nvidia-ceo-says-taiwan-is-epicentre-ai-revolution-2026-05-27/"},
            {"name": "Barron's", "url": "https://www.barrons.com"},
            {"name": "DIGITIMES", "url": "https://www.digitimes.com"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": art2_image or "",
        "body": art2_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's $100 Billion GCC Engine Is Being Rewritten by AI",
        "subheadline": "Salary inflation of 50 per cent, an 'India plus' hedging strategy, and AI-driven headcount compression are transforming the model that employs 2.36 million people.",
        "slug": make_slug("india-gcc-ai-transformation-salary-inflation"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "GCC transformation directly reshapes the return-to-India calculus for NRI tech workers — senior roles now carry real authority and narrowing pay gaps, while AI threatens entry-level hiring pipelines.",
        "tags": ["gcc", "india-tech", "ai-workforce", "outsourcing", "salary-inflation", "return-to-india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-gcc-model-shifts-cost-capability-ai-talent-strains-bite-2026-05-27/"},
            {"name": "Nasscom-Zinnov 2026 Report", "url": "https://nasscom.in"},
            {"name": "Reuters", "url": "https://www.reuters.com/business/ai-age-firms-chase-growth-with-fewer-workers-2026-05-27/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": art3_image or "",
        "body": art3_body,
    },
]

for art in articles:
    if not art["image_url"]:
        print(f"⚠️  No valid image for: {art['slug']}")
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
