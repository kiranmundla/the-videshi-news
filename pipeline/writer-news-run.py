#!/usr/bin/env python3
"""News writer — publishes 4 fresh articles to Supabase."""

import json, os, sys, uuid, re, time
from datetime import datetime, timezone

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
load_env(os.path.expanduser('~/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

import requests
import urllib.parse

# ─── Image sourcing ───

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
    """Fetch a relevant image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0].get('src', {}).get('large2x') or photos[0].get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate image URL returns a real image > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if 'image' in ct and cl > 5000:
            return True
        # Try GET for servers that don't support HEAD well
        r = requests.get(url, timeout=10, stream=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if 'image' in ct and cl > 5000:
            return True
        # Check first chunk
        chunk = next(r.iter_content(8192), b'')
        if len(chunk) > 5000 and 'image' in ct:
            return True
    except Exception as e:
        print(f"  ⚠ Image validation failed for {url[:60]}: {e}")
    return False

def is_banned_url(url):
    """Check if URL is from a banned source."""
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com']
    banned_params = ['_nc_ht=', '_nc_cat=', 'ccb=']
    for b in banned:
        if b in url:
            return True
    for p in banned_params:
        if p in url:
            return True
    return False

def get_image(person_name=None, pexels_query=None, pexels_fallback=None):
    """Get best available image. Wikipedia first for people, then Pexels."""
    if person_name:
        url = fetch_wikipedia_person_image(person_name)
        if url and not is_banned_url(url) and validate_image(url):
            return url, "Wikimedia Commons"
    
    if pexels_query:
        url = fetch_pexels_image(pexels_query, pexels_fallback)
        if url and not is_banned_url(url) and validate_image(url):
            return url, "Pexels"
    
    return None, None

# ─── Supabase helpers ───

def sb_insert(table, data):
    """Insert a row into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        },
        json=data,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0]
        return result
    else:
        print(f"  ✗ Insert error {r.status_code}: {r.text[:200]}")
        return None

# ─── Articles ───

articles = []

# ── Article 1: Supreme Court Reliance ₹447 Crore ──
articles.append({
    "headline": "Supreme Court Overturns ₹447 Crore Fraud Order Against Reliance. SEBI Must Return ₹250 Crore.",
    "subheadline": "India's apex court ruled that breaching position limits is not the same as committing fraud — a distinction that could reshape how SEBI pursues market manipulation cases for years to come.",
    "slug": "supreme-court-reliance-industries-sebi-447-crore-fraud-overturned-rpl-20260530",
    "category": "news",
    "vertical": "news",
    "person": "Mukesh Ambani",
    "pexels_query": "India Supreme Court building",
    "pexels_fallback": "India stock market trading",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/"},
        {"name": "LiveMint", "url": "https://www.livemint.com/"},
        {"name": "Bar and Bench", "url": "https://www.barandbench.com/"},
        {"name": "LiveLaw", "url": "https://www.livelaw.in/"}
    ]),
    "body": """India's Supreme Court on Friday handed Reliance Industries a major legal victory, overturning a ₹447.27 crore disgorgement order imposed by the Securities and Exchange Board of India in a case that has wound through the Indian legal system for nearly two decades.

A bench comprising Justices J.B. Pardiwala and R. Mahadevan set aside findings of fraud and market manipulation that SEBI had recorded against Mukesh Ambani's conglomerate in connection with trading in shares and derivatives of Reliance Petroleum Ltd during November 2007. The court directed SEBI to refund ₹250 crore that Reliance had deposited in the Investor Protection Fund during the pendency of the appeal.

## What the Case Was About

The dispute dates back to November 2007, when Reliance Industries — then holding roughly 75 percent of Reliance Petroleum — decided to sell about 5 percent of its stake, amounting to approximately 22.5 crore shares. Ahead of the sale, RIL had entered into arrangements with 12 entities that took short positions in RPL futures contracts. The profits and losses from those trades ultimately flowed back to the parent company.

SEBI investigated the transactions and, in a 2020 order, ruled that the arrangement amounted to fraud and market manipulation. The regulator said RIL had circumvented position limits in derivatives, cornered the market, and influenced settlement prices. SEBI directed the company to repay ₹447.27 crore — plus 12 percent annual interest — to investors.

Reliance challenged the order before the Securities Appellate Tribunal, which upheld SEBI's findings in a majority decision. The company then approached the Supreme Court.

## The Court's Reasoning

The Supreme Court held that the SAT had committed an "egregious error" in sustaining SEBI's fraud findings. In a 136-page judgment, the court drew a critical distinction between regulatory violations and fraud.

"There is no legal requirement to ensure a perfect hedge with a 1:1 ratio," the court observed, adding that hedging is a legitimate risk-management tool. The bench ruled that a breach of position limits is a regulatory violation but does not, by itself, establish the higher threshold of fraud required under the SEBI (Prohibition of Fraudulent and Unfair Trade Practices) Regulations.

SEBI, the court said, had failed to meet the burden of proof required to establish that Reliance had engaged in deliberate manipulation.

## What Survived

The ruling was not a complete exoneration. The Supreme Court upheld a separate ₹25 crore penalty imposed on RIL for violating disclosure requirements under SEBI's 2001 derivatives position-limit framework. The company's breach of position limits was acknowledged as a regulatory failure — just not fraud.

## Why This Matters for NRIs and Indian Markets

The judgment is likely to have significant implications for how India's capital markets regulator pursues market manipulation cases going forward. By raising the evidentiary bar for fraud findings, the court has effectively limited SEBI's ability to treat every position-limit violation as evidence of manipulative intent.

For NRI investors with exposure to Indian equities — and particularly to Reliance, which is one of the most widely held stocks among diaspora investors — the ruling removes a long-standing legal overhang. Reliance Industries, which recently became the first Indian company to cross $120 billion in annual revenue, has been carrying this case on its books for years.

Legal experts say the judgment could also encourage more aggressive legal challenges to SEBI enforcement actions, particularly in cases where the regulator has relied on circumstantial evidence to establish fraud.

Neither Reliance Industries nor SEBI immediately responded to requests for comment on the ruling."""
})

# ── Article 2: Fed Rate Hike Signals ──
articles.append({
    "headline": "The Fed Is Now Openly Talking About Raising Interest Rates. NRIs With American Mortgages Should Pay Attention.",
    "subheadline": "Multiple Federal Reserve officials said on Friday they may need to hike rates if the Iran war keeps pushing inflation higher. The PCE index just hit 3.8 percent.",
    "slug": "fed-rate-hike-signals-iran-war-inflation-nri-mortgages-remittances-20260530",
    "category": "news",
    "vertical": "news",
    "person": None,
    "pexels_query": "Federal Reserve building Washington DC",
    "pexels_fallback": "US dollar bills currency finance",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/markets/us/"},
        {"name": "Federal Reserve", "url": "https://www.federalreserve.gov/"},
        {"name": "Bureau of Economic Analysis", "url": "https://www.bea.gov/"}
    ]),
    "body": """For months, the Federal Reserve held the line. Interest rates were in a good place. Patience was the right posture. The Iran war would be temporary. The energy shock would pass.

On Friday, that posture cracked.

Multiple Fed officials — including some of the central bank's most dovish voices — publicly acknowledged that interest rates may need to go up, not down, if the war-driven inflation surge proves more persistent than initially expected. For the estimated 4.4 million Indian Americans in the United States, many of whom hold variable-rate mortgages, auto loans, and credit card debt, the shift matters.

## What Changed

The Personal Consumption Expenditures Price Index — the Fed's preferred inflation gauge — climbed to 3.8 percent year-over-year in April, up from 3.5 percent in March. A separate New York Fed measure of underlying inflation dynamics jumped to 4 percent from 3.5 percent. Both readings are well above the Fed's 2 percent target, which has now been exceeded for years running.

The culprit is energy. The three-month war between the United States and Iran has effectively closed the Strait of Hormuz, through which roughly one-fifth of the world's oil and gas supply normally flows. Brent crude, though it fell to $92 on Friday amid ceasefire hopes, remains sharply above pre-war levels.

## What Fed Officials Are Saying

Fed Vice Chair for Supervision Michelle Bowman, speaking at a conference in Iceland, said that if energy disruptions persist into the second half of the year, she would "consider shifting my approach to thinking about the balance of risks" — a carefully worded nod toward supporting a rate hike.

Minneapolis Fed President Neel Kashkari, one of three hawkish dissenters at last month's policy meeting, said the risk of unanchored inflation expectations was real. "I think it is premature for me to conclude we need to be raising rates right away," he said, "but it makes me further pay attention to the risk that inflation could continue to climb."

Kansas City Fed President Jeffrey Schmid was more direct: "My primary concern is inflation, which is too hot and has been above target for too long." He dismissed the textbook approach of treating energy shocks as transitory, saying it is "not viable right now."

Even San Francisco Fed President Mary Daly, who said policy was "in a good place," acknowledged that a persistent rise in oil prices would change her outlook.

## The NRI Impact

Financial markets are now pricing in a rate hike by year's end, likely lifting the federal funds rate above the current 3.50-3.75 percent range. For NRIs, the implications run across multiple channels.

**Mortgages and loans.** Anyone with an adjustable-rate mortgage, a home equity line of credit, or a variable-rate auto loan will see payments increase if the Fed raises rates. With Indian Americans disproportionately concentrated in high-cost housing markets like the Bay Area, New Jersey, and the New York metro, even a 25-basis-point hike translates into meaningful monthly increases.

**Remittances.** Higher US rates tend to strengthen the dollar against the rupee, which makes remittances cheaper in dollar terms but more valuable in rupee terms. Families sending money home may see more rupees per dollar — a modest silver lining.

**Savings and deposits.** NRI fixed deposits and savings accounts at US banks could see improved rates. But the flip side is higher borrowing costs for anyone leveraged.

**Indian markets.** A Fed hike would likely trigger capital outflows from emerging markets, including India. The rupee, which has already been under pressure from elevated oil import bills, could face further depreciation.

## What Comes Next

The Fed's next policy meeting is in June. Most officials signaled they would hold rates steady at that meeting while monitoring incoming data. But the door to a hike is now explicitly open — a shift from even a month ago, when the dominant expectation was for the next move to be a cut.

The key variable remains the Iran war. If a ceasefire deal holds and the Strait of Hormuz reopens in the coming weeks, oil prices could fall sharply, easing inflationary pressure and removing the case for tighter policy. If the ceasefire collapses — as the brief April truce did — the Fed may have no choice but to act.

For NRIs, the message is straightforward: lock in fixed rates where possible, review variable-rate exposures, and prepare for a monetary policy environment that may tighten further before it eases."""
})

# ── Article 3: Pentagon Chief Praises India at Shangri-La ──
articles.append({
    "headline": "Pentagon Chief Praises India's Military Readiness at Shangri-La. Then He Told Asian Allies to Spend 3.5% of GDP on Defense.",
    "subheadline": "US Defense Secretary Pete Hegseth singled out India as a partner that is 'improving military readiness' — while warning that freeloading allies will be pushed to the back of the line.",
    "slug": "hegseth-shangri-la-india-military-readiness-defense-spending-china-20260530",
    "category": "news",
    "vertical": "news",
    "person": "Pete Hegseth",
    "pexels_query": "military defense aircraft carrier navy",
    "pexels_fallback": "Singapore skyline Asia",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/asia-pacific/"},
        {"name": "LiveMint", "url": "https://www.livemint.com/"},
        {"name": "The Times", "url": "https://www.thetimes.com/"},
        {"name": "US Department of Defense", "url": "https://www.defense.gov/"}
    ]),
    "body": """US Defense Secretary Pete Hegseth on Saturday used Asia's most important security forum to deliver a blunt message to the region: China's military buildup is real, potentially imminent, and the era of American security subsidies is over.

Speaking at the Shangri-La Dialogue in Singapore, Hegseth singled out India as a model partner that is actively improving its military readiness — a notable endorsement at a moment when New Delhi is navigating complex relationships with both Washington and Beijing.

## The India Mention

In a speech that covered the full sweep of Indo-Pacific strategy, Hegseth praised India for investing in its own defense capabilities and improving military readiness. The comment, while brief, is significant in context. India has been steadily increasing its defense budget — it stood at roughly $75 billion in the 2025-26 fiscal year — and has accelerated purchases of American military hardware, including MQ-9B drones, MH-60R helicopters, and C-130J transport aircraft.

The endorsement also comes weeks after the India-South Korea defense and cyber pact signed in Seoul and just days after Commerce Minister Piyush Goyal's 10-day trade sprint across North America. Washington is clearly signaling that India is a preferred partner — one that is spending, modernizing, and aligning without needing to be coerced.

## The Demand: 3.5% of GDP

But the larger message was aimed at the room. Hegseth told assembled defense ministers, military chiefs, and diplomats that the United States expects its Asian allies and partners to raise defense spending to 3.5 percent of GDP — a target that most Asian nations currently fall far short of.

"Deterrence doesn't come on the cheap," Hegseth said. "The era of the United States subsidizing the defence of wealthy nations is over."

He outlined a carrot-and-stick framework: allies that meet the spending threshold will be "moved to the front of the line" for expedited arms sales, deeper industrial collaboration, and expanded intelligence sharing. Those that don't will "face a clear shift in how we do business."

The 3.5 percent target is aggressive. India currently spends roughly 2.4 percent of GDP on defense. Japan, which has been rapidly rearming, recently hit 2 percent. Most ASEAN nations hover around 1 to 2 percent. Meeting the target would require transformative budget reallocations across the region.

## The China Warning

Hegseth delivered his sharpest public comments yet on China's military posture, saying there is "rightful alarm" over Beijing's rapid buildup and the expansion of its military activities.

"A Pacific dominated by any hegemon would unravel the regional balance of power," he said. "No state, including China, can impose its hegemony and hold the security or prosperity of our nation and our allies in question."

But he also struck a measured tone on the state of the US-China relationship, saying ties are "better than they have been in many years" following the Trump-Xi summit in Beijing earlier this month. Military-to-military communication has increased, he noted, and meetings between US and Chinese counterparts are happening more frequently.

## Why This Matters for the Diaspora

For India and its diaspora, the Shangri-La speech reinforces a pattern. The US-India defense partnership has deepened significantly since the early 2020s, with bilateral military exercises, technology transfers, and intelligence-sharing agreements all expanding. India's participation in the Quad — alongside the US, Japan, and Australia — has become a cornerstone of the Indo-Pacific architecture.

The 3.5 percent GDP target, however, could create friction. India's defense budget is large in absolute terms but constrained as a share of GDP by competing demands — infrastructure, social spending, and debt servicing. If Washington begins using spending levels as a filter for partnership quality, New Delhi may face pressure to accelerate defense procurement, potentially at the expense of other priorities.

The speech also carried an implicit message about Taiwan. Hegseth, who last year suggested a Chinese invasion could be imminent, was more restrained this time but made clear that the US views its Pacific military presence as non-negotiable.

For Indian Americans working in defense, aerospace, and technology sectors — and for NRI investors exposed to Indian defense stocks like HAL, BEL, and Bharat Dynamics — the strategic alignment between Washington and New Delhi continues to create opportunities. The question is whether India can meet the spending expectations that come with being called a model ally."""
})

# ── Article 4: Texas SB4 Migrant Arrest Law ──
articles.append({
    "headline": "Texas Can Now Arrest and Deport People Suspected of Crossing Illegally. The Law Is in Effect as of Friday.",
    "subheadline": "A federal appeals court lifted an injunction against SB4, a law that makes unauthorized border crossing a state crime and lets Texas judges — not federal ones — issue deportation orders.",
    "slug": "texas-sb4-migrant-arrest-law-enforceable-fifth-circuit-immigration-nri-20260530",
    "category": "news",
    "vertical": "news",
    "person": None,
    "pexels_query": "Texas US Mexico border wall fence",
    "pexels_fallback": "immigration US passport visa",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/us/"},
        {"name": "Fox 7 Austin", "url": "https://www.fox7austin.com/"},
        {"name": "ACLU of Texas", "url": "https://www.aclutx.org/"}
    ]),
    "body": """A federal appeals court on Friday cleared the way for Texas to enforce one of the most aggressive state-level immigration laws in American history, allowing local police officers to arrest people suspected of having crossed the US-Mexico border illegally and state judges to issue deportation orders.

The 2-1 ruling by the New Orleans-based 5th US Circuit Court of Appeals lifted a preliminary injunction that a federal judge had imposed on May 14, making key provisions of Senate Bill 4 enforceable immediately. The ACLU and Texas Civil Rights Project, which represent thousands of non-citizens who could be subject to the law, called the decision "disappointing" and vowed to continue fighting.

## What SB4 Does

The law, originally passed in 2023 during a special Texas legislative session, creates a parallel state-level immigration enforcement system that operates alongside — and in some cases in place of — the federal immigration apparatus.

Under SB4, state and local police officers in Texas are authorized to detain anyone they suspect of being a non-US citizen who entered the state from Mexico or another country without authorization. The law creates a new state crime of "illegal entry" into Texas, punishable by up to six months in jail. For individuals who have previously been deported or denied admission, the charge escalates to "illegal re-entry," carrying a sentence of 10 to 20 years.

Most controversially, the law empowers Texas state judges — who are not trained in immigration law and have no federal authority over immigration matters — to issue deportation orders. Individuals who refuse to comply with a state deportation order face an additional charge punishable by 2 to 20 years in prison.

## The Legal Battle

SB4 has been the subject of intense litigation since its passage. The Biden administration initially challenged the law, arguing it unconstitutionally usurped the federal government's exclusive authority over immigration enforcement. A federal judge agreed and blocked the law from taking effect.

After the Trump administration took office, it dropped the federal government's challenge. But immigrant-rights organizations pressed on, filing a new class-action lawsuit on behalf of non-citizens directly affected by the law's provisions.

On May 14, US District Judge David Ezra issued a fresh injunction, ruling that SB4 improperly encroached on federal authority. Texas Attorney General Ken Paxton — who is running for a US Senate seat — immediately appealed. The 5th Circuit stayed the injunction on Friday, with Judge Leslie Southwick dissenting.

## Why NRIs and Indian Immigrants Should Care

While SB4 is aimed primarily at the US-Mexico border, its provisions are not limited to any specific nationality. The law applies to anyone suspected of unauthorized entry into Texas, regardless of origin.

Indian nationals represent one of the fastest-growing groups of unauthorized border crossers. In fiscal year 2024, US Customs and Border Protection encountered over 90,000 Indian nationals at the southern border — many of whom had traveled through Central America after flying to countries like Nicaragua or Ecuador. The numbers have remained elevated in 2025 and 2026.

For Indian immigrants in Texas — including those on expired visas, in pending immigration proceedings, or in gray-area situations — the law introduces a new layer of risk. Unlike federal immigration enforcement, which is handled by trained ICE agents and immigration judges, SB4 puts enforcement power in the hands of local police officers and state magistrates who may have limited understanding of the complexities of immigration status.

Immigration attorneys have flagged concerns that the law could lead to racial profiling, particularly in communities with large South Asian, Latino, and Middle Eastern populations. The ACLU has warned that even legal residents and US citizens could be swept up in enforcement actions based on appearance or accent.

Texas Governor Greg Abbott celebrated the ruling on Friday. "We will keep fighting in the courts, working with President Trump, and doing everything necessary to secure our border and protect Texans," he posted on X.

For the Indian American community in Texas — which is concentrated in the Houston, Dallas-Fort Worth, and Austin metros — the immediate advice from immigration lawyers is clear: carry documentation at all times, know your rights under the Fourth Amendment, and consult an attorney if approached by law enforcement about immigration status.

The ACLU of Texas has published a "Know Your Rights" guide specific to SB4, updated as of May 29, 2026. The organization maintains that the law remains unconstitutional and expects the litigation to continue through federal courts."""
})

# ─── Publish ───

published_count = 0
now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

for art in articles:
    print(f"\n{'='*60}")
    print(f"Publishing: {art['headline'][:80]}...")
    
    # Get image
    img_url, img_attr = get_image(
        person_name=art.get('person'),
        pexels_query=art.get('pexels_query'),
        pexels_fallback=art.get('pexels_fallback')
    )
    
    if img_url:
        print(f"  ✓ Image: {img_url[:80]}...")
    else:
        print(f"  ⚠ No image found — publishing without image")
    
    # Build record
    record = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "body": art["body"],
        "category": art["category"],
        "vertical": art["vertical"],
        "status": "published",
        "published_at": now,
        "sources": art["sources"],
        "image_url": img_url,
        "image_attribution": img_attr,
    }
    
    # Remove None values
    record = {k: v for k, v in record.items() if v is not None}
    
    result = sb_insert("p2_articles", record)
    if result:
        art_id = result.get('id', 'unknown')
        print(f"  ✓ Published! ID: {art_id}")
        published_count += 1
    else:
        print(f"  ✗ Failed to publish")
    
    time.sleep(1)

print(f"\n{'='*60}")
print(f"Done. Published {published_count}/{len(articles)} articles.")
