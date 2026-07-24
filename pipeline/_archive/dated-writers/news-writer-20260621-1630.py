#!/usr/bin/env python3
"""
Videshi News Writer — June 21, 2026 (16:30 UTC run)
2 NEW articles:
  1. RBI cuts FY27 growth to 6.6%, holds repo at 5.25% as Gulf war clouds outlook (news / economy)
  2. India's basmati exports squeezed by the Gulf war and an African dollar crunch (news / economy-trade)
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


# ─── Article 1: RBI growth downgrade / wait-and-watch ─────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: RBI growth downgrade to 6.6%")
    print("="*60)

    slug = "rbi-growth-cut-6-6-percent-fy27-mpc-minutes-repo-5-25-malhotra-gulf-war-monsoon-20260621"
    headline = "India's Central Bank Just Cut Its Growth Forecast \u2014 and Pointed Straight at the Gulf War and the Monsoon"
    subheadline = "Minutes from the Reserve Bank's June meeting, released this week, show a rate panel choosing caution over action: growth for the new fiscal year trimmed to 6.6%, the repo rate frozen at 5.25%, and inflation forecasts nudged up as oil and a weak monsoon cloud the view."

    body = """India's central bank has done something it rarely does in public: it has admitted it is flying with a clouded windscreen. The minutes of the Reserve Bank of India's June Monetary Policy Committee meeting, released this past week, lay out a rate-setting panel that chose to wait rather than move \u2014 holding the benchmark repo rate at 5.25%, keeping its stance neutral, and quietly cutting its growth forecast for the financial year that runs to March 2027 to 6.6%, down from the 6.9% it had projected only in April. The reasons it gave were unusually blunt: the war in West Asia and the threat of a poor monsoon.

For the diaspora, the RBI's caution is not abstract. The same forces the committee is worried about \u2014 oil prices, a wobbling rupee, food inflation \u2014 are the forces that decide how far a remittance stretches when it lands in a parent's account in Pune or a sibling's in Kochi, what an NRE or FCNR deposit earns, and how the Indian assets in a diaspora portfolio are likely to perform. When the RBI flags risk, it is flagging risk to the household economy that connects millions of overseas Indians to home.

## A Panel That Chose to Wait

The decision on June 5 to hold the repo rate at 5.25% was unanimous, and the minutes show why. Governor Sanjay Malhotra wrote that headline inflation was within the target band and core inflation contained, "suggesting that underlying inflation pressures remained subdued" \u2014 but immediately added the caveat that has defined this moment: "we need to be watchful of the inflation trajectory." He said he preferred a "wait and watch" approach, guided by the evolving geopolitical scenario in West Asia and the impact of a poor monsoon.

Deputy Governor Poonam Gupta echoed him, arguing explicitly against a "preemptive policy pivot." "We ought to wait a bit more for global as well as weather related uncertainties to play out over the coming months," she said. Among the external members, Ram Singh and Nagesh Kumar leaned the same way. Only Saugata Bhattacharya struck a more hawkish note, warning that the balance of risks had "tilted towards embedding inflationary pressures." The market, which had begun to wager on a rate hike as oil spiked, was effectively told to stand down.

## The Numbers Behind the Caution

The growth downgrade tells the story in one figure. GDP growth for 2026-27 is now pegged at 6.6%, trimmed from 6.9%, and well below the 7.6% the economy is estimated to have managed in 2025-26. The committee attributed the cut to prolonged global supply-chain disruptions, volatility in financial markets, and weather-related shocks. On inflation, the RBI raised its forecast for the year to an average of 5.1%, up from 4.6%, with a projected peak of 5.9% in the third quarter \u2014 and it built those numbers on an assumption of crude oil averaging $95 a barrel.

That oil assumption is the hinge on which everything turns. Brent crude, which had vaulted above $100 a barrel at the peak of hostilities between Iran and the United States, has since slid back toward $80 as the two sides edged toward a deal. But the RBI's planning number sits between those two poles \u2014 a tacit acknowledgement that nobody on the committee is willing to bet the war is over. Retail inflation stood at just under 4% in May, comfortably inside the 2-6% tolerance band, which is precisely why the panel felt it had room to wait.

## The Rupee, Steadied by Intervention

Behind the rate decision sits a currency the RBI has been working hard to defend. The rupee fell as much as 6% against the dollar this year, touching an all-time low near 97, before a package of central-bank measures and easing oil prices pulled it back toward 94.5. Those measures \u2014 including subsidising hedging costs to attract foreign-currency deposits from the diaspora \u2014 have pushed the RBI's short-dollar forward book to a record near $110 billion, and analysts at Goldman Sachs caution that the inflows are likely to be absorbed into rebuilding reserves rather than driving the rupee sharply higher. India's foreign-exchange reserves have fallen from a March peak of $728.5 billion to about $681.6 billion.

## Why It Matters for the Diaspora

For overseas Indians, the RBI's June meeting is a map of the year ahead. A weaker rupee makes remittances go further at the moment of transfer, but the inflation the central bank is guarding against erodes that gain at the grocery store back home. The diaspora-focused deposit schemes the RBI is leaning on \u2014 designed to pull dollars in from NRIs \u2014 carry better returns precisely because the currency is under pressure. And the growth downgrade, modest as it looks, is the kind of signal that ripples through the equity and bond holdings that diaspora investors increasingly own. India's economy remains one of the world's fastest-growing. But its central bank has just told everyone, in writing, that it is watching the Gulf and the sky before it makes its next move."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = ""
    img_attribution = "Wikimedia Commons"

    # Prefer Governor Sanjay Malhotra's own photo (named protagonist)
    person_img = fetch_wikipedia_person_image("Sanjay Malhotra (banker)")
    if not person_img:
        person_img = fetch_wikipedia_person_image("Sanjay Malhotra")
    if person_img:
        img_url = person_img
        img_caption = "Reserve Bank of India Governor Sanjay Malhotra, whose Monetary Policy Committee held the repo rate at 5.25% and trimmed India's growth forecast to 6.6%"
        img_attribution = "Wikimedia Commons"

    if not img_url:
        for q in ["Reserve Bank of India building", "Reserve Bank of India headquarters Mumbai", "Indian rupee currency notes"]:
            commons = fetch_wikimedia_commons_images(q)
            if commons:
                img_url = commons[0]["url"]
                img_caption = "The Reserve Bank of India; its June rate panel held the repo rate at 5.25% and cut the 2026-27 growth forecast to 6.6%, citing the Gulf war and a weak monsoon"
                break

    if not img_url:
        px = fetch_pexels_image("indian rupee money currency")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Indian rupee notes; the RBI held rates steady and downgraded its growth forecast amid Gulf-war and monsoon risks"

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
            "Reserve Bank of India \u2014 Minutes of the June 2026 Monetary Policy Committee meeting (released week of June 19); repo rate held unanimously at 5.25%, neutral stance retained; Governor Sanjay Malhotra: 'we need to be watchful of the inflation trajectory', prefers 'wait and watch'",
            "Reuters \u2014 'India rate panel downplays case for pre-emptive rate move in meeting minutes': FY27 GDP growth trimmed to 6.6% from 6.9% (vs ~7.6% in 2025-26); inflation forecast raised to 5.1% from 4.6%, peak 5.9% in Q3; crude assumed at $95/bbl; Deputy Governor Poonam Gupta against 'preemptive policy pivot'; Saugata Bhattacharya more hawkish",
            "Forbes India / Outlook Money / Devdiscourse \u2014 June 5 MPC announcement detail: GDP recalibrated to 6.6%; quarterly path Q1 6.6%, Q2 6.3%, Q3 6.5%, Q4 6.8%; inflation 5.1% for 2026-27",
            "Reuters \u2014 rupee recovered toward 94.5/dollar from a record low near 97 after RBI measures and easing oil; RBI short-dollar forward book near record $110bn; FX reserves down from $728.5bn (March) to $681.6bn; Brent eased from above $100 toward $80"
        ]),
        "diaspora_angle": "The oil, rupee and food-inflation risks the RBI is guarding against directly govern how far an NRI remittance stretches at home, what NRE/FCNR deposits earn, and how diaspora-held Indian equities and bonds perform \u2014 and the diaspora deposit schemes the RBI is leaning on to attract dollars carry better returns precisely because the currency is under pressure.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Basmati exports squeezed by war + African dollar crunch ─

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: India's rice exports squeezed")
    print("="*60)

    slug = "india-rice-exports-value-down-basmati-gulf-war-africa-dollar-crunch-record-stocks-fy26-20260621"
    headline = "India Has More Rice Than It Can Store \u2014 and Is Suddenly Struggling to Sell It Abroad"
    subheadline = "Government warehouses are bulging with record grain, yet the value of India's rice exports has fallen in the past year, caught between a war that froze basmati shipments to the Gulf and a dollar shortage that stalled buyers in Africa. The squeeze reaches every diaspora kitchen that runs on a sack of Indian rice."

    body = """India is the world's rice merchant. It ships more rice abroad than the next three exporters \u2014 Thailand, Vietnam and Pakistan \u2014 combined, accounting for more than 40% of all the rice traded on the planet. So when India's rice exports stumble, the tremor is felt from a Lagos market stall to a Saudi supermarket to the kitchen of an Indian family in New Jersey reaching for a familiar bag of basmati. And right now, even as the country sits on the largest grain stockpile in its history, the value of those exports is sliding.

For the diaspora, rice is more than a commodity \u2014 it is the staple that anchors a home kitchen abroad, the bag of basmati that turns an apartment in London or Toronto into something that smells like home. The forces buffeting India's rice trade are the same ones reshaping diaspora grocery bills: a war in the Gulf that has scrambled the basmati routes overseas Indians depend on, and a wider trade slump that is quietly nudging prices and availability on shelves far from India.

## A Glut at Home

Start with the paradox. India's rice stocks in government warehouses climbed about 15% from a year earlier to a record 68.43 million metric tons at the start of June \u2014 more than five times the government's own target of 13.5 million tons for July. Wheat stocks hit a five-year peak of 53.41 million tons, roughly double the target. Back-to-back bumper harvests, helped by strong monsoon rains in the previous crop year, drove rice and wheat production to record highs of 154.02 million and 120.66 million tons respectively.

The pile is so large that the U.S. Department of Agriculture expects New Delhi to keep releasing rice and wheat into the domestic market at subsidised prices to bring stocks down to manageable levels \u2014 a move that should keep a lid on food prices at home, even with forecasters warning of a weaker, El Nino-influenced monsoon this year. On paper, India has never been better placed to dominate the global rice trade. The problem is the trade itself.

## A War That Froze the Basmati Routes

The first squeeze came from the Gulf. India's premium basmati rice goes overwhelmingly to buyers in Saudi Arabia, Iraq, Iran and the United Arab Emirates \u2014 and those are precisely the routes disrupted by the war between Iran and the United States. In the first four months of 2026, basmati exports fell 7% to 2.3 million tons as cargoes bound for Iran, Iraq, Qatar and Saudi Arabia were delayed in transit and buyers held back on new deals. Iran was India's single biggest basmati market until last year, when Saudi Arabia overtook it; the conflict has battered both ends of that trade.

Overall rice exports in January-April slipped 1.3% from a year earlier to 8.39 million tons \u2014 a marginal drop in volume, but one that, combined with softening prices, has pulled the value of India's rice exports down around 10% over the financial year. For diaspora households in the Gulf, where Indian basmati is a kitchen fixture, the disruption has meant tighter supply and firmer prices on exactly the variety they buy most.

## The African Dollar Crunch

The second squeeze is quieter but just as damaging, and it sits far from the headlines about the Gulf. India's non-basmati rice flows in huge volumes to West Africa \u2014 Nigeria, Benin, Ivory Coast, Guinea, Cameroon. But several of those economies are starved of U.S. dollars. Exporters describe buyers in Nigeria, Senegal and Benin facing a severe shortage of hard currency, with some asking to settle trades in their own local currencies \u2014 an offer Indian exporters have largely refused. The result has been delayed contracts and a drop in fresh purchase orders.

Indian rice remains the cheapest in the world: about $350 a tonne for 5% broken grade, at least $40 below Pakistan, $60 below Vietnam and $145 below Thailand, with an even wider edge in parboiled rice. "Indian rice is the most competitive in the global market, and competitors will find it tough to match Indian rates," one exporter said. Yet competitiveness cannot conjure dollars that African buyers do not have, and exporters admit a lack of unity at home \u2014 each undercutting the other \u2014 is eroding the value they capture. Looking ahead, the USDA still projects India shipping a record 24.5 to 25 million tons of rice in the 2026-27 season, betting that the glut and low prices will eventually win through.

## Why the Diaspora Should Care

For overseas Indians, the rice story is the supply chain behind their pantry. The basmati that fills shelves in Gulf and Western grocery stores rides the same routes now disrupted by war, and prices on the premium varieties the diaspora prefers tend to firm when those routes seize up. At the macro level, a weaker rice trade dents farm incomes in the very states many NRI families come from, and shapes the rural economy they send money back to. India's granaries have rarely been fuller. Whether that abundance reaches the world \u2014 and the diaspora's dinner table \u2014 now depends on a war winding down and a dollar shortage easing thousands of miles away."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = ""
    img_attribution = "Wikimedia Commons"

    for q in ["basmati rice grain", "rice sacks market India", "paddy rice harvest India", "rice grain bag"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            img_caption = "Indian rice; government warehouses hold a record 68.43 million tons of rice even as the value of exports falls amid the Gulf war and an African dollar shortage"
            break

    if not img_url:
        px = fetch_pexels_image("basmati rice grains")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Basmati rice; India's premium rice exports to the Gulf have been disrupted by the Iran war even as domestic stocks hit record highs"

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
            "Reuters \u2014 'India's rice stocks climb to record high; wheat inventories at five-year peak': state rice reserves a record 68.43 mt as of June 1 (vs 13.5 mt target); wheat 53.41 mt (5-year high); 2025/26 record output rice 154.02 mt, wheat 120.66 mt; India ~40% of global rice exports",
            "The Hindu BusinessLine \u2014 'Facing African hurdles, Indian rice exports value down 10% in FY26': dollar shortage in Nigeria, Senegal, Benin stalled purchases; Indian rice most competitive at $350/t for 5% broken (vs Pakistan +$40, Vietnam +$60, Thailand +$145); 2026-27 exports projected 24.5 mt",
            "Reuters \u2014 'India rice exports decline as Iran war curbs basmati shipments to Gulf': Jan-April rice exports down 1.3% to 8.39 mt; basmati exports down 7% to 2.3 mt; cargoes to Iran, Iraq, Qatar, Saudi Arabia delayed; Saudi Arabia overtook Iran as top basmati market last year",
            "USDA Foreign Agricultural Service \u2014 'India: Grain and Feed Annual' and June 'Grain: World Markets and Trade': India to keep ~40% of global rice trade; record rice exports forecast ~25 mt in MY 2026/27; government expected to release subsidised grain domestically to draw down record stocks"
        ]),
        "diaspora_angle": "Indian rice is the staple anchoring diaspora kitchens worldwide; the Gulf-war disruption to basmati routes and the African dollar crunch tighten supply and firm prices on exactly the varieties overseas Indians buy most, while a weaker rice trade dents farm incomes in the rural states many NRI families come from and send remittances to.",
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
