#!/usr/bin/env python3
"""Lifestyle-health & markets-finance writer — 2026-06-29 evening run."""
import os, sys, json, re, time, io, uuid, hashlib
import requests
from datetime import datetime, timezone

# Load environment
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    k = k.replace('export ', '').strip()
                    v = v.strip().strip('"').strip("'")
                    os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')
UA = "TheVideshi/1.0 (thevideshi.com)"

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ── Image sourcing helpers ──────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    encoded = person_name.replace(' ', '_')
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


def fetch_wikimedia_commons_images(query, limit=5):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime",
        "iiurlwidth": "1200", "format": "json"
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
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []


_COMMONS_STOP = {
    "the","a","an","of","in","on","at","to","for","and","or","with","as","by","from","is",
    "are","was","were","be","new","says","after","over","amid","how","why","what","2024",
    "2025","2026","india","indian","us","usa","american","uk","first","more","than",
    "people","man","woman","group","day","year","top","big","set","get","make","makes",
    "made","you","your","they","them","this","that","social","media","using","use",
}

def commons_relevance_ok(commons_title, headline, topic=""):
    title_l = (commons_title or "").lower()
    head_l = (headline or "").lower()
    if not title_l:
        return False
    toks = re.findall(r"[A-Za-z][A-Za-z'-]+", headline or "")
    kws = set()
    for t in toks:
        tl = t.lower()
        if len(tl) >= 4 and tl not in _COMMONS_STOP:
            kws.add(tl)
    topic_toks = re.findall(r"[A-Za-z][A-Za-z'-]+", topic or "")
    for t in topic_toks:
        tl = t.lower()
        if len(tl) >= 4 and tl not in _COMMONS_STOP:
            kws.add(tl)
    if not kws:
        return True
    return any(kw in title_l for kw in kws)


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    import subprocess
    try:
        cmd = [
            "curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
            f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=3&orientation=landscape"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels: {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def download_image(url):
    import subprocess
    tmp = f"/tmp/dl_{uuid.uuid4().hex[:8]}.jpg"
    try:
        result = subprocess.run(
            ["curl", "-sS", "-L", "-A", UA, "-o", tmp, url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and os.path.exists(tmp) and os.path.getsize(tmp) > 5000:
            with open(tmp, "rb") as f:
                return f.read()
    except Exception as e:
        print(f"  ⚠ Download error: {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()


def upload_image_to_supabase(jpeg_bytes, filename):
    r = requests.post(
        f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        },
        data=jpeg_bytes, timeout=60,
    )
    if r.status_code not in (200, 201):
        print(f"  ⚠ Upload failed {r.status_code}: {r.text[:200]}")
        return None
    return f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"


def source_image(slug, headline, topic, person=None):
    """Multi-source image sourcing. Returns (url, caption, attribution) or (None, None, None)."""
    candidates = []

    # Source 1: Wikipedia person image
    if person:
        wiki_img = fetch_wikipedia_person_image(person)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "relevance": 3})

    # Source 2: Wikimedia Commons
    search_q = f"{person} {topic}" if person else topic
    commons = fetch_wikimedia_commons_images(search_q)
    if not commons:
        commons = fetch_wikimedia_commons_images(topic)
    commons = [c for c in commons if commons_relevance_ok(c.get("title", ""), headline, topic)]
    for c in commons[:2]:
        candidates.append({"url": c["url"], "source": "wikimedia_commons", "relevance": 2, "title": c.get("title", "")})

    # Source 3: Pexels fallback (only for non-person topics)
    if not person:
        pex = fetch_pexels_image(topic)
        if pex:
            candidates.append({"url": pex, "source": "pexels", "relevance": 1})

    # Pick best
    if not candidates:
        print(f"  ⚠ No image found for {slug}")
        return None, None, None

    candidates.sort(key=lambda x: -x["relevance"])
    best = candidates[0]
    print(f"  → Selected: {best['source']} — {best['url'][:80]}...")

    # Download and upload to Supabase
    raw = download_image(best["url"])
    if not raw:
        print(f"  ⚠ Could not download image")
        return None, None, None

    compressed = compress_image(raw)
    size_kb = len(compressed) / 1024
    print(f"  Compressed: {size_kb:.0f} KB")
    if size_kb < 10:
        print(f"  ⚠ Image too small ({size_kb:.0f} KB), skipping")
        return None, None, None

    filename = f"{slug}.jpg"
    final_url = upload_image_to_supabase(compressed, filename)
    if not final_url:
        return None, None, None

    attribution = "Wikimedia Commons" if best["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
    return final_url, attribution, best["source"]


def insert_article(article):
    """Insert article into p2_articles."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Inserted: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed {r.status_code}: {r.text[:300]}")
        return None


# ── ARTICLES ────────────────────────────────────────────────────────

now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

articles = []

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 1: Biological aging / cancer risk in younger generations
# ═══════════════════════════════════════════════════════════════════

art1_slug = "millennials-gen-z-aging-faster-biologically-cancer-risk-nature-medicine-phenoage-diaspora-20260629"
art1_headline = "Millennials and Gen Z Are Aging Faster Inside Their Bodies — and It May Be Fueling a Cancer Surge"
art1_subheadline = "A landmark study of 164,000 people across the US and UK found that younger generations show significantly more biological 'wear and tear' than their parents did at the same age — and the gap is linked to rising early-onset cancers in the gut, lungs, and uterus."

art1_body = """A thirty-year-old today may look younger than their parents did at the same age — better skincare, more sunscreen, fewer wrinkles. But a major new study published in *Nature Medicine* suggests that what is happening inside their bodies tells a very different story. On a molecular level, millennials and Gen Z are aging faster than any generation before them, and this accelerated internal wear may be driving a global surge in cancers diagnosed before the age of 55.

Researchers at the Washington University School of Medicine in St. Louis analyzed blood samples and health data from more than 164,000 adults across two of the world's largest health studies — the UK Biobank (154,169 participants) and the US All of Us research program (10,262 participants). Using an algorithm called PhenoAge, which estimates biological age from nine routine blood biomarkers, the team calculated each person's "age gap" — the difference between how old their body appears to be and how old they actually are.

The results were striking. In the UK cohort, people born between 1965 and 1974 had a 23 percent higher age gap than those born between 1950 and 1954. In the American cohort, the generational shift was even more dramatic: those born in the 1990s had a 92 percent higher standardized age gap than those born in the late 1960s. In plain terms, younger people's bodies are clocking more biological mileage at every age than their parents' bodies did.

## The Cancer Connection

When the researchers cross-referenced these biological aging scores with cancer diagnoses, a troubling pattern emerged. For every standard-deviation increase in the age gap score, the risk of developing cancer before age 55 rose by 8 percent overall. For lung cancer specifically, the risk jumped by 57 percent — even after accounting for smoking. The link held for digestive cancers and uterine cancers as well.

The study also drilled into organ-level aging, examining proteins tied to specific body systems. An immune system that appeared prematurely old was associated with higher early-onset lung cancer risk. Fat tissue that appeared biologically aged was linked to early-onset colorectal cancer — a cancer whose rates have been climbing sharply among young adults worldwide.

"Biological aging reflects wear and tear happening inside the body," said lead author Yin Cao, a molecular epidemiologist at Washington University. "This can include chronic inflammation, weakening of the immune system, and damage building up in cells over time."

## Why Younger Bodies Are Wearing Out Faster

Scientists do not yet have a single answer, but the leading hypotheses converge on the modern environment. Obesity rates have climbed generation over generation. Ultraprocessed foods make up an ever-larger share of diets in the US, UK, and increasingly in India. Physical inactivity is widespread. Sleep quality has deteriorated. Chronic stress has intensified. And environmental exposures — microplastics, air pollution, endocrine disruptors — have changed fundamentally over the past three decades.

The researchers believe biological age may act as a summary metric, capturing the cumulative burden of all these factors on the body in a way that no single risk factor can.

"If we can identify younger people with the highest cancer risk when they are still healthy, we can focus on prevention and early-detection strategies for the individuals who will benefit most," Cao told *ScienceAlert*.

## What This Means for the Diaspora

For South Asians in the US and UK, these findings arrive against an already concerning backdrop. South Asians carry elevated baseline risks for type 2 diabetes, cardiovascular disease, and metabolic syndrome — conditions rooted in the same inflammation and insulin resistance pathways that accelerate biological aging. Indian-Americans are among the fastest-growing demographics in both countries, and many are millennials and Gen Z professionals navigating high-stress careers and shifting diets that skew heavily toward convenience food.

The study's practical takeaway is not a new one, but its urgency has sharpened: maintaining a healthy weight, staying physically active, eating whole foods, getting adequate sleep, avoiding tobacco, and limiting alcohol remain the most evidence-based ways to slow biological aging and reduce cancer risk. The difference is that this evidence now comes with a generational alarm bell — the window for intervention may be narrower than previously assumed.

Cancer screenings designed for older adults may need to be reconsidered for younger populations, particularly those with metabolic risk factors. For NRI families with aging parents in India — where screening infrastructure is still developing — and young adult children in the West showing metabolic red flags early, this study is a reminder that prevention is not a retirement-age project. It starts now.

*Sources: Nature Medicine (June 2026); Washington University School of Medicine; UK Biobank; US All of Us Research Program; ScienceAlert; The Times (London)*"""

articles.append({
    "slug": art1_slug,
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "category": "lifestyle-health",
    "vertical": "health-research",
    "status": "review",
    "is_editorial": False,
    "published_at": now_utc,
    "sources": json.dumps(["Nature Medicine", "Washington University School of Medicine", "UK Biobank", "US All of Us Research Program", "ScienceAlert", "The Times"]),
    "diaspora_angle": "South Asians carry elevated metabolic and inflammatory risk factors that accelerate biological aging — this study adds urgency to earlier screening and lifestyle intervention for young NRI professionals.",
    "image_search_topic": "biological aging DNA damage cancer research laboratory",
    "image_person": None,
    "image_caption_text": "A researcher examines blood biomarker data in a laboratory setting",
})

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 2: Exercise prevents half of dementia cases
# ═══════════════════════════════════════════════════════════════════

art2_slug = "exercise-prevents-half-dementia-cases-university-minnesota-14-risk-factors-brain-health-diaspora-20260629"
art2_headline = "Exercise Alone Can Tackle Six of the 14 Risk Factors for Dementia — and May Prevent Half of All Cases"
art2_subheadline = "A University of Minnesota study identifies 14 modifiable lifestyle factors behind cognitive decline, and finds that consistent physical exercise addresses six of them at once — from blood pressure to depression — offering the single most powerful intervention against dementia."

art2_body = """Here is a number worth sitting with: roughly 42 percent of Americans over 55 will eventually develop some form of dementia. The number of new diagnoses per year is projected to double between 2020 and 2060. And genetics, the risk factor that looms largest in the public imagination, is only a fraction of the story.

A study from the University of Minnesota School of Nursing, highlighted during Alzheimer's and Brain Health Awareness Month, makes a forceful case that the most effective weapon against cognitive decline is also the simplest: moving your body.

According to Dereck Salisbury, an associate professor who led the research, an individual's overall dementia risk is shaped by 14 specific lifestyle and environmental factors that can be modified. Six of those 14 — obesity, high blood pressure, high blood sugar, depression, high cholesterol, and physical inactivity itself — can be directly addressed through a single intervention: consistent physical exercise.

## One Habit, Six Risk Factors

The elegance of the finding lies in how exercise cascades through interconnected health systems. Regular physical activity lowers blood pressure, improves insulin sensitivity, reduces cholesterol, counters obesity, alleviates symptoms of depression, and inherently eliminates inactivity. By addressing these six factors simultaneously, exercise protects vascular health, reduces systemic inflammation, and lowers the probability of premature cognitive decline.

"Moving your body helps protect brain health," Salisbury says. Health experts note that aerobic exercise, strength training, and mind-body activities — yoga, tai chi, even brisk walking — all contribute meaningfully to cognition, executive function, and memory.

## The Rural Telehealth Experiment

To test whether these benefits could reach underserved populations, Salisbury's team designed a virtual telehealth exercise program targeting adults aged 45 and older in rural communities — people who often lack access to gyms, specialists, or even group fitness classes. Participants were sent home equipment including stationary cycles, heart rate monitors, and blood pressure cuffs. Researchers monitored them remotely through virtual health screenings.

After just three months of structured exercise, participants showed significant improvements in aerobic fitness. The findings suggest that the barrier to dementia prevention is not knowledge — it is access and habit formation. A person does not need a gym membership or a personal trainer. They need an activity they can do at home, and one they genuinely enjoy.

"It is never too late to start a fitness routine," the researchers concluded. "But for the intervention to be truly sustainable, it needs to be an activity that the individual genuinely enjoys."

## The Eight Other Risk Factors

While the study focused on exercise, Salisbury's framework identifies 14 modifiable risk factors in total. Beyond the six that exercise addresses, the remaining eight include hearing loss, smoking, excessive alcohol use, social isolation, traumatic brain injury, air pollution exposure, limited education, and poor diet quality. Each of these carries its own evidence base for contributing to dementia risk.

The Lancet Commission on Dementia Prevention, which has been building a similar framework since 2017, estimates that up to 45 percent of dementia cases worldwide could be prevented or delayed if all modifiable risk factors were addressed. The Minnesota study sharpens this further by showing that exercise alone — if maintained — can reach more than 40 percent of that modifiable risk.

## What This Means for NRIs

For the Indian diaspora, this research carries particular weight. Dementia prevalence in India is projected to nearly triple by 2050, reaching an estimated 11 million cases — yet awareness, screening, and infrastructure remain severely limited. Many NRI families are already navigating early cognitive decline in aging parents back home, often discovering it too late for meaningful intervention.

Meanwhile, the diaspora's own risk profile is shaped by the same metabolic factors the study highlights. South Asians in the US have among the highest rates of type 2 diabetes, hypertension, and metabolic syndrome in any ethnic group — precisely the conditions that exercise most effectively mitigates.

The actionable message is clear and surprisingly precise: 150 minutes of moderate aerobic exercise per week — combined with two sessions of strength training — addresses more dementia risk factors than any drug currently available. For NRI families caring for parents in India, encouraging even modest daily walking routines through video calls or wearable devices could meaningfully change outcomes. For young South Asian professionals, starting a sustainable exercise habit in their thirties is not a vanity project — it is a neurological insurance policy.

*Sources: University of Minnesota School of Nursing; NBC Palm Springs; The Lancet Commission on Dementia Prevention; Alzheimer's Association*"""

articles.append({
    "slug": art2_slug,
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "category": "lifestyle-health",
    "vertical": "brain-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now_utc,
    "sources": json.dumps(["University of Minnesota School of Nursing", "NBC Palm Springs", "The Lancet Commission on Dementia Prevention", "Alzheimer's Association"]),
    "diaspora_angle": "Dementia in India is projected to nearly triple by 2050, and South Asians carry elevated metabolic risk — exercise is the single most accessible intervention for NRI families and aging parents.",
    "image_search_topic": "older adult exercising brain health cognitive fitness walking",
    "image_person": None,
    "image_caption_text": "An older adult exercises outdoors, an activity linked to significant dementia prevention benefits",
})

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 3: Kotak Mahindra Bank CEO exit / markets-finance
# ═══════════════════════════════════════════════════════════════════

art3_slug = "kotak-mahindra-bank-ceo-ashok-vaswani-exit-succession-stock-drop-nri-investor-20260629"
art3_headline = "Kotak Mahindra Bank's CEO Just Said He Won't Stay — and the Stock Dropped 3.3% as a Succession Battle Begins"
art3_subheadline = "Ashok Vaswani, who took over from founder Uday Kotak just three years ago, informed the board he will not seek reappointment when his term ends in December 2026 — leaving India's fourth-largest private bank searching for its third CEO in four years."

art3_body = """Kotak Mahindra Bank had barely stabilized after its founder stepped away. Now it faces another leadership vacuum.

Ashok Vaswani, the managing director and CEO of India's fourth-largest private lender by market capitalization, informed the board on Saturday that he will not seek reappointment when his current term ends on December 31, 2026, citing personal reasons. The bank confirmed the decision in an exchange filing and said it has formally initiated the succession process.

The market's response was swift. Kotak Mahindra Bank shares fell 3.3 percent on Monday to ₹395.50, hitting an intraday low of ₹394.10 on the NSE. Heavy volumes — 1.32 crore shares worth ₹529 crore — underscored the anxiety. The stock is now down nearly 10 percent year-to-date and has underperformed the Nifty 50 over one, three, and five-year horizons.

## A Short, Turbulent Tenure

Vaswani's exit after a single three-year term marks an unusually brief chapter in the bank's history. He took over on January 1, 2024, after founder Uday Kotak stepped down from the role he had held since the bank's inception as a shadow lender in 1985. Vaswani came from Barclays, where he led the UK consumer bank, and his appointment was seen as a deliberate break from Kotak's founder-led legacy — a signal that the bank was professionalizing its leadership.

But the transition was anything but smooth. Several senior executives departed shortly after Vaswani took charge. Within months, the Reserve Bank of India barred the bank from onboarding new online customers and issuing credit cards due to IT infrastructure gaps — a regulatory blow that Vaswani himself acknowledged had damaged the bank's "franchise and reputation." Stress in the broader microfinance sector forced a pullback in growth. And the stock, which had rallied on the promise of fresh professional management, went sideways.

Despite these headwinds, the bank's financial performance remained solid. In the fourth quarter of FY2025-26, Kotak Mahindra Bank reported net profit up 13 percent year-on-year to ₹4,027 crore, supported by stronger lending and lower provisions.

## The Succession Race

The bank does not currently have a Deputy Managing Director — a gap that makes the succession question more complicated. Two executives are widely seen as internal candidates:

**Anup Saha**, who was laterally hired as Executive Director in January 2026 after serving as MD and CEO of Bajaj Finance. Saha brings deep expertise in consumer lending, data analytics, and digital transformation. He currently oversees the consumer banking portfolio — the bank's largest business vertical at nearly ₹2.5 lakh crore.

**Paritosh Kashyap**, a long-serving Kotak executive who was elevated to Executive Director in May 2025. He represents institutional continuity.

The bench has been thinned by departures. Shanti Ekambaram, the former Deputy MD, retired in October 2025. KVS Manian, the former Joint MD, left to become MD and CEO of Federal Bank in September 2024. Analysts say the frequency of senior exits — three in two years — is itself a concern.

ICICI Securities retained its Buy rating with a target price of ₹480, calling any major correction a buying opportunity. The brokerage noted that current valuations sit approximately two standard deviations below the historical mean — a signal that much of the leadership uncertainty is already priced in. But it also flagged that the overhang from succession uncertainty could persist for months.

Nuvama Institutional Equities' Anand Dama told Reuters that selecting a strong long-term replacement — whether internal or external — will be critical for reassuring investors.

## Why NRI Investors Should Watch This Closely

Kotak Mahindra Bank is one of the most widely held Indian financial stocks among NRI investors, featuring prominently in India-focused mutual funds, ETFs, and direct equity portfolios. Its premium valuation has historically been justified by superior asset quality, conservative risk management, and the perceived stability of its leadership.

The CEO transition raises a set of practical questions. Will the next leader accelerate or slow the bank's digital transformation? Will Kotak pursue the M&A strategy — it had expressed interest in IDBI Bank and Deutsche Bank India's retail assets — or pull back? And critically, will the RBI's technology concerns, which led to the 2024 regulatory action, be fully resolved before the new CEO takes over?

For NRI investors holding Kotak in their India portfolio, the near-term playbook depends on time horizon. ICICI Securities' view that a correction creates an entry point is predicated on the bank's franchise quality surviving the leadership churn. The longer view is that India's private banking sector remains structurally attractive — and a ₹4 lakh crore market-cap bank trading below its historical valuation band is, for patient capital, more opportunity than threat.

But the pattern of one-term CEOs and serial senior exits is worth monitoring. A bank that cannot retain its top leadership for more than three years signals either a governance issue or a cultural one — and either would demand a higher risk premium.

*Sources: Outlook Business; Reuters; People Matters; ICICI Securities; NSE India; The Hindu Business Line*"""

articles.append({
    "slug": art3_slug,
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "body": art3_body,
    "category": "markets-finance",
    "vertical": "banking",
    "status": "review",
    "is_editorial": False,
    "published_at": now_utc,
    "sources": json.dumps(["Outlook Business", "Reuters", "People Matters", "ICICI Securities", "NSE India", "The Hindu Business Line"]),
    "diaspora_angle": "Kotak Mahindra Bank is one of the most widely held Indian stocks among NRI investors — the CEO transition and valuation correction raise key portfolio questions.",
    "image_search_topic": "Kotak Mahindra Bank headquarters Mumbai",
    "image_person": "Ashok Vaswani banker",
    "image_caption_text": "Ashok Vaswani, outgoing CEO of Kotak Mahindra Bank",
})


# ── MAIN ────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print(f"Videshi Lifestyle/Markets Writer — {now_utc}")
    print("=" * 60)

    for art_data in articles:
        slug = art_data["slug"]
        headline = art_data["headline"]
        topic = art_data.pop("image_search_topic")
        person = art_data.pop("image_person")
        caption_text = art_data.pop("image_caption_text")

        print(f"\n{'─'*60}")
        print(f"Article: {headline[:70]}...")
        print(f"Slug: {slug}")
        print(f"Category: {art_data['category']}")

        # Source image
        print(f"\n  Sourcing image...")
        img_url, attribution, source = source_image(slug, headline, topic, person)

        if img_url:
            art_data["image_url"] = img_url
            art_data["image_caption"] = caption_text
            art_data["image_attribution"] = attribution
            print(f"  ✓ Image: {img_url[:80]}...")
        else:
            print(f"  ⚠ No image — inserting without hero")

        # Validate
        body = art_data["body"]
        word_count = len(body.split())
        print(f"  Word count: {word_count}")
        if word_count < 400:
            print(f"  ✗ SKIPPING — body too short ({word_count} words)")
            continue

        if len(headline) > 200:
            print(f"  ⚠ Headline too long ({len(headline)} chars), trimming")
            art_data["headline"] = headline[:197] + "..."

        if len(art_data.get("subheadline", "")) < 15:
            print(f"  ✗ SKIPPING — subheadline too short")
            continue

        # Insert
        print(f"  Inserting article...")
        art_id = insert_article(art_data)

        if art_id:
            print(f"  ✓ SUCCESS — {slug}")
        else:
            print(f"  ✗ FAILED — {slug}")

    print(f"\n{'='*60}")
    print(f"Writer complete.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
