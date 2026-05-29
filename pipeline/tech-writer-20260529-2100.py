#!/usr/bin/env python3
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

# Verify images before using
def verify_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        return r.status_code == 200 and "image" in ct and cl > 5000
    except:
        return False

# Image URLs
img_deployCo = "https://images.pexels.com/photos/6804068/pexels-photo-6804068.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
img_h1b = "https://images.pexels.com/photos/36984937/pexels-photo-36984937.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
img_huawei = "https://images.pexels.com/photos/36169774/pexels-photo-36169774.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"

for name, url in [("deployCo", img_deployCo), ("h1b", img_h1b), ("huawei", img_huawei)]:
    if verify_image(url):
        print(f"✅ Image OK: {name}")
    else:
        print(f"⚠️ Image check failed: {name}")

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "OpenAI Just Declared War on India's $315 Billion IT Empire",
        "subheadline": "The launch of DeployCo, a $4 billion consulting arm with Forward Deployed Engineers, marks OpenAI's direct assault on the services business that sustains TCS, Infosys, and Wipro — and the hundreds of thousands of Indian engineers who work there.",
        "slug": make_slug("openai-deployco-india-it-services-threat"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Hundreds of thousands of Indian engineers work at IT services firms in India and abroad. OpenAI's consulting arm threatens the outsourcing model that's employed a generation of Indian tech graduates and funds remittances to families across the subcontinent.",
        "tags": ["openai", "indian-it", "infosys", "tcs", "ai-consulting", "deployco"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/infosys-ceos-compensation-rises-25-nearly-87-million-fiscal-2026-2026-05-29/"},
            {"name": "AI Business", "url": "https://aibusiness.com/nlp/openai-launches-ai-consulting-company-following-anthropic"},
            {"name": "The Consulting Report", "url": "https://theconsultingreport.com/openai-launches-dedicated-ai-consulting-venture-valued-at-14-billion/"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/india-at-a-crossroads/article69089245.ece"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": img_deployCo,
        "body": """On May 11, Sam Altman did something that should have sent tremors through every IT services boardroom from Bangalore to New Jersey. OpenAI launched the OpenAI Deployment Company — already known as DeployCo — a majority-owned consulting subsidiary backed by $4 billion in fresh capital at a $10 billion pre-money valuation.

The pitch is straightforward: embed Forward Deployed Engineers directly inside enterprise customers to redesign workflows around AI. Not advise. Not hand over a strategy deck. Actually sit with front-line teams, build production systems, and stick around until the thing works.

The investor list reads like a who's-who of capital that traditionally flowed to Indian IT outsourcers: TPG, Goldman Sachs, Bain Capital, McKinsey, Brookfield, SoftBank, and Capgemini. Nineteen founding partners in total. To staff up from day one, OpenAI acquired Tomoro, a London-based AI consulting firm with roughly 150 engineers — the unglamorous plumbing of SOC 2 certifications, scoping templates, and billing infrastructure that takes 18 months to build from scratch.

## The $315 Billion Question

India's IT services sector — dominated by TCS, Infosys, Wipro, and HCL Tech — generates $315 billion in annual revenue and employs over 5.4 million people. It is the single largest white-collar employer in the country and the backbone of India's middle-class economy.

The model is simple: take large enterprise technology projects, staff them with Indian engineers at a fraction of Western salaries, and deliver at scale. For three decades, this worked brilliantly.

Now the model faces a double threat. AI can automate the bulk coding, testing, and maintenance work that sustains the pyramid. And the companies building that AI are no longer content to sell tools — they want to do the deployment work themselves.

Indian IT stocks fell to their lowest point in three years after OpenAI's announcement. The timing was not coincidental.

## The Pay Paradox

Against this backdrop, Infosys CEO Salil Parekh took home ₹82.6 crore ($8.69 million) in fiscal 2026 — a 2% increase from the prior year, according to the company's annual report released Friday. Stock options worth ₹50.75 crore formed the bulk of his compensation. Parekh's pay was 742 times the median Infosys employee salary of ₹11.13 lakh.

For context, TCS CEO K Krithivasan earned $2.96 million for the same period. Infosys forecast revenue growth of just 1.5% to 3.5% for fiscal 2027 — below analyst expectations.

The irony is hard to miss. Executive pay keeps climbing at a company whose entire industry is being told it may be obsolete within a decade.

## The TCS-OpenAI Paradox

Here is where it gets strange. TCS already has a strategic partnership with OpenAI, signed in February 2026. Under that deal, Tata Group is building HyperVault AI data centers and thousands of employees got access to ChatGPT Enterprise.

But DeployCo changes the dynamic entirely. OpenAI is no longer just a technology partner — it is a direct competitor for the consulting dollars that IT services firms depend on. The $4 billion war chest, the embedded engineers, the acquisition pipeline — this is not a side project.

As one analyst at Omdia put it: "AI companies are looking in the mirror and deciding they want to be Palantir." The reference is to Palantir's Forward Deployed Engineer model, which has long bypassed traditional consulting firms by embedding directly with clients.

## What This Means for Indian Tech Workers

For the estimated 1.8 million Indian professionals working at GCCs (Global Capability Centers) of multinationals in India, the immediate impact is limited — GCCs are internal operations, not outsourcers. But for the remaining millions in the traditional services pyramid, the math is shifting.

TCS has already shed 25,000 employees in nine months while simultaneously doubling fresher intake — a classic sign of restructuring from experienced lateral hires toward cheaper, AI-augmented junior talent.

Consultant Pareekh Jain of Pareekh Consulting puts it bluntly: "AI will reduce bulk hiring in the Indian software services industry. Fresh graduates will have fewer mass-employment options."

For NRIs with family working at Indian IT companies, with retirement portfolios holding Infosys or TCS stock, or with children considering engineering careers in India — this is the story to watch. The $315 billion empire is not collapsing tomorrow. But the foundation is cracking, and the companies that built the cracks are now coming for the renovation contract too."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Federal Judge Just Asked the Question 300,000 H-1B Holders Are Thinking",
        "subheadline": "In a Boston courtroom on Friday, U.S. District Judge Leo Sorokin pressed the government on whether there is any limit to the president's power to price foreign workers out of America. Only 85 people have paid the $100,000 fee.",
        "slug": make_slug("h1b-100k-fee-court-challenge-trump-judge"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indians hold roughly 75% of all H-1B visas. The $100,000 fee has effectively frozen the program that built Silicon Valley's Indian engineering workforce. This court case will determine whether the fee stands — and with it, the future of tech immigration from India.",
        "tags": ["h1b-visa", "immigration", "indian-tech-workers", "trump", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/us-judge-questions-scope-trumps-power-impose-100000-h-1b-visa-fee-2026-05-29/"},
            {"name": "American Bazaar", "url": "https://www.americanbazaaronline.com/2026/05/28/h-1b-worker-shares-harsh-reality-of-us-tech-job-market/"},
            {"name": "Cameron Journal", "url": "https://cameronjournal.com/how-recent-immigration-policy-changes-are-reshaping-the-u-s-tech-industry/"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "image_url": img_h1b,
        "body": """The number tells you everything you need to know: 85.

That is how many employers have paid the $100,000 fee that President Trump imposed on new H-1B visa applications last September. Before the fee, tens of thousands of applications poured in during each filing window. The H-1B program offers 65,000 visas annually, plus 20,000 for workers with advanced degrees. Employers previously paid roughly $2,000 to $5,000 in fees depending on company size and circumstances.

On Friday, in a federal courtroom in Boston, U.S. District Judge Leo Sorokin heard arguments in a lawsuit brought by 20 Democratic state attorneys general challenging that fee — and he asked the question that has been haunting every H-1B holder, every Indian engineer on a transfer, and every HR department at every tech company in America.

"I'm trying to understand the government's position on the scope," Sorokin said. If the president can impose a $100,000 fee, can he impose a million-dollar fee? A ten-million-dollar fee? Is there any limit?

## The Government's Case

Tiberius Davis, a lawyer for the Department of Justice, argued that the president had lawfully imposed the fee under his "sweeping" authority under federal immigration law to restrict the entry of foreign nationals deemed detrimental to U.S. interests.

"The effect is to incentivize companies to train up and hire American workers," Davis told the court.

Sorokin acknowledged the language was "clearly broad." But the judge, appointed by President Obama, pushed back on whether the administration's reading of the law had any meaningful boundaries.

The case has not yet been decided, but the hearing itself marks a significant legal test of executive immigration authority — one with outsized consequences for the Indian tech diaspora.

## A Community in Limbo

Indians hold an estimated 72% to 75% of all H-1B visas issued in any given year. The program has been the primary legal pathway for Indian engineers, data scientists, and software developers to build careers in the United States for over two decades.

The $100,000 fee has not just reduced applications — it has fundamentally altered the calculus for companies considering foreign hires. A data engineer in Ohio recently posted on Reddit that he had applied to more than 1,500 jobs without receiving a single recruiter callback, despite three years of U.S. experience with cloud systems and production pipelines. The post triggered hundreds of responses from visa holders describing life "on a thread" — where a single layoff means not just unemployment, but potential deportation within 60 days.

The anxiety is compounded by the green card backlog. Per-country caps mean Indian nationals face wait times measured in decades for permanent residency. An engineer who entered the country at 25 on an H-1B may still be waiting for a green card at 50.

## The Offshoring Accelerant

The fee was designed to push companies toward hiring American workers. The unintended consequence — or perhaps the quiet one — is that it has accelerated offshoring.

A Moneycontrol analysis found that an increasing number of Silicon Valley firms are establishing innovation hubs in Canada, Europe, and India as alternatives to navigating the U.S. immigration system. India's Global Capability Centers — in-house tech operations run by multinationals — now employ 1.8 million professionals and generate $65 billion in revenue. Amazon has invested $35 billion in its India operations, Microsoft $17.5 billion, and Google $15 billion.

The arithmetic is simple: if bringing an engineer to San Jose now costs $100,000 in fees before you pay a dollar in salary, building a team in Hyderabad starts looking less like cost arbitrage and more like common sense.

## What the Court Decides Matters

If Judge Sorokin rules against the fee, it could reopen the H-1B pipeline and restore some predictability to a system that has been in chaos since September. If the fee stands, it will cement a structural shift in how U.S. companies access global talent — with Indian professionals bearing the heaviest burden.

For the 300,000-plus Indian-origin workers currently on H-1B visas in the United States, the stakes are personal. For the families sending children to American universities with the expectation that an H-1B will follow, the stakes are generational. And for India's IT services industry, already reeling from AI disruption, the fee represents one more crack in the foundation of a model that sustained an entire economy.

The judge has not indicated when he will rule. But for the Indian tech diaspora, this is not an abstract legal question. It is the question: does America still want us here?"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Huawei's 'Chip Queen' Just Unveiled a Replacement for Moore's Law. India's Semiconductor Bet Got More Complicated.",
        "subheadline": "He Tingbo's Tau Scaling Law and LogicFolding architecture promise 1.4nm-equivalent chip performance by 2031 — without the EUV machines that U.S. sanctions have blocked. For India's nascent fab industry, the implications are unsettling.",
        "slug": make_slug("huawei-tau-scaling-law-india-semiconductor"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India is betting billions on mature-node chip manufacturing at Dholera and Sanand. If Huawei proves that system-level optimization can bypass node scaling, it reshapes the value proposition of India's 28nm fabs — and the career calculus for every Indian semiconductor engineer deciding between TSMC, Intel, and returning home.",
        "tags": ["huawei", "semiconductor", "moores-law", "india-fab", "chip-geopolitics"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/huawei-bets-speed-over-shrinking-transistors-sidestep-us-chip-sanctions-2026-05-29/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/chinas-huawei-reveals-chip-design-breakthrough-amid-us-sanctions-2026-05-26/"},
            {"name": "Digital Trends", "url": "https://www.digitaltrends.com/computing/huawei-reveals-tau-scaling-law/"},
            {"name": "SiliconANGLE", "url": "https://siliconangle.com/2026/05/26/chinas-huawei-unveils-new-sanctions-busting-chip-architecture-replaces-moores-law/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": img_huawei,
        "body": """For decades, the semiconductor industry has operated under one guiding principle: make transistors smaller, pack more of them onto a chip, make everything faster. Moore's Law — the observation that transistor density doubles roughly every two years — has been the metronome of the computing age.

This week, Huawei said it has a new metronome.

At the 2026 IEEE International Symposium on Circuits and Systems in Shanghai, He Tingbo — president of Huawei's semiconductor business, 30-year company veteran, and the woman the Chinese tech press calls the "chip queen" — unveiled the Tau Scaling Law. The principle replaces geometric transistor shrinking with time scaling as the core measure of chip progress. Instead of making transistors smaller, make signals move faster through systems.

The key technology is called LogicFolding: an architecture that stacks logic, analog, and memory circuits in tightly connected three-dimensional structures. The goal is to shorten critical-path wiring, reduce signal-propagation delay, and improve both transistor density and circuit performance — all without requiring the extreme ultraviolet (EUV) lithography machines that U.S. sanctions have blocked China from importing since 2019.

Huawei says it has spent six years quietly validating the approach, mass-producing 381 chips based on Tau Scaling principles. The company claims the framework can achieve transistor density equivalent to 1.4 nanometers by 2031. TSMC, for comparison, expects to reach actual 1.4nm nodes by 2028.

## Breakthrough or Bluster?

The semiconductor establishment is skeptical but not dismissive. He Hui, director of semiconductor research at Omdia, called it "a credible way to extract more performance when leading-edge lithography is constrained." Others note that reducing latency and optimizing system-level integration have always been part of chip design — Huawei is packaging existing concepts under a new framework.

The eye-catching 1.4nm-equivalent projection is the keyword: equivalent. Huawei is not claiming it has built a 1.4nm fab. It is claiming its system-level approach can deliver comparable performance from chips manufactured at larger, sanctions-compliant nodes. China's most advanced domestic manufacturing capability remains widely assessed at around 7nm.

When U.S. markets opened after the announcement, Nvidia, AMD, and Intel shares rose. Wall Street, for now, is unimpressed.

But the DeepSeek precedent looms large. When that Chinese AI lab demonstrated competitive model performance at a fraction of the cost, global tech stocks briefly tanked. If Huawei demonstrates real-world performance parity through Tau Scaling, the market reaction could be very different.

## What This Means for India's Fab Ambitions

India has staked its semiconductor future on mature-node manufacturing. The Tata Electronics fab at Dholera, Gujarat — a partnership with Taiwan's PSMC — is designed to produce 300mm wafers at 28nm to 110nm nodes. It completed high-volume trial runs with 300mm wafers in January 2026 and is targeting first commercial silicon by December 2026. Micron's ATMP facility in Sanand is ramping for high-volume production. Intel just committed $3.3 billion to a substrate plant in Odisha.

The strategic logic has been sound: while TSMC, Samsung, and Intel fight over sub-5nm cutting-edge nodes for smartphones and AI accelerators, India would capture the "workhorse" market — the mature-node chips that power automobiles, 5G infrastructure, industrial systems, and defense electronics. These chips represent the bulk of global semiconductor volume.

Huawei's Tau Scaling Law complicates this picture. If system-level optimization can squeeze advanced-node performance from mature-node fabrication, it potentially positions Chinese foundries as competitors in segments India is targeting. A Chinese fab producing 28nm chips with Tau-optimized architectures could undercut Indian fabs on performance-per-dollar even at the same node.

## The Engineer's Calculus

For the thousands of Indian semiconductor engineers working at TSMC, Intel, Qualcomm, and Broadcom — and for the pipeline of IIT graduates considering careers in the field — Huawei's announcement adds a variable to an already complex equation.

India's semiconductor mission has created genuine opportunities. The Dholera and Sanand fabs will need thousands of skilled engineers. Qualcomm has 22,000 employees in India — 60% of its global workforce — and is expanding R&D. Intel's largest engineering site outside the U.S. is in India, with over 13,000 employees.

But if the semiconductor industry's axis of innovation shifts from node scaling to system-level architecture, the skills that matter change too. Packaging engineers, interconnect specialists, and system architects may become more valuable than process engineers obsessed with nanometer counts.

India's bet on mature-node fabrication remains fundamentally sound — the world needs far more 28nm chips than 3nm chips. But the assumption that mature nodes are a safe, uncontested market just got its first serious challenge. In geopolitics, as in semiconductors, the signal that matters is not the one you expected."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
