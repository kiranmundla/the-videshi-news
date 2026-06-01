#!/usr/bin/env python3
"""Lifestyle & Markets writer — 2026-06-01 run"""

import json, os, uuid, subprocess, re, datetime, urllib.parse, requests

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
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

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels using curl (urllib gets 403)."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if url:
                    # Validate image
                    check = subprocess.run(
                        ['curl', '-sS', '-I', url],
                        capture_output=True, text=True, timeout=10
                    )
                    headers_text = check.stdout
                    if '200' in headers_text.split('\n')[0]:
                        # Check content length
                        for line in headers_text.split('\n'):
                            if line.lower().startswith('content-length:'):
                                size = int(line.split(':')[1].strip())
                                if size > 5000:
                                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                                    return url
                    # If no content-length header, still use it (Pexels URLs are reliable)
                    if 'images.pexels.com' in url:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        # Download image using curl
        tmp_path = f'/tmp/{filename}'
        dl = subprocess.run(
            ['curl', '-sS', '-L', '-o', tmp_path, image_url],
            capture_output=True, text=True, timeout=30
        )
        
        # Check file size
        if not os.path.exists(tmp_path) or os.path.getsize(tmp_path) < 5000:
            print(f"  ⚠ Downloaded file too small or missing: {tmp_path}")
            return image_url  # Fall back to direct URL
        
        # Upload to Supabase storage
        upload = subprocess.run(
            ['curl', '-sS', '-X', 'POST',
             f'{SUPABASE_URL}/storage/v1/object/article-images/{filename}',
             '-H', f'Authorization: Bearer {SUPABASE_KEY}',
             '-H', 'Content-Type: image/jpeg',
             '-H', 'x-upsert: true',
             '--data-binary', f'@{tmp_path}'],
            capture_output=True, text=True, timeout=30
        )
        
        resp = json.loads(upload.stdout) if upload.stdout else {}
        if 'Key' in resp or 'Id' in resp:
            public_url = f'{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}'
            print(f"  ✓ Uploaded to Supabase storage: {public_url[:80]}...")
            os.remove(tmp_path)
            return public_url
        else:
            print(f"  ⚠ Upload response: {upload.stdout[:200]}")
            os.remove(tmp_path)
            return image_url  # Fall back to Pexels URL (permanent)
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return image_url

def insert_article(article):
    """Insert article into Supabase."""
    result = subprocess.run(
        ['curl', '-sS', '-X', 'POST',
         f'{SUPABASE_URL}/rest/v1/p2_articles',
         '-H', f'apikey: {SUPABASE_KEY}',
         '-H', f'Authorization: Bearer {SUPABASE_KEY}',
         '-H', 'Content-Type: application/json',
         '-H', 'Prefer: return=representation',
         '-d', json.dumps(article)],
        capture_output=True, text=True, timeout=30
    )
    return result.stdout

# ============================================================
# ARTICLE 1: India Heatwave (lifestyle-health)
# ============================================================

art1_id = str(uuid.uuid4())
art1_slug = "india-heatwave-2248-dead-second-deadliest-history-diaspora-families-what-to-know-20260601"
art1_headline = "India's Deadliest Heatwave in 28 Years Has Killed More Than 2,200 People. If You Have Family Back Home, Here Is What You Need to Know."
art1_subheadline = "Roads have melted in Delhi. Temperatures hit 50°C. Andhra Pradesh and Telangana account for more than 80 per cent of the dead. Monsoon relief may still be weeks away."

art1_body = """The numbers have been climbing for a week. On 24 May, the death toll stood at 330. By 27 May it had crossed 1,000. On 31 May, the Skymet Meteorology Division reported the count at 2,248 — making this the second-deadliest heatwave in Indian history, behind only the 2,541 killed in 1998, and the fifth-deadliest heatwave ever recorded globally, according to the Emergency Events Database maintained by the Centre for Research on the Epidemiology of Disasters in Brussels.

The worst damage has been concentrated in two states. Andhra Pradesh alone has recorded more than 1,334 deaths. Neighbouring Telangana has reported at least 440. Odisha has counted 43, Gujarat 7, and scattered deaths have been confirmed in Delhi, West Bengal, and Bihar. The true toll is almost certainly higher. India's heat-death reporting system is widely considered to undercount by large margins, particularly among rural labourers and homeless populations who account for the majority of victims.

## What the Data Shows

A peer-reviewed study published in *Frontiers in Environmental Health* by researchers at the University of California, Berkeley, estimates that a single day of extreme heat causes approximately 3,400 excess deaths across India. A five-day heatwave causes nearly 30,000. Uttar Pradesh alone — India's most populous state — accounts for roughly 8,100 of those deaths over five consecutive extreme-heat days. Districts like Ahmedabad, Jaipur, and Surat each exceed 250 excess deaths in a single event.

These are not projections for a future climate. They are modelled estimates for the India that exists now, using current population data and mortality rates from the Civil Registration System.

The current heatwave has been running since mid-April. Daily maximum temperatures have exceeded 46°C in dozens of cities. Khammam in Telangana hit 48°C on 24 May, shattering its all-time record of 47.2°C set in 1947. In Delhi, asphalt road surfaces melted, disrupting road markings. In Kolkata, cab drivers refused to work between 11 AM and 4 PM.

## Why This Heatwave Is Different

Three factors have converged. First, a developing El Niño has amplified pre-monsoon heat, pushing temperatures 5–8°C above seasonal norms in several regions. Second, hot and dry winds blowing from Pakistan's Sindh province across the northern plains have intensified conditions in states that might otherwise have received some respite. Third, the monsoon — which normally arrives in Kerala by early June and pushes north through the month — is forecast to deliver its weakest season in 11 years, at just 90 per cent of the long-period average.

That means the heat relief millions of Indians are waiting for may arrive late, and when it does, the rains may not be enough.

## The People Most at Risk

Construction workers, agricultural labourers, and homeless populations account for the overwhelming majority of heatwave fatalities. State governments in Telangana and Andhra Pradesh have urged people to stay indoors between 9 AM and 4 PM, wear loose clothing, and keep hydrated. Hospitals have been overwhelmed with heatstroke cases.

India's record-breaking electricity demand — driven by air conditioners running at full capacity — has triggered power cuts in parts of the country, leaving the most vulnerable without even basic cooling.

## What Diaspora Families Should Do

If you have elderly parents, grandparents, or extended family in India — particularly in Andhra Pradesh, Telangana, Odisha, Uttar Pradesh, Madhya Pradesh, Rajasthan, or Bihar — this is the week to call.

The most effective actions are practical. Ensure they have access to clean drinking water, ORS packets, and a functioning fan or cooler. Urge them to avoid outdoor activity during peak hours. For those in areas experiencing power cuts, a battery-powered fan or a UPS system for existing coolers can be the difference between manageable heat and a medical emergency.

Heat does not kill dramatically. It kills quietly — through dehydration, heatstroke, and cardiovascular failure that builds over days. The elderly and those with pre-existing conditions are most at risk, and they are often the last to seek medical help.

The pre-monsoon rains that began arriving in parts of Karnataka and Kerala over the weekend may bring temporary relief to southern states. But for central and northern India, the India Meteorological Department expects heatwave conditions to persist through much of June, with above-normal temperatures forecast in at least eight states.

The monsoon, when it comes, may not solve the problem. It may simply replace one crisis with another."""

art1_sources = json.dumps([
    {"name": "Skymet Weather", "url": "https://www.skymetweather.com/content/weather-news-and-analysis/heat-wave-intensifies-across-india-claims-over-330-lives/"},
    {"name": "Frontiers in Environmental Health (UC Berkeley study)", "url": "https://www.frontiersin.org/articles/10.3389/fenvh.2026.1595789/full"},
    {"name": "Carbon Brief", "url": "https://www.carbonbrief.org/debriefed-29-may-2026"},
    {"name": "India Meteorological Department", "url": "https://mausam.imd.gov.in/"}
])

# ============================================================
# ARTICLE 2: India Monsoon Forecast (markets-finance)
# ============================================================

art2_id = str(uuid.uuid4())
art2_slug = "india-weakest-monsoon-11-years-food-inflation-el-nino-nri-investors-20260601"
art2_headline = "India Just Forecast Its Weakest Monsoon in 11 Years. Food Prices, the Rupee, and Half the Country's Livelihoods Are in the Path."
art2_subheadline = "The IMD has cut its monsoon outlook to 90 per cent of normal. El Niño is forming. Inflation could hit 5.5 per cent. NRI investors with exposure to India need to pay attention."

art2_body = """The India Meteorological Department updated its long-range monsoon forecast on Friday, and the numbers moved in the wrong direction. Seasonal rainfall between June and September is now expected at 90 per cent of the long-period average, down from 92 per cent projected in April. If this holds, 2026 would be the driest monsoon year since 2015, when rainfall reached just 86 per cent of normal.

There is an 84 per cent probability that the monsoon will be below normal. Northwest India — which includes Punjab, Haryana, and Rajasthan — is expected to be the driest region. June rainfall, when kharif sowing begins and farmers make their most consequential planting decisions, is also forecast below 92 per cent of the long-period average.

The monsoon is not a weather event in India. It is an economic event. It delivers 70 per cent of the country's annual rainfall, replenishes reservoirs, recharges groundwater, and sustains nearly half the population that earns its livelihood from farming. Nearly half of India's farmland still lacks irrigation, which means crop yields are directly tethered to how much it rains and when.

## What Is Driving the Deficit

A developing El Niño is the primary factor. The IMD says El Niño conditions are likely to form during the monsoon season, with intensity ranging from moderate to strong in the second half (August–September). The Indian Ocean Dipole, which can sometimes offset El Niño's drying effect, is currently neutral and expected to remain so.

The last time India dealt with consecutive weak monsoons was 2014–2015, when rainfall stood at 88 and 86 per cent of the long-period average. Those years saw significant agricultural stress, rural distress, and a spike in food prices that took months to work through the economy.

## The Inflation Equation

India's retail inflation stood at 3.48 per cent in April, well below the Reserve Bank of India's 4 per cent target. But the outlook is deteriorating on multiple fronts simultaneously.

Gaura Sengupta, chief economist at IDFC First Bank, warned that a deficient monsoon — particularly in the crucial July–August months — could push inflation closer to 5.5 per cent if food prices spike. India's finance ministry, in its monthly economic report released Saturday, was blunter: the confluence of elevated global energy prices, a depreciating rupee, rising upstream cost pressures, and a below-normal monsoon "calls for sustained policy vigilance."

The Strait of Hormuz disruption remains what the finance ministry called the "single most consequential variable" for India's external and price outlook. India imports more than 80 per cent of its crude oil, and elevated energy costs are already feeding through to transport, fertiliser, and food-related costs.

## What This Means for NRI Investors

Three areas deserve attention.

**Agricultural and FMCG stocks.** Companies dependent on rural demand — consumer staples, fertiliser producers, and agricultural input firms — are directly exposed to monsoon outcomes. Consumer staples already lost more than 3 per cent in May while tech rallied 16 per cent. A weak monsoon would extend that underperformance.

**RBI rate path.** The RBI's Monetary Policy Committee meets this week. With inflation still below target, there was room for an accommodative stance. But a weak monsoon forecast changes the calculus. If food inflation materialises in July–August, the window for rate cuts narrows significantly. The RBI may hold steady rather than ease, which would weigh on India's growth-sensitive sectors.

**The rupee.** A combination of elevated oil prices ($88.83 per barrel WTI), a potential food-price shock, and hawkish US rates (10-year Treasury yields at 4.47 per cent, 50-50 chance of a Fed hike by year-end) puts further pressure on the rupee. NRIs sending remittances to India may get more favourable exchange rates in the near term, but the underlying stress on the economy is not a positive signal for long-term India allocations.

## The Broader Picture

The Wall Street Journal reported this week that El Niño, supercharged by climate change, is "the next risk hanging over the global economy." The effects extend well beyond India — during the last El Niño cycle in 2022–2023, India banned rice exports, dengue epidemics surged, the Panama Canal hit low water levels, and chocolate prices spiked globally.

For India specifically, the convergence of a record heatwave that has killed more than 2,200 people, a weakening monsoon, and energy costs driven by the Middle East conflict creates what economists call a "triple squeeze" on the agricultural economy. Half the country is already burning. The rain that could provide relief is forecast to be the weakest in over a decade.

India's nearly $4 trillion economy has shown resilience before. But as the finance ministry itself acknowledged this week, the near-term outlook is one of "cautious resilience" — a phrase that means the risks are real and the margin for error is thin."""

art2_sources = json.dumps([
    {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-warns-weakest-monsoon-11-years-inflation-risks-rise-2026-05-29/"},
    {"name": "Mint", "url": "https://www.livemint.com/news/india/is-2026-heading-for-its-driest-monsoon-since-2015-el-nino-imd-monsoon-forecast-11748510420437.html"},
    {"name": "Reuters (Finance Ministry report)", "url": "https://www.reuters.com/world/india/india-says-retail-inflation-may-accelerate-weak-monsoon-fuel-price-rise-2026-05-31/"},
    {"name": "Wall Street Journal", "url": "https://www.wsj.com/economy/global/el-nino-is-the-next-risk-hanging-over-the-global-economy-c213df40"}
])

# ============================================================
# ARTICLE 3: Vaping Cancer Risk (lifestyle-health)
# ============================================================

art3_id = str(uuid.uuid4())
art3_slug = "vaping-cancer-risk-carcinogenesis-review-dna-damage-south-asian-parents-teens-20260601"
art3_headline = "A Major Scientific Review Just Found That Vaping Can Damage DNA and May Cause Cancer. South Asian Parents Need to Read This."
art3_subheadline = "The review, published in Carcinogenesis, examined laboratory, animal, and human studies. The evidence links e-cigarette aerosols to cancers of the lung, mouth, and bladder."

art3_body = """Vaping has been marketed for years as the safer alternative to smoking. A comprehensive new review, published in the journal *Carcinogenesis*, says the picture is more complicated than that — and more alarming than most parents realise.

The paper is not a single experiment. It is a large-scale scientific review that synthesised evidence from laboratory studies, animal models, human biomarker research, and epidemiological data to assess how e-cigarettes affect cells and tissues in ways linked to cancer development. The findings are significant enough that CNN's wellness expert Dr. Leana Wen, a former Baltimore health commissioner, called them a serious concern for parents.

## What the Review Found

E-cigarette aerosols can damage DNA and trigger chronic inflammation — two processes that are among the earliest biological steps in cancer formation. The review documented that vaping aerosols contain known or suspected carcinogenic compounds, including formaldehyde, acetaldehyde, and heavy metals such as nickel, chromium, and lead that leach from the heating elements inside devices.

The evidence suggests associations between vaping and cancers of the lungs, mouth, and bladder. These are not theoretical projections based on chemical exposure alone. Human biomarker studies show measurable DNA damage in the cells of people who vape regularly.

The authors were careful to note limitations. Many of the strongest findings come from laboratory and animal models, and long-term epidemiological data on cancer incidence in vapers is still limited — e-cigarettes have only been widely used for about 15 years. But the mechanistic evidence is now substantial enough that the authors concluded vaping should not be treated as a risk-free activity.

## Why This Matters for South Asian Families

The data on South Asian teen vaping in the United States is sparse, but the structural factors are concerning. A 2024 CDC Youth Tobacco Survey found that more than 1.6 million middle and high school students in the US used e-cigarettes, with disposable devices and flavoured products the primary drivers. Among Asian American and Pacific Islander youth, vaping rates have been rising faster than in several other demographic groups.

For South Asian parents, the challenge is cultural. Smoking is widely stigmatised in Indian, Pakistani, and Bangladeshi households. Many parents know to watch for cigarettes. Far fewer are alert to vaping, which produces no lasting smell, can be done discreetly, and is aggressively marketed through social media channels that teenagers consume but parents often do not.

The devices themselves have become nearly invisible. Pod-based e-cigarettes like JUUL have given way to disposable devices that resemble USB drives, highlighters, or pens. A teenager can use one in a school bathroom, bedroom, or car without leaving any visible evidence.

## What the Science Does Not Yet Know

The review acknowledges several gaps. Cancer typically takes decades to develop, and e-cigarettes have not been in widespread use long enough to produce the kind of large-scale cancer incidence data that exists for traditional cigarettes. The relative risk of vaping versus smoking is still lower for most measures — but "safer than cigarettes" is not the same as "safe."

Dr. Wen emphasised that the framing matters. "I would not tell a current heavy smoker to avoid switching to e-cigarettes if that is the only way they will quit," she said. "But I would absolutely tell a teenager who has never smoked that vaping is not harmless and carries real health risks."

The review also found that dual use — vaping and smoking — may compound risks rather than reduce them. A significant percentage of young people who start vaping eventually progress to combustible cigarettes, which reverses any harm-reduction benefit.

## What Parents Can Do

The US Surgeon General declared youth screen time a public health crisis just this past week. Vaping has been on that same regulatory radar for years, but enforcement has not kept pace with the industry's innovation. As of 2026, flavoured disposable e-cigarettes remain widely available despite partial FDA enforcement actions.

For South Asian parents, the conversation needs to be direct and specific. Research suggests that teens respond better to factual health information than to moral arguments. Sharing that vaping causes DNA damage and contains carcinogenic heavy metals is more effective than telling them it is "bad."

Know what the devices look like. Ask your children's school about its vaping policy and whether it has detection systems in restrooms. If your teenager has friends who vape, assume they have been exposed and treat the conversation as urgent rather than precautionary.

The *Carcinogenesis* review does not call vaping a guaranteed cancer risk. But it makes clear that the biological mechanisms are present, the harmful compounds are real, and the long-term consequences are still unknown. For a generation of South Asian teens growing up in the US, UK, and Canada, that uncertainty is itself a reason for caution."""

art3_sources = json.dumps([
    {"name": "Carcinogenesis (Oxford Academic)", "url": "https://academic.oup.com/carcin/advance-article/2026"},
    {"name": "CNN Health", "url": "https://www.cnn.com/2026/05/28/health/vaping-cancer-risk-study-wellness"},
    {"name": "CDC Youth Tobacco Survey", "url": "https://www.cdc.gov/tobacco/data_statistics/surveys/nyts/index.htm"}
])


# ============================================================
# IMAGE SOURCING
# ============================================================

print("\n=== Sourcing images ===\n")

# Article 1: India heatwave — no specific person, use Pexels
print("Article 1 (Heatwave):")
img1 = fetch_pexels_image("India extreme heat sun dry cracked earth", "scorching heat wave drought summer")
if img1:
    img1_final = upload_to_supabase_storage(img1, f"{art1_id}.jpg")
else:
    img1_final = None
    print("  ✗ No image found for heatwave article")

# Article 2: India monsoon/agriculture — no specific person, use Pexels
print("\nArticle 2 (Monsoon):")
img2 = fetch_pexels_image("Indian farmer dry field agriculture drought", "monsoon rain farm India")
if img2:
    img2_final = upload_to_supabase_storage(img2, f"{art2_id}.jpg")
else:
    img2_final = None
    print("  ✗ No image found for monsoon article")

# Article 3: Vaping — no specific person, use Pexels
print("\nArticle 3 (Vaping):")
img3 = fetch_pexels_image("vaping e-cigarette smoke teenager", "electronic cigarette vape device")
if img3:
    img3_final = upload_to_supabase_storage(img3, f"{art3_id}.jpg")
else:
    img3_final = None
    print("  ✗ No image found for vaping article")


# ============================================================
# INSERT ARTICLES
# ============================================================

print("\n=== Inserting articles ===\n")

now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

articles = [
    {
        "id": art1_id,
        "headline": art1_headline,
        "subheadline": art1_subheadline,
        "body": art1_body,
        "slug": art1_slug,
        "category": "lifestyle-health",
        "status": "published",
        "published_at": now,
        "sources": art1_sources,
        "image_url": img1_final,
        "image_attribution": "Pexels" if img1_final else None,
        "is_editorial": False,
        "author": "The Videshi"
    },
    {
        "id": art2_id,
        "headline": art2_headline,
        "subheadline": art2_subheadline,
        "body": art2_body,
        "slug": art2_slug,
        "category": "markets-finance",
        "status": "published",
        "published_at": now,
        "sources": art2_sources,
        "image_url": img2_final,
        "image_attribution": "Pexels" if img2_final else None,
        "is_editorial": False,
        "author": "The Videshi"
    },
    {
        "id": art3_id,
        "headline": art3_headline,
        "subheadline": art3_subheadline,
        "body": art3_body,
        "slug": art3_slug,
        "category": "lifestyle-health",
        "status": "published",
        "published_at": now,
        "sources": art3_sources,
        "image_url": img3_final,
        "image_attribution": "Pexels" if img3_final else None,
        "is_editorial": False
    }
]

for i, article in enumerate(articles, 1):
    # Remove None values
    article = {k: v for k, v in article.items() if v is not None}
    
    print(f"Inserting article {i}: {article['headline'][:60]}...")
    result = insert_article(article)
    try:
        resp = json.loads(result)
        if isinstance(resp, list) and len(resp) > 0:
            print(f"  ✓ Inserted: {resp[0].get('id', 'unknown')}")
        elif isinstance(resp, dict) and resp.get('message'):
            print(f"  ✗ Error: {resp.get('message', 'unknown')}")
        else:
            print(f"  Response: {result[:200]}")
    except Exception as e:
        print(f"  ✗ Parse error: {e}")
        print(f"  Raw: {result[:300]}")

print("\n=== Done ===")
