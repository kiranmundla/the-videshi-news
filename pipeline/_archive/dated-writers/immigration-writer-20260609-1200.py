#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-06-09 12:00 UTC run"""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
for env_file in [Path.home() / ".env.supabase", Path.home() / "workspace/.env.pexels"]:
    if env_file.exists():
        for line in env_file.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

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

def upload_image_to_supabase(img_url, filename):
    """Download image, compress, upload to Supabase storage."""
    try:
        from PIL import Image
    except ImportError:
        # If PIL not available, just return the original URL
        return img_url

    try:
        r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        r.raise_for_status()
        img_bytes = r.content

        if len(img_bytes) < 5000:
            print(f"  ⚠ Image too small ({len(img_bytes)} bytes), skipping compression")
            return img_url

        img = Image.open(io.BytesIO(img_bytes))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > 1200:
            ratio = 1200 / img.width
            img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80, optimize=True)
        compressed = buf.getvalue()

        upload_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        }
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        ur = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
        if ur.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✅ Uploaded {filename} ({len(compressed)} bytes)")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({ur.status_code}): {ur.text[:200]}")
            return img_url
    except Exception as e:
        print(f"  ⚠ Image processing error: {e}")
        return img_url

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")


# ──────────────────────────────────────────────
# Image sourcing
# ──────────────────────────────────────────────

print("=== Sourcing images ===")

# Article 1: H-1B consultancy fraud — passport with visa stamps from Pexels
img1_url = "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&w=1200"
art1_slug = make_slug("seven-lakhs-denial-letter-h1b-consultancy-racket-india-lottery")
img1_final = upload_image_to_supabase(img1_url, f"{art1_slug}.jpg")

# Article 2: Student visa Duration of Status rule — US Capitol from Wikimedia Commons
img2_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Capitol_at_Dusk_2.jpg/1280px-Capitol_at_Dusk_2.jpg"
art2_slug = make_slug("thirty-days-get-out-dhs-rule-indian-students-grace-period")
img2_final = upload_image_to_supabase(img2_url, f"{art2_slug}.jpg")


# ──────────────────────────────────────────────
# Articles
# ──────────────────────────────────────────────

articles = [
    # ── ARTICLE 1: H-1B consultancy fraud ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Seven Lakhs and a Denial Letter — The Consultancy Racket Preying on India's H-1B Lottery Losers",
        "subheadline": "An Indian software engineer paid ₹7 lakhs to a third-party agency after five consecutive lottery failures. USCIS denied the petition anyway — and the story is far from unique.",
        "slug": art1_slug,
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Thousands of Indian IT professionals turn to consultancies every year after failing the H-1B lottery, spending lakhs on middlemen who often cut corners on USCIS filings. This story is a cautionary tale for anyone considering the consultancy route.",
        "tags": ["h1b", "uscis", "immigration", "fraud", "consultancy", "visa-lottery"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/how-a-broken-h-1b-visa-lottery-scheme-and-strict-us-immigration-policy-ruined-an-it-workers-american-dream/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/us/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-09/"},
            {"name": "USCIS", "url": "https://www.uscis.gov/working-in-the-united-states/h-1b-specialty-occupations"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img1_final,
        "image_caption": "An open passport displaying visa stamps at an airport immigration counter",
        "image_attribution": "Pexels",
        "body": """Five consecutive H-1B lottery failures is enough to break anyone's patience. For one Indian software engineer, it was enough to break his savings, too.

The worker — whose account, shared on Reddit, has since been picked up by multiple outlets — paid roughly ₹7 lakhs (about $8,400) to a third-party staffing consultancy that promised to sponsor his H-1B petition. After years of losing the annual lottery while employed at legitimate companies, he took what felt like the only remaining option.

It worked — at first. His application cleared the lottery. Then USCIS took a closer look.

## The filing that fell apart

The denial notice, when it arrived, cited multiple violations: fraudulent fee underpayments by the sponsoring employer, non-compliance with wage requirements, and filing errors that pointed to an agency cutting every corner available. The consultancy had submitted the paperwork; the worker had no way of knowing what was inside it.

"I trusted them because they said they had a 90% success rate," the engineer wrote in his Reddit post, which drew thousands of responses from Indians in similar situations. "I didn't realise until the denial that I had no control over what they filed."

This is the part of the H-1B system that rarely makes headlines. The annual lottery — with its roughly 25% selection rate for the 65,000 regular-cap visas and 20,000 master's-cap slots — creates a class of desperate applicants. And where there is desperation, there is an industry built to exploit it.

## The shadow pipeline

Immigration attorneys have long warned about what they call "body shops" — staffing firms that file H-1B petitions on behalf of workers they barely employ, charging fees that can run from $5,000 to $15,000 or more. Some operate legitimate businesses. Many do not.

The pattern is remarkably consistent. A worker fails the lottery multiple times. A friend or online forum recommends a consultancy. The consultancy charges an upfront fee — sometimes disguised as a "training" or "placement" cost — and files the H-1B petition under its own employer identification number. If the petition is selected in the lottery, the consultancy scrambles to find an end client where the worker can actually be placed.

The problem is what happens between the filing and the placement. USCIS has tightened its scrutiny of employer-employee relationships in recent years, and petitions from staffing agencies with thin client lists and questionable wage attestations are flagged at higher rates. A 2025 USCIS policy memo expanded site visits to include virtual inspections, making it harder for paper-only employers to evade detection.

## The numbers tell a story

Indians account for nearly three-quarters of all H-1B approvals, according to USCIS data. That concentration makes the Indian applicant pool disproportionately vulnerable to consultancy fraud. Immigration lawyer Cyrus Mehta has estimated that fraudulent or semi-fraudulent petitions may account for 10-15% of all H-1B filings in a given year, though exact figures are impossible to verify.

The financial toll extends beyond the filing fees. Workers who pay a consultancy and then receive a denial lose not just the money but often their legal status — particularly if they were on OPT or had gaps between visa categories. Some face voluntary departure deadlines. Others simply go underground.

## What the diaspora should know

The Reddit post that started this particular fire drew responses from dozens of Indian tech workers who had been through similar experiences. Several shared screenshots of consultancy contracts that included clauses binding the worker to "repay training costs" if they left the firm within two years — a practice that multiple federal lawsuits have challenged as a form of indentured servitude.

For anyone considering the consultancy route after repeated lottery failures, immigration attorneys recommend several precautions: verify the employer's USCIS filing history through the publicly available H-1B employer data hub, ask for copies of the Labor Condition Application before it is filed, and never sign a contract that requires repayment of H-1B filing fees — which, under federal law, must be borne by the employer.

The H-1B system is broken in ways that Congress has been unwilling to fix. Monday's federal court ruling striking down the Trump administration's $100,000 fee on new H-1B petitions may bring some relief to legitimate applicants, but it does nothing to address the shadow industry that thrives on the lottery's structural desperation.

For the engineer who lost ₹7 lakhs, the lesson was expensive and irreversible. "The system didn't fail me," he wrote in a follow-up post. "The people I paid to navigate it did."

--IANS"""
    },

    # ── ARTICLE 2: DHS Duration of Status rule for students ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Thirty Days to Get Out — The Rule That Would Cut Indian Students' Safety Net in Half",
        "subheadline": "A DHS proposal to end 'Duration of Status' for F-1 visa holders would impose a four-year cap and slash the post-graduation grace period from sixty days to thirty. Immigration experts say the impact on Indian students will be severe.",
        "slug": art2_slug,
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian students form one of the largest international student groups in the US and are disproportionately represented in the H-1B lottery. Cutting the F-1 grace period in half leaves less time to secure alternative visa options after graduation — a change that could push thousands of Indian STEM graduates out of the country.",
        "tags": ["f1-visa", "student-visa", "duration-of-status", "dhs", "immigration", "opt", "indian-students"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye (IANS)", "url": "https://theindianeye.com/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
            {"name": "Federal Register (DHS Proposed Rule)", "url": "https://www.federalregister.gov/d/2025-16554"},
            {"name": "NAFSA", "url": "https://www.nafsa.org/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img2_final,
        "image_caption": "The United States Capitol building at dusk in Washington, D.C.",
        "image_attribution": "Wikimedia Commons",
        "body": """For decades, international students in the United States have entered on F-1 visas stamped with two letters: D/S. Duration of Status. It meant that as long as you were enrolled in your programme and playing by the rules, you could stay. No fixed expiry date. No countdown clock.

The Department of Homeland Security wants to change that — and the consequences for Indian students could be enormous.

## The rule on the table

Under a proposed rule published in the Federal Register, DHS would eliminate Duration of Status for F-1 and J-1 visa holders entirely. In its place: a fixed period of admission tied to the programme end date listed on Form I-20, with a hard cap of four years. Students whose programmes run longer — doctoral candidates, for instance — would need to file Form I-539 extensions with USCIS, complete with biometrics, proof of continued eligibility, and filing fees.

The grace period after programme completion would be cut from sixty days to thirty.

That thirty-day window is not just a bureaucratic detail. It is the period in which graduating students must either leave the country, change their visa status, or secure employment authorisation through Optional Practical Training (OPT). For Indian students — who form one of the largest international student cohorts in the US and account for a significant share of H-1B lottery applicants — losing half that runway is a material reduction in options.

## What thirty days actually means

Immigration attorney Goldman, who has represented hundreds of Indian STEM professionals, described the proposed change in blunt terms during a recent analysis: "For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working.'"

The reference is to Day-1 Curricular Practical Training (CPT), an increasingly popular workaround in which H-1B lottery losers enrol in a second master's programme — often at schools that explicitly market this arrangement — in order to maintain work authorisation while continuing to enter the lottery each year. DHS has signalled that it views this practice as an abuse of the student visa system, and the proposed rule would make it significantly harder to pull off.

Under the new framework, students who enrol in a second programme would need to apply for a fresh period of admission. USCIS would evaluate whether the new programme represents a genuine academic pursuit rather than a vehicle for continued employment. The four-year cap means that a student who completes a two-year master's degree has only two years of additional admission available before needing to leave the country or obtain a different visa.

## The numbers

Indian students accounted for over 330,000 active SEVIS records in the 2024-25 academic year, second only to China. Among STEM fields — where OPT extensions allow up to three years of post-graduation work authorisation — Indian nationals are overwhelmingly represented. Many of these students plan their entire immigration trajectory around the assumption that they will have time to transition from F-1 to H-1B to green card.

The proposed rule disrupts that trajectory at its earliest stage.

Goldman warned that the impact extends beyond students to the companies that employ them. "There's no doubt about it that this is going to have a massive impact on the companies that are in desperate need of top talent," she said. Foreign nationals make up a substantial portion of the US AI talent pool, and companies could struggle to recruit and retain skilled workers if existing pathways become more restrictive.

## A multi-front squeeze

The DHS rule does not exist in isolation. Representative Chip Roy's American White-Collar Worker Jobs Act of 2026, introduced last week, would eliminate OPT entirely and shorten the H-1B visa from six years to two. If both the DHS rule and the Roy bill were to take effect, the pipeline that has fed Indian talent into American technology companies for a generation would be squeezed from both ends: fewer years to study, less time to find employment after graduation, and a shorter H-1B window with no path to permanent residency.

NAFSA, the association of international educators, has pushed back forcefully. In its public comments on the proposed rule, the organisation argued that DHS should increase the J-1 and M-1 grace periods to sixty days rather than cutting the F-1 period to thirty — achieving the "parity" DHS claims to want without reducing protections.

The public comment period on the main rule closed in September 2025. DHS has not yet issued a final rule, but the current administration's broader posture on immigration enforcement suggests that the proposal is unlikely to be softened.

## What Indian families should do

For students currently in the US on F-1 visas, the proposed rule has not yet taken effect. But the direction of travel is clear enough to warrant planning. Immigration attorneys recommend maintaining meticulous compliance with programme requirements, filing OPT applications as early as the filing window allows, and exploring O-1 visas for students with strong publication or research records.

Companies that rely on the F-1-to-H-1B pipeline should consider cap-exempt H-1B sponsorship through universities or research institutions, where the annual lottery does not apply.

The thirty days, if they come, will arrive quickly. The time to prepare is now."""
    },
]


# ──────────────────────────────────────────────
# Insert articles
# ──────────────────────────────────────────────

print("\n=== Inserting articles ===")
for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        print(f"   Headline: {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
        # Try to print response body for debugging
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text[:300]}")

print("\n=== Done ===")
