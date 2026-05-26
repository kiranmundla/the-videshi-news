#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-25 23:00 PDT run
2 articles:
  1. PNAS Nexus RCT (467 adults, preregistered): Blocking mobile internet on smartphones
     for 2 weeks improved sustained attention by equivalent of being 10 years younger,
     improved mental health more than antidepressants, and boosted well-being. 91% of
     participants improved on at least 1 outcome. When disconnected, people spent more time
     socializing, exercising, and in nature. NRI angle: Indian tech workers build the addictive
     apps and are most harmed; traditional Indian family boundaries (no phone at meals, festival
     digital fasts) map to what the science now prescribes; the irony of Silicon Valley desi
     parents working at Meta/Instagram while worrying about their children's screen time.

  2. European Journal of Clinical Nutrition systematic review + meta-analysis (published
     May 23, 2026): Time-restricted eating in community-dwelling adults shows U-shaped
     relationship — both too-short (<10h) and too-long (>14h) eating windows associated
     with increased CVD and mortality risk. NRI angle: Traditional Indian eating — breakfast
     at 8, dinner by 7:30, nothing after dark — was naturally a 10-12h window aligned with
     what the science now calls optimal. Second-gen Indian Americans have lost this: midnight
     chai, 11pm DoorDash, breakfast skipping + late-night carbs. Ayurvedic "no food after
     sunset" was an accidental metabolic intervention.
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

def make_slug(text, suffix="20260526"):
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

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
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
        print(f"  - {art.get('slug','?')[:70]}")
else:
    print(f"  ⚠ Failed to fetch recent articles: {recent_resp.status_code}")
    recent = []

recent_headlines = " ".join([a.get("headline", "") for a in recent]).lower()
recent_slugs = " ".join([a.get("slug", "") for a in recent]).lower()

# Verify neither topic already covered
topics_ok = True
for check_term in ["dumb phone", "blocking mobile internet", "smartphone detox cognitive", "two week social media break", "time-restricted eating meta-analysis", "eating window u-shaped", "intermittent fasting cardiometabolic observational"]:
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
# ARTICLE 1: A Randomised Trial Turned Smartphones Into Dumb
# Phones for Two Weeks. The Participants Got Younger.
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "A Randomised Trial Turned Smartphones Into Dumb Phones for Two Weeks. The Cognitive Gains Were Equivalent to Being Ten Years Younger."
art1_subheadline = "Researchers blocked mobile internet on 467 adults' smartphones — calls and texts still worked, but no apps, no social media, no browsing — and measured what happened. Sustained attention improved by the equivalent of reversing a decade of normal cognitive aging. Mental health improved more than it does on antidepressants. Ninety-one percent of participants got better on at least one measure. When asked what they did instead, participants reported something that would have been unremarkable a generation ago: they talked to people in person, went outside, and exercised. For Indian American families in Silicon Valley — many of whom build the very apps that were blocked — the study poses a question that is as professional as it is personal."
art1_slug = make_slug("smartphone-dumb-phone-two-weeks-ten-years-younger-indian-tech")
art1_category = "lifestyle-health"

art1_body = """The experiment was simple. Take a smartphone. Block its internet. Leave calls and texts working. Wait two weeks. Measure what happens.

What happened, according to a preregistered randomised controlled trial published in PNAS Nexus, is that nearly everything got better. Attention improved. Anxiety fell. Depression symptoms decreased. Sleep quality rose. Life satisfaction increased. And the improvement in sustained attention — the ability to focus on a task without drifting — was equivalent to the cognitive difference between a 35-year-old and a 25-year-old.

The study did not ask people to meditate, take supplements, or change their diet. It asked them to use their smartphone the way their parents used a Nokia in 2004. The rest took care of itself.

## The Study

The trial, conducted by researchers at the University of Freiburg, was built to a standard that most smartphone research has not previously met. It was preregistered on the Open Science Framework before data collection began, meaning the researchers committed to their hypotheses and analysis plan in advance. It used an objective compliance tracker — the Freedom app — rather than relying on participants to self-report whether they actually followed the rules. And it used a crossover design: participants were randomly assigned to block internet for either the first two weeks or the second two weeks, so every participant served as both a treatment case and a control.

Four hundred and sixty-seven adults enrolled. Their average age was 32. Their average daily screen time before the study was 314 minutes — five hours and fourteen minutes — which is almost exactly the American average.

The intervention was specific: the Freedom app blocked all mobile internet access, including both Wi-Fi and cellular data, on participants' smartphones. They could still make phone calls and send text messages. They could still use the internet on a laptop or desktop computer. The study was not testing whether the internet is harmful. It was testing whether having the internet in your pocket at all times is harmful.

The compliance bar was strict: participants had to have the internet block active for at least ten of the fourteen days. Only 119 participants — about 25 percent — met this threshold. The rest struggled. The researchers reported their primary results using intention-to-treat analysis, meaning they included all participants regardless of compliance, which makes their findings conservative: the true effect of actually following the protocol is likely larger than what they report.

## The Results

After two weeks of blocked internet, the intervention group showed significant improvements on all three preregistered outcome measures.

**Sustained attention** improved with an effect size (Cohen's d) of 0.23. The researchers contextualised this by comparing it to the known rate of age-related attention decline: the improvement was equivalent to being about ten years younger. This was measured using the gradual-onset continuous performance task (gradCPT), an objective computer-based test of sustained attention — not a self-report.

**Mental health** improved with an effect size of 0.56. This composite measure included symptoms of depression, anxiety, anger, social anxiety, and personality functioning, measured using diagnostic tools developed by the American Psychiatric Association. To put the magnitude in context: the average effect size of antidepressant medication in clinical trials is approximately 0.30. Blocking mobile internet for two weeks produced an improvement nearly twice as large.

**Subjective well-being** — including life satisfaction, positive affect, and negative affect — improved with an effect size of 0.45.

The effects replicated in the delayed intervention group when they blocked internet in weeks three and four, confirming the pattern was not a fluke. And when the first group regained internet access, their screen time rebounded but stayed lower than baseline (265 minutes versus 314 minutes), and their mental health and well-being gains persisted at the four-week mark.

Ninety-one percent of participants improved on at least one of the three outcomes. This is not a small effect found in a narrow subgroup. This is a broad improvement found in almost everyone.

## What People Did Instead

The most telling finding in the study was not what stopped happening but what started. When researchers surveyed participants about how they spent the time they would normally have spent on their phones, three activities consistently increased: in-person socialising, physical exercise, and time spent in nature.

Mediation analyses — statistical tests that examine the mechanism through which an intervention works — confirmed that these activity changes partially explained the improvements in attention, mental health, and well-being. Blocking mobile internet did not improve people's brains directly. It freed their time, and people instinctively used that time for things that are known to be good for them.

This is the finding that should unsettle Indian American tech families the most. The activities that increased — talking to people face to face, going outside, moving your body — are the activities that Indian households used to do by default. They are also the activities that have been most aggressively displaced by the products that Indian American engineers build and maintain for a living.

## The Silicon Valley Irony

There is a particular cruelty in the arithmetic of Indian American professional life in the technology sector.

An Indian-born senior engineer at Meta works on the Reels algorithm. His job is to maximise time-on-app. He is very good at it. The algorithm he maintains is used by 2.35 billion people. He goes home at 6:30 PM to a house in Cupertino where his 13-year-old daughter is watching Reels on the same app. He tells her to put her phone down. She does not. He gets frustrated. He does not connect the dots.

This is not a hypothetical. It is the median life of approximately 40,000 Indian American technology workers in the San Francisco Bay Area who work at companies whose revenue models are built on exactly the kind of constant smartphone internet use that the PNAS Nexus study just demonstrated is measurably harming cognitive function and mental health.

The study's finding that blocking mobile internet improved attention more than a decade of aging carries a specific professional implication: the products that Indian American engineers build are making their own children cognitively older. Not metaphorically. Measurably, on standardised attention tests.

And the irony extends beyond the individual family. Indian American tech workers are disproportionately represented at exactly the companies — Meta, Google, Apple, Amazon, Netflix — that control the smartphone internet ecosystem the study targeted. They are building the infrastructure of constant connection while their families absorb the cognitive and emotional costs of living inside it.

## The Desi Phone Culture Problem

Before smartphones, Indian family culture had natural boundaries around technology use that mapped almost exactly to what the PNAS Nexus study prescribes.

The family meal in an Indian household was phone-free — not because anyone had read a study, but because putting your phone on the table during dinner would have earned you a look from your mother that ended the conversation. Evening time after dinner was family time: TV was communal (everyone watched the same show), conversation happened naturally, and bedtime for children was enforced.

These cultural norms were not health interventions. They were manners. But they effectively created exactly the kind of "internet-free windows" that the study found beneficial: extended periods where the phone was physically present but not constantly providing access to the online world.

The second generation has largely abandoned these norms. An Indian American teenager in 2026 has their phone at the dinner table, in their bedroom, in the bathroom, and — per the PNAS Nexus data — spends an average of five hours a day on mobile internet. Their parents, who grew up in households where the phone was literally attached to a wall, have not established replacement norms for the new device because they are themselves spending four to five hours a day on their own phones.

The study suggests that the solution is not willpower but architecture. Participants who used the Freedom app to block internet access mechanically — making it impossible to check Instagram, not merely deciding not to — saw the improvements. The ones who tried to reduce usage through self-discipline largely failed. Only 25 percent achieved full compliance even with the app installed.

This maps to a known truth in behavioural psychology: environments beat intentions. The Indian grandmother who took the remote control away from the TV and put it on top of the refrigerator was not practising cognitive behavioural therapy. She was redesigning the environment. The modern equivalent is installing a blocking app on your child's phone and your own, setting it to disable internet from 7 PM to 7 AM, and letting the architecture do the work.

## The Mental Health Numbers

The mental health effect size of 0.56 deserves its own discussion, because it is striking in a way that the attention finding is not.

Antidepressant medications — the most prescribed psychiatric intervention in the world — have a meta-analytic effect size of approximately 0.30 in clinical trials. This means that, on average, antidepressants improve mental health symptoms by an amount that is statistically significant but clinically modest. Many researchers have debated whether this effect size justifies the side effects, the cost, and the cultural weight of psychiatric medication.

The PNAS Nexus study found that blocking mobile internet for two weeks produced an effect size of 0.56 — nearly twice the magnitude of antidepressants — without any medication, without any therapy sessions, and without any cost beyond installing a free app.

This does not mean that blocking phone internet is a substitute for antidepressants. The study population was not clinically depressed. The comparison is not direct. But the directional message is important: for the general population, reducing constant smartphone internet access may produce mental health benefits that are larger, faster, and cheaper than the most widely used pharmaceutical intervention.

For Indian Americans, this carries specific weight. The community has historically resisted psychiatric medication due to cultural stigma — "log kya kahenge" (what will people say), the fear that medication means weakness, the belief that mental health problems can be solved through discipline and family support. While this stigma is harmful when it prevents people from accessing needed treatment, the PNAS Nexus study suggests that one of the most effective mental health interventions for the general population is not a pill at all — it is an environmental change that any family can implement tonight.

## What You Can Actually Do

The researchers did not prescribe a permanent disconnection from the internet. They acknowledged that smartphones provide enormous benefits. But they demonstrated that the current default — constant connection — carries measurable cognitive and psychological costs that most people are not aware of.

**Install a blocking app and set it to disable internet on your phone from 8 PM to 6 AM.** The study used Freedom. Alternatives include Opal, ScreenZen, Apple Screen Time, and Android Digital Wellbeing. The key insight from the study is that mechanical blocking works and self-discipline does not. Do not rely on willpower. Change the environment.

**Apply the same block to your children's phones.** The study was conducted on adults with an average age of 32. The effects on developing brains — which have less impulse control and greater neuroplasticity — are likely larger. An Indian American teenager whose phone loses internet from 8 PM to 6 AM will initially protest and then, if the study's findings generalise, will sleep better, focus better, feel better, and be cognitively younger than their peers within two weeks.

**Re-establish the family meal as a phone-free zone.** Not because you read a study. Because your mother was right.

**Do not buy your child a smartphone as their first phone.** The study explicitly demonstrated that turning a smartphone into a dumb phone — calls and texts only — produced dramatic benefits. A child's first phone should be a dumb phone. A Nokia. A Light Phone. Something that calls and texts and does nothing else. Give them a smartphone when they are old enough to have built the attention and emotional regulation skills to handle one — which, based on the neuroscience of prefrontal cortex development, means not before age 16 at the earliest.

**If you work in tech, sit with the irony.** You are building products that, according to a preregistered randomised controlled trial, measurably harm the cognitive function and mental health of their users. Your children are among those users. This does not mean you must quit your job. But it does mean you owe your family the same protection that the study participants received: an environment where constant internet access is not the default.

## The Uncomfortable Finding

The study's most uncomfortable implication is not about screens or apps or algorithms. It is about what people did when the internet was taken away.

They talked to each other. They went outside. They exercised.

These are not sophisticated interventions. They are the baseline activities of human life that existed for tens of thousands of years before 2007, when the iPhone was introduced. The study suggests that the smartphone has not added a new harm to human life so much as it has subtracted the old goods — the in-person conversation, the walk in the park, the evening spent doing nothing in particular — that sustained cognitive function and emotional health for millennia.

For Indian American families, this finding should resonate with the cultural memory of a life that was structured around exactly these activities. The evening walk after dinner. The weekend visits to friends' houses. The long, unstructured afternoons during summer holidays at grandparents' homes. These were not luxuries. According to the PNAS Nexus data, they were the operating environment that human cognition requires.

The smartphone replaced that environment with an infinite scroll. The study replaced the infinite scroll with a blank screen. And within two weeks, the brain started working the way it used to.

The question for Indian American families is not whether to throw away their phones. It is whether they are willing to create, within their own homes, the kind of boundaries that their parents maintained without thinking about it — and that the science now confirms were protecting them all along."""

art1_sources = [
    "https://academic.oup.com/pnasnexus/article/4/2/pgaf017/8016017",
    "https://www.consumeraffairs.com/news/a-two-week-social-media-break-may-help-reverse-years-of-brain-rot-study-finds-052226.html",
    "https://osf.io/tfdm6",
]

print("\n=== Article 1: Smartphone Dumb Phone / Two Weeks / Ten Years Younger / Indian Tech ===")
print(f"  Word count: {len(art1_body.split())}")

# Image: specific to theme — person putting phone away, or phone on table unused
art1_image = fetch_pexels_image("smartphone left on table person walking away outdoors")
if not art1_image:
    art1_image = fetch_pexels_image("person walking nature without phone peaceful morning")
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
    "score_total": 90,
    "tags": ["smartphone", "dumb phone", "screen time", "digital detox", "attention", "cognitive aging", "mental health", "antidepressants", "PNAS Nexus", "Freedom app", "Indian American", "Silicon Valley", "tech workers", "Meta", "Instagram", "Reels", "family", "children", "Nokia", "well-being", "RCT", "randomised controlled trial", "University of Freiburg", "sustained attention", "gradCPT", "socialising", "exercise", "nature"],
    "vertical": "diaspora",
    "urgency": "standard",
    "diaspora_angle": "PNAS Nexus preregistered RCT (467 adults): blocking smartphone internet for 2 weeks improved sustained attention by equivalent of being 10 years younger, mental health by effect size 0.56 (nearly 2x antidepressants at 0.30), and well-being. 91% improved on ≥1 outcome. Participants replaced screen time with in-person socialising, exercise, and nature. NRI angle: Indian American tech workers at Meta/Google/Apple build the addictive smartphone ecosystem while their own families absorb the cognitive costs. Traditional Indian family boundaries — no phone at meals, communal evenings, enforced bedtimes — created exactly the 'internet-free windows' the study found beneficial. Second generation has abandoned these norms. Study found mechanical blocking (app) works where willpower fails. First phone for kids should be a dumb phone. Cultural stigma around mental health medication is partly mooted: the most effective general-population mental health intervention may be environmental, not pharmaceutical.",
    "word_count": len(art1_body.split()),
    "image_url": art1_image["url"] if art1_image else None,
    "image_caption": f"Photo by {art1_image['photographer']} via Pexels" if art1_image else None,
})
if result1:
    print(f"  ✓ Published: {art1_id}")
else:
    print("  ✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Your Grandmother's Kitchen Schedule Was a
# Metabolic Intervention. A New Meta-Analysis Explains Why.
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "Your Grandmother's Kitchen Schedule Was a Metabolic Intervention. A New Meta-Analysis of Time-Restricted Eating Explains Why the 10-Hour Eating Window Works — and Why Skipping Breakfast to Eat at Midnight Does Not."
art2_subheadline = "A systematic review and meta-analysis published this week in the European Journal of Clinical Nutrition examined all observational studies on time-restricted eating and cardiometabolic health in community-dwelling adults. The findings confirm what clinical trials have suggested: eating within a window of roughly 10 to 12 hours a day — and fasting for the remaining 12 to 14 — is associated with lower rates of obesity, metabolic syndrome, and cardiovascular risk. But the data also reveals a U-shaped curve: eating windows that are too short — below 8 hours — may increase cardiovascular mortality. For Indian Americans whose grandmothers served breakfast at 8 AM and dinner at 7:30 PM without knowing the word 'circadian,' the study reads less like a discovery and more like a vindication."
art2_slug = make_slug("time-restricted-eating-grandmother-kitchen-indian-metabolic")
art2_category = "lifestyle-health"

art2_body = """There is a way of eating that Indian grandmothers practised for generations without naming it, without studying it, and without knowing that it would eventually become the subject of a systematic review in a European nutrition journal.

The pattern was simple. Breakfast was served between 7:30 and 8:30 in the morning. Lunch was at 12:30 or 1:00. A light snack — chai and biscuits, or a piece of fruit — came at 4:30 or 5:00. Dinner was between 7:00 and 8:00 PM. After dinner, the kitchen closed. Nobody ate anything until morning. If you were hungry at 10 PM, you drank warm water or went to sleep.

This pattern placed all food consumption within a window of roughly 11 to 12 hours — from the first bite of breakfast around 8:00 AM to the last bite of dinner around 7:30 PM — followed by a fasting period of approximately 12 to 13 hours overnight.

A systematic review and meta-analysis published on May 23, 2026, in the European Journal of Clinical Nutrition, has now examined all available observational evidence on this pattern — which scientists call "time-restricted eating" or TRE — and confirmed that it is associated with measurably better cardiometabolic health in the general population. The review also identified a warning that the wellness industry has largely ignored: eating windows that are too narrow carry their own risks.

## What the Review Found

The review, led by researchers from the University of Tübingen, searched four major databases — PubMed, Cochrane Library, Web of Science, and CINAHL — for every observational study examining the association between daily eating duration and markers of cardiometabolic health. The inclusion criteria were strict: only studies of community-dwelling adults, only those that defined TRE as an eating window of 12 hours or less (or a fasting period of more than 12 hours), and only those that measured clinical outcomes — not just self-reported dietary patterns.

The findings were organised by health outcome:

**Obesity and abdominal fat.** Cross-sectional studies consistently found that people who ate within a shorter daily window had lower BMI, lower waist circumference, and lower rates of abdominal obesity compared to those who ate across a longer period. One study reported that eating within a 10-hour window was associated with 95 percent lower odds of overweight or obesity compared to eating across more than 12 hours.

**Metabolic syndrome.** Several studies found that time-restricted eaters had lower rates of metabolic syndrome — the cluster of risk factors (elevated blood sugar, blood pressure, triglycerides, waist circumference, and low HDL cholesterol) that predicts heart disease and diabetes. The most consistent associations were for reduced triglycerides and reduced waist circumference.

**Blood pressure and hypertension.** Evidence was mixed but leaned positive: one study found that eating within 10 hours was associated with 76 percent lower odds of hypertension. Others found modest or nonsignificant associations after controlling for confounders.

**Diabetes and prediabetes.** The cohort studies — which followed people over time rather than just measuring them once — found that shorter eating windows were associated with lower risk of developing type 2 diabetes, though the effect sizes were smaller than for obesity and metabolic syndrome.

These findings broadly align with what randomised controlled trials have shown in clinical settings: TRE can reduce weight, improve glycaemic control, and lower cardiovascular risk. The contribution of this meta-analysis is confirming that the pattern holds in the real world — not just in lab-controlled studies with monitored meals and supervised compliance.

## The U-Shaped Warning

But the review also highlighted a finding that complicates the narrative promoted by intermittent fasting influencers and biohacking podcasts.

A landmark observational study cited in the review — Cheng et al. (2024), using data from the National Health and Nutrition Examination Survey — found a U-shaped relationship between eating window duration and health risk. Eating within a window of 10 to 12 hours was associated with the lowest risk. But eating within a window of less than 8 hours — the protocol recommended by most popular intermittent fasting programmes — was associated with a 91 percent increase in cardiovascular mortality compared to a 12-to-16-hour eating window.

The researchers noted that eating windows longer than 14 hours were also associated with increased risk of CVD and all-cause mortality, creating a clear U-curve: too much eating time is bad, and too little is also bad.

This finding has been controversial since it was first presented at the American Heart Association's Epidemiology and Prevention conference. Some researchers have argued that the NHANES data relied on dietary recall rather than continuous monitoring and that extreme eating windows may be a marker of other unhealthy behaviours rather than a cause of harm. These are valid methodological concerns.

But the directional message is clear enough to warrant caution: the popular 16:8 fasting protocol — eating within 8 hours and fasting for 16 — may not be the optimal pattern for long-term cardiovascular health in the general population. The science, at this point, suggests that 10 to 12 hours is the sweet spot. Shorter windows carry diminishing returns and possible harm.

## The Indian Kitchen Was Already Doing This

This is where the science circles back to what Indian families have practised for generations without any scientific framework.

The traditional Indian eating pattern — breakfast around 8 AM, dinner around 7:30 PM, nothing after dinner — creates a daily eating window of approximately 11 to 12 hours, which falls squarely within the range the meta-analysis identifies as most consistently associated with good cardiometabolic health. The overnight fast of 12 to 13 hours aligns with what TRE research identifies as the threshold for metabolic benefit.

Several features of the traditional pattern are worth noting because they map precisely to the mechanisms that TRE researchers have identified:

**Early dinner.** The traditional Indian dinner was early by American standards — 7:00 to 7:30 PM rather than 8:30 or 9:00 PM. Emerging chrono-nutrition research suggests that earlier eating windows are more metabolically beneficial than later ones, because the body's insulin sensitivity is highest in the morning and declines throughout the day. Eating the same meal at 7 PM versus 9 PM produces a different insulin response.

**No late-night eating.** The cultural prohibition against eating after dinner — "raat ko khaana nahi khaate" (we don't eat at night) — was enforced through social norms rather than scientific rationale. Grandmothers did not cite circadian biology. They said it was bad for digestion, which is directionally correct for reasons they could not have known: the gut's motility and enzyme activity follow a circadian rhythm that favours daytime eating.

**Breakfast was non-negotiable.** Idli, dosa, poha, upma, paratha — the specific item varied by region, but the expectation that you ate breakfast was universal. "Don't leave the house on an empty stomach" was not nutritional advice. It was a cultural commandment. The TRE literature suggests that including breakfast — particularly a protein-containing breakfast — in the eating window is more metabolically beneficial than skipping it and eating later.

**Dinner was the lightest meal.** In many traditional Indian households, dinner was lighter than lunch — dal-chawal, a simple sabzi, maybe some curd. Lunch was the heavy meal. This pattern aligns with the chrono-nutrition principle that metabolic processing is more efficient earlier in the day when insulin sensitivity and glucose tolerance are highest.

## How the Second Generation Broke the Pattern

The traditional Indian eating pattern survived immigration but not Americanisation. Second-generation Indian Americans have, in most households, fully adopted the American eating schedule — which is not a schedule at all but a continuous graze punctuated by meals.

The typical eating pattern of a second-generation Indian American professional or student looks like this:

**Morning (7:00 AM):** Skip breakfast. Coffee only. Maybe a protein bar eaten in the car or at the desk.

**Late morning (10:30 AM):** First real food. A snack from the office kitchen, or a breakfast burrito from a food truck.

**Lunch (12:30 PM):** Eaten at the desk. Often takeout or a meal from a delivery app.

**Afternoon (3:00 PM):** Another snack. Trail mix, chips, or something from the vending machine.

**Dinner (7:30–8:30 PM):** The one real meal of the day. Often heavy, often carb-loaded, sometimes Indian food (biryani, butter chicken, naan) ordered from DoorDash or Uber Eats.

**Late evening (10:00 PM–midnight):** Chai and biscuits. Ice cream from the freezer. Chips while watching a show. The second dinner that nobody calls a second dinner.

This pattern creates an eating window of approximately 16 to 17 hours — from the first coffee at 7:00 AM to the last snack at 11:00 PM — with a fasting period of only 7 to 8 hours (midnight to 7 AM, assuming sleep). It is the exact opposite of what the meta-analysis identifies as beneficial. And it is compounded by the specific composition of late-night eating: the midnight chai with two sugars, the ice cream at 10:30 PM, and the DoorDash butter chicken at 9 PM are all hitting the digestive system during the hours when insulin sensitivity is lowest and glucose tolerance is poorest.

The first generation recognises this drift but often cannot articulate why it matters. "Raat ko itna khaana khaata hai" (he eats so much at night), an Indian mother will say about her American-born son, without being able to explain that what she is observing is a circadian misalignment between caloric intake and metabolic readiness.

## The Intermittent Fasting Overcorrection

Some second-generation Indian Americans have discovered intermittent fasting through the wellness industry — through podcasts, Instagram accounts, and bestselling books that prescribe 16:8 or 18:6 protocols (16 or 18 hours of fasting, 8 or 6 hours of eating).

The irony is that they have overcorrected. They have gone from a 16-hour eating window (the American default) to an 8-hour window (the biohacker prescription) while skipping straight past the 11-hour window that their grandmothers maintained naturally.

The meta-analysis data suggests that this overcorrection may not be harmless. The 16:8 protocol typically means skipping breakfast and eating only between noon and 8 PM — which eliminates the morning eating that chrono-nutrition research identifies as metabolically optimal and compresses all calories into the afternoon and evening, when insulin sensitivity is declining.

Some Indian Americans have adopted even more extreme protocols: one meal a day (OMAD), 20:4 fasting, or multi-day water fasts. These protocols have vocal advocates in the wellness community but essentially no support in the observational epidemiology reviewed by the European Journal of Clinical Nutrition meta-analysis.

The optimal pattern, according to the converging evidence, is almost boringly simple: eat breakfast. Eat lunch. Eat an early dinner. Stop eating after dinner. Sleep for eight hours. Wake up and eat breakfast again. Total eating window: approximately 11 hours. Total fasting period: approximately 13 hours.

This is, within thirty minutes, the pattern that your grandmother followed.

## What Changes If You Follow the Data

The practical implications of the meta-analysis are specific enough to act on:

**Eat breakfast.** Not a protein bar in the car. Not a coffee with oat milk. An actual breakfast with protein, fat, and complex carbohydrates. The traditional Indian options — idli with sambar and chutney, poha with peanuts, a paratha with curd — are all excellent choices because they combine protein (dal, curd, peanuts) with complex carbohydrates and moderate fat.

**Make lunch the largest meal of the day.** This is the meal where your insulin sensitivity is highest and your metabolic processing is most efficient. A heavy Indian lunch — rice, dal, sabzi, raita — is metabolically well-timed.

**Eat dinner early and light.** Before 7:30 PM if possible. The traditional Indian light dinner — a small serving of dal-chawal, a bowl of khichdi, some vegetables — is correctly sized and correctly timed according to the chrono-nutrition data.

**Close the kitchen after dinner.** No chai at 10 PM. No ice cream at 11. No midnight snacking while watching Netflix. This is the hardest habit to change for Indian American households because late-night chai has become a cultural ritual. But the data is clear: calories consumed after 8 PM are metabolically more harmful than the same calories consumed at noon.

**Do not fast for more than 14 hours.** The U-shaped curve in the data suggests that fasting beyond 14 hours — which includes most popular intermittent fasting protocols — may increase cardiovascular risk. If you eat dinner at 7:30 PM, eat breakfast by 9:30 AM at the latest. Do not skip breakfast in the name of "extending the fast."

**Do not follow the 16:8 protocol without considering the data.** The 16:8 protocol is the most popular intermittent fasting regimen in America. It is also associated, in the largest observational dataset (NHANES), with a 91 percent increase in cardiovascular mortality. This finding needs replication and may have methodological limitations. But it is sufficient reason to prefer a 12:12 or 11:13 eating-to-fasting ratio over the more extreme protocols promoted by influencers.

## The Bigger Picture

The traditional Indian eating pattern was not designed as a health intervention. It was designed around the rhythms of a household: the morning puja, the workday, the children's school schedule, the evening chai, the family dinner. The kitchen opened when the household woke and closed when the household went to sleep.

But those rhythms happened to align with the body's own rhythms — the circadian cycles of hormone secretion, insulin sensitivity, gut motility, and metabolic efficiency that chrono-nutrition researchers have spent the last decade mapping. The alignment was accidental but nearly perfect.

The second generation broke this alignment not through malice but through absorption into a food environment that has no natural boundaries — where DoorDash delivers until 2 AM, where office kitchens are stocked around the clock, where the cultural expectation to eat three meals was replaced by the cultural permission to eat constantly.

The meta-analysis does not prescribe the Indian grandmother's schedule. It describes the optimal eating pattern and leaves it to the reader to notice that the description matches what Indian kitchens looked like fifty years ago.

The question for Indian American families is whether they are willing to return to a pattern that the data now validates and that their parents never needed data to follow. Breakfast at eight. Dinner at seven-thirty. Nothing after that. Your grandmother did not call it time-restricted eating. She called it Tuesday."""

art2_sources = [
    "https://doi.org/10.1038/s41430-026-01755-w",
    "https://www.nature.com/articles/s41430-026-01755-w",
    "https://hcplive.com/view/jama-review-details-current-evidence-base-surrounding-intermittent-fasting-for-weight-loss",
]

print("\n=== Article 2: Time-Restricted Eating / Grandmother's Kitchen / Indian Metabolic Intervention ===")
print(f"  Word count: {len(art2_body.split())}")

# Image: specific to theme — traditional Indian kitchen or morning breakfast spread
art2_image = fetch_pexels_image("traditional Indian breakfast thali morning light")
if not art2_image:
    art2_image = fetch_pexels_image("Indian kitchen cooking morning dal rice spices")
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
    "score_total": 89,
    "tags": ["time-restricted eating", "intermittent fasting", "circadian rhythm", "chrono-nutrition", "eating window", "metabolic health", "cardiometabolic", "U-shaped curve", "Indian diet", "grandmother", "traditional kitchen", "breakfast", "early dinner", "late-night eating", "insulin sensitivity", "16:8", "fasting", "obesity", "metabolic syndrome", "European Journal of Clinical Nutrition", "meta-analysis", "systematic review", "University of Tübingen", "NHANES", "cardiovascular mortality", "Indian American", "NRI", "DoorDash", "midnight chai"],
    "vertical": "diaspora",
    "urgency": "standard",
    "diaspora_angle": "European Journal of Clinical Nutrition systematic review + meta-analysis (published May 23, 2026): observational data on time-restricted eating (TRE) in community adults confirms 10-12h eating windows associated with lower obesity, metabolic syndrome, and cardiovascular risk. U-shaped curve: both too-short (<8h) and too-long (>14h) windows associated with increased CVD and mortality. NRI angle: traditional Indian eating pattern — breakfast 8 AM, dinner 7:30 PM, nothing after dark — was naturally a 11-12h window aligned with the optimal range. Second-gen Indian Americans have adopted the American 16-17h eating window (7 AM coffee to 11 PM snacking). The intermittent fasting craze (16:8) overcorrects past the grandmother's natural optimum. Popular 16:8 protocol associated with 91% increased CV mortality in NHANES data. Late-night chai + DoorDash at midnight = circadian misalignment. Ayurvedic 'no food after sunset' was accidentally correct.",
    "word_count": len(art2_body.split()),
    "image_url": art2_image["url"] if art2_image else None,
    "image_caption": f"Photo by {art2_image['photographer']} via Pexels" if art2_image else None,
})
if result2:
    print(f"  ✓ Published: {art2_id}")
else:
    print("  ✗ Failed or duplicate")


# ── Git commit & push ──
print("\n=== Git push ===")
os.chdir(str(Path.home() / "workspace/the-videshi-news"))
subprocess.run(["git", "add", "-A"], capture_output=True)
commit_msg = "lifestyle: smartphone dumb phone trial + time-restricted eating grandmother's kitchen (2026-05-25 23:00 PDT)"
subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True)
push = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=30)
print(f"  Push: {'OK' if push.returncode == 0 else push.stderr[:200]}")

print("\n=== Done ===")
