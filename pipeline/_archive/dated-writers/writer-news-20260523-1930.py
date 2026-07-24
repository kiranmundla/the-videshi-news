#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-23 19:30 batch
Topics: 1) Trump says Iran deal "largely negotiated" — what Strait of Hormuz reopening means for India
        2) Green Card applicants must now leave the US to apply — USCIS ends Adjustment of Status
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
    "limit": "60"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Trump says Iran deal "largely negotiated" — What the Strait of Hormuz reopening means for India
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("trump-iran-deal-largely-negotiated-hormuz-india-oil-nri")
if slug1 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Trump Says Iran Deal Is 'Largely Negotiated' and the Strait of Hormuz Will Be Reopened. For India — the World's Third-Largest Oil Importer — Everything Is at Stake.",
        "subheadline": "On Saturday, President Trump announced that a memorandum of understanding with Iran has been 'largely negotiated' and that the Strait of Hormuz — the chokepoint through which 20 percent of the world's oil passes — will be opened as part of the agreement. Iran's state-affiliated Fars news agency immediately disputed the claim, saying the strait will remain under Iranian control and that 'free passage as it existed before the war' will not return. The proposed framework unfolds in three stages: ending hostilities, gradually reopening the strait, and launching a 30-day window for broader nuclear negotiations. Pakistan's military chief Asim Munir, who has been mediating, left Tehran after what Pakistan called 'encouraging progress.' Trump told Axios the odds of a deal are '50/50' and that if talks fail, he will 'blow them to kingdom come.' For India, which imports 85 percent of its crude oil and has seen energy prices spike since the February conflict began, the stakes are existential — not just for the economy, but for the 9 million Indians working in the Gulf, the rupee at 97 to the dollar, and every NRI family watching oil prices from across the ocean.",
        "slug": slug1,
        "category": "news",
        "vertical": "world",
        "diaspora_angle": "Every NRI who has filled a gas tank, sent a remittance, or checked the USD-INR rate in the last three months knows what the Strait of Hormuz closure has cost. Petrol prices in India have climbed past ₹120 per litre in several cities. The rupee has weakened to 97 against the dollar — its worst level in history — driven partly by India's ballooning oil import bill. Cooking gas prices have risen. Freight costs have spiked, making everything from dal to electronics more expensive. For the 9 million Indians in the Gulf, the war has meant frozen projects, cancelled visas, and an economy that went from 4.4 percent growth to 1.3 percent in a year. A reopening of the strait would be the single most consequential economic event for India since the war began. It would ease crude prices, strengthen the rupee, reduce inflation, and restart the Gulf construction and services economy that employs millions of Indians. But Trump's '50/50' odds and Iran's immediate pushback — insisting on continued control of the strait — suggest this is not yet a done deal. For NRIs, this is the story to watch this weekend: not because of what Trump says, but because of what happens to the price of oil, the value of the rupee, and the safety of family members in the Gulf in the next 72 hours.",
        "tags": ["Iran", "Trump", "Strait of Hormuz", "India", "oil", "crude", "energy", "NRI", "Gulf", "rupee", "Pakistan", "Asim Munir", "ceasefire", "nuclear", "deal", "Rubio"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Trump says Iran deal 'largely negotiated', dispute over strait reopening", "url": "https://www.reuters.com/world/us/trump-says-iran-deal-largely-negotiated-dispute-over-strait-reopening-2026-05-24/"},
            {"name": "CNN — Trump says agreement with Iran has 'been largely negotiated' and Strait of Hormuz will be opened", "url": "https://www.cnn.com/2026/05/23/middleeast/iran-us-progress-framework-diplomacy-intl"},
            {"name": "NY Post — Iran war agreement being 'fine-tuned' as Trump meets with Gulf allies", "url": "https://nypost.com/2026/05/24/us-news/iran-war-agreement-being-fine-tuned-as-trump-meets-with-gulf-allies/"},
            {"name": "Reuters — Rubio touts US energy on India trip meant to repair ties", "url": "https://www.reuters.com/world/rubio-touts-us-energy-india-trip-meant-repair-ties-2026-05-23/"},
            {"name": "Investors.com — Dow futures: Trump says Iran deal near with Hormuz 'opened'", "url": "https://www.investors.com/market-trend/stock-market-today/dow-jones-futures-trump-iran-deal-hormuz-opened/"}
        ]),
        "score_total": 92,
        "status": "published",
        "published_at": now,
        "body": """On Saturday evening, President Donald Trump posted on Truth Social that a memorandum of understanding with Iran had been "largely negotiated" and that the Strait of Hormuz — the narrow passage between Iran and Oman through which roughly 20 percent of the world's oil transits — would be reopened as part of the agreement.

Within hours, Iran disputed the claim. The state-affiliated Fars news agency reported that the strait would remain under Iranian control and that "free passage as it existed before the war" would not return. Iran said it had agreed to allow vessel traffic to return to pre-war levels — but on its terms, with Tehran managing the waterway.

The gap between "the strait will be opened" and "the strait will be managed by Iran" is the gap between peace and continued crisis. And for India, the world's third-largest oil importer and a country whose economy has been battered by three months of disrupted energy supplies, the difference between those two versions of the deal is worth tens of billions of dollars.

## What Is Being Negotiated

Sources have told Reuters that the proposed framework unfolds in three stages. First: formally ending the war that began on February 28, when the United States and Israel launched strikes on Tehran. Second: resolving the crisis in the Strait of Hormuz, which Iran effectively closed to most shipping in retaliation. Third: launching a 30-day window — extendable — for broader negotiations on the most contentious issue: Iran's nuclear program and its stockpile of near-weapons-grade enriched uranium.

The agreement would also unfreeze some Iranian assets held in foreign banks — reportedly around $25 billion — and end the US blockade of Iranian ports. The ceasefire that has held, nervously, for several weeks would be formalized.

Pakistan has been the primary mediator. Army chief Asim Munir spent Friday and Saturday in Tehran meeting Iran's top negotiator Mohammad Baqer Ghalibaf and Foreign Minister Abbas Araqchi. The Pakistan military described the talks as "highly productive" and said that "intensive negotiations over the last twenty-four hours have resulted in encouraging progress towards a final understanding."

Trump spoke with leaders from Saudi Arabia, Qatar, the UAE, Jordan, Egypt, Turkey, and Pakistan on Saturday. According to a person briefed on the call, the leaders encouraged Trump to accept the proposed framework. A separate call with Israeli Prime Minister Benjamin Netanyahu "went very well," Trump wrote.

But Trump himself described the odds of a deal as "a solid 50/50" in a phone interview with Axios — and added that if talks fail, the US would "blow them to kingdom come."

## Why India Cannot Afford This to Fail

India imports approximately 85 percent of its crude oil. Before the war, India was importing roughly 4.5 to 5 million barrels per day, with a significant portion transiting the Strait of Hormuz. When the strait was effectively closed in early March, global oil prices spiked past $130 per barrel. They have since fluctuated between $100 and $120 — far above the $70-80 range that India's budget projections were built on.

The consequences have cascaded through every layer of the Indian economy. Petrol and diesel prices have risen sharply — crossing ₹120 per litre in several cities and approaching ₹130 in the northeast. Cooking gas prices have increased, hitting the poorest households hardest. The rupee has weakened to 97 against the dollar, driven by a widening current account deficit as the oil import bill has swelled. Inflation, which the Reserve Bank of India had spent two years bringing under control, has crept back above the RBI's comfort zone.

For India's government, the fiscal arithmetic is punishing. Every $10 increase in the price of crude oil costs India approximately $15 billion per year in additional import costs. At current prices, India's oil import bill is running roughly $40-50 billion higher than budgeted — a gap that cannot be covered without either cutting spending elsewhere, raising taxes, or accepting a wider fiscal deficit.

This is why Rubio is in India right now. The US Secretary of State arrived in Kolkata on Saturday — his first-ever visit to India — and has been pitching American energy. Washington wants India to diversify away from Gulf oil and buy more US liquefied natural gas. The timing is not coincidental: the US wants leverage with India on trade and defence, and energy dependence gives it a wedge.

## What It Means for the Gulf — and for 9 Million Indians There

The war's impact on India is not limited to oil prices. Approximately 9 million Indians work in the Gulf — the single largest concentration of the Indian diaspora anywhere in the world. They work in construction, healthcare, retail, engineering, and domestic services. Their remittances — which totalled $102.5 billion in the first nine months of FY25 — are India's single largest source of foreign exchange and fund entire regional economies, particularly in Kerala, Uttar Pradesh, coastal Karnataka, and Hyderabad.

The war has devastated Gulf economic growth. The World Bank estimates that the Gulf region's growth rate collapsed from 4.4 percent in 2025 to 1.3 percent in 2026. Construction projects have been halted. Recruitment pipelines have frozen. India's foreign ministry confirmed that approximately 1.1 million Indians returned from the Gulf between the start of hostilities in February and the end of April.

A reopening of the Strait of Hormuz would not immediately reverse this damage. Gulf economies would take months to restart stalled projects. Employers who laid off Indian workers will not rehire instantly. Visa pipelines that have dried up will take time to reopen. But it would signal the end of the immediate crisis — and for the millions of Indian families whose livelihoods depend on the Gulf, that signal matters enormously.

## The Nuclear Question Remains

The framework being negotiated deliberately separates the immediate issues — ending the war, reopening the strait — from the nuclear question. This is what worries Israel and many US hawks.

Mike Pompeo, Trump's former Secretary of State, criticized the emerging deal and compared it unfavourably to Obama-era agreements. "Not remotely America First," he wrote on X. White House communications director Steven Cheung responded with a profane rebuke, telling Pompeo to "shut his stupid mouth."

Senators Lindsey Graham and Roger Wicker, both Republican Iran hawks, expressed concern that Iran would emerge from the conflict with its nuclear capabilities intact and its control of the Strait of Hormuz enhanced — a fundamental shift in the regional balance of power.

Iran's chief negotiator Ghalibaf struck a defiant note, warning that Iran's armed forces "have rebuilt themselves during the ceasefire" and that if Trump restarts the war, "it will definitely be more crushing and bitter for America than the first day."

Iranian Foreign Ministry spokesman Esmail Baghaei said 30-day and 60-day timeframes had been included in the memorandum text but that nothing was finalized. "We must wait and see what will happen in the next three to four days," he said.

## The Next 72 Hours

The Eid holiday ends on Friday. Pakistani sources suggest that if the US accepts the memorandum, further talks could follow immediately after. Trump has suggested he could decide by Sunday whether to resume military action.

For India, the calculation is simple. A deal that reopens the Strait of Hormuz — even partially, even on Iran's terms — would lower oil prices, strengthen the rupee, reduce inflation, and restart the Gulf economies that employ millions of Indians. A collapse of the deal would send oil prices back above $130, weaken the rupee further, trigger another round of inflation, and extend the crisis for Gulf workers and their families indefinitely.

India's government has not commented publicly on the negotiations. Prime Minister Modi's conversation with Rubio on Saturday was described by both sides as focused on trade, energy, and defence cooperation. But behind the diplomatic language, the message from New Delhi is clear: India needs this war to end. Not next month. Not after a 30-day negotiation window. Now.

The strait opening is not just an energy story. It is a remittance story, a jobs story, a currency story, and a cost-of-living story. It is the story of 1.4 billion people whose daily lives — from the price of cooking gas to the value of the money their children send home from Dubai — depend on a narrow waterway between Iran and Oman, and on whether a deal announced on Truth Social actually holds.
"""
    })
else:
    print(f"  ⚠ Skipping Iran deal article — slug already exists: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Green Card Applicants Must Now Leave the US to Apply — USCIS Ends Adjustment of Status
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("green-card-applicants-must-leave-us-apply-home-country")
if slug2 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "The US Just Told Green Card Applicants to Leave the Country and Apply From Home. For Hundreds of Thousands of Indians on H-1B Visas, This Changes Everything.",
        "subheadline": "On Friday, USCIS announced that foreigners seeking green cards must now return to their home countries to apply, ending the decades-old Adjustment of Status process that allowed people already living and working in the US to apply without leaving. The policy affects an estimated 500,000 or more people currently in the green card pipeline — and Indians, who face the longest backlogs in the system (some dating back to 2012), are by far the most affected group. A day later, Secretary of State Marco Rubio announced an 'America First' visa policy in New Delhi that prioritizes business professionals — a surreal juxtaposition for Indian tech workers who have spent a decade waiting for a green card while building American companies. The Cato Institute called the policy 'illogical.' CNN reported it could 'upend the lives of hundreds of thousands.' Immigration attorneys say it will separate families, force people to abandon jobs, and create a logistical nightmare at overcrowded US consulates in India. For NRIs in the US, this is not an abstract policy change — it is the question of whether they will have to leave their homes, pull their children out of school, and fly to Chennai or Mumbai to sit in a consular queue for a process that could take years.",
        "slug": slug2,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "This story is not about immigration policy in the abstract. It is about the Indian software engineer in Seattle who has been on an H-1B visa for 11 years, whose priority date is 2015, who has two American-born children in elementary school, and who just learned that they may have to fly back to India to apply for the green card they have been waiting for since the Obama administration. It is about the doctor in New Jersey whose H-1B is employer-sponsored, whose green card application has been pending for seven years, and who now faces the question of whether to leave the country — abandoning patients, a mortgage, and a community — to sit in the US consulate in Mumbai. It is about the couple in Austin, both on H-1Bs, both with pending I-485s, who have built a life, bought a house, enrolled their children in school, and are now being told that the process they were promised — apply from within the US, wait your turn — no longer exists. India accounts for the largest share of employment-based green card applicants, and the backlog for Indians is the longest in the system. Some EB-2 and EB-3 applicants have been waiting since 2012. The new policy does not speed up the process — it just adds a plane ticket, a consular interview in a country many have not lived in for a decade, and the uncertainty of whether they will be allowed back in. Rubio's simultaneous announcement of an 'America First' visa policy that 'prioritizes business professionals' adds a layer of cognitive dissonance that every Indian tech worker in America will recognize.",
        "tags": ["green card", "H-1B", "immigration", "USCIS", "NRI", "Indian Americans", "adjustment of status", "Trump", "Rubio", "visa", "India", "consular processing", "tech workers", "backlog"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — USCIS tells foreigners seeking green cards: Return to your countries to apply", "url": "https://www.reuters.com/world/us/uscis-tells-foreigners-seeking-green-cards-return-your-countries-apply-2026-05-23/"},
            {"name": "CNN — Trump administration upends green card process, potentially compelling hundreds of thousands to leave US to apply", "url": "https://www.cnn.com/2026/05/22/politics/green-card-seekers-leave-us-apply"},
            {"name": "Fox News — Trump administration orders green card applicants to leave the US, apply from their home countries", "url": "https://www.foxnews.com/politics/trump-administration-orders-green-card-applicants-leave-us-apply-from-home-countries"},
            {"name": "Cato Institute — David J. Bier on 'illogical' green card policy and far-reaching impacts", "url": "https://www.cato.org/blog/new-green-card-policy-illogical"},
            {"name": "Inshorts — Marco Rubio announces 'America First' visa policy in India for business travel", "url": "https://inshorts.com/en/news/marco-rubio-announces-america-first-visa-policy-in-india-for-business-travel"}
        ]),
        "score_total": 91,
        "status": "published",
        "published_at": now,
        "body": """On Friday, May 22, the US Citizenship and Immigration Services issued a policy memo that will reshape the lives of hundreds of thousands of legal immigrants living and working in the United States. The core change: foreigners seeking green cards must now return to their home countries to apply.

"From now on, an alien who is in the U.S. temporarily and wants a Green Card must return to their home country to apply, except in extraordinary circumstances," USCIS spokesperson Zach Kahler said in a statement. "This policy allows our immigration system to function as the law intended instead of incentivizing loopholes."

The "loophole" he is referring to is Adjustment of Status — a process that has been the standard path to permanent residency for decades. Under Adjustment of Status, a person already in the US on a valid visa — an H-1B work visa, a student visa, a family-sponsored visa — could apply for a green card without leaving the country. They would file Form I-485, wait for their priority date to become current, attend a biometrics appointment and an interview, and eventually receive their green card. All without buying a plane ticket.

That process is now, effectively, over. USCIS has reclassified Adjustment of Status as an "extraordinary form of relief" — available only in exceptional circumstances, at the discretion of USCIS officers. The default path is now consular processing: leave the United States, return to your home country, schedule an interview at a US consulate, and wait.

## What This Means for Indians

About 1.4 million people obtained lawful permanent residence in fiscal year 2024. More than half of applicants were already in the United States when they applied. Of those, Indians represent the single largest national group in the employment-based green card queue.

The numbers are staggering. As of early 2026, there are an estimated 400,000 to 500,000 Indians in the employment-based green card backlog. Many are on H-1B visas. Many have been in the United States for 10, 15, even 20 years. Their children were born in America. They own homes, pay taxes, coach Little League teams, and attend PTA meetings. They have built lives.

The backlog for Indian EB-2 applicants — the category that covers most skilled workers — currently stretches back to priority dates in 2012. That means an Indian software engineer who filed their green card application in 2012 is still waiting. A person filing today faces an estimated wait of 50 to 80 years under current per-country caps.

Under the old system, these applicants could at least remain in the US while they waited. They could work, using Employment Authorization Documents tied to their pending I-485 applications. Their spouses could work. Their children could go to school. Life was on hold in one sense — they could not switch jobs freely, could not start businesses easily, could not travel without advance parole documents — but they were here. They had continuity.

The new policy threatens all of that. If Adjustment of Status is no longer available, applicants must go through consular processing. That means flying to India — to the US consulate in Mumbai, Chennai, Hyderabad, New Delhi, or Kolkata — scheduling an interview, and waiting for adjudication. The wait times at Indian consulates for immigrant visa interviews are already measured in months. Adding hundreds of thousands of cases to that pipeline will create a bottleneck of historic proportions.

## The Practical Nightmare

Immigration attorneys across the country have been fielding panicked calls since Friday. The questions are practical and urgent:

If I leave the US for my consular interview, can I come back? The answer is uncertain. If the green card application is denied at the consular stage, the applicant would have no legal status to return. Even if approved, the timeline is unknown.

What happens to my job? H-1B visas are employer-specific. Leaving the country for an extended consular processing period could result in job loss. Employers cannot hold positions indefinitely for employees whose return date is unknown.

What about my children? Many Indian families in the US have American-born children — US citizens by birth. The policy could force parents to choose between staying in the US without legal status or taking their American children to India for an indeterminate period.

What about my house, my lease, my community? These are not temporary visitors. These are people who have lived in the United States for a decade or more, contributing to the economy, paying into Social Security, building neighborhoods. The policy treats them as if their presence is provisional — as if 15 years of paying taxes and building a life were merely "a visit."

David J. Bier, the director of immigration studies at the Cato Institute — a libertarian think tank, not a liberal advocacy group — described the policy as "illogical" in a detailed blog post. "It will drive talented people to other countries and make America a less competitive place for business," he wrote.

## The Rubio Juxtaposition

The timing of the USCIS announcement is almost satirical. One day after telling green card applicants to leave the country, Secretary of State Marco Rubio — on his first-ever visit to India — announced an "America First" visa policy in New Delhi that would "prioritise professionals and business leaders who contribute to expanding India-US commercial ties."

The two policies are not technically contradictory. The new visa schedule appears to fast-track business visitor visas, not immigrant visas. But the optics are brutal: the United States is simultaneously telling Indian tech workers who have spent a decade building American companies to go home and apply from there, while telling Indian business leaders that they are welcome to visit.

For the Indian software engineer in the Bay Area who writes code for a Fortune 500 company, pays $4,000 a month in rent, has a pending I-485 from 2016, and just watched Rubio announce on television that America wants to "prioritise professionals" — the cognitive dissonance is not abstract. It is personal.

## Legal Challenges Are Coming

The policy is almost certain to face legal challenges. Immigration attorneys and advocacy organizations are already preparing litigation. The argument will centre on whether USCIS has the authority to effectively eliminate Adjustment of Status — a process codified in the Immigration and Nationality Act — through a policy memo rather than through legislation.

Representative Greg Stanton, an Arizona Democrat, said the policy "makes legal immigration harder — on purpose." Representative Ted Lieu of California called it "stupid" and predicted it would "help competitors such as China and Russia." New York Governor Kathy Hochul said the policy "betrays the very promise that built this country."

But legal challenges take time. The green card backlog does not pause while courts deliberate. And for the hundreds of thousands of Indians caught in the system — people who followed every rule, filed every form, paid every fee, and waited every year — the uncertainty is not a legal abstraction. It is the question of whether the life they have built in America is still theirs.

## What NRIs Should Know Right Now

The policy memo directs USCIS officers to evaluate Adjustment of Status requests on a "case-by-case basis" for extraordinary circumstances. This creates an enormous grey area. What counts as extraordinary? Medical emergencies? US citizen children? Long-standing community ties? The memo does not define the boundaries.

Immigration attorneys are advising clients to:

Do not panic and do not self-deport. The policy does not retroactively cancel pending I-485 applications. If you have an approved I-485 or are in the final stages, your case is likely unaffected.

Consult an immigration attorney immediately. The specifics of your case — your visa type, your priority date, your employer, your family situation — determine your exposure.

Document everything. If your case involves factors that could qualify as "extraordinary circumstances," begin assembling documentation now.

Watch for legal challenges. If a federal court issues an injunction blocking the policy, it would restore the status quo ante. This could happen within weeks or months.

The green card system was already the single greatest source of stress and uncertainty for Indian families in America. The backlog was already unconscionable. The per-country caps were already discriminatory. The wait was already measured in decades. This policy does not fix any of that. It adds a plane ticket, a consular interview, and the fear of not being able to come back to a system that was already broken.

More than 500,000 Indians are waiting. Their lives are in America. And the country they built those lives in just told them to go home and ask permission to stay.
"""
    })
else:
    print(f"  ⚠ Skipping green card article — slug already exists: {slug2}")


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
