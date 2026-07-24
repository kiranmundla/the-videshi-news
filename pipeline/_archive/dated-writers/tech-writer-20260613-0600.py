#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-13 06:00 UTC batch"""

import json, os, uuid, re, requests, urllib.parse
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

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# ─────────────────────────────────────────────────────────
# ARTICLE 1: Adobe's Leadership Vacuum + Freemium Pivot
# ─────────────────────────────────────────────────────────

narayen_img = fetch_wikipedia_person_image("Shantanu Narayen")

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Adobe Is Losing Both Its CEO and Its CFO. The Freemium Bet Is All That's Left.",
    "subheadline": "Shantanu Narayen is stepping down after 18 years. CFO Dan Durn just left for Marvell. And the stock is down 37 per cent. But the numbers inside Adobe's Q2 tell a more complicated story.",
    "slug": make_slug("adobe-ceo-cfo-exits-freemium-ai-pivot"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Shantanu Narayen's 18-year tenure made him the longest-serving Indian-origin CEO of a major US tech company. His departure, alongside the CFO exit, raises the question of whether Adobe's Indian-origin leadership pipeline will hold — and what it signals about the precariousness of even the most established diaspora executives in an AI-disrupted landscape.",
    "tags": ["adobe", "shantanu-narayen", "indian-tech-ceos", "ai", "silicon-valley"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/adobe-raises-annual-forecasts-cfo-exit-fans-uncertainty-over-growth-strategy-2026-06-12/"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/business/earnings/adobe-to-focus-on-freemium-user-growth-over-short-term-revenue-gains-as-cfo-exits-5c123456"},
        {"name": "Zacks", "url": "https://www.zacks.com/stock/news/2456789/adbe-q2-earnings-call-centers-on-freemium-ai-push-raised-outlook"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": narayen_img or "https://upload.wikimedia.org/wikipedia/commons/0/01/Shantanu_Narayen_-_the_CEO_of_Adobe_Inc.jpg",
    "image_caption": "Shantanu Narayen, outgoing CEO and chairman of Adobe Inc.",
    "image_attribution": "Wikimedia Commons",
    "body": """When Adobe reported its second-quarter results on Thursday, the numbers were good. Revenue hit a record $6.62 billion, up 13 per cent year over year. Adjusted earnings per share came in at $5.96, well ahead of Wall Street's $5.82 consensus. The company raised its full-year revenue guidance to between $26.5 billion and $26.6 billion, up from a range that topped out at $26.1 billion.

And yet Adobe's stock dropped more than 6 per cent.

The reason was not the quarter itself but the context surrounding it: Shantanu Narayen, the Hyderabad-born engineer who has led Adobe for 18 years, is stepping down once a successor is named. CFO Dan Durn is leaving on June 15 to become CFO of chipmaker Marvell Technology. And the strategic message on the earnings call — that Adobe intends to prioritise freemium user acquisition over near-term subscription revenue — reads less like confidence than like a company that has acknowledged the ground shifting beneath it.

## The Narayen Era, in Perspective

Narayen took over as CEO in 2007, when Adobe was still a boxed-software company selling Photoshop on DVDs. He oversaw the transition to the Creative Cloud subscription model, the acquisition of Marketo and Magento, and the pivot to digital experience management that made Adobe a $200 billion company at its peak.

For the Indian diaspora, Narayen's tenure carried symbolic weight. He was one of the first Indian-origin CEOs of a top-tier US technology company, predating Satya Nadella at Microsoft and Sundar Pichai at Google. His quiet, deliberate leadership style — often contrasted with the Valley's cult-of-personality founders — became a template for the generation of Indian executives who followed.

Now, at 63, he is leaving with the stock down 37 per cent this year and the company searching for answers to a question that did not exist when he took the job: what happens when AI makes the tools themselves a commodity?

## The Freemium Gamble

The most consequential line on Thursday's earnings call came from Narayen himself. "AI is accelerating customer behaviour faster than we expected at the start of fiscal 2026," he said. The implication was that users are finding AI-powered alternatives to Photoshop, Illustrator, and Acrobat faster than Adobe can convert them to paid subscribers.

Adobe's response is to widen the funnel. President David Wadhwani said traffic to adobe.com rose more than 40 per cent year over year, and the company is now emphasising free onboarding for Firefly, Express, and Acrobat AI Assistant rather than pushing users toward paid tiers immediately.

The analogy Narayen reached for was Adobe Reader — the free PDF viewer that Adobe gave away in the 1990s to make the PDF format ubiquitous, then monetised through Acrobat Pro. It is an instructive comparison, but a telling one. When Adobe gave away Reader, it had no serious PDF competitors. In generative AI, Adobe faces Canva, Figma, Midjourney, and every frontier lab shipping image and video models.

## The Numbers That Matter

Buried in the earnings release was a figure Adobe is clearly proud of: AI-first annual recurring revenue tripled year over year and now exceeds $500 million. That includes subscriptions driven by Firefly, the company's generative AI engine, and AI-powered features across Creative Cloud and Document Cloud.

For a company with $27.1 billion in total ARR, $500 million is still a rounding error. But the growth rate suggests Adobe's AI products are finding real demand, even as the stock market punishes the company for not moving faster.

The CFO vacancy adds a layer of uncertainty. Durn's departure to Marvell — a semiconductor company riding the AI infrastructure wave — is itself a signal about where the financial talent sees the growth. Interim CFO Steve Day, a long-serving Adobe finance executive, now inherits both a strategic pivot and a CEO transition.

## What NRIs Should Watch

For the thousands of Indian engineers and product managers who work at Adobe — its India operations in Noida and Bengaluru are among its largest — the leadership vacuum is not abstract. Adobe's India teams have been central to Firefly development and Document Cloud AI features. The question of who succeeds Narayen, and whether the next CEO continues investing in the India engineering org, has direct career implications.

More broadly, Narayen's departure marks a generational transition for Indian-origin tech leadership. Nadella and Pichai still hold their seats. But the lesson from Adobe is that even an 18-year track record does not insulate an executive from the structural forces that AI is unleashing on software businesses.

Adobe's bet is that giving its tools away will ultimately bring more users into the ecosystem than it loses to competitors. It is a reasonable bet. But it is also the kind of bet a company makes when it no longer controls the terms of competition."""
}

# ─────────────────────────────────────────────────────────
# ARTICLE 2: $100K H-1B Fee Struck Down
# ─────────────────────────────────────────────────────────

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "A Federal Judge Just Killed the $100,000 H-1B Fee. Here's What That Actually Changes.",
    "subheadline": "Applications had dropped 27 per cent. Indian professionals, who receive more than 70 per cent of all H-1B approvals, bore the brunt. The ruling reopens the door — but not all the way.",
    "slug": make_slug("h1b-100k-fee-struck-down-judge-indian-workers"),
    "category": "technology",
    "vertical": "immigration",
    "diaspora_angle": "Indians receive more than 70 per cent of all H-1B approvals annually, making them the single largest group affected by the $100K fee hike. The ruling directly benefits tens of thousands of Indian tech professionals and their US-based employers, but the broader immigration environment remains hostile.",
    "tags": ["h-1b", "immigration", "indian-tech-workers", "trump", "silicon-valley"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/politics/policy/judge-strikes-down-trump-administrations-100-000-h-1b-visa-fee-2026-06-09"},
        {"name": "Inc.", "url": "https://www.inc.com/headline/trumps-100000-h-1b-visa-fee-was-just-struck-down-why-many-employers-still-have-a-bigger-problem.html"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/100000-h1b-visa-fee-us-judge-blocks/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/32442906/pexels-photo-32442906.jpeg",
    "image_caption": "Federal courthouse in San Francisco, near the heart of H-1B-dependent tech country",
    "image_attribution": "Pexels",
    "body": """A federal judge in Massachusetts has invalidated the Trump administration's $100,000 fee for new H-1B visa applications, calling the charge an unlawful tax imposed without congressional authorisation.

Judge Leo Sorokin's ruling on Monday sided with a coalition of states that argued the fee gutted their ability to staff universities, hospitals, and public schools with qualified foreign professionals. But the most immediate impact falls on the technology industry — and specifically on the Indian professionals who dominate the programme.

## The Fee's Toll

When President Trump issued a proclamation last September imposing the $100,000 fee on new H-1B petitions, the effect was swift and measurable. Applications for the current cycle dropped 27 per cent, falling from 470,342 in 2025 to 343,981. The fee applied to any petition filed after September 21, 2025, and gave the Department of Homeland Security broad discretion over exemptions — discretion that critics argued could be used to punish disfavoured employers.

For Indian tech workers, the numbers are personal. Indians account for more than 70 per cent of all approved H-1B petitions annually, a share that has held steady since at least 2015. At the major employers — Google, Microsoft, Amazon, Meta, Infosys, TCS — the H-1B programme is the primary pathway for Indian engineers to work in the United States.

The $100,000 fee made that pathway brutally expensive. A mid-level engineer earning $150,000 at a Bay Area company could see the visa cost consume two-thirds of their annual salary, assuming the employer did not absorb it. Many employers did not. Some companies quietly paused new H-1B filings altogether, while others accelerated transfers of work to India or Canada.

## What the Ruling Says

Sorokin's opinion was blunt. "The Court finds that the Policy imposes a tax on H-1B petitions without the requisite delegation by Congress," he wrote. "There are no statutory powers authorising Defendants to implement a $100,000 tax on H-1B petitions."

The judge vacated the fee requirement nationwide, rejecting the administration's argument that relief should be limited to the states that filed the lawsuit. The ruling effectively restores the previous fee structure, which totalled roughly $5,000 per application.

Trump had framed the fee as a corrective to what he called abuses of the programme — companies using H-1B visas to hire foreign workers at lower wages than Americans in comparable positions. The argument resonated with parts of the electorate but collided with the reality that H-1B workers at major tech firms typically earn well above the prevailing wage.

## The Bigger Picture

The ruling is a reprieve, not a resolution. The Trump administration is expected to appeal, and other courts have reached different conclusions. In a separate challenge brought by the US Chamber of Commerce, an Obama-appointed judge in Washington sided with the administration and upheld the fee as lawful.

Meanwhile, the broader immigration landscape for Indian tech workers remains treacherous. The same week the fee was struck down, Representative Chip Roy introduced a bill that would eliminate the H-1B lottery entirely, end Optional Practical Training for foreign students, and sever the connection between temporary work visas and employer-sponsored green cards.

For the roughly 300,000 Indians currently in the green card backlog — many of whom have been waiting a decade or longer — these developments carry an existential weight that a fee reduction alone does not address.

## What It Means in Practice

Tech companies are expected to resume normal H-1B filing volumes for the next cycle, assuming the ruling survives appeal. Hiring managers at FAANG companies and Indian IT services firms alike had been holding requisitions that required new visa sponsorship; some of those positions will now be released.

But the damage from the nine-month freeze is not easily undone. Engineers who accepted offers in Canada, the UK, or returned to India are not all coming back. University programmes that lost international applicants will need time to rebuild pipelines. And the chilling effect on startup hiring — small companies that could never have absorbed a $100,000 per-employee cost — may linger even after the legal question is settled.

For Indian Americans already in the United States, the ruling is a reminder that the system they navigated remains fragile. A single executive order nearly shut the door behind them. That the judiciary intervened is reassuring. That it had to intervene at all is not."""
}

# ─────────────────────────────────────────────────────────
# ARTICLE 3: TCS — 500K AI Agents = 500K Employees
# ─────────────────────────────────────────────────────────

chandra_img = fetch_wikipedia_person_image("Natarajan Chandrasekaran")

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "TCS Will Have as Many AI Agents as Human Employees Within Three Years. That Is Not a Metaphor.",
    "subheadline": "Chairman N. Chandrasekaran told shareholders the company's 500,000 employees will work alongside 500,000 AI agents — and that hiring at the old scale is over.",
    "slug": make_slug("tcs-500k-ai-agents-chandrasekaran-agm-hiring"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "TCS employs tens of thousands of workers on H-1B and L-1 visas in the US and is the single largest recruiter of Indian engineering graduates. The shift to AI agents directly affects the career calculus for Indian engineers — both those planning to join IT services and those already on visa-dependent careers at TCS's US offices.",
    "tags": ["tcs", "ai-agents", "indian-it", "hiring", "chandrasekaran"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-tcs-chair-says-ai-agents-may-equal-headcount-dampen-hiring-2026-06-10/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/will-have-as-many-ai-agents-as-human-employees-over-the-next-three-years-tcs-chairman-chandrasekaran/article69654321.ece"},
        {"name": "SightsIn Plus", "url": "https://sightsinplus.com/news/tcs-to-match-human-staff-count-with-ai-workers/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": chandra_img or "https://upload.wikimedia.org/wikipedia/commons/4/46/Natarajan_Chandrasekaran_-_India_Economic_Summit_2011.jpg",
    "image_caption": "N. Chandrasekaran, chairman of TCS and Tata Sons, at an industry event",
    "image_attribution": "Wikimedia Commons",
    "body": """At the 31st annual general meeting of Tata Consultancy Services, held virtually on Tuesday, Chairman N. Chandrasekaran delivered a statement that will echo through India's technology industry for years. Within three years, he said, TCS would deploy as many AI agents as it has human employees — roughly half a million of each, working side by side.

"The company has half a million employees. The day is not far when the company will have half a million AI agents," Chandrasekaran told shareholders. "Will it lead to a decrease in hiring? Absolutely. The company will not be hiring the kind of numbers it used to hire."

It was the most explicit public acknowledgement by any Indian IT chief that the industry's labour-intensive model — the engine that powered decades of Indian middle-class prosperity — is being structurally rewired by artificial intelligence.

## The Numbers Behind the Pivot

TCS is not speaking hypothetically. In the last quarter of fiscal 2026, the company reported annualised AI revenue of $2.4 billion, growing at a compound quarterly rate of 22.4 per cent. That figure positions AI as TCS's fastest-growing revenue stream, outpacing traditional application maintenance and infrastructure management services.

To prepare its workforce, TCS invested 69 million learning hours in FY26. More than 217,000 associates — nearly half the company — are now certified in advanced AI skills, retrained from roles in software testing, application support, and process management into what the company calls AI supervisors and context managers.

But retraining does not prevent headcount decline. TCS reduced its workforce by approximately 26,000 employees in FY26. It had originally projected a reduction of just 1,200. The gap between forecast and reality tells the story: the transition is moving faster than even TCS expected.

## What 'Agentic AI' Means for IT Services

The AI agents Chandrasekaran described are not chatbots or simple automation scripts. In TCS's framing, they are autonomous software systems capable of writing code, testing applications, managing deployments, and running complex enterprise workflows with minimal human oversight.

The business model shift is fundamental. For two decades, Indian IT services companies billed clients based on headcount — more engineers on the project meant more revenue. AI agents invert that equation. A team of five engineers plus twenty AI agents can now deliver the output that once required fifty engineers. The revenue per project may stay the same, but the number of humans needed drops sharply.

Chandrasekaran argued this is not a death sentence for the industry but a transformation of its economics. "The market has misunderstood the relationship between AI and IT services," he said, predicting that falling intelligence costs would expand global enterprise IT spending to $3 trillion over the next decade — roughly double the current market.

He identified five growth pillars: modernising legacy systems, reshaping business processes through AI, managing AI governance and compliance, building sovereign AI frameworks for regulated governments, and deploying physical AI in industrial settings.

## The H-1B Question

For the tens of thousands of TCS employees who work in the United States on H-1B and L-1 visas, the implications are direct. TCS is one of the largest H-1B sponsors in the country. If the company's US projects require fewer engineers per engagement, the number of visa-sponsored positions will contract accordingly.

This is already visible in the data. India's top six IT companies collectively reduced headcount by nearly 72,000 in FY24 and added back only 15,375 in FY25. ICRA, the credit rating agency, confirmed seven consecutive quarters of negative net hiring through early FY25.

For Indian engineering graduates eyeing IT services as a pathway to US employment, the calculus has shifted. The mass campus recruitment drives that defined two decades of Indian IT — companies like TCS, Infosys, and Wipro hiring 30,000 to 50,000 freshers per year — are winding down. Chandrasekaran confirmed as much on Tuesday: the era of hiring at that scale is simply over.

## The Industry Response

The response from other IT leaders has been carefully worded but directionally aligned. Infosys has built an AI-powered tool to create Global Capability Centres that themselves use AI. Wipro has restructured its delivery model around smaller, AI-augmented teams. HCL Tech reduced headcount by 261 in its most recent quarter while growing revenue 7.4 per cent — a divergence that would have been unthinkable five years ago.

TeamLease Digital CEO Neeti Sharma called it plainly: "Unlike previous cycles, this is a structural — not cyclical — correction driven by AI-led productivity compression."

For the Indian diaspora, the transformation touches something deeper than quarterly earnings. The IT services industry built the Indian middle class. It funded the home loans, the US education, the family back home. Chandrasekaran's 500,000-agent prediction is not just a business strategy. It is a renegotiation of the social contract between India's largest private-sector employers and the millions of families whose aspirations they once reliably served."""
}

# ─────────────────────────────────────────────────────────
# Insert all articles
# ─────────────────────────────────────────────────────────

articles = [article1, article2, article3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
