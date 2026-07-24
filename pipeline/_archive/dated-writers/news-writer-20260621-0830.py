#!/usr/bin/env python3
"""
Videshi News Writer — June 21, 2026 (08:30 UTC run)
2 NEW articles:
  1. US-Iran peace talks open at Buergenstock; JD & Usha Vance, Pakistan mediation; India's oil stake (news / geopolitics)
  2. Europe's record June heatwave — France alcohol ban, 40C+; diaspora travel/student angle (news / travel-safety)
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


# ─── Article 1: US-Iran peace talks open at Buergenstock ──────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: US-Iran peace talks open / Buergenstock")
    print("="*60)

    slug = "us-iran-peace-talks-open-buergenstock-vance-pakistan-mediation-hormuz-india-oil-20260621"
    headline = "The Talks That Will Decide India's Oil Bill Just Opened on a Swiss Mountaintop"
    subheadline = "US Vice President JD Vance and Iran's chief negotiator sat down on Sunday at the Buergenstock resort to turn a fragile 60-day ceasefire into a lasting peace \u2014 with the Strait of Hormuz, a fifth of the world's oil, and the energy security of 1.4 billion Indians hanging on the outcome."

    body = """High in the Swiss Alps on Sunday morning, on a fog-wrapped mountaintop reachable only by a single road threaded through armed checkpoints, the two governments that have spent four months at war sat down to try to end it for good. The stakes at the Buergenstock resort are global, but for India \u2014 and for the tens of millions of its citizens scattered across the Gulf \u2014 they are also intimately personal: the price of a litre of petrol, the safety of a million workers, and the cost of the cooking gas that lights a stove in Kerala all run, in some measure, through the room where these talks are taking place.

US Vice President JD Vance, accompanied by Second Lady Usha Vance, led the American delegation, which also includes envoys Steve Witkoff and Jared Kushner. Iran's team, headed by chief negotiator and parliament speaker Mohammad Baqer Qalibaf and Foreign Minister Abbas Araqchi, arrived with senior security, central bank and oil officials in tow. The resort is owned by Qatar, one of the war's principal mediators, and helicopters circled overhead as Pakistani Prime Minister Shehbaz Sharif and army chief Field Marshal Asim Munir joined the proceedings.

## From Ceasefire to Settlement

The two sides reached the table on the strength of a 60-day ceasefire and an interim deal brokered by Pakistan and signed on Wednesday by Presidents Donald Trump and Masoud Pezeshkian, ending an almost four-month war that began with US and Israeli strikes on February 28. "I think we're going to hopefully make progress on the nuclear issue, make progress on the Lebanon ceasefire issue," Vance told reporters before departing Maryland, predicting "a couple days of talks."

But the ground beneath the negotiations is unsteady. On Saturday, Iran's Islamic Revolutionary Guard Corps declared the Strait of Hormuz shut in retaliation for Israeli strikes in Lebanon, warning that ships approaching the waterway would be at risk. The US military flatly contradicted the claim: Central Command said 55 merchant vessels carrying more than 17 million barrels of oil transited the strait on Saturday alone, and vowed American forces would keep commercial traffic moving. Vance, in a Fox News interview, said he had "seen no evidence" of a closed strait.

## Why Hormuz Is India's Problem

That gap between Tehran's words and the tankers' movements matters enormously to New Delhi. The Strait of Hormuz is the artery through which a fifth of the world's oil flows, and India \u2014 the world's third-largest crude importer \u2014 draws a large share of its energy through it. Every wobble in the strait's status feeds directly into the price India pays at the pump and the subsidy bill its state oil companies absorb. Indian refiners have spent the war quietly rerouting and diversifying supply, but there is no substitute for a Hormuz that simply stays open.

A complicating thread runs through the talks themselves. Mohammad Mokhber, an adviser to Iran's supreme leader, accused Washington of failing to implement the first of the deal's 14 points \u2014 a ceasefire "on all fronts," including Lebanon \u2014 and warned that as long as the agreement remained only on paper, Middle East energy would stay halted. Trump, for his part, mused on social media about the United States one day levying a toll on strait passage "for services rendered as the Guardian Angel to the countries of the Middle East" should peace fail, though he said no toll would apply during or after the 60-day window if a deal holds.

## Why It Matters for the Diaspora

For the roughly nine million Indians living and working across the Gulf, the Buergenstock talks are not abstract diplomacy. India's Ministry of External Affairs has overseen one of the largest repatriation exercises in its history since the war began, facilitating well over a million passenger journeys home from West Asia, evacuating nationals from Iran via Armenia and Azerbaijan, and rescuing stranded seafarers. A durable peace would let the construction workers of the UAE, the nurses of Saudi Arabia and the engineers of Qatar exhale \u2014 and let the families who depend on their remittances stop watching the news with their hearts in their throats.

There is also the matter of the remittance economy itself. The Gulf is the single largest source of the money Indians abroad send home, and prolonged instability threatens both the jobs that generate those flows and the exchange rates that govern their value. A breakthrough in Switzerland would steady all of it. A breakdown \u2014 with the IRGC's threat hardening into a real closure \u2014 would send oil prices spiking, the rupee sliding, and a fresh wave of anxiety through diaspora households from Dubai to Doha. On a Swiss mountaintop this weekend, in other words, a great deal of the Indian world is holding its breath."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "The Buergenstock resort above Lake Lucerne, Switzerland, venue for the US-Iran peace talks that opened on June 21"
    img_attribution = "Wikimedia Commons"

    for q in ["Buergenstock resort Switzerland", "Buergenstock Lucerne", "oil tanker Strait of Hormuz", "Strait of Hormuz"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            t = commons[0]["title"].lower()
            if "hormuz" in t or "tanker" in t:
                img_caption = "An oil tanker transits the Strait of Hormuz; a fifth of the world's oil passes through the waterway central to the US-Iran talks"
            break

    if not img_url:
        px = fetch_pexels_image("oil tanker sea")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "An oil tanker at sea; the Strait of Hormuz carries a fifth of global oil supply"

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
            "Reuters \u2014 Top-level US-Iran peace talks to begin at Swiss resort with Hormuz in spotlight (Vance, Qalibaf, Araqchi, Witkoff, Kushner; Usha Vance; Pakistan PM Sharif and Field Marshal Munir; Qatar-owned Buergenstock; 60-day ceasefire; IRGC declares Hormuz shut; CENTCOM 55 ships/17m barrels; Trump toll remarks; Mokhber 14-point claim)",
            "Reuters \u2014 Indian shares extend gains on US-Iran peace deal (Brent crude, oil-importing India, market reaction)",
            "The Indian EYE / MEA \u2014 India repatriation from West Asia; evacuation of ~1,200 nationals from Iran via Armenia and Azerbaijan; over 11.6 lakh passengers facilitated since February 28; seafarers rescued",
            "newkerala.com \u2014 India Repatriates Over 11.6 Lakh Citizens from West Asia (MEA inter-ministerial briefing, Aseem Mahajan)"
        ]),
        "diaspora_angle": "The Strait of Hormuz carries a large share of India's imported oil and sits beside the Gulf states where roughly nine million Indians live and work, so whether the Buergenstock talks produce a durable peace will shape India's fuel prices, the rupee, and the safety and remittances of the diaspora's largest community.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Europe's record June heatwave ─────────────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Europe's record June heatwave")
    print("="*60)

    slug = "europe-record-june-heatwave-france-alcohol-ban-40c-diaspora-travellers-students-20260621"
    headline = "Europe Is Cooking. If Your Summer Plans Run Through Paris or Rome, Read This First."
    subheadline = "A punishing heatwave pushed France to ban festival alcohol, shut a Spanish fan zone and send Italy's tourists underground this weekend, with temperatures nearing 41C \u2014 a warning to the diaspora's summer travellers, parents visiting students, and anyone weighing a European campus."

    body = """Europe spent the longest weekend of the year sweltering. As temperatures climbed toward record levels across the continent, France banned alcohol at public festivals, Germany issued nationwide warnings, Spain shut a World Cup fan zone, and in Rome the tourists who had flown in for a postcard summer found themselves queuing under a blazing sun and ducking into ancient underground chambers just to cool down. For the millions of Indians who treat the European summer as a season of travel \u2014 to sightsee, to visit children at university, to scout a campus before committing a life's savings to it \u2014 the heat is more than a weather story. It is a planning problem.

France braced for the worst of it. The government expected 35 of its 96 departments to declare red heatwave alerts on Sunday, with temperatures of 39 to 40 degrees Celsius (102 to 104 Fahrenheit) forecast from the southwest through the Paris region into Burgundy, and some areas possibly touching 41C. After a crisis meeting, Prime Minister Sebastien Lecornu pre-emptively banned alcohol consumption at the annual Fete de la Musique festivals and other public events in those 35 regions, while Paris ordered its parks to stay open around the clock so residents and visitors could find air and shade through the night.

## A Continent Under Warning

The alerts spanned borders. Most of Germany was placed under heat warnings, with temperatures approaching 38C and the DWD weather service cautioning that the mix of heat and humidity could spawn severe thunderstorms. Beyond the Alps, Italian towns saw the mercury reach 36 to 37C; visitors queued outside Rome's Colosseum as sightseeing turned into a test of endurance, with some retreating to the cooler spaces beneath the half-hidden remains of the Temple of Claudius. In Bologna, one of the peninsula's hottest cities, people splashed water at the 16th-century Fountain of Neptune and clung to the shade of the porticoes.

In Spain, the football federation closed the giant-screen fan zone it had set up in Madrid's Plaza de Colon, leaving supporters to watch the national team's World Cup match against Saudi Arabia elsewhere \u2014 while the players themselves enjoyed an air-conditioned stadium in Atlanta. Scientists were unequivocal about the trend behind the misery: climate change is making European heatwaves more frequent and more intense, raising the risk of health emergencies and economic disruption with each passing summer.

## The Diaspora's European Summer

For Indian families, this is the season Europe fills up with them. Summer is peak travel time \u2014 the school holidays back home, the long-planned multi-city tour, the pilgrimage to see a son or daughter through their first year at a German or French or Italian university. It is also, increasingly, the season of campus visits, as families redraw their study-abroad maps toward Europe in response to tightening visa rules in the United States, Canada and Australia. A heatwave that turns a walking tour of Paris or a queue at the Colosseum into a health hazard lands squarely on those plans.

The practical advice is the kind that does not always reach travellers used to India's own fierce summers but unprepared for Europe's housing stock, much of which was built without air conditioning. Hydrate aggressively, shift sightseeing to the early morning and evening, and treat the midday hours as time to rest indoors. Elderly parents and young children \u2014 often the very relatives a diaspora trip is built around \u2014 are the most vulnerable to heat stress, and need shade, water and a cool room more than another monument.

## Why It Matters

There is a longer thread here too. As Indian students increasingly choose Germany and other European destinations over the traditional Anglophone trio, families are signing up not just for a different visa regime and a cheaper degree but for a different climate reality \u2014 and a continent that is, summer by summer, growing hotter. The student weighing a Munich or Milan campus, and the parents planning to visit, would do well to factor the new European summer into the decision: the dorms may not be air-conditioned, the heatwaves are arriving earlier and lasting longer, and the romantic image of a temperate European July is quietly being rewritten. For this weekend, at least, the message from Paris, Rome and Madrid was simple: if your summer runs through Europe, plan around the heat, not against it."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "Tourists at Rome's Colosseum; a record June heatwave pushed temperatures across Europe toward 41C this weekend"
    img_attribution = "Wikimedia Commons"

    for q in ["Colosseum Rome tourists summer", "tourists Rome summer heat", "Paris summer heatwave", "Fountain of Neptune Bologna"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            break

    if not img_url:
        px = fetch_pexels_image("tourists european city summer heat")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Tourists in a European city during summer; a record heatwave gripped the continent this weekend"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "travel-safety",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters \u2014 Europe swelters under heatwave, France restricts alcohol consumption (35 of 96 French departments on red alert; 39-41C; PM Lecornu festival alcohol ban; Fete de la Musique; Paris parks open 24h; Germany ~38C DWD warning; Italy 36-37C, Colosseum, Temple of Claudius, Bologna Fountain of Neptune; Spain Plaza de Colon fan zone closed; Spain vs Saudi Arabia in Atlanta)",
            "Reuters \u2014 Bank of France Governor Emmanuel Moulin on the medium-term economic toll of heatwaves",
            "VisaVerge / RBI \u2014 Indian study-abroad shift toward UK, Germany and Europe as US/Canada/Australia visa rules tighten",
            "Scientific consensus cited by Reuters \u2014 climate change making European heatwaves more frequent and intense"
        ]),
        "diaspora_angle": "Summer is peak season for diaspora travel to Europe \u2014 family tours, visits to students, and campus scouting as study-abroad plans shift toward Germany and Europe \u2014 so a record heatwave with 40C+ temperatures and emergency measures across France, Italy and Spain is a direct safety and planning concern for NRI travellers and parents.",
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
