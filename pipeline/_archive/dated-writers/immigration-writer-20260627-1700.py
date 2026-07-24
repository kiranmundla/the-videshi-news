#!/usr/bin/env python3
"""Immigration news writer — 2026-06-27 17:00 run."""
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


# ── ARTICLE 1: Doddamani Asylum Fraud Case ──────────────────────────

article1_body = """Vinod Doddamani speaks ten languages and holds four degrees. His website calls him "internationally raised" — born in India, raised in Germany, educated at Purdue and Chapman University law school. For years, the California-based immigration attorney built a practice filing asylum applications on behalf of Indian nationals in immigration courts across the country.

The Department of Homeland Security says those applications were fraudulent.

This week, Homeland Security Investigations filed five notices of intent to fine Doddamani more than $255,000 for allegedly submitting 64 fraudulent documents across 32 immigration cases. According to DHS, the asylum applications were "identical or nearly identical in language and substance," containing the same factual narrative about alleged persecution — a cut-and-paste operation applied to dozens of Indian clients with presumably different stories.

It is the first time in American history that DHS has sought financial penalties against an attorney for filing fraudulent asylum claims.

## A new weapon, deployed on Indian cases

The fine is the debut of an enforcement tool that DHS General Counsel James Percival authorised in May, when he issued a directive instructing ICE attorneys to pursue practitioners who file false asylum applications. Before that directive, DHS had no administrative mechanism to fine immigration lawyers for fraud — it could refer cases for criminal prosecution, but the faster civil-penalty path did not exist.

"Last month, we put the open borders industrial complex on notice — fraudulent asylum claims would result in fines against attorneys," Percival posted on X. "Today we fined an attorney over $255k for filing multiple fraudulent claims on behalf of Indian nationals."

ICE was even blunter. "The days of attorneys abusing and defrauding our immigration system are OVER," the agency wrote. "Our message to immigration attorneys is clear: if you engage in fraud, you will be held ACCOUNTABLE."

The emphasis was not subtle. Nor was the choice of test case.

## Why it matters for the Indian diaspora

Indian nationals represent a growing share of asylum claims filed in U.S. immigration courts — a trend driven by religious minorities, political activists, and LGBTQ individuals citing persecution. But the Doddamani case lands at a moment when every immigration pathway available to Indians is under simultaneous pressure: H-1B fees, green card backlogs, consulate appointment droughts, and now, heightened scrutiny of asylum claims.

The risk is not that fraudulent attorneys are being punished — few would argue that copy-paste persecution narratives serve genuine asylum seekers. The risk is in the spillover. Immigration attorneys who represent Indian clients now face six-figure fines if DHS determines their filings are "identical" in substance, a standard whose boundaries remain unclear. A boilerplate format describing real persecution in a particular Indian state could look suspiciously similar across multiple clients who genuinely fled the same conditions.

"Fraudulent asylum claims threaten the safety of Americans by overwhelming our burdened immigration system and delaying the removal of dangerous criminal aliens," Percival said. The framing treats fraud as a throughput problem, not a justice problem, and the consequences may land on legitimate applicants caught in a system primed to flag patterns.

## A pattern of Indian-linked fraud cases

Doddamani is not alone. In a separate case this month, ten Indian nationals were indicted in Boston for a U-visa conspiracy in which staged armed robberies were used to generate crime-victim visa applications. Two more Indian nationals pleaded guilty to H-1B fraud in Sacramento for fabricating job positions to inflate their companies' visa petitions.

The clustering of Indian-linked fraud cases gives enforcement agencies a ready-made narrative — and gives critics of the asylum and visa systems ammunition. For the millions of Indian professionals and families navigating the system honestly, each headline lands as a collective reputational hit, adding scrutiny to an already exhausting process.

## What happens next

Doddamani has not been criminally charged; the $255,000 is a civil fine. He has not publicly commented on the allegations. If DHS's new attorney-fine directive survives legal challenges and delivers results in this case, expect it to be used more broadly — and Indian-focused practices, which handle a disproportionate share of asylum filings, will remain in the enforcement crosshairs.

The message from Washington is clear enough. The question for the diaspora is whether the tool will be wielded with surgical precision or a broad brush."""


# ── ARTICLE 2: Indian Doctors / Healthcare Pipeline ──────────────────

article2_body = """When a rural hospital in southwest Missouri needs a cardiologist, it does not recruit from Stanford or Johns Hopkins. It recruits from India.

Citizens Memorial Health Care serves 130,000 residents across eight counties. Its 86-bed hospital employs seven physicians who came through the J-1 visa waiver programme, including interventional cardiologists from India and Pakistan. This is not unusual. Across the United States, approximately 25 per cent of practising physicians are International Medical Graduates — and Indian-trained doctors form one of the largest cohorts within that group.

When President Trump imposed a $100,000 fee on every new H-1B visa application last September, the hospital froze its international recruitment pipeline. So did dozens of others.

On June 8, a federal judge struck the fee down.

## The ruling — and the relief

U.S. District Judge Leo Sorokin ruled that the $100,000 fee amounted to an unauthorised tax and exceeded the government's statutory authority. The American Association of Physicians of Indian Origin (AAPI) called the decision "a healthcare victory, not a political victory."

"This ruling restores fairness and stability to a system that thousands of international physicians depend upon," said AAPI President Dr. Amit Chakrabarty. "Patients are not placed at risk due to policy barriers unrelated to clinical need."

The numbers behind the relief are stark. According to AAPI, IMGs make up roughly 40 per cent of physicians in rural and underserved areas. More than half of internal medicine trainees are IMGs. They are concentrated in specialties where shortages bite hardest — geriatrics, nephrology, endocrinology, infectious disease. In some rural counties, they account for one in three or even one in two practising doctors.

The American Medical Association and 53 medical societies had urged DHS to exempt physicians, warning that the U.S. faces a projected shortage of up to 86,000 doctors by 2036. Under the proposed fee, sponsoring a single physician would have cost a rural hospital $100,000 before the new hire saw a single patient — a price that safety-net institutions simply could not absorb.

## The relief is temporary

Judge Sorokin's ruling did not permanently settle the matter. On June 12, he issued an administrative stay of his own decision, keeping existing regulations in place while the federal government appeals to the First Circuit. DHS has argued the fee falls within its authority. USCIS continues to issue Requests for Evidence tied to H-1B filings, maintaining enforcement posture despite the ongoing litigation.

The practical effect: hospitals cannot plan with certainty. Some are resuming recruitment cautiously; others are waiting for the appeals court. For healthcare employers the stakes are measured in patient outcomes, not quarterly earnings.

"Many hospitals would have struggled to absorb such a financial burden," Dr. Chakrabarty said. "The consequences would have been immediate — fewer physicians, longer wait times, and reduced access to care for communities that already face healthcare disparities."

## More than one front

The fee fight is only one of several policy pressures squeezing the physician pipeline. USCIS's May 22 memo reclassifying Adjustment of Status as an "extraordinary form of relief" means that physicians on temporary visas — including those on J-1 waivers transitioning to H-1B status — may now need to return to India to complete green card processing, pulling working doctors out of U.S. hospitals for months.

The visa bulletin offers no comfort either. EB-2 India is unavailable for the remainder of the fiscal year. EB-1, once the fast lane for physicians with extraordinary credentials, has retrogressed. Indian-born doctors who entered the system a decade ago remain years from permanent residency.

And a proposed bill, HR-9157, would eliminate OPT entirely and auction H-1B visas by salary — a framework that could disadvantage residency-track physicians earning modest training stipends compared to tech workers commanding six-figure packages.

## The pipeline that built American healthcare

Indian doctors have been filling gaps in American healthcare since the 1970s, when severe shortages drew an earlier generation of cardiologists and internists to hospitals across the Midwest. The pipeline runs from medical colleges in Maharashtra and Tamil Nadu through residency programmes in places like Marshfield, Wisconsin, and Lubbock, Texas, and into community hospitals that serve populations no one else will.

The court ruling kept that pipeline flowing. But the feed lines are narrowing from multiple directions, and the next policy shift may not have a judge standing in its way."""


articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "An Indian-Origin Attorney Filed 64 Identical Asylum Claims. DHS Just Made Him the First Lawyer to Pay for It",
        "subheadline": "The $255,000 fine against Vinod Doddamani is ICE's debut use of a new fraud enforcement weapon — and it was field-tested almost entirely on Indian cases.",
        "slug": make_slug("dhs-fines-indian-attorney-doddamani-255k-asylum-fraud-ice-first"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals were at the centre of the first-ever use of DHS's new attorney-fine directive — raising questions about heightened scrutiny of Indian asylum claims and the quality of legal representation available to diaspora members seeking protection.",
        "tags": ["asylum", "fraud", "ICE", "DHS", "immigration", "Indian nationals", "enforcement"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Fox News", "url": "https://www.foxnews.com/politics/ice-opens-new-front-war-fraud-new-first-kind-policy-notice"},
            {"name": "News Dive / Indian Express", "url": "https://newsdive.net/2026/06/25/meet-vinod-doddamani-the-indian-american-attorney-under-scrutiny-with-a-250-000-penalty-for-asylum-fraud-in-the-u-s/"},
            {"name": "NewsPoint / Times of India", "url": "https://www.newspointapp.com/english/world/who-is-vinod-doddamani-indian-origin-immigration-attorney-in-us-faces-250000-fine-over-fraud-claims-involving-indian-nationals-toi/articleshow/14504820b381227f5d18f4c6b79892d83871d33f"},
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36984942/pexels-photo-36984942.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "Exterior of the U.S. Immigration and Customs Enforcement building in Washington, D.C.",
        "image_attribution": "Pexels",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "One in Four American Doctors Is Foreign-Trained. The $100K Fee Nearly Broke That Pipeline",
        "subheadline": "Indian physicians power rural hospitals and underserved clinics from Missouri to Mississippi. A court ruling saved the H-1B healthcare pipeline — but the threats keep multiplying.",
        "slug": make_slug("indian-doctors-100k-h1b-fee-rural-healthcare-aapi-img-pipeline"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian-origin physicians make up a large share of International Medical Graduates staffing rural and underserved hospitals across the U.S. — the $100K fee would have crippled their recruitment, and broader policy shifts still threaten the pipeline that has shaped American healthcare for half a century.",
        "tags": ["H-1B", "healthcare", "Indian doctors", "IMG", "AAPI", "physician shortage", "rural hospitals"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/17/aapi-applauds-court-ruling-blocking-100000-h-1b-physician-visa-requirement/"},
            {"name": "Reuters", "url": "https://www.reuters.com/business/healthcare-pharmaceuticals/american-medical-association-urges-dhs-exempt-physicians-new-100000-h-1b-visa-fee-2025-09-25/"},
            {"name": "STAT News", "url": "https://www.statnews.com/2025/09/25/h-1b-visa-changes-doctors-workforce-innovation/"},
            {"name": "Medscape", "url": "https://www.medscape.com/viewarticle/5-things-doctors-should-know-about-h-1b-visa-changes-2025a1000jik"},
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7578797/pexels-photo-7578797.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "A physician reviews patient records during a consultation at a medical office",
        "image_attribution": "Pexels",
        "body": article2_body
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
