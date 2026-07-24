#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-06-10 12:00 UTC run"""
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

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 1: Denaturalization — Neeraj Sharma / Indian H-1B fraud
# ─────────────────────────────────────────────────────────────────────

article1_body = """The Department of Justice filed denaturalization actions against seventeen naturalized Americans on June 8 — the second mass filing in six weeks and the latest escalation in what officials are calling the largest citizenship-revocation campaign in United States history. For the roughly 2.7 million Indian-born naturalised citizens living in the country, one name in the batch landed harder than the rest.

## The New Jersey Staffing Boss Who Forged His Way In

Neeraj Sharma, 50, a native of India and the owner of Magnavision LLC, a staffing company in New Jersey, is accused of filing eleven fraudulent H-1B visa petitions with USCIS. According to the DOJ complaint, each petition falsely claimed that the visa beneficiaries would be employed at a global financial institution, and included letters on official corporate letterhead with forged executive signatures. Sharma naturalised in December 2017 after swearing under oath that he had never committed a crime for which he was not arrested, never supplied false information to a government official, and never lied to obtain an immigration benefit. All three statements, federal prosecutors allege, were lies. He was subsequently convicted of visa fraud under 8 U.S.C. § 1546.

Sharma is not the first Indian national in the crosshairs. In April, an India-born man named Gurdev Singh Sohal had his citizenship revoked after a federal court found he had concealed a prior deportation order issued under a different name. His naturalisation had stood for twenty years before Operation Janus — a DHS fingerprint-matching programme that digitised 315,000 old paper records — caught the discrepancy.

## The Numbers Behind the Push

The scale of the current campaign dwarfs anything in modern memory. Between 1990 and 2017, the government filed an average of eleven denaturalization cases per year. During Trump's first term, that climbed to roughly 25. In April 2026, the DOJ confirmed it had referred 384 individuals for denaturalization across 39 U.S. attorney offices — more than the combined totals of the Biden and first Trump administrations. An internal USCIS memo from December 2025 set a target of 100 to 200 new cases per month.

"When criminal aliens exploit the naturalization process by breaking the law, there are consequences," Acting Attorney General Todd Blanche said in a statement. DHS Secretary Markwayne Mullin was blunter: "If you come here, break our laws, and lie in your immigration proceedings, you forfeit that privilege."

https://x.com/ABORRACHITAZ/status/1932087625032384702

## Why Indian Americans Should Pay Attention

The legal standard for denaturalization has not changed. The government still must prove in federal court that a person obtained citizenship through fraud, willful misrepresentation, or concealment of a material fact. The Supreme Court held in *Maslenjak v. United States* (2017) that the lie must have been material — meaning it actually changed the outcome. Small errors on a form, with no bearing on eligibility, do not qualify.

But the enforcement posture has changed dramatically. What was once reserved for war criminals and terrorism suspects now extends to visa fraud, benefits fraud, and undisclosed criminal records. Indian Americans, who represent one of the largest naturalized populations from any single country, have particular reason to track the trend. H-1B holders who eventually naturalise have complex paper trails — employer changes, status transitions, and I-140 filings stretching over a decade or more. Any inconsistency, however innocent, now sits in a system designed to find discrepancies at scale.

## What You Should Do

Immigration attorneys recommend three steps. First, keep your Certificate of Naturalization and U.S. passport in a secure place and make digital copies. Second, do not respond to any USCIS notice or federal court summons without consulting a lawyer — denaturalization is a civil proceeding with full judicial review. Third, review your original naturalization application (Form N-400) for accuracy. If you discover an honest error, an attorney can advise on whether a proactive correction is appropriate.

The DOJ has signalled this is not the final wave. As Operation Janus continues matching fingerprints across decades of records, the pipeline of referrals is likely to grow. For the millions of Indian Americans who did everything by the book, the practical risk remains low. But the era of treating naturalised citizenship as permanently settled is, for better or worse, over."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Neeraj Sharma Filed Eleven Fake H-1B Petitions — Now America Wants His Citizenship Back",
    "subheadline": "An Indian-born New Jersey staffing boss is among 17 naturalized citizens targeted in the DOJ's latest denaturalization sweep, the largest in US history.",
    "slug": make_slug("neeraj-sharma-h1b-fraud-denaturalization-india"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "India-born Neeraj Sharma is explicitly named in the DOJ's latest denaturalization batch for H-1B visa fraud. Combined with the earlier Gurdev Singh Sohal case (citizenship revoked after 20 years), two Indian nationals now feature in the expanded program. The 2.7M Indian-born naturalized citizens in the US face a dramatically different enforcement environment, especially those with complex H-1B-to-green-card paper trails.",
    "tags": ["denaturalization", "h1b-fraud", "uscis", "citizenship", "neeraj-sharma", "doj"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "U.S. Department of Justice", "url": "https://www.justice.gov/opa/pr/justice-department-moves-strip-us-citizenship-17-naturalized-sex-offenders-fraudsters-drug"},
        {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/06/09/trump-administration-denaturalization-citizenship-revoked/84158392007/"},
        {"name": "BET News / CBS News", "url": "https://www.bet.com/article/vbmx70/the-trump-administration-is-stripping-citizenship-at-a-record-pace"},
        {"name": "WhatsUpCongress Tracker", "url": "https://whatsupcongress.com/market-intel/trump-denaturalization-list-2026"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/2025_Naturalization_Ceremony-_Oath_of_Citizenship_%2854813557413%29.jpg/1280px-2025_Naturalization_Ceremony-_Oath_of_Citizenship_%2854813557413%29.jpg",
    "image_caption": "New US citizens take the oath of citizenship at a 2025 naturalization ceremony",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 2: Mandatory E-Verify Act of 2026
# ─────────────────────────────────────────────────────────────────────

article2_body = """Senator Katie Britt introduced the Mandatory E-Verify Act of 2026 this month, a bill that would require every employer in the United States to electronically verify the work eligibility of every new hire. The legislation is aimed squarely at illegal immigration — but if it passes, it will change the hiring paperwork for every H-1B holder, every OPT student, and every green card applicant in the country.

## What the Bill Does

The core mandate is straightforward: all U.S. employers would be required to run new hires through E-Verify, the Department of Homeland Security's online system that checks a worker's name and Social Security number against federal databases. Currently, E-Verify is mandatory only for federal contractors and in a patchwork of states that have adopted their own requirements. Most private employers use it voluntarily, if at all.

Britt's bill would end the opt-in era. It would also enhance civil and criminal penalties for employers who knowingly hire workers not authorised to work, strengthen anti-fraud measures within E-Verify itself, and — critically — prohibit states from passing laws that block employers from using the system.

The bill has bipartisan support on the surface: polls consistently show Americans favour mandatory employment verification. But it faces headwinds from business lobbies that worry about false positives, agricultural interests dependent on undocumented labour, and civil liberties groups concerned about a de facto national ID system.

## The Indian Worker Angle

If you are on an H-1B, an L-1, OPT, or STEM OPT, E-Verify already touches your life in ways you may not realise. Every time you change employers, your new company files an I-9 form. E-Verify cross-references that form with DHS and Social Security records. For authorised workers, the check usually clears within seconds. But the system has a known error rate — the Government Accountability Office has documented that roughly 0.15% of work-authorised employees receive initial "tentative non-confirmations" that require manual resolution.

For Indian workers on employer-sponsored visas, the consequences of a false positive are disproportionate. An H-1B holder who receives a tentative non-confirmation has eight federal business days to contest it. During that window, the employer cannot fire them — but the employer also knows the worker's status is under scrutiny. In a climate where companies are already nervous about immigration enforcement, a false flag from E-Verify can chill a hiring decision before it ever reaches a formal denial.

Indian IT services firms — Infosys, TCS, Wipro, Cognizant — already use E-Verify for their U.S. operations, largely because many of their clients are federal contractors. But the Britt bill would bring every small and mid-size employer into the system: the startup that hires its first H-1B engineer, the hospital that sponsors a physician, the university that employs post-docs on OPT. Compliance costs for smaller employers could range from $200 to $800 per verification cycle, according to estimates from the National Federation of Independent Business.

## The Enforcement Math

The bill arrives at a moment when the administration is tightening every lever of immigration enforcement simultaneously. The reconciliation package approved by the Senate last week includes $70 billion for border and interior enforcement through 2029. ICE deported 442,000 people in fiscal 2025. The PERM labor certification backlog has stretched to 501 days. And USCIS is processing H-1B fee increases that one federal judge has already struck down as an illegal tax.

Mandatory E-Verify adds a demand-side tool to what has been a supply-side enforcement strategy. If employers face real penalties for hiring without verification, the argument goes, the economic magnet for unauthorised migration weakens. Supporters point to states like Arizona and Mississippi, where mandatory E-Verify laws correlated with measurable declines in undocumented employment.

## What to Watch

The bill's path through Congress is uncertain. The Senate Judiciary Committee has not scheduled a hearing. Business groups including the U.S. Chamber of Commerce have historically opposed blanket mandates, preferring a voluntary system with liability protections. Agricultural lobbies will push for exemptions.

For Indian diaspora professionals, the practical takeaway is mundane but important: keep your employment authorisation documents current, ensure your Social Security records are accurate, and flag any name or date-of-birth discrepancies with SSA before they surface in an E-Verify check. If the bill passes, the I-9 process that already punctuates every job change will become the front door of a federal enforcement system — and the margin for paperwork errors will shrink to zero."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Every Employer in America May Soon Have to E-Verify You",
    "subheadline": "Katie Britt's Mandatory E-Verify Act would force all US employers to electronically confirm work eligibility — a change that touches every H-1B holder, OPT student, and green card applicant.",
    "slug": make_slug("mandatory-e-verify-act-2026-h1b-indian-workers"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "While aimed at illegal immigration, mandatory E-Verify would change the hiring verification process for every Indian H-1B holder, OPT student, and green card applicant. False positives disproportionately affect workers on employer-sponsored visas, and smaller employers unfamiliar with immigration paperwork would face new compliance costs — potentially chilling H-1B hiring.",
    "tags": ["e-verify", "h1b", "employment-verification", "katie-britt", "immigration-enforcement"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/opinion/3448977/deportation-hits-supply-illegal-immigration-mandatory-e-verify-address-demand/"},
        {"name": "Des Moines Register", "url": "https://www.desmoinesregister.com/story/news/politics/2026/06/04/iowa-public-workers-mandatory-e-verify-law/84024135007/"},
        {"name": "U.S. Government Accountability Office", "url": "https://www.gao.gov/products/gao-11-146"},
        {"name": "National Federation of Independent Business", "url": "https://www.nfib.com/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/19574309/pexels-photo-19574309.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "The US Capitol building in Washington, DC, where the Mandatory E-Verify Act faces its next legislative hurdle",
    "image_attribution": "Pexels",
    "body": article2_body,
}

# ─────────────────────────────────────────────────────────────────────
# Insert articles
# ─────────────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
