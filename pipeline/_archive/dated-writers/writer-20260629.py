#!/usr/bin/env python3
"""
Writer script for The Videshi — June 29, 2026 news batch.
Two articles:
1. Kotak Mahindra Bank CEO Ashok Vaswani stepping down
2. Fairfax India / Prem Watsa buys $1B in Indian bonds ahead of IDBI Bank bid
"""

import os, sys, json, subprocess, time, urllib.parse, re, hashlib
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────────
def load_env(path):
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env("~/.env.supabase")
load_env("~/workspace/.env.pexels")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY   = os.environ.get("PEXELS_API_KEY", "")

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"

# ── helpers ──────────────────────────────────────────────────────────────

def curl_get(url, headers=None, timeout=15):
    """HTTP GET via curl (proxy-friendly)."""
    cmd = ["curl", "-sS", "-L", "--max-time", str(timeout), "-A", UA]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
    return r.stdout

def fetch_wikipedia_person_image(person_name):
    """Fetch person image from Wikipedia REST API."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    try:
        raw = curl_get(url)
        data = json.loads(raw)
        img = (data.get("originalimage") or {}).get("source") or (data.get("thumbnail") or {}).get("source")
        if img:
            print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
            return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons(query, limit=5):
    """Search Wikimedia Commons, return list of image dicts."""
    params = urllib.parse.urlencode({
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    })
    url = f"https://commons.wikimedia.org/w/api.php?{params}"
    try:
        raw = curl_get(url)
        data = json.loads(raw)
        pages = data.get("query", {}).get("pages", {})
        results = []
        for pid, page in pages.items():
            ii = (page.get("imageinfo") or [{}])[0]
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
                "height": ii.get("height", 0),
            })
        if results:
            print(f"  ✓ Commons: {len(results)} images for '{query}'")
        return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{query}': {e}")
        return []

# Relevance gate for commons images
_COMMONS_STOP = set("the a an of in and for to from with at on by is are was were be been being it its this that these those".split())
_COMMONS_NEGATIVE = {
    "us capitol": ["state capitol", "pennsylvania", "harrisburg", "austin", "sacramento"],
    "white house": ["gingerbread", "christmas tree"],
    "supreme court": ["state supreme"],
}

def commons_relevance_ok(file_title, headline, topic):
    """Check if a Commons file title is relevant to the article."""
    ft = file_title.lower()
    hl = headline.lower()
    # negative confusables check
    for key, negatives in _COMMONS_NEGATIVE.items():
        if key in hl and any(neg in ft for neg in negatives):
            return False
    # positive: at least one distinctive keyword
    words = set(re.findall(r'[a-z]{4,}', hl + " " + topic.lower())) - _COMMONS_STOP
    if not words:
        return True  # all-generic headline, don't over-filter
    return any(w in ft for w in words)

def verify_image_url(url):
    """Verify image URL returns 200 with image content-type and >5KB."""
    try:
        cmd = ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}|%{content_type}|%{size_download}", 
               "--max-time", "10", "-A", UA, url]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        parts = r.stdout.strip().split("|")
        if len(parts) >= 3:
            code = parts[0]
            ctype = parts[1]
            size = float(parts[2])
            if code == "200" and "image" in ctype and size > 5000:
                return True
    except:
        pass
    return False

def download_and_compress(url, out_path, max_width=1200, quality=82):
    """Download image and compress with ImageMagick."""
    tmp_raw = f"/tmp/raw_{hashlib.md5(url.encode()).hexdigest()[:12]}"
    cmd = ["curl", "-sS", "-L", "--max-time", "20", "-A", UA, "-o", tmp_raw, url]
    subprocess.run(cmd, capture_output=True, timeout=25)
    if not os.path.exists(tmp_raw) or os.path.getsize(tmp_raw) < 5000:
        print(f"  ✗ Download failed: {url[:80]}")
        return False
    try:
        subprocess.run([
            "convert", tmp_raw, "-resize", f"{max_width}x>", "-quality", str(quality),
            "-strip", out_path
        ], capture_output=True, timeout=30)
        if os.path.exists(out_path) and os.path.getsize(out_path) > 5000:
            return True
    except:
        pass
    return False

def upload_to_supabase(local_path, bucket, remote_path):
    """Upload to Supabase storage. Returns public URL or None."""
    import mimetypes
    mt = mimetypes.guess_type(local_path)[0] or "image/jpeg"
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{remote_path}"
    cmd = [
        "curl", "-sS", "-X", "POST", url,
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", f"Content-Type: {mt}",
        "-H", "x-upsert: true",
        "--data-binary", f"@{local_path}",
        "--max-time", "30"
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
    if r.returncode == 0:
        try:
            resp = json.loads(r.stdout)
            if resp.get("Key") or resp.get("Id"):
                public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{remote_path}"
                print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
                return public_url
        except:
            pass
    print(f"  ✗ Upload failed: {r.stdout[:200]}")
    return None

def insert_article(article):
    """Insert article into p2_articles. Returns the inserted row or None."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    cmd = [
        "curl", "-sS", "-X", "POST", url,
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=representation",
        "-d", json.dumps(article),
        "--max-time", "15"
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    try:
        data = json.loads(r.stdout)
        if isinstance(data, list) and data:
            return data[0]
        elif isinstance(data, dict) and data.get("id"):
            return data
        else:
            print(f"  ✗ Insert error: {r.stdout[:300]}")
            return None
    except:
        print(f"  ✗ Insert parse error: {r.stdout[:300]}")
        return None


# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 1: Kotak Mahindra Bank CEO Ashok Vaswani stepping down
# ═══════════════════════════════════════════════════════════════════════

def write_article_1():
    print("\n" + "="*70)
    print("ARTICLE 1: Kotak Mahindra Bank CEO stepping down")
    print("="*70)

    slug = "kotak-mahindra-bank-ceo-ashok-vaswani-steps-down-succession-uday-kotak-20260629"

    # ── Image sourcing ──
    print("\n→ Sourcing image...")
    image_url = None
    image_caption = ""
    image_attribution = ""

    # Try Wikipedia for Ashok Vaswani
    img = fetch_wikipedia_person_image("Ashok Vaswani")
    if not img:
        img = fetch_wikipedia_person_image("Ashok Vaswani (banker)")
    
    # Try Uday Kotak (more prominent)
    if not img:
        img = fetch_wikipedia_person_image("Uday Kotak")
    
    if img and verify_image_url(img):
        image_url = img
        if "uday" in img.lower() or "kotak" in img.lower():
            image_caption = "Uday Kotak, the billionaire founder of Kotak Mahindra Bank, who stepped down as CEO in 2023"
        else:
            image_caption = "Ashok Vaswani, outgoing CEO and Managing Director of Kotak Mahindra Bank"
        image_attribution = "Wikimedia Commons"
    
    # Try Wikimedia Commons for Kotak Mahindra
    if not image_url:
        commons = fetch_wikimedia_commons("Kotak Mahindra Bank", limit=5)
        for c in commons:
            if commons_relevance_ok(c["title"], "Kotak Mahindra Bank", "banking"):
                if verify_image_url(c["url"]):
                    image_url = c["url"]
                    image_caption = "Kotak Mahindra Bank, India's fourth-largest private sector lender"
                    image_attribution = "Wikimedia Commons"
                    break

    if not image_url:
        # Try a general Kotak / Mumbai banking image from commons
        commons = fetch_wikimedia_commons("Mumbai financial district banking", limit=5)
        for c in commons:
            if verify_image_url(c["url"]):
                image_url = c["url"]
                image_caption = "Mumbai's financial district, home to India's largest private banks"
                image_attribution = "Wikimedia Commons"
                break

    if not image_url:
        print("  ✗ No suitable image found — article will still proceed with no image")

    # ── Article body ──
    body = """India's fourth-largest private bank just lost its second CEO in three years — and this time, nobody pushed him out.

Ashok Vaswani, the Managing Director and CEO of Kotak Mahindra Bank, told the board on Saturday that he will not seek reappointment when his current term ends on December 31, 2026. He cited personal reasons. The board accepted his decision and has begun the search for a successor.

Vaswani's exit is not a firing. It is not a regulatory action. But it reopens the deepest question hanging over one of India's most closely watched financial institutions: who runs the bank that Uday Kotak built?

## Three Years, Two CEOs

Kotak Mahindra is not an ordinary bank. For more than two decades, it was inseparable from its founder, billionaire Uday Kotak, who turned a small bill-discounting firm into a financial conglomerate with a market capitalisation that once crossed ₹4 lakh crore. When Reserve Bank of India rules forced him to reduce his stake below 26 percent, Kotak stepped down as CEO in September 2023 — ending the longest founder-CEO run in Indian private banking.

Vaswani was the handpicked successor. A veteran of Barclays, Citigroup, and fintech firm Pagaya, he brought three decades of global banking experience. He joined on January 1, 2024, with the RBI's blessing and a mandate to modernise. Kotak himself called him the right person to "take the bank to its next orbit."

Now, less than three years in, Vaswani is leaving. His departure means the bank will have had three different leaders in four years — a level of turnover that is unusual for a top-tier Indian lender and unsettling for investors.

## The Market Reacted Immediately

Kotak Mahindra Bank shares dropped 3.3 percent on Monday morning, falling to ₹395.95 on the NSE, making it one of the worst performers on the Nifty 50. The stock is now down nearly 10 percent for the year and has underperformed the broader index over one, three, and five years.

Analysts noted that the bank does not currently have a Deputy Managing Director — a role that would have provided a natural interim successor. However, two recent executive director appointments offer internal options. Anup Saha, the former MD and CEO of Bajaj Finance, was laterally hired as Executive Director in January 2026. Paritosh Kashyap, a Kotak veteran, was elevated to the same rank in May 2025.

ICICI Securities retained a Buy rating on the stock with a target price of ₹480, calling any significant correction a buying opportunity.

## What Vaswani Inherited — and What He Leaves Behind

When Vaswani took over, Kotak Mahindra was navigating a period of regulatory scrutiny. The RBI had flagged concerns about the bank's IT systems, and the transition away from a founder-led structure required a cultural shift.

Under his watch, the bank posted a 13 percent rise in net profit in the March quarter to ₹40.27 billion, supported by stronger lending growth and lower provisions. He told Reuters earlier this month that his ambition was to make Kotak India's third-largest private lender by after-tax profit — an aspiration the next CEO will now carry forward.

In an internal note to staff, Vaswani said he would work closely with the chairman and the board during his remaining months to ensure a smooth transition.

## The Bigger Picture: India's Banking Succession Problem

Vaswani's departure is the latest in a series of leadership shakeups across India's biggest private banks. Shanti Ekambaram, a former Deputy MD at Kotak, retired in October 2025. KVS Manian, once a Joint MD, left to lead Federal Bank as its MD and CEO in September 2024. Each departure strips institutional memory from an organisation already adapting to life without its founder.

The challenge is not unique to Kotak. Across India's top private lenders, the era of founder-CEOs is ending. Axis Bank, HDFC Bank, and ICICI Bank have all navigated their own succession transitions over the past decade. But none had the combination of a founder exit, a successor exit, and ongoing regulatory reform compressed into such a short window.

## Why NRIs Should Watch This Closely

For the Indian diaspora, Kotak Mahindra Bank is a significant presence. The bank operates NRE and NRO accounts, processes cross-border remittances, and manages wealth for high-net-worth NRIs. Its digital banking push — the very area Vaswani was brought in to accelerate — is directly relevant to diaspora customers who rely on seamless mobile banking across borders.

A leadership vacuum at a major private bank can affect everything from product launches to service quality. The next CEO will need to balance Kotak's domestic growth ambitions with the digital infrastructure that makes the bank usable for Indians living abroad.

The succession process will be completed within applicable regulatory timelines, the bank said. The RBI typically takes several months to approve a new managing director. Vaswani remains in his role through December 31, 2026, so operations continue uninterrupted — for now.

*Sources: Reuters, Outlook Business, BSE filings, ICICI Securities research note*"""

    article = {
        "headline": "Kotak Mahindra's CEO Is Leaving After Less Than Three Years. The Bank Has Now Lost Two Leaders Since Its Founder Stepped Down.",
        "subheadline": "Ashok Vaswani, a Barclays and Citigroup veteran who was handpicked to succeed billionaire Uday Kotak, told the board he will not seek reappointment. The stock fell 3.3 percent.",
        "slug": slug,
        "body": body,
        "category": "news",
        "vertical": "banking",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url or "",
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com"},
            {"name": "BSE", "url": "https://www.bseindia.com"}
        ]),
        "diaspora_angle": "Kotak Mahindra Bank serves millions of NRI customers through NRE/NRO accounts, remittances, and digital banking — a leadership vacuum at the top affects the diaspora's banking experience directly.",
        "published_at": datetime.now(timezone.utc).isoformat(),
    }

    result = insert_article(article)
    if result:
        print(f"\n✅ Article 1 inserted: {result.get('id', 'OK')}")
        print(f"   Headline: {article['headline'][:80]}...")
    else:
        print("\n❌ Article 1 FAILED to insert")
    return result


# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 2: Fairfax / Prem Watsa buys $1B Indian bonds for IDBI Bank bid
# ═══════════════════════════════════════════════════════════════════════

def write_article_2():
    print("\n" + "="*70)
    print("ARTICLE 2: Fairfax / Prem Watsa IDBI Bank billion-dollar bond play")
    print("="*70)

    slug = "fairfax-prem-watsa-1-billion-indian-bonds-idbi-bank-privatisation-diaspora-20260629"

    # ── Image sourcing ──
    print("\n→ Sourcing image...")
    image_url = None
    image_caption = ""
    image_attribution = ""

    # Try Wikipedia for Prem Watsa
    img = fetch_wikipedia_person_image("Prem Watsa")
    if img and verify_image_url(img):
        image_url = img
        image_caption = "Prem Watsa, the Indian-Canadian billionaire who chairs Fairfax Financial Holdings"
        image_attribution = "Wikimedia Commons"

    # Try Wikimedia Commons for IDBI Bank
    if not image_url:
        commons = fetch_wikimedia_commons("IDBI Bank India", limit=5)
        for c in commons:
            if commons_relevance_ok(c["title"], "IDBI Bank Fairfax", "banking privatisation"):
                if verify_image_url(c["url"]):
                    image_url = c["url"]
                    image_caption = "IDBI Bank, the state-owned lender at the centre of India's biggest privatisation deal"
                    image_attribution = "Wikimedia Commons"
                    break

    # Try Reserve Bank of India / Indian government bonds angle
    if not image_url:
        commons = fetch_wikimedia_commons("Reserve Bank India Mumbai", limit=5)
        for c in commons:
            if commons_relevance_ok(c["title"], "Reserve Bank India bonds", "banking"):
                if verify_image_url(c["url"]):
                    image_url = c["url"]
                    image_caption = "The Reserve Bank of India headquarters in Mumbai"
                    image_attribution = "Wikimedia Commons"
                    break

    if not image_url:
        print("  ✗ No suitable image found — proceeding without image")

    # ── Article body ──
    body = """A Canadian holding company run by an Indian-born billionaire just quietly parked nearly $1 billion in Indian government bonds — and the move has almost nothing to do with bonds.

Fairfax India Holding Corp, led by Hyderabad-born Prem Watsa, bought approximately $1 billion worth of Indian sovereign debt at a single bond auction last week, according to five sources cited by Reuters. The purchases were concentrated in short-duration securities: roughly ₹60 billion ($634 million) of the 6.03 percent 2029 bond, ₹6 billion of the 6.79 percent 2027 bond, and ₹26 billion in treasury bills maturing in 2027.

It was one of the largest foreign purchases of Indian government debt in recent memory — and Fairfax is not a regular player in the Indian bond market.

## The Real Prize: IDBI Bank

The bond purchases, sources told Reuters, were designed to bring capital into the country ahead of a potential deal to acquire a majority stake in government-owned IDBI Bank. India's government and state-owned Life Insurance Corporation of India together hold 94.71 percent of the lender and have been planning to sell 60.72 percent — a stake worth roughly $7 billion at current valuations.

Fairfax has been in the running for years. The Toronto-based company was among the original bidders who filed expressions of interest, and the RBI has already cleared it as a "fit and proper" participant. But the process stalled this spring when potential buyers submitted bids below the government's reserve price.

Talks to revive the sale have continued, according to the source close to Fairfax, though there is no certainty of a deal.

A key factor making the bond purchase viable was India's recent decision to exempt foreign investors in government bonds from capital gains tax — a policy change designed precisely to attract the kind of inflows Fairfax just delivered.

## How Watsa Plays the Long Game

Prem Watsa, 76, is often called the "Warren Buffett of Canada." Born in Hyderabad, he emigrated to Canada in 1972 with $8 and built Fairfax Financial Holdings into a $30 billion insurance and investment conglomerate. His interest in Indian assets is deep and personal: Fairfax India Holding, the vehicle making the bond purchases, was created specifically to invest in the subcontinent.

Fairfax already controls CSB Bank, a small private lender in Kerala. Under Indian banking regulations, a single entity cannot be the promoter of two banks simultaneously. If Fairfax wins IDBI Bank, CSB Bank would likely be merged into the larger institution — a combination that sources say would benefit IDBI's balance sheet.

The bond play is vintage Watsa: instead of waiting for the privatisation process to restart, he moved capital into Indian sovereign debt — earning a yield, parking money in-country, and positioning Fairfax to act quickly if the government reopens bidding. He bought the 2029 bond at a yield roughly 5 basis points below market levels, a sign of urgency rather than bargain-hunting.

## The India-Canada Factor

The deal is also notable for its diplomatic backdrop. India-Canada relations have been strained since 2023, when Canada alleged Indian intelligence involvement in the killing of a Sikh separatist leader in British Columbia. India has denied the allegations, and the two governments expelled diplomats in a series of tit-for-tat moves that chilled bilateral ties.

Against that backdrop, a $1 billion bet by Canada's most prominent Indian-origin investor carries symbolic weight. Fairfax's willingness to commit that kind of capital to Indian sovereign debt — ahead of what could be the largest foreign acquisition of an Indian bank — signals that commercial logic is running ahead of diplomatic friction.

India's Department of Investment and Public Asset Management (DIPAM) did not respond to Reuters' queries. Fairfax India Holding did not comment.

## What the Diaspora Should Know

The IDBI Bank privatisation is the single largest test of India's willingness to hand a state-owned bank to a private buyer. If Fairfax succeeds, it would be the first time a foreign-origin investor has taken management control of a major Indian bank through outright acquisition rather than organic growth.

For NRIs and PIOs, the implications are direct. IDBI Bank has a nationwide branch network of over 1,800 offices and significant exposure to government programmes. A new private owner would likely modernise its technology, expand digital banking services, and potentially improve the NRI banking experience — an area where IDBI has historically trailed private-sector leaders like HDFC Bank and ICICI Bank.

The government's disinvestment target for FY2026-27 also depends heavily on the IDBI transaction. If Fairfax or another bidder closes the deal, the proceeds could fund infrastructure spending that creates jobs and reduces India's fiscal deficit — both factors that influence the rupee and the value of NRI investments.

The bond purchase tells us one thing clearly: Prem Watsa is not waiting. Whether the government is ready to sell is the question that remains.

*Sources: Reuters, The Hindu BusinessLine, BSE disclosures, Fairfax Financial Holdings annual reports*"""

    article = {
        "headline": "An Indian-Born Billionaire in Canada Just Parked $1 Billion in Indian Bonds. It's Not About the Bonds.",
        "subheadline": "Prem Watsa's Fairfax bought nearly $1 billion in Indian government debt in a single week — positioning to acquire a majority stake in state-owned IDBI Bank in what could be India's biggest bank privatisation ever.",
        "slug": slug,
        "body": body,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url or "",
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"},
            {"name": "BSE", "url": "https://www.bseindia.com"}
        ]),
        "diaspora_angle": "If Prem Watsa's Fairfax wins IDBI Bank, it would be the first time a foreign-origin investor takes control of a major Indian bank — reshaping NRI banking, remittances, and India's privatisation programme.",
        "published_at": datetime.now(timezone.utc).isoformat(),
    }

    result = insert_article(article)
    if result:
        print(f"\n✅ Article 2 inserted: {result.get('id', 'OK')}")
        print(f"   Headline: {article['headline'][:80]}...")
    else:
        print("\n❌ Article 2 FAILED to insert")
    return result


# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"The Videshi Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("="*70)
    
    r1 = write_article_1()
    r2 = write_article_2()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"  Article 1 (Kotak CEO): {'✅' if r1 else '❌'}")
    print(f"  Article 2 (Fairfax/IDBI): {'✅' if r2 else '❌'}")
    
    if r1 and r2:
        print("\nBoth articles inserted with status=review.")
    elif not r1 and not r2:
        print("\n⚠ Both articles failed!")
        sys.exit(1)
