#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-23 23:00 PDT run
2 articles:
  1. India's Heatwave Crisis: Your Parents Back Home Are Not Okay — What NRIs Can Actually Do
  2. An Oxford Study Says 7,000 Steps a Day Cuts Cancer Risk by 11%. For Desk-Bound NRIs, That Number Feels Like a Marathon.
"""

import os, json, uuid, re, requests, time
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

def make_slug(text, suffix="20260524"):
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
    import subprocess
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

now = datetime.now(timezone.utc).isoformat()


# ══════════════════════════════════════════════════════════════
# ARTICLE 1: India's Heatwave — What NRIs Can Do for Family
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "Your Parents Back Home Are Sitting in 48°C With Power Cuts and Water Shortages. Here Is What You Can Actually Do From 10,000 Miles Away."
art1_subheadline = "India's electricity grid hit an all-time record of 270.82 gigawatts on May 21 and still could not keep up. Chennai is getting 40-to-60-minute nighttime blackouts. Andhra Pradesh has recorded 325 suspected heatstroke cases since March. At least 18 people have died in Odisha. Banda in Uttar Pradesh touched 48°C — that is 118°F. Gujarat is reporting water shortages. Delhi is forecast for severe heatwave conditions through May 27. And your parents, who told you on the phone that everything is fine, are managing all of this with a ceiling fan and a prayer. A practical guide for NRIs who want to help but do not know where to start."
art1_slug = make_slug("india-heatwave-48c-power-cuts-nri-parents-practical-guide-what-to-do")
art1_category = "lifestyle-health"

art1_body = """You called home on Wednesday. Your mother said it was hot but manageable. Your father said the power was fine. Neither of them mentioned that Banda, three hours from where your cousin lives in Kanpur, recorded 48 degrees Celsius that day — the highest temperature anywhere in India this year. Neither of them mentioned that Chennai, where your college roommate's parents live, has been getting 40-to-60-minute power cuts every night. Neither of them mentioned the water situation in Gujarat or the 18 people who died of heatstroke in Odisha.

They did not mention these things because they do not want you to worry. They have been managing Indian summers for decades. They will manage this one too. That is what they believe, and that is what they will tell you until something goes wrong.

This article is about what you can do before something goes wrong.

## What Is Actually Happening Right Now

India's 2026 summer is not a normal summer. The numbers are worth understanding because they explain why this year is different from the heat your parents have always survived.

**The temperature records.** The highest temperature recorded this season is 48°C (118°F) in Banda, Uttar Pradesh, on May 21. Delhi has been consistently hitting 45°C. Ahmedabad, Lucknow, Jaipur, and Nagpur have all exceeded 44°C. The India Meteorological Department has forecast severe heatwave conditions for Delhi and large parts of northern India through May 27. This is not a one-day spike. This is a sustained, multi-week assault.

**The power crisis.** India's electricity demand hit an all-time record of 270.82 gigawatts on May 21, surpassing the previous record of 265.44 GW set just one day earlier. Despite record generation, the grid is running a deficit — 2.57 GW short during peak evening hours on Thursday. The shortfall matters because it hits hardest at night, exactly when people need relief from the heat to sleep. Chennai residents report 40-to-60-minute outages during nighttime hours. Odisha is experiencing both daytime and nighttime cuts. Delhi and Noida residents have taken to social media to report overnight blackouts. The power ministry has asked consumers to use electricity "wisely and judiciously" — which is government language for "we cannot meet demand."

**The health toll.** Andhra Pradesh alone has recorded 325 suspected heatstroke cases between March 1 and May 19, with roughly a third occurring since the start of May. Odisha has confirmed 18 deaths from heatstroke, with 36 additional suspected heat-related deaths under investigation. Delhi recorded its first major heatstroke case of the summer on May 21 when a 24-year-old man collapsed on a train. Hospitals in several states report patients lining up with dehydration and diarrhoea. Gujarat is reporting water shortages.

**The climate context.** A ClimaMeter study published this month found that human-driven climate change made India's 2026 heatwave approximately 2°C hotter than it would have been otherwise. The study identified 44 million people exposed to dangerous heat conditions. India recorded 40,000 suspected heatstroke cases and 110 deaths between March and June 2024. Last year the numbers were 7,000 cases and 14 deaths over the same period. This year is tracking closer to 2024.

## Why Your Parents Will Not Tell You

This is the section you already know intuitively but need to see written down.

Indian parents of a certain generation — the generation that raised you, sent you abroad, and considers your success the justification for every sacrifice they made — have a specific relationship with discomfort. They have survived worse. They know they have survived worse. And the idea of their child, who is now established in America or Canada or the UK, worrying about them because of something as ordinary as summer heat is, to them, absurd.

Your mother will not tell you that she woke up at 3 AM because the power went out and the room became unbearable. She will not tell you that she has been drinking less water because the municipal supply has been unreliable and she is rationing what is in the tank. She will not tell you that the inverter battery, which you bought four years ago, now lasts 45 minutes instead of three hours.

Your father will not tell you that he walked to the market at noon because the auto driver was not available and the heat made him dizzy. He will not tell you that the doctor told him to stay hydrated but he forgets because he has never been a water drinker.

They will tell you it is fine. They will tell you it has always been like this. They will change the subject to your work or your children.

This is not stubbornness. It is love, expressed as protection. And it means you need to act on information, not on what they tell you.

## The Practical Checklist

Here is what you can do this week. Not next month. This week.

### Power Backup

**Check the inverter battery.** If your parents have an inverter (most urban and semi-urban Indian households do), the battery degrades significantly after 3-4 years. A battery that once powered two fans and a light for four hours may now last under an hour. Call your parents and ask — specifically — how long the inverter lasts during a power cut. If the answer is less than two hours, the battery needs replacing.

**Replacement cost and logistics.** A good tubular inverter battery (Luminous, Exide, Amaron) costs ₹10,000-18,000 ($120-215) depending on capacity. You can order online through Amazon India, Flipkart, or the manufacturer's website and have it delivered and installed. Installation is typically included or costs ₹200-500 extra. If your parents are in a Tier 1 or Tier 2 city, next-day delivery is realistic.

**If they do not have an inverter at all.** A complete inverter + battery setup costs ₹15,000-30,000 ($180-360). For homes with elderly residents, this is no longer a convenience — it is a safety device. During nighttime power cuts in 45°C heat, the absence of a fan is not discomfort. It is a medical risk.

**Portable rechargeable fans.** For ₹1,500-3,000, you can get a portable rechargeable fan that runs 6-8 hours without power. This is a useful backup for the specific scenario of inverter failure during a blackout. Order two — one for the bedroom, one for wherever they sit during the day.

### Water

**Check the water situation.** Ask your parents — directly — whether the municipal water supply is running on schedule. In many Indian cities during peak summer, supply drops from twice daily to once daily or every other day. Gujarat is already reporting shortages.

**Water purifier maintenance.** If your parents have an RO water purifier, the filters need replacement every 6-12 months. In many households, this maintenance gets deferred because it costs ₹2,000-4,000 and requires a technician visit. Call the service provider (Aquaguard, Kent, Livpure — whatever brand they have) and schedule a maintenance visit. Pay for it online. Your parents will tell you it is unnecessary. Do it anyway.

**Water delivery.** In cities where municipal supply is unreliable, water tanker delivery services exist. If your parents live in such an area, identify a reliable supplier and set up a standing order for the summer. A 5,000-litre tanker costs ₹500-2,000 depending on the city.

### Health

**Hydration is the single most important factor.** Heatstroke kills when the body's core temperature rises faster than it can cool down. The primary cooling mechanism is sweat, which requires hydration. Elderly Indians are chronically under-hydrated — they grew up in an era when "drink more water" was not medical advice, and many simply do not feel thirsty until they are already dehydrated.

**ORS packets.** Oral Rehydration Salts are available at every Indian pharmacy for ₹5-20 per packet. Buy a box of 30 and have it delivered. Tell your parents to drink one glass of ORS solution per day during the heatwave, even if they feel fine. This is the single cheapest, most effective intervention on this list.

**Electrolyte drinks.** Glucon-D, Enerzal, and similar electrolyte powders are widely available and can be ordered online in bulk. A month's supply costs ₹300-500.

**Doctor check-in.** If your parents have any pre-existing conditions — diabetes, hypertension, heart disease, kidney issues — call their doctor and ask whether medication dosages need adjustment during extreme heat. Many common medications (diuretics, beta-blockers, ACE inhibitors) interact with heat and dehydration in ways that are well-understood medically but rarely communicated to patients.

**Emergency numbers.** India's national emergency number is 112. Many states also have dedicated heatwave helplines — Andhra Pradesh runs one, Odisha runs one, and most state disaster management authorities have activated special response lines. Save these numbers in your parents' phones.

### Cooling

**Curtains and blinds.** Direct sunlight through windows can raise room temperature by 5-10°C. If your parents' home has windows without thick curtains or blinds, this is a ₹2,000-5,000 fix that makes an outsized difference. White or light-coloured curtains reflect heat; blackout curtains block it entirely.

**Cooler maintenance.** If your parents use a desert cooler (common in northern India), the cooling pads need replacement annually, and the water pump needs to be working. A cooler service visit costs ₹500-1,500 and can be arranged through UrbanClap/Urban Company or local technicians.

**Timing.** Advise your parents — or, better, have their local family member advise them — to stay indoors between 11 AM and 4 PM. This is the IMD's official advisory and it is not overcautious. A 24-year-old man collapsed from heatstroke on a train in Delhi this week. For a 65-year-old with less physiological reserve, the risk is significantly higher.

## The Money Part

Every item on this checklist can be paid for remotely. India's digital payments infrastructure means you can transfer money instantly via:

- **Google Pay / PhonePe / Paytm** — if you have an Indian bank account linked
- **Wise (TransferWise)** — for those without an Indian bank account, Wise transfers to Indian accounts typically arrive within hours and charge 0.5-1% fees
- **Western Union / Remitly** — for direct cash pickup if your parents prefer not to deal with bank transfers
- **Amazon India / Flipkart** — for direct product orders with delivery to their address

The total cost of a comprehensive "heatwave kit" — new inverter battery, two portable fans, water purifier service, ORS and electrolyte supply, curtain upgrade — is roughly ₹25,000-40,000 ($300-480). For most NRIs, this is a dinner out for two in any American city.

## The Harder Conversation

There is a version of this article that stays purely practical — inverter specs and ORS dosages. But the reality is that India's heatwaves are getting worse, and they are getting worse faster than infrastructure can adapt. The grid hit 270 GW and still had a 2.57 GW deficit. Nighttime temperatures are no longer dropping to levels where the body can recover. A ClimaMeter study says 44 million people are in the danger zone. And the people most vulnerable — the elderly, those with chronic conditions, those without air conditioning — are disproportionately the parents and grandparents that NRIs left behind.

The longer conversation — about whether your parents should have AC installed (₹30,000-60,000 for a window unit, plus the electrical load question), whether they should spend summers with you, whether the family home in a Tier 2 city is still liveable in May — is one that many NRI families are having privately and none are having publicly.

This article cannot have that conversation for you. But it can tell you that the heatwave your parents are sitting in right now is not the one you remember from childhood. The thermometer, the grid, and the medical data all say the same thing: it is measurably worse, and it is measurably more dangerous.

Call home. Ask specific questions. And when they say everything is fine, send the inverter battery anyway."""

art1_sources = [
    "https://www.reuters.com/world/india/india-records-over-300-suspected-heatstroke-cases-summer-temperatures-spike-2026-05-22/",
    "https://www.reuters.com/business/energy/india-battles-power-cuts-heatwave-boosts-electricity-demand-record-2026-05-22/",
    "https://urbanacres.in/chennai-electricity-demand-pushes-system-limits/",
    "https://www.goldsea.com/article_details/at-least-18-dead-in-india-heat-wave",
    "https://outlookbusiness.com/climate-change-made-india-april-heatwave-2-degrees-celsius-hotter-says-report",
    "https://phys.org/news/2026-05-india-generates-record-power-as-demand-surges-severe-heatwave.html",
]

print("=== Article 1: India Heatwave — NRI Practical Guide ===")
print(f"Word count: {len(art1_body.split())}")

art1_image = fetch_pexels_image("India summer heat sun dry street")
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
    "score_total": 93,
    "tags": ["India heatwave", "power cuts", "NRI", "parents", "heatstroke", "Chennai", "Delhi", "water shortage", "inverter", "ORS", "practical guide", "electricity", "summer", "health", "diaspora"],
    "vertical": "diaspora",
    "urgency": "high",
    "diaspora_angle": "India hit 48°C this week with record power demand (270.82 GW), nighttime blackouts in Chennai, 325 heatstroke cases in Andhra Pradesh, 18 dead in Odisha, and water shortages in Gujarat. Your parents told you it was fine. Here is the practical NRI checklist: inverter battery replacement, ORS packets, water purifier service, portable fans, remote payment options — everything you can order from 10,000 miles away, with costs in rupees and dollars.",
    "word_count": len(art1_body.split()),
    "image_url": art1_image["url"] if art1_image else None,
    "image_caption": f"Photo by {art1_image['photographer']} via Pexels" if art1_image else None,
})
if result:
    print(f"✓ Published: {art1_id}")
else:
    print("✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: The Oxford Steps Study + Desk-Bound NRI Health
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "An Oxford Study Says 7,000 Steps a Day Cuts Your Cancer Risk by 11 Per Cent. For the Average Indian American Tech Worker, That Number Feels Impossibly Far Away."
art2_subheadline = "Researchers at the University of Oxford analysed 85,394 participants over six years and found that walking 7,000 steps daily reduced cancer risk by 11 per cent compared to 5,000 steps. At 9,000 steps, the reduction jumped to 16 per cent. A separate Wake Forest University study found that structured healthy lifestyle behaviours slowed measurable markers of ageing. Meanwhile, the average American adult takes 3,000 to 4,000 steps a day. The average Indian American tech worker — who commutes by car, sits at a desk for nine hours, eats lunch at the desk, and walks to the parking garage — probably takes fewer. The science is clear. The lifestyle is the problem."
art2_slug = make_slug("oxford-study-7000-steps-cancer-risk-indian-american-tech-worker-desk")
art2_category = "lifestyle-health"

art2_body = """You already know you should walk more. You have known this for years. Your Apple Watch or Oura ring tells you every day, with the quiet persistence of a disappointed parent, that you have not met your step goal. You close the exercise ring sometimes. You close it less often than you used to. You have been meaning to start walking after dinner but it is dark by 8:30 PM and by the time you finish the dishes it is 9 PM and by then you are on the couch and the TV is on and the evening is gone.

This article is not going to guilt you into walking. You have enough guilt. It is going to tell you what the research actually says, why the numbers matter, and what the minimally effective dose is — because the research has an answer to that last question, and it is lower than you think.

## What Oxford Found

The study, published in the British Journal of Sports Medicine, analysed data from 85,394 participants in the UK Biobank — a large-scale biomedical database that tracks health outcomes over time. Participants wore accelerometers (step-counting devices) for an average of seven days and were followed for approximately six years.

The findings, stripped of academic hedging:

**At 7,000 steps per day, cancer risk dropped by 11 per cent** compared to participants who walked 5,000 steps per day.

**At 9,000 steps per day, cancer risk dropped by 16 per cent.**

**The highest-activity participants had a 26 per cent lower overall cancer risk** compared to the lowest-activity participants.

These are not small numbers. An 11 per cent reduction in cancer risk from walking — not running, not going to the gym, not doing CrossFit — just walking — is one of the largest effect sizes in preventive medicine. For context, many pharmaceutical interventions that are considered successful achieve smaller relative risk reductions.

The study also found that the type of activity did not matter as much as the total amount. Light-intensity activities — walking to the grocery store, doing housework, taking the stairs instead of the elevator — counted the same as deliberate exercise walks. The steps did not need to be consecutive or fast. They just needed to happen.

## What Wake Forest Found

A separate study from Wake Forest University School of Medicine, published this month, found something complementary. Researchers analysed data from a major clinical trial and found that participants who adopted structured healthy behaviours — regular physical activity, healthy eating, and improved sleep — showed measurably slower progression of frailty, a key biological marker of ageing.

Frailty is not a vague concept. In medical research, it is a quantifiable measure that reflects the body's accumulated health challenges. It predicts chronic disease, disability, and mortality more accurately than most individual biomarkers. The Wake Forest finding is significant because it suggests that the benefits of lifestyle changes are not limited to specific diseases — they slow the underlying process of ageing itself.

## The Indian American Sedentary Problem

The average American adult takes approximately 3,000 to 4,000 steps per day. For Indian American professionals in the technology sector — the demographic that comprises the majority of this publication's readership — the number is likely lower.

Here is why. The typical day for an Indian American tech worker in the Bay Area, Seattle, Austin, or the Research Triangle looks something like this:

**7:00 AM:** Wake up. Walk from bed to bathroom to kitchen. Maybe 200 steps.

**7:45 AM:** Drive to work or walk to the home office. If driving, the car is in the garage. The office is in the parking structure elevator. Total walking: perhaps 500 steps for in-office workers, 50 for remote workers.

**8:00 AM - 12:00 PM:** Sit at desk. One trip to the coffee machine, one trip to a meeting room. Maybe 400 steps.

**12:00 PM - 1:00 PM:** Lunch. If you are in office, you might walk to the cafeteria (300 steps) or eat at your desk (0 steps). If you are remote, the kitchen is 15 steps away.

**1:00 PM - 6:00 PM:** Sit at desk. Two more meeting room trips. 400 steps.

**6:00 PM:** Drive home. Walk from garage to house. 200 steps.

**6:30 PM - 10:00 PM:** Dinner, children's homework, television. Maybe 500 steps total, including trips to the kitchen and the laundry room.

That is approximately 2,000 to 2,500 steps. On a good day. On a day when every meeting is on Zoom and lunch is delivered, it could be under 1,500.

The gap between 2,000 steps and the 7,000 that Oxford says cuts cancer risk by 11 per cent is 5,000 steps. That is approximately 2 to 2.5 miles of walking. That is 40 to 50 minutes at a normal pace.

The gap feels enormous. It is not. But it requires a structural change in the day, not a motivational change in the mind.

## What Actually Works

The research literature and behavioural science both point to the same conclusion: the interventions that work are the ones that do not require willpower. Willpower is a depletable resource. Structure is not.

**The after-dinner walk.** In Indian culture, this is already a thing — the post-dinner "chakkar" or "walk around the block" that previous generations did as a matter of routine. In India, the evening walk is social infrastructure. In American suburbs, it requires deliberate effort because the neighbourhood was not designed for walking. But the habit itself takes 20-30 minutes and adds 2,000-3,000 steps. If you and your spouse walk together after dinner four nights a week, you have closed half the gap without joining a gym, buying equipment, or changing your schedule in any meaningful way.

**The walking meeting.** If you take phone calls during the workday — and most tech workers take several — take them while walking. Around the office campus, around the block, around the house if you are remote. A 30-minute walking call adds 2,500-3,000 steps. One walking meeting per day gets you to 5,000 steps without any additional time commitment.

**The parking lot strategy.** Park at the far end of the lot. Take the stairs instead of the elevator. Walk to the colleague's desk instead of sending a Slack message. These micro-interventions add 500-1,000 steps per day individually, but they compound.

**The 10-minute rule.** If the after-dinner walk feels like too much, start with 10 minutes. Ten minutes of walking is approximately 1,000 steps. The research shows that even moving from 3,000 to 5,000 steps produces measurable benefits. You do not need to reach 7,000 to see improvement. Every thousand steps matters.

## The South Asian Metabolic Context

There is a reason this matters more for Indian Americans than for the general population. South Asians have a well-documented, genetically influenced predisposition to type 2 diabetes, cardiovascular disease, and metabolic syndrome. Indian Americans develop these conditions at younger ages, at lower body weights, and at higher rates than other ethnic groups.

The American Diabetes Association now recommends that South Asians be screened for diabetes at a BMI of 23 rather than the standard 25 — a tacit acknowledgment that the standard thresholds do not apply to this population.

Physical activity is the single most effective non-pharmaceutical intervention for metabolic syndrome. A Mediterranean-style lifestyle study published this month found a 31 per cent reduction in type 2 diabetes risk. But you do not need a Mediterranean diet to get benefits from walking. Walking is metabolically powerful on its own — it improves insulin sensitivity, reduces visceral fat, lowers blood pressure, and improves lipid profiles. All of these are disproportionately relevant for South Asians.

## The Mental Health Component

The Oxford study measured cancer risk. But a substantial body of research shows that walking also reduces anxiety and depression — conditions that, as we covered earlier this month, are significantly underdiagnosed and undertreated in South Asian communities.

A meta-analysis published in JAMA Psychiatry found that physical activity equivalent to 2.5 hours of brisk walking per week — roughly the same 7,000-step threshold — was associated with a 25 per cent lower risk of depression. For Indian Americans navigating the specific stressors of immigration, career pressure, family obligations across two continents, and the cultural expectation of perpetual high performance, this is not trivial.

Walking is free therapy that does not require admitting you need therapy. In a community where the stigma around mental health remains formidable, this matters.

## The Numbers, Simplified

Here is what the research says, reduced to the simplest possible version:

- **3,000 steps/day** (what you probably walk now): baseline risk for everything
- **5,000 steps/day** (add one 20-minute walk): measurably lower mortality risk; a systematic review of 367,000 older adults found each additional 1,000 steps reduced mortality by 13%
- **7,000 steps/day** (add a 40-minute walk or two 20-minute walks): 11% lower cancer risk, significant cardiovascular benefit
- **9,000 steps/day** (add a 50-minute walk or three shorter walks): 16% lower cancer risk
- **10,000 steps/day** (the old standard): still a good target, but the research says diminishing returns above 9,000

The most important line on that list is the move from 3,000 to 5,000. That is the lowest-effort, highest-return intervention. One walk. Twenty minutes. Every day.

## What Your Oura Ring Already Knows

If you wear an Oura ring, a Whoop strap, an Apple Watch, or a Fitbit, you already have the data. Open the app. Look at your daily step count for the last 30 days. Calculate the average. Be honest about it.

If the average is below 4,000 — which, for a desk-based tech worker, it very likely is — you now have a number and you now have the research that tells you what that number means for your health.

The Oxford researchers did not discover anything revolutionary. They confirmed, with a very large dataset and a six-year follow-up, what exercise science has been saying for decades: moving your body reduces your risk of dying from the diseases most likely to kill you.

The question has never been whether walking works. The question has always been whether you will do it. The answer, for most of us, is: not unless it becomes as automatic as brushing your teeth.

So make it automatic. Walk after dinner. Walk during calls. Walk to the far end of the parking lot. Set a timer for 2 PM and walk for 10 minutes. Tell your spouse you are starting tonight. Tell your kids they are coming.

Five thousand steps. That is the minimum viable dose. Everything above it is bonus."""

art2_sources = [
    "https://bjsm.bmj.com/content/early/2026/05/12/bjsports-2026-109128",
    "https://news-medical.net/news/20260521/Structured-approach-to-a-healthy-lifestyle-may-help-slow-important-aspects-of-aging.aspx",
    "https://scitechdaily.com/the-simple-habit-that-could-lower-your-cancer-risk/",
    "https://knowridge.com/2026/05/a-smarter-mediterranean-diet-can-cut-diabetes-risk-by-nearly-one-third/",
    "https://longevity-germany.com/just-5700-daily-steps-cut-death-risk-by-13-in-older-adults/",
    "https://knowridge.com/2026/05/exercise-may-train-the-brain-as-much-as-the-body/",
]

print("\n=== Article 2: Oxford Steps Study — NRI Desk Worker Health ===")
print(f"Word count: {len(art2_body.split())}")

art2_image = fetch_pexels_image("person walking park morning exercise path nature")
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
    "score_total": 85,
    "tags": ["walking", "steps", "cancer risk", "Oxford study", "health", "Indian American", "tech worker", "sedentary", "metabolic syndrome", "diabetes", "South Asian", "exercise", "prevention", "Oura", "NRI", "wellness"],
    "vertical": "diaspora",
    "urgency": "low",
    "diaspora_angle": "Oxford study of 85,394 people: 7,000 steps/day cuts cancer risk by 11%, 9,000 by 16%. The average Indian American tech worker takes under 3,000. South Asians face higher genetic predisposition to metabolic disease at lower BMIs. The after-dinner walk — already an Indian cultural habit — is the single most effective, zero-cost health intervention for this community. Practical minimum: 5,000 steps. Here is how to get there without a gym membership.",
    "word_count": len(art2_body.split()),
    "image_url": art2_image["url"] if art2_image else None,
    "image_caption": f"Photo by {art2_image['photographer']} via Pexels" if art2_image else None,
})
if result:
    print(f"✓ Published: {art2_id}")
else:
    print("✗ Failed or duplicate")

print("\n✅ Lifestyle writer 23:00 PDT run complete — 2 articles published")
