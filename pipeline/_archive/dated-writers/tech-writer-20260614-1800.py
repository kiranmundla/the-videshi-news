#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-14 18:00 UTC batch"""

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

# Verify image URLs
def verify_image(url):
    try:
        r = requests.get(url, timeout=10, stream=True, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # For wikimedia, content-length may not be present in stream
        if r.status_code == 200 and "image" in ct:
            chunk = r.raw.read(6000)
            if len(chunk) > 5000:
                return True
        return False
    except:
        return False

# Image URLs
h1b_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Federal_Building_and_United_States_Courthouse%2C_Rome%2C_GA.jpg/1280px-Federal_Building_and_United_States_Courthouse%2C_Rome%2C_GA.jpg"
modi_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/The_official_portrait_of_Shri_Narendra_Modi%2C_the_Prime_Minister_of_the_Republic_of_India.jpg/330px-The_official_portrait_of_Shri_Narendra_Modi%2C_the_Prime_Minister_of_the_Republic_of_India.jpg"
intel_image = "https://upload.wikimedia.org/wikipedia/commons/1/10/Howard_Lutnick_with_Intel_CEO_Lip-Bu_Tan_%282025%29_%28cropped3%29.jpg"

# Verify images
for name, url in [("H-1B", h1b_image), ("Modi", modi_image), ("Intel", intel_image)]:
    ok = verify_image(url)
    print(f"Image verify {name}: {'✅' if ok else '❌'} {url[:80]}...")

articles = [
    # ARTICLE 1: H-1B $100K Fee Legal Battle
    {
        "id": str(uuid.uuid4()),
        "headline": "A Federal Judge Just Killed the $100,000 H-1B Fee. The White House Is Already Fighting Back.",
        "subheadline": "The ruling dismantled Trump's six-figure visa surcharge as an unconstitutional tax — but a partial stay and DOJ appeal mean Indian tech workers are still in limbo.",
        "slug": make_slug("h1b-100k-fee-struck-down-appeal-indian-tech-workers"),
        "category": "technology",
        "vertical": "immigration",
        "diaspora_angle": "Hundreds of thousands of Indian tech professionals on H-1B visas — and the companies that sponsor them — face continued uncertainty as the legal battle over a fee that slashed applications by 27% heads to the appeals court.",
        "tags": ["h-1b", "immigration", "tech-hiring", "silicon-valley", "trump", "federal-court"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/"},
            {"name": "Reuters", "url": "https://www.reuters.com/"},
            {"name": "Inc.", "url": "https://www.inc.com/"},
            {"name": "USA Today", "url": "https://www.usatoday.com/"},
            {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/"}
        ]),
        "score_total": 88,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": h1b_image,
        "image_caption": "Federal courthouse in the United States, where legal battles over immigration policy are fought",
        "image_attribution": "Wikimedia Commons",
        "body": """The $100,000 question hanging over Silicon Valley's hiring pipeline just got a complicated answer.

On June 8, U.S. District Judge Leo Sorokin in Boston struck down the Trump administration's $100,000 surcharge on new H-1B visa applications, calling it an unconstitutional tax that Congress never authorised. The ruling was the first legal defeat for a policy that had fundamentally reshaped how American technology companies recruit foreign talent — the vast majority of whom come from India.

Then, almost as quickly as the celebration started, it stalled. By June 12, the Department of Justice filed an emergency motion to stay the ruling, and Sorokin agreed to pause his own order while the First Circuit Court of Appeals considers the government's case. The fee, for now, remains in legal purgatory.

## What the fee actually did

When Trump imposed the $100,000 surcharge via executive proclamation in September 2025, its effects were immediate and brutal. H-1B applications for the 2026 cycle plunged 27 per cent — from 470,342 to 343,981. Only about 60,000 people receive H-1B visas in any given year, but the application pool is the pipeline through which America's technology sector replenishes its workforce.

For Indian nationals, who account for roughly 73 per cent of all H-1B approvals, the arithmetic was devastating. A senior software engineer earning $200,000 at Google or Microsoft was now expected to absorb — or have their employer absorb — a fee that represented half a year's rent in the Bay Area. Smaller companies and startups, which lack the deep pockets of Big Tech, simply stopped filing.

The fee also introduced a wage-weighted lottery system, giving applicants with the highest salaries four times better odds of selection than those at the bottom. In theory, this rewarded merit. In practice, it created an incentive for employers to inflate salary offers — not because the job required it, but to game the lottery.

## The legal reasoning — and why it matters beyond immigration

Sorokin's ruling drew explicitly on the Supreme Court's February decision striking down Trump's sweeping import tariffs. In both cases, the core argument was the same: the executive branch had claimed powers that the Constitution reserves for Congress alone. The judge wrote that "the President had no power to levy a tax on H-1B petitions" and vacated the policy entirely.

The DOJ countered that the fee was not a tax but a lawful exercise of the president's foreign commerce and immigration powers. In its appeal filing, the government argued that "every day the district court's order remains in effect, additional aliens will rush to seek classification and entry as an H-1B nonimmigrant worker."

Two other lawsuits challenging the fee are pending — one in the Northern District of California, another in the D.C. Circuit. Plaintiffs in both cases cited Sorokin's reasoning as strengthening their own challenges.

## The PROTECT Act — Congress steps in

Meanwhile, Republican Representative Mike Kennedy of Utah has introduced the PROTECT Act, which would codify the $100,000 fee at the congressional level — neatly sidestepping the constitutional objection that sank the executive order. Kennedy's bill would require applicants to pay the greater of $100,000 or the prevailing wage, and compel companies to demonstrate that no American worker could fill the role before turning to foreign nationals.

The bill faces an uncertain path in a divided Congress, but its introduction signals that the fight over H-1B economics is far from over.

## What Indian tech workers should watch

For the roughly 600,000 Indian nationals currently working in the United States on H-1B visas, and the hundreds of thousands more in the queue, three things matter right now.

First, the partial stay means the $100,000 fee remains effectively in force until the First Circuit rules. Anyone planning to file a new H-1B petition should assume the surcharge applies.

Second, the DOL's separate proposal to raise H-1B prevailing wages by up to 33 per cent — which the National Foundation for American Policy has called likely illegal — could compound the cost burden if adopted.

Third, and most critically, the legal battle has exposed a structural vulnerability in the H-1B system that no single court ruling can fix. Whether the fee stands or falls, the era of cheap H-1B hiring is over. Companies are already restructuring their talent strategies, with some accelerating offshore operations and others investing in domestic training programmes.

For Indian engineers and their families, the $100,000 fee was never just about money. It was about whether America still wants them. The courts are still deciding."""
    },

    # ARTICLE 2: Bharat Innovates 2026 in Nice
    {
        "id": str(uuid.uuid4()),
        "headline": "Modi and Macron Just Put 120 Indian Deep-Tech Startups on a Stage in Nice. The Money Is Listening.",
        "subheadline": "Bharat Innovates 2026 brings Indian semiconductor, space, and biotech ventures face-to-face with 500 global investors — and it's happening the day before the G7.",
        "slug": make_slug("bharat-innovates-2026-nice-modi-macron-deep-tech-startups"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For NRI founders, investors, and professionals debating whether India's deep-tech ecosystem is real, Bharat Innovates is the strongest signal yet that New Delhi is channelling state machinery into turning lab breakthroughs into global businesses.",
        "tags": ["bharat-innovates", "modi", "macron", "india-france", "deep-tech", "startups", "semiconductors", "space-tech"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Careers360", "url": "https://news.careers360.com/"},
            {"name": "Livemint", "url": "https://www.livemint.com/"},
            {"name": "IANS", "url": "https://ianslive.in/"},
            {"name": "YourStory", "url": "https://yourstory.com/"},
            {"name": "Press Information Bureau", "url": "https://pib.gov.in/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": modi_image,
        "image_caption": "Prime Minister Narendra Modi, who co-inaugurated Bharat Innovates 2026 with French President Macron in Nice",
        "image_attribution": "Wikimedia Commons",
        "body": """In Nice, on the French Riviera, 120 Indian startups are doing something that would have been unthinkable a decade ago: pitching semiconductor designs, space propulsion systems, and AI-driven medical diagnostics to 500 global investors, with two heads of state watching.

Prime Minister Narendra Modi and French President Emmanuel Macron jointly inaugurated Bharat Innovates 2026 on June 14 at the Palais des Expositions, kicking off a three-day conclave that the Indian government is framing as its most ambitious deep-tech showcase ever. The timing is deliberate — the event runs through June 16, one day before the G7 Summit begins in nearby Evian.

## The pitch: India has moved past consumer apps

Bharat Innovates is not another startup beauty pageant. The 120 companies on stage were selected from nearly 3,000 applicants by a Technical Oversight Committee led by Prof. Ajay Kumar Sood, India's Principal Scientific Adviser. The sectors they represent — advanced computing, semiconductors, space technology, biotechnology, clean energy, healthcare, and advanced manufacturing — are a pointed message about where India wants its next generation of global companies to come from.

"India, a nation driven by research and innovation, is at the forefront of global innovation," Macron said at the inauguration, citing the Chandrayaan-3 moon landing as evidence that India's technical ambitions are not aspirational but proven.

The investor bench is deep. Rajan Anandan of Peak XV Partners, Prashanth Prakash of Accel India, Gaurav Deepak of Avendus Capital, and Pankaj Makkar of Bertelsmann India Investments are all in Nice. On the European side, executives from Prosus, Sony Innovation Fund, and multiple French deep-tech funds are in attendance.

## The Infosys connection

The programme carries a distinct Infosys fingerprint. Co-founder Narayana Murthy is delivering a keynote, while fellow co-founder Kris Gopalakrishnan is moderating a panel on building corridors for "trusted, inclusive and scalable AI." For a conference backed by the Ministry of Education, the heavy involvement of India's most iconic technology entrepreneurs signals that the government sees this as a bridge between academic research and commercial scale.

## Why NRIs should care

For Indian-origin professionals in Silicon Valley, London, and Toronto, Bharat Innovates answers a question that many have been asking with increasing seriousness: is India's deep-tech ecosystem mature enough to invest in, collaborate with, or return to?

The startups in Nice suggest the answer is shifting. Agnikul Cosmos, which has successfully tested India's first 3D-printed rocket engine, is present. Tricog Health, whose AI algorithms diagnose cardiac conditions faster than manual testing, is pitching its technology to European healthcare markets. Gudlyf Mobility, from Madurai — a Tier-2 city rarely associated with cutting-edge engineering — is showing off hydrogen storage cylinders that are 50 per cent lighter and cheaper than conventional metal alternatives.

"Coming from a Tier-2 city and being selected for this platform is a matter of pride," said Gudlyf co-founder Dr Ajeet Babu PK. That sentiment captures something important: India's innovation pipeline is no longer just an IIT-to-Silicon-Valley conveyor belt.

## The bigger picture: India-France as a tech axis

Bharat Innovates is a product of the India-France Year of Innovation, announced by Modi and Macron in February. France's own deep-tech credentials — Sophia Antipolis, Europe's original innovation cluster, sits just down the coast from Nice — make it a natural partner for India's ambitions.

The strategic logic extends beyond bilateral warmth. As the United States tightens immigration rules and China's tech ecosystem becomes increasingly walled off, India is positioning itself as the third pole of global deep-tech development. Having France, a G7 member with its own semiconductor and space ambitions, as an explicit partner adds diplomatic and commercial credibility.

For NRI investors, the commercial opportunity is straightforward. India's deep-tech startups are raising at valuations that look cheap by Silicon Valley standards, the government is providing infrastructure and market access at a scale that startup ecosystems in Southeast Asia cannot match, and the talent pipeline — fed by IITs, IISc, and an expanding network of research institutions — is deeper than ever.

The question is no longer whether India can produce deep-tech companies. It is whether the capital, both Indian and global, will arrive fast enough to scale them before the window closes."""
    },

    # ARTICLE 3: Intel Foundry Comeback
    {
        "id": str(uuid.uuid4()),
        "headline": "Intel's Stock Has Surged 450% This Year. Lip-Bu Tan's Foundry Gamble Is Starting to Pay Off.",
        "subheadline": "Bank of America just double-upgraded Intel to Buy after foundry wins from Google, Microsoft, and potentially Nvidia. The chip giant's most troubled division is becoming its strongest story.",
        "slug": make_slug("intel-foundry-comeback-450-rally-bofa-upgrade-lip-bu-tan"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Intel's revival directly affects the tens of thousands of Indian engineers who work at the company and across its supply chain — and its American foundry buildout could reshape the H-1B landscape for semiconductor talent.",
        "tags": ["intel", "semiconductor", "foundry", "lip-bu-tan", "bank-of-america", "ai-chips", "microsoft", "google"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "ainvest", "url": "https://ainvest.com/"},
            {"name": "Barchart", "url": "https://www.barchart.com/"},
            {"name": "Tom's Hardware", "url": "https://www.tomshardware.com/"},
            {"name": "The Motley Fool", "url": "https://www.fool.com/"},
            {"name": "WebProNews", "url": "https://www.webpronews.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": intel_image,
        "image_caption": "Intel CEO Lip-Bu Tan, who has overseen the company's foundry revival since taking the helm in 2025",
        "image_attribution": "Wikimedia Commons",
        "body": """A year ago, Intel was a punchline. The company had burned through CEOs, missed process node deadlines, and watched its market capitalisation collapse while Nvidia's tripled. Analysts wrote obituaries. Employees updated their LinkedIn profiles.

Then Lip-Bu Tan took over, and the math changed.

On June 11, Bank of America double-upgraded Intel from Underperform to Buy, lifting its price target from $96 to $135. The stock jumped 5 per cent in a single session to $112.90. But the real story is not the upgrade — it is the 450 per cent rally that preceded it. Intel has been 2026's most improbable comeback in American technology, and the foundry business that nearly killed the company is now the engine driving it.

## The foundry wins that changed the narrative

Intel's IDM 2.0 strategy — the bet that it could simultaneously design its own chips and manufacture silicon for external customers — was widely dismissed as a fantasy when Pat Gelsinger first articulated it. Under Tan, the strategy has started producing customers.

Google placed an order for more than three million of its next-generation TPUs to be manufactured on Intel's processes, scheduled for 2028 delivery. Microsoft committed to having its Maia 2 AI accelerator — a 144-billion-transistor monster designed to power Azure's inference workloads — built on Intel's 18A-P node, which uses backside power delivery and Gate-All-Around transistor architecture. The chip is expected to deliver 10 petaFLOPS of FP4 compute, a threefold increase over its predecessor.

Nvidia, meanwhile, is reportedly evaluating Intel's advanced packaging capabilities as a backup manufacturing option. For a company that has built its entire GPU empire on TSMC's foundries, even considering Intel is a vote of confidence.

At Computex 2026, Intel announced a partnership with Foxconn and SambaNova to build rack-scale AI infrastructure using Xeon processors. The company also unveiled Clearwater Forest, its first high-volume product on the 18A node, which serves as a live proof point for external customers evaluating the process.

## The numbers behind the hype

Q1 2026 told the story in hard figures. Intel posted revenue of $13.6 billion against a consensus estimate of $12.4 billion, and adjusted earnings per share of $0.29 versus the $0.01 analysts expected. Foundry revenue rose 16 per cent year-over-year to $5.4 billion, and the division's operating loss narrowed by $72 million sequentially.

The market rewarded that beat with a 24 per cent single-day surge in late April — Intel's best trading day since 1987.

Bank of America's upgrade was not just about the foundry wins. Its analysts also highlighted the broader server CPU opportunity. BofA expects the global server CPU market to grow nearly fivefold to over $170 billion by 2030, driven by agentic AI applications that rely on CPUs for control logic, plan execution, and scheduling — tasks where GPUs are less efficient. Intel and AMD dominate this market, and the coming wave of AI agent deployments could be as transformative for CPU demand as cloud computing was a decade ago.

## The Indian engineer question

Intel employs roughly 10,000 engineers in India and thousands more Indian-origin professionals across its American facilities in Oregon, Arizona, New Mexico, and Ohio. The company's foundry expansion — new fabs in Arizona and Ohio, advanced packaging capabilities, and a growing design services arm — is creating demand for exactly the kind of semiconductor talent that India produces in abundance.

This matters in two directions. For Indian engineers already at Intel, the company's revival has transformed their career calculus. Retention bonuses and stock appreciation have made staying attractive in ways that were unthinkable eighteen months ago.

For the broader diaspora, Intel's American manufacturing buildout represents a structural demand driver for semiconductor H-1B hires at a moment when immigration policy is in flux. The company has been one of the most vocal corporate advocates for skilled immigration, and its expansion provides political cover for maintaining visa pathways — it is difficult to argue against importing talent to build chips on American soil when national security is the stated priority.

## The valuation question

The risk, as BofA's own analysts acknowledge, is that Intel's stock has already priced in much of the good news. A 450 per cent rally in six months is not the mark of a cheap stock. The company still carries a foundry operating loss, 18A yields have historically lagged expectations, and the revenue from major external customers like Google and Microsoft will not materialise until 2028.

But for investors who have watched Intel stumble for a decade, the narrative shift is unmistakable. The question is no longer whether Intel can compete. It is whether the market has left any room for latecomers to profit from the answer."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
