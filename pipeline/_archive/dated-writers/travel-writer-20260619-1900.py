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
        "headline": "Vietnam Is Going Digital at Every Airport — and the Diaspora's Favorite New Getaway Now Needs Paperwork Before You Board",
        "subheadline": "The mandatory pre-arrival QR card that snarled Ho Chi Minh City is now expanding to Hanoi and Da Nang. Here is the 72-hour rule NRIs need to know before the next wedding trip or layover.",
        "slug": make_slug("vietnam-digital-arrival-card-all-airports-nri-qr-rule"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Vietnam has quietly become a top wedding and leisure destination for Indian Americans as Thailand tightens its rules — and now every traveler needs a free digital arrival card filed within 72 hours of landing, or risk being stuck in the slow lane at immigration.",
        "tags": ["travel", "visa", "vietnam", "southeast-asia", "arrival-card"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "U.S. Embassy & Consulate in Vietnam", "url": "https://vn.usembassy.gov/notice-implementation-of-pre-arrival-declaration-for-international-visitors-arriving-at-airports-in-vietnam/"},
            {"name": "Travelobiz", "url": "https://travelobiz.com/"},
            {"name": "Trip.com — Vietnam Arrival Card 2026 Guide", "url": "https://www.trip.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32223420/pexels-photo-32223420.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "Travelers queue at a busy international airport check-in and immigration hall",
        "image_attribution": "Pexels",
        "body": """Vietnam is one of the few places in Asia getting *easier* for Indian travelers right now — and that is exactly why the diaspora needs to read the fine print on its border rules.

While Thailand pushed India out of its visa-free club this spring and into a paid visa-on-arrival lane, Vietnam has kept the welcome mat out. For Indian Americans, it has become a go-to for destination weddings, multi-generational family trips, and the kind of cheap, scenic week that a tightening rupee and a strong dollar make irresistible. Now there is one administrative box everyone arriving on a non-Vietnamese passport has to tick first.

## What changed this week

Vietnam's immigration authority is expanding its mandatory **digital pre-arrival declaration** from a single airport to every air gateway in the country. The U.S. Embassy in Hanoi issued a fresh traveler notice confirming the move: "All international passengers who do not hold a Vietnamese passport" must complete the declaration, "or not more than three days before arrival," and present the generated QR code to immigration on entry.

The rule first went live on 15 April 2026 at Tan Son Nhat International Airport (SGN) in Ho Chi Minh City — Vietnam's busiest gateway, where evening peaks had produced immigration queues of 500-plus people and waits of one to two hours. Officials say the digital card lets officers pull passenger data electronically instead of keying it in at the counter. Early pilot data at Da Nang showed average processing dropping from about 90 seconds per passenger to 54 seconds. With the system stable, the requirement is now rolling out to Noi Bai in Hanoi (HAN), Da Nang (DAD), and other points of entry nationwide.

## How it actually works

The declaration is free and lives at the official portal, `prearrival.immigration.gov.vn`. A few details that trip people up:

- **The window is narrow.** You can submit only within 72 hours before your scheduled arrival — not earlier, not later. File it too soon and the system will not accept it.
- **It is not a visa.** If your nationality needs an e-visa or visa-on-arrival approval, you still get that separately. The arrival card is purely an entry declaration that runs alongside your visa.
- **You will need your details handy.** Passport, visa, flight, and accommodation information all go on the form. Once approved, the portal emails you a QR code to show at the counter.
- **Almost everyone is in scope.** Foreign visitors with e-visas or paper visas, visa-on-arrival holders, visa-exempt nationalities, and overseas Vietnamese entering on a foreign passport all must complete it. Only Vietnamese passport holders and airside transit passengers who never clear immigration are exempt.

## Why this matters for NRIs

The catch for Indian American families is the QR code's reach across generations. A trip home or a Southeast Asian holiday often mixes passports — US-citizen kids, green-card-holding parents, an Indian-passport relative joining from Delhi. Under Vietnam's rule, **each non-Vietnamese passport holder needs their own declaration**, including children, though a parent or guardian can complete a minor's form. That means the family member coordinating the trip is now filing four or five separate declarations in the three days before departure, not one.

There is also the question of when you fly. Vietnam is targeting 22 million international arrivals in 2026, up from 18.6 million last year, and the digital push is explicitly meant to handle that surge. If you are connecting through Hanoi or Da Nang on a route that did not require the card a few months ago, the rules may have changed since you last flew. The State Department's notice is blunt about the consequence of skipping it: present the QR code on arrival, or fall back to a paper form and longer waits at the counter.

## What to do before your next trip

If Vietnam is on your itinerary in the coming months, the playbook is simple. Set a calendar reminder for three days before each flight, gather every traveler's passport and your hotel booking, and file each declaration at the official `.gov.vn` portal — not a lookalike site charging a "service fee," since the real one is free. Save each QR code to your phone and screenshot it in case airport Wi-Fi fails. For visa-on-arrival travelers, remember the digital card does not replace the NA1 form and stamping fee you still handle at the airport counter.

Vietnam is betting that going fully digital will keep it the smooth, friendly alternative as the rest of Southeast Asia adds friction. For the diaspora, the trade is fair — a few minutes online beats two hours in a queue — as long as you remember to do it before you board.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Consular Services in the UAE Get a New Operator on July 1 — Here's What 3.5 Million NRIs Need to Watch",
        "subheadline": "Al Hind Tours and Travels takes over passport, visa, OCI and attestation work from BLS and SGIVS. The rules don't change, but the first weeks of any handover are when appointments get messy.",
        "slug": make_slug("india-uae-consular-services-al-hind-takeover-july-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "The UAE holds one of the world's largest overseas Indian communities, and almost every family there touches consular services for passport renewals, OCI requests, and attestations — so a change in who runs those centres briefly reshapes appointment availability for millions, including relatives of US-based NRIs.",
        "tags": ["travel", "visa", "uae", "passport", "oci", "consular"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travelobiz — Embassy of India confirms Al Hind switch", "url": "https://travelobiz.com/india-uae-passport-visa-services-al-hind-2026/"},
            {"name": "Embassy of India, Abu Dhabi", "url": "https://www.indembassyuae.gov.in/"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/1381722/pexels-photo-1381722.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "The Dubai skyline at night, home to one of the world's largest overseas Indian communities",
        "image_attribution": "Pexels",
        "body": """If you have family in the UAE — and a huge share of the American desi community does — there is a quiet administrative change worth flagging on the family WhatsApp group this month.

Starting **1 July 2026**, Indian passport, visa, and consular services across the UAE move to a new outsourced operator: **Al Hind Tours and Travels LLC**. The Embassy of India in Abu Dhabi has confirmed the switch, which replaces the long-standing providers BLS International and SGIVS Global. The change covers services overseen by both the Abu Dhabi embassy and the Consulate General of India in Dubai — together responsible for one of the largest overseas Indian populations on the planet, estimated at over 3.5 million people.

## What is actually changing

To be clear about what this is and is not: it is a change in the *company that processes paperwork*, not a change in the rules, eligibility, or fees set by the Indian government. Any passport renewal, visa application, OCI-related request, or document attestation submitted on or after July 1 will be filed through centres operated by Al Hind rather than the outgoing providers.

Until then, nothing changes. BLS International and SGIVS Global will keep accepting applications through **30 June 2026**. If you — or a relative in Dubai, Abu Dhabi, Sharjah, or elsewhere in the Emirates — already hold an appointment with either provider before that date, the guidance is simply to proceed as planned.

## The catch is timing

Consular handovers look routine on paper, but the first few weeks are reliably the bumpiest. New service centre locations, fresh appointment-booking systems, updated payment portals, and new customer-support lines all come online at once. The Indian mission has said details on the following will be released separately through official channels:

- Service centre locations across the Emirates
- Appointment booking procedures
- Processing fees
- Operating hours
- Customer support contacts

In other words, the booking link and the branch your family has used for years may not be the right one come July. Anyone whose application timeline stretches into the new month should wait for Al Hind's official rollout details before booking, rather than relying on old links or third-party agents who may not have updated their information.

## Why a US-based NRI should care

This might read as a Gulf story, but the diaspora is deeply interlinked. Many Indian American families have parents, siblings, or in-laws living and working in the UAE, and consular tasks tend to cluster around family events — a parent renewing a passport before flying to a grandchild's graduation in the US, an OCI card sorted before a long visit, attestations needed for a property or marriage document back home. A temporary squeeze on appointment availability in July could ripple into travel plans that touch America.

There is also a practical lesson that travels well beyond the UAE: outsourced consular providers change periodically in every region, and each time, the safest move is to verify the current operator through the official Indian embassy or consulate website before paying anyone or booking anything. Scam operators thrive in exactly these transition windows, advertising "appointments" and "expedited service" for providers that are on their way out.

## The bottom line

For NRIs with UAE ties, the action item is small but real: if a passport, OCI, visa, or attestation task can be wrapped up with BLS or SGIVS before June 30, do it now and avoid the changeover entirely. If it has to wait until July, hold off on booking until the embassy publishes Al Hind's centre list and appointment system — and treat any link that surfaces before then with healthy suspicion. The rules are not moving. The front door is.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "New Zealand Just Finalized Its Skilled-Migrant Overhaul — and the Fine Print Cuts Both Ways for Indian Professionals",
        "subheadline": "From August 24, wage thresholds get locked in early and engineering degrees earn more points. But self-employment no longer counts, and the evidence bar for qualifications just went up.",
        "slug": make_slug("new-zealand-skilled-migrant-overhaul-august-indian-professionals"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "India is one of New Zealand's top sources of skilled migrants in IT, engineering, healthcare, and trades — and many of those professionals are part of the same globally mobile diaspora weighing the US, Canada, the UK, and Australia, so a clearer, partly friendlier NZ pathway reshuffles where the next generation of Indian talent lands.",
        "tags": ["travel", "visa", "new-zealand", "immigration", "skilled-migrant"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Immigration New Zealand", "url": "https://www.immigration.govt.nz/about-us/media-centre/news-notifications/further-changes-to-the-skilled-migrant-category"},
            {"name": "Travelobiz — NZ Skilled Migrant Changes August 2026", "url": "https://travelobiz.com/new-zealand-skilled-migrant-visa-changes-august-2026/"},
            {"name": "Fragomen — NZ Skilled Migrant Category Reforms", "url": "https://www.fragomen.com/"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/18201091/pexels-photo-18201091.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "Auckland's skyline with the Sky Tower, a top destination for skilled Indian migrants",
        "image_attribution": "Pexels",
        "body": """As the US tightens student and work visas and Canada quietly caps Indian study permits, the diaspora's most mobile professionals are scanning the map for the next reliable door. New Zealand just made its own pitch clearer — and the details, finalized this week, reward some Indian applicants while quietly closing options for others.

Immigration New Zealand has released the final shape of its revamped **Skilled Migrant Category (SMC)**, the country's main residence pathway, with changes taking effect on **24 August 2026**. India is already one of New Zealand's key sources of skilled migrants in IT, engineering, healthcare, transport, construction, and the trades, so the fine print matters to a lot of families.

## The good news: wage certainty

The headline change is about predictability. For years, the biggest frustration with New Zealand's system was that wage thresholds kept moving. A migrant could spend three or four years building toward residence, only to find the bar had risen before they could apply.

From August 24, most applicants will only need to meet the wage threshold that applied **when they started accumulating their eligible skilled work experience** — not a higher one introduced later. A new five-month grace period reinforces this: if a migrant begins skilled employment within five months of receiving a work visa, the threshold in effect on the visa-approval date keeps applying. The same wage-setting logic now extends across the Work to Residence, Care Workforce, and Transport Work to Residence pathways. For Indian professionals planning several years ahead, that removes a major source of anxiety.

Engineering graduates get a specific boost, too. The update increases points awarded for bachelor's degrees and for internationally accredited engineering qualifications — a category where Indian applicants are heavily represented.

## The catch: tougher checks

The same announcement raises the bar in three ways that Indian applicants should read carefully.

**Qualifications need more evidence.** Applicants claiming points for Level 8 or Level 9 qualifications must now generally show *both* their postgraduate qualification and a supporting bachelor's degree, with certificates and transcripts. For many Indian applicants with overseas degrees, an International Qualification Assessment (IQA) remains necessary unless the qualification is on New Zealand's exemption list. (Those claiming points for a New Zealand master's degree are spared the separate bachelor's evidence.)

**Self-employment no longer counts.** Under the new Trades and Technician and Skilled Work Experience pathways, self-employment cannot be used to satisfy directly relevant work-experience requirements. Immigration New Zealand says independently verifiable evidence is hard to obtain for self-employed work. This is a real blow to Indian freelancers, consultants, contractors, and small-business owners who hoped to count those years — they will need to secure qualifying salaried employment or find another pathway.

**Employment must be genuine.** Officers now have stronger authority to reject applications where a job offer looks artificial or created solely to secure residence. Employers must show roles are ongoing, available, and genuinely need to be based in New Zealand. Legitimate applicants have little to fear, but it tightens the net on arranged offers.

For Indian diploma holders and technical professionals, there is a useful wrinkle: for overseas qualifications, New Zealand's 120-credit rule will not apply. Instead, applicants need an IQA confirming the qualification meets at least Level 4 equivalency — a more flexible standard for credentials that do not map neatly onto New Zealand's domestic credit structure.

## Why the diaspora should watch this

New Zealand is a smaller player than the US, Canada, or Australia in absolute numbers, but it competes for exactly the same pool of skilled Indian talent — and right now that pool is reconsidering its options. With Canada floating country-specific study-permit caps and the US lengthening processing times, a New Zealand pathway that offers wage certainty and richer points for engineering degrees is a more serious alternative than it was a year ago.

For Indian American families, the relevance is generational and lateral. The cousin finishing an engineering degree in Pune, the sibling weighing a healthcare job abroad, the friend whose Canadian study plans just got riskier — these are the people for whom New Zealand's clearer, partly friendlier rules could tip a decision. The move after August 2026 rewards those who plan: review your qualifications, line up verifiable salaried experience, and choose your pathway before applying, because the system now gives more certainty to the prepared and less room to the improvising.
"""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
