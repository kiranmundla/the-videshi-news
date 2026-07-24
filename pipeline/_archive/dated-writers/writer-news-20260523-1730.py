#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-23 17:30 batch
Topics: 1) India heatwave crisis — 55+ dead in one day across Telugu states, 300+ heatstroke cases, 48°C temps
        2) India's job engine stalling — Iran war driving Gulf workers home AND crushing manufactured exports
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

def sb_get(table, params):
    r = requests.get(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(headline, date_suffix="20260523"):
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

# ── Duplicate check ──
existing = sb_get("p2_articles", {
    "select": "headline,slug",
    "status": "eq.published",
    "published_at": "gte.2026-05-22T00:00:00Z",
    "order": "published_at.desc",
    "limit": "60"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: India's Heatwave Is Killing People — 55 Dead in One Day, 48°C Temperatures, and the Worst May Still Come
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("india-heatwave-55-dead-one-day-telangana-andhra-48c")
if slug1 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "India's Heatwave Killed 55 People in a Single Day Across Andhra Pradesh and Telangana. Temperatures Have Hit 48°C. The Worst Week of the Summer Starts on Sunday.",
        "subheadline": "On Friday, May 22, at least 55 people died of heatstroke across the two Telugu states — 21 in Andhra Pradesh, including 10 in Vijayawada alone (eight of them unidentified beggars who collapsed in public spaces), and 31 to 34 in Telangana. An eight-year-old girl in Sangareddy district died after playing outside. Andhra Pradesh has recorded 325 suspected heatstroke cases since March. Banda in Uttar Pradesh touched 48°C — 118 degrees Fahrenheit — the highest temperature recorded anywhere in India this year. Delhi is under a 'severe heatwave' warning through May 27. And on Sunday, the Rohini Kartham begins — the traditional period of the most extreme heat — with forecasters warning temperatures could climb higher still. For NRIs with elderly parents, young children, and working-class family members back home, the numbers are no longer abstract.",
        "slug": slug1,
        "category": "news",
        "vertical": "india",
        "diaspora_angle": "Every NRI with family in India has had the same conversation this week — a phone call or WhatsApp message asking 'How hot is it there?' The answers are terrifying. Parents in Hyderabad saying they haven't left the house in three days. Siblings in Delhi describing power cuts during peak afternoon heat. Relatives in rural AP and Telangana who work outdoors — in fields, on construction sites, in markets — and cannot simply stay inside. The heatwave is a class crisis: it kills the people who cannot afford air conditioning, who must work in the sun to eat, who sleep on rooftops because their one-room homes are unbearable. Many NRIs left precisely these circumstances. The images of unidentified beggars dying on Vijayawada streets, of an eight-year-old girl collapsing in Sangareddy, of hospitals filling with dehydration patients — these are not distant news stories. They are the India that NRIs carry with them, and the India they send money home to protect their families from. With the Rohini Kartham starting Sunday and no rain in sight for at least another week, the calls home are going to get harder.",
        "tags": ["heatwave", "India", "Andhra Pradesh", "Telangana", "heatstroke", "Delhi", "Vijayawada", "Hyderabad", "NRI", "climate", "deaths", "Rohini Kartham", "temperature", "48 degrees", "water shortage"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — India records over 300 suspected heatstroke cases as summer temperatures spike", "url": "https://www.reuters.com/world/india/india-records-over-300-suspected-heatstroke-cases-summer-temperatures-spike-2026-05-22/"},
            {"name": "Archynetys — At least 55 dead from heatstroke across AP and Telangana on May 22", "url": "https://www.archynetys.com/heatwave-deaths-telangana-ap"},
            {"name": "PingTV — Telangana Heatwave 2026: A Public Health Crisis (66+ deaths)", "url": "https://pingtvindia.com/telangana-heatwave-2026-public-health-crisis"},
            {"name": "AIR News — 16 dead from heatstroke in Telangana; state announces ₹4 lakh ex-gratia", "url": "https://airnews.in/16-dead-heatstroke-telangana-ex-gratia"},
            {"name": "Bharat Affairs — India reports 300+ suspected heatstroke cases amid severe heatwave", "url": "https://bharataffairs.com/india-heatwave-300-heatstroke-cases"}
        ]),
        "score_total": 89,
        "status": "published",
        "published_at": now,
        "body": """On Friday, May 22, at least 55 people died from heatstroke across Andhra Pradesh and Telangana. The number is not final — some agencies report higher counts, and the gap between "suspected" and "confirmed" heatstroke deaths in India is always wider than it should be. What is not in dispute is the scale: dozens of people, in two states, in a single day, killed by heat.

In Vijayawada, the capital region of Andhra Pradesh, ten people died on Friday alone. Eight of them were unidentified — beggars who collapsed in public spaces and were found unconscious on streets near the railway gate in Ajit Singh Nagar, around Raghavayya Park, near the district jail in Hanumanpet, and beside the LIC office on Besant Road. They had no air conditioning to retreat to, no family nearby to notice the symptoms, and no medical attention until it was too late.

Three more deaths were reported in Eluru, three in Kakinada, two in Palnadu, and one each in Anakapalli and West Godavari. Andhra Pradesh's total for the day: 21 dead.

## Telangana: 31 Dead, 46°C Across 20 Districts

Across the border in Telangana, the toll was even higher. Reports range from 31 to 34 heatstroke deaths on the same day, with temperatures crossing 46°C in 20 different districts. The highest recorded temperature in the state hit 46.5°C in Sirpur, in the Asifabad district — a number that was once considered extraordinary and is now becoming routine.

The victims are not all anonymous. In Sangareddy district, an eight-year-old girl named Keerthana died from severe heatstroke after playing outside in the sun. In Nizamabad, Rajeshwar, 52, died in the Navypet mandal. In Jagtial, Srinivas, 40, a mason, collapsed while working. In Adilabad, three more people died — ages 27, 44, and 54.

These are the people the heatwave kills first: outdoor workers, the elderly, children, the homeless. People whose exposure to the sun is not a lifestyle choice but an economic necessity. A mason cannot work from home. A street vendor cannot close shop when the temperature crosses 45°C. A beggar cannot relocate to an air-conditioned mall.

Telangana's government has responded with a ₹4 lakh ex-gratia payment for each family of the deceased and has issued a red alert for 18 districts. Authorities have established hydration points and placed medical teams on alert. These are necessary measures. They are also reactive measures, deployed after the dying has already begun.

## 325 Suspected Cases, 48°C in Banda, Delhi on Alert

The Telugu states are the epicentre, but the heatwave covers more than a dozen Indian states.

Andhra Pradesh's health department reported 325 suspected heatstroke cases between March 1 and May 19 — roughly a third of them since the beginning of May, indicating a sharp acceleration as summer deepens. The actual number is almost certainly higher; many cases in rural areas go unreported because patients either do not reach hospitals or are treated at home and die without formal medical documentation.

The highest temperature recorded anywhere in India this year — 48°C, or 118 degrees Fahrenheit — was registered this week at Banda in Uttar Pradesh. To put that in perspective: 48°C is the temperature at which the human body's cooling systems begin to fail. Sweat evaporates before it can cool the skin. Core body temperature rises. Without intervention, organ failure follows within hours.

Delhi and large parts of northern India are under a "severe heatwave" warning from the India Meteorological Department through May 27. Two heatstroke patients were admitted to a state-run hospital in Delhi this week and were critical. In Gujarat, hospitals have been filling with patients suffering from diarrhoea and dehydration — the secondary effects of extreme heat on bodies that are already nutritionally stressed and inadequately hydrated.

## The Rohini Kartham: The Worst Is Not Over

The most unsettling detail in the current forecasts is what comes next.

On Sunday, May 25, the Rohini Kartham begins — a period in the Hindu calendar traditionally associated with the most intense heat of the Indian summer. Meteorologists do not rely on traditional calendars for forecasting, but this year the science and the tradition agree: the next seven to ten days will be worse than the last seven to ten days.

Forecasters warn that temperatures could climb to 48°C in parts of Telangana and Rajasthan. The India Meteorological Department has indicated that there will be no significant relief until the monsoon arrives — and the monsoon's arrival date, typically around June 1 for Kerala and early June for the southeastern coast, remains uncertain.

India recorded more than 7,000 suspected heatstroke cases and 14 deaths between March and June last year. In the same period in 2024, there were 40,000 suspected cases and 110 deaths. The 2026 trajectory, with 55 dead in a single day in just two states, suggests this year will exceed both.

## A Class Crisis, Not a Weather Event

India's heatwave coverage tends to follow a familiar arc: temperatures are reported, advisories are issued ("avoid going outdoors between 11 a.m. and 4 p.m."), a few deaths make the news, and the story fades until the monsoon arrives and replaces heat with floods.

What gets lost in this cycle is the structural reality: India's heatwaves kill poor people. They kill people who work outside because they have no other option. They kill people who live in one-room homes without fans, let alone air conditioning. They kill people who cannot afford clean drinking water, who eat once a day and whose bodies lack the reserves to fight dehydration. They kill people who sleep on rooftops and pavements because the indoors is worse than the outdoors at night.

The heatwave is not an act of nature that descends equally on all. It is a crisis that follows the fault lines of class, caste, and geography. The eight unidentified beggars who died on Vijayawada's streets were not victims of the weather. They were victims of a system that could not house them, feed them, hydrate them, or even identify them after they died.

India's total electricity-connected air conditioning penetration remains under 10 percent. In the states now recording the highest death tolls — Andhra Pradesh, Telangana, Odisha, Uttar Pradesh — the penetration is lower still. The gap between the India that experiences summer as an inconvenience and the India that experiences it as a survival threat is not a temperature gap. It is an infrastructure gap, an income gap, and a policy gap.

## What NRIs Are Watching

The heatwave has produced a specific kind of anxiety among NRIs — the anxiety of distance. The phone call to an elderly parent in Hyderabad who says "It's fine, beta, we stay inside" while the news shows that the power went out for four hours in their area. The WhatsApp message from a sibling in a tier-2 city showing the thermometer on their phone reading 47°C. The knowledge that the household help who cleans the family home walks to work in the midday sun because there is no alternative.

Many NRIs send money home specifically for summer survival — to pay electricity bills that spike with air conditioning use, to install inverters and coolers, to keep the water supply running. This year, with the rupee at 97 to the dollar, those remittances buy less than they did a year ago. And this year, the heat is worse.

The Rohini Kartham starts Sunday. The monsoon is at least ten days away. The forecasts show no relief. The families who need protection the most are the ones least able to protect themselves. And 55 people are already dead from a single day that, by all indications, was not the worst day of this summer.
"""
    })
else:
    print(f"  ⚠ Skipping heatwave article — slug already exists: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: India's Job Engine Is Stalling — Gulf Workers Coming Home, Factories at Half Capacity, and 400 Million Young People Waiting
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("india-jobs-crisis-gulf-workers-iran-war-exports-stalling")
if slug2 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "India's Job Engine Is Stalling on Two Fronts. The Iran War Is Sending Gulf Workers Home. And It's Crushing the Factories That Were Supposed to Employ Them When They Got There.",
        "subheadline": "The Iran war has dealt a double blow to Indian employment. Nine million Indians work in the Gulf, where economic growth has collapsed from 4.4 percent to 1.3 percent. Over 1.1 million have returned to India since February. At the same time, the war has driven up fuel, shipping, and logistics costs to the point where Indian factories — the ones that were supposed to absorb workers into manufacturing — are running at half capacity. In Kanpur, leather factories that once employed 500 people now employ 250. Recruiters who placed 5 to 10 candidates a month are placing one or two. Urban youth unemployment is at 14 percent. And 6 to 7 million young Indians enter the workforce every year. The economy is still growing at 7 percent. But the jobs are not growing with it.",
        "slug": slug2,
        "category": "news",
        "vertical": "economy",
        "diaspora_angle": "This story is about NRIs — literally. The 9 million Indians in the Gulf are the largest single block of the Indian diaspora. They are the construction workers in Dubai, the nurses in Saudi Arabia, the shopkeepers in Oman, the engineers in Qatar. Their remittances — $102.5 billion in the first nine months of FY25 — are the single largest source of foreign exchange for India, and they fund entire regional economies: Kerala, parts of UP, coastal Karnataka, Hyderabad. When a recruiter in Kanpur says he went from placing 10 candidates a month to placing one, he is describing the collapse of a migration pipeline that has shaped Indian families for three generations. When a jewellery worker in Saudi Arabia returns to earn a third of his previous salary at a tea stall, he is living the story that millions of Gulf NRIs fear. And the second front — factories running at half capacity — means there is nothing waiting for them at home either. For NRIs in the US, UK, and Canada, this is not distant economics. It is the phone call from a cousin who lost his Gulf job and is asking for money. It is the brother-in-law whose factory in Kanpur is on short weeks. It is the remittance that now buys less because the rupee is at 97. The Iran war is not just a geopolitical event — it is reshaping the economic lives of Indian families on both sides of the border.",
        "tags": ["jobs", "unemployment", "India", "Gulf", "Iran war", "remittances", "NRI", "manufacturing", "Kanpur", "leather", "exports", "Kerala", "youth", "economy", "Strait of Hormuz"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — India's job engine strains as Iran war hits remittances and trade", "url": "https://www.reuters.com/world/india/indias-job-engine-strains-iran-war-hits-remittances-trade-2026-05-22/"},
            {"name": "Reuters — Rubio touts US energy on India trip meant to repair ties", "url": "https://www.reuters.com/world/rubio-touts-us-energy-india-trip-meant-repair-ties-2026-05-23/"},
            {"name": "World Bank — Gulf region growth forecast to slow to 1.3% in 2026 from 4.4% in 2025", "url": "https://www.worldbank.org/en/region/mena/overview"},
            {"name": "Association of Indian Entrepreneurs — K.E. Raghunathan on structural slowdown", "url": "https://www.reuters.com/world/india/indias-job-engine-strains-iran-war-hits-remittances-trade-2026-05-22/"},
            {"name": "NORKA Roots / Kerala — Ajith Kolassery on potential mass Gulf repatriation", "url": "https://www.reuters.com/world/india/indias-job-engine-strains-iran-war-hits-remittances-trade-2026-05-22/"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "body": """Mohammad Qureshi used to earn 30,000 rupees a month — about $311 — working at a jewellery shop in Saudi Arabia. It was enough to build a small home in Kanpur and help pay for his sister's wedding. Life, as he describes it, was "easy and the money was good."

Now the 32-year-old stands beside his cousins' tea stall in Kanpur, earning barely a third of what he made in the Gulf. The Iran war disrupted his plans to return to Saudi Arabia. His visa situation is uncertain. He lives with his mother and elder sister. He prays the war ends soon.

Qureshi's story, reported by Reuters this week, is not exceptional. It is the story of millions of Indian workers whose economic lives are tethered to the Gulf — and who are now watching that lifeline fray on two fronts simultaneously.

## The Double Blow

The conventional understanding of the Iran war's economic impact on India focuses on oil prices and the rupee. Those are real. But Reuters' detailed reporting from industrial hubs like Kanpur reveals a deeper structural problem: the war is not just making India's imports more expensive. It is simultaneously destroying India's two main employment pipelines — Gulf migration and manufactured exports.

**Front one: Gulf jobs disappearing.** Out of nearly 19 million Indians working overseas, approximately 9 million are in the Gulf. The World Bank estimates that economic growth in the Gulf region will slow to 1.3 percent in 2026, down from 4.4 percent in 2025. Construction projects are being delayed. Recruitment is being frozen. Families who once paid migration agents to send their sons to Dubai or Riyadh are now hesitant to invest when the destination economy is contracting and a war is raging next door.

India's foreign ministry confirmed that about 1.1 million Indians — including passengers, workers, and other travellers — returned from the Gulf region between the start of hostilities on February 28 and the end of April. Not all of them are permanent returns. But many are workers whose projects have been halted, whose employers have laid them off, and whose visas are expiring without renewal.

**Front two: factories shrinking.** At Kings International, a leather factory in Kanpur that supplies saddlery overseas and sports goods to Decathlon, owner Taj Alam described the squeeze: the Iran war has driven up fuel, natural gas, logistics, and shipping costs, compressing margins just as international demand weakens. His factory, which can process 200 hides a day and once employed over 500 workers, is now running at half capacity with half its workforce.

"The outlook will remain bleak until the Strait of Hormuz stabilises," Alam told Reuters. "Why invest when the future looks uncertain?"

This is the double blow. The workers who are returning from the Gulf need jobs. The factories that might have absorbed them are running at half speed. The economy is growing at 7 percent — a number that looks healthy in aggregate but masks the reality that the growth is not translating into the kind of employment that 400 million Indians under 30 need.

## The Kanpur Microcosm

Kanpur is not a random example. The city accounts for roughly a quarter of India's $6 billion annual leather exports and directly or indirectly employs about 500,000 people, according to Mukhtarul Amin, vice chairman of the Council for Leather Exports. Leather is precisely the kind of labour-intensive, export-oriented manufacturing that India's economic planners have spent decades trying to build — the kind that absorbs semi-skilled workers, pays better than agriculture, and creates a path to the lower middle class.

That sector is now caught between rising input costs and falling demand. Businesses are retaining workers to avoid the cost of rehiring when conditions improve, but they are not expanding. New investment is frozen. The hiring pipeline is dry.

At Hayat Placement Services, also in Kanpur, recruiter Gautam Bhatnagar described the collapse: "Earlier, we used to place five to 10 candidates every month. Now we are lucky if we can place even one or two."

Bhatnagar's business sits at the intersection of both crises. He places workers in domestic factories and in Gulf positions. Both pipelines have dried up simultaneously.

## Kerala: Where Remittances Are the Economy

The anxiety is particularly acute in Kerala, where Gulf remittances have shaped the state's economy for three generations. Keralite nurses, engineers, and workers in Saudi Arabia, the UAE, and Oman send money that funds housing, education, healthcare, and consumption across the state.

Thomas Cherian, 50, spent 18 years working for a construction firm in Saudi Arabia before returning home on leave in December. He was due to go back in March, but his company halted its project and laid off about 600 Indian workers. If he cannot return by end-June, his visa will lapse.

"There has been no mass return so far," said Ajith Kolassery, CEO of NORKA Roots, an agency under Kerala's Non-Resident Keralites Affairs Department. "But if the conflict continues, financial stress in Gulf economies could lead to large-scale repatriation, adding pressure to Kerala's already strained job market."

Remittances from overseas Indians stood at $102.5 billion in the April-December 2025 period, up from $92.4 billion a year earlier. Data for January through March — the period after the war began — has not yet been released. The Reserve Bank of India did not respond to queries on the war's impact on remittance flows.

The concern is not just about the total number. It is about what happens when remittance-dependent households suddenly lose their income stream. In Kerala, Gulf remittances fund a significant portion of the housing market, the education sector, and consumer spending. A sustained decline would ripple through the entire state economy.

## The Numbers Behind the Numbers

India's headline unemployment rate rose to 5.2 percent in April from 4.9 percent in February — a modest increase that obscures the deeper problem. Urban youth unemployment remains at nearly 14 percent. And the unemployment rate itself does not capture underemployment — the phenomenon of educated young people working in jobs that do not match their skills, at wages that do not match their aspirations.

"This is not just a cyclical slowdown," said K.E. Raghunathan, national chairman of the Association of Indian Entrepreneurs. "AI, weak global trade and tighter migration conditions are narrowing traditional employment avenues across manufacturing, IT and overseas labour."

Ram Singh, an economist at the Indian Institute of Foreign Trade, added: "The bigger worry is weaker wage growth, especially in low-skill and routine white-collar functions vulnerable to AI-automation. With a surplus labour market and firms seeking flexibility, this could mean more contractual, gig and informal work."

India has nearly 400 million people aged 15 to 29. Every year, 6 to 7 million young Indians enter the workforce. The economy needs to generate non-farm jobs for them at a pace that India has never sustained. The Iran war has made that challenge significantly harder by simultaneously closing the Gulf safety valve and squeezing the domestic manufacturing sector that was supposed to be the alternative.

## The Rubio Visit, in Context

Secretary of State Marco Rubio arrived in India on Saturday pitching American energy — a clear signal that Washington wants India to buy more LNG from the US and reduce its dependence on Gulf oil. The pitch makes strategic sense. But it does not address the employment crisis that the war has created.

Even if the Strait of Hormuz reopens tomorrow — and the negotiations suggest it might, eventually — the damage to India's employment pipelines will take years to repair. Gulf employers who laid off Indian workers will not rehire them instantly. Factory owners who cut their workforce will not scale back up until they see sustained demand recovery. Recruiters who watched their business collapse will not invest in rebuilding until the geopolitical picture stabilises.

And the 32-year-old tea stall worker in Kanpur will still be earning a third of what he made in Saudi Arabia, still living with his mother, still waiting for a break that may not come.

The economy is growing at 7 percent. The stock market is near all-time highs. The GDP numbers look fine. But for the millions of Indians whose livelihoods depend on the Gulf and on export-oriented manufacturing — the two pillars that a generation of Indian families have built their economic lives on — the ground underneath is shifting. And nobody in Delhi or Washington is talking about what to do about it.
"""
    })
else:
    print(f"  ⚠ Skipping jobs crisis article — slug already exists: {slug2}")


# ── Insert articles ──
if articles:
    print(f"\nInserting {len(articles)} articles...")
    for i, article in enumerate(articles, 1):
        try:
            result = sb_post("p2_articles", article)
            print(f"  ✓ Article {i}: {article['headline'][:80]}...")
            print(f"    Slug: {article['slug']}")
            if result:
                print(f"    ID: {result[0]['id'] if isinstance(result, list) else result.get('id', 'ok')}")
        except Exception as e:
            print(f"  ✗ Article {i} FAILED: {e}")
else:
    print("\nNo new articles to insert (all duplicates).")

print("\nDone.")
