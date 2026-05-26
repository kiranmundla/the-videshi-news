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
        "headline": "Rubio Freezes Student Visa Appointments Worldwide — And Indian Fall Enrollments Are Already in Freefall",
        "subheadline": "The State Department has halted all new F-1, M-1, and J visa interview slots globally while it builds a social media screening apparatus. For the 200,000-plus Indian students planning to start at American universities this fall, the clock just stopped.",
        "slug": make_slug("rubio-freezes-student-visa-appointments-india-fall-enrollment"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian students are the second-largest group of international students in the US, and the F-1 pipeline feeds directly into OPT and H-1B employment. A freeze on new appointments during peak summer visa season threatens fall 2026 enrollment and disrupts the entire career pathway that hundreds of thousands of Indian families have built their plans around.",
        "tags": ["f1-visa", "student-visa", "rubio", "social-media-screening", "indian-students"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Politico (via Economic Times)", "url": "https://eximguru.com/export-import-news/foreign-exchange/u-s-halts-new-student-116495.aspx"},
            {"name": "Brookings Institution", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"},
            {"name": "Today FM", "url": "https://todayfmlive.com/trump-administration-orders-embassies-to-halt-student-visa-appointments-amid-expanded-social-media-vetting/"},
            {"name": "CNN", "url": "https://www.cnn.com/travel/us-tourism-impact-immigration-policies/index.html"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6147148/pexels-photo-6147148.jpeg",
        "image_caption": "Photo by Keira Burton / Pexels",
        "body": """Secretary of State Marco Rubio has ordered every U.S. embassy and consulate on the planet to stop adding new interview appointments for student and exchange visitor visas — effective immediately. The freeze covers F-1 (academic students), M-1 (vocational students), and J-1 (exchange visitors), and it will remain in place "until further guidance is issued."

The directive, first reported by Politico, is tied to plans for expanded social media vetting of student visa applicants. Rubio's cable to diplomatic posts did not specify what content screeners would flag, but referenced executive orders on terrorism and antisemitism — suggesting the apparatus will cast a wide net over applicants' online lives before they ever set foot in an American classroom.

## The Timing Could Not Be Worse

Summer is peak visa interview season for fall enrollment. Indian students typically book consulate appointments in Chennai, Hyderabad, Mumbai, New Delhi, and Kolkata between May and July. The freeze lands squarely in that window.

The damage is already accumulating before this latest order. Brookings projects a 29% decline in new F-1 visa issuances for 2025, based on State Department data through the first eight months of the calendar year. A separate survey by the Institute for International Education found 17% fewer international students began studies at U.S. universities in fall 2025 compared to the prior year. NAFSA estimates that decline alone will cost the American economy $1.1 billion and nearly 23,000 jobs.

Now layer on a worldwide appointment freeze during the busiest filing period of the year.

## What This Means for Indian Students

India is the second-largest source of international students in the United States, behind China. Chinese and Indian students together account for roughly 43% of all F-1 visas issued. The pipeline matters beyond the degree itself: 72% of international graduates participate in Optional Practical Training after completing their programs, and OPT is the bridge that connects an Indian student's MS in computer science at a state university to an H-1B petition at a tech company in the Bay Area.

That bridge is under attack from multiple directions. USCIS Director Joseph Edlow has indicated he wants to effectively end OPT. Former DHS Secretary Kristi Noem wrote that the department is "reevaluating whether the current regulatory framework — including the scope and duration of practical training — appropriately serves U.S. labor market, tax, and national security interests." If OPT shrinks or disappears, the student visa itself becomes less valuable — and the freeze makes even obtaining one an open question.

For families in Hyderabad, Pune, or Coimbatore who have already paid deposits, booked housing, and registered for fall courses, the freeze introduces a specific kind of anxiety: not a rejection, but silence. No new slots. No timeline. No clarity on what the social media screening will look for, how long it will take, or whether a meme shared three years ago will become grounds for denial.

## The Screening Nobody Has Defined

The social media vetting proposal remains remarkably vague. The State Department announced last June that applicants for student visas would be required to make their social media accounts public for screening against "threats to U.S. national security." A follow-up cable to embassies provided some additional direction on what investigators should examine, but the department has offered limited detail on how standards will be applied across cases.

This ambiguity is the quiet part of the story. A screening regime that lacks clear criteria will inevitably produce inconsistent outcomes — one consular officer in New Delhi flagging a post that another in Chennai would ignore. For applicants, the rational response to that uncertainty is self-censorship or withdrawal from the process entirely.

## The Competition Is Watching

Other countries are not standing still. China unveiled its K-visa late last year — the Chinese equivalent of the H-1B — in an explicit bid to attract foreign talent. Canada and Germany have both expanded skilled immigration pathways. Evidence suggests that as U.S. restrictions tighten, multinational corporations are offshoring more work to India, Canada, and China rather than fighting the visa system.

The irony is sharp: America's student visa pipeline has historically been its greatest talent acquisition tool. International students contributed $42.9 billion to the U.S. economy last year. They subsidize domestic students at public universities through full-tuition payments. And a significant share of them become the engineers, researchers, and founders who power the industries Washington claims to care about.

Rubio's freeze treats that pipeline as a security liability. The countries lining up to absorb the redirected flow see it as an opportunity."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The 'One Big Beautiful Bill' Hits the Senate — Three Republicans Hold Every Indian Immigrant's Future in Their Hands",
        "subheadline": "The House passed Trump's sweeping budget and immigration bill by a single vote. It contains the $100,000 H-1B fee, a remittance tax, and provisions that would reshape legal immigration for a generation. Now three GOP senators stand between the bill and the president's desk.",
        "slug": make_slug("one-big-beautiful-bill-senate-indian-immigrants-fate"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The OBBBA is a single legislative vehicle carrying nearly every immigration change that affects Indian professionals — the $100K H-1B fee, the remittance levy on money sent home, immigration enforcement expansion, and potential green card pathway changes. For NRIs tracking multiple policy threats, this bill is where they all converge.",
        "tags": ["obbba", "one-big-beautiful-bill", "h1b", "remittance-tax", "senate", "legislation"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Today In US And World", "url": "https://todayinusandworld.com/big-beautiful-bill-senate-holdouts/"},
            {"name": "Congressional Budget Office", "url": "https://www.cbo.gov/"},
            {"name": "Visa Verge", "url": "https://visaverge.com/"},
            {"name": "The Dispatch", "url": "https://thedispatch.com/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32177176/pexels-photo-32177176.jpeg",
        "image_caption": "Photo by Ramaz Bluashvili / Pexels",
        "body": """The One Big Beautiful Bill Act cleared the House of Representatives before the Memorial Day recess by the narrowest possible margin: 215 to 214. It is now the Senate's problem.

For Indian immigrants — whether on H-1B visas, waiting in green card queues, sending money to family back home, or all three simultaneously — this bill is not one threat. It is a collection of them, bundled into a single piece of legislation moving through budget reconciliation, which means it needs only 51 Senate votes to pass and cannot be filibustered.

The math in the Senate is this: Republicans hold 53 seats. Three of their own have signaled opposition. Majority Leader John Thune can lose exactly two members and still pass the bill with Vice President JD Vance casting a tiebreaker. As of the Memorial Day recess, he appears to have 50 firm yes votes and three senators who are, in varying degrees, unwilling to become the 51st.

## The Three Holdouts

Senator Thom Tillis of North Carolina objects primarily to the bill's Medicaid provisions — his state's rural hospitals depend heavily on Medicaid funding, and the projected loss of 7.5 to 10 million beneficiaries under the bill's work requirements creates a political problem he has not yet agreed to absorb.

Senator Rand Paul of Kentucky opposes the bill from the opposite direction. It does not cut spending enough. Paul has maintained this position on Republican legislation for over a decade, and his colleagues have largely stopped trying to move him with spending arguments.

Senator Susan Collins of Maine has voiced the broadest objections — Medicaid cuts, procedural concerns, and the principle that a bill of this magnitude should not be rushed through on a political timetable. Collins is the senator most likely to be actively negotiating with Thune's office through the recess.

None of these holdouts are primarily motivated by immigration provisions. That is the particular cruelty of reconciliation: immigration changes that would reshape the lives of hundreds of thousands of Indian professionals are attached to a $3.4 trillion fiscal package where the dominant arguments are about Medicaid and tax cuts.

## What Is in It for Indian Immigrants

The bill's immigration provisions are scattered across its hundreds of pages, but they converge on a few key pressure points.

**The $100,000 H-1B fee.** First proposed last September, this fee applies to new H-1B petitions — not renewals or status changes. The DHS secretary retains discretion to waive it for occupations deemed in the "national interest," but only about 85 companies have paid the fee so far, and the provision is already tied up in federal court challenges led by the U.S. Chamber of Commerce. If the bill passes with this fee intact, it becomes statutory rather than administrative — far harder to challenge or reverse.

**The remittance levy.** A 1% tax on remittances sent out of the United States. Indians sent $125 billion in remittances globally in 2024, with the U.S. being the largest single source. The levy falls on every wire transfer, every hawala equivalent that passes through the formal system, every birthday gift and emergency medical fund routed through Western Union or Wise. For a community that maintains deep financial ties across two countries, this is not a rounding error.

**Immigration enforcement expansion.** The bill funds additional immigration enforcement measures and includes provisions the Senate parliamentarian may or may not strike under the Byrd Rule, which restricts reconciliation bills to items with direct budgetary impact. Several immigration-related provisions from the House version are at risk of being removed before the Senate vote.

**The $18,000 in-absentia fine.** DHS published a proposed rule in the Federal Register on May 19 implementing an $18,000 fine for immigrants who miss removal hearings — a provision enabled by the OBBBA. The current fine, which DHS describes as "insufficient to cover deportation costs," would increase dramatically.

## The Moody's Backdrop

The Senate debate arrives in a fiscal context that did not exist when the House voted. Moody's stripped the United States of its last perfect credit rating on May 16, citing the bill's fiscal trajectory as a primary driver. The CBO projects the legislation will add $3.4 trillion to the deficit over a decade, on top of $36 trillion in existing national debt.

Higher Treasury yields following the downgrade mean higher borrowing costs across the economy — mortgages, car loans, business investment. Several Republican senators who had privately accepted the bill's deficit math are now recalculating. The downgrade gave the opposition's fiscal argument an external institutional endorsement that is difficult to wave away.

## The Timeline

Trump has set a July 4 signing deadline. Senate Democrats cannot block the bill under reconciliation rules, but they can extract political cost: they plan to force a full read-aloud of the bill on the Senate floor (estimated at 16 hours) and use the vote-a-rama — the open amendment process before the final vote — to put every Republican on the record on Medicaid cuts, SNAP reductions, and the Anti-Weaponization Fund.

The Senate returns the week of June 1. The bill that reaches a vote will look different from what the House passed — the parliamentarian has already struck provisions including White House security funding and voting reform measures. That matters: if the Senate version diverges significantly, the amended bill must return to the House for a second vote. Representative Marjorie Taylor Greene has already expressed regret for her House vote and indicated she may not support a materially different version.

For Indian immigrants tracking this bill, the uncomfortable reality is that their professional futures may be decided as a side effect of a fight about Medicaid in North Carolina and fiscal purity in Kentucky. The provisions that matter most to them — the fee, the levy, the enforcement expansion — are not what is keeping Tillis, Paul, and Collins awake at night."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
