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


# ─── Article 1: India-US trade deal "very close" — but hinges on a tariff edge ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: India-US trade deal very close, hinges on tariff edge")
    print("="*60)

    slug = "india-us-trade-deal-very-close-goyal-greer-tariff-advantage-july-24-deadline-bilateral-bta-20260626"
    headline = "India Says a Trade Deal With America Is 'Done.' It Just Won't Switch It On Until the Tariffs Favour India."
    subheadline = "After two days of talks with Washington's trade chief in New Delhi, Commerce Minister Piyush Goyal says the framework is agreed \u2014 but the pact stays in the drawer until the US guarantees India a lower tariff than Vietnam, Bangladesh and the rest. A July 24 deadline is now ticking against both sides."

    body = """India and the United States are, by their own account, closer to a trade agreement than they have been at any point in years \u2014 and yet the deal is not in force, and may not be for weeks. The gap between "agreed" and "in effect" is where the entire negotiation now lives, and it explains a week of carefully hedged statements out of New Delhi and Washington.

Commerce and Industry Minister Piyush Goyal, speaking in London on Thursday a day after wrapping up talks with US Trade Representative Jamieson Greer, said the two sides are "very close" to finalising a pact and that the broad framework has been settled. But he attached a condition that matters more than the optimism: the agreement will not be switched on until the United States guarantees India a clear tariff advantage over rival manufacturing economies. "The day that happens, the deal is on," Goyal said.

## The One Number That Decides Everything

The logic is blunt. "A free-trade agreement is basically about getting a comparative advantage over your competitors for market access," Goyal explained. India will not accept a deal that leaves its exporters paying the same tariff as Vietnam, Thailand, the Philippines, China, Malaysia, Bangladesh or Sri Lanka \u2014 the countries it competes with for American orders in textiles, electronics, engineering goods and pharmaceuticals. An initial understanding reached in February had set an 18 percent tariff on Indian goods in exchange for New Delhi lowering its own barriers and buying more American energy and farm produce. At the time, that rate undercut Bangladesh and Vietnam. The edge is the prize; the headline rate is secondary.

That framework was thrown into doubt when the US Supreme Court invalidated President Donald Trump's sweeping global tariffs, forcing Washington to rebuild the legal scaffolding for any country-specific rate. Goyal's repeated phrase \u2014 that the US must find "the appropriate tools and legal backing" to give India its competitive advantage \u2014 is a reference to exactly that problem. Until American negotiators can show India a durable, court-proof mechanism, India is unwilling to commit.

## A Deadline Concentrates Minds

Greer's June 22-24 visit to New Delhi \u2014 his first since the framework talks \u2014 produced what the Commerce Ministry called a "comprehensive review" of market access, digital trade, supply-chain resilience and non-tariff barriers, and "substantial progress," but no breakthrough and no date. Two unresolved Section 301 investigations into alleged Indian overcapacity and forced labour are still hanging over the table, and India is determined to shield sensitive sectors, above all agriculture and dairy, where political resistance at home is fierce.

What gives the talks urgency is the calendar. A temporary 10 percent US tariff regime on trading partners expires on July 24; without an interim arrangement, Indian exporters could face a sharper snapback. The momentum itself is recent: Trump and Prime Minister Narendra Modi met on the sidelines of the G7 summit in France on June 17 \u2014 their first meeting in more than a year \u2014 and agreed to push the deal forward, after a bruising stretch in which Washington imposed steep tariffs over India's Russian-oil purchases, leaned toward Pakistan, and US Navy action in the Gulf killed three Indian sailors. Trade has become the most tangible way to repair a strained relationship.

## Why It Matters for the Diaspora

For the Indian diaspora, a US-India trade deal is not an abstraction \u2014 it sits at the intersection of the two economies that most NRI families straddle. The United States was India's second-largest trading partner in 2025-26, with Indian exports of $87.3 billion against $52.9 billion of imports, and a hydrocarbon trade that has swelled to $14.4 billion. A pact that lowers friction would ripple through the Indian-American business community that runs much of that commerce \u2014 importers, distributors, IT-services firms and the diaspora-founded startups that move goods, software and capital across the corridor.

There is a human dimension too. A US official noted this week that more than 330,000 Indian students in American institutions contribute over $14 billion to the US economy and support more than 50,000 jobs \u2014 a reminder that the relationship the diaspora embodies is itself an argument for the deal. For NRIs watching from Edison or Sunnyvale or Houston, the message from New Delhi is that India is no longer negotiating from anxiety. It wants the agreement, but only on terms that make Indian goods more competitive than the neighbours' \u2014 and it is prepared to let the clock run to get them."""

    # Person hero: Piyush Goyal (Wikipedia first), fallback to Commons event/building
    img_url = fetch_wikipedia_person_image("Piyush Goyal")
    img_attribution = "Wikimedia Commons"
    img_caption = "Indian Commerce and Industry Minister Piyush Goyal, who says the India-US trade pact is agreed but awaits a tariff edge"
    if not img_url:
        cu, _ = pick_commons([
            "Piyush Goyal minister",
            "India United States trade meeting",
            "Ministry of Commerce and Industry India building",
        ], headline, "Piyush Goyal India US trade commerce minister")
        if cu:
            img_url = cu
            img_caption = "India's commerce ministry; New Delhi says a US trade deal is agreed but hinges on a tariff advantage"

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
            "Reuters \u2014 'India says very close to trade deal with US' (25 June 2026): Commerce Minister Piyush Goyal said in London on Thursday, a day after wrapping up talks with USTR Jamieson Greer, that India and the US are very close to finalising a trade deal; New Delhi pushing for a tariff lower than other Asian economies while Washington wants India to import more American goods; the two sides discussed how Washington will find 'the appropriate tools and legal backing' to give India an advantage over competition; 'The day that happens, the deal is on,' Goyal said; February understanding included an 18% tariff on Indian goods in exchange for lower Indian barriers and more US purchases, lower than for Bangladesh/Vietnam at the time, but the deal was waylaid when the US Supreme Court invalidated Trump's sweeping global tariffs; USTR Section 301 probe into alleged overcapacity and forced labour has complicated talks.",
            "Outlook Business \u2014 'India-US Trade Deal Very Close, But Will Not Take Effect Without Tariff Advantage, Says Goyal': Goyal said the agreement has been finalised but will not come into force until India secures a clear tariff advantage over competing economies such as Vietnam, Thailand, the Philippines, China, Malaysia, Bangladesh and Sri Lanka; 'A FTA is basically about getting a comparative advantage over your competitors for market access'; 'Until that framework of getting that competitive advantage can be finalised, we can't put a US deal into force'; the US must find the appropriate legal tools to deliver that edge.",
            "Livemint \u2014 'Goyal, Greer review interim trade agreement as India-US race against tariff deadline': Goyal and Greer held a 'comprehensive review' of the proposed bilateral trade agreement (market access, digital trade, supply-chain resilience, non-tariff barriers, strategic-sector cooperation); Greer's June 22-24 visit comes as both race to finalise an interim arrangement before the July 24 expiry of a temporary 10% US tariff regime; statement cited 'substantial progress' but did not say outstanding issues were resolved; deal aims to be 'balanced and commercially meaningful.'",
            "The Hindu BusinessLine \u2014 'No breakthrough in India-US interim trade deal talks after Greer-Goyal meeting': two days of negotiations ended Wednesday without a breakthrough; both sides reported 'substantial progress' but gave no finalisation date; persistent uncertainty over the US tariff regime including two ongoing Section 301 investigations involving India, plus the need to safeguard sensitive sectors such as agriculture and unresolved market-access issues, required more time.",
            "Livemint / US official (Deputy Assistant Secretary of State Bethany Morrison) \u2014 background: the US was India's second-largest trading partner in 2025-26; Indian exports to the US grew 0.92% to $87.3 billion while imports rose 15.95% to $52.9 billion, with the trade surplus narrowing to $34.4 billion from $40.89 billion; US-India hydrocarbon trade reached $14.4 billion; more than 330,000 Indian students in US institutions contribute over $14 billion and support 50,000+ jobs; Modi-Trump met on the sidelines of the G7 summit in France on June 17, their first meeting in over a year, reviving momentum."
        ]),
        "diaspora_angle": "A US-India trade pact sits squarely on the corridor the diaspora lives on \u2014 the importers, IT-services firms, diaspora-founded startups and the 330,000-plus Indian students who move goods, software and capital between the two economies \u2014 so whether the deal switches on, and on what tariff terms, directly shapes the commercial world Indian-Americans operate in.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    return insert_article(article)


# ─── Article 2: Hyderabad's "Donald Trump Avenue" ───

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Hyderabad's Donald Trump Avenue")
    print("="*60)

    slug = "hyderabad-donald-trump-avenue-road-renamed-us-consulate-telangana-congress-bjp-hypocrisy-row-20260626"
    headline = "Hyderabad Just Named a Road After Donald Trump. The Backlash Came From an Unexpected Direction."
    subheadline = "A Congress-run state put the US President's name on a street beside the American consulate, in the heart of a financial district ringed by Microsoft, Google and Amazon. The sharpest objection came not from Trump's critics but from Narendra Modi's own party, which called it 'hypocrisy.'"

    body = """In the Financial District of Hyderabad \u2014 a stretch of glass towers that houses the Indian back-offices of Microsoft, Google and Amazon, and adjoins the United States consulate \u2014 a road quietly acquired a new name this week. As of Tuesday, it is Donald Trump Avenue. The renaming, modest in itself, has set off a political row that says more about India's domestic divisions than about the American president it honours.

The gesture came from the government of Telangana, the southern state whose capital is Hyderabad and which is ruled by the Congress party \u2014 the principal opposition to Prime Minister Narendra Modi's Bharatiya Janata Party (BJP) at the national level. Congress framed the move as a recognition of the city's "growing role" in the India-US partnership, part of a broader naming drive by Chief Minister A. Revanth Reddy that has also proposed a Google Street, a Microsoft Road, a Wipro Junction and a Ratan Tata Road to brand Hyderabad as a magnet for global capital.

## A Backlash From an Unexpected Quarter

The objections, when they came, did not follow the usual script. The loudest criticism arrived from the BJP \u2014 the party that has most assiduously cultivated Trump \u2014 which dismissed the honour as "hypocrisy." "Rahul Gandhi says President Trump is hurting Indian interests," BJP spokesperson Shehzad Poonawalla wrote on X. "Then why is his government in Telangana giving the ultimate tribute to him by renaming a road after him?" The Communist Party of India (Marxist) went further, calling the renaming "outrageous" and demanding it be withdrawn.

The discomfort is not hard to trace. US-India ties have deteriorated sharply during Trump's second term. Washington has slapped steep tariffs on Indian goods, penalised New Delhi for buying Russian oil, leaned conspicuously toward India's rival Pakistan, and \u2014 in the most painful episode \u2014 US Navy action in the Gulf during the Iran war killed three Indian sailors aboard commercial tankers. Congress has spent months accusing Modi of being "compromised" for not confronting Trump over these slights. That the same Congress should then bestow on Trump one of the city's most visible tributes is the contradiction the BJP pounced on. Trump, for his part, has never visited Hyderabad in either term, though Bill Clinton and George W. Bush both did.

## The Corridor the Diaspora Built

Strip away the partisan theatre and the choice of location is telling. The road sits at the physical centre of the US-India technology corridor \u2014 the cluster of American multinationals whose Indian engineering centres are staffed overwhelmingly by the kind of talent that also fills H-1B visas and Silicon Valley payrolls. Hyderabad has spent a decade positioning itself as that corridor's anchor, and the Trump, Google and Microsoft road names are an act of branding aimed at investors and the diaspora alike: a declaration that the city's fortunes are tied to the American relationship regardless of who occupies the White House.

The timing sharpens the irony. The renaming landed in the same week that Modi and Trump, fresh from their G7 meeting in France, were pushing to close a long-delayed trade deal, and as Indian-American advocacy groups descended on Capitol Hill to press for stronger bilateral ties. A gesture meant to celebrate the partnership instead exposed how raw the politics around it have become.

## Why It Matters for the Diaspora

For the Indian-American community \u2014 disproportionately concentrated in technology, and disproportionately connected to Hyderabad through family, employer and alma mater \u2014 the episode is a small but revealing window into how contested the US-India relationship has become inside India itself. Many in the diaspora have watched with unease as the warmth of the Modi-Trump "Howdy Modi" era curdled into tariffs, visa anxiety and the Gulf tanker deaths. A road named for Trump beside the consulate where they queue for visas is, depending on the viewer, either a confident bet on an enduring partnership or a tone-deaf tribute to a president many blame for the strain. That two of India's major parties cannot agree which it is tells the diaspora something important: support for the American alliance is no longer a settled, cross-party consensus back home, but a live political fault line \u2014 and the corridor cities the diaspora calls a second home are now part of the argument."""

    # Hero: Commons photo of Hyderabad financial district / HITEC City; person fallback Trump
    topic = "Hyderabad Financial District HITEC City skyline buildings Telangana"
    img_url, _ = pick_commons([
        "Hyderabad Financial District",
        "HITEC City Hyderabad",
        "Hyderabad Cyberabad skyline buildings",
        "Hyderabad cityscape Telangana",
    ], headline, topic)
    img_attribution = "Wikimedia Commons"
    img_caption = "Hyderabad's Financial District, home to US tech offices and the consulate, where a road was renamed Donald Trump Avenue"
    if not img_url:
        tu = fetch_wikipedia_person_image("Donald Trump")
        if tu:
            img_url = tu
            img_caption = "US President Donald Trump, after whom a road beside the US consulate in Hyderabad was named"
    if not img_url:
        px = fetch_pexels_image("modern city office towers skyline financial district")
        if px:
            img_url = px; img_attribution = "Pexels"
            img_caption = "A modern financial district; Hyderabad renamed a road in its tech hub Donald Trump Avenue"

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
            "Reuters \u2014 'Indian tech hub names road for Trump, drawing criticism from Modi's party' (24 June 2026): A key road named after US President Donald Trump in Hyderabad has drawn criticism from the BJP, which dismissed it as 'hypocrisy'; the road in Telangana's capital, ruled by the opposition Congress, adjoins the US consulate and is near offices of Microsoft, Google and Amazon; it received the name Donald Trump Avenue on Tuesday, at a time when Congress accuses Modi of being 'compromised' for not taking on Trump over tariffs and US attacks on Indian-crewed tankers during the Iran war; BJP spokesperson Shehzad Poonawalla wrote on X: 'Rahul Gandhi says President Trump is hurting Indian interests. Then why is his government in Telangana giving the ultimate tribute to him by renaming a road after him?'; CPI(M) called the move 'outrageous' and demanded withdrawal; Congress says it shows Hyderabad's 'growing role' in the partnership; Trump has never visited Hyderabad, though Clinton and George W. Bush did; Trump and Modi met on the sidelines of the G7 summit in France and agreed to push forward the trade deal.",
            "The Hindu BusinessLine \u2014 'Hyderabad names a road after Donald Trump, faces backlash from the BJP' (24 June 2026): Donald Trump Avenue adjoins Hyderabad's US consulate; offices of Microsoft, Google and Amazon are nearby; Congress said the change shows the city's growing role in India-US ties; a BJP official called the decision hypocrisy; US-India ties have deteriorated during Trump's second term with high tariffs, punishment over Russian-oil purchases, and closeness to Pakistan.",
            "The Hindu BusinessLine \u2014 'Naming spree in Hyderabad: A Trump Avenue, Google Street and Microsoft Road' (7 Dec 2025): The Telangana government announced plans to name landmarks after Donald Trump and Ratan Tata, plus a Google Street, Microsoft Road and Wipro Junction; the road along the US Consulate General would be 'Donald Trump Avenue'; the state said it would write to the MEA and US Embassy; CM A. Revanth Reddy had proposed naming roads after global corporations while addressing the US-India Strategic Partnership Forum (USISPF) conclave in New Delhi.",
            "Livemint \u2014 'Donald Trump Avenue in Hyderabad? Telangana to unveil road named after US President on June 23': The inauguration of Donald Trump Avenue was scheduled for June 23, moving the road-naming project from announcement to implementation; part of CM Revanth Reddy's plan to rename streets after world leaders and global corporations to position Telangana as an innovation hub."
        ]),
        "diaspora_angle": "The road sits at the centre of the US-India tech corridor the diaspora is built on \u2014 the Microsoft/Google/Amazon engineering hub in Hyderabad that feeds H-1B and Silicon Valley talent \u2014 and the cross-party fight over honouring Trump shows Indian-Americans that backing the American alliance is no longer a settled consensus back home but a live political fault line.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    return insert_article(article)


if __name__ == "__main__":
    print("Videshi News Writer \u2014 2026-06-26 20:30 UTC run")
    id1 = write_article_1()
    id2 = write_article_2()
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Article 1 (India-US trade deal hinges on tariff edge): {'OK id=' + str(id1) if id1 else 'FAILED'}")
    print(f"Article 2 (Hyderabad Donald Trump Avenue row): {'OK id=' + str(id2) if id2 else 'FAILED'}")
