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
        "headline": "An Indian IT Giant Just Bought Into the AI That Could Replace It. The Logic Is Colder Than It Looks.",
        "subheadline": "HCLTech's $150 million bet on Sarvam AI is the first time an Indian services firm has taken a real stake in a homegrown model-maker. It is less a vote of confidence than a hedge.",
        "slug": make_slug("hcltech-sarvam-ai-stake-sovereign-ai-it-services-diaspora"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For the hundreds of thousands of Indians whose careers run through TCS, Infosys, Wipro and HCL — on H-1Bs in New Jersey or in Bengaluru delivery centers — this deal signals which skills the services industry will pay for next, and which it is quietly writing off.",
        "tags": ["ai", "indian-tech", "hcltech", "sarvam", "sovereign-ai", "it-services"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-hcltech-buy-105-stake-sarvam-ai-valuing-startup-15-billion/"},
            {"name": "Mint", "url": "https://www.livemint.com/companies/news/hcltech-sarvam-ai-stake-sovereign-ai.html"},
            {"name": "Inc42", "url": "https://inc42.com/buzz/hcltechs-sarvam-ai-bet-is-patient-capital-finally-here/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/C_Vijayakumar_%281%29.jpg/3840px-C_Vijayakumar_%281%29.jpg",
        "image_caption": "HCLTech chief executive C Vijayakumar, who is steering the company into sovereign AI.",
        "image_attribution": "Wikimedia Commons",
        "body": """India's largest software exporters have spent two years insisting that artificial intelligence is a tailwind, not a threat. On Monday, one of them put $150 million behind a quieter admission: the work that built the industry is shrinking, and the firms that sold it need somewhere else to stand.

HCLTech said it would acquire a 10.5% stake in Sarvam AI, the Bengaluru startup that builds large language models tuned for Indian languages, leading a Series B round that valued the two-year-old company at $1.5 billion. It is the largest single investment by an Indian IT services firm into a homegrown model-maker, and brokers were quick to label it a first of its kind. Nomura called it the opening move by an Indian services company into "sovereign AI." Morgan Stanley framed it as a strategic edge.

The framing is generous. Strip away the language of national capability, and the deal reads as a hedge by a company that knows its core business is under pressure.

**Why a services firm buys a model**

HCLTech, like its peers, sells human hours: armies of engineers who write, test and maintain code for global banks, insurers and retailers. That model lost billions in market value across the Indian IT sector in February, after Anthropic shipped an agent that could do swaths of that work without a person attached. This week, Accenture — the bellwether the whole sector watches — forecast quarterly sales below Wall Street's expectations, and India's Nifty IT index fell 5.6% in a day, dragging TCS, Infosys and HCLTech down with it.

Chief executive C Vijayakumar was blunter than the analysts. He told Mint the Sarvam stake "really creates one more very significant growth vector, which is sovereign AI" — selling specialized models to governments and regulated industries that cannot, for legal or political reasons, run their data through an American lab's servers. That is a real market, and a defensible one. It is also an admission that the old vector is no longer enough.

**The diaspora reads the tea leaves**

For the Indian engineer this matters in a specific, unsentimental way. The services giants are the largest single channel through which Indian technical talent reaches the United States — the H-1B and L-1 pipeline that fills delivery centers in New Jersey, Texas and the Bay Area. When the work those visas are tied to gets automated, the pipeline narrows from the bottom. India's tech hiring just hit a 28-month low. Entry-level "fresher" roles, the conveyor belt that historically fed the diaspora, are jamming.

What HCLTech's bet signals is where the surviving demand sits: not in writing more code faster, but in building, governing and deploying models for clients who need them locked down. Those are research and applied-AI roles, fewer in number and steeper in skill. An engineer betting on a US career through the services route should read the Sarvam deal as a map of which capabilities still command a visa sponsorship — and which are being quietly priced out.

**Patient capital, or a defensive crouch?**

Sarvam's founders, Vivek Raghavan and Pratyush Kumar, have argued that India has abundant AI talent but little experience building frontier models from scratch — and almost no patient capital willing to fund the long, expensive climb. The HCLTech cheque, mirrored against Microsoft's early backing of OpenAI, is being read as a sign that domestic money is finally waking up to those timelines.

Maybe. The scale is nowhere near the Microsoft comparison, and Sarvam's revenue, while up thirtyfold year over year, sat at just ₹45 crore in FY26. The more sober reading is that a profitable incumbent with a structurally threatened business used legacy profits to buy optionality in the thing that threatens it. That is a sensible move. It is not yet a national strategy.

For NRIs holding HCLTech or watching the broader Indian IT trade, the lesson is the same one the engineers are learning: the services era that built the diaspora is not ending tomorrow, but it is no longer the safe bet it was. The companies themselves are now telling you so, $150 million at a time.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Threads Just Hit 500 Million Users. The Quiet Engine Behind It Is India.",
        "subheadline": "Meta's three-year-old text app is now the size of X — and much of its organic, sticky growth is coming from the creators, fandoms and diaspora arguments that flourish in the Indian internet.",
        "slug": make_slug("threads-500-million-users-india-creators-meta-communities"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Threads has become the default room where Indian creators, cricket fandoms and NRI commentators argue in real time — so where Meta steers the app next directly shapes how the diaspora talks to itself, and how brands reach it.",
        "tags": ["meta", "threads", "social-media", "indian-creators", "diaspora"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/metas-threads-reaches-500-million-monthly-users-rolls-out-new-features/"},
            {"name": "Engadget", "url": "https://www.engadget.com/social-media/metas-threads-app-now-has-half-a-billion-monthly-users.html"},
            {"name": "Morningstar", "url": "https://www.morningstar.com/news/dow-jones/metas-threads-platform-hits-500-million-users"}
        ]),
        "score_total": 71,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/16852968/pexels-photo-16852968.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A smartphone displaying social media apps; Threads has crossed 500 million monthly users.",
        "image_attribution": "Pexels",
        "body": """Meta said this week that Threads has crossed 500 million monthly active users, putting the three-year-old app in the same weight class as X, Reddit and Pinterest. Mark Zuckerberg has floated a billion as the eventual ceiling. What he has not done is name the markets quietly doing the heavy lifting — and India is near the top of that list.

When Threads launched in July 2023, weeks after Elon Musk renamed Twitter, the skeptics had a reasonable case. The app borrowed its initial 100 million sign-ups wholesale from Instagram's follower graph. Retention, critics argued, would collapse once the novelty wore off. It did not. The app passed 175 million by mid-2024, 400 million by August 2025, and added roughly 100 million more in the ten months since. More tellingly, Meta says growth is now organic: more people open Threads directly rather than tapping through from Instagram or Facebook.

**The Indian internet is built for this**

Meta has been coy about country-level numbers, naming only South Korea and Japan, where time spent jumped 80% and 130% year over year. But the company's own explanation for the surge — that "communities" are driving engagement — describes the Indian internet almost exactly. Threads is where cricket arguments run for full match-days, where Bollywood fandoms organize, where regional-language creators have found a text-first home that Instagram's image grid never gave them, and where the NRI commentariat litigates Indian politics across time zones.

This week Meta leaned into precisely that behavior. It pulled its Communities feature out of beta, gave it a dedicated hub in the main menu, and added a "Community Progress" tool that nudges a hot topic toward becoming a standalone group. For a market where interest-based crowds form fast and loud, these are not cosmetic changes — they are the scaffolding for exactly the conversations that already keep Indian users on the app.

**The catch: control, and who gets it**

The other big launch, "Your Algo," lets users tell the feed to show more or less of a topic for one, three or seven days — useful for dodging cricket spoilers or a brutal news cycle. The feature is launching first in the United States, Canada, the UK, Australia and New Zealand. India, despite supplying much of the growth, is not on the list.

That gap is worth sitting with. It is a familiar pattern: a feature tested where regulators and advertisers are richest, rolled out to high-growth markets later. For Indian creators who have built audiences on Threads, the tools that shape distribution — and therefore reach, and therefore income — are arriving on someone else's schedule.

**Why the diaspora should care**

For the NRI in New Jersey or London, Threads has quietly become the room where the Indian conversation happens in real time, in a way the algorithm-throttled, video-first feeds of Instagram and TikTok do not allow. It is where a Bay Area founder, a Delhi journalist and a diaspora uncle can land in the same reply thread within minutes. As Meta formalizes communities, that room is about to get more organized — and more monetized.

Because the commercial logic is unfinished. Meta CFO Susan Li told investors in April that Threads would not be a "meaningful driver" of revenue in 2026, even after ads rolled out in 200 countries. Half a billion users with no clear business model is a position Meta has been in before, and it always ends the same way: the screws tighten. When Threads' ad machine finally turns toward its growth markets, India's creators and the brands chasing the diaspora will be among the first to feel it.

For now, the milestone is real and the trajectory is steep. The quieter story is that a platform increasingly powered by Indian and Asian users is still being steered, feature by feature, from somewhere else. That is the diaspora's relationship with Big Tech in miniature: indispensable to the growth, last in line for the controls.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Ghar Wapsi: India's Startups Are Sprinting Home Before They IPO. NRI Investors Should Read the Fine Print.",
        "subheadline": "Meesho, Zepto, Pine Labs and now Pocket FM are unwinding their offshore holding companies to list in Mumbai. The 'reverse flip' is reshaping who gets to own India's next public tech.",
        "slug": make_slug("india-startups-reverse-flip-ghar-wapsi-ipo-nri-investors"),
        "category": "technology",
        "vertical": "economy",
        "diaspora_angle": "When a startup moves its parent from Delaware or Singapore back to India ahead of an IPO, the listing happens on Indian exchanges — changing exactly how, and whether, an NRI in the US can buy in, and what tax bill comes with it.",
        "tags": ["indian-startups", "reverse-flip", "ipo", "nri-investors", "pocket-fm", "fintech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "BestMediaInfo", "url": "https://bestmediainfo.com/news/top-headlines-june-18-2026"},
            {"name": "Lexology", "url": "https://www.lexology.com/library/detail.aspx?g=reverse-flipping-india-startup-saga"},
            {"name": "Mondaq", "url": "https://www.mondaq.com/india/corporate-and-company-law/reverse-flipping-india-startups"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/13143008/pexels-photo-13143008.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Mumbai's skyline, home to the exchanges where India's returning startups are choosing to list.",
        "image_attribution": "Pexels",
        "body": """A decade ago, the smart move for an ambitious Indian startup was to flip: incorporate the parent company in Delaware or Singapore, where global venture capital felt at home, and run the operating business out of Bengaluru. This week, Pocket FM — the audio-series company eyeing both a fresh $150 million round and an eventual IPO — confirmed it is doing the opposite. It plans to move its holding structure back to India.

It is not alone, and that is the story. Meesho, Zepto, Pine Labs, PhonePe, Groww and Pepperfry have all executed or announced some version of the same maneuver, known in the trade as a "reverse flip" and, more affectionately, as ghar wapsi — a homecoming. The center of corporate gravity, having spent years offshore, is being dragged back onshore. For NRI investors who track Indian tech as a portfolio, the trend changes the basic question of how you get to own these companies at all.

**Why they are coming home**

The original logic for flipping abroad has eroded. Indian public markets are now deep enough, and richly enough valued, to reward a domestic listing — the National Stock Exchange itself just filed to go public at a reported $57 billion valuation. Maintaining an offshore parent, meanwhile, is expensive and cumbersome: annual renewals, foreign audits, multi-jurisdictional tax filings. When you no longer need foreign soil to raise money, those costs become dead weight.

Regulators have leaned in. The Ministry of Corporate Affairs amended India's merger rules to smooth the "inbound merger" route, by which a foreign holding company folds into its Indian subsidiary, and certain reorganizations now qualify for capital-gains tax neutrality under Sections 47(vi) and (vii) of the Income Tax Act. The government wants these listings — and the jobs, capital and prestige — to happen in Mumbai, not on the Nasdaq.

**The fine print that catches NRIs**

Here is where the diaspora investor needs to slow down. A reverse flip is not free, and the costs do not fall evenly.

For shareholders, the move can trigger tax. Where an inbound merger qualifies as tax-neutral, gains may be deferred; where it is structured as a share swap, it can create a real liability at the moment of the flip. Worse for some foreign backers, the clock on treaty benefits can reset. An investor who held shares in a Singapore entity acquired before the 2017 grandfathering cutoff — and who expected a tax-exempt exit — may lose that shield once the holding company becomes Indian, because the prior holding period is wiped.

Then there is access. A company that lists in Mumbai rather than New York is governed by Indian rules on foreign ownership. NRIs can invest, but through specific channels — the portfolio investment route, GIFT City vehicles, or funds with the right approvals — not simply by buying the ticker through a US brokerage the way they might an American IPO. The homecoming that thrills Indian retail investors can quietly fence out the diaspora cousin who assumed access was automatic.

**What to do with it**

The reverse-flip wave is, on balance, a confidence signal: India's founders now believe the home market can value them properly, and its regulators are paving the road back. That is genuinely good news for anyone bullish on Indian tech.

But "good for India" and "easy for NRIs" are not the same sentence. Before chasing a Meesho or Pocket FM listing, the diaspora investor should establish three things early: which exchange the company will actually list on, what route lets a US-resident NRI participate, and whether their own historical holdings carry a tax tail from the restructuring. The companies are coming home. Making sure your money can follow them through the door takes a little more paperwork than a homecoming should.
"""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        wc = len(art["body"].split())
        print(f"OK {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")
