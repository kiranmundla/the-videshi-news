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
        "headline": "HCLTech Just Bet $151 Million on Sarvam AI. India's IT Giants Are Done Renting Their Intelligence.",
        "subheadline": "The Noida outsourcing giant is leading Sarvam's Series B and taking a 10.5% stake, a sign that India's IT services model is pivoting from selling labor to owning models.",
        "slug": make_slug("hcltech-sarvam-ai-151-million-stake-sovereign-ai"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For the hundreds of thousands of Indian engineers at HCLTech, Infosys, and Wipro client sites across the US, the shift from staffing seats to owning AI models redraws what an IT-services career will look like over the next decade.",
        "tags": ["ai", "indian-tech", "hcltech", "sarvam-ai", "it-services", "sovereign-ai"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-hcltech-buy-105-stake-sarvam-ai-valuing-startup-15-billion-2026-06-15/"},
            {"name": "Mint", "url": "https://www.livemint.com/companies/news/indian-ai-startups-confront-new-risks-after-anthropic-pulls-fable-5.html"},
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/how-it-works/mohandas-pai-urges-india-ai-mission.htm"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17489163/pexels-photo-17489163.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Server racks in a data center, the kind of infrastructure that trains and runs large AI models.",
        "image_attribution": "Pexels",
        "body": """India's outsourcing industry was built on a simple arbitrage: rent out smart engineers in Bengaluru and Pune to global clients at a fraction of Western salaries. On Monday, HCLTech signaled how thoroughly that bargain is being rewritten. The Noida-based firm said it would pay 14.27 billion rupees (about $151 million) in cash for a 10.5% stake in Sarvam AI, leading the Bengaluru startup's Series B round as a strategic investor.

Sarvam was valued at $1.5 billion in the round, which pulled in $234 million in its first close out of a $300 million target. Bessemer Venture Partners co-led, with existing backers Khosla Ventures and Peak XV Partners staying in. For HCLTech, the money buys more than a logo on a cap table. The company said the deal will fund Sarvam's research into next-generation models for agentic AI, coding, and cybersecurity, and let HCLTech build its own language models and "sovereign AI" products for governments and regulated industries.

## From bodies to brains

The strategic logic is hard to miss. For two decades, the Indian IT services model meant placing armies of engineers at client sites, billing by the hour or the seat. Generative AI is quietly dismantling that. When a coding assistant can do the work of three junior developers, the seat-based pricing that funded the entire industry starts to leak. HCLTech's rivals have felt it: India's IT stocks are down 27% this year, and former Infosys CFO Mohandas Pai has been publicly warning that the country is "way behind" on AI and needs a 50,000-crore-rupee annual fund to catch up.

Buying into Sarvam is HCLTech's answer. Rather than wait for that government money, it is acquiring the ability to ship models, not just manpower. Owning a stake in a frontier-adjacent Indian lab lets HCLTech sell AI solutions built on technology it partly controls, instead of reselling someone else's API with a markup.

## Why sovereignty suddenly matters

The timing is not an accident. Indian AI firms got a cold reminder of their dependence last week when Anthropic restricted access to its Fable 5 and Mythos 5 models for users outside the United States. According to a report from Activate, Indiaspora, and Zinnov, 47% of Indian AI startups operate at the application layer, building on top of foreign models, while just 13% work at the infrastructure layer. A nation running its AI economy on borrowed foundations, as 3one4 Capital's Pranav Pai put it, "risks exposure."

Sarvam already has pedigree here. Microsoft partnered with it in 2024 to support voice-based generative AI, and the startup has positioned itself around models trained on how Indians actually speak, including the messy reality of mixing English with regional languages mid-sentence. That is exactly the kind of "full stack of frontier, small, and vertical models" that the sovereignty hawks have been demanding.

## What it means for the diaspora

For the Indian engineer on an H-1B at a US bank, working alongside an HCLTech delivery team, this is the clearest signal yet that the job is changing under their feet. The career ladder that ran from support analyst to project manager assumed a steady supply of billable seats. As IT services firms pivot to owning AI products, the premium will shift toward those who can build, fine-tune, and deploy models, not just staff them.

It also reshapes the perennial return-to-India calculation. For years, the diaspora's stay-or-go math leaned on the gap between Silicon Valley's frontier work and India's back-office grind. Deals like this narrow it. A Bengaluru lab valued at $1.5 billion, funded by Khosla and Bessemer and now an Indian IT major, is building the kind of agentic and coding models that NRIs flew to California to work on. For some, the pull factor is getting stronger.

For NRI investors, the read is more cautious. India's entire AI sector raised $860 million in 2025, against $129 billion in the US and $1.2 billion in China. The Sarvam round is a meaningful chunk of that, and a vote of confidence from a profitable, public IT major rather than a pure venture bet. But the funding chasm is real, and "sovereign AI" remains as much aspiration as achievement. The bet HCLTech just made is that closing the gap is now a survival requirement, not a patriotic luxury."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Adani and an Apple Supplier Are Building India's AI Data-Center Factory. The Hyperscalers Are the Customers.",
        "subheadline": "Jabil, which already builds parts for Apple, is teaming with Adani to manufacture AI and data-center hardware in India, part of a planned $50 billion buildout of the country's digital backbone.",
        "slug": make_slug("jabil-adani-ai-data-center-manufacturing-india"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "NRIs weighing Adani-linked stocks and India's data-center boom now have a concrete signal that the country wants to manufacture AI infrastructure, not just consume it, with implications for cross-border investment and the engineers who will run it.",
        "tags": ["ai", "data-centers", "adani", "jabil", "india-infrastructure", "hyperscalers"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/apple-supplier-jabil-adani-partner-build-ai-data-center-infra-platform-india-2026-06-15/"},
            {"name": "Reuters (SatSure / sovereign AI context)", "url": "https://www.reuters.com/technology/indias-satsure-bags-26-million-grant-build-ai-powered-earth-observation-models-2026-06-11/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4508751/pexels-photo-4508751.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Steel-framed cabinets housing servers and networking gear in a data center facility.",
        "image_attribution": "Pexels",
        "body": """India loves to talk about being the back office of the world's data. It has been less good at making the machines that store and crunch it. A partnership announced Monday tries to change that. Jabil, the Florida-based contract manufacturer that builds components for Apple, said it will team with Adani Enterprises to create an integrated platform for manufacturing AI and data-center infrastructure inside India.

The pitch is unambiguous: build the racks, servers, and supporting hardware locally, then sell them to the customers who need them most. The platform will serve global hyperscalers, co-location operators, and enterprise data centers, the companies said, taking aim at what they called "explosive" demand for AI-ready hardware both in India and abroad. Financial terms were not disclosed, and the two said they are still working out the operational framework and formal documentation.

## A $50 billion backbone

The deal sits inside a much larger number. Jabil and Adani said India's digital infrastructure is set to absorb more than $50 billion in planned spending across data centers, cloud, and AI ecosystems. Adani alone has committed to spending $100 billion on renewable-powered, AI-ready data centers by 2035, an ambition that until now leaned heavily on imported gear. Pulling manufacturing onshore is how that math starts to close.

For Jabil, the logic is the demand it is already seeing. The company raised its annual forecast in February on the strength of orders for AI data-center infrastructure, and its Apple relationship gives it a template for running high-volume, precision manufacturing in Asia. Pairing that with Adani's land, energy, and political heft in India is the kind of arrangement that has historically turned policy ambition into actual factories.

## The "Make in India" test case

India's government has spent years trying to move the country up the technology value chain, from assembling iPhones to fabricating chips. The semiconductor push, anchored by Tata's Dholera fab and Micron's Gujarat plant, gets the headlines. But data-center hardware, less glamorous and faster to stand up, may prove the more immediate win. You do not need a multi-billion-dollar fab and a decade of yield learning to build server racks and networking cabinets; you need scale, power, and reliable supply chains, all of which Adani can supply.

That matters because the AI buildout is happening now. Every model trained, every chatbot query answered, runs on physical infrastructure that someone has to build. If even a slice of that manufacturing happens in Gujarat or Maharashtra instead of Taiwan or Mexico, it is jobs, exports, and a foothold in a supply chain that the whole world is fighting over.

## Why the diaspora should watch

For NRI investors, the Adani name carries both promise and baggage. The group's infrastructure ambitions are vast, its execution record real, and its history of scrutiny well documented. A partnership with a US-listed, Apple-grade manufacturer like Jabil is a credibility marker, the kind of validation that diaspora investors tracking Adani Enterprises from New Jersey or London tend to weigh carefully. It signals that global supply-chain players are willing to put their names next to Adani's on AI infrastructure.

There is a strategic read too. The diaspora has spent the past decade watching India debate whether it can ever be more than a consumer of foreign technology. Sovereign AI advocates at home have been loud about the danger of running the country's digital economy on imported chips and borrowed models, a worry sharpened by recent US restrictions on Indian access to frontier AI systems. Manufacturing the data-center hardware locally is one concrete answer to that anxiety, even if the chips inside still come from abroad.

And for Indian engineers abroad, the buildout is a quiet recruiting pitch. Standing up a $50 billion infrastructure base requires the data-center architects, power engineers, and hardware specialists that India has long exported to the US. As the work moves home, so might some of the talent. The factory floor is not built yet, the documents are not signed, and grand Indian infrastructure announcements have a way of arriving early. But the direction of travel is clear: India wants to build the machines, not just feed them data."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "An Indian Startup Raised $30 Million to Answer the Calls You Don't Want. NRIs With Indian Numbers Know the Pain.",
        "subheadline": "Equal AI's call-screening app is built for the spam-call avalanche of Indian phone numbers, including the code-mixed Hinglish that trips up Western voice models.",
        "slug": make_slug("equal-ai-30-million-call-screening-india-code-mixing"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Any NRI who still keeps an Indian SIM for banking, family, or UPI knows the relentless spam-call problem; Equal AI is building voice models for exactly the multilingual, code-mixed reality the diaspora lives in.",
        "tags": ["ai", "indian-startups", "equal-ai", "voice-ai", "consumer-tech", "fintech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/13/equal-ai-raises-30m-to-screen-calls-so-indians-dont-have-to/"},
            {"name": "Inc42", "url": "https://inc42.com/buzz/from-gps-renewables-to-equal-ai-indian-startups-raised-243-mn-this-week/"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6862844/pexels-photo-6862844.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A person holding a smartphone showing an incoming call.",
        "image_attribution": "Pexels",
        "body": """If you have ever kept an Indian phone number alive from abroad, you know the daily ritual: the unknown number flashing at an inconvenient hour, the recorded voice pitching a personal loan or a credit card, the slim chance it is actually your bank's OTP line and you have to answer. Equal AI just raised $30 million to make that decision for you. The Bengaluru startup's app screens unknown calls with AI, and the round brings its total funding past $42 million.

The raise has an unusual structure. It is split into three tranches, with the company carrying a different valuation at each stage depending on whether it hits predetermined targets, an uncommon arrangement that lets a startup advertise its highest achieved valuation even if most of the equity sold at a lower one. Equal declined to disclose the specific numbers. Founder Keshav Reddy, who comes from the family behind the GVK conglomerate, started Equal in 2022 as a data-sharing company for financial services before pivoting toward consumers.

## Built for how Indians actually talk

The technically interesting part is the language problem. Western call-screening tools, from Google's Call Screen to Apple's recent efforts, assume callers speak one language cleanly. Indians do not. They slide between English and Hindi, Tamil, or Telugu inside a single sentence, a phenomenon linguists call code-mixing and the rest of us call Hinglish. A spam bot pitching insurance in fluent Hinglish sails right past models trained on California English.

Equal AI says it has built support for more than ten languages with exactly this in mind, stitching together speech recognition, automatic speech recognition, and speech generation under its own orchestration layer. The use case Reddy chose first was deliberate. "If you are buying car insurance, you might get 20 calls over a week, and that is hard to tackle for a human," he told TechCrunch. India's financial-services boom, with its aggressive telecallers, made call screening the obvious wedge.

## Where it is headed

Right now the app only screens unknown numbers, but the company plans to extend it to known contacts and, more ambitiously, to have the AI take action on a user's behalf, texting a delivery driver your address with consent, or placing outbound calls to book appointments. An iOS version and a paid subscription tier are in the works. The vision is less spam filter, more autonomous phone assistant, the kind of agentic feature that the entire AI industry is racing toward, tuned for Indian conditions.

Equal AI was one of the brighter spots in a modest week for Indian startups, which collectively raised about $243 million across sectors from quick commerce to spacetech. Against the backdrop of India's wider AI funding gap, consumer apps solving distinctly Indian problems remain one of the few categories where local startups have a structural advantage over global giants.

## The diaspora angle

This is a more intimate story for NRIs than the usual chip-and-cloud headlines, because almost everyone in the diaspora is still tethered to an Indian number. You keep it for the bank account you never closed, for UPI payments when you visit, for the family WhatsApp group, for the OTP that authorizes a transfer to your parents. And with that number comes the same flood of spam calls that plagues residents, except you are fielding them from a time zone twelve hours off, often in the middle of a US workday.

A screening tool that actually understands Hinglish, and that can eventually field the calls and text back on your behalf, is squarely aimed at that pain. For the NRI who handles aging parents' finances remotely, an AI that can triage a genuine bank call from a loan-pitch bot has obvious utility.

There is also a quieter signal here about where Indian consumer tech is going. The diaspora has watched Indian startups build globally relevant infrastructure, from UPI to the explosion of fintech apps. Equal AI is a reminder that the most defensible products may be the ones built for problems only India has at this scale, in languages only India speaks this way. That is a market the Silicon Valley giants cannot easily copy from Mountain View, and it is one the diaspora understands in its bones."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK {art['slug']}")
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")
