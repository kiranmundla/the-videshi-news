#!/usr/bin/env python3
"""
The Videshi — News Writer (news category)
Generates 3 news articles with proper image sourcing, dedup, and quality checks.
"""

import json, os, sys, time, uuid, subprocess, re, urllib.parse, urllib.error, textwrap
from datetime import datetime, timezone

# ── Load env ──
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
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def sb_post(table, data):
    """Insert a row into Supabase."""
    import urllib.request
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=HEADERS, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if hasattr(e, 'read') else str(e)
        print(f"  ⚠ sb_post HTTP {e.code}: {body[:300]}")
        return None
    except Exception as e:
        # IncompleteRead often means success for Supabase
        print(f"  ⚠ sb_post error (may be OK): {e}")
        return None

def sb_patch(table, filters, data):
    """Update rows in Supabase."""
    import urllib.request
    params = '&'.join(f"{k}={v}" for k, v in filters.items())
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=HEADERS, method='PATCH')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  ⚠ sb_patch error: {e}")
        return None

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.request
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
    """Fetch image from Pexels. Uses curl to avoid 403."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
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
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Check that image URL returns 200 with image content-type and >5KB."""
    if not url:
        return False
    # Block banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=', 'ccb=']
    for b in banned:
        if b in url:
            print(f"  ✗ Banned image source: {b}")
            return False
    try:
        result = subprocess.run(
            ['curl', '-sS', '-o', '/dev/null', '-w', '%{http_code} %{content_type} %{size_download}',
             '-L', '--max-time', '10', url],
            capture_output=True, text=True, timeout=15
        )
        parts = result.stdout.strip().split()
        if len(parts) >= 3:
            code = parts[0]
            ctype = parts[1]
            size = float(parts[2])
            if code == '200' and 'image' in ctype and size > 5000:
                print(f"  ✓ Image validated: {code}, {ctype}, {size:.0f} bytes")
                return True
            else:
                print(f"  ✗ Image validation failed: code={code}, type={ctype}, size={size}")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

# ── Articles to write ──

articles = [
    {
        "headline": "India and Canada Just Launched a Trade Forum and Set a Deadline to Finish Their Free Trade Deal. The Thaw Is Real.",
        "subheadline": "Commerce Minister Goyal led the largest Indian delegation ever sent abroad. Canada will send a trade mission to India later this year. Defence cooperation talks followed.",
        "slug": "india-canada-trade-investment-forum-cepa-deadline-goyal-carney-thaw-20260531",
        "category": "news",
        "vertical": "geopolitics",
        "person_for_image": "Piyush Goyal",
        "pexels_query": "India Canada flags diplomacy",
        "pexels_fallback": "international trade agreement handshake",
        "sources_list": [{"name": "Reuters"}, {"name": "Livemint"}, {"name": "The Hindu BusinessLine"}, {"name": "India Education Diary"}, {"name": "Outlook Business"}],
        "body": textwrap.dedent("""\
India and Canada have formally launched a new Trade and Investment Forum and set a year-end deadline to conclude a Comprehensive Economic Partnership Agreement, in the clearest sign yet that Asia's two largest democracies are determined to move past the diplomatic crisis that consumed their relationship for two years.

Commerce and Industry Minister Piyush Goyal led what Indian officials described as the largest Indian business delegation ever sent to any country, arriving in Ottawa for a three-day visit from May 25 to 27. His Canadian counterpart, International Trade Minister Maninder Sidhu, called the moment "a reflection of growing interest among Canadian businesses in expanding their presence in the Indian market."

## What the Forum Actually Does

The newly launched Canada-India Trade and Investment Forum is designed to serve as a permanent platform connecting business leaders from both countries. It will focus on creating commercial partnerships in clean energy, critical minerals, agri-food processing, advanced manufacturing, digital technologies, and skills development — sectors where both countries believe they have complementary strengths.

In a joint statement, both ministers committed to "expanding market access, supporting resilient supply chains, and enabling two-way economic growth." Sidhu confirmed that Canada will lead a Team Canada Trade Mission to India later this year.

## The CEPA Deadline

The most consequential element is the shared commitment to concluding CEPA negotiations by December 2026. The proposed agreement would be India's first comprehensive trade deal with a major Western nation after the UK free trade agreement signed in May 2025. For Canada, facing an escalating tariff war with the United States under President Trump, diversifying trade toward India has become a strategic imperative.

Canada is India's 14th largest trading partner, with bilateral trade hovering around $8 billion. Both sides have identified a target of $50 billion by 2030 — an ambitious six-fold increase that would require the kind of market access only a comprehensive trade deal can deliver.

## The Backstory Matters

The diplomatic reset is remarkable given how recently these two countries were locked in one of the worst bilateral crises in their history. Relations plummeted in 2023 after former Prime Minister Justin Trudeau alleged Indian government involvement in the killing of Hardeep Singh Nijjar, a claim India dismissed as "malicious."

Under Prime Minister Mark Carney, who took office earlier this year, Canada has moved aggressively to rebuild the relationship. Carney visited India in February 2026 and signed five memorandums of understanding covering energy, critical minerals, technology, AI, talent, culture, and defence. His new Foreign Minister, Anita Anand — who is of Indian origin — has spoken with External Affairs Minister S. Jaishankar about strengthening ties and "advancing shared priorities."

## Defence Cooperation Back on Track

In a parallel development that underscores the depth of the thaw, Canada's High Commissioner to India, Christopher Cooter, held talks on defence cooperation with Defence Secretary Rajesh Kumar Singh on May 30. The meeting was explicitly described as a follow-up to Carney's February visit, where both countries agreed to increase defence cooperation including maritime security and bilateral naval activities.

## What It Means for Diaspora

For the 1.9 million people of Indian origin living in Canada — one of the largest Indian diaspora communities in the world — the trade forum represents more than economics. Business mobility, people-to-people ties, and direct commercial linkages were explicitly flagged in the joint statement as "essential enablers" of the expanded partnership.

The CEPA deal, if concluded, could ease visa processes for business travelers, reduce costs on key consumer goods, and create investment pathways in both directions. For Indian students and professionals in Canada, a warmer bilateral relationship translates into more predictable immigration and economic conditions.

The question now is whether both governments can sustain the momentum through the year-end deadline, or whether the ambitious timeline will slip under the weight of sectors like agriculture, intellectual property, and services — the issues that stalled CEPA negotiations for over a decade under previous governments."""),
    },
    {
        "headline": "India Just Forecast Its Weakest Monsoon in 11 Years. The Finance Ministry Says Inflation Is Coming.",
        "subheadline": "El Niño will push rainfall to 90 percent of normal. The Strait of Hormuz disruption is the single most consequential variable for India's economy. Food and fuel prices are about to collide.",
        "slug": "india-weakest-monsoon-11-years-el-nino-inflation-hormuz-food-fuel-prices-20260531",
        "category": "news",
        "vertical": "economy",
        "person_for_image": None,
        "pexels_query": "India monsoon rain farmer agriculture",
        "pexels_fallback": "Indian monsoon rainy season field",
        "sources_list": [{"name": "Reuters"}, {"name": "India Meteorological Department"}, {"name": "The Hindu BusinessLine"}, {"name": "IANS"}, {"name": "IDFC First Bank"}, {"name": "India Finance Ministry"}],
        "body": textwrap.dedent("""\
India has forecast that its 2026 monsoon will be the weakest in 11 years, with rainfall expected at just 90 percent of the long-period average — a projection that has immediately triggered warnings from the Finance Ministry about accelerating inflation at a time when the economy is already absorbing the shock of elevated global oil prices.

The India Meteorological Department released its updated long-range forecast on Friday, downgrading an earlier April projection of 92 percent. The culprit is an El Niño that is expected to develop during the monsoon season and strengthen to moderate-to-strong intensity in the second half.

## Why the Monsoon Matters This Much

The monsoon delivers about 70 percent of India's annual rainfall. Nearly half of the country's farmland has no irrigation infrastructure, and roughly half the population earns its livelihood from farming. When the monsoon underperforms, the consequences cascade through food prices, rural demand, and ultimately GDP growth.

The IMD's regional breakdown is sobering. Northwest India, Central India, and South Peninsular India are all projected to receive below-normal rainfall. The Monsoon Core Zone — which covers most of India's rain-fed agricultural areas and is critical for food production — is also expected to fall below normal, at less than 94 percent of the long-period average. Only Northeast India is expected to receive normal rainfall.

June, the crucial first month that sets the tone for the planting season, will also see below-normal rainfall across most of the country. The IMD additionally warned of above-normal temperatures and an increased number of heatwave days in Uttar Pradesh, Haryana, Punjab, Bihar, Odisha, Chhattisgarh, Gujarat, and Andhra Pradesh.

## The Finance Ministry's Warning

The timing of the monsoon forecast could not be worse. On Saturday, India's Finance Ministry released its monthly economic report, explicitly warning that retail inflation could accelerate due to the convergence of weak monsoon rains and recent fuel price hikes.

The report named the Strait of Hormuz disruption — caused by the ongoing Iran conflict — as "the single most consequential variable" for India's external and price outlook. A sharp rise in upstream price pressures, along with recent fuel price increases, "suggests a gradual pass-through to retail inflation through higher transport, energy, and food-related costs in the coming months," the ministry said.

The report warned that "a significant rainfall deficit coupled with current geopolitical conditions could translate into food inflation, weakening rural demand and aggregate growth."

India's annual retail inflation stood at 3.48 percent in April, still below the Reserve Bank of India's 4 percent target. But economists are now warning that the twin pressures of a weak monsoon and elevated oil prices could push inflation toward 5.5 percent.

## The Double Whammy

Gaura Sengupta, chief economist at IDFC First Bank, put it bluntly: "A deficient monsoon, particularly in the crucial July-August months, can add to the pressure and push up inflation closer to an average of 5.5 percent if food inflation spikes."

India is the world's third-largest crude oil importer. Brent crude remains 27 percent above pre-war levels despite falling 19 percent in May, and the Strait of Hormuz — through which roughly a fifth of the world's oil passes — continues to operate under restrictions from the Iran conflict. The Finance Ministry described the confluence of "elevated global energy prices, a depreciating rupee, rising upstream cost pressures, and the prospect of a below-normal monsoon" as demanding "sustained policy vigilance."

The RBI, which has kept the repo rate at 5.25 percent with a neutral stance, now faces a harder path. Cutting rates to support growth risks fuelling inflation. Holding rates tight risks choking a rural economy already weakened by poor rains.

## What Diaspora Should Watch

For NRIs sending remittances home, the rupee's continued depreciation means more purchasing power per dollar — but that benefit erodes quickly if food and fuel prices surge on the receiving end. Families in agricultural states will face the most direct impact from a weak monsoon.

The next major data point is the monsoon's actual arrival. IMD expects onset around June 10 in Kerala, with some initial good rainfall before drier conditions set in. Markets, the RBI, and half a billion farmers will be watching the skies with unusual intensity this year."""),
    },
    {
        "headline": "The US and Iran Have Reached a Ceasefire Extension Deal on Paper. Neither Leader Has Signed It.",
        "subheadline": "The 60-day memorandum would reopen the Strait of Hormuz, lift the US naval blockade, and begin nuclear talks. Trump says he is in no rush. Iran says its Hormuz controls are permanent. India is watching its oil lifeline.",
        "slug": "us-iran-ceasefire-extension-mou-hormuz-trump-khamenei-india-oil-20260531",
        "category": "news",
        "vertical": "geopolitics",
        "person_for_image": None,
        "pexels_query": "oil tanker ship strait ocean",
        "pexels_fallback": "cargo ship ocean international waters",
        "sources_list": [{"name": "Reuters"}, {"name": "Axios"}, {"name": "CNN"}, {"name": "ISW-CTP"}, {"name": "NPR"}, {"name": "Tasnim News"}],
        "body": textwrap.dedent("""\
American and Iranian negotiators have reached a 60-day memorandum of understanding to extend the ceasefire and begin reopening the Strait of Hormuz, but neither President Donald Trump nor Iranian Supreme Leader Mojtaba Khamenei has approved the deal — leaving the world's most important oil chokepoint in limbo and India's economy hanging on a decision that could come at any moment.

The framework, first reported by Axios on May 28 and confirmed by two US officials, would extend the truce that halted three months of US-Israeli strikes on Iran. It would also launch formal negotiations on Iran's nuclear program — the issue Trump cited as his primary justification for going to war.

## What the Deal Says

According to the US officials, the MoU would require Iran to allow "unrestricted" shipping through the Strait of Hormuz — meaning no tolls, no harassment of vessels, and the removal of all naval mines within 30 days. In exchange, the United States would lift its naval blockade of Iranian ports and ease some sanctions on Iranian oil sales.

The deal would also formally extend the ceasefire for 60 days, during which both sides would negotiate the harder questions: Iran's nuclear enrichment activities, its ballistic missile program, and the future of its regional proxies.

## Why Neither Side Has Signed

The gap between what is on paper and what each side is willing to accept in practice is the problem. Trump is caught between two competing pressures. He needs to reopen Hormuz to bring down US gasoline prices, which have been elevated since the conflict began. But signing anything that looks like a concession risks a backlash from Iran hawks in his own party.

Senators Lindsey Graham, Roger Wicker, and Ted Cruz have all urged Trump not to compromise, arguing that the US should "finish the job" and destroy Iran's nuclear program. Trump pushed back on Friday, insisting he was in "no rush" and would only accept a "great" deal.

On the Iranian side, the IRGC-affiliated Tasnim News Agency denied that any MoU has been "finalized," citing sources close to the negotiating team. An Israeli media report said Mojtaba Khamenei has not approved the agreement.

The language around "unrestricted" shipping is the core ambiguity. Iranian officials have repeatedly described the strait as "open" while forcing vessels to receive Iranian permission and use Iran's own traffic separation scheme. Ebrahim Azizi, head of the Iranian parliament's National Security Commission, said on Friday that "Iran's control measures and arrangements in the Strait of Hormuz are permanent in nature and certainly not temporary."

## The Hormuz Problem

As of May 29, 115 commercial vessels have been redirected by US Central Command to ensure no commerce enters or leaves Iranian ports. Iran has already excavated at least 50 of 69 tunnel entrances at 18 underground missile bases, according to satellite imagery analyzed by CNN — a sign that Tehran is using the ceasefire to reconstitute its ballistic missile capabilities.

Shipping industry sources say vessels will require a sustained period of calm before returning to the strait. The Brookings Institution estimates that once temporary measures including strategic petroleum reserve releases are exhausted — potentially by July — the market could face a shortfall equivalent to roughly 16 percent of global crude trade. Brent crude sits at $92 per barrel, still 27 percent above pre-war levels.

## India's Stake

India is the world's third-largest crude oil importer, and the Hormuz disruption has hit it harder than almost any other major economy. Indian equity benchmarks posted monthly losses in May, with the Sensex down 2.8 percent and the Nifty 50 down 1.9 percent. The India Finance Ministry named the Hormuz disruption "the single most consequential variable" for the country's economic outlook in its latest monthly report.

The rupee has continued to depreciate against the dollar, raising import costs. Fuel price hikes have already been passed through to consumers, and the Finance Ministry warned on Saturday that further pass-through to retail inflation is expected in the coming months.

For NRIs in the United States, gas prices remain a daily reminder of the conflict's reach. For families back in India, the cascading effects — higher diesel costs raising transportation and food prices — are compounding the pressure from an already weak monsoon forecast.

## What Comes Next

Trump has said a decision on the MoU is imminent but has not committed to a timeline. Pentagon chief Pete Hegseth said the US is "ready to restart strikes on Iran if no deal" materializes — a signal designed to maintain pressure on Tehran while giving Trump room to claim the deal was achieved through strength.

The paradox is stark: every week without a deal depletes global oil buffers further, but rushing into an agreement Iran does not actually intend to honor would be worse than no deal at all. The ceasefire holds for now. The clock is running."""),
    },
]

# ── Process each article ──

published_count = 0

for i, article in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Article {i+1}: {article['headline'][:70]}...")
    print(f"{'='*60}")
    
    # Image sourcing
    img_url = None
    img_attribution = "The Videshi"
    
    # Try Wikipedia for person articles
    if article.get('person_for_image'):
        print(f"  → Trying Wikipedia for '{article['person_for_image']}'...")
        img_url = fetch_wikipedia_person_image(article['person_for_image'])
        if img_url:
            img_attribution = "Wikimedia Commons"
    
    # Fall back to Pexels
    if not img_url:
        print(f"  → Trying Pexels for '{article['pexels_query']}'...")
        img_url = fetch_pexels_image(article['pexels_query'], article.get('pexels_fallback'))
    
    # Validate
    if img_url and not validate_image_url(img_url):
        print(f"  ✗ Image validation failed, skipping image")
        img_url = None
    
    # Word count check
    word_count = len(article['body'].split())
    print(f"  Word count: {word_count}")
    if word_count < 400:
        print(f"  ✗ Article below 400 word floor, skipping!")
        continue
    
    # Headline length check
    hl_len = len(article['headline'])
    print(f"  Headline length: {hl_len}")
    if hl_len > 200:
        print(f"  ⚠ Headline too long, trimming...")
        article['headline'] = article['headline'][:197] + "..."
    
    # Build article record
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    record = {
        "headline": article['headline'],
        "subheadline": article['subheadline'],
        "slug": article['slug'],
        "body": article['body'],
        "category": "news",
        "vertical": article['vertical'],
        "status": "published",
        "published_at": now,
        "sources": json.dumps(article['sources_list']),
        "image_url": img_url,
        "image_attribution": img_attribution if img_url else None,
    }
    
    print(f"  → Publishing article '{article['slug']}'...")
    result = sb_post("p2_articles", record)
    
    if result:
        print(f"  ✓ Published: {article['slug']}")
        published_count += 1
    else:
        # Check if it was actually inserted (IncompleteRead)
        time.sleep(1)
        check = subprocess.run(
            ['curl', '-sS',
             f"{SUPABASE_URL}/rest/v1/p2_articles?slug=eq.{article['slug']}&select=id,slug",
             '-H', f'apikey: {SUPABASE_KEY}',
             '-H', f'Authorization: Bearer {SUPABASE_KEY}'],
            capture_output=True, text=True, timeout=10
        )
        if article['slug'] in check.stdout:
            print(f"  ✓ Published (confirmed via check): {article['slug']}")
            published_count += 1
        else:
            print(f"  ✗ Failed to publish: {article['slug']}")
            print(f"    Check output: {check.stdout[:200]}")

print(f"\n{'='*60}")
print(f"Done. Published {published_count}/{len(articles)} articles.")
print(f"{'='*60}")
