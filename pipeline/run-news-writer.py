#!/usr/bin/env python3
"""News writer for The Videshi — publishes 3 articles to Supabase."""

import json, os, re, time, subprocess, urllib.parse, datetime, requests

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
                key, _, val = line.partition('=')
                val = val.strip().strip('"').strip("'")
                os.environ[key.strip()] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

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
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Validate that an image URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get('Content-Type', '')
        content_length = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {r.status_code}, {content_type}, {content_length} bytes")
            return True
        # Try GET if HEAD doesn't give content-length
        if r.status_code == 200 and 'image' in content_type and content_length == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: {len(chunk)}+ bytes")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, type={content_type}, len={content_length}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def publish_article(article):
    """Publish an article to Supabase."""
    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    payload = {
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': article['slug'],
        'category': article['category'],
        'status': 'published',
        'published_at': now,
        'image_url': article.get('image_url', ''),
        'image_attribution': article.get('image_attribution', ''),
        'sources': ', '.join(article.get('sources', [])),
        'vertical': article.get('vertical', 'geopolitics'),
        'urgency': article.get('urgency', 'medium'),
        'diaspora_angle': article.get('diaspora_angle', ''),
        'tags': article.get('tags', []),
        'score_total': article.get('score_total', 70),
    }
    
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            headers=HEADERS,
            json=payload,
            timeout=15
        )
        if r.status_code in (200, 201):
            print(f"  ✓ Published: {article['headline'][:60]}...")
            return True
        else:
            print(f"  ✗ Publish failed ({r.status_code}): {r.text[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ Publish error: {e}")
        return False


# ============================================================
# ARTICLE 1: Hegseth calls India "critical anchor" at Shangri-La
# ============================================================
def write_article_1():
    print("\n=== Article 1: Hegseth India Critical Anchor ===")
    
    # Image: Pete Hegseth from Wikipedia
    image_url = fetch_wikipedia_person_image("Pete Hegseth")
    image_attribution = "Wikimedia Commons"
    
    if not image_url or not validate_image_url(image_url):
        image_url = fetch_pexels_image("military defense conference", "US military Indo-Pacific")
        image_attribution = "Pexels"
    
    if not validate_image_url(image_url):
        image_url = ""
        image_attribution = ""

    article = {
        'headline': "The Pentagon Just Called India a 'Critical Anchor' in the Indo-Pacific. Then It Announced Javelin Co-Production.",
        'subheadline': "US Defence Secretary Pete Hegseth used his Shangri-La Dialogue keynote to praise India's military modernisation, announce Javelin missile co-production, and demand that all Asian allies spend 3.5 percent of GDP on defence.",
        'slug': 'hegseth-india-critical-anchor-javelin-co-production-shangri-la-dialogue-20260531',
        'category': 'news',
        'image_url': image_url,
        'image_attribution': image_attribution,
        'sources': ["Reuters", "The Hindu BusinessLine", "Washington Examiner", "Wall Street Journal", "Daily Caller"],
        'vertical': 'geopolitics',
        'urgency': 'high',
        'diaspora_angle': 'A deepening US-India defence partnership — now including Javelin co-production — reinforces the geopolitical alignment that underpins H-1B policy, trade deals, and bilateral business ties. Defence-corridor manufacturing jobs in India could create new career pathways for dual-citizen professionals.',
        'tags': ['shangri-la', 'hegseth', 'india-us-defence', 'javelin', 'indo-pacific', 'military'],
        'score_total': 85,
        'body': """The United States just gave India its most emphatic public endorsement as a military partner in years — and backed it up with a concrete weapons deal.

Speaking at the Shangri-La Dialogue in Singapore on Saturday, US Defence Secretary Pete Hegseth called India "a critical anchor to hold the line" in South Asia and said a powerful India acting in its own self-interest advances the shared goal of maintaining a balance of power across the Indo-Pacific.

"India is modernising its military to carry its share of the security burden, particularly in the Indian Ocean," Hegseth told delegates at Asia's premier defence forum. "It's building out the heavy industrial and logistics capacity to sustain high-end military operations, including the ability to repair and maintain our shared platforms and support US Navy vessels operating forward in the theatre."

## Javelin Co-Production Is Now on the Table

The headline announcement went beyond rhetoric. Hegseth confirmed that the United States and India have committed to pursuing co-production of Javelin anti-tank guided munitions — a significant step that would make India one of a handful of countries involved in manufacturing one of America's most effective battlefield weapons.

"Real, tangible steps to improve the collective readiness of our forces," Hegseth said. The Javelin system, manufactured by a Lockheed Martin–Raytheon joint venture, has been battle-proven in Ukraine and is one of the most sought-after weapon systems globally.

For India's defence-industrial ambitions, Javelin co-production represents exactly the kind of high-end technology transfer that New Delhi has long sought from Washington. It also signals a level of trust in India's manufacturing base that goes well beyond simple arms sales.

## The 3.5 Percent Demand

Hegseth did not limit his remarks to praise. He demanded that all US allies in the Indo-Pacific increase defence spending to 3.5 percent of GDP, while pledging a $1.5 trillion US military investment.

"The era of the United States subsidizing the defence of wealthy nations is over," he said. "We need partners, not protectorates. No freeloading."

The demand echoes President Trump's longstanding insistence that allies pay more for their own security — a message that has previously been directed primarily at NATO members in Europe but is now being applied with equal force in Asia.

## A Softer Tone on China

In a notable shift from last year's Shangri-La speech, where Hegseth repeatedly referred to "Communist China" as a threat and warned against a Chinese invasion of Taiwan, this year's address was markedly more restrained. He did not mention Taiwan by name and did not use the word "communist."

Instead, Hegseth said US-China relations are "better than they have been in many years," pointing to President Trump's recent state visit to Beijing. He expressed that "no state, including China, can impose its hegemony" — but observers noted the phrasing was deliberately vague enough to apply to any power.

The restraint is widely attributed to the diplomatic thaw following Trump's China visit earlier this month, during which both leaders expressed a mutual desire for stability.

## Where China Was Not

For the second consecutive year, Chinese Defence Minister Dong Jun skipped the Shangri-La Dialogue entirely, sending instead a low-profile delegation of PLA "experts and scholars." The absence was conspicuous.

"I wish my counterpart was here at this conference," Hegseth remarked during his keynote, "but I look forward to other options when we can cross paths."

Australia's defence minister Richard Marles called it a "lost opportunity." Analysts suggested China may be avoiding tough questions about Taiwan, military corruption purges, and its combat readiness.

## What It Means for the Diaspora

For the three-million-strong Indian diaspora in the United States, the deepening defence partnership carries both strategic and personal significance. A stronger US-India military relationship reinforces the geopolitical alignment that underpins everything from trade deals to immigration policy. The Javelin co-production announcement could also create high-skilled manufacturing jobs in India's defence corridor — potentially opening new career pathways for dual-citizen professionals and defence-sector engineers.

The Shangri-La address comes just days after Secretary of State Marco Rubio's four-day India visit, during which India committed to purchasing $500 billion in US goods over five years and both sides suggested a bilateral trade deal could be weeks away.

Taken together, the signals are unmistakable: Washington sees India not just as a partner, but as a cornerstone of its Indo-Pacific strategy. The question is whether New Delhi can convert that embrace into the technology transfers, market access, and immigration goodwill that its diaspora is watching for."""
    }
    
    return publish_article(article)


# ============================================================
# ARTICLE 2: Shrey Parikh Wins 2026 Spelling Bee
# ============================================================
def write_article_2():
    print("\n=== Article 2: Shrey Parikh Spelling Bee ===")
    
    # Image: Try Pexels for spelling bee
    image_url = fetch_pexels_image("spelling bee competition stage", "student academic competition trophy")
    image_attribution = "Pexels"
    
    if not validate_image_url(image_url):
        image_url = ""
        image_attribution = ""

    article = {
        'headline': "An Indian American Teenager Just Won the National Spelling Bee. He Set a Record Doing It.",
        'subheadline': "Shrey Parikh, 14, from Rancho Cucamonga, California, spelled 32 words in 90 seconds to shatter the Scripps National Spelling Bee spell-off record. The winning word was bromocriptine.",
        'slug': 'shrey-parikh-wins-2026-scripps-national-spelling-bee-record-indian-american-20260531',
        'category': 'news',
        'image_url': image_url,
        'image_attribution': image_attribution,
        'sources': ["New York Post", "People", "CNN", "USA Today", "Madhyamam"],
        'vertical': 'diaspora',
        'urgency': 'medium',
        'diaspora_angle': 'Parikh continues the Indian American Spelling Bee dynasty — 28 of the last 34 champions have been Indian American. The pattern reflects H-1B-era immigration, high-income Indian American households, and a network of South Asian spelling circuits that have transformed the competition.',
        'tags': ['spelling-bee', 'indian-american', 'scripps', 'shrey-parikh', 'education', 'diaspora'],
        'score_total': 78,
        'body': """Shrey Parikh walked off the stage at DAR Constitution Hall in Washington, D.C. on Thursday night as the 2026 Scripps National Spelling Bee champion — and he did it in a way the competition has never seen before.

The 14-year-old eighth-grader from Rancho Cucamonga, California, correctly spelled 32 words in a 90-second spell-off, shattering the previous record of 29 words set in 2024. His winning word was "bromocriptine" — a polypeptide alkaloid derived from ergot that mimics the activity of dopamine.

"I feel so, so, so happy, and just kind of relieved that this long Bee is over because it's been really stressful for me," Parikh said after the victory.

## The Comeback

This was not Parikh's first time on the national stage. He first reached the Scripps National Spelling Bee in 2022, where he tied for 89th place. He returned in 2024 and finished tied for third — close enough to taste the championship but not close enough to claim it.

Then came 2025, and with it, devastation. Parikh missed the cut for the national competition entirely.

"At my school bee last year, I was really dejected and just very upset," he said. "It didn't even sink in until the next day, and I had a really tough time."

He took six months away from competitive spelling. When he came back, he came back different.

Over the past year, Parikh won the SpellPundit National Spelling Bee, the Words of Wisdom Spelling Bee, and the South Asian Spelling Bee. He qualified for the California state Mathcounts competition. He arrived at the 98th Scripps National Spelling Bee having put in more preparation than at any point in his life.

"I used more tools to help me study. Everything paid off," he said. "I could feel the difference all week and was confident throughout the Bee."

## The Spell-Off

The 98th edition of the competition reached a deadlock when 18 conventional rounds failed to separate the final two spellers. The judges triggered the competition's third-ever spell-off — a 90-second race where each contestant spells as many words as possible from an identical list.

While Parikh competed, his opponent — 12-year-old Ishaan Gupta from Jersey City, New Jersey — was sequestered in an isolated room wearing noise-cancelling headphones. Both faced the same words in the same order to ensure fairness.

Parikh was relentless, firing through 32 words — including cywyddau and taurokathapsia — before the clock ran out. Gupta, himself a formidable speller, correctly answered 25.

"Spelling fast is what I do every day," Parikh said. "A spell-off just came naturally."

Third place went to Sarv Dharavane, a three-time bee veteran who finished third for the second consecutive year after misspelling "disa," a tropical African terrestrial orchid.

## The Indian American Streak Continues

Parikh's victory continues what has become one of the most remarkable winning streaks in American academic competition. Of the last 34 Scripps National Spelling Bee champions, 28 have been Indian American — including three straight years of Indian American co-champions and the 2019 competition, when seven of eight declared champions were of Indian descent.

The pattern reflects the broader story of Indian immigration to the United States. Nearly 70 percent of Indian-born US residents arrived after 2000, many on H-1B work visas or student visas. Indian American households have a median income of $147,000 — more than twice the US median — and are more than twice as likely to hold college degrees.

But the spelling bee success is about more than demographics. It reflects a network of South Asian spelling circuits, year-round training regimens, and family support systems that have elevated the competition to levels that previous generations of contestants never approached.

## Who Is Shrey Parikh?

According to his Scripps biography, Parikh attends Day Creek Intermediate School and enjoys tennis, reading, mathematics, and chess. He plays percussion in his school band — including snare drum, bass drum, timpani, toms, triangle, glockenspiel, and marimba.

He visits India frequently to spend time with his grandparents. Representing the San Bernardino County Superintendent of Schools, he took home a $50,000 cash prize, the Scripps Cup, a commemorative medal, $2,500 from Merriam-Webster, $1,000 in Delta Air Lines flight credits, and reference works from Encyclopaedia Britannica.

There was only one word during the entire competition that gave him pause: Bhubaneswar, the capital of Odisha, which has optional spellings. Everything else, he said, he knew.

"Looking back, that makes me see how much more prepared I was than in 2024," he said.

The 2025 champion was Faizan Zaki of Texas. The 2027 competition will likely see a new generation of Indian American spellers — many of whom are already training in regional circuits across the country."""
    }
    
    return publish_article(article)


# ============================================================
# ARTICLE 3: India's $500B US Goods Commitment Under Scrutiny
# ============================================================
def write_article_3():
    print("\n=== Article 3: $500B Trade Commitment Scrutiny ===")
    
    # Image: Try Wikipedia for Marco Rubio
    image_url = fetch_wikipedia_person_image("Marco Rubio")
    image_attribution = "Wikimedia Commons"
    
    if not image_url or not validate_image_url(image_url):
        image_url = fetch_pexels_image("US India trade shipping containers", "international trade negotiation")
        image_attribution = "Pexels"
    
    if not validate_image_url(image_url):
        image_url = ""
        image_attribution = ""

    article = {
        'headline': "India Committed to Buying $500 Billion in American Goods. Economists Say the Math Does Not Add Up.",
        'subheadline': "After Secretary of State Marco Rubio's India visit, trade experts and economists are questioning whether a $100-billion-a-year import target is feasible — or wise — for an economy already strained by a weak rupee and rising oil prices.",
        'slug': 'india-500-billion-us-goods-commitment-experts-scrutiny-trade-balance-20260531',
        'category': 'news',
        'image_url': image_url,
        'image_attribution': image_attribution,
        'sources': ["Washington Examiner", "Financial Times", "Reuters", "India Today Global", "Indian Witness"],
        'vertical': 'trade',
        'urgency': 'high',
        'diaspora_angle': 'A stronger US-India economic relationship supports the policy environment sustaining H-1B visas and bilateral business ties. But if the $500B commitment is perceived as one-sided, it risks fuelling political backlash that has already led to tariff escalations and immigration crackdowns affecting NRIs.',
        'tags': ['india-us-trade', 'rubio', 'trade-deficit', 'tariffs', 'economy', 'imports'],
        'score_total': 82,
        'body': """When US Secretary of State Marco Rubio announced after his four-day India visit last week that New Delhi had "committed" to purchasing $500 billion worth of American goods over the next five years, the headline sounded like a diplomatic triumph.

Now the scrutiny has arrived.

Trade experts, economists, and policy analysts are raising pointed questions about whether the commitment is realistic, whether it serves India's interests, and whether the word "commitment" is even the right one to use.

## The Numbers Problem

The $500 billion figure works out to $100 billion per year in Indian imports of American goods — a staggering increase from current levels. India's total goods imports from the United States were approximately $50 billion in the most recent fiscal year. Doubling that would require a fundamental shift in India's procurement patterns.

"The math doesn't add up," Madhavi Arora, an economist at Emkay Global, told Reuters. She called the target "more aspirational than realistic."

Biswajit Dhar, an independent trade expert, was more blunt: "If it is a $100 billion every year, it would completely upset India's trade balance."

India already runs an overall goods trade deficit of $283.5 billion. The United States is India's top export destination, accounting for nearly a fifth of all outbound shipments. If imports from the US surge while exports hold steady, India's largest bilateral surplus could shrink or disappear entirely.

## What Changed Since February

The $500 billion target was first floated in February 2025, when Prime Minister Modi and President Trump set a goal of doubling bilateral trade to $500 billion by 2030. At the time, the Trump administration reduced tariffs on Indian goods from 50 percent to 18 percent, and Commerce Minister Piyush Goyal defended the target by pointing to India's expanding economy and aviation demand.

But the trade landscape has shifted dramatically since then. The US Supreme Court struck down parts of Trump's tariff framework, prompting Washington to impose a uniform 10 percent tariff on all trading partners under Section 122 of the Trade Act of 1974 — including India.

As the Financial Times noted, it is "rather bizarre" that India has not challenged Rubio's assertion that the target now constitutes a binding commitment, given the changed circumstances. India faces a steeper tariff rate than even Beijing — a fact that has not been lost on Indian policymakers.

## The Strain on India's Economy

The timing compounds the concern. India's economy is already under pressure from multiple directions.

The rupee has been weakening. Oil prices have spiked due to the US-Iran war and the closure of the Strait of Hormuz. India's finance ministry warned this week that the Hormuz disruption remains the "single most consequential variable" for the country's price outlook. Fuel price hikes have already begun feeding into inflation.

Against this backdrop, committing to import an additional $50 billion a year in American goods — particularly energy products like liquefied natural gas and coal — would increase India's exposure to dollar-denominated imports at a time when every rupee of forex reserves is precious.

## What India Gets in Return

The deal is not without its benefits. Energy diversification away from Russian and Iranian crude has strategic value, especially as both supply chains carry sanctions risk. American LNG provides a long-term hedge against supply disruptions.

The broader diplomatic context also matters. Rubio's visit produced a bilateral Critical Minerals Framework, and both sides suggested a comprehensive trade deal could be weeks away, with a US delegation expected in India in June. At the Quad meeting, agreements were struck on a joint port project in Fiji and an Indo-Pacific energy security initiative.

US Ambassador Sergio Gor expressed confidence the trade deal would be finalised "in the coming weeks and months," comparing the pace favourably to the EU-India FTA, which took nearly 19 years.

## The Diaspora Angle

For NRIs in the United States, the trade dynamics have direct implications. A stronger US-India economic relationship supports the policy environment that sustains H-1B visas, green card processing, and bilateral business ties. But if the $500 billion commitment is perceived as one-sided — India buying more than it gains — it risks fuelling the kind of political backlash that has already led to tariff escalations and immigration crackdowns.

External Affairs Minister S. Jaishankar has consistently framed India's approach as "India First" — protecting the country's interests while engaging pragmatically with Washington. Whether the $500 billion commitment fits that framework, or whether it was a diplomatic concession made under pressure, is the question that economists and trade watchers are now asking.

The US delegation expected in June will be the next test. What India brings to the table — and what it asks for in return — will determine whether this is a strategic partnership of equals or an arrangement that favours one side more than the other."""
    }
    
    return publish_article(article)


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("The Videshi News Writer — Running")
    print("=" * 60)
    
    results = []
    results.append(("Hegseth India Anchor", write_article_1()))
    results.append(("Spelling Bee", write_article_2()))
    results.append(("$500B Trade Scrutiny", write_article_3()))
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    for name, ok in results:
        print(f"  {'✓' if ok else '✗'} {name}")
    print("=" * 60)
