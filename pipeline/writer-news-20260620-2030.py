#!/usr/bin/env python3
"""
Videshi News Writer — June 20, 2026 (20:30 UTC run)
2 NEW articles:
  1. Indian seafarers caught in the Hormuz crisis — 3 tankers, 94 crew, finally clear (diaspora-safety / maritime)
  2. India's mango season collides with the Hormuz war: airfreight costs hit a diaspora delicacy (diaspora / trade)
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



# ─── Article 1: Indian seafarers caught in the Hormuz crisis ──────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Indian seafarers in the Hormuz crisis")
    print("="*60)

    slug = "indian-seafarers-strait-of-hormuz-tankers-clear-94-crew-iran-ceasefire-20260620"
    headline = "Three Tankers, 94 Indian Sailors, and a Strait That Tried to Trap Them. They Finally Got Out."
    subheadline = "As the first oil cargoes move again through the Strait of Hormuz after the U.S.\u2013Iran ceasefire, the slow release of 94 Indian crew on three tankers is a reminder of who actually keeps the world's energy moving \u2014 and who pays the price when the chokepoint closes."

    body = """When the Indian-flagged tanker Desh Vaibhav finally slipped out of the Strait of Hormuz this week, it carried something more precious than the hundreds of thousands of tonnes of crude in its holds: a crew of Indian sailors who had spent weeks not knowing whether they would get home.

On Saturday, India's Ports, Shipping and Waterways Minister Sarbananda Sonowal announced that three Indian-flagged tankers \u2014 the Desh Vaibhav, the Desh Vibhor and the Sanmar Herald \u2014 carrying more than 860,000 metric tonnes of oil and 94 Indian crew members had safely transited the Strait of Hormuz and were en route to India. "Our Ministry is actively coordinating with all relevant agencies to guarantee the absolute safety of Bharat's seafarers and energy lifelines," he posted on X. Before those three cargoes moved, 13 Indian-flagged cargoes had been stranded in and around the strait.

The transits came a day after oil shipments through Hormuz picked up, following the interim ceasefire deal signed Wednesday between Washington and Tehran. But the relief is fragile. U.S. President Donald Trump has warned he could resume strikes and target Iranian officials if commitments are not honoured, and Tehran has attached its own conditions to the use of the waterway. For the men aboard these ships, "safe transit" is a status that can reverse with a single announcement.

## The Hidden Workforce Behind the Headlines

The reopening of Hormuz has been told mostly as a story about oil prices, freight rates and India's import bill. But behind every one of those cargoes is a crew, and a strikingly large share of them are Indian. India ranks among the world's top three suppliers of seafarers, with a workforce of more than 300,000 \u2014 the people who crew the tankers, bulk carriers and container ships that move roughly a fifth of the world's oil and gas through this single chokepoint.

That prominence has a brutal corollary: when the strait becomes a war zone, Indians are disproportionately in harm's way. Over the course of the conflict, sailors described surviving on rationed tomatoes and potatoes at inland Iranian ports, counting more than a hundred explosions, and watching projectiles fly past their hulls. Some were stuck for two and a half weeks; others, on sanctioned vessels, for far longer, with shortages of food and fresh water. The United Nations called the situation an "unprecedented" crisis for crews trapped at sea.

## A Cost Paid in Lives

The danger has not been abstract. Earlier this month, three Indian mariners were killed aboard the tanker MT Settebello in American strikes near the strait \u2014 initially reported missing, later confirmed dead when their bodies were recovered and identified. India summoned the senior U.S. diplomat in New Delhi twice over the strikes on Indian-crewed vessels. At least eight Indian citizens have died over the broader West Asia conflict, including a worker killed in Kuwait after an Iranian strike on a desalination and power facility.

The deaths pushed seafarer safety to the top table of diplomacy. At the G7 summit in France, Prime Minister Narendra Modi made a direct pitch to fellow leaders and to Trump: "The protection of Indians working at sea is a national priority," he said, calling for the sea routes to be kept open so crews could work without fear. Trump, asked about the dead Indian mariners, called seafaring "a rough profession."

## Why It Matters for the Diaspora

For the millions in the Indian diaspora, the seafarers' ordeal is a different kind of migration story than the familiar ones about visas and green cards. These are not engineers in Silicon Valley or doctors in the Midwest; they are working-class men from coastal towns and inland districts whose remittances support entire families, and whose labour quietly underpins the global economy. When the strait closes, it is their families in Kerala, Goa, Mumbai and Uttar Pradesh refreshing their phones for a sign-off message that may never come.

The three tankers clearing Hormuz is good news. But with 13 Indian-flagged cargoes recently stranded, a fragile truce, and hundreds of thousands of Indians still crewing the world's ships, the larger question lingers: in a world where so much energy flows through so few miles of water, who looks after the people sailing through it? For now, 94 of them are headed home."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "An oil tanker at sea; three Indian-flagged tankers carrying 94 crew cleared the Strait of Hormuz this week"
    img_attribution = "Wikimedia Commons"

    for q in ["oil tanker ship high sea", "oil tanker vessel ocean", "crude oil tanker ship", "merchant ship tanker sea"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            # prefer a real photo (jpg) of reasonable size
            pick = None
            for c in commons:
                if c["width"] >= 1000 and c["original_url"].lower().endswith((".jpg", ".jpeg")):
                    pick = c
                    break
            pick = pick or commons[0]
            img_url = pick["url"]
            break

    if not img_url:
        px = fetch_pexels_image("oil tanker ship sea cargo")
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
        "vertical": "diaspora-safety",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters \u2014 Three Indian-flagged oil tankers clear Strait of Hormuz, minister says (June 20, 2026)",
            "Sarbananda Sonowal, Union Minister for Ports, Shipping and Waterways \u2014 posts on X re: Desh Vaibhav, Desh Vibhor, Sanmar Herald transit and MT Settebello deaths",
            "Reuters \u2014 Iran war leaves seafarers stranded in the Gulf (testimony of Ankit Yadav, Salman Siddiqui)",
            "CNN \u2014 UN warns of 'unprecedented' crisis for seafarers in Persian Gulf as war strands crews at sea",
            "Marine Insight / ANI \u2014 Trump calls seafaring a 'rough profession' after Indian mariner deaths in Hormuz; PM Modi's seafarer-safety pitch at the G7 summit"
        ]),
        "diaspora_angle": "India supplies more than 300,000 of the world's seafarers \u2014 a largely working-class diaspora whose remittances sustain families back home and whose labour moves a fifth of the world's oil through the Strait of Hormuz; the release of 94 Indian crew on three tankers, after others were stranded and three were killed, shows how directly the Gulf crisis lands on Indian families.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: India's mango season meets the Hormuz war ──────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Mango season vs. the Hormuz war")
    print("="*60)

    slug = "indian-mango-season-us-diaspora-hormuz-war-airfreight-prices-kesar-alphonso-sonpari-20260620"
    headline = "A Box of Alphonsos Now Costs as Much as Lobster. The War in the Gulf Is Part of the Reason."
    subheadline = "Indian mango season in America has become a full-blown diaspora frenzy \u2014 WhatsApp alerts, warehouse runs, $2,000 'mango passes.' But this year the Strait of Hormuz crisis has pushed airfreight costs up, even as a new hybrid variety, Sonpari, makes its U.S. debut at $70 a box."

    body = """Every spring, a slightly unhinged ritual unfolds across the United States. Members of the Indian diaspora track flight arrivals like anxious parents, drive to warehouses at odd hours, and walk away clutching crates as if they had just emptied a vault. The object of this devotion is the mango \u2014 not the year-round Mexican fruit that fills American grocery stores at $10 a box, but the fiercely seasonal Indian Alphonso from Maharashtra's Ratnagiri coast, the Kesar from Gujarat, the Chausa and Langra from the north.

This year, the ritual collided with a war. The same Strait of Hormuz crisis that stranded oil tankers and Indian seafarers has rippled into the cargo holds carrying India's most emotional export, pushing airfreight costs higher just as the diaspora's appetite peaks.

## A Delicacy Priced Like a Luxury

Indian mangoes were banned in the U.S. until 2007. Today they are a booming premium market. The Wall Street Journal reported premium Alphonso and Kesar varieties retailing for $50 to $60 per box of 10 to 12 mangoes \u2014 a price point on par with lobster tails. Subscription "mango passes" for weekly deliveries can run up to $2,000 for the short season that stretches from late March to July.

The economics defy ordinary logic, and the exporters know exactly why. "The emotion of Indian consumers has been very well captured," says Kaushal Khakhar, CEO of India's Kay Bee Exports. "The Indian diaspora feels that this is their way to connect to their homeland, and the flavor of the mango is way different and superior." For a family that left India decades ago, a $40 box isn't really produce. It's a plane ticket home that fits in the fridge.

## The War Tax on a Mango

What makes 2026 different is the freight. Indian mangoes must fly \u2014 they are too delicate and too seasonal to ship slowly by sea, and they require mandatory irradiation treatment under U.S. regulatory supervision before export. That makes them acutely sensitive to airfreight costs, which have climbed as the conflict in West Asia disrupted flight paths and pushed up fuel and routing expenses.

Importers feel it directly. One New Jersey importer who spent more than $1 million bringing in mangoes last year said he is spending more this season because the war in the Middle East has driven up flight prices. In one New Jersey grocery store, a mango that sells for roughly 70 cents in India was going for $5. The same Hormuz disruption that raised India's oil import bill is, in a smaller and sweeter way, taxing its diaspora's nostalgia.

## A New Contender Arrives

Even amid the cost pressure, the season is producing a debutant. A new hybrid variety called Sonpari \u2014 developed by Navsari Agricultural University as a cross between Alphonso and Banganapalli \u2014 made its first-ever U.S. export this season, with shipments arriving in Washington and New York. Each box is fetching around $70, higher than the roughly $45 for a box of Kesar.

Sonpari's appeal is partly engineering: it combines Alphonso-like flavour with larger fruit and resistance to the spongy-tissue disorder that can ruin four or five fruit in a box of Alphonsos. That defect is one reason buyers have increasingly tilted toward Kesar in recent years. Exporters say demand in the U.S. and U.K. \u2014 the strongest growth markets \u2014 has jumped 30 to 40 percent over last year, even as the Gujarat Kesar crop winds down and northern varieties like Langda and Chausa prepare to ship.

## Why It Matters for the Diaspora

The mango frenzy is, on its surface, a charming summer story. But it is also a small, vivid case study in how tightly the diaspora's everyday life is now wired to events half a world away. A ceasefire in the Gulf doesn't just move oil prices; it moves the cost of the fruit a grandmother in New Jersey buys to taste the summers of her childhood. And a hybrid bred in a Gujarat agricultural university can, within a single season, land in a Washington grocery aisle and command lobster prices.

For NRIs, the takeaway is bittersweet. The mango is more available than ever, championed even by non-Indian neighbours \u2014 one importer noted his Mexican-origin FedEx driver had switched allegiances. But the war that stranded sailors and tankers has also nudged up the price of a box of Alphonsos. The taste of home, it turns out, is not immune to geopolitics."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "Alphonso mangoes from India; diaspora demand has pushed premium boxes to lobster-tier prices in the U.S."
    img_attribution = "Wikimedia Commons"

    for q in ["Alphonso mango", "Kesar mango India", "Indian mango fruit", "mango fruit basket"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            pick = None
            for c in commons:
                if c["width"] >= 800 and c["original_url"].lower().endswith((".jpg", ".jpeg")) and "spongy" not in c["title"].lower():
                    pick = c
                    break
            pick = pick or commons[0]
            img_url = pick["url"]
            t = pick["title"].lower()
            if "kesar" in t:
                img_caption = "Kesar mangoes from Gujarat, a favourite of the Indian diaspora in the U.S."
            break

    if not img_url:
        px = fetch_pexels_image("ripe mango fruit")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Ripe mangoes"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "trade",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "The Wall Street Journal \u2014 Americans Will Do Anything to Get Indian Mangoes (premium boxes at $50\u2013$60, on par with lobster)",
            "The Packer \u2014 The $40 Taste of Home: Diaspora Demand Drives Indian Mango Surge (Kay Bee Exports CEO Kaushal Khakhar)",
            "FreshPlaza \u2014 Sonpari mango debuts in U.S. market as India's export season shifts north (Hortica Foods LLP; U.S./U.K. demand up 30\u201340%)",
            "Divya Bhaskar / Bhaskar English \u2014 Sonpari mango fetches up to $70 a box in the U.S.; over 140 tonnes exported this season",
            "BBC News India \u2014 America can't get enough of Indian mangoes (New Jersey importers; war pushing up flight prices)"
        ]),
        "diaspora_angle": "Indian mango season has become a beloved summer ritual for the U.S. diaspora \u2014 a $40 box as 'a plane ticket home' \u2014 but the Strait of Hormuz war has pushed up the airfreight these delicate, must-fly fruit depend on, even as a new hybrid, Sonpari, debuts at $70 a box, tying the price of nostalgia directly to Gulf geopolitics.",
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
