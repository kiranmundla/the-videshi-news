#!/usr/bin/env python3
"""
Videshi News Writer - June 5, 2026 batch
Writes 3 news articles with proper image sourcing and inserts into Supabase.
"""

import json, os, subprocess, time, re, urllib.parse, sys
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip()

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns (url, attribution) or (None, None)."""
    import requests
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            # Use thumbnail source AS-IS (330px, reliable)
            img = data.get("thumbnail", {}).get("source")
            if not img:
                img = data.get("originalimage", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img, "Wikimedia Commons"
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None, None

def fetch_wikimedia_commons(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    import requests
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
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for page_id, page in pages.items():
                info = page.get("imageinfo", [{}])[0]
                url = info.get("thumburl") or info.get("url")
                mime = info.get("mime", "")
                width = info.get("thumbwidth") or info.get("width", 0)
                if url and mime.startswith("image/") and width >= 200:
                    results.append({
                        "url": url,
                        "title": page.get("title", ""),
                        "width": width,
                        "mime": mime
                    })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} results for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Fetch relevant image from Pexels using curl."""
    try:
        encoded = urllib.parse.quote(query)
        result = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={encoded}&per_page=5&orientation=landscape",
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                # Pick best photo (largest landscape)
                best = max(photos, key=lambda p: p.get("width", 0))
                url = best.get("src", {}).get("large2x") or best.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                    return url, "Pexels"
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None, None

def validate_image(url):
    """Validate image URL returns HTTP 200 with image content type and >5KB."""
    try:
        result = subprocess.run(
            ["curl", "-sS", "-I", "-L", "--max-time", "10", url],
            capture_output=True, text=True, timeout=15
        )
        headers = result.stdout.lower()
        if "200" in headers and "content-type: image/" in headers:
            # Check content-length
            for line in headers.split('\n'):
                if 'content-length:' in line:
                    size = int(line.split(':')[1].strip())
                    if size > 5000:
                        return True
                    else:
                        print(f"  ⚠ Image too small: {size} bytes")
                        return False
            # No content-length header but 200 OK with image type - accept
            return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def insert_article(article):
    """Insert article into Supabase."""
    import requests
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            headers=headers,
            json=article,
            timeout=30
        )
        if r.status_code in (200, 201):
            result = r.json()
            if isinstance(result, list) and result:
                print(f"  ✓ Inserted: {result[0].get('headline', 'unknown')[:60]}...")
                return True
            print(f"  ✓ Inserted article")
            return True
        else:
            print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ Insert error: {e}")
        return False

# ===== ARTICLE 1: Indian-born founders built 96 US unicorns =====
def write_article_1():
    print("\n=== Article 1: Indian-Born Founders Built 96 US Unicorns ===")
    
    headline = "Indian Immigrants Built 96 Billion-Dollar Startups in America. The Combined Value Exceeds Germany's Stock Market."
    subheadline = "A new NFAP study finds that 59 percent of US unicorns have at least one immigrant founder. India leads all 76 source countries by a wide margin."
    slug = "indian-immigrants-96-unicorns-america-nfap-study-5-trillion-valuation-20260605"
    
    body = """The next time someone asks what the Indian diaspora has done for America, the answer is now a number: 96.

That is how many privately held US companies valued at a billion dollars or more trace their founding to an Indian-born entrepreneur, according to a new analysis by the National Foundation for American Policy released this week. No other country comes close. Israel is second with 60. The United Kingdom follows with 47. China, once considered the main rival pipeline, has 41.

## The Scale of It

The NFAP study examined all 775 active US unicorn companies as of April 2026. It found that immigrants from 76 countries have founded or co-founded 455 of them — 59 percent of the total. The combined valuation of those 455 companies exceeds five trillion dollars. To put that in perspective, the entire DAX index — Germany's benchmark stock market — is valued at roughly 2.3 trillion dollars.

Indian founders alone account for more than a fifth of all immigrant-founded unicorns. Among the five million Indian-born residents in the United States, roughly one in every 50,000 has gone on to build a billion-dollar company. That ratio — a measure of entrepreneurial density rather than raw population — is striking by any standard.

A parallel analysis by Stanford University's Venture Capital Initiative arrived at a similar conclusion, counting 90 Indian-born unicorn founders across the US startup landscape. The slight difference in methodology only reinforces the underlying finding: India is the single largest external source of high-growth entrepreneurship in the American economy.

## Why It Matters Now

The study lands at a moment of acute tension between two forces shaping the American innovation economy. On one side, the Trump administration has imposed a 100,000-dollar fee on new H-1B petitions, tightened scrutiny of employer-sponsored visas, and proposed legislation that would end the visa lottery system entirely. On the other, the data shows that immigrant founders are not marginal participants in the US economy — they are responsible for the majority of its most valuable private companies.

Each immigrant-founded unicorn employs an average of 833 people, the NFAP found. That translates into roughly 379,000 jobs across all 455 companies. These are not theoretical projections. They are existing positions at companies like Databricks, Figma, and Notion — household names in Silicon Valley that were started by people who came to America on student or work visas.

## The Diaspora Divide

For the Indian diaspora, the NFAP numbers are a source of pride and a point of anxiety in equal measure. The 96 unicorns represent the visible peak of a much larger ecosystem of Indian-founded companies, angel investors, and venture capital networks that have become central to how Silicon Valley operates.

But the pipeline that produced these founders is under pressure. The H-1B program, which has historically served as the primary entry point for skilled Indian workers, now faces its most restrictive policy environment in decades. Denial rates, which fell to 2 percent under the Biden administration, have been climbing again. The new weighted lottery system, which took effect in February, favours higher-salaried applicants — a shift that disproportionately affects early-career professionals from India who often enter the workforce at lower salary bands before rising rapidly.

The Brookings Institution warned this week that the cumulative effect of these policy changes is not just a reduction in visa approvals but an erosion of the broader talent pipeline. International student enrolments — the first step for many future founders — have already declined sharply, with F-1 visa issuances falling more steeply than at any point since the pandemic.

## What Comes Next

The NFAP study does not make policy recommendations, but its implications are difficult to ignore. If the conditions that enabled 96 Indian-born entrepreneurs to build billion-dollar companies in America are systematically dismantled, the question is not whether the next generation of unicorn founders will emerge — it is where they will choose to build.

Canada, the United Kingdom, the UAE and Singapore have all expanded their startup visa and entrepreneur programmes in the past two years, explicitly targeting the same pool of talent that once flowed almost exclusively to the United States. India itself has produced 131 domestic unicorns, a number that is growing faster than any country outside America and China.

For NRIs in the United States, the NFAP data is both validation and warning. The contribution is undeniable. The question is whether the country that benefited most from it still wants it to continue.

*Sources: National Foundation for American Policy (April 2026 analysis), Stanford Venture Capital Initiative, Brookings Institution, Bloomberg*"""
    
    # Image sourcing - try Wikimedia Commons for startup/Silicon Valley
    image_url = None
    image_caption = None
    image_attribution = None
    
    # Try Wikimedia Commons for startup/venture capital imagery
    commons_results = fetch_wikimedia_commons("Silicon Valley startup office technology")
    if commons_results:
        for r in commons_results:
            if validate_image(r["url"]):
                image_url = r["url"]
                image_caption = "Silicon Valley, the epicenter of America's billion-dollar startup ecosystem"
                image_attribution = "Wikimedia Commons"
                break
    
    if not image_url:
        # Try Pexels
        image_url, image_attribution = fetch_pexels_image("silicon valley startup technology office")
        if image_url and validate_image(image_url):
            image_caption = "Silicon Valley, the epicenter of America's billion-dollar startup ecosystem"
        else:
            image_url = None
    
    if not image_url:
        # Final fallback - Pexels with different query
        image_url, image_attribution = fetch_pexels_image("technology innovation business")
        if image_url and validate_image(image_url):
            image_caption = "The American technology sector owes much of its growth to immigrant entrepreneurs"
        else:
            image_url = None
            image_caption = None
            image_attribution = None
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "vertical": "economy",
        "is_editorial": False,
        "sources": "National Foundation for American Policy, Stanford Venture Capital Initiative, Brookings Institution, Bloomberg",
        "tags": ["unicorns", "indian-diaspora", "silicon-valley", "startups", "h1b", "immigration", "nfap"]
    }
    
    return insert_article(article)

# ===== ARTICLE 2: Federal judge strikes down Trump immigration freeze =====
def write_article_2():
    print("\n=== Article 2: Federal Judge Strikes Down Immigration Freeze ===")
    
    headline = "A Federal Judge Just Struck Down Trump's Immigration Freeze on 39 Countries. The Ruling Is 135 Pages Long."
    subheadline = "The court found that USCIS acted without legal authority and was driven by anti-immigrant animus, not national security. Indians on pending applications should take note."
    slug = "federal-judge-strikes-trump-immigration-freeze-39-countries-uscis-ruling-20260605"
    
    body = """A federal judge in Rhode Island has dismantled the Trump administration's sweeping immigration freeze in a 135-page ruling that accused US Citizenship and Immigration Services of acting illegally, ignoring Congress, and masking discrimination as national security.

Chief US District Judge John McConnell ruled on Friday that USCIS had "thrown the lives of countless immigrants living in the United States into indeterminate legal limbo" by categorically barring people from 39 countries from receiving decisions on their asylum, work permit, green card and citizenship applications.

The ruling is the most significant judicial rebuke of the administration's immigration agenda since the travel ban litigation of Trump's first term.

## What USCIS Did

The policies struck down on Friday were enacted after an Afghan national shot two National Guard members in Washington, DC last year. In the weeks that followed, the administration froze immigration benefit adjudications for applicants from 39 African, Asian, Latin American and Middle Eastern countries. It also suspended asylum processing nationwide and ordered a review of immigration benefits previously granted during the Biden administration.

The effect was immediate and far-reaching. Hundreds of thousands of immigrants who had filed applications through lawful channels — in many cases years earlier — found themselves unable to receive any decision at all. Work permits expired without renewal. Green card interviews were cancelled. Citizenship ceremonies were postponed indefinitely.

"Over six months later, many of those individuals remain without work, without legal status, and without any meaningful ability to plan for their futures," Judge McConnell wrote.

## The Court's Finding

McConnell did not merely rule that the policies were procedurally flawed. He found that they were driven by "anti-immigrant animus" — a legal finding that goes to the heart of the government's motivation.

"The Government effectively invites the Court to shut its eyes and ignore the strong evidence of anti-immigrant animus before it," he wrote. "Doing so would require profound naïveté on the Court's part. Unfortunately for the Government, that is an invitation that this Court will have to decline."

The judge found that USCIS had acted without the statutory or regulatory authority it claimed, had failed to provide reasoned explanations for its decisions, and had ignored the reliance interests of applicants who had followed every rule the government had set.

"In legal terms, that means USCIS's actions are contrary to law and arbitrary and capricious," he wrote.

## What It Means for Indians in America

India is not among the 39 countries on the travel ban list, so the direct impact of this ruling on Indian nationals is limited. But the broader implications are significant.

First, the ruling reinforces the principle that the executive branch cannot unilaterally freeze lawful immigration pathways without congressional authorisation. This matters for Indian H-1B holders, green card applicants and naturalisation candidates whose processing timelines have also been affected by the administration's broader slowdown of USCIS operations.

Second, the finding of anti-immigrant animus could strengthen legal challenges to other immigration restrictions — including the 100,000-dollar H-1B fee and the new weighted lottery system — that disproportionately affect Indian applicants.

Third, the ruling orders USCIS to resume processing the frozen applications, which could free up agency resources that have been diverted from other caseloads, including the employment-based green card backlog where Indian applicants face the longest wait times in the system.

## What Happens Next

The Department of Homeland Security did not immediately respond to requests for comment. The administration is expected to appeal the ruling, which could reach the First Circuit Court of Appeals and potentially the Supreme Court.

Democracy Forward, the legal organisation that brought the lawsuit on behalf of immigrant service groups and labour unions, called the ruling a vindication of the rule of law.

"This ruling reaffirms a basic principle: the federal government cannot shut down lawful immigration pathways or discriminate against people based on where they come from," said Skye Perryman, the group's president and CEO.

For the millions of immigrants caught in the freeze — and for the broader immigrant community watching from the sidelines — the ruling is a reminder that the courts remain a check on executive overreach, even in an era of maximum immigration enforcement.

*Sources: Reuters, CNN, Washington Examiner, Associated Press*"""
    
    # Image sourcing - try to get Judge McConnell or courthouse image
    image_url = None
    image_caption = None
    image_attribution = None
    
    # Try Wikimedia Commons for US federal courthouse or immigration
    commons_results = fetch_wikimedia_commons("US federal courthouse Providence Rhode Island")
    if commons_results:
        for r in commons_results:
            if validate_image(r["url"]):
                image_url = r["url"]
                image_caption = "A federal courthouse in Providence, Rhode Island, where the ruling was issued"
                image_attribution = "Wikimedia Commons"
                break
    
    if not image_url:
        commons_results = fetch_wikimedia_commons("USCIS immigration United States")
        if commons_results:
            for r in commons_results:
                if validate_image(r["url"]):
                    image_url = r["url"]
                    image_caption = "The US Citizenship and Immigration Services headquarters"
                    image_attribution = "Wikimedia Commons"
                    break
    
    if not image_url:
        image_url, image_attribution = fetch_pexels_image("US federal courthouse justice gavel")
        if image_url and validate_image(image_url):
            image_caption = "A federal judge ruled that USCIS immigration policies were unlawful and discriminatory"
        else:
            image_url = None
            image_caption = None
            image_attribution = None
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "vertical": "politics",
        "is_editorial": False,
        "sources": "Reuters, CNN, Washington Examiner, Associated Press",
        "tags": ["immigration", "trump", "uscis", "travel-ban", "federal-court", "nri", "green-card"]
    }
    
    return insert_article(article)

# ===== ARTICLE 3: H-1B crackdown tanks Dallas housing =====
def write_article_3():
    print("\n=== Article 3: H-1B Crackdown Tanks Dallas Housing ===")
    
    headline = "Indian Buyers Once Made Up 70 Percent of Sales in North Dallas. The H-1B Crackdown Changed That Overnight."
    subheadline = "Home prices in Collin County have fallen nearly 9 percent year-over-year. Over 100 luxury homes sit unsold. The suburbs that Indian tech workers built are learning what happens when they leave."
    slug = "h1b-crackdown-dallas-housing-crash-indian-buyers-collin-county-texas-20260605"
    
    body = """For the better part of a decade, the suburbs north of Dallas were the most reliable real estate bet in America. Frisco, Prosper, Celina, McKinney — names that meant little outside Texas became shorthand for a very specific kind of boom. New subdivisions went up faster than the roads that connected them. Schools filled before they opened. Home prices climbed with the certainty of a fixed deposit.

The engine behind all of it was Indian money. Specifically, Indian H-1B visa holders who had followed corporate America's relocation wave into the Dallas-Fort Worth corridor and decided to stay.

Now that engine has stalled. And the numbers are starting to show it.

## The Scale of the Retreat

In Collin County — the suburban epicentre of the North Texas boom — home prices fell nearly 9 percent year-over-year as of February, according to Redfin data. That is more than double the 4 percent decline recorded across the broader Dallas-Fort Worth metro area.

At Tradition Homes, a luxury builder that once counted on South Asian buyers for roughly 70 percent of its sales, that share has dropped below 30 percent. More than 100 high-end homes are sitting unsold on the company's books, according to Bloomberg.

The retreat is not a mystery. It is the direct, measurable consequence of the Trump administration's escalating crackdown on the H-1B visa programme — the permit that brought most of these buyers to Texas in the first place.

## What Changed

The policy shifts have been rapid and cumulative. In September 2025, Trump signed a proclamation imposing a 100,000-dollar fee on new H-1B petitions — a move that effectively priced out the staffing firms and mid-tier tech contractors that had been the biggest sponsors of Indian workers in markets like Dallas.

In February 2026, the Department of Homeland Security replaced the random H-1B lottery with a weighted system that favours higher-salaried applicants. In May, a new USCIS policy memo reframed adjustment of status inside the United States as "extraordinary relief" rather than a routine path — effectively telling visa holders that they may need to leave the country to pursue permanent residence.

Texas added its own layer. Governor Greg Abbott ordered a freeze on new H-1B petitions by state agencies and public universities in January. Attorney General Ken Paxton launched an investigation into nearly 30 North Texas businesses suspected of visa fraud or abuse.

The cumulative effect has been a sharp reduction in the number of Indian professionals arriving in, or staying in, the Dallas area.

## The Housing Math

The connection between H-1B policy and housing prices is not abstract in North Texas. It is arithmetic.

During the pandemic boom, South Asian buyers — predominantly Indian families on H-1B or L-1 visas — became the dominant force in new home sales across Collin and Denton Counties. They were drawn by the same things that drew their employers: good schools, relatively affordable land, no state income tax, and a growing concentration of tech and corporate headquarters.

Between 2018 and 2025, the Dallas-Fort Worth metro attracted more corporate headquarters relocations than any other metro area in the country, according to CBRE. Each relocation brought a wave of transferred employees, many of them visa holders. Each wave brought new demand for three-bedroom homes in the 400,000 to 800,000-dollar range.

When the policy environment shifted, the pipeline did not slow — it froze. FHA-insured mortgages, which some visa holders had used, became unavailable after the administration barred non-permanent residents from the programme in May 2025. The share of FHA loans issued to non-permanent residents fell from 6 percent to virtually zero within months, according to John Burns Research and Consulting.

## What It Means for NRIs

For Indian families already settled in North Dallas, the housing correction is a mixed signal. Those who bought at the peak of the boom are watching their home values decline. Those who waited may now find better prices — if their visa status allows them to stay long enough to buy.

For the broader Indian community in Texas, the story is a case study in how immigration policy can reshape local economies in ways that the policymakers who enacted it may not have anticipated — or may not care about.

The irony is not lost on anyone. The same communities that Indian tech workers built — the schools, the temples, the grocery stores, the cricket leagues — are now facing the economic consequences of their departure. The homes they bought are now the homes no one is buying.

*Sources: Bloomberg, Redfin, New York Post, Brookings Institution, John Burns Research and Consulting, CBRE*"""
    
    # Image sourcing
    image_url = None
    image_caption = None
    image_attribution = None
    
    # Try Wikimedia Commons for Dallas suburbs / Texas housing
    commons_results = fetch_wikimedia_commons("Frisco Texas suburb housing development")
    if commons_results:
        for r in commons_results:
            if validate_image(r["url"]):
                image_url = r["url"]
                image_caption = "Suburban housing in the Dallas-Fort Worth metro area"
                image_attribution = "Wikimedia Commons"
                break
    
    if not image_url:
        commons_results = fetch_wikimedia_commons("Dallas Fort Worth Texas skyline")
        if commons_results:
            for r in commons_results:
                if validate_image(r["url"]):
                    image_url = r["url"]
                    image_caption = "The Dallas-Fort Worth metro area attracted more corporate relocations than any other US city"
                    image_attribution = "Wikimedia Commons"
                    break
    
    if not image_url:
        image_url, image_attribution = fetch_pexels_image("Dallas Texas suburb houses neighborhood")
        if image_url and validate_image(image_url):
            image_caption = "Suburban housing developments in the Dallas-Fort Worth corridor"
        else:
            image_url = None
            image_caption = None
            image_attribution = None
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "vertical": "economy",
        "is_editorial": False,
        "sources": "Bloomberg, Redfin, New York Post, Brookings Institution, John Burns Research and Consulting, CBRE",
        "tags": ["h1b", "dallas", "texas", "housing", "real-estate", "immigration", "nri", "indian-diaspora"]
    }
    
    return insert_article(article)

# ===== MAIN =====
if __name__ == "__main__":
    print(f"=== Videshi News Writer - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} ===")
    
    results = []
    results.append(("Article 1 (96 Unicorns)", write_article_1()))
    results.append(("Article 2 (Immigration Ruling)", write_article_2()))
    results.append(("Article 3 (Dallas Housing)", write_article_3()))
    
    print("\n=== SUMMARY ===")
    for name, success in results:
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"  {status}: {name}")
    
    total_success = sum(1 for _, s in results if s)
    print(f"\n  {total_success}/{len(results)} articles published")
