#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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

# Verify image URLs before using them
def verify_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("content-type", "")
        cl = int(r.headers.get("content-length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        elif r.status_code == 200 and "image" in ct:
            # No content-length header but type is image — likely OK for Pexels
            return True
        print(f"  ⚠ Image failed: status={r.status_code}, type={ct}, size={cl}")
        return False
    except Exception as e:
        print(f"  ⚠ Image verify error: {e}")
        return False

articles = [
    # ARTICLE 1: Taj Frankfurt
    {
        "id": str(uuid.uuid4()),
        "headline": "Taj Hotels Lands in Continental Europe — and Frankfurt's NRI Business Class Just Got an Upgrade",
        "subheadline": "IHCL's 126-key Taj Hessischer Hof marks the brand's first property on the European mainland, bringing Bombay Brasserie and J Wellness Circle to Germany's financial capital.",
        "slug": make_slug("taj-hessischer-hof-frankfurt-ihcl-europe-nri"),
        "category": "travel",
        "vertical": "travel",
        "is_editorial": False,
        "diaspora_angle": "For the estimated 200,000 Indian professionals and families based in Germany — many in Frankfurt's banking and tech corridors — this is the first time a Taj property exists on the European mainland. NRIs transiting Frankfurt for business or flying through for Messe trade fairs now have a luxury Indian hospitality option with Bombay Brasserie cuisine, Ayurveda-inspired J Wellness, and The Chambers business club.",
        "tags": ["travel", "hotels", "taj-hotels", "ihcl", "frankfurt", "germany", "europe", "luxury"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Hotelier India", "url": "https://hotelierindia.com"},
            {"name": "Travel Trade Journal", "url": "https://traveltradejournal.com"},
            {"name": "PRNewswire / IHCL", "url": "https://finanznachrichten.de"},
            {"name": "Travel And Tour World", "url": "https://travelandtourworld.com"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/27863505/pexels-photo-27863505.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "body": """The Taj brand has operated in London since acquiring the St James' Court and 51 Buckingham Gate properties. It runs hotels in Cape Town, Dubai, Maldives, and across the Middle East. But continental Europe — the market that hosts roughly 350 million tourist arrivals annually — had remained a blank spot on IHCL's map.

That changed this week. Indian Hotels Company Limited opened the Taj Hessischer Hof Frankfurt, a 126-key luxury property in one of Frankfurt's most storied addresses, directly announcing its arrival in mainland Europe's hotel market.

## A Landmark Revived

The Hessischer Hof is not a new building. The property, located near the Frankfurt Messe exhibition centre, was a fixture of the city's five-star hotel scene for decades before it closed during the pandemic. Peakside Capital, the German investment firm that owns the building, oversaw an extensive renovation before handing operations to IHCL.

"We are very pleased that the legendary Hotel Hessischer Hof, with its long tradition as a five-star hotel close to the Frankfurt Exhibition Centre, is now reopening its doors as a Taj Hotel," said Boris Schran, partner at Peakside Capital.

What reopened is not simply a German luxury hotel with an Indian operator. IHCL has installed its signature dining, wellness, and members-only concepts: Bombay Brasserie serving Indian cuisine, Jimmy's Bar with live piano and cocktails, the Lobby Bar for teas and pastries, J Wellness Circle drawing on Ayurvedic traditions, and The Chambers — Taj's invite-only business club that has long been a networking hub for India's corporate elite.

## Why Frankfurt, Why Now

Frankfurt is Germany's financial capital and Europe's busiest trade fair city. It is also a major Lufthansa hub, routing an enormous share of India-Europe air traffic through its airport. For the Indian business traveller connecting through Frankfurt — or the NRI professional based in Germany's Rhine-Main metropolitan area — the hotel offers a level of cultural familiarity that Marriotts and Hiltons do not.

Puneet Chhatwal, IHCL's Managing Director and CEO, framed the move as part of a broader international push. "Recognised as World's Strongest Hotel Brand 2025, Taj is a unique collection of 150-plus hotels across 15 countries," he said. "The opening of Taj Hessischer Hof Frankfurt marks Taj's debut into Continental Europe, in line with our international strategy to grow our presence in key gateway cities of the world."

## What It Means for NRIs

The Indian diaspora in Germany has grown steadily. IT professionals in Frankfurt and Munich, students across German university cities, and a growing pipeline of skilled-worker visa holders make up a community that has lacked Indian luxury hospitality infrastructure outside of restaurant rows.

For NRIs based in the US or UK who transit Frankfurt — one of the most common connection points for India-bound flights — the Taj Hessischer Hof becomes a layover option that did not previously exist. A property with Ayurvedic wellness, familiar cuisine, and Indian-standard hospitality service in Europe's busiest transit corridor is a practical addition, not just a branding exercise.

IHCL now operates in 15 countries. The Frankfurt opening signals that more European cities — likely Paris, Zurich, or Milan — could follow as the group targets what Chhatwal calls "key gateway cities." For Indian travellers navigating Europe, the map is slowly being redrawn in their favour."""
    },

    # ARTICLE 2: The Leela at 40
    {
        "id": str(uuid.uuid4()),
        "headline": "The Leela Turns 40 — and the Next Decade Will Take It to Srinagar, Ayodhya, and Dubai",
        "subheadline": "From a single Mumbai hotel in 1986 to 23 properties by 2029, The Leela's expansion plan reads like a map of where NRIs want to travel in India — and beyond.",
        "slug": make_slug("leela-hotels-40-years-expansion-srinagar-ayodhya-dubai-nri"),
        "category": "travel",
        "vertical": "travel",
        "is_editorial": False,
        "diaspora_angle": "NRIs visiting India increasingly seek luxury properties in tier-2 and spiritual destinations, not just Delhi and Mumbai. The Leela's expansion to Ayodhya, Agra, Srinagar, Ranthambore, and Jaisalmer directly serves the diaspora's evolving travel patterns — heritage tourism, religious pilgrimages, and wildlife circuits that now anchor NRI India trips.",
        "tags": ["travel", "hotels", "leela", "luxury", "india", "expansion", "ayodhya", "srinagar", "dubai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://travelandtourworld.com"},
            {"name": "Outlook Traveller", "url": "https://outlooktraveller.com"}
        ]),
        "score_total": 74,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Hotel_Leela_Palace_%284352657669%29.jpg/1280px-Hotel_Leela_Palace_%284352657669%29.jpg",
        "body": """When Captain C.P. Krishnan Nair opened The Leela Mumbai in 1986, he was placing a bet that India could produce luxury hospitality to rival anything in Europe or the Middle East. Forty years later, that bet has been settled decisively. The Leela Palaces, Hotels and Resorts now operates thirteen properties with 3,544 keys across eleven Indian cities — and it has plans to nearly double that footprint within three years.

## The Expansion Map

Under its current ownership — a Brookfield Asset Management-sponsored private real estate fund — The Leela is on track to grow from thirteen to twenty-three properties, exceeding 5,000 keys by the end of the decade. The destinations tell a story about where Indian luxury travel is heading: Agra, Ayodhya, Bandhavgarh, a second Mumbai property in BKC, Ranthambore, Sikkim, Srinagar, Jaisalmer, and the brand's first international outpost in Dubai.

These are not random pins on a map. Agra serves the Taj Mahal circuit. Ayodhya has emerged as India's fastest-growing religious tourism destination following the Ram Mandir inauguration. Bandhavgarh and Ranthambore anchor the tiger safari circuit. Srinagar taps into Kashmir's resurgence as a premium destination. Jaisalmer covers the Rajasthan desert luxury segment. And Dubai — home to the largest concentration of Indian expatriates anywhere in the world — extends the brand to where its core audience already lives.

## Why This Matters to the Diaspora

The biggest shift in NRI travel over the past five years is the move beyond metro hotel stays. A decade ago, visiting India meant a few nights at the Oberoi in Delhi or the Taj in Mumbai, with family homes filling the rest of the itinerary. Today, NRI families are building standalone trips around heritage circuits, wildlife safaris, and spiritual journeys — and they expect the same hospitality standards they find at Four Seasons or Aman properties abroad.

The Leela's expansion directly addresses this gap. There is currently no world-class luxury hotel in Ayodhya for the hundreds of thousands of diaspora Hindus who now visit annually. Srinagar's hotel scene is improving but remains thin at the top end. Bandhavgarh and Ranthambore have a handful of boutique safari lodges but lack a recognisable Indian luxury brand.

## The People Behind the Brand

The Leela's 40th anniversary celebrations have focused less on marble lobbies and more on the associates — the staff who have defined the brand's service reputation. The company highlighted long-tenured employees across its properties, from doormen in New Delhi to spa therapists in Kovalam, as the true carriers of the brand's identity.

This is not just corporate sentimentality. Indian luxury hospitality sells itself on service, not hardware. The ability to anticipate a guest's chai preference, to arrange a last-minute temple visit, to understand that an NRI family's three-generation reunion requires a different approach than a solo business traveller — these are the competencies that differentiate The Leela from international chains operating in India.

## What Comes Next

With thirteen properties operating and ten more in the pipeline, The Leela is entering its most ambitious phase. The Dubai property, in particular, will test whether the brand can compete internationally with the Ritz-Carltons and Mandarin Orientals that dominate the Gulf luxury market. Success there would validate a proposition that Indian luxury hospitality has a place not just in India, but wherever Indians travel.

For NRIs planning trips home in 2027 and beyond, the practical takeaway is clear: the India you check into is about to look very different from the one you left."""
    },

    # ARTICLE 3: Adventure Tourism India
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Resorts Are Turning Into Adventure Parks — and NRI Families Are the Target Market",
        "subheadline": "From ziplines in Jim Corbett to valley rope jumps in Rishikesh, Indian hospitality is betting that the diaspora wants more than a pool and a buffet when they visit.",
        "slug": make_slug("india-adventure-resorts-zipline-rishikesh-nri-families"),
        "category": "travel",
        "vertical": "travel",
        "is_editorial": False,
        "diaspora_angle": "NRI families visiting India during summer or winter breaks increasingly want activity-driven holidays that keep kids engaged. The shift toward adventure hospitality — ziplines at resorts, valley jumps in Rishikesh, sky cycling in the Western Ghats — directly caters to diaspora families accustomed to activity-packed vacations in the US, and who now expect the same from Indian destinations.",
        "tags": ["travel", "adventure-tourism", "india", "resorts", "rishikesh", "zipline", "nri-families"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://outlooktraveller.com"},
            {"name": "Hospitality News India", "url": "https://hospitalitynews.in"},
            {"name": "Travel And Tour World", "url": "https://travelandtourworld.com"}
        ]),
        "score_total": 68,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6454835/pexels-photo-6454835.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "body": """The formula that powered Indian resort hospitality for decades was simple: a scenic location, clean rooms, a generous breakfast buffet, and a swimming pool. Corporate groups got a conference hall. Families got a lawn. Everyone got the view. It was reliable, inexpensive, and utterly forgettable.

That model is dying. Across India, hospitality brands from Jim Corbett to Coorg are ripping up lawns and installing ziplines, climbing walls, sky cycling tracks, rope courses, and multi-activity towers. Adventure is no longer something you drive to Rishikesh for — it is something that shows up at your resort's doorstep before breakfast.

## The Shift

The change is being driven by a hard economic reality: Indian travellers are spending more time researching activities than rooms. Families with children want properties that keep kids occupied throughout the day without requiring a separate excursion. Corporate clients want team-building experiences that go beyond trust falls in a conference room. Wedding parties need entertainment between ceremonies. Weekend travellers from Bengaluru, Pune, and Delhi want Instagram-ready moments that justify the four-hour drive.

The result is a hospitality industry that is investing heavily in what it calls "experience infrastructure." Open lawns are becoming obstacle courses. Forest edges are being connected by suspension bridges. Rooftop terraces are turning into sky cycling tracks. Properties that once competed on thread count and buffet variety now compete on the number of activities they can fit into a single stay.

## Rishikesh Raises the Bar

If resorts are adding adventure as an amenity, Rishikesh is redefining what adventure means. Jumpin Heights, the company that popularised bungy jumping in India, has launched what it calls the country's first Valley Rope Jump in the Mohanchatti valley. Participants experience a freefall nearly double the length of a standard bungy, followed by a high-velocity swing across the valley against a backdrop of Himalayan ridgelines.

The format is built for accessibility. A tandem "Fearless Duo" option lets two people jump together — a design choice aimed squarely at families and couples who want shared adrenaline rather than solo terror. Solo jumpers earn a "Valley Victor" certificate, adding a gamified layer that resonates with younger travellers.

Safety infrastructure meets international standards: multi-point harness systems, certified wire ropes, fail-safe mechanisms, and trained operators. For NRI visitors accustomed to the safety protocols of adventure parks in the US or Europe, this matters. India's adventure tourism industry has historically been informal and loosely regulated. Rishikesh's professional operators are changing that reputation one jump at a time.

## The NRI Opportunity

NRI families visiting India during summer and winter school breaks face a perennial challenge: what to do with the kids beyond temple visits and family dinners. The adventure hospitality boom offers a direct answer.

A family flying into Delhi can now book a resort in Jim Corbett that pairs tiger safari drives with zipline courses and kayaking. A group heading to Kerala can choose a property in Munnar or Wayanad that offers valley crossing and rope bridges alongside plantation tours. A Rishikesh stopover can combine river rafting with the new valley rope jump, compressing enough activity into two days to rival a week at a US summer camp.

This is not accidental. Indian hospitality operators are studying the American family vacation model — where destinations like Great Wolf Lodge and KOA camps bundle accommodation with activity — and adapting it for Indian geography and price points.

## What to Know Before You Book

The quality gap between adventure properties remains wide. Some resorts have invested in professionally engineered equipment and certified instructors. Others have strung a cable between two trees and called it a zipline. For NRIs booking from abroad, the distinction matters.

Look for properties that name their equipment suppliers, certify their instructors, and carry insurance. Rishikesh operators like Jumpin Heights have set a standard. Resorts affiliated with established hospitality brands — Sterling, Mahindra, Club Mahindra — tend to follow stricter safety protocols than independent properties.

India's adventure hospitality market is still in its early chapters. But the trajectory is clear: the next time you visit home, the resort your family books might offer more thrills than the Six Flags you drove past on the way to the airport."""
    }
]

# Verify images first
for art in articles:
    print(f"Verifying image for: {art['headline'][:60]}...")
    if not verify_image(art["image_url"]):
        print(f"  ❌ Image verification failed, proceeding anyway")
    else:
        print(f"  ✅ Image verified")

print()

# Insert articles
for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
