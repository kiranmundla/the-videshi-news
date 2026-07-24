#!/usr/bin/env python3
"""News writer: 3 articles for June 10, 2026 — corrected schema"""

import json, os, requests
from datetime import datetime, timezone

# Load env
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            val = val.strip().strip('"').strip("'")
            os.environ[key.strip()] = val

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

articles = []

# ─────────────────────────────────────────────────
# ARTICLE 1: Reliance-Meta 168MW AI Data Centre
# ─────────────────────────────────────────────────
articles.append({
    "headline": "Reliance and Meta Are Building India's First Hyperscale AI Data Centre. It Will Run on Seawater.",
    "subheadline": "The 168-megawatt facility in Jamnagar marks Meta's first built-to-suit data centre in the country, powered by renewables and cooled with desalinated seawater — and Reliance will run the whole thing.",
    "slug": "reliance-meta-168mw-ai-data-centre-jamnagar-seawater-cooled-20260610",
    "category": "news",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/69/Mukesh_Ambani.jpg",
    "image_caption": "Mukesh Ambani, Chairman of Reliance Industries, who called the deal a 'transformative moment' for India's digital infrastructure",
    "image_attribution": "Wikimedia Commons",
    "published_at": now_iso,
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Inc42", "url": "https://inc42.com/buzz/meta-partners-reliance-to-set-up-first-data-centre-in-india/"},
        {"name": "YourStory", "url": "https://yourstory.com"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"},
        {"name": "Meta official statement", "url": "https://about.meta.com"}
    ],
    "diaspora_angle": "India hosting physical AI infrastructure for a $1.5 trillion American tech giant marks a shift from services to foundational computing. For NRIs tracking India's tech trajectory, this puts the country in the same conversation as the US, Ireland, and Singapore for hyperscale data centres.",
    "vertical": "technology",
    "tags": ["reliance", "meta", "data-centre", "ai-infrastructure", "jamnagar", "mukesh-ambani", "zuckerberg", "renewable-energy"],
    "urgency": "high",
    "body": """India's largest private company and the world's largest social media company just shook hands on a deal that could reshape where the planet's AI infrastructure gets built.

Reliance Industries and Meta Platforms announced on Wednesday that they will jointly develop a 168-megawatt AI-enabled data centre in Jamnagar, Gujarat. The facility — Meta's first custom-built data centre anywhere in India — will be constructed by Reliance and leased to Meta, with an option to scale further. It is expected to go live within two years.

## Why Jamnagar

The choice of location is deliberate. Jamnagar is already home to the world's largest oil refinery complex, and Reliance is now pivoting the city toward a very different kind of energy infrastructure. The data centre will run entirely on renewable power and use desalinated seawater for cooling — an unusual engineering choice that eliminates the freshwater burden that makes data centres controversial in water-stressed regions.

"Building India's first built-to-suit data centre for a global technology leader of Meta's scale demonstrates India's readiness to be at the forefront of the global AI revolution," Mukesh Ambani said in a statement. "Jamnagar will become a landmark destination for hyperscale AI computing."

Mark Zuckerberg called the facility a way to "scale our AI infrastructure globally while deepening our long-term investment in India's economy."

## The Full Stack Play

Under the agreement, Reliance will act as a single-window solutions provider — handling design, construction, utility management, renewable power supply, network connectivity, and day-to-day operations. The setup leverages Jamnagar's proximity to India's western submarine cable landing stations and Jio's extensive fibre network, giving Meta low-latency connectivity to its 500-million-plus Indian user base.

Meta is also separately partnering with CleanMax and Fourth Partner Energy to back nearly 1 gigawatt of new clean energy capacity in India. The total renewable energy commitment signals that Meta is not treating India as a secondary market — it is building foundational infrastructure here.

## What It Means for the Diaspora

For NRIs watching India's tech trajectory, this deal is a marker. India has long been a services powerhouse — writing the code, running the call centres, managing the back offices. But hosting the physical AI infrastructure of a $1.5 trillion American tech giant is a qualitative shift. It puts India in the same conversation as the US, Ireland, and Singapore as a destination for hyperscale computing.

The partnership also builds on a relationship that started with Meta's $5.7 billion investment in Jio Platforms in 2020. That deal gave WhatsApp a payments layer and Facebook a distribution channel. This one gives Meta compute capacity and Reliance a foothold in one of the world's fastest-growing infrastructure markets.

## The Bigger Picture

India's data centre market is projected to grow from 1.3 GW of installed capacity in 2025 to over 3 GW by 2028, driven by the AI boom and the government's push for data localisation. Reliance, Adani, Tata, and the Hiranandani Group are all racing to build capacity. But having Meta as an anchor tenant changes the economics — and the credibility — of Jamnagar's bet.

The deal also arrives as India grapples with the Iran war's impact on energy costs. A data centre powered entirely by renewables sidesteps the fossil fuel volatility that is squeezing Indian industry right now. In that sense, Jamnagar is not just an AI play. It is a hedge."""
})

# ─────────────────────────────────────────────────
# ARTICLE 2: Zoho Nathu La Server
# ─────────────────────────────────────────────────
articles.append({
    "headline": "Zoho Just Built Its Own Server From Scratch. In Nagpur.",
    "subheadline": "The Chennai-based SaaS giant spent five years designing a server platform in-house, with all intellectual property owned in India. It wants to cut AI inference costs by 30 percent and reduce dependence on foreign hardware.",
    "slug": "zoho-nathu-la-server-designed-india-nagpur-ai-inference-sovereignty-20260610",
    "category": "news",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Zoho_headquarters_in_chennai.jpg/1280px-Zoho_headquarters_in_chennai.jpg",
    "image_caption": "Zoho Corporation headquarters in Chennai, the parent company behind the Nathu La server platform",
    "image_attribution": "Wikimedia Commons",
    "published_at": now_iso,
    "sources": [
        {"name": "Inc42", "url": "https://inc42.com/buzz/zoho-launches-in-house-server-nathu-la-to-lower-ai-inference-costs/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/zoho-launches-its-own-designed-in-india-server-nathu-la/article69671234.ece"},
        {"name": "Business Wire", "url": "https://www.businesswire.com"},
        {"name": "Express Computer", "url": "https://www.expresscomputer.in"},
        {"name": "CXOToday", "url": "https://www.cxotoday.com"}
    ],
    "diaspora_angle": "For NRIs in tech who have spent careers building infrastructure for American hyperscalers, Zoho designing competitive hardware in Nagpur — not Bangalore or an IIT incubator — is both validation and a statement about India's Tier 2 cities.",
    "vertical": "technology",
    "tags": ["zoho", "nathu-la", "made-in-india", "server", "ai-inference", "tech-sovereignty", "nagpur", "hardware"],
    "urgency": "medium",
    "body": """When India talks about technology sovereignty, the conversation usually stops at software. Zoho just pushed it down to the bare metal.

The Chennai-based enterprise SaaS giant has unveiled Nathu La, an indigenously designed server platform that was developed entirely in-house over five years by a team in Nagpur. The server runs on Intel Xeon 6 processors, uses custom-engineered motherboards and network interface cards, and delivers performance equivalent to existing alternatives — at 20 to 30 percent lower total cost of ownership and 12 to 18 percent less power consumption, according to the company.

## Built in Small-Town India

The backstory is quintessentially Zoho. In 2020, the company quietly set up a small R&D team in Nagpur — not Bangalore, not Hyderabad, not even its own headquarters in Chennai — to work on designing a server from the ground up. The talent was recruited locally and trained in-house, consistent with founder Sridhar Vembu's long-standing conviction that world-class technology can be built outside India's metro bubbles.

"We are proud to build a server system that is truly designed in India and taking a step towards creating sovereign technology," said Shailesh Davey, CEO of Zoho Corporation. "The development of the Nathu La server reflects our commitment to creating complex technology powered by talent from smaller towns and villages."

The company has already deployed a few hundred units, with 1,000 servers in production and pre-production and a target of 2,000 by the end of the year. The platform is designed for virtualisation, high-performance computing, AI inference, and storage workloads across Zoho's global SaaS infrastructure.

## Why It Matters

India imports the overwhelming majority of its server hardware. The underlying intellectual property — board designs, firmware, systems management — has historically been owned by American, Taiwanese, and Chinese companies. In 2023, the Indian government imposed import restrictions on compute devices including servers, highlighting the vulnerability.

Zoho's move makes it one of a handful of technology companies globally to own the full stack from hardware to software applications. The Nathu La platform includes in-house-designed motherboards, a proprietary Data Centre Secure Control Module, modular chassis configurations, and custom network interface cards. Assembly is handled by Indian electronics manufacturing partners. The company has filed five new patents covering thermal management and modular server architecture.

## The AI Inference Angle

The timing is not accidental. As enterprises race to deploy AI across their operations, the cost of running inference — the step where a trained model actually processes queries and generates outputs — is becoming a significant line item. For a company like Zoho, which runs AI features across dozens of SaaS products serving millions of users, even a 20 percent reduction in infrastructure cost compounds into serious savings.

"With Zoho's strategy of using contextual, right-sized models, running on our own platform, now on our own servers, accelerated by our own GPU database, we are compounding the benefits accrued from owning and operating our entire technology stack," Davey said.

## The Diaspora Connection

For NRIs in the tech industry — many of whom have spent careers building infrastructure for American hyperscalers — Zoho's achievement is both validation and provocation. The company is demonstrating that India can design competitive hardware, not just manufacture it under foreign licences. The Nagpur angle makes it sharper: this was not done at an IIT incubator or a Bangalore tech park, but at a centre specifically built to prove that India's Tier 2 and Tier 3 cities can produce cutting-edge engineering.

Zoho does not plan to commercialise the server platform yet. For now, Nathu La will serve Zoho's own infrastructure. But the IP is Indian, the talent is Indian, and the implications extend well beyond one company's data centres."""
})

# ─────────────────────────────────────────────────
# ARTICLE 3: H-1B $100K Fee Struck Down
# ─────────────────────────────────────────────────
articles.append({
    "headline": "A Federal Judge Just Killed Trump's $100,000 H-1B Fee. The Fight Is Not Over.",
    "subheadline": "The ruling strikes down a charge that threatened to choke the pipeline Indian tech workers have built careers around. But the White House plans to appeal, and other restrictions remain firmly in place.",
    "slug": "federal-judge-strikes-down-trump-100000-h1b-visa-fee-indian-tech-workers-20260610",
    "category": "news",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Capitol_at_Dusk_2.jpg/1280px-Capitol_at_Dusk_2.jpg",
    "image_caption": "The US Capitol building in Washington, where Congress holds the exclusive authority to levy taxes that the judge ruled Trump overstepped",
    "image_attribution": "Wikimedia Commons",
    "published_at": now_iso,
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com/world/us/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-09/"},
        {"name": "CNN", "url": "https://www.cnn.com/2026/06/09/politics/h1b-visa-fee-trump/index.html"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/trumps-100000-h-1b-fee-ruled-unlawful-heres-what-it-means-for-indian-applicants"},
        {"name": "Associated Press", "url": "https://apnews.com"}
    ],
    "diaspora_angle": "Indian nationals receive over 70% of all H-1B visas. The $100,000 fee threatened to fundamentally alter the economics of hiring Indian talent in America. With the Modi-Trump bilateral at the G7 just days away and H-1B visas on the agenda, the ruling adds a powerful card to New Delhi's hand.",
    "vertical": "immigration",
    "tags": ["h1b", "immigration", "trump", "visa-fee", "indian-tech-workers", "federal-court", "diaspora"],
    "urgency": "high",
    "body": """A federal judge in Boston has struck down the Trump administration's $100,000 fee on H-1B visa applications, ruling that the president imposed an unlawful tax that Congress never authorised. The decision is a landmark win for Indian tech professionals — but the relief may be temporary.

US District Judge Leo Sorokin issued the ruling on Monday in a lawsuit brought by 20 Democratic state attorneys general. The judge concluded that the fee, introduced by presidential proclamation in September 2025, functioned as a tax rather than a lawful penalty, and that neither the president nor federal agencies had the authority to collect it.

"The Court finds that the Policy imposes a tax on H-1B petitions without the requisite delegation by Congress," Sorokin wrote in a 42-page decision. "There are no statutory powers authorizing Defendants to implement a $100,000 tax on H-1B petitions."

## The Scale of the Threat

Before the fee was announced, employers typically paid between $2,000 and $5,000 to sponsor a foreign worker for an H-1B visa. Trump's $100,000 charge — a 20-to-50-fold increase — sent shockwaves through the tech industry and Indian diaspora communities. Some companies scrambled to bring workers back to the US before the policy took full effect, though the administration later clarified it would only apply to new petitions, not renewals.

The fee was so prohibitive that only 85 payments had been made as of February, according to USCIS data cited in a March court filing. The programme itself serves 65,000 new visas annually, with another 20,000 reserved for workers with advanced degrees. Indian nationals received 283,397 H-1B visas in 2024 — more than 70 percent of the total, and six times the number issued to the next-largest group, Chinese nationals.

## Why the Judge Ruled It Unlawful

Sorokin drew on the Supreme Court's February ruling that struck down Trump's sweeping tariffs under a law meant for national emergencies. Under similar reasoning, the judge found that immigration law gives the president power to restrict entry of foreign nationals — but not to levy a tax on a legal programme.

"Hiring workers pursuant to the H-1B programme is plainly lawful," the judge wrote. The fee did not penalise illegal behaviour; it taxed legal immigration — a power reserved exclusively for Congress.

The ruling also found violations of the Administrative Procedure Act, which requires agencies to undergo public notice-and-comment before implementing major policy changes. The administration had bypassed that process entirely.

## The Conflicting Rulings Problem

This is where it gets complicated. In a separate challenge brought by the US Chamber of Commerce, Judge Beryl Howell in Washington DC sided with the Trump administration in December, finding the fee lawful. A third lawsuit, filed by religious groups and labour organisations in San Francisco, is still pending.

The result is a split among federal courts — a situation that will likely force the issue to the appeals courts and potentially the Supreme Court. Until then, the legal landscape is uncertain.

## What Stays in Place

Indian diaspora organisations welcomed the ruling, but cautioned against premature celebration. Sanjeev Joshipura, Executive Director of Indiaspora, noted that the administration retains other tools to tighten the H-1B pipeline: enhanced vetting of applicants, a proposed selection process weighted toward higher-paid workers, and broader enforcement actions that fall short of outright legal violations.

The White House called the ruling "crazy" and said it was confident the decision would be reversed on appeal. Spokesperson Taylor Rogers asserted that the president "has clear legal authority to restrict entry of any class of aliens he determines is not in America's best interests."

## The Stakes for Indian Americans

The H-1B programme is the entry point for a pipeline that has produced CEOs at Google, Microsoft, and IBM; thousands of founders at American startups; and a professional class that contributes an estimated $1 trillion annually to the US economy. The $100,000 fee was not just an administrative burden — it threatened to fundamentally alter the economics of hiring Indian talent in America.

With the Modi-Trump bilateral at the G7 summit just days away, and H-1B visas reportedly on the agenda, Monday's ruling adds a powerful card to New Delhi's hand. But the game is far from over."""
})

# ─────────────────────────────────────────────────
# INSERT ALL ARTICLES
# ─────────────────────────────────────────────────
for i, article in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Inserting article {i+1}: {article['headline'][:70]}...")
    
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    
    if resp.status_code in (200, 201):
        data = resp.json()
        if isinstance(data, list) and len(data) > 0:
            print(f"  ✓ Inserted: id={data[0].get('id','?')}, slug={data[0].get('slug','?')}")
        else:
            print(f"  ✓ Inserted (response: {str(data)[:100]})")
    else:
        print(f"  ✗ FAILED: {resp.status_code} — {resp.text[:500]}")

print("\n\nDone. All 3 articles submitted for review.")
