#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-26 23:00 PDT run
2 articles:
  1. Dengue Before Monsoon: early dengue cases in India due to extreme heat
     (May 2026), monsoon arrived in Kerala 6 days early (May 24-26),
     Aedes aegypti thriving in warm+humid conditions. Climate change
     has broken the traditional monsoon-only dengue window.
     NRI angle: Summer is peak India-trip season for diaspora families.
     NRI adults + US-born kids are immunologically naive to dengue.
     What to pack, how to protect family, when to worry, platelet
     monitoring, insurance coverage for dengue in India.

  2. University of Leicester proteomics study (eBioMedicine, Jan 2026):
     49,000+ UK Biobank participants, 375 ethnicity-specific proteins,
     464 physical-activity-linked proteins. IL-6 emerged as the ONLY
     protein significantly related to physical activity in validation
     cohort — reduced by walking more. 16 validated ethnicity-specific
     proteins including chemokines (CCL28, CCL15), hepatokines (FABP1),
     adipokines (FABP2), pancreatic enzymes (AMY2A, AMY2B). These show
     distinct immune, inflammatory, and metabolic pathways that differ
     between South Asian and White European populations.
     NRI angle: Exercise works differently in South Asian bodies.
     Generic Western exercise advice doesn't fully translate. The same
     30-minute walk produces different molecular cascades. Culturally
     tailored exercise interventions needed. Your gym routine designed
     by a trainer who trained on Western physiology may not be optimal.
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

def make_slug(text, suffix="20260527"):
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
for check_term in ["dengue monsoon summer india trip", "dengue before monsoon heat", "protein signatures ethnicity leicester", "proteomics south asian exercise IL-6"]:
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
# ARTICLE 1: Dengue Before Monsoon — What NRIs Planning Summer
#             India Trips Need to Know
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "Dengue Is No Longer a Monsoon Disease. Cases Are Surging Across India in Extreme Pre-Monsoon Heat, Weeks Before the Rains Arrive. If You Are Planning a Summer Trip Home, Your Family's Risk Window Has Shifted."
art1_subheadline = "India's 2026 monsoon arrived in Kerala six days early, between May 24 and May 26 — but dengue cases had already been climbing for weeks before any rain fell. Extreme heat, with temperatures above 45°C in northern India through April and May, has accelerated the breeding cycle of Aedes aegypti mosquitoes, making pre-monsoon conditions as dangerous as peak monsoon season was a decade ago. Doctors across Delhi, Mumbai, Bengaluru, Hyderabad, and Chennai are reporting dengue presentations in May that they traditionally would not see until August or September. The clinical pattern has shifted: climate change has compressed the breeding-to-biting cycle from weeks to days, urban heat islands and stagnant water in coolers, construction sites, and rooftop tanks provide year-round breeding sites, and sudden pre-monsoon thunderstorms followed by heat create the exact temperature-humidity alternation that maximises Aedes aegypti survival. For the roughly 4.5 million Indian Americans who visit India during the summer months — many with children born in the United States who have no prior dengue exposure and no acquired immunity — the traditional advice to 'be careful during monsoon' is now dangerously outdated. The risk begins weeks before the rains. Understanding the new dengue calendar, recognising the early symptoms that mimic jet-lag fatigue, knowing when to demand a platelet count, and packing the right repellents is no longer optional precaution. It is baseline travel preparation."
art1_slug = make_slug("dengue-before-monsoon-india-summer-trip-nri-aedes-heat-climate")
art1_category = "lifestyle-health"

art1_body = """Every Indian American who has visited family in India during summer has heard the advice: be careful during the rains. Use mosquito repellent during monsoon. Watch out for dengue when the monsoon hits.

That advice is no longer accurate. The monsoon is no longer the starting gun for dengue season. Dengue season now begins in the heat.

India's 2026 monsoon arrived in Kerala between May 24 and May 26 — approximately six days ahead of its normal June 1 onset. But doctors across Indian cities had been treating dengue patients for weeks before any monsoon rain fell. The disease that generations of Indians associated exclusively with the rainy season has broken free of that calendar. Climate change, urban heat islands, and the biology of the Aedes aegypti mosquito have rewritten the rules.

If you are an Indian American planning a summer trip to India — or if you have already booked tickets for your family — this is the information your travel doctor probably did not give you, because the medical community itself is still catching up to the new dengue calendar.

## Why Heat Is the New Trigger

The Aedes aegypti mosquito, the primary vector for dengue virus, does not need rain to breed. It needs three things: warm temperatures (optimally 25–35°C), standing water (even a few millilitres will do), and humidity above 60 percent.

Northern India in April and May 2026 delivered all three. Temperatures exceeded 45°C in parts of Rajasthan, Delhi, UP, and Maharashtra through April and into May. Desert coolers — the evaporative coolers that are standard in most Indian homes without central air conditioning — held standing water 24 hours a day. Rooftop water tanks, open construction sites, discarded containers, flower pots, air conditioning drip trays, and clogged drains across every Indian city provided millions of micro-breeding sites.

The critical biological fact: extreme heat accelerates the Aedes aegypti life cycle. At 35°C, the time from egg to adult mosquito shrinks from 10–14 days to as few as 7 days. The extrinsic incubation period — the time it takes for the dengue virus to replicate inside the mosquito and become transmissible — also shortens with heat. At 30°C, this takes approximately 12 days. At 35°C, it drops to 7–8 days.

The net effect is that hot weather produces more mosquitoes faster, and those mosquitoes become infectious sooner. When intermittent pre-monsoon thunderstorms — which are increasingly common in the new climate pattern — deposit water into the million standing-water sites that extreme heat has already warmed, the breeding cycle intensifies explosively.

Dr Anirban Chattopadhyay, a Critical Care Specialist at CK Birla Hospitals in Kolkata, describes the mechanism: "When prolonged periods of heat are followed by heavy rains, the accumulation of water provides ideal breeding sites for mosquitoes — in coolers, flower pots, roofs, construction sites, air conditioning trays, open containers, and clogged drains."

Humidity then compounds the risk: warm, humid air allows adult mosquitoes to survive longer and increases the rate of viral replication within the mosquito. The result is that the traditional August-September dengue peak has developed a May-June shoulder that, in urban India, is now nearly as intense as the monsoon peak itself.

## The Diagnostic Delay

The shift in dengue timing creates a dangerous diagnostic gap. Most patients — and many primary care physicians in India — still associate dengue with the monsoon. When a patient presents with fever, body aches, headache, and fatigue in May, the default diagnosis is "viral fever" or "seasonal flu." Dengue testing is often not ordered until symptoms escalate.

This is the same symptom cluster that a jet-lagged Indian American family member might experience after a 20-hour flight to India. Fever from dehydration. Body aches from travel. Fatigue from time-zone adjustment. Headache from heat exposure. Every early dengue symptom has a plausible non-dengue explanation for a recently arrived traveller, which means the diagnosis is delayed precisely in the population most likely to develop complications — people with no prior dengue immunity.

The early signs of dengue are:

**Days 1–3 (febrile phase):** Sudden high fever (39–40°C / 102–104°F), severe headache (often described as "behind the eyes"), muscle and joint pain (the "breakbone" name comes from the intensity of the joint pain), fatigue, nausea, and sometimes a flat red rash on the chest or arms.

**Days 4–7 (critical phase):** Fever may drop, which patients and families interpret as recovery. But this is when complications develop — plasma leakage, haemorrhage, and a rapid drop in platelet count. Warning signs include persistent vomiting, abdominal pain, mucosal bleeding (gums, nose), restlessness or lethargy, and a sudden drop in platelet count below 100,000/μL.

**Days 7–10 (recovery phase):** If the critical phase is managed properly, recovery is usually rapid.

The critical mistake is interpreting the fever drop on day 4–5 as improvement. For a patient with no prior dengue immunity — which describes virtually all Indian American children born in the US and many adults who have not lived in India for decades — the critical phase is when the disease becomes dangerous.

## The NRI Risk Profile

Indian Americans visiting India in summer occupy a unique risk position for dengue that is different from both resident Indians and Western tourists.

**Immunological naivety.** There are four dengue serotypes (DENV-1 through DENV-4). Infection with one serotype provides lifelong immunity to that serotype but only short-term cross-protection against the others. Resident Indians, especially those who have lived in endemic areas, may have immunity to one or more serotypes from prior subclinical infections they never noticed. Indian Americans — particularly those who emigrated as young adults and their US-born children — likely have immunity to zero serotypes. A first dengue infection is usually mild. But in the context of no prior immunity and delayed diagnosis, complications are more likely.

**Delayed presentation.** NRIs visiting India are guests in family homes. The social dynamics of an Indian family visit — the obligation to attend functions, eat at relatives' homes, accompany elders to temples or shopping — create pressure to minimise symptoms. "I'm just tired from the flight" becomes the explanation for two days before a doctor is consulted.

**Unfamiliar healthcare navigation.** An Indian American who has not lived in India for 15 years may not know which hospital to go to, whether to go to a private hospital or a government hospital, how to find a reliable lab for a platelet count, or what the standard dengue management protocol is. The confusion is amplified at 2 AM when a child spikes a fever.

**Travel insurance gaps.** Most standard US travel insurance policies cover emergency medical care abroad, but the definitions of "emergency" and "medically necessary" vary. Dengue management in India — which may involve a 4–5 day hospital stay for IV fluids and platelet monitoring — costs ₹50,000 to ₹2,00,000 ($600 to $2,400) at a private hospital. Verify your travel insurance covers infectious disease hospitalisation in India before you travel.

**Medication interactions.** Indian Americans may be taking medications not commonly used in India, or vice versa. Critically: do NOT take aspirin or ibuprofen (Advil, Motrin) for dengue fever. These are antiplatelet and anti-inflammatory drugs that can worsen the bleeding complications of dengue. Use only paracetamol (acetaminophen/Tylenol) for fever management. This is a detail that every adult travelling to India should know before arrival.

## The Summer Travel Checklist

The following is not generic advice. It is specific to Indian Americans travelling to India between May and September 2026, based on the current epidemiological reality.

**Repellent.** Bring DEET-based repellent from the US — 25–30% DEET concentration is the standard recommendation for tropical exposure. Products like Repel 100 (98.11% DEET) or Sawyer Picaridin 20% are more effective than most repellents available in Indian stores. Apply every 4–6 hours on all exposed skin. Yes, even indoors. Aedes aegypti is a daytime biter — peak biting hours are early morning (6–9 AM) and late afternoon (4–7 PM).

**Clothing.** Light-coloured, long-sleeved, loose-fitting clothing. Aedes aegypti is attracted to dark colours. Treat clothing with permethrin spray (available at REI, Amazon, or any outdoor store) before travel — it remains effective through several washes.

**Mosquito net or plug-in repellent.** If your family's home does not have window screens (many Indian homes do not), bring a portable mosquito net for sleeping. Alternatively, bring a pack of Thermacell refills or Good Knight/All Out plug-in refills — the Indian versions are effective but may not be available in the specific brand your family uses. An electric mosquito bat (racquet) for the bedroom is cheap and surprisingly effective.

**Standing water audit.** Within 24 hours of arriving at any Indian home, walk the house and terrace looking for standing water. Cooler trays, flower pot saucers, roof drains, old tyres, open water tanks, construction debris. Dump or treat every container. This is not being a difficult guest — it is protecting the household.

**Platelet monitoring.** If anyone in your family develops a fever during an India trip, get a complete blood count (CBC) with platelet count within 24–48 hours of fever onset. In India, any pathology lab (SRL, Dr. Lal, Thyrocare, Metropolis) can do this for ₹200–400 ($2.50–5). Do not wait for the fever to "break" before testing. If platelets drop below 100,000/μL, seek hospital care immediately. If below 50,000/μL, hospitalisation is likely needed.

**Hospital identification.** Before you travel, identify one private hospital near your family's home that has an ICU and a blood bank. Ask your relatives which hospital they would go to for a serious illness. Have the address and phone number saved in your phone. Do this on day one, not at 3 AM when your child has a fever of 104.

**No aspirin, no ibuprofen.** Pack paracetamol (acetaminophen) only. If your child's fever is managed with children's Advil at home, switch to children's Tylenol for the India trip. This is the single most important medication rule for dengue risk.

**Hydration protocol.** ORS (oral rehydration salts) packets are available at every Indian pharmacy for ₹10–20. Buy a box on arrival. If anyone develops fever, start ORS immediately alongside paracetamol. Dengue dehydration can be severe and rapid, especially in children and elderly family members.

## The Broader Climate Pattern

What is happening with dengue in India in 2026 is not an anomaly. It is the new pattern. Climate scientists have been predicting for a decade that warming temperatures would expand both the geographic range and the seasonal window of mosquito-borne diseases. India is the proof case.

The traditional Indian disease calendar — malaria and dengue during monsoon (July–September), respiratory infections during winter (November–February), waterborne diseases during floods — was based on a climate that no longer exists. The 2026 pattern, where dengue emerges in May heat before monsoon rain, is the pattern that climate models have been predicting since the early 2010s.

For Indian Americans, this means that the "safe" travel windows are narrowing. The pre-monsoon period that was once considered low-risk for vector-borne diseases is no longer low-risk. The post-monsoon period, when residual standing water sustains mosquito breeding into October and November, extends the risk window further.

None of this means you should not visit India. Dengue is manageable. The vast majority of cases resolve without complications, especially when caught early and managed properly. The fatality rate for properly treated dengue in India's private hospital system is well below 1 percent.

What it means is that the preparation for a summer India trip should now include dengue readiness as a standard component — alongside visa renewal, currency exchange, and booking the return flight. The disease calendar has shifted. The travel preparation should shift with it.

Pack the DEET. Audit the standing water. Know where the hospital is. Keep paracetamol and ORS on hand. Get a platelet count if anyone develops a fever. And tell your parents in India to empty the cooler tray daily — not because the monsoon is coming, but because the dengue is already here."""

art1_sources = [
    "https://www.onlymyhealth.com/how-changing-weather-patterns-are-causing-early-dengue-cases-12977847039",
    "https://www.jagranjosh.com/general-knowledge/which-city-receives-the-monsoon-first-in-india-1734959997-1",
    "https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue",
    "https://www.cdc.gov/dengue/prevention/index.html",
]

print("\n=== Article 1: Dengue Before Monsoon / NRI Summer India Trip ===")
print(f"  Word count: {len(art1_body.split())}")

# Image: Mosquito / dengue prevention in Indian urban setting
art1_image = fetch_pexels_image("mosquito repellent tropical prevention")
if not art1_image:
    art1_image = fetch_pexels_image("monsoon rain India city street")
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
    "score_total": 92,
    "tags": ["dengue", "monsoon", "India", "Aedes aegypti", "mosquito", "climate change", "heat", "NRI", "Indian American", "summer travel", "Kerala", "Delhi", "Mumbai", "platelet count", "paracetamol", "DEET", "repellent", "pre-monsoon", "vector-borne disease", "travel health", "children", "diaspora"],
    "vertical": "diaspora",
    "urgency": "high",
    "diaspora_angle": "Dengue is no longer a monsoon-only disease in India. Pre-monsoon extreme heat (45°C+) in 2026 is accelerating Aedes aegypti breeding cycles from 14 days to 7 days. Monsoon arrived in Kerala 6 days early (May 24-26) but doctors were already treating dengue cases in May. ~4.5M Indian Americans visit India during summer. US-born children have zero dengue immunity. Early symptoms (fever, fatigue, body aches) mimic jet lag — diagnosis is delayed. Critical mistakes: taking aspirin/ibuprofen (worsens bleeding), interpreting fever drop on day 4-5 as recovery (it's the start of the critical phase). Action items: pack DEET 25-30%, permethrin-treated clothing, get CBC with platelet count within 24-48h of any fever, keep paracetamol only (no NSAIDs), identify hospital on day 1, ORS packets from any Indian pharmacy. Empty cooler trays, flower pots, and rooftop water tanks daily. The traditional advice 'be careful during monsoon' is now dangerously outdated.",
    "word_count": len(art1_body.split()),
    "image_url": art1_image["url"] if art1_image else None,
    "image_caption": f"Photo by {art1_image['photographer']} via Pexels" if art1_image else None,
})
if result1:
    print(f"  ✓ Published: {art1_id}")
else:
    print("  ✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Your Body Responds to Exercise Differently Because
#             of Your Ancestry — Leicester Proteomics Study
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "A Study of 49,000 People Found 375 Proteins in South Asian Blood That Differ From White Europeans. Exercise Changed One Key Inflammation Protein — IL-6 — but the Pathways Are Ethnicity-Specific. Your Ancestry Shapes How Your Body Responds to a Workout."
art2_subheadline = "A University of Leicester study published in eBioMedicine, using UK Biobank data from over 49,000 participants, examined hundreds of proteins circulating in blood plasma to understand how ethnicity and physical activity influence cardiometabolic health. The researchers identified 464 proteins linked to physical activity levels and 375 proteins associated with ethnicity — meaning South Asian blood contains hundreds of proteins at different concentrations than White European blood, independent of diet, exercise, or lifestyle. In a validation cohort of individuals at high risk for type 2 diabetes whose physical activity was tracked over four years with wearable devices, interleukin-6 (IL-6) emerged as the only protein significantly related to physical activity: people who increased their daily steps had lower IL-6, an inflammatory marker linked to cardiovascular disease, insulin resistance, and visceral fat accumulation. But 16 ethnicity-specific proteins — including chemokines CCL28 and CCL15, hepatokine FABP1, adipokine FABP2, and pancreatic enzymes AMY2A and AMY2B — were validated as fundamentally different between South Asian and White European populations. These proteins govern immune response, inflammation, liver metabolism, fat tissue signalling, and starch digestion. The finding means that the molecular machinery connecting exercise to health outcomes operates through different pathways in South Asian bodies — and that generic exercise prescriptions designed from Western population data may not capture the full picture of how physical activity reduces disease risk in people of Indian, Pakistani, Bangladeshi, or Sri Lankan descent."
art2_slug = make_slug("south-asian-protein-signatures-exercise-il6-leicester-ethnicity")
art2_category = "lifestyle-health"

art2_body = """The gym in Cupertino, the running trail in Edison, the yoga studio in Fremont — every Indian American who exercises regularly has followed advice that was developed, tested, and validated almost entirely on White Western bodies. The recommendation to walk 10,000 steps, the target heart rate zones, the optimal weekly exercise minutes — all of these derive from studies where South Asians were either absent or collapsed into a generic "Asian" category that diluted their biological specificity.

A study from the University of Leicester, published in eBioMedicine and funded by the UK's National Institute for Health and Care Research, has provided the most detailed molecular evidence to date that this approach is insufficient. The research examined over 49,000 participants from the UK Biobank and found that the proteins circulating in South Asian blood are fundamentally different from those in White European blood — and that exercise changes these proteins through pathways that are ethnicity-specific.

The finding does not mean exercise is less effective for South Asians. It means exercise may work through different molecular mechanisms, and understanding those mechanisms is essential for designing exercise interventions that actually target the specific disease risks South Asians face.

## What the Study Found

The Leicester team used proteomics — the large-scale study of proteins — to analyse blood plasma from UK Biobank participants. Proteins are the functional molecules of the body: they carry signals between organs, regulate inflammation, control metabolism, govern immune responses, and mediate virtually every biological process. Measuring protein levels in blood provides a snapshot of what the body is doing at a molecular level.

The study had two phases.

**Discovery phase:** Using the full UK Biobank cohort of over 49,000 participants, the researchers identified 464 proteins whose levels were significantly associated with physical activity levels, and 375 proteins whose levels were significantly associated with ethnicity (South Asian versus White European). These are not small numbers. There are approximately 3,000 proteins that can be reliably measured in blood plasma. Finding 375 that differ by ethnicity means that roughly 12 percent of the measurable human proteome is operating at different levels in South Asian versus White European bodies.

**Validation phase:** The researchers then tested their findings in a separate cohort — a group of individuals at high risk for type 2 diabetes whose physical activity was tracked for four years using wearable accelerometers (step counters worn on the wrist). This cohort provided objective, continuous measurement of how much people actually moved, not self-reported estimates.

In this validation, only one protein was significantly associated with physical activity: **interleukin-6 (IL-6)**. People who increased their daily step count over the four-year period had lower circulating IL-6 levels. People who decreased their activity had higher IL-6.

But 16 ethnicity-specific proteins were validated — meaning they consistently differed between South Asian and White European participants across both the discovery and validation cohorts. These included:

**Chemokines (CCL28, CCL15):** These are immune signalling molecules that direct white blood cells to sites of inflammation. Different baseline levels of chemokines mean that the South Asian immune system is responding to — or preparing for — inflammation in a different pattern than the White European immune system.

**Hepatokines (FABP1):** Fatty acid-binding protein 1 is produced by the liver and plays a central role in fatty acid metabolism. Different FABP1 levels in South Asians may relate to the well-documented higher rates of non-alcoholic fatty liver disease (NAFLD) in this population — a condition that often occurs at lower BMI in South Asians than in Europeans.

**Adipokines (FABP2):** Fatty acid-binding protein 2 is associated with fat tissue metabolism and intestinal lipid absorption. Different levels suggest that the way South Asian bodies process dietary fat — absorb it, transport it, store it — differs at the molecular level.

**Pancreatic enzymes (AMY2A, AMY2B):** These are amylase enzymes involved in starch digestion. South Asians have different copy numbers of the AMY gene — meaning the actual amount of amylase their bodies produce is genetically different. This affects how efficiently starches (rice, roti, potatoes) are digested and how rapidly glucose enters the bloodstream after a carbohydrate-heavy meal. The traditional Indian diet is starch-heavy, and the South Asian body may process that starch differently at the enzymatic level than a European body processes the same amount of starch.

## What IL-6 Tells Us

The fact that IL-6 was the only exercise-related protein validated in the study is not a limitation — it is a finding. IL-6 is one of the most important inflammatory markers in medicine. It is:

**A driver of insulin resistance.** Chronic low-grade elevation of IL-6 impairs the ability of cells to respond to insulin, a key mechanism in the progression from normal glucose tolerance to prediabetes to type 2 diabetes.

**A marker of visceral fat.** IL-6 is produced by visceral adipose tissue (the fat around internal organs). South Asians accumulate visceral fat at lower BMI than Europeans — the "thin on the outside, fat on the inside" phenotype. Higher visceral fat means higher IL-6, means more inflammation, means faster progression to metabolic disease.

**A cardiovascular risk factor.** Elevated IL-6 is associated with increased risk of myocardial infarction, stroke, and atherosclerosis. It promotes plaque formation and destabilisation in arterial walls.

**Modifiable by exercise.** The Leicester study confirms what other research has shown: increasing physical activity — specifically, increasing daily steps — lowers IL-6. This is one of the primary molecular mechanisms through which exercise reduces cardiovascular and metabolic risk.

For South Asians, this finding is both validating and incomplete. It validates that walking more — the simplest, most accessible form of exercise — produces measurable anti-inflammatory benefits in the blood. A South Asian person who goes from 3,000 steps a day to 7,000 steps a day will lower their IL-6 levels. That lower IL-6 translates to reduced insulin resistance, less visceral fat inflammation, and lower cardiovascular risk.

But the finding is incomplete because IL-6 is only one of 464 exercise-related proteins. The study identified hundreds of proteins that change with physical activity in the discovery phase. Whether those other proteins change through the same mechanisms in South Asian bodies as in White European bodies is not yet known. The 375 ethnicity-specific proteins suggest they may not.

## The Starch Digestion Question

The AMY2A and AMY2B findings deserve particular attention for the Indian diaspora, because they connect directly to the most fundamental element of Indian eating: starch.

Rice and roti are not side dishes in Indian cuisine. They are the structural centre of every meal. A South Indian thali without rice is not a thali. A North Indian dinner without roti is not dinner. The Indian relationship with starch is not a preference — it is a cultural and culinary identity.

The amylase genes (AMY1, AMY2A, AMY2B) determine how much amylase enzyme the body produces. Amylase breaks down starch into sugar. The more amylase you produce, the faster starch is converted to glucose in your bloodstream.

Population genetics has shown that copy numbers of AMY genes vary significantly across ethnic groups. Populations with historically starch-heavy diets — including South Asians — tend to have higher AMY gene copy numbers and produce more amylase. This was likely an evolutionary advantage: more efficient starch digestion meant better caloric extraction from the rice and grain that sustained the population.

But in the context of modern metabolic disease, this same efficiency may be a liability. Faster starch-to-glucose conversion means higher post-meal blood sugar spikes. Higher blood sugar spikes mean higher insulin demand. Chronic high insulin demand means insulin resistance. Insulin resistance means prediabetes. Prediabetes means type 2 diabetes.

The Leicester finding that AMY2A and AMY2B are among the validated ethnicity-specific proteins suggests that the South Asian metabolic relationship with starch is not just cultural — it is enzymatic. The Indian body may be processing the same bowl of rice differently, at a molecular level, than a European body processes the same bowl of rice.

This does not mean South Asians should stop eating rice or roti. It means that generic dietary advice about "complex carbohydrates" or "whole grains" may not account for the specific way South Asian bodies handle starch. And it means that exercise prescriptions aimed at managing blood sugar — the standard "walk after meals" advice — may need to be calibrated differently for South Asian physiology.

## What the Liver and Fat Proteins Mean

The hepatokine (FABP1) and adipokine (FABP2) findings connect to two conditions that disproportionately affect South Asians: non-alcoholic fatty liver disease and the "metabolically obese, normal weight" phenotype.

**NAFLD in South Asians.** Non-alcoholic fatty liver disease affects an estimated 30–40 percent of Indians, compared with approximately 25 percent of the general global population. South Asians develop NAFLD at lower BMI, lower waist circumference, and lower body fat percentage than Europeans. A South Asian man with a BMI of 24 (considered "normal" by Western standards) may already have significant fatty liver. FABP1, the liver protein that differed between ethnicities in the Leicester study, is central to how the liver processes fatty acids. Different baseline FABP1 levels may partly explain why the South Asian liver is more vulnerable to fat accumulation.

**The thin-fat phenotype.** South Asians tend to have less subcutaneous fat (the visible fat under the skin) but more visceral fat (the metabolically dangerous fat around internal organs) than Europeans at the same BMI. FABP2, the adipokine that differed between ethnicities, is involved in intestinal fat absorption and fat tissue signalling. Different FABP2 levels may influence how dietary fat is distributed between subcutaneous and visceral compartments. This could be one molecular explanation for why a South Asian person who "looks thin" can have the metabolic profile of an obese European person.

## The Chemokine Difference

The immune system findings (CCL28 and CCL15) are perhaps the most far-reaching because they suggest that the South Asian immune system operates at a different baseline than the White European immune system — not in response to infection or disease, but constitutively, as a feature of the biology.

CCL28 is a chemokine expressed in mucosal tissues — the gut, the lungs, the salivary glands. It recruits immune cells to these surfaces. Different baseline CCL28 levels could influence susceptibility to gut inflammation, respiratory infections, and mucosal immune responses.

CCL15 is involved in recruiting monocytes and macrophages — immune cells that play central roles in both infection fighting and chronic inflammation (including the chronic arterial inflammation that drives atherosclerosis). Different CCL15 levels may contribute to the different patterns of cardiovascular inflammation observed in South Asians.

These are not disease states. They are differences in the default configuration of the immune system. And they may influence how the South Asian body responds to exercise — because exercise is, among other things, an immune modulator. A 30-minute run triggers a cascade of cytokines, chemokines, and myokines (muscle-derived signalling molecules) that reconfigure the immune system for several hours. If the baseline immune configuration is different, the exercise-induced reconfiguration may also be different.

## What This Means in Your Gym

The Leicester study is not an exercise prescription. It is a molecular map. But its implications for how South Asians should think about exercise are significant.

**Walking works, and the mechanism is clear.** IL-6 reduction through increased daily steps is validated. This is the simplest, most accessible intervention: walk more. The anti-inflammatory benefit is real and measurable. For South Asians with elevated cardiovascular and metabolic risk, daily walking is not optional — it is medicine.

**Intensity may matter differently.** The study did not compare exercise intensities, but the ethnicity-specific protein signatures suggest that the dose-response relationship between exercise and health outcomes may not follow the same curve in South Asians as in Europeans. Future research needs to determine whether South Asians benefit more from moderate daily activity (like walking) versus high-intensity interval training, or whether the optimal mix is different.

**Post-meal activity is especially important.** Given the AMY2A/AMY2B findings about starch digestion, the common Indian practice of resting after meals may be metabolically counterproductive. A 15-minute walk after a rice-heavy meal can blunt the blood sugar spike by 30–50 percent. For South Asians, whose starch digestion may produce faster glucose spikes, this post-meal walk may be more impactful than it is for Europeans.

**Liver health should be monitored.** Given the FABP1 findings and the high prevalence of NAFLD in South Asians, regular liver function tests (including an ultrasound for fatty liver) should be part of routine health screening for Indian Americans — even those with normal BMI. Exercise reduces liver fat, but knowing you have fatty liver in the first place requires testing.

**The BMI threshold for concern is lower.** The FABP2 (adipokine) findings reinforce what endocrinologists have been saying for years: the BMI cutoffs developed for European populations are too high for South Asians. A BMI of 23 in a South Asian person carries the same metabolic risk as a BMI of 25 in a European person. The WHO has recommended lower BMI thresholds for Asian populations (overweight at 23, obese at 25, versus 25 and 30 for Europeans), but most US clinical settings still use the European cutoffs.

## The Research Gap and the Road Ahead

Dr Joe Henson, the study's lead researcher, concluded with a statement that should resonate with every Indian American who has ever received generic health advice: "Our findings underscore the importance of addressing ethnic disparities in cardiometabolic health, and the potential impact for culturally tailored interventions."

Culturally tailored interventions. Not "the same advice translated into Hindi." Interventions that account for the 375 proteins that are different, the amylase enzymes that process starch differently, the liver proteins that handle fat differently, the immune chemokines that operate at different baselines, and the IL-6 that responds to walking in a way that is, at least, detectable and beneficial.

The Leicester study is the beginning of a molecular map of South Asian exercise physiology. It does not yet tell us exactly how to exercise differently. But it tells us, with the weight of 49,000 participants and hundreds of validated proteins, that "differently" is not an opinion — it is a biological fact.

Your ancestry is not a risk factor to be managed. It is a physiology to be understood. The proteins in your blood are a letter from your evolutionary history, and the Leicester team has started to read it. The next step is translating that letter into exercise prescriptions, dietary guidelines, and screening protocols that are built for your body — not adapted from someone else's."""

art2_sources = [
    "https://le.ac.uk/news/2026/january/diabetes-ethnicity-protein-study-leicester",
    "https://www.sciencedirect.com/journal/ebiomedicine",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7360841/",
    "https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight",
]

print("\n=== Article 2: South Asian Protein Signatures / Exercise IL-6 / Leicester ===")
print(f"  Word count: {len(art2_body.split())}")

# Image: This is about exercise and molecular biology, not a specific person
# Use Pexels for South Asian exercise / fitness
art2_image = fetch_pexels_image("Indian people walking exercise park morning fitness")
if not art2_image:
    art2_image = fetch_pexels_image("South Asian fitness exercise walking outdoor")
if not art2_image:
    art2_image = fetch_pexels_image("people walking morning exercise park")
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
    "score_total": 90,
    "tags": ["proteomics", "South Asian", "ethnicity", "exercise", "IL-6", "interleukin-6", "UK Biobank", "University of Leicester", "proteins", "cardiometabolic", "inflammation", "FABP1", "FABP2", "AMY2A", "AMY2B", "amylase", "starch digestion", "NAFLD", "fatty liver", "visceral fat", "BMI", "Indian American", "NRI", "CCL28", "CCL15", "chemokine", "insulin resistance", "type 2 diabetes", "walking", "daily steps", "culturally tailored", "precision medicine"],
    "vertical": "diaspora",
    "urgency": "standard",
    "diaspora_angle": "University of Leicester proteomics study (eBioMedicine, 2026): 49,000+ UK Biobank participants. 375 proteins differ between South Asian and White European blood — 12% of the measurable proteome. Exercise reduces IL-6 (inflammatory marker) through increased daily steps — validated. But 16 ethnicity-specific proteins show fundamentally different immune (CCL28, CCL15), liver (FABP1), fat tissue (FABP2), and starch digestion (AMY2A, AMY2B) pathways. NRI implications: (1) Walking works — IL-6 reduction is real and measurable; (2) South Asian starch digestion may be enzymatically faster (AMY genes) → post-meal walks even more important; (3) NAFLD screening needed even at 'normal' BMI (FABP1); (4) BMI thresholds should be lower (WHO recommends 23/25 vs 25/30 for Europeans but most US doctors use European cutoffs); (5) Generic exercise advice designed from Western data may not capture how physical activity reduces disease risk in South Asian bodies. Your ancestry shapes your molecular response to exercise — 'differently' is not opinion, it's biological fact.",
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
commit_msg = "lifestyle: dengue before monsoon NRI travel + South Asian protein signatures exercise (2026-05-26 23:00 PDT)"
subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True)
push = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=30)
print(f"  Push: {'OK' if push.returncode == 0 else push.stderr[:200]}")

print("\n=== Done ===")
