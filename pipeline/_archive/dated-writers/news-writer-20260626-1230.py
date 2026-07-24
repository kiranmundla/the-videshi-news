#!/usr/bin/env python3
"""
Videshi News Writer — June 26, 2026 (12:30 UTC / 05:30 PDT run)
2 NEW articles, dedup-checked against last ~30 news articles:
  1. Weak monsoon — India draws up contingency plans for 315 vulnerable
     districts as June rainfall runs ~43% below average; IMD sees lowest in
     11 years (El Nino). Food-inflation/rural risk. NOT covered.
  2. Jio Platforms IPO — SEBI seeks clarification on Jio's DRHP; fresh issue
     of ~27 crore shares, ~Rs 35,000 cr, could be India's largest-ever
     listing; valuing the business ~$131bn. NOT covered (NSE IPO is covered,
     Jio isn't).
"""
import os, json, requests, urllib.parse, subprocess, io, re
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

# ─── Commons relevance gate (from IMAGE-SOURCING-RULES.md) ───
_COMMONS_NEGATIVE = {
    "us capitol":      ["state capitol", "pennsylvania", "texas capitol", "california state",
                        "harrisburg", "albany", "sacramento", "austin capitol"],
    "white house":     ["whitehouse station", "white house tennessee", "white house, tennessee"],
    "supreme court":   ["state supreme court", "uk supreme court"],
}
_COMMONS_STOP = {
    "the","a","an","of","in","on","at","to","for","and","or","with","as","by","from","is",
    "are","was","were","be","new","says","after","over","amid","how","why","what","2024",
    "2025","2026","india","indian","us","usa","american","uk","first","more","than",
    "people","man","woman","group","day","year","top","big","set","get","make","makes",
    "made","you","your","they","them","this","that","social","media","using","use","just",
    "here","need","know","quietly","almost","like","could","into","now","its","rare",
}

def _keywords(text):
    toks = re.findall(r"[A-Za-z][A-Za-z'-]+", text or "")
    out = []
    for t in toks:
        tl = t.lower()
        if len(tl) >= 4 and tl not in _COMMONS_STOP:
            out.append(tl)
    return out

def commons_relevance_ok(commons_title, headline, topic=""):
    title_l = (commons_title or "").lower()
    head_l  = (headline or "").lower()
    if not title_l:
        return False
    for concept, bad_tokens in _COMMONS_NEGATIVE.items():
        if concept in head_l:
            for bad in bad_tokens:
                if bad in title_l:
                    return False
    kws = set(_keywords(headline)) | set(_keywords(topic))
    if not kws:
        return True
    return any(kw in title_l for kw in kws)


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


def pick_commons(queries, headline, topic="", min_width=900):
    """Pick a Commons image that passes the relevance gate."""
    for q in queries:
        commons = fetch_wikimedia_commons_images(q)
        # relevance gate
        commons = [c for c in commons if commons_relevance_ok(c.get("title", ""), headline, topic)]
        if commons:
            pick = None
            for c in commons:
                if c["width"] >= min_width and c["original_url"].lower().endswith((".jpg", ".jpeg")):
                    pick = c
                    break
            pick = pick or commons[0]
            print(f"  \u2713 Commons pick: {pick.get('title','')}")
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


# ─── Article 1: Weak monsoon / 315-district contingency ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Weak monsoon contingency plans")
    print("="*60)

    slug = "india-weak-monsoon-315-districts-contingency-plan-el-nino-lowest-rainfall-11-years-food-inflation-20260626"
    headline = "India's Monsoon Is Running 43% Short, and 315 Districts Are Now on a Government Watch List"
    subheadline = "With June rains the weakest in years and El Nino threatening the driest season in over a decade, Delhi has drawn up emergency plans for the farm belt. For a diaspora that watches food prices and the rupee from afar, the stakes run from the dinner table to the markets."

    body = """Every year, the lives of more than a billion people hinge on a wind that turns. The southwest monsoon, which sweeps up the Indian subcontinent from June to September, delivers roughly 70% of the country's annual rainfall and waters nearly half its farmland \u2014 the half that has no irrigation and depends entirely on the sky. This year, the sky has been stingy. And in late June, the government did something it does only when it is genuinely worried: it put 315 districts on a formal watch list.

In the first three weeks of June, India received rainfall about 43% below the long-term average, one of the weakest starts in years. The India Meteorological Department, which had already trimmed its seasonal forecast to 90% of the long-period average \u2014 the threshold it calls "deficient" \u2014 now expects 2026 to deliver the lowest monsoon rainfall in 11 years, dragged down by an emerging El Nino. The last back-to-back drought years were 2014 and 2015.

## What the Government Is Actually Doing

On Tuesday, Farm Minister Shivraj Singh Chouhan said the centre had drawn up contingency plans for more than 300 districts deemed vulnerable to a weak monsoon, after a meeting with state farm ministers, officials and scientists. Of the 315 districts flagged, 111 were classified as high priority \u2014 places where less than a quarter of farmland is irrigated and a failed rain therefore means a failed crop. Another 76 were marked medium priority.

The advice flowing out to states is practical and a little grim. Farmers in rain-fed areas are being nudged toward short-duration, less thirsty crops \u2014 pulses, millets, oilseeds \u2014 instead of water-hungry paddy and cane. States have been told to repair ponds, check dams and water-harvesting structures, and to treat conservation as a priority. "Every drop of water is precious," Chouhan said.

## A Patchy, Uneven Picture

The monsoon is not failing everywhere at once, which is part of what makes it so hard to manage. After a two-week stall, the rains revived and finally reached Mumbai and parts of central India, with heavy downpours triggering a landslide at Maharashtra's Malshej Ghat. Bihar and the east have seen active spells. But the deficit in parts of central India \u2014 Chhattisgarh, Vidarbha, west Madhya Pradesh \u2014 has exceeded 60%, leaving farmers staring at the calendar, unsure whether to gamble on sowing now or wait.

Forecasters say the current and coming weeks offer the best window for planting before a possible mid-July lull. The knock-on effects are already visible in commodities: India, normally a sugar exporter, may stay off the export market for years as cane farmers in Maharashtra switch to soybeans, and output forecasts have been cut below domestic consumption.

## Why the Rupee and Your Grocery Bill Are Linked

A weak monsoon is not just an agricultural story; it is a macroeconomic one. Patchy rain pushes up food prices, and food is a heavy weight in India's inflation basket. The Reserve Bank of India's June bulletin explicitly flagged a poor monsoon \u2014 alongside any breakdown of the US-Iran peace deal \u2014 as a risk to growth that otherwise clocked a robust 7.8% in the last quarter. Higher food inflation complicates the central bank's room to keep interest rates low, and rural distress dents the consumption that powers much of the economy.

## Why It Matters for the Diaspora

For non-resident Indians, the monsoon can feel like distant weather news \u2014 until it isn't. Many in the diaspora still own farmland or property back home, send remittances to rural families, or have parents and relatives whose livelihoods rise and fall with the rains. A bad season can mean a call home about a lost crop, or a request for help that arrives a little earlier than usual.

There is a financial dimension too. A weak monsoon feeds food inflation, which pressures the rupee \u2014 the same rupee whose recent slide prompted the RBI's new diaspora deposit scheme. NRIs weighing whether to send money home, invest in Indian markets, or buy property are, knowingly or not, making a bet that partly turns on the weather. And for the millions who simply follow India from afar, the monsoon remains the closest thing the country has to a national heartbeat: when it falters, everyone from a Punjab farmer to a Mumbai trader to an engineer in New Jersey feels the rhythm change. The next three weeks of rain will tell much of the story for the rest of the year."""

    topic = "India monsoon agriculture drought"
    img_url, ititle = pick_commons([
        "monsoon rain India farmer paddy field",
        "Indian farmer rice field monsoon",
        "monsoon India agriculture",
        "paddy field India rain",
        "Indian farmer field"
    ], headline, topic)
    img_attribution = "Wikimedia Commons"
    img_caption = "A farmer in an Indian paddy field; a weak 2026 monsoon has put 315 districts on a government contingency watch list"

    if not img_url:
        px = fetch_pexels_image("indian farmer rice paddy field monsoon")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "India's monsoon is running well below average, threatening the farm belt and food prices"

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
            "Reuters (reuters.com, 24 June 2026) \u2014 'India makes contingency plans as weak monsoon threatens some farm areas': Farm Minister Shivraj Singh Chouhan said India drew up contingency plans for more than 300 districts vulnerable to a weak monsoon; monsoon rains so far ~43% below average; weather office forecasts weak rains through the week ending July 2; IMD defines normal as 96-104% of the 50-year average of 87 cm; last month forecast an El Nino-weakened 2026 monsoon, the lowest rainfall in 11 years; monsoon delivers ~70% of annual rains and waters farmland where nearly half lacks irrigation; 111 of 315 districts classified high priority (<25% irrigated), 76 medium priority; states advised to shift farmers to short-duration, less water-intensive crops (pulses, millets, oilseeds) and repair water-harvesting structures.",
            "Reuters (reuters.com, 22 June 2026) \u2014 'India monsoon revives after two-week stall, heads into central belt': first 21 days of June saw rainfall 42.2% below average; IMD forecast 90% of LPA for the season and 92% for June due to emergence of El Nino.",
            "The Hindu BusinessLine (thehindubusinessline.com, 23 June 2026) \u2014 'Monsoon enters Mumbai after a fortnight, eyes Gujarat and UP next': deficit in parts of central India has exceeded 60%; June 22-29 and June 29-July 6 the best windows for sowing; ECMWF indicates rainfall may weaken or shut down over parts of the region during the rest of July.",
            "Reuters (reuters.com, 22 June 2026) \u2014 'India likely won't export sugar for years as El Nino, ethanol squeeze supply': El Nino forecast to weaken monsoon to lowest in 11 years; June precipitation more than 40% below average prompting delayed planting; sugar output now forecast at 27.9 million tons, below ~28.5 million tons consumption.",
            "Outlook Money (outlookmoney.com, 23 June 2026) \u2014 'India's Growth Faces Risks From US-Iran Deal Breakdown, Weak Monsoon: RBI Bulletin': RBI June 2026 bulletin flags risks from a US-Iran deal breakdown and a poor monsoon; India grew 7.8% in Q4 FY2025-26; food and fuel prices show upward pressure."
        ]),
        "diaspora_angle": "A weak 2026 monsoon \u2014 running 43% below average with 315 farm districts now on a government watch list \u2014 threatens food inflation and rural incomes that directly touch the diaspora, whose remittances, Indian property and market investments, and family ties back home all rise and fall with the rains, and which feeds straight into the rupee pressure behind the RBI's new NRI deposit scheme.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Jio Platforms IPO / SEBI clarification ───

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Jio Platforms IPO")
    print("="*60)

    slug = "jio-platforms-ipo-sebi-clarification-drhp-35000-crore-largest-india-listing-ambani-reliance-20260626"
    headline = "Ambani's Jio Just Filed for What Could Be India's Biggest IPO Ever. The Regulator Is Already Asking Questions."
    subheadline = "Jio Platforms wants to raise about Rs 35,000 crore in an all-fresh share issue that could value the digital giant near $131 billion. SEBI has sought clarifications on the draft prospectus \u2014 a routine step before one of three mega-listings set to test the market this year."

    body = """For years it has been the most anticipated stock-market debut in India, dangled by Mukesh Ambani at one annual shareholder meeting after another. Now it is finally moving. Jio Platforms, the digital and telecom arm of Reliance Industries, has filed its draft red herring prospectus with the Securities and Exchange Board of India \u2014 and this week the regulator did what regulators do, sending back a request for clarifications before it gives the green light.

It is a procedural step, not a setback. SEBI routinely seeks additional information on draft papers before approving them, and it sought the same from fintech firm Razorpay, which filed confidentially on June 13. But for a listing of this scale, every move is watched. Ambani has called the Jio IPO "the most important value creation milestone this year."

## The Numbers Behind the Hype

Jio's proposed IPO is an entirely fresh issue of up to 27 crore equity shares \u2014 no offer-for-sale component, meaning existing investors are not cashing out and all the money raised flows into the company. The company is expected to raise around Rs 35,000 crore (roughly $3.7 billion), which would make it one of the largest public issues India has ever seen. Reports peg the valuation of the business at around $131 billion.

Most of the proceeds have a clear destination: Jio plans to use up to Rs 27,500 crore to prepay borrowings of its key subsidiary, Reliance Jio Infocomm. Cleaning up that debt, the prospectus says, will "position the company favourably for continued investment" in 5G network densification, fixed broadband, and AI and cloud services. The prospectus disclosed that Jio had 52.4 crore subscribers by the end of March, including 26.8 crore on 5G \u2014 making it the world's second-largest telecom operator by single-country subscribers, behind only China Mobile.

## A Crowded Runway

Jio is not arriving alone. Within weeks of each other, three giants have filed draft papers: Jio Platforms, the National Stock Exchange \u2014 the owner of the very market on which companies list \u2014 and the quick-commerce firm Zepto. Together they could raise between Rs 60,000 and Rs 70,000 crore, a stress test for the depth of domestic liquidity at a moment when equity mutual fund inflows have cooled. Actively managed equity funds drew net inflows of Rs 22,907 crore in May, the lowest monthly figure so far in 2026, though monthly SIP contributions held above Rs 30,000 crore.

The timing carries risk. Indian equities have had a bruising year, with benchmark indices well off their highs and Reliance shares down nearly 15% in 2026 amid weakness in its refining business. Whether the market can comfortably absorb a telecom-and-digital colossus, a market-infrastructure monopoly and a loss-making delivery challenger all at once is the open question hanging over Dalal Street.

## The Unusual Risk Disclosures

Jio's prospectus stood out for the futuristic risks it flagged \u2014 reading at times less like a financial document than science fiction. Among the threats it disclosed: AI failures and deepfakes, competition from satellite networks, and the impact of net-neutrality rules and gaming bans on future revenue. It is a reminder that the company is being pitched not merely as a phone network but as a bet on India's entire digital future.

## Why It Matters for the Diaspora

For the global Indian diaspora, the Jio IPO is more than a headline \u2014 it is a rare chance to own a piece of the infrastructure that connects the homeland. Many NRIs already invest in Indian equities through the portfolio investment route or GIFT City vehicles, and a marquee listing like this tends to draw diaspora money specifically. The reach is personal, too: Jio is the network that carries video calls between grandparents in Pune and grandchildren in Toronto, the SIM that NRIs buy the moment they land, the cheap data that pulled hundreds of millions of Indians online in a single decade.

A successful debut would be read worldwide as a vote of confidence in India's digital economy; a wobble, in a year of cooling inflows and falling Reliance shares, would carry the opposite signal. Either way, NRIs weighing where to place their India bets now have one more very large name to consider \u2014 and given the all-fresh structure, the entire price they pay goes to building the network rather than enriching early backers. The listing is still months away, but the most-awaited IPO in India's history has, at last, left the runway."""

    topic = "Reliance Jio IPO Mukesh Ambani telecom"
    # Person-led image: Mukesh Ambani via Wikipedia first
    img_url = None
    img_attribution = "Wikimedia Commons"
    img_caption = "Reliance chairman Mukesh Ambani, whose Jio Platforms has filed for what could be India's largest-ever IPO"
    try:
        encoded = urllib.parse.quote("Mukesh_Ambani")
        r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
                         headers={"User-Agent": UA}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            wimg = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
            if wimg:
                img_url = wimg
                print(f"  \u2713 Wikipedia image (Mukesh Ambani): {wimg[:80]}...")
    except Exception as e:
        print(f"  \u26a0 Wikipedia error: {e}")

    if not img_url:
        img_url, ititle = pick_commons([
            "Mukesh Ambani",
            "Reliance Industries headquarters Mumbai",
            "Jio logo",
            "Bombay Stock Exchange building",
            "National Stock Exchange India"
        ], headline, topic)

    if not img_url:
        px = fetch_pexels_image("stock exchange trading screen india")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Jio Platforms has filed for an IPO that could be India's largest-ever, set to test the market"

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
            "The Hindu BusinessLine (thehindubusinessline.com, 25 June 2026) \u2014 'SEBI seeks clarification from Jio Platforms, Razorpay on their draft prospectus': SEBI sought clarifications from Jio Platforms and Razorpay Software on DRHPs filed last week; Jio's proposed IPO is an entirely fresh issue of up to 27 crore equity shares with no offer-for-sale component, expected to raise around Rs 35,000 crore, possibly one of the largest public issues of the year; Razorpay filed confidentially on June 13; routine procedure before final approval.",
            "Reuters (reuters.com, 20 June 2026) \u2014 'Ambani's Jio Platforms files for $3.8 billion IPO that could be India's biggest, sources say': Reliance Jio Platforms filed regulatory papers for a Mumbai IPO to raise around $3.8 billion, a potential record listing; world's second-largest operator by single-country subscribers after China Mobile; Meta and Google among major foreign investors; targeting ~360 billion rupees (~2.9% of post-issue equity), valuing the business at around $131 billion; proceeds to repay ~275 billion rupees of Reliance Jio Infocomm debt; Ambani called it 'the most important value creation milestone this year.'",
            "Mint (livemint.com, 20 June 2026) \u2014 'Jio Platforms IPO could trump NSE's as India's biggest ever': Jio filed its DRHP with SEBI for a fresh issue of 270 million equity shares of Rs 10 face value, no offer for sale; plans to use up to Rs 27,500 crore to prepay borrowings of subsidiary Reliance Jio Infocomm; total IPO size pegged at Rs 32,000-35,000 crore ($3.4-3.7 billion); NSE filed draft papers on 17 June pegging its IPO at Rs 30,000 crore.",
            "Outlook Business (outlookbusiness.com, 24 June 2026) \u2014 'Jio, NSE And Zepto Are Raising Up To Rs 70,000 Cr; Is The Market Ready?': Jio Platforms, NSE and Zepto have filed draft papers for listings that could collectively raise Rs 60,000-70,000 crore; actively managed equity mutual funds received net inflows of Rs 22,907.77 crore in May, the lowest monthly inflow in 2026, down from April's Rs 38,440.20 crore; SIP inflows remained robust at Rs 30,954 crore.",
            "Inshorts / Outlook Money (23 June 2026) \u2014 Jio IPO may raise about Rs 36,000 crore with proceeds to repay debt; prospectus said Jio had 52.4 crore subscribers by March-end including 26.8 crore on 5G; DRHP flagged futuristic risks including AI failures, deepfakes, satellite-network competition, net neutrality and gaming bans; Reliance shares down nearly 15% in 2026 amid refining-business weakness."
        ]),
        "diaspora_angle": "Jio Platforms' filing for what could be India's largest-ever IPO \u2014 an all-fresh Rs 35,000 crore issue valuing the business near $131 billion \u2014 gives the global diaspora a rare chance to own a stake in the network that carries their calls home and powers India's digital economy, at a moment when three mega-listings test whether the market can absorb them.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    print("Videshi News Writer \u2014 2026-06-26 12:30 UTC run")
    id1 = write_article_1()
    id2 = write_article_2()
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Article 1 (weak monsoon contingency): {'OK id=' + str(id1) if id1 else 'FAILED'}")
    print(f"Article 2 (Jio Platforms IPO): {'OK id=' + str(id2) if id2 else 'FAILED'}")
