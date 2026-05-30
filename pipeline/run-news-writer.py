#!/usr/bin/env python3
"""The Videshi — News Writer (2026-05-30 evening batch)"""

import json, os, re, sys, time, uuid, urllib.parse, subprocess, hashlib
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────────
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
            os.environ[k.strip()] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SB_URL = os.environ['SUPABASE_URL']
SB_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

import requests

# ── helpers ──────────────────────────────────────────────────────────────
def sb_headers():
    return {
        'apikey': SB_KEY,
        'Authorization': f'Bearer {SB_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }

def sb_insert(table, row):
    r = requests.post(f'{SB_URL}/rest/v1/{table}', headers=sb_headers(), json=row, timeout=30)
    if r.status_code not in (200, 201):
        print(f'  ✗ Insert {table} failed: {r.status_code} {r.text[:300]}')
        return None
    data = r.json()
    return data[0] if isinstance(data, list) and data else data

def sb_patch(table, match, patch):
    params = '&'.join(f'{k}={v}' for k, v in match.items())
    r = requests.patch(f'{SB_URL}/rest/v1/{table}?{params}', headers=sb_headers(), json=patch, timeout=30)
    if r.status_code not in (200, 204):
        print(f'  ✗ Patch {table} failed: {r.status_code} {r.text[:300]}')

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
    """Fetch a relevant image from Pexels via curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print('  ⚠ No Pexels API key')
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape',
                 '-H', f'Authorization: {PEXELS_KEY}'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                src = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('original')
                alt = (photo.get('alt') or '').lower()
                # Filter out generics
                bad_alts = ['aerial', 'satellite', 'map', 'flag', 'icon', 'logo']
                if any(b in alt for b in bad_alts):
                    continue
                if src:
                    print(f"  ✓ Pexels image for '{q}': {src[:80]}...")
                    return src
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(img_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        r = requests.get(img_url, timeout=20, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200:
            print(f"  ✗ Image download failed: {r.status_code}")
            return img_url  # Fall back to original URL if it's from a permanent source
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if 'image' not in content_type:
            print(f"  ✗ Not an image: {content_type}")
            return img_url
        if len(r.content) < 5000:
            print(f"  ✗ Image too small: {len(r.content)} bytes")
            return img_url

        upload_headers = {
            'apikey': SB_KEY,
            'Authorization': f'Bearer {SB_KEY}',
            'Content-Type': content_type,
            'x-upsert': 'true'
        }
        up = requests.post(
            f'{SB_URL}/storage/v1/object/article-images/{filename}',
            headers=upload_headers,
            data=r.content,
            timeout=30
        )
        if up.status_code in (200, 201):
            public_url = f'{SB_URL}/storage/v1/object/public/article-images/{filename}'
            print(f"  ✓ Uploaded to Supabase: {filename}")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({up.status_code}), using original URL")
            return img_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return img_url

def validate_image_url(url):
    """Check that an image URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, headers={"User-Agent": "TheVideshi/1.0"}, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Some servers don't support HEAD — try GET
        r = requests.get(url, timeout=10, headers={"User-Agent": "TheVideshi/1.0"}, stream=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        return r.status_code == 200 and 'image' in ct
    except:
        return False

# ── articles ─────────────────────────────────────────────────────────────
articles = []

# ═══════════════════════════════════════════════════════════════════════════
# ARTICLE 1: India Monsoon Forecast — Weakest in 11 Years
# ═══════════════════════════════════════════════════════════════════════════
articles.append({
    "headline": "India Braces for Its Weakest Monsoon in 11 Years. El Niño, the Iran War, and a Food Price Crisis Are Converging.",
    "subheadline": "The India Meteorological Department has revised its monsoon forecast downward to 90 percent of normal. With half of India's farmland unirrigated and fuel prices already elevated, the compounding risks are hard to overstate.",
    "slug": "india-weakest-monsoon-11-years-el-nino-2026-food-inflation-crisis-20260530",
    "category": "news",
    "body": """India's monsoon season is about to begin, and the forecast is not reassuring. The India Meteorological Department on Friday revised its projection for the June-to-September southwest monsoon downward to 90 percent of the long-period average — the weakest outlook since 2015, when El Niño reduced rainfall to 87 percent and triggered a nationwide agricultural crisis.

The revision marks a further deterioration from IMD's first-stage forecast in April, which had pegged rainfall at 92 percent. The culprit is a developing El Niño — a warming of central and eastern Pacific Ocean temperatures that historically suppresses the Indian monsoon. IMD now assigns an 84 percent probability that total seasonal rainfall will come in below normal, with the emerging El Niño expected to intensify to moderate or strong levels during the critical July-August period.

## Why This Matters Beyond the Weather Map

The monsoon delivers roughly 70 percent of India's annual rainfall, replenishing reservoirs, groundwater, and rivers that sustain a $4-trillion economy. Nearly half of India's farmland lacks irrigation, meaning rain-fed agriculture — on which some 600 million people depend — is entirely at the monsoon's mercy.

A weak monsoon does not just mean dry fields. It cascades through the economy in predictable and painful ways: lower crop yields push up food prices, which feed into retail inflation, which constrains the Reserve Bank of India's ability to cut interest rates. Rural incomes fall, dampening demand for everything from motorcycles to consumer goods.

M. Ravichandran, secretary of the Earth Sciences Ministry, told reporters in New Delhi that June rainfall is expected to come in below 92 percent of the long-period average. Several states — including Uttar Pradesh, Haryana, Punjab, Bihar, Odisha, Chhattisgarh, Gujarat, and Andhra Pradesh — are also forecast to experience above-normal heatwave days in June.

## The Double Squeeze: El Niño Meets the Iran War

What makes 2026 particularly dangerous is the convergence of a weak monsoon with the economic fallout from the ongoing Iran conflict. India's finance ministry, in its monthly economic report released Saturday, identified the Strait of Hormuz disruption as the "single most consequential variable" for the country's external and price outlook.

India is the world's third-largest crude importer. Brent crude, while down 19 percent in May from its wartime peak, remains 27 percent above pre-war levels. Recent fuel price hikes — necessitated by the elevated global oil market — are already feeding into transport, energy, and food-related costs.

"A deficient monsoon, particularly in the crucial July-August months, can add to the pressure and push up inflation closer to an average of 5.5 percent if food inflation spikes," said Gaura Sengupta, chief economist at IDFC First Bank. India's retail inflation stood at 3.48 percent in April — below the RBI's target — but the trajectory now looks distinctly unfavorable.

## What NRIs Should Watch

For the Indian diaspora, the monsoon is not an abstraction. Many NRI families maintain agricultural land, have relatives in farming communities, or send remittances that partially offset rural income shortfalls. A weak monsoon year typically means increased financial pressure on families back home.

The finance ministry's warning of a "significant rainfall deficit" translating into weaker rural demand and slower aggregate growth is also a signal for NRI investors. Indian equity markets, already down 1.9 to 2.8 percent in May on Iran war jitters, face an additional headwind if agricultural distress materializes.

The monsoon's advance into central and northern India — typically June through early July — will be the next critical data point. IMD has said it will issue state-level forecasts and shorter-range updates as the season progresses.

For now, the headline number is sobering: 90 percent of normal, with an El Niño gathering strength. The last time these conditions converged, in 2015, India declared drought in 11 states.""",
    "sources": "Reuters, India Meteorological Department, IDFC First Bank, India Finance Ministry Monthly Report, The Business Standard",
    "image_query": "Indian monsoon rain farm agriculture",
    "image_fallback_query": "monsoon rain India field",
    "person_name": None
})

# ═══════════════════════════════════════════════════════════════════════════
# ARTICLE 2: Delhi HC Google Keyword Ads Ruling
# ═══════════════════════════════════════════════════════════════════════════
articles.append({
    "headline": "A Delhi Court Just Told Google It Cannot Auction Off Someone Else's Brand Name. Indian Businesses Are Cheering.",
    "subheadline": "The Delhi High Court ruled that Google's keyword advertising practice amounts to trademark infringement. Zerodha, Shaadi.com, and marketing experts say the decision could reshape a Rs 2.7-lakh-crore industry.",
    "slug": "delhi-hc-google-keyword-advertising-trademark-hindware-ruling-20260530",
    "category": "news",
    "body": """For over a decade, one of the most common tactics in Indian digital marketing has been to bid on a competitor's brand name in Google Ads. Search for "Hindware" and you might see a rival's advertisement at the top of the results. Google facilitates the auction, collects the fee, and points to the advertiser when questions arise.

On May 22, the Delhi High Court told Google that this argument no longer holds. In a ruling that Indian businesses, lawyers, and brand managers have since rallied around, Justice Mini Pushkarna permanently restrained Google LLC and Google India from using the registered trademark "Hindware" as an advertising keyword. The court ordered Google to pay Rs 30 lakh (approximately $31,600) in damages.

## What the Court Actually Said

The ruling went further than most legal observers expected. Justice Pushkarna held that Google's AdWords program is not a passive platform service — it is an active commercial venture that monetizes brand names without the trademark owner's permission.

"The manner in which Google operates its AdWords Policy makes it clear that Google sells or auctions the use of the trademark without any authorisation from the proprietor of the trademark," the court stated.

The judgment found that by enabling direct competitors to intercept users who specifically searched for Hindware, Google engaged in an "unfair practice" and exploited the distinctive character of a well-known trademark to benefit its own advertising business. The court explicitly rejected the notion that Google was a mere intermediary in the transaction.

## The Industry Reaction

The response from India's business community has been swift and enthusiastic.

Nithin Kamath, founder of the brokerage firm Zerodha, said his brand had suffered from competitor keyword bidding for years. The ruling "now opens up a route for legal recourse," he wrote on social media.

Anupam Mittal, founder of Shaadi.com, was more blunt: "You create the brand. Someone else bids on it. Google takes the fee." The ruling, he said, "could change the economics of online advertising for millions of businesses."

Marketing experts have warned that the implications extend beyond Google. Prashant Puri, CEO of AdLift, pointed out that Amazon's sponsored product placements — where competitor listings appear on a brand's own product page — and LinkedIn's B2B targeting tools could face similar legal scrutiny.

## Why This Matters at Scale

India's digital advertising market generated over Rs 1.36 lakh crore ($16 billion) in revenue in 2024 and is projected to reach Rs 2.7 lakh crore ($32 billion) by 2030. Keyword bidding is the backbone of this ecosystem. If brands can now legally prevent competitors from bidding on their names, the economics of customer acquisition change dramatically.

For startups, D2C brands, fintech companies, and SaaS businesses that depend heavily on search-driven customer acquisition, the ruling introduces a new variable. Companies that previously relied on intercepting competitor traffic may need to invest more in building their own brand recognition — or accept higher costs for generic keywords.

Sajal Gupta, CEO of Kiaos Marketing, believes the immediate financial impact on Google will be limited. But the structural implications — fewer bidders per auction, lower per-click prices, and a potential compliance burden if Google must build systems to verify trademark claims at scale — could reshape the market over time.

## The Diaspora Angle

For NRI entrepreneurs and investors with stakes in Indian tech and e-commerce, the ruling is a reminder that India's regulatory environment is evolving in ways that can reshape business models. Google, which counts India as one of its most critical global markets, will likely appeal. But in the meantime, trademark holders across the country are reviewing their options.

The ruling is not yet binding on courts outside Delhi. But as a Delhi High Court decision on a practice that is uniform across India, its persuasive value is substantial. The case that ran for over a decade has, in a single judgment, placed a legal cloud over one of digital advertising's most fundamental assumptions.""",
    "sources": "Reuters, Delhi High Court judgment (May 22, 2026), Storyboard18, Outlook Business, Exchange4Media, Devdiscourse",
    "image_query": "Google office building India",
    "image_fallback_query": "digital advertising computer screen search",
    "person_name": None
})

# ═══════════════════════════════════════════════════════════════════════════
# ARTICLE 3: Supreme Court Anti-Trafficking Protection Plan
# ═══════════════════════════════════════════════════════════════════════════
articles.append({
    "headline": "The Supreme Court Just Issued India's First Nationwide Plan to Protect Trafficking Survivors. It Took 200 Pages.",
    "subheadline": "Justice Pardiwala's bench created a binding framework for rescue, rehabilitation, and prosecution that no government had managed to produce. The ruling also clarified that voluntary adult sex work cannot be criminalized.",
    "slug": "supreme-court-india-first-nationwide-anti-trafficking-victim-protection-plan-20260530",
    "category": "news",
    "body": """The Supreme Court of India has issued what may be its most comprehensive human rights ruling of the year — a binding, nationwide Victim Protection Plan for survivors of trafficking for commercial sexual exploitation. The judgment, delivered by a bench of Justices J.B. Pardiwala and R. Mahadevan, runs to some 200 pages and covers rescue operations, victim identification, rehabilitation, prosecution mechanisms, and institutional coordination.

"It took a pretty long time to prepare this judgment, but we are sure you won't have to refer to any books henceforth on the subject," Justice Pardiwala observed at the time of pronouncement. "This will remain very close to our hearts because it will go a long way in protecting vulnerable young girls and women."

## What the Court Found

The bench identified a gap that successive governments had failed to close. Despite the existence of multiple laws dealing with trafficking and sexual exploitation — including the Immoral Traffic (Prevention) Act, the Protection of Children from Sexual Offences Act, and provisions under the Indian Penal Code — India lacked a comprehensive framework governing the rescue, protection, rehabilitation, and reintegration of trafficking victims.

The court held that this absence had resulted in "arbitrary and non-uniform treatment of survivors across the country," impairing their fundamental rights under Articles 21 (right to life and personal liberty) and 23 (prohibition of human trafficking and forced labor) of the Constitution.

The Union Government had previously acknowledged the need for such a plan and had undertaken efforts to formulate one. But no framework had been finalized, leaving the court to step in under its extraordinary powers under Articles 32 and 142 of the Constitution.

## The Framework

The Victim Protection Plan issued by the court is binding on all states and union territories. It mandates standardized protocols across several critical areas.

On **rescue operations**, the court directed that raids and rescue missions must be conducted with trained social workers present, not just law enforcement. Rescued individuals must be treated as potential victims, not as accused persons — a distinction that advocacy groups have demanded for years, pointing to widespread instances of trafficking survivors being arrested and prosecuted rather than assisted.

On **victim identification**, the ruling establishes criteria for distinguishing between victims of trafficking and individuals who may be engaged in voluntary sex work. The court was explicit that "voluntary adult sex work cannot be criminalised if based on consent" — a clarification that builds on earlier Supreme Court observations but now carries the weight of a detailed, reasoned judgment.

On **rehabilitation**, the court ordered the creation of shelters, vocational training programs, and mental health services for survivors. It directed states to ensure that survivors are not housed in conditions that amount to further detention — a persistent problem in government-run homes.

On **prosecution**, the judgment directed that charges must focus on traffickers, pimps, and customers who exploit minors or coerced adults, rather than on the victims themselves.

## Why It Matters

India is one of the countries most affected by human trafficking, with the National Crime Records Bureau recording thousands of cases annually — a figure that anti-trafficking organizations say vastly underestimates the true scale.

The gap between the law on paper and its implementation has been enormous. Without standardized procedures, survivors' experiences varied dramatically depending on which state they were rescued in, which police station handled their case, and whether any trained personnel were available.

The Supreme Court's intervention is unusual in its level of operational detail. Courts typically issue directives and leave implementation to the executive branch. Here, the bench essentially wrote the policy framework that government agencies had not produced, then made it legally binding.

## The Diaspora Connection

For the Indian diaspora, trafficking is often a hidden issue — distant from the professional and economic concerns that dominate NRI conversations about India. But the ruling intersects with broader questions about India's governance capacity and its willingness to protect its most vulnerable citizens.

Several diaspora-backed NGOs work on anti-trafficking efforts in India, and the Supreme Court's framework gives them a legal benchmark to hold state governments accountable. The judgment also addresses cross-border trafficking, noting that India shares porous borders with Nepal and Bangladesh — countries from which significant numbers of women and girls are trafficked into India.

Justice Pardiwala acknowledged the research assistance of legal scholars who contributed to the judgment, describing the matter as "deeply significant to the protection of vulnerable women and children." The ruling now becomes the binding standard against which every state's anti-trafficking efforts will be measured.""",
    "sources": "LiveLaw, Supreme Court of India judgment (May 2026), National Crime Records Bureau",
    "image_query": "Supreme Court of India building",
    "image_fallback_query": "Indian court justice gavel",
    "person_name": "Supreme Court of India"
})

# ── main loop ────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"The Videshi — News Writer")
print(f"Batch: {datetime.now(timezone.utc).isoformat()}")
print(f"Articles to write: {len(articles)}")
print(f"{'='*60}\n")

published = 0

for i, art in enumerate(articles, 1):
    print(f"\n── Article {i}/{len(articles)}: {art['headline'][:60]}...")

    # Validate article quality
    word_count = len(art['body'].split())
    if word_count < 400:
        print(f"  ✗ REJECTED: Only {word_count} words (minimum 400)")
        continue
    if len(art['headline']) < 20 or len(art['headline']) > 200:
        print(f"  ✗ REJECTED: Headline length {len(art['headline'])} out of range")
        continue
    if len(art['subheadline']) < 15:
        print(f"  ✗ REJECTED: Subheadline too short")
        continue

    print(f"  Word count: {word_count} ✓")
    print(f"  Headline: {len(art['headline'])} chars ✓")
    print(f"  Category: {art['category']} ✓")

    # Image sourcing
    img_url = None

    # Step 1: Wikipedia if it's a person article
    if art.get('person_name'):
        img_url = fetch_wikipedia_person_image(art['person_name'])

    # Step 2: Pexels fallback
    if not img_url:
        img_url = fetch_pexels_image(art['image_query'], art.get('image_fallback_query'))

    # Step 3: Upload to Supabase storage
    final_img_url = None
    if img_url:
        filename = f"{art['slug']}.jpg"
        final_img_url = upload_image_to_supabase(img_url, filename)
    else:
        print("  ⚠ No image found — publishing without image (no image > wrong image)")

    # Insert article
    row = {
        'headline': art['headline'],
        'subheadline': art['subheadline'],
        'slug': art['slug'],
        'category': art['category'],
        'body': art['body'],
        'sources': art['sources'],
        'image_url': final_img_url,
        'image_attribution': 'The Videshi' if final_img_url and 'supabase' in (final_img_url or '') else ('Wikimedia Commons' if final_img_url and 'wiki' in (final_img_url or '').lower() else None),
        'status': 'published',
        'published_at': datetime.now(timezone.utc).isoformat(),
    }

    result = sb_insert('p2_articles', row)
    if result:
        art_id = result.get('id', 'unknown')
        print(f"  ✓ Published: {art['slug']} (id: {art_id})")
        published += 1
    else:
        print(f"  ✗ Failed to insert article")

print(f"\n{'='*60}")
print(f"Batch complete: {published}/{len(articles)} articles published")
print(f"{'='*60}\n")
