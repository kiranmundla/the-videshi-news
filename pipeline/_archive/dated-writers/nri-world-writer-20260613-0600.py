#!/usr/bin/env python3
"""NRI World writer — 2026-06-13 06:00 UTC"""
import json, os, uuid, re, requests, io
from datetime import datetime, timezone
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

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


def compress_image(img_bytes, max_width=1200, quality=80):
    if Image is None:
        return img_bytes
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()


def upload_image(slug, img_url):
    """Download, compress, and upload image to Supabase storage."""
    try:
        r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        r.raise_for_status()
        compressed = compress_image(r.content)
        filename = f"{slug}.jpg"
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        }
        resp = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
        if resp.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  📸 Image uploaded: {filename} ({len(compressed)//1024}KB)")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({resp.status_code}): {resp.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Image error: {e}")
    return img_url  # fallback to original URL


now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")


# ═══════════════════════════════════════════════════════
# ARTICLE 1: Consulate Scam Wave Across North America
# ═══════════════════════════════════════════════════════

art1_slug = make_slug("consulate-scam-warnings-nri-north-america-toronto-new-york-bay-area")
art1_id = str(uuid.uuid4())

art1_body = """Indian diplomatic missions in Toronto, New York, and San Francisco have issued a coordinated volley of fraud advisories in the past week, warning diaspora communities about a surge in phone scams impersonating consular officials. The pattern is the same across all three cities: callers claim to represent the Indian Consulate, reference visa or immigration issues, and demand money or personal information. What is new is the scale, the sophistication, and the fact that three missions felt compelled to speak up almost simultaneously.

## Toronto: The Freshest Warning

The Consulate General of India in Toronto published its advisory on June 10, flagging a wave of spoofed calls targeting Indians in Canada. Scammers are posing as consular officials and contacting people about their Canadian visas, permanent residency status, immigration paperwork, and even job offers — none of which fall under the consulate's jurisdiction.

"This Consulate does not deal with these matters," the mission stated flatly, urging recipients to hang up and report the calls to the Canadian Anti-Fraud Centre at 1-888-495-8501.

The advisory made a point of clarifying the consulate's actual mandate: passports, police clearance certificates, OCI cards, attestation, and powers of attorney. Official communication, the mission stressed, originates only from email addresses ending in @mea.gov.in. And consular officials never demand payments over the phone.

## New York: A Personal Plea from the Consul General

In New York, Consul General Binaya S. Pradhan went a step further, recording a video advisory on the scam threat. "Despite repeated advisories, these fraudulent calls continue," Pradhan said. "The consulate or Indian embassy never makes such calls asking for personal information, passport details or money."

He also warned against "unscrupulous agents charging exorbitant fees" — a reference to a parallel problem in the diaspora, where unlicensed immigration consultants exploit confusion and anxiety to charge thousands of dollars for services that are either unnecessary or entirely fraudulent.

The New York advisory came days after the Indian Embassy in Myanmar confirmed the repatriation of 32 Indian nationals who had been trapped in scam compounds in the Myawaddy region — a grim reminder of how fraud targeting Indians operates on a global continuum, from phone spoofing in North America to labour trafficking in Southeast Asia.

## Bay Area: Immigration Anxieties Exploited

In the San Francisco Bay Area, Indian community organisations have reported their own spike in scam calls. According to Pravasi Samwad, fraudsters are using spoofed local numbers — not international ones — to target Indian-origin residents, exploiting the heightened anxiety around immigration enforcement and policy changes under the current US administration.

The Bay Area scams follow a familiar playbook: callers claim there is a problem with the recipient's immigration status, then pivot to demanding immediate payment to "resolve" the issue. The use of local caller IDs makes the calls harder to dismiss and easier to fall for, particularly among older community members or recent immigrants.

## Why Now?

The timing is not coincidental. Geopolitical tensions, rupee depreciation, tighter visa regimes in Canada and the United States, and widespread media coverage of immigration crackdowns have all created fertile ground for scammers. Fear is the currency they trade in, and the current news cycle is handing them plenty of raw material.

For NRIs across North America, the advice from all three consulates converges on the same points: Indian diplomatic missions will never call to demand money or personal details. Official communication uses verified government email domains. Any suspicious call should be reported immediately to local anti-fraud authorities and the nearest Indian mission.

The consulate in Toronto summed it up with characteristic diplomatic understatement: "They are advised not to reveal any personal information or transfer any money in response to such calls." It is a sentence that should not need saying. That it does, across three cities and three time zones, tells you something about the scale of the problem."""

art1_image_url = "https://images.pexels.com/photos/7821750/pexels-photo-7821750.jpeg?auto=compress&cs=tinysrgb&w=1200"

# ═══════════════════════════════════════════════════════
# ARTICLE 2: NYIFF 2026 — Indian Indie Cinema in Manhattan
# ═══════════════════════════════════════════════════════

art2_slug = make_slug("nyiff-2026-indian-film-festival-manhattan-nawazuddin-dil-chahta-hai")
art2_id = str(uuid.uuid4())

art2_body = """For a week every June, a small cinema in Manhattan's East Village becomes arguably the most important screen for Indian independent cinema in the Western hemisphere. The New York Indian Film Festival — NYIFF — returns for its 26th edition from June 19 to 21, and this year's programme reads like a quiet manifesto for everything Bollywood is not.

The lineup, announced by the Indo-American Arts Council (IAAC) in April, features films in fifteen languages — Assamese, Bengali, English, Gujarati, Hindi, Kannada, Kashmiri, Khasi, Malayalam, Marathi, Odia, Punjabi, Sinhalese, Tamil, and Arabic. That linguistic breadth alone is a rebuke to the industry's persistent Hindi-centrism, and it reflects what festival director Aseem Chhabra calls "the evolving language of Indian cinema."

## The Programme

Leading nominations this year are *Baksho Bondi* (Shadowbox), a Bengali feature; *Flowers of Acacia*, a Punjabi drama; *Ha Lyngkha Bneng* (The Elysian Field), in Khasi — a language spoken by fewer than two million people; and *Victoria*, in Malayalam. The dominance of regional cinema in the Best Film race is not an aberration. It is the trend.

"This year's nominated films represent the range and depth of storytelling in India today," Chhabra said. "From human dramas to comedies, and narratives that reflect the angst of Millennials and Gen Z."

The festival will also celebrate the 25th anniversary of Farhan Akhtar's *Dil Chahta Hai*, screening the 2001 film that fundamentally reshaped Hindi cinema's treatment of young, urban friendship. For diaspora audiences who grew up quoting Akash, Sameer, and Sid, the screening is as much nostalgia trip as cinematic event.

## Nawazuddin Returns

Actor Nawazuddin Siddiqui, who has won two NYIFF Best Actor trophies over the years, will attend this edition. He stars in *I'm Not An Actor*, Aditya Kriplani's meta-film that blurs fiction and reality in an examination of fame, identity, and the costs of being perpetually "on."

Siddiqui's presence underscores the festival's dual identity. NYIFF is small enough to feel intimate — the kind of place where you might bump into a director in the lobby — but serious enough to attract genuine talent. Its alumni list includes Anurag Kashyap, Rima Das, Mira Nair, and Shyam Benegal.

## Why It Matters for the Diaspora

Indian film festivals abroad serve a purpose that goes beyond entertainment. For second-generation Indian Americans, they are windows into a country that is more complex, more diverse, and more interesting than the version served up by mainstream Bollywood exports. For recent immigrants, they offer the rare pleasure of seeing their own languages and regions reflected on a big screen in New York City.

NYIFF was founded in 2001 by the Indo-American Arts Council, a non-profit that promotes Indian arts across the United States. Twenty-six years later, the festival's mission feels more urgent than ever. As streaming platforms homogenise content for global audiences and Bollywood doubles down on franchise sequels, NYIFF remains a place where a Khasi-language film from Meghalaya can stand shoulder to shoulder with a Marathi thriller and a Bengali psychological drama.

"This festival has long been a space where India's cinematic legacy meets its most daring futures," said Suman Gollamudi, IAAC's Executive Director. "At 26, we are not just celebrating the past — we are investing in what's next."

Tickets and the full schedule are available at nyiff.us. Screenings take place at the Village East by Angelika in Manhattan."""

art2_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Nawazuddin_Siddiqui_at_IFFK_2021_4_%28cropped%29.jpg/1920px-Nawazuddin_Siddiqui_at_IFFK_2021_4_%28cropped%29.jpg"

# ═══════════════════════════════════════════════════════
# ARTICLE 3: Srinath Ekkad — UAH Engineering Dean
# ═══════════════════════════════════════════════════════

art3_slug = make_slug("srinath-ekkad-university-alabama-huntsville-engineering-dean-indian-origin")
art3_id = str(uuid.uuid4())

art3_body = """Srinath Ekkad, a thermal sciences researcher who earned his undergraduate degree from Jawaharlal Nehru Technological University in Hyderabad, has been named Dean of Engineering at the University of Alabama in Huntsville. His appointment, effective August 5, puts him at the helm of the university's largest college — more than 3,000 students and over a third of total enrolment — at a moment when Huntsville's defence, aerospace, and technology ecosystem is expanding rapidly.

## From Hyderabad to Huntsville

Ekkad's trajectory follows a path familiar to thousands of Indian engineers who left for American graduate schools in the 1990s — but his arc has been unusually steep. After completing his B.Tech in mechanical engineering at JNTU in 1989, he earned a master's from Arizona State University and a PhD from Texas A&M. He spent two years as a senior project engineer at Rolls-Royce Allison in Indianapolis before moving into academia, first at Louisiana State University, then Virginia Tech, where he became the Rolls-Royce Commonwealth Professor for Aerospace Propulsion Systems.

Since 2017, he has led the Department of Mechanical and Aerospace Engineering at North Carolina State University. Under his watch, the department more than doubled its research expenditures, grew its faculty from 46 to 62, and expanded undergraduate enrolment by 25 per cent. Its graduate aerospace programme now ranks in the top 25 nationally, according to U.S. News & World Report.

## Why Huntsville

UAH's College of Engineering is not an ordinary academic unit. Huntsville is home to NASA's Marshall Space Flight Center, the U.S. Army's Redstone Arsenal, and a dense cluster of defence contractors — Lockheed Martin, Northrop Grumman, Boeing, Raytheon — that collectively make the city one of the most concentrated engineering talent markets in the country.

Ekkad arrives as the college prepares to open the Raymond B. Jones Engineering Building, a facility designed to support the next wave of research growth. His background in gas turbine heat transfer, propulsion diagnostics, and thermal management aligns neatly with the aerospace and defence priorities that define Huntsville's economy.

"What sets him apart as a leader is the integration of that research identity with a genuine commitment to the undergraduate experience," said UAH Provost David Puleo. "He has championed experiential and project-based learning as tools not only for student success but for connecting the college to the regional industry ecosystem."

## A Broader Trend

Ekkad's appointment is the latest in a lengthening list of Indian-origin academics ascending to deanships and senior leadership at American universities. Three Indian-origin scholars were recently named University of Florida Research Foundation Professors. Four Indian-origin writers and researchers — Amitav Ghosh, Megha Majumdar, Vivek Narayanan, and Vinod Vaikuntanathan — were named 2026 Guggenheim Fellows. And across the US, Indian-born academics now lead departments and colleges in fields ranging from computer science to public health.

The pipeline that feeds this trend — undergraduate engineering in India, graduate study in the US, postdoctoral work, tenure, and eventually administration — has been running for decades. What has changed is the scale. India now sends more students to the United States than any other country, and the alumni of institutions like JNTU, IIT, and NIT are reaching the age and seniority where deanships and provostships come into view.

For Ekkad, the move is bittersweet. "It was my honour and pleasure to be the head of the Department of Mechanical and Aerospace Engineering at NC State," he said in a farewell message. "I will certainly miss the MAE department, NC State and the Research Triangle Park area. It has been a great ride and many life-long friendships have been carved here."

His last day at NC State is August 1. By August 5, he will be in Huntsville, running a college that sits at the intersection of American defence ambitions and Indian engineering talent — a combination that has quietly been reshaping both."""

art3_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Engineering_Building_UAH.JPG/1280px-Engineering_Building_UAH.JPG"

# ═══════════════════════════════════════════════════════
# BUILD ARTICLES LIST
# ═══════════════════════════════════════════════════════

articles = [
    {
        "id": art1_id,
        "headline": "Three Indian Missions, One Week, Same Warning: Stop Picking Up the Phone",
        "subheadline": "Consulates in Toronto, New York, and the Bay Area are all sounding the alarm on a coordinated wave of phone scams targeting NRIs — and the timing tells you why.",
        "slug": art1_slug,
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "NRIs across North America are being targeted by sophisticated phone scams impersonating Indian consular officials, exploiting immigration anxieties in the current political climate.",
        "tags": ["nri", "diaspora", "scam", "consulate", "safety", "canada", "united-states"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "ANI / LatestLY", "url": "https://www.latestly.com/agency-news/world-news-indian-consulate-in-toronto-warns-nationals-against-phone-scams-by-fraudsters-impersonating-officials-6777791.html"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/12/cgi-toronto-warns-indian-nationals-against-phone-scams/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/12/consul-general-ny-issues-warning-even-as-myanmar-repatriates-32-indian-victims-of-scam/"},
            {"name": "Pravasi Samwad", "url": "https://pravasisamwad.com/pravasi-short-news-12-06-2026-2/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art1_image_url,
        "image_caption": "A smartphone displaying a fraud alert notification",
        "image_attribution": "Pexels",
        "body": art1_body
    },
    {
        "id": art2_id,
        "headline": "Fifteen Languages, Three Days, One Theatre: NYIFF 2026 Is the Most Important Indian Film Festival You Have Never Heard Of",
        "subheadline": "The New York Indian Film Festival returns for its 26th edition next week with Nawazuddin Siddiqui, a Dil Chahta Hai anniversary screening, and films in languages spoken by fewer than two million people.",
        "slug": art2_slug,
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "NYIFF is a cultural lifeline for Indian Americans seeking cinema that reflects the diversity of their homeland — far beyond the Bollywood mainstream — and a launchpad for filmmakers from India's margins.",
        "tags": ["nri", "diaspora", "film-festival", "nyiff", "cinema", "new-york", "culture"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Hollywood Reporter India", "url": "https://www.hollywoodreporterindia.com/news/new-york-indian-film-festival-2026-lineup/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2025/04/22/new-york-indian-film-festival-marks-25th-anniversary-with-powerhouse-lineup/"},
            {"name": "FilmFreeway", "url": "https://filmfreeway.com/NewYorkIndianFilmFestival"},
            {"name": "Indo-American Arts Council", "url": "https://www.iaac.us"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art2_image_url,
        "image_caption": "Nawazuddin Siddiqui at an Indian film festival",
        "image_attribution": "Wikimedia Commons",
        "body": art2_body
    },
    {
        "id": art3_id,
        "headline": "From Hyderabad's JNTU to Alabama's Rocket City: Srinath Ekkad Named Engineering Dean at UAH",
        "subheadline": "A thermal sciences researcher who started at Jawaharlal Nehru Technological University will now lead one of America's most aerospace-connected engineering colleges.",
        "slug": art3_slug,
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Ekkad's appointment extends a pattern of Indian-origin academics reaching the highest rungs of American university leadership, from JNTU undergrad to dean of UAH's 3,000-student engineering college.",
        "tags": ["nri", "diaspora", "academia", "engineering", "achievement", "alabama", "huntsville"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "University of Alabama in Huntsville", "url": "https://www.uah.edu/news"},
            {"name": "NC State College of Engineering", "url": "https://www.engr.ncsu.edu/news/2026/06/04/ekkad-to-step-down-as-mae-department-head/"},
            {"name": "Pravasi Samwad", "url": "https://pravasisamwad.com/pravasi-short-news-12-06-2026-2/"},
            {"name": "Research.com", "url": "https://research.com/u/srinath-v-ekkad"}
        ]),
        "score_total": 68,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art3_image_url,
        "image_caption": "The Engineering Building at the University of Alabama in Huntsville",
        "image_attribution": "Wikimedia Commons",
        "body": art3_body
    }
]

# ═══════════════════════════════════════════════════════
# UPLOAD IMAGES & INSERT ARTICLES
# ═══════════════════════════════════════════════════════

for art in articles:
    try:
        # Upload image to Supabase storage
        final_url = upload_image(art["slug"], art["image_url"])
        art["image_url"] = final_url

        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
