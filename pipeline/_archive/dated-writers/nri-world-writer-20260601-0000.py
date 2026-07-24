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
        "headline": "The US Trade Negotiator Lands in Delhi Tomorrow. For Five Million Indian Americans, the Subtext Is Personal.",
        "subheadline": "A four-day sprint to finalise the India-US Bilateral Trade Agreement begins June 1, with Ambassador Gor predicting a signed deal within weeks. For the diaspora that bridges a $220 billion trading relationship, the stakes extend far beyond tariffs.",
        "slug": make_slug("us-india-bta-trade-deal-brendan-lynch-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian Americans are the human infrastructure of a $220 billion bilateral trade relationship. Every tariff line, every customs facilitation clause, every investment promotion chapter in the BTA touches NRI-owned businesses, IT professionals on work visas, and the remittance corridors that connect the two economies.",
        "tags": ["nri", "diaspora", "trade", "us-india", "bilateral-trade-agreement"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/india-us-chief-negotiators-to-hold-four-day-trade-talks-from-june-1/article71044288.ece"},
            {"name": "DevDiscourse", "url": "https://www.devdiscourse.com/article/business/3925917-us-india-to-advance-trade-agreement-negotiations-in-june"},
            {"name": "The Indian EYE", "url": "https://theindianeye.com/2026/05/31/ambassador-gor-expresses-confidence-over-us-india-trade-deal/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/6077239/pexels-photo-6077239.jpeg",
        "body": """When Brendan Lynch, the US Chief Negotiator for trade, touches down in New Delhi on Monday for four days of talks with his Indian counterpart Darpan Jain, the formal agenda will read like any trade negotiation: market access, non-tariff barriers, customs facilitation, investment promotion, economic security alignment. The informal agenda is rather more urgent. Both governments want a deal, and both know the window is narrowing.

The framework for the India-US Bilateral Trade Agreement was announced on February 7, when the two sides issued a joint statement agreeing on an interim pact. Under that framework, Washington had offered to reduce tariffs on Indian goods from 50 per cent to 18 per cent and to scrap the punitive 25 per cent levy imposed over India's Russian oil purchases. India, for its part, proposed eliminating or cutting tariffs on all US industrial goods and a wide range of agricultural products, from tree nuts to wine and spirits.

Then the ground shifted. The US Supreme Court struck down President Trump's sweeping reciprocal tariffs in late February. A blanket 10 per cent tariff on all countries followed. The carefully negotiated numbers suddenly needed recalibrating.

## Why the diaspora should be watching closely

Bilateral trade between the two countries now stands at approximately $220 billion in goods and services — up from $20 billion two decades ago. Ambassador Sergio Gor, speaking in New Delhi last week, called the trajectory remarkable and predicted a signed deal "over the next few weeks and months."

That $220 billion figure is not abstract for Indian Americans. It runs through the consulting firms they own, the IT services companies where they work, the import-export businesses they operate between Houston and Hyderabad, the pharmaceutical supply chains they manage, and the technology partnerships they navigate daily. When Lynch and Jain sit down to discuss "investment promotion," they are discussing the regulatory terrain that shapes whether an Indian American entrepreneur can open a manufacturing unit in Gujarat or a joint venture in Texas without tripping over conflicting compliance regimes.

India has signalled its willingness to purchase $500 billion worth of US energy products, aircraft, precious metals, technology goods, and coking coal over the next five years. For NRI investors already channelling money into Indian infrastructure, energy, and technology sectors, these commitments create new corridors of opportunity — and new questions about how tariff structures will affect their returns.

## The Section 301 shadow

Not everything is optimistic. In March, the US Trade Representative launched two Section 301 investigations targeting India over excess capacity and labour practices. India has rejected the allegations, calling the probes unsupported. But the investigations hang over the negotiations like an uninvited guest, reminding both sides that the relationship, however warm diplomatically, remains transactional at its core.

For Indian American professionals — many of whom sit in the crosshairs of both trade and immigration policy — the message is familiar: you are valued economically, scrutinised politically, and navigated around legally. The same community that contributes up to 6 per cent of all US income taxes while constituting 1.5 per cent of the population finds itself, once again, caught in the friction between two governments trying to extract maximum advantage from each other.

## The numbers that matter

India's outbound shipments to the US grew a marginal 0.92 per cent to $87.3 billion in the 2025-26 fiscal year. Imports from the US rose 15.95 per cent to $52.9 billion. The trade surplus — long a sore point in Washington — narrowed from $40.89 billion to $34.4 billion. These are the numbers Lynch will carry into the negotiating room. The question is whether the final text will reflect the reality that Indian Americans are not bystanders to this trade but participants in it.

The four days in Delhi will not produce a final agreement. But they may produce something nearly as important: a signal about whether the world's oldest democracy and its largest one can move from framework to fine print before the political calendar makes it impossible. For five million Indian Americans living inside that hyphen, the answer is not academic."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Americans Pay Up to $300 Billion in US Taxes. Congress Wants to Tax Their Remittances Too.",
        "subheadline": "An Indiaspora-BCG report quantifies what the diaspora has long suspected: Indian Americans punch absurdly above their weight. The question is whether that economic clout translates into political protection — especially now.",
        "slug": make_slug("indiaspora-bcg-indian-american-tax-economic-clout-remittance"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "This is the diaspora's own report card — 5.1 million people paying $250-300 billion in taxes, running 16 Fortune 500 companies, co-founding 72 unicorns, holding 10% of US patents. And yet the community faces a new remittance tax and continued visa uncertainty. The gap between contribution and recognition is the core NRI story.",
        "tags": ["nri", "diaspora", "taxes", "indiaspora", "economic-impact", "remittance-tax"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Indiaspora / Boston Consulting Group", "url": "https://indiaspora.org"},
            {"name": "The Indian EYE", "url": "https://theindianeye.com/2024/06/26/small-community-big-contributions-as-indian-americans-pay-about-5-6of-all-income-taxes-in-the-us/"},
            {"name": "HDFC International Life", "url": "https://www.hdfclife-international.com/blog/us-remittance-tax-nri-impact"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/7581114/pexels-photo-7581114.jpeg",
        "body": """The numbers, once you see them laid out, have a kind of quiet absurdity. Indian Americans constitute 1.5 per cent of the US population. They pay between 5 and 6 per cent of all income taxes collected by the federal government. In dollar terms, the 5.1 million-strong Indian diaspora contributes approximately $250 to $300 billion in income taxes annually. Of those 5.1 million, 2.8 million are first-generation immigrants — people who arrived with suitcases, credentials, and a willingness to build from scratch.

These figures come from the Indiaspora-Boston Consulting Group report titled "Small Community, Big Contributions," the first data-driven attempt to map the Indian American economic footprint across five dimensions: economic, scientific, social, cultural, and civic. The report's tagline borrows from the Tamil poet Kaniyan Pungundranar: "Every town is my town, and all the people in the world are my kin." It is an ancient sentiment deployed to frame a thoroughly modern reality.

## The CEO corridor

Sixteen Indian-origin executives lead Fortune 500 companies. Microsoft's Satya Nadella. Alphabet's Sundar Pichai. Vertex Pharmaceuticals' Reshma Kewalramani, the first woman CEO of a major US biotech firm. Collectively, these sixteen employ 2.7 million Americans and generate nearly $1 trillion in annual revenue. That is not representation — it is structural economic power embedded at the highest tier of American capitalism.

Below the Fortune 500 tier, the picture is equally striking. Indians have co-founded 72 of the 648 US unicorn companies operating as of the last count — startups valued at over $1 billion. Those 72 companies employ more than 55,000 people and carry a combined valuation of $195 billion. Between 1975 and 2019, the share of US patents involving Indian-origin innovators rose from 2 per cent to 10 per cent. In 2023, research groups with Indian-origin scientists claimed 11 per cent of all National Institutes of Health grants and contributed to 13 per cent of the country's scientific publications.

Roughly 150 Indian Americans hold notable positions in the federal government. The community's presence extends from the World Bank presidency, held by Ajay Banga, to congressional offices, state legislatures, and federal advisory boards.

## The remittance paradox

Against this backdrop, the US Senate's decision to impose a remittance tax — reduced from an initially proposed 5 per cent to 1 per cent under the "One Big Beautiful Bill Act" — carries a particular sting. The tax, effective after December 31, 2025, applies to international money transfers by non-citizens, including H-1B holders, green card applicants, and international students.

The exemptions are narrow but significant: transfers from US bank accounts and US-issued debit or credit cards are excluded. This means most NRIs using mainstream channels — Wise, Remitly, ICICI Money2India, or bank wires — should be unaffected, provided the transfer originates from a US-based financial source. But the principle remains uncomfortable. A community that pays up to $300 billion in taxes is now being asked to pay an additional surcharge for sending money to ageing parents in Pune or investing in property in Bangalore.

For high-net-worth NRIs, the tax is a rounding error. For H-1B workers supporting extended families across two continents, it is a symbolic slap — a reminder that economic contribution does not automatically confer political consideration.

## The giving gap

The Indiaspora report also surfaces a less flattering dimension: philanthropy. Indian Americans donate an estimated $4 to $5 billion annually, according to a companion Indiaspora-Dalberg survey. That sounds generous until you compare it to the community's giving potential. If Indian Americans donated at the same rate as the broader US population — roughly 4 per cent of income — they could be giving $5 to $6 billion. The giving gap has narrowed from earlier estimates of $2 to $3 billion, but it persists.

The gap is partly cultural, partly structural. Indian philanthropy has historically flowed through informal channels — temple donations, community fundraisers, direct transfers to relatives — that rarely show up in formal accounting. Younger Indian Americans are changing this, channelling money through organised initiatives like India Giving Day, now in its fourth year, and the India Philanthropy Alliance.

## What the numbers cannot buy

The Indiaspora report makes its case with data. But data, in Washington, is not the same as leverage. Indian Americans have the economic profile of a community that should be untouchable — too productive to tax punitively, too integrated to ignore, too successful to dismiss. And yet the remittance tax passed. And yet H-1B uncertainty continues. And yet the community's political infrastructure, while growing, remains thinner than its economic footprint would suggest.

The numbers tell a story of extraordinary contribution. They do not yet tell a story of proportionate influence. That is the gap the diaspora has not figured out how to close."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Gujarati Community Meal in Blackburn Got One Million Views on X. The Caption Was a Lie.",
        "subheadline": "When a video of the Bharuchi Vahora UK Association's annual meeting went viral as supposed footage of a British city council, Reuters had to step in. The episode is a small thing — and a symptom of something much larger.",
        "slug": make_slug("bharuchi-vahora-uk-blackburn-viral-misinformation-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The viral misrepresentation of a routine Indian community gathering as a 'takeover' of British institutions reflects a broader pattern of anti-Indian and anti-immigrant disinformation targeting diaspora communities in the UK, amplifying far-right narratives and forcing communities to defend their mere existence.",
        "tags": ["nri", "diaspora", "uk", "misinformation", "community", "anti-indian"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters Fact Check", "url": "https://www.reuters.com/fact-check/video-indian-community-gathering-miscaptioned-uk-city-council-meeting/"},
            {"name": "Vahora Voice UK", "url": "https://www.vahoravoice.co.uk"},
            {"name": "Asian Voice", "url": "https://www.asian-voice.com"}
        ]),
        "score_total": 74,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/14625337/pexels-photo-14625337.jpeg",
        "body": """The video is entirely mundane. Dozens of men sit at two long tables in a community centre in Blackburn, northwest England. Some wear suits. Others wear Islamic headwear. They are eating rice and curry — a traditional meal of the region, as the community centre's spokesperson later put it with admirable understatement. It is the annual meeting of the Bharuchi Vahora UK Association, a Sunni Muslim group descended from the Bharuch region of India's Gujarat state, held on Sunday, May 17.

By the following day, the footage had been posted on X with a caption that read: "Believe it or not. This is a UK city council members meeting." The post received one million views. Near-identical claims spread across Facebook. Nobody, apparently, thought to check.

Reuters did check. The footage matched pictures of the conference room at Bangor Street Community Centre, which advertises itself for hire online. A spokesperson confirmed: "The people are of a Gujarati background and tucking into some rice and curry. It has nothing to do with the council in any way." The video was traced to an Instagram post by the Bharuchi Vahora UK Association itself, which had simply documented its own annual gathering.

## The mechanics of a lie

The anatomy of this particular misinformation episode is worth examining, not because it is unusual but because it is so ordinary. A community event is filmed. The footage is stripped of context. A caption is added that transforms a private meal into evidence of institutional capture. The implication — that British councils are being "taken over" by Indian and Muslim communities — does not need to be stated explicitly. The image does the work.

The Bharuchi Vahora community has roots in England stretching back to the 1950s, when members settled in Lancashire and Yorkshire for work. They are, by any measure, part of the fabric of northern England. But in the grammar of far-right misinformation, longevity of presence counts for nothing. The community is perpetually arriving, perpetually foreign, perpetually on the verge of some imagined takeover.

## A pattern, not an anomaly

The Blackburn video did not emerge in a vacuum. It landed in a media environment already primed by a series of confrontations between Indian and South Asian communities and nativist movements across the anglosphere.

In Leicester, Holi celebrations that had run for four decades were disrupted when fire service support was withdrawn at the last moment, leaving organisers unable to safely complete the ceremonial Holika Dahan fire. Organisers and local councillors questioned the timing. In London's Hammersmith, a restaurant that served as a cultural anchor for the Indian diaspora announced it would close after sixteen years. Across the Atlantic, in Frisco, Texas, city council meetings have been overtaken by residents invoking "great replacement" rhetoric to oppose Hindu temple zoning applications. A far-right figure told the council that "the Hindus and the Muslims are teaming up to take over Texans."

The specifics vary. The structure does not. A community that has lived somewhere for decades — sometimes generations — is recast as an invader. Routine cultural activity is reframed as evidence of a larger conspiracy. And the communities themselves are forced into a defensive posture, spending energy proving that a meal is just a meal, a temple is just a temple, a festival is just a festival.

## The cost of correction

Reuters debunked the Blackburn video within days. The correction will reach a fraction of the million people who saw the original post. This asymmetry — between the speed of misinformation and the reach of correction — is well documented, and the Indian diaspora is not its only victim. But the pattern has a particular edge when it targets communities that are already navigating questions of belonging in post-Brexit Britain.

The UK's Indian-origin population is the country's largest ethnic minority, with 26 Indian-origin Members of Parliament in the current House of Commons. The community's economic, cultural, and political integration is not in question to anyone paying attention. But misinformation does not require attention. It requires only a caption, a platform, and an audience predisposed to believe the worst.

## What a community centre can teach us

The Bangor Street Community Centre did not issue a lengthy rebuttal. It did not launch a social media campaign. It confirmed the facts and moved on. The Bharuchi Vahora UK Association, for its part, had simply posted its own event on Instagram — a transparent act that became raw material for a lie.

There is something clarifying about the ordinariness of all this. The community was not doing anything remarkable. It was eating dinner. The misinformation was not sophisticated. It was a false caption on a stolen video. And the correction, when it came, was not dramatic. It was a spokesperson saying, calmly, that the people in the footage were of Gujarati background and eating rice and curry.

The Indian diaspora in Britain does not need to prove its legitimacy. It does, increasingly, need to be prepared for a world in which legitimacy is beside the point."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
