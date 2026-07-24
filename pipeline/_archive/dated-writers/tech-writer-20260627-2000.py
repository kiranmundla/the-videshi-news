#!/usr/bin/env python3
"""Videshi Tech Writer — 2026-06-27 20:00 PDT run. 3 articles."""

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


# ── ARTICLE 1: Upscale AI $2B Valuation ──────────────────────────────────────

art1_body = """Two Indian-origin serial entrepreneurs have built the hottest AI infrastructure startup in Silicon Valley — and they did it by ignoring the part of AI that everyone else is chasing.

Upscale AI, co-founded by **Barun Kar** and **Rajiv Khemani**, has raised $190 million in a Series A-1 round that values the company at $2 billion and brings its total funding to $500 million. The round was led by Premji Invest, the investment arm of Indian billionaire Azim Premji, with Nvidia, Salesforce Ventures, Temasek, and a constellation of blue-chip backers joining in.

The startup isn't building the next chatbot or training the next large language model. It is building the networking fabric — the physical plumbing — that connects AI chips, memory, and storage so trillion-parameter models can actually train and run without choking on their own data.

## The Bottleneck No One Talks About

Every AI training cluster runs into the same wall: GPUs are fast, but the network connecting them isn't. Nvidia dominates this space with its proprietary NVSwitch and NVLink technology, which ties together the 72 GPUs in its $3 million NVL72 racks. Upscale's SkyHammer chip is designed to compete directly with NVSwitch — but using open standards like UALink and ESUN rather than Nvidia's locked-in approach.

"AI infrastructure is being redefined at cluster scale, and networking is one of the most critical bottlenecks," Kar told reporters. "We're building a high-performance, open-standard AI fabric purpose-built for large-scale, synchronized workloads."

The irony is worth noting: Nvidia itself invested in the round. The chip giant apparently sees value in funding a competitor to its own proprietary networking technology — or perhaps prefers to keep the alternative inside its orbit.

## Deep Roots in Indian Engineering

Kar and Khemani are not first-time founders. Before Upscale, they co-founded Auradine, a blockchain and AI computing company that raised over $300 million. Khemani's résumé reads like a tour of Silicon Valley's semiconductor aristocracy — Intel, NetApp, Sun Microsystems, and Cavium (later acquired by Marvell for $6 billion). He also led Innovium, a networking chip company acquired by Marvell in 2021.

Kar, who serves as CEO, came up through Palo Alto Networks, Juniper Networks, and Motorola. Their leadership team draws heavily from Broadcom, Cisco, AWS, and Microsoft.

The Indian engineering pipeline is visible at every level. Premji Invest's bet reflects a broader pattern: Indian capital backing Indian-origin founders building foundational infrastructure for the AI era.

## Why NRIs Should Pay Attention

For Indian tech professionals working in data centre infrastructure, cloud engineering, or chip design across the Valley and beyond, Upscale represents both a career magnet and a market signal. The company has roughly 150 employees — mostly engineers — and is scaling rapidly.

More broadly, the $2 billion valuation for a pre-revenue networking company tells you where the AI hardware market is headed. The era of GPU-only investment is giving way to a recognition that interconnects, memory, and networking are equally critical. Indian engineers, who disproportionately staff the infrastructure teams at hyperscalers, stand at the centre of that shift.

Upscale's SkyHammer chips are expected to ship later this year. If they perform, the company will have proven that two founders from IIT and the Indian engineering tradition can build the connective tissue of the AI age — one open-standard switch at a time."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Two Indian-Origin Founders Just Built a $2 Billion Chip Startup. Nvidia Invested Anyway.",
    "subheadline": "Upscale AI's SkyHammer networking chip challenges Nvidia's own NVSwitch dominance — and the chip giant put money into the challenger. Premji Invest led the round.",
    "slug": make_slug("upscale-ai-2-billion-indian-founders-premji-nvidia-skyhammer"),
    "category": "technology",
    "vertical": "semiconductor",
    "diaspora_angle": "Indian-origin serial entrepreneurs Barun Kar and Rajiv Khemani, backed by Premji Invest, are building foundational AI infrastructure — a signal of growing Indian founder dominance in deep-tech hardware, not just software.",
    "tags": ["ai-infrastructure", "semiconductor", "indian-founders", "silicon-valley", "nvidia", "premji-invest", "startup"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/upscale-ai-valued-2-billion-after-funding-extension-2026-06-23/"},
        {"name": "Data Center Dynamics", "url": "https://www.datacenterdynamics.com/en/news/nvidia-backs-ai-networking-switch-silicon-startup-upscale-in-190m-raise/"},
        {"name": "The Register", "url": "https://www.theregister.com/2026/01/28/upscale_ai_raises_200m/"},
        {"name": "The Next Platform", "url": "https://www.nextplatform.com/2026/01/27/upscale-ai-nabs-cash-to-forge-skyhammer-scale-up-fabric-switch/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/BalticServers_data_center.jpg/1280px-BalticServers_data_center.jpg",
    "image_caption": "Server racks inside a modern data centre — the kind of infrastructure Upscale AI's networking chips are designed to connect",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body
}


# ── ARTICLE 2: Tata Electronics Data Breach ───────────────────────────────────

art2_body = """A ransomware attack on Tata Electronics has exposed more than 200,000 confidential files — including Apple manufacturing specifications, TSMC test data marked "Secret," and Qualcomm trade secrets — in what may be the most damaging cyber breach in India's electronics manufacturing history.

The hack, claimed by a group called World Leaks, dumped 630 gigabytes of data onto the dark web earlier this month. The fallout is forcing India's biggest Apple supplier to lock down its systems, hire global forensic auditors, and work directly with Apple's security team to contain the damage.

## What Was Leaked

The scale is staggering. According to Reuters, the leaked cache includes:

- **Apple manufacturing specifications** and quality inspection standards for iPhone circuit board components
- A 2022 document marked **"TSMC Secret"** containing product reliability test details with photographs
- A 2023 **Apple Silicon Engineering Group** document mapping Apple part numbers to TSMC's, with Apple employee names in the revision history
- A 2021 **Qualcomm** document showing mechanical details of a power management IC, watermarked "Confidential — May Contain Trade Secrets"
- **Employee passport copies**, emails, and system logs spanning several years

The World Leaks group, which previously claimed responsibility for a Nike breach, had reportedly issued a ransom demand to Tata Electronics before publishing the files.

## The Credibility Stakes

This is not just a Tata problem. India now manufactures **26% of the world's iPhones**, up from 6% four years ago, according to Counterpoint. The country's entire pitch to global electronics manufacturers — Apple, Tesla, Samsung, Google — rests on the promise that it can be a trusted, secure alternative to China.

A breach of this magnitude tests that promise. Apple's security team is now working "closely with Tata on near- and long-term measures," Reuters reported, a diplomatic phrasing that suggests Cupertino is deeply concerned about the integrity of its Indian supply chain.

Tata Electronics has restricted internal access to sensitive systems, notified the Indian government and affected clients, and engaged a global consultant for a forensic audit. The company says its operations remain unaffected — a claim that may be technically true but misses the point. The damage here is reputational, not operational.

## A Pattern, Not an Anomaly

This is not Tata's first cyber incident. Last year, the group's British Jaguar Land Rover unit was hit by a cyberattack that halted production for six weeks. The Tata Electronics breach is more insidious — no production stoppage, but intellectual property from the world's most secretive technology companies now sits on a dark-web database accessible to anyone willing to look.

Indian cybersecurity researcher Rajshekhar Rajaharia, who reviewed the files for Reuters, confirmed they include emails, multi-year event logs, and passport copies of employees including foreign nationals. A second researcher, Rakesh Krishnan, said the data had been accessible on the dark web since at least June 10.

## Why NRIs Should Care

For the Indian diaspora invested in Tata Group companies — or in the broader thesis that India can become a global manufacturing hub — this breach is a stress test. It does not necessarily change the trajectory; India's cost advantages and scale are real. But it exposes the gap between ambition and implementation in cybersecurity infrastructure.

For NRI tech professionals in cybersecurity, the incident underscores a growing demand signal: India's manufacturing ecosystem needs world-class security talent, and it needs it now. The question is whether this breach accelerates that investment or becomes another headline that fades without structural change."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Hackers Just Published 630 GB of Apple's Manufacturing Secrets. They Got Them From Tata.",
    "subheadline": "A ransomware group leaked 200,000 files from Tata Electronics — including TSMC documents marked 'Secret' and Qualcomm trade secrets. India's credibility as a manufacturing hub is on the line.",
    "slug": make_slug("tata-electronics-data-breach-apple-tsmc-qualcomm-world-leaks"),
    "category": "technology",
    "vertical": "cybersecurity",
    "diaspora_angle": "India now makes 26% of the world's iPhones. A massive data breach at its biggest Apple supplier tests the credibility of India's manufacturing ecosystem — and the NRI investment thesis behind it.",
    "tags": ["cybersecurity", "tata-electronics", "apple", "data-breach", "india-manufacturing", "supply-chain"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/media-telecom/apple-supplier-tata-tightens-internal-controls-after-data-breach-sources-say-2026-06-26/"},
        {"name": "9to5Mac", "url": "https://9to5mac.com/2026/06/26/apple-working-with-supplier-tata-after-sensitive-files-leak-online/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/tata-electronics-under-siege-dark-web-leak-of-200000-client-files-triggers-security-crackdown"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/tata-electronics-hit-by-cyber-breach-involving-apple-and-tesla-data/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/5380642/pexels-photo-5380642.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A cybersecurity monitoring interface — the kind of system Tata Electronics is now scrambling to upgrade",
    "image_attribution": "Pexels",
    "body": art2_body
}


# ── ARTICLE 3: Apple-Intel Foundry Deal ───────────────────────────────────────

art3_body = """Apple is in early talks with Intel about manufacturing chips on American soil — a potential deal that would reshape the global semiconductor map and put thousands of Indian engineers at the centre of a geopolitical chess match.

According to Bloomberg and Reuters, Apple has held preliminary discussions with Intel about using its foundry services, while Apple executives have visited a Samsung factory under construction in Taylor, Texas. The goal: build a backup to TSMC, the Taiwanese chipmaker that currently manufactures every Apple Silicon chip in iPhones, iPads, and Macs.

No orders have been placed. TSMC remains Apple's primary — and for now, only — chip manufacturing partner. But the fact that Apple is even exploring alternatives signals a fundamental shift in how the world's most valuable company thinks about supply chain risk.

## Why Now

The trigger is straightforward: TSMC cannot keep up. Surging demand for AI chips from Nvidia, AMD, and a dozen hyperscalers has consumed TSMC's most advanced manufacturing capacity. Apple CEO Tim Cook acknowledged on an April earnings call that Mac mini and Mac Studio supply is constrained, and it may take "several months" to achieve balance.

Apple's spending at TSMC has grown from $2 billion in 2014 to roughly $24 billion in 2025, according to SemiAnalysis — a 12x increase. At points, Apple has accounted for 25% of TSMC's total revenue. That kind of concentration creates risk, and Apple knows it.

The political backdrop matters too. President Trump has pushed hard for domestic chip manufacturing, and Intel has emerged as a centrepiece of that strategy. The U.S. government owns a 10% stake in Intel, and Nvidia invested $5 billion at the White House's behest. An Apple-Intel deal would be the crown jewel of America's reshoring push.

## The Indian Engineer Factor

This is where the story gets personal for the diaspora.

Intel employs tens of thousands of Indian-origin engineers across its design, manufacturing, and process technology teams — in Oregon, Arizona, and increasingly in Bengaluru and Hyderabad. A deal with Apple would turbocharge Intel's foundry business and create significant demand for semiconductor process engineers, a field where Indians are overrepresented.

At TSMC's Arizona fab, Indian engineers already form a significant portion of the workforce. An Apple order to Intel would create parallel demand, potentially easing the H-1B bottleneck that has constrained semiconductor hiring in the U.S.

Meanwhile, in India, the timing is conspicuous. Tata Electronics is building the country's first commercial semiconductor fab in Dholera, Gujarat, with ASML lithography equipment and an $11 billion investment. India isn't competing for Apple's most advanced chips — those require 3nm and 2nm processes — but the broader expansion of foundry capacity globally creates opportunity for India's growing semiconductor workforce.

## The Catch

Analysts are blunt: this deal, if it happens, is years away from producing chips. Malcolm Penn, CEO of Future Horizons, called it "a shotgun wedding" — Intel has no track record of manufacturing for Apple, and it would take at least two to three years to design, test, and ramp production of an Apple-grade system-on-chip.

The likely starting point would be less critical components — perhaps chips for a MacBook Air or older iPad models — while Apple tests Intel's yield rates. TSMC achieves industry-leading yields; Intel's 18A process just began initial production this month.

"Investors are pricing in perfect execution by Intel, which is a company that hasn't delivered for about 20 years," said Paul Meeks of Freedom Capital Markets.

## The Bigger Picture

For NRI investors and engineers watching the semiconductor landscape, the Apple-Intel talks represent a structural shift with long-term implications. If Intel can credibly serve Apple, it validates the U.S. reshoring thesis. If it cannot, it reinforces TSMC's monopoly — and, by extension, the geopolitical risk that comes with concentrating the world's chip supply in Taiwan.

Either way, Indian semiconductor talent — in the Valley, at Intel's fabs, at Tata's Dholera plant, and in Bengaluru's design centres — will be building the future."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Apple Is Quietly Shopping for a Second Chipmaker. Intel and Samsung Are Auditioning.",
    "subheadline": "Preliminary talks with Intel and a Samsung factory visit signal Apple's first serious effort to break its TSMC dependency. The deal is years away — but Indian semiconductor engineers are already at the centre of it.",
    "slug": make_slug("apple-intel-samsung-foundry-tsmc-backup-chip-manufacturing"),
    "category": "technology",
    "vertical": "semiconductor",
    "diaspora_angle": "Intel employs thousands of Indian-origin semiconductor engineers, and a foundry deal with Apple would expand hiring in a field where diaspora talent is concentrated. India's own Tata Dholera fab rides the same global capacity wave.",
    "tags": ["apple", "intel", "samsung", "tsmc", "semiconductor", "foundry", "chip-manufacturing", "geopolitics"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Bloomberg via MacRumors", "url": "https://www.macrumors.com/2026/05/04/apple-eyes-intel-and-samsung-as-backup-us-chipmakers/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/apple-intel-chip-deal-makes-strategic-sense-production-is-years-away-2026-06-24/"},
        {"name": "Memeburn", "url": "https://memeburn.com/2026/06/apple-intel-samsung-tsmc-chip-backup/"},
        {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/apple-intel-chip-deal-makes-strategic-sense-but-production-is-years-away/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Tim_Cook_March_2026_%28cropped_2%29.jpg",
    "image_caption": "Apple CEO Tim Cook, who acknowledged chip supply constraints and is exploring alternative manufacturers",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body
}


# ── Insert all articles ──────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
