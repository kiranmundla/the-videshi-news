#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-23 15:00 PDT run
2 articles:
  1. Memorial Day Weekend NRI Travel Guide: $4.56 gas, 45M travelers, severe weather
  2. India Raised Fuel Prices Three Times in Ten Days — NRI family impact
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

def make_slug(text, suffix="20260523"):
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
# ARTICLE 1: Memorial Day Weekend — The Most Expensive Start to Summer in Years
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "Forty-Five Million Americans Are Travelling This Weekend. Gas Is $4.56. Flights Are Chaos. Here's the NRI Survival Guide for Memorial Day 2026."
art1_subheadline = "AAA projects a record 45 million Americans will travel at least 50 miles from home this Memorial Day weekend — 39.1 million by car, 3.66 million by air. The national average for regular gasoline is $4.56 a gallon, the highest Memorial Day price in four years, driven by the Iran war and the closure of the Strait of Hormuz. A sinkhole shut down a LaGuardia runway. Severe storms threaten the entire eastern half of the country. And for NRIs who are also pricing summer flights to India — up 24% year-over-year — the financial math of this summer just got significantly harder."
art1_slug = make_slug("memorial-day-2026-nri-travel-gas-prices-flights-survival-guide")
art1_category = "lifestyle-health"

art1_body = """This is the weekend America pretends summer has arrived. Forty-five million people will pack cars, board planes, and sit in traffic that moves slower than a Mumbai autorickshaw in monsoon. They will pay $4.56 a gallon for gasoline — the highest Memorial Day price since 2022 — and they will do it anyway, because Americans do not cancel summer. They postpone retirement savings instead.

For Indian Americans, this weekend carries an additional layer of financial anxiety. Memorial Day is not just the start of summer. It is the start of India Trip Planning Season — the annual exercise in which NRI families discover that the cost of visiting parents in Hyderabad or Chennai has increased by another thousand dollars since last year, and that the only affordable flights require a 14-hour layover in Doha.

This year, both costs — the domestic holiday weekend and the summer India trip — are being driven by the same cause: the Iran war, the closure of the Strait of Hormuz, and the cascading effect on global energy prices that has made everything from a gallon of gas in New Jersey to a litre of petrol in Delhi significantly more expensive.

Here is what NRIs need to know about travelling this weekend, and this summer.

## The Numbers: A Record Weekend at Record Prices

AAA's 2026 Memorial Day forecast is the organisation's biggest projection ever. Forty-five million Americans will travel at least 50 miles from home between Thursday, May 22 and Monday, May 25. Roughly 87 per cent — 39.1 million — will drive. Another 3.66 million will fly domestically.

The national average for a gallon of regular gasoline stands at $4.56, according to AAA. That is up from $3.18 at the same time last year — a 43 per cent increase in twelve months. Every single US state now has an average price above $4 a gallon. In California, Washington, and Hawaii, prices are well above $5.

Since the Iran conflict began, prices have increased by more than 50 per cent. The closure of the Strait of Hormuz — through which roughly one-fifth of the world's oil and liquefied natural gas normally passes — has disrupted global energy markets and pushed up the cost of gasoline, diesel, and jet fuel simultaneously.

GasBuddy forecasts the national average will reach $4.48 per gallon on Memorial Day itself (slightly below today's peak due to a brief dip expected over the weekend), but projects an average of $4.80 per gallon over the summer from Memorial Day through Labor Day — with the possibility of all-time record highs if the Strait remains closed.

For a family driving from, say, Edison, New Jersey to the Poconos and back — roughly 200 miles — the fuel cost alone is now about $35, compared to $24 last year. A round trip from the Bay Area to Lake Tahoe runs about $50 in gas. These are not large numbers individually, but they compound: gas for the weekend trip, plus groceries for the barbecue (up sharply — for the first time in three years, consumer prices are rising faster than wages), plus airfare if you are flying anywhere.

The collective additional cost is staggering. The Institute on Taxation and Economic Policy estimates Americans will spend an extra $3.5 billion on gasoline over this holiday weekend alone compared to last year.

## The Airports: Sinkholes, Storms, and Lines

If you are flying this weekend, the situation is not better — it is different.

On Wednesday, May 21, a sinkhole was discovered near Runway 4/22 at LaGuardia Airport in New York — one of only two runways at one of the busiest airports in the country. The runway was closed for two days. By Friday afternoon, LGA had reported nearly 600 flight delays, according to FlightAware. The runway reopened Friday evening, but residual delays are expected through the weekend.

The Transportation Security Administration expects to screen 18.3 million passengers from Thursday through next Wednesday. Jessica Mayle, a TSA regional spokesperson, advises arriving at the airport two hours early — and she means two hours from when you step foot in the building, not two hours from when your Uber drops you at the kerb.

"You can lose 30 minutes trying to get dropped off," she told CBS News. "Make sure you give yourself plenty of time."

Severe weather adds another variable. Heavy rain and thunderstorms threaten the entire eastern half of the United States this weekend, with flooding possible from the Ohio Valley and Mid-Atlantic down to the Gulf Coast. Texas and Louisiana face the greatest flooding risk on Saturday and Sunday, with slow-moving storms expected to draw deep tropical moisture from the Gulf of Mexico.

Some of the busiest airports on the East Coast could see ground stops due to thunderstorms, including Hartsfield-Jackson Atlanta International, Orlando International, and Charlotte Douglas International. If you are connecting through any of these hubs, build buffer time into your itinerary.

More than 2,000 flights were delayed and over 300 cancelled on Thursday alone, according to FlightAware. Friday numbers were similar. The weekend may improve slightly as the LaGuardia situation stabilises, but weather-related delays are unpredictable.

## The India Trip: Twenty-Four Per Cent More Expensive

For millions of NRI families, Memorial Day weekend is when the annual India trip debate begins in earnest. The kids are almost out of school. The grandparents in Bangalore or Lucknow or Kolkata have been asking when you are coming. The wedding invitations have been arriving since March.

This year, the debate includes a new number: 24 per cent.

That is how much domestic and international airfares have increased year-over-year, according to data from Points Path (a TPG partner). International fares specifically for the summer window — between Memorial Day and Labor Day — are up 22 per cent.

Flights from the US to India, which were already among the most expensive routes in the world during June-July peak season, have become even more so. United Airlines expects to serve 53 million passengers this summer — three million more than last year — and is pricing accordingly.

The math for a family of four flying economy from New York or San Francisco to Delhi or Mumbai during peak summer is now comfortably above $5,000 round-trip, and often closer to $7,000-8,000 depending on dates and airline. Business class is essentially out of reach for most families at $12,000-15,000 per seat.

The underlying driver is the same as at the gas pump: jet fuel. The Iran war and Hormuz closure have pushed jet fuel prices to multi-year highs, and airlines are passing the cost through to passengers with minimal delay.

## The NRI Specific Squeeze

Here is what makes this summer uniquely difficult for Indian American families:

**The dual inflation.** Not only is it more expensive to live in America right now ($4.56 gas, rising grocery bills, higher airfares), but India itself is also getting more expensive. India's wholesale inflation hit a 42-month high of 8.3 per cent in April. Fuel prices in India have been raised three times in the past ten days. Amul and Mother Dairy raised milk prices. Cooking oil is up 14-22 per cent. When you send money home, it buys less than it did a year ago.

**The remittance calculation.** The Indian rupee has weakened against the dollar, which partially offsets domestic inflation for dollar-earners. But the offset is not enough to compensate for the scale of price increases in India. NRIs who send fixed monthly amounts to parents — for household expenses, medical bills, property maintenance — are effectively subsidising a larger share of the family budget than they were twelve months ago.

**The heatwave factor.** If you are planning to visit India in June, you are landing in the middle of the worst heatwave season in recent memory. Temperatures have crossed 48°C in parts of Uttar Pradesh. Fifty-five people died of heatstroke in a single day last week in Andhra Pradesh and Telangana. The India Meteorological Department has warned that conditions will intensify through late May and June. The traditional advice — "visit India in winter" — has never been more relevant, but school schedules do not accommodate it.

**The school calendar trap.** This is the fundamental constraint for NRI families with school-age children. You can only visit India when school is out. School is out in summer. Summer is when flights are most expensive, India is hottest, and domestic US travel is at peak cost. There is no good workaround for this structural problem, only expensive ones.

## What You Can Actually Do

**For this weekend (domestic travel):**
- If you are driving, fill up before Sunday. Gas prices typically dip slightly on Saturday but rebound by Monday. Use GasBuddy or the AAA app to find the cheapest stations on your route.
- If you are flying, check FlightAware before leaving for the airport. Build at least a three-hour buffer for connections through eastern hub airports (ATL, CLT, MCO, LGA, EWR).
- The US-Canada border will see heavy traffic if you are heading north. US Customs and Border Protection has issued a specific travel warning for the Detroit, Port Huron, and Sault Ste. Marie crossings.
- Pack food and water for road trips. Rest stops and highway restaurants are both crowded and expensive this weekend.

**For the summer India trip:**
- Book now if you have not already. Fares typically increase further in June as inventory tightens. September and early October are significantly cheaper if your schedule allows.
- Consider alternate routing. Flights through the Middle East (Qatar Airways, Emirates, Etihad) remain competitive despite regional tensions, as these carriers have significant capacity. Turkish Airlines via Istanbul is often the best value for flexibility.
- If the trip cost is genuinely prohibitive this year, be honest with family. A two-week visit in October when fares are 40 per cent lower and temperatures are bearable may be better for everyone than a financially stressful week in July.

**For the broader financial picture:**
- Revisit your monthly India remittance amount. If your parents' household expenses have increased due to fuel and food inflation, the amount you have been sending may no longer be adequate. A conversation now prevents a crisis call in August.
- If you have a summer road trip planned beyond this weekend, do the fuel math before committing. A 1,000-mile round trip costs roughly $170 in gas at current prices, versus $120 a year ago. That $50 difference adds up across a summer of travel.

## The Bigger Picture

Memorial Day 2026 is the most expensive start to summer in at least four years, and possibly ever. The Iran war has created a global energy shock that is hitting American consumers at the pump, at the airport, at the grocery store, and — for the Indian diaspora — at the family transfer counter as well.

The sixty-year-old retiree in Illinois who told CNN he is "basically pinned at home" because gas prices make the drive to see his great-granddaughter too expensive? That feeling is universal this weekend. But for NRI families, the pinch is bilateral — you are too expensive to travel in America, and too expensive to travel to India, simultaneously.

Forty-five million Americans are travelling anyway. Many of them are Indian Americans, doing the same thing their parents taught them: you show up for family, even when it costs more than it should. The math is harder this year. The showing up has not changed."""

art1_sources = [
    "https://www.cnn.com/2026/05/22/us/travel-memorial-day-weekend",
    "https://seekingalpha.com/news/4596456-memorial-day-pump-prices-up-30-from-last-year",
    "https://wcia.com/news/millions-hit-the-roads-as-gas-prices-surge-ahead-of-memorial-day-weekend/",
    "https://thepointsguy.com/news/best-time-to-book-flights-2026/",
    "https://nbcpalmsprings.com/2026/05/23/millions-take-to-the-skies-for-memorial-day-weekend/",
    "https://audacy.com/1010wins/news/local/memorial-day-higher-fuel-prices",
]

print("=== Article 1: Memorial Day 2026 NRI Travel Survival Guide ===")
print(f"Word count: {len(art1_body.split())}")

# Fetch Pexels image for article 1
art1_image = fetch_pexels_image("highway traffic cars holiday weekend sunset")
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
    "tags": ["Memorial Day", "NRI", "gas prices", "travel", "Iran war", "airfare", "India trip", "inflation", "AAA", "summer travel", "flights", "LaGuardia", "Strait of Hormuz", "diaspora"],
    "vertical": "diaspora",
    "urgency": "high",
    "diaspora_angle": "Memorial Day 2026 is the most expensive holiday travel weekend in four years — $4.56 gas, 45M travelers, severe weather. For NRIs, the squeeze is bilateral: domestic travel costs are up 43%, and summer India flights are up 24% YoY. Plus India's own inflation (fuel hiked 3x in 10 days) means remittances buy less. A practical survival guide for both this weekend and the summer India trip.",
    "word_count": len(art1_body.split()),
    "image_url": art1_image["url"] if art1_image else None,
    "image_caption": f"Photo by {art1_image['photographer']} via Pexels" if art1_image else None,
})
if result:
    print(f"✓ Published: {art1_id}")
else:
    print("✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: India Raised Fuel Prices Three Times in Ten Days
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "India Raised Fuel Prices Three Times in Ten Days. Milk Is Up. Bread Is Up. Cooking Oil Is Up 22%. Your Family Back Home Noticed Before You Did."
art2_subheadline = "On May 15, India raised petrol and diesel prices for the first time in four years. On May 19, they raised them again. On May 23, a third increase: petrol in Delhi now costs ₹99.51 per litre, up ₹5 in ten days. Wholesale inflation has hit a 42-month high of 8.3%. Amul and Mother Dairy raised milk prices by ₹2 per litre. Modern Bread is up ₹5 per pack. Cooking oil has surged 14-22% in a year. India banned sugar exports until September. For NRIs sending money home, the rupee you wire buys measurably less than it did last month."
art2_slug = make_slug("india-fuel-price-hike-three-times-inflation-nri-family-cost-of-living")
art2_category = "lifestyle-health"

art2_body = """Your mother called last week. Not about her health, not about the neighbour's daughter's wedding, not about when you are visiting. She called about the price of Amul Gold.

"Two rupees more per litre," she said. "They increased it on the fourteenth."

Two rupees does not sound like much. It is roughly two and a half cents. But your mother buys four litres of milk a day — for tea, for curd, for the grandchildren when they visit, for the chai she makes when the neighbours come over. Eight rupees a day. Two hundred and forty rupees a month. Nearly three thousand rupees a year. On milk alone.

And milk is not the only thing that got more expensive in the past ten days. Everything did.

## Three Hikes in Ten Days

On May 15, India's state-owned fuel retailers — Indian Oil Corporation, Bharat Petroleum, and Hindustan Petroleum, which together control more than 90 per cent of the country's 103,000 fuel stations — raised petrol and diesel prices for the first time in four years.

The freeze had been political. Opposition parties have long alleged that the Modi government postponed fuel price increases ahead of state elections to avoid voter backlash. The companies absorbed losses for years, quietly subsidising the gap between global crude oil prices and domestic pump prices. That gap became untenable after the Iran war began and the closure of the Strait of Hormuz sent crude oil above $90-100 a barrel.

On May 15, the dam broke.

Four days later, on May 19, prices were raised again.

On Saturday, May 23, they were raised a third time. Petrol in Delhi now costs ₹99.51 per litre — flirting with the psychologically significant ₹100 mark. Diesel is at ₹92.49. In total, fuel has become roughly ₹5 more expensive per litre in ten days.

And BPCL's chairman said this week that the company is still losing money: 25 to 30 rupees per litre on diesel and 10 to 14 rupees per litre on petrol, even after the three hikes. More increases are coming. The oil ministry has said the government has no plans to provide financial support for refiners.

In other words: we are nowhere near the end of this.

## The Cascade Effect

Fuel prices in India are not just about what it costs to fill your car. They are the input cost for everything.

When diesel goes up, transportation costs go up. When transportation costs go up, the price of vegetables, fruit, grain, and every other commodity that moves by truck — which in India means virtually everything — goes up. When crude oil goes up, the cost of plastics, polymers, and petrochemicals goes up, which means packaging costs go up, which means every FMCG product from shampoo to biscuits to toothpaste gets more expensive.

The data is already visible:

**Dairy:** Amul and Mother Dairy raised retail milk prices by ₹2 per litre on May 14. Heritage Foods reported that average milk procurement prices rose 8 per cent year-over-year to ₹46.67 per litre in the January-March quarter. This is not a temporary blip. Feed costs, transportation costs, and cold chain costs are all rising simultaneously.

**Bread and staples:** Modern Bread increased prices by ₹5 per pack on May 16 on basic variants. Wheat and sugar prices are on an upward trajectory, putting pressure on every biscuit maker, bakery, and atta brand in the country.

**Cooking oil:** Prices have surged 14-22 per cent over the past year, according to industry reports. India banned sugar exports on May 13 until September 30 to try to contain domestic price pressures — a measure that signals the government expects the situation to worsen before it improves.

**FMCG broadly:** According to the May 2026 FMCG pulse report by Worldpanel (formerly Kantar), FMCG value growth was 13.1 per cent in the January-March quarter — but volume growth was only 5.4 per cent. The gap between those two numbers is inflation. People are spending more and getting the same amount of stuff.

## The Macro Picture: 42-Month High

India's wholesale price index (WPI) inflation surged to 8.3 per cent in April, up from 3.88 per cent in March. This is the highest reading in 42 months — three and a half years.

The driver is unmistakable. Fuel and power inflation jumped from 1.05 per cent in March to 24.71 per cent in April. Crude petroleum inflation alone hit 88.06 per cent year-on-year. According to Barclays, the sequential increase in WPI inflation was the highest on record in the series.

Retail inflation — the Consumer Price Index, which directly measures what households pay — edged up to 3.48 per cent in April, which sounds moderate. But economists warn that wholesale inflation has a way of becoming retail inflation with a lag. "Q2, you'll start seeing demand falling as an effect of all these factors," said Anand Ramanathan, partner and consumer industry leader at Deloitte South Asia. "FMCG typically takes time to react."

Standard Chartered now expects India to begin hiking interest rates in June. If the Reserve Bank of India raises rates — for the first time since the pandemic-era tightening cycle ended — the cost of home loans, car loans, and business credit will increase too. For your cousin building a house in Pune or your brother who just bought a car in Noida, this matters.

## What This Means for NRIs

If you are one of the approximately 18 million members of the Indian diaspora worldwide — and particularly if you are among the 4.8 million Indian Americans — the inflation in India is not an abstraction. It is a line item in your family's monthly budget that you are partially or fully funding.

**Your remittance buys less.** If you send ₹50,000 a month to your parents for household expenses — a common amount for middle-class NRI families supporting retired parents — that amount covered more six months ago than it does today. Milk, cooking oil, fuel, vegetables, bread: the basket of goods your parents need has gotten 5-10 per cent more expensive in aggregate, with some individual items up 15-22 per cent. If you have not adjusted your remittance amount, there is a growing gap between what you send and what it costs to live.

**The rupee helps, but not enough.** The Indian rupee has weakened to around ₹86-87 per dollar, which means your dollars buy more rupees than they did a year ago. But the exchange rate benefit (roughly 3-4 per cent over the past year) does not fully offset the domestic inflation (wholesale at 8.3 per cent, with food and fuel categories significantly higher). The net effect is negative for your family's purchasing power.

**LPG is the hidden hit.** Commercial LPG costs, which affect restaurants and small businesses, have risen sharply. But domestic LPG — the cooking gas cylinder that most Indian households depend on — is also under pressure. If your parents are on the Pradhan Mantri Ujjwala Yojana subsidy, the government has so far maintained the subsidised price. If they buy at market rates, the cost has increased meaningfully. Ask which one they are on.

**Property maintenance costs are up.** If you own property in India — a flat in Bangalore, a plot in Chandigarh, a house in Kerala — the cost of maintaining it has increased. Construction labour costs, which are linked to fuel and food prices, are rising. Painting, plumbing, electrical work: everything costs more. If you have a property manager or a relative handling maintenance, their invoices will be higher this quarter.

## The Political Dimension

The fuel price freeze was always political. India held it for four years — through the post-pandemic recovery, through the Ukraine war, through multiple state elections. The price of this freeze was borne by BPCL, IOC, and HPCL in the form of enormous losses. The companies absorbed the hit because the government asked them to.

Now the dam has broken, and the government's framing is clear: this is the Iran war's fault, not a domestic policy failure. Opposition parties are pointing out that the timing — three hikes in ten days, immediately after the recent state elections concluded — confirms that the freeze was an electoral strategy, not an economic one.

For NRIs, the politics matter less than the trajectory. Whether you blame Modi or blame Iran, the prices are going in one direction. More hikes are coming. The BPCL chairman's admission that the company is still losing ₹25-30 per litre on diesel even after three increases means the current prices are still below what the companies need to break even. The path to cost recovery is measured in months of incremental increases, not a single correction.

## What to Do

**Have the money conversation.** If you are sending a fixed amount home every month and have not revisited it in six months, now is the time. Ask your parents or siblings what their actual monthly expenses are. The answer may be 10-15 per cent higher than what they told you last year — and many Indian parents will not volunteer this information because they do not want to burden you.

**Build a fuel and food buffer.** If you are funding a household in India, add a 10-15 per cent buffer to your remittance amount for the next six months. If the inflation moderates (unlikely before the monsoon, and possibly not until the Iran situation resolves), you can scale back. If it accelerates — which Standard Chartered's forecast of rate hikes suggests is a real possibility — you will be glad you adjusted early.

**Check the LPG situation.** A five-minute phone call to find out whether your parents are getting subsidised LPG or paying market rate could save them ₹200-300 per cylinder per month. If they are eligible for the subsidy but not enrolled, the enrolment process is straightforward.

**Don't panic about interest rates — but plan for them.** If your family in India has floating-rate loans (home loan, car loan), a rate hike cycle would increase their EMIs. If they are already stretched, this is worth discussing before it happens rather than after.

**Track the rupee.** The exchange rate is one of the few variables working in NRIs' favour right now. If you have been delaying a large transfer — for property taxes, medical procedures, school fees — the weak rupee means your dollars go further. This window may not last if the RBI intervenes or global conditions shift.

## The Bottom Line

India's three fuel price hikes in ten days are the beginning of a correction, not the end of one. The wholesale inflation number — 8.3 per cent — is a headline figure that will filter through to retail prices over the coming months. For NRI families funding households in India, the cost of supporting parents, maintaining property, and planning visits has increased by a meaningful amount in a very short time.

Your mother probably will not tell you that the grocery bill went up. She will absorb the difference by buying slightly less ghee, or switching from Amul Gold to Amul Taaza, or skipping the fruit that used to be on the table every evening. She will manage, because that is what Indian mothers do.

But she should not have to manage alone. A ten-minute conversation about money — specific, numerical, honest — is worth more than any amount of concern expressed in WhatsApp voice notes.

Call her. Ask about the milk."""

art2_sources = [
    "https://www.tbsnews.net/world/south-asia/indian-retailers-raise-fuel-prices-third-time-amid-iran-war-1446496",
    "https://www.livemint.com/money/personal-finance/wholesale-inflation-hits-a-42-month-high-11779344773961.html",
    "https://www.livemint.com/companies/news/fmcg-products-costs-global-pressures-consumption-inflation-crude-oil-prices-11779337201200.html",
    "https://reuters.com/world/india/india-rate-hikes-start-june-standard-chartered-2026-05-21/",
]

print("\n=== Article 2: India Fuel Price Hikes — NRI Family Impact ===")
print(f"Word count: {len(art2_body.split())}")

# Fetch Pexels image for article 2
art2_image = fetch_pexels_image("Indian market vegetables grocery store prices")
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
    "score_total": 89,
    "tags": ["India", "fuel prices", "inflation", "NRI", "remittances", "WPI", "Amul", "cooking oil", "BPCL", "IOC", "Iran war", "cost of living", "RBI", "interest rates", "diaspora", "family", "FMCG"],
    "vertical": "diaspora",
    "urgency": "high",
    "diaspora_angle": "India raised fuel prices three times in ten days — first hike in four years. Wholesale inflation at 42-month high (8.3%). Milk, bread, cooking oil all up. For NRIs sending money home, the fixed monthly remittance now buys measurably less. Standard Chartered expects RBI rate hikes starting June. A guide to adjusting remittances and having the money conversation with family.",
    "word_count": len(art2_body.split()),
    "image_url": art2_image["url"] if art2_image else None,
    "image_caption": f"Photo by {art2_image['photographer']} via Pexels" if art2_image else None,
})
if result:
    print(f"✓ Published: {art2_id}")
else:
    print("✗ Failed or duplicate")

print("\n✅ Both articles published successfully")
