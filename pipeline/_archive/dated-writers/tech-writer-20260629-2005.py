#!/usr/bin/env python3
"""
Tech writer – replacement article #1 (Apple AI security shift)
Inserts into Supabase with status=review, category=technology, is_editorial=false.
"""

import json, os, re, subprocess, sys
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────
for envf in [
    os.path.expanduser("~/.env.supabase"),
    os.path.expanduser("~/workspace/.env.supabase"),
]:
    if os.path.exists(envf):
        with open(envf) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

# ── article ──────────────────────────────────────────────────────────

ARTICLE = {
    "headline": "Apple Just Broke a Decade-Long Rule Because AI Made Hackers Too Fast",
    "subheadline": "The company is pushing iOS security patches ahead of schedule for the first time, citing AI-driven threats. For India's booming cybersecurity sector and its 500 million smartphone users, the shift hits close to home.",
    "slug": "apple-ios-security-update-ai-cyber-threats-india-cert-in-20260630",
    "category": "technology",
    "vertical": "technology",
    "status": "review",
    "is_editorial": False,
    "score_total": 76,
    "diaspora_angle": "India is Apple's fastest-growing major market and already enforces some of the world's strictest patch timelines through CERT-In. Indian-origin cybersecurity leaders like Palo Alto Networks CEO Nikesh Arora are driving the defensive AI push, while Indian IT services firms are repositioning as cybersecurity providers for global enterprises.",
    "tags": ["Apple", "cybersecurity", "AI threats", "iOS update", "CERT-In", "Five Eyes", "Indian IT", "Nikesh Arora", "Anthropic Mythos"],
    "image_url": "https://images.pexels.com/photos/3949098/pexels-photo-3949098.jpeg",
    "image_caption": "A digital lock icon on a smartphone screen — Apple is racing to close the window between vulnerability disclosure and exploitation.",
    "image_attribution": "Dan Nelson / Pexels",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/apple-says-it-is-releasing-updates-early-response-ai-cybersecurity-concerns-2026-06-29/"},
        {"name": "MacRumors", "url": "https://www.macrumors.com/2026/06/29/ios-26-5-2-vulnerabilities/"},
        {"name": "CNN", "url": "https://www.cnn.com/2026/06/23/world/ai-five-eyes-warning-cyber-threat-intl-hnk/"},
        {"name": "The Register", "url": "https://www.theregister.com/2026/06/27/ai-vulnerability-disclosure/"},
        {"name": "NY Post", "url": "https://nypost.com/2026/06/23/business/ai-could-fuel-severe-cyberattacks-against-governments-businesses-within-months-five-eyes-spy-agencies-warn/"}
    ]),
    "body": """For more than a decade, Apple followed a simple cadence: bundle security fixes into the next numbered iOS release, let developers and testers kick the tyres, then ship it to a billion-plus phones worldwide. If a zero-day wasn't actively being exploited, it could wait.

That rule just died.

On Monday, Apple told Reuters it was pushing a batch of security patches — more than 25 of them — to all users through iOS 26.5.2, well ahead of the broader iOS 26.6 release that would normally carry them. The reason, the company said, was blunt: artificial intelligence is compressing the window between the moment a vulnerability becomes known and the moment someone builds a weapon from it.

"The time between when security fixes were first announced and when they were deployed to customers' phones needed to be compressed," Apple said.

None of the patched flaws had been exploited in the wild. The fixes, mostly targeting WebKit and the kernel, had already been circulating in the 26.6 beta. But Apple decided that the old practice of waiting for the next full release was no longer defensible.

## The warning that preceded it

Apple's shift did not happen in a vacuum. Six days earlier, the Five Eyes intelligence alliance — the United States, United Kingdom, Canada, Australia, and New Zealand — issued one of its starkest warnings yet: AI models capable of overwhelming government and corporate cyber defences are "months, not years" away.

"Frontier AI models are anticipated to exceed current industry expectations, fundamentally transforming both offensive and defensive cyber capabilities," the joint statement read. "Breaches will occur."

The intelligence agencies urged organisations to treat AI-powered attacks as inevitable and to focus not just on prevention but on containment and rapid recovery. The message was aimed at governments and Fortune 500 firms, but its implications ripple through every digital economy on Earth — India's very much included.

## Where India fits

India is already living in the compressed timeline Apple just acknowledged. In 2024, CERT-In — India's national cyber response agency — mandated that organisations report and begin patching confirmed breaches within 12 hours, one of the shortest windows any government has imposed. At the time, it was criticised as unrealistic. Today it looks prescient.

The country's attack surface is enormous and growing. India crossed 500 million smartphone users this year, and Apple's share of that market has been climbing steadily since the company began manufacturing iPhones in Tamil Nadu and Karnataka through partners like Foxconn and Tata Electronics. Every new iPhone sold in India is now a node in the same security ecosystem Apple just decided needed faster updates.

Meanwhile, the Indian cybersecurity industry has become a significant exporter of talent and services. Nikesh Arora, the Lucknow-born CEO of Palo Alto Networks, has spent the past year on an acquisition spree — including the $25 billion CyberArk deal — betting that AI will "break security as we know it." His company now runs at a $12 billion annual revenue rate, and its fastest-growing engineering centre is in Bengaluru.

Indian IT services giants are making similar pivots. TCS, Infosys, and Wipro have all expanded their managed security offerings in the past 18 months, repositioning from back-office IT outsourcing to front-line cyber defence for Western enterprises. The logic is straightforward: if AI compresses the attack cycle, the companies that can respond fastest — across time zones and at scale — win the contracts.

## The Anthropic factor

Underpinning much of this urgency is a quiet revolution in how vulnerabilities are found. Anthropic's Mythos model, used through its Project Glasswing initiative, scanned more than 1,000 open-source projects earlier this year and flagged an estimated 6,200 high or critical-severity vulnerabilities. A cybersecurity firm called Calif used the same model to discover a previously unknown macOS privilege-escalation exploit — the kind of bug that, in the wrong hands, could compromise an entire device.

Apple credited Calif and Anthropic for the discovery in its security notes. But the episode underscored a discomfiting truth: the same AI that finds bugs for defenders finds them for attackers too. The advantage goes to whoever moves first.

Swiss financial regulator FINMA put it plainly: "As hackers move faster, banks must adapt by patching vulnerabilities more rapidly." Replace "banks" with any organisation that stores user data, and the sentence still holds.

## What it means for the diaspora

For the roughly five million Indian Americans who rely on Apple devices for banking, messaging, and authentication, the accelerated patch cycle is a quiet upgrade in personal security. For the tens of thousands of Indian-origin engineers working in cybersecurity across Silicon Valley, Seattle, and Bengaluru, it is a confirmation that their field is moving from back-office function to boardroom priority.

And for India's government, which has been building out its own AI-powered cyber defence infrastructure through the National Cyber Security Coordinator's office, Apple's decision validates a posture New Delhi adopted years ago: in the age of AI, waiting is the riskiest thing you can do.""",
    "published_at": "2026-06-30T06:30:00Z",
}

# ── insert ───────────────────────────────────────────────────────────

def insert_article(art: dict) -> dict:
    payload = json.dumps(art)
    result = subprocess.run(
        [
            "curl", "-s", "-w", "\n%{http_code}",
            "-X", "POST",
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            "-H", f"apikey: {SUPABASE_KEY}",
            "-H", f"Authorization: Bearer {SUPABASE_KEY}",
            "-H", "Content-Type: application/json",
            "-H", "Prefer: return=representation",
            "-d", payload,
        ],
        capture_output=True, text=True,
    )
    lines = result.stdout.strip().rsplit("\n", 1)
    body = lines[0] if len(lines) > 1 else ""
    code = lines[-1].strip()
    return {"status_code": code, "body": body}


print("=" * 60)
print(f"Inserting: {ARTICLE['headline']}")
print(f"Slug:      {ARTICLE['slug']}")
print(f"Category:  {ARTICLE['category']}  |  Status: {ARTICLE['status']}")
print("=" * 60)

resp = insert_article(ARTICLE)
print(f"HTTP {resp['status_code']}")

if resp["status_code"].startswith("2"):
    try:
        data = json.loads(resp["body"])
        if isinstance(data, list) and data:
            print(f"✅ Inserted — id: {data[0].get('id','?')}")
        else:
            print(f"✅ Inserted — response: {resp['body'][:200]}")
    except json.JSONDecodeError:
        print(f"✅ Inserted (raw): {resp['body'][:200]}")
else:
    print(f"❌ FAILED: {resp['body'][:300]}")
