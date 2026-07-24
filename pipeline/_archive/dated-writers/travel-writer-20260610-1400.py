#!/usr/bin/env python3
"""Travel writer — 2026-06-10 14:00 UTC run"""
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

now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


articles = [
    # ── Article 1: India MEA Middle East travel advisory for Gulf NRIs ──
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Issued Its Most Sweeping Middle East Travel Advisory — and Nine Million Gulf NRIs Are in the Crosshairs",
        "subheadline": "From Iran to the UAE, India's MEA is telling nationals to register with embassies, secure visa extensions, and prepare exit plans as airspace closures and conflict spillover make the Gulf the riskiest corridor in global aviation.",
        "slug": make_slug("india-mea-middle-east-travel-advisory-gulf-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Roughly 9 million Indians live and work in the Gulf — in the UAE, Saudi Arabia, Qatar, Kuwait, Bahrain, and Oman. This advisory is not abstract: it directly affects NRI workers, students, business travelers, and the hundreds of thousands of pilgrims who transit through the region every year. For NRIs in the US routing through Dubai or Doha to reach India, it also reshapes the calculus of which airline and which hub to book this summer.",
        "tags": ["travel", "middle-east", "gulf", "nri", "travel-advisory", "mea", "safety"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/39riqrq6bd0q/"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/uk-joins-us-russia-canada-india-australia-switzerland/"},
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/emirates-offer-incentives-safety-assurances-iran-war-hits-travel-2026-06-09/"},
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/a3/Hamad_International_Airport_Qatar.jpg",
        "image_caption": "Hamad International Airport in Doha, one of the world's busiest transit hubs for India-bound flights",
        "image_attribution": "Wikimedia Commons",
        "body": """India's Ministry of External Affairs has issued its most comprehensive Middle East travel advisory in years, covering virtually every country in the region — from Iran and Israel to the UAE, Saudi Arabia, Qatar, Kuwait, Bahrain, Jordan, and Lebanon. The directive, published June 9, goes beyond the standard "exercise caution" language. It explicitly tells Indian nationals in Iran to leave immediately, and instructs citizens across the rest of the Gulf to register with embassies, secure visa extensions, and prepare contingency exit plans.

The timing matters. The advisory lands as the US, UK, Canada, Australia, Russia, and Switzerland have all independently issued their own high-level warnings for the same region. The common thread: drone threats, airspace closures tied to the Iran conflict, and the risk of sudden military escalation spilling across borders that have, until now, felt functionally safe for civilians.

## Nine Million Indians, One Region

For the Indian diaspora, the Gulf is not a vacation destination — it is home. An estimated 9 million Indian nationals live and work across the six GCC states, constituting the largest expatriate community in most of them. In the UAE alone, Indians make up roughly 30% of the population. Saudi Arabia hosts over 2.5 million Indian workers. Qatar, Kuwait, Bahrain, and Oman each have Indian communities numbering in the hundreds of thousands.

These are construction workers, IT professionals, nurses, engineers, teachers, and entrepreneurs. Many have families with them. When India's MEA issues an advisory of this scope, it is not speaking to tourists browsing Lonely Planet. It is speaking to a population that has built lives, businesses, and communities in a region now classified as high-risk by nearly every major government on Earth.

## What the Advisory Actually Says

The guidance is country-specific and, in some cases, unusually blunt:

**Iran**: Indian nationals are urged to leave immediately through any available commercial or chartered transport. The embassy in Tehran has activated emergency hotlines. Students, pilgrims, and business visitors are told to avoid protests, political gatherings, and border regions.

**UAE and Qatar**: While both countries maintain "largely stable" civil infrastructure, the advisory warns of potential rapid changes in airspace status and security protocols. Embassy registration is strongly recommended. Visa extensions and consular assistance are available for those needing to adjust travel plans.

**Saudi Arabia**: Special emphasis on pilgrim safety. With Hajj season approaching, the MEA has flagged the need for pilgrims to maintain documentation, monitor local media, and follow embassy instructions. Saudi Arabia's proximity to active conflict zones makes contingency planning essential.

**Bahrain**: Newly added to the advisory for the first time, reflecting its proximity to escalating conflict zones. Travelers are warned of potential airspace disruptions and advised to register with the Indian embassy immediately.

**Jordan and Lebanon**: Elevated alert levels, with guidance to avoid border regions and non-essential travel entirely.

## The Airspace Problem

The advisory is not just about physical safety on the ground. It is fundamentally an airspace story. The Iran conflict has created a patchwork of restricted zones across the Gulf, forcing airlines to reroute flights, cancel services, and absorb punishing fuel costs. IATA projects global airline profits will fall nearly 50% this year — from $45 billion in 2025 to $23 billion — driven largely by Middle East disruptions.

For NRIs in the US, this has a direct impact on the India travel corridor. Emirates, Qatar Airways, and Etihad — the three Gulf megacarriers that have long dominated US-India routing — are all operating under stress. Emirates' president Tim Clark told Reuters that first-class cabins are running half-full, and the airline cannot drop fares because of elevated fuel costs. Qatar has confirmed that while its airspace remains open, some carriers are bypassing the Doha FIR through June 14. The European Union Aviation Safety Agency has issued conflict-zone warnings advising airlines against flying over parts of the Gulf.

For NRIs booking summer flights to India, the practical implications are clear: direct routes (United's Newark-Delhi, Air India's SFO-Delhi) are safer bets than Gulf connections, but also more expensive and harder to find seats on.

## What NRIs Should Do Now

The MEA's advisory includes a practical checklist that every Indian national in the Gulf — or transiting through it — should take seriously:

1. **Register with the nearest Indian embassy or consulate**. This is the single most important step. In an evacuation scenario, registered citizens get priority.
2. **Keep passports, visas, and identity documents accessible at all times**. Do not leave originals with employers or in office safes.
3. **Verify visa validity and explore extensions**. Indian embassies across the region are authorized to facilitate extensions and provide document assistance.
4. **Monitor local news and official advisories daily**. Conditions are changing faster than weekly check-ins can capture.
5. **Maintain emergency cash and health supplies**. ATM networks and pharmacies can become inaccessible during sudden security incidents.
6. **Avoid military zones, border areas, and political gatherings**. This applies even in countries classified as "stable."
7. **Have a contingency exit plan**. Know the nearest airport with active commercial service, and have a backup route if your primary carrier cancels.

The MEA advisory represents a decisive shift in tone. It is no longer asking citizens to "be careful." It is telling them to prepare for the possibility that they may need to leave — quickly, and through routes they have not planned for.""",
    },

    # ── Article 2: Malaysia Visit 2026 + visa-free for Indians ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Malaysia Just Rolled Out Its Biggest Tourism Push in a Decade — and Indians Don't Even Need a Visa",
        "subheadline": "Visit Malaysia 2026 is targeting 35.6 million visitors with enhanced visa arrangements for Indians, a freshly signed tourism MoU, and a pitch that could not be better timed as Gulf transit routes deteriorate.",
        "slug": make_slug("malaysia-visit-2026-visa-free-indians-nri-travel"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For NRIs in the US, Malaysia is a 4-hour flight from most Indian cities — making it the perfect add-on to a trip home. With visa-free entry, direct flights from Delhi, Mumbai, Chennai, Hyderabad, Bengaluru, and Kochi, and prices that make Bali look expensive, Malaysia is positioning itself as the default Southeast Asian getaway for the Indian diaspora. The timing is strategic: as Gulf layover routes become riskier and pricier, Kuala Lumpur is an increasingly attractive alternative hub.",
        "tags": ["travel", "malaysia", "visa-free", "southeast-asia", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/malaysia-joins-thailand-record-breaking-2026-tourism-campaigns/"},
            {"name": "Marketing Interactive", "url": "https://production.marketing-interactive.com/malaysia-and-india-sign-mou-to-strengthen-tourism-cooperation"},
            {"name": "Human Resources Online", "url": "https://www.humanresourcesonline.net/faqs-on-malaysia-immigration-visa-free-travel-for-chinese-and-indian-citizens"},
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Bukit_Bintang_junction_in_2024_2.jpg/3840px-Bukit_Bintang_junction_in_2024_2.jpg",
        "image_caption": "The Bukit Bintang shopping district in Kuala Lumpur, a hub of Malaysian tourism",
        "image_attribution": "Wikimedia Commons",
        "body": """Malaysia has launched Visit Malaysia 2026, the country's most ambitious tourism campaign since the pre-pandemic era, with a target of attracting 35.6 million international visitors. For Indian travelers, the pitch is unusually compelling: visa-free entry for up to 30 days, a freshly signed bilateral tourism agreement, and a destination that is closer, cheaper, and more culturally familiar than most alternatives in the region.

The campaign, spearheaded by Tourism Malaysia, comes with enhanced visa arrangements specifically targeting India and China — the two fastest-growing source markets for Malaysian tourism. It is backed by a comprehensive MoU signed between the tourism ministries of both countries, covering everything from medical tourism promotion to MICE (meetings, incentives, conferences, and exhibitions) cooperation and community-based eco-tourism development.

## The Visa-Free Advantage

India's visa-free arrangement with Malaysia, first introduced in December 2023 and extended through December 2026, allows Indian passport holders to enter Malaysia without a visa for stays of up to 30 days. No e-visa application, no embassy appointment, no processing fees. You book a flight, you land, you get stamped in.

For NRIs in the US, this has a practical dimension that goes beyond vacation planning. Malaysia is a 4-to-5-hour flight from every major Indian city — Delhi, Mumbai, Chennai, Hyderabad, Bengaluru, Kochi, Kolkata. That makes it an easy side trip during a visit home, or a standalone long-weekend getaway for NRI families looking for something beyond the usual Goa-or-Kerala rotation. AirAsia, IndiGo, and Malaysia Airlines all operate direct routes, with round-trip fares from Indian metros often running under $200.

Compare that with the increasingly fraught experience of routing through the Gulf, where airspace closures, security advisories from multiple governments, and surging fuel costs have made Dubai and Doha connections less reliable and more expensive than at any point in the last decade.

## What Visit Malaysia 2026 Actually Offers

The campaign is not just a marketing exercise. Malaysia has committed to infrastructure investment across several tourism verticals:

**Eco-tourism and wellness**: Borneo's rainforests, Taman Negara national park, and the Cameron Highlands are being positioned as premium eco-tourism destinations, with new wellness retreats and guided experiences targeting affluent Asian travelers. For NRI families with roots in South India or Kerala, the tropical familiarity is a selling point — the food, the climate, and the cultural rhythms feel closer to home than Europe or the Americas.

**Cultural and heritage tourism**: Penang's George Town, a UNESCO World Heritage Site, and Malacca's Portuguese-Dutch colonial quarter are receiving upgraded visitor infrastructure. Malaysia's multicultural fabric — Malay, Chinese, Indian, and indigenous communities living side by side — gives Indian visitors a sense of cultural recognition that few other Southeast Asian destinations can match.

**Medical tourism**: The India-Malaysia MoU includes specific provisions for promoting medical tourism. Malaysia's private hospitals in Kuala Lumpur and Penang already attract significant Indian patient traffic for cardiac, orthopedic, and dental procedures at a fraction of US costs. The bilateral agreement aims to expand this, with standardized information sharing and quality benchmarking.

**Island and beach destinations**: Langkawi (duty-free shopping and pristine beaches), the Perhentian Islands (diving and snorkeling), and Tioman Island are all part of the VM2026 push. Langkawi's duty-free status makes it particularly attractive for Indian tourists accustomed to the sticker shock of Singapore or Bali.

## The India Connection Is Deepening

The tourism MoU signed between India and Malaysia goes beyond standard diplomatic courtesy. It commits both countries to joint marketing of tourism products, investment in tourism infrastructure, stakeholder cooperation between tour operators and travel agents, and the promotion of responsible and community-based tourism.

India's tourism minister, Shri Ganjendra Singh Shekhawat, and Malaysia's Tiong King Sing signed the agreement with explicit references to the growing travel corridor between the two countries. Indian arrivals to Malaysia have grown steadily since the visa-free arrangement took effect, and the VM2026 campaign is designed to accelerate that trajectory.

For Malaysia, the math is straightforward. India's outbound travel market is expected to reach 50 million trips annually by 2030, up from roughly 27 million in 2024. Every percentage point of that market share that Malaysia can capture translates into billions of ringgit in tourism revenue. The visa-free policy is the tip of the spear — a signal that Malaysia wants Indian travelers, and is willing to remove every bureaucratic barrier to get them.

## Why NRIs Should Pay Attention

The convergence of three factors makes Malaysia unusually well-positioned for the Indian diaspora in 2026:

First, the Gulf transit corridor — historically the cheapest and most convenient way for NRIs to fly between the US and India — is under genuine stress. Airlines are rerouting, canceling, and raising fares. For families planning summer trips to India, a Malaysia stopover on the way back offers a week of beach and culture without the anxiety of transiting through a conflict zone.

Second, the rupee-to-ringgit exchange rate remains favorable. A family of four can do a week in Malaysia — flights from India, hotels, food, and activities — for roughly $1,500 to $2,000, depending on the level of luxury. That is roughly half the cost of an equivalent trip to Singapore or a third of what a European vacation would run.

Third, the food. Malaysian Indian cuisine — roti canai, nasi kandar, banana leaf rice, teh tarik — is not a derivative of Indian cooking. It is its own tradition, shaped by generations of Tamil, Malayali, Punjabi, and Gujarati migration. For NRI families who miss the flavors of home, Kuala Lumpur's Little India and Penang's Indian enclaves offer the real thing, served in a context that feels both foreign and familiar.

Visit Malaysia 2026 is not the most glamorous tourism campaign of the year. But for Indian travelers — especially NRIs weighing their summer options — it may be the most practical one.""",
    },
]


for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
