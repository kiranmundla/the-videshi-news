#!/usr/bin/env python3
"""
Videshi News Writer — June 22, 2026 (18:30 UTC run)
2 NEW articles:
  1. RBI is courting the diaspora's dollars — bearing the full hedging cost on
     fresh FCNR(B) deposits, exempting NRE/FCNR deposits from CRR/SLR, sending
     bank rates toward 7%, all to stabilise the rupee. Directly actionable for
     NRIs. (economy / personal-finance)
  2. Tata Electronics confirms a cyber breach; a ransomware crew leaked 200,000+
     files including purported Apple and Tesla trade secrets — a blow to India's
     bid to be the world's electronics workshop. (tech)
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


# ─── Article 1: RBI courts the diaspora's dollars ───────────────────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: RBI diaspora dollar drive (FCNR/NRE)")
    print("="*60)

    slug = "rbi-fcnr-nre-deposit-drive-hedging-cost-nri-dollars-rupee-7-percent-20260622"
    headline = "India's Central Bank Just Made the Diaspora an Offer It Has Used Only Once Before. NRI Deposit Rates Are Now Near 7%."
    subheadline = "To steady a sliding rupee, the Reserve Bank of India is absorbing the cost of currency risk on fresh NRI dollar deposits and freeing banks from reserve rules — the same playbook that pulled in tens of billions in 2013. Banks are racing to pass the windfall to non-resident Indians."

    body = """The Reserve Bank of India has reached into a toolkit it has opened only once before, and the target is the wallet of the global Indian diaspora. In a set of measures announced on June 5 and expanded through the month, the central bank is offering to bear the full cost of hedging on fresh foreign-currency deposits from non-resident Indians, freeing those deposits from reserve requirements, and in effect handing banks the room to push NRI deposit rates toward 7% — levels not seen in years.

The aim is the rupee. India's currency has been under sustained pressure in 2026, battered by a record exodus of foreign portfolio money — more than $30 billion pulled from Indian equities so far this year — and by the oil-price shock of the Gulf conflict. The RBI's answer is to court a more loyal source of dollars: the roughly 35 million people of Indian origin living abroad, whose deposits in Indian banks already total about $166 billion.

## What the RBI Actually Did

The centrepiece is a currency-swap facility. Until September 30, the RBI will absorb the full hedging cost for banks that raise fresh three-to-five-year Foreign Currency Non-Resident (Bank), or FCNR(B), deposits — the dollar-denominated accounts NRIs use to park savings without taking on rupee risk. Hedging that currency exposure normally costs a bank around 3% a year; with the central bank picking up that tab, lenders can pass the saving straight to depositors.

They have moved fast. Banks that were offering about 3% on FCNR(B) deposits have lifted rates into the 6-7% range. Bandhan Bank now advertises 7.1% on deposits of $1 million or more and 7% below that, for tenors of three to five years. State Bank of India's managing director Ashwini Kumar Tewari called the roughly 3% advantage real "new money" and said the bank would go "all out" to market the scheme to NRIs in the Gulf, the United States and Europe.

The RBI then went further. It exempted these fresh FCNR(B) deposits — and, from June 19, fresh three-year-plus Non-Resident (External) Rupee, or NRE, term deposits — from the cash reserve ratio and statutory liquidity ratio. Normally a bank can lend out only about ₹79 of every ₹100 it takes in, parking the rest with the RBI or in government bonds. With the exemption, the whole deposit can be lent on, giving banks every incentive to compete for diaspora money with still-higher rates.

## A Move With Form

This is not an untested gamble. The RBI ran almost exactly the same play in 2013, when a collapsing rupee during the "taper tantrum" forced its hand. That swap window helped lift total NRI deposits from $71 billion in FY13 to $127 billion by FY16, with FCNR(B) balances alone jumping from $15 billion to $45 billion. A Bank of Baroda research report this month concluded the current measure is "likely to support growth in overall NRI deposits as seen between the FY13-16 period."

The scale of the bet varies by who is counting. Tewari pegged likely inflows at upwards of $10 billion for the banking system; the brokerage Nomura put the figure as high as $55 billion, with the bulk arriving in August and September, and noted that because US dollar rates are far higher now than in 2013, the returns on offer are richer. Standard Chartered's India chief called the facility a potential "game-changer." Indian banks are now lobbying the RBI to let their offshore units in Gujarat's GIFT City help fund the deposits, a sign of how aggressively they want to chase the money.

## Why the Diaspora Should Pay Attention

For an NRI sitting on dollar savings, this is one of the rare moments when the macroeconomics of Mumbai land directly in a personal bank statement. A three-to-five-year FCNR(B) deposit now offers a dollar return near 7% with no rupee-conversion risk — a combination that did not exist a month ago and is, by design, time-limited to deposits booked before September 30. NRE deposits, which are rupee accounts but fully repatriable and tax-free in India, are getting the same reserve relief, nudging their rates up too.

There are the usual cautions. The headline rates apply to specific tenors and, in some cases, to large balances; the fine print on lock-ins, premature-withdrawal penalties and the choice between a dollar (FCNR) and a rupee (NRE) account matters, and an NRI betting on the rupee's direction will weigh those two very differently. But the broader signal is unmistakable: after a year in which the rupee, study-abroad budgets and remittance math have all moved against diaspora families, India is, for once, competing hard for their money — and paying a premium to win it. The window closes at the end of September."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url, ctitle = pick_commons([
        "Reserve Bank of India building Mumbai",
        "Reserve Bank of India headquarters",
        "Reserve Bank of India",
        "Indian rupee banknotes"
    ])
    img_caption = "The Reserve Bank of India's headquarters in Mumbai; the central bank is courting non-resident Indian deposits to steady the rupee"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("indian rupee currency money")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Indian rupee notes; the RBI is offering NRIs richer deposit rates to draw in dollars"

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
            "Reuters \u2014 Indian banks push for lending via GIFT City units in dollar deposit scheme, sources say (June 19-20, 2026): RBI offered to subsidise hedging costs for FCNR deposits to attract diaspora dollars; scheme echoes 2013; Nomura estimates the scheme could attract $55 billion, bulk in August-September; banks seek RBI nod to fund FCNR deposits via GIFT City offshore units",
            "The Hindu Business Line \u2014 RBI seeks daily data from banks under its limited period measures to attract foreign capital (June 19, 2026): banks raised FCNR(B) USD deposit rates in the 3-5 year tenor to 6-7% from ~3%; RBI to bear full hedging cost on fresh 3-5 year FCNR(B) deposits till Sep 30, 2026; such deposits exempt from CRR and SLR; concessional forex swap for ECBs by PSUs till Sep 30",
            "The Hindu Business Line \u2014 RBI exempts banks from maintaining statutory reserve ratios on fresh NRE term deposits (June 19, 2026): fresh NRE term deposits of 3 years or more mobilised June 19-Sep 30 2026 exempt from CRR (and earlier SLR); CRR at 3% and SLR at 18%; transfers from NRO to NRE accounts do not qualify",
            "Devdiscourse / Bank of Baroda research \u2014 RBI looks to revive NRI deposit growth through FCNR(B) route (June 2026): total NRI deposits flatlined at $166bn in FY26 from $165bn; NRI deposits grew 3.1% annually over five years vs 7.8% for overall deposits; 2013 swap window lifted total NRI deposits from $71bn (FY13) to $127bn (FY16), FCNR(B) from $15bn to $45bn",
            "Livemint \u2014 RBI to bear hedging costs for banks' foreign currency deposits, flows of over $10 bn seen (June 2026): Governor Sanjay Malhotra announced full hedging cost facility till Sep 30, 2026; SBI MD Ashwini Kumar Tewari pegged flows upwards of $10 billion, citing a clear 3% advantage; Standard Chartered's P.D. Singh called it a 'game-changer'",
            "Tripura Star News \u2014 Bandhan Bank Increases FCNR (B) Deposit Offerings (June 20, 2026): Bandhan Bank offering 7.1% on FCNR(B) deposits of $1 million and above and 7% up to $1 million, for 3-5 year tenors, following the RBI's USD-INR forex swap facility"
        ]),
        "diaspora_angle": "The RBI's drive deliberately targets non-resident Indians' savings: FCNR(B) and NRE deposit rates near 7% with the central bank absorbing currency-hedging risk make this one of the rare times India is paying a premium specifically to win diaspora money \u2014 and the offer expires September 30.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Tata Electronics breach exposes Apple/Tesla secrets ─────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Tata Electronics cyber breach")
    print("="*60)

    slug = "tata-electronics-cyber-breach-apple-tesla-trade-secrets-world-leaks-ransomware-20260622"
    headline = "Hackers Just Dumped 200,000 Files From an Indian Apple Supplier. Some Are Marked 'Trade Secret.'"
    subheadline = "Tata Electronics, the Tata group's bet on making India the world's iPhone workshop, has confirmed a cyber breach after a ransomware crew posted purported Apple and Tesla design documents on the dark web. The leak lands at the most sensitive possible moment for India's manufacturing ambitions."

    body = """Tata Electronics, the company at the heart of India's drive to become a global electronics manufacturing hub, confirmed on Monday that it had suffered a cybersecurity breach — after security researchers reported that a ransomware group had posted more than 200,000 files allegedly stolen from the firm on the dark web, including purported trade secrets belonging to two of its biggest customers, Apple and Tesla.

"A few weeks ago, Tata Electronics identified a cybersecurity incident on some of our systems," the company said in a statement. "Our response protocols were deployed immediately, and the incident has had no impact on our operations across businesses, which remain unaffected." A source familiar with the matter told Reuters that Tata had received a ransom demand, and that Apple was investigating, with "a full analysis going on." Apple and Tesla did not respond to requests for comment.

## What Was Leaked

The trove is large and, according to researchers who examined it, highly sensitive. Investigators identified at least 181 Apple-related files and folders, some carrying Apple's internal confidentiality markings, among them a 52-page document setting out inspection requirements for iPhone circuit-board components. Many of the files traced back to Tata's facility in Hosur, Tamil Nadu, a key site producing components for Apple products.

The cache also appears to contain Tesla material. Researchers found documents tied to "Project Highland," Tesla's internal codename for the redesigned Model 3 — engineering drawings, manufacturing specifications, and files referring to a charge-port controller used in North American vehicles, with some labelled as trade secrets. The wider archive reportedly included internal emails, log files, quality standards, and even copies of employee passports, and had been accessible on the dark web since at least June 10.

Responsibility was claimed by World Leaks, a group that emerged in early 2025 as a rebrand of the Hunters International ransomware operation. The crew has increasingly shifted from encrypting victims' files to simply stealing data and threatening to publish it unless paid — a model that makes a supplier like Tata, sitting on the secrets of multiple global clients, an especially rich target.

## Why This Stings for India

The timing could hardly be worse. Tata Electronics is the symbol of India's most ambitious industrial bet: persuading Apple and others to shift manufacturing out of China and into India. The Tata group acquired Wistron's iPhone assembly operations, took a controlling stake in a Pegatron plant, and is building out component production and a semiconductor business — all premised on convincing the world's most secretive technology companies that their crown-jewel designs are safe on Indian soil.

A breach that exposes a customer's trade secrets cuts at exactly that promise. The episode shows how attackers can compromise a single supplier to reach the confidential information of several multinationals at once — a structural weakness of the global supply chain that India is racing to climb. It is not an isolated scare, either: a cyberattack on Taiwan's Foxconn earlier this year exposed documents from Apple, Nvidia and others, and a separate incident hit the Chinese assembler Luxshare. India's manufacturers are joining a club whose membership comes with a target on its back.

## The Diaspora Stake

For the Indian diaspora, "Make in India" is more than a slogan. The push has reshaped Apple's supply map, created hundreds of thousands of jobs in Tamil Nadu and Karnataka, and become a point of pride for NRIs who watch India move up the technology value chain rather than merely supplying it with engineers. Indian-origin executives sit in senior roles across Apple, Tesla and the broader chip industry, and the credibility of India as a manufacturing base touches diaspora-run businesses that increasingly source from it.

Tata has stressed that its operations are running normally, and there is no suggestion that production lines have been disrupted. But the reputational question is harder to wave away. Apple's willingness to deepen its India footprint rests on trust, and a leak carrying its confidentiality stamps — alongside separate scrutiny of environmental complaints at the Hosur plant — adds friction to a relationship India badly wants to expand. The files cannot be un-leaked; a CAD model or a schematic does not lose value when a password is reset. For a country selling itself as the safe alternative to China's factory floor, the next test is less about cleaning up this breach than about proving it will not become routine."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url, ctitle = pick_commons([
        "Tata Group headquarters Bombay House",
        "iPhone assembly manufacturing",
        "smartphone circuit board assembly",
        "iPhone 15"
    ])
    img_caption = "Bombay House, the Tata group's Mumbai headquarters; Tata Electronics confirmed a cyber breach affecting customer data"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("smartphone circuit board manufacturing")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A smartphone circuit board on an assembly line; a breach at Tata Electronics exposed component design files"

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
            "Reuters \u2014 India's Tata Electronics hit by cyber breach claiming to expose Apple, Tesla trade secrets (June 22, 2026): Tata confirmed a recent cybersecurity incident; ransomware group World Leaks posted 200,000+ files including purported Apple and Tesla component design and specification papers; Tata received a ransom demand; Apple investigating; no impact on operations per Tata",
            "The Tech Portal \u2014 Tata Electronics suffers massive data breach, leaked files allegedly include Apple and Tesla documents (June 22, 2026): at least 181 Apple-related files/folders, including a 52-page iPhone circuit-board inspection document with Apple confidentiality markings; Tesla 'Project Highland' (redesigned Model 3) drawings, specs and a charge-port controller file labelled trade secret; many files linked to Tata's Hosur, Tamil Nadu facility",
            "Footstream / News Corner (via Reuters) \u2014 Tata Electronics hit by massive cyber breach exposing Apple and Tesla secrets (June 22, 2026): leaked cache includes internal emails, log files, engineering drawings, product specs, quality standards and employee passports; data accessible on dark web since at least June 10; World Leaks is a 2025 rebrand of Hunters International, focused on data exfiltration over encryption",
            "PYMNTS \u2014 Supply Chain Cyberattack Puts Enterprise Trade Secrets at Risk (2026): supplier-level breaches (e.g. Luxshare) can expose secrets of Apple, Nvidia, Tesla and others at once; leaked CAD models and circuit-board schematics retain value long after a breach, unlike credentials",
            "Bharat Horizon \u2014 Tata Electronics hit by cyber breach; Apple, Tesla secrets at risk (June 2026): Tata operates a major Hosur facility making iPhone enclosures/components and is building a Tesla-parts plant; incident comes as Tata faces separate environmental allegations at Hosur; attackers believed to have used phishing"
        ]),
        "diaspora_angle": "India's bid to become the world's electronics workshop \u2014 a source of pride and jobs for the diaspora and a magnet for Indian-origin tech talent \u2014 rests on convincing Apple and Tesla their designs are safe in India, and a leak carrying customer confidentiality stamps strikes directly at that promise.",
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
