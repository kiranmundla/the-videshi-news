#!/usr/bin/env python3
"""News writer for The Videshi — June 4, 2026 batch"""

import json, os, sys, uuid, requests, io, time, subprocess
from datetime import datetime, timezone
from urllib.parse import quote

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    if line.startswith('export '):
                        line = line[7:]
                    k, v = line.split('=', 1)
                    v = v.strip().strip('"').strip("'")
                    os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SB_URL = os.environ.get('SUPABASE_URL', '')
SB_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"

# ---- Image sourcing functions ----

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
    encoded = quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
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


def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": UA},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
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
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0)
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={quote(query)}&per_page=3&orientation=landscape"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()


def download_image(url):
    """Download image bytes from URL."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200 and r.headers.get('Content-Type', '').startswith('image'):
            if len(r.content) > 5000:
                return r.content
            else:
                print(f"  ⚠ Image too small: {len(r.content)} bytes")
        else:
            print(f"  ⚠ Image download failed: HTTP {r.status_code}")
    except Exception as e:
        print(f"  ⚠ Image download error: {e}")
    return None


def upload_to_supabase(img_bytes, filename):
    """Upload image to Supabase storage bucket 'article-images'."""
    url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    try:
        r = requests.post(url, headers=headers, data=img_bytes, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {filename}")
            return public_url
        else:
            print(f"  ⚠ Supabase upload failed: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Supabase upload error: {e}")
    return None


def source_image(person_names, wiki_queries, pexels_query, slug):
    """Multi-source image search: Wikipedia person → Wikimedia Commons → Pexels."""
    candidates = []
    
    # Source 1: Wikipedia person images
    for name in person_names:
        url = fetch_wikipedia_person_image(name)
        if url:
            candidates.append({"url": url, "source": "wikipedia", "desc": f"Photo of {name}"})
            break
    
    # Source 2: Wikimedia Commons
    for q in wiki_queries:
        results = fetch_wikimedia_commons_images(q)
        for r in results[:2]:
            candidates.append({"url": r["url"], "source": "wikimedia_commons", "desc": r["title"]})
        if results:
            break
    
    # Source 3: Pexels
    if pexels_query:
        url = fetch_pexels_image(pexels_query)
        if url:
            candidates.append({"url": url, "source": "pexels", "desc": pexels_query})
    
    # Pick best: Wikipedia > Wikimedia Commons > Pexels
    for cand in candidates:
        raw = download_image(cand["url"])
        if raw:
            compressed = compress_image(raw)
            if len(compressed) > 5000:
                filename = f"{slug}.jpg"
                public_url = upload_to_supabase(compressed, filename)
                if public_url:
                    attribution = "Wikimedia Commons" if cand["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
                    return public_url, attribution
    
    print("  ⚠ No valid image found from any source")
    return None, None


def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SB_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None


# ---- ARTICLES ----

articles = []
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ========== ARTICLE 1: India-Oman CEPA ==========
print("\n=== ARTICLE 1: India-Oman CEPA ===")

art1_slug = "india-oman-cepa-trade-pact-hormuz-bypass-gulf-gateway-20260604"
art1_headline = "India's New Trade Pact With Oman Bypasses the Strait of Hormuz. That May Matter More Than the Tariff Cuts."
art1_subheadline = "The India-Oman CEPA grants duty-free access to 99% of Indian exports — but the agreement's real strategic value lies in Oman's coastline, which sits outside the world's most dangerous chokepoint."

art1_body = """The India-Oman Comprehensive Economic Partnership Agreement came into force on June 1, 2026, and the headline numbers are impressive enough. Oman has granted duty-free access across 98% of its tariff lines, covering 99.38% of Indian exports by value. That is a leap from the previous arrangement, under which only about 15% of Indian goods entered Oman at zero duty.

But reduce this to pure trade economics and you miss the point. India's bilateral trade with Oman — $4 billion in exports, $7.16 billion in imports in FY26 — is a rounding error next to its commerce with the UAE or Saudi Arabia. Oman's GDP of $110 billion and population of 5.5 million make it a modest market. The Global Trade Research Initiative, a Delhi-based think tank, said as much: the direct trade gains will remain limited.

## Why Oman Is Not Just Another Gulf Market

The strategic calculation is geographic. Unlike every other Gulf Cooperation Council member, most of Oman's coastline lies outside the Strait of Hormuz. Its major ports — Salalah, Duqm, and Sohar — face the Arabian Sea and the Indian Ocean directly. They do not depend on passage through the narrow waterway that Iran has repeatedly threatened and that has been functionally disrupted since the U.S.-Israeli strikes began in late February.

The data makes the case. India's imports from major Gulf economies collapsed from $15 billion in April 2025 to $9.8 billion in April 2026 as the Hormuz crisis choked trade flows. Exports to the region fell from $4.4 billion to $2.7 billion over the same period.

Oman was the outlier. India's imports from Oman surged 246% year-on-year, driven almost entirely by crude oil and urea purchases rerouted away from Hormuz-dependent suppliers. India's exports to Oman declined by only 10.3% — a fraction of the regional average.

"As a result, Oman can continue serving as a reliable trade and energy gateway during periods of conflict or instability in the Gulf," said Ajay Srivastava, founder of GTRI. "The ongoing Gulf conflict has clearly demonstrated this advantage."

## What the Diaspora Gains

Nearly seven lakh Indians live and work in Oman, making the Indian community one of the largest expatriate groups in the sultanate. The CEPA includes provisions that go beyond goods, covering services, investment, and professional mobility.

Indian professionals in healthcare, architecture, taxation, and accountancy will benefit from streamlined entry and work provisions. Indian companies gain 100% foreign direct investment access in several key services sectors. A fast-track pharmaceutical approval mechanism allows drugs already cleared by the USFDA, the European Medicines Agency, or the UK's MHRA to receive accelerated regulatory clearance in Oman.

Commerce Minister Piyush Goyal described Oman as "more than a market" — a gateway to the wider GCC, East Africa, and the Indian Ocean economy. "As we speak, more than 10 consignments are being shipped availing preferential duty access in Oman from different parts of India," he said at the CEPA launch ceremony.

## The Sectors That Stand to Gain

The immediate beneficiaries are India's labour-intensive export sectors. Oman has eliminated its 5% MFN duty across all 945 textile and apparel tariff lines. Gems and jewellery, leather, footwear, pharmaceuticals, engineering goods, processed foods, and marine products all gain preferential access.

India's textile exports to Oman stood at $95.1 million in FY26 against Oman's total textile imports of $598 million, leaving substantial room for market share growth. The handicrafts sector benefits similarly, with immediate zero-duty access replacing the previous 5% levy.

Oman has also committed to lifting a decades-old ban on exporting unpolished marble, which will allow craftsmen in Rajasthan and Andhra Pradesh to source raw material directly — a niche but significant concession that reflects the agreement's attention to artisan industries.

## The Bigger Picture

The CEPA is part of a broader acceleration in India's trade diplomacy. New Delhi signed a landmark free trade agreement with the European Union in January 2026 and is now in what both sides describe as the final stages of a bilateral trade agreement with the United States.

But the Oman pact stands apart because it serves a dual purpose that no other recent agreement matches. It is simultaneously a conventional trade deal — expanding market access, reducing tariffs, opening services — and a strategic hedge against the single largest vulnerability in India's energy supply chain: the Strait of Hormuz.

The agreement was signed in Muscat in December 2025, in the presence of Prime Minister Modi and Sultan Haitham bin Tarik. At the time, the Hormuz crisis was already underway but not yet at its current intensity. Four months later, with the strait still largely closed, the timing looks less like foresight and more like necessity.

*Sources: Reuters, The Hindu BusinessLine, DevDiscourse, Global Trade Research Initiative, Ministry of Commerce and Industry*"""

img1_url, img1_attr = source_image(
    person_names=["Piyush Goyal"],
    wiki_queries=["Oman port Muscat trade", "Port of Salalah Oman"],
    pexels_query="Oman port shipping trade",
    slug=art1_slug
)

articles.append({
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "slug": art1_slug,
    "category": "news",
    "vertical": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": now,
    "sources": json.dumps(["Reuters", "The Hindu BusinessLine", "DevDiscourse", "GTRI"]),
    "image_url": img1_url,
    "image_caption": "The Port of Salalah in Oman, located outside the Strait of Hormuz on the Arabian Sea coastline",
    "image_attribution": img1_attr or "Wikimedia Commons"
})


# ========== ARTICLE 2: Clean Energy Grid Rules ==========
print("\n=== ARTICLE 2: Clean Energy Grid Rules ===")

art2_slug = "india-clean-energy-grid-rules-kkr-cppib-actis-investor-alarm-20260604"
art2_headline = "India's New Grid Rules Could Cut Solar Revenues by 11% and Wind by 48%. The Investors Are Already Walking."
art2_subheadline = "KKR, Canada Pension Plan, Actis, and Macquarie-backed Blueleaf have warned Indian officials that tighter power grid penalties are advancing faster than the infrastructure to support them."

art2_body = """India's renewable energy sector is facing a regulatory collision. Tougher grid discipline rules, set to take full effect in April 2027, will sharply increase penalties when solar and wind producers fail to deliver electricity matching their commitments — and the investors who have poured billions into the sector say the country is not ready for them.

Industry groups estimate the revised framework could cut revenue by approximately 11% for solar projects and as much as 48% for wind farms, according to investor presentations and documents reviewed by Reuters. The potential impact has turned what was a technical regulatory dispute into a full-blown investor confidence crisis.

## Who Raised the Alarm

The scale of concern became clear in April, when a group of major foreign investors met with Indian officials to deliver a blunt warning. KKR, Canada Pension Plan Investment Board, and Actis — three of the largest institutional investors in India's clean energy sector — raised concerns about lower returns, policy unpredictability, and financial stress from the tighter rules, according to five industry sources familiar with the discussions.

Their core argument: regulatory tightening is advancing faster than improvements in transmission infrastructure and battery storage capacity. The grid itself cannot absorb what the new rules demand.

Blueleaf Energy, a clean energy producer backed by Australia's Macquarie Asset Management, put the tension in practical terms. "The market has not yet developed for generators to be that accurate," said Pratyush Thakur, Blueleaf's India country head. The company plans to deploy about $3 billion in India, including $1 billion in equity over the next three years, but now expects grid-related constraints to delay that equity deployment by two to three additional years.

## What the Rules Actually Do

Under the revised framework, penalties escalate based on the gap between scheduled and actual power supplied to the grid. Solar and wind generators are inherently variable — output depends on weather conditions that cannot be perfectly predicted. The current penalty regime accommodates that variability. The new rules tighten the tolerance bands significantly.

"Developers will face very high penalties even when deviations are small. This tightens margins, revenues will shrink and project viability will be affected," said Debabrat Ghosh, India head at Aurora Energy Research.

The federal power regulator has defended the tighter framework as essential for grid stability. As renewable capacity expands — India had 288 GW of non-fossil fuel capacity as of March, with wind and solar accounting for 73% — the grid faces increasing challenges managing intermittent supply. In the first quarter of 2026 alone, curtailments due to grid and transmission constraints reached 300 GWh, representing two-thirds of total curtailments in the period, according to climate think tank Ember.

## The Infrastructure Gap

Developers say India lacks several tools needed to meet the tighter standards. Weather forecasts are typically updated only a few times daily, compared with near-real-time forecasting in European power markets. Battery storage remains limited. Transmission infrastructure has not kept pace with the renewable capacity buildout.

Industry groups have appealed directly to the Prime Minister's Office for relief, according to two sources. The Ministry of New and Renewable Energy has held discussions with industry groups and appears open to easing implementation of the rules.

But the Ministry of Power, the Central Electricity Authority, and Grid India — the country's grid operator — have maintained that stricter enforcement is necessary to prevent grid instability. None responded to Reuters' requests for comment.

## Why It Matters for India's Climate Targets

India has committed to installing 500 GW of non-fossil fuel capacity by 2030. Reaching that target from the current 288 GW requires sustained annual additions of roughly 50 GW — a pace that demands billions of dollars in foreign capital flowing steadily into the sector.

The risk is straightforward: if the regulatory environment makes renewable investments less attractive relative to other markets, capital will redirect elsewhere. India is competing for the same pool of institutional clean energy investment as Southeast Asia, the Middle East, and Latin America.

Actis said India remained one of its preferred investment destinations. KKR and Canada Pension Plan Investment Board did not respond to Reuters' requests for comment. But the very fact that these investors felt compelled to raise concerns directly with government officials — rather than simply adjusting their portfolios quietly — signals the severity of their alarm.

The clean energy ministry's willingness to engage suggests the government recognises the tension. The question is whether the easing comes quickly enough to prevent commitments from being deferred — or quietly redirected to markets where the rules of the game are not changing mid-play.

*Sources: Reuters, OilPrice.com, Ember, The Hindu BusinessLine*"""

img2_url, img2_attr = source_image(
    person_names=[],
    wiki_queries=["India solar energy farm renewable", "solar panels India"],
    pexels_query="solar energy farm India",
    slug=art2_slug
)

articles.append({
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "slug": art2_slug,
    "category": "news",
    "vertical": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": now,
    "sources": json.dumps(["Reuters", "OilPrice.com", "Ember", "The Hindu BusinessLine"]),
    "image_url": img2_url,
    "image_caption": "A solar energy installation in India, part of the country's push toward 500 GW of non-fossil fuel capacity by 2030",
    "image_attribution": img2_attr or "Pexels"
})


# ========== ARTICLE 3: Rubio Testimony - India in US Foreign Policy ==========
print("\n=== ARTICLE 3: Rubio Testimony — India in US Foreign Policy ===")

art3_slug = "rubio-congress-testimony-india-central-us-foreign-policy-quad-trade-20260604"
art3_headline = "Rubio Told Congress That India Is Central to American Foreign Policy. He Was Not Exaggerating."
art3_subheadline = "In a marathon Congressional testimony, the Secretary of State cited India more than any other partner — on trade, the Quad, de-escalation with Pakistan, and the Indo-Pacific strategy that now anchors Washington's Asia doctrine."

art3_body = """Secretary of State Marco Rubio appeared before the House Foreign Affairs Committee on Wednesday to defend the State Department's Fiscal Year 2027 budget. The hearing was combative, interrupted by partisan clashes over Iran, Trump's financial dealings, and the appointment of loyalists to national security posts. But buried in the noise was a signal that mattered more than the fireworks: Rubio cited India more often than any other country when listing what he called the administration's diplomatic achievements.

The testimony was not a courtesy mention. It was a strategic positioning of India at the centre of the Trump administration's foreign policy architecture — across trade, defence, multilateral frameworks, and regional crisis management.

## The Trade Deal

The most immediate takeaway for New Delhi was Rubio's disclosure that the U.S.-India bilateral trade agreement is now weeks away from conclusion.

"The hopes that we can wrap up the negotiations on our trade agreement, which we think were a few weeks away from being able to conclude," Rubio told lawmakers, responding to questions from Rep. Bill Huizenga about his recent India visit. "Both sides want to see it done."

India's Commerce Minister Piyush Goyal offered a parallel confirmation on Thursday, announcing that an American trade delegation would travel to India next month for critical bilateral discussions. "There is some plan for them to come next month," Goyal said, clarifying that the delegation would be separate from Rubio's own diplomatic schedule.

India's Ambassador to the U.S., Sergio Gor, expressed confidence that the deal would be finalised in the "coming weeks and months," drawing a pointed comparison with the EU-India trade agreement that took nearly 19 years to close.

## The Quad and Indo-Pacific

Rubio used his testimony to elevate the Quad — the grouping of India, the United States, Japan, and Australia — as a cornerstone of the administration's Indo-Pacific strategy.

"The Quad, an important alliance in the Indo-Pacific between India, Japan, Australia — we've had multiple meetings of that group, including a meeting just last week in India and a follow-up that's going to occur later this year, including a leaders' meeting before the end of the year," Rubio told the committee.

The framing was deliberate. At a moment when the administration faces Congressional scrutiny over its handling of the Iran conflict and its commitment to Ukraine, Rubio positioned the Indo-Pacific — and India specifically — as the arena where American diplomacy is producing tangible results without military escalation.

## India-Pakistan De-escalation

Rubio opened his testimony by listing the State Department's recent achievements. The first item on his list was not Iran, not Ukraine, not China. It was India and Pakistan.

"India and Pakistan were on the verge of an all-out war. The State Department and I personally were involved in de-escalating that conflict and bringing it to an end — a war between two nuclear powers," Rubio said.

The reference was brief and offered no operational details, but its placement at the top of the administration's diplomatic achievements list was notable. It suggests the White House views the India-Pakistan de-escalation as one of its strongest foreign policy credentials — and one it is prepared to cite in domestic political arguments.

## What This Means for the Diaspora

For the estimated 4.4 million Indian Americans, the Congressional hearing carried a practical message: India's centrality in Washington's strategic calculations translates into sustained policy attention on issues that directly affect the diaspora — trade facilitation, visa regimes, defence cooperation, and the diplomatic bandwidth allocated to India-related concerns.

The trade deal, if concluded as Rubio suggested, would reshape the tariff landscape for goods flowing between the two countries. It would also provide a framework for addressing long-standing irritants, including market access restrictions, intellectual property disputes, and agricultural trade barriers that have festered through multiple administrations.

The Quad elevation matters differently. It locks India into a multilateral security architecture that both parties have an interest in maintaining, reducing the risk that India becomes collateral damage in Washington's other geopolitical confrontations — whether with China over Taiwan or with Iran over the strait.

## The Hearing's Other Moments

The India content competed for attention with sharp exchanges over the administration's conduct of the Iran war, the appointment of Bill Pulte as acting Director of National Intelligence, and accusations by Rep. Ted Lieu that Trump had fallen asleep during meetings.

Rubio grew visibly frustrated with the partisan tone. "Is this the Foreign Affairs Committee, or is this like a circus? What is this?" he asked at one point. He defended Trump's work ethic by saying the president "literally doesn't sleep" and "works day and night."

But the substantive content of the testimony — the items Rubio chose to lead with, the countries he cited as evidence of success — told a clearer story than the confrontations. India was not mentioned as a challenge, a problem, or a complication. It was mentioned as a partnership that is delivering results. In a hearing where almost everything else was contested, that positioning was not accidental.

*Sources: U.S. Department of State, IANS, The Indian EYE, Fox News, Washington Examiner*"""

img3_url, img3_attr = source_image(
    person_names=["Marco Rubio"],
    wiki_queries=["Marco Rubio Secretary of State", "US India diplomacy"],
    pexels_query="US Congress hearing diplomacy",
    slug=art3_slug
)

articles.append({
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "body": art3_body,
    "slug": art3_slug,
    "category": "news",
    "vertical": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": now,
    "sources": json.dumps(["U.S. Department of State", "IANS", "The Indian EYE", "Fox News", "Washington Examiner"]),
    "image_url": img3_url,
    "image_caption": "U.S. Secretary of State Marco Rubio, who cited India as central to American foreign policy during Congressional testimony",
    "image_attribution": img3_attr or "Wikimedia Commons"
})


# ---- Insert all articles ----
print("\n=== INSERTING ARTICLES ===")
for art in articles:
    if not art.get("image_url"):
        print(f"  ⚠ Skipping image for {art['slug']} — no valid image found")
        del art["image_caption"]
        del art["image_attribution"]
        art.pop("image_url", None)
    
    art_id = insert_article(art)
    if art_id:
        print(f"  ✅ Published: {art['headline'][:60]}...")
    else:
        print(f"  ❌ Failed: {art['headline'][:60]}...")
    time.sleep(1)

print("\n=== NEWS WRITER COMPLETE ===")
print(f"Total articles attempted: {len(articles)}")
