#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-31 16:00 UTC run"""

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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# Verify images before inserting
def verify_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        return r.status_code == 200 and "image" in ct and cl > 5000
    except Exception:
        return False


# ── Article 1 ──────────────────────────────────────────────────────────────
art1_image = "https://images.pexels.com/photos/7009478/pexels-photo-7009478.jpeg?auto=compress&cs=tinysrgb&w=1200"
art1_body = """The H-1B lottery used to be the opening act. You registered, crossed your fingers, and if the algorithm smiled on you, you spent the next six to twelve years grinding toward a green card through EB-2 or EB-3 — categories with Indian backlogs stretching past 2012 priority dates.

That calculus is breaking apart. With the $100,000 employer fee discouraging new H-1B petitions, the weighted lottery favoring higher-wage positions, and USCIS processing times ballooning for routine extensions, a growing number of Indian tech professionals are skipping the queue entirely and self-petitioning for EB-1A — the "extraordinary ability" green card that requires no employer sponsorship, no labor certification, and no lottery.

## The Numbers Tell the Story

EB-1A applications surged 56 percent quarter-over-quarter to 7,338 in the first quarter of FY 2025, according to data cited by Boundless Immigration — the sharpest single-quarter jump since records began. Immigration attorneys in Bengaluru and Hyderabad report a three-fold increase in Indian tech founders and senior engineers seeking help with citation analysis, reference letter strategy, and the ten-point evidentiary test that EB-1A demands.

The trend has only accelerated since. With FY 2027 H-1B registrations collapsing 38 percent year-over-year and only 85 employers willing to pay the $100,000 surcharge as of February, the economic logic of EB-1A has become irresistible for anyone with a plausible claim to "extraordinary" achievement.

## What EB-1A Actually Requires

The bar is high but not impossible. Applicants must demonstrate sustained national or international acclaim and meet at least three of ten criteria: original contributions of major significance, published scholarly articles, judging the work of others, membership in associations requiring outstanding achievement, high salary, and so on. In practice, a senior engineer at a major tech company with a few patents, conference presentations, and peer-reviewed publications can build a competitive case.

The appeal for Indians is structural. Unlike EB-2 or EB-3, where priority dates for India-born applicants are mired in backlogs that can stretch 10 to 15 years, EB-1A is a first-preference category with significantly shorter waits. And unlike NIW — the National Interest Waiver pathway that saw denial rates surpass EB-1A's last fiscal year — the EB-1A category carries a denial rate of roughly 26 percent, manageable for well-prepared petitions.

## The Economics of Escape

The math is straightforward. An H-1B renewal now risks an employer facing the $100,000 fee if the worker leaves and re-enters on a new petition. An EB-1A self-petition costs roughly $2,500 in government fees (plus premium processing at $2,805) and requires no employer involvement at all. The worker controls the timeline, the employer bears no cost, and the green card — once approved — frees both parties from the cycle of visa renewals, stamping trips to Chennai or Hyderabad, and the omnipresent threat of a 60-day clock after layoff.

Immigration lawyers note one critical advantage: EB-1A holders are not tied to a sponsoring employer. In an era of mass tech layoffs — 110,000 and counting in 2026 — that portability is worth more than any lottery win.

## The Catch

USCIS adjudication standards remain exacting under current memos. Officers are applying the Kazarian framework — a two-step process that first checks whether the applicant meets three of the ten criteria, then evaluates whether the totality of evidence demonstrates sustained acclaim. Weak claims get denied, and denials carry consequences: a failed EB-1A attempt does not bar future filings, but it can trigger scrutiny on subsequent petitions.

The practical advice from attorneys: start building your portfolio 12 to 18 months before filing. Patent applications, peer-reviewed publications, media coverage, and documented impact on your field all count. What does not count: simply being good at your job. USCIS draws a firm line between "skilled" and "extraordinary."

## Why This Matters for Indian Americans

For the roughly 300,000 Indian nationals waiting in the EB-2 and EB-3 backlogs, EB-1A represents the only realistic path to a green card within a human lifetime. The category does not eliminate the backlog — it offers an exit from it. And as H-1B becomes more expensive, more uncertain, and more politically fraught, the exodus from employer-dependent visa categories to self-petitioned green cards is likely to accelerate.

The question is whether USCIS can handle the volume. If EB-1A applications continue growing at their current pace, the category itself could develop a backlog — turning today's escape hatch into tomorrow's bottleneck."""

# ── Article 2 ──────────────────────────────────────────────────────────────
art2_image = "https://images.pexels.com/photos/7178551/pexels-photo-7178551.jpeg?auto=compress&cs=tinysrgb&w=1200"
art2_body = """Two federal courthouses. Two judges. Two very different readings of the same question: can a president charge employers $100,000 for each H-1B visa, using nothing more than a broad immigration statute and his own proclamation?

On one side of the ledger, U.S. District Judge Beryl Howell in Washington, D.C., ruled in the U.S. Chamber of Commerce's challenge that Trump's sweeping powers under federal immigration law gave him the authority to impose the fee. The business lobby's case was dismissed. On the other, U.S. District Judge Leo Sorokin in Boston spent a hearing on May 30 doing something Howell did not: pressing the government to explain whether that authority has any limits at all.

The answer he got from the Department of Justice was remarkable — and troubling for every Indian tech worker whose career depends on the H-1B program.

## "It's a Very Sweeping Power"

Tiberius Davis, the DOJ attorney defending the fee, told Sorokin that Trump's authority under the Immigration and Nationality Act to restrict entry of noncitizens is essentially boundless. When the judge asked whether that theory would permit the president to impose a $100,000 fee on Americans wanting to marry non-citizens — or force a company to forfeit 10 percent of its equity to bring in a single foreign worker — Davis responded that yes, Trump "possibly could take those hypothetical actions."

"It's a very sweeping power," Davis said.

The admission was not a gaffe. It was the government's legal position, stated on the record in open court.

## The Tariff Precedent

James Richardson, representing California and 19 other state attorneys general, offered the judge a counter-argument with real teeth. He pointed to the Supreme Court's February ruling striking down Trump's emergency tariffs — a case where the court found that Congress does not delegate taxing authority through vague statutory language, even when the statute technically permits the executive to act.

"Congress does not delegate a tax authority in ambiguous language," Richardson argued. If the tariff ruling means anything, he said, it means that calling the $100,000 charge a "fee" does not transform what is functionally an unconstitutional tax into a lawful exercise of immigration authority.

The distinction matters enormously. If Sorokin follows Howell and defers to the executive, the $100,000 fee stands — and the president has established the legal precedent to raise it further, extend it to other visa categories, or impose similar financial barriers on any immigration pathway. If he follows the tariff ruling and treats the fee as a tax that Congress never authorized, the proclamation collapses.

## Eighty-Five Payments

The fee's practical impact is already visible in the data. As of February 15, USCIS had received exactly 85 payments of the $100,000 fee — out of the tens of thousands of H-1B petitions typically filed each year. FY 2027 H-1B registrations dropped 38 percent year-over-year. The fee did not reform the system. It emptied it.

For Indian IT services firms — Infosys, TCS, Wipro, and their smaller competitors — the fee has effectively priced out new H-1B placements. Major American tech companies can absorb the cost for critical hires, but the middle tier of employers that once sponsored thousands of Indian workers each year has largely stopped trying. The work is moving offshore, to Hyderabad and Pune, exactly as the administration intended.

## What Happens Next

Judge Sorokin has not yet ruled. Legal observers expect a decision within weeks, and a split between the D.C. and Massachusetts courts would create a circuit conflict that almost certainly reaches the Supreme Court. The justices have already shown willingness to curb executive overreach on economic matters — the tariff ruling being the most direct precedent — but immigration has historically been treated as a domain of broad executive discretion.

The case is *State of California et al v. Mullin*, No. 25-cv-13829, in the District of Massachusetts.

## Why This Matters for Indian Americans

For the roughly 600,000 Indian nationals in the H-1B pipeline — those currently working, those waiting for lottery results, and those whose employers are deciding whether to sponsor them — these two court cases will determine the financial architecture of legal immigration for years to come. A Supreme Court ruling upholding the $100,000 fee would not merely make H-1B visas expensive. It would establish that the president can unilaterally set any price on any immigration benefit, at any time, with no congressional approval required.

That is not a fee structure. It is a veto power with a price tag."""

# ── Build article records ─────────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Skip the Lottery, File Your Own Case — Inside the EB-1A Gold Rush Reshaping Indian Immigration",
        "subheadline": "EB-1A self-petitions surged 56 percent in a single quarter as Indian tech workers abandon the H-1B pipeline for a green card category that requires no employer, no lottery, and no $100,000 fee.",
        "slug": make_slug("eb1a-gold-rush-indian-tech-self-petition-green-card"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For the 300,000 Indian nationals stuck in EB-2/EB-3 backlogs stretching past 2012 priority dates, EB-1A is the only realistic path to a green card within a human lifetime — and the $100K H-1B fee has made the economics irresistible for anyone who qualifies.",
        "tags": ["eb-1a", "green-card", "h1b", "immigration", "self-petition", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "VisaHQ", "url": "https://visahq.com/costly-h1b-stricter-us-rules-push-indians-toward-self-sponsored-eb-1a-green-cards"},
            {"name": "Boundless Immigration", "url": "https://www.boundless.com/"},
            {"name": "Reuters", "url": "https://www.reuters.com/legal/us-judge-questions-scope-trumps-power-impose-100000-h-1b-visa-fee-2026-05-30/"},
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": art1_image,
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Two Courts, Two Answers, One $100,000 Question — The H-1B Fee Fight Heading for the Supreme Court",
        "subheadline": "A federal judge in D.C. upheld the fee. A federal judge in Boston wants to know if it has any limits at all. The DOJ says it does not.",
        "slug": make_slug("h1b-100k-fee-circuit-split-supreme-court-indian"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For the 600,000 Indian nationals in the H-1B pipeline, these two cases will determine whether the president can unilaterally set any price on any immigration benefit — turning legal immigration from a process into a pricing decision.",
        "tags": ["h1b", "100k-fee", "court", "supreme-court", "immigration", "legal-challenge"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/us-judge-questions-scope-trumps-power-impose-100000-h-1b-visa-fee-2026-05-30/"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/doj-asserts-trump-authority-in-h-1b-visa-fee-case-has-few-limits"},
            {"name": "Daily Caller", "url": "https://dailycaller.com/2026/05/29/irs-weaponization-fund-immigration-enforcement-reconciliation/"},
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": art2_image,
        "body": art2_body,
    },
]

# Validate images
for art in articles:
    img = art["image_url"]
    if not verify_image(img):
        print(f"⚠️  Image failed validation for {art['slug']}: {img}")
        # Use a known-good fallback
        art["image_url"] = "https://images.pexels.com/photos/8061944/pexels-photo-8061944.jpeg?auto=compress&cs=tinysrgb&w=1200"

# Insert
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
