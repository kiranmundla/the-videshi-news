#!/usr/bin/env python3
"""
Immigration Writer — 2026-06-14 04:00 UTC
Two fresh immigration articles for The Videshi.
"""

import json, os, uuid, re, requests, io
from datetime import datetime, timezone
from pathlib import Path

# --- ENV ---
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

pexels_env = Path.home() / "workspace/.env.pexels"
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
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

def download_and_upload_image(source_url, filename):
    """Download image, compress, upload to Supabase storage. Returns public URL."""
    try:
        from PIL import Image
    except ImportError:
        # Fallback: just return source URL if PIL not available
        print(f"  ⚠ PIL not available, using source URL directly")
        return source_url

    try:
        r = requests.get(source_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            print(f"  ⚠ Not an image: {content_type}")
            return source_url
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small ({len(r.content)} bytes)")
            return source_url

        # Compress
        img = Image.open(io.BytesIO(r.content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        max_width = 1200
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80, optimize=True)
        compressed = buf.getvalue()
        print(f"  📦 Compressed: {len(r.content)} → {len(compressed)} bytes ({img.width}x{img.height})")

        # Upload to Supabase storage
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
            print(f"  ✅ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({ur.status_code}): {ur.text[:200]}")
            return source_url
    except Exception as e:
        print(f"  ⚠ Image processing error: {e}")
        return source_url

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")


# ─── ARTICLE 1: H-4 EAD Rescission Rule ───

art1_id = str(uuid.uuid4())
art1_slug = make_slug("h4-ead-rescission-dhs-proposed-rule-h1b-spouses-work-permit")

art1_body = """The Department of Homeland Security is in the final stages of drafting a proposed rule that would terminate the H-4 Employment Authorization Document programme — the Obama-era regulation that lets certain spouses of H-1B workers hold jobs in the United States. According to a court filing in *Save Jobs USA v. DHS*, the rule is clearing its last internal hurdles before being sent to the Office of Management and Budget for review. DHS originally planned to publish the proposal in February; it now expects to release it for public comment as early as this month.

The stakes are arithmetically simple and personally devastating. An estimated 100,000 H-4 spouses hold active EADs. The overwhelming majority are Indian women married to H-1B workers who have approved I-140 petitions but whose green card priority dates are stuck somewhere in the EB-2 or EB-3 India backlog — a queue that stretches back more than a decade. These are not workers on a temporary reprieve. They have been filing taxes, building careers, and in many cases earning salaries that keep their families solvent during a green card wait that was never supposed to take this long.

## What The Current Rule Allows

The H-4 EAD programme, established in 2015, grants work authorisation to H-4 dependent spouses if their H-1B partner meets one of two conditions: an approved Form I-140 immigrant worker petition, or a one-year extension of H-1B status beyond the statutory six-year maximum under the American Competitiveness in the Twenty-First Century Act. H-4 children are not eligible.

The rule was designed as a retention mechanism. The logic was that if a skilled worker's spouse could not work during a multi-year green card wait, the family might leave the country altogether — taking the worker's skills and the employer's investment with them.

## Why DHS Wants to Kill It

The proposed rescission is rooted in *Save Jobs USA v. DHS*, a lawsuit filed by a group of American technology workers who argued the programme displaced domestic workers. The case was dismissed in 2016, but the plaintiffs appealed to the D.C. Circuit. The court proceedings have been held in abeyance — paused, effectively — while DHS moved forward with its own plans to rescind the regulation.

The Trump administration has framed the rescission as part of its broader "America First" hiring agenda, arguing that employment authorisation for dependent spouses was never mandated by statute and that the executive branch overstepped when it created the programme. DHS has been conducting an economic impact analysis, which delayed the original February publication date.

## What Happens If The Rule Is Published

Publication in the Federal Register would trigger a mandatory public comment period — typically 60 days. After reviewing comments, DHS would need to issue a final rule, a process that historically takes several months. During that entire stretch, eligible H-4 spouses can continue to apply for and renew their EADs under the existing regulation.

But the uncertainty alone has consequences. Immigration attorneys across the country report that H-4 holders are already making contingency plans: accelerating savings, exploring EB-1A self-petition routes, or preparing to downshift from professional careers to unpaid caregiving if their work authorisation evaporates.

## Why Indian Families Are Uniquely Exposed

The per-country cap ensures that Indian nationals face the longest green card queues in the system. An EB-2 India applicant with a priority date in 2014 has been waiting more than a decade. An EB-3 India applicant from 2013 has waited even longer. During that entire period, the H-4 EAD has been the legal mechanism that allowed spouses — the vast majority of them women — to contribute economically to their households.

Strip that mechanism away and you create a class of professionals who are legally present, whose families are legally employed, whose children attend American schools, but who are themselves barred from earning a living. The financial arithmetic of Silicon Valley or the New York metro area on a single H-1B salary, with a mortgage and school-age children, is not generous.

## What To Do Now

If you hold an H-4 EAD or are eligible for one, immigration attorneys uniformly advise filing or renewing immediately. An approved EAD would remain valid for its duration even if the programme is later rescinded — though the specifics of any grandfathering provision will depend on the text of the final rule, which remains confidential until publication.

The public comment period, once it opens, will be the primary mechanism for opposition. Organisations including the American Immigration Lawyers Association and several Indian American advocacy groups have signalled they will mount aggressive comment campaigns. The H-4 EAD programme survived one rescission attempt during Trump's first term, when the proposal stalled at OMB for years. Whether it survives a second attempt may depend on whether the political calculus has changed — and whether the families affected can make their case before the window closes."""

art1 = {
    "id": art1_id,
    "headline": "Washington Is About to Pull the Work Permit from a Hundred Thousand H-1B Spouses",
    "subheadline": "DHS is finalising a proposed rule to rescind the H-4 EAD programme. For Indian families who depend on two incomes to survive the green card wait, the clock is measured in weeks.",
    "slug": art1_slug,
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "An estimated 100,000 H-4 EAD holders are overwhelmingly Indian women married to H-1B workers stuck in the EB-2/EB-3 India green card backlog — losing work authorisation would force families to survive on a single income during a wait that already stretches a decade or more.",
    "tags": ["h4-ead", "h1b", "uscis", "work-permit", "immigration", "dhs"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Fragomen", "url": "https://www.fragomen.com"},
        {"name": "EY Global", "url": "https://www.ey.com"},
        {"name": "Federal Register", "url": "https://www.federalregister.gov"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "",  # Will be set after upload
    "image_caption": "A USCIS Employment Authorization Document, the card at the centre of the H-4 EAD debate",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}


# ─── ARTICLE 2: OPT/SEVIS Fraud Crackdown ───

art2_id = str(uuid.uuid4())
art2_slug = make_slug("opt-sevis-termination-indian-students-uscis-fraud-algorithm")

art2_body = """When USCIS flipped the switch on its new fraud detection algorithm in January 2025, the system began cross-referencing SEVIS records with IRS payroll data and flagging anomalies 25 per cent faster than any previous method. By the end of the first quarter of 2026, more than 500 OPT work authorisations had been revoked through enhanced employer site visits alone. The people losing their status are disproportionately Indian — accounting for half of all tracked visa revocations, according to data compiled by the American Immigration Lawyers Association.

The numbers are not a coincidence. Indian students are the largest international cohort in the United States at 363,000, and they are concentrated in the STEM OPT pipeline — the 36-month post-graduation work authorisation that serves as the primary bridge between a student visa and an H-1B petition. A SEVIS termination does not merely end OPT work authorisation. It starts the unlawful-presence clock, blocks reinstatement applications, and casts a shadow over every future immigration filing.

## The Algorithm and How It Works

USCIS launched the fraud detection system on 15 January 2025. It pulls data from three sources: SEVIS enrolment records maintained by Designated School Officials, IRS payroll filings from employers, and the results of physical site visits conducted by USCIS Fraud Detection and National Security officers. When the system detects a mismatch — an OPT student listed at an employer address that does not exist, a zero-wage filing for someone supposedly working full-time, an employer with a suspiciously high ratio of OPT workers to revenue — it generates a flag.

The consequences cascade quickly. Under 8 CFR 214.2(f)(9), unauthorised employment voids F-1 status instantly upon detection. No grace period applies. Each day in the United States after status loss counts towards the 180-day and one-year bars under INA §212(a)(9)(B), which prohibit re-entry for three and ten years respectively. ICE has given OPT violators priority in removal dockets during what enforcement agencies internally describe as the 2026 surge.

## The Fraud Ring Problem

The crackdown is not without cause. Federal investigators have charged 45 fraud ring operators since early 2025 — people who operated shell companies, issued fake employment letters, and collected fees from students desperate to maintain OPT status after legitimate employers fell through. Students who showed up for "orientation" at these firms found no real work, minimal pay through cash apps, and periods of "benching" without compensation.

The trouble is that the algorithm does not distinguish between a student who knowingly enrolled with a fraudulent employer and one who was deceived. A terminated SEVIS record looks the same regardless of intent, and the reinstatement process through Form I-539 requires demonstrating "extraordinary circumstances" — a standard rarely met in fraud-adjacent cases.

## Why Indian Students Bear the Brunt

Three factors converge. First, scale: with 363,000 students, India is the single largest source country, and a proportional share of fraud targets Indian students because fraudulent operators market their services within Indian student networks. Second, concentration: Indian students are heavily represented in STEM fields eligible for the 36-month OPT extension, making them more likely to be on OPT at any given time. Third, the H-1B pipeline: for many Indian students, OPT is not just a work programme but the only viable path to long-term employment in the United States, creating demand that fraudulent operators exploit.

The AILA data is stark. Of all tracked SEVIS terminations, Indian nationals account for 50 per cent. Chinese students account for 14 per cent. Every other nationality combined makes up the remaining third.

## The Collateral Damage

A SEVIS termination does not just end a student's current job. It contaminates their immigration record. H-1B lottery entries face additional scrutiny if a fraud flag appears. Green card adjustment applications trigger secondary review. Naturalization petitions can be delayed or denied based on a status violation that occurred years earlier.

Students who discover mid-OPT that their employer is fraudulent face an impossible choice: continue working and risk deeper complicity, or quit and start the unemployment clock. OPT holders are permitted a maximum of 90 days of unemployment (150 days for STEM OPT). Exceeding that limit is itself a status violation.

Immigration attorneys advise current OPT holders to maintain comprehensive personal records: employer name, employment dates, supervisor contact information, weekly hours, job title, and a description of duties directly related to their field of study. This documentation may be the only defence against an algorithmic flag that treats every anomaly as fraud until proven otherwise.

## What Comes Next

The enforcement posture shows no signs of easing. DHS is simultaneously advancing a proposed rule to replace Duration of Status — the flexible framework that allows F-1 students to remain in the United States as long as they maintain valid academic status — with a fixed four-year cap. If both measures take effect, Indian students will face a compressed timeline, tighter enforcement, and fewer pathways to recover from a misstep.

For the 363,000 Indian students currently in the system, the message is unambiguous: the margin for error has shrunk to zero, and the algorithm is not interested in context."""

art2 = {
    "id": art2_id,
    "headline": "Half of All Visa Revocations Are Indian Students — and USCIS Just Deployed an Algorithm to Find More",
    "subheadline": "A new fraud detection system cross-references SEVIS records with IRS payrolls and has already revoked 500 OPT authorisations this quarter. Indian nationals account for 50 per cent of all tracked terminations.",
    "slug": art2_slug,
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian students make up half of all tracked SEVIS terminations and are the largest international student cohort in the US at 363,000. For families who sent children abroad for education, a SEVIS termination means not just a lost job but a poisoned immigration record that follows them for years.",
    "tags": ["f1-visa", "opt", "sevis", "uscis", "indian-students", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "American Immigration Lawyers Association (AILA)", "url": "https://www.aila.org"},
        {"name": "VisaVerge", "url": "https://visaverge.com/immigration-news/2026-opt-fraud-crackdown/"},
        {"name": "Collegedunia", "url": "https://collegedunia.com/usa/article/us-sevis-termination-rules-2026-what-indian-f1-students-must-know"},
        {"name": "SEVP (Student and Exchange Visitor Program)", "url": "https://www.ice.gov/sevis"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "",  # Will be set after upload
    "image_caption": "The USCIS Application Support Center in Jamaica, Queens — one of the offices processing the surge of OPT-related cases",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}


# ─── IMAGE PROCESSING ───

print("\n📸 Processing images...")

# Article 1: USCIS EAD card from Wikimedia Commons
print("\n--- Article 1: H-4 EAD ---")
art1_img_source = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/USCIS_EAD_card.jpg/1200px-USCIS_EAD_card.jpg"
art1_img_url = download_and_upload_image(art1_img_source, f"{art1_slug}.jpg")
art1["image_url"] = art1_img_url

# Article 2: USCIS Application Support Center from Wikimedia Commons
print("\n--- Article 2: OPT/SEVIS ---")
art2_img_source = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1200px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg"
art2_img_url = download_and_upload_image(art2_img_source, f"{art2_slug}.jpg")
art2["image_url"] = art2_img_url


# ─── INSERT ───

print("\n📝 Inserting articles...")

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")
