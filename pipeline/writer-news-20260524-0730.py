#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-24 07:30 batch
Topics: 1) India joins China/Japan/South Korea at WTO against UK steel tariffs — India-UK FTA stalled
        2) BLA suicide train bombing kills 24+ in Pakistan's Quetta — Pakistan mediating US-Iran deal while Balochistan burns
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

def sb_patch(table, params, data):
    h = {**HEADERS}
    r = requests.patch(f"{SB_URL}/rest/v1/{table}", headers=h, params=params, json=data, timeout=30)
    r.raise_for_status()
    return r

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
# ARTICLE 1: India Joins China at WTO Against UK Steel Tariffs — India-UK FTA Stalled
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("india-china-japan-wto-uk-steel-tariffs-fta-stalled-july")
if slug1 not in existing_slugs:
    a1_id = str(uuid.uuid4())
    articles.append({
        "id": a1_id,
        "headline": "India Just Sided With China Against Britain at the WTO. The India-UK Free Trade Deal — Signed Ten Months Ago — Has Not Been Implemented. Steel Is the Reason.",
        "subheadline": "At a WTO Council for Trade in Goods meeting in Geneva on May 20-21, India joined Japan, South Korea, China, Brazil, Australia, Switzerland and Turkey to protest the United Kingdom's decision to slash tariff-free steel import quotas by 60 per cent and impose a 50 per cent tariff on anything above the quota, effective July 1. India exported $900 million in iron and steel to the UK last year — a significant share of the $13.4 billion in total merchandise trade. The India-UK free trade agreement, called CETA, was signed on July 24, 2025, after years of negotiation. It promised tariff elimination on 99 per cent of Indian goods. But the deal has not been operationalised. India is refusing to implement it until the steel dispute is resolved. Commerce Secretary Rajesh Agrawal said India and the UK are working on a 'creative solution' — possibly an India-specific quota within the UK's new framework. For the 1.5 million British Indians and the thousands of workers employed by Tata Steel across the UK, this is not an abstract trade dispute. It is a test of whether the post-Brexit UK-India relationship will be defined by partnership or by protectionism.",
        "slug": slug1,
        "category": "news",
        "vertical": "economy",
        "diaspora_angle": "For the 1.5 million Indians in the United Kingdom, the India-UK FTA was supposed to be a milestone — a deal that recognised the £36 billion annual contribution of the British Indian community to the UK economy and formalised the economic ties that generations of Indians had built. Tata Steel, owned by India's Tata Group, is the UK's largest steelmaker. It employs over 8,000 people at Port Talbot in Wales and Scunthorpe in Lincolnshire. In January 2024, Tata announced plans to close the Port Talbot blast furnaces and transition to electric arc furnace steelmaking — a £1.25 billion investment backed by £500 million in UK government subsidies. The new UK steel tariffs add a layer of complexity to this transition: while Tata is restructuring its UK operations, the parent company's Indian steel exports to the UK face a 50 per cent tariff wall. British Indians in manufacturing, logistics, and trade are caught in the crossfire of a dispute between the two governments. For NRIs in the United States and Canada, this matters because the India-UK FTA was seen as a template for India's broader trade deal strategy — if the UK deal stalls, it raises questions about India's ability to simultaneously close deals with the EU and the US.",
        "tags": ["India", "UK", "WTO", "steel", "tariffs", "FTA", "CETA", "Tata Steel", "trade", "China", "Japan", "NRI", "British Indians", "protectionism", "Brexit"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu Business Line — India joins forces with China, Japan against UK steel curbs at WTO", "url": "https://www.thehindubusinessline.com/economy/india-joins-forces-with-china-japan-against-uk-steel-curbs-at-wto/article71007310.ece"},
            {"name": "The Daily Jagran — India Raises Concerns Over UK's Steel Safeguard Measures In WTO", "url": "https://www.thedailyjagran.com/business/india-raises-concerns-over-uks-steel-safeguard-measures-in-wto-details-10313241"},
            {"name": "SRK Analytics — India Joins Global Front Against UK Steel Tariffs as FTA Talks Continue", "url": "https://srkanalytics.com/india-joins-global-front-against-uk-steel-tariffs"},
            {"name": "The Hindu Business Line — India flags UK steel import curbs at WTO trade meeting", "url": "https://www.thehindubusinessline.com/economy/india-flags-uk-steel-import-curbs-at-wto/article71007300.ece"}
        ]),
        "score_total": 84,
        "status": "published",
        "published_at": now,
        "body": """On July 24, 2025, India and the United Kingdom signed a comprehensive free trade agreement. It was called CETA — the Comprehensive Economic and Trade Agreement. It promised tariff elimination on 99 per cent of Indian goods entering the UK. Trade ministers called it historic. Headlines called it the deal that would define the post-Brexit UK-India relationship.

Ten months later, the deal has not been implemented. India refuses to operationalise it. And this week, India stood alongside China at the World Trade Organization to formally protest British trade policy.

The reason is steel.

## What the UK Is Doing

From July 1, 2026, the United Kingdom will impose a new steel safeguard regime. The changes are severe:

**Tariff-free steel import quotas will be slashed by 60 per cent.** The UK will dramatically reduce the volume of steel that can enter the country duty-free under its existing safeguard measures.

**Anything above the reduced quota will face a 50 per cent tariff.** This is not a marginal increase. A 50 per cent duty on steel imports is a near-prohibitive barrier for most exporters.

**The measures target any steel product that can also be made in the UK.** This is a broad definition that covers a wide range of products, from flat-rolled steel to structural sections.

The UK's justification is existential: without these measures, Britain was on track to become the first G7 country without primary steelmaking capability. The UK steel industry employs tens of thousands and has been under pressure from cheap imports — particularly from China, which produces over half the world's steel.

## India's $900 Million Problem

India's iron and steel exports to the UK totalled approximately $900 million in FY2025-26, representing a meaningful share of the $13.4 billion bilateral merchandise trade. Much of this could be hit by the new safeguard measures.

At the WTO Council for Trade in Goods meeting in Geneva on May 20-21, India joined a coalition of steel-exporting nations to formally challenge the UK's decision. Japan and South Korea introduced the agenda item. India, China, Brazil, Australia, Switzerland and Turkey supported them.

The coalition's argument was pointed: concerns about global steel overcapacity should be addressed at the source — not through import restrictions that punish efficient producers. They questioned whether the UK's measures were consistent with WTO rules.

## The FTA Deadlock

The steel dispute has created a peculiar situation: India and the UK signed a free trade agreement that neither side is implementing.

The new steel measures were not accounted for in the CETA negotiations, which concluded in July 2025. India was promised broad tariff elimination — but the steel safeguard imposes an additional burden that effectively negates those promises for one of India's key export sectors.

India's response has been to stall. Commerce Secretary Rajesh Agrawal told reporters last week that the two sides are "working together to find a creative solution around the steel measure and operationalise the CETA at an early date."

The creative solution being explored is an India-specific quota within the UK's new framework — essentially carving out a protected lane for Indian steel within the broader tariff wall. But no agreement has been reached.

## India and China on the Same Side

The WTO challenge produced an unusual alignment: India and China, which are strategic competitors on nearly every other front, stood together against the UK.

This is not without precedent — trade disputes at the WTO routinely create unusual coalitions — but it underscores how the UK's steel policy has managed to unite countries that agree on very little else. China is the world's largest steel producer and the primary driver of the overcapacity that the UK is trying to address. India, which ranks as the world's second-largest steel producer, is caught in the same tariff net despite not being the source of the problem the UK is trying to solve.

For India, the optics are uncomfortable. New Delhi has spent the past several years positioning itself as an alternative to Chinese supply chains — the "China plus one" strategy that Western companies and governments have embraced. Siding with China against a key Western partner complicates that narrative.

## What This Means for the Indian Diaspora

For the 1.5 million British Indians — the UK's largest ethnic minority group — the India-UK FTA was supposed to be more than a trade document. It was a recognition of the community's £36 billion annual economic contribution and a formalisation of ties built over generations.

The steel dispute threatens that promise.

**Tata Steel is at the centre.** Tata Group's UK steel operations employ over 8,000 workers at Port Talbot in Wales and Scunthorpe in Lincolnshire. In January 2024, Tata announced a £1.25 billion plan to close the blast furnaces and transition to electric arc furnace steelmaking, backed by £500 million in UK government subsidies. The new steel tariffs add complexity: while Tata restructures its UK operations, the parent company's Indian steel exports face a 50 per cent tariff wall. Tata is simultaneously the UK's largest steelmaker and an Indian exporter being punished by UK policy.

**The broader British Indian business community feels the chill.** Indian-owned businesses in the UK span manufacturing, logistics, IT services, pharmaceuticals, and trade. A stalled FTA means delayed tariff relief across sectors — not just steel. The Double Contributions Convention, which would simplify cross-border work for temporary workers posted between India and the UK, is also stuck until the FTA is operationalised.

**For NRIs in America and Canada, the India-UK FTA was a template.** India is simultaneously negotiating trade deals with the EU (signed January 2026) and the United States (deal expected "in coming weeks or months" per Ambassador-designate Sergio Gor). If the UK deal — the simplest of the three — stalls over a single sector dispute, it raises questions about India's ability to close and implement the more complex EU and US agreements.

## What Happens Next

The immediate deadline is July 1 — the date the UK's new steel safeguards take effect. If India and the UK have not reached a bilateral resolution by then, Indian steel exports will face the 50 per cent tariff, and the FTA will remain frozen.

The WTO challenge is a parallel track, but WTO dispute resolution moves slowly. India's real leverage is bilateral: the UK wants the FTA implemented, and India can hold it hostage until the steel issue is resolved.

Commerce Secretary Agrawal's reference to a "creative solution" suggests both sides are still negotiating. An India-specific steel quota would allow the UK to maintain its broader safeguard while giving India a carve-out that reflects the FTA commitment. But the details — how large the quota would be, which products it would cover, and whether it would be time-limited — remain unresolved.

For the Indian diaspora watching from London, New York, and Toronto, the lesson is sobering: trade deals that take years to negotiate can be undermined in months by a single protectionist measure. The India-UK FTA was signed with ceremony and celebration. Its implementation may require something far more difficult: compromise."""
    })
    print(f"✅ Article 1 prepared: {slug1}")
else:
    print(f"⚠️ Article 1 slug already exists: {slug1}")

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Pakistan Quetta Train Bombing — BLA Suicide Attack Kills 24+
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("pakistan-quetta-train-bombing-bla-balochistan-iran-mediator")
if slug2 not in existing_slugs:
    a2_id = str(uuid.uuid4())
    articles.append({
        "id": a2_id,
        "headline": "The Country Brokering America's Iran Peace Deal Just Had 24 People Killed in a Train Bombing. The Balochistan Insurgency Is Pakistan's Open Wound — and It Sits on India's Doorstep.",
        "subheadline": "On Sunday morning, a suicide vehicle-borne IED detonated near a railway station in Quetta, the capital of Pakistan's Balochistan province, as a shuttle train carrying military personnel and their families passed through. At least 24 people were killed and over 70 injured. Two carriages overturned. The Baloch Liberation Army claimed responsibility, calling it a 'fidayeen attack.' The bombing happened on the same day that US Secretary of State Marco Rubio was in New Delhi discussing counter-terrorism with Indian Foreign Minister S. Jaishankar ahead of Monday's Quad Foreign Ministers Meeting. It happened while Pakistan's army chief — General Asim Munir — was serving as the primary interlocutor between Washington and Tehran in the Iran ceasefire negotiations. For India, which shares a western border with Pakistan and has invested in Iran's Chabahar port as a counter to the China-Pakistan Economic Corridor that runs through Balochistan, the bombing is a reminder that the most volatile geography in South Asia is not Kashmir. It is the 347,190-square-kilometre province that Pakistan's central government has never fully controlled.",
        "slug": slug2,
        "category": "news",
        "vertical": "world",
        "diaspora_angle": "For the Indian diaspora, Pakistan's internal security is not a distant concern — it is a variable in the calculus of every major geopolitical decision that affects India. The Iran ceasefire being brokered by Pakistan's army chief will directly determine oil prices, the value of the rupee, fuel costs for families in India, and the economic stability of the nine million Indians working in the Gulf. If Pakistan's internal fragility undermines its credibility as a mediator, the deal could collapse — and the economic consequences would fall disproportionately on India and its diaspora. The Quad meeting in Delhi on Monday, attended by Rubio, Jaishankar, and foreign ministers from Australia and Japan, will discuss counter-terrorism and maritime security. Balochistan is ground zero for the kind of non-state actor violence that the Quad was designed to address. For NRIs in the US, the political dimension matters too: Pakistan receives billions in US military aid, which is ostensibly meant to fight terrorism. The BLA attack raises the perennial question that Indian-American advocacy groups have raised in Congress: is US military aid making Pakistan safer, or is it subsidising a state that cannot secure its own railways?",
        "tags": ["Pakistan", "Quetta", "Balochistan", "BLA", "train bombing", "terrorism", "Iran", "ceasefire", "India", "Quad", "Rubio", "Jaishankar", "Chabahar", "CPEC", "NRI", "security"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — At least 24 killed in Pakistan train blast claimed by separatist militants", "url": "https://www.reuters.com/world/asia-pacific/blast-hits-train-southwest-pakistan-casualties-feared-2026-05-25/"},
            {"name": "CNN — Bomb attack near railway station in southwest Pakistan kills at least 23", "url": "https://www.cnn.com/2026/05/25/asia/pakistan-quetta-train-bombing-bla/index.html"},
            {"name": "The Sun — At least 24 killed in Pakistan train bombing as carriages overturned in fireball explosion", "url": "https://www.thesun.co.uk/news/35673214/pakistan-train-bombing-military-staff-killed/"},
            {"name": "Reuters — India, US discuss Middle East, trade as Rubio cites progress on Iran conflict", "url": "https://www.reuters.com/world/india/india-us-discuss-middle-east-trade-us-cites-progress-iran-conflict-2026-05-24/"}
        ]),
        "score_total": 83,
        "status": "published",
        "published_at": now,
        "body": """At approximately 9:30 AM local time on Sunday, a suicide vehicle-borne improvised explosive device detonated near a railway station in Quetta, the capital of Pakistan's Balochistan province. A shuttle train carrying Pakistani military personnel and their families was passing through. The explosion overturned two carriages, destroyed dozens of nearby cars and buildings, and sent shrapnel tearing through the area.

At least 24 people were killed. Over 70 were injured, many critically. Rescue workers pulled bloodied survivors from the wreckage as armed security forces stood guard.

The Baloch Liberation Army claimed responsibility, calling it a "fidayeen attack" — the Urdu term for a suicide mission.

## The Timing Is the Story

The bombing did not happen in a vacuum. It happened on a day when three separate diplomatic processes involving Pakistan were in motion:

**Pakistan is mediating the Iran peace deal.** Pakistan's army chief, General Asim Munir, is the primary interlocutor between Washington and Tehran in the ceasefire negotiations that could reopen the Strait of Hormuz. On Saturday, US President Donald Trump said the deal was "largely negotiated." Secretary of State Marco Rubio, in New Delhi, said more news could come on Sunday. The credibility of the mediator matters — and the BLA just demonstrated that Pakistan's own security forces cannot protect a routine train journey in Balochistan.

**The Quad Foreign Ministers Meeting is Monday.** Rubio, Indian Foreign Minister S. Jaishankar, and their counterparts from Australia and Japan will meet in New Delhi on May 26 to discuss maritime security, counter-terrorism, energy cooperation, and supply chain resilience. Counter-terrorism is on the agenda. The Quetta bombing will inevitably feature in those conversations.

**Rubio and Jaishankar discussed terrorism today.** The Reuters readout of Sunday's bilateral meeting in New Delhi confirmed that the two discussed the Middle East, trade, visas, maritime security, and energy. But it also confirmed that Rubio described India as a key partner on terrorism. The Quetta attack landed hours before or during those discussions.

## What the BLA Is

The Baloch Liberation Army is a separatist militant organisation fighting for an independent Balochistan. The group has intensified operations over the past two years, targeting military convoys, infrastructure projects, and Chinese workers associated with the China-Pakistan Economic Corridor (CPEC).

Balochistan is Pakistan's largest province by area — 347,190 square kilometres — but its poorest and least developed. It borders Iran to the west and Afghanistan to the north. The population is primarily ethnic Baloch, and decades of grievances over resource extraction, military operations, and political marginalisation have fuelled a long-running insurgency.

The BLA's attacks have grown more sophisticated and more frequent. In 2024, the group launched simultaneous attacks across multiple districts in what it called "Operation Heretic." In August 2024, a coordinated assault on the Gwadar port and surrounding areas killed dozens. The Pakistan military has responded with intensified counter-insurgency operations, but the insurgency has not been contained.

## India's Calculus

For India, the Balochistan insurgency is not a peripheral concern. It is embedded in the architecture of India's strategic competition with Pakistan and China.

**Chabahar vs. Gwadar.** India has invested $1.6 billion in developing Iran's Chabahar port — located less than 100 kilometres from Gwadar, the Chinese-built port that anchors the CPEC. Chabahar is India's gateway to Afghanistan and Central Asia, bypassing Pakistan entirely. But both ports sit in the same volatile geography. The security of the Chabahar corridor depends, in part, on the stability of the wider Balochistan region. When the BLA attacks infrastructure in Pakistani Balochistan, it signals a level of instability that affects the entire zone — including the roads and supply lines that connect Chabahar to its hinterland.

**CPEC vulnerability.** The China-Pakistan Economic Corridor runs directly through Balochistan. Chinese workers have been repeatedly targeted by Baloch separatists. Beijing has pressured Islamabad to provide security, and Pakistan has deployed thousands of troops to protect CPEC infrastructure. Every BLA attack that succeeds is a reminder that the corridor is vulnerable — and for India, which views CPEC as a sovereignty violation (it passes through Pakistan-administered Kashmir), the vulnerability of the project is strategically useful information.

**The Quad and counter-terrorism.** Monday's Quad meeting in Delhi will discuss how the four democracies — India, the US, Australia, and Japan — can cooperate on security in the Indo-Pacific and beyond. Pakistan's internal fragility is a subtext. The Quad does not directly address Pakistan, but the security challenges that emanate from the Pakistan-Afghanistan-Iran triangle — terrorism, narcotics, nuclear proliferation, and refugee flows — are core concerns for all four Quad members.

## The Mediator Problem

Pakistan's role as the Iran ceasefire mediator gives the Quetta bombing an additional dimension.

General Asim Munir has been the primary channel between Washington and Tehran. Pakistan has the unique advantage of maintaining relationships with both sides: it borders Iran, it has a Shia minority population with cultural ties to Iran, and it has been a US security partner for decades. The ceasefire framework being negotiated — Hormuz reopening, mines cleared, sanctions waivers for Iranian oil sales, nuclear commitments — is being structured through Pakistani intermediation.

But the BLA attack undermines the image of Pakistan as a stabilising force. A country that cannot prevent a suicide bombing on its own railway system in its own provincial capital is asking the world to trust it as the guarantor of a peace deal between the United States and Iran.

This is not a new problem. Pakistan has long juggled its role as a counter-terrorism partner while facing accusations of harbouring or tolerating militant groups on its own soil. The BLA is a separatist movement, not a religious extremist group — and Pakistan classifies it as a terrorist organisation — but the pattern is familiar: Pakistan projects strength and mediation capacity abroad while struggling to maintain control within its own borders.

## What This Means for the Indian Diaspora

For the nine million Indians working in the Gulf, the Iran ceasefire is the single most important geopolitical event of the year. If the deal holds, oil could fall below $80. If it collapses, analysts warn of $200 a barrel by July. The rupee, fuel prices, remittances, and the Indian stock market all depend on whether the Strait of Hormuz reopens.

Pakistan's credibility as the mediator of that deal matters because the deal's durability depends on the mediator's ability to enforce compliance, manage spoilers, and maintain back-channel communication. A Pakistan that is itself under attack from an insurgency that it cannot suppress is a weaker guarantor.

For Indian-Americans and British Indians, the political dimension is equally important. The US has provided Pakistan with billions of dollars in military aid over the past two decades. The question of whether that aid has made the region safer — or whether it has simply subsidised a state that cannot secure its own territory — is one that Indian-American advocacy groups have raised repeatedly in Congress. The Quetta bombing will add fuel to that argument.

The Quad meeting on Monday will produce a joint statement. It will reference counter-terrorism. It will reference maritime security. What it will not do is name Pakistan. But everyone in the room will know what happened on Sunday morning in Quetta."""
    })
    print(f"✅ Article 2 prepared: {slug2}")
else:
    print(f"⚠️ Article 2 slug already exists: {slug2}")

# ── Insert articles ──
if not articles:
    print("No new articles to insert")
    exit(0)

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ Inserted: {art['slug']} → {art['id']}")
    except Exception as e:
        print(f"❌ Failed to insert {art['slug']}: {e}")

print(f"\n✅ Done — {len(articles)} articles published")
