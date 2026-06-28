#!/usr/bin/env python3
"""Lifestyle-Health & Markets-Finance writer – 2026-06-28 run"""

import os, sys, json, uuid, requests, subprocess, io, re, hashlib
from datetime import datetime, timezone
from urllib.parse import quote, quote_plus

# ── env ──────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:]
            k, _, v = line.partition('=')
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k.strip(), v)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')
UA = 'TheVideshi/1.0 (thevideshi.com)'

# ── helpers ──────────────────────────────────────────────────────────────
def sb_headers():
    return {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation',
    }

def sb_insert(table, row):
    r = requests.post(f'{SUPABASE_URL}/rest/v1/{table}',
                      headers=sb_headers(), json=row, timeout=30)
    if r.status_code not in (200, 201):
        print(f'  ⚠ insert error {r.status_code}: {r.text[:300]}')
        return None
    data = r.json()
    return data[0] if isinstance(data, list) else data

def fetch_wikipedia_person_image(person_name):
    encoded = quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f'https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}',
            headers={'User-Agent': UA}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            img = data.get('originalimage', {}).get('source') or data.get('thumbnail', {}).get('source')
            if img:
                print(f'  ✓ Wikipedia image for "{person_name}": {img[:80]}...')
                return img
    except Exception as e:
        print(f'  ⚠ Wikipedia error for "{person_name}": {e}')
    return None

def fetch_wikimedia_commons(query, limit=5):
    params = {
        'action': 'query', 'generator': 'search',
        'gsrsearch': query, 'gsrnamespace': '6', 'gsrlimit': str(limit),
        'prop': 'imageinfo', 'iiprop': 'url|size|mime',
        'iiurlwidth': '1200', 'format': 'json',
    }
    try:
        r = requests.get('https://commons.wikimedia.org/w/api.php',
                         params=params, headers={'User-Agent': UA}, timeout=15)
        if r.status_code == 200:
            pages = r.json().get('query', {}).get('pages', {})
            results = []
            for pid, page in pages.items():
                ii = page.get('imageinfo', [{}])[0]
                mime = ii.get('mime', '')
                if not mime.startswith('image/') or mime == 'image/svg+xml':
                    continue
                if ii.get('width', 0) < 300:
                    continue
                results.append({
                    'url': ii.get('thumburl') or ii.get('url', ''),
                    'original_url': ii.get('url', ''),
                    'title': page.get('title', ''),
                    'width': ii.get('width', 0),
                    'height': ii.get('height', 0),
                })
            return results
    except Exception as e:
        print(f'  ⚠ Commons error: {e}')
    return []

# ── commons relevance gate ──────────────────────────────────────────────
_COMMONS_STOP = {
    'the','a','an','of','in','on','at','to','for','and','or','with','as','by',
    'from','is','are','was','were','be','new','says','after','over','amid',
    'how','why','what','2024','2025','2026','india','indian','us','usa',
    'american','uk','first','more','than','people','man','woman','group',
    'day','year','top','big','set','get','make','makes','made','you','your',
    'they','them','this','that','social','media','using','use',
}

def _keywords(text):
    toks = re.findall(r'[A-Za-z][A-Za-z\'-]+', text or '')
    return [t.lower() for t in toks if len(t) >= 4 and t.lower() not in _COMMONS_STOP]

def commons_relevance_ok(title, headline, topic=''):
    title_l = (title or '').lower()
    if not title_l:
        return False
    kws = set(_keywords(headline)) | set(_keywords(topic))
    if not kws:
        return True
    return any(kw in title_l for kw in kws)

def fetch_pexels(query):
    if not PEXELS_KEY:
        return None
    try:
        cmd = [
            'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
            f'https://api.pexels.com/v1/search?query={quote_plus(query)}&per_page=3',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                return photos[0]['src']['large2x']
    except Exception as e:
        print(f'  ⚠ Pexels error: {e}')
    return None

def download_image(url):
    """Download image bytes, trying curl first."""
    try:
        cmd = ['curl', '-sS', '-L', '-A', UA, '-o', '-', url]
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        if result.returncode == 0 and len(result.stdout) > 5000:
            return result.stdout
    except:
        pass
    try:
        r = requests.get(url, headers={'User-Agent': UA}, timeout=20)
        if r.status_code == 200 and len(r.content) > 5000:
            return r.content
    except:
        pass
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

def upload_to_supabase(jpeg_bytes, filename):
    r = requests.post(
        f'{SUPABASE_URL}/storage/v1/object/article-images/{filename}',
        headers={
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'image/jpeg',
            'x-upsert': 'true',
        },
        data=jpeg_bytes, timeout=60)
    if r.status_code not in (200, 201):
        print(f'  ⚠ Upload failed {r.status_code}: {r.text[:200]}')
        return None
    return f'{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}'

def source_and_upload_image(slug, search_queries, person_name=None, headline=''):
    """Multi-source image search, compress, upload. Returns (url, attribution) or (None, None)."""
    candidates = []

    # Source 1: Wikipedia person image
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({'url': wiki_img, 'source': 'wikipedia'})

    # Source 2: Wikimedia Commons
    for q in search_queries[:2]:
        results = fetch_wikimedia_commons(q)
        relevant = [r for r in results if commons_relevance_ok(r['title'], headline, q)]
        for r in relevant[:2]:
            candidates.append({'url': r['url'], 'source': 'wikimedia_commons', 'title': r['title']})
        if relevant:
            break

    # Source 3: Pexels fallback (not for person articles)
    if not person_name and not candidates:
        for q in search_queries[:2]:
            pex = fetch_pexels(q)
            if pex:
                candidates.append({'url': pex, 'source': 'pexels'})
                break

    if not candidates:
        print(f'  ⚠ No image found for {slug}')
        return None, None

    # Try candidates in order
    for c in candidates:
        print(f'  → Trying {c["source"]}: {c["url"][:80]}...')
        raw = download_image(c['url'])
        if not raw:
            print(f'    ⚠ Download failed, trying next')
            continue
        compressed = compress_image(raw)
        size_kb = len(compressed) / 1024
        print(f'    Compressed: {size_kb:.0f} KB')
        if size_kb < 10:
            print(f'    ⚠ Too small, skipping')
            continue
        final_url = upload_to_supabase(compressed, f'{slug}.jpg')
        if final_url:
            attr = 'Wikimedia Commons' if c['source'] in ('wikipedia', 'wikimedia_commons') else 'Pexels'
            print(f'    ✓ Uploaded: {final_url[:60]}...')
            return final_url, attr
    return None, None


# ══════════════════════════════════════════════════════════════════════════
# ARTICLE 1: HPV Vaccine — Zero Cervical Cancer Deaths
# ══════════════════════════════════════════════════════════════════════════

art1_slug = 'hpv-vaccine-zero-cervical-cancer-deaths-england-lancet-india-nationwide-campaign-diaspora-20260628'
art1_headline = 'The HPV Vaccine Has Reduced Cervical Cancer Deaths to Zero in Young Women — and India Is Finally Racing to Catch Up'
art1_subheadline = 'A landmark Lancet study finds 100% reduction in cervical cancer deaths among vaccinated women in England, while India — home to a quarter of the world\'s cervical cancer fatalities — launches its largest-ever immunisation drive'

art1_body = """India accounts for one in every four cervical cancer deaths on the planet. A woman is diagnosed every four minutes; another dies every seven. But a study published this month in *The Lancet* offers the most powerful evidence yet that this toll is not inevitable — and that a single vaccine, given early enough, can bring the death count to zero.

The study, led by Peter Sasieni, professor of cancer epidemiology at Queen Mary University of London, analysed English data from 2001 to 2024 across three age cohorts. Among women aged 20 to 24 — the first group to have been widely vaccinated at age 12 or 13 — there was not a single cervical cancer death for five consecutive years. A 100% reduction. In the 25-to-29 group, the result was the same: zero deaths. Among women aged 30 to 34, who had less access to the vaccine, deaths still fell by 63%.

"I was expecting to see a fall in deaths from cervical cancer, but I was not expecting to see zero deaths for five years running," Sasieni said. "The public health community set out to greatly reduce cancer of the cervix and deaths from cancer of the cervix, and they have achieved just that."

## Why the vaccine works so well

The HPV vaccine — specifically the 9-valent Gardasil 9, which covers the virus types responsible for over 90% of cervical cancers — generates a durable immune response when administered before exposure. The Lancet findings are reinforced by a separate May 2026 analysis from the University of Minnesota's Center for Infectious Disease Research and Policy, which reviewed 121 studies worldwide and concluded that even a single vaccine dose can protect against HPV infection.

Andrea Tufano-Sugarman, a gynecologic oncologist at Memorial Sloan Kettering Cancer Center, called the level of effectiveness "stunning." The vaccine does not just prevent cancer — a May 2024 *British Medical Journal* study showed that girls vaccinated between ages 12 and 13 had an 83.9% reduction in cervical cancer diagnosis and a 94.3% reduction in CIN3, a precancerous condition.

## India's enormous gap — and a historic campaign

India reports over 120,000 new cervical cancer cases and nearly 80,000 deaths annually, according to WHO's GLOBOCAN report. One in every 50 girls born in India is expected to develop the disease in her lifetime. Yet until this year, HPV vaccination coverage in India was negligible.

On 28 February 2026, Prime Minister Modi launched India's first nationwide HPV vaccination campaign from Ajmer, Rajasthan. During a 90-day drive, 11.5 million girls aged 14 years are being administered the vaccine free of charge at government health facilities. WHO Director-General Tedros Adhanom Ghebreyesus called it "the largest free HPV vaccination campaign in history."

The vaccine being deployed is India's own Cervavac, developed by the Serum Institute of India — the same manufacturer that scaled COVID-19 vaccine production for the developing world. As of February 2026, 8.73 crore women had been screened for cervical cancer through the national NCD portal, though screening remains uneven outside urban centres.

## What NRIs should know

For diaspora families, the implications are immediate. The HPV vaccine is available in the United States (where completion rates hover around 64%), the UK (90%), Canada, and Australia. The CDC recommends vaccination at age 11 or 12 for both boys and girls, with catch-up dosing available through age 45. Yet misconceptions — about infertility, about sexual activity — continue to depress uptake even among well-educated communities.

The new data should settle any residual doubt. "For those currently eligible for the vaccine, this data turns a theoretical recommendation into a life-saving recommendation," says oncologist Stephanie Pinder. "If a child is vaccinated at age 12 or 13, their risk of dying from cervical cancer before age 30 is essentially zero."

For NRIs with family in India, especially in rural areas where screening access remains limited, the nationwide vaccination campaign offers a generational opportunity. The disease that kills an Indian woman every seven minutes may, within a decade, become as rare in India as it is about to become in England.

**Sources:** *The Lancet* (June 17, 2026); National Geographic; WHO GLOBOCAN 2022; Gavi/VaccinesWork; Press Information Bureau, Government of India (March 10, 2026); *British Medical Journal* (May 2024); University of Minnesota CIDRAP (May 2026)"""

art1_sources = json.dumps([
    {"name": "The Lancet", "url": "https://www.thelancet.com"},
    {"name": "National Geographic", "url": "https://www.nationalgeographic.com/health/article/cervical-cancer-hpv-vaccine-success"},
    {"name": "Gavi / VaccinesWork", "url": "https://www.gavi.org"},
    {"name": "Press Information Bureau, India", "url": "https://pib.gov.in"},
    {"name": "British Medical Journal", "url": "https://www.bmj.com"},
])

# ══════════════════════════════════════════════════════════════════════════
# ARTICLE 2: Any Level of Alcohol Increases Dementia Risk
# ══════════════════════════════════════════════════════════════════════════

art2_slug = 'any-alcohol-increases-dementia-risk-oxford-yale-cambridge-brain-volume-nature-health-diaspora-20260628'
art2_headline = 'Any Amount of Alcohol Raises Dementia Risk, a Massive New Study Confirms — and the "One Drink Is Fine" Belief Was an Illusion'
art2_subheadline = 'An Oxford-Yale-Cambridge-Harvard analysis of 560,000 adults and genetic data from 2.4 million people finds no safe level of drinking for brain health, while a separate Nature Health study links alcohol to 20 chronic conditions including multiple cancers'

art2_body = """For decades, a glass of red wine with dinner carried a faint halo of medical respectability. Moderate drinking, the conventional wisdom went, protected the heart and possibly the brain. A massive new study from researchers at Oxford, Yale, Cambridge, and Harvard has dismantled that idea with the largest genetic analysis of alcohol and dementia risk ever conducted — and the conclusion is unequivocal: there is no safe level.

The study analysed data from more than 560,000 adults aged 56 to 72, combined with genetic information from 2.4 million participants across 45 studies. Using Mendelian randomisation — a technique that uses genetic variants as natural experiments to separate cause from correlation — the team found that every tripling of weekly alcohol consumption raised dementia risk by 15%.

Alcohol was shown to reduce brain volume, damage myelin (the insulating sheath that allows neurons to communicate), and increase iron accumulation in the brain — a marker directly linked to Alzheimer's and Parkinson's disease.

## The "moderate drinking is protective" myth, debunked

"Our findings challenge the common belief that low levels of alcohol are beneficial for brain health," said Dr Anya Topiwala, the study's lead author and a senior clinical researcher at Oxford Population Health. "Genetic evidence offers no support for a protective effect — in fact, it suggests the opposite."

The apparent protection seen in older observational studies? The researchers found a likely explanation: people in early, undiagnosed cognitive decline were already quietly reducing their drinking before they received a dementia diagnosis, making non-drinkers in the comparison group look riskier than they actually were. The protection was a statistical artefact, not a biological reality.

A separate Wake Forest University study reinforced the findings, showing that even modest alcohol use accelerated the buildup of amyloid plaques — the toxic protein deposits that define Alzheimer's disease.

## Cancer, liver disease, and 20 other conditions

The brain is not the only organ at risk. A comprehensive analysis published on 1 June 2026 in *Nature Health* by the Institute for Health Metrics and Evaluation at the University of Washington — covering 843 cohort and case-control studies — found that alcohol consumption raises the risk of at least 20 health conditions.

The risks were clearest and most dose-dependent for cancers. Alcohol elevated the risk of lip and oral cavity cancer, laryngeal cancer, colorectal cancer, breast cancer, and pancreatic cancer — even at levels below one drink per day. Cirrhosis, pancreatitis, and chronic liver diseases showed similarly steep risk curves.

"Even low levels of alcohol use come with health risks," said lead author Kevin Shield, an associate professor at the University of Toronto and a WHO collaborator. "And that risk continues to increase the more someone drinks."

## Why this matters for the Indian diaspora

South Asian drinking patterns are shifting rapidly, particularly among diaspora communities. Social drinking culture has normalised moderate alcohol use in professional and social circles in the US, UK, and Gulf countries. At the same time, India's domestic alcohol market is among the world's fastest-growing — a 2025 IWSR report estimated India's spirits market at $35 billion, expanding at roughly 7% annually.

The metabolic context compounds the risk. South Asians carry a higher baseline burden of type 2 diabetes, cardiovascular disease, and metabolic syndrome — conditions that alcohol now appears to worsen rather than protect against. The "thin-fat" phenotype common among South Asians, where visceral fat accumulates even at a normal BMI, may make the metabolic effects of alcohol more damaging than population-level studies suggest.

For NRIs caring for ageing parents in India, where dementia awareness and diagnosis remain limited, the actionable message is straightforward: the old advice that a daily drink is fine for the brain is no longer supported by the best available evidence.

"There was a time when medical knowledge seemed to support that light drinking would be beneficial to brain health," said Dr Joel Gelernter, professor at Yale and senior author. "This work adds to the evidence that this is not correct."

**Sources:** Oxford Population Health / University of Oxford; *Nature Health* (June 1, 2026); Journal of Studies on Alcohol and Drugs / Rutgers University; Wake Forest University; Healthline; Medical Xpress"""

art2_sources = json.dumps([
    {"name": "University of Oxford / Oxford Population Health", "url": "https://www.ox.ac.uk"},
    {"name": "Nature Health (IHME, University of Washington)", "url": "https://www.nature.com"},
    {"name": "Journal of Studies on Alcohol and Drugs", "url": "https://www.jsad.com"},
    {"name": "Healthline", "url": "https://www.healthline.com"},
    {"name": "Medical Xpress", "url": "https://medicalxpress.com"},
])

# ══════════════════════════════════════════════════════════════════════════
# ARTICLE 3: India's IPO Mega Wave — Jio, NSE, Zepto in H2 2026
# ══════════════════════════════════════════════════════════════════════════

art3_slug = 'india-ipo-mega-wave-jio-nse-zepto-sbi-mf-h2-2026-sebi-nri-investor-20260628'
art3_headline = 'India Is About to Launch the Biggest IPO Wave in Its History — and NRI Investors Are Watching Closely'
art3_subheadline = 'Jio Platforms, the National Stock Exchange, Zepto, and SBI Mutual Fund are among at least ₹90,000 crore worth of public offerings lined up for the second half of 2026, led by what could be India\'s largest-ever listing'

art3_body = """The second half of 2026 is shaping up to be the most consequential stretch in the history of India's primary capital markets. Reliance Jio Platforms, the country's largest telecom operator with over 500 million users, has filed its draft red herring prospectus with SEBI and is awaiting final approval for what would be India's biggest-ever initial public offering. It is just the headliner in a pipeline that could collectively raise over ₹90,000 crore — roughly $11 billion.

SEBI has issued initial observations on Jio's filing and is seeking further clarifications, Outlook Money reported on 26 June. The IPO is expected to comprise a fresh issue of 270 million equity shares — no offer for sale — aiming to raise approximately ₹35,000 crore. The proceeds are earmarked primarily for repaying borrowings of subsidiary Reliance Jio Infocomm, with the remainder going toward general corporate purposes.

## The Jio arithmetic

Jefferies has valued Jio Platforms at $180 billion. At a 2.5% free float — the level Reliance has indicated it prefers, pending a SEBI rule change to reduce the minimum listing requirement for large companies from 5% to 2.5% — the IPO would raise around $4.5 billion, eclipsing Hyundai Motor India's record $3.3 billion listing in 2024.

The company has also held talks with its 13 marquee foreign investors — including Meta (9.99% stake), Google (7.73%), KKR, Vista Equity, and three Gulf sovereign wealth funds — about each selling roughly 8% of their individual holdings as part of the IPO, Reuters reported. The combined stake sale effectively amounts to about 2.5% of outstanding shares.

Over the past six years, Jio has diversified well beyond telecoms into AI infrastructure, 5G, cloud services, and digital commerce. Roughly 75-80% of annual revenues still come from the core telecom business, but it is the AI and digital ecosystem play that investment bankers are pitching at a valuation of $200 billion to $240 billion.

## The supporting cast

Jio is not alone. The National Stock Exchange of India — the country's largest bourse by trading volume — has appointed 20 merchant bankers and is expected to raise around ₹30,000 crore in what would be one of the most unusual listings anywhere: a stock exchange going public on its own platform.

Other major offerings in the pipeline:

- **SBI Mutual Fund**: India's largest mutual fund house is targeting a listing by September 2026, with an estimated ₹10,000 crore issue.
- **Zepto**: The quick-commerce startup has secured SEBI's in-principle approval for an ₹8,010 crore IPO, with the fresh issue likely combined with secondary stake sales.
- **Acko**: The insurtech firm is preparing a ₹2,831 crore issue.
- **PhonePe**: Has received SEBI's nod but delayed amid volatile markets. Plans to raise ~₹12,000 crore.
- **Flipkart**: Has shifted its domicile from Singapore to India and is in the process of filing its DRHP.

Goldman Sachs, Kotak Mahindra, and JPMorgan expect India's total 2026 IPO proceeds to hit $25 billion — a record for the third consecutive year.

## The NRI question: profit extraction or growth investment?

For NRI investors, the wave carries both opportunity and caution. A Reuters investigation flagged a structural concern: of the six foreign-based companies that listed their Indian units in Mumbai since 2024, five were structured purely as secondary offerings, with existing shareholders cashing out rather than raising new capital. For every dollar raised in these IPOs combined, more than $59 was repatriated to foreign headquarters. Hyundai and LG accounted for over 80% of the nearly $5 billion extracted.

Jio's listing bucks the trend — its fresh issue of ₹35,000 crore brings new capital into the company. But the simultaneous stake sale by Meta, Google, and other marquee investors suggests that for some, the IPO is as much an exit opportunity as a growth story.

Indian market analyst MUFG Bank has warned that IPO-linked capital repatriations are contributing to foreign capital outflows, which have already crossed a record $30.6 billion year-to-date. "IPO-linked capital outflows are exerting a steady depreciation bias on the rupee," noted Axis Bank's Tanay Dalal.

## How NRIs can participate

NRI investors can apply for Indian IPOs through NRE or NRO demat accounts linked to ASBA-enabled bank accounts. Both repatriable (NRE) and non-repatriable (NRO) routes are available, though NRIs from the US and Canada face additional compliance requirements under FATCA.

For the Jio IPO specifically, institutional NRI investors may access the qualified institutional buyer (QIB) or non-institutional investor (NII) categories, while retail NRIs can apply in the retail category up to ₹2 lakh per application.

With SEBI reviewing Jio's DRHP and the IPO window expected to open in Q3 or Q4 2026, the clock is ticking for NRIs who want a seat at the table.

**Sources:** Reuters; Outlook Money; Inshorts; The Hindu BusinessLine / Bloomberg; Upstox; Livemint; IPO Watch India"""

art3_sources = json.dumps([
    {"name": "Reuters", "url": "https://www.reuters.com"},
    {"name": "Outlook Money", "url": "https://www.outlookmoney.com"},
    {"name": "The Hindu BusinessLine / Bloomberg", "url": "https://www.thehindubusinessline.com"},
    {"name": "Inshorts", "url": "https://www.inshorts.com"},
    {"name": "Livemint", "url": "https://www.livemint.com"},
])

# ══════════════════════════════════════════════════════════════════════════
# MAIN: source images → insert articles
# ══════════════════════════════════════════════════════════════════════════

def main():
    now = datetime.now(timezone.utc).isoformat()
    articles = []

    # ── Article 1: HPV ──
    print('\n=== Article 1: HPV Vaccine ===')
    img1_url, img1_attr = source_and_upload_image(
        art1_slug,
        ['HPV vaccination adolescent girl', 'cervical cancer vaccine India'],
        headline=art1_headline
    )

    articles.append({
        'headline': art1_headline,
        'subheadline': art1_subheadline,
        'slug': art1_slug,
        'body': art1_body,
        'category': 'lifestyle-health',
        'vertical': 'public-health',
        'status': 'review',
        'is_editorial': False,
        'sources': art1_sources,
        'image_url': img1_url,
        'image_caption': 'A healthcare worker administers an HPV vaccine to a young patient',
        'image_attribution': img1_attr or 'Wikimedia Commons',
        'diaspora_angle': 'India accounts for 25% of global cervical cancer deaths; NRI families should ensure children receive the HPV vaccine, which the new Lancet study shows reduces cervical cancer mortality to zero when given before age 14.',
        'published_at': now,
    })

    # ── Article 2: Alcohol / Dementia ──
    print('\n=== Article 2: Alcohol & Dementia ===')
    img2_url, img2_attr = source_and_upload_image(
        art2_slug,
        ['alcohol brain health dementia', 'wine glass drink'],
        headline=art2_headline
    )

    articles.append({
        'headline': art2_headline,
        'subheadline': art2_subheadline,
        'slug': art2_slug,
        'body': art2_body,
        'category': 'lifestyle-health',
        'vertical': 'neuroscience',
        'status': 'review',
        'is_editorial': False,
        'sources': art2_sources,
        'image_url': img2_url,
        'image_caption': 'Research now shows any level of alcohol consumption poses risks to brain health',
        'image_attribution': img2_attr or 'Pexels',
        'diaspora_angle': 'South Asian drinking culture is normalising in the diaspora, but the new Oxford-Harvard genetic study shows no safe level of alcohol for brain health — particularly concerning given South Asians\' elevated baseline risk for metabolic disease and dementia.',
        'published_at': now,
    })

    # ── Article 3: IPO wave ──
    print('\n=== Article 3: IPO Mega Wave ===')
    img3_url, img3_attr = source_and_upload_image(
        art3_slug,
        ['Bombay Stock Exchange Mumbai', 'Indian stock market trading'],
        person_name='Mukesh Ambani',
        headline=art3_headline
    )

    articles.append({
        'headline': art3_headline,
        'subheadline': art3_subheadline,
        'slug': art3_slug,
        'body': art3_body,
        'category': 'markets-finance',
        'vertical': 'capital-markets',
        'status': 'review',
        'is_editorial': False,
        'sources': art3_sources,
        'image_url': img3_url,
        'image_caption': 'Mukesh Ambani\'s Jio Platforms is set to launch India\'s largest-ever IPO in 2026',
        'image_attribution': img3_attr or 'Wikimedia Commons',
        'diaspora_angle': 'NRI investors can participate in India\'s historic IPO wave through NRE/NRO demat accounts; the ₹35,000 crore Jio listing alone could be the largest opportunity in Indian market history.',
        'published_at': now,
    })

    # ── Insert all ──
    print('\n=== Inserting articles ===')
    for art in articles:
        if not art.get('image_url'):
            art.pop('image_url', None)
            art.pop('image_caption', None)
            art.pop('image_attribution', None)
        result = sb_insert('p2_articles', art)
        if result:
            print(f'  ✓ Inserted: {art["headline"][:60]}... (id={result.get("id", "?")})')
        else:
            print(f'  ✗ FAILED: {art["headline"][:60]}...')

    print('\n=== Done ===')

if __name__ == '__main__':
    main()
