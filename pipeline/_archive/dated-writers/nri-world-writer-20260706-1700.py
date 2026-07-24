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
        "headline": "Vancouver's Indian Summer Festival Returns With 90 Artists, Free Programming, and a Theme That Asks the Diaspora to Listen",
        "subheadline": "The 16th edition of Canada's largest South Asian arts festival opens July 9 with 'Ragas for a Ruptured World' — a provocation aimed squarely at a diaspora navigating belonging in unsettled times.",
        "slug": make_slug("indian-summer-festival-vancouver-ragas-ruptured-world"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian Summer Festival is one of North America's premier South Asian cultural events, rooted in Vancouver's large Punjabi and South Asian diaspora. Its free programming in Surrey's Punjabi Market and partnership with Indo-Canadian artists make it a direct expression of diaspora cultural identity and cross-generational connection.",
        "tags": ["nri", "diaspora", "arts", "culture", "vancouver", "canada", "festival", "south-asian", "music", "punjabi"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Drishti Magazine", "url": "https://drishtimagazine.com/arts/indian-summer-festival-2026/"},
            {"name": "Stir Vancouver", "url": "https://www.createastir.ca/articles/indian-summer-festival-2026"},
            {"name": "Indian Summer Festival", "url": "https://www.indiansummerfest.ca/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/18086255/pexels-photo-18086255.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
        "image_caption": "A performer on stage at a South Asian cultural event",
        "image_attribution": "Pexels",
        "body": """Every July, a particular kind of argument breaks out in diaspora group chats across Metro Vancouver. What does it mean to be South Asian in a country that alternately celebrates and sidelines you? Is the old culture something to preserve, to remix, or to let go? Is it possible to feel at home when the ground keeps shifting?

Indian Summer Festival does not answer those questions. For sixteen years, it has asked them — and this year's theme, "Ragas for a Ruptured World," is the sharpest framing yet.

The festival runs July 9 through 19, with more than 90 Canadian and international artists spread across venues in downtown Vancouver and Surrey. It is, by attendance and scope, the largest South Asian arts festival in Canada, and one of the few anywhere in North America that treats diaspora culture as living art rather than heritage display.

## A programme built around dissonance

The "raga" in the title is not metaphorical. Indian classical music forms are woven through the programme — but the rupture is everywhere too. Raagaverse, an Indo-jazz ensemble, opens the festival with a set that pulls Hindustani melodic structures through contemporary jazz improvisation. It is a sound that could only come from musicians who grew up between two traditions and stopped apologising for the collision.

Punjabi singer Rashmeet Kaur, whose collaborations have moved between Bollywood playback and independent Punjabi pop, brings a voice shaped by the same duality — classically trained but pop-fluent, equally comfortable with a folk wedding song and an electronic beat drop.

Comedy gets its own strand. Vidura Bandara Rajapaksa — a Sri Lankan-born, Canada-raised comedian — performs a set that mines the specific absurdities of growing up South Asian in Canada: the parental expectations, the cultural code-switching, the quiet ridiculousness of being told to be proud of your heritage while also being told, implicitly, to be less of it at work.

The programming is deliberately wide. There are visual art installations, panel discussions on diaspora identity, workshops on traditional craft forms, and a series of literary events that bring together writers from across the South Asian world. The breadth is the point: Indian Summer has always resisted the idea that "South Asian culture" is a single, knowable thing.

## Free access in Punjabi Market

Among the festival's more significant decisions is the expansion of free programming in Surrey's Punjabi Market — the commercial and cultural heart of one of Canada's densest South Asian neighbourhoods.

Surrey is home to the largest concentration of Punjabi Canadians in the country. It is also a neighbourhood where many residents — particularly first-generation immigrants and seniors — would not typically attend a ticketed arts festival downtown. The free programming is designed to meet them where they are: outdoor performances, street-level installations, family activities, food vendors, and community-curated events that blur the line between festival and neighbourhood life.

It is a practical concession and a philosophical statement. If the festival exists to explore what it means to be South Asian in Canada, it cannot do that exclusively in the venues of downtown Vancouver. The stories are in Surrey. The aunties and uncles who remember Partition, who built the gurdwaras, who raised children who now run tech companies and hip-hop labels — they are the living archive the festival draws from.

## Why this edition matters

Indian Summer Festival has always been more than entertainment, but this year's theme carries a particular weight. The "ruptured world" in the title gestures at a global moment — war, displacement, political polarisation, climate crisis — but it also speaks to fractures within diaspora communities themselves.

Across North America, South Asian communities are navigating internal tensions around caste, religion, political allegiance to India, and generational divides over assimilation. The festival does not resolve these tensions. It stages them, in public, through art — which is perhaps the only honest thing to do with a rupture you cannot fix.

For diaspora families in Metro Vancouver — and the estimated 1.8 million people of South Asian origin across Canada — the festival is a rare space where complexity is welcome. Where you can be proudly Punjabi and ambivalently Canadian. Where classical ragas and standup comedy can share a programme without anyone pretending they belong to the same tradition.

"Ragas for a Ruptured World" opens July 9. Tickets and free programming details are available at indiansummerfest.ca. For a community perpetually asked to explain itself, it offers something rarer: a chance to be explored, not explained."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "America's Fastest-Growing Diaspora Is Getting Old. The Safety Net Barely Exists.",
        "subheadline": "In Queens, an AI-powered food pantry is feeding 1,500 South Asian seniors a year. In Irvine, a new wellness centre serves elders who speak no English. Across the country, a crisis is building that the community has only begun to name.",
        "slug": make_slug("diaspora-seniors-aging-crisis-india-home-queens-gopio"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The aging of the first large wave of Indian immigrants to the US and the growing phenomenon of 'parent visas' — elderly parents brought over to help with grandchildren — has created a uniquely diaspora elder care crisis. Language barriers, cultural isolation, unfamiliarity with American social services, and the shame associated with admitting family cannot cope are all distinctly NRI dimensions of the problem.",
        "tags": ["nri", "diaspora", "seniors", "elder-care", "aging", "queens", "california", "gopio", "india-home", "community"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.net/gopio-webinar-diaspora-indians-aging-gracefully/"},
            {"name": "India Home", "url": "https://indiahome.org/"},
            {"name": "Diverse Elders Coalition", "url": "https://www.diverseelders.org/"},
            {"name": "AAPI Data", "url": "https://aapidata.com/"}
        ]),
        "score_total": 79,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36883131/pexels-photo-36883131.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
        "image_caption": "Elderly women at a community gathering, sharing companionship and support",
        "image_attribution": "Pexels",
        "body": """In a converted community space in Jackson Heights, Queens, a room full of South Asian seniors — most of them women, most of them in saris, most of them over seventy — gather on a weekday morning. They speak Bengali, Hindi, Urdu, Punjabi, Gujarati, and a little English. They share a meal. They do chair yoga. Some attend a computer literacy class. A few play carrom.

This is India Home, and for many of the 1,500-plus people it serves each year, it is the only place outside their family's apartment where they feel fully understood.

The organisation, founded in 2008, has become the largest provider of culturally specific elder care services for South Asian seniors in the United States. It operates senior centres in Jackson Heights and Sunnyside, runs home-based case management, and has recently launched what may be the most unexpected innovation in diaspora elder care: a Robo Food Pantry, built in partnership with Zippin, that uses autonomous checkout technology to let seniors select their own groceries — including culturally appropriate staples like dal, atta, basmati rice, and ghee — with dignity and without a queue.

The food pantry is a small, practical thing. But it gestures at a much larger problem that the Indian American community has been slow to confront: its elders are aging, many of them are alone, and the systems built to help them are not designed for people who arrived in this country in their sixties with no English, no Social Security history, and no idea how American healthcare works.

## The quiet crisis

The numbers are still emerging, but what exists is stark. According to AAPI Data, South Asians are one of the fastest-growing elderly populations in the United States. Between 2010 and 2020, the number of Indian Americans over 65 nearly doubled. Many are "follow-to-join" parents — brought to the US on dependent visas by adult children, often to help with grandchildren, and then left in a kind of domestic limbo when the grandchildren grow up and the adult children work long hours.

They live in their children's homes but do not drive. They speak their mother tongue but not the language of the country they now inhabit. They have no independent social network, no work history that qualifies them for Medicare or Social Security, and no cultural frame of reference for what "senior services" means in America.

In June, the Global Organization of People of Indian Origin — GOPIO — convened a webinar titled "Diaspora Indians: Aging Gracefully" that attempted to surface the scope of the problem. The panellists included geriatricians, social workers, and community organisers from across the US, and the picture they painted was consistent: isolation is endemic, depression is underdiagnosed, elder abuse is underreported, and the family — long held up as the Indian alternative to institutional care — is buckling under the weight.

"There is a cultural expectation that the family will take care of everything," said one panellist. "But the family is a dual-income household in New Jersey with two children in competitive schools and a mortgage. The grandmother sits in the living room and watches Hindi serials all day. That is not care. That is containment."

## Building what does not exist

India Home's response has been to build, from scratch, the infrastructure that neither the Indian American community nor the American welfare state has provided.

Its senior centres operate in the languages its members speak. Meals are vegetarian and culturally familiar. Case managers help seniors navigate Medicaid applications, citizenship paperwork, and housing assistance — bureaucratic processes that are bewildering even for native English speakers. A new affordable housing project, currently in fundraising with a target of $3 to $4 million, aims to create dedicated senior housing in Queens.

On the other coast, the Ektaa Center — operated by the South Asian Social and Health Alliance, or SASHA — opened in Irvine, California, serving a similar population. The centre offers yoga, meditation, group meals, and social programming tailored to South Asian seniors who may never have attended anything resembling a Western "senior centre." In the Bay Area, the Saheli network and various gurdwara-based programmes fill some of the gaps, though coverage remains patchy.

What all these organisations share is a recognition that mainstream American elder services — designed around English-speaking, car-driving, Medicare-enrolled retirees — do not work for a population that matches none of those assumptions.

## The sandwich generation

The crisis is not only the seniors'. Their adult children — often called the "sandwich generation" — are caught between ageing parents who need care and growing children who need attention, with the added complexity of cultural guilt. In Indian families, putting a parent in an assisted living facility is widely regarded as a moral failure, a betrayal of the implicit contract between generations.

This taboo keeps many families from seeking help until the situation is acute. A father who has had a fall. A mother who has stopped eating. A parent who has quietly been showing signs of cognitive decline for years, but no one said anything because saying it would mean admitting the family could not cope.

The Diverse Elders Coalition, a national advocacy group, has argued that culturally specific elder care is not a niche service but a civil rights issue. For South Asian seniors in America, the right to age with dignity depends on services that speak their language, serve their food, understand their family structures, and respect the enormous difficulty of growing old in a country that was never designed to grow old in.

## What comes next

India Home is expanding. The Robo Food Pantry, powered by Zippin's autonomous retail technology, is a pilot that could be replicated in other South Asian enclaves. The affordable housing project, if funded, would be the first dedicated senior housing for South Asians in the US. And GOPIO's webinar, though modest in scale, signalled that the organised diaspora is beginning to treat elder care as an institutional priority, not just a family problem.

For the estimated 4.4 million Indian Americans — and the broader South Asian community of nearly 6 million — the question is not whether this crisis exists. It is whether the community will build the answer before the first generation that made it to America ages out of the conversation entirely."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
