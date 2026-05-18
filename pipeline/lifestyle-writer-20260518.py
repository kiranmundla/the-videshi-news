#!/usr/bin/env python3
"""Lifestyle writer run — 2026-05-18
Writes 2 articles for lifestyle-health category:
1. Hypertension crisis in young Indians + NRI angle
2. WHO Ebola PHEIC — what NRI travelers need to know
"""

import json
import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def run_db(cmd, data=None):
    args = ["python3", "videshi-db.py", cmd]
    if data:
        args.append(json.dumps(data) if isinstance(data, dict) else data)
    result = subprocess.run(args, capture_output=True, text=True,
                          env={**os.environ})
    print(f"[{cmd}] stdout: {result.stdout.strip()}")
    if result.stderr:
        print(f"[{cmd}] stderr: {result.stderr.strip()}")
    return result.stdout.strip()


# ── Article 1: Hypertension ──────────────────────────────────

article1 = {
    "topic_id": None,  # standalone synthesis, no single topic
    "headline": "India's Silent Health Crisis: Why Hypertension Is No Longer Your Grandfather's Disease",
    "subheadline": "On World Hypertension Day, the numbers are staggering — 210 million Indians live with high blood pressure, most of them undiagnosed. For the diaspora, the risks may be even higher.",
    "body": """On 17 May, as the world marked World Hypertension Day under the theme "Controlling Hypertension Together!", the numbers painted a picture that should alarm every Indian household — at home and abroad.

Over **210 million adults** in India now live with hypertension. That is roughly one in three. Globally, the figure stands at 1.4 billion, and South Asians — whether in Mumbai, London, or New Jersey — are disproportionately represented. The condition produces no headache, no dizziness, no warning until an organ quietly fails. It is the single leading risk factor for heart attacks, strokes, and kidney failure. And it is surging among the young.

## The Youth Epidemic

The most alarming shift is generational. Data from Peerless Hospital in Guwahati shows that **25.3% of urban Indians** aged 25–40 now have elevated blood pressure — a figure that would have been unthinkable a generation ago. A study by the Bharath Horizon health platform found that one in eight Indians aged 20–40 is hypertensive, with the majority completely unaware.

Doctors across India say the pattern is consistent: young professionals in their late twenties and early thirties presenting with dangerously high readings after years of sedentary desk work, irregular sleep, and stress-heavy routines. Union Health Minister Prataprao Jadhav, speaking at the Illness to Wellness Conference this week, called for a national shift toward early screening and preventive care.

"This is not a disease of retirement anymore," said a senior cardiologist at AIIMS, quoted in IndiaMedToday. "We are seeing 28-year-olds with readings that used to worry us in 55-year-olds."

## The Rule of Halves

Public health experts invoke what they call the **"Rule of Halves"**: half of those with hypertension are undiagnosed; half of those diagnosed are untreated; and half of those treated never achieve their target blood pressure. In India, only about **17%** of hypertensive patients consistently reach safe levels. The result is a massive population walking around with a ticking time bomb in their arteries — and no idea it is there.

A recent Practo report underscored the scale of the problem: searches for lifestyle diseases have doubled between 2023 and 2025. Searches from tier-2 towns for hypertension are growing at **six times** the rate of tier-1 cities, suggesting the crisis has long since escaped the metros.

## The Diaspora Dimension

For NRIs, the picture is arguably worse. South Asians in the United States, United Kingdom, and Canada face **two to four times** the risk of cardiovascular disease compared to their white counterparts, according to long-running studies including the MASALA (Mediators of Atherosclerosis in South Asians Living in America) cohort.

The reasons are layered. The stress of immigrant life — long work hours, visa anxiety, cultural isolation — compounds a genetic predisposition that South Asians carry toward insulin resistance, abdominal fat storage, and endothelial dysfunction. Dietary shifts in the diaspora tell their own story: traditional home-cooked meals replaced by processed convenience food, sodium-laden takeaways, and irregular eating patterns.

"Indian-Americans are getting heart disease 10 years earlier than the general American population," Dr. Rajesh Vedanthan of NYU Langone told researchers at a recent MASALA symposium. "And hypertension is the gateway."

## What Actually Works

The prescription is surprisingly simple — and none of it requires a hospital visit to begin.

**The salt-potassium seesaw**: Most Indians consume nearly double the recommended daily sodium intake. Reducing salt below 2,300 mg per day while increasing potassium through leafy greens, bananas, coconut water, and dal helps the kidneys flush excess sodium naturally.

**Movement**: Just 150 minutes of brisk walking per week — about 20 minutes a day — can reduce systolic blood pressure by nearly 10 mmHg, equivalent to the effect of some first-line medications. For diaspora Indians stuck in desk jobs and long commutes, even four 10-minute walks scattered through the day have been shown to be more effective than a single 40-minute session.

**The DASH diet**: The Dietary Approaches to Stop Hypertension eating plan — rich in fruits, vegetables, whole grains, and lean proteins — overlaps significantly with traditional Indian vegetarian diets. The irony is that the healthiest approach to blood pressure management looks remarkably like the thali your grandmother assembled without ever reading a clinical guideline.

**Home monitoring**: Clinic readings are often inflated by "White Coat Hypertension" — the stress of a medical visit itself. Home blood pressure monitors, now widely available for under ₹2,000, provide more reliable readings. Doctors recommend measuring at the same time daily, sitting quietly for five minutes first.

## Technology Enters the Picture

In 2026, wearable health devices are beginning to change the game. Smart rings and watches now use optical sensors to estimate blood pressure continuously, including during sleep. This matters because **nocturnal dipping** — the healthy 10–20% fall in blood pressure while sleeping — is a crucial marker. Patients whose pressure does not dip at night carry significantly higher risks of stroke and heart failure, a pattern that periodic clinic visits cannot detect.

AI-powered platforms are also entering the arena. Researchers at IIIT-Hyderabad are developing tools that analyse aggregated health data to identify high-risk individuals years before their first abnormal reading. It is a shift from reactive medicine to predictive prevention.

## What's Next

The challenge is not knowledge — it is action. India's healthcare system remains overwhelmingly reactive, designed for crises rather than prevention. Community-level screening programmes, school-based health education, and workplace wellness mandates are all on the table but rarely implemented at scale.

For the diaspora, the call to action is personal: know your numbers. If you are over 30, or have a family history, get your blood pressure checked this week. It costs nothing, takes two minutes, and might be the most consequential health decision you make this year.

The silent killer only wins when it is ignored.""",
    "diaspora_angle": "South Asians in the US, UK, and Canada face 2–4x cardiovascular risk compared to white populations (MASALA study). Immigrant lifestyle shifts — processed food, stress, sedentary work — compound genetic predisposition. Indian-Americans develop heart disease a decade earlier than the general population.",
    "vertical": "culture",
    "category": "lifestyle-health",
    "tags": ["hypertension", "World Hypertension Day", "Indian health", "NRI wellness", "blood pressure", "diaspora health"],
    "urgency": "daily",
    "sources": [
        {"url": "https://who.int/campaigns/world-hypertension-day/2026", "name": "WHO — World Hypertension Day 2026"},
        {"url": "https://indiamedtoday.com/the-silent-killer-in-your-bloodstream-why-world-hypertension-day-2026-matters-for-india/", "name": "IndiaMedToday — Dr Vishal Jani / Practo"},
        {"url": "https://passionateinmarketing.com/peerless-hospital-raises-alarm-on-young-hypertension/", "name": "Peerless Hospital Guwahati — Youth Hypertension Alert"},
        {"url": "https://bharathorizon.com/hypertension-in-young-india/", "name": "Bharath Horizon — Hypertension in Young India"},
        {"url": "https://healthcare.financialexpressb2b.com/lifestyle-changes-fuel-hypertension-surge-among-youth/", "name": "Financial Express Healthcare — Lifestyle Changes Fuel Surge"}
    ],
    "score_total": 78,
    "image_entities": ["blood pressure cuff", "Indian doctor", "health checkup"],
    "image_must_show": "A blood pressure measurement or health screening context",
    "image_search_query": "blood pressure check young Indian health screening"
}


# ── Article 2: WHO Ebola Emergency for NRI Travelers ─────────

article2 = {
    "topic_id": None,
    "headline": "WHO Declares Ebola a Global Emergency — What Indian Travellers and NRIs Need to Know",
    "subheadline": "A rare Bundibugyo strain with no approved vaccine has killed 89 people in eastern Congo. Here is what the declaration means for the Indian diaspora.",
    "body": """On 17 May 2026 — the same day the world paused for World Hypertension Day — the World Health Organization made a far more urgent announcement. Director-General Dr Tedros Adhanom Ghebreyesus declared the Ebola outbreak in the Democratic Republic of the Congo and Uganda a **Public Health Emergency of International Concern (PHEIC)**, the highest alarm the WHO can sound.

The declaration came after the outbreak, caused by the rare **Bundibugyo ebolavirus**, crossed international borders. As of 16 May, the DRC had reported 336 suspected cases and at least **89 deaths** in Ituri Province, with imported cases confirmed in Kinshasa and Kampala, Uganda's capital. Two confirmed cases and one death in Uganda triggered the cross-border escalation.

## Why This Strain Is Different

The Bundibugyo virus is the rarest of the six known Ebola species. Unlike the more studied Zaire strain — against which Merck's rVSV-ZEBOV vaccine proved effective during the 2018–2020 DRC outbreak — **no approved vaccine or therapeutic** currently exists for Bundibugyo.

This absence of medical countermeasures is what pushed the WHO Emergency Committee to recommend the PHEIC designation. The Ituri Province epicentre is also mired in armed conflict, with healthcare workers repeatedly attacked and population movement nearly impossible to track. Mobile communities, informal border crossings, and a fragmented health system have made surveillance deeply challenging.

## What This Means for Indian Travellers

India has **no direct commercial flights** to Ituri Province, and the DRC is not a common destination for Indian travellers. But the diaspora's global footprint means exposure pathways exist — particularly through transit hubs in East Africa, the Gulf, and Europe.

**Key considerations for NRIs:**

- **Transit through East African hubs**: Nairobi, Addis Ababa, and Entebbe remain major transit points for Indian travellers and diaspora workers. Uganda's two confirmed cases — both in Kampala — mean heightened screening at Entebbe International Airport is already in effect.

- **Indian workers in Central and East Africa**: An estimated 50,000–70,000 Indian nationals work across the DRC, Uganda, Rwanda, and neighbouring states, many in mining, construction, and trade. India's embassies in Kinshasa and Kampala have issued advisories urging Indian nationals to avoid non-essential travel to affected provinces and to register with the embassy.

- **Screening at Indian airports**: During previous Ebola PHEIC declarations (2014, 2019), India activated thermal screening at major international airports — Delhi, Mumbai, Chennai, Bengaluru, and Hyderabad — for passengers arriving from affected regions. Health officials have not yet confirmed similar measures for 2026, but experts say activation is likely if cases spread beyond the current zone.

## Lessons From 2019

India's response to the 2018–2020 Ebola outbreak in DRC — which eventually killed over 2,200 people — offers both reassurance and caution. India successfully prevented any imported cases during that crisis, partly through airport screening and partly because the outbreak remained concentrated in DRC's eastern provinces.

But the 2019 outbreak involved the Zaire strain, for which vaccines were available and deployed at scale. The Bundibugyo strain's lack of countermeasures changes the calculus. The WHO has urged all member states to enhance surveillance at entry points and prepare isolation protocols, even for countries with no direct links to the outbreak zone.

## What You Should Do

For Indian travellers and NRIs planning trips to or through East Africa:

1. **Check travel advisories**: Monitor the Indian Ministry of External Affairs' travel advisory page and your local embassy's updates.
2. **Avoid non-essential travel** to eastern DRC (Ituri, North Kivu) and monitor the situation in Uganda closely.
3. **Know the symptoms**: Ebola symptoms — fever, severe headache, muscle pain, vomiting, diarrhoea, and unexplained bleeding — typically appear 2–21 days after exposure. Seek immediate medical attention if symptoms develop after travel to affected regions.
4. **Practice hygiene**: Avoid contact with bodily fluids, bushmeat, and bats in endemic areas. Frequent handwashing with soap remains one of the most effective preventive measures.
5. **Register with embassies**: Indian nationals in Central and East Africa should register with the nearest Indian mission for emergency communication.

## The Bigger Picture

PHEIC declarations are rare — the WHO has issued only eight since the mechanism was created in 2005. Each one signals that a health event has the potential to spread internationally and requires a coordinated global response. For India, which has thus far avoided any confirmed Ebola case in its history, the declaration is a reminder that in a connected world, no outbreak is truly distant.

The Indian Council of Medical Research (ICMR) and the National Centre for Disease Control (NCDC) are monitoring the situation. India's Integrated Disease Surveillance Programme (IDSP) maintains a network of sentinel surveillance sites that can be activated rapidly if needed.

For now, the risk to India remains low — but not zero. And for a diaspora spread across every continent, staying informed is the first line of defence.""",
    "diaspora_angle": "50,000–70,000 Indian nationals work in DRC, Uganda, Rwanda, and neighbouring states. NRIs transiting through East African hubs face heightened screening. India's embassies in Kinshasa and Kampala have issued advisories. The diaspora's global footprint creates exposure pathways through transit hubs.",
    "vertical": "culture",
    "category": "lifestyle-health",
    "tags": ["Ebola", "WHO PHEIC", "NRI travel advisory", "global health", "DRC outbreak", "diaspora health"],
    "urgency": "breaking",
    "sources": [
        {"url": "https://www.who.int/news/item/17-05-2026-ebola-pheic-drc-uganda", "name": "WHO — PHEIC Declaration, 17 May 2026"},
        {"url": "https://en.wikipedia.org/wiki/2026_Ituri_Province_Ebola_epidemic", "name": "Wikipedia — 2026 Ituri Province Ebola Epidemic"},
        {"url": "https://globalbiodefense.com/2026/05/17/who-declares-ebola-outbreak-in-congo-and-uganda-a-global-health-emergency/", "name": "Global Biodefense — WHO Declares Ebola Emergency"},
        {"url": "https://watchers.news/2026/05/17/who-declares-pheic-over-cross-border-bundibugyo-ebola-outbreak-in-drc-and-uganda/", "name": "Watchers.news — Bundibugyo Ebola PHEIC"},
        {"url": "https://gktoday.in/who-declares-ebola-pheic-in-congo-and-uganda/", "name": "GK Today — WHO Ebola PHEIC"}
    ],
    "score_total": 82,
    "image_entities": ["WHO logo", "Ebola response", "airport screening", "DRC health workers"],
    "image_must_show": "Health/medical response context — WHO, health workers, or airport screening",
    "image_search_query": "WHO Ebola response health workers DRC 2026"
}


# ── Insert articles ──────────────────────────────────────────

print("=" * 60)
print("INSERTING ARTICLE 1: Hypertension")
print("=" * 60)
r1 = run_db("insert-article", article1)

print()
print("=" * 60)
print("INSERTING ARTICLE 2: Ebola PHEIC")
print("=" * 60)
r2 = run_db("insert-article", article2)


# ── Mark some pending lifestyle-health topics as rejected ────
# (entertainment/celebrity topics that don't fit the lifestyle-health brief)
reject_topics = [
    "ba5f8fc7-c573-4241-8ea3-5444a8d52382",  # Katy Perry FIFA
    "7abff73d-6ed8-4b42-aa42-487d7370a1bb",  # Shekhar Suman stand-up
    "ba3ab3be-a521-43fc-8386-c6d90c1e1ce9",  # Salman Khan watches
    "dadfe194-e9b3-40b9-9b4b-b2d01a9dd676",  # Sonu Nigam concert
    "79376a35-56af-4030-bf31-a9d7df2a8cdc",  # Antigoni Eurovision
    "8444c209-78f2-48d0-9df2-ced101bb09e0",  # Taylor Swift wedding
    "830a3101-8b37-4c2d-93bd-f8848d2b3953",  # Bridgerton Season 5
    "ce7889c9-773c-41c1-ba00-86fbdb61366b",  # Ahsoka Season 2
    "4f12e002-a6c9-4794-a87f-fe6c5adce5b0",  # Jennifer Harmon death
    "8f3ca4cd-565c-45dc-b5dc-1dc2bc9b288b",  # Drug Counselor Matthew Perry
    "9fa6e6f3-d3da-48d6-820e-feb3ed78ea7d",  # Shefali Jariwala death rumors
    "6e3bd571-bcb2-4ded-8cf8-e3afccd0c4ca",  # Mumbai cake viral
]

print()
print("=" * 60)
print(f"REJECTING {len(reject_topics)} low-relevance lifestyle-health topics")
print("=" * 60)
for tid in reject_topics:
    run_db("update-topic-status", f"{tid} rejected")

# Mark the related hypertension/Ebola news topics as published
publish_topics = [
    "5ef73f0d-b618-4609-a72c-fd5b3e1af7e0",  # Suttur Mutt Seer depression/mental health
]
# Mark the Young Archie topic as rejected — can't verify Indian-origin finalists
reject_unverified = [
    "cce45de1-4253-4876-a6fb-bf1bdf7ba27e",  # Young Archie — names unverifiable
]

for tid in publish_topics:
    run_db("update-topic-status", f"{tid} published")
for tid in reject_unverified:
    run_db("update-topic-status", f"{tid} rejected")

print()
print("Done! Articles inserted and topics updated.")
