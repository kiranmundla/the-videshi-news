#!/usr/bin/env python3
"""Travel writer — 2026-06-08 06:00 UTC run"""
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
        "headline": "Indonesia Is Deporting Influencers Who Work on Tourist Visas — and NRIs Who Mix Bali Holidays With Content Should Pay Attention",
        "subheadline": "Indonesian immigration is cracking down on foreign creators doing paid work in Bali. Indian travelers who shoot sponsored content on vacation could face detention, deportation, and entry bans.",
        "slug": make_slug("indonesia-bali-influencer-visa-crackdown-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Bali is one of the most popular international destinations for Indian travelers, and India's booming influencer economy means thousands of NRIs and India-based creators routinely shoot sponsored content there. The new enforcement directly threatens anyone conflating a holiday with a brand deal.",
        "tags": ["travel", "visa", "bali", "indonesia", "influencers", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Aviation A2Z", "url": "https://www.aviationa2z.com/index.php/2026/06/07/indonesia-cracks-down-influencers-tourist-visas/"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/indonesia-tightens-tourist-visa-rules-as-bali-influencers-face-new-pressure-over-paid-content-work/"},
            {"name": "The Young Villas - Bali Visa Guide 2026", "url": "https://theyoungvillas.com/bali-visa-guide/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Besakih_Bali_Indonesia_Pura-Besakih-01.jpg/1280px-Besakih_Bali_Indonesia_Pura-Besakih-01.jpg",
        "image_caption": "Pura Besakih, Bali's most sacred temple complex, a popular destination for Indian tourists",
        "image_attribution": "Wikimedia Commons",
        "body": """Bali has a problem with influencers, and Indonesia is no longer willing to look the other way.

Indonesian immigration authorities have stepped up enforcement against foreign visitors who use tourist visas to do paid work on the island — including sponsored social media posts, brand collaborations, commercial photography, and promotional campaigns. The result: dozens of detentions, deportations, and multi-year entry bans, according to Aviation A2Z and other regional outlets reporting on the crackdown this week.

The rule itself is not new. Indonesia's tourist visa — whether the standard Visa on Arrival or the electronic e-VOA, both priced at IDR 500,000 (roughly $32) — explicitly permits leisure travel, family visits, and tourism activities. It does not permit work. What has changed is how broadly "work" is now being interpreted, and how aggressively it is being enforced.

## The line between holiday and hustle

Under the current policy, Indonesian officials classify sponsored social media content, barter deals with hotels or brands, promotional photography projects, product endorsements, and commercial modelling as work — even when the foreign visitor is not being paid directly by a local Indonesian business. The key distinction is whether the content generates income or economic value. If it does, a standard tourist visa is not sufficient.

This matters because Bali's appeal to creators has blurred the line between personal travel and professional content production. A reel shot at a beach club with a tagged brand partner, a hotel stay exchanged for Instagram coverage, or a YouTube vlog with embedded affiliate links could all, in theory, trigger an immigration violation.

Officials have made clear that the absence of a local Indonesian paycheck does not provide legal cover. If your Bali trip produces content that earns money anywhere in the world, you may need a work visa or Indonesia's dedicated remote worker permit.

## Why this matters to Indian travelers

Bali ranks among the top five international destinations for Indian tourists. Direct flights from Delhi, Mumbai, and Bengaluru — operated by carriers including IndiGo and Air India Express — have made the island easier to reach than ever. And India's influencer economy, valued at over ₹3,400 crore and growing at more than 20% annually, has turned Bali into a particularly popular backdrop for Indian content creators.

The overlap is obvious. Indian food bloggers, travel creators, fashion influencers, and even wedding photographers routinely shoot in Bali. Many operate on tourist visas, assuming that content created for an Indian audience or an Indian brand falls outside Indonesian jurisdiction. That assumption is now dangerous.

For NRIs based in the United States, the risk is slightly different but no less real. A Bay Area tech worker who moonlights as a travel influencer, or a New York-based lifestyle creator who schedules brand shoots during a Bali holiday, is just as exposed to enforcement as someone flying in from Mumbai.

## What you actually need to know

If you are traveling to Bali purely for leisure — personal photos, unsponsored reels, dinner at a beach club — the standard Visa on Arrival remains fine. You can film personal memories, post travel experiences, and explore destinations without issue.

The risk begins the moment content becomes paid work. A few practical guidelines:

Do not accept paid or barter work arrangements tied to your Bali trip if you are entering on a tourist visa. If a brand is compensating you in any form — cash, free stays, products, affiliate commissions — for content produced in Indonesia, you may need a different visa category.

Do not assume that being paid by a non-Indonesian entity protects you. Indonesian immigration authorities have explicitly stated that the source of payment is irrelevant; what matters is whether work-like activity occurs on Indonesian soil.

If content creation is a meaningful part of your trip, consider Indonesia's remote worker permit or consult with an immigration specialist before booking. The penalties for violations include detention, deportation, and bans that can last several years.

## The bigger picture

Indonesia's crackdown reflects a broader global trend. Thailand, Portugal, and several Caribbean nations have introduced or tightened digital nomad and creator visa categories in recent years, precisely because the old tourist-visa-covers-everything assumption no longer holds.

For Indian travelers — and especially for the growing cohort of NRI creators who treat international travel as both holiday and content pipeline — Bali's enforcement shift is a signal worth heeding. The island is not going anywhere. But the days of winging it on a tourist visa while shooting sponsored content may be numbered."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Killed the Grace Period for Long-Stay Visitors — and NRI Families With Foreign Passports Need to Know",
        "subheadline": "New rules require foreign nationals to register before hitting the 180-day limit, not after. Visa extensions will now be granted only in emergencies. The change affects NRI spouses, children, and parents on foreign passports.",
        "slug": make_slug("india-180-day-visa-stay-rule-tightened-nri-families"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Millions of NRIs have family members — spouses, children, aging parents — who hold foreign passports and visit India on tourist or e-visas. The 180-day stay limit and the new registration rules directly affect extended family visits, gap-year stays, and eldercare arrangements.",
        "tags": ["travel", "visa", "india", "immigration", "nri", "180-day-rule"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "travelobiz", "url": "https://www.travelobiz.com/india-tightens-180-day-stay-rules-for-foreign-visitors-makes-visa-extensions-harder/"},
            {"name": "IndiaLaw.in", "url": "https://indialaw.in/blog/visa/india-visa-oci-rules-complete-legal-guide/"},
            {"name": "Consulate General of India, San Francisco", "url": "https://www.cgisf.gov.in/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/7235904/pexels-photo-7235904.jpeg",
        "image_caption": "An Indian passport and visa documents — the 180-day stay limit is now strictly enforced",
        "image_attribution": "Pexels",
        "body": """India's Ministry of Home Affairs has quietly tightened the rules for foreign nationals staying in the country beyond 180 days — and the change has immediate implications for millions of NRI families whose relatives hold foreign passports.

The core revision is straightforward but consequential: the 14-day grace period that previously allowed visitors to register with immigration authorities *after* crossing the 180-day stay limit has been eliminated. Under the new framework, anyone on a visa that permits up to 180 days of stay must complete their registration with the Foreigners Regional Registration Office (FRRO) *before* that limit is reached.

The second change is arguably more significant. Visa extensions, which were previously granted through a relatively routine administrative process, will now be approved only in "emergent circumstances." The days of casually extending a tourist visa for a few extra weeks appear to be over.

## Who this actually affects

The 180-day rule applies to all foreign nationals visiting India on tourist visas, e-tourist visas, and certain other visa categories. For Indian Americans, the most common scenario is this: a spouse, child, or parent who holds a US, UK, Canadian, or Australian passport visits India for an extended stay — perhaps to care for aging relatives, spend a summer with family, or simply enjoy a longer trip home.

Under India's e-tourist visa framework, nationals of the US, UK, Canada, and Japan are permitted a continuous stay of up to 180 days per visit on a one-year or five-year e-visa. For most other nationalities, the cap is 90 days. Either way, the cumulative stay within a calendar year is also capped at 180 days for tourist visa holders.

The practical impact falls hardest on mixed-passport families. An NRI couple in New Jersey where one spouse holds an Indian passport and the other holds an American one will now face different bureaucratic realities when visiting India together for an extended period. The Indian passport holder enters freely; the American spouse must track their days carefully and register before hitting the limit — with no grace period if they miscalculate.

## The FRRO registration requirement

India's Foreigners Regional Registration Office system requires foreign nationals staying beyond a certain duration to register in person or online. The process involves submitting passport details, visa information, proof of address in India, and a photograph. It is not especially onerous, but it is easy to overlook — particularly for visitors who have been coming to India for decades and never bothered with it.

Previously, the 14-day grace window after the 180-day mark provided a buffer. Visitors who realized belatedly that they had overstayed could register without penalty. That safety net is now gone. Failure to register before the deadline can result in fines, complications at departure, and potential issues with future visa applications.

The registration can be completed through the FRRO's online portal (indianfrro.gov.in) or at a physical FRRO office. For visitors staying in major cities — Delhi, Mumbai, Bengaluru, Hyderabad, Chennai — the online process is generally functional, though not always intuitive. For those in smaller cities or towns, a physical visit may still be necessary.

## What NRIs should do now

If you have family members on foreign passports planning extended stays in India, a few practical steps are worth taking now.

First, count the days carefully. The 180-day limit is cumulative within a calendar year for tourist visa holders. Multiple short trips can add up faster than expected — a two-week visit in January, a month in April, and a summer stay starting in June can push past the limit well before anyone thinks to check.

Second, register early. Do not wait until the last week of a 180-day window. The FRRO system occasionally experiences delays, and completing the process with time to spare avoids unnecessary stress.

Third, do not assume extensions will be granted. The new "emergent circumstances" language signals that India is moving toward the compliance-first approach already standard in the US, UK, and Schengen zone. Medical emergencies and genuine crises may still qualify for extensions, but a desire to stay a few extra weeks for a family wedding probably will not.

Fourth, consider the OCI card. For NRI family members who visit India frequently and for extended periods, the Overseas Citizen of India card remains the most practical long-term solution. OCI holders enjoy lifelong multi-entry access with no stay limits, no FRRO registration requirement, and no visa extension headaches. The application process is not quick, but it eliminates the 180-day problem entirely.

## The signal behind the policy

India's tightening of stay rules is part of a broader immigration modernization effort. The mandatory DigiYatra biometric system at four major airports, stricter visa extension protocols, and the elimination of administrative grace periods all point in the same direction: India wants more control over who stays, for how long, and under what conditions.

For NRIs, the message is clear. India welcomes you home — but your foreign-passport-holding family members now need to plan their visits with the same precision they would bring to a Schengen or US entry."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Bengaluru Airport Just Launched a Skip-the-Line Security Service — and It's Free While They Test It",
        "subheadline": "Kempegowda International Airport's new PreSecure programme lets passengers book a fast-track security slot through the BLR Pulse app. The pilot is running at Terminal 1, with Terminal 2 expansion planned.",
        "slug": make_slug("bengaluru-airport-presecure-fast-track-security-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Bengaluru is the primary arrival airport for hundreds of thousands of NRIs in tech — the Bay Area-to-BLR corridor alone accounts for some of the heaviest traffic on the India-US route. Faster security at Terminal 1 directly improves the domestic connection experience for NRIs landing from international flights.",
        "tags": ["travel", "airport", "bengaluru", "security", "technology", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/getting-there/bengaluru-airport-terminal-1-presecure/"},
            {"name": "NewsFirst Prime", "url": "https://www.newsfirstprime.com/general/skip-the-queue-bengaluru-airport-launches-fast-track-security-screening-at-terminal-1/"},
            {"name": "Curly Tales", "url": "https://curlytales.com/what-is-presecure-at-bengaluru-airports-terminal-1/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Terminal_1_of_Kempegowda_International_Airport.jpg/1280px-Terminal_1_of_Kempegowda_International_Airport.jpg",
        "image_caption": "Terminal 1 of Kempegowda International Airport, Bengaluru, where PreSecure is now live",
        "image_attribution": "Wikimedia Commons",
        "body": """Anyone who has connected through Bengaluru's Kempegowda International Airport on a busy Friday evening knows the drill: clear immigration after a 15-hour flight from San Francisco, collect your bags, walk to Terminal 1 for a domestic connection to Chennai or Hyderabad, and then stand in a security line that stretches back to the check-in counters. The airport handles more than 37 million passengers a year. The security queues reflect it.

Bangalore International Airport Limited (BIAL) is now testing a fix. A new service called PreSecure, launched this month at Terminal 1, allows departing passengers to reserve a dedicated security screening time slot through the BLR Pulse mobile app. Passengers who book a slot are directed to a separate, faster security lane — bypassing the general queue entirely.

## How it works

The process is simple enough. Download the BLR Pulse app (available on both Android and iOS), scan your boarding pass, and select an available security screening slot based on your departure time. Bookings can be made up to 75 minutes before your scheduled flight. Once confirmed, you head to the dedicated PreSecure security lane near Check-in Counter 86 at Terminal 1.

The separate lane is staffed and equipped identically to the standard security checkpoints — the same CISF screening, the same X-ray machines, the same procedures. The only difference is the queue length. Because slots are limited and time-boxed, the wait is substantially shorter.

For now, the service is free. BIAL has positioned this as a pilot programme, and the airport authority will evaluate passenger response and operational performance before deciding on next steps. If the trial succeeds, expect it to become a paid service — airport officials have already indicated that commercialisation is the eventual plan. An extension to Terminal 2, which handles most international departures, is also under consideration.

## Why NRIs should care

Bengaluru is not just any Indian airport for the diaspora. It is the tech corridor gateway. The SFO-BLR, SEA-BLR, and EWR-BLR routes are among the most heavily traveled diaspora corridors in the world, carrying software engineers, startup founders, and their families between Silicon Valley and India's own tech capital.

For NRIs arriving on long-haul international flights, the domestic connection experience at BLR has historically been the weakest link. You clear customs in Terminal 2, but if your onward flight departs from Terminal 1, you re-enter the domestic departure flow — which means another security screening, often during peak hours. PreSecure directly addresses that bottleneck.

The service is also relevant for NRIs visiting family across Karnataka and South India. Bengaluru is the natural hub for onward flights to Mangaluru, Hubli, Mysuru, Coimbatore, Kochi, and Thiruvananthapuram. A faster security experience at Terminal 1 makes the entire connecting journey less painful.

## Part of a bigger push

PreSecure is the latest in a series of passenger experience upgrades at Kempegowda International Airport. The BLR Pulse app, first launched in 2023, already offers real-time queue wait times, flight status updates, indoor navigation through the WayFinder feature, and the Pulse Rewards loyalty programme (which lets passengers earn points on dining and shopping within the terminals).

The app has quietly become one of the more functional airport companion tools in India — a contrast to the often bare-bones digital offerings at other major Indian airports. Adding slot-based security screening turns it from a convenience into a genuinely useful travel tool.

BIAL's investment in passenger flow technology also reflects the airport's growth trajectory. Bengaluru handled its 37-millionth passenger last year and is on track to exceed 40 million this year. Terminal 2, which opened in late 2022, was designed to handle the international surge, but Terminal 1's domestic operations have been straining under the volume. PreSecure is a software solution to what is ultimately an infrastructure capacity problem — but for passengers, the result is the same: less time in line.

## The bottom line

If you are flying through Bengaluru's Terminal 1 in the coming weeks, download BLR Pulse before you get to the airport. The PreSecure service is free during the pilot phase, and there is no reason not to use it. Book a slot 75 minutes before departure, head to Counter 86, and skip the line.

For the hundreds of thousands of NRIs who transit through BLR every year — particularly those connecting from international arrivals to domestic flights — this is a small but meaningful quality-of-life improvement. The fact that it is free right now makes it even easier to try.

Whether BIAL keeps it free or eventually charges for the service (as seems likely), the concept itself is overdue. India's airports have invested billions in terminals, lounges, and duty-free zones. Making the security queue less miserable is arguably more valuable than all of it."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
