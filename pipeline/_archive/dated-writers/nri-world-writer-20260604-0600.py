#!/usr/bin/env python3
"""NRI World Writer — 2026-06-04 06:00 UTC run"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# ── Supabase credentials ────────────────────────────────────────────
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


# ════════════════════════════════════════════════════════════════════
# ARTICLE 1: Surati Holi Hai 2026 in Jersey City
# ════════════════════════════════════════════════════════════════════

article1_body = """The East Coast's largest Holi celebration is returning to the Jersey City waterfront this Saturday, and the organisers have a point to make: the festival of colours no longer needs an Indian neighbourhood to thrive. It needs a skyline.

Surati Holi Hai — run by Surati for Performing Arts — will take over Exchange Place on June 6, from noon to 8 PM. Thousands of attendees from New York, New Jersey, Connecticut and beyond are expected to stream into the waterfront plaza for an eight-hour programme of live music, dance, colour play, and a cultural marketplace that has become a fixture of the tri-state Indian calendar.

## Artists Fly In From India

This year's edition has pulled off something most diaspora festivals struggle with: headline acts from India who aren't just Bollywood playback names on a nostalgia circuit. Sumit Roy — known as the "Man with the Golden Voice" and the Calypso King — arrives alongside composer-filmmaker Rajesh Roy and multilingual playback singer Pritha Majumdar. The three are also performing as the Surati Baul Blues Band at the Voices International Festival at White Eagle Hall on Thursday night, a cross-genre set blending Baul folk traditions with blues that nods to the festival's broader ambition: positioning Indian culture as a participant in global arts, not a heritage exhibit.

Live performances run from noon to 3 PM. The remaining five hours are built around the communal colour play, food stalls, and the kind of unstructured social mixing that organisers say has always been the festival's real purpose.

## More Than a Festival

Rimli Roy, the artistic force behind Surati for Performing Arts, founded the organisation with a dual mandate: preserving Indian classical and folk arts in America, and using those traditions as a bridge to non-Indian communities. Holi — a festival whose primary ritual involves throwing coloured powder at strangers — is perhaps the most natural vehicle for that mission.

The festival's growth mirrors a broader pattern in the tri-state diaspora. Where community events once served primarily as gatherings for homesick first-generation immigrants, Holi Hai has become a fixture for second-generation Indian Americans, mixed families, and non-Indian New Yorkers who have adopted the celebration as their own. Exchange Place, with the Manhattan skyline as its backdrop, is a deliberate choice: a public, highly visible space that frames the event as a civic celebration rather than a community picnic.

## The Logistics of Joy

Jersey City has emerged as one of the most significant hubs for Indian cultural events on the East Coast. The city's Indian-origin population has grown steadily, and its waterfront venues offer the kind of open-air, transit-accessible space that Manhattan's congested event calendar cannot easily match. The PATH train delivers attendees from midtown Manhattan in under 20 minutes.

For the organisers, the logistical challenge is as much about managing tens of thousands of colour-dusted revellers as it is about maintaining artistic credibility. The festival has resisted the drift toward purely commercial Holi events — ticketed, DJ-driven, heavy on colour packets and light on culture — that have proliferated across American cities in the past decade.

Surati Holi Hai charges no entry fee. The colour is part of the programme, not the whole programme. And the performers are artists, not influencers.

The festival runs from 12 PM to 8 PM at Exchange Place, Jersey City. No tickets required."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Jersey City's Holi Hai Returns This Saturday. The East Coast's Biggest Colour Festival Has a Point to Make.",
    "subheadline": "Surati Holi Hai 2026 takes over Exchange Place with artists flown in from India, eight hours of programming, and free admission — a deliberate counterpoint to the ticketed, DJ-driven Holi events that have spread across American cities.",
    "slug": make_slug("jersey-city-holi-hai-surati-2026-east-coast-diaspora"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The festival embodies the second-generation diaspora's effort to transform Indian cultural traditions into civic celebrations that bridge communities — moving beyond nostalgia gatherings into mainstream public events.",
    "tags": ["nri", "diaspora", "holi", "jersey-city", "cultural-festival", "surati"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/surati-holi-hai-2026-returns-to-jersey-city/"},
        {"name": "Destination Jersey City", "url": "https://destinationjerseycity.com/surati-holi-hai-2026-returns-jersey-city/"},
        {"name": "Eventbrite", "url": "https://www.eventbrite.com/e/surati-holi-hai-color-festival-2026-tickets"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Lathmar_Holi_2022_in_Nandgaon%2C_Uttar_Pradesh_%28edited%29.jpg/1280px-Lathmar_Holi_2022_in_Nandgaon%2C_Uttar_Pradesh_%28edited%29.jpg",
    "image_caption": "Revellers celebrating Holi with coloured powder in Nandgaon, Uttar Pradesh",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip()
}


# ════════════════════════════════════════════════════════════════════
# ARTICLE 2: Kerala Pioneers NRI E-Ballot Voting
# ════════════════════════════════════════════════════════════════════

article2_body = """For decades, the right to vote has been the most expensive democratic privilege an NRI can exercise. In the 2024 Lok Sabha elections, more than 22,000 Kerala-origin NRIs flew home to cast their ballots — a round-trip that could cost anywhere from $800 to $2,500 depending on the departure city. The Election Commission of India has now decided that at least some of them should be able to skip the flight.

Kerala has been selected as the pilot state for India's first NRI e-ballot voting programme, targeting the 2026 assembly elections. Eligible overseas voters in the UAE, the United States, and Singapore will be able to cast their ballots electronically through a secure government portal, with physical return through Indian embassies. It is the most concrete step India has taken toward fulfilling a promise that NRI advocacy groups have been pushing for more than a decade.

## How It Works

The system adapts the existing e-postal ballot mechanism already used by armed forces personnel. The process runs in four stages:

First, registration. NRIs must be listed as overseas voters by submitting Form 6A through the Election Commission's website or through Indian embassies in their country of residence. A valid Indian passport and proof of current residence are required.

Second, application. After the election is notified, voters must inform the Returning Officer of their intent to use the e-postal ballot within five days.

Third, delivery. The Returning Officer sends the ballot electronically through a secure portal with two-factor authentication — OTP and PIN verification — designed to prevent duplication.

Fourth, the return. Voters download and mark their ballots, then return them with an attested declaration through Indian embassies or designated postal services. The ballots are segregated by constituency at the embassy level before dispatch to India.

## Why Kerala, and Why These Three Countries

Kerala was the obvious choice. The state's relationship with emigration is almost definitional — remittances from Gulf-based Keralites have been a cornerstone of the state's economy for half a century, and the Malayali diaspora is among the most politically engaged in India. The state consistently records some of the highest voter turnout rates in the country, and NRI voter registration has been steadily rising.

The UAE was selected for the sheer density of its Keralite population — an estimated 700,000 Indians in the UAE hail from Kerala. The United States and Singapore were chosen for logistical feasibility and the presence of robust Indian diplomatic infrastructure in both countries.

The Ministry of External Affairs has agreed to facilitate the process, provided the Election Commission arranges additional manpower at embassies to handle attestation and ballot collection — a detail that, in the typically understaffed world of Indian consular services, is not trivial.

## The Stakes

India has roughly 13 million registered NRI voters, but only a fraction have ever exercised that right because doing so requires physical presence in their home constituency on polling day. The Supreme Court affirmed NRIs' right to vote in 2014, but the practical infrastructure has lagged far behind the legal framework.

For Kerala's estimated 2.1 million NRIs, the pilot is personal. Assembly elections in the state are perennially tight — the 2021 election saw the LDF retain power with a margin that mattered in several constituencies. A significant NRI vote could shift that calculus in ways that no Indian election has ever accounted for.

The Election Commission has framed this as a pilot with potential for nationwide rollout. If the system works — if the security holds, if the embassies can handle the volume, if the return logistics function within the election timeline — the 2029 general election could look very different for the 35-million-strong Indian diaspora worldwide.

For now, the experiment begins in Kerala. The state that exports the most Indians may finally get to hear from them at the ballot box without requiring a plane ticket."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Kerala Will Let NRIs Vote From Abroad for the First Time. The Pilot Covers Three Countries and Could Change Indian Elections.",
    "subheadline": "India's Election Commission has selected Kerala for its first NRI e-ballot voting pilot, targeting overseas voters in the UAE, US, and Singapore for the 2026 assembly elections — the most concrete step yet toward fulfilling a decade-old promise.",
    "slug": make_slug("kerala-nri-e-ballot-voting-pilot-2026-assembly-election"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "For 13 million NRI voters who have been legally entitled to vote but practically unable to, remote voting could transform the diaspora from a remittance pipeline into a political constituency that Indian parties must actually court.",
    "tags": ["nri", "diaspora", "kerala", "voting", "election", "e-ballot", "political-participation"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "NRI Globe", "url": "https://nriglobe.com/nri-voting-rights-kerala-pioneers-e-ballot-pilot-for-2026-assembly-elections/"},
        {"name": "Election Commission of India", "url": "https://eci.gov.in/"},
        {"name": "The Hindu", "url": "https://www.thehindu.com/elections/kerala-assembly/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/5926271/pexels-photo-5926271.jpeg",
    "image_caption": "A voter casting their ballot at a polling station",
    "image_attribution": "Pexels",
    "body": article2_body.strip()
}


# ════════════════════════════════════════════════════════════════════
# ARTICLE 3: Indian American Philanthropy — Narrowing the Giving Gap
# ════════════════════════════════════════════════════════════════════

article3_body = """Indian Americans gave an estimated four to five billion dollars to charitable causes in 2024. A decade earlier, the number was roughly half that. The giving gap — the difference between what the community could donate based on its income and what it actually did — has shrunk from two to three billion dollars to just one billion. By any measure, this is one of the fastest philanthropic accelerations any American ethnic group has produced. The question is no longer whether Indian Americans give. It is where the money is going, and what it is building.

A landmark study released by Dalberg, Indiaspora, and the India Philanthropy Alliance in late 2025 — "From Closing the Gap to Setting the Standard" — laid out the numbers with unusual precision. The headline finding was the gap closure. But the more revealing data sat underneath: the giving increase was not simply a function of rising Indian American incomes, though those have climbed steadily. The primary driver was a deepened commitment to giving among higher-income donors, who now donate a larger share of their income than the US average.

## Three Billion to American Universities

The most visible concentration of Indian American philanthropy has been in higher education. Publicly tracked donations to US universities by Indian American donors have crossed three billion dollars, according to Indiaspora's ongoing tracking. The money flows overwhelmingly into three fields: medical and health sciences, engineering, and business education — a pattern that mirrors the professional concentrations of the community itself.

But a quieter line item may matter more in the long run. Over twelve per cent of tracked gifts — more than 140 million dollars — have gone toward cultural programming: South Asian studies departments, Hindu studies chairs, and centres for Indian civilisational research. Sumir Chadha's donation to Princeton established the Chadha Center for Global India. Chandrika Tandon's gifts to NYU endowed a school of engineering that carries her name. These are not vanity projects. They are bets on institutional permanence — the kind of infrastructure that ensures a community's story is told on its own terms, in the places where American elite opinion is formed.

## Geography Is Shifting

For years, Indian American philanthropy was concentrated on the coasts — Stanford, MIT, Harvard, Columbia. The Dalberg report documents a deliberate expansion. Monte Ahuja has championed Ohio universities. Satish and Yasmin Gupta have directed substantial giving to Texas institutions. Kiran and Pallavi Patel have reshaped medical education funding in Florida. Deepak Raj and Niraj Shah have added to the portfolio of donors whose giving footprint extends well beyond the traditional coastal corridors.

This geographic diversification tracks the community's own dispersal. Indian Americans are no longer concentrated solely in the Bay Area, the New York metro, and the D.C. suburbs. As the community has spread into the Sun Belt, the Midwest, and the South — drawn by tech hubs in Austin, healthcare in Houston, and lower costs of living everywhere — the philanthropy has followed.

## India Giving Day and the Infrastructure of Generosity

The acceleration did not happen spontaneously. Indiaspora, the India Philanthropy Alliance, and a network of community organisations have spent a decade building what amounts to a philanthropic infrastructure: events, peer networks, giving pledges, and data that makes the community's contributions visible to itself.

India Giving Day — held annually in early March — has become a focal point for this effort. The 2026 edition drew participation from donors across income levels, and Indiaspora has increasingly positioned the event not as a fundraiser but as a cultural assertion: Indian Americans give, and they should give visibly, systematically, and at a scale commensurate with their economic success.

Alex Counts, executive director of the India Philanthropy Alliance, framed the gap closure as a generational milestone. "For years, closing the vast philanthropic gap seemed unachievable," he said. "Seeing the deficit drop to just one billion is a testament to what coordinated action, data, and community leadership can accomplish."

## The Last Billion

The remaining one-billion-dollar gap is, by the report's own analysis, the hardest to close. It sits among middle-income donors — professionals earning between 150,000 and 400,000 dollars — who give, but at rates below the national average for their income bracket. The reasons are structural rather than cultural: many are first-generation immigrants still building wealth, remitting money to family in India, and navigating the peculiar American landscape of nonprofit giving that has no real equivalent in the Indian context.

For the diaspora, the philanthropy story is ultimately about something larger than tax-deductible donations. It is about whether a community that has achieved extraordinary economic success in America will build the institutions — cultural, educational, civic — that translate wealth into lasting influence. Three billion dollars to universities is a start. The question is what comes after the endowments."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Indian Americans Have Given $3 Billion to US Universities. The Giving Gap Is Down to Its Last Billion.",
    "subheadline": "A decade of coordinated effort has nearly tripled Indian American charitable giving to an estimated $4-5 billion a year. The philanthropy is diversifying — from coastal elite campuses to Midwest and Sun Belt institutions — and the community is now giving at rates above the national average.",
    "slug": make_slug("indian-american-philanthropy-giving-gap-universities-diaspora"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Indian American philanthropy has shifted from remittance-era giving to institutional endowment — building the cultural and educational infrastructure that translates economic success into lasting civic influence in America.",
    "tags": ["nri", "diaspora", "philanthropy", "education", "universities", "giving", "indiaspora"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Dalberg / Indiaspora / IPA", "url": "https://dalberg.com/our-ideas/indian-american-philanthropy-narrows-giving-gap/"},
        {"name": "Indiaspora", "url": "https://indiaspora.org/from-migration-to-endowment-diaspora-support-for-education/"},
        {"name": "PR Newswire / Financial Content", "url": "https://markets.financialcontent.com/stocks/article?storyId=0502240800en-2"},
        {"name": "India Philanthropy Alliance", "url": "https://www.indiapa.org/"}
    ]),
    "score_total": 74,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/7972508/pexels-photo-7972508.jpeg",
    "image_caption": "Students at an American university campus",
    "image_attribution": "Pexels",
    "body": article3_body.strip()
}


# ── Publish ──────────────────────────────────────────────────────────
articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
