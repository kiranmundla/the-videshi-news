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

body_goyal = """India and Canada spent the better part of two years barely speaking. Diplomats were expelled, trade talks were frozen, and the roughly 1.8 million people of Indian origin who call Canada home found themselves living inside a quarrel they had not started. This week, a different kind of delegation landed in Toronto — and its size was the message.

Commerce Minister Piyush Goyal arrived leading what officials described as the largest-ever Indian business delegation to Canada, representatives of more than 100 companies, to push along stalled negotiations over the Comprehensive Economic Partnership Agreement (CEPA). It was the most visible sign yet that Ottawa and New Delhi are trying to thaw a relationship that went cold after the 2023 killing of a Sikh separatist on Canadian soil.

## The diaspora as ballast

For the Indo-Canadian community, the visit carried a subtext that no communiqué spelled out. Through the freeze, it was ordinary families — running gurdwaras and grocery chains, sitting in Parliament and on hospital boards — who absorbed the awkwardness of being told, in effect, that their two homes were at odds.

Goyal leaned into that. He met members of the Canada-India Foundation and praised "the invaluable contribution of the Indo-Canadian community in bringing the two nations closer through stronger business engagement and people-to-people ties." It is the standard ministerial line. But after two years in which the community was more often discussed as a security problem than an asset, the framing landed differently.

## What is actually on the table

The numbers explain the urgency. Bilateral trade sits at around $8.5 billion, a rounding error for two G20 economies, and both governments say they want it at $50 billion by 2030. Reaching anything close means a trade deal, and a trade deal means the political relationship has to function.

Goyal's itinerary tracked that ambition. Beyond CEPA, he met institutional investors including the Ontario Teachers' Pension Plan and CPP Investments — among the deepest pools of patient capital on earth — about infrastructure, renewables, logistics and the digital economy back in India. He urged Canadian firms toward clean energy, aerospace, food processing and technology.

## The bridge that did not burn

What makes the diaspora indispensable here is precisely what made it uncomfortable during the freeze: it is genuinely binational. An Indo-Canadian executive understands a Brampton supply chain and a Gujarat factory floor. A second-generation engineer in Waterloo can read both a Toronto term sheet and a Bengaluru cap table. That fluency is the actual product India is selling, and Canada is, however cautiously, buying.

None of this means the underlying tensions have vanished. The diplomatic wounds of the past two years are real, and a single ministerial visit does not reset them. Sikh-separatist politics remain a live irritant, and Canadian electoral arithmetic will keep the file sensitive. But trade has a way of forcing pragmatism, and a delegation of 100 companies is hard to ignore.

For Indo-Canadians who spent two years fielding pointed questions at dinner parties and in comment sections, the week offered something quieter than vindication: the sense that the relationship they embody, the one that lives in mixed marriages and dual passports and WhatsApp groups spanning Surrey and Surat, was being treated, at last, as the country's most valuable asset rather than its most awkward one.

## What's next

CEPA talks are expected to resume in earnest, with negotiators aiming for an interim agreement before tackling the harder chapters on services and mobility. For the diaspora, the mobility chapter matters most: easier movement of professionals and students is the part of any deal that touches kitchen tables, not just boardrooms. Whether the warmth survives the next political shock is the open question. The community has learned not to assume it will."""

body_holi = """On a Saturday in June, a stretch of the Jersey City waterfront across the Hudson from Lower Manhattan disappeared under a haze of pink, green and gold. The occasion was Surati Holi Hai 2026, billed as one of the largest Festival of Colors celebrations on the American East Coast, and by mid-afternoon several thousand people had turned Exchange Place into something that looked, for eight hours, transplanted from Mathura.

That a spring festival was being celebrated in summer is itself a small lesson in how the diaspora keeps tradition alive: not by replicating the calendar, but by replicating the feeling, scheduled around American work weeks and outdoor-permit seasons rather than the lunar one.

## A festival that grew up

Surati Holi Hai, organized by Surati for Performing Arts under artistic director Rimli Roy, has become a fixture. What began as a community gathering now runs as a full-day production, from noon to 8 p.m., drawing families from across New York, New Jersey and Connecticut.

This year's lineup reached back to the source. The festival flew in guest artists from India — Sumit Roy, the singer billed as the "Man with the Golden Voice"; the composer and filmmaker Rajesh Roy; and the Bollywood playback singer Pritha Majumdar — who also performed earlier in the week at the Voices International Festival at White Eagle Hall as part of the Surati Baul Blues Band.

## More than nostalgia

It would be easy to read events like this as nostalgia theater, the diaspora performing a postcard version of home for itself. The reality is more interesting. For second-generation kids who have never seen Holi in India, the Jersey City festival is not a copy of the real thing; it is the real thing — the only Holi they know, complete with American cousins, Spanish-speaking neighbors and a skyline of glass towers instead of temple spires.

That blending is the point. Surati describes its mission as bringing diverse communities together through art and culture, and the crowd reflects it: Gujarati grandmothers, Punjabi teenagers, and a healthy number of attendees with no Indian heritage at all, drawn by the simple proposition that throwing colored powder at strangers is a good time.

## The infrastructure of belonging

Behind the spectacle sits an unglamorous truth about diaspora life. Festivals like this do not happen by themselves. They require nonprofits, volunteers, municipal permits, sponsors and the patient institution-building that turns a one-off gathering into an annual rite. Surati for Performing Arts is part of a dense ecosystem of South Asian cultural organizations in the New York metropolitan area that, over decades, has constructed the scaffolding of community: dance schools, language classes, temple committees and, yes, color festivals.

That scaffolding is what lets a family that immigrated for a tech job in Hoboken raise children who can dance to a dhol beat and explain Holi to their classmates. It is the difference between a population and a community.

## What's next

Surati's calendar rolls on toward the autumn festival season, when Navratri and Diwali events will fill the same halls and waterfronts. For the organizers, each sold-out gathering is a quiet argument that the diaspora's cultural life is not a museum exhibit but a living, evolving thing — louder, more colorful, and a little more American with every passing year. The colored powder washes off by Sunday. The community it briefly made visible does not."""

body_aisle = """For decades, the Indian aisle in a Western supermarket was a cramped, slightly apologetic affair: a few shelves of basmati and lentils, some jars of pickle, tucked between the "international" instant noodles and the kosher section. The taste of home arrived in suitcases, smuggled past customs in checked baggage, or hunted down at the one good grocery a forty-minute drive away.

This week, a small milestone suggested how far that has shifted. Great White Northern Spirits (GWNS) formally launched what it calls the "Indian Aisle in Canada," putting premium Indian beverages into duty-free retail at major gateways — Toronto Pearson, Vancouver International, airports across Alberta, and land-border duty-free locations in Ontario and British Columbia.

## From ethnic shelf to mainstream gateway

The detail that matters is the location. Duty-free space is some of the most expensive and tightly controlled retail real estate in the world, reserved for brands that move volume and signal prestige — single malts, French cognac, luxury fragrance. An Indian product earning a ribbon-cutting in that environment is a different proposition from a sack of atta on a back shelf.

"Today is not just about launching products into a new market; it is about opening doors for Indian heritage, craftsmanship and stories to travel globally," said Balaji Nagaraja and Pooja S, the founders of GWNS, framing the launch as cultural as much as commercial. The company calls Canada's multicultural identity "the perfect home" for the initiative.

## The diaspora built the demand

Behind the corporate language sits a simpler story, and it belongs to the diaspora. The market for Indian products in Canada did not appear because a duty-free buyer had an epiphany. It was built, gradually and unglamorously, by 1.8 million Indo-Canadians who kept buying, kept cooking, and kept introducing colleagues and neighbors to flavors that were once exotic and are now, in cities like Toronto and Vancouver, simply normal.

That is the quiet economics of diaspora taste. A community large enough and settled enough stops being a niche and becomes a market. Restaurants follow, then groceries, then mainstream brands, and eventually the airport shelf. What looks like a sudden arrival is the visible end of a decades-long process of normalization that the community financed one grocery run at a time.

## A two-way mirror

The launch also tracks a broader diplomatic and commercial thaw between India and Canada, coming the same week as a 100-company Indian trade delegation to the country. Officials have been quick to link the two, casting consumer visibility as a complement to bilateral trade ambitions. There is something to that: soft power and hard commerce tend to travel together, and a recognizable Indian brand at an airport does work that no trade communiqué can.

But for the diaspora, the symbolism cuts a particular way. The generation that arrived with spice boxes wrapped in newspaper, who explained to bemused customs officers what asafoetida was, now watches its children pass Indian brands in the duty-free hall on the way home for the holidays. The pantry that once marked them as outsiders has become a category the mainstream wants to sell.

## What's next

GWNS says it intends to expand the format, and the duty-free debut will be watched as a test of whether Indian consumer brands can hold premium shelf space rather than competing only on price in the ethnic aisle. If it works, expect imitators — and expect the "Indian aisle" to keep migrating out of the back of the store and toward the front. For a community that spent years hunting for a taste of home, the more telling change is that home is now doing the selling."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Ottawa and Delhi Barely Spoke for Two Years. This Week, 100 Companies Flew In to Change That.",
        "subheadline": "Commerce Minister Piyush Goyal led India's largest-ever business delegation to Canada — and cast the Indo-Canadian diaspora as the bridge that outlasted the diplomatic freeze.",
        "slug": make_slug("piyush-goyal-canada-business-delegation-cepa-indo-canadian-diaspora-thaw"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "After two years caught in the India-Canada diplomatic crossfire, 1.8 million Indo-Canadians are being recast from a security headache into the relationship's most valuable asset as trade talks revive.",
        "tags": ["nri", "diaspora", "canada", "india-canada", "trade", "indo-canadian", "cepa"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian EYE — Piyush Goyal lauds role of Indian diaspora in Canada", "url": "https://www.theindianeye.com/"},
            {"name": "Reuters — India File: Rupee gets diaspora lifeline", "url": "https://www.reuters.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Piyush_Goyal_crop.jpg/330px-Piyush_Goyal_crop.jpg",
        "image_caption": "Indian Commerce Minister Piyush Goyal, who led the largest-ever Indian business delegation to Canada",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": body_goyal
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Stretch of the Jersey City Waterfront Vanished Under Colored Powder. For Thousands, It Was the Only Holi They Know.",
        "subheadline": "Surati Holi Hai 2026 drew thousands to Exchange Place — a summer-scheduled spring festival that shows how the diaspora keeps tradition alive by replicating the feeling, not the calendar.",
        "slug": make_slug("surati-holi-hai-jersey-city-festival-colors-diaspora-community-building"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For second-generation kids who have never seen Holi in India, the Jersey City festival is not a copy of home — it is the real thing, and the institution-building behind it is what turns a population into a community.",
        "tags": ["nri", "diaspora", "holi", "festival", "new-jersey", "culture", "community"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian EYE — Surati Holi Hai 2026 Returns to Jersey City", "url": "https://www.theindianeye.com/"},
            {"name": "South Asian Herald — Indian Diaspora cultural festivals in the US", "url": "https://southasianherald.com/"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/14872084/pexels-photo-14872084.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Revelers covered in colored powder at a Holi festival celebration",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body_holi
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Taste of Home Used to Arrive in a Suitcase. Now It Has a Shelf in the Duty-Free Hall.",
        "subheadline": "Premium Indian beverages have entered Canada's airport duty-free retail — a milestone built, one grocery run at a time, by 1.8 million Indo-Canadians.",
        "slug": make_slug("indian-aisle-canada-duty-free-diaspora-taste-mainstream-retail-gwns"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The generation that arrived with spice boxes wrapped in newspaper now watches its children pass Indian brands in the duty-free hall — the pantry that once marked them as outsiders has become a category the mainstream wants to sell.",
        "tags": ["nri", "diaspora", "canada", "business", "retail", "indo-canadian", "culture"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian EYE — Great White Northern Spirits launches 'Indian Aisle in Canada'", "url": "https://www.theindianeye.com/"},
            {"name": "Industries News (ANI) — 'Indian Aisle in Canada' launch", "url": "https://entertainment.industriesnews.net/"}
        ]),
        "score_total": 66,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32998741/pexels-photo-32998741.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An airport duty-free retail hall, where premium Indian products are now finding shelf space",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body_aisle
    }
]

for art in articles:
    try:
        wc = len(art["body"].split())
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
