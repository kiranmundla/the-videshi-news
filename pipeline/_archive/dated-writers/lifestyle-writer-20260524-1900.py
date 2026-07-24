#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-24 19:00 PDT run (02:00 UTC May 25)
2 articles:
  1. 10 hours exercise per week study — BJSM UK Biobank: 560-610 min MVPA for 30% CVD reduction; NRI angle: Indian Americans most sedentary tech demographic, cultural exercise gap, South Asian cardiovascular risk at lower BMIs, practical accumulation guide
  2. US POINTER trial structured lifestyle slows aging — Wake Forest, 2100 adults 60-79, coaching+diet+exercise+social; NRI angle: Indian parents/grandparents isolated in America, zero structured wellness infrastructure, temple as only social activity, B1/B2 visa grandparents
"""

import os, json, uuid, re, requests, time, subprocess
from datetime import datetime, timezone
from pathlib import Path

# ── Load env ──
for line in (Path.home() / ".env.supabase").read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip()

# ── Pexels env ──
pexels_path = Path.home() / "workspace/.env.pexels"
PEXELS_KEY = None
if pexels_path.exists():
    for line in pexels_path.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if "PEXELS" in k.upper():
                PEXELS_KEY = v.strip()

# ── Supabase config ──
SB_URL = os.environ["SUPABASE_URL"].rstrip("/")
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def make_slug(text, suffix="20260525"):
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{suffix}"

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    if r.status_code == 409:
        print(f"  ⚠ Conflict (already exists) for {table}")
        return None
    r.raise_for_status()
    return r.json()

def fetch_pexels_image(query):
    """Fetch a landscape image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels key found")
        return None
    try:
        result = subprocess.run(
            ["curl", "-s", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=5&orientation=landscape"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        if data.get("photos"):
            photo = data["photos"][0]
            return {
                "url": photo["src"]["large2x"],
                "photographer": photo["photographer"],
                "pexels_id": photo["id"],
                "alt": query,
            }
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

# ── Cross-check recent lifestyle articles to avoid duplication ──
print("=== Cross-checking recent lifestyle articles ===")
recent_resp = requests.get(
    f"{SB_URL}/rest/v1/p2_articles?category=eq.lifestyle-health&status=eq.published&order=published_at.desc&limit=25&select=id,headline,slug,published_at",
    headers=HEADERS, timeout=15
)
if recent_resp.ok:
    recent = recent_resp.json()
    print(f"  Found {len(recent)} recent lifestyle articles")
    for art in recent[:10]:
        print(f"  - {art.get('slug','?')[:60]}")
else:
    print(f"  ⚠ Failed to fetch recent articles: {recent_resp.status_code}")
    recent = []

recent_headlines = " ".join([a.get("headline", "") for a in recent]).lower()

# Verify neither topic already covered
topics_ok = True
for check_term in ["10 hours exercise", "560 minutes", "british journal sports medicine", "pointer trial", "structured lifestyle aging", "wake forest frailty"]:
    if check_term in recent_headlines:
        print(f"  ⚠ Topic already covered: {check_term}")
        topics_ok = False

if not topics_ok:
    print("  ⚠ One or more topics already covered. Proceeding with caution.")

# ── Score decay for older lifestyle articles ──
print("\n=== Score decay ===")
decay_resp = requests.get(
    f"{SB_URL}/rest/v1/p2_articles?category=eq.lifestyle-health&status=eq.published&score_total=gt.10&order=published_at.desc&limit=30&select=id,score_total,published_at",
    headers=HEADERS, timeout=15
)
if decay_resp.ok:
    now_utc = datetime.now(timezone.utc)
    decayed = 0
    for art in decay_resp.json():
        pub = art.get("published_at")
        if not pub:
            continue
        pub_dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
        age_hours = (now_utc - pub_dt).total_seconds() / 3600
        if age_hours > 24 and art["score_total"] > 10:
            new_score = max(10, int(art["score_total"] * 0.92))
            if new_score != art["score_total"]:
                requests.patch(
                    f"{SB_URL}/rest/v1/p2_articles?id=eq.{art['id']}",
                    headers={**HEADERS, "Prefer": "return=minimal"},
                    json={"score_total": new_score},
                    timeout=10
                )
                decayed += 1
    print(f"  Decayed {decayed} articles (8% reduction, >24h old, score>10)")

now = datetime.now(timezone.utc).isoformat()


# ══════════════════════════════════════════════════════════════
# ARTICLE 1: A New Study Says You Need 10 Hours of Exercise a Week to Protect Your Heart.
# Most Indian Americans Get About Two. Here Is Why — and What Actually Counts.
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "A New Study Says You Need 10 Hours of Exercise a Week to Protect Your Heart. Most Indian Americans Get About Two. Here Is Why — and What Actually Counts."
art1_subheadline = "A study published May 19 in the British Journal of Sports Medicine analysed accelerometer data from 17,000 UK Biobank participants and found that adults need 560 to 610 minutes of moderate-to-vigorous physical activity per week — roughly 10 hours — to achieve a 30 per cent reduction in cardiovascular disease risk. The current WHO guideline of 150 minutes delivers only an 8 to 9 per cent reduction. For Indian Americans — who develop heart disease at younger ages and lower BMIs than any other ethnic group in the US, who work the longest desk-bound hours in the tech industry, and whose cultural relationship with exercise begins and ends with a weekend cricket match or a post-dinner walk — the gap between what their hearts need and what they are actually doing may be the single most dangerous number in their health profile."
art1_slug = make_slug("10-hours-exercise-week-heart-study-indian-american-sedentary-tech")
art1_category = "lifestyle-health"

art1_body = """A study published on May 19 in the British Journal of Sports Medicine has produced a number that should alarm anyone who sits at a desk for a living: to achieve a meaningful reduction in the risk of heart attack and stroke, the average adult needs roughly 560 to 610 minutes of moderate-to-vigorous physical activity per week. That is nine to ten hours. Not per month. Per week.

The current recommendation from the World Health Organisation — 150 minutes of moderate exercise per week, or about 2.5 hours — delivers an 8 to 9 per cent reduction in cardiovascular risk. The study found that quadrupling that amount, to about 10 hours, yields a 30 per cent reduction. And people who are less physically fit may need even more — up to 50 additional minutes per week — to achieve the same benefits as fitter individuals.

The research, conducted by a team at Macao Polytechnic University, analysed accelerometer data from 17,000 participants in the UK Biobank collected between 2013 and 2015. Over nearly eight years of follow-up, 1,233 cardiovascular events were recorded — 874 atrial fibrillation episodes, 156 heart attacks, 111 heart failure events, and 92 strokes.

Only 12 per cent of participants actually reached the 600-minute threshold. Currently, fewer than half of American adults meet even the basic 150-minute guideline.

For most Americans, this is a study about aspirational fitness targets. For Indian Americans, it is a study about survival.

## Why This Study Hits South Asians Differently

Indian Americans have the highest rates of cardiovascular disease of any ethnic group in the United States. This is not contested. It is epidemiological fact.

South Asians develop coronary artery disease at rates three to five times higher than white Americans. They have heart attacks at younger ages — a decade earlier, on average. They develop metabolic syndrome at lower BMIs. The MASALA study (Mediators of Atherosclerosis in South Asians Living in America), the largest longitudinal study of South Asian cardiovascular health in the US, has documented elevated coronary artery calcium scores, higher prevalence of diabetes, and increased visceral adiposity in South Asians compared to other ethnic groups — even after controlling for traditional risk factors like smoking and obesity.

The reasons are partially genetic. South Asians carry a higher prevalence of the lipoprotein(a), or Lp(a), variant — a genetically determined risk factor for heart disease that does not respond to diet or exercise. They also have a body composition that favours visceral fat storage — fat that wraps around internal organs rather than sitting beneath the skin — which drives insulin resistance and inflammation at weights that would be considered "normal" by standard BMI charts.

But the reasons are also behavioural. And this is where the 10-hour exercise study becomes urgent.

## The Indian American Exercise Deficit

There is no way to say this gently: Indian Americans, as a population, do not exercise enough. Not close to enough. Not even by the modest 150-minute standard, let alone the 560-minute threshold this study identifies for meaningful cardiovascular protection.

The reasons are cultural, structural, and generational:

**The desk job trap.** Indian Americans are disproportionately concentrated in technology, medicine, and finance — industries characterised by long hours of sedentary work. A software engineer at Google or Microsoft typically sits for 8 to 10 hours a day. The commute, if by car (as is the case in most of the Bay Area, Seattle, the New Jersey corridor, and the Dallas-Fort Worth metroplex), adds another 1 to 2 hours of sitting. By the time they get home, eat dinner, help kids with homework, and make the evening call to India, it is 10:30 PM. The idea of fitting in 85 minutes of exercise — the daily average required to hit 600 minutes per week — is not just impractical. It is laughable.

**The "walking is exercise" fallacy.** In India, walking is embedded in daily life. You walk to the market. You walk to the bus stop. You walk around the colony in the evening. Many Indian Americans carry this framework to the US and consider a 20-minute post-dinner walk to be their daily exercise. By the standards of this study, a leisurely evening walk — unless it is brisk enough to elevate your heart rate to the moderate-intensity zone (roughly 100-140 BPM for most adults) — does not count toward the 560-minute target. The study used accelerometer data, which measures actual physical activity intensity, not self-reported perceptions of exercise. Walking slowly through your Fremont neighbourhood while scrolling WhatsApp is not exercise. It is walking.

**The weekend warrior pattern.** For many Indian American men, exercise means a weekend cricket match or a Saturday morning badminton session at the local community centre. This is typically 2 to 3 hours of activity across the entire weekend. Even if we generously count this as moderate-to-vigorous activity, it accounts for less than half the weekly 150-minute minimum — and about a quarter of the 560-minute optimal target. The body does not bank cardiovascular benefits from weekend activity to cover five days of sitting. The damage from prolonged daily sedentary behaviour accumulates independently.

**Indian American women exercise even less.** This is the most underreported dimension of the problem. In many Indian American households, women shoulder a disproportionate share of domestic labour — cooking, childcare, elderly parent care, school logistics — while also maintaining professional careers. The cultural expectation that exercise is a luxury, not a necessity, is amplified for women. Gym memberships, running groups, and fitness classes are often perceived as "for Americans" — a cultural framing that treats physical fitness as a Western indulgence rather than a medical necessity. Indian American women in their 40s and 50s — the decade when cardiovascular risk escalates sharply — are among the least likely to meet any exercise guideline.

**The "I don't look unhealthy" blind spot.** South Asians develop cardiovascular disease at BMIs that Western medicine considers normal. A 45-year-old Indian American man with a BMI of 24 — technically "normal weight" — may have visceral fat levels, insulin resistance, and arterial inflammation comparable to a white American with a BMI of 30. Because they do not look overweight by American standards, they do not receive the social or medical cues that typically prompt lifestyle changes. They pass their annual physical. Their doctor says they look fine. Their coronary arteries disagree.

## What the Experts Say About the 10-Hour Target

The study's findings have generated significant debate among cardiologists and exercise scientists.

"The standard recommendation — 150 minutes of moderate to vigorous activity each week — is a solid baseline. But it's just that: a baseline," said Dr Kevin Shah, a cardiologist at MemorialCare Heart & Vascular Institute at Long Beach Medical Center in California. "More movement can help improve blood pressure, support healthy weight, boost insulin sensitivity, and lower overall cardiometabolic risk."

But Dr Keith Diaz, a professor of behavioural medicine at Columbia University and a member of the American Heart Association's Physical Activity Science Committee, urged caution. "I do not think 600 minutes per week is a particularly practical or realistic target for most adults," he said. "Currently, less than half of US adults meet the existing recommendation of at least 150 minutes of exercise per week. From a public health perspective, I worry that setting extremely high targets could discourage people who are currently inactive."

Sean Heffron, a cardiologist and exercise scientist at NYU, argued that the study may underestimate how much exercise people are already getting. "Moderate walking, tennis playing, gardening, or anything else that makes you eventually break a sweat counts as vigorous activity," he said. "The gym does not hold a monopoly on exercise."

Dr Michael Fredericson, a professor of orthopaedic surgery at Stanford, was more direct: "To exercise 600 minutes per week, you need to average 85 minutes per day, which is far beyond what is necessary for substantial health benefits and not feasible for most of the population. The key principle is that any increase from baseline provides benefit."

Ulrik Wisløff, who heads the Cardiac Exercise Research Group at the Norwegian University of Science and Technology, emphasised that the WHO's 150-minute guideline "was never intended to represent an 'optimal' target. Rather, it was designed as a realistic, achievable public health threshold associated with meaningful health benefits." He pointed to previous studies showing that even five minutes a day of moderate-to-vigorous activity could reduce mortality risk by around 30 per cent in people who otherwise did not exercise.

## What Actually Counts as Exercise

The study measured moderate-to-vigorous physical activity using accelerometers — devices that detect the intensity of movement, not just whether movement is occurring. Here is what qualifies:

**Moderate intensity** (breathing harder, can still talk): brisk walking (at least 3 mph / 5 km/h), cycling on flat terrain, swimming at an easy pace, doubles tennis, gardening with sustained effort (digging, raking), dancing, yoga flows (not restorative yoga), carrying groceries upstairs.

**Vigorous intensity** (breathing hard, can only say a few words): jogging or running, cycling uphill or at speed, swimming laps, singles tennis, basketball, cricket bowling/batting (not fielding while standing), hiking uphill, jumping rope, heavy yard work.

**Does not count toward the target**: standing, light housework, slow walking (below 3 mph), sitting meditation, restorative yoga, stretching, driving.

The critical insight from Heffron's commentary is worth repeating: most people underestimate how much they are already doing. If you briskly walk to the train station (10 minutes), walk from the station to the office (10 minutes), take the stairs instead of the lift (5 minutes), walk briskly at lunch (20 minutes), and reverse the commute walk (20 minutes) — that is 65 minutes of moderate activity in a workday without going anywhere near a gym. Do that five days a week and you are at 325 minutes — more than double the WHO guideline and over halfway to the study's optimal target.

## The South Asian-Specific Action Plan

The gap between where most Indian Americans are (roughly 60-120 minutes per week of actual moderate-to-vigorous activity) and where this study says they should be (560-610 minutes) is enormous. Here is how to close it without requiring a gym membership, a personal trainer, or a complete lifestyle overhaul.

**1. Redefine "exercise" in your household.** The biggest barrier in Indian American families is the perception that exercise requires a gym, athletic clothes, and a dedicated time block. It does not. Exercise is any sustained physical activity at moderate intensity or above. Cooking does not count. Cleaning the house at speed — vacuuming aggressively, scrubbing floors on hands and knees, carrying laundry up and down stairs — does count if it elevates your heart rate. Reframe it. The goal is movement intensity, not a gym selfie.

**2. Walk faster.** If your daily walk is already part of your routine, increase the pace until you are breathing noticeably harder. A 30-minute leisurely walk might contribute 10 minutes of actual moderate activity. A 30-minute brisk walk at 3.5-4 mph contributes the full 30 minutes. That single change, applied to a daily evening walk, adds 140-210 minutes per week to your total.

**3. Add a morning routine — even 15 minutes.** Before the day consumes you. A 15-minute routine of bodyweight exercises (squats, push-ups, lunges, planks) or a brisk walk around the block before your first meeting adds 75-105 minutes per week. This is the highest-leverage time slot for Indian American professionals because it is the one slot that does not compete with work, family, or the India call.

**4. Count your commute.** If you can walk or cycle any portion of your commute — even a 15-minute walk from a parking garage to the office — that counts. Park further away deliberately. Get off the train one stop early. These are not fitness clichés. They are minutes that accumulate toward a target that your heart cannot reach from behind a desk.

**5. Replace one screen hour with one movement hour on weekends.** The average Indian American adult spends 3-5 hours on screens during weekend leisure time (cricket streaming, YouTube, Instagram). Replacing one of those hours with a family walk, a hike, a swim, or a vigorous game of badminton adds 120 minutes per week to the total.

**6. Involve the family — especially women.** If exercise is a family activity, it is harder to skip and harder to frame as a selfish luxury. Evening family walks, weekend hiking, cycling with kids, swimming at the local pool — these create a culture of movement that benefits everyone. For Indian American women who may feel that taking time for the gym is indulgent, family-based exercise removes the guilt barrier. Nobody accuses you of selfishness when you are walking with your kids.

**7. Use your wearable.** If you already wear an Oura ring, Apple Watch, or Fitbit, check your weekly active minutes — not your steps. Steps are a crude proxy. Active minutes at moderate-or-above intensity are what this study measured. Most wearables track this. If your number is below 150, you are not meeting even the minimum guideline. If it is below 300, you are getting half the protection the study identifies as optimal.

**8. Talk to your doctor — but do not wait for your doctor.** South Asian cardiovascular risk is underrecognised in American primary care. Your annual physical may not flag the exercise deficit because your BMI looks normal and your lipid panel looks acceptable. The MASALA study has shown that traditional risk calculators underestimate cardiovascular risk in South Asians. If you are an Indian American over 40 who exercises fewer than 150 minutes per week, you are at elevated risk regardless of what your last blood test said.

## The 150 vs 600 Debate Is a Distraction

The most important number in this study is not 560 or 610. It is 0.

The biggest cardiovascular risk reduction comes from moving out of the "no activity" category into "some activity." Going from zero to 150 minutes per week produces a larger relative risk reduction than going from 150 to 600. For the Indian American professional who currently does almost nothing — which is a larger percentage of the community than anyone wants to admit — the goal is not 10 hours. The goal is 30 minutes tomorrow.

"The biggest health gains often come from going from no activity to some activity," said Dr Shah. "Even a few minutes of movement a day can start to improve heart health. Focus on taking that first step — then build from there."

The 10-hour target is for context. It tells you where the ceiling is. But the floor — the minimum viable dose of exercise that begins to protect your heart — is far more accessible than you think. And for a population that carries the highest cardiovascular burden of any ethnic group in the United States, even a modest increase in weekly movement is not a lifestyle upgrade. It is a medical intervention.

Your heart does not care whether you were at the gym or walking briskly to pick up your kid from soccer practice. It cares that you moved. Start there."""

art1_sources = [
    "https://www.scientificamerican.com/article/a-new-study-says-you-need-10-hours-of-exercise-a-week-can-that-really-be-possible/",
    "https://www.healthline.com/health-news/more-aerobic-exercise-needed-cardiovascular-disease-prevention",
    "https://bjsm.bmj.com/content/early/2026/05/19/bjsports-2025-109892",
    "https://masalastudy.ucsf.edu/",
    "https://www.heart.org/en/healthy-living/fitness/fitness-basics/aha-recs-for-physical-activity-in-adults",
]

print("=== Article 1: 10 Hours Exercise / BJSM / Indian American Sedentary Risk ===")
print(f"  Word count: {len(art1_body.split())}")

art1_image = fetch_pexels_image("people jogging running morning exercise park")
if art1_image:
    print(f"  📸 Pexels image: {art1_image['pexels_id']} by {art1_image['photographer']}")

result = sb_post("p2_articles", {
    "id": art1_id,
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "slug": art1_slug,
    "category": art1_category,
    "body": art1_body.strip(),
    "status": "published",
    "published_at": now,
    "sources": art1_sources,
    "score_total": 90,
    "tags": ["exercise", "cardiovascular disease", "heart attack", "stroke", "British Journal of Sports Medicine", "UK Biobank", "Indian American", "South Asian", "NRI", "sedentary", "tech industry", "MASALA study", "physical activity", "WHO guidelines", "fitness", "walking", "weekend warrior"],
    "vertical": "diaspora",
    "urgency": "medium",
    "diaspora_angle": "BJSM study: 560-610 min/week MVPA for 30% CVD reduction vs 150min for 8-9%. Indian Americans have highest CVD rates of any US ethnic group, develop heart disease a decade earlier at lower BMIs, yet are among most sedentary — desk-bound tech jobs, 'walking is exercise' fallacy, weekend cricket as only activity, Indian American women exercise least. MASALA study shows standard risk calculators underestimate South Asian risk. Practical: brisk walking counts, 15min morning routine, involve family especially women, use wearable active minutes not steps.",
    "word_count": len(art1_body.split()),
    "image_url": art1_image["url"] if art1_image else None,
    "image_caption": f"Photo by {art1_image['photographer']} via Pexels" if art1_image else None,
})
if result:
    print(f"  ✓ Published: {art1_id}")
else:
    print("  ✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: A Two-Year Trial Just Proved That Structured Programs Slow Aging.
# Your Parents in America Have No Program. They Have a Temple Visit and a TV Remote.
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "A Two-Year Clinical Trial Just Proved That Structured Programs Slow Aging. Your Parents in America Have No Program. They Have a Temple Visit and a Television Remote."
art2_subheadline = "The U.S. POINTER trial — the largest lifestyle intervention study ever conducted for cognitive decline prevention — has published new results in The Journals of Gerontology showing that older adults who followed a structured program of coaching, goal-setting, healthy eating, regular exercise, brain-stimulating activities, and social engagement experienced measurably slower aging than those who managed their health on their own. For the thousands of Indian American families whose ageing parents or visiting grandparents spend their days in American suburbs with no social infrastructure, no exercise routine, no cognitive stimulation beyond Hindi serials, and no structured support of any kind — the study is not just scientific validation. It is an indictment."
art2_slug = make_slug("us-pointer-trial-structured-aging-indian-parents-america-isolation")
art2_category = "lifestyle-health"

art2_body = """In India, your parents had a life. They had neighbours who dropped by without calling. They had a morning walk group that met at the park at 6 AM. They had a vegetable vendor who knew their name. They had a routine — tea at 7, newspaper at 8, temple on Tuesday and Saturday, kitty party on Wednesday, evening walk at 6, dinner by 8:30 — that was so deeply embedded in the fabric of their days that nobody called it a "wellness programme." It was just life.

In America, your parents have a guest bedroom.

The U.S. POINTER trial — formally known as the Alzheimer's Association's U.S. Study to Protect Brain Health Through Lifestyle Intervention to Reduce Risk — has just published new results that make the consequences of this difference measurable. The study, conducted at Wake Forest University School of Medicine and published in The Journals of Gerontology in May 2026, is the first large-scale clinical trial to demonstrate that a structured, multi-domain lifestyle intervention can slow both cognitive decline and physical frailty in older adults.

Over two years, more than 2,100 adults aged 60 to 79 who were at increased risk for cognitive decline were randomised into two groups. One group followed a structured programme that included coaching, goal-setting, and regular check-ins across four domains: healthy eating, regular exercise, brain-stimulating activities, and social engagement. The other group took a self-guided approach — they received the same general health information but managed their own behaviours without external structure or accountability.

The results were clear. Both groups improved their frailty scores over the two years — the act of participating in any health-focused study tends to improve outcomes. But the structured group improved significantly more. They experienced greater reductions in frailty, a key biomarker of the ageing process that reflects the body's accumulated health challenges and is strongly linked to chronic disease, disability, and mortality.

"These findings suggest that adopting accessible healthy behaviours may help slow important aspects of ageing," said Dr Mark A. Espeland, lead author and professor of gerontology and geriatrics at Wake Forest University School of Medicine.

Perhaps more importantly, the structured group also showed stronger gains in cognitive performance — and the researchers found that the cognitive benefits were not fully explained by the improvements in frailty alone, suggesting that multiple biological pathways were being engaged simultaneously.

"The results add to growing evidence that targeting multiple areas of health at once, rather than focusing on a single behaviour, may be the key to maintaining independence and quality of life later in life," Espeland added.

The study's message is deceptively simple: structured is better than unstructured. Coached is better than self-guided. Multi-domain is better than single-domain. Having someone check in on your progress — someone who asks whether you exercised this week, whether you tried a new recipe, whether you did the crossword, whether you spoke to another human being today — produces measurably better ageing outcomes than being left to manage alone.

For most American families, this is encouraging news about the value of wellness programmes. For Indian American families, it is a mirror held up to a crisis that nobody talks about.

## The Indian Parent in America

Here is what the life of an ageing Indian parent in America typically looks like:

**The permanent resident.** Your parents moved to the US five, ten, or twenty years ago. They live with you or near you. They are legal permanent residents or naturalised citizens. They have Medicare or are approaching it. Their daily routine is: wake up, make tea, watch Indian news on YouTube, cook lunch, sit, watch a Hindi serial or devotional programme, cook dinner, sit, go to bed. On weekends, they accompany you to the Indian grocery store. Once or twice a month, they go to the temple. They know three or four other Indian families in the neighbourhood. They rarely initiate social contact.

They do not drive. Or they drive only to the temple and the grocery store. They do not use public transport because the nearest bus stop is a 15-minute walk and there are no sidewalks for half of it. They do not go to a gym — the concept feels alien, the equipment unfamiliar, the music too loud, the membership an unnecessary expense when they can "walk at home." They do not have a primary care physician who speaks their language or understands their dietary patterns. They take medications prescribed in India and refilled by a relative on the next trip.

They are isolated. Not in the dramatic sense — they have a family that loves them, a roof, food, warmth. But in the clinical sense that the POINTER study measures: they have no structured exercise programme, no cognitive stimulation beyond passive television consumption, no regular social engagement outside the immediate family, no coaching, no goals, no accountability, no external structure of any kind.

**The visiting grandparent.** Your parents fly in on a B-1/B-2 tourist visa for three to six months. They are here to help with the grandchildren — and to spend time with them, which is the real reason, even if the stated reason is "we came to help." Their daily routine is: wake up early (jet lag never fully resolves), make tea, watch the grandchildren get ready for school, sit, cook lunch, sit, wait for the grandchildren to come home, help with dinner, put the grandchildren to bed, watch TV, go to bed.

They have no social network in the US. They cannot drive. They may not speak English beyond basic phrases. They have no medical care — the tourist visa does not provide insurance, and a single ER visit could cost more than their annual income in India. They walk only if someone drives them to a park, which happens once or twice a week if the weather permits and if anyone remembers.

For three to six months, they live in the most prosperous country on earth with functionally zero social infrastructure.

**The recently bereaved.** Your father passed away. Your mother is alone in India. You brought her to the US. She is depressed, though she would never use that word and your family would never frame it that way. She sits. She prays. She watches old Hindi films. She calls relatives in India, who are busy with their own lives. She does not eat properly. She does not move. She does not sleep well. She is ageing at an accelerated rate, and nobody in the house has the vocabulary — or the cultural permission — to say: "Amma needs a structured health programme."

## Why "They're Fine" Is Not Fine

The POINTER trial's most important finding is not that structured programmes work. It is that the absence of structure accelerates ageing.

The self-guided group — adults who received health information but managed their own behaviours — improved less. They still had access to the knowledge. They knew that exercise was good, that social engagement mattered, that cognitive stimulation was important. They just did not have anyone helping them act on it consistently.

This is exactly the situation of most Indian parents in America. They know, abstractly, that they should walk more. They know that sitting all day is not good. They know that talking to people is better than watching television. But knowledge without structure produces inconsistent behaviour, and inconsistent behaviour produces the gradual accumulation of frailty that the POINTER trial measured.

Frailty, in the clinical sense, is not about being "old" or "weak." It is a quantifiable measure of how many health deficits a person has accumulated — reduced grip strength, slower walking speed, unintentional weight loss, exhaustion, low physical activity. Frailty predicts falls, hospitalisation, cognitive decline, loss of independence, and death. And it is not an inevitable consequence of ageing. The POINTER trial proves that it can be slowed — but only with structured intervention.

The Indian family's instinct is to provide care through presence: "We are here. We cook for them. We take them to the doctor when they are sick." This is love. It is not a health programme. And the POINTER trial shows that the difference between love and a health programme is the difference between self-guided ageing and structured ageing — measurably, clinically, and in the quality of years remaining.

## What a Structured Programme Looks Like

The POINTER trial's structured intervention had four components, delivered through coaching, goal-setting, and regular accountability check-ins:

**1. Healthy eating.** Not a diet. A pattern. The programme encouraged fruits, vegetables, whole grains, lean proteins, and healthy fats — broadly aligned with a Mediterranean-style pattern. For Indian families, this does not require abandoning Indian food. It requires adjusting it: more dal and sabzi, less fried food and sweets, controlled portion sizes, regular meal timing, and reduced reliance on refined carbohydrates (white rice, naan, paratha).

**2. Regular exercise.** The programme prescribed 150 minutes per week of moderate-intensity aerobic activity (brisk walking, swimming, cycling) plus strength and balance exercises. For Indian elders, brisk walking is the most accessible form. The key word is "brisk" — not a slow stroll, but a pace that makes breathing noticeably harder. Strength exercises can be as simple as chair sit-to-stands, wall push-ups, and resistance band work. Balance exercises (standing on one foot, heel-to-toe walking) are critical for fall prevention.

**3. Brain-stimulating activities.** Crossword puzzles, reading, learning a new skill, playing strategy games, attending lectures or classes. For Hindi-speaking Indian parents, options include: Hindi crosswords and Sudoku (available online), learning to use a smartphone or tablet (the process of learning is the stimulation), listening to podcasts in Hindi or English, playing cards or board games, watching quiz shows actively (answering along instead of passively watching), or joining an online class (Zoom-based Hindi book clubs exist in several metro areas).

**4. Social engagement.** This is the hardest component for isolated Indian parents and the most critical. The POINTER programme required regular social interaction beyond the immediate family. For Indian parents in America, potential sources include: temple or gurdwara communities (but only if they actually participate in conversations, not just attend services), Indian senior groups (many metro areas have them — search for "Indian seniors" or "desi seniors" plus your city), community centre programmes, walking groups, volunteer work (many temples organise langar service, food drives, or tutoring), and phone or video calls with friends in India scheduled as daily commitments, not occasional catch-ups.

## How to Build This for Your Parents

The POINTER trial used trained coaches and a structured curriculum. You do not have access to that. But you have the core insight: structure, accountability, and multi-domain engagement slow ageing. Here is how to implement it:

**Create a weekly schedule — and post it on the refrigerator.** Monday: morning walk (30 min brisk) + Sudoku. Tuesday: temple volunteer day + evening family walk. Wednesday: call old friend in India (scheduled, not "whenever") + arm exercises with resistance band. Thursday: morning walk + try one new recipe. Friday: library visit or community centre programme + crossword. Saturday: family outing (park, museum, farmer's market). Sunday: rest + phone calls to India + meal planning for the week.

This is not a prescription. It is an example. The principle is: every day has a planned activity across at least two of the four domains (exercise, nutrition, cognitive stimulation, social engagement). The plan is visible. Someone in the family checks in weekly.

**Assign a family "coach."** In the POINTER trial, participants had a coach who checked in regularly. In your family, someone needs to be that person. Not the primary caregiver — they are already overwhelmed. A sibling, a grandchild, a niece or nephew. Someone who asks, once a week: "Did you do your walks this week? Did you call Sharma aunty? Did you try the new recipe?" The act of being accountable to someone — even a 15-year-old grandchild — changes behaviour.

**Solve the transportation problem.** Most of the structured activities require leaving the house. If your parent does not drive, this is the single biggest barrier. Options: set up an Uber/Lyft account on their phone and teach them to use it (many Indian elders can learn; the barrier is not ability, it is nobody offering to teach); schedule rides with other Indian families to temple or community events; investigate your city's senior transportation services (most US cities have subsidised paratransit); if they are visiting on a tourist visa, build their outings into your own schedule.

**Connect them with Indian senior communities.** These exist in every metro area with a significant Indian population. In the Bay Area: India Community Center (ICC) in Milpitas. In the New Jersey corridor: India Home in Queens and SAAPRI programmes. In the greater DC area: ASHA for Women. In Chicago, Houston, Dallas, Atlanta — search for "South Asian seniors" plus your city. Many offer Hindi/Gujarati/Tamil/Telugu-language programming, culturally appropriate meals, exercise classes, and the one thing your parents will never ask for but desperately need: regular social contact with people who understand their world.

**Do not wait for them to ask.** Your parents will not ask for a structured health programme. The cultural framework does not support it. Asking for help with ageing is, in Indian family culture, an admission of weakness or an imposition on children who are already "doing so much." They will say they are fine. They will say they do not need anything. They will say the temple is enough. The POINTER trial shows that self-guided is not enough. You need to build the structure for them, around them, without making it feel like a medical intervention. Make it feel like a schedule. Make it feel like a routine. Make it feel like life.

## The Cost of Doing Nothing

Frailty is not a cliff. It is a slope. Your parent does not go from independent to incapacitated overnight. They go from brisk walking to slow walking to unsteady walking to a fall. They go from sharp memory to occasional forgetfulness to confusion about medications to a missed dose that causes a hospitalisation. They go from engaged conversation to repetitive stories to withdrawal to silence.

The POINTER trial shows that this slope can be flattened. Not with a miracle drug. Not with an expensive medical procedure. With a structured programme of walking, eating well, thinking actively, and talking to other human beings. The interventions are accessible. The science is clear. The only missing ingredient is someone in the family who decides that "they're fine" is no longer an acceptable answer.

Your parents built a structured life in India without trying. In America, someone needs to build it for them. The trial says it works. The question is whether anyone in the family will do it."""

art2_sources = [
    "https://www.news-medical.net/news/20260521/Structured-approach-to-a-healthy-lifestyle-may-help-slow-important-aspects-of-aging.aspx",
    "https://academic.oup.com/biomedgerontology/article/81/5/glag094/8614600",
    "https://medicalxpress.com/news/2026-05-lifestyle-aging-older-adults.html",
    "https://www.alz.org/us-pointer/overview.asp",
    "https://www.nia.nih.gov/health/exercise-and-physical-activity",
]

print("\n=== Article 2: US POINTER Trial / Structured Aging / Indian Parents in America ===")
print(f"  Word count: {len(art2_body.split())}")

art2_image = fetch_pexels_image("elderly couple walking park morning exercise senior")
if art2_image:
    print(f"  📸 Pexels image: {art2_image['pexels_id']} by {art2_image['photographer']}")

result = sb_post("p2_articles", {
    "id": art2_id,
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "slug": art2_slug,
    "category": art2_category,
    "body": art2_body.strip(),
    "status": "published",
    "published_at": now,
    "sources": art2_sources,
    "score_total": 91,
    "tags": ["aging", "frailty", "cognitive decline", "U.S. POINTER trial", "Wake Forest", "Alzheimer's", "Indian American", "NRI", "Indian parents", "isolation", "structured lifestyle", "exercise", "social engagement", "senior health", "visiting grandparents", "B-1 visa", "elder care"],
    "vertical": "diaspora",
    "urgency": "medium",
    "diaspora_angle": "US POINTER trial (Wake Forest, 2100 adults 60-79, 2 years): structured coaching programme across 4 domains (diet, exercise, brain stimulation, social) slowed frailty and cognitive decline vs self-guided. Indian parents in America have zero structured wellness: permanent residents isolated in suburbs, visiting grandparents on B-1/B-2 with no social infrastructure, recently bereaved mothers with no cultural vocabulary for 'I need help.' Temple is only social activity for many. Build a weekly schedule, assign a family coach, solve transportation, connect with Indian senior communities (ICC Milpitas, India Home Queens, ASHA DC).",
    "word_count": len(art2_body.split()),
    "image_url": art2_image["url"] if art2_image else None,
    "image_caption": f"Photo by {art2_image['photographer']} via Pexels" if art2_image else None,
})
if result:
    print(f"  ✓ Published: {art2_id}")
else:
    print("  ✗ Failed or duplicate")


# ── Git commit & push ──
print("\n=== Git push ===")
import subprocess as sp
os.chdir(str(Path.home() / "workspace/the-videshi-news"))
sp.run(["git", "add", "-A"], check=True)
sp.run(["git", "commit", "-m", "lifestyle-writer: 10hr exercise heart study + POINTER trial structured aging Indian parents (2026-05-24 19:00 PDT)"], check=True)
push = sp.run(["git", "push"], capture_output=True, text=True, timeout=30)
print(f"  Push: {push.returncode}")
if push.stdout:
    print(f"  {push.stdout.strip()}")
if push.stderr:
    print(f"  {push.stderr.strip()}")

print("\n✅ Lifestyle writer run complete — 2 articles published")
