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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Pull the Officers, Ground the Planes — Inside DHS's Airport Ultimatum",
        "subheadline": "Homeland Security Secretary Mullin threatened to yank CBP officers from airports in sanctuary cities, with the World Cup eight days out and millions of Indian diaspora travelers caught in the crossfire.",
        "slug": make_slug("mullin-airport-shutdown-threat-sanctuary-cities-world-cup-indian-travelers"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian Americans who fly through Newark, SFO, LAX, and Chicago — the four busiest hubs for India-bound travel — would face chaos if CBP officers were pulled. H-1B workers returning from visa stamping, parents visiting on B-1/B-2 visas, and OCI cardholders heading home for summer would all be stranded.",
        "tags": ["cbp", "airport", "world-cup", "sanctuary-city", "mullin", "newark"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/us/trump-homeland-secretary-testifies-before-senate-panel-amid-airport-threats-2026-06-02/"},
            {"name": "The Oklahoman (AP)", "url": "https://www.oklahoman.com/story/news/politics/2026/06/02/mullin-testifies-to-senate-amid-airport-restriction-threats-detention-protests/84838163007/"},
            {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/news/watch-live-markwayne-mullin-testifies-before-senate-on-budget-request/"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/law-order/3487649-tensions-rise-at-newark-airport-amid-immigration-policy-concerns"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/A_U.S._Customs_and_Border_Protection_operations_related_to_international_travelers_and_luggage_arriving_at_Baltimore-Washington_International_Thurgood_Marshall_Airport_on_February_27%2C_2025_-_10.jpg/1280px-thumbnail.jpg",
        "body": """The threat landed on a Thursday, between a press conference and a news cycle. DHS Secretary Markwayne Mullin said he was prepared to pull U.S. Customs and Border Protection officers from Newark Liberty International Airport unless local law enforcement secured the area around the Delaney Hall detention facility in Newark, where protesters had been gathering for weeks over conditions inside the ICE-contracted jail.

By Monday, Mullin had backed off — New Jersey State Police had closed the protest perimeter, and he said there was "no need" to halt international flight processing at Newark "as long as we continue to have this partnership with local and state law enforcement." But the threat was not retracted. It was shelved. And the list of airports Mullin has flagged for possible CBP pullbacks reads like a directory of Indian diaspora air travel: San Francisco, Los Angeles, Chicago O'Hare, Boston, Denver, Philadelphia, Seattle.

## What a CBP Pullback Actually Means

When Mullin says "pull officers," he means withdrawing the federal agents who process every international passenger arriving in the United States. No CBP, no passport stamps. No passport stamps, no entry. Airlines would be forced to cancel inbound international flights or divert them to other airports — assuming those airports have the capacity, which most do not.

Major airline, travel, and business groups warned last week that barring border processing at Newark or other major airports could strand thousands of tourists and Americans trying to get home, and shut down crucial cargo shipments. Newark is a major United Airlines hub and the primary international gateway for the New York metro area's 20 million residents.

The economic math is blunt. Industry groups estimate the sanctuary city airport threat covers terminals handling 68 million international passengers annually. A shutdown at even one major hub could trigger a $70 billion economic ripple.

## The World Cup Factor

The timing could not be worse. The FIFA World Cup kicks off on June 11 — eight days from now. Eight matches, including the final, will be played at MetLife Stadium in East Rutherford, New Jersey, a short drive from Newark airport. Millions of foreign visitors are expected. FIFA's visa bond waiver program, which the U.S. negotiated to smooth entry for ticket holders, depends entirely on CBP officers being present to process arrivals.

Mullin's hearing before the Senate Appropriations Subcommittee on Tuesday — his first congressional appearance as DHS chief — was dominated by the airport standoff and a $118.4 billion FY2027 budget request that allocates $23 billion for CBP and $10.5 billion for ICE. In his opening remarks, Mullin urged Democrats to approve funding, saying federal immigration officers have "been willing to do the job for free."

## Why Indian Travelers Should Be Paying Attention

The airports on Mullin's list are not random. They are sanctuary cities — jurisdictions that limit cooperation with federal immigration enforcement. They also happen to be the cities where Indian Americans live, work, and fly.

Consider the exposure. Newark and JFK handle the bulk of nonstop flights to Delhi, Mumbai, and Hyderabad. SFO and LAX are the gateways for the Bay Area and Southern California's massive Indian tech workforce. Chicago O'Hare connects the Midwest's Indian diaspora to the subcontinent. These are the airports H-1B workers transit through after visa stamping at Indian consulates — a journey that already involves six-month social media vetting delays, $100,000 fees, and the ever-present risk of administrative processing.

A CBP pullback at any of these airports would not just inconvenience travelers. It would strand H-1B workers mid-renewal, separate families waiting for B-1/B-2 visitors to land, and create a logistical nightmare for OCI cardholders who fly between the two countries routinely.

## The Bigger Picture

Mullin's airport threat is a pressure tactic aimed at sanctuary cities, not a policy designed to improve immigration processing. But the collateral damage falls on legal travelers, legal immigrants, and legal visa holders who have no involvement in the detention protests that triggered the standoff.

The DHS FY2027 budget tells its own story: $23 billion for the agency that stamps passports and $10.5 billion for the agency that deports people, while USCIS — the agency that actually processes visas, green cards, and work permits — continues to run primarily on application fees from the very immigrants it serves. The enforcement apparatus grows. The processing apparatus does not.

For Indian Americans planning summer travel — and there are hundreds of thousands who fly to India between June and August — the message is sobering. Your flight home now depends on whether Mullin and a New Jersey governor can agree on protest management outside a detention center you have never visited and will never enter.

The World Cup starts in eight days. The airports are open. For now."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Clock Starts Now — DHS Wants to Put an Expiration Date on Every Student Visa in America",
        "subheadline": "A proposed rule would end decades of open-ended F-1 stays, impose four-year caps with mandatory USCIS extensions, slash the grace period in half, and force hundreds of thousands of Indian students into a bureaucratic gauntlet that the agency is not equipped to handle.",
        "slug": make_slug("dhs-duration-of-status-f1-student-visa-four-year-cap-indian"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals are the second-largest group of international students in the U.S. and account for the largest share of H-1B lottery applicants. The proposed rule would disproportionately affect Indian students in STEM programs that run longer than four years, compress the critical job-search window after graduation, and potentially trigger unlawful presence bars for students who overshoot a fixed deadline.",
        "tags": ["f1-visa", "student-visa", "duration-of-status", "opt", "cpt", "uscis"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/02/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/immigration/white-house-reviewing-rule-to-limit-foreign-students-status"},
            {"name": "ICEF Monitor", "url": "https://monitor.icef.com/2026/05/us-to-end-duration-of-status-for-f-j-and-i-visas/"},
            {"name": "Berardi Immigration Law", "url": "https://berardiimmigrationlaw.com/dhs-proposed-rule-end-of-duration-of-status-for-f-1-j-1/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/29229903/pexels-photo-29229903.jpeg",
        "body": """For decades, the deal was simple. If you were an international student in America on an F-1 visa, you were admitted for "duration of status" — a bureaucratic phrase that meant you could stay as long as you were enrolled in a legitimate program, maintained your visa requirements, and kept your paperwork current with your university. Your I-94 arrival record simply read "D/S." No fixed end date. No clock ticking.

DHS wants to change that. On May 5, the Department of Homeland Security sent a final rule to the White House Office of Management and Budget that would replace the duration of status framework with a fixed admission period of up to four years for most F-1 students. The rule, which has been moving through the regulatory pipeline since August 2025, is expected to be finalized and published by the end of June, with implementation targeting the fall 2026 semester.

## What the Rule Would Do

The changes are sweeping. Under the proposed framework:

- **Four-year cap**: Most F-1 students would be admitted for a maximum of four years. Any time beyond that — whether for a longer PhD program, a second degree, or OPT — would require filing a formal extension of stay with USCIS.
- **Grace period halved**: The current 60-day grace period after a program ends would be cut to 30 days. That is the window students use to pack up, settle affairs, find a job, or file for a change of status.
- **First-year restrictions**: Students would face new limits on changing their program or major within the first year of enrollment.
- **Unlawful presence clock**: Under the current D/S system, students only accrue unlawful presence if a judge or USCIS formally finds a status violation. Under the new rule, unlawful presence would begin automatically the day a fixed admission period expires — triggering the three-year and ten-year reentry bars that have devastated countless immigration cases.
- **No more deference**: The rule would also remove the regulatory codification of USCIS's policy of deferring to prior adjudications, meaning every extension filing could be adjudicated from scratch.

## The Indian Student Problem

Indian nationals are the second-largest group of international students in the United States, behind China. They account for a disproportionate share of graduate programs in STEM fields — the very programs most likely to exceed four years.

A PhD in computer science at a major research university takes five to seven years. An MD residency can run six. A student who enters a four-year engineering program, graduates, applies for OPT, and then enters a STEM OPT extension is already pushing past the four-year mark without having done anything unusual. Under the new rule, each of these transitions would require a formal USCIS filing — with processing times, fees, and the risk of denial or delay.

"The duration of status rule that has been proposed is going to fundamentally change the flexibility that students have had to apply for Optional Practical Training and Curricular Practical Training," said Danielle Goldman, co-founder and CEO of Build, an immigration advisory firm, in a recent interview with The Indian Eye.

The Day 1 CPT pathway — the backup plan that thousands of Indian graduates use when they lose the H-1B lottery — would narrow significantly. Goldman noted that under the proposed rule, students who already hold a master's degree would struggle to justify enrolling in another program solely for work authorization. "For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working,'" she said.

## The USCIS Capacity Question

Here is the math that makes immigration lawyers nervous. USCIS's own projections estimate that the rule would generate approximately 300,000 extension of stay requests annually from F-1 students alone, with additional filings from J-1 exchange visitors and I visa holders. The agency's current processing time for I-539 change of status applications — the same form students would use — is already running at six months.

That means a student whose fixed admission period expires in August could file for an extension and wait until February for a decision, assuming no requests for evidence or administrative delays. During that waiting period, their status is uncertain. Their work authorization is uncertain. Their ability to travel is uncertain.

USCIS is already drowning in a 12-million-case backlog. I-485 employment-based adjustments take 10 to 35 months. I-765 employment authorization documents take up to 19.5 months. Adding 300,000 annual extension filings to this pipeline is like pouring water into a cup that is already overflowing.

## The Grace Period Cut

The reduction from 60 to 30 days may sound minor. It is not. The 60-day grace period is the window during which a graduating student can interview for jobs, negotiate offers, and — critically — have an employer file an H-1B cap-exempt petition or apply for a change of status. Thirty days compresses that timeline to the point where students need to have employment lined up before graduation, not after.

For Indian students in AI, machine learning, software engineering, and data science — fields where the hiring process routinely takes four to eight weeks — a 30-day window is functionally no window at all.

## What Happens Next

The final rule is at OMB now. Once cleared, it will be published in the Federal Register with a 60-day implementation timeline. NAFSA, the Association of International Educators, has told institutions to prepare for the rule to take effect in time for fall 2026 arrivals.

Goldman warned that the impact extends beyond students. "There's no doubt about it that this is going to have a massive impact on the companies that are in desperate need of top talent," she said. Foreign nationals make up a substantial portion of the U.S. AI talent pool, and companies may either struggle to recruit or be forced into alternative visa categories — O-1 visas, cap-exempt H-1Bs, or simply moving positions offshore.

The proposed rule is not yet law. Public comment periods have closed. Legal challenges from university groups and education organizations are expected. But the direction is unmistakable: the open-ended student visa that allowed generations of Indian engineers, scientists, and entrepreneurs to build careers in America is being replaced with a ticking clock and a filing cabinet full of extension requests that USCIS cannot process fast enough to keep up.

Four years. That is what the government thinks your education should take. The research, the internships, the OPT — figure it out."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['headline']}")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
