#!/usr/bin/env python3
"""
Videshi News Writer — June 19, 2026 (10:30 UTC run)
2 NEW articles for the "news" category:
  1. Modi disburses Rs 2,400 cr under PM Viksit Bharat Rozgar Yojana (today, June 19)
  2. NSE files for landmark IPO — $2.6bn windfall, ~$57bn valuation
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


# ─── Article 1: Modi PM-VBRY Rs 2,400 cr disbursal ───────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Modi PM-VBRY Rs 2,400 cr disbursal")
    print("="*60)

    slug = "modi-pm-vbry-2400-crore-employment-incentive-disbursal-20260619"
    headline = "Modi Hands Out Rs 2,400 Crore to First-Time Workers Today. It's a Bet That India's Jobs Problem Can Be Bought Down."
    subheadline = "At Vigyan Bhawan on Friday, the Prime Minister disburses the first big tranche of the Viksit Bharat Rozgar Yojana — a Rs 99,446 crore scheme that pays young Indians to enter the formal economy and pays employers to hire them."

    body = """Prime Minister Narendra Modi steps up to a podium at Vigyan Bhawan in New Delhi on Friday evening to do something his government has staked a large part of its economic credibility on: pay people to get jobs, and pay companies to create them. The occasion is the disbursal of around Rs 2,400 crore under the Pradhan Mantri Viksit Bharat Rozgar Yojana, the flagship employment-linked incentive scheme that has quietly become one of the most ambitious labour-market experiments India has attempted.

The numbers behind the ceremony are large. The scheme carries a total outlay of Rs 99,446 crore and is designed to support the creation of more than 3.5 crore jobs over two years. Of those targeted beneficiaries, roughly 1.92 crore are expected to be first-time entrants to the workforce — the young Indians stepping off campuses and out of training programmes into a labour market that has long struggled to absorb them.

## How the Money Moves

The mechanics are straightforward by design. First-time employees registered in the formal system are eligible for an incentive of up to Rs 15,000, a direct cash cushion as they take their first salaried job. Employers, meanwhile, can claim up to Rs 3,000 per month for each additional employee they hire, a subsidy meant to tip the calculus toward expansion rather than caution.

There is a deliberate tilt toward factories. Recognising manufacturing's outsized role in soaking up labour, the scheme extends incentives to manufacturing employers for four years, against two years for firms in other sectors. It is a policy bet aligned with the broader "Make in India" and production-linked incentive push — the idea that if India is to employ its young millions, it must build things at scale.

Since its launch in August 2025, the government says the scheme has already supported the creation of around 15 lakh employment opportunities. Friday's disbursal is being framed as a milestone moment, the point at which the programme moves from rollout to visible payout.

## The Problem It Is Trying to Solve

Behind the ceremony sits India's most stubborn economic anxiety. The country adds millions of working-age people each year, and formal-sector employment has never grown fast enough to match. Too many Indians remain in informal, insecure work without social security, contracts, or a path upward. The Viksit Bharat Rozgar Yojana is, at its core, an attempt to drag both workers and employers across the line into the formal economy — where wages are recorded, benefits accrue, and the state can see and support its workforce.

Whether cash incentives can durably change hiring behaviour is the open question. Critics of employment-linked subsidies note that such schemes can end up rewarding hiring that would have happened anyway, and that the formalisation they produce can fade once the payments stop. Supporters counter that the social-security coverage and formal records created along the way have lasting value, pulling first-time workers into a system that protects them.

## Why It Matters for the Diaspora

For the Indian diaspora, a scheme about first-time factory and office workers in Delhi and Pune may feel distant. It is not. The diaspora's relationship with India runs through its economy — through the family members still job-hunting back home, through the remittances that cushion households between paychecks, and through the investment decisions of NRIs weighing whether India's growth story is real or rhetorical.

A government willing to spend Rs 99,446 crore to formalise its workforce is signalling where it thinks the next decade of growth comes from: young, employed, taxpaying Indians inside the formal economy rather than outside it. For NRIs sending money home, that promises households less dependent on remittances over time. For diaspora investors, a broadening formal workforce is the demographic engine beneath every bullish India pitch they have heard. And for the millions of families with one foot in India and one abroad, a job scheme that works means fewer relatives asking for help — the quiet, personal measure by which the diaspora actually judges whether India's economy is delivering.

The test, as always, is execution. Friday's Rs 2,400 crore is real money reaching real workers. The harder question — whether it becomes a permanent rung on India's economic ladder or a subsidy that evaporates — will take years, and many more disbursals, to answer."""

    print("  Sourcing image...")
    img_url = fetch_wikipedia_person_image("Narendra Modi")
    img_caption = "Prime Minister Narendra Modi, who disbursed Rs 2,400 crore under the PM Viksit Bharat Rozgar Yojana on June 19"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        commons = fetch_wikimedia_commons_images("Narendra Modi 2024")
        if commons:
            img_url = commons[0]["url"]

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
            "IANS \u2014 PM Modi to disburse Rs 2,400 crore under Viksit Bharat Rozgar Yojana on June 19",
            "India Education Diary \u2014 PM to disburse incentives worth around Rs 2,400 crore under PM-VBRY on 19 June",
            "Prime Minister's Office (PMO) \u2014 PM-VBRY scheme details and beneficiary figures"
        ]),
        "diaspora_angle": "India is spending Rs 99,446 crore to pull its young workforce into the formal economy \u2014 a bet that, if it works, means households less dependent on diaspora remittances and a stronger demographic case for every NRI weighing an investment back home.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: NSE IPO ──────────────────────────────────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: NSE files for landmark IPO")
    print("="*60)

    slug = "nse-ipo-draft-filing-2026-57-billion-valuation-diaspora-investors-20260619"
    headline = "After Years of Delay, India's Biggest Stock Exchange Files to Go Public. The NSE IPO Could Be Worth $57 Billion."
    subheadline = "The National Stock Exchange — the world's busiest derivatives market — has finally filed draft IPO papers, setting up a $2.6 billion windfall for its investors and a landmark listing that lands just as India throws its equity markets open to NRIs."

    body = """For more than a decade, the most-anticipated listing in Indian finance was the one that never came. The National Stock Exchange — the country's largest bourse and the world's most active derivatives market — has been talked about as an IPO candidate for so long that its absence from its own platform became something of a running joke. On Wednesday night, the joke ended. NSE filed draft papers for an initial public offering, clearing one of the last great regulatory logjams in Indian capital markets.

The scale is enormous. NSE shares trade at close to 1,900 to 2,000 rupees apiece in the unlisted market, implying a valuation of roughly $57 billion. That would make the exchange the world's fifth most valuable bourse, behind only the London Stock Exchange Group and a handful of others. At around 1,900 rupees per share, the offering itself could be worth some $3.3 billion — placing it alongside Mukesh Ambani's Reliance Jio, expected to list this year in an IPO of about $4 billion, as one of India's two largest public offerings ever.

## A Windfall, Years in the Making

The listing is structured as a pure offer-for-sale: existing shareholders will sell roughly 6 per cent of the exchange's equity, and no fresh capital will be raised. That detail matters. It means the IPO is, in effect, a long-deferred payday for the people who backed NSE and waited out the regulatory delays.

And the beneficiaries are a who's who of patient institutional capital. Investors set to reap a collective $2.6 billion windfall range from Indian state-owned lenders to Singapore's sovereign wealth fund and Canada's national pension manager — global money that bet on Indian market infrastructure years ago and is about to see it marked to a public price. NSE has more than 200,000 investors on its register today.

Pricing is not yet locked. Three sources, including merchant bankers, said the exchange may offer shares at a 5 to 10 per cent discount to private-market valuations, with a figure around 1,900 rupees under discussion — a level intended to attract new buyers "while not short-changing existing ones," as one put it. A final decision will follow investor roadshows.

## Why the Timing Is Pointed

The NSE filing does not arrive in a vacuum. It lands in the middle of a deliberate campaign by Indian regulators to widen access to the country's equity markets — and, crucially, to open them to the diaspora. The Reserve Bank of India has just raised the ceilings on how much NRIs and Overseas Citizens of India can own in Indian companies, lifting the individual limit from 5 to 10 per cent of a firm's paid-up capital and the aggregate NRI limit from 10 to 24 per cent.

Put those two developments side by side and the strategy is hard to miss. India is simultaneously listing the institution at the heart of its markets and dismantling the barriers that kept overseas Indians from buying in. The country is not just inviting foreign portfolio money; it is courting its own diaspora as a permanent class of domestic-market investors.

## Why It Matters for the Diaspora

For NRIs, the NSE IPO is more than a marquee deal to read about over morning coffee. It is a test case for the new, more open India equity regime they have just been handed the keys to. The exchange that processes the trades is itself about to become one of those trades — a chance to own a slice of the plumbing of the world's fifth-largest economy.

There is symbolism here too. The diaspora has spent years watching India's markets from the outside, often through the narrow window of mutual funds or family-managed portfolios back home. A listed NSE, arriving alongside expanded ownership limits, signals an India confident enough to put its core financial machinery on public display and to invite overseas Indians to buy a stake in it directly.

The caveats are the usual ones. Valuations near $57 billion price in a great deal of future growth, derivatives volumes can be volatile, and regulatory scrutiny of India's frothy options market is intensifying even as the exchange goes public. The NSE itself has flagged fresh risk warnings ahead of the listing. But for a diaspora that has long wanted a cleaner, more direct way to invest in the India story, the exchange's debut — whenever it finally prices — will be one of the most closely watched bells the market has rung in years."""

    print("  Sourcing image...")
    img_url = None
    img_caption = "The National Stock Exchange of India, which filed draft papers for a landmark IPO"
    img_attribution = "Wikimedia Commons"

    for q in ["National Stock Exchange India building", "Bombay Stock Exchange Mumbai", "Mumbai financial district BKC"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            if "stock exchange" in commons[0]["title"].lower():
                img_caption = "The National Stock Exchange of India, the world's busiest derivatives market, in Mumbai"
            break

    if not img_url:
        px = fetch_pexels_image("stock market trading screen finance")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A stock market trading display"

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
            "Reuters \u2014 India's long-delayed NSE IPO sets up $2.6 billion windfall for top investors",
            "Reuters \u2014 Indian rupee, bonds to get a boost from Iran peace deal, eye Fed move",
            "NRI Globe \u2014 RBI increases investment limits for NRIs and OCIs in Indian equities"
        ]),
        "diaspora_angle": "India is listing the exchange at the heart of its markets just as it raises the limits on how much NRIs can own in Indian companies \u2014 a one-two move that courts the diaspora as a permanent class of domestic-market investors.",
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
