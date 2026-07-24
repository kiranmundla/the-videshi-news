#!/usr/bin/env python3
"""Immigration writer — 2026-06-05 04:00 UTC run.
Publishes 2 fresh immigration articles for The Videshi.
"""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# ── Load env ──────────────────────────────────────────────────
for env_file in [Path.home() / ".env.supabase", Path.home() / "workspace/.env.pexels"]:
    if env_file.exists():
        for line in env_file.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

SB_URL  = os.environ["SUPABASE_URL"]
SB_KEY  = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# ── Helpers ───────────────────────────────────────────────────
def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-20260605"

def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()

def upload_to_supabase(image_url, filename):
    """Download, compress, upload to article-images bucket. Return public URL."""
    r = requests.get(image_url, headers=UA, timeout=20)
    r.raise_for_status()
    raw = r.content
    if len(raw) < 5000:
        print(f"  ⚠ Image too small ({len(raw)} bytes), skipping upload")
        return None
    compressed = compress_image(raw)
    print(f"  📦 Compressed: {len(raw)} → {len(compressed)} bytes")
    upload_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    up = requests.post(
        f"{SB_URL}/storage/v1/object/article-images/{filename}",
        headers=upload_headers,
        data=compressed,
        timeout=30,
    )
    up.raise_for_status()
    return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"

def validate_image(url):
    """Quick HEAD check for image validity."""
    try:
        r = requests.head(url, headers=UA, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        return r.status_code == 200 and "image" in ct and cl > 5000
    except:
        return False


# ── Article 1: EB-2 India Boomerang Warning ──────────────────
art1_id = str(uuid.uuid4())
art1_slug = make_slug("eb2-india-boomerang-priority-date-artificial-gains-retrogression-risk")

# Image: 2023 green card front from Wikimedia Commons
art1_source_img = "https://upload.wikimedia.org/wikipedia/commons/4/49/2023_green_card_front.jpg"
print(f"Article 1: Sourcing image from Wikimedia Commons...")
art1_img = upload_to_supabase(art1_source_img, f"{art1_slug}.jpg")
if not art1_img:
    # Fallback to passport stamp from Pexels
    art1_source_img = "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&w=1200"
    art1_img = upload_to_supabase(art1_source_img, f"{art1_slug}.jpg")

art1_body = """The numbers looked too good to be true. Between October 2025 and April 2026, the EB-2 India Final Action Date surged from April 1, 2013 to July 15, 2014 — the kind of movement that, in any normal year, would take the better part of a decade. Thousands of Indian professionals filed I-485 adjustment of status applications, booked medical exams, and dared to imagine the end of a wait that had stretched across their entire American career.

Now a former State Department official is warning them to brace for a correction.

## The "Completely Artificial" Advance

Charlie Oppenheim, who spent decades as Chief of the Visa Control and Reporting Division at the Department of State, has issued a blunt assessment of the recent EB-2 India gains. In an analysis shared with the American Immigration Lawyers Association, Oppenheim called the priority date movement "completely artificial," driven not by any structural improvement in the system but by a policy quirk: the Trump administration's travel restrictions on 75 countries.

The mechanism is straightforward. When nationals from dozens of countries are blocked from receiving immigrant visas, their unused visa numbers become available to other countries — chiefly India and China, which have the longest backlogs. The result is a temporary acceleration that has nothing to do with the underlying demand.

"These are completely artificial movements, and if or when the Administration's restrictions affecting the 75 countries are lifted, there will be a boomerang effect," Oppenheim wrote. "The longer the policy remains in place, the more severe the corrective action may be."

## The FY2026 Timeline, Month by Month

The pattern is unmistakable. Here is the EB-2 India Final Action Date progression through this fiscal year:

- **October 2025**: April 1, 2013
- **November 2025**: April 1, 2013
- **December 2025**: May 15, 2013
- **January 2026**: July 15, 2013
- **February 2026**: July 15, 2013
- **March 2026**: September 15, 2013
- **April 2026**: July 15, 2014

That last jump — a full ten months in a single bulletin — was the largest EB-2 India advance since 2019. It happened because the 75-country policy was suppressing Rest of World demand, freeing up numbers that would otherwise have gone to applicants from those nations.

## The June 2026 Switch

For June 2026, USCIS made the situation more precarious by switching from the Dates for Filing chart to the Final Action Dates chart for determining adjustment of status eligibility. Under the previous months' Dates for Filing chart, applicants with somewhat later priority dates could still submit their I-485 packets and begin accruing interim benefits — work authorization, advance parole, the ability to change employers without losing their place in line.

The switch to Final Action Dates means USCIS will only accept applications from those whose priority dates are actually current for final adjudication. For EB-2 India, the cutoff stands at July 15, 2014. Anyone who filed during the more generous window now faces a wait with no guarantee their date will hold.

## What the Boomerang Looks Like

Oppenheim draws a direct parallel to the COVID era. When employment-based visa caps were temporarily raised to 281,000 in fiscal year 2022 — double the usual allocation — priority dates lunged forward. Then, when the numbers reverted to normal, retrogression hit hard. Dates that had advanced by years snapped back, stranding applicants who had assumed the gains were permanent.

The current scenario carries a similar risk. The affected applicants from the 75 restricted countries are not disappearing. They are accumulating at the front of the Rest of World line, many with priority dates earlier than those of Indian and Chinese applicants. The moment restrictions are lifted, those applicants will flood back into the system, and India will once again be constrained by its seven-percent per-country cap.

"The affected applicants are not going away and will be at the front of the visa line with early Rest of World priority dates," Oppenheim warned. "This would mean that China and India would again be subject to their low per-country limits."

## What This Means for Indians in the Queue

For the roughly 400,000 Indian nationals waiting for employment-based green cards, the takeaway is uncomfortable: do not plan your life around the current priority date. The gains of the past nine months are a side effect of a policy that could be reversed by executive order, court ruling, or simple diplomatic recalibration.

Immigration attorneys are advising clients to file I-485 if their date is current — the benefits of pending status are real — but to avoid making irreversible decisions based on the assumption that approval is imminent. Job changes, home purchases, children's college planning: all of these should account for the possibility that EB-2 India could retrogress by several years in a single bulletin.

The system is not broken in a new way. It is broken in the same old way, temporarily masked by a policy that was never designed to help Indian applicants. When the mask comes off, the line will be exactly where it was."""

art1 = {
    "id": art1_id,
    "headline": "The Boomerang Is Coming — A Former State Department Official Says India's EB-2 Gains Are Built on Sand",
    "subheadline": "Charlie Oppenheim warns that the EB-2 India priority date surge from April 2013 to July 2014 is entirely artificial, driven by the 75-country travel ban — and that a severe correction is inevitable when the restrictions end.",
    "slug": art1_slug,
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "For the 400,000 Indian nationals waiting for employment-based green cards, the recent priority date movement felt like a breakthrough. A former State Department official says it is a mirage — and the retrogression that follows could erase years of apparent progress overnight.",
    "tags": ["eb-2", "green-card", "visa-bulletin", "retrogression", "priority-date", "india-backlog", "charlie-oppenheim"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "WR Immigration (Wolfsdorf) — Oppenheim Analysis", "url": "https://wolfsdorf.com/india-eb-2-and-eb-3-visa-bulletin-movement-reading-between-the-lines-february-april-2026/"},
        {"name": "Manifest Law — June 2026 EB-2 India Updates", "url": "https://manifestlaw.com/what-is-the-eb-2-priority-date-for-india/"},
        {"name": "Colombo Hurd Law — May 2026 Visa Bulletin Analysis", "url": "https://colombohurdlaw.com/may-2026-visa-bulletin-eb-2-is-current/"},
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": art1_img,
    "image_caption": "A 2023 US permanent resident card, the document at the center of a decade-long wait for Indian applicants",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": art1_body,
}


# ── Article 2: OPT Fraud Dragnet ─────────────────────────────
art2_id = str(uuid.uuid4())
art2_slug = make_slug("opt-fraud-dragnet-ice-10000-students-india-shell-companies")

# Image: University students from Pexels
art2_source_img = "https://images.pexels.com/photos/7972324/pexels-photo-7972324.jpeg?auto=compress&cs=tinysrgb&w=1200"
print(f"Article 2: Sourcing image from Pexels...")
art2_img = upload_to_supabase(art2_source_img, f"{art2_slug}.jpg")
if not art2_img:
    art2_source_img = "https://images.pexels.com/photos/6147148/pexels-photo-6147148.jpeg?auto=compress&cs=tinysrgb&w=1200"
    art2_img = upload_to_supabase(art2_source_img, f"{art2_slug}.jpg")

art2_body = """ICE says it has identified more than 10,000 foreign students connected to employers it considers fraudulent — companies that existed on paper but operated from empty offices, shell addresses, and unverifiable business registrations. Investigators report that a significant portion of the fraud network was coordinated from India, targeting students desperate for the work authorization that keeps them legally in the country after graduation.

The crackdown represents the largest enforcement action in the history of the Optional Practical Training program, and it lands at the worst possible moment for Indian graduates trying to build careers in America.

## How the Scheme Worked

Optional Practical Training allows international graduates to work in the United States for up to 12 months after completing their degree — or up to 36 months for those in STEM fields. The program has become the single most important stepping stone between an American degree and an H-1B visa for hundreds of thousands of Indian students.

The fraud exploited that dependency. Investigators found companies that charged students thousands of dollars for "employment" that never existed. The companies filed the necessary paperwork with USCIS, produced fake pay stubs and employment verification letters, and maintained the fiction of a legitimate employer-employee relationship. Students received OPT-based work authorization while performing no actual work.

ICE Director Todd Lyons called the 10,000 identified cases "the tip of the iceberg," suggesting the investigation is ongoing and the final numbers will be substantially higher. The agency is tracing financial transactions, communication networks, and employer registration patterns to map the full scope of the operation.

## The India Connection

The fraud networks are not randomly distributed. According to enforcement officials, many of the shell companies were set up and managed from India, with operatives coordinating placements across multiple American cities. The structure mirrors earlier schemes that led to high-profile busts — most notably the University of Farmington sting in 2019, where ICE created a fake university in Michigan to catch students and recruiters engaged in visa fraud. More than 250 students, overwhelmingly Indian nationals, were arrested or deported in that operation.

The current investigation is different in scale and method. Rather than setting traps, ICE is conducting forensic audits of existing employers — visiting listed addresses, verifying business operations, and cross-referencing employment records with tax filings. When agents find locked doors and empty buildings where hundreds of students supposedly work, the cases build themselves.

## The Legislative Pile-On

The enforcement action is not happening in a vacuum. On Capitol Hill, the OPT program is under simultaneous legislative assault from multiple directions.

Representative Chip Roy's American White-Collar Worker Jobs Act, introduced this week, includes a provision to abolish OPT entirely. The bill frames the program as a pipeline that undercuts American STEM graduates by providing employers with a cheaper, more compliant workforce. Roy's legislation would also end the H-1B visa's role as a pathway to permanent residency — effectively severing the student-to-green-card pipeline that the Indian tech workforce has relied on for three decades.

Separately, Representative Paul Gosar's bill proposes terminating the OPT program outright, which would immediately affect roughly 200,000 participants, a substantial share of whom are Indian nationals.

And a proposed rule change would cut the post-completion grace period for F-1 students from 60 days to 30 days, while imposing stricter justification requirements for students who enrol in additional degree programs — a direct strike at the Day 1 CPT pathway that thousands of Indian graduates use as a bridge when they fail to win the H-1B lottery.

## The Squeeze on Legitimate Students

The collateral damage extends far beyond the fraudsters. Immigration attorney Jessica Goldman has warned that the tighter rules could be devastating for Indian professionals working in artificial intelligence, machine learning, software engineering, and data science — fields where foreign nationals comprise a disproportionate share of the talent pool.

"For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working,'" Goldman told reporters. "There's no doubt about it that this is going to have a massive impact on the companies that are in desperate need of top talent."

The paradox is acute. The United States is engaged in an AI arms race with China that depends on exactly the kind of skilled immigrants the enforcement and legislative actions are targeting. Indian nationals hold a majority of H-1B visas in the technology sector. Many of them entered the country on F-1 student visas, used OPT to gain their first professional experience, and eventually secured employer-sponsored work authorization.

## What Indian Graduates Should Know

Students currently on OPT should verify that their employer is legitimate — not just on paper, but in practice. USCIS site visits are increasing, and students found at fraudulent employers face not just the loss of their work authorization but potential bars on future visa applications.

Those considering Day 1 CPT programs should be aware that the window for serial enrollment may be closing. And anyone in the H-1B lottery should know that if Roy's or Gosar's bills gain traction, the entire post-graduation pathway could look fundamentally different within a year.

The message from Washington is consistent, even if the methods vary: the era of easy access to the American labour market through the student visa pipeline is ending. For Indian graduates, the question is no longer whether the rules will change, but how fast."""

art2 = {
    "id": art2_id,
    "headline": "Ten Thousand Students, Zero Real Jobs — ICE's OPT Dragnet Has India Written All Over It",
    "subheadline": "Investigators found shell companies operating from India that charged students thousands for fake employment. The crackdown hits as Congress moves to abolish the OPT program entirely.",
    "slug": art2_slug,
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian graduates are the largest group relying on OPT to bridge the gap between their American degree and an H-1B visa. The fraud investigation targets networks coordinated from India, while new legislation would eliminate the program that 200,000 foreign graduates — many of them Indian — depend on.",
    "tags": ["opt", "student-visa", "f1", "ice", "fraud", "chip-roy", "indian-students", "uscis"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Meyka — ICE OPT Fraud Crackdown", "url": "https://meyka.com/ice-cracks-down-on-opt-fraud-may-14-10000-students-targeted/"},
        {"name": "Rep. Chip Roy — American White-Collar Worker Jobs Act Press Release", "url": "https://roy.house.gov/press-releases"},
        {"name": "The Indian Eye — Tighter Student Visa Rules", "url": "https://theindianeye.com/2023/11/30/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
        {"name": "ThisDay — Roy Bill OPT Abolition Details", "url": "https://thisday.com.ng/new-bill-by-chip-roy-targeting-h-1bs-wants-to-end-lottery-opt/"},
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "image_url": art2_img,
    "image_caption": "Students on a university campus — the starting point of the F-1 to OPT to H-1B pipeline that Indian graduates depend on",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": art2_body,
}

# ── Insert articles ──────────────────────────────────────────
articles = [art1, art2]
for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ Published: {art['headline'][:80]}...")
        print(f"   Slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
        # Print response body for debugging
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text[:500]}")

print(f"\nDone. {len(articles)} articles processed.")
