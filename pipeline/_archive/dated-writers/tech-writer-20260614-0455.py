#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-14 batch"""

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


# ─────────────────────────────────────────────
# ARTICLE 1: Forbes 250 Most Successful Immigrants
# ─────────────────────────────────────────────

art1_body = """Forbes has put a number on what the Indian diaspora has long felt in its bones. Of the 250 most successful living immigrants in the United States — a list timed to America's 250th anniversary — at least 26 are of Indian origin. They span technology, finance, venture capital, academia, clean energy, and even television.

Vinod Khosla, the Sun Microsystems co-founder who remade himself as one of Silicon Valley's most prolific climate and AI investors, landed at No. 14, making him the highest-ranked Indian on the list. Naval Ravikant, the AngelList co-founder who seeded early bets in Twitter, Uber, and Postmates before any of them were household names, came in at No. 27.

## The CEO corridor

The names that follow read like a roll call of the American technology establishment. Sundar Pichai (Alphabet/Google), Satya Nadella (Microsoft), Arvind Krishna (IBM), Shantanu Narayen (Adobe), Nikesh Arora (Palo Alto Networks), and Sanjay Mehrotra (Micron Technology) all made the cut. Together, these six Indian-born CEOs run companies worth well north of $7 trillion in combined market capitalisation.

Forbes notes that the broader list includes the founders or leaders of NVIDIA, Google, AMD, Linux, DoorDash, Zoom, Databricks, Snowflake, Anthropic, Perplexity, and Waymo — many of them also immigrant-founded. But no single country of origin commands the depth of representation that India does in the technology and enterprise brackets.

## Beyond the corner office

The list reaches well past tech. Abhijit Banerjee, the MIT economist who won the Nobel Prize for his experimental approach to alleviating global poverty, features alongside Indra Nooyi, whose 12-year tenure atop PepsiCo reshaped the food and beverage giant's portfolio toward health. Padma Lakshmi, the author, television host, and activist, represents Indian-origin influence in media and culture.

Other honorees include Neha Narkhede, the co-founder of Confluent who built the real-time data streaming platform that underpins much of Wall Street's infrastructure; Jay Chaudhry, the Himachal Pradesh-born founder of Zscaler, now among the wealthiest cybersecurity entrepreneurs alive; Hemant Taneja, the General Catalyst CEO steering one of the country's most ambitious venture funds; and Rakesh Gangwal, who co-founded IndiGo and once chaired US Airways.

Clean-energy pioneer K.R. Sridhar (Bloom Energy), Toast co-founder Aman Narang, Kiva co-founder Premal Shah, and investor Kavitark Ram Shriram round out a roster that covers practically every artery of the American economy.

## Why it matters to NRIs

For Indian Americans navigating a political climate that has often conflated immigration with economic anxiety, the Forbes list is a data point in an ongoing argument. The 26 Indian-origin leaders on the list collectively command companies and institutions worth trillions of dollars. They have generated millions of American jobs. And they arrived, almost without exception, through the country's higher education and skilled immigration system — the same pipeline that H-1B debates routinely threaten to constrict.

The list arrives in a year when Indian IT stocks have cratered 27%, when the Anthropic export ban has reminded Indian engineers of their geopolitical vulnerability, and when a federal judge has just struck down a proposed $100,000 H-1B fee. It is, in short, a reminder that the diaspora's contribution to American prosperity is not abstract. It is Photoshop. It is Azure. It is the semiconductor fab in Gujarat. It is the venture cheque that funded the next AI model. Forbes, for once, just counted."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Forbes Names 26 Indian-Origin Immigrants Among America's Most Successful. The List Reads Like a Tech Boardroom.",
    "subheadline": "From Vinod Khosla at No. 14 to Padma Lakshmi, Indian-born Americans dominate Forbes' 250th anniversary ranking of the nation's most impactful immigrants.",
    "slug": make_slug("forbes-250-immigrants-26-indian-origin-leaders"),
    "category": "technology",
    "vertical": "diaspora-achievement",
    "diaspora_angle": "26 Indian-origin leaders on America's top immigrants list is a data point in the H-1B and immigration debate — and a measure of how deeply the diaspora has shaped the US tech economy.",
    "tags": ["forbes", "indian-diaspora", "immigration", "silicon-valley", "vinod-khosla", "sundar-pichai", "satya-nadella"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "IndiaWest News", "url": "https://www.indiawest.com/"},
        {"name": "Forbes", "url": "https://www.forbes.com/"},
        {"name": "Gulte", "url": "https://www.gulte.com/"},
        {"name": "Founder News", "url": "https://foundernews.eu/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/2024-03-14_SXSW_Vinod-Khosla_08741.jpg/330px-2024-03-14_SXSW_Vinod-Khosla_08741.jpg",
    "image_caption": "Vinod Khosla at SXSW 2024, the highest-ranked Indian-origin leader on the Forbes list at No. 14",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body
}


# ─────────────────────────────────────────────
# ARTICLE 2: Meta-Reliance 168MW AI Data Centre
# ─────────────────────────────────────────────

art2_body = """Meta has signed its first built-to-suit data centre deal in India, and the name on the other side of the contract is Mukesh Ambani's Reliance Industries. The facility — a 168-megawatt hyperscale data centre in Jamnagar, Gujarat — will be built by Reliance and leased by Meta to run its AI workloads. It is, by any measure, a defining marker in India's emergence as a global AI infrastructure hub.

Mark Zuckerberg called the facility a way to "scale our AI infrastructure globally while deepening our long-term investment in India's economy." Ambani, characteristically, went bigger: "Building India's first built-to-suit AI data centre for a global technology leader of Meta's scale demonstrates India's readiness to be at the forefront of the global AI revolution."

## The Jamnagar advantage

The choice of Jamnagar is strategic, not accidental. The city is home to Reliance's flagship energy complex — one of the world's largest refining operations — and offers ready access to power, water, and heavy industrial infrastructure at a cost that most Indian cities cannot match. The data centre will run on renewable energy and use desalinated seawater for cooling, drawing on Reliance's existing renewable power assets at the complex.

Meta will bear the full cost of energy and water. The company has separately purchased more than 900 megawatts of clean energy in India through partnerships with CleanMax and Fourth Partner Energy. The data centre comes with an option to scale beyond 168 MW.

## A relationship that keeps deepening

The Jamnagar facility is the latest chapter in a relationship that began with Meta's $5.7 billion investment in Jio Platforms in 2020 — a bet that made Zuckerberg one of Ambani's most prominent backers. Last year, the two companies formed a joint venture to build AI platforms and enterprise tools using Meta's Llama models, committing a combined $90 million.

The data centre deepens this partnership from software into physical infrastructure. Reliance will provide end-to-end services spanning design, construction, utility management, network connectivity, and managed operations. Legal advisories were handled by Khaitan & Co (for Reliance) and Shardul Amarchand Mangaldas (for Meta), underscoring the complexity of the cross-border transaction.

## India's data centre gold rush

Meta is not alone. Amazon, Microsoft, and Google have all accelerated hyperscale data centre builds across India as New Delhi has rolled out aggressive incentives — including a 20-year-plus tax break for foreign companies using local data centres. In February, Reliance committed roughly $110 billion and Adani outlined $100 billion in investments to position India as an AI computing hub. India's data centre market is projected to nearly double to $13.11 billion by 2034, according to IMARC Group.

## The NRI angle

For Indian Americans in the technology industry, the Jamnagar data centre is a signal worth watching. It means that the AI models they build and train in Silicon Valley could, increasingly, run on Indian soil — powered by Indian renewable energy, cooled by Indian seawater, and managed by Indian infrastructure. It also means that Reliance, long seen as a conglomerate tethered to oil and telecom, is now a genuine player in the global AI infrastructure stack.

The deal also has implications for return-to-India calculations. As US tech companies build serious compute presence in India, the engineering talent that services, operates, and improves that infrastructure will need to be local. For NRIs weighing career options across borders, Jamnagar just became a data point on the map."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Meta's First AI Data Centre in India Will Run on Ambani's Renewable Grid. It's 168 Megawatts.",
    "subheadline": "Reliance will build, Meta will lease, and Jamnagar will become a landmark for hyperscale AI computing — powered by desalinated seawater and Gujarat sunshine.",
    "slug": make_slug("meta-reliance-jamnagar-ai-data-centre-168mw"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "India's emergence as a global AI infrastructure hub means the models NRIs build in Silicon Valley could increasingly run on Indian soil — and Jamnagar needs local engineering talent.",
    "tags": ["meta", "reliance", "data-centre", "ai-infrastructure", "mukesh-ambani", "jamnagar", "india-tech"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "TechCircle", "url": "https://www.techcircle.in/"},
        {"name": "DatacenterDynamics", "url": "https://www.datacenterdynamics.com/"},
        {"name": "Bar and Bench", "url": "https://www.barandbench.com/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/69/Mukesh_Ambani.jpg",
    "image_caption": "Mukesh Ambani, chairman and managing director of Reliance Industries",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body
}


# ─────────────────────────────────────────────
# ARTICLE 3: Adobe CEO Succession — Indian-Origin Candidates
# ─────────────────────────────────────────────

art3_body = """Shantanu Narayen has run Adobe for 18 years. When he announced in March that he would step down once a successor is named, the obvious question was who would replace one of the most consequential Indian-origin CEOs in Silicon Valley history. The answer, increasingly, looks like it could be another Indian-origin executive.

Bloomberg reported that the two leading internal candidates are David Wadhwani, president of Adobe's creativity and productivity unit, and Anil Chakravarthy, president of the customer experience orchestration business. Both are of Indian origin. Both have run significant companies before joining Adobe. And both are now in a succession race that will determine the direction of a $82-billion software giant navigating the most disruptive technology shift since the move to the cloud.

## The frontrunners

Wadhwani's path to the shortlist runs through AppDynamics, the application intelligence company he led as CEO before Cisco acquired it for $3.7 billion in 2017. He returned to Adobe in 2019 and now oversees the Creative Cloud and Document Cloud empire — the products that define Adobe for most of the world. Under his watch, Adobe has integrated Firefly, its generative AI image model, into Photoshop, Illustrator, and the broader creative suite.

Chakravarthy carries a different résumé. He holds a B.Tech from IIT Varanasi (now IIT BHU) and a PhD from MIT. Before Adobe, he was CEO of Informatica, where he led the company's transition to cloud and subscription services. At Adobe, he runs the Experience Cloud business — the enterprise platform that powers marketing operations for Fortune 500 companies. His unit has quietly crossed the $1 billion quarterly revenue mark.

## Why the succession matters now

Adobe is not in a comfortable spot. The stock has fallen more than 37% this year as investors question whether AI design tools from Figma, Canva, and the frontier AI labs could erode Adobe's creative monopoly. The company's CFO, Dan Durn, departed for Marvell Technology last week, compounding leadership uncertainty. Adobe has hired Heidrick & Struggles to run a parallel external search, with a preference for candidates who have experience developing or deploying AI products.

Yet the most recent earnings suggest the core business remains formidable. Revenue rose 13% to $6.62 billion in the second quarter, beating estimates. AI-first annual recurring revenue tripled and exceeded $500 million. Adobe raised its full-year forecast to $26.5-26.6 billion in revenue. The company is not dying; it is anxious about what comes next.

## The deeper pattern

If either Wadhwani or Chakravarthy gets the job, Adobe would mark a striking continuity: an Indian-origin CEO succeeded by another Indian-origin CEO at one of the world's most important software companies. That is not common, even in a Valley where Indian-origin leaders have become fixtures in the C-suite.

The precedent matters for NRI professionals watching from inside and outside the company. Adobe employs thousands of Indian-origin engineers and product managers in both the US and India. The choice of a new CEO — and whether that person is someone who shares the diaspora's background — will shape not just product strategy but the career calculus of an entire internal constituency.

Piper Sandler analyst Billy Fitzsimmons has said an internal appointment is "largely expected." Jefferies analyst Brent Thill has written that long-term investors may reward bold strategic moves from a new CEO. For Wadhwani and Chakravarthy, the stakes are the same: prove that Adobe can outrun AI, not be consumed by it. For the diaspora, the stakes are different — but no less real."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Adobe's Next CEO Could Be Indian-Origin Too. Two Candidates Are Already in the Ring.",
    "subheadline": "David Wadhwani and Anil Chakravarthy — both Indian-born, both presidents of Adobe's main business units — lead the internal race to succeed Shantanu Narayen.",
    "slug": make_slug("adobe-ceo-succession-wadhwani-chakravarthy-indian"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "An Indian-origin CEO succeeded by another at a $82B software giant would be unprecedented continuity — and signals the depth of Indian-origin leadership in US tech.",
    "tags": ["adobe", "ceo-succession", "shantanu-narayen", "david-wadhwani", "anil-chakravarthy", "indian-tech-leaders"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/"},
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/"},
        {"name": "Barchart", "url": "https://www.barchart.com/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/01/Shantanu_Narayen_-_the_CEO_of_Adobe_Inc.jpg",
    "image_caption": "Shantanu Narayen, Adobe's outgoing CEO after an 18-year tenure",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body
}


# ─────────────────────────────────────────────
# INSERT ALL
# ─────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
