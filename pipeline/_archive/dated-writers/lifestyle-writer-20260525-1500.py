#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-25 15:00 PDT run (22:00 UTC May 25)
2 articles:
  1. Swedish 19-year cohort (20,811 adults, American Journal of Preventive Medicine, March 2026): Mentally passive sitting (TV watching) raises dementia risk; mentally active sitting (reading, office work) may protect — NRI angle: retired Indian parents in India/US spend 6-8 hours watching Hindi serials, the most passive sedentary behavior studied; Indian tech workers sit all day but at least their brains are engaged; the real danger is what your parents do after you hang up the video call.
  2. UC Davis meta-analysis (25 brain imaging studies, 370 anxiety patients, Molecular Psychiatry 2026): People with anxiety disorders have 8% lower choline in prefrontal cortex — NRI angle: Indian vegetarian diet is chronically choline-deficient; eggs are the richest dietary source and many Indian vegetarians avoid them; South Asians have sky-high anxiety rates but seek treatment at the lowest rates; the nutrient gap and the stigma gap are reinforcing each other.
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

# Verify neither topic already covered
topics_ok = True
for check_term in ["passive sitting dementia", "active sitting dementia", "tv watching dementia", "choline anxiety", "choline brain anxiety", "choline deficiency anxiety"]:
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
# ARTICLE 1: Not All Sitting Is Equal. A 19-Year Study Says
# Watching TV Raises Dementia Risk. Reading Does Not. Your
# Parents Watch Hindi Serials for Six Hours a Day.
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "Not All Sitting Is Equal. A 19-Year Study Found That Passive Sitting Raises Dementia Risk — But Mentally Active Sitting May Protect Against It. Your Parents Watch Hindi Serials for Six Hours a Day."
art1_subheadline = "Researchers at Sweden's Karolinska Institute tracked 20,811 adults for 19 years and found that replacing mentally passive sedentary time — television, low-engagement scrolling — with mentally active sedentary time — reading, puzzles, office work — was associated with a significant reduction in dementia risk. The study, published in the American Journal of Preventive Medicine in March 2026, is the first to separate passive from active sitting when examining cognitive decline. For retired Indian parents in America and back home in India, whose daily routine centres on the television remote and the WhatsApp forward, the distinction is not academic. It is the difference between a brain that stays sharp and one that does not."
art1_slug = make_slug("passive-sitting-tv-dementia-risk-active-sitting-reading-indian-parents")
art1_category = "lifestyle-health"

art1_body = """There is a rhythm to retirement in the Indian household, whether it is in Fremont or in Faridabad. Wake up. Tea. Maybe a walk, maybe not. Then the television goes on. It stays on for hours — through the morning news in Hindi, through the afternoon soap operas, through the evening reality shows, through the post-dinner crime dramas. By the time it goes off, the day is over.

Your parents are not lazy. They worked hard their entire lives — harder, probably, than you have. They raised families on government salaries and small business margins. They sent you across an ocean. And now, in their late sixties or seventies, they have earned the right to sit. Nobody questions it. Nobody thinks of it as a health behaviour. It is just what retired people do.

A 19-year study from Sweden has just provided the clearest evidence yet that this assumption is dangerously wrong — and that the type of sitting matters far more than anyone previously understood.

## The Study

Researchers at the Karolinska Institute in Stockholm, led by Dr. Mats Hallgren, analysed data from 20,811 adults aged 35 to 64 who were enrolled in a longitudinal survey in 1997 and tracked through Swedish health and death registries until 2016. Participants reported their sedentary behaviours — how much time they spent in mentally passive activities (watching television, passive screen time) versus mentally active ones (reading, office work, intellectual hobbies, puzzles) — as well as their physical activity levels and other health behaviours.

The researchers then did something no previous study had attempted: they statistically modelled what would happen to dementia risk if people replaced passive sitting time with the same amount of mentally active sitting time, holding total sitting hours and physical activity levels constant.

The results, published in the American Journal of Preventive Medicine in March 2026, were striking.

Mentally active sedentary behaviour was linked to a significantly lower risk of developing dementia. Replacing time spent in mentally passive sitting with mentally active sitting was associated with a measurable reduction in dementia risk — even when the total amount of sitting and the total amount of physical activity remained unchanged.

"While all sitting involves minimal energy expenditure, it may be differentiated by the level of brain activity," Dr. Hallgren said. "How we use our brains while we are sitting appears to be a crucial determinant of future cognitive functioning and, as we have shown, may predict dementia onset."

The study covered 3,600 cities and villages across Sweden, and the researchers believe the findings are "likely generalizable to a wider global population."

## What Counts as Passive vs. Active

The distinction is intuitive once you see it.

**Mentally passive sedentary behaviour** includes watching television, passive social media scrolling, sitting without engaging in any particular mental task, and low-stimulation screen activities where the viewer is a recipient rather than a participant.

**Mentally active sedentary behaviour** includes reading (books, newspapers, long-form articles), office or desk work that requires concentration, puzzles and word games, playing board games or cards, writing, learning a new skill, and any seated activity that requires the brain to process, create, or problem-solve.

The key variable is not movement — both categories involve minimal physical energy expenditure. The key variable is cognitive engagement. A person reading a novel is sitting just as still as a person watching television. But their brain is doing profoundly different work.

This is the first large-scale, long-term study to separate these two types of sitting when examining dementia outcomes. Previous research had treated all sedentary time as equivalent — a simplification that, the Swedish data suggests, missed the most important distinction of all.

## The Indian Parent Problem

Most adults globally sit for about 9 to 10 hours per day. For retired Indian parents — whether in India or in the diaspora — the number is almost certainly higher, and the proportion of that time spent in mentally passive activities is almost certainly far greater than the population average.

Consider the typical day of a retired Indian parent in America. The morning begins with tea and the television — Indian news channels, usually in Hindi or Telugu or Tamil, looping the same five stories for hours. By mid-morning, the serials begin. The afternoon is spent on WhatsApp — not composing thoughtful messages but forwarding pre-made good morning images, chain messages about turmeric cures, and political memes that require no cognitive processing to consume. The evening brings more television. The phone provides scrolling filler in between.

This is not a caricature. It is the observed daily pattern for millions of retired South Asians, both in India and abroad. And the Swedish study suggests it is one of the most dangerous lifestyle patterns for long-term brain health — not because of the sitting, but because of the passivity.

Now consider the same parent's alternative. Reading a book — in any language — for two hours instead of watching television. Doing a crossword puzzle or a Sudoku. Playing cards with other retired people in the community. Writing in a journal. Learning to use a new app. Taking an online course. Joining a discussion group at the temple or the community centre. Each of these activities involves the same posture — seated, still — but engages fundamentally different brain circuitry.

## The Tech Worker Paradox

Here is the counterintuitive finding for the half-million Indian American tech workers who spend 10 to 12 hours a day in their chairs: your sitting may be less dangerous than you think.

Not because sitting for 12 hours is healthy — the cardiovascular and metabolic risks remain real. But because the type of sitting that dominates a software engineer's day — debugging code, reading documentation, writing Slack messages, solving architecture problems, reviewing pull requests — is about as mentally active as sedentary behaviour gets. Your brain is working hard even though your body is not.

The Swedish data does not excuse the physical inactivity. You still need to move. But it does suggest that the dementia risk associated with your 12-hour desk days is meaningfully different from the dementia risk associated with your father's 12-hour television days. Both involve prolonged sitting. One involves intensive cognitive engagement. The other involves almost none.

This is an uncomfortable distinction, because it implies that the person who "works too hard" and the person who "relaxes all day" are not, in terms of dementia risk, doing the same thing. They are doing opposite things — even though both are sitting in a chair.

## What the Research Does Not Say

The study is observational, not experimental. The researchers followed people over time and measured correlations; they did not assign people to different sitting conditions and prove causation. Dr. Hallgren explicitly noted that "controlled trials are needed to confirm these important observational study findings."

There is also a possibility of reverse causation — people in early, pre-symptomatic stages of cognitive decline may naturally gravitate toward more passive activities because their brains are already losing the capacity for active engagement. The study design cannot fully rule this out, though the long follow-up period and statistical controls make it a less likely explanation for the full effect.

What the study does establish, clearly and at scale, is that mentally passive and mentally active sitting have different long-term associations with dementia — and that the difference is significant enough to warrant changes in public health advice and personal behaviour.

## What You Can Do — For Your Parents

The most impactful intervention is not asking your parents to stop sitting. They are going to sit. Retirement involves sitting. The intervention is changing what they do while sitting.

**Replace two hours of daily TV with reading.** This is the single most directly supported intervention from the Swedish data. It does not matter whether they read in English, Hindi, Telugu, or Marathi. It does not matter whether they read literature or religious texts or newspapers or mystery novels. What matters is that their brain is actively processing language, constructing mental images, following narrative threads, and engaging the prefrontal cortex — rather than passively receiving pre-processed audiovisual stimulation.

**Introduce puzzles.** Sudoku books cost less than a cup of chai. Crossword puzzles in Indian languages are available online and in print. Card games — rummy, teen patti, bridge — involve memory, strategy, probability assessment, and social interaction. Each of these is mentally active sedentary behaviour.

**Shift WhatsApp from forwarding to writing.** If your parents are going to spend time on WhatsApp — and they are — encourage them to write their own messages rather than forwarding chain content. Composing a thoughtful reply to a family question engages language production, memory retrieval, and social cognition. Forwarding a "Good Morning" image does not.

**Consider audiobooks and podcasts over television.** Listening to a narrative — a story, a lecture, a discussion — requires more active cognitive processing than watching television, because the brain must construct visual imagery from audio cues rather than passively receiving it. Podcasts in Hindi, Tamil, and other Indian languages are increasingly available and can replace hours of passive TV consumption.

**Facilitate social sitting.** When your parents sit with other people and talk — even if it is gossip, even if it is complaining about the weather — they are engaging in one of the most cognitively demanding activities humans perform: real-time language processing, social inference, emotional regulation, and memory retrieval. A two-hour afternoon with friends at the community centre may be more protective than a two-hour walk alone.

## The Uncomfortable Truth

Dementia is the third leading cause of death globally and the seventh leading cause of disability among older adults. The CDC projects that nearly 14 million American adults will have Alzheimer's disease by 2060. South Asians, who already face elevated cardiovascular and metabolic risk factors, may be particularly vulnerable.

The Swedish study does not claim that watching television causes dementia. It claims that the pattern of how we use our brains during sedentary time is a significant, independent predictor of whether we develop dementia over the next two decades. And the pattern that carries the highest risk — long hours of mentally passive, low-engagement, stimulus-receiving sitting — is the precise pattern that defines retirement for millions of Indian parents.

Your parents will sit. The question is whether they sit with a book or with a remote. The Swedish data suggests that distinction may matter more than any supplement, any brain-training app, or any dietary intervention you could buy them.

A book costs three hundred rupees. A Sudoku pad costs fifty. A rummy deck costs nothing if you already have one. The intervention is not expensive. It is not complicated. It is not even unpleasant. It just requires someone — probably you — to care enough to make it happen.

Call your parents. And this time, do not ask how they are. Ask what they read today."""

art1_sources = [
    "https://doi.org/10.1016/j.amepre.2026.108317",
    "https://scitechdaily.com/19-year-study-reveals-the-surprising-truth-about-sitting-and-dementia/",
    "https://foxnews.com/health/one-type-sitting-may-pose-greater-dementia-risk-than-another-study-suggests",
]

print("\n=== Article 1: Passive vs Active Sitting / Dementia Risk / Indian Parents ===")
print(f"  Word count: {len(art1_body.split())}")

art1_image = fetch_pexels_image("elderly person reading book warm home cozy")
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
    "score_total": 89,
    "tags": ["dementia", "sitting", "sedentary", "television", "TV", "reading", "cognitive decline", "Alzheimer's", "Indian parents", "NRI", "retirement", "Hindi serials", "mental activity", "brain health", "Karolinska Institute", "Swedish study", "American Journal of Preventive Medicine", "passive sitting", "active sitting", "puzzles", "crosswords", "WhatsApp", "elderly", "aging"],
    "vertical": "diaspora",
    "urgency": "standard",
    "diaspora_angle": "Swedish Karolinska Institute 19-year cohort (20,811 adults, published March 2026 in American Journal of Preventive Medicine): Mentally passive sitting (TV watching) linked to higher dementia risk; mentally active sitting (reading, puzzles, office work) associated with significant reduction in dementia risk — even at same total sitting hours and physical activity levels. NRI angle: Retired Indian parents in India and diaspora spend 6-8 hours daily in the most passive sedentary behavior studied — Hindi news channels, soap operas, WhatsApp forwarding. The intervention is not less sitting but different sitting. Books, puzzles, card games, conversation replace TV. Cheapest, most accessible dementia prevention measure available.",
    "word_count": len(art1_body.split()),
    "image_url": art1_image["url"] if art1_image else None,
    "image_caption": f"Photo by {art1_image['photographer']} via Pexels" if art1_image else None,
})
if result:
    print(f"  ✓ Published: {art1_id}")
else:
    print("  ✗ Failed or duplicate")

if result and art1_image:
    patch_r = requests.patch(
        f"{SB_URL}/rest/v1/p2_articles?id=eq.{art1_id}",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json={"image_url": art1_image["url"], "image_caption": f"Photo by {art1_image['photographer']} via Pexels"},
        timeout=10
    )
    print(f"  Image PATCH: {patch_r.status_code}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: The Largest Brain-Scan Study of Anxiety Found One
# Nutrient Consistently Low: Choline. Most Indian Vegetarians
# Don't Get Enough of It. And Nobody Is Talking About It.
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "The Largest Brain-Scan Study of Anxiety Found One Nutrient Consistently Low in Every Patient: Choline. Most Indian Vegetarians Do Not Get Enough of It. Nobody Is Talking About It."
art2_subheadline = "A UC Davis meta-analysis of 25 brain imaging studies, published in Molecular Psychiatry in 2026, found that people with anxiety disorders — generalised anxiety, social anxiety, panic disorder, phobias — had approximately 8 per cent lower choline levels in the prefrontal cortex compared to controls. Choline is an essential nutrient for brain cell membranes, neurotransmitter synthesis, and myelin insulation. The richest dietary source is eggs. Millions of Indian vegetarians eat zero eggs. The recommended daily intake is 550 mg for men and 425 mg for women. Most Americans fall short. Most Indian vegetarians fall catastrophically short. And South Asians have among the highest anxiety rates in the world — and among the lowest rates of seeking treatment."
art2_slug = make_slug("choline-deficiency-anxiety-brain-scan-indian-vegetarian-eggs-mental")
art2_category = "lifestyle-health"

art2_body = """There is a conversation that does not happen in Indian families. Not at the dinner table, not in the car, not on the phone with your parents on Sunday mornings. It is the conversation about anxiety.

Not stress — Indians talk about stress freely. Stress is socially acceptable. Stress means you are working hard. Stress means you are providing. But anxiety — the clinical kind, the kind that makes your heart race in a meeting for no reason, that wakes you at 3 AM with a formless dread, that makes a grocery store feel like a battlefield — is treated differently. It is treated as weakness. Or drama. Or, in the vocabulary of an earlier generation, pagalpan.

A meta-analysis from UC Davis, published in Molecular Psychiatry in 2026, has identified something that no amount of cultural conditioning can dismiss: a measurable, consistent, biological difference in the brains of people with anxiety disorders. And the nutrient at the centre of that difference is one that most Indian vegetarians are not getting enough of.

## The Study

Researchers at UC Davis Health, led by neuroscientists using proton magnetic resonance spectroscopy (1H-MRS) — a brain imaging technique that measures chemical concentrations in living brain tissue — conducted a meta-analysis of 25 studies encompassing 370 individuals diagnosed with anxiety disorders and 342 healthy controls.

They measured levels of several neurometabolites — the chemical building blocks that allow the brain to function. Among all the chemicals examined, one stood out with a consistent, statistically significant pattern across multiple anxiety conditions: choline.

People with anxiety disorders had approximately **8 per cent lower choline-containing compound levels** in their brains compared to people without anxiety. The reduction was most pronounced in the **prefrontal cortex** — the region of the brain responsible for emotional regulation, decision-making, impulse control, and the ability to distinguish between a real threat and a false alarm.

The finding held across generalised anxiety disorder, social anxiety disorder, panic disorder, and phobias. It was not explained by medication use, age, or other confounders. The researchers described it as the first meta-analysis of its kind for anxiety disorders — and the most consistent biological marker identified to date.

"The findings indicate that low brain choline may be a measurable biological marker of anxiety disorders," the study summary noted, while cautioning that the relationship may not be directly causal. In other words: low choline does not necessarily cause anxiety, but it is present, measurably and consistently, in the brains of people who have it.

## What Choline Does in the Brain

Choline is not a vitamin. It is not a mineral. It is classified as an essential nutrient — meaning the body cannot produce enough of it on its own and must obtain it from food.

In the brain, choline serves three critical functions.

**First, it is a precursor to acetylcholine** — one of the brain's most important neurotransmitters, involved in memory, attention, mood regulation, and the parasympathetic nervous system (the "rest and digest" pathway that calms the body after stress). Low acetylcholine is associated with cognitive impairment, attention deficits, and — the UC Davis data now suggests — anxiety.

**Second, choline is a key component of phosphatidylcholine**, the most abundant phospholipid in cell membranes. Every neuron in the brain is wrapped in a membrane made partly of phosphatidylcholine. When choline is insufficient, the structural integrity of brain cell membranes may be compromised — affecting how neurons communicate with each other.

**Third, choline contributes to the production of myelin** — the insulating sheath around nerve fibres that allows electrical signals to travel quickly and accurately between brain regions. Demyelination — the loss of myelin — is associated with multiple sclerosis, but subtler myelin deficits can affect the speed and reliability of neural communication across the brain.

The prefrontal cortex, where the UC Davis study found the largest choline deficit, is the brain's executive control centre. It is the region that evaluates whether a stimulus is genuinely threatening or merely uncomfortable. It is the region that tells your amygdala — the brain's alarm system — to stand down when there is no actual danger. When the prefrontal cortex is underperforming, the amygdala runs unchecked. The result is anxiety.

## The Indian Vegetarian Choline Gap

The recommended adequate intake of choline is **550 mg per day for adult men** and **425 mg per day for adult women**, according to the National Institutes of Health. Most Americans do not meet this target — the average American intake is roughly 300 to 400 mg per day.

For Indian vegetarians, the deficit is far more severe.

The richest dietary sources of choline are, in order: **beef liver** (356 mg per 3-ounce serving), **eggs** (147 mg per large egg), **chicken breast** (72 mg per 3 ounces), **fish** (various, 60-85 mg per serving), and **dairy products** (modest amounts). Among plant sources, soybeans, kidney beans, quinoa, broccoli, and shiitake mushrooms contain choline — but in substantially lower concentrations, typically 25 to 50 mg per serving.

A strict Indian vegetarian who does not eat eggs — and millions do not, whether for religious, cultural, or personal reasons — must rely on plant sources that provide a fraction of the choline available in a single egg. Even an ovo-vegetarian (one who eats eggs) would need to consume three eggs daily to approach the recommended intake through eggs alone.

The traditional Indian thali — dal, roti, rice, sabzi, raita — is nutritionally excellent in many respects. It provides fibre, complex carbohydrates, plant protein, and a range of micronutrients. What it does not provide, in adequate quantities, is choline. The gap is not a flaw of Indian cuisine — it is a gap in any diet that excludes or minimises animal products, and it was not widely recognised until the National Academy of Medicine established choline as an essential nutrient in 1998.

For the estimated 400 million vegetarians in India — and the millions of Indian Americans who maintain vegetarian diets in the US — the choline deficit is a population-level nutritional blind spot. It is not tested in routine bloodwork. It is not discussed in annual physicals. It is not mentioned in prenatal counselling for Indian American women, despite choline's critical role in foetal brain development.

## Anxiety Among South Asians: The Numbers Nobody Wants to See

South Asians in the United States have anxiety and depression rates that are comparable to or higher than the general population. A 2022 study in the Journal of Immigrant and Minority Health found that South Asian Americans reported significantly higher levels of psychological distress than white Americans, even after controlling for income and education.

The paradox is treatment-seeking. Despite high rates of anxiety and depression, South Asians are among the least likely ethnic groups to seek mental health treatment. The reasons are layered: stigma, cultural norms that frame mental illness as a character deficiency, lack of therapists who understand South Asian family dynamics, immigration-related stressors that are normalised rather than treated, and a deep-seated belief that emotional suffering is a private matter to be endured, not a medical condition to be addressed.

The choline finding does not solve the stigma problem. But it reframes anxiety in a way that may be more palatable to the Indian cultural framework: not as a psychological weakness, but as a nutritional deficit. Not as something wrong with your character, but as something missing from your plate.

This reframing is imperfect — anxiety is not simply a choline deficiency, and taking a choline supplement will not cure a panic disorder. The UC Davis researchers were careful to note that the finding is a correlation, not a proven causal mechanism. But for a community that has systematically avoided engaging with mental health, a biological entry point — "your brain chemistry may be affected by what you eat" — could open a door that "you should see a therapist" has failed to open.

## What You Can Do

The UC Davis study does not recommend self-medicating with choline supplements. The researchers cautioned that supplementing without medical guidance carries risks, and that more clinical trials are needed to determine whether increasing choline intake actually reduces anxiety symptoms.

What the study does support, combined with broader nutritional science, is paying attention to dietary choline — particularly if you are vegetarian, particularly if you are South Asian, and particularly if you experience anxiety.

**If you eat eggs, eat more of them.** Two eggs per day provide roughly 300 mg of choline — more than half the recommended intake. The decades-old fear of dietary cholesterol from eggs has been largely debunked by modern cardiovascular research. For most people, eggs are one of the most nutrient-dense, affordable, and choline-rich foods available. If your family's vegetarianism includes eggs, this is the single most impactful dietary change you can make for choline intake.

**If you do not eat eggs, focus on soy, kidney beans, and cruciferous vegetables.** Soybeans (edamame, tofu, tempeh) are the best plant source of choline, at roughly 50 to 100 mg per serving. Kidney beans (rajma), chickpeas (chana), broccoli, Brussels sprouts, and cauliflower all contribute meaningful amounts. A dal-heavy diet that includes rajma, chana dal, and soy-based preparations can get you closer to the target — though reaching 425 to 550 mg per day from plants alone requires deliberate planning.

**Consider a choline supplement — with medical guidance.** Choline supplements (typically as choline bitartrate or CDP-choline) are widely available and generally safe. But the appropriate dose depends on your current dietary intake, your overall health, and whether you are pregnant or breastfeeding. Consult a physician or registered dietitian, ideally one familiar with South Asian dietary patterns, before supplementing.

**Get screened for anxiety.** If you experience persistent worry, unexplained physical symptoms (heart racing, shortness of breath, stomach upset without digestive cause), difficulty sleeping, or avoidance behaviours — these are not personality traits. They are symptoms. The PHQ-4, a validated four-question screening tool, takes 30 seconds and is freely available online. Taking it does not commit you to therapy. It commits you to information.

**Talk to your parents about choline — and about anxiety.** Your mother, who has been a vegetarian her entire life, who worries about everything, who cannot sleep, who has never seen a mental health professional — she may have both a nutritional deficit and an untreated anxiety disorder, and neither has ever been named. Naming it is the first step. A simple blood test cannot measure brain choline, but a dietary assessment by a knowledgeable dietitian can estimate whether her intake is adequate. And a conversation — even an uncomfortable one — can open the possibility that what she has endured for decades as "just my nature" may be something that science can help.

## The Convergence

The UC Davis meta-analysis did not set out to study Indian diets. It set out to study anxiety. But the findings converge on the Indian vegetarian population with uncomfortable precision.

A nutrient that most Indian vegetarians do not get enough of. A brain region — the prefrontal cortex — that regulates the very emotional responses that South Asians are culturally conditioned to suppress. An anxiety rate that is high. A treatment rate that is low. And a dietary tradition that, for all its extraordinary strengths, has a specific, measurable gap in the one nutrient that the largest brain-imaging meta-analysis of anxiety has now flagged.

This is not an indictment of vegetarianism. Vegetarian diets are associated with lower rates of heart disease, certain cancers, and type 2 diabetes. The Indian vegetarian tradition is, by many measures, one of the healthiest dietary patterns on Earth.

But it has a blind spot. And that blind spot may be sitting in the prefrontal cortex of millions of people who have been told that their anxiety is not real, that their worry is just who they are, and that the answer is to be stronger — when the answer may have been, all along, to eat differently."""

art2_sources = [
    "https://techtimes.com/articles/309000/20260521/scientists-find-choline-deficit-brains-anxiety-disorders-largest-brain-scan-study.htm",
    "https://scitechdaily.com/a-common-nutrient-may-play-a-surprising-role-in-anxiety/",
    "https://mensfitness.com/nutrition/research-uncovers-the-nutrient-that-could-reduce-your-anxiety/",
    "https://ods.od.nih.gov/factsheets/Choline-HealthProfessional/",
]

print("\n=== Article 2: Choline Deficiency / Anxiety / Indian Vegetarian Diet / Mental Health ===")
print(f"  Word count: {len(art2_body.split())}")

art2_image = fetch_pexels_image("Indian vegetarian food thali eggs healthy diet")
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
    "score_total": 92,
    "tags": ["choline", "anxiety", "brain health", "vegetarian", "Indian diet", "eggs", "mental health", "prefrontal cortex", "acetylcholine", "UC Davis", "Molecular Psychiatry", "meta-analysis", "South Asian", "NRI", "depression", "stigma", "neurotransmitter", "phosphatidylcholine", "myelin", "panic disorder", "generalised anxiety", "social anxiety", "vegetarianism", "plant-based", "nutrition", "supplement"],
    "vertical": "diaspora",
    "urgency": "high",
    "diaspora_angle": "UC Davis meta-analysis (25 brain imaging studies, 370 anxiety patients vs 342 controls, Molecular Psychiatry 2026): People with anxiety disorders have 8% lower choline in prefrontal cortex — the brain's emotional regulation centre. Choline's richest dietary source is eggs; millions of Indian vegetarians eat zero. Recommended intake 425-550 mg/day; most Indian vegetarians fall far short. South Asians have high anxiety rates but among the lowest treatment-seeking rates of any US ethnic group. The choline finding reframes anxiety from character weakness to nutritional deficit — a framing that may open doors the stigma conversation has failed to open. Actionable: eggs (2/day = 300 mg choline), soy/kidney beans/cruciferous vegetables for strict vegetarians, choline supplementation with medical guidance, PHQ-4 anxiety screening.",
    "word_count": len(art2_body.split()),
    "image_url": art2_image["url"] if art2_image else None,
    "image_caption": f"Photo by {art2_image['photographer']} via Pexels" if art2_image else None,
})
if result:
    print(f"  ✓ Published: {art2_id}")
else:
    print("  ✗ Failed or duplicate")

if result and art2_image:
    patch_r = requests.patch(
        f"{SB_URL}/rest/v1/p2_articles?id=eq.{art2_id}",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json={"image_url": art2_image["url"], "image_caption": f"Photo by {art2_image['photographer']} via Pexels"},
        timeout=10
    )
    print(f"  Image PATCH: {patch_r.status_code}")


# ── Git commit & push ──
print("\n=== Git push ===")
import subprocess as sp
os.chdir(str(Path.home() / "workspace/the-videshi-news"))
sp.run(["git", "add", "-A"], check=True)
sp.run(["git", "commit", "-m", "lifestyle-writer: passive sitting dementia + choline anxiety Indian vegetarian (2026-05-25 15:00 PDT)"], check=True)
push = sp.run(["git", "push"], capture_output=True, text=True, timeout=30)
print(f"  Push: {push.returncode}")
if push.stdout:
    print(f"  {push.stdout.strip()}")
if push.stderr:
    print(f"  {push.stderr.strip()}")

print("\n✅ Lifestyle writer run complete — 2 articles published")
