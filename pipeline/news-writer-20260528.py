#!/usr/bin/env python3
"""
Videshi News Writer — 2026-05-28 batch
Publishes 3 news articles with Wikipedia-first image sourcing.
"""

import os, json, requests, urllib.parse, uuid, time, re, subprocess
from datetime import datetime, timezone

# ── Supabase credentials ────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                k = k.replace('export ', '').strip()
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# ── Image Sourcing ──────────────────────────────────────────────────

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
    """Fetch an image from Pexels API using curl (urllib gets 403)."""
    pexels_key = None
    pexels_env = os.path.expanduser('~/workspace/.env.pexels')
    if os.path.exists(pexels_env):
        with open(pexels_env) as f:
            for line in f:
                if 'PEXELS' in line and '=' in line:
                    pexels_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break
    if not pexels_key:
        print("  ⚠ No Pexels API key found")
        return None

    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {pexels_key}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if url:
                    # Validate size
                    head = requests.head(url, timeout=10)
                    cl = int(head.headers.get('Content-Length', 0))
                    if cl > 5000:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase article-images bucket."""
    try:
        r = requests.get(image_url, timeout=20, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200:
            print(f"  ⚠ Failed to download image: HTTP {r.status_code}")
            return image_url  # fallback to direct URL
        
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if 'image' not in content_type:
            content_type = 'image/jpeg'
        
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small ({len(r.content)} bytes), skipping upload")
            return image_url

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': content_type,
            'x-upsert': 'true'
        }
        up = requests.post(upload_url, data=r.content, headers=upload_headers, timeout=30)
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {up.status_code} {up.text[:200]}")
            return image_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return image_url


def validate_image(url):
    """Validate image URL returns proper image with sufficient size."""
    if not url:
        return False
    # Block banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=', 'ccb=']
    for b in banned:
        if b in url:
            print(f"  ✗ Banned source detected: {b}")
            return False
    try:
        head = requests.head(url, timeout=10, allow_redirects=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = head.headers.get('Content-Type', '')
        cl = int(head.headers.get('Content-Length', 0))
        if 'image' in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD
        if 'image' in ct:
            return True
    except:
        pass
    return False


# ── Article publishing ──────────────────────────────────────────────

def publish_article(article):
    """Insert an article into p2_articles."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    payload = {
        'id': art_id,
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': article['slug'],
        'category': article['category'],
        'vertical': article.get('vertical', 'general'),
        'status': 'published',
        'published_at': now,
        'created_at': now,
        'sources': json.dumps(article['sources']),
        'image_url': article.get('image_url'),
        'image_caption': article.get('image_caption'),
        'image_attribution': article.get('image_attribution'),
        'score_total': article.get('score_total', 75),
        'is_featured': False,
        'tags': '{' + ','.join(article.get('tags', [])) + '}',
        'diaspora_angle': article.get('diaspora_angle', ''),
        'urgency': article.get('urgency', 'medium'),
    }

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=30
    )
    if r.status_code in (200, 201):
        print(f"  ✓ Published: {article['headline'][:60]}... (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Failed to publish: {r.status_code} {r.text[:300]}")
        return None


# ── Articles ────────────────────────────────────────────────────────

articles = []

# ────────────────────────────────────────────────────────────────────
# ARTICLE 1: Iran-US Ceasefire Framework Deal
# ────────────────────────────────────────────────────────────────────
articles.append({
    'headline': "Iran and the U.S. Have a Draft Deal to Reopen the Strait of Hormuz. India Needs It More Than Either of Them.",
    'subheadline': "A 60-day memorandum would restore shipping, lift the naval blockade, and launch nuclear talks. Pakistan brokered it. Trump has not signed it yet.",
    'slug': 'iran-us-ceasefire-deal-hormuz-60-day-mou-india-oil-imports-20260528',
    'category': 'news',
    'sources': [
        {"name": "Reuters", "url": "https://www.reuters.com/world/middle-east/iran-says-draft-us-deal-would-reopen-hormuz-shipping-end-naval-blockade-2026-05-27/"},
        {"name": "Axios", "url": "https://www.axios.com"},
        {"name": "FX Street", "url": "https://www.fxstreet.com"},
        {"name": "Reuters - Dollar falls", "url": "https://www.reuters.com"}
    ],
    'image_search_person': None,
    'image_pexels_query': 'oil tanker strait shipping',
    'image_pexels_fallback': 'cargo ship ocean sunset',
    'image_caption': 'Oil tankers in the Strait of Hormuz, a chokepoint for 20 percent of global crude shipments',
    'vertical': 'geopolitics',
    'tags': ['iran', 'ceasefire', 'hormuz', 'oil', 'gulf-indians', 'trade', 'india-foreign-policy'],
    'diaspora_angle': 'Nine million Indians live in Gulf states directly affected by the Hormuz blockade. Oil price relief would ease fuel costs for NRI families visiting India and reduce remittance friction.',
    'urgency': 'high',
    'body': """The outlines of a deal to end the three-month-old Iran-U.S. war emerged on Thursday, and the details explain why Delhi has been making frantic calls to both Washington and Tehran for weeks.

According to an Axios report citing two U.S. officials, American and Iranian negotiators have agreed on a 60-day memorandum of understanding that would extend the ceasefire, reopen commercial shipping through the Strait of Hormuz to pre-war levels within 30 days, and launch direct negotiations over Iran's nuclear program. The agreement awaits President Donald Trump's final signature.

## What the Draft Says

Iran's state television published what it described as an unofficial framework. Under its terms, Iran would restore commercial vessel traffic through the strait within a month. The United States would withdraw military forces from Iran's vicinity and lift the naval blockade that has choked global shipping since February.

The framework excludes military vessels and envisions Iran managing ship traffic through the strait in cooperation with Oman. Tehran said it would take no steps without "tangible verification." If a final agreement is reached within 60 days, it could be approved as a binding United Nations Security Council resolution.

Pakistan played the central mediating role in the indirect talks that produced the framework — a diplomatic win for Islamabad and a sign of how deeply the Gulf conflict has reshaped South Asian diplomacy.

## Why India Cannot Wait

India imports roughly 85 percent of its crude oil, and the Strait of Hormuz handles about 20 percent of global crude shipments. Since the war began on February 28, when U.S. and Israeli forces struck Iranian targets and Iran retaliated with missiles and drones, oil prices have surged past $110 a barrel. Indian petrol prices have crossed ₹100 in most cities after four fuel-price hikes in two weeks.

The blockade has also disrupted non-oil trade. India's basmati rice exports crashed 27 percent as Gulf trade routes choked. IndiGo and Air India cut up to 22 percent of domestic flights because of jet fuel costs. The Reserve Bank of India is watching imported inflation closely, with consumer prices already above the central bank's comfort zone.

For the nearly 9 million Indians living in Gulf states — the largest diaspora bloc in the region — the shipping disruption has meant delayed remittances, paused construction projects, and an ambient sense of danger underscored this week when Iranian drones and a ballistic missile targeted a U.S. base in Kuwait, where nearly a million Indians live.

## The Fragility Problem

The framework arrived hours after the latest ceasefire violation. U.S. Central Command said it shot down five Iranian attack drones and struck a ground control station near Bandar Abbas that was about to launch a sixth. Iran's Revolutionary Guard Corps then fired a ballistic missile at the U.S. base in Kuwait, which Kuwaiti forces intercepted.

Both sides described their actions as defensive. The U.S. called its strikes "measured" and "intended to maintain the ceasefire." Iran said any repeat would invite a "more decisive response." Kuwait condemned the attack and demanded an immediate halt.

This is the second flare-up this week, and it coincided with Eid al-Adha celebrations across the region — a reminder that the ceasefire exists more on paper than on the ground.

## What the Markets Heard

Financial markets responded instantly to the Axios report. Oil prices reversed course and traded lower. The U.S. dollar fell against major currencies, with the euro gaining 0.27 percent and the dollar index dropping 0.29 percent to 99.02. Indian markets were closed on Thursday for the Eid holiday, but the rupee and Sensex are likely to react on Friday.

For Indian policymakers, the math is straightforward. Every dollar added to the oil price costs India approximately $2 billion in additional import bills annually. If the MOU holds and Hormuz reopens, crude prices could ease by $15-20 a barrel within weeks — translating to ₹5-8 per liter in fuel price relief and a significant easing of the current account deficit.

## What Comes Next

Trump has not signed. The framework is unofficial. Both militaries are still firing at each other. But the mere existence of a written agreement — with a timeline, a verification mechanism, and a path to the UN Security Council — is the most concrete progress since the April ceasefire that never quite held.

India's external affairs ministry has not commented on the draft, but Delhi's position is well known: India wants the strait open, fuel prices down, and its Gulf diaspora safe. Whether Trump signs may depend on domestic politics as much as geopolitics. For the million Indians in Kuwait who heard a ballistic missile intercepted overhead this week, the 60-day clock cannot start soon enough."""
})

# ────────────────────────────────────────────────────────────────────
# ARTICLE 2: India's First Hydrogen Train
# ────────────────────────────────────────────────────────────────────
articles.append({
    'headline': "India Just Approved Its First Hydrogen-Powered Passenger Train. It Runs on Water Vapour.",
    'subheadline': "The 10-coach train will serve 2,600 passengers daily on a Haryana route, joining Germany, Japan, and China in the hydrogen rail club.",
    'slug': 'india-first-hydrogen-train-jind-sonipat-green-railways-20260528',
    'category': 'news',
    'sources': [
        {"name": "APAC News Network", "url": "https://apacnewsnetwork.com/2026/05/indias-first-hydrogen-powered-passenger-train-gets-green-signal-from-railways-ministry/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com"},
        {"name": "Latestly", "url": "https://www.latestly.com"},
        {"name": "Enerside Media", "url": "https://enersidermedia.com"}
    ],
    'image_search_person': None,
    'image_pexels_query': 'Indian railway train modern station',
    'image_pexels_fallback': 'train railway station India',
    'image_caption': 'Indian Railways is betting on hydrogen fuel cells to replace diesel on non-electrified routes',
    'vertical': 'infrastructure',
    'tags': ['railways', 'hydrogen', 'green-energy', 'infrastructure', 'india-modernization', 'net-zero'],
    'diaspora_angle': 'The hydrogen train sits alongside Vande Bharat and the bullet train as evidence of infrastructure modernization NRIs hear about but rarely see. Green hydrogen investment opportunities may emerge as India targets below-₹100/kg costs.',
    'urgency': 'medium',
    'body': """India's Railway Board has approved the launch of the country's first hydrogen-powered passenger train, clearing the final regulatory hurdle for a project that turns water vapour into a selling point and diesel into a relic.

The train — a 10-coach Diesel Electric Multiple Unit retrofitted with 1,200 kilowatt hydrogen fuel cells — will operate on the 89-kilometre Jind-Sonipat route in Haryana, serving over 2,600 passengers daily with two round trips at speeds up to 75 kilometres per hour. Its only emission is water vapour.

## How It Works

Unlike conventional trains that burn diesel to generate electricity for traction motors, the hydrogen DEMU uses fuel cells that combine hydrogen and oxygen in an electrochemical reaction. The process produces electricity, heat, and water — no carbon dioxide, no particulate matter, no nitrogen oxides.

The 1,200 kW system uses Distributed Power Rolling Stock technology, distributing propulsion across multiple coaches rather than relying on a single locomotive. The Research Designs and Standards Organisation completed oscillation trial runs in March 2026, and the Railway Board's approval followed technical safety evaluations that included hydrogen leak detection systems and round-the-clock monitoring protocols.

## India Joins an Elite Club

With this approval, India becomes the fifth country to operate hydrogen-powered passenger trains, joining Germany, which launched the world's first hydrogen train in 2018, along with Sweden, Japan, and China. Germany's Coradia iLint, built by Alstom, runs on routes in Lower Saxony. China began hydrogen tram operations in Foshan in 2019 and is expanding to intercity routes.

India's version is notable because it is indigenously developed — not imported or licensed — and is part of the National Green Hydrogen Mission, a ₹19,744 crore initiative launched in 2023 to position India as a global green hydrogen hub.

## The Economics Are Complicated

The approval is a technical achievement, but the economics are harder. Green hydrogen — produced by splitting water using renewable electricity — currently costs between ₹300 and ₹400 per kilogram in India, roughly three to four times the cost of diesel on an energy-equivalent basis. The government's target is to bring green hydrogen costs below ₹100 per kilogram by 2030, a target that requires massive scaling of electrolyser manufacturing and renewable energy capacity.

The Jind-Sonipat route was chosen partly because a hydrogen production plant in Jind is nearing final commissioning. Without co-located production, transporting hydrogen to fuelling points would add significant cost and logistical complexity.

Industry analysts note that the real value of the project lies in proving the technology at scale on Indian railways, which operates the fourth-largest rail network in the world. Indian Railways consumed approximately 2.6 billion litres of diesel in the 2023-24 fiscal year. Converting even a fraction of non-electrified routes to hydrogen could significantly reduce the railway's carbon footprint and its ₹30,000 crore annual diesel bill.

## The Bigger Push

The hydrogen train is part of a broader ₹1.53 lakh crore railway investment wave approved in the current fiscal year, covering more than 100 projects across 6,000 kilometres of network expansion. The Railway Ministry reported a 56 percent increase in project approvals and a 110 percent rise in capital spending year-on-year.

For Indian Railways, the calculation is both environmental and strategic. About 40 percent of India's rail network remains non-electrified, mostly in rural and semi-urban stretches where overhead wiring is expensive and geographically difficult. Hydrogen offers a zero-emission alternative without the infrastructure cost of electrification — if the fuel economics come down.

## What NRIs Should Watch

For the diaspora, the hydrogen train is a signal of the kind of India they often hear about but rarely see firsthand. It sits alongside the Vande Bharat semi-high-speed trains and the Mumbai-Ahmedabad bullet train project as evidence that Indian infrastructure is no longer decades behind the rest of the world.

The commercial question — whether hydrogen trains make financial sense at scale before the Green Hydrogen Mission brings costs down — will determine whether this is a one-off showcase or the beginning of a transformation. The trial runs start on an 89-kilometre stretch in Haryana. The answer will determine whether they reach the rest of the country's 68,000 kilometres of railway track."""
})

# ────────────────────────────────────────────────────────────────────
# ARTICLE 3: India Forms Committee on Illegal Immigration
# ────────────────────────────────────────────────────────────────────
articles.append({
    'headline': "Modi Just Created a Committee to Study How Illegal Immigration Changed India's Demographics. It Has One Year.",
    'subheadline': "A retired Supreme Court judge will lead the panel. It can recommend detention and deportation systems. The timing — days after Rubio's visit — is not coincidental.",
    'slug': 'india-high-level-committee-illegal-immigration-demographics-naolekar-20260528',
    'category': 'news',
    'sources': [
        {"name": "VisaVerge", "url": "https://www.visaverge.com/news/modi-government-forms-high-level-committee-to-study-illegal-immigration-and-demography-change/"},
        {"name": "DevDiscourse", "url": "https://www.devdiscourse.com"},
        {"name": "SCC Online", "url": "https://www.scconline.com"},
        {"name": "Press Information Bureau", "url": "https://pib.gov.in"}
    ],
    'image_search_person': 'Amit Shah',
    'image_pexels_query': None,
    'image_pexels_fallback': None,
    'image_caption': 'Union Home Minister Amit Shah announced the committee, calling illegal infiltration a challenge to India\'s present and future',
    'vertical': 'immigration',
    'tags': ['immigration', 'demographics', 'amit-shah', 'nri-world', 'deportation', 'border-security', 'rubio-india'],
    'diaspora_angle': 'India cracking down on illegal immigration mirrors its argument to the U.S. about protecting legal H-1B and student pathways. NRIs on both sides of the immigration debate will see parallels with their own visa battles.',
    'urgency': 'high',
    'body': """India's government has created a committee with the power to reshape how the country identifies, detains, and deports people it classifies as illegal immigrants. The timing — announced two days after U.S. Secretary of State Marco Rubio left Delhi — places it at the intersection of two countries simultaneously tightening their borders.

Union Home Minister Amit Shah announced the formation of the High-Level Committee on Demographic Change on May 26, 2026, through the Press Information Bureau and social media. The committee will study how illegal immigration has altered population patterns across India and recommend enforcement mechanisms.

## Who Is on the Panel

The committee is chaired by retired Supreme Court Justice Prakash Prabhakar Naolekar. Its members include the Census Commissioner of India, Durga Shankar Mishra (a former Urban Affairs Secretary), Balaji Srivastava (a former Delhi Police Commissioner), Dr. Shamika Ravi (an economist and former member of the Prime Minister's Economic Advisory Council), and the Joint Secretary for Foreigners in the Ministry of Home Affairs, who will serve as member secretary.

The composition is deliberate. A former Supreme Court judge gives the panel judicial authority. A former police commissioner brings enforcement perspective. An economist provides demographic modelling capacity. The Census Commissioner connects the work to India's population data infrastructure.

## What It Can Do

The committee's mandate extends far beyond a population study. It will conduct a scientific assessment of demographic shifts caused by "illegal infiltration" and "unnatural causes" across religious and social communities. It will recommend institutional mechanisms to strengthen borders and stabilize populations. Most significantly, it will propose a permanent operational mechanism for identifying, detaining, and deporting illegal immigrants.

Shah framed the issue in security terms: "Infiltration and other reasons causing unnatural demographic change pose a very significant challenge to the present and future of any nation."

The committee has one year to deliver its report, with a possible six-month extension. An Updated Deportation Framework released in 2026 sets 30-to-90-day verification timelines for suspected foreign nationals — suggesting the government wants a standing system rather than case-by-case action.

## The Independence Day Promise

The committee fulfils a commitment Prime Minister Narendra Modi made during his Independence Day address on August 15, 2025, when he proposed a formal study of immigration-driven demographic change. That speech was widely seen as a signal that the BJP intended to make illegal immigration — particularly from Bangladesh and Myanmar — a central governance issue in its third term.

India shares a 4,096-kilometre border with Bangladesh, much of it porous. The government estimates millions of undocumented Bangladeshi migrants live in India, concentrated in West Bengal, Assam, and the northeast. The Assam National Register of Citizens exercise in 2019 excluded 1.9 million people, though the follow-up process stalled amid legal challenges and political controversy.

## The Rubio Connection

The committee's announcement came during a consequential week for immigration diplomacy. Rubio visited Delhi from May 23-26 and discussed immigration during a joint press conference with External Affairs Minister S. Jaishankar on May 24.

Rubio described Washington's immigration crackdown as global rather than India-specific: "The modernization of our migration system is not focused on India specifically. We've had a migratory crisis in the US — over 20 million people illegally entered the US over the last few years."

Jaishankar responded with a line India has repeated in every recent migration conversation: "While we cooperate to deal with illegal and irregular mobility, our expectation is that legal mobility would not be adversely impacted."

That distinction — illegal immigration bad, legal immigration protected — is India's position at home and abroad. The committee's domestic mandate to crack down on illegal infiltration mirrors the argument India makes to Washington about protecting H-1B workers and students.

## What This Means for the Diaspora

For Indian Americans and NRIs, the committee creates a two-track reality. India is simultaneously arguing that the United States should protect legal Indian immigration while launching its own enforcement mechanism against illegal immigration from its neighbours.

The USCIS directive issued on May 22 — requiring foreign nationals seeking Green Cards to leave the U.S. and apply from home — has already unsettled the Indian American community. Jaishankar's public pushback on that policy during Rubio's visit showed how seriously Delhi takes the legal-immigration issue.

The domestic committee will likely generate headlines that read differently in Assam than they do in Silicon Valley. For the diaspora, the key question is whether India's crackdown on illegal immigration strengthens or weakens its moral authority when arguing for legal immigration protections abroad.

The committee has one year. The debate will last much longer."""
})


# ── Main Execution ──────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Videshi News Writer — 2026-05-28 Batch")
    print("=" * 60)
    
    for i, article in enumerate(articles, 1):
        print(f"\n--- Article {i}/{len(articles)}: {article['headline'][:50]}... ---")
        
        # Image sourcing
        img_url = None
        img_attribution = None
        
        # Step 1: Try Wikipedia for person articles
        person = article.get('image_search_person')
        if person:
            print(f"  Trying Wikipedia for '{person}'...")
            img_url = fetch_wikipedia_person_image(person)
            if img_url:
                img_attribution = "Wikimedia Commons"
        
        # Step 2: Try Pexels as fallback
        if not img_url and article.get('image_pexels_query'):
            print(f"  Trying Pexels for '{article['image_pexels_query']}'...")
            img_url = fetch_pexels_image(article['image_pexels_query'], article.get('image_pexels_fallback'))
            if img_url:
                img_attribution = "Pexels"
        
        # Step 3: Upload to Supabase if we found an image
        if img_url:
            if validate_image(img_url):
                filename = f"{article['slug']}.jpg"
                final_url = upload_to_supabase_storage(img_url, filename)
                article['image_url'] = final_url
                article['image_attribution'] = img_attribution
            else:
                print(f"  ⚠ Image validation failed, proceeding without image")
                article['image_url'] = None
                article['image_attribution'] = None
        else:
            print(f"  ⚠ No image found, proceeding without image")
            article['image_url'] = None
            article['image_attribution'] = None
        
        # Publish
        art_id = publish_article(article)
        if art_id:
            print(f"  ✓ Article {i} published successfully")
        else:
            print(f"  ✗ Article {i} failed to publish")
        
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("Batch complete.")
    print("=" * 60)


if __name__ == '__main__':
    main()
