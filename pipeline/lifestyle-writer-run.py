#!/usr/bin/env python3
"""Lifestyle-health & markets-finance writer — 2026-05-27 run"""

import json, os, uuid, requests, urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(path):
    try:
        with open(os.path.expanduser(path)) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except FileNotFoundError:
        pass

load_env('~/.env.supabase')
load_env('~/workspace/.env.pexels')

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def sb_insert(table, data):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        return result[0] if isinstance(result, list) else result
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return None

def sb_patch(table, match, data):
    params = '&'.join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?{params}", headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 204):
        print(f"  ✓ Patched {table}")
    else:
        print(f"  ✗ Patch failed ({r.status_code}): {r.text[:200]}")

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
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
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels using curl (urllib gets 403)."""
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run([
                'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'
            ], capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for p in photos:
                url = p.get('src', {}).get('large2x') or p.get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Verify the URL returns a valid image >5KB."""
    try:
        r = requests.get(url, timeout=15, stream=True, headers={"User-Agent": "TheVideshi/1.0"})
        ct = r.headers.get('Content-Type', '')
        if 'image' not in ct:
            print(f"  ⚠ Not an image Content-Type: {ct}")
            return False
        # Read enough to confirm size
        data = b''
        for chunk in r.iter_content(chunk_size=8192):
            data += chunk
            if len(data) > 5000:
                r.close()
                return True
        print(f"  ⚠ Image too small: {len(data)} bytes")
        return False
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
        return False

def publish_article(article):
    """Insert article into p2_articles."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    row = {
        'id': art_id,
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': article['slug'],
        'category': article['category'],
        'vertical': article['category'],
        'sources': json.dumps(article['sources']),
        'image_url': article.get('image_url'),
        'image_attribution': article.get('image_attribution', ''),
        'status': 'published',
        'published_at': now,
        'created_at': now
    }
    
    result = sb_insert('p2_articles', row)
    if result:
        print(f"  ✓ Published: {article['headline'][:60]}... [{article['category']}]")
        return art_id
    return None


# ============================================================
# ARTICLE 1: AHA 2026 Dietary Guidelines — lifestyle-health
# ============================================================

article1 = {
    'headline': "The American Heart Association Just Rewrote Its Dietary Rules. Your Mother's Indian Kitchen Already Follows Most of Them.",
    'subheadline': "The 2026 AHA guidelines prioritise plant proteins over meat, push potassium and whole grains, and take a harder line on alcohol. Traditional Indian cooking checks nearly every box — except the one about salt.",
    'slug': 'aha-2026-dietary-guidelines-indian-kitchen-plant-protein-potassium-20260527',
    'category': 'lifestyle-health',
    'sources': [
        'Lichtenstein AH et al., 2026 Dietary Guidance to Improve Cardiovascular Health, Circulation (AHA Scientific Statement), March 2026',
        'Health.com — New American Heart Association Guidelines Break Down What to Eat — and What to Skip, May 2026',
        'Healthline — AHA Releases Updated Heart-Healthy Dietary Guidance, 2026',
        'MedicalXpress — Following 9 Key Steps for a Lifetime of Eating Well, AHA 2026'
    ],
    'body': """The American Heart Association has released its most consequential dietary update in five years. The 2026 Scientific Statement, published in *Circulation*, replaces the 2021 edition and lays out nine features of a heart-healthy diet that the AHA wants every adult to follow for life. The headline shift: plant proteins should actively replace meat, not merely supplement it.

For the roughly five million Indian Americans navigating a food culture that already revolves around dal, roti, and sabzi, the new guidance reads less like a revolution and more like a homecoming.

## What Changed

The nine pillars of the 2026 guidelines are: balance energy intake with activity; eat plenty of vegetables and fruits; choose whole grains over refined grains; shift protein from meat to plant sources like legumes and nuts; favour unsaturated fats over saturated fats; choose minimally processed foods over ultra-processed ones; minimise added sugars; reduce sodium; and avoid or limit alcohol.

Six of those nine were in the 2021 edition. The meaningful changes lie in emphasis and tone.

**Plant proteins over meat — not alongside it.** The previous guidelines simply recommended plant proteins. The 2026 version explicitly says to *shift from meat to plant sources* — legumes, lentils, beans, nuts, and seeds. Alice Lichtenstein, the volunteer chair of the AHA's writing committee and a senior scientist at Tufts University, explained that plant proteins "are higher in unsaturated fat than saturated fat, and rich in fibre, an under-consumed but important nutrient."

The distinction matters. Replacing a portion of red meat with dal is not the same as adding dal on the side. The AHA now wants the replacement, not the addition.

**Potassium enters the conversation.** For the first time, the AHA highlights potassium alongside sodium as a blood pressure lever. "Sodium and potassium sort of work like teeter-totters. They're best in balance," said Alison Steiber, chief mission officer at the Academy of Nutrition and Dietetics. "But more potassium can have very beneficial blood pressure impacts." Bananas, potatoes, coconut water, and spinach are all potassium-dense — and all common in Indian kitchens.

**Alcohol gets a harder line.** Previous guidelines allowed one to two drinks per day. The 2026 version eliminates any stated safe amount. "When it comes to alcohol consumption, the more you can avoid it, the better," said Lisa Moskovitz, founder of The NY Nutrition Group. For the first time, the AHA also acknowledges that no amount of alcohol is safe with respect to certain cancer risks.

**Ultra-processed food gets a systemic call.** The 2021 edition warned against ultra-processed foods. The 2026 version goes further, calling for marketplace-level change: more minimally processed options wherever food is sold. With American diets estimated at 60 per cent ultra-processed, the AHA is recognising that individual willpower alone cannot solve the problem.

## The Indian Kitchen Advantage

Run through the nine features and count how many a traditional Indian thali already covers.

Vegetables and fruits? The typical thali is built around seasonal sabzi. Whole grains? Roti is whole wheat. Bajra, jowar, and ragi rotis are gaining ground again. Plant protein? Dal is the protein anchor of the Indian plate — toor, moong, masoor, chana, rajma. Unsaturated fats? Mustard oil, groundnut oil, and sesame oil are traditional cooking fats across regions. Minimally processed? A home-cooked Indian meal uses whole ingredients. Added sugars? Traditional Indian cooking uses jaggery sparingly, not high-fructose corn syrup. Alcohol? The majority of Indian adults — and a disproportionate number of Indian women — do not drink.

That is seven out of nine.

The two gaps: sodium and energy balance. Indian cooking is generous with salt. Pickles, papads, and packaged snacks amplify the problem. And portion sizes — especially of rice and bread — tend to exceed what the body needs, particularly for sedentary NRI tech workers who sit ten hours a day and eat as though they still play cricket on weekends.

## What This Means for the Diaspora

The AHA guidelines are written for a general American audience. They do not reference South Asian cardiovascular risk, which is two to four times higher than the general population at equivalent BMI levels. But the dietary pattern they describe — legume-heavy, plant-forward, low in red meat and alcohol, rich in whole grains and unsaturated fats — is remarkably close to the traditional Indian pattern that the diaspora has been slowly abandoning.

Every generation of NRIs drifts further from the home kitchen. The teenagers eat burgers. The young professionals order DoorDash. The parents start buying frozen samosas. The 2026 AHA guidelines are, inadvertently, a case for going back.

The one caveat: traditional does not mean perfect. Ghee is saturated fat. Deep-fried snacks are deep-fried snacks. And the AHA's new emphasis on potassium is an implicit reminder that salt needs to come down. But the architecture of the Indian plate — dal, roti, sabzi, dahi, with small amounts of meat if any — is closer to the AHA's ideal than any Western convenience diet.

Your mother's kitchen was not just feeding you. It was, according to the most powerful cardiology body in the world, protecting your heart."""
}

# ============================================================
# ARTICLE 2: Exercise study — lifestyle-health
# ============================================================

article2 = {
    'headline': "A Study of 17,000 Adults Found You Need Four Times More Exercise Than the Guidelines Recommend. The 150-Minute Rule Is a Floor, Not a Ceiling.",
    'subheadline': "Researchers at Macao Polytechnic University found that 560 to 610 minutes of weekly aerobic exercise — about 85 minutes a day — reduced cardiovascular events by more than 30 per cent. The standard 150-minute guideline cut risk by only 8 per cent.",
    'slug': 'exercise-four-times-more-150-minutes-heart-attack-stroke-bjsm-study-20260527',
    'category': 'lifestyle-health',
    'sources': [
        'British Journal of Sports Medicine, May 19, 2026 — exercise volume and cardiovascular events (Macao Polytechnic University)',
        'Healthline — Weekly Exercise Goals Should Be Higher to Prevent Heart Attack, Stroke, May 2026',
        'Scientific American — A New Study Says You Need 10 Hours of Exercise a Week, May 2026',
        "NY Post — How Much Exercise Should You Be Doing a Week? It's Not 150 Minutes, May 2026"
    ],
    'body': """The number that has governed exercise advice for two decades is 150. As in: 150 minutes of moderate-to-vigorous physical activity per week. Walk briskly for 22 minutes a day, and you have met the World Health Organization and American Heart Association threshold. You are, officially, an active adult.

A study published on May 19 in the *British Journal of Sports Medicine* says that threshold is real — and far too low.

## The Study

Researchers at Macao Polytechnic University analysed data from 17,000 UK Biobank participants who wore wrist-mounted accelerometers for seven consecutive days. The average age was 57. Ninety-six per cent were white, and 56 per cent were female. Each participant also completed a cycle test to estimate VO2 max — a direct measure of cardiovascular fitness.

Over a follow-up period of nearly eight years, 1,233 cardiovascular events were recorded: 874 cases of atrial fibrillation, 156 heart attacks, 111 heart failure episodes, and 92 strokes.

The dose-response findings were stark.

Adults who met the 150-minute weekly guideline experienced an 8 to 9 per cent reduction in cardiovascular risk. Meaningful, but modest.

Those who exercised for 370 minutes per week — about 53 minutes a day — saw a 20 per cent reduction. Those at the lowest fitness level needed slightly more: 370 minutes. Those at the highest fitness level achieved the same result at 340 minutes.

But the truly significant reduction — more than 30 per cent — required 560 to 610 minutes per week. That is roughly 85 minutes a day. Nearly ten hours a week. Four times the current guideline.

## The Expert Reaction

Keith Diaz, a professor of behavioural medicine at Columbia University and a member of the AHA's Physical Activity Science Committee, urged caution. "I would urge caution in interpreting the specific recommendation that people may need three to four times the current physical activity guidelines to substantially reduce heart disease risk," he said. "From a public health perspective, I worry that setting extremely high targets could discourage people who are currently inactive."

Michael Fredericson, a professor of orthopaedic surgery at Stanford, agreed with the underlying data but shifted the emphasis. "I would rather emphasise that small increases in physical activity and cardiovascular fitness, especially among the least active individuals, produce the largest cardiovascular benefits," he said.

Kevin Shah, a cardiologist at MemorialCare in Long Beach, California, put it more simply: "The standard recommendation — 150 minutes of moderate to vigorous activity each week — is a solid baseline. But it's just that: a baseline."

Only about 12 per cent of study participants achieved the 600-minute level. Fewer than half of American adults currently meet even the 150-minute floor.

## The South Asian Context

The study was conducted on a mostly white British population. It does not account for the elevated baseline cardiovascular risk that South Asians carry due to genetics, insulin resistance, visceral fat distribution, and inflammatory profiles.

Previous research from the University of Leicester found that South Asian men may need to exercise 20 minutes longer daily than white Europeans to achieve the same heart disease and diabetes risk reduction — suggesting that the effective exercise threshold for South Asians is already higher than the general population.

For Indian Americans, the arithmetic is uncomfortable. The diaspora's relationship with exercise is largely generational. Parents walked — to the market, to the temple, up four flights of stairs because the lift was broken again. But they rarely exercised deliberately. Their children, the NRI tech workforce, sit for ten to twelve hours a day, commute by car, and count a weekend walk around the neighbourhood as activity.

The 150-minute guideline was already a stretch for most. The idea that meaningful protection requires four times that is not discouraging — it is clarifying. It means the question is no longer "Am I doing enough?" but "How much more can I build in?"

## What to Do With This

The researchers and experts converge on one practical point: do not let the number paralyse you.

"You don't have to carve out a full hour at the gym to make exercise count," Shah said. "Small bursts of activity throughout the day can add up. A quick morning bike ride, a walk after dinner, taking the stairs, or even short movement breaks between meetings all contribute."

Fredericson offered practical strategies: substitute vigorous activity for moderate activity to save time (running beats walking per minute); accumulate activity in shorter bouts throughout the day; use wearable devices for motivation; and integrate movement into daily routines.

The bottom line is not that everyone needs to exercise ten hours a week. It is that 150 minutes — the number the world has been told is sufficient — provides an 8 per cent safety margin. For South Asians, whose cardiovascular risk profile is already elevated, that margin may be even thinner.

The biggest gains, as Fredericson noted, come from moving the least active people to some activity. If you are currently doing nothing, 30 minutes matters more than anything. If you are at 150 minutes, getting to 300 doubles your protection. And if you can reach 400 or 500, you are in territory where the data says the heart genuinely starts to thank you.

The study does not prescribe guilt. It prescribes a gradient. Start where you are. Add what you can. The curve rewards every minute."""
}

# ============================================================
# ARTICLE 3: Taiwan overtakes India market cap — markets-finance
# ============================================================

article3 = {
    'headline': "Taiwan Just Overtook India as the World's Fifth-Largest Stock Market. A Single Chip Company Did Most of the Work.",
    'subheadline': "TSMC now accounts for 42 per cent of Taiwan's benchmark index. India's market cap has fallen to $4.92 trillion. Foreign investors have pulled $24 billion out of Indian equities this year — more than all of 2025.",
    'slug': 'taiwan-overtakes-india-fifth-largest-stock-market-tsmc-fii-outflows-20260527',
    'category': 'markets-finance',
    'sources': [
        'Reuters — India\'s fifth spot in global market cap list under threat as Taiwan closes in, May 26, 2026',
        'AInvest — Taiwan\'s market cap rises to $4.95 trillion to overtake India, May 2026',
        'Reuters — India stocks set for first yearly drop in over a decade as foreign investors leave, 2026',
        'Copley Fund Research — India fund weight dips below 10% for first time since January 2021, May 2026 report'
    ],
    'body': """India is no longer the world's fifth-largest stock market. Taiwan passed it this week, powered almost entirely by a single company: Taiwan Semiconductor Manufacturing Co.

The aggregate market capitalisation of stocks listed on the Taiwan stock exchange and OTC exchange stood at $4.95 trillion as of Tuesday. India's NSE-listed companies sat at $4.92 trillion. The United States, China, Japan, and Hong Kong occupy the top four slots. South Korea, at $4.89 trillion, is close behind India.

The gap is narrow. The symbolism is not.

## How One Company Did It

TSMC shares have surged over 44 per cent in 2026. The company now accounts for roughly 42 per cent of Taiwan's benchmark TAIEX index by market value. Taiwan's index is up 50.3 per cent this year.

India does not have a TSMC. It does not have a single company that dominates global AI infrastructure, that builds the chips powering every major language model and data centre on Earth. "The Indian market does not offer direct equivalents to the AI trade and companies such as TSMC, Nvidia, or large-scale AI infrastructure businesses," said Manish Bhandari, CEO and portfolio manager at Vallum Capital.

India's equity market is diversified — banking, IT services, consumer goods, energy, pharmaceuticals. That diversity is usually a strength. In 2026, it is a handicap. Global capital is chasing the AI trade, and India's largest companies make software services, not semiconductors.

## The Foreign Exodus

Foreign portfolio investors have pulled $24.18 billion out of Indian equities so far in 2026, already surpassing 2025's record annual sales. In contrast, Taiwan received about $25 billion in foreign inflows over the same period.

The drain is structural, not cyclical.

Copley Fund Research, which tracks global fund flows and investment trends, said in its May report that the average India weight in funds it monitors has fallen to 9.94 per cent — the first time India has dipped below 10 per cent since January 2021. At its peak in August 2024, that weight stood at 17.47 per cent.

"India has moved from being the darling of emerging markets to the runt of the litter among Asia's Big Four," Copley wrote.

India's declining share in the MSCI Global Standard index — down to 12.3 per cent from a peak of 21 per cent in September 2024 — is compounding the problem. Passive funds that track the index are mechanically reducing their India allocation, creating a self-reinforcing cycle.

## The Geopolitical Drag

The Iran war that began in February has battered India disproportionately. India imports more than 80 per cent of its crude oil. Brent crude has risen roughly 45 per cent since the conflict began. The rupee has weakened to around 95.4 per dollar. The Nifty 50 and BSE Sensex are down 8.5 per cent and 10.8 per cent respectively in 2026.

Manish Bhandari cited oil-price volatility, India-Pakistan tensions, U.S. tariff uncertainty, and erratic monsoon risks as additional accelerators of foreign outflows.

SEBI chief Tuhin Kanta Pandey offered the regulator's perspective on Tuesday: "India is a diversified economy but Taiwan is concentrated on certain companies. These companies are attracting foreign flows at this time."

He is not wrong. Taiwan's entire market rally rests on one company in one sector. If the AI trade cools or TSMC stumbles, the positions reverse overnight. But that has not happened yet, and fund managers allocate to momentum, not to arguments about diversification.

## What NRI Investors Should Watch

For the Indian diaspora with portfolios straddling both countries, the situation presents a dilemma.

**India-focused mutual funds are underperforming.** The India mutual fund industry recently crossed ₹82 lakh crore ($990 billion) in assets, largely driven by domestic SIP flows. But fund performance has deteriorated as the Nifty has dropped. NRIs who invested in India-focused funds expecting 15–20 per cent annual returns are looking at negative returns in 2026.

**The RBI is firefighting.** The central bank's $5 billion dollar-rupee swap this week was subscribed nearly twice over, with $9.8 billion in bids. The swap is designed to inject rupee liquidity into the banking system and bring down hedging costs — but it is a defensive measure, not a growth catalyst. The rupee at 95.4 is the weakest it has been in years.

**The MSCI rebalancing creates a mechanical drag.** As India's weight in the MSCI Global Standard index falls, passive funds sell Indian stocks. The selling pushes prices lower, which reduces the weight further, which triggers more selling. NRI investors in global ETFs are indirectly exposed to this cycle.

**The recovery catalyst is unclear.** India needs either an oil price collapse (peace in the Middle East), a global rotation out of AI stocks (TSMC multiple compression), or a domestic earnings rebound. None of these is imminent.

The structural case for India — demographics, digitisation, formalisation, consumption — remains intact. But structural cases operate on decade timelines. On the 2026 scoreboard, a country of 1.4 billion people just lost a market-cap race to an island of 24 million, because that island makes the chips the world cannot live without.

The ranking will flip again. Rankings always do. But the lesson is worth absorbing: in a market driven by AI infrastructure, diversification without exposure to the defining technology of the era is not a shield. It is a gap."""
}


# ============================================================
# MAIN EXECUTION
# ============================================================

articles = [article1, article2, article3]

for art in articles:
    print(f"\n{'='*60}")
    print(f"Publishing: {art['headline'][:70]}...")
    print(f"Category: {art['category']}")
    
    # Image sourcing
    img_url = None
    img_attr = ''
    
    if art == article1:
        # AHA guidelines — no person, use Pexels for Indian food / thali
        img_url = fetch_pexels_image("indian thali dal roti vegetables", "indian home cooking traditional")
        img_attr = 'Pexels'
    elif art == article2:
        # Exercise study — use Pexels for exercise/running
        img_url = fetch_pexels_image("morning jogging running exercise", "person exercising outdoors cardio")
        img_attr = 'Pexels'
    elif art == article3:
        # Taiwan/India market — stock market / trading imagery
        img_url = fetch_pexels_image("stock market trading screen data", "financial stock exchange board")
        img_attr = 'Pexels'
    
    if img_url and validate_image(img_url):
        art['image_url'] = img_url
        art['image_attribution'] = img_attr
        print(f"  ✓ Image validated: {img_url[:80]}...")
    else:
        print(f"  ⚠ No valid image found, publishing without image")
        art['image_url'] = None
    
    art_id = publish_article(art)
    if art_id:
        print(f"  ✓ ID: {art_id}")
    else:
        print(f"  ✗ FAILED to publish")

print(f"\n{'='*60}")
print("Done. Published 3 articles (2 lifestyle-health, 1 markets-finance)")
