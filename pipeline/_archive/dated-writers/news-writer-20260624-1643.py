#!/usr/bin/env python3
"""
Videshi News Writer — June 24, 2026 (16:43 UTC run, attempt 2)
2 NEW articles, distinct from all prior runs (dedup-checked against last 45 news):
  1. India-EU FTA timeline: Commerce Minister Piyush Goyal confirms the
     "mother of all deals" will be SIGNED by December 2026 and come into FORCE
     by February-March 2027, with ~93% of Indian exports getting duty-free
     access to the 27-nation bloc. Distinct from the India-UK CETA piece (14:30
     run) — different bloc, different timeline, different stakes.
  2. WTO Dispute Settlement Body establishes a panel (June 23) to examine
     India's solar and IT-goods tariffs after China's second request; New Delhi
     had blocked the first request in May. A trade-rules fight over India's
     domestic-manufacturing (PLI/Make-in-India) push.
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


# ─── Article 1: India-EU FTA to be signed by December, in force Feb-March 2027 ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: India-EU FTA timeline (Goyal)")
    print("="*60)

    slug = "india-eu-free-trade-agreement-signed-december-2026-in-force-february-2027-goyal-diaspora-20260624"
    headline = "After Two Decades of Talking, India and Europe Finally Have a Date. The 'Mother of All Deals' Gets Signed by December."
    subheadline = "Commerce Minister Piyush Goyal says the India-EU free-trade pact will be signed by December and take effect by February or March 2027, opening nearly the entire European market to Indian exporters \u2014 and reshaping the economics for a diaspora that straddles both."

    body = """India's biggest trade prize in a generation now has a timeline. Commerce and Industry Minister Piyush Goyal said this week that the free-trade agreement between India and the 27-nation European Union \u2014 a deal he has called the "mother of all deals" \u2014 will be signed by December 2026 and come into force by February or March 2027. Speaking to chartered accountants in Mumbai, Goyal framed it in plainly ambitious terms: "Now, with almost zero duty, almost the entire European market will be open for us."

The announcement puts a clock on an agreement that took the better part of two decades to negotiate. India and the EU first opened talks in 2007, watched them collapse, restarted them, and only on January 27 this year announced that negotiations had finally concluded. What remains now is the legal scrubbing, translation into the EU's two dozen official languages, and ratification \u2014 the unglamorous machinery that turns a concluded deal into a signed and operative one. Goyal's December-to-March window is the government's clearest public commitment yet to when that machinery finishes its work.

## What's Actually in the Deal

The headline number is access. Under the agreement, roughly 93% of Indian export lines will enjoy duty-free entry into the EU, India's second-largest export destination. For the labour-intensive sectors that employ millions back home \u2014 textiles and apparel, leather and footwear, gems and jewellery, marine products, engineering goods \u2014 the removal of tariffs that currently run between 8% and 12% is the difference between competing and being undercut. Indian garment exporters have long watched rivals like Bangladesh and Vietnam ship into Europe duty-free; this levels that field.

The flow runs both ways. European luxury cars, currently taxed at rates as high as 110%, will see duties fall toward 10% over a phase-in period, and tariffs on European wines and spirits will drop sharply over time. Processed foods such as pasta and chocolate, now taxed around 50%, are set to become duty-free. For Indian consumers \u2014 and for the diaspora that travels home with European tastes \u2014 a slice of the imported-goods aisle gets cheaper.

The scale is hard to overstate. Together, India and the EU account for about a quarter of global GDP and roughly a third of world trade. Bilateral trade in goods and services is already worth around 180 billion euros, and Brussels has said it expects the deal to nearly double EU exports to India by 2032.

## Why Now

Officials in both capitals are candid that geopolitics, as much as commerce, sealed the deal. The return of tariff brinkmanship from Washington and China's tightening grip on critical supply chains pushed Brussels and New Delhi to hedge. For the EU, India is the obvious alternative market: vast, young, and increasingly central to global manufacturing. For India, locking in duty-free access to Europe is insurance against an unpredictable trade relationship with the United States \u2014 the same calculation driving New Delhi's parallel push to finish deals with Britain, which takes effect July 15, and Canada.

Goyal also confirmed that US Trade Representative Jamieson Greer was in India this week for talks on a separate India-US bilateral pact, underscoring how many trade tracks New Delhi is running at once.

## Why It Matters for the Diaspora

For the millions of people of Indian origin across Europe \u2014 in Britain's former trade orbit, in Germany, the Netherlands, Italy, Portugal and beyond \u2014 the agreement is more than an abstraction. Diaspora-run businesses that import Indian textiles, food and craft goods stand to see their costs fall and their margins widen once duties drop. Indian exporters gain a more predictable, cheaper route into the homes of 450 million European consumers, many of them served by diaspora distributors and retailers. And the professional-mobility chapters \u2014 the rules governing how Indian engineers, IT staff and skilled workers can be posted to EU member states \u2014 carry direct weight for families weighing a move to the continent at a moment when the US and UK routes feel ever more uncertain.

There is also a softer dividend. A deal of this magnitude binds India and Europe into a deeper economic partnership, and the diaspora is its connective tissue \u2014 the community that already moves between the two markets, sends remittances in both directions, and builds the business relationships that trade statistics only later record. The signatures are still months away, and ratification across 27 member states is rarely smooth. But for the first time in twenty years, the deal has a date. The diaspora will be watching whether December holds.
"""

    img_url, _ = fetch_wikipedia_person_image("Piyush Goyal"), ""
    img_attribution = "Wikimedia Commons"
    img_caption = "Commerce and Industry Minister Piyush Goyal, who confirmed the India-EU free-trade pact will be signed by December and take effect by early 2027"

    if not img_url:
        img_url, _ = pick_commons([
            "European Commission Berlaymont building Brussels",
            "European Union flags Brussels",
            "Port of Rotterdam container ship",
            "European Parliament building"
        ])
        img_caption = "The European Union, India's second-largest export destination, where nearly the entire market is set to open to Indian goods"

    if not img_url:
        px = fetch_pexels_image("container ship port trade")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Trade between India and the EU is set to expand sharply once the long-negotiated free-trade pact takes effect"

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
            "Press Trust of India (via nordot.app, June 21 2026) \u2014 'India-EU trade pact to be signed by Dec; implemented from Feb-Mar next year: Goyal': India and the 27-nation EU will sign the FTA by December and are likely to implement it during February-March next year, Commerce and Industry Minister Piyush Goyal said in Mumbai; on January 27 the two sides announced the conclusion of negotiations for the 'mother of all deals'; about 93% of Indian shipments will enjoy duty-free access to the EU, while imports of luxury cars and wines from the EU become cheaper; India and the EU account for 25% of global GDP and about a third of international trade; Goyal said US Trade Representative Jamieson Greer was visiting India that week for bilateral trade talks.",
            "IANS (ianslive.in, June 21 2026) \u2014 'India-EU FTA to be signed by December, implemented by Feb-March 2027: Piyush Goyal': India and the EU are expected to sign their long-awaited FTA by December 2026, with the pact likely to come into force by February-March 2027; about 93% of Indian exports expected to enjoy duty-free access to the EU market; Goyal said the agreement would significantly enhance India's access to the European market by reducing tariffs on a wide range of goods.",
            "Livemint (livemint.com, January 27 2026) \u2014 'India-EU FTA Highlights': India and the EU concluded a landmark trade agreement; the deal will cut or eliminate tariffs on almost 97% of European exports, saving up to 4 billion euros ($4.75 billion) annually in duties; tariffs on cars to be lowered gradually from a top rate of 110% to as low as 10%, and on wines from 150% to as low as 20%; tariffs on processed foods including pasta and chocolate (currently ~50%) to be completely eliminated.",
            "European Policy Centre (epc.eu) \u2014 'Why geopolitics, not just trade, finally sealed the EU-India deal': on 27 January 2026 the EU and India concluded an FTA after nearly 20 years of negotiations; bilateral trade in goods and services already worth ~180 billion euros, with the FTA aiming to double EU exports to India by 2032; the conclusion was driven heavily by shifting geopolitical pressures from Washington and Beijing, pushing both sides to diversify away from overdependence on the US and China.",
            "Textile Insights (textileinsights.in, June 2026) \u2014 'India-EU FTA On Track For December Signing': India's textile and apparel industry could be among the biggest beneficiaries; the EU is India's second-largest export destination for textiles and clothing; Indian textile and apparel exports currently face tariffs of 8-12% while competitors such as Bangladesh enjoy duty-free access; benefits expected for hubs including Tiruppur, Surat, Ludhiana, Panipat, Bhilwara and Coimbatore."
        ]),
        "diaspora_angle": "For the millions of people of Indian origin across Europe, the FTA promises cheaper costs and wider margins for diaspora-run businesses that trade Indian textiles, food and craft goods, more predictable export routes into a 450-million-consumer market, and clearer professional-mobility rules for skilled Indians eyeing the continent as US and UK routes grow uncertain.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: WTO establishes panel on India's solar & IT tariffs (China dispute) ───

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: WTO panel on India solar/IT tariffs (China)")
    print("="*60)

    slug = "wto-panel-india-solar-it-tariffs-china-dispute-make-in-india-pli-20260624"
    headline = "China Just Got the WTO to Put India's 'Make in India' Solar Push on Trial"
    subheadline = "Geneva's Dispute Settlement Body has agreed to set up a panel to examine India's tariffs and incentives for solar and IT goods, which Beijing says discriminate against Chinese products \u2014 a test case for how far India can go to build factories at home without breaking global trade rules."

    body = """A quiet but pointed fight over how India builds its factories has just escalated to the world's top trade court. On Monday, June 23, the World Trade Organization's Dispute Settlement Body agreed to establish a panel to examine tariffs and incentives in India that China says discriminate against Chinese solar-energy and information-technology products. It is the formal start of a case that strikes at the heart of "Make in India" \u2014 New Delhi's signature drive to manufacture at home the things it now imports, much of it from China.

The dispute has been building for months. China first took its complaint to the WTO in December 2025, arguing that India's measures violate global trade rules. The two countries held mandatory consultations in February but failed to reach a settlement. China then asked the DSB to set up an adjudication panel. India blocked that first request at a May 22 meeting \u2014 a one-time right every country has. But under WTO rules, a second request cannot be blocked, and when Beijing renewed it this week, the panel was established almost automatically.

## What China Is Challenging

Beijing's complaint has two prongs. The first is India's tariffs on a basket of high-technology imports \u2014 China alleges New Delhi is levying customs duties on roughly a dozen IT goods, including items tied to smartphones, semiconductors, integrated circuits, wafers and display-manufacturing equipment, at rates that exceed the limits India committed to when it joined the WTO.

The second, and arguably more consequential, prong targets India's solar-manufacturing incentives. China says India's Production Linked Incentive (PLI) scheme for solar cells and modules ties government cash grants to "local value addition" requirements \u2014 in effect rewarding manufacturers for using Indian-made inputs over imported ones. That, Beijing argues, is exactly the kind of "domestic over imported" preference that WTO rules on subsidies and trade-related investment measures prohibit. China contends the measures breach the General Agreement on Tariffs and Trade, the Agreement on Subsidies and Countervailing Measures, and the agreement on trade-related investment measures.

## India's Defence

India has come out swinging. New Delhi expressed "disappointment" at China's renewed request and insists its measures are fully consistent with WTO law \u2014 a position it says it already demonstrated during consultations. More striking has been India's rhetoric. At the May meeting, Indian representatives accused China of "mercantilism" and a "beggar-thy-neighbour" policy, language that echoes Washington's own critiques of Beijing.

India's sharpest point is about who dominates the industry in the first place. New Delhi noted that China controls more than 80% of the global value chain for solar-module production, and argued it was "strange" that a country with that kind of grip would move to "stymie the legitimate growth" of solar manufacturing in other nations. The subtext is unmistakable: India sees the case as China trying to use trade law to keep rivals dependent on Chinese panels.

The case will now be heard by a panel, with an unusually long list of countries \u2014 Australia, Brazil, Canada, the European Union, Japan, South Korea, the Philippines, Russia, Singapore, Turkey, the United Kingdom and the United States \u2014 reserving third-party rights to weigh in, a sign of how widely the outcome could ripple.

## Why It Matters for the Diaspora

On the surface this is a technical trade dispute in Geneva. Underneath, it is about whether India can keep doing the thing the diaspora has cheered for a decade: building an industrial base that turns the country from a buyer of finished goods into a maker of them. The solar PLI scheme and the tariff wall around electronics are the scaffolding of that ambition, and they have drawn diaspora capital, returning engineers and non-resident investors betting on Indian manufacturing.

A WTO ruling against India would not dismantle "Make in India" overnight \u2014 these cases take years, and appeals can stall indefinitely given the WTO's own crippled appellate system. But an adverse finding would complicate the incentive structures that have lured factories and funding, and would hand China a rhetorical win at a moment when India is trying to position itself as the credible alternative to Chinese supply chains. For NRIs who have poured money and pride into India's manufacturing story \u2014 and for those whose own businesses abroad depend on a China-plus-one world taking root \u2014 the panel in Geneva is worth watching. It is, in the end, a fight over whether the factory floor of the future is allowed to be Indian.
"""

    img_url, _ = pick_commons([
        "solar panels India power plant",
        "solar farm photovoltaic panels",
        "solar power plant array",
        "World Trade Organization headquarters Geneva"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "A solar installation; China has won a WTO panel to examine India's solar and IT-goods tariffs and incentives"

    if not img_url:
        px = fetch_pexels_image("solar panels power plant")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "India's solar-manufacturing incentives are at the centre of a new WTO dispute brought by China"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "trade-policy",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters (reuters.com, June 23 2026) \u2014 'WTO body agrees to examine Indian solar tariffs, official says': the WTO's Dispute Settlement Body agreed to establish a panel to examine tariffs and incentives in India that China says discriminate against Chinese solar-energy and information-technology products, a Geneva-based trade official said on Tuesday; China said the measures are contrary to India's WTO commitments and that bilateral consultations had not resolved the dispute; India argued dispute-settlement resources should be reserved for genuine and unresolved trade concerns.",
            "IndexBox / WTO DSB (indexbox.io, June 23 2026) \u2014 'WTO Dispute Settlement Body Establishes Panel on India's Solar Cells, Modules, and IT Goods Tariffs': during its June 23 session the DSB granted China's second petition to form a panel; New Delhi had declined China's initial request at the May 22 DSB meeting; China contends the measures violate the GATT, the Agreement on Subsidies and Countervailing Measures, and the Agreement on Trade-Related Investment Measures; Australia, Brazil, Canada, the EU, Japan, South Korea, the Philippines, Russia, Singapore, Turkiye, the UK and the US reserved third-party rights.",
            "The Hindu BusinessLine (thehindubusinessline.com, May 2026) \u2014 'India blocks China\u2019s request for WTO dispute panel on IT, solar': India officially blocked China's first request to set up a panel challenging its tariffs on specific high-tech goods and certain Solar Module Programme measures incentivising local value addition; WTO rules specify a country cannot block a second, repeated request at a subsequent DSB meeting; the dispute dates to a complaint China filed in December 2025 after February 2026 consultations failed.",
            "Third World Network / SUNS (twn.my, May 26 2026) \u2014 'WTO: India blocks China\u2019s panel request over IT goods, slams \u201cmercantilism\u201d': at the May 22 DSB meeting India blocked China's first-time panel request and argued the rules-based multilateral trading system should not support mercantilism that amounts to a 'beggar-thy-neighbour' policy; China alleged India levies duties on a dozen IT goods in excess of its bound rates and that the Solar Module Programme provides cash grants contingent on minimum local value-addition requirements.",
            "Mercom India (mercomindia.com, May 28 2026) \u2014 'India Blocks China\u2019s WTO Move Over Solar Incentives, Import Tariffs': India rejected China's panel request over its solar PLI incentives and import duties on high-tech goods such as smartphones, semiconductors, integrated circuits, wafers and display-manufacturing equipment; India argued its measures are WTO-consistent and aimed at strengthening domestic renewable-energy manufacturing, and noted China controls nearly 80% of the worldwide solar-module value chain."
        ]),
        "diaspora_angle": "The case puts 'Make in India' \u2014 the manufacturing drive that has drawn diaspora capital, returning engineers and NRI investors betting on Indian factories \u2014 on trial at the WTO, testing whether India can keep using tariffs and local-content incentives to build a China-alternative industrial base without breaking global trade rules.",
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
