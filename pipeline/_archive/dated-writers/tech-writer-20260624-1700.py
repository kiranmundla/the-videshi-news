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

skyroot_body = """A 23-metre rocket is sitting on a launch pad at Sriharikota, and for the first time the company that built it does not have "Government of India" on its letterhead. Skyroot Aerospace, the Hyderabad startup founded by two former ISRO engineers, is in the final stretch before the maiden orbital flight of Vikram-1 — the first attempt by a private Indian company to design, build and launch its own rocket all the way to orbit.

If it works, India joins a very short list. Only a handful of private firms anywhere — Rocket Lab and Firefly in the United States chief among them — have put their own vehicles into orbit. Skyroot's pitch is the same as theirs: small, dedicated, on-demand launches for the swelling market of satellite operators who do not want to wait years for a slot on someone else's big rocket.

## From a garage idea to the pad

Skyroot was founded in 2018 by Pawan Kumar Chandana and Naga Bharath Daka, both of whom cut their teeth on propulsion at ISRO. In November 2022 the company flew Vikram-S, a suborbital demonstrator, becoming the first private Indian rocket to reach space. Vikram-1 is the serious follow-up: a four-stage vehicle with an all-carbon-composite body, 3D-printed engines, and the ability to loft roughly 300 kilograms into low Earth orbit.

The hardware has been working through its checklist in public. The Kalam-1200 first stage — at 11 metres, the largest solid rocket motor ever built by India's private sector — passed a 110-second static fire. The second stage, Kalam-250, was the first carbon-composite motor ever tested at an ISRO facility. The nose cone and stages were flagged off from Skyroot's Hyderabad campus by the Telangana chief minister and trucked to Sriharikota, where final integration and launch-campaign work has been under way. The flight is being conducted under the authorisation of IN-SPACe, the regulator Delhi created when it opened the sector to private players in 2020, with ISRO providing technical oversight.

## Money is following the rockets

The timing is not an accident. In May, Skyroot raised $60 million at a $1.1 billion valuation, becoming India's first space-tech unicorn. The round was co-led by GIC, Singapore's sovereign fund, and Sherpalo Ventures — the firm run by Ram Shriram, an early Google backer who now sits on Alphabet's board and is joining Skyroot's. BlackRock-managed funds chipped in as well. That is the kind of investor roster that, a few years ago, would not have returned a phone call from an Indian rocket company.

Skyroot is not alone. Chennai's Agnikul Cosmos, also out of IIT Madras, is chasing its own orbital debut; Pixxel is building an Earth-imaging constellation; Digantara is tracking objects in space. A government industry that India guarded for half a century is turning into something that looks, increasingly, like an industry.

## Why an NRI should care

For Indian Americans, the obvious frame is the wallet. The two marquee India IPOs queued up for later this year — Reliance Jio and the National Stock Exchange — will draw plenty of diaspora money, and a credible private space sector adds a new column to the "invest back home" spreadsheet. Skyroot is still pre-revenue, and a maiden launch is exactly the moment when rockets blow up, so this is venture risk, not a savings account. But a successful Vikram-1 flight would re-rate the whole sector.

There is also a talent story that lands closer to home. Plenty of the engineers who would once have left Bangalore or Chennai for a propulsion job at SpaceX or Blue Origin now have a domestic option that is genuinely cutting-edge. For the Indian-origin aerospace engineer in California weighing a move, or for the founder wondering whether deep-tech capital exists in India, Skyroot is a data point that did not exist five years ago.

And for the diaspora that grew up watching ISRO's Mars and Moon missions as a point of pride, this is a different kind of milestone: not the state agency pulling off a feat, but a private company doing it the way Silicon Valley does. Whether Vikram-1 reaches orbit on the first try or not, the more durable signal is that India now has a space economy, not just a space programme."""

chip_body = """India has spent four years promising to make chips. The latest budget line tells you how it plans to spend the next one: roughly Rs 7,100 crore (about $850 million) in semiconductor incentives this fiscal year, aimed at a very specific shopping list — one chip fabrication plant, nine other manufacturing units, and thirty design firms.

The numbers are modest next to the tens of billions that Taiwan, the United States and China throw at the sector. But the structure of this year's plan is more revealing than the headline figure, and it says something about where India has decided it can actually win.

## What the money buys

According to government officials cited by Mint, the department of expenditure has tasked the IT ministry with disbursing the funds under the Modified Programme for Development of Semiconductors. The single fab unit gets Rs 2,000 crore in fiscal support and is expected to pull in Rs 4,000 crore of private investment and 1,500 jobs. The remaining Rs 5,000 crore is spread across nine units — compound semiconductors, silicon photonics, sensors, discrete-device fabs, and the assembly, testing and packaging (ATMP/OSAT) plants that do the unglamorous back-end work — meant to attract about Rs 11,000 crore in investment and 3,000 jobs.

This sits inside the bigger Semicon India programme, a Rs 76,000 crore commitment that has already cleared ten projects worth around Rs 1.6 lakh crore, including two fabs and eight packaging units, several now in pilot production. The Union Budget in February added a second tranche, ISM 2.0, explicitly aimed at materials, equipment and "full-stack Indian IP."

## The quiet pivot to design

Read closely, and the strategy is no longer "out-build Taiwan." It is "out-design where we can." Thirty design companies and a heavy tilt toward packaging and compound semiconductors is an admission that leading-edge silicon fabs — the multi-billion-dollar plants that print the most advanced logic chips — are a race India is not going to win this decade. What India does have is engineers. The government says 350 universities now have access to chip-design software used by 65,000 engineers, and 24 startup design projects have been backed, 16 of which have completed tapeouts.

That plays to a well-known strength. A very large share of the world's chip-design workforce — the people writing RTL at Nvidia, Qualcomm, AMD and Intel — is already Indian, much of it sitting in those companies' enormous Bangalore and Hyderabad campuses.

## Why this matters to the diaspora

For an Indian-origin chip engineer in the Bay Area or Austin, this is the most concrete "you could do this at home" signal yet. The design-led bet is aimed squarely at the kind of work the diaspora already dominates abroad — and the companies setting up Indian operations are the same ones that sponsored the H-1B that brought many of them over. As US visa costs and processing risk keep climbing, a credible Indian design ecosystem changes the math for a mid-career engineer weighing whether the green-card wait is worth it.

For NRI investors, the read is more cautious. The incentive is real money but spread thin, and the bulk of the value chain it funds is back-end packaging and niche compound chips, not the high-margin frontier. The opportunity is in the suppliers, the equipment makers and the design-services firms that ISM 2.0 is trying to seed — not in a single national champion fab that does not yet exist.

The honest takeaway: India is not about to dethrone TSMC. But it is building the layer of the industry where its people already lead, and funding it on a schedule. For a diaspora that has spent two decades designing the world's chips from someone else's payroll, that is the part of the semiconductor story worth watching."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India's First Private Rocket-to-Orbit Is on the Pad. The Company Behind It Isn't ISRO.",
        "subheadline": "Skyroot's Vikram-1 is in final preparations at Sriharikota for the maiden orbital flight of an Indian private rocket — backed by GIC, BlackRock and an early Google investor.",
        "slug": make_slug("skyroot-vikram-1-private-orbital-launch-sriharikota-space-unicorn-nri"),
        "category": "technology",
        "vertical": "space-tech",
        "diaspora_angle": "For NRI investors eyeing India's marquee IPOs and for diaspora aerospace engineers weighing a move home, Skyroot's launch is proof that India now has a private space economy — not just a state space programme.",
        "tags": ["space-tech", "skyroot", "indian-tech", "startups", "isro", "deep-tech"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/05/11/indias-first-space-tech-unicorn-emerges-as-skyroot-gears-up-for-orbital-launch/"},
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/indias-skyroot-becomes-first-1-bln-space-tech-startup/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/science/skyroot-static-tests-vikram-1s-powerful-kalam-1200-booster/"},
            {"name": "AirPro News", "url": "https://airpronews.com/skyroot-aerospace-dispatches-vikram-1-orbital-rocket-to-spaceport/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/12/Vikram-S_rocket%27s_Mission_Prarambh_%28cropped_wide%29.png",
        "image_caption": "Skyroot Aerospace's Vikram-S rocket lifts off on Mission Prarambh from Sriharikota in November 2022, India's first private rocket to reach space.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": skyroot_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Set Its Chip Budget for the Year: Rs 7,100 Crore, and a Quiet Bet on Design Over Fabs",
        "subheadline": "The FY27 plan funds one fab, nine manufacturing units and thirty design firms — an admission that India will compete where its engineers already dominate, not where Taiwan does.",
        "slug": make_slug("india-semiconductor-incentive-7100-crore-fy27-chip-design-fabs-nri-engineers"),
        "category": "technology",
        "vertical": "semiconductors",
        "diaspora_angle": "For the Indian-origin chip engineer at Nvidia or Qualcomm, India's design-led semiconductor bet is the clearest 'you could do this at home' signal yet — aimed at exactly the work the diaspora already dominates abroad.",
        "tags": ["semiconductors", "india-semiconductor-mission", "chip-design", "indian-tech", "policy", "make-in-india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Mint", "url": "https://www.livemint.com/industry/india-plans-semiconductor-buildout-with-7100-crore-incentives-in-fy27"},
            {"name": "DIGITIMES", "url": "https://www.digitimes.com/news/india-plans-fresh-chip-incentive-fiscal-2027.html"},
            {"name": "Press Information Bureau", "url": "https://pib.gov.in/PressReleasePage.aspx?PRID=semicon-india-programme"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f3/200mm_Wafer_Fertigungslinie.JPG",
        "image_caption": "A 200mm semiconductor wafer fabrication line, the kind of back-end and manufacturing capacity India's FY27 incentives target.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": chip_body
    }
]

# Word count sanity check
for art in articles:
    wc = len(art["body"].split())
    print(f"  [{wc} words] {art['headline'][:60]}")

print("---INSERTING---")
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
