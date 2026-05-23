#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-23 (01:30 AM batch)
Topics: India heatwave crisis + SoCal chemical tank evacuation near Disneyland
"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# ── Supabase config ──
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_patch(table, filters, data):
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{filters}", headers={**HEADERS, "Prefer": "return=minimal"}, json=data, timeout=30)
    return r.status_code

def sb_get(table, params):
    r = requests.get(f"{SB_URL}/rest/v1/{table}?{params}", headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(headline, date_suffix="20260523"):
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: India's Heatwave Crisis — 48°C, 325+ Heatstroke Cases
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "India Just Recorded 48°C. Hospitals in Delhi Are Overwhelmed, Gujarat Has Run Out of Water, and Your Parents Are Probably Not Telling You How Bad It Is.",
    "subheadline": "Andhra Pradesh has logged 325 suspected heatstroke cases since March. Banda in Uttar Pradesh hit 48°C this week — the highest temperature anywhere in India this year. The IMD says severe heatwave conditions will persist across Delhi, Haryana, UP, Rajasthan, and Bihar through May 27. Last year, 7,000 heatstroke cases were reported in this window. In 2024, it was 40,000.",
    "slug": make_slug("india-heatwave-48c-heatstroke-delhi-nri-parents"),
    "category": "news",
    "vertical": "india",
    "diaspora_angle": "For the millions of NRIs whose elderly parents are in Delhi, Lucknow, Jaipur, Ahmedabad, or Hyderabad right now, this is not a weather story — it is a welfare check. Every summer, the diaspora WhatsApp groups fill with the same anxious messages: 'Is the AC working? Are you drinking enough water? Don't go outside.' This year, the numbers suggest those messages are more urgent than ever.",
    "tags": ["heatwave", "India", "heatstroke", "Delhi", "Uttar Pradesh", "Andhra Pradesh", "Gujarat", "water shortage", "IMD", "Banda", "NRI", "climate"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters — India records over 300 suspected heatstroke cases as summer temperatures spike", "url": "https://www.reuters.com/world/india/india-records-over-300-suspected-heatstroke-cases-summer-temperatures-spike-2026-05-22/"},
        {"name": "Livemint — From Delhi to UP, heatwave intensifies across India; Banda records season's highest at 48°C", "url": "https://www.livemint.com/news/india/from-delhi-to-up-heatwave-intensifies-across-india-banda-records-season-s-highest-at-48-c-see-full-list-inside-11779421057897.html"},
        {"name": "Bharat Affairs — India Reports 300+ Suspected Heatstroke Cases Amid Severe Heatwave", "url": "https://bharataffairs.com/india-reports-300-suspected-heatstroke-cases-amid-severe-heatwave/"}
    ]),
    "score_total": 88,
    "status": "published",
    "published_at": now,
    "body": """The thermometer in Banda, a small district in Uttar Pradesh that most NRIs would struggle to place on a map, hit 48 degrees Celsius this week. That is 118 degrees Fahrenheit — the kind of temperature at which asphalt softens, metal surfaces become untouchable, and the human body begins to fail in ways that are difficult to reverse.

Banda's reading was the highest anywhere in India this year, but the broader picture is worse than any single number suggests. The India Meteorological Department has issued a severe heatwave warning stretching from May 22 to May 27 across a belt that covers virtually every major population centre in northern India: Delhi, Haryana, Chandigarh, Punjab, both halves of Uttar Pradesh, Rajasthan, Madhya Pradesh, Bihar, Jharkhand, Odisha, Vidarbha, and Telangana. This is not a localised event. It is a subcontinental crisis that is only intensifying.

## The Numbers So Far

Andhra Pradesh's health department has documented 325 suspected heatstroke cases between March 1 and May 19, with roughly a third of those reported in the first three weeks of May alone. The acceleration is alarming — heatstroke is a medical emergency that can trigger confusion, seizures, organ failure, and death within hours if untreated.

In Delhi, two heatstroke patients were admitted to a state-run hospital on Friday in critical condition. Across northern India, hospitals are reporting surges in patients presenting with dehydration, diarrhoea, and heat exhaustion — the precursors to heatstroke that overwhelm already strained public health infrastructure.

The IMD's own data provides the most sobering context. In the March-to-June period last year, India recorded approximately 7,000 suspected heatstroke cases and 14 confirmed deaths. In the same window in 2024, the numbers were staggering: 40,000 suspected cases and 110 deaths. We are not yet through May, and the trajectory suggests 2026 could rival or exceed 2024's toll.

## Temperatures Well Above Normal

The current heatwave is not merely hot — it is abnormally hot. Maximum temperatures across northwest, west, central, and parts of eastern India have ranged between 40°C and 47°C over the past week, with several districts in Uttar Pradesh recording temperatures "markedly above normal" — meaning 3°C to 5°C higher than what those regions typically experience in late May.

In the Prayagraj division, which includes Fatehpur, Kaushambi, and Pratapgarh, temperatures were "appreciably above normal" — deviations exceeding 5.1°C. Lucknow, Jhansi, Agra, Meerut, Varanasi, and Kanpur all reported temperatures well above seasonal averages. Bramhapuri and Chandrapur in Vidarbha hit 46.4°C on Wednesday afternoon.

The IMD has warned of continued heatwave to severe heatwave conditions across this entire belt through at least May 27. "Warm night" conditions — when nighttime temperatures remain so high that the body cannot adequately cool down during sleep — are expected in parts of UP, Bihar, Haryana, Delhi, and Vidarbha. Warm nights are particularly dangerous because they deny the body the recovery window that prevents cumulative heat stress from becoming lethal.

## The Water Crisis

In Gujarat, the heat has triggered acute water shortages. Visuals from news agencies showed long queues at municipal water distribution points, with residents in some districts waiting hours for a single tanker to arrive. The western state, which typically manages summer water stress through a network of reservoirs and canals, is running low earlier than expected this year.

The water crisis compounds the health crisis. Without adequate hydration, the body's ability to thermoregulate collapses — and in homes without reliable electricity or air conditioning, which describes the majority of Indian households outside metro centres, the margin between discomfort and medical emergency narrows to almost nothing.

State authorities across the affected belt have advised residents to avoid going outdoors between 11 a.m. and 4 p.m. It is sound advice. But for the tens of millions of Indians who work as manual labourers, street vendors, construction workers, and agricultural hands, staying indoors during peak heat is not a choice — it is a luxury they cannot afford.

## What NRIs Need to Know

For the Indian diaspora in the United States, Canada, and the United Kingdom, the heatwave arrives as a familiar annual anxiety. Every May and June, NRI WhatsApp groups become informal welfare networks: checking on elderly parents in Delhi's Dwarka or Lucknow's Gomti Nagar, reminding them to keep the inverter charged, urging them not to walk to the market in the afternoon.

This year, the anxiety is warranted by data. The heatwave is more intense, more widespread, and arriving earlier in its severity than in recent years. The IMD's forecasts suggest no relief until at least May 28, and the monsoon — which typically begins reaching northern India in late June — is still more than a month away.

For NRIs with aging parents in the affected zones, some practical steps: ensure the home has a functioning air cooler or air conditioner with backup power; arrange for ORS (oral rehydration solution) packets and electrolyte supplements to be available; confirm that the local water supply is consistent or arrange for supplementary tanker delivery; and remind family members — gently, persistently — that heatstroke symptoms like confusion, rapid heartbeat, and cessation of sweating require immediate hospital attention, not home remedies.

The diaspora cannot control the weather. But it can close the information and preparation gap that turns extreme heat from an ordeal into a tragedy. Forty thousand heatstroke cases in 2024 suggest that gap remains wide. The numbers this year will tell us whether it is narrowing — or whether India's summers have outpaced its ability to adapt."""
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Southern California Chemical Leak — 40,000 Evacuated
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "A 34,000-Gallon Chemical Tank Near Disneyland Could Explode at Any Moment. Forty Thousand People Have Been Told to Leave — Including Thousands in Orange County's Indian Heartland.",
    "subheadline": "A methyl methacrylate tank at GKN Aerospace in Garden Grove has been 'actively in crisis' for two days. The evacuation zone spans nine square miles across five Orange County cities — cutting through one of Southern California's densest Indian American corridors. Six thousand residents have refused to leave.",
    "slug": make_slug("garden-grove-chemical-tank-explosion-orange-county-indian"),
    "category": "news",
    "vertical": "nri-world",
    "diaspora_angle": "Orange County's Garden Grove-Anaheim-Santa Ana corridor sits at the edge of one of the largest Indian American population centres in Southern California. The evacuation zone borders communities in Anaheim and Westminster where thousands of Indian families live, work, and send their children to schools that were shut down on Friday. For NRIs across the country, the images of families fleeing with pets and bags are a reminder that the suburbs they chose for safety are never entirely immune to industrial hazards.",
    "tags": ["Garden Grove", "chemical leak", "Orange County", "methyl methacrylate", "GKN Aerospace", "evacuation", "Disneyland", "Southern California", "Indian American", "NRI"],
    "urgency": "breaking",
    "sources": json.dumps([
        {"name": "CNN — 40,000 residents under evacuation orders in Southern California as tank containing toxic chemical at risk of explosion", "url": "https://www.cnn.com/2026/05/22/us/chemical-spill-orange-county-california"},
        {"name": "Reuters — Thousands evacuated in Southern California due to failing chemical tank", "url": "https://www.reuters.com/world/us/thousands-evacuated-southern-california-chemical-tank-failing-2026-05-22/"},
        {"name": "Fox News — California officials warn massive chemical tank will likely spill thousands of gallons or 'blow up'", "url": "https://www.foxnews.com/us/california-officials-warn-massive-chemical-tank-will-likely-spill-thousands-gallons-blow-up"},
        {"name": "NPR — 40,000 people under evacuation orders after chemical tank leak in Southern California", "url": "https://www.npr.org/2026/05/23/nx-s1-5409268/chemical-spill-southern-california-orange-county-garden-grove"}
    ]),
    "score_total": 86,
    "status": "published",
    "published_at": now,
    "body": """At some point in the next few hours — or the next few days — a 34,000-gallon tank full of methyl methacrylate at a GKN Aerospace facility in Garden Grove, California, is going to fail. The question is not whether. The question is how.

"This thing is going to fail," Orange County Fire Authority Division Chief Craig Covey told reporters on Friday, with the kind of bluntness that emergency officials reserve for situations that have exhausted their technical options. "This is highly volatile, it's highly toxic, and it's highly flammable."

The two possible outcomes, according to the manufacturer's own assessment: the tank cracks and leaks approximately 7,000 gallons of the industrial chemical into a parking lot, or it explodes. There is no third option. The manufacturer's response team has tried everything available to them and told authorities they could not mitigate the crisis.

Forty thousand people across nine square miles and five Orange County cities have been ordered to evacuate. The facility sits five miles from Disneyland and four miles from Knott's Berry Farm — but the more immediately relevant geography is the residential fabric of Garden Grove, Anaheim, Westminster, Santa Ana, and Stanton that surrounds the industrial site on every side.

## What Happened

The crisis began on Thursday afternoon, when Orange County Fire Authority crews responded to a vapour release at 12122 Western Avenue — a GKN Aerospace facility that uses methyl methacrylate, or MMA, in plastics manufacturing. One of three chemical tanks at the site had overheated, activating a relief valve designed to safely vent vapours and an overhead sprinkler system to cool the tank.

Initial evacuation orders were issued Thursday evening but were lifted that night after vapour conditions improved. The reprieve was short-lived. When crews attempted to remove the chemical from the tank on Friday, they discovered a damaged valve that made extraction impossible. The evacuation orders were reinstated — this time covering a much larger zone.

By Friday evening, the tank's temperature had dropped to around 61 degrees — "with 50 being its happy place," Covey said — but officials stressed that the improvement was fragile and that containment efforts would continue overnight. The other two tanks at the facility had been either neutralised or were not at risk.

## The Chemical

Methyl methacrylate is a flammable, volatile liquid used in the production of acrylic plastics. According to the Environmental Protection Agency, exposure can cause significant irritation to the lungs and nasal passages, dizziness, and nausea. It is heavier than air, meaning that in the event of a release, the vapour would settle at ground level — precisely where people live, sleep, and breathe.

Orange County Health Officer Dr. Regina Chinsio-Kwong acknowledged that there are not many documented cases of large-scale human exposure to MMA, making the potential effects of an explosion unpredictable. "We're going into unique times and we have limited information," she said — a statement that underscores both the rarity of the situation and the limits of the official response.

The chemical can produce a fruit-like scent, although smelling it does not necessarily indicate dangerous exposure levels. Air quality monitors had not detected any vapour outside the evacuation zone as of Friday evening, but officials urged residents to remain vigilant. MMA is not currently detectable in the ambient air, meaning the danger is latent — waiting behind a failing steel wall.

## The Human Cost

Thirteen schools and two district facilities within the Garden Grove Unified School District were evacuated on Friday morning. Evacuation shelters were established in neighbouring cities. Reverse 911 calls went out. Police posted on social media.

And yet, approximately 6,000 residents — roughly 15% of the affected population — refused to leave.

"I was sleeping in my house until this morning when they told us we had to leave," resident Diane Chavira told a local CBS affiliate, describing the scramble to collect her four dogs and get out of the area. "It's been chaos," said Jacqueline Riegos, who evacuated from Stanton. "Nobody can really give us any details about what's going on. And we don't know how long this is going to be."

The uncertainty is perhaps the most corrosive element. Unlike a wildfire with a visible perimeter or an earthquake with a measurable aftershock window, a chemical tank failure offers no timeline and no visual cue. Residents cannot see the danger. They can only be told to trust that it exists — and some, understandably, find that trust difficult to extend when the evacuation has already been issued, lifted, and reinstated once.

## The Orange County Corridor

Garden Grove and its surrounding cities sit within one of the most ethnically diverse suburban corridors in the United States. The area's Vietnamese American community in Westminster's "Little Saigon" is the most visible, but the broader OC suburban belt — stretching from Anaheim through Irvine, Tustin, and south toward Mission Viejo — is also home to one of the largest and fastest-growing Indian American populations in Southern California.

The evacuation zone itself borders communities where thousands of South Asian families have settled over the past two decades, drawn by good schools, relative affordability compared to West LA, and proximity to the tech and aerospace employers that dot Orange County's industrial parks. Some of those employers, it turns out, sit uncomfortably close to the homes they helped attract.

For the broader Indian American community watching from the Bay Area, the New York metro, or the Dallas suburbs, the Garden Grove crisis is a reminder of an uncomfortable truth: the same suburban industrial parks that provide aerospace and tech jobs also house chemicals that, on a bad Thursday afternoon, can turn a quiet neighbourhood into an evacuation zone. Orange County's Indian families are not uniquely affected — but they are part of the community fabric that has been disrupted, displaced, and left waiting for a steel tank to decide their next 48 hours.

## What Comes Next

Authorities said the tank's declining temperature was encouraging but not conclusive. Covey indicated that the cooler conditions might allow crews to attempt close-proximity mitigation strategies that were previously too dangerous — but he did not specify what those strategies might be.

The wind direction remains a wild card. "People need to get out of their houses and get into a safe space because when this thing goes, depending on the wind direction it's going, we cannot control the weather," Covey said. The statement is a rare admission of what emergency management professionals know but rarely say publicly: that in a chemical emergency, the outcome depends as much on meteorology as on engineering.

For now, 34,000 residents have complied. Six thousand have not. And a tank of methyl methacrylate sits in a parking lot in Garden Grove, deciding — by the laws of thermodynamics and the integrity of a damaged valve — whether this weekend stays a disruption or becomes a disaster."""
})

# ── Insert articles ──
print(f"\n{'='*60}")
print(f"Publishing {len(articles)} articles...")
for a in articles:
    try:
        res = sb_post("p2_articles", a)
        print(f"  ✓ [{a['category']}] {a['headline'][:80]}...")
        print(f"    ID: {a['id']}, Slug: {a['slug']}")
    except Exception as e:
        print(f"  ✗ FAILED: {a['headline'][:60]}... — {e}")

# ── Mark corresponding pending topics as written ──
print(f"\n{'='*60}")
print("Marking related pending topics as written...")
topic_titles_to_mark = [
    "Southern California Chemical Leak Forces Evacuation of 40,000 Residents",
]
for title in topic_titles_to_mark:
    try:
        topics = sb_get("p2_topics", f"canonical_title=eq.{requests.utils.quote(title)}&status=eq.pending&select=id")
        for t in topics:
            sb_patch("p2_topics", f"id=eq.{t['id']}", {"status": "written"})
            print(f"  ✓ Marked topic {t['id'][:8]} as written: {title[:60]}")
    except Exception as e:
        print(f"  ✗ Topic mark error: {e}")

# ══════════════════════════════════════════════════════════════
# SCORE DECAY — age out older articles
# ══════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print("Running score decay...")
try:
    resp = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?status=eq.published&score_total=gt.30&select=id,score_total,published_at",
        headers=HEADERS, timeout=30
    )
    all_arts = resp.json()
    from datetime import timedelta
    now_dt = datetime.now(timezone.utc)
    decayed = 0
    for art in all_arts:
        pub = datetime.fromisoformat(art["published_at"].replace("Z", "+00:00"))
        age_hours = (now_dt - pub).total_seconds() / 3600
        if age_hours > 48:
            new_score = max(30, int(art["score_total"] * 0.97))
            if new_score < art["score_total"]:
                sb_patch("p2_articles", f"id=eq.{art['id']}", {"score_total": new_score})
                decayed += 1
    print(f"  Decayed {decayed} articles (of {len(all_arts)} eligible)")
except Exception as e:
    print(f"  Score decay error: {e}")

print(f"\n{'='*60}")
print("Writer batch complete!")
