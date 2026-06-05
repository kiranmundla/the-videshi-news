#!/usr/bin/env python3
"""Immigration writer — 2026-06-05 00:58 PDT run"""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path

# Pillow for image compression
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
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
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
    """Download image, compress, upload to Supabase storage bucket 'article-images'."""
    print(f"  Downloading image: {img_url[:80]}...")
    r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=30)
    r.raise_for_status()

    content_type = r.headers.get("Content-Type", "")
    if not content_type.startswith("image/"):
        print(f"  ⚠ Not an image (Content-Type: {content_type})")
        return None

    raw_bytes = r.content
    if len(raw_bytes) < 5000:
        print(f"  ⚠ Image too small ({len(raw_bytes)} bytes), skipping")
        return None

    compressed = compress_image(raw_bytes)
    print(f"  Compressed: {len(raw_bytes)} → {len(compressed)} bytes")

    # Upload to Supabase storage
    upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    upload_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    up = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
    if up.status_code in (200, 201):
        public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✅ Uploaded: {public_url}")
        return public_url
    else:
        print(f"  ❌ Upload failed ({up.status_code}): {up.text[:200]}")
        return None


now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")


# ─────────────────────────────────────────────────
# IMAGE SOURCING
# ─────────────────────────────────────────────────

print("=" * 60)
print("IMAGE SOURCING")
print("=" * 60)

# Article 1: Day-1 CPT crackdown — international students on campus
print("\n--- Article 1: Day-1 CPT image ---")
img1_url = "https://images.pexels.com/photos/6147148/pexels-photo-6147148.jpeg?auto=compress&cs=tinysrgb&w=1200"
art1_id = str(uuid.uuid4())
art1_slug = make_slug("day-1-cpt-escape-hatch-closing-indian-h1b-lottery")
img1_filename = f"{art1_slug}.jpg"
img1_final = upload_to_supabase(img1_url, img1_filename)
img1_attribution = "Pexels"
img1_caption = "International students on a university campus — thousands rely on Day-1 CPT programs to stay employed after losing the H-1B lottery"

# Article 2: Brookings pipeline — passport with visa stamps (talent pipeline / visa system)
print("\n--- Article 2: Brookings pipeline image ---")
img2_url = "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&w=1200"
art2_id = str(uuid.uuid4())
art2_slug = make_slug("brookings-talent-pipeline-breaking-f1-h1b-green-card")
img2_filename = f"{art2_slug}.jpg"
img2_final = upload_to_supabase(img2_url, img2_filename)
img2_attribution = "Pexels"
img2_caption = "An open passport displaying visa stamps — each one representing a step in the talent pipeline that Brookings says is narrowing"


# ─────────────────────────────────────────────────
# ARTICLES
# ─────────────────────────────────────────────────

print("\n" + "=" * 60)
print("PUBLISHING ARTICLES")
print("=" * 60)

articles = [
    {
        "id": art1_id,
        "headline": "The Day-1 CPT Escape Hatch Is Closing — and Thousands of Indian Workers Are Still Inside",
        "subheadline": "A proposed DHS rule would gut the graduate re-enrollment pathway that keeps Indian tech professionals employed between H-1B lottery losses, while slashing the grace period that gives them time to plan.",
        "slug": art1_slug,
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Tens of thousands of Indian professionals in the US rely on Day-1 CPT programs as a legal bridge after failing the H-1B lottery. The proposed rule would shut this pathway down, forcing them to leave the country or find another status — with half the time they used to have.",
        "tags": ["day-1-cpt", "f-1", "h-1b", "uscis", "student-visa", "dhs"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/02/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
            {"name": "DHS Proposed Rule - Duration of Status", "url": "https://www.federalregister.gov/documents/2026/05/05/"},
            {"name": "LexBlog - Immigration Attorney Analysis", "url": "https://www.lexblog.com/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": img1_final or "",
        "image_caption": img1_caption,
        "image_attribution": img1_attribution,
        "is_editorial": False,
        "body": """For years, it has been the worst-kept workaround in American immigration: lose the H-1B lottery, enroll in a new master's program, activate Curricular Practical Training on day one, and keep working. The practice, known colloquially as "Day-1 CPT," has sustained tens of thousands of Indian technology professionals who would otherwise have had to pack their desks and book flights home.

That door is about to get a lot harder to walk through.

On May 5, the Department of Homeland Security published a proposed rule that would replace the decades-old "Duration of Status" framework for F-1 student visas with a fixed admission period of up to four years. On its face, the rule is about time limits. In practice, it is a surgical strike against the re-enrollment pipeline that keeps Indian workers in the country between lottery cycles.

## How the Bridge Works — and Why DHS Wants to Burn It

Under the current system, international students are admitted for as long as they maintain valid student status. If an H-1B application is rejected, a worker can enroll in a new academic program, obtain a fresh I-20, and activate CPT — all without leaving the United States or petitioning USCIS for a status extension.

The proposed rule changes the mechanics. Students would receive a fixed four-year admission stamp. Anything beyond that window — including re-enrollment in a new program to access CPT — would require formal USCIS approval. That approval is neither automatic nor fast. In a system where processing times regularly stretch to six months or more, the bureaucratic friction alone could make the pathway unworkable.

"For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorization to continue working,'" said Danielle Goldman, co-founder and CEO of Build, an immigration technology firm, in an analysis published this week.

## Thirty Days Instead of Sixty

Buried in the same proposal is a second cut: the grace period available to F-1 students after their status ends would shrink from 60 days to 30. That may sound like an administrative detail. It is not.

The grace period is the window during which a student who has finished a program or lost OPT employment can arrange a change of status, find a new sponsor, or simply make travel plans. For Indian nationals — who face some of the longest consular wait times in the world — losing half that window compresses an already stressful process into something approaching impossible.

Immigration attorneys warn that the 30-day period would leave insufficient time to file a change-of-status application, receive a receipt notice, and avoid accruing unlawful presence. A single misfiled form or postal delay could turn a compliant visa holder into an overstay statistic.

## The AI Talent Bottleneck

The stakes extend well beyond individual workers. Goldman noted that foreign nationals make up a disproportionate share of the American AI talent pool. Indian professionals working in machine learning, data science, and software engineering are precisely the workers most likely to be caught in the Day-1 CPT squeeze.

"There's no doubt about it that this is going to have a massive impact on the companies that are in desperate need of top talent," Goldman said.

The numbers tell the story. Indian nationals accounted for roughly 72 percent of all H-1B visa approvals in fiscal year 2025. Many of those workers first entered the United States on student visas and used OPT or CPT to bridge the gap before securing employer sponsorship. Cut the bridge, and the pipeline feeding American technology firms starts to dry up.

Companies are already adjusting. Some are exploring cap-exempt H-1B pathways through universities and nonprofits. Others are shifting to O-1 "extraordinary ability" petitions — a route that demands a higher evidentiary bar but sidesteps the lottery entirely. Neither option scales the way Day-1 CPT did.

## What Indian Workers Should Do Now

The rule is still in the public comment period, and immigration advocates are pushing for modifications. But the direction of travel is clear, and Indian professionals currently relying on CPT as a safety net should be planning for a world without it.

Goldman's advice: develop multiple backup plans rather than betting everything on a single pathway. That might mean filing for O-1 status, exploring EB-1A self-petition options, or having a realistic conversation with an employer about sponsorship timelines.

For the thousands of Indians who entered the United States as students, built careers in American technology, and have been cycling through the H-1B lottery year after year, the Day-1 CPT closure is not an abstract policy debate. It is a countdown."""
    },
    {
        "id": art2_id,
        "headline": "Brookings Puts a Number on the Damage — 29 Percent Fewer Student Visas, 1.2 Million in the Green Card Queue",
        "subheadline": "A comprehensive new analysis from the Brookings Institution maps how Trump administration policies are squeezing every segment of the immigrant talent pipeline, from university enrollment to permanent residency.",
        "slug": art2_slug,
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals dominate every segment of the pipeline Brookings describes: the largest group of F-1 students, the highest share of H-1B holders, and the longest green card backlogs. The report's findings are, in effect, a portrait of the Indian-American immigration experience under the current administration.",
        "tags": ["brookings", "f-1", "h-1b", "green-card", "talent-pipeline", "student-visa"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Brookings Institution", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/02/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
            {"name": "Aviation A2Z / DHS Testimony", "url": "https://aviationa2z.com/index.php/2026/06/04/dhs-reveals-massive-demand-for-h-1b-visas-despite-100000-fee/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": img2_final or "",
        "image_caption": img2_caption,
        "image_attribution": img2_attribution,
        "is_editorial": False,
        "body": """The anecdotes have been piling up for months: a Hyderabad engineer whose H-1B premium processing fee ballooned to six figures, a Bengaluru graduate who shelved her American university plans, an EB-2 applicant who has been "current" for years with nothing to show for it. Now the Brookings Institution has done what individual stories cannot — it has put the whole system on a single page and measured the bleeding.

In a research paper published in late May, economists Tara Watson, Matthew Wich, and Johnny Willing document what they call a systematic erosion of the immigrant talent pipeline under the Trump administration. Their findings land like a body blow: a projected 29 percent decline in F-1 student visa issuances, a green card applicant backlog estimated at roughly 1.2 million people, and policy changes at every link in the chain from classroom to corner office.

## The Student Visa Collapse

The most striking number is the F-1 decline. Using newly released State Department data, the Brookings team projects that student visa issuances fell 29 percent in 2025 compared to the prior year. That is not a dip. That is an enrollment cliff.

For Indian students — who have been surging toward becoming the largest foreign student population in America, with a 20 percent increase in visa issuances last year alone — the reversal is especially jarring. A record 125,000 visas were issued to Indian students in the most recent year of growth. How many will be issued this year is suddenly an open question.

The causes are layered. The DHS proposal to replace Duration of Status with fixed four-year admission periods has injected uncertainty into the decision calculus for prospective students. Rising anti-immigrant rhetoric has made parents in India and elsewhere think twice. And the practical difficulties — longer consular wait times, canceled appointments in Hyderabad and Chennai, visa revocations based on years-old arrest records — have turned the application process into an obstacle course.

## The H-1B Squeeze

If the student pipeline is the entry point, the H-1B program is the bottleneck. Brookings documents two major policy shifts that are reshaping it.

First, the $100,000 fee. Imposed last September, the fee was designed to prevent employers from "artificially suppressing wages" using foreign labor. The initial uptake was modest — Brookings noted that early reports showed only about 85 companies had paid. But by the time DHS Secretary Markwayne Mullin testified before the Senate Appropriations Subcommittee on June 2, the picture had changed dramatically: more than 200,000 out of 286,000 FY2026 applicants had paid the fee, choosing 15-day processing over a 7.5-month standard wait.

The fee remains under legal challenge — the U.S. Chamber of Commerce and others have filed suits that are still working through the courts. But the market has already rendered its verdict: employers will pay whatever it takes.

Second, the lottery itself has been reweighted. A final DHS rule published in late December shifted H-1B selection from random to wage-weighted, favoring higher-paid workers. The rule took effect on February 27 and applies to the FY2027 lottery, which opened on March 4 and hit its cap just 25 days later on March 31. For early-career workers and those in lower-paying sectors — including many fresh Indian graduates — the new weighting makes an already improbable lottery even harder to win.

## The Green Card Wall

Even for those who clear the H-1B hurdle, the destination — a green card — remains effectively unreachable for most Indians. Brookings estimates the total employment-based green card backlog at approximately 1.2 million applicants. Indian nationals, subject to a per-country cap that limits them to the same annual allocation as applicants from Iceland, account for the overwhelming majority of that queue.

The report does not editorialize about the per-country cap. It does not need to. The math speaks for itself: at current processing rates, an Indian-born EB-2 applicant filing today could wait decades. The system is not slow. It is effectively frozen.

## What the Pipeline Metaphor Misses

Brookings frames the analysis as a talent pipeline — students flow in, workers move through, permanent residents come out the other end. The metaphor is useful but incomplete. What it misses is that each segment of the pipeline is now being squeezed simultaneously, and the effects compound.

A student who decides not to come to America is also a future H-1B applicant who never materializes, a green card applicant who never enters the queue, and a potential entrepreneur who builds a company somewhere else. Brookings cites research showing that high-skill immigrants start businesses at high rates, contribute more in taxes than they consume in benefits, and strengthen the firms and universities they join. Each lost applicant is a multiplier effect that never happens.

For the Indian diaspora, this is personal arithmetic. The software engineer in Sunnyvale waiting for a green card, the master's student in Austin deciding whether to stay, the parent in Pune wondering whether the American dream is still worth the application fee — they are all points on the same pipeline, and Brookings has shown that the pipe is narrowing at every joint.

The research paper runs to 28 minutes of reading. The conclusion can be stated in one sentence: the United States is making it harder for talented people to come, stay, and contribute, and it is doing so at every stage of the process at once."""
    },
]

for art in articles:
    # Skip articles with no image
    if not art["image_url"]:
        print(f"⚠ No image for {art['slug']} — publishing without image")
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ Published: {art['headline'][:80]}...")
        print(f"   Slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
