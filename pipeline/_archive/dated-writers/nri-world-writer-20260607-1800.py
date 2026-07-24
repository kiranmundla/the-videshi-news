#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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
    {
        "id": str(uuid.uuid4()),
        "headline": "India Leads the World in Building America's Billion-Dollar Startups. The Numbers Are Not Even Close.",
        "subheadline": "A new study finds Indian immigrants have founded 96 US unicorns — more than Israel, the UK and China combined at the top. Six Indians are among 15 immigrants who built two or more billion-dollar companies.",
        "slug": make_slug("india-leads-unicorn-founders-nfap-study-96-billion-dollar-startups"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The NFAP study quantifies what the diaspora has long sensed: Indian immigrants are not just filling jobs in America but creating the companies that define its economic future, from cybersecurity to AI to aviation.",
        "tags": ["nri", "diaspora", "startups", "unicorns", "silicon-valley", "indian-american", "entrepreneurs"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "LiveMint", "url": "https://www.livemint.com/news/world/indian-immigrants-built-96-unicorns-in-america-now-worth-more-than-germanys-stock-market-11780642420018.html"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/data-stories/india-is-largest-source-for-immigrant-founders-of-us-unicorns-but-still-not-shooting-for-the-stars/article71065983.ece"},
            {"name": "National Foundation for American Policy (NFAP)", "url": "https://nfap.com/"},
            {"name": "Inshorts", "url": "https://inshorts.com/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/b/b1/Jay_Chaudhry.png",
        "image_caption": "Jay Chaudhry, founder of Zscaler and the wealthiest Indian immigrant startup founder in America",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """India has produced more founders of American billion-dollar startups than any other country on Earth, and the gap is widening.

A new analysis by the National Foundation for American Policy, published in the first week of June, examined the origins of founders across all 775 US unicorn companies as of April 2026. Indian immigrants came out on top with 96 billion-dollar companies to their name. Israel placed a distant second with 60, followed by the United Kingdom at 47 and China at 41.

The sheer scale demands a pause. Of approximately five million Indian immigrants in America, roughly one in every 50,000 has founded a company valued at a billion dollars or more. That ratio, applied to a community best known for H-1B employment and corporate leadership, reveals a parallel entrepreneurial engine that most policy debates overlook entirely.

## The wealth they built

The collective valuation of the 455 immigrant-founded unicorn companies stands at $5 trillion — a figure exceeding the total stock market capitalisation of all but seven countries, including the United Kingdom and Germany. Indian-founded companies represent a significant share of that staggering sum.

Jay Chaudhry, who grew up in Panoh, a village in Himachal Pradesh without running water, leads the wealth table with a net worth of $13.1 billion as founder and CEO of cybersecurity giant Zscaler. Vinod Khosla, who studied at IIT Delhi before co-founding Sun Microsystems and launching Khosla Ventures, follows at $9.2 billion. Rakesh Gangwal, co-founder of IndiGo and former chairman of US Airways, sits at $6.6 billion.

Perplexity, the AI search company founded by Aravind Srinivas just over three years ago, is the highest-valued US unicorn with an Indian founder at $20 billion — ranked twelfth among all American unicorns.

## Serial builders

Perhaps the most telling detail in the NFAP data: six of the 15 immigrants worldwide who have built two or more billion-dollar companies were born in India. They are Mohit Aron, Jyoti Bansal, Ashutosh Garg, Arvind Jain, Sachin Nayyar and Ajeet Singh. No other country produces serial unicorn founders at this rate.

The student pipeline fuels the machine. Some 76 Indian-born international students have gone on to found unicorns after studying in the US, accounting for a substantial portion of the 183 student-founded unicorn companies that collectively employ an average of 1,123 workers each.

## The ambition gap

Not everyone sees an unqualified triumph. Indian-founded unicorns tend to cluster below $10 billion in valuation. The highest-valued unicorns with immigrant founders — SpaceX at $1.5 trillion, Anthropic at $965 billion, OpenAI at $852 billion — were all started by founders from other countries.

"Given the relatively humble backgrounds Indians grew up in, they are less likely to shoot for the stars like an Elon Musk would do," observes Arun Natarajan, founder of Venture Intelligence. "However, serial entrepreneurs of Indian-origin, especially those well set financially after exiting their first ventures, are often more ambitious."

The structural obstacle is real. H-1B holders face cumbersome restrictions on starting and running ventures — a constraint that disproportionately affects Indians, who wait the longest for employment-based green cards. The NFAP report frames its findings explicitly within tightening immigration policy, concluding that restricting immigrant pathways carries a measurable economic cost: without foreign-born founders, America would likely have fewer than half as many billion-dollar companies.

## What the diaspora built

For the NRI community, these numbers are more than an economic footnote. They represent a generation of immigrants who arrived with engineering degrees and modest savings and built enterprises that now employ tens of thousands. SpaceX leads all immigrant-founded unicorns with 25,700 workers, but the Indian-founded companies — Cohesity, FalconX, Rippling, Carta — are growing fast.

The question is whether America's immigration system will continue to let them in. If the NFAP data is any guide, the answer matters to the tune of $5 trillion."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Sunil Gavaskar Auctioned His Cricket Bats for Blind Children. The Diaspora Wrote the Cheques.",
        "subheadline": "At back-to-back galas in New Jersey, two Indian American foundations raised nearly $1 million to fight blindness in India — continuing a tradition of diaspora philanthropy that has restored sight to millions.",
        "slug": make_slug("gavaskar-sankara-eye-foundation-gala-diaspora-philanthropy-blindness"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "These twin galas illustrate the quiet machinery of NRI philanthropy — professionals and entrepreneurs in America funding eye surgeries, training doctors, and building hospitals across India, one fundraiser dinner at a time.",
        "tags": ["nri", "diaspora", "philanthropy", "healthcare", "eye-care", "sunil-gavaskar", "sankara-eye-foundation"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian EYE", "url": "https://theindianeye.com/"},
            {"name": "India Tribune", "url": "https://www.indiatribune.com/public/eye-foundation-of-america-raises-hope-for-a-world-without-childhood-blindness-at-charity-gala-in-new-jersey"},
            {"name": "Sankara Eye Foundation USA", "url": "https://www.giftofvision.org/"},
            {"name": "Eye Foundation of America", "url": "https://www.eyefoundationofamerica.org/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/3d/Anu_Ranjan%2C_Amruta_Fadnavis%2C_Sunil_Gavaskar%2C_Shashi_Ranjan_graces_the_Gr8_Beti_event_%2802%29_%28cropped_-_Gavaskar%29.jpg",
        "image_caption": "Sunil Gavaskar, cricketing legend and guest of honour at the Sankara Eye Foundation USA gala",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """The ballroom math at Indian American charity galas follows a familiar pattern: seat 300 doctors, engineers and entrepreneurs at round tables, serve paneer and promises, and pass around pledge cards. What makes the recent season of eye-care fundraisers remarkable is not the formula but the scale — and the star power.

At the Sankara Eye Foundation USA's annual donor appreciation gala, the guest who drew the loudest applause was not a tech CEO or a congressman. It was Sunil Gavaskar, the man who once faced the West Indian fast bowling attack with a prayer and a straight bat, and who now wields his fame to fight a quieter enemy: curable blindness in India.

## Bats for sight

Gavaskar did more than give a speech. He offered autographed cricket bats to donors contributing over $5,000, and bats plus his authored books to those giving $10,000 or more. The gesture triggered what organisers described as "an outpouring of generous donations."

"Just as a cricketer's vision is crucial on the field, sight is vital to living a full life," Gavaskar told the audience. "Sankara Eye Foundation is giving people a chance to regain that fundamental gift."

Sitting beside Gavaskar on the fireside chat stage was Srikanth Bolla, the CEO of Bollant Industries, who was born visually impaired and fought a legal battle to win the right to study STEM in India. Bolla's story — from denied college admission to founding a manufacturing company that employs hundreds — embodied the foundation's thesis: that sight, in both the physical and metaphorical sense, is a precondition for everything else.

The Sankara Eye Foundation USA, headquartered in San Jose, California, has maintained a four-star rating from Charity Navigator for nine consecutive years. It channels diaspora donations into a growing network of free eye hospitals across India, with a stated goal of reaching one million free surgeries.

## Across town, $900,000 for baby eyes

Weeks earlier, another Indian American foundation held its own gala barely 30 miles away. The Eye Foundation of America hosted an elegant fundraiser at The Imperia in Somerset, New Jersey, raising $900,000 with the help of matching funds — the largest single-event haul in recent memory for the 49-year-old organisation.

Dr V.K. Raju, the foundation's founder and a world-renowned ophthalmologist, spoke about a specific frontier: Retinopathy of Prematurity, a condition that silently steals sight from premature babies. In India, where 3.5 million premature births occur annually, an estimated 200,000 children are at risk.

"Every child deserves to see the world with clarity and purpose," Dr Raju told attendees. "The greatest challenge is ensuring these life-changing treatments are accessible and affordable to the millions of children who need them most."

The numbers behind EFA are staggering for a diaspora-funded operation: 2.5 million patients served, more than 340,000 vision-saving surgeries performed — including over 30,000 on children — across partnerships in more than 30 countries. What began as a mission focused on southern India has grown into a global network.

## The machinery of giving

These twin galas illuminate a pattern that rarely makes headlines. Indian American philanthropy has surged in recent years, with total diaspora giving estimated at $4 to $5 billion annually. Healthcare, particularly eye care, remains a cornerstone cause — perhaps because the outcomes are so tangible. A $300 donation funds a cataract surgery. A $50,000 pledge equips a screening centre.

The pipeline from American banquet hall to Indian operating theatre runs on volunteer energy. Sankara Eye Foundation's chapters in New York and New Jersey are entirely volunteer-run. The Eye Foundation of America's board trustees — Sam Maddali, Sekhar Vemparala, Srinu Maddula — are entrepreneurs and professionals who organise fundraisers between their day jobs.

Dr Srinu Maddula captured the philanthropic logic in a single sentence: "When you help a baby open her eyes for the first time, you truly change the world — one baby at a time, one family at a time, one village at a time."

For the diaspora, these evenings are more than charity events. They are the clearest expression of a community that has prospered abroad and is determined to send something back — not just remittances, but sight itself."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
