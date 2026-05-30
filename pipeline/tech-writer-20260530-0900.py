#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-30 09:00 UTC batch"""

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

def verify_image(url):
    """Verify an image URL returns a valid image."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", "0"))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image verified: {url[:80]}... ({cl} bytes)")
            return True
        else:
            print(f"  ✗ Image failed: status={r.status_code}, type={ct}, size={cl}")
            return False
    except Exception as e:
        print(f"  ✗ Image error: {e}")
        return False

# --- IMAGE SOURCING ---

print("=== Sourcing images ===")

# Article 1: Cognizant — corporate/IT services story, use Pexels
img_cognizant = "https://images.pexels.com/photos/5483059/pexels-photo-5483059.jpeg"
if not verify_image(img_cognizant):
    img_cognizant = "https://images.pexels.com/photos/7071/space-desk-office-workspace.jpg"
    verify_image(img_cognizant)

# Article 2: Anthropic — person story (Dario Amodei)
img_anthropic = fetch_wikipedia_person_image("Dario Amodei")
if not img_anthropic or not verify_image(img_anthropic):
    img_anthropic = "https://images.pexels.com/photos/8566534/pexels-photo-8566534.jpeg"
    verify_image(img_anthropic)

# Article 3: H-1B job market — tech worker story
img_h1b = "https://images.pexels.com/photos/4226218/pexels-photo-4226218.jpeg"
if not verify_image(img_h1b):
    img_h1b = "https://images.pexels.com/photos/52608/pexels-photo-52608.jpeg"
    verify_image(img_h1b)

print()

# --- ARTICLES ---

articles = [
    # ---- ARTICLE 1: Cognizant Project Leap ----
    {
        "id": str(uuid.uuid4()),
        "headline": "Cognizant's Project Leap Could Cut 15,000 Jobs. Most of Them Will Be in India.",
        "subheadline": "The New Jersey IT giant's AI restructuring may generate $300 million in savings — but its 250,000-strong India workforce is bearing the brunt.",
        "slug": make_slug("cognizant-project-leap-15000-jobs-india-ai"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Cognizant is the second-largest H-1B sponsor in the US. Its AI-driven restructuring directly threatens Indian tech workers on both sides of the ocean — those in Bengaluru and Chennai campuses, and those on H-1B visas in New Jersey, Texas, and the Bay Area.",
        "tags": ["cognizant", "layoffs", "ai-restructuring", "indian-it", "h1b"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Connected to India", "url": "https://www.connectedtoindia.com/cognizant-technology-solutions-plans-to-layoff-4000-jobs-reports-82948.html"},
            {"name": "Financial News India", "url": "https://financialnewsindia.com/cognizant-layoffs-2026-15000-cognizant-employees-to-lose-jobs-globally-major-impact-expected-in-india/"},
            {"name": "ETCIO via Owler", "url": "https://www.owler.com/reports/cognizant/cognizant-weighs-up-to-15-000-job-cuts-under-restructuring-plan/1748606412195"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": img_cognizant,
        "body": """When Cognizant CEO Ravi Kumar S unveiled Project Leap earlier this year, the messaging was familiar: streamline operations, boost AI capabilities, build a "future-ready" workforce. The numbers underneath that corporate poetry, however, are anything but gentle.

Reports now indicate that Cognizant is preparing to cut between 12,000 and 15,000 jobs globally — roughly 3-4% of its 357,000-strong workforce. The company had initially signalled around 4,000 reductions. The latest figures, reported by ETCIO and corroborated by multiple Indian business outlets, represent a significant escalation and place Project Leap among the largest single restructuring programmes in Indian IT services history.

## Where the Cuts Fall

Of Cognizant's global headcount, approximately 250,000 employees — over 70% — are based in India. While the company has not officially confirmed the geographic breakdown, industry analysts expect the majority of reductions to hit Indian campuses in Bengaluru, Chennai, Hyderabad, and Pune. The cuts are concentrated in mid-level roles, the very positions that form the backbone of India's IT outsourcing machine.

In a pointed contrast, Cognizant has said it plans to onboard more than 20,000 fresh graduates this year. The arithmetic is clear: replace experienced mid-level engineers with cheaper entry-level hires who can be trained on AI-first workflows from day one.

"In fostering a workforce that is appropriately sized, AI-enabled, and equipped with the skills required for future success, we aim to streamline operations and drive productivity through AI-led efficiencies," the company said in a statement that managed to use every corporate synonym for "layoff" without actually saying the word.

## The H-1B Shadow

For Indian tech workers in the United States, the implications are particularly acute. Cognizant has historically been one of the top H-1B visa sponsors in America, filing thousands of petitions annually to place Indian engineers at client sites across finance, healthcare, and retail. Workers on H-1B visas who lose their jobs face a 60-day grace period to find a new sponsoring employer — or leave the country.

The combination of Project Leap's mid-level focus and Cognizant's heavy US visa footprint means that some of the most vulnerable workers are those who have spent years building careers in America: data architects in New Jersey, SAP consultants in Dallas, cloud engineers in the Bay Area. For them, a restructuring spreadsheet in Teaneck is a ticking clock in a foreign country.

## The AI Calculus

Project Leap is expected to generate savings of $200 million to $300 million in 2026. That money is being redirected toward AI capabilities, integrated offerings, and partnerships — areas where Cognizant has lagged behind rivals Infosys and TCS in recent quarters.

The restructuring follows a pattern now visible across the Indian IT services industry. TCS cut thousands of experienced roles last year while expanding campus hiring. Infosys is aggressively reskilling its workforce for generative AI projects. Wipro just landed an agentic AI deal with ServiceNow that sent its ADR up 18% in a single day — the kind of market reaction that rewards companies for proving they can do more work with fewer people.

For Cognizant, the strategic logic is sound. Its revenue growth has been uneven, its margins have faced pressure, and clients are increasingly asking for AI-augmented delivery rather than headcount-heavy teams. The company cannot afford to be the last major Indian IT firm still running on a labour-arbitrage model in an age of autonomous code generation.

## What Comes Next

The severance costs will be substantial. Cognizant has budgeted for them under Project Leap's financial framework, though exact figures remain undisclosed. Indian labour law provides some protection for workers in India, but the practical reality for mid-career professionals — particularly those in their late 30s and 40s with mortgages and children in school — is a job market that has fundamentally shifted beneath their feet.

The industry that built middle-class prosperity for an entire generation of Indian engineers is now rebuilding itself around tools that do not need salaries, health insurance, or H-1B sponsorship. For the 15,000 workers who may receive that email in the coming months, the question is not whether AI is coming for their jobs. It is whether the next job will be there when they need it."""
    },

    # ---- ARTICLE 2: Anthropic India Expansion ----
    {
        "id": str(uuid.uuid4()),
        "headline": "Anthropic Just Named Its India Startup Chief. The $965 Billion AI Lab Is Done Window-Shopping.",
        "subheadline": "With Sangeeta Bavi leading startup growth and Irina Ghose running the Bengaluru office, Anthropic's India buildout is now the most aggressive of any frontier AI company.",
        "slug": make_slug("anthropic-india-sangeeta-bavi-startup-claude"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Anthropic's India expansion opens new career paths for Indian AI engineers and startup founders building on Claude. For NRIs considering return-to-India moves, Anthropic's Bengaluru office adds another frontier AI employer to the list alongside Google DeepMind and Microsoft Research India.",
        "tags": ["anthropic", "claude", "india-ai", "startups", "bengaluru"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CEO Vine", "url": "https://ceovine.com/anthropic-appoints-sangeeta-bavi-as-head-of-startups-and-growth-in-india/"},
            {"name": "Digitimes", "url": "https://www.digitimes.com/news/a20260528VL206/anthropic-claude-india-ai-startup.html"},
            {"name": "Martechai", "url": "https://martechai.com/anthropic-appoints-sangeeta-bavi-to-drive-startup-and-ai-growth-in-india/"},
            {"name": "CXO Digital Pulse", "url": "https://cxodigitalpulse.com/anthropic-strengthens-india-growth-push-with-sangeeta-bavi/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": img_anthropic,
        "body": """When Dario Amodei visited India late last year, the Anthropic co-founder spoke about alignment, safety, and the scale of India's technical talent. What he did not say — but what has become unmistakable in the months since — is that Anthropic has decided India is not a market to dabble in. It is a market to dominate.

The latest signal: the appointment of Sangeeta Bavi as Head of Digital Natives, Startups and Growth for India. Bavi, who previously served as COO at YourStory and spent nearly a decade at Microsoft building the company's startup business in India, is not a placeholder hire. She is a builder with deep roots in the Indian founder ecosystem, and her mandate is expansive: accelerate Claude adoption among startups, digital-first businesses, and mid-market enterprises across the country.

## The India War Room Takes Shape

Bavi's appointment is part of a broader leadership buildout that has quietly made Anthropic's India operation the most senior and most structured of any frontier AI lab in the country.

Irina Ghose, formerly of Microsoft India, was named Managing Director for India earlier this year. Rahul Patil, Anthropic's global CTO of Indian origin, has been instrumental in shaping the Bengaluru strategy. Additional hires across partnerships and business development have followed. The Bengaluru office — Anthropic's second in the Asia-Pacific region after Tokyo — is expected to be fully operational by mid-2026.

The scale of the investment becomes clearer when you consider the competitive landscape. OpenAI has made intermittent forays into India but has not established a dedicated office or leadership team of this depth. Google DeepMind has a significant research presence in Bengaluru, but its commercial operations are largely integrated into Google Cloud. Meta AI's India presence is research-focused. Anthropic is the only frontier AI company building a standalone commercial operation in India with dedicated startup, enterprise, and partnerships leadership.

## Why India, Why Now

The business case is compelling. India is currently one of Claude's fastest-growing markets globally, contributing a significant share of global usage. The country's developer base — estimated at over 5 million software developers — represents the largest pool of potential Claude API customers outside the United States. Indian startups, from fintech to edtech to healthtech, are increasingly building AI-native products, and many are evaluating which frontier model to build on.

Anthropic's pitch to Indian founders is straightforward: Claude is the best model for enterprise work that requires safety, reliability, and nuance. The company's emphasis on responsible AI development — constitutional AI, interpretability research, and alignment work — resonates with Indian enterprises operating in regulated sectors like banking, insurance, and healthcare.

For startups specifically, Bavi's background at Microsoft gives her a playbook for the kind of ecosystem development that works in India: developer advocacy, startup credits, co-building programmes, and strategic integration partnerships with the VCs and accelerators that fund India's next generation of technology companies.

## The Diaspora Dimension

For NRIs in the technology industry, Anthropic's India expansion adds a new data point to the return-to-India calculation. Bengaluru already hosts research labs for Google, Microsoft, Amazon, and Meta. Adding a frontier AI company that is valued at $965 billion — a figure that would have seemed absurd even two years ago — means that Indian AI engineers no longer need to be in San Francisco to work at the cutting edge.

It also creates a new competitive dynamic for Indian IT services companies. Anthropic's Claude Cowork, launched in January 2026, can automate coding, debugging, and deployment tasks that form the bread and butter of firms like TCS, Infosys, and Wipro. Early adopters have reported productivity gains of 40-60%. If Anthropic succeeds in making Claude the default AI assistant for Indian startups and enterprises, the downstream effects on the traditional IT services labour model could be profound.

## What Bavi Inherits

The opportunity is real, but so are the challenges. India's AI market is price-sensitive. Many startups currently use open-source models or cheaper alternatives to frontier APIs. Claude's pricing, while competitive globally, faces resistance in a market where a $20/month API bill can be a meaningful line item for a seed-stage company.

Anthropic will also need to invest in Indic language capabilities. India's 22 official languages and hundreds of dialects present a localisation challenge that no frontier AI lab has fully solved. The company has spoken about these plans but has not yet shipped production-grade Indic language support for Claude.

What Bavi brings, above all, is credibility with the people who matter most: the founders. She knows their language, their constraints, and their aspirations. In a market where every AI company is making grand promises, having someone who has actually built startup ecosystems before is Anthropic's most important asset in India."""
    },

    # ---- ARTICLE 3: H-1B Job Market Reality ----
    {
        "id": str(uuid.uuid4()),
        "headline": "An H-1B Data Engineer Applied to 1,500 Jobs. Not One Recruiter Called Back.",
        "subheadline": "A viral Reddit post from an Ohio-based visa holder has reignited a conversation Indian tech workers have been having quietly for months: the American tech job market is broken for immigrants.",
        "slug": make_slug("h1b-data-engineer-1500-jobs-no-callback-tech"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indians constitute roughly 75% of H-1B visa holders in the US. This story directly affects hundreds of thousands of Indian tech workers and their families who have built lives in America under the assumption that specialised skills would always find employment.",
        "tags": ["h1b", "tech-jobs", "immigration", "layoffs", "indian-tech-workers"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "American Bazaar", "url": "https://www.americanbazaaronline.com/2026/05/29/h-1b-worker-shares-harsh-reality-of-us-tech-job-market/"},
            {"name": "Marketplace (NPR)", "url": "https://www.marketplace.org/2022/11/09/with-tech-layoffs-visa-workers-could-lose-right-to-stay-in-the-us/"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/tech-industry-layoffs-mean-added-headaches-for-h-1b-visa-workers"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": img_h1b,
        "body": """The numbers were stark even before you got to the punchline. More than 1,500 job applications. Months of searching. Three-plus years of experience in cloud systems, ETL workflows, and production data pipelines. Not a single recruiter callback.

The Reddit post, written by a Data Engineer based in Ohio who identified himself as an H-1B visa holder, went viral this week on immigration and tech career forums. "I honestly never thought I would be in this situation," the user wrote. Hundreds of responses poured in — from fellow H-1B workers, former visa holders who had already left, and American tech workers who said the job market felt just as hostile from their side of the fence.

The thread crystallised something that Indian tech workers across the United States have been discussing in private WhatsApp groups, LinkedIn DMs, and weekend dinner conversations for the better part of two years: the American tech job market, particularly for visa-dependent workers, has fundamentally changed.

## The Structural Shift

This is not simply a cyclical downturn. The wave of layoffs that swept through Big Tech in 2023 and 2024 — Meta, Google, Amazon, Microsoft, Salesforce — was followed not by a recovery in hiring, but by a permanent recalibration of how technology companies build teams.

Companies that once hired aggressively for headcount are now hiring selectively for capability. AI tools have compressed the work that once required teams of five into tasks manageable by two. Managers who previously signed off on H-1B transfer petitions without a second thought are now asking whether the role can be automated or offshored entirely.

The result is a job market that still posts openings — Indeed and LinkedIn are full of them — but responds to applications at rates that would have been unimaginable five years ago. Multiple commenters on the Reddit thread reported similar experiences: 500, 800, 1,200 applications with zero or single-digit responses.

## The 60-Day Clock

For H-1B holders, the mathematics of unemployment are existential in a way that American workers simply do not experience. Under current immigration rules, a laid-off H-1B worker has approximately 60 days to find a new employer willing to sponsor their visa. Fail to do so, and the worker must leave the country — regardless of how many years they have lived in America, how much they have paid in taxes, or whether their children are enrolled in local schools.

Indians, who constitute roughly three-quarters of all H-1B holders in the United States, face an additional burden: the per-country green card cap means that even workers who have been in the US for a decade or more may be decades away from permanent residency. They exist in a legal limbo where they are too established to leave easily but too temporary to stay with confidence.

"You spend 10 years building a life," one former H-1B holder told Marketplace. "And now you have 60 days to sell your house, to sell your car, to get your kids out of school, and leave the country."

## The Sponsorship Drought

The problem is not just layoffs. It is the evaporation of visa sponsorship itself. Companies that were once reliable H-1B sponsors — mid-tier IT services firms, consulting companies, regional banks with technology operations — have quietly pulled back. The cost of sponsorship, combined with increased USCIS scrutiny, higher filing fees (the registration fee alone jumped from $10 to $215 for FY2026), and the legal overhead of compliance, has made many employers conclude that hiring American workers or using contractors is simply less complicated.

For the Ohio Data Engineer and thousands like him, this means competing not just against other qualified candidates, but against the structural disincentives that make employers reluctant to even consider visa holders. The job may exist. The skills may match. But the three letters — H-1-B — on the application are enough to move a resume from the "maybe" pile to the "not worth the paperwork" pile.

## What the Data Shows

The broader numbers support the anecdotal evidence. Tech industry layoffs in 2026 are running at a pace comparable to 2023, according to FRED data and independent layoff trackers. Meta alone has cut approximately 8,000 workers this year while simultaneously reassigning 7,000 to AI projects. Intuit filed WARN Act notices for over 1,000 workers in California and Nevada. Webflow, Cloudflare, and Groupon have all announced AI-driven restructurings.

Meanwhile, new H-1B registrations continue at high volumes, creating a growing pool of workers competing for a shrinking number of sponsoring positions. The mismatch between supply and demand is producing exactly the kind of desperation visible in that Reddit thread.

## The Quiet Conversation

In Indian-American communities across the Bay Area, the Research Triangle, and the New Jersey tech corridor, the conversation has shifted from "how do I get promoted" to "how do I stay." WhatsApp groups that once traded salary benchmarks and interview tips now share immigration attorney contacts and emergency fund calculators.

Some are exploring plan B: returning to India, where a booming AI startup ecosystem and companies like Anthropic, Google, and Microsoft are expanding their Bengaluru operations. Others are considering Canada, which has actively marketed its immigration system as a more predictable alternative. A few are shifting to entrepreneurship, converting to O-1 "extraordinary ability" visas that do not depend on employer sponsorship.

None of these options are easy. All of them require the kind of calculated risk-taking that brought most H-1B workers to America in the first place. The difference is that this time, the gamble is not about building a career. It is about preserving one."""
    },
]

# --- PUBLISH ---

print("=== Publishing articles ===")
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles processed.")
