#!/usr/bin/env python3
"""
Videshi News Writer — June 25, 2026 (18:30 UTC / 11:30 PDT run)
2 NEW articles, dedup-checked against last ~40 news articles:
  1. US premium visa appointment pilot — State Dept July 1-Dec 31 2026 trial
     lets B-1/B-2 applicants pay USD 750 (on top of USD 185 fee) for an
     interview within 10 business days at select missions. Big for Indian
     travellers facing long backlogs. NOT covered.
  2. NSE files DRHP with SEBI for ~Rs 30,000 crore IPO ($3.3B), pure
     offer-for-sale of 6% (148.9M shares), ~$55-57B valuation, set to be
     India's largest-ever public issue. Diaspora investment angle. Jio IPO
     covered separately; NSE NOT covered.
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


# \u2500\u2500\u2500 Article 1: US premium visa appointment pilot \u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: US premium visa appointment pilot")
    print("="*60)

    slug = "us-premium-visa-appointment-pilot-750-dollars-faster-interview-b1-b2-indian-travellers-july-december-2026-20260625"
    headline = "America Will Soon Let You Pay $750 to Skip the Visa Line. India's Travellers Are the Obvious Customer."
    subheadline = "A six-month State Department pilot starting July 1 lets visitor-visa applicants buy an interview within 10 business days \u2014 a paid fast lane in a system where Indians have long waited months for a slot."

    body = """For anyone who has tried to book a US visitor-visa interview from India, the hardest part has rarely been the interview itself. It is getting to the window at all. Wait times for a B-1/B-2 appointment in Indian cities have stretched into months at various points in recent years, turning a summer family visit or a conference trip into an exercise in calendar archaeology. Now Washington is testing a way to jump the queue \u2014 for a price.

The US Department of State has announced a temporary pilot programme that, from July 1 to December 31, 2026, will let eligible applicants for B-1 and B-2 visas \u2014 the categories used for business and tourism \u2014 pay an extra fee in exchange for a guaranteed interview within 10 business days at select embassies and consulates. The catch is the cost, and a long list of fine print.

## The Price of Skipping the Line

The expedited service will cost USD 750, on top of the standard non-immigrant visa application fee of USD 185. In practical terms, an applicant choosing the premium route pays USD 935 before an interview has even taken place \u2014 roughly four times the normal fee. The service is optional, and it will be offered only in limited numbers: participating missions will release a restricted pool of premium slots, and the State Department says a full list of eligible posts will be published before the launch.

Crucially, the money buys speed, not a visa. Every existing eligibility rule for visitor visas stays in place. Applicants who pay are assessed against exactly the same criteria as everyone else, and the fee does nothing to accelerate the security checks, administrative processing, or final adjudication that follow the interview. In the State Department's framing, the pilot is a market test \u2014 a way to gauge whether enough travellers will pay a premium for a faster slot to justify making the service permanent.

## Why India Is the Test Case That Matters

Officially, Washington has not confirmed whether its missions in India will take part. But it is hard to imagine a pilot aimed at clearing appointment backlogs that does not eventually run through the country that generates some of the world's heaviest demand for US visas. India sits alongside the United Arab Emirates, Canada, Nigeria, and Ghana on the list of markets where appointment queues have been a chronic complaint, and few of those rival India for sheer volume.

That volume is precisely what makes the diaspora the natural customer. The people most likely to reach for a USD 750 fast pass are not first-time tourists but the frequent fliers of the India-US corridor: parents flying out to meet a newborn grandchild, founders racing to a closing or a demo day, wedding guests with non-negotiable dates, and the professionals who shuttle between Bengaluru and the Bay Area and simply cannot afford a three-month wait for a slot.

## A Two-Tier System, Quietly Arriving

For the broader diaspora, the pilot lands as the latest signal of a US immigration and travel system that increasingly sorts people by willingness to pay. Premium processing has long existed on the employment side; now the logic is creeping into visitor visas. Supporters will call it a pragmatic relief valve for a system buckling under demand. Critics will note that it formalises a two-tier queue, in which those with USD 750 to spare move to the front while everyone else keeps waiting under the old emergency-appointment system, which generally required documented proof of urgency.

There is also a hard-nosed question of value. Paying nearly four times the standard fee for an interview that still carries the same odds of refusal will strike many as steep. For a family of four, the premium alone adds USD 3,000 to the bill before a single ticket is booked. Whether that math works depends entirely on how much a guaranteed early date is worth against a particular trip.

## What It Means for the Diaspora

For India's vast network of non-resident families, the practical takeaways are concrete. First, watch for the list of participating posts before July 1 \u2014 the whole calculation changes depending on whether Mumbai, New Delhi, Chennai, Hyderabad or Kolkata are included. Second, treat the fee as a tool for genuinely time-sensitive travel, not a default; the standard appointment system and emergency requests remain available at no extra cost. Third, remember what the money does and does not buy: a faster seat at the window, and nothing more.

For a community whose calendar is stitched together across continents \u2014 a graduation here, a cremation there, a board meeting in between \u2014 the appeal of a guaranteed slot is obvious. The pilot is a small, six-month experiment. But if Indians take to it, as the State Department is clearly betting they might, the paid fast lane could become a permanent fixture of how the diaspora travels home and back again."""

    img_url, ititle = pick_commons([
        "US Embassy New Delhi",
        "United States Embassy India",
        "U.S. Consulate Mumbai",
        "American consulate India"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "The U.S. Embassy in New Delhi; a new State Department pilot offers Indian travellers faster visa interviews for a fee"

    if not img_url:
        px = fetch_pexels_image("passport airport travel queue")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A new US pilot lets visitor-visa applicants pay for a faster interview appointment"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Outlook Traveller (outlooktraveller.com, June 23, 2026) \u2014 'US To Offer Faster Visa Appointments Within 10 Days\u2014For An Additional Fee': the US Department of State announced a temporary pilot programme running July 1 to December 31, 2026, allowing eligible B-1/B-2 applicants to pay an extra USD 750 (on top of the USD 185 application fee, for USD 935 total) to secure an interview within 10 business days at select embassies and consulates; the service is optional and limited in quantity, guarantees a faster appointment but not visa approval, does not accelerate security checks or administrative processing, and a list of participating missions is to be published before launch; India, the UAE, Canada, Nigeria and Ghana are cited as high-demand markets, though US participation of missions in India is not yet confirmed.",
            "US Department of State (state.gov / travel.state.gov, 2026) \u2014 official framework for the temporary expedited visa-appointment pilot for non-immigrant B-1/B-2 visitor visas, under which existing eligibility criteria and adjudication standards remain unchanged and the premium fee buys only an earlier interview date.",
            "Background on US visa appointment backlogs in India (2026) \u2014 historically high demand for B-1/B-2 visitor-visa appointments at US consular missions in India, where wait times for interview slots have at times stretched to months, prompting reliance on emergency and priority appointment requests."
        ]),
        "diaspora_angle": "Indians generate some of the world's heaviest demand for US visitor visas and have long faced months-long appointment backlogs, so a paid fast lane offering an interview within 10 business days \u2014 for USD 750 on top of the USD 185 fee \u2014 lands squarely on the diaspora's frequent fliers, from parents visiting grandchildren to founders and professionals shuttling across the India-US corridor.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: NSE IPO DRHP filing \u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: NSE files for India's largest-ever IPO")
    print("="*60)

    slug = "nse-national-stock-exchange-files-drhp-sebi-largest-ipo-india-30000-crore-offer-for-sale-2026-20260625"
    headline = "After a Decade of Waiting, India's Biggest Stock Exchange Is Finally Going Public. The Owner of the Market Is About to Join It."
    subheadline = "The National Stock Exchange has filed for a roughly Rs 30,000-crore offer-for-sale \u2014 set to be India's largest-ever IPO \u2014 at a valuation near $55 billion, ending a listing saga that has dragged since 2016."

    body = """For nearly a decade, the National Stock Exchange has been the great absentee from the market it runs. It is the venue where India's stocks are bought and sold, the world's most active derivatives exchange by volume, and one of the country's most widely held companies \u2014 yet its own shares have never traded on a public exchange. That is about to change.

NSE has filed its Draft Red Herring Prospectus with the Securities and Exchange Board of India (SEBI), setting in motion an initial public offering that industry estimates put at around Rs 30,000 crore. If it lands as expected, it would be the largest public issue in India's history, edging past every record-breaker before it and arriving alongside the other mega-listing of the year, Mukesh Ambani's Reliance Jio.

## A Pure Cash-Out for Long-Patient Owners

The structure is unusual for a deal this size. The NSE IPO will be a pure offer for sale: the exchange itself raises no fresh capital. Instead, existing shareholders will sell roughly 148.9 million shares \u2014 about 6% of the company \u2014 cashing out stakes many have held for years. Reuters estimates the sale will hand top investors a windfall of around USD 2.6 billion.

The seller list reads like a who's who of Indian and global institutional finance. Life Insurance Corporation of India is the single largest shareholder with a 10.72% stake; State Bank of India and its capital-markets arm together hold around 7.5%. Among foreign backers, Singapore's Temasek (through its Aranda Investments arm) and the Canada Pension Plan Investment Board are set to pare holdings. For all of them, the listing is the long-awaited exit from a stock that has traded actively in the unlisted "grey" market but never had a public ticker.

## The Valuation, and the Numbers Behind It

At the prices NSE shares have fetched in the unlisted market \u2014 close to Rs 2,000 each \u2014 the exchange is valued at roughly USD 55 to 57 billion. That would place it among India's ten largest companies by market capitalisation and make it the world's fifth most valuable exchange operator, comparable to the London Stock Exchange Group. Bankers have suggested the IPO may price at a modest 5% to 10% discount to grey-market levels, around Rs 1,900 a share, to leave room for new investors without short-changing the old.

The business underneath the valuation is formidable. For the year ended March 2026, NSE reported total income of Rs 18,713 crore and net profit of Rs 10,302 crore \u2014 a margin most listed companies can only envy, built largely on the explosive growth of India's derivatives trading. Founded in 1992, the exchange now counts more than 200,000 of its own shareholders and sits at the centre of a market with roughly 257 million investor accounts and 130 million unique investors, a retail base far larger than that of Western peers like Nasdaq or the New York Stock Exchange.

## Why the Wait Was So Long

The listing's near-decade delay is its own story. NSE first filed IPO papers in 2016, only for the process to stall amid the co-location controversy \u2014 a long-running case over allegations that some brokers got unfair, preferential access to the exchange's trading systems. Regulatory scrutiny kept the listing in limbo even as rival BSE went public in 2017. SEBI's no-objection certificate, granted earlier this year, finally cleared the path, and the exchange's board approved the offer in February. The government's recent move to halve the minimum public float for the very largest companies \u2014 letting those valued above Rs 5 trillion sell as little as 2.5% \u2014 also smoothed the way.

## Why It Matters for the Diaspora

For non-resident Indians, the NSE listing is more than a domestic financial milestone \u2014 it is a chance to own a slice of the plumbing of the very market many of them already invest in. NRIs route remittances and savings into Indian equities and index funds in growing volumes, and the exchange that hosts those trades has, until now, been off-limits as an investment. Eligible NRIs can typically participate in Indian IPOs through their NRE/NRO accounts under the portfolio investment route, subject to the usual rules.

There is a bigger signal here too. Two of India's largest-ever IPOs \u2014 NSE and Jio \u2014 lining up in a single year points to the deepening and maturing of India's capital markets, the same markets that are increasingly central to how the diaspora keeps financial roots at home. For an investor in New Jersey or Dubai watching India's growth story from afar, the company that runs the marketplace finally putting itself up for sale is about as direct a way to buy into that story as exists."""

    img_url, ititle = pick_commons([
        "National Stock Exchange India",
        "National Stock Exchange Mumbai",
        "NSE building Mumbai",
        "Bombay Stock Exchange building"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "The National Stock Exchange building in Mumbai; NSE has filed for what would be India's largest-ever IPO"

    if not img_url:
        px = fetch_pexels_image("stock exchange trading floor")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "NSE has filed draft papers for what would be India's largest-ever public issue"

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
            "Reuters (reuters.com, June 2026) \u2014 'India's largest bourse NSE files for IPO after years of regulatory delays': NSE filed draft papers for an IPO, one of two mega IPOs this year alongside Reliance Jio; the exchange has been trying to list since 2016 when its first filing stalled over a regulatory enquiry; estimated valuation around USD 55 billion based on unlisted-market trading, placing it among India's 10 largest companies and comparable to the London Stock Exchange Group ($58B); the offer is a pure OFS of 148.9 million shares (6%); LIC, SBI, Bank of Baroda, state insurers, Temasek and CPPIB among sellers; NSE has ~200,909 shareholders and the market has ~257 million investor accounts and 130 million unique investors; government halved the minimum float for companies valued above Rs 5 trillion to 2.5%.",
            "Reuters (reuters.com, June 2026) \u2014 'India's long-delayed NSE IPO sets up $2.6 billion windfall for top investors': the listing will be a pure offer-for-sale of about 6% of equity with no fresh capital raised; NSE shares trade near Rs 2,000 in the unlisted market implying a ~$57 billion valuation; bankers indicated a possible 5-10% discount to grey-market levels, around Rs 1,900 per share, putting the IPO at roughly $3.3 billion, comparable to Reliance Jio's ~$4 billion offering.",
            "The Indian Eye (theindianeye.com, June 2026) \u2014 'NSE Files for IPO worth Rs 30,000-Crore, set to become India's Largest Public Issue': NSE filed its DRHP with SEBI for a ~Rs 30,000-crore IPO expected to be India's largest ever; pure OFS of ~148.9 million shares (~6%); for FY ended March 2026 NSE reported total income of Rs 18,713 crore and net profit of Rs 10,302 crore; listing delayed nearly a decade by regulatory hurdles including the co-location controversy.",
            "The Hindu BusinessLine (thehindubusinessline.com, June 2026) \u2014 coverage of the NSE DRHP filing: board approved the IPO on February 6 after SEBI's NOC; entirely an offer for sale; LIC is the single largest shareholder at 10.72%, SBI and SBI Capital Markets together ~7.5%, with Temasek's Aranda Investments and CPPIB among foreign holders; NSE first filed offer documents in 2016 to raise ~Rs 10,000 crore before SEBI withheld approval amid governance and co-location concerns."
        ]),
        "diaspora_angle": "NRIs increasingly route remittances and savings into Indian equities and index funds, and the NSE IPO offers a chance to own a piece of the marketplace itself \u2014 a stock that has been off-limits until now \u2014 with eligible NRIs able to apply via NRE/NRO portfolio accounts, while the back-to-back NSE and Jio mega-listings signal the deepening of the very markets the diaspora uses to keep financial roots at home.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    print("Videshi News Writer \u2014 2026-06-25 18:30 UTC run")
    id1 = write_article_1()
    id2 = write_article_2()
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Article 1 (US premium visa pilot): {'OK id=' + str(id1) if id1 else 'FAILED'}")
    print(f"Article 2 (NSE IPO DRHP): {'OK id=' + str(id2) if id2 else 'FAILED'}")
