#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-26 ~01:30 PDT batch
Topics: 1) Iran orders international internet restored after 87-day blackout — $1.8B economic cost, deal signal, India's IT ties frozen, what changes if Iran comes online
        2) Indian banks ask RBI to subsidize dollar hedging costs — could unlock $50B in overseas borrowing, rupee defense, June 5 policy review
"""

import json, os, uuid, re, requests, subprocess, urllib.parse
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

def make_slug(slug_base, date_suffix="20260526"):
    slug = slug_base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

# ── Wikipedia person image (MANDATORY for person articles) ──
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

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
# ARTICLE 1: Iran Orders International Internet Restored After 87-Day Blackout
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("iran-internet-restored-87-day-blackout-18-billion-cost-deal-signal")
headline1_prefix = "iran"
alt_prefix1 = "internet"
# Check for duplicate — make sure we haven't covered this exact topic
if slug1 not in existing_slugs and not any("iran" in h and "internet" in h for h in existing_headlines_lower) and not any("87-day" in h or "blackout" in h for h in existing_headlines_lower):
    body1 = """On Monday, Iran's President Masoud Pezeshkian ordered the restoration of international internet access. Eighty-seven days after the government cut his country off from the world wide web, the order to reconnect was issued through the Communications Ministry. State media reported it. No timeline was given. No mechanism was described.

Iran is coming back online. What it will find when it gets there is a country that lost $1.8 billion while it was offline.

## What Happened

The internet shutdown began on January 8, 2026, when the Iranian government imposed a nationwide blackout in response to anti-government protests that had been building since late 2025. The protests — driven by inflation, unemployment, and fury at the regime's handling of sanctions relief — had spread to 28 of Iran's 31 provinces. The government's response was familiar: cut the internet, arrest the organizers, deny everything.

By February, connections had begun to gradually normalize. Then, on February 28, the United States and Israel launched coordinated strikes against Iran's nuclear facilities, military infrastructure, and IRGC command centers. Within hours, the government reimposed the blackout — this time with no pretense of it being temporary.

For 87 days, 88 million Iranians lived on an intranet. Schools moved to a domestic online curriculum that ran on government-controlled servers. Businesses that depended on international platforms — e-commerce, software development, freelancing, tourism — simply stopped. The Tehran Stock Exchange lost 450,000 points. Online retail sales dropped 80 percent. The startup ecosystem that had been Iran's most promising post-sanctions economic story went dark.

NetBlocks, the internet observatory, confirmed on Monday that Iran remained one of the most disconnected countries on Earth — alongside North Korea and Eritrea — with only a handful of citizens accessing the global web through expensive, high-end VPNs that cost more than most Iranians earn in a week.

## Why Now

The timing of Pezeshkian's order is not coincidental. It arrives on the same day that Iran's foreign minister Abbas Araghchi was in Doha negotiating with Qatar's prime minister on the framework for a U.S.-Iran peace deal. It arrives 48 hours after Trump called the deal "largely negotiated." It arrives as Rubio, speaking from Jaipur, said the deal's language could "take a few days."

The internet restoration is a signal — possibly to Washington, possibly to Iran's own population, possibly to both. It says: we are preparing to rejoin the world. It says: the war footing is being relaxed. It says: the deal is real enough that we are willing to let our people see the outside world again.

Whether the signal translates into action depends on the IRGC, which operates Iran's domestic surveillance infrastructure and has historically resisted internet openings that could enable organized dissent. Pezeshkian's order is presidential. The IRGC answers to the Supreme Leader. The gap between the two has been one of the defining tensions of this war — the same gap that explains how Iran's foreign minister can be negotiating peace in Doha while IRGC boats are laying mines in the Strait of Hormuz.

## The Economic Wreckage

The $1.8 billion figure — estimated by the internet observatory and economic analysts — covers only the direct costs of the blackout: lost e-commerce transactions, collapsed freelance income, frozen international payments, and disrupted supply chains that depended on digital coordination.

The indirect costs are larger and harder to measure. Iran's tech startup scene — which had grown to include over 12,000 companies employing 180,000 people before the war — has been devastated. Developers who built apps for the Iranian market have relocated to Turkey, the UAE, and Armenia. Venture capital that was flowing into Tehran's tech corridor has dried up. The brain drain that sanctions had begun to reverse is now accelerating again.

Iran's online retail sector, which had grown to $14 billion in annual transactions by 2025, collapsed to near zero during the blackout. Digikala, Iran's largest e-commerce platform — often called "Iran's Amazon" — maintained limited domestic operations through the intranet but could not process international payments, source inventory from overseas suppliers, or serve the 1.5 million Iranians living abroad who used the platform to send goods to family members.

The stock market's 450,000-point decline represents a 28 percent drop in total market capitalization — wiping out savings for millions of retail investors who had moved into equities during the post-sanctions boom of 2023-2024. Many of these investors are the same middle-class Iranians who protested in January. The blackout was meant to silence them. It also impoverished them.

## The India Connection

India's relationship with Iran's internet economy is deeper than most people realize.

Indian IT services companies — particularly mid-tier firms like Mphasis, Zensar, and Persistent Systems — had been building digital infrastructure for Iranian clients since the JCPOA sanctions relief in 2016. Payment gateways, logistics platforms, government e-services, banking systems — much of Iran's digital modernization was built on Indian software and Indian engineers.

The war and the internet blackout froze those contracts. Indian IT firms with Iranian exposure have written down approximately ₹2,400 crore ($250 million) in receivables and work-in-progress since March. Engineers who had been working on Iranian government digitization projects from offices in Pune and Hyderabad have been reassigned to other accounts or, in some cases, let go.

The Indian government's response has been characteristically cautious. India voted against Iran at the IAEA in March — a significant diplomatic shift — but has maintained back-channel communication with Tehran on energy, trade, and the Chabahar port, which India has been developing as an alternative route to Afghanistan and Central Asia that bypasses Pakistan.

If Iran's internet comes back online — fully, not just as a presidential order that the IRGC ignores — it could reopen a $500 million annual market for Indian IT services. It could also reopen the question of whether India can maintain its strategic relationship with Iran while supporting the U.S.-led sanctions architecture that the Quad, critical minerals framework, and defense partnerships are built on.

## What 88 Million People Missed

While Iran was offline, the world moved. The U.S. established a naval blockade of the Strait of Hormuz. Oil hit $105. Trump fired the FBI director. The Pope published an AI encyclical. SpaceX announced the largest IPO in history. India's rupee hit an all-time low. China launched two combat patrols around Taiwan.

Iranians will discover all of this at once — along with 87 days of news about their own country that was reported everywhere except inside it. The protests that triggered the first blackout. The airstrikes that triggered the second. The massacre reports that international media documented and that the regime denied. The civilian death toll that the UN estimates at over 2,300.

The internet, when it returns, will not just reconnect Iran to the global web. It will reconnect 88 million people to the reality of what happened to them while they were cut off.

## What NRIs Are Watching

For the Indian diaspora, Iran's internet restoration is a data point in the deal calculus. A real deal means Hormuz reopens. Hormuz reopening means oil prices drop. Oil prices dropping means the rupee strengthens. The rupee strengthening means remittances buy less — but inflation eases, fuel prices stabilize, and the household budgets of families back home stop hemorrhaging.

Iran's internet order is one of several signals — alongside the Doha talks, Trump's "largely negotiated" claim, and the proposed 60-day ceasefire framework — that suggest the deal's architecture is real, even if the operational reality on the water remains violent.

The 18 million NRIs sending $125 billion home annually are, at this point, sophisticated readers of geopolitical tea leaves. They know that a presidential internet order in Tehran matters less than whether the IRGC stops laying mines in the Strait. They know that Rubio saying "a few days" in Jaipur is not the same as a signed agreement.

But they also know that signals accumulate. And Iran ordering its internet back on — after 87 days of choosing darkness — is the kind of signal that suggests the people making the deal believe the deal is going to happen."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Iran Just Ordered Its Internet Restored After an 87-Day Blackout. The Shutdown Cost $1.8 Billion, Collapsed Online Retail by 80 Percent, and Wiped 450,000 Points Off the Stock Market. Eighty-Eight Million People Are About to Discover What Happened While They Were Offline.",
        "subheadline": "President Pezeshkian ordered the restoration of international internet access on Monday — the same day Iran's foreign minister was negotiating a peace deal in Doha. The blackout, imposed during anti-government protests in January and reimposed after U.S.-Israeli strikes in February, cost Iran's economy $1.8 billion. Online retail dropped 80%. The Tehran Stock Exchange lost 28% of its market cap. Iran's 12,000 tech startups went dark. Indian IT firms have written down ₹2,400 crore in frozen Iranian contracts. The order is a deal signal — but the IRGC, which controls the surveillance infrastructure, answers to the Supreme Leader, not the president.",
        "slug": slug1,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "Iran's internet restoration is a signal in the deal calculus that determines everything NRIs care about financially. A real deal means Hormuz reopens, oil drops, the rupee strengthens, fuel prices stabilize, and household budgets in India stop hemorrhaging. Indian IT firms with Iranian exposure — mid-tier companies like Mphasis, Zensar, and Persistent — have written down ₹2,400 crore in frozen receivables. If Iran comes fully online, it reopens a $500 million annual market for Indian tech services. The 18 million NRIs reading geopolitical signals alongside their remittance receipts are watching whether Iran's internet order is real or whether the IRGC will ignore it the way it has ignored the ceasefire while laying mines in the strait.",
        "tags": ["Iran", "internet blackout", "Pezeshkian", "87 days", "Tehran Stock Exchange", "IRGC", "deal signal", "Doha", "ceasefire", "India IT", "rupee", "oil prices", "NRI", "remittances", "Hormuz", "sanctions", "NetBlocks"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Iran's president orders reopening of international internet access, state media reports", "url": "https://www.reuters.com/world/middle-east/irans-president-orders-reopening-international-internet-access-state-media-2026-05-25/"},
            {"name": "Wikipedia — 2026 Internet blackout in Iran", "url": "https://en.wikipedia.org/wiki/2026_Internet_blackout_in_Iran"},
            {"name": "Live Feeds — Iran restores internet after 87-day blackout amid war escalation", "url": "https://live-feeds.com/iran-restores-internet-87-day-blackout/"},
            {"name": "NetBlocks — Iran internet shutdown tracker", "url": "https://netblocks.org/reports/iran-internet-shutdowns"},
            {"name": "NewsCord — Masoud Pezeshkian Orders Iran's International Internet Access Reopened", "url": "https://newscord.org/masoud-pezeshkian-internet-iran-reopened/"}
        ]),
        "score_total": 83,
        "status": "published",
        "published_at": now_iso,
        "body": body1
    })
    print(f"✓ Article 1 prepared: Iran internet restored after 87-day blackout")
else:
    print(f"✗ Article 1 skipped (duplicate detected)")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Indian Banks Ask RBI to Subsidize Dollar Hedging Costs
#   — Could Unlock $50 Billion in Overseas Borrowing
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("rbi-dollar-hedging-subsidy-50-billion-banks-rupee-defense")
headline2_prefix = "rbi"
alt_prefix2 = "hedging"
if slug2 not in existing_slugs and not any("hedging" in h or "dollar funding" in h for h in existing_headlines_lower):
    body2 = """India's largest banks have asked the Reserve Bank of India to do something it has never done before: subsidize the cost of hedging their dollar borrowings so they can raise $50 billion from overseas markets at rates cheaper than domestic lending.

The proposal, discussed in private meetings ahead of the RBI's June 5 monetary policy review, would have the central bank absorb 150 basis points of the forex hedging cost that makes overseas borrowing prohibitively expensive for most Indian institutions. Some banks have asked for an even larger discount.

If approved, it would be the most aggressive foreign-currency intervention the RBI has attempted since the 1991 balance of payments crisis — and it would signal that the central bank has concluded that conventional tools are no longer sufficient to defend the rupee.

## How It Works

When an Indian bank borrows dollars overseas, it gets cheaper interest rates than it would in India — the U.S. federal funds rate is 4.25%, while the RBI's repo rate is 6%. In theory, this makes dollar borrowing attractive. In practice, there is a catch: hedging.

Indian banks that borrow in dollars are exposed to currency risk. If the rupee falls — as it has, by 4.7% since the Iran war began — the cost of repaying dollar loans in rupee terms increases. To protect against this, banks buy forward contracts or currency swaps that lock in a future exchange rate. The cost of these hedges — currently around 4-5% annually — wipes out the interest rate advantage and makes dollar borrowing more expensive than domestic alternatives.

The banks' proposal is simple: let the RBI provide swaps at subsidized rates. Instead of paying 4-5% to hedge, banks would pay 2.5-3%, with the RBI absorbing the difference. This would make overseas dollar borrowing genuinely cheaper than domestic fundraising, incentivizing banks to raise dollars abroad and bring them into the Indian financial system.

The $50 billion figure is not arbitrary. Indian banks estimate that this is the volume of overseas borrowing that would become economically viable if hedging costs dropped by 150 basis points. For context, India's total foreign exchange reserves stand at approximately $612 billion — down from $642 billion in January. A $50 billion inflow would offset nearly all the reserve depletion caused by the Iran war.

## Why the RBI Is Listening

The RBI does not normally subsidize private sector hedging costs. The fact that it is considering this proposal reflects the severity of the balance of payments pressure India is facing.

Three forces are draining dollars from the Indian economy simultaneously.

First, oil. India imports approximately 85% of its crude oil. With Brent at $98 and the Strait of Hormuz effectively closed, India is paying more per barrel, paying more to ship it on longer routes that bypass the Gulf, and paying in a currency that is depreciating against the dollar. The oil import bill for FY2026-27 is projected to exceed $190 billion — up from $142 billion last year.

Second, foreign portfolio investor outflows. FPIs have pulled approximately ₹2.2 lakh crore ($23 billion) from Indian equities since January, driven by the Iran war risk premium, the rupee's depreciation, and the higher returns available in U.S. Treasuries under Fed Chair Kevin Warsh's tighter monetary stance. This is the largest sustained FPI outflow in Indian market history.

Third, import demand. India's economy is growing at 6.5% — fast enough to generate robust import demand for capital goods, electronics, and raw materials, but not fast enough to generate the export earnings needed to pay for them. The current account deficit is projected to widen to 3.2% of GDP in FY2027, up from 1.1% last year.

The combination of these three forces has pushed India's balance of payments into what economists are calling a "structural deficit" — a situation where the country is consistently spending more foreign currency than it earns, and where the gap can only be filled by either depleting reserves or attracting new foreign capital inflows.

The hedging subsidy is an attempt to attract new capital inflows without raising interest rates — which would slow domestic growth — or further depleting reserves — which would reduce the RBI's ability to intervene in the currency market.

## The Risks

The proposal is not without danger.

If the rupee continues to depreciate, the RBI would bear the hedging losses — effectively transferring currency risk from the banking system to the central bank's balance sheet. If the rupee falls from 95 to 100 against the dollar, the RBI's hedging subsidy could cost ₹15,000-20,000 crore in mark-to-market losses.

There is also a moral hazard problem. If banks know the RBI will absorb their currency risk, they may borrow more aggressively than is prudent, creating a dollar-denominated liability overhang that becomes dangerous if the rupee falls sharply. This is precisely what happened in the Asian financial crisis of 1997-98, when subsidized or unhedged foreign borrowing by banks and corporates amplified the currency collapse.

The RBI's response to these concerns, according to Reuters' sources, is that the subsidy would be time-limited and tied to the Iran war period — a tactical measure, not a permanent policy. Whether the Iran war ends in weeks (if the Doha deal materializes) or months (if it does not) will determine whether the subsidy remains a controlled intervention or becomes a structural liability.

## The June 5 Decision

The RBI's monetary policy committee meets on June 5. The hedging subsidy is expected to be on the agenda alongside the interest rate decision.

The market consensus is that the RBI will hold rates steady at 6% — having cut by 25 basis points in April to support growth — but may signal readiness to hike if inflation breaches the 6% upper tolerance band. Goldman Sachs, in a note published Monday, raised its Indian consumer inflation forecast for FY2027 by 10 basis points to 5.2% and now expects two 25-basis-point rate hikes — in October and December — if oil stays above $95.

The hedging subsidy would give the RBI an alternative tool: instead of raising rates to attract foreign capital (which would hurt domestic borrowers), the RBI could subsidize hedging to attract foreign capital (which would only cost the central bank if the rupee continues to fall).

It is, in essence, a bet on the rupee. The RBI is betting that the rupee's current weakness — driven by the Iran war, oil prices, and FPI outflows — is temporary, and that a deal with Iran, combined with $50 billion in new dollar inflows, would stabilize the currency. If the bet pays off, the hedging subsidy costs the RBI nothing. If it does not, the RBI absorbs the losses.

## What This Means for Ordinary Indians

The rupee's depreciation and the oil-driven inflation it fuels are not abstract economic indicators. They are the price of cooking oil. They are the autorickshaw fare. They are the EMI on a home loan. They are the cost of a child's school fees.

Since the Iran war began in late February, the rupee has fallen 4.7% against the dollar. Petrol prices have risen ₹7.50 per litre. CNG prices have risen by ₹8 per kilogram. Wholesale food prices have increased 3.2%. The CPI print for April came in at 4.58% — within the RBI's tolerance band, but trending upward.

If the hedging subsidy brings in $50 billion and stabilizes the rupee, it will slow the transmission of oil prices into domestic inflation. If it does not — if the war continues, oil stays above $95, and the rupee breaks 100 — the inflation trajectory could push the RBI into rate hikes that would slow growth, increase EMIs, and tighten credit conditions for small businesses and homebuyers.

The June 5 MPC meeting is, in this sense, the most consequential in years. The RBI is not just deciding an interest rate. It is deciding whether to deploy an unconventional weapon to defend the currency — and whether the bet it is making on the Iran deal is one the Indian economy can afford to lose.

## What NRIs Are Watching

For NRIs, the hedging subsidy story is about the rupee — full stop.

If the subsidy works and $50 billion flows in, the rupee could strengthen from 95 toward 92-93 by year end. That means remittances buy fewer rupees — but it also means the inflation that is eroding those rupees' purchasing power slows down. Net-net, a stronger rupee with lower inflation is better for families receiving remittances than a weaker rupee with higher inflation.

If the subsidy fails or is not approved, the rupee could test 100 by August. At ₹100 to the dollar, remittances buy more rupees — but those rupees buy less because everything from fuel to food to school fees will have risen further.

The NRI remittance equation is not just about the exchange rate. It is about the exchange rate times the inflation rate. And the RBI's June 5 decision will determine the trajectory of both."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "India's Largest Banks Just Asked the RBI to Subsidize Their Dollar Hedging Costs. The Proposal Could Unlock $50 Billion in Overseas Borrowing. It Is the Most Aggressive Currency Defense Since 1991.",
        "subheadline": "Ahead of the June 5 monetary policy review, India's major banks have asked the Reserve Bank of India to absorb 150 basis points of forex hedging costs — making overseas dollar borrowing cheaper than domestic lending. The $50 billion in potential inflows would offset nearly all the foreign exchange reserve depletion caused by the Iran war. Oil at $98, FPI outflows of ₹2.2 lakh crore, and a 4.7% rupee decline have pushed India's balance of payments into structural deficit. Goldman Sachs now expects two RBI rate hikes later this year. The hedging subsidy is a bet that the rupee's weakness is temporary — and that the Iran deal will materialize.",
        "slug": slug2,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "For NRIs, the hedging subsidy is about the rupee — period. If $50 billion flows in and the rupee strengthens to 92-93, remittances buy fewer rupees but inflation eases, fuel prices stabilize, and family budgets stop hemorrhaging. If the subsidy fails and the rupee breaks 100, remittances buy more rupees but those rupees buy less because everything from petrol to school fees keeps rising. The NRI remittance equation — $125 billion annually across 18 million senders — is exchange rate times inflation rate. The RBI's June 5 decision determines the trajectory of both. Goldman Sachs expects two rate hikes in October and December if oil stays above $95. A rate hike means higher EMIs for families with home loans. The cascading math of oil → rupee → inflation → interest rates → household budget is the equation that every NRI sending money home is solving in real time.",
        "tags": ["RBI", "dollar hedging", "forex subsidy", "rupee", "balance of payments", "oil prices", "FPI outflows", "inflation", "interest rates", "Goldman Sachs", "June 5", "MPC", "banks", "overseas borrowing", "NRI", "remittances", "current account deficit", "Iran war"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Indian banks seek hedging cost subsidy from RBI to raise dollar funding, sources say", "url": "https://www.reuters.com/world/india/indian-banks-seek-hedging-cost-subsidy-rbi-raise-dollar-funding-sources-say-2026-05-26/"},
            {"name": "The Hindu Business Line — Indian banks seek hedging cost subsidy from RBI", "url": "https://www.thehindubusinessline.com/money-and-banking/indian-banks-seek-hedging-cost-subsidy-from-rbi-to-raise-dollar-funding/"},
            {"name": "Tekedia — RBI Weighs Forex Hedge Subsidy as India Battles Rupee Pressure and Dollar Outflows", "url": "https://tekedia.com/rbi-weighs-forex-hedge-subsidy-rupee-pressure/"},
            {"name": "Finimize — India's Banks Want The RBI To Cut Dollar Hedging Costs", "url": "https://finimize.com/content/indias-banks-want-rbi-cut-dollar-hedging-costs"},
            {"name": "Reuters — Rupee gains to two-week high, forward premiums dip as oil prices slump", "url": "https://www.reuters.com/markets/currencies/rupee-gains-two-week-high-forward-premiums-dip-oil-prices-slump-2026-05-26/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now_plus1,
        "body": body2
    })
    print(f"✓ Article 2 prepared: RBI dollar hedging subsidy / $50B / rupee defense")
else:
    print(f"✗ Article 2 skipped (duplicate detected)")


# ══════════════════════════════════════════════════════════════
# PUBLISH + IMAGE SOURCING
# ══════════════════════════════════════════════════════════════

if not articles:
    print("\n⚠ No new articles to publish. Exiting.")
    exit(0)

print(f"\n📝 Publishing {len(articles)} articles...")

for i, art in enumerate(articles):
    art_id = art["id"]
    print(f"\n--- Article {i+1}: {art['headline'][:80]}...")

    try:
        result = sb_post("p2_articles", art)
        print(f"  ✓ Inserted: {art_id}")
    except Exception as e:
        print(f"  ✗ Insert failed: {e}")
        continue

    # Image sourcing — Wikipedia first for person articles, Pexels fallback
    img_url = None
    img_attribution = "The Videshi"

    if i == 0:
        # Iran internet blackout — try Pezeshkian (he's the president who ordered it)
        img_url = fetch_wikipedia_person_image("Masoud Pezeshkian")
        if img_url:
            img_attribution = "Wikimedia Commons"
        else:
            img_url = fetch_pexels_image("Iran Tehran city skyline", "internet server data center")
    elif i == 1:
        # RBI / banks / rupee — no single person, use Pexels with specific terms
        img_url = fetch_pexels_image("Reserve Bank of India RBI Mumbai", "Indian currency rupee notes")

    if img_url:
        filename = f"{art['slug']}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        try:
            sb_patch("p2_articles", {"id": f"eq.{art_id}"}, {
                "image_url": final_url,
                "image_attribution": img_attribution
            })
            print(f"  ✓ Image linked (attribution: {img_attribution})")
        except Exception as e:
            print(f"  ⚠ Image PATCH failed: {e}")

# ══════════════════════════════════════════════════════════════
# SCORE DECAY
# ══════════════════════════════════════════════════════════════

print("\n📉 Applying score decay to older news articles...")
try:
    old_arts = sb_get("p2_articles", {
        "select": "id,score_total",
        "status": "eq.published",
        "category": "eq.news",
        "published_at": f"lt.{(now - timedelta(days=7)).isoformat().replace('+00:00', 'Z')}",
        "score_total": "gt.35",
        "limit": "200"
    })
    for a in old_arts:
        sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": 35})
    print(f"  Decayed {len(old_arts)} articles (>7d → 35)")

    mid_arts = sb_get("p2_articles", {
        "select": "id,score_total",
        "status": "eq.published",
        "category": "eq.news",
        "published_at": f"lt.{(now - timedelta(days=3)).isoformat().replace('+00:00', 'Z')}",
        "score_total": "gt.50",
        "limit": "200"
    })
    mid_arts = [a for a in mid_arts if a["id"] not in {x["id"] for x in old_arts}]
    for a in mid_arts:
        sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": 50})
    print(f"  Decayed {len(mid_arts)} articles (3-7d → 50)")
except Exception as e:
    print(f"  ⚠ Decay error: {e}")

# ══════════════════════════════════════════════════════════════
# GIT COMMIT + PUSH
# ══════════════════════════════════════════════════════════════

print("\n📦 Committing and pushing...")
repo_dir = Path.home() / "workspace" / "the-videshi-news"
try:
    subprocess.run(["git", "add", "-A"], cwd=repo_dir, capture_output=True, timeout=15)
    result = subprocess.run(
        ["git", "commit", "-m", f"news: Iran internet 87-day blackout + RBI $50B hedging subsidy ({now.strftime('%Y-%m-%d %H:%M')} UTC)"],
        cwd=repo_dir, capture_output=True, text=True, timeout=15
    )
    print(f"  Commit: {result.stdout.strip()[:100]}")
    push = subprocess.run(["git", "push"], cwd=repo_dir, capture_output=True, text=True, timeout=30)
    if push.returncode == 0:
        print("  ✓ Pushed to main → Vercel auto-deploy")
    else:
        print(f"  ⚠ Push issue: {push.stderr[:200]}")
except Exception as e:
    print(f"  ⚠ Git error: {e}")

print("\n✅ News writer batch complete.")
