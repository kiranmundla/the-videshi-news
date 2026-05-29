#!/usr/bin/env python3
"""Fixed publisher — adds vertical field."""

import json, os, uuid, requests
from datetime import datetime, timezone

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS_SB = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                'https://api.pexels.com/v1/search',
                headers={'Authorization': PEXELS_KEY},
                params={'query': q, 'per_page': 5, 'orientation': 'landscape'},
                timeout=10
            )
            if r.status_code == 200:
                for photo in r.json().get('photos', []):
                    url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                    if url:
                        check = requests.head(url, timeout=10)
                        if 'image' in check.headers.get('Content-Type', '') and int(check.headers.get('Content-Length', 0)) > 5000:
                            print(f"  ✓ Pexels: {url[:80]}...")
                            return url
        except Exception as e:
            print(f"  ⚠ Pexels error: {e}")
    return None

def upload_to_supabase(image_url, filename):
    try:
        r = requests.get(image_url, timeout=30)
        if r.status_code != 200:
            return image_url
        ct = r.headers.get('Content-Type', 'image/jpeg')
        resp = requests.post(
            f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}",
            headers={
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': ct,
                'x-upsert': 'true'
            },
            data=r.content,
            timeout=30
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded: {filename}")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {resp.status_code}")
            # Use Pexels direct URL as fallback (permanent)
            return image_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return image_url

def publish(article):
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')
    
    payload = {
        'id': art_id,
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': article['slug'],
        'category': article['category'],
        'vertical': article['category'],  # match category
        'sources': json.dumps(article['sources']),
        'image_url': article.get('image_url'),
        'image_caption': article.get('image_caption', ''),
        'image_attribution': article.get('image_attribution', 'Pexels'),
        'status': 'published',
        'published_at': now,
        'created_at': now,
        'updated_at': now,
        'score_total': 75
    }
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=payload,
        timeout=15
    )
    
    if r.status_code in (200, 201):
        print(f"  ✓ Published: {article['headline'][:70]}...")
        print(f"    ID: {art_id} | Slug: {article['slug']}")
        return art_id
    else:
        print(f"  ✗ FAILED: {r.status_code} - {r.text[:400]}")
        return None


# ==============================
# ARTICLE 1 — image upload needed
# ==============================
print("=== Article 1: Yale leisure exercise study ===")
img1 = fetch_pexels_image('person jogging morning park recreational exercise', 'outdoor running fitness leisure')
if img1:
    img1 = upload_to_supabase(img1, 'yale-leisure-exercise-vs-work-movement-nature-genetics-indian-american-health-20260529.jpg')

a1 = publish({
    'headline': "A Yale Study of 540,000 People Found That Your Body Can Tell the Difference Between Working Hard and Working Out. Only One of Them Protects Your Health.",
    'subheadline': "New research in Nature Genetics shows leisure-time exercise activates biological pathways that workplace movement and household chores simply cannot replicate. Indian-American professionals are among the most affected.",
    'body': """Your Fitbit logged 9,000 steps yesterday. You carried groceries up two flights of stairs. You paced through three back-to-back meetings. By every casual measure, you moved plenty.

A new study published in *Nature Genetics* says most of it probably did not count — at least not the way you think it did.

## The Study That Separates Motion From Exercise

Researchers at the Yale School of Medicine and the VA Connecticut Healthcare System analysed genetic data from nearly 190,000 participants in the Million Veteran Program, supplemented by roughly 350,000 individuals in the UK Biobank. Their goal was not merely to confirm that exercise is good for you — decades of research have already established that. Instead, they wanted to understand whether the *context* in which you move your body changes its biological effect.

The answer was unambiguous. Leisure-time physical activity — the kind you choose to do, on your own schedule, for its own sake — was genetically distinct from work-related and household physical activity. The three types of movement activated different biological pathways, and only leisure-time activity showed consistent, broad-spectrum health benefits across cardiovascular, metabolic, and mental health outcomes.

"This work not only shows the genetic differences associated with physical activity performed in different contexts but also highlights the significant health benefits of engaging in physical activity during leisure time," said Marco Galimberti, the paper's first author and an associate research scientist at Yale.

## Why Your 12-Hour Workday Does Not Count

The finding cuts against a belief common among Indian-American professionals — that a demanding day filled with movement is a reasonable substitute for deliberate exercise. Software engineers who walk to whiteboard sessions, physicians who log miles in hospital corridors, parents who sprint between school pickups and cooking — all of them are moving, often considerably. But the study suggests that the metabolic, cardiovascular, and neurological signals triggered by leisure-time physical activity are biologically different from those triggered by occupational or domestic movement.

The researchers found that occupational and household physical activity can even carry *negative* health associations, particularly for musculoskeletal outcomes and long-term well-being. The "physical activity paradox," as the British Journal of Sports Medicine has labelled it, is real: people who move all day at work sometimes have worse health outcomes than people who sit at desks but exercise deliberately after hours.

## What Makes Leisure Exercise Different

The distinction appears to be rooted in autonomy, intensity control, and psychological context. When you choose to run, swim, play badminton, or lift weights during your free time, your body engages systems — including stress-recovery pathways, heart rate variability regulation, and neuroplasticity — that simply do not fire in the same way when you are carrying laundry or walking to a conference room.

Joel Gelernter, a professor of psychiatry and genetics at Yale and the paper's senior author, noted that the genomic architecture underlying these traits provides a foundation for future research into why exercise context matters as much as exercise volume.

## The Diaspora Health Angle

South Asian Americans have among the highest rates of cardiovascular disease, type 2 diabetes, and metabolic syndrome of any ethnic group in the United States. Multiple studies have shown that these risks emerge at lower BMI thresholds than in other populations, and that the protective effect of physical activity is correspondingly more important.

Yet time-use surveys consistently show that first-generation Indian immigrants spend significantly less time on recreational physical activity than US-born adults. The cultural framework around "being busy" — equating long work hours and domestic labour with virtue — may inadvertently crowd out the one type of movement that the body registers as genuinely protective.

The Yale study does not prescribe a specific exercise regimen. But its central implication is clear: 30 minutes of deliberate, self-chosen physical activity — a morning jog, an evening cricket game, a weekend hike — activates biological mechanisms that 10 hours of incidental workplace movement simply cannot replicate.

## What This Means for You

If you are an Indian-American professional who has been telling yourself that your busy day is exercise enough, this study is a direct challenge to that assumption. The steps your phone counts at the office are not the steps your body counts for long-term protection against heart disease, diabetes, and cognitive decline.

The research does not suggest that work and household activity are harmful in themselves. They are simply not substitutes for leisure-time exercise. Your body can tell the difference, even if your fitness tracker cannot.

The study was published in *Nature Genetics* and included researchers from the VA Connecticut Healthcare System and Yale School of Medicine.""",
    'slug': 'yale-leisure-exercise-vs-work-movement-nature-genetics-indian-american-health-20260529',
    'category': 'lifestyle-health',
    'sources': [
        {"name": "Nature Genetics", "url": "https://www.nature.com/"},
        {"name": "Psychiatric Times", "url": "https://www.psychiatrictimes.com/view/yale-study-physical-activity-and-its-relationship-to-health-well-being-and-illness"},
        {"name": "British Journal of Sports Medicine", "url": "https://bjsm.bmj.com/"}
    ],
    'image_url': img1,
    'image_caption': 'Leisure-time exercise — the kind you choose to do — activates biological pathways that workplace movement cannot replicate.',
    'image_attribution': 'Pexels'
})


# ==============================
# ARTICLE 2 — image already uploaded
# ==============================
print("\n=== Article 2: Vaping DNA damage / cancer risk ===")
img2_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/vaping-e-cigarette-dna-damage-cancer-risk-carcinogenesis-review-indian-american-teens-20260529.jpg"

a2 = publish({
    'headline': "A Review of Every Major Vaping Study Since 2017 Found DNA Damage, Heavy Metals, and Early Cancer Signals. 'Safer Than Cigarettes' Was Never the Same as 'Safe.'",
    'subheadline': "E-cigarette aerosols contain formaldehyde, nickel, and chromium. Asian-American teens are among the fastest-growing users. Indian-American parents may be the last to notice.",
    'body': """For years, the pitch has been simple: vaping is safer than smoking. Millions of parents heard it and exhaled in relief. If their teenager was going to do something, at least it was not cigarettes.

A comprehensive new review published in the journal *Carcinogenesis* says that relief may have been premature.

## What the Review Found

The paper is not a single experiment. It is a large-scale scientific review of evidence spanning laboratory studies, animal research, human biomarker analyses, and epidemiological data — all examining whether e-cigarettes damage cells and tissues in ways linked to cancer.

The findings are consistent and concerning. E-cigarette aerosols can damage DNA, the molecular blueprint every cell relies on to divide correctly. They trigger chronic inflammation — a known precursor to tumour formation. And they contain potentially carcinogenic compounds including formaldehyde, acetaldehyde, and heavy metals such as nickel, chromium, and lead, many of which leach from the heating elements inside vaping devices.

The review also examined evidence suggesting possible associations between vaping and cancers of the lungs, mouth, and bladder. While no study has yet produced the kind of definitive, decades-long population data that links cigarettes to lung cancer — e-cigarettes have not existed long enough for that — the authors concluded that the consistency of biological evidence across many types of studies raises "substantial concern."

## Safer Does Not Mean Safe

The distinction matters more than most people realise. Vaping exposes users to fewer toxic chemicals than burning tobacco. That is true and well-established. But "fewer" is not "none," and the gap between "less harmful than cigarettes" and "safe" is enormous.

When a vaping device heats its liquid solution — typically containing nicotine, flavouring chemicals, and solvents like propylene glycol — the process generates ultrafine particles that penetrate deep into the lungs. Nicotine itself, while not a classic carcinogen, may promote tumour growth, blood vessel formation, and cellular signalling pathways that support cancer progression.

Dr Leana Wen, an emergency physician and adjunct associate professor at George Washington University, summarised the problem in a CNN interview: "I worry that 'safer than cigarettes' is often interpreted as 'safe,' and that is not supported by the evidence."

## The Numbers That Should Worry Indian-American Parents

More than 1.6 million US middle and high school students reported current e-cigarette use in 2024, according to the Centers for Disease Control and Prevention. Flavoured products — mango, mint, strawberry — remain the most popular among youth, and many teenagers underestimate the nicotine concentrations in the devices they use.

Indian-American families face a particular version of this challenge. Cultural conversations about substance use in South Asian households often focus on alcohol and drugs, while vaping occupies a perceptual blind spot — it does not smell like cigarettes, it does not look like cigarettes, and many parents do not recognise the sleek, USB-shaped devices that their children carry.

Research consistently shows that Asian-American adolescents are among the fastest-growing demographics for e-cigarette use. The stigma around traditional smoking in South Asian culture may paradoxically make vaping more attractive to teenagers looking for a substance that their parents will not immediately recognise or object to.

## Dual Use Makes Everything Worse

The review also highlighted the growing problem of "dual use" — people who both smoke traditional cigarettes and vape. Many do so because they are trying to cut down, or because they vape in settings where smoking is prohibited.

The problem is that dual users continue exposing themselves to cigarette toxins while adding vaping-specific exposures. Multiple studies have found that dual users can have cardiovascular and respiratory risks equal to or exceeding those of smokers alone. Unless vaping completely replaces cigarettes — and for many users, it does not — the net health effect is neutral at best and potentially worse.

## What the Science Recommends

For people who have never smoked, the advice is straightforward: do not start vaping. There is no health benefit to introducing nicotine and aerosolised chemicals into lungs that were previously clear.

For smokers who switched entirely to vaping, the situation is more nuanced. Vaping is preferable to cigarettes, but the long-term goal should be complete freedom from nicotine. The FDA has approved several evidence-based cessation tools — nicotine patches, gums, lozenges, and prescription medications like varenicline and bupropion — that have stronger clinical backing than any commercial vaping product.

For parents, the review is a prompt for direct, nonjudgmental conversation. Vaping is not flavoured water vapour. It is a nicotine delivery system that contains chemicals capable of damaging DNA, and the cancer risk — while not yet fully quantified — is real enough that the world's leading carcinogenesis researchers are raising the alarm.

The review was published in *Carcinogenesis* (Oxford Academic) and covered studies from 2017 through 2025.""",
    'slug': 'vaping-e-cigarette-dna-damage-cancer-risk-carcinogenesis-review-indian-american-teens-20260529',
    'category': 'lifestyle-health',
    'sources': [
        {"name": "Carcinogenesis (Oxford Academic)", "url": "https://academic.oup.com/carcin"},
        {"name": "CNN Health", "url": "https://www.cnn.com/2026/05/28/health/vaping-smoking-nicotine-cancer-wellness"},
        {"name": "US CDC", "url": "https://www.cdc.gov/"}
    ],
    'image_url': img2_url,
    'image_caption': 'E-cigarette aerosols contain DNA-damaging compounds including formaldehyde and heavy metals.',
    'image_attribution': 'Pexels'
})


# ==============================
# ARTICLE 3 — image already uploaded
# ==============================
print("\n=== Article 3: RBI June 5 rate decision ===")
img3_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/rbi-june-5-rate-decision-nri-home-loan-deposits-remittances-rupee-oil-20260529.jpg"

a3 = publish({
    'headline': "The RBI Meets on June 5. Bond Traders Are Pricing In 100 Basis Points of Hikes. Your Home Loan, Your NRI Deposits, and Your Remittances Are All on the Table.",
    'subheadline': "Oil is above $90. The rupee just hit an all-time low. Inflation is back above 5 per cent. The Reserve Bank of India faces its hardest decision in two years — and NRIs have more at stake than most.",
    'body': """The Reserve Bank of India's Monetary Policy Committee will meet from June 3 to June 5. The decision it announces on Thursday will be the most consequential in at least two years — and the most difficult.

After cutting interest rates by a cumulative 125 basis points between February and December 2025, the RBI paused in April 2026, holding the repo rate at 5.25 per cent. At that meeting, Governor Sanjay Malhotra described the situation as a "cautious balancing act." Since then, every variable he was balancing has deteriorated.

## The Numbers That Have Changed

Brent crude, which the RBI's April projections assumed at $85 per barrel, has spent most of May above $90 and briefly touched $100 this week after fresh US military strikes near Iran's Bandar Abbas port. The Strait of Hormuz — through which roughly 14 million barrels per day of Middle Eastern oil once flowed — remains at a virtual standstill after three months of the US-Iran conflict.

The Indian rupee has weakened to 95.76 against the dollar, its lowest level on record. The one-year overnight index swap rate — a gauge of market expectations on central bank policy — rose 3 basis points to 6.19 per cent on May 28, signalling that bond traders are pricing in nearly 100 basis points of rate hikes over the next 12 months.

Wholesale inflation hit 8.3 per cent in April. CPI inflation, currently at 5.22 per cent, is forecast to breach 5 per cent again in June after the government raised petrol and diesel prices and doubled the import duty on gold to 15 per cent.

## The Split Among Forecasters

Major global banks are divided. MUFG, ANZ, and Standard Chartered have pencilled in a rate hike at the June 5 meeting — a 25-basis-point increase that would take the repo rate to 5.50 per cent. Their argument: with oil above $90, the rupee under sustained pressure, and inflation expectations unanchored, the RBI cannot afford to wait.

Domestic consensus, however, favours a hold. Icra's chief economist Aditi Nayar told PTI that the current price shock is supply-driven, fundamentally different from the simultaneous supply-and-demand shock of the Covid era. "June policy is probably too early," she said, adding that August would offer greater clarity on fuel-price transmission and the monsoon's trajectory.

The RBI itself has warned that if crude stays above $100, headline inflation could exceed 6 per cent — the upper bound of its tolerance band — for sustained periods, forcing a tightening cycle that would be the first since 2022-23.

## What a Rate Hike Would Mean for NRI Money

For the roughly 32 million Indians living abroad, the June 5 decision touches at least four financial channels.

**Home loans.** A 25-basis-point hike would push the average floating home loan rate from approximately 8.75 per cent to 9.00 per cent. For a ₹50-lakh, 20-year loan, the monthly EMI would rise by roughly ₹800 — not catastrophic in isolation, but significant after nearly five years of rate volatility. NRIs with home loans in India should check whether their bank has passed through the full 125 basis points of cuts delivered since February 2025. Many have not.

**NRI deposits.** Higher rates are good news for NRI fixed deposits. Banks typically raise FCNR(B) and NRE deposit rates within weeks of a repo rate increase. Current one-year NRE FD rates hover around 6.5–7.0 per cent. A hike could push them toward 7.25 per cent — attractive for dollar-earners parking money in India, especially with the rupee at historic lows offering a favourable conversion.

**Remittances.** The rupee at 95.76 means every dollar sent home buys more rupees than ever before. But a rate hike, if it stabilises the rupee, could reduce that advantage. NRIs who have been delaying large remittances — for property purchases, family support, or investment — may want to act before the RBI's decision. The $5 billion FX swap the RBI conducted this week, which was subscribed nearly twice over, suggests the central bank is already laying the groundwork for rupee defence.

**Indian equity.** Foreign investors have pulled $23 billion from Indian equities in the current fiscal year. A rate hike could accelerate the exodus in the short term, but if it succeeds in anchoring inflation expectations, it may stabilise markets by August. For NRI investors with SIPs or direct equity exposure, the June 5 decision is less about the immediate market reaction and more about the RBI's forward guidance — specifically whether it signals a one-off adjustment or the start of a tightening cycle.

## The Bigger Picture

The June 5 decision will not happen in isolation. The US Federal Reserve meets on June 17, and there is currently less than a 2 per cent chance of a rate cut at that meeting. Fed board member Lisa Cook said this week that if disinflation does not resume, she would be "prepared to raise rates." Sri Lanka already delivered a surprise 100-basis-point hike. The Philippines is considering an off-cycle increase.

India's central bank is caught between an economy that still needs growth support — GDP growth has been revised down to 6.3 per cent for FY27 — and inflation that is being driven by forces entirely outside its control. Oil prices, geopolitical conflict, and currency pressure are not problems that interest rates can solve. But they may be problems that interest rates can contain.

The decision drops on June 5. If you have money moving between the US and India, the next seven days are worth paying attention to.""",
    'slug': 'rbi-june-5-rate-decision-nri-home-loan-deposits-remittances-rupee-oil-20260529',
    'category': 'markets-finance',
    'sources': [
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "Upstox / PTI", "url": "https://upstox.com/news/personal-finance/financial-regulations/rbi-mpc-june-2026-no-emi-change-expected-fd-rates-steady-for-now-inflation-outlook-in-focus/article-194409/"},
        {"name": "Barron's", "url": "https://www.barrons.com/"}
    ],
    'image_url': img3_url,
    'image_caption': 'The RBI faces its most consequential monetary policy decision in two years as oil, inflation, and the rupee converge.',
    'image_attribution': 'Pexels'
})

print("\n" + "=" * 60)
print(f"RESULTS: {sum(1 for x in [a1, a2, a3] if x)}/3 published")
for slug, aid in [
    ('yale-leisure-exercise', a1),
    ('vaping-cancer-risk', a2),
    ('rbi-june-5', a3)
]:
    status = f"✓ {aid}" if aid else "✗ failed"
    print(f"  {slug}: {status}")
print("=" * 60)
