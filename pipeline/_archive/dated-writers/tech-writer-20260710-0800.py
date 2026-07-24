#!/usr/bin/env python3
"""Tech writer — 2026-07-10 08:00 PDT run. Three articles."""

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


articles = [
    # ─────────────────────────────────────────────
    # ARTICLE 1: India scraps import duties on electronics parts
    # ─────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Scrapped Import Duties on Key Smartphone Parts. Apple and Xiaomi Stand to Gain.",
        "subheadline": "New Delhi removed the 5–7.5 per cent levies on wireless charging modules, lithium-ion cells and display components, pushing its electronics manufacturing target to $500 billion by 2030.",
        "slug": make_slug("india-scraps-import-duty-smartphone-electronics-apple"),
        "category": "technology",
        "vertical": "manufacturing",
        "diaspora_angle": "NRI investors tracking Make in India should watch this closely — the tariff cuts strengthen the investment case for Apple's India supply chain, Indian battery startups and the broader electronics manufacturing complex.",
        "tags": ["apple", "xiaomi", "make-in-india", "electronics-manufacturing", "import-duty", "smartphones"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/india-removes-import-duty-some-electronics-smartphone-parts-2026-07-09/"},
            {"name": "Grant Thornton Bharat (via Reuters)", "url": "https://www.reuters.com/technology/india-removes-import-duty-some-electronics-smartphone-parts-2026-07-09/"},
            {"name": "Counterpoint Research", "url": "https://www.counterpointresearch.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5554948/pexels-photo-5554948.jpeg",
        "image_caption": "A smartphone assembly line inside an electronics manufacturing facility",
        "image_attribution": "Pexels",
        "body": """India has eliminated import duties on a batch of components critical to smartphone and electronics manufacturing, in a move that directly benefits Apple, Xiaomi and the constellation of contract manufacturers building devices on Indian soil.

The government scrapped levies of 5 per cent and 7.5 per cent on parts including wireless charging modules for mobile phones, display panels used in medical devices and automobiles, and lithium-ion cells — the building blocks of every rechargeable battery from an iPhone to an electric scooter. The exemption runs until March 2029, giving manufacturers a four-year window to lock in lower input costs.

## Why It Matters for India's Manufacturing Bet

The tariff cut is the latest in a series of policy signals aimed at pulling global electronics supply chains toward India and away from China. New Delhi has set a target of $500 billion in electronics output by fiscal year 2030 — roughly nine times its 2018 level. Smartphone production alone surged 28-fold over the past decade to ₹5.45 trillion ($57 billion) in the year ended March 2025.

"This should boost cost competitiveness, domestic value addition and localisation of high-value smartphone and electronics manufacturing," said Manoj Mishra, a partner at Grant Thornton Bharat.

For Apple, the stakes are especially large. India now supplies 71 per cent of all iPhones sold in the United States, up from 31 per cent a year earlier, according to Counterpoint Research. Foxconn's Indian plants are running at scale, and Tata Electronics is ramping up assembly in Hosur, Tamil Nadu. Removing duties on wireless charging parts and display components lowers input costs for these factories at a moment when Apple is under pressure from U.S. tariffs on Chinese goods.

Xiaomi, which dominates India's smartphone market by volume, also stands to gain. The company assembles the bulk of its devices locally, but still imports specialised components. Lower levies on lithium-ion cells could reduce battery costs across Xiaomi's Indian lineup.

## The Lithium-Ion Cell Angle

The exemption on lithium-ion cell manufacturing equipment may be the most consequential item on the list. India has been trying to build a domestic battery supply chain to support both consumer electronics and electric vehicles. Today, nearly all lithium-ion cells used in Indian devices are imported from China, South Korea or Japan. Zero import duty on cell manufacturing equipment could spur companies to set up cell production lines in India — closing one of the last major gaps in the country's electronics value chain.

## The Diaspora Investment Case

For NRI investors, the tariff cuts reinforce a structural thesis. India's electronics manufacturing sector has moved from a policy aspiration to a production reality. Apple's India revenue crossed $12 billion in the last fiscal year. Tata Electronics, Dixon Technologies, Amber Enterprises and a dozen other listed and unlisted manufacturers are riding the wave.

The cuts also strengthen India's pitch against Vietnam, which had been gaining ground as an alternative to China for companies looking to diversify. With lower input costs and the Production-Linked Incentive scheme still active, India is making it harder for manufacturers to justify going elsewhere.

The question is no longer whether India can build phones at scale. It is whether the country can move up the value chain — from assembling finished devices to producing the chips, batteries and advanced components that go inside them. These tariff cuts suggest New Delhi is betting the answer is yes."""
    },

    # ─────────────────────────────────────────────
    # ARTICLE 2: WhatsApp username freeze + Kunal Shah
    # ─────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "WhatsApp's New Indian-Born Chief Faces His First Test. Delhi Just Froze His Biggest Feature.",
        "subheadline": "India ordered Meta to halt WhatsApp's username feature over fraud concerns — weeks after appointing CRED founder Kunal Shah to lead the app and investing $900 million in his startup.",
        "slug": make_slug("whatsapp-kunal-shah-username-india-freeze-meta"),
        "category": "technology",
        "vertical": "regulation",
        "diaspora_angle": "The standoff between Meta and New Delhi is a live case study in how India regulates tech products used by half a billion people — and what happens when a diaspora-connected founder takes the wheel of a global platform.",
        "tags": ["whatsapp", "meta", "kunal-shah", "cred", "india-regulation", "meity", "digital-fraud"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-file-whatsapps-ambitions-hit-resistance-2026-07-07/"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/23/whatsapp-gets-new-chief-as-meta-taps-indias-cred-founder-kunal-shah-and-invests-900m-in-startup/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"},
            {"name": "PTI (via Inshorts)", "url": "https://inshorts.com/"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/83/Kunal_Shah_in_FreeCharge_T-Shirt_%28cropped%29.jpg",
        "image_caption": "Kunal Shah, the CRED founder appointed as WhatsApp's new global head",
        "image_attribution": "Wikimedia Commons",
        "body": """Kunal Shah has barely settled into his new job as WhatsApp's global chief, and he already has a crisis on his desk — in the very market that made him valuable enough for Meta to pay $900 million to get him.

India's Ministry of Electronics and Information Technology issued a formal notice to Meta on July 1, ordering WhatsApp to explain its proposed username feature and to freeze the rollout until government consultations are complete. The feature, announced on June 29, would let users message each other using unique handles instead of phone numbers — a design familiar from Telegram, Signal and Instagram, but one that New Delhi views as a potential accelerant for online fraud.

## The Government's Concern

The ministry's objections are blunt. Usernames, officials argue, could make it easier for scammers to hide behind fresh identities, widening the risks of phishing, impersonation and so-called "digital arrest" scams — a peculiarly Indian phenomenon in which fraudsters impersonate police officers on video calls to extort money. A June home ministry report had already flagged anonymity tools as a growing vector for cybercrime and the sharing of illegal content.

"Usernames that resemble banks, government agencies or individual names could make spoofing easier," the ministry warned, adding that the feature would weaken the link between a message and a verified phone number — a link that Indian law enforcement considers essential for traceability.

WhatsApp responded on July 9, and the government is now examining its reply. Telegram and Signal, which received similar notices over their own username features, have not yet responded.

## The Kunal Shah Dimension

The timing is awkward. Meta announced Shah's appointment as WhatsApp's global head in late June, alongside a $900 million investment in his fintech startup CRED that valued the company at $4.5 billion. The deal was widely read as Meta's bid to crack India's payments and commerce market — WhatsApp's biggest user base, with more than 500 million people, but one where the app has struggled to turn messaging dominance into meaningful revenue.

Shah built CRED from scratch with $1 million of personal capital in 2018, growing it to 17 million members and roughly $325 million in annual revenue across payments, lending, insurance and wealth management. He recorded CRED's first profitable quarter this year. Miten Sampat, who led strategy and finance, has stepped in as interim CEO.

Analysts saw the appointment as a signal that Meta was ready to get serious about India. Shah is based in India, knows the regulatory landscape, and understands the Indian consumer at a level that few executives at Meta's Menlo Park headquarters can match.

But the username freeze suggests the regulatory landscape is not ready for him. India's IT ministry has spent the past year tightening its grip on messaging platforms, treating product design choices not as feature updates but as public-safety decisions. The username feature, which WhatsApp positioned as a privacy enhancement, landed squarely in regulators' crosshairs.

## What Comes Next

Meta has assured the government it will not launch usernames in India while discussions continue. If Meta's July 9 submission does not satisfy officials, the feature could be blocked in India indefinitely.

For Shah, the episode is a preview of the job ahead. WhatsApp's ambitions in India — business messaging, payments, commerce — all require regulatory goodwill. His first task is not to build a new product. It is to keep the government from blocking one."""
    },

    # ─────────────────────────────────────────────
    # ARTICLE 3: India's dedicated AI law
    # ─────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "India Is Drafting Its First AI Law. Chatbots Get a Pass. Banks and Hospitals Do Not.",
        "subheadline": "New Delhi is preparing a risk-based statute that would classify AI systems by danger level and give the government emergency powers to shut them down — a sharp reversal from its hands-off stance eight months ago.",
        "slug": make_slug("india-ai-law-risk-based-regulation-chatbots-banks"),
        "category": "technology",
        "vertical": "regulation",
        "diaspora_angle": "Indian AI founders, NRI investors in Indian tech, and diaspora engineers building AI products for the Indian market all need to understand this incoming regulatory framework — it could determine which AI businesses can operate freely and which face compliance costs that rival the EU's.",
        "tags": ["ai-regulation", "india", "meity", "artificial-intelligence", "deepfakes", "ai-governance"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Communications Today", "url": "https://communicationstoday.co.in/india-moves-toward-a-dedicated-ai-law/"},
            {"name": "Economic Times (via Communications Today)", "url": "https://communicationstoday.co.in/india-moves-toward-a-dedicated-ai-law/"},
            {"name": "Atlantic Council", "url": "https://www.atlanticcouncil.org/in-depth-research-reports/issue-brief/indias-ai-playbook-from-talent-incubator-to-ai-leader/"},
            {"name": "Carnegie Endowment for International Peace", "url": "https://carnegieendowment.org/research/2026/06/indias-advance-on-ai-regulation"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8386440/pexels-photo-8386440.jpeg",
        "image_caption": "Digital network visualization representing artificial intelligence infrastructure",
        "image_attribution": "Pexels",
        "body": """Eight months ago, India's position on AI regulation was clear: existing laws were sufficient, and a standalone statute was not immediately necessary. That position is now dead.

An official told the Economic Times on July 6 that New Delhi is preparing a dedicated, risk-based law to govern artificial intelligence — a framework that would classify AI systems into tiers based on the danger they pose and impose obligations accordingly. Low-risk tools such as chatbots, productivity software and recommendation engines would face minimal rules. High-risk applications deployed in banking, finance and healthcare would be held to significantly stricter requirements.

The draft is also expected to include emergency powers allowing the government to direct companies to shut down AI systems or disclose their technical details during a crisis. No bill, consultation paper or timeline has been released yet.

## A Sharp Reversal

The shift is notable because of how recently India took the opposite view. In November 2025, the Ministry of Electronics and Information Technology published its India AI Governance Guidelines, which explicitly argued that a dedicated AI statute was not yet required. The document leaned toward industry self-regulation and sector-specific guidance — a posture closer to the United States than to the European Union.

What changed? Two things. First, the rapid proliferation of generative AI tools across Indian banking, insurance and government services created risks that voluntary guidelines struggled to address. Second, the deepfake crisis. India saw a wave of AI-generated impersonation content in late 2025 and early 2026, prompting MeitY to amend the IT Rules in February 2026. Platforms must now label AI-generated content, detect and flag synthetic media, and take down unlawful material within three hours — with a two-hour window for non-consensual deepfakes.

Together, the IT Rules amendment and the forthcoming AI law represent a two-track approach: an immediate crackdown on synthetic content, and a broader structural framework for governing AI across the economy.

## What the Risk Tiers Could Look Like

India has not published the proposed classification system, but the contours are already visible. The Atlantic Council, in an issue brief published on July 7, noted that India has adopted a "use-case-driven AI strategy" focused on deploying AI across education, healthcare, energy, agriculture and financial services. A risk-based law would likely follow the same logic: regulate AI based on where it is used, not on the technology itself.

The Carnegie Endowment for International Peace, in a separate analysis, found that Indian industry broadly supports a two-level approach — voluntary self-regulation for most AI applications, with bespoke rules and compliance requirements for high-risk use cases. Civil society groups, however, have pushed back against industry self-regulation, calling the argument that rules stifle innovation a "convenient oversimplification."

The EU AI Act, which India is watching closely, classifies AI into four risk tiers: unacceptable, high-risk, limited-risk and minimal-risk. India's version is expected to be less prescriptive — officials have repeatedly said they want to avoid the compliance burden that European companies face — but the inclusion of emergency shutdown powers suggests the government wants more teeth than a set of voluntary principles.

## What This Means for Indian AI Companies

For startups like Sarvam AI, which just became India's newest AI unicorn with a $234 million Series B, the law could create a two-speed market. Enterprise AI products deployed in regulated sectors — banking, insurance, defence, healthcare — would need to pass compliance thresholds that consumer-facing chatbots would not. The cost of compliance could become a moat for well-funded startups and a barrier for smaller ones.

IT services giants — TCS, Infosys, HCL Tech, Wipro — would face a different calculus. Their AI consulting and deployment businesses serve clients in exactly the sectors likely to be classified as high-risk. Compliance expertise could become a billable service line. But if the rules are too onerous, clients may slow AI adoption rather than accelerate it.

## The NRI Angle

For Indian engineers at Google, Microsoft and Meta who are building AI products with Indian users in mind, the law adds a layer of regulatory complexity that did not exist six months ago. For NRI investors funding Indian AI startups, it introduces a new variable in due diligence. And for diaspora founders contemplating a return to India to build AI businesses, it changes the risk calculus — though not necessarily for the worse. Clear rules, even strict ones, are often preferable to regulatory ambiguity.

India's AI law is still in draft. But the direction is unmistakable: the era of self-regulation is ending, and what replaces it will shape the next decade of Indian AI."""
    },
]


for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
