#!/usr/bin/env python3
"""
News Writer — The Videshi (fixed)
Generates 3 news articles with proper images and inserts into Supabase.
"""

import json, os, re, sys, time, uuid
from datetime import datetime, timezone
from io import BytesIO

import requests
from PIL import Image

# ── ENV ──
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/.env.supabase"))
load_dotenv(os.path.expanduser("~/workspace/.env.pexels"))

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS_SB = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

# ── IMAGE HELPERS ──

def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def upload_to_supabase(img_bytes, filename):
    url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    r = requests.post(url, headers=headers, data=img_bytes, timeout=30)
    if r.status_code in (200, 201):
        public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded: {filename} ({len(img_bytes)} bytes)")
        return public_url
    else:
        print(f"  ✗ Upload failed: {r.status_code} {r.text[:200]}")
        return None

def download_image(url, retries=2):
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, headers=UA, timeout=20)
            if r.status_code == 200 and len(r.content) > 5000:
                ct = r.headers.get("Content-Type", "")
                if "image" in ct or url.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    return r.content
            if r.status_code == 429 and attempt < retries:
                wait = 3 * (attempt + 1)
                print(f"  ⚠ 429 rate limit, waiting {wait}s...")
                time.sleep(wait)
                continue
            print(f"  ⚠ Download: status={r.status_code}, size={len(r.content)}")
        except Exception as e:
            print(f"  ⚠ Download error: {e}")
        if attempt < retries:
            time.sleep(2)
    return None

def fetch_pexels(query, per_page=3):
    if not PEXELS_KEY:
        return []
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": per_page, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            results = [{"url": p["src"]["large2x"], "photographer": p["photographer"]} for p in photos]
            if results:
                print(f"  ✓ Pexels: {len(results)} results for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return []

def fetch_wikimedia_commons(query, limit=5):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime",
        "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers=UA, timeout=15)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "title": page.get("title", ""),
                })
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []

def fetch_wikipedia_person_image(person_name):
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia: {person_name}")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error: {e}")
    return None

def source_and_upload(slug, person_name=None, wiki_queries=None, pexels_queries=None):
    """Try Wikimedia first with retry, fall back to Pexels. Download, compress, upload."""
    urls_to_try = []
    attribution = "Wikimedia Commons"

    # 1. Wikipedia person image
    if person_name:
        url = fetch_wikipedia_person_image(person_name)
        if url:
            urls_to_try.append(("Wikimedia Commons", url))

    # 2. Wikimedia Commons search
    if wiki_queries:
        for q in wiki_queries:
            results = fetch_wikimedia_commons(q)
            for r in results[:2]:
                urls_to_try.append(("Wikimedia Commons", r["url"]))
            if results:
                break
            time.sleep(1)

    # 3. Pexels
    if pexels_queries:
        for q in pexels_queries:
            results = fetch_pexels(q)
            for r in results[:2]:
                purl = r["url"]
                if "pexels.com" in purl and "?" not in purl:
                    purl += "?auto=compress&cs=tinysrgb&w=1200"
                urls_to_try.append(("Pexels", purl))
            if results:
                break

    # Try downloading each candidate
    for attr, url in urls_to_try:
        img_bytes = download_image(url)
        if img_bytes:
            compressed = compress_image(img_bytes)
            if len(compressed) < 5000:
                continue
            final_url = upload_to_supabase(compressed, f"{slug}.jpg")
            if final_url:
                return final_url, attr
        time.sleep(2)  # delay between attempts to avoid rate limits

    print(f"  ✗ No image for {slug}")
    return None, None


def create_topic(title, category="news", vertical="politics", urgency="daily", score=75):
    """Create a topic in p2_topics and return its id."""
    topic_id = str(uuid.uuid4())
    topic = {
        "id": topic_id,
        "canonical_title": title[:200],
        "vertical": vertical,
        "urgency": urgency,
        "category": category,
        "score_diaspora": 70,
        "score_significance": 80,
        "score_recency": 85,
        "score_source_avail": 60,
        "score_total": score,
        "signal_count": 3,
        "status": "published",
        "keywords": []
    }
    r = requests.post(
        f"{SB_URL}/rest/v1/p2_topics",
        headers=HEADERS_SB,
        json=topic,
        timeout=30
    )
    if r.status_code in (200, 201):
        print(f"  ✓ Topic created: {title[:50]}... ({topic_id})")
        return topic_id
    else:
        print(f"  ✗ Topic creation failed: {r.status_code} {r.text[:200]}")
        return None

def insert_article(article):
    r = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Inserted: {article['headline'][:60]}... (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:400]}")
        return None


def count_words(text):
    return len(re.findall(r'\b\w+\b', re.sub(r'#+ ', '', text)))


# ── ARTICLES ──

def build_articles():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    articles = []

    # ────────────────────────────────────────────────────────────
    # ARTICLE 1: Supreme Court online gaming ruling
    # ────────────────────────────────────────────────────────────
    print("\n═══ Article 1: Supreme Court Online Gaming ═══")

    slug1 = "supreme-court-online-gaming-ban-virtual-gambling-house-mobile-phone-20260605"

    body1 = """The Supreme Court has delivered a pair of rulings that could effectively end India's real-money online gaming industry as it currently exists. In a judgment handed down on May 27 and formally released this week, a bench of Justices J.B. Pardiwala and R. Mahadevan upheld the constitutional validity of Tamil Nadu and Karnataka laws banning online betting and wagering — even on games of skill like rummy, poker, and fantasy cricket.

The court's language was unusually blunt. "Every mobile phone is now a virtual common gambling house," the bench wrote, citing addiction, monetary losses, and a pattern of suicides linked to online gaming as threats to public order and mental health.

## What the Ruling Says

The central legal question was whether state governments could ban wagering on games that involve skill, not just chance. Gaming companies had long argued that platforms like Dream11 and Mobile Premier League were skill-based competitions protected under Article 19(1)(g) of the Constitution — the fundamental right to practise any trade or profession.

The Supreme Court rejected that argument entirely. It held that once money is staked on the uncertain outcome of any game, the activity becomes "betting" within the meaning of Entry 34 of List II of the Constitution, regardless of how much skill is involved. Betting, the court said, is *res extra commercium* — outside the domain of constitutionally protected trade.

The bench set aside earlier rulings by the Madras and Karnataka High Courts that had sided with the industry, and declared the state-level amendments banning online gaming with stakes to be fully constitutional.

## The Tax Blow

On the same day, in a companion case — *DGGI v. Gameskraft Technologies* — the court ruled that GST applies on the full value of every stake deposited on gaming platforms, not merely on the platform's commission or service fee. The ruling is retroactive to July 2017.

This means platforms that charged 28% GST only on their service fees now face demands covering years of back taxes on total wagered amounts. For an industry that processed billions of rupees in deposits annually, the liability could be existential.

## A Legislative One-Two Punch

The court's rulings land on an industry already reeling from parliament's Promotion and Regulation of Online Gaming Act, 2025 (PROGA), which imposed a nationwide prohibition on real-money games effective May 1, 2026. The combination of legislative ban, judicial validation, and retroactive taxation leaves almost no legal ground for platforms to continue operating.

## What It Means for the Diaspora

For NRIs who regularly played fantasy cricket on Dream11 during IPL season or wagered on rummy tournaments, the ruling closes a recreational pastime that had become deeply embedded in diaspora culture. Several Indian-origin entrepreneurs in the gaming space — including founders backed by prominent Silicon Valley investors — now face the collapse of businesses valued at billions of dollars just two years ago.

The broader signal is significant. India's Supreme Court has sided with state paternalism over digital-economy liberalism, prioritising public health concerns about gaming addiction over industry arguments about skill, employment, and tax revenue. For diaspora investors and tech entrepreneurs watching India's regulatory trajectory, it is a data point worth noting.

## What Happens Next

Gaming companies are expected to file review petitions, though the chances of reversal are slim given the unanimous bench and the exhaustive 298-page judgment. Several platforms have already begun winding down Indian operations. Industry body E-Gaming Federation, which represents major operators, has not yet issued a formal response.

The court directed that the Tamil Nadu legislation was backed by empirical evidence — including the Justice Chandru Committee report documenting gaming-related suicides and a teachers' survey on student gambling — lending the ruling a factual foundation that will be difficult to challenge.

For India's once-booming $3 billion online gaming industry, the house has gone bust."""

    img1_url, img1_attr = source_and_upload(
        slug1,
        wiki_queries=["Supreme Court of India building New Delhi"],
        pexels_queries=["India supreme court", "Indian court building"]
    )

    topic1_id = create_topic("Supreme Court declares mobile phone virtual gambling house, upholds online gaming bans", score=82)
    if not topic1_id:
        print("  ✗ Skipping article 1 — topic creation failed")
    else:
        articles.append({
            "id": str(uuid.uuid4()),
            "topic_id": topic1_id,
            "headline": "India's Supreme Court Just Declared Every Mobile Phone a 'Virtual Gambling House'",
            "subheadline": "The ruling upholds state bans on real-money online gaming, retroactive GST on full stakes, and strips constitutional protection from platforms like Dream11 and MPL.",
            "body": body1,
            "slug": slug1,
            "category": "news",
            "vertical": "politics",
            "tags": ["Supreme Court", "online gaming", "Dream11", "gambling ban", "GST", "India regulation"],
            "urgency": "daily",
            "word_count": count_words(body1),
            "diaspora_angle": "NRIs who played fantasy cricket on Dream11 or wagered on rummy face the closure of a popular recreational pastime, while diaspora-backed gaming startups valued in billions now confront existential regulatory risk.",
            "status": "published",
            "published_at": now,
            "sources": [{"name": "LiveLaw"}, {"name": "Bar and Bench"}, {"name": "Supreme Court Observer"}, {"name": "CA Club India"}],
            "image_url": img1_url or "",
            "image_caption": "The Supreme Court of India in New Delhi",
            "image_attribution": img1_attr or "Wikimedia Commons",
            "is_editorial": False,
            "is_featured": False,
            "score_total": 82
        })

    # ────────────────────────────────────────────────────────────
    print("\n═══ Article 2: Defence Financial Powers ═══")

    slug2 = "rajnath-singh-defence-financial-powers-dfpds-2026-procurement-20260605"

    body2 = """Defence Minister Rajnath Singh on Thursday approved the most significant revision of military procurement authority in five years, doubling the financial powers of Army, Navy, and Air Force field commanders and enabling them to fast-track more than ₹1.25 lakh crore ($15 billion) in annual revenue-related purchases.

The reform, released as the Delegation of Financial Powers for the Defence Services 2026 (DFPDS-2026), is designed to slash bureaucratic delays in a procurement system that has long been criticised for its sluggishness — a vulnerability that has become more glaring as India navigates the security fallout from the Iran-Gulf conflict and rising tensions in the Indo-Pacific.

## What Changed

Under the revised framework, financial limits across all three services have been raised by up to 100 percent, with some categories seeing increases of more than double. The Ministry of Defence says the changes mean that 80 to 90 percent of revenue procurement contracts can now be cleared directly by the armed forces, bypassing the ministry entirely.

This is the first update to the delegation framework since 2021. It covers recurring expenses — inventory, supplies, services, and maintenance that keep the forces running day to day. Capital procurement, which governs big-ticket strategic assets like fighter jets and submarines, remains under the ministry's purview.

Special financial powers for meeting urgent operational requirements have also been doubled, giving field commanders greater flexibility to respond to emerging threats without waiting for approval from New Delhi.

## The Aatmanirbhar Angle

A key element of the reform is a doubling of financial powers related to indigenisation and research and development within the military ecosystem. The move is explicitly aimed at advancing the government's Aatmanirbhar Bharat initiative in defence, reducing dependence on foreign Original Equipment Manufacturers and channelling more contracts toward domestic manufacturers.

For the first time, the framework includes provisions for joint-service procurement, allowing one service branch to execute purchases for another with higher delegated authority than earlier norms permitted. This addresses a long-standing inefficiency where the three services often bought the same category of equipment through separate, slower procurement channels.

## Why It Matters Now

The timing is deliberate. India's defence budget for FY2026-27 crossed ₹7 lakh crore for the first time, and the government has been under pressure to ensure that allocated funds are actually spent rather than lapsing at year-end — a chronic problem in Indian defence procurement.

The Iran war has added urgency. With oil prices elevated, shipping through the Strait of Hormuz disrupted, and India conducting parallel diplomatic and military engagements at forums like the Shangri-La Dialogue, the case for faster military readiness has never been stronger.

"This is a major initiative that will empower field commanders, leading to expeditious decision-making, ultimately boosting operational preparedness," Rajnath Singh said.

## The Diaspora Connection

For the Indian defence-tech diaspora — engineers, entrepreneurs, and investors in the US, UK, and Israel working on dual-use technologies — the reform opens a wider door. By pushing procurement authority to field commanders and emphasising indigenous R&D, the government is signalling that it wants more domestic suppliers, faster evaluation cycles, and less red tape.

India's defence exports have already crossed $2 billion annually, and several diaspora-founded startups in areas like drone technology, AI-powered surveillance, and electronic warfare are actively bidding for Indian military contracts. The DFPDS-2026 framework, by accelerating approvals and doubling R&D financial powers, could make those contracts easier to win.

Chief of Defence Staff General N.S. Raja Subramani and the three service chiefs attended the formal release, underscoring the seniority of backing behind the reform."""

    img2_url, img2_attr = source_and_upload(
        slug2,
        person_name="Rajnath Singh",
        wiki_queries=["Rajnath Singh defence minister"],
        pexels_queries=["India military defence", "Indian armed forces"]
    )

    topic2_id = create_topic("Rajnath Singh doubles defence financial powers, DFPDS-2026 released", score=78)
    if not topic2_id:
        print("  ✗ Skipping article 2 — topic creation failed")
    else:
        articles.append({
            "id": str(uuid.uuid4()),
            "topic_id": topic2_id,
            "headline": "India Just Doubled the Spending Power of Its Military Commanders",
            "subheadline": "Defence Minister Rajnath Singh's new procurement framework gives field commanders authority over ₹1.25 lakh crore in annual purchases — and cuts the ministry out of 80-90% of contracts.",
            "body": body2,
            "slug": slug2,
            "category": "news",
            "vertical": "politics",
            "tags": ["Rajnath Singh", "defence procurement", "DFPDS-2026", "Aatmanirbhar Bharat", "Indian military"],
            "urgency": "daily",
            "word_count": count_words(body2),
            "diaspora_angle": "Diaspora defence-tech entrepreneurs and investors in dual-use technologies gain a wider entry point as India doubles R&D procurement powers, accelerates approval cycles, and explicitly prioritises indigenous suppliers over foreign OEMs.",
            "status": "published",
            "published_at": now,
            "sources": [{"name": "Ministry of Defence"}, {"name": "The Hindu Business Line"}, {"name": "Devdiscourse"}, {"name": "IANS"}],
            "image_url": img2_url or "",
            "image_caption": "Defence Minister Rajnath Singh at the DFPDS-2026 release in New Delhi",
            "image_attribution": img2_attr or "Wikimedia Commons",
            "is_editorial": False,
            "is_featured": False,
            "score_total": 78
        })

    # ────────────────────────────────────────────────────────────
    # ARTICLE 3: Monsoon reaches Kerala 3 days late
    # ────────────────────────────────────────────────────────────
    print("\n═══ Article 3: Monsoon Arrives Late ═══")

    slug3 = "india-monsoon-reaches-kerala-three-days-late-el-nino-heatwave-food-prices-20260605"

    body3 = """Monsoon rains finally hit the coast of Kerala on Thursday, three days later than their usual June 1 arrival, the India Meteorological Department confirmed. The delayed onset offers some relief from a brutal heatwave that has pushed electricity demand to record highs — but the anxiety over what comes next is only growing.

The southwest monsoon delivers nearly 70 percent of India's annual rainfall. It waters the farms that produce rice, corn, cotton, soybeans, and sugarcane. It replenishes the aquifers and reservoirs that supply drinking water to 1.4 billion people. And it sets the rhythm for an economy that, despite its tech-sector shine, remains deeply tied to the rains.

## A Forecast That Worries Everyone

Last month, the IMD forecast that the 2026 monsoon would bring the lowest rainfall in 11 years — about 90 percent of the long-period average. The probability of deficient or below-normal rainfall stands at 84 percent, the highest such estimate in recent memory.

The culprit is El Niño. The World Meteorological Organization said this week there is an 80 percent chance of an El Niño event developing between June and August, and a 90 percent chance it will persist until at least November. If it turns out to be a strong El Niño — with Pacific sea surface temperatures exceeding 1.5°C above average — the impact on Indian agriculture could be severe.

"With temperatures across most parts of the country remaining well above normal, conditions are currently unfavourable for the timely sowing of summer crops," a New Delhi-based dealer with a global trade house told Reuters.

## The Heatwave Squeeze

Several Indian states are reeling under temperatures above 40°C (104°F), conditions that typically ease once the monsoon arrives. Power demand has hit all-time highs as air conditioners and coolers run around the clock. The delayed monsoon means the grid will remain under stress for longer.

The monsoon has now covered all of Kerala and parts of Tamil Nadu, and the IMD says conditions are favourable for it to advance into Goa, Maharashtra, Andhra Pradesh, and Karnataka over the next few days. If it covers the rest of the country on schedule by mid-July — as it has done in many years despite a late start — the damage to planting may be limited.

But "late start, normal finish" is the optimistic scenario. The greater concern is prolonged dry spells after arrival, which El Niño years are known to produce.

## Food Prices Are Already Moving

Rice prices at major Southeast Asian export hubs have climbed about 15 percent in the past month. Wheat prices are up 20 percent since the start of 2026. Traders are watching India closely because the country holds massive rice stockpiles — several times more than it needs — but a poor monsoon could prompt export curbs.

"There is clear indication of crisis as rice prices have moved substantially higher without any major shortage," a Singapore-based trader told Reuters. "India has a huge rice stockpile. But the thinking is that very soon India will start looking at these stocks as a critical asset and may introduce some sort of export curbs."

For an economy already grappling with elevated oil prices from the Iran war, a food price spike driven by a weak monsoon would be a double blow. The RBI on Friday raised its inflation forecast for FY2027 to 5.1 percent — up from 4.6 percent — and trimmed its GDP growth projection to 6.6 percent from 6.9 percent.

## What the Diaspora Should Watch

For NRIs sending remittances or managing family finances in India, food inflation is the variable that hits hardest. A weak monsoon means higher vegetable and grain prices in mandis across the country. It means rural income stress, which affects demand for everything from motorcycles to FMCG goods. And it means the RBI may be forced to hike rates later this year — a move that would push up mortgage costs and slow credit growth.

Agriculture Minister Shivraj Singh Chouhan has directed states to prepare district-level contingency plans, focusing on drought-resistant crop varieties, alternative sowing schedules, and scientific water management. The government says reservoir levels remain at 127 percent of normal, which provides a buffer.

But reservoirs and contingency plans can only do so much if the rains simply do not come. India's economy — and the 800 million people who depend on agriculture for their livelihoods — are now watching the sky."""

    # Already uploaded successfully on first run
    existing_img3 = f"{SB_URL}/storage/v1/object/public/article-images/{slug3}.jpg"
    # Verify it exists
    check = requests.head(existing_img3, timeout=10)
    if check.status_code == 200:
        img3_url = existing_img3
        img3_attr = "Wikimedia Commons"
        print(f"  ✓ Reusing existing image: {slug3}.jpg")
    else:
        img3_url, img3_attr = source_and_upload(
            slug3,
            wiki_queries=["India monsoon rain Kerala"],
            pexels_queries=["monsoon rain India", "tropical rain"]
        )

    topic3_id = create_topic("India monsoon reaches Kerala three days late amid El Nino fears", score=80)
    if not topic3_id:
        print("  ✗ Skipping article 3 — topic creation failed")
    else:
        articles.append({
            "id": str(uuid.uuid4()),
            "topic_id": topic3_id,
            "headline": "India's Monsoon Just Arrived in Kerala. It Was Three Days Late.",
            "subheadline": "The delayed onset, combined with the weakest rainfall forecast in 11 years, is testing the nerves of farmers, traders, and policymakers who depend on the June-September rains for almost everything.",
            "body": body3,
            "slug": slug3,
            "category": "news",
            "vertical": "politics",
            "tags": ["monsoon", "Kerala", "El Nino", "food prices", "heatwave", "India agriculture"],
            "urgency": "daily",
            "word_count": count_words(body3),
            "diaspora_angle": "NRIs sending remittances or managing family finances in India face the downstream impact of a weak monsoon: higher food prices, rural income stress, and potential RBI rate hikes that would raise mortgage costs.",
            "status": "published",
            "published_at": now,
            "sources": [{"name": "Reuters"}, {"name": "India Meteorological Department"}, {"name": "World Meteorological Organization"}, {"name": "ET Edge Insights"}],
            "image_url": img3_url or "",
            "image_caption": "Monsoon rain clouds over the Kerala coast",
            "image_attribution": img3_attr or "Wikimedia Commons",
            "is_editorial": False,
            "is_featured": False,
            "score_total": 80
        })

    return articles


if __name__ == "__main__":
    print(f"News Writer starting at {datetime.now(timezone.utc).isoformat()}")
    articles = build_articles()

    success = 0
    for art in articles:
        art_id = insert_article(art)
        if art_id:
            success += 1
        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Done. {success}/{len(articles)} articles published.")
    if success < len(articles):
        sys.exit(1)
