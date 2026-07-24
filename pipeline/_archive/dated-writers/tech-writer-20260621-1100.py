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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Data-Centre Pipeline Just Hit 8.33 Gigawatts. The Real Bottleneck Is Power, Not Demand.",
        "subheadline": "A new Knight Frank tally puts India's planned data-centre capacity at five times what is live today, as hyperscalers and AI workloads pour into Mumbai and Hyderabad. For NRIs, it is a rare infrastructure bet hiding in plain sight.",
        "slug": make_slug("india-data-centre-pipeline-8-33-gigawatts-knight-frank-ai-mumbai-hyderabad-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian-American engineers and NRI investors weighing where the next decade of cloud and AI infrastructure money flows now have a concrete number: India's data-centre build-out is one of the largest in the world, and the talent and capital to run it will increasingly be sourced from the diaspora.",
        "tags": ["data-centers", "ai", "indian-tech", "cloud", "infrastructure"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/indias-data-centre-pipeline-reaches-833-gw-on-ai-and-cloud-demand-surge/article69715000.ece"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/news/business/indias-data-centre-pipeline-hits-833-gw-as-ai-demand-reshapes-digital-infra-knight-frank-india"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/cpp-investments-invest-740-million-indias-ctrls-datacenters-2026-06-17/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4508751/pexels-photo-4508751.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=900&w=1600",
        "image_caption": "Server racks and networking equipment inside a modern data centre",
        "image_attribution": "Pexels",
        "body": """India's data-centre industry has spent two years being talked up. This week it got a number that is hard to wave away. The total development pipeline across India's major markets has reached **8.33 gigawatts**, according to a new tally from Knight Frank India — more than five times the country's current live capacity of roughly 1.6 GW.

For a sector that trades in superlatives, the breakdown matters more than the headline. Knight Frank says 0.32 GW is under construction, another 2.92 GW has reached the committed stage, and a striking 5.41 GW — nearly two-thirds of the pipeline — sits in early-stage development. That last figure is the tell. Early-stage capacity is a bet on demand that has not arrived yet, and developers are making it anyway.

## Context & Background

The demand has a name, and it is artificial intelligence. Training and running large models is a brute-force exercise in electricity and cooling, and the hyperscalers — Amazon, Microsoft, Google — have spent the past year racing to localise that compute inside India, partly to serve Indian customers and partly because data-localisation rules increasingly require it. Layered on top is the IndiaAI Mission, the government's push for sovereign compute, which has anchored deals like Yotta's Nvidia Blackwell supercluster near Delhi and L&T's gigawatt-scale ambitions in Chennai and Mumbai.

Mumbai dominates the map, with a 3.75 GW pipeline built on its subsea-cable landings, fibre density and financial-capital gravity. Hyderabad has emerged as the surprise second city at 1.93 GW, courtesy of cheap power and an unusually cooperative state government. Chennai follows at 1.36 GW, leaning on its role as India's gateway for Southeast Asian traffic.

## Current Developments

The money is following the megawatts. This week Canada's CPP Investments committed roughly $740 million to CtrlS Datacenters, taking an 8.2% stake and seeding a joint venture to build campuses across India. Jabil and Adani announced a partnership to manufacture AI-ready data-centre hardware locally, part of Adani's stated plan to spend $100 billion on renewable-powered facilities by 2035. India's data-centre market, by IMARC's estimate, will nearly double to $13.11 billion by 2034.

But the constraint is shifting from capital to electrons. A single gigawatt-scale AI campus built around Nvidia's next-generation Vera Rubin systems could carry an annual power bill north of $1 billion. India's grid, already strained in summer, was not designed for clusters that each draw as much power as a small city. The committed pipeline assumes power-purchase agreements, renewable tie-ups and substations that in many cases do not yet exist. The gap between "early-stage" and "live" is, in practice, the gap between a signed land deal and a reliable megawatt.

## Diaspora Impact

For the Indian diaspora, this is one of the few infrastructure stories with a direct line back to their working lives. Tens of thousands of Indians staff the cloud and AI-infrastructure teams at Amazon, Microsoft and Google in Seattle, the Bay Area and New Jersey — the same teams now deciding where to put capacity. A maturing Indian data-centre market changes the calculus for the engineer who has quietly wondered whether a senior infrastructure role could one day be based in Hyderabad rather than Herndon.

For NRI investors, the appeal is the unglamorous part of the AI trade. Everyone owns Nvidia; far fewer have exposure to the power, real estate and cooling that AI actually runs on. Indian data-centre operators, the REITs forming around them, and the power and cabling suppliers feeding them are a leveraged bet on AI adoption that does not depend on picking which model wins. The risk is equally unglamorous: if the grid cannot keep up, a chunk of that 5.41 GW early-stage pipeline quietly never gets built.

## What's Next

Watch the conversion rate. The number that will matter over the next 18 months is not the 8.33 GW pipeline but how much of the 2.92 GW committed stage actually energises on schedule. Power availability, not investor appetite, is now the gating factor — and it is the one metric the press releases tend to skip."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Carmakers Just Got a Duty-Free Lane Into Britain's EV Market. The Fine Print Is a 15-Year Wait.",
        "subheadline": "The India-UK trade pact opens a quota-based, duty-free path for made-in-India electric cars from Tata, Maruti and Mahindra — but the concessions phase in slowly, and the diaspora is the obvious first customer.",
        "slug": make_slug("india-uk-fta-ev-exports-tata-maruti-mahindra-duty-free-quota-nri-britain"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For the large Indian community in Britain, a made-in-India electric SUV arriving duty-free is both a consumer story and a point of pride — and for NRI investors tracking Tata Motors and Mahindra, it reframes the India-UK FTA as an auto-export thesis, not just a trade headline.",
        "tags": ["ev", "tata-motors", "mahindra", "india-uk-fta", "indian-tech", "mobility"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Business / PTI", "url": "https://www.outlookbusiness.com/industry/indian-passenger-vehicle-makers-eye-opportunity-in-uks-ev-market-via-fta"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/companies/indian-passenger-vehicle-makers-eye-opportunity-in-uks-ev-market-via-fta/article69716000.ece"},
            {"name": "Reuters", "url": "https://www.reuters.com/business/autos-transportation/indias-tata-motor-pv-targets-18-20-market-share-double-digit-margin-2026-06-16/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/TATA_Electric_car_on_road_with_number_plate.jpg/1280px-TATA_Electric_car_on_road_with_number_plate.jpg",
        "image_caption": "A Tata electric car on an Indian road",
        "image_attribution": "Wikimedia Commons",
        "body": """When the India-UK free trade agreement comes into force on July 15, the headlines will be about whisky and textiles. The quieter, longer story is about electric cars — and it gives India's automakers something they have wanted for years: a duty-free lane into a rich, right-hand-drive market.

Maruti Suzuki, Mahindra & Mahindra and Tata Motors are all eyeing the opening, executives told PTI this week. Under the Comprehensive Economic and Trade Agreement (CETA) document released last week, India gets quota-based, duty-free access to Britain's electric, hybrid and hydrogen passenger-car segments. The catch is in the timing.

## Context & Background

Britain is one of the few large markets that drives on the same side of the road as India, which removes an expensive engineering hurdle that has long kept Indian models out of Europe. It is also a market under regulatory pressure to electrify: the UK's zero-emission vehicle mandate required EVs to hit 33% of sales in 2026, and the market is running behind at under 24%. That shortfall is precisely the gap an affordable, made-in-India electric SUV could fill.

Maruti is already testing the water. Its eVITARA has shipped roughly 36,000 units to Europe within nine months of launch, with the UK as the top destination — and that was before any tariff relief. Tata Motors, which owns Jaguar Land Rover and therefore knows the British market intimately, called the framework a "calibrated pathway" for Indian-made EVs.

## Current Developments

The concessions are deliberately gradual. Duty-free access begins only in the **sixth year** of the agreement, split across three price brackets — under £20,000, £20,000-£40,000, and £40,000-£80,000. In year six, just 6,800 units each are allowed in the two cheaper bands and 4,000 in the premium band, totalling 17,600 cars. The quota climbs to a peak of 88,000 units from year 15. Cars priced above £80,000 get no concession at all, which neatly excludes the luxury tier and protects British and German premium brands.

In other words, this is not a flood. It is a metered tap, designed to give Indian manufacturers a foothold without alarming domestic UK industry. For Tata, which this week reiterated a target of 18-20% market share and double-digit margins in its passenger-vehicle business, the UK quota is a useful export valve rather than a transformation.

## Diaspora Impact

The first buyers are almost certainly going to be Indian. Britain's roughly 1.9-million-strong diaspora is concentrated in exactly the suburban, commuter-belt geographies where a sub-£30,000 electric SUV makes sense — and where badge familiarity matters. A Tata or Mahindra EV in a London driveway carries a cultural charge that a Hyundai or MG does not. For first-generation NRIs in particular, buying an Indian-built car that is genuinely competitive on price and range would be a small but real marker of how far Indian manufacturing has come.

For the investor side of the diaspora, the FTA reframes a familiar trade. Tata Motors and Mahindra have been domestic EV plays with a slow-burn export option attached. CETA puts a number and a calendar on that option. It will not move earnings in 2026 or 2027 — the duty relief is years out — but it changes the long-term story from "India sells EVs to Indians" to "India exports EVs to the rich world," which is a different multiple.

## What's Next

The near-term test is whether Maruti, Tata and Mahindra can build right-hand-drive EVs that hit British safety and emissions certification cheaply enough to use the quota when it opens. The FTA gives them the lane. Filling it will depend on charging infrastructure, residual values and whether British buyers — diaspora and otherwise — decide an Indian EV is a bargain or a gamble."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Digital Fraud Rate Is Now Nearly Double the World's. The Weak Point Is the Account You Already Have.",
        "subheadline": "A new TransUnion report pegs India's suspected digital fraud rate at 7.1% versus a 3.8% global average, with account takeovers surging. For NRIs running money across two countries, the exposure is doubled.",
        "slug": make_slug("india-digital-fraud-rate-7-1-percent-transunion-account-takeover-nri-cybersecurity"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "NRIs juggle Indian bank accounts, UPI apps, brokerage logins and remittance services from abroad — a fragmented footprint that account-takeover fraudsters love, making India's spiking fraud rate a direct personal-security problem for the diaspora, not a distant statistic.",
        "tags": ["cybersecurity", "fraud", "fintech", "indian-tech", "upi"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/cybersecurity/cybersecurity-red-flag-india-sees-7-1-digital-fraud-rate-as-account-takeovers-surge"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/cybersecurity/researchers-say-sweeping-hack-campaign-against-fortinet-devices-compromised-2026-06-17/"},
            {"name": "Inc.", "url": "https://www.inc.com/sam-blum/the-surprisingly-simple-way-hackers-just-breached-samsung-oracle-and-accenture/"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5935794/pexels-photo-5935794.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=900&w=1600",
        "image_caption": "A person typing on a laptop, illustrating digital fraud and account-takeover risk",
        "image_attribution": "Pexels",
        "body": """India built the world's most-used real-time payments rail. It is now learning the cost of that scale. A new report from TransUnion puts India's suspected digital fraud rate at **7.1% in 2025** — nearly twice the global average of 3.8% — and warns that the fastest-growing category is the most personal one: account takeovers.

The distinction matters. For years, fraud in India meant fake accounts opened with stolen identities. TransUnion's H1 2026 State of Omnichannel Fraud Report says criminals have shifted to a more efficient target — the accounts people already own, with real transaction histories and saved payment methods. Why build a fake when you can hijack a genuine one?

## Context & Background

The mechanics are mundane, which is what makes them dangerous. Account takeovers typically start with credentials harvested from earlier breaches or phishing, then tested against login pages at scale. India's explosion of UPI apps, digital wallets, broker accounts and e-commerce logins has multiplied the number of doors a fraudster can rattle. UPI alone now processes over 640 million transactions a day, more than Visa handles globally; every one of those is a habit a criminal can try to impersonate.

The vulnerability is not unique to India, and recent global incidents show how basic the failures are. The "FortiBleed" campaign disclosed this month compromised roughly 75,000 Fortinet firewall and VPN devices worldwide — with the US, India and Taiwan worst hit — not through some exotic zero-day, but by guessing and reusing leaked passwords. Security researchers were blunt: the failure was not weak passwords, but the assumption that a password alone was ever enough.

## Current Developments

TransUnion's data lands amid a broader Indian fraud wave. The report flags account logins as among the most common fraud sources, with criminals blending stolen credentials and social engineering to slip past defences. Indian companies are responding with multi-factor authentication and behavioural analytics that watch for the small anomalies — a login from an unusual device, a transfer at an odd hour — that betray a hijacked session. But security teams concede they are adapting to attackers who move faster than governance does.

The 7.1% figure is a national-average alarm bell. It says that for every roughly 14 digital interactions India's fraud systems screen, one looks suspicious — a rate that erodes the trust UPI and India Stack were built to create.

## Diaspora Impact

NRIs are unusually exposed, and not because they are careless. The typical non-resident Indian runs a split financial life: an NRE or NRO bank account in India, a UPI app linked to it, a domestic brokerage or mutual-fund login, remittance services, plus the full stack of accounts in their country of residence. That fragmentation is exactly the surface account-takeover fraud thrives on — more logins, more reused passwords, and crucially, a user who is in a different time zone and may not notice a fraudulent transaction for hours.

The remittance angle sharpens it. Diaspora money flowing into India — for parents, property or investments — moves through precisely the digital channels seeing the highest fraud rates. An NRI who has not logged into an Indian account in weeks is a softer target than a resident transacting daily, because anomalies are harder to spot when there is no baseline of normal activity.

The defensive playbook is unromantic but effective: turn on multi-factor authentication on every Indian financial login, never reuse a password across the India and overseas footprints, and set transaction alerts on NRE/NRO accounts so a hijack surfaces in minutes, not weeks.

## What's Next

Expect India's regulators and the NPCI to lean harder on device-binding, behavioural biometrics and tighter login controls as the fraud rate climbs. But the structural problem — too many accounts, too many reused passwords — sits with users, including the diaspora. The country that taught the world to pay in real time now has to teach itself to log in safely."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
