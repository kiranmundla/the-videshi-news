#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
    env_file = Path.home() / "workspace" / ".env.supabase"
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
        "headline": "Vishal Sikka Ran Infosys. Now He's Built an AI Startup Aimed at Killing the Business He Came From.",
        "subheadline": "The former Infosys CEO's new venture, Hang Ten Systems, raised $32 million to let AI do the integration-and-maintenance grunt work that built India's $315 billion IT industry.",
        "slug": make_slug("vishal-sikka-hang-ten-systems-ai-it-services-infosys-nri-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Hundreds of thousands of Indian engineers — in Bengaluru delivery centers and on H-1B and L-1 visas at US client sites — earn a living doing exactly the integration and maintenance work Sikka now wants software to automate.",
        "tags": ["ai", "indian-tech", "it-services", "silicon-valley", "startups"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/24/former-infosys-chief-vishal-sikka-startup-hang-ten-systems/"},
            {"name": "Mint — AI, weak demand cloud FY27 outlook for Indian IT", "url": "https://www.livemint.com/companies/news/ai-weak-demand-cloud-fy27-outlook-for-indian-it.html"},
            {"name": "Reuters — Indian IT stocks tumble as Accenture flags weak outlook", "url": "https://www.reuters.com/markets/indian-it-stocks-tumble-accenture-flags-weak-outlook/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/VishalSikkaSapphireOrlando2010.jpg/1280px-VishalSikkaSapphireOrlando2010.jpg",
        "image_caption": "Vishal Sikka, former CEO of Infosys, speaking at an enterprise technology conference.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """The man who once ran Infosys now wants to automate away the work that made it. Vishal Sikka, who led India's second-largest IT services firm from 2014 to 2017, has launched a startup whose entire pitch is that artificial intelligence can do much of what an army of human engineers has done for three decades: customize, integrate, and maintain enterprise software.

His new venture, Hang Ten Systems, came out of stealth on June 24 with a $32 million seed round led by Mayfield, plus a strategic cheque from Aramco Ventures and a board that includes Yahoo co-founder Jerry Yang. Sikka, 59, says the Bay Area company helps enterprises "continuously build, modify, and operate software using AI-driven development and automation." Early customers reportedly include Siemens Gamesa and Fresenius. Mayfield's Navin Chaddha says the firm "just got started a month back" and already has paying clients.

## Why this is pointed at India

Strip away the surfing metaphors — Sikka wrote that Hang Ten is helping enterprises "hang ten on the biggest wave of our lifetimes" — and the target is unmistakable. The IT services model is built on labor arbitrage: large teams of engineers, many of them Indian, doing the unglamorous middle work of enterprise software. That is precisely the layer Sikka is betting AI can compress.

He is not alone in the bet, and that is the uncomfortable part for the diaspora. The companies he is effectively competing with — Infosys among them — are racing to strike the same partnerships with Anthropic and OpenAI that underpin tools like his. The difference is that Sikka is building a business that assumes the work shrinks, while the incumbents are trying to sell AI as a way to grow.

## The numbers behind the anxiety

The timing lands in the middle of the worst stretch Indian IT has seen in years. The Nifty IT index fell more than 5% in a single session this month after Accenture, the industry's bellwether, cut the top end of its annual revenue forecast. TCS, Infosys, and HCL Tech dropped between 5% and 8% that day. Analysts at Kotak now model AI-led "revenue deflation" of up to 3 to 3.5% a year for the next three years.

Collectively, TCS, Infosys, and Wipro have shed roughly ₹8.5 lakh crore in market value over five years — the only major sector in India to post a cumulative decline, even as homegrown AI firms like Sarvam climb the value charts. TCS has already cut about 12,000 mostly mid- and senior-level jobs and is experimenting with gig-based hiring. Attrition among senior staff, once the firm's quiet strength, has crept up.

## What it means for an Indian engineer abroad

For an NRI working a client-site contract in New Jersey or a delivery role in the Bay Area, the through-line is direct. The roles most exposed to a tool like Hang Ten's are exactly the ones that have historically been the on-ramp to a US tech career: software customization, integration, testing, and maintenance. Those jobs are what convert into H-1B sponsorships and, eventually, green cards.

The optimistic reading — and it is the one Infosys chairman Nandan Nilekani made at the company's recent AGM — is that AI expands the pie rather than shrinks the workforce. India's IT majors spent more than $5 billion on AI-focused acquisitions in the last fiscal year, and employees are logging far more training hours: TCS staff averaged 120 learning hours in FY26, up 25%. The bet there is that engineers move up the stack, from writing code to orchestrating the agents that write it.

The pessimistic reading is Sikka's. He spent 12 years building enterprise software at SAP and a stint on Oracle's board before Infosys; few people understand the machinery he is now trying to dismantle better than he does. That a former Infosys CEO is the one placing the bet against the model is the part the diaspora should sit with.

## What's next

Hang Ten is hiring across delivery, engineering, and sales and plans to expand globally. The real test is whether enterprises treat AI-native delivery as a replacement for outsourced teams or merely a faster version of them. For the millions of Indian professionals whose careers ride on the answer, Sikka's startup is less a curiosity than a forecast — from someone with a uniquely good view of the wave he says is coming."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Washington Just Cut Off Foreign Nationals From Anthropic's Best AI. India's 'Sovereign AI' Startups Got the Gift of the Year.",
        "subheadline": "A US export-control order barring all foreign nationals — even Anthropic's own employees — from its top models has made the case for homegrown AI overnight. Sarvam and a wave of Indian builders are the unexpected winners.",
        "slug": make_slug("anthropic-foreign-nationals-ban-sovereign-ai-india-sarvam-nri-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian engineers and founders building or relying on frontier AI just watched access to the best US model get revoked in 90 minutes — proof that for NRIs and India alike, depending on a single foreign lab is now a strategic risk, not a convenience.",
        "tags": ["ai", "sovereign-ai", "anthropic", "indian-tech", "geopolitics"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Anthropic's Mythos model found vulnerabilities in classified US systems", "url": "https://www.reuters.com/technology/anthropic-mythos-model-vulnerabilities-us-government-systems/"},
            {"name": "Fast Company — Anthropic's Mythos model shows weaknesses in US government systems", "url": "https://www.fastcompany.com/anthropic-mythos-fable-foreign-nationals-restriction"},
            {"name": "The Register — Anthropic's Mythos mess just keeps getting more complicated", "url": "https://www.theregister.com/2026/06/24/anthropic_mythos_fable_export_control/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37730211/pexels-photo-37730211.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Server racks in a secure data center, the infrastructure layer at the heart of the sovereign-AI debate.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """The letter gave Anthropic about ninety minutes to decide. Last week the Trump administration, citing the Bureau of Industry and Security's export-control authority, told the company that its two most advanced models — Fable 5 and a more powerful sibling called Mythos 5 — could not be used by any foreign national, anywhere, inside or outside the United States. The restriction was so broad it swept in Anthropic's own foreign-national employees. With no clean way to wall those users off, Anthropic disabled both models for every customer.

The trigger was alarming on its own terms. In a restricted testing program, Mythos reportedly found vulnerabilities in highly sensitive US government systems; Senator Mark Warner said the NSA chief told him the model "broke into almost all of our classified systems, not in weeks, but in hours." Washington responded by treating frontier AI like any other dual-use weapon technology.

## Why an NRI engineer should care

For the diaspora, the abstract debate about AI governance just became concrete. If you are an Indian citizen on an H-1B at a US firm, or a green-card holder, or a founder in Bengaluru wiring a product on top of a US model, you watched access to the best available system vanish overnight — not because of anything you did, but because of where your passport was issued. More than 100 cybersecurity leaders, including people from Adobe and Nvidia, signed a letter urging the administration to reverse course, warning it hands an advantage to adversaries. It has not been reversed.

The lesson landing across boardrooms is blunt. Cohere's CEO called renting frontier AI without control "digital serfdom." The question, he argued, is who holds the off switch. Last week, the answer for millions of non-American users was: not them.

## India's accidental windfall

Here is the twist. The single most effective advertisement for "sovereign AI" — the idea that a country should own its own models, compute, and data rather than rent them — was just delivered, for free, by the US government. And India has builders ready to catch it.

Sarvam AI, India's first homegrown large-language-model developer, became the country's first sovereign-AI unicorn this week on the back of a roughly $234 million raise, with HCLTech leading a $150 million strategic cheque. Around it sits a thickening ecosystem: Krutrim from Ola, BharatGPT efforts, and a deep-tech funding base that has already absorbed over a billion dollars this year. India's venture firms are writing larger cheques into AI infrastructure precisely on the thesis that government backing plus domestic demand can produce globally competitive models.

The Anthropic episode reframes all of it. A sovereign Indian model is no longer just a nationalist talking point or an import-substitution play; it is insurance against exactly the kind of 90-minute revocation Anthropic's customers just lived through. For Indian enterprises, banks, and government systems, "what happens if Washington pulls the plug?" is now a question with a real precedent attached.

## The catch

Sovereignty is expensive. Frontier training demands enormous capital, energy, and chips — the same chips caught in US-China export fights. Few nations can build the entire stack alone, which is why even sovereignty advocates push for alliances over autarky. India's models still trail the US and Chinese frontier on raw capability, and a homegrown unicorn is not the same as a homegrown GPT-class system.

There is also a sharper irony for the diaspora. The very Indian-origin researchers who help build frontier models at US labs are, under the new directive, foreign nationals — the people the order is designed to exclude. Some of the talent that could anchor India's sovereign push is currently sitting inside the American companies now restricted from sharing their best work with it.

## What's next

Watch whether the administration narrows or lifts the directive under industry pressure, and watch how fast Indian enterprises move procurement toward domestic options. The Five Eyes intelligence alliance warned this week that AI capable of overwhelming cyber defenses is "months, not years" away. In that climate, the country that controls its own models sleeps better. For India — and for the NRIs deciding where to build — last week made the cost of dependence impossible to ignore."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's IT Giants Just Lost ₹8.5 Lakh Crore in Five Years. The Companies Replacing Them on the Value Charts Are AI Startups.",
        "subheadline": "TCS, Infosys, and Wipro are the only major Indian sector to post a cumulative decline in value — while four pure-play AI firms, led by Sarvam, crashed onto the rankings. For NRI investors, the great rotation is here.",
        "slug": make_slug("indian-it-tcs-infosys-wipro-value-decline-ai-startups-nri-investors"),
        "category": "technology",
        "vertical": "economy",
        "diaspora_angle": "NRIs hold Indian IT through mutual funds, ADRs, and direct stakes as the safe, dividend-paying bet on India's tech story — but the value is rotating from the outsourcers their generation worked for to the AI startups disrupting them.",
        "tags": ["indian-tech", "it-services", "markets", "ai", "investing"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Business — TCS, Infosys, Wipro Shed Rs 8.5 Lakh Cr as AI Startups Enter Value Charts", "url": "https://www.outlookbusiness.com/deeptech/tcs-infosys-wipro-shed-value-ai-startups-sarvam-groww-hurun"},
            {"name": "AInvest — Contrarian Signal in Indian IT: PPFAS Increases Exposure Amid Selloff", "url": "https://www.ainvest.com/news/contrarian-signal-indian-it-ppfas-increases-exposure-selloff/"},
            {"name": "Reuters — Indian IT stocks tumble as bellwether Accenture flags weak outlook", "url": "https://www.reuters.com/markets/indian-it-stocks-tumble-accenture-flags-weak-outlook/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/16594725/pexels-photo-16594725.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A financial trading screen displaying market charts and data.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """For a generation of the Indian diaspora, the IT majors were the safe bet — the dividend-paying, dollar-earning proof that India had arrived in global technology. Many NRIs hold TCS, Infosys, and Wipro through mutual funds, US-listed ADRs, or direct stakes, treating them as the conservative core of an India portfolio. That core is quietly being hollowed out.

According to the latest Hurun India 500 analysis, TCS, Infosys, and Wipro have together shed roughly ₹8.5 lakh crore in value over five years — making IT the only major Indian sector to record a cumulative decline. In the same window, four pure-play AI companies, including Sarvam AI, India's first homegrown LLM developer, debuted on the rankings. The symbolism is hard to miss: value is rotating out of the firms that built India's tech reputation and into the ones threatening to disrupt them.

## The fear, in numbers

The proximate cause of the latest leg down is Accenture. When the industry's bellwether trimmed the top of its annual revenue guidance this month, India's Nifty IT index fell 5.6% in a session, with TCS, Infosys, and HCL Tech dropping 5 to 8%. TCS and Wipro have touched 52-week lows. Brokerages have grown bearish: Kotak models AI-led "revenue deflation" of up to 3.5% a year over three years, and Morgan Stanley sees little near-term relief.

The structural worry is straightforward. India's $315 billion IT industry was built on bodies — large teams billing for software customization, integration, testing, and maintenance. If large language models compress that work, the headcount-export model looks exposed. TCS has already cut about 12,000 jobs and is testing gig-based hiring; senior attrition is rising.

## The contrarian case

Not everyone is selling. In a notable move, India's largest fund house, SBI Mutual Fund, and value shop PPFAS have been increasing IT exposure into the selloff — a contrarian signal worth weighing. Their argument: the doomsday scenario is overpriced. Revenue for the top six Indian IT firms is still expected to grow roughly 10.9% year-over-year, hardly terminal decline. The Big Five spent more than $5 billion on AI-focused acquisitions in the last fiscal year, buying the capabilities they lack rather than standing still. Employees are retraining fast — TCS staff logged 120 learning hours in FY26, up 25%; Infosys jumped 58%.

The bull case treats AI as forcing evolution, not extinction: the moat shifts from cheap labor to client relationships, domain depth, and the ability to orchestrate AI agents at enterprise scale. Nandan Nilekani told the Infosys AGM that AI will expand the services market, not shrink the workforce — the opposite of what most of his peers imply.

## What it means for an NRI portfolio

For a diaspora investor, this is less a sell signal than a rebalancing prompt. Three things are worth sitting with.

First, concentration risk. If your "India tech" exposure is really just three legacy outsourcers, you are betting heavily on one contested thesis. The value migrating to AI startups is, for now, largely locked in private markets — but vehicles like Info Edge (which has deployed ₹1,003 crore across 54 AI and deep-tech startups) offer listed proxies, and a wave of IPOs is coming.

Second, the dividend trade still works — until it doesn't. IT majors remain cash-generative and shareholder-friendly. The question is whether you are being paid enough to hold through a multi-year margin reset.

Third, valuation has done some of the work. With the sector near 52-week lows and growth still in double digits, the risk/reward looks less lopsided than the headlines suggest — which is exactly why India's biggest domestic funds are leaning in.

## What's next

The June-quarter results, due over the coming weeks, will show whether AI is genuinely eating margins or merely scaring the market. Watch deal bookings, not just revenue. For NRIs who have ridden Indian IT for two decades, the trade hasn't broken — but the easy years are over, and the value charts are already pointing to who comes next."""
    }
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\n{len(inserted)} of {len(articles)} inserted")
