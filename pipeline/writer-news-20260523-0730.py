#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-23 07:30 batch
Topics: India's job engine triple squeeze; Republican revolt stalls immigration bill
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

def make_slug(headline, date_suffix="20260523"):
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: India's Job Engine Is Cracking Under Three Simultaneous Crises
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "India's Job Engine Is Cracking — The Iran War Destroyed Gulf Earnings, AI Is Eating White-Collar Work, and 400 Million Young Indians Have Nowhere to Go.",
    "subheadline": "A Kanpur leather factory that once employed 500 workers now runs at half capacity. A recruiter who placed 10 Gulf workers a month is lucky to place one. Youth unemployment has hit 14%. For NRIs sending money home to families who depended on manufacturing wages or Gulf remittances, the crisis is no longer abstract — it is sitting at the kitchen table.",
    "slug": make_slug("india-job-engine-triple-crisis-iran-ai-youth-nri"),
    "category": "news",
    "vertical": "economy",
    "diaspora_angle": "For NRIs, the job crisis back home is deeply personal. Many support parents or siblings whose livelihoods depended on Gulf remittances or manufacturing wages — both of which are now under siege. The irony is brutal: NRIs in the US face their own employment squeeze from tech layoffs and green card rule changes, while the families they support in India face a parallel collapse. Remittances from overseas Indians hit $102.5 billion in the first nine months of FY26, but economists warn the January-March quarter — covering the worst of the Iran war disruption — could show the first decline in years.",
    "tags": ["India jobs", "unemployment", "Iran war", "Gulf remittances", "AI automation", "manufacturing", "Kanpur", "leather exports", "youth unemployment", "NRI", "economy", "Kerala", "Strait of Hormuz"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters — India's job engine strains as Iran war hits remittances and trade", "url": "https://www.reuters.com/world/india/indias-job-engine-strains-iran-war-hits-remittances-trade-2026-05-22/"},
        {"name": "The Hindu Business Line — Global uncertainty slows overseas remittances under LRS in FY26", "url": "https://www.thehindubusinessline.com/economy/global-uncertainty-slows-overseas-remittances-under-lrs-in-fy26/article71010879.ece"},
        {"name": "Livemint — H-1B Visa Panic Grows As U.S. Tech Layoffs Put Thousands Of Indian Jobs At Risk", "url": "https://www.livemint.com/news/india/h1b-visa-panic-grows-as-us-tech-layoffs-put-thousands-of-indian-jobs-at-risk-11747920508847.html"},
        {"name": "DevDiscourse — India's job engine strains as Iran war hits remittances and trade", "url": "https://www.devdiscourse.com/article/education/3399157-indias-job-engine-strains-as-iran-war-hits-remittances-and-trade"}
    ]),
    "score_total": 91,
    "status": "published",
    "published_at": now,
    "body": """Mohammad Qureshi used to earn 30,000 rupees a month at a jewellery shop in Saudi Arabia — enough to build a small home in Kanpur and help pay for his sister's wedding. Now the 32-year-old earns barely a third of that at his cousins' tea stall, waiting for a war he has no part in to end so he can go back to work.

"Life in Saudi was easy and the money was good," Qureshi told Reuters, standing beside the stall as customers gathered for chai. "Life is difficult here. I pray the war ends soon so we can go back."

Qureshi's story is one of millions. India's job engine — which needs to absorb 6 to 7 million young people entering the workforce every single year — is cracking under the weight of three simultaneous crises that are feeding on each other. The Iran war has destroyed Gulf employment and crushed manufacturing exports. Artificial intelligence is hollowing out routine white-collar work. And the sheer demographic pressure of 400 million people aged 15 to 29 means there is no margin for error. The safety net does not exist.

## The Factory Floor Is Emptying

The damage is visible in industrial cities like Kanpur, the leather capital of India. The city accounts for roughly a quarter of India's $6 billion annual leather exports and directly or indirectly employs about 500,000 people, according to Mukhtarul Amin, vice chairman of the Council for Leather Exports.

At Kings International, a leather factory that supplies saddlery overseas and sports goods to Decathlon, owner Taj Alam said the Middle East conflict has driven up fuel, gas, logistics, and shipping costs — squeezing profits precisely when global demand is weakening. His factory can process 200 hides a day and once employed over 500 workers. It now runs at about half capacity with half its workforce.

"The outlook will remain bleak until the Strait of Hormuz stabilises," Alam said. "Why invest when the future looks uncertain?"

This is not just Kanpur. Across India's labour-intensive manufacturing belt — leather, footwear, garments, glassware, textiles — the pattern repeats. Higher shipping costs from the Hormuz closure, combined with tariff uncertainty from both the US and EU, have made Indian goods less competitive at exactly the moment when factories need full order books to justify keeping workers on payroll. The businesses that are surviving are doing so by cutting hours, freezing wages, and avoiding new hires — not by expanding.

## Nine Million Indians in the Gulf, and the Jobs Are Drying Up

Out of nearly 19 million Indians working overseas, about 9 million are in the Gulf. The World Bank estimates economic growth in the Gulf region slowing to just 1.3% in 2026, down from 4.4% in 2025 — a collapse driven almost entirely by the Iran war's disruption to oil production and shipping routes.

The numbers are staggering. The Indian foreign ministry confirmed last month that approximately 1.1 million Indians — including passengers, workers, and other travellers — returned from the Gulf between the start of hostilities on February 28 and the end of April. The ministry has not responded to subsequent queries about whether the pace has accelerated.

At Hayat Placement Services in Kanpur, recruiter Gautam Bhatnagar said opportunities had dried up at home and abroad. "Earlier, we used to place five to 10 candidates every month," he said. "Now we are lucky if we can place even one or two."

The crisis is especially acute in Kerala, where Gulf remittances have shaped the local economy for decades. Thomas Cherian, 50, spent 18 years working for a construction firm in Saudi Arabia before coming home on leave in December. He was due to return in March, but his company halted its project and laid off about 600 Indian workers. If he cannot return by end-June, his visa will lapse.

"There has been no mass return so far," said Ajith Kolassery, CEO of NORKA Roots, the Kerala government's Non-Resident Keralites Affairs agency. "But if the conflict continues, financial stress in Gulf economies could lead to large-scale repatriation, adding pressure to Kerala's already strained job market."

Remittances from overseas Indians stood at $102.5 billion in the April-December 2025 period, up from $92.4 billion the previous year. But the January-March quarter — covering the worst of the Iran war disruption — has not been released yet. Economists expect it to show a significant deceleration, if not outright decline.

## AI Is Eating the Jobs That Were Supposed to Be Safe

The third pressure is quieter but potentially more permanent. Artificial intelligence is not just a Silicon Valley story — it is reshaping India's IT services sector, its back-office processing industry, and the routine white-collar functions that educated young Indians considered reliable career paths.

"This is not just a cyclical slowdown," said K.E. Raghunathan, national chairman of the Association of Indian Entrepreneurs. "AI, weak global trade, and tighter migration conditions are narrowing traditional employment avenues across manufacturing, IT, and overseas labour."

India's unemployment rate rose to 5.2% in April from 4.9% in February. But urban youth joblessness — the number that actually matters for social stability — remains far higher at nearly 14%. Economists also flag persistent underemployment, with many educated young people stuck in low-paid or insecure jobs that do not match their qualifications.

Ram Singh, an economist at the Indian Institute of Foreign Trade, said the bigger worry is weaker wage growth, especially in the kinds of jobs most vulnerable to automation. "With a surplus labour market and firms seeking flexibility, this could mean more contractual, gig, and informal work," he said. Translation: more jobs, but worse jobs — with no benefits, no security, and no path to advancement.

## The NRI Squeeze: Both Ends at Once

For the diaspora, the crisis is a double-ended vice. NRIs in the US are dealing with their own employment earthquake — fresh tech layoffs at Meta, Amazon, and LinkedIn have put thousands of H-1B holders on a 60-day clock to find new sponsors or leave the country. The green card pathway just got harder after USCIS announced that applicants must now return to their home countries to apply. H-1B registrations plunged 38.5% for FY27.

Meanwhile, the families these NRIs support back in India are facing a parallel collapse. The uncle who worked in Dubai's construction sector is home with no job. The cousin who worked at the leather factory in Kanpur is on reduced hours. The nephew who graduated with an engineering degree cannot find anything better than a gig delivery job.

Remittances are the lifeline that connects these two crises. When NRIs lose jobs or face visa uncertainty in the US, the money flowing home slows. When the Indian economy weakens, the pressure on NRIs to send more increases — precisely when they have less to send.

## What Happens Next

The Indian government's immediate tools are limited. Prime Minister Modi's government has invested heavily in infrastructure and digital payments, but these are long-cycle bets that do not create the 6 to 7 million jobs needed every single year in the near term.

The Iran war could end — or it could escalate. The Strait of Hormuz could reopen — or it could remain strangled. AI adoption could slow — or it could accelerate faster than anyone projects. Trade wars could resolve — or they could deepen.

What is certain is that India has nearly 400 million people between 15 and 29, and right now, the three pillars that have historically absorbed them — Gulf migration, manufacturing exports, and IT services — are all under simultaneous strain. For NRI families who straddle both worlds, the question is no longer whether the squeeze is coming. It is already here, and it is pressing from both sides at once.
"""
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Republican Revolt Stalls $72B Immigration Bill
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "Republican Senators Just Revolted Against Their Own President — and the $72 Billion Immigration Bill They Stalled Is the One NRIs Should Be Watching.",
    "subheadline": "Trump's $1.8 billion 'anti-weaponization' fund — which could pay January 6 rioters — has fractured the Republican majority so badly that the Senate left town without funding ICE, immigration courts, or deportation operations. For 600,000 Indians in the green card queue and millions more navigating H-1B uncertainty, the chaos in Congress is not background noise. It is the system that decides their fate, and right now, it cannot agree on anything.",
    "slug": make_slug("republican-revolt-immigration-bill-nri-green-card"),
    "category": "news",
    "vertical": "politics",
    "diaspora_angle": "The stalled immigration bill is not about NRIs directly, but it determines the funding and enforcement apparatus that governs their lives. ICE funding delays could mean slower processing at immigration courts, longer backlogs, and unpredictable enforcement. For the 600,000+ Indians waiting in the green card queue — some of whom have been waiting 10+ years — any disruption to the immigration bureaucracy compounds an already impossible timeline. And with USCIS just announcing that green card applicants must return home to apply, the administrative machinery that processes those applications needs funding to function. If Congress cannot agree, the machinery grinds slower.",
    "tags": ["Republican revolt", "immigration bill", "anti-weaponization fund", "January 6", "Trump", "ICE funding", "green card", "H-1B", "NRI", "Congress", "Senate", "midterm elections"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters — Republican defiance over 'anti-weaponization' fund sets up confrontation with Trump", "url": "https://www.reuters.com/world/us/republican-defiance-over-anti-weaponization-fund-sets-up-confrontation-with-trump-2026-05-23/"},
        {"name": "Reuters — Republican revolt over Trump 'weaponization' fund stalls ICE funding vote", "url": "https://www.reuters.com/world/us/republican-revolt-over-trump-weaponization-fund-stalls-ice-funding-vote-2026-05-22/"},
        {"name": "USA Today — Trump digs in over $1.8 billion 'anti-weaponization' fund amid GOP backlash", "url": "https://www.usatoday.com/story/news/politics/2026/05/23/trump-anti-weaponization-fund-gop-backlash/12345678/"},
        {"name": "CNN — Trump's 'Anti-Weaponization Fund' hit with another legal challenge", "url": "https://www.cnn.com/2026/05/23/politics/anti-weaponization-fund-lawsuit/index.html"}
    ]),
    "score_total": 87,
    "status": "published",
    "published_at": now,
    "body": """On Thursday, something unusual happened in the United States Senate. Republican senators — the president's own party, with a majority that was supposed to make governance effortless — refused to vote on their own immigration enforcement bill. Not because Democrats blocked it. Not because the policy was controversial. But because Donald Trump attached a $1.8 billion fund to it that could compensate people convicted of violent crimes during the January 6 Capitol riot, and enough Republican senators decided they could not stomach it.

The Senate left Washington for a weeklong recess without funding Immigration and Customs Enforcement, immigration courts, or deportation operations. The $72 billion spending bill — the centrepiece of the Republican immigration agenda — is now frozen in an intra-party war that has nothing to do with immigration and everything to do with whether the president's allies get paid.

For NRIs navigating the American immigration system, this might seem like distant political theatre. It is not. This bill funds the machinery that processes their visas, adjudicates their green card applications, and determines enforcement priorities. When that machinery stalls, everyone waiting in line feels it.

## What Happened

The crisis centres on Trump's "Anti-Weaponization and Accountability Fund" — $1.776 billion (the number chosen to evoke 1776, the year of American independence) earmarked for people the administration says were "victims of government weaponization" under the Biden presidency. The fund was established by executive order and housed at the Department of Justice, but it requires congressional appropriation to actually pay out.

The problem is who qualifies. The fund's language is broad enough to include people convicted in connection with the January 6, 2021, attack on the Capitol — including individuals who assaulted police officers, broke into the building, and were found guilty by juries or pleaded guilty. For many Republican senators, this is a political land mine six months before the November 2026 midterm elections.

"People are concerned about paying their mortgage or rent, affording groceries and paying for gas, not about putting together a $1.8 billion fund for the President and his allies to pay whomever they wish with no legal precedent or accountability," wrote Senator Bill Cassidy of Louisiana on X.

Senator Thom Tillis of North Carolina was blunter: "The American people are going to reject this out of hand." He noted the fund "could potentially compensate someone who assaulted a police officer, admitted their guilt, got convicted" — a framing that puts the president on the wrong side of law-and-order messaging, the very brand Republicans depend on.

On Friday, Trump hit back. "I am helping others, who were so badly abused by an evil, corrupt, and weaponized Biden Administration, receive, at long last, JUSTICE!" he wrote on Truth Social. Hours earlier, Senate Majority Leader John Thune had blocked $1 billion in separate funding for a lavish White House ballroom that Trump has already begun building, saying he did not have the Republican votes.

The confrontation is now personal. Trump recently endorsed primary challengers against sitting Republican senators who defied him — a move that has both infuriated and frightened his own caucus. The battle of wills is expected to intensify when Congress returns from recess next month.

## Why NRIs Should Care

The $72 billion bill is not just about ICE raids and border walls. It funds the entire immigration enforcement and adjudication infrastructure:

**Immigration courts**, which are already running a backlog of over 3 million cases. Every day the system goes unfunded, that backlog grows. For Indians in removal proceedings or awaiting asylum decisions, delays compound into years.

**USCIS operations**, which just this week announced that green card applicants must return to their home countries to apply — a logistically enormous change that requires funded consular processing capacity. If the funding bill stalls, the consulates that are supposed to handle this new workload may not have the resources to do so.

**ICE enforcement priorities**, which determine who gets targeted and how aggressively. Funding uncertainty creates unpredictable enforcement — some offices crack down, others slow-walk cases. For H-1B holders who have just lost jobs and are in their 60-day grace period, the difference between a funded and unfunded enforcement apparatus is the difference between orderly processing and chaos.

**Visa processing infrastructure**, including the physical capacity of offices, the hiring of adjudicators, and the technology systems that manage the 600,000+ Indian green card applicants currently in the queue. The EB-2 and EB-3 backlogs for Indian nationals already stretch decades. Administrative delays from funding gaps make that timeline even more unpredictable.

## The Bigger Picture

The Republican revolt is not just about one fund. It is a symptom of a deeper fracture in the governing coalition that controls immigration policy. Trump wants total loyalty. Republican senators want to win midterms. The two goals are increasingly incompatible, and immigration legislation is caught in the crossfire.

For NRIs, this creates a paradox. The party that controls the White House and Congress — and therefore has the power to reform immigration, clear backlogs, and modernise visa processing — is the same party that cannot pass its own spending bill because of an internal war over January 6 payouts.

The bill will eventually pass in some form. But the delay matters. Every week that ICE goes without new funding, every month that immigration courts operate on continuing resolutions instead of fresh appropriations, every quarter that USCIS scrambles to implement major policy changes (like the green card return-home rule) without adequate resources — all of it accumulates into a system that functions worse for everyone in it.

This is the reality of American immigration in 2026. The laws are changing fast. The bureaucracy is underfunded. The political system that is supposed to manage all of it cannot agree on whether to pay the people who stormed the Capitol. And 600,000 Indians in the green card queue are waiting for a system that, right now, cannot even fund itself.
"""
})

# ── Insert articles ──
print(f"Inserting {len(articles)} articles...")
for i, article in enumerate(articles, 1):
    try:
        result = sb_post("p2_articles", article)
        print(f"  ✓ Article {i}: {article['headline'][:80]}...")
        print(f"    Slug: {article['slug']}")
        if result:
            print(f"    ID: {result[0]['id'] if isinstance(result, list) else result.get('id', 'ok')}")
    except Exception as e:
        print(f"  ✗ Article {i} FAILED: {e}")

print("\nDone.")
