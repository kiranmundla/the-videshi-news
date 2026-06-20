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
        "headline": "A Doctor Born to Immigrants Is About to Spend Eight Months in Orbit. The Diaspora Has a New Kind of Hero.",
        "subheadline": "Anil Menon, son of an Indian father and a Ukrainian mother, launches next month on his first spaceflight — a quiet rebuke to anyone who thinks the immigrant story has only one script.",
        "slug": make_slug("anil-menon-nasa-astronaut-iss-mission-diaspora-first-spaceflight"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Menon's path — Harvard, Stanford, the ER, SpaceX, now the ISS — is the diaspora's familiar overachiever arc bent toward an unfamiliar destination. He represents a generation of Indian-American children no longer choosing between medicine and a dream.",
        "tags": ["nri", "diaspora", "anil-menon", "nasa", "space", "indian-american"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "NASA — Expedition 75 crew", "url": "https://www.nasa.gov/humans-in-space/"},
            {"name": "Firstpost America", "url": "https://www.youtube.com/results?search_query=anil+menon+nasa+first+space+mission"},
            {"name": "Livemint — Who is Anil Menon", "url": "https://www.livemint.com/news/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/NASA_Astronaut_Anil_Menon_%28jsc2024e013690_alt%29.jpg/1280px-NASA_Astronaut_Anil_Menon_%28jsc2024e013690_alt%29.jpg",
        "image_caption": "NASA astronaut Anil Menon in his official portrait at the Johnson Space Center",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """When Anil Menon straps into a Soyuz capsule at the Baikonur Cosmodrome next month, he will carry with him a résumé that reads like a parody of diaspora ambition. A neurobiology degree from Harvard. A medical degree and a master's in mechanical engineering from Stanford. A stint as SpaceX's first flight surgeon. A colonelcy in the U.S. Space Force. And now, a seat on Expedition 75 and roughly eight months aboard the International Space Station.

It is the kind of curriculum vitae that Indian-American parents quote to their children, usually as a threat. But Menon's story is less a tidy immigrant fable than a reminder that the script has more than one ending.

### Two immigrant homes, one trajectory

Menon was born in Minneapolis to an Indian father and a Ukrainian mother — two immigrant homes folded into one. That detail matters. The diaspora narrative is often told as a single straight line from a village in Gujarat or a suburb of Chennai to a corner office in California. Menon's background scrambles that. He is a product of two migrations, and his life suggests the second-generation experience is increasingly a braid of more than one heritage.

He trained as an emergency physician, the least glamorous and most relentless corner of medicine, before drifting toward the specialty almost nobody plans for: aerospace medicine. At SpaceX he built the company's medical operations from scratch, supporting the Demo-2 mission that returned American astronauts to orbit on an American rocket for the first time in nearly a decade. He joined NASA's astronaut corps in 2021 and graduated with its 2024 class.

### Why a flight surgeon goes to space

The mission itself is unglamorous in the way that real science usually is. Menon will serve as a flight engineer alongside Russian cosmonauts Pyotr Dubrov and Anna Kikina, conducting experiments in microgravity meant to inform NASA's longer-term plans for the Moon and Mars. There will be no flag-planting, no first-human-on-anything headline. He will spend most of his time maintaining a laboratory that happens to orbit the Earth sixteen times a day.

For the diaspora, though, the symbolism is hard to ignore. Indians abroad have grown used to celebrating their own in boardrooms and on ballots — a bank chief here, a senator there. Space is a different register. It is the one frontier where achievement cannot be attributed to networking, lobbying, or the soft advantages of a well-connected community. You either pass the centrifuge or you do not.

Menon joins a small but growing roster of astronauts with Indian roots — Kalpana Chawla, Sunita Williams, and now him — whose careers have unfolded entirely within American institutions while remaining, in the public imagination back home, unmistakably Indian. That dual claim is itself a feature of diaspora life: the achievement belongs to two countries at once, and both will take credit.

### A different kind of role model

There is a quieter point buried in Menon's biography. For decades, the diaspora's success was measured in proximity to money and power — the doctor, the engineer, the executive. Those remain the default aspirations in many Indian-American households. Menon's path runs through all of them and then keeps going, into a vocation that offers neither wealth nor obvious security.

That is the part worth dwelling on. The first generation of Indian immigrants to the United States optimized for stability, choosing professions that travelled well and paid reliably. Their children, raised with that stability already banked, are now free to chase the impractical. An eight-month tour on a space station is not a hedge against anything. It is the opposite — a bet that the immigrant story has finally earned the right to be about something other than survival.

When the Soyuz lifts off, families from Edison to Fremont will pull up the livestream and tell their kids to watch. The lesson they intend to teach is the old one about hard work. The lesson that may actually land is newer: that the destinations have changed, and the diaspora's children are allowed to aim past the corner office now."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "He Wore No. 10 for New Zealand and Made History for India Without Ever Playing for It",
        "subheadline": "Sarpreet Singh became the first player of Indian heritage to start a World Cup match. He is one of at least four at this tournament — a scattered, accidental Indian team playing under other flags.",
        "slug": make_slug("indian-heritage-players-fifa-world-cup-2026-sarpreet-singh-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "India has never qualified for a men's World Cup, yet its bloodlines are all over the 2026 tournament — in New Zealand, Australian, Qatari and Congolese shirts. It is the diaspora's strange consolation: present everywhere, representing no one back home.",
        "tags": ["nri", "diaspora", "fifa-world-cup", "sarpreet-singh", "football", "sports"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "India-West", "url": "https://www.indiawest.com/"},
            {"name": "FIFA World Cup 2026", "url": "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/b/bd/Sarpreet_Singh_Training_2019-07-28_FC_Bayern_Munich.png",
        "image_caption": "Sarpreet Singh training with FC Bayern Munich in 2019",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """On June 16, in the Group G match between New Zealand and Iran, a 27-year-old midfielder from Auckland wearing the No. 10 shirt did something no player of Indian heritage had managed in the 96-year history of the men's World Cup: he started one.

Sarpreet Singh, born to Punjabi parents in New Zealand, played until the closing stages of the All Whites' 2-2 draw, threading through the middle and testing the Iranian goal more than once. He is not a household name, even among the diaspora that might claim him. But his presence in that starting lineup is a small landmark — and a window into one of the odder facts about Indian football.

### A team that doesn't exist

India has never qualified for a men's World Cup. The national side is currently ranked outside the world's top 120, and the prospect of a maiden appearance feels as distant as it has for decades. And yet the bloodlines of the Indian subcontinent are scattered across the 2026 tournament, stitched into the shirts of at least four other nations.

Alongside Singh there is Nishan Velupillay, the Melbourne-born forward of Tamil and Anglo-Indian descent who made his World Cup debut for Australia on June 14, coming on as a substitute in a 2-0 win over Türkiye. There is Tahsin Mohammed Jamshid, born in Doha to parents from Kerala, in Qatar's squad. And there is Samuel Moutoussamy, the DR Congo midfielder born in France to a mother from Congo and a father of Indo-Guadeloupean Tamil heritage — a lineage that traces back to the indentured-labour migrations of the nineteenth century.

They will never share a pitch as teammates. They represent four federations, four passports, four anthems. But taken together they form a kind of phantom Indian side, present at the World Cup in everything but name.

### The diaspora's familiar bargain

This is, in microcosm, the diaspora's oldest arrangement. The talent leaves, or is born elsewhere, and flourishes under another flag. India gets the reflected pride and none of the points. Singh's career is the perfect illustration: in 2019 he became the first player of Indian descent to appear in Germany's Bundesliga, turning out for Bayern Munich, before stints in Portugal, Serbia and a return to New Zealand football.

Had the structures back home been different — better academies, a professional pathway, a federation that could spot a Punjabi kid in Auckland — perhaps some of these players would have worn blue. Instead they did what migrants' children have always done: they took root wherever the soil was ready and grew there.

### What the diaspora actually celebrates

For Indian-origin football fans abroad, the 2026 tournament offers a peculiar pleasure. There is no India to support, so they assemble their own. A New Zealand jersey here, a Qatari one there, a quiet eye on the DR Congo squad sheet. It is fandom by ancestry rather than nationality — the same instinct that has Indian-Americans cheering a spelling-bee champion or a newly minted CEO, transplanted onto the world's biggest sporting stage.

Singh himself has been understated about the milestone, the way professional athletes usually are about anything that isn't the result. But the symbolism outruns him. A boy from a Punjabi family in New Zealand, starting a World Cup match with a 10 on his back, is the diaspora's condition rendered in ninety minutes: belonging fully to the country that raised you, while a second country, half a world away, decides it belongs a little to you too.

India will not lift the trophy in 2026. It was never in the draw. But its grandchildren are out there on the grass, and for a community used to celebrating its scattered success, that may be the only Indian team this tournament was ever going to field."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Dangled a 7% Dollar Return at the Diaspora. Now Its Banks Are Scrambling to Fund the Promise.",
        "subheadline": "The RBI's special deposit window could pull in $55-70 billion from NRIs by September. But behind the headline rates, banks are quietly fighting over who is allowed to make the loans that make the math work.",
        "slug": make_slug("nri-fcnr-deposit-scheme-gift-city-banks-rbi-dollar-inflows-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For NRIs, the pitch is simple — a tax-free 7% dollar return from a home-country bank. But the scramble behind the scenes shows how badly India needs the diaspora's savings right now, and how the fine print decides who actually benefits.",
        "tags": ["nri", "diaspora", "fcnr", "nre", "rbi", "remittances", "banking", "gift-city"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/"},
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/GIFT_City%2C_Gandhinagar%2C_India_Sep_27%2C_2025_07-28-42_AM_from_IndiGo_flight.jpeg/1280px-GIFT_City%2C_Gandhinagar%2C_India_Sep_27%2C_2025_07-28-42_AM_from_IndiGo_flight.jpeg",
        "image_caption": "An aerial view of GIFT City, India's tax-neutral financial hub in Gandhinagar, Gujarat",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """For the non-resident Indian with dollars to park, the offer arriving from home looks almost too good. A foreign-currency deposit in an Indian bank now pays between 6% and 7.1% — tax-free, denominated in dollars, with no exposure to the rupee's slide. A few months ago the same deposit paid barely 3%.

The headline is doing exactly what New Delhi wants. Behind it, though, India's banks are in a quieter, more revealing fight over how to make the promise pay for itself.

### What the RBI actually did

On June 17, the Reserve Bank of India temporarily lifted the interest-rate ceiling on fresh Foreign Currency Non-Resident, or FCNR(B), deposits of three-to-five-year tenor, along with the cap on Non-Resident External (NRE) rupee deposits of three years and above. The relaxation runs until September 30. It followed a June 5 measure in which the central bank agreed to absorb the cost of currency hedging on new FCNR(B) deposits — effectively handing banks a subsidy so they could offer depositors more.

The motive is not subtle. The rupee was among Asia's worst-performing currencies in 2025, falling around 10%, and has shed nearly 6% more this year. A spike in crude prices following the Iran-US conflict widened the import bill and piled pressure on the currency. India imports close to 90% of its energy. Faced with that, the RBI reached for an old tool: the diaspora's savings.

It has worked before. In 2013, during the "taper tantrum," a similar FCNR(B) scheme under then-governor Raghuram Rajan pulled in roughly $25 billion and helped steady a falling rupee. This time the estimates are larger. Brokerage Nomura reckons the window could attract $55 billion, with the bulk arriving in August and September; other forecasts run to $70 billion.

### The fight the headlines miss

Here is where it gets technical, and telling. The scheme works through a leverage mechanism: banks offer loans to depositors, who then park that money in dollar deposits, with the central bank's swap facility making the hedging affordable. The question now dividing the industry is who gets to make those loans.

Banks want to route the funding through their units in GIFT City — the Gujarat International Finance Tec-City, India's tax-neutral offshore hub — which operate under offshore banking rules and, the lenders argue, function much like foreign banks. The RBI has not yet said whether GIFT City branches qualify.

"Most banks have branches in GIFT City, but many of them do not have a presence in foreign countries," VRC Reddy, treasury head at Karur Vysya Bank, told Reuters. "If the leverage is not allowed through GIFT, these banks will have to depend on foreign lenders." In plain terms: without GIFT City in play, smaller Indian banks lose the ability to compete for diaspora dollars, and the whole inflow tilts toward a handful of large players with overseas reach.

### And the depositors who came too early

There is a second, sharper grievance — this one from NRIs themselves. The RBI's higher rates apply only to fresh deposits and those that have already matured. Anyone who locked in an FCNR(B) deposit in the past few months, before the window opened, is stuck earning the old 3%-odd rate while watching newer money earn double.

Banks have asked the RBI for permission to let those customers break existing deposits and rebook them under the new terms. The numbers suggest real frustration: bankers estimate nearly $1 billion in deposits could be pulled prematurely — penalties and all — if the central bank refuses to allow clean rebooking. Under the scheme, eligible FCNR deposits must come in multiples of $1 million and carry a one-year lock-in, and the swap facility covers only US-dollar deposits.

### The diaspora as shock absorber

For the diaspora, the episode is a familiar one dressed in new arithmetic. India's roughly nine million NRIs already send home some $138 billion a year in remittances, the largest such flow in the world. When the rupee wobbles, the diaspora's savings become a lever the central bank can pull — courted with tax breaks and premium rates precisely when the home economy needs a cushion.

The 7% return is real, and for many NRIs it is a genuinely good deal before the September 30 window shuts. But the scramble underneath it is the more honest story. India is not simply rewarding its expatriates' loyalty. It is leaning on it — and the fine print, as ever, will decide who actually comes out ahead."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK  {art['slug']}")
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")
