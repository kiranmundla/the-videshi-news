#!/usr/bin/env python3
"""
Videshi News Writer — June 26, 2026 (04:30 UTC / June 25 21:30 PDT run)
2 NEW articles, dedup-checked against last ~30 news articles:
  1. RBI FCNR(B) diaspora deposit scheme — RBI absorbs hedging cost on fresh
     3-5 yr FCNR(B) deposits, banks now offering 6-7%, plus loans against
     deposits via GIFT City => equity-like returns (up to 12-15% w/ leverage)
     for overseas Indians; Nomura sees $55bn inflows, Axis up to $100bn. NRI
     finance story, NOT covered.
  2. Indian Embassy UAE pauses passport/visa/consular services June 26-30 as
     it switches outsourced provider (BLS/SGIVS -> Al Hind Tours & Travel from
     July 1). Directly affects 4.4M Indians in the UAE. NOT covered.
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


# \u2500\u2500\u2500 Article 1: RBI FCNR(B) diaspora deposit scheme \u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: RBI FCNR(B) diaspora deposit scheme")
    print("="*60)

    slug = "rbi-fcnr-b-deposit-scheme-hedging-cost-nri-banks-6-7-percent-gift-city-loans-55-billion-rupee-20260625"
    headline = "India Is Quietly Offering Its Diaspora a Rare Deal: Park Dollars Home, Earn Almost Like Stocks"
    subheadline = "The RBI is swallowing the currency-hedging cost on new FCNR(B) deposits, pushing rates to 6-7%. With loans now allowed against those deposits through GIFT City, returns could climb toward double digits \u2014 and analysts expect tens of billions of NRI dollars to follow."

    body = """For most non-resident Indians, the choice has always been a quiet compromise. Keep your savings in dollars and watch them earn next to nothing in a Western bank, or move them home for a higher rupee rate and absorb the risk that the currency slides before you bring the money back. This month, the Reserve Bank of India has tried to make that trade-off disappear \u2014 and in the process has dangled one of the most attractive deals overseas Indians have seen in over a decade.

On June 5, the central bank announced it would absorb the cost of hedging the foreign-exchange risk on fresh foreign currency non-resident, or FCNR(B), deposits of three to five years. In plain terms: a depositor parks dollars in an Indian bank, earns a dollar-denominated interest rate, and faces no rupee risk \u2014 because the RBI, not the depositor, is carrying the cost of insuring against currency swings. The bank swaps the dollars with the central bank at a concessional rate, and the hedging cost that normally ate into returns effectively drops to zero.

## Why the Rates Suddenly Look So Good

That subsidy has freed banks to raise their offers sharply. Lenders are now marketing FCNR(B) deposits at around 6% to 7%, well above the roughly 3.35% that three-year dollar deposits fetched before the scheme, and comfortably above the 4%-ish yield on equivalent U.S. Treasuries. For an NRI sitting on idle dollars, that gap is the whole point.

Then the RBI went a step further. On June 23, it clarified that Indian banks \u2014 including through their overseas branches and units in the tax-neutral hub of GIFT City in Gujarat \u2014 may extend loans to non-residents against these deposits, and issue standby letters of credit to back them. That opens the door to leverage: borrow cheaply, deposit the proceeds, and amplify the return. Macquarie analysts estimate that with such leverage, returns could approach 12%; Axis Bank's calculations suggest as much as 15% at higher leverage levels. Equity-like numbers, from what is fundamentally a fixed-income product.

## A Familiar Playbook, a Bigger Prize

India has reached for its diaspora before in moments of currency stress. The RBI ran a similar FCNR swap window during the 2013 "taper tantrum," pulling in over \u002420 billion and helping steady a sliding rupee. This time the ambitions are larger. Nomura estimates the new scheme could attract about \u002455 billion, with the bulk arriving in August and September. State Bank of India's economists peg FCNR(B) flows at \u002440-45 billion, while Axis Bank sees scope for as much as \u0024100 billion if the leverage mechanics work as banks hope.

The logic is simple. When those dollars are swapped into rupees at the RBI, they shore up a currency that has weakened roughly 15% over the past year, rebuild foreign-exchange reserves, and ease pressure on domestic lending rates. The diaspora, in effect, becomes a financial stabiliser \u2014 and gets paid handsomely for the service. The window is open until September 30.

## The Catch Worth Reading

None of this is risk-free in the fine print. The RBI's swap covers only the principal, not the interest, and the headline 6-7% rates already bake in the hedging subsidy, so bankers caution there is limited room to push them higher. Leverage cuts both ways: the double-digit returns analysts cite assume borrowing costs and swap terms hold steady over the deposit's life. And the scheme's most generous mechanics \u2014 dollar loans routed through GIFT City \u2014 are still being negotiated between banks and the regulator, with smaller lenders that lack overseas branches worried about being left out.

## Why It Matters for the Diaspora

For the roughly 35 million people of Indian origin scattered from Silicon Valley to the Gulf, this is one of the rare moments when sending money home is framed not as remittance or sentiment, but as a genuinely competitive investment. An NRI in New Jersey or Dubai weighing where to park a dollar cushion now has an Indian option that beats a U.S. savings account without the usual currency gamble.

The deposits are also tax-efficient for many overseas Indians, and the three-to-five-year lock-in suits the long horizons of families who plan to return or to fund children's education and parents' care back home. Expect the marketing to intensify through the summer: banks have every incentive to chase the August-September surge that analysts are forecasting, and NRI inboxes are already filling with pitches. The advice from advisers is the same as ever \u2014 read the lock-in terms, understand whether you are taking on leverage, and remember that a 6% headline rate from a well-capitalised Indian bank is a different animal from a 15% leveraged structure. For a diaspora that has long subsidised home with remittances out of duty, India is, for once, making the pitch on the numbers."""

    img_url, ititle = pick_commons([
        "Reserve Bank of India building Mumbai",
        "Reserve Bank of India headquarters",
        "Reserve Bank of India",
        "GIFT City Gandhinagar",
        "Indian rupee currency notes"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "The Reserve Bank of India headquarters in Mumbai, which is absorbing the hedging cost on new FCNR(B) diaspora deposits"

    if not img_url:
        px = fetch_pexels_image("indian rupee currency money")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "The RBI's new deposit scheme offers NRIs dollar rates of 6-7% with no rupee risk"

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
            "Reuters India File (reuters.com, 23 June 2026) \u2014 'Rupee gets diaspora lifeline \u2014 banks cash in': RBI announced earlier in June it would absorb the cost of hedging foreign currency deposits placed with Indian banks for three to five years, letting overseas Indians earn high domestic rates without currency risk; banks now marketing FCNR(B) deposits at ~6-7%; Nomura puts potential inflows at ~\u002455bn, Axis Bank at ~\u0024100bn; banks seeking RBI approval to offer dollar loans via overseas branches and GIFT City; with leverage returns could approach 12% (Macquarie, \u002430-50bn inflows) or 15% (Axis); India's diaspora ~37 million.",
            "The Hindu BusinessLine (thehindubusinessline.com, 23 June 2026) \u2014 'RBI permits domestic banks to extend credit against foreign currency deposits abroad': RBI notice on Tuesday allows domestic lenders to extend loans to non-residents against FX deposits including via offshore/GIFT City branches, using deposits as collateral; banks may issue standby letters of credit; RBI swap covers only principal not interest; scheme announced earlier in June to bolster dollar inflows and the rupee; Nomura estimates \u002455bn with bulk in August-September.",
            "Mint (livemint.com, 23-24 June 2026) \u2014 'RBI allows banks to give loans for FCNR deposits': on 5 June RBI said it would absorb the forex hedging cost on fresh FCNR(B) deposits, creating an opportunity for overseas Indians to earn equity-like returns from a fixed-income product; banks may raise/renew FCNR(B) deposits of 3-5 years and swap dollars with RBI at a concessional rate, hedging cost effectively zero; scheme open till 30 September; banks sought clarity on lending to non-residents through overseas branches, now granted.",
            "The Hindu BusinessLine (thehindubusinessline.com, 17 June 2026) \u2014 'RBI temporarily withdraws interest rate ceiling on fresh FCNR(B) deposits of 3-5 yr tenor': revised rates of ~6-7% on FCNR(B) reflect RBI bearing full hedging cost; pre-scheme three-year FCNR(B) rate ~3.35%, hedging forward premium ~3.5%, card rate ~6.5% (SBI report); SBI economists expect ~\u002440-45bn via the FCNR(B) route; RBI ran a similar FCNR swap window during the 2013 taper tantrum that brought in over \u002420bn; rupee down ~15% over the past year."
        ]),
        "diaspora_angle": "The RBI is absorbing the currency-hedging cost on new three-to-five-year FCNR(B) deposits, pushing dollar rates for non-resident Indians to 6-7% with no rupee risk \u2014 and with loans now permitted against those deposits through GIFT City, leveraged returns could approach 12-15%, making 'sending money home' a genuinely competitive investment for the world's 35-million-strong Indian diaspora rather than an act of sentiment.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: Indian Embassy UAE pauses consular services \u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Indian Embassy UAE pauses consular services")
    print("="*60)

    slug = "indian-embassy-uae-pauses-passport-visa-consular-services-june-26-30-bls-sgivs-al-hind-provider-switch-20260625"
    headline = "India's UAE Embassy Is Hitting Pause on Passports and Visas for Five Days. Here's What 4 Million Indians Need to Know."
    subheadline = "Regular consular services in the UAE shut from June 26 to June 30 as the mission swaps outsourcing partners. From July 1, a new operator, Al Hind Tours and Travel, takes over passport, visa and attestation work."

    body = """For the roughly 4.4 million Indians who call the United Arab Emirates home \u2014 the single largest concentration of the diaspora anywhere in the world \u2014 a routine errand is about to get briefly complicated. The Embassy of India in Abu Dhabi has announced that regular passport, visa, attestation and consular services across the UAE will be paused from June 26 to June 30, 2026, while the mission changes the private firm that runs its application centres.

It is a bureaucratic handover rather than a crisis, but for a community that depends on these centres for everything from renewing a child's passport to attesting a degree certificate for a new job, the five-day gap is worth planning around.

## What Is Actually Changing

The pause stems from a switch in outsourced service providers. Until June 25, the existing operators \u2014 BLS International and SGIVS Global \u2014 continued to accept applications. After that date, they stopped taking new submissions. From July 1, a newly appointed firm, Al Hind Tours and Travel LLC, takes over the management of passport, visa and attestation services across the UAE.

The five days in between are the transition window. During that period, no regular appointments for passport, visa or consular services will be available through the application centres. The embassy said the change follows a formal tender and evaluation process, and is being managed to ensure what it called a smooth handover.

## The Reassurance in the Fine Print

Two details will matter most to worried applicants. First, anything already submitted is safe: the embassy stressed that applications lodged before the transition will continue to be processed through the existing centres without disruption. If your paperwork is already in the system, you do not need to do anything.

Second, emergencies are still covered. During the five-day pause, emergency consular assistance will be handled directly by the Embassy of India in Abu Dhabi and the Consulate General of India in Dubai. Anyone facing an urgent situation \u2014 a death in the family requiring travel, a lost passport, a medical emergency \u2014 can reach the authorities through a dedicated toll-free number, WhatsApp line and email that the mission has published. From July 1 onward, all new applications will be routed through the centres operated by Al Hind Tours and Travel.

## Why a Five-Day Gap Is a Big Deal Here

The numbers explain the sensitivity. Indians make up close to a third of the UAE's total population and are woven into every layer of its economy, from construction sites to hospital wards to corporate boardrooms. The volume of consular work that flows through these centres \u2014 passport renewals, visa stamping, document attestation, emergency certificates \u2014 is enormous, and even a short interruption ripples through the plans of thousands of families.

A blue-collar worker whose passport is expiring may need it renewed to keep a job or visa valid. A student heading to a university abroad needs degree certificates attested on a deadline. A family planning summer travel back to India needs documents in order. For all of them, a five-day blackout in late June is a scheduling problem that rewards anyone who acts early.

## Why It Matters for the Diaspora

The episode is a small but useful reminder of how much of life abroad runs through the machinery of consular services \u2014 and how a back-office contract change in Abu Dhabi can touch millions of lives. The practical takeaway is straightforward: if you have a passport renewal, visa application or attestation that can be filed before June 26, do it now through the existing BLS or SGIVS centres, and it will be processed without interruption. If your need falls inside the June 26-30 window and is not an emergency, plan to submit from July 1 through the new provider.

For the broader diaspora, the smoother story is the one underneath: India has been steadily professionalising the way it serves its citizens overseas, putting consular work out to formal tender and rotating providers to keep service standards up. The transition will be invisible to most within a week. But for the family with a deadline this week, the difference between filing on June 24 and waiting until July 1 is the difference between a non-event and a scramble \u2014 which is exactly why the embassy put out the notice early."""

    img_url, ititle = pick_commons([
        "Embassy of India Abu Dhabi",
        "Abu Dhabi skyline",
        "Abu Dhabi cityscape",
        "Indian passport document",
        "Dubai skyline"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "Abu Dhabi, where the Indian Embassy is pausing regular passport, visa and consular services from June 26 to 30 during a provider switch"

    if not img_url:
        px = fetch_pexels_image("abu dhabi skyline uae")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Indian consular services across the UAE pause June 26-30 as the embassy changes its outsourced provider"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-services",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Channel iam (en.channeliam.com, 23 June 2026) \u2014 'India Embassy UAE Pauses Services': the Embassy of India in Abu Dhabi announced a temporary pause in regular passport, visa and consular services from June 26 to June 30, 2026, due to a change in its outsourced service provider in the UAE; Al Hind Tours and Travel LLC will take over passport, visa and attestation services from July 1, 2026; until June 25 existing providers BLS International and SGIVS Global continued accepting applications, after which no new submissions processed through them; no regular appointments available during the five-day transition; emergency consular assistance handled directly by the Embassy in Abu Dhabi and the Consulate General in Dubai via toll-free number, WhatsApp and email; applications submitted before transition processed without disruption; from July 1 all new applications routed through the new provider; change follows a formal tender and evaluation process.",
            "Indian diaspora population data (en.wikipedia.org, accessed 25 June 2026) \u2014 Indians in the United Arab Emirates number approximately 4,425,144, the largest single national concentration of the Indian diaspora; Indians constitute roughly a third of the UAE's total population."
        ]),
        "diaspora_angle": "Regular Indian passport, visa, attestation and consular services across the UAE \u2014 home to the world's largest Indian diaspora community of about 4.4 million \u2014 are paused from June 26 to 30 as the embassy switches its outsourced provider from BLS/SGIVS to Al Hind Tours and Travel, meaning non-emergency applicants should file before June 26 or wait until July 1, while already-submitted applications and genuine emergencies remain covered.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    print("Videshi News Writer \u2014 2026-06-26 04:30 UTC run")
    id1 = write_article_1()
    id2 = write_article_2()
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Article 1 (RBI FCNR(B) diaspora deposit scheme): {'OK id=' + str(id1) if id1 else 'FAILED'}")
    print(f"Article 2 (Indian Embassy UAE consular pause): {'OK id=' + str(id2) if id2 else 'FAILED'}")
