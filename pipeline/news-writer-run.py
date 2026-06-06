#!/usr/bin/env python3
"""News writer for The Videshi — June 6, 2026 evening run."""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

# Load Supabase creds
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

def insert_article(article):
    """Insert a single article into Supabase."""
    payload = json.dumps(article)
    result = subprocess.run(
        [
            "curl", "-sS", "-w", "\n%{http_code}",
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            "-H", f"apikey: {SUPABASE_KEY}",
            "-H", f"Authorization: Bearer {SUPABASE_KEY}",
            "-H", "Content-Type: application/json",
            "-H", "Prefer: return=representation",
            "-d", payload,
        ],
        capture_output=True, text=True, timeout=30
    )
    output = result.stdout.strip()
    lines = output.split("\n")
    http_code = lines[-1] if lines else "000"
    body = "\n".join(lines[:-1])
    print(f"  → HTTP {http_code} for '{article['headline'][:60]}...'")
    if http_code.startswith("2"):
        print(f"  ✓ Published: {article['slug']}")
        return True
    else:
        print(f"  ✗ FAILED: {body[:300]}")
        return False

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

articles = []

# ── ARTICLE 1: India E85 Ethanol Launch ─────────────────────────────

articles.append({
    "headline": "India Launches E85 Fuel at ₹20 Below Petrol. The Flex-Fuel Era Has Begun.",
    "subheadline": "The oil minister unveiled 85-percent-ethanol fuel on World Environment Day, with Maruti Suzuki, Hero MotoCorp and Toyota already rolling out compatible vehicles. The timing, with crude above $100 and the Strait of Hormuz partially closed, is not accidental.",
    "slug": "india-launches-e85-ethanol-fuel-flex-vehicles-puri-world-environment-day-20260606",
    "category": "news",
    "vertical": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/4d/Hardeep_Singh_Puri_with_PM_Modi_%28cropped%29.jpg",
    "image_caption": "Union Petroleum Minister Hardeep Singh Puri, who launched E85 fuel in New Delhi",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com"},
        {"name": "Livemint", "url": "https://www.livemint.com"},
        {"name": "ChiniMandi", "url": "https://www.chinimandi.com"}
    ]),
    "body": """India on Friday launched E85 fuel — gasoline blended with 85 percent ethanol — at a price roughly ₹20 per litre below conventional petrol, in what the government is calling the opening chapter of the country's flex-fuel era. Union Petroleum and Natural Gas Minister Hardeep Singh Puri unveiled the fuel at an IndianOil retail outlet in New Delhi on World Environment Day, flanked by executives from automakers that have already begun delivering E85-compatible vehicles to showrooms.

The rollout began at 48 public-sector fuel stations nationwide, with plans to expand to 500 outlets by December 2026 and approximately 5,000 by the end of 2027. E85 contains between 80 and 85 percent ethanol blended with conventional petrol, and can only be used in flex-fuel vehicles — cars and two-wheelers engineered to run on ethanol concentrations ranging from E20 to E100.

## Context and Background

The timing of the launch is difficult to separate from the geopolitical crisis in the Persian Gulf. With the Strait of Hormuz partially blocked since the start of the Iran war in February, crude oil prices have climbed above $100 a barrel and India's annual oil import bill — already the third largest in the world — has swelled further. India imports roughly 88.5 percent of its crude, a dependency that every disruption in West Asia converts into a direct fiscal and inflationary hit.

Against that backdrop, ethanol offers a domestically produced alternative that does not require a single barrel to cross the strait. India achieved its target of 20 percent ethanol blending in petrol in 2025, five years ahead of schedule. Since 2014, blending has risen from 1.53 percent to 20 percent, saving the country more than ₹1.84 lakh crore in foreign exchange and reducing crude oil imports by nearly 302 lakh metric tonnes, according to the petroleum ministry.

## Current Developments

Three automakers are already in the market with E85-compatible models. Maruti Suzuki has released a flex-fuel variant of its best-selling WagonR. Hero MotoCorp has launched flex-fuel versions of its Splendor and HF Deluxe motorcycles — significant given that India's two-wheeler fleet exceeds 30 crore vehicles. Toyota showcased a flex-fuel Innova at the Delhi launch event.

Puri sought to address consumer anxiety immediately. After the E85 launch, motorists flooded social media with questions about whether their existing E20-compatible vehicles would become obsolete. The petroleum ministry issued a formal clarification: E85 is an entirely separate fuel category, dispensed only through dedicated pumps with distinct signage. Existing E20 and standard petrol vehicles will continue to be manufactured and fuelled as before.

"E85 should not be confused with E20 fuel," Puri said in a video response on social media. "The introduction of E85 does not mean the end of E20 or petrol vehicles."

## Diaspora Impact

For the Indian diaspora, the E85 push carries echoes of a familiar playbook. Flex-fuel vehicles have been mainstream in Brazil and increasingly common in the United States, where E85 is widely available at gas stations across the Midwest. NRIs in those markets already understand the trade-offs — lower fuel cost per litre offset by slightly reduced fuel efficiency due to ethanol's lower calorific value.

The more consequential signal is macroeconomic. Each percentage point of additional ethanol blending reduces India's oil import bill and, by extension, the current account deficit that has historically pressured the rupee. A weaker rupee directly erodes the purchasing power of remittances, which totalled $129 billion in 2025 — the largest flow for any country.

The government has also framed E85 as a farmer income programme. Ethanol in India is produced from sugarcane, agricultural waste, grains, bamboo and seaweed. The ministry estimates that if 50 percent of newly sold vehicles become flex-fuel compatible, it could generate demand for over 311 crore litres of additional ethanol and channel nearly ₹12,403 crore in extra income to Indian farmers.

## What's Next

The government plans to raise India's overall ethanol blending level to nearly 26 percent by 2030–31. Achieving that will require not just consumer adoption of flex-fuel vehicles, but a parallel buildout of ethanol production capacity, which has already expanded nearly fivefold to approximately 2,000 crore litres. The petroleum ministry is also working on a programme to boost compressed biogas production, opening a second front in India's biofuel strategy.

Whether E85 remains a niche curiosity or becomes a genuine mass-market fuel will depend on how quickly the vehicle ecosystem scales. For now, the government is betting that $100 crude oil and a ₹20-per-litre discount will do the persuading."""
})

# ── ARTICLE 2: Hegseth Calls India "Critical Anchor" ────────────────

articles.append({
    "headline": "The Pentagon Just Called India a 'Critical Anchor.' Then It Offered to Co-Produce Javelin Missiles.",
    "subheadline": "At the Shangri-La Dialogue in Singapore, US Secretary of Defense Pete Hegseth described India as essential to Indo-Pacific stability and confirmed joint production of Javelin anti-tank guided munitions — a level of defence-industrial integration Washington has reserved for its closest allies.",
    "slug": "hegseth-india-critical-anchor-javelin-co-production-shangri-la-2026-20260606",
    "category": "news",
    "vertical": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Pete_Hegseth_Official_Portrait.jpg/3840px-Pete_Hegseth_Official_Portrait.jpg",
    "image_caption": "US Secretary of Defense Pete Hegseth at the Shangri-La Dialogue in Singapore",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://www.theindianeye.com"},
        {"name": "US Department of War", "url": "https://www.war.gov"},
        {"name": "Defence Connect Australia", "url": "https://www.defenceconnect.com.au"},
        {"name": "Pacific Forum", "url": "https://www.pacforum.org"}
    ]),
    "body": """US Secretary of Defense Pete Hegseth on Saturday elevated India's role in American Indo-Pacific strategy to its most explicit public framing yet, calling the country a "critical anchor" for regional stability and confirming that Washington and New Delhi have committed to jointly producing Javelin anti-tank guided munitions.

Speaking on the second day of the Shangri-La Dialogue in Singapore — Asia's premier defence summit — Hegseth placed India alongside traditional US treaty allies in a speech that outlined the Trump administration's vision for deterring China and managing the ongoing Iran conflict simultaneously.

## Context and Background

"In South Asia, India is a critical anchor to hold the line," Hegseth said. "A powerful India acting in its own self-interest advances our shared goal of maintaining a balance of power across the region."

The language represents a deliberate escalation in diplomatic signalling. Previous administrations have described India as a "strategic partner" or a "net security provider." The term "critical anchor" places India in a structural category — not just a partner to consult, but a load-bearing element of the regional security architecture. Coming from a Pentagon chief who struggled to name ASEAN members during his confirmation hearing earlier this year, the specificity was striking.

Hegseth went further, praising India's military modernisation in terms typically reserved for formal allies. "India is modernising its military to carry its share of the security burden, particularly in the Indian Ocean," he said. "It's building out the heavy industrial and logistics capacity to sustain high-end military operations, including the ability to repair and maintain our shared platforms and support US Navy vessels operating forward in the theatre."

## Current Developments

The most consequential line in Hegseth's address was the Javelin announcement. "We've also committed to pursuing co-production with India to advance capabilities like Javelin anti-tank guided munitions," he said. "Real, tangible steps to improve the collective readiness of our forces."

Javelin missiles are made by a Lockheed Martin–Raytheon joint venture and have been among the most closely guarded weapons systems in the US arsenal. Co-production — as distinct from simple procurement — involves transferring manufacturing know-how and establishing production lines on Indian soil. Until recently, this level of defence-industrial integration was reserved for a small circle: the United Kingdom, Australia, Japan and a handful of NATO allies.

Hegseth also disclosed that the US and India held their first-ever joint industry-government experts exchange last month to develop autonomous systems under the newly established US-India Autonomous Systems Industry Alliance. "This kind of industrial muscle isn't just a long-term goal, it's an immediate operational imperative," he said.

The remarks came alongside Defence Secretary Rajesh Kumar Singh's 10 bilateral meetings on the Shangri-La sidelines — with counterparts from the US, Australia, Japan, South Korea, France, the United Kingdom, Canada, NATO, and several ASEAN nations — underscoring India's emergence as the most sought-after interlocutor at the summit.

## Diaspora Impact

For the more than five million Indian Americans in the United States, the deepening US-India defence relationship carries both strategic and economic implications. Defence co-production agreements typically spawn supply chains that run through both countries, creating engineering and manufacturing opportunities in American cities with large Indian diaspora populations.

The Javelin co-production specifically opens a corridor for Indian defence firms — and the diaspora professionals who work across both ecosystems — to participate in the highest-value segment of the bilateral relationship. Several Indian-American entrepreneurs are already involved in the US-India Autonomous Systems Industry Alliance announced by Hegseth.

## What's Next

The framework for deeper integration is moving fast. Earlier this week, India and the US agreed to sign a 10-year Defence Framework — the first formal agreement of its kind, replacing the ad-hoc renewal of shorter-term memoranda. Separately, the Pentagon confirmed that discussions are underway for India to co-produce and repair US military platforms, including possibly servicing US Navy vessels at Indian shipyards.

Whether the "critical anchor" framing survives beyond rhetoric will depend on execution. The Javelin co-production timeline, the autonomous systems alliance's first deliverables, and the 10-year framework's binding provisions will determine whether Saturday's speech was a diplomatic gesture or a structural shift. For now, Washington is making its bet in public."""
})

# ── ARTICLE 3: India-Australia Defence Ties ──────────────────────────

articles.append({
    "headline": "India and Australia Just Widened Their Defence Partnership. Maritime Security Is the Centrepiece.",
    "subheadline": "Rajnath Singh and Australian counterpart Richard Marles agreed to expand cooperation in maritime security, cybersecurity and emerging technologies — a step Australia's government described by calling India a 'top-tier security partner.'",
    "slug": "india-australia-defence-partnership-rajnath-marles-maritime-cyber-20260606",
    "category": "news",
    "vertical": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/63/2025_Rajnath_Singh_%28cropped%29.jpg",
    "image_caption": "Indian Defence Minister Rajnath Singh, who met his Australian counterpart in New Delhi",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://www.theindianeye.com"},
        {"name": "Ministry of Defence India", "url": "https://www.mod.gov.in"},
        {"name": "Reuters", "url": "https://www.reuters.com"}
    ]),
    "body": """India and Australia have agreed to significantly broaden their defence partnership, adding maritime security, cybersecurity and emerging technologies to a relationship that Australia's government now describes with language it typically reserves for its closest Western allies: "top-tier security partner."

Defence Minister Rajnath Singh met his Australian counterpart, Deputy Prime Minister and Minister for Defence Richard Marles, in New Delhi this week for talks that produced a commitment to expand and diversify defence-industry collaboration. The Ministry of Defence said the two sides agreed to deepen cooperation across counter-terrorism, hydrographic security and joint innovation in critical and emerging technologies.

## Context and Background

The India-Australia defence relationship has evolved rapidly over the past five years, accelerated by the Quad framework and growing shared concern over China's military assertiveness in the Indo-Pacific. The two countries signed a Mutual Logistics Support Agreement in 2020, enabling their navies to use each other's bases for replenishment — a privilege that signals deep operational trust.

Joint exercises have expanded in scope and frequency. The Malabar naval exercise, which India conducts with the US, Japan and Australia, has grown into one of the Indo-Pacific's most complex multinational drills. Indian and Australian forces also participate in the bilateral AUSINDEX exercise and have begun interoperability trials across maritime, land and air domains.

But the relationship's structural limitation has been the absence of deep defence-industrial links. Unlike India's emerging co-production arrangements with the United States — including the newly announced Javelin missile co-production — the India-Australia defence trade has remained modest, dominated by small-scale procurements rather than joint manufacturing.

## Current Developments

The New Delhi meeting appears designed to change that. Marles and Singh agreed to identify specific areas for defence-industry collaboration, moving beyond the logistics and exercise framework into the commercial spine of the relationship. The focus areas — cybersecurity, critical minerals, space and autonomous systems — are domains where Australia brings world-class capabilities and India brings scale and engineering depth.

Australia is a global leader in mining and processing the critical minerals that underpin modern defence systems, from lithium for batteries to rare earths for precision-guided munitions. India's push to build a domestic semiconductor and defence-electronics ecosystem — underscored by the NITI Aayog semiconductor roadmap released this week — creates a natural complementarity.

"Both sides are now seeking to deepen interoperability across maritime, land and air domains," the Indian defence ministry said in a statement. The agreement also covers hydrographic security — the mapping and monitoring of undersea terrain — a domain of increasing strategic importance as submarine warfare and undersea cables become central to Indo-Pacific security planning.

The maritime dimension is particularly significant. The Indian Ocean remains the most important waterway for both countries' trade and energy security. The Strait of Hormuz crisis has underlined how quickly a disruption in one chokepoint can cascade across the entire ocean. India's growing naval presence — including its third aircraft carrier programme and expanded submarine fleet — aligns with Australia's own investment in nuclear-powered submarines under the AUKUS framework.

## Diaspora Impact

The roughly 800,000 people of Indian origin in Australia form one of the country's fastest-growing diaspora communities and have become an informal bridge between the two countries' strategic establishments. Several Indian-Australian professionals work across both countries' defence research agencies, and the bilateral relationship increasingly draws on this human capital for technical and policy expertise.

For NRIs in Australia, the deepening defence partnership also signals stability in the broader bilateral relationship, which has occasionally been strained by trade disputes and visa policy changes. A robust defence link creates structural incentives for both governments to manage other irritants constructively.

The cooperation in critical minerals and space technology could also create career and investment pathways for diaspora professionals in both countries, as joint ventures in these sectors scale up.

## What's Next

The next milestone will be the identification of specific defence co-production projects flowing from the New Delhi agreement. Both sides are expected to present a joint workplan at the next Australia-India 2+2 ministerial dialogue, which brings together the two countries' foreign and defence ministers.

The broader trajectory is clear: India and Australia are building a defence relationship that goes beyond diplomatic symbolism and joint exercises into the hard infrastructure of interoperability and industrial integration. Whether they can move at the speed the Indo-Pacific demands remains the open question."""
})

# ── INSERT ALL ───────────────────────────────────────────────────────

print(f"\n{'='*60}")
print(f"Inserting {len(articles)} articles at {now}")
print(f"{'='*60}\n")

success = 0
for i, article in enumerate(articles, 1):
    print(f"\n[{i}/{len(articles)}] {article['headline'][:70]}...")
    if insert_article(article):
        success += 1

print(f"\n{'='*60}")
print(f"Done: {success}/{len(articles)} articles published successfully")
print(f"{'='*60}")
