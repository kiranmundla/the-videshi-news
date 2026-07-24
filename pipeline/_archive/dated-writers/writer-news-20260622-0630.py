#!/usr/bin/env python3
"""
Videshi News Writer — June 22, 2026 (06:30 UTC run)
2 NEW articles:
  1. Explosion at Qatar's Ras Laffan / Barzan gas plant — 54 injured, 18 missing;
     Indians are the largest expat group in Qatar, many in oil & gas (diaspora-safety)
  2. India's monsoon starts weak — ~38% rain deficit, Mumbai water rationing,
     kharif sowing down, food-inflation risk for the diaspora (economy)
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
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
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
            return pick["url"]
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


# ─── Article 1: Qatar Ras Laffan / Barzan explosion ──────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Qatar Ras Laffan / Barzan gas plant explosion")
    print("="*60)

    slug = "qatar-ras-laffan-barzan-gas-plant-explosion-54-injured-18-missing-indian-workers-20260622"
    headline = "An Explosion Tore Through Qatar's Biggest Gas Hub. The Search Is On for 18 Missing in a City Built by Indian Hands."
    subheadline = "A blast and fire at the Barzan plant in Ras Laffan left 54 injured and 18 missing on Sunday night. In a country where Indians are the single largest community, the diaspora is now waiting on the casualty list."

    body = """A loud boom rolled south across the desert toward Doha on Sunday evening, and in some accounts was felt as far away as Bahrain. It came from Ras Laffan Industrial City, the sprawling complex on Qatar's northern coast that is the beating heart of the country's liquefied natural gas industry. An explosion, followed by fire, had torn through the Barzan gas plant during what QatarEnergy described as the start-up of operations.

By Monday morning, the toll was sobering. Qatar's Interior Ministry said 54 people had been injured and 18 were missing, with the Qatari International Search and Rescue Group working alongside civil defence teams to find them. QatarEnergy said emergency crews had brought the fire under control. The ministry attributed the blast to a "technical accident" and stressed there was no gas leak that threatened public safety. A source told Reuters the incident was the result of an "operational error" during restart.

## A Plant Already Wounded by War

The Barzan facility is not just any plant. Ras Laffan is the core of Qatar's LNG processing operations, and Qatar is one of the world's top exporters of the fuel, alongside the United States, Australia and Russia. The complex had already been badly damaged earlier this year during the US-Iran war, with QatarEnergy's chief executive Saad al-Kaabi previously estimating that a full recovery could take three to five years. Sunday's explosion struck precisely as the company was trying to bring operations back online.

That timing matters far beyond Qatar's borders. Global energy markets remain jittery after a spring of conflict in the Gulf, and any fresh disruption at a facility of Ras Laffan's scale risks rippling into LNG and gas prices worldwide. QatarEnergy did not say whether the explosion had damaged the plant itself, which feeds gas to Qatar's domestic market.

## Why the Diaspora Is Holding Its Breath

For Indian families, the more urgent question is not about markets but about people. Indians are the single largest community in Qatar — official Indian government figures put the number at roughly 830,000, and independent 2026 estimates place it near 730,000, around a fifth of the entire population. They are not a community on the margins of Qatar's economy; they are woven through its construction sites, its services, and crucially its oil and gas sector, the very industry where Sunday's blast occurred.

Ras Laffan and Qatar's energy plants employ large numbers of South Asian workers in operations, maintenance and contracting roles. As the names of the injured and the 18 missing are confirmed in the coming days, it is statistically likely that Indian nationals are among them. That is the quiet arithmetic the diaspora understands instinctively whenever an industrial accident strikes the Gulf: in a workforce this heavily Indian, no major incident stays a foreign story for long.

It is a familiar anxiety. The Gulf states are home to roughly nine million Indian workers, and the chain of events after an accident — the scramble for news, the calls to embassies, the wait for an official casualty list, the question of compensation and repatriation — has played out many times before. India's mission in Doha typically activates a helpline and coordinates with Qatari authorities in such cases.

## What Comes Next

The immediate priority is the search for the 18 missing workers, which was ongoing as of Monday. Qatari authorities have promised an investigation into what caused a restart to end in catastrophe. For the energy industry, the focus will be on whether the blast sets back Ras Laffan's already-lengthy recovery and what that means for an LNG market still on edge.

For hundreds of thousands of Indian families with a husband, a son or a brother working in Qatar, the next few days will be spent watching the official statements for names — and hoping not to find one they recognise. The Barzan plant supplies gas to keep Qatar running. The people who run it, in large part, came from somewhere else."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = pick_commons([
        "Ras Laffan Qatar LNG",
        "liquefied natural gas plant Qatar",
        "LNG terminal gas processing plant",
        "natural gas refinery industrial plant"
    ])
    img_caption = "An LNG processing facility; Qatar's Ras Laffan complex is the core of its gas industry"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("liquefied natural gas plant industrial")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "An industrial gas processing plant"

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
            "Reuters \u2014 Fifty-four injured and 18 missing after explosion at Qatar LNG site, authorities say (June 22, 2026): explosion and fire during start-up at Barzan local gas supply facility in Ras Laffan; Interior Ministry says 54 injured, 18 missing; attributed to technical accident; no leak threatening public safety; search ongoing",
            "QatarEnergy statement (via Reuters/ZeroHedge) \u2014 'operational incident' during start-up of operations at Ras Laffan Industrial City resulted in explosion and fire at Barzan local gas supply facility; emergency teams deployed; fire brought under control",
            "AInvest / Reuters \u2014 Qatar's Ras Laffan Gas Terminal Blast: blast during efforts to restart exports halted after earlier damage; CEO Saad al-Kaabi previously estimated 3-5 year recovery; Qatar among top global LNG producers; market-volatility risk",
            "India Ministry of External Affairs (Rajya Sabha UQ 1996, Dec 2024) \u2014 estimated 830,491 Indians in Qatar, the single largest community; Global Media Insight 2026 estimate ~0.73 million Indians (21.8% of population)"
        ]),
        "diaspora_angle": "Indians are the single largest community in Qatar \u2014 roughly 730,000 to 830,000 people, about a fifth of the population, with a heavy presence in the oil, gas and construction sectors where Sunday's deadly blast occurred, leaving hundreds of thousands of families waiting on the casualty list.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: India's weak monsoon / rain deficit ──────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: India's weak monsoon start, rain deficit")
    print("="*60)

    slug = "india-weak-monsoon-rain-deficit-mumbai-water-rationing-kharif-sowing-food-inflation-20260622"
    headline = "India's Monsoon Was Supposed to Break the Heat. Three Weeks In, the Rain Gauges Are Still Running a Third Empty."
    subheadline = "Cumulative rainfall is running nearly 38% below normal, Mumbai is rationing water, and farmers are delaying planting. For a diaspora that watches India's food prices and the rupee, a weak start to the monsoon is a number worth tracking."

    body = """Every June, India waits for the same thing: the southwest monsoon, the four-month rainy season that fills the reservoirs, waters roughly half the country's farmland, and finally breaks the brutal pre-monsoon heat. This year, three weeks into the season, the rain has largely failed to show up.

Cumulative rainfall as of mid-June stood at about 46 millimetres against a normal of 74 millimetres — a deficit of roughly 38%, according to a research note from 360 ONE Capital Research. Twenty-two of India's 36 meteorological subdivisions have recorded deficient rainfall. Central India has been the hardest hit, running 62% below normal, with eastern India 44% short. Forecasters warn that if the dry spell holds, June's overall shortfall could approach 45%. The India Meteorological Department's first long-range forecast already pegs the full season at 90–92% of the long-period average, placing it in the "below normal" band — and on course to be among the weakest monsoons in over a decade.

## A City Rationing Its Water

The most visible casualty so far is Mumbai. India's financial capital has just lived through its driest June in more than a decade, and the seven lakes that supply the city of 13 million had fallen to barely 10% of capacity — around 40 days of water. Authorities responded by cutting off supply to construction sites and slashing industrial and commercial use by 20%, on top of an earlier 10% cut imposed in May. Maharashtra as a whole received some 75% less rain than normal in the first half of the month.

The monsoon's advance has been sluggish. Meteorologists point to a neutral Indian Ocean Dipole that is neither helping nor hurting, and to El Niño conditions that are expected to weaken this year's rains. IIT Kanpur's Raghu Murtugudde noted that moisture is adequate but clouds are not condensing efficiently over eastern and northeastern India. The IMD expects the monsoon to push into Odisha, Jharkhand, Bihar and parts of Chhattisgarh over the coming days, but to stay weak until at least June 24.

## The Worry on the Farm

The timing is what makes a weak June dangerous. June is the sowing window for kharif crops — paddy, maize, cotton, pulses — and in rain-fed belts, farmers make planting decisions inside a narrow two-to-three-week window. As of mid-June, total kharif sowing was down nearly 4% year-on-year, with pulses and cotton areas contracting sharply as farmers held back. In Maharashtra's sugar belt, some growers are switching from water-hungry cane to soybeans and pulses, and India is now expected to struggle to export sugar for years.

None of this guarantees drought. The monsoon often starts weak and recovers strongly in July and August, and reservoir buffers and resilient rice sowing offer some cushion. But a prolonged shortfall feeds quickly into food prices: during the 2023 monsoon shock, vegetables turned 37% more expensive. With the after-effects of the Gulf conflict still pushing up fuel and fertiliser costs, a weak harvest would land on an economy with little slack.

## Why It Matters to the Diaspora

For NRIs, the monsoon is one of those Indian variables that quietly governs the numbers they actually watch. A weak season raises food inflation, and food inflation is the single biggest driver of India's headline inflation — which in turn shapes the Reserve Bank of India's interest-rate decisions and, ultimately, the rupee. Every remittance sent home and every NRI deposit parked in an Indian bank is valued in that currency.

There is a household-level stake too. Families with parents, property or businesses in India feel a bad monsoon in the price of vegetables, the cost of water tankers in cities like Mumbai, and the squeeze on rural relatives who depend on the harvest. And for the millions of diaspora households with roots in farming districts, the question of whether the rains arrive by July is not an abstraction on a weather map — it is whether the family land turns a profit this year. For now, India is doing what it does every June: watching the sky, and waiting."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = pick_commons([
        "monsoon rain India",
        "Indian farmer paddy field monsoon",
        "monsoon clouds India agriculture",
        "drought dry reservoir India"
    ])
    img_caption = "Monsoon rains over India; a weak start has left cumulative rainfall running well below normal"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("monsoon rain india farmer field")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Monsoon rains over a field in India"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "360 ONE Capital Research (via Devdiscourse) \u2014 Weak start to monsoon clouds Kharif season outlook (June 2026): cumulative rainfall June 17 at 46.2mm vs normal 74.3mm, a 38% deficit; weekly rain 48% below LPA; 22 of 36 subdivisions deficient; central India -62%, eastern India -44%; kharif sowing -3.9% YoY, pulses -43.2%, cotton -28%, rice +28.4%",
            "Reuters \u2014 India's Mumbai rations water supply as June rainfall hits 12-year low: seven supply lakes at 10.35% capacity (~40 days' water); construction supply cut, industrial/commercial use cut 20%; Maharashtra 75% below normal in first 16 days of June; India facing weakest monsoon in 11 years",
            "Dainik Bhaskar (English) \u2014 India Rainfall Deficit 38%: neutral IOD; IIT Kanpur's Raghu Murtugudde says moisture adequate but cloud condensation inefficient; IMD expects monsoon advance into Odisha/Jharkhand/Bihar but weak until June 24; June deficit could reach 45%",
            "Reuters \u2014 India likely won't export sugar for years as El Nino, ethanol squeeze supply: El Nino forecast to weaken monsoon to lowest in 11 years; June rain >40% below average; farmers delaying planting and switching crops; output cut to 27.9M tons below ~28.5M consumption",
            "IMD first long-range forecast (via Bhaskar explainer) \u2014 season projected at 90-92% of long period average ('below normal'); past 37% vegetable price spike cited from 2023 monsoon shock"
        ]),
        "diaspora_angle": "A weak monsoon drives up India's food inflation \u2014 the biggest component of headline inflation \u2014 which shapes interest rates and the rupee, the currency that values every NRI remittance and deposit, and hits families back home through costlier vegetables, water shortages and rural incomes tied to the harvest.",
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
