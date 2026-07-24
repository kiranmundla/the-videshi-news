#!/usr/bin/env python3
"""
Videshi News Writer — 2026-06-15 PM3 batch (scheduled videshi-writer-news, 14:30 UTC run)
3 fresh articles (distinct from all earlier 2026-06-15 batches):
  1. GIFT City emerges as NRI investment magnet — FFIF, family offices, diversification (economy/finance)
  2. UK overhauls immigration rulebook for Indians; CETA mobility route opens (immigration)
  3. 16 India-bound fertiliser ships stranded in Strait of Hormuz threaten summer sowing (economy/food-security)
"""

import json, os, subprocess, re, time, datetime, urllib.parse, requests

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                key = key.strip().replace('export ', '')
                val = val.strip().strip('"').strip("'")
                os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}


def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10)
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=8):
    params = {
        "action": "query", "generator": "search", "gsrsearch": search_query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers=UA, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                width = ii.get("width", 0)
                if url and "image" in mime and width > 300:
                    results.append({"url": url, "title": page.get("title", ""),
                                    "width": width, "height": ii.get("height", 0)})
            print(f"  \u2713 Wikimedia Commons: {len(results)} results for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        print("  \u26a0 No Pexels API key")
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5&orientation=landscape"],
            capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
        for photo in data.get("photos", []):
            url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
            if url:
                print(f"  \u2713 Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  \u26a0 Pexels error: {e}")
    return None


def validate_image(url):
    try:
        r = requests.get(url, timeout=12, stream=True, allow_redirects=True, headers=UA)
        ct = r.headers.get("Content-Type", "")
        chunk = r.raw.read(12000)
        if r.status_code == 200 and "image" in ct and len(chunk) > 5000:
            print(f"  \u2713 Image validated: {r.status_code}, {ct}, {len(chunk)}+ bytes")
            return True
        print(f"  \u2717 Image validation failed: {r.status_code}, {ct}, {len(chunk)} bytes")
    except Exception as e:
        print(f"  \u2717 Image validation error: {e}")
    return False


def pick_commons_image(query, keywords, caption):
    for img in fetch_wikimedia_commons_images(query, 8):
        tl = img["title"].lower()
        if any(kw in tl for kw in keywords) and validate_image(img["url"]):
            return img["url"], caption, "Wikimedia Commons"
    return None, "", ""


def insert_article(article):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=20)
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  \u2713 Inserted: {result[0].get('slug', 'unknown')}")
            return True
        print("  \u2713 Inserted (no body returned)")
        return True
    print(f"  \u2717 Insert failed: {r.status_code} \u2014 {r.text[:300]}")
    return False


def finalize(article, image_url, image_caption, image_attribution):
    if image_url:
        article["image_url"] = image_url
        article["image_caption"] = image_caption
        article["image_attribution"] = image_attribution
    else:
        print("  \u26a0 No valid image found \u2014 inserting without image")
    return insert_article(article)


# ========================================================================
# ARTICLE 1: GIFT City NRI investment magnet
# ========================================================================
def write_article_1():
    print("\n" + "=" * 60)
    print("ARTICLE 1: GIFT City NRI investment magnet")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "GIFT City Gandhinagar", ["gift", "gandhinagar", "gujarat", "tower", "city"],
        "GIFT City near Gandhinagar, India's first International Financial Services Centre")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "GIFT City Gujarat skyscraper", ["gift", "gujarat", "skyscraper", "building", "tower"],
            "The skyline of GIFT City, India's emerging international finance hub in Gujarat")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "financial district skyscraper India", ["financial", "district", "tower", "building", "india", "skyline"],
            "A financial district; GIFT City is positioning itself as a gateway for India-linked global capital")
    if not image_url:
        px = fetch_pexels_image("modern financial district skyscrapers")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "A modern financial district", "Pexels"

    slug = "gift-city-ifsc-nri-investment-magnet-family-offices-2026-20260615"

    body = """For decades, the wealthy Indian diaspora has parked its offshore money in Dubai, Singapore and London. In 2026, a stretch of gleaming towers between Ahmedabad and Gandhinagar is making a serious bid to win some of it back \u2014 not by replacing those hubs, but by giving Non-Resident Indians a India-linked base that finally speaks their language.

GIFT City, India's first International Financial Services Centre (IFSC), has crossed the line from policy experiment to functioning financial hub. Built to bring global finance closer to India, it offers international banking, fund management, fintech and offshore capital markets under a single progressive regulator \u2014 the International Financial Services Centres Authority (IFSCA). For NRIs weighing where to structure their wealth, the pitch is increasingly hard to ignore.

## What Changed in 2026

Two developments this year have moved GIFT City from "promising" to "credible." In April 2026, the IFSCA approved the first Foreign Family Investment Fund (FFIF) under its 2025 regulations \u2014 a milestone that validates GIFT City as a viable jurisdiction for family offices, alternative investment funds, cross-border estate planning and global wealth structures. For diaspora families who have spent years routing succession planning through Singapore or the Gulf, it opens the door to building India-linked wealth structures within a framework that is globally oriented yet domestically aligned.

The second is a wave of institutional confidence from established centres. In May 2026, Singapore's High Commissioner to India, Simon Wong, highlighted rising Singaporean investment in Gujarat, including GIFT City, and pointed to its emergence as a hub for USD-INR bond issuance, international banking and fintech. When a financial centre as mature as Singapore starts feeding capital into a rival, the market notices.

## The Tax and Cost Case

The structural appeal is straightforward. GIFT City entities enjoy a suite of incentives unavailable in mainland India: exemptions on securities transaction tax (STT), specific capital gains benefits, tax holidays and other concessions for IFSC entities. Compliance is more streamlined than India's traditional regulatory systems, and operating costs sit well below those of Dubai or Singapore, making it an efficient base for long-term structures.

For an NRI, that translates into something concrete: the ability to run an offshore fund, a family office or a cross-border investment vehicle that is plugged directly into the Indian growth story, without the friction and tax drag of doing it onshore \u2014 and at a fraction of the cost of doing it from a legacy hub.

## Geopolitics Is Doing the Marketing

The timing is not accidental. Months of conflict in the Middle East have made diaspora investors acutely aware of regional concentration risk. Dubai retains powerful structural advantages, but periods of instability have reinforced an old lesson: diversification across jurisdictions matters. Increasingly, NRIs are not choosing between Dubai and GIFT City \u2014 they are building multi-hub structures that combine Dubai, Singapore and GIFT City to spread geographic and regulatory exposure.

"As someone based in Ahmedabad-Gandhinagar, I have seen the pace at which GIFT City is evolving," said Malav Deliwala, Head of Legal at the Adani Group. "While infrastructure and investor confidence are steadily growing, investment decisions should be driven by long-term vision rather than short-term speculation."

## The Honest Caveats

GIFT City is rising, but it is still building. Liquidity across IFSC exchanges is improving but trails established global markets. The ecosystem of banks, asset managers and insurers is expanding but remains shallow compared with Singapore. Real estate inside GIFT City offers modern infrastructure and attractive entry points, but returns are tied to how quickly the broader ecosystem scales \u2014 a long-term play, not a quick yield.

The practical verdict from wealth advisers is measured: treat GIFT City as a complementary layer within a broader global portfolio, not a replacement for mature hubs. It occupies a unique middle ground \u2014 developed enough to be credible, yet early enough to offer meaningful upside.

## Why It Matters to the Diaspora

For NRIs, GIFT City represents something the diaspora has wanted for a generation: a way to invest in India's rise without surrendering the legal clarity, tax efficiency and global connectivity they enjoy abroad. Every regulatory milestone \u2014 the FFIF approval, the doubling of diaspora investment limits under the Portfolio Investment Scheme, the simplification of NRI real estate transactions \u2014 chips away at the friction that once pushed overseas Indian capital toward foreign hubs.

The asymmetry, as advisers frame it, is simple. Entering today means navigating a developing ecosystem but gaining early positioning. Waiting may bring maturity, but at the cost of relative advantage. For diaspora investors who have long looked for a credible India-linked alternative to Dubai and Singapore, the question is no longer whether GIFT City is perfect. It is whether to participate while it is still being built.

**Sources:** Bar & Bench (HSA Advocates analysis), International Financial Services Centres Authority, Mint / Budget 2026 coverage"""

    article = {
        "headline": "Dubai and Singapore Have Long Held NRI Money. GIFT City Is Now Making a Serious Bid to Bring It Home.",
        "subheadline": "With the first Foreign Family Investment Fund approved and Singaporean capital flowing in, India's IFSC at GIFT City is positioning itself as a tax-efficient, India-linked base for diaspora wealth.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "GIFT City offers NRIs a tax-efficient, India-linked base for family offices, offshore funds and succession planning \u2014 letting the diaspora invest in India's growth without the friction of onshore structures or the geopolitical concentration risk of a single foreign hub.",
        "sources": ["Bar & Bench (HSA Advocates)", "International Financial Services Centres Authority (IFSCA)", "Mint / Budget 2026 coverage"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 2: UK immigration overhaul + CETA mobility
# ========================================================================
def write_article_2():
    print("\n" + "=" * 60)
    print("ARTICLE 2: UK immigration overhaul + CETA mobility")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "UK Home Office building London", ["home office", "london", "building", "marsham", "whitehall"],
        "The UK Home Office in London, which is rolling out a sweeping overhaul of immigration rules")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "London Westminster Parliament", ["westminster", "parliament", "london", "thames", "big ben"],
            "Westminster, London; the UK is reshaping visa and settlement rules that affect Indian migrants")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Heathrow Airport terminal UK border", ["heathrow", "airport", "terminal", "border", "uk"],
            "A UK airport border; new visa and travel rules are reshaping migration from India")
    if not image_url:
        px = fetch_pexels_image("london westminster parliament thames")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "Westminster, London", "Pexels"

    slug = "uk-overhauls-immigration-rules-indians-ceta-mobility-route-2026-20260615"

    body = """Indians are the single largest group of migrants to the United Kingdom \u2014 the largest source of work visas, one of the largest sources of students, and the community most exposed to every twist in British immigration policy. This year, that policy is being rewritten almost line by line, and the changes land squarely on Indian families planning to study, work or settle in Britain.

The overhaul flows from the UK government's 2025 immigration white paper, and it is being rolled out in stages through 2028. Some measures tighten the door. One, tied to the long-awaited India-UK trade deal, swings a new one open. For the diaspora, the net effect is a moving target that demands close attention.

## The Door That Is Opening

The most consequential development for Indians is buried in the implementation of the Comprehensive Economic and Trade Agreement (CETA), the free trade deal India and the UK signed in July 2025. Once CETA enters into force, the UK will expand its Global Business Mobility \u2013 Service Supplier route to allow Indian nationals \u2014 including self-employed individuals \u2014 delivering contracted services covered by the agreement to come to the UK for up to 12 months.

Paired with the deal's Double Contributions Convention, which spares temporary Indian workers from paying social security in both countries, it is one of the most significant mobility wins India has secured in any trade agreement. The catch: CETA is not yet fully operational. Both governments must complete domestic ratification and exchange notifications before any mobility provision takes effect, a process that officials have said could stretch into 2026 and beyond.

## The Doors That Are Closing \u2014 or Narrowing

Against that single opening sits a longer list of restrictions, several already in force:

- **Tougher English requirements.** Since January 8, 2026, new applicants for Skilled Worker, Scale-up and High Potential Individual visas must demonstrate B2-level English, a notably higher bar than the previous B1 standard.
- **A shrinking Skilled Worker list.** An initial cut to the list of jobs eligible for sponsorship took effect in July 2025, and overseas recruitment of social care workers \u2014 a route many Indians used \u2014 ended the same month.
- **Higher charges.** The immigration skills charge rose in December 2025, raising the cost of sponsoring overseas workers.
- **Stricter student compliance.** New compliance rules for universities sponsoring international students took effect on June 1, 2026.

Looking ahead, the squeeze intensifies. From January 1, 2027, the Graduate visa \u2014 the post-study work route that has been a major draw for Indian students \u2014 will last just 18 months instead of two years (though PhD holders keep 36 months). From March 26, 2027, a higher standard of English will be required for indefinite leave to remain. And from August 2028, an international student levy of \u00a3925 per student per year of study will take effect, a cost universities are widely expected to pass on to applicants.

## A Pathway for Talent

The picture is not uniformly restrictive. From July 1, 2026, the UK will add a dedicated design-industry pathway to its Global Talent route and simplify fast-track endorsements for PhD-level academics and researchers at approved institutions \u2014 a quiet signal that Britain still wants high-end Indian talent even as it tightens the broader system. German and other European envoys have been courting the same pool of skilled Indians displaced by US H-1B turbulence, and the UK is wary of losing the race.

## Why It Matters to the Diaspora

For Indian families, the stakes are immediate and financial. A student weighing a UK degree must now factor in a shorter post-study work window, a looming per-year levy and stricter university compliance that could disrupt enrolment. A skilled worker faces a higher English bar and steeper sponsorship costs. A professional or entrepreneur, by contrast, may soon find a genuinely new route into Britain through CETA \u2014 if and when ratification completes.

The throughline is that the UK is reshaping who it lets in and on what terms, and Indians sit at the centre of nearly every category affected. The practical advice from immigration advisers is consistent: lock in plans under current rules where possible, watch the CETA ratification timeline closely, and budget for a system that is getting more expensive and more selective by the year.

**Sources:** House of Commons Library, UK Home Office / GOV.UK, Morgan Lewis immigration analysis"""

    article = {
        "headline": "Britain Is Rewriting Its Immigration Rulebook. For Indians \u2014 Its Biggest Migrant Group \u2014 One Door Opens as Several Narrow.",
        "subheadline": "A CETA trade-deal route could let Indian professionals work in the UK for up to a year, even as tougher English tests, a shorter graduate visa and a new student levy raise the cost of British migration.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "Indians are the UK's largest migrant group \u2014 the biggest source of work visas and among the largest of students \u2014 so every shift in British visa, settlement and trade-deal mobility rules directly reshapes the plans of diaspora families studying, working or settling in Britain.",
        "sources": ["House of Commons Library", "UK Home Office / GOV.UK", "Morgan Lewis"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 3: Fertiliser ships stranded in Hormuz
# ========================================================================
def write_article_3():
    print("\n" + "=" * 60)
    print("ARTICLE 3: Fertiliser ships stranded in Hormuz")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "bulk carrier cargo ship fertiliser", ["bulk", "carrier", "cargo", "ship", "vessel", "freighter"],
        "A bulk cargo carrier; 16 India-bound ships loaded with fertiliser are stranded in the Strait of Hormuz")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Strait of Hormuz cargo ship", ["hormuz", "strait", "ship", "cargo", "vessel"],
            "The Strait of Hormuz, where India-bound fertiliser cargoes are stuck amid the Gulf conflict")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "farmer field India agriculture sowing", ["farmer", "field", "agriculture", "india", "crop", "paddy"],
            "An Indian farmer in a field; the fertiliser shortfall threatens the summer sowing season")
    if not image_url:
        px = fetch_pexels_image("cargo ship bulk carrier ocean")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "A bulk cargo carrier at sea", "Pexels"

    slug = "india-fertiliser-ships-stranded-strait-hormuz-summer-sowing-season-20260615"

    body = """The Gulf conflict that has killed Indian sailors and rattled oil markets is now reaching into something far closer to the Indian household: the fields that feed the country. Sixteen India-bound ships carrying fertiliser are stranded in the Strait of Hormuz, the government confirmed on Monday, raising the spectre of a supply crunch just as farmers prepare to sow the all-important summer crop.

Bandana Preyashi, a joint secretary in the fertilisers ministry, laid out the stranded cargo at a press conference: eight ships carrying 330,000 metric tons of urea, four loaded with 257,000 tons of di-ammonium phosphate (DAP), one vessel carrying ammonia, and three ships with 110,000 tons of sulphur. All of it is sitting in the world's most contested shipping chokepoint, unable to move.

## Why Fertiliser Is the Quiet Crisis

For a country where agriculture still employs nearly half the workforce, fertiliser is not a commodity \u2014 it is a lever on food prices, rural incomes and political stability. The kharif (summer) sowing season, which begins with the monsoon, is the single largest cropping window of the year, and it runs on a reliable, well-timed supply of urea, DAP and other nutrients. A shortfall at the wrong moment can dent yields, push up food inflation and ripple through the rural economy for months.

India is heavily dependent on imports for these inputs, and a significant share of that supply moves through the Gulf and the Strait of Hormuz \u2014 the same waters where Iran's months-long disruption of shipping has left cargoes stuck and insurers nervous.

## The Government's Reassurance

Officials are working to project calm. India has already imported five million tons of crop nutrients, including urea, this season, while boosting domestic output, Preyashi said. To plug the gap, the government has floated a global tender to import 1.7 million tons of urea. The nation is expected to consume 38.39 million tons of fertilisers during the current harvest season.

"At present, we see no major challenge to the availability of fertilisers in the current sowing season," Preyashi said \u2014 a statement designed to head off panic-buying and hoarding as much as to describe the underlying reality.

The reassurance lands against a fragile backdrop. The US and Iran announced over the weekend that they had reached an initial agreement to end their war and reopen the Strait of Hormuz, with traffic reportedly beginning to resume. But clearing the waterway of mines and restoring normal shipping could take weeks, and the durability of any deal remains unproven. For fertiliser cargoes on a seasonal clock, weeks matter.

## A Pattern of Spillover

The stranded fertiliser ships are the latest example of how a conflict India had no hand in starting keeps imposing costs on it. The same blockade has killed Indian seafarers, forced refiners to scramble for alternative crude from Latin America and Africa, and pushed New Delhi to suspend import taxes on petrochemicals used in pharmaceuticals. Now it is testing the supply chain that underpins the country's food security.

India has responded with a mix of stockpiling, diversification and diplomacy \u2014 importing nutrients ahead of need, floating fresh tenders, and pressing for the strait's reopening. Whether that proves enough depends on a variable entirely outside its control: how quickly the Gulf's most important waterway returns to normal.

## Why It Matters to the Diaspora

For the diaspora, the fertiliser crunch is a reminder that the Gulf conflict's reach extends well beyond oil prices and headlines. Many NRIs send money home to farming families, own agricultural land, or simply track the rural economy that shaped where they came from. A disrupted sowing season can mean higher food inflation for relatives in India, squeezed incomes in farming districts, and added pressure on the remittances that already cushion millions of households.

It also underscores a strategic vulnerability the diaspora has watched with unease: India's dependence on a single, conflict-prone waterway for the inputs that feed its people. The stranded ships may soon sail again. The question of how to insulate India's food supply from the next Gulf crisis will not move as quickly.

**Sources:** Reuters, India's Ministry of Chemicals and Fertilisers briefing, Press Trust of India"""

    article = {
        "headline": "The Gulf Crisis Just Reached India's Fields. Sixteen Fertiliser Ships Are Stranded in the Strait of Hormuz.",
        "subheadline": "With 330,000 tons of urea and 257,000 tons of DAP stuck in contested waters, New Delhi insists the summer sowing season is safe \u2014 even as it floats fresh import tenders to plug the gap.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "Many NRIs remit money to farming families, own agricultural land, or track India's rural economy \u2014 and a fertiliser shortfall at sowing time means higher food inflation, squeezed rural incomes and added pressure on the remittances that cushion millions of households back home.",
        "sources": ["Reuters", "Ministry of Chemicals and Fertilisers (India)", "Press Trust of India"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# MAIN
# ========================================================================
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"VIDESHI NEWS WRITER (PM3) \u2014 {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")

    results = []
    results.append(("GIFT City NRI magnet", write_article_1()))
    results.append(("UK immigration overhaul", write_article_2()))
    results.append(("Fertiliser ships stranded", write_article_3()))

    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    for name, success in results:
        print(f"  {'\u2713 SUCCESS' if success else '\u2717 FAILED'}: {name}")
    print(f"{'='*60}\n")
