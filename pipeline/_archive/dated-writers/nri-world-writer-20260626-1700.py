#!/usr/bin/env python3
"""NRI World Writer — 2026-06-26 17:00 PT run"""

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
        "headline": "Paris Is About to Get Europe's First Traditional Hindu Temple. Thousands of Diaspora Devotees Are Already Packing.",
        "subheadline": "BAPS Swaminarayan Hindu Mandir opens in September with a 13-day Festival of Culture — boat processions on the Seine, Vedic rituals, and a Parisian exhibition that places the temple alongside Notre-Dame.",
        "slug": make_slug("baps-paris-mandir-hindu-temple-europe-festival-culture-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Paris mandir crystallises a pattern the diaspora has been pursuing for two decades: building permanent, architecturally ambitious Hindu sacred spaces abroad — from Robbinsville to Abu Dhabi — that anchor community identity for generations. For NRIs across Europe, it means no longer flying to London or India for a traditional temple experience.",
        "tags": ["nri", "diaspora", "hindu-temple", "baps", "paris", "france", "europe"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "BAPS Official", "url": "https://www.baps.org/News/2026/Festival-of-Culture--Launch-of-Mandir-Mahotsav-31325.aspx"},
            {"name": "Hinduism Today", "url": "https://hinduismtoday.com/press-releases/baps-hindu-mandir-in-paris-to-open-in-2026/"},
            {"name": "BAPS Paris Exhibition", "url": "https://www.baps.org/Photos/2025/Sacred-Places-Exhibition-32706.aspx"},
            {"name": "Global Holidays USA", "url": "https://globalholidays.us/why-paris-baps-mandir-opening-is-historic/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Swaminarayan_Akshardham_Temple-Delhi-96.jpg/1280px-Swaminarayan_Akshardham_Temple-Delhi-96.jpg",
        "image_caption": "Swaminarayan Akshardham in Delhi, built in the same tradition as the upcoming BAPS mandir in Paris",
        "image_attribution": "Wikimedia Commons",
        "body": """In Bussy-Saint-Georges, a multicultural suburb on the eastern edge of Greater Paris, a 5,000-square-metre temple is nearing completion on the Esplanade des Religions et des Cultures — a boulevard that already hosts a mosque, a Buddhist pagoda, a Sikh gurdwara, and a synagogue. When the BAPS Swaminarayan Hindu Mandir opens its doors on 2 September, it will become the first traditional Hindu temple in France, and the most architecturally ambitious one in continental Europe.

The opening will not be a quiet ribbon-cutting. BAPS has announced a 13-day *Festival of Culture* running from 2 to 14 September, blessed by the organisation's spiritual head, Mahant Swami Maharaj. The programme reads like a controlled spectacle of devotion and soft diplomacy: a *Jal Yatra* — a boat procession carrying sacred water along the River Seine — a *Nagar Yatra* through central Paris, daily Vedic fire rituals, a women's convention, a musical tribute, and the centrepiece *murti-pratishtha* ceremony between 4 and 7 September, when deities are formally consecrated and installed.

## A Vision 56 Years in the Making

The temple's origins trace back to July 1970, when the late Yogiji Maharaj paused at Le Bourget Airport during a European trip and told followers he could envision a spiritual centre in France. It took 18 more years for Pramukh Swami Maharaj to bless the Parisian land with a shower of flowers from an aeroplane in 1988. Construction finally broke ground in June 2024, with carved stones shipped from workshops in India where artisans followed ancient Vedic architectural scripts — the same method used for the BAPS Akshardham complex in Delhi and the record-breaking Robbinsville mandir in New Jersey.

The Parisian temple will be the first traditional multi-floor Hindu mandir in Europe. Its ground floor will house a community hall, a library, an exhibition centre, and a dining area. The upper floor will hold the main prayer hall, with shrines to Lord Shankar and Parvati, Ganesh, Shriram and Janki, Shrikrishna and Radha, Hanuman, and the Swaminarayan and Gunatitanand Swami *murtis*.

## Seated Alongside Notre-Dame

Even before its opening, the Paris mandir has won an unusual honour from the French establishment. A major exhibition titled *Sacred Places: Building, Celebrating, Coexisting* — presented by the Pavillon de l'Arsenal, Paris's leading architecture centre, and hosted at Espace Notre-Dame beneath the recently restored cathedral — featured the BAPS mandir among seven buildings whose floorplans were etched onto the exhibition floor. The curator, French architectural historian Mathieu Lours, included it alongside Notre-Dame itself, framing the upcoming temple as one of the places that "bring meaning and beauty to the city."

For a diaspora that has long funded and championed temple construction abroad — from the $96 million Robbinsville complex to the Abu Dhabi Akshardham that opened in 2024 — the Parisian exhibition matters. It signals recognition from a secular European cultural institution that Hindu sacred architecture has a permanent place in the city's civic identity, not merely its immigrant enclaves.

## The Diaspora Packs Its Bags

Registration for the Festival of Culture is mandatory, and BAPS chapters from the United States, the United Kingdom, and across Europe have been mobilising devotees since March, when the event was launched simultaneously in *satsang* assemblies around the world. Travel agencies in New Jersey are already marketing group pilgrimage-and-Europe-tour packages combining the temple opening with stops in Switzerland, Italy, and Germany — nine- to sixteen-day itineraries that blur the line between spiritual tourism and family holiday.

In the weeks before the announcement, BAPS volunteers from the UK completed a London-to-Paris charity cycle ride in support of the mandir — part of a broader fundraising push that has underwritten the temple's construction across decades. The French Préfet of Seine-et-Marne, Pierre Ory, visited the construction site in May and publicly praised its progress.

## Why Paris, Why Now

The timing is not accidental. France's Indian-origin population — smaller than Britain's or America's, but growing — has lacked a large-scale traditional temple. Most European Hindus outside the UK have worshipped in converted houses or community halls. The Paris mandir fills that gap, and its location on the Esplanade des Religions et des Cultures embeds Hinduism in France's official vocabulary of interfaith coexistence.

For Indian-American and Indian-British families planning the trip, the September opening is already becoming a once-in-a-generation marker — the kind of event, like Robbinsville's consecration or Abu Dhabi's inauguration, that the diaspora circles on the calendar and recounts for years afterward. Whether the Festival of Culture achieves the crowd numbers its planners expect remains to be seen. But the stones are carved, the Seine awaits its boat procession, and the tickets are moving."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Diaspora Built an American Dream. It Forgot to Plan for Getting Old in It.",
        "subheadline": "A Queens nonprofit is building robotised food pantries and affordable housing for South Asian seniors. A California volunteer group charges five dollars a class. Across the country, the infrastructure to age with dignity in a foreign land is being improvised from scratch.",
        "slug": make_slug("indian-diaspora-aging-seniors-india-home-gopio-elder-care"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The first large wave of Indian professionals arrived in America after the 1965 Immigration Act. Sixty years later, that cohort is entering its seventies and eighties — in a country whose elder-care infrastructure was not designed for people who speak Gujarati, eat vegetarian, and expect their children to live under the same roof. The story of how the community is scrambling to fill the gap is a defining NRI challenge of this decade.",
        "tags": ["nri", "diaspora", "aging", "seniors", "elder-care", "india-home", "gopio"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/26/gopio-organizes-webinar-on-diaspora-indians-aging-gracefully/"},
            {"name": "India Home Inc / GivingTuesday", "url": "https://givingtuesday.mightycause.com/organization/India-Home-Inc"},
            {"name": "AARP", "url": "https://www.aarp.org/caregiving/home-care/info-2021/aapi-senior-community-centers.html"},
            {"name": "PubMed / Oxford Academic", "url": "https://pubmed.ncbi.nlm.nih.gov/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8436645/pexels-photo-8436645.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An elderly woman participating in a community yoga session",
        "image_attribution": "Pexels",
        "body": """Saroj Topiwala is 71 years old, lives in a Chicago suburb with her son's family, and spent most of her waking hours on the couch until someone told her about a South Asian senior centre nearby. "It was a boring life at home," she told AARP in a profile that could have described tens of thousands of immigrant elders across the United States. "I wasn't happy."

Her story — the parent who followed adult children to America, who speaks limited English, who cannot wander down a street and chat with a neighbour the way they once did in Ahmedabad or Hyderabad — is one the Indian-American community has whispered about for decades but rarely treated as a structural problem. That is beginning to change, unevenly and often on shoestring budgets, as the first large cohort of post-1965 Indian immigrants enters its seventies and eighties.

## The Arithmetic of an Aging Diaspora

A 2026 study published in *Health Affairs* found that the share of immigrants who are older adults in the United States has risen from 10 percent in 2001 to over 15 percent in 2023, with Asia as one of the fastest-growing regions of origin. Immigrants from Asia were significantly less likely to reside in nursing homes than native-born Americans — but far more likely to live with adult offspring. The study's dry conclusion carries an emotional charge for any NRI family: South Asian elders are aging at home because the alternatives are culturally unthinkable, not because home is adequate.

The Global Organization of People of Indian Origin picked up this thread at its June 2026 webinar, *Diaspora Indians — Aging Gracefully*, which drew service providers, Ayurvedic practitioners, and nutritionists from across the country. The panel's makeup told its own story: there were no government officials, no hospital executives, and no representatives from mainstream American elder-care institutions. The diaspora's senior-care infrastructure is being built by the diaspora itself.

## India Home: From Basement Centre to Robo Pantry

The most striking example sits in Queens, New York. India Home, founded in 2007 by healthcare professionals who noticed that South Asian seniors in the city had nowhere to go, now serves over 1,500 elderly people annually across multiple neighbourhood centres in Jamaica, Flushing, and other Queens communities. Its programming — congregate vegetarian and halal meals, yoga classes, Diwali celebrations, digital literacy workshops, benefits counselling — is designed to feel like the community hall back in Surat or Dhaka.

Dr. Vasundhara Kalasapudi, India Home's founder and executive director, told the GOPIO webinar about two projects that signal where the organisation is heading. The first is an affordable housing development in Queens for South Asian seniors, which has raised $3 to $4 million from community members — no small feat, she noted, in a diaspora accustomed to investing in for-profit ventures but allergic to nonprofit fundraising. "The community is wealthy," she said, "but convincing them to invest in a nonprofit was a different conversation entirely." Jewish community organisations, she added, provided crucial early loans when Indian donors hesitated.

The second is a technology bet that sounds improbable for a senior centre: a *Robo Food Pantry*, built in partnership with Zippin, the checkout-free retail technology company. Traditional food pantries operate a few hours a week, creating barriers for seniors with mobility issues, language difficulties, and long commute times. India Home's automated pantry will offer fresh, culturally appropriate groceries — dal, atta, basmati rice, the staples that mainstream food banks rarely stock — twelve hours a day, six days a week, using camera-and-sensor technology to eliminate checkout lines.

## The California Model: Five Dollars and a City Partnership

Three thousand miles away, in Irvine, California, the South Asian Senior Association operates on a radically different model. SASA, presented at the GOPIO webinar by programme director Preeti Singh, is a volunteer-driven organisation that partners directly with municipal governments. The city of Irvine provides access to community space; SASA charges a modest $5 per class to cover instructor costs. The model is self-sustaining with minimal grants and replicable in any suburb with a willing city council.

Singh outlined five pillars for what she called graceful aging in the diaspora: preventing isolation, engaging in purposeful activities, maintaining preventive health care, understanding government resources (Medicare, Social Security, benefits that many immigrant seniors do not know they qualify for), and planning ahead. The last pillar, she acknowledged, is the hardest. Many first-generation Indians resisted discussing wills, advanced directives, or long-term care plans — partly because such conversations feel Western, partly because the assumption was always that the children would handle it.

## The Ayurveda Angle

The GOPIO panel also gave airtime to something rarely discussed in mainstream elder-care policy: Ayurvedic approaches to aging. Dr. Jaya Daptardar, an Ayurvedic physician and healthcare executive, laid out a framework rooted in the five elements — earth, water, fire, air, space — and their corresponding sense organs, with practical prescriptions that ranged from daily oil massage and tongue scraping to periodic *panchakarma* detoxification retreats.

It would be easy for a Western observer to dismiss this as fringe. But for a generation of elderly Indians who grew up with Ayurvedic practitioners as their primary physicians and who distrust American pill-heavy geriatrics, the appeal is real and practical. Rita Batheja, a registered dietitian on the panel, bridged the two worlds, emphasising gut-health science and electrolyte balance while recommending familiar desi staples: chickpeas, soy beverages, nuts, and seeds as protein sources that do not require persuading a vegetarian grandmother to eat chicken.

## What Is Missing

For all the energy on display at the GOPIO webinar, the gaps remain enormous. India Home operates in one city. SASA covers a few Southern California suburbs. There is no national Indian-American elder-care organisation, no coordinated lobbying effort for culturally competent Medicare services, and no large-scale senior housing development comparable to what Chinese-American and Korean-American communities have built in several states. New Jersey and upstate New York were identified as future possibilities for affordable senior housing — but possibilities is not ground broken.

The generation that arrived with engineering degrees in the 1970s, built billion-dollar companies, funded temples from Robbinsville to Abu Dhabi, and sent record remittances home is now discovering that America's elder-care system was not designed for them. Fixing that will require the same organised ambition that built the temples — directed inward, for once, at the community's own aging parents."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
