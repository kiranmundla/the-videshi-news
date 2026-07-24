#!/usr/bin/env python3
"""Immigration writer — July 1, 2026 1:00 PM PDT run"""
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

# -------------------------------------------------------------------
# ARTICLE 1: USCIS Signature Rule
# -------------------------------------------------------------------
art1_body = """Your employer's HR director signed an H-1B petition last year by scanning her signature from a previous filing and pasting it into the new form. The petition was accepted, receipted, and is now pending. Under the old regime, USCIS might have sent a Request for Evidence asking for a fresh signature. Under the rule that takes effect on July 10, it can simply deny the case, keep the filing fee, and move on.

The interim final rule, published on May 11 in the Federal Register at 91 FR 25479, codifies something USCIS officers have been doing inconsistently for years: treating copy-pasted, stamped, and software-generated signatures as grounds for denial rather than mere rejection. The difference matters. A rejection returns the fee and lets the petitioner refile. A denial retains the fee, closes the case, and forces the petitioner to choose between a costly appeal on Form I-290B or starting over with a brand-new filing — and a brand-new cheque.

## What Counts as Invalid

The rule draws a surprisingly hard line. Copy-pasted signature images — the most common shortcut in high-volume corporate immigration filing — are flatly invalid, even when the underlying signature is genuinely the signatory's own. Rubber stamps, electronic signature tools like DocuSign and Adobe Sign, and reused scanned signature pages from prior filings all fail. The only path to a valid signature on a paper-filed or PDF-uploaded form is a fresh, wet-ink signature applied directly to the specific form being filed. That original can then be scanned for submission, but the scan must reproduce a real, contemporaneous signature — not a digital copy lifted from another document.

USCIS justified the crackdown with hard numbers. Denials for signature defects climbed from 300 in fiscal year 2021 to 2,953 in fiscal year 2025 — a nearly tenfold increase. The agency's Administrative Appeals Office has already processed 758 appeals tied to copied signatures. In one case cited in the rule, a consulting firm filed roughly 3,000 Form I-140 petitions using a single pasted signature image. In another, a signatory signed a blank sheet and instructed a subordinate to copy the signature onto at least 20 Form I-129 petitions.

## No Cure, No Grace Period

The rule's sharpest edge is what it omits: any mechanism to fix a signature after filing. USCIS considered and explicitly rejected allowing petitioners to substitute a corrected signature on a pending case. The agency's reasoning was blunt — permitting cures would let deficient filings hold cap slots and priority dates ahead of properly signed ones. For cap-subject H-1B petitions, where the filing window is finite and a lost receipt date means a lost cap slot, this is not a theoretical concern.

The rule applies to all benefit requests submitted on or after July 10, 2026. It was issued as an interim final rule, meaning the comment period — also closing July 10 — runs concurrently with the effective date. Comments will not delay enforcement.

## Why Indians Should Care

Indians account for more than 70 per cent of approved H-1B petitions annually. The volume of Indian-sponsored filings means that even a small percentage of signature defects translates into hundreds of denied cases. And the financial stakes are considerable. An H-1B filing with premium processing now costs upwards of $6,000 in government fees alone. A denial with no refund, followed by a refile with identical fees, doubles that cost overnight.

The operational burden falls hardest on mid-size IT services firms and staffing companies — categories where Indian-founded and Indian-led companies are disproportionately represented. These firms file dozens or hundreds of petitions per cap season. When signature workflows rely on pasted images or electronic tools, every petition in the batch is exposed.

For individual workers, the consequences are subtler but no less real. A denied I-140 petition means a lost priority date, potentially adding years to an already interminable green card queue. A denied H-1B extension can trigger a gap in status.

## What to Do Now

The compliance checklist is short: require a fresh wet-ink signature on every form, on the form itself, signed by the actual petitioner or an explicitly authorised signatory. Scan it. File the scan. Keep the original. Eliminate stamps, eliminate DocuSign on paper-filed forms, and stop reusing scanned signature pages across filings. Any firm that files more than a handful of petitions per year should audit its signature workflow before July 10 — because after that date, the first USCIS officer to notice a pasted image will not be sending a polite letter asking for clarification."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Your DocuSign Could Kill Your H-1B Petition. A New USCIS Rule Takes Effect July 10",
    "subheadline": "Starting next week, a pasted or electronically generated signature on an immigration form can result in an outright denial — no refund, no chance to fix it.",
    "slug": make_slug("uscis-signature-rule-july-10-docusign-h1b-denial"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians file over 70 per cent of H-1B petitions annually. High-volume filers using copy-paste or electronic signatures face mass denials — and lost priority dates in the already decades-long green card queue.",
    "tags": ["h1b", "uscis", "immigration", "signature-rule", "docusign", "i-140"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reddy Neumann Brown PC", "url": "https://www.rnlawgroup.com/new-uscis-signature-rule-takes-effect-july-10-2026-how-to-sign-immigration-forms-correctly-and-avoid-a-costly-denial/"},
        {"name": "Holland & Hart LLP", "url": "https://www.hollandhart.com/new-uscis-signature-rule-could-put-immigration-filings-at-risk"},
        {"name": "Ogletree Deakins (JDSupra)", "url": "https://www.jdsupra.com/legalnews/uscis-rule-raises-stakes-for-signature-3083285/"},
        {"name": "Federal Register (91 FR 25479)", "url": "https://www.federalregister.gov/documents/2026/05/11/2026-10587/signatures-on-immigration-benefit-requests"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7567551/pexels-photo-7567551.jpeg",
    "image_caption": "A hand holding a pen and signing a document — a ritual that USCIS now demands be done fresh for every immigration filing",
    "image_attribution": "Pexels",
    "body": art1_body
}

# -------------------------------------------------------------------
# ARTICLE 2: SCOTUS Immigration Power Week
# -------------------------------------------------------------------
art2_body = """In the space of seventy-two hours last week, the Supreme Court handed the Trump administration three immigration victories, each decided along the same 6–3 ideological line. Individually, the rulings address Temporary Protected Status, asylum access at the border, and the scope of judicial review. Taken together, they redraw the boundary between executive power and the courts in ways that should concern every Indian national navigating the American immigration system.

## What the Court Decided

The most consequential ruling came in *Mullin v. Doe*, where the court held that the administration can strip Temporary Protected Status from roughly 300,000 Haitian and 6,000 Syrian immigrants who had been living and working legally in the United States for years. The majority concluded that lower courts had overstepped by blocking the Department of Homeland Security's termination decision, and rejected claims that the move was racially motivated. The core legal holding: a statute barring judicial review of TPS determinations means exactly what it says. Courts cannot second-guess the secretary's decision.

On the same day, the court backed the government's authority to physically turn away asylum seekers at the U.S.-Mexico border when officials deem ports of entry overburdened — a practice known as "metering." And earlier in the week, in *Blanche v. Lau*, the court made it easier to deny entry to returning green card holders at the border.

"The Trump administration has turned the immigration system into a deportation machine," said Elora Mukherjee, director of the Immigrants' Rights Clinic at Columbia Law School. "In most cases, the Supreme Court has been a rubber stamp."

## The Precedent That Matters

TPS does not directly apply to Indians — there is no TPS designation for India, and the population affected is overwhelmingly Haitian and Syrian. But the legal principle the court endorsed reaches far beyond TPS. The majority held that when Congress bars judicial review of an executive immigration decision, courts must respect that bar even when plaintiffs raise constitutional claims. Justice Thomas, in concurrence, went further: aliens have no equal protection right against the federal government to a discretionary immigration privilege.

This reasoning has immediate implications for the cluster of legal challenges currently working through the federal courts on behalf of Indian visa holders. The $100,000 H-1B fee was struck down by a district judge in Boston just weeks ago, partly on the strength of the Supreme Court's earlier tariff ruling. But the TPS decision pushes in the opposite direction — it signals that when the executive invokes immigration authority, courts should be reluctant to interfere. The White House has already said it will appeal the fee ruling. The TPS precedent gives its lawyers a powerful new argument.

## The Cascade for Indians

Consider the policies now in play. The wage-weighted H-1B lottery, which replaced the random draw in February 2026, favours higher-paid petitions and has already reduced selection rates for Indian IT services firms. USCIS's directive that green card applicants must leave the country for consular processing — rather than adjusting status inside the United States — upends the plans of hundreds of thousands of Indians mid-queue. The signature rule taking effect July 10 gives USCIS unchecked discretion to deny petitions for trivial defects. Each of these policies rests on executive authority. Each is, or will be, challenged in court.

After last week, those challenges face steeper odds. The court's message, stated or implied across all three rulings, is that immigration policy belongs to the political branches. If Congress wrote the statute and the executive acted within it, judges should stay out.

For the roughly 1.2 million Indian nationals and their dependents stuck in the employment-based green card backlog, this is not an abstraction. The EAGLE Act — the legislative fix that would eliminate per-country caps — was blocked again last week when the House Armed Services Committee refused to include it in the National Defense Authorization Act. With Congress unwilling to act and the courts increasingly unwilling to check the executive, the institutional guardrails that once constrained immigration policy are thinning at both ends.

## What Comes Next

The administration has already asked the Supreme Court to let it detain immigrants arrested in enforcement sweeps without a chance to seek bond, even those who have lived in the country for years. Two of the three federal appeals courts that have reviewed the practice have endorsed it. Given the trajectory of the past week, a favourable ruling seems more likely than not.

For Indian H-1B holders, the practical advice has not changed: maintain status meticulously, avoid travel for visa stamping unless absolutely necessary, and assume that every executive policy currently in force will survive judicial review. The era when a district court injunction could pause a hostile immigration policy for months is, at minimum, contracting. The Supreme Court has made clear that "temporary" means temporary, "no judicial review" means no judicial review, and "discretion" belongs to the executive. The rest is arithmetic."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "The Supreme Court Handed Trump Three Immigration Wins in One Week. Indians Should Pay Attention",
    "subheadline": "The rulings concern Haitians, Syrians, and asylum seekers — but the legal precedent they set could make every challenge to H-1B and green card policies harder to win.",
    "slug": make_slug("scotus-three-immigration-wins-tps-metering-indian-implications"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The court's endorsement of unreviewable executive power on immigration weakens the legal foundation for challenges to the $100K H-1B fee, wage-weighted lottery, and consular processing mandates — all of which disproportionately affect Indians.",
    "tags": ["scotus", "immigration", "tps", "h1b", "green-card", "executive-power", "judicial-review"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/legal/us-supreme-court/immigration-supreme-court-accedes-trumps-restrictive-agenda-2026-06-27/"},
        {"name": "NBC Palm Springs", "url": "https://nbcpalmsprings.com/2026/07/01/supreme-court-rules-expand-trump-administration-immigration-powers/"},
        {"name": "New York Post", "url": "https://nypost.com/2026/06/26/us-news/supreme-court-rules-trump-can-remove-deportation-protection-from-haitians-syrians/"},
        {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/06/27/haitians-tps-dhs-supreme-court/77112456007/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Exterior_of_Supreme_Court_Building_20240601.jpg/1280px-Exterior_of_Supreme_Court_Building_20240601.jpg",
    "image_caption": "The United States Supreme Court building in Washington, D.C.",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body
}

# -------------------------------------------------------------------
# INSERT
# -------------------------------------------------------------------
articles = [art1, art2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
