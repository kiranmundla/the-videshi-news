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

chip_body = """India has spent years and billions of dollars chasing a single, stubborn goal: to make a chip of its own. This month, in a quiet corner of the power sector, it finally has one rolling toward the real world.

Azimuth AI, a Hyderabad-based semiconductor design startup backed by the engineering firm Cyient, has begun supplying a locally patented 40-nanometre system-on-chip for smart electricity meters, with commercial deployment starting as early as June 2026. Branded ARKA GKT-1 and unveiled by Ashwini Vaishnaw, the union minister for electronics and IT, it is being described as one of the first privately designed and commercialized industrial chips to come out of India. The system-on-chip, which packs the components of an entire processing system onto a single sliver of silicon, was developed over roughly two years with an investment of about 150 crore rupees.

## Why a humble meter chip is a milestone

The instinct is to ask why anyone should care about a chip for an electricity meter when the headlines belong to Nvidia's AI processors and the bleeding edge of 2-nanometre fabrication. The answer is that India's problem has never been ambition at the frontier; it has been shipping anything at all. For decades the country designed chips for foreign companies but owned almost none of the intellectual property and commercialized even less. ARKA GKT-1 changes the verb. The IP resides in India, the design was done in India, and a domestic startup will sell it.

The market is real, not symbolic. India aims to deploy some 300 million smart meters by 2030 as part of a national push to modernize its creaking electricity grid and cut the losses that plague distribution. Cyient is targeting a global smart-meter market worth around $29 billion. Azimuth says its chipset delivers 20 to 30 percent local value addition for the clients building those meters, a meaningful dent in a sector long dependent on imported power-management components.

## The diaspora's quiet stake

For the Indian diaspora, this is more than a feel-good story about self-reliance. The global semiconductor industry runs on Indian engineers, many of them trained at the IITs and seasoned at Intel, AMD, Qualcomm, Nvidia and Texas Instruments across the United States. For years the lament has been that India produces the talent but not the silicon, sending its best chip designers abroad because there was nothing to build at home. A homegrown startup that designs, owns and sells its own IP is exactly the kind of anchor that can begin to reverse that flow, giving an NRI semiconductor veteran a reason to consult, invest or relocate.

It also matters to the diaspora's wallet. Indian-origin investors and family offices have been hunting for the country's first credible fabless success stories, and Cyient's bet sits alongside Mindgrove Technologies, an IIT Madras-incubated startup pursuing the same domestic-IP playbook. The companies plan to extend the model into power, space and battery management, with Cyient's leadership noting that much of a patented design can be reused across new chips for new sectors. The thesis is that one good chip becomes a platform, not a one-off.

## What India still cannot do

Sobriety is in order. The chip is designed in India, but it is still manufactured overseas, because the country lacks meaningful fabrication capacity. India's first 28-nanometre chip remains in testing, and the four semiconductor plants the government has championed are only now inching toward commercial output. Forty nanometres is a mature node, decades behind the cutting edge, well suited to an industrial meter but nowhere near the chips that power phones or data centers. The roughly three-year journey from design to commercialization is exactly what Cyient says it wants to compress.

Cyient's executives have framed the security angle pointedly: a chip designed and owned in India for critical infrastructure ensures there are "no backdoors" in the meters that will sit in hundreds of millions of homes. That argument, about sovereignty as much as economics, is the one most likely to keep government money flowing under the country's 760-billion-rupee semiconductor incentive scheme.

## What to watch

The signal to track is the second chip, not the first. A single smart-meter SoC proves India can finish the race once. A pipeline of reusable, India-owned designs across power, automotive and IoT would prove it can build an industry. For the diaspora engineers who left because there was nothing to build, that is the number that decides whether the next generation has a reason to stay."""

forti_body = """The most damaging cyberattack of the year so far did not exploit a clever new flaw. It walked in through the front door, using passwords the criminals already had. And India sat near the front of the casualty list.

Researchers have disclosed a sweeping campaign, dubbed "FortiBleed," that compromised verified login credentials for roughly 75,000 Fortinet firewall and VPN devices across more than 15 countries. The United States, India and Taiwan were among the worst hit. Hudson Rock, the cybercrime-tracking firm that helped surface the breach, called the scale "staggering" and said it touched "nearly every sector of the global economy, sparing no industry." Confirmed victims reportedly include Accenture, Oracle, Samsung, Foxconn, Lenovo, Siemens and PwC.

## A breach made of paperwork, not genius

What makes FortiBleed unsettling is how mundane it was. Fortinet said the activity was "not related to any recent incident or advisory" and involved no new vulnerability. Instead, attackers drew on data from previous incidents and hammered devices with repeated password guesses, a brute-force technique scaled to industrial proportions: more than 1.16 billion credential attempts against roughly 320,000 FortiGate targets. As one analyst put it, "the perimeter device is no longer breached by cleverness; it is breached by paperwork the criminals already had."

Firewalls and VPN gateways are precisely the machines companies trust to keep everyone else out. They are the locked door to the corporate network and the tunnel through which remote employees log in. Once an attacker holds valid credentials to one, the door opens quietly, and from there they can move laterally, escalate into Active Directory, and steal data without tripping the alarms designed to catch intruders. US cyber agency CISA has urged organizations to rotate credentials, enforce phishing-resistant multifactor authentication, and pull firewall management interfaces off the public internet.

## Why India is in the crosshairs

India's prominence on the victim list is not an accident of size. The country has become one of the most-targeted nations in the Asia-Pacific region for cyberattacks, with ransomware incidents climbing sharply as its digital economy races ahead of its security maturity. A vast and rapidly expanding base of internet-facing infrastructure, much of it run by small and mid-sized firms without dedicated security teams, makes for a target-rich environment. When a campaign sprays 1.16 billion password attempts across the internet, the countries with the most exposed devices and the thinnest defenses light up first.

For the diaspora, the exposure is personal and professional at once. Indian IT services giants and the global capability centers that multinationals have planted across Bengaluru, Hyderabad and Pune are exactly the kind of organizations whose perimeters depend on devices like these. Many of the engineers managing corporate security for Fortune 500 firms, on either side of the Pacific, are Indian. A breach at an Accenture or an Oracle reverberates through teams staffed heavily by Indian professionals, and through the family businesses and startups back home that increasingly run on the same off-the-shelf gear.

## The cybersecurity beat the diaspora already owns

There is an irony worth naming. The fastest-growing corner of enterprise technology, cybersecurity, is one where Indian-origin leadership is unusually deep. Nikesh Arora has turned Palo Alto Networks into a consolidation machine, snapping up companies to build an end-to-end security platform precisely because incidents like FortiBleed show that point products and good intentions are not enough. The lesson Arora has been selling to boards, that security must be unified, automated and assume the perimeter is already compromised, just got an expensive, real-world advertisement.

## What to watch

The number that matters now is not 75,000 devices but how many of those stolen logins turned into actual intrusions, a figure no one has yet established. Free lookup tools from Hudson Rock and SOCRadar let organizations check whether their domains appear in the leaked set, and the responsible move for any Indian firm or diaspora-run business using Fortinet gear is to assume exposure and rotate now. FortiBleed is a reminder that in 2026 the weakest link is rarely an unpatched bug. It is a reused password, sitting in a database the attackers bought long ago, waiting for someone to try the door."""

trupeer_body = """When a young Indian software startup wants to signal that it has graduated from promising to serious, it does something specific: it hires someone who has already built a giant. This month, Trupeer AI did exactly that.

The company, which calls itself a "workflow knowledge layer" for teams and AI agents, announced on June 18 that it had appointed Raghu Subramanian as president and chief business officer. The name carries weight in enterprise software. Subramanian was a founding member of the management team at UiPath, the automation company he helped grow from a single-digit-million valuation into a New York-listed business worth more than $35 billion. He established UiPath's India operations in 2016 and later ran the company as president and CEO for India and the Asia-Pacific region. The hire is Trupeer's bet that the same playbook can be run again.

## What Trupeer actually does

Trupeer's product attacks a problem every large organization quietly suffers from: knowledge that lives in people's heads and never makes it into usable form. Its platform takes messy, multimodal workflows, the way someone actually clicks through a system, and turns them into standard operating procedures, training guides, studio-quality videos and, crucially, continuously updated context that AI agents can consume. It claims more than 50,000 teams across 100-plus countries and delivers material in over 120 languages. Backed by RTP Global and Salesforce Ventures, it is positioning itself for the moment when companies stop experimenting with AI and start demanding that it plug into how work is genuinely done.

The "AI-ready context" piece is the tell. As enterprises rush to deploy AI agents, they are discovering that the agents are only as good as the institutional knowledge they can reach. A model that does not know your company's actual procedures is a confident stranger. Trupeer is selling the connective tissue, and Subramanian's job is to push that into the same enterprises, SaaS companies and global capability centers that he spent a decade selling automation to.

## Why this is a diaspora story

This is the India-US technology corridor functioning exactly as it now does. Trupeer is part of a generation of startups built by Indian founders who target global enterprise customers from day one rather than serving the domestic market alone. Subramanian's career, from CTO of EXL Service to the top of UiPath's India and APAC business, is the archetype of the diaspora operator: someone fluent in both Silicon Valley's go-to-market machinery and India's engineering depth, who can carry a young company across that bridge.

The global capability center, or GCC, sits at the heart of the strategy, and that detail matters for the diaspora. GCCs, the in-house technology and operations hubs that multinationals run in India, have become one of the most important employers of Indian tech talent, absorbing the very engineers that layoffs at Western firms have shaken loose. Trupeer naming GCCs as a core market is a sign of where enterprise software value is migrating: toward the India-based hubs that increasingly do the real work for global companies, not just the back-office support.

## The pattern behind the hire

There is a recognizable rhythm here. A founder-led startup proves product-market fit, raises from brand-name investors, and then imports a seasoned operator, often someone who scaled a previous category leader, to handle the unglamorous machinery of enterprise sales, partnerships and international expansion. Subramanian is that operator. His arrival does not tell us Trupeer will succeed; plenty of well-staffed startups stall. But it tells us the company intends to compete for large, multi-year enterprise contracts rather than settle for a niche.

## What to watch

The question for the diaspora's founders and engineers is whether the "knowledge layer" becomes a durable category or a feature that the big platforms, the Microsofts and Salesforces and ServiceNows, simply absorb. Salesforce Ventures' presence on Trupeer's cap table cuts both ways: a powerful backer, and a reminder of who could one day build or buy the same thing. The signal to track is customer concentration. If Trupeer can turn its 50,000 teams into a handful of large, expanding GCC and enterprise accounts under Subramanian, the bet pays off. If not, it becomes another reminder that in enterprise AI, distribution still beats cleverness."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Shipped a Chip of Its Own. It Powers an Electricity Meter, and That's the Point.",
        "subheadline": "Cyient-backed Azimuth AI is rolling out ARKA GKT-1, a homegrown 40nm system-on-chip whose IP stays in India. For the diaspora's semiconductor engineers, it's the anchor that's been missing.",
        "slug": make_slug("india-first-homegrown-chip-azimuth-cyient-arka-smart-meter-semiconductor-nri"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "The global chip industry runs on Indian engineers who left because there was nothing to build at home; a startup that designs, owns and sells its own IP in India is the kind of anchor that can begin reversing that talent and investment flow.",
        "tags": ["semiconductors", "azimuth-ai", "cyient", "make-in-india", "indian-tech", "deep-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Mint", "url": "https://www.livemint.com/companies/news/indiamade-40nm-chip-to-power-smart-meters-by-june-cyient-azimuth-ai-semiconductor.html"},
            {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/cyient-to-supply-40nm-smart-meter-chip-by-june/"},
            {"name": "Electronics For You", "url": "https://www.electronicsforyou.biz/industry-buzz/indias-new-40nm-chip-signals-major-leap-for-smart-meter-technology/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/12-inch_silicon_wafer.jpg/1280px-12-inch_silicon_wafer.jpg",
        "image_caption": "A silicon wafer, the foundation of semiconductor manufacturing. India's ARKA GKT-1 is designed and IP-owned domestically, though still fabricated overseas.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": chip_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "75,000 Firewalls, One Stolen Password at a Time: Why India Was Among the Worst Hit by 'FortiBleed'",
        "subheadline": "The year's biggest breach exploited no new flaw, just credentials the attackers already had. India's exposed, fast-growing digital infrastructure put it near the front of the casualty list.",
        "slug": make_slug("fortibleed-fortinet-breach-75000-firewalls-india-worst-hit-cybersecurity-nri"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India's IT giants and the GCCs that multinationals run there depend on exactly this kind of gear, and many of the engineers securing Fortune 500 firms are Indian; a breach at an Accenture or Oracle ripples through diaspora-staffed teams and family businesses back home.",
        "tags": ["cybersecurity", "fortinet", "data-breach", "india", "nikesh-arora", "enterprise-security"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/researchers-say-sweeping-hack-campaign-against-fortinet-devices-compromised-2026-06-18/"},
            {"name": "Inc.", "url": "https://www.inc.com/sam-blum/the-surprisingly-simple-way-hackers-just-breached-samsung-oracle-and-accenture/"},
            {"name": "The420.in", "url": "https://the420.in/fortibleed-campaign-compromises-75000-fortinet-firewalls/"}
        ]),
        "score_total": 79,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/BalticServers_data_center.jpg/1280px-BalticServers_data_center.jpg",
        "image_caption": "Rows of servers in a data center. The FortiBleed campaign compromised credentials on roughly 75,000 firewall and VPN devices worldwide.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": forti_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A UiPath Veteran Just Joined Trupeer AI. It's a Familiar Move in the India-US Tech Playbook.",
        "subheadline": "Raghu Subramanian, who scaled UiPath into a $35 billion company, is betting a young Indian startup can sell AI-ready knowledge to the world's enterprises and the GCCs doing their real work.",
        "slug": make_slug("trupeer-ai-raghu-subramanian-uipath-enterprise-ai-gcc-indian-startup-nri"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Trupeer naming global capability centers as a core market points to where tech value is migrating, toward the India-based hubs absorbing engineers shaken loose by Western layoffs, sold by a diaspora operator fluent in both Silicon Valley's machinery and India's engineering depth.",
        "tags": ["trupeer-ai", "raghu-subramanian", "uipath", "enterprise-ai", "gcc", "indian-startups"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Business News This Week", "url": "https://www.businessnewsthisweek.com/business/trupeer-ai-appoints-former-uipath-ceo-raghu-subramanian-as-president-and-chief-business-officer/"},
            {"name": "The Tech Portal", "url": "https://thetechportal.com/2026/06/18/trupeer-ai-raghu-subramanian-president/"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7876706/pexels-photo-7876706.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_attribution": "Pexels",
        "image_caption": "An enterprise software team at work. Trupeer AI turns messy workflows into training material and AI-ready context for large organizations.",
        "is_editorial": False,
        "body": trupeer_body
    }
]

print("=== word counts ===")
for art in articles:
    wc = len(art["body"].split())
    flag = "OK" if 580 <= wc <= 820 else "CHECK"
    print(f"  [{flag}] {wc} words  {art['slug']}")

print("\n=== inserting ===")
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK  {art['slug']}")
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")
