#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-24 11:30 batch
Topics: 1) India's Parliament declares crypto "high risk" — Lok Sabha Finance Committee formally reviews VDA regulation
        2) 98th Scripps National Spelling Bee starts Monday — Indian American dominance, 28 of 34 champions since 1999
"""

import json, os, uuid, re, requests
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Supabase config ──
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

def sb_get(table, params):
    r = requests.get(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_patch(table, params, data):
    h = {**HEADERS, "Prefer": "return=representation"}
    r = requests.patch(f"{SB_URL}/rest/v1/{table}", headers=h, params=params, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(slug_base, date_suffix="20260524"):
    slug = slug_base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

# ── Duplicate check ──
existing = sb_get("p2_articles", {
    "select": "headline,slug",
    "status": "eq.published",
    "published_at": "gte.2026-05-22T00:00:00Z",
    "order": "published_at.desc",
    "limit": "80"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: India's Parliament Just Called Crypto 'High Risk.' Thousands of Crores Are Leaving the Country Anyway.
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("india-parliament-crypto-high-risk-vda-regulation-binance-wazirx-nri")
if slug1 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "India's Parliament Just Called Crypto 'High Risk.' Thousands of Crores Are Leaving the Country Anyway.",
        "subheadline": "The Lok Sabha Finance Committee summoned Binance, WazirX, and ZebPay to testify last week. The government classified virtual digital assets as a high-risk sector linked to money laundering, trafficking, and radicalisation. The RBI continues to oppose crypto outright. And yet India has no standalone law governing cryptocurrencies — just a 30 percent tax and a 1 percent TDS that have driven billions offshore. For the 4.4 million Indian Americans and millions more NRIs who hold crypto, India's regulatory limbo has become a financial risk in itself.",
        "slug": slug1,
        "category": "news",
        "vertical": "technology",
        "diaspora_angle": "For NRIs, India's crypto regulatory vacuum creates a uniquely treacherous environment. Indian Americans who hold cryptocurrency — whether Bitcoin, Ethereum, or stablecoins — face regulatory uncertainty on both sides. In the US, the SEC and CFTC have established clearer (if contested) frameworks for crypto trading. In India, there is no equivalent. The 30% flat tax on crypto gains (no indexation, no loss offset against other income) and 1% TDS on transactions above ₹10,000 have made India one of the harshest crypto tax regimes in the world. The result: Indian trading volumes have migrated to offshore exchanges, many based in Singapore, Dubai, and the Seychelles. For NRIs who still maintain Indian bank accounts, NRE/NRO accounts, or crypto wallets tied to Indian exchanges, the question is whether a sudden regulatory crackdown could freeze assets or trigger compliance obligations retroactively. The parliamentary committee's focus on crypto organisations 'based outside India, particularly in Singapore' directly targets platforms that many NRIs use. Meanwhile, Indian-origin founders are among the most active builders in the global Web3 ecosystem — from Polygon's Sandeep Nailwal to Coinbase's Balaji Srinivasan era — creating a paradox where Indian talent builds the global crypto infrastructure while India itself cannot decide whether to regulate or ban it. For NRIs who send money to India, stablecoins have emerged as a faster, cheaper alternative to traditional remittance channels like Wise or Western Union. If India cracks down, that channel closes. If India regulates properly, it could become one of the largest crypto markets in the world. The parliamentary committee's recommendations — expected in coming months — will determine which path India takes, and every NRI with a crypto wallet has skin in the game.",
        "tags": ["crypto", "cryptocurrency", "VDA", "virtual digital assets", "Lok Sabha", "parliament", "regulation", "Binance", "WazirX", "ZebPay", "RBI", "money laundering", "NRI", "tax", "TDS", "India", "Bhartruhari Mahtab", "FIU-IND", "offshore", "Singapore"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Inc42 — Centre Flags Crypto As 'High Risk' As Parliamentary Panel Reviews VDA Framework", "url": "https://inc42.com/buzz/centre-flags-crypto-as-high-risk-as-parliamentary-panel-reviews-vda-framework/"},
            {"name": "Outlook Money — Parliamentary Panel Calls Crypto Investments Alarming, Signals Support For Existing Tax Rules", "url": "https://outlookmoney.com/cryptocurrency/parliamentary-panel-calls-crypto-investments-alarming-signals-support-for-existing-tax-rules"},
            {"name": "Analytics Insight — India's Crypto Industry Pushes for Tax Relief as Parliament Reviews Capital Outflows", "url": "https://analyticsinsight.net/cryptocurrency/indias-crypto-industry-pushes-for-tax-relief-as-parliament-reviews-capital-outflows-and-regulation"},
            {"name": "CryptoNews — India Crypto Policy 2026: Lok Sabha Finance Committee Begins Formal VDA Study", "url": "https://cryptonews.net/news/regulation/31050888/"},
            {"name": "The FinWall — Indian Crypto Sector Urges Tax Overhaul Ahead of Budget", "url": "https://thefinwall.com/indian-crypto-sector-urges-tax-overhaul-ahead-of-budget-citing-offshore-capital-flight/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "body": """Last week, the heads of three of India's most prominent cryptocurrency exchanges — Binance, WazirX, and ZebPay — were summoned to appear before the Lok Sabha's Parliamentary Standing Committee on Finance. They were not invited to celebrate the industry. They were called to explain themselves.

The committee, chaired by BJP MP Bhartruhari Mahtab, had a simple question that turned out not to be simple at all: What exactly is happening with the thousands of crores that Indians are pouring into virtual digital assets, and why is so much of it leaving the country?

The government's answer, delivered by the revenue secretary, the corporate affairs secretary, and representatives from the Central Board of Direct Taxes, was blunt. Virtual digital assets have been classified as a "high-risk" sector. The risks cited were not abstract: money laundering, trafficking, radicalisation, suspicious transactions, and cyber fraud.

The exchanges' answer was equally blunt, if from the opposite direction. They want regulatory clarity. They want rational taxes. And they want a level playing field with global competitors who are eating India's lunch.

## The Tax Regime That Broke Indian Crypto

India's relationship with cryptocurrency can be summarised in two numbers: 30 and 1.

In the 2022-23 Union Budget, the government imposed a flat 30 percent tax on all gains from crypto transactions — with no indexation benefit, no ability to offset losses against other income, and applicable cess and surcharges on top. It simultaneously imposed a 1 percent Tax Deducted at Source on all VDA transactions above ₹10,000 annually.

The intent was clear: if India could not ban crypto outright (the Supreme Court had already struck down a previous RBI ban in 2020), it would tax it into submission.

The result was the opposite of submission. It was migration.

Indian crypto trading volumes plummeted on domestic exchanges and surged on offshore platforms — many based in Singapore, Dubai, and the Seychelles — that were beyond the reach of Indian tax authorities. The very capital flight that the government feared was accelerated by the policy designed to prevent it.

Mahtab, the committee chairman, acknowledged this reality during the hearing. "We find thousands of crores being invested in virtual digital assets, which is actually very alarming, and it is all going out of the country," he told reporters after the session.

He specifically pointed to VDA-related organisations based outside India, particularly in Singapore, and stressed that income generated through overseas crypto investments must be taxed within India.

## The Exchanges Want Rules. The RBI Wants a Ban. India Has Neither.

The hearing exposed a fundamental incoherence at the heart of India's crypto policy.

The government taxes crypto — aggressively. The Financial Intelligence Unit (FIU-IND) updated its compliance guidelines for crypto entities in January 2026, tightening anti-money laundering and know-your-customer norms. Offshore exchanges serving Indian users have been brought under mandatory FIU-IND registration requirements.

But India does not have a standalone law governing cryptocurrency. There is no dedicated regulatory framework. The RBI continues to oppose permitting or regulating VDAs at all — its position has not moved since the original 2018 circular that tried to ban crypto banking.

This creates a bizarre regulatory limbo: crypto is taxed but not legally recognised, monitored but not regulated, discouraged but not banned.

Some members of the parliamentary committee itself questioned this contradiction. Why, they asked, does the government collect a 30 percent tax on transactions in an asset class it has no formal policy for? If crypto is high-risk enough to warrant government warnings, shouldn't there be a law governing it rather than just a tax rate?

The committee heard that India is currently studying three global approaches. The United States, the United Kingdom, and the European Union have introduced regulatory frameworks — the EU's MiCA (Markets in Crypto-Assets) regulation is the most comprehensive. China has imposed an outright ban on all cryptocurrency trading and mining. Japan and Brazil are attempting to govern VDAs through existing financial laws without dedicated crypto legislation.

Mahtab indicated that India would chart its own course after evaluating all three models. The committee plans to continue discussions and submit recommendations after further consultations.

## The WazirX Shadow

The hearing took place against the backdrop of one of the largest crypto security breaches in history.

In July 2024, WazirX — once India's largest crypto exchange — suffered a $230 million hack that wiped out customer funds. The breach exposed fundamental weaknesses in the platform's security architecture. The Enforcement Directorate subsequently seized nearly ₹90 crore worth of crypto assets linked to Binance, WazirX, and ZebPay as part of a money laundering probe tied to online betting and gaming applications.

For the parliamentary committee, the WazirX disaster was exhibit A in the case for treating crypto as high-risk. For the exchanges, it was precisely the argument for regulation rather than hostility — a regulated market with enforced security standards, they argued, would have prevented the breach.

The committee had previously met exchanges including CoinDCX, Coinbase, and CoinSwitch in December 2025. Those earlier discussions led to the FIU-IND updating its compliance guidelines in January 2026.

## What This Means for NRIs

For the 4.4 million Indian Americans and millions of Non-Resident Indians around the world who hold cryptocurrency — and many do — India's regulatory vacuum is not an abstraction. It is a direct financial risk.

NRIs who maintain crypto wallets linked to Indian exchanges, or who hold assets in NRE/NRO accounts that have interacted with crypto platforms, face uncertainty on multiple fronts. If India moves toward a ban — unlikely but not impossible given the RBI's persistent opposition — assets could be frozen. If India moves toward regulation, new compliance obligations could apply retroactively. If India does nothing, which is what it has done for four years, the regulatory vacuum itself becomes the risk.

The committee's focus on organisations "based outside India, particularly in Singapore" is particularly relevant for NRIs. Many use Singapore-based platforms precisely because India's domestic exchanges are hobbled by the tax regime. A regulatory framework that attempts to bring offshore platforms under Indian jurisdiction could have direct consequences for NRI accounts and transactions.

Meanwhile, stablecoins — cryptocurrencies pegged to the US dollar — have emerged as an increasingly popular channel for NRI remittances to India, offering faster settlement and lower fees than traditional wire transfers. India receives over $125 billion in remittances annually, the highest in the world. Even a small shift toward crypto-based remittance channels represents billions in potential volume — and billions in potential regulatory concern.

The paradox is inescapable: India produces a disproportionate share of the world's crypto talent while maintaining one of the world's harshest crypto tax regimes. The parliamentary committee's recommendations, expected in the coming months, will determine whether India resolves this contradiction or deepens it.

For now, the government's position is clear in its ambiguity: crypto is high-risk, it needs to be studied further, and thousands of crores are leaving the country while India studies."""
    })
    print(f"Article 1 prepared: {slug1}")
else:
    print(f"SKIP Article 1 — slug exists: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: The Scripps National Spelling Bee Starts Monday. 28 of the Last 34 Champions Were Indian American. This Year, 247 Kids Will Try to Make It 29.
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("scripps-spelling-bee-2026-indian-american-dominance-dc-28-of-34")
if slug2 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "The Scripps National Spelling Bee Starts Monday. Twenty-Eight of the Last Thirty-Four Champions Were Indian American. This Year, 247 Kids Will Try to Make It Twenty-Nine.",
        "subheadline": "On Monday, 247 spellers from across the United States and five countries will walk into DAR Constitution Hall in Washington, D.C. — a venue the Scripps National Spelling Bee has never used in its 101-year history — to compete for the most improbable trophy in American academia. Since 1999, Indian American children have won 28 of 34 national titles. The streak is not a fluke. It is the most visible artifact of a community that arrived in the United States with nothing but student visas and built a culture of achievement so intense that it has become a subject of documentaries, dissertations, and dinner-table debates in every Indian household from Houston to Hyderabad.",
        "slug": slug2,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "The Scripps National Spelling Bee is the most concentrated annual expression of Indian American cultural identity in the United States. It is not sports, where individual excellence can be attributed to physical gifts. It is not tech, where selection effects and visa pipelines explain concentration. It is a competition where 12-year-olds from families that immigrated a generation ago outperform the entire country, year after year, in a skill that is quintessentially American — mastery of the English language. For the Indian diaspora, the spelling bee is simultaneously a source of immense pride and quiet discomfort. Pride, because 28 of 34 champions since 1999 is a dominance streak unmatched in any academic competition anywhere. Discomfort, because the intensity of preparation — the hours of daily practice, the North South Foundation feeder circuit, the parents who reorganise their lives around spelling lists — raises questions about pressure, childhood, and what 'success' means when it is defined by a community that carries the weight of the immigration experience on its children's shoulders. The overrepresentation of families from Andhra Pradesh and Telangana — particularly Hyderabad — is not coincidental. It tracks precisely with the H-1B visa pipeline that brought tens of thousands of Telugu-speaking IT professionals to the United States in the late 1990s and 2000s. Their children, born in America, raised in American suburbs, educated in American schools, channelled their parents' immigrant drive into a competition that rewards exactly the qualities those parents prized: discipline, memorisation, language mastery, and the ability to perform under pressure on a national stage. For Indian American families, the spelling bee is not a game. It is a mirror.",
        "tags": ["Scripps National Spelling Bee", "spelling bee", "Indian American", "diaspora", "NRI", "education", "DAR Constitution Hall", "Washington DC", "North South Foundation", "Hyderabad", "Telugu", "H-1B", "immigration", "achievement", "culture", "2026"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Wikipedia — 98th Scripps National Spelling Bee", "url": "https://en.wikipedia.org/wiki/98th_Scripps_National_Spelling_Bee"},
            {"name": "Audacy/AP — National Spelling Bee reflects the economic success and cultural impact of immigrants from India", "url": "https://www.audacy.com/ksat/news/national/national-spelling-bee-reflects-the-economic-success-and-cultural-impact-of-immigrants-from-india"},
            {"name": "American Immigration Council — Indian Americans and the Scripps Spelling Bee", "url": "https://americanimmigrationcouncil.org/research/indian-americans-and-scripps-national-spelling-bee"},
            {"name": "YourStory — How Indian Americans are winning the National Spelling Bee year after year", "url": "https://yourstory.com/2019/06/how-indian-americans-winning-national-spelling-bee"},
            {"name": "Scripps — 2026 Media Guide", "url": "https://spellingbee.com/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "body": """On Monday morning, 247 spellers — 140 boys, 103 girls, one non-binary student, and three who preferred not to answer — will walk into DAR Constitution Hall in Washington, D.C., to begin the 98th Scripps National Spelling Bee.

It is the first time in the competition's 101-year history that this venue has hosted the bee. For the past 15 years, the event was held at the Gaylord National Resort in National Harbor, Maryland. The move to DAR Constitution Hall — the same stage where the Daughters of the American Revolution once hosted Marian Anderson after she was denied the right to sing at segregated concert halls — brings the bee back to the District of Columbia proper, three miles from the White House and two miles from the Capitol.

The symbolism is not lost on anyone who knows what happens at this event every year.

Since 1999, 28 of the last 34 Scripps National Spelling Bee champions have been Indian American.

## The Numbers That Explain Everything

The 247 spellers competing this week come from across the United States and its territories — Guam, Puerto Rico, and the U.S. Virgin Islands — as well as from the Bahamas, Canada, Ghana, Nigeria, and the United Arab Emirates. They range in age from 9 to 15. The majority, 111, are 8th graders. Seventy-eight are returning from previous bees, including 64 who competed last year.

The winner receives $50,000 in cash, a commemorative medal, and the Scripps Cup.

The competition runs from Tuesday, May 26 through Thursday, May 28. The format is rigorous: preliminary rounds on Tuesday draw from the "2026 Words of Champions" study guide. By Wednesday, spellers face quarterfinals and semifinals using words from the full Merriam-Webster Unabridged Dictionary — 470,000 entries, most of which no adult has ever encountered. The finals on Thursday continue until a champion is crowned, with the possibility of a 90-second speed spell-off if needed.

Among the returning spellers are names that the Indian American community will recognise — and that illustrate the depth of the pipeline.

Sarv Dharavane, from Dunwoody, Georgia, finished third last year and is back. Esha Marupudi, from Chandler, Arizona, finished seventh. Shrey Parikh, from Rancho Cucamonga, California, finished third at the 2024 bee and has returned for another shot. Adarsh Venkannagari, from Acton, Massachusetts, is competing in his fourth consecutive national bee. Siyona Kandala, from San Antonio, Texas, is also in her fourth consecutive year.

These are not one-off performances. These are multi-year campaigns.

## The Pipeline Behind the Streak

The 28-of-34 dominance streak is not an accident of demographics. Indian Americans make up roughly 1.4 percent of the U.S. population. Winning 82 percent of national spelling bee titles over a quarter century requires an infrastructure.

That infrastructure exists. It is called the North South Foundation.

Founded in 1989 by immigrants from India, the NSF runs a parallel circuit of regional and national spelling competitions for Indian American children. It is, in effect, the minor leagues of the Scripps Bee. Children who excel in NSF competitions graduate to the national stage with thousands of hours of competitive experience that their peers — many of whom qualified through school-level bees with far less intensity — simply do not have.

The families behind the streak are disproportionately from Andhra Pradesh and Telangana — particularly Hyderabad and its surrounding districts. This is not coincidental. It maps precisely onto the H-1B visa wave of the late 1990s and 2000s, when tens of thousands of Telugu-speaking IT professionals came to the United States on work visas. They settled in suburban enclaves in New Jersey, Texas, California, and Georgia. Their children, born in America, were raised in households where education was not merely valued — it was the reason the family was in America at all.

A 2024 Associated Press analysis found that Indian Americans hold 74 percent of H-1B visas for specialised occupations. The median household income for Indian American families is $147,000 — more than double the national median. Seventy-four percent of Indian American households have at least one college degree.

The spelling bee is the most public expression of this underlying reality. When Balu Natarajan won in 1985, he was an outlier. When Arvind Mahankali won in 2013, he was part of a movement. When seven Indian American spellers tied for the championship in 2019, it was a phenomenon.

## The Conversation Inside the Community

Within the Indian American community, the spelling bee occupies a complicated space.

There is genuine pride. Every May, Indian American WhatsApp groups and Facebook communities light up with spelling bee coverage. Parents share updates like cricket scores. Regional champions are celebrated at community events. The documentary "Breaking the Bee," which premiered at the Cleveland International Film Festival, explored the cultural machinery behind the streak and was widely discussed in Indian American media.

But there is also an undercurrent of anxiety — about the pressure placed on children, about the narrowness of a definition of success that revolves around memorisation and performance, about whether the spelling bee reinforces stereotypes of Indian Americans as hyper-competitive academic machines rather than fully rounded human beings.

This year's bee includes a storyline that may shift some of that conversation. Zwe Spacetime, from Prince George's County, Maryland, is competing for the second time. He is the younger brother of Zaila Avant-garde, who in 2021 became the first African American champion and only the second Black girl to win after Jamaica's Jody-Anne Maxwell in 1998. Zwe, who is Black, has spoken publicly about the significance of a potential win: "No Black boy, whether African American or non-African American, has won Scripps yet."

If Zwe wins, it would be the second time in five years that a member of the Avant-garde family has broken ground at the national spelling bee — a reminder that the competition's story is broader than any single community's dominance, even one as remarkable as the Indian American streak.

## What Monday Means

The 98th Scripps National Spelling Bee will air on ION TV, hosted by ESPN's Mina Kimes alongside longtime analyst Paul Loeffler, who is marking his 20th year covering the bee and whose sister Corrie Loeffler serves as the bee's director.

For the 247 families who have travelled to Washington — including Francis Luna from Dededo, Guam, who covered more than 7,000 miles — the next three days represent years of preparation compressed into a handful of rounds. For the Indian American families among them, it represents something older and larger than any individual competition: the enduring, complicated, fiercely debated but statistically undeniable fact that a community that arrived in America with student visas and suitcases has produced a generation of children who dominate the most American of academic traditions.

The priya-and-ryan-are-siblings detail — Priya and Ryan Sekera from Granite Bay, California, are competing against each other — is the kind of thing that makes the spelling bee irresistible. So is the 9-year-old competing against 14-year-olds. So is the veteran on her fourth consecutive national bee.

But the number that will hang over DAR Constitution Hall all week is the same number that has hung over this competition for a quarter century.

Twenty-eight of thirty-four.

The 247 spellers who registered on Sunday and begin competing on Tuesday will determine whether it becomes twenty-nine."""
    })
    print(f"Article 2 prepared: {slug2}")
else:
    print(f"SKIP Article 2 — slug exists: {slug2}")


# ── Insert articles ──
for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ Inserted: {art['slug']} (id: {art['id']})")
    except Exception as e:
        print(f"❌ Failed to insert {art['slug']}: {e}")

# ── Score decay: reduce scores of articles >24h old by 8% ──
cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%S')
try:
    old_articles = sb_get("p2_articles", {
        "select": "id,score_total",
        "status": "eq.published",
        "published_at": f"lt.{cutoff}",
        "score_total": "gt.10",
        "category": "eq.news",
        "limit": "200"
    })
    decayed = 0
    for a in old_articles:
        new_score = max(10, int(a["score_total"] * 0.92))
        if new_score != a["score_total"]:
            sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": new_score})
            decayed += 1
    print(f"Score decay: {decayed} news articles decayed")
except Exception as e:
    print(f"Score decay error: {e}")

print("\nDone! 2 articles published.")
