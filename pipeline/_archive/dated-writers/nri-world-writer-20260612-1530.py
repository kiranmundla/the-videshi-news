#!/usr/bin/env python3
"""NRI World writer — 2026-06-12 batch (2 articles)"""

import json, os, uuid, requests
from datetime import datetime, timezone

# ---------- Supabase config ----------
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
TABLE_URL = f"{SUPABASE_URL}/rest/v1/p2_articles"

# ---------- Articles ----------
articles = [
    # ── Article 1: Belfast Riots — Indian Food Relief ──
    {
        "id": str(uuid.uuid4()),
        "headline": "'Let Me Cook and Feed People': An Indian Woman's Response to Belfast's Anti-Immigrant Violence",
        "subheadline": "As masked mobs torched homes in Northern Ireland, Ruchira Rangaprasad rallied 30 strangers to deliver food to terrified families",
        "slug": "belfast-riots-indian-food-relief-20260612",
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian immigrant in Northern Ireland leads grassroots food relief amid anti-immigrant riots, symbolising cross-community solidarity within the diaspora",
        "tags": ["belfast", "northern-ireland", "anti-immigrant-violence", "community-response", "diaspora-solidarity", "uk"],
        "urgency": "high",
        "sources": ["Reuters", "Wikipedia"],
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "image_url": "https://images.pexels.com/photos/34612590/pexels-photo-34612590.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Volunteers distributing packaged food at a community relief drive",
        "image_attribution": "Photo by Caleb Oquendo / Pexels",
        "body": """When masked groups began rampaging through the streets of Belfast on the night of June 9, setting fire to homes and vehicles and targeting anyone believed to be an immigrant, Ruchira Rangaprasad knew she had to do something. Not run. Not hide. Cook.

Rangaprasad, who moved to Northern Ireland from India three years ago, turned to social media with a simple offer: she would prepare home-cooked meals for families too frightened to leave their homes. Within hours, more than 30 volunteers — most of them complete strangers — had stepped forward to help her distribute dozens of food boxes across Belfast's besieged neighbourhoods.

"People are scared to step out of their home, and food is like a basic need, and especially like nutritious home-cooked food," Rangaprasad told Reuters. "So that's why I thought, let me cook and help feed people."

## A City Under Siege

The violence erupted after a knife attack on June 9 for which a Sudanese man was charged with attempted murder. By nightfall, masked mobs had descended on parts of Belfast, torching cars, smashing windows, and targeting the homes and businesses of ethnic minorities. Smaller outbreaks of unrest continued into Wednesday, with fears that the situation could escalate further.

At least 30 families were evacuated from their homes over two nights. Workers from the public sector union Unison reported being stopped by vigilante patrols near hospitals, where groups checked the ethnicity of passersby and recorded car registration numbers. In one harrowing incident, a nurse was chased by four masked men inside a major hospital in east Belfast.

"This is hatred that is putting lives at risk," said Patricia McKeown, regional secretary for Unison.

Britain's minister for Northern Ireland condemned the attacks as "racist thuggery." Police deployed water cannon and fired plastic bullets in an effort to restore order. Northern Ireland, where 97 per cent of the population is white according to the 2021 census, has seen sectarian tensions increasingly give way to hostility toward ethnic minorities in recent years.

## Diaspora Caught in the Crossfire

For Belfast's immigrant communities — many of whom fled conflict in their home countries — the violence was grimly familiar.

"Women and kids are terrified and in shock," said Twasul Mohammed, who came to Northern Ireland from Sudan as a refugee in 2016. "We are keeping our kids at home. I haven't sent my kids to school since this has happened."

Mohammed pushed back against the scapegoating: "Immigrants are not the problem. We are not causing the housing crisis or the health service. Every one of us wants to be a part of this community and help build it."

The Indian community in Northern Ireland, while small, has grown steadily through healthcare workers, IT professionals, and students drawn to the region's universities. Rangaprasad's spontaneous food relief has become a symbol of cross-community solidarity — proof that decency can surface even in the ugliest moments.

## 'Belfast Is Full of Decent People'

Kashif Akram, a member of the executive committee at the Belfast Islamic Centre and a lifelong Northern Ireland resident, offered a more hopeful reading.

"It's heartbreaking. At the same time Belfast is full of a lot of decent people," Akram, 44, told Reuters. "The people who are spreading the hate at the moment, they are a minority, there are very few."

For the Indian diaspora in Britain and Ireland, the events in Belfast carry a sharp reminder: the rise of anti-immigrant sentiment is not an abstract political debate. It shows up at your door at night, with masks and matches. But so, it turns out, do strangers with food boxes.

Community organisations across the UK have begun coordinating support for displaced families in Belfast. For Indians abroad watching the situation unfold, Rangaprasad's kitchen may be small — but the message it sends is anything but.""",
    },

    # ── Article 2: EB-2 India Visa Retrogression ──
    {
        "id": str(uuid.uuid4()),
        "headline": "The Wait Gets Longer: EB-2 India Retrogression Rattles Thousands of NRI Professionals",
        "subheadline": "The June 2026 Visa Bulletin pushed back priority dates for Indian applicants, adding fresh uncertainty to careers, mortgages, and family plans",
        "slug": "eb2-india-retrogression-june-2026-20260612",
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Green card backlog directly impacts NRI professionals' career mobility, home ownership, and long-term family planning in America",
        "tags": ["eb-2", "visa-bulletin", "green-card", "nri-professionals", "immigration-backlog", "united-states"],
        "urgency": "medium",
        "sources": ["India West", "U.S. Department of State"],
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "image_url": "https://images.pexels.com/photos/1181302/pexels-photo-1181302.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Indian-born professionals across America face renewed uncertainty after the June 2026 Visa Bulletin",
        "image_attribution": "Photo by Christina Morillo / Pexels",
        "body": """For thousands of Indian-born professionals in the United States, the June 2026 Visa Bulletin delivered a gut punch. The U.S. Department of State announced that the EB-2 India Final Action Date has moved backward — a process known as retrogression — extending an already punishing wait for permanent residency.

The EB-2 category covers professionals with advanced degrees or exceptional ability, a classification that captures a vast swathe of the Indian diaspora in America: software engineers at Silicon Valley firms, hospital physicians in the Midwest, research scientists at East Coast universities. For many, the green card is not merely a document but the foundation on which career changes, home purchases, and long-term family plans are built.

## What Retrogression Means in Practice

Retrogression occurs when the demand for immigrant visas in a given category exceeds the annual supply. The U.S. allocates a fixed number of employment-based green cards each year, and no single country can claim more than seven per cent of the total — a cap that disproportionately penalises applicants from high-demand countries like India and China.

When the State Department determines that too many applications have been filed relative to available visa numbers, it moves the priority date cutoff backward. In practical terms, this means that applicants who were approaching the front of the queue suddenly find themselves pushed further back, their timelines stretched by months or years.

For Indian EB-2 applicants, the backlog is already staggering. Wait times can stretch well beyond a decade, during which applicants are typically tied to a single employer and unable to start businesses, accept promotions at rival firms, or move freely between jobs without jeopardising their visa status.

## The NRI Life on Hold

The impact extends far beyond immigration paperwork. Indian professionals caught in the EB-2 backlog describe a peculiar kind of limbo — earning six-figure salaries in one of the world's richest countries while being unable to make the most basic life decisions with any certainty.

Can you buy a house if you might have to leave the country? Should you enrol your children in local schools or keep a return-to-India option open? Can you accept that promotion if it requires switching employers and restarting the green card process?

These are the daily calculations of what immigration attorneys call "high-skilled uncertainty" — a condition that affects hundreds of thousands of Indian-born workers and their families across America.

## A Community Watching Closely

The retrogression has reignited debate within Indian-American community organisations. Groups like Immigration Voice have long lobbied Congress for reforms to the per-country cap, arguing that it punishes applicants for their nationality rather than their qualifications.

Legislative proposals to eliminate per-country limits for employment-based green cards have repeatedly stalled on Capitol Hill. Without legislative relief, the EB-2 India backlog is projected to grow, with some estimates suggesting that new applicants could face wait times exceeding 30 years.

## What Comes Next

Immigration experts stress that retrogression does not mean existing applications have been denied. Applicants with pending cases can continue to maintain their status and monitor future Visa Bulletin updates for potential forward movement.

Industry analysts believe the start of the next U.S. fiscal year in October could bring renewed visa availability and some advancement in priority dates. But future progress will depend on overall visa demand, processing volumes, and annual allocations determined by the State Department.

For now, immigration attorneys are advising applicants to keep documentation scrupulously updated, avoid unnecessary employer changes, and track the monthly Visa Bulletin closely.

The broader pattern is unmistakable. Year after year, the world's largest democracy sends its most skilled workers to the world's largest economy, where they pay taxes, build companies, and raise American-born children — while waiting a decade or more for the right to stay. The June 2026 bulletin is another chapter in a story that shows no sign of ending.""",
    },
]

# ---------- Insert ----------
inserted = []
for art in articles:
    # Supabase expects native arrays, not JSON strings
    payload = dict(art)

    resp = requests.post(TABLE_URL, headers=HEADERS, json=payload)
    if resp.status_code in (200, 201):
        row = resp.json()
        if isinstance(row, list):
            row = row[0]
        inserted.append({"id": row["id"], "slug": row["slug"], "headline": row["headline"]})
        print(f"✅  Inserted: {row['slug']}")
    else:
        print(f"❌  FAILED ({resp.status_code}): {art['slug']}")
        print(f"    {resp.text[:500]}")

print(f"\n{'='*60}")
print(f"Total inserted: {len(inserted)} / {len(articles)}")
for r in inserted:
    print(f"  • {r['slug']}")
