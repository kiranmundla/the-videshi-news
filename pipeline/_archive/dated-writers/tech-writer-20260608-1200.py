#!/usr/bin/env python3
"""Tech writer batch — 2026-06-08 12:00 UTC"""
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

# ─────────────────────────────────────────────────────────
# Article 1: Sriram Krishnan Exits White House
# ─────────────────────────────────────────────────────────

art1_body = """Sriram Krishnan, the Chennai-born technologist who spent the past eighteen months as the White House's senior policy adviser on artificial intelligence, announced Saturday that he will leave his post at the end of June. His departure closes a chapter that gave the Indian American community an unusually direct line to the machinery shaping how the world's most powerful country regulates its most powerful technology.

"This journey has been the privilege of a lifetime," Krishnan wrote on X, thanking President Donald Trump for the opportunity. "Without his leadership, we would not be leading in the AI race."

## The Architect of America's AI Playbook

Krishnan was not a figurehead appointment. He co-authored the administration's AI Action Plan, a document that prioritised the construction of data centres and the expansion of compute capacity over the regulatory guardrails that characterised the Biden-era approach. He helped draft an executive order that sought to limit the ability of individual states to regulate AI — a move that pleased Silicon Valley but drew pushback from Trump's own populist base.

More recently, Krishnan was involved in the administration's national AI policy framework and represented the United States at international AI summits and state visits. David Sacks, the investor who served as Trump's AI and crypto czar before stepping into a co-chair role on the President's Council of Advisors on Science and Technology, called Krishnan's skills "genuinely unique."

"A rare combination of deep technical fluency in AI, sharp policy instincts, exceptional strategic thinking, and true diplomatic talent," Sacks wrote. "It will be a huge loss for the administration."

## From Chennai to the Situation Room

Krishnan's trajectory reads like a syllabus in diaspora ambition. Born in Chennai, he studied information technology at SRM Engineering College before moving to the United States. He built Facebook's Audience Network, led product at Twitter during a period of 20 per cent annual user growth, and was reportedly in contention to become Twitter's CEO after Elon Musk's 2022 acquisition. He then joined Andreessen Horowitz as a general partner, eventually opening the firm's London office.

When Trump tapped him in late 2024, Krishnan became the most senior Indian American voice on AI inside the federal government — a role that carried weight precisely because the community's representation in the companies building these systems vastly outstrips its representation in the government regulating them.

## What Happens Now

Krishnan said he intends to take a break before "building institutions that help tackle some of the large challenges facing America on AI." He will continue as an outside adviser to the White House.

His departure arrives at a pivotal moment. The administration last week released an executive order directing federal agencies to ask leading AI developers to voluntarily submit their most capable models for government cybersecurity tests. Trump has also floated the idea of the U.S. government taking equity stakes in AI companies — a concept that would have seemed radical twelve months ago.

For the Indian American tech community, Krishnan's exit raises a practical question: who fills the vacuum? The diaspora's influence in Silicon Valley is structural — Indians lead Alphabet, Microsoft, Adobe, IBM, Palo Alto Networks, and a half-dozen other major companies. Its influence in Washington is still personal, dependent on individuals who happen to cross over. Krishnan made the crossing. Whether the bridge outlasts him is an open question."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Sriram Krishnan Is Leaving the White House. He Shaped Every AI Policy That Matters.",
    "subheadline": "The Chennai-born architect of America's AI Action Plan steps down after 18 months, leaving the Indian American tech community without its most powerful voice in Washington.",
    "slug": make_slug("sriram-krishnan-white-house-ai-adviser-exit"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Krishnan was the most senior Indian American voice on AI policy in the federal government. His exit highlights the gap between the diaspora's enormous corporate influence in Silicon Valley and its still-fragile presence in Washington's policy apparatus.",
    "tags": ["ai-policy", "indian-diaspora", "white-house", "sriram-krishnan", "silicon-valley"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/07/sriram-krishnan-is-leaving-his-role-as-white-house-ai-advisor/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/white-house-ai-policy-adviser-krishnan-leave-position-2026-06-07/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/white-house-ai-adviser-sriram-krishnan-to-step-down-at-end-of-june/article69661234.ece"},
        {"name": "IANS via LatestLY", "url": "https://www.latestly.com/agency-news/white-house-ai-adviser-sriram-krishnan-announces-exit-credits-donald-trump-for-americas-ai-leadership-6620811.html"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/da/MS200024.jpg",
    "image_caption": "Sriram Krishnan, former White House AI policy adviser",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body
}

# ─────────────────────────────────────────────────────────
# Article 2: T-Mobile Hyderabad GCC
# ─────────────────────────────────────────────────────────

art2_body = """T-Mobile opened a 250,000-square-foot Global Capability Centre in Hyderabad on June 4 and plans to hire nearly 1,000 engineers by 2027. The announcement would be unremarkable — another American company chasing Indian talent — were it not for the timing. The telecom giant has spent much of 2026 laying off workers across the United States.

The juxtaposition has drawn pointed commentary. PhoneArena bluntly headlined the story: "T-Mobile will hire from India after layoffs in the US." T-Mobile's response was carefully worded: the Hyderabad team, it said, was "converted from an existing team of long-term contractors and vendors" and does not represent a shift of US roles to India.

## The Numbers Tell a Different Story

T-Mobile cut 393 jobs in Washington state earlier this year, affecting analysts, engineers, technicians, directors, and seven vice presidents. The company has also closed retail locations and pushed customers toward its T-Life app for self-service. Under new CEO Srini Gopalan, who replaced Mike Sievert in November 2025, the carrier is explicitly repositioning itself as a "digital-first" company.

Against that backdrop, the Hyderabad GCC will employ engineers working on software development, DevOps, product development, data analytics, and cybersecurity — the same disciplines that figured prominently in the Washington layoff notices. Whether or not specific US roles were "shifted," the talent pipeline is clearly being rerouted.

## India's GCC Boom Is No Longer About Cost Arbitrage

T-Mobile is hardly alone. Meta, Oracle, Amazon, and a procession of Fortune 500 companies have opened Global Capability Centres in India in recent years. Bengaluru alone now hosts over 1,000 GCCs employing approximately 660,000 professionals. Two-thirds of new GCCs choose Bengaluru or Hyderabad, according to a May 2026 Nasscom-Zinnov report.

The nature of the work has shifted. ISG's 2026 GCC Services report found that these centres have "moved well beyond their origins as cost arbitrage vehicles." Companies are now building them as hubs for innovation, AI-led operations, and strategic decision-making. UK-based database firm DSP just launched its first overseas GCC in Bengaluru's Prestige Tech Park, inaugurated with support from the British Deputy High Commission.

"To manage this complexity, companies need leaders who can think globally and execute locally, and India's talent pool is uniquely suited for that," ANSR CEO Lalit Ahuja told CNBC.

## The Diaspora's Uncomfortable Middle

For Indian Americans working in US tech, the GCC boom creates a peculiar tension. On one hand, it validates the skills and work ethic of Indian engineers — the entire model rests on the premise that Hyderabad can do what Bellevue does. On the other hand, it accelerates the very offshoring dynamic that makes H-1B workers nervous about their own positions.

The numbers from Challenger, Gray & Christmas make the anxiety concrete: US employers announced over 97,000 job cuts in May 2026, the highest for the month since the pandemic. AI has overtaken all other reasons cited for layoffs. Technology firms recorded the largest share of workforce reductions.

T-Mobile insists its US tech team "continues to hire." But the 250,000 square feet of office space in Hyderabad, opened the same quarter that hundreds of American workers lost their jobs, tells its own story. The question for the Indian American tech workforce is not whether the work is moving to India — it plainly is, at scale — but whether the bridge between Hyderabad and Silicon Valley creates more opportunities than it displaces."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "T-Mobile Is Hiring 1,000 Engineers in Hyderabad. It Just Laid Off Hundreds in America.",
    "subheadline": "The telecom giant opens a massive new tech hub in India the same quarter it cuts US workers — and it's far from alone. India's GCC boom is reshaping who builds American technology.",
    "slug": make_slug("t-mobile-hyderabad-gcc-us-layoffs-india-tech-hub"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "The GCC boom validates Indian engineering talent but accelerates offshoring that makes H-1B workers in the US anxious. Indian Americans sit uncomfortably at the intersection — their homeland's gain is sometimes their adopted country's loss.",
    "tags": ["gcc", "t-mobile", "hyderabad", "offshoring", "h-1b", "india-tech"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/t-mobile-opens-india-tech-centre-hire-nearly-1000-by-2027-2026-06-04/"},
        {"name": "TheStreet", "url": "https://www.thestreet.com/technology/t-mobiles-hiring-efforts-take-an-unexpected-turn-after-layoffs"},
        {"name": "PhoneArena", "url": "https://www.phonearena.com/news/t-mobile-will-hire-from-india-after-layoffs-in-the-us_id240729"},
        {"name": "Communications Today India", "url": "https://www.communicationstoday.co.in/t-mobile-launches-india-gcc-targets-1000-employees-by-2027/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/36926207/pexels-photo-36926207.jpeg",
    "image_caption": "Glass architecture of a Hyderabad tech park, where T-Mobile's new GCC is located",
    "image_attribution": "Pexels",
    "body": art2_body
}

# ─────────────────────────────────────────────────────────
# Article 3: UPI Lands in Cambodia — 9 Countries and Counting
# ─────────────────────────────────────────────────────────

art3_body = """On June 2, a QR code scanned at a market stall in Phnom Penh settled a payment in Indian rupees, routed through a system designed in Bengaluru, governed by the Reserve Bank of India, and processed without a single credit card, wire transfer, or currency exchange counter. Cambodia became the ninth country where India's Unified Payments Interface works — and for the diaspora, the implications go well beyond convenience.

The India-Cambodia payment linkage, built by NPCI International Payments Limited in partnership with Acleda Bank, covers more than 4.5 million merchants across the country. Indian travellers can use their existing UPI apps — Google Pay, PhonePe, BHIM — to pay by scanning Cambodia's KHQR codes. The amount appears in dirhams, riels, or whatever the local currency is, and debits directly from an Indian bank account. No intermediary. No forex markup (beyond the standard interbank rate). No plastic.

## Nine Countries, 23 MoUs, One Ambition

Cambodia joins Singapore, the UAE, France, Mauritius, Nepal, Bhutan, Qatar, and Sri Lanka on UPI's international map. Days after the Cambodia launch, India also linked UPI to Nepal's National Payments Interface, enabling faster and cheaper cross-border remittances — a corridor that matters enormously to the millions of Nepali workers in India and the Indian families who send money home from the Gulf.

As of February 2026, India has signed memorandums of understanding with 23 countries for sharing or cooperation on the India Stack — the country's digital public infrastructure that includes Aadhaar (identity), DigiLocker (documents), and UPI (payments). The ambition is explicit: make UPI a global standard for real-time payments, the way Visa and Mastercard standardised card payments a generation ago.

## From Payments to Sovereignty

The RBI's Annual Report for 2025-26, released in early June, reframed the digital rupee from a fintech experiment to geopolitical infrastructure. The central bank is now positioning its CBDC — the e-rupee — as a strategic hedge against SWIFT dependency and geopolitical payment risk.

Programmable welfare delivery is already live: pilots in Gujarat, Puducherry, and Chandigarh use programmable e-rupee tokens for food subsidies — tokens redeemable only for eligible commodities at specific shops, eliminating leakage at the point of disbursement. The RBI has signed an MoU with Singapore's MAS and held bilateral discussions with the UAE central bank to operationalise cross-border e-rupee pilots in 2026-27.

The India-UAE CBDC corridor, when live, will reshape how the $20 billion-plus annual India-UAE remittance flow is settled. For NRIs in Dubai, Abu Dhabi, and Sharjah, this is not abstract policy — it is the plumbing through which their money reaches home.

## What This Means for NRIs

The practical upside is already real. An Indian American visiting Singapore can split a dinner bill via Google Pay. A tech worker on vacation in France can pay at a boulangerie without hunting for a currency exchange. A family visiting Nepal can send money to relatives without Western Union fees.

But the strategic upside is larger. India is building a payments infrastructure that its diaspora carries in their pockets, one that works in nine countries today and is contractually committed to expanding further. China's Alipay and WeChat Pay already blanket Southeast Asia. India's UPI is now competing for the same corridors — with the critical difference that UPI is an open, interoperable protocol, not a walled garden controlled by a single company.

For the 32 million Indians living abroad, UPI's expansion means that the financial tether to home is getting shorter, cheaper, and more seamless. It also means India is building soft power through infrastructure — not aid, not diplomacy, but the quiet authority of a payments system that just works."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India's UPI Just Landed in Cambodia. Nine Countries and Counting.",
    "subheadline": "From Phnom Penh to Paris, India's payments protocol is going global — and the RBI wants it to rival SWIFT itself. Here's why NRIs should pay attention.",
    "slug": make_slug("upi-cambodia-nine-countries-india-digital-payments"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "UPI's international expansion directly affects NRIs — cheaper remittances, seamless travel payments, and a growing India-connected financial ecosystem. The India-UAE CBDC corridor will reshape how NRI money reaches home.",
    "tags": ["upi", "digital-payments", "india-stack", "fintech", "rbi", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "ET Edge Insights", "url": "https://etedge-insights.com/latest-updates/upi-goes-global-india-cambodia-enable-real-time-qr-payments/"},
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/uae-joins-singapore-france-mauritius-nepal-sri-lanka-and-other-top-destinations-as-cambodia-becomes-the-9th-country/"},
        {"name": "RBI Annual Report 2025-26 via LinkedIn Analysis", "url": "https://www.linkedin.com/pulse/crypto-fintech-weekly-uae-india-asia-week-ending-7-june-2026/"},
        {"name": "The Asset", "url": "https://www.theasset.com/article/51234/interoperable-digital-payment-systems-bridge-more-markets"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/12935064/pexels-photo-12935064.jpeg",
    "image_caption": "Contactless QR code payment at a retail counter — the same experience UPI now enables in nine countries",
    "image_attribution": "Pexels",
    "body": art3_body
}

# ─────────────────────────────────────────────────────────
# Insert all articles
# ─────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
