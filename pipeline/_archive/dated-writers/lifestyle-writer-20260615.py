#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-15 batch."""

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
# ARTICLE 1: Resistance training sweet spot (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Just 90 Minutes of Lifting a Week Cuts Death Risk. For South Asians, There Is No Cheaper Insurance Policy.",
    "subheadline": "A 147,000-person study spanning three decades, published in the British Journal of Sports Medicine, found the clearest survival benefit at 90 to 119 minutes of weekly resistance training \u2014 a finding that matters acutely for a community that loses muscle faster and earlier than almost any other.",
    "slug": "resistance-training-90-minutes-sweet-spot-mortality-south-asian-muscle-loss-20260615",
    "category": "lifestyle-health",
    "vertical": "health-science",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6815693/pexels-photo-6815693.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "An older couple working out with dumbbells, illustrating the survival benefits of regular resistance training",
    "image_attribution": "Pexels",
    "diaspora_angle": "South Asians carry less skeletal muscle and more visceral fat at any given weight, so the protective payoff from a modest weekly lifting habit is disproportionately large for the diaspora's aging parents and midlife professionals.",
    "sources": json.dumps([
        {"name": "British Journal of Sports Medicine", "url": "https://bjsm.bmj.com/"},
        {"name": "Fox News Health", "url": "https://foxnews.com/health/weekly-weightlifting-sweet-spot-may-linked-longer-life-study-finds"},
        {"name": "Inshorts", "url": "https://inshorts.com/en/news/weekly-strength-training-may-boost-longevity-and-brain-health"}
    ]),
    "body": """For years, the message about exercise and longevity was simple: walk more, raise your heart rate, do your cardio. Strength training was treated as an optional extra \u2014 something for bodybuilders, not for people trying to live longer. A sweeping new study has just complicated that picture, and the implications land hardest on the South Asian diaspora.

Research published this week in the British Journal of Sports Medicine followed more than 147,000 American adults across three large health studies spanning up to 30 years. More than 35,000 of those participants died during the study period, giving scientists an unusually rich dataset to ask a precise question: how much weightlifting actually moves the needle on staying alive?

## The Sweet Spot

The answer turned out to be surprisingly modest. The clearest benefit appeared at around 90 to 119 minutes of resistance training per week \u2014 roughly two gym sessions, or three shorter ones. People who hit that range had a 13 per cent lower risk of death from any cause, a 19 per cent lower risk of dying from heart disease, and a striking 27 per cent lower risk of death from neurological disease.

Crucially, more was not better. Beyond 120 minutes per week, the survival benefit flattened out. Even very small amounts mattered: just 30 to 59 minutes of resistance work per week was linked to a 12 per cent lower risk of cancer death. The findings held up even after researchers adjusted for age, smoking, diet quality, alcohol intake, family history, and aerobic activity.

The lowest death risk of all was found in people who combined moderate-to-high resistance training with higher levels of aerobic exercise \u2014 the two forms of movement working together rather than competing. The authors were careful to note that the study shows association, not direct cause, and that participants reported their own exercise habits, which can be imprecise. But the consistency across 147,000 people and three decades is hard to dismiss.

## Why This Hits South Asians Harder

For the Indian diaspora in the United States, Britain, and Canada, this is not an abstract longevity headline. South Asians carry a well-documented body-composition disadvantage: at any given body mass index, they tend to have less skeletal muscle and more visceral fat than white, Black, or East Asian populations. This "thin-fat" phenotype \u2014 normal weight on the scale, high fat and low muscle underneath \u2014 is a major driver of the community's elevated rates of type 2 diabetes and early heart disease.

Muscle is not just for strength. Skeletal muscle is the body's largest reservoir for glucose disposal; the more you have, the better your body manages blood sugar. Resistance training directly builds that reservoir. For a population genetically primed toward insulin resistance, the metabolic dividend from lifting weights is larger than it is for the average gym-goer.

Age compounds the problem. Sarcopenia \u2014 the progressive loss of muscle that begins in the 40s and accelerates after 60 \u2014 arrives functionally earlier in South Asians who start with a thinner muscle baseline. For the diaspora's aging parents, many of whom were never raised in a culture of recreational weight training, the gap between a sedentary old age and an independent one can come down to a couple of resistance sessions a week.

## What "90 Minutes" Actually Looks Like

The encouraging part of the data is how little is required. Ninety minutes spread across a week is two 45-minute sessions, or three half-hour ones. It does not require a barbell or a gym membership. Resistance bands, bodyweight squats, push-ups, and chair stands all count \u2014 a point reinforced by a separate Penn State study this month showing that just four minutes a day of four basic movements measurably improved fitness in adults over 65.

For multigenerational diaspora households, that opens a practical path. A parent doing band exercises in the living room, a teenager doing push-ups, a working professional fitting two short sessions around a desk job \u2014 none of it demands the hours that the cardio-centric fitness culture once implied. The biology rewards consistency over intensity.

## The Takeaway

The headline number \u2014 90 to 119 minutes a week \u2014 is worth remembering precisely because it is achievable. It is less time than most people spend scrolling in a single evening. For a community that does many things right on diet and lifestyle yet still falls ill earlier, building and keeping muscle may be one of the highest-return, lowest-cost health investments available. As one trainer quoted in coverage of the study put it, strength training should be "the basis of what you do" \u2014 not the afterthought it has long been treated as.

None of this replaces medical advice, and anyone with existing heart or joint conditions should start gradually and consult a clinician. But the direction of the evidence is now unambiguous: for staying alive and staying independent, the weights matter as much as the walking."""
})

# ============================================================
# ARTICLE 2: Sex-specific longevity diet (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Men and Women Need Different Diets to Live Longer, a 104,000-Person Study Finds. The Indian Plate Already Has an Edge.",
    "subheadline": "Research from Queen Mary University of London, published in Science Advances, found the ideal life-extending diet differs by sex \u2014 coffee and blood-sugar control for men, more fish and protein for women \u2014 and could add up to three years of life. Much of what it recommends is already built into the diaspora kitchen.",
    "slug": "sex-specific-longevity-diet-men-women-queen-mary-study-indian-plate-advantage-20260615",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/11097823/pexels-photo-11097823.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A vibrant fruit and vegetable display at an outdoor market, the foundation of the life-extending diets the study identified",
    "image_attribution": "Pexels",
    "diaspora_angle": "The study's life-extending recommendations \u2014 abundant vegetables, legumes, fish, and a blood-sugar-conscious approach \u2014 map closely onto traditional Indian regional cooking, giving diaspora families a head start if they resist the drift toward ultraprocessed Western convenience food.",
    "sources": json.dumps([
        {"name": "Science Advances", "url": "https://www.science.org/journal/sciadv"},
        {"name": "Queen Mary University of London", "url": "https://www.qmul.ac.uk/"},
        {"name": "The Scottish Sun", "url": "https://www.thescottishsun.co.uk/health/"}
    ]),
    "body": """The advice to "eat more vegetables and less red meat" is so familiar it has lost the power to change behaviour. A new study from Queen Mary University of London adds a twist that may make people pay closer attention: the diet that helps you live longest depends on whether you are a man or a woman \u2014 and the differences are large enough to matter.

Published in the journal Science Advances, the research analysed the eating habits of nearly 104,000 middle-aged British adults and tracked who died young. The right diet, the scientists found, could cut the risk of premature death by up to 24 per cent. For men, eating well added roughly three years of life expectancy; for women, about 2.3 years. But the optimal route to those extra years diverged by sex.

## Coffee for Men, Fish for Women

Both sexes benefited from the same foundation: plenty of vegetables, nuts, seeds, and beans, and far less red and processed meat, white bread, fried food, and ready meals. A Mediterranean-style pattern came out on top for everyone. The divergence was in the fine-tuning.

Men lived longest on a variant the researchers described as a diabetes-risk-reduction diet \u2014 one that prioritises keeping blood sugar low, helped along by generous amounts of coffee. The antioxidants in coffee have been tied in numerous studies to benefits for the brain, heart, and liver, and for men the blood-sugar-control angle appeared especially protective.

Women, by contrast, survived longest on an alternate Mediterranean pattern that boosted protein through extra fish while cutting back on potatoes. Fish delivers protein, vitamins, minerals, and omega-3 fatty acids while staying low in calories; potatoes, loaded with starch that converts quickly to sugar, fared worse on the female side of the analysis. "Our findings underscore the advantages of healthy diets in prolonging life expectancy," said study author Dr Jing Song.

The sex difference itself is the novel contribution. Most dietary guidelines treat men and women identically. This study suggests that hormonal, metabolic, and body-composition differences mean the same plate does not yield identical returns \u2014 a nuance that personalised-nutrition researchers have suspected but rarely quantified at this scale.

## The Indian Plate Already Has an Edge

Here is where the diaspora should lean in. Strip the study down to its principles \u2014 abundant vegetables, legumes as a protein backbone, minimal red and processed meat, restrained refined carbohydrates \u2014 and you are describing the architecture of traditional Indian regional cooking. A South Indian thali built on sambar, rasam, vegetables, and lentils; a Gujarati meal heavy on dal and shaak; a Bengali plate centred on fish; coastal cuisines rich in seafood: these patterns already align with what the Queen Mary team found extends life.

The legume point deserves emphasis. Indian diets are among the most lentil- and bean-forward in the world, and the study singled out beans and legumes as life-extending. The fish recommendation for women maps neatly onto Bengali, Goan, Kerala, and coastal Tamil traditions. Even the coffee finding has a regional echo in South India's filter kaapi culture, recently linked in a separate genetic study to better blood-sugar handling via the gut microbiome.

## The Threat Is Convenience

The risk for the diaspora is not the inherited diet \u2014 it is what replaces it. Second- and third-generation NRI families, time-pressed in fast-paced Western jobs, drift toward exactly the foods the study flagged as harmful: ready meals, fried convenience food, refined white bread and pasta, and ultraprocessed snacks. The frozen-paratha and instant-mix economy, convenient as it is, sits on the wrong side of this research.

The study's practical message for diaspora households is therefore less about adopting something foreign and more about resisting drift. The protective pattern is closer to a grandmother's kitchen than to a supermarket freezer aisle. Cooking dal from scratch, keeping vegetables and legumes at the centre of the plate, choosing fish over red meat, and treating refined carbohydrates as occasional rather than default \u2014 these are not new disciplines for Indian families. They are old ones worth reclaiming.

## A Caveat and a Direction

As with most nutrition research, this was an observational study: it shows strong associations, not ironclad cause and effect, and self-reported eating habits are imperfect. Individual needs vary, and anyone managing diabetes, kidney disease, or other conditions should personalise with a clinician.

But the headline is both encouraging and actionable. Up to three years of additional life from dietary choices is a meaningful return, and the sex-specific tuning gives men and women a sharper target than the generic "eat healthy." For the diaspora, the most striking part may be how little needs to change \u2014 provided the modern kitchen does not abandon the wisdom already on the menu."""
})

# ============================================================
# ARTICLE 3: RBI measures + bond rally (markets-finance)
# ============================================================
articles.append({
    "headline": "Foreigners Dumped \u20b962,800 Crore of Indian Stocks This Month. Then the RBI Quietly Reopened the Debt Door.",
    "subheadline": "As foreign portfolio investors pulled a record \u20b92.87 lakh crore from Indian equities in 2026, New Delhi scrapped taxes on government bonds and subsidised NRI deposit hedging \u2014 triggering over $1 billion of foreign bond buying in days and reshaping where diaspora money should look.",
    "slug": "fpi-equity-exodus-rbi-bond-tax-scrapped-nri-deposit-hedging-debt-inflows-20260615",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/5476028/pexels-photo-5476028.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A close-up of Indian rupee notes and coins, the currency at the centre of the RBI's inflow measures",
    "image_attribution": "Pexels",
    "diaspora_angle": "The RBI's package directly targets non-resident Indians \u2014 fully subsidising hedging costs on three-to-five-year NRI dollar deposits until September \u2014 while the bond-tax overhaul changes the risk-reward calculation for diaspora investors weighing Indian equities against fixed income.",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/markets/asia/indian-rupee-bonds-get-boost-iran-peace-deal-eye-fed-move-2026-06-15/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/markets/fpi-exodus-continues-62800-crore-pulled-out-from-equities-in-first-fortnight-of-june"},
        {"name": "Reuters \u2014 bond-tax measures", "url": "https://www.reuters.com/markets/asia/india-bond-tax-moves-catalyse-foreign-debt-inflows-2026/"}
    ]),
    "body": """The headline numbers from India's stock market this year read like a slow-motion exodus. Foreign portfolio investors yanked \u20b962,853 crore out of Indian equities in just the first fortnight of June, pushing total 2026 outflows to a staggering \u20b92.87 lakh crore. That single-year figure has already blown past the \u20b91.66 lakh crore foreigners pulled out across all of 2025, according to National Securities Depository data.

The causes are by now familiar to anyone tracking Asia's third-largest economy: a rupee that has weakened nearly 6 per cent this year and roughly 10 per cent over twelve months, sliding to around 95 to the dollar; an oil-price shock from West Asian conflict that inflated India's import bill; and stubbornly high US long-end yields that made emerging markets look less attractive. Foreign holdings of Indian equities have fallen to a 14-year low of 14.7 per cent, even as domestic institutions have climbed to a record 18.9 per cent.

But beneath the equity bloodletting, a quieter and arguably more consequential story has been unfolding in the bond market \u2014 and it is one the diaspora cannot afford to ignore.

## The RBI's Door-Reopening

On June 5, the Reserve Bank of India unveiled a wide-ranging package aimed squarely at drawing dollars back into the country. The centrepiece for global investors: New Delhi scrapped withholding and capital-gains taxes on foreign investment in government bonds and broadened the pool of securities available without investment limits. For a debt market long hamstrung by tax friction, the change was immediate and tangible.

"We believe that these changes are a game-changer for debt flows," said Jennifer Taylor, head of emerging market debt at State Street Investment Management, which oversees about $5.6 trillion. The reaction backed up the rhetoric. Foreign investors bought more than $1 billion of Indian government debt in just three sessions following the announcement \u2014 nearly matching the $1.6 billion purchased in the entire year up to that point. Net foreign bond buying over six sessions starting June 5 reached \u20b9155.5 billion, overtaking the \u20b9155 billion bought for the whole year through June 4.

Yields fell across the curve, with the steepest declines at shorter maturities. The benchmark 10-year yield ended last week at 6.90 per cent, down seven basis points and posting a third straight weekly decline. Corporate borrowers rushed in: companies raised more than \u20b9310 billion through bonds of up to five years in a single week as AAA-rated corporate yields fell 40 to 45 basis points from seven-year highs. State-run REC and NABARD both locked in three-year money at 7.34 per cent \u2014 well below the near-8 per cent rates of just weeks earlier.

## The NRI-Specific Hook

The piece of the package aimed directly at the diaspora is the deposit measure. The RBI is now fully subsidising hedging costs on foreign-currency deposits raised from non-resident Indians, for maturities of three to five years, on funds raised until September 30. By absorbing the hedging cost, the central bank lets banks convert NRI dollar deposits into rupees far more cheaply \u2014 which in turn lets them offer more competitive returns to attract that money.

For NRIs, this is the revival of a 2013-style mobilisation window, the same playbook India used during its last major currency crunch. The practical upshot: banks have a fresh incentive to court NRI dollar deposits with attractive rates, and the window has a hard September deadline. Diaspora savers sitting on dollars and weighing where to park them have a time-boxed opportunity to lock in.

## The Iran Wildcard

The picture brightened further over the weekend. Signals of a US-Iran peace deal \u2014 with an agreement to end hostilities and reopen the Strait of Hormuz \u2014 sent Brent crude tumbling 4.5 per cent to around $83 a barrel, a three-month low. The rupee was expected to open the new week stronger, in the 94.80 to 94.85 range, having settled at 95.11 on Friday. If crude stays anchored near $80, traders say the pressure from equity outflows should ease and portfolio flows could return.

The durability of that peace is the open question. A lasting drop in oil prices would relieve India's import bill, support the rupee, and reinforce the bond rally already underway. A relapse would reverse it.

## What the Diaspora Should Read Into This

For NRI investors, the divergence between equities and debt is the signal. Foreign money is fleeing Indian stocks on currency and valuation concerns \u2014 India still trades at a roughly 40 per cent premium to the broader emerging-market index \u2014 even as the same investors pile into newly tax-free Indian government bonds. That is not a vote of no confidence in India; it is a rotation toward better risk-adjusted returns within India.

The week ahead will test the trend. India's May wholesale inflation print, the US Federal Reserve's policy decision on June 17, and the Bank of Japan and Bank of England meetings all land within days, and any of them could move flows. But the structural shift is clear: New Delhi has deliberately tilted the field toward debt and toward NRI deposits. For diaspora investors who have watched their Indian equity exposure bleed all year, the most attractive opportunity right now may not be in stocks at all \u2014 and the deposit window closes in September."""
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
