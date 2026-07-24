#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-05 06:00 UTC run"""
import json, os, uuid, re, requests, io, urllib.parse
from datetime import datetime, timezone
from pathlib import Path

# --- Env ---
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
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_upload_image(img_bytes, filename):
    """Upload compressed image to Supabase storage bucket article-images."""
    upload_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    r = requests.post(url, headers=upload_headers, data=img_bytes, timeout=30)
    r.raise_for_status()
    return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"

def compress_image(img_bytes, max_width=1200, quality=80):
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params, headers=UA, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                })
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []

def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5",
            headers={"Authorization": PEXELS_KEY}, timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                return photos[0]["src"]["large2x"]
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def download_and_upload(img_url, slug):
    """Download image, compress, upload to Supabase, return public URL."""
    try:
        r = requests.get(img_url, headers=UA, timeout=20)
        r.raise_for_status()
        ct = r.headers.get("Content-Type", "")
        if not ct.startswith("image/"):
            print(f"  ⚠ Not an image: {ct}")
            return img_url
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return img_url
        compressed = compress_image(r.content)
        filename = f"{slug}.jpg"
        final_url = sb_upload_image(compressed, filename)
        print(f"  ✓ Uploaded to Supabase: {filename} ({len(compressed)} bytes)")
        return final_url
    except Exception as e:
        print(f"  ⚠ Download/upload failed: {e}, using original URL")
        return img_url

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-20260605"

# ═══════════════════════════════════════════════════
# ARTICLE 1: AI Job Cuts at Record Levels
# ═══════════════════════════════════════════════════

art1_slug = make_slug("ai-top-reason-us-job-cuts-challenger-data-indian-tech-workers")
art1_id = str(uuid.uuid4())

print(f"\n📰 Article 1: AI Job Cuts")
print("  Sourcing image...")

# Wikimedia Commons for tech layoffs / AI jobs
art1_img = None
commons1 = fetch_wikimedia_commons_images("technology workers office Silicon Valley")
if commons1:
    art1_img = commons1[0]["url"]
    art1_attribution = "Wikimedia Commons"
    art1_caption = "Tech workers at a Silicon Valley office campus"
    print(f"  Using Commons image: {commons1[0]['title']}")

if not art1_img:
    art1_img = fetch_pexels_image("technology office workers corporate layoff")
    if art1_img:
        art1_attribution = "Pexels"
        art1_caption = "Workers at a technology company office"

if art1_img:
    art1_img = download_and_upload(art1_img, art1_slug)

art1_body = """Ninety-seven thousand. That is how many job cuts American employers announced in May, according to Challenger, Gray & Christmas, the outplacement firm that has tracked corporate layoffs for decades. It is a 16 per cent jump from April, the third consecutive monthly increase, and the highest May total since the pandemic gutted the economy in 2020.

But the headline number is not the story. The reason behind it is.

For the third straight month, artificial intelligence was the single most-cited justification for eliminating positions. Of May's 97,000 announced cuts, more than 38,000 — roughly 40 per cent — were attributed directly to AI. Year-to-date, AI-driven layoffs have reached nearly 88,000, already surpassing the total for all twelve months of 2025. "AI is now the leading reason companies give for cutting jobs, and the primary industry citing it is technology," said Andy Challenger, the firm's chief revenue officer.

## The tech sector is the epicentre

The technology industry announced 38,242 job cuts in May alone, the highest monthly figure since August 2024. Through the first five months of 2026, tech companies have disclosed 123,653 planned reductions — a 66 per cent increase over the same period last year.

Meta set the tone. In late May, the company laid off approximately 8,000 employees and closed another 6,000 open positions. CEO Mark Zuckerberg, in a company-wide memo, called AI "the most consequential technology of our lifetimes" and framed the reductions as necessary to redirect capital toward an AI infrastructure buildout projected to cost up to $145 billion this year. Seven thousand surviving employees were reassigned to AI-focused roles.

Amazon has trimmed some 30,000 corporate positions since October 2025. Block, the fintech company behind Square, tagged roughly 40 per cent of its workforce for elimination in what it called an "AI remake." Oracle shed approximately 30,000 roles. Microsoft offered voluntary buyouts to 7 per cent of its US workforce. The pattern repeats across the industry.

## For Indian professionals, the stakes are existential

These are not abstract statistics for the hundreds of thousands of Indian-origin engineers working at American technology companies. Indians hold between 71 and 73 per cent of all approved H-1B visas, making them the single largest beneficiary group in the programme. When Meta or Amazon announces a restructuring, a disproportionate share of the affected workers are Indian nationals whose immigration status is tied directly to continued employment.

Under current US immigration rules, an H-1B holder who loses their job has exactly 60 days to find a new sponsoring employer or begin the process of leaving the country. In the first quarter of 2026 alone, more than 110,000 tech employees were let go across 144 companies. A survival guide published by StudentEB5, an immigration advisory firm, detailed the grim mechanics: the grace period begins on the last day of actual employment, not when severance payments end, and misunderstanding this distinction can trigger a three-year or ten-year bar from re-entry.

The 60-day clock does not care about your pending green card application or your child's school year.

## The paradox: tech is also hiring

The Challenger data contains a less-reported counterpoint. Despite leading the country in job cuts, the technology sector simultaneously leads in new hiring intentions, accounting for 11,000 planned new positions in May. The national unemployment rate has held steady at 4.3 per cent. Companies are not so much shrinking as reshaping — eliminating roles they believe AI can absorb while creating new ones to build, manage, and deploy that same AI.

NVIDIA, which sits at the centre of the global AI boom, increased its H-1B visa certifications by 20 per cent year-over-year in the first half of fiscal 2026, securing approval for approximately 1,200 positions. While Google's approved H-1B hires dropped from 5,100 to 2,200 and Amazon's fell from 6,100 to 4,300, NVIDIA was expanding — a reflection of which companies are consuming AI and which are building its infrastructure.

## Is AI really doing the firing?

Some researchers urge caution. Fabian Stephany, assistant professor of AI and work at the Oxford Internet Institute, has suggested that companies may be "scapegoating" AI to mask decisions driven by pandemic-era overhiring and broader market adjustments. The Yale Budget Lab found that AI has not yet caused widespread job losses across the economy, suggesting the corporate narrative may be running ahead of the actual displacement.

Andy Challenger offered a more measured framing. "Like spreadsheets and email before it, the technology will ultimately make workers more productive," he said. "But our data shows companies are already acting on it, citing AI for more cuts than any other reason."

For an Indian engineer in Sunnyvale watching their team get restructured, the academic debate over whether AI is the real reason or merely the stated one is a distinction without a practical difference. The layoff letter arrives either way."""

art1 = {
    "id": art1_id,
    "headline": "AI Is Now America's Top Excuse for Firing People. The Data Says It Might Not Be Wrong.",
    "subheadline": "Challenger data shows 88,000 AI-driven job cuts in five months — already exceeding all of 2025. For Indian H-1B holders, the 60-day clock is ticking louder than ever.",
    "slug": art1_slug,
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indians hold 71-73% of H-1B visas. AI-driven layoffs at Meta, Amazon, and Oracle disproportionately affect Indian tech workers who face a 60-day grace period to find new sponsorship or leave the US.",
    "tags": ["ai", "layoffs", "h1b", "silicon-valley", "indian-tech-workers", "meta"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/economy/jobs/technology-sector-leads-u-s-layoff-plans-69e8e95e"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/us-tech-sector-announces-most-job-cuts-in-nearly-two-years"},
        {"name": "Challenger, Gray & Christmas (via LinkedIn)", "url": "https://www.linkedin.com/pulse/tech-job-cuts-surge-hitting-nearly-two-year-high-andrew-challenger/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/inside-nvidias-global-talent-push-h-1b-surge-and-467-crore-salaries-for-ai-researchers-architects-and-engineers"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": art1_img or "",
    "image_caption": art1_caption if art1_img else "",
    "image_attribution": art1_attribution if art1_img else "",
    "is_editorial": False,
    "body": art1_body
}

# ═══════════════════════════════════════════════════
# ARTICLE 2: Meta Keylogging Employees to Train AI
# ═══════════════════════════════════════════════════

art2_slug = make_slug("meta-keylogging-employees-train-ai-zuckerberg-mci")
art2_id = str(uuid.uuid4())

print(f"\n📰 Article 2: Meta Keylogging")
print("  Sourcing image — Mark Zuckerberg (Wikipedia)...")

art2_img = fetch_wikipedia_person_image("Mark Zuckerberg")
art2_attribution = "Wikimedia Commons"
art2_caption = "Meta CEO Mark Zuckerberg, who called his employees 'smart people' whose computer use should train AI models"

if not art2_img:
    art2_img = fetch_pexels_image("computer keyboard surveillance monitoring")
    art2_attribution = "Pexels"
    art2_caption = "A computer keyboard — Meta is now recording every keystroke its employees make"

if art2_img:
    art2_img = download_and_upload(art2_img, art2_slug)

art2_body = """The flyers started appearing in Meta's office bathrooms sometime in May. They were not about policy changes or team outings. They were protests — printed by employees who had just learned that the company was installing software on their work computers to record their keystrokes, mouse movements, clicks, and periodic screenshots of their screens.

The programme is called the Model Capability Initiative, or MCI. Its purpose, according to internal memos first reported by Reuters in late April, is to capture how humans interact with computers so that Meta can train AI agents to do the same work autonomously. Meta's CTO Andrew Bosworth described the endgame in a separate memo: "The vision we are building towards is one where our agents primarily do the work and our role is to direct, review and help them improve."

On Tuesday, after weeks of internal revolt, Meta offered a concession. Employees may now pause the tracking for 30-minute intervals when they need to "check something personal." A subset — remote workers with bandwidth concerns, those handling sensitive material, or people who cannot keep laptops plugged in — can request a full exemption.

Thirty minutes. That was the compromise.

## Zuckerberg's pitch: 'Smart people'

A leaked recording of an internal all-hands meeting from April 30, obtained by the worker advocacy group More Perfect Union, captured Zuckerberg's logic in his own words. "We are using this to feed a very large amount of content into the AI model, so that way it can learn how smart people use computers to accomplish tasks," he said. "The average intelligence of the people who are at this company is significantly higher than the average set of people that you can get to do tasks."

The flattery was deliberate. Zuckerberg explained that Meta chose to capture data from its own employees rather than hiring outside contractors because its workforce was, in his assessment, smarter. Throughout the six-minute monologue, he returned to the phrase "smart people" repeatedly.

He also said the data would not be used for performance reviews or employee surveillance. He did not commit to anonymising it.

## Training the replacement

The timing makes the programme difficult to swallow. MCI was announced in late April. Within weeks, Meta laid off approximately 8,000 employees and closed 6,000 open positions. Seven thousand remaining workers were reassigned to AI-focused teams. A new internal unit called Applied AI Engineering was created to improve the coding capabilities of Meta's models and build agents that could "do the bulk of the work to build, test and ship future products."

The sequence is hard to misread: Meta is recording how its engineers work, using that data to train AI that can replicate their work, and then eliminating their positions. One engineer, in an internal post viewed by nearly 20,000 colleagues and later obtained by Wired, wrote that he was uncomfortable watching his screen being scraped to train machines that could take his job. "What kind of norms are we establishing about how the technology is used, and how people are going to be treated?" he asked.

Some employees took to calling MCI the "Employee Data Extraction Factory."

## The legal void

In the United States, there is no federal law preventing an employer from monitoring everything an employee does on a company device. "On the US side, federally, there is no limit on worker surveillance," said Ifeoma Ajunwa, a law professor at Yale University. State-level laws require, at most, that workers be broadly informed when monitoring is occurring.

In Europe, the story would be different. Valerio De Stefano, a professor of technology and labour law at York University in Toronto, noted that European data protection frameworks would likely prohibit this level of monitoring. But Meta's MCI programme is currently deployed only on US-based employees' machines.

## Why Indian engineers at Meta should care

Meta is one of the largest employers of Indian-origin technologists in the United States. The company's engineering floors in Menlo Park, Seattle, and New York are staffed substantially by H-1B visa holders and green card applicants of Indian origin.

For these workers, the MCI programme creates a particular dissonance. They are being asked to generate training data for AI systems while simultaneously watching their colleagues get laid off in the name of AI efficiency. Those who remain are acutely aware that their immigration status depends on continued employment at a company that has stated, in writing, that it wants agents to do the bulk of the work.

The 30-minute pause is not a privacy protection. It is a pressure valve — a small enough gesture to acknowledge the discomfort without changing the direction of travel. Meta is not backing away from MCI. It is polishing the edges while the programme proceeds."""

art2 = {
    "id": art2_id,
    "headline": "Meta Is Recording How Its Engineers Use Computers. The 30-Minute Bathroom Break Was a Concession.",
    "subheadline": "The Model Capability Initiative captures keystrokes, clicks, and screenshots to train AI agents. Employees protested. Zuckerberg called them 'smart people.' Then 8,000 of them got laid off.",
    "slug": art2_slug,
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Meta is one of the largest H-1B employers for Indian engineers. Workers are generating training data for AI while watching colleagues get laid off — and their own immigration status depends on staying employed at the company building their replacement.",
    "tags": ["meta", "ai", "surveillance", "silicon-valley", "indian-tech-workers", "zuckerberg"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Register", "url": "https://www.theregister.com/2026/06/04/meta_keylogging_staff_breaks/"},
        {"name": "Engadget", "url": "https://www.engadget.com/big-tech/meta-will-reportedly-let-employees-take-30-minute-breaks-from-its-tracking-program-193517083.html"},
        {"name": "WebProNews", "url": "https://www.webpronews.com/meta-lets-workers-pause-its-ai-training-tracker-for-30-minutes-after-staff-revolt/"},
        {"name": "Inc.", "url": "https://www.inc.com/kit-eaton/after-weeks-of-pushback-meta-will-now-give-employees-a-30-minute-break-from-its-ai-surveillance-tool/91052159"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": art2_img or "",
    "image_caption": art2_caption if art2_img else "",
    "image_attribution": art2_attribution if art2_img else "",
    "is_editorial": False,
    "body": art2_body
}

# ═══════════════════════════════════════════════════
# ARTICLE 3: Cadence + IIT Delhi Lab / India Chip Talent
# ═══════════════════════════════════════════════════

art3_slug = make_slug("cadence-iit-delhi-chip-design-lab-semiconductor-talent")
art3_id = str(uuid.uuid4())

print(f"\n📰 Article 3: Cadence-IIT Delhi Lab")
print("  Sourcing image...")

art3_img = None
# Try Wikimedia Commons for IIT Delhi or semiconductor lab
commons3 = fetch_wikimedia_commons_images("IIT Delhi campus")
if commons3:
    art3_img = commons3[0]["url"]
    art3_attribution = "Wikimedia Commons"
    art3_caption = "The Indian Institute of Technology Delhi campus, home to the new Cadence chip design innovation lab"
    print(f"  Using Commons image: {commons3[0]['title']}")

if not art3_img:
    commons3b = fetch_wikimedia_commons_images("semiconductor chip design laboratory")
    if commons3b:
        art3_img = commons3b[0]["url"]
        art3_attribution = "Wikimedia Commons"
        art3_caption = "A semiconductor chip design facility — India is racing to build its chip talent pipeline"

if not art3_img:
    art3_img = fetch_pexels_image("semiconductor chip design circuit board closeup")
    if art3_img:
        art3_attribution = "Pexels"
        art3_caption = "A semiconductor chip — India's design talent pipeline is expanding rapidly"

if art3_img:
    art3_img = download_and_upload(art3_img, art3_slug)

art3_body = """On Wednesday, Cadence Design Systems and the Indian Institute of Technology Delhi jointly announced the IIT Delhi-Cadence Innovation Lab, a multidisciplinary centre of excellence that gives Indian students and researchers access to the same electronic design automation tools used by professional chip designers at Intel, Qualcomm, and NVIDIA.

The announcement would have been unremarkable five years ago — another corporate lab at another IIT. In 2026, it lands in the middle of a semiconductor talent crisis that could determine whether India's $200-billion chip ambitions remain a policy document or become a functioning industry.

## What the lab actually provides

The lab offers access to more than 200 industry-grade Cadence solutions across four domains: chip design verification, digital implementation, analogue design, and system design and analysis. Crucially, these are the production tools — not academic versions or simulation-only licences, but the same software that engineers at leading semiconductor companies use daily.

Cadence has also introduced courses that combine theory with project-based labs, replacing a theory-only model that has long frustrated Indian industry. Select fourth-year undergraduates from IITs and NITs can enter an Early Master's Research pathway, mentored jointly by Cadence experts and IIT Delhi faculty. A parallel incubator programme supports pre-seed startups with a low-cost route to their first tape-out — the moment a chip design is finalised and sent to a fabrication facility.

The lab aligns with India's Design-Linked Incentive scheme, which provides financial support to domestic chip design firms. It is, in essence, an attempt to address the pipeline problem at its source: there are not enough Indians who can design chips, and the ones who can are mostly working in San Jose.

## The talent gap behind the factories

India's semiconductor ambitions are extensive. The country has approved a $2.75-billion Micron assembly and test facility in Gujarat, a Tata-Powerchip fabrication project in Dholera that ASML has agreed to equip, and a series of OSAT and compound semiconductor plants across multiple states. NITI Aayog projects the domestic semiconductor market will reach approximately $200 billion by 2035.

But factories need engineers. By various industry estimates, India will require upward of 85,000 semiconductor professionals by 2030, spanning design, process engineering, packaging, and testing. The current domestic supply is a fraction of that number. India produces approximately 25,000 VLSI engineering graduates annually, but the vast majority lack the hands-on experience with industry-grade tools that employers require. The gap between an academic curriculum and a tape-out-ready engineer is several years wide.

## The diaspora problem — and opportunity

This is where the Indian diaspora enters the picture. An estimated 25 to 30 per cent of the semiconductor engineering workforce in the United States is of Indian origin. They design chips at Intel and AMD in Santa Clara, architect GPU interconnects at NVIDIA in San Jose, and lead process development at TSMC's new Arizona fabs. They possess exactly the expertise India needs.

Some are returning. Agrani Labs, founded by four former Intel and AMD executives, is building AI inference chips in India. C2i Semiconductors, started by Texas Instruments veterans, taped out an AI power management chip in late May and secured fresh venture funding. VerveSemi raised a $10-million Series A in February for its mixed-signal and analogue chips. Netrasemi, backed by Zoho and others, has its flagship 12nm edge AI system-on-chip — described by IT Minister Ashwini Vaishnaw as India's first edge AI SoC — approaching commercial readiness for 2027.

In the first five months of 2026, Indian chip design startups raised $92 million in aggregate, roughly four times the total for all of 2025. The money is arriving. But the question is whether the people will follow.

## The IIT pipeline is necessary but not sufficient

The Cadence lab at IIT Delhi addresses one bottleneck: giving students access to real tools so they graduate closer to productive. But the deeper issue is scale and incentive. A senior chip designer in the Bay Area earns between $250,000 and $500,000 in total compensation. A comparable role at an Indian startup, even a well-funded one, offers a fraction of that.

For an Indian-American chip engineer with a mortgage in Cupertino, children in good schools, and a green card finally within reach after a decade-long queue, the calculation is not straightforward. The pull of India's semiconductor moment is real. The push of American compensation, stability, and an immigration system that penalises departure is equally real.

Cadence's lab will train the next generation. The question India has not yet answered is whether that generation will stay."""

art3 = {
    "id": art3_id,
    "headline": "Cadence Gave IIT Delhi Its Best Chip Design Tools. India's Talent Pipeline Still Isn't Ready.",
    "subheadline": "The new innovation lab puts 200+ industry-grade EDA tools in students' hands. But India needs 85,000 semiconductor engineers by 2030, and most of the ones it has are working in San Jose.",
    "slug": art3_slug,
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "25-30% of the US semiconductor workforce is Indian-origin. India's chip ambitions depend on this diaspora returning or the domestic pipeline catching up — the Cadence-IIT Delhi lab is a bet on the latter.",
    "tags": ["semiconductors", "india", "cadence", "iit-delhi", "chip-design", "diaspora"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "LatestLY / BusinessWire India", "url": "https://www.latestly.com/agency-news/business-news-iit-delhi-and-cadence-launch-ai-enabled-innovation-lab-to-advance-indias-semiconductor-talent-6889474.html"},
        {"name": "The News Headliner", "url": "https://thenewsheadliner.com/iit-delhi-and-cadence-launch-ai-enabled-innovation-lab-to-advance-indias-semiconductor-talent/"},
        {"name": "Communications Today", "url": "https://communicationstoday.co.in/indias-semiconductor-moment/"},
        {"name": "DIGITIMES", "url": "https://apps.digitimes.com/tag/india"}
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "image_url": art3_img or "",
    "image_caption": art3_caption if art3_img else "",
    "image_attribution": art3_attribution if art3_img else "",
    "is_editorial": False,
    "body": art3_body
}

# ═══════════════════════════════════════════════════
# PUBLISH
# ═══════════════════════════════════════════════════

articles = [art1, art2, art3]

print("\n" + "="*60)
print("PUBLISHING")
print("="*60)

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print("\nDone.")
