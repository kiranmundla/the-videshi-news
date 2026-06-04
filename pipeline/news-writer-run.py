#!/usr/bin/env python3
"""
News writer — 2026-06-04 run
3 articles: US forced labor tariffs, UK-India FTA steel dispute, Foreign investors short India debt
"""
import requests
import json
import os
import uuid
import time
from datetime import datetime, timezone
from PIL import Image
import io

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, val = line.partition('=')
                    val = val.strip().strip('"').strip("'")
                    os.environ.setdefault(key.strip(), val)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')
UA = "TheVideshi/1.0 (thevideshi.com)"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
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
                if not mime.startswith("image/"):
                    continue
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for a relevant image. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    import subprocess
    try:
        import urllib.parse
        encoded = urllib.parse.quote(query)
        cmd = f'curl -sS "https://api.pexels.com/v1/search?query={encoded}&per_page=3" -H "Authorization: {PEXELS_KEY}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{query}': {url[:60]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None

def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
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
    """Download image bytes."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200 and 'image' in r.headers.get('Content-Type', ''):
            if len(r.content) > 5000:
                return r.content
            else:
                print(f"  ⚠ Image too small: {len(r.content)} bytes")
    except Exception as e:
        print(f"  ⚠ Download error: {e}")
    return None

def upload_to_supabase(img_bytes, filename):
    """Upload image to Supabase storage bucket 'article-images'."""
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    try:
        r = requests.post(url, headers=headers, data=img_bytes, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {filename}")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None

def source_image(slug, person_name=None, wiki_search=None, pexels_query=None):
    """Multi-source image search: Wikipedia → Wikimedia Commons → Pexels. Returns (url, attribution) or (None, None)."""
    candidates = []
    
    # Source 1: Wikipedia person image
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "priority": 1})
    
    # Source 2: Wikimedia Commons
    if wiki_search:
        commons = fetch_wikimedia_commons_images(wiki_search)
        for c in commons[:3]:
            candidates.append({"url": c["url"], "source": "wikimedia_commons", "priority": 2})
    
    # Source 3: Pexels
    if pexels_query:
        pexels_img = fetch_pexels_image(pexels_query)
        if pexels_img:
            candidates.append({"url": pexels_img, "source": "pexels", "priority": 3})
    
    # Try each candidate in priority order
    for cand in sorted(candidates, key=lambda x: x["priority"]):
        img_bytes = download_image(cand["url"])
        if img_bytes:
            compressed = compress_image(img_bytes)
            if len(compressed) >= 10000:
                filename = f"{slug}.jpg"
                final_url = upload_to_supabase(compressed, filename)
                if final_url:
                    attr = "Wikimedia Commons" if cand["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
                    print(f"  ✓ Selected image from {cand['source']}: {len(compressed)} bytes")
                    return final_url, attr
            else:
                print(f"  ⚠ Compressed image too small: {len(compressed)} bytes, skipping")
    
    print(f"  ⚠ No suitable image found for {slug}")
    return None, None

def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Published: {article['headline'][:60]}... (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None

# ============================================================
# ARTICLE 1: US proposes 12.5% forced labor tariffs on India
# ============================================================
print("\n" + "="*60)
print("ARTICLE 1: US Section 301 forced labor tariffs")
print("="*60)

art1_slug = "us-section-301-forced-labor-tariffs-india-12-percent-60-countries-20260604"
art1_headline = "Trump Just Proposed a 12.5% Tariff on India Over Forced Labour. Sixty Countries Are in the Crosshairs."
art1_subheadline = "The Section 301 investigation is designed to rebuild the tariff architecture the Supreme Court dismantled in February. India rejected the allegations and said it would seek resolution through trade talks."

art1_body = """The Trump administration proposed tariffs of up to 12.5 per cent on imports from 60 countries on Tuesday, citing their failure to curb trade in goods made with forced labour. India, placed in the higher-tariff tier alongside China, Japan, South Korea and Brazil, dismissed the allegations and said it would address the issue through ongoing bilateral trade negotiations.

The proposal, issued by the Office of the United States Trade Representative under Section 301 of the Trade Act of 1974, is an attempt to reconstruct the tariff regime that collapsed after the Supreme Court struck down Trump's emergency tariffs in February. Unlike the earlier tariffs, which relied on broad executive authority, Section 301 provides a more durable legal foundation — these tariffs have no statutory expiration dates or maximum percentage caps.

## What the Proposal Covers

The USTR divided the 60 countries into two tiers. Fourteen economies — including Canada, the European Union, Britain, Mexico, Indonesia, Pakistan, Argentina, Bangladesh and Taiwan — would face 10 per cent additional duties. These countries were credited with having partial enforcement frameworks or commitments under existing trade agreements.

The remaining 45 countries, including India, China, Nigeria, Japan, South Korea, Vietnam, Australia and New Zealand, would face 12.5 per cent duties. The USTR determined these nations had not taken adequate steps to prohibit or enforce bans on imports of goods produced with forced labour.

For India specifically, the USTR identified exposure across sectors including aluminium, cotton, fish, coffee, nickel, palm oil and rice. The allegation is that India imported forced-labour-linked inputs and exported downstream products to the United States.

Certain categories — energy, pharmaceuticals, beef, coffee and some fruits and vegetables — are exempt from the proposed tariffs.

## The Legal Architecture

The shift from emergency tariffs to Section 301 is strategic. Trade lawyers have noted that Section 301 tariffs have been far less vulnerable to judicial challenge. The tariffs imposed on Chinese goods under this mechanism during Trump's first term remain in place years later.

"Section 301 allows the government to investigate foreign nations suspected of violating trade agreements or engaging in practices that systematically disadvantage American businesses," noted legal analysts tracking the case. "Crucially, tariffs implemented under Section 301 have no statutory expiration dates."

The proposed tariffs will not take effect immediately. The USTR has opened a formal public comment period running through 6 July, with public hearings scheduled for 7 July.

## India's Response

India rejected the forced-labour allegations and signalled it would seek resolution through the bilateral trade agreement currently under negotiation. The timing is significant: US chief negotiator Brendan Lynch visited New Delhi from 1 to 4 June for talks on the proposed interim agreement, and both sides have described the deal as "99 per cent done."

Commerce Minister Piyush Goyal has repeatedly said India is seeking a fair, balanced agreement that provides a competitive advantage over other Asian manufacturing hubs. The forced-labour tariffs could complicate those negotiations, adding a new layer of friction just as the two governments appeared close to a framework deal.

## What It Means for the Diaspora

For Indian exporters and NRI business owners with supply chains spanning both countries, the proposed tariffs threaten to raise costs across multiple sectors. Aluminium, cotton textiles and processed food products — categories where Indian exports to the US are substantial — could face immediate price pressure.

The tariffs also arrive at a delicate moment for the rupee, which has already weakened 6.5 per cent this year under pressure from the Iran-war-driven oil shock and sustained foreign portfolio outflows. Additional trade friction with the United States would add to the headwinds facing India's external accounts.

Human Rights Watch noted that forced labour is embedded in supply chains globally, including in the United States itself. "Singling out some countries just based on trade volumes is questionable and may even be counterproductive," said Helene de Rengerve, a corporate responsibility official at the organisation.

The proposal remains open for public comment. Whether it ultimately takes effect will depend on the hearings, the trajectory of the bilateral trade deal, and the broader geopolitical calculus between Washington and New Delhi.

**Sources**: Reuters, Barron's, GKToday, Office of the US Trade Representative"""

# Source image
print("  Sourcing image...")
art1_img_url, art1_img_attr = source_image(
    art1_slug,
    person_name="Jamieson Greer",
    wiki_search="US Trade Representative Section 301 tariffs",
    pexels_query="US trade tariffs shipping containers"
)

art1 = {
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "slug": art1_slug,
    "category": "news",
    "vertical": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": art1_img_url,
    "image_caption": "US Trade Representative Jamieson Greer announced the proposed tariffs under Section 301",
    "image_attribution": art1_img_attr or "Pexels",
    "sources": json.dumps(["Reuters", "Barron's", "GKToday", "Office of the US Trade Representative"])
}
if not art1_img_url:
    art1.pop("image_url")
    art1.pop("image_caption")
    art1.pop("image_attribution")

insert_article(art1)
time.sleep(1)

# ============================================================
# ARTICLE 2: UK-India FTA stalls over steel
# ============================================================
print("\n" + "="*60)
print("ARTICLE 2: UK-India FTA steel dispute")
print("="*60)

art2_slug = "uk-india-trade-deal-steel-dispute-whisky-tariff-delay-autumn-20260604"
art2_headline = "India's Trade Deal With Britain Is Stuck on Steel. Scotch Whisky Is Being Used as Leverage."
art2_subheadline = "Britain's new steel safeguards cut tariff-free imports by 60 per cent. India is now reviewing the duty concessions it offered on whisky, automobiles and medical devices as a countermeasure."

art2_body = """Britain's trade minister Peter Kyle returned from Delhi on Wednesday insisting the UK-India free trade deal would not be reopened. But he also conceded, almost in the same breath, that implementation might slip to autumn — months later than India had expected and well past the anniversary of the agreement's signing.

The free trade agreement, hailed as a landmark when it was signed in July 2025, was supposed to enter force within about a year. Britain would slash 99 per cent of its tariffs on Indian goods. India would cut 90 per cent of its tariffs on British products. But a steel dispute has pulled the deal into a holding pattern, and both sides are now using their best bargaining chips as leverage.

## The Steel Problem

At the heart of the impasse is Britain's decision to introduce stricter steel safeguard measures effective 1 July. The new policy would cut tariff-free steel import quotas by 60 per cent compared to current levels and impose a 50 per cent duty on volumes exceeding the cap.

For Indian steel exporters, the measures represent a fundamental disruption. India has emerged as a significant exporter of finished and semi-finished steel to the UK market, and the safeguards would sharply limit that access — despite the free trade agreement's explicit promise of liberalised trade.

The British government framed the move as domestic industrial policy, citing the need to protect UK steelmaking capacity at a time when it has already nationalised British Steel to prevent job losses. A British official said the implementation talks were "separate" from the steel measures, though Indian officials clearly disagree.

## India's Counter-Move

New Delhi has responded by reviewing the tariff concessions it offered Britain on Scotch whisky, automobiles, medical devices and other products. Under the deal, India had agreed to cut import duties on UK whisky and gin from 150 per cent to 75 per cent immediately, with phased reductions to 40 per cent over ten years.

That whisky concession was one of Britain's most visible commercial wins in the entire agreement. India is one of the world's largest and most attractive spirits markets, and Scotch producers had been lobbying for decades for lower duties. If India withdraws or modifies the concession, the political fallout in Britain would be substantial.

"India argues that such measures could hurt Indian steel exporters and undermine market access promised under the trade deal," trade analysts noted. "The immediate issue is Scotch whisky versus steel. The larger issue is whether each side believes the agreement remains commercially balanced once domestic protection measures are introduced."

## The Timing Problem

Kyle's acknowledgement that autumn implementation would still represent "the fastest implementation period of any trade deal that Britain has ever signed" is accurate but misses the broader context. India had been operating on a May timeline. A slip of several months, driven by British domestic protectionism, risks eroding trust between the two governments at a moment when both face separate trade pressures from the United States.

The US forced-labour tariff proposal, announced the same day Kyle was briefing reporters in London, adds another dimension. Britain was placed in the lower 10 per cent tariff tier — a vindication Kyle pointed to. India faces 12.5 per cent. The divergence means both countries now have reason to ensure their bilateral deal works, even as their respective trade relationships with Washington grow more complicated.

## Why NRIs Should Pay Attention

The UK-India FTA matters directly to the 1.9 million people of Indian heritage living in Britain. The deal was designed to lower costs on everything from Indian textiles and food products entering the UK to British financial services and education exports reaching India.

A delayed or weakened implementation would postpone those benefits. For NRI business owners operating in both markets — particularly in sectors like food, fashion, pharmaceuticals and professional services — the uncertainty around steel safeguards and retaliatory tariff reviews creates planning headaches that a signed deal was supposed to eliminate.

**Sources**: Reuters, Financial News, Global Banking and Finance, Whalesbook, Business News Today"""

# Source image
print("  Sourcing image...")
art2_img_url, art2_img_attr = source_image(
    art2_slug,
    person_name="Peter Kyle",
    wiki_search="UK India free trade agreement steel",
    pexels_query="steel factory industrial UK"
)

art2 = {
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "slug": art2_slug,
    "category": "news",
    "vertical": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": art2_img_url,
    "image_caption": "UK Trade Minister Peter Kyle after returning from trade talks in New Delhi",
    "image_attribution": art2_img_attr or "Pexels",
    "sources": json.dumps(["Reuters", "Financial News", "Global Banking and Finance", "Whalesbook", "Business News Today"])
}
if not art2_img_url:
    art2.pop("image_url")
    art2.pop("image_caption")
    art2.pop("image_attribution")

insert_article(art2)
time.sleep(1)

# ============================================================
# ARTICLE 3: Foreign investors pivot to short India debt
# ============================================================
print("\n" + "="*60)
print("ARTICLE 3: Foreign investors short India debt")
print("="*60)

art3_slug = "foreign-investors-pivot-short-india-bonds-rbi-rate-decision-rupee-20260604"
art3_headline = "Foreign Investors Are Quietly Shifting to Short-Term Indian Bonds. The Signal Is Hard to Ignore."
art3_subheadline = "Two-thirds of top foreign bond purchases in March through May were in maturities under five years. The front end of the curve now offers better risk-adjusted carry — and the back end is a bet most fund managers do not want to take."

art3_body = """Overseas investors are staging a quiet but significant shift in the way they hold Indian government debt. Over the past three months, they have moved decisively toward short-term bonds, abandoning the long end of the yield curve as inflation risks mount and the Reserve Bank of India faces its most difficult policy decision in years.

Bonds with maturities of less than five years made up over two-thirds of the top ten notes foreign investors purchased during March through May, according to clearing house data compiled by Reuters. That is a sharp increase from less than half in January and February. The rebalancing happened as yields climbed, the rupee fell, and the Iran-war-driven energy shock upended the inflation outlook.

## The Math Behind the Move

The ten-year benchmark bond yield has risen 34 basis points from March to May. The five-year yield has risen 55 basis points. The spread between the two dropped to an eight-month low of 15 basis points, a textbook signal that the market expects tighter monetary policy and is front-loading that bet by buying the short end.

"In such an environment, the front end offers more attractive risk-adjusted carry with lower duration risk, while the long end remains vulnerable to further repricing if the tightening cycle materialises," said Krishna Bhimavarapu, APAC economist at State Street Investment Management.

The logic is straightforward. Short-term bonds lock in higher yields while limiting the losses that would come from a rate hike. If the RBI raises rates — as Standard Chartered has predicted with a 25-basis-point increase — holders of ten-year or longer bonds would see their prices fall more sharply than holders of three-year or five-year paper.

## The RBI's Dilemma

The Reserve Bank of India will announce its rate decision on Friday morning. Most economists polled by Reuters expect Governor Sanjay Malhotra to hold the repo rate at 5.25 per cent, but the decision is anything but routine.

Brent crude remains elevated near $96 a barrel. The rupee has fallen 6.5 per cent this year, making it one of the weakest-performing Asian currencies. Foreign portfolio investors have been pulling money out of Indian equities for weeks. And overnight indexed swaps — a forward-looking market indicator — are already pricing in a rate hike.

"We expect the RBI to hold rates steady, while signalling readiness to respond, should inflation risks intensify and second-round pressures begin to emerge," said Madhavi Arora of Emkay Global Financial Services.

A more hawkish guidance without an actual hike would likely push the rupee lower in the short term, according to traders, but the central bank's aggressive FX swap operations over the past ten days suggest it is prepared to intervene. One-year hedging costs have already dropped from a mid-May peak of 3.50 per cent to 2.92 per cent, compressed by RBI's buy-sell dollar-rupee swaps.

## What Changed the Calculus

Foreign investors had been net buyers of Indian bonds through early 2026, attracted by the country's inclusion in major global bond indices and yields that looked generous compared with developed markets. In January and February, overseas investors bought bonds worth 221 billion rupees.

Then came March. As the Iran crisis escalated and crude prices surged, foreign investors sold a record 177 billion rupees in Indian bonds in a single month. They turned buyers again in April and May, but the composition of their purchases had changed — shorter maturities, less duration risk, a more defensive posture.

"The curve has bear-flattened with short-end yields rising more than the long-end yields. This has created a valuations-driven opportunity for foreign investors to buy short-end bonds," said Nagaraj Kulkarni, chief rates strategist for South Asia and Indonesia at Standard Chartered.

## The Diaspora Angle

For NRIs with investments in Indian fixed-income markets — whether through NRE or NRO deposits, mutual fund debt schemes, or direct government bond holdings — the bond market dynamics carry practical implications. Short-term deposit rates are likely to rise if the RBI turns hawkish, making fresh deposits more attractive. But existing long-duration bond holdings could lose value if a tightening cycle begins.

The government's recent decision to scrap capital gains tax on foreign investment in government bonds — announced earlier this week in a bid to stem rupee outflows — may attract some fresh inflows. But the structural picture is clear: investors are positioning for a world in which Indian interest rates go up, not down.

Friday's decision will reveal whether the central bank agrees.

**Sources**: Reuters, Outlook Money, The Hindu BusinessLine, ANZ Research, Standard Chartered"""

# Source image
print("  Sourcing image...")
art3_img_url, art3_img_attr = source_image(
    art3_slug,
    person_name="Sanjay Malhotra RBI",
    wiki_search="Reserve Bank of India Mumbai building",
    pexels_query="Indian stock market trading bonds"
)

art3 = {
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "body": art3_body,
    "slug": art3_slug,
    "category": "news",
    "vertical": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": art3_img_url,
    "image_caption": "The Reserve Bank of India headquarters in Mumbai, where the MPC will announce its rate decision on Friday",
    "image_attribution": art3_img_attr or "Wikimedia Commons",
    "sources": json.dumps(["Reuters", "Outlook Money", "The Hindu BusinessLine", "ANZ Research", "Standard Chartered"])
}
if not art3_img_url:
    art3.pop("image_url")
    art3.pop("image_caption")
    art3.pop("image_attribution")

insert_article(art3)

print("\n" + "="*60)
print("Done! All 3 articles published.")
print("="*60)
