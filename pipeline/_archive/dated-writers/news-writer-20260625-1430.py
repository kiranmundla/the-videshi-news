#!/usr/bin/env python3
"""
Videshi News Writer — June 25, 2026 (14:30 UTC / 07:30 PDT run)
2 NEW articles, dedup-checked against last ~40 news articles:
  1. India-UK Free Trade Agreement (CETA) goes live July 15; Goyal in UK
     June 25-27 for implementation talks. Tariff cuts (Scotch 150->40%,
     cars 100->10%), professional mobility (1,800 chefs/yoga/musicians/yr),
     Double Contribution Convention exempting ~75,000 Indian workers from
     dual social security. NOT covered in existing articles.
  2. Venezuela twin earthquakes (M7.2 + M7.5) near Caracas; thousands feared
     dead, 10,000+ unaccounted. Diaspora angle: Indian-origin community in
     Caribbean/Latin America, oil-market impact on Indian economy. NOT
     covered in existing articles.
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


# \u2500\u2500\u2500 Article 1: India-UK FTA goes live \u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: India-UK FTA (CETA) goes live July 15")
    print("="*60)

    slug = "india-uk-free-trade-agreement-ceta-goes-live-july-15-goyal-london-scotch-cars-double-contribution-20260625"
    headline = "After Three Years of Talks, the India-UK Trade Deal Finally Goes Live July 15 \u2014 and It Quietly Rewrites the Rules for Indian Workers Abroad"
    subheadline = "Cheaper Scotch and British cars grab the headlines, but the deal's real prize for the diaspora is a pact that spares some 75,000 Indian professionals from paying into two countries' social-security systems at once."

    body = """The most consequential part of the India-UK free trade agreement is not the one you will read about first. The Comprehensive Economic and Trade Agreement (CETA), which comes into force on July 15, will eventually make Scotch whisky and Range Rovers cheaper in India and Indian textiles and seafood cheaper in Britain. But buried in the fine print is a provision that matters far more to the millions of Indians who actually move between the two countries for work \u2014 and it has been three years in the making.

India's commerce minister Piyush Goyal arrived in London this week, on a June 25-27 visit, to finalise the implementation arrangements before the deal takes effect. The trip caps a negotiation that began in January 2022, stalled repeatedly over visas, autos and whisky, and was signed only after both governments decided the prize was worth the compromises. It is Britain's most economically significant trade deal since leaving the European Union, and India's most ambitious with a Western economy.

## The Headline Numbers

On paper, the tariff cuts are dramatic. Duties on Scotch whisky and gin will fall from 150% to 75% immediately, and down to 40% over a decade. Tariffs on British cars will drop from over 100% to 10% under a quota system. In the other direction, Britain will scrap duties on roughly 99% of Indian exports by value \u2014 covering textiles, leather, footwear, gems and jewellery, marine products and engineering goods \u2014 sectors that employ millions in India. The two governments estimate the deal will boost bilateral trade by around \u00a325.5 billion ($34 billion) a year by 2040.

For Indian exporters, the labour-intensive sectors are the immediate winners. Indian-made shirts, shoes and shrimp that once carried tariffs of 8% to 12% entering Britain will now arrive duty-free, putting them on a level footing with rivals from Bangladesh and Vietnam that already enjoyed preferential access.

## The Real Prize: The Double Contribution Convention

The provision that has Indian professionals paying attention is the Double Contribution Convention. Until now, an Indian employee posted to Britain on a short-term assignment had to pay into the UK's National Insurance system \u2014 even though they would never claim a British pension \u2014 while often still contributing to India's provident fund back home. They were, in effect, taxed twice for social security on the same income.

Under the new convention, Indian workers seconded to the UK for up to three years, and their employers, will be exempt from British social-security contributions and will pay only in India. New Delhi estimates this will benefit more than 75,000 Indian workers and over 900 employers, saving Indian companies and staff an estimated \u20b94,000 crore (around $480 million). British workers posted to India get the reciprocal benefit. For Indian IT firms that rotate thousands of engineers through British client sites, the savings are substantial \u2014 and the change makes posting Indian talent to the UK markedly cheaper.

## A Door Cracked Open for Skilled Workers

The deal also widens, modestly, the path for Indian professionals to work in Britain. It commits the UK to streamlined visa processing for Indian business visitors, intra-corporate transferees, and \u2014 in a detail that delighted Indian negotiators \u2014 independent professionals such as yoga instructors, classical musicians and chefs, with provision for around 1,800 such specialists a year. It stops well short of the open immigration access India had once sought, and Britain was careful to stress that the deal does not change its points-based immigration system. But for a country that has tightened student and work routes, even a calibrated opening is notable.

## Why It Matters for the Diaspora

The roughly 1.9 million-strong Indian diaspora in Britain \u2014 the country's largest ethnic-minority group \u2014 sits at the centre of this agreement, both as its beneficiaries and as the human bridge that made it politically possible. NRIs who run import-export businesses, restaurants and textile firms will feel the tariff changes directly. Professionals on secondment will keep more of their pay. Families that move between Mumbai and Manchester will find one bureaucratic indignity \u2014 paying twice for a pension you will collect once \u2014 finally removed.

There is symbolism, too. A British-Indian, Rishi Sunak, was prime minister when much of this deal was hammered out; the diaspora's growing economic and political weight is precisely what made a Western government willing to write social-security relief for Indian workers into a treaty. When CETA takes effect on July 15, the cheaper whisky will be the story of the day. The quieter rewrite of how Indians work, save and move between the two countries will be the story of the decade."""

    img_url = fetch_wikipedia_person_image("Piyush Goyal")
    img_attribution = "Wikimedia Commons"
    img_caption = "India's commerce minister Piyush Goyal, in London for talks before the India-UK trade deal takes effect July 15"

    if not img_url:
        img_url, ititle = pick_commons([
            "Piyush Goyal",
            "India United Kingdom flags",
            "London Westminster trade"
        ])

    if not img_url:
        px = fetch_pexels_image("London United Kingdom flag India")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "The India-UK free trade agreement, three years in the making, comes into force on July 15"

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
            "Reuters (reuters.com, June 2026) \u2014 reporting on the India-UK Comprehensive Economic and Trade Agreement (CETA): the deal cuts tariffs on Scotch whisky and gin from 150% to 40% over ten years and on British cars from over 100% to 10% under quotas; Britain removes duties on about 99% of Indian exports by value; both sides estimate bilateral trade rising by around \u00a325.5 billion a year by 2040; the agreement was signed after negotiations that began in January 2022.",
            "The Hindu BusinessLine (thehindubusinessline.com, June 2026) \u2014 coverage of commerce minister Piyush Goyal's UK visit and CETA implementation: the Double Contribution Convention exempts Indian workers seconded to the UK for up to three years from UK social-security (National Insurance) contributions, expected to benefit more than 75,000 Indian workers and over 900 employers and save an estimated \u20b94,000 crore.",
            "Outlook Business (outlookbusiness.com, June 2026) \u2014 'India-UK FTA: What changes for trade and professionals': the deal eases mobility for Indian business visitors, intra-corporate transferees and independent professionals including yoga instructors, classical musicians and chefs, with provision for roughly 1,800 specialists a year; the UK stresses the agreement does not alter its points-based immigration system.",
            "gov.uk / UK Department for Business and Trade (gov.uk, 2026) \u2014 official statements on the UK-India trade deal: Britain's most significant trade agreement since leaving the EU, eliminating tariffs on the vast majority of Indian goods exports and improving access for UK exporters of whisky, cars, medical devices and food and drink."
        ]),
        "diaspora_angle": "For Britain's 1.9-million-strong Indian community \u2014 the country's largest ethnic-minority group \u2014 the deal cuts tariffs that touch NRI-run import, restaurant and textile businesses, eases visas for chefs, yoga teachers and musicians, and, most importantly, ends the double social-security charge on the roughly 75,000 Indian professionals seconded to the UK who until now paid into two pension systems while collecting from one.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: Venezuela twin earthquakes \u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Venezuela twin earthquakes near Caracas")
    print("="*60)

    slug = "venezuela-twin-earthquakes-caracas-thousands-feared-dead-oil-markets-indian-diaspora-20260625"
    headline = "Twin Earthquakes Devastate Venezuela Near Caracas, Killing Scores \u2014 and the Shock Reaches India's Oil Bill"
    subheadline = "Two powerful quakes struck barely 39 seconds apart, flattening buildings in a country already hollowed out by years of crisis, while a jump in crude prices ripples toward import-dependent India."

    body = """Two powerful earthquakes struck near the Venezuelan capital Caracas barely 39 seconds apart on Wednesday evening, collapsing buildings across a country already exhausted by a decade of economic collapse and killing at least 164 people, with the toll widely expected to climb. The first quake, measured by the U.S. Geological Survey at magnitude 7.2, was followed less than a minute later by an even stronger magnitude 7.5 jolt \u2014 a rare \"doublet\" that gave residents almost no time to escape between the two and that seismologists warned could be followed by significant aftershocks.

The full toll is still impossible to fix with precision \u2014 a grim feature of disasters in countries whose institutions have frayed. Acting President Delcy Rodriguez confirmed at least 164 dead and more than 971 injured by Thursday morning, cautioning that the figures did not yet include the hard-hit state of La Guaira, home to the capital's international airport. The USGS issued a red alert, its most severe, and its modelling warned the death toll could most likely run into the thousands, with a substantial probability of exceeding 10,000. Emergency workers have described scenes of widespread devastation in the densely populated barrios that climb the hills around Caracas, where informal construction offers little resistance to violent shaking, digging through rubble with limited heavy equipment and intermittent electricity.

## A Disaster Atop a Disaster

Venezuela was uniquely ill-prepared for a catastrophe of this scale. Years of hyperinflation, sanctions and mismanagement have gutted public services, driven more than seven million people to emigrate, and left hospitals short of supplies and the power grid prone to failure even in normal times. The quakes struck during Battle of Carabobo Day, a public holiday marking an 1821 victory in Venezuela's independence war, so most people were at home. The country's largest airport, Simon Bolivar International near Caracas, suffered ceiling and roof damage and was closed, and power and internet outages spread across the capital. An earthquake that would test any nation has landed on one whose capacity to respond has been hollowed out. Aid agencies warned that the combination of collapsed infrastructure, fuel shortages and a weakened state could turn the rescue window \u2014 the critical 72 hours when trapped survivors are most likely to be found alive \u2014 into a period of agonising delay.

International offers of help began arriving within hours; U.S. President Donald Trump publicly offered assistance after what he called a devastating number of deaths, though Venezuela's strained relations with much of the West complicate the logistics of getting search-and-rescue teams, field hospitals and supplies into the country quickly. Neighbouring Colombia and Brazil, along with international relief organisations, signalled readiness to assist.

## The Tremor in the Oil Market

Venezuela holds the world's largest proven crude-oil reserves, and even a damaged, sanctions-constrained Venezuelan oil industry remains a factor in global supply. News of the quakes, and of possible damage to oil infrastructure around the Orinoco Belt and export terminals, sent crude prices higher as traders priced in the risk of disrupted output. That price move is where a disaster thousands of miles away touches the Indian economy directly.

India imports more than 85% of the crude oil it consumes, and is acutely sensitive to any sustained rise in global prices. A higher oil bill widens India's trade deficit, pressures the rupee, and feeds into the cost of petrol, diesel, fertiliser and transport \u2014 inflationary forces that the Reserve Bank of India watches closely. While India buys little oil directly from Venezuela today, the global crude market is a single connected pool: a supply scare anywhere lifts the price everywhere, including at the pump in Pune and the diesel that moves India's freight.

## Why It Matters for the Diaspora

People of Indian origin have lived in the Caribbean and Latin America for generations \u2014 descendants of indentured labourers in Trinidad, Guyana and Suriname, and smaller communities of traders and professionals scattered across the region, including in Venezuela itself. For these families, a catastrophe in Caracas is not distant news but a threat to relatives, businesses and the cross-border ties that bind the region's Indian-origin communities together. India's Ministry of External Affairs typically moves quickly in such moments to account for Indian nationals and offer consular help, as it has during past disasters from Nepal to Turkey.

For the broader diaspora, the Venezuela earthquakes are a reminder of how interconnected the modern world's shocks have become. A seismic fault rupturing beneath South America can, within a day, raise the price an Indian family pays to fill a scooter, squeeze an importer's margins in Mumbai, and mobilise the Indian government's disaster-diplomacy machinery on behalf of citizens half a world away. As rescuers in Caracas race against time, the human tragedy is the story that matters most \u2014 but its aftershocks, economic and humanitarian, will be felt far beyond Venezuela's borders."""

    img_url, ititle = pick_commons([
        "Caracas Venezuela skyline",
        "Caracas city Venezuela",
        "earthquake damaged building"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "Caracas, Venezuela; twin earthquakes near the capital have left thousands feared dead"

    if not img_url:
        px = fetch_pexels_image("Caracas Venezuela city")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "The Venezuelan capital Caracas, where twin earthquakes caused widespread devastation"

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
            "Reuters (reuters.com, June 25, 2026) \u2014 'Quakes rock Venezuela, killing at least 32 and injuring hundreds' and updates: two powerful earthquakes struck Venezuela on Wednesday; a magnitude 7.2 quake about 160 km (100 miles) west of Caracas was followed less than a minute later by a magnitude 7.5 tremor, per the USGS; dozens of buildings collapsed in and around Caracas; the USGS predictive model estimated the death toll would most likely run into the thousands with a substantial probability of exceeding 10,000; interim/acting President Delcy Rodriguez described a 'true tragedy' and said initial figures excluded the worst-hit La Guaira state.",
            "The Times / People / AP (2026) \u2014 acting President Delcy Rodriguez confirmed at least 164 dead and more than 971 injured by Thursday, June 25; the USGS classed the event as a 'doublet' (a 7.2 foreshock followed 39 seconds later by a 7.5 main shock) and issued a red alert warning of probable high casualties and widespread damage; the 7.5 quake was the largest in Venezuela since a 7.7 event in 1900; Simon Bolivar International Airport near Caracas suffered roof/ceiling damage and the quakes struck during the Battle of Carabobo Day holiday.",
            "Reuters / international wires (2026) \u2014 coverage of the global oil-market reaction: crude prices rose on concern over possible damage to Venezuelan oil infrastructure, given the country holds the world's largest proven crude reserves; analysts noted the connected nature of the global oil market means a supply scare lifts prices broadly.",
            "Indian context \u2014 India's reliance on imported crude (more than 85% of consumption) makes it highly sensitive to global oil-price rises, which widen the trade deficit, pressure the rupee and feed domestic inflation in fuel, fertiliser and transport, factors the Reserve Bank of India monitors closely.",
            "Diaspora context \u2014 people of Indian origin have long-established communities across the Caribbean and Latin America, including descendants of indentured labourers in Trinidad, Guyana and Suriname, and India's Ministry of External Affairs routinely mobilises to account for and assist Indian nationals during overseas disasters."
        ]),
        "diaspora_angle": "A catastrophe in Venezuela reaches Indians on two fronts \u2014 the long-rooted Indian-origin communities across the Caribbean and Latin America with relatives and businesses in the region, and the wider economy at home, where a quake-driven rise in global crude prices lifts the import bill of a country that buys more than 85% of its oil abroad.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    print("Videshi News Writer \u2014 2026-06-25 14:30 UTC run")
    id1 = write_article_1()
    id2 = write_article_2()
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Article 1 (India-UK FTA): {'OK id=' + str(id1) if id1 else 'FAILED'}")
    print(f"Article 2 (Venezuela quakes): {'OK id=' + str(id2) if id2 else 'FAILED'}")
