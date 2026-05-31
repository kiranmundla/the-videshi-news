#!/usr/bin/env python3
"""The Videshi — News Writer (2026-05-31 batch)"""

import json, os, re, sys, time, uuid, urllib.parse, urllib.request
from datetime import datetime, timezone

# ── Supabase ──
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:]
            k, _, v = line.partition('=')
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k.strip(), v)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SB_URL = os.environ.get('SUPABASE_URL', '')
SB_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SB_KEY,
    'Authorization': f'Bearer {SB_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def sb_post(table, payload):
    url = f"{SB_URL}/rest/v1/{table}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=HEADERS, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  ⚠ Supabase POST error: {e}")
        return None

def sb_patch(table, filters, payload):
    qs = '&'.join(f"{k}={v}" for k, v in filters.items())
    url = f"{SB_URL}/rest/v1/{table}?{qs}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=HEADERS, method='PATCH')
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  ⚠ Supabase PATCH error: {e}")
        return None

# ── Image sourcing ──
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        req = urllib.request.Request(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run([
                'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape'
            ], capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0]['src']['large2x']
                print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Verify URL returns valid image with Content-Length > 5000."""
    if not url:
        return False
    try:
        req = urllib.request.Request(url, method='HEAD', headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        with urllib.request.urlopen(req, timeout=10) as r:
            ct = r.headers.get('Content-Type', '')
            cl = int(r.headers.get('Content-Length', 0))
            if 'image' in ct and cl > 5000:
                return True
            elif 'image' in ct and cl == 0:
                # Some servers don't return Content-Length for HEAD
                return True
    except Exception as e:
        print(f"  ⚠ Image validation failed for {url[:60]}: {e}")
    return False

def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        req = urllib.request.Request(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        with urllib.request.urlopen(req, timeout=20) as r:
            img_data = r.read()
            content_type = r.headers.get('Content-Type', 'image/jpeg')
        
        if len(img_data) < 5000:
            print(f"  ⚠ Image too small ({len(img_data)} bytes), skipping upload")
            return None
        
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            'Authorization': f'Bearer {SB_KEY}',
            'Content-Type': content_type,
            'x-upsert': 'true'
        }
        req2 = urllib.request.Request(upload_url, data=img_data, headers=upload_headers, method='POST')
        with urllib.request.urlopen(req2, timeout=30) as r2:
            pass
        
        public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
        return public_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return None

# ── Articles ──
ARTICLES = [
    {
        "headline": "India's Trade Deal With Oman Goes Live Tomorrow. Here Is What Changes for Exporters and Workers in the Gulf.",
        "subheadline": "The CEPA eliminates duties on 98 percent of Indian exports, raises mobility quotas for professionals, and opens Oman's services market to Indian companies for the first time.",
        "slug": "india-oman-cepa-trade-deal-live-june-1-exports-professionals-gulf-nri-20260531",
        "category": "news",
        "sources": "Outlook Business, Directorate General of Foreign Trade (DGFT), Ministry of Commerce press release, NationPress, Devdiscourse",
        "image_search_person": None,
        "image_pexels_query": "Muscat Oman port trade",
        "image_pexels_fallback": "shipping container port Gulf",
        "image_attribution": "Pexels",
        "body": """India's Comprehensive Economic Partnership Agreement with Oman takes effect on June 1, opening the Gulf nation's market to Indian goods on terms that New Delhi has spent two years negotiating. The deal, signed during Prime Minister Narendra Modi's visit to Muscat in December 2025, eliminates tariffs on 98.08 percent of Oman's tariff lines — covering 99.38 percent of India's export value to the country.

For Indian exporters, the numbers translate into immediate relief. Duties of up to 5 percent on goods worth approximately $3.64 billion will disappear overnight. The sectors that stand to gain the most — textiles, gems and jewellery, pharmaceuticals, leather, engineering goods, automobiles, and medical devices — are precisely the labour-intensive industries that India has been trying to push into Gulf markets for years.

## What the Deal Actually Covers

The Directorate General of Foreign Trade confirmed on Friday that electronic preferential certificates of origin will be issued through the Trade Connect ePlatform starting June 1. Exporters will need to select "India Oman CEPA (Agency Issued)" when applying, and the system will generate QR-coded digital certificates. This is not a ceremonial announcement. Without these certificates, exporters cannot claim duty-free access at Omani ports.

India, for its part, is liberalising 77.79 percent of its own tariff lines — covering 94.81 percent of imports from Oman by value. Omani dates, marbles, and petrochemical products will enter India at reduced rates. Sensitive Indian sectors, including dairy, tea, coffee, tobacco, gold and silver bullion, and certain agricultural goods, have been excluded from concessions entirely.

Bilateral trade between the two countries already crossed $10.61 billion in FY2024-25, up significantly from the previous year. Petroleum products dominate — light oils and preparations alone accounted for $1.57 billion in FY26 — but the CEPA is designed to diversify the export basket beyond energy.

## The Diaspora Angle: Professional Mobility

For the estimated 780,000 Indians living and working in Oman, the deal carries implications that go beyond trade statistics. The CEPA includes what the government calls an "enhanced mobility framework" under Mode 4 — the first of its kind in any Indian trade agreement with a Gulf state.

Oman has raised the quota for intra-corporate transferees from 20 percent to 50 percent, meaning Indian companies operating in Oman can now move significantly more of their own employees into the country. The permitted stay for contractual service suppliers has been extended from 90 days to two full years, with the option of a further two-year extension. Professionals in accountancy, taxation, architecture, and medical services get more liberal entry conditions.

The agreement also permits 100 percent foreign direct investment by Indian companies in major Omani services sectors through commercial presence — a provision that could reshape how Indian IT firms, consulting companies, and healthcare providers operate in the region.

Perhaps most notably, Oman has made its first-ever comprehensive commitment on traditional medicine across all modes of supply. This creates a formal opening for India's AYUSH and wellness sector in the Gulf — a niche but symbolically significant concession that no other country has offered.

## Strategic Timing

The deal arrives at a moment when the Strait of Hormuz — the waterway that Oman partially flanks — remains a flashpoint. The US naval blockade of Iranian ports continues, commercial shipping volumes through the strait have dropped, and oil markets remain volatile. Against that backdrop, a trade agreement that deepens India's commercial ties with a stable Gulf partner on the strait's opposite shore carries obvious strategic weight.

Discussions are also ongoing about the Middle East-India Deepwater Pipeline, a proposed subsea gas project linking Oman's coast with Gujarat. The CEPA creates a broader commercial framework within which such infrastructure projects could advance.

India already has trade agreements with the UAE, Australia, and several ASEAN nations. The Oman pact is Muscat's first bilateral trade agreement since its deal with the United States in 2006 — a fact that underscores the significance both sides attach to the partnership.

For Indian exporters, the immediate task is prosaic: register on the Trade Connect platform, update their Digital Signature Certificate details, and start filing for certificates of origin. The tariff walls come down at midnight."""
    },
    {
        "headline": "Blue Origin's New Glenn Rocket Exploded on the Launch Pad. Here Is Why It Matters Beyond Space.",
        "subheadline": "The blast destroyed Jeff Bezos' only heavy-lift launch site, delays Amazon's satellite internet rollout, and hands SpaceX an even larger lead in the commercial launch market.",
        "slug": "blue-origin-new-glenn-explosion-launch-pad-amazon-leo-spacex-nasa-artemis-20260531",
        "category": "news",
        "sources": "Reuters, GeekWire, Florida Today, Wikipedia, NBC Palm Springs",
        "image_search_person": "Jeff Bezos",
        "image_pexels_query": "rocket launch Cape Canaveral",
        "image_pexels_fallback": "space rocket launch pad explosion",
        "image_attribution": "Wikimedia Commons",
        "body": """A Blue Origin rocket exploded during a static fire test at Cape Canaveral on Thursday night, producing what observers described as the most powerful rocket explosion since the Soviet Union's N1 moon rocket was destroyed during a launch attempt in 1969.

The blast destroyed the New Glenn booster nicknamed "No, It's Necessary" — a reference to a line from the film Interstellar — along with its fuelled second stage. More critically, it "practically destroyed" Launch Complex 36, Blue Origin's only operational New Glenn launch site. Engineers expect at least six months of repairs, possibly longer.

No injuries were reported. Jeff Bezos, the company's founder, confirmed on X that all personnel had been accounted for.

## The Immediate Fallout

The rocket had been scheduled to carry 48 satellites into low Earth orbit as early as the following week for Amazon Leo — the company's high-speed internet constellation, formerly known as Project Kuiper. That launch is now off the table.

Amazon, however, is not without options. The day after the explosion, United Launch Alliance successfully sent 29 Amazon Leo satellites into orbit on an Atlas V rocket from a pad not far from the ruins of Blue Origin's facility. Amazon has also reserved launches on Arianespace's Ariane 6, ULA's Vulcan, and SpaceX's Falcon 9.

"Weirdly, as far as New Glenn customers go, Amazon is probably in the best position to deal with this setback," said Caleb Henry, director of research at Quilty Space. "They've got safety through the diversity of their launch supplier base."

The irony is not lost on industry watchers. Amazon's contingency plan involves relying, in part, on SpaceX — the company run by Elon Musk, Bezos' long-running commercial rival. The explosion hands Musk's business leverage over Bezos at a critical moment.

## NASA's Lunar Problem

The damage extends beyond commercial satellite launches. NASA Administrator Jared Isaacman visited Launch Complex 36 to inspect the damage and speak with Blue Origin employees. In an email to the NASA workforce, he said the incident could potentially affect the agency's Artemis program and Moon Base plans.

Blue Origin is a key contractor for Artemis. The company's Blue Moon lander was selected to carry astronauts to the lunar surface. Any delay to the New Glenn launch vehicle ripples through NASA's lunar timeline — a program already under pressure from budget constraints and political scrutiny.

"It's only been a year since the SpaceX Starship also exploded on the launch pad and Blue Origin can also recover. But it will take months to rebuild," said Antoine Grenier, partner and head of space consulting at Analysys Mason.

SpaceX itself spent more than a year repairing its pad after a Falcon 9 exploded in 2016, though it resumed launches within four and a half months by shifting operations to a second Florida pad. Blue Origin does not have a second New Glenn pad.

## The Bigger Picture

The explosion comes at a pivotal moment for the commercial space industry. Amazon's Leo satellite internet service is racing to catch up with SpaceX's Starlink, which already has thousands of satellites in orbit and millions of paying subscribers. The initial Amazon Leo constellation calls for around 3,000 satellites — and the company was counting on New Glenn to carry a significant share of them.

For India's space sector, the implications are indirect but real. ISRO and Indian private launch companies like Skyroot and Agnikul have been positioning themselves in the small and medium satellite launch market. Every setback for the giants — whether it's Blue Origin's explosion or Vulcan's solid rocket booster issues — creates potential openings for alternative launch providers.

The Indian diaspora in the US aerospace industry, meanwhile, watches closely. Indian-origin engineers occupy senior positions across Blue Origin, SpaceX, Amazon, and NASA. The investigation into the explosion's cause will determine how quickly Bezos can rebuild — not just the launch pad, but confidence in a program that was supposed to prove Blue Origin could compete at the highest level.

Musk, for his part, offered brief sympathy on X: "Sorry to see this, I hope you recover quickly." In the commercial space race, even condolences carry competitive subtext."""
    },
    {
        "headline": "Modi Used Mann Ki Baat to Celebrate Two Sprinters Who Broke India's 100-Metre Record Three Times in Two Days.",
        "subheadline": "In the 134th episode of his monthly address, the Prime Minister spoke to Gurinder Veer Singh and Animesh Kujur — and also talked about Chola copper plates returned from the Netherlands, traditional summer drinks, and dolphin conservation.",
        "slug": "modi-mann-ki-baat-134-gurinder-veer-animesh-kujur-100m-record-chola-copper-plates-20260531",
        "category": "news",
        "sources": "DD News, Tripura Star News (full transcript), NDTV, IANS, India Today",
        "image_search_person": "Narendra Modi",
        "image_pexels_query": None,
        "image_pexels_fallback": None,
        "image_attribution": "Wikimedia Commons",
        "body": """Prime Minister Narendra Modi used the 134th episode of Mann Ki Baat on Sunday to call two athletes who had just rewritten Indian sprinting history — and in the process delivered a pointed rebuttal to the idea that Indians cannot compete in the 100-metre dash.

Gurinder Veer Singh, a Petty Officer in the Indian Navy, and Animesh Kujur, an athlete from Chhattisgarh who plays for Odisha, broke the national record in the men's 100-metre race three times within two days at the National Senior Athletics Federation Competition in Ranchi, Jharkhand. Nearly 800 athletes competed in the event, and four national records fell across different disciplines.

## The Conversation

Modi spoke to both athletes live on air. The exchange was unusually personal for a programme that typically keeps to scripted inspirational narratives.

Gurinder Veer, who ran 10.09 seconds to become the first Indian to break the 10.1-second barrier, told Modi about growing up in a middle-class family and cleaning his father's trophies as a child. "I used to clean any trophy and ask him where he won it," Gurinder said. "Then I would tell him, I also want to do some sport."

He recalled his mother switching off the television during a broadcast of a world record race. "I said, 'It's okay, you don't let me watch TV. One day, you'll find me on TV.'"

Animesh Kujur, who holds national records in the 200m and 400m, described how he began athletics only in 2021 after passing out of Sainik School Ambikapur. He had played football, switched to running during COVID, got selected for the nationals from a state meet he entered casually, and now represents India internationally.

Both athletes addressed the same prejudice directly: that Indian genes are not suited for sprinting. "People used to tell me the body of Indians is not at all made for 100 meters," Gurinder said. "My father and I always used to say, we will show them that we can do it."

Animesh echoed the sentiment: "People used to tell me the genes of Indians are not such that they can run Sub 10. But now both of us have proved that Indians can also do it." Both have been selected for the Commonwealth Games.

## Chola Copper Plates Return From the Netherlands

Modi also spoke about his recent visit to the Netherlands, where ancient copper plates from the Chola period were formally returned to India. The Prime Minister of the Netherlands was present at the ceremony. Modi said he had received "continuous messages from India and abroad" about the repatriation, and noted that the Tamil community worldwide was "particularly enthusiastic."

The Chola-era copper plates are among the most significant recent examples of heritage repatriation — a subject that has gained momentum globally as former colonial powers face pressure to return artefacts taken during the colonial era.

## Summer Drinks and Mango Diplomacy

In a lighter segment, Modi delivered what amounted to a geography lesson through beverages. He listed traditional summer drinks across Indian states — Aam Panna in North India, lassi in Punjab and Haryana, buttermilk in Rajasthan and Gujarat, Sattu sherbet in Bihar and Jharkhand, Kokum sherbet and Sol Kadhi in Konkan and Goa, Panakam and Neer Mor in South India, and Bael Pana in Odisha.

He then pivoted to mangoes, naming varieties from every region: Maharashtra's Alphonso, Gujarat's Kesar, UP's Dussehri and Langra ("which often remains green even after ripening"), Bihar's Zardalu, Bengal's Himsagar, and South India's Banganapalli and Totapuri. The segment was designed to highlight India's agricultural diversity, but it also doubled as soft cultural diplomacy — the kind of content that travels on WhatsApp forwards among diaspora communities.

## Dolphin Conservation and Swimming in Rivers

Modi highlighted efforts to protect the endangered Ganges river dolphin and praised Saji Valasheril from Aluva, Kerala, who runs a swimming club in a river where more than 15,000 people have learned to swim — including children with disabilities. Saji began the initiative after several students died in a boat accident.

The 134th episode aired at 11 AM IST across All India Radio, DD News, and government digital channels. For the diaspora, it was available on YouTube through multiple news channels."""
    }
]

# ── Main ──
def main():
    print(f"\n{'='*60}")
    print(f"The Videshi — News Writer")
    print(f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Articles to write: {len(ARTICLES)}")
    print(f"{'='*60}\n")

    published = 0

    for i, article in enumerate(ARTICLES, 1):
        print(f"\n--- Article {i}/{len(ARTICLES)}: {article['headline'][:60]}... ---")

        # Image sourcing
        img_url = None
        attribution = article.get('image_attribution', 'The Videshi')

        # Step 1: Wikipedia for person articles
        if article.get('image_search_person'):
            img_url = fetch_wikipedia_person_image(article['image_search_person'])
            if img_url:
                attribution = "Wikimedia Commons"

        # Step 2: Pexels fallback
        if not img_url and article.get('image_pexels_query'):
            img_url = fetch_pexels_image(
                article['image_pexels_query'],
                article.get('image_pexels_fallback')
            )
            if img_url:
                attribution = "Pexels"

        # Step 3: Upload to Supabase storage for permanence
        art_id = str(uuid.uuid4())
        final_image_url = None

        if img_url:
            filename = f"{art_id}.jpg"
            final_image_url = upload_to_supabase_storage(img_url, filename)
            if not final_image_url:
                # Try using original URL if it's from a permanent source
                if 'upload.wikimedia.org' in img_url or 'images.pexels.com' in img_url:
                    final_image_url = img_url
                    print(f"  ℹ Using original permanent URL")

        if not final_image_url:
            print(f"  ⚠ No image — publishing without hero image")

        # Publish
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        payload = {
            "id": art_id,
            "headline": article['headline'],
            "subheadline": article['subheadline'],
            "slug": article['slug'],
            "body": article['body'],
            "category": article['category'],
            "status": "published",
            "published_at": now,
            "sources": article['sources'],
            "image_url": final_image_url,
            "image_attribution": attribution if final_image_url else None,
        }

        result = sb_post('p2_articles', payload)
        if result:
            published += 1
            print(f"  ✅ Published: {article['slug']}")
        else:
            print(f"  ❌ Failed to publish: {article['slug']}")

        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Done. Published {published}/{len(ARTICLES)} articles.")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
