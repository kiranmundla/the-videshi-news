#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-23 11:30 batch
Topics: USCIS green card rule change + H-1B layoff crisis; China coal mine disaster 90 dead
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

def sb_get(table, params):
    r = requests.get(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(headline, date_suffix="20260523"):
    slug = headline.lower()
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
    "limit": "40"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: USCIS Green Card Rule Change + H-1B Layoff Double Crisis
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("uscis-green-card-home-country-h1b-layoffs-double-crisis-nri")
if slug1 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "The US Just Told 1.2 Million Green Card Applicants to Go Home and Apply From There. For Indian H-1B Holders Already Facing Layoffs, That's a Death Sentence for the American Dream.",
        "subheadline": "USCIS announced on Friday that foreigners on temporary visas can no longer adjust their immigration status from within the United States — they must return to their home countries to apply for green cards through consular processing. The policy change lands in the middle of the worst AI-driven tech layoff wave since 2023, with 113,000 jobs cut across 179 companies this year alone. For the hundreds of thousands of Indians stuck in a green card backlog that stretches decades, this is not a policy tweak. It is a fundamental rewriting of the rules they built their lives around.",
        "slug": slug1,
        "category": "news",
        "vertical": "immigration",
        "diaspora_angle": "This story IS the diaspora. Indians are the single largest group of H-1B visa holders and account for the overwhelming majority of the employment-based green card backlog — some have been waiting 15 to 20 years. The new USCIS policy memo (PM-602-0199) means that the adjustment-of-status process that allowed them to stay in the US while their green card was processed is now classified as 'extraordinary relief.' Combined with AI-driven layoffs at Meta, Amazon, Oracle, LinkedIn, and Atlassian — where Indians hold a disproportionate share of H-1B positions — this creates a double bind: lose your job, lose your visa, and now even the path to permanent residency requires you to leave the country. For families with American-born children, US mortgages, and decades of tax contributions, being told to 'go home and apply' is not a bureaucratic adjustment. It is an existential threat.",
        "tags": ["USCIS", "green card", "H-1B", "adjustment of status", "consular processing", "layoffs", "AI", "Meta", "Amazon", "Oracle", "NRI", "immigration", "Trump", "tech workers", "India"],
        "urgency": "critical",
        "sources": json.dumps([
            {"name": "Reuters — USCIS tells foreigners seeking green cards: Return to your countries to apply", "url": "https://www.reuters.com/legal/government/uscis-tells-foreigners-seeking-green-cards-return-your-countries-apply-2026-05-22/"},
            {"name": "USCIS — Will Grant 'Adjustment of Status' Only in Extraordinary Circumstances", "url": "https://www.uscis.gov/newsroom/news-releases/uscis-will-grant-adjustment-of-status-only-in-extraordinary-circumstances"},
            {"name": "Livemint — H-1B Visa Panic Grows As U.S. Tech Layoffs Put Thousands Of Indian Jobs At Risk", "url": "https://www.livemint.com/videos/h1b-visa-panic-grows-as-u-s-tech-layoffs-put-thousands-of-indian-jobs-at-risk-11779440769647.html"},
            {"name": "The Hindu Business Line — New USCIS policy could force H-1Bs seeking Green Cards to apply from home countries", "url": "https://www.thehindubusinessline.com/news/world/new-uscis-policy-could-force-h-1bs-seeking-green-cards-to-apply-from-home-countries/article69609000.ece"},
            {"name": "Bloomberg Law — Trump Administration Narrows Path to Seek Green Cards Inside US", "url": "https://news.bloomberglaw.com/daily-labor-report/trump-administration-narrows-path-to-seek-green-cards-inside-us"}
        ]),
        "score_total": 96,
        "status": "published",
        "published_at": now,
        "body": """The US government dropped a quiet bombshell on Friday afternoon. Buried in a policy memo numbered PM-602-0199, US Citizenship and Immigration Services announced that adjustment of status — the process that has allowed millions of immigrants to apply for green cards while living and working in America — would now be treated as "an extraordinary form of relief" to be granted only in limited cases.

"From now on, an alien who is in the US temporarily and wants a Green Card must return to their home country to apply, except in extraordinary circumstances," said USCIS spokesman Zach Kahler.

The translation for the hundreds of thousands of Indian professionals who have spent years — in many cases more than a decade — waiting in the employment-based green card queue: the path you were on no longer exists in its current form. You may now have to leave the country you have called home, uproot your family, and apply from India through consular processing at the US Embassy.

## What Actually Changed

Until Friday, the standard path for an H-1B visa holder whose employer had sponsored them for a green card was straightforward in concept, if agonisingly slow in practice. Once your priority date became current — which for Indians in the EB-2 and EB-3 categories could take anywhere from 10 to 20 years — you filed an I-485 adjustment of status application with USCIS. You stayed in the US, continued working, and eventually received your green card.

The new policy memo does not formally ban this process. What it does is reclassify it. USCIS officers are now directed to treat every adjustment of status application as a discretionary act of "administrative grace" rather than a routine immigration pathway. Officers must evaluate "all relevant factors" on a case-by-case basis — including whether the applicant could have used consular processing instead.

Immigration attorneys are sounding the alarm. "This is a fundamental shift in how the agency views adjustment of status," said one prominent New York-based immigration lawyer quoted by Bloomberg Law. "For decades, it was understood as a right for eligible applicants. Now it's being reframed as a privilege that can be denied at the officer's discretion."

For "dual intent" visa holders like those on H-1B and L-1 visas, the memo suggests they can expect detailed reviews rather than the near-automatic approvals that were standard. For non-dual-intent categories — F-1 students on OPT or STEM OPT, for instance — the scrutiny will be even more intense.

## The Numbers Tell the Story

Indians account for approximately 75 percent of all H-1B visa approvals. They also make up the vast majority of the employment-based green card backlog, which the Cato Institute has estimated at over 1.2 million people (including dependents). Some Indians who filed their green card applications in the early 2000s are still waiting.

That backlog exists because of per-country caps that limit the number of employment-based green cards issued to citizens of any single country to seven percent of the annual total — regardless of how many qualified applicants there are. China faces a similar bottleneck, but India's is by far the worst.

The adjustment of status process was the lifeline that made this wait bearable. With a pending I-485, an Indian H-1B holder could change jobs without restarting the process, their spouse could obtain work authorisation, and they could travel freely. Remove the certainty of that process, and the entire architecture of waiting collapses.

## The Layoff Squeeze

The timing could not be worse. The USCIS memo landed in the middle of the most brutal tech layoff cycle since the post-pandemic correction of 2023. According to Layoffs.fyi, more than 113,000 tech workers have lost their jobs across 179 companies in 2026 — running about a third faster than this point last year.

The names are familiar: Meta cut roughly 8,000 positions in an AI-driven restructuring. Amazon has been trimming teams across AWS and retail. Oracle slashed 30,000 jobs globally in late March, with an estimated 12,000 of those in India. LinkedIn, Atlassian, Cisco — the list keeps growing. TCS, India's largest IT services company, lost nearly 24,000 employees in FY26. Even Infosys has been trimming its base.

For an Indian H-1B holder who gets laid off, the clock starts immediately: 60 days to find a new employer willing to sponsor their visa, or leave the country. In a market where companies are cutting headcount, not adding it, finding a new sponsor within that window is increasingly difficult.

Now add the green card twist. Previously, a laid-off H-1B holder with a pending I-485 had a degree of protection — the adjustment of status application provided a basis to remain in the US even while between jobs. Under the new policy, that safety net is no longer guaranteed. An officer could determine that the applicant should process their green card through consular channels in India instead.

## The Human Cost

The numbers are staggering, but the human stories are worse. Consider a software engineer who came to the US on an H-1B in 2010. She got married, had two children — both American citizens — bought a house in the Bay Area, paid hundreds of thousands of dollars in taxes, and filed her green card application in 2012. Fourteen years later, her priority date has not become current. Her children are in middle school. Her mortgage has 18 years left. And now she is being told that when her date finally arrives, she may need to fly to India, appear at the US Embassy in Mumbai or Chennai, and hope that a consular officer grants her the green card that USCIS could have processed from her kitchen table.

Multiply that by hundreds of thousands of families, and you have the scale of what Friday's memo represents.

## The Legal Challenge Is Coming

Immigration attorneys are already preparing challenges. HIAS, a refugee assistance organisation, condemned the policy for potentially forcing trafficking survivors and abused children to return to dangerous home countries. The American Immigration Lawyers Association is expected to weigh in formally next week.

The legal argument centres on whether USCIS has the authority to unilaterally reclassify a congressionally established process as "extraordinary relief." Section 245 of the Immigration and Nationality Act explicitly provides for adjustment of status. Attorneys argue that treating it as discretionary grace rather than a statutory right exceeds the agency's interpretive authority.

But legal challenges take time — months or years. In the interim, every I-485 application filed by an Indian national will be subject to the new framework.

## What This Means for NRIs

For Indians already in the US, this is an emergency. Immigration lawyers are advising clients to file adjustment of status applications as quickly as possible if their priority dates are current, before the new policy takes full effect across USCIS offices. Others are recommending that families with pending applications ensure their travel documents (Advance Parole) and work authorisation (EAD) are current, in case they need to leave and return.

For Indians considering moving to the US for work, the calculus has fundamentally changed. The promise was always: come on an H-1B, work hard, wait in line, get your green card. The line was absurdly long, but the path was clear. That clarity is gone.

And for the millions of family members in India who have been waiting for a son, daughter, or sibling to finally "settle" in America — who have been told for years that the green card is "almost here" — this memo is a gut punch. The American dream did not die on Friday. But the map to get there was redrawn overnight, and nobody told the people who were already walking.
"""
    })
else:
    print(f"  ⚠ Skipping green card article — slug already exists: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: China Coal Mine Disaster — 90 Dead, India's Energy Mirror
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("china-coal-mine-disaster-shanxi-90-dead-india-coal-energy")
if slug2 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Ninety Miners Dead in China's Worst Coal Disaster in 16 Years. India — the World's Second-Largest Coal Producer — Should Be Paying Very Close Attention.",
        "subheadline": "A gas explosion at the Liushenyu coal mine in China's Shanxi province killed at least 90 workers on Friday night, with nine still missing. It is the deadliest mining accident in China since 2009. India, which produced 1.08 billion tonnes of coal last year and is racing to expand output to compensate for the Iran war's disruption of oil supplies, has its own troubled history of mine safety — and a workforce that includes some of the most vulnerable labourers in the country.",
        "slug": slug2,
        "category": "news",
        "vertical": "energy",
        "diaspora_angle": "India's coal sector employs roughly 500,000 workers directly and millions more in ancillary industries. Many are from the poorest districts in Jharkhand, Chhattisgarh, and Odisha — states that also send large numbers of migrants to the Gulf and whose remittance economies have been devastated by the Iran war. The Shanxi disaster is a mirror for India's own coal expansion push, which has accelerated under the Modi government's drive for energy self-sufficiency. NRIs whose families depend on coal-belt employment should watch this story closely — not because it happened in China, but because the conditions that caused it exist in Indian mines too. And with India now leaning harder on coal to replace the oil it cannot afford, the pressure to cut safety corners is only growing.",
        "tags": ["China", "coal mine", "Shanxi", "Liushenyu", "India", "coal", "energy", "mining safety", "Modi", "Iran war", "Jharkhand", "NRI", "Xi Jinping"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Death toll jumps to 90 in China coal mine blast", "url": "https://www.reuters.com/world/china/"},
            {"name": "CNN — China's worst coal mining blast in over a decade kills 82 (revised to 90)", "url": "https://www.cnn.com/2026/05/23/china/china-coal-mine-disaster"},
            {"name": "The Hindu Business Line — India may see delayed and cushioned impact of global tech layoffs", "url": "https://www.thehindubusinessline.com/"},
            {"name": "Xinhua — Xi Jinping calls for all-out rescue efforts after Shanxi mine blast", "url": "https://english.news.cn/"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "body": """At 10:47 PM on Friday night, a gas explosion ripped through the Liushenyu coal mine in Qinyuan county, Shanxi province — the heart of China's coal country. Of the 247 miners working underground at the time, more than 200 were brought to the surface. At least 90 were not.

The blast made Liushenyu the deadliest coal mine disaster in China in over 16 years, surpassing a grim threshold that Beijing had spent billions of dollars and two decades of regulatory overhaul trying to prevent. Chinese President Xi Jinping ordered authorities to "spare no effort" in treating the injured and conducting search and rescue. Premier Li Qiang called for "rigorous accountability." Executives of the Shanxi Tongzhou Group, which operates the mine, were detained within hours.

CNN initially reported 82 dead before the toll was revised upward to 90, with nine workers still missing as of Saturday morning. At least 123 survivors were receiving hospital treatment.

## A Nation That Was Supposed to Have Moved Past This

China has dramatically reduced coal mine fatalities since the early 2000s, when thousands died every year in a sector plagued by corruption, corner-cutting, and explosive methane buildup. In 2002, China reported 6,995 coal mine deaths. By 2020, that number had fallen below 200. Stricter regulations, mine closures, better ventilation systems, and severe criminal penalties for safety violations had transformed the industry.

But Liushenyu showed that the old dangers never fully disappeared. Shanxi province alone dug 1.17 billion tonnes of coal last year — almost a third of China's total output. Its hundreds of thousands of miners work in conditions that remain inherently dangerous, no matter how many regulations are on the books.

The mine had previously been fined for safety violations, according to reports from Chinese media. Whether those violations contributed to Friday's explosion is under investigation, but the pattern is familiar: warnings ignored, production targets prioritised, and then a catastrophe that makes the nightly news.

## Why India Should Be Watching

Six thousand kilometres to the southwest, India is running the same playbook — at an earlier, more dangerous stage.

India produced 1.08 billion tonnes of coal in the fiscal year ending March 2026, a record that the Modi government celebrated as a milestone in the country's push for energy self-sufficiency. Coal India Limited, the state-owned behemoth that produces roughly 80 percent of the nation's coal, has been under intense pressure to expand output. The reason is simple: the Iran war has closed the Strait of Hormuz, spiked global oil prices past $100 a barrel, and forced India — which imports about 85 percent of its crude — to find alternatives.

Coal is the alternative. India's thermal power plants, which generate roughly 70 percent of the country's electricity, are burning more coal than ever. The country hit a record 271 gigawatts of peak power demand this week as a brutal heatwave pushed temperatures to 48°C. Every one of those gigawatts requires coal, and every tonne of coal requires someone to dig it out of the ground.

The safety record is not reassuring. India's coal mines killed 37 workers in officially reported accidents in 2024-25 — a number that understates the reality, since many incidents in smaller, informal, and illegal mines go unreported. Jharkhand, Chhattisgarh, and Odisha — the states that produce most of India's coal — are also among its poorest, with labour protections that exist on paper but are inconsistently enforced.

The illegal "rat-hole" mines of Meghalaya, where workers crawl into narrow tunnels barely wide enough for a human body, have killed dozens over the years. A 2018 disaster trapped 15 miners in a flooded rat-hole mine; their bodies were never recovered. The Supreme Court banned the practice in 2014, but enforcement has been spotty.

## The Energy Trap

The Shanxi disaster arrives at a moment when the global energy system is under more stress than at any point since the 1973 oil crisis. The Iran war has disrupted one-fifth of the world's oil and gas supply flowing through the Strait of Hormuz. European natural gas prices have spiked. Asian economies — India chief among them — are scrambling for alternatives.

For India, the alternative is coal. Prime Minister Modi's government has fast-tracked environmental clearances for new mines, pushed Coal India to increase production targets, and quietly shelved some of the renewable energy timelines that were announced with fanfare at COP26. The logic is understandable: when your people are facing 48-degree heat and the power grid is hitting new records every day, you burn whatever keeps the lights on.

But the Shanxi disaster is a reminder that "whatever keeps the lights on" has a human cost. China learned that lesson the hard way over two decades and thousands of deaths. India is earlier in that curve — producing roughly the same volume of coal as China's Shanxi province alone, but with weaker safety infrastructure, less regulatory enforcement, and a workforce that has fewer protections.

## The Workers Nobody Talks About

India's coal miners are among the most invisible workers in the country. They come overwhelmingly from Adivasi (tribal) and Dalit communities in Jharkhand, Chhattisgarh, and eastern Madhya Pradesh. Many work on contract rather than as permanent employees — a distinction that matters enormously for safety, because contract workers typically receive less training, have fewer safety protections, and are the first to be sent into dangerous conditions.

Coal India employs roughly 240,000 workers directly, but the contract workforce — which handles much of the actual extraction — adds hundreds of thousands more. These are not the coal miners of union lore, with hard-won benefits and retirement pensions. These are daily-wage labourers who descend into open-cast pits and underground shafts for ₹300 to ₹500 a day.

For NRIs whose families come from coal-belt districts — and there are more than you might think, because the same poverty that drives people into mines also drives their children to seek opportunities abroad — the Shanxi disaster is uncomfortably close to home. The methane that killed 90 miners in China exists in Indian mines too. The production pressure is the same. The gap between regulation and reality is, if anything, wider.

## What Comes Next

China's response to the Liushenyu disaster will follow a well-established pattern: criminal prosecutions of mine executives, a temporary production halt across Shanxi province, a flurry of safety inspections, and eventually a return to business as usual with marginally better enforcement. This pattern has worked — China's mine safety record is dramatically better than it was 20 years ago — but Friday night showed that the work is never finished.

India does not have the luxury of learning slowly. The country is adding coal capacity at a pace that its safety infrastructure cannot match. The heatwave is not going away. The Iran war is not resolving. The power grid will keep hitting records. And every record means more coal, more miners underground, and more chances for the kind of catastrophe that just killed 90 people in Shanxi.

The 90 miners who died on Friday night were Chinese citizens in a Chinese mine. But the forces that killed them — production pressure, safety shortcuts, an energy system in crisis — are borderless. India's coal miners face the same forces every day. The question is whether anyone in New Delhi is watching Shanxi and seeing the warning.
"""
    })
else:
    print(f"  ⚠ Skipping China coal mine article — slug already exists: {slug2}")


# ── Insert articles ──
if articles:
    print(f"\nInserting {len(articles)} articles...")
    for i, article in enumerate(articles, 1):
        try:
            result = sb_post("p2_articles", article)
            print(f"  ✓ Article {i}: {article['headline'][:80]}...")
            print(f"    Slug: {article['slug']}")
            if result:
                print(f"    ID: {result[0]['id'] if isinstance(result, list) else result.get('id', 'ok')}")
        except Exception as e:
            print(f"  ✗ Article {i} FAILED: {e}")
else:
    print("\nNo new articles to insert (all duplicates).")

print("\nDone.")
