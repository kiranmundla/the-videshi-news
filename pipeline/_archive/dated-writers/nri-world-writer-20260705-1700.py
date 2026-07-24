#!/usr/bin/env python3
"""NRI World writer — July 5, 2026 17:00 PT run.

Two articles:
1. Melbourne Meets Modi community reception at Marvel Stadium — 26,000 registrations,
   death threat, community excitement and concerns, safety backdrop.
2. Melbourne's $1.2M Little India precinct in Docklands — Australia's first officially
   recognised Indian cultural zone, the debate around it, and the bigger Dandenong development.
"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# ── env ──────────────────────────────────────────────────────────────────────
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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ── articles ─────────────────────────────────────────────────────────────────

articles = [
    # ── ARTICLE 1: Melbourne Meets Modi ──────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Twenty-Six Thousand Indian Australians Signed Up for a Stadium Reception. Then Came the Death Threat.",
        "subheadline": "The 'Melbourne Meets Modi' reception at Marvel Stadium on July 9 has become the largest Indian diaspora gathering ever planned in Australia — and one of the most contested.",
        "slug": make_slug("melbourne-meets-modi-marvel-stadium-death-threat-indian-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Australia's million-strong Indian-born community navigates competing emotions — rockstar excitement and rising hostility — as it prepares to host Modi in a country still debating how much room to make for its largest overseas-born population.",
        "tags": ["nri", "diaspora", "australia", "modi", "community", "safety"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Indian Link / Europe Says", "url": "https://www.europesays.com/australia/43299/"},
            {"name": "Frame and Share", "url": "https://frameandshare.com/"},
            {"name": "Unmute Australia", "url": "https://unmuteaustralia.com.au/"},
            {"name": "WebfitNews", "url": "https://webfitnews.com/"},
            {"name": "Bhaskar English", "url": "https://bhaskarenglish.in/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/asia-pacific/indias-modi-visit-indonesia-australia-new-zealand-next-week-2026-07-04/"},
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Marvel_Stadium_during_curtain_raiser.jpg/1280px-Marvel_Stadium_during_curtain_raiser.jpg",
        "image_caption": "Marvel Stadium in Melbourne's Docklands, where up to 26,000 Indian Australians are expected on July 9",
        "image_attribution": "Wikimedia Commons",
        "body": """When the Australia India Foundation opened registrations for a community reception honouring Prime Minister Narendra Modi at Melbourne's Marvel Stadium on July 9, they expected strong interest. What they got was a stampede.

Nearly 26,000 people registered through the portal — already surpassing attendance at Modi's 2023 reception at Sydney's Qudos Bank Arena. The system caps each application at five people, with entry contingent on approval from a recognised Welcome Partner organisation. Tickets have become so coveted that comparisons to FIFA World Cup passes are routine.

"Even my wife couldn't get the chance," Yashpal Vasudeva, 79, from Doncaster East told Indian Link. "She was upset like anything, saying 'what a mistake you've done, how could you miss me!'"

Then, on July 4, the mood shifted. Australian authorities disclosed that a threatening comment had appeared under the event's Facebook post from an account named "Abu Mustafa," reading: "The rooftops of the stadium better close during the event or he will be coming to Australia for his death."

The Australian Federal Police launched an investigation, tracing the IP address and assessing whether a criminal offence was committed. India's Ministry of External Affairs responded with characteristic restraint. Secretary Rudrendra Tandon called terrorism "a crime against humanity" and said India raises the issue "at both bilateral and multilateral levels."

## A community between celebration and caution

For Australia's roughly one million Indian-born residents — now the country's largest overseas-born population — the Melbourne reception carries weight well beyond a diplomatic photo-op. Modi skipped Melbourne during his 2023 visit, a slight the Victorian diaspora has not forgotten.

"We were disappointed when he went to Sydney; many people travelled from Melbourne, but I was not fortunate enough to," says Ranganathan Padmanabhan, 70, of Oakleigh. "I think people will go ballistic once they see him here."

The enthusiasm spans generations. Anup Deshmukh, 42, is driving from Adelaide with 30 performers from his Dhol Tasha group, hauling instruments in a rented truck. Hiren Chauhan, 25, from Fraser Rise, plans to wear his India cricket jersey. A charter flight from Sydney is already taking expressions of interest.

But not everyone is boarding the train. Raman Ahuja, 51, from Prahran, said he was excited when Modi became PM in 2014 but has since grown disillusioned. "Over the years, I have seen how his government has controlled media and awarded contracts to their friends," he told Indian Link. "My Thursday evening will be at home with my family rather than to hear tall tales."

## Racism as backdrop

The death threat arrives against a pattern of escalating hostility toward Indians in Australia. Hindu temples have been vandalised with Khalistani graffiti. The Indian consulate in Melbourne was defaced earlier this year. In New Zealand — where Modi visits on July 10, the first Indian PM to do so in 40 years — racist graffiti targeting Indians recently appeared outside a school in Auckland's Papatoetoe neighbourhood.

Community members say the visit is a chance for Modi to acknowledge what many feel has been left unsaid.

"Although it doesn't seem big, I think racism's something that's creeping up exponentially," says Shreya Bose, 32, from Clyde. "We're facing lots of unwarranted racism right now and I really hope Modiji's visit navigates and addresses that."

Others frame the gathering in identity terms. "His visit will definitely help us establish an identity — having his support, hearing him talk about how we're doing, it'll invoke a greater sense of community between Indian Australians here," says Shivani Verma, 26, from Taylors Hill.

## What's on the community wishlist

With Victoria a key destination for international students and skilled workers, education and visa cooperation will likely feature in bilateral discussions. "We have a lot of good skilled professionals here, so I hope the agenda is about the productivity and contribution we are making to each other," says Nirali Dhruv, 43, from Viewbank.

The gates at Marvel Stadium open at 3.30 p.m. on July 9. Attendees will need digital entry passes and government-issued photo ID. Beyond the security screenings, the event will test whether the world's largest diaspora can project unity at the very moment its host country is debating how much room to make for it.""",
    },

    # ── ARTICLE 2: Little India Docklands ────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Melbourne Spent $1.2 Million to Build Australia's First 'Little India.' Not Everyone Is Celebrating.",
        "subheadline": "Backed by the city's biggest cultural budget in years, the Docklands precinct would join Chinatown and Koreatown as an officially recognised cultural hub — but not without a fight.",
        "slug": make_slug("melbourne-little-india-docklands-cultural-precinct-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For the quarter-million Indian-born Melburnians who have long lacked a geographic cultural home, the precinct signals institutional acceptance — and reveals the tensions that come with it.",
        "tags": ["nri", "diaspora", "australia", "melbourne", "culture", "community"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "City of Melbourne", "url": "https://www.melbourne.vic.gov.au/"},
            {"name": "Secret Melbourne", "url": "https://secretmelbourne.com/"},
            {"name": "Beat Magazine", "url": "https://beat.com.au/"},
            {"name": "Concrete Playground", "url": "https://concreteplayground.com/"},
            {"name": "The Urban Developer", "url": "https://theurbandeveloper.com/"},
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/42_Docklands_city_skyline_in_Melbourne%2C_Australia_-_free_photo_with_attribution.jpg/1280px-42_Docklands_city_skyline_in_Melbourne%2C_Australia_-_free_photo_with_attribution.jpg",
        "image_caption": "Melbourne's Docklands waterfront, the planned site of Australia's first officially recognised Little India precinct",
        "image_attribution": "Wikimedia Commons",
        "body": """When the City of Melbourne announced $1.2 million in funding for a dedicated Little India precinct in Docklands, the move looked like a straightforward win for a community that had been asking for one since 2019. The reality has proved messier.

The proposal, adopted as part of the city's 2026–27 budget, would make Little India the third officially recognised cultural precinct in Melbourne, joining Chinatown and Koreatown. The funding follows a $150,000 scoping study that identified Docklands — a waterfront neighbourhood long criticised for lacking a distinctive identity — as the natural home.

The demographic logic is hard to dispute. Greater Melbourne is home to Australia's largest Indian diaspora, with an Indian-born population approaching 250,000. Census data shows roughly 15 per cent of Docklands residents were born in India. The area already hosts the country's biggest Indian cultural events: in October 2024, Melbourne's largest-ever Diwali celebration drew more than 20,000 people to Marvel Stadium's Town Square precinct.

"Docklands feels like the natural home for something like Little India," says Sunny Pathak, director of Holi Festival Melbourne, whose annual celebration transforms the waterfront into a sea of colour and music. "It already has a strong Indian community, Indian businesses and major cultural events like Holi, so the foundations are already there."

## The blueprint

Early proposals include outdoor dining facilities, public art installations, recreation spaces and family-friendly attractions. Fifteen community organisations and associations have been consulted, and the city has created a new $250,000 multicultural events stream to support cultural programming across the municipality.

Councillor Philip Le Liu, who oversees Melbourne's creative and arts portfolio, has framed the investment in civic-branding terms. "We're taking big steps to make Little India a reality," he said. "This investment is about cementing Melbourne's reputation as Australia's cultural capital."

Lord Mayor Nicholas Reece has gone further, publicly hoping that Prime Minister Modi — due in Melbourne on July 9 for a bilateral summit and community reception — will attend the precinct's official opening once it is ready. "In some ways, I'm surprised that it's taken Melbourne this long to come up with a Little India idea," Reece told SBS Hindi.

## The pushback

The announcement prompted online debate — some sharply hostile — questioning the idea of formally recognising Indian culture in Melbourne's urban landscape. Reece responded directly: "Diversity is Melbourne's strength, and racism has no place here."

Others have raised subtler objections. Writing in Medium, analyst Anagh Baijal asked whether the precinct represented "cultural acceptance or strategic marketing" — whether genuine cultural uplift or a carefully packaged branding exercise was the actual goal.

Pathak, who has spent years watching sceptics become converts at the Holi Festival, is unfazed. "Online, people can say anything. But in real life, I've seen what happens when people come to our festival for the first time. They realise the stereotypes just don't match reality."

## Bigger money 38 kilometres south

The Docklands precinct is not the only Little India taking shape. In Dandenong, the suburb described as the "spiritual heart of Indian and subcontinent culture since 1990," Capital Alliance has been greenlit for a $300 million three-tower development at 139–157 Thomas Street. The project, designed by WMK Architecture, includes 325 residential units and more than 10,000 square metres of retail and food-and-drink space facing the existing Little India cultural zone.

Capital Alliance founder Mohan Du called the initiative "a significant long-term transformation," noting "it's encouraging to see continued momentum across the precinct." The development, which includes 10 per cent affordable housing and a childcare centre, aims to activate street frontages toward the speciality shops and restaurants that have defined the area for three decades.

## The bigger question

Together, the two projects — one civic, one commercial — signal that Melbourne's Indian community has crossed a demographic threshold where diaspora nostalgia becomes economic infrastructure. Whether the city's broader population views that as cultural enrichment or encroachment will depend, in part, on whether the foot traffic follows.

For now, the precinct remains in the consultation phase. But on July 9, when tens of thousands pack Marvel Stadium to welcome Modi, the Docklands waterfront will provide the backdrop — an apt setting for a community that is simultaneously building its future and negotiating its place.""",
    },
]


# ── insert ───────────────────────────────────────────────────────────────────
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
