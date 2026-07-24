#!/usr/bin/env python3
"""
Videshi News Writer — June 24, 2026 (10:30 UTC run)
2 NEW articles, distinct from all prior runs:
  1. Indian-American lawmakers (Krishnamoorthi, Subramanyam, Thanedar) urge the
     diaspora to run for office amid rising anti-Hindu / anti-India hate. Capitol
     Hill / FIIDS event. Diaspora civic-power story for 5.2M Indian-Americans.
  2. RBI clears banks to LEND to NRIs against their dollar (FCNR) deposits,
     including via GIFT City — the leverage piece that can push diaspora returns
     to ~12-15% and is the final missing link in the rupee-support deposit scheme.
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


# ─── Article 1: Indian-American lawmakers urge diaspora into politics ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Indian-American lawmakers urge diaspora into politics")
    print("="*60)

    slug = "indian-american-lawmakers-urge-diaspora-run-for-office-anti-india-hate-20260624"
    headline = "Their Lawmakers Have a Message for 5 Million Indian-Americans: Stop Being on the Menu, Get a Seat at the Table."
    subheadline = "At a Capitol Hill gathering, Congressmen Raja Krishnamoorthi, Suhas Subramanyam and Shri Thanedar urged Indian-Americans to run for office at every level as anti-Hindu and anti-India hate rises \u2014 a call for one of America's wealthiest and most-educated communities to convert economic clout into political power."

    body = """Indian-Americans are among the most educated and prosperous communities in the United States. Their elected representatives in Washington have decided that is no longer enough. At an event on Capitol Hill this week, a cluster of Indian-American lawmakers delivered a blunt message to the diaspora: the time for sitting on the sidelines of American politics is over.

"There is the rise of anti-Hindu, anti-Indian, anti-Desi hate," Congressman Raja Krishnamoorthi, a Democrat from Illinois, told the gathering, organised by the Foundation for India and Indian Diaspora Studies (FIIDS). "It's time to get more involved than you've ever been. You have to raise your voice. You have to speak up. You have to show up. You have to make sure that your voices are heard everywhere."

## 'On the Menu' or 'At the Table'

Krishnamoorthi's pitch was less about ideology than about presence. He urged community members to run for public office regardless of party. "I want you to think about running for office, whether it's city council. I don't care if you're a Republican, Democrat, or Independent," he said. "There's an old saying in Washington DC, if you don't have a seat at the table, you're on the menu. And none of you can afford to be on the menu, nor can our families, nor can our interests."

He ran down the ladder deliberately \u2014 city council, state house, state senate, the US Congress \u2014 a reminder that political power in America is built locally long before it reaches Washington. Congressman Suhas Subramanyam echoed the point, arguing that the most effective way to address the community's concerns is to have its own people inside the bodies that make decisions. Congressman Shri Thanedar warned that hate against immigrants more broadly is climbing, and urged the diaspora to stay united in confronting it.

## Why the Alarm, and Why Now

The lawmakers were not speaking in the abstract. Indian-American leaders and advocacy groups have spent recent years cataloguing a string of incidents: attacks and vandalism targeting Hindu temples, anti-Hindu graffiti, the disruption of religious events, and organised campaigns opposing Indian representation in corporate and civic life. The worry is that a community long content to excel quietly in medicine, technology and business has been slow to build the political defences that other established immigrant groups developed generations ago.

The numbers explain why both parties are paying attention. The Indian-American community was estimated at 5.2 million people as of 2023, according to the US Census Bureau, making it one of the fastest-growing and most influential ethnic groups in the country, with deepening footprints in business, academia and public service. That is a constituency with money, organisational capacity and \u2014 increasingly \u2014 its own bench of elected officials willing to recruit the next generation.

## A Bipartisan Audience

The event drew support from across the aisle, a sign that courting the diaspora has become a mainstream political calculation rather than a niche one. US Senator Roger Marshall, a Kansas Republican, used the platform to talk up the growing India-US partnership, arguing that a bilateral trade agreement would benefit both countries and, pointedly, farmers in his home state. Several Democratic lawmakers \u2014 among them Sanford Bishop, James Walkinshaw, Brad Sherman and Bill Huizenga \u2014 pledged support on the issues the community raises most often: immigration, and the years-long backlog for permanent residency that traps so many skilled Indian workers.

That overlap is the quiet strategic message of the gathering. Anti-India hate, the green-card backlog, temple security and trade are not partisan problems for this community; they are shared ones. The lawmakers' argument is that a diaspora with representatives in both parties, in statehouses as well as Congress, is far harder to ignore \u2014 or to put on the menu.

## What Comes Next

The harder question is whether exhortation translates into candidates. Running for office demands time, money and a tolerance for public scrutiny that many first-generation professionals have deliberately avoided. But the trajectory is unmistakable: a community that a generation ago counted its elected officials on one hand now has enough of them to hold a recruitment drive on Capitol Hill. The message from those already inside the room is that the next wave will have to come from the dinner tables, school boards and city councils of suburban America \u2014 or risk watching decisions about their families, faith and futures be made by people who do not answer to them.
"""

    # Hero: Wikipedia photo of Raja Krishnamoorthi (named, prominent person)
    img_url = fetch_wikipedia_person_image("Raja Krishnamoorthi")
    img_attribution = "Wikimedia Commons"
    img_caption = "Congressman Raja Krishnamoorthi, who urged Indian-Americans to run for office at every level"

    if not img_url:
        cu, _ = pick_commons(["Raja Krishnamoorthi", "United States Capitol building"])
        if cu:
            img_url = cu
            img_caption = "The US Capitol, where Indian-American lawmakers urged the diaspora to seek elected office"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "The Hindu BusinessLine (thehindubusinessline.com, June 24 2026) \u2014 'Indian-American lawmakers urge diaspora to enter politics amid rise in anti-India sentiment': at a Capitol Hill event organised by the Foundation for India and Indian Diaspora Studies (FIIDS), Congressman Raja Krishnamoorthi (D-Illinois) said 'There is the rise of anti-Hindu, anti-Indian, anti-Desi hate' and urged Indian-Americans to run for office at any level regardless of party ('if you don't have a seat at the table, you're on the menu'); Congressman Suhas Subramanyam said representation in decision-making bodies is the best way to address community concerns; Congressman Shri Thanedar said anti-immigrant hate is rising and urged unity; Senator Roger Marshall (R-Kansas) highlighted the India-US partnership and a bilateral trade deal; Democratic lawmakers Sanford Bishop, James Walkinshaw, Brad Sherman and Bill Huizenga pledged support on immigration and the green-card backlog; community estimated at 5.2 million per the US Census Bureau (2023).",
            "US Census Bureau / community estimates \u2014 the Indian-American population estimated at 5.2 million as of 2023, among the fastest-growing and most influential ethnic groups in the US with rising representation in business, academia and public service; advocacy groups have documented temple vandalism, anti-Hindu graffiti, disruptions of religious events and campaigns opposing Indian representation in corporate organisations."
        ]),
        "diaspora_angle": "This is a direct call to the 5.2-million-strong Indian-American community to convert its economic and educational success into political representation, framed by its own elected lawmakers as the only durable defence against rising anti-Hindu and anti-India hate and against stalled priorities like the green-card backlog.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: RBI lets banks lend to NRIs against dollar deposits ───

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: RBI clears banks to lend to NRIs against FX deposits")
    print("="*60)

    slug = "rbi-banks-lend-nris-against-dollar-fcnr-deposits-leverage-gift-city-rupee-20260624"
    headline = "India Will Now Let Its Banks Lend NRIs Money to Buy More Indian Deposits. The Returns Could Touch 15%."
    subheadline = "The Reserve Bank of India has cleared domestic lenders to extend loans to non-residents against their foreign-currency deposits \u2014 including through GIFT City \u2014 the final missing piece of a scheme designed to pull diaspora dollars in and prop up a weak rupee. Analysts say leverage could lift NRI returns toward 12-15 percent and draw in tens of billions."

    body = """India's central bank has quietly added the most powerful ingredient yet to its campaign to lure diaspora money home. In a notice issued on Tuesday, the Reserve Bank of India said domestic lenders may now extend loans to non-residents against their foreign-currency deposits, including through banks' offshore branches and units in the tax-neutral hub of GIFT City. In plain terms: an overseas Indian can now park dollars in an Indian bank, and then borrow against those very dollars to park even more \u2014 a leverage loop that sharply magnifies returns.

It is the last brick in a structure the RBI has been assembling for weeks. Earlier this month the central bank moved to subsidise hedging costs on three- to five-year foreign currency non-resident (FCNR) deposits, and banks responded by raising rates on those deposits to roughly 6 to 7 percent. What was missing was leverage. Indian banks had been openly lobbying for permission to lend against the deposits \u2014 a function that until now was largely the preserve of foreign banks. Tuesday's notice grants it.

## How the Math Works

The appeal to a non-resident Indian is straightforward arithmetic. An FCNR deposit lets overseas Indians earn relatively high Indian interest rates on dollars without taking on rupee currency risk. Stack borrowed money on top, and the returns climb fast. Macquarie analysts estimate that with leverage, returns could approach 12 percent; Axis Bank's calculations suggest that at higher levels of leverage, returns could rise toward 15 percent. For a diaspora investor comparing that against US deposit rates, the gap is hard to ignore.

The RBI has set guardrails. Banks can extend loans to non-residents from their overseas branches, including GIFT City, using the deposits as collateral; they can issue standby letters of credit against such deposits; and they can place a lien on the accounts. The central bank's swap facility will cover only the principal of the deposits, not the interest, and swaps are limited to tenors of under three years, available only to banks that have mobilised eligible foreign-exchange deposits for at least three years.

## Why India Wants the Money

The deeper purpose is to defend the rupee. When banks convert incoming diaspora dollars into rupees at the RBI, those inflows support a currency that has been under pressure through the months of the Iran conflict and the oil-price shock that followed. The scheme echoes a 2013 playbook, when India last leaned on its diaspora to steady the rupee during a balance-of-payments scare. The difference this time, Nomura noted, is that US dollar rates are far higher and the scheme adds leverage \u2014 a combination that should make it more attractive than the version a decade ago.

The estimates of how much could flow in are large and rising. Nomura puts the potential at about $55 billion, with the bulk expected in August and September. Axis Bank is more bullish still, seeing scope for around $100 billion. Macquarie pencils in $30 billion to $50 billion. Whatever the precise figure, it would represent one of the biggest single mobilisations of diaspora capital India has attempted.

## The Banks Cash In Too

Indian lenders stand to be major beneficiaries, which is why they pushed so hard for the rule. The inflows could revive deposit growth, which has lagged in recent years, while improving liquidity in the financial system and nudging market interest rates lower. Crucially, analysts at Ambit Capital note, these deposits are exempt from reserve requirements, making them an especially cheap and efficient source of funding. The market has already voted: the Nifty Bank index has risen sharply over the past month, outpacing the broader market, with large lenders that have a strong overseas presence \u2014 State Bank of India and HDFC Bank among them \u2014 seen as the biggest winners.

## What to Watch

For NRIs, the promise of double-digit returns comes with the usual caveats. Leverage amplifies losses as well as gains, and the eye-catching 12-to-15 percent figures assume aggressive borrowing that not every investor will want or qualify for. The scheme's window is also finite, tied to deposits mobilised through September. Still, the message from Mumbai is unmistakable: India is offering its diaspora a deal it has used only in moments of real need, and this time it has sweetened it with leverage. For the millions of overseas Indians weighing where to put their dollars, the next few months may be the most lucrative entry point in more than a decade.
"""

    # Hero: Wikimedia Commons photo of RBI building (institution, not a named person)
    img_url, _ = pick_commons([
        "Reserve Bank of India building Mumbai",
        "Reserve Bank of India headquarters",
        "GIFT City Gujarat"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "The Reserve Bank of India, which cleared banks to lend to NRIs against their foreign-currency deposits"

    if not img_url:
        px = fetch_pexels_image("Indian rupee currency notes finance")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Indian rupee notes; the RBI is using diaspora dollar deposits to support the currency"

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
            "Reuters (reuters.com, June 23 2026) \u2014 'India's RBI to allow domestic banks to extend loans against overseas FX deposits': per an RBI notice issued Tuesday, Indian banks may extend loans to non-residents against foreign-currency deposits from their overseas branches, including GIFT City units, using the deposits as collateral; banks may issue standby letters of credit against such deposits and place a lien on accounts; the RBI swap covers only the principal (not interest) and is limited to tenors under three years for deposits mobilised for at least three years; earlier this month the RBI offered to subsidise hedging costs on FCNR deposits; Nomura estimates the scheme could attract $55 billion, with the bulk in August-September.",
            "Reuters India File (reuters.com, June 23 2026) \u2014 'Rupee gets diaspora lifeline \u2014 banks cash in': FCNR deposits placed with Indian banks for three to five years let overseas Indians earn high domestic rates without currency risk; banks have raised rates to around 6-7%; with leverage, returns could approach 12% (Macquarie, which estimates $30-50bn inflows) and up to 15% at higher leverage (Axis Bank, which sees scope for ~$100bn); deposits are exempt from reserve requirements (Ambit Capital); the Nifty Bank index rose ~7.2% over the past month, with SBI and HDFC Bank seen as biggest beneficiaries.",
            "The Hindu BusinessLine (thehindubusinessline.com, June 23 2026) \u2014 'RBI permits domestic banks to extend credit against foreign currency deposits abroad': confirms the RBI notice and details, including subsidised hedging costs for FCNR deposits and analyst estimates of up to $55 billion in inflows over the coming months."
        ]),
        "diaspora_angle": "This is aimed squarely at non-resident Indians: the RBI is now letting banks lend NRIs money against their own dollar deposits, a leverage loop that analysts say could push diaspora returns toward 12-15 percent while channelling tens of billions of overseas-Indian dollars back home to steady the rupee.",
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
