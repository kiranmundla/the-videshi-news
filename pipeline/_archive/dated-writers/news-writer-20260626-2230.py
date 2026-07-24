#!/usr/bin/env python3
"""
Videshi News Writer — June 26, 2026 (13:30 PDT / 20:30 UTC run)
2 NEW articles, dedup-checked against last 3 days of `news` category.

  1. India-US trade deal "very close" but won't take effect without a tariff
     EDGE over rivals — Goyal after the Greer visit (June 22-24). DISTINCT
     from the India-UK FTA piece (different country) and from the earlier
     FCNR/GIFT-City diaspora-capital pieces. This is the BTA / interim-deal
     race against the July 24 tariff-snapback deadline.
  2. Hyderabad renames a Financial-District road "Donald Trump Avenue"
     beside the US Consulate — Congress-ruled Telangana's gesture, the BJP
     calling it "hypocrisy," CPI(M) calling it "outrageous." A domestic
     political flashpoint over the diaspora-heavy US-India tech corridor.
     NOT previously covered.
"""
import os, json, requests, urllib.parse, subprocess, io, re
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

_COMMONS_STOP = {
    "the","a","an","of","in","on","at","to","for","and","or","with","as","by","from","is",
    "are","was","were","be","new","says","after","over","amid","how","why","what","2024",
    "2025","2026","india","indian","us","usa","american","uk","first","more","than",
    "people","man","woman","group","day","year","top","big","set","get","make","makes",
    "made","you","your","they","them","this","that","social","media","using","use","just",
    "here","need","know","quietly","almost","like","could","into","now","its","rare",
    "still","won","four","losing","grip","door","park","earn","deal","take","effect",
    "without","road","avenue","named","name","city","ties","tech","hub",
}

def _keywords(text):
    out = []
    for t in re.findall(r"[A-Za-z][A-Za-z'-]+", text or ""):
        tl = t.lower()
        if len(tl) >= 4 and tl not in _COMMONS_STOP:
            out.append(tl)
    return out

def commons_relevance_ok(commons_title, headline, topic=""):
    title_l = (commons_title or "").lower()
    if not title_l:
        return False
    kws = set(_keywords(headline)) | set(_keywords(topic))
    if not kws:
        return True
    return any(kw in title_l for kw in kws)

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=12)
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia API error for '{person_name}': {e}")
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
            pages = r.json().get("query", {}).get("pages", {})
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
            if results:
                print(f"  \u2713 Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Commons error: {e}")
    return []

def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape",
            headers={"Authorization": PEXELS_KEY, "User-Agent": UA}, timeout=10)
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  \u2713 Pexels image for '{query}'")
                return url
    except Exception as e:
        print(f"  \u26a0 Pexels error: {e}")
    return None

def download_and_compress(url, slug):
    try:
        r_content = None
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
            if r.status_code == 200 and len(r.content) >= 5000:
                r_content = r.content
        except Exception:
            pass
        if r_content is None:
            tmp = f"/tmp/{slug}_src"
            subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, url], timeout=40, check=True)
            with open(tmp, "rb") as f:
                r_content = f.read()
            if len(r_content) < 5000:
                print(f"  \u26a0 Image too small after curl fallback")
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
            print(f"  \u26a0 Compressed too small")
            return None
        print(f"  \u2713 Compressed: {len(r_content)} \u2192 {len(compressed)} bytes")

        filename = f"{slug}.jpg"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        requests.delete(upload_url, headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY})
        resp = requests.post(upload_url, data=compressed, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY,
            "Content-Type": "image/jpeg", "x-upsert": "true"}, timeout=30)
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded: {public_url[:80]}...")
            return public_url
        print(f"  \u26a0 Upload failed ({resp.status_code}): {resp.text[:200]}")
        return None
    except Exception as e:
        print(f"  \u26a0 Download/compress error: {e}")
        return None

def pick_commons(queries, headline, topic="", min_width=800):
    for q in queries:
        commons = fetch_wikimedia_commons_images(q)
        commons = [c for c in commons if commons_relevance_ok(c.get("title", ""), headline, topic)]
        if commons:
            pick = None
            for c in commons:
                if c["width"] >= min_width and c["original_url"].lower().endswith((".jpg", ".jpeg")):
                    pick = c
                    break
            pick = pick or commons[0]
            print(f"  \u2713 Commons pick: {pick.get('title','')}")
            return pick["url"], pick.get("title", "")
    return None, ""

def insert_article(article):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  \u2713 Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
    return None


# ─── Article: US strikes Iran after Hormuz cargo-ship drone attack ───

def write_article_hormuz():
    print("\n" + "="*60)
    print("ARTICLE: US strikes Iran after Hormuz drone attack on ship")
    print("="*60)

    slug = "us-strikes-iran-hormuz-cargo-ship-drone-attack-ceasefire-violation-indian-seafarers-oil-20260626"
    headline = "America Just Bombed Iran Again. The Trigger Was a Drone Hitting a Ship in the World's Most Important Oil Lane."
    subheadline = "Nine days after a ceasefire, the US struck Iranian missile, drone and radar sites in retaliation for an attack on a cargo vessel crossing the Strait of Hormuz \u2014 the chokepoint where thousands of Indian sailors work and through which a fifth of the world's oil flows. A UN evacuation of stranded crews is on hold."

    body = """The fragile peace between Washington and Tehran cracked on Friday evening. The US military launched air strikes on Iran \u2014 hitting missile and drone storage sites and coastal radar installations near the Strait of Hormuz \u2014 in what US Central Command called a "powerful response" to an Iranian drone attack on a commercial ship transiting the strait a day earlier. It was the first American strike on Iran since the two countries agreed a ceasefire on June 14, and it threw the survival of that nine-day-old deal into question.

The chain of events moved fast. On Thursday, a cargo vessel \u2014 identified in reports as the Taiwanese-operated, Singapore-flagged M/V Ever Lovely \u2014 was struck while crossing the Strait of Hormuz. Two US officials said Iran fired at least four one-way attack drones at ships in the waterway; one drone hit the upper deck of the ship, which was damaged but able to continue. "Obviously, this is a foolish violation of our Ceasefire Agreement," President Donald Trump wrote on Truth Social. Asked whether Iran would face consequences, he told reporters only, "You'll find out." Hours later, the warplanes flew.

## A Calibrated Blow, Not a New War

US officials framed the strike as deliberately limited. "The unwarranted aggression against commercial shipping by Iranian forces clearly violated the ceasefire," CENTCOM said, adding that Iran's behaviour "undermined freedom of navigation." But a US official told CNN the strikes did not signal a return to major combat operations, at least for now. Vice President JD Vance, who has led negotiations with Tehran, put it bluntly on X: "Iran signed a ceasefire agreement. We have honored it... But violence will be met with violence." Iranian media said a projectile struck near a pier in Sirik, on the strait's northern shore.

Iran, for its part, is not backing down. On Friday it reasserted its right to control shipping through Hormuz and warned Gulf states against siding with Washington. Its Revolutionary Guards had earlier declared that safe passage would be possible only along routes Iran designates, and that it would act against vessels that failed to comply. The standoff leaves the world's single most important oil chokepoint \u2014 through which roughly a fifth of global oil and liquefied natural gas passed before the conflict \u2014 once again a live flashpoint.

## The Indians Caught in the Middle

For India, this is not a distant quarrel. Thousands of Indian seafarers crew the commercial vessels that thread the Strait of Hormuz, and New Delhi has made clear they are its first concern. After an earlier strike on the tanker MT Settebello, India lodged a strong protest with Washington and summoned the US Charg\u00e9 d'Affaires, Jason Meeks; Additional Secretary (Americas) Nagaraj Naidu conveyed India's worry about the safety of its citizens at sea. "We conveyed that the welfare of our seafaring community is very important, and the attacks that are happening must stop," Ministry of External Affairs spokesperson Randhir Jaiswal said.

The danger to crews is acute. A UN-led effort to shepherd hundreds of stranded ships and roughly 2,500 seafarers out of the Gulf was paused on Thursday after the attack on the Ever Lovely; IMO Secretary-General Arsenio Dominguez said about 115 vessels had made it through before the halt and that completing the evacuation could take weeks. Many of those waiting crews are Indian.

## Why It Matters for the Diaspora

Beyond the sailors, the strait is India's economic artery. India imports more than 80 percent of its crude oil, and a large share of it \u2014 along with the LPG that fuels millions of Indian kitchens \u2014 moves through Hormuz. Benchmark oil prices jumped more than 2 percent after Thursday's attack before sliding again on Friday as tankers kept moving; the after-hours confirmation of the US strike nudged crude back up. For the diaspora in the Gulf \u2014 the millions of Indians living and working in the UAE, Qatar, Saudi Arabia and Oman, who send home a huge slice of India's remittances \u2014 instability in these waters is personal, threatening both the regional economies that employ them and the flights and shipping lanes that connect them to home. A "limited" strike may calm markets for a day. Whether it calms the strait is the question now hanging over every Indian household with someone working the Gulf."""

    # Hero: Commons photo of Strait of Hormuz / oil tanker / Gulf shipping
    topic = "Strait of Hormuz oil tanker ship Persian Gulf navigation"
    img_url, _ = pick_commons([
        "Strait of Hormuz",
        "oil tanker Persian Gulf",
        "crude oil tanker ship sea",
        "container ship Gulf",
    ], headline, topic)
    img_attribution = "Wikimedia Commons"
    img_caption = "A tanker in the Strait of Hormuz, the oil chokepoint where the US struck Iran after a drone hit a cargo ship"
    if not img_url:
        px = fetch_pexels_image("oil tanker cargo ship at sea")
        if px:
            img_url = px; img_attribution = "Pexels"
            img_caption = "An oil tanker at sea; the US struck Iran over an attack on a ship in the Strait of Hormuz"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

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
            "Reuters \u2014 'US strikes Iran following attack on cargo ship in Strait of Hormuz' (26 June 2026): The US military attacked Iran on Friday in response to an Iranian drone strike on a cargo ship in the Strait of Hormuz, throwing the fate of the interim peace deal into question; US Central Command said aircraft struck missile and drone storage locations and coastal radar sites; Iranian media said a projectile struck an area around a pier in Sirik, a city on the shores of the strategic waterway; separately, Israel and Lebanon signed an agreement framed as an initial step toward Hezbollah disarming and Israel withdrawing from Lebanon.",
            "CNN \u2014 'US strikes Iranian targets in response to attack on cargo ship' (26 June 2026): CENTCOM said US aircraft struck Iranian missile and drone storage locations and coastal radar sites; 'The unwarranted aggression against commercial shipping by Iranian forces clearly violated the ceasefire'; a US official said the strikes do not reflect a return to major combat operations for now; Trump on Truth Social said Iran shot at least four one-way attack drones at ships transiting the strait, one hitting the upper deck of a large cargo ship which was damaged but able to proceed, and called it 'a foolish violation of our Ceasefire Agreement'; asked about consequences he told reporters, 'You'll find out.'",
            "New York Post \u2014 'US military strikes Iran \u2014 in payback for unwarranted drone attack on cargo ship' (26 June 2026): Iranian drone storage facilities and coastal radar sites were hit by US warplanes in retaliation for the Thursday attack on the M/V Ever Lovely, a Singapore-flagged cargo ship; VP JD Vance wrote on X, 'Iran signed a ceasefire agreement. We have honored it... But violence will be met with violence'; the resumption of operations comes nine days after Trump and Iran's President Masoud Pezeshkian signed a memorandum of understanding to end fighting and begin 60 days of talks.",
            "The Indian Eye \u2014 'Strait of Hormuz Crisis Poses New Test for India-US Ties': MEA spokesperson Randhir Jaiswal said the welfare of Indian seafarers remained a matter of paramount concern; after the attack on MT Settebello, India lodged a strong protest and summoned US Charge d'Affaires Jason Meeks, with Additional Secretary (Americas) Nagaraj Naidu conveying India's concerns; 'We conveyed that the welfare of our seafaring community is very important, and the attacks that are happening must stop'; thousands of Indian seafarers work on ships passing through the strait.",
            "Reuters \u2014 'UN agency working to restart Hormuz evacuations after ship attack' (26 June 2026): The UN's IMO 'temporarily paused' its evacuation initiative after a container ship operated by Taiwan's Evergreen was attacked; about 115 vessels and around 2,500 seafarers were able to sail through before evacuations were paused, IMO Secretary-General Arsenio Dominguez said, adding the evacuation could take weeks; Tehran on Friday reasserted its right to control shipping in the waterway and warned Gulf neighbours against siding with Washington.",
            "Reuters / MarketWatch \u2014 oil reaction (25-26 June 2026): Benchmark oil prices rose about 2% after Thursday's attack near Oman, which prompted the UN to suspend its voluntary evacuation scheme; before the conflict the strait handled about a fifth of the world's daily oil and LNG supplies; crude fell more than 3% on Friday on easing supply concerns as Saudi Arabia resumed Gulf loadings, but moved back up in after-hours trade once the US confirmed the retaliatory strike."
        ]),
        "diaspora_angle": "The Strait of Hormuz is where thousands of Indian seafarers work and through which most of India's imported crude and cooking gas flows, so a US strike on Iran there directly threatens Indian crews stranded at sea, the oil-import bill behind India's fuel prices, and the millions of Gulf-based NRIs whose livelihoods and remittances depend on a stable region.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    return insert_article(article)


if __name__ == "__main__":
    print("Videshi News Writer \u2014 2026-06-26 22:30 UTC run")
    idh = write_article_hormuz()
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Article (US strikes Iran / Hormuz / Indian seafarers): {'OK id=' + str(idh) if idh else 'FAILED'}")
