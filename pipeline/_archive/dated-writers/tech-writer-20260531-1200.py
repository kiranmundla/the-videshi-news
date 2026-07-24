#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-31 12:00 UTC batch"""

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


# ─────────────────────────────────────────────────────────
# ARTICLE 1: Tata Electronics + ASML Dholera Fab
# ─────────────────────────────────────────────────────────

art1_body = """India's semiconductor ambitions took a tangible step forward this week when Tata Electronics signed a memorandum of understanding with ASML, the Dutch company that holds a near-monopoly on the lithography systems without which no modern chip can be manufactured. The deal, inked during Prime Minister Narendra Modi's state visit to the Netherlands, will bring ASML's advanced lithography platforms to Tata's upcoming 300mm fabrication plant in Dholera, Gujarat — India's first commercial semiconductor fab.

The Dholera facility, developed in partnership with Taiwan's Powerchip Semiconductor Manufacturing Corporation (PSMC), represents an investment of approximately ₹91,000 crore (roughly $11 billion). When operational, it will manufacture chips at 28nm, 50nm, and 55nm process nodes — mature geometries, but ones that power everything from automotive electronics and industrial controllers to power management ICs and display drivers. Planned capacity stands at 50,000 wafers per month.

## Why ASML Matters More Than the Headlines Suggest

ASML is not just another equipment vendor. The company's extreme ultraviolet (EUV) lithography systems are the irreplaceable bottleneck in advanced chipmaking — no ASML machines, no leading-edge chips. While Dholera will use ASML's deep ultraviolet (DUV) platforms rather than EUV (the 28nm node doesn't require it), the partnership signals something more important: ASML is willing to invest in India's semiconductor ecosystem at the ground floor. The MoU extends beyond hardware sales to include workforce training, research collaboration, and development of local supply chain capabilities.

For context, building a semiconductor fab is one of the most technically demanding industrial projects on earth. Taiwan spent three decades perfecting its ecosystem. India is attempting to compress that timeline dramatically, and having ASML as a committed partner rather than merely a transactional vendor changes the calculus.

## The Diaspora Dimension

For the estimated 300,000 Indian-origin engineers working in the global semiconductor industry — at Intel, Qualcomm, TSMC, Samsung, and AMD — the Dholera fab represents something unprecedented: a potential career path that doesn't require choosing between technical ambition and proximity to home.

Tata Electronics CEO Randhir Thakur has said the facility will need approximately 300 distinct suppliers in its vicinity and will generate over 20,000 direct and indirect skilled jobs. The India Semiconductor Mission 2.0, outlined in the Union Budget 2026 with a ₹1,000 crore allocation, has broadened its focus from fab-centric subsidies to the entire value chain — equipment, materials, Indian IP, and supply-chain resilience.

For NRI investors watching India's manufacturing push, the ASML partnership provides a credibility signal that pure government announcements cannot. ASML doesn't sign MoUs for facilities it expects to fail. The company's due diligence on fab viability is arguably more rigorous than any government assessment.

The first chips from Dholera are expected by late 2027. Whether they arrive on schedule will determine if India's semiconductor story moves from PowerPoint to production."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "ASML Is Bringing Its Chip-Making Machines to India. Tata's Dholera Fab Just Got Real.",
    "subheadline": "The Dutch lithography giant signed an MoU with Tata Electronics during Modi's Netherlands visit, committing equipment, training, and supply chain support to India's first commercial semiconductor fab.",
    "slug": make_slug("asml-tata-electronics-dholera-fab-semiconductor-india"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "The ASML-Tata deal creates a credible career path for 300,000+ Indian-origin semiconductor engineers globally and signals institutional confidence in India's chip manufacturing ambitions — relevant to NRI investors and professionals weighing return-to-India decisions.",
    "tags": ["semiconductor", "tata-electronics", "asml", "dholera", "india-semiconductor-mission", "manufacturing"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Europe Says", "url": "https://europesays.com/1882791/asml-and-tata-electronics-sign-mou-to-support-indias-first-commercial-semiconductor-fab-netherlands/"},
        {"name": "DIGITIMES", "url": "https://www.digitimes.com/news/a20260516PD218.html"},
        {"name": "NexNews", "url": "https://nexnews.org/indias-expanding-semiconductor-ecosystem-and-manufacturing-push/"},
        {"name": "Forbes India", "url": "https://www.forbesindia.com/article/take-one-big-story-of-the-day/tata-group-aims-to-make-gujarats-dholera-the-global-epicentre-of-semiconductor-excellence-tata-electronics-ceo-randhir-thakur/93053/1"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6755081/pexels-photo-6755081.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "body": art1_body
}


# ─────────────────────────────────────────────────────────
# ARTICLE 2: Nikesh Arora / Palo Alto Networks
# ─────────────────────────────────────────────────────────

art2_body = """Nikesh Arora has had a very good year. The stock of Palo Alto Networks, the cybersecurity giant he has led since 2018, has surged more than 50 per cent in 2026, touching record highs above $283 and pushing the company's market capitalisation past $229 billion. The former Google and SoftBank executive — who grew up in Ghaziabad and studied at IIT Varanasi before heading to Northeastern University and Boston College — now presides over what many analysts consider the most strategically positioned cybersecurity company in the world.

When the company reports its fiscal third-quarter earnings on June 2, Wall Street expects revenue of $2.94 billion, up 29 per cent year-over-year. Arora himself put $10 million of his own money into PANW shares in March, buying 68,085 shares at $146.87 — a signal that even he considered the stock undervalued at the time. It has nearly doubled since.

## The AI Security Thesis

Palo Alto's rally isn't merely a rising-tide-lifts-all-boats story. The company has spent three years executing what Arora calls "platformisation" — consolidating dozens of point security products into a unified platform that covers network security, cloud security, and security operations. The strategy initially spooked investors when Arora offered free trials to lure customers onto the platform, but the bet is paying off.

The company's XSIAM product — an AI-driven security operations platform — and its SASE (Secure Access Service Edge) offerings have been the primary growth engines. UBS analysts noted this week that sentiment across the cybersecurity sector has "significantly improved," with Palo Alto Networks as the primary beneficiary.

More importantly, as enterprises pour billions into AI infrastructure, they're discovering that AI systems create entirely new attack surfaces. AI models can be poisoned, prompt-injected, and manipulated in ways traditional security tools were never designed to handle. Palo Alto's early investments in AI-native security have positioned it to capture this emerging market.

## The Indian Connection Runs Deep

Arora's trajectory — IIT to global tech executive to cybersecurity CEO — is a template recognisable to thousands of Indian engineers in Silicon Valley. But what makes his current position unusual is the scale of the empire he controls. At $229 billion, Palo Alto Networks is worth more than most Indian IT companies combined.

The cybersecurity sector is also one of the fastest-growing employers of Indian talent in the United States. With an estimated 40,000 Indian-origin professionals working in cybersecurity roles across American companies, Palo Alto's expansion has direct H-1B and green card implications. The company has been hiring aggressively, in contrast to the layoff-heavy trend across broader tech.

For NRI investors, PANW has been one of the standout performers in 2026, outpacing the Nasdaq's already strong rally. The question heading into Tuesday's earnings is whether the stock's premium valuation — trading well above analysts' mean price target of $212 — can be sustained. Eleven of 14 analysts rate it a "buy," but the stock has already priced in considerable optimism.

Arora, characteristically, isn't waiting for analysts to catch up. He bought at $147 when the consensus was uncertain. The stock's subsequent run suggests he understood something the market didn't."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Nikesh Arora Bet $10 Million on His Own Company. Palo Alto Networks Stock Has Nearly Doubled Since.",
    "subheadline": "The IIT alumnus who runs America's most valuable cybersecurity firm heads into Tuesday's earnings with a stock up 50 per cent this year and Wall Street scrambling to raise targets.",
    "slug": make_slug("nikesh-arora-palo-alto-networks-earnings-cybersecurity"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Arora's IIT-to-$229B-company trajectory is a diaspora archetype, and Palo Alto Networks' aggressive hiring contrasts sharply with broader tech layoffs — directly relevant to Indian cybersecurity professionals on H-1B visas and NRI investors tracking the stock's record run.",
    "tags": ["nikesh-arora", "palo-alto-networks", "cybersecurity", "indian-ceo", "earnings", "nri-investors"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Investopedia", "url": "https://www.investopedia.com/heres-how-much-traders-expect-palo-alto-networks-stock-to-move-after-earnings-11737993"},
        {"name": "Seeking Alpha", "url": "https://seekingalpha.com/article/4775207-palo-alto-networks-worth-buying-before-june-2"},
        {"name": "MarketBeat", "url": "https://www.marketbeat.com/instant-alerts/palo-alto-networks-inc-nasdaqpanw-is-bearing-point-capital-llcs-9th-largest-position-2026-05-31/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
    "body": art2_body
}


# ─────────────────────────────────────────────────────────
# ARTICLE 3: India's Space Tech — Chandrayaan-3 Award + Gaganyaan
# ─────────────────────────────────────────────────────────

art3_body = """Three announcements in the span of a single week have thrust India's space programme into sharp global focus. Chandrayaan-3 received the 2026 Goddard Astronautics Award — the highest honour bestowed by the American Institute of Aeronautics and Astronautics — for its historic soft landing near the Moon's south pole. India's Gaganyaan mission entered its final phase, with the crewed launch now confirmed for the first quarter of 2027. And NASA Administrator Bill Nelson, visiting India, declared that the two nations are working to send an Indian astronaut to the International Space Station.

Taken individually, each is noteworthy. Taken together, they represent a structural shift in how the global space establishment views India — not as an emerging player, but as an established one.

## The Goddard Award: More Than a Trophy

The Goddard Astronautics Award, presented at the AIAA ASCEND 2026 conference in Washington on May 21, is named after Robert Goddard, the father of modern rocketry. India's Ambassador to the United States, Vinay Kwatra, accepted on behalf of ISRO.

What makes the award significant beyond ceremony is what Chandrayaan-3 actually accomplished. On August 23, 2023, the Vikram lander touched down near the lunar south pole — a region no spacecraft had previously reached at surface level. The mission confirmed the presence of key chemical elements in lunar south polar soil, data that directly supports planning for future lunar habitation.

For ISRO, which achieved this on a budget of approximately $75 million — less than the production cost of the film *Gravity* — the recognition from America's premier aerospace body is validation of a cost-innovation model that has no parallel in global space exploration.

## Gaganyaan: The Final Countdown

The more consequential development for India's long-term space trajectory is Gaganyaan entering its final phase. Union Minister Dr. Jitendra Singh confirmed that the crewed launch is scheduled for Q1 2027, which would make India the fourth nation to independently send humans to space, after the Soviet Union, the United States, and China.

The programme has completed critical milestones: the TV-D1 test vehicle flight, the Test Vehicle Abort Mission (TVAM), and rigorous astronaut training at Russia's Yuri Gagarin Cosmonaut Training Centre. The four selected astronauts — all Indian Air Force officers — are now in mission-specific preparation at India's astronaut training centre. Key technologies including the human-rated LVM3 launch vehicle, crew escape system, and service modules are in final integration.

## NASA's Open Door

Perhaps the most geopolitically significant signal came from NASA Administrator Nelson, who stated that the US is "open to collaborating with India in building its own space station" and that the two nations are actively planning to send an Indian astronaut to the ISS.

Wing Commander Shubhanshu Shukla, an IAF officer and Gaganyaan astronaut, has already been selected as pilot for the Axiom Mission 4 to the ISS — making him India's second astronaut in space since Rakesh Sharma's 1984 mission. The collaboration positions India squarely within the US-led space architecture, with implications that extend well beyond science into geopolitics and defence.

## What This Means for the Diaspora

India's space ambitions are creating real economic opportunities. The commercial space sector — led by startups like Agnikul Cosmos, Skyroot Aerospace, Pixxel, and Dhruva Space — is growing rapidly, fuelled by reformed FDI policies and ISRO's willingness to share technology. For NRI engineers and investors, particularly those in aerospace and defence, the sector represents a rare intersection of national ambition and commercial opportunity.

Prime Minister Modi's Space Vision 2047 — an Indian space station by 2035, astronauts on the Moon by 2040 — would have sounded aspirational five years ago. After this week, it sounds like a plan."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Space Programme Just Had Its Biggest Week in a Decade. Three Milestones Explain Why.",
    "subheadline": "Chandrayaan-3 won America's highest astronautics honour. Gaganyaan confirmed a crewed launch for 2027. And NASA offered to help India build its own space station.",
    "slug": make_slug("india-space-chandrayaan-goddard-gaganyaan-nasa-iss"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "India's space breakthroughs create aerospace career paths for NRI engineers, commercial investment opportunities in India's growing private space sector, and a source of diaspora pride as India enters the elite club of crewed spaceflight nations.",
    "tags": ["isro", "chandrayaan-3", "gaganyaan", "nasa", "india-space", "space-tech", "goddard-award"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/aiaa-honors-chandrayaan-3-with-goddard-astronautics-award/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/indias-gaganyaan-mission-enters-final-phase-crewed-launch-set-for-early-2027/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/us-and-india-working-towards-sending-an-indian-astronaut-to-the-iss/"},
        {"name": "Wikipedia - 2026 in spaceflight", "url": "https://en.wikipedia.org/wiki/2026_in_spaceflight"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/aa/Chandrayaan-3_%E2%80%93_Image_of_Vikram_lander_on_lunar_surface_taken_by_Pragyan_rover_navcam_at_1104_IST%2C_30_August_2023_from_15_meters_away_%28with_text%29.webp",
    "body": art3_body
}


# ─────────────────────────────────────────────────────────
# PUBLISH ALL
# ─────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles processed.")
