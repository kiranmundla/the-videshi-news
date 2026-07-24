#!/usr/bin/env python3
"""
Videshi News Writer — 2026-06-17 02:30 UTC run (scheduled videshi-writer-news)
3 fresh articles, distinct from all 2026-06-15/16 published news topics (H-1B fee
ruling, trade deal tranche, domestic renewal pilot, Iran ceasefire, oil/markets rally,
Modi-Trump meet, Canada deportations, birth tourism, NRI deposit rates, ultra-rich
exodus, Modi-Slovakia, Rubio racism remarks, denaturalization, Bangladesh airport row,
GCC boom):
  1. India's May wholesale inflation surges to 9.68% on Middle East fuel shock;
     new 2022-23 base series — economy
  2. Indian student enrolment in the US falls 6.9% (sharpest drop in a decade) as
     visa denials hit a 10-year high — immigration/education
  3. International Day of Yoga 2026 (theme: Yoga for Healthy Ageing) lights up the
     US diaspora — Lincoln Memorial, Times Square, 2,500 global venues — diaspora
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
load_env(os.path.expanduser('~/workspace/.env.pexels'))

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


def wc(body):
    return len(re.sub(r'[#*>\n]', ' ', body).split())


def finalize(article, image_url, image_caption, image_attribution):
    if image_url:
        article["image_url"] = image_url
        article["image_caption"] = image_caption
        article["image_attribution"] = image_attribution
    else:
        print("  \u26a0 No valid image found \u2014 inserting without image")
    article["word_count"] = wc(article["body"])
    print(f"  word_count={article['word_count']}")
    return insert_article(article)


# ========================================================================
# ARTICLE 1: India's May WPI inflation surges to 9.68%
# ========================================================================
def write_article_1():
    print("\n" + "=" * 60)
    print("ARTICLE 1: India May WPI inflation 9.68%")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Reserve Bank of India building Mumbai",
        ["reserve bank", "rbi", "mint road"],
        "The Reserve Bank of India in Mumbai, which raised its inflation forecast to 5.1% for the year")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "petrol pump fuel station India price",
            ["petrol", "fuel", "pump", "petroleum", "diesel", "gas station"],
            "A fuel station in India; wholesale fuel and power prices jumped 30% year-on-year in May")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Indian rupee banknotes currency",
            ["rupee", "banknote", "currency", "indian money"],
            "Indian rupee banknotes; wholesale inflation hit a six-month high in May")
    if not image_url:
        px = fetch_pexels_image("indian rupee money inflation finance")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "Indian currency; wholesale inflation surged to a six-month high in May", "Pexels"

    slug = "india-may-wholesale-inflation-9-68-percent-middle-east-fuel-shock-new-base-series-20260617"

    body = """India's wholesale price inflation surged to 9.68 percent in May, its fastest pace in six months, as the energy shock from the now-easing Middle East war worked its way through the supply chain. The reading, released on June 15, came in well above the 9.05 to 9.1 percent that economists had expected and marked a sharp acceleration from 8.26 percent in April \u2014 a reminder that even as the guns fall silent in West Asia, the price of the conflict is still landing on Indian shelves.

The number is the first print from a modernised wholesale price series with a new base year of 2022-23, replacing the old 2011-12 benchmark. Under the revised methodology, the all-commodities index reached 109.9 in May from 108.8 the month before, and the item basket expands from 697 to 957 products. The government is also rolling out new Producer Price Indices, and has signalled that the wholesale series will eventually be phased out in favour of the PPI over the next five years.

## Fuel Did the Damage

The single biggest driver was energy. Wholesale fuel and power inflation jumped to 30.33 percent year-on-year in May from 24.89 percent in April, while petroleum and natural gas prices alone rocketed 61.51 percent. Crude oil had climbed roughly 27 percent since the U.S.-Israel war on Iran erupted in late February, prompting state-run oil marketing companies to raise retail fuel prices four separate times during May.

The pressure was broad-based beyond fuel. Manufactured-products inflation rose to 7.48 percent from 6.68 percent, primary articles to 4.99 percent from 3.78 percent, and the wholesale food index to 4.49 percent from 3.11 percent. In other words, the cost of nearly everything that moves through India's factories and mandis was rising faster in May than in April.

## The Retail-Wholesale Gap

For ordinary households, the more familiar number is retail inflation, which rose to 3.93 percent in May from 3.48 percent in April \u2014 still below the Reserve Bank of India's 4 percent target but climbing steadily. The gap between the two measures matters: wholesale inflation, which carries a heavier weighting of fuel, tends to lead retail prices, and economists expect the West Asia cost shock to show up more visibly in consumer prices over the coming months.

The Reserve Bank, which targets 4 percent retail inflation within a 2-to-6 percent band, held interest rates steady at its June meeting, choosing to watch for second-round effects before tightening. But it raised its inflation forecast for the current fiscal year to 5.1 percent from 4.6 percent, citing higher oil and the risk of a weak monsoon. Several economists now expect rate hikes to begin around October, with some warning inflation could approach 6 percent \u2014 the top of the tolerance band \u2014 by year-end.

## What People Actually Feel

The official numbers also understate the squeeze that households perceive. Reserve Bank survey data showed inflation expectations jumping sharply in May, with the current-rate perception rising 56 basis points \u2014 the highest since September 2022. Against headline retail inflation of 3.93 percent, the public's own estimate of current inflation stood near 7.76 percent, almost double. A Mint analysis of 358 items found 60 of them rising more than 6 percent in May, up from 40 in January, with edible oils, kerosene, firewood and coarse grains among the worst hit.

There is, however, a glimmer of relief on the horizon. The preliminary U.S.-Iran framework to end the war, halt the blockade and reopen the Strait of Hormuz sent global oil prices falling, and the rupee firmed to around 94.6 to the dollar, its strongest level in two weeks. Economists at ICRA expect the cooling in energy and commodity prices to ease the June wholesale print.

## Why It Matters to the Diaspora

For non-resident Indians, inflation at home is not an abstraction \u2014 it directly shapes the real value of the money they send back. India received a record-setting flow of remittances last year, and when domestic prices for essentials climb faster than headline figures suggest, each dollar wired to family stretches less far than it did a year ago. A firmer rupee partially offsets that, improving the exchange rate NRIs receive, but rising food and fuel costs erode the cushion.

The deeper signal is about the trajectory of the Indian economy the diaspora remains invested in, through deposits, property and equities. With the central bank flagging upside risks and a possible weak monsoon ahead, the months after a war meant to bring relief may still test household budgets \u2014 and the patience of a diaspora watching the numbers from afar.

**Sources:** Reuters, Ministry of Commerce & Industry (DPIIT), Mint"""

    article = {
        "headline": "India's Wholesale Inflation Just Hit a Six-Month High of 9.68%. The Middle East War Is Still on the Bill.",
        "subheadline": "May wholesale prices rose far faster than forecast as fuel and power inflation surged past 30 percent \u2014 even as an easing of the West Asia conflict promises relief and the RBI holds rates while lifting its inflation outlook to 5.1 percent.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "Inflation at home directly shapes the real value of the record remittances NRIs send back, and a wholesale print running at 9.68 percent \u2014 with essentials rising faster than headline figures suggest \u2014 means each dollar wired to family stretches less far, even as a firmer rupee and falling post-ceasefire oil prices offer a partial cushion.",
        "sources": ["Reuters", "Ministry of Commerce & Industry (DPIIT)", "Mint"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 2: Indian student enrolment in US falls 6.9%
# ========================================================================
def write_article_2():
    print("\n" + "=" * 60)
    print("ARTICLE 2: Indian student enrolment in US falls 6.9%")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "university graduation ceremony students United States",
        ["graduation", "commencement", "convocation", "graduates", "university"],
        "A U.S. university commencement; Indian student enrolment in the United States fell 6.9 percent in a year")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "university campus library United States students",
            ["campus", "library", "university", "college", "student"],
            "A U.S. university campus; the number of Indian students has dropped to its lowest in years")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "United States visa passport stamp",
            ["visa", "passport", "stamp", "consulate"],
            "A U.S. visa; consular denials of international student visas hit a decade high")
    if not image_url:
        px = fetch_pexels_image("university graduation students campus")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "University graduates; Indian student numbers in the US are falling sharply", "Pexels"

    slug = "indian-student-enrolment-us-falls-6-9-percent-visa-denials-decade-high-2026-20260617"

    body = """For two generations, a U.S. degree was the single most reliable on-ramp into the Indian-American story \u2014 the student visa that became an H-1B, the H-1B that became a green card, the green card that became a family. That pipeline is now narrowing at its mouth. The number of Indian students in the United States has fallen 6.9 percent in a single year, the sharpest annual drop in more than a decade, and the forces behind it suggest the decline may not be a one-off.

According to data from the U.S. Department of Homeland Security's SEVIS tracking system, shared with India's Parliament by the Ministry of External Affairs, the total number of Indian students across all programs fell from 378,787 in February 2025 to 352,644 in February 2026. The decline is broad-based \u2014 spanning school, vocational, undergraduate and postgraduate enrolments alike \u2014 and India, while still the largest source of international students in America, has watched its lead over second-ranked China narrow for the first time since 2019.

## A Wall of Visa Rejections

The proximate cause is not a loss of appetite for American education but a hardening of the door. A report from Shorelight Education found that the United States denied 35 percent of international student visa applications in 2025, the highest rejection rate in a decade. Visa wait times remain punishing in India: as of the State Department's February update, applicants faced delays of roughly two months in Kolkata and up to two and a half months in Mumbai and Hyderabad.

The squeeze is most visible at the graduate level, where international students make up a far larger share of enrolment. International graduate student enrolment fell 12 percent nationwide in the autumn of 2025. Law schools have been hit especially hard: LL.M. applications to Berkeley dropped 20 percent and to the University of Michigan 30 percent, while international enrolment in traditional three-year J.D. programs slid nearly 6 percent.

## The Visa-Fee Shadow

Looming over the numbers is the broader immigration climate \u2014 the proposed $100,000 H-1B fee fought over in the courts, a weighted lottery that favours high earners, and expanded consular vetting that now reaches applicants' social-media histories. For a prospective student weighing six figures in tuition, the calculation increasingly turns on a single question: will the degree actually lead to work in America, or to an expensive credential and a flight home?

That uncertainty is pushing students toward alternatives. Counsellors report rising interest in the United Kingdom, Canada, Australia, Germany and France \u2014 destinations offering clearer post-study work pathways and, in many cases, faster visa processing. Observers warn that the centre of gravity in international education could shift away from the United States toward Europe and the Gulf if the trend persists across multiple admission cycles.

## The Counterintuitive Opportunity

Yet the contraction has created an unexpected opening for the students who do still apply. With Indian enrolment down sharply, U.S. universities \u2014 which rely on full-fee international students for a critical slice of revenue \u2014 are competing harder for strong candidates. Admissions advisers report scholarships and assistantships at selective institutions becoming more accessible than they have been in years, particularly for applicants with high test scores, strong GPAs and research experience. For a well-prepared student willing to navigate the visa gauntlet, 2026 may paradoxically be one of the better years to win a place and aid.

The financial stakes for American higher education are real: NAFSA estimates that a decline in new international students could cost the U.S. economy more than a billion dollars, and institutions with heavy graduate and STEM concentrations are the most exposed.

## Why It Matters to the Diaspora

The Indian-American community was built on this exact pathway, and its contraction touches the diaspora on two fronts. For families still sending children to study in the U.S., the message is to plan earlier, apply more widely, and treat the visa interview as the decisive hurdle rather than a formality. For the community as a whole, the numbers mark a quieter shift in the migration story itself: as the student pipeline thins and the GCC boom pulls talent back toward Bengaluru and Hyderabad, the one-way flow that defined the diaspora for decades is giving way to something more circular.

What is not in doubt is the underlying ambition. Indian students have not stopped wanting world-class education; they are simply recalculating where, and at what cost, to pursue it. Whether the United States remains their first choice is now, for the first time in a generation, an open question.

**Sources:** Reuters, The Hindu BusinessLine, Institute of International Education / Shorelight Education"""

    article = {
        "headline": "Indian Student Numbers in the US Just Fell 6.9% \u2014 the Sharpest Drop in a Decade",
        "subheadline": "U.S. visa denials for international students hit a 10-year high of 35 percent as Indian enrolment slid to 352,644, with graduate and law programs hardest hit \u2014 pushing students toward the UK, Canada and Australia even as scholarships open up for those who stay the course.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "The student visa was the original on-ramp into the Indian-American story \u2014 study to H-1B to green card to family \u2014 so a 6.9 percent enrolment drop and a decade-high 35 percent visa-denial rate signal a narrowing of the very pathway the diaspora was built on, forcing families to plan earlier and apply wider even as the reverse pull of India's tech boom makes the old one-way migration more circular.",
        "sources": ["Reuters", "The Hindu BusinessLine", "Institute of International Education / Shorelight Education"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 3: International Day of Yoga 2026 in the US diaspora
# ========================================================================
def write_article_3():
    print("\n" + "=" * 60)
    print("ARTICLE 3: International Day of Yoga 2026 US diaspora")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "International Day of Yoga celebration participants",
        ["yoga day", "international day of yoga", "yoga"],
        "An International Day of Yoga gathering; the 12th edition is celebrated worldwide on June 21")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "yoga group practice outdoor mats",
            ["yoga", "asana", "meditation", "padmasana"],
            "A group yoga session; the 2026 theme is 'Yoga for Healthy Ageing'")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Lincoln Memorial Washington DC",
            ["lincoln memorial", "washington"],
            "The Lincoln Memorial in Washington, the venue for the Indian Embassy's Yoga Day event")
    if not image_url:
        px = fetch_pexels_image("yoga group practice outdoor sunrise")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "A group yoga session; communities worldwide mark International Day of Yoga on June 21", "Pexels"

    slug = "international-day-of-yoga-2026-us-diaspora-lincoln-memorial-times-square-healthy-ageing-20260617"

    body = """When the sun rises over the Lincoln Memorial on Friday morning, the marble steps where Martin Luther King Jr. once spoke will fill instead with yoga mats. The Indian Embassy in Washington has chosen the iconic monument as the venue for its International Day of Yoga celebration on June 19, the opening note in a week of festivities that will carry the practice from the U.S. capital to a sunrise gathering in Times Square \u2014 and to roughly 2,500 locations across the world.

The 12th International Day of Yoga, formally observed on June 21, arrives this year under the theme "Yoga for Healthy Ageing," a deliberate framing for a world living longer than ever. Prime Minister Narendra Modi will lead the national celebration in Kolkata, on the historic Red Road, while the Ministry of Ayush coordinates events through more than 210 Indian diplomatic missions and the Indian Council for Cultural Relations. The scale is already record-breaking: a nationwide live session on June 14 drew more than four lakh participants simultaneously, setting a new Guinness World Record.

## A Diaspora Showcase

For the Indian-American community, the week is as much a cultural statement as a wellness event. In New York, the Consulate General of India will host the marquee celebration in Times Square on June 21, an event that routinely draws thousands of practitioners to one of the most photographed public spaces on earth. The chief guest is Padma Shri Dr. H. R. Nagendra \u2014 the yoga scholar who guides Modi's own personal practice and serves as president of Bengaluru's S-VYASA University \u2014 lending the gathering a direct line to the discipline's most prominent modern advocate.

Nagendra's U.S. visit, at the invitation of the Rajasthan Association of North America, threads through the diaspora's institutional life. Before Times Square, he is slated to inaugurate a wellness retreat at a longevity resort in upstate New York, joined by figures such as Mount Sinai interventional cardiologist Dr. Samin K. Sharma \u2014 a pairing of ancient practice and modern medicine that captures the "healthy ageing" theme precisely.

## Wellness Meets Soft Power

The celebrations stretch well beyond the marquee venues. In Houston, the Consulate General will gather practitioners at Midtown Park on June 20. Community organisations from GOPIO to local cultural associations are staging their own sessions, including accessible, chair-based formats designed for seniors and first-timers. The United Nations, which adopted India's proposal for the day back in 2014, will hold its own observance on June 18.

That global footprint is no accident. Since 2014, India has steadily built Yoga Day into one of its most effective instruments of soft power \u2014 a low-cost, broadly welcomed expression of cultural identity that needs no translation. "Yoga has transcended borders, cultures and languages," Ayush minister Prataprao Jadhav said at the curtain-raiser, framing it as a shared global movement rather than a national export. For a country often defined abroad by its politics and its economy, the image of thousands stretching in unison in Times Square is a gentler kind of diplomacy.

## Why It Matters to the Diaspora

For the Indian diaspora in the United States, this year's theme lands with particular resonance. The first large wave of Indian immigrants who arrived in the 1960s and 1970s is now entering its seventies and eighties, and the question of how to age well \u2014 physically active, mentally sharp, and connected to community \u2014 is no longer abstract. A celebration built around "healthy ageing" speaks directly to families navigating that passage, often while caring for parents in one country and children in another.

There is a quieter function, too. Events like the Lincoln Memorial sunrise or the Times Square gathering are gathering points \u2014 places where second- and third-generation Indian-Americans encounter a piece of their heritage in a form that is celebrated rather than explained, claimed by the wider American mainstream rather than confined to the home. Yoga has become one of the diaspora's most successful cultural exports precisely because it belongs to everyone now. On June 21, from a marble monument in Washington to a neon-lit square in Manhattan, the community will roll out its mats and, for a morning at least, breathe together.

**Sources:** The Indian Eye, IANS, Ministry of Ayush"""

    article = {
        "headline": "From the Lincoln Memorial to Times Square, the Diaspora Rolls Out Its Mats for Yoga Day 2026",
        "subheadline": "The 12th International Day of Yoga, themed 'Yoga for Healthy Ageing,' will be marked at 2,500 venues worldwide on June 21 \u2014 with Modi leading in Kolkata and Indian-American communities gathering from Washington to New York to Houston.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "This year's 'healthy ageing' theme lands directly on a diaspora whose first 1960s-70s immigrant wave is now in its seventies and eighties, while marquee gatherings at the Lincoln Memorial and Times Square serve as cultural anchor points where second- and third-generation Indian-Americans encounter their heritage as something celebrated by the American mainstream rather than confined to home.",
        "sources": ["The Indian Eye", "IANS", "Ministry of Ayush"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# MAIN
# ========================================================================
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"VIDESHI NEWS WRITER \u2014 {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")

    results = []
    results.append(("India May WPI inflation 9.68%", write_article_1()))
    results.append(("Indian student enrolment US -6.9%", write_article_2()))
    results.append(("International Day of Yoga 2026 diaspora", write_article_3()))

    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    for name, success in results:
        print(f"  {'\u2713 SUCCESS' if success else '\u2717 FAILED'}: {name}")
    print(f"{'='*60}\n")
