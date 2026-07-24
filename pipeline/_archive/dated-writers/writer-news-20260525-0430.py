#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-25 04:30 UTC batch
Topics: 1) India heatwave — all 50 hottest cities on earth are Indian, 34+ dead, glaciers collapsing
        2) Rupee crashed to ₹97 record low, 4th fuel hike in May, Modi's austerity call — the India-side energy crisis
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
# ARTICLE 1: India Heatwave — All 50 Hottest Cities on Earth Are Indian
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("india-heatwave-50-hottest-cities-earth-47c-vidarbha-telangana-deaths-glaciers-nri")
headline1_prefix = "every single one of the world"
if slug1 not in existing_slugs and not any(headline1_prefix in h for h in existing_headlines_lower):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Every Single One of the World's 50 Hottest Cities Right Now Is in India. Thirty-Four People Have Died This Week From the Heat. The Glaciers That Feed India's Rivers Are Collapsing.",
        "subheadline": "On May 22, air quality tracker AQI.in published the global list of the hottest cities on the planet. All fifty were Indian — not a single city from Africa, the Middle East, or anywhere else made the cut. Vidarbha recorded 47.2°C. Telangana and Andhra Pradesh reported 34 heatstroke deaths in 48 hours. Delhi hit 42.7°C with the IMD warning worse is coming. Meanwhile, a thousand kilometres north, ISRO scientists have confirmed that a 69-million-kilogram ice patch on the Srikanta Glacier collapsed last summer — not from a cloudburst, but from warming temperatures stripping its protective snow cover. The heat killing people on the plains and the ice collapsing in the Himalayas are the same crisis. For the millions of NRIs planning summer trips home, for those whose elderly parents live alone in UP or Telangana, for anyone who sends money to a family that cooks with gas that just got more expensive — this heatwave is not a weather headline. It is the thing happening to the people you love right now.",
        "slug": slug1,
        "category": "news",
        "vertical": "climate",
        "diaspora_angle": "Every NRI with parents or grandparents in India should be making a phone call today. Not next week. Today. The heatwave sweeping India right now is not the familiar summer heat that your relatives dismiss with 'hum toh reh lete hain.' This is 47°C in Vidarbha. This is 34 people dead from heatstroke in Telangana in two days — elderly residents, farmers, daily wage workers, students. This is all 50 of the hottest cities on earth being in one country, your country, at the same time. If you are planning a summer trip to India this year — and millions of NRIs are, despite $1,200-$1,800 flight prices — you need to understand that the India you land in between now and mid-June, before the monsoon arrives, is physically dangerous. Delhi at 42.7°C is not the Delhi of your childhood summers. The urban heat island effect means road surfaces hit 65°C. Power demand has hit record highs and grids are straining. Hospitals are filling with dehydration and heatstroke cases. If your parents are in UP, which accounts for more than half the world's 50 hottest cities right now, or in Telangana, where the state government is paying ₹4 lakh to families of the dead, this is immediate and personal. Call them. Make sure they have working coolers, that they are drinking water, that they are not going out between 11 and 4. The monsoon may arrive early — IMD says May 26 for Kerala — but relief for the north is weeks away.",
        "tags": ["heatwave", "India", "climate", "Vidarbha", "Telangana", "Delhi", "UP", "Himalayas", "glacier", "ISRO", "monsoon", "NRI", "summer", "deaths", "heat dome", "AQI", "IMD"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "IndianYug — Every Single One of the World's 50 Hottest Cities Right Now Is in India", "url": "https://indianyug.com/world-50-hottest-cities-india-heatwave-2026"},
            {"name": "International News and Views — India Heatwave 2026: Vidarbha Records 47.2°C, Telangana Reports 16 Heatstroke Deaths Amid Monsoon Forecast", "url": "https://internationalnewsandviews.com/india-heatwave-2026-vidarbha-47c-telangana-heatstroke-deaths-monsoon-update-403835-2/"},
            {"name": "The Raisina Hills — India Is Burning: The Himalayas Are Paying the Price", "url": "https://theraisinahills.com/india-heatwave-2026-deaths-glaciers-climate-crisis/"},
            {"name": "Reuters — Rupee to extend rally on US-Iran deal hopes (mentions 4th fuel price hike)", "url": "https://www.reuters.com/world/india/rupee-extend-rally-us-iran-deal-hopes-rbi-governors-remarks-aid-sentiment-2026-05-25/"},
            {"name": "News Ei Samay — Delhi scorches at 42.7°C as IMD hints at more intense days ahead", "url": "https://newseisamay.com/delhi-42-7-heat-2026/"}
        ]),
        "score_total": 84,
        "status": "published",
        "published_at": now_iso,
        "body": """On May 22, 2026, air quality tracker AQI.in published the list of the hottest cities on the planet. All fifty were Indian.

Not a single city from the Sahara. Not from the Arabian Peninsula. Not from Central Australia or Death Valley or the deserts of Iran. Every single one of the fifty hottest places on earth, at that moment, was in India.

Uttar Pradesh alone accounted for more than 25 of them. Varanasi, Ayodhya, Banda, Bareilly, Prayagraj — all between 42°C and 43°C. One state, containing more than half of the hottest locations on the planet.

Climate data historian Maximiliano Herrera called it one of the harshest heat events on record globally. He said this in April, before the numbers got worse.

## The Death Toll

In Telangana, at least 34 people have died from heatstroke in the past week, according to state officials. The deaths span more than a dozen districts — Khammam, Karimnagar, Nalgonda, Suryapet, Warangal, and others. The victims include elderly residents, farmers, agricultural labourers, daily wage workers, and students.

Telangana Revenue Minister Ponguleti Srinivasa Reddy held an emergency review meeting at the state secretariat. The government announced ₹4,00,000 in financial assistance for each victim's family.

In neighbouring Andhra Pradesh, the combined two-day death toll crossed 40 by May 24, with temperatures reaching 46°C. Red alerts were issued across both states.

In Uttar Pradesh, the death count is harder to verify. Russia's President Putin sent condolences for more than 100 deaths from storms and abrupt weather in UP — a diplomatic message that inadvertently highlighted how severely Indian state governments underreport heat deaths. The National Crime Records Bureau revealed in 2024 that actual heat stroke deaths were 127.9% higher than state-reported figures — 1,832 versus the 804 initially claimed. UP alone had 352 unreported deaths that year.

The real toll this May is almost certainly higher than anyone is saying.

## What the Temperatures Look Like

Brahmapuri in Maharashtra's Vidarbha region recorded 47.2°C — the hottest temperature in India this season. Vidarbha had already crossed 46°C multiple times that week. The region has been under sustained heat dome conditions, where high-pressure atmospheric systems trap superheated air over the Indo-Gangetic plains and prevent normal atmospheric mixing.

Delhi hit 42.7°C, with the India Meteorological Department warning that temperatures in Delhi, Punjab, and Haryana may rise further before any meaningful relief arrives. A ground report from Delhi's Nand Nagri area measured road and vehicle surfaces at 65°C under direct sunlight — even as weather apps showed a comparatively lower 42°C air temperature.

Rajasthan's Chittorgarh recorded 44.2°C. Agra in western UP has repeatedly crossed 46°C. Ballia and the Bundelkhand districts — historically among India's most heat-exposed areas — are seeing hospital admissions spike again.

The IMD issued heatwave alerts across northern and central India, warning that dry conditions and strong sunlight will continue for several more days. Even in traditionally cooler Himachal Pradesh, a yellow alert was issued for May 26-27.

## The Convergence: Why 2026 Is This Bad

This is not one problem. It is five problems happening at once.

**Climate change is raising the baseline.** India's annual average temperature has risen 0.15°C per decade between 1951 and 2016, and the trajectory is accelerating. What used to be a once-in-a-decade extreme is now showing up every summer.

**Pre-monsoon activity has been weak.** The usual cloud cover and sporadic rains that offer relief in April and May have not materialised on schedule. Without that buffer, the sun has been beating down on bare ground for weeks.

**Dry northwesterly winds** are pushing hot air from Rajasthan and Pakistan deep into central and northern India. These winds carry no moisture — only heat.

**A heat dome** has settled over the region, trapping hot air that cannot rise and disperse. Temperatures ratchet up day after day. The body never recovers because even nighttime temperatures stay dangerously high.

**A possible Super El Niño** is developing for later this year. That typically means below-average monsoon rains for India — less groundwater recharge, lower reservoir levels, agricultural stress, and extended heat for longer than usual.

And all of this is colliding with an energy crisis. Power demand has hit record highs as air conditioners and coolers strain grids that were never built for sustained load at this level. The Iran war has pushed crude prices above $100 a barrel. India's state-owned fuel retailers just implemented their fourth price hike this month. The people who can least afford the electricity to power a fan are the same people dying from the heat.

## The Himalayas Are Collapsing

Turn north — to Uttarakhand, where India's great rivers are born — and the story becomes existential.

On August 5, 2025, a violent wall of water, rocks, and mud slammed into Dharali village in Uttarkashi district, destroying homes, hotels, and markets along the Khir Gad stream before reaching the Bhagirathi River. The initial explanation was a cloudburst.

It was not a cloudburst. ISRO scientists, using satellite imagery, digital elevation models, and publicly available video, determined the real trigger: a 69-million-kilogram ice patch on the Srikanta Glacier had suddenly collapsed. The ice mass, at roughly 5,220 metres altitude, had been exposed by the thinning of its protective snow cover — a direct consequence of warming temperatures.

"As deglaciation advances, ice-patch instability in nivation zones is a growing and under-recognised threat across high-mountain catchments," the ISRO researchers warned in their study, published in NPJ Natural Hazards.

This is not a separate event from the heatwave. It is the same event, happening at a different altitude. The same rising temperatures sending thermometers past 47°C in Vidarbha are stripping protective snow cover from glaciers at 5,000 metres. In the short term, melting glaciers temporarily increase river flows — providing false comfort before the water runs out permanently. In the long term, the Ganga and Yamuna, which hundreds of millions depend on, face a future of diminishing glacial input.

## The One Piece of Good News

The southwest monsoon is arriving early. The IMD confirmed that the monsoon has advanced rapidly across the Andaman Sea, the Arabian Sea, and the Bay of Bengal. Its onset in Kerala is now expected by May 26 — several days ahead of the traditional June 1 date.

Heavy rainfall is forecast over Kerala, Lakshadweep, Tamil Nadu, and the northeastern states over the next four to five days.

But Kerala getting rain does not cool Delhi. The monsoon's march northward across the subcontinent typically takes weeks. North India, where most of the dying is happening, may not see meaningful monsoon relief until mid to late June. Until then, the IMD's forecast is more heat, more alerts, and more days where the thermometer reads numbers that the human body was not designed to survive outdoors.

## What This Means for the Diaspora

If you are an NRI planning a summer trip to India between now and mid-June, understand what you are walking into. Delhi at 42.7°C with 65°C road surfaces is not the summer you remember from childhood visits. If you have young children or elderly parents travelling with you, adjust your plans. Fly into Kerala or a southern coastal city where the monsoon has already broken. Avoid northern India until late June at the earliest.

If your parents live alone in UP, Telangana, Rajasthan, Maharashtra's Vidarbha, or any of the states under IMD heatwave alerts, this is the call you need to make today. Thirty-four people have already died. The victims are disproportionately elderly, living alone, without access to cooling. Make sure your parents have working desert coolers or air conditioning. Make sure they are drinking water regularly and not going outside between 11 AM and 4 PM. Make sure someone is checking on them.

If you send money home, understand that the family receiving it is simultaneously dealing with the fourth fuel price hike this month, electricity bills at record levels from running coolers around the clock, and cooking gas that costs more than it did six months ago. The ₹10,000 you send goes less far when everything costs more because the energy supply chain is broken.

At current warming trajectories, experts warn that parts of India could see heat index values — the "feels like" temperature — reach 60°C by 2050. At that level, the human body physically cannot cool itself through sweating. The heat becomes unsurvivable for healthy adults outdoors.

That is 24 years away. The 47.2°C in Vidarbha is happening right now."""
    })
    print(f"✅ Article 1 queued: {slug1}")
else:
    print(f"⏭️  Article 1 skipped (duplicate): {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: India's Rupee Crashed to ₹97/$ — Fourth Fuel Hike, Modi's Austerity Call, RBI Scrambles
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("india-rupee-97-record-low-fuel-hike-modi-austerity-rbi-nri-remittance")
headline2_prefix = "the rupee just hit"
if slug2 not in existing_slugs and not any(headline2_prefix in h for h in existing_headlines_lower):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "The Rupee Just Hit ₹97 to the Dollar — Its Worst Level in History. India Raised Fuel Prices for the Fourth Time This Month. Modi Asked Citizens to Work From Home and Skip Foreign Travel.",
        "subheadline": "Last Wednesday, the Indian rupee crashed to nearly ₹97 against the US dollar — a record low, down 6% since January, making it Asia's worst-performing currency in 2026. The RBI Governor told the Mint newspaper on Sunday that the rupee appears 'undervalued' and the central bank will do 'whatever is required.' On Monday, state-owned fuel retailers raised petrol and diesel prices for the fourth time in May. MK Global estimates prices may need to rise another ₹10 per litre to cover oil marketing companies' losses. And on May 10, Prime Minister Modi did something rarely seen in peacetime: he publicly asked Indian citizens to revive work-from-home, avoid non-essential foreign travel for a year, and conserve fuel. For the 4.4 million Indian Americans who send money home, every dollar buys more rupees than ever — but every rupee buys less than ever. The arithmetic of the diaspora's relationship with India just changed.",
        "slug": slug2,
        "category": "news",
        "vertical": "economy",
        "diaspora_angle": "For NRIs, a collapsing rupee is two contradictory things at once. It is a windfall and a crisis, happening to the same family simultaneously. When you open your remittance app and see that $1,000 now converts to ₹95,500 instead of the ₹86,000 it was in January, it looks like your family is getting more. But your family is paying ₹113 for a litre of petrol in Mumbai. They are paying ₹950-1,000 for a cooking gas cylinder. Their electricity bill has doubled because they are running coolers 18 hours a day in a heatwave. The price of atta, dal, vegetables — all of it has climbed because transport costs are up, because diesel is up, because the Strait of Hormuz was closed for three months. Your $1,000 buys more rupees, but the rupees buy less life. When Modi asks citizens to work from home and avoid foreign travel, when the government raises gold import duty to 15% and restricts silver imports, when the RBI burns through $30 billion in reserves trying to slow the slide — these are emergency measures for an economy under energy siege. NRI bond schemes may be coming, as they were in 1998 and 2013. If you own Indian property, its dollar value has dropped 6% this year without the property losing a single rupee. If you are sending money for a parent's medical procedure, the timing helps. If you are planning a wedding in India this winter, your dollar goes further. But if your family in India is trying to live on their rupee salary, they are being squeezed from every direction — fuel, food, electricity, cooking gas — with no relief in sight until the Iran deal resolves or the monsoon arrives or both.",
        "tags": ["rupee", "India", "economy", "fuel price", "RBI", "Modi", "dollar", "Hormuz", "Iran war", "oil", "NRI", "remittance", "inflation", "forex", "OMC", "Sanjay Malhotra", "gold import duty"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Rupee to extend rally on US-Iran deal hopes, RBI Governor's remarks aid sentiment", "url": "https://www.reuters.com/world/india/rupee-extend-rally-us-iran-deal-hopes-rbi-governors-remarks-aid-sentiment-2026-05-25/"},
            {"name": "Stockk.trade — Rupee at 96: Why India's Currency Is Falling and What RBI Can Do", "url": "https://stockk.trade/blogs/rupee-at-96-and-rising-is-rbi-running-out-of-options"},
            {"name": "Asian News 18 — Fuel Price Hike Looms in India: Petrol, Diesel May Rise Up to ₹10", "url": "https://asiannews18.com/en/news/breaking-news/2026-05-22/fuel-price-hike-looms-in-india-petrol-diesel-may-rise-up-to-indian-rupee10-amid-crude-oil-surge"},
            {"name": "Reuters — India's state-owned fuel retailers increased diesel and petrol prices on Monday, the fourth hike in May", "url": "https://www.reuters.com/world/india/rupee-extend-rally-us-iran-deal-hopes-rbi-governors-remarks-aid-sentiment-2026-05-25/"}
        ]),
        "score_total": 83,
        "status": "published",
        "published_at": now_plus1,
        "body": """On Wednesday, May 21, the Indian rupee hit 97 against the US dollar. It was the lowest the currency has ever been.

By Friday, after two days of aggressive Reserve Bank of India intervention — selling dollars through state-run banks, leaning on the market with the full weight of the central bank's balance sheet — the rupee recovered to 95.69. On Monday morning, it opened at 95.50, aided by optimism about a possible US-Iran peace deal and a Brent crude price that had retreated below $100 a barrel for the first time in over two weeks.

But the recovery is fragile. The rupee is still down 6% since January 1, making it Asia's worst-performing currency in 2026. And the forces driving it lower have not gone away.

## The Numbers Behind the Collapse

The rupee's fall is not a mystery. It is a direct consequence of the Iran war.

When the US-Iran conflict erupted on February 28, 2026, and the Strait of Hormuz — through which 45% of India's crude oil imports had transited — was closed, India's energy supply chain was thrown into crisis. Brent crude, which was trading below $85 per barrel before the conflict, surged past $100 and peaked near $111.

India imports roughly 85% of its crude oil. When crude prices spike by 30% in three months, the trade deficit widens catastrophically, the current account deficit expands, and every barrel India buys requires more dollars than the market can supply without pushing the rupee lower.

The numbers tell the story:

The rupee was at ₹86.22 on January 30. It was at ₹87.46 when the war began on February 28. By mid-April, RBI intervention had stabilised it in the 94-95 range. Then the intervention could not hold. On May 18, it crashed to an intraday low of ₹96.20. By May 21, it touched ₹97.

In less than three months, the rupee lost roughly 10 rupees against the dollar — a pace of depreciation that India has rarely seen outside of full-blown financial crises.

## The Fourth Fuel Hike

On Monday, May 25, India's state-owned fuel retailers — Indian Oil, Bharat Petroleum, and Hindustan Petroleum — raised petrol and diesel prices for the fourth time this month.

The government had already raised prices by roughly ₹3 per litre earlier in May. But according to a report by financial services firm MK Global, that is not enough. Oil marketing companies may need to increase retail fuel prices by as much as ₹10 per litre to cover their mounting losses.

Petrol now costs ₹97.5 to ₹114.93 per litre depending on the city. Diesel ranges from ₹92 to ₹96 per litre. Mumbai remains among the most expensive cities, with petrol near ₹113.

Every ₹1 increase in fuel prices ripples through the economy. Transport costs rise. Vegetable and grocery prices follow. Construction materials get more expensive. The cost of running a generator during a power cut — increasingly common as the heatwave strains electricity grids — goes up.

A $10 per barrel rise in crude is estimated to push retail inflation by 0.3% and widen the current account deficit by a similar margin. Crude has risen by roughly $25 per barrel since January.

## Modi's Unprecedented Austerity Call

On May 10, Prime Minister Narendra Modi did something that Indian leaders rarely do in peacetime. Speaking at an event in Secunderabad, he publicly asked Indian citizens to revive work-from-home practices, avoid non-essential foreign travel for at least one year, and conserve fuel wherever possible.

On the surface, it was responsible messaging during a global energy crisis. Markets read it differently. For analysts, it was an open admission that the energy situation was serious enough to warrant public behavioural change at scale. Opposition leader Akhilesh Yadav called it "an admission of failure."

The government followed up with emergency economic measures:

**Gold import duty** was raised from 6% to 15%, with the effective rate crossing 18% when IGST is included. India imports roughly $72 billion worth of gold annually, and every dollar spent on gold is a dollar not available to pay for oil.

**Silver imports** were placed under a restricted monitoring framework, requiring higher compliance and effectively limiting the flow.

**The RBI sold $3.6 billion** in spot market intervention in April alone, and has conducted two consecutive days of firm intervention as recently as last week. India's forex reserves have declined by over $30 billion from their late-February peak.

These are not routine policy adjustments. They are the actions of a government and central bank in crisis-management mode.

## The RBI Governor Speaks

On Sunday, RBI Governor Sanjay Malhotra told the Mint newspaper that the central bank will do "whatever is required" to ensure orderly movements in the foreign exchange market. He also said that following its recent fall, the rupee appears undervalued.

"Undervalued" is significant language from a central bank governor. It signals that the RBI believes the rupee's fall has overshot fundamentals — that the currency should be worth more than ₹95 to the dollar — and that the central bank is prepared to use its reserves to defend that view.

But the RBI's ammunition is not unlimited. Forex reserves have already dropped substantially. Every dollar the RBI sells to support the rupee is a dollar removed from India's financial safety net. Analysts at ING cautioned on Monday: "We've been at this stage before, only for talks to break down. The market will likely be more cautious about overreacting to these headlines."

Bank of America has revised its end-of-2026 forecast to ₹98 per dollar. If the Iran deal collapses, analysts at CR Forex see a scenario where the rupee hits ₹100-108.

## The Remittance Paradox

For the 4.4 million Indian Americans in the United States, the rupee's collapse creates an unusual paradox. Every dollar sent home now buys more rupees than at any point in history. A $1,000 remittance that converted to ₹86,000 in January now converts to roughly ₹95,500. A family sending $2,000 a month home is effectively sending an extra ₹19,000 per month compared to six months ago — without changing the dollar amount.

This is significant. India received $125 billion in remittances in 2025 — the largest remittance-receiving country in the world. For millions of families, the monthly transfer from a son, daughter, or spouse working abroad is the single largest income source. A weaker rupee means that income goes further in rupee terms.

But here is the paradox: the rupee is weak because everything in India is getting more expensive. The extra ₹19,000 your family receives is being eaten by ₹113 petrol, ₹950 cooking gas cylinders, electricity bills that have doubled because coolers are running 18 hours a day in the worst heatwave of the century, and food prices inflated by transport cost increases that cascade through every supply chain.

The rupee buys more of itself per dollar. But each rupee buys less of everything else.

## What History Tells Us May Come Next

India has been here before. In 1998, after nuclear sanctions devastated the rupee, the government launched the Resurgent India Bonds — a special instrument designed to attract dollar deposits from the Indian diaspora at premium interest rates. It raised $4.2 billion.

In 2013, when the rupee crashed past ₹68 amid the "taper tantrum," the RBI launched the FCNR(B) scheme, raising $34 billion from NRI deposits in three months. It worked. The rupee stabilised. Capital flowed in.

Analysts are watching for something similar now. If reserves continue declining toward $680 billion, the RBI may announce a new NRI bond scheme — effectively asking the diaspora to lend dollars to India during a crisis. The terms would likely include above-market interest rates, tax exemptions, and principal protection in dollars.

For NRIs, this would be a financial opportunity wrapped in a patriotic obligation. The 2013 scheme delivered returns above 7% for dollar deposits — more than double what a US savings account offers today.

## The Iran Deal: The Variable That Changes Everything

The one factor that could reverse all of this — the rupee's fall, the fuel price hikes, the austerity measures — is the resolution of the Iran war and the reopening of the Strait of Hormuz.

On Monday, Brent crude dropped below $100 per barrel for the first time in over two weeks, on optimism that the US and Iran are moving toward a deal. Asian stocks rose over 1%. Regional currencies strengthened. The dollar index fell below 99.

But the administration has sent mixed signals. On Saturday, Trump said Washington and Iran had "largely negotiated" a memorandum of understanding. On Sunday, the administration downplayed expectations of a quick deal.

If a deal holds — if Hormuz reopens, crude drops to $75-85, and sanctions are lifted in phases — analysts at Stockk.trade estimate the rupee could recover to 88-91 over three to six months. The RBI would rebuild reserves. A rate cut cycle could begin. The fuel price hikes would reverse.

If the deal collapses or the conflict escalates, the rupee could breach ₹100 by year-end. Crude could hit $130-140. Emergency capital controls — the kind India has not used since the 1991 crisis — become possible.

For the average Indian family, the distance between these two scenarios is the distance between an economy that recovers and one that breaks down. For the average NRI family, it is the distance between a remittance that helps and a remittance that barely keeps pace.

The RBI Governor says he will do "whatever is required." The Prime Minister says to stay home and conserve fuel. The fuel companies say prices need to rise another ₹10. And in Washington and Tehran, two governments cannot agree on whether the deal that would fix all of this actually includes the hardest part.

The rupee, as of Monday morning, is ₹95.50. It is waiting — like everyone else — to find out."""
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

print("\n✅ Writer pipeline complete")
