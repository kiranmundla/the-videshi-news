#!/usr/bin/env python3
"""
Videshi News Writer — June 2, 2026 batch
Publishes 3 articles in the 'news' category.
"""
import os, json, sys, uuid, re, time
from datetime import datetime, timezone
import requests, urllib.parse

# ── Load env ──────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, _, val = line.partition('=')
            key = key.replace('export ', '').strip()
            val = val.strip().strip('"').strip("'")
            os.environ.setdefault(key, val)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# ── Image helpers ─────────────────────────────────────────────────────────────
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

def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels API using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('original')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Check image URL returns 200 with image content-type and >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Sometimes HEAD doesn't return Content-Length, try GET with stream
        if r.status_code == 200 and 'image' in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, timeout=15,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Download failed: status={r.status_code}, size={len(r.content)}")
            return None
        ct = r.headers.get('Content-Type', 'image/jpeg')
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        r2 = requests.post(upload_url, data=r.content, headers={
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': ct,
            'x-upsert': 'true'
        }, timeout=30)
        if r2.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {r2.status_code} {r2.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None

# ── Supabase insert ──────────────────────────────────────────────────────────
def insert_article(article):
    """Insert article into p2_articles."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]['id'] if isinstance(data, list) else data.get('id')
        print(f"  ✓ Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None

# ── Articles ─────────────────────────────────────────────────────────────────
articles = [
    # ── Article 1: BrahMos Vietnam Deal ──
    {
        "headline": "India Just Signed a BrahMos Deal With Vietnam. Three Southeast Asian Nations Now Carry the Missile.",
        "subheadline": "Defence exports hit a record ₹38,424 crore as Operation Sindoor drives unprecedented global demand for Indian weapons systems.",
        "slug": "india-brahmos-vietnam-deal-defense-exports-record-38424-crore-southeast-asia-20260602",
        "category": "news",
        "status": "published",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        
        "sources": json.dumps([
            "Reuters — 'India says signed BrahMos missile deal with Vietnam' (May 30, 2026)",
            "IANS — 'Brahmos cruise missile deal with Vietnam already signed: Defence Secretary' (May 30, 2026)",
            "The Hindu Business Line — 'India signs BrahMos missile deal with Vietnam' (May 30, 2026)",
            "Bhaskar English — 'India Defence Exports Surge: BrahMos, Akash, Netra Deals Worth ₹21K Cr' (June 1, 2026)"
        ]),
        "body": """India has signed an agreement to supply its BrahMos supersonic cruise missiles to Vietnam, Defence Secretary Rajesh Kumar Singh confirmed at the Shangri-La Dialogue in Singapore on Saturday. A similar deal with Indonesia is in the "final stages," Singh said, marking the third Southeast Asian nation to acquire the weapon system after the Philippines, which took delivery of its first batch in 2024.

## The Deal

The Vietnam agreement is valued at approximately ₹6,000 crore ($629 million) and includes training, spare parts, and logistical support. Vietnam's package focuses on land-based coastal defence batteries designed for rapid anti-ship strikes — a direct response to its maritime disputes in the South China Sea.

"My understanding is that with both Indonesia and with Vietnam, the deal is in the final stages. In fact, for Vietnam, I understand that it has already been signed, probably not publicly announced," Singh told delegates in Singapore.

Indonesia, which confirmed a preliminary framework with India in March, is reportedly pursuing the naval variant that can be launched from frigates and submarines. The deal with Jakarta is estimated at ₹3,600 crore and is in the final approval stage.

## Record Defence Exports

The BrahMos deals are the centrepiece of a broader transformation in India's defence export profile. According to the Ministry of Defence, India's defence exports reached a record ₹38,424 crore in FY 2025-26 — up 62 per cent from the previous year. India now exports defence equipment to more than 100 countries, with the United States, France, and Armenia among the largest buyers.

The US alone imports systems and components worth $2.8 billion, supplied to major contractors including Boeing and Lockheed Martin. Armenia has signed a ₹6,100 crore contract for the Akash missile system, a surface-to-air platform.

In total, BrahMos-related export deals worth approximately ₹12,500 crore have been signed with the Philippines, Vietnam, and at least two other undisclosed nations.

## The Operation Sindoor Effect

Much of the recent global interest can be traced to Operation Sindoor, India's military operation earlier this year. The combat deployment of Indian-made weapons — BrahMos, Akash, loitering munitions, and the Netra airborne early warning system — gave the world its first real-time look at India's indigenous defence technology under actual battlefield conditions.

Several nations have since expressed interest in purchasing these systems. Deals worth more than ₹21,000 crore across multiple weapon platforms are now in various stages of negotiation.

## What It Means for the Indo-Pacific

India's defence export push is not purely commercial. It is a deliberate strategic play to position New Delhi as a "friendly defence partner" to nations navigating China's growing military assertiveness in the South China Sea and Indian Ocean.

"We treat you all as friendly foreign countries with whom we can share advanced defence technology," Singh told the gathering in Singapore.

The BrahMos missile itself — co-developed with Russia, capable of flying at nearly Mach 3 with a strike range exceeding 400 kilometres — gives smaller nations a credible deterrent against high-value naval targets. For countries like Vietnam and the Philippines, which face maritime disputes with China, the calculus is straightforward: the missile changes the risk equation for any adversary contemplating incursion.

## The Diaspora Angle

The expansion of India's defence industrial base has a direct impact on the Indian diaspora. Thousands of NRI engineers and defence professionals work in the US and European defence sectors. The deepening US-India defence industrial partnership — with $2.8 billion in components flowing from India to American defence giants — creates a two-way talent and technology corridor that benefits diaspora professionals on both sides.

The government has set a defence export target of ₹50,000 crore by 2029-30. From a base of just ₹1,522 crore in 2016-17, that represents a more than 25-fold increase in under a decade — a trajectory that would have been unthinkable a generation ago.""",
        "image_search_person": "BrahMos missile",
        "image_search_pexels": "military missile launch defense",
        "image_search_pexels_fallback": "supersonic cruise missile"
    },

    # ── Article 2: Rafale ₹3.25 Lakh Crore LoR ──
    {
        "headline": "India Just Sent France the Paperwork for 114 Rafale Jets. The Bill Is ₹3.25 Lakh Crore.",
        "subheadline": "The Letter of Request for the country's largest-ever defence acquisition comes weeks before Modi's expected visit to Paris. Ninety-four of the jets will be built in India.",
        "slug": "india-114-rafale-jets-letter-of-request-france-325-lakh-crore-make-in-india-20260602",
        "category": "news",
        "status": "published",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        
        "sources": json.dumps([
            "The Hindu Business Line — 'India Issues Letter of Request to France for ₹3.25-Lakh-Crore Rafale Deal' (June 1, 2026)",
            "Devdiscourse — 'India Seeks to Boost Air Power with Massive Rafale Deal with France' (June 1, 2026)",
            "Whispersinthecorridors.in — 'Indian Navy Signs ₹63,000 Cr Deal for 26 Rafale-M Fighters' (June 1, 2026)",
            "Breaking Defense — 'India, France increase defense ties with new Rafale jet and submarine buys'"
        ]),
        "body": """India has formally issued a Letter of Request to France for the procurement of 114 Rafale fighter aircraft in a government-to-government deal estimated at ₹3.25 lakh crore — the largest defence acquisition in Indian history.

According to Defence Ministry sources, the Acquisition Wing sent the request to Paris recently, initiating the next phase of negotiations for a purchase that will reshape the Indian Air Force's combat fleet for the next three decades.

## The Numbers

Of the 114 aircraft, 94 are expected to be manufactured in India through a partnership between French aerospace major Dassault Aviation and an Indian company, in line with the 'Make in India' initiative. The remaining 20 would be delivered directly from France.

France is expected to respond within two to three months. Both countries are aiming to conclude the agreement within the coming year. The deal comes ahead of Prime Minister Narendra Modi's expected visit to France later this month, where the Rafale programme is certain to dominate bilateral discussions.

The Indian Air Force currently operates 36 Rafale jets, acquired under an earlier ₹59,000 crore deal signed in 2016. The new order would bring India's total Rafale fleet to 150 aircraft — making it one of the largest Rafale operators in the world alongside France itself.

## The Navy Gets Its Own

Separately, India and France have signed an Inter-Governmental Agreement for the procurement of 26 Rafale-M (Marine) fighters for the Indian Navy, valued at approximately ₹63,000 crore. The naval order includes 22 single-seat and 4 twin-seat variants, making India the first international operator of the Rafale's carrier-based version.

The deal, signed by Defence Minister Rajnath Singh and his French counterpart Sébastien Lecornu, includes training, flight simulators, weapons with transfer of technology (including integration of India's Astra beyond-visual-range missile), five-year performance-based logistics, and maintenance facilities to be established in India.

The Rafale-M jets will operate from India's two aircraft carriers — INS Vikrant and INS Vikramaditya. Deliveries are expected to begin in mid-2028 and continue through 2030.

## Why This Matters

The IAF's fighter squadron strength has been shrinking for years. Against a sanctioned strength of 42 squadrons, the force currently operates roughly 30 — a gap that defence planners have repeatedly flagged as dangerous, particularly given the two-front threat from China and Pakistan.

The 114-jet order under the Multi-Role Fighter Aircraft (MRFA) programme is designed to address this gap with a proven 4.5-generation platform. The Rafale's omni-role capability — air superiority, deep strike, nuclear deterrence, maritime attack, and reconnaissance — makes it the most versatile fighter in India's inventory.

The emphasis on domestic manufacturing is significant. Setting up a Rafale production line in India is expected to create thousands of jobs in the domestic aerospace sector, from Tier 1 suppliers to the MSME ecosystem. This aligns with the broader goal of reducing import dependency: the recently released Defence Acquisition Procedure (DAP) 2026 has raised indigenous content requirements from 50 per cent to 60 per cent.

## The Strategic Partnership With France

The Rafale deals cement France as one of India's most consequential defence partners. Beyond fighter jets, India operates six Scorpene-class submarines built with French Naval Group technology, and three more are under negotiation. The two countries are also collaborating on the Jaitapur nuclear project, clean energy, semiconductor development, and a bilateral trade relationship exceeding €15 billion.

The deepening of defence ties reflects a deliberate Indian strategy: diversifying its weapons supply chain away from historical dependency on Russia while building technology partnerships that strengthen the domestic industrial base.

## What NRIs Should Watch

For the Indian diaspora, the defence procurement wave has broader economic implications. The Rafale production line will require advanced manufacturing capabilities — precision machining, avionics, composite materials — that could create opportunities for Indian-origin professionals in the global aerospace industry. French defence major Dassault has signalled interest in establishing research centres in India, potentially creating a new corridor of aerospace talent exchange similar to what exists in the IT sector.""",
        "image_search_person": "Rafale fighter jet",
        "image_search_pexels": "Rafale fighter jet military aircraft",
        "image_search_pexels_fallback": "fighter jet aircraft carrier navy"
    },

    # ── Article 3: Hegseth Praises India at Shangri-La ──
    {
        "headline": "The US Defence Secretary Just Called India a 'Powerful' Military Nation. He Said It at Asia's Top Security Forum.",
        "subheadline": "Pete Hegseth praised India's military modernisation and industrial capacity at the Shangri-La Dialogue while calling on Asian allies to raise defence spending to 3.5% of GDP.",
        "slug": "hegseth-india-powerful-military-shangri-la-dialogue-defense-spending-35-percent-gdp-20260602",
        "category": "news",
        "status": "published",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        
        "sources": json.dumps([
            "News Dive — 'Amid US Concerns Over China, Hegseth Highlights India's Military Modernization' (May 31, 2026)",
            "The Indian Eye — 'India reaffirms defence cooperation with US at Shangri-La Dialogue' (May 30, 2026)",
            "IANS — 'Defence Secretary discusses strengthening ties with Defence Ministers of Singapore, New Zealand' (May 31, 2026)",
            "Ainvest — 'India Emerges as Go-To Arms Supplier for Southeast Asian Nations' (June 1, 2026)"
        ]),
        "body": """US Secretary of Defense Pete Hegseth described India as a "powerful" nation that is "in the process of modernising its military capabilities" during his keynote address at the Shangri-La Dialogue in Singapore on Saturday — the most prominent annual security forum in Asia.

## What Hegseth Said

Hegseth highlighted India's "substantial industrial and logistical infrastructure necessary for conducting advanced military operations" and expressed the US commitment to co-production initiatives with New Delhi to enhance joint military capabilities.

His remarks came within a broader call for Asian allies to raise defence spending to 3.5 per cent of GDP — a significant increase from the current levels of most nations in the region, including India, which spends approximately 1.9 per cent of GDP on defence but is aiming to reach 2.5 per cent over the next five years.

The US defence chief assessed ties with Japan, South Korea, ASEAN nations, and Australia alongside India, reiterating Washington's position that the Indo-Pacific is the world's most important strategic region. But his praise for India was notably specific: where other nations were mentioned in the context of alliances and treaties, India was singled out for its independent military industrial capacity and its role in "maintaining a balanced power dynamic" in the Indian Ocean.

## India's Diplomatic Blitz in Singapore

India's delegation at the Dialogue was led by Defence Secretary Rajesh Kumar Singh, who conducted an unusually intensive schedule of bilateral meetings. Over three days, Singh met with defence officials from more than ten countries, including the US, Singapore, New Zealand, Sweden, the Netherlands, and several ASEAN nations.

Singh articulated India's vision for a "stable, secure, and inclusive Indo-Pacific" in a policy address attended by think tanks, academia, and the Indian High Commissioner to Singapore, Shilpak Ambule.

Key bilateral discussions focused on maritime security cooperation, military exchange programmes, information-sharing mechanisms, and defence technology partnerships. The Singapore meeting with President Tharman Shanmugaratnam, held at the Istana reception, underscored the strategic depth of India-Singapore ties, recently elevated to a Comprehensive Strategic Partnership.

## Why This Matters Now

Hegseth's remarks land at a moment when India's defence posture is undergoing a visible transformation. In the past week alone, India signed a BrahMos missile deal with Vietnam, issued a ₹3.25 lakh crore Letter of Request for 114 Rafale jets, and saw the Navy sign a ₹63,000 crore agreement for 26 Rafale-M carrier-based fighters.

Defence exports hit a record ₹38,424 crore in FY 2025-26. Operation Sindoor — the military operation earlier this year — gave the world a live demonstration of India's indigenous weapons capability, driving unprecedented international demand for BrahMos, Akash, and Netra systems.

The convergence of these developments at the Shangri-La Dialogue was not accidental. India used the forum to signal that it is no longer merely a defence importer. It is now a manufacturer, exporter, and strategic partner willing to share advanced military technology with "friendly foreign countries."

## The Context: China

The subtext of the entire Dialogue was China. Beijing sent only a low-profile delegation, with senior officials conspicuously absent from key ministerial sessions. Analysts interpreted the move as an attempt to avoid tough questions about its military build-up in the South China Sea, its expanding presence along the India-China border in Ladakh, and the construction of new military villages in Bhutanese territory near the Doklam plateau.

Hegseth's pointed messaging — praising India while calling on Asian nations to spend more on defence — reflects Washington's evolving strategy of building a networked coalition of capable regional powers rather than relying solely on hub-and-spoke alliance structures.

For India, the calculus is straightforward: deeper engagement with the US and ASEAN on defence, without a formal alliance, while building the domestic industrial base to sustain strategic autonomy. The Shangri-La meetings suggest that formula is gaining traction.

## The Diaspora Connection

Indian-origin professionals are increasingly embedded in the US defence ecosystem. The $2.8 billion in components India already supplies to Boeing and Lockheed Martin represents just the beginning of a co-production relationship that could expand dramatically as the Rafale production line comes online and defence technology transfer agreements multiply. For NRIs working in engineering, aerospace, and technology, the deepening US-India defence partnership is creating a talent bridge that did not exist a decade ago.""",
        "image_search_person": "Pete Hegseth",
        "image_search_pexels": "military defense forum conference",
        "image_search_pexels_fallback": "international security summit diplomacy"
    }
]

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    published = 0
    for i, art in enumerate(articles):
        print(f"\n{'='*60}")
        print(f"Article {i+1}: {art['headline'][:70]}...")
        print(f"{'='*60}")

        # Extract search hints
        person = art.pop('image_search_person', None)
        pexels_q = art.pop('image_search_pexels', None)
        pexels_fb = art.pop('image_search_pexels_fallback', None)

        # Image sourcing
        img_url = None
        img_attribution = None

        # Try Wikipedia for person/topic
        if person:
            wiki_url = fetch_wikipedia_person_image(person)
            if wiki_url and validate_image(wiki_url):
                # Upload to Supabase for permanence
                fname = f"{art['slug']}.jpg"
                uploaded = upload_to_supabase_storage(wiki_url, fname)
                if uploaded:
                    img_url = uploaded
                    img_attribution = "Wikimedia Commons"
                else:
                    img_url = wiki_url
                    img_attribution = "Wikimedia Commons"

        # Fallback to Pexels
        if not img_url and pexels_q:
            pexels_url = fetch_pexels_image(pexels_q, pexels_fb)
            if pexels_url and validate_image(pexels_url):
                fname = f"{art['slug']}.jpg"
                uploaded = upload_to_supabase_storage(pexels_url, fname)
                if uploaded:
                    img_url = uploaded
                    img_attribution = "Pexels"
                else:
                    img_url = pexels_url
                    img_attribution = "Pexels"

        if img_url:
            art['image_url'] = img_url
            if img_attribution:
                art['image_attribution'] = img_attribution
            print(f"  ✓ Final image: {img_url[:80]}...")
        else:
            print(f"  ⚠ No image found — publishing without image (better than wrong image)")

        # Insert
        art_id = insert_article(art)
        if art_id:
            published += 1
        else:
            print(f"  ✗ FAILED to publish article {i+1}")

        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Published {published}/{len(articles)} articles")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
