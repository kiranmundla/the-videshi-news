#!/usr/bin/env python3
"""Lifestyle-health & markets-finance writer for The Videshi — June 6, 2026 run"""

import json, os, sys, uuid, requests, subprocess, io, time
from datetime import datetime, timezone
from PIL import Image

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    if line.startswith('export '):
                        line = line[7:]
                    k, v = line.split('=', 1)
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

# ── Image helpers ──

def fetch_wikipedia_person_image(person_name):
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
    try:
        time.sleep(2)  # Rate limit protection
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query", "generator": "search",
                "gsrsearch": search_query, "gsrnamespace": "6",
                "gsrlimit": str(limit), "prop": "imageinfo",
                "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
            },
            headers={"User-Agent": UA}, timeout=15
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
                    "height": ii.get("height", 0)
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []

def fetch_pexels_image(query):
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        result = subprocess.run(
            ["curl", "-sS",
             f"https://api.pexels.com/v1/search?query={encoded_query}&per_page=3",
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        if result.stdout.strip():
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
            else:
                print(f"  ⚠ Pexels: no photos for '{query}'")
        else:
            print(f"  ⚠ Pexels: empty response")
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def upload_to_supabase(img_url, filename):
    """Download image, compress, upload to Supabase storage."""
    try:
        print(f"  Downloading: {img_url[:80]}...")
        time.sleep(2)  # Rate limit for Wikimedia
        r = requests.get(img_url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 429:
            print(f"  ⚠ Rate limited, waiting 5s and retrying...")
            time.sleep(5)
            r = requests.get(img_url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Download failed: HTTP {r.status_code}")
            return None
        ct = r.headers.get('Content-Type', '')
        if not ct.startswith('image/'):
            print(f"  ⚠ Not an image: {ct}")
            return None
        raw = r.content
        if len(raw) < 5000:
            print(f"  ⚠ Image too small: {len(raw)} bytes")
            return None

        compressed = compress_image(raw)
        print(f"  Compressed: {len(raw)} → {len(compressed)} bytes")

        # Upload to Supabase storage
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true"
            },
            data=compressed,
            timeout=30
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {resp.status_code} {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return None

def insert_article(article):
    """Insert article into Supabase."""
    # Remove None values to let DB defaults apply
    clean = {k: v for k, v in article.items() if v is not None}
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=clean,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            art_id = data[0].get('id', 'unknown')
            print(f"  ✓ Article inserted: {art_id}")
            return art_id
        print(f"  ✓ Article inserted (no ID returned)")
        return True
    else:
        print(f"  ⚠ Insert failed: {r.status_code} {r.text[:300]}")
        return None


# ── ARTICLE 1: GRWD5769 wonder pill ──
def write_grwd5769_article():
    print("\n═══ Article 1: GRWD5769 Cancer Wonder Pill ═══")
    slug = "grwd5769-wonder-pill-shrinks-tumours-six-cancer-types-asco-2026-south-asian-20260606"

    # Image sourcing
    print("Sourcing image...")
    candidates = []

    # Wikimedia Commons: cancer immunotherapy
    commons = fetch_wikimedia_commons_images("immunotherapy cancer treatment")
    for c in commons[:2]:
        candidates.append({"url": c["url"], "source": "wikimedia_commons"})

    # Wikimedia Commons: ASCO oncology
    commons2 = fetch_wikimedia_commons_images("oncology clinical trial")
    for c in commons2[:2]:
        candidates.append({"url": c["url"], "source": "wikimedia_commons"})

    # Pexels
    pexels = fetch_pexels_image("cancer research laboratory immunotherapy")
    if pexels:
        candidates.append({"url": pexels, "source": "pexels"})

    img_url = None
    img_attribution = "Pexels"
    for c in candidates:
        uploaded = upload_to_supabase(c["url"], f"{slug}.jpg")
        if uploaded:
            img_url = uploaded
            img_attribution = "Wikimedia Commons" if c["source"] == "wikimedia_commons" else "Pexels"
            break

    body = """A twice-daily pill developed by Oxford scientists has shrunk tumours by at least 30 per cent across six of the most common and treatment-resistant cancer types, according to early trial results presented at the American Society of Clinical Oncology's annual meeting in Chicago this week.

The drug, called GRWD5769, was tested in 83 patients with cervical, bladder, liver, bowel, lung and head-and-neck cancers across trial sites in the United Kingdom, France, Spain and Australia. Every participant had already failed to respond to existing treatments — most had run out of options entirely. Crucially, immunotherapy had either never worked or had stopped working for all of them.

## How the Drug Works

Immunotherapy has transformed cancer care over the past decade by enlisting the body's own T-cells to hunt and destroy tumour cells. But the treatment fails in roughly two-thirds of patients because many tumours learn to hide from the immune system.

They do this by manipulating an enzyme called ERAP1 — endoplasmic reticulum aminopeptidase 1 — which alters the proteins displayed on the tumour's surface. Without the right markers, T-cells simply cannot recognise the cancer.

GRWD5769, developed by Greywolf Therapeutics in Oxford, inhibits ERAP1 and strips away what researchers describe as the tumour's "invisibility cloak." Once exposed, the cancer becomes visible to T-cells again, allowing a standard immunotherapy drug, cemiplimab, to do its work.

The drug is taken in three-week cycles — three weeks on, three weeks off — to prevent T-cell exhaustion and generate alternating antigen profiles that broaden the immune response.

## The Numbers

Among the 83 patients in the phase 1b EMITT-1 trial, tumours shrank in 26. Fifteen of those experienced reductions of at least 30 per cent, with some shrinking by as much as 95 per cent.

Disease was halted for at least six months in 18 per cent of cervical cancer patients, 32 per cent of liver cancer patients, 36 per cent of bladder cancer patients, 38 per cent of head-and-neck cancer patients, 51 per cent of bowel cancer patients and 55 per cent of lung cancer patients.

The bowel cancer results are particularly significant. Microsatellite-stable colorectal cancer — the subtype studied — rarely responds to immunotherapy at all. The 51 per cent disease control rate in this group is, as one independent oncologist at the conference described it, "a clinically meaningful signal."

## Why South Asians Should Pay Attention

Cancer incidence among South Asians in the West has been rising steadily. Head-and-neck cancers, liver cancers and colorectal cancers are all disproportionately common in the diaspora — driven by dietary shifts, alcohol consumption patterns and delayed screening. The Indian subcontinent also has among the world's highest rates of cervical cancer.

For the millions of NRIs who navigate between two healthcare systems, a pill-based treatment that can be taken at home rather than requiring intravenous infusions at a hospital represents a fundamental shift in how cancer could be managed.

## What Comes Next

Professor Fiona Thistlethwaite, the trial's principal investigator at the Christie NHS Foundation Trust in Manchester, called the results "very impressive" for a tablet-form drug. "It's early days, and we need further studies, but this is a new drug with a new mechanism that clearly helps immunotherapy perform more effectively," she said.

Stage 2 cohort expansions are now underway, with a randomised phase 2 study planned next. If the drug maintains its safety-to-efficacy profile — the trial reported only one serious adverse event among all 83 patients — it could reach clinical practice within the next few years.

Dr Samuel Godfrey of Cancer Research UK, who was not involved in the study, offered a measured endorsement. "It is unusual to see such outcomes in patients whose cancers have already stopped responding to treatment, particularly across several hard-to-treat cancer types," he said. "Larger trials will be needed to determine whether this approach can deliver lasting benefits."

For a diaspora community with elevated cancer risks and strong ties to healthcare innovation on both sides of the Atlantic, this is a trial worth watching closely.

---

*Sources: ASCO 2026 presentation (EMITT-1 trial); The Guardian; MedicalBrief; The Times*"""

    article = {
        "headline": "A British-Made Pill Just Shrank Tumours Across Six Cancer Types. Every Patient Had Run Out of Options.",
        "subheadline": "The Oxford-developed drug GRWD5769 strips away cancer's 'invisibility cloak,' allowing immunotherapy to work in patients where it had failed. The ASCO results are early but remarkable.",
        "body": body,
        "slug": slug,
        "category": "lifestyle-health",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_caption": "Cancer researchers at a clinical trial laboratory studying immunotherapy treatments",
        "image_attribution": img_attribution,
        "is_editorial": False,
        "vertical": "culture",
        "sources": json.dumps(["ASCO 2026 (EMITT-1 trial)", "The Guardian", "MedicalBrief", "The Times"]),
    }

    return insert_article(article)


# ── ARTICLE 2: Strength Training ──
def write_strength_training_article():
    print("\n═══ Article 2: Strength Training Longevity ═══")
    slug = "strength-training-90-minutes-week-lower-death-risk-13-percent-bjsm-south-asian-20260606"

    # Image sourcing
    print("Sourcing image...")
    candidates = []

    # Wikimedia Commons: weight training
    commons = fetch_wikimedia_commons_images("weight training dumbbell exercise")
    for c in commons[:2]:
        candidates.append({"url": c["url"], "source": "wikimedia_commons"})

    commons2 = fetch_wikimedia_commons_images("resistance training gym")
    for c in commons2[:2]:
        candidates.append({"url": c["url"], "source": "wikimedia_commons"})

    pexels = fetch_pexels_image("strength training weights gym fitness")
    if pexels:
        candidates.append({"url": pexels, "source": "pexels"})

    img_url = None
    img_attribution = "Pexels"
    for c in candidates:
        uploaded = upload_to_supabase(c["url"], f"{slug}.jpg")
        if uploaded:
            img_url = uploaded
            img_attribution = "Wikimedia Commons" if c["source"] == "wikimedia_commons" else "Pexels"
            break

    body = """Ninety minutes of strength training a week — that is roughly 13 minutes a day — is enough to lower your risk of dying from any cause by 13 per cent, according to the largest and longest study ever conducted on the subject.

The research, published in the British Journal of Sports Medicine on June 2, tracked 147,374 men and women over 30 years across three major US health studies. It is the most comprehensive evidence to date that lifting weights does not just build muscle. It extends life.

## The Sweet Spot

The study found that people who did between 90 and 120 minutes of strength training per week had a 13 per cent lower risk of death from any cause compared to those who did none.

The protection was even stronger for specific diseases. Cardiovascular death risk — from heart attacks, strokes and related conditions — dropped by 19 per cent. Neurological disease mortality, including conditions like Alzheimer's and Parkinson's, fell by 27 per cent.

Crucially, no additional benefit was observed above 120 minutes per week. The curve flattened. Two hours was enough.

## What Counts as Strength Training

The researchers defined strength training broadly: any exercise that uses weights or bodyweight resistance. Push-ups, squats, lunges, dumbbell curls, resistance bands, kettlebells and weight machines all qualify. You do not need a gym membership or expensive equipment.

This matters for the millions of deskbound NRIs in tech, finance and consulting who spend their working hours seated and their evenings too tired for a full workout. Thirteen minutes a day of bodyweight exercises — push-ups before coffee, squats during a call, lunges in the evening — meets the threshold.

## The Combination Effect

The strongest finding may be the synergy between strength training and aerobic exercise. Participants who did high levels of both — think regular running or cycling combined with weight training — had the lowest mortality risk of any group in the study.

The authors wrote that "engaging in sufficient aerobic or resistance training alone is linked to lower mortality," but added that the "lowest risk" of early death was observed only when participants did high levels of both.

For South Asians, this is particularly relevant. The community carries a disproportionate burden of cardiovascular disease, Type 2 diabetes and metabolic syndrome. Exercise is one of the few interventions that addresses all three simultaneously. But the cultural emphasis has historically favoured walking and yoga over resistance training.

## The Neurological Surprise

The 27 per cent reduction in neurological disease mortality was the study's most unexpected finding. Strength training has traditionally been associated with musculoskeletal benefits — stronger bones, better balance, reduced falls in older adults. Its protective effect on the brain is a more recent discovery.

Emerging research suggests that resistance exercise stimulates the release of brain-derived neurotrophic factor (BDNF), a protein that supports the survival of existing neurons and encourages the growth of new ones. The effect appears to be distinct from what aerobic exercise provides, which may explain why the combination of both yields the strongest protection.

For a diaspora population that is ageing rapidly in countries where dementia care is expensive and culturally isolating, this is data worth acting on.

## The Practical Takeaway

The study was observational, not a randomised trial, which means it cannot prove direct causation. Self-reported exercise data is also imperfect. But with 147,374 participants and 30 years of follow-up, the signal is robust.

The message is simple: if you are doing zero strength training, starting any amount helps. If you are already active, adding 90 minutes of resistance work per week may be the highest-return health investment you can make. And if you are doing more than two hours, there is no measurable benefit to doing more.

A pair of dumbbells and 13 minutes a day. The data suggests that may be enough to change your odds.

---

*Sources: British Journal of Sports Medicine (June 2, 2026); USA Today; Diabetes.co.uk; Knowridge Science*"""

    article = {
        "headline": "Ninety Minutes of Weight Training a Week Lowers Your Risk of Dying by 13 Per Cent. The Study Tracked 147,000 People for 30 Years.",
        "subheadline": "The largest-ever study on strength training and longevity found a sweet spot of 90 to 120 minutes a week — with the biggest surprise being a 27 per cent drop in neurological disease deaths.",
        "body": body,
        "slug": slug,
        "category": "lifestyle-health",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_caption": "A person performing dumbbell strength training exercises at a gym",
        "image_attribution": img_attribution,
        "is_editorial": False,
        "vertical": "culture",
        "sources": json.dumps(["British Journal of Sports Medicine", "USA Today", "Diabetes.co.uk", "Knowridge Science"]),
    }

    return insert_article(article)


# ── ARTICLE 3: Fitch / Oil / India ──
def write_fitch_oil_article():
    print("\n═══ Article 3: Fitch Downgrade + Oil Shock ═══")
    slug = "fitch-cuts-global-growth-oil-shock-hormuz-india-lpg-crisis-nri-20260606"

    # Image sourcing
    print("Sourcing image...")
    candidates = []

    # Wikimedia Commons: Strait of Hormuz or oil tanker
    commons = fetch_wikimedia_commons_images("Strait of Hormuz oil tanker")
    for c in commons[:2]:
        candidates.append({"url": c["url"], "source": "wikimedia_commons"})

    commons2 = fetch_wikimedia_commons_images("oil refinery India petroleum")
    for c in commons2[:2]:
        candidates.append({"url": c["url"], "source": "wikimedia_commons"})

    pexels = fetch_pexels_image("oil tanker ship ocean petroleum")
    if pexels:
        candidates.append({"url": pexels, "source": "pexels"})

    img_url = None
    img_attribution = "Pexels"
    for c in candidates:
        uploaded = upload_to_supabase(c["url"], f"{slug}.jpg")
        if uploaded:
            img_url = uploaded
            img_attribution = "Wikimedia Commons" if c["source"] == "wikimedia_commons" else "Pexels"
            break

    body = """Fitch Ratings cut its global growth forecast for 2026 on Friday, warning that the oil shock triggered by the US-Iran conflict and the 14-week closure of the Strait of Hormuz has inflicted broader damage on the world economy than initially expected. For India — and for the millions of NRIs whose financial lives straddle both sides of the equation — the numbers are getting harder to ignore.

## The Fitch Downgrade

The ratings agency now expects global growth of 2.4 per cent this year, down from its earlier projection of 2.6 per cent. It raised its average Brent crude forecast for 2026 to $87 per barrel, up sharply from $70 previously.

The US economy is now expected to grow 1.9 per cent and the eurozone just 0.9 per cent. China was the lone exception — Fitch raised its forecast to 4.6 per cent after a stronger first quarter.

"Forecast cuts have been widespread as higher inflation squeezes real wages, dampens consumption and raises companies' input costs," the Fitch report said. The agency expects the Federal Reserve and the Bank of England to hold rates through 2026 before cutting in 2027. The ECB may actually hike in June before reversing next year.

Under an adverse scenario where oil averages $100 per barrel, US growth could drop to 0.8 per cent and eurozone growth to 0.3 per cent.

## India's Acute Vulnerability

India imports roughly 89 per cent of its crude oil, and before the Strait of Hormuz closure in early March, 45 per cent of those imports — along with half its LNG and 90 per cent of its LPG — passed through the strait.

The impact has been immediate and tangible. According to the Atlantic Council, India's policymakers are scrambling to find replacement supplies for constrained energy flows. The Indian crude oil basket stood at $100.13 per barrel as of June 3, with the monthly average at $98.12 — levels not seen since 2022.

LPG has been hit hardest. India sources nearly 90 per cent of its cooking gas from West Asia. On Thursday, a joint secretary at the Ministry of Petroleum told reporters that state-run oil marketing companies are absorbing an under-recovery of Rs 700 on every LPG cylinder sold, with cumulative daily losses running at Rs 550 crore.

Goldman Sachs, in a separate note on Friday, estimated that global oil demand fell by 4 to 5 million barrels per day in April — a 4 to 5 per cent decline — driven by the Hormuz closure, weak Chinese consumption and soft European retail fuel sales. Brent settled at $93.09 on Friday, down nearly $2 on the day.

## What This Means for NRIs

The cascading effects hit NRIs from multiple directions.

**The rupee.** Higher oil prices widen India's import bill and put downward pressure on the rupee. The currency has already hit historic lows against the dollar. Every $10 rise in crude adds roughly $20 billion to India's annual import bill and shaves 0.3 to 0.4 per cent off GDP growth while adding 0.4 per cent to inflation.

**Remittances.** A weaker rupee means NRI remittances buy more in India — a temporary silver lining. But if inflation erodes purchasing power at home, the real value of those transfers shrinks.

**Investments.** Indian equities have so far held up better than many emerging markets, buoyed by domestic flows and a strong fiscal year. But Fitch warned that if the adverse oil scenario materialises, equity markets could fall 10 per cent globally, and credit conditions would tighten. NRIs with significant exposure to Indian mutual funds, NRE deposits or real estate should be watching the oil price as closely as they watch the Sensex.

**H-1B and immigration.** If US growth slows materially — Fitch's adverse case puts it at 0.8 per cent — hiring freezes and layoffs in tech could return. The last time oil-driven stagflation fears gripped the US, in 2022, the tech sector shed hundreds of thousands of jobs. Workers on H-1B visas, who have 60 days to find new employment if laid off, are the most exposed.

## The One Bright Spot

Fitch noted that one factor is cushioning the global drag: the surge in artificial intelligence spending. "The world is in the midst of a very pronounced boom in global spending on IT, and that is cushioning the impact on activity in the near term, particularly in Asia," said Brian Coulton, Fitch's chief economist.

For India's IT sector and the NRI professionals who staff it, this is a double-edged reality. AI spending is keeping tech employment buoyant even as the broader macro picture darkens. How long that continues depends on whether corporate clients maintain AI budgets through a slowdown — a question no one can answer yet.

The oil shock is no longer a short-term disruption. At 14 weeks and counting, with Fitch saying a Hormuz reopening is unlikely before July, it has become a structural feature of the global economy in 2026. Plan accordingly.

---

*Sources: Fitch Ratings (June 2026); Wall Street Journal; Reuters; Atlantic Council; LiveMint; Goldman Sachs*"""

    article = {
        "headline": "Fitch Just Cut Global Growth Forecasts. Oil Is Near $100. India's LPG Crisis Is Getting Worse. Here Is the Full Picture.",
        "subheadline": "The 14-week Strait of Hormuz closure is no longer a short-term disruption. From the rupee to remittances to H-1B visa holders, every NRI is exposed.",
        "body": body,
        "slug": slug,
        "category": "markets-finance",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_caption": "An oil tanker navigating through shipping lanes critical to global energy supply",
        "image_attribution": img_attribution,
        "is_editorial": False,
        "vertical": "economy",
        "sources": json.dumps(["Fitch Ratings", "Wall Street Journal", "Reuters", "Atlantic Council", "LiveMint", "Goldman Sachs"]),
    }

    return insert_article(article)


# ── Main ──
if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi — Lifestyle/Markets Writer Run")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    results = []

    r1 = write_grwd5769_article()
    results.append(("GRWD5769 Cancer Pill", r1))

    r2 = write_strength_training_article()
    results.append(("Strength Training", r2))

    r3 = write_fitch_oil_article()
    results.append(("Fitch Oil Shock", r3))

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    for name, result in results:
        status = "✓ SUCCESS" if result else "✗ FAILED"
        print(f"  {status}: {name}")
    
    failed = sum(1 for _, r in results if not r)
    if failed:
        print(f"\n⚠ {failed} article(s) failed")
        sys.exit(1)
    else:
        print("\n✓ All 3 articles published successfully")
