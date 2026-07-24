#!/usr/bin/env python3
"""Travel writer — 3 articles for 2026-05-30 evening run."""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")


# ── Article 1: Noida International Airport ──────────────────────────

article1_body = """Delhi-NCR is about to get a second major airport — and for NRIs who have spent years enduring the controlled chaos of Indira Gandhi International, the timing could not be better.

Noida International Airport, built on the Jewar site along the Yamuna Expressway in Uttar Pradesh's Gautam Buddh Nagar district, will begin commercial operations on June 15, 2026. IndiGo will operate the inaugural flight. Akasa Air follows a day later with daily nonstops to Bengaluru and Navi Mumbai. Air India Express is also confirmed for early operations.

## What NRIs Actually Get

The immediate payoff is pressure relief on IGI. Delhi's main airport handled over 73 million passengers last year — well above its designed capacity — and the congestion shows in everything from immigration queues to taxi stand gridlock. For NRIs arriving on overnight long-haul flights and connecting domestically, IGI's bottlenecks can turn a 90-minute layover into a missed connection.

Noida's Phase 1 terminal can handle 12 million passengers annually, with a single runway rated for wide-body operations. The full four-phase buildout targets 70 million passengers per year, which would make it one of India's largest airports by capacity.

The location matters. Noida International sits roughly 72 kilometres from central Delhi via the Yamuna Expressway, making it more accessible for travellers headed to or from Noida, Greater Noida, Agra, or anywhere along the UP–Rajasthan corridor. For NRIs with family in western Uttar Pradesh — one of the most densely populated regions in the country — this airport eliminates the slog across Delhi entirely.

## The Bigger Picture

India is quietly building a multi-airport metro system that mirrors London, New York, and Tokyo. Navi Mumbai International Airport opened on December 25, 2025, with a Zaha Hadid-designed terminal now handling IndiGo, Akasa, and Air India Express flights. Mumbai went from one airport to two in a single quarter. Delhi now follows suit.

The contrast with the domestic flight cuts makes this interesting. Air India and IndiGo are trimming 250 daily domestic flights through August due to fuel costs from the Iran conflict. New airport capacity arriving precisely when existing capacity is being cut back means route allocation will shift. Airlines may reroute some operations to Noida or Navi Mumbai to capture demand that the legacy hubs can no longer absorb efficiently.

## International Flights: Not Yet, But Soon

Phase 1 is domestic only. But carriers from West Asia and Southeast Asia are already eyeing international slots, according to Hindustan Times. For NRIs, the dream scenario — landing at Noida on an Emirates or Singapore Airlines flight and skipping IGI altogether — is plausible within the next 12 to 18 months.

The ₹11,200-crore investment is structured as a public-private partnership. Ground transport connectivity is the remaining question mark. Metro links and expressway interchanges are under construction but not yet complete for opening day. Early users should budget extra time for ground transfers.

## The Bottom Line

If you fly into Delhi even twice a year, Noida International matters. The airport will not replace IGI — it will complement it. But for the millions of NRIs whose India trips start with a three-hour taxi ride from Terminal 3 to Noida or Agra, this is the single biggest quality-of-life improvement in years."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Noida International Airport Opens June 15 — Delhi-NCR Finally Gets a Second Gateway",
    "subheadline": "IndiGo flies first, Akasa Air follows the next day. For NRIs tired of IGI's perpetual congestion, the Jewar airport changes the maths on every trip home.",
    "slug": make_slug("noida-international-airport-opens-june-nri-delhi"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs flying into Delhi-NCR now have an alternative to IGI Airport's chronic overcrowding. Noida International is closer to western UP, where millions of diaspora families are based, and international flights are expected within 18 months.",
    "tags": ["travel", "airports", "delhi", "noida", "infrastructure", "aviation"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Bhaskar English", "url": "https://bhaskarenglish.in"},
        {"name": "Travel and Tour World", "url": "https://travelandtourworld.com"},
        {"name": "Reuters", "url": "https://reuters.com"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_at_the_inauguration_ceremony_of_the_Noida_International_Airport%2C_Jewar.jpg",
    "body": article1_body,
}


# ── Article 2: Ebola Travel Restrictions ─────────────────────────────

article2_body = """The Ebola outbreak centred in the Democratic Republic of Congo and Uganda has triggered a cascade of travel restrictions that NRIs need to understand — not because most are heading to Central Africa, but because the knock-on effects are already disrupting transit routes, summit schedules, and entry rules in countries Indian travellers use regularly.

## What Has Happened

The World Health Organisation declared the current Bundibugyo-strain Ebola outbreak a public health emergency of international concern on May 17. As of late May, the WHO has confirmed 101 cases from more than 900 suspected infections globally. There is no approved vaccine or treatment for this strain.

India quarantined a 28-year-old Ugandan woman in Bengaluru this week after she developed mild symptoms consistent with Ebola following travel from Uganda via Ahmedabad. Her test results came back negative, but the incident underscored how quickly the outbreak can reach Indian soil.

New Delhi has responded with airport screening and surveillance at all international entry points, advisories urging citizens to avoid non-essential travel to the DRC, Uganda, and South Sudan, and the postponement of the India-Africa Forum Summit that was scheduled for this week in the capital.

## The Restrictions That Matter for NRIs

**United States:** The CDC has prohibited non-citizens who visited the DRC, South Sudan, or Uganda within the past 21 days from entering the country. Green card holders who spent the last 21 days in affected nations are also barred. Returning US passport holders face mandatory screening, temperature checks, and travel history verification at airports.

**Canada:** A 90-day entry ban for residents of the DRC, Uganda, and South Sudan took effect this week. Canadian citizens and permanent residents returning from these regions face a mandatory 21-day quarantine — even without symptoms.

**Gulf transit hubs:** Bahrain suspended entry from all three affected countries for 30 days. Jordan suspended entry from the DRC and Uganda. These restrictions matter because Gulf airports are the most common transit points for NRIs flying between the US and India.

**Thailand:** Travellers from the DRC and Uganda can now only enter through Bangkok's Suvarnabhumi Airport, where they face screening and potential 21-day quarantine.

**Mexico:** Health Secretary David Kershenovich has mandated 21-day quarantine for travellers from affected nations and instituted Ebola screenings at airports.

## What NRIs Should Do

If you have any travel history involving the DRC, Uganda, or South Sudan — including layovers — within the past 21 days, expect disruption at US and Canadian ports of entry. This is not theoretical: the US ban on non-citizens is absolute, and Canada's quarantine applies even to symptom-free travellers.

For NRIs with business interests in East Africa — and the Indian diaspora in Africa is substantial, spanning Kenya, Tanzania, Nigeria, and South Africa — the prudent move is to check whether your transit routing touches any restricted country, even indirectly. Some airlines are adjusting flight paths to avoid affected regions.

The India-Africa Summit postponement is a diplomatic signal worth watching. India-Africa trade exceeded $100 billion last year, and any sustained disruption to travel and commerce corridors will be felt by the business community on both sides.

## The Outlook

The Bundibugyo strain has historically been less lethal than the Zaire strain, but the WHO's concern is the speed of spread. The International Civil Aviation Organization has urged governments to avoid blanket travel shutdowns in favour of targeted exit screening in affected nations. But the trend is clearly toward tighter restrictions, not looser ones.

For NRIs, the practical takeaway is straightforward: check the entry requirements for every country on your itinerary, including transit stops, before you fly. Rules are changing weekly."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Ebola Travel Restrictions Are Spreading Fast — What NRIs Need to Know",
    "subheadline": "The US has barred entry for travellers from three African nations. Canada mandates 21-day quarantine. Gulf transit hubs are tightening. Here is how the outbreak reshapes NRI travel plans.",
    "slug": make_slug("ebola-travel-restrictions-nri-us-canada-india"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs with business or family ties in East Africa face direct disruption. The US entry ban, Canada's 21-day quarantine, and Gulf transit restrictions affect the most common NRI travel corridors. Even indirect layovers in restricted countries can trigger entry denial.",
    "tags": ["travel", "ebola", "travel-advisory", "health", "us-immigration", "africa"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/countries-tighten-travel-rules-ebola-risk-rises-2026-05-28/"},
        {"name": "Reuters — Bengaluru quarantine", "url": "https://www.reuters.com/world/india/indias-bengaluru-quarantines-uganda-woman-suspected-ebola-infection-source-says-2026-05-27/"},
        {"name": "News Dive", "url": "https://newsdive.net"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/13471768/pexels-photo-13471768.jpeg",
    "body": article2_body,
}


# ── Article 3: Weakest Monsoon in 11 Years ──────────────────────────

article3_body = """India's weather department has forecast the weakest monsoon in 11 years, and NRIs planning summer trips home need to recalibrate their expectations about everything from heat to hotel pricing to the roads they will drive on.

## The Forecast

The India Meteorological Department projects that the southwest monsoon — which typically accounts for 70 percent of the country's annual rainfall — will deliver below-normal precipitation this year. The culprit is a developing El Niño pattern in the Pacific, which historically suppresses Indian monsoon activity. India has received below-average rainfall in most El Niño years, sometimes triggering droughts that damage crops and push food prices sharply higher.

The monsoon's advance has already slowed. Rains were expected to hit India's southern coast by May 26; the revised estimate pushes arrival to early June, later than the June 1 norm. The delayed onset means an extended pre-monsoon heatwave, with maximum and minimum temperatures through June likely to stay above average across southern, western, central, and northern states.

## What This Means If You Are Flying Home

**Hotter conditions, longer.** If your India trip falls in June or early July, prepare for temperatures that will exceed the seasonal average. States across the Hindi belt — Uttar Pradesh, Madhya Pradesh, Rajasthan, Maharashtra — will see more heatwave days than usual. The kind of 44°C afternoons that Delhi experienced in April could stretch well into June.

**Water and power disruptions.** A weak monsoon strains municipal water supplies, particularly in Tier 2 and Tier 3 cities where NRI families often live. Power outages also increase as air conditioning demand outpaces generation capacity. If you are visiting family in Hyderabad, Lucknow, or Ahmedabad during peak summer, expect intermittent disruptions.

**Flight delays.** Pre-monsoon thunderstorms and dust storms in northern India are a leading cause of flight delays at Delhi's IGI Airport and other northern hubs. A delayed monsoon extends this volatile weather window. NRIs with tight connecting flights should build in buffer time.

**Lower hotel rates in monsoon destinations.** The silver lining: destinations that depend on monsoon tourism — Udaipur, Goa, Munnar, Coorg — will likely offer discounted rates as visitor numbers soften with weaker rainfall. If you can tolerate humidity without the payoff of dramatic waterfalls and lush greenery, you will get better deals.

## The Destinations That Still Work

Not all of India suffers equally in a weak monsoon. The rain-shadow regions — Ladakh, Spiti Valley, and parts of Rajasthan — receive minimal monsoon rainfall regardless. Ladakh's peak season runs June through September precisely because it sits north of the monsoon belt. The Valley of Flowers in Uttarakhand opens June 1, with peak bloom from mid-July to mid-August even in low-rainfall years, thanks to glacial melt.

For NRIs who planned around the monsoon, the shift is straightforward: go north, go high, or go early. The window between late May and mid-June — before the monsoon and after the worst heatwaves — is narrow but ideal for Himalayan destinations.

## The Economic Ripple

NRIs with agricultural land or rural family connections should pay attention. A weak monsoon threatens early-season planting of pulses, cotton, oilseeds, and coarse grains. Rice paddy in non-irrigated areas across northern and northwestern states is also at risk. Lower rural incomes dampen the broader consumer economy — from motorcycle sales to refrigerator purchases — and can push food inflation higher.

India's government holds sufficient stockpiles of rice and wheat, so no immediate food crisis is expected. But the pricing of vegetables, pulses, and cooking oils at your local Indian grocery store in the US could drift upward later this year if the monsoon underperforms.

## The Practical Checklist

If you are visiting India between June and August this year, pack lighter cotton clothing than you think you need, carry electrolyte supplements, confirm your accommodation has reliable backup power, and check the monsoon status of your specific destination before booking domestic flights. The India Meteorological Department's website (mausam.imd.gov.in) publishes regional forecasts that are more useful than the national headline number."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "India Braces for Its Weakest Monsoon in 11 Years — and NRIs Heading Home Should Plan Accordingly",
    "subheadline": "El Niño threatens below-normal rainfall, extended heatwaves, and economic ripple effects. Here is what the forecast means for summer trips, family visits, and the price of dal at your local Indian grocery.",
    "slug": make_slug("india-weakest-monsoon-11-years-nri-summer-travel"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs visiting India this summer face hotter-than-normal conditions, potential water and power disruptions, and flight delays from extended pre-monsoon weather. A weak monsoon also threatens rural incomes and may push food prices higher — including at Indian grocery stores in the US.",
    "tags": ["travel", "monsoon", "weather", "india", "el-nino", "summer-travel"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-warns-weakest-monsoon-11-years-inflation-risks-rise-2026-05-29/"},
        {"name": "Wego Travel Blog", "url": "https://blog.wego.com/best-monsoon-destinations-india/"},
        {"name": "India Meteorological Department", "url": "https://mausam.imd.gov.in"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/13759774/pexels-photo-13759774.jpeg",
    "body": article3_body,
}

# ── Insert ───────────────────────────────────────────────────────────

articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
