#!/usr/bin/env python3
"""
News writer for The Videshi - 2026-06-01 batch
Covers:
1. India GDP expected to ease to 7.2% in Q1 2026
2. EB-2 green cards frozen for Indians until October 2026
3. June 1 financial rule changes (UPI, LPG, ATM, solar, PAN, Maruti)
"""

import os, json, sys, uuid, time, re
import requests
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

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

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = requests.utils.quote(person_name.replace(' ', '_'))
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
    """Fetch image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                headers={"Authorization": PEXELS_KEY},
                timeout=10
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                    if url:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate image URL returns a real image > 5KB."""
    if not url:
        return False
    # Block banned domains
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com']
    if any(b in url for b in banned):
        print(f"  ✗ Banned domain in URL: {url[:60]}")
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        # Some servers don't return Content-Length on HEAD, try GET
        if r.status_code == 200 and 'image' in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            size = len(r2.content)
            if size > 5000:
                print(f"  ✓ Image validated (GET): {size} bytes")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, timeout=15,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ✗ Download failed: status={r.status_code}, size={len(r.content)}")
            return None
        
        ct = r.headers.get('Content-Type', 'image/jpeg')
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': ct,
                'x-upsert': 'true'
            },
            data=r.content,
            timeout=30
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ✗ Upload failed: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"  ✗ Upload error: {e}")
    return None

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Article inserted: {data[0].get('id', 'unknown')}")
            return data[0]
        print(f"  ✓ Article inserted (raw response)")
        return data
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None

# ==========================
# ARTICLE 1: India GDP Q1 2026
# ==========================
def write_gdp_article():
    print("\n=== Article 1: India GDP Q1 2026 ===")
    slug = "india-gdp-q1-2026-eases-7-2-percent-fastest-growing-major-economy-iran-war-tariffs"
    headline = "India's Economy Is Still the World's Fastest Growing. But the Cracks Are Starting to Show."
    subheadline = "A Reuters poll of 45 economists expects Q1 2026 GDP growth to ease to 7.2%, down from 7.8%, as US tariffs and the Iran war weigh on exports and private investment."

    body = """India's economy likely grew 7.2% year-on-year in the January–March 2026 quarter, down from 7.8% in the previous three months, according to a Reuters poll of 45 economists. The estimates ranged from 6.1% to 7.7%, with the official data due on Friday, June 5.

The slowdown is not a surprise. Three external shocks hit India in the first quarter — higher US tariffs on Indian goods, the US-Israeli war with Iran that sent crude oil prices surging past $90 a barrel, and a broader global pullback in trade that crimped export demand.

## Still the Fastest-Growing Major Economy

Despite the deceleration, India remains the world's fastest-growing large economy, comfortably ahead of China's sub-5% pace. The revised national accounts series, which shifted the GDP base year to 2022-23 from 2011-12 in February, puts India's growth trajectory in sharper focus.

Government spending did much of the heavy lifting. Capital expenditure on infrastructure — roads, railways, defence — maintained a healthy pace, partially offsetting the weakness in private investment, which economists describe as "moribund."

"Underlying drivers suggest a transition from broad-based expansion to a more uneven growth profile," said Dhiraj Nim, economist at ANZ. "Government spending likely maintained a healthy pace of growth, while external demand weakened amid global disruptions."

## What the Numbers Mean for NRIs

For the Indian diaspora watching from abroad, the GDP print is a mixed signal. On one hand, India's resilience through a global war and a tariff escalation is remarkable — no other major economy has held above 7% under comparable stress. On the other hand, the weakness in private investment is the statistic that should worry long-term watchers.

Private investment is what creates well-paying jobs for the millions entering India's workforce each year. Without it, the burden falls entirely on government capex — a model that works in the short term but cannot scale indefinitely.

## The RBI's Dilemma

The growth data arrives just as the Reserve Bank of India's Monetary Policy Committee meets this week to decide on interest rates. The RBI faces a triple bind: a weakening rupee that argues for holding rates, crude oil prices above $90 that add inflationary pressure, and the forecast of the driest monsoon in 11 years that could push food prices higher.

Markets are pricing in a hold, with some analysts now expecting a rate hike if the monsoon forecast deteriorates further. The Nifty 50 has fallen 2.7% over four sessions, and foreign investors dumped a record $2.22 billion in Indian stocks on Friday alone.

## The Bigger Picture

Gross value added, which strips out taxes and subsidies, is estimated at 7.3% — suggesting the underlying productive economy is holding up slightly better than the headline GDP number implies.

The Asian Development Bank recently upgraded India's full-year FY26 growth forecast to 7.2%, up from its earlier estimate of 6.5%, calling India a "key driver of global growth." But that optimism is increasingly conditional on two things: the Iran war finding a resolution that reopens the Strait of Hormuz, and the monsoon delivering enough rain to keep food inflation in check.

For now, India is growing fast enough to matter and slow enough to worry. The June 5 data will tell us which way the balance is tipping.

*Sources: Reuters poll of 45 economists (June 1, 2026); Asian Development Bank FY26 forecast revision; ANZ Economics research note*"""

    # Image: try Wikipedia for "Indian economy" or Pexels
    print("  Sourcing image...")
    img_url = fetch_pexels_image("Indian rupee currency notes", "India Reserve Bank building")

    final_img = None
    if img_url and validate_image(img_url):
        final_img = upload_to_supabase_storage(img_url, f"{slug}.jpg")

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": final_img,
        "image_attribution": "Pexels" if final_img else None,
        "sources": json.dumps(["Reuters", "Asian Development Bank", "ANZ Economics"]),
        "is_editorial": False,
        "vertical": "news"
    }

    return insert_article(article)


# ==========================
# ARTICLE 2: EB-2 Green Cards Frozen
# ==========================
def write_eb2_article():
    print("\n=== Article 2: EB-2 Green Cards Frozen ===")
    slug = "us-freezes-eb2-green-cards-indians-october-2026-quota-exhausted-2800-visas"
    headline = "The US Just Froze EB-2 Green Cards for Indians. The Next One Will Not Be Issued Until October."
    subheadline = "The State Department says all 2,800 EB-2 visas allocated to India for FY2026 have been used. No final approvals will happen until the new fiscal year begins on October 1."

    body = """The United States State Department has confirmed that the EB-2 immigrant visa category for Indian nationals is now "unavailable" for the remainder of fiscal year 2026. Every green card allocated to India under the EB-2 preference — roughly 2,800 out of a global cap of about 40,000 — has been issued.

No new EB-2 green cards will be approved for Indians until October 1, 2026, when the next fiscal year's quota opens.

## What EB-2 Covers

The EB-2 category is one of the primary employment-based routes to permanent residency in the United States. It covers professionals with advanced degrees — masters and above — and individuals with exceptional ability in science, business, or the arts. For tens of thousands of Indian engineers, doctors, researchers, and tech workers on H-1B visas, EB-2 is the main pathway from temporary work status to a green card.

## The Math Behind the Freeze

US immigration law caps total employment-based green cards at 140,000 per year. The EB-2 category receives 28.6% of that — about 40,000 visas. But a per-country cap of 7% means India can receive only around 2,800 EB-2 green cards annually, despite representing the single largest source of demand.

The mismatch between demand and supply has been structural for over a decade. The current EB-2 Final Action Date for India stands at September 1, 2013 — meaning only applicants who filed their petitions 13 years ago are currently eligible for final processing.

## The June 2026 Visa Bulletin's Other Bad News

The freeze is not the only setback. The June 2026 Visa Bulletin also showed EB-1 India retrogressing 3.5 months to December 15, 2022, and EB-2 India retrogressing 10.4 months to September 1, 2013. Immigration attorney Charlie Oppenheim, formerly of the State Department, has warned that the recent forward movements were "completely artificial" — driven by reduced processing for nationals of 75 countries whose immigrant visas were paused by the Trump administration.

"The longer the policy remains in place, the more severe the corrective action may be," Oppenheim said. "The affected applicants are not going away and will be at the front of the visa line with early Rest of World priority dates."

## What This Means for Indians in the US

If you are an Indian professional with a pending EB-2 petition, USCIS may continue accepting applications, but no final adjudication can happen until fresh visa numbers become available in October. Your case moves forward on paper; nothing moves in reality.

For those on H-1B visas waiting for EB-2 processing, the freeze extends what is already one of the longest immigration queues in the world. Many Indian professionals have been waiting 10 to 15 years for a green card that nationals of most other countries receive in months.

## The Broader Pattern

The EB-2 freeze is part of a broader tightening. USCIS recently issued a policy memo emphasising that Adjustment of Status — the process of applying for a green card from within the US — is a "discretionary benefit," signalling that officers may scrutinise applications more closely. The agency later walked back parts of the memo, but the message was clear: the path to permanent residency is getting narrower, not wider.

Germany, meanwhile, has approved 30 new initiatives to recruit Indian skilled workers, reserving 90,000 visas. Canada, Australia, and the UK continue to expand their own talent pipelines. For Indian professionals weighing their options, the EB-2 freeze is one more data point in a shifting global calculus.

*Sources: US State Department June 2026 Visa Bulletin; Outlook Business; WR Immigration analysis; USCIS policy guidance*"""

    # Image: try Pexels for US visa/passport
    print("  Sourcing image...")
    img_url = fetch_pexels_image("US visa passport stamp", "American immigration documents")

    final_img = None
    if img_url and validate_image(img_url):
        final_img = upload_to_supabase_storage(img_url, f"{slug}.jpg")

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": final_img,
        "image_attribution": "Pexels" if final_img else None,
        "sources": json.dumps(["US State Department", "Outlook Business", "WR Immigration", "USCIS"]),
        "is_editorial": False,
        "vertical": "politics"
    }

    return insert_article(article)


# ==========================
# ARTICLE 3: June 1 Rule Changes
# ==========================
def write_june1_rules_article():
    print("\n=== Article 3: June 1 Rule Changes ===")
    slug = "india-june-1-2026-rule-changes-upi-lpg-atm-solar-pan-maruti-prices"
    headline = "Nine Things That Changed in India on June 1. Your Wallet Will Notice Most of Them."
    subheadline = "From UPI security upgrades to commercial LPG price hikes, new ATM withdrawal rules, and the solar panel mandate — here is everything that kicked in today."

    body = """June 1, 2026 brought a stack of regulatory and price changes that will affect everyone from restaurant owners in Delhi to NRIs sending money home through UPI. Here is what changed and what it means.

## 1. UPI Gets New Security Layers

High-value UPI transactions now require additional authentication beyond the standard PIN. Under the new framework, larger transfers may need extra verification steps, including beneficiary name confirmation before the payment is processed. The Reserve Bank of India has been pushing these measures since early 2026 to reduce payment fraud, which crossed ₹1,200 crore last fiscal year.

For the diaspora, the UPI changes are relevant because international UPI-linked remittance services are growing. The extra verification adds a few seconds to each transaction but should reduce the misdirected payment problem that has plagued the platform.

## 2. Commercial LPG Prices Rise Up to ₹53.50

Indian Oil Corporation raised the price of 19-kg commercial LPG cylinders by ₹42 to ₹53.50 depending on the city. Delhi's price moved to ₹3,113.50 from ₹3,071.50. Kolkata saw the steepest increase at ₹53.50, while Mumbai and Chennai rose by ₹43.50 and ₹46 respectively.

The hike hits restaurants, hotels, and catering businesses hardest. Domestic LPG cylinder prices — the ones used in homes — remain unchanged for now, but energy analysts warn that a sustained rise in global crude could trigger a review.

## 3. ATM Withdrawals Now Count UPI Cardless Cash

Banks will now include UPI-based cardless cash withdrawals within monthly free ATM transaction limits. Customers who exceed their free withdrawal quota — typically three to five per month for non-home bank ATMs — will face the same ₹21 surcharge that applies to card-based withdrawals.

## 4. The Solar Cell Mandate Is Live

The Ministry of New and Renewable Energy has enforced the ALMM List-II (Approved List of Models and Manufacturers) requirement for solar PV cells from today. Only domestically manufactured, ALMM-approved solar cells can now be used in eligible projects. India's cumulative solar cell manufacturing capacity reached 40 GW at the end of March 2026, with 27.23 GW already on the approved list.

The ministry confirmed on Monday that "no blanket extension" would be given. The mandate is designed to support India's push for energy self-reliance and give policy certainty to domestic manufacturers who have invested heavily in cell production.

## 5. Export Duty on Fuel Products Revised

The government reduced export duty on petrol to ₹1.5 per litre, diesel to ₹13.5 per litre, and aviation turbine fuel to ₹9.5 per litre. The revision is part of the fortnightly review cycle that tracks global crude prices. Domestic fuel prices are not directly affected by this change.

## 6. Jet Fuel for International Airlines Slashed 27%

ATF prices for international carriers were cut by 27% — more than $400 per kilolitre — to about $1,100 per kilolitre. Domestic airline ATF rates, however, remain unchanged at ₹1,04,927.18 per kilolitre for the second consecutive month.

## 7. PAN Card Rules for Cash Transactions Updated

PAN is no longer mandatory for certain cash deposits exceeding ₹50,000, though reporting requirements for higher-value transactions remain. The threshold for mandatory PAN disclosure in property transactions has also been raised.

## 8. Maruti Suzuki Raises Car Prices

Maruti Suzuki has increased prices on several models, including the Alto and Brezza, citing higher production costs. The exact increase varies by model and variant.

## 9. Advance Tax Deadline Approaches

Taxpayers whose estimated annual tax liability exceeds ₹10,000 must pay 15% of their estimated liability by June 15 — the first instalment of advance tax for FY2026-27. Missing the deadline attracts interest charges under Sections 234B and 234C.

## The NRI Takeaway

For Indians abroad, the UPI security upgrade and PAN rule changes are the most directly relevant. If you send money to family through UPI-linked services, expect minor workflow changes. If you are planning property transactions in India, the revised PAN thresholds are worth reviewing with your CA before you sign.

*Sources: IANS; Indian Oil Corporation; Reserve Bank of India; Ministry of New and Renewable Energy; Dainik Bhaskar*"""

    # Image: Pexels for UPI / digital payment / India financial
    print("  Sourcing image...")
    img_url = fetch_pexels_image("mobile phone digital payment India", "smartphone banking transaction")

    final_img = None
    if img_url and validate_image(img_url):
        final_img = upload_to_supabase_storage(img_url, f"{slug}.jpg")

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": final_img,
        "image_attribution": "Pexels" if final_img else None,
        "sources": json.dumps(["IANS", "Indian Oil Corporation", "RBI", "MNRE", "Dainik Bhaskar"]),
        "is_editorial": False,
        "vertical": "news"
    }

    return insert_article(article)


# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi News Writer - 2026-06-01")
    print("=" * 60)

    results = []

    r1 = write_gdp_article()
    results.append(("GDP Q1 2026", r1))

    r2 = write_eb2_article()
    results.append(("EB-2 Green Card Freeze", r2))

    r3 = write_june1_rules_article()
    results.append(("June 1 Rule Changes", r3))

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    for name, result in results:
        status = "✓ Published" if result else "✗ Failed"
        print(f"  {status}: {name}")
    
    failed = sum(1 for _, r in results if not r)
    if failed:
        print(f"\n⚠ {failed} article(s) failed to publish")
        sys.exit(1)
    else:
        print(f"\n✓ All {len(results)} articles published successfully")
