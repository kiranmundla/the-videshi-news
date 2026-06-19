#!/usr/bin/env python3
"""
Videshi News Writer — June 19, 2026 (18:30 UTC run)
2 NEW articles:
  1. India's Immigration & Foreigners (Amendment) Rules 2026 — FRRO registration tightened, new rules for foreign-citizen children of Indian parents (immigration / diaspora)
  2. India-Canada CEPA reset at G7 Evian — Modi & Carney target FTA by year-end, doubling trade (geopolitics / trade)
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


# ─── Article 1: Immigration & Foreigners (Amendment) Rules 2026 ──

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: India's 2026 immigration rules tighten registration")
    print("="*60)

    slug = "india-immigration-foreigners-amendment-rules-2026-frro-registration-oci-foreign-children-20260619"
    headline = "India Quietly Rewrote Its Foreigner Registration Rules. NRI Families With Foreign-Passport Kids Need to Read the Fine Print."
    subheadline = "The Immigration and Foreigners (Amendment) Rules, 2026 \u2014 in force since June 1 \u2014 scrap the old 14-day grace period for long-stay registration, allow late filing only in 'emergent circumstances,' and impose a new 30-day reporting duty on parents whose India-born child later takes a foreign citizenship."

    body = """India has changed the rules for foreigners who live in the country for extended periods \u2014 and for the diaspora families who move between two passports, the changes are more than a bureaucratic footnote. The Ministry of Home Affairs notified the Immigration and Foreigners (Amendment) Rules, 2026 through a gazette notification dated June 1, and they took effect immediately, reshaping how and when foreign nationals must register with the authorities and adding fresh reporting duties for the children of mixed-citizenship families.

The amendments sit on top of the Immigration and Foreigners Act, 2025 and its rules \u2014 the new statutory framework that replaced India's patchwork of decades-old foreigner laws. For Overseas Citizens of India, returning NRIs married to foreign nationals, and the growing number of diaspora families raising children across borders, the latest tweaks change the everyday paperwork of living in India.

## The 14-Day Grace Period Is Gone

The headline change is about timing. Under the earlier framework, a foreign national staying in India beyond 180 days had a 14-day window after that period expired to register with the Foreigners Registration Officer (FRO) or the Foreigners Regional Registration Office (FRRO). The amendment to Rule 12 erases that buffer. Registration must now be completed "any time before the expiry of the said period of one hundred and eighty days" \u2014 meaning the clock to register runs out on day 180, not two weeks after.

The rule applies to foreigners on visas that permit a maximum stay of 180 days who then intend to remain longer, as well as to those holding longer-validity visas that cap any single stay at 180 days. The shift from "within 14 days after" to "before the expiry of" is subtle on paper but consequential in practice: it removes the cushion that travellers and long-stay residents have long relied on, and it demands that families plan their registration well in advance rather than scrambling after the deadline.

## Late Filing Now Needs an "Emergent" Excuse

The rules also tighten the door on those who miss the deadline. Delayed registration beyond the prescribed period will be permitted only under exceptional circumstances \u2014 the notification inserts the condition that "such registration shall be granted only in emergent circumstances." Combined with the Immigration and Foreigners Act, 2025, which carries significantly stiffer penalties for overstaying and non-registration, including fines and potential imprisonment, the message is that the system has far less tolerance for paperwork that slips.

For a family that has historically treated registration as a formality to sort out on arrival, that is a meaningful change. Non-compliance can also complicate future Indian visa applications and clearance at departure \u2014 a quiet risk that compounds over years of back-and-forth travel.

## A New 30-Day Clock for Foreign-Citizen Children

The most diaspora-specific change concerns children. The amendment introduces an important exemption: where either parent is an Indian citizen and wishes to retain the Indian citizenship of a child born in India under Section 3 of the Citizenship Act, 1955, the parents no longer need to notify the FRO of the child's birth, as the earlier rules required. That removes a registration headache for thousands of families where one parent holds an Indian passport.

But the rules add a new obligation in return. If a child born in India later acquires the citizenship of a foreign country while continuing to reside in India, either parent must inform the Registration Officer within 30 days of that acquisition. For diaspora families who, say, raise a child in India and then secure US, Canadian, British or Australian citizenship for that child, this creates a reporting trigger that did not exist in the same form before \u2014 and a 30-day window that is easy to miss amid the paperwork of acquiring a second nationality.

## Why It Matters for the Diaspora

For NRIs, OCI holders and their spouses, these changes land squarely in everyday life. A foreign-national spouse spending several months a year in India to be near family, a returning NRI couple settling in for a long stretch, or a household navigating which child holds which passport \u2014 all now operate under a tighter, less forgiving registration regime. The loss of the 14-day grace period means deadlines must be tracked from the day of arrival, not after the fact, and the "emergent circumstances" standard for late filing leaves little room for honest delay.

The child-citizenship reporting rule deserves particular attention from globe-spanning families. The exemption is welcome news for India-citizen parents who want their India-born child to remain Indian. But the flip side \u2014 the 30-day notification when a resident child takes foreign citizenship \u2014 is a new compliance step that diaspora parents will need to build into their plans, alongside the separate and well-known restrictions on dual citizenship that India maintains.

None of this changes the fundamentals of OCI status or the right of overseas Indians to visit and stay. What it changes is the discipline the system now expects. For a diaspora that prides itself on keeping one foot in India, the practical takeaway is simple: check your dates, register before day 180, and if a child's nationality changes, start counting to 30. The rules are in force now, and the old cushions are gone."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "India's Ministry of Home Affairs oversees the new Immigration and Foreigners (Amendment) Rules, 2026"
    img_attribution = "Wikimedia Commons"

    for q in ["Indian passport document", "India immigration office airport", "Ministry of Home Affairs India building New Delhi", "Indian visa passport stamp"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            t = commons[0]["title"].lower()
            if "passport" in t:
                img_caption = "An Indian passport; new 2026 rules tighten registration timelines for long-staying foreign nationals"
            elif "immigration" in t or "airport" in t:
                img_caption = "An Indian immigration counter; the 2026 amendment scraps the 14-day grace period for FRRO registration"
            break

    if not img_url:
        px = fetch_pexels_image("passport immigration documents travel")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Passport and travel documents"

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
            "Ministry of Home Affairs \u2014 Immigration and Foreigners (Amendment) Rules, 2026 (Gazette notification dated June 1, 2026)",
            "Bar and Bench \u2014 India's 2026 Immigration Rules: Stricter registration and new reporting for children of foreign nationals",
            "IANS \u2014 Centre notifies Immigration and Foreigners (Amendment) rules; revamps process",
            "Lexology \u2014 FRRO Registration in India: Process, Requirements & Rules - Guidance for Foreign Nationals in 2026",
            "Ministry of External Affairs \u2014 Foreigners Registration guidelines"
        ]),
        "diaspora_angle": "India's new 2026 immigration rules scrap the 14-day registration grace period for long-staying foreigners and impose a 30-day reporting duty on parents whose India-born child later acquires foreign citizenship \u2014 changes that directly affect OCI holders, NRIs with foreign-national spouses, and diaspora families raising children across two passports.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: India-Canada CEPA reset at G7 Evian ─────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: India-Canada CEPA reset, FTA target by year-end")
    print("="*60)

    slug = "india-canada-cepa-trade-deal-modi-carney-g7-evian-year-end-target-diaspora-20260619"
    headline = "India and Canada Want a Trade Deal Signed This Year. For Three Million Indians in Canada, the Reset Is Personal."
    subheadline = "Meeting on the sidelines of the G7 in Evian \u2014 their fourth in under a year \u2014 Narendra Modi and Mark Carney pledged to conclude a long-stalled Comprehensive Economic Partnership Agreement by the G20, aiming to double bilateral trade to $50 billion and explicitly leaning on the diaspora as the bridge between the two countries."

    body = """Two years ago, India and Canada were barely on speaking terms. This week, their leaders set a deadline to sign a free trade deal. The turnaround \u2014 from a diplomatic rupture to a fast-tracked economic partnership \u2014 was on full display when Prime Minister Narendra Modi and Canadian Prime Minister Mark Carney met on the sidelines of the G7 Summit in Evian, France, and committed to closing a Comprehensive Economic Partnership Agreement (CEPA) before the year is out.

It was their fourth meeting in less than a year, a cadence that itself tells the story of how quickly the relationship has been rebuilt. "In less than a year, it is our fourth meeting, indicating our commitment to strong India-Canada ties," Modi posted after the talks, noting the ground covered since the two last met. Carney, for his part, was effusive: "Four continents, four meetings, one year... you've set a high bar for the relationship and what we can do together."

## A Deadline, and a Number

Both leaders attached hard targets to the warmth. "His Excellency likes a deadline. I like one as well. And our deadline is to complete by the G20," Carney said, referring to the goal of concluding CEPA negotiations by the time of the next G20 summit. The shared ambition is to double bilateral trade by the end of the decade \u2014 a target India and Canada have framed as reaching roughly $50 billion by 2030, up from about $8.66 billion in two-way merchandise trade in FY 2024-25.

The negotiations cover trade in goods and services, and both sides have signalled they want to go well beyond tariffs. Carney said the teams were exploring opportunities in "energy, agri-food, tech, and education," while a joint framework from earlier this year flagged cooperation in critical minerals, clean technology, digital innovation, civil nuclear energy \u2014 including a multi-billion-dollar uranium supply arrangement \u2014 and, crucially for the diaspora, talent mobility.

## From Rupture to Reset

The speed of the thaw is striking given where the relationship stood. Canada paused trade negotiations in 2023 after relations collapsed over Ottawa's allegation of Indian involvement in the killing of a Canadian Sikh separatist \u2014 a charge New Delhi flatly denied. Diplomats were expelled, high commissions were hollowed out, and the trade file went cold for nearly two years.

Carney's arrival in office reset the tone. He has framed deeper ties with India as central to his strategy of diversifying Canadian trade away from over-dependence on the United States, calling a deal with India a "game changer for Canadian workers and businesses." His government relaunched CEPA talks during a visit to New Delhi earlier in the year, and the Evian meeting added political momentum and a clear deadline to the technical work already under way.

## The Diaspora as the Bridge

What sets the India-Canada relationship apart is how openly both governments invoke the people who connect the two countries. At Evian, Modi thanked Carney directly "for your concern about the Indian diaspora," and the leaders' warmth was framed repeatedly around the human ties \u2014 students, families and businesses \u2014 that span the two nations. With roughly three million people of Indian origin in Canada, the diaspora is not a backdrop to this relationship; it is a central pillar of it.

That matters because the people-to-people channel was exactly what suffered most during the freeze. Indian students \u2014 long the largest international cohort on Canadian campuses \u2014 faced uncertainty, visa processing slowed, and families with members on both sides of the ocean felt the chill directly. A concluded CEPA that explicitly addresses talent mobility, university exchanges and professional services could restore and expand the very pathways that the diaspora depends on.

## Why It Matters for the Diaspora

For the Indian community in Canada \u2014 and for the families in India tied to them \u2014 a trade deal is not an abstraction. Talent-mobility provisions could ease the movement of skilled professionals and smooth the path for students; expanded services trade could open opportunities for the IT and consulting workers who form a large share of the diaspora's professional class. Energy, critical minerals and clean-tech cooperation point to longer-term investment that creates jobs in the regions where Indian-Canadians live and work.

There are caveats. The G20 deadline is ambitious, and trade negotiations have a habit of slipping; the underlying political relationship, while warmer, was fragile enough two years ago to freeze entirely. But the direction of travel is unmistakable. After a bruising chapter that left many in the diaspora caught between two governments, the message from Evian was that the two countries now see their three-million-strong human bridge as an asset to build on \u2014 and they have put a date on the calendar to prove it."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "Prime Minister Narendra Modi; India and Canada pledged to conclude a trade deal by the G20"
    img_attribution = "Wikimedia Commons"

    # Try a Modi+Carney joint Commons photo first, then fall back to Modi Wikipedia portrait
    for q in ["Narendra Modi Mark Carney", "Narendra Modi G7 2026", "Mark Carney Narendra Modi meeting"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            img_caption = "Prime Minister Narendra Modi and Canadian PM Mark Carney; the two leaders met on the sidelines of the G7 in Evian"
            break

    if not img_url:
        wiki = fetch_wikipedia_person_image("Narendra Modi")
        if wiki:
            img_url = wiki
            img_caption = "Indian Prime Minister Narendra Modi, who set a G20 deadline to conclude the India-Canada trade deal"

    if not img_url:
        wiki = fetch_wikipedia_person_image("Mark Carney")
        if wiki:
            img_url = wiki
            img_caption = "Canadian Prime Minister Mark Carney, who has framed an India trade deal as a 'game changer'"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "IANS \u2014 'Four continents, four meetings, one year': Canadian PM lauds growing ties with India in meeting with PM Modi (Evian, June 16, 2026)",
            "Inshorts \u2014 'Grateful for your concern about Indian diaspora': PM Modi to Canadian PM",
            "LiveMint \u2014 India, Canada push to conclude trade pact this year, deepen strategic ties",
            "Reuters \u2014 Canada, India agree to restart trade talks, says Indian government",
            "Ainvest \u2014 India and Canada Agree to Conclude Free Trade Pact Talks by Year-End"
        ]),
        "diaspora_angle": "India and Canada set a G20 deadline to conclude a long-stalled trade deal and double bilateral trade to $50 billion \u2014 a reset that directly affects the roughly three million people of Indian origin in Canada through talent-mobility, student-exchange and services provisions, after a two-year freeze that hit the diaspora's people-to-people ties hardest.",
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
