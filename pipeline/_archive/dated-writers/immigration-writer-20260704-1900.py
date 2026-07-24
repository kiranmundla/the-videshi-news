#!/usr/bin/env python3
"""Immigration writer — July 4, 2026 evening run."""

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
    # ──────────────────────────────────────────────────────────────
    # ARTICLE 1: DOJ Denaturalization Push
    # ──────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Sixty-Nine Denaturalisations and Counting. Your US Citizenship May Not Be Permanent",
        "subheadline": "The Justice Department has filed more cases to strip naturalised Americans of their citizenship this year than in any single year of the first Trump term — and the pace is accelerating.",
        "slug": make_slug("doj-denaturalization-surge-69-cases-indian-americans"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "With 2.7 million Indian-born Americans having naturalised, the expanding denaturalisation programme creates a new layer of uncertainty — even for those who believed the process was finished.",
        "tags": ["denaturalization", "citizenship", "doj", "uscis", "indian-americans", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/us-law-week/trump-doj-faces-legal-resource-hurdles-in-denaturalization-push"},
            {"name": "Democracy Forward", "url": "https://democracyforward.org/"},
            {"name": "Center for Immigration Studies", "url": "https://cis.org/"},
            {"name": "National Partnership for New Americans", "url": "https://partnershipfornewamericans.org/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/USCIS_July_4th_Naturalization_Ceremony_%2819227250219%29.jpg/1280px-USCIS_July_4th_Naturalization_Ceremony_%2819227250219%29.jpg",
        "image_caption": "A Fourth of July naturalization ceremony at a USCIS facility in the United States",
        "image_attribution": "Wikimedia Commons",
        "body": """As America marked its 250th birthday on Friday, the Department of Justice was busy with a different kind of citizenship project. Not granting it — revoking it.

The DOJ has filed 69 civil denaturalisation cases since the start of President Trump's second term, according to an analysis by the legal advocacy group Democracy Forward. Thirty-three of those were filed in June alone, more than tripling the pace of earlier months and far outstripping the 11-case annual average maintained between 1990 and 2017.

The administration calls it restoring integrity. Immigration attorneys call it unprecedented. For the roughly 2.7 million Indian-born Americans who have naturalised over the decades, it introduces a question many assumed was settled the day they took the oath: can this be taken away?

## What the Law Actually Says

Under Section 340 of the Immigration and Nationality Act, a naturalised citizen can be stripped of citizenship for "concealment" or "willful misrepresentation" of a "material fact" that would have prevented naturalisation in the first place. There is no statute of limitations. A person who became a citizen in 1978 is as legally vulnerable as someone who naturalised last year.

Most cases filed so far involve individuals who committed crimes before naturalisation and were later convicted — fraud, money laundering, violent offences. But immigration rights advocates note that the scope appears to be widening. Some recent cases involve allegations of financial fraud and money laundering that were never flagged during the original naturalisation review.

"The government is most likely to focus on the low-hanging fruit — people who have big convictions, recent convictions that they can find easily," said Nancy Canter, a former DOJ and USCIS counsel. "But the broader discretion being exercised is new."

## The Indian American Exposure

India is one of the largest sources of naturalised US citizens. The Indian American community has grown to over 4.8 million, with a substantial majority having gone through the full immigration pipeline — F-1 to H-1B to green card to citizenship. That pipeline generates mountains of paperwork across decades, and every form is a potential point of scrutiny under denaturalisation review.

The risk is not theoretical. Consider a common scenario: an Indian professional who adjusted status from H-1B to green card using employer-sponsored PERM labour certification, later changed jobs, and eventually naturalised. If any element of the original PERM application is retroactively deemed inaccurate — a job description that evolved, a wage level that shifted — it could in theory be used as grounds for revocation.

Ramya Reddy, director of policy at the National Partnership for New Americans, said the administration is "using broader discretion over who can be denaturalised" than any recent predecessor. At least nine cases have already resulted in denaturalisation rulings.

## Legal Hurdles Remain

Former government lawyers caution that the push faces real constraints. The DOJ's Civil Division has lost staff through attrition and buyouts, and denaturalisation cases require significant investigative resources. Each case demands proof of deliberate misrepresentation — a high legal bar.

"It's going to be very difficult to meet those goals, especially if the government only wants to bring strong cases, which require a lot of work," said George Fishman, senior legal fellow at the Center for Immigration Studies.

Federal courts have also pushed back. The Supreme Court's 1943 ruling in *Schneiderman v. United States* held that the government bears the burden of proof in denaturalisation by "clear, unequivocal, and convincing" evidence — a standard just below criminal prosecution. Several recent cases have been contested on similar grounds.

## What This Means for the Diaspora

For Indian Americans who have already naturalised, the practical advice from immigration attorneys is straightforward: keep every document. Naturalisation certificates, N-400 applications, tax returns from the year of filing, employment records, travel histories — all of it. The government's ability to revisit a case from 20 or 30 years ago means the paper trail matters indefinitely.

For those still in the pipeline — on H-1B or with a pending I-485 — the denaturalisation expansion adds another variable to an already volatile calculus. Citizenship was supposed to be the finish line. It may now be a checkpoint.

The DOJ has not indicated whether it plans to further accelerate filings. But with 33 cases in June alone, the trajectory is clear. America may be celebrating 250 years of independence, but for some of its newest citizens, the permanence of belonging has never felt less certain."""
    },
    # ──────────────────────────────────────────────────────────────
    # ARTICLE 2: Healthcare Workforce Resilience Act
    # ──────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Forty Thousand Green Cards for Doctors and Nurses. The Bill That Could Actually Pass",
        "subheadline": "The Healthcare Workforce Resilience Act would recapture unused employment-based visas, reserve them for physicians and nurses, and exempt them from per-country caps — a rare bipartisan lifeline for Indian medical professionals stuck in the backlog.",
        "slug": make_slug("healthcare-workforce-resilience-act-40000-green-cards-nurses"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian physicians make up 22 per cent of all immigrant doctors in the US — 59,000 people — and Indian nurses number 32,000. This bill is designed for them, even if it never says so explicitly.",
        "tags": ["green-card", "healthcare", "nurses", "physicians", "immigration", "per-country-cap", "recapture"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Congress.gov", "url": "https://www.congress.gov/bill/119th-congress/house-bill/5283/text"},
            {"name": "AONL", "url": "https://www.aonl.org/resources/nursing-leadership-news/bill-would-bolster-numbers-foreign-nurses-physicians"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/17/aapi-applauds-court-ruling-blocking-100000-h-1b-physician-visa-requirement/"},
            {"name": "Remitly / Indian Eye", "url": "https://theindianeye.com/2023/05/01/every-5th-immigrant-doctor-in-us-is-an-indian/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5327579/pexels-photo-5327579.jpeg",
        "image_caption": "A physician holding a stethoscope at a medical facility in the United States",
        "image_attribution": "Pexels",
        "body": """There are 59,000 Indian-born doctors practising medicine in the United States. That is one in five of every immigrant physician in the country — more than China, Pakistan and the Philippines combined. Add 32,000 Indian-born registered nurses, and the picture is clear: India does not just contribute to American healthcare. In large parts of rural and underserved America, India *is* the healthcare system.

Yet the immigration pipeline that delivers these professionals is the same one that makes an Indian EB-2 applicant wait over a decade for a green card. The same system where EB-2 India just went "Unavailable" through September 30, 2026, and where EB-5 unreserved for India has been shut as well.

Now a bipartisan bill in Congress is proposing something simple, targeted, and — by Washington standards — almost elegant. The Healthcare Workforce Resilience Act (H.R. 5283 in the House, S. 2759 in the Senate) would recapture unused employment-based green cards from fiscal years 1992 through 2024 and reserve up to 40,000 of them specifically for healthcare workers: 25,000 for professional nurses and 15,000 for physicians.

The visas would be exempt from per-country caps. They would be issued in order of priority date. And they would come from green cards that Congress already authorised but that were never used due to bureaucratic processing delays.

## Why This Bill Matters More Than the Others

Congress has seen no shortage of green card reform proposals. The EAGLE Act, which would eliminate per-country caps entirely for employment-based categories, has been introduced — and has failed — in every recent session. The latest attempt died when it was dropped from the NDAA earlier this year.

The Healthcare Workforce Resilience Act is different in two critical ways. First, it is narrow. It does not attempt to restructure the entire employment-based immigration system. It targets a specific, well-documented labour shortage — the United States needs an estimated 124,000 more physicians by 2034, according to the Association of American Medical Colleges — and offers a specific remedy.

Second, it is bipartisan. Senators Dick Durbin (D-IL) and Kevin Cramer (R-ND) co-sponsor the Senate version. Representatives Brad Schneider (D-IL) and Don Bacon (R-NE) introduced it in the House. In a Congress where immigration votes are tribal, healthcare labour shortages cross party lines. Rural Republican districts depend on International Medical Graduates as much as urban Democratic ones.

## The Numbers Behind the Shortage

International Medical Graduates make up roughly 25 per cent of the US physician workforce. They provide care to nearly one in six patients nationwide. About 40 per cent of physicians in rural and underserved areas are IMGs. More than half of internal medicine trainees are IMGs.

Within this cohort, Indian-trained physicians dominate. According to a Remitly analysis, India produces more immigrant doctors in the US than any other country — 59,000, constituting 22 per cent of all immigrant physicians. China and Hong Kong account for 16,000, Pakistan for 13,000.

The story is similar in nursing. Of the 540,000 immigrant registered nurses in the US, 32,000 are Indian-born — the second-largest group after the Philippines.

These professionals are concentrated in exactly the specialties where shortages are most acute: internal medicine, geriatrics, nephrology, endocrinology, infectious disease. They work disproportionately in safety-net hospitals, federally qualified health centres, and Veterans Affairs facilities.

## What Happens Without It

The American Association of Physicians of Indian Origin (AAPI) has been vocal about the stakes. When a federal judge recently blocked the proposed $100,000 supplemental H-1B fee — which would have hit physician visa applications — AAPI President Dr. Amit Chakrabarty called the ruling "a healthcare victory, not a political one."

"Many hospitals would have struggled to absorb such a financial burden," Dr. Chakrabarty said. "The consequences would have been immediate — fewer physicians, longer wait times, and reduced access to care for communities that already face healthcare disparities."

Without targeted relief, the math is bleak. EB-2 India is closed for the rest of the fiscal year. EB-3 India's final action date sits at January 2014 — meaning anyone who filed after that is waiting in a queue that moves in months, not years. The National Interest Waiver route, which some physicians have used to self-petition, is seeing falling approval rates as USCIS tightens scrutiny.

## The Political Calculus

The bill's bipartisan backing reflects a cold political reality: healthcare worker shortages affect red and blue districts alike. A hospital in rural Nebraska that loses its only nephrologist to visa delays does not care about per-country caps or the H-1B wage lottery. It cares about keeping its doors open.

That gives the Healthcare Workforce Resilience Act something most immigration bills lack — a constituency that includes the people who vote against immigration reform. Whether that translates into floor votes in a Congress consumed by enforcement politics remains the open question.

The bill has been introduced in three consecutive Congresses. It has never received a floor vote. But with the physician shortage worsening, EB-2 India frozen, and the nursing pipeline under strain, the argument for doing nothing gets harder to make every year.

For the 59,000 Indian doctors and 32,000 Indian nurses building careers and communities across America, 40,000 green cards would not solve everything. But it would be a start — and in the current immigration landscape, a start is more than most bills offer."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
