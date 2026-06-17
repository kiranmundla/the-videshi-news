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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "On June 21, the Indian Diaspora Will Roll Out Mats From Times Square to the Lincoln Memorial. It Is the Most Organized Soft Power India Owns.",
        "subheadline": "More than 210 Indian missions are staging Yoga Day at nearly 2,500 sites worldwide. The biggest crowds will not be in India — they will be in the cities where the diaspora lives.",
        "slug": make_slug("international-yoga-day-2026-diaspora-times-square-lincoln-memorial-soft-power"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Yoga Day has become the one event where Indian-American community groups, consulates and temple networks mobilize at scale every year — a recurring stress test of the diaspora's organizing muscle and a rare moment when Indian culture occupies the most public spaces in American and British cities.",
        "tags": ["nri", "diaspora", "yoga-day", "culture", "community"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye — Indian Embassy to celebrate International Day of Yoga at Lincoln Memorial", "url": "https://theindianeye.com/2026/06/16/indian-embassy-to-celebrate-international-day-of-yoga-2026-at-lincoln-memorial/"},
            {"name": "The Indian Eye — PM Modi's Yoga Guru to lead Times Square Yoga Day event", "url": "https://theindianeye.com/2026/06/16/pm-modis-yoga-guru-to-lead-times-square-yoga-day-event/"},
            {"name": "IANS — PM Modi to lead International Day of Yoga 2026 celebrations in Kolkata", "url": "https://ianslive.in/pm-modi-to-lead-international-day-of-yoga-2026-celebrations-in-kolkata"},
            {"name": "Eventbrite — IDUK International Day of Yoga 2026, Slough", "url": "https://www.eventbrite.co.uk/e/iduks-international-day-of-yoga-2026-tickets"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/NewYork_TimeSquare_Yoga_%2842561435395%29.jpg/1280px-NewYork_TimeSquare_Yoga_%2842561435395%29.jpg",
        "image_caption": "Thousands gather to practice yoga in the middle of Times Square, New York, on International Day of Yoga",
        "image_attribution": "Wikimedia Commons",
        "body": """When the United Nations adopted India's proposal for an International Day of Yoga in 2014, the cynics filed it under feel-good diplomacy. Twelve years on, the cynics have a problem: it works. On Sunday, June 21, India's foreign ministry says more than 210 of its missions abroad will run Yoga Day events at nearly 2,500 locations, in coordination with the Indian Council for Cultural Relations. Prime Minister Narendra Modi will lead the national showcase on Kolkata's Red Road. But the more revealing crowds will assemble several thousand miles away — in Washington, New York, Birmingham and Slough — and they will be organized largely by Indians who left.

## The map of the celebration is the map of the diaspora

Look at where the marquee events land. The Indian Embassy in Washington has booked the steps of the Lincoln Memorial for Friday, June 19, inviting practitioners to one of the most symbolically loaded patches of ground in American public life. In New York, the Consulate General is staging its annual session in Times Square on June 21, with Padma Shri Dr. H. R. Nagendra — the yoga scholar who guides Modi's own practice and heads Bengaluru's S-VYASA University — as chief guest. Nagendra's trip is itself a piece of diaspora machinery: he was invited by the Rajasthan Association of North America, and before Times Square he will inaugurate a wellness retreat upstate at a longevity resort in Monticello, flanked by Indian-American physicians from Mount Sinai.

This is the quiet truth of Yoga Day. The Indian state supplies the brand and the gurus; the diaspora supplies the venues, the volunteers and the turnout. The Consulate General hangs the banner, but the Rajasthan Association, GOPIO, the Indian American Forum and a dozen temple committees fill the square.

## Britain shows the same pattern, in miniature

The British leg is a study in how thoroughly the day has localized. In Birmingham, the Consulate General has run a six-week "curtain raiser" series leading into June 21 — saree yoga, kids' picnic yoga, Ayurveda sessions delivered by the Isha Foundation, Brahma Kumaris, Heartfulness and Art of Living, each a diaspora organization with its own following. The Slough event, staged by a group calling itself simply Indian Diaspora in the UK, bolts a sports-achievement awards ceremony onto the morning's stretching. None of this is centrally scripted from Delhi. It is a franchise, and the franchisees are British Indians.

## Why the diaspora carries it

For a community that spends much of the year navigating the gap between two identities, Yoga Day offers something unusually frictionless: a piece of Indian heritage that the host country actively wants. An American city that might hesitate over an overtly religious procession will happily close part of Times Square for a wellness event. A British council that debates the politics of immigration will co-sponsor a sunrise session in a public square. Yoga is the part of the cultural inheritance that travels without an asterisk, and the diaspora has learned to use it as a door.

That utility cuts both ways. This year's theme — "Yoga for Healthy Ageing" — is aimed at an Indian population worldwide that is itself greying, including first-generation migrants who arrived in the 1970s and 1980s and are now in their seventies. The senior-citizen associations that co-host these events, like the Federation of Indian Senior Associations of North America, are not incidental partners. For many older NRIs, the Yoga Day gathering is also the social calendar.

## The soft power nobody else has to fund

India spends a fraction of what China pours into Confucius Institutes, yet on a single Sunday it can put Indian culture into 2,500 public spaces across more than 200 missions, with most of the labor donated by emigrants. A nationwide live session in India on June 14 drew more than four lakh simultaneous participants and a Guinness record; the global footprint is harder to count but plainly larger. The genius of the model is that it does not depend on the Indian treasury. It depends on the diaspora's appetite to be seen — favorably, on its own terms — in the countries it now calls home.

On June 21, that appetite will once again be visible from the steps of the Lincoln Memorial. It is worth watching not as a wellness story but as the most reliable demonstration of organizing capacity the Indian diaspora stages all year."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Films Are Now Beating Australian Films at Australia's Own Box Office. A National Festival Is Trying to Turn That Into Permanence.",
        "subheadline": "NIFFA 2026 has grown to 32 films, 18 languages and 14 cities — including outback towns like Alice Springs and Broken Hill. The expansion tracks the fastest-growing migrant community in the country.",
        "slug": make_slug("niffa-australia-2026-indian-cinema-diaspora-box-office-regional-expansion"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indians are now the largest source of new migrants to Australia and Punjabi is its fastest-growing language. A film festival that started as a single-city event and now reaches outback towns is a measure of how quickly that community has put down roots — and how Indian cinema is moving from diaspora comfort viewing to Australian mainstream.",
        "tags": ["nri", "diaspora", "australia", "cinema", "culture"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Cinema Express — Boong opens National Indian Film Festival of Australia", "url": "https://www.cinemaexpress.com/entertainment/hindi/2026/Mar/18/boong-opens-national-indian-film-festival-of-australia"},
            {"name": "Variety / IMDb — Australia's National Indian Film Festival Expands to Regional Markets", "url": "https://www.imdb.com/news/australia-national-indian-film-festival-expands-regional-markets"},
            {"name": "Wikipedia — National Indian Film Festival of Australia", "url": "https://en.wikipedia.org/wiki/National_Indian_Film_Festival_of_Australia"},
            {"name": "City of Darwin — NIFFA 2026 Darwin Edition", "url": "https://www.darwin.nt.gov.au/community/events/niffa-2026-darwin-edition"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/0e/Anupam_Kher_at_56th_IFFI.jpg",
        "image_caption": "Actor Anupam Kher, who received NIFFA 2026's International Indian Cinema Icon Award, at a film festival appearance",
        "image_attribution": "Wikimedia Commons",
        "body": """There is a statistic that ought to unsettle Australia's film establishment and delight its newest citizens in equal measure: Indian films are currently outperforming Australian films at the Australian box office. That is the backdrop against which the National Indian Film Festival of Australia, now in its second year, has gone from a single-city novelty to a sprawling national event running from March 18 through July 5, 2026, across 14 cities in 18 languages.

## From seven cities to the outback

The leap in scale is the story. NIFFA's debut in 2025 covered seven metropolitan cities — Sydney, Melbourne, Brisbane, Perth, Adelaide, Canberra and Darwin. The 2026 edition keeps those and adds a string of regional and remote centres: Alice Springs, Broken Hill, Dubbo, Leeton, Griffith, Geelong, Hobart. That a festival of Indian cinema now plays Broken Hill — a mining town deep in the New South Wales outback — says less about cinephilia than about demographics. The audience has arrived there, so the films follow.

The opening title set the tone. The festival launched not with a Bollywood blockbuster but with Boong, a BAFTA-winning Manipuri-language film directed by Lakshmipriya Devi and produced by Farhan Akhtar — a deliberate signal that NIFFA wants to be read as a showcase of India's regional cinemas, not just Hindi-language exports. With over 32 films across 18 languages, the programme leans into exactly the diversity that distinguishes the modern Indian-Australian community, which is far from monolithically north-Indian.

## The community behind the screenings

Australia's Indian population is no longer a niche. Indians have become the country's largest source of new migrants, overtaking England, and Punjabi is now Australia's fastest-growing language. The Australian Bureau of Statistics recently recorded Indians edging past the England-born as the largest overseas-born group in the country. A festival is one of the clearest cultural expressions of a community that has reached that critical mass — large enough that civic institutions court it.

And court it they do. The Geelong launch was hosted by the city's mayor in partnership with the local council and a waterfront film foundation. Veteran actor Anupam Kher received the festival's International Indian Cinema Icon Award — a figure whose résumé spans Hindi cinema and Hollywood (The Big Sick, Silver Linings Playbook, Bend It Like Beckham), making him a fitting emblem for a diaspora that lives across both. His own film, Tanvi the Great, inspired by his autistic niece, anchored a new festival strand called Able + Diverse, built around disability representation.

## Cinema as the diaspora's connective tissue

For a migrant community, a film festival does work that goes well beyond entertainment. It gives second-generation children, raised on English-language media, a reason to sit through three hours of Tamil or Marathi storytelling with their parents. It gives recent arrivals a monthly anchor of familiarity. And it gives the wider Australian public a low-stakes way to encounter Indian culture as art rather than as headline — a screening at Dendy Newtown is an easier introduction than any debate about migration figures.

## Building permanence

What separates NIFFA from a one-off cultural gala is its move toward institutional permanence. The festival has signed a memorandum of understanding with India's National Film Development Corporation and the International Film Festival of India, positioning itself as a fixed platform for Indian cinema in the Southern Hemisphere. A 2023 Australia–India Co-Production Treaty already streamlines collaboration, and organizers point to more than AUD 75 million in India-centric screen projects in development across the two countries.

The arithmetic of that ambition is straightforward. India is the supply of stories; the diaspora is the guaranteed audience; the co-production treaty is the bridge. If Indian films keep outselling local product at Australian cinemas, NIFFA will not be remembered as a diaspora festival at all. It will simply be part of how Australia watches movies — which is, quietly, the most complete kind of arrival a migrant culture can achieve."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Twenty-Four Thousand Signed Up for a 15,000-Seat Arena. The Real Story Is the 590 Organizations That Got Them There.",
        "subheadline": "A September event on Long Island has already oversold by 60 percent. Behind the numbers sits the dense, unglamorous network of community groups that is the Indian diaspora's most underrated asset.",
        "slug": make_slug("indian-american-mega-event-590-organizations-community-network-diaspora-capacity"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The headline numbers around large diaspora gatherings obscure the real machinery: hundreds of small associations — by language, region, profession and faith — that can collectively mobilize tens of thousands of people across dozens of states. That distributed organizing capacity, not any single event, is what makes the Indian-American community politically and culturally formidable.",
        "tags": ["nri", "diaspora", "community", "indian-american", "organizing"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Asian Voice — Over 24,000 Indian-Americans sign up for community event", "url": "https://www.asian-voice.com/News/USA/Over-24000-Indian-Americans-sign-up-for-community-event"},
            {"name": "The Indian Eye — Over 24,000 Indian-Americans sign up for mega community event in NY", "url": "https://theindianeye.com/2026/06/over-24000-indian-americans-sign-up-for-mega-community-event-in-ny/"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36871083/pexels-photo-36871083.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A large crowd gathers for a vibrant Indian cultural celebration",
        "image_attribution": "Pexels",
        "body": """The number doing the rounds is 24,000 — the count of Indian-Americans who have registered for a community event on September 22 at the Nassau Veterans Memorial Coliseum on Long Island, an arena that seats roughly 15,000. An oversubscription of 60 percent before summer has even started makes for a tidy headline. But the figure that deserves attention is buried in the organizers' own statement: the registrations came through 590 community organizations, all signed up as "Welcome Partners," drawing attendees from at least 42 states.

Five hundred and ninety. That is the real story, and it is one the diaspora rarely tells about itself.

## The architecture beneath the crowd

No single body can summon 24,000 people across 42 states. What can is a federated structure — hundreds of small, autonomous associations, each with its own membership list, WhatsApp groups and Sunday gatherings, stitched loosely together for a common occasion. The Indo-American Community of USA, which is convening the September event, did not build a crowd so much as plug into an existing grid.

That grid is organized along every axis the community recognizes. There are regional and linguistic associations — Telugu, Gujarati, Tamil, Punjabi, Bengali, Malayalam, each often with chapters in a dozen metros. There are professional bodies for physicians, hoteliers, technologists and entrepreneurs. There are temple and gurdwara committees, alumni networks of Indian universities, and senior-citizen federations. The organizers were explicit that participating groups span Hindu, Sikh, Muslim, Christian, Jain and Zoroastrian communities — the full religious spread of the subcontinent, reassembled in suburban America.

## Why the density matters

Most immigrant communities have associations. Few have them at this density or with this reach. The Indian-American population is barely over one percent of the United States, yet it can field a 590-organization coalition for a single event and over-subscribe a major arena months out. That capacity is the quiet engine behind the community's outsized footprint — in philanthropy, where annual giving campaigns now raise millions in a single day across dozens of cities; in politics, where the same lists turn out for candidate fundraisers; and in culture, where they fill Yoga Day squares and film-festival theatres.

It is also self-reinforcing. Each large gathering renews the relationships among the organizers, tests their logistics, and adds names to the rolls. An event like September's is, in effect, a periodic audit of the network's strength — and a 60 percent oversell is a clean bill of health.

## The vulnerability inside the strength

A federated structure has a flip side. Because the network is built from groups defined by region, language and faith, the same density that produces turnout can also produce fragmentation. Coalitions assembled for a celebratory event do not always hold for harder, more contested questions, where regional or political differences within the diaspora surface. The 590 partners agree readily on a community showcase; they would not agree as easily on, say, a single political endorsement.

There is a generational question too. The associations that anchor this network were largely built by first-generation migrants who arrived from the 1970s onward and who treat the local Telugu or Gujarati society as a second family. Whether their American-born children — who socialize across community lines and may feel only a diffuse connection to a specific regional identity — will sustain 590 organizations into the next decades is genuinely unsettled. The senior-citizen federations now multiplying within the network are one sign of an aging founding cohort.

## The metric to watch

For now, the capacity is real and growing. The lesson of the September numbers is not that one event will be crowded. It is that the Indian diaspora in America has quietly built one of the densest civic networks of any immigrant community in the country — and that its true scale is measured not in arena seats but in the count of organizations willing to put their name and their members behind a common cause.

Twenty-four thousand is the crowd. Five hundred and ninety is the machine."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK {art['slug']}")
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")
