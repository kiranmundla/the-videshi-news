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

# Validate image URLs
def validate_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        print(f"  ⚠️ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
        return False
    except Exception as e:
        print(f"  ⚠️ Image validation error: {e}")
        return False


# ──────────────────────────────────────────────────
# ARTICLE 1: The $100K H-1B Fee Lawsuits
# ──────────────────────────────────────────────────

art1_image = "https://images.pexels.com/photos/36984937/pexels-photo-36984937.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"

art1_body = """Only 70 companies have paid the $100,000 H-1B filing fee since President Trump imposed it by proclamation last September. Seventy. Out of the tens of thousands of employers who sponsor H-1B workers every year.

That number — buried in a Bloomberg Law analysis and confirmed by USCIS filing data — tells you everything about how the fee is actually working. It is not filtering for quality. It is not selecting for the "best and brightest," as the administration promised. It is selecting for the very few employers who can absorb a six-figure charge on a single visa petition, which in practice means a handful of large tech companies and investment banks. Everyone else has stopped filing.

## Three Lawsuits, One Appeals Court

The legal battle over the fee has consolidated around three parallel challenges, all of which argue the same fundamental point: a president cannot impose a $100,000 tax on a congressionally created visa program without Congress's approval.

The lead case is the U.S. Chamber of Commerce's suit, now before the D.C. Circuit Court of Appeals. A federal judge rejected the Chamber's initial challenge on December 24, 2025, ruling the fee fell within executive authority. The appeals court fast-tracked the case — opening briefs were due in January, with oral arguments held in February 2026. During those arguments, the three-judge panel pressed government attorneys on a question that could unravel the entire fee: is this actually a tax?

If the court determines the $100,000 charge functions as a revenue-raising measure rather than a regulatory fee, Trump lacked the constitutional authority to impose it. Only Congress can levy taxes. The government's own lawyers struggled with this distinction during oral argument, at one point describing the fee as designed to "deter use" of the H-1B program — which, as the Chamber's attorneys noted, is precisely what a prohibitive tax does.

The second lawsuit, *Global Nurse Force v. Trump*, was filed by a coalition of healthcare staffing agencies, hospitals, and religious organizations. Their argument is narrower but arguably more politically potent: the $100,000 fee is devastating sectors that Congress never intended to harm. Rural hospitals that rely on international nurses cannot absorb $100,000 per petition. Neither can Catholic dioceses sponsoring parish priests, or school districts hiring special education teachers from abroad. The fee was marketed as targeting tech outsourcing firms. It hit everyone else instead.

The third challenge comes from an unlikely alliance: the American Association of University Professors (AAUP) and the United Auto Workers (UAW), joined by other unions. Their argument is that the fee will destroy university research programs that depend on international postdoctoral researchers and faculty — positions that pay $60,000 to $80,000 a year, making a $100,000 filing fee literally larger than the annual salary.

## The Research That Justified the Fee Is Falling Apart

The academic underpinning of the $100,000 fee came primarily from Harvard economist George Borjas, a former adviser to the Council of Economic Advisers, who argued the fee would filter H-1B applicants toward higher-skilled, higher-wage workers. But Bloomberg Law reported that Borjas's research contained methodological errors that may have produced flawed conclusions about wage gaps between H-1B and domestic workers. Other economists have challenged his dataset choices and statistical controls, arguing the research overstated the wage depression caused by H-1B workers.

The erosion of the fee's intellectual justification matters because it weakens the government's argument that the fee serves a legitimate regulatory purpose rather than simply raising revenue — the exact distinction the D.C. Circuit is now evaluating.

## What This Means for Indian Professionals

Indians account for roughly 72% of all H-1B visa holders. Every ripple in the H-1B system hits the Indian diaspora disproportionately.

If the $100,000 fee survives court challenge, the practical effect is a two-tier H-1B system: one for companies wealthy enough to pay six figures per petition, and one for everyone else — meaning no system at all. Mid-size IT services firms, healthcare networks, and universities that historically sponsored thousands of Indian engineers, nurses, and researchers will simply stop. The 70 companies that have paid so far are the ceiling, not the floor.

If the D.C. Circuit strikes the fee down, it establishes a significant precedent limiting presidential authority over immigration fees — a ruling that would constrain future administrations from using fee structures as back-door policy tools. Either outcome reshapes the landscape Indian professionals navigate for years to come.

The court's decision is expected before the FY2027 H-1B filing deadline on June 30, 2026. For hundreds of thousands of Indian workers whose employers are waiting on the ruling before deciding whether to file, the next few weeks are not academic."""

art1_sources = json.dumps([
    {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/few-us-businesses-have-paid-100-000-fee-to-hire-h-1b-workers"},
    {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/dc-circuit-questions-if-trumps-100-000-h-1b-fee-is-a-tax"},
    {"name": "Reuters", "url": "https://www.reuters.com/legal/us-appeals-court-fast-tracks-100000-h-1b-visa-fee-dispute-2026-01-06/"},
    {"name": "California Attorney General", "url": "https://oag.ca.gov/news/press-releases/attorney-general-bonta-supports-legal-challenge-trump-administrations-unlawful"},
    {"name": "Inside Higher Ed", "url": "https://www.insidehighered.com/news/faculty-issues/unions/2025/10/06/aaup-other-unions-sue-trump-admin-over-h-1b-fee"}
])


# ──────────────────────────────────────────────────
# ARTICLE 2: The 3.5% Remittance Tax
# ──────────────────────────────────────────────────

art2_image = "https://images.pexels.com/photos/4968380/pexels-photo-4968380.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"

art2_body = """Every time a non-citizen in the United States sends money abroad — to a parent in Kerala, a sibling in Hyderabad, a cousin building a house in Punjab — the federal government now takes 3.5 cents of every dollar. The remittance excise tax, tucked into the One Big Beautiful Bill Act and effective since January 1, has been operating for five months. Its effects are no longer theoretical.

India is the world's largest recipient of remittances. In 2024, the country received $137.7 billion from its diaspora, according to the World Bank — more than Mexico, China, and the Philippines combined. The United States is the single largest source corridor, with an estimated 5.4 million Indians living in America on various immigration statuses: H-1B holders, green card recipients still years from citizenship, L-1 transferees, H-4 dependents, students.

None of them are citizens. All of them are subject to the tax.

## The Math No One Wants to Do

A software engineer in the Bay Area on an H-1B visa sending $2,000 a month to aging parents in India now pays $70 a month in remittance tax — $840 a year — on top of the wire transfer fees their bank or money transfer service already charges. For a family sending $5,000 quarterly to fund a sibling's medical expenses, the annual tax bill is $700. These are not large sums for people in high-paying tech roles, though they add up. For Indian restaurant workers, H-4 spouses with modest EAD income, or students on OPT sending small amounts home, the 3.5% is proportionally brutal.

The Vision IAS research institute estimates the tax could reduce total remittance inflows to India by $1.6 billion annually. That figure represents money that was going directly to Indian households — paying school fees, covering medical bills, funding small business investments, supporting elderly parents without pensions. It was not passing through government intermediaries or development agencies. It was private family support, and Congress decided to tax it.

## How It Actually Works

The tax applies to "remittance transfers" as defined under the Electronic Fund Transfer Act — essentially any transfer of funds initiated by a consumer in the United States to a recipient in a foreign country. Wire transfers, services like Remitly, Wise, and Western Union, and bank-initiated international transfers all fall within scope. The tax is collected by the remittance transfer provider at the point of transfer and remitted to the IRS.

U.S. citizens are exempt, provided they use qualified remittance providers. This creates a two-tier system that tracks precisely with immigration status. A naturalized Indian American sending money to the same family member, through the same service, pays nothing. Their colleague on an H-1B — who may have been in the country for a decade, paying taxes, contributing to Social Security they may never collect — pays 3.5%.

The original House version of the bill proposed a 5% rate. The reduction to 3.5% was presented as a concession during Senate negotiations. It was not experienced as one by the people paying it.

## The Enforcement Dimension

What has received less attention is the secondary effect of the tax: it creates a federal paper trail of every international money transfer made by non-citizens. Each transaction is now reported to the IRS with the sender's immigration status attached. Immigration attorneys have noted that USCIS officers are beginning to reference remittance patterns during adjustment-of-status interviews — not as evidence of wrongdoing, but as data points in the newly expanded discretionary review framework established by the May 21 policy memorandum.

Sending money home was once a private family act. It is now a taxable, trackable, reviewable transaction that sits in a federal database alongside your immigration file.

## Why This Matters to Indian Americans Specifically

The Indian diaspora in America occupies a unique position in the remittance landscape. Unlike many immigrant communities where remittances are primarily sent by low-wage workers, a substantial share of Indian remittances comes from high-earning professionals — exactly the population on H-1B and green card tracks who are most visible to USCIS and least likely to risk any complication in their immigration case.

The tax also arrives in the context of a green card backlog that keeps Indian nationals as non-citizens for decades. An Indian engineer who entered the U.S. in 2010 on an H-1B, filed for a green card in 2012, and is still waiting in 2026 has been paying American taxes for 16 years. They have been subject to the remittance tax since January. They will continue paying it for however many more years it takes to naturalize — which, for EB-2 India, could be another decade.

The bill's sponsors described the remittance tax as ensuring that "those who benefit from the American economy contribute to it." Indian professionals on H-1B visas already contribute: through federal income tax, state income tax, Social Security, and Medicare — programs many will never access. The remittance tax adds a surcharge on the money left over after all those contributions, directed at the specific act of supporting family abroad.

Five months in, the checks are clearing. The IRS is collecting. And 5.4 million Indians in America are calculating whether the cost of staying keeps going up."""

art2_sources = json.dumps([
    {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/us-revises-tax-on-outbound-remittances-to-35/article69630000.ece"},
    {"name": "Vision IAS", "url": "https://dce.visionias.in/current-affairs/whom-the-remittance-toll-bells"},
    {"name": "BizzBuzz News", "url": "https://www.bizzbuzz.news/economy/india-tops-global-remittance-charts-at-1377-billion-in-2024-1381073"},
    {"name": "Political Science Solution", "url": "https://politicalsciencesolution.com/us-house-approves-one-big-beautiful-bill/"},
    {"name": "Immigration Forum", "url": "https://immigrationforum.org/wp-content/uploads/2025/05/One-Big-Beautiful-Bill-Act-Immigration-Provisions-1.pdf"}
])


articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Seventy Companies Paid. Three Lawsuits Filed. The $100,000 H-1B Fee Is Heading for a Reckoning.",
        "subheadline": "The D.C. Circuit is weighing whether the president can impose a six-figure charge on a visa program Congress created — and the answer could reshape immigration fees for a generation.",
        "slug": make_slug("100k-h1b-fee-lawsuits-dc-circuit-70-companies"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold 72% of H-1B visas. If the $100K fee survives, mid-size employers will stop sponsoring — collapsing the pipeline that brings Indian engineers, nurses, and researchers to America. If it falls, it limits presidential power over immigration fees for future administrations.",
        "tags": ["h1b", "uscis", "immigration", "lawsuit", "100k-fee", "dc-circuit"],
        "urgency": "high",
        "sources": art1_sources,
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": art1_image,
        "image_caption": "The United States Supreme Court — while the $100K H-1B fee case is being heard at the D.C. Circuit, the legal questions may ultimately reach the highest court.",
        "body": art1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Five Months In, the 3.5% Remittance Tax Is Costing Indian Families $1.6 Billion a Year",
        "subheadline": "The One Big Beautiful Bill's excise tax on money sent abroad by non-citizens has been quietly draining the world's largest remittance corridor since January — and creating a federal paper trail of every dollar Indian immigrants wire home.",
        "slug": make_slug("remittance-tax-obbba-indian-families-16-billion"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "India receives more remittances than any country on earth — $137.7 billion in 2024. The 3.5% tax falls exclusively on non-citizens, which includes every Indian on an H-1B, green card, or student visa. With EB-2 India backlogs keeping people as non-citizens for decades, this is a long-term surcharge on supporting family back home.",
        "tags": ["remittance-tax", "obbba", "immigration", "nri", "india-remittances"],
        "urgency": "medium",
        "sources": art2_sources,
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": art2_image,
        "image_caption": "Every dollar sent home now carries a 3.5% federal surcharge for non-citizens — a tax that tracks precisely with immigration status.",
        "body": art2_body
    }
]

# Validate images before inserting
for art in articles:
    print(f"Validating image for: {art['headline'][:60]}...")
    if not validate_image(art["image_url"]):
        print(f"  ❌ Bad image, removing image_url")
        art["image_url"] = None
        art["image_caption"] = None

# Insert articles
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
