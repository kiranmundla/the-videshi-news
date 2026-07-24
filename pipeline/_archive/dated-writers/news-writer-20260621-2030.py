#!/usr/bin/env python3
"""
Videshi News Writer — June 21, 2026 (20:30 UTC run)
2 NEW articles:
  1. Jio Platforms files for India's potentially largest-ever IPO (news / markets)
  2. India's IT index hits a three-year low after Accenture's warning (news / tech-economy)
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



# ─── Article 1: Jio Platforms files for India's largest-ever IPO ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Jio Platforms IPO")
    print("="*60)

    slug = "reliance-jio-platforms-ipo-drhp-sebi-filing-mukesh-ambani-record-india-listing-20260621"
    headline = "Ambani Just Filed the Papers for What Could Be India's Biggest-Ever IPO. The Diaspora's Phone Carrier Is Going Public."
    subheadline = "The board of Jio Platforms approved its draft prospectus on June 19 and filed with India's market regulator the same day, clearing the way for a Mumbai listing that bankers say could raise around $3.8 billion — and that Mukesh Ambani called Reliance's 'most important value-creation milestone this year.'"

    body = """India's most-watched corporate event of the year finally has a paper trail. At Reliance Industries' 49th annual general meeting on June 19, chairman Mukesh Ambani told shareholders that the board of Jio Platforms — the digital and telecom arm that runs the carrier nearly half a billion Indians use — had approved its draft red herring prospectus and would file it with the Securities and Exchange Board of India that same day. For a listing that has been rumoured, deferred and dissected for the better part of six years, the filing turns speculation into a formal process.

The numbers are the kind that reset records. The offer is structured as a fresh issue of up to 27 crore (270 million) equity shares with a face value of ₹10 each, priced through a book-building process. People familiar with the plan told Reuters the IPO is targeting roughly ₹360 billion, or about $3.8 billion — which would make it the largest public offering in Indian history. The size represents only about 2.9% of Jio's post-issue equity, a sliver made possible by recently relaxed SEBI rules that let companies with a post-issue market capitalisation above ₹5 lakh crore float as little as 2.5% to the public. Brokerages have pegged Jio Platforms' value at around $180 billion.

For the Indian diaspora, this is not an abstract Mumbai market story. Jio Platforms houses Reliance Jio Infocomm, the world's second-largest telecom operator by subscribers after China Mobile, with roughly 500 million users and about 60% of India's data traffic. It is, very literally, the company that connects the relatives NRIs call home, that powers the video streams of cricket and Bollywood watched across time zones, and that underpins the UPI payments and digital services families lean on when they visit. A stake in Jio is, for many overseas Indians, a stake in the infrastructure of their own connection to India.

There is also a global-investor through-line that the diaspora's tech crowd will recognise. When Jio raised a wave of capital in 2020, the marquee backers included Meta and Alphabet's Google — Meta still holds nearly 10% of Jio Platforms and Google about 7.7%, with Reliance owning more than 66%. Those were bets on India's digital economy of 1.4 billion people, cheap data and a mobile-first young population moving online at scale. The IPO now offers public investors, including non-resident Indians who can participate through permitted routes, a chance to buy into the same thesis the Silicon Valley giants did.

Ambani framed the listing in nation-building terms, telling shareholders the float "will demonstrate to the world that India can build technology companies of global scale, global capability, and global value." He also made it a generational handover: his children — Akash, Isha and Anant — are leading the IPO process, which he described as the family's next chapter of "value creation." Jio outlined five strategic priorities for its next phase, spanning 5G expansion, home broadband, artificial intelligence and international technology platforms.

The timing is conspicuous. The offering lands in a jittery market: the benchmark Sensex has fallen nearly 10% so far in 2026, weighed down by valuation worries, foreign outflows and the economic fallout of the Gulf conflict on India as a major oil importer. IPO activity has been subdued all year as sentiment soured. Yet the heavyweights are moving anyway — the National Stock Exchange of India itself filed for an IPO the same week. Analysts caution that a richly valued Jio listing could leave Reliance Industries trading at a holding-company discount as value migrates to the separately listed unit.

What happens next is a regulatory clock, not a calendar date. The draft prospectus now sits with SEBI, the BSE and the NSE for review; a price band, final issue size and listing window will follow only after approvals and market conditions allow. The offer is explicitly subject to the regulator's sign-off, and Reliance has cautioned that final details could shift closer to the listing. For diaspora investors weighing whether to participate, the practical questions — eligibility under NRI investment rules, the eventual price band, and how much of Jio's lofty private valuation survives contact with public markets — remain open. What is settled, after years of waiting, is that the process has begun."""

    img_url = None
    img_caption = ""
    img_attribution = ""

    # Mukesh Ambani — Wikipedia person image (mandatory first for person-led article)
    person_img = fetch_wikipedia_person_image("Mukesh Ambani")
    if person_img:
        img_url = person_img
        img_caption = "Reliance Industries chairman Mukesh Ambani, who announced the Jio Platforms IPO filing at the company's annual general meeting"
        img_attribution = "Wikimedia Commons"

    if not img_url:
        for q in ["Mukesh Ambani Reliance", "Reliance Jio logo", "Reliance Industries headquarters Mumbai"]:
            commons = fetch_wikimedia_commons_images(q)
            if commons:
                img_url = commons[0]["url"]
                img_caption = "Reliance Jio, the telecom and digital arm filing for a record India IPO"
                img_attribution = "Wikimedia Commons"
                break

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
            "Reuters — 'Ambani's Jio Platforms eyes record $3.8 billion Indian IPO, sources say' (June 19, 2026): fresh issue of up to 270 million shares, ~₹360 billion (~$3.81 billion) target, about 2.9% of post-issue equity; Jio houses Reliance Infocomm (~500 million users, ~60% of India's data traffic); Reliance owns >66%, Meta ~10%, Google 7.7%; Jefferies has valued the business at ~$180 billion",
            "The Hindu BusinessLine — 'Reliance Jio Board approves DRHP for IPO before SEBI on June 19' (June 19, 2026): board approved the Draft Red Herring Prospectus, filed with SEBI/BSE/NSE; fresh issue of 27,00,00,000 equity shares of ₹10 face value via book building; brokerages estimate ~$180 billion value, one of the largest potential offerings in Indian corporate history",
            "The Wall Street Journal — 'Reliance's Jio Platforms to Seek India Listing' (June 19, 2026): board approved draft IPO prospectus to be submitted to SEBI; up to 270 million new shares; Sensex down nearly 10% in 2026; subdued listing activity amid weaker sentiment; NSE also filed for its IPO the same week",
            "Outlook Business / exchange4media (Reliance AGM 2026 coverage, June 19, 2026): Ambani called the Jio IPO the 'most important value creation milestone this year'; Akash, Isha and Anant Ambani leading the process; five strategic priorities outlined spanning 5G, broadband, AI and international technology platforms"
        ]),
        "diaspora_angle": "Jio is the carrier that connects nearly half a billion Indians — the network NRIs use to call home, stream cricket and run UPI payments — so its record IPO is both a chance for overseas Indians to invest in the backbone of their own ties to India and a marquee test of whether Indian tech can list at global scale.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: India's IT index hits a three-year low ──────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Nifty IT three-year low after Accenture warning")
    print("="*60)

    slug = "india-nifty-it-three-year-low-accenture-warning-infosys-tcs-wipro-discretionary-spending-20260621"
    headline = "One Warning From Accenture Knocked India's IT Stocks to a Three-Year Low. The Diaspora's Bellwether Sector Is Flashing Red."
    subheadline = "When the world's largest consulting firm flagged cautious client spending and a $400 million Middle East hit, India's tech index tumbled to levels last seen in 2023 — dragging Infosys, TCS and Wipro and shaking the industry that employs and exports the most diaspora talent."

    body = """India's IT services industry has long been the diaspora's economic mirror — the sector that sends engineers to New Jersey and London, that anchors the H-1B debate, and whose fortunes track the careers of millions of overseas Indians. This week it flashed a warning. The Nifty IT index fell about 3.7% to a three-year low after Accenture, the world's largest consulting and technology services firm, told investors that clients remain deeply cautious with their budgets and that violence in the Middle East would cost it some $400 million. Indian IT majors, which fish in the same global pipeline of discretionary technology projects, were dragged down with it.

The mechanism is one investors know well by now. "Accenture has effectively confirmed that clients remain highly cautious with their wallets," said Shashwat Singh, a fundamental analyst at Bajaj Broking. "Because Indian IT firms rely heavily on the same global pipeline for discretionary tech projects, Accenture's forecast is a warning for the entire sector." Infosys and Wipro shares slid in US trading on the back of the outlook before the selling carried into Mumbai, where the IT sub-index sank to its lowest level in three years even as the broader market had been rallying on cheaper oil.

The damage was concentrated, not broad. On June 19 the Sensex shed more than 800 points intraday and the Nifty 50 slipped below 24,000, but it was technology that did the heavy lifting on the downside — the IT index fell while sectors such as pharma and healthcare held up. That divergence matters: the benchmarks had just posted five straight sessions of gains, rising roughly 4-5%, powered by easing oil prices after the interim Iran-US peace deal. The IT slump took the wheels off that rally rather than reflecting a market-wide rout.

For the diaspora, the read-through is personal as much as financial. The big Indian IT firms — Tata Consultancy Services, Infosys, Wipro, HCLTech and their peers — are the largest formal channel through which Indian technical talent reaches the United States, the United Kingdom, Canada and the Gulf. When clients in those markets freeze discretionary spending, the consequences ripple outward into slower hiring, thinner onsite deployments, tighter bonus pools and more cautious visa sponsorship — the very levers that shape whether a young engineer in Pune or Hyderabad gets posted to a client site in Dallas or Manchester. A three-year low in the index is, in part, a barometer of that pipeline narrowing.

There is a sharper geopolitical thread, too. Accenture's explicit $400 million Middle East warning is a reminder that the Gulf conflict is not only an oil-price story for India. The region is a major market for IT services and a heavy employer of Indian tech and engineering workers, and disruption there hits revenue directly. For an industry already wrestling with the slow, uneven adoption of generative AI by clients — which has made many enterprises pause large transformation projects while they figure out what to automate — a fresh source of uncertainty is unwelcome. The caution Accenture described is structural, not a one-quarter blip.

The macro backdrop offers cold comfort. Even as the rupee logged its best week in 11 on bond inflows and softer oil, and the Reserve Bank of India's measures helped steady the currency near 94.3 per dollar, the equity market's risk appetite stayed fragile. Foreign investors sold Indian equities worth over ₹1,000 crore in a single session, and record foreign outflows of around $30 billion in 2026 so far have left sentiment brittle. IT, with its large foreign-institutional ownership and dollar-revenue exposure, tends to feel those swings first.

What the diaspora's investors and would-be migrants should watch from here is not the index level but the guidance. Accenture's commentary is a leading indicator; the real test comes when TCS, Infosys and Wipro report their own quarterly numbers and, more importantly, their outlook for client spending and hiring in the coming year. If the majors echo Accenture's caution, the three-year low could mark a reset in expectations for an industry that has carried both India's services exports and a generation of diaspora careers. If they signal that AI-led deals are finally converting into revenue, the sell-off may prove an overreaction. For now, the bellwether is blinking, and overseas Indians whose livelihoods are tied to Indian IT have good reason to read the signal closely."""

    img_url = None
    img_caption = ""
    img_attribution = ""

    for q in ["Infosys campus Bangalore", "Tata Consultancy Services building", "Bangalore IT park India", "Wipro headquarters"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            img_caption = "An Indian IT services campus; the sector's stocks fell to a three-year low after Accenture's cautious outlook"
            img_attribution = "Wikimedia Commons"
            break

    if not img_url:
        px = fetch_pexels_image("software developers office India")
        if px:
            img_url = px
            img_caption = "India's IT services sector, whose stocks slid to a three-year low"
            img_attribution = "Pexels"

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
            "Reuters — 'Indian shares snap 5-session rally on IT drag; log weekly gains on oil slide' (June 19, 2026): Nifty IT index dropped 3.7% to a three-year low after Accenture's weak revenue forecast; Indian IT firms rely on the same global discretionary-tech pipeline; Nifty 50 fell 0.64% to 24,013.1, Sensex shed 0.78% to 76,802.90 after five sessions of 4.3-4.8% gains; quote from Shashwat Singh, Bajaj Broking",
            "The Hindu BusinessLine — 'Stock Market Live, June 19: Sensex sheds over 800 pts, Nifty slips below 24,000 as IT stocks plunge over 5%' (June 19, 2026): Accenture's weak revenue forecast and warning of a $400 million Middle East impact dragged Infosys and Wipro lower in US trading; rupee near 94.36; Brent rebounded toward $80 on renewed geopolitical concerns",
            "Reuters — 'Rupee records strongest week in 11 as bond inflows, softer oil prices lend support' (June 19, 2026): rupee best week since early April, ended near 94.32 per dollar on debt inflows and RBI measures; context on foreign outflows and fragile risk appetite",
            "Reuters market coverage (June 2026): record ~$30 billion foreign equity outflows in 2026 to date; foreign investors sold Indian equities worth over ₹1,000 crore in a single session; IT sub-index's high foreign-institutional ownership and dollar-revenue exposure"
        ]),
        "diaspora_angle": "India's IT majors are the largest formal channel sending Indian tech talent to the US, UK, Canada and the Gulf, so when the sector's stocks hit a three-year low on warnings of frozen client budgets, it signals slower hiring, fewer onsite postings and tighter visa sponsorship — the levers that directly shape diaspora careers.",
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
