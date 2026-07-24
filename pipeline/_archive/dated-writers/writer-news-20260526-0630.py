#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-26 ~06:30 UTC batch
Topics: 1) US strikes IRGC boats + missile site near Bandar Abbas even as ceasefire talks continue in Doha — oil back to $98, Indian markets open lower, rupee rally halted
        2) Quad Foreign Ministers' Meeting outcomes in Delhi — India-US critical minerals framework + rare earths deal signed, maritime surveillance initiative launched, first Quad FM meeting since 2023
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
# ARTICLE 1: US Strikes IRGC Boats & Missile Site Near Bandar Abbas
#   — While Ceasefire Talks Continue in Doha
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("us-strikes-iran-irgc-boats-mines-bandar-abbas-ceasefire-talks")
headline1_prefix = "us strikes"
alt_prefix1 = "bandar abbas"
if slug1 not in existing_slugs and not any(headline1_prefix in h or alt_prefix1 in h for h in existing_headlines_lower):
    body1 = """On Memorial Day — the day America honors its war dead — the United States sank two Iranian boats, destroyed a surface-to-air missile site, and called it self-defense.

The targets were in southern Iran, near the port city of Bandar Abbas, which sits at the throat of the Strait of Hormuz. The Islamic Revolutionary Guard Corps boats were laying mines in the strait, according to Central Command. The missile site fired on American warplanes that responded. CENTCOM eliminated both threats and issued a four-sentence statement.

"U.S. Central Command continues to defend our forces while using restraint during the ongoing ceasefire," Captain Tim Hawkins said.

It is a ceasefire in which one side is laying mines and the other is launching airstrikes. It is also a ceasefire during which the two sides are simultaneously negotiating a peace deal in Doha.

## Negotiating and Striking at the Same Time

The timing is what makes this escalation different from the dozens that have preceded it since the Iran war began in late February.

On Saturday, President Trump said a deal with Iran was "largely negotiated." Axios reported a proposed 60-day ceasefire extension during which the Strait of Hormuz would reopen, Iran would clear its mines, the U.S. would lift its blockade, and Iran would sell oil freely. Two U.S. sources told the New York Times that Iran had agreed in principle to give up its stockpile of highly enriched uranium. Oil prices fell 5.5 percent on the news. Markets rallied globally. The Indian rupee gained 0.4 percent to a two-week high of 95.28 per dollar.

Then, on Monday — while Iran's foreign minister Abbas Araghchi was meeting Qatar's prime minister in Doha to discuss the deal's terms — CENTCOM sank two IRGC boats and hit a missile launcher near Bandar Abbas.

Iran's Fars News Agency reported major explosions in Bandar Abbas and in the Persian Gulf. The Wall Street Journal confirmed the U.S. sank two boats that were actively deploying mines, after which Iran fired surface-to-air missiles at U.S. aircraft, prompting the strike on the missile site.

Secretary of State Marco Rubio, speaking from Jaipur during his India visit, said the deal's language could "take a few days" to finalize. He also said the Strait of Hormuz "has to be open, one way or the other" — a statement that is simultaneously diplomatic and threatening.

## The Market Reaction

The optimism of the weekend evaporated overnight.

Brent crude futures rose more than 2 percent to approximately $98 per barrel in early Asian trading on Tuesday. U.S. West Texas Intermediate crude was up from Monday's last traded price — though still down 5.5 percent from Friday's close, reflecting the whiplash between deal hopes and military reality.

Indian equity benchmarks opened lower on Tuesday morning. The Nifty 50 fell 0.11 percent to 24,004. The BSE Sensex shed 0.35 percent to 76,224. Eleven of sixteen major sectors declined at open.

The Indian rupee's rally — which had carried it from a record low of 96.96 to 95.28 in three sessions on the back of deal optimism — stalled. Reuters reported that the rupee's gains "may be halted by dented peace deal hopes and month-end dollar demand." Goldman Sachs raised its Indian consumer inflation forecast for FY2026-27 by 10 basis points to 5.2 percent and now expects the RBI to raise rates twice — by 25 basis points each — in October and December.

For Indian markets, the Iran war has become a binary trade: deal on means oil down, rupee up, inflation eases; deal off means oil up, rupee down, inflation accelerates. Monday's strikes pushed the needle back toward "off" without fully resetting it. The talks continue. The mines continue. The strikes continue. The market oscillates between hope and fear on a 48-hour cycle.

## What India Cannot Control

India imported 4.57 million barrels of oil per day in April — down 15.5 percent year-over-year because of the Hormuz closure. The country has redrawn its entire supply map in 90 days, turning to Venezuela, Brazil, Angola, and Nigeria to replace Gulf supplies that can no longer transit the strait.

State-owned fuel retailers raised petrol and diesel prices for the fourth time in ten days on Monday — the same day the U.S. struck Iranian targets near the strait that caused the price increases. The cumulative hike since May 15 has reached ₹7.50 per litre for petrol. CNG prices were raised by ₹2 per kilogram on Tuesday.

India's compressed natural gas price hike — the fourth in two weeks — hits autorickshaw and taxi drivers hardest, the same population that absorbs every fuel increase first and passes it to consumers last. In Delhi, CNG now costs ₹83.09 per kilogram. The cascading effect through transportation and food supply chains is already visible in wholesale price indices.

The Indian government's options are limited. It cannot influence the military dynamics between the U.S. and Iran. It cannot reopen the Strait of Hormuz. It can subsidize fuel prices — which it has resisted — or it can let the market absorb the shock and manage the political fallout. So far, it has chosen the latter.

## The Paradox of the Ceasefire

The word "ceasefire" has lost most of its meaning in this conflict. The United States and Iran declared a ceasefire weeks ago. Since then, Iran has continued laying mines in the Strait of Hormuz. The U.S. has maintained its naval blockade. CENTCOM has reported redirecting over 100 vessels and disabling four. Iran has mined. The U.S. has struck. Both sides call it defensive.

The Doha talks represent a genuine attempt to convert this armed ceasefire into an actual peace: the Strait reopens, Iran clears mines, the U.S. lifts its blockade, Iran sells oil freely, and separate negotiations begin on Iran's nuclear program. The proposed 60-day framework is detailed and specific. Both sides have made verbal commitments.

But the mines being laid on Monday suggest that not everyone in Tehran has received — or accepted — the memo. The IRGC operates with a degree of independence from Iran's diplomatic apparatus. The boats laying mines in the Strait of Hormuz may not have been acting on the same instructions as the foreign minister negotiating in Doha.

This is the paradox that makes the Iran deal simultaneously close and fragile. The deal's architecture exists. The language is being finalized. The intent appears genuine on both sides. But the operational reality on the water — mines going down, boats being sunk, missiles being fired, aircraft striking back — is running on a parallel track that could derail the diplomatic one at any moment.

## What NRIs Are Watching

For the Indian diaspora, this is the single most consequential geopolitical variable in their financial lives right now. The Iran war determines oil prices. Oil prices determine the rupee. The rupee determines remittance value, import costs, and the inflation rate that shapes the daily expenses of families back home.

Every deal rumor sends the rupee up and oil down. Every military escalation sends the rupee down and oil up. The NRI community — 18 million strong, sending over $125 billion in remittances annually — is living on a 48-hour volatility cycle driven by events in a strait most of them have never seen.

The Doha talks will continue. Rubio says the language could take days. Trump has said the U.S. will not rush. Iran's negotiating team is in Qatar. Iran's IRGC is laying mines near Bandar Abbas.

Both things are true. That is what makes this moment so dangerous — and so important for every Indian watching oil prices, checking the rupee exchange rate, or wondering why the petrol pump changed its price board again."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "The US Just Sank Two Iranian Boats and Destroyed a Missile Site Near the Strait of Hormuz. It Happened on the Same Day Both Sides Were Negotiating a Peace Deal in Doha. Oil Is Back to $98. Indian Markets Opened Lower.",
        "subheadline": "On Memorial Day, U.S. Central Command struck IRGC boats laying mines in the Strait of Hormuz and destroyed a surface-to-air missile site near Bandar Abbas — calling it self-defense during an 'ongoing ceasefire.' The strikes came 48 hours after Trump called the Iran deal 'largely negotiated' and as Iran's foreign minister was meeting Qatar's PM in Doha to finalize terms. Brent crude surged back above $97. Indian stocks fell at open. The rupee's three-day rally stalled. Goldman Sachs raised India's inflation forecast and now expects two RBI rate hikes. CNG prices were raised for the fourth time in two weeks. The deal is not dead — but the mines are still going down.",
        "slug": slug1,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "The Iran war's 48-hour volatility cycle is now the single biggest variable in the NRI financial equation. Every deal rumor sends the rupee up — it rallied from 96.96 to 95.28 in three sessions on peace optimism. Every military escalation sends it back down. Oil at $98 means India's fuel retailers will keep hiking prices. Goldman Sachs now expects two RBI rate hikes in October and December. CNG at ₹83/kg in Delhi hits autorickshaw and taxi fares, which hit food delivery costs, which hit household budgets. For NRIs sending money home, the rupee-dollar rate and the inflation rate are moving in opposite directions simultaneously — more rupees per dollar, but each rupee buys less. The $125 billion annual remittance flow is being whipsawed by events in a strait 7,400 kilometers from Mumbai.",
        "tags": ["Iran war", "US strikes", "IRGC", "Strait of Hormuz", "Bandar Abbas", "ceasefire", "oil prices", "Brent crude", "Indian markets", "Nifty", "Sensex", "rupee", "CNG", "Goldman Sachs", "RBI", "inflation", "NRI", "remittances", "Doha talks", "CENTCOM", "Rubio"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — US military strikes Iranian boats, missile launch sites: CENTCOM", "url": "https://www.reuters.com/world/us-military-strikes-iranian-boats-missile-launch-sites-centcom-2026-05-26/"},
            {"name": "Wall Street Journal — U.S. Launches Strikes on Targets in Southern Iran", "url": "https://www.wsj.com/world/middle-east/u-s-launches-strikes-on-targets-in-southern-iran-2026-05-26/"},
            {"name": "Reuters — Indian shares open lower as US strikes dent Mideast peace hopes", "url": "https://www.reuters.com/markets/asia/indian-shares-open-lower-us-strikes-dent-mideast-peace-hopes-2026-05-27/"},
            {"name": "Reuters — Oil rises, stocks mixed as new US strikes dampen peace deal optimism", "url": "https://www.reuters.com/business/energy/oil-rises-stocks-mixed-us-strikes-dampen-peace-deal-optimism-2026-05-27/"},
            {"name": "Reuters — Rupee's rally may be halted by dented peace deal hopes, month-end dollar demand", "url": "https://www.reuters.com/markets/currencies/rupees-rally-may-be-halted-dented-peace-deal-hopes-2026-05-27/"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now_iso,
        "body": body1
    })
    print(f"✓ Article 1 prepared: US strikes Iran / Bandar Abbas / oil $98 / Indian markets lower")
else:
    print(f"✗ Article 1 skipped (duplicate detected)")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Quad Foreign Ministers' Meeting in Delhi — Concrete Outcomes
#   — Critical minerals deal, rare earths, maritime surveillance initiative
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("quad-foreign-ministers-delhi-critical-minerals-rare-earths-deal")
headline2_prefix = "quad foreign ministers"
alt_prefix2 = "critical minerals"
if slug2 not in existing_slugs and not any(headline2_prefix in h or alt_prefix2 in h for h in existing_headlines_lower):
    body2 = """On Monday, the foreign ministers of Australia, India, Japan, and the United States sat down in New Delhi for the first Quad Foreign Ministers' Meeting since 2023. They signed a critical minerals framework. They launched a maritime surveillance initiative. They sealed a rare earths deal.

Then they went back to a world on fire.

The Quad — which spent its first decade being dismissed as a "talk shop" and the last three years struggling to define itself beyond anti-China rhetoric — produced more concrete deliverables in one afternoon than it has in any single meeting since its elevation to leader level in 2021.

The question is whether any of it matters when the strait that carries 20 percent of the world's oil is mined, the largest land war in Europe since 1945 grinds on, and the host country's currency is at a record low.

## What They Actually Signed

The headline outcome was the India-U.S. Critical Minerals Framework — a bilateral agreement within the Quad structure that commits both countries to joint exploration, processing, and supply-chain development for critical minerals including lithium, cobalt, nickel, and rare earth elements.

The framework matters because of who it is aimed at: China.

China controls roughly 60 percent of global rare earth mining and over 85 percent of rare earth processing. Every semiconductor, every electric vehicle battery, every wind turbine, every advanced weapons system in the world depends on materials that flow through Chinese processing facilities. The U.S. and India have been trying to break this dependency for years. The Quad framework is the most structured attempt to date.

Under the deal, India will expand mining and processing of rare earths — particularly in Andhra Pradesh, Odisha, and Jharkhand, where deposits are substantial but underdeveloped. The U.S. will provide technology transfers, financing mechanisms, and guaranteed offtake agreements. Japan and Australia — both major players in the critical minerals supply chain — will contribute processing technology and logistics infrastructure.

Jaishankar and Rubio also signed a separate rare earths deal that goes beyond the broader framework. The specifics have not been fully disclosed, but Livemint reported that it includes provisions for India to supply processed rare earth oxides to U.S. defense and technology manufacturers — a direct challenge to China's near-monopoly on the materials that go into F-35 fighter jet magnets, Tomahawk missile guidance systems, and iPhone vibration motors.

## The Maritime Surveillance Initiative

The second major outcome was the launch of the Indo-Pacific Maritime Surveillance Cooperation initiative — a system for real-time monitoring of vessel movements and suspicious activities across the Indian and Pacific Oceans.

The initiative builds on the existing Indo-Pacific Maritime Domain Awareness (IPMDA) program but expands it significantly. The new system will integrate satellite imagery, ship-tracking data, and AI-driven anomaly detection to monitor everything from illegal fishing to sanctions evasion to naval movements by countries that the Quad has carefully avoided naming but everyone understands to be China.

For India, the maritime surveillance initiative has immediate practical value. India's coastline stretches over 7,500 kilometers. Its Exclusive Economic Zone covers 2.37 million square kilometers. The Indian Navy has been stretched thin by the Iran war — monitoring the Strait of Hormuz situation, escorting commercial vessels through contested waters, and maintaining its regular patrols in the Indian Ocean — while also keeping an eye on China's growing naval presence in the region.

The Quad surveillance system gives India access to sensor networks and data fusion capabilities that would cost billions to develop independently. Japan's maritime surveillance technology — among the most advanced in the world — will be shared under the framework. Australia's experience with monitoring the vast distances of the Pacific adds another layer.

## The Trust Deficit

Reuters headlined its Quad coverage with a pointed observation: the grouping "seeks relevance."

Under Biden, the Quad had momentum. Leaders met annually. Initiatives were launched on vaccines, climate, technology, and cybersecurity. The grouping was positioned as the democratic world's answer to Chinese assertiveness in the Indo-Pacific.

Under Trump, the momentum stalled. Trump's transactional foreign policy — tariffs on allies, demands for trade reciprocity, bilateral dealmaking over multilateral architecture — has made every Quad member uncertain about how much the U.S. values the partnership. India, specifically, has been hit by tariffs on steel, aluminum, and textiles. The India-U.S. relationship, which multiple analysts describe as being at its lowest point in two decades, provided the backdrop to a meeting that was supposed to project unity.

Rubio's presence was meant to signal that the U.S. still cares about the Quad. His four-day India trip — the first by a Secretary of State in this administration — included bilateral meetings with Jaishankar, discussions on defense cooperation, energy security, and visa processing, and a visit to the Taj Mahal. He called the India-U.S. partnership "one of the most important in the world."

But the trust deficit runs deeper than optics. India wanted movement on H-1B visa processing times, which have ballooned under the new USCIS guidelines. India wanted clarity on tariff exemptions for IT services. India wanted a timeline for the Modi-Trump meeting that has been discussed but not scheduled. What India got was a critical minerals framework, a rare earths deal, and a maritime surveillance system.

These are not small things. They are strategic investments that will pay dividends over decades. But they are not the things that resolve the immediate friction between two countries that agree on China and disagree on almost everything else.

## The Jaishankar Signal

Jaishankar's press conference remarks were characteristically measured. He called for "deeper Indo-Pacific cooperation" and emphasized that the Quad was evolving from a security dialogue to "a full-spectrum regional architecture."

The phrase "full-spectrum" is doing heavy lifting. It means the Quad is no longer just about countering China in the South China Sea. It is about undersea cables, critical minerals, counter-terrorism, maritime law, supply-chain resilience, climate adaptation, and technology standards. It is about building the infrastructure of an alternative international order — one that does not depend on Chinese supply chains, Russian energy, or Iranian oil routes.

Whether this alternative order can be built while its members are simultaneously struggling with $98 oil, record currency depreciation, domestic inflation, and a migration crisis that is reshaping the politics of every Quad country is the question that the framework agreements cannot answer.

## What NRIs Are Watching

For the Indian diaspora, the Quad meeting's significance is both strategic and personal.

The critical minerals deal positions India as a key node in the global supply chain for the materials that power the technology sector — the same sector that employs millions of Indian-origin workers in the United States, Australia, Japan, and across the Indo-Pacific. If India can develop its rare earth processing capacity, it creates high-value manufacturing jobs that could attract returnees from the diaspora and provide an alternative to the H-1B dependency that has defined the Indian professional migration story for three decades.

The maritime surveillance initiative affects shipping routes that carry goods to and from India — including the remittance-funded imports that sustain millions of Indian households.

And Rubio's visit — set against the backdrop of the USCIS adjustment-of-status policy change, H-1B registration drops, and the Vembu "come home" controversy — raises the question that 4.8 million Indian Americans are asking: does the United States still want us?

The Quad's answer is that the U.S. wants India's minerals, India's strategic geography, India's naval cooperation, and India's market. Whether it wants India's people — the engineers, the doctors, the entrepreneurs who built the human bridge between the two countries — is a question the critical minerals framework does not address.

It is, perhaps, the most important question the Quad has not yet asked."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "India and the US Just Signed a Critical Minerals Deal and a Rare Earths Agreement at the First Quad Foreign Ministers' Meeting Since 2023. The Goal Is to Break China's Monopoly on the Materials That Power Everything.",
        "subheadline": "The Quad Foreign Ministers met in New Delhi on Monday — the first such meeting since 2023. India and the U.S. signed a critical minerals framework covering lithium, cobalt, nickel, and rare earths. A separate rare earths deal will supply processed materials to U.S. defense and tech manufacturers. A new Indo-Pacific Maritime Surveillance Cooperation initiative was launched. Jaishankar called it 'full-spectrum regional architecture.' China controls 60% of rare earth mining and 85% of processing. The Quad is trying to build an alternative supply chain — while its members struggle with $98 oil, record currency depreciation, and a trust deficit that tariffs and visa crackdowns have deepened.",
        "slug": slug2,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "The critical minerals deal positions India in the global technology supply chain — the same chain that employs millions of Indian-origin workers worldwide. If India develops rare earth processing, it creates high-value manufacturing jobs that could attract diaspora returnees and offer an alternative to H-1B dependency. But the deal's strategic framing — Rubio signing mineral agreements while USCIS restricts Green Card pathways — captures the contradiction Indian Americans live with: the U.S. wants India's geography, minerals, and naval cooperation, but is simultaneously tightening the door on the 4.8 million Indian-origin people who built the human bridge between the two countries. The Quad answers what the U.S. wants from India. It does not answer whether the U.S. still wants Indians.",
        "tags": ["Quad", "foreign ministers", "Jaishankar", "Rubio", "critical minerals", "rare earths", "India-US", "China", "lithium", "cobalt", "maritime surveillance", "Indo-Pacific", "IPMDA", "supply chain", "NRI", "H-1B", "trade", "defense"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Australia-India-Japan-US Quad seeks relevance as foreign ministers meet in New Delhi", "url": "https://www.reuters.com/world/quad-foreign-ministers-meet-new-delhi-2026-05-26/"},
            {"name": "Livemint — Quad FM Meeting LIVE: India-US critical minerals framework signed; Jaishankar, Rubio seal rare earths deal", "url": "https://www.livemint.com/news/india/quad-foreign-ministers-meeting-live-updates-2026-05-26/"},
            {"name": "IAAN Express — Quad Launches New Maritime Surveillance Initiative at New Delhi Foreign Ministers' Meeting", "url": "https://iaanexpress.com/quad-maritime-surveillance-initiative-new-delhi-2026/"},
            {"name": "Nation Press — Quad Foreign Ministers Meeting 2026: Jaishankar calls for deeper Indo-Pacific cooperation", "url": "https://nationpress.com/quad-foreign-ministers-meeting-2026/"},
            {"name": "The Indian Eye — New Delhi to host Quad Foreign Ministers on May 26 to sharpen Indo-Pacific strategy", "url": "https://theindianeye.com/new-delhi-to-host-quad-foreign-ministers-may-26-2026/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now_plus1,
        "body": body2
    })
    print(f"✓ Article 2 prepared: Quad FM meeting / critical minerals / rare earths / maritime surveillance")
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
        # US strikes Iran — no single person, use Pexels with specific terms
        img_url = fetch_pexels_image("Strait of Hormuz naval warship", "Persian Gulf naval vessel military")
        # No generic stock — if Pexels fails, leave without image
    elif i == 1:
        # Quad FM meeting — Jaishankar is the central figure
        img_url = fetch_wikipedia_person_image("Subrahmanyam Jaishankar")
        if img_url:
            img_attribution = "Wikimedia Commons"
        else:
            img_url = fetch_wikipedia_person_image("S. Jaishankar")
            if img_url:
                img_attribution = "Wikimedia Commons"
            else:
                img_url = fetch_pexels_image("diplomatic summit foreign ministers", "international diplomacy meeting flags")

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
        ["git", "commit", "-m", f"news: US strikes Iran + Quad FM critical minerals deal ({now.strftime('%Y-%m-%d %H:%M')} UTC)"],
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
