#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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
        "headline": "Cognizant Just Wired ServiceNow's AI Agents Into Its Own. The Company That Sells Indian Labor Is Selling Orchestration Now.",
        "subheadline": "The IT-services giant that employs hundreds of thousands of Indians is repositioning as the conductor of enterprise AI agents — a pivot that decides whether the diaspora's career ladder survives automation.",
        "slug": make_slug("cognizant-servicenow-ai-agents-neuro-orchestration-it-jobs-diaspora"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Cognizant employs more Indians than almost any US-listed firm; its bet that the future is orchestrating AI agents rather than writing code signals which skills will keep H-1B careers alive — and which won't.",
        "tags": ["cognizant", "servicenow", "agentic-ai", "indian-it", "h1b", "it-services"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Cognizant / PR Newswire", "url": "https://www.prnewswire.com/news-releases/cognizant-expands-cross-platform-agentic-ai-with-new-servicenow-ai-agent-interoperability-302803971.html"},
            {"name": "StockTitan — CTSH Stock News", "url": "https://www.stocktitan.net/news/CTSH/"},
            {"name": "IDC Global AI Tech Buyer Sentiment Survey", "url": "https://www.idc.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Cognizant%27s_Delivery_Center_in_Bangalore.jpg",
        "image_caption": "Cognizant's delivery center in Bangalore, one of the company's large Indian engineering hubs",
        "image_attribution": "Wikimedia Commons",
        "body": """Cognizant has spent three decades selling one thing better than anyone: armies of Indian engineers who could build and maintain the software that runs Western companies, cheaper than the West could do it itself. This week the company announced something that quietly admits that model is ending.

Cognizant said ServiceNow's AI agents now plug directly into its own Neuro AI Multi-Agent Accelerator — a layer that lets a company coordinate AI agents from different vendors, plus its own custom ones, from a single place. The pitch is no longer "we'll write your code." It's "we'll conduct the robots that write it."

## What actually changed

For years, AI agents from different vendors lived in isolation. A ServiceNow agent handling IT tickets couldn't easily talk to a Salesforce agent in the sales pipeline or a homegrown system in finance. Each needed its own connectors and manual babysitting. Cognizant's accelerator, built on the open Model Context Protocol, is meant to discover and route work across all of them automatically, while respecting ServiceNow's existing access controls and audit logs.

"Multi-agent systems are the future of enterprise AI," said Babak Hodjat, Cognizant's chief AI officer. "The value is in networks of agents working together rather than any single agent, platform or vendor." IDC research the company cited claims more than 70% of enterprises plan to invest in some mix of prebuilt, custom, and embedded AI agents over the next 18 months.

Translated from press-release English: the money is moving from people who do tasks to people who design and govern systems that do tasks.

## Why an Indian engineer should read this twice

Cognizant is, functionally, an Indian company with an American stock ticker. The bulk of its roughly 350,000 employees sit in India, and tens of thousands more work across the US on H-1B and L-1 visas. When Cognizant changes what it sells, it changes the career math for a very large slice of the diaspora's engineering class.

The old ladder was clear: join as a fresher, learn a stack, bill hours, climb. That ladder is built on volume — more tickets closed, more code shipped, more bodies on the project. Agentic orchestration is designed to compress exactly that volume. If one engineer supervising a network of agents can do the work of ten, the ten is what gets cut.

The market has already smelled it. On the day adjacent to the announcement, Cognizant shares slipped about 4.4%, and peers Accenture, Infosys, and Wipro moved down with it — a sector-wide flinch, not a company-specific stumble. Wall Street is repricing the whole labor-arbitrage business.

## The opportunity hiding inside the threat

There is a more hopeful reading, and it matters for anyone whose green-card clock is tied to one of these firms. The companies that win the agentic era will need people who understand both the messy reality of enterprise systems and the new orchestration tools sitting on top — and that hybrid skill is exactly what experienced Indian IT engineers already have. Knowing how a bank's claims process actually works is worth more, not less, when you're the one teaching agents to run it.

The engineers most exposed are the ones doing repeatable, well-documented work — the rung Cognizant built its empire on. The ones best positioned are those who move up into governance, integration, and the unglamorous job of making sure autonomous agents don't quietly break things in regulated industries.

## What's next

Watch Accenture's earnings, due this week — the firm employs more Indians than any other and serves as a referendum on whether clients are still paying for headcount or starting to pay for outcomes. Watch, too, whether Cognizant's India delivery centers shift their hiring mix toward AI-platform skills and away from raw coding seats. The company has told the market where it thinks the value is going. For the diaspora that built it, the question is whether they climb onto the new ladder before someone pulls up the old one.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "ISRO Is Betting Its Reputation on One Rocket Launch in Early July. After Two Failures, the Diaspora Is Watching Its Money Too.",
        "subheadline": "India's workhorse PSLV returns to the pad after back-to-back failures grounded a rocket that private startups and foreign clients depend on — and a new generation of NRI-backed space firms is riding on the comeback.",
        "slug": make_slug("isro-pslv-comeback-launch-skyroot-private-space-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "India's space program has become an investable sector, not just a source of pride; whether ISRO restores the PSLV's credibility shapes the bet NRI capital is making on Skyroot, Agnikul, and a privatized launch market.",
        "tags": ["isro", "pslv", "space-tech", "skyroot", "agnikul", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Indian Defence News", "url": "https://www.indiandefensenews.in/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
            {"name": "Wikipedia — 2026 in spaceflight", "url": "https://en.wikipedia.org/wiki/2026_in_spaceflight"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/PSLV-C50%2C_CMS-01-_Lift-off_003.jpg/1280px-PSLV-C50%2C_CMS-01-_Lift-off_003.jpg",
        "image_caption": "An ISRO PSLV rocket lifts off from Sriharikota carrying the CMS-01 satellite",
        "image_attribution": "Wikimedia Commons",
        "body": """For most of its life, ISRO's Polar Satellite Launch Vehicle was the boring rocket — and that was the highest compliment you could pay it. A success rate above 90%, a reputation for putting other countries' satellites into orbit on budget, the reliable mule of India's space program. Boring rockets are how you build a commercial launch business.

That reputation is now on the line. After two consecutive PSLV failures — EOS-09 in May 2025 and EOS-N1 in January 2026, both lost during the rocket's third stage — ISRO is preparing a comeback launch for late June or early July. Union minister Jitendra Singh confirmed the timeline. The agency has switched the vendor supplying the components blamed for the failures and insists the two faults were unrelated rather than a sign of something systemic.

## Why two failures are a bigger deal than they sound

A 90%-plus success rate means the PSLV almost never fails. So two misses in eight months isn't noise; it's a pattern that customers notice. And the PSLV's customers are no longer just ISRO. Foreign clients pay NewSpace India Ltd., the agency's commercial arm, to ride Indian rockets. ISRO says none of those clients have pulled their payloads — a quiet vote of confidence — but the next launch has to convert that patience into proof.

Singh framed it bluntly: the credibility of the PSLV is vital, and this mission is meant to restore it.

## The part the diaspora should care about

A decade ago, "Indian space" meant ISRO, full stop. National pride, the occasional viral Mars-mission cost comparison, and not much an investor could touch. That has changed. India has opened its space sector to private capital, and a cluster of startups — Skyroot Aerospace, which became India's first space-tech unicorn; Agnikul Cosmos; earth-observation firms like Pixxel and SatSure — now form an ecosystem that NRI investors and diaspora-backed funds are actively betting on. Skyroot's Vikram-1 is itself slated for a maiden orbital attempt this year.

Here is the dependency that ties it all together: most of these startups still lean on ISRO — for launch slots, for shared infrastructure, for the talent pipeline, and for the simple credibility that comes from a national program that works. When the PSLV stumbles, it doesn't just dent ISRO's order book. It raises the risk premium on every Indian space bet sitting in a diaspora portfolio. A clean comeback launch does the opposite: it tells global insurers and customers that the foundation under India's private space rush is solid.

## A homecoming of a different kind

For many in the diaspora, the space story carries an emotional charge that the IT-services story never did. Watching Indian rockets work is a different feeling from watching Indian engineers staff someone else's data center. And now that feeling has a financial expression — you can put money into the homeland's frontier industry rather than just cheering it.

That cuts both ways. Sentiment-driven investing in a hard-tech sector with long timelines and literal explosions as a failure mode is how people lose money. The same diaspora capital that rushed into Indian startups at frothy valuations could repeat the mistake in space, mistaking national pride for due diligence.

## What's next

The early-July PSLV mission is the one to watch — a success resets the narrative; a third failure would be a genuine crisis for the commercial program. Beyond it, ISRO has lined up an ambitious manifest, including uncrewed Gaganyaan test flights ahead of India's first human spaceflight. For the diaspora, the launch pad at Sriharikota has quietly become something it never used to be: a place where both pride and portfolios are riding on the same countdown.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Real AI War Isn't About Chatbots. It's About Who Owns the Data Underneath — and Indian Engineers Are Building Both Sides.",
        "subheadline": "Snowflake, Databricks, Microsoft and the model makers are converging on a single fight over the enterprise 'system of intelligence' — the layer that decides whose AI agents actually get to run a company.",
        "slug": make_slug("snowflake-databricks-system-of-intelligence-agentic-ai-data-platform-indian-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian data engineers staff the platform teams at Snowflake, Databricks, and every cloud fighting this war; the winner of the enterprise data-and-agent battle determines which skills — SQL warehousing or ML pipelines — keep diaspora careers in demand.",
        "tags": ["snowflake", "databricks", "agentic-ai", "data-engineering", "enterprise-ai", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "SiliconANGLE — Breaking Analysis", "url": "https://siliconangle.com/"},
            {"name": "MarketBeat — Snowflake news", "url": "https://www.marketbeat.com/stocks/NYSE/SNOW/"},
            {"name": "Data Engineer Academy", "url": "https://dataengineeracademy.com/"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17489163/pexels-photo-17489163.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Rows of servers in a modern data center, the physical backbone of the enterprise AI platform war",
        "image_attribution": "Pexels",
        "body": """Ask a casual observer who's winning the AI war and they'll name a chatbot — ChatGPT, Gemini, Claude. Ask the people who actually run enterprise software and you'll get a stranger answer: the war is over the data underneath, and the chatbots are just the part you can see.

A sharp analysis circulating this week reframed the whole contest. The fights everyone narrates separately — Snowflake versus Databricks, copilots versus agents, model makers versus app vendors — are really one question: who owns the new intelligent client, and the "system of intelligence" back end that makes it useful?

## The plain-English version

An AI agent is only as smart as what it knows about your specific business. A model can write beautiful code or summarize a contract, but it has no idea what your company's pricing rules are, how your supply chain actually behaves, or which customer is about to churn. That knowledge lives in your data — and in the messy, undocumented logic of how your business runs.

Whoever owns the layer that captures and encodes that knowledge — Snowflake with its CoWork and CoCo agents, Databricks with Genie, Microsoft with Copilot, Google with Gemini Enterprise, plus Salesforce, SAP and ServiceNow — owns the place where AI actually does work. The model is rentable. The system of intelligence is sticky. That's the prize.

Snowflake sits at the center of this not because it's winning, but because it's exposed: analysts at Jefferies still like it against Databricks, citing strong cash flow and a reasonable valuation, but everyone acknowledges the competition is intensifying, and the real rivals now include Microsoft, Google, and the model labs — not just the company across the street.

## Why this is a diaspora story

Walk the platform-engineering and data teams at any of these companies and you'll find Indian engineers everywhere — building the warehouses, the pipelines, the governance layers, the agent frameworks. This is one of the densest concentrations of diaspora talent in tech, and the outcome of the data-platform war directly reprices their skills.

Here's the fork. The Snowflake world rewards SQL fluency, analytics engineering, and clean warehouse design — the skill set a huge share of Indian data professionals built their careers on. The Databricks world rewards Spark, Python, ML pipelines, and heavier data engineering. The agentic layer on top rewards a third thing: people who can model business logic so that both humans and AI agents can act on it. An engineer who only knows one of these is betting their career on one platform winning. An engineer who can move across all three is irreplaceable regardless of who wins.

For the NRI working at one of these firms — or the one weighing job offers between them — the practical advice is to stop treating Snowflake-versus-Databricks as a religious war and start treating fluency in the connective tissue between them as the actual moat.

## The investor angle

For diaspora investors holding these names, the reframing is a warning against single-stock conviction. If the real contest is about owning the system of intelligence, then the winners may not be the pure-play data companies at all — they could be the cloud giants and model labs that already sit closer to where decisions get made. Snowflake's relatively modest valuation reflects exactly that uncertainty; the cheap multiple is the market hedging its bet.

## What's next

Watch how aggressively Snowflake and Databricks push their agent products into production rather than demos, and watch whether the model labs — OpenAI, Anthropic, Google — start reaching down into the enterprise data layer rather than staying at the model. The company that captures, harmonizes, and encodes how a business actually operates wins the decade. A lot of the engineers building that capture, on every side, will be Indian. The question for the diaspora is whether they're building the winning side — and whether they've kept their skills portable enough that it doesn't matter.
"""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK {art['slug']}")
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")
