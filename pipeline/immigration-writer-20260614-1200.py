#!/usr/bin/env python3
"""Immigration writer — 2026-06-14 12:00 UTC run"""
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
        "headline": "Seventy Billion Dollars, Zero Guardrails — What the Secure America Act Means for Legal Indian Immigrants",
        "subheadline": "Trump signed the largest single immigration enforcement package in American history on June 10. The three-year funding spree shields ICE and CBP from congressional oversight — and it has every Indian on a work visa asking the same question.",
        "slug": make_slug("secure-america-act-70-billion-ice-cbp-indian-immigrants"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian immigrants on H-1B, H-4, and green card tracks face intensified enforcement operations, neighbourhood checks for citizenship applicants, and a chilling effect on community participation as ICE receives $38.5 billion with minimal oversight.",
        "tags": ["ice", "cbp", "secure-america-act", "immigration-enforcement", "dhs", "h1b"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Ballotpedia", "url": "https://news.ballotpedia.org/2026/06/12/trump-signs-the-secure-america-act-into-law/"},
            {"name": "New York Post", "url": "https://nypost.com/2026/06/09/us-news/congress-passes-70b-for-immigration-enforcement-ending-months-long-fight/"},
            {"name": "National Catholic Reporter", "url": "https://www.ncronline.org/news/70b-immigration-enforcement-funds-exclude-bishops-supported-migrant-protections"},
            {"name": "The White House", "url": "https://www.whitehouse.gov/articles/the-secure-america-act-ends-democrat-obstruction/"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/34151775/pexels-photo-34151775.jpeg",
        "image_caption": "The United States Capitol building in Washington, D.C., where the Secure America Act passed 214-212",
        "image_attribution": "Pexels",
        "body": """President Donald Trump signed the Secure America Act into law on June 10, delivering $70 billion in funding to Immigration and Customs Enforcement and Customs and Border Protection through the end of his second term. The legislation passed the House in a razor-thin 214-212 party-line vote and sailed through the Senate at 52-47 the previous week, capping a months-long standoff that included a historic 76-day partial shutdown of the Department of Homeland Security.

The numbers are worth pausing over. ICE alone receives $38.5 billion. CBP gets $22.6 billion. Another $3.5 billion goes to border security technology, and $5 billion in additional appropriations flows to DHS. The funding runs through September 30, 2029 — meaning no future Congress can easily claw it back while Trump remains in office.

## The Enforcement Machine Gets Bigger

Border Czar Tom Homan was blunt about what the money buys. "You're going to see targeting increase, you're going to see arrests increase," he said before the signing. "With additional funding, we're going to keep our foot on the gas."

The legislation was passed through budget reconciliation — a procedural mechanism that bypasses the usual appropriations process and its attendant oversight hearings, spending guidelines, and annual reviews. House Minority Leader Hakeem Jeffries called it "a blank check to ICE without any guardrails, any oversight or any accountability."

Kevin Appleby, a senior fellow at the Center for Migration Studies and former director of migration policy for the U.S. Conference of Catholic Bishops, warned that "DHS now has an almost unlimited amount of funding to build a mass deportation infrastructure with no guardrails or accountability."

## Why Indian Americans Should Be Paying Attention

The Secure America Act is ostensibly about border security and undocumented immigration. But its consequences radiate well beyond those categories.

The Trump administration has already resurrected "neighbourhood checks" for citizenship applicants — a practice last used during the first Bush administration — in which federal agents visit applicants' homes and interview neighbours as part of the naturalization process. With $38.5 billion in fresh ICE funding, the capacity to scale such programmes is no longer theoretical.

For the estimated 400,000 Indians waiting in employment-based green card queues, the chilling effect is real. Many live in mixed-status households or communities where a single ICE operation can disrupt families with entirely legal immigration status. The fear is not deportation — it is the ambient dread of a vastly expanded enforcement apparatus operating with broad discretion and limited judicial oversight.

H-1B holders are particularly exposed. The 60-day grace period after a job loss already forces workers into a desperate scramble. An enforcement regime flush with cash and political mandate makes every status transition — every gap between an I-797 receipt and an approval notice — feel more precarious.

## The Political Arithmetic

The 76-day DHS shutdown that preceded the bill was itself a symptom of how polarised immigration politics have become. Senate Democrats blocked funding for months after ICE operations in Minneapolis resulted in the fatal shootings of two American citizens. The compromise that ended the broader shutdown restored funding for the Coast Guard, FEMA, TSA, and the Secret Service — but deliberately excluded ICE and CBP, forcing Republicans to use reconciliation to fund them.

A controversial $1.776 billion settlement fund for political allies who claim political persecution was stripped from the bill after bipartisan backlash, but the core enforcement spending remained untouched.

## What Comes Next

The Secure America Act is not a policy bill. It creates no new categories of enforcement, establishes no new visa programmes, and reforms nothing. It simply writes the largest cheque in American history for agencies whose mandate is to find, detain, and remove people.

For Indian Americans navigating the legal immigration system — already stretched thin by decades of backlogs, fee hikes, and regulatory whiplash — the question is not whether this funding will be used. It is how, and against whom, and with what recourse.

The answer, for now, is that nobody has to tell you. That is what "zero guardrails" means."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The PROTECT Act Would Make the $100,000 H-1B Salary Floor Permanent Law",
        "subheadline": "A Utah congressman wants Congress to codify what a federal judge just struck down — and for Indian tech workers, the legislation is arguably worse than the executive order it replaces.",
        "slug": make_slug("protect-act-kennedy-100k-h1b-salary-floor-congress"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals receive the majority of H-1B visas each year. A $100,000 salary floor codified in statute would be far harder to challenge than an executive order, threatening IT outsourcing firms and entry-level Indian tech professionals.",
        "tags": ["h1b", "protect-act", "salary-floor", "congress", "mike-kennedy", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "IndiaWest", "url": "https://indiawest.com/h-1b-reform-battle-moves-to-congress-following-court-ruling/"},
            {"name": "Daily Caller", "url": "https://dailycaller.com/2026/06/11/rep-mike-kennedy-plan-bypass-obama-judges-ruling-protect-american-workers/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/us/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-09/"},
            {"name": "Inc.", "url": "https://www.inc.com/kit-eaton/trumps-100000-h-1b-visa-fee-was-just-struck-down-why-many-employers-still-have-a-bigger-problem/91122918"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/49/Kennedy_Mike_119th_Congress_2.jpg",
        "image_caption": "Rep. Mike Kennedy (R-UT), sponsor of the PROTECT Act to codify a $100,000 H-1B salary floor",
        "image_attribution": "Wikimedia Commons",
        "body": """The ink on Judge Leo Sorokin's ruling was barely dry when Rep. Mike Kennedy started making calls. On June 9, the Obama-appointed federal judge in Boston struck down President Trump's $100,000 fee on H-1B visa applications, calling it an unconstitutional tax that Congress never authorised. The next day, the Utah Republican went public with his countermove: the PROTECT Act, a bill that would take the same $100,000 figure and carve it into statute where no judge can touch it.

"An activist judge stepped in to strike down the President's critical H-1B immigration reforms," Kennedy said. "The judge claims only Congress can do this? Fine. I already introduced the PROTECT Act, which will codify the President's H-1B reforms and make it the law of the land."

## What the Bill Actually Does

The Prioritising Resources for Our Citizens and Talent Act — PROTECT, for those who enjoy legislative acronyms — does more than simply replicate Trump's executive order. It reshapes the H-1B programme in three significant ways.

First, it establishes a $100,000 annual salary floor for all H-1B workers, adjusted for inflation, or the prevailing wage for a comparable American worker — whichever is higher. This is not a one-time application fee, as Trump's proclamation imposed. It is a minimum salary requirement, which means employers cannot sponsor an H-1B worker for any position paying less than six figures.

Second, the bill would prioritise visa petitions offering higher salaries. Under current rules, the H-1B lottery is essentially random — a software engineer at Google earning $250,000 has the same chance as a junior analyst at a consulting firm making $65,000. Kennedy's legislation would tilt the system toward higher-paid workers, effectively pricing out entry-level positions.

Third, the PROTECT Act tightens restrictions on workers placed at third-party client sites — the staffing model that defines much of India's IT outsourcing industry. Companies like TCS, Infosys, and Wipro, which place thousands of Indian workers at client locations across the United States, would face significantly higher compliance burdens.

## The Healthcare Carve-Out Tells You Everything

Kennedy's bill includes exemptions for physicians, registered nurses, pharmacists, therapists, and other direct patient-care workers — provided employers can demonstrate they tried and failed to recruit qualified Americans first.

The exemption is revealing. It acknowledges that certain industries genuinely cannot function without foreign workers, and that a blanket $100,000 floor would cripple rural hospitals and underserved clinics that rely on international medical graduates. But it also underscores who the bill is really aimed at: the technology sector, where Indian nationals dominate H-1B approvals.

## Why This Matters More Than the Executive Order

When Trump imposed the $100,000 fee by proclamation last September, immigration lawyers immediately identified it as vulnerable to legal challenge. The Constitution is unambiguous about who can levy taxes, and a president unilaterally demanding six-figure payments stretched the definition of "entry restriction" past its breaking point.

The PROTECT Act eliminates that vulnerability. If Congress passes a law requiring $100,000 salaries for H-1B workers, courts will have far less room to intervene. A statute carries a presumption of constitutionality that an executive proclamation does not.

For Indian tech professionals, this distinction matters enormously. Trump's executive order was always temporary — set to expire in September 2026 and subject to the next administration's priorities. A congressional statute would be permanent, surviving changes in the White House and requiring a future Congress to muster the votes to repeal it.

## The Numbers That Should Worry You

H-1B registrations have already dropped 27 per cent this year, from 470,342 to 343,981, largely because of uncertainty around the $100,000 fee. Only about 85 employers actually paid the fee before the court struck it down, collecting $8.5 million for the government.

But a $100,000 salary floor would cut deeper than a one-time fee. According to USCIS data, a significant proportion of H-1B positions — particularly at Level 1 and Level 2 wage classifications — pay between $60,000 and $95,000. These are the roles most commonly filled by recent Indian graduates, early-career professionals, and workers at IT consulting firms.

Kennedy acknowledged the bill is a starting point, not a ceiling. "I think $100,000 is a good baseline," he told the Daily Caller News Foundation, "but I'm open to increasing the amount over time."

## The Road Ahead

The PROTECT Act faces the usual gauntlet of committee hearings, floor votes, and Senate negotiations. Kennedy's bill has no Democratic co-sponsors, and the tech industry lobby — which fought the executive order aggressively — will oppose codification with equal force.

But the political tailwinds are strong. The H-1B programme has become a bipartisan punching bag, with Republicans framing it as a threat to American workers and some Democrats uncomfortable defending a system that primarily benefits large corporations. Kennedy's framing — "the judge said Congress has to do this, so let's do it" — is politically potent.

For the hundreds of thousands of Indian professionals whose American lives depend on the H-1B programme, the message is clear: the $100,000 question is not going away. It is just moving to a courtroom where the odds are worse."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Every Employer in America Would Have to Run Your Name Through E-Verify Under a New Senate Bill",
        "subheadline": "The Mandatory E-Verify Act of 2026, backed by ten Republican senators, would create a national employment verification mandate — and its 2% error rate for legal immigrants is a feature its sponsors refuse to discuss.",
        "slug": make_slug("mandatory-e-verify-act-2026-indian-immigrants-error-rate"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "E-Verify's error rate for legal immigrants and green card holders is ten times higher than for US-born citizens. Indian H-1B workers, OPT holders, and recent green card recipients with transliterated names or pending status changes are disproportionately at risk of false flags that delay or block employment.",
        "tags": ["e-verify", "employment-verification", "senate", "katie-britt", "h1b", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Sen. Katie Britt", "url": "https://www.britt.senate.gov/updates/u-s-senator-katie-britt-leads-mandatory-e-verify-legislation/"},
            {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/opinion/3453041/deportation-hits-illegal-immigration-supply-mandatory-e-verify-will-address-demand/"},
            {"name": "Cato Institute", "url": "https://www.cato.org/blog/e-verify-has-delayed-or-cost-half-million-jobs-legal-workers"},
            {"name": "Sen. Tuberville", "url": "https://www.tuberville.senate.gov/newsroom/press-releases/tuberville-britt-introduce-mandatory-e-verify-legislation-to-crack-down-on-illegal-immigration/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7841420/pexels-photo-7841420.jpeg",
        "image_caption": "An employment agreement on a desk — under the proposed E-Verify mandate, every hire would require federal verification",
        "image_attribution": "Pexels",
        "body": """Senator Katie Britt of Alabama wants to solve a problem that has vexed every administration for decades: how to stop employers from hiring people who are not authorised to work in the United States. Her answer is the Mandatory E-Verify Act of 2026, introduced with nine Republican co-sponsors, which would require every employer in America to run every new hire through the federal government's electronic employment verification system.

E-Verify, for those who have never encountered it, is a web-based system that checks information from an employee's I-9 form against records held by the Social Security Administration and the Department of Homeland Security. About 1,080 employers currently use it voluntarily, and several states already mandate it. Britt's bill would make it the law of the land.

"If you come to this country illegally, you shouldn't be here to begin with, and you shouldn't be working in the United States," Britt said in introducing the legislation.

## The Problem With the Pitch

The bill's sponsors frame E-Verify as a simple, proven tool. The reality, documented across two decades of government audits and independent research, is considerably messier — especially for people who were born outside the United States.

The Cato Institute, hardly a pro-immigration outfit, has tracked E-Verify's error rates since the system's inception. The numbers are stubborn. The tentative non-confirmation rate — the rate at which the system flags a worker as potentially unauthorised — runs at about 0.2 per cent for US-born citizens. For legal immigrants, including green card holders and visa workers, the rate jumps to 2 per cent. That is a tenfold disparity.

Scale those percentages to a national mandate covering 150 million American workers, and the arithmetic gets uncomfortable. A 2 per cent error rate applied to the roughly 25 million legal immigrants in the US workforce produces 500,000 erroneous flags. Each flag triggers a process: the worker must formally contest the error, visit a Social Security Administration office or a DHS field office, and resolve a discrepancy they did not create, often without knowing what the discrepancy is.

## Where Indian Workers Get Caught

The reasons E-Verify trips on legal immigrants are structural, not random. Name transliteration is a persistent issue. An Indian worker whose name appears as "Raghunath" on their passport but "Raghunathan" in the SSA database — or whose surname and given name are transposed, a common occurrence with South Indian naming conventions — will receive a tentative non-confirmation that they must then spend days or weeks resolving.

Status transitions create another trap. An H-1B worker whose employer files an extension but whose I-797 receipt notice has not yet been entered into the DHS database will trigger a flag. An OPT holder whose STEM extension was approved but not yet reflected in SEVIS will show as potentially unauthorised. A new green card holder whose status change is still being processed by USCIS will appear in the system as a temporary worker whose authorisation has expired.

These are not edge cases. They are the routine friction points of a legal immigration system that processes millions of status changes annually with paper-era technology and chronic staffing shortages.

## What the Bill Would Actually Change

Beyond the mandate itself, the Mandatory E-Verify Act enhances civil and criminal penalties for employers who hire unauthorised workers, strengthens fraud-prevention measures within the E-Verify programme, and — critically — prohibits states from blocking employers from using E-Verify.

That last provision is aimed at states like California and Illinois, which have placed restrictions on how employers can use the system, partly to protect workers from discriminatory screening. Under Britt's bill, those protections would be pre-empted by federal law.

The legislation also extends E-Verify to contract labour. Any employer using subcontractors would be required to certify that all parties to the contract use E-Verify. Failure to include the certification would itself constitute a violation.

## The Enforcement Climate

The Mandatory E-Verify Act does not exist in a vacuum. It arrives alongside the $70 billion Secure America Act funding ICE and CBP through 2029, the PROTECT Act seeking to codify a $100,000 H-1B salary floor, and a Department of Labour proposal to raise prevailing wages by 33 per cent. Each bill individually would reshape some corner of the immigration system. Together, they describe a comprehensive effort to raise the cost — financial, administrative, and psychological — of employing foreign workers in the United States.

For Indian professionals who followed every rule, filed every form, and paid every fee, the mandatory E-Verify regime adds one more choke point to an already punishing process. It is not that the system cannot distinguish between legal and illegal workers. It is that, at scale, it reliably fails to — and the burden of correcting its failures falls entirely on the worker.

## The Votes

The bill has ten Republican co-sponsors: Britt, Tuberville, Blackburn, Budd, Capito, Cotton, Cruz, Graham, Hyde-Smith, and Lankford. No Democrats have signed on. The bill faces an uncertain path in a closely divided Senate, and the tech industry lobby, which depends on a smooth hiring pipeline for foreign workers, is expected to oppose it.

But the political logic is straightforward: if the enforcement apparatus gets $70 billion and the H-1B programme gets a $100,000 salary floor, a national E-Verify mandate becomes the logical next piece. Britt and her colleagues are betting that no politician wants to be seen opposing a tool that, in theory, protects American jobs.

Whether the tool actually works as advertised is, apparently, a secondary concern."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
