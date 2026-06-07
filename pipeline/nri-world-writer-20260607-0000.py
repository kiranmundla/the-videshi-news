#!/usr/bin/env python3
"""NRI World Writer — 2026-06-07 batch"""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path

# ── env ──────────────────────────────────────────────────────────────
env_file = Path.home() / ".env.supabase"
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
STORAGE_HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
}

now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")

def compress_image(img_bytes, max_width=1200, quality=80):
    from PIL import Image
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
    """Download image, compress, upload to Supabase storage."""
    r = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=30)
    r.raise_for_status()
    compressed = compress_image(r.content)
    size_kb = len(compressed) / 1024
    print(f"  Image: {size_kb:.0f} KB after compression")

    upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    up_headers = {
        **STORAGE_HEADERS,
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    resp = requests.post(upload_url, headers=up_headers, data=compressed, timeout=30)
    if resp.status_code not in (200, 201):
        # Try PUT for upsert
        resp = requests.put(upload_url, headers=up_headers, data=compressed, timeout=30)
    resp.raise_for_status()
    public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
    return public_url


# ── ARTICLE 1: Yoga Day 2026 ─────────────────────────────────────────

art1_id = str(uuid.uuid4())
art1_slug = make_slug("yoga-day-lincoln-memorial-times-square-diaspora-nagendra")
art1_headline = "Modi's Yoga Guru Will Stand at Times Square on June 21. The Diaspora Arranged the Invitation."
art1_subheadline = "Padma Shri HR Nagendra will headline the biggest International Day of Yoga celebrations in the US — at the Lincoln Memorial and Times Square. Behind the scenes, a decade-long diaspora network made it happen."

art1_body = """The Indian Embassy in Washington has announced that the Lincoln Memorial will host International Day of Yoga celebrations on June 19 — the first time the monument synonymous with American democracy will double as a stage for one of India's most visible cultural exports.

Two days later, on June 21 — the official International Day of Yoga — thousands are expected to gather at Times Square in New York for the flagship event, headlined by Padma Shri HR Nagendra, the 83-year-old yoga scholar who personally guides Prime Minister Narendra Modi's practice and serves as president of Bengaluru's S-VYASA University.

The dual-city programme amounts to the most ambitious Yoga Day celebration the Indian diaspora has assembled in the United States. And the infrastructure behind it — built over a decade by a handful of Indian-American organisations with deep diplomatic ties — reveals how a network of community leaders has quietly turned an annual UN observance into a permanent fixture of American public life.

## A three-day retreat before the main event

Before the Times Square spectacle, Nagendra will inaugurate a three-day Yoga and Wellness Retreat at the YO1 Longevity and Health Resort in Monticello, New York, running from June 12 to 14. The programme covers yoga sessions, meditation, and lectures on stress management, healthy ageing, and holistic wellness.

The speaker list signals an effort to bridge traditional yoga practice with Western clinical credibility. Dr Samin K Sharma, Director of Interventional Cardiology at Mount Sinai Hospital in New York, is confirmed alongside Raj Bansal, founder of one of the nation's Accountable Care Organisations. Nagendra will be accompanied by S-VYASA Vice Chancellor NK Manjunath.

This year's theme, "Yoga for Healthy Aging," reflects a pivot from general awareness to targeted health outcomes — positioning yoga not as a cultural curiosity but as an evidence-based intervention for an ageing global population.

## The organisations behind the curtain

The visit was organised at the invitation of the Rajasthan Association of North America (RANA), alongside BRUHUD NY Seniors and Jaipur Foot USA — a constellation of Indian diaspora groups that have worked for years to embed yoga into American institutional life.

Central to this effort is Prem Bhandari, Chairman of Jaipur Foot USA and President of RANA New York, who has spent over a decade organising yoga programmes at venues including the United Nations headquarters and Capitol Hill. Nagendra acknowledged Bhandari's role directly, noting that his efforts had helped bring "the timeless wisdom of yoga to people from all walks of life."

Bhandari, for his part, framed the visit as a milestone. "After a decade of promoting yoga across the US with diplomatic missions and institutions, we are deeply honoured to welcome Padma Shri HR Nagendra to New York, whose visit will strengthen yoga education, research, and India-US cultural bonds."

## Soft power, institutionalised

The Times Square Yoga Day event has become, arguably, the single most visible annual demonstration of Indian soft power in the United States. Its origins trace to December 2014, when the United Nations General Assembly passed a resolution designating June 21 as International Day of Yoga — a proposal driven by Modi at the UNGA earlier that year. The inaugural global observance was held in 2015.

Since then, India's Ministry of External Affairs has worked with consulates worldwide to make Yoga Day a flagship element of its public diplomacy. Times Square has emerged as the most prominent annual venue. That the Prime Minister's personal yoga guru will stand at its centre on June 21 carries a symbolism unlikely to be lost on either Delhi or Washington.

S-VYASA, founded in Bengaluru, is one of India's leading institutions dedicated to integrating yoga with modern science. It offers graduate and postgraduate programmes and conducts research into yoga's therapeutic applications. Nagendra's previous visit to New York, in 2018, also facilitated by Bhandari, is cited by the university as a milestone in its international outreach.

For the estimated 4.4 million Indian Americans, Yoga Day has evolved from a diplomatic gesture into something more practical: a platform where diaspora organisations demonstrate their capacity to shape American wellness culture from the inside. The Lincoln Memorial event — placing yoga on the same steps where Martin Luther King Jr. delivered his most famous speech — makes the ambition explicit."""

# Image: Times Square Yoga from Wikimedia Commons
art1_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Yoga_at_Times_Square%2C_New_York_City_in_2015.jpg/1200px-Yoga_at_Times_Square%2C_New_York_City_in_2015.jpg"
art1_image_caption = "Yoga practitioners at Times Square in New York City during International Day of Yoga celebrations"
art1_image_attribution = "Wikimedia Commons"


# ── ARTICLE 2: Bobby Mukkamala — AMA's First Indian-Heritage President ──

art2_id = str(uuid.uuid4())
art2_slug = make_slug("bobby-mukkamala-ama-first-indian-heritage-president-flint")
art2_headline = "Bobby Mukkamala Survived Brain Surgery and Won the AMA Presidency. His Next Fight Is American Healthcare Itself."
art2_subheadline = "The first physician of Indian heritage to lead the American Medical Association is a brain tumour survivor from Flint, Michigan — and the unlikely face of a diaspora that now shapes US health policy from the top."

art2_body = """A few months before he was inaugurated as the 180th president of the American Medical Association, Bobby Mukkamala did not know whether the ceremony would happen at all. Last November, the otolaryngologist from Flint, Michigan, was diagnosed with an 8-centimetre brain tumour. Surgery followed at the Mayo Clinic. Recovery was uncertain.

"As I lay in recovery from brain surgery, with tubes and wires monitoring my every movement, this night — this honour — this opportunity to improve healthcare seemed a very distant dream," Mukkamala told the audience at his inauguration in June 2025. He was the first physician of Indian heritage to lead the AMA in its 178-year history.

One year into his presidency, Mukkamala has become the most prominent Indian American in US healthcare policy — and his agenda, shaped in no small part by the city that raised him, reaches well beyond the community that celebrates him.

## Flint, and what it teaches

Mukkamala's parents moved from India to Michigan in the early 1970s, both physicians, and settled in Flint — a city that would become synonymous with American infrastructure failure. Bobby grew up there, graduated from the University of Michigan Medical School, completed his residency at Loyola University Medical Center in Chicago, and then did something unusual: he went back.

He and his wife, Nita Kulkarni, an obstetrician-gynaecologist, established a private practice in Flint and set up the Endowed Health Professions Scholarships at the University of Michigan, Flint, in 2012. When the Flint water crisis broke, Mukkamala chaired the Community Foundation of Greater Flint, directing resources toward mitigating lead exposure in children. He later partnered with his son to 3D-print N95-style masks for healthcare workers during the COVID-19 pandemic.

"I believe physicians are built for moments like this," he said in his inaugural address. "We are problem solvers. We are advocates. We are resilient."

## The community infrastructure that mirrors it

Mukkamala's ascent is not an isolated data point. Indian Americans now constitute a disproportionate share of the US physician workforce — by some estimates, one in seven practising doctors in the country is of Indian origin. And beneath the individual milestones, a dense institutional network has formed.

In Chicago, the Indian American Medical Association of Illinois (IAMA-IL) and its charitable arm, the Indian American Charitable Foundation (IAMA-CF), have run a free clinic for over three decades. The Seva Community Health Clinic, as it is known, expanded in 2025-2026 to operate six days a week, added a dedicated Women's Health clinic, launched telemedicine capabilities, and began regular community health seminars.

At the association's annual banquet in April 2026, where Mukkamala appeared as chief guest, 375 physicians and families gathered at Ashton Place in Willowbrook, Illinois. Dr Samir Shah, president of IAMA-CF, outlined the clinic's transformation. The keynote came from Dr Subrahmanyam Dravida, president of EKAL-USA, who drew lines between medical service in Chicago's underserved neighbourhoods and rural education in India through Ekal Vidyalaya's initiatives.

The awards that night — a Lifetime Achievement Award for Dr Thomas John, a Distinguished Physician Award for Dr Ngozi Ezike — captured a community that has moved beyond professional networking into structured civic infrastructure.

## The policy fights ahead

Mukkamala's AMA presidency has focused on what he calls the structural barriers of American healthcare: physician shortages, burnout, the bureaucratic weight of prior authorisation, and the erosion of independent practice. In a two-part interview with Medical Economics published this week, he was blunt about the scale of the problem.

"There are tremendous gaps in our healthcare system that require our attention," he said. "It all starts with timely access to care."

He has also positioned himself as an advocate for AI in medicine — with caveats about physician autonomy — and has pushed for reforms to Medicare physician reimbursement, which has failed to keep pace with inflation for over two decades.

As chair of the AMA's Substance Use and Pain Care Task Force, Mukkamala championed evidence-based approaches to the opioid epidemic long before the presidency. His appointment as a trustee of the C.S. Mott Foundation, headquartered in Flint, added a philanthropic dimension to an already crowded portfolio.

## What the milestone means

For the Indian diaspora, Mukkamala's presidency carries a significance that extends beyond symbolism. Indian American physicians have long been essential to the American healthcare system — particularly in rural and underserved areas where other doctors decline to practise. The AMA presidency puts one of them at the centre of the policy conversation, not just the exam room.

"The son of two immigrant physicians," the AMA noted in its announcement, "Dr Mukkamala was inspired to go into medicine and return to his hometown of Flint to serve the community that welcomed his family decades before."

It is a sentence that could describe thousands of Indian American doctors. That one of them now leads the most powerful medical organisation in the country suggests the diaspora's influence in American healthcare is no longer peripheral. It is structural."""

# Image: Bobby Mukkamala at USDA event from Wikimedia Commons  
art2_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/20260211-USDA-OSEC-CDP-1201_%2855091006480%29.jpg/1200px-20260211-USDA-OSEC-CDP-1201_%2855091006480%29.jpg"
art2_image_caption = "AMA President Bobby Mukkamala delivers remarks at a health policy event in Washington, DC"
art2_image_attribution = "Wikimedia Commons"


# ── Upload images & publish ──────────────────────────────────────────

articles = [
    {
        "id": art1_id,
        "headline": art1_headline,
        "subheadline": art1_subheadline,
        "slug": art1_slug,
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian diaspora organisations in the US have built a decade-long infrastructure to embed yoga in American public life — from the UN to Capitol Hill to Times Square.",
        "tags": ["nri", "diaspora", "yoga", "cultural-diplomacy", "yoga-day-2026"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "NewKerala / ANI", "url": "https://www.newkerala.com/news/a/yoga-lincoln-memorial-indian-embassy-brings-international-day-588.htm"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/06/indian-embassy-to-celebrate-international-day-of-yoga-2026-at-lincoln-memorial/"},
            {"name": "LatestLY", "url": "https://www.latestly.com/world/yoga-at-lincoln-memorial-indian-embassy-brings-international-day-of-yoga-2026-to-iconic-us-landmark-6653832.html"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "",   # filled after upload
        "image_caption": art1_image_caption,
        "image_attribution": art1_image_attribution,
        "is_editorial": False,
        "body": art1_body,
        "_source_image": art1_image_url,
    },
    {
        "id": art2_id,
        "headline": art2_headline,
        "subheadline": art2_subheadline,
        "slug": art2_slug,
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Bobby Mukkamala's AMA presidency represents the structural influence Indian American physicians have built in US healthcare — from free clinics to national policy.",
        "tags": ["nri", "diaspora", "healthcare", "bobby-mukkamala", "ama", "indian-american-physicians"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "American Medical Association", "url": "https://www.ama-assn.org/press-center/press-releases/bobby-mukkamala-md-inaugurated-180th-ama-president"},
            {"name": "Medical Economics", "url": "https://www.medicaleconomics.com/view/bobby-mukkamala-m-d-sworn-in-as-180th-ama-president"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/07/service-to-underserved-seva-indian-american-physicians-celebrate-legacy-leadership-and-harmony-in-healing/"},
            {"name": "Medical Dialogues", "url": "https://medicaldialogues.in/medical-news/indian-origin-doctor-bobby-mukkamala-to-head-us-medical-body-140143"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "",   # filled after upload
        "image_caption": art2_image_caption,
        "image_attribution": art2_image_attribution,
        "is_editorial": False,
        "body": art2_body,
        "_source_image": art2_image_url,
    },
]

for art in articles:
    source_img = art.pop("_source_image")
    filename = f"{art['id']}.jpg"
    try:
        print(f"\n📸 Uploading image for: {art['headline'][:60]}...")
        public_url = upload_to_supabase(source_img, filename)
        art["image_url"] = public_url
        print(f"  ✅ Image uploaded: {public_url[:80]}...")
    except Exception as e:
        print(f"  ⚠️ Image upload failed: {e}")
        # Use original URL as fallback
        art["image_url"] = source_img

    try:
        sb_post("p2_articles", art)
        print(f"✅ Published: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\n🎯 Done. {len(articles)} articles processed.")
