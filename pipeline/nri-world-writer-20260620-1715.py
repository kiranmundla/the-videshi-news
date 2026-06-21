#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

env_file = Path.home() / ".env.supabase"
if not env_file.exists():
    env_file = Path.home() / "workspace" / ".env.supabase"
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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Nine Women, Three Cities, One Dance: How Brazil's Indian Diaspora Choreographed a Welcome for Modi",
        "subheadline": "The performers had jobs, small children and full lives. They rehearsed over Zoom across São Paulo, Campinas and Rio to put Operation Sindoor on a Rio stage.",
        "slug": make_slug("brazil-indian-diaspora-women-modi-welcome-operation-sindoor-dance"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Far from the headline diplomacy of a BRICS summit, the labour of diaspora community life is usually invisible — the WhatsApp groups, the weekend rehearsals, the borrowed venues. This is what it actually looks like when a scattered community decides to show up.",
        "tags": ["nri", "diaspora", "brazil", "modi", "community", "culture"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/how-indian-diaspora-welcomed-pm-modi-in-brazil/"},
            {"name": "Mint", "url": "https://www.livemint.com/news/india/pm-modi-gets-grand-welcome-in-brazil-indian-diaspora-perform-dance-on-theme-of-operation-sindoor-watch"},
            {"name": "LatestLY (ANI)", "url": "https://www.latestly.com/agency-news/world-news-brazil-indian-diaspora-expresses-delight-over-pm-modis-visit"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8566097/pexels-photo-8566097.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Women in traditional dress perform a cultural dance, the kind staged by diaspora community groups at official receptions.",
        "image_attribution": "Pexels",
        "body": """When Narendra Modi stepped off his plane in Rio de Janeiro, the welcome that moved him most was not arranged by a protocol office. It was put together by nine women who had never all been in the same room.

Set to the patriotic numbers *Tujhe Namami Ho* and *Saugandh Mujhe Is Mitti Ki*, the performance pulled dancers from three Brazilian cities — São Paulo, Campinas and Rio — onto one stage. The youngest performer, ten-year-old Jayesh Karahe, played Modi himself in the closing tableau. According to organisers, the prime minister could not stop clapping. "He smiled and said, 'Excellent performance!'" recalled Gyaneshree Karahe, who helped coordinate the troupe. "That one moment was worth everything."

## The unglamorous work of showing up

What the cameras captured in a few minutes took weeks to assemble, and the logistics say more about diaspora life than the spectacle does. The performers — Abha Joshi, Shilpa Pinaki, Vaijanti Raut and Gyaneshree from São Paulo; Jalak Modi and Raksha Bagaria from Campinas; Sneha Prateek, Puja Shah and Rajani Sinha from Rio — rehearsed almost entirely over video calls.

"We rehearsed through Zoom calls, video tutorials, and coordinated our moves and efforts across cities," Gyaneshree said. "These are women with jobs, small children, and daily responsibilities — but they came together because they believed in the cause."

That is the part of the diaspora story that rarely makes it into the official photo essays. A community of a few thousand, spread across a country larger than the continental United States, does not have the density of a Jackson Heights or a Southall. Pulling off a coordinated cultural performance means borrowing rehearsal space, splitting choreography across time zones within the same country, and leaning on the institutions that hold scattered communities together — in this case the Indian embassy, the consulate, the Swami Vivekananda Cultural Centre and the local Indian Association.

## A theme with an edge

The choice of material was pointed. One sequence was built around Operation Sindoor, the Indian military action earlier launched in response to a terror attack, with the line *ye desh nahi mitne dunga* — "I will not let this nation be erased" — echoing through the venue. The organisers framed it deliberately as women honouring an operation publicly associated with India's women.

"Operation Sindoor, led by Indian women, was now being paid tribute to by Indian women in Brazil," Gyaneshree said. "It was a message of empowerment, strength, and gratitude — from us, to our nation."

For a diaspora that often expresses itself through the safe vocabulary of food festivals and Diwali melas, a performance with explicit political content is a different kind of statement — an assertion that distance does not dilute opinion.

## Why Brazil matters more than its numbers

India's community in Brazil is small, and easy to overlook in a diaspora conversation dominated by the Gulf, North America and Britain. But the BRICS architecture has quietly raised its profile. Every Indian leader's visit to a BRICS capital now comes with a diaspora reception, and those receptions have become a way for tiny communities to punch above their demographic weight — to be seen by New Delhi, and to remind their adopted home that they exist as a constituency.

The Indian Council for Cultural Relations runs programmes in Brazil ranging from yoga and Odissi classes to a project it calls "India in your library." The dance in Rio was the visible tip of that slow, unglamorous institution-building.

## What's next

The performers have gone back to their jobs and their children. The embassy will file its report, the photographs will circulate on community WhatsApp groups, and the next reception — whenever the next dignitary passes through — will be organised by some of the same people. That is the rhythm of a small diaspora: long stretches of ordinary life, punctuated by bursts of collective effort that briefly make a few thousand people feel like a community of one.

What lingers is less the spectacle than the method. A performance stitched together over Zoom by working mothers in three cities is, in its own way, a more honest portrait of the diaspora than any official welcome — proof that belonging abroad is something you have to keep choosing to build."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "On the Longest Day, Britain's Indian Diaspora Rolls Out Its Mats — and Its Soft Power",
        "subheadline": "From Victoria Square in Birmingham to Slough's Langley Academy, International Day of Yoga has become the diaspora's most reliable public ritual. The crowds keep growing.",
        "slug": make_slug("international-day-of-yoga-2026-uk-indian-diaspora-soft-power"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Yoga Day is one of the few occasions when the Indian diaspora invites the wider public into its cultural space rather than performing for itself — a rare, repeatable act of integration that doubles as a quiet flex of India's global brand.",
        "tags": ["nri", "diaspora", "uk", "yoga", "culture", "soft-power"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Eventbrite — IDY 2026 Birmingham (Consulate General of India)", "url": "https://www.eventbrite.com/e/international-day-of-yoga-2026-tickets"},
            {"name": "Eventbrite — IDUK Yoga Day 2026", "url": "https://www.eventbrite.co.uk/e/iduks-international-day-of-yoga-2026-tickets"},
            {"name": "Suryaa / IANS", "url": "https://www.suryaa.com/world/privileged-to-be-part-of-this-celebration-indian-diaspora-in-uk-celebrates-yoga-day"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Yoga_Day_at_Victoria.jpg/1280px-Yoga_Day_at_Victoria.jpg",
        "image_caption": "A public International Day of Yoga gathering at Victoria Square, Birmingham, where the Consulate General of India hosts its annual event.",
        "image_attribution": "Wikimedia Commons",
        "body": """On Sunday, 21 June, the Consulate General of India in Birmingham will close part of Victoria Square, hand out yoga mats, and invite anyone walking past to join in. It is a scene that will repeat across Britain on the same morning — Slough, London, Oxford, Cambridge, Southampton — and it has become, almost by accident, the Indian diaspora's most dependable annual appearance in British public life.

This year's International Day of Yoga, the twelfth, carries the theme "Yoga for Wellness, Wisdom and World Peace." The Birmingham programme alone ran a month of lead-up sessions — Ayurveda demonstrations, "saree yoga," a children's "picnic yoga," and a mental-health session co-hosted with the Isha Foundation — before the main event in the square.

## A festival that faces outward

Most diaspora gatherings are, by design, inward-looking. A temple anniversary, a regional association's gala, a Telugu or Gujarati convention — these are spaces where the community talks to itself, conducts its business, hands out its awards. They are vital, but they rarely draw in the neighbour who has never set foot in a mandir.

Yoga Day is the exception. It is staged in town squares rather than community halls, it is free, and the whole point is to attract people who are not Indian. "We're celebrating the 11th International Day of Yoga at a free event open to everyone here in London," one participant said at last year's edition, held against the backdrop of the city's historic architecture. "It's truly a privilege to be part of this celebration."

In Slough, the group Indian Diaspora in the UK (IDUK) folds a different agenda into its Langley Academy event: alongside the Zumba and meditation, it honours local residents who have contributed to sport. The mix — wellness, recognition, networking — is telling. Yoga Day has become a container into which diaspora organisations pour whatever community-building they need to do, knowing the wider public will turn up for the headline act.

## The soft-power machine behind the mats

None of this is spontaneous. The events are organised and bankrolled by India's diplomatic missions and their cultural wings, and they are an explicit instrument of statecraft. Yoga Day exists at all because India lobbied the United Nations to create it in 2014; the annual spectacle is the payoff.

India's High Commissioner to the UK, Vikram Doraiswami, has been candid about the strategy. The aim, he said of a recent edition, was "to take yoga to as many places as possible," with events deliberately seeded in university towns — Oxford, Cambridge, Southampton — "in collaboration with many partners." The mission works through local yoga studios, community groups and universities to push the day beyond the big cities.

For the diaspora, this produces an unusual alignment of interests. The Indian state wants visibility for a wellness brand it has successfully globalised. Community organisations want a respectable, well-attended public platform. And second-generation Britons of Indian heritage get a version of their culture that their non-Indian friends already admire and want to participate in — a rare thing to be able to offer.

## The quiet ambivalence

Not everyone in the diaspora is entirely comfortable with how thoroughly the day has been absorbed into official messaging. Yoga's roots are spiritual and contested; its packaging as a frictionless, exportable wellness product can feel like a flattening. And there is an awkwardness in a community that still faces its own integration struggles being deployed, however gently, as a goodwill ambassador for a government back home.

But on a June Sunday in Victoria Square, those tensions tend to dissolve into the simple fact of a crowd. People of every background unrolling mats together is not a bad image for a diaspora to project — and unlike most of what the community organises, it is one the rest of Britain actually shows up for.

## What's next

The mats will be rolled up by lunchtime, the consulate will tally attendance, and the photographs will travel back to Delhi as evidence of reach. The harder question is whether a once-a-year ritual translates into anything more durable — sustained interest, deeper ties, new members for the studios and associations that do the year-round work. For now, the diaspora will take the win it can rely on: one morning a year when its culture is the thing everyone wants to join."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Twenty Years Ago It Was a Day in a Park. This Weekend DesiFest Took Over Downtown Toronto for Three Days.",
        "subheadline": "Canada's largest South Asian music and arts festival turns 20 — a milestone that maps how far a once-marginal community has moved toward the centre of Canadian cultural life.",
        "slug": make_slug("desifest-toronto-20th-anniversary-south-asian-festival-canada-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "A festival's survival to 20 years, and its move from a community park to a flagship downtown square, is a measurable proxy for a diaspora's arrival — from tolerated minority to a culture the mainstream programmes around.",
        "tags": ["nri", "diaspora", "canada", "toronto", "festival", "music", "culture"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "DesiFest official site", "url": "https://desifest.ca/"},
            {"name": "Eventbrite / festival listings", "url": "https://desifest.ca/"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/13230484/pexels-photo-13230484.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A crowd gathers under stage lights at an outdoor music festival, the kind of free public event DesiFest has become in Toronto.",
        "image_attribution": "Pexels",
        "body": """DesiFest began as the kind of thing that is easy to start and hard to keep alive: a single day of South Asian music in a Toronto park, run on goodwill and volunteer hours. This weekend, on its twentieth anniversary, it occupied Sankofa Square in the heart of downtown for three days — a launch night billed as "The Homecoming," a Friday of "Bollywood Remix," and a twelve-hour Saturday flagship of live music, dance and food, all free and open to the public.

The arithmetic of that journey is the real story. Most diaspora cultural projects do not make it to year five, let alone year twenty. They run out of money, volunteers burn out, founders move on, the second generation drifts. A festival that survives two decades — and graduates from a community green to a marquee city square — is not just a party. It is a data point about where a community sits in the culture around it.

## From the margins to Sankofa Square

The venue change tells you most of what you need to know. Twenty years ago, South Asian culture in Canada largely happened in places South Asians already controlled: community centres, banquet halls, gurdwara and temple grounds, suburban parks in Brampton and Mississauga where the diaspora is densest. Those spaces were safe, but they were also a kind of containment — culture practised among ourselves, on the edges of the metropolis.

Holding the twentieth-anniversary edition in a central downtown square is a different proposition. It puts Punjabi anthems, classical fusion and Bollywood remixes on a stage that the rest of Toronto walks past, and frames South Asian music not as a niche to be sought out but as part of the city's summer programming. The festival's own tagline — "Where South Asian Culture Meets the World" — is a statement of intent about that shift.

## The second generation takes the mic

The programming reveals a community comfortable in two registers at once. "Bollywood Remix" night leaned on DJs and live bands "flipping the classics and fusing South Asian sound with hip-hop, afrobeats, electronic." The Saturday flagship promised everything from Punjabi anthems to "classical fusion" and "original hits."

That blend is the sound of a diaspora's second and third generations — artists who grew up with both their parents' film music and the city's hip-hop, and who refuse to choose. It is also a commercial signal. Festivals that stay purely nostalgic tend to age with their first audience and quietly fade. DesiFest's longevity suggests it has kept recruiting younger performers and younger crowds, which is the only way these things survive.

The launch night, pitched as a reunion of "past artists, founding supporters, and the community that turned a dream into Canada's largest South Asian music festival," made the generational handoff explicit — honouring the people who started it while clearing the stage for whoever comes next.

## Canada's particular moment

The anniversary lands at a complicated time for Indians in Canada. Diplomatic relations between Ottawa and New Delhi have been strained, immigration politics have sharpened, and the community has at times felt unusually scrutinised. A large, joyful, downtown celebration of South Asian culture is, in that context, its own kind of answer — a reminder that the diaspora is woven into the fabric of Canadian cities regardless of the state of bilateral relations.

It is worth noting what DesiFest is not. It is not an embassy production or a soft-power exercise run from abroad. It grew from the community itself, which makes its endurance a more reliable indicator of roots than any government-sponsored gala.

## What's next

Twenty years in, the test for DesiFest is the same one every long-running cultural institution faces: whether it can keep feeling essential rather than ceremonial. The move downtown buys it visibility; the younger lineup buys it relevance. The harder work is staying the place where the next generation of South Asian Canadian artists wants to be seen — and where the rest of the country keeps choosing to show up. On the evidence of a three-day, city-centre twentieth birthday, it is winning that argument for now."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
