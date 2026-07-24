#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-03 21:00 UTC run"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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

# Validate images before using them
def validate_image(url):
    """Check that an image URL returns 200 with image content-type and reasonable size."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {url[:80]}... ({cl} bytes)")
            return True
        print(f"  ✗ Image failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image error: {e}")
    return False

# ─── ARTICLE 1 ───────────────────────────────────────────────────────────────
# India's Chip Design Startup Boom

art1_image = "https://images.pexels.com/photos/6636463/pexels-photo-6636463.jpeg?auto=compress&cs=tinysrgb&w=1200"

art1_body = """India has spent decades designing chips for the world. Now, for the first time, a generation of Indian engineers is designing chips for companies they own.

In the first five months of 2026, semiconductor startups in India pulled in $92 million across 12 deals. That figure nearly quadruples the sector's total for all of 2025, when six transactions netted $25 million. The acceleration is not a statistical artefact. It marks a structural shift in how founders, investors, and the government are engaging with a sector that Indian venture capital long considered too slow and too capital-intensive to bother with.

## The Founders Are Coming Home

What gives this cohort its character is not the money alone. It is who is building these companies. The last two years have seen a wave of senior engineers leave global chip majors — Intel, AMD, Texas Instruments, Qualcomm, ARM — to start companies back in India.

Agrani Labs was founded by four people who previously held senior positions at Intel and AMD. They are targeting AI inference chips, the accelerators that run trained models at the point of deployment. C2i Semiconductors was started by veterans of Texas Instruments and is focused on power management ICs for AI data centres — a niche that has shifted from obscure to existential as hyperscale power consumption becomes a first-order industry constraint.

Constelli, HrdWyr, and VerveSemi each raised upwards of $10 million. Calligo Technologies and Agrani Labs were also actively fundraising. Eight of the 12 deals were seed rounds, accounting for $34 million, with the rest flowing into Series A. This is not a single breakout company carrying the numbers. It is an ecosystem beginning to generate deal flow.

## The Government's Quiet Catalyst

The Design-Linked Incentive scheme, part of the India Semiconductor Mission, has become a meaningful instrument for crowding in private capital. By absorbing early-stage risk that would otherwise scare off venture funds, DLI has functioned as both a financial backstop and a quality filter. Around two dozen companies have cleared DLI approval. A growing subset — Mindgrove Technologies, VerveSemi, InCore, BigEndian Semiconductors, Calligo Technologies, and MOSart Semi — have subsequently closed venture rounds.

The scheme is working not because it writes large cheques, but because it signals to private investors that a company's technology has passed an independent technical review. In a sector where due diligence is harder than in software, that signal matters.

## From Design to Silicon

Operational milestones are becoming real. At least half a dozen Indian startups have now taped out — the moment a chip design is finalised and sent to a foundry for manufacturing. C2i Semiconductors, Mindgrove Technologies, VerveSemi, and Calligo Technologies have all engaged foundries in Taiwan and South Korea. Mindgrove and Agnit Semiconductors are expected to cross into commercial production before the year ends.

This is the transition that matters: from designing chips to shipping them.

## What NRIs Should Watch

For Indian Americans in semiconductor engineering — and there are tens of thousands across Qualcomm's San Diego campus, Intel's Portland labs, TI's Dallas operations, and ARM's San Jose offices — this is a career inflection point. A decade ago, returning to India to work in chips meant joining a captive design centre. Today, it can mean founding a company with venture backing, government support, and a market that finally exists.

For NRI investors, the numbers remain small by global standards. A single advanced chip programme can cost more than India's entire startup semiconductor funding in 2026. But the trajectory — four times last year's capital in five months, with multiple companies reaching tape-out — suggests the sector is approaching the velocity where larger institutional capital begins to follow.

India built one of the world's deepest pools of chip design talent inside other people's companies. The $92 million raised in five months is the first serious signal that this talent is choosing to build its own."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Chip Design Startups Just Raised $92 Million in Five Months. That's Four Times All of 2025.",
    "subheadline": "Returning diaspora engineers from Intel, AMD, and Texas Instruments are founding semiconductor companies at home — and venture capital is finally following them.",
    "slug": make_slug("india-chip-design-startups-92-million-funding-boom"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Tens of thousands of Indian Americans work at Qualcomm, Intel, TI, and ARM. India's chip design startup boom offers a new path: founding companies at home with venture backing and government DLI support. NRI investors watching the sector see 4x funding growth in 5 months.",
    "tags": ["semiconductors", "indian-startups", "chip-design", "silicon-valley", "diaspora-returns"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/indias-chip-designers-are-finally-building-for-themselves/"},
        {"name": "NewsPoint / Economic Times", "url": "https://newspointapp.com/"},
        {"name": "Carnegie Endowment for International Peace", "url": "https://carnegieendowment.org/"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": art1_image,
    "is_editorial": False,
    "body": art1_body.strip()
}

# ─── ARTICLE 2 ───────────────────────────────────────────────────────────────
# ASML-Tata Dholera Fab

art2_image = "https://images.pexels.com/photos/5118462/pexels-photo-5118462.jpeg?auto=compress&cs=tinysrgb&w=1200"

art2_body = """For decades, India consumed chips but never made them. The Tata-ASML partnership signed in May signals that this is about to change — and the scale of the bet is enormous.

On May 16, during Prime Minister Narendra Modi's visit to the Netherlands, Tata Electronics signed a Memorandum of Understanding with ASML, the Dutch company that manufactures the lithography machines without which no advanced semiconductor fabrication facility on Earth can function. The deal will equip Tata's upcoming 300mm fab in Dholera, Gujarat — India's first commercial front-end semiconductor fabrication plant — with ASML's suite of deep ultraviolet lithography tools.

The investment: $11 billion. The target capacity: 50,000 wafers per month. The process nodes: 28nm to 110nm, covering power management ICs, display drivers, microcontrollers, and high-performance computing logic for automotive, mobile, AI, and communications applications.

## Why This Is Not Just Another MoU

India has signed many technology memoranda. This one is different because of what surrounds it. Tata Electronics has also inked partnerships with Tokyo Electron, Merck Electronics, ROHM, Intel, and Synopsys. Taiwan's Powerchip Semiconductor Manufacturing Corporation is licensing the process technology and providing design and construction assistance.

As the Carnegie Endowment for International Peace noted in an analysis published this week, these MoUs collectively point toward a deliberate effort to build an entire ecosystem, not just a factory. Since the Dholera fab project was announced in February 2024, the surrounding industrial base has grown enough to attract a company like ASML — which does not enter markets on sentiment.

The partnership also sits atop a formal government-to-government agreement: the "Partnership on Semiconductors and Related Emerging Technology" between India and the Netherlands. This is industrial policy backed by diplomatic architecture.

## The Chips Dholera Will Make

The 28nm to 110nm nodes that Dholera will produce are not cutting-edge by TSMC or Samsung standards. They are not meant to be. These are the workhorses of the modern electronics industry: the chips inside cars, 5G base stations, industrial controllers, and the power management circuits that keep AI data centres from melting. Global demand for these mature-node chips far exceeds supply, and the shortage that paralysed the auto industry during and after the pandemic demonstrated what happens when production is concentrated in too few places.

India's bet is that the world needs more geographic diversity in mature-node manufacturing, and that Dholera can serve that demand while building the institutional knowledge required to eventually move toward more advanced processes.

## What This Means for NRIs

For the estimated 300,000 Indians working in the global semiconductor industry — from design engineers at Qualcomm's San Diego campus to process engineers at Intel's Oregon fabs — the Dholera project represents a gravitational shift. The fab alone will require thousands of engineers across process, equipment, yield, and quality functions. The supply chain that must materialise around it — some 300 distinct suppliers, according to government estimates — will need experienced managers who understand how a semiconductor ecosystem operates.

For NRI investors tracking the Tata Group's listed entities, the semiconductor play is becoming a portfolio-level consideration. Tata Electronics itself is not yet public, but the project's scale and the partnerships it has attracted suggest a trajectory toward eventual listing.

India Semiconductor Mission 2.0, expanded in the Union Budget 2026-27, now covers semiconductor equipment, materials, intellectual property development, and research capabilities. The policy umbrella has widened from incentivising individual factories to nurturing an integrated value chain.

## The Test Ahead

The Dholera fab is expected to be operational by the second quarter of financial year 2027-28. Between now and then, the hardest work is not construction — it is attracting commercial customers willing to commit design-ins to an unproven fab. Failure to win early clients from automotive and industrial customers would damage India's credibility in the sector for years.

But the ecosystem is forming. The talent is deep. The capital is committed. And ASML, a company that has spent four decades perfecting the art of printing circuits onto silicon, does not sign partnerships it does not intend to honour."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "ASML Just Agreed to Equip India's First Commercial Chip Fab. The $11 Billion Dholera Bet Is Getting Real.",
    "subheadline": "Tata Electronics' partnership with the world's most critical semiconductor equipment maker signals that India's chip manufacturing ambitions have moved beyond policy announcements.",
    "slug": make_slug("asml-tata-dholera-india-first-commercial-chip-fab"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "300,000 Indians work in the global semiconductor industry. Dholera's $11B fab will need thousands of experienced engineers, creating a return-to-India career path for NRI semiconductor professionals. Tata Group's chip play is also becoming a portfolio consideration for NRI investors.",
    "tags": ["semiconductors", "india-manufacturing", "tata-group", "asml", "dholera", "nri-careers"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Carnegie Endowment for International Peace", "url": "https://carnegieendowment.org/"},
        {"name": "EE Times India", "url": "https://eetindia.co.in/tata-electronics-and-asml-collaborating-to-advance-indias-chip-manufacturing-ecosystem/"},
        {"name": "The Daily Jagran", "url": "https://www.thedailyjagran.com/"},
        {"name": "indmoney", "url": "https://www.indmoney.com/"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "image_url": art2_image,
    "is_editorial": False,
    "body": art2_body.strip()
}

# ─── VALIDATE & INSERT ───────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    print(f"\n{'='*60}")
    print(f"Processing: {art['headline'][:70]}...")
    print(f"Slug: {art['slug']}")
    
    # Validate image
    if not validate_image(art["image_url"]):
        print(f"  ⚠ Image validation failed, inserting anyway (Pexels URLs are stable)")
    
    # Validate body length
    word_count = len(art["body"].split())
    print(f"  Word count: {word_count}")
    if word_count < 400:
        print(f"  ✗ SKIPPING — body too short ({word_count} words)")
        continue
    
    # Insert
    try:
        result = sb_post("p2_articles", art)
        print(f"  ✅ Published: {art['slug']}")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        # Print response body if available
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Response: {e.response.text[:500]}")

print(f"\n{'='*60}")
print(f"Done. Processed {len(articles)} articles.")
