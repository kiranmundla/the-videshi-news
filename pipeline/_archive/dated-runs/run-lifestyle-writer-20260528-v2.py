#!/usr/bin/env python3
"""
Videshi Lifestyle-Health + Markets-Finance Writer — v2 (with topic creation)
"""

import json, os, subprocess, uuid, urllib.parse, time
import requests
from datetime import datetime, timezone

# ── ENV ──────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def fetch_pexels_image(query, fallback_query=None):
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            print(f"  ✓ Image valid: {ct}, {cl} bytes")
            return True
        r = requests.get(url, timeout=10, stream=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            return True
        print(f"  ✗ Image invalid: {ct}, {cl} bytes")
        return False
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
        return False


def sb_insert(table, row):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=row, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        return data[0] if isinstance(data, list) and data else data
    print(f"  ✗ INSERT {table} failed ({r.status_code}): {r.text[:300]}")
    return None


def create_topic(title, category, keywords):
    """Create a p2_topics row and return its id."""
    row = {
        "canonical_title": title,
        "category": category,
        "keywords": keywords,
        "status": "accepted",
        "score_total": 70,
        "score_recency": 80,
        "score_significance": 70,
        "score_diaspora": 75,
        "score_source_avail": 70,
        "signal_count": 3,
        "urgency": "normal",
    }
    result = sb_insert("p2_topics", row)
    if result:
        tid = result.get("id")
        print(f"  ✓ Topic created: {tid}")
        return tid
    return None


# ── ARTICLES DATA ────────────────────────────────────────────────────
now_iso = datetime.now(timezone.utc).isoformat()

articles = [
    {
        "topic_title": "UK Doctors Declare Social Media as Dangerous as Smoking for Children",
        "topic_category": "lifestyle-health",
        "topic_keywords": ["social media", "children", "smoking", "UK doctors", "mental health", "screen time", "Indian parents"],
        "headline": "Britain's Top Doctors Just Declared Social Media as Dangerous as Smoking for Children. Indian Diaspora Parents Raising Kids in the West Should Read the Fine Print.",
        "subheadline": "The Academy of Medical Royal Colleges — 23 institutions representing every branch of British medicine — issued its strongest warning yet. Here is what it means for your family.",
        "slug": "social-media-smoking-children-uk-doctors-indian-diaspora-parents-20260528",
        "category": "lifestyle-health",
        "sources": json.dumps([
            "https://www.reuters.com/legal/litigation/social-media-bad-children-smoking-british-doctors-say-2026-05-26/",
            "https://www.thetimes.com/uk/society/article/social-media-is-the-new-smoking-say-medical-leaders-20260527",
            "https://people.com/social-media-use-as-bad-for-young-people-as-smoking-claims-new-report-11738092"
        ]),
        "image_query": "teenager smartphone screen time",
        "image_fallback": "child using phone worried parent",
        "body": """Britain's most senior doctors have drawn a line that Indian parents abroad have been feeling in their bones for years: social media is now as dangerous to children as cigarettes once were.

The Academy of Medical Royal Colleges — representing all 23 royal medical colleges and faculties across the UK and Ireland — submitted its assessment to the British government's consultation on child safety online this week. The language was unusually blunt for an institution that typically communicates in measured clinical prose.

"It ranks alongside smoking and wearing seatbelts in cars as a unifying force for the medical profession," the Academy said. "There can be few issues which have united clinicians so resoundingly in recent years as the impact that unfettered exposure to tech and devices is currently having on children and young people's health."

## The Numbers Behind the Warning

More than half of 132 doctors surveyed by the Academy reported seeing at least one case of health harm related to technology and devices every single week. Over a third encountered such harm multiple times a week.

The harms documented were not abstract. They ranged from physical injuries — including ones caused by children replicating acts seen in extreme pornography — to deep mental health impacts from exposure to online violence, self-harm content, and algorithmically served material that no child went searching for.

Dr Emily Sehmer, a consultant child psychiatrist, put it plainly: "Mental health services are inundated with referrals for children with anxiety, low mood, inattention, sleep disorders, challenging behaviours, violence and toxic ideology as a direct result of time spent online."

## What Britain Plans to Do About It

The UK government is now actively consulting on restricting children's access to social media. Options on the table include an outright ban for under-16s — following Australia's lead in December 2025 — as well as curfews, app time limits, and curbs on what officials call "addictive design features."

Technology Secretary Liz Kendall left little room for ambiguity: "The question isn't whether we are going to act; we will, whether that is a ban on social media for the under-16s or restrictions on key features and functions."

Hundreds of British families are already testing social media bans and curfews in government-backed pilot programmes, measuring impact on children's sleep, family dynamics, and academic performance.

## Why This Hits Differently for Indian Families Abroad

For the roughly four million people of Indian origin living in the UK, and the five million in the United States, this is not just a policy debate. It is a parenting crisis playing out in real time across two cultural operating systems.

Indian parenting traditions emphasise academic achievement, family cohesion, and respect for elders — values that sit in direct tension with the attention economy designed by Silicon Valley. The algorithmic feed does not care about your family's values. It cares about engagement, and engagement is maximised by content that provokes anxiety, outrage, or compulsive comparison.

South Asian children in Western countries face a specific version of this problem. They are navigating identity formation across cultures while being exposed to content streams that amplify body image anxiety, social comparison, and cultural dislocation. The manosphere — a network of online influencers promoting toxic masculinity — has been documented as particularly harmful to boys of colour, including South Asian boys.

Research from the UK's National Health Service shows that South Asian teenagers are significantly less likely to seek mental health support than their white British peers, even when experiencing equivalent levels of distress. The stigma around mental health in Indian families means that the damage from social media often compounds silently.

## What You Can Do Now

The Academy's recommendation is not to wait for legislation. Doctors are urging families to act immediately.

Screen-free bedrooms and screen-free mealtimes are the two interventions with the strongest evidence base. The correlation between smartphone presence in bedrooms and disrupted adolescent sleep is now as well-established as the link between passive smoking and childhood asthma.

For Indian families, the conversation requires cultural specificity. The cousin group chat on WhatsApp, the family TikTok sharing, the Instagram comparison with peers — these are not generic Western parenting concerns. They are culturally embedded behaviours that require culturally informed boundaries.

The Academy's comparison to smoking is not rhetorical hyperbole. It took decades for the medical establishment to move from suspecting that cigarettes were harmful to declaring it unequivocally. The doctors are saying they do not want to repeat that delay with social media.

The question for every Indian parent raising children in the West is no longer whether social media is harmful. It is what you are going to do about it before the legislation catches up.

*The UK government's consultation on protecting children online closed on 27 May 2026. Australia banned social media for under-16s in December 2025. No equivalent federal legislation exists in the United States.*"""
    },

    {
        "topic_title": "Urine Test Detects Autism in Children With 90% Accuracy via Gut Metabolites",
        "topic_category": "lifestyle-health",
        "topic_keywords": ["autism", "urine test", "gut microbiome", "children", "diagnosis", "metabolites", "Arizona State"],
        "headline": "A Simple Urine Test Can Now Detect Autism in Children With 90 Per Cent Accuracy. The Gut Bacteria Tell the Story Before Behaviour Does.",
        "subheadline": "Arizona State University researchers found that 17 microbial metabolites in a child's urine can flag autism risk as early as age two. For Indian families, where diagnostic hesitancy runs deep, a biology-based test could change everything.",
        "slug": "urine-test-autism-90-percent-gut-bacteria-metabolites-indian-families-20260528",
        "category": "lifestyle-health",
        "sources": json.dumps([
            "https://nypost.com/2026/05/27/health/new-urine-test-could-diagnose-autism-in-children-study/",
            "https://www.nature.com/articles/s41380-026-02925-3",
            "https://medicalxpress.com/news/2026-05-urine-autism-children-ages.html"
        ]),
        "image_query": "child medical test laboratory diagnosis",
        "image_fallback": "pediatric healthcare screening",
        "body": """The future of autism diagnosis may not involve a clinician watching your child play with blocks. It may involve a urine sample.

Researchers at Arizona State University have developed a screening tool that analyses 17 microbial metabolites — molecules produced by bacteria in the gut — to identify children with autism spectrum disorder. The test, published this week in the journal Molecular Psychiatry, showed 90 per cent sensitivity and 100 per cent specificity in trials. It correctly flagged nine out of ten children with autism and misidentified none.

## How It Works

The study examined urine samples from 99 children between the ages of two and eleven. Fifty-two had been diagnosed with autism; 47 had not.

The researchers built a classification system called the Microbially-Derived Metabolite System, or MDM. It scores the number of metabolites in a child's urine that exceed the typical range. Nearly all the children with autism had at least one metabolite level that surpassed the highest observed in the group without the disorder.

The most striking finding was the magnitude of the difference. Some metabolites were elevated by a factor of 1,000 in children with autism — not a subtle variation, but a biological signal loud enough to be unmistakable.

"What's really striking about the bacteria is that they make metabolites that are basically altered versions of serotonin and dopamine," said James Adams, the corresponding study author. Both neurotransmitters regulate mood, cognition, and memory, which could "explain many of the symptoms and co-occurring symptoms in children with autism — their social communication, anxiety, depression and attention."

The findings align with more than 40 previous studies that documented elevated gut microbiome metabolites in children with autism.

## Why This Matters for Indian Families

Autism diagnoses in the United States have risen 175 per cent between 2011 and 2022. The CDC now estimates that roughly 1 in 36 children in the US is on the autism spectrum. In India, the estimated prevalence is 1 in 100 — though experts widely believe this is a severe undercount driven by limited screening infrastructure and persistent stigma.

For Indian families — whether in India or abroad — the diagnostic journey for autism is often painfully slow and culturally fraught. Current diagnostic methods rely on behavioural observation, typically by specialists with long waiting lists. Many Indian parents delay seeking evaluation because of social stigma, family pressure, or a belief that the child will "grow out of it."

A biology-based test changes the framing entirely.

"Sometimes diagnostic hesitancy happens because parents feel like they're not good enough parents and they're being judged," said Christina Flynn, the study's first author. "But that's not the case because if we can detect it in urine, it's a biology-based condition. Hopefully that will prevent any hesitancy on parents' parts to seek treatment and seek it as early as possible."

This reframing is especially powerful in South Asian contexts. When autism can be identified through a laboratory test rather than a clinical judgement about behaviour, it removes the implication that parenting or family environment is at fault. It becomes a medical finding, not a social verdict.

## The Gut-Brain Connection

The research points to a distinct biological subtype the researchers are calling ASD-MDM — autism spectrum disorder associated with microbially-derived metabolites — which they estimate encompasses roughly 90 per cent of autism cases.

The gut-brain axis has been a growing area of scientific interest for over a decade. The idea that the trillions of bacteria living in the human digestive system can influence brain development and behaviour is no longer speculative. This study adds the most direct diagnostic evidence yet.

For Indian families, there is an additional layer of relevance. Indian diets — particularly vegetarian diets rich in legumes, fermented foods, and spices — shape the gut microbiome in ways that differ significantly from Western diets. Whether these dietary patterns interact with the metabolites flagged in this study is an open question that future research will need to address.

## What Comes Next

Further testing is underway to validate the MDM System on a larger and more diverse sample. The researchers are clear that this is a screening tool, not a replacement for comprehensive clinical evaluation. A high MDM score would flag a child for further assessment, potentially cutting months or years off the diagnostic timeline.

For NRI families navigating the American healthcare system, where autism evaluations can involve six-month waiting lists and thousands of dollars in out-of-pocket costs, a urine-based preliminary screen could be transformative.

The test also opens the door to targeted interventions. If the gut microbiome is driving a measurable portion of autism-related symptoms, then microbiome-directed therapies — probiotics, dietary modifications, or faecal microbiota transplantation — could become meaningful treatment pathways rather than fringe alternatives.

The science is moving faster than the conversation in most Indian families. A generation of parents who grew up in a culture that rarely named autism are now raising children in a country that diagnoses it at record rates. A simple urine test will not resolve the cultural complexity, but it may give families the one thing that has been hardest to find: an early, objective answer.

*The study was published in Molecular Psychiatry on 27 May 2026. The research was conducted at Arizona State University's Biodesign Institute.*"""
    },

    {
        "topic_title": "India Becomes a Stock-Pickers' Market as FPI Exodus and Oil Volatility Reshape June Outlook",
        "topic_category": "markets-finance",
        "topic_keywords": ["India", "Nifty", "stock market", "FPI", "oil", "metals", "pharma", "IT", "June 2026", "NRI investors"],
        "headline": "India Is About to Become a Stock-Pickers' Market. If You Have Been Sitting on the Sidelines, June May Be Your Entry Window.",
        "subheadline": "The Nifty ended the May series flat at 23,914. Foreign investors are still selling. Domestic money is rotating into specific sectors. Two brokerages say the game has changed — and here is where they see the opportunities.",
        "slug": "india-stock-pickers-market-june-nri-sectors-metals-pharma-it-20260528",
        "category": "markets-finance",
        "sources": json.dumps([
            "https://www.reuters.com/world/india/india-track-become-stock-pickers-market-june-brokerages-say-2026-05-27/",
            "https://www.reuters.com/world/india/indian-shares-end-flat-hdfc-bank-offsets-rally-metal-stocks-2026-05-27/",
            "https://www.reuters.com/world/india/india-stocks-set-first-yearly-drop-over-decade-foreign-investors-leave-2026-05-27/"
        ]),
        "image_query": "Indian stock market trading Bombay",
        "image_fallback": "stock exchange trading floor",
        "body": """The Indian stock market is sending a very specific signal right now: the index is going nowhere, but the money inside it is moving fast.

The Nifty 50 ended the May derivatives series barely changed at 23,913.7 points. For a headline number, that looks like stagnation. But underneath it, a rotation is underway that two major brokerages — Systematix and Axis Direct — say is creating the best stock-picking environment India has seen in months.

## The Setup

The May series marked what Systematix calls a shift in "market character." The recovery that began in April was initially driven by short covering — traders closing out bearish bets rather than making new bullish ones. By the end of May, the market transitioned to fresh positioning near higher levels, with the blue-chip index stalling just below its 50-day moving average.

This is the classic precondition for a stock-pickers' market: the broad index goes sideways, but individual sectors and stocks move sharply based on their own fundamentals.

Market-wide rollover — the percentage of futures positions carried forward from one series to the next — stood at 94.2 per cent in May, beating both three-month and six-month averages. That signals resilient participation despite the headline flatness. Notably, India's smaller and mid-cap stocks outperformed the Nifty during the latest series, a sign that domestic investors are hunting for value outside the blue-chip index.

## The Oil Factor

The single largest variable remains oil. Brent crude plunged 5.3 per cent to $94.29 on Wednesday after reports that a US-Iran peace deal could reopen the Strait of Hormuz within a month. Then it bounced 2.5 per cent on Thursday after fresh US strikes on Iranian drone installations near Bandar Abbas.

For India, which imports over 80 per cent of its crude, every dollar move in oil has a measurable impact on the current account deficit, the rupee, and corporate margins. The rupee is currently hovering around 95.68 to the dollar, with the Reserve Bank of India actively intervening through state-run bank dollar sales and forward swaps to prevent a breach above 96.

If the US-Iran deal materialises, it could shave 15 to 20 per cent off India's energy import bill within six months — a scenario that would be profoundly bullish for Indian equities. If it collapses, oil above $100 would push the Nifty toward the lower end of the projected 23,000 to 25,000 June range.

## Where the Money Is Going

The derivatives data reveals where institutional money is positioning for June.

**Metals.** Open interest data shows significant accumulation in metal stocks, driven by China's infrastructure stimulus and improving global demand. Indian steel and aluminium producers stand to benefit from both volume growth and margin expansion if raw material costs stabilise.

**Pharma.** The sector has been quietly building positions. Indian pharmaceutical companies benefit from a weakening rupee — their revenues are dollar-denominated while costs are largely in rupees. With the US generic drug market entering a new approval cycle, Indian pharma is in a structural sweet spot.

**Power.** India's electricity demand hit all-time highs during the 2026 heatwave, and the government's push to add renewable capacity is accelerating. Power sector stocks have seen sustained open-interest buildup across the May series.

**IT — The Wildcard.** Information technology stocks have the highest concentration of short positions of any sector. If those crowded shorts begin to unwind — triggered by a positive earnings surprise, a deal announcement, or simply a shift in sentiment — the resulting short-covering bounce could be sharp and fast. For NRI investors who work in tech and understand the sector's fundamentals, this is worth watching closely.

## The Foreign Investor Problem

Foreign portfolio investors have pulled $24.3 billion out of Indian equities so far in 2026, surpassing record annual outflows seen last year. A Reuters poll of 24 analysts projects the Nifty to end 2026 at 26,000 — roughly 8.7 per cent above current levels — which would still mark the index's first annual loss since 2015.

The domestic side tells a different story. Indian mutual fund inflows through systematic investment plans continue to set records, and local institutional money is increasingly willing to buy what foreign investors are selling. This divergence — foreign selling, domestic buying — is precisely what creates a stock-pickers' market rather than a broad-based rally.

## What NRI Investors Should Consider

For NRIs with rupee-denominated investments or those considering entry into Indian equities, the June setup offers a specific kind of opportunity.

**Dollar-cost averaging into Indian ETFs or mutual funds** remains the lowest-friction approach. The Nifty's projected 23,000 to 25,000 range means you are unlikely to catch a catastrophic entry point, but equally unlikely to time the bottom perfectly.

**Sector-specific bets** carry more risk but align with the data. Metals, pharma, and power are where the smart money is positioning. IT is the high-risk, high-reward contrarian play.

**Currency timing matters.** If you are converting dollars to rupees for investment, the current 95 to 96 range is historically weak for the rupee. A peace deal that brings oil below $85 could strengthen it to 90 to 92 within months, meaning your dollars buy more rupees now than they might later.

The Nifty may not make headlines in June. But the trades inside it will. For investors willing to do the work of picking individual sectors and stocks rather than riding the index, this is the market India has been waiting to become.

*Indian markets were closed on Thursday for a local holiday. The June derivatives series begins on Friday. Data sourced from Systematix, Axis Direct, and Reuters.*"""
    },
]


# ── PUBLISH ──────────────────────────────────────────────────────────

published = 0

for i, art in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Article {i+1}: {art['headline'][:80]}...")
    print(f"Category: {art['category']}")

    # 1. Create topic
    topic_id = create_topic(art["topic_title"], art["topic_category"], art["topic_keywords"])
    if not topic_id:
        print("  ✗ Failed to create topic, skipping article")
        continue

    # 2. Source image
    img_url = fetch_pexels_image(art["image_query"], art.get("image_fallback"))
    if img_url and not validate_image(img_url):
        img_url = fetch_pexels_image(art.get("image_fallback"))
        if img_url and not validate_image(img_url):
            img_url = None

    # 3. Insert article
    row = {
        "topic_id": topic_id,
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "category": art["category"],
        "body": art["body"],
        "sources": art["sources"],
        "status": "published",
        "published_at": now_iso,
    }

    if img_url:
        row["image_url"] = img_url
        row["image_attribution"] = "Pexels" if "pexels.com" in img_url else "Wikimedia Commons"

    result = sb_insert("p2_articles", row)
    if result:
        art_id = result.get("id")
        print(f"  ✓ Published: {art['slug']} (id: {art_id})")
        published += 1
    else:
        print(f"  ✗ FAILED to publish: {art['slug']}")

    time.sleep(1)

print(f"\n{'='*60}")
print(f"Done. Published {published}/{len(articles)} articles.")
