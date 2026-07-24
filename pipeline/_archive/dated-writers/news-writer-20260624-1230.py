#!/usr/bin/env python3
"""
Videshi News Writer — June 24, 2026 (12:30 UTC run)
2 NEW articles, distinct from all prior runs:
  1. Bajaj Auto hit by a ransomware attack (June 23) affecting the automaker and
     its subsidiary Bajaj Auto Technology Ltd; CERT-In notified. A cyber-security
     story for the diaspora, who ride and own Bajaj's global brands.
  2. Record-breaking, deadly heatwave grips the UK and western Europe — Met
     Office red alert, schools shut, transport disrupted — a diaspora-safety
     story for Britain's 1.9M Indians and millions more across Europe.
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


# ─── Article 1: Bajaj Auto hit by ransomware attack ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Bajaj Auto ransomware attack")
    print("="*60)

    slug = "bajaj-auto-ransomware-attack-cert-in-cyber-india-manufacturing-20260624"
    headline = "One of India's Biggest Automakers Woke Up to a Ransomware Attack. The Bigger Worry Is What It Signals."
    subheadline = "Bajaj Auto, the Pune-based maker of motorcycles and three-wheelers sold from Lagos to Los Angeles, says a ransomware attack hit its systems and those of its technology arm early on June 23. It calls its response successful so far \u2014 but the breach lands amid a wave of cyberattacks on India's industrial backbone."

    body = """India's manufacturing heartland got an unwelcome reminder this week of how exposed even its biggest, most sophisticated companies have become. Bajaj Auto, the Pune-based giant whose motorcycles and three-wheelers move people across India, Africa, Latin America and South Asia, disclosed that it had been struck by a ransomware attack \u2014 the latest large Indian manufacturer to be hit as cybercriminals increasingly turn their sights on the country's industrial base.

In a regulatory filing on Tuesday, the company said the cyber incident was detected at around 8 a.m. on June 23 and affected its own systems as well as those of its wholly owned subsidiary, Bajaj Auto Technology Ltd. Technical teams, senior management and external cyber-security experts immediately initiated precautionary measures and response protocols to contain the breach. "These measures have so far been successful," Bajaj Auto said.

## What the Company Has \u2014 and Hasn't \u2014 Said

Crucially, Bajaj Auto has not disclosed the full extent of the incident. It has not said how many systems were affected, whether any sensitive or confidential data was accessed, or whether manufacturing, sales, supply-chain or customer-facing operations suffered any direct disruption. Nor has it described the nature of the ransomware or named any group behind it. Ransomware is a form of cybercrime in which attackers typically encrypt an organisation's systems or data, then demand payment in exchange for restoring access.

The company said it had reported the incident to the Indian Computer Emergency Response Team (CERT-In), the national cyber-security agency, in accordance with the Information Technology Act, 2000, and framed the disclosure itself as a matter of good governance. For now, investors and industry observers are left waiting for further updates on what was actually compromised.

## A Pattern, Not an Isolated Strike

The attack did not happen in a vacuum. Over the past few years, ransomware groups have increasingly targeted manufacturing companies worldwide, viewing them as attractive marks precisely because production disruptions translate quickly into financial losses \u2014 and, the attackers wager, a greater willingness to pay. Modern automakers are especially exposed: they depend on sprawling enterprise software systems for manufacturing operations, inventory management, vendor coordination, product development and dealer networks. A single successful intrusion can in theory halt assembly lines, freeze logistics or expose proprietary business information.

That Bajaj's wholly owned technology subsidiary was caught up in the breach underscores how digitisation has widened the attack surface for industrial firms. The more connected the factory, the supply chain and the vehicle itself become, the more doors there are for an attacker to try.

## Why It Lands Harder Now

The timing is uncomfortable for corporate India. Bajaj's disclosure came in the same week that a separate cyber incident put a major Indian Apple supplier's files in the spotlight, reinforcing a sense that the country's marquee manufacturers are being probed and breached with growing frequency. As India positions itself as an alternative manufacturing hub to China \u2014 courting global electronics, auto and component makers \u2014 the resilience of its companies' digital defences is no longer a back-office concern. It is part of the pitch.

## What It Means for the Diaspora

For the millions of overseas Indians who follow corporate India as investors, the immediate market question is whether the breach dented production or leaked data; so far the company says no, but the lack of detail leaves room for nerves. The longer-term signal matters more. Bajaj is not a soft target \u2014 it is a globally recognised, deeply digitised manufacturer, and it was still hit. For NRIs who own Indian equities, run businesses that plug into Indian supply chains, or simply take pride in the global reach of brands like Bajaj, the episode is a warning that India's industrial ascent now travels with a cyber-risk shadow. The companies that manage that risk transparently \u2014 disclosing early, notifying regulators, containing fast \u2014 will be the ones that keep the trust of a watching diaspora.

## What to Watch

The key updates will come in the days ahead: whether Bajaj confirms any data was exfiltrated, whether any plants or dealer systems were knocked offline, and whether CERT-In or the company attribute the attack to a known ransomware operation. How quickly and candidly Bajaj fills in those blanks will shape not just its own reputation, but the wider read on how ready India's manufacturing champions really are for the cyber age.
"""

    # Hero: Wikimedia Commons photo of Bajaj (institution/brand, not a named person)
    img_url, _ = pick_commons([
        "Bajaj Auto factory Pune",
        "Bajaj Auto headquarters",
        "Bajaj motorcycle",
        "Bajaj Auto"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "Bajaj Auto, the Pune-based maker of motorcycles and three-wheelers, disclosed a ransomware attack on its systems"

    if not img_url:
        cu, _ = pick_commons(["cyber security ransomware", "computer server data center"])
        if cu:
            img_url = cu
            img_caption = "A data centre; Bajaj Auto says a ransomware attack hit its systems and those of its technology subsidiary"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "tech",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters (reuters.com, June 23 2026) \u2014 'India's Bajaj Auto says ransomware attack hits systems': Bajaj Auto (BAJA.NS) said a ransomware attack earlier in the day impacted the automaker and its unit Bajaj Auto Technology's systems; the company said it initiated necessary precautionary actions and protocols to mitigate the impact, with measures successful so far (reporting by Urvi Dugar, Bengaluru).",
            "Autocar Professional (autocarpro.in, June 23 2026) \u2014 'Bajaj Auto Reports Ransomware Attack, Says Operations Safeguarded After Swift Response': in a regulatory filing, the Pune-based two- and three-wheeler maker said the June 23 incident (detected ~8 a.m. IST) affected its systems and those of wholly owned subsidiary Bajaj Auto Technology Ltd; technical teams, management and external cyber-security experts initiated containment, which it called successful; it reported the incident to CERT-In; the company did not disclose the nature of the attack, whether data was compromised, or whether manufacturing/sales/supply-chain operations were disrupted.",
            "The420.in (the420.in, June 23 2026) \u2014 'Ransomware Attack Targets Bajaj Auto Systems; National Cyber Agency Informed': confirms the breach affected IT systems of both Bajaj Auto and Bajaj Auto Technology Ltd, that emergency protocols were triggered, that the preliminary assessment found mitigation measures successful, and that the company notified CERT-In; full extent (systems affected, data accessed, production impact) remains undisclosed."
        ]),
        "diaspora_angle": "Bajaj is a globally recognised Indian brand whose two- and three-wheelers are sold across the diaspora's home markets in Africa, Latin America and South Asia, and a stock many NRIs hold; a ransomware hit on so digitised a manufacturer is a warning sign about the cyber-resilience of the Indian industrial firms the diaspora invests in and takes pride in.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Record deadly heatwave grips UK and Europe ───

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Record heatwave grips UK and Europe")
    print("="*60)

    slug = "uk-europe-record-heatwave-met-office-red-alert-indians-britain-diaspora-20260624"
    headline = "Britain Is About to Smash Its June Heat Record. For 1.9 Million Indians There, This Is a Safety Story."
    subheadline = "A Saharan 'heat dome' has pushed western Europe into a deadly, record-breaking heatwave. The UK Met Office has issued a rare red alert warning of a risk to life, schools are shutting and trains are cancelled \u2014 just as London hosts its flagship climate week and changes prime ministers."

    body = """A blast of Saharan air has turned western Europe into a furnace this week, and the numbers are the kind meteorologists struggle to describe without reaching for the word "insane." Britain, home to roughly 1.9 million people of Indian origin, is forecast to obliterate its June temperature record, with authorities issuing a rare red extreme-heat warning that signals an increased risk to life across the entire population \u2014 not just the vulnerable.

The heat is being driven by a "heat dome": a strong high-pressure system trapping a mass of hot air drawn north from the Sahara over western and central Europe, allowing temperatures to build day after day. Heat alerts have been in place across more than 20 European countries.

## How Hot, and How Dangerous

In Britain, temperatures are expected to peak around 38\u201339 degrees Celsius (100\u2013102 Fahrenheit), with forecasters giving Thursday a real chance of touching 40C \u2014 a threshold the country has reached only once before, in July 2022. That would shatter the previous June record of 35.6C, set in Southampton in 1976. The Royal Meteorological Society's chief executive, Liz Bentley, warned of "an unprecedented heat wave," noting that May and June would together mark two consecutive months in which UK temperature records were "annihilated by well over 2C."

The UK Health Security Agency issued only its second-ever heat-health alert of this severity, warning of a risk to life even for healthy people and urging the elderly to take extra care. "Humidity is also a factor, making this heatwave even more impactful," the Met Office said, warning of "tropical nights" when temperatures fail to drop below 20C \u2014 the kind of relentless heat that gives bodies no chance to recover.

The red alert covers London, the Midlands, the east, south-west and south-east of England and parts of south Wales, with amber alerts across much of the rest of England and Wales. Hundreds of schools have closed, cut to half-days or relaxed uniform rules; Chiltern Railways cancelled more than half its services to keep the railway running safely; and motoring groups urged drivers without air-conditioning to postpone non-essential journeys.

## A Continent on Alert

Britain's ordeal is the northern edge of a far deadlier picture. France recorded its hottest day since records began nearly 80 years ago, with 44.3C in the south-west; at least 48 people have died there from drowning while seeking relief, and two young children died after being left in a hot car. Spain saw temperatures above 40C and two heatstroke deaths, while Italy issued its highest heat alert for 16 cities including Rome, Milan and Florence. Forecasters compared the pattern to the catastrophic 2003 heatwave that caused an estimated 80,000 excess deaths across Europe. The World Meteorological Organization notes that Europe is warming at more than twice the global average, making such episodes increasingly likely.

## Why This Matters for the Diaspora

For the Indian diaspora, this is not a distant weather story \u2014 it is happening in the cities where they live, work and send their children to school. Britain's 1.9-million-strong Indian community is concentrated in heat-exposed urban areas like London, Leicester, Birmingham and the West Midlands, much of it in older housing stock built to retain warmth, not repel it, and rarely fitted with air-conditioning. Elderly first-generation migrants, many with the kind of cardiovascular and respiratory conditions that heat aggravates, are squarely in the at-risk group health officials are warning about. Indian students and young professionals across the UK and Europe face cancelled trains, shut campuses and sweltering flats during exam and internship season.

There is a practical checklist for families: keep homes shaded and ventilated overnight, stay hydrated, avoid strenuous activity in the afternoon, check on elderly relatives and neighbours, and treat the official advice to avoid non-essential travel as exactly that. For those with parents visiting from India \u2014 a common summer pattern \u2014 the warnings deserve particular attention.

## The Bigger Backdrop

The heat has collided with a chaotic week in Britain: it arrived as London hosted its flagship climate event, London Climate Action Week, and as Prime Minister Keir Starmer resigned, throwing Downing Street into another leadership change. "London isn't just calling, it's cooking," UN Secretary-General Antonio Guterres told the gathering \u2014 a grim irony at a summit meant to confront exactly this. Conditions in Britain are expected to ease toward the end of the week, but the message from this June is unmistakable: record-shattering heat is no longer a once-in-a-generation event, and for a diaspora spread across an ever-hotter Europe, it is becoming a recurring part of life.
"""

    # Hero: Wikimedia Commons photo (scene/place, not a named person)
    img_url, _ = pick_commons([
        "London heatwave sun summer",
        "London skyline summer sun",
        "Big Ben London summer",
        "London cityscape"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "London under the summer sun; Britain is forecast to break its June heat record amid a rare Met Office red alert"

    if not img_url:
        px = fetch_pexels_image("London city heat summer sun")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A sweltering London skyline as Britain braces for record-breaking June heat"

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
            "Reuters (reuters.com, June 22 2026) \u2014 'UK temperature seen breaking June record as heatwave spreads': temperatures in Britain expected to reach 39C (102.2F) by mid-week in a four-day heatwave, easily breaking the June record of 35.6C (1957, matched 1976); UK's all-time high is 40.3C (July 2022); UK Health Security Agency issued only its second-ever heat-health alert of this severity, warning of risk to life even for healthy people; Met Office warned of humidity and 'tropical nights' above 20C; heatwave spread north from western Europe across the Channel.",
            "The Times (thetimes.com, June 23 2026) \u2014 'June heat record almost certain with 40C highs and school closures': Tuesday's peak was 34.6C in Wisley, Surrey; Met Office expects significant build Wednesday\u2013Thursday, almost certainly breaking the June record, with Thursday the hottest (39C likeliest, ~30% chance of 40C); red alert in place for the Midlands, east, south-west and south-east England, London and parts of south Wales; amber alerts for Wales, north-west/north-east England and Yorkshire; Chiltern Railways cancelled over half its services; hundreds of schools closed or cut to half-days.",
            "CNN (cnn.com, June 23 2026) \u2014 'Dozens drown, schools close, heat records set to be annihilated': UK Met Office issued a very rare red warning for extreme heat indicating risk to life; the June record could be smashed by as much as 6F; UN Secretary-General Antonio Guterres said 'London isn't just calling, it's cooking' at London Climate Week; in France at least 48 died from drowning and two children died in a hot car; heat alerts across 23 European countries.",
            "Phys.org / AFP (phys.org, June 22 2026) \u2014 'Europe sweats through new heat wave, with worse to come': Royal Meteorological Society chief Liz Bentley warned of 'an unprecedented heat wave' with temperatures likely 38\u201339C, surpassing the 35.6C June record, marking two consecutive months (May and June) of UK records 'annihilated by well over 2C'; Europe warming at more than twice the global average per the WMO."
        ]),
        "diaspora_angle": "Britain's 1.9 million people of Indian origin \u2014 concentrated in heat-exposed cities, often in older homes without air-conditioning, with elderly relatives in the at-risk group \u2014 are living through a record, potentially deadly heatwave, making this an urgent safety story for the UK and wider European diaspora, complete with the official guidance families need.",
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
