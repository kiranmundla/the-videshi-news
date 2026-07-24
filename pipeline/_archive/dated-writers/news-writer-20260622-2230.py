#!/usr/bin/env python3
"""
Videshi News Writer — June 22, 2026 (22:30 UTC run)
2 NEW articles (both fresh, distinct from the 30 most recent news pieces):
  1. 'Documented Dreamers' — ~250,000 children of legal (mostly Indian) work-visa
     holders face 'aging out' at 21 and self-deportation; renewed diaspora push
     for the bipartisan America's CHILDREN Act. (immigration / diaspora)
  2. White House/OMB has cleared a DHS proposal to scrap the open-ended F-1
     'Duration of Status' system for fixed admission terms and cut the post-study
     grace period from 60 to 30 days — hitting ~360,000 Indian students, the
     largest international cohort in the US. (immigration / students)
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



# ─── Article 1: Documented Dreamers / America's CHILDREN Act ─────────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Documented Dreamers / America's CHILDREN Act")
    print("="*60)

    slug = "documented-dreamers-indian-diaspora-aging-out-americas-children-act-deportation-20260622"
    headline = "They Grew Up American. At 21, the Law Says They Have to Leave."
    subheadline = "An estimated 250,000 'Documented Dreamers' — many of them the children of Indian professionals on work visas — face self-deportation when they turn 21 and age out of their parents' green-card line. A renewed push for the bipartisan America's CHILDREN Act is the diaspora's last, narrow hope."

    body = """Muhil Ravichandran was two years old when she arrived in the United States. She is 24 now, and the country she has called home for almost her entire life is preparing to push her out. "Due to the Green Card backlog, I had aged out by the time my parents finally received their green cards," she said. "My future is now uncertain." She is not undocumented. She did nothing wrong. She is one of an estimated 250,000 young people the immigration system has a cold name for: Documented Dreamers — and a disproportionate share of them are the children of Indian families.

Their predicament is a quiet cruelty buried in the machinery of US immigration law. They came as small children, lawfully, as dependents on a parent's employment-based visa — most often the H-1B that powers Silicon Valley and America's hospitals and universities. They grew up here, went to American schools, and in many cases know no other home. But the Immigration and Nationality Act defines a "child," for immigration purposes, as someone unmarried and under 21. The day they turn 21, they "age out" of their parent's pending green-card application and lose their dependent status — even if the family has been waiting in line, in good faith, for the better part of two decades.

## The Math of the Backlog

For Indian families, the trap is almost guaranteed by arithmetic. More than 1.2 million Indians, including dependents, are stuck in the employment-based green-card queue across the EB-1, EB-2 and EB-3 categories, according to an analysis of USCIS data by the National Foundation for American Policy. Because the law caps how many green cards any single country can claim in a year, the Indian backlog has stretched so long that estimates for some categories run to decades. A child who arrives at age five can comfortably hit 21 — and age out — while the family's place in line has barely moved.

When that happens, the options are bleak: file a fresh application from the back of a different line, fall out of status and become undocumented in the only country they have ever known, or self-deport to a "home" country they may not remember and whose language they may not speak. Laurens van Beek, one Documented Dreamer profiled in earlier years, had to leave for Belgium after college — his first international flight since arriving in the US at age seven.

## A Bill With Rare Bipartisan Support

The fix has a name and a number. The America's CHILDREN Act, introduced by Representatives Deborah Ross of North Carolina and Mariannette Miller-Meeks of Iowa, would do two things. It would create a pathway to permanent residency for young people who grew up here — generally those present in the US for at least ten years, eight of them as dependents under 21, and who graduated from an American university. And it would establish age-out protections going forward, locking in a child's age for immigration purposes as of the date their parents filed for a green card, so that a family that arrived together is allowed to stay together.

Advocates note it is among the most bipartisan immigration measures in Congress, having drawn Republican and Democratic co-sponsors in equal measure and Senate support spanning Rand Paul, Alex Padilla and others. In 2022, the House even passed an age-out protection as a bipartisan amendment to the defense authorization bill, 329-101, before it stalled in the Senate. "It is time to permanently end the aging out and pass the America's CHILDREN Act," said Dip Patel, founder of Improve The Dream, the organization that has carried the issue to Capitol Hill for years. "Fixing this loophole will ensure that America reaps the benefits of the contributions of the children it raised and educated."

## Why It Matters to the Diaspora

This is the most intimate immigration fight the Indian community faces, because it is about its own children. A family can do everything right — arrive legally, pay taxes, build a life, wait patiently in a line not of its making — and still watch a son or daughter forced out on a 21st birthday. For a community that prizes education and stability above almost everything, the prospect of a US-raised, US-educated child being deported to a country they left as a toddler is a particular kind of heartbreak.

The bill's fate now sits with a Congress bitterly divided on immigration, where even rare bipartisan measures struggle to reach the floor. For the quarter-million young people running, as one report put it, "from pillar to post," and for the parents who brought them, the window is narrow and the clock is the most unforgiving thing of all: it is their own age."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url, ctitle = pick_commons([
        "United States Capitol building Washington",
        "US Congress immigration rally",
        "United States Citizenship and Immigration Services building",
        "immigration reform demonstration Washington DC"
    ])
    img_caption = "The US Capitol; a renewed push for the bipartisan America's CHILDREN Act seeks to protect young 'Documented Dreamers' from aging out"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("united states capitol washington")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "The US Capitol in Washington, where the America's CHILDREN Act awaits action to protect Documented Dreamers from deportation"

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
            "The Indian EYE \u2014 'Documented dreamers' of Indian diaspora in US face uncertain future (June 2026): Indian Americans seek passage of America's Children Act; ~250,000 documented dreamers enter the US as child dependents on employment-based visas and face an uncertain future or deportation when they turn 21; Muhil Ravichandran, 24, came to the US at age 2 and aged out due to the green card backlog; Dip Patel of Improve The Dream urges Congress to end aging out",
            "American Immigration Council \u2014 Documented Dreamers: An Overview: the America's CHILDREN Act would amend the Immigration and Nationality Act to protect documented dreamers from aging out; dependents on a parent's work visa for at least eight years before turning 21 could use their age at the time of the initial nonimmigrant petition; previously denied applicants could reopen cases within two years of enactment",
            "Bipartisan Policy Center \u2014 Documented Dreamers: An Explainer: America's Children Act (H.R. 4331) introduced by Reps. Deborah Ross (D-NC) and Mariannette Miller-Meeks (R-IA); provides a pathway to permanent residency, age-out protections, work authorization, and lets aged-out children retain their original green-card priority date by locking in age on the filing date; a version was attached to the FY2023 NDAA and passed the House 329-101 on July 14, 2022",
            "Reason \u2014 When Will Congress Protect Documented Dreamers?: the bill is among the most bipartisan immigration measures in Congress, with 14 Republican and 14 Democratic House co-sponsors and Senate sponsors including Rand Paul (R-KY), Alex Padilla (D-CA) and Kyrsten Sinema (I-AZ); it would grant permanent residency to those present 10 years (eight under age 21) who graduated from a US university; Documented Dreamer Laurens van Beek had to self-deport to Belgium after college",
            "India Today / National Foundation for American Policy \u2014 Why thousands of children of Indian-Americans face deportation risk: over 250,000 children of legal immigrants, many Indian-American, are at risk due to 'aging out'; NFAP analysis of USCIS data found over 1.2 million Indians including dependents waiting for green cards in EB-1, EB-2 and EB-3 categories; the INA defines a child as unmarried and under 21"
        ]),
        "diaspora_angle": "An estimated 250,000 'Documented Dreamers' \u2014 a disproportionate share of them children of Indian H-1B and other work-visa holders trapped in a green-card backlog of more than 1.2 million Indians \u2014 face losing legal status and self-deporting the day they turn 21, making the America's CHILDREN Act the most intimate immigration fight the diaspora faces because it is about its own US-raised children.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: F-1 Duration of Status rule cleared by White House ──────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: F-1 Duration of Status rule cleared by White House")
    print("="*60)

    slug = "us-f1-duration-of-status-fixed-term-rule-indian-students-30-day-grace-period-20260622"
    headline = "Washington Just Moved to End the Open-Ended Student Visa. India's 360,000 Students Are First in Line."
    subheadline = "The White House budget office has cleared a DHS rule that would scrap the decades-old 'Duration of Status' system for fixed admission terms and halve the post-study grace period to 30 days. Indian students, the largest international cohort in the US, stand to be hit hardest."

    body = """For decades, an international student admitted to the United States on an F-1 visa has lived under a simple, generous rule: stay as long as your studies last. That rule is now on the chopping block. The White House Office of Management and Budget has completed its review of a Department of Homeland Security proposal to abolish "Duration of Status" — the open-ended admission that lets students remain in the country as long as they are enrolled full-time — and replace it with fixed terms of admission. For the roughly 360,000 Indians studying in America, the largest international student population in the country, it could become the biggest change to the student-visa system in a generation.

Under the current system, a student is admitted for "D/S" — duration of status — and can move from an undergraduate degree to a master's, then on to Optional Practical Training (OPT) or STEM OPT, all without seeking a fresh period of admission. The proposed rule would end that flexibility. Students would be admitted for a set window, and anyone needing more time would have to file an extension request with US Citizenship and Immigration Services — new paperwork, new fees, and a new chance for the answer to be no.

## What Would Change

Reports indicate the fixed term would run somewhere between two and four years. That is a poor fit for the very students India sends in the largest numbers: those in doctoral, research and specialised programmes that routinely run longer than four years. A PhD candidate four years into a six-year program could find themselves filing for an extension mid-dissertation, their ability to keep studying hostage to a processing queue.

A second change cuts just as deep. The post-study grace period — the cushion that currently gives graduates 60 days to leave the country, line up further study, or switch to a work visa — would be halved to 30 days. For a new graduate scrambling to convert an OPT job offer into H-1B sponsorship, losing a month of runway is the difference between a smooth transition and falling out of status. The rule would also subject university transfers and course changes to fresh review, adding friction to choices students now make freely.

## A Squeeze From Several Directions

The student-visa overhaul does not arrive in isolation. It lands amid a broader tightening that has already unsettled the diaspora: a proposed near-doubling of the naturalization fee, the elimination of fee waivers, the July visa bulletin freezing the EB-2 and EB-5 green-card categories for Indians, and a contested $100,000 H-1B fee that a Boston judge struck down only for the government to seek its reinstatement. Together they form a wall that rises a little higher at every stage of the journey — study, work, permanent residency, citizenship.

Immigration lawyers warn the practical effect could be to narrow the pathways Indian graduates rely on most. Many who miss out in the H-1B lottery currently lean on "Day 1 CPT" programmes — enrolling in a further course to keep working legally — a route that could close if students can no longer easily extend or stack programmes. "There's no doubt about it that this is going to have a massive impact on the companies that are in desperate need of top talent," immigration attorney Jennifer Goldman warned, noting that foreign nationals make up a large share of the US AI and engineering talent pool.

## Why It Matters to NRIs

For Indian families, sending a child to study in America has long been a defining aspiration — a down payment on a career, often a first step toward a green card and a life in the US. Nearly 360,000 Indian students enrolled in the 2024-25 academic year, pouring billions into American universities and local economies. A system that forces them to repeatedly re-justify their presence, and that shortens the window to convert a degree into a job, changes that calculus. The diaspora has watched its students reroute toward Canada, the UK and Australia as US rules tightened; this proposal gives them another reason to look elsewhere.

The rule is not yet law. It must still be published in the Federal Register and run a public-comment period before taking effect, and DHS frames it as a measure to better track visa overstays. But Indian-origin Congressman Raja Krishnamoorthi has already raised concerns that piling on immigration hurdles will erode America's ability to attract global talent. For the families weighing tuition deposits this summer, the message from Washington is unmistakable: the open door is being fitted with a lock."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url, ctitle = pick_commons([
        "university graduation ceremony students",
        "international students university campus United States",
        "college graduates commencement",
        "university library students studying"
    ])
    img_caption = "International students at a US university; a proposed DHS rule would replace open-ended F-1 status with fixed admission terms"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("university graduation students")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "University graduates; Washington has cleared a rule to end the open-ended F-1 'Duration of Status' system for international students"

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
            "Outlook Business \u2014 US Clears Visa Rule Change, Foreign Students May Face Stay Limits, Here's What It Means For Indians (June 22, 2026): the OMB has completed review of a DHS proposal to replace the open-ended Duration of Status system with fixed admission periods for F-1 students; ~360,000 (3.6 lakh) Indian students enrolled in 2024-25 per Open Doors; post-study grace period would be cut from 60 to 30 days; rule to be published in the Federal Register before taking effect later this year; Indian-origin Congressman Raja Krishnamoorthi raised concerns",
            "Shiksha \u2014 US Student Visa Shake-Up: 3.6 Lakh Indian Students Face Fixed Stay Limits (June 2026): OMB cleared a DHS proposal to scrap open-ended Duration of Status; five changes proposed including fixed admission period set at entry, mandatory USCIS extension requests, new approval for OPT/STEM OPT transitions, 30-day grace period (down from 60), and fresh review for transfers and course changes; rule still requires Federal Register publication",
            "The Indian EYE / Tighter student visa rules may impact Indians in US: Expert (June 2026): immigration attorney Jennifer Goldman warns the reduced 60-to-30-day grace period and fixed terms could narrow 'Day 1 CPT' pathways used by graduates who miss the H-1B lottery; thousands of Indian professionals in AI, machine learning, software engineering and data science could face uncertainty; 'massive impact' on companies in need of top talent",
            "Tupaki \u2014 Trump Gives Another Shock To Indians (June 21, 2026): White House cleared a DHS rule to replace F-1 Duration of Status with fixed admission periods of 2-4 years; affects F-1, J-1 and I visas covering work, study, media and journalism; rule has completed White House review but not yet been publicly released; framed by the administration as closing a long-term legal migration loophole",
            "US Open Doors data / Institute of International Education: nearly 360,000 (3.6 lakh) Indian students enrolled at US institutions during the 2024-25 academic year, the largest international student population in the United States, many in doctoral, research and specialised programmes lasting more than four years"
        ]),
        "diaspora_angle": "Indians are the largest international student population in the US at roughly 360,000, many in multi-year doctoral and research programmes, so a rule scrapping open-ended F-1 'Duration of Status' for fixed 2-4 year terms and halving the post-study grace period to 30 days strikes at a defining diaspora aspiration and the study-to-work-to-green-card pathway thousands of NRI families depend on.",
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
