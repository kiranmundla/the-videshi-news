#!/usr/bin/env python3
"""
Lifestyle & Markets writer — June 7 2026 run
Produces 2 lifestyle-health + 1 markets-finance articles.
"""
import json, os, sys, uuid, re, time, subprocess, io, textwrap
from datetime import datetime, timezone
from urllib.parse import quote, quote_plus

import requests
from PIL import Image

# ── env ──────────────────────────────────────────────────────────────
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
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SB_URL = os.environ['SUPABASE_URL']
SB_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SB_KEY,
    'Authorization': f'Bearer {SB_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
}

UA = 'TheVideshi/1.0 (thevideshi.com)'

# ── image helpers ────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    encoded = quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f'https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}',
            headers={'User-Agent': UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get('originalimage', {}).get('source') or data.get('thumbnail', {}).get('source')
            if img:
                print(f'  ✓ Wikipedia image for "{person_name}": {img[:90]}...')
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
        r = requests.get(
            'https://commons.wikimedia.org/w/api.php',
            params=params, headers={'User-Agent': UA}, timeout=15
        )
        if r.status_code == 200:
            pages = r.json().get('query', {}).get('pages', {})
            results = []
            for p in pages.values():
                ii = p.get('imageinfo', [{}])[0]
                mime = ii.get('mime', '')
                if not mime.startswith('image/') or mime == 'image/svg+xml':
                    continue
                if ii.get('width', 0) < 300:
                    continue
                results.append({
                    'url': ii.get('thumburl') or ii.get('url', ''),
                    'original_url': ii.get('url', ''),
                    'title': p.get('title', ''),
                    'width': ii.get('width', 0),
                    'height': ii.get('height', 0),
                })
            if results:
                print(f'  ✓ Commons: {len(results)} images for "{query}"')
            return results
    except Exception as e:
        print(f'  ⚠ Commons error: {e}')
    return []


def fetch_pexels(query):
    if not PEXELS_KEY:
        return None
    try:
        result = subprocess.run(
            ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
             f'https://api.pexels.com/v1/search?query={quote_plus(query)}&per_page=3'],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get('photos', [])
        if photos:
            url = photos[0]['src']['large2x']
            print(f'  ✓ Pexels: {url[:80]}...')
            return url
    except Exception as e:
        print(f'  ⚠ Pexels error: {e}')
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


def download_and_upload(image_url, slug):
    """Download, compress, and upload to Supabase article-images bucket."""
    try:
        r = requests.get(image_url, headers={'User-Agent': UA}, timeout=20)
        if r.status_code != 200:
            print(f'  ✗ Download failed ({r.status_code}) for {image_url[:80]}')
            return None
        ct = r.headers.get('Content-Type', '')
        if 'image' not in ct:
            print(f'  ✗ Not an image: {ct}')
            return None
        raw = r.content
        if len(raw) < 5000:
            print(f'  ✗ Image too small: {len(raw)} bytes')
            return None
        compressed = compress_image(raw)
        print(f'  → Compressed: {len(raw)} → {len(compressed)} bytes')

        filename = f'{slug}.jpg'
        upload_url = f'{SB_URL}/storage/v1/object/article-images/{filename}'
        up = requests.post(
            upload_url,
            headers={
                'Authorization': f'Bearer {SB_KEY}',
                'Content-Type': 'image/jpeg',
                'x-upsert': 'true',
            },
            data=compressed, timeout=20
        )
        if up.status_code in (200, 201):
            public_url = f'{SB_URL}/storage/v1/object/public/article-images/{filename}'
            print(f'  ✓ Uploaded → {public_url[:80]}...')
            return public_url
        else:
            print(f'  ✗ Upload failed ({up.status_code}): {up.text[:200]}')
            return None
    except Exception as e:
        print(f'  ✗ download_and_upload error: {e}')
        return None


def source_image(person_name, topic_queries, slug):
    """Multi-source image search: Wikipedia → Commons → Pexels. Returns (url, attribution)."""
    candidates = []

    # 1. Wikipedia person image
    if person_name:
        wiki = fetch_wikipedia_person_image(person_name)
        if wiki:
            candidates.append(('wikipedia', wiki))

    # 2. Wikimedia Commons
    for q in topic_queries:
        commons = fetch_wikimedia_commons(q)
        for c in commons[:2]:
            candidates.append(('wikimedia_commons', c['url']))
        if commons:
            break

    # 3. Pexels (last resort, topic/scene only)
    if not person_name:
        for q in topic_queries:
            px = fetch_pexels(q)
            if px:
                candidates.append(('pexels', px))
                break

    # Pick best & upload
    for source, url in candidates:
        uploaded = download_and_upload(url, slug)
        if uploaded:
            attr = 'Wikimedia Commons' if source in ('wikipedia', 'wikimedia_commons') else 'Pexels'
            return uploaded, attr

    print(f'  ✗ No image found for {slug}')
    return None, None


# ── article insert ───────────────────────────────────────────────────
def insert_article(article):
    """Insert article into p2_articles."""
    r = requests.post(
        f'{SB_URL}/rest/v1/p2_articles',
        headers=HEADERS,
        json=article,
        timeout=20
    )
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]['id'] if isinstance(result, list) else result.get('id')
        print(f'  ✓ Published: {article["headline"][:60]}... (id={art_id})')
        return art_id
    else:
        print(f'  ✗ Insert failed ({r.status_code}): {r.text[:300]}')
        return None


# ── build articles ───────────────────────────────────────────────────
def build_articles():
    now = datetime.now(timezone.utc)
    articles_data = []

    # ================================================================
    # ARTICLE 1: Wegovy / Semaglutide helps Sleep Apnea and Asthma
    # Category: lifestyle-health
    # ================================================================
    slug1 = 'wegovy-semaglutide-sleep-apnea-asthma-ada-2026-south-asian-diaspora-20260607'
    headline1 = "Wegovy Now Helps Sleep Apnoea and Asthma, Not Just Weight Loss. South Asians Should Be Paying Attention."
    subheadline1 = "New data from four major trials presented at ADA 2026 show semaglutide improves obstructive sleep apnoea, reduces asthma flare-ups, lowers blood pressure, and protects the liver — benefits that go well beyond the number on the scale."
    body1 = textwrap.dedent("""\
When Novo Nordisk's Wegovy arrived as a weight-loss injection, the conversation was simple: it helps people shed kilos. That narrative is now officially outdated. At the American Diabetes Association's 86th Scientific Sessions in New Orleans this week, the Danish pharmaceutical giant presented post hoc analyses from four landmark trials — SELECT, STEP, ESSENCE, and OASIS — showing that semaglutide, the active ingredient in Wegovy, is doing far more than trimming waistlines.

The new data reveals clinically meaningful improvements across obstructive sleep apnoea, asthma-related outcomes, uncontrolled hypertension, and liver health in people with obesity or overweight. For South Asians — a population that carries disproportionate metabolic risk at lower body weights — these findings matter more than the headlines suggest.

## Sleep Apnoea: The Silent Epidemic in South Asian Homes

Obstructive sleep apnoea affects roughly one billion people worldwide, and South Asians are among the most under-diagnosed. Craniofacial anatomy, visceral fat distribution, and high rates of insulin resistance make the community particularly vulnerable. Many desi families normalise heavy snoring as "just how uncle sleeps" while the condition quietly drives hypertension, heart attacks, and strokes.

The SELECT trial data presented at ADA 2026 showed that semaglutide 2.4 mg weekly reduced the severity of obstructive sleep apnoea in adults with established cardiovascular disease and obesity. Participants experienced fewer apnoeic episodes and reported improved sleep quality — outcomes that translate directly into lower cardiovascular risk over time.

For NRIs managing demanding tech careers, long commutes, and high-stress lifestyles, sleep quality is not a luxury. Untreated sleep apnoea impairs cognition, raises accident risk, and accelerates metabolic syndrome. A drug that treats both obesity and sleep apnoea simultaneously could change the calculus for thousands of Indian Americans who currently manage neither condition.

## Asthma Flare-Ups Drop — Without Changing Inhalers

A separate post hoc analysis from the SELECT and STEP programmes showed that semaglutide use was associated with a reduction in asthma-related adverse outcomes in people with overweight or obesity. This did not require patients to change their existing asthma medications.

The mechanism is believed to be partly weight-related — excess body fat compresses the lungs and increases airway inflammation — and partly anti-inflammatory. GLP-1 receptor agonists like semaglutide appear to dampen systemic inflammation in ways that benefit the airways independently of weight loss.

India has an estimated 34 million asthma patients, and diaspora communities carry elevated prevalence partly due to genetic predisposition and partly due to urban pollution exposure during childhood years spent in Indian metros. For NRIs with both excess weight and asthma, semaglutide may now offer a dual benefit that no single drug previously delivered.

## Blood Pressure and Liver: The Quieter Wins

The ADA presentations also included data showing improvements in systolic blood pressure among patients with uncontrolled hypertension and obesity. Given that hypertension is the leading cause of death in the Indian diaspora — affecting over 30 per cent of South Asian adults in the United States — any drug that reliably lowers both weight and blood pressure simultaneously commands attention.

Additional data from the ESSENCE trial highlighted liver health improvements, specifically in patients with metabolic dysfunction-associated steatohepatitis, formerly known as non-alcoholic fatty liver disease. MASH disproportionately affects South Asians: community studies have found prevalence rates exceeding 30 per cent even among lean individuals, driven by insulin resistance and visceral fat patterns specific to the population.

## What This Means for Indian Americans

"These new analyses build on the growing body of clinical evidence for semaglutide, an important medicine that has already been extensively studied not only in obesity but also in cardiovascular disease and MASH," said Andrea Traina, senior medical director for obesity and liver health at Novo Nordisk.

The practical implication is significant. South Asian patients who might have dismissed Wegovy as "just a weight-loss drug" now face a different value proposition: a single weekly injection that simultaneously addresses obesity, sleep apnoea, asthma severity, blood pressure, and fatty liver disease. These are not five separate conditions for the community — they are often five manifestations of the same underlying metabolic dysfunction.

## The Access Problem Remains

None of this matters if patients cannot afford or access the drug. Wegovy's list price in the United States remains above $1,300 per month, and insurance coverage is uneven. Medicare does not cover anti-obesity medications, and many employer plans require extensive prior authorisation. Indian Americans on H-1B visas face additional uncertainty: a job change can mean a change in insurance, which can mean a sudden loss of medication access.

Novo Nordisk's Phase 3 pipeline includes an oral version of semaglutide and next-generation combinations with amylin analogs that could eventually bring costs down. But for now, the gap between what the science promises and what patients can actually get remains the defining challenge.

The data presented this week in New Orleans is unambiguous. Semaglutide is no longer a weight-loss drug that happens to have side benefits. It is a cardiometabolic platform therapy — and for a community that faces the highest burden of exactly those conditions, the science has moved faster than the system designed to deliver it.

*Sources: Novo Nordisk ADA 2026 press release; SELECT, STEP, ESSENCE, and OASIS post hoc analyses presented at ADA 86th Scientific Sessions, New Orleans, June 5-8 2026; Lancet Respiratory Medicine South Asian sleep apnoea prevalence data; American Heart Association hypertension statistics.*""")

    # ================================================================
    # ARTICLE 2: ESPRIT trial — blood pressure targets
    # Category: lifestyle-health
    # ================================================================
    slug2 = 'esprit-trial-blood-pressure-120-target-south-asian-hypertension-20260607'
    headline2 = "Targeting 120 Instead of 140 Cut Cardiovascular Deaths by 39 Per Cent. Most South Asians Are Still Aiming Too High."
    subheadline2 = "The ESPRIT trial tracked 11,255 high-risk adults for three years and found that aggressive blood pressure lowering dramatically reduced heart attacks, strokes, and death — findings that carry outsized relevance for a community where one in three adults has hypertension."
    body2 = textwrap.dedent("""\
For decades, the standard treatment target for high blood pressure has been to keep systolic readings below 140 mm Hg. It is a number drilled into medical school curricula, printed on clinic wall charts, and embedded in the muscle memory of family physicians worldwide. A major clinical trial now says that target is not good enough — and for South Asians, who face the world's highest burden of hypertension-related cardiovascular disease, the implications are enormous.

The ESPRIT trial, led by Dr Jing Li at China's National Center for Cardiovascular Diseases, randomised 11,255 adults with high blood pressure and elevated cardiovascular risk into two groups. One received intensive treatment to push systolic blood pressure below 120 mm Hg. The other received standard treatment targeting below 140 mm Hg. Both groups used antihypertensive medications, but the intensive group typically required more drugs at higher doses.

## The Numbers That Matter

After three years, the intensive group showed a 12 per cent reduction in major cardiovascular events including heart attacks and strokes. They were 39 per cent less likely to die from cardiovascular disease. And they were 21 per cent less likely to die from any cause during the study period.

Those are not marginal gains. A 39 per cent reduction in cardiovascular death is the kind of number that rewrites treatment guidelines.

The ESPRIT results align with and reinforce the earlier American SPRINT trial, which found similarly dramatic benefits from targeting 120 mm Hg in a North American population. Together, the two trials now provide robust evidence across both Western and Asian populations that the traditional 140 mm Hg target leaves preventable deaths on the table.

## Why South Asians Cannot Ignore This

Hypertension is not a niche concern for the Indian diaspora. It is the leading risk factor for death. Studies consistently show that over 30 per cent of South Asian adults in the United States, United Kingdom, and Canada have hypertension, and the condition develops earlier and progresses faster than in European-origin populations.

The reasons are partly genetic — South Asians have a higher prevalence of salt-sensitive hypertension and endothelial dysfunction — and partly lifestyle-driven. High sodium intake from traditional cooking methods, limited physical activity, elevated stress from immigration and career pressures, and visceral fat accumulation all contribute.

What makes the ESPRIT data particularly relevant is the population it studied. The average participant was 64 years old. Nearly 39 per cent had diabetes. Many had already experienced a cardiac event. This is a profile that maps closely onto the at-risk segment of the South Asian diaspora: older NRIs with metabolic syndrome who are managing multiple conditions simultaneously.

## The Safety Question

The objection to aggressive blood pressure lowering has always been safety. Doctors worry about dizziness, fainting, falls, and kidney injury — particularly in older patients.

ESPRIT addressed this directly. Fainting occurred slightly more often in the intensive group, but the increase was small: roughly three additional episodes per 1,000 patients. The researchers concluded that the cardiovascular benefits — preventing heart attacks, strokes, and deaths — far outweighed this modest risk.

A secondary analysis published in the Journal of the American College of Cardiology examined stroke outcomes specifically and found that ischaemic stroke risk declined in the intensive arm, with time-dependent benefits emerging after the first year of treatment. This matters for South Asians, who carry elevated stroke risk partly due to the interaction between hypertension and diabetes.

## What NRIs Should Do Now

If you are a South Asian adult over 40 with high blood pressure, the practical question is whether your treatment target should change. The answer, increasingly, is yes — but with caveats.

First, intensive blood pressure lowering requires close monitoring. The ESPRIT participants were seen regularly and their medications adjusted systematically. This is not a set-and-forget approach.

Second, home blood pressure monitoring becomes essential. Office readings can be unreliable, and the ESPRIT protocol relied on careful, repeated measurements. Investing in a validated home blood pressure cuff and tracking readings over weeks gives both patient and physician the data needed to titrate medications safely.

Third, lifestyle interventions remain foundational. The DASH diet — emphasising fruits, vegetables, whole grains, and low sodium — has been shown to lower systolic blood pressure by 8 to 14 mm Hg. Regular aerobic exercise contributes another 5 to 8 mm Hg reduction. These effects are additive with medication and can sometimes mean the difference between two drugs and three.

Fourth, ask your doctor specifically about the 120 mm Hg target. Many physicians still default to 140 mm Hg out of habit or concern about older guidelines. The ESPRIT and SPRINT data now provide strong evidence that the lower target saves lives, and a conversation about whether it is appropriate for your risk profile is warranted.

## The Bigger Picture

Hypertension kills more people in India and among the Indian diaspora than any other single condition. It is cheap to diagnose, inexpensive to treat, and responds well to lifestyle changes. Yet it remains poorly controlled across the community — partly because it causes no symptoms until it causes a catastrophe, and partly because treatment targets have been too generous for too long.

The ESPRIT trial is one of the largest and most rigorous blood pressure studies ever conducted. Its message is straightforward: for high-risk patients, 140 is not low enough. 120 saves more lives. And for South Asians, whose baseline cardiovascular risk already sits at the top of the global distribution, that 20-point difference may be the single most important number in preventive medicine.

*Sources: ESPRIT trial (Li J et al., American Heart Association Scientific Sessions); JACC secondary stroke analysis; SPRINT trial (NEJM); American Heart Association hypertension prevalence data; MASALA study (Northwestern University) South Asian cardiovascular risk data.*""")

    # ================================================================
    # ARTICLE 3: India stagflation risk — Nuvama warning
    # Category: markets-finance
    # ================================================================
    slug3 = 'india-stagflation-risk-nuvama-rbi-rate-hike-iran-oil-monsoon-nri-20260607'
    headline3 = "India Faces Its First Stagflation Scare in a Decade. Here Is What NRIs Need to Understand."
    subheadline3 = "Nuvama Institutional Equities warns that the Iran oil shock combined with a potentially weak monsoon could push India into a rare growth-inflation trap — forcing the RBI to hike rates just as the economy slows."
    body3 = textwrap.dedent("""\
The word stagflation has not featured in serious Indian economic commentary since the early 2010s. That just changed. Nuvama Institutional Equities, one of India's most closely watched brokerages, published a GDP analysis report this week warning that the convergence of the Iran oil shock and a potentially subpar monsoon raises the risk of a stagflationary environment in FY27 — a scenario where growth slows and inflation simultaneously rises, leaving policymakers with no good options.

For NRIs with money in India — through NRE deposits, mutual funds, real estate, or family businesses — this is the kind of macro risk that can erode returns across every asset class at once.

## What Nuvama Is Actually Saying

The brokerage's core argument is straightforward but alarming. India's economy closed FY26 with strong 7.7 per cent GDP growth, accelerating from 7.1 per cent in FY25. The March quarter came in at an impressive 7.8 per cent. By most measures, the economy was firing on all cylinders.

But FY27 faces a fundamentally different operating environment. The Iran war has kept crude oil prices elevated near $95 per barrel since February, with the Strait of Hormuz — which carried nearly 20 per cent of global oil supply before the conflict — effectively shut. India imports over 85 per cent of its crude oil. Every $10 per barrel increase in oil prices widens the current account deficit by roughly 0.4 per cent of GDP and adds 30 to 40 basis points to inflation.

Compounding the oil shock is the monsoon outlook. Early forecasts suggest the 2026 monsoon may underperform, which would push food prices higher just as input cost inflation from oil is feeding through the supply chain. Food and fuel together account for nearly half of India's consumer price basket.

Nuvama has revised its FY27 real GDP growth forecast down to 6 to 6.5 per cent, while expecting nominal GDP growth to accelerate to 11 to 12 per cent — a classic stagflationary signature where prices are rising faster than real output.

## The RBI's Impossible Position

The Reserve Bank of India held its repo rate unchanged at 5.25 per cent on Friday, the third consecutive policy meeting without action. Governor Sanjay Malhotra called it a "data-dependent" pause, but the underlying numbers are tightening in ways that may force the central bank's hand.

The RBI raised its FY27 inflation projection to 5.1 per cent from 4.6 per cent and trimmed its GDP growth forecast to 6.6 per cent from 6.9 per cent. More concerning is the quarterly trajectory: the central bank expects CPI inflation to reach 5.9 per cent in both Q3 and Q4 of FY27, pushing uncomfortably close to the upper tolerance band of 6 per cent.

Meanwhile, the rupee has fallen over 6 per cent against the dollar in 2026, making it the worst-performing currency among major emerging markets. The RBI's foreign exchange reserves, while still substantial at roughly $590 billion, have been drawn down to defend the currency.

Capital Economics, a London-based research firm, has gone further than most: it projects the RBI will be forced to hike rates by a cumulative 75 basis points to 6 per cent by the end of 2026. ICRA's chief economist Aditi Nayar has not ruled out a hike as early as Q3 FY27.

If hikes materialise, they would reverse the easing cycle that began with a 25 basis point cut in December 2025 — a whiplash reversal that would catch many investors off guard.

## What This Means for NRI Money

The implications cascade across asset classes.

**NRE and NRO fixed deposits**: If the RBI hikes rates, Indian bank deposit rates will rise. NRIs currently earning 7 to 7.5 per cent on NRE fixed deposits could see rates climb to 8 per cent or higher. For those with dollar income, this becomes increasingly attractive — but only if the rupee stabilises. A depreciating rupee can wipe out the interest rate advantage when funds are eventually repatriated.

**Equity markets**: The Sensex and Nifty fell for a second consecutive week, weighed down by global headwinds and RBI caution. Rate hikes are unambiguously negative for equity valuations, particularly for the rate-sensitive sectors — real estate, banking, auto, and consumer discretionary — that make up a significant portion of Indian indices. Nuvama's stagflation scenario implies a period where corporate earnings growth slows while borrowing costs rise, a combination that compresses price-to-earnings multiples.

**Real estate**: For NRIs who have been buying property in India or considering it, rising rates mean higher home loan costs. The affordable housing segment, which has driven much of India's real estate recovery since 2021, is most sensitive to rate changes. A 75 basis point hike would add roughly Rs 1,200 to the monthly EMI on a Rs 50 lakh home loan.

**Remittances**: NRIs sending money to family in India face a secondary hit. The weaker rupee means each dollar buys more rupees — a positive in the short term for remittance recipients. But if inflation in India is running at 5 to 6 per cent, the purchasing power of those rupees erodes quickly. The net benefit of a weaker rupee is much smaller than it appears on the exchange rate screen.

## The Rupee Defence Package

To its credit, the RBI did not sit idle. Alongside the rate hold, it announced measures to attract dollar inflows: scrapping capital gains tax for foreign portfolio investors in government bonds, sweetening FCNR(B) deposit schemes for NRIs, and signalling willingness to intervene in currency markets to prevent disorderly moves.

The bond tax exemption, in particular, is designed to draw foreign institutional money into India's sovereign debt market — a market where foreign participation has historically been low despite India's investment-grade rating. If successful, the measure could support the rupee and lower government borrowing costs simultaneously.

The rupee strengthened 0.6 per cent to 95.24 against the dollar after the announcements, suggesting some immediate market confidence. But structural relief depends on whether oil prices retreat — which in turn depends on whether the US-Iran ceasefire talks produce a durable agreement.

## What to Watch

Three variables will determine whether India's stagflation scare becomes reality or fades into the background.

First, the monsoon. June and July rainfall patterns will set the trajectory for food prices through the rest of FY27. A below-normal monsoon would confirm the worst-case scenario for inflation.

Second, crude oil. If the Strait of Hormuz reopens on a sustained basis, Brent could drop to $75 to $80 per barrel, easing India's import bill and inflation outlook. If the conflict drags on or escalates, $100 or above becomes the base case.

Third, the Fed. The US Federal Reserve's own rate path influences global capital flows. If the Fed hikes — rate hike odds after the latest jobs report sit at 70 per cent — capital will flow out of emerging markets toward dollar assets, adding more pressure on the rupee and forcing the RBI's hand.

For NRI investors, the message from Nuvama's report is not to panic but to stress-test. The assumptions that underpinned portfolio allocation six months ago — stable oil, falling rates, strong rupee — have all shifted. Portfolios that were built for an easing cycle need to be reviewed for a tightening one.

*Sources: Nuvama Institutional Equities GDP analysis report (June 2026); RBI MPC statement June 5 2026; Reuters; Capital Economics India outlook; ICRA monetary policy commentary; Livemint; The Hindu Business Line.*""")

    # ──────────────────────────────────────────────────────────────────
    # Assemble articles metadata
    # ──────────────────────────────────────────────────────────────────
    articles_data = [
        {
            'slug': slug1,
            'headline': headline1,
            'subheadline': subheadline1,
            'body': body1,
            'category': 'lifestyle-health',
            'vertical': 'lifestyle-health',
            'person_name': None,
            'image_queries': ['semaglutide injection obesity', 'Wegovy weight loss medication', 'obesity treatment medicine'],
            'image_caption': 'A semaglutide injection pen used for weight management and cardiometabolic health',
            'sources': json.dumps([
                'Novo Nordisk ADA 2026 press release',
                'SELECT, STEP, ESSENCE, OASIS clinical trials post hoc analyses',
                'ADA 86th Scientific Sessions June 2026',
                'Lancet Respiratory Medicine'
            ]),
        },
        {
            'slug': slug2,
            'headline': headline2,
            'subheadline': subheadline2,
            'body': body2,
            'category': 'lifestyle-health',
            'vertical': 'lifestyle-health',
            'person_name': None,
            'image_queries': ['blood pressure measurement hypertension', 'sphygmomanometer doctor checking blood pressure', 'cardiovascular health monitoring'],
            'image_caption': 'A clinician measuring blood pressure — the ESPRIT trial suggests lower targets save more lives',
            'sources': json.dumps([
                'ESPRIT trial (Li J et al., AHA Scientific Sessions)',
                'JACC secondary stroke analysis',
                'SPRINT trial (New England Journal of Medicine)',
                'MASALA study Northwestern University'
            ]),
        },
        {
            'slug': slug3,
            'headline': headline3,
            'subheadline': subheadline3,
            'body': body3,
            'category': 'markets-finance',
            'vertical': 'markets-finance',
            'person_name': 'Sanjay Malhotra',  # RBI Governor
            'image_queries': ['Reserve Bank of India building', 'RBI monetary policy Mumbai', 'Indian economy inflation'],
            'image_caption': 'RBI Governor Sanjay Malhotra held rates steady at 5.25 per cent but faces mounting pressure to hike',
            'sources': json.dumps([
                'Nuvama Institutional Equities GDP analysis report June 2026',
                'RBI MPC statement June 5 2026',
                'Reuters',
                'Capital Economics India outlook',
                'Livemint'
            ]),
        },
    ]

    published = 0
    for art in articles_data:
        print(f'\n{"="*60}')
        print(f'Processing: {art["headline"][:60]}...')
        print(f'Category: {art["category"]}')

        # Source image
        person = art.pop('person_name')
        queries = art.pop('image_queries')
        caption = art.pop('image_caption')

        img_url, img_attr = source_image(person, queries, art['slug'])

        payload = {
            'headline': art['headline'],
            'subheadline': art['subheadline'],
            'body': art['body'],
            'slug': art['slug'],
            'category': art['category'],
            'vertical': art['vertical'],
            'status': 'published',
            'published_at': now.isoformat(),
            'sources': art['sources'],
            'is_editorial': False,
            'image_url': img_url,
            'image_caption': caption if img_url else None,
            'image_attribution': img_attr,
        }

        art_id = insert_article(payload)
        if art_id:
            published += 1

    print(f'\n{"="*60}')
    print(f'Done. Published {published}/{len(articles_data)} articles.')
    return published


if __name__ == '__main__':
    n = build_articles()
    sys.exit(0 if n > 0 else 1)
