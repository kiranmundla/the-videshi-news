#!/usr/bin/env python3
"""News writer for The Videshi — June 1, 2026 batch."""

import json, os, re, sys, time, uuid, datetime, requests, urllib.parse, subprocess

# ── Env ──────────────────────────────────────────────────────────────────
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
PEXELS_KEY   = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
}

# Valid columns in p2_articles
VALID_COLS = {
    'id', 'topic_id', 'headline', 'subheadline', 'body', 'diaspora_angle',
    'vertical', 'tags', 'urgency', 'sources', 'slug', 'word_count', 'status',
    'is_featured', 'published_at', 'image_url', 'category', 'image_attribution',
    'is_editorial',
}


def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f'https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}',
            headers={'User-Agent': 'TheVideshi/1.0 (thevideshi.com)'},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get('originalimage', {}).get('source') or data.get('thumbnail', {}).get('source')
            if img:
                print(f'  ✓ Wiki img for "{person_name}": {img[:80]}...')
                return img
    except Exception as e:
        print(f'  ⚠ Wiki error for "{person_name}": {e}')
    return None


def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            for p in data.get('photos', []):
                url = p.get('src', {}).get('large2x') or p.get('src', {}).get('original')
                if url:
                    print(f'  ✓ Pexels img for "{q}": {url[:80]}...')
                    return url
        except Exception as e:
            print(f'  ⚠ Pexels error for "{q}": {e}')
    return None


def validate_image(url):
    if not url:
        return None
    for bp in ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=']:
        if bp in url:
            return None
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={'User-Agent': 'TheVideshi/1.0 (thevideshi.com)'})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return url
        # Retry with GET
        r2 = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                          headers={'User-Agent': 'TheVideshi/1.0 (thevideshi.com)', 'Range': 'bytes=0-1023'})
        if r2.status_code in (200, 206) and 'image' in r2.headers.get('Content-Type', ''):
            return url
    except:
        pass
    return None


def word_count(text):
    return len(re.findall(r'\b\w+\b', text))


def insert_article(art):
    art['status'] = 'published'
    art['published_at'] = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
    art['is_editorial'] = False
    art['word_count'] = word_count(art.get('body', ''))
    if 'id' not in art:
        art['id'] = str(uuid.uuid4())
    # Filter to valid columns only
    payload = {k: v for k, v in art.items() if k in VALID_COLS}
    r = requests.post(
        f'{SUPABASE_URL}/rest/v1/p2_articles',
        headers=HEADERS, json=payload, timeout=30,
    )
    if r.status_code in (200, 201):
        print(f'  ✅ Published: {art["headline"][:70]}...')
        return True
    else:
        print(f'  ✗ Insert failed ({r.status_code}): {r.text[:300]}')
        return False


def get_image_attr(url):
    if not url:
        return None
    if 'wikimedia' in url.lower() or 'wikipedia' in url.lower():
        return 'Wikimedia Commons'
    if 'pexels' in url.lower():
        return 'Pexels'
    return None


# ═══════════════════════════════════════════════════════════════════════════
# ARTICLE 1: India-Oman CEPA
# ═══════════════════════════════════════════════════════════════════════════
def write_oman_cepa():
    print('\n📰 Article 1: India-Oman CEPA')
    img = fetch_wikipedia_person_image('Piyush Goyal')
    if not img:
        img = fetch_pexels_image('Oman port trade ships', 'Gulf shipping trade')
    img = validate_image(img)

    body = """India's newest trade agreement went live on Monday, and its biggest advantage isn't on the tariff schedule — it's on the map.

The India-Oman Comprehensive Economic Partnership Agreement, or CEPA, came into force on June 1, 2026. On paper, it gives Indian exporters immediate zero-duty access to 98 per cent of Oman's tariff lines, covering 99.38 per cent of trade value. In practice, it opens a reliable trade corridor to the Gulf at a time when the Strait of Hormuz — through which most Gulf commerce flows — remains effectively disrupted.

## Why Oman Is Different

Unlike Saudi Arabia, the UAE, Qatar, and Kuwait, much of Oman's coastline sits outside the Strait of Hormuz, directly on the Arabian Sea and the Gulf of Oman. Its major ports — Salalah, Sohar, and Duqm — remain fully operational even when Hormuz traffic is blocked. Since the US-Iran conflict began disrupting Strait traffic in early 2026, India's imports from major Gulf economies plummeted from $15 billion in April 2025 to $9.8 billion in April 2026. Oman was the exception: India's imports from Oman surged 246 per cent in the same period, from $430 million to nearly $1.5 billion.

Commerce Minister Piyush Goyal, who presided over the formal entry-into-force ceremony on Monday, called the CEPA a gateway not just to Oman but to the wider Gulf Cooperation Council, East Africa, and the Indian Ocean economy. "More than ten consignments are already being shipped availing preferential duty access from different parts of India," he said.

## What Indian Exporters Get

The deal eliminates tariffs across sectors dominated by small businesses: textiles, leather, gems and jewellery, auto components, pharmaceuticals, medical devices, sports goods, agricultural products, marine products, and machinery. Before the CEPA, most Indian goods entering Oman faced an average 5 per cent duty, with rates as high as 100 per cent on select products. An estimated $3.64 billion in Indian exports become immediately more competitive.

For textile clusters in Tirupur, Surat, Ludhiana, and Coimbatore, the agreement means direct tariff-free access to a market that until now applied duties on most fabrics and garments. Goyal specifically noted that artisans and weavers across India would benefit from higher international demand.

Oman, in return, gets tariff concessions from India on 77.79 per cent of tariff lines, covering 94.81 per cent of its exports to India by value. The country has also committed to lifting its decades-old ban on exporting unpolished marble, allowing craftsmen in Rajasthan and Andhra Pradesh to source raw material directly.

## The Diaspora Angle

The CEPA goes beyond goods. Oman has committed to raising the ceiling for intra-corporate transferees from 20 per cent to 50 per cent and providing easier temporary entry for business visitors and independent professionals across 127 service sub-sectors, including legal, accounting, IT, medical, and tourism services.

For the roughly 780,000 Indians living in Oman — the largest expatriate community in the country — the agreement formalises professional mobility provisions that have until now been negotiated case by case. Indian professionals in sectors like healthcare, engineering, and finance now have a treaty-backed pathway to work in Oman with fewer bureaucratic hurdles.

## The Strategic Calculation

Bilateral trade between India and Oman stood at $11.18 billion in FY2025-26. That is modest by Gulf standards — India's trade with the UAE alone exceeds $80 billion. But as the Global Trade Research Initiative noted in its analysis: this is not just a trade agreement. It is an investment in India's long-term energy and economic security.

With the Strait of Hormuz conflict showing no sign of resolution — Iran and the US exchanged fresh strikes over the weekend — the Oman corridor is no longer a backup plan. It is becoming the primary route.

*Sources: Ministry of Commerce and Industry, GTRI, Hindu BusinessLine, IANS, Reuters*"""

    return insert_article({
        'headline': "India Just Opened a Trade Corridor to the Gulf That Doesn't Go Through the Strait of Hormuz.",
        'subheadline': "The India-Oman CEPA came into force on June 1, giving Indian exporters duty-free access to 98 per cent of Oman's tariff lines — and a strategic port network that bypasses the world's most dangerous chokepoint.",
        'body': body,
        'slug': 'india-oman-cepa-trade-pact-june-1-2026-hormuz-bypass-nri-mobility',
        'category': 'news',
        'vertical': 'news',
        'image_url': img,
        'image_attribution': get_image_attr(img),
        'sources': json.dumps([{'name': 'Ministry of Commerce and Industry'}, {'name': 'GTRI'}, {'name': 'Hindu BusinessLine'}, {'name': 'IANS'}, {'name': 'Reuters'}]),
        'tags': ['India-Oman', 'CEPA', 'trade', 'Hormuz', 'Gulf', 'exports', 'NRI'],
    })


# ═══════════════════════════════════════════════════════════════════════════
# ARTICLE 2: JEE Advanced 2026 Results
# ═══════════════════════════════════════════════════════════════════════════
def write_jee_results():
    print('\n📰 Article 2: JEE Advanced 2026 Results')
    img = fetch_pexels_image('Indian university students campus', 'engineering college India')
    img = validate_image(img)

    body = """Every year, roughly two million Indian students begin the pipeline that ends at one of the IITs — the engineering schools that have produced a disproportionate share of Silicon Valley's executives, America's tech workforce, and India's startup founders. On Monday, the latest round of results arrived.

Shubham Kumar, an 18-year-old from Gaya, Bihar, topped JEE Advanced 2026 with a score of 330 out of 360, securing All India Rank 1. He plans to study Computer Science at IIT Bombay — the same programme that has shaped the careers of Google's Sundar Pichai, Twitter's former CEO Parag Agrawal, and thousands of engineers now building AI systems across the world.

## The Numbers

IIT Roorkee, which administered this year's exam, released results on Monday morning. Out of 1,87,389 registered candidates, 1,79,694 appeared for both papers on May 17. Of those, 56,880 qualified — including 10,107 women, a number that continues to rise year over year.

Shubham was followed by Kabeer Chhillar of Gurugram with 329 marks and Jatin Chahar with 319 marks, both from the IIT Delhi zone. The top female qualifier was Arohi Deshpande, who secured Common Rank List position 77 with 280 marks.

## How the Topper Prepared

Shubham moved to Kota, Rajasthan — India's coaching capital — two years ago as a Class 11 student to attend Allen Career Institute. He followed a gruelling routine: 8 to 10 hours of study daily, cricket and badminton only on Sundays, and a self-imposed social media ban.

"I had been toiling hard for the entrance exam for two years, so it was natural to expect good marks," he told PTI. His father Shiv Kumar runs a hardware business in Gaya; his mother Kanchan Devi is a homemaker.

Shubham's consistency is striking. He scored 100 percentile in both sessions of JEE Main 2026 — in January and again in April — and 96.8 per cent in his CBSE Class 12 board exams. He credits self-study and conceptual understanding over rote memorisation, saying he did not attend private tuition until Class 10.

## The Kota Question

Kota has been in the headlines for years — not always for academic achievement. The city, which hosts hundreds of thousands of students preparing for IIT and medical entrance exams, has faced scrutiny over student mental health and multiple suicides linked to academic pressure. Shubham said he chose to ignore the negative coverage and focus on the ecosystem that draws students to the city year after year.

"I didn't use social media. I only used my phone to connect with my parents and teachers," he said. His strategy included regular meditation, which he credited as essential for maintaining focus during the two-year preparation grind.

## Why It Matters for the Diaspora

JEE Advanced is the single largest feeder into the IIT system, and the IITs remain the single largest feeder into India's global tech workforce. In the United States alone, IIT alumni lead companies worth trillions of dollars, run major research labs, and dominate H-1B visa applications in the technology sector.

For NRI families watching from the US, Canada, and the UK, JEE results are a yearly reminder of the pipeline — and the pressure system — that produces the engineers they work alongside. The 56,880 students who qualified on Monday will spend four years at one of 23 IITs before many of them board flights to the same cities where the diaspora already lives.

The JoSAA counselling process begins shortly, with seat allocation running through July. For Shubham Kumar and 56,879 others, the next chapter starts now.

*Sources: IIT Roorkee, Careers360, PTI, IANS, DevDiscourse*"""

    return insert_article({
        'headline': "A Student From Bihar Just Topped India's Toughest Engineering Exam. He Studied 10 Hours a Day and Stayed Off Social Media.",
        'subheadline': "Shubham Kumar scored 330 out of 360 on JEE Advanced 2026 to claim All India Rank 1. Over 56,000 students qualified from nearly 1.8 lakh who sat the exam.",
        'body': body,
        'slug': 'jee-advanced-2026-results-shubham-kumar-air-1-iit-56880-qualify',
        'category': 'news',
        'vertical': 'news',
        'image_url': img,
        'image_attribution': get_image_attr(img),
        'sources': json.dumps([{'name': 'IIT Roorkee'}, {'name': 'Careers360'}, {'name': 'PTI'}, {'name': 'IANS'}, {'name': 'DevDiscourse'}]),
        'tags': ['JEE Advanced', 'IIT', 'education', 'Bihar', 'engineering', 'Shubham Kumar'],
    })


# ═══════════════════════════════════════════════════════════════════════════
# ARTICLE 3: India Fiscal Deficit 4.4%
# ═══════════════════════════════════════════════════════════════════════════
def write_fiscal_deficit():
    print('\n📰 Article 3: India Fiscal Deficit 4.4%')
    img = fetch_wikipedia_person_image('Nirmala Sitharaman')
    if not img:
        img = fetch_pexels_image('India parliament budget economy', 'Indian rupee finance')
    img = validate_image(img)

    body = """India's government delivered on a fiscal promise that even its own analysts thought might slip.

Data released on Monday by the Controller General of Accounts showed that India's fiscal deficit for the year ended March 31, 2026, stood at 4.4 per cent of GDP — precisely matching the revised estimate presented by Finance Minister Nirmala Sitharaman in the February budget. The absolute figure: ₹15.19 trillion ($159.9 billion), or 97.5 per cent of the revised estimate.

## The Numbers Behind the Number

The government collected ₹33 trillion in net tax receipts, up from ₹30.87 trillion the previous year — a 7 per cent increase that came despite a ₹1 trillion revenue hit from raising the income tax threshold from ₹700,000 to ₹1.2 million. Non-tax revenue jumped to ₹6.8 trillion from ₹5.31 trillion, driven largely by dividends from the Reserve Bank of India and public sector companies.

Total government expenditure was ₹49 trillion, up from ₹47.16 trillion the previous year. Capital expenditure — the spending that goes into roads, railways, airports, and industrial corridors — reached ₹10.7 trillion, up from ₹10.18 trillion, maintaining the infrastructure-led growth strategy that has defined the government's economic policy.

## Why This Matters

Hitting the 4.4 per cent target is more impressive than the number suggests in isolation. The fiscal year was defined by extraordinary external shocks: the US-Iran war that effectively closed the Strait of Hormuz and sent oil prices soaring; a $47 billion drawdown of foreign exchange reserves as the RBI spent billions defending the rupee; and a sharp slowdown in foreign investment, including a record single-day sell-off of $2.22 billion by foreign institutional investors.

In August 2025, BMI — Fitch Solutions' analytics arm — had predicted the government would miss the target, forecasting a deficit of 4.5 per cent. The government proved the sceptics wrong through a combination of expenditure discipline and stronger-than-expected tax collections, particularly in the second half of the year.

## Fiscal Consolidation, Year by Year

The deficit has narrowed steadily from its pandemic peak of over 9 per cent in 2020-21. The trajectory — 6.4 per cent in 2022-23, 5.6 per cent in 2023-24, 4.8 per cent in 2024-25, and now 4.4 per cent — represents one of the most consistent fiscal consolidation runs among major emerging economies.

The government has signalled it will shift from deficit-to-GDP to debt-to-GDP as its primary fiscal benchmark starting FY2026-27, targeting a debt ratio of 50 per cent by March 2031, down from the current 57.1 per cent. It is a strategic pivot that follows global practice and gives the government more flexibility in how it manages its balance sheet.

## The Road Ahead Is Harder

The FY2026-27 budget targets a deficit of 4.3 per cent — another step down. But BMI has already warned that figure may be breached. The Strait of Hormuz conflict has forced the government to establish a ₹1 trillion Economic Stabilisation Fund to cushion energy and fertiliser costs, and subsidy spending — which had been trimmed to around 1.5 per cent of GDP in recent years — is expected to rise.

For Indian households and the diaspora watching from abroad, the arithmetic is direct: the government's ability to keep spending on infrastructure while holding the deficit in check determines whether roads get built, trains arrive on time, and the cost of borrowing stays affordable. For the millions of NRIs sending remittances home, fiscal stability also underpins the rupee's value — and by extension, the purchasing power of every dollar they wire back. For now, the books balance.

*Sources: Controller General of Accounts, Reuters, BMI/Fitch Solutions, Ministry of Finance*"""

    return insert_article({
        'headline': "India Hit Its Fiscal Deficit Target Despite a War, an Oil Shock, and a $47 Billion Reserve Drawdown.",
        'subheadline': "The government's 2025-26 fiscal deficit came in at 4.4 per cent of GDP — exactly where it was budgeted — as tax receipts grew 7 per cent and capital spending crossed ₹10.7 trillion.",
        'body': body,
        'slug': 'india-fiscal-deficit-4-4-percent-fy26-on-target-war-oil-economy',
        'category': 'news',
        'vertical': 'news',
        'image_url': img,
        'image_attribution': get_image_attr(img),
        'sources': json.dumps([{'name': 'Controller General of Accounts'}, {'name': 'Reuters'}, {'name': 'BMI/Fitch Solutions'}, {'name': 'Ministry of Finance'}]),
        'tags': ['fiscal deficit', 'economy', 'budget', 'GDP', 'tax', 'infrastructure', 'RBI'],
    })


# ═══════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    ok = 0
    for fn in [write_oman_cepa, write_jee_results, write_fiscal_deficit]:
        try:
            if fn():
                ok += 1
        except Exception as e:
            print(f'  ✗ Error in {fn.__name__}: {e}')
            import traceback; traceback.print_exc()
    print(f'\n{"="*60}')
    print(f'Published {ok}/3 articles')
    sys.exit(0 if ok >= 2 else 1)
