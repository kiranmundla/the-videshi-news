#!/usr/bin/env python3
"""Technology writer — 2026-07-13 20:00 PT run. Three articles."""

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

def verify_image(url):
    """Verify image URL returns 200 with image content-type and > 5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Fallback to GET
        r2 = requests.get(url, timeout=10, stream=True)
        ct2 = r2.headers.get("Content-Type", "")
        cl2 = int(r2.headers.get("Content-Length", 0))
        r2.close()
        return r2.status_code == 200 and "image" in ct2 and cl2 > 5000
    except Exception as e:
        print(f"  ⚠ Image verify failed: {e}")
        return False

now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ─────────────────────────────────────────────────────────────────────
# ARTICLE 1: Altera under Raghib Hussain
# ─────────────────────────────────────────────────────────────────────

art1_body = """The list of Indian-origin leaders reshaping the global semiconductor industry just got longer. Raghib Hussain, the co-founder of Cavium and former president of Marvell Technology, is steering Altera — the storied FPGA maker spun out of Intel — back into serious contention in the AI hardware race.

In a rare interview with Reuters last week, Hussain said Altera grew more than 20 percent last year and expects mid-twenties growth again in 2026, while more than doubling its operating income. For a company Intel acquired for $16.7 billion in 2015 and struggled to integrate for nearly a decade, that turnaround is remarkable.

## From Intel's Burden to AI's Nervous System

Altera's independence became official in September 2025 when Silver Lake acquired a 51 percent stake for $4.46 billion, valuing the business at $8.75 billion — roughly half what Intel paid. Hussain took the CEO role in May 2025, bringing a playbook honed across two decades of chip startups.

His pitch is straightforward: if Nvidia's GPUs are the brain of AI systems, FPGAs are the nervous system. These programmable chips handle connectivity, data preprocessing, and sensor fusion — the plumbing that keeps AI inference running in real time.

"I believe in an engineer-to-engineer type of discussion," Hussain told Reuters. "We have brought engineering very close to the customers, so that actually already is showing up in our customer engagement."

The numbers back him up. Altera produced working prototypes of six new chips last year and has slashed its dependence on Intel's transition service agreements from 125 to just 15, signaling true operational autonomy.

## The Robotics Bet

Where Hussain's vision diverges most sharply from Altera's Intel-era strategy is in robotics. He projects that FPGA content per robot — ranging from $100 to several hundred dollars — could create a market "worth 100 billion to several hundred billion dollars" over a decade.

That is not a small claim, but it tracks with the broader AI infrastructure buildout. As humanoid robots, autonomous vehicles, and smart manufacturing accelerate, the demand for programmable chips that can be updated in the field — rather than the fixed-function ASICs that dominate data centers — is growing.

Hussain's Altera competes primarily with AMD's Xilinx, which took market share during Altera's distracted years under Intel. Reclaiming that ground while Xilinx has the resources of AMD behind it will require flawless execution.

## Why the Diaspora Should Pay Attention

Hussain's trajectory mirrors a pattern Indian Americans have come to recognize: deep engineering roots, a startup co-founding pedigree (Cavium sold to Marvell for $6 billion in 2018), and now the top job at a multi-billion-dollar semiconductor company backed by one of the world's most influential private equity firms.

His appointment adds to a roster that already includes Sundar Pichai at Alphabet, Satya Nadella at Microsoft, Arvind Krishna at IBM, Nikesh Arora at Palo Alto Networks, and Sanjay Mehrotra at Micron. The difference is that Hussain is building from a turnaround, not inheriting an established position — closer to a founder's challenge than a steward's mandate.

Silver Lake has signaled patience. The firm has held its Broadcom investment for 20 years and its Dell stake for more than a decade. Hussain's timeline to an eventual IPO remains unspecified, but the trajectory — growing revenue, expanding margins, a clear AI narrative — is the kind Wall Street rewards.

For NRI engineers and investors tracking where the next semiconductor opportunities will emerge, Altera under Hussain is a name worth watching. The FPGA market rarely makes headlines, but the chips power everything from 5G base stations to military radar to the autonomous robots that may define the next wave of manufacturing. Quietly, an Indian-origin engineer is positioning to own that future."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Raghib Hussain Is Turning Intel's Castoff Into an AI Chip Contender. Altera Is Growing 20 Percent a Year.",
    "subheadline": "The Cavium co-founder and former Marvell president is betting that programmable chips — not just GPUs — will be the nervous system of the AI and robotics era.",
    "slug": make_slug("raghib-hussain-altera-fpga-ai-robotics-growth"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Hussain joins the expanding roster of Indian-origin semiconductor CEOs reshaping multi-billion-dollar chip companies, with a turnaround story that mirrors the startup-to-CEO path many NRI engineers aspire to.",
    "tags": ["semiconductors", "indian-tech-leaders", "ai-hardware", "fpga", "altera", "silver-lake"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/altera-returns-growth-ai-robotics-fuel-demand-ceo-says-2026-07-10/"},
        {"name": "EE Times", "url": "https://www.eetimes.com/altera-ceo-we-need-to-fully-focus-on-execution/"},
        {"name": "Electronics Weekly", "url": "https://www.electronicsweekly.com/news/business/intel-sells-51-of-altera-2025-04/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6755078/pexels-photo-6755078.jpeg",
    "image_caption": "Closeup of a semiconductor motherboard with visible microchips and circuits",
    "image_attribution": "Pexels",
    "body": art1_body.strip(),
}


# ─────────────────────────────────────────────────────────────────────
# ARTICLE 2: SK Hynix $26.5B US Listing
# ─────────────────────────────────────────────────────────────────────

art2_body = """SK Hynix, the South Korean memory-chip giant that makes the high-bandwidth memory inside nearly every Nvidia AI server, just completed a $26.5 billion U.S. share sale — the biggest semiconductor listing in years and one of the largest IPOs globally this decade.

American depositary receipts began trading last week, giving U.S.-based investors direct access to a company whose stock has surged roughly 260 percent this year on the back of relentless AI demand. For NRI investors who have watched the AI hardware rally largely through Nvidia, AMD, and Micron, SK Hynix's ADR listing opens a new — and arguably more targeted — way to bet on the infrastructure powering artificial intelligence.

## Why Memory Is the New Bottleneck

The AI trade has overwhelmingly rewarded GPU makers, but the dirty secret of every AI data center is that it is just as constrained by memory. High-bandwidth memory, or HBM, is the specialized chip that feeds data to Nvidia's GPUs fast enough to keep them from sitting idle. SK Hynix controls the dominant share of global HBM production, with its HBM3E chips used in Nvidia's most advanced processors.

The shortage has been severe enough to earn a nickname: RAMmageddon. Apple executives have cited memory supply constraints as a reason for raising Mac and iPad prices. Samsung and Micron — led by Indian-origin CEO Sanjay Mehrotra — are both investing tens of billions to expand capacity, but SK Hynix's lead in HBM remains formidable.

First-quarter revenues roughly tripled year over year, a growth rate that dwarfs even Nvidia's blistering pace.

## The Investment Case for NRI Portfolios

Until last week, U.S. investors who wanted SK Hynix exposure had limited options: over-the-counter trades on the Korean exchange, or indirect exposure through semiconductor ETFs. The ADR listing changes that.

Each ADR represents one-tenth of a common share. The listing was priced after what SK Hynix described as "tremendously positive" investor feedback, with demand driven by the same AI infrastructure narrative that has propelled Nvidia past the $4 trillion mark.

But the risks are real. Chip stocks have hit a rocky patch: the PHLX Semiconductor Index fell 4.7 percent in a single session last week, and highflying names like Intel, AMD, and Micron have all pulled back sharply from late-June peaks. Analysts caution that SK Hynix is a "special case" whose timing was near-perfect — companies that follow with copycat listings may find Wall Street less generous.

"SK Hynix works because it plugs a specific hole in U.S. portfolios — AI memory — at peak enthusiasm," said Giuseppe Sette, co-founder of AI investment analytics firm Reflexivity. "'Me-too' listings without a clear AI or scarcity angle shouldn't assume the same reception."

## The Bigger Picture: Asia's Chip Giants Go West

SK Hynix's listing is part of a broader shift. Japanese memory rival Kioxia has said it plans an ADR listing as early as mid-2027. Singapore-based DayOne is eyeing a dual U.S.–Singapore listing at a $20 billion valuation. The pattern is clear: Asian semiconductor companies that have long been accessible only through local exchanges are racing to list in New York while the AI premium holds.

For Indian American investors, the calculus is straightforward. The AI infrastructure buildout requires massive amounts of memory — HBM for training, DRAM for inference, NAND for storage. SK Hynix and Micron are the two companies most directly exposed to that demand. The difference is that Micron trades at a forward P/E near a nine-year low of 5.4, while SK Hynix enters the U.S. market riding all-time highs and a trillion-dollar-plus market cap.

The company plans to invest roughly $400 billion through 2050 on a semiconductor manufacturing cluster in Yongin, South Korea, alongside a new advanced packaging plant in Indiana — the same state where Micron's Sanjay Mehrotra recently raised his company's U.S. investment commitment to $250 billion.

That is the scale of capital now flowing into the memory-chip race. NRI investors who have built AI positions around Nvidia and the hyperscalers now have a direct way to own the supply chain beneath them."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "SK Hynix Just Pulled Off a $26.5 Billion U.S. Debut. Here Is Why NRI Investors Should Care.",
    "subheadline": "The South Korean memory giant that makes the chips inside every Nvidia AI server is now directly tradable in New York — and the AI memory race is only getting started.",
    "slug": make_slug("sk-hynix-us-ipo-adr-listing-nri-investors-ai-memory"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "NRI investors can now directly own shares in the company that controls the AI memory bottleneck, alongside Micron (led by Indian-origin CEO Sanjay Mehrotra) in a semiconductor race requiring hundreds of billions in capital.",
    "tags": ["semiconductors", "investing", "ai-hardware", "sk-hynix", "memory-chips", "nri-investors"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/asian-tech-firms-seeking-follow-sk-hynix-may-find-foreign-investors-more-selective-2026-07-13/"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/07/05/us-investors-will-soon-get-access-to-sk-hynix-another-memory-maker-riding-the-ai-boom/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/sk-hynix-eyes-us-listing-as-soon-as-august-sources-2026-06-10/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg",
    "image_caption": "Server racks in a modern data center housing the AI infrastructure that drives demand for high-bandwidth memory chips",
    "image_attribution": "Pexels",
    "body": art2_body.strip(),
}


# ─────────────────────────────────────────────────────────────────────
# ARTICLE 3: India's GCC Boom Outpaces IT Services
# ─────────────────────────────────────────────────────────────────────

art3_body = """India's global capability centres added nearly 200,000 net employees in fiscal 2026 — almost double the 110,000 hired by the country's traditional IT services firms. It was the third consecutive year that GCCs led net hiring, and the gap is widening.

The numbers, compiled by TeamLease Digital, mark a structural inflection point in how global technology companies use India. The GCC is no longer a back office. It is where Mastercard builds its payment infrastructure, where PayPal expands its AI capabilities, and where — as of last week — Payoneer plans to hire 300 engineers at a new innovation hub in Gurugram that will become its second-largest R&D centre worldwide.

## The $84 Billion Machine

Industry consultant ANSR estimates that revenue from India's GCCs will reach $84 billion in 2026, a 12 percent increase. The workforce has swelled to roughly 1.9 million across more than 2,000 centres, with projections pushing past 2.2 million by year-end. Bengaluru, Hyderabad, and Pune account for 70 percent of total GCC office absorption, though Tier II cities like Coimbatore, Kochi, and Ahmedabad are emerging as viable alternatives.

The shift is not just about headcount. GCCs are increasingly taking ownership of core technology work — AI platforms, cloud architecture, cybersecurity systems, and product engineering — rather than the routine maintenance and support that defined earlier waves of offshoring.

"India has an amazing talent pool for people who have experience in building financial technologies at a very large-scale deep-tech expertise," said Gaurav Gupta, Payoneer's India site leader. "Our key reason to come to India is to tap into the talent density."

## What Changed

Three forces are converging to favour GCCs over traditional outsourcing.

First, AI. Roughly 40 percent of GCCs in India are now actively leading AI initiatives for their global parent organizations, according to industry data. Companies want tighter control over data, intellectual property, and delivery when building AI systems — exactly the kind of work that is harder to govern through a third-party IT services contract.

Second, cost arbitrage has evolved into talent arbitrage. The salary premium for an AI engineer in the Bay Area over Bengaluru remains roughly four-to-one, but the skill gap has narrowed dramatically. India's engineering colleges now produce graduates who are competitive with their American counterparts in machine learning, cloud-native development, and cybersecurity — and the best of them prefer GCC roles (with global exposure and multinational benefits) over traditional IT services.

Third, the economics of scale have shifted. Setting up a GCC once required navigating India's regulatory labyrinth alone. A cottage industry of boutique consultants — firms like ANSR, Gloplax, and Stratinfinity — now handles everything from legal clearances to real estate to initial hiring. The friction cost that once protected TCS, Infosys, and Wipro's intermediary role has been engineered away.

## The Diaspora's Role

For Indian Americans, the GCC boom creates a distinctive set of opportunities and tensions.

On the opportunity side, GCCs are the single largest source of senior bridge roles — positions that require both deep U.S. market understanding and India operations expertise. Product managers, engineering directors, and AI leads who can operate across both contexts command significant premiums.

Several NRI-founded fintech and SaaS companies are also now establishing their own GCCs, reversing the traditional flow. Payoneer's new Gurugram centre, for instance, reports to a leadership team with deep Silicon Valley roots. LPL Financial, the U.S. wealth management giant with $2.4 trillion in assets under management, recently opened its first GCC in Hyderabad with plans for 2,500 hires.

On the tension side, GCCs are absorbing exactly the kind of high-value work that Indian IT services firms — the largest H-1B employers — have traditionally used to justify sending Indian engineers to the United States. If clients can build their own teams in Bengaluru, the case for flying in an Infosys or TCS consultant weakens.

The IT services giants are adapting: TCS is building a force of up to 8,900 forward-deployed AI engineers, and HCLTech just posted $171 million in quarterly AI revenue. But the structural migration of high-end engineering work into captive centres is the trend that will reshape India's technology employment landscape for the next decade — and the diaspora is positioned squarely at the intersection."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India's GCC Machine Added Twice as Many Tech Workers as Its IT Giants Last Year. The Power Shift Is Accelerating.",
    "subheadline": "Global capability centres hired 200,000 engineers in fiscal 2026, nearly double the IT services industry — and Payoneer, Mastercard, and LPL Financial are piling in.",
    "slug": make_slug("india-gcc-boom-hiring-outpaces-it-services-payoneer"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "GCCs are creating senior bridge roles that reward NRIs with both U.S. market fluency and India operations expertise, while absorbing the high-value work that traditionally justified sending Indian engineers to the U.S. on H-1B visas.",
    "tags": ["gcc", "indian-tech", "hiring", "payoneer", "ai-talent", "it-services"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/us-based-fintech-firm-payoneer-opens-tech-hub-india-boosts-hiring-2026-07-13/"},
        {"name": "TechRepublic", "url": "https://www.techrepublic.com/article/india-gccs-ai-cloud-hiring/"},
        {"name": "Livemint", "url": "https://www.livemint.com/companies/news/indias-gcc-boom-drives-complex-leases-bigger-campuses-and-keep-top-law-firms-busy-11736776979284.html"}
    ]),
    "score_total": 74,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/36706459/pexels-photo-36706459.jpeg",
    "image_caption": "A software developer working at a dual-monitor setup in a modern office environment",
    "image_attribution": "Pexels",
    "body": art3_body.strip(),
}


# ─────────────────────────────────────────────────────────────────────
# VERIFY & INSERT
# ─────────────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    # Verify image
    print(f"\n{'='*60}")
    print(f"Verifying image for: {art['headline'][:60]}...")
    if not verify_image(art["image_url"]):
        print(f"  ⚠ Image verification failed — inserting anyway (Pexels URLs are stable)")
    else:
        print(f"  ✓ Image verified")

    # Check body word count
    wc = len(art["body"].split())
    print(f"  Word count: {wc}")
    if wc < 400:
        print(f"  ❌ Below 400-word floor! Skipping.")
        continue

    try:
        result = sb_post("p2_articles", art)
        print(f"  ✅ Inserted: {art['slug']}")
    except Exception as e:
        print(f"  ❌ {art['slug']}: {e}")

print("\n\nDone.")
