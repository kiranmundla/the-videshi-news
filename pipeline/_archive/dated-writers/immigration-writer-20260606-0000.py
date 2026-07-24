#!/usr/bin/env python3
"""Immigration writer — 2026-06-06 00:00 UTC run"""

import json, os, uuid, re, io, requests, time
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# Load env
for env_file in [Path.home() / "workspace" / ".env.supabase", Path.home() / "workspace" / ".env.pexels"]:
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
    print(f"  Downloading: {img_url[:80]}...")
    r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=30)
    r.raise_for_status()
    raw = r.content
    print(f"  Downloaded: {len(raw)} bytes")
    compressed = compress_image(raw)
    print(f"  Compressed: {len(compressed)} bytes")

    upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    upload_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    ur = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
    if ur.status_code not in (200, 201):
        # Try PUT
        ur = requests.put(upload_url, headers=upload_headers, data=compressed, timeout=30)
    ur.raise_for_status()
    public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
    print(f"  Uploaded: {public_url[:80]}...")
    return public_url

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-20260606"

# ============================================================
# ARTICLE 1: Senate passes $70B enforcement bill
# ============================================================
art1_id = str(uuid.uuid4())
art1_slug = make_slug("senate-70b-enforcement-bill-passes-ice-cbp-funded-through-2029-indian-visa")

print(f"\n📰 Article 1: Senate $70B enforcement bill")
print(f"   Slug: {art1_slug}")

# Image: US Capitol from Pexels
art1_img_url = upload_to_supabase(
    "https://images.pexels.com/photos/32177182/pexels-photo-32177182.jpeg?auto=compress&cs=tinysrgb&w=1200",
    f"{art1_slug}.jpg"
)

art1_body = """The United States Senate voted 52-47 early Friday morning to pass a $69.5 billion budget reconciliation package that funds Immigration and Customs Enforcement and Customs and Border Protection through the end of President Trump's second term in 2029. The bill allocates $30.73 billion for ICE, $22.57 billion for CBP, and $2.5 billion for Department of Homeland Security appropriations.

The passage came after an 18-hour marathon of amendment votes — the procedural mechanism known as a "vote-a-rama" — that stretched through Thursday night and into the predawn hours. Senator Lisa Murkowski of Alaska was the lone Republican to vote against the measure, citing concerns about bypassing the regular appropriations process to fund agencies for three years through reconciliation.

## The Anti-Weaponization Fund That Almost Killed the Bill

The legislation should have been an easy win for Senate Republicans. It was not. The Department of Justice's surprise announcement of a $1.8 billion "anti-weaponization" fund — which critics said could compensate January 6 defendants convicted of assaulting police officers — nearly torpedoed the entire effort.

Senator Bill Cassidy of Louisiana, who lost his primary last month after Trump endorsed his opponent, threatened to side with Democrats on a procedural motion that would have sent the bill back to committee. Three vulnerable Republicans — Susan Collins of Maine, Jon Husted of Ohio, and Dan Sullivan of Alaska — voted with Democrats to block the fund, bringing the motion within a single vote of passage.

Acting Attorney General Todd Blanche told lawmakers earlier in the week that the administration was not moving forward with the fund. Trump undercut that assurance on Wednesday when he refused to rule out reviving it. "The weaponization fund, as far as I'm concerned, was a beautiful thing," he told reporters. "I love it."

In the end, Cassidy voted to keep the bill on track, and his own amendment to redirect the fund toward Capitol police officers injured on January 6 failed when the parliamentarian ruled it needed 60 votes to pass.

## What $70 Billion in Enforcement Money Means for Indian Visa Holders

The headline number — $70 billion for immigration enforcement through 2029 — lands at a time when the enforcement apparatus is already expanding its reach into the workplaces and communities where Indian professionals live and work.

ICE has ramped up worksite investigations under the Trump administration. The Department of Labor launched Project Firewall last September, an initiative specifically targeting H-1B employer compliance that has produced a 48 percent increase in investigations, according to Bloomberg Law reporting. The Labor Secretary can now personally certify investigations into employers suspected of visa program abuse, and the department is using AI systems to flag compliance anomalies.

For the roughly 600,000 Indian nationals on H-1B visas and the hundreds of thousands more on dependent statuses, the practical implications are significant. More funding means more ICE agents, more CBP officers, and more capacity for the kind of targeted enforcement operations that have already rattled Indian communities — from the arrest of 30 Indian truck drivers in Arizona under Operation Checkmate to ICE's identification of more than 10,000 suspected OPT fraud cases tied to shell companies.

## The 76-Day Shutdown That Led Here

The reconciliation route was itself a product of political crisis. Democrats refused to fund ICE after federal officers shot and killed 37-year-old Alex Pretti during Operation Metro Surge in Minneapolis in January. The standoff produced a 76-day shutdown of the Department of Homeland Security — the longest in the agency's history.

Republicans eventually separated ICE and CBP funding from the rest of DHS, passed a regular appropriations bill for the department's non-enforcement functions, and pushed the enforcement money through reconciliation to bypass a Democratic filibuster entirely.

## What Happens Next

The bill now moves to the House, where Speaker Mike Johnson plans to bring it to the floor next week. Passage there is expected but not guaranteed — the same internal Republican tensions over the anti-weaponization fund that delayed the Senate could surface again among House members facing competitive midterm races.

For Indian professionals watching from their cubicles and kitchen tables, the message embedded in the bill is unmistakable: the federal government is investing heavily in the machinery of immigration enforcement, and that machinery does not distinguish between unauthorized border crossers and H-1B holders whose employers cut corners on a Labor Condition Application. The era of light-touch visa compliance is over."""

art1 = {
    "id": art1_id,
    "headline": "Fifty-Two to Forty-Seven — The Senate Just Funded ICE Through the End of Trump's Presidency",
    "subheadline": "A $69.5 billion reconciliation package clears the Senate after an 18-hour vote-a-rama, giving ICE and Border Patrol three years of guaranteed funding — and Indian visa holders three years of guaranteed scrutiny.",
    "slug": art1_slug,
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "With $30.73 billion allocated to ICE and Project Firewall investigations up 48%, Indian H-1B workers and their employers face an enforcement apparatus with deeper pockets and longer reach than ever before.",
    "tags": ["senate", "ice", "cbp", "enforcement", "h1b", "project-firewall", "reconciliation"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/us/us-senate-approves-70-billion-trump-migrant-deportations-2026-06-05/"},
        {"name": "The Hill / WCIA", "url": "https://www.wcia.com/hill-politics/senate-passes-immigration-enforcement-funding-after-clashes-over-white-house-ballroom-anti-weaponization-fund/"},
        {"name": "Associated Press", "url": "https://apnews.com/article/senate-immigration-enforcement-bill-trump-2026"},
        {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/news/senate/3438829/senate-sends-immigration-enforcement-bill-house-without-lawfare-fund-ban/"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/employers-see-spike-in-labor-department-immigration-enforcement"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": art1_img_url,
    "image_caption": "The United States Capitol building in Washington, D.C., where the Senate voted 52-47 to pass the enforcement bill",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": art1_body,
}

# ============================================================
# ARTICLE 2: Pew data on AOS green cards at risk
# ============================================================
art2_id = str(uuid.uuid4())
art2_slug = make_slug("pew-data-39190-indian-green-cards-adjustment-of-status-pm602-threat")

print(f"\n📰 Article 2: Pew data on AOS green cards")
print(f"   Slug: {art2_slug}")

# Image: Actual US green card from Wikimedia Commons
art2_img_url = upload_to_supabase(
    "https://upload.wikimedia.org/wikipedia/commons/4/49/2023_green_card_front.jpg",
    f"{art2_slug}.jpg"
)

art2_body = """In the fiscal year 2024, exactly 39,190 Indian nationals obtained their green cards through a process called adjustment of status — applying for permanent residency from within the United States rather than traveling back to India to complete the paperwork at a consulate. That represents 61 percent of all Indian green card approvals for the year.

Those numbers, published this week by the Pew Research Center in a new analysis of Department of Homeland Security data, put a precise figure on what is at stake as the Trump administration moves to restrict the very pathway that most Indian immigrants have relied on for decades.

## The PM-602 Memo and What It Actually Says

On May 21, USCIS issued Policy Memorandum PM-602-0199, instructing officers that adjustment of status — known in immigration shorthand as AOS — is "an act of administrative grace, not an entitlement." The memo tells adjudicators that consular processing outside the United States should be treated as the default route, with AOS reserved for cases involving "extraordinary circumstances."

The language is bureaucratic. The consequences are not. For an Indian engineer in San Jose with an approved I-140 petition but a priority date that will not be current for another decade, the memo raises a question that previously had a simple answer: do I stay in the country while I wait, or do I have to leave?

Under the old regime, staying was the obvious choice. File Form I-485 when the dates allow, collect an Employment Authorization Document and Advance Parole while waiting, and eventually receive the green card without ever leaving American soil. The PM-602 memo does not eliminate that option, but it gives USCIS officers the discretion to steer applicants toward consular processing — a process that requires traveling to India, attending an interview at a U.S. consulate, and hoping that nothing goes wrong while you are outside the country.

## What the Pew Data Reveals

The Pew analysis, drawing on DHS immigration statistics going back to 2000, makes clear that adjustment of status is not some fringe procedure. It is how America has processed the majority of its green cards for the better part of two decades.

In FY2024, the U.S. issued a total of 1.36 million green cards. Of those, 782,770 — or 58 percent — went to immigrants already living in the country through AOS. Among employment-based green cards specifically, the share was even higher: 69 percent, or 118,480 of 170,980 approvals, were processed through AOS.

India ranks fourth among all countries for AOS green card volume, behind Cuba (155,630 at 87 percent), Mexico (131,330 at 65 percent), and China (46,530 at 66 percent). But the Indian numbers carry a weight that raw volume does not capture, because the Indian employment-based green card backlog is, by a wide margin, the longest of any nationality.

Brookings Institution estimates that approximately 627,000 Indian-born immigrants and their family members are trapped in the employment-based green card queue. The per-country cap — which limits any single nation to seven percent of annual EB visas regardless of demand — means that an Indian EB-2 applicant filing today can expect to wait well over a decade, possibly two, for a final green card.

## Why Consular Processing Terrifies the Backlog

For most immigrant groups, consular processing is an inconvenience — a flight, a few days of paperwork, an interview. For Indian green card applicants, it is a potential trap.

The wait times at U.S. consulates in India are already severe. Mumbai is booking visa interviews nine months out. Hyderabad runs six to eight months. Even Chennai, the fastest post, requires a three-month wait for a B1/B2 appointment. Work visa categories move faster — about one to three months — but the sheer volume of Indian applicants creates unpredictable delays.

More critically, leaving the United States to complete consular processing introduces risks that do not exist when adjusting status domestically. An H-1B holder who travels to India and encounters an unexpected administrative processing delay at the consulate could be stuck outside the country for weeks or months, unable to return to work, while their employer scrambles to manage the absence.

The PM-602 memo's instruction to treat AOS as discretionary — rather than as the standard pathway — adds a layer of uncertainty to every green card interview for Indian applicants. Immigration attorneys report that recent AOS interviews have included questions about why the applicant chose to adjust status rather than return to their home country, a line of inquiry that was virtually unheard of before the memo.

## The Wider Pattern

The Pew data arrives in a week that has made the contours of the current immigration landscape unmistakable. The Senate passed a $70 billion enforcement bill early Friday. USCIS continues to expand the scope of the PM-602 memo. The EB-2 India category has exhausted its FY2026 visa allocation entirely.

For the 39,190 Indian nationals who received their green cards through AOS last year — and for the hundreds of thousands more who are planning to do the same whenever their priority dates arrive — the numbers in the Pew report are not abstract data points. They are the dimensions of a door that is slowly closing."""

art2 = {
    "id": art2_id,
    "headline": "Thirty-Nine Thousand Green Cards at Risk — Pew Puts a Number on the PM-602 Panic",
    "subheadline": "New research from Pew shows 61 percent of Indian green cards were processed inside the United States in 2024. The administration's new memo treats that pathway as a privilege, not a right.",
    "slug": art2_slug,
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "With 627,000 Indians stuck in the green card backlog and 61% of Indian green cards historically obtained through adjustment of status, the PM-602 memo threatens the single most important pathway Indian professionals have used to build lives in America.",
    "tags": ["green-card", "adjustment-of-status", "pm602", "consular-processing", "pew-research", "backlog", "eb2"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Pew Research Center", "url": "https://www.pewresearch.org/short-reads/2026/06/02/majority-of-new-green-cards-have-gone-to-immigrants-already-living-in-us/"},
        {"name": "Brookings Institution", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"},
        {"name": "USCIS PM-602-0199", "url": "https://www.uscis.gov/policy-manual/updates"},
        {"name": "Murthy Law Firm", "url": "https://www.murthy.com/category/immigrant-family/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy-and-policy/green-card-process-changes-in-us-heres-what-it-means-for-indian-applicants"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": art2_img_url,
    "image_caption": "A United States permanent resident card — the green card that 39,190 Indian nationals obtained through adjustment of status in 2024",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": art2_body,
}

# ============================================================
# Insert all articles
# ============================================================
articles = [art1, art2]
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ Published: {art['slug']}")
    except Exception as e:
        print(f"❌ Failed: {art['slug']}: {e}")

print(f"\n🏁 Done. {len(articles)} articles processed.")
