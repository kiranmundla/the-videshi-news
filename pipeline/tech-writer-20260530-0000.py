#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-30 00:00 UTC batch"""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Salil Parekh Earned 742 Times the Median Infosys Salary. The Real Story Is What Comes Next.",
        "subheadline": "As India's IT sector stares down an AI-driven reckoning, Infosys disclosed its longest-serving non-founder CEO earned ₹82.6 crore — and stayed silent on whether his contract will be renewed.",
        "slug": make_slug("salil-parekh-infosys-ceo-pay-742x-ai-disruption"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Infosys is one of the largest H-1B visa sponsors in the United States, employing tens of thousands of Indian tech workers. Its trajectory under AI disruption directly affects NRI job security, career planning, and the broader Indian IT services model that enabled a generation of diaspora immigration.",
        "tags": ["infosys", "salil-parekh", "indian-it", "ceo-compensation", "ai-disruption", "h1b"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/infosys-ceos-compensation-rises-25-nearly-87-million-fiscal-2026-2026-05-29/"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/infosys-ceo-salil-parekh-earns-826-crore-in-fy26/article69630251.ece"},
            {"name": "Business Standard", "url": "https://www.business-standard.com/companies/news/infosys-ceo-salil-parekh-salary-fy26-82-crore-125052901036_1.html"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e5/Infosys_%284911287704%29.jpg",
        "body": """The annual report is a ritual. The numbers come first — revenue, margins, headcount. Then, buried somewhere between governance disclosures and risk factors, comes the line item that everyone reads and nobody talks about: the CEO's pay.

Infosys disclosed on Friday that Salil Parekh, its Chief Executive and Managing Director, earned a total remuneration of ₹82.6 crore ($8.69 million) in fiscal year 2026 — a 2.5% increase from the prior year. That figure is 742 times the median employee salary at the company, which stood at ₹11.13 lakh.

The composition is instructive. Parekh's base salary was a relatively modest ₹7.97 crore. Bonuses and variable pay contributed ₹23.35 crore. The real weight came from exercised stock options — ₹50.75 crore — a reminder that in modern executive compensation, the paycheck is a side dish. The equity is the meal.

## The Silence That Speaks

What the annual report did not say may matter more than what it did. Parekh's current five-year term expires in March 2027, making him the longest-serving non-founder CEO in Infosys history. The report offered no indication of whether his contract would be renewed. In a company whose leadership transitions have historically been anything but smooth — recall the Vishal Sikka departure in 2017, or the Nandan Nilekani restoration that followed — that silence carries weight.

Nilekani, for his part, voluntarily took no remuneration as Chairman during the fiscal year. The symbolism is hard to miss: the founder who built the company takes nothing; the professional manager who runs it takes 742 times what its median employee earns.

## The ₹315 Billion Question

This compensation disclosure arrives as India's $315-billion IT services sector faces what may be its most serious structural threat since the 2008 financial crisis.

Earlier this month, Indian IT stocks fell to a three-year low after OpenAI announced a new services-led venture that directly competes with the labor-arbitrage model that built companies like Infosys, TCS, and Wipro. Infosys itself forecast revenue growth of just 1.5% to 3.5% for fiscal 2027, below analysts' expectations.

The math is stark. If AI tools can replicate even 30% of the routine coding, testing, and maintenance work that Indian IT firms sell to Western clients — a figure some analysts now consider conservative — then the entire pyramid staffing model that sustains these companies begins to crack. TCS shed 25,000 jobs in nine months. Cognizant and Wipro have been restructuring continuously.

## What It Means in Jersey City

For the Indian tech professional in the United States — the software engineer at an Infosys client site in Plano, the project manager in Edison, the architect in the Bay Area — this is not abstract. Infosys is one of the top H-1B visa sponsors in America. Its business health directly determines how many positions it maintains onshore, how many visas it sponsors, and how stable those roles are.

The shift from time-and-materials billing to outcome-based AI-augmented delivery doesn't just change Infosys's margins. It changes the demand curve for the specific type of Indian tech talent that the H-1B system was designed to import. Mid-level engineers with 8-12 years of experience in legacy delivery environments — the demographic that forms the backbone of the Indian IT workforce in America — are exactly the roles most vulnerable to AI substitution.

Parekh's pay, viewed in this light, is less a story about one executive's compensation and more a data point about the last chapter of a business model. The CEO of a company built on human capital arbitrage earned ₹82.6 crore in a year when the technology to replace that arbitrage became commercially viable.

## The Comparison

For context: K. Krithivasan, CEO of Infosys's larger rival TCS, earned $2.96 million for the same fiscal year — roughly a third of Parekh's compensation. HCLTech and Wipro have not yet released their annual reports.

The gap matters because it raises the question every NRI investor and IT professional is already asking: Is the premium justified by performance, or is it an artifact of a compensation structure designed in a different era?

Infosys reported a 20.8% rise in quarterly net profit and 13.4% revenue growth in Q4 FY26. By conventional metrics, Parekh has delivered. But conventional metrics were designed for a world where the primary competitive variable was headcount. That world is ending.

The annual report has been filed. The numbers are in the record. What happens next — to Parekh's tenure, to Infosys's model, to the hundreds of thousands of Indian professionals whose careers are tethered to this industry — remains unwritten."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Two Indian Startups Want to Put a Data Center in Orbit. The Pathfinder Launch Is Set for Q4 2026.",
        "subheadline": "Pixxel and Sarvam AI are building India's first orbital data center satellite — a 200-kg spacecraft running sovereign AI models on GPU compute, powered by solar energy, with zero dependence on foreign cloud infrastructure.",
        "slug": make_slug("pixxel-sarvam-ai-orbital-data-center-satellite-india"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "This partnership represents a new category of deep-tech investment opportunity for NRI investors and professionals. Both companies were founded by young Indian engineers — Pixxel by BITS Pilani alumni — and the project positions India as a competitor in the orbital computing race against US and European players.",
        "tags": ["pixxel", "sarvam-ai", "orbital-data-center", "space-tech", "satellite", "sovereign-ai", "india-startups"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "W.Media", "url": "https://w.media/pixxel-sarvam-join-indias-orbital-data-center-race/"},
            {"name": "The GreyLens", "url": "https://thegreylens.com/pixxel-and-sarvam-ai-partner-to-develop-ai-powered-orbital-data-centers"},
            {"name": "ET CIO", "url": "https://cio.economictimes.indiatimes.com/news/data-center/space-company-pixxel-and-ai-firm-sarvam-join-hands-to-build-orbital-data-centre-satellite/121412345"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/60132/pexels-photo-60132.jpeg",
        "body": """The pitch sounds like a Y Combinator application written by a science fiction author: take a GPU-equipped satellite, load it with sovereign AI models built entirely in India, launch it into low Earth orbit, and run training and inference 400 kilometers above the planet's surface. No ground-based cloud. No foreign infrastructure dependency. Solar-powered. Operational by the end of 2026.

Except this is not a pitch deck. It is a signed partnership between two of India's most credible deep-tech startups, and the hardware is already being designed.

Pixxel, the Bengaluru-based satellite imaging company, and Sarvam AI, the Indian foundational AI company, have announced a collaboration to build what they call India's first orbital data center satellite. The mission is named Pathfinder — a 200-kilogram-class spacecraft scheduled to reach orbit as early as Q4 2026.

## Why Orbit?

The logic starts with constraints on the ground. Data centers consume enormous quantities of electricity, water, and land. Google's planned $15 billion AI hub in Visakhapatnam will use the equivalent electricity of six million people in India annually. Cooling alone accounts for 40% of a typical data center's energy bill.

In orbit, the constraints are different. Solar energy is abundant — no clouds, no night cycle on the sun-facing side of an orbit. Cooling in the vacuum of space is a solved thermal engineering problem. And for certain workloads — particularly those involving satellite-generated data that currently must be downlinked to Earth before processing — computing in orbit eliminates bandwidth bottlenecks entirely.

"Ground-based data centers are facing increasing constraints around energy, land, regulation, and scale," said Awais Ahmed, CEO of Pixxel. "Orbital data centers open up a new frontier, where compute can be powered by abundant solar energy, operate closer to space-based data, and move beyond some of the limits faced on Earth."

## The Architecture

Pixxel brings the space hardware. The company, founded by BITS Pilani graduates Awais Ahmed and Kshitij Khandelwal, already operates India's first private satellite constellation — six hyperspectral imaging satellites in orbit, with clients including Rio Tinto, BP, and India's Ministry of Agriculture. The Google-backed startup is targeting a 24-satellite constellation and has been valued in the hundreds of millions.

Sarvam AI brings the software stack. The company has built what it calls a Full-stack Sovereign AI Platform — foundational generative AI models developed and governed entirely in India, optimized for Indian languages and use cases. On the Pathfinder satellite, Sarvam's models and inference platform will run directly on the spacecraft's GPU compute layer.

The critical design choice: no dependence on foreign cloud or ground infrastructure. Data goes up, gets processed in orbit by Indian AI models running on Indian hardware, and only the results come back down. In the vocabulary of the moment, this is sovereign AI taken to its most literal extreme — sovereign compute that is physically outside the jurisdiction of any nation.

## The Competition

Pixxel and Sarvam are not alone in this race, but they may be the most advanced non-Western entrants. Power Bank and Orbit AI launched the first dedicated compute satellite in December 2025. Canada's Galaxia received a $2.5 million defense contract for orbital infrastructure. US startup Lumen Orbit (now Starcloud) raised over $10 million for AI training in space. Axiom Space and Red Hat are building general-purpose edge computing prototypes on the ISS.

India's entry matters for two reasons. First, it establishes that orbital compute is not exclusively a Western capability. Second, it tests whether a country with a $8 billion space sector (targeting $44 billion by 2030) can leapfrog the infrastructure buildout phase entirely — skipping the decade-long process of acquiring land, securing water rights, and negotiating power purchase agreements that ground-based data centers require.

## The NRI Angle

For Indian-origin professionals in Silicon Valley, Seattle, and the global semiconductor corridor, this partnership represents a category that barely existed 18 months ago. Orbital compute sits at the intersection of space technology, AI infrastructure, and sovereign technology policy — three domains where India has been building capability independently, but never combined them into a single commercial product.

The investment signal is worth watching. Pixxel has attracted backing from Google, Radical Ventures, and Omnivore. Sarvam counts Lightspeed and Peak XV among its investors. If Pathfinder works — if you can demonstrate commercially viable GPU inference in orbit, running Indian AI models on Indian hardware — the addressable market extends far beyond India to every country seeking compute sovereignty.

The satellite is being built. The launch window is seven months away. The frontier, for once, is not in a Bengaluru office park or a Bay Area garage. It is 400 kilometers straight up."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Maharashtra Just Offered 2,000 GPUs to Any Startup That Asks. India's AI Compute Race Is Getting Real.",
        "subheadline": "At Mumbai Tech Week 2026, Chief Minister Devendra Fadnavis announced a 'Compute as a Service' initiative — free GPU access for startups and researchers — while OpenAI, Meta, and Anthropic showcased at the country's largest AI festival.",
        "slug": make_slug("maharashtra-2000-gpu-compute-as-service-mumbai-tech-week"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Maharashtra's GPU initiative directly addresses the compute bottleneck that has forced Indian AI startups to depend on US cloud providers. For NRI tech founders considering return-to-India moves, state-backed GPU access changes the startup economics calculation significantly.",
        "tags": ["maharashtra", "mumbai-tech-week", "gpu", "ai-compute", "devendra-fadnavis", "india-ai", "startups"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Business News This Week", "url": "https://businessnewsthisweek.com/business/honble-chief-minister-shri-devendra-fadnavis-inaugurates-mumbai-tech-week-2026-announces-2000-gpu-compute-as-a-service-initiative/"},
            {"name": "IT Voice", "url": "https://www.itvoice.in/honble-chief-minister-devendra-fadnavis-announces-mumbai-tech-week-2026-by-team"},
            {"name": "Business News Matters", "url": "https://businessnewsmatters.com/every-creator-will-become-a-studio-industry-leaders-map-indias-ai-powered-storytelling-future-at-mumbai-tech-week-2026/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg",
        "body": """Mumbai's Jio World Convention Centre hosted something unusual this week: a state government openly competing for the attention of AI companies the way cities once competed for automobile factories.

At the inauguration of Mumbai Tech Week 2026, Maharashtra Chief Minister Devendra Fadnavis announced a "Compute as a Service" initiative offering 2,000 GPUs to startups, researchers, and AI developers. The proposition is straightforward — if you are building AI in Maharashtra, the state will give you the compute to train your models. No upfront hardware costs. No dependency on AWS, Azure, or Google Cloud pricing.

The announcement, made at India's largest AI-focused technology festival, came alongside showcases from OpenAI, Meta, Anthropic, Google Cloud, and Neysa — a lineup that would have been unimaginable at an Indian state government event even two years ago.

## The Compute Problem

To understand why 2,000 GPUs matter, you need to understand what has been holding Indian AI back.

Training a competitive large language model requires thousands of high-end GPUs running for weeks or months. A single NVIDIA H100 chip costs roughly $30,000. A cluster of 1,000 H100s — the minimum for serious foundation model work — represents a $30 million capital expenditure before you write a single line of code. Cloud alternatives are not much better: renting equivalent compute from AWS or Azure runs into hundreds of thousands of dollars per month.

This pricing structure has created a structural disadvantage for Indian AI startups. While US companies raise $100 million rounds with compute budgets baked in, Indian startups building sovereign AI models — companies like Sarvam AI, Krutrim, and BharatGPT — have had to either raise at Silicon Valley scales or accept architectural compromises.

Maharashtra's 2,000 GPU pool does not solve this entirely. But it lowers the barrier to experimentation. A researcher at IIT Bombay or a two-person startup in Powai can now test model architectures, fine-tune domain-specific models, or run inference workloads without the $50,000-per-month cloud bill that currently makes such experiments prohibitive.

## The AI Governance Showcase

The GPUs were the headline, but the governance demonstrations may have been the more telling signal.

Maharashtra showcased Mahavistar AI, a platform that provides hyperlocal weather updates, crop advisories, mandi prices, pest detection, and government scheme information to over four million farmers across the state. The system operates in local languages through both text and voice, addressing the interface gap that has historically limited digital adoption in rural India.

More striking was CIVIT — described as India's first AI-powered digital approval twin for building permissions. Built for Mumbai's BMC, the system uses 12 specialized AI agents to validate documents, identify compliance gaps, and assist architects through the notoriously opaque building approval process. Anyone who has navigated municipal bureaucracy in an Indian city — or watched a relative in India attempt it — will recognize the magnitude of that ambition.

These are not concept demos. Mahavistar is live, serving millions. CIVIT is in deployment. The state is not just talking about AI governance — it is running it.

## Mumbai's Positioning Play

The festival itself — organized by the Tech Entrepreneurs Association of Mumbai in collaboration with the state government and co-powered by Meta — reflects a deliberate effort to position Mumbai as India's AI capital.

Bengaluru has the talent density. Hyderabad has the data centers. Delhi has the policy levers. Mumbai is making a different bet: that the convergence of enterprise decision-makers, capital markets, startup talent, and digital infrastructure in a single city creates conditions that no other Indian metro can replicate.

The AI Excellence Awards, an early-stage startup showcase, and an AI-powered job fair with 25 companies offering 250 positions across a talent pool of 30,000 candidates were not afterthoughts. They were the infrastructure of an ecosystem play.

## What NRI Founders Should Notice

For Indian-origin technology professionals in the United States considering a return — a demographic that has grown significantly since 2023 — Maharashtra's compute initiative changes one of the most important variables in the startup equation.

The standard calculus has been: great talent in India, great market in India, but compute costs are the same as Silicon Valley because you are renting from the same cloud providers. State-subsidized GPU access does not eliminate that constraint, but it introduces a variable that did not exist before. If you can prototype and validate an AI product using free state compute, then raise a round, then migrate to commercial infrastructure — the early-stage economics look meaningfully different.

The 2,000 GPUs are a number. The signal is that Indian state governments now understand that the AI race is an infrastructure race, and they are willing to spend capital to compete in it. Whether 2,000 GPUs becomes 20,000 — and whether the initiative survives the inevitable bureaucratic friction of a government program — will determine if this was a press conference or a policy shift.

Mumbai Tech Week 2026 runs through May 30 at the Jio World Convention Centre. The GPUs, presumably, will take somewhat longer to arrive."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
