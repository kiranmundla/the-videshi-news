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
        "headline": "Mullin Just Blinked — DHS Signals It Could Waive the $100,000 H-1B Fee",
        "subheadline": "In his first Senate budget hearing, the Homeland Security secretary hinted at case-by-case relief from the massive surcharge — a shift that could reshape the calculus for thousands of Indian employers and workers.",
        "slug": make_slug("mullin-dhs-100k-h1b-fee-waiver-flexibility-senate"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian IT services firms and their workers are the single largest group affected by the $100,000 H-1B fee. Any waiver mechanism — however narrow — directly determines whether mid-size Indian staffing companies can continue operating in the US, and whether individual H-1B holders sponsored by smaller firms keep their jobs.",
        "tags": ["h1b", "uscis", "dhs", "mullin", "h1b-fee", "senate"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/homelands-mullin-signals-flexibility-on-100-000-h-1b-visa-fees"},
            {"name": "Audacy / AP", "url": "https://www.audacy.com/national-news/democrats-press-mullin-on-border-officer-pullback-threat-at-airports"},
            {"name": "Audacy / AP", "url": "https://www.audacy.com/national-news/democrats-hammer-dhs-secretary-markwayne-mullin-in-a-heated-senate-hearing"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/DHS_Secretary_Markwayne_Mullin_Official_Portrait_%2855166865268%29.jpg/3840px-DHS_Secretary_Markwayne_Mullin_Official_Portrait_%2855166865268%29.jpg",
        "body": """For months, the $100,000 H-1B fee has been the immigration policy equivalent of a closed fist — absolute, unyielding, and aimed squarely at the employers who rely most heavily on foreign talent. On Tuesday, the fist opened slightly.

DHS Secretary Markwayne Mullin, testifying before the Senate Appropriations Committee in his first budget hearing since replacing the fired Kristi Noem, told lawmakers that his department has "flexibility" to provide relief from the surcharge in certain cases. The remark, brief and carefully hedged, nonetheless marks the first time a senior administration official has publicly acknowledged that the fee could be softened rather than simply defended in court.

## What Mullin actually said

The $100,000 per-petition fee was imposed by presidential proclamation in September 2025 and has since been challenged in at least two federal courts. A Boston judge questioned whether the government could effectively "seize 10% of a company's equity," while a circuit split between districts has made a Supreme Court showdown increasingly likely.

Mullin did not propose scrapping the fee. What he signaled was that DHS could use its existing authority to grant waivers on a case-by-case basis where the fee would cause disproportionate harm — language that tracks the proclamation's "national interest" exception, which has so far been applied in what court filings describe as "extraordinarily rare circumstances."

Republican Sen. Susan Collins of Maine pressed Mullin directly on whether DHS would show flexibility on "high fees and quotas for certain types of work visas." Mullin's response — "We do need some flexibility there" — was notable less for its specificity than for its departure from the administration's previous stance, which has been to defend the fee without qualification.

## Why this matters for Indian workers

Indian nationals account for roughly 72% of all H-1B approvals in a typical year, and Indian IT services companies — from the big four (TCS, Infosys, Wipro, HCLTech) to hundreds of mid-size staffing firms — file tens of thousands of petitions annually. The $100,000 fee, applied per petition rather than per company, hits this ecosystem harder than any other.

For a mid-size firm filing 50 H-1B petitions, the surcharge adds $5 million to annual costs before a single worker starts. Several smaller staffing companies have already told immigration attorneys they are pausing new H-1B filings entirely, shifting work to Canada or India instead.

A waiver mechanism, even a narrow one, could change that arithmetic. If DHS were to exempt petitions below a certain wage threshold, or provide industry-specific carve-outs for healthcare and education — sectors that Collins specifically flagged — the Indian IT workforce would be among the primary beneficiaries.

## The hearing's other flashpoint

The $100,000 fee was not the only immigration topic that drew fire. Democratic Sen. Patty Murray blasted Mullin over his repeated threats to withdraw Customs and Border Protection officers from airports in so-called sanctuary cities — a move that would paralyze international travel at hubs including JFK, SFO, LAX, and O'Hare.

"Your plan to withdraw CBP officers from airports in cities that don't roll over for Trump — that is insane," Murray said. "It would also spell economic crisis for blue and red states."

Mullin has not put forward a concrete proposal, but the U.S. Travel Association confirmed he discussed the idea during a meeting last month. Even Transportation Secretary Sean Duffy has publicly said the plan "doesn't make sense." For the millions of Indian Americans who transit through sanctuary-city airports — which include every major hub with direct flights to India — the threat adds another layer of uncertainty to an already fraught travel environment.

## What comes next

Mullin will testify before the House on Wednesday, where he is likely to face similar questions. The more consequential development will be whether DHS formalizes any waiver guidance. The proclamation grants the secretary broad discretion to waive the fee for any "individual alien," "company," or "industry" where doing so serves the national interest — but neither the proclamation nor any subsequent materials define what "national interest" means in this context.

Immigration attorneys are cautiously optimistic. The signal from Mullin is encouraging, they say, but until DHS publishes actual guidance on who qualifies for a waiver and how to apply, the $100,000 fee remains the default for every new H-1B petition filed after October 1.

For the Indian diaspora, the math is blunt: flexibility in principle is not flexibility in practice. The clock is ticking toward the FY2027 filing season, and employers need clarity before they commit to sponsoring workers who may cost them six figures before they write a line of code."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Visa System Is Crashing — and Indian Applicants Are Stuck in the Queue",
        "subheadline": "US visa processing websites have gone down amid surging summer demand, while Indian consulates book interview slots 10 to 12 months out and the US Embassy warns that screening never actually stops.",
        "slug": make_slug("us-visa-website-outage-india-consulate-delays-summer"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "India is the single largest source of US visa applicants, and Indian consulates are among the most backlogged in the world. Website outages disproportionately affect Indian applicants who must navigate a system already stretched to breaking — especially those trying to schedule H-1B stamping, parents visiting on B-1/B-2, and students filing F-1 renewals.",
        "tags": ["visa", "consulate", "india", "ustraveldocs", "uscis", "world-cup"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "AInvest", "url": "https://www.ainvest.com/news/us-visa-website-outages-cause-delays-worldwide-amid-summer-travel-season-and-fifa-world-cup-2026-demand/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/us-embassy-in-india-warns-visa-holders-that-visa-screening-continues-even-after-visa-is-granted/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/tighter-student-visa-rules-may-impact-indians-in-us-expert/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/32227477/pexels-photo-32227477.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """If you have tried to book a US visa appointment from India in the past week, you already know the punchline: the website does not work.

USTravelDocs.com, the primary portal for scheduling visa interviews at US consulates worldwide, has been experiencing significant technical failures. Users report errors when trying to pay fees, schedule interviews, and access their accounts. The Consular Electronic Application Center — CEAC — which handles immigrant visa applications, is also suffering intermittent outages affecting document uploads and payment processing.

The State Department has acknowledged the problems and says it is "actively working to resolve" them. No timeline has been provided. Applicants are told to wait 24 hours and try again — advice that rings hollow when the next available interview slot is already a year away.

## India bears the brunt

India is not just any visa-processing country. It is the largest source of H-1B workers, the second-largest source of international students, and one of the highest-volume B-1/B-2 tourist visa markets in the world. At any given time, hundreds of thousands of Indian nationals are somewhere in the US visa pipeline — waiting for an interview, waiting for administrative processing, waiting for a passport to be returned.

Most US consulates in India are currently booking interview slots 10 to 12 months in advance. That means an applicant who needs a visa stamped today will not sit down with a consular officer until the spring of 2027. For H-1B workers who need to travel for stamping and return to their US jobs, that timeline is career-threatening. For parents hoping to visit children in the US, it means missing another year of grandchildren's milestones.

The website outages make an already glacial process worse. When the portal goes down, applicants lose their place in appointment queues, payment confirmations vanish, and rescheduling becomes impossible. Several immigration attorneys have reported clients whose paid appointments disappeared entirely after an outage, forcing them to repay the $185 Machine Readable Visa fee and start over.

## Screening that never ends

Adding to the anxiety, the US Embassy in New Delhi posted a pointed reminder this week: visa screening and vetting does not stop after a visa is granted.

"We use all available information in our visa screening and vetting to identify visa applicants who are inadmissible to the United States, including those who pose a threat to U.S. national security," the embassy said, referencing information collected through visa application forms and the expanded social media review process that went into effect in December 2025.

The message, while technically a restatement of existing policy, landed differently in the current climate. Indian H-1B holders have already faced mass appointment reschedulings since December due to the Online Presence Review — a new vetting layer that requires consular officers to examine social media and digital footprints for all H-1B applicants and dependents. That review has reduced the number of daily interviews at Indian posts and pushed wait times from weeks to months.

The embassy also clarified that India is not on the administration's 2025 travel ban list, which fully bars nationals from 12 countries and partially restricts seven others. That clarification, while reassuring, underscores how volatile the landscape has become — the fact that "India is not banned" now qualifies as good news tells you everything about where the baseline has moved.

## The World Cup factor

The timing of these outages could hardly be worse. The FIFA World Cup 2026 kicks off in the United States in June, and visa demand from virtually every country — including India, where football's popularity has surged — is spiking. The State Department has already introduced expedited processing for World Cup-related travel, including bond waivers for fan visas from certain countries. But the underlying infrastructure is the same creaking portal that cannot handle routine appointment bookings.

For Indian applicants, the World Cup adds competition for limited interview slots. Consular resources are finite, and every slot diverted to event-specific processing is a slot that an H-1B worker or a parent on a B-2 does not get.

## What applicants can do

Immigration attorneys advise Indian visa applicants to monitor USTravelDocs and CEAC status pages for restoration updates, screenshot every confirmation and payment receipt, and avoid traveling for stamping unless absolutely necessary. H-1B holders with valid I-797 approval notices who are already in the US should strongly consider postponing any international travel until the consular backlog eases — a calculus that has been standard advice since December but is now even more urgent.

The system was built for a different era of demand. It is not handling this one well, and the people waiting in the longest queues are, disproportionately, Indian."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
