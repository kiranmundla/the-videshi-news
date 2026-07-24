#!/usr/bin/env python3
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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Marriott's 10,000th Hotel Is a Tiger Safari Lodge in Rajasthan — and NRIs Should Take Note",
        "subheadline": "The JW Marriott Ranthambore Resort & Spa marks a historic milestone for global hospitality — and signals that India's wildlife destinations are now firmly in the luxury lane.",
        "slug": make_slug("jw-marriott-ranthambore-10000th-hotel-nri-safari"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs visiting family in Jaipur or Delhi can now add a luxury weekend safari to their itinerary, and Marriott Bonvoy points earned on US stays transfer directly to this property.",
        "tags": ["travel", "hotels", "rajasthan", "wildlife", "luxury"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Marriott International", "url": "https://news.marriott.com/news/2026/06/11/marriott-international-celebrates-10000-properties-globally"},
            {"name": "Travel Pulse Canada", "url": "https://www.travelpulse.ca/news/hotels-and-resorts/marriott-unveils-10000th-property-with-opening-of-jw-marriott-in-india"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/marriott-international-celebrates-global-growth-with-iconic-jw-marriott-ranthambore-launch/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/7f/Ranthambore_National_Park.JPG",
        "image_caption": "Ranthambore National Park in Rajasthan, home to India's most photographed Bengal tigers",
        "image_attribution": "Wikimedia Commons",
        "body": """Marriott International has opened its 10,000th property worldwide — and the fact that it chose Rajasthan to mark the milestone says as much about India's luxury travel ambitions as it does about the hotel chain's growth.

The JW Marriott Ranthambore Resort & Spa, located a short drive from Ranthambore National Park in southeastern Rajasthan, officially opened this week with 127 rooms, including private villas, suites, and guestrooms designed around the surrounding wildlife corridor. The resort offers curated safari excursions into the park, where visitors can spot Bengal tigers, leopards, sloth bears, and over 300 bird species alongside elevated dining featuring modern Indian cuisine and locally inspired botanical cocktails.

## Why the 10,000th Matters

Marriott was a nine-seat root beer stand 99 years ago. That it now operates properties across 146 countries and territories — and chose India for this particular benchmark — reflects a deliberate bet on the country's premium hospitality market. The JW Marriott brand alone now spans more than 130 properties globally, and India accounts for a growing share of Marriott's Asia-Pacific expansion.

"Marking this accomplishment with a property carrying the JW Marriott brand is especially meaningful given its naming after our co-founder, J. Willard Marriott," said Marriott International President and CEO Anthony Capuano at the opening ceremony, which was attended by Chairman David Marriott and Rajeev Menon, President of the Asia Pacific excluding China division.

## The NRI Play

For Indian Americans, the opening reshapes what a trip home can look like. Ranthambore is roughly five hours by road from Jaipur and six from Delhi — manageable additions to any family visit. Until recently, Indian wildlife lodges operated at a very different standard from what NRI travelers expected. That gap is closing fast.

The practical upside is significant: Marriott Bonvoy members — and there are millions of Indian Americans enrolled — can redeem points earned at Courtyard by Marriotts and Westins across the US directly at this property. A weekend tiger safari booked on accumulated business travel points is a compelling proposition that did not exist at this quality tier in India a decade ago.

The resort also sits within striking distance of Rajasthan's heritage circuit. Guests can combine safari mornings with afternoon drives to the 10th-century Ranthambore Fort, a UNESCO World Heritage Site, or the stepwells and temples dotting the Sawai Madhopur district.

## India's Wildlife Luxury Moment

The opening is part of a broader trend. India's five-star hotel bookings surged over 100% in the past year, driven by both domestic demand and returning diaspora visitors. Rajasthan alone added several high-end properties in 2025-2026, including an Oberoi in Khajuraho and a Japanese-inspired Ananta resort in Jaipur.

Wildlife tourism, in particular, has entered a new phase. Ranthambore's tiger population has stabilized at around 80, up from fewer than 25 two decades ago — a conservation success story that has made the park one of India's most reliable safari destinations. The arrival of a globally recognized luxury brand adds infrastructure and visibility that benefits the entire corridor.

For NRIs who have exhausted the Golden Triangle and are looking for a reason to extend their next India trip, Marriott's bet on Ranthambore is a clear invitation: India's wild side now comes with turndown service."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Sarnath Could Become India's 45th UNESCO World Heritage Site Next Month — Here's What That Means for NRIs",
        "subheadline": "India's nomination of the ancient Buddhist site near Varanasi will be reviewed at the UNESCO World Heritage Committee session in Busan this July, potentially reshaping heritage tourism in one of the diaspora's most visited cities.",
        "slug": make_slug("sarnath-unesco-world-heritage-nomination-varanasi-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Varanasi is among the top pilgrimage and heritage destinations for the Indian diaspora, and UNESCO recognition for Sarnath would boost infrastructure, access, and international visibility for a city NRIs already visit frequently.",
        "tags": ["travel", "heritage", "unesco", "varanasi", "buddhism"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "UNESCO", "url": "https://whc.unesco.org/en/sessions/48COM/"},
            {"name": "Manorama Yearbook", "url": "https://www.manoramayearbook.in/current-affairs/india/2026/06/11/busan-to-host-48th-session-of-unesco-world-heritage-committee.html"},
            {"name": "United Nations India", "url": "https://india.un.org/en/282167-unesco-world-heritage-committee-concludes-historic-session-india"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Dhamek_Stupa%2C_Sarnath.jpg/1280px-Dhamek_Stupa%2C_Sarnath.jpg",
        "image_caption": "The Dhamek Stupa at Sarnath, where the Buddha delivered his first sermon after enlightenment",
        "image_attribution": "Wikimedia Commons",
        "body": """The 48th session of the UNESCO World Heritage Committee opens in Busan, South Korea on July 20, and tucked into the agenda is a nomination that should matter to every NRI who has ever made the trip to Varanasi: India has put forward the Ancient Buddhist Site at Sarnath for inscription on the World Heritage List.

If approved, Sarnath would become India's 45th World Heritage property — and only the second in Uttar Pradesh after the Taj Mahal. For a site where Siddhartha Gautama delivered his first sermon after attaining enlightenment, the recognition is arguably overdue.

## What Sarnath Actually Is

Sarnath sits about 13 kilometres northeast of Varanasi's old city, a 30-minute drive through increasingly congested roads that, in their current state, undersell what awaits. The archaeological complex includes the Dhamek Stupa, a massive cylindrical structure dating to 500 CE that marks the exact spot of the Buddha's first discourse; the Ashoka Pillar, whose four-lion capital became India's national emblem; and the ruins of monasteries that once housed thousands of monks during the Gupta period.

The site's museum, maintained by the Archaeological Survey of India, holds some of the finest examples of Mauryan and Gupta-era sculpture anywhere in the country. The polished sandstone Lion Capital of Ashoka — the original, not a replica — is displayed here, though most visitors to India never realize it exists outside of currency notes and government letterheads.

## Why UNESCO Status Changes the Equation

Heritage designation does not merely add a line to a plaque. In practice, it unlocks international conservation funding, compels infrastructure investment, and dramatically increases a site's visibility in global travel planning. India's existing 44 World Heritage Sites — from the Western Ghats to the Historic City of Ahmedabad — collectively draw millions of tourists and generate significant local revenue.

For Varanasi specifically, the timing is notable. Air India launched its Easy Connect service from Varanasi to Delhi this month, allowing passengers to complete immigration at Lal Bahadur Shastri International Airport before connecting to international flights. A UNESCO-listed Sarnath would give NRIs flying into Varanasi through this new system a second compelling reason to extend their stay beyond the ghats and evening aarti.

## The NRI Connection

Varanasi is already one of the most emotionally significant cities for the Indian diaspora. It draws NRIs for everything from pilgrimage and last rites to wedding ceremonies and family reunions. But Sarnath remains undervisited relative to its historical weight — partly because Varanasi's own gravitational pull keeps visitors at the ghats, and partly because the infrastructure connecting the two has lagged.

UNESCO inscription would change that calculus. The committee's 30 nominations this cycle include sites from Brazil, China, France, Japan, and Thailand, among others. India's bid is for a "cultural site" designation, which requires demonstrating outstanding universal value — a bar that Sarnath, as the birthplace of organized Buddhism, clears comfortably.

The committee's decision is expected by July 29. For the millions of NRIs who consider Varanasi a second home, Sarnath's elevation would add a layer of global validation to a city they already know is extraordinary — and perhaps finally bring the roads between the ghats and the stupa up to the standard the site deserves."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The World's Biggest Destination Wedding Summit Is Coming to India for the First Time — Thanks to NRI Spending",
        "subheadline": "The DWP Congress, which has previously convened in Florence, Lake Como, Bali, and Dubai, will hold its 17th edition at Fairmont Udaipur Palace this October — a recognition of India's dominance in the $400 billion luxury wedding market.",
        "slug": make_slug("dwp-congress-udaipur-destination-wedding-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRI weddings in India — particularly in Rajasthan — represent a multi-billion-dollar segment of the destination wedding industry, and the DWP Congress's arrival in Udaipur is a direct response to diaspora spending power.",
        "tags": ["travel", "weddings", "udaipur", "luxury", "rajasthan"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "DWP Congress", "url": "https://www.dwpcongress.com/"},
            {"name": "Breaking Travel News", "url": "https://www.breakingtravelnews.com/news/article/the-worlds-most-influential-destination-wedding-platform-arrives-in-india-for-the-first-time/"},
            {"name": "IndexBox", "url": "https://www.indexbox.io/blog/17th-dwp-congress-in-india-udaipur-to-host-global-wedding-planners-in-october-2026/"}
        ]),
        "score_total": 73,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Evening_view%2C_City_Palace%2C_Udaipur.jpg/1280px-Evening_view%2C_City_Palace%2C_Udaipur.jpg",
        "image_caption": "The City Palace complex in Udaipur at dusk, overlooking Lake Pichola",
        "image_attribution": "Wikimedia Commons",
        "body": """For 16 editions, the Destination Wedding Planners Congress has rotated through the world's most aspirational venues — Florence, Lake Como, Bali, Dubai, Phuket, Rhodes, Victoria Falls. The common thread: places where very wealthy people get married. That the 17th edition is heading to Udaipur, India for the first time is not just flattering. It is an acknowledgment of who is actually driving the global luxury wedding economy.

The DWP Congress 2026 will take place October 6-8 at the Fairmont Udaipur Palace, a sprawling 18-acre estate set against the Aravalli Hills with over 140,000 square feet of indoor and outdoor event space. More than 350 of the world's top destination wedding planners, luxury suppliers, hospitality leaders, and creative directors will gather for three days of business meetings, masterclasses, and cultural immersion.

## The Numbers Behind the Move

The global destination wedding industry is projected to exceed $400 billion by 2030. India is among the fastest-growing segments of that market, and the growth is not coming from domestic demand alone.

NRI weddings in India have become a category unto themselves. Indian American families routinely plan multi-day celebrations in Udaipur, Jaipur, Goa, and Kerala that rival or exceed the budgets of weddings in the Amalfi Coast or the French Riviera. A single NRI wedding in Rajasthan can generate $500,000 to $2 million in local spending across venues, catering, decor, entertainment, travel, and accommodation — with guest lists often exceeding 300 people flying in from three or more countries.

Sidh N.C., Director of QnA International, which organizes the DWP Congress, was explicit about the rationale: "India has long been the world's most celebrated canvas for luxury weddings, and Udaipur, with its timeless romance and regal grandeur, is the perfect stage for this chapter."

## Why Udaipur Keeps Winning

Udaipur's appeal to NRI wedding planners is not accidental. The city offers a combination that is genuinely difficult to replicate: lakeside palace venues with centuries of royal provenance, world-class hospitality infrastructure from operators like Taj, Oberoi, and now Fairmont, and a visual backdrop — the City Palace reflected in Lake Pichola at dusk — that photographs better than almost any other wedding destination on Earth.

The Fairmont Udaipur Palace itself features Jewel, one of India's largest ballrooms, the ceremonial gardens of Jashn Bagh, and the dramatic Chand Baori venue — spaces designed for exactly the kind of 400-person, three-day celebrations that NRI families favor. The property sits at the intersection of Rajputana grandeur and contemporary luxury, which is precisely the aesthetic that second-generation Indian Americans tend to seek: rooted but modern, traditional but not stuffy.

## What This Means for NRIs Planning Ahead

The DWP Congress itself is a trade event, not a consumer show. But its arrival in India has practical implications for NRIs in the wedding-planning pipeline. First, it will bring 350 of the world's best wedding professionals into direct contact with Indian venues and vendors, likely increasing the number of international planners who can competently execute Indian weddings. Second, the media attention will further normalize India as a premium destination — useful for NRI couples navigating in-law expectations about "why not just do it in New Jersey."

For context, past DWP Congress host cities — Lake Como, Bali, Dubai — all saw measurable increases in destination wedding bookings in the 12-18 months following the event. Udaipur, which already hosts an estimated 2,000 destination weddings annually, is positioned to see similar tailwinds.

The Indian wedding industry has been telling itself for years that it belongs on the global luxury stage. In October, the global luxury stage is coming to confirm it."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
