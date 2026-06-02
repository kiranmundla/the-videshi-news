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
        "headline": "Fifty Embassies Down to Twenty — The Africa Visa Purge Is a Dress Rehearsal",
        "subheadline": "The State Department is gutting consular capacity across an entire continent. For Indian professionals watching from the sidelines, the playbook should look uncomfortably familiar.",
        "slug": make_slug("africa-visa-hub-consolidation-india-consular-playbook"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "India is the world's largest US visa applicant country — 65% of all H&L applicants, 20% of student visa applicants. If the Africa hub model spreads to South Asia, the impact on H-1B stamping, B1/B2 wait times, and family visa processing would be catastrophic. Indian IT companies operating across Africa (TCS, Infosys, Wipro) are directly affected by the consolidation.",
        "tags": ["visa-processing", "state-department", "consular", "africa", "india", "rubio"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Associated Press via Reuters", "url": "https://www.reuters.com/world/us-slash-number-embassies-africa-that-process-visas-ap-reports-2026-06-02/"},
            {"name": "Ghana News Page", "url": "https://ghananewspage.com/u-s-state-department-to-consolidate-visa-processing-hubs-across-africa/"},
            {"name": "British Brief", "url": "https://britbrief.co.uk/us-to-dramatically-reduce-visa-processing-embassies-in-africa-to-20-hubs/"},
            {"name": "FrontPage Africa", "url": "https://fpa.news/liberia-us-to-drastically-slash-embassy-visa-processing-across-africa-retains-liberia-among-20-regional-hubs/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/33500646/pexels-photo-33500646.jpeg",
        "body": """The State Department is about to do something it has never done before: strip visa-processing authority from more than half the US diplomatic missions on an entire continent.

Under a directive signed by Secretary of State Marco Rubio last week and first reported by the Associated Press on Monday, the nearly 50 US embassies and consulates across Africa that currently handle visa applications will be consolidated into just 20 designated "hubs." The change is expected to take effect this month.

## The Twenty That Remain

The surviving hubs read like a strategic map of American interests rather than a geography of applicant need: Abidjan, Accra, Addis Ababa, Cape Town, Dakar, Dar es Salaam, Djibouti, Johannesburg, Kampala, Kigali, Kinshasa, Lagos, Lomé, Luanda, Malabo, Monrovia, Nairobi, Port Louis, Praia, and Yaoundé.

Consular sections in the remaining 30-odd countries will stay open — but only for American citizen services, passport renewals, emergency requests, and diplomatic visas. If you are a Mozambican engineer with a conference in San Jose or a Chadian student admitted to Georgia Tech, you will now need to fly to a hub country, secure accommodation, and wait.

## The Layered Barrier

This is not happening in a vacuum. African visa applicants were already navigating a thicket of new restrictions: a travel ban on citizens of several African nations, a $15,000 refundable visa bond requirement for applicants from roughly 50 countries deemed high-overstay-risk, and tightened screening protocols expanded after the Ebola outbreak earlier this year.

The consolidation adds a logistical layer on top of the financial and bureaucratic ones. A citizen of Mali seeking a visitor visa will now need to travel to Dakar — a 1,200-kilometer journey across an international border — before even joining a visa queue. The costs of flights, hotels, and time off work effectively price out a significant share of applicants. That is, of course, part of the point.

## Why India Should Be Paying Attention

The Africa consolidation is a proof of concept, not an isolated policy. The Trump administration has already scaled back embassy personnel globally and imposed social media screening requirements that halved daily appointment capacity at several posts, including all five US consulates in India.

The numbers tell the story of India's exposure. Indians represent roughly 65 percent of all H-1B and L-1 visa applicants worldwide and 20 percent of all student visa applicants. The five US consulates in India — New Delhi, Mumbai, Chennai, Hyderabad, and Kolkata — together process more employment-based visas than any other country's consular network.

If the hub model were applied to South Asia, even a modest consolidation — say, reducing processing authority to three of five Indian cities — would create bottlenecks that dwarf the current nine-month wait times in Mumbai. H-1B workers returning from India after visa stamping already face anxiety about passport retention during "administrative processing" that can stretch to six weeks. Fewer processing locations would compound every existing delay.

## The Indian Business Angle

India's largest IT services companies — TCS, Infosys, Wipro, HCL Technologies — maintain significant operations across Africa, deploying Indian engineers and consultants to client sites in Nigeria, Kenya, South Africa, and beyond. Those workers, typically on short-term business visas, will now face longer transit times and higher costs to secure US visas from their African postings.

For the estimated 300,000 Indian nationals working across Africa in IT, banking, and infrastructure, the consolidation creates a new wrinkle in an already complex visa calculus. A project manager in Nairobi is fine — it remains a hub. Her colleague in Maputo is not.

## The Pattern

The State Department has not said whether the Africa model will be replicated elsewhere. But the logic of the consolidation — concentrate resources, reduce processing volume, raise the effective cost of applying — is entirely consistent with the administration's broader immigration posture: the $100,000 H-1B fee, the $15,000 visa bonds, the prevailing wage hikes, the adjustment-of-status restrictions under PM-602-0199.

Each policy works on a different pressure point. Together, they form an architecture of friction designed to reduce immigration through procedural burden rather than statutory change. The Africa consolidation is simply the most visible example of the physical infrastructure being reshaped to match that intent.

For Indian diaspora professionals — whether tracking their own green card timelines from Sunnyvale or managing teams across Johannesburg and Lagos — the lesson is the same one it has been all year: the machinery of legal immigration is being redesigned, one embassy at a time."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Visa Bonds Waived for Football Fans, $100,000 for H-1B Workers — The World Cup's Immigration Double Standard",
        "subheadline": "As Iran's squad scrambles for entry and South Africa's team gets stranded at the airport, the US builds a priority lane for spectators while skilled workers wait in the regular queue.",
        "slug": make_slug("world-cup-visa-bond-waiver-h1b-double-standard-indian-diaspora"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "India is not in the 2026 World Cup, so Indian nationals get no bond waiver or FIFA PASS priority appointments. The same administration charging $100,000 for H-1B petitions and restricting green card adjustments is fast-tracking football fans. For Indian-American soccer fans wanting to attend matches, and for H-1B workers whose consular appointment slots may be diverted to World Cup processing, the two-tier system is personal.",
        "tags": ["world-cup", "visa-bond", "h1b", "fifa", "immigration-policy", "double-standard"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Envoy Global", "url": "https://www.envoyglobal.com/blog/us-waive-visa-bond-fifa-world-cup-2026"},
            {"name": "Reuters", "url": "https://www.reuters.com/sports/iran-beat-gambia-federation-seeks-fifa-clarity-over-visas-2026-05-30/"},
            {"name": "Sports Illustrated", "url": "https://www.si.com/soccer/south-africa-latest-country-to-face-visa-issues-ahead-of-2026-world-cup"},
            {"name": "VisaVerge", "url": "https://visaverge.com/fifa-pass-explained-priority-us-visa-for-world-cup-fans/"},
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/esta-for-fifa-world-cup-2026/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/34170128/pexels-photo-34170128.jpeg",
        "body": """The FIFA World Cup kicks off on June 11 in Mexico City, with matches across the United States through July 19. By the time the final whistle blows, millions of fans will have crossed international borders to attend. For many of them, the US government has rolled out something it rarely offers anyone: a smoother path in.

For Indian Americans watching the tournament — and watching the immigration system — the contrast is hard to miss.

## The Fast Lane

In May, the State Department announced a visa bond waiver for nationals of countries competing in the World Cup. The policy targets citizens of roughly 50 nations that normally face a refundable bond of up to $15,000 as a condition of receiving a US visitor visa — a requirement the administration imposed to discourage overstays from countries it deems high-risk.

Five bond-eligible countries qualified for the World Cup: Algeria, Cape Verde, Ivory Coast, Senegal, and Tunisia. Their citizens who purchased FIFA tickets by April 15 and enrolled in the FIFA Priority Appointment Scheduling System (PASS) will have the bond requirement waived entirely. Athletes, coaches, support staff, and immediate family members of team personnel also qualify.

FIFA PASS itself is a separate concession: a priority visa appointment lane for ticket holders from non-Visa Waiver Program countries, managed in coordination with the State Department. It does not guarantee approval, but it does guarantee a faster interview slot than the standard queue — a queue that, in many countries, stretches months into the future.

## The Slow Lane

Now consider the parallel reality. An Indian software engineer on an H-1B visa who needs to re-stamp her passport at the Chennai consulate faces a wait of approximately three months — if she can get an appointment at all. If she works for a company that must pay the $100,000 H-1B fee imposed by presidential proclamation last September, her employer is weighing whether the sponsorship is even worth it. As of February, only 85 employers had paid the fee.

Her colleague applying for a green card under PM-602-0199 now faces the prospect of returning to India for consular processing rather than adjusting status from within the United States — a policy change USCIS framed as restoring the "proper pathway" but that immigration attorneys have called the most significant procedural restriction in decades.

Neither of them is eligible for a priority appointment lane. Neither gets a bond waiver. Neither has a well-funded international sports federation negotiating on their behalf.

## When Even Teams Cannot Get In

The irony deepens when you look at how the World Cup's own participants are faring. Iran's national football team has relocated its entire training camp from Arizona to Tijuana, Mexico, after failing to secure US visas. The team has written to FIFA asking for clarity on when — or whether — tournament visas will be issued. Iran is scheduled to play all three group-stage matches on US soil, in Los Angeles and Seattle, and will need to cross the border from Mexico for each one.

South Africa's squad fared only slightly better. The team's departure to their training base in Pachuca, Mexico was delayed by a day after visa issues left several players and staff stranded. Sports Minister Gayton McKenzie publicly called the situation "embarrassing and grossly unfair," demanding a report from the national football association. The players eventually received their visas, but the assistant coach, team doctor, head of security, and an analyst were still waiting.

These are not anonymous applicants. They are credentialed athletes with FIFA backing, host-country obligations, and global media attention. If their visa processes are this chaotic, the ordinary applicant has no chance of a seamless experience.

## What Indian Fans Face

India is not competing in the 2026 World Cup. That means Indian nationals — whether US-based NRIs or fans traveling from India — receive none of the FIFA PASS or bond waiver benefits. An Indian cricket fan in Mumbai who wants to catch a match in New Jersey will join the standard B1/B2 visa queue, currently estimated at five to nine months depending on the consulate.

Worse, the World Cup processing surge may actually displace regular visa appointments. When consular resources are diverted to FIFA PASS priority slots and team credential processing, the regular appointment pool shrinks. Indian applicants seeking H-1B stamping, B1/B2 renewals, or F-1 interviews during the June-July window may find even fewer available slots than usual.

## The Arithmetic of Priorities

The numbers lay bare the gap. A football fan from Senegal with a $200 FIFA ticket gets a bond waiver worth $15,000 and a priority visa appointment. An Indian engineer with a $100,000 H-1B fee, a six-figure salary, and a decade of US tax contributions gets a three-month wait and a discretionary denial risk on her green card application.

This is not hypocrisy in the crude sense — the World Cup is a one-time diplomatic and economic event, and host-country obligations create legitimate pressure to facilitate entry. But it reveals something the immigration system rarely makes this explicit: the speed and cost of the process depend entirely on which lane you are in, and the lanes have nothing to do with merit, contribution, or how long you have been waiting.

For the Indian diaspora, the World Cup visa apparatus is not a grievance. It is a data point. The system can move fast when it wants to. It can waive fees when the incentive is right. It can create priority lanes overnight. The question Indian Americans have been asking for years — why not for us? — has never had a clearer answer: because nobody with a billion-dollar tournament on the line is asking on their behalf."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
