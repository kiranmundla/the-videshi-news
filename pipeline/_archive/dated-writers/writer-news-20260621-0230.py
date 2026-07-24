#!/usr/bin/env python3
"""
Videshi News Writer — June 21, 2026 (02:30 UTC run)
2 NEW articles:
  1. DHS final rule ending "Duration of Status" for F-1 students clears White House/OMB —
     imminent release, ~360k Indian students affected (immigration)
  2. India's state fuel retailers hitting borrowing limits as Q1 losses top Rs 1 trillion —
     pump-price policy under strain after the Gulf oil shock (economy)
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

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"


# ─── Image sourcing functions ────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
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
            return pick["url"]
    return None


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


# ─── Article 1: F-1 fixed-duration final rule clears OMB ──────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: F-1 Duration of Status final rule clears White House")
    print("="*60)

    slug = "dhs-f1-duration-of-status-final-rule-clears-omb-indian-students-fixed-four-year-20260621"
    headline = "The Rule That Will End Open-Ended Study in America Just Cleared the White House. 360,000 Indian Students Are Next."
    subheadline = "For three decades, an F-1 visa let students stay as long as they kept studying. A final rule that quietly cleared the Office of Management and Budget this week replaces that with a fixed four-year clock \u2014 and Indians are the largest group caught by it."

    body = """For more than thirty years, the deal for an international student in America was simple to understand. Your F-1 visa did not carry an expiry date stamped against the calendar; it carried "D/S" \u2014 duration of status. As long as you stayed enrolled, made academic progress and obeyed the rules, you could remain in the country to finish your degree, add a second one, or move from a bachelor's to a master's to a PhD without asking Washington for permission each time.

That arrangement is now in its final days. The Department of Homeland Security's rule replacing duration of status with a fixed period of admission cleared the White House Office of Management and Budget this week \u2014 the last bureaucratic gate before a regulation is published. OMB signed off on the final rule, identified in the regulatory docket as RIN 1653-AA95, on Wednesday. Once it appears in the Federal Register, the countdown to implementation begins.

## What Actually Changes

Under the new framework, most international students will be admitted for a fixed term \u2014 generally up to four years \u2014 rather than for the open-ended duration of their studies. Anyone who needs more time, whether to finish a longer programme, move to a higher degree, or stay on for post-graduation work, will have to file a formal extension-of-stay application with US Citizenship and Immigration Services and wait for approval.

The proposal, first published by DHS in August 2025 and submitted to OMB in early May, bundles several other restrictions alongside the headline change. Students in shorter programmes would be expected to leave at the end of the course unless granted an extension; language students face a 24-month cap. Graduate students would be barred from switching programmes, and the rule would block "lateral or reverse" moves \u2014 starting a new programme at the same or a lower level after finishing one. Crucially, the open-ended grace that designated school officials on campus could grant would be replaced by a federal process that runs through USCIS.

## Why Indians Are at the Centre of This

No nationality has more at stake. According to the latest Open Doors data, there were roughly 360,000 Indian students in the United States in the 2024-25 academic year \u2014 about 31% of all 1.1 million international students, the single largest cohort. Indian enrolment skews heavily toward STEM master's and doctoral programmes, exactly the longer and multi-stage academic paths most exposed to a hard four-year ceiling.

The deeper danger is procedural. Under the current system, a student only begins accruing "unlawful presence" if an immigration officer or judge formally rules that status was violated. Immigration lawyers warn that under the new rule, the clock could start the moment a fixed admission period lapses \u2014 even if an extension application is still pending. More than 180 days of unlawful presence triggers a three-year re-entry bar; more than a year triggers a ten-year ban. For a student waiting months on a USCIS queue, an administrative backlog could quietly harden into an exile.

There is a knock-on risk for those on Optional Practical Training, the post-study work window that is the main bridge to an H-1B visa. Attorneys have flagged that OPT holders could face work-authorisation gaps if their admission period expires while an extension is in process, even when they hold a valid employment card.

## What It Means for the Diaspora

For Indian families, an American degree has long been a multi-year project financed with loans, sold property and savings \u2014 a calculated bet that a student admitted today can see the plan through to a job offer and, eventually, a green-card line. The fixed-duration rule injects fresh uncertainty into every stage of that bet. A delayed extension is no longer just paperwork; it can mean a lapse in status, a lost work permit, or a re-entry bar that upends a family's plans on both continents.

College groups and medical organisations fought the same idea when the first Trump administration floated it, arguing it would saddle students and universities with needless administrative hurdles and chill enrolment. Foreign enrolment at US universities already dipped this past year for the first time in three. The rule is not yet law: publication in the Federal Register, typically followed by a short implementation window, comes next, and litigation is likely. But the clearance at OMB means the most consequential change to the international-student system in a generation is no longer a proposal on a comment docket. It is a final rule, waiting to be switched on."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = pick_commons([
        "university graduation ceremony students",
        "international students university campus",
        "college graduation diploma students",
        "university lecture hall students"
    ])
    img_caption = "International students at a US university graduation; Indians are the largest foreign-student cohort in America"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("university graduation students")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Students at a university graduation ceremony"

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
            "Bloomberg Law \u2014 Rule Limiting Foreign Students in US Cleared by White House (June 2026): OMB cleared final rule RIN 1653-AA95 on Wednesday, last step before public release; replaces duration of status with fixed four-year admission",
            "Bloomberg Law \u2014 White House Reviewing Rule to Limit Foreign Students' Status: final rule sent to OMB's OIRA; four-year stay periods before renewal with DHS; also limits J-1 and I visa holders",
            "USA Today / Times of India (immigration attorney Rajiv S. Khanna) \u2014 360,000 Indian students = ~31% of 1.1M international students (Open Doors 2024-25); unlawful-presence accrual on expiry; OPT work-authorisation interruption risk; bar on graduate program changes and reverse matriculation",
            "ICEF Monitor \u2014 US to end 'Duration of Status' for F, J and I visas: ~4-year completion expectation; 60-day implementation period; 24-month cap for language students",
            "Washington University OISS / Cornell ISS guidance \u2014 DHS proposed rule published Aug 28, 2025; final rule submitted to OMB May 5, 2026; I-539 extension process; restrictions on transfers and changes of educational objective"
        ]),
        "diaspora_angle": "Indians are the single largest group of international students in the United States \u2014 roughly 360,000, about 31% of all foreign students \u2014 and the new fixed four-year admission rule reshapes the multi-year bet families make on a US degree, with delayed extensions risking lapsed status, lost OPT work permits, and multi-year re-entry bars.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: India's fuel retailers hit borrowing limits ──────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: India's state fuel retailers hit borrowing limits")
    print("="*60)

    slug = "india-state-fuel-retailers-borrowing-limits-one-trillion-rupee-losses-gulf-oil-shock-20260621"
    headline = "India Held the Line on Petrol Prices Through a War. Now Its State Oil Companies Are Running Out of Room to Borrow."
    subheadline = "While much of the world passed the Gulf oil shock straight to the pump, India's refiners absorbed it \u2014 and the bill has reached a trillion rupees in a single quarter, with IOC, BPCL and HPCL now bumping against their borrowing limits."

    body = """When the war in the Gulf sent crude prices spiking toward $120 a barrel this spring, governments around the world did the obvious thing: they let the cost flow to the petrol pump. Across many countries, retail prices of gasoline and diesel jumped 40% to 50%. India did something else. It held the line, raising pump prices for the two fuels by less than 10%, and asked its state-owned oil companies to swallow the difference.

That decision is now showing up on the balance sheets. India's oil secretary, Neeraj Mittal, told an industry gathering on Thursday that state fuel retailers' revenue losses in the first quarter of this year had risen to roughly one trillion rupees \u2014 about $10.6 billion \u2014 as they sold petrol, diesel and cooking gas below market rates. The three big state retailers, Indian Oil Corporation, Bharat Petroleum and Hindustan Petroleum, have been borrowing to cover those losses. And, Mittal warned, that borrowing is now hitting its limits.

## A Subsidy by Another Name

India did not announce a fuel subsidy this spring. But by capping pump-price increases while crude soared, it effectively created one \u2014 paid not from the budget but from the books of three listed companies the government controls. For a few months, that shielded households and businesses from the full force of the oil shock. It kept inflation in check, steadied the rupee, and avoided the political pain of a sudden spike in transport and food costs.

The cost of that shield is now coming due. When a company that imports oil at war-inflated prices and sells it at home for less keeps doing so quarter after quarter, the gap has to be funded somewhere \u2014 and the funding has been debt. As borrowing approaches its ceilings, the retailers face a squeeze: keep absorbing losses and risk their balance sheets, or pass more of the cost to consumers and risk the inflation and political fallout New Delhi has worked to avoid.

## Why the Pressure Isn't Over

The truce in the Gulf has cooled crude back toward $82 a barrel, which should, in time, ease the bleeding. But the relief is fragile. Iran's Revolutionary Guards declared the Strait of Hormuz shut again on Saturday even as peace talks opened in Switzerland, a reminder that the chokepoint carrying roughly a third of India's crude can swing on a single statement. India's energy import bill had already soared nearly 82% year-on-year in May to $18.7 billion as the country leaned on costlier non-Middle Eastern cargoes. Until the ceasefire firms into something durable, the math that drove the retailers into the red could return with little warning.

The government has signalled it expects the companies to recover their losses gradually as prices normalise rather than through a one-time pump-price shock. But with borrowing limits in sight, the room to wait is shrinking.

## Why It Matters for the Diaspora

For NRIs, this is a story that runs underneath almost everything else they track about India. State oil companies are among the heaviest weights in the Nifty and Sensex; their stretched balance sheets and the dividends the government leans on from them feed directly into the market portfolios and mutual funds many in the diaspora hold back home. Fuel prices, in turn, shape inflation, and inflation shapes the rupee \u2014 the single number that governs the value of every remittance sent home and every NRI deposit parked in an Indian bank.

There is a more direct stake too. Families with property, businesses or aging parents in India feel pump prices in the cost of everything from a delivery van's diesel to an autorickshaw fare to the price of vegetables trucked to a city market. India's choice to absorb the Gulf shock has, for now, kept those everyday costs from jumping. Whether it can keep doing so \u2014 and what happens to three of the country's biggest companies if it does \u2014 is the quiet sequel to a war that never quite reached the Indian pump."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = pick_commons([
        "Indian Oil petrol pump station",
        "petrol pump India fuel station",
        "fuel station India Bharat Petroleum",
        "petrol station fuel nozzle"
    ])
    img_caption = "A fuel station in India; state retailers IOC, BPCL and HPCL absorbed the Gulf oil shock at the pump"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("petrol pump fuel station")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A fuel pump at a petrol station"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters \u2014 Indian state fuel retailers hitting borrowing limits, says official (June 2026): oil secretary Neeraj Mittal says Q1 revenue losses risen to 1 trillion rupees ($10.6B); IOC, BPCL, HPCL borrowing rising to cover losses; India raised petrol/diesel prices <10% vs 40-50% elsewhere",
            "Reuters \u2014 India's May oil supply / energy import bill: import bill +82% YoY in May to $18.7 billion as India leaned on costlier non-Middle Eastern crude",
            "Reuters \u2014 US disputes Iranian claims about closing Strait of Hormuz (June 21, 2026): IRGC declares Strait shut Saturday as Switzerland talks open; Brent near $82 after the ceasefire",
            "Reuters \u2014 Indian shares climb on Gulf peace deal: Brent fell ~5% to about $82.8 a barrel, lowest since March; lower oil a positive for inflation, rupee and trade deficit"
        ]),
        "diaspora_angle": "India absorbed the Gulf oil shock by capping pump prices and pushing the losses onto state oil giants IOC, BPCL and HPCL \u2014 heavyweight stocks in the Nifty and Sensex that NRI portfolios and mutual funds hold \u2014 and the resulting strain feeds into inflation, the rupee, and the everyday cost of living for families back home.",
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
