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

article1_body = """The H-1B program survived a $100,000 fee, a court fight, and a 27 percent collapse in registrations. Now a Texas Republican wants to take away the one thing that made the visa worth having in the first place: the road to a green card.

On June 4, Congressman Chip Roy introduced the American White-Collar Worker Jobs Act of 2026. Most of the headlines fixated on its plan to scrap the lottery in favor of a wage-based selection process. That is the part employers will fight over. But buried in the text is a provision that would land hardest on Indians, because it targets the exact mechanism that an entire generation of Indian professionals has built their American lives around.

## The end of dual intent

For thirty-five years, the H-1B has carried a quietly radical feature called "dual intent." It lets a worker hold a temporary visa while openly pursuing permanent residency at the same time. No pretending you plan to leave. No fiction about maintaining a home abroad. You can arrive on an H-1B, file a green card petition the next week, and the government treats both intentions as legitimate.

Roy's bill kills that. Under the proposed law, every H-1B applicant would have to prove they maintain a residence abroad and do not intend to abandon it — the same standard applied to tourists and short-term business visitors. Declaring any interest in a green card would, in effect, make you ineligible for the visa that gets you in the door.

The bill goes further still. It would:

- **End the use of H-1B as a pathway to permanent residency** outright.
- **Shorten the visa from six years to two**, with no extensions while a green card is pending.
- **Eliminate Optional Practical Training (OPT)**, the post-graduation work window that bridges student life and full employment.
- **Bar companies that have recently conducted layoffs** from hiring H-1B workers at all.

## Why this is an India problem

Indians are not incidental to this story. They are the story. Indian nationals account for roughly 70 percent of H-1B holders and the overwhelming majority of the employment-based green card backlog — a queue so long that an Indian filing today in EB-2 or EB-3 can wait decades for a number to become available.

That backlog only exists because dual intent makes it survivable. The entire premise of waiting fifteen years for a green card is that you can keep living, working, and renewing your H-1B while you wait. Strip out dual intent and cap the visa at two years with no extensions, and the wait becomes mathematically impossible. You would be required to leave long before your priority date ever came current.

For the Indian on an H-1B today, the bill reframes a familiar anxiety. The $100,000 fee was a barrier to entry — painful, but something an employer might absorb. This is different. It attacks the exit. It tells the worker already inside the system that the destination they have been driving toward for a decade simply will not exist.

OPT's removal compounds the squeeze for students. For Indian graduates of American universities — the single largest foreign student cohort — OPT is the runway between a degree and an H-1B. Without it, the gap between graduation and a work visa becomes a cliff, and many would have no lawful way to stay employed long enough to enter the lottery at all.

## How worried should you be?

A draft bill is not a law. Roy's measure has cosponsors and the backing of restrictionist groups like the Federation for American Immigration Reform and US Tech Workers, and it builds on Rep. Eli Crane's separate proposal for a three-year pause on H-1B issuance. But it has not passed a committee, let alone a chamber, and it faces the full weight of an industry that depends on this pipeline.

What it signals matters more than its immediate odds. The political center of gravity on legal immigration has shifted from "how many" to "whether at all." A year ago the fight was over wage floors and lottery odds. Now a sitting congressman is proposing to dismantle the green card bridge entirely. For Indians weighing whether to stake their thirties and forties on a queue that Washington keeps threatening to dissolve, the calculation is getting harder to justify — and bills like this are exactly why.
"""

article2_body = """The visa was never really the prize. The green card at the end of it was. That is the calculation India's biggest IT firms appear to have quietly abandoned.

Official US data shows that the six largest Indian IT services companies — Tata Consultancy Services, Infosys, Cognizant, HCL Technologies, Wipro, and Tech Mahindra — collectively received 11,041 H-1B visas as of March 31, 2026. That is down 40 percent from roughly 18,469 the year before. For an industry that built its American business on the back of the H-1B, a drop of that size is not a blip. It is a strategy change.

## TCS bleeds, Infosys gains

The pain is not evenly spread. TCS, India's largest IT firm, saw the steepest fall — about 2,885 approvals, down by 3,242 from a year earlier. Infosys went the other way, picking up 3,195 approvals, the most of any firm in the group and the only one to improve on its prior-year number.

The divergence says less about each company's appetite for American talent than about how aggressively each is retreating from the old model. The H-1B that once shuttled thousands of engineers from Chennai and Hyderabad to client sites in New Jersey and Texas is being replaced by two things: more work done offshore from India, and more local hiring of workers already in the US who need no visa at all.

## The squeeze that forced the shift

The 40 percent collapse did not happen in a vacuum. It is the cumulative result of an administration that has spent a year making the H-1B more expensive and less reliable:

- A **$100,000 fee** on new petitions, imposed by proclamation in September 2025 — struck down by a federal judge on June 8, then promptly appealed, leaving employers in limbo.
- A **weighted, wage-based lottery** that favors higher-paid roles, disadvantaging the entry- and mid-level staffing roles that body shops and large outsourcers traditionally filled.
- A **proposed 33 percent hike in prevailing wages** from the Labor Department.
- Heightened scrutiny, denials, and processing delays across the board.

Faced with that, the rational corporate move is to stop fighting for visas and start moving the work. TCS Chairman N. Chandrasekaran told shareholders this month that the firm expects to slow hiring as it builds toward a workforce with as many AI agents as employees. The company's net headcount fell by more than 23,000 in the fiscal year ended March 2026.

## What it means for the Indian diaspora

For the Indian professional, this is the part that stings: the door is not just harder to walk through — your old employer may have stopped holding it open.

For two decades, a job at TCS or Infosys was the most reliable on-ramp to the United States for a middle-class Indian engineer. You joined in Bangalore, proved yourself, and got deputed onto an H-1B to a client site in America. That path is narrowing fast. With offshore work expanding and US hiring tilting toward people who are already here, the classic "get to America via your Indian employer" route is being quietly dismantled.

For Indians already in the US, the picture is more mixed. Local hiring favors those who hold a degree from an American university or already have work authorization — which describes a large slice of the existing diaspora. The shift rewards the immigrant who is already inside the system and penalizes the aspirant still in India hoping to be sent over.

And there is a longer-term worry. As the GCC model — global capability centers run by multinationals inside India — absorbs more of this work, the center of gravity for high-skilled Indian tech careers is migrating back home. That is good news for Bengaluru's economy. It is a harder story for the family that assumed the American chapter was still available to write.

The 40 percent number, in other words, is not just a visa statistic. It is the sound of a well-worn migration path being paved over — and the diaspora would do well to notice which doors are closing while everyone watches the courtroom drama over the $100,000 fee.
"""

article3_body = """For months the complaint sat in WhatsApp groups and Reddit threads: an H-1B stamping appointment booked, then cancelled, then rebooked months out, then cancelled again. Jobs left hanging. Children's school years disrupted. Now India's government has made it official.

The Ministry of External Affairs has formally raised the issue of prolonged H-1B visa appointment delays and repeated rescheduling with the United States — in both New Delhi and Washington. It is a notable escalation: a bilateral diplomatic flag on what had been treated as an administrative backlog.

## The problem in plain terms

The mechanics are simple and brutal. An Indian on an H-1B who leaves the US — for a family emergency, a wedding, a parent's illness — generally needs a valid visa stamp in their passport to return. If their stamp has expired, they must book a consular appointment in India to get a new one. And those appointments, by the State Department's own admission, can carry waits of six, eight, even twelve months.

Worse than the wait is the unpredictability. Applicants describe securing a slot only to have it cancelled, then being pushed months further down the calendar. For someone whose US job, mortgage, and children's enrollment all depend on getting back, an open-ended delay is not an inconvenience. It is a life on hold.

## Washington's answer: domestic renewal

There is a fix in motion, and it is aimed squarely at India. The State Department plans to launch a pilot program for domestic renewal of certain H-1B visas beginning in December — letting eligible workers renew their stamp without leaving the country at all.

Julie Stufft, Deputy Assistant Secretary of State for Visa Services, was blunt about the scale of the Indian problem. "In India, the demand is still very high. The wait time of 6, 8, and 12 months is not what we need," she said, adding that it is "not indicative of how we view India."

The pilot will issue 20,000 visas over its first three months to people already inside the US, and "the vast majority of those will be Indian nationals." The logic is twofold: keep Indian professionals from having to fly home for a routine renewal, and free up the consulates in India to focus on first-time applicants stuck in the queue.

## Why this matters for the diaspora

This is one of the rare immigration stories of 2026 that points in a hopeful direction for Indians — and it matters for a specific, practical reason.

The single most paralyzing feature of life on an H-1B is the travel trap: the fear that leaving the US, even briefly, could strand you abroad for the better part of a year waiting for a stamp. It is why many Indian professionals go years without visiting aging parents, skip weddings and funerals, and treat international travel as a luxury they cannot risk. Domestic renewal, if it works, dismantles that trap. You could renew your status without ever boarding a plane to a consulate that may not see you for a year.

The catch is in the word "pilot." Twenty thousand visas is a fraction of the Indian H-1B population, and eligibility rules — which categories qualify, who is in the first tranche — will be spelled out in a forthcoming Federal Register notice. Until that notice lands, no one should rebook a long-delayed India trip on the assumption they are covered.

Still, the combination is telling: India's government formally pressing the issue, and the US explicitly designing relief around Indian nationals. For a diaspora that has spent the year absorbing fee shocks, wage hikes, and bills threatening to dismantle the green card pathway, a program built to keep Indian families from being stranded is a small but real piece of good news — provided Washington delivers on the December timeline.
"""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The H-1B Bill That Would Make the Green Card Dream Mathematically Impossible for Indians",
        "subheadline": "Chip Roy's American White-Collar Worker Jobs Act would scrap dual intent, cap the visa at two years, and kill OPT — attacking the exit, not just the entrance.",
        "slug": make_slug("chip-roy-white-collar-jobs-act-dual-intent-opt-green-card-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold roughly 70% of H-1B visas and dominate the green card backlog; this bill would eliminate the dual-intent mechanism that makes a decade-long wait survivable, making permanent residency unreachable for the workers already in the queue.",
        "tags": ["h1b", "chip-roy", "green-card", "opt", "dual-intent", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/world/us-lawmaker-proposes-major-h-1b-visa-overhaul-and-end-to-green-card-pathway/article69661234.ece"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/us-bill-eyes-major-h-1b-overhaul-seeks-to-end-green-card-track"},
            {"name": "Rep. Chip Roy (Press Release)", "url": "https://roy.house.gov/media/press-releases"}
        ]),
        "score_total": 86,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Chip_Roy_118th_Congress.jpg",
        "image_caption": "Congressman Chip Roy (R-TX), who introduced the American White-Collar Worker Jobs Act of 2026.",
        "image_attribution": "Wikimedia Commons",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian IT Giants' H-1B Visas Fell 40% in a Year — and the Old Road to America Is Being Paved Over",
        "subheadline": "TCS took the steepest hit while Infosys gained, as the big six outsourcers shift work offshore and hire locally instead of fighting for visas.",
        "slug": make_slug("indian-it-firms-h1b-visas-fell-40-percent-offshore-tcs-infosys"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For two decades a job at TCS or Infosys was the most reliable on-ramp to the US for middle-class Indian engineers; the 40% drop in their H-1B approvals signals that the classic 'get to America via your Indian employer' path is being dismantled.",
        "tags": ["h1b", "tcs", "infosys", "offshore", "indian-it", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "LiveMint", "url": "https://www.livemint.com/companies/news/top-it-firms-h-1b-visas-slump-40-tcs-worst-hit-while-infosys-gains-11748000000000.html"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-tcs-chair-says-ai-agents-may-equal-headcount-dampen-hiring-2026-06-09/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36706459/pexels-photo-36706459.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A software developer at work; Indian IT firms are shifting more work offshore as US H-1B approvals fall.",
        "image_attribution": "Pexels",
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Formally Confronts Washington Over H-1B Stamping Delays — and a December Fix Is Aimed at Indians",
        "subheadline": "The MEA has raised months-long appointment waits with the US, as the State Department prepares a domestic visa renewal pilot built largely for Indian nationals.",
        "slug": make_slug("india-mea-h1b-stamping-delays-domestic-renewal-pilot-december"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The travel trap — fear that leaving the US could strand you abroad for months awaiting a visa stamp — keeps Indian professionals from visiting aging parents; a domestic renewal pilot issuing 20,000 visas, mostly to Indians, could dismantle that trap.",
        "tags": ["h1b", "visa-stamping", "domestic-renewal", "mea", "consulate", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "NRI Globe", "url": "https://nriglobe.com/nri-news-roundup-june-8-2026/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/us-to-launch-new-plan-for-work-visas-in-december-likely-to-benefit-the-indians-most/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A traveler holds an open passport; H-1B holders face months-long waits for visa stamping appointments in India.",
        "image_attribution": "Pexels",
        "body": article3_body
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        wc = len(art["body"].split())
        print(f"OK  {art['slug']}  ({wc} words)")
    except Exception as e:
        print(f"ERR {art['slug']}: {e}")
