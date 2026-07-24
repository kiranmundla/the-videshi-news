#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-06-05 10:00 UTC run"""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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


# ── ARTICLE 1: US Student Visa Tightening ──────────────────────────────

art1_body = """The U.S. Embassy in India dropped a blunt warning on X last Saturday that landed like a cold splash of water on every Indian visa holder's timeline: "U.S. visa screening does not stop after a visa is issued. We continuously check visa holders to ensure they follow all U.S. laws and immigration rules — and we will revoke their visas and deport them if they don't."

The statement is the sharpest public articulation yet of a policy shift that has been gathering force since mid-2025. Taken together with two other recent moves — a proposed rule to eliminate the "Duration of Status" framework for F-1 student visas, and a mandate that all student and exchange visa applicants set their social media profiles to public — the message is unmistakable: the era of flexible, trust-based immigration for Indian students in America is narrowing fast.

## The Duration of Status Bombshell

On May 5, the Department of Homeland Security proposed scrapping the Duration of Status (D/S) framework that has governed F-1 visas for decades. Under the current system, international students can remain in the U.S. as long as they maintain valid student status and comply with visa conditions — no fixed end date, no clock ticking.

The proposed replacement: a hard four-year admission cap. Any extension — whether for continued studies, Optional Practical Training, or Curricular Practical Training — would require formal approval from USCIS, the same bureaucracy already infamous for multi-year backlogs on H-1B petitions.

"The duration of status rule that has been proposed is going to fundamentally change the flexibility that students have had to apply for OPT and CPT," said Danielle Goldman, co-founder and CEO of Build, an immigration advisory firm. She warned that thousands of Indian professionals in AI, machine learning, and software engineering could face sudden uncertainty if the Day 1 CPT pathway — a lifeline for those who fail the H-1B lottery — becomes significantly harder to access.

A related proposal would cut the post-status grace period from 60 days to 30, halving the window graduates have to secure alternative visa sponsorship after their student status ends.

## Social Media Under the Microscope

Since June 2025, every F, M, and J visa applicant has been required to set all social media accounts to "public" before their consular interview. Consular officers now conduct what the State Department calls "comprehensive and thorough vetting" of an applicant's entire online presence — not just social media, but search results, databases, and anything that surfaces a "hostile attitude toward U.S. citizens, culture, government, institutions, or founding principles."

Officers screenshot and record anything flagged. Posts from up to five years ago can trigger a visa denial. Even keeping a profile private can be treated as evasive behavior and result in a refusal under Section 221(g) of the Immigration and Nationality Act.

## Why NRIs Should Care

India sends more students to the U.S. than any country except China. In the 2024-25 academic year, over 330,000 Indian students were enrolled at American institutions. Many of their parents — NRI professionals who built careers in the U.S. — helped fund those degrees with the implicit understanding that OPT, CPT, and the H-1B pipeline would eventually convert education into employment.

That pipeline is being squeezed from multiple directions simultaneously. The embassy's public warning signals that even approved visa holders face ongoing scrutiny, not just at the port of entry but throughout their stay. For NRI families with children approaching college age, the calculus around U.S. higher education is changing in real time.

Goldman put it plainly: "The companies will either struggle because they won't have the talent or they will have to get creative and find alternate solutions." For Indian families caught in the middle, creativity is no longer optional — it is the only strategy left."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "America Is Tightening the Screws on Student Visas — and NRI Families Will Feel It First",
    "subheadline": "A proposed end to Duration of Status, mandatory social media screening, and an embassy warning that surveillance never stops: three moves reshaping the Indian student pipeline to the U.S.",
    "slug": make_slug("us-student-visa-tightening-nri-families"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Over 330,000 Indian students in the U.S. and their NRI families face a narrowing immigration pipeline — Duration of Status elimination, social media screening, and continuous post-approval surveillance could reshape the economics of American higher education for the Indian diaspora.",
    "tags": ["travel", "visa", "immigration", "students", "nri", "usa"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/02/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/04/us-embassy-in-india-warns-visa-holders/"},
        {"name": "CU Boulder ISSS", "url": "https://www.colorado.edu/isss/expanded-visa-vetting"},
        {"name": "U.S. State Department", "url": "https://travel.state.gov/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
    "image_caption": "An open passport displaying multiple visa stamps from various countries",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": art1_body.strip()
}


# ── ARTICLE 2: India's Spiritual Tourism Boom ──────────────────────────

art2_body = """Summit Hotels & Resorts has launched The Mandir Collection, a hospitality brand built entirely around pilgrimage destinations — and it is betting that the 1-in-5 Indians now planning faith-based or wellness trips will pay for proper rooms when they get there.

The first property, Summit Salasar — The Mandir Collection, will rise near the Salasar Balaji Temple in Rajasthan, one of the most visited Hanuman temples in northern India. The roughly 70-room property will include private pool villas, Satvik dining, temple assistance services, wellness programmes, and devotional evening activities. It is designed not just for the devout but for families, wellness seekers, and destination event guests.

"Spiritual travel in India is experiencing a massive boom," said Sumit Mitruka, CEO of Summit Hotels & Resorts. He cited industry projections that India's spiritual tourism economy could reach $135 billion by 2034.

## The Infrastructure Finally Catches Up

For decades, India's pilgrimage circuit has been defined by a jarring disconnect: temples of extraordinary beauty surrounded by accommodation that ranges from spartan dharamshalas to questionable lodges. NRIs visiting Varanasi, Tirupati, or the Char Dham have long navigated a gap between the spiritual experience they sought and the hospitality infrastructure available to support it.

That gap is closing from both ends. Indian Railways has expanded the Vande Bharat Express network to 100-plus routes, with deliberate priority given to temple towns — Ayodhya, Amritsar, Varanasi, Tirupati, Shirdi, and Vaishno Devi all now have semi-high-speed rail connections. IRCTC's Bharat Gaurav tourist trains run dedicated temple circuits, including a 10-day "Divine East Temple Tour" covering major eastern pilgrimage sites in a single curated trip.

On the hotel side, the action is no longer limited to Summit. IHG Hotels & Resorts recently reopened its InterContinental Chennai Mahabalipuram Resort, a reimagined luxury coastal property near the UNESCO-listed Shore Temple. The Leela is planning a Jaisalmer property, an 80-room desert resort with tented villas that doubles as a destination wedding venue. And Taj Hotels' IHCL has been quietly expanding its presence at heritage and pilgrimage destinations, with the Vivanta and SeleQtions brands now present at several temple towns.

## The NRI Pilgrimage Problem

For the Indian American diaspora, visiting ancestral temples has always been an exercise in logistical compromise. A family flying from Chicago to Tirupati budgets $2,000 per ticket, clears a 20-hour journey, and often arrives to find that the nearest decent hotel is a 45-minute drive away.

The new infrastructure changes that equation. Direct and improved air connectivity — Air India's expanding network, IndiGo's domestic coverage — means fewer missed connections at hub airports. Better trains mean the Delhi-Varanasi corridor that once required an overnight rattler now takes eight hours on a Vande Bharat. And branded hotels at pilgrimage destinations mean NRI families no longer have to choose between proximity to the temple and basic comfort.

The Amrit Bharat Express network, now 60 routes strong with 100 percent occupancy rates, has also opened budget rail travel on long-distance routes connecting pilgrimage sites to major cities. At roughly ₹500 per 1,000 kilometers, it offers NRI visitors a way to experience India's rail network without the chaos of general unreserved coaches.

## A $135 Billion Bet

The numbers behind the spiritual tourism push are striking. India's religious tourism already accounts for a significant share of domestic travel — the Kumbh Mela alone drew an estimated 400 million visitors across its 2025 cycle. Kedarnath and Badrinath in the Char Dham circuit see record pilgrim numbers each season, despite helicopter services currently strained by a fuel crisis linked to the Iran conflict.

What Summit, IHG, and their competitors are betting on is that this demand, historically served by informal and unbranded hospitality, is ready to formalize. The target audience is not the backpacker sleeping on temple floors — it is the NRI family that wants to introduce their American-born children to Varanasi's ghats without compromising on hygiene, safety, or comfort.

For the diaspora, the emergence of branded spiritual hospitality is not just a convenience upgrade. It is a signal that India's tourism infrastructure is finally catching up to the scale of its spiritual heritage — and to the expectations of the millions who left but never stopped coming back."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Spiritual Tourism Is Getting the Five-Star Treatment It Deserves",
    "subheadline": "Summit Hotels launches The Mandir Collection at pilgrimage destinations, joining a wave of branded hospitality that is finally closing the gap between India's sacred sites and the comfort NRI families expect.",
    "slug": make_slug("india-spiritual-tourism-five-star-hotels-mandir-collection"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRI families visiting ancestral temples have long navigated a gap between extraordinary sacred sites and inadequate lodging. Branded hotel chains like Summit, IHG, and The Leela are now building directly at pilgrimage destinations, transforming the economics and comfort of diaspora temple visits.",
    "tags": ["travel", "hotels", "spiritual-tourism", "pilgrimage", "india", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Restaurant India", "url": "https://restaurantindia.in/news/summit-hotels-launches-the-mandir-collection-spiritual-tourism"},
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/intercontinental-chennai-mahabalipuram-resort/"},
        {"name": "TravelPlusStyle", "url": "https://www.travelplusstyle.com/best-luxury-hotel-openings"},
        {"name": "Press Information Bureau", "url": "https://pib.gov.in/"}
    ]),
    "score_total": 75,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f4/Varanasi%2C_India%2C_Benares_ghats.jpg",
    "image_caption": "The ghats of Varanasi along the Ganges, one of India's most visited pilgrimage destinations",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": art2_body.strip()
}


# ── ARTICLE 3: Visa-Free Destinations With US Visa ─────────────────────

art3_body = """Here is a fact that most Indian passport holders with a valid U.S. visa do not fully appreciate: that blue stamp in your passport does not just get you into America. It unlocks visa-free or visa-on-arrival access to more than 15 countries, several of them prime summer destinations that are a short flight from major U.S. cities.

With airfares to India running steep this summer — a combination of the Iran conflict rerouting flights and reduced capacity across Indian carriers — NRI families looking for a break might find better value looking south and east rather than across the Atlantic.

## Mexico: The Easiest Win

Indian citizens holding a valid multiple-entry U.S. visa can enter Mexico visa-free for up to 180 days. No prior application, no embassy visit, no fee beyond the Visit Form (FMM) typically included in your air ticket price.

Cancun is a four-hour direct flight from Houston, three and a half from Miami. The Riviera Maya offers cenotes, Mayan ruins at Chichén Itzá and Tulum, and some of the Caribbean's best beaches at a fraction of what a comparable resort week costs in the U.S. Virgin Islands.

For NRI families, the food is worth the trip alone. Mexican cuisine shares more DNA with Indian cooking than most people realize — the same reverence for chili, cumin, cilantro, and slow-cooked meats. Vegetarian options are plentiful: think cheese quesadillas, bean burritos, elote, and fresh guacamole at every turn.

Practical note: carry a printed copy of your hotel reservation and return flight. Airline staff at check-in occasionally ask for proof of accommodation, even though Mexico does not formally require it.

## The Caribbean: More Options Than You Think

Several Caribbean nations offer visa-free entry to Indian passport holders traveling with a valid U.S. visa:

**Costa Rica** allows stays of up to 90 days. The country is a nature paradise — cloud forests, volcanoes, Pacific and Caribbean coastlines within a few hours of each other. San José is a direct flight from many U.S. hubs.

**Panama** offers 30 days visa-free. The Canal, Casco Viejo's colonial old town, and the San Blas Islands are underrated. Tocumen Airport in Panama City is also one of the Americas' best-connected hubs, making it a natural stopover.

**Belize** grants 30 days. Think the Great Blue Hole, Mayan ruins at Xunantunich, and the world's second-largest barrier reef. It is one of the few Caribbean countries where English is the official language, which simplifies everything from restaurant menus to emergency situations.

**The Bahamas, Jamaica, Barbados, and Aruba** all have varying entry rules that generally favor holders of valid U.S. visas, though the specifics depend on your passport and the length of stay. Check the specific country's immigration website before booking.

## Asia-Pacific Gems

**The Philippines** allows Indian citizens with a valid U.S. visa to enter visa-free for 30 days. The beaches of Palawan and Cebu rival anything in Thailand or Bali, at significantly lower prices. Manila is a hub for cheap intra-Asia flights if you want to extend your trip.

**South Korea** recently extended its visa fee waiver for Indian group tourists through June 2026. Green card holders can enter without a visa entirely. Seoul's food scene, K-culture infrastructure, and proximity to Japan make it an increasingly popular NRI destination.

**Georgia** — the country, not the state — offers Indian green card holders visa-free entry for up to a full year. Tbilisi is one of Europe's most underrated cities: stunning architecture, extraordinary food, and wine country that predates French viticulture by several thousand years. Flights from Istanbul are under three hours.

## The Smart Play for Summer 2026

With India-bound flights expensive and overbooked, and the monsoon making large parts of the subcontinent less than ideal for family holidays through September, the smartest summer move for many NRI families may be to look at destinations their U.S. visa already covers.

A week in Cancun for a family of four can run $3,000-4,000 all-in, including flights from Texas or Florida. The same family flying SFO-DEL return this July is looking at $1,200-1,500 per person in economy, before a single hotel night or domestic flight in India.

The math is not subtle. And the destinations are often better suited to American-raised kids who want beaches, snorkeling, and Instagram-worthy ruins rather than another 14-hour flight to Nani's house in the July heat.

Keep your passports current, confirm your U.S. visa validity, and start searching flights to Cancun. Your kids will thank you."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Your US Visa Unlocks 15 Countries This Summer — Here's the NRI Cheat Sheet",
    "subheadline": "Mexico, Costa Rica, the Philippines, and a dozen more destinations offer visa-free entry to Indian passport holders with a valid American visa. With India flights running expensive, the smartest summer trip might be south of the border.",
    "slug": make_slug("us-visa-unlocks-15-countries-nri-summer-guide"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRI families facing steep India-bound summer fares can use their existing U.S. visa to access 15+ visa-free destinations including Mexico (180 days), Costa Rica (90 days), the Philippines (30 days), and Georgia (1 year for green card holders) — often at a fraction of the cost of a trip home.",
    "tags": ["travel", "visa-free", "mexico", "caribbean", "nri", "summer"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Voye Global", "url": "https://www.voyeglobal.com/blog/countries-indians-can-visit-with-us-visa/"},
        {"name": "Marble Law", "url": "https://marble.co/resources/posts/where-can-green-card-holders-travel-without-a-visa"},
        {"name": "Ease India Trip", "url": "https://www.easeindiatrip.com/blog/south-korea-visa-fee-waiver-indian-group-tourists/"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/20210498/pexels-photo-20210498.jpeg",
    "image_caption": "Aerial view of Cancun's turquoise coastline and beachfront resorts along the Caribbean",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": art3_body.strip()
}


# ── INSERT ──────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
