#!/usr/bin/env python3
"""Immigration writer — 2026-07-14 01:00 PDT run."""

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
    return slug[:70].rstrip("-") + "-20260714"


# ────────────────────────────────────────────────────────────────
# ARTICLE 1
# ────────────────────────────────────────────────────────────────

article1_body = """Three federal agencies issued new guidance on Monday telling banks that loans to people without legal work authorization in the United States carry elevated credit risk. The advisory is nonbinding. Its practical effect may be anything but.

The Office of the Comptroller of the Currency, the Federal Deposit Insurance Corporation, and the National Credit Union Administration issued the joint statement to implement a May executive order from President Trump directing regulators to flag potential financial-services risks tied to undocumented immigrants. The guidance does not create new legal requirements, but it crystallises a message the administration has been telegraphing for months: lenders who extend credit to borrowers whose immigration status is uncertain do so at their own regulatory peril.

"When a borrower's income is derived from employment that is not legally authorized, the source of repayment may be less reliable and may present increased credit risk," the agencies wrote. They cited possible deportation, involuntary job loss, and an inability to find future legal employment as factors that could impair repayment.

## The bigger picture

Monday's guidance is the latest in a cascade of federal actions squeezing non-citizen borrowers out of the American financial system. In January 2026, the Department of Justice and the Consumer Financial Protection Bureau withdrew a Biden-era policy that had explicitly barred lenders from discriminating on the basis of immigration status. In June, the CFPB went further, issuing guidance that lenders *may be legally required* to consider a borrower's immigration status under the Truth in Lending Act — particularly where deportation could disrupt income.

And then there is the FHA ban. In May 2025, the Department of Housing and Urban Development ended eligibility for FHA-insured mortgages for non-permanent residents, including H-1B visa holders. The impact was swift: Optimal Blue data shows that non-permanent residents' share of FHA mortgage locks fell from 3.8 per cent in September 2024 to 0.2 per cent by September 2025.

## Why Indian Americans should pay attention

The guidance technically targets people without legal work authorisation — a category that does not include H-1B holders, green card applicants in queue, or EAD holders. But the regulatory direction of travel is clear, and banks tend to over-comply.

When regulators tell banks to scrutinise a borrower's work authorisation, the compliance departments that implement the guidance rarely draw fine distinctions between an undocumented worker and an H-1B holder whose visa expires in eleven months. The chilling effect is what matters. An Indian software engineer in Sunnyvale with a perfectly valid H-1B and an I-140 approval may find that her mortgage application triggers additional documentation requests, longer processing times, or quiet steering toward higher-rate conventional products now that FHA is closed.

The practical squeeze is compounding. H-1B holders can no longer access FHA-insured mortgages. Banks are now being told to factor work-authorisation risk into underwriting. The $100,000 H-1B filing fee — struck down by a federal judge in June but still effective in another circuit — has already prompted some employers to pause sponsorship. Each measure, individually, is defensible. Together, they form a financial architecture that makes it harder for legal, documented, tax-paying immigrants to build wealth in the country they live and work in.

## What the industry says

The Wall Street Journal reported that the administration had considered — but ultimately did not pursue — a more aggressive approach that would have required banks to collect citizenship data on all account holders. Monday's guidance was characterised as a lighter touch. The banking industry, by most accounts, exhaled.

But immigration attorneys say the softer language is precisely the point. "Nonbinding guidance that reminds banks of 'existing obligations' is how you change behaviour without changing law," said one New York-based immigration lawyer who represents Indian-origin professionals. "Banks read the room. They will be more cautious."

A working paper from the Federal Reserve Bank of Dallas, released alongside the guidance, estimated that unauthorised immigrant worker flows accounted for roughly 30 per cent of home-price growth and about 20 per cent of rent growth in the average metro area between March 2021 and March 2024. The administration cited the paper as evidence that immigrant lending warrants greater scrutiny; economists noted the paper explicitly said immigration was not the "sole driver" of rising housing costs.

## The bottom line

For the roughly 600,000 Indian-origin H-1B holders and their families — many of whom have lived in the United States for a decade or more while waiting for green cards — the question is no longer just whether they can stay. It is whether the financial system will treat them as full participants while they do."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Three Federal Agencies Just Told Banks to Think Twice Before Lending to Immigrants",
    "subheadline": "New OCC, FDIC, and NCUA guidance flags work-authorisation risk in lending. The rules target undocumented workers. The chill will reach H-1B holders.",
    "slug": make_slug("bank-regulators-warn-immigrant-lending-risk-h1b"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "H-1B holders and green card applicants may face tighter lending scrutiny as banks over-comply with new federal guidance, compounding the FHA mortgage ban that already shut them out of government-backed home loans.",
    "tags": ["h1b", "immigration", "banking", "mortgage", "fha", "cfpb", "occ"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/finance/us-bank-regulators-warn-firms-lending-undocumented-workers-2026-07-13/"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/politics/policy/trump-regulators-seek-to-discourage-loans-to-undocumented-immigrants-0b2a3f12"},
        {"name": "ABA Banking Journal", "url": "https://bankingjournal.aba.com/2026/06/cfpb-creditors-may-be-required-to-check-immigration-status/"},
        {"name": "Fast Company (ResiClub)", "url": "https://www.fastcompany.com/91257161/fha-ban-nonpermanent-residents-mortgage-locks-h1b"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/CFPB_Consumer_Financial_Protection_Bureau_entrance_Washington_DC_2025-02-10_11-14-45.jpg/1280px-CFPB_Consumer_Financial_Protection_Bureau_entrance_Washington_DC_2025-02-10_11-14-45.jpg",
    "image_caption": "The entrance to the Consumer Financial Protection Bureau headquarters in Washington, D.C.",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip(),
}

# ────────────────────────────────────────────────────────────────
# ARTICLE 2
# ────────────────────────────────────────────────────────────────

article2_body = """Congress wants to bring 40,000 foreign doctors and nurses into the United States. The Department of Labor is investigating whether the ones already here got in through fraud. Both things are happening at the same time, and no one in Washington appears to see the contradiction.

The Healthcare Workforce Resilience Act, a bipartisan bill reintroduced in both chambers, would recapture up to 40,000 unused employment-based green cards — 25,000 for nurses and 15,000 for physicians — and expedite processing without additional fees. The bill has fourteen Senate co-sponsors across both parties, backing from the American Hospital Association, the American Medical Association, and dozens of healthcare organisations, and a simple premise: the country is bleeding healthcare workers and immigrants can help stop it.

The numbers support the premise. The Association of American Medical Colleges projects a shortage of up to 124,000 physicians by 2034. The American Hospital Association estimates that more than 610,000 nurses intend to leave the profession by 2027. Rural and medically underserved areas are hit hardest.

Then, on July 8, the other shoe dropped.

## The fraud probe

Vice President JD Vance and Labor Department Inspector General Anthony D'Esposito announced a "major investigation" into H-1B visa fraud, and they singled out healthcare as a primary target. D'Esposito told the New York Post that fraudsters had scammed "hundreds of millions" of dollars from the medical industry. He described schemes in which "employers and labor brokers submitted fraudulent applications, exploited foreign workers through coercive wage-kickback arrangements, and undercut American workers by flooding the market with below-wage labor."

His office has issued dozens of subpoenas. On Fox Business, D'Esposito said whistleblowers had come forward about "some of the biggest companies," naming Cognizant, the India-founded IT services firm based in New Jersey. Cognizant did not respond to requests for comment.

The probe's healthcare focus carries a sharper edge. The Daily Caller reported that India seized over 100,000 forged diplomas from 28 universities in December 2025 — diplomas that had been accepted by American companies for employment. A former U.S. diplomat, Mahvash Siddiqui, has alleged that 80 to 90 per cent of the H-1B visa applications from India she reviewed during her tenure involved "fraudulent documentation or unqualified applicants."

India is the largest source country for physicians and surgeons in the United States and the second largest for registered nurses.

## The $100,000 wall

Meanwhile, a separate bipartisan bill — the Physicians and the Healthcare Workforce Act, sponsored by Representatives Mike Lawler (R-NY), Sanford Bishop (D-GA), Maria Elvira Salazar (R-FL), and Yvette Clarke (D-NY) — would exempt healthcare workers from the $100,000 H-1B visa filing fee that President Trump imposed via executive order in September 2025. A federal judge struck the fee down in June, ruling it was an unlawful tax, but the fee remains in effect in another federal circuit pending appeal.

The American Hospital Association has warned that the fee has already forced hospitals to limit their intake of sponsored residents and reconsider hiring any applicant who requires H-1B sponsorship. Immigrants account for 27 per cent of physicians and surgeons in the United States, 22 per cent of nursing assistants, and 16 per cent of registered nurses, according to federal data cited in the legislation.

## The diaspora paradox

For Indian-origin healthcare workers, the crosscurrents are disorienting.

On one track, Congress is saying: we cannot staff our hospitals without you. On the other, the executive branch is saying: we believe a significant fraction of you may be fraudulent. Both messages land in the inbox of an Indian doctor in Topeka who trained for five years at an American teaching hospital, passed the USMLE, completed residency, and is now wondering whether her green card application will survive the climate.

The tension is not new — Congress has been trying to pass some version of visa recapture for healthcare workers since at least 2020 — but it has never been this stark. The Healthcare Workforce Resilience Act exempts recaptured visas from per-country caps, which would disproportionately benefit Indian nationals who face the longest backlogs. If the bill passes, Indian doctors and nurses would be among its largest beneficiaries. If the fraud probe's dragnet sweeps too wide, Indian applicants may face the most collateral scrutiny.

Immigration attorneys say the two tracks are not as contradictory as they appear — one targets visa supply, the other targets fraud — but acknowledge that the political messaging collapses the distinction.

## What happens next

The Healthcare Workforce Resilience Act has bipartisan momentum but faces an uncertain path in a Congress consumed by budget fights and the looming fiscal year deadline. The fraud probe is proceeding on its own timeline, with D'Esposito promising to "track down every lead." The $100K fee exemption bill is in committee.

For the Indian doctor in Topeka, none of these timelines answers the question she actually needs answered: Can I stay, and will anyone let me work?"""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "America Desperately Needs Foreign Doctors. It Is Also Investigating Them for Fraud",
    "subheadline": "Congress is trying to recapture 40,000 green cards for nurses and physicians. The DOL is probing healthcare visa fraud worth hundreds of millions. Indian medical professionals are caught in the middle.",
    "slug": make_slug("healthcare-workforce-green-card-recapture-fraud-probe-paradox"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian-origin doctors and nurses — the largest foreign-born group in US healthcare — stand to gain the most from green card recapture legislation but face the most collateral damage from the sweeping healthcare fraud probe.",
    "tags": ["healthcare", "green-card", "h1b", "immigration", "fraud", "uscis", "nursing-shortage"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "American Hospital Association", "url": "https://www.aha.org/news/headline/2025-09-10-congress-reintroduces-aha-supported-bipartisan-workforce-bill-supporting-foreign-nurses-physicians"},
        {"name": "Congress.gov", "url": "https://www.congress.gov/bill/119th-congress/house-bill/5283/text"},
        {"name": "New York Post", "url": "https://nypost.com/2026/07/09/us-news/vance-labor-watchdog-launch-immigration-fraud-probe-to-protect-american-jobs/"},
        {"name": "Becker's Hospital Review", "url": "https://www.beckershospitalreview.com/workforce/federal-bill-seeks-to-exempt-healthcare-workers-from-100k-h-1b-visa-fee.html"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6129243/pexels-photo-6129243.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "A doctor and nurse reviewing patient records in a hospital ward",
    "image_attribution": "Pexels",
    "body": article2_body.strip(),
}

# ────────────────────────────────────────────────────────────────
# INSERT
# ────────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
