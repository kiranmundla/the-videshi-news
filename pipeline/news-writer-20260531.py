#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-05-31 batch)
Writes 3 news articles with proper image sourcing and publishes to Supabase.
"""

import json, os, re, sys, uuid, urllib.parse
from datetime import datetime, timezone

import requests

# === Load environment ===
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}


# === Image sourcing ===
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
            # Use thumbnail.source AS-IS (330px, always works)
            # originalimage can return HTML on some Wikimedia setups
            img = data.get("thumbnail", {}).get("source")
            if not img:
                img = data.get("originalimage", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels using curl (Python urllib gets 403)."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5",
                headers={"Authorization": PEXELS_API_KEY},
                timeout=10
            )
            if r.status_code == 200:
                photos = r.json().get('photos', [])
                for photo in photos:
                    src = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('original')
                    if src:
                        print(f"  ✓ Pexels image found for '{q}': {src[:80]}...")
                        return src
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Verify URL returns a valid image > 5KB."""
    if not url:
        return False
    # Check for banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com']
    if any(b in url for b in banned):
        print(f"  ✗ BANNED image source: {url[:60]}")
        return False
    if '_nc_ht=' in url or '_nc_cat=' in url or 'ccb=' in url:
        print(f"  ✗ Signed Meta URL detected: {url[:60]}")
        return False
    try:
        r = requests.get(url, timeout=15, stream=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if 'image' in ct and cl > 5000:
            return True
        # For streams without Content-Length, read initial bytes
        if 'image' in ct and cl == 0:
            chunk = r.raw.read(6000)
            if len(chunk) > 5000:
                return True
        print(f"  ✗ Image validation failed: CT={ct}, CL={cl}")
        return False
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
        return False


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        r = requests.get(image_url, timeout=30,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ✗ Download failed: status={r.status_code}, size={len(r.content)}")
            return None
        
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if 'image' not in content_type:
            content_type = 'image/jpeg'
        
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_r = requests.post(
            upload_url,
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': content_type,
                'x-upsert': 'true'
            },
            data=r.content,
            timeout=30
        )
        if upload_r.status_code in [200, 201]:
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ✗ Upload failed: {upload_r.status_code} {upload_r.text[:200]}")
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return None


def source_image(person_name=None, pexels_query=None, pexels_fallback=None, article_id=None):
    """Source image following the hierarchy: Wikipedia → Pexels → None."""
    attribution = None
    img_url = None
    
    # 1. Try Wikipedia for person articles
    if person_name:
        img_url = fetch_wikipedia_person_image(person_name)
        if img_url:
            attribution = "Wikimedia Commons"
    
    # 2. Fallback to Pexels
    if not img_url and pexels_query:
        img_url = fetch_pexels_image(pexels_query, pexels_fallback)
        if img_url:
            attribution = "Pexels"
    
    # 3. Validate
    if img_url and not validate_image_url(img_url):
        img_url = None
        attribution = None
    
    # 4. Upload to Supabase for permanence (non-Pexels, non-Wikimedia sources)
    if img_url and article_id:
        domain = urllib.parse.urlparse(img_url).netloc
        if 'pexels.com' not in domain and 'wikimedia.org' not in domain:
            uploaded = upload_to_supabase_storage(img_url, f"{article_id}.jpg")
            if uploaded:
                img_url = uploaded
                attribution = "The Videshi"
    
    return img_url, attribution


def publish_article(article):
    """Insert article into Supabase p2_articles table."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    # Source image
    img_url, img_attr = source_image(
        person_name=article.get('person_name'),
        pexels_query=article.get('pexels_query'),
        pexels_fallback=article.get('pexels_fallback'),
        article_id=art_id
    )
    
    payload = {
        'id': art_id,
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': article['slug'],
        'category': 'news',
        'status': 'published',
        'published_at': now,
        'created_at': now,
        'updated_at': now,
        'sources': json.dumps(article.get('sources', [])),
        'image_url': img_url,
        'image_attribution': img_attr,
        'diaspora_angle': article.get('diaspora_angle', ''),
        'vertical': 'news',
        'tags': article.get('tags', []),
        'urgency': article.get('urgency', 'medium'),
    }
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=30
    )
    
    if r.status_code in [200, 201]:
        result = r.json()
        rid = result[0]['id'] if isinstance(result, list) and result else art_id
        print(f"✅ Published: {article['headline'][:80]}...")
        print(f"   ID: {rid}")
        print(f"   Slug: {article['slug']}")
        print(f"   Image: {img_url or 'NONE'}")
        return rid
    else:
        print(f"❌ FAILED: {article['headline'][:80]}...")
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.text[:300]}")
        return None


# === ARTICLES ===

articles = [
    {
        "headline": "AUKUS Just Signed Its First Undersea Drone Pact. India Is Not Part of It.",
        "subheadline": "The US, UK, and Australia will jointly develop unmanned underwater vehicles to protect seabed cables and project power. Deliveries begin in 2027. India — a Quad partner but not an AUKUS member — faces hard questions about its own undersea ambitions.",
        "slug": "aukus-underwater-drones-uuv-pillar-two-shangri-la-india-indo-pacific-20260531",
        "person_name": None,
        "pexels_query": "submarine underwater navy",
        "pexels_fallback": "undersea military technology",
        "sources": ["Reuters", "Breaking Defense", "Livemint", "Capital FM"],
        "diaspora_angle": "Indian-origin defence technology professionals work across the US, UK, and Australian defence sectors. India's exclusion from AUKUS undersea tech raises questions about NRI-connected defence innovation pipelines and India's strategic tier in the Indo-Pacific.",
        "tags": ["aukus", "undersea-drones", "uuv", "shangri-la-dialogue", "indo-pacific", "india-defence", "china"],
        "urgency": "high",
        "body": """The three members of the AUKUS security pact — the United States, the United Kingdom, and Australia — have signed the alliance's first official technology agreement under its advanced capabilities track, committing to the joint development of unmanned undersea vehicles designed to protect critical seabed infrastructure and project military power across the Indo-Pacific.

The announcement, made on the sidelines of the Shangri-La Dialogue in Singapore on Saturday, marks a concrete step for a partnership that has drawn intense scrutiny from both China and nations watching from the periphery — including India.

## What the Agreement Covers

Under what AUKUS calls "Pillar Two" — the advanced technology sharing arm distinct from the nuclear submarine program — the three countries will develop a suite of multi-mission payloads for uncrewed underwater vehicles. The program covers sensors, weapons systems, and autonomous platforms capable of protecting undersea communication cables and energy pipelines, conducting surveillance and reconnaissance, executing strikes, and performing logistics operations in contested waters.

UK Defence Secretary John Healey, standing alongside US Defense Secretary Pete Hegseth and Australian Defence Minister Richard Marles, said the UK has committed £150 million to the effort. Deliveries of the initial payloads are expected to begin in 2027.

"This will rapidly give our forces the very most advanced battlefield technologies as together we produce a range of cutting-edge sensors and weapons systems for undersea drones," Healey said. He added a pointed self-critique: "For too long in AUKUS, we talked too much and delivered too little."

Hegseth echoed the ambition: "The signature project will deliver a suite of highly adaptable multi-mission UUV payloads designed to support undersea operations and maintain our collective advantage in the maritime domain."

## Why the Seabed Matters Now

Australia's Richard Marles framed the urgency in stark terms during his plenary address at the Shangri-La Dialogue, calling undersea cables "the arteries of modern civilization" and declaring that "the seabed is evolving into a battlefield."

He cited five incidents of cable severance in the Taiwan Strait linked to China and three in the Baltic Sea attributed to Russia over the past 18 months. For island nations like Australia — and for India, which depends heavily on undersea cables for its digital economy and IT services sector — the vulnerability is not abstract.

The program will also enhance capabilities in anti-submarine warfare, mine countermeasures, electronic warfare, and contested coastal operations.

## India's Position: Inside the Quad, Outside AUKUS

India has conspicuously remained outside the AUKUS framework since its formation in 2021. As a Quad partner alongside the US, Australia, and Japan, New Delhi shares strategic alignment on a free and open Indo-Pacific. But AUKUS operates at a different level of military-technological integration — one that involves sharing nuclear propulsion technology and, now, autonomous weapons systems.

India's Defence Secretary Rajesh Kumar Singh held five bilateral meetings at the Shangri-La Dialogue this week, including with the US Indo-Pacific Command chief, the NATO Military Committee chair, and counterparts from the Netherlands, Australia, Canada, and the EU. India has been actively deepening its defence diplomacy. But the underwater domain remains a gap.

India's submarine fleet — a mix of aging Kilo-class boats and the indigenously built Scorpene-class Kalvari submarines — faces well-documented modernization challenges. The navy's long-delayed Project 75I for advanced conventional submarines has yet to produce a contract. Meanwhile, China's submarine fleet has expanded rapidly, with the PLA Navy now operating the world's largest fleet of conventional submarines alongside a growing nuclear submarine force.

The AUKUS underwater drone program, built specifically for Indo-Pacific operations, sharpens the question: as the subsurface domain becomes increasingly contested, can India afford to remain a bystander in the most significant undersea technology partnership in the region?

## China's Response

Beijing has consistently condemned AUKUS as destabilizing, warning it could trigger an arms race in the Asia-Pacific. China's decision to skip the Shangri-La Dialogue for the second consecutive year — sending no senior military figure — has been noted by participants as a missed opportunity for dialogue.

## The Diaspora Angle

For Indian Americans and the broader NRI community, the AUKUS announcement carries implications beyond defence strategy. India's technology sector — with major presence in cybersecurity, AI, and advanced manufacturing — could potentially contribute to undersea capabilities if New Delhi pursued deeper partnerships. Several Indian-origin defence technology professionals work across the US, UK, and Australian defence sectors.

The question is whether India will seek a technology-sharing arrangement with AUKUS partners under separate bilateral frameworks, or whether the strategic architecture of the Indo-Pacific will increasingly divide into tiers — with India in a second tier when it comes to the most sensitive military technologies.

For now, the underwater frontier has a new power trio. India is watching from the surface."""
    },
    {
        "headline": "India's Power Grid Just Hit 270 Gigawatts of Peak Demand. Coal India Is Scrambling to Keep Up.",
        "subheadline": "A record-breaking heatwave has pushed India's electricity consumption to an all-time high. Twenty-one power plants have critically low coal stocks. Blackouts are spreading from Gurugram to Bihar.",
        "slug": "india-power-grid-270gw-record-demand-coal-shortage-heatwave-blackouts-20260531",
        "person_name": None,
        "pexels_query": "power lines electricity grid India",
        "pexels_fallback": "electrical transmission tower sunset",
        "sources": ["Reuters", "Outlook Business", "Carbon Brief", "Associated Press"],
        "diaspora_angle": "NRIs with family in India are hearing reports of load-shedding, water tanker shortages, and elderly relatives suffering without AC. The 270 GW demand peak and coal supply scramble expose the gap between India's tech-power ambitions and its grid infrastructure reality.",
        "tags": ["india-heatwave", "power-grid", "coal-india", "electricity", "blackouts", "energy-crisis", "climate"],
        "urgency": "high",
        "body": """India's power grid hit a record peak demand of 270.8 gigawatts last week, and the system is straining to hold. A brutal heatwave — sustained since mid-April with temperatures running five to eight degrees Celsius above seasonal norms — has pushed millions of Indians to crank up air conditioners, coolers, and fans. The result is an electricity crisis that exposes the fragility of the world's third-largest power market.

Coal India, the state-owned behemoth that supplies about 80 percent of the country's coal, has ordered its eight subsidiaries to maximize dispatches to power plants using every available transport mode, including direct rail links from mines. The urgency is real: twenty-one power plants across India now have critically low coal stocks, with supplies sufficient for less than a week's generation, according to the latest data from the Central Electricity Authority.

## A Grid Built for Yesterday's Demand

The immediate trigger is the heat. But the structural problem runs deeper.

In Gurugram, the satellite city that houses the back offices of half the world's Fortune 500 companies, a fire broke out at a 220-KV power station in Sector 72 on a recent Friday evening. Power was cut across multiple neighborhoods. A rapid metro train was halted mid-route, trapping hundreds of commuters in coaches as outside temperatures exceeded 41°C. Passengers eventually climbed out onto the tracks, navigating by phone flashlight.

Energy analysts say the crisis reflects infrastructure planned nearly a decade ago using demand projections that have been overtaken by reality. India's power consumption has grown faster than any model predicted, driven by urbanization, industrial expansion, and — crucially — the exponential adoption of air conditioning. When the heatwave creates two demand peaks in a single day, including nighttime peaks when solar generation drops to zero, substations designed for lower loads begin to fail.

"Many urban outages are linked to local distribution and substation stress, as heat waves are now creating two separate demand peaks in a single day," said energy analyst Akkenaguntla Karthik. "This places enormous stress on local substations and distribution infrastructure, especially during night hours when solar supply is unavailable."

## The Coal Paradox

India has installed 228 GW of non-fossil fuel capacity — an impressive figure. But coal still generates more than 70 percent of the country's electricity. When solar drops off at sunset, coal must fill the gap. And coal cannot ramp up instantly.

Coal India's production actually declined 9.7 percent in April, to 56.1 million metric tons. Stockpiles at mines stood at 113.5 million tons as of May 23 — up 10 percent from a year earlier, but not enough to eliminate anxiety. The company said it held 47.6 million tons at power plants, sufficient for about 19 days of consumption. That sounds comfortable until you realize that specific plants in specific regions can run dry much faster than the national average suggests.

The company has urged utilities to pre-position stocks, particularly those in "logistically challenging areas" — a euphemism for plants connected by single-track rail lines or located in regions where monsoon flooding routinely disrupts supply chains just as the heat begins to break.

## The Death Toll No One Can Count

More than 100 people died in the southern states of Andhra Pradesh and Telangana within just three days this week, according to the Khaleej Times. Ninety-six additional deaths were reported across Uttar Pradesh and Bihar, the country's two most populous states. The India Meteorological Department recorded 47.5°C in Khandua, Madhya Pradesh — nearly 118°F.

These numbers are almost certainly undercounts. A peer-reviewed study published this month in Frontiers estimated that a single day of extreme heat causes approximately 3,400 excess deaths nationally. A five-day heatwave — which is what India has been experiencing on repeat — yields nearly 30,000.

The victims are overwhelmingly laborers, street vendors, rickshaw pullers, and construction workers — people who cannot afford to stay indoors and whose deaths are often attributed to other causes on medical certificates.

## What the Monsoon May or May Not Fix

The India Meteorological Department has forecast the weakest monsoon in 11 years, driven by El Niño conditions. In a normal year, the monsoon's arrival in June brings a sharp drop in temperatures and eases electricity demand. If the monsoon is delayed or weakened, the power crisis could extend deep into June and beyond.

The Finance Ministry has already flagged the Strait of Hormuz disruption — caused by the US-Iran war — as the single biggest risk to the economy. Higher fuel prices combined with weak monsoon rains create a toxic combination: energy costs rise while agricultural output — and with it, rural income — falls. Inflation is the nearly certain outcome.

## The Diaspora Impact

For NRIs with family in India, the heatwave is not an abstraction. Phone calls home carry reports of load-shedding, water tanker shortages, and elderly relatives unable to sleep without air conditioning that cuts out at midnight. The disconnect between India's ambitions as a global technology power and the reality of its power grid — where a single substation fire can strand commuters in 41°C heat — is a recurring source of frustration for the diaspora.

India needs massive investment in grid modernization, battery storage, and transmission infrastructure. The government's $452 million scheme for four additional gigawatts of battery storage by 2031 is a start, but the scale of the challenge dwarfs the commitment. As one energy startup founder put it: "One significant policy change can kickstart the entire ecosystem."

The monsoon may bring relief. But the grid needs more than rain."""
    },
    {
        "headline": "The UK Foreign Secretary Is Visiting India Next Week. The Free Trade Deal They Signed Is Already in Trouble.",
        "subheadline": "Yvette Cooper will meet S. Jaishankar to discuss the Russia-Ukraine war, Ebola, and trade. But London's new steel tariffs have created the first major friction point in an agreement that was supposed to be the UK's biggest post-Brexit prize.",
        "slug": "uk-foreign-secretary-cooper-india-visit-jaishankar-free-trade-deal-steel-tariff-trouble-20260531",
        "person_name": "Yvette Cooper",
        "pexels_query": "UK India trade diplomacy",
        "pexels_fallback": "steel manufacturing factory",
        "sources": ["Reuters", "The Times", "GTR Global Trade Review", "IndiaWest"],
        "diaspora_angle": "1.9 million people of Indian heritage in the UK form the 'living bridge.' The trade deal promised easier business travel and reduced costs. UK steel tariffs threaten that promise and small business owners who import Indian goods face higher costs.",
        "tags": ["uk-india", "free-trade-deal", "steel-tariffs", "yvette-cooper", "jaishankar", "brexit", "trade"],
        "urgency": "medium",
        "body": """Britain's Foreign Secretary Yvette Cooper is heading to India next week to meet External Affairs Minister S. Jaishankar, part of a broader diplomatic tour that also includes China. The agenda is dense — the Russia-Ukraine war, the Ebola outbreak in the Democratic Republic of Congo, and the state of UK-India trade relations. But it is the last item that carries the most friction.

The UK and India signed their long-awaited free trade agreement in May 2025, a deal three years in the making and the largest Britain had secured since leaving the European Union. The agreement was designed to increase bilateral trade by an estimated £25.5 billion by 2040, cut 90 percent of Indian tariffs on British goods, and eliminate UK tariffs on 99 percent of Indian imports.

Fourteen months later, the deal's implementation has run into its first serious obstacle: steel.

## London's Steel Tariffs and Delhi's Frustration

The UK government recently imposed sweeping new steel import quotas and tariffs, a protectionist move designed to shield what remains of the British steel industry — including the recently nationalized British Steel operations in Scunthorpe. The measures have drawn furious criticism from British industry itself, with manufacturers warning that the tariffs will destroy downstream jobs while failing to save upstream ones.

But the international dimension is equally volatile. India, which has seen its steel exports to the UK surge in recent years, is one of the countries most directly affected. Indian steelmakers view the new measures as a betrayal of the spirit of the trade deal, which was supposed to open markets, not close them.

The irony is thick. Tata Steel — India's largest steelmaker and the operator of the Port Talbot works in Wales — shut down its UK blast furnaces while simultaneously investing in new capacity in India. The UK government stepped in to keep British Steel's Scunthorpe furnaces alight and prevent 2,700 redundancies. And now London is erecting barriers against the very country whose largest industrial conglomerate was until recently the backbone of British steelmaking.

## The Broader Trade Picture

The UK-India free trade deal was propelled, in large part, by geopolitics. Donald Trump's tariff regime — including 10 percent duties on both UK and Indian goods — made diversification urgent for both countries. Britain needed new markets after losing frictionless access to the EU. India wanted a showcase agreement with a major Western economy to demonstrate its willingness to open up.

The deal delivered real wins. Indian automotive tariffs were slashed from prohibitive levels to 10 percent, opening a market for British luxury car manufacturers. Tariffs on Scotch whisky were halved immediately from 150 percent to 75 percent, with further reductions over a decade. British firms gained improved access to Indian government procurement contracts, while Indian professionals got streamlined business mobility provisions.

But steel was always the sticking point. During negotiations, it was widely reported as the issue most likely to derail the entire agreement. Both sides thought they had found a workable compromise. The UK's subsequent unilateral imposition of new steel measures — outside the framework of the trade deal — has reopened the wound.

## What Cooper and Jaishankar Will Discuss

Cooper's visit comes at a moment of geopolitical complexity for both countries. The UK is navigating its position between the US and China, managing the economic fallout from Trump's tariffs while trying to maintain relationships with both Asian powers. India is in the middle of a diplomatic blitz — hosting the Quad, negotiating the final percentage points of a trade deal with the US, and deepening defence partnerships with Australia, France, and Japan.

The steel issue is unlikely to be resolved in a single meeting. But the visit matters because it signals whether London views the India relationship as strategic — something worth protecting from domestic political pressures — or transactional, to be sacrificed when local steel constituencies make noise.

For Jaishankar, the meeting is an opportunity to press the UK on implementation timelines and to extract assurances that the steel measures will not expand. India's trade negotiators are watching closely: if the UK can sign a deal and then undermine it with unilateral measures, it sets a precedent that weakens Delhi's confidence in Western trade commitments more broadly.

## The Living Bridge

The diaspora dimension is impossible to ignore. An estimated 1.9 million people of Indian heritage live in the United Kingdom, forming what both governments call the "living bridge" between the two countries. They are business owners, professionals, students, and voters.

For Indian-origin communities in Britain, the trade deal was personal. It promised easier business travel, reduced costs on imported goods, and recognition of the economic ties that bind the two countries. The steel tariffs, by contrast, feel like a step backward — particularly for small business owners who import Indian goods and now face higher costs and uncertain supply chains.

Cooper's task in New Delhi will be to reassure Jaishankar that the UK's commitment to the trade deal is genuine, even as domestic politics pull in the other direction. Whether she can deliver that reassurance — and whether Delhi will believe it — will shape the trajectory of one of Britain's most important post-Brexit relationships.

The free trade deal was signed with fanfare. The question now is whether it will be implemented with conviction."""
    }
]


# === Main ===
if __name__ == '__main__':
    print(f"\n{'='*60}")
    print(f"The Videshi — News Writer")
    print(f"Batch: 2026-05-31")
    print(f"Articles: {len(articles)}")
    print(f"{'='*60}\n")
    
    results = []
    for i, article in enumerate(articles, 1):
        print(f"\n--- Article {i}/{len(articles)} ---")
        print(f"Headline: {article['headline']}")
        word_count = len(article['body'].split())
        print(f"Word count: {word_count}")
        
        if word_count < 400:
            print(f"  ⚠ WARNING: Article below 400-word floor ({word_count} words)")
        
        art_id = publish_article(article)
        results.append({
            'headline': article['headline'],
            'slug': article['slug'],
            'id': art_id,
            'word_count': word_count,
            'status': 'published' if art_id else 'FAILED'
        })
    
    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    for r in results:
        status = "✅" if r['status'] == 'published' else "❌"
        print(f"  {status} [{r['word_count']}w] {r['headline'][:70]}...")
    
    failed = sum(1 for r in results if r['status'] != 'published')
    if failed:
        print(f"\n⚠ {failed} article(s) FAILED to publish")
        sys.exit(1)
    else:
        print(f"\n✅ All {len(results)} articles published successfully")
