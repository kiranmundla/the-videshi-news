#!/usr/bin/env python3
"""
Videshi News Writer — June 21, 2026 (00:30 UTC run)
2 NEW articles:
  1. IRGC declares Strait of Hormuz shut on Saturday even as US-Iran talks open in Switzerland — India's oil lifeline back in doubt (geopolitics)
  2. Starmer on the brink of resigning — what it means for the India-UK CETA trade deal NRIs are watching (diaspora/geopolitics)
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


# ─── Article 1: IRGC declares Hormuz shut as US-Iran talks open ──────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: IRGC declares Hormuz shut as talks open")
    print("="*60)

    slug = "irgc-declares-strait-hormuz-shut-us-iran-switzerland-talks-india-oil-lifeline-doubt-20260621"
    headline = "Days After the Oil Started Flowing Again, Iran's Guards Declared the Strait of Hormuz Shut. India's Refiners Are Watching the Water."
    subheadline = "Even as US and Iranian negotiators arrive in Switzerland for Sunday peace talks, Tehran's Revolutionary Guards say the world's most important oil chokepoint is closed again \u2014 a reminder of how fragile the lifeline carrying a third of India's crude really is."

    body = """For about a week, it looked like the worst was over. An interim US-Iran deal, brokered by Pakistan and signed on Wednesday, had reopened the Strait of Hormuz after nearly four months of disruption. Tankers were moving again. Oil prices, which had spiked to $120 a barrel during the war, were sliding back down. Indian refiners, who source roughly a third of their crude through that narrow waterway, exhaled.

Then, on Saturday, Iran's Islamic Revolutionary Guard Corps declared the Strait of Hormuz shut once more.

The timing could hardly be more pointed. A high-level Iranian delegation had just landed in Switzerland for peace talks set to begin Sunday, with US Vice President JD Vance flying in to meet them. And yet, even as its negotiators sat down, Tehran's hardline military wing warned that ships approaching the Strait would be "at risk," citing what it called Israeli violations of the ceasefire in Lebanon. For a country like India, which imports more than 85% of the oil it burns, that contradiction is the whole problem in miniature: the peace is on paper, but the guns \u2014 and the chokepoints \u2014 are still live.

## The US Says the Water Is Open. Iran Says It Isn't.

Washington moved quickly to dispute the claim. US Central Command said 55 merchant ships transited the Strait on Saturday, carrying more than 17 million barrels of oil to global markets, and pledged that American forces "will ensure commercial traffic continues." Vance, speaking to Fox News before he left, said he had "seen no evidence that the Strait of Hormuz was closed" and expressed confidence the ceasefire would hold.

But the gap between the two narratives is exactly what unsettles oil markets and energy planners. An adviser to Iran's Supreme Leader, Mohammad Mokhber, posted on X that as long as the agreement remained "only on paper," the flow of Middle East energy would stay halted. President Trump, for his part, wrote on social media that no toll would be charged for passage through the Strait during or after the 60-day ceasefire \u2014 while leaving open the possibility of a US-imposed toll "for services rendered as the Guardian Angel" should the talks collapse.

## Why India Is Not Rushing Back

Here is the quiet irony for India: even with Hormuz nominally reopened, Indian refiners are in no hurry to return to Gulf crude. Industry sources say the country's refiners have roughly two months of supply on hand and are bracing for higher freight rates and war-risk insurance premiums while the ceasefire's durability remains in doubt. That has made cheap Russian barrels \u2014 bought on a delivered basis, with the seller arranging shipping and absorbing the risk \u2014 more attractive than ever, at discounts of $1 to $2 a barrel to Dated Brent.

Indian Oil Corp has issued a tender to charter tankers to lift cargoes from behind the Strait, but sources caution it should not be read as a signal of imminent resumption. Middle Eastern producers have approached Indian buyers to start taking committed volumes under long-term contracts; the buyers, so far, are not eager, and New Delhi has yet to give the green light for Indian tankers to set off for the Persian Gulf.

The deeper damage is already done. India's energy import bill soared nearly 82% year-on-year in May, hitting $18.7 billion, as the country leaned on costlier non-Middle Eastern cargoes. To cope, the government advised energy conservation and allowed fuel retailers to raise pump prices for the first time in years \u2014 four hikes in a single month. Saturday's IRGC declaration is a warning that those pressures could return with little notice.

## Why It Matters for the Diaspora

For NRIs, this is not a distant geopolitical drama \u2014 it is a line item that runs through the entire diaspora economy. The price of crude shapes the rupee, and a weaker rupee changes the math on everything from remittances sent home to the value of NRI deposits parked in Indian banks. When freight and war-risk premiums spike, so do the shipping costs baked into the price of Indian exports \u2014 the textiles, gems and jewellery, and engineering goods that diaspora-linked businesses trade in.

It also hits closer to the bone for the millions of Indians living and working in the Gulf, whose livelihoods are tethered to the same waterway and the same fragile peace. Saturday's reversal is a reminder that the calm of the past week was provisional. Until the Switzerland talks produce something firmer than a 14-point document, the Strait of Hormuz \u2014 and the cost of filling a tank in Mumbai or sending money to Kerala \u2014 will swing on the word of whoever is standing on its shore."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "An oil tanker transits the Strait of Hormuz, the chokepoint carrying about a fifth of the world's oil"
    img_attribution = "Wikimedia Commons"

    for q in ["Strait of Hormuz oil tanker", "oil tanker Persian Gulf ship", "crude oil tanker sea"]:
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
        px = fetch_pexels_image("oil tanker ship sea")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "An oil tanker at sea"

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
            "Reuters \u2014 US disputes Iranian claims about closing Strait of Hormuz as negotiators head to Switzerland (June 21, 2026): IRGC declares Strait shut Saturday; CENTCOM says 55 ships transited with 17M+ barrels; Vance, Trump statements",
            "OilPrice.com \u2014 India Isn't Rushing Back to Middle Eastern Oil Despite Hormuz Reopening (refiners hold ~2 months supply; return to Russian crude; $18.7B May energy bill, +82% YoY)",
            "The Hindu BusinessLine \u2014 Indian refiners in no hurry to return to West Asian oil as Hormuz reopens (delivered-basis Russian barrels at $1-2 discount; IOC tanker tender)",
            "Reuters \u2014 India's May oil supply from UAE tops pre-war levels as imports rise (crude imports 5.27 mbpd, Russia largest supplier at 36.5%)"
        ]),
        "diaspora_angle": "India sources roughly a third of its crude through the Strait of Hormuz and imports over 85% of its oil, so a renewed closure feeds straight into the rupee, NRI deposit values, remittance math, and the livelihoods of millions of Indians working in the Gulf.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Starmer on the brink and the India-UK CETA ──────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Starmer's exit and the India-UK trade deal")
    print("="*60)

    slug = "uk-starmer-resignation-brink-burnham-india-uk-ceta-trade-deal-july-15-nri-impact-20260621"
    headline = "Britain May Change Prime Ministers on Monday. The India-UK Trade Deal Was Due to Be Signed in July."
    subheadline = "Keir Starmer is reportedly on the brink of resigning, with Andy Burnham waiting in the wings \u2014 and the timing lands awkwardly for the CETA agreement and its quiet National Insurance win that NRIs sent to Britain have been waiting on."

    body = """Britain may be about to install its seventh prime minister in just over a decade. According to the Observer, Keir Starmer is expected to resign on Monday and set out a timetable for his departure, capping a weekend of "brutal" conversations with cabinet ministers who told him his time was up. A government source insisted Starmer remained focused on the job. But the political reality shifted sharply on Friday, when his rival Andy Burnham \u2014 the popular former mayor of Greater Manchester \u2014 romped to a by-election win in Makerfield, taking 55% of the vote and clearing his path to a formal leadership challenge.

For the Indian diaspora in Britain and for NRIs watching from afar, the drama in Westminster carries a specific, practical question: what happens to the India-UK trade deal?

## A Deal With a Date \u2014 and a Quiet Win for NRI Pay

The Comprehensive Economic and Trade Agreement (CETA) between India and the United Kingdom had finally acquired a concrete signing target of mid-July, after years of on-again, off-again negotiation. Buried inside it is a provision that matters enormously to the roughly 1.8 million people of Indian origin in the UK and to the Indian professionals who rotate through London on work assignments: the Double Contribution Convention.

Under that arrangement, Indian workers temporarily posted to the UK \u2014 and their employers \u2014 would be exempted from paying British National Insurance contributions for up to three years, because they continue contributing to India's social security system back home. For an Indian IT professional on a short London posting, that is a meaningful bump in take-home pay, ending the long-standing complaint of paying into a British system they would never draw a pension from.

## Why a Change at the Top Creates Jitters

Trade deals are negotiated by governments, not individuals, and the broad architecture of CETA enjoys cross-party support in Britain because of the economic heft it carries \u2014 India is on track to become the world's third-largest economy by 2030. A new prime minister does not automatically tear up a deal his predecessor's government built.

But timing is everything, and a leadership transition is precisely the kind of event that can slow a signing ceremony scheduled for mid-July. A caretaker period, a new cabinet finding its feet, a fresh trade secretary wanting to review the fine print \u2014 any of these can push a date to the right. Burnham, whose pitch is built on a "Makerfield test" of whether policies "work for people here," will face pressure to scrutinise a deal partly framed around easing the movement of foreign professionals into Britain, even as immigration remains the third rail of UK politics and Reform UK breathes down Labour's neck.

## The Larger Diaspora Stakes

The UK is not an abstraction for the Indian diaspora. Indian students are now the single largest international cohort at British universities, surpassing China, even as new visa rules and a shortened post-study work window have already dented enrolment. The community's economic and cultural footprint \u2014 from the City of London to the corner shop \u2014 makes the health of the bilateral relationship a lived, daily matter.

CETA was meant to be the anchor of a deepening tie: lower tariffs on Indian goods, easier services trade, and that National Insurance exemption sweetening the deal for the people who move between the two countries. A wobble at the top of British politics does not sink any of that, but it does inject uncertainty into a timeline the diaspora had begun to count on.

## What to Watch

The immediate signal will come early in the week. If Starmer sets out an orderly transition \u2014 staying on through the Labour conference in September, as some ministers expect \u2014 the July signing could still proceed on schedule under his government. If he goes abruptly and Burnham moves quickly into No. 10, the new administration's first priorities will tell the story: a leader who reaffirms the deal sends one message; one who orders a review sends another.

For NRIs, the advice is simply to watch the calendar. The Double Contribution Convention and the wider CETA framework remain the most tangible diaspora wins on the table in any Western capital right now. They are not in danger of being scrapped \u2014 but in politics, a delayed win and a denied one can feel uncomfortably similar while you wait."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = fetch_wikipedia_person_image("Keir Starmer")
    img_caption = "UK Prime Minister Keir Starmer, reportedly on the brink of resigning as Labour leader"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        for q in ["Keir Starmer 2024", "Keir Starmer portrait", "10 Downing Street"]:
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
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters \u2014 Report says UK PM Starmer ready to quit, but source says he is still focused on the job (June 20-21, 2026): Observer reports expected Monday resignation; Burnham's Makerfield by-election win with 55%; 100+ Labour MPs want him to set exit timeline",
            "The Times \u2014 In public, Keir Starmer is defiant. In private, he 'considers resigning' (cabinet pressure from Alexander, Cooper, Reynolds; possible September transition at Labour conference)",
            "The Sun \u2014 Embattled Starmer 'read his last rites' by Cabinet as they urge him to stand down for Burnham 'coronation' (transition scenarios; Burnham as frontrunner)",
            "The Videshi / prior reporting \u2014 India-UK CETA signing targeted for mid-July with Double Contribution Convention exempting posted Indian workers from UK National Insurance for up to three years",
            "India Tribune / IANS \u2014 Indian students in UK surpass all nations, including China (British High Commissioner Alex Ellis)"
        ]),
        "diaspora_angle": "The India-UK CETA, due to be signed in mid-July, carries a National Insurance exemption worth real take-home pay for Indian professionals posted to Britain; a sudden change of UK prime minister days before the target date injects fresh uncertainty into a timeline the 1.8-million-strong Indian-origin community had begun to count on.",
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
