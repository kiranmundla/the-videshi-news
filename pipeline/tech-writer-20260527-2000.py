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

# Verify images
def verify_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET for servers that don't support HEAD well
        r2 = requests.get(url, timeout=10, stream=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct2 = r2.headers.get("Content-Type", "")
        cl2 = int(r2.headers.get("Content-Length", 0))
        return r2.status_code == 200 and "image" in ct2 and cl2 > 5000
    except:
        return False

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Nikesh Arora Added 959 Jobs While Big Tech Cut 80,000. Here's His Playbook.",
        "subheadline": "The Indian-origin CEO of Palo Alto Networks is betting that AI means more cybersecurity workers, not fewer — and a $25 billion acquisition to prove it.",
        "slug": make_slug("nikesh-arora-palo-alto-hiring-cyberark-ai"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian-origin CEO leading the largest cybersecurity company's expansion while peers slash workforces — a counternarrative for Indian tech professionals worried about AI displacement and H-1B vulnerability.",
        "tags": ["cybersecurity", "indian-ceo", "palo-alto-networks", "nikesh-arora", "ai-jobs"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "NewsPoint / Times of India", "url": "https://www.newspointapp.com/english/tech/palo-networks-ceo-nikesh-arora-it-is-mistake-to-believe-that-ai-productivity-gains-automatically-means-fewer-employees-in-fact-for-engineers-toi/articleshow/14504820ccc6e66d2e878e3c5418e54452dffc95"},
            {"name": "Calcalist Tech", "url": "https://www.calcalistech.com/ctechnews/article/sjdjs6wpxg"},
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NASDAQ/PANW/earnings/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
        "body": """The first half of 2026 has been defined by a single, grim statistic: more than 80,000 tech workers lost their jobs in Q1 alone. Companies blamed AI. They blamed "efficiency." They blamed the post-pandemic hangover. The result was the same — pink slips, 60-day visa clocks, and frantic LinkedIn updates.

Nikesh Arora went the other way.

## The Contrarian Bet

The CEO of Palo Alto Networks — the $206 billion cybersecurity giant headquartered in Santa Clara — added 959 employees in the first two quarters of fiscal 2026. Not despite AI, but because of it.

"The fallacy is that organizations are going to get 30, 40, 50, 60 percent more productive, so we need less people," Arora told the New York Times' Hard Fork podcast. "No, I need more."

His argument is straightforward: AI makes individual engineers faster. But faster engineers don't eliminate work — they expose the backlog. "Most technologists have a feature request list longer than their arm," Arora said. AI lets companies tackle projects that have been deferred for years, which means new hires with new skill sets, not layoffs.

It's a position that puts him directly at odds with Block's Jack Dorsey, Cisco's Chuck Robbins, and the growing chorus of CEOs using AI as cover for headcount reduction.

## The $25 Billion Identity Play

Arora isn't just talking. In February, Palo Alto completed its largest acquisition ever — the $25 billion purchase of Israeli cybersecurity firm CyberArk. The deal, which valued CyberArk at $45 per share in a cash-and-stock transaction, gives Palo Alto a dominant position in identity security, the discipline of controlling who (and what) can access enterprise systems.

The timing is deliberate. As companies deploy autonomous AI agents — code-writing bots, data-processing workflows, agentic assistants that operate without human oversight — the attack surface has exploded. Every agent needs permissions. Every permission is a potential breach.

"All these agents are going to need permissions and access," Arora told analysts. "We need to manage these agents just the way you manage identities for machines or humans."

CyberArk's speciality in privileged access management, bolstered by its own $1.5 billion acquisition of certificate authority Venafi, positions Palo Alto to secure the AI infrastructure layer — not just the networks and endpoints it already dominates.

## The Numbers Behind the Swagger

Palo Alto's Q1 2026 results justify the confidence. Revenue hit $2.5 billion, up 16 percent year-over-year. Next-Generation Security ARR — the metric Wall Street watches — surged 29 percent to $5.9 billion. The company's Q3 earnings report is due June 2, and analysts expect continued acceleration.

The stock, trading near $248 after a 3.2 percent dip on Wednesday, has recovered sharply from its 52-week low of $139, reflecting investor belief in Arora's platform consolidation strategy.

## What This Means for Indian Tech Workers

For the tens of thousands of Indian professionals in American cybersecurity — from SOC analysts in Dallas to cloud security architects in the Bay Area — Arora's stance carries particular weight. When the CEO of a $206 billion company says AI creates jobs rather than destroying them, it's not just corporate spin. It's a hiring signal.

Palo Alto's Q3 earnings call on June 2 will reveal whether the hiring pace held through spring. If it did, Arora won't just have a contrarian opinion. He'll have the receipts.

And in a year when 80,000 tech workers learned their jobs were expendable, receipts matter more than rhetoric."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Approved $18.2 Billion in Chip Projects. The Real Test Is Execution.",
        "subheadline": "Ten semiconductor projects, a landmark ASML deal, and an ambition to become the world's 'China Plus One' — but India's fab dream has a long history of false starts.",
        "slug": make_slug("india-18-billion-semiconductor-tata-asml-fab"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "NRI semiconductor engineers and investors are watching India's $18.2B chip push closely — it could create a viable return-to-India career path in chip design and fabrication, while offering investment exposure to India's hardware manufacturing pivot.",
        "tags": ["semiconductor", "india", "tata-electronics", "asml", "micron", "chips"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CryptoRank / Tech Coverage", "url": "https://cryptorank.io/news/india-approved-18-billion-semiconductor-projects"},
            {"name": "IndMoney", "url": "https://www.indmoney.com/articles/stocks/asml-tata-electronics-semiconductor-fab"},
            {"name": "Financial Content / Boston Herald", "url": "https://markets.financialcontent.com/bostonherald/article/marketersmedia-2025-6-18-indias-silicon-leap-10-major-semiconductor-projects-approved-in-massive-18-billion-strategic-push"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5554948/pexels-photo-5554948.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """India has approved $18.2 billion across ten semiconductor projects under the India Semiconductor Mission. The ambition is enormous: build an end-to-end chip ecosystem — from front-end fabrication to testing and packaging — and position the country as the world's credible alternative to Chinese manufacturing. Whether this time is different depends on whether India can solve the problems that have defeated every previous attempt.

## The Centrepiece: Tata's 300mm Fab

The flagship project is Tata Electronics' 300-millimetre fabrication facility in Dholera, Gujarat — India's first front-end fab. The $11 billion plant, built in partnership with Dutch lithography giant ASML, will produce chips at the 28nm to 110nm process nodes. These aren't cutting-edge by TSMC standards (the Taiwanese foundry is ramping 2nm), but they serve the vast majority of the world's chip demand: automotive controllers, power management ICs, industrial sensors, and the unglamorous silicon that keeps modern infrastructure running.

ASML will supply its deep ultraviolet (DUV) lithography systems — the same tools that produce roughly 80 percent of global chip output. For ASML, it's a hedge against geopolitical risk in East Asia. For India, it's a foundational technology transfer that no previous government initiative managed to secure.

## Beyond Tata: The Supporting Cast

The remaining nine projects span the semiconductor value chain. Micron's Gujarat assembly and test facility — the American memory giant's first in India — is already under construction, backed by CEO Sanjay Mehrotra's personal conviction about India's potential. CG Power and Japan's Renesas are building a $1 billion analog and mixed-signal plant, also in Gujarat. Multiple advanced packaging and testing units round out the portfolio.

Together, the ten projects are expected to create over 20,000 direct jobs and catalyse a much larger ecosystem of suppliers, design houses, and equipment vendors.

## The NRI Calculus

For the estimated 300,000 Indian-origin professionals working in the global semiconductor industry — from process engineers at Intel's Oregon fabs to design architects at Qualcomm San Diego — India's chip push reshapes the career equation.

Until now, "returning to India" in semiconductors meant joining an IT services firm or a design centre doing verification work for foreign chipmakers. A functioning 300mm fab changes the calculus. It creates roles in process engineering, yield management, equipment maintenance, and fab operations — the hands-on, high-paying jobs that have historically existed only in Taiwan, South Korea, and the United States.

The diaspora advantage cuts both ways. India needs the expertise its engineers accumulated abroad. But those engineers need assurance that India's fabs will actually reach volume production — a milestone that has eluded every previous Indian semiconductor initiative, from the ill-fated 2007 SemIndia project to the stalled ISMC consortium.

## The 'China Plus One' Thesis

The geopolitical backdrop is favourable. The U.S. CHIPS Act has accelerated the "China Plus One" strategy, pushing global manufacturers to diversify supply chains away from East Asia. India — with its English-speaking workforce, democratic governance, and growing domestic electronics market — is the obvious beneficiary.

But "obvious" and "inevitable" are different things. Vietnam, Malaysia, and even Saudi Arabia are competing for the same investment. India's advantages in talent and scale are offset by persistent challenges: unreliable power grids, complex land acquisition, water scarcity in Gujarat's industrial zones, and a regulatory environment that can shift between state and central governments.

## The Execution Gap

The money is committed. The partnerships are signed. What remains is the hardest part: building and operating semiconductor facilities at global quality standards, on schedule, in a country where major infrastructure projects routinely overshoot timelines by years.

India's semiconductor moment is real. Whether it becomes India's semiconductor decade depends on execution — and execution, unlike ambition, cannot be legislated into existence."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Skyroot Is India's First Space-Tech Unicorn. Now It Has to Actually Reach Orbit.",
        "subheadline": "Founded by two ISRO engineers who left government jobs, Skyroot Aerospace has raised over $95 million and is preparing Vikram-1 for India's first private orbital launch.",
        "slug": make_slug("skyroot-aerospace-unicorn-vikram-orbit-india"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian diaspora investors and space enthusiasts are watching Skyroot's orbital attempt as a litmus test for India's private space sector — a potential new asset class and career path for NRI aerospace engineers.",
        "tags": ["space-tech", "skyroot", "india", "isro", "startups", "unicorn"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Skyroot_Aerospace"},
            {"name": "Inc42", "url": "https://www.inc42.com/features/capital-with-conditions-indian-spacetech-startups-expected-to-break-new-grounds-in-2026/"},
            {"name": "Business Outreach", "url": "https://www.businessoutreach.in/skyroot-aerospace-success-story/"},
            {"name": "Inc42", "url": "https://inc42.com/features/india-must-build-space-tech-companies-the-way-nasa-built-spacex/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/586061/pexels-photo-586061.png?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """In November 2022, a slender rocket named Vikram-S lifted off from Sriharikota and reached an altitude of 89.5 kilometres. It stayed aloft for about five minutes, carried no payload of commercial value, and splashed into the Bay of Bengal. It was, by any orbital standard, trivial.

It was also the most consequential Indian rocket launch in years — because it wasn't built by ISRO.

Skyroot Aerospace, the Hyderabad-based startup behind Vikram-S, has since raised over $95 million, achieved a valuation exceeding $1 billion, and become India's first space-tech unicorn. The company is now preparing Vikram-1, a four-stage solid-fuel rocket, for India's first private orbital launch. If it succeeds, Skyroot won't just validate a company. It will validate an entire thesis about India's private space economy.

## From Government Labs to Garage (Almost)

Skyroot was founded in 2018 by Pawan Kumar Chandana and Naga Bharath Daka, both former ISRO scientists who left stable government positions to build rockets commercially. The timing was deliberate: India had just begun liberalising its space sector, allowing private companies to access ISRO facilities, launch infrastructure, and — crucially — the institutional knowledge accumulated over six decades of government-led space exploration.

The founders' ISRO pedigree wasn't just credibility. It was an engineering shortcut. Skyroot's propulsion systems, carbon composite structures, and mission planning draw directly on the intellectual capital of India's space programme, adapted for commercial speed and cost discipline.

## The Vikram Family

Skyroot's rocket family — named after Vikram Sarabhai, the father of India's space programme — is designed for the small-satellite market, the fastest-growing segment of the launch industry. Vikram-1, the company's orbital vehicle, can carry up to 480 kilograms to low Earth orbit. Vikram-2, still in development, targets the heavier end of the small-sat market.

The commercial thesis is straightforward. As constellations of small satellites proliferate — for communications, Earth observation, IoT connectivity, and defence — demand for dedicated small-satellite launchers is outstripping supply. Rocket Lab's Electron has proven the model works. Skyroot wants to be the Indian alternative: lower cost, competitive reliability, and access to ISRO's Sriharikota launch complex.

## The Ecosystem Effect

Skyroot isn't alone. India now has over 400 space-tech startups, up from fewer than 50 in 2019. Agnikul Cosmos, also founded by IIT alumni, has tested the world's first single-piece 3D-printed semi-cryogenic rocket engine. Pixxel is building a constellation of hyperspectral imaging satellites. Dhruva Space is developing satellite deployment systems. ISRO's Gaganyaan programme — India's first human spaceflight mission — has its uncrewed test flight slated for 2026.

The government's IN-SPACe regulatory body has cleared dozens of private missions, and Prime Minister Modi's Space Vision 2047 has set ambitious targets for deep-space exploration and commercial launch volume. But the ecosystem's credibility ultimately hinges on one thing: getting a private Indian rocket to orbit.

## The NRI Opportunity

For Indian-origin aerospace engineers — at SpaceX, Blue Origin, Rocket Lab, Northrop Grumman, and NASA's Jet Propulsion Laboratory — Skyroot's progress creates a career path that didn't exist five years ago. The company has been actively recruiting from the diaspora, and its unicorn valuation has attracted attention from NRI angel investors and family offices looking for exposure to India's deep-tech sector.

The broader investment thesis is compelling. India's space economy is projected to reach $44 billion by 2033, growing at roughly 8 percent annually. Private capital, which barely existed in Indian space before 2020, now accounts for a significant share of sector funding. Skyroot's $60 million Series C — which pushed it past the unicorn threshold — was oversubscribed.

## What Comes Next

Vikram-1's maiden orbital launch, targeted for later this year, will be the most watched Indian space event since Chandrayaan-3's lunar landing. If the rocket reaches orbit, Skyroot will join an exclusive club: fewer than a dozen private companies worldwide have achieved orbital insertion. If it doesn't, the failure will be instructive but survivable — SpaceX's first three Falcon 1 launches failed before the fourth succeeded.

Either way, the trajectory is clear. India's private space sector is no longer a policy aspiration. It's a funded, staffed, and technically capable industry approaching its first orbital proof point. For the diaspora, that's not just news. It's an invitation."""
    },
]

# Verify images before publishing
for art in articles:
    img_ok = verify_image(art["image_url"])
    print(f"Image check for '{art['headline'][:50]}...': {'✅ OK' if img_ok else '⚠️ FAILED'}")

print()

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
