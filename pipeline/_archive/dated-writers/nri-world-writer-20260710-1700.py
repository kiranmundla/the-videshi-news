#!/usr/bin/env python3
"""NRI World Writer — July 10, 2026 17:00 PT run"""
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
        "headline": "Twenty-Five Thousand Devotees, Three Chariots, Fifty Years: ISKCON's Golden Jubilee Is Rolling Across North America",
        "subheadline": "From a Manhattan street where a young property developer once lent his land for the first parade to a continent-wide circuit drawing tens of thousands, the Hare Krishna chariot festival marks half a century in the West.",
        "slug": make_slug("iskcon-ratha-yatra-50th-anniversary-north-america-golden-jubilee"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Ratha Yatra's 50-year arc mirrors the Indian diaspora's own journey in North America — from a handful of immigrants improvising a chariot parade in 1976 to a sprawling cultural institution that now anchors Hindu community life in dozens of cities.",
        "tags": ["nri", "diaspora", "iskcon", "ratha-yatra", "hindu", "culture", "community"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Religion News Service", "url": "https://religionnews.com/2026/06/15/hare-krishnas-celebrate-a-50-year-milestone-with-a-parade-of-chariots-in-manhattan/"},
            {"name": "ISKCON News", "url": "https://iskconnews.org"},
            {"name": "LA Ratha Yatra", "url": "https://larathayatra.com"},
            {"name": "ISKCON Ottawa", "url": "https://iskconottawa.ca"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Rath_Yatra_or_Chariot_Festival_held_in_CT%2C_USA.jpg/1280px-Rath_Yatra_or_Chariot_Festival_held_in_CT%2C_USA.jpg",
        "image_caption": "Devotees pull a decorated chariot during a Ratha Yatra festival in the United States",
        "image_attribution": "Wikimedia Commons",
        "body": """On a blazing Saturday in mid-June, New Yorkers heading to watch a World Cup match or celebrate the Knicks' NBA title found themselves sharing Fifth Avenue with something considerably older than either sport. Three chariots, each standing roughly twenty-five feet tall and festooned with jewel-toned balloons and silk garlands, rolled south from 41st Street toward Washington Square Park. More than 25,000 people turned out, according to organisers — pulling ropes, chanting, dancing, and eating free vegetarian food prepared in overnight shifts by over 400 volunteers. The occasion was the 50th anniversary of ISKCON's New York Ratha Yatra, the "Chariot Journey" that has become the single largest annual event for the Hare Krishna movement in the Western Hemisphere.

The milestone matters beyond ISKCON's own ranks. The Ratha Yatra's half-century arc in North America traces the diaspora's broader evolution — from a small, counter-cultural community of devotees in the 1970s to a sprawling institution that now anchors Hindu cultural life in dozens of cities across the continent.

## A chariot, a developer, and a conch shell

The first New York Ratha Yatra took place in 1976, a decade after A.C. Bhaktivedanta Swami Prabhupada arrived in America with the mission of spreading Krishna consciousness. The movement was still young, its devotees often viewed with bewilderment. When organisers struggled to find a spot near Fifth Avenue to assemble the giant wooden chariots, they turned to a new property owner in the neighbourhood: Donald Trump. He offered his land, and the inaugural parade went ahead.

For the golden jubilee, organisers spent six months preparing and approximately $160,000 — all from donations. They transported one of the original 1976 chariots from Florida to New York for the occasion. As saffron-robed monks blew conch shells and offered blessings, devotees in silk saris and patterned tunics picked up the ropes and pulled. The chariots gained momentum, turning onto Fifth Avenue enveloped in the rhythms of dhol and manjira.

"We don't see anything like this back home," said Patrick Ornelas, a bystander visiting from Salt Lake City.

## From Brooklyn ashram to continent-wide circuit

ISKCON now counts over one million devotees in more than 80 countries. Its Brooklyn temple houses about 40 full-time monks and attracts some 500 regular attendees for services. But the annual Ratha Yatra dwarfs those numbers, regularly engaging tens of thousands and serving as a public-facing outreach event that welcomes newcomers through food, music and conversation.

"Our aim is to reach out and see if we can get around three per cent of the population of North America coming to these festivals, enjoying the company of the devotees and eating sanctified food," said Aditya Devi Dasi, vice president of ISKCON's New York City branch.

The golden-jubilee energy is not confined to Manhattan. The 50th-anniversary season stretches across the continent this summer: Toronto hosts its Ratha Yatra this weekend on July 11 and 12, Ottawa follows on July 18, Vancouver on July 26, and Los Angeles stages its own 50th celebration at Venice Beach on August 2, with San Francisco closing out the major circuit on August 23.

## A $15 million master plan in Los Angeles

The Los Angeles celebration, in particular, signals ambition beyond a single parade day. ISKCON's New Dvaraka temple in LA recently raised more than $300,000 at a fundraising gala attended by some 300 guests, including representatives from the Indian Consulate and renowned devotional singer Anup Jalota. The event also saw the public unveiling of a $15 million master plan for the future development of the historic temple community — a bet that the movement's next 50 years will demand permanent infrastructure, not just annual processions.

The LA Ratha Yatra is one of the longest-running Jagannatha chariot festivals outside India. Its 50th anniversary on August 2 will feature a two-day programme: a kirtan mela on August 1, followed by the chariot parade down Main Street and the Venice Beach boardwalk, and an afternoon of festivities at Windward Plaza.

## Knicks fans and viral clips

ISKCON has also found an unlikely cultural crossover in recent months. During the Knicks' NBA championship run, Hare Krishna devotees went viral for chanting with fans outside Madison Square Garden. Mahamantra, the ISKCON monk who featured in the clips, was selling Hare Krishna T-shirts styled in the Knicks' neon orange at the New York Ratha Yatra.

"I'm excited for if the Knicks win, but I'm most excited to be with people dancing and chanting," he said, adding that the videos had driven a noticeable uptick in interest.

For Sarvopama Das, a 79-year-old devotee who flew in from Chicago, the journey from curiosity to cultural mainstream has been remarkable. He had volunteered to serve watermelon at the very first Ratha Yatra in 1976. "We thought we were cool talking about karma in the hippie days," he said. "Now it's in the dictionary."

Among the younger generation, the appeal is less about counterculture and more about community. Payal Mazumdar, 15, attends weekly Bhagavad Gita classes at ISKCON Brooklyn. "I have a really bad overthinking problem," she told Religion News Service. "But through the ISKCON community and philosophies, it felt like I had a support system on my side."

In the coming weeks, the three New York chariots will be transported to other cities for their own Ratha Yatras — growing the movement, organisers hope, with every turn of the wheel."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Forty-Nine Years of Prayers, Dosas, and New Beginnings: Inside America's Second-Oldest Hindu Temple on Its Birthday",
        "subheadline": "On July 4th, as the United States marked 250 years, the Ganesh Temple in Flushing, Queens, celebrated its own anniversary — a quieter milestone that traces the entire arc of Hindu community-building in America.",
        "slug": make_slug("flushing-ganesh-temple-49th-anniversary-americas-250th-queens"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Flushing temple's story is the diaspora's story in miniature — a community of immigrants who arrived after the 1965 Immigration Act, pooled their resources, bought a former church, and built a spiritual anchor that has served generations. Its anniversary falling on July 4th is a coincidence that became a tradition, quietly linking the Indian-American journey to the American one.",
        "tags": ["nri", "diaspora", "hindu-temple", "flushing", "queens", "new-york", "community", "culture"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Religion News Service", "url": "https://religionnews.com/2026/07/07/nearly-50-years-after-its-founding-a-hindu-temple-in-queens-still-draws-the-faithful/"},
            {"name": "Hindu Temple Society of North America", "url": "https://www.nyganeshtemple.org/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Hindu_Temple_Society_of_North_America_%28Flushing%2C_Queens_-_exterior%29.jpg/1280px-Hindu_Temple_Society_of_North_America_%28Flushing%2C_Queens_-_exterior%29.jpg",
        "image_caption": "The exterior of the Hindu Temple Society of North America in Flushing, Queens, New York",
        "image_attribution": "Wikimedia Commons",
        "body": """Temple bells echoed through the sanctuary. Priests chanted Sanskrit prayers before black granite deities draped in silk and fresh flowers. Barefoot worshippers carrying coconuts, bananas and jasmine garlands moved from shrine to shrine. Downstairs, volunteers poured steaming sambar over plates of idli and crisp dosas. It was July 4th in Flushing, Queens — and the Ganesh Temple was turning forty-nine.

The Šri Mahã Vallabha Ganapati Devasthãnam, as it is formally known, is the second-oldest traditional Hindu temple founded by Indian immigrants in the United States. Only Sri Venkateswara Temple in Pittsburgh's Penn Hills, consecrated a few weeks earlier on June 8, 1977, holds seniority. The Flushing temple opened its doors on July 4th of that year, a date that was practical — most people had the day off — but has since become a tradition that quietly links the Indian-American journey to the American one.

This year, as the United States marked its 250th anniversary, more than a hundred worshippers gathered at the temple to mark its own, considerably younger, milestone.

## From a church to a mandir

The temple's origin story is, in many ways, the diaspora's origin story. After the Immigration and Nationality Act of 1965 abolished the national-origins quota system, a wave of Indian professionals — engineers, doctors, scientists — arrived in the New York metropolitan area. They wanted a place of worship. The community formed the Hindu Temple Society of North America and purchased the site of a former Russian Orthodox church in Flushing, Queens, converting it into a traditional South Indian temple.

Nearly five decades later, the Hindu Temple Society counts more than 20,000 devotees on its mailing list. And the landscape it helped pioneer has transformed beyond recognition: there are now an estimated 1,000 Hindu temples spread across 45 states, from elaborate multi-shrine complexes in New Jersey and Texas to modest prayer halls in the Midwest.

The Flushing temple, however, retains a pull that newer, larger mandirs often cannot replicate. Dedicated to Lord Ganesha — the elephant-headed deity revered as the remover of obstacles — it has long been the place diaspora families visit before a milestone: starting a new job, welcoming a child, beginning a new chapter.

## The canteen that became a destination

Ask many New Yorkers about the Ganesh Temple and they will mention the food before the deities. The temple's basement canteen, opened in 1993, has become one of the city's best-known destinations for South Indian vegetarian cuisine. The menu is simple — idli, dosa, vada, uttapam, sambar, chutneys — and the prices are modest. It draws Hindu worshippers alongside neighbourhood residents, students, tourists and food writers. Many visit the temple after stopping for a meal; others make the meal the pilgrimage.

Beyond daily worship and the canteen, the temple hosts religious festivals, cultural celebrations and educational programmes throughout the year. Its Ganeša Pãtašãlã, a religious and cultural school established in 1998, offers instruction in Hindu religion, Indian languages, classical music and Bharatanatyam dance, giving second- and third-generation Indian Americans a structured connection to their heritage.

## Pilgrims from Kansas and Cincinnati

On July 4th, worshippers filled the temple from early morning, lining up with trays of fruit, coconuts and flowers as priests performed special pujas throughout the day. Families gathered before the shrines, then made their way downstairs to the canteen.

Some had travelled only a few subway stops. Others had driven or flown hundreds of miles.

Sai Yash, 34, had come from Wichita, Kansas. "I came after hearing that this is one of the finest temples," he said. "Whenever we begin something, a new job, the first prayer we do is to Ganesha. That's why we came to this temple."

Dharti Adhia had travelled from Cincinnati with her husband and their 11-month-old child. The visit fulfilled a promise she had made to herself years earlier. "The first time I came here, I remember thinking that one day I'd bring my baby here," she said. "This place has always felt very special."

For Jai Yaram, 34, who immigrated from India several years ago, the temple has been a constant through the disorientation of building a new life. "It gives me a lot of peace," he said. "It brings the values from India here. I hope this temple stands forever, because I came here as an immigrant, and gradually I'm progressing."

## Approaching fifty

Next year, the Flushing temple will reach its golden jubilee — fifty years since a group of immigrants who had left everything familiar pooled their resources and turned a disused church into a mandir. By then, the number of Hindu temples in the United States will likely have climbed past the thousand mark. But for the families who keep returning to this corner of Queens — carrying coconuts, ordering dosas, asking Ganesha to clear the way — the numbers matter less than the continuity.

The temple was built because a community needed it. Nearly half a century later, it endures because the need has not changed."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
