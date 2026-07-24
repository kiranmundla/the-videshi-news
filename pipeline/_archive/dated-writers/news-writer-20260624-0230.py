#!/usr/bin/env python3
"""
Videshi News Writer — June 24, 2026 (02:30 UTC run)
2 NEW articles, distinct from all prior runs (Iran War Powers, sanctions lift,
Sensex/monsoon markets, USTR trade talks, RBI NRI deposits, F-1 duration, etc.):
  1. India failing monsoon: 43% rain deficit, 300+ vulnerable districts, govt
     contingency plans; forecast lowest rainfall in 11 years (El Nino). Food/
     rural-economy + remittance/return-migration diaspora angle.
  2. IMO launches large-scale evacuation of ~11,000 seafarers stranded in the
     Gulf through the Strait of Hormuz after the US-Iran ceasefire. Indians are
     a huge share of global crews — direct human diaspora story.
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




# ─── Article 1: India's failing monsoon ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: India's weak monsoon, 300+ vulnerable districts")
    print("="*60)

    slug = "india-weak-monsoon-43-percent-deficit-300-districts-contingency-el-nino-diaspora-20260624"
    headline = "India's Monsoon Is Running 43% Short, and the Government Is Drawing Up Plans for 300 Districts"
    subheadline = "With rains the weakest in over a decade and the weather office warning of an El Nino-stunted season, New Delhi has put more than 300 farm districts on a contingency footing. For a diaspora bound to rural India by remittances and family land, a thin monsoon is more than a weather story \u2014 it is a livelihood story."

    body = """India's most important economic event of the year is not a budget or a summit. It is the monsoon, the four-month rainy season that waters roughly half the country's farmland and feeds 1.4 billion people. This year, that rain is not coming as it should. As of Tuesday, the monsoon had delivered rainfall about 43 percent below the long-period average, and the India Meteorological Department has forecast weak rains through at least the week ending July 2.

In response, the government has drawn up contingency plans for more than 300 districts judged most vulnerable to a poor monsoon. Farm Minister Shivraj Singh Chouhan announced the measures on Tuesday after chairing a meeting with state farm ministers, officials and agricultural scientists. Of the 315 districts under watch, 111 have been classified as high priority because less than a quarter of their farmland is irrigated, leaving them almost entirely at the mercy of the sky. Another 76 have been designated medium priority.

## A Season That Could Be the Driest in Years

The IMD defines a "normal" monsoon as between 96 and 104 percent of the 50-year average of 87 centimetres of rain across the June-September season. Last month, the state-run weather office forecast an El Nino-weakened monsoon for 2026 \u2014 one that, if it materialises as feared, would deliver the lowest rainfall in 11 years. El Nino, the periodic warming of the Pacific Ocean, has historically been associated with suppressed monsoon rains over the Indian subcontinent, and its return is the single biggest worry hanging over this year's planting season.

The monsoon delivers about 70 percent of India's annual rainfall and is critical for replenishing reservoirs, rivers and groundwater. With nearly half of the country's cropland lacking any irrigation, and about half the population relying on farming for a living, the timing and spread of the rains shape rural incomes, food prices and, ultimately, the mood of the world's most populous nation.

## What the Government Is Doing

The contingency strategy leans heavily on adaptation. States have been advised to encourage farmers in rain-fed areas to switch from thirsty crops to short-duration and less water-intensive alternatives such as pulses, millets and oilseeds. The government has also asked states to repair ponds, check dams and other water-harvesting structures and to prioritise water-conservation works ahead of the peak sowing weeks.

Millions of farmers begin planting rice, corn, cotton, soybeans and sugarcane during the rainy months of June and July. A delayed or patchy monsoon can cut yields and drag down rural incomes, even though India enters this season with ample buffer stocks of staples like rice and wheat that should cushion any immediate threat to food availability. The danger is less about empty granaries and more about the incomes of the hundreds of millions of Indians whose earnings rise and fall with the harvest.

## Why the Diaspora Should Care

For Indians abroad, a weak monsoon lands closer to home than it might first appear. The 37-million-strong diaspora is tethered to rural India through remittances \u2014 India remains the world's largest recipient, taking in well over $100 billion a year \u2014 and a large share of that money flows to families in farming districts. When the monsoon fails, those families lean harder on relatives overseas, and remittance demand tends to climb just as the rupee comes under pressure.

There is a macro dimension too. A poor harvest can stoke food inflation, which in turn shapes the Reserve Bank of India's interest-rate decisions and the value of the rupee \u2014 the same currency in which NRIs hold deposits, send money and watch their Indian assets denominated. A monsoon shortfall that pushes up food prices can erode the real value of every remittance dollar by the time it reaches a village in Maharashtra or Bihar. And for the growing number of diaspora families who own farmland back home or are weighing a return, the climate trajectory of Indian agriculture is becoming a factor in long-term planning.

## What's Next

The next two weeks are decisive. If the rains pick up by early July, much of the lost ground in sowing can still be recovered. If the El Nino-driven shortfall deepens, expect the government to lean further into crop-switching advisories, possible curbs on exports of sensitive staples to protect domestic supply, and targeted relief for the hardest-hit districts. The diaspora will feel the effects indirectly but unmistakably \u2014 in food prices, in the rupee, and in the quiet calculus of how much to send home this year."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    # Topic imagery: monsoon / Indian farmer / paddy field. Generic scene, no named person.
    img_url, ctitle = pick_commons([
        "monsoon India rice paddy field farmer",
        "Indian farmer paddy field",
        "monsoon rain India agriculture",
        "paddy field India cultivation",
        "drought Indian farmland"
    ])
    img_caption = "A farmer in an Indian paddy field; the 2026 monsoon is running about 43% below average"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("india paddy field monsoon farmer")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "An Indian paddy field; a weak monsoon has put more than 300 farm districts on a contingency footing"

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
            "Reuters (reuters.com, June 23, 2026) \u2014 'India makes contingency plans as weak monsoon threatens some farm areas': Farm Minister Shivraj Singh Chouhan said contingency plans drawn up for more than 300 districts vulnerable to a weak monsoon; monsoon so far about 43% below average, weather office forecasts weak rains through week ending July 2; IMD defines normal rainfall as 96-104% of the 50-year average of 87 cm for the June-September season; last month the weather office forecast an El Nino-weakened 2026 monsoon meaning the lowest rainfall in 11 years; monsoon delivers ~70% of annual rains; nearly half of farmland lacks irrigation and about half the population relies on farming; India holds ample rice and wheat stocks; of 315 districts watched, 111 high priority (under a quarter of farmland irrigated) and 76 medium priority; states advised to shift to short-duration, less water-intensive crops (pulses, millets, oilseeds) and to repair ponds, check dams and water-harvesting structures.",
            "Reuters (reuters.com, June 23, 2026) \u2014 'IT, metals drag Indian shares; weak business data, monsoon worries weigh': monsoon worries and a three-month-low PMI triggered profit-booking; Nifty 50 and Sensex fell 1.16% to 23,824.10 and 76,200.68; analysts cited 'persistent concerns over the monsoon shortfall'; Brent crude at $77.4, down ~39% from the $126.4 Iran-war peak.",
            "Background \u2014 India agriculture and remittances (2026): the monsoon waters roughly half of India's cropland; India is the world's largest recipient of remittances at well over $100 billion annually, with a large share flowing to families in farming districts; food inflation from a poor harvest feeds into RBI rate decisions and rupee valuation; El Nino is the periodic Pacific warming historically associated with suppressed Indian monsoon rains."
        ]),
        "diaspora_angle": "A failing monsoon hits the diaspora indirectly but unmistakably \u2014 the families that NRIs support with over $100 billion in annual remittances are concentrated in rain-fed farming districts, so a poor harvest raises remittance demand even as food inflation pressures the rupee in which overseas Indians hold deposits and send money home, while the climate trajectory of Indian agriculture increasingly shapes the plans of diaspora families who own land back home or are weighing a return.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: IMO evacuation of 11,000 stranded seafarers ───

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: IMO launches evacuation of 11,000 stranded seafarers")
    print("="*60)

    slug = "imo-evacuation-11000-seafarers-strait-hormuz-ceasefire-indian-crews-diaspora-20260624"
    headline = "A Rescue Plan for 11,000 Stranded Sailors Is Now Underway in the Gulf. Many of Them Are Indian."
    subheadline = "The UN's shipping agency said on Tuesday it has begun contacting hundreds of vessels trapped behind the Strait of Hormuz to start evacuating some 11,000 seafarers, after the US-Iran ceasefire reopened a path through the waterway. For the world's largest single supplier of merchant sailors, the operation is intensely personal."

    body = """For more than three months, hundreds of ships have sat trapped behind the Strait of Hormuz, their crews unable to leave as war between the United States and Iran turned one of the planet's busiest shipping lanes into a minefield \u2014 in places, literally. On Tuesday, the United Nations' shipping agency said the wait may finally be ending. The International Maritime Organization announced that a large-scale operation to evacuate roughly 11,000 stranded seafarers through the strait is now underway.

"We have now started contacting the ships to start the evacuation," an IMO spokesperson said, declining to give a timeframe. The agency said it had secured "the necessary safety guarantees and have thoroughly verified the conditions for safe navigation to support these operations." IMO Secretary-General Arsenio Dominguez described it as a "large-scale operation" to be carried out "in close cooperation with Iran, Oman, all other coastal states in the region, the United States and the maritime industry."

## Why So Many of Those Sailors Are Indian

This is, for India, a deeply national story dressed as a maritime one. Indians make up the single largest nationality in the global merchant marine \u2014 by most industry counts well over 250,000 serving seafarers, somewhere between a tenth and a fifth of the entire worldwide crewing pool. On any given day, a substantial share of the officers and ratings aboard the world's tankers and cargo ships are Indian citizens, many from coastal states like Kerala, Goa, Maharashtra and Andhra Pradesh, and from the maritime training hubs that feed the industry. When thousands of crew are trapped in the Gulf, a large number of the families waiting for news are in India.

The danger has already proved fatal. India confirmed earlier this month that three of its seafarers died after an attack on the vessel MT Settebello, one of several commercial ships disabled by US forces enforcing a blockade on Iranian oil. On June 11, the tanker MT Jalveer, carrying 20 Indian crew, was struck in the Gulf of Oman. India's shipping ministry has said it is "actively coordinating with all relevant agencies to guarantee the absolute safety of Bharat's seafarers and energy lifelines," and three Indian-flagged tankers carrying 94 Indian crew recently cleared the strait safely \u2014 a small advance party for the much larger evacuation now beginning.

## A Reopening That Is Not Yet a Recovery

The path out remains fragile. While Iran and the United States signed an initial accord last week to halt the conflict and reopen oil shipping, Tehran subsequently announced a fresh closure of the strait amid renewed clashes between Israel and Iran-backed Hezbollah in Lebanon. Industry bodies warn that the central part of the strait remains mined and unnavigable, with only the inshore traffic zones near Oman and Iran reportedly clear. Oman has circulated navigation guidance and, in coordination with the IMO, set up a temporary maritime corridor for vessels attempting the transit.

Even with a corridor, the practical obstacles are formidable. Maritime war-risk insurers withdrew coverage in the first days of the war and have been slow to restore it. Ships anchored for over three months may have run low on fuel and supplies, and some need their hulls scraped of barnacles before they can sail. "It's not a case of just saying the light is now green. Everyone can start your engines and off you go," one seafarers' charity director observed. Diplomacy is proceeding in parallel: talks in Switzerland have opened a 60-day window aimed at a permanent settlement, but Iranian President Masoud Pezeshkian has warned that progress depends on all sides honouring their commitments.

## Why the Diaspora Should Care

For the Indian diaspora, the seafaring community is family in the most literal sense. These are workers whose remittances support households across India's coastal belt, and whose plight over the past three months \u2014 trapped, in some cases killed, far from home \u2014 has been one of the rawest human costs of a distant war. The IMO's evacuation is the first concrete sign that thousands of them may soon be home. It also underscores a quieter truth about the diaspora's reach: Indian labour does not just staff Silicon Valley and the NHS, it crews the ships that carry the world's oil and goods, and when global shipping seizes up, India feels it in its kitchens and its coastal towns.

## What's Next

The IMO has not given a timeline, and the operation's pace will depend on safe-passage guarantees holding, insurers returning to the market, and the ceasefire surviving the flare-ups in Lebanon. India's government, which has already evacuated roughly 1,700 citizens from the broader war zone, is expected to keep pressing through diplomatic and maritime channels to bring its seafarers home. For thousands of families along India's coast, the next few weeks will be spent watching ship-tracking maps and waiting for a phone call."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    # Topic imagery: oil tanker / cargo ship / Strait of Hormuz. Generic scene, no named person.
    img_url, ctitle = pick_commons([
        "oil tanker ship Strait of Hormuz",
        "merchant ship crew tanker",
        "cargo ship Persian Gulf",
        "oil tanker sea",
        "container ship ocean"
    ])
    img_caption = "An oil tanker at sea; the IMO has begun evacuating some 11,000 seafarers stranded behind the Strait of Hormuz"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("oil tanker ship ocean")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A tanker at sea; a UN operation to evacuate stranded Gulf crews is now underway"

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
            "Reuters (reuters.com, June 23, 2026) \u2014 'Evacuation plan through Hormuz for stranded ships in Gulf underway, UN agency says': an evacuation plan for hundreds of ships with some 11,000 seafarers stranded in the Gulf is underway after the US-Iran ceasefire; IMO spokesperson said 'We have now started contacting the ships to start the evacuation' without a timeframe; IMO said it secured 'the necessary safety guarantees and have thoroughly verified the conditions for safe navigation'; Secretary-General Arsenio Dominguez said the operation will be carried out in cooperation with Iran, Oman, other coastal states, the United States and the maritime industry.",
            "Devdiscourse / PTI (devdiscourse.com, June 23, 2026) \u2014 'UN agency says major plan underway to evacuate 11,000 seafarers through Strait of Hormuz': IMO circulated Oman-provided navigation guidance for vessels transiting the strait, a chokepoint that handled ~one-fifth of global oil and gas trade before the war; Iran announced a fresh closure of the strait after renewed Israel-Hezbollah clashes in Lebanon; talks in Switzerland opened a 60-day window for a permanent resolution; Iranian President Masoud Pezeshkian, visiting Pakistan, said progress depends on all sides honouring commitments.",
            "Reuters (reuters.com, June 20, 2026) \u2014 'Three Indian-flagged oil tankers clear Strait of Hormuz, minister says': shipping minister Sarbananda Sonowal said the Desh Vaibhav, Desh Vibhor and Sanmar Herald carried more than 860,000 metric tons of oil and 94 Indian crew safely through the strait; prior to these three, 13 Indian-flagged cargoes were stranded; ministry 'actively coordinating with all relevant agencies to guarantee the absolute safety of Bharat's seafarers and energy lifelines.'",
            "The Indian Eye / CNN (theindianeye.com, cnn.com, June 2026) \u2014 background on the danger: India confirmed three Indian seafarers died after an attack on MT Settebello; on June 11 the tanker MT Jalveer carrying 20 Indian crew was struck in the Gulf of Oman; US CENTCOM said it disabled multiple commercial vessels for allegedly violating the blockade; an estimated 20,000 crew were stuck in the Persian Gulf; the central strait is mined and only inshore zones near Oman and Iran are reportedly mine-free; maritime war-risk insurers withdrew coverage and have been slow to restore it; India is the largest single supplier of merchant seafarers globally (well over 250,000 serving)."
        ]),
        "diaspora_angle": "Indians are the single largest nationality in the global merchant marine \u2014 well over 250,000 serving seafarers \u2014 so a UN operation to evacuate the ~11,000 crew stranded behind the Strait of Hormuz is, for India's coastal communities, a story about their own sons and the remittances that sustain their families, and a reminder that Indian labour crews the ships carrying the world's oil just as visibly as it staffs Silicon Valley and the NHS.",
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
