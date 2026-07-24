#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
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
        "headline": "The Clock Is Coming to the Student Visa. A Four-Year Cap Just Cleared Its Last Hurdle",
        "subheadline": "A rule ending the decades-old 'duration of status' for F-1 students has finished White House review and could publish any day. Indian students, the largest cohort, stand to lose the most flexibility.",
        "slug": make_slug("dhs-duration-of-status-four-year-cap-f1-students-omb-cleared-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are the single largest group of international students in the US, and many are in multi-year PhD and research programs that a four-year admission cap would force into repeated USCIS extension filings.",
        "tags": ["f1", "students", "opt", "duration-of-status", "uscis", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg Law — White House Reviewing Rule to Limit Foreign Students' Status", "url": "https://news.bloomberglaw.com/daily-labor-report/white-house-reviewing-rule-to-limit-foreign-students-status"},
            {"name": "University of Wisconsin ISS — Summary of the Proposed Duration of Status Rule Change", "url": "https://iss.wisc.edu/"},
            {"name": "DHS — Proposed Rule on Fixed Admission Period for F, J and I Nonimmigrants", "url": "https://www.dhs.gov/"},
            {"name": "ICEF Monitor — US to end Duration of Status for F, J, and I visas", "url": "https://monitor.icef.com/"}
        ]),
        "score_total": 85,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/29229903/pexels-photo-29229903.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
        "image_caption": "International graduates in academic gowns celebrating outside a university building",
        "image_attribution": "Pexels",
        "body": """For more than thirty years, an Indian student arriving on an F-1 visa got a small mercy printed on their I-94: the words "duration of status," or D/S, instead of a hard expiry date. It meant you could stay as long as you remained a bona fide student in good standing — finish the PhD, switch from a master's to a doctorate, ride out a slow Optional Practical Training (OPT) approval — without filing a single extension with the federal government. That mercy is now on the verge of ending.

The Department of Homeland Security's rule replacing D/S with a fixed admission period — capped at four years for most students — has cleared its final bureaucratic checkpoint. The Office of Information and Regulatory Affairs inside the White House's Office of Management and Budget concluded its review on June 17, the last step before a final rule can be published in the Federal Register. Once it appears, it takes effect 60 days later. The administration has made no secret of wanting it in place for students arriving this fall.

## What actually changes

Under the proposal, the open-ended "admit until" notation disappears. In its place: an end date matching the program length, or four years, whichever is shorter. Students from countries with visa overstay rates above 10% could be held to a two-year limit. Anyone needing more time — to finish a degree, change majors, or move from study into OPT — would have to file an extension with USCIS and wait for it to be adjudicated.

That last clause is where the diaspora math turns ugly. USCIS is sitting on a backlog that, by mid-2025 figures, was running roughly 48% higher than at the end of the previous administration, with processing times up across nearly every category. Folding hundreds of thousands of student extension requests into that pipeline does not obviously end well for the people waiting in it.

## Why Indians feel this first

Indian nationals are the largest single group of international students in the United States, and crucially they are over-represented in exactly the programs the cap squeezes hardest: research-heavy PhDs and doctoral tracks in computer science, AI, and engineering that routinely run five, six, or seven years. A four-year clock means a built-in mid-degree appointment with USCIS — and the risk that a pending extension, an unrenewed I-20, or an administrative delay leaves a student technically out of status through no fault of their own.

The knock-on effect lands on work authorization. Immigration practitioners warn the rule would strip away the flexibility universities currently use to manage OPT and Curricular Practical Training (CPT) in-house. Today a designated school official can sign off on much of it. Under a fixed-period regime, more of that flow gets routed through formal USCIS filings — slower, costlier, and exposed to the same backlog.

## The financial stakes

OPT is not a nicety for Indian families; it is the return-on-investment engine of the entire decision to study abroad. An Indian student typically spends $60,000 to $100,000 on a US STEM degree, and the up-to-three-years of post-study work that STEM OPT allows is how that loan gets repaid and a career gets started. Anything that makes OPT harder to reach — or makes a student's underlying status more fragile while they pursue it — directly attacks the economic case for coming at all. NAFSA has estimated international students, led by Indians, contribute roughly $33 billion to the US economy.

## What to do now

The rule is not yet law. It still has to be published, and litigation is near-certain — a version floated in the first Trump administration drew fierce opposition from universities and hospitals and never took effect. But the smart move for Indian students already in the pipeline is to treat publication as imminent:

- **Know your program end date cold.** If your degree runs past four years, assume you will need a USCIS extension and start documenting academic progress now.
- **Don't sit on OPT.** File early and keep your school's international office in the loop on any status change.
- **Avoid mid-stream major or level changes** if you can help it — the proposed rule adds friction there specifically.

For a generation of Indian families, the American degree has been a calculated bet with a clear payoff window. Putting a hard clock on the visa doesn't kill the bet. It just shortens the odds — and adds a federal filing fee to the wager."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's IT Giants Just Took a 40% H-1B Haircut. The Bill Is Landing on Subcontractors",
        "subheadline": "H-1B approvals for India's six largest IT firms fell to 11,041 this year, down 40%. TCS was hit hardest; Infosys was the lone gainer. The fix — offshore work and pricey local subcontractors — is quietly reshaping who actually goes to America.",
        "slug": make_slug("indian-it-firms-h1b-approvals-down-40-percent-tcs-subcontractor-costs"),
        "category": "immigration",
        "vertical": "economy",
        "diaspora_angle": "The H-1B was the on-ramp that let hundreds of thousands of Indian engineers move from Bengaluru and Hyderabad to American clients; its sharp contraction at the big outsourcers narrows that on-ramp for the next cohort of entry-level Indian tech workers.",
        "tags": ["h1b", "tcs", "infosys", "indian-it", "offshore", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Mint — Top IT firms' H-1B visas slump 40%, TCS worst hit while Infosys gains", "url": "https://www.livemint.com/companies/news/top-it-firms-h-1b-visas-slump-40-tcs-worst-hit-while-infosys-gains"},
            {"name": "People Matters — TCS, Wipro, Tech Mahindra hit hard as H-1B approvals fall sharply in FY26", "url": "https://www.peoplematters.in/"},
            {"name": "The Hindu BusinessLine — Indian IT majors see rise in subcontractor costs in Q3 FY26 amid H1B disruptions", "url": "https://www.thehindubusinessline.com/"},
            {"name": "Nearshore Americas — India's IT Giants Scale Back H-1B Visa Dependence", "url": "https://nearshoreamericas.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6804068/pexels-photo-6804068.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
        "image_caption": "A team of software developers working together at computers in a modern tech office",
        "image_attribution": "Pexels",
        "body": """The headline number is blunt: India's six largest IT services firms — Tata Consultancy Services, Cognizant, Infosys, HCLTech, Wipro and Tech Mahindra — were granted 11,041 H-1B visas as of March 31, 2026. A year earlier the same group collectively received about 18,469. That is a 40% drop in a single cycle, and it is the clearest signal yet that the H-1B-powered "offshore-onsite" model that built modern Indian IT is being dismantled in real time.

The pain was not evenly shared. TCS, the bellwether, saw the steepest fall — down roughly 3,242 approvals to about 2,885. Wipro and Tech Mahindra also contracted sharply. Infosys was the lone exception in the cohort, edging up to 3,195 approvals, the highest of the group. For a sector that employs some 1.9 million people, this is not a rounding error; it is a structural pivot.

## What's driving the cut

Two policy forces are squeezing simultaneously. The first is cost: the Trump administration's attempt to slap a $100,000 fee on new H-1B petitions — struck down this month by a Boston federal judge as an unlawful tax, but now headed for appeal — made every onshore deployment a high-stakes gamble. As one analyst put it, applying for 5,000 H-1Bs at $100,000 each would mean a half-billion-dollar fee alone. Even with the fee in legal limbo, the threat alone changed corporate behavior.

The second is the quieter, more durable change: wage-weighted selection. USCIS has been steering the lottery toward higher-paid petitions, which prices out the entry-level, lower-wage roles that historically formed the bulk of Indian IT's H-1B intake. USCIS itself framed this as a feature, declaring in a May post that "the days of abusing the program with mass, low-wage registrations are over."

## The cost didn't disappear — it moved

Here is the part that gets lost in the visa-count drama: the work still has to get done for American clients, and doing it has gotten more expensive. With fewer of their own people able to fly over, the big firms are leaning on locally hired subcontractors in the US — and those bills are surging.

In the December 2025 quarter, three of India's top five IT firms posted more than 20% year-on-year jumps in subcontracting expenses. TCS led with a 26.6% rise to ₹3,560 crore; Infosys was up 23.9% to ₹4,092 crore; HCLTech up 23.3% to ₹4,775 crore. Analysts describe subcontracting as having shifted from a convenience to "an operational necessity" — a margin-eroding workaround for the simple fact that it is now harder and costlier to put an Indian engineer in front of an American client.

## What it means for the diaspora

For individual Indian engineers, the implications cut two ways.

For those already established in the US, the big-firm pullback matters less — most Indian IT workers on these visas represent a shrinking 3-5% of active workforces, and US tech giants like Amazon, Microsoft, Meta, Apple and Google have kept their own Indian-talent H-1B pipelines flowing. The squeeze is concentrated at the outsourcers, not at the product companies.

For the next cohort, though, the on-ramp is narrowing. The classic path — join TCS or Infosys in India, get deployed to a US client on an H-1B in your mid-20s — is becoming a far longer shot. More of that work is staying offshore in India, or going to subcontractors already in America, many of them earlier-generation immigrants who have aged out of the entry-level pool.

## The bigger picture

Indian IT has weathered visa shocks before, and the sector is genuinely adaptable — diversified delivery, nearshore centers in Mexico and Canada, AI-driven automation that reduces the headcount needed onsite at all. The firms will be fine. The open question is whether the individual ambition that powered this industry — a young engineer in Pune banking on a US posting as the first rung of a global career — survives the same way. The data suggests that rung is being quietly sawed off, and replaced with a more expensive, more local substitute that doesn't have an Indian passport attached."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "America Now Rejects 61% of Indian Student Visas. Families Are Doing the Math and Walking",
        "subheadline": "F-1 refusals for Indians have nearly doubled since 2023, even as the UK and Germany keep approving. With OPT under threat and a four-year cap looming, the world's biggest student-export market is starting to look elsewhere.",
        "slug": make_slug("us-f1-visa-rejection-61-percent-indian-students-uk-germany-pivot"),
        "category": "immigration",
        "vertical": "diaspora-education",
        "diaspora_angle": "Indian families weighing a six-figure US education are now factoring in a 61% refusal rate, months-long administrative processing for STEM applicants, and shrinking post-study work — and increasingly redirecting their children to countries that still say yes.",
        "tags": ["f1", "students", "opt", "study-abroad", "visa-rejection", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Collegedunia — Indian Student Visa Approval Rates 2026: US Rejections Hit 61%", "url": "https://collegedunia.com/news"},
            {"name": "ICEF Monitor — US student visa issuances fell 36% in summer 2025; OPT uncertainty a factor", "url": "https://monitor.icef.com/"},
            {"name": "Collegedunia — US F-1 Visa Administrative Processing Surge: India Cities Most Affected", "url": "https://collegedunia.com/news"},
            {"name": "Leap Scholar — F1 Visa Slots for Fall 2026-2027: Dates, Process & Tips", "url": "https://leapscholar.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/3885598/pexels-photo-3885598.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
        "image_caption": "A student waiting in an airport terminal holding a passport",
        "image_attribution": "Pexels",
        "body": """The American degree has been the gold standard of Indian middle-class aspiration for a generation. The numbers now suggest a quieter reckoning: more than six in ten Indian students who apply for a US F-1 visa are being turned away.

The US rejection rate for Indian student-visa applicants has climbed from 36% in 2023 to 61% in 2025 — the highest in over a decade. That is not a blip. It is the cumulative weight of a year of disruption: a suspension of visa interviews in May 2025, mass revocations of student statuses that triggered more than 100 lawsuits, and a proposed four-year cap on student visas that finished White House review on June 17 and could publish at any time.

## The squeeze isn't just rejections

Even students who get an interview face a gauntlet. State Department wait-time data shows Mumbai and Hyderabad — the two busiest consulates for STEM applicants — running 2.5-month queues just to reach the interview window. From there, applicants in sensitive technology fields can land in administrative processing (AP) for four to six months or longer, thanks to new social-media and academic-background vetting protocols. Immigration lawyers call the AP surge "the new norm," not a temporary spike.

The math for a Fall 2026 applicant is brutal. A Mumbai-based computer science student booking today could face a mid-summer interview followed by a months-long AP hold, pushing a decision into October or November — well past an August program start. F-1 issuances to Indian students already fell roughly 69-78% in the peak months of 2025, meaning pent-up demand is hitting the 2026 season even harder.

## The OPT question hanging over everything

Behind the visa friction sits a deeper fear: that the financial logic of a US degree is eroding. Optional Practical Training — the up-to-three-years of post-study work that lets STEM graduates repay $60,000-$100,000 in education costs — is under active reform pressure, with at least one bill seeking to eliminate it entirely. As the Times of India put it bluntly, "Without OPT, US universities become overpriced diplomas without job prospects."

For Indian families running the numbers, that is the whole ballgame. The willingness to spend a fortune on a US education was always a bet on the runway that follows it. Shorten or remove the runway, and the bet stops making sense.

## Where the students are going instead

The diversion is already visible in the comparative approval data:

- **Germany** approves roughly 90% of Indian student applicants — and charges a fraction of US tuition.
- **The UK** still clears about 94% of Indian applicants, though it has trimmed its post-study Graduate Route from two years to 18 months for students graduating from January 2027 and raised its student-visa fee.
- **Canada** has tightened sharply — capping 2026 study permits at 408,000, down 16% — and Indian rejection rates there have spiked, removing what was once the obvious fallback.

The picture that emerges is not a wholesale abandonment of the West, but a careful rerouting. The US still has the marquee universities and the deepest job market. But for the median Indian applicant — strong but not exceptional, funding the degree with family savings and loans — the combination of a 61% refusal rate, multi-month processing, and a shrinking work runway is tipping the decision toward countries that still roll out the welcome mat.

## What applicants should do

For those still set on the US, the consular timeline leaves no room for drift:

- **Finish the DS-160 and pay the MRV fee immediately** — you cannot book an appointment until the fee clears.
- **Consider New Delhi**, which has consistently shown shorter waits than Mumbai or Hyderabad.
- **Build a 90-day buffer** before your program start, and remember that since January 2026 you get only one free reschedule.

The American dream is not closed to Indian students. But it has, for the first time in a generation, become a coin-flip with a six-figure ante — and a growing number of families are deciding the odds are better elsewhere."""
    }
]

ok = 0
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        ok += 1
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
print(f"\n{ok}/{len(articles)} inserted")
