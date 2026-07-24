#!/usr/bin/env python3
"""
Videshi News Writer — June 13, 2026 batch
3 articles for the "news" category
"""

import os, json, requests, urllib.parse, uuid, subprocess, time, re
from datetime import datetime, timezone

# Load env
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
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=5):
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
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
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
                print(f"  ✓ Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def download_and_compress(url, slug):
    """Download image, compress to JPEG, upload to Supabase storage."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Download failed ({r.status_code}): {url[:80]}")
            return None
        ct = r.headers.get("Content-Type", "")
        if "image" not in ct and len(r.content) < 5000:
            print(f"  ⚠ Not an image or too small: {ct}, {len(r.content)} bytes")
            return None

        # Compress with PIL
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(r.content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > 1200:
            ratio = 1200 / img.width
            img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80, optimize=True)
        compressed = buf.getvalue()

        if len(compressed) < 5000:
            print(f"  ⚠ Compressed image too small: {len(compressed)} bytes")
            return None

        print(f"  ✓ Compressed: {len(r.content)} → {len(compressed)} bytes")

        # Upload to Supabase storage
        filename = f"{slug}.jpg"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        
        # Try delete first (ignore errors)
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
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None

    except Exception as e:
        print(f"  ⚠ Download/compress error: {e}")
        return None


def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  ✓ Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ─── Article 1: IT Sector 27% Rout ────────────────────────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: India's IT Sector 27% Rout — AI Repricing")
    print("="*60)

    slug = "nifty-it-down-27-percent-2026-ai-repricing-outsourcing-structural-shift-20260613"
    headline = "Nifty IT Has Lost 27% This Year. The Market Is Not Punishing a Cycle. It Is Repricing an Entire Industry."
    subheadline = "Seven consecutive sessions of losses, 40,000 layoffs, and a TCS chairman who says AI agents will match headcount. The structural reckoning India's outsourcing machine tried to postpone has arrived."

    body = """India's $315 billion IT services industry — the sector that made Bangalore a global noun and sent a generation of engineers to Cupertino, Seattle, and Jersey City — is in the middle of its worst stock market rout in over a decade. And this time, the market is not reacting to a bad quarter. It is reassessing whether the business model itself has a future.

The Nifty IT index has fallen 27 per cent since January, making it the worst-performing sectoral index on the Indian market this year. In one stretch this week, it lost 10.6 per cent across seven consecutive sessions — the kind of sustained selling typically seen during recessions or financial crises, not mid-cycle corrections.

Every name was hit. Wipro fell 15.47 per cent in those seven sessions. TCS dropped 14.57 per cent. Infosys lost 12.33 per cent. HCLTech declined 10.75 per cent. On Friday, when the broader Sensex rallied 2.3 per cent on peace deal hopes, IT stocks fell another 4.2 per cent. The market is making a directional statement.

## What Changed

The trigger was not a single earnings miss but a cascade of signals that the AI productivity curve is now steep enough to reduce the need for human labour in software services — the core of what India's top IT firms sell.

Anthropic's latest AI models, Claude Fable 5 and Mythos 5, launched in early June, intensified these fears. Analysts say the models deliver software engineering capabilities approaching human quality, with the gap expected to close within a year. For an industry built on billing hours of human coding, testing, and maintenance work, this is not a competitive threat from another company. It is a threat from the tool itself.

"The key concern is that productivity improvements in software engineering are occurring much faster than in non-software domains," said Sumit Pokharna, senior vice president of fundamental research at Kotak Securities. "This increases the risk of lower effort requirements, reduced billing volumes, and pricing pressure for traditional application development and maintenance contracts."

## The Numbers Behind the Narrative

TeamLease Digital counted close to 40,000 tech layoffs across India over the past year, including mid-level managerial roles — not just freshers. TCS alone shed 23,400 jobs in the fiscal year ending March 2026. Oracle laid off an estimated 10,000 people in India and redirected the budget toward AI infrastructure.

India's top six IT companies collectively reduced headcount by 71,936 in FY24 and added back only 15,375 in FY25. ICRA confirmed seven consecutive quarters of negative net hiring through Q1 FY25.

In the United States, a Stanford study using ADP payroll data found that employment for workers aged 22 to 25 in AI-exposed roles fell 13 per cent since late 2022. For young software developers specifically, the drop was 20 per cent.

TeamLease Digital CEO Neeti Sharma called it "a structural — not cyclical — correction driven by AI-led productivity compression."

## TCS Says the Quiet Part Out Loud

At TCS's annual general meeting this week, Chairman N. Chandrasekaran made the most explicit statement yet from an Indian IT chief: the company is moving toward having an equal number of employees and AI agents.

"If the company has half a million employees, the day is not far when the company will have half a million AI agents," he said. "The company's employees and AI agents will work together, and that will be the future."

TCS shares have fallen more than 32 per cent in 2026. The company announced a partnership with Anthropic this week to deploy Claude across 50,000 employees — the same AI firm whose product launch in February wiped more than $62.8 billion off Indian IT market capitalisation in a single month.

## The Counterargument: India Is 'Over-Punished'

Not everyone thinks the selloff is rational. BlackRock said this week that India's equity market has been "over-punished" for lacking a direct AI play, noting that the market had lost its position relative to South Korea and Taiwan on market capitalisation. Foreign investors have pulled a record $30 billion from Indian equities this year, piling into semiconductor names in East Asia.

Lighthouse Canton, a global wealth manager, went further. Chief Investment Officer Abhay Laijawala argued that India's absence from chip fabrication is actually an "advantage of absence" — the next wave of AI spending goes into power infrastructure, data centres, cooling systems, electrical equipment, and engineering goods, all of which India has listed companies for.

"We have plenty of picks and shovels," Laijawala said.

## What It Means for the Diaspora

For the estimated four million Indian-origin technology workers in the United States alone, this is personal. The traditional pipeline — an engineering degree from an IIT or NIT, a services job at TCS or Infosys, an H-1B transfer to the US — is being squeezed from both ends. Fewer entry-level positions in India. Fewer billable roles to justify a visa transfer abroad.

For NRIs invested in Indian IT stocks through mutual funds, NRE portfolios, or direct equity, the 27 per cent drawdown has erased years of compounding. The sector that once seemed like a one-way bet on India's human capital advantage is being revalued on the assumption that human capital is becoming less scarce.

The question is not whether AI will displace some IT services work. It already has. The question is how quickly — and whether India's IT firms can reinvent themselves as AI-native companies fast enough to recapture the premium the market once gave them. TCS is trying with its Anthropic partnership. Infosys struck a similar deal in February. But the market, for now, is not buying the pivot. It is selling the legacy."""

    # Source image
    print("  Sourcing image...")
    # Try Wikimedia Commons for Bangalore tech/IT
    commons = fetch_wikimedia_commons_images("Bangalore technology park India IT")
    img_url = None
    img_caption = "The skyline of Bangalore's Outer Ring Road technology corridor, home to India's largest concentration of IT services firms"
    img_attribution = "Wikimedia Commons"

    if commons:
        img_url = commons[0]["url"]
    else:
        # Try Pexels
        pexels = fetch_pexels_image("Bangalore India technology office skyline")
        if pexels:
            img_url = pexels
            img_attribution = "Pexels"
            img_caption = "A technology office building in Bangalore, the hub of India's IT services industry"

    final_img_url = None
    if img_url:
        final_img_url = download_and_compress(img_url, slug)

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "technology",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters — Indian IT Stocks Tumble, Nifty IT Down 26.6% YTD",
            "Reuters — TCS Chair Says AI Agents May Equal Headcount",
            "Reuters — Lighthouse Canton Says India Past Peak Outflows",
            "Outlook Money — Nifty IT Has Lost 10% In A Week",
            "LinkedIn — TeamLease Digital, 40,000 Tech Layoffs",
            "Kotak Securities — Sumit Pokharna Analysis"
        ]),
        "diaspora_angle": "Millions of NRIs work in IT services or hold IT stocks — the 27% rout directly impacts diaspora wealth and the H-1B pipeline that brought many to the US.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: FCNR Leverage Play ────────────────────────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: FCNR Leverage — 21.8% Dollar Returns")
    print("="*60)

    slug = "rbi-fcnr-leverage-21-percent-dollar-returns-nri-deposits-emkay-september-20260613"
    headline = "RBI Just Turned Dollar Deposits Into a 21% Yield Machine for NRIs. The Window Closes September 30."
    subheadline = "Banks are advertising 7 per cent on FCNR deposits. But the real story is what happens when you layer leverage on top. Emkay says a million-dollar deposit could generate $220,000 a year."

    body = """The Reserve Bank of India's decision to absorb the full foreign exchange hedging cost on fresh FCNR(B) deposits was supposed to attract dollar inflows and defend the rupee. It has done that. But it has also created an unusual opportunity that wealth managers and private bankers across the Gulf and the United States are now racing to structure for their NRI clients: the possibility of earning equity-like returns from what is essentially a fixed-income instrument.

The headlines this week focused on the deposit rates themselves. Banks have hiked aggressively. AU Small Finance Bank is offering 7.10 per cent on three-year dollar deposits. Yes Bank is at 7 per cent. Karur Vysya Bank and Tamilnad Mercantile Bank have both moved to 7 per cent. The major banks — HDFC Bank, SBI, ICICI, Kotak Mahindra — are clustered around 5.5 to 6.15 per cent, depending on the amount and tenure.

But the rates are only the beginning of the story.

## The Leverage Math

According to calculations by Emkay Global Financial Services, an NRI investor depositing one million dollars and leveraging it nine times through margin lending could generate annual returns of approximately $220,000 — a return of 21.8 per cent on the original capital deployed. Even at more conservative leverage levels of five times and three times, returns work out to 15 per cent and 11.6 per cent, respectively.

These are equity-like returns from a fixed-income product denominated in dollars, with no rupee conversion risk.

The mechanics are straightforward. RBI's new circular, announced on June 5 as part of a broader package to support the rupee, allows banks to swap their dollar inflows with the central bank at the same exchange rate in and out, with zero cost. RBI absorbs the currency mismatch on its own balance sheet. Banks pass the savings on as higher deposit rates.

What private bankers have noticed is that the scheme also allows banks to provide guarantees to offshore lenders, who then lend to NRIs. Those borrowed funds can be placed as FCNR(B) deposits. The result is a leveraged carry trade within a regulated banking framework.

## How It Works, Step by Step

An NRI deposits, say, $1 million in FCNR(B) at an Indian bank offering 6.5 per cent. With RBI's swap window absorbing the hedging cost, the bank's effective cost of funds is much lower than usual. The NRI then borrows against that deposit — typically at 1 to 2 per cent over the deposit rate — and redeposits the borrowed amount. Each layer of leverage amplifies the spread between the borrowing cost and the deposit rate that RBI is subsidising.

The product is not new. FCNR(B) deposits have existed for decades. What is new is the subsidy. By removing the 2 to 3 per cent annual hedging cost that previously capped returns, RBI has effectively lifted the ceiling on what banks can offer — and what leverage structures can yield.

## The Window

The scheme runs from June 8 to September 30, 2026. Fresh deposits raised during this window are exempt from statutory reserve requirements (CRR and SLR), further reducing the bank's cost. The minimum tenure is three years, with a one-year lock-in period.

SBI economists estimate $40 to $45 billion could flow in through the FCNR(B) route. Jefferies puts the upper estimate at $50 to $70 billion.

## Who Benefits

The scheme is most attractive to NRIs with significant dollar liquidity — those in the Gulf states, the United States, the United Kingdom, and Canada. For someone sitting on a dollar savings balance earning 4.5 to 5 per cent at a US bank, an FCNR(B) deposit at 6.5 to 7 per cent — with the option of leverage — represents a meaningful uplift with no currency risk, since principal and interest are repaid in dollars.

The tax treatment is also favourable. FCNR(B) interest is exempt from Indian income tax for eligible NRI and OCI depositors, provided the depositor qualifies under the Income Tax Act. (US-based NRIs still owe US taxes on global income, but can claim foreign tax credits.)

## The Risks

Leverage amplifies returns, but it also amplifies risk. If a bank's credit quality deteriorates, the deposit could face delays. DICGC insurance covers only up to ₹5 lakh — negligible for a large dollar deposit. Premature withdrawal before the one-year lock-in is not permitted, and exit after that is at the bank's discretion.

There is also the question of whether the RBI subsidy itself will be extended. The scheme expires September 30. If the rupee stabilises before then — perhaps aided by a US-Iran peace deal that reduces India's oil import bill — RBI may not need to extend it. NRIs who enter late may have less flexibility to exit.

## The Bottom Line

For NRIs with dollar savings, the FCNR(B) window is the most attractive fixed-income opportunity from India in years. The base rates of 6 to 7 per cent already beat most US money market funds. The leverage play — available through private banking channels — can push yields well into double digits. But the window is narrow, the lock-in is real, and the subsidy is temporary. The math works today. Whether it works in October is a different question."""

    # Source image
    print("  Sourcing image...")
    commons = fetch_wikimedia_commons_images("Reserve Bank of India Mumbai building")
    img_url = None
    img_caption = "The Reserve Bank of India headquarters in Mumbai"
    img_attribution = "Wikimedia Commons"

    if commons:
        for c in commons:
            if "reserve" in c.get("title", "").lower() or "rbi" in c.get("title", "").lower():
                img_url = c["url"]
                break
        if not img_url:
            img_url = commons[0]["url"]

    if not img_url:
        img_url = fetch_pexels_image("Indian rupee currency dollar banking")
        if img_url:
            img_attribution = "Pexels"
            img_caption = "Indian rupee and US dollar notes"

    final_img_url = None
    if img_url:
        final_img_url = download_and_compress(img_url, slug)

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
            "Mint — RBI's FCNR Move Opens Door to Equity-Like Dollar Returns for NRIs",
            "Reuters — Some Lenders Hike Rates on FX Deposits for Non-Resident Indians",
            "The Hindu BusinessLine — Smaller Lenders Offer Over 7% on USD Deposits",
            "Outlook Business — SBI, ICICI, Other Banks Hike FCNR Deposit Rates",
            "Value Research — RBI Is Offering NRIs Up to 7% on Dollar Deposits"
        ]),
        "diaspora_angle": "NRIs in the US, UK, Gulf, and Canada with dollar savings now have a narrow window to earn 6-7% (or much more with leverage) in a risk-free-currency deposit at Indian banks — the best FCNR opportunity in years.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 3: India Demands US Attacks Cease ────────────────────

def write_article_3():
    print("\n" + "="*60)
    print("ARTICLE 3: India Maritime Alert — US Tanker Strikes")
    print("="*60)

    slug = "india-demands-us-attacks-cease-three-tankers-sailors-killed-maritime-alert-20260613"
    headline = "'These Attacks Must Cease and End.' India Lodges a Second Diplomatic Protest After Three Ships Are Hit in Five Days."
    subheadline = "India's shipping ministry has ordered all agencies on heightened alert. The US has disabled nine vessels and redirected 135 others in its blockade. Three Indian sailors are dead."

    body = """India lodged a second diplomatic protest with the United States on Friday after American forces struck three Indian-crewed oil tankers in the Gulf of Oman in the space of five days, killing three sailors and putting hundreds of Indian seafarers in the line of fire.

"These attacks must cease and end," said Randhir Jaiswal, spokesperson for India's Ministry of External Affairs. "We also call for dialogue and diplomacy so that we can have an early return to peace and stability in the region."

The statement, unusually direct for Indian diplomacy, came as the Ministry of Ports, Shipping, and Waterways ordered all government agencies to remain on "heightened alert" and maintain readiness to respond to any contingency involving Indian seafarers or maritime interests. The Directorate General of Shipping issued an advisory to all Indian seafarers serving on Indian and foreign-flagged vessels in conflict-affected waters to exercise "the highest degree of caution and vigilance."

## Three Ships in Five Days

The escalation has been swift. On Monday, US forces disabled the M/T Marivex using precision munitions after the vessel allegedly failed to comply with blockade directions. On Tuesday, a US aircraft fired into the engine room of the M/T Settebello, a Palau-flagged tanker. Twenty-four Indian mariners were aboard. Three were killed. Twenty-one were rescued by the Omani Navy after jumping overboard when the engine room caught fire.

On Thursday, a US aircraft fired two Hellfire missiles into the engine room of the M/T Jalveer, a Guinea-Bissau-flagged tanker, again after the crew allegedly failed to comply. Twenty Indian seafarers were evacuated in coordination with the Omani Navy. All survived.

In each case, US Central Command said the vessels had violated the ongoing blockade by attempting to transport oil from Iran. Since imposing the blockade on April 13, the US military has disabled nine non-compliant vessels, redirected 135 others, and allowed 42 vessels carrying humanitarian aid to pass through.

## A Peace Deal and a Blockade, Simultaneously

The attacks have continued even as the United States and Iran signal that a memorandum of understanding to end the war could be signed as soon as this weekend, possibly in Geneva. Pakistan's Prime Minister Shehbaz Sharif said on Friday that the two sides had reached "a final, agreed-upon text" of a peace deal.

But on the same day, US forces shot down multiple Iranian drones heading toward the Strait of Hormuz, underscoring how fragile the situation remains. Iranian Foreign Minister Abbas Araqchi declared on state television: "Our sword will always hang over the Strait of Hormuz."

For India, the paradox is acute. A peace deal would bring down crude oil prices — Brent fell to $87.33 per barrel on Friday, a near three-month low — easing pressure on India's import bill and fiscal deficit. But the blockade that is supposed to end with the deal is, in the meantime, killing Indian citizens.

## "If He Had Told Us, I Would Have Called Him Back"

Sushila Devi sat sobbing on the floor of her house in Deoria, Uttar Pradesh, after authorities confirmed that her husband, Shivanand Chaurasia, was one of the three sailors killed aboard the Settebello. He was the sole earner in the family and had two young children.

"If he had told us about the dangers, I would have called him back," she said. "The government should not allow people to go there."

India has more than 300,000 sailors working in global shipping fleets, according to government data. Many serve on vessels flagged to countries of convenience — Palau, Guinea-Bissau, Liberia — that offer limited protections. When a blockade enforcement action turns lethal, it is often Indian crews who pay the price.

India's shipping minister, Sarbananda Sonowal, called the deaths "a profound loss to our maritime family." The ministry said it was coordinating with the Ministry of External Affairs, the Indian Navy, and maritime administrations of friendly countries.

## The Diplomatic Calculus

India summoned the US deputy chief of mission in New Delhi on Wednesday to convey "its deepest concerns over the ongoing attacks." A second protest was lodged on Friday.

Critics say the response has been insufficient. India has not threatened retaliatory diplomatic measures, has not recalled its ambassador, and Prime Minister Modi has not publicly commented on the deaths — a silence that has drawn growing attention as he departed for a six-day visit to France and Slovakia, where he is expected to meet President Trump at the G7 summit.

The government's position appears to balance outrage at the strikes against the broader diplomatic calculus: India needs the US-Iran war to end, needs the Strait of Hormuz to reopen, and needs the trade relationship with Washington to hold together through an interim trade deal expected by mid-July. Calling out the blockade too forcefully risks complicating all three.

But for the families in Deoria and coastal India, diplomacy is not the point. Their men went to sea to earn a living. Three of them are not coming home."""

    # Source image: Try Wikipedia for Strait of Hormuz or Indian Navy
    print("  Sourcing image...")
    commons = fetch_wikimedia_commons_images("Strait of Hormuz shipping tanker")
    img_url = None
    img_caption = "Oil tankers in the waters near the Strait of Hormuz, the choke point at the centre of the US-Iran conflict"
    img_attribution = "Wikimedia Commons"

    if commons:
        for c in commons:
            title_lower = c.get("title", "").lower()
            if "hormuz" in title_lower or "tanker" in title_lower or "gulf" in title_lower:
                img_url = c["url"]
                break
        if not img_url and commons:
            img_url = commons[0]["url"]

    if not img_url:
        img_url = fetch_pexels_image("oil tanker cargo ship ocean")
        if img_url:
            img_attribution = "Pexels"
            img_caption = "An oil tanker at sea"

    final_img_url = None
    if img_url:
        final_img_url = download_and_compress(img_url, slug)

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters — India Orders Agencies on Alert After Strikes on Ships in Gulf",
            "Reuters — India Demands End to US Attacks on Ships After Three Sailors Killed",
            "Reuters — US Confirms Third Strike on Indian-Crewed Tankers This Week",
            "Reuters — Indians Grieve and Call for Action After US Strike Kills Sailors",
            "Reuters — Iran Peace Deal Looms, New Military Action Flares Near Strait of Hormuz"
        ]),
        "diaspora_angle": "More than 300,000 Indian sailors serve in global shipping fleets — the Gulf crisis puts their lives at risk while NRIs watch the diplomatic fallout between Delhi and Washington unfold.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Main ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Videshi News Writer — June 13, 2026")
    print("=" * 60)

    results = []

    art1 = write_article_1()
    results.append(("IT Sector Rout", art1))

    art2 = write_article_2()
    results.append(("FCNR Leverage", art2))

    art3 = write_article_3()
    results.append(("Maritime Alert", art3))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, art_id in results:
        status = "✓ OK" if art_id else "✗ FAILED"
        print(f"  {status} — {name}: {art_id}")

    failed = sum(1 for _, aid in results if not aid)
    print(f"\nTotal: {len(results)} articles, {len(results)-failed} succeeded, {failed} failed")
