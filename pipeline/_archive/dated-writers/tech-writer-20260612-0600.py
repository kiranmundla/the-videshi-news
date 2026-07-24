#!/usr/bin/env python3
"""Technology writer – 3 articles for The Videshi, 2026-06-12 06:00 batch.
Topics: Opendoor India exit / AI reshoring, H-1B lottery replacement bill, NVIDIA+Abridge healthcare AI.
"""

import json, os, uuid, io, subprocess, requests, time
from datetime import datetime, timezone
from PIL import Image

# ── env ──
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/.env.supabase"))
load_dotenv(os.path.expanduser("~/workspace/.env.pexels"))
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY   = os.environ.get("PEXELS_API_KEY", "")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

now_iso = datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════════
# IMAGE HELPERS
# ═══════════════════════════════════════════════════════════════════

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
    result = buf.getvalue()
    print(f"    Compressed: {len(img_bytes)//1024}KB → {len(result)//1024}KB, {img.width}x{img.height}")
    return result


def upload_to_supabase(img_bytes, filename, bucket="article-images"):
    """Upload image bytes to Supabase storage. Returns public URL."""
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    resp = requests.post(url, headers=headers, data=img_bytes, timeout=30)
    if resp.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
        print(f"    ✓ Uploaded to Supabase: {filename}")
        return public_url
    else:
        print(f"    ✗ Upload failed [{resp.status_code}]: {resp.text[:200]}")
        return None


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's photo from Wikipedia REST API."""
    import urllib.parse
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
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200",
        "format": "json",
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params, headers=UA, timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels for an image. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        # Use curl because Python urllib gets 403 from Pexels
        cmd = [
            "curl", "-s", "-H", f"Authorization: {PEXELS_KEY}",
            f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=5&orientation=landscape"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            # Pick photo with good resolution
            for p in photos:
                src = p.get("src", {})
                url = src.get("large2x") or src.get("large") or src.get("original")
                if url:
                    print(f"  ✓ Pexels image: {url[:80]}...")
                    return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def download_image(url):
    """Download image bytes from URL."""
    try:
        r = requests.get(url, headers=UA, timeout=20)
        if r.status_code == 200 and len(r.content) > 5000:
            print(f"    Downloaded: {len(r.content)//1024}KB")
            return r.content
        else:
            print(f"    ⚠ Download issue: status={r.status_code}, size={len(r.content)}")
    except Exception as e:
        print(f"    ⚠ Download error: {e}")
    return None


def source_and_upload_image(slug, wiki_person=None, wiki_queries=None, pexels_query=None):
    """Multi-source image sourcing. Returns (url, attribution) or (None, None)."""
    print(f"\n🖼  Sourcing image for: {slug}")
    candidates = []

    # Source 1: Wikipedia person
    if wiki_person:
        url = fetch_wikipedia_person_image(wiki_person)
        if url:
            candidates.append({"url": url, "source": "wikipedia", "attribution": "Wikimedia Commons"})

    # Source 2: Wikimedia Commons
    if wiki_queries:
        for q in wiki_queries:
            results = fetch_wikimedia_commons_images(q, limit=3)
            for r in results:
                if r["width"] >= 400:
                    candidates.append({"url": r["url"], "source": "wikimedia", "attribution": "Wikimedia Commons"})
            if candidates:
                break

    # Source 3: Pexels
    if pexels_query:
        url = fetch_pexels_image(pexels_query)
        if url:
            candidates.append({"url": url, "source": "pexels", "attribution": "Pexels"})

    # Pick best and upload
    if not candidates:
        print("  ✗ No image found")
        return None, None

    best = candidates[0]
    print(f"  → Selected: {best['source']} — {best['url'][:80]}...")

    img_bytes = download_image(best["url"])
    if not img_bytes:
        # Try next candidate
        for c in candidates[1:]:
            img_bytes = download_image(c["url"])
            if img_bytes:
                best = c
                break
    if not img_bytes:
        print("  ✗ Could not download any candidate")
        return None, None

    compressed = compress_image(img_bytes)
    if len(compressed) < 10000:
        print("  ⚠ Compressed image too small (<10KB), skipping")
        return None, None

    filename = f"{slug}.jpg"
    final_url = upload_to_supabase(compressed, filename)
    return final_url, best["attribution"]


# ═══════════════════════════════════════════════════════════════════
# ARTICLES
# ═══════════════════════════════════════════════════════════════════

articles = []

# ───────────────────────────────────────────────────────────────────
# ARTICLE 1 — Opendoor India Exit & AI Reshoring
# ───────────────────────────────────────────────────────────────────
art1_id = str(uuid.uuid4())
art1_slug = "opendoor-india-exit-ai-reshoring-outsourcing-20260612"

articles.append({
    "id": art1_id,
    "headline": "Opendoor Shuts Its India Office and Sparks a $315 Billion Question About AI and Outsourcing",
    "subheadline": "The proptech firm's decision to wind down 250 jobs in Chennai and Bengaluru has become a flashpoint in the debate over whether AI is dismantling the economics of offshore work",
    "slug": art1_slug,
    "body": """Opendoor, the San Francisco-based online home-buying platform, announced on Wednesday that it is shutting down its entire India operations, affecting roughly 250 employees in Chennai and Bengaluru. The decision, less than two years after the company expanded its Indian presence, has become the most visible signal yet that artificial intelligence may be rewriting the economics of global outsourcing.

CEO Kaz Nejatian framed the move in geographic terms. "Our customers are in America, and that's where our operational work belongs," he wrote in a public note. The company had built its India team to manage manual workflows across fragmented back-office systems — the kind of repetitive, process-heavy work that made India the world's outsourcing capital. Those systems, Nejatian said, have now been unified, and smaller "AI-native" teams based in the United States will handle what remains.

## Not Just a Layoff Story

The closure is not straightforward. Opendoor has been shrinking across the board. Securities filings show global headcount fell from roughly 1,470 at the end of 2024 to 1,042 by year-end 2025, with non-US staff dropping from 342 to 184. The US housing market's extended downturn has hit online home-buying companies especially hard. But the language Nejatian used — "AI-native teams," "simplifying operations" — resonated far beyond his company's balance sheet.

"As manual work gets replaced by AI, a lot of jobs will be lost in India," wrote Sheel Mohnot, co-founder of Better Tomorrow Ventures, on X. Keshav Lohia of Emergent Ventures called it a "watershed moment" for AI-driven operations. Phil Fersht, CEO of HFS Research, the outsourcing advisory firm, told TechCrunch that Opendoor's decision reflects a pattern he describes as "services-as-software" — companies combining AI, software, and lean human teams to deliver outcomes without scaling headcount.

"This is not an isolated restructuring," Fersht said. "It is part of a much broader pattern we are starting to see as companies redesign operations around AI, automation, and much leaner workflows."

## The $315 Billion Stakes

India's outsourcing industry is no longer just call centres and data entry. The country is the world's largest Global Capability Centre market, with more than 2,100 centres employing approximately 2.36 million people and generating nearly $100 billion in annual revenue, according to Reuters. India's broader technology and outsourcing industry — encompassing IT services giants like TCS, Infosys, and Wipro — generates an estimated $315 billion annually and directly underpins the middle-class prosperity of cities like Bengaluru, Hyderabad, and Pune.

The question Opendoor has surfaced is whether AI erodes the cost-arbitrage model that built this ecosystem. When the primary advantage of an offshore team was doing the same work for a fraction of the cost, and AI can now do portions of that work for a fraction of a fraction, the calculus shifts. Not overnight — India's GCC workforce handles complex engineering, R&D, and analytics that AI cannot easily replicate — but the lower-skill operational work that employed hundreds of thousands is squarely in the crosshairs.

## A Dual Anxiety for the Diaspora

For NRIs in the American technology sector, Opendoor's move triggers a peculiar dual anxiety. On one side, the reshoring narrative — bringing jobs back to America, replacing offshore teams with domestic AI-native units — aligns with the broader political push to prioritise American workers, a push that also produces tighter H-1B rules and louder calls to restrict immigration. Indian-origin professionals in Silicon Valley are simultaneously the beneficiaries of American AI investment and potential casualties of the nativist politics that accompanies it.

On the other side, family members back home are watching outsourcing-dependent career paths narrow. Parents who steered children toward business process management or IT support roles — historically stable, well-paying positions in Indian cities — are beginning to recalibrate. The advice filtering through WhatsApp family groups is already shifting: learn to build AI, not just use the systems AI is replacing.

Opendoor's India team will receive severance packages and outplacement support. A small subset will stay temporarily to complete the transition. The company insists the decision reflects no judgment on its Indian employees' quality. That is almost certainly true, and almost certainly beside the point. The question is not whether India's tech workers are good enough. It is whether the work they were hired to do will continue to exist at all.""",
    "category": "technology",
    "status": "review",
    "is_editorial": False,
    "vertical": "technology",
    "image_url": "",
    "image_caption": "Opendoor's offices in India employed roughly 250 people in Chennai and Bengaluru before the shutdown",
    "image_attribution": "",
    "sources": json.dumps([
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/10/opendoors-india-exit-is-fueling-a-bigger-conversation-about-ai-and-outsourcing/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/opendoor-winds-down-india-operations-affecting-nearly-250-employees"},
        {"name": "Inc42", "url": "https://inc42.com/buzz/us-based-opendoor-lays-off-entire-india-team-of-250-employees/"},
    ]),
    "diaspora_angle": "NRIs in US tech face dual anxiety — reshoring politics that fuel H-1B restrictions overlap with family back home watching outsourcing careers narrow as AI replaces the manual workflows that employed hundreds of thousands",
    "published_at": now_iso,
    "created_at": now_iso,
    "updated_at": now_iso,
    "score_total": 78,
})

# ───────────────────────────────────────────────────────────────────
# ARTICLE 2 — H-1B Lottery Replacement Bill
# ───────────────────────────────────────────────────────────────────
art2_id = str(uuid.uuid4())
art2_slug = "h1b-lottery-replacement-bill-chip-roy-merit-wage-20260612"

articles.append({
    "id": art2_id,
    "headline": "A New Bill Would Kill the H-1B Lottery, End OPT, and Sever the Path to a Green Card",
    "subheadline": "Representative Chip Roy's American White-Collar Worker Jobs Act of 2026 proposes the most sweeping overhaul of the skilled-visa system in decades — and Indian professionals have the most to lose",
    "slug": art2_slug,
    "body": """On June 5, Texas Representative Chip Roy formally introduced the American White-Collar Worker Jobs Act of 2026, a bill that would dismantle several pillars of the system Indian technology professionals have relied on for decades to build careers in the United States. If enacted, it would end the H-1B visa lottery, eliminate the Optional Practical Training programme that allows international students to work after graduation, and sever the pathway from H-1B status to permanent residency.

The bill is not a refinement. It is a structural demolition of the skilled-immigration pipeline as it has existed since the H-1B programme's creation, and its consequences would fall disproportionately on Indian nationals, who account for nearly 70 percent of H-1B beneficiaries.

## What the Bill Would Do

The legislation targets five mechanisms simultaneously. First, the randomised lottery that currently allocates up to 85,000 H-1B visas annually — 65,000 regular plus 20,000 for advanced-degree holders — would be replaced by a merit-and-wage-based selection system. Petitions offering higher salaries and requiring more specialised skills would be prioritised.

Second, the bill would abolish OPT entirely. The programme currently allows international graduates of American universities to work in the US for up to 12 months after completing their degree, with STEM graduates eligible for a 24-month extension. For hundreds of thousands of Indian students at American universities, OPT is the bridge between a degree and an H-1B petition. Removing it eliminates the bridge.

Third, H-1B status would no longer serve as a pathway to a green card. Under current law, employers can sponsor H-1B workers for permanent residency, a process that for Indian nationals already involves a backlog stretching decades due to per-country caps. Roy's bill would formalise the separation entirely, making the H-1B an explicitly temporary visa with no residency trajectory.

Fourth, employers would be required to demonstrate credible efforts to hire American workers before filing an H-1B petition. Fifth, companies that have conducted recent layoffs would be barred from seeking H-1B visas — a provision clearly aimed at the practice of laying off domestic workers while simultaneously sponsoring foreign replacements.

## A System Already in Motion

The bill arrives in a system already shifting. In December 2025, the Department of Homeland Security finalised a rule replacing the pure lottery with a wage-weighted selection process for the FY 2027 cap season. Under this rule, applicants whose job offers fall in higher wage tiers receive multiple entries in the selection pool, increasing their odds. The first selection round under these rules concluded in March 2026.

Separately, on June 8 — three days after Roy introduced his bill — a federal judge struck down the Trump administration's $100,000 fee on new H-1B sponsorships, ruling that the executive branch lacked the authority to impose such a levy. That fee, announced last September, had generated only 85 payments worth $8.5 million as of mid-February, as most employers simply refused to pay. The judicial rebuke may embolden legislative efforts like Roy's to achieve through statute what executive orders could not.

## The Indian Calculus

The numbers are stark. Indian professionals file roughly 70 percent of all H-1B petitions. Indian students constitute the second-largest international student population in the US, behind China, with over 330,000 enrolled. OPT is the mechanism that allows many of them to stay and work after graduation. The green card backlog for Indian nationals in the EB-2 and EB-3 employment categories already stretches past 2060 under current rules. Roy's bill would not just extend that wait — it would eliminate the destination.

For Indian IT services firms — TCS, Infosys, Wipro, and HCLTech — which have historically been among the largest H-1B sponsors, the wage-based selection framework presents an operational challenge. These companies often place mid-level engineers at client sites at salaries that, while competitive in India, fall in the lower wage tiers by American standards. A system that explicitly favours higher-paid petitions structurally disadvantages this staffing model.

The bill must still pass committee review, potential amendments, and votes in both chambers of Congress. Its chances of passing intact are uncertain, particularly given that the technology industry retains significant lobbying power and that even some Republican lawmakers represent districts with large immigrant populations. But its introduction shifts the Overton window. The conversation is no longer about adjusting the H-1B programme's parameters. It is about whether the programme, as Indian professionals have known it, should continue to exist in recognisable form.

For the roughly two million Indian-origin technology workers in the United States — and the hundreds of thousands of students planning to join them — the bill is a reminder that the rules of engagement are not fixed. They are, at this moment, actively being rewritten.""",
    "category": "technology",
    "status": "review",
    "is_editorial": False,
    "vertical": "technology",
    "image_url": "",
    "image_caption": "The US Capitol, where the American White-Collar Worker Jobs Act of 2026 will face committee review",
    "image_attribution": "",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/unfvlf3u9z00/"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/h-1b-visa-rules-have-changed-again-what-to-know-explainer"},
        {"name": "People Matters", "url": "https://www.peoplematters.in/news/compensation-benefits/major-relief-for-indian-tech-talent-as-us-court-scraps-100000-h-1b-fee-46843"},
    ]),
    "diaspora_angle": "Indian nationals account for 70% of H-1B beneficiaries; the bill would eliminate OPT (the bridge from US degrees to work visas) and sever the H-1B-to-green-card path that two million Indian-origin tech workers in America depend on",
    "published_at": now_iso,
    "created_at": now_iso,
    "updated_at": now_iso,
    "score_total": 82,
})

# ───────────────────────────────────────────────────────────────────
# ARTICLE 3 — NVIDIA + Abridge Healthcare AI
# ───────────────────────────────────────────────────────────────────
art3_id = str(uuid.uuid4())
art3_slug = "nvidia-abridge-healthcare-ai-nemotron-clinical-20260612"

articles.append({
    "id": art3_id,
    "headline": "NVIDIA and Abridge Are Building an AI That Listens to Your Doctor — and Indian-Origin Founders Are Leading the Charge",
    "subheadline": "A new clinical AI model trained on NVIDIA's Nemotron platform could reshape how American hospitals document care, with implications for the growing Indian health-tech workforce",
    "slug": art3_slug,
    "body": """NVIDIA and Abridge announced on Thursday a partnership to build what they describe as the first foundation model purpose-built for clinical conversations. The model, trained on NVIDIA's open-source Nemotron family using Blackwell AI infrastructure, will be deployed exclusively within Abridge's platform — a tool that already transcribes doctor-patient encounters and converts them into structured, billable medical notes.

The collaboration places NVIDIA deeper into healthcare than its previous partnerships, which focused largely on drug discovery and medical imaging. Abridge, founded by Dr. Shiv Rao, a cardiologist of Indian origin, has positioned itself as the company that understands what happens in the exam room — the messy, jargon-laden, often interrupted conversations where clinical decisions actually get made.

## What the Model Does

The new model is not a general-purpose chatbot applied to medicine. It is being trained specifically on de-identified clinical conversation data, with domain adaptation built into the earliest stages of model development rather than bolted on through fine-tuning after the fact. Kimberly Powell, NVIDIA's vice president of healthcare, told The Wall Street Journal that the approach represents "an opportunity to take these models and adapt them with clinical intelligence at a much earlier stage of model development."

In practical terms, this means the model should better understand medical terminology in context, distinguish between a symptom mentioned in passing and one the clinician is actively investigating, and generate documentation that maps accurately to billing codes — a task that currently consumes an estimated two hours of administrative work for every hour of patient care.

Abridge's platform already serves health systems across the United States, transforming conversations into what the company calls "contextually aware, clinically useful, and billable AI-generated notes." The NVIDIA partnership is designed to make those notes more accurate, reduce hallucinations in clinical contexts where errors carry real consequences, and extend the system to support clinical decision support and even trial screening.

## A Hospital System Already Primed for AI

The timing is not accidental. A September 2025 report from the Office of the National Coordinator for Health IT found that 71 percent of US hospitals were already using predictive AI integrated with electronic health records in 2024, up from 66 percent in 2023. Microsoft announced a collaboration with Mayo Clinic last week to build a healthcare-focused AI model. Both OpenAI and Anthropic have launched digital health offerings aimed at consumers and providers.

The difference with the NVIDIA-Abridge model is specificity. Rather than adapting a general model for healthcare, they are building a model that begins with clinical conversations as its native domain. The Nemotron open model family — where both model weights and training data are available — gives Abridge the ability to optimise at every layer, deploying different model configurations for different workflows. Documentation might use a lighter model; clinical reasoning support might call on a heavier one.

For hospitals already under pressure to reduce clinician burnout, the appeal is obvious. American physicians report spending roughly 16 minutes per patient encounter on documentation. Specialties like emergency medicine and primary care are particularly burdened. If the NVIDIA-Abridge model can cut that time meaningfully while maintaining or improving accuracy, the adoption curve will be steep.

## The Indian Health-Tech Pipeline

Dr. Shiv Rao's trajectory — trained in cardiology, founded a company at the intersection of clinical medicine and AI, now partnering with the world's most valuable chipmaker — is not an outlier. Indian-origin founders and engineers are disproportionately represented in American health-tech. Vinod Khosla's eponymous venture firm has backed multiple AI health startups. Niramai, an Indian breast cancer screening startup using AI, was acquired by Siemens Healthineers. Qure.ai, a Mumbai-based company, deploys AI-powered chest X-ray analysis across 90 countries.

For the estimated 80,000 Indian-origin physicians practising in the United States — roughly one in seven of all practising doctors — clinical AI tools are simultaneously a productivity aid and a professional disruption. The administrative burden that AI documentation promises to lift is real and resented. But so is the unease about a technology that could, over time, encroach on clinical judgment itself.

In India, the healthcare AI market is projected to reach $3.2 billion by 2028, driven by diagnostic imaging, telemedicine, and electronic health records adoption. The talent pipeline between Indian medical schools, American residency programmes, and Silicon Valley health-tech startups is well established. NVIDIA's open model approach — making Nemotron weights and training methodology available for adaptation — could accelerate that pipeline, giving Indian health-tech companies the foundation models they need to build locally relevant clinical tools without starting from scratch.

The stethoscope is not going anywhere. But the note-taking is about to change, and Indian-origin doctors and engineers are building the system that replaces it.""",
    "category": "technology",
    "status": "review",
    "is_editorial": False,
    "vertical": "technology",
    "image_url": "",
    "image_caption": "Healthcare AI tools are transforming clinical documentation in American hospitals",
    "image_attribution": "",
    "sources": json.dumps([
        {"name": "The Wall Street Journal", "url": "https://www.wsj.com/tech/ai/nvidia-is-developing-an-ai-healthcare-model-with-startup-abridge-5daf5b80"},
        {"name": "PYMNTS", "url": "https://www.pymnts.com/artificial-intelligence-2/2026/nvidia-accelerates-healthcare-ai-race-with-transcription-model/"},
        {"name": "Abridge (BusinessWire)", "url": "https://www.businesswire.com/news/home/20260611647090/en/Abridge-Unveils-Patient-Centered-Clinician-Intelligence-Platform"},
    ]),
    "diaspora_angle": "Indian-origin cardiologist Dr. Shiv Rao founded Abridge; roughly 80,000 Indian-origin physicians in the US stand to benefit from clinical AI; India's $3.2B healthcare AI market could leverage NVIDIA's open Nemotron models",
    "published_at": now_iso,
    "created_at": now_iso,
    "updated_at": now_iso,
    "score_total": 75,
})


# ═══════════════════════════════════════════════════════════════════
# IMAGE SOURCING
# ═══════════════════════════════════════════════════════════════════

# Article 1: Opendoor/reshoring — Pexels for tech office or outsourcing scene
img1_url, img1_attr = source_and_upload_image(
    art1_slug,
    wiki_queries=["Indian IT outsourcing Bengaluru", "software outsourcing office India"],
    pexels_query="India technology office workers software"
)
if img1_url:
    articles[0]["image_url"] = img1_url
    articles[0]["image_attribution"] = img1_attr

# Article 2: H-1B bill — US Capitol or immigration imagery
img2_url, img2_attr = source_and_upload_image(
    art2_slug,
    wiki_person="United States Capitol",
    wiki_queries=["H-1B visa United States", "US Capitol building Washington"],
    pexels_query="United States Capitol building Washington DC"
)
if img2_url:
    articles[1]["image_url"] = img2_url
    articles[1]["image_attribution"] = img2_attr

# Article 3: NVIDIA healthcare AI — Jensen Huang or healthcare AI
img3_url, img3_attr = source_and_upload_image(
    art3_slug,
    wiki_queries=["NVIDIA healthcare artificial intelligence", "clinical AI healthcare technology"],
    pexels_query="doctor using technology tablet hospital AI"
)
if img3_url:
    articles[2]["image_url"] = img3_url
    articles[2]["image_attribution"] = img3_attr


# ═══════════════════════════════════════════════════════════════════
# WORD COUNT VALIDATION
# ═══════════════════════════════════════════════════════════════════
for a in articles:
    wc = len(a["body"].split())
    if wc < 400:
        print(f"⚠ BELOW FLOOR: {a['slug']} has only {wc} words!")
    elif wc < 600:
        print(f"⚠ Below target: {a['slug']} has {wc} words (target 600-800)")
    elif wc > 850:
        print(f"⚠ Over target: {a['slug']} has {wc} words (target 600-800)")
    else:
        print(f"✓ Word count OK: {a['slug']} — {wc} words")


# ═══════════════════════════════════════════════════════════════════
# INSERT INTO SUPABASE
# ═══════════════════════════════════════════════════════════════════
url = f"{SUPABASE_URL}/rest/v1/p2_articles"
for a in articles:
    resp = requests.post(url, headers=HEADERS, json=a)
    if resp.status_code in (200, 201):
        row = resp.json()
        if isinstance(row, list):
            row = row[0]
        print(f"✓ Inserted: {row['slug']}  (id={row['id']})")
    else:
        print(f"✗ FAILED [{resp.status_code}]: {a['slug']}")
        print(f"  {resp.text[:300]}")

print(f"\nDone — {len(articles)} articles submitted at {now_iso}")
