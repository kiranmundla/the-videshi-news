#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS + TECH articles for 2026-05-22 (night batch)
Topics: Pulwama mastermind killed in PoK, OpenAI+SpaceX IPO Supercycle
"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
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

def sb_patch(table, filters, data):
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{filters}", headers={**HEADERS, "Prefer": "return=minimal"}, json=data, timeout=30)
    return r.status_code

def make_slug(headline, date_suffix="20260522"):
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Pulwama Attack Mastermind Killed in PoK
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "The Mastermind of the Pulwama Attack Has Been Gunned Down in Pakistan-Occupied Kashmir. India Has Waited Seven Years for This.",
    "subheadline": "Arjumand Gulzar, alias Hamza Burhan — designated terrorist, Al-Badr commander, and the man Indian intelligence linked to the 2019 CRPF convoy bombing that killed 40 jawans — was shot dead by unidentified gunmen in Muzaffarabad on Thursday. He was living under ISI protection with eight commandos and a bulletproof car.",
    "slug": make_slug("pulwama-mastermind-hamza-burhan-killed-pok"),
    "category": "news",
    "vertical": "security",
    "diaspora_angle": "The Pulwama attack remains one of the most emotionally charged events in modern Indian history — one that diaspora communities rallied around in 2019 with candlelight vigils from New York to London. For NRIs who remember the Balakot airstrikes and the war scare that followed, Hamza Burhan's death closes a chapter but raises fresh questions about Pakistan's terror infrastructure.",
    "tags": ["Pulwama", "Hamza Burhan", "Arjumand Gulzar", "Al-Badr", "ISI", "CRPF", "PoK", "Muzaffarabad", "Balakot", "terrorism"],
    "urgency": "breaking",
    "sources": json.dumps([
        {"name": "Devdiscourse — Pulwama attack mastermind Burhan Hamza shot dead by unknown men in PoK", "url": "https://www.devdiscourse.com/article/politics/3917207-pulwama-attack-mastermind-burhan-hamza-shot-dead-by-unknown-men-in-pok"},
        {"name": "Livemint — Who was Arjumand Gulzar, alias Burhan Hamza, 2019 Pulwama attack mastermind shot dead in PoK?", "url": "https://www.livemint.com/news/who-was-arjumand-gulzar-alias-burhan-hamza-2019-pulwama-attack-mastermind-shot-dead-in-pok-11747920485261.html"},
        {"name": "The Hindu Business Line — Pulwama terror attack wanted Hamza Burhan shot dead in PoK", "url": "https://www.thehindubusinessline.com/news/pulwama-terror-attack-wanted-hamza-burhan-shot-dead-in-pok/article69611234.ece"},
        {"name": "LatestLY — Hamza Burhan Killed: Unknown Gunmen Eliminate Pulwama Attack Mastermind in PoK", "url": "https://www.latestly.com/india/national/hamza-burhan-killed-unknown-gunmen-eliminate-pulwama-attack-mastermind-in-pok-6649280.html"},
        {"name": "Inshorts — Pulwama attack mastermind Hamza Burhan killed by unknown men in PoK", "url": "https://inshorts.com/en/news/pulwama-attack-mastermind-hamza-burhan-killed-by-unknown-men-in-pok"}
    ]),
    "score_total": 94,
    "status": "published",
    "published_at": now,
    "body": """The man India held responsible for one of the deadliest terrorist attacks on its soil is dead. Arjumand Gulzar, known by his operational alias Hamza Burhan, was shot dead by unidentified gunmen in Muzaffarabad, the capital of Pakistan-occupied Kashmir, on Thursday morning. He was the designated mastermind of the February 14, 2019, Pulwama suicide bombing — a car packed with over 300 kilograms of explosives that rammed into a CRPF convoy on the Srinagar-Jammu highway, killing 40 paramilitary personnel in the worst terror attack in the Kashmir Valley in three decades.

Hamza was critically injured in the attack — three bullets to the head, fired at close range as he emerged from a college where he had been working as a principal, according to police in the area. He was airlifted to the Combined Military Hospital in Rawalpindi, where he was placed on a ventilator. Sources confirmed to PTI that he succumbed to his injuries shortly after. Pakistani police have arrested one suspect and recovered the weapon used in the attack. The other assailants fled before local security forces could intervene.

## A Terrorist Under State Protection

The circumstances of Hamza Burhan's life in Pakistan-occupied Kashmir tell their own story. He was living in Cheela Bandi, a densely populated neighbourhood on the outskirts of Muzaffarabad, with a security detail of eight commandos, a bulletproof vehicle, and an escort car — the kind of protection typically reserved for senior military officers or political figures. Indian intelligence sources have long maintained that this level of security indicated not just personal risk but operational importance to Pakistan's Inter-Services Intelligence.

The security cover was reportedly upgraded after Hamza staged what Indian officials describe as a "fabricated" attack on himself sometime between January and February 2025 — a move they say was designed to justify additional ISI resources and deepen his protection.

Originally from Khar in Pulwama district of Jammu and Kashmir, Hamza began his militant career with Al-Badr, a Pakistan-backed terror group that has operated in Kashmir since the 1990s. He later moved to Al-Baraq, a smaller outfit, before breaking away. Throughout, he maintained what Indian investigators describe as a "close alliance" with the ISI, particularly with an officer identified in dossiers as Colonel Rizwan.

He worked closely with Farooq Qureshi, a former Al-Baraq commander whose name appears in Indian intelligence dossiers linked to narcotics trafficking, counterfeit currency operations, arms smuggling, and cross-border militant operations. The two operated from an industrial compound in Muzaffarabad locally known as the "Machis Factory."

## The Pulwama Attack and Its Aftermath

The February 14, 2019, attack on the CRPF convoy remains seared into Indian national memory. A Jaish-e-Mohammad suicide bomber, Adil Ahmad Dar, drove an explosive-laden vehicle into a bus carrying jawans on the Srinagar-Jammu highway near Lethpora in Pulwama district. The blast was so powerful it scattered debris over a 100-metre radius and reduced the bus to twisted metal.

India's response came 12 days later. In the early hours of February 26, Indian Air Force jets crossed the Line of Control and struck what India described as the largest JeM training camp in Balakot, deep inside Pakistani territory. The airstrikes brought India and Pakistan to the brink of a full-scale military conflict — Pakistani jets crossed into Indian airspace the following day, and an Indian pilot, Wing Commander Abhinandan Varthaman, was captured and later released.

The Union Home Ministry designated Hamza Burhan a terrorist under the Unlawful Activities (Prevention) Act in 2022, formally linking him to the orchestration of the Pulwama bombing and to Pakistan-based terror infrastructure.

## Who Killed Him — and Why?

The identity and motives of the gunmen remain officially unknown, and that ambiguity is itself significant. The killing fits a pattern that Indian security analysts have tracked for years: high-profile militants and terror operatives in Pakistan and PoK being eliminated by "unknown assailants" in what are widely believed to be either internal militant rivalries, ISI housekeeping operations, or hits by foreign intelligence agencies.

Hamza had recently married the daughter of Qadir Lala, a former Hizbul Mujahideen operative from Kupwara who is now employed at a Hizbul housing project in Chek Shezad, Pakistan. He also maintained close ties with Murtaza, another former Hizbul operative from Pulwama now based in Islamabad. This web of connections across rival militant factions — Al-Badr, Al-Baraq, JeM, Hizbul — may have generated the kind of friction that makes men targets.

Indian officials have offered no public claim or comment. The silence is deliberate, and familiar.

## What This Means

For India's security establishment, Hamza Burhan's death is a milestone — one of the most wanted men linked to the Pulwama attack is now dead. But the broader infrastructure that enabled the 2019 bombing remains intact. Pakistan's policy of sheltering, arming, and deploying militants against India continues, and the ISI's network in PoK has not been dismantled by the loss of a single operative, however senior.

For the Indian diaspora, Pulwama occupies a specific place in collective memory. It was the attack that prompted candlelight vigils in Times Square and Trafalgar Square, that triggered calls from NRI organisations for sanctions on Pakistan, and that briefly made the prospect of a subcontinental war feel real. Hamza Burhan's killing does not undo the loss of 40 jawans. But for the families who have spent seven years demanding accountability, it is a grim and partial answer — delivered not by a courtroom, but by unidentified gunmen on a Muzaffarabad street."""
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: The $3 Trillion IPO Week — SpaceX + OpenAI
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "SpaceX and OpenAI Just Filed for the Two Biggest IPOs in History — in the Same Week. Indian-Origin Talent Built the Engines Behind Both.",
    "subheadline": "SpaceX's $1.75 trillion S-1 dropped on Tuesday. OpenAI's confidential filing, targeting $1 trillion, landed on Friday. Anthropic is eyeing October. The combined new equity supply could exceed $135 billion — and the Indian diaspora is entangled at every level, from the engineers who built the products to the investors betting billions on AI.",
    "slug": make_slug("spacex-openai-ipo-trillion-dollar-week-indian-diaspora"),
    "category": "technology",
    "vertical": "business",
    "diaspora_angle": "Indian-origin engineers and executives are deeply embedded in both companies — from OpenAI's research teams to SpaceX's propulsion division. SoftBank, with its $44 billion OpenAI stake, is led by a board that includes Indian-origin investors. NRI retail investors in the US face a historic allocation question: which trillion-dollar bet to make?",
    "tags": ["SpaceX", "OpenAI", "IPO", "Anthropic", "SoftBank", "AI", "Sam Altman", "Elon Musk", "Nasdaq", "Goldman Sachs", "Indian tech", "Silicon Valley"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Grey Journal — OpenAI Files Confidentially for Trillion Dollar IPO", "url": "https://greyjournal.net/news/openai-confidential-ipo-filing-trillion-valuation/"},
        {"name": "CNBC / Reuters — OpenAI to file for IPO in coming weeks, go public in Sept", "url": "https://www.reuters.com/technology/openai-prepares-confidential-ipo-filing-2026-05-20/"},
        {"name": "Zacks — IPO Mania: SpaceX On Deck", "url": "https://www.zacks.com/stock/news/2502876/ipo-mania-spacex-on-deck"},
        {"name": "Reuters — Bound for Mars, Elon Musk's SpaceX unveils filing for blockbuster IPO", "url": "https://www.reuters.com/business/spacex-unveils-filing-blockbuster-ipo-2026-05-21/"},
        {"name": "Wall Street Journal — SpaceX's AI Revenues Haven't Been Rocketing Upward", "url": "https://www.wsj.com/business/spacex-ai-revenues-ipo-2026/"},
        {"name": "The Motley Fool — SpaceX Finally Made Its S-1 Public. 3 Things Smart Investors Need to Know", "url": "https://www.fool.com/investing/2026/05/22/spacex-s1-ipo-3-things-investors-need-to-know/"}
    ]),
    "score_total": 90,
    "status": "published",
    "published_at": now,
    "body": """In the span of five days, two companies that have defined the technological ambitions of the 21st century — one building rockets to Mars, the other building intelligence that may replace the need to go — filed for initial public offerings that would collectively be worth more than the GDP of France. There is no precedent for what is about to happen to the stock market, and no community more entangled in both stories than the Indian diaspora.

SpaceX filed its public S-1 prospectus with the SEC on Tuesday, May 20, targeting a valuation between $1.75 trillion and $2 trillion under the Nasdaq ticker SPCX. It would be the largest IPO in stock market history, aiming to raise up to $75 billion, with Goldman Sachs, Morgan Stanley, Bank of America, Citi, and JPMorgan leading the deal. Trading is targeted for around June 12.

On Friday, May 22, OpenAI filed a confidential IPO prospectus with the SEC, targeting a valuation above $1 trillion with a public listing window between September and November 2026. Goldman Sachs and Morgan Stanley are leading the filing. OpenAI was last valued at $852 billion after closing a $122 billion funding round in March, backed by Amazon, Nvidia, and SoftBank.

And waiting in the wings: Anthropic, valued at $900 billion in private markets, has signalled it is weighing a public listing as early as October 2026.

## The Numbers Are Staggering

SpaceX's S-1 revealed $18.7 billion in revenue for 2025, against a net loss of $4.9 billion. The company operates three businesses: a profitable rocket launch division that dominates the global commercial launch market, Starlink — the satellite internet constellation that now has millions of subscribers — and a cash-hungry AI infrastructure unit that generated just $1.3 billion in revenue last year. Elon Musk retains 85.1 per cent of total voting power through a dual-class share structure. At $1.75 trillion, investors are paying 109 times revenue — a multiple that makes even the most generous tech valuations look quaint.

OpenAI's numbers tell a different story but arrive at a similar destination. Annualised revenue hit $25 billion in February 2026, up from roughly $4 billion a year earlier — a growth trajectory that Sam Altman has said should reach $100 billion by 2027. The company completed an 18-month restructuring from a capped-profit nonprofit into a Public Benefit Corporation, a legal conversion that was required before any public listing was possible. A federal jury dismissed Elon Musk's $134 billion lawsuit against OpenAI on May 18, removing the last major legal overhang just four days before the filing.

Combined, the two IPOs represent approximately $2.75 trillion in potential market capitalisation. Add Anthropic's expected listing, and the figure crosses $3.5 trillion. If all three companies price near their targets in the same quarter, combined new equity supply could exceed $135 billion. There is no modern precedent for that scale of capital absorption.

## The Indian Thread

The Indian diaspora's fingerprints are on both companies in ways that extend far beyond the familiar "Indians in tech" narrative.

At OpenAI, Indian-origin researchers and engineers have been part of the core teams building the models that power ChatGPT. The broader AI industry in San Francisco — where OpenAI, Anthropic, and dozens of AI startups are headquartered — is deeply staffed by Indian-origin talent, many of them H-1B visa holders or recent green card recipients who arrived through the same immigration pipeline now under political attack.

At SpaceX, Indian-origin engineers work across the company's propulsion, avionics, and Starlink divisions. The company's Hawthorne, California headquarters and its rapidly expanding Starbase facility in Texas employ thousands of engineers, a significant proportion of whom are immigrants or children of immigrants from India.

On the investment side, SoftBank — which has committed $44 billion to OpenAI and reported $25 billion in paper gains on that stake in the first quarter alone — is the single largest outside investor in the OpenAI IPO. Masayoshi Son's bet on OpenAI is now the defining position of his career, and SoftBank shares surged on the filing news. Indian-origin investors and fund managers across Wall Street will be key allocators in both offerings.

For NRI retail investors — and Indian Americans are among the most active retail trading demographics in the United States — the allocation question is unusually consequential. Both companies will likely be in the S&P 500 within a year of listing. Index funds will be forced buyers. But at current valuations, the entry price carries risk that no index inclusion can eliminate.

## What Makes This Week Different

The concentration of capital is the story. Three of the four firms that co-led Anthropic's $30 billion funding round also hold OpenAI positions. The largest growth-equity funds in the world are running parallel positions in two or three foundation-model companies simultaneously, and the IPOs will force those positions into the public market where they can be marked, traded, and scrutinised in real time.

For AI startups raising Series B and later rounds, the timing is treacherous. The late-2026 IPO window will absorb growth-equity capital that would otherwise flow into private rounds. Funds that wrote $2 billion cheques into Anthropic and OpenAI in 2025 and early 2026 will be allocating to the public offerings through Q4. Series B and Series C fundraises in adjacent AI categories should be planned around that liquidity rotation, not against it.

The public-market reception will also set the benchmark for every private AI valuation. Bloomberg has reported that some bankers privately estimate Anthropic's public-market valuation at $400 to $500 billion — a sharp discount to its $900 billion private mark. If OpenAI prices and trades materially below its private target, every AI startup carrying a 2026 valuation will face a markdown conversation at its next round.

## The Valuation Question

At 109 times revenue, SpaceX's asking price has no true comparable. Facebook went public at 12 times revenue. Tesla at six. Saudi Aramco at five. SpaceX's bull case rests on Starlink's global subscriber growth, the launch monopoly, and a speculative AI data-centre business that has barely started generating revenue. The bear case is simple arithmetic: the company lost $4.9 billion in 2025 and $4.3 billion in Q1 2026 alone.

OpenAI's valuation is less absurd on a revenue multiple basis — at $25 billion annualised revenue, a $1 trillion valuation implies roughly 40 times revenue, expensive but not unprecedented for a company growing at triple-digit percentages. The risk is whether that growth rate holds as competition from Anthropic, Google, and Meta intensifies, and whether the company can become profitable before its cash reserves require another infusion.

## What Happens Next

Three signals will define the second half of 2026. The first is SpaceX's June 12 trading debut — the single-day market reaction will calibrate every subsequent tech IPO for the year. The second is whether OpenAI flips its confidential filing public in July or August, locking in the September listing window. The third is Anthropic's decision: if it files in October, the fourth quarter of 2026 will absorb more tech IPO capital than any quarter in market history.

For Indian-origin engineers at both companies — many of whom hold equity grants that will vest or become liquid upon listing — the IPOs are not abstract market events. They are generational wealth moments. For the diaspora's investors, the question is simpler and harder: which trillion-dollar bet do you believe in more — the one heading to Mars, or the one heading toward artificial general intelligence?"""
})


# ══════════════════════════════════════════════════════════════
# INSERT ARTICLES
# ══════════════════════════════════════════════════════════════
print(f"Inserting {len(articles)} articles...")
for a in articles:
    try:
        result = sb_post("p2_articles", a)
        print(f"  ✓ {a['headline'][:80]}...")
    except Exception as e:
        print(f"  ✗ {a['headline'][:60]}... — {e}")

# Mark relevant topics
topic_ids_published = [
    "ea74ce96-8ab1-4a6d-8a5c-085ae6d39cea",  # Pulwama mastermind killed
    "4f3f290d-6327-420a-9315-1ee28951a16d",  # OpenAI IPO filing
    "b12919d1-1577-40da-b038-f36cf7f8946f",  # SpaceX IPO filing
]

for tid in topic_ids_published:
    code = sb_patch("p2_topics", f"id=eq.{tid}", {"status": "published", "updated_at": now})
    print(f"  Topic {tid[:8]} → published ({code})")

print("Done!")
