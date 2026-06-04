#!/usr/bin/env python3
"""Immigration writer — 2026-06-04 20:00 UTC run. Two articles."""

import json, os, uuid, re, requests, io
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# Load env
for env_file in [Path.home() / ".env.supabase", Path.home() / "workspace" / ".env.pexels"]:
    if env_file.exists():
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

def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def upload_to_supabase(img_url, filename):
    """Download image, compress, upload to Supabase storage bucket article-images."""
    r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
    r.raise_for_status()
    raw = r.content
    if len(raw) < 5000:
        print(f"  ⚠ Image too small ({len(raw)} bytes), skipping")
        return None
    compressed = compress_image(raw)
    size_kb = len(compressed) / 1024
    print(f"  Compressed: {size_kb:.0f} KB")

    upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    upload_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    ur = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
    if ur.status_code not in (200, 201):
        # Try PUT for upsert
        ur = requests.put(upload_url, headers=upload_headers, data=compressed, timeout=30)
    ur.raise_for_status()
    public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
    print(f"  ✅ Uploaded: {public_url[:80]}...")
    return public_url

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")


# ── Article 1: Chip Roy's American White-Collar Worker Jobs Act ──

art1_id = str(uuid.uuid4())
art1_slug = make_slug("chip-roy-h1b-lottery-kill-bill-white-collar-worker-act")

print("📸 Sourcing image for Article 1 (Chip Roy)...")
art1_img_url = None
try:
    art1_img_url = upload_to_supabase(
        "https://upload.wikimedia.org/wikipedia/commons/d/de/Chip_Roy_118th_Congress.jpg",
        f"{art1_id}.jpg"
    )
except Exception as e:
    print(f"  ❌ Image upload failed: {e}")

art1_body = """Rep. Chip Roy wants to kill the H-1B lottery. On June 4, the Texas Republican introduced the American White-Collar Worker Jobs Act, a bill that would replace the random selection system with merit-based criteria and force employers to prove they tried to hire Americans first.

The bill's core provisions are blunt. Employers would need to pass a labor market test — conducted jointly by the Department of Labor and USCIS — demonstrating a "good faith effort" to recruit American workers before petitioning for an H-1B. Visa holders would have to be paid the same wage as an American with equivalent experience and qualifications. No more prevailing-wage loopholes. No more lottery luck.

## What the Bill Actually Does

The American White-Collar Worker Jobs Act targets three structural features of the current H-1B system that critics have long called out:

**Lottery elimination.** Instead of the current random selection from a pool of petitions each April, applicants would be ranked on merit — a scoring system that presumably weights salary, qualifications, and employer need, though the bill text's full scoring framework has not been released.

**Wage parity mandate.** Employers must pay H-1B workers at the same level as American employees with comparable experience and credentials. This goes beyond the existing prevailing-wage requirement, which allows employers to pay at the 17th or 34th percentile of local wages for the occupation.

**Labor market testing.** Before filing an H-1B petition, employers must demonstrate to DOL and USCIS that they made genuine attempts to recruit domestically. This mirrors requirements in other countries' work-visa systems — Australia, Canada, and the UK all require some form of labor market impact assessment.

## The Timing Is Not Accidental

Roy's bill drops into a Congress already saturated with H-1B reform proposals. Rep. Paul Gosar's H.R. 8443 would pause H-1B hiring entirely. The Heritage Foundation recently published its own reform blueprint. And the $100,000 H-1B fee — imposed by presidential proclamation last September — has already reshaped the program's economics, with DHS Secretary Markwayne Mullin testifying this week that over 200,000 of 286,000 FY2026 applicants paid the premium fee.

"For its nearly forty-year history, the H-1B visa has been abused, allowing employers to routinely sideline American STEM workers in favor of cheap foreign labor, while masking layoffs and wage suppression as 'shortages,'" Roy said in a statement provided to the Daily Caller.

The bill has no Democratic co-sponsors and faces long odds in a Congress where even Republicans are divided on H-1B policy. Trump himself has oscillated between defending the program and signing the $100,000 fee proclamation.

## What This Means for Indian H-1B Workers

Indians account for roughly 72% of all H-1B approvals. A merit-based system could benefit highly paid senior engineers and architects at companies like Google or Microsoft, whose salaries would score well under any points framework. But it could devastate the IT services model that employs hundreds of thousands of Indian workers through companies like Infosys, TCS, and Wipro, where salaries cluster closer to the prevailing-wage floor.

The labor market test is the provision that should keep immigration attorneys busy. If enforced strictly, it would add months to the H-1B petition timeline and create a paper trail that makes denials easier to justify. If enforced loosely, it becomes a checkbox exercise — much like the current Labor Condition Application.

For the roughly 700,000 Indians currently on H-1B status or waiting in the green card backlog, Roy's bill is unlikely to become law in its current form. But it signals that the legislative pressure on work visas is intensifying from the restrictionist right, even as the administration collects billions from the fee it imposed on the same program these lawmakers want to dismantle."""

art1 = {
    "id": art1_id,
    "headline": "Kill the Lottery, Test the Market — Chip Roy's Bill Would Remake H-1B From Scratch",
    "subheadline": "The American White-Collar Worker Jobs Act would end random selection, mandate wage parity, and force employers to prove they tried hiring Americans first. Indians hold 72% of H-1B approvals.",
    "slug": art1_slug,
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians dominate H-1B approvals at 72%. A merit-based system would benefit high-salary tech workers but could gut the IT services staffing model that employs hundreds of thousands. The labor market test adds new uncertainty for every Indian professional whose employer sponsors them.",
    "tags": ["h1b", "chip-roy", "h1b-lottery", "congress", "immigration-reform", "merit-based"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Daily Caller", "url": "https://dailycaller.com/2026/06/04/chip-roy-h1-b-abuses-white-collar-jobs/"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/homelands-mullin-signals-flexibility-on-100-000-h-1b-visa-fees"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/news/over-2-lakh-applicants-paid-100000-for-faster-h-1b-visa-processing-in-fy2026-dhs-says/article69641234.ece"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": art1_img_url or "",
    "image_caption": "Rep. Chip Roy (R-TX) in his official 118th Congress portrait",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": art1_body
}


# ── Article 2: EB-2 India Per-Country Limit Exhausted ──

art2_id = str(uuid.uuid4())
art2_slug = make_slug("eb2-india-shut-out-fy2026-per-country-limit-exhausted")

print("📸 Sourcing image for Article 2 (EB-2 India)...")
art2_img_url = None
try:
    art2_img_url = upload_to_supabase(
        "https://upload.wikimedia.org/wikipedia/commons/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
        f"{art2_id}.jpg"
    )
except Exception as e:
    print(f"  ❌ Image upload failed: {e}")

# Fallback to Pexels if USCIS photo fails
if not art2_img_url:
    print("  Trying Pexels fallback...")
    try:
        art2_img_url = upload_to_supabase(
            "https://images.pexels.com/photos/32642491/pexels-photo-32642491.jpeg?auto=compress&cs=tinysrgb&w=1200",
            f"{art2_id}.jpg"
        )
    except Exception as e:
        print(f"  ❌ Pexels fallback also failed: {e}")

art2_body = """The gate just closed four months early. The State Department, in coordination with USCIS, has announced that all available EB-2 immigrant visas for applicants chargeable to India have been issued for fiscal year 2026. No more green cards in this category will be approved or issued to Indian nationals until October 1, when FY2027 begins and the annual limits reset.

The announcement, while not unexpected for anyone tracking the visa bulletin's trajectory, landed with a familiar sting. India's EB-2 allocation runs out every single year — in FY2025, it happened in the summer too — but this year's cutoff arrives alongside a Visa Bulletin that has turned visibly hostile to Indian applicants.

## The Numbers Tell the Story

Under the Immigration and Nationality Act, no single country can receive more than 7% of the total employment-based immigrant visas issued in a fiscal year. For FY2026, that means roughly 10,000 EB-2 visas across all of India — a country that produces the largest share of EB-2 petitions by a wide margin. Once those are gone, they are gone.

The June 2026 Visa Bulletin made things worse. USCIS switched from the Dates for Filing chart to the Final Action Dates chart, which immediately tightened eligibility. The EB-2 India final action date retrogressed from July 15, 2014 in May to September 1, 2013 in June — a backward jump of nearly ten months in a single bulletin cycle. That means an Indian professional whose employer filed their I-140 petition in, say, November 2013 went from being eligible to file their green card application to being shut out in the span of one month.

The Dates for Filing cutoff remains at January 15, 2015, but with USCIS now using Final Action Dates, that number is decorative. You can calculate your theoretical place in line, but you cannot move.

## What EB-2 Exhaustion Actually Means

For Indians in the EB-2 queue — and there are hundreds of thousands — the practical effects cascade quickly:

**Adjustment of status freezes.** No I-485 applications will be approved in this category until October. For anyone whose case was pending approval, the wait just extended by four months at minimum.

**Consular processing stops.** Embassies and consulates in India have been directed to halt EB-2 immigrant visa issuance for the remainder of FY2026. If your interview was scheduled for July, August, or September, it will not result in a visa stamp.

**EAD and Advance Parole continue.** The one silver lining: if you already filed I-485, your Employment Authorization Document and travel permission remain valid and renewable. The exhaustion affects new approvals, not interim benefits.

**Downgrade math gets complicated.** Some applicants have been porting their priority dates to EB-3, where the backlog has occasionally moved faster for India. But EB-3 India is also severely backlogged, and the calculus of switching categories mid-wait is not straightforward. An immigration attorney should run the numbers before anyone jumps lanes.

## The Per-Country Cap Debate Returns

Every time EB-2 India exhausts its allocation, the conversation circles back to the 7% per-country cap, a provision that treats India — with 1.4 billion people and a dominant share of STEM immigration — identically to Liechtenstein. Bills to eliminate or raise the cap have been introduced in nearly every Congress for the past decade. None have passed.

The most recent legislative movement on this front came from a bipartisan group proposing to phase out country quotas for employment-based green cards and recapture unused visas for healthcare workers. But with Congress currently consumed by the $70 billion immigration enforcement reconciliation bill and the political drama surrounding the anti-weaponization fund, per-country cap reform is not on anyone's floor calendar.

## Twelve Years and Counting

The EB-2 India final action date of September 1, 2013 means that USCIS is currently processing petitions filed nearly thirteen years ago. An Indian engineer who had their I-140 approved in late 2013 has been waiting through the entirety of the Biden administration and now the second Trump term for a green card. They have likely changed employers, changed cities, watched their children grow up without permanent status, and renewed their H-1B six or seven times.

The October reset will reopen the pipeline, but only to resume the slow crawl. FY2027's allocation will face the same structural math: massive demand from India, a 7% cap that does not bend, and a system designed four decades ago for a labor market that no longer exists."""

art2 = {
    "id": art2_id,
    "headline": "Shut Out Until October — EB-2 India Exhausts Its FY2026 Visa Allocation",
    "subheadline": "The State Department has issued all available EB-2 green cards for Indian nationals this fiscal year. The final action date retrogressed nearly ten months in June alone, pushing the backlog past thirteen years.",
    "slug": art2_slug,
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Hundreds of thousands of Indian professionals in the EB-2 queue face a hard stop until October 1. The 7% per-country cap and the switch to Final Action Dates mean anyone with a priority date after September 2013 cannot move forward. Adjustment of status approvals, consular interviews, and immigrant visa issuance are all frozen.",
    "tags": ["eb2", "green-card", "per-country-cap", "visa-bulletin", "uscis", "backlog"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "NewsPoint / Times of India", "url": "https://www.newspointapp.com/english/tech/as-india-per-country-limit-reached-in-eb-2-category-for-fy-2026-uscis-says-annual-limits-will-reset-with-the-start-of-toi/articleshow/1450482087435c31b8c72a220b4248cf92b26b7a"},
        {"name": "Manifest Law", "url": "https://manifestlaw.com/blog/eb2-priority-date-india/"},
        {"name": "Ogletree Deakins (FY2025 precedent)", "url": "https://ogletree.com/insights-resources/blog-posts/state-department-announces-fy-2025-visa-limit-has-been-reached-for-the-eb-2-category/"}
    ]),
    "score_total": 88,
    "status": "published",
    "published_at": now,
    "image_url": art2_img_url or "",
    "image_caption": "A USCIS Application Support Center in Queens, New York",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": art2_body
}


# ── Insert articles ──
articles = [art1, art2]
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ Published: {art['slug']}")
        print(f"   Headline: {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\n🏁 Done. {len(articles)} articles processed.")
