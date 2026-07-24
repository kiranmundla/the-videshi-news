#!/usr/bin/env python3
"""
Videshi News Writer — June 23, 2026 (04:30 UTC run)
2 NEW articles (both fresh, distinct from the 02:45 run which covered Iran
sanctions/oil and the foreign-investor return):
  1. SpaceX shares post their worst day since the record IPO, shedding $400.8bn
     in a single session — the 2nd-largest one-day market-cap wipeout in US
     history — slipping below their IPO-day close. (tech / markets — NRI
     investor angle via Nasdaq-100/index funds and Musk)
  2. Bihar police bust an interstate 'solver gang' during the NEET-UG re-exam,
     arresting 30 — including nine MBBS students hired as proxies and 18
     biometric-verification staff — after the original May test was scrapped
     over a paper leak. (education integrity / diaspora-trust angle)
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


# ─── Article 1: SpaceX worst day since IPO ─────────────────────────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: SpaceX worst day since IPO, sheds $400bn")
    print("="*60)

    slug = "spacex-worst-day-since-ipo-sheds-400-billion-falls-below-debut-close-musk-nasdaq-india-20260623"
    headline = "SpaceX Just Had the Second-Biggest One-Day Wipeout in US Market History. A Lot of Indian Portfolios Felt It."
    subheadline = "The most hyped IPO ever erased $400.8 billion in a single session on Monday, sliding below its debut-day close — and because the stock auto-joins the Nasdaq-100, the pain reaches index funds and pensions far beyond Elon Musk's orbit, including the diaspora's."

    body = """Less than two weeks after the largest stock-market debut in history, Elon Musk's SpaceX has gone from a market darling to a cautionary tale. The company's shares closed down 16.4% on Monday at $154.60 \u2014 their worst single day since going public on June 12 \u2014 erasing $400.8 billion in market value. That is the largest one-day loss SpaceX has ever recorded and, according to Dow Jones Market Data, the second-largest single-day market-capitalisation wipeout for any US company, ever.

The slide carried the stock below the $160.95 it closed at on its first day of trading, which means anyone who bought in after the debut is now underwater, at least on paper. SpaceX ended Monday with a $2.04 trillion valuation, slipping from the sixth-largest company in the world to the seventh, just behind Taiwan Semiconductor Manufacturing. It was the third straight down day, and the stock now sits 23.4% below the record closing high of $201.80 it touched on June 16 \u2014 a giddy peak, hit only days earlier, that had briefly made Musk the world's first trillionaire.

## How the Hype Unwound

The IPO was a spectacle. SpaceX priced at $135 a share on June 11, raising about $85.7 billion in the biggest offering on record, then jumped roughly 19% in its Nasdaq debut and kept climbing past $200, at one point valuing the rocket-and-satellite company near $3 trillion \u2014 above Amazon and Microsoft. Retail investors piled in, drawn by the Musk mystique and the Starlink, rocketry and artificial-intelligence story.

Then the math reasserted itself. SpaceX disclosed a $4.9 billion net loss on $18.7 billion in revenue last year, and a first-quarter net loss of $4.3 billion, as capital spending \u2014 especially on AI, where Musk merged his xAI venture into SpaceX in February \u2014 ballooned. On Monday the company confirmed plans to sell senior unsecured notes to raise cash and help repay debt, including a $20 billion bridge loan originally taken on to pay off xAI's borrowings, even though it is sitting on $100.8 billion in cash. A thin float made the swings violent: only about 5% of the company actually trades, with the rest locked up, so relatively small flows move the price hard in both directions.

## Why a Rocket Stock Lands in Indian Portfolios

It is tempting to file this under "Musk being Musk" and move on. But the diaspora has a quieter, structural stake in it. Under Nasdaq's fast-entry rule, SpaceX qualifies to join the Nasdaq-100 after just fifteen days of trading, which triggers automatic, "forced" buying from the index funds and exchange-traded funds that track the benchmark. Those funds sit inside an enormous share of the world's retirement and brokerage accounts \u2014 including the 401(k)s, IRAs and college-savings plans that millions of Indian-Americans, and NRIs invested in US markets globally, hold without ever picking a single stock.

That is the double edge of index investing: you get exposure to a company's rise whether or not you believe in it, and you wear its fall the same way. A name this large, this volatile and this freshly added can swing a chunk of the Nasdaq-100 on its own, which is precisely why a bad day for one rocket company shows up in a diaspora family's monthly statement. For the many Indian-origin engineers and professionals across Silicon Valley and beyond whose compensation and savings are heavily tied to tech, the concentration risk is sharper still.

## What's Next

The real test, analysts say, is still ahead. SpaceX used a staggered lockup rather than a single expiry, and the first window \u2014 letting eligible holders sell up to 20% of their locked shares, with a further tranche unlocked if the stock has traded at least about 30% above the $135 offer price \u2014 opens within days of its first earnings report, expected in late July or early August. That is when a wave of new supply could hit a stock whose float has so far been kept artificially thin. The full 180-day lockup does not lift until around December, and Musk's own stake stays restricted until next June.

Even after Monday's bruising, SpaceX remains about 14.5% above its IPO price, so this is a deflation of euphoria, not yet a collapse of the business. For diaspora investors, the lesson is the same one every blockbuster listing eventually teaches: the most exciting stock in the market and the steadiest place for your savings are rarely the same thing \u2014 and when they briefly overlap, the gravity always returns."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url, ctitle = pick_commons([
        "SpaceX Falcon 9 launch",
        "SpaceX Starship launch",
        "Falcon Heavy launch Kennedy Space Center",
        "SpaceX rocket launch"
    ])
    img_caption = "A SpaceX rocket launch; the company's shares posted their worst day since its record June 12 IPO, shedding $400.8 billion"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("rocket launch space")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A rocket launch; SpaceX shares fell 16.4% on Monday, the second-largest one-day market-cap loss in US history"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "markets",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "MarketWatch \u2014 SpaceX posts worst day since public debut, shedding $400 billion in market value (June 22, 2026): SpaceX shares closed down 16.4% at $154.60 on Monday, the largest one-day percentage decline since the June 12 IPO; the drop erased $400.8 billion, the largest one-day loss on record for SpaceX and the second-largest one-day market-cap loss for any US company per Dow Jones Market Data; the company ended with a $2.04 trillion valuation, falling from sixth- to seventh-largest globally behind Taiwan Semiconductor; the stock is 23.4% below its record close of $201.80 set June 16 and 31.5% below its record intraday high of $225.64; it remains 14.5% above its $135 IPO price",
            "MarketWatch \u2014 SpaceX sheds $400 billion in value as stock slides below its IPO-day closing price (June 22, 2026): the stock finished at $154.60, below the $160.95 close on June 12, meaning anyone who bought after the first day has lost money on paper; the company confirmed plans to offer senior unsecured notes to raise cash and help pay off existing debt, including a $20 billion bridge loan originally taken to pay off xAI debt, despite $100.8 billion in cash and equivalents, most from the more than $85 billion raised in the IPO",
            "Morningstar \u2014 SpaceX's IPO Filing: Big Spending, Big Losses: SpaceX disclosed a net loss of $4.9 billion on $18.7 billion in revenue last year; in Q1 2026 it posted a $4.3 billion net loss on $4.7 billion in revenue; capital expenditures hit $10.1 billion in the quarter, $7.72 billion of it AI; the AI segment lost $2.5 billion in Q1 and $6.4 billion in 2025; the IPO is the biggest ever; under Nasdaq's fast-entry rule the stock joins the Nasdaq-100 after fifteen days of trading, driving forced buying from ETFs and index funds",
            "The Motley Fool \u2014 SpaceX Stock's Biggest Test Isn't Its Post-IPO Drop. It's Coming in Late July: the IPO priced at $135 on June 11 and floated only about 5% of the company; SpaceX used a staggered lockup whose first window opens within days of its first earnings report, allowing eligible holders to sell up to 20% of locked shares, with an additional tranche if the stock has traded at least 30% above the $135 offer (about $175.50); the full 180-day lockup lifts around December and Musk's stake stays restricted until next June; xAI merged into SpaceX in February"
        ]),
        "diaspora_angle": "SpaceX auto-joins the Nasdaq-100 under Nasdaq's fast-entry rule, so its record one-day plunge flows straight into the index funds, ETFs and US retirement accounts that millions of Indian-Americans and globally-invested NRIs hold \u2014 making a single volatile rocket stock a real line item in diaspora savings.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: NEET-UG re-exam solver gang busted in Bihar ────────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: NEET-UG re-exam solver gang busted in Bihar")
    print("="*60)

    slug = "neet-ug-2026-re-exam-solver-gang-busted-bihar-30-arrested-mbbs-proxies-biometric-staff-20260623"
    headline = "India Re-Ran Its Biggest Medical Exam to Restore Trust. Police Arrested 30 People for Rigging It Anyway."
    subheadline = "The NEET-UG was held again on Sunday after the original May test was scrapped over a paper leak. By Monday, Bihar police had busted an interstate 'solver gang' \u2014 nine MBBS students hired as proxies, 18 biometric-verification staff, and deals worth up to \u20b912 lakh a seat."

    body = """India re-ran its single most consequential examination on Sunday to rescue its credibility \u2014 and within a day, police had arrested 30 people for trying to rig it. The National Eligibility cum Entrance Test for undergraduates (NEET-UG), the gateway to every MBBS seat in the country, had been held again across the state of Bihar under heavy security after the original May test was cancelled amid widespread allegations of a question-paper leak. The do-over was supposed to be the clean slate. Instead it exposed a fraud network operating in plain sight.

In Lakhisarai district, a joint operation by police and district officials uncovered what investigators are calling an interstate "solver gang": proxy candidates sitting the exam in place of registered aspirants, allegedly waved through by the very people meant to stop them. Of the 30 arrested, nine were impersonators \u2014 all of them current medical students \u2014 and 18 were staff of the outsourced biometric-verification firm hired to confirm candidates' identities. The remaining arrests were facilitators and middlemen. Three separate FIRs were registered across multiple centres, and the alleged mastermind, police say, is a student at Pawapuri Medical College in Rajgir.

## How the Racket Worked

The scheme turned the exam's own security system against it. According to the Lakhisarai sub-divisional police officer, the gang negotiated deals ranging from \u20b910 lakh to \u20b912 lakh (roughly $12,000\u2013$14,000) per candidate, collecting an advance of \u20b91\u20132 lakh up front and the balance only after results and admission. The solvers were drawn from medical colleges across the country \u2014 reports name AIIMS Rae Bareli, Banaras Hindu University, Patna Medical College, ANMMCH Gaya and a Delhi medical college \u2014 high-scoring students paid to write the test under another person's name.

The crucial weak link was biometrics. Fingerprint and identity checks at the centre door were supposed to make impersonation impossible. Investigators allege the verification staff were "in cahoots," compromising the process to let imposters through. The first breakthrough came at Hasanpur High School, where a centre superintendent acting on a tip-off alerted the magistrate and a suspicious candidate was detained during document verification. The thread unravelled from there. The National Testing Agency, which conducts NEET, had days earlier dismissed a viral video claiming a fresh paper leak and insisted the re-exam ran successfully under tight security.

## Why the Diaspora Watches This So Closely

For the Indian diaspora, NEET is not an abstraction \u2014 it is a recurring family drama. A large share of NRI households still steer at least one child toward medicine, and the children of overseas Indians who hold Indian citizenship compete for the same seats through the same single exam. Many diaspora families specifically choose to sit NEET and study medicine in India precisely because it is meritocratic and far cheaper than a Western medical degree. Every credible cheating scandal chips away at the one thing that makes that bet worth taking: the belief that the test is fair.

It also lands in a raw spot. The 2024 NEET-UG was engulfed by a paper-leak crisis that reached the Supreme Court and dominated national headlines, and the diaspora's WhatsApp groups and parent forums followed every twist. A repeat in 2026 \u2014 on the very re-test meant to prove the system had been fixed \u2014 confirms the fear that the rot is structural, not a one-off. Families weighing whether to send a child "back home" for an affordable medical education now have to price in the possibility that the playing field is quietly tilted.

## What's Next

The investigation is widening. Senior officers, including the district magistrate and superintendent of police, are personally monitoring the probe, and raids are underway at locations linked to the network; authorities expect more arrests as they trace how many proxy candidates actually sat the exam and how deep the biometric collusion ran. The bigger question is institutional: if outsourced verification staff can be bought, the technology that was meant to guarantee integrity becomes just another point of sale.

For the roughly two million-plus aspirants who sit NEET honestly each year \u2014 and for the diaspora parents cheering them on from abroad \u2014 Sunday's re-exam was meant to close a painful chapter. The 30 arrests reopened it. Until the people who run the test can prove that the person in the chair is the person on the admit card, every Indian medical seat will carry an asterisk the diaspora can no longer ignore."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url, ctitle = pick_commons([
        "examination hall students India",
        "students writing exam India",
        "school examination India",
        "Bihar police station India"
    ])
    img_caption = "Students at an examination centre in India; Bihar police arrested 30 over a solver-gang racket during the NEET-UG re-exam"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("students writing examination")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Students sitting an examination; 30 were arrested in Bihar over alleged impersonation during the NEET-UG re-exam"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "education",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Sambad English / IANS \u2014 NEET-UG exam scam: Solver gang busted in Bihar, 30 arrested for impersonation (June 22, 2026): Bihar police cracked down on a racket of impersonators during the NEET-UG 2026 re-exam after cheating and alleged manipulation of biometric verification surfaced at multiple centres; 30 people arrested including imposters who appeared in place of genuine candidates; the alleged mastermind is a student of Pawapuri Medical College in Rajgir; deals ranged from Rs 10 lakh to Rs 12 lakh per candidate with an advance of Rs 1\u20132 lakh; all nine arrested 'solvers' are medical students; Lakhisarai SDPO Shivam Kumar quoted",
            "Careers360 \u2014 NEET UG 2026 re-exam: Bihar Police bust solver gang, arrest MBBS students (June 22, 2026): Bihar police arrested five medical and nursing students plus others from AIIMS Rae Bareli, BHU, PMCH, ANMMCH Gaya and a Delhi medical college, and 14 employees of a biometric verification firm for allegedly running a solver gang; the scam was busted when a suspicious individual posing as a biometric company employee was caught at a centre; the NTA had refuted a viral re-NEET paper-leak video and said the test ran under tight security",
            "OrangeNews9 / IANS \u2014 28 people held in Bihar for attempting irregularities in NEET-UG re-exam (June 22, 2026): the re-examination was conducted across Bihar on Sunday under tight security after the original undergraduate medical entrance test in early May was cancelled amid widespread allegations of a question-paper leak; ADG (Law and Order) Sudhanshu Kumar said 18 biometric-verification staff were arrested for colluding with dummy candidates and middlemen; nine impersonators and 21 others arrested; DM Shailendra Kumar and SP Prerna Kumar monitoring",
            "Patna Press \u2014 NEET Re-Exam Fraud Busted In Bihar: 30 Arrested As Interstate Solver Gang Allegedly Used MBBS Students As Proxies (June 22, 2026): arrests made at multiple centres in Lakhisarai including Hasanpur High School, KRK High School, Kendriya Vidyalaya and Kiul; three FIRs registered (244/26, 245/26, 64/26); proxy candidates, biometric operators and intermediaries worked together to bypass security; the first breakthrough came at Hasanpur High School after Centre Superintendent Mrityunjay Kumar alerted the magistrate"
        ]),
        "diaspora_angle": "Many NRI families still steer children toward an affordable, merit-based MBBS in India through NEET, and children of overseas Indians with Indian citizenship sit the very same exam \u2014 so a solver-gang scandal on the re-test meant to restore trust strikes directly at the fairness that makes a medical education back home worth the bet.",
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
