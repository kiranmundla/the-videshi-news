#!/usr/bin/env python3
"""
Videshi News Writer — June 20, 2026 (18:30 UTC run)
2 NEW articles:
  1. DOJ denaturalization push ramps up; Indian-origin naturalized citizens in the crosshairs (immigration / diaspora-safety)
  2. Anil Menon, Indian-American NASA astronaut, set for first ISS mission aboard Soyuz MS-29 on July 14 (diaspora / space)
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


# ─── Article 1: DOJ denaturalization push & Indian diaspora ──────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: DOJ denaturalization push & Indian diaspora")
    print("="*60)

    slug = "doj-denaturalization-push-indian-american-citizens-trump-second-term-naturalized-20260620"
    headline = "Citizenship Was Supposed to Be the Finish Line. The Justice Department Is Quietly Reopening Old Files."
    subheadline = "A ramped-up federal denaturalization effort \u2014 a dedicated DOJ unit, a June memo listing ten priority categories, and a fresh batch of cases including the first in Oregon this term \u2014 is unsettling naturalized Indian-Americans who assumed the oath was the end of the immigration road, not a document the government could revisit."

    body = """For most of the roughly two million naturalized Indian-Americans, the day they raised their right hand and took the oath of citizenship felt like a finish line \u2014 the irreversible end of a years-long, often decades-long immigration journey. A new and intensifying federal effort is testing that assumption. The Department of Justice is ramping up denaturalization, the legal process of stripping citizenship from naturalized Americans, and the scale of the push marks a sharp break from how rarely the tool has been used in modern history.

The numbers tell the story. According to a CNN report this week, the DOJ has stood up a dedicated denaturalization unit staffed by roughly a dozen attorneys and expects to file "several hundred more" cases. For context, the Biden administration filed only about two dozen denaturalization cases across four years, and historically the government averaged around eleven a year between 1990 and 2017. A shift from single digits to hundreds is not a tweak; it is a different posture entirely.

## What Is Actually Happening

Denaturalization is not new \u2014 it has long existed to revoke citizenship obtained through fraud or willful misrepresentation, such as concealing a criminal past or lying on an application. What has changed is the appetite to use it, and the breadth of the net.

A June 2025 memo by Assistant Attorney General Brett Shumate, head of the DOJ's Civil Division, directed prosecutors to "prioritize and maximally pursue" denaturalization and laid out ten broad categories of cases to target \u2014 ranging from those who pose national-security concerns to those who allegedly committed fraud against government programs. Critics note the list is expansive enough to sweep in a wide range of naturalized citizens, and that civil denaturalization cases carry fewer protections than criminal ones: there is no guaranteed right to an attorney, and the government's burden of proof is lower.

The cases are already moving. In early June, the DOJ publicly identified a batch of individuals being targeted nationwide, following an earlier group flagged in May. And on June 15, federal prosecutors in Oregon filed to revoke the citizenship of Jaswinder Singh, a 54-year-old man of Indian origin, accused of obtaining naturalization under a dual identity \u2014 the first denaturalization case brought in the state during the current term.

## Why Indian-Americans Are Paying Attention

Indian-Americans are among the largest and fastest-growing naturalized populations in the United States, with tens of thousands taking the oath every year. That prominence cuts both ways. It means a community deeply invested in the permanence of citizenship, and a community statistically likely to appear in any large-scale review of naturalization files.

Immigration attorneys serving the diaspora report a sharp rise in anxious queries: green-card holders asking whether it is now safer to delay naturalizing, and citizens of many years wondering whether an old paperwork error \u2014 a misremembered date, an ambiguous answer on a decades-old form \u2014 could be reframed as fraud. Lawyers are largely counseling calm, stressing that the overwhelming majority of naturalized citizens who answered honestly have nothing to fear, and that the government must still prove illegality, typically before a federal judge. But the chilling effect is real, and it lands hardest on a community that prizes documentation and legal compliance.

## The Broader Legal Climate

The denaturalization push does not stand alone. It arrives alongside a parallel fight over birthright citizenship now before the Supreme Court, and a wider tightening of immigration enforcement across visa categories. Civil-rights groups, including Asian Americans Advancing Justice, have challenged aspects of the administration's approach in court, arguing that an aggressive denaturalization program risks creating two tiers of citizenship \u2014 one secure, one perpetually provisional \u2014 and could deter eligible immigrants from naturalizing at all.

Department officials frame it differently. In a statement, Homeland Security leadership has called American citizenship "a privilege, not a right," and argued that those who obtained it through fraud were never entitled to it in the first place. The legal core of that position is uncontroversial: citizenship procured by genuine fraud has always been revocable. The dispute is over scale, process and intent \u2014 whether a tool used a handful of times a year is being turned into an instrument of mass review.

## Why It Matters for the Diaspora

For the Indian diaspora, the practical takeaway is sobering but manageable. Naturalized citizens who applied honestly remain on solid ground; the law still requires the government to prove fraud or material misrepresentation. But the change in posture is a reminder that, for naturalized Americans, the paperwork trail does not simply close on oath day. Attorneys are advising clients to retain their immigration records, avoid panic, and seek counsel before responding to any government inquiry. The deeper message is harder to file away: for a community that treated citizenship as the settled end of the journey, the finish line now feels, unsettlingly, like it can be redrawn."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "A U.S. naturalization ceremony; the Justice Department is ramping up its denaturalization effort"
    img_attribution = "Wikimedia Commons"

    for q in ["United States naturalization ceremony oath citizens", "US citizenship ceremony naturalization", "United States Department of Justice building Washington", "naturalization ceremony American flag"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            t = commons[0]["title"].lower()
            if "justice" in t or "doj" in t:
                img_caption = "The U.S. Department of Justice, which has stood up a dedicated unit to pursue denaturalization cases"
            elif "naturalization" in t or "citizen" in t or "oath" in t:
                img_caption = "A U.S. naturalization ceremony; a ramped-up DOJ effort is reopening the question of whether citizenship is final"
            break

    if not img_url:
        px = fetch_pexels_image("american flag passport citizenship documents")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "An American flag and citizenship documents"

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
            "CNN \u2014 Trump administration ramps up effort to strip citizenship from naturalized Americans (June 18, 2026)",
            "U.S. Department of Justice, Civil Division \u2014 memo by Assistant Attorney General Brett Shumate directing prioritization of denaturalization (June 2025)",
            "U.S. Attorney's Office, District of Oregon \u2014 denaturalization complaint against Jaswinder Singh (June 15, 2026)",
            "USCIS / DOJ \u2014 batches of denaturalization cases identified (May 8 and June 8, 2026)",
            "Asian Americans Advancing Justice \u2014 litigation and statements on the administration's denaturalization program"
        ]),
        "diaspora_angle": "A sharply expanded federal denaturalization effort \u2014 a dedicated DOJ unit expecting 'several hundred' cases, a June memo listing ten priority categories, and the first Oregon case of the term targeting an Indian-origin man \u2014 is unsettling the roughly two million naturalized Indian-Americans who treated the citizenship oath as the irreversible end of their immigration journey.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Anil Menon, Indian-American astronaut, first ISS mission ──

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Anil Menon — first ISS mission, Soyuz MS-29")
    print("="*60)

    slug = "anil-menon-indian-american-nasa-astronaut-first-iss-mission-soyuz-ms29-july-14-20260620"
    headline = "An Emergency-Room Doctor From Minneapolis Is About to Become the Diaspora's Newest Astronaut. Liftoff Is July 14."
    subheadline = "Anil Menon \u2014 son of a Malayali father and a Ukrainian mother, SpaceX's first flight surgeon, and now a U.S. Space Force colonel \u2014 will launch aboard Soyuz MS-29 for an eight-month stay on the International Space Station, adding another Indian-origin name to the short, storied list of those who have left the planet."

    body = """On July 14, a Soyuz rocket is scheduled to climb off a launch pad at the Baikonur Cosmodrome in Kazakhstan, and aboard it will be a 49-year-old emergency-medicine physician from Minneapolis who has spent his career caring for other people in their worst moments. For Dr. Anil Menon, the launch is the culmination of a journey that runs from a science-museum IMAX theater in Minnesota to the front lines of earthquake disaster zones to the medical bay at SpaceX \u2014 and now, finally, to orbit. It will be his first spaceflight.

Menon, selected by NASA in its 2021 astronaut class and graduated with the 23rd class in 2024, will serve as a flight engineer aboard the International Space Station as part of Expeditions 74 and 75. He launches alongside Roscosmos cosmonauts Pyotr Dubrov and Anna Kikina, and the trio is expected to spend roughly eight months \u2014 about 240 days \u2014 aboard the orbiting laboratory before returning to Earth in the spring of 2027.

## A Diaspora Story Written Across Continents

Menon's heritage is itself a map of migration. He was born and raised in Minneapolis to immigrant parents \u2014 a Malayali father from India and a Ukrainian mother \u2014 and his ties to India are more than ancestral. After earning a neurobiology degree from Harvard in 1999, Menon spent time in India as a Rotary Ambassadorial Fellow at Jawaharlal Nehru University, where he took part in the country's anti-polio drive before returning to the United States for a master's in mechanical engineering and a medical degree from Stanford.

That places him firmly in a lineage that the Indian diaspora has watched with pride for decades \u2014 from Kalpana Chawla and Sunita Williams to Raja Chari, and most recently Shubhanshu Shukla. Menon now joins the growing roster of astronauts with Indian roots helping shape the future of human spaceflight, a list that carries particular emotional weight for a community that has long measured its arrival in America partly through such milestones.

## From Disaster Zones to the Launch Pad

Menon's resume reads less like a typical astronaut's and more like a humanitarian's. As an emergency physician, he was a first responder during the 2010 Haiti earthquake, the 2015 Nepal earthquake, and the 2011 Reno Air Show crash. In the U.S. Air Force he logged more than 100 sorties in the F-15 and helped transport critically injured patients as part of a critical-care air transport team. He later became SpaceX's first flight surgeon, helping launch the company's first crewed mission, Demo-2, in 2020, and building the medical organization that now supports private astronauts.

His family is woven into the new era of spaceflight too. His wife, Anna Menon, is a lead space operations engineer at SpaceX and herself flew to orbit on the private Polaris Dawn mission \u2014 making the Menons one of the rare couples who can both claim spaceflight experience.

## The Mission and Its Science

This flight also marks a milestone for the program itself: it is the return of crewed Soyuz launches after an incident during the MS-28 launch in November 2025, when a service platform beneath the pad came loose and damaged the site. A successful uncrewed resupply launch from the repaired pad in March cleared the way.

Once aboard, Menon's eight months will be packed with science. NASA says he will take part in hundreds of experiments, including studies of astronaut vein structure, blood flow and blood composition in microgravity \u2014 research that draws directly on his medical training. In one experiment, he will test producing intravenous fluids using the station's own potable water, a capability that could matter enormously for future long-duration missions to the Moon and Mars, where resupply from Earth is impossible.

## Why It Matters for the Diaspora

For Indian-Americans \u2014 and for Indians watching from home \u2014 Menon's launch is the kind of story that transcends the daily churn of visa rules and trade talks. It is a reminder that the diaspora's reach now extends, literally, beyond the planet. A boy who first dreamed of space watching a shuttle film at the Science Museum of Minnesota, the son of an Indian immigrant, will spend the better part of a year orbiting Earth in the name of science that could carry humanity to other worlds.

It also lands at a moment when the broader narrative around immigration in America has turned anxious and contentious. Against that backdrop, Menon's ascent offers a quieter counterpoint: a story of an immigrant family's son reaching the highest frontier there is, carrying with him a heritage that spans Kerala, Ukraine and the American Midwest. When the Soyuz lifts off on July 14, a piece of the diaspora goes with it."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "NASA astronaut Anil Menon, who launches to the International Space Station aboard Soyuz MS-29 on July 14"
    img_attribution = "NASA / Wikimedia Commons"

    # Try Wikipedia portrait first (person)
    wiki_img = fetch_wikipedia_person_image("Anil Menon")
    if wiki_img:
        img_url = wiki_img

    if not img_url:
        for q in ["Anil Menon astronaut NASA", "Soyuz MS-29 crew", "Soyuz spacecraft launch Baikonur", "International Space Station"]:
            commons = fetch_wikimedia_commons_images(q)
            if commons:
                img_url = commons[0]["url"]
                t = commons[0]["title"].lower()
                if "menon" in t:
                    img_caption = "NASA astronaut Anil Menon, who launches to the ISS aboard Soyuz MS-29 on July 14"
                elif "soyuz" in t:
                    img_caption = "A Soyuz spacecraft; Anil Menon will fly aboard Soyuz MS-29 for his first spaceflight"
                    img_attribution = "Wikimedia Commons"
                elif "space station" in t or "iss" in t:
                    img_caption = "The International Space Station, where Anil Menon will spend roughly eight months"
                    img_attribution = "NASA / Wikimedia Commons"
                break

    if not img_url:
        px = fetch_pexels_image("astronaut space station orbit earth")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "An astronaut in orbit"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "NASA \u2014 NASA Assigns Astronaut Anil Menon to First Space Station Mission",
            "NASA \u2014 NASA Astronaut Anil Menon Available for Prelaunch Virtual Interviews (June 2026); launch targeted July 14 aboard Soyuz MS-29",
            "NASASpaceFlight.com \u2014 Next NASA ISS astronaut, doctor discusses upcoming mission",
            "NASA biography \u2014 Anil Menon, M.D., Colonel, U.S. Space Force (born Minneapolis to Ukrainian and Indian immigrants)",
            "Wikipedia \u2014 Anil Menon; Expedition 75"
        ]),
        "diaspora_angle": "Anil Menon \u2014 the Minneapolis-born son of a Malayali father and Ukrainian mother, SpaceX's first flight surgeon and now a U.S. Space Force colonel \u2014 launches July 14 aboard Soyuz MS-29 for an eight-month ISS mission, adding another Indian-origin name to the lineage of Kalpana Chawla, Sunita Williams and Shubhanshu Shukla and giving the diaspora a rare moment of pride beyond the daily churn of immigration and trade news.",
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
