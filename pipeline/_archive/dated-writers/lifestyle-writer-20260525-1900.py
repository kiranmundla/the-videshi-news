#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-25 19:00 PDT run (02:00 UTC May 26)
2 articles:
  1. UPenn/UT Southwestern study (Neuron, May 16 2026): Exercise physically rewires the brain — SF1 neurons in the hypothalamus fire AFTER a workout and are essential for building endurance. Blocking them prevents fitness gains even when animals exercise. NRI angle: Indian American tech workers skip cooldowns and jump straight into Zoom calls; the post-exercise brain window is where adaptation happens. "Rest after exercise" (Indian grandparent wisdom) was accidentally right — but for reasons nobody expected.
  2. UCL/King's/Oxford systematic review (Population Studies, May 2026, 88,500 Britons, 51 studies, cohorts 1946-2002): Each generation since WWII is objectively sicker at the same age — obesity, mental health, diabetes all worse. NRI angle: Indian immigrants arrive healthier than average Americans, but their children absorb American processed food + Indian academic pressure + sedentary tech culture — the "immigrant health advantage" erodes within one generation, and no one is measuring it.
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
    f"{SB_URL}/rest/v1/p2_articles?category=eq.lifestyle-health&status=eq.published&order=published_at.desc&limit=30&select=id,headline,slug,published_at",
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
recent_slugs = " ".join([a.get("slug", "") for a in recent]).lower()

# Verify neither topic already covered
topics_ok = True
for check_term in ["exercise brain endurance neuron", "sf1 neuron hypothalamus", "exercise rewires brain", "generational health drift", "each generation sicker", "younger generations worse health"]:
    if check_term in recent_headlines or check_term in recent_slugs:
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
# ARTICLE 1: Your Brain Keeps Working After You Stop Running.
# A Penn Study Says That's Where Fitness Actually Happens.
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "Your Brain Keeps Working After You Stop Running. A New Study Says That Post-Exercise Window — Not the Workout Itself — Is Where Your Body Actually Gets Fitter."
art1_subheadline = "Researchers at the University of Pennsylvania and UT Southwestern found that a cluster of neurons deep in the brain fires intensely after exercise ends — and that silencing those neurons prevents the body from building endurance, even when the animal keeps training. The study, published in Neuron on May 16, 2026, is the first to show that physical fitness depends on a brain signal that arrives after the workout is over. For the Indian American tech worker who squeezes in a 6 AM run and then sits on a stressful conference call by 6:45, the implication is unsettling: you may be interrupting the most important part of your workout without knowing it."
art1_slug = make_slug("exercise-brain-sf1-neurons-endurance-post-workout-indian-tech-worker")
art1_category = "lifestyle-health"

art1_body = """You finished your run. You towelled off, checked your Garmin, drank your protein shake, opened your laptop, and joined the standup. The workout is done. The benefits are locked in. That is the assumption that governs how most working adults — and especially Indian American professionals in time-starved dual-income households — structure their exercise.

A study from the University of Pennsylvania has just demonstrated that this assumption is wrong. The most important phase of your workout is not the workout. It is what your brain does in the minutes and hours immediately after you stop moving.

## The Neurons That Fire After You Stop

The research, led by Professor J. Nicholas Betley at Penn, Professor Kevin W. Williams at UT Southwestern, and Professor Erik Bloss at The Jackson Laboratory, focused on a cluster of brain cells called steroidogenic factor-1 (SF1) neurons, located in the ventromedial hypothalamus — a small, ancient region deep in the brain that regulates metabolism, energy balance, and hunger.

The scientists used miniature microscopes mounted on the heads of mice to record what these neurons did during and after treadmill running. They expected to see peak activity during the exercise itself, when metabolic demand was highest.

What they found instead was striking: the SF1 neurons became most active immediately after exercise ended. They fired intensely in the post-workout period — and this post-exercise burst of brain activity continued for at least an hour after the animals stopped running.

"The brain isn't just a passenger during exercise," Williams told PsyPost. "It is actively involved in the adaptations that make you fitter over time."

## Silencing the Signal Kills the Gains

The researchers then asked the critical question: what happens if you block this post-exercise brain signal?

They genetically modified a group of mice so that their SF1 neurons could not communicate — introducing a tetanus toxin into those specific cells to prevent them from releasing chemical signals. These modified mice were put through the same treadmill exercise stress tests as normal mice.

The results were unambiguous. The modified mice consumed oxygen at normal rates — their lungs and hearts were fine. But they exhausted much faster. And when both groups were put through a three-week training programme — running on the treadmill five days a week at gradually increasing speeds — normal mice rapidly improved their running times and distances. The mice with silenced brain cells showed no improvement in stamina whatsoever.

The scientists collected skeletal muscle tissue and analysed which genes were turned on after exercise. In normal mice, a cascade of genetic changes reshaped the muscles for better energy use. In the mice with silenced SF1 neurons, those normal genetic changes in the muscle were almost entirely absent. The muscles were receiving no permission signal from the brain to remodel.

"We were struck by how pronounced the effect was," Williams said. "Disrupting SF1 neuron activity significantly blunted endurance improvements even when the animals were still running, which suggested the neurons aren't just responding to exercise, but are actively mediating adaptation."

## The 15-Minute Experiment

To prove that the timing of the brain signal mattered specifically, the researchers used optogenetics — a technique that lets scientists turn brain cells on or off with light through a tiny fibre optic cable inserted into the brain.

During a three-week training programme, they turned off the SF1 neurons for just fifteen minutes immediately following each daily run. That brief suppression — only fifteen minutes of silenced brain activity after exercise — was enough to prevent the mice from improving their stamina across the entire training period.

In a separate group, the researchers did the opposite: they stimulated the SF1 neurons for a full hour after each training session. These mice gained significantly more endurance than mice undergoing the exact same physical training without the extra brain stimulation. They ran longer and at higher speeds by the end of the trial.

The post-exercise window is not just important. It appears to be the primary mechanism through which the body converts physical effort into lasting fitness.

## What Changes in the Brain

The study documented physical changes in the brain itself. After three weeks of exercise, the mice had twice as many dendritic spines — the tiny branch-like structures where brain cells connect and communicate — on their SF1 neurons compared to sedentary mice. The spontaneous firing rate of these neurons more than doubled. In the exercised group, there were no completely silent neurons; every SF1 cell was active and engaged.

Exercise had physically rewired the brain to receive and send more signals. The brain had adapted to exercise just as muscles adapt — by building new infrastructure for communication.

## The Indian Tech Worker Problem

Here is where this becomes personal for the half-million Indian American technology workers who structure their lives around maximising productive hours.

The typical morning for a senior engineer or product manager in the Bay Area, Seattle, or Hyderabad time-zone-straddling companies goes like this: alarm at 5:30 AM, run or gym by 5:45, workout from 5:45 to 6:30, shower, coffee, first meeting at 7:00 or 7:15 AM. Sometimes the meeting starts at 6:45 because India is online and someone scheduled a sync.

The Penn study suggests that the period from 6:30 to 7:30 — the hour after exercise ends — is when the brain is sending its most critical adaptation signals. It is when SF1 neurons are firing at peak intensity. It is when the genetic cascade that remodels muscle tissue is being initiated from the brain. And it is exactly the window that gets sacrificed to the first Zoom call.

Nobody knows yet whether a stressful conference call disrupts SF1 neuron activity in the same way that optogenetic silencing does in mice. That experiment has not been done. But the directional logic is clear: the post-exercise brain state is not a passive cooldown. It is an active, signal-intensive process that the brain has evolved to prioritise. Flooding that window with cortisol from a status update about a missed deadline is unlikely to help.

This matters especially for Indian American professionals because the cultural model of productivity — inherited from both Indian academic culture and Silicon Valley hustle culture — treats non-working minutes as waste. The fifteen-minute post-workout stretch, the twenty-minute walk after a run, the quiet coffee before opening Slack — these are the minutes that get compressed first when schedules tighten. They are also, according to this study, the minutes that determine whether your exercise actually makes you fitter.

## Your Grandparents Were Accidentally Right

Indian grandparents have a phrase for what you should do after exercise: "thoda rest karo" — take some rest. The advice was never framed in terms of hypothalamic neuroscience. It was framed as common sense, usually accompanied by the suggestion to drink warm water and sit quietly for a few minutes.

The Penn study does not validate every piece of traditional Indian health advice. But it does validate this specific instinct: the period after physical effort is not downtime. Something important is happening in the body — and now we know it is happening in the brain.

The difference is that "thoda rest karo" meant lying on the sofa. What the science actually suggests is that the brain needs a period of low-stress, low-stimulation recovery — not necessarily sleep, not necessarily meditation, but not a high-cortisol cognitive task either. A walk. A quiet cup of chai. Reading the newspaper. Anything that does not require the brain to shift from metabolic adaptation mode into fight-or-flight mode.

## What You Can Actually Do

The study was conducted in mice, and the researchers explicitly caution that translation to humans requires further work. The hypothalamic circuits studied are conserved across mammals, which makes the findings plausible in humans, but not yet proven.

That said, the directional advice is straightforward:

**Protect the post-exercise window.** If you run at 6 AM, do not schedule your first meeting at 6:30. Give yourself at least 30 to 45 minutes of low-stress time after your workout. Shower slowly. Eat breakfast. Walk the dog. Do not open Slack, do not check email, do not jump on a call.

**Do not count the cooldown as wasted time.** The Indian professional tendency to treat every non-productive minute as inefficiency has a cost. If your brain needs that post-workout window to consolidate fitness gains, then compressing it is not saving time — it is wasting the workout.

**If you must work out in a tight window, move the workout later.** A 7 PM run followed by a quiet dinner and sleep may deliver more fitness benefit than a 5:30 AM run followed by an immediate 6:30 AM standup — because the evening run's post-exercise window falls into a naturally low-stress period.

**Weekend warriors get a natural advantage here.** If you run on Saturday morning and then spend two hours reading the paper and drinking coffee, your post-exercise brain window is fully protected. This may partially explain why some people see disproportionate benefits from weekend exercise compared to daily compressed workouts.

**Watch your children's sports schedule.** Indian American parents who drive their kids to 6 AM soccer practice and then immediately drop them at school may be short-circuiting the same mechanism. The child's brain needs post-exercise recovery time, not a pre-calc worksheet in the car.

## The Bigger Picture

The Penn study adds to a growing body of research showing that fitness is not purely a muscular or cardiovascular phenomenon. The brain is not just reacting to exercise — it is actively directing the body's response to it. The muscles need a signal from the brain to remodel. Without that signal, exercise is effort without adaptation.

"Exercise remains one of the best medicines we have," Williams said, "and understanding its biology in the brain is still in its early days. Studies like this remind us that the brain's role in physical fitness is far more active and specific than we once appreciated."

For the Indian American community — which faces elevated risks of diabetes, cardiovascular disease, and metabolic syndrome despite high education and income levels — this finding reframes the exercise conversation. The question is no longer just whether you exercise, or how hard, or how often. The question is what you do in the hour after you stop.

The answer, it turns out, is nothing. And that nothing is the most productive thing you will do all day."""

art1_sources = [
    "https://doi.org/10.1016/j.neuron.2026.04.024",
    "https://www.psypost.org/scientists-reveal-the-brains-surprisingly-active-role-in-building-exercise-endurance/",
    "https://knowridge.com/2026/05/your-brain-keeps-working-after-exercise-and-it-may-help-you-get-fitter/",
    "https://newstarget.com/2026-05-18-exercise-rewires-brain-to-improve-endurance.html",
]

print("\n=== Article 1: Exercise Brain SF1 Neurons / Post-Workout Window / Indian Tech Workers ===")
print(f"  Word count: {len(art1_body.split())}")

art1_image = fetch_pexels_image("runner resting after workout morning light calm")
if art1_image:
    print(f"  📸 Pexels image: {art1_image['pexels_id']} by {art1_image['photographer']}")

result1 = sb_post("p2_articles", {
    "id": art1_id,
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "slug": art1_slug,
    "category": art1_category,
    "body": art1_body.strip(),
    "status": "published",
    "published_at": now,
    "sources": art1_sources,
    "score_total": 88,
    "tags": ["exercise", "brain", "neurons", "endurance", "fitness", "hypothalamus", "SF1 neurons", "post-workout", "recovery", "cooldown", "Indian American", "tech workers", "Silicon Valley", "Neuron journal", "University of Pennsylvania", "UT Southwestern", "optogenetics", "metabolism", "dendritic spines", "morning workout", "Zoom calls", "cortisol", "stress"],
    "vertical": "diaspora",
    "urgency": "standard",
    "diaspora_angle": "UPenn/UT Southwestern study in Neuron (May 16, 2026): SF1 neurons in hypothalamus fire AFTER exercise ends, not during — silencing them for just 15 minutes post-workout blocks all endurance gains even when animals keep training. Exercise physically rewires the brain (2x dendritic spines, doubled firing rates). NRI angle: Indian American tech workers compress the post-exercise window into zero — 6 AM run → 6:30 AM Zoom standup is the default schedule. The most important part of the workout is not the workout but the low-stress recovery hour afterward. 'Thoda rest karo' was accidentally right. Also applies to kids: 6 AM soccer → immediate school drop-off may undermine the adaptation window.",
    "word_count": len(art1_body.split()),
    "image_url": art1_image["url"] if art1_image else None,
    "image_caption": f"Photo by {art1_image['photographer']} via Pexels" if art1_image else None,
})
if result1:
    print(f"  ✓ Published: {art1_id}")
else:
    print("  ✗ Failed or duplicate")

if result1 and art1_image:
    patch_r = requests.patch(
        f"{SB_URL}/rest/v1/p2_articles?id=eq.{art1_id}",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json={"image_url": art1_image["url"], "image_caption": f"Photo by {art1_image['photographer']} via Pexels"},
        timeout=10
    )
    print(f"  Image PATCH: {patch_r.status_code}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Every Generation Since World War II Has Been
# Sicker Than the One Before It. Your Children Are Growing
# Up in the Worst Health Environment in Modern History.
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "Every Generation Since World War II Has Been Sicker Than the One Before It. A Review of 88,500 Britons Confirms the Pattern. Your Children Are Growing Up in the Worst Health Environment in Modern History."
art2_subheadline = "Researchers at University College London, King's College London, and the University of Oxford reviewed 51 studies covering six British birth cohorts from 1946 to 2002 — and found that for obesity, mental health, and diabetes, each successive generation was objectively worse at the same age than the one before it. The trend, which they call 'generational health drift,' has continued despite declining smoking rates, rising education levels, and improving material circumstances. For Indian Americans who moved to the West for a better life, the finding raises an uncomfortable question: if the destination country's health trajectory is pointing downward, what exactly are you raising your children into?"
art2_slug = make_slug("generational-health-drift-each-generation-sicker-indian-children-america")
art2_category = "lifestyle-health"

art2_body = """The story that Indian immigrants tell themselves — the story that justified the visa lottery, the H-1B queue, the years of separation from parents, the rented apartments in suburbs you had never heard of — is that you came to a country where your children would have a better life. Better schools. Better opportunities. Better health. Better everything.

A systematic review from three of Britain's leading universities has just confirmed something that epidemiologists have suspected for years but have struggled to prove at scale: the trajectory of health in the Western world is not going up. It is going down. And it has been going down for every generation born since 1946.

## The Study

The review, published in the journal Population Studies in May 2026, was led by Laura Gimeno at the Centre for Longitudinal Studies, University College London, with co-authors from King's College London and the University of Oxford. The team examined 51 peer-reviewed studies that compared health outcomes across six British birth cohort datasets — following babies born in 1946, 1958, 1970, 1989-90, 1991-92, and 2000-02.

The cohorts together comprised over 88,500 individuals. The methodological strength of these datasets is almost unique in global health research: they followed the same people from birth for decades, measuring health outcomes at consistent ages, using validated instruments that allow direct comparison across generations.

The researchers compared health measures from people born in different years at the point they reached similar ages. A person born in 1946 was compared to a person born in 1958 at the same age. A person born in 1958 was compared to a person born in 1970 at the same age. And so on.

The pattern was consistent and disquieting.

## The Findings

**Obesity**: Every successive generation was heavier at the same age than the generation before it. This was the most consistently observed trend across all cohorts and all studies.

**Mental health**: Depression and anxiety symptoms — measured using validated self-report scales, not diagnostic labels — were higher in each successive generation at the same age. Gen X reported worse mental health than Baby Boomers. Millennials reported worse mental health than Gen X.

**Diabetes**: Evidence for generational worsening was found specifically in comparisons between Generation X and Baby Boomers, using both self-reported diagnoses and objectively measured biomarkers.

The researchers found "little suggestion of improvements in health for people born since 1946." The worsening was observed despite three factors that should have produced improvement: smoking rates fell dramatically across these decades, educational attainment rose consistently, and material living standards improved in early life.

"If more recent generations are 'drifting' backwards in health," lead author Laura Gimeno said, "it implies that society is not reaching the biological limits of health improvement. Instead, we're seeing the consequences of preventable social and environmental exposures that have shaped population health over time and across generations."

## Why This Is Not Just a Measurement Artefact

The researchers anticipated the most obvious objection: that the worsening trends simply reflect better diagnosis. More people are diagnosed with depression today because depression is more widely recognised. More people are classified as obese because we measure BMI more routinely.

The paper addresses this directly. The obesity comparisons are based on measured weight — a number on a scale, not a clinical diagnosis. You cannot argue that people were secretly just as heavy in 1960 but nobody noticed. The mental health comparisons used self-reported symptom scales, not diagnostic categories, and the measurement tools have been extensively validated for cross-cohort consistency. The diabetes comparisons included objective biomarkers — blood glucose and HbA1c levels — not just self-reports.

The consistency across both self-reported and objectively measured outcomes makes it unlikely that changes in measurement or diagnostic practice explain the pattern. The researchers believe the most plausible explanation is a genuine increase in poor health, driven by changing exposure to social and environmental risk factors — what they call "obesogenic environments" — throughout people's lives.

## The Immigrant Health Paradox — and Its Expiry Date

There is a well-documented phenomenon in epidemiology called the "healthy immigrant effect." When people migrate from lower-income countries to higher-income countries, they typically arrive in better health than the native-born population of the destination country. Indian immigrants to the United States are among the clearest examples: first-generation Indian Americans have lower rates of obesity, lower smoking rates, and often better cardiovascular markers than the average American.

The reasons are intuitive. The people who migrate are not a random sample of the origin country's population. They are, on average, younger, better educated, more ambitious, and more health-conscious than both the general population they left behind and the general population of the country they enter. They also bring dietary habits, cultural practices, and activity patterns that are often healthier than those of the destination country.

But the healthy immigrant effect has an expiry date.

Within one generation — sometimes within a decade — the health advantages of immigrant populations begin to erode. The children of Indian immigrants in America eat more processed food, exercise less, experience more academic stress, sleep worse, and spend more time on screens than their parents did at the same age. They also live in what the UCL researchers now confirm is an environment where each successive generation is getting objectively sicker.

This creates a compounding problem. The Indian American child is absorbing the worst of both worlds: the health-deteriorating trends of the American environment — ultra-processed food, sedentary lifestyles, social media-driven anxiety — plus the distinctly Indian pressures that remain culturally persistent: academic pressure that crowds out sleep and physical activity, carbohydrate-heavy diets that persist from parental cooking habits, and a cultural stigma around mental health that delays diagnosis and treatment.

Nobody is measuring this convergence in real time. There is no longitudinal cohort study tracking the health trajectories of second-generation Indian Americans the way the British birth cohort studies track Britons. The data gap is itself a health risk — because without measurement, there is no intervention, and without intervention, the generational health drift applies to your children just as it applies to everyone else's.

## The Uncomfortable Arithmetic

The British study found that each generation born since 1946 spent more years in poor health than the generation before it. Healthy life expectancy in the UK — the number of years a person can expect to live in good health — has actually fallen in recent years, to 60.7 years for men and 60.9 years for women.

This means that a British man born in 2000 can expect, on average, to spend his last two decades living with chronic illness. His grandfather, born in 1946, had better odds.

The American data is different in detail but consistent in direction. Life expectancy in the United States has declined in recent years, driven by rising rates of obesity, diabetes, mental illness, drug overdoses, and what epidemiologists call "deaths of despair." The United States now has the lowest life expectancy of any wealthy nation.

Indian Americans are partially shielded by their socioeconomic position — they are among the highest-earning ethnic groups in America — and by the residual dietary and lifestyle benefits of first-generation immigrant culture. But socioeconomic advantage does not override biological environment. Wealthy Americans are healthier than poor Americans, but wealthy Americans in 2026 are less healthy than wealthy Americans in 1990. The tide is going out for everyone.

## What the Drift Means for Your Family

The practical implications for Indian American families are specific and uncomfortable:

**Your children are not growing up in the health environment you think they are.** The implicit promise of immigration — that the destination country offers a healthier life — was true when the destination country's health trajectory was improving. It is no longer improving. Your children are growing up in a country where the baseline health of each generation is worse than the one before it. The schools are better. The opportunities are greater. The food is worse. The mental health support is better-resourced but more needed. The net health effect is negative and getting more negative.

**The Indian diet is not automatically protective for the second generation.** First-generation Indian immigrants eat dal, roti, sabzi, and rice cooked from scratch. Their children eat the same dinner but add breakfast cereal, school cafeteria food, vending machine snacks, Chick-fil-A on weekends, and whatever DoorDash delivers during college. The protective elements of the Indian diet are diluted by the addition of American processed food — they are not replaced by it but supplemented, which means total caloric intake rises even as dietary quality falls.

**Academic pressure crowds out protective behaviours.** The cultural emphasis on academic achievement — SAT prep, AP classes, extracurricular padding for college applications — directly competes with the behaviours that protect against generational health drift: sleep, physical activity, unstructured outdoor time, and social connection. An Indian American teenager who studies until midnight, wakes at 6 AM, eats a granola bar in the car, sits through eight hours of school, does three hours of homework, and then studies for the SAT is exhibiting the exact behavioural profile — high sedentary time, poor sleep, high stress, processed food — that the British data associates with each generation's decline.

**Mental health stigma accelerates the drift.** The UCL study found that mental health deterioration was among the most consistent generational trends. Indian American families are simultaneously more exposed to mental health stressors (immigration trauma, identity conflict, high-achievement pressure, racial microaggressions) and less likely to seek treatment (cultural stigma, family reputation concerns, "log kya kahenge"). This means the generational drift in mental health may be accelerated in Indian American children compared to the general population.

## What You Can Do

The generational health drift is a population-level phenomenon. You cannot single-handedly reverse it for your family. But you can refuse to passively participate in it.

**Measure.** Get your children's metabolic markers tested — not just weight and height, but fasting glucose, HbA1c, lipid panel, vitamin D, and inflammatory markers. Indian children are at elevated risk for insulin resistance and early metabolic syndrome. Catching it at 14 is different from catching it at 40.

**Protect sleep.** The single most consistently protective behaviour across the health drift literature is adequate sleep. Indian American teenagers sleep less than almost any demographic — between academic pressure, screen time, and parental expectations to be "up early and productive." Eight hours minimum. Nine is better. No negotiation.

**Cook.** The protective effect of the Indian diet is not in the spices or the vegetarianism. It is in the cooking — the act of preparing food from unprocessed ingredients. Every meal cooked from scratch is a meal that does not contain the additives, preservatives, seed oils, and refined sugars that the generational drift literature implicates. Your mother's dal chawal is a metabolic intervention. Treat it like one.

**Permit physical activity without academic justification.** Indian American parents are more likely to support sports if they help a college application than if they simply make the child healthier. This calculus is backwards. The child who plays pickup basketball three times a week and does not list it on a resume is making a better health investment than the child who does robotics club for the application and sits for twelve hours a day.

**Talk about mental health.** Not once. Not as a crisis intervention. Regularly, casually, as part of how your family works. Normalise therapy. Normalise saying you are struggling. Normalise the idea that a generation facing worse mental health outcomes than any generation before it might need more support, not less.

## The Uncomfortable Conclusion

The generational health drift is not a failure of medicine. Medicine has improved enormously since 1946. It is a failure of environment — of the food systems, built environments, social structures, and cultural pressures that shape health outcomes long before anyone visits a doctor.

Indian Americans moved to the West for better lives. In many ways, they got them. But the health trajectory of the destination country is now pointing in the wrong direction, and the children of immigrants are not exempt from the drift. They are subject to it — and to the additional pressures of bicultural identity, academic intensity, and dietary transition that make the drift potentially faster and steeper.

The British study cannot tell you what to do about this. It can only tell you that the trend is real, that it has been real for eighty years, and that every generation born since World War II has been measurably sicker at the same age than the one before it.

What you do with that knowledge — for your children, for your family, for your community — is the only question that matters now."""

art2_sources = [
    "https://doi.org/10.1080/00324728.2026.2652038",
    "https://www.news-medical.net/news/20260522/Research-show-worsening-health-trends-for-post-1946-generations.aspx",
    "https://britbrief.co.uk/health/nhs/uk-youth-health-worse-than-previous-generations-study.html",
]

print("\n=== Article 2: Generational Health Drift / Each Generation Sicker / Indian Children in America ===")
print(f"  Word count: {len(art2_body.split())}")

art2_image = fetch_pexels_image("diverse children playing outside sunlight healthy")
if art2_image:
    print(f"  📸 Pexels image: {art2_image['pexels_id']} by {art2_image['photographer']}")

result2 = sb_post("p2_articles", {
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
    "tags": ["generational health drift", "obesity", "mental health", "diabetes", "UK study", "British birth cohorts", "UCL", "King's College London", "Oxford", "Population Studies", "Indian American", "NRI", "children", "immigration", "healthy immigrant effect", "processed food", "academic pressure", "sleep", "second generation", "metabolic syndrome", "life expectancy", "preventive health", "Western lifestyle", "environment"],
    "vertical": "diaspora",
    "urgency": "standard",
    "diaspora_angle": "UCL/King's College/Oxford systematic review (Population Studies, May 2026, 51 studies, 88,500 Britons, birth cohorts 1946-2002): Every generation since WWII is measurably sicker at the same age than the one before it — obesity, mental health, diabetes all worsening despite declining smoking, rising education, and improved material circumstances. Researchers call it 'generational health drift' and say it reflects preventable environmental exposures. NRI angle: Indian immigrants arrive with the 'healthy immigrant effect' but their children absorb the worst of both worlds — American processed food, sedentary lifestyles, and social media anxiety PLUS Indian academic pressure, carb-heavy dietary transition, and mental health stigma. The destination country's health trajectory is now pointing downward. No longitudinal cohort study is tracking second-generation Indian American health.",
    "word_count": len(art2_body.split()),
    "image_url": art2_image["url"] if art2_image else None,
    "image_caption": f"Photo by {art2_image['photographer']} via Pexels" if art2_image else None,
})
if result2:
    print(f"  ✓ Published: {art2_id}")
else:
    print("  ✗ Failed or duplicate")

if result2 and art2_image:
    patch_r = requests.patch(
        f"{SB_URL}/rest/v1/p2_articles?id=eq.{art2_id}",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json={"image_url": art2_image["url"], "image_caption": f"Photo by {art2_image['photographer']} via Pexels"},
        timeout=10
    )
    print(f"  Image PATCH: {patch_r.status_code}")


# ── Git commit & push ──
print("\n=== Git push ===")
os.chdir(str(Path.home() / "workspace/the-videshi-news"))
subprocess.run(["git", "add", "-A"], capture_output=True)
commit_msg = "lifestyle: exercise brain SF1 neurons + generational health drift (2026-05-25 19:00 PDT)"
subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True)
push = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=30)
print(f"  Push: {'OK' if push.returncode == 0 else push.stderr[:200]}")

print("\n=== Done ===")
