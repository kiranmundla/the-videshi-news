#!/usr/bin/env python3
"""Immigration writer – July 4 2026, 1300 PT run."""

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
# ARTICLE 1: Indiana FAIRNESS Act + State Enforcement Wave
# ─────────────────────────────────────────────────────────────────────

art1_body = """Indiana's FAIRNESS Act went live on July 1. It is now the broadest state-level employer immigration enforcement law in the United States — covering every employer, every industry, with no minimum size threshold. And Indian business owners across the state are scrambling to comply.

Senate Enrolled Act 76, signed by Governor Mike Braun in March and branded with the reassuringly patriotic acronym FAIRNESS, does three things. It prohibits employers from knowingly recruiting, hiring, or continuing to employ unauthorised workers. It requires every state and local government body to comply with ICE detainer requests. And it bars Indiana's universities from restricting cooperation with federal immigration enforcement.

The penalties are not symbolic. The state attorney general can now investigate any employer suspected of hiring unauthorised workers and file civil enforcement actions. A first violation triggers a five-business-day suspension of the company's operating authorisation. A willful repeat violation can result in permanent revocation of all operating authorisations in the state — meaning the business shuts down entirely.

## The E-Verify safe harbour

There is exactly one shield: E-Verify. Employers who verify work eligibility through the Department of Homeland Security's electronic verification system, or a comparable programme, are protected. Attorney General Todd Rokita has said the law is not designed to punish "innocent mistakes" but to target knowing violations. His office plans to act on tips from ICE, the federal Department of Labour, and local law enforcement, as well as from workers themselves.

"We're going to quickly discern if you're just a competitor trying to gain a competitive advantage by tattling on your competition," Rokita told reporters at a June 30 press conference in Mishawaka.

## Part of a much larger trend

Indiana is not an outlier. It is the latest and broadest entrant in a growing wave of states that have built their own immigration enforcement infrastructure, layered on top of federal requirements.

Florida's Senate Bill 1718 has required E-Verify for private employers with 25 or more employees since 2023. Ohio's E-Verify Workforce Integrity Act took effect on March 19, 2026, targeting nonresidential construction contractors with fines up to $25,000 per violation. Alabama, Arizona, Georgia, Mississippi, North Carolina, South Carolina, Tennessee, and Utah already maintain some form of state-level employer mandate. Indiana's contribution is scale: no industry carve-outs, no size floor, and the attorney general gets shutdown authority.

"Indiana is the latest, but it won't be the last," said Jed Butler, CEO of I9 Intelligence, a compliance firm. "Every quarter, another state passes employer-facing penalties, and the common thread is always the same — E-Verify becomes the safe harbour."

## Why this matters to Indian Americans

Indianapolis and its suburbs — Carmel, Fishers, Noblesville — are home to one of the largest Indian American communities in the Midwest. Indians own gas stations, hotels, restaurants, IT staffing firms, and medical practices across the state. The Asian American Hotel Owners Association, whose membership is predominantly Indian American, represents a majority of hotel properties in Indiana.

For Indian-owned businesses that already run clean operations with legally authorised workers, E-Verify compliance should be straightforward. H-1B employees are fully authorised and will clear E-Verify without issue. But the compliance burden is real: every hire must now be verified, documentation must be airtight, and the consequences of a paperwork gap have escalated from a federal audit risk to a state-level shutdown threat.

The university provision carries its own weight. Purdue, Indiana University, and Notre Dame — all with substantial Indian student populations — are now explicitly prohibited from limiting cooperation with federal immigration enforcement. For international students already navigating the end of Duration of Status protections and tighter OPT scrutiny, the campus is no longer quite the buffer it once was.

## The bottom line

The federal government sets immigration policy. But enforcement is increasingly a state-by-state affair. For Indian Americans running businesses or studying in states with these laws, the practical reality is a compliance landscape that varies by zip code. The E-Verify safe harbour works — but only if you are standing inside it.

*Sources: Indiana Senate Enrolled Act 76; South Bend Tribune; Faegre Drinker Biddle & Reath analysis; The Indiana Lawyer; I9 Intelligence; Kahn, Dees, Donovan & Kahn LLP*"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Indiana Can Now Shut Down Your Business for Hiring Wrong. Ten States and Counting",
    "subheadline": "The FAIRNESS Act is the broadest state-level employer immigration enforcement law in America. Indian business owners in the Midwest are on notice.",
    "slug": make_slug("indiana-fairness-act-e-verify-state-enforcement-indian-business"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian Americans own a disproportionate share of Indiana's hotels, gas stations, and IT firms — all now subject to the country's broadest state-level employer immigration enforcement law with business shutdown penalties.",
    "tags": ["immigration", "e-verify", "indiana", "state-enforcement", "business-compliance"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "South Bend Tribune", "url": "https://www.southbendtribune.com/story/news/local/2026/07/01/attorney-general-rokita-vows-strict-enforcement-of-fairness-act/"},
        {"name": "Faegre Drinker Biddle & Reath", "url": "https://www.faegredrinker.com/en/insights/publications/2026/7/the-fairness-act-indianas-new-immigration-law-with-a-july-1-2026-deadline-for-employers"},
        {"name": "The Indiana Lawyer", "url": "https://www.theindianalawyer.com/articles/indiana-attorney-general-readies-new-immigration-biz-enforcement-powers"},
        {"name": "Kahn Dees Donovan & Kahn LLP", "url": "https://www.kddk.com/new-indiana-law-imposes-requirements-for-employers-concerning-employment-of-unauthorized-aliens/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Capitol_del_Estado_de_Indiana%2C_Indian%C3%A1polis%2C_Estados_Unidos%2C_2012-10-22%2C_DD_04.jpg/1280px-Capitol_del_Estado_de_Indiana%2C_Indian%C3%A1polis%2C_Estados_Unidos%2C_2012-10-22%2C_DD_04.jpg",
    "image_caption": "The Indiana State Capitol in Indianapolis, where Governor Mike Braun signed the FAIRNESS Act into law",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}


# ─────────────────────────────────────────────────────────────────────
# ARTICLE 2: Social Media Vetting / Online Presence Review
# ─────────────────────────────────────────────────────────────────────

art2_body = """Since December 15, 2025, every H-1B worker who walks into a US consulate for a visa stamp has had their Instagram scrolled, their LinkedIn inspected, and their X feed parsed by a consular officer with a checklist and a mandate. The State Department calls it the Online Presence Review. Six months in, its consequences are still reverberating through Indian consulates, American boardrooms, and the travel plans of roughly 300,000 Indian professionals.

The policy, announced on December 3, 2025, extended mandatory social media vetting from students and exchange visitors to all H-1B applicants and their H-4 dependents. Applicants are instructed to set all social media privacy settings to "public" to facilitate the review. The stated goal: to identify visa applicants who are "inadmissible to the United States, including those who pose a threat to U.S. national security or public safety."

The practical effect was immediate and brutal. Consulates in India — Chennai, Hyderabad, Mumbai, New Delhi — slashed their daily interview capacity to accommodate the additional vetting time. Appointments that had been confirmed for mid-December 2025 were unilaterally rescheduled to March, April, and in some cases June 2026. Applicants received emails telling them the consulate "will not be able to see you on your original appointment date."

## What officers actually look for

A May 2025 State Department cable, subsequently reported by multiple outlets, directed consular officers to vet social media primarily for "hostile attitudes" toward the United States. The review encompasses posts, comments, photos, affiliations, and other online content across platforms including Facebook, Instagram, LinkedIn, X, TikTok, and YouTube.

Inconsistencies between an applicant's online profile and their visa application — a different job title on LinkedIn, an employment gap that does not match the petition, or affiliations that raise security flags — can trigger a follow-up interview or an outright refusal. Yale University's Office of International Students and Scholars warned that "keeping portions of social media accounts private or the lack of an online or social media presence can lead to an adverse inference in some situations."

In other words: too much online presence is a risk. Too little is also a risk.

## The math of being stranded

The operational impact hits Indian H-1B workers hardest. Indians hold 283,772 of the 406,348 approved H-1B petitions — roughly 70 per cent. Any worker whose visa stamp has expired must visit a consulate abroad to renew it before re-entering the US. Under the old system, a routine trip to India for a visa stamp took two to three weeks. Under the new one, workers report being stranded for four to six months.

The professional consequences compound. Employers cannot legally allow most H-1B employees to work remotely from India due to payroll, tax, and export-control restrictions. A worker who travels for stamping and gets rescheduled faces a choice between months of unpaid absence and resigning. For H-4 spouses and children, the delays mean extended family separations.

Immigration attorney Amy Peck of Jackson Lewis noted that "for companies that rely on H-1B talent — especially in technology, social media and online content industries — this development could materially affect visa success rates, processing speeds and risk evaluations."

## The new calculus

Six months into the policy, the informal advice circulating through Indian professional networks is blunt: do not travel unless you absolutely must. If your visa stamp is valid, stay put. If it has expired but you are legally working in the US on an approved petition, avoid any international trip that would trigger a consular appointment.

For those who must travel, immigration lawyers recommend a preparation checklist that would have seemed absurd five years ago. Set all social media profiles to public at least several weeks before the appointment. Review every post, comment, and photo for anything that could be read as inconsistent with the visa application or critical of the United States. Ensure that LinkedIn accurately reflects current employment, title, and salary. Carry printed documentation of the employer's petition approval, the I-797, and the DS-160 confirmation.

The deeper concern — one that immigration attorneys raise privately but rarely in print — is that the policy introduces a layer of subjectivity into what was previously a largely documentary process. Whether a five-year-old tweet about American foreign policy constitutes a "hostile attitude" depends entirely on the officer reading it.

For Indian H-1B families, the calculation is now painfully simple. Every consulate visit is a gamble — not just on the outcome, but on the timeline. And the house always sets the odds.

*Sources: US Department of State; SHRM; Taft Law; Yale University OISS; Mondaq/Green & Spiegel; Reddy Neumann Brown PC; Jackson Lewis*"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Your Instagram Is Now Part of Your Visa Interview. Consular Officers Have Been Scrolling Since December",
    "subheadline": "The State Department's Online Presence Review has turned routine H-1B visa stamps into months-long ordeals. For Indian workers, there is no opting out.",
    "slug": make_slug("social-media-vetting-h1b-visa-stamp-online-presence-review"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians hold 70 per cent of all H-1B visas and are disproportionately affected by the State Department's mandatory social media screening at US consulates in India, which has turned routine visa renewals into months-long separations.",
    "tags": ["h1b", "visa-stamping", "social-media", "online-presence-review", "consulate"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "US Department of State", "url": "https://travel.state.gov/content/travel/en/News/visas-news/announcement-of-expanded-screening-and-vetting-for-h-1b-and-dependent-h-4-visa-applicants.html"},
        {"name": "SHRM", "url": "https://www.shrm.org/topics-tools/news/talent-acquisition/state-dept-adds-social-media-review-h-1b-h-4-visa-applicants"},
        {"name": "Taft Law", "url": "https://www.taftlaw.com/news-events/law-bulletins/dos-expands-mandatory-social-media-and-online-presence-review"},
        {"name": "Reddy Neumann Brown PC", "url": "https://www.rnlawgroup.com/stop-holiday-travel-for-stamping/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg",
    "image_caption": "An open passport displaying travel stamps at a consular appointment",
    "image_attribution": "Pexels",
    "body": art2_body,
}


# ─────────────────────────────────────────────────────────────────────
# Insert
# ─────────────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
