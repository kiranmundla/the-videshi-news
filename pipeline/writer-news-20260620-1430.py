#!/usr/bin/env python3
"""
Videshi News Writer — June 20, 2026 (14:30 UTC run)
2 NEW articles:
  1. UAE grants a final 30-day visa grace period (June 10–July 9) for residents
     stranded by the spring airspace disruptions (diaspora-mobility / Gulf NRIs)
  2. The Fed's Warsh era opens hawkish — dot plot flips toward a 2026 hike,
     dollar firms, rupee and NRI money feel it (economy / diaspora-finance)
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


# ─── Article 1: UAE final 30-day visa grace period ──────────────────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: UAE final 30-day visa grace period")
    print("="*60)

    slug = "uae-final-30-day-visa-grace-period-overstay-fines-airspace-disruption-indian-residents-20260620"
    headline = "The UAE Just Gave Stranded Residents One Last Window. For Indians Caught by the Spring Airspace Chaos, the Clock Runs to July 9."
    subheadline = "Abu Dhabi's identity authority has opened a final 30-day grace period \u2014 running June 10 to July 9 \u2014 for those who benefited from this spring's overstay-fine waivers, letting them regularise their status or leave penalty-free as the Gulf's largest Indian community sorts out paperwork left in limbo by the regional flight shutdowns."

    body = """For the hundreds of thousands of Indians who keep the United Arab Emirates running \u2014 and who found their travel plans torn up when the region's skies closed this spring \u2014 the federal government has just offered a clear, time-bound off-ramp. The UAE's Federal Authority for Identity, Citizenship, Customs and Ports Security, known as the ICP, has announced a final 30-day grace period for anyone who previously benefited from the overstay-fine exemptions granted during the airspace disruptions earlier this year.

The window is precise. It began on June 10 and runs until July 9, 2026. Within those dates, eligible residents can either regularise their residency or employment status and stay in the country, or leave the UAE without paying a single dirham in overstay penalties.

## What the Grace Period Actually Covers

The relief traces back to a turbulent spring. In March 2026, after airspace closures and flight suspensions snarled travel across the region from late February onward, the ICP waived overstay fines for people who simply could not get out in time. That exemption applied to a broad group: ordinary visa holders, individuals already issued departure permits, and residents whose visas had been cancelled but who were physically unable to leave because flights had stopped.

The new announcement is the closing chapter of that policy. The ICP framed it as a consequence of the region returning to normal \u2014 with stability restored and flights running on schedule, the open-ended waiver is being wound down and replaced by a firm one-month runway. Crucially, the authority confirmed that affected individuals do not need to file any fresh application to benefit; eligibility carries over automatically. Those who want to stay can complete the standard procedures to fix their legal status, and those who want to go can depart through ordinary channels, fine-free, before the deadline.

## Why the Timing Matters for Indians

No diaspora has more skin in this than India's. Indians are the single largest expatriate community in the UAE \u2014 more than three and a half million people, roughly a third of the country's entire population. They span the spectrum, from construction crews and delivery riders to nurses, accountants, engineers and small-business owners, and a great many of them travel home to India on tight, cost-sensitive schedules.

When the airspace closed this spring, it was precisely those workers \u2014 the ones who had booked the cheapest possible fares, who were mid-transfer between jobs, or whose visas were already in the cancellation pipeline \u2014 who got caught. A worker whose residence visa lapsed while flights were grounded had no clean way to either renew or exit. The grace period is, in effect, a reset button for exactly that predicament, and the practical advice from the missions is simple: do not let the date slip. After July 9, the ordinary overstay-fine regime snaps back into force.

## A Second Deadline NRIs Should Note

The grace period also lands in the same fortnight as a separate, unrelated piece of UAE consular news that Indians have been tracking. Indian passport, visa and attestation services across the UAE are set to pause for five days, from June 26 to June 30, as the missions transition to a new outsourced provider, Al Hind Tours and Travel LLC, with a new appointment portal going live on July 1. The two timelines overlap awkwardly: anyone hoping to regularise their status before the July 9 grace deadline should account for that service blackout and move early rather than banking on the final days.

## Why It Matters for the Diaspora

For the Gulf's Indian families, this is the kind of bureaucratic housekeeping that quietly decides whether a household stays whole or gets split across borders. An overstay fine in the UAE can run into thousands of dirhams and, left unresolved, can harden into a re-entry ban \u2014 a disproportionate punishment for someone whose only mistake was being unable to board a cancelled flight.

The ICP's message, repeated in its statement, is to rely only on official channels and ignore the rumour mill that tends to swirl around visa changes. For the millions of Indians whose remittances home are a lifeline \u2014 and who collectively send back a record share of India's foreign earnings \u2014 a clean, penalty-free path to fix their papers is more than administrative trivia. It is the difference between a stable Gulf posting and an expensive, avoidable scramble. The window is open now. It closes on July 9."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "Abu Dhabi's skyline; the UAE has opened a final 30-day grace period for residents stranded by the spring airspace disruptions"
    img_attribution = "Wikimedia Commons"

    for q in ["Abu Dhabi skyline", "Dubai immigration airport terminal", "Abu Dhabi city UAE", "Dubai International Airport"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            t = commons[0]["title"].lower()
            if "dubai" in t and "airport" in t:
                img_caption = "Dubai International Airport; the UAE's grace period lets stranded residents leave penalty-free by July 9"
            elif "dubai" in t:
                img_caption = "Dubai, UAE; Indians are the country's largest expatriate community, many caught by the spring flight shutdowns"
            else:
                img_caption = "Abu Dhabi's skyline; the UAE has opened a final 30-day visa grace period running to July 9, 2026"
            break

    if not img_url:
        px = fetch_pexels_image("Dubai skyline UAE city")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A UAE city skyline"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-mobility",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Federal Authority for Identity, Citizenship, Customs and Ports Security (ICP), UAE \u2014 announcement of final 30-day grace period (June 10 \u2013 July 9, 2026)",
            "Madhyamam Online \u2014 UAE grants final 30-day visa grace period after flight disruption exemptions (June 20, 2026)",
            "Ainvest \u2014 Indian Passport, Visa Services in UAE to Pause for 5 Days from June 26 (Embassy of India, Abu Dhabi)",
            "Institute for Defence Studies and Analyses (IDSA) \u2014 Indian Expatriates and Labour Reforms in GCC Countries (UAE Indian diaspora figures)"
        ]),
        "diaspora_angle": "Indians are the UAE's largest expatriate community \u2014 over 3.5 million people \u2014 and many were left with lapsed or cancelled visas when regional airspace closed this spring; the ICP's final 30-day grace period to July 9, 2026 gives them a penalty-free path to either fix their status or leave, with a five-day consular service blackout (June 26\u201330) complicating the timeline.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Fed's Warsh era opens hawkish ───────────────────────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Fed's Warsh era opens hawkish")
    print("="*60)

    slug = "fed-warsh-first-meeting-hawkish-dot-plot-rate-hike-2026-dollar-rupee-nri-deposits-20260620"
    headline = "The Fed Just Hinted Its Next Move Is Up, Not Down. For NRIs, That Quietly Rewrites the Math on the Rupee and Their Dollar Savings."
    subheadline = "In Kevin Warsh's debut meeting the Federal Reserve held rates but flipped its dot plot toward a 2026 hike \u2014 firming the dollar, pressuring the rupee, and reshaping the calculus for diaspora investors weighing US yields against India's newly sweetened NRI deposit rates."

    body = """The Federal Reserve did the expected thing on June 17 and the unexpected thing in the same breath. It left its benchmark interest rate untouched at 3.50 to 3.75 percent \u2014 a fourth straight pause \u2014 but the projections released alongside the decision told a far more hawkish story than markets had braced for. For the millions of Indians abroad who hold dollars, send money home, or invest across both economies, the message under new Chair Kevin Warsh's first meeting matters well beyond Washington.

## The Dot Plot Flipped

The headline was buried in the numbers. The Fed's "dot plot" \u2014 the chart mapping where each policymaker expects rates to go \u2014 flipped from pointing toward a cut, as it did in March, to pointing toward a hike. Nine of the policymakers now foresee at least one quarter-point increase before the end of 2026, with six expecting two or more. Another nine expect no move or a cut, leaving the committee sharply divided. Seventeen of eighteen officials judged the risks to inflation to be tilted to the upside.

The vote to hold was unanimous, 12-0, in Warsh's first gathering as chair. But the unity on the pause masked a real split on direction \u2014 the defining tension of the day. Inflation, the committee noted, remains above its 2 percent target, pushed up in part by higher energy prices linked to the Middle East conflict.

## A New Voice at the Fed

Warsh wasted no time stamping his style on the institution. The post-meeting statement was stripped down to a spare, declarative format reminiscent of the Greenspan era, and it removed forward guidance about future moves altogether. "I can't give you any forward guidance about what we're going to do next," Warsh told reporters, adding pointedly, "The good news is we'll be meeting in six weeks." He also launched a sweep of task forces to review the Fed's communications, balance sheet, data use and inflation framework \u2014 a signal that more change is coming.

Appointed by President Donald Trump with an expectation that he would deliver the rate cuts the president has demanded, Warsh instead opened his tenure by nailing his credibility to taming inflation. The committee's blunt closing line carried no hedge and no timeline: "The Committee will deliver price stability."

## The Dollar Firms, the Rupee Feels It

For the diaspora, the transmission runs through the currency. A Fed signalling higher-for-longer rates strengthens the dollar, tightens global financial conditions, and pressures emerging-market currencies \u2014 the rupee among them. The Indian currency has only recently clawed back from the brink of 97 to the dollar, helped by a plunge in oil prices, and a more hawkish Fed is exactly the kind of headwind that can stall a fragile recovery.

Indian analysts were quick to add a crucial caveat: the Reserve Bank of India is expected to set its own course, guided mainly by domestic data rather than Washington's mood. India's inflation has been benign and its growth solid, so the RBI is not obliged to follow the Fed step for step. But a strong dollar still raises the cost of India's imports, complicates the RBI's defence of the rupee, and can nudge foreign portfolio money out of Indian equities and bonds.

## Why It Matters for the Diaspora

This is where the abstract turns personal. For an NRI sitting on dollar savings, a Fed that keeps rates elevated \u2014 or raises them \u2014 means US deposits and money-market funds keep paying handsomely, a reason to think twice before rushing money into rupee assets. Yet the timing is striking: the RBI has just removed the caps on what Indian banks can offer non-resident depositors, and NRI deposit rates have already jumped toward 7 percent as banks compete for diaspora dollars.

So the diaspora investor faces a genuine fork. A higher-for-longer dollar makes holding savings in the US more rewarding and can erode the value of remittances once converted to rupees. But a weaker rupee also stretches every dollar sent home further, and India's banks are dangling some of their most attractive NRI rates in years. The Fed's hawkish turn does not settle that calculation \u2014 it sharpens it. With Warsh promising no signposts and the next meeting only six weeks away, the one certainty for globally spread Indian households is that the easy-money assumptions of early 2026 are gone, and every cross-border money decision now deserves a second look."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "Federal Reserve Chair Kevin Warsh; his debut meeting flipped the Fed's dot plot toward a 2026 rate hike"
    img_attribution = "Wikimedia Commons"

    # Person-first: Kevin Warsh
    wiki = fetch_wikipedia_person_image("Kevin Warsh")
    if wiki:
        img_url = wiki
        img_caption = "Federal Reserve Chair Kevin Warsh, whose first meeting signalled rates could rise in 2026"

    if not img_url:
        for q in ["Kevin Warsh", "Federal Reserve building Washington", "Marriner Eccles Federal Reserve", "United States Federal Reserve"]:
            commons = fetch_wikimedia_commons_images(q)
            if commons:
                img_url = commons[0]["url"]
                t = commons[0]["title"].lower()
                if "warsh" in t:
                    img_caption = "Federal Reserve Chair Kevin Warsh, whose first meeting signalled rates could rise in 2026"
                else:
                    img_caption = "The U.S. Federal Reserve; its hawkish June turn firms the dollar and pressures the rupee"
                    img_caption = "The U.S. Federal Reserve in Washington; its hawkish June turn firms the dollar and pressures the rupee"
                break

    if not img_url:
        px = fetch_pexels_image("US dollar currency finance")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "U.S. dollars and global currency"

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
            "U.S. Federal Reserve \u2014 FOMC statement and Summary of Economic Projections, June 17, 2026",
            "Reuters / Devdiscourse \u2014 Fed begins Warsh era by keeping rates on hold, sees one hike later this year (June 17, 2026)",
            "Outlook Business \u2014 US Fed Decision Explained: How Kevin Warsh's First Move Will Impact India",
            "The Hindu BusinessLine \u2014 Federal Reserve holds rates steady as officials split over future hikes amid rising inflation",
            "StockTitan \u2014 Fed Holds Rates June 2026; Dot Plot Flips to a Hike"
        ]),
        "diaspora_angle": "The Fed's hawkish turn under new Chair Kevin Warsh \u2014 a dot plot now pointing to a 2026 hike \u2014 strengthens the dollar and pressures the rupee, reshaping the trade-off NRIs face between elevated US yields and India's newly uncapped NRI deposit rates near 7 percent, and affecting the rupee value of every remittance sent home.",
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
