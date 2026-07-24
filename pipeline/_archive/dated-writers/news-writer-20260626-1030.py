#!/usr/bin/env python3
"""
Videshi News Writer — June 26, 2026 (10:30 UTC / June 26 03:30 PDT run)
2 NEW articles, dedup-checked against last ~40 news articles:
  1. India resumes tourist visas for Bangladeshi nationals from June 28, 2026 —
     ending a ~2-year suspension since Aug 5, 2024. Announced by new HC Dinesh
     Trivedi in Dhaka June 25. Five IVACs. Signals thawing India-Bangladesh ties.
     NOT covered.
  2. Europe's record-breaking "killer" heatwave (late June 2026) — worst ever
     recorded for the continent; UK/France/Switzerland June records broken;
     code-red alerts; 55+ deaths in France; large Indian diaspora in UK/Europe.
     NOT covered.
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
load_env(os.path.expanduser('~/workspace/.env.supabase'))
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


# ── Commons relevance gate (see AGENTS.md) ──
_COMMONS_STOP = set("""a an the of for and or to in on at by with from into over under
this that these those is are was were be been being it its as new news photo
image picture file svg png jpg jpeg people person year day man woman men women
city street view scene general world global national international his her their
""".split())

def commons_relevance_ok(title, keywords):
    """Require >=1 distinctive keyword (len>=4) to appear in the Commons file title."""
    if not title:
        return False
    t = title.lower()
    kws = [k.lower() for k in keywords if len(k) >= 4 and k.lower() not in _COMMONS_STOP]
    if not kws:
        return True
    return any(k in t for k in kws)


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


def pick_commons(queries, keywords, min_width=900):
    """Pick a Commons image, applying the relevance gate against keywords."""
    for q in queries:
        commons = fetch_wikimedia_commons_images(q)
        if not commons:
            continue
        # prefer wide JPEGs that pass relevance gate
        for c in commons:
            if (c["width"] >= min_width
                    and c["original_url"].lower().endswith((".jpg", ".jpeg"))
                    and commons_relevance_ok(c.get("title", ""), keywords)):
                return c["url"], c.get("title", "")
        # fallback: any that passes the relevance gate
        for c in commons:
            if commons_relevance_ok(c.get("title", ""), keywords):
                return c["url"], c.get("title", "")
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


# ─── Article 1: India resumes tourist visas for Bangladesh ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: India resumes tourist visas for Bangladesh")
    print("="*60)

    slug = "india-resume-tourist-visa-bangladesh-june-28-2026-dinesh-trivedi-dhaka-ivac-two-year-suspension-20260626"
    headline = "After Nearly Two Years, India Reopens Its Doors to Bangladeshi Tourists"
    subheadline = "From June 28, Bangladeshis can once again apply for Indian tourist visas at five centres across the country, ending a suspension that began amid the 2024 upheaval. The thaw is the clearest sign yet that ties between the two neighbours are mending."

    body = """For nearly two years, a Bangladeshi family wanting to visit the Taj Mahal, shop in Kolkata or take a child to a Chennai hospital had to navigate a closed door. India's tourist visa counters in Dhaka had gone dark in the summer of 2024, casualties of a political rupture that sent relations between the two neighbours into a deep freeze. On Thursday, that door swung back open.

India will resume issuing tourist visas to Bangladeshi citizens from June 28, the country's newly appointed High Commissioner to Bangladesh, Dinesh Trivedi, announced at a briefing at the Indian Visa Application Centre in Dhaka on June 25. "I am very happy to announce that we are resuming our normal visa applications for tourist visas, which can be submitted from Sunday, 28th June 2026," Trivedi said, adding that medical and humanitarian visas would continue to be facilitated on urgent grounds.

## Five Centres Reopen

Tourist visa services will be available through five Indian Visa Application Centres — in Dhaka, Rajshahi, Chattogram, Sylhet and Khulna — with officials indicating plans to expand further in time. The announcement came just hours after Trivedi formally presented his credentials to Bangladesh's President Mohammed Shahabuddin at the Bangabhaban presidential palace, having arrived in Dhaka by road through the Petrapole-Benapole border crossing on June 12.

The resumption marks the end of a suspension that began on August 5, 2024, when the Indira Gandhi Cultural Centre in Dhaka's Dhanmondi neighbourhood was ransacked and set ablaze and five visa centres came under attack amid the unrest that followed the ouster of pro-India Prime Minister Sheikh Hasina. Indian personnel working on development projects were threatened. Through it all, the High Commission kept its centres running for medical and emergency cases, issuing more than 1,500 visas a day across every category except tourism.

## A Relationship Slowly Mending

The reopening is the most concrete step yet in a careful diplomatic thaw. Ties had soured badly during the 18-month interim administration of Muhammad Yunus, strained by India's hosting of the deposed Hasina and by rhetoric from Dhaka about India's northeast that New Delhi viewed as provocative. The situation began to stabilise after Tarique Rahman of the Bangladesh Nationalist Party was sworn in as Prime Minister in February 2026, replacing the interim setup with an elected government that has pursued a more pragmatic, trade-focused engagement with India.

A visit by Bangladesh's Foreign Minister to New Delhi in April served as what one official described as an "ice-breaker," the first high-level engagement since the transition and the opening that paved the way for restored consular services. Bangladesh had already resumed issuing visas to Indians across all categories earlier in the year, granting more than 13,000 since reopening around February 20; India's restart had lagged, running at just 15 to 20 percent of pre-crisis capacity. Thursday's announcement closes much of that gap.

The human toll of the freeze shows up starkly in the numbers. The flow of Bangladeshi visitors to India collapsed from 2.12 million in 2023 to just 470,000 in 2025 — a market that India, long the top medical-tourism and shopping destination for middle-class Bangladeshis, was keen to recover. Kolkata's hospitals and hotels, Chennai's medical districts and the markets of the border states had all felt the absence.

## Why It Matters for the Diaspora

For the South Asian diaspora, the reopening resonates well beyond tourism statistics. Families straddling the India-Bangladesh frontier — and the large Bangladeshi-origin communities in Britain, the United States, Canada and the Gulf with relatives on both sides — have spent two years watching a once-routine border harden. Cross-border visits for weddings, funerals and family reunions, the connective tissue of the eastern subcontinent's diaspora, became tangled in geopolitics.

A normalised visa regime also lowers the friction for the broader desi world, where Indians and Bangladeshis abroad often share neighbourhoods, businesses and places of worship, and where regional stability tends to register quickly in community sentiment. Trivedi framed the decision as one expected to ease mobility, strengthen bilateral ties and revive tourism flows. For now, Indian authorities have not detailed whether new requirements or restrictions will apply to applicants under the resumed programme — a question that will matter to the many families already eyeing a long-delayed trip. But after two years of a closed counter, the simple fact that applications reopen on Sunday is, for them, the headline that counts."""

    img_url, ititle = pick_commons(
        [
            "Indian High Commission Dhaka",
            "India Bangladesh border Benapole Petrapole",
            "Dhaka cityscape Bangladesh",
            "Indian visa stamp passport",
        ],
        keywords=["dhaka", "bangladesh", "india", "commission", "border", "benapole", "petrapole", "visa", "passport"],
    )
    img_attribution = "Wikimedia Commons"
    img_caption = "India will resume issuing tourist visas to Bangladeshi nationals from June 28, 2026, ending a nearly two-year suspension"

    if not img_url:
        px = fetch_pexels_image("passport visa stamp travel document")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "India reopens tourist visa applications for Bangladeshi nationals from June 28, 2026"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diplomacy",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "The Business Standard / TBS News (tbsnews.net, 25 June 2026) \u2014 'India to resume tourist visas for Bangladeshis from 28 June': newly appointed Indian High Commissioner to Bangladesh Dinesh Trivedi announced at a briefing at the Indian Visa Application Centre in Dhaka on 25 June that India will resume issuing tourist visas to Bangladeshi citizens from 28 June, ending a suspension in place for nearly two years; services available through five IVACs in Dhaka, Rajshahi, Chattogram, Sylhet and Khulna; Trivedi presented his credentials to President Mohammed Shahabuddin; arrived in Dhaka on 12 June; India suspended tourist visa services following the 5 August 2024 political transition, limiting issuance to medical and business travellers.",
            "Bharat Horizon (bharathorizon.com, 25 June 2026) \u2014 'India to Resume Tourist Visas for Bangladesh from June 28: High Commissioner Trivedi': Trivedi announced tourist visas resume Sunday, June 28, 2026 at five visa application centres including the IVAC at Jamuna Future Park; quotes him saying medical visas continue on humanitarian grounds; background that on 5 August 2024 the Indira Gandhi Cultural Centre in Dhanmondi was ransacked and set on fire and five IVACs were attacked; High Commission continued issuing over 1,500 visas daily across all categories except tourist; Trivedi arrived via the Petrapole-Benapole border on June 12 and presented credentials at Bangabhaban.",
            "The Business Standard / TBS News (tbsnews.net, 3 May 2026) \u2014 'India, Bangladesh move towards full resumption of visa services': Bangladesh has resumed issuing visas to Indians across all categories and issued more than 13,000 since restoring operations around 20 February 2026; Indian visa services for Bangladeshis were operating at 15-20% of pre-December 2025 capacity; the April visit of Bangladesh's Foreign Minister to New Delhi served as an ice-breaker; ties recalibrated under PM Tarique Rahman (BNP), sworn in February 2026; Bangladeshi visitors to India fell from 2.12 million in 2023 to 470,000 in 2025.",
            "Inshorts (inshorts.com, 25 June 2026) \u2014 'Why had India temporarily restricted tourist visas to Bangladeshis?': India is resuming tourist visas for Bangladeshis from June 28, lifting a restriction imposed for nearly two years owing to political unrest and attacks on Indian diplomatic establishments in 2024; ties deteriorated after the ouster of pro-India PM Sheikh Hasina."
        ]),
        "diaspora_angle": "India's decision to resume tourist visas for Bangladeshi nationals from June 28, after a nearly two-year suspension, signals a thawing of relations that resonates across the eastern subcontinent's diaspora \u2014 families straddling the India-Bangladesh frontier, and the large Bangladeshi-origin communities in Britain, the US, Canada and the Gulf with relatives on both sides, can again plan the cross-border visits for weddings, funerals and reunions that had been tangled in geopolitics since 2024.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Europe's record-breaking heatwave ───

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Europe's record-breaking killer heatwave")
    print("="*60)

    slug = "europe-record-heatwave-june-2026-uk-france-code-red-deaths-indian-diaspora-climate-change-20260626"
    headline = "Europe Is Living Through Its Worst Heatwave on Record. Millions of Indians Live Right In It."
    subheadline = "Britain, France and Switzerland have all broken June temperature records as a 'killer' heatwave scientists link to climate change grips the continent. With dozens dead and code-red alerts from London to the Netherlands, the diaspora is feeling the heat too."

    body = """The continent that millions of Indians now call home is buckling under heat the likes of which it has never recorded. From Britain and France to Germany, Italy, Austria and Serbia, Western Europe has spent the past week sizzling under what scientists are calling the most severe heatwave ever recorded for the region — a slow-moving dome of high pressure that has shattered temperature records, killed dozens, melted road surfaces and forced cultural landmarks to close.

The numbers are startling. France recorded its hottest day on record on June 24, with a national average temperature of 30.0°C, beating a mark set only the day before; in the western town of Pulluau, the mercury hit 43.8°C. Britain logged its hottest June temperature in half a century, while Switzerland topped 37°C for the first time ever in June, reaching 38°C in Basel. Paris hit a June record of 40.9°C. Scientists at the World Weather Attribution group said the heatwave would have been "virtually impossible" without human-caused climate change, which has made the soaring night-time temperatures roughly 100 times more likely than two decades ago.

## A Deadly Toll

The heat has turned lethal across the continent. At least 55 deaths linked to the heatwave have been reported in France, where authorities counted around 40 drownings as people sought relief in rivers and lakes, and two young children died in a hot car. Spain's mortality monitoring system attributed more than 200 deaths to the heat over four days, as the country recorded its hottest late-June days on record. Italy reported heat-related deaths including a vineyard worker and a farmhand, and put 16 cities on its highest alert.

Authorities have responded with measures rarely seen in Europe. Britain's Met Office extended a red extreme-heat warning — only the second such warning in its history — into a record third straight day. The Netherlands declared a rare "code red" for almost the entire country and shut many schools. Paris banned drinking alcohol in public and asked organisers of major events, including a music festival, to cancel. In Germany, extreme heat buckled and ruptured the A2 motorway, damaging up to 30 vehicles. French nuclear plants, which cannot draw enough cooling water when rivers run warm, cut output, and hundreds of thousands of birds died on poultry farms in Brittany.

## Why It Matters for the Diaspora

For the Indian diaspora, this is not a distant news story unfolding somewhere else — it is the weather outside their own windows. The United Kingdom alone is home to roughly two million people of Indian origin, with large communities in London, the Midlands and the north; France, Germany, Italy and the Netherlands host hundreds of thousands more, from students and tech workers to nurses, shopkeepers and retirees. Many live in housing built for a cool, damp climate, where air conditioning is rare and homes are designed to trap heat rather than shed it.

That mismatch is exactly what makes European heatwaves so dangerous. Unlike in much of India, where homes, workplaces and routines are built around the expectation of brutal summer heat, large parts of northern Europe have little physical or behavioural defence against it. Elderly diaspora members, often the most vulnerable, may have spent decades acclimatising to mild British or continental summers. Students sitting exams in un-air-conditioned halls, delivery riders and construction workers on the job, and shop owners without cooling all face real risk when temperatures climb past 38°C.

There are practical knock-ons too. Rail operators warned passengers to avoid travel as tracks risked buckling; flights and power supplies were disrupted; schools closed or moved to half-days, upending the routines of working parents. For families with relatives back in India watching the headlines, the role reversal is hard to miss — it is the relatives in supposedly temperate Europe, not those in Delhi or Ahmedabad, fielding worried calls about the heat.

Scientists are blunt about what comes next. Europe is the world's fastest-warming continent, and researchers say record temperatures will be "exceeded more and more frequently" as warming continues. Of more than 800 European cities studied, nearly half have recorded or are forecast to record their highest-ever heat stress for late June. For a diaspora that chose Europe in part for its temperate calm, the message of this week is unsettling: the summers they moved into are not the summers they will live through."""

    img_url, ititle = pick_commons(
        [
            "heat wave Europe sun thermometer",
            "Paris summer Eiffel Tower heat",
            "London summer heat people",
            "drought dry ground sun",
        ],
        keywords=["heat", "heatwave", "summer", "drought", "sun", "thermometer", "paris", "london", "europe"],
    )
    img_attribution = "Wikimedia Commons"
    img_caption = "Western Europe is enduring its worst recorded heatwave, with Britain, France and Switzerland all breaking June temperature records in late June 2026"

    if not img_url:
        px = fetch_pexels_image("heatwave sun hot summer city")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A record-breaking heatwave has gripped Western Europe, breaking June temperature records and prompting code-red alerts"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "climate",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters (reuters.com, 26 June 2026) \u2014 'Europe on high alert as killer heat spreads': health authorities across Europe on high alert as a killer heatwave progresses, prompting alcohol bans in France and cracking road surfaces in Germany; scientists said the heatwave was the worst recorded for Europe; at least 55 deaths linked to the heatwave reported in France, where Paris hit 40.9C on Wednesday; Britain's Met Office extended a red heat alert into Friday, the first time issued for three consecutive days; a rare 'code red' alert issued for almost the whole of the Netherlands with schools closed; extreme heat buckled the A2 motorway in eastern Germany, damaging up to 30 vehicles.",
            "Reuters (reuters.com, 25 June 2026) \u2014 'Britain, Switzerland break June temperature record as deadly heatwave grips Europe': temperatures in Britain and Switzerland hit record June highs on Thursday; Paris endured a June record of 40.9C on Wednesday; southwest England reached 36.7C, provisionally the hottest June day recorded in Britain; Switzerland rose above 37C for the first time in June, hitting 38C in Basel; Paris police banned public drinking from Friday; French Health Minister Stephanie Rist warned of rising emergency-ward visits.",
            "United Nations News / WMO (news.un.org, 25 June 2026) \u2014 'Europe heatwave breaks records as UN agencies ramp up health warnings': France recorded its hottest day on record on 24 June with a national average of 30.0C, beating a record set the previous day; Pulluau reached 43.8C; top-level red alerts for a record 58 departments; WMO noted around 40 drowning deaths in France; Spain recorded its hottest June days on record (23-24 June) with temperatures above 40C; the UK Met Office issued a red extreme heat warning for 24-25 June with a provisional new June high of 36.1C at Gosport; Germany and three Swiss cities (Geneva, Basel, Zurich) under red alerts.",
            "Reuters (reuters.com, 26 June 2026) \u2014 'Europe's heatwave virtually impossible without climate change, scientists say': the World Weather Attribution group said the record-breaking heatwave would have been virtually impossible without human-caused climate change, which made the week's soaring night-time temperatures 100 times more likely than two decades ago; 'this heatwave is the most severe ever recorded' over the region studied; of more than 800 European cities analysed, 45% recorded or are forecast to record their highest heat stress levels for late June; Europe is the world's fastest-warming continent.",
            "CNN (cnn.com, 25 June 2026) \u2014 'Europe endures another day of record-breaking heat, as countries warn it's already killed hundreds': over four days 212 people in Spain died due to the heatwave per the MoMo mortality monitoring system; at least 48 people drowned in France over a week seeking relief and three children found dead in hot cars; Italy reported at least five heat-related deaths; red alerts covered 72 of France's 96 mainland regions; the UK remained under a rare red extreme heat warning extended into Friday for a record three straight days."
        ]),
        "diaspora_angle": "Europe's worst recorded heatwave is the weather outside the windows of millions of Indians who now call the continent home \u2014 roughly two million people of Indian origin in the UK alone, plus hundreds of thousands across France, Germany, Italy and the Netherlands \u2014 many living in homes built for a cool climate, without air conditioning, leaving elderly relatives, students in un-air-conditioned exam halls and outdoor workers acutely exposed as records fall and code-red alerts spread.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    print("Videshi News Writer \u2014 2026-06-26 10:30 UTC run")
    id1 = write_article_1()
    id2 = write_article_2()
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Article 1 (India resumes Bangladesh tourist visas): {'OK id=' + str(id1) if id1 else 'FAILED'}")
    print(f"Article 2 (Europe record heatwave): {'OK id=' + str(id2) if id2 else 'FAILED'}")
