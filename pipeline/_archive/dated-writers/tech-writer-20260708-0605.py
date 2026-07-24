#!/usr/bin/env python3
"""Technology writer — 2026-07-08 06:05 PDT batch"""

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
    # ─────────────────────────────────────────────────────────────────
    # ARTICLE 1: OpenAI GPT-5.6 Public Launch
    # ─────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Washington Just Cleared GPT-5.6 for the World. Here's What Indian Developers Get on Thursday.",
        "subheadline": "After weeks of government testing and security reviews, OpenAI's most powerful model family goes public — with Elon Musk's Grok 4.5 crashing the party on the same day.",
        "slug": make_slug("openai-gpt56-sol-launch-india-developers"),
        "category": "technology",
        "vertical": "ai",
        "diaspora_angle": "Indian AI engineers at OpenAI helped build these models, Indian startups are among the heaviest API consumers, and the new government oversight framework will shape how quickly India gets access to frontier AI.",
        "tags": ["ai", "openai", "gpt-5.6", "frontier-models", "sam-altman", "national-security"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/openai-gets-us-approval-broad-gpt-56-rollout-axios-reports-2026-07-08/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/amp/corporate/us-gives-green-light-to-openais-gpt-5-6-here-s-what-it-can-do"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/openai-gets-us-approval-for-broad-gpt-56-rollout-axios/article69768382.ece"},
            {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/GPT-5.6"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg",
        "image_caption": "Sam Altman, CEO of OpenAI, at a meeting in Washington in February 2025",
        "image_attribution": "Wikimedia Commons",
        "body": """The waiting is nearly over. OpenAI confirmed late Tuesday that it will publicly launch GPT-5.6 — its most advanced model family to date — on Thursday, after the U.S. Department of Commerce completed a government-mandated security review and gave its approval.

The launch ends a tense three-week standoff between Silicon Valley's most valuable AI company and Washington. When OpenAI first previewed GPT-5.6 on June 26, it was forced to limit access to a small group of vetted partners at the government's request, citing national security concerns about frontier AI capabilities in cyberattack acceleration and biological threat identification.

## Three Models, Three Price Points

The GPT-5.6 family comes in three tiers. Sol sits at the top — OpenAI's flagship, with a "max reasoning effort" mode for deep problem-solving and an "ultra mode" that deploys multiple sub-agents in parallel. On benchmarks, Sol scored 91.9% on TerminalBench 2.1 in ultra mode, beating Anthropic's Mythos 5 at 88.0%. It also matched Mythos on ExploitBench, a cybersecurity benchmark, using roughly a third of the output tokens.

Terra is the workhorse: competitive with the previous-generation GPT-5.5 at half the cost. Luna is the budget play, fast and affordable for high-volume work.

For Indian startups running tight margins on AI-powered products — and there are hundreds of them, from Sarvam AI to Krutrim to the growing cohort building on top of OpenAI's APIs — Terra may be the most consequential release. A model that matches GPT-5.5 at 50% of the price changes unit economics overnight.

## The Government Gets a Seat at the Table

The delay itself is the bigger story. President Trump's June executive order established a voluntary framework under which AI developers can provide "covered frontier models" to the government for up to 30 days before public release. OpenAI's Commerce Department testing, conducted by the Center for AI Standards and Innovation, is the first major test of that framework.

This matters for India because the same oversight infrastructure is now shaping who gets access to frontier AI and when. Anthropic's Mythos 5 and Fable 5 were abruptly disabled for all users after a June 12 export control order; those restrictions were only lifted last week after Anthropic implemented additional safeguards. If Washington decides a model poses national security risks, India's access isn't guaranteed — and Delhi knows it.

India's own AI governance framework, still in draft, has been deliberately permissive compared to the EU's heavy-handed AI Act. But as frontier models become more capable and more tightly controlled by Washington, the question shifts from whether India will regulate AI to whether India can even get unrestricted access to the best models.

## The Competition Heats Up

The timing is no coincidence. On the same day OpenAI announced the GPT-5.6 public launch, Elon Musk said SpaceXAI would also make its leading model Grok 4.5 available to the public. The AI arms race now has three serious contenders — OpenAI, Anthropic, and SpaceXAI — all releasing their most powerful models within weeks of each other.

Meanwhile, China's authorities have held meetings with top tech firms about potentially restricting overseas access to China's own most advanced AI models. The result is a bifurcating world where the frontier of AI increasingly runs along geopolitical fault lines.

For the estimated 300,000 Indian AI engineers and researchers working across these companies in the U.S. — and the thousands more building on their APIs from Bengaluru, Hyderabad, and Pune — Thursday's launch is not just a product update. It is the opening round of a new era in which governments, not just companies, decide who gets to use the most powerful tools ever built.

*The GPT-5.6 Sol, Terra, and Luna models are expected to be available through OpenAI's API and ChatGPT starting Thursday.*"""
    },

    # ─────────────────────────────────────────────────────────────────
    # ARTICLE 2: China Claude Code Backdoor Alert
    # ─────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "China Just Called Anthropic's Claude Code a Security Threat. Alibaba Already Banned It.",
        "subheadline": "Beijing's cybersecurity authority says Claude Code secretly transmits user data to remote servers. The move deepens the US-China AI cold war — and Indian developers are caught in the crossfire.",
        "slug": make_slug("china-claude-code-backdoor-alibaba-ban-india"),
        "category": "technology",
        "vertical": "ai",
        "diaspora_angle": "Indian AI engineers and startups are heavy Claude Code users; as the US-China AI war escalates, India must navigate which AI tools it can safely adopt without getting locked into either bloc's restrictions.",
        "tags": ["ai", "anthropic", "claude-code", "china", "alibaba", "cybersecurity", "geopolitics"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/litigation/china-issues-backdoor-security-alert-over-anthropics-claude-code-2026-07-08/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/articles/china-says-it-has-found-security-vulnerabilities-in-anthropics-claude-code"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/amp/corporate/alibaba-bans-claude-code-after-anthropic-s-theft-allegations"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/07/04/alibaba-reportedly-bans-employees-from-using-claude-code/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Dario_Amodei_at_TechCrunch_Disrupt_2023_01_%28cropped%29.jpg",
        "image_caption": "Dario Amodei, CEO of Anthropic, whose Claude Code tool has been flagged by China's cybersecurity authorities",
        "image_attribution": "Wikimedia Commons",
        "body": """China's National Vulnerability Database dropped a bombshell on Wednesday: Anthropic's Claude Code, the AI coding tool that has become indispensable to developers worldwide, contains what Beijing's cybersecurity platform called a "serious security backdoor."

The government-run NVDB said in a WeChat statement that Claude Code versions 2.1.91 through 2.1.196 include a built-in monitoring mechanism capable of transmitting sensitive information — including users' geographic location and identity-related identifiers — to remote servers without consent. It advised organizations to immediately uninstall affected versions or upgrade to the latest release.

The alert came hours after Alibaba confirmed it would ban all employees from using Claude Code starting July 10, classifying the tool as "high-risk software" and directing its workforce to switch to Qoder, Alibaba's internally developed AI coding platform.

## The Backstory Is Uglier Than the Alert

The security alert did not emerge in a vacuum. It follows weeks of escalating hostilities between Anthropic and Chinese AI companies.

In June, Anthropic sent a letter to two U.S. senators accusing Alibaba of illicitly extracting Claude's capabilities through "distillation" — a technique where a weaker model is trained on outputs from a stronger one. Anthropic argued the practice amounted to a massive subsidy for America's geopolitical competitors, turning "hundreds of billions of dollars in American investment and R&D" into a gift for China.

Alibaba's stock dropped 7.3% on the news.

Then came the Reddit exposé. Developers discovered that certain versions of Claude Code contained mechanisms that inspected user environments, checking timezone and proxy-related information, and inserted subtle markers into prompts sent to Anthropic's servers. In effect, the code could identify users accessing Claude from China.

An Anthropic employee confirmed on X that the feature was "an experiment we launched in March" to prevent account abuse by unauthorized resellers and protect against distillation. He said the team had "landed stronger mitigations since then" and had been meaning to remove it.

China's NVDB alert reframes that experiment as espionage. Whether it is a legitimate security concern or political retaliation depends on which side of the Pacific you are sitting on.

## Why Indian Developers Should Pay Attention

Claude Code has become one of the most popular AI coding assistants globally, and Indian developers are among its heaviest users. Anthropic's Claude models power everything from code generation to document analysis across India's startup ecosystem and its outsourcing giants.

The escalating US-China AI cold war creates a specific risk for India. On one side, Washington is tightening export controls on frontier AI models — Anthropic's Mythos and Fable were temporarily disabled for all users in June under a national security order. On the other, Beijing is now flagging American AI tools as security threats and potentially restricting its own models from overseas access.

India sits uncomfortably in the middle. The country's developers and IT services firms need access to the best tools from both ecosystems. If forced to choose sides, the economic consequences could be severe. TCS, Infosys, Wipro, and HCL collectively employ hundreds of thousands of developers who use a mix of American and Chinese AI tools daily. Indian AI startups building on Claude's APIs face the additional risk that Anthropic's anti-China measures could inadvertently flag Indian users accessing services through VPNs or shared infrastructure.

The practical advice for Indian engineering teams is straightforward: audit which Claude Code version your organization runs, update to the latest release, and begin evaluating alternatives. The deeper concern is strategic. India's AI sovereignty — the ability to build, access, and deploy AI tools without being subject to the security politics of either Washington or Beijing — is no longer a theoretical policy question. It is an operational one.

*Anthropic has not publicly responded to China's NVDB alert. The ban on Claude Code at Alibaba takes effect July 10.*"""
    },

    # ─────────────────────────────────────────────────────────────────
    # ARTICLE 3: Apple Loses EU DMA Court Challenge
    # ─────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Apple Just Lost Its Biggest European Court Battle. India's Antitrust Watchdog Is Taking Notes.",
        "subheadline": "The EU's General Court dismissed every Apple challenge to the Digital Markets Act. With India's own antitrust case heating up, the ruling could reshape how the App Store works for a billion users.",
        "slug": make_slug("apple-eu-dma-court-loss-india-antitrust-cci"),
        "category": "technology",
        "vertical": "tech-regulation",
        "diaspora_angle": "Indian app developers pay Apple's 30% commission on every in-app purchase; the EU ruling could set precedent for India's CCI case that would benefit the thousands of Indian iOS developers and NRI investors holding Apple stock.",
        "tags": ["apple", "eu", "digital-markets-act", "antitrust", "india", "app-store", "regulation"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/apple-loses-challenges-against-eu-rules-curb-big-tech-2026-07-08/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/articles/apple-loses-court-battle-over-ios-and-app-store-under-eus-tech-rules"},
            {"name": "MacRumors", "url": "https://www.macrumors.com/2026/06/03/apple-agrees-financial-data-india-antitrust/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/apple-withholds-data-india-antitrust-case-watchdog-sets-final-hearing-2026-04-09/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Tim_Cook_March_2026_%28cropped_2%29.jpg",
        "image_caption": "Apple CEO Tim Cook, whose company lost its challenge against the EU's Digital Markets Act",
        "image_attribution": "Wikimedia Commons",
        "body": """Apple's legal strategy in Europe hit a wall on Wednesday. The EU's General Court in Luxembourg dismissed every one of the company's challenges to the Digital Markets Act, affirming that Apple's App Store and iOS operating system are correctly classified as "gatekeeper" platforms subject to strict competition obligations.

The ruling was comprehensive. Apple had argued that its five App Stores — across iPhones, iPads, Macs, Apple TVs, and Apple Watches — should be treated as separate platforms, not a single core service. The court disagreed. "Irrespective of the devices in question, those stores have the same purpose, namely to connect app developers with end users in order to facilitate the distribution of software applications," the judges wrote.

Apple also challenged a Commission probe into whether iMessage should be subject to the DMA. The court called that action "inadmissible."

## What the DMA Actually Demands

The Digital Markets Act, which took effect in May 2023, is Europe's most aggressive attempt to rein in Big Tech. It designates companies that control key digital infrastructure — app stores, search engines, browsers, messaging platforms — as "gatekeepers," then imposes a list of dos and don'ts. The penalties for non-compliance can reach 10% of global annual turnover, which for Apple means fines north of $39 billion.

Among the DMA's most consequential requirements: gatekeepers must allow third-party app stores, permit developers to use alternative payment systems, and stop steering users toward their own services. Apple has complied grudgingly, introducing third-party app stores in the EU while imposing new fees — 13% for smaller businesses, up to 20% for App Store purchases — that critics say violate the spirit of the law.

The European Commission already fined Apple €500 million earlier this year for obstructing developers from guiding users to alternative payment methods. Wednesday's court ruling removes Apple's best legal argument for resisting further enforcement.

## India Is Running a Parallel Case

Here is where it gets interesting for the diaspora. India's Competition Commission (CCI) has been running its own antitrust investigation into Apple's App Store practices since 2021, triggered by complaints from a non-profit group, Tinder-owner Match, and Indian startups.

CCI investigators concluded in 2024 that Apple exploits its dominant position in the apps market by forcing developers to use its proprietary in-app purchase system — essentially the same finding the EU reached. Apple has pushed back, arguing it is a small player in India, where Android phones dominate with over 90% market share.

But the CCI is not buying it. After Apple withheld financial data and attempted to stall proceedings by challenging India's penalty law in the Delhi High Court, the watchdog set a final hearing date. Apple recently agreed to hand over its financial data, a signal that the case is nearing resolution.

The EU court ruling strengthens the CCI's hand. Regulators in India routinely look to EU precedent when building competition cases, and a definitive court victory in Luxembourg makes it harder for Apple to argue that its App Store practices are lawful.

## What This Means for Indian Developers

India's iOS developer community is growing fast. Apple's share of India's smartphone market has climbed from 2% to 9% in five years, and the company has significantly expanded manufacturing in the country. More Indian developers are building iOS apps, and every one of them pays Apple's 30% commission on in-app purchases (15% for small businesses under $1 million in annual revenue).

If the CCI follows the EU's lead and forces Apple to open its payment ecosystem, Indian developers could save millions collectively. For NRI investors, the picture is more mixed — Apple stock dipped on the news, but the company's $3.5 trillion market cap can absorb regulatory headwinds.

Tim Cook issued a carefully worded response: "We firmly believe the DMA's mandate goes beyond what is lawful and proportionate, threatening to erode decades of privacy and security protections we've built and leaving our users vulnerable to new risks." Apple can still appeal to the Court of Justice of the European Union.

But the trajectory is clear. The era of unchallenged app store gatekeeping — in Europe, in India, and increasingly in the United States, where the American Innovation and Choice Online Act is making a fresh run through Congress — is drawing to a close.

*Apple can appeal the ruling to the Court of Justice of the European Union. India's CCI is expected to issue its final order in the coming months.*"""
    },
]


for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline'][:80]}...")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
