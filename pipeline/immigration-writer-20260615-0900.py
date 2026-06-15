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

body1 = """A $250,000 problem now has a one-fifth-the-price answer, and it is sitting in Bengaluru.

That is the arithmetic American technology executives are running after the Trump administration's $100,000 supplemental fee on new H-1B petitions, and it is reshaping where Indian engineers will spend their careers — not in San Jose, but increasingly at home.

## The new math of moving an engineer

Greyhound Research puts the all-in cost of bringing a mid-level engineer to the United States today at roughly $250,000 per person, once salary, the new visa fee, and relocation are stacked together. The same headcount in India costs a fifth to a sixth of that. Forrester estimates the fee alone could add about $2 billion in costs if service providers file as many petitions as they did in 2025 — a number large enough that most simply will not.

The response is not a tweak. "We are witnessing a full-scale architectural pivot in how US enterprises access and deploy global tech talent," Sanchit Vir Gogia of Greyhound Research told Computerworld. "The old playbook — move the best minds to the US, integrate them into HQ, and control innovation centrally — is breaking apart."

## Why the lottery rewrite makes it worse

The fee does not stand alone. Beginning with the FY 2027 cap season, USCIS replaced the decades-old random lottery with a wage-weighted system that hands Level IV positions four entries and Level I just one. Entry-level and consulting roles — the bread and butter of the India-based IT services model — now draw the worst odds in the pool while carrying the heaviest fee burden. Staffing firms that once flooded the lottery with tens of thousands of registrations are pulling back sharply.

For the big Indian IT houses, the message is unambiguous: the onsite-offshore model that defined Infosys, TCS, and Wipro for a generation no longer pencils out. Work that used to justify a US visa now stays in Indian delivery centers, and the global capability centers (GCCs) that multinationals run in Bengaluru, Hyderabad, and Pune are absorbing the higher-value work that used to require a flight to America.

## What it means for the Indian American on an H-1B

If you are already in the United States on an H-1B, the immediate sting is muted — the $100,000 fee applies to new petitions filed from abroad, not to extensions or to those changing status from an F-1 already inside the country. But the second-order effects land squarely on the diaspora.

First, fewer new arrivals means a thinner pipeline of the colleagues, cousins, and recruits who have historically followed the same path. The community that built itself around the H-1B is being throttled at the front door.

Second, the work is migrating to where the workers are. Analysts describe a "permanent structural shift" in which India has become the second-largest technology talent base for most global enterprises. For Indian professionals weighing whether to chase a US posting or build a career in a Bengaluru GCC, the calculus has flipped. The prestige assignment increasingly sits in India, not Silicon Valley.

Third, for those already here and eyeing the green card finish line, a shrinking onshore footprint at the big employers can mean fewer internal transfers, leaner US teams, and more pressure to justify a role that now costs a quarter-million dollars to seed from scratch.

## The longer game

None of this happens cleanly. Remote-first models carry their own coordination tax, and a generation of US managers built their careers on having talent in the next cubicle. But cost gravity is relentless. Bringing a mid-level engineer to America at $250,000 against $40,000-$50,000 for the same person in India is not a gap that quarterly earnings calls forgive.

The irony is hard to miss. A policy sold as protection for American workers is accelerating the offshoring it was meant to curb — and handing India the higher-end work it has spent two decades trying to win. For the diaspora, the H-1B was never just a visa. It was the on-ramp to a life in America. That on-ramp is narrowing, and the traffic is finding another road home.
"""

body2 = """The State Department's new $750 fast-pass to a US visa interview arrives just in time for the World Cup crowd. For the Indian engineer waiting on an H-1B stamp, it is worth precisely nothing.

That is the quiet catch buried in the temporary final rule published in the Federal Register on June 9. The expedited appointment service — which lets applicants jump the queue for a slot within 10 business days — applies only to B1/B2 visitor visas. The H and L visas that move skilled Indian workers across the Pacific are excluded.

## The backlog the fee does not touch

US consulates in India remain choked. Foreign nationals seeking employment-based nonimmigrant visas — the H-1B, the L-1 intra-company transfer — face appointment waits of 75 to more than 125 days across Chennai, Hyderabad, Kolkata, Mumbai, and New Delhi. The cause is no mystery: demand has climbed for months while consular staffing at the US mission to India has not.

The $750 premium, sold by the State Department as an "optional premium addition," was designed for a different crowd entirely. It runs as a pilot from July 1 to December 31, timed to the more than one million foreign tourists FIFA's 2026 World Cup is expected to draw to American stadiums. The department projects roughly 25,705 applicants a year will buy the upgrade, generating about $19.3 million in revenue. Every one of those is a tourist or business visitor — not a worker.

## $935 to visit, and a wall for everyone else

For the B1/B2 applicant, the deal is steep but real: $750 on top of the standard $185 fee, for a total near $935, in exchange for skipping waits that can stretch to two years at the worst-hit posts. "It's a lot of money in this country," New York immigration attorney Michael Cataliotti told USA TODAY, "but it's an exorbitant amount in many of the countries where people are applying for these visas."

The department is careful to note the fee buys a faster appointment, not faster processing — "This service will not expedite any processing steps, including any time needed for administrative processing." Pay the premium, and you still wait out any 221(g) security check like everyone else.

## Why this lands hard on the diaspora

For Indian Americans, the gap between the two tracks is the whole story.

A family in New Jersey trying to bring elderly parents over for a wedding or the birth of a grandchild can now, in theory, buy down a punishing B1/B2 wait — if their parents are applying at one of the still-limited posts where the pilot operates. That is genuine relief for the visitor-visa crowd, even at $935 a head.

But the H-1B professional whose visa stamp expired while they were inside the United States, and who must now travel to a consulate in India to get it renewed, has no such option. They are stuck in the 75-to-125-day employment-visa queue with no premium lane to buy. A routine trip home for a family emergency can turn into a months-long exile from job, mortgage, and children's school — the precise risk that has long made stamp-dependent workers dread leaving US soil.

The interview-waiver "Dropbox" route, consolidated in New Delhi since March 2024, remains the one real workaround for eligible renewals, and applicants can still submit waiver documents at VACs in Chennai, Hyderabad, Kolkata, Mumbai, or New Delhi. But Dropbox eligibility has narrowed under tightened rules, and those who fall outside it face the full in-person backlog.

## The signal beneath the fee

The pilot tells you what Washington is optimizing for. With the World Cup and the 2028 Los Angeles Olympics ahead, the priority is moving tourists through the gate — visitors who spend money and leave. The skilled worker, who stays, builds, and eventually petitions for a green card, gets no fast lane.

For a community that built itself on the employment visa, the message stings. The government has found the staff and the system to expedite a tourist for $750. It simply has not chosen to do the same for the engineer who keeps the lights on at half of Silicon Valley.
"""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A $250,000 Engineer or a $45,000 One — Trump's H-1B Fee Is Sending the Work Back to India",
        "subheadline": "The $100,000 fee plus the new wage-weighted lottery has flipped the math on bringing Indian talent to America. Analysts call it a permanent structural shift toward India's GCCs.",
        "slug": make_slug("h1b-100k-fee-offshoring-cost-shift-india-gcc-talent-pivot"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The H-1B was the on-ramp to American life for Indian professionals; the new fee economics are narrowing it and pulling the higher-value work back to India's capability centers, reshaping where the next generation of diaspora engineers builds their careers.",
        "tags": ["h1b", "offshoring", "gcc", "indian-it", "uscis", "tech-talent"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Computerworld", "url": "https://www.computerworld.com/article/restrictive-h1b-policies-drive-tech-talent-back-to-india.html"},
            {"name": "Reuters", "url": "https://www.reuters.com/legal/government/the-100000-question-navigating-new-h-1b-lottery-system-2026-03-24/"},
            {"name": "Lexology / Greenberg Traurig", "url": "https://www.lexology.com/library/detail.aspx?g=uscis-finalizes-wage-weighted-h1b-cap-selection-rule"}
        ]),
        "score_total": 84,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Infosys_Mysore_Campus.jpg/1280px-Infosys_Mysore_Campus.jpg",
        "image_caption": "An Infosys campus in India, where global capability centers are absorbing higher-value work once tied to US visas.",
        "image_attribution": "Wikimedia Commons",
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "$750 Buys a Tourist a Fast Visa Slot. The H-1B Worker Stuck in India Gets Nothing",
        "subheadline": "Washington's new expedited-interview pilot covers only B1/B2 visitor visas, leaving Indian skilled workers in a 75-to-125-day employment-visa backlog with no premium lane to buy.",
        "slug": make_slug("750-dollar-expedite-pilot-b1b2-only-h1b-workers-india-backlog-excluded"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian American families can now buy down punishing visitor-visa waits for visiting parents, but H-1B professionals who must renew their stamp in India remain trapped in a months-long backlog with no fast-track option — turning a routine trip home into a career risk.",
        "tags": ["visa-stamping", "consulate", "h1b", "b1b2", "dropbox", "state-department"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "USA TODAY", "url": "https://www.usatoday.com/story/travel/2026/06/10/750-fee-fast-track-us-visa-interviews/"},
            {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/news/state-department-750-fee-fast-track-visa-interviews"},
            {"name": "Fragomen", "url": "https://www.fragomen.com/insights/update-on-visa-appointment-backlogs-at-u-s-consulates-in-india.html"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/United_States_Passport_Visa_Pages.jpg/1280px-United_States_Passport_Visa_Pages.jpg",
        "image_caption": "Visa pages inside a passport; the State Department's new $750 expedite pilot applies only to B1/B2 visitor visas, not H or L work visas.",
        "image_attribution": "Wikimedia Commons",
        "body": body2
    }
]

# Word count check
for art in articles:
    wc = len(art["body"].split())
    print(f"[wc] {art['slug']}: {wc} words")

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK {art['slug']}")
    except Exception as e:
        print(f"ERR {art['slug']}: {e}")
