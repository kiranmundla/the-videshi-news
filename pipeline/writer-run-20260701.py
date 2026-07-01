#!/usr/bin/env python3
"""
Videshi News Writer — July 1, 2026 run
Writes 2 articles: semiconductor milestone + SCOTUS birthright ruling
"""

import os, json, requests, subprocess, sys, re, uuid
from datetime import datetime, timezone

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                val = val.strip().strip('"').strip("'")
                os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

UA = 'TheVideshi/1.0 (thevideshi.com)'

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
    encoded = person_name.replace(' ', '_')
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
        "iiprop": "url|size|mime|extmetadata",
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
                title = page.get("title", "")
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": title,
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons API error for '{search_query}': {e}")
    return []


def search_pexels(query, per_page=5):
    """Search Pexels for stock images using curl (Python requests gets 403)."""
    try:
        result = subprocess.run(
            ['curl', '-sS', '-H', 'Authorization: 563492ad6f91700001000001e3400f5c5e1e4d0387f8e46f0e2d6291',
             f'https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page={per_page}'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                print(f"  ✓ Pexels: {len(photos)} images found for '{query}'")
                return [{'url': p['src']['large2x'], 'photographer': p.get('photographer', '')} for p in photos]
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return []


def verify_image_url(url):
    """Verify an image URL returns HTTP 200 with image content-type and >5KB."""
    try:
        r = subprocess.run(
            ['curl', '-sS', '-o', '/dev/null', '-w', '%{http_code} %{content_type} %{size_download}',
             '-A', UA, '-L', url],
            capture_output=True, text=True, timeout=15
        )
        if r.returncode == 0:
            parts = r.stdout.strip().split()
            code = parts[0] if parts else ''
            ctype = parts[1] if len(parts) > 1 else ''
            size = float(parts[2]) if len(parts) > 2 else 0
            if code == '200' and 'image' in ctype and size > 5000:
                print(f"  ✓ Image verified: {url[:80]}... ({size:.0f} bytes)")
                return True
            else:
                print(f"  ✗ Image check failed: code={code}, type={ctype}, size={size}")
    except Exception as e:
        print(f"  ⚠ Image verify error: {e}")
    return False


def insert_article(article):
    """Insert article into Supabase p2_articles table."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Article inserted: {result[0].get('slug', 'unknown')}")
            return result[0]
        print(f"  ✓ Article inserted (no body returned)")
        return result
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


def commons_relevance_ok(title, headline, topic):
    """Check if a Commons file title is relevant to the article."""
    title_lower = title.lower()
    headline_lower = headline.lower()
    
    # Extract distinctive keywords from headline/topic (len>=4, skip generic)
    generic = {'from', 'with', 'that', 'this', 'just', 'have', 'been', 'will',
               'what', 'here', 'more', 'than', 'when', 'year', 'also', 'into',
               'over', 'most', 'some', 'made', 'make', 'back', 'only', 'even',
               'they', 'their', 'after', 'about', 'could', 'would', 'first',
               'people', 'other', 'which', 'world', 'under', 'every', 'where',
               'three', 'being', 'state', 'national', 'social', 'media'}
    words = re.findall(r'[a-zA-Z]+', headline_lower + ' ' + (topic or '').lower())
    distinctive = [w for w in words if len(w) >= 4 and w not in generic]
    
    if not distinctive:
        return True  # Don't over-filter all-generic headlines
    
    # At least one distinctive keyword must appear in the file title
    for kw in distinctive:
        if kw in title_lower:
            return True
    return False


# ============================================================
# ARTICLE 1: India's Semiconductor Chip Milestone
# ============================================================

def write_semiconductor_article():
    print("\n=== ARTICLE 1: India's Semiconductor Milestone ===\n")
    
    slug = "india-first-semiconductor-chip-shipment-cg-semi-sanand-third-plant-july-20260701"
    
    # Image sourcing
    print("Sourcing images...")
    
    # Try Wikimedia Commons for semiconductor/chip manufacturing images
    commons_results = fetch_wikimedia_commons_images("semiconductor chip manufacturing India", limit=5)
    commons_results += fetch_wikimedia_commons_images("CG Power India semiconductor", limit=5)
    commons_results += fetch_wikimedia_commons_images("semiconductor wafer fabrication plant", limit=5)
    
    hero_url = None
    hero_caption = None
    hero_attribution = None
    
    # Check Commons results for relevance
    for img in commons_results:
        if commons_relevance_ok(img['title'], "India semiconductor chip", "semiconductor manufacturing"):
            if verify_image_url(img['url']):
                hero_url = img['url']
                hero_caption = f"Semiconductor wafer processing at an advanced chip fabrication facility"
                hero_attribution = "Wikimedia Commons"
                break
    
    # Fallback to Pexels for semiconductor imagery
    if not hero_url:
        pexels = search_pexels("semiconductor chip manufacturing circuit board", per_page=5)
        for p in pexels:
            if verify_image_url(p['url']):
                hero_url = p['url']
                hero_caption = "Advanced semiconductor chip on a circuit board"
                hero_attribution = f"Pexels / {p.get('photographer', 'Unknown')}"
                break
    
    if not hero_url:
        print("  ✗ No suitable hero image found, trying direct Wikimedia file")
        # Try a known semiconductor image
        direct_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Silicium.jpg/1200px-Silicium.jpg"
        if verify_image_url(direct_url):
            hero_url = direct_url
            hero_caption = "A silicon wafer — the foundation of modern semiconductor chips"
            hero_attribution = "Wikimedia Commons"
    
    if not hero_url:
        print("  ✗ CRITICAL: No hero image found. Skipping article.")
        return None
    
    headline = "India Just Shipped Its First Semiconductor Chips Abroad. The Third Factory Starts This Month."
    subheadline = "CG Semi's Sanand plant sent its first commercial chip shipment to Malaysia in June — and India's semiconductor mission is about to cross another threshold as a third plant goes live in July."
    
    body = """India's semiconductor ambitions crossed a milestone that no policy document, subsidy announcement, or prime ministerial speech could have delivered on its own: on June 19, the first commercial shipment of 'Made in India' semiconductor chips left CG Semi's Sanand facility in Gujarat, bound for Kuala Lumpur.

The chips — microcontrollers packaged and tested for Japan's Renesas Electronics — were produced at India's first operational Outsourced Semiconductor Assembly and Test (OSAT) plant, a joint venture between CG Power's Murugappa Group, Renesas, and Thailand's Stars Microelectronics. The facility, built at an investment of ₹7,600 crore, completed its pilot line in August 2025 and transitioned to commercial production earlier this year.

## From Zero to Three Plants in Four Years

The shipment comes as India's semiconductor mission is about to notch another milestone. Union Electronics Minister Ashwini Vaishnaw confirmed in May that a third semiconductor manufacturing facility will begin commercial production in July, with a fourth set to follow by November or December. Two plants — Micron's memory packaging unit and CG Semi's G1 line, both at Sanand — are already producing commercially.

"In 1962, we started this journey. So many prime ministers tried," Vaishnaw said at the CII Annual Business Summit. "Finally, the success came to Prime Minister Narendra Modi, and today we have two factories which are already doing commercial production."

Work is underway on 12 semiconductor factories across the country under the India Semiconductor Mission (ISM), with an approved investment pipeline of approximately ₹1.64 lakh crore. The mission's second phase, ISM 2.0, was announced in the Union Budget 2026-27 with a focus on equipment, materials, indigenous IP, and resilient supply chains.

## The Sanand Cluster Takes Shape

Gujarat's Sanand industrial zone has emerged as the nerve centre of India's chip ecosystem. Within a few kilometres of each other, three facilities — CG Semi, Micron Technology, and Kaynes Semicon — are now operational, creating what industry observers call India's first semiconductor packaging cluster.

CG Semi's larger second facility (G2), spanning 28–32 acres, is under construction and slated for completion by end-2027. At full capacity, the two sites together will produce roughly 14.5 million chip units per day and create over 5,000 jobs — from engineering graduates out of Bihar and West Bengal to tribal women from Chhattisgarh who scored 92 per cent in a Japanese quality audit, according to a recent ground report by ThePrint.

Micron, meanwhile, inaugurated Phase 1 of its advanced test and packaging (ATMP) plant at Sanand earlier this year. CEO Sanjay Mehrotra urged the broader supply chain to deepen its Indian footprint: "Proximity matters. Local presence and local end-support and services matter."

## Beyond Packaging: The Fab Frontier

The current plants handle the back end of chipmaking — assembly, testing, and packaging. The front end, where silicon wafers are etched into circuits, is still years away. Tata Electronics is building India's first commercial 300mm semiconductor fabrication plant in Dholera, Gujarat, at a cost of ₹91,000 crore, in partnership with Dutch lithography giant ASML and Taiwan's PSMC. That fab is expected to be operational by 2028.

Intel and 3DGS Inc. have signed an MoU to invest $3.3 billion in a substrate manufacturing plant in Odisha. The project, expected to create 1,800 high-skilled jobs, will focus on advanced glass core substrates and high-density interconnect technologies.

Under the IndiaAI Mission, the government has also deployed over 45,000 GPUs as shared compute infrastructure and is supporting 15 Large Language Models across speech, text, and vision.

## What It Means for the Diaspora

For NRIs working in the global semiconductor supply chain — from Synopsys and Cadence in the Bay Area to ASML in the Netherlands — India's emergence as a chip producer opens a new axis of professional opportunity. Design-linked incentive schemes have already approved 24 chip design projects and given 105 companies access to advanced EDA tools. Twenty-three design tapeouts have been completed at foundries including at advanced nodes.

CG Power chairman Vellayan Subbiah framed it as a collective challenge: "Industries must support each other and embrace domestically made chips. As India's demand grows, we must start moving to making chips and using chips that are made in India."

Four years ago, 'Made in India' semiconductors were a policy aspiration. Today, they are sitting on a logistics dock in Malaysia."""

    sources = json.dumps([
        {"name": "Communications Today", "url": "https://communicationstoday.co.in"},
        {"name": "Reuters", "url": "https://reuters.com"},
        {"name": "Outlook Business", "url": "https://outlookbusiness.com"},
        {"name": "The Hindu BusinessLine", "url": "https://thehindubusinessline.com"},
        {"name": "ThePrint", "url": "https://theprint.in"}
    ])
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "tech",
        "status": "review",
        "is_editorial": False,
        "image_url": hero_url,
        "image_caption": hero_caption,
        "image_attribution": hero_attribution,
        "sources": sources,
        "diaspora_angle": "NRI semiconductor professionals in the Bay Area and globally now have a growing domestic chip ecosystem to engage with through design incentives and manufacturing opportunities.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    
    return insert_article(article)


# ============================================================
# ARTICLE 2: SCOTUS Birthright Citizenship Ruling 
# ============================================================

def write_birthright_article():
    print("\n=== ARTICLE 2: SCOTUS Birthright Citizenship Ruling ===\n")
    
    slug = "supreme-court-upholds-birthright-citizenship-6-3-indian-american-families-celebrate-20260701"
    
    # Image sourcing - US Supreme Court
    print("Sourcing images...")
    
    commons_results = fetch_wikimedia_commons_images("United States Supreme Court building", limit=5)
    
    hero_url = None
    hero_caption = None
    hero_attribution = None
    
    for img in commons_results:
        title_lower = img['title'].lower()
        # Look for actual Supreme Court building images
        if any(kw in title_lower for kw in ['supreme court', 'scotus']):
            if verify_image_url(img['url']):
                hero_url = img['url']
                hero_caption = "The United States Supreme Court in Washington, D.C."
                hero_attribution = "Wikimedia Commons"
                break
    
    if not hero_url:
        # Try direct known image
        direct_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/US_Supreme_Court_Building.jpg/1200px-US_Supreme_Court_Building.jpg"
        if verify_image_url(direct_url):
            hero_url = direct_url
            hero_caption = "The United States Supreme Court in Washington, D.C."
            hero_attribution = "Wikimedia Commons"
    
    if not hero_url:
        # Another attempt
        direct_url2 = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Panorama_of_United_States_Supreme_Court_Building_at_Dusk.jpg/1280px-Panorama_of_United_States_Supreme_Court_Building_at_Dusk.jpg"
        if verify_image_url(direct_url2):
            hero_url = direct_url2
            hero_caption = "The United States Supreme Court building at dusk in Washington, D.C."
            hero_attribution = "Wikimedia Commons"
    
    if not hero_url:
        print("  ✗ CRITICAL: No hero image found. Skipping article.")
        return None
    
    headline = "The Supreme Court Just Ruled 6-3 That Children of H-1B Parents Born in America Are Citizens. No President Can Change That."
    subheadline = "In a landmark ruling, the conservative-majority court struck down Trump's executive order targeting birthright citizenship — a decision that Indian American advocacy groups are calling 'a profound affirmation of who belongs in America.'"
    
    body = """The United States Supreme Court has upheld birthright citizenship in a 6-3 ruling that strikes down President Donald Trump's executive order attempting to deny automatic citizenship to children born on American soil to non-citizen parents. For the estimated 5.2 million Indian Americans in the United States — many of them navigating decades-long visa backlogs — the decision removes a constitutional threat that had hung over their families since January 2025.

The ruling, delivered on Tuesday, affirms that the 14th Amendment's guarantee of citizenship to all persons "born or naturalized in the United States, and subject to the jurisdiction thereof" cannot be narrowed by presidential decree. Chief Justice John Roberts, joined by conservative Justices Neil Gorsuch and Amy Coney Barrett alongside the three liberal justices, wrote that the text and history of the amendment left no room for the executive order's restrictions.

## 'Your Children Are American'

Indian American Impact, a national organisation that mobilises the South Asian diaspora in U.S. civic life, issued a forceful response within hours of the ruling.

"Today's ruling is a profound affirmation of who belongs in America," said Chintan Patel, the organisation's executive director. "Indian and South Asian immigrant families are among those most directly threatened by Trump's executive order — communities navigating long visa backlogs and uncertain immigration timelines, where children are often born here long before their parents have a clear path to permanence. Today, the Supreme Court looked at those families and said: your children are American."

The ruling is the third major defeat for the Trump administration at the Supreme Court this term, following the February decision striking down his global tariff programme and Monday's refusal to let him fire Federal Reserve Governor Lisa Cook.

## Why It Matters for Indian Families

The executive order, signed on Trump's first day back in office in January 2025, sought to deny citizenship to children born in the U.S. whose parents were neither citizens nor lawful permanent residents. It was immediately challenged by a coalition of states and civil rights groups, and multiple federal judges blocked it from taking effect.

For Indian families, the stakes were unusually high. India accounts for one of the largest backlogs in the U.S. employment-based green card system, with wait times stretching beyond 50 years for some categories. During those years, families on H-1B and L-1 visas raise children, buy homes, and build careers — all while their immigration status remains technically temporary. Children born during that limbo are, under the 14th Amendment, American citizens. The executive order sought to change that.

"For birthright Indian Americans in particular, the president's attack comes at an especially bad time," wrote Trisha Prabhu, a Yale Law student and founder of ReThink Citizens, in an op-ed published after the ruling. "Anti-Indian sentiment has reached a fever pitch. And now, at a moment when the country expresses its distaste for the Indian part of our identity, we also have had to contend with attacks on the American part."

## The Kavanaugh Caveat

Justice Brett Kavanaugh offered a partial concurrence that has drawn attention from immigration lawyers. While agreeing that the executive order was unconstitutional, Kavanaugh wrote that Congress — unlike the president — retains the power to "establish exceptions to birthright citizenship for children born to foreign citizens unlawfully or temporarily in the country."

No other justice in the majority joined Kavanaugh's view, and constitutional scholars are divided on whether Congress could actually restrict birthright citizenship through ordinary legislation rather than a constitutional amendment, which requires a two-thirds vote in both chambers and ratification by 38 states.

Trump, posting on Truth Social after the ruling, called the decision "too bad for our Country" and urged Congress to act: "No long and unwieldy Constitutional Amendment is necessary! Congress should start TODAY."

## Birth Tourism Crackdown

Hours after the ruling, the Department of Justice announced it would make the prosecution of birth tourism schemes "a priority across the country." Border Czar Tom Homan said immigration enforcement would surge in response, vowing to "triple, quadruple down" on investigations.

The crackdown targets organised schemes in which pregnant foreign nationals travel to the U.S. specifically to give birth, securing citizenship for their children. While legal, these schemes have drawn bipartisan criticism — Democratic Senator Harry Reid introduced a bill to restrict birth tourism as far back as 1993.

## What Comes Next

The ruling is final and directly binding. The 14th Amendment's citizenship clause, as interpreted by the court, cannot be overridden by any executive order. A legislative attempt to narrow birthright citizenship would almost certainly face another Supreme Court challenge — and, based on this ruling, would likely fail.

For Indian American families, the practical takeaway is straightforward: if your child was born in the United States, they are an American citizen. That was true before the executive order, it remained true while it was blocked by lower courts, and it is now confirmed by the highest court in the land.

"The Court reaffirmed it," Patel said. "They belong here."

*Sources: Supreme Court of the United States, Reuters, The Indian Eye, USA Today, Wall Street Journal, The Daily Caller*"""

    sources = json.dumps([
        {"name": "Supreme Court of the United States", "url": "https://supremecourt.gov"},
        {"name": "Reuters", "url": "https://reuters.com"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com"},
        {"name": "USA Today", "url": "https://usatoday.com"},
        {"name": "Wall Street Journal", "url": "https://wsj.com"}
    ])
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": hero_url,
        "image_caption": hero_caption,
        "image_attribution": hero_attribution,
        "sources": sources,
        "diaspora_angle": "Indian families on H-1B and L-1 visas, who face the longest green card backlogs in the system, now have Supreme Court confirmation that their U.S.-born children's citizenship is constitutionally protected.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    
    return insert_article(article)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print(f"=== Videshi News Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} ===")
    
    results = []
    
    r1 = write_semiconductor_article()
    if r1:
        results.append(r1)
    
    r2 = write_birthright_article()
    if r2:
        results.append(r2)
    
    print(f"\n=== Done: {len(results)} articles written ===")
    for r in results:
        if isinstance(r, dict):
            print(f"  - {r.get('slug', 'unknown')}")
        elif isinstance(r, list) and r:
            print(f"  - {r[0].get('slug', 'unknown')}")
