#!/usr/bin/env python3
"""Technology writer – 3 articles for The Videshi, 2026-06-12."""

import json, os, uuid, requests
from datetime import datetime, timezone

# ── env ──
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/.env.supabase"))
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

now_iso = datetime.now(timezone.utc).isoformat()

articles = []

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 1 — Broadcom's "Chips Only" Pivot
# ═══════════════════════════════════════════════════════════════════
articles.append({
    "id": str(uuid.uuid4()),
    "headline": "Broadcom Bets Everything on Custom Chips — and Wall Street Isn't Sure What to Think",
    "subheadline": "Record AI semiconductor revenue, a $35 billion infrastructure fund, and a deliberate retreat from integrated systems mark a pivotal turn for the San Jose chipmaker",
    "slug": "broadcom-custom-chips-pivot-ai-infrastructure-20260612",
    "body": """Broadcom has drawn a line in the silicon. In its fiscal second-quarter earnings call last week, CEO Hock Tan laid out a strategy that sounds counterintuitive for a company riding the AI hardware wave: step back from building complete AI systems and double down on designing the custom chips that power them.

The numbers behind the pivot are hard to argue with. Broadcom's AI semiconductor revenue hit a record $10.8 billion for the quarter, up 143 percent year-over-year. Total revenue reached $22.19 billion. The company now counts eight hyperscale customers — up from three a year ago — each commissioning bespoke AI accelerators tailored to their specific workloads. These are the chips that train and run the large language models at Google, Meta, and ByteDance, among others.

## The ASIC Advantage

What Broadcom is selling isn't off-the-shelf hardware. It's custom application-specific integrated circuits, or ASICs, designed in close collaboration with each client's engineering teams. Where Nvidia offers a general-purpose GPU that works for almost everyone, Broadcom builds a chip that works for exactly one customer — and works exceptionally well. The trade-off is higher design cost and longer lead times, but hyperscalers with billions to spend on AI infrastructure increasingly prefer the efficiency gains.

Tan's decision to exit the integrated systems business — selling racks, networking, and software as a bundle — signals confidence that the real margin lives in silicon, not in assembling boxes. It's a bet that the cloud giants would rather build their own infrastructure around Broadcom's chips than buy a turnkey solution.

## A $35 Billion War Chest

To fund the buildout, Broadcom announced the AI XPV Platform, a $35 billion joint venture with Apollo Global Management and Blackstone to finance AI data centre infrastructure. The fund will provide capital to companies deploying Broadcom-designed chips at scale, including customers of Anthropic and OpenAI. It's an unusual move for a semiconductor company — part industrial policy, part venture capital — and it ties Broadcom's fortunes even more tightly to the AI infrastructure boom.

Wall Street's reaction was decidedly mixed. Broadcom's stock fell roughly 19 percent after the earnings release, despite the record results. Analysts pointed to weaker-than-expected guidance for the next quarter and concerns that the "chips only" strategy limits Broadcom's addressable market. The broader semiconductor sector also felt pressure: Qualcomm dropped seven percent amid reports that ByteDance is developing custom AI chips that could reduce its reliance on third-party silicon.

## The Indian Engineering Engine

For the thousands of Indian engineers in Broadcom's San Jose headquarters and design centres, the pivot reshapes their daily work. Custom ASIC design is among the most demanding disciplines in chip engineering, requiring deep expertise in digital logic, physical design, and verification. Broadcom's Bengaluru and Hyderabad offices, which handle significant portions of the design pipeline, stand to see expanded roles as the customer roster grows.

The implications ripple outward. Indian semiconductor talent — concentrated at Broadcom, Qualcomm, AMD, and Intel — is increasingly the workforce building the custom silicon that powers American AI. As India's own semiconductor ambitions advance, with Tata Electronics constructing its first fab at Dholera in Gujarat, this ASIC design expertise becomes a strategic asset. Engineers who spend a decade designing custom chips for hyperscalers are exactly the talent pool India needs to build its domestic chip industry.

Broadcom's bet is clear: in a world where every major tech company wants its own AI chip, the company that designs them best wins. Whether the market agrees is another matter entirely.""",
    "category": "technology",
    "status": "review",
    "is_editorial": False,
    "vertical": "technology",
    "image_url": "https://images.pexels.com/photos/37052613/pexels-photo-37052613.jpeg",
    "image_caption": "Detailed close-up of a microprocessor circuit board",
    "image_attribution": "Pexels",
    "sources": json.dumps([
        {"name": "Barron's", "url": "https://www.barrons.com/articles/broadcom-earnings-stock-price-ai-chips"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/broadcom-ai-revenue-2026"},
        {"name": "The Wall Street Journal", "url": "https://www.wsj.com/business/broadcom-ai-infrastructure-fund"}
    ]),
    "diaspora_angle": "Thousands of Indian engineers at Broadcom and rival chipmakers design the custom ASICs powering American AI infrastructure; this expertise is also the talent pipeline India needs for its own semiconductor ambitions at Tata Dholera and beyond",
    "published_at": now_iso,
    "created_at": now_iso,
    "updated_at": now_iso,
})

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 2 — India's EV Market Doubles
# ═══════════════════════════════════════════════════════════════════
articles.append({
    "id": str(uuid.uuid4()),
    "headline": "India's Electric Car Sales Nearly Double in May as Tata and Mahindra Leave Tesla in the Dust",
    "subheadline": "With 26,682 EVs sold in a single month, India's domestic automakers are building an electric future that looks nothing like America's",
    "slug": "india-ev-sales-double-may-2026-tata-mahindra-20260612",
    "body": """India sold 26,682 electric cars in May 2026, an 81.2 percent surge over the same month last year. The numbers, released this week by the Federation of Automobile Dealers Associations, confirm what industry watchers have suspected for months: India's EV transition is accelerating faster than almost anyone predicted, and it is being led entirely by domestic manufacturers.

Tata Motors commanded the field with 10,340 units sold, a 103 percent year-over-year increase that gives it a 39 percent market share. The Nexon EV and the newer Curvv EV have become the default choices for Indian families making their first electric purchase. Mahindra followed with 6,210 units, up 115 percent, driven by the XEV 9e and BE 6e — vehicles that reviewers have praised for punching well above their price point.

## Tesla's 35-Unit Reality Check

The most striking number in the FADA data may be Tesla's. Elon Musk's company, which entered India with considerable fanfare and a starting price north of ₹55 lakh for the Model 3, sold exactly 35 units in May. That figure puts Tesla behind not just Tata and Mahindra but also Maruti Suzuki's eVitara, which moved 1,591 units in its launch month, and well behind BYD (801 units) and Hyundai's Creta Electric (2,218 units).

The gap illustrates a fundamental mismatch. Tesla's vehicles are engineered and priced for American and European buyers. India's EV market is being built around vehicles in the ₹10-25 lakh range — roughly $12,000 to $30,000 — with features calibrated for Indian driving conditions: shorter range but adequate for urban commutes, robust suspension for uneven roads, and compact footprints for congested cities.

## The Infrastructure Catch-Up

The sales surge comes against a backdrop of rapid charging infrastructure expansion. India now has over 18,000 public charging stations, up from roughly 6,000 two years ago. Tata Power, Ather Energy, and ChargeZone are building networks along national highways, though coverage remains patchy outside major metros. The government's FAME III subsidy scheme, which offers up to ₹1.5 lakh per vehicle, has helped push fence-sitters toward electric.

VinFast, the Vietnamese manufacturer, is another emerging player, selling 573 units in May as it builds out its dealership network. The company's aggressive pricing and willingness to invest in Indian manufacturing — it has announced a factory in Tamil Nadu — mirrors the playbook that worked in Southeast Asia.

## What NRIs Are Watching

For the Indian diaspora, the EV numbers carry both investment and personal significance. Tata Motors is listed on the NSE and BSE, and its stock has responded to the EV momentum. Mahindra's electric vehicle division is reportedly exploring a separate listing. Ather Energy, backed by Hero MotoCorp, filed for its IPO earlier this year and is expected to list before Diwali.

For NRIs considering a return to India — or simply visiting family — the EV landscape is becoming relevant in practical ways. Ride-hailing fleets in Bengaluru, Delhi, and Mumbai are adding electric vehicles at pace. Airport taxi services are transitioning. The experience of being driven in an electric Nexon from Kempegowda Airport to Whitefield is, for many returning NRIs, their first encounter with India's quiet automotive revolution.

Auto-technology venture funding in India reached $7.2 billion between 2021 and 2026, with battery technology, charging networks, and fleet management software attracting the bulk of investment. The sector is creating a new category of technical jobs — battery management systems, power electronics, embedded software — that mirrors the kind of engineering work that drew an earlier generation of Indian talent to Detroit and Silicon Valley.

India's EV story is no longer about policy ambitions or concept cars at auto expos. It is 26,682 vehicles in a single month, mostly built by Indian companies, mostly bought by Indian families, and accelerating.""",
    "category": "technology",
    "status": "review",
    "is_editorial": False,
    "vertical": "technology",
    "image_url": "https://images.pexels.com/photos/24376862/pexels-photo-24376862.jpeg",
    "image_caption": "Electric vehicle charging on a city street",
    "image_attribution": "Pexels",
    "sources": json.dumps([
        {"name": "Rushlane", "url": "https://www.rushlane.com/electric-car-sales-may-2026"},
        {"name": "GaadiWaadi", "url": "https://www.gaadiwaadi.com/ev-sales-india-may-2026"},
        {"name": "Autocar Professional", "url": "https://www.autocarpro.in/india-ev-market-may-2026"}
    ]),
    "diaspora_angle": "NRI investors tracking Tata Motors and Mahindra EV listings on NSE; Ather Energy IPO expected before Diwali; returning NRIs encountering India's electric transition firsthand through ride-hailing fleets and airport taxis",
    "published_at": now_iso,
    "created_at": now_iso,
    "updated_at": now_iso,
})

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 3 — AgniKul Cosmos Cluster Test
# ═══════════════════════════════════════════════════════════════════
articles.append({
    "id": str(uuid.uuid4()),
    "headline": "AgniKul Fires Four 3D-Printed Rocket Engines at Once, and India's Space Startup Race Enters a New Phase",
    "subheadline": "The Chennai startup's successful cluster test — a first for India — demonstrates that 3D-printed propulsion can scale, with a space-based AI data centre launch planned for 2027",
    "slug": "agnikul-3d-printed-rocket-engines-cluster-test-20260612",
    "body": """AgniKul Cosmos lit up four semi-cryogenic rocket engines simultaneously on May 19, making it the first Indian company to successfully conduct a cluster test with 3D-printed propulsion hardware. The test, carried out at the Indian Space Research Organisation's Mahendragiri facility in Tamil Nadu, is a critical milestone toward the startup's goal of offering reliable, low-cost orbital launches by 2027.

Each of the four engines was 3D-printed as a single piece of metal in approximately seven days — a manufacturing process that AgniKul says is 97 percent faster than traditional fabrication methods. The engines use a semi-cryogenic fuel mix of liquid oxygen and kerosene, a combination chosen for its balance of performance and handling simplicity. Firing them together in a cluster configuration proves that the printed hardware can withstand the vibrational and thermal stresses of multi-engine operation, the kind of punishment that has historically required months of hand-tuned assembly and testing.

## From Lab to Launchpad

AgniKul was incubated at IIT Madras and has raised over $50 million, with its valuation now exceeding $500 million. The company's first suborbital launch in 2024 demonstrated a single 3D-printed engine in flight. The cluster test brings it meaningfully closer to its Agnibaan rocket, a small satellite launch vehicle designed to carry payloads up to 300 kilograms to low Earth orbit.

What makes AgniKul's approach distinctive is the radical simplification of manufacturing. A conventional rocket engine consists of hundreds of individually machined components — injectors, combustion chambers, nozzles, cooling channels — assembled over weeks or months. AgniKul prints the entire engine as one monolithic part using selective laser melting, eliminating joints, welds, and assembly errors. The result is faster production, fewer failure points, and dramatically lower costs.

Tamil Nadu's state industrial development corporation, TIDCO, invested ₹25 crore in AgniKul earlier this year, making it the first Indian state government to take an equity stake in a private space startup. The investment signals a shift in how Indian states view the space economy — not as a central government monopoly run through ISRO, but as an industrial sector worth cultivating with local capital and infrastructure.

## The Space-Based Data Centre Bet

AgniKul's ambitions extend beyond launch services. The company announced a partnership with NeevCloud, a Hyderabad-based startup, to develop space-based AI data centres. The concept — placing computing infrastructure in orbit where cooling is essentially free and power can come from solar arrays — targets a launch in 2027. If it works, it could address one of India's most pressing technology bottlenecks: the enormous energy and cooling costs of running AI workloads in a tropical climate.

The idea sounds speculative, but it has attracted serious attention from investors who see terrestrial data centre costs spiraling as AI models grow larger. India's data centre capacity is expected to double by 2028, and the power and water demands of that expansion are already drawing regulatory scrutiny in Maharashtra and Tamil Nadu.

## A Crowded Launchpad

AgniKul is not alone. Skyroot Aerospace, based in Hyderabad, successfully launched its Vikram-S rocket in 2022 and recently signed a memorandum of understanding with Axiom Space for human spaceflight support. Skyroot's new Infinity Campus will house engine testing, satellite integration, and mission control. Pixxel, another IIT alumni venture, is building a hyperspectral imaging satellite constellation. Dhruva Space and Bellatrix Aerospace round out a cohort of Indian space startups that barely existed five years ago.

For the Indian diaspora, particularly the dense network of IIT alumni in Silicon Valley and the US aerospace industry, this is personal. Many of the engineers and scientists at SpaceX, Blue Origin, and NASA's Jet Propulsion Laboratory are Indian-born or of Indian descent. AgniKul's progress suggests that the next generation may not need to move abroad to work on cutting-edge propulsion — the launchpad is being built at home.

India's private space sector processed $350 million in venture investment between 2020 and 2026. The cluster test at Mahendragiri is the kind of hardware milestone that converts investor curiosity into committed capital. Four engines, printed in a week, fired together successfully. The physics works. Now comes the business of making it routine.""",
    "category": "technology",
    "status": "review",
    "is_editorial": False,
    "vertical": "technology",
    "image_url": "https://images.pexels.com/photos/586061/pexels-photo-586061.png",
    "image_caption": "Rocket launch from spaceport against overcast sky",
    "image_attribution": "Pexels",
    "sources": json.dumps([
        {"name": "OfficeChai", "url": "https://officechai.com/stories/agnikul-cosmos-cluster-test-3d-printed-engines"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/agnikul-four-engine-cluster-test"},
        {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/science-environment/agnikul-cosmos-space-startup"}
    ]),
    "diaspora_angle": "IIT alumni network driving India's private space revolution; NRI engineers at SpaceX and NASA watching as launchpad opportunities emerge at home; diaspora investors backing the $350M space startup ecosystem",
    "published_at": now_iso,
    "created_at": now_iso,
    "updated_at": now_iso,
})

# ── Insert ──
url = f"{SUPABASE_URL}/rest/v1/p2_articles"
for a in articles:
    resp = requests.post(url, headers=HEADERS, json=a)
    if resp.status_code in (200, 201):
        row = resp.json()
        if isinstance(row, list):
            row = row[0]
        print(f"✓ Inserted: {row['slug']}  (id={row['id']})")
    else:
        print(f"✗ FAILED [{resp.status_code}]: {a['slug']}")
        print(f"  {resp.text[:300]}")

print(f"\nDone — {len(articles)} articles submitted at {now_iso}")
