#!/usr/bin/env python3
"""
Videshi News Writer — June 22, 2026 (14:30 UTC run)
2 NEW articles:
  1. Operation Sindhu: India evacuates 1,713+ nationals from Iran amid Israel war (news / diaspora-safety)
  2. India quietly overhauls its visa system: 10-year extensions, consolidated categories, cheaper interns (news / immigration)
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
                if ii.get("width", 0) < 600:
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




# ─── Article 1: Operation Sindhu evacuation ──────────────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Operation Sindhu — 1,713+ evacuated from Iran")
    print("="*60)

    slug = "operation-sindhu-india-evacuates-indians-iran-israel-war-mashhad-armenia-students-diaspora-20260622"
    headline = "India Has Flown 1,700 of Its Own Out of a War Zone. The Planes Are Still Going Back for More."
    subheadline = "Under Operation Sindhu, special flights from Mashhad, Yerevan and Ashgabat have brought home more than 1,700 Indians from Iran, with hundreds more from Israel routed through Jordan. For families of students and workers caught in the Iran-Israel war, each landing is a name crossed off a list."

    body = """The eighth flight came in just before midnight. At 2330 hours on Sunday, a special aircraft from the Iranian city of Mashhad touched down at Delhi airport carrying 285 Indian nationals, and a junior foreign minister was on the tarmac to receive them. With that batch — people from Bihar, Jammu and Kashmir, Delhi, Uttar Pradesh, Rajasthan, Gujarat and Maharashtra — the number of Indians brought home from Iran under Operation Sindhu crossed 1,700. By Monday, officials said three more flights were scheduled over the next two to three days, and that 162 Indians who had crossed from Israel into Jordan would be repatriated within a day or two.

Operation Sindhu is the Indian government's emergency answer to the war between Iran and Israel, an evacuation mission that began on June 18 as Israeli airstrikes on Iranian cities turned a region full of Indian students, workers, pilgrims and fishermen into a place they urgently needed to leave. The first flight out carried 110 Indian students from Yerevan, the capital of Armenia, most of them from Jammu and Kashmir who had been studying at Iranian universities; officials said some had narrowly escaped harm when a dormitory was hit by missile fire. They had been moved overland from Iran into Armenia before being flown to Delhi — a pattern that has defined the operation ever since.

The geography of the rescue tells its own story. With Iranian airspace largely closed, India's missions in Tehran, Yerevan and Ashgabat first coordinated to move people across land borders into Armenia and Turkmenistan, from where they could be flown out. The breakthrough came on June 20, when Iran agreed to open its airspace for Indian evacuation flights at New Delhi's request, allowing the bulk of the operation to run through Mashhad in the country's northeast. "We thank the Government of Iran for this gesture," the Ministry of External Affairs said, a rare public note of gratitude to Tehran in the middle of a shooting war.

The scale has grown by the day. From a third flight that lifted the total past 500 on June 21, to the batch of 285 that crossed 1,700 on June 22, the count has climbed steadily as the foreign ministry has chartered civilian aircraft and, where needed, leaned on the Indian Air Force's heavy-lift C-17s. Each arrival has been turned into a small ceremony of reassurance, with ministers receiving evacuees and the MEA posting tallies on social media — a deliberate signal to anxious families back home that the state is counting, and coming for, every one of its citizens.

For the diaspora, Operation Sindhu lands on a deeply familiar nerve. India has built, over the past three decades, a distinct national reflex for pulling its people out of harm's way abroad: from the airlift of more than 170,000 from Kuwait during the 1990 Gulf crisis — still cited in the Guinness records as the largest civilian evacuation in history — to Operation Ganga from Ukraine in 2022 and Operation Kaveri from Sudan in 2023. A diaspora of some 32 million people, many of them living and working in the volatile arc from the Gulf to the Levant, has come to treat these operations as a quiet contract: go abroad to study and earn, and if the ground gives way, the planes will come. The names of those operations have become part of how Indians abroad measure what their passport is worth.

The students at the centre of this one make the stakes vivid. Thousands of young Indians, a large share of them from Jammu and Kashmir, study medicine and other subjects at Iranian universities, drawn by lower fees than private colleges at home. When the war reached their campuses, it was their parents — in Srinagar, in small towns across the north — who flooded helplines and local representatives with calls. Jammu and Kashmir's chief minister, Omar Abdullah, publicly tracked the movement of students out through Armenia, a reminder that for many families this was not foreign news but a direct line to a child in a dormitory near the fighting.

The operation is not finished, and the danger has not fully passed. Indian missions in Israel have continued to issue advisories to the tens of thousands of Indians there — caregivers, construction and farm workers, students — even as the heaviest evacuation effort has focused on Iran. Flights from Jordan, Egypt's Sharm el-Sheikh and other waypoints are folding Israel-based nationals into the same pipeline. For now, the message from each late-night landing at Delhi airport is the one the diaspora most wants to hear: the list is getting shorter, and the next flight is already in the air."""

    img_url = None
    img_caption = ""
    img_attribution = ""

    for q in ["Indira Gandhi International Airport Delhi", "evacuation aircraft India", "Indian Air Force C-17 Globemaster", "Air India aircraft New Delhi airport"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            img_caption = "Special flights under Operation Sindhu have brought more than 1,700 Indian nationals home from Iran through Delhi airport"
            img_attribution = "Wikimedia Commons"
            break

    if not img_url:
        pex = fetch_pexels_image("airport arrivals aircraft")
        if pex:
            img_url = pex
            img_caption = "Evacuees under Operation Sindhu have landed at Delhi airport on charter and military flights"
            img_attribution = "Pexels"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-safety",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Livemint / ANI — 'Operation Sindhu: India to operate 3 more evacuation flights as 1,713 nationals return from Iran' (June 22, 2026): MoS for External Affairs Pabitra Margherita said three more flights scheduled over the next 2-3 days; latest batch of 285 Indians arrived in New Delhi from Mashhad at 2330 hrs on June 22 (the eighth batch), taking the total brought home from Iran to 1,713; evacuees from Bihar, J&K, Delhi, UP, Rajasthan, Gujarat and Maharashtra; 162 Indians who crossed from Israel into Jordan to be repatriated within a day or two",
            "RNA Media — 'Operation Sindhu Expands: Over 1,000 Indians Evacuated As Iran-Israel Conflict Continues': operation launched after Israeli airstrikes on Iranian cities; first flight brought 110 Indian students from Yerevan, Armenia on June 18, coordinated by Indian Embassy in Tehran and Indian Mission in Armenia; most students from J&K studying at Iranian universities, some narrowly escaped when a dormitory was hit by Israeli missile fire; second phase included three charter flights (~1,000) plus a flight from Ashgabat, Turkmenistan carrying Indians who crossed overland",
            "The Daily Jagran / MEA spokesperson Randhir Jaiswal — 'Operation Sindhu: Third Flight Lands In Delhi, 517 Indians Evacuated From Iran So Far': special evacuation flight from Ashgabat, Turkmenistan landed in New Delhi at 0300 hrs June 21 taking the total to 517; earlier Friday-night flight from Iran carried 290 Indians including students and pilgrims; Iran granted a special exception to India for evacuation despite closed airspace; J&K CM Omar Abdullah tracked students leaving Iran via land routes to Armenia",
            "Ministry of External Affairs (via ANI/Times Now) — Operation Sindhu background: India coordinated evacuation through missions in Tehran, Yerevan and Ashgabat using land border crossings to Armenia and Turkmenistan; Iran opened its airspace for Indian evacuation flights on June 20 at India's request, allowing flights through Mashhad; India's evacuation tradition includes the 1990 Kuwait airlift of ~170,000 (largest civilian evacuation, Guinness records), Operation Ganga (Ukraine, 2022) and Operation Kaveri (Sudan, 2023)"
        ]),
        "diaspora_angle": "An estimated 32 million Indians live abroad, many in the volatile arc from the Gulf to the Levant; Operation Sindhu reaffirms the unwritten contract behind every Indian passport — that when a war zone closes in on students, workers and pilgrims overseas, New Delhi will send the planes to bring them home.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: India's visa system overhaul ─────────────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: India overhauls visa system — 10-year extensions")
    print("="*60)

    slug = "india-visa-overhaul-2026-ten-year-extensions-consolidated-categories-intern-salary-e-visa-oci-diaspora-20260622"
    headline = "India Just Rewrote the Rulebook for Foreigners Who Want to Stay. The Diaspora's Spouses and Kids Are the Quiet Winners."
    subheadline = "In a wave of changes flowing from its new immigration law, India has stretched employment and business visa extensions to ten years, folded a tangle of visa types into cleaner categories, added e-visa options and slashed the salary bar for interns. For OCI families and foreign-passport relatives, the paperwork of belonging just got lighter."

    body = """India is quietly rebuilding the machinery that decides who gets to live, work and study within its borders — and for the millions of diaspora families whose lives straddle two passports, the changes are more consequential than the lack of headlines suggests. Flowing from the Immigration and Foreigners Act that took effect this year, a series of orders and portal updates from the Ministry of Home Affairs has stretched visa extensions to a decade, consolidated a confusing thicket of visa types, expanded electronic visas and sharply lowered the salary threshold for hiring foreign interns. Taken together, they mark the most substantial reworking of India's visa system in years.

The single biggest change is one of duration. Foreign nationals in India on employment and business visas can now extend their stay for up to ten years at a time, double the previous five-year ceiling. For the practical purposes of a diaspora family, that means an executive of Indian origin on a foreign passport, or a returning professional running a business in Bengaluru or Gurugram, no longer has to return to their home country to apply afresh after five years. The renewal can be done from within India, removing a recurring disruption that has long forced people to plan international trips around the expiry of a stamp in their passport.

The second shift is one of order. India has folded several stand-alone visa types into broader parent categories: the Project visa, used by foreigners working in the power and steel sectors, is now a sub-category of the Employment visa, while the Intern and Research visas have become sub-categories of the Student visa. The government has also rolled out a system of sub-categories across nearly every visa type — Tourist, Business, Employment, Conference, Journalist, Medical and more — requiring applicants to specify the precise purpose of their visit. The stated aim is to simplify the system and let the state track foreigners more accurately by why they are in the country, though immigration advisers caution that document requirements and processing times are, for now, unchanged.

Some of the most diaspora-friendly tweaks are in the fine print. Two new electronic visa sub-categories — e-Conference and e-Medical Attendant — have been added to the existing e-Business, e-Medical and e-Tourist options. That matters for families who fly an elderly parent's foreign-passport-holding relative to India for treatment, or for diaspora professionals attending government-backed conferences: where they once had to queue at an Indian embassy or consulate, they can now apply online and expect faster processing. And the minimum salary required to bring a foreign national into India as an intern has been cut by more than half, to 360,000 rupees a year from 780,000 — a change aimed at making it easier for Indian companies, including diaspora-founded startups, to bring in young foreign talent.

Running underneath all of this is the immigration law that frames it — and not all of it is permissive. The Immigration and Foreigners Act, which replaced a patchwork of colonial-era statutes, places the burden of proving Indian citizenship on anyone identified as an "illegal migrant," empowers police to arrest without a warrant on reasonable suspicion of entering without valid documents, and mandates biometric collection from foreigners. It also requires hospitals, universities and even lodging providers to report the arrival of foreign nationals to the Foreigners Regional Registration Office — a compliance burden that, for OCI cardholders and long-staying foreign-passport relatives, translates into more touchpoints with the bureaucracy, not fewer.

That is the tension the diaspora now has to navigate. The same season that brought ten-year extensions and online medical-attendant visas also brought a fully digitised, tightly tracked OCI regime, sharper FRRO reporting rules, and a redrawn map of "protected areas" that foreigners cannot freely enter. For Indian-origin families, the message is mixed but clear: the doors to staying longer have widened, and the routine paperwork of doing so has eased, but the state's ability to see exactly who is inside the country, and on what terms, has grown at the same time.

For now, the people most likely to feel the benefit first are the ones whose lives already span borders — the foreign-passport-holding spouses and children of OCI cardholders, the returning professionals, the startup founders who want to hire across nationalities. India has spent the past decade courting its diaspora with the language of belonging. These changes are the unglamorous follow-through: not speeches about the motherland, but the quiet, cumulative easing of how long you can stay and how much paperwork it takes to do it. The guidelines that will settle the remaining ambiguities are expected in phases — and the diaspora, as ever, will read the fine print carefully."""

    img_url = None
    img_caption = ""
    img_attribution = ""

    for q in ["Indian passport visa", "Ministry of Home Affairs India building", "Indian visa stamp passport", "passport immigration India"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            img_caption = "India has stretched employment and business visa extensions to ten years as part of a wide overhaul of its visa system"
            img_attribution = "Wikimedia Commons"
            break

    if not img_url:
        pex = fetch_pexels_image("passport visa documents")
        if pex:
            img_url = pex
            img_caption = "India's visa overhaul consolidates categories and adds new e-visa options for foreign nationals"
            img_attribution = "Pexels"

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
            "Fragomen — 'New Streamlined Visa Categories Implemented' (June 2026): India's Ministry of Home Affairs has streamlined and consolidated visa categories on the Indian visa application portal; the Project visa (power and steel sector) is now a sub-category under Employment visa; Intern and Research visas have become sub-categories of the Student visa; MHA guidelines on the streamlined categories expected in the near future",
            "Fragomen — 'Immigration Policies Further Relaxed' (June 2026): two new electronic visa sub-categories added (e-Conference and e-Medical Attendant), expanding from the prior three (e-Business, e-Medical, e-Tourist); employment and business visa holders can now extend visas for up to 10 years (previously up to 5), no longer required to leave India to apply for a new visa after five years; minimum salary threshold for interns reduced by over 50% to INR 360,000 from INR 780,000 per year; further changes expected in phases",
            "Fragomen — 'Visa Sub-Categories Introduced': MHA introduced sub-categories for Tourist, Business, Employment, Project, Intern, Student, Research, Conference, Missionary, Journalist, Entry, Diplomatic, Official, UN Diplomat and UN Official visas; foreign nationals must select a specific purpose of travel on the online application; document requirements and processing times unchanged",
            "SCC Times — 'Immigration & Foreigners Amendment Order 2026: Explained' (notified June 18, 2026) and Wikipedia 'Immigration and Foreigners Act, 2025': the Act introduces definitional clarity, relaxes certain permit conditions and revises the list of protected areas with implications for foreign nationals, OCI cardholders and tourism; the law places the onus of proving citizenship on anyone identified as an 'illegal migrant', empowers police (head constable and above) to arrest without warrant on reasonable suspicion, mandates biometric collection, and requires hospitals, educational institutions and lodging providers to report arrivals of foreigners to the FRRO"
        ]),
        "diaspora_angle": "From foreign-passport spouses and children of OCI cardholders to returning professionals and diaspora-founded startups hiring abroad, the people whose lives span two countries are the first to feel India's quieter immigration reforms — longer stays and lighter paperwork, set against a more tightly tracked system.",
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
