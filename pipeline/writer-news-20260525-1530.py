#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-25 15:30 PDT batch
Topics: 1) Netanyahu escalates Hezbollah strikes in Lebanon even as US-Iran deal nears — India's workers, peacekeepers, and multi-alignment tested
        2) Memorial Day 2026 — Trump honors 13 killed in Iran war at Arlington while UFC octagon goes up on the White House lawn
"""

import json, os, uuid, re, requests, subprocess
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

def make_slug(slug_base, date_suffix="20260525"):
    slug = slug_base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

# ── Duplicate check ──
existing = sb_get("p2_articles", {
    "select": "headline,slug",
    "status": "eq.published",
    "published_at": "gte.2026-05-23T00:00:00Z",
    "order": "published_at.desc",
    "limit": "80"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc)
now_iso = now.isoformat().replace('+00:00', 'Z')
now_plus1 = (now + timedelta(minutes=1)).isoformat().replace('+00:00', 'Z')

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Netanyahu Escalates Hezbollah Strikes in Lebanon
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("netanyahu-hezbollah-lebanon-escalation-india-unifil-workers-iran-deal")
headline1_prefix = "netanyahu"
if slug1 not in existing_slugs and not any(headline1_prefix in h for h in existing_headlines_lower):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Netanyahu Just Promised to 'Intensify' Strikes on Hezbollah in Lebanon. India Has Peacekeepers on the Ground, Thousands of Workers in the Country, and an Iran Deal It Desperately Needs — and the Escalation Threatens All Three.",
        "subheadline": "On Monday night, Israeli Prime Minister Benjamin Netanyahu released a video on Telegram declaring 'We are at war with Hezbollah, and we will intensify our strikes.' Hours earlier, he told President Trump in a phone call that Israel would retain the right to confront perceived threats on 'all fronts, including Lebanon.' The Israeli military launched strikes on more than 70 Hezbollah targets across Lebanon — command centers, weapons depots, logistics routes. Right-wing Israeli ministers demanded that '10 buildings should fall in Beirut for every drone.' India has an 814-strong UNIFIL contingent stationed in southern Lebanon, directly in the zone of operations. An estimated 15,000-20,000 Indian workers remain in Lebanon. And the fragile US-Iran peace deal that India needs to reopen the Strait of Hormuz — the deal that would bring down oil prices, stabilize the rupee, and end the fuel hike spiral — depends on a broader de-escalation that Netanyahu is now actively undermining. For the second time in a year, India's multi-alignment doctrine is being tested by events it cannot control.",
        "slug": slug1,
        "category": "news",
        "vertical": "diplomacy",
        "diaspora_angle": "For NRIs in America, Netanyahu's Lebanon escalation is not a distant Middle Eastern conflict. It is a direct threat to the Iran deal that India needs to stabilize its economy — the same economy that determines the value of every dollar you send home. The rupee just hit ₹97 to the dollar. Fuel prices have been raised four times in ten days. Oil is above $90 a barrel because the Strait of Hormuz remains restricted. The Iran deal was supposed to fix all of this. Netanyahu is now saying, in effect, that Israel's war with Hezbollah will continue regardless of what Washington and Tehran agree to — which means the broader regional de-escalation that India's economy depends on may not materialize even if Trump signs a deal with Iran. For Indian families with relatives working in Lebanon — construction workers, domestic staff, hospitality employees — the escalation is more immediate. India's Embassy in Beirut has periodically issued advisories, but a full-scale Israeli assault on Hezbollah in eastern Lebanon and potentially Beirut would trigger an evacuation scenario similar to the 2006 Lebanon war, when India evacuated over 2,200 nationals. And for the Indian diaspora watching the Quad meeting tomorrow in New Delhi, the question is whether India's strategic partnership with the United States gives it any leverage to influence Washington's approach to Netanyahu's escalation — or whether multi-alignment means watching from the sidelines while the Middle East burns and the rupee falls.",
        "tags": ["Netanyahu", "Hezbollah", "Lebanon", "Israel", "India", "UNIFIL", "peacekeepers", "Iran deal", "Hormuz", "Strait of Hormuz", "oil prices", "Bekaa Valley", "Smotrich", "Trump", "Quad", "NRI", "evacuation", "multi-alignment"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Israel will escalate strikes against Hezbollah in Lebanon, Netanyahu says", "url": "https://www.reuters.com/world/middle-east/israel-will-escalate-strikes-against-hezbollah-lebanon-netanyahu-says-2026-05-25/"},
            {"name": "Reuters — Israeli right-wing ministers urge Netanyahu to resume Beirut strikes to counter Hezbollah drone attacks", "url": "https://www.reuters.com/world/middle-east/israeli-right-wing-ministers-urge-netanyahu-resume-beirut-strikes-2026-05-25/"},
            {"name": "The Oceania Cables — Israel Launches Strikes on Over 70 Hezbollah Targets Across Lebanon", "url": "https://theoceaniacables.com/israel-launches-strikes-on-over-70-hezbollah-targets-across-lebanon/"},
            {"name": "USA Today — Pressure mounts as US and Iran resume peace talks", "url": "https://www.usatoday.com/story/news/world/2026/05/25/iran-war-live-updates/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now_iso,
        "body": """On Monday night, Israeli Prime Minister Benjamin Netanyahu released a video on Telegram with a message that was five words long and unmistakable: "We are at war with Hezbollah, and we will intensify our strikes."

Hours earlier, Netanyahu had spoken with President Donald Trump by phone. The Israeli leader emerged from the call saying the two had agreed that Israel would retain the right to confront perceived threats on "all fronts, including Lebanon." The Israeli military then launched strikes on more than 70 Hezbollah targets across Lebanon — command centers, weapons depots, logistics routes in the Bekaa Valley and eastern Lebanon.

Inside Netanyahu's coalition, the pressure was even more explicit. Finance Minister Bezalel Smotrich, a far-right settler advocate, demanded that "10 buildings should fall in Beirut for every drone" after Hezbollah FPV drones killed an Israeli soldier in southern Lebanon. The right-wing coalition partners are pushing Netanyahu toward a full-scale assault on Beirut itself — the kind of urban bombing campaign that would trigger a humanitarian catastrophe and make any US-Iran deal politically impossible.

The escalation arrived on the same day that Trump stood at Arlington National Cemetery honoring 13 American service members killed in the Iran war, and on the eve of the Quad Foreign Ministers' Meeting in New Delhi — a meeting where India had hoped to project strategic confidence and regional stability.

## India's Three Vulnerabilities

India's exposure to the Lebanon escalation operates on three distinct levels, each with its own timeline and consequences.

**First, the peacekeepers.** India maintains an 814-strong contingent in the United Nations Interim Force in Lebanon (UNIFIL), deployed in the border zone between Israel and Lebanon that is now the active theater of Israeli military operations. UNIFIL has been operating under increasingly dangerous conditions since the broader Iran conflict began. The UN confirmed that its peacekeepers "remain in all positions" despite Israeli requests to relocate — a diplomatic formulation that translates to: India's soldiers are in the line of fire and are not leaving.

India's UNIFIL contribution is one of its oldest and most significant peacekeeping deployments, dating back decades. Indian peacekeepers have been wounded and killed in previous rounds of Israel-Hezbollah violence. If Netanyahu's escalation intensifies into the kind of ground operation that right-wing ministers are demanding, India's UNIFIL contingent will be directly at risk — and New Delhi will face the agonizing choice between maintaining its peacekeeping commitment and protecting its soldiers from a conflict in which it has no direct stake.

**Second, the workers.** An estimated 15,000 to 20,000 Indian nationals live and work in Lebanon — construction workers, domestic staff, hospitality employees, small business operators, and professionals. Many are concentrated in Beirut and the southern suburbs, the areas most vulnerable to an expanded Israeli bombing campaign.

India evacuated over 2,200 nationals from Lebanon during the 2006 war, using the Indian Navy and chartered flights in an operation that took weeks and required coordination with multiple governments. A similar evacuation today would be complicated by the broader regional war, restricted airspace, and the fact that Beirut's airport could be targeted or closed.

The Indian Embassy in Beirut has periodically issued travel advisories, but the escalation from targeted strikes on Hezbollah positions in the Bekaa Valley to the kind of urban warfare that Smotrich is demanding would transform the risk from manageable to acute overnight.

**Third, and most consequentially for 1.4 billion Indians: the Iran deal.**

## The Deal That India Needs

The fragile US-Iran peace process — the deal that Trump says is "largely negotiated," the deal that Iran says is a 14-point memorandum of understanding, the deal that would reopen the Strait of Hormuz and bring oil prices down from above $90 a barrel — depends on a broader regional de-escalation that Netanyahu is now actively undermining.

The logic is straightforward. Iran's negotiating position has always been that any deal must address not just its nuclear program but also the broader conflict — including Israeli attacks on Iranian allies. Hezbollah is Iran's most significant regional proxy. An Israeli escalation against Hezbollah, conducted with what Netanyahu claims is American acquiescence, gives Iran's hardliners the argument they need to reject any deal: why agree to disarm when your ally is being bombed with American-supplied weapons?

For India, this is not abstract diplomacy. The Strait of Hormuz closure has been the single most disruptive event for India's economy in 2026. Oil prices have pushed fuel costs to four hikes in ten days. The rupee has fallen to ₹97 to the dollar. Inflation is rising. The Reserve Bank of India has signaled it will do "whatever is required" to maintain currency stability — language that suggests intervention, rate hikes, or both.

The Iran deal was supposed to fix this. If Hormuz reopens, oil prices fall. If oil prices fall, fuel prices stabilize. If fuel prices stabilize, inflation eases. If inflation eases, the RBI can hold rates, the rupee steadies, and the economy can resume the growth trajectory that attracted $83 billion in foreign investment last year.

Netanyahu's escalation puts all of this at risk. Not because Israel's actions directly affect Hormuz — they don't — but because the escalation undermines the political conditions under which Iran's leadership can justify signing a deal. If Iran's supreme leader believes that the United States is simultaneously negotiating a peace deal and greenlighting Israeli attacks on Iran's closest ally, the deal collapses. And if the deal collapses, Hormuz stays restricted, oil stays expensive, and India's economy continues to bleed.

## The Multi-Alignment Test

India's foreign policy establishment has spent years building what External Affairs Minister Jaishankar calls a "multi-alignment" approach — maintaining strong relationships with the United States, Israel, Iran, and the Gulf states simultaneously, refusing to choose sides, and leveraging each relationship for specific benefits.

The Lebanon escalation tests this approach to its breaking point.

India has a defense relationship with Israel worth billions. It purchases Israeli weapons systems, surveillance technology, and missile defense components. It conducts joint military exercises. It has deepened intelligence cooperation. India does not criticize Israeli military operations publicly and has consistently abstained on UN votes critical of Israel.

Simultaneously, India needs Iran to agree to a deal that reopens Hormuz. India imports a significant portion of its crude through the strait. India has invested in Iran's Chabahar port as an alternative trade route to Central Asia. India has maintained diplomatic channels with Tehran even during the current war.

These two relationships are now in direct conflict. Netanyahu's escalation against Hezbollah makes an Iran deal harder. India's interest is in de-escalation — in a deal that brings stability to the region and brings oil prices down. Israel's interest, or at least Netanyahu's political interest, is in continued military pressure on Iran's proxies regardless of the diplomatic consequences.

India cannot publicly criticize Israel without jeopardizing a defense relationship it values. It cannot publicly support Netanyahu's escalation without alienating Iran at the moment India needs Iran to sign a deal. And it cannot do nothing, because the economic consequences of inaction — continued high oil prices, a weakening rupee, mounting inflation — are borne by 1.4 billion Indians.

## Tomorrow's Quad Meeting

The timing is particularly uncomfortable for the Quad Foreign Ministers' Meeting in New Delhi on Tuesday. The Quad — the United States, India, Japan, and Australia — was designed to address Indo-Pacific security, not Middle Eastern conflicts. But the Iran war and the Lebanon escalation have become impossible to ignore at any multilateral forum.

Jaishankar will sit across from Marco Rubio — the same Marco Rubio who, on Saturday in New Delhi, said that the India-US partnership is "one of the most important in the world." Rubio will also be carrying the weight of the Trump administration's position on Netanyahu's escalation — a position that, based on Monday's phone call, appears to be tacit approval.

India's challenge at the Quad will be to maintain the appearance of a strategic partnership with the United States while privately pressing Washington to restrain Netanyahu in the interest of the Iran deal that both India and the US ostensibly want. Whether Rubio has the political capital to deliver that message to Netanyahu — or whether the Trump administration even wants to — is the question that will determine whether India's multi-alignment survives this test.

## The View From the Diaspora

For the Indian diaspora in the United States, the Lebanon escalation is a reminder that the conflicts shaping their daily lives — gas prices at $4.56 a gallon, the rupee's decline reducing the value of remittances, uncertainty about H-1B visas in a wartime economy — are connected to decisions made in Tel Aviv, Tehran, and Washington in ways that no multi-alignment doctrine can fully insulate against.

Indian Americans have limited political influence over US policy toward Israel and Lebanon. But they are among the Americans most affected by the economic consequences of the broader Iran war — both as US consumers paying higher gas prices and as NRIs watching the Indian economy absorb the shock of restricted oil supplies.

If Netanyahu's escalation prevents an Iran deal, the consequences will be measured in rupees and dollars, in fuel prices and flight costs, in remittance values and retirement plans. The war in Lebanon is 7,000 kilometers from New Delhi. Its effects will be felt in every household in India and every Indian household in America.

## What Happens Next

The next 72 hours will be critical. The Quad meeting on Tuesday will test whether the United States is willing to push back on Netanyahu's escalation. The Iran negotiations in Doha will test whether Iran's leadership can sustain a diplomatic track while Hezbollah is being bombed. And Netanyahu's coalition will test whether right-wing ministers can push the prime minister toward the full-scale Beirut assault they are demanding.

India will watch from New Delhi, from Beirut where its workers live, from southern Lebanon where its peacekeepers stand, and from the foreign exchange desks where the rupee trades. Multi-alignment has served India well for two decades. The question is whether a doctrine built for peace can survive a region at war."""
    })
    print(f"✅ Article 1 queued: {slug1}")
else:
    print(f"⏭️  Article 1 skipped (duplicate): {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Memorial Day 2026 — Trump at Arlington, 13 Dead in Iran War, UFC on the White House Lawn
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("memorial-day-2026-trump-arlington-13-dead-iran-war-ufc-white-house")
headline2_prefix = "memorial day"
if slug2 not in existing_slugs and not any(headline2_prefix in h for h in existing_headlines_lower):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "It Is Memorial Day. Thirteen American Service Members Have Died in the Iran War. Trump Honored Them at Arlington. A Bereaved Family Sat in the Audience. And on the White House South Lawn, Workers Are Building a UFC Octagon for a Fight Card on Trump's 80th Birthday.",
        "subheadline": "On Monday morning, President Donald Trump laid a wreath at the Tomb of the Unknown Soldier at Arlington National Cemetery and stood before rows of white headstones to honor the thirteen United States service members killed since the Iran war began eighty-seven days ago. 'These incredible men and women gave their lives to ensure that the world's number one state sponsor of terror will never have a nuclear weapon,' he said. At least one bereaved family was in the audience. Flags across the country flew at half-staff — including for Staff Sergeant Benjamin N. Pennington, 26, assigned to Fort Carson, who died March 8 from injuries sustained in an attack at Prince Sultan Air Base in Saudi Arabia. Hours later, photographs emerged of a temporary UFC octagon being constructed on the White House South Lawn for 'Freedom 250,' a star-studded fight card scheduled for June 14 — which is both Flag Day and Trump's 80th birthday. Grammy-winning country singer Gretchen Wilson will perform. For the Indian American community, Memorial Day carries a particular weight this year: the war that killed these thirteen Americans is the same war that closed the Strait of Hormuz, sent oil prices above $90, pushed gas to $4.56 a gallon, weakened the rupee to ₹97, and triggered four fuel price hikes in India in ten days. The human cost and the economic cost are the same war.",
        "slug": slug2,
        "category": "news",
        "vertical": "politics",
        "diaspora_angle": "Memorial Day is the most American of holidays — a day that asks you to remember the cost of the country you chose. For the 4.4 million Indian Americans who live in the United States, the holiday has always carried a specific weight. Some have family members who serve. Some arrived as immigrants and became citizens and buried their parents in a country they never planned to stay in. Some are on H-1B visas and cannot vote but pay taxes that fund the military and the wars it fights. This Memorial Day, the Iran war makes the connection between the diaspora and the military unavoidable. The 13 service members who died — at Prince Sultan Air Base, at Al Udeid, in the waters of the Persian Gulf — died in a war that has directly shaped the economic reality of every Indian American family. The Strait of Hormuz closure sent oil prices above $90 a barrel. Gas prices hit $4.56 a gallon, the highest Memorial Day price in American history. The rupee fell to ₹97 because India imports 85 percent of its crude through routes affected by the conflict. Every dollar sent home is worth less. Every flight to India costs more. Every family member calling from Delhi or Mumbai is complaining about fuel prices that have been hiked four times in ten days. The war is not abstract. The 13 dead are not statistics. And the UFC octagon going up on the White House lawn — where a fight card will celebrate both Flag Day and the president's birthday — is a reminder that in America, solemnity and spectacle are never more than a few hundred yards apart.",
        "tags": ["Memorial Day", "Trump", "Arlington", "Iran war", "service members", "Benjamin Pennington", "Fort Carson", "Prince Sultan Air Base", "UFC", "Freedom 250", "White House", "Gretchen Wilson", "Indian Americans", "diaspora", "oil prices", "Hormuz", "NRI"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "USA Today — Trump honors soldiers killed in Iran war, lays wreath on Memorial Day", "url": "https://www.usatoday.com/story/news/politics/2026/05/25/trump-memorial-day-arlington-iran-war/"},
            {"name": "New York Post — Trump vows Iran will never have nukes while mourning 13 servicemembers", "url": "https://nypost.com/2026/05/25/us-news/trump-vows-iran-will-never-have-nukes-while-mourning-13-servicemembers/"},
            {"name": "Washington Examiner — Freedom 250 hosts candlelight tribute on Memorial Day", "url": "https://www.washingtonexaminer.com/news/white-house/freedom-250-candlelight-tribute-memorial-day/"},
            {"name": "Coloradoan — Why flags are half-staff on May 25", "url": "https://www.coloradoan.com/story/news/2026/05/25/why-flags-half-staff-today/"}
        ]),
        "score_total": 83,
        "status": "published",
        "published_at": now_plus1,
        "body": """On Monday morning at Arlington National Cemetery, President Donald Trump walked past rows of white marble headstones in the warm Virginia sun and laid a wreath at the Tomb of the Unknown Soldier. It is a ceremony that every president performs. The wreath is always the same. The walk is always the same. The silence of the crowd is always the same.

What was not the same was the war.

For the first time since the Afghanistan withdrawal in 2021, an American president stood at Arlington with an active military conflict producing American casualties. Thirteen United States service members have been killed in the eighty-seven days since the Iran war began — in missile attacks, in base incursions, in naval engagements in the Persian Gulf.

"These incredible men and women gave their lives to ensure that the world's number one state sponsor of terror will never have a nuclear weapon," Trump told the audience, which included at least one bereaved military family.

## The Thirteen

The names of the dead have appeared in local newspapers, on military base announcements, in hometown memorial services across the country. They have not, until now, been the subject of a presidential ceremony.

Staff Sergeant Benjamin N. Pennington, 26, was assigned to Fort Carson, Colorado. He died on March 8 from injuries sustained in an attack at Prince Sultan Air Base in Saudi Arabia. His death was announced weeks later. Flags were lowered to half-staff from sunrise on March 20 to sunset on March 21.

The other twelve include service members killed at Al Udeid Air Base in Qatar, in naval operations in the Persian Gulf, and in the initial military exchanges that followed the broader US-Israeli strikes on Iranian nuclear facilities. Their ranks range from enlisted to officer. Their ages range from early twenties to late thirties. They come from at least eight states.

The Pentagon has not released a comprehensive list of casualties with full details, citing operational security. But the number — thirteen — has become a symbolic marker. It is the same number of service members killed in the Kabul airport bombing during the Afghanistan withdrawal in August 2021, an event that became a defining political moment for the Biden administration.

Trump, who campaigned against what he called Biden's "disastrous" withdrawal from Afghanistan, now carries his own number. Thirteen.

## The Octagon

Several hundred yards from Arlington National Cemetery, across the Potomac River on the White House South Lawn, workers on Monday were assembling a different structure: a temporary UFC octagon.

"Freedom 250" is a star-studded Ultimate Fighting Championship event scheduled for June 14 — which is both Flag Day and President Trump's 80th birthday. The event will be held on the White House grounds, an unprecedented use of the executive mansion for a combat sports event.

Grammy Award-winning country singer Gretchen Wilson is slated to perform. The card is expected to feature top UFC fighters in what the White House describes as a celebration of "American freedom, strength, and competitive spirit."

New photographs released Monday showed the octagon structure taking shape on the lawn where presidents have hosted state dinners, Easter egg rolls, and Fourth of July celebrations. The construction crews worked through Memorial Day.

The juxtaposition — a wreath-laying ceremony for thirteen war dead in the morning, a fight cage going up in the afternoon — generated no official comment from the White House. The two events occupy different symbolic registers: one is solemnity, the other is spectacle. In the Trump administration, both are governance.

## The War and the Economy

For most Americans, the Iran war is experienced not through casualty reports but through prices. Gas at $4.56 a gallon. Flights that cost 30 percent more than last summer. Diesel prices that have pushed up the cost of everything that moves by truck.

The war closed the Strait of Hormuz — the narrow waterway through which 20 percent of the world's oil passes. Iran mined the strait after the US-Israeli strikes on its nuclear facilities. The US Navy is conducting mine-clearing operations. Oil tankers have begun transiting again, but insurance costs have skyrocketed and shipping volumes remain well below pre-war levels.

The economic consequences have been global, but for India and the Indian diaspora, they have been particularly acute.

## What the War Costs India

India imports approximately 85 percent of its crude oil. A significant portion of that oil transits the Strait of Hormuz. When the strait was effectively closed in March, India's oil import costs immediately spiked.

The downstream effects have cascaded through the Indian economy in the twelve weeks since:

**Fuel prices:** India's state-run oil marketing companies raised petrol and diesel prices for the fourth time in ten days on Monday. Petrol crossed ₹102 per litre in Delhi and ₹110 in Bengaluru. The cumulative increase since May 15, when the price freeze ended, has approached ₹7.50 per litre. The opposition called Prime Minister Modi "Inflation Man."

**The rupee:** India's currency fell to ₹97 to the dollar — its worst level in history. The Reserve Bank of India's governor said the central bank would do "whatever is required" to ensure orderly currency movement, a statement that markets interpreted as a signal for intervention and possible rate hikes.

**Inflation:** Rising fuel prices feed directly into transportation costs, which feed into food prices, which feed into the cost-of-living index that determines whether the 800 million Indians who depend on subsidized food grains can afford to eat.

**Remittances:** India received approximately $125 billion in remittances in 2025, making it the world's largest recipient. Those remittances are sent overwhelmingly in dollars. When the rupee weakens, each dollar buys more rupees — which might sound like good news for NRI families sending money home, but the calculation is offset by higher costs on the Indian side. The ₹7.50 fuel hike means the extra rupees buy less.

The war that killed thirteen American service members is the same war that raised fuel prices in Mumbai. The Strait of Hormuz does not distinguish between military casualties and economic casualties.

## Memorial Day in the Diaspora

Memorial Day occupies an unusual space in the Indian American calendar. It is neither Diwali nor Thanksgiving — it is not a holiday that the community has made its own. For most Indian American families, it is a long weekend, a barbecue, a trip to Costco, maybe the start of summer.

But for the estimated 130,000 Indian Americans who have served in the US military — and for the families of those currently serving — Memorial Day is personal. Indian Americans serve in every branch of the military. They deploy to the same bases in the Middle East where the thirteen service members were killed. They operate the same Patriot missile systems, fly the same F-35s, crew the same destroyers.

The community's relationship with military service is complicated. Indian parents who immigrated for economic opportunity often discourage their children from enlisting, preferring medicine, engineering, or law. But Indian Americans who do serve report a deep connection to the country that gave their families a chance — and a desire to earn their place in it through service that cannot be questioned.

This Memorial Day, those who serve are being asked to fight a war that is simultaneously defending American interests and damaging Indian ones. The Strait of Hormuz is being cleared so American and allied shipping can pass. That same clearance benefits India's oil imports. But the war itself is the reason the strait was mined.

## The Arithmetic of Sacrifice

Thirteen dead is a small number by the standards of American wars. In Iraq, 4,431 service members were killed over eight years. In Afghanistan, 2,461 died over twenty years. Thirteen dead in eighty-seven days is a casualty rate that the American public has barely registered.

But Trump's decision to name the number at Arlington — to stand at the Tomb of the Unknown Soldier and say "thirteen" — was a political choice as much as a memorial one. He is framing the war as a sacrifice that has already produced results: "the world's number one state sponsor of terror will never have a nuclear weapon."

Whether that claim is accurate depends on the outcome of negotiations that are still underway. The US says Iran's Supreme Leader has agreed to give up enriched uranium. Iran disputes the characterization. Trump says a deal is "largely negotiated." Iran says Trump's claim is premature. The 14-point memorandum of understanding that both sides have discussed includes a 60-day ceasefire and Hormuz mine-clearing, but no final text has been signed.

If the deal holds, the thirteen dead will be remembered as the cost of ending Iran's nuclear program. If it doesn't, they will be remembered as the beginning of a longer war.

## The Distance Between Arlington and the South Lawn

In the geography of Washington, Arlington National Cemetery and the White House South Lawn are separated by the Potomac River and approximately three miles of road. On Monday, the distance between them felt both shorter and longer than that.

At Arlington, a president laid a wreath for the dead. At the White House, workers built a cage for fighters. One is the oldest American tradition — honoring those who gave everything. The other is the newest — turning the people's house into an arena.

Both are real. Both are this administration. And both are happening in the shadow of a war that has cost thirteen American lives and is costing India billions of dollars and a currency crisis that will take years to unwind.

For the Indian diaspora, sitting in living rooms in Fremont and Edison and Plano, Memorial Day 2026 is the day the war became personal — not because they knew the thirteen, but because they pay for the war every time they fill a gas tank, every time they check the exchange rate, every time their parents in Delhi complain about the price of cooking gas.

The octagon on the South Lawn will seat thousands for a birthday fight card. Arlington seats no one. The dead do not need chairs. They need only to be remembered, on this day and on the days when the bills come due."""
    })
    print(f"✅ Article 2 queued: {slug2}")
else:
    print(f"⏭️  Article 2 skipped (duplicate): {slug2}")


# ── Insert articles ──
for article in articles:
    try:
        result = sb_post("p2_articles", article)
        print(f"✅ Inserted: {article['slug']} → {article['id']}")
    except Exception as e:
        print(f"❌ Insert failed for {article['slug']}: {e}")

print(f"\n{'='*60}")
print(f"Published {len(articles)} articles")
print(f"{'='*60}")

# ── Source images for articles ──
PEXELS_KEY = ""
pexels_env = Path.home() / "workspace" / ".env.pexels"
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if "pexels" in k.lower():
                PEXELS_KEY = v.strip()

def search_pexels(query, per_page=5):
    if not PEXELS_KEY:
        return []
    r = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": PEXELS_KEY},
        params={"query": query, "per_page": per_page, "orientation": "landscape"},
        timeout=15,
    )
    if r.status_code == 200:
        return r.json().get("photos", [])
    return []

def get_pexels_image_url(query):
    photos = search_pexels(query)
    if photos:
        return photos[0]["src"]["large2x"]
    return None

image_queries = {
    slug1: "military fighter jets middle east conflict aerial",
    slug2: "arlington national cemetery memorial day wreath tombstones",
}

for art in articles:
    slug = art["slug"]
    query = image_queries.get(slug, "")
    if not query:
        continue
    img_url = get_pexels_image_url(query)
    if img_url:
        try:
            sb_patch("p2_articles", {"id": f"eq.{art['id']}"}, {"image_url": img_url})
            print(f"🖼️  Image set for {slug}: {img_url[:80]}...")
        except Exception as e:
            print(f"⚠️  Image PATCH failed for {slug}: {e}")
    else:
        print(f"⚠️  No Pexels image found for {slug}")

# ── Score decay for news articles older than 12h ──
try:
    decay_articles = sb_get("p2_articles", {
        "select": "id,score_total,published_at",
        "status": "eq.published",
        "category": "eq.news",
        "score_total": "gt.40",
        "published_at": "lt." + (now - timedelta(hours=12)).isoformat().replace('+00:00', 'Z'),
        "order": "published_at.desc",
        "limit": "50"
    })
    decayed = 0
    for a in decay_articles:
        age_hours = (now - datetime.fromisoformat(a["published_at"].replace('Z', '+00:00'))).total_seconds() / 3600
        if age_hours > 48:
            decay = 3
        elif age_hours > 24:
            decay = 2
        else:
            decay = 1
        new_score = max(40, a["score_total"] - decay)
        if new_score != a["score_total"]:
            sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": new_score})
            decayed += 1
    print(f"\n📉 Score decay: {decayed} news articles decayed")
except Exception as e:
    print(f"⚠️ Score decay error: {e}")

# ── Git commit & push ──
try:
    repo = Path.home() / "workspace" / "the-videshi-news"
    subprocess.run(["git", "add", "-A"], cwd=repo, capture_output=True, timeout=30)
    msg = f"news: Netanyahu Lebanon escalation + Memorial Day Iran war ({now.strftime('%Y-%m-%d %H:%M UTC')})"
    subprocess.run(["git", "commit", "-m", msg, "--allow-empty"], cwd=repo, capture_output=True, timeout=30)
    push = subprocess.run(["git", "push"], cwd=repo, capture_output=True, timeout=60)
    if push.returncode == 0:
        print("🚀 Git push successful → Vercel deploy triggered")
    else:
        print(f"⚠️ Git push issue: {push.stderr.decode()[:200]}")
except Exception as e:
    print(f"⚠️ Git error: {e}")

print("\n✅ Writer pipeline complete")
