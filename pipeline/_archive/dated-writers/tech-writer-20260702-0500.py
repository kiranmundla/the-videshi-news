#!/usr/bin/env python3
"""Videshi Technology Writer - 2026-07-02 05:00 PDT"""

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
    return slug[:70].rstrip('-') + "-20260702"

articles = [
    # ─────────────────────────────────────────────────────────
    # ARTICLE 1: Skyroot Aerospace Vikram-1 Launch
    # Beat: Indian Tech Ecosystem / Space Tech
    # ─────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "India's First Private Rocket Is Headed to the Launchpad. The Window Opens July 12.",
        "subheadline": "Skyroot Aerospace, founded by two ex-ISRO engineers and now valued at $1.1 billion, will attempt to put a satellite in orbit from Sriharikota — a milestone no Indian private company has reached.",
        "slug": make_slug("skyroot-vikram-1-private-rocket-launch-india-space"),
        "category": "technology",
        "vertical": "space-tech",
        "diaspora_angle": "NRI investors and Indian-American tech leaders like Alphabet board member Ram Shriram are backing India's private space race, which aims to build a $44 billion economy by 2033.",
        "tags": ["space-tech", "skyroot", "isro", "startup", "indian-tech"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/space/indias-skyroot-aerospace-readies-countrys-first-private-orbital-rocket-launch-2026-07-02/"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/05/07/indias-first-space-tech-unicorn-emerges-as-skyroot-gears-up-for-orbital-launch/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/companies/skyroot-aerospace-becomes-unicorn-after-60-million-funding-ahead-of-vikram-1-launch/article69542340.ece"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/90/Vikram-S_rocket%27s_Mission_Prarambh_04.webp",
        "image_caption": "Skyroot's Vikram-S rocket launching during Mission Prarambh from Sriharikota in 2022",
        "image_attribution": "Wikimedia Commons",
        "body": """Somewhere in the scrublands of Sriharikota, on the same launchpad complex where ISRO has sent missions to the Moon and Mars, a seven-storey rocket built entirely by a private Indian company is being assembled. If all goes to plan, it will lift off between July 12 and August 4.

The rocket is Vikram-1. The company behind it is Skyroot Aerospace. And the mission — dubbed Aagaman, or "arrival" — would make Skyroot the first Indian private firm to place a satellite in orbit.

## Two Engineers, One Bet

Skyroot was founded in 2018 by Pawan Kumar Chandana and Naga Bharath Daka, both former ISRO propulsion engineers who decided that India's space sector needed something it had never had: a credible private launch provider. The model they are chasing is closer to Rocket Lab than to SpaceX — small rockets carrying payloads of up to 350 kilograms to low Earth orbit, built for the booming small-satellite market.

The company proved it could fly hardware in November 2022, when its suborbital demonstrator Vikram-S became the first privately built Indian rocket to launch from an ISRO facility. That test cleared the path for Vikram-1, a far more ambitious four-stage vehicle with solid propulsion on its first three stages and a 3D-printed liquid engine on top for orbital insertion.

In May, Skyroot closed a $60 million round co-led by Singapore's GIC and Sherpalo Ventures, the fund run by Ram Shriram — an Indian-American tech investor who sits on Alphabet's board. The round valued Skyroot at $1.1 billion, making it India's first space-tech unicorn. BlackRock-affiliated funds contributed structured debt.

## Why NRIs Should Watch

The test flight will carry a mix of domestic and international payloads, but its real cargo is a proof of concept for India's private space ambitions. The government has set a target of building a $44 billion space economy by 2033, and it has opened launchpads, spectrum, and regulatory pathways to private companies for the first time.

Skyroot is not alone. Agnikul Cosmos recently signed a deal to launch Finnish radar satellites. Pixxel is building an earth-observation constellation. Industrial groups like Larsen & Toubro and Hindustan Aeronautics are entering rocket manufacturing. But Vikram-1's orbital attempt is the highest-stakes test yet of whether India's startups can compete globally in launch services — a market currently dominated by SpaceX, Rocket Lab, and a handful of Chinese firms.

For diaspora investors and engineers, the signals are hard to ignore. The involvement of GIC and BlackRock points to institutional confidence. Shriram's board seat at Skyroot is the kind of Silicon Valley-to-Hyderabad bridge that rarely existed a decade ago. And if Vikram-1 reaches orbit, the commercial implications — cheaper launch costs, faster turnaround, Indian-built supply chains — ripple well beyond Sriharikota.

## The Risk Is Real

Orbital rocketry has a long history of humbling first attempts. Rocket Lab's first Electron launch in 2017 failed due to a telemetry glitch. Firefly Aerospace's Alpha exploded 150 seconds into its debut flight. Reaching orbit on the first try would be exceptional, not expected.

Skyroot has spent years qualifying every subsystem — static-firing the Kalam-100 solid stage, testing 3D-printed cryogenic engines, validating avionics. But flight is flight, and the data from this launch, success or failure, will define the company's trajectory for years.

The window opens July 12. If Vikram-1 clears the pad and delivers its payloads to orbit, India's private space era will have officially begun — and the $44 billion target will look a lot less aspirational."""
    },

    # ─────────────────────────────────────────────────────────
    # ARTICLE 2: India-Japan AI Pact
    # Beat: Global Tech with Diaspora Angle
    # ─────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "India and Japan Just Signed an AI Pact. Their First Target Is a Joint Language Model.",
        "subheadline": "At their 16th annual summit in New Delhi, Modi and Takaichi inked agreements on AI, semiconductors, and critical minerals — positioning both countries to reduce their dependence on American and Chinese tech stacks.",
        "slug": make_slug("india-japan-ai-pact-modi-takaichi-semiconductor-llm"),
        "category": "technology",
        "vertical": "geopolitics",
        "diaspora_angle": "Indian-origin engineers at Japanese firms and NRI researchers at IITs stand to gain from the AI research partnership, while semiconductor collaboration opens new career and investment pathways beyond Silicon Valley.",
        "tags": ["ai", "india-japan", "semiconductor", "geopolitics", "modi"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/asia-pacific/india-japan-sign-pacts-ai-metals-energy-after-modi-takaichi-talks-2026-07-02/"},
            {"name": "Kyodo News", "url": "https://nordot.app/"},
            {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/india-japan-set-to-expand-ai-and-semiconductor-partnership/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Official_portrait_of_Sanae_Takaichi%2C_Prime_Minister_of_Japan_%28HD%29.jpg/330px-Official_portrait_of_Sanae_Takaichi%2C_Prime_Minister_of_Japan_%28HD%29.jpg",
        "image_caption": "Japanese Prime Minister Sanae Takaichi, who visited New Delhi for the 16th India-Japan annual summit",
        "image_attribution": "Wikimedia Commons",
        "body": """India and Japan signed roughly ten agreements on Thursday covering artificial intelligence, semiconductors, critical minerals, and defence co-development — the most technology-heavy outcome from their annual summit in years. The centrepiece is a joint statement on AI cooperation that commits both countries to building large language models together, an initiative that would link Japan's Preferred Networks and National Institute of Informatics with India's IIT network.

"The convergence of Japan's precision technology and India's software capabilities will give a new momentum and strength to global AI development," Prime Minister Narendra Modi said after talks with his Japanese counterpart, Sanae Takaichi, at Hyderabad House in New Delhi.

## More Than a Photo Op

On paper, India-Japan summits have been annual rituals since 2006. In practice, this one carried sharper urgency. The United States has turned inward with escalating tariffs and "America First" technology restrictions. China is weaponising rare earth exports and expanding its AI footprint across Asia. Both India and Japan are looking for partners they can actually depend on — and finding each other.

The AI pact is the most concrete signal. According to Kyodo News, the agreement elevates the bilateral AI relationship to "strategic R&D partners" — a level Japan has previously reserved for the US and EU. Preferred Networks, one of Japan's most advanced AI companies, will collaborate with IIT researchers on developing LLMs capable of handling India's linguistically diverse market, where demand for multilingual models far outstrips what OpenAI or Anthropic currently offer.

The semiconductor dimension is equally significant. Japan hosts critical chipmaking equipment manufacturers — Tokyo Electron, Screen Holdings, Disco Corporation — whose tools are essential for the fabs India is now building. Takaichi's visit is expected to accelerate the flow of Japanese equipment and expertise into India's semiconductor mission, which has already approved foundries by Tata Electronics in Dholera and assembly plants by Micron in Gujarat.

## The Numbers Behind the Handshake

Bilateral trade between India and Japan hit $27.5 billion in the fiscal year ending March 2026. Japanese investment in India totalled $3.2 billion between April and December 2025. Japan remains one of India's largest infrastructure investors, bankrolling the Mumbai-Ahmedabad bullet train and, more recently, taking a $1.6 billion stake in Yes Bank.

But the tech investment has lagged. India hosts roughly 1,400 Japanese companies, compared with 30,000 in China. The AI and semiconductor agreements are designed to change that ratio — not by matching China's scale, but by creating deep, strategically motivated partnerships in areas where both countries feel exposed.

## What It Means for the Diaspora

For Indian engineers and researchers, the pact opens a second axis of international collaboration that does not run through Silicon Valley. IIT graduates may soon find research fellowships at Japanese AI labs carrying real institutional backing, not just ceremonial MoUs. Indian semiconductor professionals — already in demand for the Tata and Micron fabs — could gain access to Japanese equipment training and process know-how that currently flows almost exclusively through TSMC's ecosystem.

For NRI investors, Japan's deepening commitment to India is a portfolio signal. Japanese institutional money — patient, strategic, and enormous — tends to move in decades, not quarters. When GIC, Shriram, and now Japan's sovereign capital all point in the same direction, the thesis is not speculative anymore.

The harder question is execution. India has signed AI cooperation agreements with the US, the EU, and now Japan. Turning them into working models, trained researchers, and functioning supply chains will take years. But Takaichi's visit, her first to India as prime minister, carried enough substance to suggest this is not just diplomatic choreography. The money and the memoranda both point toward something real."""
    },

    # ─────────────────────────────────────────────────────────
    # ARTICLE 3: India Data Center Boom
    # Beat: Indian Tech Ecosystem / Global Tech
    # ─────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Every Big Tech Company Is Building Data Centres in India. The Tax Break Lasts Until 2047.",
        "subheadline": "Microsoft, Google, Amazon, Meta, and OpenAI have collectively committed over $80 billion to Indian data centre infrastructure. Nomura says capacity will grow tenfold in a decade.",
        "slug": make_slug("india-data-center-boom-microsoft-google-amazon-tax-break"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "NRI engineers at FAANG companies are building the very AI infrastructure being deployed to India, while the data centre boom creates investment, career, and return-to-India opportunities across cloud, networking, and power engineering.",
        "tags": ["data-center", "microsoft", "google", "amazon", "india-tech", "ai-infrastructure"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Barron's", "url": "https://www.barrons.com/articles/ai-data-centers-india-75425e19"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/microsoft-partners-with-singapores-lightstorm-build-india-southeast-asia-undersea-cable-2026-07-02/"},
            {"name": "Barron's (Amazon)", "url": "https://www.barrons.com/articles/amazon-india-data-center-investment-ai-51ff3fd7"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5203849/pexels-photo-5203849.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Server racks with fibre optic cables inside a modern data centre",
        "image_attribution": "Pexels",
        "body": """Here is a list, incomplete, of what American tech companies have promised to build in India in the past eighteen months: Microsoft committed $17.5 billion, its largest-ever investment in Asia. Google pledged $15 billion for three data centre campuses in Visakhapatnam. Amazon raised its total planned investment to $48 billion through 2030, including a fresh $13 billion announced last week for Mumbai and Hyderabad. Meta, OpenAI, and a constellation of smaller cloud providers have added their own pledges on top.

Add it up and the commitments exceed $80 billion. The question for anyone tracking India's tech economy — including the hundreds of thousands of Indian engineers who helped build these companies — is whether the money is serious or ceremonial.

## Why Now, Why India

The short answer is physics. Data centres need to be close to their users to reduce latency. Indians are now the second-largest users of ChatGPT and Claude globally, after Americans. Every AI query, every cloud workload, every streamed video benefits from being processed closer to the person making the request.

The longer answer is policy. In February, India declared zero taxes until 2047 on overseas services delivered by foreign companies operating data centres in the country. Land is cheaper. Approvals come without the public hearings that have slowed or killed data centre projects across the American heartland. The government is not just welcoming hyperscalers — it is actively removing friction.

Nomura projects India's data centre capacity will grow tenfold over the next decade. Synergy Research Group's chief analyst John Dinsdale estimates India will rise from 1.3 per cent of global capacity to 3 per cent. "That may not sound like a big shift," Dinsdale told Barron's, "but these are percentages of enormous numbers."

Macquarie Equity Research puts the near-term trajectory at a doubling of operational capacity from the current 1.4 gigawatts by 2027, with a potential five-fold increase by 2030 if planned projects are fast-tracked.

## The Infrastructure Stack

The data centres themselves are only one layer. Microsoft is simultaneously building a 3,600-kilometre undersea cable from India to Singapore with Tata Communications, announced this week. Google is laying its own submarine routes. Amazon Web Services has expanded its Indian footprint to three availability zones, with more planned. The entire fibre, power, and cooling ecosystem around these facilities is creating a secondary boom in construction, electrical engineering, and networking.

Andhra Pradesh's Visakhapatnam — where both Google and Meta have announced campuses — is emerging as a data centre corridor alongside Mumbai and Hyderabad. The landing station for the Microsoft-Tata cable is in Machilipatnam, also in Andhra Pradesh, turning the state's coastline into a digital infrastructure hub.

## What NRIs Should Be Watching

The most immediate implication is career opportunity. Every hyperscale data centre needs hundreds of engineers — cloud architects, network designers, cooling specialists, power engineers, security professionals. The companies building in India are the same ones that employ the largest share of H-1B workers in the United States. For Indian engineers weighing a return to India or a dual-location career, the data centre boom is creating roles that did not exist five years ago.

For investors, the infrastructure buildout is creating an entire ecosystem of investable companies — from Tata Communications and Lightstorm (planning a mid-2027 IPO at a projected $1.5 billion valuation) to power companies, real estate developers, and cooling-technology firms feeding the construction wave.

The strategic subtext is harder to miss. India is positioning itself not just as a consumer of cloud services but as a physical node in the global AI infrastructure. When the world's five largest technology companies all choose the same country as their next major buildout site, the signal is not ambiguous. The bet is on India — and the tax break lasts another twenty-one years."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
