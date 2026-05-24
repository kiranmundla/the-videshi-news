#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-24 13:30 batch
Topics: 1) Russia fires Oreshnik hypersonic missile at Kyiv — India's balancing act between Moscow and Washington
        2) Modi and Trump set for first face-to-face in 16 months at G7 Évian — $500B trade deal, Iran, visas on the table
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
# ARTICLE 1: Russia Fired a Nuclear-Capable Missile at Kyiv.
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("russia-oreshnik-missile-kyiv-india-neutral-stance-nri-diaspora")
if slug1 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Russia Just Fired a Nuclear-Capable Missile at Kyiv. India Bought $10 Billion in Russian Oil Last Month. The Balancing Act That Defines the Diaspora's Geopolitical Reality Just Got Harder.",
        "subheadline": "On Sunday, Russia launched 90 missiles and 600 drones at Ukraine's capital in one of the heaviest bombardments of the four-year war. Among the weapons was an Oreshnik — an intermediate-range hypersonic missile capable of carrying nuclear warheads. It was only the third time Russia has used the weapon. A Chernobyl memorial museum was destroyed. Nearly 100 people were wounded. European leaders called it an escalation. India said nothing. For the 4.4 million Indian Americans watching from the US, India's silence on Russia has become the single most complicated feature of their dual identity — because the same country that sells them their H-1B visas also buys discounted crude from the country firing hypersonic missiles at European cities.",
        "slug": slug1,
        "category": "news",
        "vertical": "world",
        "diaspora_angle": "For NRIs in America, India's relationship with Russia is not an abstract geopolitical question — it is a daily tension that affects their professional and social standing. When colleagues at American companies ask 'Why won't India condemn Russia?', there is no one-sentence answer. India buys Russian oil because the Iran war has pushed global crude prices above $100 a barrel and the Indian economy cannot function without affordable energy. India buys Russian defence equipment — the S-400 missile system, MiG-29 fighters, nuclear submarine leases — because decades of procurement decisions cannot be reversed overnight. India abstains from UN votes condemning Russia because it needs Russian diplomatic support on Kashmir at the Security Council. All of this is true simultaneously. But the Oreshnik changes the calculus. This is not a conventional weapon. It is an intermediate-range ballistic missile designed to carry nuclear warheads, fired 40 miles from a capital city of 3 million people. European leaders called it 'nuclear brinkmanship.' The EU's top diplomat called it a 'scare tactic.' India's External Affairs Ministry issued no statement. This silence has consequences for the diaspora. Every time India refuses to condemn Russian aggression, it complicates the narrative that Indian Americans have built over decades — that India is the world's largest democracy, a natural ally of the West, a rules-based partner. When the US considers H-1B quotas, trade deals, and technology transfers, India's Russia relationship is a factor. When Congress debates the $500 billion bilateral trade target that Rubio just discussed in New Delhi, someone will ask why America should deepen economic ties with a country that won't call a nuclear-capable missile strike on a European capital what it is. The Oreshnik missile did not hit India. But for NRIs whose lives span both countries, the shrapnel is diplomatic, economic, and deeply personal.",
        "tags": ["Russia", "Ukraine", "Oreshnik", "missile", "Kyiv", "India", "Modi", "neutral", "oil", "defence", "S-400", "NRI", "diaspora", "geopolitics", "nuclear", "Zelenskyy", "Europe", "NATO", "hypersonic", "Hormuz"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Russia hits Ukraine with Oreshnik missile in one of war's biggest attacks on Kyiv", "url": "https://www.reuters.com/world/europe/ukraines-capital-kyiv-hit-by-massive-missile-drone-attack-2026-05-23/"},
            {"name": "Washington Examiner — Russia attacks Ukraine with nuclear-capable missile for the third time", "url": "https://www.washingtonexaminer.com/news/world/russia-attacks-ukraine-nuclear-capable-missile-third-time"},
            {"name": "CNN — Bomb attack near railway station in southwest Pakistan kills at least 23", "url": "https://www.cnn.com/2026/05/24/asia/quetta-pakistan-train-blast"},
            {"name": "DevDiscourse — Whether it is Ukraine or West Asia, we will continue to support efforts for early end of conflict: PM Modi", "url": "https://www.devdiscourse.com/article/headlines/modi-cyprus-president-ukraine-west-asia-peace"},
            {"name": "Wikipedia — India and the Russo-Ukrainian war (2022–present)", "url": "https://en.wikipedia.org/wiki/India_and_Russo-Ukrainian_war_(2022%E2%80%93present)"}
        ]),
        "score_total": 84,
        "status": "published",
        "published_at": now,
        "body": """On Sunday morning, Russia launched one of the heaviest bombardments of Kyiv since the full-scale invasion began in February 2022. Ninety missiles. Six hundred drones. An hours-long barrage that killed four people, wounded nearly 100, and damaged dozens of residential buildings, schools, government offices, and cultural landmarks in the heart of Ukraine's capital.

Among the weapons was an Oreshnik — Russia's intermediate-range hypersonic ballistic missile, capable of carrying nuclear warheads, with a range of several thousand kilometres. Its warhead split into 36 submunitions, according to analysis of Reuters footage by the Centre for Information Resilience.

It was only the third time Russia has fired an Oreshnik at Ukraine since the war began.

European leaders called it an escalation. The EU's top diplomat, Kaja Kallas, accused Moscow of "reckless nuclear-brinkmanship." Britain and Germany described the use of a nuclear-capable missile as a deliberate provocation. Ukrainian President Volodymyr Zelenskyy called it a "pure propaganda show" at the UN Security Council and urged allies to act.

India said nothing.

## What Russia Destroyed

The scale of Sunday's attack was staggering even by the standards of a four-year war.

Russia's Defence Ministry said it used Oreshnik, Iskander, Kinzhal, and Zircon missiles — a full spectrum of its most advanced ballistic and hypersonic weapons — targeting what it described as Ukrainian military command facilities, air bases, and military-industrial sites.

What actually got hit tells a different story.

Kyiv's national art museum was badly damaged. The city's philharmonic hall was struck. A newly opened museum commemorating the 1986 Chernobyl nuclear disaster — which had celebrated its inauguration just weeks earlier — was destroyed. Zelenskyy visited the ruins personally.

"This is a war against our culture, memory, and identity," said Kyrylo Budanov, Zelenskyy's top aide. "For centuries, Moscow has tried to destroy everything that makes us Ukrainian."

In the Lukyanivka district, north of the city centre, a shopping centre and nearby market were gutted by flames. Dozens of apartment blocks — many already scarred by previous strikes — absorbed fresh damage. Residents who had sought shelter in metro stations overnight emerged to streets covered in glass and rubble.

A cafe that had celebrated its grand opening on Saturday was serving customers on Sunday morning as staff swept debris from the floor.

"Once the emotions die down a bit, we'll think about whether to restore everything … or whether to work at all," said Yevhenii Prusak, the cafe's co-owner.

## Why the Oreshnik Matters

The Oreshnik is not just another missile. It is an intermediate-range ballistic missile — a category of weapon that was banned under the now-defunct INF Treaty between the US and Russia from 1987 to 2019. It can carry conventional or nuclear warheads. It travels at hypersonic speeds. It is, by design, a strategic weapon — the kind of thing that exists to signal the possibility of nuclear war.

Russia first used the Oreshnik against Ukraine in November 2024, striking Dnipro. The second strike hit another major city. Sunday's attack brought it within 40 miles of Kyiv itself.

Moscow said the attack was retaliation for Ukrainian strikes on civilian targets in Russia — a claim Ukraine denies. Russia's consistent position is that it does not target civilians, despite thousands of documented civilian deaths from its bombardments of Ukrainian cities over four years.

The use of a nuclear-capable weapon in a conventional conflict — and the steady reduction in distance between Oreshnik strikes and the Ukrainian capital — represents exactly the kind of escalation that nuclear deterrence theory was supposed to prevent.

## India's Silence — and Its Logic

Two days before Russia fired the Oreshnik, Prime Minister Narendra Modi stood alongside Cyprus President Nikos Christodoulides in New Delhi and reaffirmed India's commitment to supporting "all diplomatic efforts for an early resolution to ongoing conflicts in Ukraine and West Asia."

It was the kind of statement India has issued dozens of times since February 2022 — carefully balanced, conspicuously non-specific, and deliberately free of any language that could be read as criticism of Moscow.

This is not an accident. It is a strategy — and it has logic.

India imports approximately 40 percent of its crude oil from Russia, a figure that has surged since 2022 when Western sanctions made Russian crude available at significant discounts. With the Iran war pushing global oil prices above $100 per barrel, Indian refiners have become some of Russia's most important customers. In 2025-26, India purchased an estimated $46 billion worth of Russian crude — a lifeline for both the Indian economy and Russia's war-funding capacity.

India's defence relationship with Russia runs even deeper. The Indian military operates Russian-made S-400 air defence systems, MiG-29 and Su-30MKI fighter jets, T-90 tanks, Kilo-class submarines, and leased nuclear submarines. Decades of procurement decisions have created dependencies that cannot be unwound in a single budget cycle.

And at the United Nations Security Council, Russia's veto power has historically shielded India on Kashmir-related resolutions — a diplomatic debt that New Delhi factors into every vote it casts.

The result is a foreign policy that Western capitals find frustrating and Indian diplomats consider pragmatic: India talks to everyone, condemns no one by name, and quietly ensures its own energy and security interests are protected regardless of who is firing what at whom.

## The Diaspora's Impossible Position

For the 4.4 million Indian Americans living in the United States, India's Russia policy is not an abstract debate in international relations journals. It is a conversation that happens at work, at dinner parties, and in newsrooms.

When Russia invaded Ukraine in 2022, Indian Americans found themselves explaining their home country's abstention at the UN to American colleagues who could not understand how "the world's largest democracy" could sit out the defining geopolitical crisis of the decade. Four years later, the explanations have not gotten easier.

The tension is structural. Indian Americans have built their professional and community lives in a country — the United States — that views Russia as an adversary and has spent tens of billions of dollars arming Ukraine. They simultaneously maintain deep ties to a country — India — that views Russia as a strategic partner and has spent tens of billions of dollars buying Russian oil and weapons.

Every time India abstains from a UN vote, every time the External Affairs Ministry declines to name Russia in a statement, every time India is photographed buying discounted crude while European cities burn, the diaspora absorbs the reputational cost.

This matters in concrete ways. When the US Congress debates expanding H-1B visa allocations, India's foreign policy alignment is a factor — not always explicitly, but always present. When trade negotiators in Washington discuss the $500 billion bilateral trade target that Secretary of State Marco Rubio outlined in New Delhi last week, the question of India's reliability as a strategic partner includes its posture on Russia. When technology transfer agreements are evaluated, India's defence relationship with Moscow is scrutinised.

The Oreshnik missile was fired at Kyiv. But for NRIs whose personal and professional identities span both countries, the fallout travels further than any warhead.

## What Happens Next

The immediate geopolitical question is whether Sunday's attack derails the tentative momentum on the Iran deal — which, if finalised, would reopen the Strait of Hormuz and reduce the very energy price pressures that make Russian oil so essential to India.

If the Iran deal goes through and global oil prices fall, India's incentive to buy discounted Russian crude diminishes — and with it, one of the strongest arguments for maintaining neutrality. If the deal collapses and energy prices spike further, India's dependence on Russian oil deepens — and the balancing act becomes even more precarious.

Meanwhile, Modi is set to meet Trump face-to-face at the G7 summit in Évian, France, from June 15 to 17 — their first direct engagement in over 16 months. Russia's escalation in Ukraine will be one of many topics on the table. How India navigates that conversation — and whether it moves even slightly from its studied neutrality — will be watched closely by every capital in the world.

Including Washington. And including the millions of Indian Americans who live there."""
    })
    print(f"Article 1 prepared: {slug1}")
else:
    print(f"SKIP Article 1 — slug exists: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Modi-Trump G7 Évian — First Face-to-Face in 16 Months
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("modi-trump-g7-evian-france-meeting-trade-deal-500-billion-nri")
if slug2 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Modi and Trump Haven't Met in Over a Year. That Changes in Three Weeks at the G7 in France. The $500 Billion Trade Deal, the Iran War, and 4.4 Million Indian Americans Are All on the Table.",
        "subheadline": "French President Emmanuel Macron has invited India to the 52nd G7 summit in Évian-les-Bains from June 15 to 17, 2026 — and for the first time since Canada's G7 in 2025, Narendra Modi and Donald Trump will be in the same room. The last time they were supposed to meet, Trump left the summit before bilateral talks could happen. This time, the agenda is different. Rubio just visited New Delhi. A $500 billion trade target has been set. The Iran war is reshaping energy markets. And the largest single-country group waiting for US green cards — Indians — needs answers that only a Modi-Trump handshake can begin to provide.",
        "slug": slug2,
        "category": "news",
        "vertical": "diplomacy",
        "diaspora_angle": "For the 4.4 million Indian Americans — and the roughly 1 million Indians currently in the US immigration queue — the Modi-Trump meeting at Évian is not a photo op. It is a policy event with direct consequences. Three issues on the G7 agenda map directly onto diaspora life. First: the $500 billion bilateral trade target. If Modi and Trump make progress on tariff reductions, market access, and defence procurement, it strengthens the economic case for the US to streamline visa and immigration pathways for Indian workers — the logic being that deeper economic integration requires freer movement of talent. Second: the Iran deal. If a ceasefire holds and the Strait of Hormuz reopens, global oil prices drop, inflation eases, and the Federal Reserve's rate calculus shifts — which directly affects NRI remittances (weaker dollar = fewer rupees per dollar sent home, but lower inflation improves purchasing power), mortgage rates for Indian Americans buying homes, and the broader economic environment in which visa sponsorship decisions are made. Third: immigration itself. Rubio's New Delhi meetings explicitly discussed 'visa-related challenges faced by Indian workers.' India has the longest green card backlog in the world — some employment-based applicants face wait times exceeding 100 years under current quotas. Whether Modi raises this directly with Trump, and whether Trump's response signals any movement on country caps or backlog reform, will be parsed word by word by every Indian American immigration lawyer in the country. The G7 is a club of wealthy democracies. India is not a member. But every time Modi is invited to the table, it reinforces India's claim to a permanent seat — and every NRI's claim that their home country belongs in the conversation.",
        "tags": ["Modi", "Trump", "G7", "Evian", "France", "Macron", "trade", "500 billion", "Iran", "Hormuz", "visa", "H-1B", "green card", "immigration", "NRI", "diaspora", "Rubio", "Jaishankar", "diplomacy", "India-US"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Mera Bharat Samachar — Modi-Trump Meeting Scheduled Next Month? Macron's G7 Invite Fuels Buzz", "url": "https://merabharatsamachar.com/2026/05/20/modi-trump-meeting-scheduled-next-month-macrons-g7-invite-fuels-buzz-over-high-stakes-talks/"},
            {"name": "Wikipedia — 52nd G7 summit", "url": "https://en.wikipedia.org/wiki/52nd_G7_summit"},
            {"name": "Top Indian News — PM Modi-Trump Meeting Likely in France During G7 Summit", "url": "https://topindiannews.com/pm-modi-trump-meeting-likely-france-g7-2026/"},
            {"name": "Reuters — India, US discuss Middle East, trade as Rubio cites progress on Iran conflict", "url": "https://www.reuters.com/world/india-us-discuss-middle-east-trade-rubio-cites-progress-iran/"},
            {"name": "GenReaders — Modi Trump G7 Meeting: Will the $500B Trade Deal Finally Pass?", "url": "https://genreaders.com/modi-trump-g7-meeting-500b-trade-deal/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "body": """In three weeks, Narendra Modi will fly to France for the 52nd G7 summit in Évian-les-Bains — the elegant spa town on the shores of Lake Geneva where, in 2003, Jacques Chirac hosted a summit that coincidentally also took place against the backdrop of a war that divided the Western alliance.

This time, the war is in Iran. The division is less about whether to fight and more about how to stop. And for India, the summit offers something that has been missing for over 16 months: a face-to-face meeting between Modi and Donald Trump.

French President Emmanuel Macron extended the invitation to India as a "key Global South partner" — a diplomatic designation that reflects both India's growing economic weight and France's strategy of keeping New Delhi close as a counterbalance to Beijing. The summit runs from June 15 to 17. Modi's attendance has been confirmed. Trump's has been assumed.

The last time both leaders were at the same summit — the G7 in Canada in 2025 — Trump left before bilateral discussions could take place. India reportedly declined a subsequent invitation to visit Washington on Modi's return journey, partly because of scheduling conflicts with a planned trip to Croatia and partly because of concerns about the optics of an interaction that might have involved Pakistan's army chief.

Sixteen months of no direct engagement between the leaders of the world's two largest democracies is a long time. In that period, a war with Iran began, the Strait of Hormuz was blockaded, oil prices surged past $100, the rupee fell to 97 against the dollar, H-1B registrations dropped 38.5 percent, and Secretary of State Marco Rubio flew to New Delhi to set a $500 billion bilateral trade target.

Everything is on the table at Évian. Possibly for the first time.

## The Rubio Prelude

The timing of the G7 meeting is not coincidental. It comes less than a month after Rubio's visit to India on May 22-23, during which he met Foreign Minister S. Jaishankar and described the India-US partnership as "one of the most important in the world."

The Rubio visit produced several concrete signals. The two sides discussed efforts to conclude a bilateral trade deal. They addressed visa-related challenges faced by Indian workers — a reference that immigration lawyers across America immediately parsed for subtext. Rubio reiterated that Iran could never be allowed to have a nuclear weapon. And he extended a White House invitation from Trump to Modi — an invitation that the G7 meeting in France may now render moot, since the two leaders can meet on neutral territory without either side having to absorb the domestic political cost of a formal state visit.

Jaishankar, who visited France separately to meet French Foreign Minister Jean-Noël Barrot, reportedly used the meeting to align positions on the G7 agenda and discuss India's contributions to international security and economic stability. The diplomatic groundwork, in other words, has been laid.

What remains is the conversation between the two principals.

## The $500 Billion Question

The headline number — a $500 billion bilateral trade target — has been circulating since Rubio's India visit. It is ambitious. Current bilateral trade between the US and India stands at roughly $200 billion annually. To reach $500 billion requires not just growth but structural changes: tariff reductions, market access in agriculture and dairy, defence procurement deals, technology transfers, and the kind of regulatory harmonisation that neither bureaucracy is particularly good at.

The strategic logic is clearer than the implementation path. Both countries want to reduce dependence on Chinese supply chains. India has positioned itself as a manufacturing alternative — Apple now assembles more than a quarter of its iPhones in India. The US has signalled willingness to treat India as a preferred partner in sectors like semiconductors, defence, and clean energy.

But the details are contentious. India's tariffs on American agricultural products remain among the highest in the world. The US wants India to open its dairy market — a political impossibility in a country where the cow is sacred to the ruling party's base. Defence procurement involves not just purchases but technology transfer and co-production agreements that the Pentagon has historically been reluctant to grant.

Rubio's visit set the target. The G7 meeting is where Modi and Trump determine whether it is a target or a talking point.

## The Iran Variable

Every economic calculation between the US and India now passes through the Strait of Hormuz.

The Iran war — which began in February 2026 after US and Israeli strikes on Iranian nuclear facilities — has blockaded the strait, disrupted one-fifth of global oil shipments, and pushed crude prices above $100 per barrel. India, which imports roughly 85 percent of its oil, has been among the hardest-hit economies.

As of this weekend, the outlines of a deal are emerging. A 60-day ceasefire extension would reopen Hormuz toll-free. Iran would agree to clear the mines it deployed. The US would lift its naval blockade and issue some sanctions waivers. Iran has given verbal commitments on suspending uranium enrichment and disposing of its highly enriched stockpile — though nothing has been signed, and Trump said on Sunday that he would not rush into any agreement.

For India, the Iran deal is existential economics. If the strait reopens and oil prices fall, the rupee stabilises, inflation eases, and the fiscal pressure that has forced India to buy discounted Russian crude — at significant diplomatic cost — begins to lift.

If the deal collapses, India's energy crisis deepens. The rupee continues its slide. And the economic argument for the $500 billion trade target becomes harder to make.

Modi will arrive in Évian knowing which scenario has played out — and that will shape every conversation he has with Trump.

## The Immigration Subtext

For the roughly one million Indians currently in the US immigration queue — including hundreds of thousands in the employment-based green card backlog with wait times that can exceed a century under current per-country caps — the Modi-Trump meeting carries a specific, personal weight.

Immigration was explicitly on the agenda during Rubio's New Delhi visit. The discussion of "visa-related challenges faced by Indian workers" is diplomatic language for a problem that Indian Americans know intimately: the H-1B visa system is narrowing (registrations dropped 38.5 percent this year), the green card backlog is growing, and the consular processing system has been thrown into chaos by the Trump administration's directive that green card applicants leave the US and apply from their home countries.

Whether Modi raises immigration directly with Trump at the G7 — and whether Trump's response signals any willingness to reform country caps, expand visa allocations, or reverse the consular processing directive — will be watched with extraordinary attention by the Indian American community.

The precedent is mixed. Modi has historically avoided publicly pressing the US on immigration, preferring to frame the issue as part of broader people-to-people ties. Trump, for his part, has shown a willingness to use immigration policy as leverage in trade negotiations — tightening restrictions to gain concessions elsewhere.

The G7 is not the venue for detailed immigration legislation. But a signal — even a vague one — from the Modi-Trump meeting could shift the political dynamics in Washington that determine whether the backlog ever gets addressed.

## What Évian Means

The G7 is a club of seven wealthy democracies: the US, UK, France, Germany, Italy, Japan, and Canada. India is not a member. It does not get a vote. It is a guest — invited at the discretion of the host country, present at the sufferance of the members.

And yet India's invitation to every recent G7 summit reflects a reality that the formal membership structure has not caught up with. India is the world's fifth-largest economy. It is the most populous country on Earth. It is the largest democracy. It is the swing vote on virtually every major geopolitical question — from climate change to the Russia-Ukraine war to the Iran deal to the restructuring of global supply chains.

Macron's decision to invite India as a "key Global South partner" is not just diplomatic courtesy. It is an acknowledgement that the G7 cannot address any of its stated priorities — reducing economic imbalances, climate security, technology governance — without India in the room.

For the 4.4 million Indian Americans who live at the intersection of both countries' interests, the Évian summit is the most consequential diplomatic event of the year. It will determine the trajectory of trade, the posture on immigration, the alignment on Iran, the relationship with Russia, and the broader question of where India sits in the global order.

Three weeks. One meeting. Everything at stake.

The last time Modi and Trump were supposed to talk, Trump left early. This time, neither leader can afford to."""
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
