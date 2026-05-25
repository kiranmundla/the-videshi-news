#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-25 18:30 UTC batch
Topics: 1) US tourism collapse — 4 million fewer visitors, India down 4%, $8.4B lost, self-inflicted
        2) Five South Asian Americans won historic elections in Georgia on a single night — first Sikh, first South Asian Lt. Gov nominee
"""

import json, os, uuid, re, requests, subprocess
from datetime import datetime, timezone, timedelta
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

def sb_patch(table, params, data):
    h = {**HEADERS, "Prefer": "return=representation"}
    r = requests.patch(f"{SB_URL}/rest/v1/{table}", headers=h, params=params, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(slug_base, date_suffix="20260525"):
    slug = slug_base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

# ── Pexels helper ──
pexels_env = Path.home() / "workspace" / ".env.pexels"
PEXELS_KEY = None
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.split("=", 1)[1].strip()

def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        print("  ⚠ No Pexels key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=15
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                if photos:
                    url = photos[0]["src"]["large2x"]
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    try:
        img_data = requests.get(image_url, timeout=20).content
        content_type = "image/jpeg"
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        h = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        r = requests.post(upload_url, headers=h, data=img_data, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {filename}")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({r.status_code}): {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return image_url

# ── Duplicate check ──
existing = sb_get("p2_articles", {
    "select": "headline,slug",
    "status": "eq.published",
    "published_at": "gte.2026-05-23T00:00:00Z",
    "order": "published_at.desc",
    "limit": "80"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc)
now_iso = now.isoformat().replace('+00:00', 'Z')
now_plus1 = (now + timedelta(minutes=1)).isoformat().replace('+00:00', 'Z')

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: US Tourism Collapse — 4 Million Fewer Visitors, India Down 4%
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("us-tourism-collapse-4-million-fewer-visitors-india-down-4-percent-nri")
headline1_prefix = "four million fewer"
if slug1 not in existing_slugs and not any(headline1_prefix in h for h in existing_headlines_lower):
    body1 = """The complete 2025 data is in, and the number is worse than anyone expected.

Four million fewer international visitors came to the United States last year compared to 2024. Total foreign spending dropped by $8.4 billion. It was the worst single-year decline in international tourism in two decades, with the sole exception of the pandemic year. And unlike 2020, this was not caused by a virus.

"We used to be a country that others wanted to emulate. That narrative no longer exists," said Juliette Kayyem, faculty chair of the Homeland Security Project at the Harvard Kennedy School.

The analysis, published by CNN on May 25 using data from Tourism Economics and the World Travel and Tourism Council, identifies a convergence of factors: presidential rhetoric, ICE enforcement actions, a proposed $250 visa integrity fee, the defunding of Brand USA — the only American organization that markets US tourism to international audiences — and the Iran war, which has restricted air routes across the Middle East and spiked jet fuel prices globally.

India is specifically called out. Visitor numbers from India are expected to dip more than 4 percent this year, driven in part by restricted airspace over the Middle East that has complicated and lengthened flights between India and the United States.

## The Scale of the Self-Inflicted Damage

The 5.5 percent decline in international arrivals did not happen in a vacuum. Eighty million more people traveled internationally in 2025 than in 2024, according to the World Travel and Tourism Council. They chose other destinations.

The United States was an outlier — a country that got fewer visitors while the rest of the world got more. Tourism Economics estimates the true loss, measured against what was forecast if the US had stayed on its pre-existing growth track, is closer to $25 billion.

For context, the US has historically maintained a positive trade balance in only one significant sector: travel. In 2025, that flipped. Americans now spend more traveling abroad than foreign visitors spend visiting the United States.

Adam Sacks, president of Tourism Economics, called the combination of proposed visa fees and tariff wars "pennywise and pound foolish" — policies that create an appearance of bringing in revenue while costing the economy far more in lost tourism.

## What Is Keeping People Away

The reasons are both perceptual and practical.

The perceptual side: international visitors absorb a filtered story of the United States — "a dysfunctional government, ICE raids, Americans being killed, crime everywhere," as Kayyem described it. The images that define America abroad are no longer the Statue of Liberty and Silicon Valley. They are immigration raids on restaurants, federal agents confronting citizens in Minneapolis, and a president posting AI-generated images of Iranian boats being destroyed.

Brand USA, which existed specifically to counter these perceptions and market the United States as a destination, was defunded. Bills to restore funding were introduced in both the House and Senate. Neither has moved forward.

The practical side: a proposed $250 visa integrity fee that has created confusion even though it is not yet being collected. A floated idea from the Department of Homeland Security secretary to restrict customs processing at airports in sanctuary cities. A Trump administration proposal to collect five years of social media history from certain visitors. Each of these, even when not implemented, contributes to a perception that the United States is not welcoming visitors — it is screening them.

Then there is the Iran war. The conflict has closed or restricted air routes across the Middle East. Jet fuel prices have spiked. For Indian travelers specifically, the most direct path between major Indian cities and the eastern United States runs through Middle Eastern airspace. Those routes are now disrupted.

## Disney Felt It. Florida Felt It. Business Owners Went Under.

The damage is not abstract. Walt Disney World reported domestic theme park attendance down 1 percent in its most recent quarter, "reflecting, in part, continued softness in international visitation." Hotel occupancy at Disney's domestic resorts fell from 92 percent to 89 percent year-over-year.

Florida, the country's most popular warm-weather destination for international visitors, bore the worst of the decline. The Sunshine State is a magnet for snowbirds from Canada — and Canadians led the retreat from the United States, accounting for the vast majority of the 4-million-visitor drop. Cell phone tracking data from Cuebiq shows a 42 percent decline in Canadian visits to US metropolitan areas in the past year.

Small businesses are drowning. Joe Koenen, who runs Seattle Free Walking Tours, has spent more on marketing than ever. Bookings are still down. Adam Duford, who runs Surf City Tours in Santa Monica, had to let go of all seven employees. His 2025 revenue was less than half of what it was in previous years. He now runs one tour bus to Malibu by himself while trying to pay off a Covid-era loan.

"It was terrible," Duford said of letting his team go. "They were so surprised and taken off guard. I was surprised they were surprised, so that made it almost worse."

## The Recovery Will Be Slow

Overseas travel to the US — excluding Canada and Mexico — is "down another 4.3 percent through April" of 2026, according to Tourism Economics. There are hints of a rebound: Canadian car visits increased 5.8 percent in April compared to the same month last year, the first monthly increase in over a year. But air visits are still down, and the broader recovery is projected to be long. The National Travel and Tourism Office does not expect international arrivals to exceed pre-pandemic levels until 2029 — a full decade after Covid.

The FIFA World Cup, which the US is co-hosting this summer, is one bright spot. An estimated 1 million visitors are expected. But FIFA had initially anticipated the equivalent of 100 Super Bowls' worth of visitors; the reality will be closer to 10 Super Bowls, Sacks said — nowhere near enough to offset the 2025 losses.

## What This Means for the Indian Diaspora

For India, the numbers tell a particular story.

Indian visitor numbers to the US are expected to drop more than 4 percent this year. That is not a number about tourists. Indian visitors to the United States are overwhelmingly family — parents visiting their children in the Bay Area, grandparents coming for a grandchild's birth, siblings attending a wedding. The B-1/B-2 visitor visa is, for the Indian diaspora, a family reunification mechanism.

When those numbers drop, it means families are not seeing each other. It means a grandmother in Hyderabad who saved for three years for a plane ticket is reconsidering because the route now takes 18 hours instead of 14, costs 30 percent more due to fuel surcharges, and arrives in a country where she has seen news clips of elderly people being questioned by immigration agents.

The US visa experience for Indian visitors was already one of the most challenging in the world. Wait times for B-1/B-2 visa interviews at the Chennai and Mumbai consulates regularly exceeded 300 days. The proposed $250 visa integrity fee — even though it has not been implemented — adds psychological weight to a process that already feels adversarial. An Indian family that has to travel to a different city for a consulate appointment, wait a year for the interview, pay existing fees, and now potentially face an additional $250 charge, is being told, in the language of bureaucracy, that their visit is a compliance risk to be managed rather than an economic contribution to be welcomed.

The irony is that Indian visitors to the United States spend. They stay for weeks, not days. They shop. They pay for hotels, flights, restaurants, theme parks. They attend conferences. The average Indian visitor to the US spends considerably more per trip than visitors from most European countries, because the trip is expensive enough that only those with significant budgets undertake it.

When the US loses 4 percent of those visitors, it is not losing backpackers. It is losing families with purchasing power who have chosen — or been forced — to spend that money elsewhere.

And for the 4.8 million Indian Americans already in the country, the message is different but related. The decline in Indian visitors is not just an economic statistic. It is a measure of how accessible America is to the people they love. Every percentage point represents someone's mother who did not come this year, someone's father who could not get a visa appointment, someone's brother who looked at the flight prices and the news cycle and decided it was not worth the risk.

Kayyem put it starkly: "The long-term harm is that the world will not know America."

For the Indian diaspora, the harm is more immediate. America is where they live. India is where their families are. And the distance between those two places — measured not in miles but in visa wait times, restricted airspace, spiking costs, and a national mood that treats visitors as threats — is growing."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Four Million Fewer People Visited the United States Last Year. It Was the Worst Decline Since the Pandemic. India's Visitor Numbers Are Down More Than 4 Percent. The Reasons Are Entirely Self-Inflicted.",
        "subheadline": "Complete 2025 data shows the US lost 4 million international visitors and $8.4 billion in tourism spending — the worst single-year decline in two decades outside of Covid. Eighty million more people traveled internationally in 2025 than in 2024. They chose other destinations. India is specifically flagged: visitor numbers are expected to dip more than 4 percent this year, driven by restricted Middle East airspace from the Iran war, spiking jet fuel prices, and a visa process that has become increasingly adversarial. Brand USA, the country's only international tourism marketing body, was defunded. A proposed $250 visa integrity fee has created confusion. Disney's international attendance is down. Florida took the worst hit. Small tourism businesses have shuttered. Tourism Economics says recovery won't reach pre-pandemic levels until 2029 — a full decade after Covid.",
        "slug": slug1,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "Indian visitors to the United States are not tourists. They are parents visiting children in California. Grandparents traveling for a grandchild's first birthday. Siblings attending a wedding. The B-1/B-2 visa is the Indian diaspora's family reunification mechanism — and every percentage point of that 4 percent decline represents someone's mother who did not come this year. The visa interview wait at Chennai and Mumbai regularly exceeds 300 days. The proposed $250 fee adds insult to an already punishing process. Middle East airspace restrictions from the Iran war have turned a 14-hour flight into an 18-hour ordeal at 30 percent higher cost. And the news cycle — ICE raids, border enforcement rhetoric, customs processing threats — tells Indian families that America is not welcoming visitors, it is screening them. For 4.8 million Indian Americans, the tourism collapse is not an economic abstraction. It is measured in how many months it has been since they saw their parents. The US trade surplus in travel — historically the one sector where America exported more than it imported — has flipped. Americans now spend more traveling abroad than foreigners spend visiting the US. The country that built an economy on welcoming the world has made the world feel unwelcome. Indian families with purchasing power who used to spend weeks in America — shopping, eating, attending parks, visiting family — are reconsidering. Some are going to Dubai instead. Some are going to Singapore. Some are simply not going anywhere. And the distance between an NRI in San Jose and their parents in Hyderabad — measured not in miles but in visa wait times, restricted airspace, spiking costs, and political hostility — keeps growing.",
        "tags": ["US tourism", "international visitors", "India", "NRI", "visa", "Brand USA", "ICE", "Iran war", "airspace", "travel", "Disney", "Florida", "Canada", "tourism collapse", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "CNN — Analysis: Millions fewer visitors, billions in lost tourism dollars", "url": "https://www.cnn.com/2026/05/25/travel/analysis-tourism-fewer-international-visitors-2025-vis"},
            {"name": "World Travel and Tourism Council — US Tourism Crossroads Report", "url": "https://wttc.org/"},
            {"name": "Tourism Economics — International Visitor Forecasts", "url": "https://tourismeconomics.com/"},
            {"name": "Statistics Canada — Border Crossing Data", "url": "https://www150.statcan.gc.ca"}
        ]),
        "score_total": 86,
        "status": "published",
        "published_at": now_iso,
        "body": body1
    })
    print(f"✓ Article 1 prepared: US tourism collapse / India visitors down 4%")
else:
    print(f"✗ Article 1 skipped (duplicate detected)")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Five South Asian Americans Won Historic Elections in Georgia
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("georgia-south-asian-americans-historic-election-wins-nabilah-parkes-jyot-singh")
headline2_prefix = "south asian"
headline2_alt = "georgia"
if slug2 not in existing_slugs and not any(headline2_prefix in h and headline2_alt in h for h in existing_headlines_lower):
    body2 = """On the night of May 19, five South Asian Americans won primary elections or advanced to runoff races in Georgia. One of them could become the first South Asian and Asian American lieutenant governor nominee from any party in the state's history. Another is on track to become the first Sikh elected official in Georgia history.

This happened one week before a sitting member of Congress proposed a constitutional amendment to bar naturalized citizens from serving in government. It happened in a state with more than 600,000 Asian American residents and an Asian American voter turnout growth of 84 percent since 2016.

Nobody in national media covered it as a story.

## Who Won

**Nabilah Islam Parkes** advanced to a runoff in the race for lieutenant governor of Georgia. If she wins the runoff, she will become the first South Asian and the first Asian American lieutenant governor nominee from any political party in Georgia's history.

Parkes, 36, was born in Atlanta to parents from Bangladesh. Her father worked as a file clerk at the Internal Revenue Service. Her mother, originally from Noakhali, Bangladesh, worked various low-wage jobs — at one point as a cook at Hardee's, at another in a warehouse. When an insurance company tried to deny her mother health benefits after she took time off work due to a herniated disc, Parkes became a healthcare advocate. She has not stopped.

She graduated from Central Gwinnett High School and Georgia State University. She ran for Congress in 2020 in Georgia's 7th Congressional District and was endorsed by Alexandria Ocasio-Cortez, Ilhan Omar, and Ro Khanna. She finished a close third with 12.3 percent of the vote. During that campaign, she could not afford her rent, did not have health insurance, and put her student loans into forbearance. She filed a petition to the Federal Election Commission to allow candidates to use campaign contributions for a minimum salary and health benefits — arguing that current regulations effectively barred working-class people from running for office. In December 2023, the FEC approved that rule change in a 5-1 vote. Every working-class candidate who runs for office in America from this point forward benefits from a rule that Nabilah Islam Parkes made happen.

In 2022, she won a state Senate seat in Gwinnett County, becoming the first Muslim woman in the Georgia State Senate. The Atlanta Journal-Constitution called her "Georgia's AOC." She resigned from the Senate in March 2026 to run for lieutenant governor.

**Jyot Singh** won the Democratic primary for State House District 97 outright. He is on track to become the first Sikh elected official in Georgia history.

For a community that has been in the United States since the early 1900s — Sikh immigrants were among the first Asian arrivals in the American West — the absence of Sikh elected officials in a state with a significant Punjabi population was not an oversight. It was a gap. Jyot Singh's victory fills it.

**Saira Draper** won a competitive primary for State Senate District 44. She joins a growing roster of South Asian women in Georgia state government who are building political careers not through family dynasties or corporate networks, but through district-level organizing.

**Akbar Ali** secured the Democratic nomination for State House District 106. He is already the youngest state legislator in Georgia. His re-nomination confirms that his initial win was not a novelty — it was a mandate.

**Rahul Garabadu** advanced to a runoff in a competitive State Senate District 7 race. His name alone tells a story about the new Georgia electorate: a Garabadu running for state senate in a state where, two decades ago, the name would have needed a pronunciation guide for the voter registration office.

## The Numbers Behind the Night

Indian American Impact, the organization that endorsed all five candidates, has supported more than 200 candidates across the country since its founding in 2016, marshaling upward of $20 million in resources. Chintan Patel, the organization's executive director, said the results "speak to the growing political power and representation of our communities."

The numbers back him up. Georgia is home to more than 600,000 Asian American residents. Asian American voter turnout in the state has grown 84 percent since 2016. Metro Atlanta's Gwinnett County — where Parkes built her political career — has become one of the most diverse counties in the American South. The Asian American Advocacy Fund has doubled the state legislature's AAPI caucus to 10 members. Eight Indian Americans appeared on Atlanta Magazine's 2024 Power 500 list — not in a dedicated "diversity" section, but alongside the city's most influential leaders in business, technology, and civic life.

This is not a trend. It is a structural shift in who holds power in a state that, until 2020, was considered reliably Republican.

## Why This Matters Beyond Georgia

The same week these five South Asian Americans won elections, Representative Nancy Mace of South Carolina proposed a constitutional amendment to bar all naturalized citizens from serving in Congress. She named Pramila Jayapal, born in Chennai, and Shri Thanedar, born in Belgaum, as examples of the people she wanted to exclude.

The juxtaposition is almost too neat. In one chamber of American politics, a legislator argues that people who were not born in the United States should be stripped of the right to serve. In another — 500 miles away, in the red clay of Georgia — voters are electing South Asian Americans to serve in record numbers. They are doing it not as a symbolic gesture, but because these candidates knocked on doors, organized precincts, and won more votes.

Mace's amendment requires two-thirds of Congress and ratification by 38 states. It will not pass. The Georgia results, by contrast, are already law. These candidates won. They will serve. And in Nabilah Islam Parkes' case, she may serve in the second-highest executive office in a state with 10.7 million people.

The question is not whether South Asian Americans belong in American government. Georgia answered that on May 19. The question is whether the rest of the country is paying attention.

## The Immigrant Parent Story

What makes these victories distinctive is not just the candidates' ethnicity. It is their origin story.

Nabilah Islam Parkes is the daughter of a file clerk and a Hardee's cook from Bangladesh. She could not pay her rent while running for Congress. She is now one election away from being lieutenant governor.

Jyot Singh will be the first Sikh to hold elected office in a state where Sikh temple congregations have existed for decades — worshipping, paying taxes, running businesses, and raising children who now run for office.

Akbar Ali is the youngest legislator in Georgia. He did not wait for permission or precedent.

These are not dynasty politicians. They are not the children of diplomats or tech executives. They are the children of immigrants who worked in warehouses and government offices and fast-food kitchens, who could not have imagined that their children would one day write the laws of the state they came to.

Indian American Impact has endorsed 200 candidates since 2016. The organization exists because the old model — waiting for mainstream parties to notice that 4.8 million Indian Americans exist and then offer them a seat — was not working. So they built their own pipeline. And on one Tuesday night in May, in a state that Joe Biden won by fewer than 12,000 votes in 2020, five products of that pipeline won.

The Mace amendment asks whether naturalized Americans are American enough to serve. Georgia's voters have given their answer. It is not a debate. It is a ballot count."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Five South Asian Americans Won Historic Elections in Georgia on a Single Night. One Could Become the State's First Asian American Lieutenant Governor. Another Will Be Its First Sikh Elected Official. Nobody Covered It.",
        "subheadline": "On May 19, Georgia's primary elections produced a slate of South Asian American victories that would have been unimaginable a decade ago. Nabilah Islam Parkes — the daughter of a Bangladeshi file clerk and a Hardee's cook — advanced to a runoff for lieutenant governor, positioning her to become the first South Asian and first Asian American nominee for the office in Georgia history. Jyot Singh won State House District 97 outright, on track to become the first Sikh elected official in the state. Saira Draper, Akbar Ali, and Rahul Garabadu also won or advanced. Georgia has more than 600,000 Asian American residents and has seen 84 percent growth in Asian American voter turnout since 2016. The results came one week before a sitting congresswoman proposed banning all naturalized citizens from government service.",
        "slug": slug2,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "If you are South Asian in America and wondering whether your community has political power, Georgia just gave you the answer. Five South Asian Americans won or advanced in primary elections on a single night — in a state that was reliably Republican until 2020. The lieutenant governor candidate's parents are from Bangladesh. Her mother worked at Hardee's. Her father was a file clerk at the IRS. Their daughter could not afford rent while running for Congress four years ago. She is now one runoff away from the second-highest office in a state of 10.7 million people. The first Sikh elected official in Georgia's history will take office because Jyot Singh knocked on enough doors in House District 97 to win outright. This is not representation as symbolism — it is representation as arithmetic. Indian American Impact has endorsed 200+ candidates since 2016, investing more than $20 million, because the old model of waiting for party gatekeepers to notice that 4.8 million Indian Americans exist was not producing results. So they built their own pipeline. And in Gwinnett County — one of the most diverse counties in the American South — that pipeline is now producing lieutenant governor candidates. One week after these elections, Representative Nancy Mace proposed banning all naturalized citizens from Congress. She named two Indian-born lawmakers. Georgia's voters had already given their response: they elected five South Asian Americans in one night. The contrast is not subtle. And the fact that it received almost no national media coverage tells you exactly how far ahead of the conversation the Indian diaspora's political infrastructure already is.",
        "tags": ["Georgia", "South Asian Americans", "Indian Americans", "Nabilah Islam Parkes", "Jyot Singh", "Saira Draper", "Akbar Ali", "Rahul Garabadu", "elections", "primary", "lieutenant governor", "Sikh", "Gwinnett County", "NRI", "Indian American Impact", "political power"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye — Indian American Impact Congratulates Endorsed Candidates on Historic Wins in Georgia", "url": "https://theindianeye.com/2026/05/21/indian-american-impact-congratulates-endorsed-candidates-on-historic-wins-in-georgia/"},
            {"name": "South Asian Herald — Indian American Impact Celebrates Georgia Primary Wins", "url": "https://southasianherald.com/indian-american-impact-celebrates-georgia-primary-wins/"},
            {"name": "Wikipedia — Nabilah Parkes", "url": "https://en.wikipedia.org/wiki/Nabilah_Parkes"},
            {"name": "Asian American Advocacy Fund — Historic Wins in Georgia Election", "url": "https://asianamericanadvocacyfund.org/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now_plus1,
        "body": body2
    })
    print(f"✓ Article 2 prepared: Georgia South Asian election victories")
else:
    print(f"✗ Article 2 skipped (duplicate detected)")


# ══════════════════════════════════════════════════════════════
# PUBLISH + IMAGE SOURCING
# ══════════════════════════════════════════════════════════════

if not articles:
    print("\n⚠ No new articles to publish. Exiting.")
    exit(0)

print(f"\n📝 Publishing {len(articles)} articles...")

for i, art in enumerate(articles):
    art_id = art["id"]
    print(f"\n--- Article {i+1}: {art['headline'][:80]}...")

    try:
        result = sb_post("p2_articles", art)
        print(f"  ✓ Inserted: {art_id}")
    except Exception as e:
        print(f"  ✗ Insert failed: {e}")
        continue

    if i == 0:
        img_url = fetch_pexels_image("empty airport terminal international", "airport arrivals departure hall")
    else:
        img_url = fetch_pexels_image("voting election American democracy", "ballot box election day")

    if img_url:
        filename = f"{art['slug']}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        try:
            sb_patch("p2_articles", {"id": f"eq.{art_id}"}, {"image_url": final_url})
            print(f"  ✓ Image linked")
        except Exception as e:
            print(f"  ⚠ Image PATCH failed: {e}")

# ══════════════════════════════════════════════════════════════
# SCORE DECAY
# ══════════════════════════════════════════════════════════════

print("\n📉 Applying score decay to older news articles...")
try:
    old_arts = sb_get("p2_articles", {
        "select": "id,score_total",
        "status": "eq.published",
        "category": "eq.news",
        "published_at": f"lt.{(now - timedelta(days=7)).isoformat().replace('+00:00', 'Z')}",
        "score_total": "gt.35",
        "limit": "200"
    })
    for a in old_arts:
        sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": 35})
    print(f"  Decayed {len(old_arts)} articles (>7d → 35)")

    mid_arts = sb_get("p2_articles", {
        "select": "id,score_total",
        "status": "eq.published",
        "category": "eq.news",
        "published_at": f"lt.{(now - timedelta(days=3)).isoformat().replace('+00:00', 'Z')}",
        "score_total": "gt.50",
        "limit": "200"
    })
    mid_arts = [a for a in mid_arts if a["id"] not in {x["id"] for x in old_arts}]
    for a in mid_arts:
        sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": 50})
    print(f"  Decayed {len(mid_arts)} articles (3-7d → 50)")
except Exception as e:
    print(f"  ⚠ Decay error: {e}")

# ══════════════════════════════════════════════════════════════
# GIT COMMIT + PUSH
# ══════════════════════════════════════════════════════════════

print("\n📦 Committing and pushing...")
repo_dir = Path.home() / "workspace" / "the-videshi-news"
try:
    subprocess.run(["git", "add", "-A"], cwd=repo_dir, capture_output=True, timeout=15)
    result = subprocess.run(
        ["git", "commit", "-m", f"news: US tourism collapse + Georgia South Asian victories ({now.strftime('%Y-%m-%d %H:%M')} UTC)"],
        cwd=repo_dir, capture_output=True, text=True, timeout=15
    )
    print(f"  Commit: {result.stdout.strip()[:100]}")
    push = subprocess.run(["git", "push"], cwd=repo_dir, capture_output=True, text=True, timeout=30)
    if push.returncode == 0:
        print("  ✓ Pushed to main → Vercel auto-deploy")
    else:
        print(f"  ⚠ Push issue: {push.stderr[:200]}")
except Exception as e:
    print(f"  ⚠ Git error: {e}")

print("\n✅ News writer batch complete.")
