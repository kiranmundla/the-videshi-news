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
        "headline": "An Indian Air Force Pilot Just Became the First ISRO Astronaut on the Space Station. The Next Stop Is India's Own.",
        "subheadline": "Shubhanshu Shukla's two weeks aboard the ISS are a dress rehearsal for Gaganyaan — and a recruiting poster for a space program the diaspora keeps funding from abroad.",
        "slug": make_slug("shubhanshu-shukla-axiom-4-iss-isro-first-gaganyaan-nri-space"),
        "category": "technology",
        "vertical": "space-tech",
        "diaspora_angle": "For an Indian family in New Jersey or the Bay Area, Shukla is the first of their own to fly to the space station — and the human face of a Gaganyaan program that diaspora engineers and donors have quietly been bankrolling.",
        "tags": ["space", "isro", "indian-tech", "gaganyaan", "axiom"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian EYE", "url": "https://theindianeye.com/international-space-station-welcomes-first-indian/"},
            {"name": "NASA / Axiom Space", "url": "https://www.axiomspace.com/missions/ax-4"},
            {"name": "ISRO", "url": "https://www.isro.gov.in/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/3a/Wing_Commander_Shubhanshu_Shukla.jpg",
        "image_caption": "Group Captain Shubhanshu Shukla, the first ISRO astronaut to reach the International Space Station, in his Indian Air Force uniform.",
        "image_attribution": "Wikimedia Commons",
        "body": """Group Captain Shubhanshu Shukla floated into the International Space Station this week as the pilot of Axiom Mission 4, and in doing so became the first astronaut of the Indian Space Research Organisation ever to reach the orbiting laboratory. The SpaceX Dragon capsule, nicknamed *Grace*, docked autonomously at the Harmony module at 4:05 pm IST on Thursday, ahead of schedule, with NASA flight engineers Anne McClain and Nichole Ayers watching the approach.

"As I sat in the capsule on the launchpad yesterday after 30 days of quarantine, all I could think was: just go," Shukla said in a live interaction from orbit. "When the launch finally happened, it was something else entirely. You're pushed back into the seat — and then suddenly, there's silence. You're just floating in the vacuum, and it's magical."

It is the kind of sentence that gets clipped and shared in a hundred family WhatsApp groups. But behind the goosebumps is a deliberate piece of national strategy.

## A rehearsal, not a victory lap

Shukla flew alongside veteran commander Peggy Whitson and two more first-timers — Sławosz Uznański-Wiśniewski of Poland and Tibor Kapu of Hungary — on a roughly two-week mission of science experiments, outreach and commercial work. For the other three countries this is a debut. For India it is reconnaissance.

ISRO is racing toward Gaganyaan, its first crewed orbital flight, and the agency has been explicit that Shukla's stint is a way to bank real human-spaceflight experience while its own hardware is still being tested. The agency's chair has pointed to a Gaganyaan launch following tests slated through early 2027, with uncrewed flights carrying the humanoid robot Vyommitra — Sanskrit for "space friend" — as the rehearsals before any Indian rides an Indian rocket from Indian soil.

That sequencing matters. India is trying to do what only the United States, Russia and China have done: put its own people in orbit on its own vehicle. Renting a seat on a SpaceX Dragon through Axiom is the fastest way to learn what the checklists, the medical protocols and the muscle memory actually feel like before betting a life on an LVM3.

## The diaspora angle nobody puts on the press release

Here is why a software engineer in Sunnyvale or a physician in Edison should care beyond pride. India's space ambitions have become one of the cleanest stories the diaspora tells about itself — proof that the country that exports H-1B talent can also build hard things. That narrative has dollars attached. Indian-American donors fund STEM scholarships pegged to ISRO; NRI-backed venture funds have written cheques into the private launch startups — Skyroot, Agnikul, Pixxel, Dhruva Space — now being handed access to ISRO's own rocket technology. Shukla is the recruiting poster for all of it.

There is also a talent-flow question that cuts the other way. For two decades the default path for a brilliant Indian aerospace graduate ran through a US university and stayed there. A visible, government-backed human spaceflight program — with a face like Shukla's on it — is exactly the kind of thing that makes a 22-year-old in Hyderabad reconsider whether the interesting work is only abroad. For the diaspora, that is a complicated, welcome mirror.

## What's next

Shukla and the Ax-4 crew will spend their two weeks running experiments, several of them designed by Indian institutions, before the Dragon undocks for the return splashdown. The data and the operational lessons feed straight back into Gaganyaan planning.

The bigger calendar item is closer to home. ISRO is also preparing the return-to-flight of its workhorse PSLV rocket by late June or early July, after two consecutive third-stage failures dented confidence in a vehicle with a 90%-plus success record. The agency has swapped vendors for the components blamed for the failures. A clean PSLV launch, followed by Gaganyaan's uncrewed rehearsals, would turn this week's borrowed seat into the opening act of something India owns outright.

For now, an Indian Air Force test pilot is circling the planet every 90 minutes, and a generation of diaspora kids just watched someone who looks like them call the vacuum of space "magical." That is worth more than any single experiment he runs up there."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "IndiaMART Connects 600 Buyers a Minute. Now It's Doubling Its AI Spend Every Six Months to Stop the Fakes.",
        "subheadline": "India's biggest B2B marketplace is pouring money into AI to police counterfeit listings and replace call-centre work — a quiet test of whether Indian platforms can clean themselves up before regulators do it for them.",
        "slug": make_slug("indiamart-ai-spend-fake-listings-counterfeit-b2b-marketplace-nri"),
        "category": "technology",
        "vertical": "india-tech",
        "diaspora_angle": "NRIs who source products from India for US storefronts — or who hold IndiaMART in their India portfolios — have a direct stake in whether the platform can scrub counterfeit and proxy sellers off a US 'Notorious Markets' watchlist.",
        "tags": ["ai", "indian-tech", "ecommerce", "marketplace", "fintech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indiamart-doubles-down-ai-curb-fake-listings-improve-buyer-interaction-2026-06-25/"},
            {"name": "Office of the US Trade Representative", "url": "https://ustr.gov/issue-areas/intellectual-property/Special-301/notorious-markets-list"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6170188/pexels-photo-6170188.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A worker sorting parcels in a logistics office, illustrating the B2B trade IndiaMART intermediates between buyers and sellers.",
        "image_attribution": "Pexels",
        "body": """IndiaMART, one of the largest online B2B marketplaces in the world, plans to double its spending on artificial intelligence every six months — a steep ramp for a company that has, until now, been conspicuously cautious about AI. The reason is unglamorous but existential: the platform has a fakes problem, and it would rather solve it with software than have a regulator solve it with a blacklist.

The numbers behind IndiaMART are genuinely large. Chief Product Officer Amarinder S. Dhaliwal told Reuters the platform matches roughly 600 buyers with suppliers every minute, draws about 90 million visitors a month, and hosts around 220,000 sellers with a buyer conversion rate near 45%. The company connects buyers and sellers across everything from phone chargers and lawn mowers to pharmaceutical products and — memorably — anatomical skeleton models. It does not, crucially, oversee the transactions themselves. That hands-off model is exactly what makes policing the listings so hard.

## The Notorious Markets shadow

IndiaMART has lived with counterfeit concerns for years. In 2022 it landed on the US Trade Representative's "Notorious Markets" list, which flagged counterfeit goods on the platform as a "serious concern." For a company whose entire value proposition is *trust between strangers doing trade*, that designation is corrosive — and for the diaspora entrepreneurs who use IndiaMART to source goods from India for storefronts in New Jersey, Houston or London, it is a real liability.

The AI push is aimed squarely at two failure modes Dhaliwal calls "supplier contamination" — bad-intent sellers slipping onto the platform — and outright "malicious listings" such as drugs or firearms. IndiaMART is using AI to detect proxy accounts by pattern-matching across seller profiles, the kind of network analysis that catches a single bad actor running fifty fake storefronts. It is also rolling out real-time voice-to-text tools to process buyer requests, a task that used to belong to call-centre employees.

That last detail is the one diaspora tech workers should sit with.

## Where the call-centre jobs go

For a generation of Indians, the business-process-outsourcing call centre was a first rung — the job that paid for an engineering degree, a sibling's wedding, sometimes a cousin's eventual move abroad. IndiaMART quietly automating buyer-request handling with voice-to-text is a small, concrete instance of the larger story India's IT sector is now living through: AI eating the labour-intensive middle. It is the same anxiety driving headlines about Accenture, TCS and Infosys, just at the scale of one marketplace's support desk.

IndiaMART, for its part, is doing this on a relatively modest budget. The company's technology and content expenses in fiscal 2026 were around 2.26 billion rupees — about $24 million — and it declined to disclose a specific AI budget. It said it is building some tools in-house while working with unnamed external AI firms. Doubling a small number every six months still compounds fast.

## Why the diaspora should track this

There are two stakes here for NRIs. The first is portfolio-shaped: IndiaMART is a listed company (INMR on the NSE), and a credible cleanup of its listings is the difference between a marketplace that scales toward its stated goal of a million sellers and one that stays capped by trust problems. The second is structural. India's consumer-internet platforms — IndiaMART, the quick-commerce players, the payments apps — are increasingly being judged on whether they can self-police fraud at the speed they grew. Do it well, and Indian platforms earn the global credibility to expand into diaspora markets. Do it badly, and they invite the kind of regulatory friction that has dogged them on counterfeit and content for years.

AI cleaning up an Indian marketplace is not a flashy story. But it is a useful tell. It shows whether the country's biggest digital platforms can grow up — turning the same technology that threatens their call-centre jobs into the thing that finally makes them trustworthy at scale."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Wants Its AI to Run on Indian Soil. A Navi Mumbai Company Is Stacking 80,000 GPUs to Make That Real.",
        "subheadline": "Yotta's bet on 'sovereign' data centres — Blackwell chips, Indian data residency, no dependence on US hyperscalers — is the picks-and-shovels play behind India's AI ambitions. The diaspora's startups are the customers.",
        "slug": make_slug("yotta-sovereign-ai-data-center-india-gpu-blackwell-nvidia-nri"),
        "category": "technology",
        "vertical": "ai-infrastructure",
        "diaspora_angle": "Indian AI startups founded by returnees and NRIs need compute that keeps data inside India for regulatory and cost reasons — Yotta's GPU farms are the rails those companies, and diaspora investors backing them, are betting on.",
        "tags": ["ai", "indian-tech", "data-center", "nvidia", "sovereign-ai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "PR Newswire", "url": "https://www.prnewswire.com/news-releases/yotta-data-services-receives-frost--sullivans-2026-indian-company-of-the-year-recognition.html"},
            {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17489151/pexels-photo-17489151.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Tower servers in a data center, the kind of GPU-dense infrastructure Yotta is scaling for India's sovereign AI push.",
        "image_attribution": "Pexels",
        "body": """The most-discussed companies in artificial intelligence write models. The companies that decide whether India gets to keep its AI ambitions on home soil build buildings full of chips. Yotta Data Services, a Navi Mumbai operator just named Frost & Sullivan's 2026 Indian Company of the Year for sovereign AI infrastructure, is firmly in the second camp — and its expansion plan reads like a wager on the whole "Make AI in India" thesis.

The hardware roadmap is the headline. Yotta currently runs 1,024 NVIDIA L40S and 8,192 H100 GPUs live at its NM1 facility in Navi Mumbai. It plans to scale past 80,000 next-generation GPUs by fiscal 2027–28, including Blackwell B200 and B300 parts. Specifically, the company says it will deploy 30,000 NVIDIA Blackwell B300 Ultra GPUs at a 60 MW data centre in Greater Noida — scalable to 250 MW — and 36,000 GB300/Vera Rubin GPUs at a 75 MW Navi Mumbai campus that it says can scale to a staggering 2 GW.

Those are numbers that, until very recently, only American hyperscalers threw around.

## What "sovereign" actually buys

The word doing the heavy lifting here is *sovereign*. Yotta's pitch, under co-founder and CEO Sunil Gupta, is that Indian government bodies and enterprises can run AI workloads on infrastructure that keeps data physically inside India, under Indian governance, with predictable local pricing — instead of renting from AWS, Azure or Google Cloud and accepting both the foreign jurisdiction and the dollar-denominated bill. Its platforms, branded Shakti Cloud (GPU infrastructure) and Shakti Studio (an "AI token factory"), sit on NVIDIA-certified stacks with InfiniBand networking.

This is the unglamorous foundation under every flashier India-AI story of the past month. The "sovereign AI" startups — Sarvam, Krutrim, the BharatGPT efforts — all need somewhere to train and serve models that satisfies the same data-residency and cost logic. A Wall Street bank recently warned that India's AI is a "fighter jet it doesn't own," because so much of the country's AI runs on foreign models and foreign clouds. Companies like Yotta are the attempt to at least own the runway.

## The diaspora's stake

For NRIs, this is a picks-and-shovels investment thesis hiding in plain sight. The diaspora has poured capital into Indian AI application startups — the model companies, the agentic-AI accelerators, the vertical SaaS plays. But applications are only as cheap and compliant as the compute beneath them. If that compute has to be rented abroad, margins compress and data-residency rules get awkward for any company touching Indian government or financial data. Domestic GPU capacity changes that math.

There is also a returnee angle. A meaningful slice of the engineers who can architect and operate hyperscale GPU clusters learned the craft at Google, Meta, Microsoft and NVIDIA in the US. Building 2 GW of AI-ready capacity in India creates exactly the kind of frontier-scale operational role that has, for two decades, existed mostly in Silicon Valley. It is one more reason for a senior infrastructure engineer in Seattle to take a call from Mumbai.

## The caveats

Sovereignty is expensive and unproven at this scale. Power is the binding constraint — a 2 GW campus needs generation, substations and cooling that India's grid will be stress-tested to provide, which is why Yotta talks up its own substations, renewable integration and closed-loop cooling. Blackwell-class GPUs are supply-constrained globally, and a Frost & Sullivan award is a marketing milestone, not an earnings report. The roadmap to 80,000 GPUs is a plan, not a fact.

But the direction is the point. India has decided it does not want to be a tenant in the AI era. Whether Yotta and its peers can actually pour that much concrete and power that many chips is now one of the more important questions for the diaspora's investment in the country's tech future — far more consequential, in the long run, than which chatbot tops this week's benchmark."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
