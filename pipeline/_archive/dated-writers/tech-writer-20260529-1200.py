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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Intel's 230% Stock Surge Is the Chip Comeback Nobody Predicted",
        "subheadline": "The AI inference boom has turned Intel from Wall Street's punchline into its biggest semiconductor winner of 2026 — and thousands of Indian engineers in Bangalore helped make it happen.",
        "slug": make_slug("intel-230-stock-surge-cpu-inference-comeback"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Intel employs over 10,000 engineers in Bangalore and Hyderabad, making it one of the largest employers of Indian chip designers. The CPU inference boom creates massive upside for Indian semiconductor professionals and NRI investors who wrote Intel off.",
        "tags": ["intel", "semiconductors", "ai-inference", "cpu", "indian-tech-workers", "chip-stocks"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "MarketWatch", "url": "https://www.marketwatch.com"},
            {"name": "Barron's", "url": "https://www.barrons.com"},
            {"name": "Barchart", "url": "https://www.barchart.com"},
            {"name": "Reuters", "url": "https://www.reuters.com"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/10/Howard_Lutnick_with_Intel_CEO_Lip-Bu_Tan_%282025%29_%28cropped3%29.jpg",
        "image_caption": "Intel CEO Lip-Bu Tan, whose turnaround has sent Intel shares surging past their dot-com era highs. Photo: Wikimedia Commons",
        "body": """For a company that spent most of the past five years as Silicon Valley's cautionary tale — the chipmaker that missed mobile, fumbled manufacturing, and watched Nvidia eat its lunch — Intel's 2026 has been nothing short of extraordinary.

Intel's stock has rocketed 230% this year, making it the single best performer in the PHLX Semiconductor Index. That index itself has soared 79.3% in the first 100 trading days of 2026, shattering the previous record set during the dot-com boom of 1995. But while the broader chip rally has lifted all boats, Intel's surge stands apart — and the reason has everything to do with a tectonic shift in how AI actually works.

## The Inference Revolution

The story of AI's first wave was simple: train massive models using Nvidia's GPUs. Companies poured billions into graphics processors, and Nvidia's stock became the most watched ticker on Wall Street. But AI's second wave — inference, where trained models actually do things for users — runs on different hardware.

Inference workloads, particularly the "agentic AI" applications now proliferating across enterprise software, are CPU-hungry. As AI models shift from learning to doing — answering queries, executing multi-step tasks, running autonomous agents — the humble central processing unit has reclaimed strategic importance.

CEO Lip-Bu Tan, who took the reins from the ousted Pat Gelsinger, framed the opportunity in Intel's blowout Q1 2026 earnings call: while GPU-to-CPU ratios in training environments run 8-to-1, agentic workloads could push that ratio toward parity — or even invert it in Intel's favor. The numbers bore him out. Data Center and AI revenue hit $5.05 billion, up 22% year-over-year, crushing the $4.41 billion Wall Street had expected.

Demand was so fierce that Intel sold chips it had previously written off — legacy and de-spec product that had been shelved was pulled back into the supply chain because customers needed anything they could get.

## Why Indian Engineers Should Care

Intel's India operations aren't a satellite office. Bangalore houses one of Intel's largest design centers globally, with over 10,000 engineers working on everything from Xeon server processors to AI accelerators. Hyderabad adds another significant contingent. When Intel's fortunes rise, the career trajectories and compensation packages of thousands of Indian semiconductor professionals rise with them.

The CPU inference boom is also creating a structural demand shift that favors exactly the kind of work Intel's India teams do — low-level chip architecture, power optimization, and server platform design. For Indian engineers who spent years being told that GPUs were the only game in town, the inference revolution is vindicating.

For NRI investors, Intel's transformation demands a re-evaluation. At around $120 per share and a market cap north of $600 billion, Intel has surpassed its August 2000 dot-com high of $75 — a peak that stood for 26 years. At least 23 brokerages raised their price targets after Q1, with the median target jumping from $46.50 to $75 in a single month (and the stock has since blown past even that).

## The Broader Picture

Intel's resurgence doesn't exist in isolation. AMD has risen 131% this year, crossing $800 billion in market cap and unseating JPMorgan Chase. Samsung, Micron, and SK Hynix have all joined the trillion-dollar club. The SOX index's 79.3% gain is putting the dot-com rally to shame.

But Intel's story is the most dramatic because it involves genuine reinvention, not just riding the wave. Under Tan, Intel has refocused on foundry services, secured CHIPS Act funding for U.S. manufacturing, and — crucially — positioned its Xeon processors as the inference engines that every data center needs alongside its Nvidia GPUs.

The question for the next twelve months is whether Intel can sustain this momentum as Nvidia fires back with its own Vera CPU and AMD pushes aggressively into server processors. For the thousands of Indian engineers designing Intel's next generation of chips in Bangalore, the answer to that question is also the answer to their next performance review."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Jensen Huang Is Spending $150 Billion a Year in Taiwan. India Should Be Taking Notes.",
        "subheadline": "Ahead of Computex 2026, Nvidia's CEO doubled down on Taiwan as the 'epicentre of the AI revolution' — a commitment that dwarfs India's entire semiconductor ambition.",
        "slug": make_slug("nvidia-150-billion-taiwan-computex-india-semiconductor"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India's semiconductor mission, while ambitious, operates at a fraction of Nvidia's Taiwan spend. NRI investors and Indian engineers should understand how deeply the AI supply chain depends on Taiwan — and what it means for India's fab dreams.",
        "tags": ["nvidia", "taiwan", "computex", "semiconductors", "india-semiconductor-mission", "jensen-huang", "geopolitics"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/nvidia-taiwans-expanding-role-ai-infrastructure-set-take-centre-stage-computex-2026-05-29/"},
            {"name": "Barron's", "url": "https://www.barrons.com"},
            {"name": "DIGITIMES", "url": "https://www.digitimes.com"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
        "image_caption": "Nvidia CEO Jensen Huang in Taipei, where he announced plans to spend $150 billion annually with Taiwanese suppliers. Photo: Wikimedia Commons",
        "body": """Jensen Huang landed in Taipei more than a week early. By the time Computex 2026 officially opens on June 2, Nvidia's CEO will have already held a near-continuous stream of dinners and meetings with the people who actually build the AI revolution: TSMC CEO C.C. Wei, Foxconn Chairman Young Liu, Quanta Computer Chairman Barry Lam, and dozens of other supply chain executives.

The headline number he brought with him was staggering: Nvidia plans to spend as much as $150 billion a year in Taiwan.

"Four years ago, five years ago, Nvidia was spending about 10, 15 billion dollars a year in Taiwan," Huang told the crowd at the launch celebration for Nvidia's planned Taiwan headquarters. "Now we're spending 100, going to 150 billion dollars in Taiwan each year."

To put that in context: India's entire Semiconductor Mission — the government's flagship initiative to build a domestic chip ecosystem — has committed roughly $10 billion in incentives. Nvidia alone plans to spend 15 times that annually in a single island nation.

## Taiwan's Transformation

Taiwan's role in the AI economy has quietly evolved from a semiconductor story into an infrastructure story. The island doesn't just make chips anymore. It designs the advanced packaging, assembles the AI servers, builds the liquid cooling systems, and integrates the networking hardware that turns silicon into functioning data centers.

"The question is no longer only who makes the chip, but who can turn it into a powered, cooled, networked and serviceable AI system," said Ryan Fletcher, a partner at McKinsey & Company.

Nvidia's new Taiwan campus, breaking ground this year and operational by 2030, will employ 4,000 people. AMD's Lisa Su also committed $10 billion to Taiwan's AI sector last week. TSMC, the world's largest contract chipmaker, manufactures AI processors for Nvidia, AMD, Google, Amazon, Meta, and Microsoft — virtually every company building the AI future.

## The Geopolitical Shadow

Huang's massive bet comes with an unavoidable asterisk: Taiwan sits at the center of the world's most dangerous geopolitical flashpoint. President Trump recently suggested he might use a $14 billion U.S. arms package for Taiwan as a "negotiating chip" with China, comments that unsettled markets and diplomats alike.

For Nvidia, doubling down on Taiwan is a calculated gamble. The company's $5 trillion market cap depends on a supply chain that runs through an island Beijing considers its own territory. Huang has addressed this tension by framing Taiwan as irreplaceable — not vulnerable — arguing that the sheer depth of its manufacturing ecosystem makes it strategically untouchable.

## What India Should Learn

India's semiconductor ambitions are real and growing. Tata Electronics recently signed an MOU with Dutch lithography giant ASML to support its 300mm fab ramp-up in Dholera, Gujarat. Micron's $2.75 billion ATMP facility in Sanand has moved into production. India Semiconductor Mission 2.0 is targeting advanced nodes and compound semiconductors.

But the scale mismatch is sobering. Nvidia's annual Taiwan spend would fund India's entire semiconductor mission roughly every 25 days. More importantly, Taiwan's advantage isn't just money — it's a decades-deep ecosystem of packaging specialists, component suppliers, cooling engineers, and integration expertise that India is only beginning to cultivate.

For NRI engineers working at Nvidia, TSMC, or AMD in the Bay Area, the Taiwan-centricity of AI infrastructure means their work is more strategically important than ever. For NRI investors, Nvidia's concentration risk in Taiwan is worth understanding — the same geopolitical tensions that make the stock volatile also make the island irreplaceable.

India's semiconductor journey will take a generation. But watching Huang spend $150 billion a year next door should clarify both the scale of the opportunity and the distance still to travel."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Wix, Webflow, Cloudflare: AI Just Gutted Three Software Companies in One Week",
        "subheadline": "A brutal wave of AI-driven layoffs is reshaping the software industry — and Indian tech workers on H-1B visas have the most to lose.",
        "slug": make_slug("wix-webflow-cloudflare-ai-layoffs-h1b-workers"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian H-1B holders at software companies face a 60-day grace period to find new employment or leave the country when laid off. The AI-driven restructuring hitting SaaS and web-platform companies directly threatens the visa status and career stability of thousands of Indian tech workers.",
        "tags": ["ai-layoffs", "h1b-visa", "wix", "webflow", "cloudflare", "indian-tech-workers", "software-engineering"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "New York Post", "url": "https://nypost.com"},
            {"name": "CNN", "url": "https://www.cnn.com"},
            {"name": "Investor's Business Daily", "url": "https://www.investors.com"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6804068/pexels-photo-6804068.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The latest wave of AI-driven layoffs is hitting software companies hardest. Photo: Pexels",
        "body": """The numbers from the past few weeks tell a story that no amount of corporate euphemism can soften. Wix cut 1,000 employees — 20% of its workforce. Webflow gutted its engineering teams in what one former employee called a "bloodbath." Cloudflare fired 1,100 people. Upwork slashed 24% of its staff. In each case, the stated reason was the same: artificial intelligence.

This isn't the familiar tech layoff pattern of pandemic over-hiring followed by correction. These companies are cutting because AI is fundamentally changing what it takes to build and maintain software — and they're betting they can do the same work with dramatically fewer people.

## The New Math

Wix CEO Avishai Abrahami was unusually direct. AI, he said, means the company needs "fewer layers and fewer workers." It can now help companies "build things the previous generation literally could not have imagined." But the flip side is fewer humans needed to do the building.

At Upwork, the calculus was even starker. Revenue from AI-related freelance work grew 40% year-over-year — but CEO Hayden Brown acknowledged that since late February, "the pace of AI automation was faster than previously seen." Listings for tasks that AI can now handle "are basically burning off the platform." A marketplace built on connecting humans to work is watching AI vaporize the work itself.

Webflow's layoffs drew particular ire. A former software engineer told the San Francisco Chronicle that the C-suite "thinks that I'm being replaced by AI, but they don't actually understand what AI is doing." The counter-argument from management: CEO Linda Tong said AI is "rewriting the rules for how marketing teams create, test, and optimize digital experiences."

Cloudflare CEO Matthew Price was the most matter-of-fact, calling AI and agents "now core parts of our workforce" as he announced 1,100 cuts on May 7.

## The H-1B Vulnerability

For Indian tech workers in the United States, these layoffs carry a uniquely existential dimension. Under current immigration rules, H-1B visa holders who lose their jobs have a 60-day grace period to find new employment, transfer their visa, or leave the country. With a spouse and children often on dependent H-4 visas — and potentially years invested in a green card backlog — a layoff isn't just a career setback. It's a life disruption.

The companies cutting jobs are exactly the kind of mid-size SaaS and platform companies that employ thousands of Indian engineers. Cloudflare, Wix, Upwork, and Webflow all have significant engineering teams that include H-1B holders. When AI-driven restructuring hits, visa workers can't simply ride out a few months of unemployment like their citizen colleagues.

Boston Consulting Group estimated in April that 10 to 15 percent of U.S. jobs — 16 million to 24 million positions — are vulnerable to AI substitution over the next four to five years. The executive outplacement firm Challenger, Gray & Christmas reported that AI was the top reason companies cited for job cuts in April, for the second consecutive month.

## The Role Is Changing

The deeper shift isn't just about headcount — it's about what software engineering means. At Google, a DeepMind director told CNN that many internal apps are now "mostly" written by the company's AI coding tool. Anthropic's head of Claude Code said that 100% of his recent contributions to the product were written by AI. Boris Cherny suggested the title "software engineer" might eventually be replaced by something like "builder" — reflecting a job focused on high-level decisions rather than writing code.

For Indian engineers, many of whom entered the U.S. tech workforce through deep technical coding skills, this redefinition is both threat and opportunity. The threat is obvious: if the core skill that earned the H-1B petition is now automated, the value proposition changes. The opportunity is that Indian engineers with strong architectural thinking, system design experience, and product judgment are precisely the kind of "builders" these companies still need.

## What Comes Next

The layoff wave will accelerate. Every earnings call now includes a section on AI-driven productivity gains, and CEOs are under pressure from boards and investors to translate those gains into lower headcounts. Companies that don't cut will face questions about why they aren't leveraging AI to reduce costs.

For Indian tech workers, the playbook is uncomfortably clear: specialize in areas where AI augments rather than replaces, build toward roles with architectural and strategic scope, and maintain the professional network that can produce a job offer within 60 days if the worst happens. The software industry's AI reckoning has arrived, and it's moving faster than anyone predicted."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
