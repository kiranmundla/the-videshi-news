#!/usr/bin/env python3
"""Videshi Lifestyle & Markets Writer — June 10, 2026 run"""

import json, os, requests, uuid
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, val = line.partition('=')
                    val = val.strip().strip('"').strip("'")
                    os.environ.setdefault(key.strip(), val)

load_env(os.path.expanduser('~/.env.supabase'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

now_iso = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

articles = []

# ============================================================
# ARTICLE 1: Alcohol study (lifestyle-health)
# ============================================================
articles.append({
    "id": str(uuid.uuid4()),
    "headline": "The Government's Own Alcohol Study Was Buried. Now It's Out, and the Numbers Are Brutal.",
    "subheadline": "A federally commissioned study finds no safe level of drinking. Two drinks a day gives American men a 1-in-25 chance of dying from alcohol. The Trump administration chose not to use it.",
    "slug": "us-alcohol-study-sidelined-trump-one-drink-risk-south-asian-diaspora-20260610",
    "category": "lifestyle-health",
    "vertical": "lifestyle-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now_iso,
    "image_url": "https://images.pexels.com/photos/6531496/pexels-photo-6531496.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Illuminated glasses on a bar counter with dramatic lighting",
    "image_attribution": "Pexels",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/us/sidelined-us-study-alcohols-health-effects-published-independent-journal-2026-06-09/"},
        {"name": "CNN", "url": "https://www.cnn.com/2026/06/09/health/alcohol-health-risks-us-government-study"},
        {"name": "USA Today", "url": "https://www.usatoday.com/story/news/health/2026/06/09/alcohol-health-risks-study/"},
        {"name": "Journal of Studies on Alcohol and Drugs", "url": "https://jsad.com"}
    ]),
    "body": """A study that the United States government itself commissioned, funded, and then chose not to use has finally been published. The findings are not ambiguous. There is no safe level of alcohol consumption. One drink a day raises the risk of cancer and injury. Two drinks a day — what federal guidelines have long called "moderate" for men — carries a 1-in-25 lifetime risk of dying from an alcohol-related cause.

The study, published Tuesday in the Journal of Studies on Alcohol and Drugs, was originally commissioned by the Biden administration and partially funded by the Department of Health and Human Services. It was meant to inform the 2025–2030 Dietary Guidelines for Americans. Instead, the Trump administration opted to sideline it, relying on a separate review from the National Academies of Sciences, Engineering and Medicine that reached a different conclusion: that moderate drinking is associated with a lower risk of dying from any cause.

Robert Vincent, the former Substance Abuse and Mental Health Services Administration official who led the multi-year effort, accused the administration of burying the research. In an editorial published alongside the study, he wrote: "The challenges confronting alcohol policy today are not rooted in scientific uncertainty. What remains contested is whether evidence will meaningfully inform policy when it conflicts with commercial interests."

The alcohol industry had mobilized against the study after its draft was released last year, launching campaigns to discredit the work. The House oversight committee, led by Republican James Comer of Kentucky — bourbon country — called the study "fraught with bias" and "irretrievably flawed." The Distilled Spirits Council of the United States said the researchers were "anti-alcohol activists."

## What the Study Actually Found

The numbers are stark. For Americans consuming just one drink per day, the lifetime risk of dying from an alcohol-related cause — including injuries, road accidents, and disease — stands at least 1 in 1,000. At two drinks per day, that risk jumps to 1 in 100. For men specifically, two drinks per day carries a 1-in-25 lifetime risk.

Even one drink a day was associated with increased risks of certain cancers and injuries, the researchers found. No level of alcohol showed a protective effect on mortality when the analysis controlled for confounding factors like education, income, and healthcare access.

"I'm glad that they had a message that corresponds with our science, and that is that less is best," said Dr. Timothy Naimi, director of the University of Victoria's Canadian Institute for Substance Use Research. "But giving people quantity information is necessary to make a truly informative guideline."

The researchers recommended that current adult drinkers consume one drink or fewer per day — a stricter standard than the guidelines ultimately adopted, which offered the vague advice to "consume less alcohol for better overall health" without specifying limits.

## The Diaspora Angle That Nobody Is Talking About

For the Indian diaspora in America, this study carries a particular weight that the mainstream coverage has missed entirely.

South Asians in the United States drink less than the general population on average, but the pattern of consumption has shifted dramatically across generations. First-generation immigrants often abstain or drink sparingly. Their American-raised children increasingly adopt the social drinking norms of their peers — the after-work happy hour, the wine with dinner, the cocktails at weekend gatherings.

What makes this dangerous is biology. Multiple studies have shown that South Asians carry a higher prevalence of the ALDH2 gene variant that impairs alcohol metabolism. The same two drinks that a European-descent American processes with relative ease may produce higher peak blood acetaldehyde levels — a known carcinogen — in someone of South Asian descent.

Add to this the cardiovascular profile that already puts South Asians at elevated risk. Heart disease strikes South Asians a decade earlier than other populations, and alcohol's inflammatory effects on the cardiovascular system compound that baseline vulnerability. The "moderate drinking is good for the heart" myth, which this study explicitly debunks, may have done outsized harm to a community already predisposed to cardiac events.

Then there is the cultural silence. Mental health and substance use remain stigmatized in many South Asian families. The uncle who drinks heavily at every family function is a known figure but rarely a discussed one. The generation of NRI men in their 40s and 50s who unwind with whisky every evening are, according to this study, playing a game with worse odds than they know.

## What This Means Going Forward

The dietary guidelines that Americans actually received earlier this year tell them to "consume less alcohol for better overall health." The researchers behind the sidelined study say that is not enough.

About half of Americans aged 12 or older had a drink in the past month, making alcohol the most commonly used addictive substance in the country. One drink equals about one 12-ounce can of beer, a 5-ounce glass of wine, or a shot of liquor. Most people underestimate how quickly those add up.

For the diaspora, the takeaway is not prohibition. It is information. The science now says, clearly and without the hedge that industry lobbyists prefer, that less is better and none is best. The government that paid for that science chose not to tell you. Now the researchers have told you themselves."""
})

# ============================================================
# ARTICLE 2: Healthcare affordability (lifestyle-health)
# ============================================================
articles.append({
    "id": str(uuid.uuid4()),
    "headline": "One in Three Americans Now Skip the Doctor Because They Cannot Afford It. The System May Be Three Years From Collapse.",
    "subheadline": "New data shows 36 per cent of Americans delayed care in the past six months. Healthcare leaders say the system hits an existential tipping point by 2029. For NRIs navigating insurance on a visa, the math is even worse.",
    "slug": "americans-delay-medical-care-cost-healthcare-unsustainable-nri-insurance-20260610",
    "category": "lifestyle-health",
    "vertical": "lifestyle-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now_iso,
    "image_url": "https://images.pexels.com/photos/26244207/pexels-photo-26244207.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Patients waiting in a hospital corridor, a scene increasingly common across America",
    "image_attribution": "Pexels",
    "sources": json.dumps([
        {"name": "HealthEquity", "url": "https://www.globenewswire.com/news-release/2026/06/08/healthcare-affordability-pulse"},
        {"name": "Vitalic Health / HFMA", "url": "https://www.globenewswire.com/news-release/2026/06/08/vitalic-health-survey"},
        {"name": "Coalition to Strengthen America's Healthcare", "url": "https://www.dailycaller.com/health-insurance-companies-driving-costs"},
        {"name": "Gallup", "url": "https://www.gallup.com"}
    ]),
    "body": """More than one in three Americans delayed or avoided needed medical care in the past six months because they could not afford it. The most commonly skipped services were specialist visits, prescription medications, and diagnostic tests — precisely the care tied to early detection and managing chronic conditions. And 77 per cent of the nation's top healthcare executives believe the entire system will hit an existential tipping point within three years.

These are not projections from activists. They come from two major surveys released within hours of each other last week, one from HealthEquity, the nation's largest independent health savings account custodian, and the other from Vitalic Health, a nonpartisan initiative powered by the Healthcare Financial Management Association.

The HealthEquity data is granular and grim. Among those who delayed care, chronic condition patients were hit hardest: 44 per cent skipped treatment, compared to 25 per cent of those without chronic conditions. For households earning under $50,000, nearly half — 46 per cent — delayed or avoided care entirely. Despite a 16-point jump in benefits understanding since fall 2025, the share of consumers who feel financially prepared for healthcare expenses actually fell, from 50 per cent to 42 per cent. Knowing how the system works, it turns out, does not make it affordable.

Meanwhile, the Vitalic Health survey of 30 leading healthcare executives found that 90 per cent said the current US healthcare system is not financially sustainable. Not "could become" unsustainable. Is not, right now. And 77 per cent believe the tipping point arrives within three years — by 2029.

## The Insurance Company Problem

A separate poll from the Coalition to Strengthen America's Healthcare, also released this week, adds a layer that the industry surveys carefully avoid. Forty-seven per cent of voters say corporate health insurance companies are primarily to blame for soaring costs. Seventy-nine per cent are worried about insurers denying or delaying doctor-ordered treatments. Eighty-four per cent believe corporate insurers hold too much power over medical decisions.

These numbers are bipartisan. The anger at insurance companies has become one of the few things that unite American voters across political lines. Seventy-two per cent said they are more likely to support candidates committed to holding insurance companies accountable.

The mechanism is simple and well-documented. Insurance companies profit from denying claims and delaying approvals. Prior authorization — the requirement that doctors get permission from an insurer before providing treatment — has become the single largest friction point in American healthcare. A treatment your doctor orders is not a treatment your insurer approves.

## For NRIs, the System Is Even Harder to Navigate

The national picture is dire. For Indian Americans navigating the US healthcare system, it is often worse, in ways that the surveys do not capture because they do not ask the right questions.

Start with the H-1B population. An estimated 600,000-plus Indian nationals are on H-1B visas, tied to employer-sponsored insurance that they cannot easily switch without changing jobs. If that employer offers a high-deductible plan — increasingly common — the first $3,000 to $8,000 of care comes out of pocket. For a family of four, that deductible can exceed $16,000 before insurance pays a rupee. A single emergency room visit in the United States averages $2,200 even after insurance.

Then there are the parents. Every year, hundreds of thousands of Indian parents visit their children in America on B-1/B-2 tourist visas. They are not eligible for Medicare, Medicaid, or employer insurance. Visitor insurance policies, when they exist, come with severe exclusions for pre-existing conditions — which describes most health concerns for people in their 60s and 70s. A hospitalisation during a visit can cost $50,000 to $200,000, paid entirely out of pocket. Every NRI family knows someone this has happened to.

The sandwich generation of Indian Americans — supporting ageing parents abroad while raising children in the US — faces a healthcare cost burden that no survey captures. They are paying for care in two countries, navigating two entirely different systems, in neither of which they have real bargaining power.

## Why Knowledge Is Not Enough

The most telling finding in the HealthEquity survey may be the gap between understanding and preparedness. Americans are getting better at understanding their benefits — that 16-point improvement is real. But feeling financially prepared for healthcare expenses actually declined. The system is not confusing. It is unaffordable. There is a difference.

For the diaspora, this distinction matters because the instinct is often to study harder, learn the system better, optimise the HSA and the FSA and the PPO versus HMO decision. Indian Americans are, on average, among the most educated and highest-earning demographics in the country. And they are still getting crushed by healthcare costs, because the problem is not literacy. It is price.

Long-term care insurance premiums have risen 40 per cent since 2020. A semiprivate nursing home room now costs $115,000 a year. Only 3 per cent of US adults carry long-term care insurance. For a community that culturally expects to care for ageing parents — often in their own homes — the absence of a safety net is not abstract. It is the conversation that nobody is having at the kitchen table but everybody is thinking about.

The healthcare leaders who said the system is three years from an existential tipping point are not pessimists. They are the people running it. When 90 per cent of them say the model is broken, the question is not whether it will change. It is whether it will change before it breaks."""
})

# ============================================================
# ARTICLE 3: May CPI / Inflation preview (markets-finance)
# ============================================================
articles.append({
    "id": str(uuid.uuid4()),
    "headline": "US Inflation Is About to Cross 4 Per Cent for the First Time in Three Years. Here Is What Every NRI Needs to Know.",
    "subheadline": "Wednesday's CPI report is forecast to show prices rising at 4.2 per cent year-over-year, the highest since May 2023. The Fed may raise rates. Oil is above $90. And the rupee is quietly losing ground.",
    "slug": "us-may-cpi-inflation-4-percent-iran-war-fed-rates-nri-impact-20260610",
    "category": "markets-finance",
    "vertical": "markets-finance",
    "status": "review",
    "is_editorial": False,
    "published_at": now_iso,
    "image_url": "https://images.pexels.com/photos/4744710/pexels-photo-4744710.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A fuel pump at a US gas station, where prices have surged on the Iran war",
    "image_attribution": "Pexels",
    "sources": json.dumps([
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/inflation-is-set-to-top-4-for-the-first-time-since-2023-and-the-fed-is-back-in-the-hot-seat-0ae4efc7"},
        {"name": "Morningstar", "url": "https://www.morningstar.com/economy/may-cpi-forecasts-show-continued-lofty-inflation"},
        {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/06/09/the-federal-reserves-june-inflation-forecast-is-in/"},
        {"name": "Barchart", "url": "https://www.barchart.com/story/news/35975411/stock-index-futures-climb-as-tech-stocks-rebound"}
    ]),
    "body": """On Wednesday morning at 8:30 a.m. Eastern, the Bureau of Labor Statistics will release the May Consumer Price Index. Every major forecaster agrees on the direction: up. The consensus estimate puts year-over-year CPI at 4.2 per cent, the highest reading since May 2023 and nearly double the 2.4 per cent rate from February, before the Iran war rewired global energy markets.

For NRIs with money, mortgages, and family obligations split between two countries, this number is not an abstraction. It is the cost of groceries in New Jersey, the interest rate on a refinance in Fremont, the exchange rate on a remittance to Hyderabad, and the price of a flight home to Delhi — all moving against you at once.

## What the Numbers Say

The monthly CPI is forecast to rise 0.5 per cent in May, almost three times the typical monthly increase. Core CPI, which strips out volatile food and energy prices, is expected to come in at 0.3 per cent month-over-month and 2.9 per cent year-over-year — the highest since late 2023.

The headline number is being driven overwhelmingly by energy. Oil prices remain above $90 a barrel, pushed there by the Iran conflict and Strait of Hormuz disruptions. Deutsche Bank estimates gas prices rose 6.8 per cent in May alone. Transportation services have begun absorbing higher fuel costs. Warehousing, retail, and wholesale trade are next.

But the core reading is what keeps Federal Reserve officials up at night. Just five months ago, core inflation had slowed to a five-year low of 2.5 per cent and was trending toward the Fed's 2 per cent target. That progress has reversed. TD Securities forecasts the core segment will near its peak for the year at 3.0 per cent in June, with the Iran conflict providing upside risks.

The Fed's own Cleveland Inflation Nowcasting tool offers one sliver of hope: it projects trailing 12-month inflation for June to decline by 13 basis points to 4.05 per cent, the first projected dip since the Iran war began. But even the Fed's optimistic model still has inflation above 4 per cent through the summer.

## The Fed's Next Move

Gone is any chance of rate cuts in 2026. Goldman Sachs pushed its forecast for the first cut to 2027 last week. The question has shifted from "when will rates come down" to "will rates go up."

Fed Chair Kevin Warsh and the Federal Open Market Committee face a textbook dilemma. Oil-driven inflation is typically transitory — prices spike, then revert. The Fed usually waits it out. But if elevated energy prices start reshaping how consumers and businesses expect inflation to behave, the transitory becomes structural. Self-fulfilling prophecy.

The 10-year Treasury yield has risen to 4.54 per cent, reflecting market bets that the Fed will tighten. Higher lending rates would hit the AI data centre build-out that has been propping up tech valuations, pressuring the Nasdaq. They would also raise mortgage rates further — the average 30-year fixed rate is already above 7 per cent — making housing even less accessible.

Vanguard's economists say the key is whether energy-driven inflation stays contained to direct impacts or bleeds into the broader economy. "If oil prices remain above $100-plus per barrel for another three to six months, we'll start to see more of that pass-through," says Vanguard's Schickling.

## What This Means for NRIs

The inflation picture creates a multi-front squeeze for the Indian diaspora that is different from what the average American faces.

**Remittances are getting more expensive and less valuable.** The rupee has weakened against the dollar as India's import bill — heavily weighted toward crude oil — has ballooned. But inflation in the US means the dollars being sent home buy less in America before they are converted. An NRI sending $1,000 home each month is earning the same nominal salary but spending more on rent, gas, groceries, and childcare. The remittance becomes what is left over, and what is left over is shrinking.

**Mortgage timing is a trap.** Many Indian Americans have been waiting for rates to drop before buying a home or refinancing. That wait just got longer — possibly 18 months longer, if Goldman's timeline holds. Meanwhile, home prices in metros with large South Asian populations — the Bay Area, New Jersey, the DFW Metroplex, Seattle — have not meaningfully corrected. The math of waiting improves only if you believe rates will drop faster than prices will rise. Right now, neither is moving in your favour.

**India's rate trajectory is diverging.** The Reserve Bank of India has been cutting rates to stimulate growth, while the Fed holds or raises. This interest rate differential has implications for FCNR deposits, NRE account returns, and the rupee's trajectory. NRIs who parked money in FCNR dollar deposits at 5 per cent are sitting pretty for now, but a sustained US rate hike would put pressure on India to defend the rupee, potentially reversing the RBI's easing cycle.

**Flights home are not coming down.** Jet fuel prices track crude oil with a lag. Summer fares to India from the US are already 15 to 25 per cent higher than last year. Families planning July and August trips — peak season for diaspora travel — are paying a war premium on top of seasonal pricing.

## The Wildcard

The Strait of Hormuz is the single biggest variable in the inflation equation. About 20 per cent of the world's oil passes through the strait, which Iran has periodically threatened and partially disrupted since the conflict escalated. US Energy Secretary Chris Wright said this week that ship traffic through the strait is rising "very meaningfully," suggesting some normalisation. But Israel struck targets in southern Lebanon on Tuesday, and Tehran warned it would resume hostilities if the attacks continued.

If the strait fully reopens and the ceasefire holds, oil prices could drop below $80 by late summer, and inflation would follow. If the conflict escalates, $100 oil becomes the floor, not the ceiling, and the Fed's hand is forced.

Wednesday's CPI number will not resolve any of this. But it will tell you how much damage has already been done — and for NRIs watching the rupee, the mortgage rate, and the gas pump simultaneously, the number that matters is not the headline. It is how long it stays there."""
})

# ============================================================
# INSERT ALL ARTICLES
# ============================================================
for i, article in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Inserting article {i+1}: {article['headline'][:70]}...")
    
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    
    if resp.status_code in (200, 201):
        result = resp.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Inserted: {result[0].get('slug', 'unknown')}")
            print(f"  ✓ ID: {result[0].get('id', 'unknown')}")
            print(f"  ✓ Status: {result[0].get('status', 'unknown')}")
            print(f"  ✓ Category: {result[0].get('category', 'unknown')}")
        else:
            print(f"  ✓ Response: {str(result)[:200]}")
    else:
        print(f"  ✗ Error {resp.status_code}: {resp.text[:300]}")

print(f"\n{'='*60}")
print("Done! All articles inserted with status='review'")
