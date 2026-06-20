#!/usr/bin/env python3
"""
Videshi News Writer — June 20, 2026 (22:30 UTC run)
2 NEW articles:
  1. Modi's Paris diaspora address — UPI in France, eased student/professional mobility (diaspora)
  2. The proposed F-1 rule that could trap Indian students between an H-1B miss and a 30-day clock (immigration)
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


# ─── Article 1: Modi's Paris diaspora address ──────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Modi's Paris diaspora address")
    print("="*60)

    slug = "modi-paris-indian-diaspora-address-upi-france-student-mobility-vivatech-20260620"
    headline = "In Paris, Modi Told the Diaspora They Are India's Soft Power. Then He Made Their Lives a Little Easier."
    subheadline = "At a packed Salle Pleyel, the Prime Minister thanked the Indian community for being the 'true strength' of the India\u2013France partnership \u2014 and pointed to two concrete wins for them: UPI payments going live in France and eased mobility for Indian students and professionals."

    body = """When Narendra Modi walked into the Salle Pleyel concert hall in Paris this week, the crowd did not greet him like a visiting head of government. They greeted him like family. Chants of "Modi, Modi" and "Bharat Mata Ki Jai" rolled across a hall packed with Tamils, Punjabis, Gujaratis, Marathis and Bengalis \u2014 a cross-section of India transplanted to France. "It feels like a Bharat Connect event," the Prime Minister told them, on the final leg of a Europe tour that had taken him through Nice, Slovakia, the G7 summit in Evian, and finally to Paris for the VivaTech technology conference alongside French President Emmanuel Macron.

The speech was, on its surface, the familiar diaspora-rally fare: pride, nostalgia, and a recital of India's growth story. But underneath the applause were two announcements that will land in the everyday lives of Indians living in and travelling to France.

## UPI Comes to the City of Lights

The first is money. Modi confirmed that India's Unified Payments Interface (UPI) \u2014 the real-time payments system that now handles close to half of the world's real-time digital transactions \u2014 is being rolled out in France, with acceptance at high-traffic spots including the Eiffel Tower and Paris airports. For an Indian tourist or student, that means scanning a familiar QR code instead of fumbling with foreign cards and conversion fees. "This would give a boost to tourism flows between the two countries," the Prime Minister noted, framing UPI not just as a convenience but as a quiet export of Indian digital infrastructure into the heart of Europe.

## Easier Movement for Students and Workers

The second is mobility. Modi pointed to people-to-people ties that have expanded as more Indian students, professionals and tourists choose France, and he "expressed appreciation for the steps taken to ease mobility of people." That is diplomatic shorthand for a tangible diaspora benefit: France now offers a two-year post-study work permit to Indian graduates, a window that several students in the audience singled out as life-changing.

"I came here as a student, and thanks to the strong ties between India and France, Indian students receive a two-year work permit, which is a significant opportunity," one community member told reporters after the event. At a moment when Indian families are watching the United States tighten student and work-visa pathways, a European country actively widening the door is not a small thing.

## A Reflection of India, Abroad

Modi leaned hard into the idea of the diaspora as living advertisements for India. He praised the community for "brilliantly mirroring India's core values on foreign soil," and called them the true strength of the India\u2013France Special Global Strategic Partnership. He credited them with connecting Indian innovation and ideas to global markets \u2014 a nod to the engineers, founders and researchers who increasingly move between Bengaluru, Paris and beyond.

It was also a recruiting pitch. Invoking the "Viksit Bharat" (Developed India) goal, the Prime Minister invited the diaspora to become partners in India's growth, not just spectators to it. He rattled off the numbers that have become a fixture of these speeches \u2014 GDP doubled, 250 million lifted out of poverty, airports and universities doubled, mobile manufacturing up a hundredfold \u2014 before deflecting the credit. "What is the greatest force behind this transformation? It is not because of Modi. It is because of the people of India," he said.

Modi marked the gathering as a kind of capstone, noting his government had recently completed 12 years in office and that serving as Prime Minister had been the greatest fortune of his life. "This is the power of Indian democracy, which made a tea seller reach till here," he said.

https://www.instagram.com/reel/DZu9RxrT2u4/

## Why It Matters for the Diaspora

For NRIs, the Paris stop is a useful contrast in how host countries are treating the Indian community right now. On one side of the Atlantic, the conversation is about denaturalization cases, retrogressed green-card dates and proposals to shorten the grace period for students. On the other, France is being held up as a country smoothing the path \u2014 UPI for payments, a two-year work permit for graduates, and a head of state actively courting Indian talent and tourism.

That divergence matters for the choices diaspora families make: where to send a child to study, where to build a career, where the welcome feels durable rather than conditional. Modi's message in Paris was that the diaspora is India's most valuable export and its best ambassador. The quieter subtext, audible to anyone weighing their next move, was that some doors are opening even as others close."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = fetch_wikipedia_person_image("Narendra Modi")
    img_caption = "Prime Minister Narendra Modi, who addressed the Indian community in Paris during his June 2026 Europe tour"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        for q in ["Narendra Modi 2024", "Narendra Modi portrait", "Narendra Modi official"]:
            commons = fetch_wikimedia_commons_images(q)
            if commons:
                pick = None
                for c in commons:
                    if c["width"] >= 800 and c["original_url"].lower().endswith((".jpg", ".jpeg")):
                        pick = c
                        break
                pick = pick or commons[0]
                img_url = pick["url"]
                break

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
            "Ministry of External Affairs / IANS \u2014 PM Modi given warm welcome by Indian diaspora in Paris, says it reflects 'deep affection for motherland' (June 19, 2026)",
            "PMINDIA.gov.in \u2014 PM addresses the Indian Community in Paris (UPI in France, eased mobility, Viksit Bharat invitation)",
            "IANS \u2014 'All of us are very emotional': Indian diaspora after meeting PM Modi in Paris (two-year student work permit testimony)",
            "The Indian Eye \u2014 PM Modi lauds diaspora as true strength of India-France ties",
            "Bhaskar English \u2014 PM Modi at VivaTech 2026 Paris (12 years in office, GDP and infrastructure figures, 'tea seller' remark)"
        ]),
        "diaspora_angle": "Modi's Paris address paired symbolism with two concrete diaspora wins \u2014 UPI payments going live in France and a two-year post-study work permit for Indian graduates \u2014 a striking contrast to the tightening student and work-visa climate in the United States that diaspora families are now weighing.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Proposed F-1 rule and Day-1 CPT squeeze ──────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: The F-1 rule that could trap Indian students")
    print("="*60)

    slug = "us-f1-student-visa-rule-30-day-grace-day-1-cpt-indian-students-h1b-20260620"
    headline = "A Proposed Visa Rule Would Give Indian Graduates 30 Days to Solve a Problem That Can Take Years"
    subheadline = "Washington is weighing changes that would halve the grace period for F-1 students and narrow the 'Day 1 CPT' workaround \u2014 the two safety nets that thousands of Indian graduates lean on when they lose the H-1B lottery."

    body = """For an Indian student who has just spent two years and a small fortune earning a master's degree in the United States, the scariest moment is not graduation. It is the H-1B lottery. Win it, and the path to a career in America stays open. Lose it \u2014 as most applicants do \u2014 and a clock starts ticking. A proposed set of immigration rule changes now under discussion in Washington would make that clock run faster, and close one of the few exits students use to stop it.

## The 60-Day Cushion, Cut in Half

Today, an international student on an F-1 visa whose status ends \u2014 because they graduated, lost work authorization, or fell out of a program \u2014 has a 60-day grace period to either leave the country or line up another lawful status. One proposal under review would shorten that window to 30 days.

Thirty days is not much time to restructure your entire legal life. "The proposal could have a disproportionate impact on Indian students," immigration attorney Goldman warned, noting they form one of the largest international student groups in the United States and a significant share of the H-1B applicant pool. For a graduate who has just been rejected in the lottery, halving the grace period can be the difference between finding a sponsoring employer or a cap-exempt alternative and being forced to pack up and fly home.

## The Day 1 CPT Lifeline, Narrowed

The second change is subtler but arguably more consequential. Many Indian graduates who fail to secure an H-1B currently rely on "Day 1 CPT" programs \u2014 enrolling in another academic course that allows them to keep working legally through Curricular Practical Training from the first day of study. It has become an informal bridge across the gap years between repeated H-1B attempts.

That bridge may be about to narrow sharply. "For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorization to continue working,'" Goldman explained. If the route closes, thousands of Indian professionals working in artificial intelligence, machine learning, software engineering and data science could be left with no legal way to keep working after a lottery loss.

## Not Just a Student Problem

The pain would not stop at the students. Goldman argued the impact would ripple out to the U.S. employers who depend on this talent. "There's no doubt about it that this is going to have a massive impact on the companies that are in desperate need of top talent," she said, pointing out that foreign nationals make up a substantial portion of the country's AI workforce.

Faced with a narrower funnel, companies have two options, neither good: become more cautious about hiring international graduates, or get creative with cap-exempt H-1B arrangements and O-1 "extraordinary ability" visas reserved for the most accomplished. "The companies will either struggle because they won't have the talent, or they will have to get creative and find alternate solutions," she said.

## A Pattern, Not a One-Off

The proposals do not exist in a vacuum. Indian applicants are already absorbing blow after blow in the employment-based system: the July 2026 visa bulletin marks EB-2 and EB-5 categories for India as "Unavailable" for the rest of the fiscal year, and EB-1 has retrogressed. Denaturalization cases are climbing. Deportation numbers are at record highs. Each individual change is technical; together they read as a steady tightening of the screws on exactly the cohort \u2014 highly educated Indian professionals \u2014 that the system once courted.

## Why It Matters for the Diaspora

For Indian families, the calculus around an American education is shifting in real time. The U.S. degree was long treated as a near-guaranteed on-ramp to a green card and a settled life. These proposals chip away at the margin for error that made that bet feel safe. A 30-day grace period and a closed Day 1 CPT door mean that a single bad draw in the H-1B lottery \u2014 a process governed by luck, not merit \u2014 can unravel years of investment in weeks.

The advice from practitioners is blunt: anyone in a category that is still current should file now and not wait, and students should map out their backup options well before graduation rather than after a rejection. For a community that has poured talent and tuition into the American system for decades, the message is sobering. The welcome mat is being trimmed at the edges, and the people most exposed are the ones who did everything by the book."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "International students at a U.S. university commencement; proposed rules would shorten the F-1 grace period"
    img_attribution = "Wikimedia Commons"

    for q in ["university graduation ceremony students", "college commencement graduates United States", "graduation caps students university"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            pick = None
            for c in commons:
                if c["width"] >= 1000 and c["original_url"].lower().endswith((".jpg", ".jpeg")):
                    pick = c
                    break
            pick = pick or commons[0]
            img_url = pick["url"]
            break

    if not img_url:
        px = fetch_pexels_image("university graduation students campus")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Graduates at a university commencement ceremony"

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
            "The Indian Eye \u2014 Tighter student visa rules may impact Indians in US: Expert (attorney Goldman on 60-to-30-day grace period and Day 1 CPT narrowing)",
            "U.S. Department of State \u2014 July 2026 Visa Bulletin (EB-2 and EB-5 India 'Unavailable' for the rest of FY2026; EB-1 India retrogression)",
            "Reuters / Washington Examiner \u2014 Record U.S. deportation figures under the current administration",
            "Statesman Journal \u2014 Federal government seeks to strip citizenship from Oregon immigrant (rising denaturalization cases)"
        ]),
        "diaspora_angle": "Indian students are the largest cohort relying on the F-1 grace period and Day 1 CPT as fallbacks after H-1B lottery losses; halving the grace period to 30 days and narrowing CPT would leave thousands of Indian graduates in AI, software and data science with no legal bridge to keep working \u2014 turning one unlucky lottery draw into a forced exit.",
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
