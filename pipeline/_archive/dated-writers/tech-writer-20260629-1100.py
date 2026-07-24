#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-29 11:00 PT run"""
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
    # ──────────────────────────────────────────────────────────
    # ARTICLE 1: Apple vs India CCI antitrust
    # ──────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Apple Calls India's Antitrust Case a Copy-Paste Job. A Potential $38 Billion Fine Says Otherwise.",
        "subheadline": "In its sharpest legal volley yet, Apple told India's Competition Commission that its investigators didn't investigate — they just parroted PhonePe and Paytm. The watchdog has heard this before, from Google, and it didn't care.",
        "slug": make_slug("apple-india-cci-antitrust-copy-paste-38-billion"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian-American app developers who build for the App Store face real consequences from CCI's outcome — and NRI investors hold significant Apple stock in a company now making 26% of the world's iPhones in India.",
        "tags": ["apple", "india-regulation", "cci", "app-store", "antitrust", "phonpe", "paytm"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/apple-accuses-india-copy-pasting-rivals-claims-antitrust-investigation-2026-06-29/"},
            {"name": "Reuters (financials submission)", "url": "https://www.reuters.com/technology/apple-agrees-submit-india-financials-long-pending-antitrust-case-2026-06-03/"},
            {"name": "Livemint (Delhi HC order)", "url": "https://www.livemint.com/companies/news/apple-anti-trust-probe-delhi-hc-asks-cci-to-hold-its-order-till-15-july-orders-firm-to-cooperate-11747912994640.html"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Apple_Park.jpg/1280px-Apple_Park.jpg",
        "image_caption": "Apple Park headquarters in Cupertino, California",
        "image_attribution": "Wikimedia Commons",
        "body": """Apple has accused India's top antitrust investigators of building their case with a copy-paste function rather than an actual investigation — and the resulting legal filing, first reported by Reuters on June 29, marks the most combative escalation yet in one of the most consequential tech regulation battles in Asia.

In a submission dated June 25 to the Competition Commission of India, Apple argued that CCI's investigation team did not independently analyse the company's conduct on the App Store. Instead, Apple alleged, the investigators "blindly replicated" claims made by complainants including Walmart-owned PhonePe, Paytm, and Tinder-parent Match Group — companies that stand to benefit from any order forcing Apple to open its payment systems.

"The DG made no effort whatsoever to independently verify or critically assess these statements, often parroting them verbatim," Apple wrote in the regulatory papers reviewed by Reuters.

## The Stakes Are Enormous

The numbers explain Apple's aggression. India's amended Competition Act empowers the CCI to calculate penalties based on a company's *global* turnover — not just its Indian revenue. Apple has separately challenged that law in the Delhi High Court, arguing it could face fines of up to $38 billion if the global standard is applied.

In a partial concession, Apple recently submitted its India-specific financials for fiscal years 2022-24 — a step it had resisted for over two years. The CCI typically uses such data as the baseline for penalty calculations.

A closed-door hearing with all parties is scheduled for July 21.

## The Precedent That Should Worry Cupertino

Apple's "copy-paste" argument is not novel in Indian antitrust proceedings. Google deployed a nearly identical defence in its Android case, accusing the CCI of importing reasoning from European regulators. The Commission's response at the time was blunt: "We have not cut, copy and pasted." Google was subsequently forced to alter how it promoted Android in India.

The CCI has also accused Apple of stalling — and the timeline supports that reading. The case dates back to 2021, when a non-profit called Together We Fight Society filed the original complaint. Apple has resisted submitting evidence, pursued parallel court challenges, and in one episode, successfully forced the CCI to recall and reissue investigation reports after confidential business information was inadvertently shared with other parties.

A Delhi High Court bench led by Chief Justice Devendra Kumar Upadhyaya told Apple in May to "cooperate," while ordering the CCI not to issue a final order before the next hearing on July 15.

## Why This Hits Different for India

The case lands at a peculiar moment in Apple's India relationship. On one hand, the country is becoming indispensable to Apple's supply chain: India is projected to produce 26 percent of the world's iPhones in 2026, up from just 6 percent four years ago, according to Counterpoint Research. Apple has exported iPhones worth $51 billion from India over the past five years.

On the other hand, Apple remains a "minuscule player" by its own admission, holding under 6 percent of India's smartphone market — a market overwhelmingly dominated by Android. That's Apple's core legal argument: it cannot abuse a dominant position it does not hold.

But the CCI's investigation focused specifically on the market for app distribution on iOS — a far narrower definition where Apple's control is effectively total. Every app installed on an iPhone in India passes through Apple's store. Every in-app payment routes through Apple's system. That framing is the same logic that regulators in the EU, the US, Japan, and South Korea have used to challenge Apple.

## The Indian App Developer's Dilemma

For the estimated 500,000-plus developers in India who build for iOS, and for the Indian-American engineers who make up a significant share of Silicon Valley's app economy, the outcome matters concretely. If the CCI orders Apple to allow third-party payment systems — as the EU has already done — Indian fintech companies like PhonePe and Paytm could become direct payment processors within iOS apps, potentially cutting Apple's 15-30 percent commission.

That would reshape the economics of app development in India and provide Indian payment platforms with a foothold they've never had inside Apple's walled garden.

Apple's position is that "forced alterations to Apple's carefully designed App Store could disrupt its integrated business model" and that "the imposition of remedies would create regulatory uncertainty and could deter investments in India's digital economy."

The CCI will weigh those arguments against its own track record of not being swayed by them. When Google warned that regulatory intervention would "stall its growth" in India, the Commission proceeded anyway. Apple, with its $38 billion exposure, has considerably more reason to worry."""
    },

    # ──────────────────────────────────────────────────────────
    # ARTICLE 2: Tata Electronics data breach
    # ──────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "A Ransomware Gang Just Published 630 GB of Apple and Tesla Secrets. They Got Them from Tata.",
        "subheadline": "The World Leaks attack on Tata Electronics exposed manufacturing specs, component designs, and trade secrets belonging to Apple, Tesla, TSMC, and Qualcomm — and puts India's 'Make in India' electronics push under uncomfortable scrutiny.",
        "slug": make_slug("tata-electronics-data-breach-apple-tesla-tsmc-ransomware"),
        "category": "technology",
        "vertical": "cybersecurity",
        "diaspora_angle": "Thousands of Indian-American engineers work at Apple, Tesla, TSMC, and Qualcomm — the companies whose proprietary data was compromised. India's credibility as a trusted manufacturing partner is now directly at stake.",
        "tags": ["cybersecurity", "tata-electronics", "apple", "tesla", "data-breach", "ransomware", "make-in-india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/apple-supplier-tata-tightens-internal-controls-after-data-breach-sources-say-2026-06-26/"},
            {"name": "9to5Mac", "url": "https://9to5mac.com/2026/06/27/apple-working-with-supplier-tata-data-breach/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/tata-electronics-hit-by-cyber-breach-involving-apple-and-tesla-data/"},
            {"name": "The420.in", "url": "https://the420.in/tata-electronics-tightens-internal-security-following-massive-dark-web-data-breach/"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5380603/pexels-photo-5380603.jpeg",
        "image_caption": "Computer monitors displaying code and cybersecurity interfaces in a dark room",
        "image_attribution": "Pexels",
        "body": """The ransomware group called World Leaks didn't bother with subtlety. It dumped more than 200,000 files — 630 gigabytes of data — onto the dark web, claiming it had extracted the lot from Tata Electronics, one of India's most strategically important technology manufacturers. Among the alleged haul: Apple manufacturing specifications, Tesla internal project files, documents marked "TSMC Secret," and Qualcomm component designs watermarked "Confidential — May Contain Trade Secrets."

Tata Electronics confirmed the "cybersecurity incident" in a terse statement, adding that operations remain unaffected. Apple's security team is now working directly with Tata on "near- and long-term measures," according to a person familiar with the matter cited by Reuters. Tesla, TSMC, and Qualcomm have not commented publicly.

What's clear is that the breach has shaken the trust equation underlying one of the decade's biggest industrial shifts: the relocation of global electronics manufacturing to India.

## What Was Leaked

The scope of the alleged breach is staggering, according to Reuters' review of the published data.

Among the Apple-related files: manufacturing specifications, quality inspection standards for iPhone circuit board components, internal communications, and employee passport copies. One document reportedly mapped Apple part numbers to TSMC's internal numbering system, with Apple employees named in the revision history.

The TSMC files included at least 16 folders of purported documents, with one marked "TSMC Secret" containing product reliability test details and component photographs. Qualcomm's contribution to the leak: 23 files and folders, including a 2021 document with mechanical schematics for a power management integrated circuit.

The authenticity of the data could not be independently verified. But the specificity of the file descriptions — part numbers, revision histories, watermarks — suggests something considerably more serious than a fabricated dump.

## Tata's Response

Tata Electronics moved quickly once the breach was detected, restricting remote access to sensitive internal systems across all its facilities. Before the incident, access to tools like purchase order systems was more broadly available; it has now been limited to select employees. Work-from-home arrangements continue, but with significantly tightened security protocols.

The company has hired a global consulting firm to conduct a forensic audit and has reported the incident to both the Indian government and its affected clients. The investigation is ongoing.

"Tata Electronics has hardened access to its sensitive internal systems," a company source told Reuters.

## The 'Make in India' Stress Test

The timing is uncomfortable. India has spent billions positioning itself as an alternative to China for electronics manufacturing. Tata Electronics is central to that strategy — it operates iPhone assembly lines in Karnataka and is building India's first commercial semiconductor fabrication facility in Dholera, Gujarat, an $11 billion venture backed by an ASML partnership signed in May.

Apple, for its part, has gone deep on India. The country now produces approximately 26 percent of the world's iPhones, up from 6 percent just four years ago. Apple has exported $51 billion worth of iPhones from India in the past five years. Foxconn, its other major Indian supplier, just shipped its first iPhones from a new Bengaluru factory.

A breach of this magnitude at a key supplier doesn't just expose files — it exposes a vulnerability in the argument that India can handle the security demands of hosting the world's most valuable intellectual property. It's the kind of incident that supply chain security reviewers at Apple, Tesla, and their peers will study carefully when deciding where to place the next tranche of manufacturing.

## The Cybersecurity Gap

India's cybersecurity infrastructure has not kept pace with its manufacturing ambitions. The Indian Computer Emergency Response Team (CERT-In) issued 1.2 million threat alerts in 2025, but the country's cybersecurity workforce remains significantly undersized relative to the scale of its digital economy. Ransomware attacks on Indian organisations more than doubled between 2023 and 2025, according to industry estimates, and the targeting of supply chain companies — rather than their end clients — has become a favoured tactic.

World Leaks, the group claiming responsibility, is a relatively new entrant to the ransomware landscape but has established a pattern of targeting manufacturers and extracting data before attempting extortion.

## What NRIs Should Watch

For the Indian-American professionals who make up a substantial share of the engineering workforce at Apple, Tesla, TSMC, and Qualcomm, the breach has personal dimensions. Their work — the designs they've contributed to, the specifications they've written — may now be on the dark web because of a security failure thousands of miles away in a supply chain they don't control.

The broader question is whether this incident becomes a one-off embarrassment that Tata and India's security apparatus can learn from, or whether it becomes a data point in a pattern that erodes confidence in India as a manufacturing destination. The answer will depend less on the forensic audit and more on what India's government and corporate sector do next — in regulation, in investment, and in the boring, expensive work of building cybersecurity capacity to match manufacturing ambition.

Apple, at least, is not waiting. Its security team is embedded with Tata, conducting its own analysis of what was compromised. The investigation, as Tata's source put it, is ongoing. For India's electronics manufacturing dream, the verdict will take longer."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
