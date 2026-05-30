#!/usr/bin/env python3
"""NRI World Writer — 2026-05-30 batch"""

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


# ── ARTICLE 1 ──────────────────────────────────────────────────────────────
art1_body = """The first thing to understand about the Indian Restaurant Congress landing in London is that it wasn't a vanity exercise. When the Congress & Awards held its inaugural international edition at the Royal Lancaster London on May 28, timed to coincide with India Week 2026, it was staking a claim on a market that has already moved far beyond tikka masala.

The United Kingdom is home to more than 12,000 Indian restaurants. They contribute an estimated £4–5 billion annually to the economy and support over 100,000 jobs. Those numbers alone would justify the attention. But the industry's trajectory tells a more interesting story — one that maps neatly onto the broader evolution of the Indian diaspora in Britain.

## From curry house to Michelin star

For decades, the British Indian restaurant was a particular thing: a neighbourhood curry house, often Bangladeshi-run, serving anglicised versions of Mughlai cuisine to post-pub crowds. That model created an entire ecosystem — a supply chain, a workforce pipeline, a cultural shorthand. It also became a constraint. Indian food in the UK was cheap, reliable, and invisible as cuisine.

That has changed, and the Congress acknowledged it. The event, organised by Scale Media International in association with Franchise India and Entrepreneur Asia Pacific, brought together operators, investors, and chefs who represent the new wave: Michelin-starred dining, premium casual concepts, chef-led brands, and scalable international businesses. The old curry house isn't dead, but it now shares the stage with restaurants that charge £80 a head and have six-week waiting lists.

## The diaspora demand engine

What's driving this isn't just British palates catching up. It's the diaspora itself. The 1.8 million people of Indian origin in the UK eat differently from their grandparents — not less Indian, but more discerningly so. They want regional specificity: Chettinad, not just "South Indian"; Lucknowi biryani, not generic rice. They're willing to pay for it, and they're vocal about quality.

This mirrors a pattern visible from Dubai to Sydney to Toronto: wherever Indian diaspora populations reach critical mass and economic confidence, the food scene upgrades. Indian restaurants in these cities are no longer catering to nostalgia. They're building brands.

## A global platform takes shape

The London edition is positioned as the opening move in a broader strategy. Scale Media International and Franchise India plan to replicate the Congress across major food capitals — a circuit that could eventually connect London, Dubai, Singapore, and New York under a single industry umbrella.

The timing matters. Cross-border franchising of Indian restaurant brands has accelerated sharply. Chains like Dishoom, which started in London's Shoreditch, now operate in Edinburgh, Manchester, Birmingham, and have plans for international expansion. Indian street food concepts — Chaiiwala, Wrapchic, Tiffin Box — are scaling through franchise models that would have seemed implausible a decade ago.

The Congress also arrives at a moment when Indian cuisine is receiving institutional recognition that was long withheld. In 2025, the UK saw its highest-ever number of Indian restaurants receive Michelin recognition. Three hold stars; dozens more feature in the guide's broader recommendations.

## What's at stake

For the diaspora restaurateur, the message from India Week London was clear: the infrastructure of a global Indian hospitality industry is being built, and those who want a seat at the table should show up now. For the diner — whether in Southall or Soho — the implications are more immediate. The curry house era gave Britain a cheap and wonderful thing. What comes next will cost more, taste sharper, and look nothing like what your parents ordered after the pub."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Indian Restaurant Congress Just Went International. London Was the Obvious First Stop.",
    "subheadline": "India Week 2026 hosted the industry's first global summit at the Royal Lancaster London. With 12,000 Indian restaurants and £4–5 billion in annual revenue, the UK market has outgrown the curry house era.",
    "slug": make_slug("indian-restaurant-congress-london-india-week-global"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The UK's Indian restaurant industry is a diaspora creation — built by immigrants, scaled by their children, and now being institutionalised through global platforms that connect operators from London to Dubai to Singapore.",
    "tags": ["nri", "diaspora", "indian-restaurants", "uk", "india-week", "london"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "LatestLY / BusinessWire India", "url": "https://www.latestly.com/agency-news/business-news-indian-restaurant-congress-goes-global-with-landmark-london-edition-during-india-week-2026-6685131.html"},
        {"name": "The News This Week UK", "url": "https://thenewsthisweek.co.uk/indian-restaurant-congress-goes-global-with-landmark-london-edition-during-india-week-2026/"},
        {"name": "Restaurant India", "url": "https://www.restaurantindia.in/"}
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/34080434/pexels-photo-34080434.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art1_body,
}


# ── ARTICLE 2 ──────────────────────────────────────────────────────────────
art2_body = """Somewhere in Washington DC, an investment firm called Avni LLC is claiming it has the answer to one of the more embarrassing problems in Indian sport: the country of 1.4 billion people cannot watch the FIFA World Cup.

The 2026 tournament kicks off on June 11 in the United States, Mexico, and Canada. As of late May, India — which has an estimated 300 million football fans and a rapidly growing viewership base — does not have a confirmed broadcaster. No television deal. No streaming agreement. Nothing.

## The DC bid

Avni LLC, led by president and CEO Deelip Mhaske, says it submitted a corporate guarantee backed by financial commitments exceeding $300 million in February 2026 as part of FIFA's closed tender process for the Indian subcontinent. The firm claims an associated partner secured the winning bid after competing against several major Indian broadcasters.

The pitch goes beyond conventional television. Mhaske envisions a model built around OTT platforms, AI-powered multilingual broadcasting, mobile micro-subscriptions, and esports integrations across Asia. "The Indian subcontinent alone has the ability to exceed initial valuation expectations," he told The Indian Eye.

It is, on paper, exactly the kind of diaspora entrepreneurship story that makes headlines: an Indian American firm leveraging its position between two markets, bringing Silicon Valley thinking to an old-media problem. Whether it translates into actual broadcasts on June 11 is another matter.

## Why India has no broadcaster

The backdrop is instructive. FIFA initially valued the India broadcasting rights package for the 2026 and 2030 World Cups at around $100 million. There were no takers. The price was reportedly slashed to roughly $35 million. Still no final agreement.

The contrast is stark. China's state broadcaster CMG sealed a comprehensive deal with FIFA on May 15. Most major football markets locked in their rights months or years ago. India's situation reflects a fundamental tension: the sport is growing fast in viewership but hasn't yet produced the advertising revenue that justifies premium rights costs for Indian broadcasters.

For the NRI community — many of whom live in World Cup host cities across the United States and will attend matches in person — the irony cuts deep. They can walk into the stadium but their families back in India might not be able to watch.

## The courts step in

The Delhi High Court has now entered the picture. Justice Purushaindra Kumar Kaurav issued notice to the Centre and Prasar Bharati on a petition seeking directions to ensure the World Cup is broadcast in India, specifically through free-to-air platforms like Doordarshan and DD Sports.

The petition, filed by advocate Avdhesh Bairwa, argues that depriving millions of football fans from watching the tournament would violate their right to access sporting events of national importance. It's a legally interesting argument, and it reflects genuine public anxiety.

## The diaspora angle

For Indian Americans, this story sits at an uncomfortable intersection. The World Cup is coming to their backyard — literally. Matches will be played in New York, San Francisco, Dallas, Houston, Atlanta, and other cities with large Indian populations. Indian diaspora businesses will advertise, host watch parties, and celebrate.

Meanwhile, their relatives in Mumbai and Kolkata — cities where football fandom runs deep — may face a total blackout.

Avni LLC's bid, whatever its ultimate outcome, highlights something real: the Indian diaspora is increasingly willing to step into gaps that Indian domestic players have left open. Whether that's building technology companies, acquiring media rights, or launching restaurant franchises, the pattern is the same. The diaspora sees an opportunity that the home market has underpriced.

FIFA has said only that discussions in India "are ongoing and must remain confidential at this stage." The clock, meanwhile, keeps ticking."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "An Indian American Firm Just Bid $300 Million for FIFA World Cup India Rights. The Bigger Story Is Why India Still Doesn't Have a Broadcaster.",
    "subheadline": "With the tournament two weeks away and no Indian deal in sight, a Washington DC-based investment firm is making an audacious play — while the Delhi High Court asks why 1.4 billion fans might face a total blackout.",
    "slug": make_slug("avni-llc-fifa-world-cup-india-broadcasting-rights-diaspora"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "An Indian American investment firm from Washington DC is stepping into a gap that Indian domestic broadcasters have left open — a pattern increasingly visible across diaspora entrepreneurship, from media rights to restaurant franchises to technology ventures.",
    "tags": ["nri", "diaspora", "fifa", "world-cup", "broadcasting", "indian-american"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/21/indian-american-firm-claims-fifa-india-rights/"},
        {"name": "Delhi High Court petition (reported)", "url": "https://theindianeye.com/2026/05/21/indian-american-firm-claims-fifa-india-rights/"},
        {"name": "SOFX.com (UAE/FIFA context)", "url": "https://sofx.com/"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4777979/pexels-photo-4777979.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art2_body,
}


# ── ARTICLE 3 ──────────────────────────────────────────────────────────────
art3_body = """The India Philanthropy Alliance's Youth Essay Competition is now in its seventh year. That fact alone is worth pausing on. In a diaspora landscape littered with one-off galas, annual dinners that serve mainly as networking events, and mentorship programs that fizzle after their founding cohort, something that has run continuously since 2020 and is still growing deserves attention.

This year's theme is #YouthWithPurpose. The premise is straightforward: middle school and high school students across the United States are invited to identify an area of need in India and write a well-researched personal essay proposing solutions. Essays are judged anonymously by a panel of philanthropists, nonprofit professionals, and — in a nice generational touch — past competition winners.

The top essays win grant money that students can direct to an Indian nonprofit of their choosing. It sounds simple. The results have been anything but.

## The case for the dinner table

Raj Gupta, the former chairman and CEO of Rohm and Haas who co-authored a recent Indiaspora blog post about the competition, frames it in terms that would resonate with any NRI parent: the essay competition "helps spur dinner-table conversations between the generations about all the benefits of generosity."

That framing is deliberate. The Indian American community's philanthropic relationship with India is complicated and evolving. A 2025 Dalberg report, produced in partnership with IPA and Indiaspora, found that diaspora giving to India had significantly increased since 2018 — but also identified youth engagement as a major untapped opportunity.

The second generation isn't ungenerous. But their connection to India is different from their parents'. They may have visited grandparents in Hyderabad or Jaipur, but they didn't grow up there. Their sense of obligation is mediated through family stories, not direct experience. A competition that asks them to research an Indian problem, write about it personally, and then direct real money to a real organisation bridges that gap in a way that a gala dinner never could.

## What the essays reveal

The winning entries offer a window into what diaspora youth actually care about — and it's rarely what their parents might expect.

Aneesh Gupta, the 2025 high school winner, wrote about unregistered births in India. His essay, titled "India's Invisible Children and the Fight for Recognition," examined how millions of Indian children who lack birth certificates face lifelong barriers to education, healthcare, and legal identity. He directed his $1,000 grant to CRY America.

Esha Kondapalli, the 2025 middle school winner, tackled India's rabies epidemic. "I entered IPA's Youth Essay Competition because of my deep passion for writing," she said afterward. "Writing has always been my way of expression, especially on issues I care about."

These aren't safe topics. They're specific, researched, and reflect genuine curiosity about a country these students know primarily through family ties.

## Building institutional muscle

The competition has begun to develop the kind of institutional connective tissue that turns a program into a pipeline. This year, for the first time, the top ten high school finalists will be invited to participate in the World Food Prize Global Youth Institute in Des Moines, Iowa. Winners will present at the Indiaspora and IPA Philanthropy Summit in Dallas in September.

Past winners have joined IPA's Youth Leadership Council, run fundraising campaigns for India Giving Day, and served as interns. One former winner, Eisha Yadav, who won the middle school category in 2021, recently wrote to organisers to share that she's heading to UC Berkeley to study computer science — and credited the competition with giving her "new confidence and insights."

The new Deepak Raj Rising Star Award, launching in 2026 for someone under 40, extends this logic further up the age ladder. Nominations for the inaugural award close June 30.

## Why it matters

The Indian American community is the highest-earning ethnic group in the United States, with a median household income above $150,000. Its philanthropic capacity is enormous. But sustaining generosity across generations requires more than wealth transfer — it requires meaning transfer. That's harder, slower work.

IPA's essay competition won't solve the problem by itself. But it represents one of the more thoughtful attempts to give diaspora youth a personal stake in India's challenges — through the unglamorous but durable medium of writing. In a community that sometimes defaults to STEM competitions and spelling bees as the primary vehicle for youth achievement, that's a quietly radical choice."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "An Essay Competition Is Quietly Teaching Indian American Kids to Care About India. It's Working.",
    "subheadline": "The India Philanthropy Alliance's Youth Essay Competition is in its seventh year. Past winners have directed grants to Indian nonprofits, joined leadership councils, and landed at UC Berkeley. The real product is dinner-table conversations between generations.",
    "slug": make_slug("ipa-youth-essay-competition-diaspora-philanthropy"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The competition addresses a core diaspora challenge: how do you sustain philanthropic engagement with India across generations when the second generation's connection to the country is mediated through family stories rather than direct experience?",
    "tags": ["nri", "diaspora", "philanthropy", "youth", "ipa", "indiaspora", "essay-competition"],
    "urgency": "low",
    "sources": json.dumps([
        {"name": "Indiaspora Blog", "url": "https://indiaspora.org/engaging-diaspora-youth-through-creative-writing/"},
        {"name": "India Philanthropy Alliance", "url": "https://www.indiaphilanthropyalliance.org/"},
        {"name": "Dalberg Report 2025 (via Indiaspora)", "url": "https://dalberg.com/"}
    ]),
    "score_total": 68,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8005016/pexels-photo-8005016.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art3_body,
}


articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. Published {len(articles)} articles at {now}")
