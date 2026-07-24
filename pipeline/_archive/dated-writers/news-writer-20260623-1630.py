#!/usr/bin/env python3
"""
Videshi News Writer — June 23, 2026 (16:30 UTC run)
2 NEW articles, both fresh & distinct from prior runs (which covered SpaceX,
NEET re-exam, Iran sanctions/oil, foreign-investor return, USTR Delhi trade,
China normalisation, PMI, RBI NRI deposits, Jio/NSE IPO, Russian crude, H-1B
$100k fee, student-visa duration, citizenship fee, CUET results, FCRA rules,
July Visa Bulletin EB-2 unavailable, $750 expedited interview pilot):
  1. The "perfect storm" driving Indian students away from the big-four study
     destinations: rupee crash + visa crackdowns + bleak job markets, with the
     September intake already shrinking and Europe rising as the alternative.
     (education — diaspora study-abroad / family-finance angle)
  2. Anil Menon, the Indian- and Ukrainian-American physician-astronaut, set to
     launch July 14 aboard Soyuz MS-29 for an eight-month ISS stay — a rare
     diaspora milestone in human spaceflight. (space — diaspora-achievement angle)
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


# \u2500\u2500\u2500 Article 1: Indian students rethink studying abroad \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Indian students rethink studying abroad")
    print("="*60)

    slug = "indian-students-rethink-studying-abroad-rupee-crash-visa-crackdown-perfect-storm-20260623"
    headline = "The Dream Degree Abroad Is Getting Too Expensive and Too Risky. Indian Families Are Doing the Math."
    subheadline = "A rupee that has lost more than a tenth of its value in a year, visa crackdowns from Washington to Ottawa, and a job market that no longer pays off the loan \u2014 the calculus that sent a generation of Indians to the West is breaking down, and the September intake is already shrinking."

    body = """For two decades the path was almost a reflex for India's aspiring middle class: borrow heavily, fly West, earn a degree in the United States, Britain, Canada or Australia, find a job, and let the foreign salary repay the loan many times over. That equation is now coming apart, and the people who make a living arranging these journeys say the change is structural, not a passing dip.

"The market is clearly showing signs of slowing down. We've already seen enrolments to the UK and US fall by 20% over the last two years, and I expect another 10-15% decline from those levels going forward," Sushil Sukhwani, founder of Edwise International, which sends thousands of Indian students abroad each year, told the BBC. More than 1.2 million Indian students were enrolled in higher education abroad in 2025, with India having long ago overtaken China as the world's leading source of international students \u2014 which is exactly why a slowdown of this size ripples so far.

## A Perfect Storm

Three forces are converging at once. The first is the rupee. The currency has fallen more than 10% against the US dollar in the past year alone, and by Sukhwani's reckoning has depreciated between 35% and 47% against the currencies of the major study destinations since 2019. For a family that budgeted a loan in rupees, that means the same degree now costs lakhs more than it did when the plan was hatched \u2014 and students already overseas are quietly refinancing loans and scrambling for extra funds to cover instalments they had thought were settled.

The second is the wall of visa restrictions going up across the English-speaking world. In the United States, Indian enrolment fell nearly 7% between February 2025 and February 2026, the sharpest drop in over a decade, against a backdrop of frozen interview slots, tighter scrutiny and proposals to shorten how long students can stay. In the United Kingdom, 76% of universities reported a decline in Indian enrolments for the January intake. Canada, once the friendliest of the four, has slashed study-permit numbers and pushed Indian refusal rates sharply higher.

The third is the broken promise at the end of the journey. The whole model rested on a well-paid job after graduation that would retire the debt. "They arrive hoping to secure skilled jobs in the fields they trained for and end up working in the gig economy. Earlier, that work helped fund their education. Now many are graduating and doing it full-time," said Sudhanshu Kaushik, founder of the North America Association of Indian Students in Washington. "The depreciating currency, the job market, the rise of AI, the visa issues and the current administration's policies have all combined to create a perfect storm. No one wins."

## Why the Diaspora Should Care

This is not an abstract policy story; it is a household-finance story for a vast slice of the diaspora's feeder class. The decision to send a child abroad is, for most Indian families, the single largest financial bet they will ever make \u2014 often secured against a home or a lifetime of savings. When the rupee falls and the post-graduation job disappears, that bet curdles into a debt trap, and the anxiety reaches into the diaspora itself: relatives in the US and UK are increasingly the co-signers, the emergency lenders and the safety net when a niece or nephew's loan repayments outrun their gig-economy earnings.

For NRI parents weighing where to send their own children, the shift reframes the question entirely. The aura of the American or British degree as a guaranteed ticket is fading, and the families doing the math are concluding that the risk-adjusted return no longer justifies the price. Demand for foreign education itself remains strong \u2014 the aspiration has not died \u2014 but it is being redirected.

## What's Next

The redirection is already visible in the map of where Indians are choosing to go. "Countries such as Germany, Ireland, Italy and several other European destinations are attracting increasing interest from Indian students because of lower tuition costs, favourable post-study work pathways, strong employment prospects and a more attractive overall value proposition," said Mayank Maheshwari of student-accommodation platform University Living. The Global Student Flows Report 2026 forecasts that Indian enrolments in the "big four" will decline by an average of 0.5% a year through 2030 \u2014 a slow bleed for nations that spent decades building higher education into one of their most profitable exports and most effective instruments of soft power. As Kaushik put it, the United States in particular "is retreating from the gains we made." For India's students, the era of the automatic Western degree is giving way to a colder, more careful arithmetic \u2014 one in which Rome, Dublin and Berlin increasingly beat Boston and London on the spreadsheet."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    # Topic imagery: university campus / international students / graduation. No single named person.
    img_url, ctitle = pick_commons([
        "international students university campus",
        "university graduation ceremony students",
        "King's College London university building",
        "university library students studying",
        "college campus students walking"
    ])
    img_caption = "International students on a university campus; a weak rupee and visa crackdowns are pushing Indian families to rethink studying abroad"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("university students campus graduation")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "University students on campus; rising costs and tighter visas are reshaping where Indians choose to study abroad"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "education",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "BBC News / Globlens (globlens.com, June 22, 2026) \u2014 'Currency crash and visa crackdowns force Indian students to rethink studying abroad': more than 1.2 million Indian students enrolled abroad in 2025; rupee down more than 10% against the US dollar in the past year and 35-47% against major study-destination currencies since 2019; Edwise International founder Sushil Sukhwani says UK and US enrolments fell 20% over two years with a further 10-15% decline expected; UK saw 76% of universities report declining Indian enrolment for the January intake; US Indian enrolment fell nearly 7% between February 2025 and February 2026; Sudhanshu Kaushik (North America Association of Indian Students) describes a 'perfect storm' of currency, jobs, AI, visas and policy; Mayank Maheshwari (University Living) cites Germany, Ireland and Italy as rising alternatives; Global Student Flows Report 2026 forecasts big-four Indian enrolment declining ~0.5% a year through 2030.",
            "Collegedunia (collegedunia.com) \u2014 'Indian Students in US Fall 6.9% to 3.52 Lakh': Indian student enrolment in US institutions fell 6.9% from 378,787 (February 2025) to 352,644 (February 2026), the sharpest year-on-year drop in over a decade, per India's Ministry of External Affairs reply in the Rajya Sabha on April 2, 2026, drawn from the US DHS SEVIS Mapping Tool; decline broad-based across school, vocational, undergraduate and postgraduate levels; India remains the largest source country but its lead over China has narrowed.",
            "Inside Higher Ed (insidehighered.com) \u2014 'How Colleges Hope to Approach International Higher Ed in 2026': new international enrolment at US colleges dipped 17% year-on-year this past fall; administration actions included revoked SEVIS records, travel bans, frozen visa interviews and proposed limits on length of stay and Optional Practical Training; students and families increasingly building backup plans in the UK, Australia and elsewhere."
        ]),
        "diaspora_angle": "Sending a child to study in the West is the biggest financial bet most Indian middle-class and NRI families make, so a falling rupee, visa crackdowns and a broken post-graduation job market turn that bet into a potential debt trap \u2014 and increasingly the diaspora's relatives abroad are the co-signers and safety net when the loans outrun gig-economy earnings.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: Anil Menon Soyuz MS-29 launch \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Anil Menon ISS launch")
    print("="*60)

    slug = "anil-menon-indian-american-astronaut-soyuz-ms29-iss-launch-july-2026-diaspora-20260623"
    headline = "A Doctor Who Built SpaceX's Medical Unit Is About to Become an Astronaut. His Roots Run to Kerala."
    subheadline = "Anil Menon \u2014 emergency physician, Space Force colonel and son of an Indian father and Ukrainian mother \u2014 launches July 14 aboard Soyuz MS-29 for an eight-month stay on the International Space Station, his first spaceflight and a rare diaspora milestone in human exploration."

    body = """In a little over three weeks, a 49-year-old emergency-room doctor from Minneapolis will strap into a Russian Soyuz capsule on the Kazakh steppe and ride a rocket into orbit. Anil Menon's path to that seat is one of the more improbable resumes in the astronaut corps \u2014 Harvard neurobiology, a Stanford medical degree and a master's in mechanical engineering, board certifications in emergency and aerospace medicine, a commission as a colonel in the United States Space Force, and a stint as SpaceX's very first flight surgeon \u2014 and on July 14, it culminates in his first journey beyond Earth.

Menon is assigned as a flight engineer on Expeditions 74/75, launching aboard the Roscosmos Soyuz MS-29 spacecraft alongside cosmonauts Pyotr Dubrov and Anna Kikina. After lifting off from the Baikonur Cosmodrome, the trio will spend roughly eight months \u2014 about 240 days \u2014 aboard the orbiting laboratory, with a return to Earth planned for spring 2027. During the mission he will run scientific investigations and technology demonstrations designed to prepare humans for deeper space missions and to feed discoveries back to medicine on the ground.

## From the Emergency Room to Orbit

Menon's career has been an unusual bridge between three worlds: medicine, the military and spaceflight. Born in 1976 to an Indian father and a Ukrainian mother, he trained as an emergency physician and still practises at Memorial Hermann's Texas Medical Center and mentors residents at the University of Texas even while preparing to leave the planet. Before NASA selected him for its 23rd astronaut class in 2021, he had already spent years as a NASA flight surgeon supporting station crews and training in Star City, Russia, to back up Soyuz missions.

It was at SpaceX, though, that Menon left a particular mark. As the company's first flight surgeon he helped launch the first crewed Dragon spacecraft on NASA's Demo-2 mission in 2020 and built the medical organisation that now supports the company's human spaceflights. He graduated with his astronaut class in 2024 and has been preparing for this assignment since.

## Why the Diaspora Should Care

For the Indian diaspora, astronauts who carry the community's heritage into orbit occupy a special place in the imagination \u2014 a lineage that runs from Rakesh Sharma to Kalpana Chawla to Sunita Williams, names that became shorthand for how far the community's children could reach. Menon adds a distinctly modern, hyphenated chapter to that story: an Indian-and-Ukrainian-American who reached space not through a single discipline but by stitching medicine, engineering and military service together, and who helped a private company open the era of commercial human spaceflight before flying himself.

His launch also lands in a season unusually rich for people of Indian origin in space. Group Captain Shubhanshu Shukla recently became the focus of attention for Indian in-orbit research, and the broader arc \u2014 NASA's diaspora astronauts, India's own Gaganyaan ambitions, and a generation of Indian-origin engineers across the world's space agencies and companies \u2014 makes Menon's flight feel less like an isolated achievement than part of a widening presence. For diaspora families, and especially for the children who see a doctor-engineer-soldier-astronaut and recognise a face that looks like their own, that visibility is the quiet, durable payoff.

## What's Next

The Soyuz MS-29 launch is targeted for Tuesday, July 14, from Baikonur, after which Menon joins the long-running rotation of crews keeping the International Space Station staffed and its experiments running. His eight-month expedition will stretch into the spring of 2027, and his medical background gives him an unusual dual role \u2014 both a subject of the human research that the station specialises in and one of its most qualified caretakers, watching over how the human body copes with months of weightlessness. For a man who has spent his career figuring out how to keep people alive in the most hostile environments imaginable, the ultimate test is now only a launch window away."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    # Named person \u2014 Wikipedia FIRST, then Commons.
    img_url = fetch_wikipedia_person_image("Anil Menon (astronaut)")
    img_caption = "NASA astronaut Anil Menon, who launches aboard Soyuz MS-29 on July 14, 2026 for his first spaceflight"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        img_url, ctitle = pick_commons([
            "Anil Menon astronaut portrait",
            "Anil Menon NASA",
            "Soyuz MS-29 crew",
            "International Space Station"
        ])

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "space",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "NASA (nasa.gov) \u2014 'NASA Astronaut Anil Menon to Discuss Upcoming Launch, Mission' (advisory updated April 23, 2026) and 'NASA Assigns Astronaut Anil Menon to First Space Station Mission': Soyuz MS-29 targeted to launch Tuesday, July 14, 2026, carrying Menon and Roscosmos cosmonauts Pyotr Dubrov and Anna Kikina to the ISS for an eight-month stay as part of Expeditions 74/75; Menon's first spaceflight; selected as a NASA astronaut in 2021, graduated with the 23rd astronaut class in 2024; born and raised in Minneapolis; emergency medicine physician, mechanical engineer and colonel in the US Space Force; bachelor's in neurobiology from Harvard, master's in mechanical engineering and medical degree from Stanford; served as SpaceX's first flight surgeon, helping launch the first crewed Dragon on NASA's Demo-2 mission in 2020.",
            "News Dive (newsdive.net, ~June 18, 2026) \u2014 'Indian-American Anil Menon Transitions from Medicine to Space': Menon, of Indian-American heritage, scheduled to launch July 14, 2026 aboard Soyuz MS-29 from Baikonur Cosmodrome with cosmonauts Pyotr Dubrov and Anna Kikina for an eight-month (~240 day) mission, returning spring 2027; son of Indian and Ukrainian immigrants; trained at Star City, Russia, as a Soyuz support flight surgeon; joined SpaceX as its first flight surgeon and helped create astronaut medical protocols and the Demo-2 mission.",
            "Outlook Business / Livemint \u2014 profiles of Anil Menon: US Air Force/Space Force colonel, emergency physician and former NASA flight surgeon, born in the US in 1976, set for first space mission in 2026 as Expedition 75 flight engineer; will conduct scientific research and technology demonstrations to advance human space exploration and benefit life on Earth."
        ]),
        "diaspora_angle": "Astronauts who carry Indian heritage into orbit \u2014 from Rakesh Sharma to Kalpana Chawla to Sunita Williams \u2014 hold a special place for the diaspora, and Anil Menon adds a modern, hyphenated chapter as an Indian-and-Ukrainian-American physician-astronaut whose July 14 launch gives diaspora children another face that looks like their own reaching space.",
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
