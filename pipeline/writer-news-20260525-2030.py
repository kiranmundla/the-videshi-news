#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-25 20:30 UTC batch
Topics: 1) India fuel price hike — 4th in 10 days, petrol crosses Rs 102, Rs 7.5/liter cumulative, post-election timing, inflation spiral
        2) Trump demands Abraham Accords expansion — Pakistan rejects, "silence on the line," India's strategic advantage
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

# ── Pexels helper ──
pexels_env = Path.home() / "workspace" / ".env.pexels"
PEXELS_KEY = None
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.split("=", 1)[1].strip()

def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        print("  ⚠ No Pexels key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=15
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                if photos:
                    url = photos[0]["src"]["large2x"]
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    try:
        img_data = requests.get(image_url, timeout=20).content
        content_type = "image/jpeg"
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        h = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        r = requests.post(upload_url, headers=h, data=img_data, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {filename}")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({r.status_code}): {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return image_url

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
# ARTICLE 1: India Fuel Price Hike — 4th in 10 Days
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("india-fuel-price-hike-fourth-time-petrol-crosses-102-delhi-iran-war")
headline1_check = "fuel price"
headline1_check2 = "petrol"
if slug1 not in existing_slugs and not any(headline1_check in h and headline1_check2 in h for h in existing_headlines_lower):
    body1 = """India's state-run fuel retailers raised petrol and diesel prices for the fourth time in ten days on Monday. Petrol in Delhi crossed ₹102 per litre. Diesel hit ₹95.20. In Mumbai, petrol is now ₹111.21. The cumulative increase since May 15 is nearly ₹7.50 per litre — a 7.8 percent rise for petrol and 8.6 percent for diesel, pushing prices to their highest levels since May 2022.

Indian Oil Corporation, Bharat Petroleum, and Hindustan Petroleum — which together control roughly 90 percent of India's retail fuel market — cited surging global crude oil prices, a weakened rupee, and tightening refining margins. Private operators like Shell are already charging more than ₹116 per litre for petrol and ₹127 for diesel.

The hikes have triggered a political firestorm. Congress leader Rahul Gandhi coined a new epithet for the prime minister — "Mehangai Manav Modi" — accusing the government of picking citizens' pockets "in installments, bit by bit." Congress president Mallikarjun Kharge described the repeated revisions as a "daily assault" of "fuel loot."

## The Timing Is the Story

The opposition's sharpest argument is not about the economics. It is about the calendar.

India had effectively frozen retail fuel prices for nearly four years. The Modi government maintained this freeze through a period when crude oil surged more than 50 percent — absorbing the cost through state-run oil companies that were posting combined losses of ₹10 billion daily at the peak.

The first hike came on May 15. That date matters. The BJP had just won three of five state and union territory assembly elections, including West Bengal. The Congress argues that the government weaponized fuel pricing: freeze the pain before votes are cast, unleash it once they are counted.

"For months, I had been warning of an impending economic storm," Gandhi wrote on X. "But Modi Ji, true to form, was busy with elections at the time — and the moment the elections ended, he hiked the prices of petrol and diesel by ₹8."

The timeline: May 15, ₹3 per litre up. May 19, 90 paise. May 23, 87-91 paise. May 25, ₹2.61-2.71. Four installments in ten days. The Congress calls it "installment looting." The BJP responds that prices are still below market-linked levels — oil companies are still losing roughly ₹6 billion daily even after the hikes — and that further adjustments are necessary to prevent a fiscal crisis.

Both sides are correct. That is the problem.

## The Iran War Made This Inevitable

India's fuel pricing was already unsustainable before the first hike. What made it untenable was the Iran war.

Global crude oil prices have surged more than 50 percent since late February, driven by US-Israeli strikes on Iran and the effective closure of the Strait of Hormuz — the chokepoint through which roughly 20 percent of the world's oil supply passes. India imports more than 85 percent of its crude oil. A significant share of that historically transited through Hormuz.

The rupee has dropped 4.7 percent against the dollar since the war began — making every barrel of imported crude more expensive in rupee terms. Brent crude, though it dipped below $100 on Monday on Iran peace deal optimism, remains structurally elevated. The Energy Information Administration expects it to average above $100 in the near term.

Even after Monday's hike, India's state-run retailers are selling fuel below market-linked levels. Sujata Sharma, joint secretary in the oil ministry, told reporters that oil marketing companies' losses have "narrowed to slightly less than ₹6 billion daily, from ₹10 billion." That framing — celebrating that public companies are only losing ₹6 billion per day — tells you everything about the scale of the problem.

## The Cascade Is Coming

Diesel is the bloodstream of India's economy. Every truck, every tractor, every freight train runs on it. When diesel prices rise ₹7.50 in ten days, the cost of moving vegetables from farm to mandi rises. The cost of delivering rice from warehouse to ration shop rises. The cost of running the generator that keeps the cold storage unit operational during a power cut rises.

Economists are flagging a broader inflationary spiral. Radhika Piplani of Motilal Oswal projects inflation climbing to 5.7 percent for the current financial year — well above the Reserve Bank of India's own forecast of 4.6 percent. The fuel price hikes alone will add an estimated 38 basis points to the consumer price index, according to Nomura's Sonal Varma.

The RBI's Monetary Policy Committee meets June 3-5 for an interest rate decision. The central bank had been on a cautious easing cycle. That calculus has changed. Governor Sanjay Malhotra has said the RBI will do "whatever is required" to ensure orderly movement in the foreign exchange market — language that carries more weight when the rupee is at its weakest against the dollar in years.

Indian Oil reported that diesel sales at its retail outlets climbed 18 percent in the first 22 days of May compared to last year. Petrol sales rose 14 percent. Part of this is genuine demand. Part of it is panic buying. And part of it is arbitrage — state-run companies are selling diesel to bulk users at premiums of at least ₹40 per litre above retail prices, which has driven commercial buyers to stock up at subsidized retail stations. The result: dry-outs at fuel stations across multiple states, and growing concerns about supply shortages.

LPG prices are expected to follow. "We expect more action to come through another retail fuel price hike and a hike in liquefied petroleum gas prices," Piplani said.

## What This Means for the Diaspora

For the 32 million Indians living abroad, the fuel price hikes are not a domestic news story. They are a direct hit on the families they support.

India received $129 billion in remittances in 2024 — more than any other country. A significant share of that money goes toward household expenses: cooking gas, transportation, school fees, medical bills. When petrol crosses ₹102 and diesel approaches ₹100, the purchasing power of every rupee remitted from San Jose or Dubai or London diminishes.

The cascade is real. When diesel rises, the auto-rickshaw fare rises. The delivery charge on the Swiggy order rises. The price of tomatoes at the vegetable market rises — not because tomatoes cost more to grow, but because they cost more to move. A grandmother in Chennai whose NRI son sends ₹50,000 per month is now buying less with that money than she was buying ten days ago.

The timing compounds the pain. The rupee's 4.7 percent decline against the dollar since February means remittances in dollar terms go slightly further in rupee value — but the inflation those rupees encounter when spent erases the gain. If you are sending $600 from the Bay Area to your parents in Hyderabad, the exchange rate might give you 57,000 rupees instead of 55,000. But when those rupees hit a city where petrol has risen 8 percent and vegetables have followed, your parents are not better off. They are worse off.

For NRIs who are planning visits home this summer, the costs compound further. Domestic flights in India run on aviation turbine fuel, which is derived from the same crude oil that just got more expensive. Internal travel costs — taxi fares, train travel, even the cost of hiring a car for a family trip — are all rising.

And for the Indian tech workers on H-1B visas who send money home while navigating their own cost-of-living pressures in the US — where inflation has stubbornly persisted — the dual squeeze is acute. Prices are rising in both countries simultaneously, and there is no hedge for a family that straddles both economies.

The Indian government's argument is that the hikes were inevitable and that further delay would have created a larger crisis. The opposition's argument is that the government chose the timing for political advantage. For the diaspora, neither argument matters much. What matters is that cooking gas, petrol, and diesel in India just got significantly more expensive, and every indication suggests they will get more expensive still."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "India Just Raised Fuel Prices for the Fourth Time in Ten Days. Petrol Has Crossed ₹102 in Delhi. ₹111 in Mumbai. The Cumulative Hike Is Nearly ₹7.50 Per Litre. The Opposition Is Calling It 'Installment Looting.' The Government Says It Is Still Losing ₹6 Billion a Day.",
        "subheadline": "State-run fuel retailers — Indian Oil, Bharat Petroleum, Hindustan Petroleum — raised petrol by ₹2.61 and diesel by ₹2.71 on Monday, the fourth hike since May 15. Cumulative increases: 7.8% for petrol, 8.6% for diesel, pushing prices to the highest since 2022. Rahul Gandhi coined 'Mehangai Manav Modi'; Congress president Kharge called it a 'daily assault of fuel loot.' The opposition's core argument: prices were frozen during state elections, then unleashed after the BJP won. Oil companies are still losing ₹6 billion daily at these prices. The Iran war's closure of the Strait of Hormuz has pushed crude up 50% since February. The rupee has fallen 4.7% against the dollar. RBI meets June 3-5. Economists expect inflation to hit 5.7%, well above the central bank's 4.6% forecast. LPG hikes are expected next.",
        "slug": slug1,
        "category": "news",
        "vertical": "economy",
        "diaspora_angle": "India received $129 billion in remittances in 2024. When petrol crosses ₹102 and diesel approaches ₹100, every rupee remitted from San Jose or Dubai buys less. The rupee's 4.7% decline since the Iran war means dollar remittances convert to slightly more rupees — but inflation erases the gain. Cooking gas, transport, vegetables, school fees — all rising simultaneously. NRIs planning summer visits face higher domestic flight costs (aviation fuel), taxi fares, and internal travel costs. Indian tech workers on H-1B face a dual squeeze: inflation in both countries, no hedge for families straddling both economies.",
        "tags": ["fuel prices", "petrol", "diesel", "India", "inflation", "Iran war", "Strait of Hormuz", "rupee", "RBI", "Congress", "BJP", "Rahul Gandhi", "remittances", "NRI", "oil companies", "economy"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg via Rigzone — India Raises Diesel, Gasoline Prices for 4th Time in May", "url": "https://www.rigzone.com/news/wire/india_raises_diesel_gasoline_prices_for_4th_time_in_may-25-may-2026-183771-article/"},
            {"name": "BRICS Times — Opposition Demands Rollback of 4th Fuel Hike", "url": "https://bricstimes.in/india/opposition-demands-rollback-fourth-petrol-diesel-price-hike-10-days-india-2026/"},
            {"name": "Livemint — Oil drops below $100 on Iran peace hopes, but fuel prices rise again", "url": "https://www.livemint.com/"},
            {"name": "Reuters — Rupee gains to two-week high, forward premiums dip as oil prices slump", "url": "https://www.reuters.com/"},
            {"name": "APAC News Network — Fuel Price Hike Today: Petrol Up Rs 2.61, Diesel Rises", "url": "https://apacnewsnetwork.com/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now_iso,
        "body": body1
    })
    print(f"✓ Article 1 prepared: India fuel price hike — 4th in 10 days")
else:
    print(f"✗ Article 1 skipped (duplicate detected)")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Trump Demands Abraham Accords Expansion — Pakistan Rejects
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("trump-abraham-accords-expansion-pakistan-rejects-india-advantage")
headline2_check = "abraham accords"
if slug2 not in existing_slugs and not any(headline2_check in h for h in existing_headlines_lower):
    body2 = """On Saturday, Donald Trump got on a conference call with the leaders of Saudi Arabia, the United Arab Emirates, Qatar, Pakistan, Turkey, Egypt, Jordan, and Bahrain. He told them he wanted every single one of them to sign the Abraham Accords — the US-brokered framework for normalizing relations with Israel — as a condition of any deal to end the Iran war.

There was silence on the line. Trump joked and asked if they were still there.

On Monday, he made it public. "I am mandatorily requesting that all Countries immediately sign the Abraham Accords," Trump wrote on Truth Social. "And that, if Iran signs its Agreement with me, as President of the United States of America, it would be an Honor to have them also be part of this unparalleled World Coalition."

Pakistan was the first to publicly reject the demand. "Pakistan is under no compulsion to adhere to any such demand," a Pakistani source familiar with the matter told Reuters, adding that the Abraham Accords and the Iran ceasefire were "not interlinked and cannot be made so."

None of the other five uninvolved countries — Saudi Arabia, Qatar, Turkey, Egypt, or Jordan — have publicly responded. None are expected to say yes. But none said no on the call either, and that is the space Trump is working in.

## What Trump Is Actually Doing

This is not a peace proposal. This is leverage architecture.

The Abraham Accords were originally brokered during Trump's first term in 2020, largely by his son-in-law Jared Kushner. The United Arab Emirates and Bahrain signed first, followed by Morocco and Sudan. The accords established normalized diplomatic, commercial, and security relations between Israel and Arab states — without resolving the Palestinian issue. The biggest prize, Saudi Arabia, never signed. Crown Prince Mohammed bin Salman signaled openness but set a precondition: a clear and irreversible roadmap for a Palestinian state, which Israel has never agreed to provide.

What Trump did on Saturday's call was take his Iran war leverage — America's military position, the Strait of Hormuz reopening, the potential release of tens of billions in frozen Iranian assets — and attach it to a completely separate diplomatic objective: Israel normalization. He is using the Iran crisis as a forcing function for the Abraham Accords expansion that eluded him in his first term.

The logic, from Trump's perspective, is that these countries need the Iran war to end — disrupted oil flows, spiking fuel costs, closed airspace — and that need gives him leverage to extract concessions on Israel that have nothing to do with Iran. It is transactional diplomacy applied with a sledgehammer.

## Why Pakistan Said No

Pakistan's rejection was immediate and unambiguous, and it was never really in doubt.

Pakistan has never recognized Israel. The country's founding identity is intertwined with Muslim solidarity — its very creation was predicated on the idea that Muslims on the Indian subcontinent needed a separate state. Recognizing Israel, in the context of the ongoing war in Gaza and the destruction of Palestinian infrastructure, would be political suicide for any Pakistani leader.

But Pakistan's rejection carries an additional irony. Pakistan was reportedly invited to the Saturday call because of its recent role as a mediator in the Iran crisis — its army chief, General Asim Munir, had just returned from Tehran where he met with Iranian leadership. Pakistan has been positioning itself as a diplomatic bridge between the US and Iran. Trump's demand to sign the Abraham Accords as part of that same process effectively conflated two fundamentally different diplomatic tracks.

The Pakistani source's statement — that the two issues are "not interlinked and cannot be made so" — was both a rejection and a warning. Pakistan will continue mediating on Iran. It will not normalize with Israel. And it will not accept a framework where one requires the other.

## The Silence on the Line

What is more telling than Pakistan's rejection is the silence from the others.

Saudi Arabia did not respond. For the kingdom that controls Islam's two holiest sites, Mecca and Medina, recognizing Israel while the world watches Gaza remains a non-starter in public. But privately, Saudi-Israeli relations have been developing for years — intelligence cooperation, backchannel diplomacy, shared concern about Iran's nuclear program. The kingdom has not said no. It has said "not yet, and not without a Palestinian state." That is a negotiating position, not a brick wall.

Qatar, which hosts Hamas's political leadership and has been the primary mediator in Gaza hostage negotiations, is in an impossible position. Turkey, under Erdogan, has been the most vocal critic of Israel in the Muslim world. Egypt has a cold peace with Israel dating to 1979 but has no appetite for expanding it during a period of regional instability. Jordan, which has the largest Palestinian refugee population of any country, faces domestic constraints that make Abraham Accords membership politically toxic.

But none of them pushed back on the call the way Pakistan did. The silence, as Axios reported, hung in the air. And that silence is data. It means Trump's proposal is being considered — not as a realistic near-term outcome, but as a marker of what America will expect in exchange for ending the Iran war.

## What This Means for India

India was not on Saturday's call. India does not need to sign the Abraham Accords — it already has full diplomatic relations with Israel, established in 1992. But Trump's gambit reshapes the regional geometry in ways that matter enormously for New Delhi.

First, it deepens Pakistan's isolation. If the Abraham Accords expand — even modestly, even to one or two additional countries — Pakistan's refusal to recognize Israel puts it further outside the emerging Middle Eastern security architecture. Pakistan's traditional leverage in the Gulf — its military manpower, its nuclear capability, its ideological solidarity — is being eroded by economic realities. The Gulf states are diversifying away from security dependence on Pakistan and toward commercial partnerships with India, Israel, and East Asia. Every step toward expanded Abraham Accords is a step away from the regional framework Pakistan has relied on for decades.

Second, it accelerates corridors that benefit India. The India-Middle East-Europe Economic Corridor (IMEC), announced at the G20 in 2023 under India's presidency, is designed to create a shipping and rail link from India through the UAE and Saudi Arabia to Europe via Israel. The corridor requires normalized relations between the Gulf states and Israel to function. If Trump's pressure yields even partial results — Saudi Arabia formalizing commercial ties with Israel, for instance — the IMEC corridor becomes more viable.

Third, it reinforces India's multi-alignment strategy. India maintains strong ties with Israel (defense, technology, agriculture), with the Gulf states (energy, labor, remittances), and with Iran (Chabahar port, cultural ties). Trump's attempt to force countries into a binary — sign the accords or lose access to Iran deal benefits — is exactly the kind of rigid framework India has been navigating around. India's position on the Abraham Accords is simple: it does not need to sign because it already recognizes Israel, and it does not need to choose between Israel and the Arab world because it has relationships with both.

The Quad foreign ministers meeting scheduled for May 26 — with Jaishankar hosting Rubio, along with counterparts from Australia and Japan — adds another layer. India is simultaneously deepening its strategic partnership with the US while maintaining its independent foreign policy. Trump's Abraham Accords push, by pressuring Pakistan and the Gulf states, creates space for India without requiring India to do anything.

## The Diaspora Dimension

For the Indian diaspora, this story operates on multiple levels.

The 3.5 million Indians in the Gulf — the largest migrant worker population in the region — are directly affected by Middle Eastern stability. The Abraham Accords, if expanded, could create new economic corridors, new business opportunities, and new labor markets. But instability in the process — Saudi-Israeli tensions, Pakistan-Gulf frictions, the ongoing Iran war — keeps the region volatile and keeps Indian workers exposed.

For the 4.8 million Indian Americans, the geopolitical chess game has a more subtle implication. Indian Americans are increasingly prominent in US foreign policy circles — from Vivek Ramaswamy to Sriram Krishnan to Kash Patel. India's strategic ascent in a post-Abraham Accords Middle East is not just a diplomatic abstraction. It is a source of community standing, of professional relevance, and of the quiet pride that comes from watching your country of origin gain influence in the world's most consequential region.

The contrast with Pakistan is stark. While India navigates multi-alignment and deepens ties with every major player in the Middle East, Pakistan is being asked to make a choice it cannot make — and the consequences of that refusal are being compounded by its own internal instability, its debt crisis, and its diminishing leverage with Gulf allies who increasingly see India as the more reliable partner.

Trump's demand for mandatory Abraham Accords signing will almost certainly not succeed in its current form. Pakistan will not recognize Israel. Saudi Arabia will not move without a Palestinian state framework. Turkey will not reverse under Erdogan. But the demand has changed the conversation. It has established a price for American involvement in ending the Iran war. And in that repricing, India — which already has what Trump is asking others to give — finds itself on the right side of every equation."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Trump Got on a Call with Eight Middle Eastern Leaders and Told Them to Sign the Abraham Accords. There Was Silence on the Line. He Asked If They Were Still There. Pakistan Was the First to Say No. India Was Not on the Call. India Did Not Need to Be.",
        "subheadline": "Trump demanded that Saudi Arabia, Qatar, Pakistan, Turkey, Egypt, and Jordan sign the Abraham Accords — normalizing relations with Israel — as a precondition for ending the Iran war. He posted it on Truth Social: 'I am mandatorily requesting that all Countries immediately sign.' Pakistan immediately rejected the demand: 'Pakistan is under no compulsion to adhere to any such demand.' None of the others have responded publicly. The Axios account of the Saturday conference call — where silence followed Trump's demand, and he had to ask if the leaders were still on the line — captures a collision between American transactional leverage and the deepest political fault lines in the Muslim world. India, which has had full diplomatic relations with Israel since 1992, does not need to sign. But the expansion of the Abraham Accords framework accelerates corridors, deepens Pakistan's isolation, and reinforces the multi-alignment strategy that has made India the Middle East's most versatile partner.",
        "slug": slug2,
        "category": "news",
        "vertical": "diplomacy",
        "diaspora_angle": "3.5 million Indians in the Gulf are directly affected by Abraham Accords dynamics — expanded normalization could create new economic corridors and business opportunities. For 4.8 million Indian Americans, India's rising influence in the Middle East is a source of community standing: Indian Americans are increasingly prominent in US foreign policy (Ramaswamy, Krishnan, Patel). India's multi-alignment — strong ties with Israel, Gulf states, and Iran simultaneously — positions it uniquely. Pakistan's rejection deepens its isolation from the emerging Middle Eastern security architecture that Indian diaspora professionals are helping shape. The IMEC corridor (India-UAE-Saudi-Israel-Europe) becomes more viable with every step toward expanded accords.",
        "tags": ["Abraham Accords", "Trump", "Pakistan", "Israel", "India", "Saudi Arabia", "Iran war", "Middle East", "diplomacy", "IMEC", "Quad", "Gulf states", "Jaishankar", "NRI"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Trump links Abraham Accords to any Iran deal", "url": "https://www.reuters.com/world/trump-links-abraham-accords-any-iran-deal-2026-05-25/"},
            {"name": "The Daily Jagran — Abraham Accords Explained: Could Iran's Entry Hurt Pakistan?", "url": "https://www.thedailyjagran.com/world/trump-urges-arab-nations-to-join-abraham-accords-after-iran-deal-10313549"},
            {"name": "Axios — Trump demands Abraham Accords expansion on conference call", "url": "https://www.axios.com/"},
            {"name": "Global Defense Corp — Pakistan, Qatar and Saudi Arabia under pressure", "url": "https://globaldefensecorp.com/"},
            {"name": "Washington Examiner — Trump says Gulf States should recognize Israel", "url": "https://www.washingtonexaminer.com/"}
        ]),
        "score_total": 87,
        "status": "published",
        "published_at": now_plus1,
        "body": body2
    })
    print(f"✓ Article 2 prepared: Trump Abraham Accords expansion / Pakistan rejects")
else:
    print(f"✗ Article 2 skipped (duplicate detected)")


# ══════════════════════════════════════════════════════════════
# PUBLISH + IMAGES
# ══════════════════════════════════════════════════════════════

image_queries = [
    ("India petrol pump fuel station", "Indian gas station queue"),
    ("diplomatic conference call world leaders", "Middle East diplomacy summit"),
]

for i, article in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Publishing article {i+1}: {article['headline'][:80]}...")

    # Fetch Pexels image
    q1, q2 = image_queries[i] if i < len(image_queries) else ("news", None)
    pexels_url = fetch_pexels_image(q1, q2)

    # Insert article
    row = {
        "id": article["id"],
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "slug": article["slug"],
        "body": article["body"],
        "category": article["category"],
        "vertical": article.get("vertical", ""),
        "diaspora_angle": article.get("diaspora_angle", ""),
        "tags": article["tags"],
        "sources": article["sources"],
        "score_total": article["score_total"],
        "status": "published",
        "published_at": article["published_at"],
        "image_url": pexels_url or "",
    }

    try:
        result = sb_post("p2_articles", row)
        print(f"  ✓ Inserted: {article['slug']}")
        article_id = result[0]["id"] if isinstance(result, list) else result["id"]
    except Exception as e:
        print(f"  ✗ Insert failed: {e}")
        continue

    # If we have a Pexels image but insert didn't set it, patch it
    if pexels_url and not row.get("image_url"):
        try:
            sb_patch("p2_articles", {"id": f"eq.{article_id}"}, {"image_url": pexels_url})
            print(f"  ✓ Image URL patched")
        except Exception as e:
            print(f"  ⚠ Image patch failed: {e}")

print(f"\n{'='*60}")
print(f"Published {len(articles)} articles total")

# ── Score decay ──
print("\n── Score decay ──")
# Decay articles older than 7 days
decay_7d = sb_get("p2_articles", {
    "select": "id,score_total",
    "status": "eq.published",
    "category": "eq.news",
    "published_at": "lt.2026-05-18T00:00:00Z",
    "score_total": "gt.35",
    "limit": "50"
})
if decay_7d:
    for a in decay_7d:
        try:
            sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": 35})
        except:
            pass
    print(f"  7d+ decay: {len(decay_7d)} articles → 35")

# Decay articles 3-7 days old
decay_3d = sb_get("p2_articles", {
    "select": "id,score_total",
    "status": "eq.published",
    "category": "eq.news",
    "published_at": "lt.2026-05-22T00:00:00Z",
    "published_at": "gte.2026-05-18T00:00:00Z",
    "score_total": "gt.50",
    "limit": "50"
})
if decay_3d:
    for a in decay_3d:
        try:
            sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": 50})
        except:
            pass
    print(f"  3-7d decay: {len(decay_3d)} articles → 50")

if not decay_7d and not decay_3d:
    print("  No articles to decay")

# ── Git commit ──
print("\n── Git commit ──")
try:
    subprocess.run(["git", "add", "-A"], cwd=str(Path.home() / "workspace" / "the-videshi-news"), capture_output=True)
    result = subprocess.run(
        ["git", "commit", "-m", f"writer-news 20:30 UTC — fuel hikes + abraham accords"],
        cwd=str(Path.home() / "workspace" / "the-videshi-news"),
        capture_output=True, text=True
    )
    if result.returncode == 0:
        push = subprocess.run(
            ["git", "push"],
            cwd=str(Path.home() / "workspace" / "the-videshi-news"),
            capture_output=True, text=True, timeout=30
        )
        print(f"  ✓ Pushed to git" if push.returncode == 0 else f"  ⚠ Push failed: {push.stderr[:200]}")
    else:
        print(f"  ℹ Nothing to commit")
except Exception as e:
    print(f"  ⚠ Git error: {e}")

print("\n✅ Writer run complete")
