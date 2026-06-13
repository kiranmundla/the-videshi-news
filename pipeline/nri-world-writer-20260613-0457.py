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
        "headline": "Twenty-One Years, One Gopuram: Berlin's Sri Ganesha Temple Opens as One of Europe's Largest Hindu Shrines",
        "subheadline": "Black granite carved in Tamil Nadu, water from the Ganges poured by crane, and a Modi-Merz visit pencilled for October — the Neukölln temple is the diaspora's most ambitious European construction project in a generation.",
        "slug": make_slug("sri-ganesha-temple-berlin-europe-largest-hindu-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "A two-decade community effort by Berlin's Tamil Hindu diaspora — students, IT workers, Sri Lankan refugees — built one of Europe's largest Hindu temples entirely through donations and volunteer labour, creating a permanent spiritual anchor for South Asians across Germany.",
        "tags": ["nri", "diaspora", "hindu-temple", "germany", "berlin", "europe", "community"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/08/sri-ganesha-temple-in-berlin-opens-doors/"},
            {"name": "The Berliner", "url": "https://www.the-berliner.com/english-news-berlin/hindu-temple-opens-at-hasenheide/"},
            {"name": "Ulagam / Astroulagam", "url": "https://astroulagam.com.my/lifestyle/berlin-welcomes-one-europes-largest-hindu-temples-dream-21-years-making"},
            {"name": "Hinduism Today", "url": "https://hinduismtoday.com/press-releases/sri-ganesha-temple-one-of-the-largest-hindu-temples-in-europe-opens-doors-in-berlin/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/%2820260607_143234213%29_Sri_Ganesha_Hindu_Temple_Berlin.jpg/1280px-%2820260607_143234213%29_Sri_Ganesha_Hindu_Temple_Berlin.jpg",
        "image_caption": "The Sri Ganesha Hindu Temple in Berlin's Neukölln district on the day of its consecration, June 7, 2026",
        "image_attribution": "Wikimedia Commons",
        "body": """On June 7, 2026, a crane lowered a vessel of Ganga water onto the spire of a 17-metre vimana rising above Hasenheide Park in Berlin's Neukölln district. The act completed the Mahakumbhabhishekam — the most sacred ceremony in Hindu temple tradition — and opened one of the largest Hindu temples in Europe to the public.

The Sri Ganesha Hindu Temple had taken twenty-one years to build. Every euro of its €1.1 million construction cost came from donations. Every hour of non-specialist labour came from volunteers. The result is a South Indian temple built to classical Agamic standards in the middle of a German city better known for techno clubs and döner kebab.

## From Foundation Stone to Gopuram

The project began on 24 September 2005, when a small group of Tamil Hindus — some from India, others from Sri Lanka's war-displaced diaspora — laid a foundation stone on a plot bordering one of Neukölln's busiest parks. For years, the building rose in fits and starts, fundraising drive by fundraising drive.

The first gopuram tower appeared above the roofline in 2015. Black granite, quarried and hand-carved by traditional stonemasons in Tamil Nadu, was shipped to Berlin in containers and fitted to a modern structural frame. The contrast is the point: the temple is architecturally rooted in the Dravidian tradition but built with German engineering permits and Berlin fire code compliance.

Three pujaris now conduct daily aarti, morning and evening. Ten volunteer board members manage operations. The Finanzamt — Germany's tax authority — recognises the temple as a registered non-profit.

## A Five-Day Festival, 4,000 Visitors

The consecration ran from June 3 to June 7. Priests from India and several European countries performed the rituals over the first three days, with public access restricted. On the final weekend, over 4,000 devotees and visitors streamed through the gates — one of the largest Hindu religious gatherings Berlin has ever seen.

The celebrations included Mallakhamb demonstrations (the ancient Indian pole-gymnastics discipline), devotional music, and traditional South Indian vegetarian meals served to all comers. The water ceremony on Sunday morning used both Ganga water and water collected from Berlin's own rivers, a symbolic blending of the sacred and the local.

Members of the Bundestag and the Berlin Senate attended alongside consular officials. The temple is open to all Hindu currents — Vaishnava, Shaiva, Shakta, Smarta — and to anyone who walks in: Berlin families, students, mixed-faith couples, school groups on open days.

## Modi and Merz in October

The temple's significance has not escaped diplomatic notice. Indian Prime Minister Narendra Modi and German Chancellor Friedrich Merz are expected to visit the temple together in October, when the two countries mark 75 years of diplomatic relations. The visit would be one of the highest-profile political endorsements a diaspora-built temple has received anywhere in Europe.

## What It Means for Germany's Hindus

Germany is home to an estimated 130,000 to 170,000 Hindus, a community that includes long-settled Tamil families, newer IT professionals on Blue Card visas, and university students. Until recently, most had no large-scale temple to visit. The smaller Sri-Mayurapathy-Murugan-Tempel in Berlin's Britz neighbourhood opened in 2014 as the city's first Hindu temple, but the Ganesha temple operates on a different scale entirely.

For the families who spent two decades raising money and filing permits, the temple is a statement that permanence is possible. Diaspora institutions tend to be provisional — rented halls, weekend language classes, festival committees that form and dissolve. A 17-metre granite tower in the middle of a European capital is something else: a structure built to last centuries, by a community that plans to be around that long.

Doors at Hasenheide 106 open every day from 4 pm to 6 pm. There is no entry fee."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Banks Are Racing to Offer NRIs Up to 7.1% on Dollar Deposits. The RBI Engineered the Whole Thing.",
        "subheadline": "A central bank intervention designed to shore up the rupee has turned FCNR deposits into the hottest NRI financial product in a decade, with leverage potentially pushing returns past 20 per cent.",
        "slug": make_slug("rbi-fcnr-nri-deposit-rate-war-banks-dollar-returns"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "NRIs holding dollars in US or Gulf bank accounts now face a rare window — three-to-five-year FCNR deposits in Indian banks offering returns that rival equities, tax-free in India, with principal fully repatriable. The catch: the scheme closes September 30.",
        "tags": ["nri", "diaspora", "banking", "fcnr", "rbi", "investment", "rupee", "deposit-rates"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/some-lenders-hike-rates-fx-deposits-non-resident-indians-2026-06-11/"},
            {"name": "Mint", "url": "https://www.livemint.com/money/personal-finance/rbis-fcnr-move-opens-door-to-equity-like-dollar-returns-for-nris-11749555643421.html"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/money-and-banking/banks-hike-fcnrb-deposit-rates-to-attract-nri-funds-after-rbi-forex-swap-move/article69675917.ece"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/banking/sbi-icici-other-banks-hike-fcnr-deposit-rates"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5476028/pexels-photo-5476028.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Indian rupee notes and coins — NRI deposits are now at the centre of a central bank strategy to attract dollars",
        "image_attribution": "Pexels",
        "body": """On June 5, the Reserve Bank of India announced that it would absorb the full hedging cost on fresh Foreign Currency Non-Resident deposits — FCNR(B), in banking shorthand — with maturities of three to five years. Within days, nearly every major Indian bank had rewritten its rate card. By June 11, AU Small Finance Bank was offering 7.1 per cent on three-year dollar deposits. HDFC Bank had jumped to 6 per cent. ICICI was at 6.5 per cent. State Bank of India launched a new "SBI Advantage FCNR(B)" scheme with rates up to 6 per cent for deposits above a million dollars.

The numbers, on their own, are remarkable. A year ago, most FCNR dollar deposit rates hovered between 2.5 and 3.5 per cent — roughly what a US Treasury would pay. Now they are double that, and in some cases triple.

## Why the RBI Did It

The proximate cause is the rupee. Asia's second-worst-performing major currency this year, the Indian unit has fallen 6 per cent against the dollar, hitting record lows in May. Foreign portfolio investors have been pulling money out of Indian equities. The RBI's foreign exchange reserves, while still substantial, have been under pressure.

The FCNR scheme is, in effect, the central bank paying banks to attract NRI dollars. Under normal circumstances, an Indian bank accepting dollar deposits must hedge its currency exposure — converting dollars to rupees at today's rate while committing to return dollars at maturity. That hedging cost, typically 2 to 3 per cent annually, ate into the rates banks could offer depositors. By absorbing that cost through a concessional swap facility, the RBI has removed the single biggest drag on FCNR competitiveness.

The scheme is temporary. It runs until September 30, 2026, with an extended swap window through October 16 for deposits already booked. Fresh deposits are exempt from statutory reserve requirements — the CRR and SLR mandates that normally lock up a portion of bank funds — making them even more attractive to lenders.

## The Leverage Play

What has really caught the attention of private bankers and wealthy NRIs is not the headline rate but the leverage.

The RBI's guidelines explicitly allow Indian banks to issue Standby Letters of Credit to offshore banks, which can then lend to NRI clients against those guarantees. The borrowed funds get deposited back into the Indian bank's FCNR scheme. According to calculations by Emkay Global Financial Services, an investor placing $1 million of their own money and leveraging it nine times could generate annual returns of about $220,000 — a return of 21.8 per cent on the original capital. At a more conservative five-times leverage, returns still work out to roughly 15 per cent.

These are equity-like numbers from what is technically a fixed-income product. The principal is fully repatriable. Interest income on FCNR deposits is tax-exempt in India.

## How Much Will Flow In?

Estimates vary. SBI's research team projects $40 to $45 billion. Outlook Business, citing unnamed experts, puts the figure at $60 to $70 billion. The 2013 precedent — the last time the RBI ran a similar scheme — brought in $34 billion in a few months. The current package is more generous.

The competition among banks is already fierce. Kotak Mahindra is at 6.15 per cent for large deposits. Bank of Baroda is offering 6 per cent on dollars, 5.15 per cent on Canadian dollars, and 4.75 per cent on pounds and Australian dollars. Karur Vysya Bank jumped to 7 per cent from 2.63 per cent — a 437-basis-point increase overnight. Tamilnad Mercantile Bank made a similar leap.

## What NRIs Should Watch

The window is short. Deposits must be booked by September 30. There is a mandatory one-year lock-in period, and the minimum maturity is three years. The scheme is available in any freely convertible currency, but the RBI's swap facility is dollar-only — meaning rates on other currencies will be lower.

For NRIs holding substantial dollar savings in US bank accounts earning 4 to 5 per cent, the arithmetic is straightforward. For those with access to leverage through their overseas banking relationships, the numbers become genuinely unusual.

The risk, as always with Indian financial products, is the rupee itself. If the currency depreciates further over the deposit term, dollar-denominated returns could shrink when converted back. But with the deposit denominated in dollars and the principal fully repatriable in dollars, the currency risk is the RBI's problem, not the depositor's.

The scheme closes in 109 days. The rate war is already under way."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Fifty Years of Chariots on Fifth Avenue: New York's Ratha Yatra Marks a Half-Century of Krishna in America",
        "subheadline": "What began as a handful of Hare Krishna devotees pulling a homemade chariot through Manhattan in 1976 has become one of the city's longest-running religious processions — and a barometer of how deeply Indian spiritual traditions have rooted in American soil.",
        "slug": make_slug("nyc-ratha-yatra-50th-anniversary-iskcon-fifth-avenue"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The NYC Ratha Yatra's 50th anniversary reflects a half-century arc of Indian spiritual culture embedding in America — from counterculture curiosity to mainstream cultural institution, with the festival now drawing as many first-generation Indian professionals and families as it does Western-born devotees.",
        "tags": ["nri", "diaspora", "ratha-yatra", "iskcon", "new-york", "hare-krishna", "culture", "festival"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "ISKCON NYC", "url": "https://iskconnyc.com/event/nyc-ratha-yatra-hare-krishna-festival/"},
            {"name": "Eventbrite", "url": "https://www.eventbrite.com/e/hare-krishna-festival-nyc-50th-anniversary-tickets"},
            {"name": "Festival of India Tour", "url": "https://www.festivalofindia.org/2026-hare-krishna-festival-tour-tentative-schedule/"},
            {"name": "The Pluralism Project, Harvard University", "url": "https://pluralism.org/krishnas-chariot-festival"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Rath_Yatra_or_Festival_of_Chariot_in_CT%2C_USA.jpg/1280px-Rath_Yatra_or_Festival_of_Chariot_in_CT%2C_USA.jpg",
        "image_caption": "Devotees pull a Ratha Yatra chariot through a street in the United States",
        "image_attribution": "Wikimedia Commons",
        "body": """On Saturday, June 13, three towering chariots draped in red and green silk will roll down Fifth Avenue from East 45th Street, pulled by hundreds of hands gripping thick ropes. By noon, the procession will reach Washington Square Park, where a festival of kirtan, dance, vegetarian feasting, and cultural performances will run until evening. It is the New York City Ratha Yatra — the Festival of Chariots — and this year marks its 50th anniversary.

The numbers alone tell a story. What started in 1976 with a single homemade chariot and a small band of Hare Krishna devotees has grown into one of Manhattan's longest-running religious processions. ISKCON New York City, which organises the festival from its Brooklyn headquarters on Schermerhorn Street, describes this year's edition as "one of the largest and most successful Ratha Yatras in ISKCON."

## What Ratha Yatra Is

Ratha Yatra originates in Puri, Odisha, where the festival of Lord Jagannath — "Lord of the Universe" — has been celebrated for centuries. The deities of Jagannath, his sister Subhadra, and brother Balarama are placed on massive wooden chariots and pulled through the streets by devotees. The theological point is simple and radical: God leaves the temple to go out among the people.

The tradition was brought to the West by A.C. Bhaktivedanta Swami Prabhupada, the founder of the International Society for Krishna Consciousness. The first Western Ratha Yatra took place in San Francisco in 1967. New York's followed nine years later, and the festival has not missed a year since.

## Three Days in Manhattan

This year's celebrations span June 12 to 14. The schedule opens with an ecstatic kirtan session at Times Square on Thursday evening — chanting and dancing at what ISKCON calls "the Crossroads of the World." The main festival on Saturday begins with the Fifth Avenue chariot parade at 11 a.m. and continues at Washington Square Park from noon to 7 p.m., with a free vegetarian feast, artisan vendors, cultural performances, and spiritual dramas.

Sunday closes the weekend with a Kirtan Mela and open house at the ISKCON temple in Brooklyn.

The festival is free, ticketed only for tracking purposes on Eventbrite. The vegetarian feast — a tradition as old as the festival itself — is served to every attendee at no charge.

## From Counterculture to Community Anchor

The Ratha Yatra's demographic transformation over five decades mirrors the Indian diaspora's own arc in America. In the 1970s and 1980s, the festival's core audience was largely Western converts drawn to Krishna Consciousness through the counterculture. The crowd at Washington Square Park was predominantly white, with saffron-robed devotees outnumbering Indian-born attendees.

That ratio has quietly reversed. Today's Ratha Yatra draws substantial numbers of first-generation Indian professionals and their families — software engineers from Jersey City, doctors from Long Island, students from NYU and Columbia — alongside the ISKCON faithful. For many Indian Americans, the festival serves a function that has little to do with ISKCON as an institution: it is one of the few large-scale, public Hindu celebrations in the city, a place where children can see their religious traditions occupying public space in a way that feels both ancient and unmistakably New York.

## The Broader Circuit

New York is one stop on a North American Ratha Yatra circuit that now spans the continent. The 2026 schedule includes confirmed festivals in Atlanta, Harrisburg, Boston, Montreal, Toronto, Vancouver, Los Angeles, Redmond, San Francisco, and Philadelphia, running from May through October. Calgary's Ratha Yatra falls on June 21. The Baltimore celebration marks the 50th anniversary of Lord Jagannath's installation at that temple.

The circuit's growth reflects something broader than ISKCON's institutional reach. Hindu festival culture in North America has expanded dramatically in the past decade, driven less by missionary zeal than by demographic weight. The Indian-born population in the United States has roughly doubled since 2010, and with it has come demand for the kind of large-scale public religious observance that was once confined to Puri, Kolkata, and Ahmedabad.

Fifty years ago, a chariot on Fifth Avenue was an oddity — exotic enough to draw curious onlookers, strange enough to make the evening news. Today, it is part of the city's cultural furniture, as familiar to New Yorkers as the Puerto Rican Day Parade or the Feast of San Gennaro. That ordinariness, more than any anniversary milestone, is what the past half-century has built."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
