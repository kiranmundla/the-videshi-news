#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-24 05:30 batch
Topics: 1) US-Iran 60-day ceasefire deal terms leaked via Axios/Reuters — Hormuz reopens toll-free, Iran clears mines, US lifts port blockade, sanctions waivers for oil sales, nuclear commitments; Pakistan mediating; India impact on oil, rupee, Gulf workers
        2) Tulsi Gabbard resigns as DNI — first Hindu to hold the role, sidelined from Iran war, fourth Cabinet departure, Iran praised her, Indian-American representation implications
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

def make_slug(text, date_suffix="20260524"):
    slug = text.lower()
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

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: US-Iran 60-Day Ceasefire Deal Terms — Hormuz Reopening, Nuclear Commitments, India Impact
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("us-iran-deal-terms-60-day-ceasefire-hormuz-mines-oil-india")
if slug1 not in existing_slugs:
    a1_id = str(uuid.uuid4())
    articles.append({
        "id": a1_id,
        "headline": "The Terms of the Iran Deal Just Leaked. Hormuz Reopens Toll-Free. Iran Clears Its Own Mines. The US Lifts Its Blockade. For India, This Is the Most Consequential Oil Document of the Decade.",
        "subheadline": "Axios reported on Saturday, citing a US official, that Washington and Tehran are close to signing a 60-day ceasefire extension under which the Strait of Hormuz would reopen without tolls, Iran would clear the mines it deployed in the waterway, and ships would pass freely. In exchange, the United States would lift its blockade on Iranian ports and issue sanctions waivers allowing Iran to sell oil on the open market. Iran has given verbal commitments through mediators — Pakistan's army chief is the primary interlocutor — to negotiate a suspension of uranium enrichment and the removal of its stockpile of highly enriched uranium. The deal also includes a commitment from Iran to never pursue nuclear weapons. For India, which imports 85 per cent of its crude oil and has endured five fuel price hikes since February, the Strait of Hormuz is not a geopolitical abstraction. It is the pipe through which the economy breathes. If this deal holds, oil could drop below $80 by year's end. If it doesn't, analysts warn of $200 a barrel by July.",
        "slug": slug1,
        "category": "news",
        "vertical": "world",
        "diaspora_angle": "The Hormuz closure has been the single most disruptive event for the Indian diaspora since COVID-19. Nine million Indians work in the Gulf states — UAE, Saudi Arabia, Qatar, Kuwait, Oman, Bahrain — and the war between the US-Israel coalition and Iran has placed them in a geography of active conflict. Remittances from the Gulf to India exceeded $30 billion in 2025; disruption to Gulf economies disrupts the financial lifeline that millions of Indian families depend on. In the US, Indian Americans are paying $4.50+ per gallon at the pump. In India, the rupee has fallen past 96 to the dollar, partly driven by India's ballooning oil import bill. The five fuel price hikes since February have cascading effects on food prices, transportation costs, and inflation that erode the purchasing power of every family in India — including those receiving remittances from the diaspora. A reopened Hormuz would immediately ease crude prices, stabilise the rupee, and reduce the fiscal pressure that has forced India to draw down its strategic petroleum reserves. For NRIs who invest in Indian markets, a Hormuz deal is the single biggest macro catalyst available.",
        "tags": ["Iran", "US", "Hormuz", "ceasefire", "oil prices", "India", "crude oil", "nuclear", "sanctions", "Pakistan", "NRI", "Gulf", "rupee", "fuel prices", "Axios", "Trump"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Axios says proposed US-Iran deal involves opening strait during 60-day ceasefire extension", "url": "https://www.reuters.com/world/asia-pacific/axios-says-proposed-us-iran-deal-involves-opening-strait-during-60-day-ceasefire-2026-05-24/"},
            {"name": "NY Post — Trump says Iran peace deal is near finalization — here's how it would reopen the Strait of Hormuz", "url": "https://nypost.com/2026/05/24/us-news/trump-says-iran-peace-deal-near-finalization-strait-of-hormuz/"},
            {"name": "The Hindu Business Line — Oil swings with market focused on US-Iran peace prospects", "url": "https://www.thehindubusinessline.com/markets/commodities/oil-swings-us-iran-peace/article69600123.ece"},
            {"name": "Reuters — Trump says Iran deal 'largely negotiated', would reopen Strait of Hormuz", "url": "https://www.reuters.com/world/middle-east/trump-says-iran-deal-largely-negotiated-2026-05-23/"},
            {"name": "The Hindu Business Line — Crude oil prices could hit $200 per barrel if Strait of Hormuz remains closed", "url": "https://www.thehindubusinessline.com/markets/commodities/crude-oil-prices-200-hormuz/article69590123.ece"}
        ]),
        "score_total": 92,
        "status": "published",
        "published_at": now,
        "body": """For three months, the Strait of Hormuz has been closed. Iran mined it. The United States blockaded it from the other side. Twenty per cent of the world's oil — roughly 17 million barrels a day — stopped flowing through the 33-kilometre chokepoint between Iran and Oman. Oil hit $105 a barrel. India hiked fuel prices five times. The rupee fell past 96. The Gulf economies where nine million Indians work began to crack under the pressure.

On Saturday, the terms of the deal that could end all of this leaked.

## What the Deal Says

Axios reported, citing a US official familiar with the negotiations, that Washington and Tehran are close to signing a framework agreement built around a 60-day ceasefire extension. The terms are specific:

**The Strait of Hormuz reopens.** During the 60-day period, the Strait would be fully open to commercial shipping, with no tolls. Iran would agree to clear the mines it deployed in the waterway in February and allow ships to pass freely. This is the single most important clause in the document.

**The US lifts its blockade.** In exchange for the Hormuz reopening, the United States would end its naval blockade of Iranian ports, which has been in place since the war began. American warships have been enforcing a no-entry zone around Bandar Abbas and other Iranian ports since March.

**Iran can sell oil again.** The US would issue sanctions waivers allowing Iran to sell crude oil on the open market during the 60-day period. Iran has not been able to export oil at scale since the war began, collapsing its primary source of revenue.

**Nuclear commitments.** Iran would commit to never pursuing nuclear weapons and would agree to negotiate the suspension of its uranium enrichment programme and the removal of its stockpile of highly enriched uranium. Iran has given verbal commitments through mediators about the scope of these concessions, according to two sources cited by Axios.

**Frozen funds.** The US would agree to negotiate the lifting of broader sanctions and the unfreezing of Iranian funds during the 60-day window. The total value of frozen Iranian assets across various jurisdictions exceeds $100 billion.

**Pakistan is the mediator.** Pakistan's army chief has been the primary interlocutor between Washington and Tehran, travelling between capitals as the backchannel that neither side would admit to in public. He arrived in Tehran this week amid signals of progress.

## What Iran Says

Iran's Fars News disputed the characterisation that a final deal has been reached. Tehran's position, expressed through its own media and through the Iranian Embassy in Armenia, is that the framework is still under discussion and that the US has not yet met key Iranian conditions.

This gap between American optimism and Iranian caution has defined the negotiation from the start. Trump declared the deal "largely negotiated" on Friday. Iran's foreign ministry did not confirm that characterisation.

The White House did not immediately respond to Reuters' request for comment on the Axios report.

## Why This Deal Is Different From the Last Three Announcements

The Hormuz crisis has produced a pattern: Trump announces progress, markets rally briefly, Iran denies finality, prices settle back. It has happened three times since March.

This round is different for two reasons.

First, the terms are specific. Previous announcements were vague — "progress," "framework," "largely negotiated." The Axios leak contains operational details: mine clearance, toll-free passage, sanctions waivers, port blockade removal. These are the building blocks of an executable agreement, not talking points.

Second, Secretary of State Marco Rubio is currently in India, meeting with External Affairs Minister Jaishankar and Prime Minister Modi. Energy cooperation has been the centrepiece of his visit. He told reporters on Saturday that the US is ready to sell India "as much energy as they'll buy." That pitch only works if the Strait is about to reopen and oil prices are about to drop — otherwise India has no leverage to diversify away from the Gulf.

The timing of the leak, Rubio's energy pitch, and Pakistan's army chief in Tehran all point toward a deal that is closer to real than the previous three rounds suggested.

## What This Means for Oil Prices

If the deal is signed and the Strait reopens, oil analysts project a rapid correction. The International Energy Agency has modelled a "Quick Peace" scenario in which a resolution by June would bring Brent crude down to around $80 per barrel by the end of 2026 and $65 by 2027.

The alternative is catastrophic. If the Strait remains closed, the same IEA analysis warns of oil at $200 per barrel by July, severe shortages through the third quarter, and a shallow global recession in the second half of 2026.

Currently, West Texas Intermediate is trading around $96 a barrel. Brent crude is at approximately $106. The war premium embedded in these prices is enormous — and it would evaporate almost overnight if ships start transiting the Strait again.

## What This Means for India

India imports approximately 85 per cent of its crude oil. The country consumed 5.3 million barrels per day in 2025. The Strait of Hormuz is the transit route for roughly 60 per cent of India's oil imports — crude from Saudi Arabia, Iraq, Kuwait, and the UAE all passes through the chokepoint.

The closure has forced India to reroute imports through longer, more expensive routes. Insurance premiums for tankers in the region have skyrocketed. The landed cost of crude has risen by an estimated $8 to $12 per barrel over pre-war levels, translating into billions of additional spending per quarter.

The consequences are visible at every petrol pump in India. Five fuel price hikes since February have pushed petrol past ₹115 per litre in most cities. Diesel — the fuel that moves India's trucks, trains, and agriculture — has crossed ₹105. These increases cascade through the entire economy: transportation costs rise, food prices follow, and the Consumer Price Index climbs.

The rupee has fallen past 96 to the dollar, driven partly by India's widening current account deficit as oil import costs balloon. The Reserve Bank of India has been intervening in foreign exchange markets to slow the decline, burning through reserves at an unsustainable rate.

A Hormuz reopening would provide immediate relief on all three fronts: lower crude costs, reduced fiscal pressure, and a stabilised rupee. The Petroleum Ministry has been preparing contingency plans for both scenarios — a deal, and no deal.

## What This Means for the Diaspora

For the nine million Indians working in the Gulf states, the Hormuz closure has been a slow-motion economic crisis. Gulf economies — particularly the UAE, Qatar, and Kuwait — depend on oil revenue and maritime trade. Construction projects have slowed. Hiring has frozen in several sectors. Some Indian workers have reported delayed salary payments.

Remittances from the Gulf to India exceeded $30 billion in 2025, making it the single largest source of diaspora income flowing back to the country. Any disruption to Gulf economic activity directly affects the families in Kerala, Tamil Nadu, Andhra Pradesh, Telangana, Rajasthan, and Punjab who depend on those monthly transfers.

NRI deposits in Indian banks have also been falling — data from earlier this month showed $2 billion in net withdrawals as overseas Indians moved money to safer jurisdictions amid uncertainty. A deal would reverse that outflow.

For Indian Americans, the impact is less direct but still significant. US fuel prices have risen above $4.50 per gallon in many markets, driven by the same Hormuz premium. The inflationary pressure has contributed to the Federal Reserve's decision to hold rates higher for longer under new chair Kevin Warsh, which in turn affects mortgage rates, auto loans, and the broader cost of living.

## The 60-Day Clock

Even if the deal is signed, 60 days is not peace. It is a window. During those 60 days, Iran would clear the mines. The US would withdraw its blockade. Ships would transit. Oil would flow. And both sides would sit down to negotiate the harder questions: permanent sanctions relief, the future of Iran's nuclear programme, the status of US forces in the region, and the reconstruction of the three nuclear sites the US and Israel destroyed last year.

Sixty days is also the timeline for the US to sell India on a long-term energy partnership. Rubio's pitch — buy American LNG, diversify away from the Gulf — only has traction if India believes the Hormuz disruption could happen again. If the deal leads to lasting peace, India's incentive to buy expensive American gas diminishes. If it leads to another closure, India will wish it had diversified while it had the chance.

The Strait of Hormuz is 33 kilometres wide. The deal to reopen it, if the leaked terms are accurate, would be one of the most consequential economic documents of the decade — not just for the Middle East, but for every country that burns oil to keep its economy running. India is the third-largest among them."""
    })
    print(f"Prepared article 1: US-Iran deal terms — {a1_id}")
else:
    print(f"Skipped article 1 (slug exists): {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Tulsi Gabbard Resigns as DNI — Sidelined, Praised by Iran, Indian-American Representation
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("tulsi-gabbard-resigns-dni-sidelined-iran-hindu-cabinet")
if slug2 not in existing_slugs:
    a2_id = str(uuid.uuid4())
    articles.append({
        "id": a2_id,
        "headline": "Tulsi Gabbard — the First Hindu to Run America's Intelligence Agencies — Just Resigned. She Was Sidelined From the Iran War. Iran Praised Her on the Way Out.",
        "subheadline": "On Friday, Director of National Intelligence Tulsi Gabbard submitted her resignation to President Trump, effective June 30, 2026, citing her husband Abraham Williams's diagnosis with an extremely rare form of bone cancer. She is the fourth Cabinet-level official to leave Trump's second term. The Wall Street Journal reported that Gabbard was largely sidelined from the Iran war before it began, was not informed of the Venezuela operation to snatch Nicolás Maduro, diverged from administration talking points by saying the US and Israel had 'differing objectives,' and spent recent months pursuing 2020 voter fraud theories at Trump's behest. Iran's embassy praised her after her resignation, saying she 'sometimes spoke truths about Iran that Trump hated.' For Indian Americans — who watched a Hindu woman of Samoan heritage become the first person of their faith to oversee 18 US spy agencies — her departure raises a question that has nothing to do with intelligence: when the most visible Hindu in the American government leaves, who fills the space?",
        "slug": slug2,
        "category": "news",
        "vertical": "world",
        "diaspora_angle": "Tulsi Gabbard's tenure as DNI carried outsized symbolic weight for Hindu Americans and the broader Indian-American community, even though she is of Samoan — not Indian — descent. She was the first Hindu to hold a Cabinet-level position in the US government. Her confirmation in February 2025 was covered extensively by Indian media and celebrated in some Hindu American circles as a milestone for religious representation. Her departure leaves no Hindu in the Cabinet. For a diaspora community that has produced CEOs at Google, Microsoft, Adobe, IBM, and Chanel, the gap between private-sector representation and political representation remains stark. Only five Indian Americans currently serve in Congress. Gabbard's exit also has operational implications: as DNI, she oversaw intelligence-sharing arrangements with India, including those relevant to counterterrorism and Indo-Pacific security — the very agenda that Rubio and Jaishankar are discussing in New Delhi this weekend. Her replacement will matter for the trajectory of US-India intelligence cooperation.",
        "tags": ["Tulsi Gabbard", "DNI", "resignation", "Hindu", "Cabinet", "Trump", "Iran", "intelligence", "Indian American", "Abraham Williams", "cancer", "representation", "NRI", "US politics"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "WSJ — Tulsi Gabbard Resigns as U.S. Intelligence Chief", "url": "https://www.wsj.com/politics/tulsi-gabbard-is-preparing-to-resign-as-u-s-intelligence-chief-2d6b2951"},
            {"name": "Reuters — Gabbard resigns as Trump's top US intelligence official", "url": "https://www.reuters.com/world/us/tulsi-gabbard-resigns-director-national-intelligence-2026-05-22/"},
            {"name": "CNN — Tulsi Gabbard is resigning as director of national intelligence", "url": "https://www.cnn.com/2026/05/22/politics/tulsi-gabbard-resigning-director-national-intelligence/"},
            {"name": "USA Today — Trump intelligence chief Tulsi Gabbard resigns, cites husband's cancer", "url": "https://www.usatoday.com/story/news/politics/2026/05/22/tulsi-gabbard-resigns-director-national-intelligence/"},
            {"name": "Inshorts — Iran praises Gabbard after resignation: 'You spoke truth'", "url": "https://inshorts.com/en/news/you-spoke-truth-iran-tulsi-gabbard-quits-us-intelligence-chief"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "body": """Tulsi Gabbard resigned on Friday as Director of National Intelligence, the official who oversees all 18 US spy agencies. In her resignation letter, posted on X and addressed to President Trump, she cited her husband Abraham Williams's recent diagnosis with an "extremely rare form of bone cancer."

"I cannot in good conscience ask him to face this fight alone while I continue in this demanding and time-consuming post," she wrote. Her resignation is effective June 30, 2026.

Trump responded on social media: "Tulsi has done an incredible job, and we will miss her." He announced that her deputy, Aaron Lukas, would serve as acting director.

The public response split along familiar lines. Republicans thanked her for her service. Democrats celebrated her departure. Iran praised her.

## What the Wall Street Journal Revealed

The resignation letter tells one story — a wife stepping away to care for a sick husband. The reporting tells another.

The Wall Street Journal reported that Gabbard was "largely sidelined" from Trump's national security operations throughout her tenure. She was not a significant part of conversations about the Iran war before it began in February. When Trump's team huddled at the end of 2025 to finalise the operation to extract Venezuelan strongman Nicolás Maduro, Gabbard was posting beach photos in Hawaii, unaware of the operation's details.

She repeatedly diverged from administration talking points on Iran. She said publicly that the United States and Israel had "differing objectives" in the war — a statement that contradicted the White House's position of unified command. She told reporters that Tehran had made "no efforts" to rebuild its nuclear programme since American attacks destroyed three nuclear sites last year — an assessment that put her at odds with the CIA's more hawkish reading of Iranian intentions.

Trump instead relied on CIA Director John Ratcliffe for intelligence consultations, effectively making Gabbard's role ceremonial in the most consequential national security crisis of his presidency.

In recent months, according to the Journal, Gabbard spent time pursuing theories of voter fraud in the 2020 election at Trump's behest. She appeared at a Fulton County, Georgia, election centre where FBI agents had seized voting machines earlier this year. State and local audits and recounts found no evidence of widespread tampering or fraud.

## Iran's Response

The Iranian Embassy in Armenia issued a statement after Gabbard's resignation that was remarkable for its specificity.

"You have previously shown at times that you work for America and not Israel," the statement said. "Sometimes you spoke truths about Iran that Trump hated. It was a pity that someone like you worked with this government."

For the DNI of the United States to receive a public compliment from the government she was ostensibly gathering intelligence against is, to put it mildly, unusual. The statement underscores the degree to which Gabbard's anti-interventionist views — the same views that made her a 2020 Democratic presidential candidate and later a Trump ally — created tension within an administration prosecuting a war she did not appear to support.

## The Fourth to Leave

Gabbard is the fourth Cabinet-level official to depart Trump's second term. Homeland Security Secretary Kristi Noem and Labour Secretary Lori Chavez-DeRemer left earlier this year. Attorney General Pam Bondi was pushed out for not moving swiftly enough on Trump's priorities. Gabbard's departure is officially voluntary, framed around her husband's health.

The front-runner to replace her is Michael Ellis, the deputy director of the Central Intelligence Agency, according to the Journal. Others being considered include Representative Elise Stefanik of New York. The position requires Senate confirmation.

## What Her Tenure Meant — and Didn't Mean — for Hindu Americans

Tulsi Gabbard is not Indian American. She is of Samoan descent, born in American Samoa, raised in Hawaii. But she is Hindu — a practising member of the faith since her teenage years, initiated into Gaudiya Vaishnavism. When she was confirmed as DNI in February 2025, she became the first Hindu to hold a Cabinet-level position in the history of the United States.

That milestone mattered to Hindu Americans. It was covered extensively by Indian media — Times of India, NDTV, India Today — and celebrated in Hindu American advocacy circles. The Hindu American Foundation issued a statement at the time calling her confirmation "historic." Indian American political action committees noted the symbolic significance.

The reality of her tenure was more complicated. Gabbard's Hinduism was rarely a factor in her policy positions. Her anti-interventionism predated and existed independently of her faith. Her support for Modi's government — she met the Prime Minister during her congressional tenure — was noted but never became a defining feature of her DNI role. The intelligence-sharing arrangements between the US and India continued on institutional tracks that neither required nor were shaped by the DNI's personal religious identity.

But symbols matter in diaspora politics. For Indian Americans — a community of 4.4 million that has produced the CEOs of Google, Microsoft, Adobe, IBM, and Chanel, but has only five representatives in Congress and zero in the Senate — political visibility at the Cabinet level is rare. Gabbard provided it, however imperfectly and however unrelated to India her actual work was.

Her departure leaves no Hindu in the executive branch at Cabinet level. The candidates to replace her — Ellis, Stefanik — are not Hindu. The symbolic gap reopens.

## The Operational Question

Beyond symbolism, Gabbard's replacement matters for US-India relations at a specific moment.

Secretary of State Rubio is currently in India, meeting with External Affairs Minister Jaishankar and Prime Minister Modi. The Quad Foreign Ministers' Meeting is scheduled for Monday in New Delhi. The agenda includes intelligence cooperation, maritime domain awareness, and counterterrorism — all areas that fall under the DNI's purview.

The US and India have deepened intelligence-sharing arrangements over the past decade, particularly on counterterrorism (Afghanistan, Pakistan-based groups), Indo-Pacific maritime surveillance (Chinese naval activity), and cyber threats. The DNI's office coordinates these arrangements across the 18 agencies it oversees — CIA, NSA, DIA, NGA, and others.

A new DNI — especially one who is not sidelined from the Iran war and who has the president's ear — could either strengthen or complicate these arrangements. Ellis, if nominated, comes from a CIA career track with extensive experience in signals intelligence and covert operations. His approach to India would likely be more institutionally grounded than Gabbard's, which was largely disengaged.

For Indian diplomats, the transition creates a brief window of uncertainty. Intelligence relationships between nations are built on personal trust between senior officials as much as on institutional agreements. A new DNI means new relationships to build, new priorities to negotiate, and a new personality to read.

## The Broader Pattern

Tulsi Gabbard's career trajectory — Democratic congresswoman, presidential candidate, party defector, Trump appointee, sidelined intelligence chief, early resignation — is uniquely American. No other democracy produces political biographies this volatile.

For the Indian diaspora, her story illustrates both the possibilities and limits of representation. A Hindu woman ran America's intelligence agencies. She was also, by most credible reporting, not actually running them — at least not during the most consequential period of her tenure. The title was real. The power, apparently, was not.

Her husband's cancer diagnosis is not a political story. It is a personal crisis that demands privacy and compassion. But the political story around her departure — sidelined, praised by an adversary, replaced by a CIA insider — is one that the Indian American community will read for what it says about the distance between symbolic milestones and actual influence.

Gabbard leaves office on June 30. She asked Trump to ensure "no disruption in leadership or momentum." Given that the momentum of her office was largely directed elsewhere during her tenure, the transition may be smoother than either side admits."""
    })
    print(f"Prepared article 2: Tulsi Gabbard resigns — {a2_id}")
else:
    print(f"Skipped article 2 (slug exists): {slug2}")


# ── Insert articles ──
for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ Inserted {art['id']} — {art['headline'][:80]}...")
    except Exception as e:
        print(f"❌ Failed to insert {art['id']}: {e}")

print(f"\n{'='*60}")
print(f"Published {len(articles)} articles at {now}")
print(f"{'='*60}")
