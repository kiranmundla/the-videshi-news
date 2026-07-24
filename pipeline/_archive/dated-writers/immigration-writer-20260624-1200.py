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

GOLD_BODY = """The pitch is blunt: pay $5 million, skip the queue, and call America home. President Donald Trump's "Gold Card" — the investor-residency program he has floated as a replacement for the decades-old EB-5 visa — is now being marketed in earnest to India's wealthy, and the early verdict from Mumbai and Delhi drawing rooms is more shrug than scramble.

That coolness is worth dwelling on, because Indians have historically been among the most eager buyers of American residency. They are the largest cohort waiting in the employment-based green card backlog, and demand for the existing EB-5 program — which grants a green card for an $800,000 investment that creates ten US jobs — has surged this year as families rush to file before any threshold rises. So why is the headline product getting a lukewarm reception?

## The math problem

Start with the price. At $5 million, the Gold Card is the most expensive residency-by-investment scheme in the world, several times the cost of EB-5 and orders of magnitude above rival programs. The UAE's Golden Visa, by comparison, can be secured for roughly ₹4 crore — about a fifth of the Gold Card's cost — and offers proximity to India, no income tax, and a long-term renewable residency that many affluent Indians find perfectly adequate.

For someone with a net worth north of ₹50 crore, the calculation rarely favors relocation. A ten-year B1/B2 tourist visa already permits frequent, lengthy visits to the United States for business and family. Unless the holder has genuine billion-dollar ambitions that require sitting inside the US economy, paying $5 million for the privilege of residency — and the tax exposure that can come with it — looks less like a deal and more like a vanity purchase.

## The tax wrinkle that actually matters

The one feature that has caught the attention of tax advisers is the administration's suggestion that Gold Card holders would be taxed only on US-source income, not on their worldwide income — a carve-out not available to ordinary green card holders or citizens. For a globally diversified Indian business family, that distinction is enormous. Whether it survives contact with Congress and the Internal Revenue Service is another question entirely.

And that is the deeper issue hanging over the whole program: legal authority. The EB-5 program was reauthorized by Congress in 2022 through the Reform and Integrity Act, with protections for existing investors and a statutory life running to 2027. A president cannot unilaterally abolish a congressionally created visa category or invent a new one with a $5 million price tag; immigration law lives under Article I. Lawyers tracking the proposal expect any serious version of the Gold Card to require legislation — which means the "available in two weeks" promise first made in early 2025 remains, more than a year later, unfulfilled.

## Why this matters to the diaspora

For the vast majority of the Indian diaspora — H-1B engineers, EB-2 and EB-3 applicants stuck in a queue measured in decades, students gambling on the H-1B lottery — the Gold Card is a reminder of a widening two-tier system. The traditional, merit-based pathways that built the Indian-American professional class are getting slower, costlier, and more uncertain, while a parallel cash lane is being paved for those who can write an eight-figure check.

There is a strategic read here too. The very existence of the Gold Card conversation is nudging Indian families who *can* afford EB-5 to file now, before the existing $800,000 route is closed or repriced. Immigration consultants in India report a spike in inquiries, and collateral-free US-sourced loans of up to $300,000 are being marketed to applicants who are short of the full amount. The window, they warn, may not stay open.

For everyone else, the lesson is colder: in 2026, the surest way into America is increasingly the most expensive one. The Gold Card may flop with India's billionaires who already have what they need. But its arrival signals where the system is drifting — toward a model where permanent residency is less a reward for skill than a line item for the wealthy.

**Sources:** The Indian Eye, Reuters, AILA, Lippes Mathias LLP."""

COURT_BODY = """In a single Tuesday, June 23, America's courts pulled the immigration system in two opposite directions — and both rulings land on the desks of people who thought the rule of law was simpler than this.

In Washington, the US Court of Appeals for the DC Circuit handed the Trump administration a major win, reviving its plan to apply "expedited removal" nationwide. The 2-1 decision lets immigration authorities fast-track the deportation of people found anywhere in the country who cannot prove they have lived in the United States continuously for at least two years — no hearing before an immigration judge required. For nearly three decades the tool was confined to recent arrivals caught near the border. Now, in the majority's words, the Department of Homeland Security may apply it "to the maximum extent allowed by law."

Hours earlier and a continent away, a federal judge in California pushed the other way. US District Judge P. Casey Pitts vacated the administration's policy of arresting noncitizens at immigration courthouses, finding it "arbitrary and capricious" and warning that turning courthouses into "hunting grounds" would have a chilling effect on the entire system. His 71-page order also capped how long noncitizens can be held in short-term cells.

## Why a high-skilled diaspora should read the fine print

It is tempting for an H-1B engineer or an EB-2 green card applicant to file both rulings under "not my problem." That would be a mistake.

The expedited-removal expansion is built around a burden of proof — and the burden falls on the individual, on the spot. The exemptions are real: anyone who can show two years of continuous presence, asylum seekers who pass a credible-fear screening, and lawful status holders are not the targets. But the operative word is *show*. The policy puts the onus on the person stopped to produce evidence quickly, in a high-pressure encounter, before a frontline officer rather than a judge.

For the diaspora, the gray zones are where the risk lives. A worker between a lapsed status and a pending extension. A student whose SEVIS record was terminated in error during this year's wave of cancellations. A spouse whose H-4 paperwork is caught in processing. A green card holder traveling without documents. None of these people are the intended quarry, but a system that compresses decisions into hours and shifts the burden onto the noncitizen leaves less room for the benefit of the doubt.

## The practical takeaway

Immigration attorneys have a consistent message after these rulings: carry proof of status, and keep it current. That means physical or readily accessible evidence — a valid I-94, an EAD card, an approval notice, a green card — on your person, not in a drawer at home. It means keeping copies of documents that establish more than two years of US presence: leases, pay stubs, tax filings, utility bills. And it means resolving any status ambiguity with counsel rather than hoping it goes unnoticed.

The courthouse ruling, by contrast, is a reminder that the judiciary remains a genuine check. The administration has lost as often as it has won this year — the $100,000 H-1B fee was struck down, mass student-visa cancellations were largely reversed, and now courthouse arrests have been blocked. DHS has signaled it will appeal both the expedited-removal limits it dislikes and defend the wins it secured, so neither ruling is the last word. The expedited-removal expansion in particular may yet reach the Supreme Court.

## What's next

For the Indian diaspora, the larger pattern matters more than any single decision. The enforcement architecture is being rebuilt to move faster and demand more of the individual, while the courts intermittently slow it down. Living lawfully is necessary but, increasingly, not sufficient — being able to *prove* it on short notice is becoming part of the job of being an immigrant in America.

The advice that once applied mainly to the undocumented now extends, quietly, to the documented: know your status, carry your evidence, and do not assume that a clean record speaks for itself.

**Sources:** CNN, Reuters, Washington Examiner, Bloomberg Law, USA Today."""

CPT_BODY = """For two decades, the Indian student in America has had an unwritten insurance policy. Lose the H-1B lottery? Enroll in another program, switch to "Day 1 CPT," and keep working legally while you try again next year. Run out of options after graduation? You had 60 days of grace to find a fix. A pair of proposed federal rules now threatens to cancel both safety nets at once — and Indians, who make up the single largest slice of the affected population, stand to lose the most.

The mechanism is a Department of Homeland Security proposal, advanced in May and now cleared through White House review, that would scrap the long-standing "Duration of Status" framework for F-1 student visas. Today, international students may remain in the US as long as they maintain their student status. Under the new rule, they would instead be admitted for a fixed period — up to four years — with any extension, including continued study or post-graduation work authorization, requiring a formal application to USCIS.

## Two quiet changes with loud consequences

The headline is the four-year cap. But buried in the details are two changes that hit the Indian diaspora's improvisational playbook directly.

The first is the likely end of "Day 1 CPT" as a fallback. Curricular Practical Training lets students work as part of their coursework, and a cottage industry of programs has marketed "Day 1 CPT" — work authorization from the first day of enrollment — as a bridge for graduates who strike out in the H-1B lottery. As Danielle Goldman, co-founder of the immigration platform Build, put it, someone who already holds a master's degree "is not going to be able to go back and say, 'I need another master's degree because I need work authorization to continue working.'" Under a rigid, USCIS-approved extension regime, that maneuver becomes far harder to justify.

The second is a proposed reduction of the post-completion grace period from 60 days to 30. That single month matters enormously. The 60-day window is what gives a graduate time to find an employer, file a change of status, or arrange an orderly departure. Halving it turns a manageable transition into a scramble — and raises the odds of an inadvertent status violation that, under the expedited-enforcement climate now taking shape, carries real consequences.

## Why Indians are disproportionately exposed

Indian nationals are the largest or near-largest group of international students in the US and account for an outsized share of H-1B lottery registrations. They are also concentrated in exactly the fields — artificial intelligence, machine learning, software engineering, data science — where the lottery is most oversubscribed and where repeated rejections are common. The Day 1 CPT bridge and the H-1B lottery's multiple bites at the apple are precisely the tools this cohort has relied on to stay in the country between graduation and a cap-subject work visa.

Remove the flexibility, and the calculus for an Indian student changes before they even board the plane. Goldman warns the impact "is going to have a massive impact on the companies that are in desperate need of top talent," noting that foreign nationals make up a substantial share of the US AI workforce. Employers, she says, will either struggle to recruit or be forced toward narrower alternatives — cap-exempt H-1B roles at universities and nonprofits, or O-1 visas reserved for the genuinely exceptional.

## The diaspora angle

This is the supply line of the Indian-American professional class being quietly re-plumbed. The pipeline has long run: undergraduate or master's degree, OPT, a few rounds of the H-1B lottery cushioned by CPT, and eventually a work visa and the long green card wait. Tighten the student phase, and fewer Indians ever reach the H-1B stage at all — a shift already visible in collapsing enrollment numbers and students rerouting to Canada, Germany, and Ireland.

The rule is not yet final, and it is certain to draw litigation and a flood of public comment. But students arriving for the autumn term should plan as if their margin for error has shrunk. Maintain status meticulously, treat the grace period as 30 days rather than 60, and do not count on Day 1 CPT being there as a parachute. The era of "stay as long as you study" is ending, and with it some of the quiet flexibility that made America the default choice for a generation of Indian talent.

**Sources:** The Indian Eye, Build, US Department of Homeland Security."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "America's $5 Million Gold Card Is Here. India's Rich Are Unimpressed",
        "subheadline": "Trump's flagship investor visa is the world's priciest residency. For wealthy Indians weighing a UAE Golden Visa or a 10-year tourist visa, the math rarely adds up — and the program may not even be legal yet.",
        "slug": make_slug("trump-gold-card-5-million-wealthy-indians-skeptical-eb5-uae"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The $5M Gold Card signals a widening two-tier system where America's wealthy buy residency outright while H-1B engineers and EB-2 applicants wait decades — and it's pushing affluent Indians to file EB-5 now before the cheaper route closes.",
        "tags": ["gold-card", "eb5", "investor-visa", "green-card", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/is-gold-card-by-us-the-best-bet-for-rich-indians/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/us/trump-floats-5-million-gold-card-route-us-citizenship-2025-02-25/"},
            {"name": "AILA", "url": "https://www.aila.org/library/think-immigration-eb-5-visas-and-trumps-gold-card-idea"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32642484/pexels-photo-32642484.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A US passport with cash and credit cards, illustrating investor-based pathways to American residency",
        "image_attribution": "Pexels",
        "body": GOLD_BODY
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Two Court Rulings, One Day, Opposite Directions: What Indians Should Take From June 23",
        "subheadline": "An appeals court let the Trump administration fast-track deportations nationwide; hours later a judge blocked ICE arrests at courthouses. For visa holders, the lesson is the same: carry proof of your status.",
        "slug": make_slug("expedited-removal-courthouse-arrests-rulings-indians-carry-proof-status"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Expedited removal now shifts the burden of proof onto the individual in high-pressure encounters, so even lawful H-1B, H-4, F-1 and green card holders need documents on hand — living lawfully is no longer enough; proving it on short notice is.",
        "tags": ["expedited-removal", "ice", "deportation", "due-process", "h1b"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "CNN", "url": "https://www.cnn.com/2026/06/23/politics/expedited-removal-appeals-court"},
            {"name": "Reuters", "url": "https://www.reuters.com/legal/trump-administration-can-expand-fast-track-deportation-process-us-appeals-court-2026-06-23/"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/us-law-week/trump-fast-deportation-rule-cleared-by-appeals-court-for-now"},
            {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/06/23/federal-judge-blocks-ice-courthouse-arrests/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/15084326/pexels-photo-15084326.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Sheriff vehicles parked in front of a US county courthouse",
        "image_attribution": "Pexels",
        "body": COURT_BODY
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Student Visa Safety Nets Indians Relied On Are About to Disappear",
        "subheadline": "A DHS rule cleared by the White House would cap student stays at four years, gut the 'Day 1 CPT' fallback, and halve the post-graduation grace period from 60 days to 30. Indian students are the most exposed.",
        "slug": make_slug("dhs-duration-of-status-day1-cpt-grace-period-indian-students-f1"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are the largest cohort of US international students and H-1B lottery registrants, and they lean heavily on Day 1 CPT and the 60-day grace period as bridges between failed lottery attempts — removing both narrows the pipeline that built the Indian-American professional class.",
        "tags": ["f1", "opt", "cpt", "student-visa", "duration-of-status"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
            {"name": "US Department of Homeland Security", "url": "https://www.dhs.gov/"},
            {"name": "Tupaki", "url": "https://english.tupaki.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/29229903/pexels-photo-29229903.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "University graduates in caps and gowns celebrating at a commencement ceremony",
        "image_attribution": "Pexels",
        "body": CPT_BODY
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"… {art['slug']}  ({wc} words)")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
