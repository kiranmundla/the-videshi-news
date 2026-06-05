#!/usr/bin/env python3
"""
News Writer — The Videshi
Generates 3 articles, sources images, inserts to Supabase.
"""
import json, os, re, time, subprocess, urllib.parse, uuid
from datetime import datetime, timezone

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                key, _, val = line.partition('=')
                val = val.strip('"').strip("'")
                os.environ[key.strip()] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

import requests

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns (url, attribution) or (None, None)."""
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
                return img, "Wikimedia Commons"
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None, None


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
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
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
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels for an image. Returns (url, attribution) or (None, None)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None, None
    try:
        # Use curl since urllib gets 403
        result = subprocess.run(
            ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
             f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3'],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get('photos', [])
        if photos:
            photo = photos[0]
            url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
            if url:
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url, "Pexels"
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None, None


def validate_image(url):
    """Verify URL returns a valid image >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get('Content-Type', '')
        content_length = int(r.headers.get('Content-Length', 0))
        if 'image' in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {content_length} bytes, {content_type}")
            return True
        elif 'image' in content_type and content_length == 0:
            # Some servers don't return Content-Length on HEAD; try GET
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: {len(chunk)}+ bytes")
                return True
        print(f"  ✗ Image validation failed: type={content_type}, size={content_length}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def insert_article(article):
    """Insert article into Supabase."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=headers,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Article inserted: {result[0].get('id', 'unknown')}")
            return True
        print(f"  ✓ Article inserted (no ID returned)")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return False


def source_image(person_name=None, wiki_search=None, pexels_query=None):
    """Multi-source image search. Returns (url, caption_hint, attribution) or (None, None, None)."""
    # 1. Wikipedia person image
    if person_name:
        url, attr = fetch_wikipedia_person_image(person_name)
        if url and validate_image(url):
            return url, person_name, attr

    # 2. Wikimedia Commons
    if wiki_search:
        results = fetch_wikimedia_commons_images(wiki_search)
        for r in results:
            img_url = r.get('url') or r.get('original_url')
            if img_url and validate_image(img_url):
                return img_url, r.get('title', '').replace('File:', ''), "Wikimedia Commons"

    # 3. Pexels
    if pexels_query:
        url, attr = fetch_pexels_image(pexels_query)
        if url and validate_image(url):
            return url, pexels_query, attr

    return None, None, None


# ===================== ARTICLES =====================

now_utc = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

articles = []

# ---- ARTICLE 1: NY State Senate India Independence Day Resolution ----
print("\n=== ARTICLE 1: NY State Senate India Independence Day Resolution ===")

img1_url, img1_hint, img1_attr = source_image(
    person_name="Jeremy Cooney (politician)",
    wiki_search="New York State Senate chamber",
    pexels_query="Indian American celebration flag"
)
# Fallback search
if not img1_url:
    img1_url, img1_hint, img1_attr = source_image(
        wiki_search="India Independence Day celebration",
        pexels_query="India independence day flag"
    )

article1 = {
    "vertical": "news",
    "headline": "New York's State Senate Just Declared August 15 India Independence Day. The Man Behind It Was Adopted From Kolkata.",
    "subheadline": "Resolution J1935 urges Governor Kathy Hochul to formally recognise India's 79th Independence Day across the state — sponsored by the first Asian American elected to state office from upstate New York.",
    "slug": "new-york-state-senate-india-independence-day-resolution-jeremy-cooney-kolkata-20260605",
    "category": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": now_utc,
    "body": """The New York State Senate has adopted Resolution J1935, urging Governor Kathy Hochul to proclaim August 15, 2026, as India Independence Day in the State of New York. The resolution, which passed with bipartisan support, paves the way for formal statewide celebrations marking India's independence — a first for the state legislature's annual calendar.

The resolution was sponsored by State Senator Jeremy Cooney, a Democrat representing Rochester. Cooney's personal story gives the measure an unusual emotional weight. Adopted from an orphanage in Kolkata and raised by a single mother in upstate New York, he made history in 2020 as the first Asian American elected to state office from outside New York City.

"Across the globe, Indians are making lasting impacts in their communities, and this is an opportunity to join together and celebrate and reflect on our shared history, culture, and heritage," Cooney told the Senate during deliberations.

## A Chorus of Recognition

Several senators used the floor debate to speak about India's civilisational heritage and the growing influence of the Indian American community across New York.

Senator Joseph P. Addabbo Jr. invoked Mahatma Gandhi, noting that his message that "the future depends on what we do in the present" continues to inspire Indian Americans and future generations. Senator John C. Liu offered a broader historical frame: "India has been around for thousands of years. It has been a civilisation. It has been a country. It has been a model of democracy for actually a lot longer than our country."

Senator Jeremy Zellner said the Indian American community is "woven into the fabric of our everyday life" in his district. "They are our neighbours raising families here, working in critical professions, and helping shape the character of our region," he added.

## What the Resolution Says

The text of Resolution J1935 notes that India's independence "is enormously important to people around the world" and that it "marks the end of a 90-year struggle to achieve stronger civil, political, and economic rights along with self-determination." It follows the legislature's tradition of recognising official days significant to the cultural heritage of New York's citizens.

The resolution does not have the force of law. It memorialises the Governor — effectively requesting, rather than requiring, the proclamation. But the symbolic weight is significant. Indian Americans are among the fastest-growing demographic groups in New York, with a community concentrated in Queens that is among the largest in the Western Hemisphere.

## The Consulate Responds

The Consulate General of India in New York welcomed the Senate's decision. "The Consulate General of India, New York, expresses its sincere gratitude to Senator Jeremy Cooney for sponsoring the adopted resolution," the office said in a statement. It noted that the remarks by senators "reflected the deep people-to-people bonds between India and the United States and the growing role of the Indian American diaspora in strengthening communities across New York."

## Why It Matters for the Diaspora

India will mark its 79th Independence Day on August 15, 2026. The New York resolution arrives at a moment when Indian Americans are more visible in American public life than at any point in the country's history. From Usha Vance in the White House to Kash Patel at the FBI, from Sriram Krishnan advising on AI policy to Ajay Banga leading the World Bank, the community's footprint extends well beyond traditional strongholds in medicine and technology.

For the estimated 900,000 Indian Americans living in New York — and for the millions more across the country — a formal recognition from one of America's most powerful state legislatures is not merely ceremonial. It is an acknowledgement that the community's contributions have become too significant to ignore.

The resolution now awaits Governor Hochul's response. If she issues the proclamation, August 15 will join a roster of cultural heritage days formally recognised across New York State.

*Sources: PTI, hi INDiA, The Indian Eye, New York State Senate records*""",
    "sources": json.dumps(["PTI", "hi INDiA", "The Indian Eye", "New York State Senate"]),
    "image_url": img1_url,
    "image_caption": "The New York State Senate adopted Resolution J1935 recognising India Independence Day",
    "image_attribution": img1_attr or "Wikimedia Commons"
}
articles.append(article1)


# ---- ARTICLE 2: India AI Hiring Crisis ----
print("\n=== ARTICLE 2: India AI Hiring Crisis ===")

img2_url, img2_hint, img2_attr = source_image(
    person_name="Mukesh Ambani",
    wiki_search="Reliance Industries headquarters Mumbai",
    pexels_query="India technology office workers"
)

article2 = {
    "vertical": "news",
    "headline": "Reliance's Hiring Has Slowed to a Crawl. AI Is About to Make It Worse.",
    "subheadline": "India's largest private employer grew headcount by just 4% last year, one quarter of the previous year's pace. At TCS and Infosys, the workforce has already shrunk. The AI squeeze is only beginning.",
    "slug": "reliance-ai-hiring-slump-india-tcs-infosys-youth-unemployment-20260605",
    "category": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": now_utc,
    "body": """Finding a good job in India is about to get significantly harder. A convergence of slowing investment cycles and accelerating AI adoption is squeezing employment at the country's most powerful private companies — and the structural nature of the shift means the pressure is unlikely to ease.

Reliance Industries, India's biggest private company by market capitalisation at $190 billion, employed over 419,000 people as of March 2026. That represents headcount growth of just 4% year-on-year — one quarter of its expansion rate the previous year. The company has also grown less transparent about its workforce: it quietly discontinued a detailed breakdown of employees by division in last year's annual report.

The slowdown at Reliance is partly cyclical. A phase of aggressive recruitment for its renewable energy business has wound down. But the deeper signal is structural. Reliance has said it is "building talent fluent in leveraging AI to enhance decision-making, productivity and purpose-driven work" — language that signals fewer humans per unit of output going forward.

## The IT Outsourcers Are Already Shrinking

The pattern is more advanced at India's IT outsourcing giants, the companies that built the country's middle class and powered an entire generation of NRI migration to the West.

Tata Consultancy Services and Infosys, India's second- and third-largest companies by market capitalisation, have seen their headcounts fall to as much as 5% below their March 2023 peaks. Revenue growth has slowed. And the rise of AI-powered coding tools — GitHub Copilot, Amazon CodeWhisperer, and their successors — is eroding the demand for the entry-level programming work that once employed hundreds of thousands of fresh graduates each year.

The Forum for IT Employees (FITE) in Maharashtra has documented the damage at the ground level. "Earlier, large IT companies hired freshers in huge numbers every year, especially from top colleges, which created a ripple effect across the market," Pavanjit Mane, FITE's Maharashtra president, told Outlook Business. "That pipeline has now weakened significantly."

Thousands of graduates from the 2023, 2024, and 2025 batches are still waiting for jobs. Joining dates have been delayed by six to ten months. Campus intake has been slashed.

## The Youth Unemployment Crisis

India's Chief Economic Advisor, V. Anantha Nageswaran, warned in February that future job growth is a bigger concern than headline layoffs. His call on the private sector to hire more and balance capital-intensive growth with labour-intensive employment has gone largely unanswered.

The numbers bear out the anxiety. Urban youth unemployment stands at 13.6%. It is common for college graduates to queue up for janitorial roles in the public sector. The aspirational promise of the IT industry — stable incomes, overseas assignments, upward social mobility — is dimming for an entire generation.

## What This Means for the Diaspora

The implications extend well beyond India's borders. The IT outsourcing model was the engine that drove Indian migration to the United States, Britain, Canada, and Australia for three decades. H-1B visas, L-1 transfers, and onsite assignments at client offices built the economic foundation of the Indian diaspora in the West.

If the volume of entry-level IT hiring continues to fall, fewer Indians will get the corporate launchpad that historically led to overseas postings. The pipeline that produced NRI professionals — and the remittances, investments, and cultural exchange that followed — could narrow significantly.

Reuters' Breakingviews analysis warns that the current hiring squeeze may be "the calm before the AI storm." The real impact of AI on India's job market, the analysis suggests, will become clearer in the next 12 to 18 months, as companies move from AI pilots to full deployment.

## A Consumption Crisis in Waiting

The economic ripple effects could be severe. A potential 30% reduction in the 15-million-strong outsourcing and global capability centre workforce over the next two years could shrink India's top consuming class by about 5 million people, according to estimates from Blume Ventures. At an estimated annual income of $15,000 per person, that would reduce total spending power by roughly $75 billion a year.

Household savings are already declining. Indians saved barely 23% of their disposable income in the year to March 2025, down from nearly 30% two decades earlier. Debt as a share of disposable income has surged to 55% from 31% over the same period.

The AI revolution may create new jobs in time. But the transition will be painful — and for millions of young Indians who bet their futures on the IT dream, the window may be closing faster than anyone expected.

*Sources: Reuters Breakingviews, Outlook Business, National Stock Exchange data, CLSA, Blume Ventures*""",
    "sources": json.dumps(["Reuters Breakingviews", "Outlook Business", "NSE data", "CLSA"]),
    "image_url": img2_url,
    "image_caption": "Reliance Industries chairman Mukesh Ambani at a company event in Mumbai",
    "image_attribution": img2_attr or "Wikimedia Commons"
}
articles.append(article2)


# ---- ARTICLE 3: PhysicsWallah Reverses Lending Strategy ----
print("\n=== ARTICLE 3: PhysicsWallah Reverses Lending Strategy ===")

img3_url, img3_hint, img3_attr = source_image(
    person_name="Alakh Pandey",
    wiki_search="PhysicsWallah edtech India",
    pexels_query="India students education classroom"
)

article3 = {
    "vertical": "news",
    "headline": "PhysicsWallah Killed Its Lending Plan One Week After Announcing It. The Stock Surged 18%.",
    "subheadline": "The edtech giant scrapped a ₹120 crore student lending bet after investors revolted — and the market rewarded the U-turn instantly.",
    "slug": "physicswallah-reverses-finz-finance-lending-nbfc-partnership-stock-surge-20260605",
    "category": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": now_utc,
    "body": """PhysicsWallah, one of India's most watched edtech companies, has abruptly abandoned its plan to lend directly to students — just one week after announcing a ₹120 crore infusion into its lending subsidiary. The reversal sent the company's shares surging nearly 18% in a single session, a striking market verdict on the original decision.

The Alakh Pandey-led company said on Thursday that it has restructured its lending strategy and will now partner with multiple regulated non-banking financial companies (NBFCs) instead of building an in-house lending book through its subsidiary, FinZ Finance Private Limited.

"We received feedback from our partners that our core strength lies in building communities and our online business," co-founder Prateek Maheshwari said. "Our lending business is best left to regulated third-party NBFCs who have created robust underwriting capabilities."

## The Week That Changed Everything

The U-turn was swift even by startup standards. Last week, PhysicsWallah had filed an exchange disclosure announcing a ₹120 crore equity infusion into FinZ Finance, signalling ambitious plans to enter student financing directly. The market's response was immediate and negative: shares fell steadily as investors questioned why an education platform was taking on credit risk.

The backlash came from multiple directions. Long-term investors and strategic partners reportedly advised the company to stick to its core education business rather than diversify into a domain that requires specialised underwriting capabilities and regulatory expertise. The message was clear: build courses, not loan books.

By Thursday morning, the reversal was official. PhysicsWallah said it would function as a technology platform connecting students to a "curated set of regulated lending partners," with financing decisions tied to students' learning lifecycle and academic outcomes. The asset-light model eliminates balance sheet exposure and credit risk.

## What Happens to FinZ Finance

The ₹120 crore already invested in FinZ Finance now needs to be recovered. According to people familiar with the matter, PhysicsWallah is weighing several options: a potential sale of the subsidiary, transfer of its existing loan book, or surrender of its lending-related licences. The final decision will follow a board review and regulatory approval.

The rapid pivot reflects a broader maturation in India's startup ecosystem, where investors are increasingly intolerant of mission creep. The days when venture-backed companies could expand into adjacent businesses without scrutiny are over. Capital efficiency and focus are the new watchwords.

## The Market's Verdict

The stock market's reaction was unambiguous. PhysicsWallah shares opened at ₹91 on Thursday and surged to an intraday high of ₹108.45, eventually closing at ₹106.50 — up 15.6% from the previous session. Trading volume was extraordinary, with approximately 562 lakh shares changing hands worth ₹583 crore.

The surge partially reversed a 20% year-to-date decline in the stock, which had been under sustained pressure. The company's market capitalisation recovered to approximately ₹30,764 crore (about $3.2 billion).

## The Edtech Lending Dilemma

PhysicsWallah's brief lending experiment highlights a tension that runs through India's edtech sector. The companies that serve aspirational students — many from Tier-2 and Tier-3 cities — are acutely aware that affordability is the single biggest barrier to education. The temptation to solve the financing problem in-house is powerful.

But lending is a fundamentally different business from education. It requires regulatory compliance, credit risk assessment, collections infrastructure, and capital reserves that sit uneasily alongside the high-growth, technology-first culture of a startup. Companies like Byju's learned this lesson at great cost. PhysicsWallah, to its credit, learned it in a week.

The new NBFC partnership model represents a compromise: PhysicsWallah keeps its students within its ecosystem while outsourcing the financial risk to institutions built for it. If the partnerships work, students get access to financing without the company betting its balance sheet on their repayment.

For Alakh Pandey, whose YouTube-to-unicorn journey has made him one of India's most recognised entrepreneurs, the episode is a reminder that markets reward discipline as readily as they punish overreach.

*Sources: Inc42, The Hindu BusinessLine, LiveMint, Reuters, Storyboard18*""",
    "sources": json.dumps(["Inc42", "The Hindu BusinessLine", "LiveMint", "Reuters", "Storyboard18"]),
    "image_url": img3_url,
    "image_caption": "PhysicsWallah co-founder Alakh Pandey built the edtech platform from a YouTube channel",
    "image_attribution": img3_attr or "Pexels"
}
articles.append(article3)


# ===================== INSERT ALL =====================
print("\n=== INSERTING ARTICLES ===")
success_count = 0
for i, article in enumerate(articles):
    print(f"\nArticle {i+1}: {article['headline'][:60]}...")
    if not article.get('image_url'):
        print("  ⚠ No image found — inserting without image")
        article.pop('image_url', None)
        article.pop('image_caption', None)
        article.pop('image_attribution', None)
    if insert_article(article):
        success_count += 1

print(f"\n=== DONE: {success_count}/{len(articles)} articles inserted ===")
