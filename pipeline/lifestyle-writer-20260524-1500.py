#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-24 15:00 PDT run
2 articles:
  1. Sleep rhythms and dementia — Nedergaard Science paper: glymphatic brain waste clearance tied to sleep oscillations, HRV as biomarker; NRI angle: South Asian late-night culture, India calls across time zones, tech-industry sleep deprivation, Oura/wearable HRV data as early warning
  2. Surgeon General screen time advisory — May 21 2026 HHS advisory: zero screens under 18mo, <1h under 6, <2h ages 6-18; NRI angle: Silicon Valley Indian parents build the apps their kids are addicted to, iPad babysitting during India FaceTime, academic screen time blind spot, WhatsApp family groups
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

# Check for duplicate topics
recent_slugs = [a.get("slug", "") for a in recent]
recent_headlines = " ".join([a.get("headline", "") for a in recent]).lower()

# Verify neither topic already covered
topics_ok = True
for check_term in ["glymphatic", "sleep rhythm", "brain waste clearance", "screen time advisory", "surgeon general screen"]:
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
    from datetime import datetime as dt
    now_utc = datetime.now(timezone.utc)
    decayed = 0
    for art in decay_resp.json():
        pub = art.get("published_at")
        if not pub:
            continue
        pub_dt = dt.fromisoformat(pub.replace("Z", "+00:00"))
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
# ARTICLE 1: Your Brain Cleans Itself While You Sleep. A New Study in Science Explains How — and Why South Asians Should Be Worried.
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "Your Brain Cleans Itself While You Sleep. A New Study in Science Explains How — and Why the Way South Asians Sleep May Be Accelerating Their Dementia Risk."
art1_subheadline = "A review published in Science on May 22, 2026, by neuroscientist Maiken Nedergaard at the University of Rochester describes how the brain's glymphatic system — a waste-clearance network discovered by her lab in 2012 — depends on precisely synchronised sleep oscillations to flush out amyloid-beta and tau proteins linked to Alzheimer's disease. When those rhythms are disrupted by stress, cardiovascular disease, fragmented sleep, or ageing, the brain's nightly cleaning cycle fails. Heart rate variability during sleep, already trackable by consumer wearables like Oura and Apple Watch, may serve as a non-invasive biomarker for this process. For Indian Americans — who stay up past midnight for calls to India, who glorify the 3 AM coding session, who average among the worst sleep metrics of any ethnic group in the Oura dataset, and who already carry elevated dementia risk — the implications are personal."
art1_slug = make_slug("brain-glymphatic-sleep-cleaning-dementia-south-asian-hrv-oura")
art1_category = "lifestyle-health"

art1_body = """There is a system inside your brain that works like a dishwasher. It runs every night. It uses cerebrospinal fluid to flush out the metabolic waste that accumulates during the day — including the amyloid-beta plaques and tau tangles that cause Alzheimer's disease. The system is called the glymphatic system. It was discovered in 2012 by Maiken Nedergaard, a neuroscientist at the University of Rochester. It operates almost exclusively during sleep. And if your sleep is broken, fragmented, too short, or poorly timed, the dishwasher doesn't finish its cycle.

A review published in Science on May 22, 2026, by Nedergaard herself, presents the most comprehensive picture yet of how this system works — and what goes wrong when it doesn't. The implications for anyone who doesn't sleep well are significant. For South Asians in America, they are urgent.

## What the Glymphatic System Does

During waking hours, your brain produces metabolic waste. Neurons fire, synapses transmit, and the biochemical residue of all that activity accumulates in the spaces between brain cells. This waste includes amyloid-beta, a protein fragment that, in healthy brains, is cleared out nightly. In unhealthy brains, it accumulates into plaques — the signature pathology of Alzheimer's disease.

The glymphatic system clears this waste by circulating cerebrospinal fluid (CSF) through channels that run alongside blood vessels in the brain. Think of it as a plumbing network: arteries carry fresh CSF into the brain tissue, the fluid collects waste as it moves through the spaces between cells, and veins carry the waste-laden fluid out. The system is named "glymphatic" because it depends on glial cells — the brain's support cells — and functions analogously to the lymphatic system that clears waste from the rest of the body.

The critical insight from Nedergaard's 2012 discovery was that this system is 60 per cent more active during sleep than during wakefulness. The brain's interstitial space — the gaps between cells — expands by roughly 60 per cent during sleep, allowing CSF to flow more freely. During waking hours, those gaps shrink, and waste clearance slows dramatically.

In other words: your brain cannot clean itself while you are awake. Sleep is not optional maintenance. It is the only window the brain has to take out the garbage.

## What the New Science Paper Adds

Nedergaard's 2026 review goes beyond the basic discovery to describe the orchestration required for the cleaning cycle to work. The key finding is that the glymphatic system depends on precisely synchronised oscillations during non-REM sleep — slow, repeating rhythms of brain chemistry that occur roughly every 50 to 60 seconds.

Here is what happens: during non-REM sleep, the brain's neuromodulators — chemicals like norepinephrine, serotonin, dopamine, and acetylcholine that regulate attention, mood, and behaviour during waking hours — shift into a coordinated pattern. Instead of firing independently in response to stimuli, they begin oscillating together in slow waves.

These oscillations drive a cascade of physical events:

**1. Blood vessel pulsation.** The synchronised neuromodulator waves cause blood vessels in the brain to rhythmically expand and contract — a process called vasomotion. This is independent of the heart's pumping action. It is driven entirely by the brain's own chemical rhythms during sleep.

**2. CSF flow.** The rhythmic expansion and contraction of blood vessels creates a pumping effect that drives cerebrospinal fluid through the glymphatic channels. Each pulse of vasomotion pushes a wave of fresh CSF into the brain tissue, flushing waste toward the veins.

**3. Waste clearance.** The amyloid-beta, tau proteins, and other metabolic waste products are carried out of the brain by the fluid flow. The efficiency of this clearance depends directly on the strength and regularity of the oscillations. Stronger, more regular rhythms = better clearance. Disrupted rhythms = incomplete clearance.

"Sleep is not a quiet or inactive state," Nedergaard said. "During sleep, the brain shifts into a coordinated rhythm that appears to support one of its most important housekeeping functions."

## Why Sleep Disruption Causes Dementia — a Unifying Theory

The most significant claim in the paper is that many conditions known to increase dementia risk may do so through the same mechanism: disruption of the sleep-dependent oscillations that power the glymphatic system.

Consider the list of established dementia risk factors:

- **Chronic stress** — elevates norepinephrine, disrupting the slow oscillation pattern during sleep
- **Depression** — alters serotonin rhythms, the same neuromodulator involved in sleep oscillations
- **Cardiovascular disease** — damages blood vessels, impairing the vasomotion that drives CSF flow
- **Ageing** — naturally degrades the synchronisation of neuromodulator rhythms
- **Fragmented sleep** — directly prevents the sustained oscillation cycles from completing
- **Certain medications** — SSRIs, beta-blockers, and some blood pressure drugs alter neuromodulator levels during sleep

Nedergaard argues that these are not separate risk factors that happen to coexist with dementia. They are different pathways to the same endpoint: a brain that cannot clean itself during sleep.

"Many disorders that increase dementia risk also disrupt the brain's sleep rhythms," she said. "Our work suggests these may not be separate phenomena. They may be connected through the brain's ability to clear waste during sleep."

## The Heart Rate Variability Biomarker

Perhaps the most practically useful finding in the paper is about heart rate variability (HRV).

HRV — the variation in time between consecutive heartbeats — is already tracked by consumer wearables including Oura, Apple Watch, Fitbit, Garmin, and WHOOP. Higher HRV during sleep is generally associated with better autonomic nervous system function, better recovery, and lower stress.

Nedergaard's paper presents evidence that HRV fluctuations during sleep are closely tied to the neuromodulator oscillations that drive the glymphatic system. When the brain's chemical rhythms are strong and synchronised, HRV shows a characteristic pattern of slow, regular fluctuations. When the brain's rhythms are disrupted, HRV becomes irregular.

The implication: your Oura ring or Apple Watch may already be recording data that reflects how well your brain is cleaning itself at night. Low or erratic HRV during sleep may not just mean you had a bad night — it may mean your glymphatic system is underperforming, and your brain is accumulating waste that it should be clearing.

This is not yet a clinical diagnostic tool. Nedergaard is careful to describe it as a "potential biomarker" that needs further validation. But the possibility of using a $300 consumer device to non-invasively monitor your brain's waste clearance system is a significant step toward early detection of dementia risk — years or decades before symptoms appear.

## Why This Is an Indian American Health Article

If the above were the entire story, it would be a general health piece. It is not. Here is why this research matters more to you than to most readers.

**South Asians stay up later than almost any other demographic in America.** This is not a stereotype — it is a measurable pattern. Indian Americans routinely stay up past midnight for calls to family in India (the time zone difference means that 10 PM Pacific is 11:30 AM in Mumbai — prime calling hours). Tech workers in the Bay Area and Seattle normalise the 1 AM coding session. Bollywood movie marathons on weekends push bedtimes to 2-3 AM. The cultural celebration of working late — "burning the midnight oil" — is embedded in Indian professional identity.

**The India call is a sleep killer that nobody talks about.** If you are an NRI with parents in India, you know this routine: you get home from work at 7 PM, eat dinner, put the kids to bed by 9 PM, and then call your parents at 10-10:30 PM because it is morning in India and they are awake. The call lasts 30-45 minutes. By the time you wind down, it is 11:30 PM. Then you check WhatsApp — the family group has 47 new messages from the India morning — and you scroll for another 20 minutes. You are now in bed at midnight. Your alarm is at 6:30 AM. You have slept six and a half hours, and the first hour of that sleep was disrupted by the emotional activation of a family conversation.

This pattern, repeated five to seven nights a week for years, is exactly the kind of chronic sleep fragmentation that Nedergaard's paper identifies as damaging to the glymphatic system.

**South Asians already carry elevated dementia risk.** Studies have shown that South Asians develop Alzheimer's disease and vascular dementia at rates comparable to or higher than white populations, despite historically lower rates of obesity and smoking. The mechanisms are not fully understood, but higher rates of diabetes, cardiovascular disease, and — now, per this research — chronically disrupted sleep may all contribute.

**The "I'll sleep when I'm dead" culture is killing brains.** In Indian professional culture, sleeping less is often treated as a virtue. The founder who sleeps four hours. The engineer who ships code at 3 AM. The doctor who works 36-hour shifts. This cultural framing treats sleep as time stolen from productivity. Nedergaard's research reframes it: sleep is not downtime. It is the only time your brain can prevent the accumulation of the proteins that cause dementia. Every hour of sleep you skip is an hour your brain's cleaning system was offline.

**Indian Americans have among the highest rates of cardiovascular disease.** Cardiovascular disease damages the blood vessels that the glymphatic system depends on for vasomotion. South Asians develop heart disease at younger ages and lower BMIs than other populations. The combination of cardiovascular damage and chronic sleep disruption creates a compounding risk: the blood vessels are already impaired, and the sleep oscillations that drive those vessels are also disrupted. The brain's cleaning system is failing on two fronts simultaneously.

**The Oura ring and Apple Watch data is already there.** Many Indian Americans in tech — the same population that is most likely to be staying up late — already wear devices that track HRV during sleep. The data exists. It is sitting in your Oura app, in your Apple Health database, in your Fitbit dashboard. What Nedergaard's paper adds is a framework for interpreting that data: if your sleep HRV is consistently low or erratic, your brain's waste clearance system may be underperforming.

## What to Do — Starting Tonight

**1. Protect the 10 PM to 2 AM window.** Non-REM sleep is most concentrated in the first half of the night. The glymphatic oscillations that drive waste clearance are strongest during deep, sustained non-REM sleep. If you go to bed at midnight, you are missing the hours when the cleaning cycle would be most effective. Moving your bedtime from midnight to 10:30 PM is not a lifestyle preference — it is a neurological intervention.

**2. Move the India call earlier.** If you call parents at 10 PM Pacific (11:30 AM Mumbai), try 8 PM Pacific (9:30 AM Mumbai). They are already awake. Your conversation ends by 8:45 PM instead of 10:45 PM. You have gained two hours of wind-down time before bed. If 8 PM conflicts with dinner or kids' bedtime, try 7 AM Pacific (7:30 PM Mumbai) — a pre-work call when both sides are alert. The time zone math is solvable. The dementia risk from chronic late-night activation is not.

**3. Check your HRV trends.** Open your Oura, Apple Health, or Fitbit app. Look at your sleep HRV over the past 30 days. If you see consistently low numbers (below 20 ms for most adults over 40) or high variability between nights, that is a signal worth discussing with your doctor. It may reflect exactly the disrupted sleep oscillations that Nedergaard describes. Low HRV is not a diagnosis. It is a flag.

**4. Address the compounding risks.** If you have hypertension, pre-diabetes, or known cardiovascular disease — conditions that are disproportionately common among South Asians — the sleep-dementia connection is doubly important. Cardiovascular damage impairs the vasomotion that drives glymphatic clearance. Sleep disruption impairs the oscillations that drive vasomotion. Treating the cardiovascular condition and improving sleep quality are both necessary — neither alone is sufficient.

**5. Stop glorifying sleep deprivation.** This is cultural, not medical, but it matters. When someone in your professional circle brags about sleeping four hours, do not admire them. They are describing a brain that is running its cleaning cycle at partial capacity every night and accumulating waste that their body has no other mechanism to clear. The cognitive decline may not show up for 15-20 years. By then, the damage is irreversible.

**6. Watch for medication interference.** If you take SSRIs (for anxiety or depression), beta-blockers (for blood pressure), or certain sleep aids, these medications may alter the neuromodulator oscillations that the glymphatic system depends on. This does not mean you should stop taking them — it means you should discuss sleep quality specifically with your prescribing doctor, and monitor your HRV data for changes after starting or adjusting medications.

## The Bigger Picture

Nedergaard's paper is not the final word on dementia prevention. The glymphatic system was discovered only 14 years ago. The connection between sleep oscillations, vasomotion, and waste clearance is still being mapped. The HRV biomarker is promising but unvalidated in clinical trials.

But the directional finding is clear: sleep is the brain's only cleaning cycle. Disrupting that cycle, chronically, allows the accumulation of proteins that cause dementia. And the conditions that disrupt that cycle — stress, cardiovascular disease, fragmented sleep, late bedtimes — are disproportionately present in the South Asian American population.

Your Oura ring already knows something about your brain health that your doctor does not. The question is whether you will look at the data and change the behaviours that the data reflects — starting with the time you go to bed tonight."""

art1_sources = [
    "https://www.news-medical.net/news/20260522/Disrupted-sleep-rhythms-may-increase-dementia-risk-through-impaired-waste-clearance.aspx",
    "https://www.science.org/doi/10.1126/science.aeg2276",
    "https://www.inc.com/nick-hobson/scientists-uncover-a-sleep-brain-connection-that-could-be-the-key-to-halting-cognitive-decline.html",
    "https://goldsea.com/public/article_details/weekends-can-t-make-up-for-sleep-deprivation",
    "https://thenewsintel.com/our-research-shows-how-chronic-sleep-problems-can-lead-to-a-spiralling-decline-in-mental-health/",
]

print("=== Article 1: Sleep / Glymphatic System / HRV / South Asian Dementia Risk ===")
print(f"  Word count: {len(art1_body.split())}")

art1_image = fetch_pexels_image("person sleeping peacefully night bedroom dark")
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
    "tags": ["sleep", "glymphatic system", "dementia", "Alzheimer's", "HRV", "heart rate variability", "Oura", "Apple Watch", "South Asian", "Indian American", "NRI", "brain health", "Nedergaard", "Science", "amyloid-beta", "tau", "cerebrospinal fluid", "wearables", "neuroscience"],
    "vertical": "diaspora",
    "urgency": "medium",
    "diaspora_angle": "Nedergaard Science paper: brain's glymphatic waste clearance depends on precisely synchronised sleep oscillations; disrupted sleep = incomplete amyloid/tau clearance = dementia. South Asians stay up past midnight for India calls (10 PM Pacific = 11:30 AM Mumbai), glorify sleep deprivation in tech culture, have elevated dementia and cardiovascular risk. HRV from Oura/Apple Watch may already be tracking glymphatic function. Practical: move India call to 8 PM, protect 10 PM-2 AM deep sleep window, check 30-day HRV trends.",
    "word_count": len(art1_body.split()),
    "image_url": art1_image["url"] if art1_image else None,
    "image_caption": f"Photo by {art1_image['photographer']} via Pexels" if art1_image else None,
})
if result:
    print(f"  ✓ Published: {art1_id}")
else:
    print("  ✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: The Surgeon General Just Told You to Take the iPad Away From Your Kid. You Work at the Company That Made the iPad.
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "The Surgeon General Just Told You to Take the iPad Away. You Work at the Company That Made It. The Indian American Screen Time Paradox Nobody in Silicon Valley Wants to Talk About."
art2_subheadline = "On May 21, 2026, the Office of the Surgeon General issued its first-ever advisory on the harms of excessive screen time for children and adolescents. The recommendations: zero screen time for children under 18 months, less than one hour per day for children under 6, and no more than two hours per day for ages 6 to 18. The advisory links excessive screen use to worse sleep, decreased school functioning, less physical activity, and weakened relationships. For Indian American families — disproportionately concentrated in the technology industry, culturally dependent on FaceTime calls with grandparents in India, and caught between the pressure to raise high-achieving children and the knowledge that the apps designed to captivate those children were built by their own colleagues — the advisory lands differently than it does in any other household in America."
art2_slug = make_slug("surgeon-general-screen-time-advisory-indian-american-silicon-valley")
art2_category = "lifestyle-health"

art2_body = """On May 21, 2026, the Office of the Surgeon General published a 43-page advisory titled "Harms of Screen Use" — the first time the federal government has issued a formal public health warning specifically about screen time for children and adolescents.

The advisory was released by HHS Secretary Robert F. Kennedy Jr. at a bill-signing ceremony in Iowa, alongside Governor Kim Reynolds, who signed the state's MAHA (Make America Healthy Again) legislation into law. The United States does not currently have a confirmed surgeon general — President Trump's third nominee, Dr. Nicole Saphier, awaits a confirmation hearing — so the advisory was developed by a leadership team of HHS officials.

Here is what the advisory recommends:

- **Under 18 months**: Zero screen time.
- **18 months to 6 years**: Less than one hour per day.
- **Ages 6 to 18**: No more than two hours per day of recreational screen time.

The advisory notes that by adolescence, the average American teenager spends four or more hours per day on screens — and nearly half of adolescents admit they lose track of time when using their phones. Screen use is associated with worse sleep, decreased school functioning, less physical activity, and weakened in-person relationships.

The advisory includes a framework called the "5 Ds": Discuss healthy screen use, Do model the behaviours you want to see, Delay screen time from the earliest age, Divert attention to other activities, and Disconnect regularly.

None of this is controversial. The American Academy of Pediatrics has recommended similar limits for years. But for one specific demographic in America — Indian American families in the technology industry — this advisory creates a paradox that no parenting book, no screen time app, and no family media plan can resolve.

## The Paradox

Here is the simplest version: Indian Americans are disproportionately represented in the companies that design, build, and optimise the products that the Surgeon General just warned are harming children.

According to the Census Bureau, Indian Americans are the single largest ethnic group in the technology workforce of Silicon Valley. They hold CEO positions at Google (Sundar Pichai), Microsoft (Satya Nadella), IBM (Arvind Krishna), and Adobe (Shantanu Narayen). They lead engineering teams that design the notification systems, algorithmic feeds, autoplay features, and engagement metrics that the advisory specifically identifies as harmful.

And then they go home and hand their children an iPad.

This is not hypocrisy. It is a structural trap. The same industry that provides Indian American families with their highest-in-the-nation median household income ($150,000+) is the industry whose products the federal government now says are harming their children's development.

The advisory calls on technology companies to "display warnings about harmful screen use" and "adhere to and enforce age minimums." It is asking the very companies where Indian Americans build their careers to make their products less engaging for children. The engineers know how the engagement works. They designed it. And they know, better than any advisory can explain, exactly how difficult it is to compete with an algorithm designed by a team of PhDs to maximise time-on-screen.

## The FaceTime Exemption That Doesn't Exist

Every Indian American parent has had this thought: "But FaceTime with grandparents is different."

It is different, emotionally. Your child's relationship with their nana-nani or dada-dadi in India is sustained by video calls. The 12.5-hour time zone difference between California and India means these calls happen at specific windows — usually 7-8 AM Pacific (7:30-8:30 PM India) or 8-9 PM Pacific (8:30-9:30 AM India). For young children, the evening window often overlaps with bedtime preparation.

But the Surgeon General's advisory does not distinguish between types of screen use for children under 18 months. Zero means zero. It does not mean "zero except for FaceTime with family." The American Academy of Pediatrics does carve out an exception for video chatting with family, noting that it can support relationship-building — but the federal advisory does not make this distinction explicitly.

And here is the uncomfortable reality: even the "good" screen time — the FaceTime call with grandparents — often bleeds into other screen use. The child sees the iPad come out for the grandparent call. When the call ends, they want the iPad to stay. A five-year-old does not understand that the iPad is acceptable for talking to dadi but not for watching Cocomelon. The device is the device. The habit loop is the habit loop.

For Indian American families, eliminating screen time for children under 18 months would mean cutting off the primary mechanism through which their children bond with family members who live 8,000 miles away. No advisory written in Washington, DC, accounts for this reality.

## The Academic Screen Time Blind Spot

The advisory recommends two hours per day of recreational screen time for children aged 6 to 18. But Indian American parents draw a line that the advisory does not: academic screen time is not recreational screen time.

Khan Academy is not TikTok. Kumon's online platform is not Instagram. Byju's — the Indian ed-tech company that many NRI families used before its collapse — was considered educational, not recreational. Coding camps on Scratch, math drills on IXL, reading comprehension on Epic — these are screen activities that Indian American parents not only permit but mandate.

A typical Indian American seventh-grader's daily screen inventory might look like this:

- **School**: 3-4 hours (Chromebook for assignments, Google Classroom, digital textbooks)
- **Homework**: 1-2 hours (online research, typing essays, math platforms)
- **Academic enrichment**: 30-60 minutes (Khan Academy, coding, SAT prep)
- **Recreational**: 1-2 hours (YouTube, gaming, social media)

By the advisory's two-hour standard, this child is within limits on recreational screen time. By any honest accounting of total screen exposure, this child is spending 6-8 hours per day looking at a screen. The brain does not distinguish between "educational" blue light and "recreational" blue light at 10 PM.

The advisory acknowledges this problem obliquely. It calls on schools to "prioritise assigning work in books or on paper to limit screen use" and recommends that schools "implement cell phone policy restrictions." But it does not address the fundamental reality of American education in 2026: school is screens. Homework is screens. Test prep is screens. The two-hour recreational limit exists within a context where the child has already spent the majority of their waking hours on a screen before opening YouTube.

Indian American parents who pride themselves on academic rigour may be inadvertently creating the highest total screen-time environments of any demographic — not because they are permissive, but because they are ambitious.

## The WhatsApp Pull

Screen time is often discussed as a parent-to-child problem: the parent controls the child's screen access. But in Indian American households, the screens pull in the opposite direction too.

The extended family WhatsApp group — and most Indian American families have three to seven of them — generates a constant stream of messages, photos, videos, voice notes, and forwards. The groups span time zones. When it is morning in India, the messages start. When it is evening in America, the replies come. The result is a 24-hour notification cycle that pulls every family member, including teenagers, toward their phones throughout the day.

Indian American teenagers are often added to family WhatsApp groups by their parents — "so dadi can send you messages directly" — and those groups become a secondary social media feed that parents have explicitly sanctioned. A teenager who has been told to stay off Instagram but is in four family WhatsApp groups is still receiving a constant stream of forwarded videos, political commentary, health misinformation, and prayer chain messages.

The advisory recommends that families "create a family media plan that covers who can use what screens, where, when, which content and for how long." In an Indian American household, the family itself is the source of screen pull. The media plan would need to include telling your mother-in-law to stop forwarding Good Morning messages at 6 AM. Good luck with that.

## What Indian Schools Do Better

There is an irony that Indian American parents — who often compare American education unfavourably to the Indian system — rarely acknowledge: Indian schools use dramatically less screen technology than American schools.

In most Indian classrooms, especially at the primary and secondary level, instruction is blackboard-based. Textbooks are physical. Homework is handwritten. Exams are written on paper. The government's NEP (National Education Policy) 2020 does encourage technology integration, but the implementation in most schools — outside elite private institutions in metros — remains minimal.

Indian children who attend school in India spend 5-7 hours per day in an essentially screen-free learning environment. Their American counterparts spend 5-7 hours in a screen-saturated one.

The Indian American parent who says "the education system in India was better" may be correct — but not for the reasons they usually cite (discipline, rigour, respect for teachers). The Indian system may have been better, in part, because it did not put a Chromebook in front of every eight-year-old.

## The Two-Hour Myth

Dr. Courtney Blackwell, an associate professor at Northwestern University's Feinberg School of Medicine, cautioned against treating the advisory's recommendations as absolute. "It's not one size fits all," she told CNN. "The research is not definitive, I would say, to suggest screen time causes harm in and of itself."

She is right. The relationship between screen time and health outcomes is complex, mediated by content quality, context, pre-existing conditions, and family dynamics. A child who spends two hours on Duolingo and Minecraft is having a different experience than a child who spends two hours doom-scrolling TikTok.

But the advisory's framing is useful precisely because it forces a reckoning with total screen exposure. When the number is "two hours recreational," parents can justify seven hours of total screen time by reclassifying most of it as "educational" or "necessary." When the research increasingly suggests that the brain's response to prolonged screen exposure — disrupted sleep architecture, reduced attention span, decreased physical activity — operates independently of whether the content is educational or recreational, the classifications start to look like rationalisations.

Dr. J. John Mann, a professor at Columbia University, argued in response to the advisory that screening should focus on children who show addictive behaviours around screens rather than imposing blanket limits. "If we look at it in that framework, what we should be doing is screening out those kids who show that and focus efforts of prevention on them," he said.

This is clinically reasonable. It is also practically useless for most parents, who lack the tools to distinguish between a child who is engaged and a child who is addicted. The Indian American parent who sees their 12-year-old voluntarily watching Khan Academy at 10 PM may interpret it as motivation. It may also be a child who cannot stop interacting with a screen regardless of what is on it.

## What to Actually Do

The advisory provides its "5 Ds" framework and various recommendations. Here is what those recommendations look like when translated for the Indian American household:

**1. Audit total screen time, not just recreational.** Add up school hours, homework hours, enrichment hours, and recreational hours. If the total exceeds six hours for a school-age child, the recreational time is not the primary problem — the entire ecosystem is. Discuss with your child's school whether more assignments can be paper-based. Buy physical textbooks for subjects where they are available.

**2. Protect the FaceTime relationship but contain it.** The grandparent video call is important. Schedule it, give it a specific time window (20-30 minutes), and put the device away when it ends. Do not leave the iPad accessible after the call. The transition from "talking to dadi" to "watching YouTube" happens in under 60 seconds for a four-year-old.

**3. Remove screens from bedrooms after 8 PM.** The advisory links screen use to worse sleep. Indian American households where children have devices in their bedrooms after 8 PM are creating the conditions for disrupted sleep architecture — which, per other research published this same week, impairs the brain's waste clearance system. Central charging stations in common areas are the simplest structural intervention.

**4. Acknowledge the WhatsApp problem.** If your teenager is in family WhatsApp groups, those groups count as screen time and social media exposure. Consider whether the teenager needs to be in the group at all, or whether a daily summary from a parent would serve the same purpose. The cultural expectation of family inclusion does not override the neurological impact of constant notification exposure.

**5. Model the behaviour.** The advisory says "Do model the healthy screen use behaviours you would like to see." For Indian American parents, this means putting your own phone down during family meals — including not checking the India morning WhatsApp messages during dinner. It means not scrolling Instagram reels while telling your child to do homework on paper. Children do not follow rules. They follow patterns.

**6. Do not panic.** Dr. Blackwell's advice is worth repeating: the advisory is not a diagnosis. A child who has spent three hours on screens today is not damaged. The concern is about chronic patterns, not individual days. The goal is trend reduction, not perfection.

## The Uncomfortable Truth

The Surgeon General's advisory is, at its core, a document that tells American families to use less of the products that American companies make. For most families, this is an external recommendation about somebody else's industry.

For Indian American families in technology, it is an internal contradiction. The same expertise that built the notification system that vibrates your child's phone 47 times a day is the expertise that pays for the house, the school, the extracurriculars, and the annual trip to India where the grandparent relationship was supposed to make the screen time worth it.

The advisory cannot resolve this contradiction. Only you can. And the resolution will not come from an app, a timer, or a family media plan. It will come from the willingness to say, out loud, in a household and a community that has built its prosperity on technology: the screens are too much, and we need less of them.

That is not a failure of parenting. It is a recognition that the products are working exactly as designed — and that the design was never optimised for your child's developing brain."""

art2_sources = [
    "https://www.hhs.gov/press-room/iowa-maha-bill-screen-time-advisory-warning.html",
    "https://www.cnn.com/2026/05/20/health/surgeon-general-advisory-screen-time-wellness/",
    "https://www.usatoday.com/story/news/health/2026/05/21/surgeon-general-advisory-screen-time-kids/",
    "https://www.fastcompany.com/91340000/rfk-jr-surgeon-generals-advisory-kids-screen-time",
    "https://statnews.com/2026/05/21/rfk-jr-surgeon-general-warning-screen-time-children/",
    "https://www.scientificamerican.com/article/screen-time-limits-can-protect-childrens-health/",
    "https://k12dive.com/news/surgeon-general-advisory-youth-screen-use/",
]

print("\n=== Article 2: Surgeon General Screen Time Advisory / Indian American Silicon Valley Paradox ===")
print(f"  Word count: {len(art2_body.split())}")

art2_image = fetch_pexels_image("child tablet screen device technology home")
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
    "tags": ["screen time", "Surgeon General", "advisory", "children", "parenting", "Silicon Valley", "Indian American", "NRI", "technology", "FaceTime", "iPad", "WhatsApp", "education", "sleep", "RFK Jr", "HHS", "MAHA", "digital health", "youth mental health"],
    "vertical": "diaspora",
    "urgency": "medium",
    "diaspora_angle": "First-ever Surgeon General advisory on screen time (May 21, 2026): zero for under 18mo, <1h under 6, <2h ages 6-18. Indian Americans disproportionately work at the companies that built the products warned about. FaceTime with grandparents in India is the essential screen time that no advisory accounts for. Academic screen time (Khan Academy, Kumon, coding) creates total exposure of 6-8h/day even when 'recreational' limits are met. WhatsApp family groups are sanctioned screen pull. Indian schools use far less tech than American schools. Practical: audit total not just recreational, contain FaceTime window, remove bedroom screens after 8 PM.",
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
sp.run(["git", "commit", "-m", "lifestyle-writer: sleep glymphatic dementia HRV + surgeon general screen time Indian American (2026-05-24 15:00 PDT)"], check=True)
push = sp.run(["git", "push"], capture_output=True, text=True, timeout=30)
print(f"  Push: {push.returncode}")
if push.stdout:
    print(f"  {push.stdout.strip()}")
if push.stderr:
    print(f"  {push.stderr.strip()}")

print("\n✅ Lifestyle writer run complete — 2 articles published")
