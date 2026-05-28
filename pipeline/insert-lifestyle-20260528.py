#!/usr/bin/env python3
"""Insert the two articles into Supabase with correct schema."""
import json, os, subprocess, urllib.parse, urllib.request
from datetime import datetime, timezone

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

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

now_iso = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

articles = [
    {
        "id": "f32e53ed-9cb6-4ee5-93bd-e0a7177cc603",
        "slug": "surgeon-general-screen-time-public-health-crisis-indian-american-parents-20260528",
        "headline": "America Just Declared Your Child's Screen Time a Public Health Crisis. The Recommended Limit for Teenagers Is Two Hours a Day. Most Indian-American Kids Are Doing Double That.",
        "subheadline": "A new Surgeon General's advisory calls for bell-to-bell phone bans in schools, age-gated design changes from tech companies, and family media plans. For Indian-American parents who grew up without screens, the rules of engagement just changed.",
        "body": """The United States government has done something it rarely does about technology: it issued a formal public health warning.

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

*Sources: CNN, HHS.gov, NBC Palm Springs, American Academy of Pediatrics, UCSF Adolescent Brain Cognitive Development Study, JAMA Network*""",
        "category": "lifestyle-health",
        "vertical": "health",
        "image_url": f"{SUPABASE_URL}/storage/v1/object/public/article-images/f32e53ed-9cb6-4ee5-93bd-e0a7177cc603.jpg",
        "image_attribution": "Pexels",
        "sources": "CNN, HHS.gov, NBC Palm Springs, American Academy of Pediatrics, UCSF Adolescent Brain Cognitive Development Study, JAMA Network",
        "status": "published",
        "published_at": now_iso,
    },
    {
        "id": "ef3f33ce-a93b-4141-91d8-14680af06ee3",
        "slug": "india-coal-india-divestment-ofs-central-bank-800-billion-rupees-nri-20260528",
        "headline": "India Just Sold Shares in Coal India at a 10 Per Cent Discount. It Sold Central Bank of India the Week Before. The Government's ₹800 Billion Sell-Off Is Accelerating.",
        "subheadline": "Modi's divestment machine is back in gear. Two major public-sector stake sales in one week, a stock market battered by the Iran war, and an ₹800 billion target to hit by March 2027. Here is what NRI investors need to know.",
        "body": """The Indian government is selling assets faster than it has in years, and the timing tells you everything about the pressure it is under.

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

*Sources: Reuters, Angel One, Multibagg, SRK Analytics, Copley Fund Research, Reserve Bank of India*""",
        "category": "markets-finance",
        "vertical": "economy",
        "image_url": f"{SUPABASE_URL}/storage/v1/object/public/article-images/ef3f33ce-a93b-4141-91d8-14680af06ee3.jpg",
        "image_attribution": "Pexels",
        "sources": "Reuters, Angel One, Multibagg, SRK Analytics, Copley Fund Research, Reserve Bank of India",
        "status": "published",
        "published_at": now_iso,
    },
]

# Insert each article
for art in articles:
    print(f"\nPublishing: {art['headline'][:80]}...")
    print(f"  Category: {art['category']}, Vertical: {art['vertical']}")
    
    word_count = len(art['body'].split())
    print(f"  Words: {word_count}")
    
    data = json.dumps(art).encode()
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        data=data,
        headers={
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation',
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            print(f"  ✓ Published: {art['slug']}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ✗ Error {e.code}: {body[:400]}")
    except Exception as e:
        # IncompleteRead on Supabase — check if actually inserted
        print(f"  ⚠ Exception: {e}")
        try:
            check_url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{art['id']}&select=id,slug"
            check_req = urllib.request.Request(check_url, headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
            })
            with urllib.request.urlopen(check_req, timeout=10) as resp:
                check_data = json.loads(resp.read())
                if check_data:
                    print(f"  ✓ Actually inserted despite error")
                else:
                    print(f"  ✗ Not inserted")
        except:
            pass

print("\nDone.")
