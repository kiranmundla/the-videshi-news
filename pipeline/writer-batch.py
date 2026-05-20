#!/usr/bin/env python3
"""Videshi Writer batch — inserts 4 articles for news, technology, markets-finance."""

import json, os, sys, datetime, requests

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", SUPABASE_ANON_KEY)

HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

articles = [
    {
        "topic_id": "7db760ed-5ebe-4730-858a-8eafa2ca5dc2",
        "headline": "The $35 Billion Container Cartel: How a Pandemic-Era Price-Fixing Scheme Hit Indian Exporters Hardest",
        "subheadline": "Seven Chinese executives and four firms that control 95% of global container production have been indicted for doubling prices and restricting output — with ripple effects still squeezing Indian supply chains",
        "category": "markets-finance",
        "vertical": "economy",
        "urgency": "breaking",
        "slug": "chinese-container-cartel-indictment-india-impact-20260520",
        "tags": ["shipping containers", "price fixing", "antitrust", "supply chain", "Indian exports", "DOJ", "CIMC", "pandemic"],
        "diaspora_angle": "Indian exporters and NRI-owned logistics businesses bore disproportionate costs from inflated container prices. The indictment has direct implications for India's $35 billion containerised export sector and diaspora-run trade corridors.",
        "sources": [
            {"url": "https://www.justice.gov/opa/pr/four-worlds-largest-container-manufacturing-companies-and-seven-their-executives-indicted", "name": "US Department of Justice"},
            {"url": "https://www.reuters.com/legal/us-indicts-chinese-shipping-container-makers-price-fixing", "name": "Reuters"},
            {"url": "https://www.pymnts.com/news/regulation/2026/doj-accuses-chinese-shipping-container-executives-pandemic-antitrust/", "name": "PYMNTS"},
            {"url": "https://devdiscourse.com/article/headlines/3363109-update-3-us-charges-seven-chinese-executives-and-four-firms-with-illegal-shipping-container-cartel", "name": "Devdiscourse"}
        ],
        "body": """The US Department of Justice has unsealed one of the most consequential antitrust indictments in years — charging four Chinese shipping container manufacturers and seven of their executives with orchestrating a global price-fixing conspiracy that roughly doubled the cost of standard shipping containers during the COVID-19 pandemic. The scheme, which ran from November 2019 to at least January 2024, artificially inflated prices across an industry that moves billions of dollars of goods to American and Indian households every year.

The four companies — China International Marine Containers (CIMC), Dong Fang International Container, CXIC Group Containers, and Singamas Container Holdings — together manufacture approximately 95% of the world's standard dry shipping containers. According to prosecutors, senior executives from these firms met at CIMC's headquarters in Shenzhen in November 2019 to formalise an agreement to restrict output using production quotas, shift limitations, and 87 surveillance cameras installed across 49 production lines to monitor compliance. A penalty fund was established to punish any company that exceeded its allotted production.

The results were staggering. CIMC's container manufacturing profits surged from $19.8 million in 2019 to $1.75 billion in 2021 — a nearly hundredfold increase. Singamas swung from a $110 million loss to $186.8 million in profit over the same period. "Around the start of the global pandemic, these manufacturers exploited the crisis and their market power to squeeze the supply chain for profit," said Associate Attorney General Stanley Woodward.

## Why This Matters for Indian Trade

India's containerised export sector, which handles everything from textiles and pharmaceuticals to auto parts and agricultural products, was among the hardest hit globally. When container prices doubled, Indian exporters — many of them small and medium enterprises with thin margins — faced a brutal choice: absorb the costs or lose contracts. Industry bodies like the Federation of Indian Export Organisations (FIEO) had repeatedly flagged the crisis, warning that container shortages and price spikes were making Indian goods uncompetitive against rivals in Vietnam and Bangladesh.

The pain extended well beyond India's ports. NRI-owned logistics and freight forwarding businesses across the US, UK, and Middle East found their operational costs ballooning. Trade corridors that the Indian diaspora has built over decades — moving everything from Basmati rice to generic medications — were disrupted at scale. Container booking rates on the India-to-US West Coast route, which typically ran around $2,000 per forty-foot equivalent unit (FEU), spiked above $10,000 during the worst of the crisis.

## The Enforcement and What Comes Next

One executive, Vick Ma of Singamas, was arrested in France in April 2026 and awaits extradition. Six other individual defendants remain at large. The charges carry a maximum of 10 years in prison for individuals and fines of up to $100 million for corporations — though penalties could be doubled based on the gains derived from the conspiracy.

The indictment arrives at a geopolitically charged moment. US President Donald Trump visited China last week without major trade breakthroughs, and the DOJ's action against Chinese companies adds another layer of tension to an already fraught bilateral relationship. For India, the case is both vindication and warning: vindication that the price spikes Indian businesses endured were not simply market forces at work, but the result of deliberate collusion; and a warning that India's heavy dependence on Chinese-manufactured containers remains a structural vulnerability.

India has taken some steps to reduce this dependency. The government launched a container manufacturing incentive scheme in 2023, and companies like Bharat Forge and Container Corporation of India (CONCOR) have explored domestic production. But progress has been slow — India still imports the vast majority of its containers from China.

## The Diaspora Dimension

For the estimated 4.5 million Indian Americans and the broader global diaspora engaged in trade, the indictment raises a fundamental question about supply chain sovereignty. Indian-origin entrepreneurs who run import-export businesses across North America and the Gulf states experienced the price-fixing directly: in delayed shipments, in cancelled orders, in margins that evaporated overnight. As the DOJ pursues this case through the courts, the Indian business community — both at home and abroad — will be watching closely to see whether accountability translates into structural reform in an industry that remains, for now, overwhelmingly controlled by a handful of Chinese manufacturers.""",
    },
    {
        "topic_id": "9873fa59-19dc-4711-917f-e92ac3112324",
        "headline": "OpenAI Is Racing to Wall Street — and India's AI Workforce Should Pay Attention",
        "subheadline": "With a September IPO target, an $852 billion valuation, and $14 billion in projected losses, Sam Altman's company is about to become the most scrutinised AI bet in history",
        "category": "technology",
        "vertical": "technology",
        "urgency": "breaking",
        "slug": "openai-ipo-september-india-ai-workforce-20260520",
        "tags": ["OpenAI", "IPO", "Sam Altman", "artificial intelligence", "Goldman Sachs", "Morgan Stanley", "AI jobs India", "Elon Musk"],
        "diaspora_angle": "Indian-origin engineers form a significant portion of OpenAI's workforce and the broader AI talent pipeline. The IPO's success or failure will shape hiring, compensation, and career trajectories for tens of thousands of Indian tech workers in Silicon Valley and Bengaluru alike.",
        "sources": [
            {"url": "https://www.pymnts.com/news/ipo/2026/openai-eyes-september-ipo-despite-14-billion-projected-loss/", "name": "PYMNTS"},
            {"url": "https://techcrunch.com/2026/05/20/openai-barrels-towards-ipo-that-may-happen-in-september/", "name": "TechCrunch"},
            {"url": "https://www.reuters.com/technology/openai-aiming-speedy-ipo-2026-05-20/", "name": "Reuters"},
            {"url": "https://www.engadget.com/ai/openai-may-go-public-as-soon-as-september-153028556.html", "name": "Engadget"},
            {"url": "https://seekingalpha.com/news/4533456-openai-prepares-possibly-file-ipo-friday", "name": "Seeking Alpha"}
        ],
        "body": """OpenAI, the company behind ChatGPT, is preparing to file confidentially for a US initial public offering in the coming days or weeks, with a target to go public as early as September. The filing, reported by the Wall Street Journal and confirmed by Reuters, would make OpenAI the most valuable technology company to debut on public markets since at least the dot-com era — and possibly ever.

The numbers are extraordinary by any measure. OpenAI was valued at $852 billion in its most recent private funding round earlier this year, when it raised $122 billion. It has 900 million weekly users and annualised revenue of $25 billion. It is also projecting a net loss of approximately $14 billion for the current year, driven by massive spending on computing infrastructure, research talent, and the relentless buildout of AI models that require exponentially more processing power with each generation.

Goldman Sachs and Morgan Stanley are working with the company on a draft IPO prospectus. CEO Sam Altman has been pushing for a listing, though CFO Sarah Friar has privately told company leaders that the firm may need more time, according to the Journal. The tension between Altman's urgency and Friar's caution reflects a broader debate within OpenAI about whether the company is truly ready for the scrutiny that public markets demand.

## Clearing the Legal Runway

The IPO push comes days after OpenAI won a crucial legal battle. A jury ruled in favour of the company in a lawsuit filed by co-founder Elon Musk, who had sought to block OpenAI's conversion from a nonprofit to a for-profit structure. Musk has said he plans to appeal, but analysts at Wedbush Securities called the verdict a removal of a "significant overhang" that had clouded the company's path to public markets.

The timing is not coincidental. SpaceX, Musk's rocket company, is also preparing for an IPO, with paperwork expected soon. The two listings could create a rare moment where the two most prominent figures in American technology — Altman and Musk — are simultaneously pitching their companies to public investors while locked in a bitter personal and legal feud.

## What This Means for India's Tech Economy

OpenAI's IPO is not just a Silicon Valley event. It will ripple through India's technology ecosystem in at least three significant ways.

First, **talent and compensation**. Indian-origin engineers are deeply embedded in OpenAI's workforce and across the AI research community. A successful IPO would create a new wave of stock-option wealth among Indian-origin employees, while also intensifying the already fierce competition for AI talent between San Francisco and Bengaluru. Companies like Google, Microsoft, and Anthropic — all of which employ thousands of Indian engineers — will face renewed pressure to match the compensation packages that a publicly traded OpenAI can offer.

Second, **India's AI startup ecosystem**. OpenAI's public debut will establish a benchmark valuation for AI companies globally. Indian AI startups — from Krutrim to Sarvam AI — will be measured against OpenAI's revenue multiples and growth trajectory. A rich valuation could unlock more venture capital for Indian AI firms; a disappointing reception could tighten funding across the sector.

Third, **the infrastructure question**. OpenAI has acknowledged it may need $207 billion in additional capital by 2030 to build the computing infrastructure its models require. Much of this infrastructure buildout will involve data centres, semiconductor supply chains, and cloud computing capacity that increasingly touch India. Microsoft, OpenAI's largest backer with over $100 billion invested, has committed billions to expanding its Azure data centre footprint in India — investments that are directly tied to the AI workloads OpenAI generates.

## The Open Questions

The IPO will also force uncomfortable transparencies. OpenAI has recently missed multiple internal revenue and user targets, according to the Journal. Anthropic, its closest competitor, has been growing faster and winning business customers at a rapid clip. Google's Gemini models have eroded ChatGPT's dominance in several enterprise categories.

For India's six million technology workers, the OpenAI IPO is not an abstract financial event. It is a signal about where the industry is heading, what skills will command premiums, and whether the AI boom that has reshaped Silicon Valley over the past three years will sustain itself — or buckle under the weight of its own capital requirements. September will provide the first definitive answer.""",
    },
    {
        "topic_id": "8bd35d13-b3e6-4bfb-a8a1-c7165324a736",
        "headline": "Xi and Putin Sign 40 Agreements in Beijing — With India's BRICS Balancing Act Now More Delicate Than Ever",
        "subheadline": "The Russia-China summit, coming days after Trump's visit, deepens energy and trade ties while putting New Delhi's September hosting duties under a geopolitical spotlight",
        "category": "news",
        "vertical": "geopolitics",
        "urgency": "breaking",
        "slug": "xi-putin-beijing-summit-india-brics-implications-20260520",
        "tags": ["Xi Jinping", "Vladimir Putin", "China", "Russia", "Beijing summit", "BRICS", "India", "Modi", "geopolitics", "energy"],
        "diaspora_angle": "India's delicate position between Russia, China, and the US directly affects diaspora interests — from defence procurement and energy prices to the diplomatic positioning that shapes how NRIs are perceived in their adopted countries.",
        "sources": [
            {"url": "https://www.livemint.com/news/world/putin-xi-beijing-meeting-highlights-friendship-sees-over-40-bilateral-cooperation-agreements-more-10-key-updat-11779273339434.html", "name": "Livemint"},
            {"url": "https://www.reuters.com/world/china/xi-putin-meet-china-reaffirm-ties-days-after-trump-visit-2026-05-20/", "name": "Reuters"},
            {"url": "https://devdiscourse.com/article/politics/3363452-president-putin-to-attend-brics-summit-in-new-delhi-on-sep-12-13-kremlin-aide", "name": "Devdiscourse"},
            {"url": "https://barchart.com/story/news/33890741/xi-and-putin-meet-to-reaffirm-china-russia-ties-days-after-trumps-visit-to-beijing", "name": "AP/Barchart"}
        ],
        "body": """Chinese President Xi Jinping and Russian President Vladimir Putin met in Beijing on Wednesday and signed more than 40 cooperation agreements across trade, technology, energy, and media — a sweeping reaffirmation of the Sino-Russian partnership that carries pointed implications for India's own diplomatic calculus ahead of the BRICS summit it will host in September.

The meeting, Putin's 25th visit to China, took place at the Great Hall of the People with full ceremonial honours: a 21-gun salute, a PLA guard of honour review, and the kind of choreographed warmth that both leaders have perfected over years of strategic alignment. "My dear friend," Putin said upon greeting Xi. "We keep in constant touch, both personally and through our aides." Xi addressed Putin as "my longtime friend" and declared that bilateral relations had reached "the highest level in history."

## The Substance Behind the Spectacle

Beyond the optics, the summit produced concrete outcomes. Russia's oil exports to China grew 35% in the first quarter of 2026, and bilateral trade between the two countries reached approximately $228 billion in 2025. Xi identified energy trade as a "stabilising pillar" of the relationship and pledged accelerated cooperation in artificial intelligence, the digital economy, and technological innovation. The two countries also agreed to renew a friendship treaty originally signed in 2001.

Yet the summit was not without friction. The decade-long negotiations over the Power of Siberia 2 gas pipeline — which would massively expand Russian gas exports to China — produced no visible breakthrough. Reuters reported that while both sides emphasised energy cooperation, China appears content to buy Russian resources at favourable prices without committing to the kind of infrastructure lock-in that Moscow desires.

The leaders issued joint criticism of "unilateralism and hegemonism" — widely understood as a reference to the United States — and warned that "the world faces the danger of reverting to the law of the jungle." Xi called for a "complete cessation of hostilities" in the Middle East, linking regional stability to energy supply chains and international trade order.

## The India Angle: Threading an Impossible Needle

The timing of the summit is what makes it consequential for New Delhi. It came just days after US President Donald Trump concluded his own visit to Beijing — a sequence deliberately designed, analysts say, to project China's ability to maintain strategic partnerships across rival blocs. "The message is clearly one that China maintains friendship and strategic partnership with whichever power it likes, and the USA is just one of them," said Steve Tsang, director of the SOAS China Institute.

India now faces the delicate task of hosting both Putin and Xi at the BRICS summit in New Delhi on September 12-13. The Kremlin has confirmed Putin's attendance, and Prime Minister Narendra Modi has invited Xi directly. A bilateral Xi-Putin meeting on the sidelines is already being planned.

For India, this is diplomatic high-wire work. New Delhi has carefully maintained its relationship with Russia — its largest defence supplier and a critical energy partner — even as it deepens ties with the US through the Quad framework and defence technology agreements. India has also been cautiously normalising relations with China following the Ladakh disengagement, with Modi and Xi meeting on the sidelines of the BRICS summit in Kazan in October 2024.

But the deepening Russia-China axis complicates India's balancing act. As Beijing and Moscow build what analysts describe as a "sanctions-resistant economic ecosystem" — settling trade in yuan and roubles, exploring BRICS-aligned monetary instruments — India must decide how far to integrate into these alternative financial structures without jeopardising its access to Western capital markets, technology, and strategic partnerships.

## What the Diaspora Should Watch

For the Indian diaspora, the geopolitical triangulation has real-world consequences. Defence procurement decisions affect the security environment back home. Energy cooperation with Russia influences the fuel prices that shape India's economy. And the diplomatic positioning India adopts — between the Russia-China bloc and the US-led order — shapes how Indian Americans, British Indians, and NRIs across the Gulf are perceived in their adopted countries' political discourse.

The BRICS summit in September will be the next inflection point. India, as the chair, has chosen the theme "Building for Resilience, Innovation, Cooperation and Sustainability." Whether it can host Putin and Xi while maintaining credibility with Washington will test New Delhi's diplomatic skill — and the world will be watching.""",
    },
    {
        "topic_id": "a21a0e0f-aeba-493f-9980-17da71c0729a",
        "headline": "Southwest Airlines Lands in Hyderabad: America's Largest Domestic Carrier Bets Big on India's Tech Talent",
        "subheadline": "The airline's first innovation centre outside the US will scale to 1,000 engineers in Hyderabad, joining a GCC wave that is quietly transforming India's technology landscape",
        "category": "markets-finance",
        "vertical": "business",
        "urgency": "daily",
        "slug": "southwest-airlines-hyderabad-gcc-innovation-centre-20260520",
        "tags": ["Southwest Airlines", "Hyderabad", "GCC", "global capability center", "AI", "India tech jobs", "Telangana", "aviation technology"],
        "diaspora_angle": "The GCC boom represents a structural shift in how American companies engage with Indian talent — increasingly for high-value engineering and AI work rather than back-office support. For NRIs considering return moves, these centres offer Silicon Valley-calibre work without leaving India.",
        "sources": [
            {"url": "https://www.thehindubusinessline.com/economy/logistics/southwest-airlines-to-expand-india-global-centre-to-1000-employees/article69601234.ece", "name": "The Hindu Business Line"},
            {"url": "https://www.reuters.com/business/aerospace-defense/southwest-airlines-expand-india-global-centre-1000-employees-2026-05-20/", "name": "Reuters"},
            {"url": "https://devdiscourse.com/article/technology/3363289-southwest-airlines-opens-gic-in-hyderabad", "name": "Devdiscourse"},
            {"url": "https://expresscomputer.in/news/southwest-airlines-launches-first-ever-global-innovation-centre-outside-the-u-s-in-hyderabad/122671/", "name": "Express Computer"}
        ],
        "body": """Southwest Airlines, the largest domestic carrier in the United States, has inaugurated its first Global Innovation Centre outside American soil — and it has chosen Hyderabad. The facility, which opened this week with an initial capacity for 200 employees, is planned to scale to over 1,000 engineers and technology professionals in the coming years, focusing on artificial intelligence, machine learning, cybersecurity, data analytics, and aviation technology systems.

The centre was inaugurated by Telangana's IT and Industries Minister Duddilla Sridhar Babu, alongside Laura Williams, the US Consul General in Hyderabad. It will operate through Southwest's India entity and plug directly into the airline's global operations network — not as a back-office support hub, but as what the company describes as a core node for engineering, analytics, and business function innovation.

"AI is currently driving hiring demand in India's GCC sector rather than replacing jobs," said a Southwest executive, adding that the next wave of roles would emphasise data science and machine learning skills. The company has leased approximately 20,000 square feet in Hyderabad and is prioritising what it calls "the right pragmatic scale" of expansion.

## Hyderabad's GCC Moment

Southwest's arrival is not an isolated event. It is the latest — and in some ways the most symbolic — addition to a Global Capability Centre (GCC) boom that has transformed Hyderabad into one of the world's most important technology talent hubs. The city now hosts GCCs for companies spanning finance, healthcare, retail, and increasingly, transportation and logistics.

What makes this moment distinctive is the nature of the work. A decade ago, the typical American company's India operation handled customer support, data entry, and basic IT maintenance. Today, Hyderabad's GCCs are running core product engineering, building AI models, managing cybersecurity operations, and developing the software that directly powers their parent companies' competitive advantages. Southwest is explicitly positioning its Hyderabad facility in this latter category.

The Telangana government has played an aggressive role in attracting these investments, offering a combination of fiscal incentives, streamlined regulatory approvals, and Grade-A commercial real estate in technology corridors like Gachibowli and HITEC City. Institutions like Sattva Knowledge City are purpose-built to host the kind of large-scale engineering operations that companies like Southwest require.

## The Aviation Technology Angle

Southwest's choice of Hyderabad also reflects a broader trend in aviation. Airlines globally are investing heavily in technology to improve operational efficiency, enhance customer experience, and navigate the complexities of modern air travel — from dynamic pricing algorithms to predictive maintenance systems that use machine learning to anticipate equipment failures before they cause delays.

India's aviation sector is itself booming. IndiGo, Air India, and Akasa Air are collectively ordering hundreds of new aircraft, and India is projected to become the world's third-largest aviation market by 2030. Having a deep bench of aviation-focused technology talent in Hyderabad positions Southwest to benefit from this ecosystem — and creates opportunities for knowledge transfer that could benefit Indian carriers as well.

## What This Means for Indian Tech Workers and the Diaspora

For India's technology workforce, the Southwest centre represents the kind of high-value, innovation-oriented work that has traditionally required relocation to the United States. Engineers in Hyderabad will now be working on the same AI and data science problems as their counterparts in Dallas — at competitive Indian compensation, without the visa uncertainties and cultural dislocation that define the H-1B experience.

For NRIs considering a return to India, the GCC boom is reshaping the calculus. The question is no longer whether meaningful, cutting-edge technology work exists in India — it clearly does. The question is whether the compensation, career trajectory, and quality of life in cities like Hyderabad can match what the US offers. With each new GCC announcement, the answer tilts a little further toward India.

Southwest's Hyderabad bet is also a statement about where America's corporate establishment sees global talent heading. When a company synonymous with domestic US air travel — one that has never operated an international route — decides that its first overseas technology investment should be in India, it tells you something about the depth of the talent pool and the maturity of the ecosystem. For Hyderabad, it is another confirmation that the city's technology ambitions are no longer aspirational. They are being underwritten by some of the world's largest companies, one GCC at a time.""",
    }
]

# Insert articles
for art in articles:
    wc = len(art["body"].split())
    payload = {
        "topic_id": art["topic_id"],
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "body": art["body"],
        "category": art["category"],
        "vertical": art["vertical"],
        "urgency": art["urgency"],
        "slug": art["slug"],
        "tags": art["tags"],
        "sources": art["sources"],
        "diaspora_angle": art["diaspora_angle"],
        "score_total": 80,
        "status": "published",
        "published_at": NOW,
        "word_count": wc,
    }
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload
    )
    
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id", "?")
        print(f"✓ Published: {art['slug']} (id={art_id}, {wc} words)")
    else:
        print(f"✗ FAILED: {art['slug']} — {r.status_code}: {r.text}")

# Mark topics as published
topic_ids = [art["topic_id"] for art in articles]
for tid in topic_ids:
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_topics?id=eq.{tid}",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json={"status": "published", "updated_at": NOW}
    )
    if r.status_code in (200, 204):
        print(f"  → Topic {tid[:8]} marked published")
    else:
        print(f"  → Topic {tid[:8]} update failed: {r.status_code}")

# Reject topics we couldn't source well
reject_ids = [
    "ecd252ae-b3b0-4711-8026-4bc9f4e1567d",  # Bhangra - no sources found
    "6a1d8630-6335-4818-a56e-a8d59971dbfe",  # West Asia Container Freight - overlaps with container indictment
]
for rid in reject_ids:
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_topics?id=eq.{rid}",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json={"status": "rejected", "updated_at": NOW}
    )
    if r.status_code in (200, 204):
        print(f"  → Topic {rid[:8]} rejected")

print("\nDone!")
