#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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

article1_body = """For decades, the story was told in numbers that sounded too neat to be true: Indian Americans, most of them named Patel, own roughly half the motels in the United States. The figure has been repeated so often it has become a kind of folk fact, the sort of thing that turns up in stand-up sets and trivia nights. What it has rarely had is a permanent home — a place where the people behind the figure are named, their ledgers and registration cards preserved, their long nights at the front desk treated as history rather than punchline.

That is about to change in San Francisco, where the Tenderloin Museum is building the first permanent exhibition in the country dedicated to the Indian American hoteliers who reshaped the lodging industry. The institution broke ground this summer on a capital expansion that will connect its current building to the space next door — once home to Newman's Gym, where Muhammad Ali trained, and the former ballroom of the Cadillac Hotel — and the Indo-American Hotelier History Exhibit will occupy part of that new footprint.

## A ledger of arrival

The exhibition takes much of its narrative from Mahendra K. Doshi's book *Surat to San Francisco: How the Patels from Gujarat Established the Hotel Business in California 1942–1960*. Doshi spent eight years on the project, interviewing more than 150 people, tracing how a handful of undocumented and barely-banked immigrants went from leasing run-down single-room-occupancy hotels in the Tenderloin to operating a national network of properties.

It is a story the diaspora knows in its bones, because so many families lived a version of it. The arithmetic of the early years was brutal and simple: a cheap residential hotel could be leased with little capital, the family lived on-site, the children did the books, and the margins came from labor that never clocked out. The Tenderloin, then as now one of San Francisco's poorest districts, was where that model was first tested.

## Why a museum, and why now

The exhibit, developed with a committee of hoteliers connected to the neighborhood and backed by the Asian American Hotel Owners Association and the American Hotel & Lodging Association, will trace the shift from SRO management to nationwide ownership through first-person accounts, artifacts and historical records. AAHOA, whose members today own a large share of American hotels, has framed the project in plainly celebratory terms — a chance, as its committee put it, to honor "the pioneers and foundational figures of Indian American hotel history."

But the timing matters in a way the press releases understate. The generation that arrived in the 1940s through the 1970s is aging out, and with it the institutional memory of how the business was actually built — the informal lending circles, the mutual-aid networks, the practice of one family co-signing for the next. An exhibit fixes that memory before it disappears into anecdote.

## The diaspora's quiet infrastructure

For the broader Indian American community, the hotelier story has always been awkwardly positioned. It is a genuine triumph — a near-monopoly in a fragmented industry, built by people with no English and less capital — but it sits uneasily beside the more flattering diaspora narrative of doctors, engineers and Silicon Valley founders. The motel owner does not fit the model-minority brochure. He worked with his hands and his whole family, in neighborhoods the professional class drove past.

Putting that history in a museum is, in its way, a statement about which immigrant stories the community chooses to claim. The hoteliers did not arrive with credentials. They arrived with a willingness to live behind the front desk, and they turned that into one of the most durable business franchises any immigrant group has assembled in America.

## What comes next

The museum's expansion is being built in phases, and the hotelier exhibit will open as construction advances. A 2025 documentary, *Patel Motel Story*, has already begun screening alongside Doshi's lectures, suggesting an appetite well beyond the Tenderloin's foot traffic.

For visitors who know the figure but not the people, the exhibit promises the harder, more interesting thing: names, faces, and the registration cards of a generation that checked America in one guest at a time.

Sources: Asian Hospitality; Today's Hotelier; Tenderloin Museum."""

article2_body = """In the affluent suburbs north of Philadelphia, an idea that began in 1999 with a handful of families and a stubborn worry has finally taken physical form. The Bharatiya Temple in Chalfont, Pennsylvania, has inaugurated the Bharatiya Learning Center, an $8.5 million cultural and educational facility built for a single, quietly urgent purpose: to keep the next generation of Indian Americans fluent in where they came from.

The ribbon-cutting drew more than 300 people, including U.S. Congressman Brian Fitzpatrick and Montgomery County Commissioner Neil Makhija, himself a child of the same diaspora the building is meant to serve. For a community organization, the guest list was its own kind of statement — a marker of how far Indian American institutions have moved from the church-basement and rented-gymnasium phase of community life.

## The long arithmetic of belonging

Nearly three decades separate the vision from the ceremony. That gap is the real story. The center was conceived when many of its eventual donors were young parents anxious that their American-born children would lose Gujarati, Hindi, Telugu or Tamil — and with the language, the texture of the culture it carries. By the time the doors opened, some of those children had children of their own.

The $8.5 million price tag was raised the way diaspora institutions almost always raise money: slowly, locally, and through relentless social pressure converted into generosity. There was no single benefactor, no naming-rights windfall. There was a board that kept asking, a volunteer corps that kept showing up, and a community that treated the project as a collective obligation rather than a charity.

## What a building is for

The center's stated mission — preserving Indian language, heritage and values for future generations — sounds anodyne until you consider what it is actually competing against. The pull of assimilation on a third-generation child is not hostile; it is frictionless. English is the language of school, of friends, of the phone. Weekend language classes exist precisely because the default is forgetting.

Speaking at the inauguration, Fitzpatrick made the familiar argument that communities which preserve their heritage strengthen the national fabric. Makhija, whose own political rise has been read by many in the diaspora as proof of arrival, emphasized the role of spaces that keep families connected to their roots. Both were saying, in the language of public officials, what the founders have believed for 26 years: that cultural continuity does not happen by accident, and that it needs walls, classrooms and a budget.

## The model-minority paradox

There is a paradox buried in projects like this one. The Indian American community is routinely cited as the wealthiest and best-educated immigrant group in the country, a success measured almost entirely by the speed of its integration — the test scores, the medical degrees, the corner offices. Yet the same community pours millions into institutions whose explicit goal is to slow one particular kind of integration: the linguistic and cultural kind.

That tension is not a contradiction so much as a negotiation, the daily work of every diaspora family. You want your child to win in America without becoming a stranger to your own parents. A learning center is an attempt to engineer that outcome at scale — to make sure a grandchild can still speak to a grandmother, still sit through a religious ceremony and understand the words, still locate themselves on a map that includes Gujarat as well as Greater Philadelphia.

## A template for others

Chalfont's center will not be the last. Across the country, the first wave of immigrant temples and associations is reaching the stage where surplus energy and accumulated wealth turn toward permanence — toward buildings designed to outlive their founders. The Bharatiya Learning Center, three decades in the making, offers a template and a caution in equal measure: the work is generational, the money is hard, and the payoff is measured not in ribbon-cuttings but in whether a five-year-old, twenty years from now, still knows the words.

Sources: The Indian Eye; Bharatiya Temple."""

article3_body = """At the New South Wales Premier's Harmony Dinner in Sydney this month, a Melbourne-founded newspaper that has spent more than three decades chronicling the lives of Indian Australians walked away with the Best Multicultural Publication award. For Indian Link, it was the fifth time winning that particular prize and the 33rd award the masthead has collected since the honours were first handed out in 2012 — a tally that says as much about the community it covers as about the paper itself.

The recognition arrives at a pointed moment. Australia's Indian-origin population has become one of the country's largest and fastest-growing migrant communities, and also one of its most contested — the subject of inflated migration statistics, anti-immigration rallies, and online claims that have required formal fact-checking. Against that backdrop, a community paper that has outlasted most of its rivals is doing something more than publishing event listings.

## The long game of community media

Indian Link was founded by Pawan and Rajni Luthra, who have run it through the entire arc of the modern Indian Australian story — from a community small enough to fit in a single hall to one whose festivals fill stadiums and whose voters politicians court. Community-language and community-focused mastheads tend to have short, underfunded lives. Surviving 33 years, and remaining good enough to keep winning a state's top multicultural media honour, is its own quiet achievement in an industry where even national newspapers are shedding staff.

What such outlets provide is hard to replicate. Mainstream Australian media covers the Indian community in spikes — during a cricket series, an election, or a controversy. A dedicated masthead covers the texture in between: the association galas, the temple openings, the small-business profiles, the obituaries that tell a newcomer who the community's elders were. That continuity is what builds the archive of a diaspora.

## Why the award matters now

The win lands amid a season of friction. Earlier this year, organisers of anti-immigration marches circulated flyers claiming more migrants had arrived from India in five years than from Italy and Greece combined over a century — a claim that fact-checkers found false, but which spread widely before it was corrected. A British MP's remarks about "Indians and Pakistanis taking jobs" rippled across the same social networks Australian Indians inhabit.

In that environment, a state premier's dinner publicly honouring an Indian Australian publication is not merely a media-industry footnote. It is an official counter-signal — a government acknowledgment that the community's storytellers belong in the room, at a time when louder voices are arguing the opposite about the community itself.

## Storytelling as belonging

The Luthras have described their work in terms that go beyond circulation: amplifying diverse voices, building a platform that connects and empowers the Indian Australian community "and beyond." It is the kind of mission statement that sounds soft until you set it against the alternative — a community whose story is told only by outsiders, in moments of conflict, through statistics it did not choose.

Victoria is home to the largest Indian community in Australia, and the state's leaders have increasingly treated the diaspora as both an economic bridge to India and a domestic constituency worth cultivating. Two-way trade, international education, cricket and cinema all bind the two countries. But trade figures do not make a community feel seen. A newspaper that has shown up, week after week, for 33 years does.

## The wider lesson

For Indian diaspora communities everywhere — in Britain, Canada, the Gulf, the United States — the Indian Link milestone is a reminder that institutional permanence is built slowly and defended constantly. Temples and associations get the ribbon-cuttings; the media that records them rarely gets the credit. An award like this one, in a year like this one, is a small correction — proof that the people who keep the community's record are part of the community's success, not a footnote to it.

Sources: Indian Link / NSW Premier's Harmony Dinner; AAP FactCheck."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Half of America's Motels Have an Indian Owner. San Francisco Is Building Them a Museum.",
        "subheadline": "The Tenderloin Museum's permanent Indo-American Hotelier exhibit fixes a diaspora folk fact into history — names, ledgers and all — before the founding generation fades.",
        "slug": make_slug("tenderloin-museum-indo-american-hotelier-exhibit-patel-motel-san-francisco"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Patel-motel story is one of the diaspora's most successful but least celebrated immigrant business sagas — a museum claims it as heritage worth preserving rather than a punchline.",
        "tags": ["nri", "diaspora", "san-francisco", "hoteliers", "patel", "history", "aahoa"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Asian Hospitality", "url": "https://www.asianhospitality.com/indo-american-hotelier-exhibit-san-francisco/"},
            {"name": "Today's Hotelier", "url": "https://todayshotelier.com/2025/08/a-legacy-of-hard-work/"},
            {"name": "Tenderloin Museum", "url": "https://www.tenderloinmuseum.org/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/26776776/pexels-photo-26776776.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A vintage American roadside motel sign, the kind of property Gujarati immigrant families built into a nationwide hospitality network.",
        "image_attribution": "Pexels",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Twenty-Six Years and $8.5 Million Later, a Pennsylvania Temple Opens a School to Outrun Forgetting",
        "subheadline": "The Bharatiya Learning Center in Chalfont is the diaspora's bet that cultural continuity needs walls, classrooms and a budget — not just good intentions.",
        "slug": make_slug("bharatiya-learning-center-chalfont-pennsylvania-indian-american-heritage"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Every immigrant family negotiates the same bargain: let the kids win in America without becoming strangers to their grandparents. This $8.5M center is that bargain built in brick.",
        "tags": ["nri", "diaspora", "pennsylvania", "heritage", "language", "temple", "community"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/05/bharatiya-learning-center-opens-in-pennsylvania-marking-major-milestone-for-indian-american-community/"},
            {"name": "Bharatiya Temple", "url": "https://www.bharatiyatemple.org/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5905929/pexels-photo-5905929.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Schoolchildren at work in a classroom — the kind of weekend language and heritage instruction the new center is built to house.",
        "image_attribution": "Pexels",
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A 33-Year-Old Indian Newspaper Just Won Australia's Top Multicultural Prize. The Timing Wasn't an Accident.",
        "subheadline": "Indian Link's fifth Best Multicultural Publication win lands in a year of inflated migration claims and anti-immigration marches — an official counter-signal to louder voices.",
        "slug": make_slug("indian-link-australia-best-multicultural-publication-award-diaspora-media"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "When mainstream media covers a diaspora only in moments of conflict, the community's own storytellers become its memory — and its defense. This award honors 33 years of that work.",
        "tags": ["nri", "diaspora", "australia", "media", "indian-link", "community"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Indian Link / NSW Premier's Harmony Dinner 2026", "url": "https://www.youtube.com/watch?v=1FipqYllxHs"},
            {"name": "AAP FactCheck", "url": "https://www.aapnews.aap.com.au/"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36376224/pexels-photo-36376224.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Freshly printed newspapers come off a press — community-language media remains a diaspora's most durable record of itself.",
        "image_attribution": "Pexels",
        "body": article3_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}  ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
