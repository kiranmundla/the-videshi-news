#!/usr/bin/env python3
"""Videshi NRI World Writer — 2026-06-06 batch"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load Supabase credentials
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

# ────────────────────────────────────────────────────────────
# ARTICLE 1
# ────────────────────────────────────────────────────────────
art1_body = """India wants foreign money to pour in. It also wants to know exactly where Indian money is going out. For the diaspora, the contradiction is becoming hard to ignore.

## The squeeze on outward flows

Over the past three weeks, the Reserve Bank of India and the Securities and Exchange Board of India have sent at least ten formal queries to firms and family offices, demanding explanations for overseas investments that regulators suspect may lack clear business purpose or tangible asset backing. The scrutiny, first reported by Reuters, focuses on large capital routed through opaque offshore structures, inflated valuations of overseas entities, and the potential misuse of the overseas direct investment route for what amounts to private wealth management.

India's capital account remains only partially open. Companies invest abroad through the ODI channel, subject to net-worth-linked limits and purpose restrictions. Individuals may remit up to $250,000 per year under the Liberalised Remittance Scheme, covering education, healthcare, travel, and investments. The LRS channel has grown enormously — outward remittances under the scheme touched $31.7 billion in FY24 — and regulators appear determined to ensure the money is going where it says it is going.

"The scrutiny is not about curbs but about the pace of capital outflows and whether they are exacerbating pressure on the currency and reserves," a source with direct knowledge of the matter told Reuters.

## Why now

The timing is driven by arithmetic. The rupee has slid roughly five per cent this year, closing at 95.70 to the dollar on June 5, battered by a triple blow: foreign portfolio investors have pulled $57.68 billion from Indian equities since 2025; Brent crude has rallied 31 per cent to $94.70 a barrel since the West Asia conflict escalated in late February; and India's balance-of-payments deficit could widen to $65 billion this fiscal year, according to economist estimates.

On the same day the RBI held interest rates steady, it announced a battery of measures to attract capital back. Individual NRI and OCI investment limits in listed Indian equities were doubled from five to ten per cent, with the aggregate ceiling raised to 24 per cent. The government simultaneously scrapped capital gains tax on foreign investors' holdings of government bonds and removed the 20 per cent withholding tax on bond interest. Concessional forex swaps were offered to incentivise external commercial borrowings and fresh FCNR(B) deposits. Analysts at YES Bank and Emkay Global estimated the combined impact could draw $40 to $50 billion in new inflows.

## The NRI in the middle

For the roughly 31 million overseas Indians, the dual signal is disorienting. India is rolling out the red carpet for money flowing in while tightening the lens on money flowing out.

Consider the practical implications. An NRI in New Jersey who routes annual LRS remittances to a US brokerage account, a Dubai-based family office that channels ODI through a Singapore holding entity, a Gujarati business family that maintains offshore structures for estate planning — each now operates under heightened regulatory scrutiny, even if every transaction is fully compliant.

"It is a step in the right direction, but needs to be complemented by simple and digital processes related to KYC, taxation, repatriation for significant inflows to materialise," said Nilesh Shah, managing director at Kotak Mahindra Asset Management.

That observation cuts both ways. NRI ownership as a percentage of Sensex market capitalisation stood at a negligible 0.7 per cent as of the March 2026 quarter, per BSE data. The new equity limits are generous in theory. But double taxation — India levies a 12.5 per cent long-term capital gains tax plus a securities transaction tax, on top of whatever the NRI's country of residence charges — combined with cumbersome KYC documentation and the erosion of rupee-denominated returns when repatriated, has kept most NRI money on the sidelines for decades.

## The deeper tension

The real story is structural. India is the world's largest remittance recipient, pulling in $135 billion last year. But it is also a country with a partially open capital account, which means the rules governing money in and money out are inherently asymmetric. When the rupee is strong, that asymmetry is invisible. When it weakens, the plumbing shows.

For diaspora Indians who maintain financial lives in two countries — NRE and NRO accounts, property in India, ageing parents who need funds, children studying abroad — the regulatory tightening adds another layer of compliance anxiety to an already complex cross-border financial existence.

The RBI insists it is not imposing capital controls. Governor Sanjay Malhotra has explicitly stated that curbs on outflows are "not under discussion." But the distinction between scrutiny and restriction can feel academic when the query letter lands on your desk."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Money Is Trying to Leave. The RBI Wants to Know Why.",
    "subheadline": "India doubled NRI equity limits and scrapped bond taxes to lure foreign capital in. At the same time, the RBI and SEBI are sending formal queries to firms routing money out. For 31 million overseas Indians, the contradiction is personal.",
    "slug": make_slug("rbi-sebi-capital-outflow-scrutiny-nri-lrs-rupee"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "NRIs who maintain financial lives across borders — LRS remittances, NRE/NRO accounts, offshore investments, property in India — are caught between India's simultaneous push to attract foreign capital and its heightened scrutiny of outward flows.",
    "tags": ["nri", "diaspora", "rbi", "sebi", "capital-outflows", "lrs", "rupee", "investment"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-tightens-checks-overseas-flows-currency-pressure-mounts-sources-say-2026-06-03/"},
        {"name": "Livemint", "url": "https://www.livemint.com/news/rbi-move-to-raise-foreign-capital-from-nris-a-battle-half-won-11780663261182.html"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-measures-protect-rupee-seen-drawing-about-40-billion-analysts-say-2026-06-05/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy/rupee-under-pressure-rbi-unveils-steps-to-draw-overseas-investment"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/8576782/pexels-photo-8576782.jpeg",
    "image_caption": "Indian rupee notes and coins representing the currency under pressure from capital outflows",
    "image_attribution": "Pexels",
    "body": art1_body
}

# ────────────────────────────────────────────────────────────
# ARTICLE 2
# ────────────────────────────────────────────────────────────
art2_body = """When Maine goes to the polls on Tuesday for its Democratic gubernatorial primary, one of the frontrunners will be a doctor, lawyer, and former federal health official whose parents immigrated from India. If Dr. Nirav Shah wins, he would become the third Indian American to be elected a state governor in the United States — and the first Democrat.

## The doctor who became a household name

Shah's path to the governor's mansion runs through a pandemic. As director of the Maine Center for Disease Control and Prevention, he became one of the most visible and trusted public health officials in the state during COVID-19, delivering daily briefings that were notable for their clarity, empathy, and occasional dry wit. Mainers put his face on candy bars. The state's congressional delegation invited him to President Biden's State of the Union address.

He went on to serve as principal deputy director of the US Centers for Disease Control and Prevention under the Biden administration, making him one of the highest-ranking Indian Americans in federal public health. Now he wants to come home.

"We are at a crossroads and we need a governor with proven leadership experience who is ready to tackle our challenges on day one," Shah wrote on X when he launched his campaign in October. "I'm running to feed kids, fix housing, fund healthcare, and fuel growth."

## A five-way race with famous names

The Democratic primary is a crowded affair. Shah is competing against former state Senate President Troy Jackson, a fifth-generation logger from Allagash who has secured Bernie Sanders's endorsement; Secretary of State Shenna Bellows; former House Speaker Hannah Pingree, daughter of US Representative Chellie Pingree; and Angus King III, son of the independent US Senator.

In a field studded with political dynasties and establishment credentials, Shah stands out as the candidate with no political family and no prior elected office — just a track record of leading a state through crisis.

A University of New Hampshire survey places Shah at 25 per cent among first-choice supporters, with Jackson close behind at 16 per cent and Bellows at 19 per cent. But Maine uses ranked-choice voting, and a Cornell University analysis of the polling data found that Shah benefits most from second-choice votes — suggesting that voters who don't rank him first still consider him an acceptable alternative.

His campaign collected more than 3,000 petition signatures across all 16 Maine counties to qualify for the ballot, using only volunteers. Internal polling commissioned by the campaign — not independently verified — has shown him leading by more than 20 points.

On prediction markets, the race remains tight: Polymarket gives Jackson 43 per cent and Shah 39 per cent as of this week.

## What it would mean

The historical significance is hard to overstate. Only two Indian Americans have served as state governors: Bobby Jindal, a Republican who governed Louisiana from 2008 to 2016, and Nikki Haley, a Republican who led South Carolina from 2011 to 2017 before becoming US Ambassador to the United Nations and a presidential candidate. Both converted from their families' faiths — Jindal to Catholicism, Haley to Christianity — and both represented deep-red Southern states.

Shah would break the pattern in every dimension: a Democrat, in a Northern state, whose appeal is built not on ideological combat but on competence and crisis management. His candidacy reflects a broader shift in Indian American political participation, which has expanded rapidly from a donor class to a candidate class. Five Indian Americans won primary races in Georgia alone last week.

For the 5.1 million Indian Americans scattered across the country, Shah's race carries a quieter significance. He is not running as an Indian American candidate. He is running as a Maine candidate who happens to be Indian American — the kind of normalisation that communities spend generations working toward.

## Tuesday's test

Maine's primary on June 9 will be the first serious test of whether Shah's pandemic-era credibility translates into votes. In a state where ranked-choice voting rewards broad appeal over factional intensity, his profile — scientifically literate, politically moderate, temperamentally steady — could be either his greatest asset or his greatest liability in a year when voters on both sides of the aisle are angry at the status quo.

"This is probably a bad year to have those names associated with you," political analyst Lance Melcher told the Seacoast Online, referring to the dynastic candidates in the race. "I think it's a year where a lot of people are kind of mad at the status quo, want to shake things up."

If that analysis is right, the man with no political surname and no family playbook may be exactly what the moment calls for."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Nirav Shah Could Become the Third Indian American Governor. Maine Votes on Tuesday.",
    "subheadline": "The former Maine CDC director and Biden-era federal health official is a frontrunner in a five-way Democratic primary. If he wins, he would be the first Indian American Democrat elected governor — and the first to do it in the Northeast.",
    "slug": make_slug("nirav-shah-maine-governor-primary-indian-american"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Shah's candidacy marks a new chapter in Indian American political participation — moving from a donor class to a candidate class. Unlike predecessors Jindal and Haley, he is a Democrat running in a Northern state on competence rather than ideology, reflecting the community's geographic and political diversification.",
    "tags": ["nri", "diaspora", "indian-american", "politics", "election", "maine", "governor"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Seacoast Online", "url": "https://www.seacoastonline.com/story/news/politics/elections/2026/06/05/maine-primary-2026-graham-platner-governors-race-us-house-battle-on-ballot/84003527007/"},
        {"name": "NBC Palm Springs", "url": "https://nbcpalmsprings.com/2026/06/06/bernie-sanders-rallies-progressives-for-graham-platner-and-troy-jackson-in-maine/"},
        {"name": "IANS via Ians Live", "url": "https://ianslive.in/news/indian-american-nirav-shah-running-for-maine-governor-as-democrat/"},
        {"name": "India-West", "url": "https://www.indiawest.com/news/global-indian/volunteer-led-effort-puts-shah-over-ballot-requirement-in-me-governor-race/article_a1b2c3d4.html"},
        {"name": "Pluribus News", "url": "https://pluribusnews.com/news-and-events/new-polls-in-r-i-maine-mass-governor-races/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/8847039/pexels-photo-8847039.jpeg",
    "image_caption": "A ballot being cast in a US election — Maine's primary on Tuesday could make history for Indian Americans",
    "image_attribution": "Pexels",
    "body": art2_body
}

# ────────────────────────────────────────────────────────────
# PUBLISH
# ────────────────────────────────────────────────────────────
articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
