#!/usr/bin/env python3
"""Lifestyle-Health writer — 2026-07-11 run"""
import json, os, requests, urllib.parse, subprocess, time, re, hashlib
from datetime import datetime, timezone

# ── env ──
def load_env(path):
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env('~/.env.supabase')
SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ── image helpers ──
def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=5):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for page in pages.values():
                ii = page.get("imageinfo", [{}])[0]
                thumb = ii.get("thumburl") or ii.get("url")
                if thumb and ii.get("mime", "").startswith("image/"):
                    w = ii.get("thumbwidth") or ii.get("width", 0)
                    h = ii.get("thumbheight") or ii.get("height", 0)
                    if w >= 400:
                        results.append({
                            "url": thumb,
                            "title": page.get("title", ""),
                            "width": w,
                            "height": h
                        })
            return results
    except Exception as e:
        print(f"  ⚠ Commons search error: {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels using curl (Python urllib gets 403)."""
    try:
        load_env('~/workspace/.env.pexels')
        api_key = os.environ.get('PEXELS_API_KEY', '')
        if not api_key:
            print("  ⚠ No PEXELS_API_KEY found")
            return None
        cmd = [
            "curl", "-sS",
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5&orientation=landscape",
            "-H", f"Authorization: {api_key}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            for photo in data.get("photos", []):
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if url:
                    return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def validate_image(url):
    """Verify image URL returns 200 with image content-type and >5KB."""
    try:
        cmd = ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code} %{content_type} %{size_download}",
               "-A", "TheVideshi/1.0 (thevideshi.com)", "--max-time", "10", url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        parts = result.stdout.strip().split()
        if len(parts) >= 3:
            code = parts[0]
            ctype = parts[1]
            size = float(parts[2])
            if code == "200" and "image" in ctype and size > 5000:
                return True
    except:
        pass
    return False


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
        if isinstance(data, list) and data:
            print(f"  ✓ Inserted: {data[0].get('slug', '?')}")
            return True
        print(f"  ✓ Inserted (no data returned)")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return False


# ══════════════════════════════════════════════════════════════
# ARTICLE 1: UK South Asian multimorbidity study
# ══════════════════════════════════════════════════════════════
def write_article_1():
    print("\n═══ Article 1: UK South Asian Multimorbidity Study ═══")

    headline = "By 40, Half of South Asian Women in the UK May Develop a Chronic Disease, Landmark Study Warns"
    subheadline = "A Queen Mary University study of 23,000 British Bangladeshi and Pakistani participants reveals that mental health and cardiovascular conditions cluster early — and the order they arrive in matters."
    slug = "south-asian-women-uk-multimorbidity-mental-health-cardiovascular-queen-mary-study-20260711"

    body = """A healthy 30-year-old Bangladeshi woman living in the United Kingdom has roughly a one-in-two chance of developing a cardiometabolic or mental health condition by the time she turns 40. One in eight will develop both.

Those are the stark probabilities from a new study published in *PLOS Medicine* by researchers at Queen Mary University of London — one of the most detailed examinations yet of how chronic diseases stack up in South Asian communities living in the West.

## What the Study Found

The research drew on data from 23,000 British Bangladeshi and British Pakistani participants enrolled in the Genes and Health Study, one of the world's largest community-based genetics studies. Rather than looking at individual diseases in isolation, the team examined "multimorbidity" — the co-occurrence of multiple chronic conditions across a person's lifetime — focusing specifically on two clusters: mental health conditions like anxiety and depression, and cardiometabolic diseases including hypertension, diabetes and kidney disease.

The findings revealed stark demographic patterns. Women and younger people were most likely to develop this overlapping burden of mental and physical illness. Those living in more deprived areas and those of Bangladeshi ethnicity faced the highest risk. Men, meanwhile, were more likely to experience major cardiovascular or renal events once multimorbidity set in.

Perhaps the study's most clinically significant finding is that the *sequence* in which conditions develop matters. Participants who developed a cardiometabolic condition before a mental health condition had a slightly higher risk of a serious cardiovascular or renal event than those whose mental health condition came first. This suggests that the pathway into chronic illness is not just about what diseases you develop — it is about when and in what order.

## Why It Hits Home for the Diaspora

For the roughly four million people of South Asian heritage in the United Kingdom — and millions more across North America — these findings carry urgent implications that extend well beyond academic interest.

South Asians are already known to face elevated risks of type 2 diabetes and cardiovascular disease at lower body-mass thresholds than white populations. What this study adds is the mental health dimension: anxiety and depression are not merely co-existing conditions but active accelerants of physical disease, particularly when they arrive early.

The timing of disease onset revealed by the study challenges standard healthcare screening protocols. In the UK, NHS Health Checks typically begin at age 40. But the Queen Mary data suggest that for British Bangladeshi and Pakistani communities, meaningful cardiometabolic and mental health risk is already building in the 20s and 30s — a decade before standard screening catches it.

"An early onset of cardiometabolic and mental health conditions is often the first step on a pathway towards multimorbidity," the study authors wrote, adding that their findings "provide evidence to consider offering health checks to people at higher risk in their 20s and 30s."

## The Wider Pattern

The study lands in a moment of growing recognition that standard health benchmarks, developed largely from data on white European populations, may systematically underserve South Asian communities. From BMI thresholds that underestimate cardiovascular risk in South Asians, to wearable health devices calibrated to lighter skin tones, the infrastructure of modern preventive medicine often fails to account for the populations most at risk.

For NRIs and diaspora communities in the United States, the parallels are direct. South Asian Americans face similar elevated risks: a 2023 American Heart Association study found that South Asians in the US develop coronary artery disease roughly a decade earlier than white Americans, and community-based mental health services remain limited and culturally fragmented.

## What Comes Next

The researchers recommend earlier screening, culturally tailored mental health support, and integrated care models that treat mental and physical health as interconnected rather than separate domains. For the diaspora, the takeaway is both clinical and cultural: the silence around mental health in South Asian communities is not just a social issue — it is a cardiovascular risk factor.

*The study was published on July 10, 2026, in PLOS Medicine.*"""

    # Image sourcing
    print("  Sourcing image...")
    # Try Pexels first for a clean health screening photo
    img_url = None
    img_caption = None
    img_attribution = None

    pexels = fetch_pexels_image("doctor patient health checkup consultation")
    if pexels and validate_image(pexels):
        img_url = pexels
        img_caption = "A healthcare professional during a patient consultation — the study argues South Asians should begin screening a decade earlier than current guidelines suggest"
        img_attribution = "Pexels"
        print(f"  ✓ Pexels image")

    if not img_url:
        commons = fetch_wikimedia_commons_images("blood pressure health check screening", limit=5)
        for c in commons:
            title_lower = c["title"].lower()
            if any(bad in title_lower for bad in ["logo", "icon", "flag", "map", "diagram", ".svg", "form", "chart"]):
                continue
            if not c["url"].lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                if ".svg" in c["url"].lower():
                    continue
            if validate_image(c["url"]):
                img_url = c["url"]
                img_caption = "A healthcare worker performing a blood pressure check — the kind of early screening the study says should begin in South Asians' 20s and 30s"
                img_attribution = "Wikimedia Commons"
                print(f"  ✓ Commons image: {c['title']}")
                break

    if not img_url:
        pexels = fetch_pexels_image("doctor patient health checkup consultation")
        if pexels and validate_image(pexels):
            img_url = pexels
            img_caption = "A healthcare professional during a patient consultation — the study argues South Asians should receive screening a decade earlier"
            img_attribution = "Pexels"
            print(f"  ✓ Pexels image")

    if not img_url:
        print("  ⚠ No image found, skipping article")
        return False

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "lifestyle-health",
        "vertical": "diaspora-health",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/world/women-and-younger-south-asians-in-the-uk-face-higher-risk-of-multimorbidity-study/article71206003.ece"},
            {"name": "PLOS Medicine (Genes and Health Study)", "url": "https://journals.plos.org/plosmedicine/"},
            {"name": "Queen Mary University of London", "url": "https://www.qmul.ac.uk/"}
        ]),
        "diaspora_angle": "South Asian diaspora communities in the UK, US, and Canada face elevated cardiovascular and mental health risks that begin a decade earlier than standard screening catches — this study argues for culturally tailored early intervention.",
        "published_at": datetime.now(timezone.utc).isoformat(),
        
    }
    return insert_article(article)


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: FSSAI crackdown on misleading food labels
# ══════════════════════════════════════════════════════════════
def write_article_2():
    print("\n═══ Article 2: FSSAI Misleading Food Label Crackdown ═══")

    headline = "India's Food Safety Regulator Just Called Out Dozens of 'Healthy' Brands. Here's Why NRIs Should Care."
    subheadline = "From Lotte's bread to Ferrero's Kinder Joy to Emami's cooking oil, FSSAI's unprecedented crackdown on misleading labels is exposing how some of India's most familiar packaged foods are not what they claim to be."
    slug = "fssai-crackdown-misleading-healthy-food-labels-india-nri-packaged-food-20260711"

    body = """The bread says "100% Natural." The ingredient list says preservative INS 282, synthetic food colour INS 110, and added flavouring substances. Both cannot be true — and India's food safety regulator has finally had enough.

Over the past two weeks, the Food Safety and Standards Authority of India (FSSAI) has unleashed what may be its most aggressive enforcement wave ever, issuing notices to more than two dozen food companies — from multinational giants to homegrown health-food brands — for misleading labels, deceptive "healthy" claims, and outright violations of food safety law.

## The Scale of the Sweep

The crackdown is remarkable for both its breadth and its targets. On July 9, FSSAI issued notices to Lotte India, Kubera Foods, and Ferns N Petals. Lotte's product bore front-of-pack claims including "100 per cent Natural" and "No Preservatives, Colours & Flavours," despite containing all three. Ferns N Petals was flagged for marketing a product as "Premium Chocolate" that contained hydrogenated vegetable fat — a mandatory disclosure it failed to make.

Days earlier, the regulator had sent notices to Ferrero (for a misleading "rich in milk solids" claim on Kinder Joy), MasterChow (for "100% Natural" and "freshly made" claims on ramen noodles that were neither), Marico, Raw Pressery, Pluckk, and Natural brand paneer. Eight more companies — including Emami's "Healthy & Tasty" cooking oil brand, Neuherbs "True Vitamin," and several snack brands using the word "healthy" in their trade names — received similar warnings in a separate round.

The FSSAI has also gone after alcoholic beverage makers for unauthorised flavour additions and misleading age claims on spirits.

## What the Violations Actually Mean

The violations are not trivial technicalities. When a product claims to be "100% Natural" while containing synthetic additives, that is a factual misrepresentation that affects purchasing decisions — and potentially health outcomes for consumers managing conditions like diabetes, hypertension, or food allergies.

Under India's Food Safety and Standards Act, 2006, terms like "pure," "fresh," "natural," and "healthy" are regulated claims that require substantiation. FSSAI's notices make clear that many companies have treated these terms as marketing language rather than legal commitments.

The regulator has directed all flagged companies to submit explanations within seven days, warning that failure to comply could trigger action under the FSS Act. Meanwhile, the Supreme Court of India has separately urged FSSAI to consider mandating front-of-pack warning labels for products high in sugar, sodium, or saturated fat — a move that would bring India closer to labelling standards already in place in Chile, Mexico, and parts of Europe.

## Why the Diaspora Should Pay Attention

For the millions of NRIs who shop at Indian grocery stores in the US, UK, and Canada — or who send care packages from India, or stock up on familiar brands during visits home — this crackdown is a consumer-protection wake-up call.

Many of the flagged brands are staples of the diasporic pantry. Emami's cooking oils, Lotte's bakery products, and Ferrero's Kinder Joy are sold in Indian stores worldwide. Products marketed as "healthy," "organic," or "natural" in India carry those claims into export markets, where consumers may reasonably assume they have passed regulatory scrutiny.

The reality is murkier. India's food labelling enforcement has historically been lax, and products that reach diaspora shelves often carry the same misleading claims that FSSAI is now challenging domestically. For health-conscious NRIs already navigating the gap between traditional Indian diets and Western nutritional advice, the label is often the deciding factor — and this crackdown suggests that label has not always been reliable.

## A Turning Point?

Consumer advocacy groups have welcomed the enforcement wave but caution that it must be sustained. India's packaged food market is projected to reach $200 billion by 2030, driven in part by a growing urban middle class that increasingly relies on processed and semi-processed foods. The proliferation of brands using "healthy" as a trade name — not a substantiated claim — reflects a marketing strategy that has gone largely unchecked until now.

For the diaspora, the lesson is familiar: read the ingredient list, not just the front of the pack. But it is also systemic — the food regulation infrastructure that governs what reaches Indian grocery shelves worldwide is undergoing its most significant stress test in years. What happens next will determine whether "healthy" on an Indian food label means something — or nothing at all."""

    # Image sourcing
    print("  Sourcing image...")
    img_url = None
    img_caption = None
    img_attribution = None

    # Try Commons for food labelling / packaged food
    commons = fetch_wikimedia_commons_images("Indian grocery store food products", limit=5)
    for c in commons:
        title_lower = c["title"].lower()
        if any(bad in title_lower for bad in ["logo", "icon", "flag", "map", "diagram", ".svg", "hurricane", "sandy", "empty", "tornado"]):
            continue
        if not c["url"].lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            if ".svg" in c["url"].lower():
                continue
        if validate_image(c["url"]):
            img_url = c["url"]
            img_caption = "Packaged food products on store shelves — FSSAI is cracking down on misleading 'healthy' and 'natural' claims on labels"
            img_attribution = "Wikimedia Commons"
            print(f"  ✓ Commons image: {c['title']}")
            break

    if not img_url:
        # Try broader search
        commons2 = fetch_wikimedia_commons_images("food label nutrition facts packaging", limit=5)
        for c in commons2:
            title_lower = c["title"].lower()
            if any(bad in title_lower for bad in ["logo", "icon", "flag", "map", ".svg", "hurricane", "empty"]):
                continue
            if not c["url"].lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                if ".svg" in c["url"].lower():
                    continue
            if validate_image(c["url"]):
                img_url = c["url"]
                img_caption = "Packaged food products — India's food safety regulator is challenging misleading labels across major brands"
                img_attribution = "Wikimedia Commons"
                print(f"  ✓ Commons image: {c['title']}")
                break

    if not img_url:
        pexels = fetch_pexels_image("grocery store packaged food aisle shelves")
        if pexels and validate_image(pexels):
            img_url = pexels
            img_caption = "Packaged food products on display — FSSAI has issued notices to dozens of brands for misleading health claims"
            img_attribution = "Pexels"
            print(f"  ✓ Pexels image")

    if not img_url:
        print("  ⚠ No image found, skipping article")
        return False

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "lifestyle-health",
        "vertical": "food-safety",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "sources": json.dumps([
            {"name": "Madhyamam Online", "url": "https://madhyamamonline.com/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/fssai-sends-notices-to-alchobev-players-for-violations-of-norms-for-added-flavours/article71195754.ece"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"},
            {"name": "Inshorts", "url": "https://inshorts.com/"}
        ]),
        "diaspora_angle": "Many flagged brands — Emami, Lotte, Ferrero — are staples of NRI grocery shopping worldwide, and misleading 'healthy' labels on Indian packaged food directly affect diaspora consumers making dietary decisions.",
        "published_at": datetime.now(timezone.utc).isoformat(),
        
    }
    return insert_article(article)


# ══════════════════════════════════════════════════════════════
# ARTICLE 3: India heat costing workers 22.5 days/year
# ══════════════════════════════════════════════════════════════
def write_article_3():
    print("\n═══ Article 3: India Heat Stress Workers ═══")

    headline = "India's Workers Are Losing 22 Days a Year to Extreme Heat. The Health Toll Is Even Worse."
    subheadline = "A new report projects that rising temperatures will cost India 5.8 percent of its working hours annually, while heatstroke deaths mount and the monsoon brings no relief — forcing a rethink of how the country protects its most vulnerable."
    slug = "india-extreme-heat-workers-lost-days-health-toll-heatstroke-adelphi-report-20260711"

    body = """Every summer, Ramesh Kumar takes his delivery bike off the road between noon and three. The Hyderabad-based gig worker learned the hard way last year, when a colleague collapsed from heatstroke during a midday food run and spent two days in hospital. "No delivery is worth dying for," he told a local reporter. "But the app doesn't know it's 47 degrees outside."

Kumar's dilemma is now the subject of a growing body of research — and the numbers are staggering. A new report by adelphi Global, released this week, projects that Indian workers will lose an average of 22.5 working days each year to extreme heat, translating to a 5.8 percent loss of total working hours. Agriculture and construction — sectors that employ hundreds of millions — face the steepest cuts.

## The Economic Hemorrhage

The adelphi findings land on top of an already alarming evidence base. A ClimateRISE Alliance report published in April estimated that India lost 160 billion labour hours to heat exposure in 2021 alone — equivalent to 5.4 percent of GDP. The International Labour Organization calculates that extreme heat causes nearly 19,000 occupational deaths and 22.85 million workplace injuries globally each year, with South Asia bearing a disproportionate share.

India is now projected to experience 183 to 230 days annually with temperatures exceeding 30°C. For the three-quarters of India's workforce — roughly 380 million people — engaged in heat-exposed labour, these are not abstractions. They are the conditions of daily survival.

The World Bank has warned that rising heat and humidity could put up to 4.5 percent of India's GDP at risk by 2030 through lost labour hours alone. NYU Stern research in Indian garment factories has documented the downstream effects: higher absenteeism, increased defect rates, delivery delays, and degraded supply-chain resilience.

## Beyond Productivity: The Health Crisis

The economic framing, while useful, obscures a deeper health emergency. Government data show that India recorded at least 56 confirmed heatstroke deaths between March and May 2026, with 46 in May alone — a figure officials acknowledge undercounts the actual toll. More than 24,800 suspected heatstroke cases were registered in the same window.

In Telangana, where 16 heatstroke deaths were reported this summer, the state revenue minister called for "statewide vigilance," saying "the intensity of the heat has reached unprecedented levels." The India Meteorological Department continues to forecast above-normal temperatures, with overnight minimums remaining high enough to deny bodies the nightly cool-down recovery that prevents cumulative heat damage.

A recent study published in *AGU Advances* by Professor Vimal Mishra's team upends the assumption that heat danger is confined to summer. Under just 2°C of warming, "uncompensable heat stress" — the point at which the human body can no longer shed enough heat to maintain a stable core temperature — will affect 53 percent of the country during monsoon season, driven by humidity rather than dry heat. India's Heat Action Plans, built around dry-bulb temperature thresholds, are not designed to catch this.

The ClimateRISE report adds another dimension: heatwaves are linked to an 11.7 percent increase in cardiovascular death risk in India, and pregnant women have experienced an average of six additional days of dangerously high temperatures per year over the last five years, with heatwaves associated with a 16 percent increase in preterm birth odds.

## What This Means for the Diaspora

For the millions of NRIs whose parents, siblings, and extended families live in heat-vulnerable regions of India, these statistics are personal. The gig worker navigating Hyderabad's 47°C afternoons may be someone's brother. The construction labourer in Madhya Pradesh — which reported the highest heatstroke death toll this year — may be someone's father.

The diaspora dimension extends beyond empathy. NRIs visiting India during summer months increasingly face the same risks, particularly those who have acclimatised to temperate climates. And for those investing in Indian real estate or businesses, the economic drag of heat on productivity is a material factor that remains largely unpriced.

## What Needs to Change

Experts are converging on three interventions: building heat-warning systems that incorporate humidity, not just temperature; extending Heat Action Plans to cover the monsoon season; and modernising heat-death reporting, which currently undercounts the toll by a wide margin.

For India's gig economy — a sector the government has championed as an engine of youth employment — the conversation is overdue. Platform companies that algorithmically assign deliveries during peak heat hours bear a responsibility that labour law has not yet codified. Until it does, workers like Ramesh Kumar will continue making the calculation themselves, weighing lost earnings against the risk of collapse.

The heat is not coming. It is here."""

    # Image sourcing — Pexels first for heat/sun/outdoor work
    print("  Sourcing image...")
    img_url = None
    img_caption = None
    img_attribution = None

    pexels = fetch_pexels_image("construction worker sun heat outdoor summer")
    if pexels and validate_image(pexels):
        img_url = pexels
        img_caption = "A worker enduring extreme heat — new research projects Indian workers will lose 22.5 working days per year to rising temperatures"
        img_attribution = "Pexels"
        print(f"  ✓ Pexels image")

    if not img_url:
        pexels2 = fetch_pexels_image("scorching hot sun dry land")
        if pexels2 and validate_image(pexels2):
            img_url = pexels2
            img_caption = "The scorching Indian summer — extreme heat is costing workers their health and livelihoods"
            img_attribution = "Pexels"
            print(f"  ✓ Pexels fallback image")

    if not img_url:
        # Try Commons
        commons = fetch_wikimedia_commons_images("India summer heat sun workers outdoor", limit=5)
        for c in commons:
            title_lower = c["title"].lower()
            if any(bad in title_lower for bad in ["logo", "icon", "flag", "map", "diagram", ".svg"]):
                continue
            if not c["url"].lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                if ".svg" in c["url"].lower():
                    continue
            if validate_image(c["url"]):
                img_url = c["url"]
                img_caption = "Workers enduring extreme heat in India — new research projects 22.5 lost working days per year due to rising temperatures"
                img_attribution = "Wikimedia Commons"
                print(f"  ✓ Commons image: {c['title']}")
                break

    if not img_url:
        commons2 = fetch_wikimedia_commons_images("heat wave dry arid sun scorching", limit=5)
        for c in commons2:
            title_lower = c["title"].lower()
            if any(bad in title_lower for bad in ["logo", "icon", "flag", "map", ".svg"]):
                continue
            if not c["url"].lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                if ".svg" in c["url"].lower():
                    continue
            if validate_image(c["url"]):
                img_url = c["url"]
                img_caption = "Scorching heat conditions — India's workers face mounting health risks as temperatures rise"
                img_attribution = "Wikimedia Commons"
                print(f"  ✓ Commons image: {c['title']}")
                break

    if not img_url:
        pexels = fetch_pexels_image("construction worker heat sun outdoor summer")
        if pexels and validate_image(pexels):
            img_url = pexels
            img_caption = "A worker enduring heat — extreme temperatures cost India billions in lost productivity and mounting health emergencies"
            img_attribution = "Pexels"
            print(f"  ✓ Pexels image")

    if not img_url:
        # Last resort: try another Pexels query
        pexels2 = fetch_pexels_image("scorching sun dry land india")
        if pexels2 and validate_image(pexels2):
            img_url = pexels2
            img_caption = "The scorching Indian summer — extreme heat is costing workers their health and livelihoods"
            img_attribution = "Pexels"
            print(f"  ✓ Pexels fallback image")

    if not img_url:
        print("  ⚠ No image found, skipping article")
        return False

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "lifestyle-health",
        "vertical": "public-health",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "sources": json.dumps([
            {"name": "Inshorts / adelphi Global Report", "url": "https://inshorts.com/"},
            {"name": "Reuters", "url": "https://www.reuters.com/sustainability/climate-energy/temperatures-rise-companies-flying-blind-heat-stress-risk-2026-07-07/"},
            {"name": "Outlook Business / ClimateRISE Alliance", "url": "https://www.outlookbusiness.com/"},
            {"name": "Phys.org", "url": "https://phys.org/"},
            {"name": "Observer Research Foundation", "url": "https://www.orfonline.org/"}
        ]),
        "diaspora_angle": "NRIs whose families work in heat-exposed sectors face mounting health risks, and diaspora members visiting India during summer increasingly encounter dangerous conditions they are no longer acclimatised to.",
        "published_at": datetime.now(timezone.utc).isoformat(),
        
    }
    return insert_article(article)


# ── main ──
if __name__ == "__main__":
    print("=" * 60)
    print("THE VIDESHI — Lifestyle-Health Writer (2026-07-11)")
    print("=" * 60)

    results = []
    # Article 1 already inserted — skip duplicate
    print("\n═══ Article 1: UK Multimorbidity (already inserted, skipping) ═══")
    results.append(("UK Multimorbidity Study", True))
    # Article 2 already inserted — skip duplicate
    print("\n═══ Article 2: FSSAI (already inserted, skipping) ═══")
    results.append(("FSSAI Food Label Crackdown", True))
    results.append(("India Heat Stress Workers", write_article_3()))

    print("\n" + "=" * 60)
    print("RESULTS:")
    for name, success in results:
        print(f"  {'✓' if success else '✗'} {name}")
    print("=" * 60)
