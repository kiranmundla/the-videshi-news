#!/usr/bin/env python3
"""Writer run for 2026-06-29 morning: 2 articles."""
import os, json, subprocess, sys, urllib.parse, re, time, requests
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────
def load_env(path):
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env("~/.env.supabase")
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

UA = "TheVideshi/1.0 (thevideshi.com)"

# ── image helpers ────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error: {e}")
    return None

def fetch_wikimedia_commons(query, limit=5):
    params = {
        "action": "query", "generator": "search", "gsrsearch": query,
        "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime",
        "iiurlwidth": "1200", "format": "json",
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params, headers={"User-Agent": UA}, timeout=15,
        )
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
                })
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []

def fetch_pexels(query):
    """Fetch from Pexels using curl (urllib gets 403)."""
    key = os.environ.get("PEXELS_API_KEY", "")
    if not key:
        print("  ⚠ No PEXELS_API_KEY")
        return None
    cmd = [
        "curl", "-sS", "-H", f"Authorization: {key}",
        f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape",
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        data = json.loads(r.stdout)
        photos = data.get("photos", [])
        if photos:
            return photos[0]["src"]["large2x"]
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def verify_image(url):
    """Verify URL returns 200 with image content-type and >5KB."""
    try:
        cmd = ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code} %{content_type} %{size_download}", "-L", url]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        parts = r.stdout.strip().split()
        if len(parts) >= 3:
            code = parts[0]
            ctype = parts[1]
            size = float(parts[2])
            if code == "200" and "image" in ctype and size > 5000:
                return True
    except:
        pass
    return False

# ── commons relevance gate ───────────────────────────────────────────
_COMMONS_STOP = {
    "the","a","an","of","in","on","at","to","for","and","or","with","as","by","from","is",
    "are","was","were","be","new","says","after","over","amid","how","why","what","2024",
    "2025","2026","india","indian","us","usa","american","uk","first","more","than",
    "people","man","woman","group","day","year","top","big","set","get","make","makes",
    "made","you","your","they","them","this","that","social","media","using","use",
}

def _keywords(text):
    toks = re.findall(r"[A-Za-z][A-Za-z'-]+", text or "")
    return [t.lower() for t in toks if len(t) >= 4 and t.lower() not in _COMMONS_STOP]

def commons_relevance_ok(commons_title, headline, topic=""):
    title_l = (commons_title or "").lower()
    kws = set(_keywords(headline)) | set(_keywords(topic))
    if not kws:
        return True
    return any(kw in title_l for kw in kws)


# ── DB insert ────────────────────────────────────────────────────────
def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
    )
    if r.status_code in (200, 201):
        result = r.json()
        slug = result[0].get("slug") if isinstance(result, list) else result.get("slug")
        print(f"  ✓ Inserted: {slug}")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return False


# ════════════════════════════════════════════════════════════════════
# ARTICLE 1: RBI NRI Deposit Scheme — Diaspora as Rupee's Lifeline
# ════════════════════════════════════════════════════════════════════
def write_article_1():
    print("\n═══ Article 1: RBI NRI Deposit Scheme ═══")

    # Image: RBI building from Wikimedia Commons
    image_url = None
    image_caption = ""
    image_attribution = ""

    # Try Wikimedia Commons for RBI
    commons = fetch_wikimedia_commons("Reserve Bank of India building Mumbai")
    for c in commons:
        if commons_relevance_ok(c["title"], "RBI Reserve Bank India", "central bank monetary policy"):
            if verify_image(c["url"]):
                image_url = c["url"]
                image_caption = "The Reserve Bank of India headquarters in Mumbai"
                image_attribution = "Wikimedia Commons"
                print(f"  ✓ Using Commons: {c['title']}")
                break

    if not image_url:
        # Try Wikipedia for RBI
        img = fetch_wikipedia_person_image("Reserve Bank of India")
        if img and verify_image(img):
            image_url = img
            image_caption = "The Reserve Bank of India headquarters in Mumbai"
            image_attribution = "Wikimedia Commons"

    if not image_url:
        # Fallback: Pexels for Indian currency/banking
        img = fetch_pexels("Indian rupee currency notes")
        if img and verify_image(img):
            image_url = img
            image_caption = "Indian rupee notes"
            image_attribution = "Pexels"

    if not image_url:
        print("  ✗ No valid image found, using blank")
        return False

    slug = "rbi-nri-fcnr-deposit-scheme-banks-7-percent-diaspora-dollar-inflows-20260629"
    headline = "India's Central Bank Just Gave NRIs a Reason to Move Their Dollars Home. Banks Are in a Frenzy to Cash In."
    subheadline = "The RBI is bearing the hedging cost on foreign currency deposits so NRIs can earn 7% risk-free on their dollars. Banks are scrambling to attract up to $100 billion, and the diaspora holds the key to rescuing the rupee."

    body = """The Reserve Bank of India has rolled out a scheme so generous that Indian banks are stumbling over each other to market it to the diaspora. And for the 37 million Indians living abroad, the math has never been this good.

Here is the deal: the RBI is absorbing the full cost of hedging foreign currency non-resident deposits — known as FCNR(B) deposits — with maturities of three to five years. That means NRIs can park their dollars in an Indian bank, earn domestic interest rates of 6% to 7%, and not worry about the rupee depreciating against the dollar before their money comes back. The central bank is picking up the tab on the currency risk.

## Why This Matters Now

The scheme, announced at the RBI's June 5 monetary policy meeting, is a direct response to the rupee's worst stretch in years. The Indian currency slumped to a record low of 96.96 per dollar last month as surging oil prices from the Iran war and rising global bond yields hammered emerging-market currencies. The RBI burned through $8.9 billion in net dollar sales in April alone, and India's foreign exchange reserves dropped to a one-year low of $671.6 billion.

The diaspora is being called in as a financial lifeline. India has turned to its overseas population in moments of currency stress before — most famously in 1998 and 2013 — and the playbook is being dusted off again.

## The Numbers Are Staggering

Analysts are projecting enormous inflows. Nomura estimates the scheme could attract $55 billion in deposits, with the bulk expected in August and September. Axis Bank is even more bullish, pegging the potential at $100 billion. Macquarie analysts calculate that with leverage — the RBI now allows domestic banks to extend dollar loans against these deposits — returns for NRIs could approach 12%. Axis Bank's estimates show returns could rise to 15% at higher leverage levels.

Indian banks have responded with urgency. South Indian Bank is eyeing $1 billion in fresh FCNR deposits by September, leveraging its deep NRI customer base in Kerala and the Gulf. The bank has raised its highest rate on dollar deposits above $500,000 to 7% across multiple maturity buckets.

Larger lenders are even more aggressive. Certificates of deposit rates have plunged by 60 basis points in three weeks as the promise of FCNR inflows eases funding pressure. State Bank of India and HDFC Bank — the giants with the biggest overseas branch networks — are seen as the primary beneficiaries.

## What NRIs Need to Know

The scheme runs until September 30, 2026. Deposits must be for a minimum of three years, and there is a one-year lock-in period with penalties for early withdrawal. The RBI's hedging subsidy applies to the principal amount, not the interest.

Banks have also been cleared to issue standby letters of credit against these deposits, allowing NRIs to borrow against their holdings through the bank's overseas branches or through India's tax-neutral financial hub, GIFT City in Gujarat. This leverage mechanism is what turns a 7% deposit into a potential 12–15% return — though it comes with its own risks.

The critical detail: the RBI has temporarily exempted these fresh deposits from statutory reserve requirements, meaning banks can deploy more of the money rather than parking a portion with the central bank. That makes the deposits even more attractive for lenders, which is why rates have jumped from around 3% to 7% almost overnight.

## The Bigger Picture

RBI Governor Sanjay Malhotra has signalled that interest rate hikes remain off the table for now, telling ET Now it is "premature to discuss rate hikes" because inflation has not become broad-based. That means the rupee's defence rests heavily on attracting capital inflows rather than raising rates — and the diaspora deposit scheme is the centrepiece of that strategy.

The rupee has already stabilised somewhat, closing at 94.68 per dollar. Brent crude has retreated to its lowest since late February as stranded oil tankers begin moving out of the Strait of Hormuz. But the monsoon deficit — running 43% below normal — and the still-fragile Iran peace process mean the rupee's troubles may not be over.

For NRIs weighing the decision, the window is narrow and the terms are historically favourable. Banks are competing hard for your dollars. The question is whether the risk-free 7% is genuinely risk-free when the scheme has an expiry date, and whether the rupee will hold the line long enough for the inflows to matter.

*Sources: Reuters, The Hindu BusinessLine, Outlook Money, Reserve Bank of India*"""

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "diaspora_angle": "NRIs can earn 6-7% risk-free on dollar deposits as India's central bank absorbs currency hedging costs — a rare moment when the diaspora's savings are being actively courted to rescue the rupee.",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"},
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com"},
            {"name": "Reserve Bank of India", "url": "https://www.rbi.org.in"}
        ]),
        "published_at": datetime.now(timezone.utc).isoformat(),
    }

    return insert_article(article)


# ════════════════════════════════════════════════════════════════════
# ARTICLE 2: Ireland Coach Steps Down After Historic India Whitewash
# ════════════════════════════════════════════════════════════════════
def write_article_2():
    print("\n═══ Article 2: Ireland Coach Malan Steps Down ═══")

    # Image: Try Heinrich Malan or Ireland cricket
    image_url = None
    image_caption = ""
    image_attribution = ""

    # Try Wikipedia for Heinrich Malan
    img = fetch_wikipedia_person_image("Heinrich Malan cricket coach")
    if img and verify_image(img):
        image_url = img
        image_caption = "Heinrich Malan, the outgoing Ireland head coach"
        image_attribution = "Wikimedia Commons"

    if not image_url:
        # Try Lorcan Tucker (Ireland captain who led the series win)
        img = fetch_wikipedia_person_image("Lorcan Tucker")
        if img and verify_image(img):
            image_url = img
            image_caption = "Ireland captain Lorcan Tucker led his side to a historic 2-0 series win over India in Belfast"
            image_attribution = "Wikimedia Commons"

    if not image_url:
        # Try Commons for Ireland cricket
        commons = fetch_wikimedia_commons("Ireland cricket team")
        for c in commons:
            if commons_relevance_ok(c["title"], "Ireland cricket", "cricket team"):
                if verify_image(c["url"]):
                    image_url = c["url"]
                    image_caption = "The Ireland cricket team"
                    image_attribution = "Wikimedia Commons"
                    break

    if not image_url:
        # Try Commons for Stormont cricket ground Belfast
        commons = fetch_wikimedia_commons("Stormont Belfast cricket")
        for c in commons:
            if commons_relevance_ok(c["title"], "Stormont Belfast cricket ground", "cricket"):
                if verify_image(c["url"]):
                    image_url = c["url"]
                    image_caption = "The Civil Service Cricket Club at Stormont, Belfast, where Ireland made history"
                    image_attribution = "Wikimedia Commons"
                    break

    if not image_url:
        # Fallback: try Shreyas Iyer since he's mentioned prominently
        img = fetch_wikipedia_person_image("Shreyas Iyer")
        if img and verify_image(img):
            image_url = img
            image_caption = "Shreyas Iyer's debut series as India's T20 captain ended in a historic 2-0 defeat to Ireland"
            image_attribution = "Wikimedia Commons"

    if not image_url:
        print("  ✗ No valid image found")
        return False

    slug = "ireland-coach-heinrich-malan-steps-down-india-t20-whitewash-gary-wilson-20260629"
    headline = "He Made Ireland Beat India Twice in Three Days. Then He Quit."
    subheadline = "Heinrich Malan is stepping down as Ireland's head coach on the back of cricket's biggest upset of the year. Gary Wilson becomes the first Irish-born coach in over 30 years. India, meanwhile, is in 'disbelief.'"

    body = """Heinrich Malan woke up on Monday morning as the man who had just pulled off the most remarkable result in Irish cricket history. By lunchtime, he had resigned.

Cricket Ireland announced on Monday that the South African head coach will step down from his role after overseeing a 2-0 T20 International series whitewash of India — the double world champions, the top-ranked team in the format, and the side that had not lost a T20 series since 2023.

"He believes the timing is right in the cycle to step back following the just-concluded successful T20 series versus India," Cricket Ireland said in a statement.

## Leaving on Top

Malan, 45, was appointed in 2022 and transformed a team that had long been treated as cannon fodder in world cricket into genuine competitors. Under his watch, Ireland qualified for three consecutive T20 World Cups, secured their first three Test match victories, and beat England in a T20 World Cup group game.

But nothing in his tenure — or in Irish cricket's 170-year history — compared to what happened in Belfast over the past weekend.

In the first T20 on Friday, Ireland posted 182 as captain Lorcan Tucker scored a half-century and Gareth Delany made a quickfire 49. India, chasing, were bundled out for 148 — a 34-run humiliation. It was Ireland's first-ever victory over India in any format.

The second match on Sunday was tighter and more dramatic. Ireland managed 154 for 8, with Harry Tector marking his 100th T20I with a gritty 53. India's chase began catastrophically — both openers, Sanju Samson and Abhishek Sharma, were dismissed for first-ball ducks in the opening over from debutant Jai Moondra. Tilak Varma's fighting 55 dragged India close, but with eight runs needed from two balls, Harshit Rana was caught on the boundary trying to clear it for six. India finished on 153 for 9, losing by one run.

The result ended India's 16-series unbeaten streak in T20 cricket.

## 'Disbelief' in the Indian Camp

The fallout in the India camp was immediate. Assistant coach Ryan ten Doeschate described the mood as one of "disbelief."

"It's very hard to be critical of guys who have just won a World Cup," he told reporters after the second match. "We've been outdone or outsmarted by a team who just did the basics very well."

Ten Doeschate pointed to India's inability to adjust after coming off the flat pitches and short boundaries of the Indian Premier League. "We're probably too used to a tempo and style where you can hit sixes more freely," he said. "We're going to have to adapt and be a lot smarter about how we'd like to play."

The diagnosis is uncomfortable for India's cricket establishment. Under head coach Gautam Gambhir, the team's T20 selections have come under heavy criticism. Shreyas Iyer's debut series as captain was a disaster — he scored just 10 in the second match and his captaincy drew pointed questions. Fan reaction on social media was brutal: "Gambhir has been made to eat a humble pie for his selection disasters," one viral post read.

## An Irish-Born Coach Takes the Reins

Malan will be replaced by Gary Wilson, who represented Ireland 292 times as a player between 2005 and 2020. Wilson joined Ireland's coaching staff as assistant coach in 2022 and becomes the first Irish-born head coach in over 30 years, since John Wills in the early 1990s.

The appointment is significant. Irish cricket has long relied on South African, English, and other foreign coaches. Wilson's elevation signals that the programme is producing not just world-class cricketers but also coaching talent from within.

"It has been an absolute privilege to work with these players, staff and the wider Irish cricket community," Malan said. "On the field, we can look back with great pride."

Wilson's first assignment will be a one-day international series against Afghanistan in August, followed by World Cup qualifiers in early 2027.

## What Comes Next for India

India's next stop is England, where they face five T20Is and three ODIs starting Tuesday, July 1. Ten Doeschate acknowledged the conditions will be similar — "maybe slightly quicker wickets, maybe slightly less wind" — and that the team will need a fundamentally different approach.

For a side that lifted the T20 World Cup trophy just four months ago, the Ireland series was supposed to be a gentle warm-up. Instead, it has become a reckoning: a reminder that flat IPL pitches and home conditions are poor preparation for cricket abroad, and that the world's best cannot coast on reputation alone.

Ireland, missing five first-choice players, did not get that memo.

*Sources: Reuters, CricketCountry, CricFit, Cricket Addictor*"""

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "sports",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "diaspora_angle": "India's cricket humiliation in Belfast resonates deeply with the diaspora — many followed the IPL from abroad and now face ribbing from Irish and British colleagues as the team heads to England next.",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "CricketCountry", "url": "https://www.cricketcountry.com"},
            {"name": "CricFit", "url": "https://www.cricfit.com"},
            {"name": "Cricket Addictor", "url": "https://www.cricketaddictor.com"}
        ]),
        "published_at": datetime.now(timezone.utc).isoformat(),
    }

    return insert_article(article)


# ── main ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    results = []
    results.append(("RBI NRI Deposits", write_article_1()))
    results.append(("Ireland Coach", write_article_2()))

    print("\n═══ Summary ═══")
    for name, ok in results:
        print(f"  {'✓' if ok else '✗'} {name}")

    failures = [n for n, ok in results if not ok]
    if failures:
        print(f"\n⚠ Failed: {', '.join(failures)}")
        sys.exit(1)
    else:
        print("\n✓ All articles inserted successfully")
