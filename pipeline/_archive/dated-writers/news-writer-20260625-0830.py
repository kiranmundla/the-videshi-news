#!/usr/bin/env python3
"""
Videshi News Writer — June 25, 2026 (08:30 UTC run)
2 NEW articles, dedup-checked against last ~30 news articles:
  1. Amazon to invest an ADDITIONAL $13 billion in India by 2030 (announced
     June 25, 2026) for AI + cloud infrastructure, on top of the previously
     planned $35 billion. Fresh tech/economy story; not in recent set.
  2. US EB-2 green-card category for India exhausted for FY2026 — State Dept
     confirms no more EB-2 immigrant visas to Indian applicants until Oct 1,
     2026. Distinct from the recent naturalization-fee and F-1 duration-of-status
     pieces; this is the employment-based green-card backlog angle.
"""
import os, json, requests, urllib.parse, subprocess, io
from datetime import datetime, timezone

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k] = v.strip().strip('"').strip("'")

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
    "Prefer": "return=representation",
}


def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error: {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=6):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers={"User-Agent": UA}, timeout=15)
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
                print(f"  \u2713 Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape",
            headers={"Authorization": PEXELS_KEY, "User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  \u2713 Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  \u26a0 Pexels error: {e}")
    return None


def download_and_compress(url, slug):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  \u26a0 Download failed ({r.status_code}): {url[:80]}")
            try:
                tmp = f"/tmp/{slug}_src"
                subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, url], timeout=30, check=True)
                with open(tmp, "rb") as f:
                    content = f.read()
                if len(content) < 5000:
                    return None
                r_content = content
            except Exception:
                return None
        else:
            r_content = r.content
        ct = r.headers.get("Content-Type", "") if r.status_code == 200 else "image/jpeg"
        if "image" not in ct and len(r_content) < 5000:
            print(f"  \u26a0 Not an image or too small: {ct}, {len(r_content)} bytes")
            return None

        from PIL import Image
        img = Image.open(io.BytesIO(r_content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > 1200:
            ratio = 1200 / img.width
            img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80, optimize=True)
        compressed = buf.getvalue()

        if len(compressed) < 5000:
            print(f"  \u26a0 Compressed image too small: {len(compressed)} bytes")
            return None

        print(f"  \u2713 Compressed: {len(r_content)} \u2192 {len(compressed)} bytes")

        filename = f"{slug}.jpg"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"

        requests.delete(upload_url, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY
        })

        resp = requests.post(upload_url, data=compressed, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY,
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }, timeout=30)

        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  \u26a0 Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None

    except Exception as e:
        print(f"  \u26a0 Download/compress error: {e}")
        return None


def pick_commons(queries, min_width=900):
    for q in queries:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            pick = None
            for c in commons:
                if c["width"] >= min_width and c["original_url"].lower().endswith((".jpg", ".jpeg")):
                    pick = c
                    break
            pick = pick or commons[0]
            return pick["url"], pick.get("title", "")
    return None, ""


def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS, json=article, timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  \u2713 Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# \u2500\u2500\u2500 Article 1: Amazon's additional $13bn India AI/cloud investment \u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Amazon additional $13bn India investment")
    print("="*60)

    slug = "amazon-additional-13-billion-india-ai-cloud-investment-2030-aws-data-centres-diaspora-20260625"
    headline = "Amazon Just Doubled Down on India. It's Putting Another $13 Billion Into AI and the Cloud."
    subheadline = "The fresh commitment, announced Thursday, lifts Amazon's planned India spending to nearly $50 billion by 2030 \u2014 a vote of confidence in the country's data-centre boom that the diaspora's engineers and small businesses will feel directly."

    body = """Amazon is making one of its biggest bets yet on India. The company said on Thursday that it will invest an additional $13 billion in the country by 2030 to expand artificial-intelligence and cloud infrastructure \u2014 money that comes on top of the more than $35 billion it had already committed last December. Taken together, the two pledges push Amazon's planned India outlay to roughly $50 billion before the end of the decade, among the largest single-country commitments the company has made anywhere outside the United States.

The new spending will flow primarily through Amazon Web Services, the company's cloud arm, into data centres, servers, high-performance computing and the telecommunications backbone that powers them. AWS already operates data-centre regions in Mumbai and Hyderabad, and has been steadily enlarging its footprint in Maharashtra and Telangana, the two states that have emerged as India's core hubs for digital infrastructure. The fresh capital is aimed squarely at the surge in demand for the compute that generative AI consumes.

## Why India, Why Now

The timing is not accidental. India's cloud-services market has been growing at more than 20% a year, and the government's IndiaAI Mission has been courting global technology giants to build the physical capacity the country's AI ambitions require. Amazon is far from alone: Microsoft and Google have each announced sizeable data-centre investments in India over the past year, and the competition to host the nation's AI workloads has become one of the defining contests in global technology.

For Amazon, the logic runs in two directions. India is both an enormous and fast-digitising market in its own right \u2014 one where AWS counts customers across manufacturing, finance, travel and government \u2014 and a deep pool of engineering talent that can build and run that infrastructure at scale. The company says it has trained more than six million people in India in cloud skills since 2017 through programmes such as AWS Skill Builder, AWS Educate and re/Start, and has been layering AI courses on top of them.

## The Small-Business Angle

Beyond the steel and silicon, Amazon has framed the investment as a way to bring AI tools to India's vast base of small enterprises. The company has said it wants more than 15 million small businesses to benefit from AI-driven tools across its ecosystem by 2030 \u2014 from an agentic-AI seller assistant and generative listing tools to a creative studio for advertising and a low-cost video generator. The pitch is that even a tiny seller in a tier-three town can operate, in Amazon's words, with "enterprise-grade intelligence." The company has also pledged to bring AI literacy to four million government-school students by 2030, aligning the effort with India's National Education Policy.

That ambition arrives with real-world friction. AWS's expansion has drawn scrutiny over the water and power that data centres consume, in a country where 18% of the world's population shares just 4% of its freshwater. Amazon said earlier this month that its Indian operations had turned "water positive" a year ahead of schedule and that it does not use water to cool its Indian data centres \u2014 a pointed response to mounting environmental pushback as Mumbai and Bengaluru grapple with severe shortages this summer.

## Why It Matters for the Diaspora

For the Indian diaspora, an investment of this size is more than a corporate press release. The Indian-origin technologists who help run AWS \u2014 and the wider community of cloud architects, data engineers and AI researchers scattered across Seattle, the Bay Area and Bengaluru \u2014 are precisely the people who design and operate this infrastructure. A bigger AWS presence in India means more senior roles based at home, a stronger case for the reverse-migration that schemes like the government's research fellowships are trying to encourage, and deeper rungs on the ladder for engineers who would once have had to leave to do frontier work.

There is a business dimension too. Many diaspora-founded startups in the US, the UK and the Gulf build on AWS and serve Indian customers; cheaper, closer and more powerful compute lowers their costs and shortens their latency. And for the millions of small Indian businesses \u2014 many of them family enterprises with relatives abroad \u2014 the promise of affordable AI tools could reshape how they sell, advertise and compete. Whether the $13 billion delivers on that promise will depend on execution, and on resolving the resource strains that come with it. But as a statement of intent, the message is unambiguous: one of the world's most valuable companies sees India not as a back office, but as a front line of the AI era.
"""

    img_url, ititle = pick_commons([
        "Amazon Web Services data center building",
        "Amazon data center",
        "data center server room"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "An Amazon Web Services data centre; AWS anchors Amazon's expanded AI and cloud investment in India"

    if not img_url:
        px = fetch_pexels_image("data center server room")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Amazon will invest an additional $13 billion in AI and cloud data-centre infrastructure in India by 2030"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "tech",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters (reuters.com, June 25, 2026) \u2014 'Amazon to invest additional $13 billion in India': Amazon said on Thursday it is investing an additional $13 billion in India by 2030 to expand and support AI and cloud infrastructure; the investment is in addition to the more than $35 billion it announced last year in December.",
            "Reuters (reuters.com, June 2026) \u2014 'Amazon points to water conservation steps in India amid data centre scrutiny': Amazon plans to invest more than $35 billion in India by 2030 to boost AI capabilities and exports; AWS plans to invest about $8.2 billion in Maharashtra; Amazon said its Indian operations turned 'water positive' a year ahead of schedule and that it does not use water to cool its Indian data centres; Microsoft and Google have also announced sizeable data-centre investments in India over the past year.",
            "The Hindu BusinessLine (thehindubusinessline.com, December 2025) \u2014 'Amazon sets 2030 AI push with $12.7 billion India bet': Amazon is strengthening AWS capacity in Telangana and Maharashtra; the company plans to enable over 15 million small businesses with AI-driven tools including an agentic-AI seller assistant, generative listing tools, a creative studio for ad creation and a video generator; it aims to bring AI literacy to 4 million government-school students by 2030 in line with the National Education Policy 2020; AWS has data centres in the Mumbai and Hyderabad regions.",
            "Outlook Business (outlookbusiness.com, June 1, 2026) \u2014 'Amazon Expects Its $12.7 bn AI Investment to Benefit 15 mn Small Biz in India by 2030': Amazon's SVP for Emerging Markets Amit Agarwal said the long-term goal is aligned with the Government of India's AI Mission, aiming to empower over 15 million small businesses and provide AI literacy to 4 million government-school students by 2030; AWS says it has trained over 6.2 million individuals in India with cloud skills since 2017 through AWS Skill Builder, AWS Educate and re/Start."
        ]),
        "diaspora_angle": "Amazon's additional $13 billion India investment \u2014 lifting its planned spend to nearly $50 billion by 2030 \u2014 deepens the country's AI and cloud capacity, creating senior technical roles at home that strengthen the case for diaspora reverse-migration, lowering costs for diaspora-founded startups that build on AWS, and promising affordable AI tools to millions of small Indian businesses with relatives abroad.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: EB-2 green card category for India exhausted FY2026 \u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: EB-2 India green-card category exhausted FY2026")
    print("="*60)

    slug = "us-eb2-green-card-category-india-exhausted-fy2026-state-department-october-reset-diaspora-20260625"
    headline = "America Has Run Out of EB-2 Green Cards for Indians This Year. The Wait Now Stretches to October."
    subheadline = "The State Department says the entire FY2026 allocation of employment-based second-preference visas for Indian applicants is gone \u2014 freezing one of the diaspora's main paths to a green card until the new fiscal year resets the count on October 1."

    body = """One of the most important doors into permanent residency in the United States has just closed for Indian professionals \u2014 at least until autumn. The State Department, working with U.S. Citizenship and Immigration Services, has confirmed that all available immigrant visas in the Employment-Based Second Preference (EB-2) category for applicants chargeable to India have been issued for fiscal year 2026. Until the new fiscal year begins on October 1, 2026, no further EB-2 green cards can be issued to Indian applicants anywhere in the world.

For the hundreds of thousands of Indian engineers, doctors, researchers and other advanced-degree professionals who rely on this category, it is a hard stop. EB-2 covers workers with advanced degrees or "exceptional ability," and it is one of the most heavily subscribed routes for skilled Indian immigrants to convert temporary work status into a green card. With the year's numbers exhausted, embassies, consulates and USCIS adjudicators cannot finalise these cases until the count resets.

## How the Cap Works

The freeze is a function of arithmetic written into U.S. law decades ago. The Immigration and Nationality Act sets the annual EB-2 allocation at 28.6% of the worldwide employment-based limit. On top of that, no single country may receive more than 7% of all employment-based and family-sponsored visas in a given year. Because demand from India dwarfs that ceiling \u2014 the product of a vast, highly qualified applicant pool and a per-country cap that does not scale with it \u2014 the Indian allocation runs dry well before the fiscal year ends.

This is not a one-off. The same exhaustion happened to EB-2 India in FY2025, and the EB-5 investor category and other employment-based streams for India have hit their limits this year too. Applications can still be filed, and many adjustment-of-status cases will simply sit pending; what stops is the final issuance of the visa or the green card itself. The annual numbers will reset on October 1, and consulates will then resume issuing EB-2 visas to qualified Indian applicants \u2014 only for the same wall to loom again later in FY2027.

## A Backlog Measured in Decades

The immediate freeze sits on top of a structural backlog that immigration lawyers describe in generational terms. Because of the per-country limits, Indian nationals in the employment-based queue can face waits that stretch across decades \u2014 long enough that children who arrived as dependents can "age out" of eligibility before a green card becomes available. Each year's exhaustion deepens the sense that the system is mismatched to the scale of Indian demand.

There have been crosscurrents. A spillover of roughly 46,000 unused family-based green-card numbers into the employment side this fiscal year pushed some priority dates forward in the spring, and attorneys note that continued low family-based issuance could spill over again into FY2027, easing movement for applicants from lower-demand countries. But for Indians specifically, the 7% per-country cap blunts much of that benefit \u2014 which is why EB-2 India still hit its wall while other categories had room.

## Why It Matters for the Diaspora

For the Indian diaspora in America, this is not abstract policy \u2014 it is the difference between settling permanently and living year to year on a temporary visa. Many of those affected are H-1B holders who have spent a decade or more in the country, raising families, buying homes and building careers while waiting for a green card that the math keeps pushing further away. A mid-year freeze adds fresh uncertainty to that limbo: pending cases stall, planned travel becomes riskier, and job changes grow more fraught.

Immigration attorneys are urging affected professionals to monitor the monthly Visa Bulletin closely, keep their underlying work status valid, and weigh alternative routes \u2014 EB-1 for those with extraordinary ability, or in some cases the EB-5 investor path \u2014 where they qualify. None of those are simple substitutes. The deeper issue, advocates argue, is the per-country cap itself, which Indian-American lawmakers and community groups have lobbied for years to reform without success. Until that changes, the annual ritual is likely to repeat: the queue grows, the cap holds, and each fiscal year the door swings shut a little earlier than the last.
"""

    img_url, ititle = pick_commons([
        "United States Department of State building Washington",
        "Harry S Truman Building State Department",
        "United States passport green card"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "The U.S. Department of State, which confirmed the EB-2 green-card category for India is exhausted for fiscal year 2026"

    if not img_url:
        px = fetch_pexels_image("united states immigration documents")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "The EB-2 employment-based green-card category for Indian applicants is exhausted for FY2026 until October 1"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "U.S. Department of State, Travel.State.Gov (travel.state.gov, 2026) \u2014 'Annual Limit Reached in the EB-2 Category': the State Department, working with USCIS, has issued all available immigrant visas in the Employment-Based Second Preference (EB-2) category; INA 203(b)(2) sets the annual EB-2 limit at 28.6% of the worldwide employment limit; once all available EB-2 visas are used, embassies and consulates may not issue visas in the category for the remainder of the fiscal year, with limits resetting at the start of the new fiscal year on October 1.",
            "Berry Appleman & Leiden LLP / BAL (bal.com, 2026) \u2014 'United States | EB-2 visa limit met for India': the State Department announced that all available EB-2 immigrant visas for applicants chargeable to India have been issued for FY2026; natives of any single foreign state may not receive more than 7% of employment-based and family-sponsored visas; annual limits reset on Oct. 1, 2026, for the start of FY2027, when consulates may resume issuing EB-2 visas to qualified Indian applicants; a related alert notes the EB-5 unreserved visa limit for India was also met as of June 5, 2026.",
            "India-West (indiawest.com, June 2026) \u2014 'India Hits EB-2 Visa Cap; Processing Paused Until October': Indian applicants seeking permanent residency through EB-2 will no longer receive visa issuances for the remainder of FY2026; the State Department, working with USCIS, said all available EB-2 immigrant visas for applicants from India have been exhausted; the annual EB-2 allocation is capped at 28.6% of the worldwide limit and no single country may receive more than 7% of total employment-based and family-sponsored visas; the allocation resets Oct. 1, 2026.",
            "Manifest Law (manifestlaw.com, June 2026) \u2014 '46,000 Extra Employment Green Cards in FY 2026': roughly 46,000 additional employment-based green cards became available in FY2026 because of spillover from unused family-based numbers, helping explain forward movement in the March and April 2026 Visa Bulletins; because no single nation can receive more than 7% of the total supply, EB-2 India still reached its annual limit for FY2026 and will remain static until the next fiscal year begins on October 1, 2026; the trend of spillover could continue into FY2027."
        ]),
        "diaspora_angle": "The exhaustion of the EB-2 green-card category for India until October freezes one of the diaspora's main paths to U.S. permanent residency, stranding hundreds of thousands of Indian professionals \u2014 many long-time H-1B holders with families and homes \u2014 in temporary-visa limbo, and underscoring how the decades-old 7% per-country cap keeps Indian demand permanently mismatched with supply.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    ids = []
    ids.append(write_article_1())
    ids.append(write_article_2())
    print("\n" + "="*60)
    print(f"DONE. Inserted IDs: {[i for i in ids if i]}")
    print("="*60)
