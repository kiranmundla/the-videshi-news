#!/usr/bin/env python3
"""Immigration writer — 2026-06-08 00:58 PDT run."""

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


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ── Article 1: Dallas Housing ──────────────────────────────────────────────────

art1_body = """North of Dallas, in the booming suburbs of Collin County, builders once designed model homes with north-facing *puja* rooms for Hindu prayer and optional spice kitchens. South Asian buyers represented seventy per cent of sales for some developers. That was eighteen months ago. Today, home prices in Collin County have fallen nearly nine per cent year-over-year — more than double the four per cent decline across the broader Dallas–Fort Worth metro — and the clientele that once drove the market has largely vanished.

The retreat is not accidental. It is the downstream consequence of Washington's most aggressive assault on the H-1B programme in decades, and its ripple effects are rewriting the economics of housing in one of America's fastest-growing corridors.

## Thirty-Two Thousand Visas, One Metro

During the Biden administration, the Dallas area received nearly 32,000 new H-1B approvals — more than Silicon Valley, Seattle, San Francisco, or Washington, according to a Bloomberg investigation published this week citing USCIS data. Only the New York City metro ranked higher. The workers who arrived on those visas poured into new subdivisions in Prosper, Frisco, and Celina, where the population tripled in five years.

Collin County's Indian-born population surged to an annual average of 116,000 residents by 2024, up from 70,000 in the preceding five-year period. In Frisco alone — a city of 235,000 roughly thirty miles north of downtown Dallas — the Indian share of the population ballooned from six per cent in the early 2010s to nearly twenty per cent.

Then the policy environment shifted.

## A Wall of New Restrictions

Trump raised minimum salary thresholds, imposed a wage-weighted lottery, and directed the Labour Department to launch Project Firewall, an enforcement initiative targeting alleged employer abuse. In September 2025, the administration imposed a $100,000 fee on new H-1B petitions — a measure that effectively priced out the staffing firms and mid-tier tech contractors that were the biggest sponsors of Indian workers in Dallas.

The Department of Housing and Urban Development separately barred non-permanent residents, including H-1B holders, from accessing FHA-insured mortgages. The share of FHA loan volume issued to non-permanent residents fell from six per cent in April to virtually zero by late summer, according to data from John Burns Research and Consulting.

At the state level, Governor Greg Abbott froze new H-1B petitions by state agencies and public universities. Attorney General Ken Paxton launched a probe into the programme, serving civil investigative demands to nearly thirty North Texas businesses suspected of fraud or abuse.

## Why This Matters to Indian Americans

For the Indian diaspora, the numbers are personal. Roughly three-quarters of all H-1B workers approved in fiscal year 2023 were born in India, according to Pew Research Centre. Dallas was not just a housing market — it was a community.

Zach Schneider, a builder at Tradition Homes, told Bloomberg that South Asian buyers have fallen from seventy per cent to below thirty per cent of his sales, even as he sits on 125 luxury homes under construction. Real estate agent Neeraj Gupta, who arrived in Dallas on an H-1B visa in 2000, said his phone — once ringing with buyers — now rings with sellers looking to cut their losses. Some clients are absorbing $300 to $1,500 monthly rental losses while waiting for a recovery that may not arrive.

One client, a senior IT director holding two Frisco homes each valued above $1 million, is weighing a return to India. Another financed an $800,000 home almost entirely with debt; the property is now underwater.

Immigration attorney Sharadha Kodem, practising in Frisco, described the anxiety as unlike anything in her career. Clients who bought in remote suburbs during the remote-work era are now being recalled to offices in Dallas — or told to relocate to Seattle or San Francisco. Those who are laid off have just sixty days to secure a new employer sponsor before their visa status lapses. Several need more time to sell but still face mortgage payments.

The pattern echoes moves elsewhere: Canada capped international students in 2024 to ease housing pressure, and Spain halted its golden visa programme. But in Dallas, housing analyst Alex Barron posed the uncomfortable question that no policy memo has answered: "Who is there to replace them?"

The answer, for now, is no one."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Nine Per Cent and Falling — The Dallas Suburbs Indian Workers Built Are Emptying Out",
    "subheadline": "Collin County home prices have dropped at double the metro rate as the H-1B crackdown, FHA mortgage ban, and tech layoffs drive Indian buyers out of North Texas.",
    "slug": make_slug("dallas-collin-county-housing-crash-indian-h1b-buyers"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Three-quarters of H-1B workers are Indian-born. Dallas's Indian community — 116,000 strong in Collin County — is watching home values collapse, facing 60-day visa clocks after layoffs, and weighing whether to return to India as the housing market they built unravels beneath them.",
    "tags": ["h1b", "dallas", "housing", "indian-americans", "visa-crackdown", "fha-mortgage"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "New York Post / Bloomberg", "url": "https://nypost.com/2026/06/05/real-estate/trumps-crackdown-on-h1b-visa-abuse-sends-dallas-home-prices-down/"},
        {"name": "USCIS Data via Bloomberg", "url": "https://www.uscis.gov/"},
        {"name": "Pew Research Center", "url": "https://www.pewresearch.org/"},
        {"name": "John Burns Research and Consulting", "url": "https://jbrec.com/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/17286412/pexels-photo-17286412.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "Aerial view of suburban subdivision homes in Texas",
    "image_attribution": "Pexels",
    "body": art1_body,
}

# ── Article 2: Federal Judge Strikes Down 39-Country USCIS Ban ─────────────────

art2_body = """A federal judge in Rhode Island has torn into the Trump administration's immigration machinery, ruling that USCIS adopted a series of unlawful policies that left people from thirty-nine countries in what he called "indeterminate legal limbo" — unable to receive decisions on asylum claims, work permits, green cards, or citizenship applications.

Chief U.S. District Judge John McConnell Jr., in a blistering opinion issued on Friday, found that USCIS "claims statutory and regulatory authority that it does not possess; makes decisions without the reasoned explanations that it must provide; acts without regard for the reliance interests of applicants that it must consider; and justifies its actions with pretextual concerns of 'national security' that mask anti-immigrant sentiments."

In legal terms, the judge wrote, "that means USCIS's actions are contrary to law and arbitrary and capricious."

## What Happened

The policies in question were enacted after the shooting of two National Guard members near the Farragut West metro station in Washington, D.C., last Thanksgiving. The administration used the attack — by an Afghan national — to impose sweeping restrictions on immigrants from dozens of African, Asian, Latin American, and Middle Eastern countries covered by full or partial travel bans.

The result: tens of thousands of pending cases at USCIS were effectively frozen. Naturalization ceremonies were cancelled. Work permit renewals went unanswered. Applicants who had followed every step of the legal process found themselves unable to work, travel, or plan.

The ruling orders the administration to resume processing and reschedule the cancelled ceremonies.

## India Is Not on the List — But the Precedent Matters

India does not appear among the thirty-nine travel-ban countries directly affected by the ruling. But for the hundreds of thousands of Indian nationals navigating America's immigration system — waiting in decade-long green card queues, tracking H-1B renewals, filing EAD applications — the decision carries weight far beyond its immediate scope.

The core of Judge McConnell's reasoning is that USCIS cannot unilaterally freeze lawful immigration pathways without Congressional authority. That principle applies equally to the agency's handling of Indian-dominated employment-based visa categories, where processing delays, memo-driven policy shifts, and discretionary holds have become routine.

"USCIS's hold on adjudications cannot be attributed to anything that these individuals did wrong; rather, it arises solely by the happenstance of their birth," McConnell wrote. For Indian professionals who have watched their green card queues stall for reasons that feel equally arbitrary — per-country caps, shifting USCIS memos, reclassification of adjustment-of-status norms — the language resonates.

## What the Ruling Means in Practice

The decision, brought by a coalition of immigrant service organisations and labour unions represented by Democracy Forward, is broad. It impacts all pending USCIS cases from the affected countries, not just those named in the lawsuit, according to the American Immigration Lawyers Association.

"This ruling reaffirms a basic principle: the federal government cannot shut down lawful immigration pathways or discriminate against people based on where they come from," said Skye Perryman, president of Democracy Forward.

The Department of Homeland Security has not commented. DHS General Counsel James Percival dismissed the ruling's logic as "sabotage dressed in legal clothing," calling the animus-based legal strategy a pattern used since 2017.

An appeal is likely. But the ruling establishes a clear judicial marker: there are limits to how far USCIS can stretch executive authority over immigration processing, even under the banner of national security. For Indian Americans watching the agency's handling of their own cases — the PM-602 memo, the new AOS interview questions, the PERM processing crisis — that marker matters."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "A Judge Just Called USCIS Lawless — and the Ruling Should Worry Every Indian Waiting in Line",
    "subheadline": "A federal court struck down USCIS policies freezing cases from 39 countries, finding the agency exceeded its authority. India isn't on the list, but the precedent reaches much further.",
    "slug": make_slug("federal-judge-uscis-39-country-ban-struck-down-india-precedent"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "While India isn't among the 39 travel-ban countries, the ruling's core principle — that USCIS cannot unilaterally freeze lawful immigration pathways — directly challenges the agency's handling of Indian employment-based visa processing, where memo-driven delays, AOS policy shifts, and PERM backlogs have become the norm.",
    "tags": ["uscis", "federal-court", "travel-ban", "immigration-law", "judicial-review", "green-card"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "AP via Audacy", "url": "https://www.audacy.com/kmbz/news/national/trump-immigration-asylum-citizenship-10591d120e5cb13da736d9eeb06757c8"},
        {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/"},
        {"name": "American Immigration Lawyers Association", "url": "https://www.aila.org/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/32442906/pexels-photo-32442906.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "Neoclassical federal courthouse with American flags in the foreground",
    "image_attribution": "Pexels",
    "body": art2_body,
}

# ── Article 3: $2.25 Billion IT Fee Impact ──────────────────────────────────────

art3_body = """The arithmetic is brutal. If the $100,000 H-1B fee had been in effect between May 2020 and May 2024, Infosys would owe $1.04 billion. Tata Consultancy Services would face $650 million. Cognizant: more than $560 million. The combined exposure across just three Indian IT outsourcing giants exceeds $2.25 billion — and the fee is now very much in effect.

A Bloomberg investigation, drawing on USCIS consular processing data, has quantified what the Indian IT services industry has long feared: the $100,000-per-petition fee imposed by presidential proclamation in September 2025 does not merely raise costs. It restructures the entire business model that sent hundreds of thousands of Indian engineers to American client sites over the past two decades.

## The Mechanics of a $100,000 Problem

The fee applies to new H-1B petitions for workers processed at U.S. consulates abroad — the standard channel for the outsourcing industry, which recruits engineers in India and stations them at American client offices. More than ninety per cent of new Infosys H-1B hires in the four-year period were approved through this channel. For TCS, the figure was eighty-two per cent; for Cognizant, eighty-nine.

These are not edge cases. Consular processing is the core of the IT services delivery model. The fee targets it precisely.

Indian IT industry body NASSCOM has pushed back, but the numbers speak for themselves. Even before formal legal challenges yielded results, Bloomberg reported that experts projected a thirty to fifty per cent drop in H-1B lottery applications and an acceleration of offshore hiring.

## The Strategic Pivot

The response is already visible. Major IT firms and their multinational clients are shifting work back to India at pace. Industry whispers — corroborated by hiring data from firms like Accenture — suggest a twenty per cent increase in offshoring to India by multinationals adjusting to the new cost structure. By one estimate, Trump's H-1B reforms could push 50,000 IT jobs back to Indian delivery centres by the end of 2026.

T-Mobile's recent announcement of a 1,000-person technology centre in Hyderabad is a case study in what this looks like in practice: the work gets done, the talent stays in India, and no H-1B visa is required.

For the Indian IT services sector, this is not entirely bad news. Bangalore, Hyderabad, Pune, and Chennai stand to absorb a significant volume of high-value technology work. But for the hundreds of thousands of Indian professionals already in the United States — the ones who moved their families, bought homes, enrolled their children in American schools — the pivot leaves them stranded between a shrinking visa pipeline and an employer base with less incentive to sponsor them.

## Why This Matters to Indian Americans

The $100,000 fee has redrawn the calculus of every H-1B-dependent career path. Employers that once filed dozens of petitions annually are now selective to the point of paralysis. Mid-tier consulting firms and staffing agencies — the on-ramp for many Indian professionals — are pulling back entirely. The workers already on H-1B visas are not directly hit by the fee, but they operate in an ecosystem where renewal, transfer, and green card sponsorship all depend on employer willingness to invest in a programme that Washington has made conspicuously expensive.

Former Infosys CFO Mohandas Pai has been blunt: the fee will accelerate offshoring and reduce the flow of Indian talent to the United States. For the diaspora, the implication is a two-speed system — one for workers already established in America, fighting to stay, and another for the next generation, increasingly likely to build their careers from Bangalore or Hyderabad rather than Frisco or Redmond.

The $2.25 billion figure is not a hypothetical. It is the price tag that Indian IT's American ambition now carries — and the industry is deciding, in real time, whether to pay it or walk away."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Two and a Quarter Billion Dollars — The H-1B Tab That Could End Indian IT's American Era",
    "subheadline": "Infosys, TCS, and Cognizant face a combined $2.25 billion in H-1B fees under Trump's $100,000-per-petition rule. The industry's response — offshoring fifty thousand jobs back to India — is already underway.",
    "slug": make_slug("225-billion-h1b-fee-indian-it-infosys-tcs-cognizant-offshoring"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The $100,000 fee restructures the outsourcing model that brought hundreds of thousands of Indian engineers to America. Those already on H-1B visas face a tighter employer ecosystem; the next generation may build careers from Bangalore instead of Redmond.",
    "tags": ["h1b", "infosys", "tcs", "cognizant", "100k-fee", "offshoring", "indian-it"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Bloomberg / Trak.in", "url": "https://trak.in/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
        {"name": "Bloomberg Tax", "url": "https://news.bloombergtax.com/"},
        {"name": "Whispers in the Corridors", "url": "https://www.whispersinthecorridors.com/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7581127/pexels-photo-7581127.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "Technology professionals collaborating in a modern office environment",
    "image_attribution": "Pexels",
    "body": art3_body,
}

# ── Insert ──────────────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
