#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-15 14:00 UTC batch."""

import json, os
from datetime import datetime, timezone
import requests

env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

def insert_article(article):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=headers, json=article, timeout=30
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        print(f"  \u2713 Inserted: {article['slug']} (id: {data[0]['id'] if data else 'ok'})")
        return True
    else:
        print(f"  \u2717 FAILED: {article['slug']} \u2014 {resp.status_code}: {resp.text[:300]}")
        return False

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
articles = []

# ============================================================
# ARTICLE 1: No safe level of alcohol (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Nightly Drink Was Never Harmless. A Review of 7,200 Studies Just Put a Number on the Risk.",
    "subheadline": "Research published in the Journal of Studies on Alcohol and Drugs finds the safest amount of alcohol is none \u2014 and that the old \u2018two drinks a day\u2019 limit carries a 1-in-25 lifetime risk of death. For a diaspora where social drinking is rising fastest among the young and the affluent, the math is worth reading carefully.",
    "slug": "no-safe-level-alcohol-study-7200-reviews-one-in-25-risk-south-asian-diaspora-20260615",
    "category": "lifestyle-health",
    "vertical": "health-science",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6449866/pexels-photo-6449866.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Red wine being poured into a glass, the kind of nightly drink a new study says carries more risk than long assumed",
    "image_attribution": "Pexels",
    "diaspora_angle": "Alcohol consumption is climbing fastest among young, affluent, and urban Indians and second-generation diaspora professionals, even as the community already carries elevated liver-disease and cancer susceptibility \u2014 making a clear-eyed read of the new dose-risk math especially relevant to NRI families.",
    "sources": json.dumps([
        {"name": "Journal of Studies on Alcohol and Drugs", "url": "https://www.jsad.com/"},
        {"name": "USA Today", "url": "https://www.usatoday.com/story/news/health/2026/06/10/alcohol-risk-study-one-drink-day/"},
        {"name": "Fox News Health", "url": "https://www.foxnews.com/health/nightly-glass-wine-may-not-as-harmless-many-people-think-study-suggests"},
        {"name": "World Health Organization", "url": "https://www.who.int/europe/news/item/04-01-2023-no-level-of-alcohol-consumption-is-safe-for-our-health"}
    ]),
    "body": """For decades, the comforting story about alcohol was that a little was good for you. A glass of red wine with dinner was practically a health prescription, backed by studies that showed moderate drinkers outliving teetotallers. That story is now collapsing, and a sweeping new analysis has put a hard number on what it is being replaced with.

Research published this month in the Journal of Studies on Alcohol and Drugs reviewed more than 7,200 studies on alcohol-related disease and reached a blunt conclusion: the safest amount of alcohol to drink is none. If adults do choose to drink, the authors recommend a ceiling of one drink a day \u2014 roughly seven a week \u2014 and even that, they stress, is not free of risk.

## Putting a Number on "Moderate"

What makes this study land harder than the usual health warning is its arithmetic. The researchers translated drinking habits into lifetime risk of death, and the numbers escalate quickly. Seven drinks a week \u2014 the one-a-day ceiling \u2014 carries a roughly 1-in-1,000 lifetime risk of dying from an alcohol-related cause. Add just two more drinks, for a total of nine a week, and that risk jumps tenfold, to 1 in 100.

Stick to the old federal guideline of two drinks a day, or 14 a week, and the lifetime risk of death surges to 1 in 25. To put that in perspective, that is a level of risk most people would never knowingly accept from any other everyday habit. And these rates, the authors found, were fairly consistent across men and women, with only small variation.

"Even low levels of alcohol use come with health risks," said lead author Kevin Shield of the University of Toronto, "and that risk continues to increase the more someone drinks." His co-author, Columbia University epidemiologist Katherine Keyes, was equally direct: "No protective effect of drinking was observed even at low levels."

## The Myth of the Healthy Glass of Wine

The single most consequential finding is what it demolishes. The long-held belief that a bit of red wine protects the heart was, the study concludes, a statistical mirage. Older research compared people by how much they drank rather than randomly assigning them, which meant the supposedly healthy "moderate drinkers" were often simply healthier and wealthier to begin with. Once researchers adjusted for income, education, and access to healthcare, the protective glow around moderate drinking faded.

This echoes the World Health Organization's 2023 statement that no level of alcohol consumption is safe, and that risk "starts from the first drop." Alcohol is a confirmed carcinogen, and there is no threshold below which its cancer-causing effects switch off. Liver disease, stroke, hypertension, and several cancers all rise with consumption, with no safe floor.

## Why the Diaspora Should Pay Closer Attention

For Indian families in the United States, Britain, and Canada, this is not a distant debate. Traditionally, large parts of the community drank little or not at all, for cultural and religious reasons. But that is changing fast. Alcohol consumption in India and among younger diaspora professionals is rising more quickly than in most populations, particularly among affluent, urban, and second-generation drinkers who have absorbed Western social-drinking norms \u2014 the after-work cocktail, the wedding open bar, the wine-with-dinner habit.

That shift collides with biology. South Asians already carry elevated baseline risks for the very conditions alcohol aggravates: fatty liver disease, type 2 diabetes, and cardiovascular illness that strikes a decade earlier than in other groups. A population starting from a higher disease baseline has less margin to absorb an additional carcinogen, and the assumption that "a couple of drinks is fine" was built on data that did not include them.

## What to Actually Do With This

The study's authors are careful to note its limits. It is an observational analysis built on statistical modelling of national health databases, not a controlled trial, and Fox News medical analyst Dr. Marc Siegel cautioned that it draws on Canadian methods applied to U.S. census data. It cannot prove that any single drink caused any single death.

But the direction of the evidence is now overwhelming and consistent across the WHO, the Lancet, and this latest review. The practical takeaway is not abstinence by decree but informed choice: there is no health benefit to chase at the bottom of a glass, the risk rises steadily with every additional drink, and the old "two a day is fine" guidance was generous to a fault. For diaspora households weighing how to fold drinking into celebrations and daily life, the cheapest insurance policy turns out to be the simplest \u2014 less is genuinely better, and none is best."""
})

# ============================================================
# ARTICLE 2: MIND diet & brain structure (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Decade of Brain Scans Shows the MIND Diet Slows Ageing in the Brain. The Indian Plate Is Halfway There.",
    "subheadline": "A Framingham Heart Study analysis published in the Journal of Neurology, Neurosurgery & Psychiatry tracked brain structure over ten years and found that people who stuck closest to the MIND diet had measurably younger-looking brains. Much of what it rewards \u2014 leafy greens, beans, whole grains \u2014 already lives in the diaspora kitchen.",
    "slug": "mind-diet-brain-structure-decade-framingham-study-south-asian-diet-overlap-20260615",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4887993/pexels-photo-4887993.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A fresh salad of leafy greens and vegetables, the dietary foundation the MIND diet links to slower brain ageing",
    "image_attribution": "Pexels",
    "diaspora_angle": "The MIND diet's brain-protective core \u2014 leafy greens, legumes, whole grains, and nuts \u2014 overlaps heavily with traditional Indian regional cooking, giving diaspora families a built-in advantage against cognitive decline if they resist the drift toward fried and ultraprocessed convenience food.",
    "sources": json.dumps([
        {"name": "Journal of Neurology, Neurosurgery & Psychiatry", "url": "https://jnnp.bmj.com/content/97/6/505"},
        {"name": "PubMed", "url": "https://pubmed.ncbi.nlm.nih.gov/41844283/"},
        {"name": "Framingham Heart Study", "url": "https://www.framinghamheartstudy.org/"}
    ]),
    "body": """The brain shrinks as it ages. Grey matter thins, the fluid-filled spaces inside it widen, and small areas of white-matter damage accumulate \u2014 changes that quietly precede memory loss and dementia. The open question has always been whether anything we do at the dinner table can slow that decline. A new long-term study offers one of the clearest answers yet, and it is encouraging news for the way Indian families have eaten for generations.

Researchers drawing on the Framingham Heart Study \u2014 one of the longest-running health investigations in the world \u2014 tracked the brain structure of participants over a full decade and matched it against how closely each person followed the MIND diet. Their findings, published in the Journal of Neurology, Neurosurgery & Psychiatry, were straightforward: the people who adhered most faithfully to the diet showed slower structural ageing in the brain, with healthier tissue volumes a decade on.

## What the MIND Diet Actually Is

The MIND diet \u2014 short for Mediterranean-DASH Intervention for Neurodegenerative Delay \u2014 is a hybrid built specifically to protect the brain. It borrows from the Mediterranean diet and the blood-pressure-lowering DASH diet, then narrows the focus to foods that research has tied to cognitive health.

Its "eat more" list is short and specific: leafy green vegetables, other vegetables, berries, nuts, beans and legumes, whole grains, fish, poultry, and olive oil. Its "eat less" list is equally clear: red meat, butter and margarine, cheese, fried food, pastries, and sweets. The diet rewards consistency rather than perfection \u2014 a daily serving of greens and a handful of nuts matters more than any single heroic meal.

Crucially, this latest study did not rely on memory tests alone, which can be noisy and subjective. It used repeated brain imaging over ten years, giving researchers a physical, structural readout of ageing rather than a questionnaire score. That makes the association between diet and a more youthful brain harder to dismiss.

## Where the Indian Plate Already Wins

For the diaspora, the striking thing about the MIND diet's grocery list is how much of it is already standard in a traditional Indian kitchen. Leafy greens are a daily staple \u2014 palak, methi, sarson, and a dozen regional saags. Legumes are the backbone of the cuisine: dal, rajma, chana, and sambar deliver exactly the beans the diet prioritises. Whole grains appear as bajra, jowar, ragi, and brown rice. Turmeric, ginger, and other spices add anti-inflammatory compounds the MIND diet's designers never even scored.

In other words, a household cooking the way a grandmother in Maharashtra or Tamil Nadu cooked is already hitting several of the diet's targets without trying. That is a genuine head start, and it helps explain why first-generation immigrants often arrive in remarkably good metabolic shape.

## The Catch: Drift and Frying

The advantage erodes fast, however, and the MIND diet's "eat less" column is where diaspora habits get into trouble. Indian cooking can be heavy on ghee, deep-frying, and refined-flour treats \u2014 the samosas, pooris, jalebis, and mithai that cluster around every festival and family gathering. And the second-generation drift toward Western convenience food, takeout, and ultraprocessed snacks pushes households straight into the categories the diet warns against.

The fix is not to abandon the cuisine but to tilt it. Steaming or sauteing greens instead of frying them, leaning on dals and vegetables as the centre of the plate rather than the side, swapping refined maida for whole grains, and treating fried and sugary items as genuine occasions rather than daily fare. None of this requires adopting an unfamiliar Mediterranean menu \u2014 it largely means returning to the everyday, less-celebratory version of Indian home cooking.

## The Bigger Picture

This is one observational study, and it shows association rather than proof that the diet directly caused the slower brain ageing. People who follow the MIND diet may also exercise more, sleep better, or have other advantages the analysis could not fully strip out. The authors themselves frame it as adding to a body of evidence rather than settling the question.

But it joins a growing stack of research pointing the same way: what protects the heart tends to protect the brain, and the protection is cumulative across decades rather than something you can cram late in life. For diaspora families watching aging parents and thinking about their own cognitive future, the message is unusually actionable. The most powerful brain-protecting diet on the menu is not exotic or expensive \u2014 it is, in large part, the plate their own kitchens already know how to make."""
})

# ============================================================
# ARTICLE 3: India WPI 9.68% (markets-finance)
# ============================================================
articles.append({
    "headline": "India's Wholesale Inflation Just Hit a Six-Month High of 9.68%. Why the RBI Is Not Panicking \u2014 and What It Means for NRIs.",
    "subheadline": "May wholesale price inflation came in far above forecasts at 9.68 per cent, driven by a 61 per cent surge in petroleum and gas prices from the Middle East energy shock. Yet retail inflation sits below 4 per cent and the rupee is rallying \u2014 a divergence diaspora investors and remittance senders need to understand.",
    "slug": "india-wpi-wholesale-inflation-968-may-2026-rbi-rupee-nri-remittance-impact-20260615",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/5476028/pexels-photo-5476028.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Indian rupee notes and coins, as wholesale inflation climbed to a six-month high in May",
    "image_attribution": "Pexels",
    "diaspora_angle": "The gap between soaring wholesale prices and tame retail inflation, combined with a rallying rupee, directly shapes how far NRI remittances stretch and whether the Reserve Bank moves on rates \u2014 decisions that affect every diaspora family sending money home or invested in Indian assets.",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-may-wholesale-price-inflation-rises-968-2026-06-15/"},
        {"name": "FXStreet", "url": "https://www.fxstreet.com/news/indias-wholesale-price-index-inflation-rises-to-968-yoy-in-may"},
        {"name": "Press Information Bureau, Government of India", "url": "https://pib.gov.in/"}
    ]),
    "body": """India's factory-gate prices are climbing at their fastest pace in six months, and the headline number released on Monday was startling. Wholesale price inflation hit 9.68 per cent year-on-year in May, government data showed \u2014 well above the 9.05 per cent economists had forecast, and a sharp jump from 8.26 per cent in April. It is the highest reading in six months under the government's newly revised price series.

The driver is no mystery. The energy shock from the conflict in the Middle East has rippled straight into India's wholesale basket. Fuel and power prices jumped 30.33 per cent year-on-year in May, up from 24.89 per cent in April, while petroleum and natural gas prices alone soared 61.51 per cent. Crude prices have risen roughly 27 per cent since hostilities broke out in late February, forcing state-run oil marketers to raise retail fuel prices four times during the month.

## The Number That Looks Scarier Than It Is

A near-10-per-cent inflation print would normally send markets into a defensive crouch. Yet the response has been notably calm, and the reason lies in a crucial distinction between two different inflation gauges.

Wholesale inflation \u2014 the WPI \u2014 carries a heavy weighting toward fuel and industrial commodities, which is exactly why it spiked. But India's central bank does not target the WPI. It targets retail inflation, the consumer price index, which measures the prices households actually pay and is dominated by food. And that number tells a far gentler story: retail inflation was just 3.93 per cent in May, comfortably below the Reserve Bank of India's 4 per cent target and well inside its 2-to-6 per cent tolerance band.

That divergence \u2014 wholesale prices running hot while consumer prices stay tame \u2014 is why the RBI held rates steady at its June meeting and is signalling patience. Policymakers want to see whether the fuel shock feeds through into broader consumer prices, the so-called second-round effect, before tightening. "The recent cooling in global energy and commodity prices after the easing of tensions in West Asia is expected to provide respite to the WPI inflation print for June 2026," noted Rahul Agrawal, principal economist at rating agency ICRA.

## The Iran Wildcard Changes the Math

The timing of the data release could hardly be more pointed. Even as the May numbers landed, the news that mattered more was coming from the other direction. A preliminary framework between the United States and Iran to end their war, halt the U.S. blockade, and reopen the Strait of Hormuz sent Brent crude tumbling more than 5 per cent to around $83 a barrel on Monday \u2014 its lowest level since March.

For the world's third-largest oil importer, which buys nearly 90 per cent of its crude from abroad, that is the single most important variable. Cheaper oil eases the pressure on inflation, on the rupee, and on the trade deficit all at once. If crude stays anchored near $80, economists expect the wholesale inflation surge to reverse in the coming months, and several have already upgraded their forecasts for India's balance of payments from a large deficit toward a small surplus.

## What This Means for the Diaspora

For non-resident Indians, three threads tie together here, and they pull in a favourable direction for once.

First, the rupee. After sliding to a record low near 97 per dollar last month and shedding about 6 per cent this year, the currency has staged a sharp turn, climbing to a five-week high around 94.5 on the back of the oil crash and the RBI's recent measures to attract dollar inflows. For NRIs, a stronger rupee is a double-edged signal: money sent home buys fewer rupees, so remittances stretch less far, but Indian assets held in rupees gain in dollar terms and the case for India's macro stability strengthens.

Second, remittance timing. Diaspora families who send money home regularly have watched the rupee's slide make their dollars and pounds go further all year. That window is now narrowing as the currency recovers \u2014 a consideration for anyone weighing a large transfer for a wedding, property purchase, or family support.

Third, the policy path. The combination of cooling oil, a recovering rupee, and sub-4 per cent retail inflation gives the RBI room to stay on hold rather than hike, which supports both Indian bonds and equities. The week ahead will test the picture, with the U.S. Federal Reserve's decision on June 17 \u2014 the first under new Chair Kevin Warsh \u2014 alongside the Bank of Japan and Bank of England meetings, any of which could move global flows.

The takeaway for diaspora investors and savers is to look past the alarming 9.68 per cent headline. It is a backward-looking snapshot of an energy shock that may already be fading. The forward-looking signals \u2014 cheaper oil, a firmer rupee, and a patient central bank \u2014 matter far more, and for now they are pointing the right way."""
})

# ============================================================
# INSERT
# ============================================================
print(f"\n{'='*60}\nInserting {len(articles)} articles at {now}\n{'='*60}\n")
success = 0
for a in articles:
    wc = len(a['body'].split())
    print(f"  [{a['category']}] {a['slug']} \u2014 {wc} words")
    if insert_article(a):
        success += 1
print(f"\n{'='*60}\nDone: {success}/{len(articles)} articles inserted\n{'='*60}")
