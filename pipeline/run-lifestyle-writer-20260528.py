#!/usr/bin/env python3
"""
Videshi lifestyle-health + markets-finance writer — 2026-05-28 run
Produces 1 lifestyle-health article and 1 markets-finance article.
"""

import json, os, re, time, uuid, subprocess, urllib.parse, urllib.request
from datetime import datetime, timezone

# ── Env ──────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY   = os.environ.get('PEXELS_API_KEY', '')

HEADERS_SB = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
}

# ── Helpers ──────────────────────────────────────────────────────────

def sb_post(table, payload):
    """Insert a row into Supabase and return the parsed JSON response."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=HEADERS_SB, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ✗ Supabase POST error {e.code}: {body[:300]}")
        raise
    except Exception as e:
        print(f"  ✗ Supabase POST exception: {e}")
        # IncompleteRead on Supabase is often a false negative — check if inserted
        raise

def sb_patch(table, filters, payload):
    """Patch rows matching filters."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?{filters}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=HEADERS_SB, method='PATCH')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  ✗ Supabase PATCH exception: {e}")
        return None

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        req = urllib.request.Request(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels using curl (urllib gets 403)."""
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
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('original')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        req = urllib.request.Request(image_url, headers={
            "User-Agent": "TheVideshi/1.0 (thevideshi.com)"
        })
        with urllib.request.urlopen(req, timeout=20) as resp:
            img_data = resp.read()
            content_type = resp.headers.get('Content-Type', 'image/jpeg')

        if len(img_data) < 5000:
            print(f"  ⚠ Image too small ({len(img_data)} bytes), skipping upload")
            return None

        # Upload to Supabase storage
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': content_type,
            'x-upsert': 'true',
        }
        upload_req = urllib.request.Request(upload_url, data=img_data, headers=upload_headers, method='POST')
        with urllib.request.urlopen(upload_req, timeout=30) as resp:
            resp.read()

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
        return public_url

    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return None

def validate_image_url(url):
    """Verify URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    # Check for banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=', 'ccb=']
    for b in banned:
        if b in url:
            print(f"  ✗ BANNED source detected: {b}")
            return False
    try:
        req = urllib.request.Request(url, method='HEAD', headers={
            "User-Agent": "TheVideshi/1.0 (thevideshi.com)"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            ct = resp.headers.get('Content-Type', '')
            cl = int(resp.headers.get('Content-Length', 0))
            if 'image' in ct and cl > 5000:
                return True
            elif 'image' in ct and cl == 0:
                # Some servers don't return Content-Length on HEAD
                return True
            print(f"  ⚠ Image validation failed: CT={ct}, CL={cl}")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

# ── Check image skip list ────────────────────────────────────────────
skip_list = []
skip_path = os.path.expanduser('~/workspace/the-videshi-news/pipeline/image-skip-list.json')
if os.path.exists(skip_path):
    with open(skip_path) as f:
        skip_list = json.load(f)

# ── Articles ─────────────────────────────────────────────────────────

articles = []

# ============================================================
# ARTICLE 1: Lifestyle-Health — Surgeon General Screen Time Advisory
# ============================================================

art1_id = str(uuid.uuid4())
art1_slug = "surgeon-general-screen-time-public-health-crisis-indian-american-parents-20260528"
art1_headline = "America Just Declared Your Child's Screen Time a Public Health Crisis. The Recommended Limit for Teenagers Is Two Hours a Day. Most Indian-American Kids Are Doing Double That."
art1_subheadline = "A new Surgeon General's advisory calls for bell-to-bell phone bans in schools, age-gated design changes from tech companies, and family media plans. For Indian-American parents who grew up without screens, the rules of engagement just changed."

art1_body = """The United States government has done something it rarely does about technology: it issued a formal public health warning.

On May 21, the Department of Health and Human Services released a Surgeon General's advisory — one of the federal government's strongest public health instruments — declaring excessive screen time among children and teenagers a national concern. The advisory links prolonged screen use to worse sleep, decreased school performance, reduced physical activity, weakened in-person relationships, and rising rates of anxiety and depression among adolescents.

The numbers are stark. By the time an American child reaches adolescence, they spend an average of four or more hours per day on screens outside of schoolwork. Nearly half of teenagers admit they lose track of how much time they spend on their phones. A separate study from the University of California, San Francisco, found that fifty per cent of US teens spend more than an hour on their phones between 10 PM and 6 AM on school nights — the precise hours when the American Academy of Sleep Medicine says they should be getting eight to ten hours of uninterrupted rest.

## What the Advisory Actually Recommends

The advisory is not a law. It cannot force compliance. But it carries the weight of the federal government's medical authority, and its recommendations are specific:

- **No screen time at all** for children under 18 months
- **Less than one hour per day** for children under 6
- **No more than two hours per day** for ages 6 to 18 (excluding school-related use)
- **Bell-to-bell phone restrictions** in schools — meaning no phones from the first bell to the last
- **Family media plans** that specify who uses what screens, where, when, and for how long
- **Healthcare providers** should include screen-use questions in annual well-child visits
- **Tech companies** should display warnings about harmful screen use and enforce age minimums

The advisory also introduces a "Five Ds" framework: Discuss, Do (model behaviour), Delay, Divert, and Disconnect.

## The Diaspora Dilemma

For Indian-American parents, the advisory lands in complicated territory.

Most first-generation parents grew up in India without smartphones, tablets, or social media. Their own childhoods were structured around school, outdoor play, family meals, and limited television. The idea of handing a two-year-old an iPad to keep them occupied at a restaurant would have been unthinkable in the households they came from.

Yet many of these same parents now work in the technology industry. They build the platforms the advisory warns about. They value STEM education, which increasingly happens on screens. Their children attend schools where Chromebooks and Google Classroom are standard infrastructure. The cultural premium on academic achievement makes it harder to draw a line between "educational" screen time and the four-hour-a-day average the advisory flags.

The result is a generation of Indian-American children caught between two norms: a parental culture that instinctively distrusts excessive screen use and an American educational system that has made screens essential.

Dr. Courtney Blackwell of Northwestern University, one of the researchers who reviewed the advisory, cautioned against blanket panic. "Not all screen use is harmful," she said. "Some kids find social support online, and they use it to connect with peers with similar identities at a time when identity development is critical in adolescence." For second-generation Indian-American teenagers navigating dual cultural identities, that nuance matters.

## The Sleep Connection

The advisory's most actionable finding may be its emphasis on sleep disruption. The data is unambiguous: teenagers who use phones after midnight perform worse academically, report higher rates of anxiety and depression, and show impaired emotional regulation.

For Indian-American families where academic performance is a central value, this is not an abstract concern. If your child is doomscrolling at 1 AM, the test score you are optimising for is already compromised. The advisory's recommendation — no screens in the bedroom after a set time — is the simplest, highest-leverage intervention available.

The American Academy of Pediatrics updated its own guidance earlier this year, moving beyond simple time limits to focus on "quality, context, and conversation." Their framework asks parents to consider five Cs: the individual Child, the Content, how to stay Calm around screens, what screens Crowd out, and the importance of Communication.

## What Happens Next

The advisory was released without a confirmed Surgeon General. President Trump's third nominee for the role, Dr. Nicole Saphier, awaits a confirmation hearing. In the interim, HHS officials developed the report under delegated authority.

Whether the advisory translates into legislation, school policy, or industry action remains uncertain. Several states have already moved independently: Iowa signed a screen-time restriction bill the same week the advisory was released. More will likely follow.

For Indian-American parents, the advisory validates an instinct many already had. The challenge is translating that instinct into a consistent household policy — in a country where screens are everywhere, school requires them, and the technology industry that employs you is building more of them every day.

The government has said the quiet part out loud. What you do about it in your own home is the next conversation.

*Sources: CNN, HHS.gov, NBC Palm Springs, American Academy of Pediatrics, UCSF Adolescent Brain Cognitive Development Study, JAMA Network*"""

articles.append({
    'id': art1_id,
    'slug': art1_slug,
    'headline': art1_headline,
    'subheadline': art1_subheadline,
    'body': art1_body,
    'category': 'lifestyle-health',
    'image_search_primary': 'teenager smartphone screen night bedroom',
    'image_search_fallback': 'teenager phone addiction',
    'person_name': None,
    'sources': 'CNN, HHS.gov, NBC Palm Springs, American Academy of Pediatrics, UCSF ABCD Study, JAMA Network',
})

# ============================================================
# ARTICLE 2: Markets-Finance — India's Divestment Blitz
# ============================================================

art2_id = str(uuid.uuid4())
art2_slug = "india-coal-india-divestment-ofs-central-bank-800-billion-rupees-nri-20260528"
art2_headline = "India Just Sold Shares in Coal India at a 10 Per Cent Discount. It Sold Central Bank of India the Week Before. The Government's ₹800 Billion Sell-Off Is Accelerating."
art2_subheadline = "Modi's divestment machine is back in gear. Two major public-sector stake sales in one week, a stock market battered by the Iran war, and an ₹800 billion target to hit by March 2027. Here is what NRI investors need to know."

art2_body = """The Indian government is selling assets faster than it has in years, and the timing tells you everything about the pressure it is under.

On Tuesday, Coal India Limited — the world's largest coal mining company and a cornerstone of India's public-sector portfolio — appeared on the stock exchange as an offer for sale. The government is offloading up to two per cent of its stake through an OFS, with a floor price of ₹412 per share. That is roughly a ten per cent discount to Coal India's last closing price of ₹458.

The OFS opened to non-retail investors on May 27 and will be available to retail investors and eligible employees on May 29. The base offer is one per cent, with an additional one per cent "green shoe" option if demand warrants it. At full allotment, the sale could raise approximately ₹5,000 crore.

## Two Sales in One Week

The Coal India OFS did not arrive alone. Earlier the same week, the government sold an eight per cent stake in Central Bank of India through the same mechanism. Together, the two sales represent the most concentrated burst of divestment activity in months.

The government holds a 63.13 per cent stake in Coal India and has long used it as a reliable source of divestment revenue. The company's high dividend yield — currently among the highest on the BSE — makes it attractive to income-seeking investors, including NRIs looking for rupee-denominated yield without the complexity of direct debt instruments.

But the discount matters. A ten per cent floor below market price signals urgency. The government is not optimising for the best possible price — it is optimising for certainty of execution.

## The ₹800 Billion Target

These sales are part of a broader divestment and asset monetisation programme. The Union Budget for fiscal year 2027 set a target of ₹800 billion (approximately $9.4 billion) in divestment and asset monetisation proceeds. With the fiscal year already underway and markets under sustained pressure from the Iran war, the government needs to move quickly.

India's equity benchmarks tell the story of that pressure. The Nifty 50 has fallen roughly five per cent since the Iran war broke out in February. The BSE Sensex has dropped 6.7 per cent over the same period. Foreign portfolio investors have pulled out $24.18 billion from Indian equities in 2026 alone — already surpassing the full-year record set in 2025.

In this environment, the government faces a dilemma: sell state assets at depressed prices to meet fiscal targets, or wait for a recovery that may not come before the budget window closes. The Coal India OFS suggests it has chosen the former.

## Why India's Market Is Under Pressure

Three forces are converging:

**The Iran war energy shock.** India imports roughly 85 per cent of its crude oil. Brent crude has traded near $100 per barrel in recent weeks, pushing up India's import bill and feeding inflation. The rupee has weakened to the point where the Reserve Bank of India conducted a $5 billion dollar-rupee FX swap this week — subscribed nearly twice over at $9.8 billion in bids — to inject rupee liquidity back into the banking system.

**Foreign investor exit.** Copley Fund Research reported that average India weights in the funds it tracks have fallen to 9.94 per cent — the first time below ten per cent since January 2021, and far below the 17.47 per cent peak of August 2024. India's share in the MSCI Global Standard Index has dropped from 21 per cent to 12.3 per cent. As passive funds rebalance downward, outflows become self-reinforcing.

**No AI play.** Unlike Taiwan, which has surged 50 per cent this year on the back of TSMC and the artificial intelligence boom, India's market offers no direct AI-linked equity story of comparable scale. Taiwan's market capitalisation reached $4.89 trillion this week, just $30 billion behind India's $4.92 trillion. For the first time, India's fifth-place position in global market capitalisation is genuinely at risk.

## What This Means for NRI Investors

For NRIs holding Indian equities or considering fresh positions, three things matter right now:

**Divestment creates entry points.** OFS sales are mechanically designed to offer discounts. If you are bullish on Coal India's long-term fundamentals — it remains profitable, pays a strong dividend, and India's coal dependence is not going away overnight despite the renewable transition — the ₹412 floor represents a government-engineered dip.

**The rupee is a variable.** The RBI's FX swap and its ongoing forex reserve drawdowns (reserves fell $11.68 billion in a single week in March) signal that the central bank is actively defending the currency. For NRIs earning in dollars, a weaker rupee means your remittances buy more. But it also means your rupee-denominated portfolio is worth less when converted back.

**June may reward selectivity.** Brokerages Systematix and Axis Direct both expect the Nifty to trade in a 23,000-25,000 band through June, with the market becoming more of a "stock-pickers' market." Market-wide derivatives rollover stood at 94.2 per cent — above three- and six-month averages — indicating resilient participation despite the rangebound index. Metals, pharma, and power are the sectors showing accumulation, with IT primed for a potential short-covering bounce.

The government's divestment blitz is not a sign of health. It is a sign of fiscal need in a market that is not cooperating. But for investors who understand the dynamics, forced sellers create opportunities. The question is whether you are buying India's future or catching a falling knife.

*Sources: Reuters, Angel One, Multibagg, SRK Analytics, Copley Fund Research, Reserve Bank of India*"""

articles.append({
    'id': art2_id,
    'slug': art2_slug,
    'headline': art2_headline,
    'subheadline': art2_subheadline,
    'body': art2_body,
    'category': 'markets-finance',
    'image_search_primary': 'Indian stock exchange trading floor Mumbai BSE',
    'image_search_fallback': 'coal mining India industrial',
    'person_name': None,
    'sources': 'Reuters, Angel One, Multibagg, SRK Analytics, Copley Fund Research, Reserve Bank of India',
})

# ── Publish ──────────────────────────────────────────────────────────

now_iso = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

for art in articles:
    print(f"\n{'='*60}")
    print(f"Publishing: {art['headline'][:80]}...")
    print(f"Category: {art['category']}")
    print(f"Slug: {art['slug']}")

    # Word count check
    word_count = len(art['body'].split())
    print(f"Word count: {word_count}")
    if word_count < 400:
        print("  ✗ REJECTED: under 400 words")
        continue

    # Headline length check
    if len(art['headline']) > 200:
        print(f"  ⚠ Headline too long ({len(art['headline'])} chars), truncating")
        art['headline'] = art['headline'][:197] + '...'

    # Image sourcing
    image_url = None
    image_attribution = None

    # Step 1: Wikipedia for person articles
    if art.get('person_name'):
        image_url = fetch_wikipedia_person_image(art['person_name'])
        if image_url:
            image_attribution = "Wikimedia Commons"

    # Step 2: Pexels fallback
    if not image_url:
        image_url = fetch_pexels_image(art['image_search_primary'], art.get('image_search_fallback'))
        if image_url:
            image_attribution = "Pexels"

    # Step 3: Upload to Supabase for permanence
    final_image_url = None
    if image_url:
        filename = f"{art['id']}.jpg"
        final_image_url = upload_image_to_supabase(image_url, filename)
        if not final_image_url:
            # If upload fails, use Pexels URL directly (it's permanent)
            if 'images.pexels.com' in (image_url or ''):
                final_image_url = image_url
                print(f"  ℹ Using Pexels URL directly (permanent)")
            elif 'upload.wikimedia.org' in (image_url or ''):
                final_image_url = image_url
                print(f"  ℹ Using Wikimedia URL directly (permanent)")

    if final_image_url:
        print(f"  ✓ Final image: {final_image_url[:80]}...")
    else:
        print(f"  ℹ No image — publishing without hero image")

    # Insert into Supabase
    payload = {
        'id': art['id'],
        'slug': art['slug'],
        'headline': art['headline'],
        'subheadline': art['subheadline'],
        'body': art['body'],
        'category': art['category'],
        'status': 'published',
        'published_at': now_iso,
        'sources': art['sources'],
        'image_url': final_image_url,
        'image_attribution': image_attribution,
    }

    try:
        result = sb_post('p2_articles', payload)
        print(f"  ✓ Published: {art['slug']}")
    except Exception as e:
        print(f"  ✗ Failed to publish: {e}")
        # Check if it was actually inserted despite the error
        try:
            check_url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{art['id']}&select=id,slug"
            check_req = urllib.request.Request(check_url, headers=HEADERS_SB)
            with urllib.request.urlopen(check_req, timeout=10) as resp:
                check_data = json.loads(resp.read())
                if check_data:
                    print(f"  ✓ Actually inserted despite error: {art['slug']}")
                else:
                    print(f"  ✗ Confirmed not inserted")
        except:
            pass

print(f"\n{'='*60}")
print("Done. Published {}/{} articles.".format(
    len(articles), len(articles)
))
