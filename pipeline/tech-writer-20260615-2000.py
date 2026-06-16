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

NADELLA_IMG = "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg"
CHIP_IMG = "https://images.pexels.com/photos/785418/pexels-photo-785418.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
SECURITY_IMG = "https://images.pexels.com/photos/60504/security-protection-anti-virus-software-60504.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Shareholders Sue Satya Nadella's Microsoft, Saying It Hid How Much AI Was Eating Azure",
        "subheadline": "A Michigan pension fund's class action accuses Microsoft of masking slowing cloud growth while quietly diverting chips to prop up Copilot. The stakes reach every Indian engineer whose stock grant is tied to MSFT.",
        "slug": make_slug("microsoft-shareholder-lawsuit-nadella-azure-copilot-securities"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Tens of thousands of Indian engineers at Microsoft hold MSFT stock as a core part of their compensation, and the lawsuit's claims about Copilot's struggles cut to the heart of where their employer is betting its future.",
        "tags": ["microsoft", "satya-nadella", "azure", "copilot", "indian-tech", "ai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/microsoft-sued-by-shareholders-over-expenses-cloud-business-ai-2026-06-15/"},
            {"name": "Stocktwits", "url": "https://stocktwits.com/news-articles/markets/equity/msft-stock-rises-despite-shareholder-lawsuit"},
            {"name": "Business Wire / Rosen Law Firm", "url": "https://www.businesswire.com/news/home/microsoft-msft-stockholders-rights"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": NADELLA_IMG,
        "image_caption": "Microsoft chairman and CEO Satya Nadella, named as a defendant in the proposed shareholder class action.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """A pension fund for police officers and firefighters in suburban Detroit has done something the AI boom's cheerleaders rarely have to confront: it has put Microsoft's spending spree in front of a federal judge.

On June 12, the City of St. Clair Shores Police and Fire Retirement System filed a proposed class action in Seattle federal court accusing Microsoft of defrauding investors. The claim is that the company, led by chairman and chief executive Satya Nadella and finance chief Amy Hood, inflated its stock price by hiding how badly its prized Azure cloud business was slowing — even as it quietly poured billions into artificial intelligence.

The trigger was a single brutal day. After Microsoft's earnings report in late January, the stock fell about 10 percent, erasing roughly $357 billion in market value — its worst single-day drop in nearly six years. The proposed class period runs from May 1, 2025 to January 28, 2026.

### What the lawsuit actually alleges

Strip away the legal boilerplate and the complaint tells a specific story. Microsoft, the plaintiffs say, did not disclose that its Copilot family of products had run into trouble — weak adoption, data-siloing headaches, and a flagship in-house AI model that ranked below rivals on benchmark tests. To shore up Copilot's competitive position, the suit alleges, Microsoft had to divert GPU and CPU capacity away from the profitable Azure services that customers were actually paying for, and spend billions more than it let on.

The numbers around the quarter are not in dispute. Azure and other cloud revenue grew 39 percent, meeting forecasts but down from 40 percent the prior quarter. Capital spending hit $37.5 billion, up nearly 66 percent year over year and well above the roughly $34 billion analysts expected. Microsoft attributed the slowing growth and ballooning spend to capacity constraints as it shifted resources toward AI and Copilot.

Microsoft calls the claims "without merit" and says it "stands by the integrity of its public statements." Several plaintiffs' firms, including Rosen Law and Robbins Geller, are now circling for lead-counsel status — the familiar choreography after any sharp, unexpected stock decline.

### Why an NRI engineer should read past the headline

For the Indian diaspora, this is not abstract courtroom drama. Microsoft employs tens of thousands of Indian professionals, many on H-1B and L-1 visas, and for most of them a meaningful slice of pay arrives as restricted stock units that vest over years. When MSFT loses $357 billion in a day, it is not only Wall Street that feels it — it is the down payment on a house in Redmond or Hyderabad, the cushion that makes the visa gamble worth taking.

There is a second, more strategic reason to pay attention. The lawsuit is essentially a bet that Copilot, the product Nadella has staked the company's AI identity on, is underperforming against Google's Gemini and OpenAI's models. Indian engineers building on Azure, or weighing whether to join Microsoft's AI org over a rival's, are effectively making the same wager every day with their careers. A legal filing that forces internal numbers into the open could tell them more about Copilot's real traction than any keynote.

### The market shrugged — for now

Tellingly, MSFT shares actually rose about 2.3 percent the Monday after the suit surfaced, and 53 of 56 analysts still rate the stock a buy, with an average target implying close to 40 percent upside. Securities class actions are routine after big drops, and most settle quietly years later. The proxy that matters, as one analyst put it, is whether Azure's growth and Microsoft's $135 billion of OpenAI exposure hold up — not whether a Michigan pension fund wins its motion.

But the case lands at an awkward moment for the whole industry. Regulators are already probing Microsoft's bundling and cloud dominance, and shareholders elsewhere are starting to ask whether the AI capex arms race is disciplined investment or expensive faith. For Indian-origin leaders who now run a striking share of American tech — Nadella at Microsoft, Sundar Pichai at Alphabet, Arvind Krishna at IBM — the scrutiny that comes with the territory is intensifying. The question the St. Clair Shores fund is really asking is one every diaspora investor and employee is quietly asking too: how much of the AI story is growth, and how much is hope dressed up as guidance?

### What's next

Microsoft will move to dismiss, as defendants almost always do, and the fight over lead plaintiff will play out over the coming weeks. The disclosures that emerge — if the case survives that long — will be worth more than the eventual settlement. For anyone whose paycheck, portfolio, or career path runs through Redmond, the fine print of this complaint is the most candid read on Copilot they are likely to get this year."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Your Company's AI Agents Just Became Employees. NewCore Raised $66 Million to Give Them ID Badges.",
        "subheadline": "A stealth startup from Dome9's founder argues the identity systems guarding enterprise data were built for humans logging into web apps — not millions of autonomous agents. For India's security engineers, it names the next big job market.",
        "slug": make_slug("newcore-66-million-ai-agent-identity-agentic-security"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "India supplies a large share of the world's enterprise cybersecurity and identity-management engineers, and the scramble to govern AI agents is opening a new, well-funded specialization that diaspora professionals are positioned to lead.",
        "tags": ["cybersecurity", "ai-agents", "identity", "startups", "enterprise-ai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/15/as-ai-agents-become-employees-newcore-emerges-with-66m-to-give-them-identities/"},
            {"name": "SiliconANGLE", "url": "https://siliconangle.com/2026/06/15/newcore-launches-security-first-identities-ai-agents-66m-seed/"},
            {"name": "PR Newswire / Morningstar", "url": "https://www.morningstar.com/news/pr-newswire/newcore-emerges-from-stealth-66m"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": SECURITY_IMG,
        "image_caption": "Enterprise identity has become the primary attack surface — and AI agents are widening it.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """For two decades, the question enterprise security teams asked was simple: who is logging into our systems? NewCore, a startup that came out of stealth on June 15 with $66 million in seed funding, argues the question has changed. It is no longer who. It is what.

The "what" is the swarm of AI agents now being deployed across companies — autonomous software that spins up in seconds, demands fine-grained access to production systems, and then, often, vanishes. Goldman Sachs has tested an AI coding agent as a new hire. McKinsey says 25,000 AI agents already work alongside its 60,000 humans. NewCore's bet is that these digital workers need to be managed exactly like human employees: authenticated, governed, given permissions, and revoked when their job is done.

### A familiar founder, a $300 million valuation

The round was led by cybersecurity specialist Cyberstarts, with Index Ventures and Evolution Equity Partners joining, valuing the company at $300 million. The pedigree is the pitch. Co-founder and CEO Zohar Alon previously built cloud-security firm Dome9, acquired by Check Point in 2018. His CTO, Amihai Neiderman, is a former research leader at Israel's Unit 8200 signals-intelligence unit; chief commercial officer Erez Yarkoni was once CIO of T-Mobile USA and Telstra.

Their thesis is blunt. "The scale and the complexity that those things are going to add to 15- or 20-year-old identity platforms are going to break them," Alon told TechCrunch. The dominant identity systems, he argues, were architected for a world of employees signing into web apps — built on aging protocols like SAML, static service accounts, and password-derived session tokens. None of that was designed to be the security perimeter for millions of agents.

NewCore's answer leans on what it calls Secure Split Key technology, hardware-bound verification, and continuous discovery of shadow accounts and ungoverned agents — and it ships with support for the coding agents engineers actually use, including Claude Code, Codex, and Cursor.

### Why this is a diaspora story

On its face, NewCore is an Israeli-American company with no obvious India angle. Look closer and it names a market the Indian diaspora is unusually well positioned to own.

Identity and access management — the unglamorous plumbing of enterprise security — has long been disproportionately staffed by Indian engineers, in Bengaluru delivery centers, in the security orgs of every major US bank, and across the consulting giants. Okta, AWS, Veza, Silverfort, and Token Security have all launched or expanded non-human identity products over the past year. That is not a single startup's gamble; it is an emerging category, and categories create careers.

For an Indian engineer at a US firm watching AI automate away routine coding work, "securing the agents" is one of the few job descriptions getting more headcount, not less. The breaches that made identity the top attack surface — MGM, Change Healthcare, the Snowflake-customer compromises — were not exotic. They were old identity infrastructure asked to do a job it was never built for. Fixing that, for an enterprise now running thousands of agents, is durable, well-paid work.

### The catch

The skeptic's view is that NewCore is selling a problem before most companies feel the pain. Plenty of enterprises are still figuring out whether to trust AI agents with production access at all, let alone how to issue them revocable credentials at scale. And the incumbents are not asleep: when AWS bakes agent-identity controls directly into its cloud, a startup has to prove it does something the platform can't.

But the direction of travel is hard to argue with. If McKinsey already runs 25,000 agents internally, the governance bill comes due whether or not the tooling is mature. NewCore's $66 million says investors believe the agentic enterprise is arriving faster than its security can keep up — and for the diaspora's deep bench of identity engineers, that gap is the opportunity."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Wants to Make Its Own Memory Chips. The Minister in Charge Thinks the AI Data-Center Boom Will Force It.",
        "subheadline": "Ashwini Vaishnaw says rising AI demand will pull both existing and new investors into Indian memory-chip production, as the Semiconductor Mission pivots from building fabs to designing chips and the machines that make them.",
        "slug": make_slug("india-memory-chips-ism-2-vaishnaw-ai-data-center-demand"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For NRI semiconductor engineers and investors weighing a move home or a bet on Indian chip stocks, the shift from foreign fabs to indigenous chip design is the clearest signal yet of where the opportunities — and the jobs — will be.",
        "tags": ["semiconductors", "india-semiconductor-mission", "memory-chips", "ai-infrastructure", "make-in-india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/vaishnaw-expects-more-companies-to-start-production-of-memory-chips-in-india/"},
            {"name": "AInvest", "url": "https://www.ainvest.com/news/india-aims-boost-semiconductor-production-new-investments"},
            {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/indias-semiconductor-moment-from-diplomatic-frameworks-to-factory-floors/"}
        ]),
        "score_total": 73,
        "status": "review",
        "published_at": now,
        "image_url": CHIP_IMG,
        "image_caption": "A circuit board with mounted chips — India is pushing from packaging plants toward memory production and chip design.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """India has spent the last three years persuading the world's chipmakers to build factories on its soil. The next phase, according to the minister steering the effort, will be pulled along by something India can't manufacture its way out of: the insatiable hunger of AI data centers for memory.

Ashwini Vaishnaw, the Union minister for electronics and IT, said this week he expects more companies — both existing investors scaling up and new entrants — to start producing memory chips in India to close a widening demand-supply gap. The driver, he argued, is the rapid build-out of AI data centers, which consume high-bandwidth memory in enormous volumes. "Looks like both might happen," he said of the prospect that incumbents expand and newcomers arrive.

### From building fabs to designing chips

The more consequential shift is strategic. India Semiconductor Mission 1.0, launched in December 2021, was about fabrication and packaging — getting plants physically built. Vaishnaw says ISM 2.0 will reorder the priorities: chip design first, then the equipment used to manufacture semiconductors.

That second piece is ambitious. Vaishnaw said the government will court the equipment makers — the specialized toolmakers that even Taiwan and South Korea largely import — to both design and build their machines in India, and will look at indigenous production of the complex chemicals and gases that fabrication requires. ISM 1.0, he noted, drew roughly 48 startups into chip-related products; design will be the "topmost priority" the second time around.

The foundation is already pouring. A $2.75 billion Micron facility in Gujarat and a $10.9 billion Tata Electronics–PSMC joint venture, also in Gujarat, anchor India's assembly, testing, and packaging capacity. With the Cabinet's recent clearance of four more projects, the number of approved units under the mission has climbed, spread across multiple states.

Vaishnaw's pitch to the hyperscalers rests on three claims: a deep talent pool, a near-new electricity grid with more than 200,000 kilometers of transmission lines added in a decade, and abundant renewable power — close to half of installed generation capacity. Those are exactly the inputs an AI data center cares about.

### What it means for the diaspora

For the Indian diaspora, the memory-chip story is more concrete than the usual "India rising" rhetoric, and it cuts in two directions.

First, jobs and return decisions. The global semiconductor workforce is thick with Indian engineers — at Micron, Intel, Qualcomm, Nvidia, and Applied Materials. For an NRI process engineer or chip designer in Boise or Austin who has wondered whether the India fab story is real enough to move home for, the pivot toward indigenous design is the signal that matters. Packaging plants employ technicians; design centers employ the high-value architects the diaspora has spent careers becoming. ISM 2.0's emphasis on design and equipment is where those roles will sit.

Second, the investment lens. NRIs tracking Indian equities have watched the country's IT-services giants stumble under "AI deflation," even as the chip ambition draws fresh capital. The two trends are connected: as AI commoditizes routine software work, India is trying to climb the value chain into hardware that AI cannot easily replace. Whether the memory-chip bet pays off depends on execution — the gap between a Cabinet approval and a wafer rolling off a line is measured in years — but the direction is unambiguous.

### The hard part

Skeptics have heard versions of this before. India has announced semiconductor ambitions for over a decade, and memory production in particular is brutally capital-intensive, dominated by a handful of players in Korea, the US, and Taiwan who guard their process technology fiercely. Designing the manufacturing equipment domestically is harder still; it is a niche so specialized that even chip superpowers depend on a few foreign suppliers.

What is different now is the demand pull. AI data centers need memory faster than the existing supply chain can deliver it, and India is offering land, power, and people at a moment when buyers are desperate to diversify away from a concentrated, geopolitically fragile supply base. Vaishnaw is betting that scarcity, not subsidy, will be what finally makes Indian memory chips inevitable. For the engineers and investors of the diaspora, it is a bet worth watching closely — and, for some, worth flying home for."""
    }
]

ok = 0
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        ok += 1
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\n{ok}/{len(articles)} articles inserted.")
