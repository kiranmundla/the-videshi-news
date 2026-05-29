#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-29 16:11 UTC run"""
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
        "headline": "Your Bank Just Got a New Job — Immigration Enforcement",
        "subheadline": "A May 19 executive order directs federal regulators to treat immigration status as a financial risk factor, and Indian immigrants with perfectly legal visas are wondering what that means for their mortgages.",
        "slug": make_slug("bank-immigration-enforcement-executive-order-indian"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B holders carry mortgages, auto loans, and credit cards that depend on a banking system that has never asked about visa status. This EO changes the regulatory incentive structure — banks may begin treating non-citizen customers as elevated risk, even if they have spotless credit and years of US tax filings.",
        "tags": ["executive-order", "banking", "immigration", "financial-services", "h1b"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Mayer Brown", "url": "https://www.mayerbrown.com/en/insights/publications/2026/05/president-trump-signs-executive-order-directing-federal-financial-regulators-to-address-risks-to-us-financial-system-presented-by-customer-immigration-status"},
            {"name": "Capitalism Institute", "url": "https://capitalisminstitute.org/trump-executive-order-targets-banks-serving-illegal-immigrants/"},
            {"name": "Oltarsh & Associates", "url": "https://oltarsh.com/immigrant-bank-account-rights-what-trump-order-means/"},
            {"name": "Mexico Business News", "url": "https://mexicobusiness.news/professional-services/news/trump-order-targets-undocumented-immigrants-financial-access"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7821495/pexels-photo-7821495.jpeg",
        "body": """On May 19, President Trump signed an executive order titled "Restoring Integrity to America's Financial System." The directive tells federal financial regulators — Treasury, the CFPB, and banking agencies — to identify risks posed by extending credit and financial services to people without valid work authorization. It stops short of requiring banks to verify citizenship at the counter. But it makes immigration status a formal variable in the risk calculus of American finance, and that shift has implications far beyond the undocumented population it claims to target.

## What the Order Actually Does

The executive order instructs the Treasury Department to advise financial institutions on indicators of suspicious activity involving undocumented immigrants. It references cross-border fund transfers linked to narcotics trafficking and money laundering networks, citing a federal analysis that identified foreign passport holders using US-based accounts to facilitate over $312 billion in laundered funds for criminal organizations.

Wall Street had braced for worse. Earlier drafts reportedly required banks to collect proof of citizenship from every customer — a proposal that the financial industry called "unworkable." The final version pulled back. According to Semafor, "In a win for Wall Street, the final version instead directs Treasury Secretary Scott Bessent to advise financial institutions on ways undocumented immigrants might open accounts or receive loans." American Banker confirmed the narrower scope: agencies will issue guidance on suspicious activity indicators, not mandate citizenship checks.

But the regulatory direction is unmistakable. As one immigration attorney noted, the order "shifts the regulatory posture in a direction that should worry anyone who has relied on federal indifference to immigration status in the financial system."

## Why Indian Immigrants Should Pay Attention

The order targets undocumented immigrants. Indian H-1B holders, green card applicants, and naturalized citizens are not its intended subjects. But immigration policy has a way of splashing beyond its stated boundaries.

Consider the practical reality. An Indian engineer on an H-1B visa walks into a bank to refinance a mortgage. The banker pulls up the account. Under current norms, immigration status is irrelevant — credit score, income, employment history determine the outcome. Under the new regulatory guidance, banks will be incentivized to build immigration-status risk models. If the system flags non-citizen customers for additional review, the H-1B holder with a 780 credit score and twelve years of W-2 income could face questions that a citizen with identical financials would not.

This is not hypothetical. A 2026 study by the Urban Institute estimated that between 5,000 and 6,000 mortgages were issued to customers using Individual Taxpayer Identification Numbers — the tax filing mechanism typically used by undocumented workers. Banks already lend reluctantly to ITIN holders. Fannie Mae and Freddie Mac are similarly hesitant to insure such mortgages. The EO reinforces that hesitancy and could extend it upward into the legal immigration stack.

For the roughly 700,000 Indians currently in the US on temporary work visas, the concern is not that their accounts will be closed tomorrow. It is that the cost of being a non-citizen customer just went up — in scrutiny, in friction, in the quiet algorithmic adjustments that banks make when regulators signal a new enforcement priority.

## The Remittance Dimension

The order also has implications for remittances. Indian immigrants sent approximately $32 billion home in 2024, making India the world's largest recipient of remittance flows from the US. The OBBBA's 3.5% remittance tax — already costing Indian families an estimated $1.6 billion annually — operates in the same regulatory neighborhood. As banks tighten their compliance frameworks around cross-border transfers, remittance costs could rise further through enhanced due diligence requirements, even for fully documented senders.

## What Happens Next

The order directs agencies to issue guidance within 180 days. The specifics — what indicators banks should flag, what enhanced due diligence looks like, whether non-citizen status alone triggers additional review — remain undefined. Financial institutions are in a holding pattern, waiting for Treasury to translate presidential rhetoric into operational compliance requirements.

For Indian Americans, the practical advice is straightforward: maintain meticulous documentation of legal status, keep immigration paperwork current, and ensure that financial institutions have updated employment authorization records on file. The regulatory ground is shifting. The question is no longer whether immigration status will affect financial access, but how quickly and how broadly.

The executive order does not close bank accounts. But it opens a door that the financial industry spent decades keeping shut — and once regulators walk through it, the distinction between documented and undocumented may prove thinner than anyone in a Cupertino mortgage office would like to believe."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "211,600 — Inside the Biggest Single-Year Collapse in H-1B Applications",
        "subheadline": "FY2027 registrations fell 38.5% in one year. The $100,000 fee, a wage-weighted lottery, and a fraud crackdown have reshaped who gets to compete for an American work visa — and Indians are still 71% of the shrinking pool.",
        "slug": make_slug("h1b-fy2027-registration-collapse-38-percent-indian"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians account for 71% of all approved H-1B applications. A 38.5% registration drop doesn't just shrink the lottery pool — it changes its composition. Indian IT outsourcing firms have cut filings by 46% over five years. The Indians who remain in the pool are increasingly direct hires at US tech companies, earning higher wages. The H-1B program is becoming more elite, more expensive, and less accessible to the broad base of Indian tech talent that built it.",
        "tags": ["h1b", "fy2027", "uscis", "registration-decline", "indian-tech"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/h-1b-registrations-down-in-fy27-more-approvals-for-higher-degrees-salaries/article69606070.ece"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/new-uscis-policy-could-force-h-1bs-seeking-green-cards-to-apply-from-home-countries/article69611523.ece"},
            {"name": "TechGig", "url": "https://content.techgig.com/technology/massive-drop-in-h-1b-visa-signups-for-2026-whats-behind-the-decline/articleshow/121096419.cms"},
            {"name": "BizzBuzz News", "url": "https://www.bizzbuzz.news/economy/indian-tech-jobs-in-us-at-risk-h-1b-approvals-fall-sharply-1361988"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
        "body": """The numbers arrived quietly in a USCIS data release last week: 211,600 H-1B registrations for fiscal year 2027, down from 343,981 the previous year. A 38.5% decline. The steepest single-year drop in the program's modern history. For a visa category that has defined the Indian professional diaspora in America for three decades, the contraction signals something more fundamental than a bad year — it marks the end of the H-1B program as mass immigration pathway and its transformation into an elite credentialing system.

## Three Forces, One Outcome

The decline has three distinct causes, each reinforcing the others.

**The $100,000 fee.** In September 2025, President Trump signed a proclamation requiring a $100,000 payment for certain H-1B filings. The fee does not apply to every petition — it targets new cap-subject filings where the offered wage falls below a threshold. But the chilling effect has been enormous. As of late May 2026, approximately 70 companies have paid it. Three lawsuits challenging the fee are now before the DC Circuit. For Indian IT services firms that historically filed thousands of petitions at lower wage levels, the fee is functionally prohibitive. Several have simply stopped filing for positions that would trigger it.

**The wage-weighted lottery.** Effective February 27, 2026, USCIS replaced the random H-1B lottery with a weighted selection system. Registrations assigned to Wage Level IV — the highest-paid positions — enter the selection pool four times. Level III enters three times. Level II twice. Level I once. The math is brutal for entry-level positions: a fresh graduate hired at Level I now has one-quarter the selection probability of a senior architect at Level IV. USCIS framed this as prioritizing "higher-skilled and higher-paid" workers. The practical effect is that companies must offer higher salaries to have competitive lottery odds.

**The fraud crackdown.** USCIS has aggressively targeted duplicate registrations and shell-company filings since the 2023-2024 fraud cases. The new beneficiary-centric selection system ensures each individual is counted once regardless of how many employers file on their behalf. Registrations that once inflated the pool — multiple filings for the same worker through staffing intermediaries — have been purged.

## What the Indian Pipeline Looks Like Now

Indians still dominate the H-1B landscape. An estimated 71% of all approved applications go to Indian nationals, according to USCIS data. But the composition of that 71% is shifting dramatically.

The six largest Indian IT employers — TCS, Infosys, HCL Technologies, Wipro, Tech Mahindra, and LTIMindtree — have reduced H-1B filings by 46% over the past five years. TCS was an exception in FY2025, sponsoring 5,505 visas, but the industry trend is unmistakable. These companies have pivoted to local hiring in the US, nearshore centers in Mexico and Canada, and automation.

The Indians who remain in the H-1B pool are increasingly direct hires at Amazon, Google, Microsoft, Apple, and Meta — positions that command Level III and IV wages, carry advanced degree preferences, and survive the weighted lottery's selection bias. USCIS itself noted the shift: "We're approving more applicants with advanced degrees and higher salaries — especially those who studied at U.S. universities."

## The Two-Track Diaspora

For Indian professionals already in the US, the shrinking pool has a counterintuitive upside: less competition at the top. If you hold a US master's degree and a job offer above the $130,000 median for computer occupations, your lottery odds under the weighted system are better than they were under random selection. The H-1B is becoming a program for people who are, statistically speaking, already winning.

For the broader ecosystem of Indian tech talent — the Tier 2 engineering college graduate, the three-year experience developer at a services company in Hyderabad, the first-generation applicant hoping the lottery changes everything — the doors are narrowing. The registration fee alone ($250, up from $10) makes speculative applications expensive. The weighted lottery makes low-wage filings near-futile. The $100,000 surcharge makes employer sponsorship at entry-level wages economically irrational.

## What This Means Going Forward

The 38.5% decline is not a one-year anomaly. It is the intended consequence of a policy architecture designed to reduce volume and increase selectivity. USCIS received 17,000 comments on the weighted lottery rule and made no changes. The $100,000 fee survived its initial legal challenges (though appeals continue). The fraud crackdowns are permanent.

For Indian families planning around the H-1B pathway — parents advising children on US graduate school, engineers weighing the GRE against a Bangalore promotion — the message is clear. The H-1B still exists. Indians still win most of them. But "most of a smaller number" is a very different proposition than "most of a large one." The program that once processed 780,000 registrations in a single year now handles 211,600. That is not a lottery. That is a filter."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The New H-1B Wage Floor Is Still a Basement",
        "subheadline": "The Department of Labor proposes raising the minimum H-1B salary from the 17th to the 34th percentile. Critics say it still lets employers pay foreign workers less than two-thirds of their American colleagues — and Indian tech workers will feel it first.",
        "slug": make_slug("dol-h1b-prevailing-wage-rule-34th-percentile-indian"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals hold 71% of H-1B visas, and a disproportionate share are filed at Level I and Level II wages — the exact tiers affected by this rule. The proposed change simultaneously raises the floor (more money) and worsens lottery odds (the weighted system penalizes lower wage levels). For Indian tech workers, it is a double squeeze: pay more to compete, and still compete at a disadvantage.",
        "tags": ["h1b", "prevailing-wage", "dol", "wage-rule", "indian-tech-workers"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Daily Caller", "url": "https://dailycaller.com/2026/05/23/trumps-labor-department-is-making-critical-mistake-with-immigration-rule/"},
            {"name": "LegalClarity", "url": "https://legalclarity.org/u-s-visa-updates-h-1b-uscis-fees-and-ead-changes/"},
            {"name": "Mondaq", "url": "https://www.mondaq.com/unitedstates/immigration/1569984/us-immigration-updates--january-2026"},
            {"name": "BizzBuzz News", "url": "https://www.bizzbuzz.news/economy/indian-tech-jobs-in-us-at-risk-h-1b-approvals-fall-sharply-1361988"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5198201/pexels-photo-5198201.jpeg",
        "body": """The US Department of Labor has proposed a new rule governing the minimum salary employers must pay H-1B workers. It is being promoted as a major reform to protect American workers from wage undercutting. A closer look at the numbers suggests the protection is more theatrical than structural — and for the roughly 500,000 Indian professionals currently working on H-1B visas, the implications cut in multiple directions at once.

## The Prevailing Wage System, Explained

Every H-1B petition requires the employer to pay at least the "prevailing wage" for the occupation and geographic area. The government divides wages into four levels. Level I is for entry-level positions. Level IV is for fully competent, senior roles. In theory, this prevents employers from using foreign labor to undercut domestic salaries. In practice, the floors have been set so low that the system has functioned as a discount mechanism.

For years, Level I wages sat at approximately the 17th percentile — meaning employers could legally pay an H-1B worker less than what 83% of American workers in the same occupation already earned. The new proposal raises Level I to around the 34th percentile. Level II moves from the 34th to approximately the 45th percentile.

The increase sounds meaningful until you do the arithmetic. At the 34th percentile, an employer can still pay an H-1B software developer less than what two-thirds of similarly employed Americans make. The "prevailing wage" is not, and has never been, anything close to the actual prevailing wage. It is a regulatory floor set well below the market median.

## The Double Squeeze on Indian Workers

The prevailing wage rule does not operate in isolation. It intersects with the new weighted H-1B lottery system that went into effect for FY2027, creating a compounding pressure on Indian tech workers.

Under the weighted lottery, registrations at Wage Level IV enter the selection pool four times; Level I enters once. This means that a Level I filing has roughly one-quarter the selection probability of a Level IV filing. The DOL's proposed wage increase raises the Level I floor — making it more expensive to file at the bottom tier — but does nothing to improve the lottery odds for those positions. An employer who previously filed an H-1B at Level I for a junior developer in Dallas now faces a higher minimum salary AND worse lottery odds.

For Indian IT services companies — TCS, Infosys, Wipro, HCL — that historically filed large numbers of H-1B petitions at Level I and Level II wages, the combined effect is devastating. Higher wage floors increase labor costs. Worse lottery odds decrease the probability of securing the visa. The $100,000 surcharge on certain lower-wage filings adds a third layer of cost. The rational business response is exactly what the data shows: Indian IT firms have cut H-1B filings by 46% over five years.

## Who Benefits, Who Loses

The wage rule creates clear winners and losers within the Indian diaspora.

**Winners:** Indian professionals already employed at US companies in senior roles. Higher prevailing wages across the board mean their own compensation benchmarks rise. A Level III or Level IV H-1B worker at Google or Microsoft benefits from a system that forces employers to pay more — it protects against the theoretical scenario where a company replaces them with a cheaper H-1B hire. These workers also have superior odds in the weighted lottery and are unaffected by the $100,000 surcharge.

**Losers:** Early-career Indian professionals seeking their first H-1B sponsorship. The higher wage floor, combined with the weighted lottery and the $100,000 fee, makes entry-level H-1B sponsorship economically irrational for many employers. A company considering whether to sponsor a fresh IIT graduate at a Level I salary must now weigh the higher minimum wage, the diminished lottery odds, and the potential $100,000 surcharge against simply hiring locally or offshoring the role to Bangalore.

## The Unspoken Architecture

Read together — the weighted lottery, the $100,000 fee, and the prevailing wage increase — these policies form a coherent architecture. They do not eliminate the H-1B program. They stratify it. The top tier of Indian talent — US-educated, senior-level, employed at brand-name companies — retains access. The broad middle — competent engineers at services firms, first-generation applicants from Tier 2 colleges, early-career developers — is systematically priced out.

The DOL's proposed rule is currently in the public comment period. The 17,000 comments submitted on the weighted lottery rule produced zero changes. Whether the prevailing wage proposal fares differently depends on whether the administration views the comments as democratic input or procedural obligation.

For Indian tech workers doing the math on their American future, the calculation increasingly favors one conclusion: the H-1B is no longer a program for the many. It is a program for the few who can afford to play at Level III and above. The wage floor may have risen from the 17th percentile to the 34th. But when the ceiling of opportunity is dropping faster, a higher floor is cold comfort."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
