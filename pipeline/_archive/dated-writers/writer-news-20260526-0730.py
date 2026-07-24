#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-26 ~07:30 PDT batch
Topics: 1) India heatwave: 18+ dead, electricity demand hits record 270.82 GW, power cuts, 21 plants at critical coal stocks, El Niño, IMD warns of continued extremes
        2) US courts dismantle Trump's tariff wall — SCOTUS struck down IEEPA tariffs, federal court struck down Section 122 10% tariffs, stay denied May 20; India-US trade deal July deadline in flux
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
# ARTICLE 1: India Heatwave — 18+ Dead, Record Electricity Demand,
#   Power Outages, Coal Crisis, El Niño
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("india-heatwave-18-dead-270gw-electricity-record-power-cuts")
headline1_prefix = "india"
# Check for overlapping heatwave articles
heatwave_dupes = [h for h in existing_headlines_lower if "heatwave" in h or "heat wave" in h or "270" in h or "electricity demand" in h]
if slug1 not in existing_slugs and not heatwave_dupes:
    body1 = """India's electricity grid just broke. Not literally — but the margins that separate a functioning power system from cascading blackouts have never been thinner.

On May 21, India's peak daytime electricity demand hit 270.82 gigawatts. It was the fourth consecutive day the country shattered its own record. The previous high — 265.44 GW — had lasted exactly one day. The day before that, it was 260.45 GW. Before that, 257.37 GW. Each day hotter than the last. Each day more air conditioners switched on. Each day the grid absorbed more load than it was designed to handle.

The Ministry of Power called it a success: demand was "successfully met." Reuters called it something else: "India battles power cuts as heatwave boosts electricity demand to record."

Both are true. The national grid held. The local grids did not.

## The Numbers

Temperatures across more than a dozen Indian states have crossed 45°C (113°F) this week. In Madhya Pradesh's Khandua, the thermometer hit 47.5°C — 117.5 degrees Fahrenheit. Delhi recorded 44.5°C on Thursday. Vidarbha in Maharashtra crossed 46°C. Rajasthan, Uttar Pradesh, Gujarat, Odisha, Telangana, Andhra Pradesh — the heat has spared almost nothing north of the Tropic of Cancer.

At least 18 people have died from heatstroke in Odisha alone, according to the state revenue department. Another 36 suspected heat-related deaths are being investigated. In Telangana, 16 heatstroke deaths have been confirmed. Across the country, the true toll is almost certainly higher — India has historically undercounted heat deaths by a factor of ten or more, because most victims die at home and are recorded as cardiac arrest or dehydration.

The India Meteorological Department has issued severe heatwave warnings through May 27 for northwest and central India. The heat is not breaking. It is building.

## The Grid Under Stress

The record demand is being driven by a simple equation: heat plus rising incomes equals air conditioning. India added an estimated 15 million air conditioning units in 2025-26. The country now has roughly 80 million room ACs — and at peak afternoon heat, they consume approximately 60-70 GW of electricity by themselves.

The power ministry reported that 62% of the record 270.82 GW demand was met by thermal generation — overwhelmingly coal. Coal India has directed all subsidiaries to ramp up supplies after 21 power plants reported critical coal stock levels, defined as less than seven days of fuel on hand. Nationally, coal stocks at power stations stand at roughly 16.5 operational days — adequate but declining.

The paradox is that India has 228 GW of non-fossil fuel capacity — solar, wind, hydro, nuclear — but solar generation drops sharply after 4 PM, precisely when household cooling demand peaks. The evening ramp, when solar disappears and thermal plants must surge to fill the gap, is the most dangerous moment for the grid. Storage capacity to bridge this gap remains negligible.

India's peak power deficit — the gap between demand and supply at the moment of highest load — reached 2.57 GW this week. That deficit translates directly into power cuts. Chennai has experienced rolling outages. Parts of Uttar Pradesh and Bihar have seen 8-12 hour daily cuts. Rural areas in Rajasthan and Madhya Pradesh report sporadic supply for days at a time.

## El Niño and the Structural Problem

This year's heatwave has been amplified by El Niño — the periodic warming of Pacific Ocean surface temperatures that raises temperatures across South and Southeast Asia. El Niño years in India consistently produce above-normal pre-monsoon heat, delayed monsoon onset, and below-normal rainfall.

The 2026 monsoon is expected to arrive in Kerala by June 1 — roughly on schedule — but its northward progression will determine whether the heat breaks in June or persists into July. Last year's monsoon was 8% below normal. Two consecutive weak monsoons would put India's agricultural output, groundwater reserves, and hydroelectric generation at risk simultaneously.

The structural problem is deeper than any single weather event. India's cooling demand is growing at 15-20% annually. Its grid infrastructure is growing at 8-10%. Every summer, the gap narrows. The grid managers perform increasingly heroic feats of load balancing. But the physics of a 270 GW peak met with 16.5 days of coal reserves and negligible battery storage is not a success story — it is a warning.

## What Families Back Home Are Living Through

The heatwave is not an abstraction for the 18 million Indians living abroad. It is a phone call. It is a WhatsApp message from a parent in Lucknow saying the power has been out since 2 PM. It is a mother in Nagpur saying the inverter battery died and the house is 44 degrees inside. It is a brother in Bhubaneswar saying three people in the neighborhood collapsed yesterday.

India's urban poor are the most exposed. Tin-roof settlements absorb and radiate heat. Outdoor workers — construction laborers, delivery drivers, street vendors, agricultural workers — have no option to stay indoors. The Economic Survey estimated that heat stress reduces outdoor labor productivity in India by 5-8% during peak summer months, equivalent to roughly ₹4-6 lakh crore in annual economic output.

For the diaspora sending money home, the heatwave has a direct financial dimension. Higher electricity bills — residential tariffs have been raised in multiple states this month — consume remittance money. Spoiled food from unreliable refrigeration costs money. Medical bills from heat-related illness cost money. The inverter batteries, the desert coolers, the water purifiers that Indian families buy to survive summer — all funded, in millions of cases, by NRI remittances.

## The Climate Question No One Is Asking

India contributes 7% of global carbon emissions. It has contributed roughly 4% of cumulative historical emissions. Its per-capita emissions are one-eighth of the United States' and one-third of China's.

And yet India absorbs a disproportionate share of climate consequences. The Himalayan glaciers that feed the Ganges, Yamuna, and Brahmaputra river systems are melting at rates that glaciologists describe as "alarming." The heat that kills workers in Odisha was not manufactured in Odisha. It was manufactured by two centuries of industrialization in countries that are now, in some cases, lecturing India about coal dependency — while India burns coal to keep its citizens alive at 47.5 degrees.

This is the climate justice argument that India's government makes at every COP summit. It is also the argument that rings hollow when India's own coal production hits record levels to power the air conditioners of its expanding middle class. The contradiction is real. The suffering is also real. Both things coexist.

The heatwave will end. The monsoon will arrive. The temperatures will drop. But next year will be hotter. The year after that, hotter still. And the grid that barely held at 270.82 GW will face 290 GW, then 310, then 330. The question is not whether India can survive this summer. It is whether India is building the infrastructure to survive the next ten."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "India's Heatwave Has Killed at Least 18 People in Odisha Alone. Electricity Demand Just Hit an All-Time Record of 270.82 Gigawatts. Twenty-One Power Plants Are Running on Critical Coal Stocks. The Grid Held. Barely.",
        "subheadline": "Temperatures have crossed 47.5°C in Madhya Pradesh, 46°C in Maharashtra's Vidarbha, and 44.5°C in Delhi. At least 18 confirmed dead in Odisha, 16 in Telangana, with dozens more under investigation. India's electricity demand has broken records four days running — 257 GW, then 260, then 265, then 270.82 GW on May 21. Coal powers 62% of the load. Twenty-one plants have critical fuel stocks. Chennai faces rolling blackouts. The peak deficit hit 2.57 GW. The IMD warns the heat continues through May 27. El Niño is making it worse. The monsoon has not yet arrived.",
        "slug": slug1,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "For 18 million NRIs, the heatwave is a phone call from home. Parents whose power went out at 2 PM and won't return until midnight. Siblings reporting three hospitalizations in their neighborhood. Higher electricity bills consuming remittance money. Inverter batteries, desert coolers, water purifiers — all funded by diaspora earnings. The Economic Survey estimates heat stress costs India ₹4-6 lakh crore in lost outdoor labor productivity annually. Residential tariffs have been raised in multiple states this month. For NRI families funding household expenses back home, the heatwave is not a weather event — it is a line item on the monthly transfer that keeps growing.",
        "tags": ["heatwave", "India", "electricity demand", "270 GW", "record", "power cuts", "coal", "El Nino", "IMD", "Odisha", "Madhya Pradesh", "Delhi", "Maharashtra", "grid", "climate", "NRI", "remittances", "monsoon"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — India battles power cuts as heatwave boosts electricity demand to record", "url": "https://www.reuters.com/world/india/india-battles-power-cuts-heatwave-boosts-electricity-demand-record-2026-05-22/"},
            {"name": "Reuters — Scorching heat drives India's power demand to a record 270 GW amid outages", "url": "https://www.reuters.com/world/india/scorching-heat-drives-indias-power-demand-record-270-gw-amid-outages-2026-05-22/"},
            {"name": "Reuters — Coal India asks units to ramp up supplies as heatwave fuels record power demand", "url": "https://www.reuters.com/business/energy/coal-india-asks-units-ramp-up-supplies-heatwave-fuels-record-power-demand-2026-05-22/"},
            {"name": "Livemint — India's peak power demand hits record 270GW as temperature soars", "url": "https://www.livemint.com/news/india/indias-peak-power-demand-hits-record-270gw-as-temperature-soars/"},
            {"name": "Phys.org — India generates record power as demand surges in severe heat wave", "url": "https://phys.org/news/2026-05-india-power-demand-surges-severe.html"}
        ]),
        "score_total": 86,
        "status": "published",
        "published_at": now_iso,
        "body": body1
    })
    print(f"✓ Article 1 prepared: India heatwave / 270 GW / 18 dead / power cuts / El Niño")
else:
    print(f"✗ Article 1 skipped (duplicate detected)")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: US Courts Dismantle Trump's Tariff Wall —
#   SCOTUS + CIT Rulings and the India Trade Deal
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("us-courts-strike-down-trump-tariffs-india-trade-deal-july")
headline2_prefix = "us courts"
alt_prefix2 = "tariff wall"
tariff_court_dupes = [h for h in existing_headlines_lower if "court" in h and "tariff" in h]
if slug2 not in existing_slugs and not tariff_court_dupes:
    body2 = """The United States government has lost the legal authority to impose the tariffs it is simultaneously using as leverage to negotiate a trade deal with India. That sentence should not make sense. It does.

Here is what has happened, in order:

In April 2025, President Trump invoked the International Emergency Economic Powers Act (IEEPA) to declare America's trade deficit a national emergency. He imposed sweeping reciprocal tariffs on nearly every country on Earth — 26% on India, 54% on China, 20% on the EU, double-digit rates on allies and adversaries alike. It was the most aggressive use of executive trade power since the Smoot-Hawley Tariff Act of 1930.

On February 28, 2026, the Supreme Court of the United States ruled that IEEPA does not authorize tariffs. The Constitution gives Congress — not the president — the power to establish taxes, including tariffs. Congress can delegate that power, but IEEPA was not a delegation of tariff authority. The tariffs were struck down.

Within days, Trump signed a new executive order imposing a 10% global tariff on all imports, this time invoking Section 122 of the Trade Act of 1974. Section 122 allows the president to impose temporary tariffs — for up to 150 days — to address balance-of-payments problems. The administration argued that America's trade deficit constituted such a problem.

On May 7, the Court of International Trade ruled 2-1 that the Section 122 tariffs were also illegal. The court found that the United States does not, in fact, have a balance-of-payments deficit — it has a trade deficit, which is a different thing. The tariffs were "invalid" and "unauthorized by law," the majority wrote.

On May 20, the same court denied the government's motion to stay the ruling during appeal. For now, Section 122 duties cannot be collected.

The administration is expected to appeal to the U.S. Court of Appeals for the Federal Circuit, and potentially to the Supreme Court again. The Section 122 tariffs were set to expire July 24 in any case.

## What This Means for the India Deal

India and the United States are negotiating an interim trade deal with a target date of July 8-9. The deal was conceived in a world where the U.S. held all the tariff leverage — 26% reciprocal tariffs on Indian goods, the threat of more, and the offer to reduce them in exchange for Indian concessions on market access, agricultural imports, digital services, and defense procurement.

That leverage has been dismantled by the courts.

The Supreme Court struck down the IEEPA tariffs. The CIT struck down the Section 122 tariffs. The government's motion to keep collecting them during appeal was denied. As of this week, the United States has no legally enforceable general tariffs on Indian imports beyond the pre-existing Section 301 duties on specific goods and standard MFN rates.

This does not mean tariffs are over. The administration retains authority under Section 301 (unfair trade practices), Section 232 (national security — the basis for steel and aluminum tariffs), and potentially Section 201 (safeguard tariffs). It is also conducting two new investigations — one into "overproduction" by 16 trading partners including China, the EU, and Japan, and another into forced-labor trade by 60 economies — that could produce new tariff actions.

But the general 10%-26% tariff regime that defined the first year of Trump's second term is legally dead. And the India trade talks were structured around that regime.

India's Ambassador to the U.S., Vinay Mohan Kwatra, expressed confidence that a deal would materialize. India's lead negotiators have framed the discussions around "a balanced agreement" that addresses both countries' concerns. The target remains July 8-9 in New Delhi, with discussions covering tariff reductions on pork and medical devices, increased Indian purchases of U.S. liquefied natural gas and defense equipment, and provisions for digital services — though digital trade rules were deferred to the full Bilateral Trade Agreement.

India had been seeking full exemption from the 26% additional tariff. The courts have now granted what the negotiators could not: the tariffs have been struck down entirely.

## The Constitutional Moment

What is happening in the U.S. trade courts is not a temporary setback for one administration's trade policy. It is a constitutional reckoning over who controls the American economy.

For decades, Congress delegated increasing trade authority to the executive branch. Presidents of both parties used this authority — Section 201, Section 301, Section 232, IEEPA, Section 122 — to impose tariffs without congressional votes. The logic was efficiency: trade negotiations move faster than legislation.

Trump tested the limits of this delegation. He used IEEPA — a law designed for sanctions on hostile nations — to impose tariffs on allies. The Supreme Court said no. He used Section 122 — a law designed for temporary balance-of-payments emergencies — to impose permanent-style tariffs on everyone. The CIT said no.

The emerging legal consensus is that the president's tariff authority is narrower than any recent president has assumed. If the Federal Circuit and Supreme Court uphold the CIT ruling, the practical effect is that any future broad tariff regime will require an act of Congress. Given the current congressional composition — a narrow Republican majority in the House that includes free-trade members — that is not guaranteed.

For India, this is both an opportunity and a risk. The opportunity: the tariff threat that was depressing Indian exports has been removed by the courts. Indian IT services, textiles, pharmaceuticals, and agricultural products face lower barriers than at any point since 2024. The risk: without tariff leverage, the U.S. may have less incentive to finalize a comprehensive deal, or may shift to non-tariff measures that are harder to challenge legally.

## The $500 Billion Question

Both countries have articulated a goal of $500 billion in bilateral trade by 2030. Current bilateral trade stands at approximately $190 billion annually. Reaching $500 billion requires a compound annual growth rate of roughly 21% — implausible without structural changes in market access, regulatory alignment, and supply-chain integration.

The court rulings create a window. With the tariff overhang removed, Indian exporters can plan investments without the uncertainty of a 26% duty that could be reimposed at any time. American companies importing from India can order without hedging against tariff volatility. The bilateral trade pipeline — which had been choked by uncertainty — can begin to flow again.

But windows close. The administration is already exploring new legal authorities. The Office of the U.S. Trade Representative's "overproduction" investigation could produce tariffs under Section 301 that survive judicial review, because Section 301 has a longer track record of court-upheld use. If India is included in the scope — and as one of the 16 named trading partners, it might be — the tariff threat returns under a different statute.

## What NRIs Are Watching

For Indian-origin professionals in the United States, the tariff saga intersects with a broader question about the India-U.S. relationship.

The trade deal being negotiated in Delhi is not just about pork tariffs and LNG imports. It is about whether the economic architecture between the two countries — the architecture that created the conditions for Indian professionals to work in American companies, for Indian IT firms to serve American clients, for Indian pharmaceutical companies to supply American pharmacies — will survive the current political moment.

The court rulings suggest that the rule of law still constrains executive economic power in the United States. That is reassuring for anyone whose livelihood depends on predictable trade rules. But the speed with which the administration pivots from one struck-down authority to the next — IEEPA to Section 122 to overproduction investigations — suggests that the impulse toward protectionism has not been defeated. It has only been rerouted.

The July deadline approaches. The tariffs are down. The negotiations continue. The question is whether both sides can build something durable in the space the courts have created — or whether the space will close before they finish building."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "The US Supreme Court Struck Down Trump's Tariffs. A Federal Court Struck Down the Replacements. The Government's Stay Was Denied. India's 26% Tariff Threat Is Legally Dead. The Trade Deal Deadline Is July 8.",
        "subheadline": "In February, the Supreme Court ruled that IEEPA does not authorize tariffs. Trump imposed new 10% tariffs under Section 122 of the Trade Act of 1974. On May 7, the Court of International Trade struck those down too — the U.S. does not have a balance-of-payments deficit. On May 20, the court denied a stay. The tariffs that were the centerpiece of U.S. leverage in India trade negotiations are now legally unenforceable. India and the U.S. are targeting an interim deal by July 8-9. The $500 billion bilateral trade goal by 2030 suddenly has fewer barriers — and fewer incentives for the U.S. to deal.",
        "slug": slug2,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "The tariff saga is not abstract for the 4.8 million Indian Americans whose professional lives exist within the India-U.S. economic corridor. Indian IT services, pharmaceuticals, and textiles face lower barriers than at any point since 2024. But the USTR's 'overproduction' investigation names 16 trading partners — if India is included, tariff threats return under Section 301. The July deal's scope — covering digital services, defense procurement, LNG — shapes the economic architecture that created conditions for Indian professionals in America. The courts have created a window. Whether both governments build something durable in it, or whether it closes before July, determines the economic terms under which the next generation of Indian-origin workers will live and work in the U.S.",
        "tags": ["tariffs", "US Supreme Court", "IEEPA", "Section 122", "Court of International Trade", "India-US trade deal", "Trump", "trade deficit", "July deadline", "NRI", "Indian exports", "IT services", "Section 301", "USTR", "bilateral trade"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "NBC News — Federal court rules against global tariffs Trump imposed after loss at the Supreme Court", "url": "https://www.nbcnews.com/politics/trump-administration/federal-court-rules-against-new-global-tariffs-trump-imposed-rcna344156"},
            {"name": "JD Supra / Husch Blackwell — Court of International Trade Denies Government's Motion to Stay Section 122 Ruling", "url": "https://www.jdsupra.com/legalnews/court-of-international-trade-denies-5694283/"},
            {"name": "AEI — The Role of GATT Article XII in Interpreting and Applying Section 122", "url": "https://www.aei.org/articles/the-role-of-gatt-article-xii-in-interpreting-and-applying-section-122/"},
            {"name": "Exim Guru — Court rulings cloud India-US trade talks", "url": "https://www.eximguru.com/exim/news/court-rulings-cloud-india-us-trade-talks.aspx"},
            {"name": "Exim Guru — Interim trade deal with US likely by July 8; India for full exemption from 26% additional tariff", "url": "https://www.eximguru.com/exim/news/interim-trade-deal-with-us-likely-by-july-8.aspx"}
        ]),
        "score_total": 87,
        "status": "published",
        "published_at": now_plus1,
        "body": body2
    })
    print(f"✓ Article 2 prepared: US courts strike down tariffs / India trade deal July deadline")
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
        # Heatwave article — no single person. Use Pexels with specific terms.
        img_url = fetch_pexels_image("India heatwave scorching sun dry cracked earth", "extreme heat summer India dusty road")
        # No generic stock — if Pexels fails, leave without image
    elif i == 1:
        # Trade/tariffs article — no single person. Use Pexels with specific terms.
        img_url = fetch_pexels_image("US Capitol building Washington DC", "American court building columns law")
        # No generic stock — if Pexels fails, leave without image

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
        ["git", "commit", "-m", f"news: heatwave 270GW + US tariff wall collapses ({now.strftime('%Y-%m-%d %H:%M')} UTC)"],
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
