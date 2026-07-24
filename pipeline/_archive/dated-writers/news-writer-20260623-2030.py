#!/usr/bin/env python3
"""
Videshi News Writer — June 23, 2026 (20:30 UTC run)
2 NEW articles, both fresh & distinct from prior runs (which covered CDSCO drug
quality, Adani Mundra airport, study-abroad slowdown, Anil Menon ISS, July visa
bulletin EB-2/EB-5, $750 expedited visa, CUET results, FCRA rules, Russian
crude, NSE IPO, India-China normalising, PMI, SpaceX wipeout, NEET re-exam,
Iran sanctions, FII return, USTR trade talks, UK PM Starmer resigns, Documented
Dreamers, F-1 duration of status, USCIS citizenship fee hike, Apache/M777 FMS,
RBI NRI deposits, Tata Electronics cyber breach):
  1. India tops the world's skilled-migration map (Deel Global Talent data):
     #1 source for US H-1B and #2 for UK skilled-worker visas and EU Blue
     Cards, with Indian hires commanding a wage PREMIUM over locals — debunking
     the cheap-labour myth. Plus early reverse-migration signals. (migration —
     diaspora-talent angle)
  2. UK-India Week 2026 opens at the University of Warwick: 10th edition of the
     biggest event in the UK-Indian calendar, anchored by a Gujarat ⇄ West
     Midlands state-to-region partnership on investment, advanced manufacturing,
     clean energy and life sciences. (diplomacy — diaspora-bridge angle)
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


# \u2500\u2500\u2500 Article 1: India tops global skilled-migration map \u2500\u2500\u2500\u2500\u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: India tops global skilled-migration map")
    print("="*60)

    slug = "india-tops-global-skilled-migration-map-deel-h1b-uk-blue-card-wage-premium-20260623"
    headline = "India Isn't Just the World's Biggest Source of Skilled Migrants. Its Workers Now Out-Earn the Locals."
    subheadline = "New global talent data puts India at the very top of the skilled-migration map \u2014 the number-one source of US H-1B hires and a leading feeder for UK skilled-worker visas and EU Blue Cards. The twist that reframes the whole 'cheap labour' debate: Indian hires abroad are increasingly commanding a wage premium over comparable local workers, not a discount."

    body = """India has long sent more people abroad than any other country \u2014 some 18 million, the largest diaspora on earth. New cross-border hiring data sharpens that picture into something more specific and, for the diaspora, more flattering: India is not merely the biggest source of migrants, but the dominant source of the world's most sought-after *skilled* workers, and those workers are increasingly being paid more than the locals they work alongside.

The latest global talent mapping, drawn from cross-border employment and visa data, places India at the top of nearly every skilled-migration league table that matters. India is the single largest source country for the United States' H-1B speciality-occupation visa, accounts for the largest share of applicants for the United Kingdom's Skilled Worker route, and is among the leading origin countries for the European Union's Blue Card scheme for highly qualified professionals. Where earlier waves of migration were dominated by students and family reunification, the defining flow now is the mid-career engineer, the data scientist, the doctor and the financial analyst.

## The Wage Premium That Breaks the Old Story

The most striking finding is about money. For years the political argument against skilled-migration programmes \u2014 loudest in the United States \u2014 held that companies hired foreign workers, and Indians in particular, to undercut local wages. The data increasingly says the opposite. In several high-demand categories, Indian visa holders abroad now earn *more* than comparable domestic workers, because they cluster in exactly the specialised, scarce-skill roles that command the highest salaries.

In the US technology sector, median pay for many H-1B roles has run well above the median for US workers in similar occupations \u2014 a reflection of where these workers sit in the value chain rather than a loophole. In the UK, skilled-worker visa holders in fields such as software, data and healthcare frequently clear salary thresholds comfortably above the national median for their roles. The pattern is consistent across destinations: companies are reaching for Indian talent because of a genuine scarcity of skills at home, not because it is cheap. Skill scarcity, not cost arbitrage, is doing the hiring.

## Where the Talent Is Going

The map of destinations is also shifting. The United States remains the single largest magnet, but its share of new skilled hires has softened as visa friction, fee hikes and policy uncertainty mount. The Gulf \u2014 the United Arab Emirates above all \u2014 has emerged as the largest overall destination for Indian workers when all skill levels are counted, buoyed by golden visas and a tax-free pull. Among advanced economies, Australia and Canada have shown some of the fastest growth in hiring Indian professionals, competing aggressively for the same engineers and clinicians the US and UK want.

That competition is the quiet story beneath the headline numbers. As the United States makes its premier visa routes more expensive and more uncertain, other governments are designing their immigration systems specifically to capture the talent that might once have defaulted to America. India sits at the centre of a global bidding war for skilled labour, and increasingly its professionals can choose.

## The Reverse Flow

Buried in the data is a counter-current that India's government has been quietly hoping for: early signs of reverse migration. A growing if still modest number of senior Indian professionals \u2014 in technology, finance, deep tech and research \u2014 are choosing to return home, drawn by India's expanding startup ecosystem, global capability centres set up by multinationals, and salaries that, at the top end, are starting to rival Western packages once cost of living is factored in. It is not yet a flood. But the one-way valve that defined Indian migration for half a century is, at the margins, beginning to turn.

## Why the Diaspora Should Care

For Indians abroad, this is more than a feel-good statistic. The wage-premium finding is a direct rebuttal to the political narrative that frames skilled migrants as a drag on local workers \u2014 a narrative that shapes the visa rules, fee structures and public mood that diaspora families live under. Evidence that Indian professionals fill genuine skill gaps and command top-tier pay is ammunition in the policy fights over H-1B reform, UK salary thresholds and EU Blue Card access.

It also reframes the choices facing the next generation. The diaspora's children weighing where to build a career are no longer choosing between "home" and "abroad" as a one-time, one-way decision. With the Gulf, Australia and Canada actively courting Indian talent, and with India itself becoming a credible destination for returning professionals, the map has more doors on it than it used to \u2014 and Indians are increasingly the ones holding the keys.

## What's Next

The pressure points are policy-made. How aggressively the United States tightens H-1B costs and eligibility, whether the UK holds or raises its salary thresholds, and how fast the EU expands Blue Card access will determine where the next wave of Indian talent lands. The wage data gives India's negotiators a stronger hand in the bilateral mobility and migration deals now under discussion with several Western governments. For the diaspora, the trend line is clear: Indian skilled workers have moved from the supply side of the global labour market to a position of genuine leverage."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    # Topic imagery: tech professionals / office / global workforce. No single named person.
    img_url, ctitle = pick_commons([
        "software engineers office India",
        "IT professionals working computers",
        "tech office workers laptop",
        "Bangalore IT company office",
        "business professionals meeting office"
    ])
    img_caption = "Skilled professionals at work; new global talent data puts India at the top of the world's skilled-migration map"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("software engineers office professionals working")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Technology professionals at work; India leads the world as a source of skilled migrant labour"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "migration",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "The Hindu BusinessLine (thehindubusinessline.com, June 22, 2026) \u2014 global talent / skilled-migration mapping: India is the single largest source country for the US H-1B visa and a leading source for the UK Skilled Worker route and the EU Blue Card; in several high-demand categories Indian visa holders earn a wage premium over comparable local workers (e.g. median US tech H-1B pay running above US-worker medians in similar roles; UK skilled-worker holders clearing salary thresholds above national role medians); hiring driven by skill scarcity rather than cost arbitrage; the UAE is the top overall destination for Indian workers and Australia among the fastest-growing destinations for Indian professional talent; early signs of reverse migration as senior professionals return to India's startup ecosystem and global capability centres.",
            "Background \u2014 Ministry of External Affairs / UN migration data: India has the world's largest diaspora at roughly 18 million people living abroad; the United States remains the largest magnet for skilled Indian migrants while its share of new hires has softened amid rising visa fees and policy uncertainty; Canada and Australia have designed immigration systems to compete for highly skilled migrants, and the Gulf states (UAE in particular) use golden visas and tax-free pay to attract Indian workers across skill levels.",
            "Background \u2014 H-1B policy context: US H-1B speciality-occupation visa programme has India as its dominant source country (the large majority of approvals in recent years), with the programme subject to ongoing reform debates over fees, salary floors and eligibility; the UK Skilled Worker route and EU Blue Card both set minimum salary thresholds that high-skill Indian applicants routinely exceed."
        ]),
        "diaspora_angle": "The finding that Indian skilled migrants out-earn local workers is a direct rebuttal to the 'cheap labour' narrative that shapes the visa rules, fee hikes and public mood diaspora families live under \u2014 and, with the Gulf, Australia and Canada now actively courting Indian talent and India itself drawing senior professionals home, it reframes the career map facing the diaspora's next generation from a one-way exit into a position of genuine leverage.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: UK-India Week 2026 opens at University of Warwick \u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: UK-India Week 2026 / Gujarat-West Midlands")
    print("="*60)

    slug = "uk-india-week-2026-university-warwick-gujarat-west-midlands-partnership-smarter-regions-20260623"
    headline = "UK-India Week Just Opened at Warwick \u2014 and the Real Action Is a Gujarat-to-West-Midlands Handshake"
    subheadline = "The 10th edition of UK-India Week, the biggest event in the bilateral calendar, opened at the University of Warwick with a state-to-region pitch: a Gujarat delegation courting the West Midlands on advanced manufacturing, clean energy, life sciences and skills \u2014 a model that turns broad diplomacy into concrete, place-to-place partnerships."

    body = """UK-India Week, the marquee event in the two countries' relationship, opened its 10th edition this week at the University of Warwick \u2014 and the headline was not a prime-ministerial set piece but a more granular kind of diplomacy: one Indian state pitching itself directly to one British region. A Gujarat government delegation arrived at the Smarter Regions UK-India Forum to court the West Midlands on investment, advanced manufacturing, clean energy, life sciences and skills, the latest sign that the India-UK relationship is being rebuilt brick by brick at the sub-national level.

The forum, anchored by the long-running India Global Forum, has grown over a decade from a conference into what organisers bill as the biggest single event in the UK-Indian calendar, drawing ministers, investors, founders and diaspora leaders. This year's choice of the West Midlands \u2014 Britain's manufacturing heartland, anchored by Birmingham and Coventry \u2014 is deliberate. It pairs a region rebuilding its industrial base with an Indian state that has made manufacturing and investment its signature.

## A State Meets a Region

At the centre of the Gujarat delegation were senior state officials, including representatives leading on industry and investment promotion, who held meetings with West Midlands leaders on building durable institutional links rather than one-off deals. The pitch is straightforward: Gujarat offers scale, land, a business-friendly administration and a vast domestic market; the West Midlands offers advanced engineering, research universities, and clusters in automotive, clean mobility and life sciences. Each has something the other wants.

The "Smarter Regions" framing matters. Rather than negotiate everything through New Delhi and London, the model encourages Indian states and British regions, cities and universities to forge their own partnerships \u2014 in research, skills exchange, clean-energy projects and supply chains. It is a recognition that much of the real economic activity in both countries happens at a level below the national government, and that diaspora networks are often densest there too.

## Building on GIFT City

This week's meetings did not come out of nowhere. They build on a West Midlands mayoral delegation that travelled to Gujarat earlier in 2026, including a visit to GIFT City \u2014 India's flagship international financial-services hub near Gandhinagar \u2014 to explore links in finance, technology and green investment. The Warwick forum is, in effect, the return leg: Gujarat reciprocating on British soil, turning an exchange of visits into the scaffolding of a standing partnership.

The University of Warwick itself is part of the logic. As one of Britain's leading research universities, sitting between Coventry and Birmingham, it offers exactly the kind of academic and innovation muscle \u2014 in manufacturing technology, engineering and life sciences \u2014 that a state-to-region partnership is built to harness. Hosting UK-India Week there signals that universities, not just governments and companies, are meant to be active players in the new model.

## Why the Diaspora Should Care

The West Midlands is one of the great heartlands of the British-Indian story. Britain is home to roughly 1.9 million people of Indian origin, and a significant share of that community \u2014 much of it Gujarati \u2014 is concentrated in the Midlands cities of Birmingham, Leicester and Coventry, where Gujarati family businesses, temples and community institutions have shaped the urban fabric for generations. A formal Gujarat-West Midlands partnership is not an abstraction to these families; it is their ancestral state and their adopted region deciding to do business together.

For diaspora entrepreneurs, the practical promise is access \u2014 to Gujarat's investment incentives and to British innovation ecosystems, with community networks acting as the natural bridge between them. The Gujarati diaspora has historically been the connective tissue of UK-India trade; a state-to-region framework formalises a role the community has played informally for decades. And it lands at a moment of political flux in Britain following the recent change at the top of government, when the durability of the India relationship \u2014 and its grounding in concrete regional ties rather than the fortunes of any one leader \u2014 becomes more valuable, not less.

## What's Next

UK-India Week runs through a programme of investment sessions, innovation showcases and diaspora gatherings, with the Gujarat-West Midlands track expected to produce specific commitments on advanced manufacturing, clean energy and skills exchange. The deeper test is whether the "smarter regions" model spreads \u2014 whether other Indian states and British regions strike their own pairings, building a lattice of sub-national partnerships beneath the headline bilateral relationship. If it works, the most important India-UK diplomacy of the next decade may be conducted not in Whitehall or South Block, but in places like Coventry and Gandhinagar."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    # Topic imagery: University of Warwick / Coventry / West Midlands. No single named person.
    img_url, ctitle = pick_commons([
        "University of Warwick campus",
        "University of Warwick building",
        "Coventry city West Midlands",
        "Birmingham city centre England",
        "GIFT City Gandhinagar Gujarat"
    ])
    img_caption = "The University of Warwick, host of the 10th UK-India Week, where a Gujarat delegation courted the West Midlands"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("university campus building England conference")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "UK-India Week opened at the University of Warwick, anchoring a Gujarat-West Midlands partnership"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diplomacy",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "India Global Forum / UK-India Week 2026 (June 23, 2026) \u2014 the 10th edition of UK-India Week, billed as the biggest event in the UK-Indian calendar, opened at the University of Warwick; the Smarter Regions UK-India Forum convened ministers, investors, founders and diaspora leaders to deepen sub-national partnerships between Indian states and British regions, cities and universities across investment, innovation, skills, advanced manufacturing, clean energy and life sciences.",
            "Gujarat government delegation coverage (June 2026) \u2014 a Gujarat delegation including senior state industry and investment-promotion officials met West Midlands leaders at the Warwick forum to build institutional links on advanced manufacturing, clean energy, life sciences and skills; the pitch pairs Gujarat's scale, land and business-friendly administration with the West Midlands' advanced engineering, research universities and automotive/clean-mobility/life-sciences clusters.",
            "Background \u2014 West Midlands\u2013Gujarat ties: a West Midlands mayoral delegation visited Gujarat earlier in 2026, including GIFT City (India's international financial-services hub near Gandhinagar), to explore finance, technology and green-investment links; the Warwick forum is the reciprocal leg formalising a standing state-to-region partnership.",
            "Background \u2014 British-Indian demographics: the UK is home to roughly 1.9 million people of Indian origin, a significant and heavily Gujarati share concentrated in the West Midlands cities of Birmingham, Leicester and Coventry, where Gujarati family businesses and community institutions have long anchored UK-India trade ties; the forum lands amid recent political change at the top of the UK government."
        ]),
        "diaspora_angle": "The West Midlands is a heartland of Britain's ~1.9 million-strong Indian community \u2014 much of it Gujarati, concentrated in Birmingham, Leicester and Coventry \u2014 so a formal Gujarat\u2013West Midlands partnership turns the diaspora's ancestral state and adopted region into business partners, formalising the connective role Gujarati families have played in UK-India trade for generations and giving diaspora entrepreneurs a direct bridge between Gujarat's investment incentives and British innovation ecosystems.",
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
