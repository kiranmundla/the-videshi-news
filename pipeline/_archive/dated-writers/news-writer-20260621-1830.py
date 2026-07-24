#!/usr/bin/env python3
"""
Videshi News Writer — June 21, 2026 (18:30 UTC run)
2 NEW articles:
  1. India's Immigration & Foreigners (Amendment) Order 2026 — OCI definition + Rajasthan protected areas (news / immigration)
  2. Two players of Indian origin head to the 2026 FIFA World Cup (news / sports-diaspora)
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


# ─── Article 1: Immigration & Foreigners (Amendment) Order 2026 ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Immigration & Foreigners (Amendment) Order 2026")
    print("="*60)

    slug = "india-immigration-foreigners-amendment-order-2026-oci-cardholder-definition-rajasthan-protected-areas-20260621"
    headline = "India Just Wrote 'OCI Cardholder' Into Its Immigration Rulebook \u2014 and Redrew the Map of Where Foreigners Can Go"
    subheadline = "A quietly notified amendment, published on June 18, formally defines the Overseas Citizen of India for the first time inside the country's immigration order and completely rewrites the list of protected border zones in Rajasthan \u2014 with carve-outs that keep the desert's famous tourist trail open."

    body = """India has amended the rulebook that governs how every foreigner \u2014 and every Overseas Citizen of India \u2014 moves through the country, and for the diaspora the change is more than bureaucratic housekeeping. The Immigration and Foreigners (Amendment) Order, 2026, published in the official gazette on June 18, does two things that reach directly into the lives of people who hold an OCI card: it writes the term "OCI Cardholder" formally into the immigration order for the first time, and it completely redraws the map of protected zones in the border state of Rajasthan, where some of the diaspora's favourite heritage destinations sit.

For the millions of overseas Indians who travel back on an OCI card \u2014 the lifelong visa that lets people of Indian origin live, work and study in India without a citizen's passport \u2014 the amendment is the latest in a run of rule changes that have made the document feel less like a settled privilege and more like a moving target. This one clarifies who an OCI holder is in the eyes of immigration law, and where they, like any foreign national, may and may not wander.

## Putting 'OCI Cardholder' on the Books

The headline change is definitional. The amendment modifies the parent Immigration and Foreigners Order, 2025, to formally include the term "Overseas Citizen of India (OCI) Cardholder," with the definition aligned to the Citizenship Act, 1955. Until now, the immigration order spoke largely of "foreigners" in general; the diaspora's particular legal status sat slightly outside the four corners of the document. Writing it in is meant to settle ambiguity about exactly how OCI holders are treated within immigration regulations \u2014 a clarification lawyers had been asking for.

The order also builds in flexibility on permits, allowing the authorities to permit movement either with or without a permit depending on the situation. That discretion cuts both ways: it lets officials wave travellers through where security allows, but it also formalises the machinery for requiring special permission where it does not.

## Redrawing Rajasthan's Protected Map

The most substantial part of the amendment is a complete revision of the schedule covering Rajasthan, the desert state that shares a long and sensitive frontier with Pakistan. The notification identifies protected areas across key border districts \u2014 Jaisalmer, Bikaner, Sriganganagar, Barmer, Phalodi and Jalore \u2014 covering entire tehsils, or sub-districts, in some cases and, in others, specific stretches lying west of major highways such as NH-11, NH-62 and NH-68. Foreign nationals heading into these zones may need advance approval from the authorities.

Crucially for travellers, the order is studded with exemptions designed to keep tourism flowing. The highway corridors along NH-11, NH-62 and NH-68 are themselves excluded from the restrictions. So are the municipal limits of the major towns \u2014 Jaisalmer, Bikaner, Barmer, Sriganganagar, Phalodi and Pokaran among them. And the marquee tourist sites stay open: the Sam sand dunes, the abandoned village of Kuldhara, Amarsagar, Khuri, and the desert safari and camping grounds that draw visitors from around the world. A 500-metre corridor along the roads leading to those spots is carved out too, so the journey to them does not stray into a restricted zone.

## A Year of OCI Rule Changes

The amendment lands in the middle of the most active period of OCI rule-making in years, and it pays to read it alongside the others. Earlier in 2026 the government revised the OCI fee structure, setting a $275 application charge abroad, and made it mandatory for cardholders to update their card within three months of getting a new passport, with penalties for late updates. The old PIO cards stopped being valid at the end of 2025, folding that category into the OCI system. A new e-OCI process has been rolled out to move applications online.

Separately, the Ministry of Home Affairs has stepped up enforcement of a long-standing but loosely applied requirement: OCI cardholders engaged in research as scholars, in journalism, or in certain missionary work, and those visiting protected, restricted or prohibited areas, must obtain special permission in advance from the relevant Indian authority \u2014 a consular post, the Foreigners Regional Registration Office, or another designated body. A new notification rule also asks OCI holders living in India to inform the FRRO of any change in their permanent Indian address or occupation.

## Why It Matters for the Diaspora

Taken together, these moves sketch a clear direction: the government wants the OCI relationship to be more precisely defined, more digitally tracked, and more tightly enforced at the edges. For most diaspora travellers, the practical effect of the June 18 order is modest \u2014 the tourist trail through Jaisalmer and the dunes stays open, and the everyday holiday is unaffected. But the document is a reminder that the OCI card, the diaspora's deepest legal tie to India, now sits inside a rulebook that is being rewritten in real time. Anyone planning research, journalism or off-the-beaten-track travel near the western border would do well to check whether a permit is now required before they go."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = ""
    img_attribution = "Wikimedia Commons"

    for q in ["Jaisalmer Fort Rajasthan", "Sam sand dunes Jaisalmer", "Jaisalmer desert Rajasthan", "Indian passport document"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            img_caption = "Jaisalmer, Rajasthan; the June 18 amendment redraws protected border zones across the desert state while keeping its famous tourist sites and highway corridors open to foreign visitors"
            break

    if not img_url:
        px = fetch_pexels_image("Jaisalmer Rajasthan desert fort")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Jaisalmer, Rajasthan; India's amended immigration order revises protected border zones while exempting major tourist destinations"

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
            "SCC Times (SCC Online) \u2014 'Immigration & Foreigners Amendment Order 2026: Explained' (published June 20): the Order, published 18-6-2026, modifies the Immigration and Foreigners Order, 2025; formally includes the term 'Overseas Citizen of India (OCI) Cardholder' aligned to the Citizenship Act, 1955; permit flexibility (movement with or without a permit); complete revision of the Third Schedule for Rajasthan listing protected areas in Jaisalmer, Bikaner, Sriganganagar, Barmer, Phalodi and Jalore; exemptions for NH-11/NH-62/NH-68 corridors, municipal areas of major towns, and tourist sites (Sam dunes, Kuldhara, Amarsagar, Khuri) plus a 500m corridor to them",
            "Curly Tales \u2014 'Planning A Rajasthan Trip? Foreign Nationals Must Follow New Rules At Border Areas' (June 19): tehsils and areas near the India-Pakistan border marked as protected; foreign nationals may need advance approval; city limits of Sri Ganganagar, Suratgarh, Bikaner, Phalodi, Bap, Pokaran, Jaisalmer, Barmer and Sanchore excluded from restrictions",
            "Fragomen, Del Rey, Bernsen & Loewy LLP \u2014 'Increased Enforcement and New Notification Rule for Overseas Citizen of India Cardholders': MHA enforcing pre-approval for OCI cardholders doing research, journalism, missionary work, or visiting Protected/Restricted/Prohibited areas; new rule requiring OCI holders in India to notify the FRRO/FRO of changes in residential address or occupation; penalties not yet outlined",
            "Background on 2026 OCI rule changes (India Abroad and related diaspora coverage): new $275 application fee abroad; mandatory card update within three months of a new passport with late-update penalties; PIO cards invalid after Dec 31, 2025; rollout of e-OCI online processing"
        ]),
        "diaspora_angle": "The OCI card is the diaspora's deepest legal tie to India, and this amendment \u2014 formally defining 'OCI Cardholder' in immigration law and redrawing Rajasthan's protected border zones \u2014 is the latest in a year of rule changes (new $275 fee, passport-update deadlines, tighter enforcement) that make the card feel like a moving target; travellers planning research, journalism or off-trail trips near the western border may now need a permit, even as the popular Jaisalmer-and-dunes tourist route stays open.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Two players of Indian origin at the 2026 World Cup ─

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Indian-origin players at the 2026 FIFA World Cup")
    print("="*60)

    slug = "indian-origin-players-2026-fifa-world-cup-tahsin-jamshid-qatar-nishan-velupillay-australia-20260621"
    headline = "India Has Never Qualified for a World Cup. This Year, Two Players With Indian Roots Are There Anyway."
    subheadline = "As the 2026 FIFA World Cup plays out across North America, the diaspora has found a team to follow even without an Indian flag on the pitch: Qatar's Tahsin Mohammed Jamshid, with roots in Kerala, and Australia's Nishan Velupillay, the first footballer of Tamil heritage at the tournament."

    body = """India is a cricketing nation that has never once qualified for a football World Cup, and for the country's vast diaspora the planet's biggest sporting event has always been something watched from the outside \u2014 a spectacle to enjoy, but never quite to claim. This year is different. As the 2026 FIFA World Cup unfolds across the United States, Canada and Mexico, two players carrying Indian heritage are on the team sheets, giving overseas Indians a thread of belonging to pull on football's grandest stage.

The moment was flagged by Congress MP Shashi Tharoor, who called it "a historic moment for Indian football fans" and pointed to two names: 19-year-old Tahsin Mohammed Jamshid, selected for Qatar, and 25-year-old Nishan Velupillay, named in Australia's squad. Neither wears the blue of India \u2014 a country that has never reached this tournament \u2014 but both trace their lineage to it, and for a diaspora that has learned to find itself in the achievements of its scattered children, that is enough to tune in.

## Tahsin Mohammed Jamshid: From Kannur to Qatar

Tahsin Mohammed Jamshid was born and raised in Doha, but his family roots run to Kannur, in Kerala \u2014 part of the enormous Malayali community that has built lives across the Gulf over generations. A winger who came up through Qatar's renowned Aspire Academy, he now plays his club football for Al Duhail and made his senior international debut for Qatar in a World Cup qualifier against Afghanistan.

His selection carries a specific distinction: he is the first player of Indian origin ever chosen for Qatar's national football team, and should he take the field at this World Cup, he would become the first player of Indian origin to feature in a World Cup match. For the Gulf's huge Indian population \u2014 Qatar alone is home to hundreds of thousands of Indians, many of them Keralite \u2014 a young man with family in Kannur running out at a World Cup is the kind of story that travels fast through WhatsApp groups and community gatherings.

## Nishan Velupillay: The First Tamil at a World Cup

Australia's Nishan Velupillay tells a different version of the same diaspora story. Born and raised in Melbourne, he has Tamil roots through his father, while his mother is Anglo-Indian. A winger for Melbourne Victory known for his pace and attacking instinct, he debuted for Australia's Socceroos in 2024 and scored on his first appearance, in a World Cup qualifier against China, before becoming a regular in the national setup.

With his selection, Velupillay is set to become the first footballer of Tamil heritage to play at a World Cup \u2014 a milestone for the global Tamil community spread across Australia, Southeast Asia, Europe and North America. His journey, from a Melbourne childhood to the Socceroos' World Cup squad, mirrors the trajectory of so many second-generation diaspora children who grow up wholly of their new country while carrying the threads of an older one.

## A Diaspora Tradition Older Than This Tournament

Tharoor also reached back two decades to remind fans this is not entirely new. Vikash Dhorasoo, who represented France at the 2006 World Cup and was part of the side that finished runners-up in Germany, traced his ancestry to Vizianagaram in Andhra Pradesh, before his forebears settled in Mauritius and then France \u2014 a route that captures the long, layered history of Indian migration across the colonial world. The presence of Jamshid and Velupillay in 2026 places them in that lineage: players whose national jerseys are not India's, but whose stories are unmistakably part of the Indian story.

## Why It Matters for the Diaspora

For overseas Indians, sport has always been a way of negotiating dual belonging \u2014 cheering for the country you live in while quietly tracking anyone who shares your roots. Football, the world's game, has long been the one arena where India was simply absent from the top table. The 2026 World Cup, running from June 11 to July 19 and billed as the largest edition ever, changes that calculus in a small but meaningful way. India still has not qualified, and may not for years. But in Doha-raised Tahsin Mohammed Jamshid and Melbourne-raised Nishan Velupillay, the diaspora has found a way in \u2014 two young men who carry Kerala and Tamil Nadu onto a stage their ancestral homeland has never reached, and who let millions of Indians around the world watch this World Cup with something more personal than curiosity."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = ""
    img_attribution = "Wikimedia Commons"

    # Try player photos first (likely unavailable for young players), then generic football imagery
    person_img = fetch_wikipedia_person_image("Nishan Velupillay")
    if person_img:
        img_url = person_img
        img_caption = "Nishan Velupillay of Melbourne Victory and Australia, set to become the first footballer of Tamil heritage to play at a World Cup"
        img_attribution = "Wikimedia Commons"

    if not img_url:
        for q in ["FIFA World Cup 2026 football match", "association football match stadium", "soccer ball stadium football", "football pitch stadium crowd"]:
            commons = fetch_wikimedia_commons_images(q)
            if commons:
                img_url = commons[0]["url"]
                img_caption = "The 2026 FIFA World Cup, hosted across the United States, Canada and Mexico, features two players of Indian heritage \u2014 Qatar's Tahsin Mohammed Jamshid and Australia's Nishan Velupillay"
                break

    if not img_url:
        px = fetch_pexels_image("football soccer stadium match")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Two players of Indian origin \u2014 Qatar's Tahsin Mohammed Jamshid and Australia's Nishan Velupillay \u2014 are at the 2026 FIFA World Cup"

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
            "Connected to India / The Free Press Journal \u2014 'Indian-origin Tahsin Mohammed Jamshid, Nishan Velupillay set to represent Qatar and Australia at FIFA World Cup': Tahsin Mohammed Jamshid, 19, first player of Indian origin selected for Qatar, born/raised in Doha with roots in Kannur, Kerala, Aspire Academy graduate, plays for Al Duhail, debuted vs Afghanistan; Nishan Velupillay, 25, Melbourne Victory winger born/raised in Melbourne, Tamil roots via father and Anglo-Indian mother, debuted for Australia in 2024 scoring vs China, set to be first footballer of Tamil heritage at a World Cup",
            "Shashi Tharoor (MP) via social media \u2014 called it 'a historic moment for Indian football fans', highlighting two players of Indian heritage at the 2026 World Cup and recalling Vikash Dhorasoo (France, 2006 runners-up), whose ancestry traced to Vizianagaram, Andhra Pradesh, via Mauritius and France",
            "CommBank Socceroos (@Socceroos) \u2014 confirmation of Nishan Velupillay's inclusion in Australia's 26-man World Cup squad",
            "FIFA / tournament background \u2014 the 2026 FIFA World Cup runs June 11 to July 19, hosted by the United States, Canada and Mexico, the largest edition of the tournament to date; India has never qualified for a FIFA World Cup"
        ]),
        "diaspora_angle": "Football is the one global stage India has never reached, so for the diaspora the 2026 World Cup is usually watched from the outside; this year, Kerala-rooted Tahsin Mohammed Jamshid (Qatar) and Tamil-and-Anglo-Indian Nishan Velupillay (Australia) give overseas Indians \u2014 especially the huge Malayali community in the Gulf and Tamil communities worldwide \u2014 a personal thread to follow at the tournament.",
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
