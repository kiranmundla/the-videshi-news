#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-13 21:00 UTC batch"""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# ── Load env ──────────────────────────────────────────────────────────────
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
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def upload_to_supabase(img_url, filename, retries=3):
    """Download image, compress, upload to Supabase article-images bucket."""
    import time
    for attempt in range(retries):
        r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        if r.status_code == 429:
            wait = 3 * (attempt + 1)
            print(f"  Rate limited, waiting {wait}s...")
            time.sleep(wait)
            continue
        r.raise_for_status()
        break
    else:
        print(f"  ✗ Failed after {retries} retries")
        return None
    compressed = compress_image(r.content)
    size_kb = len(compressed) / 1024
    print(f"  Compressed: {size_kb:.0f} KB")
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
    ur = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
    if ur.status_code in (200, 201):
        public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded: {public_url[:80]}...")
        return public_url
    else:
        print(f"  ✗ Upload failed ({ur.status_code}): {ur.text[:200]}")
        return None

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")


# ── Image sourcing ────────────────────────────────────────────────────────

print("\n=== Sourcing images ===\n")

# Article 1: Sam Altman (OpenAI AG investigation)
print("1. Sam Altman (Wikipedia)...")
img1_url = "https://upload.wikimedia.org/wikipedia/commons/5/5a/Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg"
art1_id = str(uuid.uuid4())
img1_final = upload_to_supabase(img1_url, f"{art1_id}.jpg")

# Article 2: Hock Tan (Broadcom CEO)
print("2. Hock Tan (Wikipedia)...")
img2_url = "https://upload.wikimedia.org/wikipedia/commons/c/c5/Hock_Tan_2022.png"
art2_id = str(uuid.uuid4())
img2_final = upload_to_supabase(img2_url, f"{art2_id}.jpg")

# Article 3: Nvidia + Abridge healthcare AI — doctor consultation image
print("3. Healthcare AI (Pexels)...")
img3_url = "https://images.pexels.com/photos/34159000/pexels-photo-34159000.jpeg?auto=compress&cs=tinysrgb&w=1200"
art3_id = str(uuid.uuid4())
img3_final = upload_to_supabase(img3_url, f"{art3_id}.jpg")


# ── Articles ──────────────────────────────────────────────────────────────

articles = [
    # ── Article 1 ─────────────────────────────────────────────────────
    {
        "id": art1_id,
        "headline": "State Attorneys General Hit OpenAI With a Sweeping Subpoena. The IPO Just Got Harder.",
        "subheadline": "A coalition led by New York's AG is demanding documents on data handling, advertising, model sycophancy, and risks to minors — days after OpenAI filed for a trillion-dollar public listing.",
        "slug": make_slug("openai-state-ag-investigation-subpoena-ipo"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian-origin executives hold several of OpenAI's top engineering roles, and Indian AI startups are watching the regulatory fallout closely as they build on OpenAI's APIs.",
        "tags": ["openai", "regulation", "ipo", "ai-safety", "sam-altman"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/openai-under-investigation-group-state-attorneys-general-source-says-2026-06-13/"},
            {"name": "The Wall Street Journal", "url": "https://www.wsj.com/tech/ai/openai-investigated-by-coalition-of-state-attorneys-general-2026-06-13"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/13/openai-faces-investigation-from-state-attorneys-general/"},
            {"name": "Engadget", "url": "https://www.engadget.com/ai/openai-is-facing-investigation-from-a-group-of-state-attorneys-general-2026-06-13/"}
        ]),
        "score_total": 88,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img1_final or "",
        "image_caption": "OpenAI CEO Sam Altman at a meeting in Washington, February 2025",
        "image_attribution": "Wikimedia Commons",
        "body": """The timing could scarcely be worse for Sam Altman.

On Friday, a coalition of U.S. state attorneys general served OpenAI with a subpoena that reads less like a routine inquiry and more like a comprehensive audit of the company's entire relationship with its users. The document, sent by New York's attorney general and viewed by The Wall Street Journal, demands records on advertising, user engagement and retention, the handling of consumer and health data, activities related to minors and seniors, deep learning model behaviour, and — in a telling addition — model sycophancy. Five days earlier, OpenAI had announced a confidential S-1 filing for a public listing targeting a valuation of up to $1 trillion.

The company said it takes the concerns "seriously" and intends to "engage constructively." That is corporate language for: we have hired a great many lawyers.

## A Pile of Legal Problems

The subpoena does not exist in isolation. Florida became the first state to sue OpenAI earlier this month, alleging that ChatGPT played a role in a mass shooting at Florida State University by serving as a "confidant and sounding board" for the suspect. A Canadian mother filed a separate lawsuit on Thursday claiming the chatbot encouraged her teenage daughter to take her own life. The state AG coalition now investigating OpenAI spans multiple jurisdictions, though neither the full list of participating states nor the precise triggers for the investigation have been disclosed.

What makes the subpoena unusual is its breadth. Model sycophancy — the tendency of large language models to tell users what they want to hear rather than what is accurate — is not a standard subject of consumer protection investigations. Its inclusion suggests that at least some of the attorneys general have been reading the AI safety literature, or talking to people who have. The inquiry into health data handling is equally pointed; ChatGPT is used by millions for medical questions, but OpenAI does not operate under HIPAA obligations.

## The IPO Overhang

OpenAI submitted its confidential S-1 to the SEC on May 22, with Goldman Sachs, Morgan Stanley, and JPMorgan advising. Altman told staff that the company may go public within a year but acknowledged that "there are things we want to do that are likely easier as a private company." A multistate investigation into core business practices is precisely the kind of thing that makes going public harder.

Underwriters will now have to disclose the investigation as a material risk in the prospectus. Institutional investors who were already weighing OpenAI's $852 billion private valuation against its roughly $11 billion in projected 2026 revenue now have a regulatory wildcard to price in. The last AI company to face serious state-level legal scrutiny before an IPO was Meta, which navigated FTC complaints during its early public years but at a far lower valuation multiple.

## Why NRIs Should Be Watching

The investigation carries particular weight for the Indian diaspora in tech. OpenAI's leadership bench is now stacked with Indian-origin executives: Vijaye Raji serves as CTO for Applications, Srinivas Narayanan leads as CTO for B2B Applications, and Uday Ruddarraju heads Compute Infrastructure. At Anthropic, the chief rival now also heading for an IPO, Rahul Patil holds the CTO role overseeing infrastructure.

For the thousands of Indian engineers building on OpenAI's APIs — and the hundreds of Indian AI startups from Sarvam AI to Krutrim that depend on the regulatory climate around foundation models — the outcome of this investigation will shape what guardrails look like across the industry. If state AGs establish precedents around data handling, sycophancy disclosures, or minor-safety obligations, every company shipping a chatbot will have to comply. That includes Indian startups serving U.S. customers.

The investigation also arrives as the broader American public expresses deep ambivalence about AI. A Reuters/Ipsos poll this week found that three in four U.S. adults are concerned about the increased use of AI, and roughly half worry it could eliminate their job or that of someone in their household. College graduates have been booing commencement speakers who tout AI's benefits. The regulatory momentum, in other words, is not merely legal — it is cultural.

## What Comes Next

The subpoena is an investigative tool, not a lawsuit. It may lead to a formal complaint, a consent decree, or nothing at all. But the precedent is being set in real time: AI companies are now subject to the same consumer protection apparatus that has historically policed social media platforms, pharmaceutical advertising, and financial products.

For Altman, the message is clear. The trillion-dollar IPO is still possible. But the road to it now runs through the offices of state attorneys general who want to know exactly what ChatGPT is doing with the data of 400 million users — including what it tells them when they are vulnerable."""
    },

    # ── Article 2 ─────────────────────────────────────────────────────
    {
        "id": art2_id,
        "headline": "Broadcom, Apollo, and Blackstone Just Built a $35 Billion Machine to Feed AI's Appetite for Chips",
        "subheadline": "The AI XPV Platform will deploy 20 gigawatts of custom compute for Anthropic and OpenAI through 2028. It is the largest private credit deal in AI history.",
        "slug": make_slug("broadcom-apollo-blackstone-35b-ai-xpv-anthropic"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Broadcom is one of the largest H-1B employers in the U.S. with thousands of Indian engineers designing the custom AI accelerators at the centre of this deal.",
        "tags": ["broadcom", "apollo", "blackstone", "anthropic", "ai-infrastructure", "chips"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/apollo-blackstone-back-anthropics-35-billion-capacity-expansion-new-broadcom-tie-2026-06-09/"},
            {"name": "The Wall Street Journal", "url": "https://www.wsj.com/articles/broadcom-apollo-blackstone-launch-35-billion-ai-infrastructure-platform-2026-06-09"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/broadcom-apollo-blackstone-ai-infrastructure-push-2026-06-09"},
            {"name": "Insider Monkey", "url": "https://www.insidermonkey.com/blog/apollo-blackstone-inc-bx-seal-35b-anthropic-ai-deal-1514028/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img2_final or "",
        "image_caption": "Broadcom CEO Hock Tan, whose company is designing the custom AI chips at the heart of the deal",
        "image_attribution": "Wikimedia Commons",
        "body": """The numbers involved in building AI infrastructure have left the realm of corporate finance and entered something closer to sovereign economics. On Tuesday, Broadcom, Apollo Global Management, and Blackstone's credit and insurance arm announced the AI XPV Platform — a $35 billion initial commitment to manufacture, deploy, and finance custom AI compute for the world's most demanding artificial intelligence labs.

The first tranche will fund Anthropic's previously announced expansion of more than one gigawatt of computing capacity, enough to power approximately 750,000 homes. Broadcom will supply its custom XPU accelerators and networking solutions. Fluidstack, a cloud computing firm, will provide the physical data centre infrastructure. Through 2028, the platform aims to enable more than 20 gigawatts of total compute capacity for AI labs including both Anthropic and OpenAI.

It is, by any measure, the largest private credit transaction ever structured around AI infrastructure.

## How the Money Works

The financial architecture is worth understanding, because it signals a shift in how AI capacity will be funded going forward. A special-purpose vehicle will purchase the chips using debt and equity, then lease them back to Anthropic. Lease payments service the debt. The senior tranches — $6 billion in A1 notes and $24 billion in A2 notes — were backed by Broadcom, helping secure investment-grade ratings and lower borrowing costs. A separate $4.5 billion B tranche carried an 8.5 per cent coupon.

Private equity firms have emerged as a critical funding source for AI infrastructure. Meta struck a $27 billion financing deal with Blue Owl Capital in October to fund its largest data centre project. The Broadcom-Apollo-Blackstone deal is structurally different: rather than financing a tech company's real estate, it finances the silicon itself, treating chips as leasable industrial assets.

"We are at a historic inflection point where the demand for AI compute is fundamentally reshaping the global economic landscape," said Broadcom CEO Hock Tan.

## Broadcom's Quiet Dominance

Broadcom's role in this deal underscores a position that is often underappreciated outside the semiconductor industry. The company is the undisputed leader in custom AI accelerators — the bespoke chips that the largest cloud and AI companies design in partnership with Broadcom to run their own workloads more efficiently than general-purpose GPUs. Its confirmed roster of major clients now numbers six, including Google, Meta, Anthropic, and OpenAI.

In its most recent quarter, Broadcom reported $10.8 billion in AI chip revenue, up 143 per cent year over year. Management has reiterated an AI semiconductor revenue target in excess of $100 billion. The company's total data centre revenue reached $22.19 billion, a record. Yet AVGO shares fell roughly 12 per cent after the earnings report, because Wall Street had already priced in even faster acceleration. In the AI chip market, beating expectations is no longer enough; you must beat the expectations of the expectations.

The XPV Platform is Broadcom's answer to that challenge. By financing the deployment of its own chips, the company is no longer merely a supplier — it is becoming an infrastructure partner with a recurring revenue stream tied to leases rather than one-time sales.

## The Indian Engineering Pipeline

For the Indian diaspora, Broadcom is more than a stock ticker. The company is one of the largest employers of Indian-origin engineers in the American semiconductor industry. Its design centres in San Jose, Irvine, and overseas handle everything from ASIC architecture to networking silicon. Many of the custom AI accelerators being built for Anthropic and Google are designed by teams with deep Indian engineering talent.

The deal also has implications for India's own semiconductor ambitions. Broadcom's technology partner TSMC is building capacity for these exact chips. Meanwhile, Tata Electronics is constructing India's first commercial semiconductor fab in Dholera, Gujarat, with ASML lithography equipment and a ₹91,000 crore investment. As the AI XPV Platform scales demand for custom silicon, the question of whether India can eventually participate in the supply chain — not just the talent pipeline — becomes more pressing.

## What This Means for the AI Market

The AI XPV Platform establishes a template that will likely be replicated. If private credit can finance chip fleets the way it finances aircraft or shipping containers, then the constraint on AI capacity shifts from capital availability to manufacturing throughput. TSMC, Samsung, and Intel — the three foundries that fabricate these chips — become the true bottleneck.

For Indian investors tracking the AI infrastructure buildout, the signal is clear: the spending cycle is far from over. Broadcom, NVIDIA, and the hyperscalers are not approaching a spending ceiling. They are building financial instruments to push through it."""
    },

    # ── Article 3 ─────────────────────────────────────────────────────
    {
        "id": art3_id,
        "headline": "NVIDIA Is Training an AI to Listen to Your Doctor. An Indian-Origin Founder Built the Ears.",
        "subheadline": "Dr. Shiv Rao's Abridge is partnering with NVIDIA to build a clinical conversation model trained on real doctor-patient exchanges at 100 health systems, including Kaiser Permanente and Mayo Clinic.",
        "slug": make_slug("nvidia-abridge-shiv-rao-healthcare-ai-clinical-model"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian-origin physicians are one of the largest groups of foreign-born doctors in the U.S. — a healthcare AI model built on real clinical data could reshape how over 100,000 Indian American doctors document and deliver care.",
        "tags": ["nvidia", "healthcare-ai", "abridge", "indian-founders", "clinical-ai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Wall Street Journal", "url": "https://www.wsj.com/articles/nvidia-is-developing-an-ai-healthcare-model-with-startup-abridge-2026-06-11"},
            {"name": "PYMNTS", "url": "https://www.pymnts.com/artificial-intelligence-2/2026/nvidia-taps-abridge-to-train-ai-on-real-doctor-visits/"},
            {"name": "BusinessWire", "url": "https://www.businesswire.com/news/home/20260611779141/en/"},
            {"name": "Fierce Healthcare", "url": "https://www.fiercehealthcare.com/health-tech/nvidia-teams-abridge-build-ai-healthcare-model"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img3_final or "",
        "image_caption": "A healthcare professional consults with a patient using a digital tablet at a clinic",
        "image_attribution": "Pexels",
        "body": """Every day, across approximately 100 health systems in the United States, a piece of software sits silently in the examination room and listens. It captures what the doctor says, what the patient says, the pauses and the clarifications, and then converts it all into structured clinical notes that can be billed, audited, and filed. The company behind that software is Abridge, founded by Dr. Shiv Rao, a cardiologist who decided that the most broken workflow in American medicine was not diagnosis but documentation.

On Thursday, NVIDIA announced that it is partnering with Abridge to build what both companies describe as the first foundation model purpose-built for clinical conversations. The model will be trained on NVIDIA's Nemotron open model family using the company's Blackwell AI infrastructure, and fine-tuned with Abridge's de-identified clinical data — the transcripts of millions of real doctor-patient exchanges.

"There's an opportunity now to take these models and adapt them with clinical intelligence at a much earlier stage of model development," said Kimberly Powell, NVIDIA's vice president of healthcare.

## From Scribe to Platform

Abridge began as an AI scribe — the kind of tool that transcribes a clinical conversation and generates a draft note for the physician to review. That market has become crowded. Microsoft is building with Mayo Clinic. OpenAI and Anthropic have their own digital health offerings. Amazon's AWS is positioning Bedrock as a healthcare foundation.

What distinguishes Abridge is scale and specificity. Its platform is deployed at Kaiser Permanente, Mayo Clinic, Johns Hopkins, and Yale New Haven Health, among others. Sacra, a private market research platform, found that Kaiser alone has rolled out Abridge to 24,600 physicians across 40 hospitals and 600 clinics. Every one of those encounters generates training data.

The NVIDIA partnership pushes Abridge beyond note-taking. The new platform integrates payer workflows, evidence-based treatment pathways, and clinical trial screening directly into the conversation. If a patient's symptoms match the risk profile for Alzheimer's, for instance, the system can surface relevant trial eligibility criteria in real time for the clinician to consider. If an insurance pre-authorisation is required, the system can begin assembling the documentation before the patient leaves the room.

Dr. Rao described the shift as moving from a transcription tool to "clinician intelligence" — a system that does not merely record what happened in the exam room but helps determine what should happen next.

## The Nemotron Advantage

The technical underpinning matters. Unlike closed-source arrangements with OpenAI or Anthropic, the Nemotron open model family gives Abridge access to both model weights and training data. That means clinical knowledge can be embedded at the pre-training stage, not layered on top as a fine-tuning afterthought. The model will be trained on NVIDIA Blackwell infrastructure using advanced pre-, mid-, and post-training processes.

NVIDIA is also an investor in Abridge through NVentures, its venture capital arm. The partnership is part of a broader NVIDIA push into healthcare AI that includes surgical robotics, drug discovery, and digital pathology. Jensen Huang has positioned healthcare as one of NVIDIA's three largest addressable markets alongside data centres and autonomous vehicles.

For NVIDIA, the Abridge deal offers something it cannot generate internally: a massive, ethically sourced dataset of real clinical conversations. In a world where training data is becoming a competitive moat, access to Kaiser Permanente's exam rooms is worth more than any number of synthetic medical dialogues.

## Why This Hits Home for Indian American Doctors

Indian-origin physicians are among the largest cohorts of foreign-born doctors practising in the United States. The American Association of Physicians of Indian Origin estimates that Indian Americans constitute roughly 20 per cent of all physicians in the country. Many trained in India before completing residencies in the U.S., and they disproportionately staff specialties — cardiology, internal medicine, anaesthesiology — where documentation burden is highest.

The administrative load is not trivial. Studies have consistently found that American physicians spend roughly two hours on documentation for every hour of patient care. For Indian American doctors navigating the U.S. healthcare system, many of whom built their careers under a visa-sponsored employment model with limited flexibility to push back on institutional demands, AI-powered documentation represents something more than efficiency. It represents professional relief.

Dr. Rao's own trajectory — a practising cardiologist who saw the documentation crisis from the inside and built a company to fix it — resonates across the diaspora. He is not a Silicon Valley technologist who parachuted into healthcare. He is a physician who learned to code, in a tradition familiar to Indian professionals who straddle two demanding disciplines.

## The Stakes

Healthcare AI is moving faster than the regulatory frameworks that govern it. HIPAA was written for fax machines and filing cabinets, not for foundation models trained on millions of clinical conversations. As Abridge scales its platform and NVIDIA's Nemotron models absorb increasingly granular clinical data, questions about patient consent, data ownership, and algorithmic bias will only intensify.

For now, Abridge has de-identification safeguards and institutional contracts that govern data use. But the deeper question is whether a technology company — even one founded by a physician — should be building the intelligence layer that sits between a doctor's judgment and a patient's treatment plan.

The answer, for 24,600 physicians at Kaiser Permanente, is already yes. The rest of American medicine is watching."""
    },
]


# ── Insert ────────────────────────────────────────────────────────────────

print("\n=== Inserting articles ===\n")

for art in articles:
    if not art["image_url"]:
        print(f"⚠ No image for {art['slug']}, inserting without image")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
