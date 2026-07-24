#!/usr/bin/env python3
"""
Videshi NRI-World Writer — June 23, 2026 (18:00 run)
2 NEW NRI-World articles, fresh & distinct from prior runs (which covered
India Heritage Center DC, NRI mutual funds/FATCA, GLO-INDIA gala, Indiaspora
tax report, Pravasi Rishta portal, FCNR deposit war, Viksit Bharat House of
Lords, remittances record, GOPIO-CT 20th, Oxford mandir, etc.):
  1. Padma Awards 2026 — at the second Civil Investiture Ceremony, President
     Murmu honours two US-based Indian-origin physicians, Dr Dattatreyudu Nori
     (Padma Bhushan) and Prof Prateek Sharma (Padma Shri), a quiet recognition
     of the diaspora's medical contribution. (diaspora-achievement angle)
  2. UK-India Week 2026 opens at the University of Warwick — the 10th edition,
     with a Gujarat delegation and West Midlands leaders turning the diaspora's
     soft power into hard investment, skills and clean-energy deals. (diaspora
     economic-bridge angle)
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
        print(f"  \u26a0 Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=8):
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


# \u2500\u2500\u2500 Article 1: Padma Awards 2026 \u2014 diaspora physicians honoured \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Padma Awards 2026 \u2014 diaspora physicians")
    print("="*60)

    slug = "padma-awards-2026-diaspora-physicians-nori-prateek-sharma-civil-investiture-20260623"
    headline = "Two American Doctors Got One of India's Highest Honours This Week. Both Left India Decades Ago."
    subheadline = "At the second Padma investiture of 2026, President Droupadi Murmu pinned the Padma Bhushan on a New York radiation oncologist and the Padma Shri on a Kansas gastroenterologist \u2014 a reminder that India still counts the diaspora's achievements as its own."

    body = """When President Droupadi Murmu stepped forward at Rashtrapati Bhavan this week to confer the second tranche of the 2026 Padma Awards, the citations read out in the ceremonial hall stretched well beyond India's borders. Among the recipients were two physicians who built their careers not in Delhi or Mumbai but in the hospitals of New York and Kansas \u2014 a quiet acknowledgement that, for India, the diaspora's accomplishments are still tallied on the home country's ledger.

Dr Dattatreyudu Nori, a radiation oncologist long associated with NewYork-Presbyterian and Weill Cornell Medicine, received the Padma Bhushan, the third-highest of India's civilian honours. Professor Prateek Sharma, a gastroenterologist at the University of Kansas School of Medicine, was awarded the Padma Shri. They were among 65 awardees honoured at the second Civil Investiture Ceremony of the year, the function the government uses to clear the long list of names announced each Republic Day.

## A Lifetime in Cancer Medicine

Nori's recognition caps a career that has shaped how cancer is treated in the United States. A pioneer of brachytherapy \u2014 the technique of placing radioactive sources directly inside or beside a tumour \u2014 he has spent decades treating prostate, gynaecological and other cancers, training generations of oncologists, and serving in senior roles at major American cancer centres. For Indian-Americans of a certain vintage, his name has long been a fixture on the short list of diaspora doctors who reached the very top of their specialty in the West while remaining visible benefactors of medical education back home.

Sharma's Padma Shri honours a different but equally consequential strand of medicine. As a gastroenterologist and researcher at the University of Kansas, he is internationally known for his work on Barrett's oesophagus and the early detection of oesophageal cancer, and for advancing the endoscopic imaging techniques now used to catch the disease before it turns deadly. His research has helped write the clinical guidelines that gastroenterologists around the world follow.

## The Diaspora on India's Honours List

The Padma Awards have, for years, made room for people of Indian origin settled abroad, and 2026 is no exception. This week's list also included foreign nationals \u2014 among them recipients from Russia and Georgia \u2014 alongside a roster of domestic figures from the arts, sport and public life, including tennis veteran Vijay Amritraj, the actor Mammootty and the playback singer Alka Yagnik. But it is the inclusion of working American physicians that tends to resonate most directly with the diaspora, because it frames their professional lives as a contribution India chooses to claim.

That framing is not merely sentimental. Indian-origin doctors make up a strikingly large share of the physician workforce in both the United States and the United Kingdom, and they have become one of the diaspora's most powerful sources of soft influence \u2014 in hospitals, in medical schools, and increasingly in the philanthropy and training partnerships that connect Western institutions back to India. Honouring two of them at Rashtrapati Bhavan is, in effect, India publicly counting that influence as part of its own story.

## Why It Matters

For the millions of Indians abroad who will never receive a state honour, the symbolism still lands. A Padma award handed to a doctor who emigrated decades ago tells second- and third-generation diaspora families that distance and a foreign passport do not sever the tie \u2014 that the country of origin is still watching, and still keeping score in the achievement column. For the medical diaspora in particular, it is a rare moment of formal recognition from a homeland that more often makes headlines abroad for visa rules and remittance flows than for saying thank you.

## What's Next

The investiture closes out the formal recognition cycle that began with the Republic Day announcement in January, though the conversations it triggers tend to outlast the ceremony. Diaspora medical associations in the United States and Britain frequently use such honours as rallying points for fundraising and training initiatives, and the two physicians recognised this week are likely to be feted again at community galas closer to home in the months ahead. For India, the calculation is simpler: as long as its most accomplished children abroad keep accepting the call to Rashtrapati Bhavan, the diaspora's success remains, in part, India's to celebrate."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = fetch_wikipedia_person_image("Dattatreyudu Nori")
    img_caption = "Dr Dattatreyudu Nori receiving a Padma award at a Civil Investiture Ceremony at Rashtrapati Bhavan; the New York radiation oncologist was conferred the Padma Bhushan in 2026"
    img_attribution = "Government of India / Wikimedia Commons"

    if not img_url:
        img_url, ctitle = pick_commons([
            "Droupadi Murmu Padma award ceremony",
            "Padma award ceremony Rashtrapati Bhavan",
            "Rashtrapati Bhavan ceremony"
        ])
        img_caption = "A Padma Award investiture ceremony at Rashtrapati Bhavan in New Delhi"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "nri-world",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "NationPress (nationpress.com, June 2026) \u2014 coverage of the second Civil Investiture Ceremony 2026 at Rashtrapati Bhavan, where President Droupadi Murmu conferred 65 Padma Awards; US-based Indian-origin physicians Dr Dattatreyudu Nori (Padma Bhushan, radiation oncology, NewYork-Presbyterian / Weill Cornell) and Prof Prateek Sharma (Padma Shri, gastroenterology, University of Kansas) among the honourees, alongside foreign nationals from Russia and Georgia and Indian figures including Vijay Amritraj, Mammootty and Alka Yagnik.",
            "Indian.Community / hi INDiA (indian.community, hiindia.com, June 2026) \u2014 reports on Indian-Americans honoured at the 2026 Padma investiture, detailing Dr Nori's career in brachytherapy and radiation oncology and Prof Sharma's work on Barrett's oesophagus and early oesophageal-cancer detection at the University of Kansas.",
            "Wikipedia (en.wikipedia.org) \u2014 biographical entries for Dattatreyudu Nori (radiation oncologist, brachytherapy pioneer associated with Weill Cornell / NewYork-Presbyterian) and Prateek Sharma (gastroenterologist at the University of Kansas School of Medicine known for oesophageal-cancer research), and the list of Padma Award recipients."
        ]),
        "diaspora_angle": "Indian-origin doctors are one of the diaspora's biggest contributions to the West \u2014 a huge share of physicians in the US and UK \u2014 yet they rarely get formal recognition from the homeland; pinning a Padma Bhushan and a Padma Shri on two American-based physicians is India publicly counting the medical diaspora's success as its own, and telling emigrant families that a foreign passport and decades abroad don't cut the tie.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: UK-India Week 2026 opens at Warwick \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: UK-India Week 2026 at Warwick")
    print("="*60)

    slug = "uk-india-week-2026-warwick-gujarat-west-midlands-investment-diaspora-20260623"
    headline = "Britain's Big India Summit Left London This Year. It Went to the Midlands Instead."
    subheadline = "The 10th UK-India Week opened at the University of Warwick, with a Gujarat delegation courting West Midlands leaders on investment, skills and clean energy \u2014 a sign that the diaspora's economic diplomacy is moving out of the capital and into Britain's industrial heartland."

    body = """For nine years, the centre of gravity of Britain's most prominent India-focused business gathering has been London \u2014 its boardrooms, its think-tank halls, the gilded rooms of Westminster. This year, the 10th edition of UK-India Week opened somewhere less expected: the campus of the University of Warwick, in the West Midlands, the industrial belt that still builds much of what Britain makes.

The choice of venue is itself the story. By convening its Smarter Regions strand at Warwick, the India Global Forum \u2014 the organisation behind UK-India Week \u2014 signalled a deliberate shift away from a capital-centric idea of the bilateral relationship toward one rooted in regional economies, advanced manufacturing and the universities that feed them. For the Indian diaspora in Britain, much of which lives and works well outside London, it is a recognition that the relationship's next chapter will be written in places like Birmingham, Coventry and the wider Midlands.

## A Gujarat Delegation in the Midlands

At the centre of the Warwick proceedings was a delegation from Gujarat, led by senior state officials including Mamta Verma and the IAS officer Dr Vikrant Pandey, who met West Midlands leaders to discuss investment, innovation, skills and advanced manufacturing. The agenda ran through the sectors where the two regions' interests overlap most naturally \u2014 clean energy, life sciences, advanced manufacturing \u2014 and where a fast-industrialising Indian state and a post-industrial British region each have something the other wants.

The Warwick meetings did not appear from nowhere. They build directly on exchanges that began in February 2026, when officials from GIFT City \u2014 Gujarat's flagship international finance hub \u2014 and the West Midlands started mapping out where investment, financial services and skills partnerships might flow. This week's forum turned those early conversations into face-to-face negotiation, the kind of patient relationship-building that precedes any actual deal.

## The Diaspora as the Connective Tissue

What gives the West Midlands its claim on India is not just industrial capacity but people. The region is home to one of Britain's largest and most established Indian-origin populations, a community whose family businesses, professional networks and cultural ties have for decades quietly underwritten trade between the two countries. UK-India Week is, in large part, an attempt to formalise that informal advantage \u2014 to turn diaspora relationships into investment pipelines, university partnerships and joint ventures.

That is why the forum's themes \u2014 investment, innovation, skills, advanced manufacturing, clean energy and life sciences \u2014 read less like a wish list than a map of where diaspora networks already operate. Indian-origin entrepreneurs and professionals sit on both sides of many of these sectors, and events like this one exist to introduce the institutions that have not yet found one another.

## Why It Matters

For NRIs in Britain, the symbolism of moving the summit out of London matters as much as the deals themselves. It suggests that the economic relationship between the two countries is broadening from a narrow, finance-and-Whitehall affair into something more distributed \u2014 one that touches regional universities, mid-sized manufacturers and the skills agenda that determines whether young people in both places find good work. The diaspora has long argued that its value lies precisely in these everyday, regional connections rather than in marquee summits; holding UK-India Week at Warwick is a tacit agreement.

## What's Next

UK-India Week typically unfolds over several days and multiple venues, building toward its set-piece events and the announcements that organisers like to time for maximum attention. The Gujarat\u2013West Midlands track will be watched for concrete commitments \u2014 memoranda of understanding, university tie-ups, investment pledges \u2014 that convert this week's meetings into something durable. Whether or not specific deals land immediately, the larger signal is already clear: the architecture of the UK-India relationship is being rebuilt to run through the regions, and the diaspora that populates them is being asked to help hold it up."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url, ctitle = pick_commons([
        "University of Warwick campus",
        "University of Warwick building",
        "University of Warwick"
    ])
    img_caption = "The University of Warwick in the West Midlands, which hosted the opening of the 10th UK-India Week in 2026"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("Birmingham England business district skyline")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "The West Midlands, the focus of this year's UK-India Week and a hub of Britain's Indian-origin business community"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "nri-world",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "The Hindu BusinessLine (thehindubusinessline.com, June 2026) \u2014 coverage of UK-India Week 2026 and the India Global Forum's Smarter Regions Forum hosted at the University of Warwick, including a Gujarat delegation meeting West Midlands leaders on investment, innovation, skills and advanced manufacturing.",
            "Swadesi / BizNewsDesk / PRNewswire (swadesi.com, biznewsdesk.com, June 2026) \u2014 reports on the 10th edition of UK-India Week opening at Warwick, the Gujarat delegation led by officials including Mamta Verma and Dr Vikrant Pandey (IAS), and the forum's focus on clean energy, life sciences and advanced manufacturing.",
            "LatestLY / GIFT City coverage (latestly.com, February 2026) \u2014 background on the February 2026 exchanges between GIFT City (Gujarat International Finance Tec-City) and the West Midlands on investment, financial services and skills partnerships that the Warwick meetings build upon."
        ]),
        "diaspora_angle": "Britain's largest concentration of Indian-origin families and businesses sits outside London, in places like the West Midlands; moving UK-India Week's regions forum to the University of Warwick \u2014 and pairing a Gujarat delegation with Midlands leaders \u2014 is an attempt to turn the diaspora's informal, decades-old family and professional networks into formal investment pipelines, university tie-ups and clean-energy and manufacturing deals.",
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
