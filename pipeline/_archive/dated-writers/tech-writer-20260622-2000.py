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
        "headline": "Arvind Krishna Spent Years Calling IBM an AI Company. Now He's Buying OpenAI's Help to Prove It.",
        "subheadline": "IBM joined OpenAI's cyber program and put a $5 billion bet behind securing the world's open-source code. For Indian engineers in security and consulting, it redraws where the jobs are.",
        "slug": make_slug("ibm-openai-cyber-daybreak-project-lightwell-arvind-krishna-nri-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "IBM's pivot to AI-driven application security reshapes the career math for the tens of thousands of Indian engineers in its security, consulting and Bengaluru delivery arms, even as CEO Arvind Krishna warns the broader AI buildout may be a bubble.",
        "tags": ["ibm", "openai", "arvind-krishna", "cybersecurity", "ai", "indian-tech", "h1b"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "PR Newswire / IBM", "url": "https://www.prnewswire.com/news-releases/ibm-and-openai-bring-frontier-ai-to-cyber-defensehelping-enterprises-keep-pace-with-machine-speed-threats-302806843.html"},
            {"name": "StockTitan", "url": "https://www.stocktitan.net/news/IBM/ibm-and-openai-bring-frontier-ai-to-cyber-defense-helping-enterprises-keep-pace-with-machine-speed-threats"},
            {"name": "CRN Australia", "url": "https://www.crn.com.au/news/ibm-think-2026-showcases-agentic-ai-and-sovereign-cloud-strategy"},
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/zohos-sridhar-vembu-warns-against-chasing-ai-investment-bubble"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Arvind_Krishna_at_SXSW_2025.jpg/1280px-Arvind_Krishna_at_SXSW_2025.jpg",
        "image_caption": "IBM Chairman and CEO Arvind Krishna speaking at SXSW in 2025",
        "image_attribution": "Wikimedia Commons",
        "body": """On Monday, IBM did something that would have been unthinkable a decade ago, when it was still trying to convince Wall Street that Watson was the future of artificial intelligence: it signed up to use a rival's models. The company joined OpenAI's **Daybreak Cyber Partner Program** and launched a managed application-security service built on OpenAI's frontier cyber models — not its own.

The service is the visible tip of something larger. IBM is calling it **Project Lightwell**, a $5 billion commitment from IBM and Red Hat to patch, validate and manage open-source code across the software supply chain. Instead of just scanning code for known flaws, the OpenAI-powered tool is meant to prioritise vulnerabilities, validate whether they are actually exploitable, and do it with read-only, governed access inside a client's own environment.

For Arvind Krishna, the Hyderabad-born CEO who has spent six years repositioning a 114-year-old hardware company as an enterprise-AI and hybrid-cloud business, the message is pragmatic to the point of bluntness: own the workflow and the trust layer, and you don't need to own the model.

## Why a model deal is really a services deal

It is easy to read this as IBM conceding the AI race. That misreads what IBM sells. At its annual Think conference in May, Krishna told analysts that a chatbot only captures "the first 20 percent of the value" — the rest comes from connecting an enterprise's messy data sources and infrastructure to make AI agents actually work. That connective tissue is consulting and managed services, and it is overwhelmingly delivered by people.

A large share of those people are in India. IBM's consulting and software arms run vast delivery centres in Bengaluru, Pune, Hyderabad, Kochi and Gurugram, and security operations is one of the labour-intensive functions IBM has been steadily moving toward AI assistance rather than headcount. An OpenAI-powered service that "validates" vulnerabilities is, in plain terms, automating a chunk of what junior security analysts do today.

## The bubble warning underneath

What makes this week interesting is that Krishna himself has been one of the loudest voices warning that the AI infrastructure boom is overheating. His scepticism was echoed on Monday by Zoho founder Sridhar Vembu, who said the massive data-centre buildout could be a bubble and that he would rather build core capability than chase it — "to some people that would sound defeatist, but we will talk in five years."

The IBM–OpenAI deal is the practical expression of that view. Rather than spending tens of billions to train frontier models it might never recoup, IBM is renting the model and selling the thing that is genuinely scarce: the ability to deploy it safely inside a bank, a hospital or a government agency. IBM's own research, released this month, found that 81% of executives say a seven-day AI-vendor outage would cause severe disruption, and that only 7% of companies have advanced controls over their AI dependencies.

## What it means for the diaspora

For an Indian engineer at IBM — or at the Indian IT firms that compete with it, like TCS, Infosys and Wipro — the strategic logic cuts both ways.

The opportunity: governed, security-focused AI deployment is exactly the high-trust, regulated work that is hard to offshore casually and hard to fully automate. Engineers who can wire frontier models into compliance, data-residency and zero-trust frameworks are moving up the value chain, not out of it. This is the work IBM is betting a $5 billion fund on.

The risk: the same tools compress the bottom of the pyramid. The army of analysts who manually triage alerts and chase false positives is precisely who an AI that "prioritises and validates vulnerabilities" is built to replace. For H-1B and L-1 holders whose visa status is tied to a specific role, a restructuring that thins entry-level security operations is not an abstract worry.

The throughline for NRIs watching from New Jersey or the Bay Area is that the most durable jobs in this cycle are not at the model labs everyone reads about. They are in the unglamorous layer IBM just doubled down on — making someone else's AI safe enough for a regulated enterprise to actually run. Krishna has bet the company that this layer outlasts the hype. The engineers who staff it are betting their careers on the same thing."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Every Tech CEO Is Pouring Billions Into AI Data Centres. The Founder of India's Biggest SaaS Firm Says He'll Sit It Out.",
        "subheadline": "Sridhar Vembu calls the AI buildout a bubble, ships a made-in-India ERP, and rules out an IPO again. His pitch to NRIs is unusually direct: come home.",
        "slug": make_slug("zoho-sridhar-vembu-ai-bubble-warning-made-in-india-erp-sovereignty-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Zoho's bootstrapped, no-IPO, build-it-in-India playbook is a direct counter-pitch to the venture-and-equity model most NRI tech workers know, and Vembu is explicitly inviting Indian engineers abroad to return and build.",
        "tags": ["zoho", "sridhar-vembu", "saas", "india-tech", "ai-bubble", "atmanirbhar", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/zohos-sridhar-vembu-warns-against-chasing-ai-investment-bubble"},
            {"name": "PTI News (via YouTube)", "url": "https://www.youtube.com/watch?v=ptizohoerp"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/start-up/technology-can-be-weaponised-sridhar-vembu-advocates-indian-control-over-digital-infrastructure"},
            {"name": "Forrester", "url": "https://www.forrester.com/blogs/zohoday-2026-one-stack-more-stakes/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Zoho_headquarters_in_chennai.jpg/1280px-Zoho_headquarters_in_chennai.jpg",
        "image_caption": "Zoho Corporation's headquarters in Chennai, India",
        "image_attribution": "Wikimedia Commons",
        "body": """There is a familiar rhythm to tech leadership in 2026: announce a frontier model, commit billions to data centres, and warn that anyone who hesitates will be left behind. Sridhar Vembu, the founder of Zoho, has decided to do the opposite of all three.

This week Vembu said the enormous AI infrastructure buildout sweeping the industry could be a bubble, aligning himself with IBM's Arvind Krishna, who has voiced similar doubts. Zoho, he said, will focus on developing core AI capability rather than chasing the spend. "To some people that would sound defeatist," he said, "but we will talk in five years."

Coming from almost anyone else, that would read as an excuse for falling behind. Coming from Vembu, it is consistent with a 30-year track record of refusing to do what everyone else does.

## The anti-Silicon-Valley playbook

Zoho is one of the most successful software companies most American consumers have never heard of: more than 100 million users, 60-plus business apps, profitable, and resolutely private. Vembu has built it from a campus in rural Tamil Nadu, trained engineers who never went to elite colleges, and repeatedly ruled out the thing every other founder chases — an IPO.

He ruled it out again this month, while launching a **made-in-India ERP** (enterprise resource planning) system aimed first at Indian businesses before a phased global rollout. Announced from Kumbakonam, not Bengaluru or San Francisco, the product is a direct shot at the entrenched incumbents — SAP, Oracle and Microsoft — that have dominated the software that runs a company's finance, inventory and operations.

"We prefer to remain private to reinvest heavily into research and development," Vembu said, framing the IPO refusal as the thing that lets Zoho avoid short-term market pressure. It is also, increasingly, a political stance.

## Sovereignty as strategy

Vembu has folded Zoho's business case into India's national one. "To be a sovereign nation means that you have control over the technology," he said, arguing that ERP — the operational backbone of any business — is too important to run on foreign software. Zoho's messaging app Arattai and Zoho Mail have been publicly endorsed by Union ministers including Amit Shah and Ashwini Vaishnaw, and Vembu has explicitly drawn parallels with China's strategy of backing national technology champions.

The timing is not accidental. The same week, the abrupt US export ban on Anthropic's most advanced AI models — which cut off foreign nationals worldwide overnight — turned "sovereign AI" from a slogan into a procurement reality. When access to critical software can be revoked by a letter from Washington, a homegrown, independently owned stack stops looking quaint and starts looking like risk management.

## The pitch to NRIs

For the Indian diaspora, the most pointed part of Vembu's message was not about software at all. "This is home… your motherland is waiting for you," he said, addressing Indian professionals abroad directly. "There's so much opportunity here."

It is a genuine counter-narrative to the one most NRI engineers have internalised — that the best work, the best pay and the best equity are in the US. Vembu's bet is that India's expanding base of Global Capability Centres and its growing software depth mean the return trip is no longer a step down. Zoho's rural campuses are the proof of concept he keeps pointing to.

There are reasons for caution. Bootstrapping limits how fast Zoho can move in a field where rivals are spending tens of billions, and an ERP launch is the easy part — winning customers away from SAP and Oracle, with their deep implementation ecosystems, is a years-long grind. Vembu's AI-bubble call could also simply be wrong; "we'll talk in five years" is a bet, not a result.

But for an NRI weighing whether the next decade of opportunity is in Sunnyvale or back home, Vembu has done something useful. He has built a large, profitable, globally competitive software company entirely on the premise that you do not need Silicon Valley's money, its exit model, or its consensus to win. Whether that premise survives the AI era is the question he is daring everyone to wait five years to answer."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Washington Cut Off Anthropic's Best AI Models to Foreign Nationals Overnight. Indian Engineers Just Learned Who Owns the Switch.",
        "subheadline": "A single export-control letter pulled Fable 5 and Mythos 5 from everyone, including Anthropic's own foreign-born staff. For India's AI workforce, the lesson is about dependence.",
        "slug": make_slug("anthropic-fable-mythos-export-ban-foreign-nationals-sovereign-ai-india-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "The export ban barred foreign nationals — a category that includes a large share of Indian engineers at US AI labs and the millions of Indian developers who build on frontier models — exposing how quickly access to critical AI can vanish.",
        "tags": ["anthropic", "ai", "export-controls", "sovereign-ai", "indian-engineers", "h1b", "regulation"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/us-curbs-ai-spur-european-firms-spread-risk-2026-06-22/"},
            {"name": "CNN", "url": "https://www.cnn.com/2026/06/21/tech/anthropic-ai-regulation-export-control"},
            {"name": "The Register", "url": "https://www.theregister.com/2026/06/22/anthropic_mythos_export_control/"},
            {"name": "Memeburn", "url": "https://memeburn.com/2026/06/anthropic-curbs-push-india-into-sovereign-ai-debate-in-2026/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Dario_Amodei_at_TechCrunch_Disrupt_2023_01_%28cropped%29.jpg",
        "image_caption": "Anthropic CEO Dario Amodei at TechCrunch Disrupt in 2023",
        "image_attribution": "Wikimedia Commons",
        "body": """It took about ninety minutes. Last Friday, the Trump administration sent Anthropic CEO Dario Amodei a letter, citing national-security concerns, declaring that the company's two most advanced AI models — Fable 5 and the cybersecurity-focused Mythos 5 — could not be used by **any foreign national**, inside or outside the United States. The restriction was so broad it covered Anthropic's own foreign-born employees.

Facing the impossibility of cleanly walling off who could and couldn't use the models, Anthropic did the only thing it could: it pulled both offline for everyone, worldwide. The most powerful public AI model on the market, days after release, simply vanished.

For India's enormous AI workforce — at the US labs, on H-1B visas in the Bay Area, and among the millions of developers in Bengaluru and Hyderabad who build on frontier models — the episode is less a news story than a warning shot.

## What actually happened

Commerce Secretary Howard Lutnick's letter invoked the Bureau of Industry and Security's authority to require a licence for exporting "any item subject to export administration regulations" where there is risk of diversion to a "military intelligence end use." In other words, the government chose to treat a frontier AI model like a dual-use weapon.

The trigger, according to multiple reports, was a reported jailbreak in Fable 5 combined with alarm over Mythos 5 — a model so adept at finding software vulnerabilities that a US senator claimed it had breached "almost all" classified systems in an authorised internal test within hours. Anthropic disputes that the flaw warranted so extreme a response, but it complied while talks continue.

## The "foreign national" problem hits home

The phrase "foreign national" is where this lands for the diaspora. At America's frontier AI labs, a substantial share of the technical staff are Indian-origin researchers and engineers, many on visas. An export-control regime that bars foreign nationals from touching a model — even employees of the company that built it — creates an impossible workplace, and it puts a cloud over the immigration-dependent talent pipeline that has powered US AI.

It also reaches far beyond the labs. As one analysis put it, modern AI models are no longer chatbots; they are work systems that write code, audit security and automate operations. When a model disappears, a company does not lose a product — it loses a workflow. Indian IT services firms and startups that had begun building on Anthropic's models discovered overnight that the foundation could be pulled out from under them by a government they don't answer to.

## India's sovereign-AI moment

The ban has supercharged a debate already underway in India. Just days earlier, Bengaluru's **Sarvam** became the country's second AI unicorn, raising $234 million for an explicitly *sovereign* AI platform — models trained in India, for Indian languages, that enterprises and governments can own and operate themselves. At the time, "sovereign AI" sounded like a marketing flourish. After the Anthropic shutdown, it sounds like insurance.

Europe is having the same realisation. Reuters reported that executives at Siemens, Renault and Orange are now deliberately spreading risk across US, Chinese and European models to avoid dependence on any single provider, and the UK and EU are lobbying Washington for exemptions — so far without success. The lesson everyone is drawing is identical: a remotely delivered proprietary model can be switched off, and a model you can run on your own servers cannot.

## What it means for NRIs

For an Indian engineer in the US, the immediate worry is professional whiplash — building on a frontier model that may be export-controlled out of your hands, in a regulatory environment that even CNN described as a "mess" with no transparent, consistent framework.

For NRI investors and founders, the longer arc is more interesting. The US just handed the sovereign-AI category its most effective demand signal yet, entirely by accident. Capital is already flowing toward India's open-weight and homegrown model efforts, toward the data-centre buildout, and toward firms like Sarvam and the IT majors positioning to run AI that no foreign government can revoke.

The uncomfortable question India's tech leaders are now asking out loud is the one the Anthropic letter forced into the open: if AI becomes core infrastructure, who really controls the switch? For a generation of Indian engineers who assumed the answer didn't matter, it suddenly does."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
