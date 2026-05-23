#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-23 09:30 batch
Topics: Rubio's India visit / US-India trade deal; Iran peace talks 50/50 moment
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
    "limit": "30"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Rubio Lands in India — The First US Secretary of State Visit in 14 Years
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("rubio-india-visit-trade-deal-quad-modi-nri")
if slug1 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Rubio Just Landed in India With a $500 Billion Trade Target and an Energy Sales Pitch. What He Didn't Bring Is the One Thing Modi Actually Wanted.",
        "subheadline": "The first US Secretary of State visit to India in 14 years was supposed to signal a reset after tariffs and Trump's Beijing trip rattled New Delhi. Rubio touted American energy, discussed the Iran war, and delivered a White House invitation. But the comprehensive trade deal that India has been chasing since February remains unsigned — and the Quad summit that Modi hoped would bring Trump to India has been quietly downgraded to a foreign ministers' meeting for the third time.",
        "slug": slug1,
        "category": "news",
        "vertical": "diplomacy",
        "diaspora_angle": "For NRIs who straddle both economies, the Rubio visit is a barometer of the relationship that governs their professional and personal lives. The stalled trade deal directly affects IT services exports, pharmaceutical tariffs, and the cost of goods that diaspora families rely on. The $60 billion in American corporate investment commitments could mean more jobs in India for NRI families — or more competition for the same roles. And the energy conversation has a personal dimension: the Iran war that Rubio discussed with Modi is the same war that has driven up gas prices in the US and crushed Gulf remittances that NRI families depend on.",
        "tags": ["Marco Rubio", "India", "US-India", "trade deal", "Quad", "Modi", "energy", "tariffs", "NRI", "diplomacy", "Kolkata", "Sergio Gor", "Iran war"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Rubio touts US energy on India trip meant to repair ties", "url": "https://www.reuters.com/world/china/rubios-trip-india-signals-us-need-repair-ties-2026-05-23/"},
            {"name": "Livemint — India-US trade deal could be finalised in coming weeks or months, says Sergio Gor", "url": "https://www.livemint.com/news/india/indiaus-trade-deal-could-be-finalised-in-coming-weeks-months-says-sergio-gor-president-trump-pm-modi-11779410421535.html"},
            {"name": "DevDiscourse — US Secretary of State Marco Rubio arrives in Kolkata", "url": "https://www.devdiscourse.com/article/politics/3399000-us-secretary-of-state-marco-rubio-arrives-in-kolkata-as-part-of-his-4-day-visit-to-india"},
            {"name": "IANS — US Secretary of State Marco Rubio arrives in Kolkata, set to meet PM Modi", "url": "https://ianslive.in/news/us-secretary-of-state-marco-rubio-arrives-in-kolkata-set-to-meet-pm-modi-today-20260523"}
        ]),
        "score_total": 93,
        "status": "published",
        "published_at": now,
        "body": """Marco Rubio landed in Kolkata on Saturday morning — the first US Secretary of State to visit India in 14 years — and immediately headed to Mother House, the global headquarters of Saint Teresa's Missionaries of Charity. The symbolism was deliberate. The substance, however, was trickier.

In a meeting with Prime Minister Narendra Modi later that day, Rubio pushed American energy exports, discussed the Iran war, and delivered an invitation from President Trump for Modi to visit the White House. The US summary of the meeting said Rubio "emphasized that U.S. energy products have the potential to diversify India's energy supply" and that "the United States will not let Iran hold the global energy market hostage."

What Rubio did not bring was the one thing New Delhi has been waiting for: a signed trade deal.

## The $500 Billion Bet That Nobody Can Close

The numbers tell a story of ambition outrunning execution. Two days before Rubio's arrival, US Ambassador to India Sergio Gor told the American Chamber of Commerce that bilateral trade had grown eleven-fold over two decades — from $20 billion to over $220 billion in goods and services — and that both countries shared the ambition of hitting $500 billion by 2030.

"We are confident that in the coming weeks and months, this trade deal could be finalised," Gor said. Commerce Minister Piyush Goyal added that American companies had committed more than $60 billion in investments over the past six months alone.

But the deal itself remains elusive. In February, the two countries announced a "framework for an interim agreement" that would lower Trump's tariffs on Indian goods from a punishing 50 percent to 18 percent. Half of that original 50 percent had been linked to India's purchases of Russian oil — a punishment for a relationship Washington has spent years trying to disrupt.

Then the US Supreme Court struck down Trump's tariffs in late February, effectively bringing the duty rate on Indian goods down to 10 percent. That threw the entire negotiation into confusion. Why would India sign a deal locking in 18 percent tariffs when the current rate is 10 percent? The answer is that the Trump administration is pursuing trade investigations under unfair-practices legislation that is widely expected to restore much of the prior levies. India is essentially racing to sign a deal before the tariffs come back — while trying to get the best terms possible in the window.

"I do not expect Secretary Rubio will have much impact in changing the downward trajectory," said Richard Rossow of the Center for Strategic and International Studies. "The lack of a trade agreement — more than three months after the announcement of the 'interim deal' — clouds other areas of engagement."

## The Quad Downgrade Nobody Is Talking About

Rubio will attend the Quad Foreign Ministers' Meeting in New Delhi on Monday — the grouping of the US, India, Japan, and Australia that was supposed to be the centrepiece of Indo-Pacific strategy. But this will be the third consecutive Quad gathering without a leader-level summit, which Rossow called an "unannounced downgrade" of the grouping.

Modi has been pressing for a Trump visit to India, tied to a Quad leaders' summit. That fell by the wayside amid trade tensions, Trump's preoccupation with the Iran war, and his recent trip to Beijing — which amplified concerns in New Delhi about where India sits in Washington's hierarchy of relationships.

"Trump's approach has created a perfect storm of anxiety in India about the US relationship," said Basant Sanghera, a former State Department South Asia policy expert now with The Asia Group consultancy. "But ties have stabilized and both sides are trying to build momentum in the areas that there is convergence."

The convergence, for now, is energy. The Iran war has closed the Strait of Hormuz to most shipping, spiked global oil prices, and set back US efforts to wean India off Russian crude. Washington sees this as an opportunity to sell American LNG and oil to India — displacing both Russian and Gulf supplies. For India, which imports roughly 85 percent of its oil, the pitch is both tempting and politically complicated.

## The Pakistan Factor

Adding to New Delhi's discomfort is Pakistan's emergence as the primary mediator in the Iran peace talks. Pakistan's army chief Asim Munir has been shuttling between Washington, Islamabad, and Tehran, and Rubio himself acknowledged Pakistan's role on Saturday, saying "there's been some progress made" on Iran.

For India, watching its neighbour and rival become Washington's go-to interlocutor in the Middle East's biggest crisis is a strategic headache. The US-Pakistan rapprochement — driven by the Iran mediation — has been one of the most unexpected diplomatic shifts of 2026, and it complicates India's efforts to position itself as America's indispensable partner in the region.

## What This Means for NRIs

The stalled trade deal has real consequences for the diaspora. IT services exports — the backbone of the Indian economy and the sector that employs the families of millions of NRIs — are directly affected by tariff uncertainty. Pharmaceutical tariffs determine the cost of generic drugs that NRI families send back home. And the $60 billion in American corporate investment commitments could reshape the job market in both directions — creating opportunities in India while potentially outsourcing more roles from the US.

The energy conversation is equally personal. The Iran war that Rubio discussed with Modi is the same war that has driven gas prices above $5 a gallon in parts of the US, crushed Gulf remittances that NRI families depend on, and forced 1.1 million Indian workers to return from the Gulf since February.

Rubio's visit is a four-day, four-city affair — Kolkata, Agra, Jaipur, and New Delhi. The optics will be warm. The photos will be great. But for the 4.5 million Indians living in the United States and the millions more whose livelihoods depend on the US-India relationship, the only number that matters is the one on the trade deal. And that number is still missing.
"""
    })
else:
    print(f"  ⚠ Skipping Rubio article — slug already exists: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Iran Peace Deal at 50/50 — Trump's Decision Expected by Tomorrow
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("trump-iran-peace-deal-5050-strait-hormuz-nri-gulf")
if slug2 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Trump Says He's '50/50' on an Iran Deal and Will Decide by Tomorrow. If He Chooses War, 9 Million Indians in the Gulf Are in the Blast Radius.",
        "subheadline": "The president reviewed a draft peace agreement on Saturday, skipped his own son's wedding to stay in Washington, and warned he might 'blow them to kingdom come.' Pakistan's army chief just left Tehran after 'encouraging' talks. Iran says it has rebuilt its military during the ceasefire. For the Indian diaspora — from Gulf construction workers to NRI investors watching oil prices — the next 48 hours could determine whether the world's most dangerous conflict ends or escalates.",
        "slug": slug2,
        "category": "news",
        "vertical": "geopolitics",
        "diaspora_angle": "The Iran war has already displaced 1.1 million Indian Gulf workers since February, crashed Kerala's remittance-dependent economy, and driven up fuel costs for NRIs in the US. A peace deal would reopen the Strait of Hormuz, normalize shipping, bring down oil prices, and allow Gulf employers to resume hiring — directly benefiting the 9 million Indians working in the region. A resumption of war would do the opposite: accelerate the Gulf exodus, spike inflation on both sides of the ocean, and add to the pressure on NRI families already squeezed by H-1B uncertainty and green card backlogs. This is not a foreign policy abstraction for the diaspora. It is the single biggest variable in their economic lives right now.",
        "tags": ["Iran", "Trump", "peace deal", "Strait of Hormuz", "Gulf workers", "India", "NRI", "Pakistan", "Asim Munir", "oil prices", "war", "ceasefire", "nuclear", "Rubio"],
        "urgency": "critical",
        "sources": json.dumps([
            {"name": "Reuters — U.S. and Iran report progress on talks ending war, looking to next few days", "url": "https://www.reuters.com/world/asia-pacific/us-iran-report-progress-talks-ending-war-looking-to-next-few-days-2026-05-23/"},
            {"name": "New York Post — Trump says he's a 'solid 50/50' on Iran as he weighs peace deal", "url": "https://nypost.com/2026/05/23/us-news/trump-a-solid-50-50-on-iran-as-he-weighs-peace-deal-but-he-may-blast-them-to-kingdom-come/"},
            {"name": "Reuters — US Secretary of State Rubio sees progress in Iran talks, more work to be done", "url": "https://www.reuters.com/world/us-secretary-state-rubio-sees-progress-iran-talks-more-work-be-done-2026-05-23/"},
            {"name": "AP via Audacy — Rubio reports 'slight progress' in Iran talks as Pakistan renews efforts to mediate a peace deal", "url": "https://www.audacy.com/wben/news/national/rubio-reports-slight-progress-in-iran-talks-as-pakistan-renews-efforts-to-mediate-a-peace-deal"}
        ]),
        "score_total": 95,
        "status": "published",
        "published_at": now,
        "body": """Donald Trump said on Saturday that it was a "solid 50/50" whether he would accept a peace deal with Iran — and that if the answer is no, he would "blow them to kingdom come."

The president made the remarks as he prepared to review Iran's latest response to the American peace proposal with his negotiators, Steve Witkoff and son-in-law Jared Kushner. He said he had already seen a draft agreement but would not reveal whether he had approved it. He told CBS News: "They're getting a lot closer." He said he would likely make his decision by Sunday.

Trump also said he was skipping his own son's wedding this weekend to remain in Washington, citing Iran among the reasons. That alone signals how close to the wire this has become.

## Three Capitals, One Weekend, No Guarantee

The diplomatic push is happening simultaneously across three capitals. In Tehran, Pakistan's army chief Asim Munir met Iran's top negotiator Mohammad Baqer Qalibaf and Foreign Minister Abbas Araqchi before sitting down with President Masoud Pezeshkian. The Pakistani military said the previous 24 hours of negotiations had produced "encouraging" progress towards a final understanding.

In New Delhi, US Secretary of State Marco Rubio — on a four-day India visit — said there had been "some progress made, even as I speak to you now." He added: "There is a chance that, whether it's later today, tomorrow, in a couple days, we may have something to say."

And in Washington, Trump is weighing a decision that could end the most disruptive conflict since the 2003 Iraq invasion — or escalate it into something far worse.

The talks are centred on a 14-point document proposed by Iran. The key sticking points are predictable but enormous: the Strait of Hormuz, which Iran has kept closed to most shipping since the war began; Iran's stockpile of near-weapons-grade enriched uranium, which the US and Israel want surrendered; and the conflict in Lebanon, where Iran-allied Hezbollah fighters are engaged with Israeli forces in the south.

Rubio repeated Trump's red lines from India: "Iran can never have a nuclear weapon. The straits need to be open without tolls. They need to turn over their enriched uranium."

Iran's Foreign Ministry spokesperson Esmail Baghaei offered a more cautious assessment: "The trend this week has been towards a reduction in disputes, but there are still issues that need to be discussed through mediators. We will have to wait and see where the situation ends in the next three or four days."

## Iran's Warning Shot

Perhaps the most significant statement came from Qalibaf himself. He said Iran's armed forces had used the ceasefire period to rebuild their military capabilities and warned that if the United States "foolishly restarts the war," the consequences would be "more forceful and bitter" than at the start of the conflict.

That is not empty rhetoric. Despite weeks of US and Israeli strikes, Iran has preserved its stockpile of enriched uranium, maintained its missile and drone capabilities, and kept its proxy networks in Lebanon, Iraq, and Yemen operational. A second round of hostilities would not be a replay of the first — it would be fought by an adversary that has had time to prepare.

For Trump, the calculus is both strategic and political. The war has hammered his approval ratings — energy prices have been the single biggest driver of consumer dissatisfaction, and voters in swing states are paying over $5 a gallon at the pump. A deal would allow him to claim a historic diplomatic achievement. A resumption of war, especially one that drives oil even higher, could be devastating heading into the November 2026 midterms.

## What a Deal Would Mean — and What War Would Cost

The stakes for the Indian diaspora are staggering.

**If a deal is reached:** The Strait of Hormuz reopens. Global oil prices, currently hovering around $107 a barrel, could drop sharply. Gulf economies, which have been contracting since the war began, would resume hiring. The 9 million Indians working in the Gulf — who account for a significant chunk of India's $120-plus billion annual remittance inflow — would see their jobs stabilise and, in many cases, return. Gas prices in the US would fall, easing the cost-of-living squeeze that NRIs have been feeling alongside every other American consumer.

**If war resumes:** Oil prices could spike past $130. The Strait of Hormuz stays closed indefinitely. Gulf economies contract further, accelerating the exodus of Indian workers — already 1.1 million have returned since February. Kerala's remittance-dependent economy, already under severe strain, faces potential crisis. Indian manufacturing exports, already hurt by shipping disruptions, take another hit. And for NRIs in the US, higher energy costs mean higher inflation, which means higher interest rates, which means a tighter housing market and a harder environment for the tech sector that employs hundreds of thousands of Indian-origin workers.

## Pakistan's Moment — and India's Anxiety

The most geopolitically awkward element for India is Pakistan's central role in the mediation. Asim Munir has emerged as the primary shuttle diplomat between Washington and Tehran — a role that has given Islamabad more diplomatic relevance than it has had in years.

India, which considers itself the natural interlocutor for the region and has historically maintained decent relations with both the US and Iran, has been largely sidelined. Modi told Rubio on Saturday that India supports "peaceful resolution of conflict through dialogue and diplomacy," but the statement was generic and carefully avoided mentioning Iran by name.

For the diaspora, the Pakistan angle adds another layer of complexity. Indian-Americans who have watched their home country invest heavily in its relationship with Washington now see Pakistan — with a fraction of the diplomatic infrastructure — playing the decisive role in the biggest crisis of the decade.

## The Next 48 Hours

Trump's "50/50" framing is characteristically dramatic, but it tracks with the actual state of play. Both sides have moved closer. Neither has moved enough. The window for a deal is measured in days, not weeks — Rubio said as much from New Delhi, and Iran's spokesperson put it at "three or four days."

For 9 million Indians in the Gulf, for the families in Kerala and Uttar Pradesh who depend on their remittances, for the NRIs in the US watching gas prices and mortgage rates, and for anyone with money in markets that swing on every Hormuz headline — this weekend is not background noise. It is the most consequential 48 hours of 2026, and the outcome is genuinely uncertain.
"""
    })
else:
    print(f"  ⚠ Skipping Iran article — slug already exists: {slug2}")


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
