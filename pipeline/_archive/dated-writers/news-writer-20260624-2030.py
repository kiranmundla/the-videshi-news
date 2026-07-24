#!/usr/bin/env python3
"""
Videshi News Writer — June 24, 2026 (20:30 UTC run)
2 NEW articles, distinct from all prior runs (dedup-checked against last 45 news):
  1. India's ODI squad for the England tour: BCCI named a 15-member ODI squad for
     the 3-match series starting July 14, with Shubman Gill captaining, Shreyas
     Iyer his deputy, and Virat Kohli's inclusion subject to a hamstring-injury
     fitness check. Distinct from any prior IPL/cricket coverage.
  2. Indian-origin players at the 2026 FIFA World Cup: for the first time, three
     players of Indian heritage — Sarpreet Singh (New Zealand), Tahsin Mohammed
     Jamshid (Qatar) and Nishan Velupillay (Australia) — are at football's biggest
     stage simultaneously. A diaspora-identity story, distinct from all prior runs.
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


# \u2500\u2500\u2500 Article 1: India's ODI squad for England tour, Kohli's return \u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: India ODI squad for England tour (Kohli return)")
    print("="*60)

    slug = "india-odi-squad-england-tour-kohli-fitness-gill-captain-bumrah-returns-diaspora-20260624"
    headline = "Kohli's Name Is on India's England Squad. Whether He Boards the Plane Is Another Question."
    subheadline = "The BCCI has named a 15-man ODI squad for next month's tour of England, with Shubman Gill leading, Jasprit Bumrah back, and Virat Kohli picked subject to a fitness check on the hamstring that troubled him in the IPL final \u2014 a selection the diaspora will be watching closer than most."

    body = """India's selectors have done the thing the country's cricket fans most wanted and most feared in equal measure: they have put Virat Kohli's name on the squad sheet for the upcoming one-day series in England \u2014 but with an asterisk. The 15-member ODI squad announced by the Board of Control for Cricket in India (BCCI) for the three-match series, which begins on July 14, lists Kohli's selection as subject to a fitness assessment, after the hamstring strain he picked up during the IPL 2026 final cast doubt over his availability.

For a generation of diaspora cricket fans, that single conditional clause is the headline. Kohli, still among the most bankable batters in the white-ball game, remains the player whose presence fills stands from Birmingham to Manchester \u2014 and the uncertainty over whether he will actually take the field has turned a routine squad announcement into a fitness vigil.

## A Squad Built Around Youth and Experience

The bigger story, though, is the shape of the team around him. Shubman Gill, fresh off captaining India to a 3-0 sweep of Afghanistan, has been confirmed as ODI captain, with Shreyas Iyer named his deputy. It is a clear statement of generational intent: the leadership of India's 50-over side is being handed to its rising stars even as the old guard lingers.

The squad pairs that youth with the return of its most important fast bowler. Jasprit Bumrah, managed carefully across formats, is back for the ODI leg, anchoring a pace attack that also features Arshdeep Singh, Prasidh Krishna, Harshit Rana and uncapped paceman Gurnoor Brar. The spin department leans on Kuldeep Yadav, Axar Patel and the all-round Washington Sundar, while the batting blends Rohit Sharma, KL Rahul, Ishan Kishan and Nitish Kumar Reddy with Gill, Iyer and \u2014 fitness permitting \u2014 Kohli.

The full ODI squad: Shubman Gill (c), Shreyas Iyer (vc), Rohit Sharma, Virat Kohli (subject to fitness), KL Rahul, Ishan Kishan, Nitish Kumar Reddy, Washington Sundar, Axar Patel, Kuldeep Yadav, Jasprit Bumrah, Arshdeep Singh, Prasidh Krishna, Harshit Rana and Gurnoor Brar.

## T20Is First, With a Teenage Sensation

Before the one-dayers, England and India will contest a five-match T20I series running from July 1 to July 11. That side is led by Shreyas Iyer and is notable for the inclusion of 15-year-old batting prodigy Vaibhav Sooryavanshi, whose rapid rise has made him one of the most talked-about young cricketers in the country. The T20I squad did take an early blow: Nitish Kumar Reddy was ruled out of the shortest-format leg with a left quadriceps injury and replaced by all-rounder Suryansh Shedge, though Reddy remains in the ODI plans.

On the other side, England have assembled a strong white-ball unit. Harry Brook captains the hosts, with Jos Buttler, the express pace of Jofra Archer, leg-spinner Rehan Ahmed and the explosive Phil Salt among the names lining up to test a transitioning India.

## Why It Matters for the Diaspora

An India tour of England is unlike any other on the calendar for the diaspora. The United Kingdom is home to one of the largest and oldest Indian-origin communities in the world, and a summer series turns grounds like Edgbaston, Old Trafford and The Oval into something close to home fixtures, with tens of thousands of British Indians filling the stands in blue. For families across the UK \u2014 and for the wider diaspora watching from North America and the Gulf through the small hours \u2014 these matches are appointment viewing, a shared ritual that stitches generations together around a screen or a stadium.

The stakes run deeper than nostalgia. This series is an early waypoint on the road to the 2027 ODI World Cup, to be co-hosted by South Africa, Zimbabwe and Namibia, and the blend of Gill's young leadership group with the experience of Rohit, Kohli and Bumrah is exactly the balance the selectors are trying to calibrate. For the diaspora fan, every selection call \u2014 starting with whether Kohli's hamstring holds \u2014 is a clue to what India's next World Cup team will look like. The squad sheet is out. Now everyone waits to see who actually walks out to bat.
"""

    img_url = fetch_wikipedia_person_image("Virat Kohli")
    img_attribution = "Wikimedia Commons"
    img_caption = "Virat Kohli, whose inclusion in India's ODI squad for the England tour is subject to a fitness check on a hamstring strain from the IPL 2026 final"

    if not img_url:
        img_url = fetch_wikipedia_person_image("Shubman Gill")
        img_caption = "Shubman Gill, named captain of India's ODI squad for the three-match series in England beginning July 14"

    if not img_url:
        img_url, _ = pick_commons([
            "Virat Kohli batting",
            "Shubman Gill cricket India",
            "India cricket team ODI",
            "cricket stadium England"
        ])
        img_caption = "India has named its ODI squad for next month's three-match series in England"

    if not img_url:
        px = fetch_pexels_image("cricket stadium match")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "India's ODI squad for the England tour blends a young leadership group with returning senior players"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "cricket",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "BCCI / PTI (via Indian sports press, June 2026) \u2014 'India name 15-member ODI squad for England tour': the BCCI announced a 15-man ODI squad for the three-match series in England beginning July 14; Shubman Gill was named captain and Shreyas Iyer vice-captain; Virat Kohli was included subject to a fitness assessment following a hamstring strain sustained in the IPL 2026 final; Jasprit Bumrah returns to the ODI side; the squad also includes Rohit Sharma, KL Rahul, Ishan Kishan, Nitish Kumar Reddy, Washington Sundar, Axar Patel, Kuldeep Yadav, Arshdeep Singh, Prasidh Krishna, Harshit Rana and uncapped Gurnoor Brar.",
            "ESPNcricinfo (espncricinfo.com, June 2026) \u2014 'Gill to lead, Kohli subject to fitness as India pick England ODI squad': Shubman Gill, fresh from a 3-0 ODI sweep of Afghanistan, will captain India in England; the selectors flagged Kohli's availability as dependent on recovery from an IPL-final hamstring injury; the ODI series forms part of India's build-up to the 2027 ODI World Cup co-hosted by South Africa, Zimbabwe and Namibia.",
            "Hindustan Times (hindustantimes.com, June 2026) \u2014 'India T20I squad for England: Shreyas Iyer to lead, Vaibhav Sooryavanshi included': India's five-match T20I series in England runs July 1\u201311, with Shreyas Iyer captaining and 15-year-old Vaibhav Sooryavanshi named in the squad; Nitish Kumar Reddy was ruled out of the T20I leg with a left quadriceps injury and replaced by Suryansh Shedge, while remaining in the ODI squad.",
            "Sky Sports (skysports.com, June 2026) \u2014 'England name white-ball squads for India series': England's white-ball unit for the India series is led by Harry Brook and includes Jos Buttler, Jofra Archer, Rehan Ahmed and Phil Salt; the series spans T20Is and ODIs through July as both sides continue rebuilding their limited-overs teams."
        ]),
        "diaspora_angle": "An India tour of England is a home-from-home event for Britain's large Indian-origin community, turning grounds like Edgbaston and Old Trafford into seas of blue, while diaspora fans across North America and the Gulf watch through the night \u2014 and Kohli's fitness saga, Gill's new captaincy and the road to the 2027 World Cup make every selection call matter to millions.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: Indian-origin players at the 2026 FIFA World Cup \u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Indian-origin players at the 2026 World Cup")
    print("="*60)

    slug = "indian-origin-players-2026-fifa-world-cup-sarpreet-singh-tahsin-jamshid-nishan-velupillay-diaspora-20260624"
    headline = "India Isn't at the World Cup. But Three Players of Indian Descent Are."
    subheadline = "For the first time, three footballers of Indian heritage \u2014 New Zealand's Sarpreet Singh, Qatar's Tahsin Mohammed Jamshid and Australia's Nishan Velupillay \u2014 are playing at a men's World Cup simultaneously, carrying a diaspora's story onto the sport's biggest stage even as India watches from the outside."

    body = """India, a nation of 1.4 billion people, has never qualified for the men's FIFA World Cup. But at the 2026 tournament \u2014 the sprawling, 48-team edition co-hosted by the United States, Canada and Mexico \u2014 the Indian story is on the field anyway, stitched into the squads of three other nations. For the first time, three players of Indian heritage are competing at a men's World Cup at the same time, a quiet milestone that has lit up diaspora social media even as India's own team watches from home.

The trio carry their roots in different ways, through different countries, but together they form something the diaspora has never quite had before: representation at football's defining event.

## Sarpreet Singh: New Zealand's Punjabi Playmaker

The most established of the three is Sarpreet Singh, the New Zealand midfielder who wears the number 10. Born in Auckland to parents who emigrated from Jalandhar in Punjab, Singh is believed to be the first Sikh footballer to play at a men's World Cup \u2014 a detail that has resonated powerfully across the Punjabi diaspora. A graduate of the FC Bayern Munich system who now plays for Wellington Phoenix, he featured for 92 minutes in New Zealand's spirited 2-2 group-stage draw against Iran, pulling the strings in midfield. New Zealand's campaign has been hard going since \u2014 a 3-1 loss to Egypt left them needing a result against Belgium on June 27 \u2014 but Singh's presence alone has made him a folk hero among fans who rarely see a turban or a Punjabi surname on a World Cup team sheet.

## Tahsin Mohammed Jamshid: Qatar's Malayali Winger

The youngest and perhaps most historic selection is Tahsin Mohammed Jamshid, a 19-year-old winger born in Doha to Malayali parents with roots in Kannur, Thalassery and Valapattanam in Kerala. A product of Qatar's renowned Aspire Academy who now plays for Al Duhail, Jamshid is the first player of Indian origin ever selected by Qatar \u2014 a remarkable arc for a son of the Gulf's enormous Malayali community, the very community whose labour and remittances have shaped both Kerala and the UAE-Qatar corridor for decades. For the millions of Indians in the Gulf, seeing one of their own in Qatari maroon at a World Cup is a moment of profound pride.

## Nishan Velupillay: Australia's Melbourne Flyer

The third is Nishan Velupillay, the 25-year-old Australia winger who plays his club football for Melbourne Victory. His heritage is a tapestry of the wider South Asian diaspora: a father of Sri Lankan Tamil descent with Malaysian roots, and an Anglo-Indian mother. Velupillay announced himself on the international stage by scoring on his debut against China, and his rise reflects the increasingly multicultural face of Australian football, where players of South Asian descent remain rare but rising. Australia next face Paraguay on June 25.

## A Lineage, and a Larger Question

The three are not entirely without precedent. Football historians point to Vikash Dhorasoo, the France midfielder who featured at the 2006 World Cup and whose ancestors hailed from Vizianagaram in Andhra Pradesh \u2014 a reminder that the Indian thread has surfaced at this tournament before, however rarely. But three at once is new, and it has not gone unnoticed at home. Shashi Tharoor, the member of parliament and diaspora commentator, called it a "historic moment" on X, celebrating the players while gently underlining the obvious irony.

## Why It Matters for the Diaspora

That irony is the heart of the story. For the global Indian diaspora \u2014 some 35 million people scattered across the Gulf, North America, the UK, Australia and beyond \u2014 these three players are a source of uncomplicated joy and a pointed question rolled into one. They are proof that Indian-origin talent can reach the world's biggest stage when nurtured in systems that develop it, from Aspire Academy to the A-League to the Bundesliga pipeline. And they are an implicit indictment of why that talent so rarely emerges at home. India's own captain, goalkeeper Gurpreet Singh Sandhu, posted an Instagram story during the tournament reflecting on why India isn't there \u2014 a rare, raw acknowledgement from inside the national setup. For now, the diaspora has found its representatives by adoption rather than by flag. When Sarpreet Singh steps onto the pitch in his number 10, or Jamshid is sent on to chase a game for Qatar, millions of Indians half a world away will feel, for ninety minutes, like they finally made it to the World Cup.
"""

    img_url = fetch_wikipedia_person_image("Sarpreet Singh")
    img_attribution = "Wikimedia Commons"
    img_caption = "Sarpreet Singh, the New Zealand midfielder born in Auckland to a family from Jalandhar, Punjab \u2014 believed to be the first Sikh footballer at a men's World Cup"

    if not img_url:
        img_url = fetch_wikipedia_person_image("Nishan Velupillay")
        img_caption = "Nishan Velupillay, the Melbourne-born Australia winger whose heritage spans the wider South Asian diaspora"

    if not img_url:
        img_url, _ = pick_commons([
            "Sarpreet Singh footballer",
            "Nishan Velupillay",
            "FIFA World Cup 2026",
            "association football match stadium"
        ])
        img_caption = "Three players of Indian heritage are featuring at the 2026 FIFA World Cup"

    if not img_url:
        px = fetch_pexels_image("soccer football stadium match")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "For the first time, three players of Indian descent are at a men's World Cup simultaneously"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "sports",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "The Indian Express (indianexpress.com, June 2026) \u2014 'Three players of Indian origin at the 2026 FIFA World Cup': for the first time, three footballers of Indian heritage are at a men's World Cup simultaneously \u2014 Sarpreet Singh (New Zealand), Tahsin Mohammed Jamshid (Qatar) and Nishan Velupillay (Australia); Sarpreet Singh, born in Auckland to Punjabi parents from Jalandhar, is believed to be the first Sikh player at a men's World Cup and came through FC Bayern Munich's system before joining Wellington Phoenix.",
            "Khaleej Times (khaleejtimes.com, June 2026) \u2014 'Qatar's Tahsin Jamshid: first player of Indian origin in maroon': Tahsin Mohammed Jamshid, 19, born in Doha to Malayali parents with roots in Kannur, Thalassery and Valapattanam, is the first Indian-origin player selected by Qatar; a product of Aspire Academy, he plays club football for Al Duhail; the selection has been celebrated across the Gulf's large Malayali community.",
            "ESPN (espn.com, June 2026) \u2014 'New Zealand held by Iran as Sarpreet Singh impresses; Velupillay scores for Australia': Sarpreet Singh played 92 minutes in New Zealand's 2-2 draw with Iran before a 3-1 loss to Egypt left the All Whites needing a result against Belgium on June 27; Australia's Nishan Velupillay, who scored on his international debut against China, faces Paraguay on June 25; Velupillay's father is of Sri Lankan Tamil descent with Malaysian roots and his mother is Anglo-Indian.",
            "Hindustan Times (hindustantimes.com, June 2026) \u2014 'Shashi Tharoor hails \\u2018historic moment\\u2019 as players of Indian origin feature at World Cup': Congress MP Shashi Tharoor called it a 'historic moment' on X as three players of Indian descent competed at the 2026 World Cup; the piece notes the precedent of Vikash Dhorasoo, the France midfielder at the 2006 World Cup whose ancestry traced to Vizianagaram in Andhra Pradesh, and references India captain Gurpreet Singh Sandhu's reflection on why India has not qualified."
        ]),
        "diaspora_angle": "For a diaspora of some 35 million that has never seen India at a men's World Cup, the simultaneous presence of three Indian-origin players \u2014 a Punjabi Sikh for New Zealand, a Gulf-born Malayali for Qatar, and a South-Asian-heritage winger for Australia \u2014 is both a source of pride and a pointed reminder of the talent India fails to develop at home, making the 2026 tournament a uniquely personal watch for Indians worldwide.",
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
