#!/usr/bin/env python3
"""
Videshi News Writer — June 23, 2026 (12:30 UTC run)
2 NEW articles, both fresh & distinct from prior runs (which covered SpaceX,
NEET re-exam, Iran sanctions/oil, foreign-investor return, USTR Delhi trade,
China normalisation, PMI, RBI NRI deposits, Jio/NSE IPO, Russian crude, H-1B
$100k fee, student-visa duration, citizenship fee, CUET results, FCRA rules):
  1. July 2026 US Visa Bulletin — India EB-2 and EB-5 Unreserved go
     "Unavailable" for the rest of FY2026; EB-1 India retrogresses ~2 months;
     EB-3 inches forward. (immigration — diaspora green-card-backlog angle)
  2. US launches $750 expedited B1/B2 visa-interview pilot (Jul 1-Dec 31,
     2026) — pay extra for an appointment within 10 business days; doesn't
     speed processing or guarantee a visa. (immigration — diaspora
     family-visit / business-travel angle)
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


# ─── Article 1: July 2026 Visa Bulletin — India EB-2 / EB-5 unavailable ─────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: July 2026 Visa Bulletin")
    print("="*60)

    slug = "july-2026-visa-bulletin-india-eb2-eb5-unavailable-eb1-retrogress-green-card-diaspora-20260623"
    headline = "Two of the Main Roads to a US Green Card Just Closed for Indians \u2014 Until October at the Earliest"
    subheadline = "The State Department's July Visa Bulletin marks both the EB-2 and the unreserved EB-5 categories \"Unavailable\" for India and pushes the EB-1 cutoff back another two months \u2014 freezing tens of thousands of high-skilled Indian professionals and investors in a queue that no longer moves until the new fiscal year begins."

    body = """The United States has effectively shut two of the most important employment-based routes to a green card for Indian nationals, at least until the federal fiscal year resets on October 1. In its Visa Bulletin for July 2026, the State Department listed both the EB-2 category \u2014 the advanced-degree professionals' route that millions of Indian engineers, doctors and scientists rely on \u2014 and the unreserved EB-5 immigrant-investor category as "Unavailable" for applicants chargeable to India. For the first preference, EB-1, the India cutoff retrogressed again, slipping from December 15, 2022 to October 15, 2022.

The word "Unavailable" is not a typo or a temporary glitch. In the language of the bulletin, it means the government will not issue any green cards in that category for India for the rest of FY2026. The State Department had signalled this was coming: on May 22 it announced that the annual limit for Indian EB-2 visa issuance had already been reached, and in the June bulletin it warned that further retrogression \u2014 or making categories unavailable outright \u2014 might be necessary to keep number use within the per-country caps. July is the month that warning became reality.

## What Actually Changed

The damage is uneven across the employment-based ladder. EB-1, reserved for priority workers such as multinational executives and people of extraordinary ability, did not go unavailable but moved backwards by two months, so only Indians whose petitions were filed before October 15, 2022 can now have their cases finalised. EB-2, the workhorse category for India's white-collar diaspora, went from a cutoff of September 1, 2013 in June to flatly "Unavailable" in July \u2014 a category that was already running more than a decade behind has now stopped entirely.

There were two small consolations. EB-3, covering skilled workers and professionals, edged forward for India to a cutoff of January 1, 2014, a movement of roughly two weeks. And the EB-5 set-aside categories \u2014 the rural, high-unemployment and infrastructure investment tracks created by the 2022 reform \u2014 remain "Current" for India, meaning investors who put their money into those specific project types can still move ahead even as the unreserved EB-5 track for India closes. The Dates for Filing chart, which governs when an applicant can submit paperwork rather than when a visa is actually granted, still shows India EB-2 at January 15, 2015 and unreserved EB-5 at May 1, 2024 \u2014 but for adjustment-of-status filings in the United States, USCIS has been requiring the more restrictive Final Action Dates chart, so the "Unavailable" stamp is what bites.

## Why the Diaspora Should Care

For the Indian diaspora in America, this is the immigration story that touches the most lives most directly. Indians are the single largest group caught in the employment-based green-card backlog, a queue so long that government and think-tank estimates have for years put the realistic wait for some Indian EB-2 and EB-3 applicants in the decades. EB-2 and unreserved EB-5 going dark for a full quarter means that a worker who finally reached the front of the line this summer \u2014 someone who may have waited a decade or more \u2014 now watches the line stop moving entirely until the calendar turns to October.

The practical consequences are real and immediate. Applicants whose final action dates briefly became current cannot get their green cards approved during this window, even if every other document is in order. People weighing a job change, a promotion, or simply whether to keep renewing an H-1B for another three years must now factor in a category that has frozen with no firm restart date beyond the start of the next fiscal year. Families with children approaching 21 \u2014 the age at which a dependent can "age out" of a parent's petition \u2014 face the cruelest version of the squeeze, because every month the queue stalls is a month closer to a child losing their place. And for the immigrant-investor community, the closure of unreserved EB-5 for India steers fresh capital toward the rural and high-unemployment set-aside projects, the only EB-5 lanes still open to Indian money.

## What's Next

The clock now points to October 1, when FY2027 begins and a fresh annual allotment of immigrant-visa numbers becomes available. In most years, the categories that go unavailable late in a fiscal year spring back to a cutoff date when the new year starts, and applicants and attorneys will be watching the October bulletin closely to see how far the India dates recover \u2014 and how quickly demand eats through the new numbers. Until then, the message in the July bulletin is stark for hundreds of thousands of Indians who have built their American lives around a green card that is, for now, simply not being issued."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    # Topic imagery: US immigration / State Dept / passport / flag building. No single named person.
    img_url, ctitle = pick_commons([
        "Harry S Truman Building State Department Washington",
        "United States passport green card",
        "US Citizenship and Immigration Services building",
        "United States Capitol building Washington",
        "US visa document immigration"
    ])
    img_caption = "U.S. immigration documents; the State Department's July 2026 Visa Bulletin marked India's EB-2 and unreserved EB-5 categories \"Unavailable\""
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("united states passport immigration document")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A U.S. passport and immigration paperwork; India's main employment green-card routes are frozen until October"

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
            "Shusterman Immigration Law (shusterman.com) \u2014 Visa Bulletin July 2026 employment-based final action date chart: India EB-1 10-15-22; India EB-2 Unavailable; India EB-3 1-01-14; India EB-3 Unskilled/Other Workers 1-01-14; India EB-4 9-15-22; India EB-5 Unreserved Unavailable; India EB-5 Set Aside Current. Filing-date chart shows India EB-2 1-15-15 and India EB-5 Unreserved 5-01-24.",
            "Ogletree Deakins via JD Supra \u2014 USCIS Requires Final Action Dates for Employment-Based Filings (June 2026 Visa Bulletin): for June 2026, EB-1 India retrogressed by three and a half months and EB-2 India retrogressed by more than ten months; EB-3 India advanced one month; EB-5 Unreserved current for most countries; June 2026 India dates \u2014 EB-1 December 15, 2022, EB-2 September 1, 2013, EB-3 December 15, 2013, EB-5 Unreserved May 1, 2022; further retrogression or unavailability in EB-1, EB-2 and EB-5 Unreserved (India) flagged as possible before end of FY2026.",
            "U.S. Department of State, Visa Bulletin (travel.state.gov) \u2014 official guidance: 'Unavailable'/'U' means immigrant visa numbers are not authorized for issuance in that category; high demand and number use by India-chargeable applicants in EB-1 and EB-2 required retrogression to hold within FY2026 annual limits, with categories able to become 'Unavailable' before the September 30 fiscal year-end if per-country limits are reached; on May 22, 2026 the Department announced the India EB-2 annual issuance limit had been reached, so India EB-2 applicants would not receive immigrant visas for the rest of FY2026.",
            "The Citizen Edition (thecitizenedition.com) \u2014 July 2026 Visa Bulletin analysis: EB-2 and unreserved EB-5 designated 'unavailable' for the remainder of the fiscal year, EB-1 Final Action Date moved back roughly two months, EB-3 and EB-4 advanced slightly; categories reset when annual limits renew on October 1, 2026."
        ]),
        "diaspora_angle": "Indians are the largest group trapped in the US employment green-card backlog, so EB-2 and unreserved EB-5 going 'Unavailable' until at least October freezes tens of thousands of high-skilled Indian professionals and investors \u2014 and puts the children of long-waiting applicants at greater risk of 'aging out' before the queue restarts.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: $750 expedited B1/B2 visa-interview pilot ───────────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: $750 expedited US visa-interview pilot")
    print("="*60)

    slug = "us-750-dollar-expedited-b1-b2-visa-interview-pilot-july-2026-diaspora-family-visit-20260623"
    headline = "America Will Now Sell You a Faster Visa Interview for $750. India's Families Are the Obvious Market."
    subheadline = "From July 1, the State Department's six-month pilot lets B1/B2 visitor-visa applicants pay an extra $750 \u2014 four times the standard fee \u2014 to lock in an interview within 10 business days. It buys a slot, not a visa, and it does nothing to speed the background checks that follow."

    body = """The United States is about to put a price on jumping the visa-interview queue. Under a Temporary Final Rule announced by the State Department and the Bureau of Consular Affairs, eligible applicants for B-1 (business) and B-2 (tourism) visitor visas will be able to pay an additional $750 fee to secure an interview appointment within 10 business days at participating embassies and consulates. The pilot runs from July 1 to December 31, 2026, after which the department will decide whether to keep, change or scrap it.

The fee is steep by design. It sits on top of the standard $185 visa application fee, meaning an applicant who opts in pays roughly $935 before they have spoken to a single consular officer \u2014 about four times the usual cost. And it is important to be precise about what the money buys. The $750 guarantees a faster interview slot. It does not guarantee a visa, and it explicitly does not accelerate the background checks, administrative processing or the final adjudication that determine whether the visa is ultimately granted. An applicant can pay for speed at the front door and still wait the usual length of time \u2014 or be refused \u2014 once inside.

## How It Works, and Who It's For

Until now, applicants desperate to move up the queue had limited and discretionary options: submit a written justification, or seek help through the Priority Appointment Request or Referrals processes, both of which depend on a consular officer's judgement. The pilot replaces some of that discretion with a flat, payable fee. The service is optional, limited in quantity, and confined to the B1/B2 visitor categories \u2014 it does not touch H-1B work visas, F-1 student visas or immigrant-visa interviews. The State Department has not yet published the list of participating posts, and crucially has not confirmed whether India's high-volume missions will be among them.

That last detail is where the suspense lies for Indian applicants, because India is one of the places where the everyday pain of visa wait times is sharpest. Appointment backlogs at US consulates in India have at various points stretched into many months, long enough that a parent hoping to attend a child's graduation, a wedding, or the birth of a grandchild could miss the event entirely while waiting for a slot. A guaranteed 10-business-day interview is precisely the kind of relief that population has been asking for \u2014 if, and only if, the Indian posts are included when the participating list is released.

## Why the Diaspora Should Care

For the Indian diaspora in the United States, the B1/B2 visa is the thread that keeps families connected across an ocean. It is the visa that brings parents over for months at a time, that lets siblings attend weddings, that allows a relative to help with a newborn. The diaspora is, in effect, the natural customer base for a pay-to-skip-the-line product: a US-based professional with the means to spend an extra $750 to get an ageing parent an interview in two weeks rather than two months will, for many, consider it money well spent.

But the pilot also sharpens an uncomfortable question about fairness. A scheme that lets those who can pay move ahead of those who cannot risks turning a public service into a tiered one, where a well-paid software engineer's parents get an interview in ten days while a less affluent family waits out the standard queue. The $750 figure is trivial for some diaspora households and prohibitive for others, and the same family event \u2014 a wedding date, a medical emergency, a graduation \u2014 does not wait for either. For NRIs weighing the option, the calculus is unusually concrete: the fee is real, the time saved could be real, but the outcome of the application itself is no more certain than before.

## What's Next

The immediate unknown is the roster of participating embassies and consulates, which the State Department has yet to announce; whether the missions in New Delhi, Mumbai, Chennai, Hyderabad and Kolkata take part will determine whether this is a meaningful option for Indian families or a footnote that applies elsewhere. Beyond that, the six-month window is a test. If demand is high and the system holds, the department may extend or expand it; if it strains consular capacity or draws a backlash over equity, it could quietly lapse at the end of December. Either way, the principle it establishes \u2014 that a faster appointment can be bought \u2014 is a notable shift in how the world's most sought-after travel document is rationed, and the Indian diaspora will be among the first to feel which way it cuts."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    # Topic imagery: US embassy / consulate / visa / passport. No single named person.
    img_url, ctitle = pick_commons([
        "Embassy of the United States New Delhi",
        "United States passport visa",
        "US consulate building India",
        "United States visa document",
        "Statue of Liberty New York"
    ])
    img_caption = "A U.S. visa and travel documents; a State Department pilot lets B1/B2 applicants pay $750 for a faster interview from July 1, 2026"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("united states visa passport travel")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A U.S. passport and visa; the State Department's pilot offers a faster interview slot for an added $750 fee"

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
            "Travel and Leisure Asia (travelandleisureasia.com) \u2014 US Visa Interview: Pay USD 750 To Get An Appointment In 10 Days (June 22, 2026): US State Department and Bureau of Consular Affairs launched a temporary pilot program running July 1 to December 31, 2026; eligible B-1 (business) and B-2 (tourism) applicants can pay an additional USD 750 fee on top of the standard USD 185 application fee for an expedited interview appointment within 10 business days at selected embassies; the fee guarantees a faster appointment, not a visa; background checks and administrative processing timelines remain unchanged; service is optional and limited in quantity; effected via a Temporary Final Rule (TFR).",
            "Outlook Traveller (outlooktraveller.com) \u2014 US To Offer Faster Visa Appointments Within 10 Days\u2014For An Additional Fee (June 23, 2026): pilot set to launch in July 2026; expedited appointment service costs USD 750 in addition to the standard USD 185 visa application fee (nearly four times the standard fee); paying the fee does not guarantee a visa, only a faster interview within 10 business days; standard background checks, administrative reviews and final visa decisions follow the same processes and timelines; list of participating embassies and consulates \u2014 including whether the service will be available in India \u2014 is yet to be announced; previously applicants could move up the queue only via written justification, Priority Appointment Request or Referrals.",
            "U.S. Department of State / Bureau of Consular Affairs \u2014 Temporary Final Rule on expedited visa-interview appointment service: applies to B-1/B-2 nonimmigrant visitor-visa applicants; optional add-on fee for an expedited interview appointment; effective July 1 through December 31, 2026; does not affect adjudication standards or processing times; State Department to assess after the pilot period whether to continue or adjust the service."
        ]),
        "diaspora_angle": "The B1/B2 visitor visa is how the Indian diaspora brings parents and relatives over for weddings, graduations and newborns, so a pay-$750-to-skip-the-line option is squarely aimed at NRI families \u2014 valuable if India's high-backlog consulates are included, but raising hard questions about a tiered system where only those who can pay get a fast interview.",
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
