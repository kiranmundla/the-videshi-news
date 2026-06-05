#!/usr/bin/env python3
"""Immigration writer — 2026-06-05 12:00 UTC run"""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# ── Env ──────────────────────────────────────────────────────────────
for env_file in [Path.home() / ".env.supabase", Path.home() / "workspace" / ".env.supabase"]:
    if env_file.exists():
        for line in env_file.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
        break

for env_file in [Path.home() / "workspace" / ".env.pexels", Path.home() / ".env.pexels"]:
    if env_file.exists():
        for line in env_file.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
        break

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def compress_image(img_bytes, max_width=1200, quality=80):
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
    """Download image, compress, and upload to Supabase storage."""
    r = requests.get(img_url, headers=UA, timeout=30)
    r.raise_for_status()
    raw = r.content
    compressed = compress_image(raw)
    size_kb = len(compressed) / 1024
    print(f"  Image: {size_kb:.0f} KB after compression")
    if size_kb < 10:
        print("  ⚠ Image too small, skipping upload")
        return None

    upload_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    resp = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
    if resp.status_code in (200, 201):
        public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✅ Uploaded: {public_url}")
        return public_url
    else:
        print(f"  ❌ Upload failed: {resp.status_code} {resp.text[:200]}")
        # Try PUT instead
        resp2 = requests.put(upload_url, headers=upload_headers, data=compressed, timeout=30)
        if resp2.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✅ Uploaded (PUT): {public_url}")
            return public_url
        print(f"  ❌ PUT also failed: {resp2.status_code}")
        return None

def validate_image_url(url):
    """Verify the URL returns a valid image."""
    try:
        r = requests.head(url, headers=UA, timeout=15, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if 'image' in ct and cl > 5000:
            return True
        # Try GET if HEAD doesn't give Content-Length
        if 'image' in ct:
            r2 = requests.get(url, headers=UA, timeout=15, stream=True)
            chunk = r2.raw.read(6000)
            return len(chunk) >= 5000
    except Exception as e:
        print(f"  ⚠ Validation error: {e}")
    return False


now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")


# ══════════════════════════════════════════════════════════════════════
# ARTICLE 1: NVIDIA's H-1B Hiring Surge
# ══════════════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_slug = make_slug("nvidia-h1b-hiring-surge-big-tech-retreats-indian-professionals")

art1_body = """NVIDIA secured nearly 1,200 visa certifications for foreign worker hiring in the first two quarters of fiscal year 2026, a 20 per cent year-on-year increase. In the same period, Alphabet and Amazon slashed their visa certifications by roughly 40 per cent. The divergence tells a story about who is winning the AI race — and who is paying for their caution with talent.

## The Numbers That Matter

The data, drawn from Department of Labor filings, reveals a stark bifurcation in the technology sector's appetite for skilled foreign workers. NVIDIA, riding an unprecedented demand surge for its AI accelerators, is not just maintaining its H-1B pipeline — it is actively expanding it. The company's GPU architecture has become the de facto foundation of every serious AI training operation on the planet, and it needs the engineers to match.

Meanwhile, the broader tech industry is contracting. More than 123,000 technology workers were laid off in 2026 alone, according to Layoffs.fyi tracking data. That retrenchment has collided with a political environment increasingly hostile to work visas, creating a two-speed labour market: AI-adjacent firms hiring aggressively, and everyone else pulling back.

## Why Indians Are the Biggest Beneficiaries

Indian professionals secured between 71 and 73 per cent of all H-1B visas issued by the United States in recent fiscal years, a dominance that shows no sign of fading. NVIDIA's hiring surge is disproportionately channeled through Indian talent — both in its Santa Clara headquarters and its expanding operations in Bangalore and Hyderabad.

The company's workforce needs are concentrated in precisely the disciplines where Indian graduate programmes have produced deep bench strength: chip design, CUDA programming, machine learning infrastructure, and systems engineering. A single NVIDIA GPU architect can command a total compensation package north of $400,000 — well above the new weighted H-1B lottery thresholds that favour higher-wage positions.

That last point matters. The Trump administration's weighted selection rule, effective since February 2026, assigns lottery entries based on wage levels. Level IV positions get four entries; Level I gets one. NVIDIA's compensation structure means its H-1B petitions are almost exclusively in the top tiers — making them far more likely to survive the new lottery than petitions from IT services firms paying Level I wages.

## The Retreat Elsewhere

Alphabet's 40 per cent reduction in visa certifications reflects a broader reorientation. The company has been cutting headcount and shifting investment toward AI infrastructure that requires fewer, more senior engineers. Amazon's parallel pullback tracks with its efficiency drive under CEO Andy Jassy, who has been consolidating teams and reducing external hiring.

The pattern extends beyond the two giants. Across the technology sector, companies that are not directly building AI infrastructure — those in cloud services, enterprise software, digital advertising — are tightening their immigration pipelines. The Brookings Institution reported this week that F-1 student visa issuances to India dropped 29 per cent under the current policy environment, threatening the upstream pipeline that feeds H-1B hiring.

## What This Means for Indian H-1B Holders

The polarisation creates a paradox for Indian professionals in the United States. If you work in AI — particularly in hardware, training infrastructure, or foundational model engineering — demand for your skills has never been higher, and companies like NVIDIA will fight through any regulatory obstacle to keep you. If you work in traditional software engineering, QA, or IT services, the landscape has shifted against you on two fronts: employers are hiring fewer people, and the visa system now penalises lower-wage petitions.

For Indian graduates weighing their options, the signal is clear. The H-1B programme is not shrinking uniformly; it is concentrating around a smaller number of high-value employers willing to pay premium wages and navigate an increasingly complex regulatory environment. NVIDIA is the most visible example, but similar patterns are emerging at companies like OpenAI, Anthropic, and Tesla's AI division.

The question for the Indian diaspora is whether this concentration is sustainable — or whether it creates a fragile dependency on a handful of companies whose fortunes are tied to a single technology cycle. For now, the engineers with NVIDIA on their visa petitions are the safest people in American immigration. Everyone else is watching the floor move beneath them.
"""

# Image: NVIDIA Headquarters (Wikimedia Commons)
art1_img_source = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/NVIDIA_Headquarters.jpg/1280px-NVIDIA_Headquarters.jpg"
print("Article 1: Sourcing image — NVIDIA Headquarters from Wikimedia Commons")
if validate_image_url(art1_img_source):
    art1_img = upload_to_supabase(art1_img_source, f"{art1_id}.jpg")
else:
    print("  ⚠ NVIDIA HQ image validation failed, trying Jensen Huang Wikipedia photo")
    art1_img_source = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Jen-Hsun_Huang_2025.jpg/800px-Jen-Hsun_Huang_2025.jpg"
    art1_img = upload_to_supabase(art1_img_source, f"{art1_id}.jpg") if validate_image_url(art1_img_source) else None

art1 = {
    "id": art1_id,
    "headline": "NVIDIA Is Hiring More H-1B Workers Than Ever. The Rest of Big Tech Is Walking Away.",
    "subheadline": "The chipmaker's visa certifications rose 20 per cent while Alphabet and Amazon cut theirs by 40. For Indian professionals, the AI boom is creating a two-speed immigration market.",
    "slug": art1_slug,
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian professionals secured 71-73% of all H-1B visas and are the primary beneficiaries of NVIDIA's hiring surge. The weighted H-1B lottery now favours the high-wage AI positions NVIDIA fills, while penalising lower-wage IT services roles that employ millions of Indians.",
    "tags": ["h1b", "nvidia", "ai", "tech-hiring", "indian-professionals", "weighted-lottery"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Inshorts", "url": "https://inshorts.com/en/news/nvidia-expands-h-1b-hiring-amid-job-loss-reports-due-to-ai-1780419265443"},
        {"name": "Brookings Institution", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"},
        {"name": "Daily Caller (Chip Roy bill / OPT data)", "url": "https://dailycaller.com/2026/06/04/chip-roy-h1b-abuses-white-collar-jobs/"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": art1_img or "",
    "image_caption": "NVIDIA headquarters in Santa Clara, California — the epicentre of AI-driven H-1B hiring",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": art1_body.strip(),
}


# ══════════════════════════════════════════════════════════════════════
# ARTICLE 2: Laid-Off H-1B Workers and the 60-Day Clock
# ══════════════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_slug = make_slug("110000-tech-layoffs-h1b-60-day-clock-survival-guide-indian-workers")

art2_body = """More than 110,000 technology workers were laid off in the first quarter of 2026 alone, across 144 companies. For American citizens and green card holders, a layoff is a financial setback. For the thousands of Indian professionals on H-1B visas among them, it is a legal emergency with a hard deadline they cannot afford to misunderstand.

## The Clock Starts Earlier Than You Think

The 60-day grace period under 8 CFR 214.1(l)(2) is the single most important — and most misunderstood — regulation in an H-1B worker's life after a layoff. The clock begins on the last actual day of employment, not when severance payments end, not when COBRA benefits expire, and not when HR completes offboarding paperwork.

This distinction has tripped up thousands of workers. A generous severance package — four months of pay, continued health benefits, career coaching — can create the illusion that visa status is similarly extended. It is not. If your employment termination date is June 1, your 60-day window closes on July 31, regardless of whether severance cheques continue arriving in August.

Miss that deadline and the consequences are severe. Accruing unlawful presence can trigger a three-year bar from re-entry to the United States if it stretches past 180 days, or a ten-year bar beyond a year. For someone who has spent a decade building a career, buying a home, and enrolling children in American schools, those bars are effectively permanent exile.

## Four Bridges, Each With a Weight Limit

Immigration attorneys and a recently published strategic guide from StudentEB5 outline four primary bridging options for H-1B workers who cannot secure a new employer within the grace period. Each has trade-offs that Indian workers should understand before committing.

**H-1B portability** remains the fastest path if a new employer files a non-frivolous petition on your behalf. You can begin working for the new employer as soon as USCIS receives the petition — no waiting for approval. The catch is that you need an employer willing to sponsor you, and in a market shedding 110,000 jobs in a single quarter, those offers are harder to come by.

**B-1/B-2 change of status** via Form I-539, filed within the grace period, halts the accumulation of unlawful presence and preserves the right to remain in the country while searching for work. The critical limitation: you cannot earn income while on B-1/B-2 status. For a single-income household — common among Indian H-1B families where the spouse holds an H-4 — this means surviving on savings alone.

**H-4 dependent status** is available to workers whose spouses hold a valid H-1B. If the principal spouse has an approved I-140, the H-4 holder can also obtain an Employment Authorisation Document, though USCIS processing times for H-4 EADs have stretched to 6-12 months in recent cycles, and the automatic 540-day EAD extension only applies to timely renewal filings.

**Cap-exempt employment** at universities, non-profit research organisations, or affiliated institutions offers an immediate transfer pathway that bypasses the annual H-1B lottery entirely. The positions tend to pay less than private sector equivalents, but for workers facing a ticking clock, the certainty can outweigh the salary cut.

## The EB-5 Escape Hatch

For those with capital — and the 2022 Reform and Integrity Act set the minimum at $800,000 for Targeted Employment Area investments — the EB-5 Immigrant Investor Program removes employer dependence from the equation permanently. H-1B workers in lawful status can file Form I-526E and Form I-485 concurrently. Once the I-485 is pending, the applicant enters a period of authorised stay and can remain in the United States indefinitely while the green card is adjudicated.

Two deadlines sharpen the urgency. The grandfathering provision under the RIA expires on September 30, 2026, protecting investors who file before that date from the risk of the Regional Centre programme not being reauthorised. The minimum TEA investment amount is also projected to increase to between $940,000 and $950,000 in early 2027, based on inflation adjustments.

The EB-5 route is not available to most laid-off H-1B workers — $800,000 is serious capital. But for senior engineers, directors, and executives who have accumulated equity from years at high-growth companies, it is the only immigration pathway that does not require another employer to vouch for them.

## What This Means for the Indian Diaspora

The Indian community is disproportionately exposed. Indians are the largest single national group in the H-1B programme and are heavily concentrated in the technology sector that is shedding jobs. The combination of a hostile regulatory environment — the weighted lottery, the proposed OPT restrictions, tighter student visa rules — and a contracting job market creates a vice that is squeezing Indian workers from both sides.

The practical advice from immigration attorneys is blunt: know your exact employment termination date, not your severance end date. File for a change of status or a new H-1B transfer before the 60-day window closes. Do not assume that being in a "grace period" means you can take your time. And if you are considering the EB-5 route, the months of source-of-funds documentation and project due diligence mean you should have started yesterday.

For the thousands of Indian professionals who received layoff notices this year, the 60-day clock is not a metaphor. It is the most consequential countdown of their American lives.
"""

# Image: Open office workspace (Pexels)
art2_img_source = "https://images.pexels.com/photos/7071/space-desk-office-workspace.jpg?auto=compress&cs=tinysrgb&w=1200"
print("\nArticle 2: Sourcing image — Empty office workspace from Pexels")
if validate_image_url(art2_img_source):
    art2_img = upload_to_supabase(art2_img_source, f"{art2_id}.jpg")
else:
    print("  ⚠ Pexels image validation failed")
    art2_img = None

art2 = {
    "id": art2_id,
    "headline": "One Hundred and Ten Thousand Cuts — What Laid-Off H-1B Workers Must Know About the 60-Day Clock",
    "subheadline": "Q1 2026 saw 110,000 tech layoffs across 144 companies. For Indian H-1B holders, the grace period starts ticking from the last day of employment — not when severance runs out.",
    "slug": art2_slug,
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians are the largest national group on H-1B visas and are heavily concentrated in the technology sector now shedding jobs. The 60-day grace period misconception, combined with tightening visa rules, creates acute risk for thousands of Indian families who may lose both income and immigration status simultaneously.",
    "tags": ["h1b", "tech-layoffs", "60-day-grace-period", "immigration-status", "eb5", "indian-workers"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "StudentEB5 / Noida Chronicle", "url": "https://noidachronicle.net/studenteb5-releases-comprehensive-survival-guide-for-h-1b-visa-holders-facing-layoffs-in-2026-tech-sector-downturn/"},
        {"name": "Northern India Herald", "url": "https://northernindiaherald.in/studenteb5-releases-comprehensive-survival-guide-for-h-1b-visa-holders-facing-layoffs-in-2026-tech-sector-downturn/"},
        {"name": "Inshorts / NVIDIA H-1B data", "url": "https://inshorts.com/en/news/nvidia-expands-h-1b-hiring-amid-job-loss-reports-due-to-ai-1780419265443"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": art2_img or "",
    "image_caption": "An open-plan tech office workspace — scenes increasingly emptied by the 2026 layoff wave",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": art2_body.strip(),
}


# ══════════════════════════════════════════════════════════════════════
# INSERT
# ══════════════════════════════════════════════════════════════════════

articles = [art1, art2]

for art in articles:
    # Final checks
    if not art["image_url"]:
        print(f"⚠ No image for {art['slug']}, inserting without image")
    word_count = len(art["body"].split())
    print(f"\n{'='*60}")
    print(f"Inserting: {art['headline']}")
    print(f"  Slug: {art['slug']}")
    print(f"  Words: {word_count}")
    print(f"  Image: {'✅' if art['image_url'] else '❌'}")
    try:
        result = sb_post("p2_articles", art)
        print(f"  ✅ Published: {art['slug']}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        # Try to get error detail
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Response: {e.response.text[:500]}")

print("\n" + "="*60)
print(f"Done. {len(articles)} articles processed.")
