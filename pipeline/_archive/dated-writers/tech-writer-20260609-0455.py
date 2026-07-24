#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-09 04:55 PDT run"""
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
# Article 1: Sriram Krishnan Leaving White House AI Role
# ─────────────────────────────────────────────────────────

article1_body = """Sriram Krishnan, the Chennai-born technologist who spent the last 18 months as the White House's senior policy adviser on artificial intelligence, announced over the weekend that he will leave his post at the end of June. His departure closes one of the most consequential chapters of Indian-American influence on US technology policy — and opens a question about who fills the vacuum.

Krishnan's farewell, posted on X on Saturday, was calibrated for maximum Silicon Valley pathos. "It is hard to express how big a privilege it has been to serve the American people," he wrote, before rattling off his resume of accomplishments: the American AI Action Plan, a national AI policy framework, and the agreements that gave Washington early access to frontier models from Google, Microsoft, and xAI before public release.

x-official:https://x.com/sriramk/status/2063302213926105273

David Sacks, the White House AI and crypto czar turned co-chair of the President's Council of Advisors on Science and Technology, called Krishnan's skillset "genuinely unique: a rare combination of deep technical fluency in AI, sharp policy instincts, exceptional strategic thinking, and true diplomatic talent." The White House confirmed that Krishnan will remain connected to the administration's AI efforts as an outside adviser.

## The Architect of 'AI Dominance'

Before his government stint, Krishnan's trajectory read like a textbook Silicon Valley success story, IIT Bombay-flavoured. He built products at Microsoft (Windows Azure), Facebook, Twitter, and Snap before joining Andreessen Horowitz, one of the Valley's most powerful venture firms. He gained broader visibility as part of Elon Musk's transition team after the Twitter acquisition.

In Washington, Krishnan helped steer an administration that explicitly framed AI policy around acceleration rather than regulation. The AI Action Plan he championed prioritised data centre construction and market-driven innovation over the guardrails favoured by the previous administration. More recently, he was involved in a new executive order seeking pre-release access to frontier AI models — a policy that walks the line between national security prudence and industry co-optation.

## Why NRIs Should Pay Attention

Krishnan's role represented something unusual: an Indian-American technologist shaping not just products but the regulatory architecture around the most consequential technology of the decade. His departure comes at a moment when AI policy is becoming increasingly geopolitical. The $100,000 supplemental fee on new H-1B petitions, the ongoing chip export controls affecting India's semiconductor ambitions, and the Trump administration's push for government equity stakes in AI companies all intersect with the diaspora's professional and investment interests.

For the thousands of Indian engineers at Google, Microsoft, and Meta whose daily work is directly shaped by the AI Action Plan's deregulatory approach, Krishnan's exit raises practical questions. Will the next adviser maintain the same pro-acceleration stance? Will the relationships Krishnan built with Indian-origin tech leaders — Sundar Pichai, Satya Nadella — carry over?

Krishnan says he plans to take a break before "working on helping tackle some of the large challenges facing America on AI," hinting at institution-building efforts around energy, data centres, and global AI access. For a 42-year-old who has already shaped products used by billions and policies affecting trillions in economic value, the next act may matter even more than the last."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Sriram Krishnan Is Leaving the White House. He Helped Write America's AI Playbook.",
    "subheadline": "The Chennai-born technologist spent 18 months as the most influential Indian-American voice in US AI policy. His departure leaves a hole at the intersection of Silicon Valley and Washington.",
    "slug": make_slug("sriram-krishnan-white-house-ai-adviser-departure"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Krishnan's White House role gave Indian-Americans unprecedented influence over AI policy affecting H-1B workers, chip exports, and the regulatory environment at companies where thousands of NRIs work. His exit raises questions about continued diaspora influence on US tech policy.",
    "tags": ["ai-policy", "white-house", "sriram-krishnan", "indian-american", "silicon-valley"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/08/sriram-krishnan-is-leaving-his-role-as-white-house-ai-advisor/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/white-house-ai-adviser-sriram-krishnan-to-step-down-at-end-of-june/article69669041.ece"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy-and-policy/who-is-sriram-krishnan-the-white-house-ai-adviser-set-to-step-down-in-june"},
        {"name": "PYMNTS", "url": "https://www.pymnts.com/artificial-intelligence-2/2026/trump-ai-advisor-sriram-krishnan-departs/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/da/MS200024.jpg",
    "image_caption": "Sriram Krishnan, outgoing White House senior policy adviser on artificial intelligence",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body
}


# ─────────────────────────────────────────────────────────
# Article 2: TCS Launches GVIC for AI-Native GCCs
# ─────────────────────────────────────────────────────────

article2_body = """India's largest IT services company just made a bet that sounds, at first, like a company building its own replacement. Tata Consultancy Services on Monday launched the Global Value & Innovation Centres (GVIC) Business Unit — a dedicated operation to help enterprises build, scale, and transform their in-house technology centres in India and beyond. In other words, TCS is now formally in the business of constructing the very Global Capability Centres that have been poaching its talent and eating its margins for the past five years.

x-official:https://x.com/TCS/status/2064306331037958520

"With TCS GVIC, we are bringing together TCS' deep experience across the GCC lifecycle with our strengths in AI, engineering, talent and operations," said K. Krithivasan, CEO and Managing Director of TCS, in language that carefully avoided acknowledging the existential tension at the heart of the announcement.

## The Numbers That Forced the Pivot

The maths behind the GVIC launch are brutal for the traditional outsourcing model. India now hosts over 1,800 GCCs employing nearly two million professionals, up from 1,450 in 2022. Those centres added 320,000 workers since FY22 — nearly matching the 350,000 added by the entire IT services industry. GCCs now pay 15-25 per cent more than IT services firms for standard engineering roles, and 30-40 per cent premiums for AI and cloud specialists. The talent drain is visible in TCS's own numbers: the company shed roughly 12,000 mid-to-senior employees in 2025, citing "skill mismatch."

The GVIC unit, led by Soumen Roy — a 30-year TCS veteran who most recently ran TCS Canada — will offer services across the full GCC lifecycle: strategy, setup, operations, and AI transformation. The unit bundles TCS's proprietary platforms, including TCS COIN and TCS Pace, with what it calls a "Human + AI Operating Model."

## If You Can't Beat Them, Build Them

The strategic logic is counterintuitive but sound. Multinational corporations are going to build GCCs in India regardless — the cost advantages, talent pool, and time-zone coverage make it inevitable. JPMorgan, Barclays, AWS, Dell, and Capgemini all run major India operations. Over 120 new GCCs were established in India since 2023, with Hyderabad emerging as the fastest-growing destination.

Rather than lose revenue to in-housing, TCS is positioning itself as the premium builder and operator of these centres. The company already works with over 150 enterprises on GCC-related engagements. The GVIC launch formalises what was previously scattered across multiple business units.

## What It Means for Indian Tech Workers

For the approximately 600,000 TCS employees in India and the millions more across the IT services sector, the GVIC signals a structural shift in what career growth looks like. The traditional progression — join TCS or Infosys, rotate across client projects, aim for an onsite posting — is being supplemented by a new path: work inside a GCC that TCS itself built and manages.

GCCs are hiring four times faster than IT services firms, according to Nasscom, with AI engineering, data science, cybersecurity, and cloud architecture in highest demand. TCS's bet is that by becoming the default GCC builder, it can capture the services revenue that flows around these centres — consulting, managed operations, AI integration — even as the centres themselves hire directly.

The announcement also coincided with TCS winning a multimillion-euro deal from Canada Life to modernise IT infrastructure across Europe, reinforcing that the traditional large-deal engine remains healthy even as the company diversifies.

For NRI tech professionals considering a return to India or evaluating career options, the GCC boom represents an increasingly attractive proposition: multinational work, Indian location, salaries that compete with — and sometimes exceed — IT services benchmarking. TCS just decided it would rather be the architect than the bystander."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "TCS Is Now Building the Offices That Steal Its Engineers. That's the Point.",
    "subheadline": "India's largest IT company launches a dedicated business unit to help multinationals build AI-native Global Capability Centres — the same centres that have been draining its talent pool for years.",
    "slug": make_slug("tcs-gvic-ai-native-gcc-business-unit-launch"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "GCCs are reshaping Indian tech careers — paying 15-40% more than traditional IT services, hiring 4x faster, and offering multinational work without leaving India. For NRIs evaluating return-to-India options, TCS's pivot signals that the future of Indian tech employment is inside GCCs, not servicing them.",
    "tags": ["tcs", "gcc", "global-capability-centres", "indian-it", "ai-transformation"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/tcs-launches-dedicated-business-to-build-ai-native-global-capability-centres/article69670208.ece"},
        {"name": "AInvest", "url": "https://www.ainvest.com/news/tcs-launches-dedicated-business-unit-to-help-enterprises-build-ai-native-global-capability-centres/"},
        {"name": "ScanX", "url": "https://scanx.trade/news/tcs-launches-new-business-unit-to-help-enterprises-build-ai-native-gccs/"},
        {"name": "Nasscom Community", "url": "https://community.nasscom.in/communities/gcc/leader-talk-global-capability-centres-2026-redefining-gccservice-provider-partnerships"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/TCS_SIPCOT_Building.jpg/3840px-TCS_SIPCOT_Building.jpg",
    "image_caption": "TCS SIPCOT IT Park in Chennai, headquarters of India's largest IT services company",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body
}


# ─────────────────────────────────────────────────────────
# Article 3: Tim Cook's Last WWDC — Apple's India Bet Under a New CEO
# ─────────────────────────────────────────────────────────

article3_body = """Tim Cook stood on stage at Apple Park on Monday evening for the last time as CEO, delivered a standing ovation-worthy farewell, and handed the company its biggest AI upgrade in a decade. But the real story for Indian Americans was not Siri's long-overdue resurrection. It was the quiet question hovering over every announcement: what happens to Apple's India strategy when John Ternus takes over on 1 September?

Cook's 15-year tenure transformed Apple from a $350 billion company into a $4.5 trillion empire — and in the process, turned India from an afterthought into a manufacturing cornerstone. Under his watch, iPhone production in India grew from zero to roughly 20 per cent of global output. Foxconn's factory in Tamil Nadu and Tata Electronics' expanding operations now assemble $22 billion worth of iPhones annually. India exported approximately ₹1.5 trillion in iPhones in FY2024-25, with the United States as the top destination.

Cook was "over the moon excited" about India as recently as April, calling out record quarterly revenue from the country on an earnings call. The company is targeting 25 per cent of global iPhone production from India by next year, up from 14 per cent.

## Ternus Inherits an Unfinished India Story

John Ternus, 49, is Apple's current senior vice president of hardware engineering — the man responsible for the physical devices that Indian factories assemble. His appointment signals a board that believes the next decade of competition will be won at the hardware-AI intersection, not the software layer. For India's manufacturing ambitions, a hardware-first CEO could be a net positive.

But the geopolitical context has shifted. Donald Trump reportedly told Cook directly, "I don't want you building in India." Apple responded with a $600 billion US investment pledge and an American Manufacturing Program. Analysts warn that while low-cost assembly in India is secure for now, higher-value manufacturing growth could face headwinds if domestic-content demands harden.

Ternus will also inherit Apple's most ambitious hardware launch in years. A foldable iPhone is expected as early as autumn 2026, meaning his first major product announcement could arrive within weeks of taking the CEO role. If India's factories handle any portion of foldable production, it would represent a new tier of manufacturing complexity — and trust.

## The AI Angle: Siri Finally Speaks Indian

Monday's WWDC keynote revealed Siri AI, a ground-up rebuild of Apple's voice assistant powered by a custom Google Gemini model. The new Siri is conversational, context-aware, and available as a standalone app. It can draft messages, identify food nutrition from photos, and stack multiple requests into a single command.

For Apple's approximately 16 million iPhone users in India, the upgrade arrives with a caveat: Siri AI launches in English only in September, with more languages following. Hindi, Tamil, and other Indian languages — which would unlock the assistant for hundreds of millions — remain on an unstated timeline. (European Union users, meanwhile, will not get Siri AI at all due to Apple's ongoing regulatory dispute.)

Craig Federighi, Apple's software chief, emphasised privacy as the differentiator: "We believe that there can be no compromise with privacy in AI." User data is processed to fulfil requests and nothing more, with external audits available for verification. For Indian users wary of how their data travels through US and Chinese servers, the promise is meaningful — if Apple delivers on it.

## What NRIs Should Watch

Three metrics will define the Cook-to-Ternus transition for the diaspora:

**Manufacturing depth.** India currently handles final assembly. Ternus's hardware background positions him to push component manufacturing — displays, chip packaging, perhaps even some semiconductor work — into Indian supply chains. Foxconn has pledged $1.5 billion to expand in Tamil Nadu, including a display module plant.

**AI localisation.** Apple Intelligence and Siri AI are English-first. The speed at which Indian languages arrive will determine whether Apple's AI features remain a premium-market novelty or become genuinely useful for the country's billion-plus population.

**Developer ecosystem.** WWDC 2026 drew developers from 65 countries. India's iOS developer community — already the third-largest globally — stands to benefit from new tools like natural-language Shortcuts creation and AI-powered photo editing. But Apple's developer programs in India remain smaller in scale than Google's, and Ternus will need to decide whether to invest more aggressively.

Cook signed off with characteristic restraint: "I truly believe the best is still ahead." For Apple's India story, the next CEO will determine whether that optimism is justified or merely nostalgic."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Tim Cook Said Goodbye at WWDC. His India Legacy Is What Happens Next.",
    "subheadline": "Apple's outgoing CEO turned India into a $22 billion iPhone factory. His successor John Ternus inherits both the promise and the politics.",
    "slug": make_slug("tim-cook-wwdc-farewell-apple-india-ternus-successor"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Cook's tenure made India central to Apple's supply chain ($22B/yr in manufacturing). For NRIs in tech, the CEO transition matters: Ternus's hardware background could deepen India's manufacturing role, while AI localisation timelines affect whether Apple Intelligence works for Indian-language users.",
    "tags": ["apple", "tim-cook", "wwdc-2026", "india-manufacturing", "siri-ai", "john-ternus"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/apple-rolls-out-new-ai-powered-siri-annual-wwdc-2026-06-09/"},
        {"name": "Barron's", "url": "https://www.barrons.com/livecoverage/apple-wwdc-2026/card/tim-cook-ends-wwdc-with-farewell-message"},
        {"name": "TheStreet", "url": "https://www.thestreet.com/technology/tim-cook-final-act-apple-ceo"},
        {"name": "Mint", "url": "https://www.livemint.com/technology/apple-wwdc-2026-updates-ios-27-siri-ai-macos-27"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Tim_Cook_March_2026_%28cropped_2%29.jpg",
    "image_caption": "Tim Cook at his final WWDC keynote as Apple CEO, June 2026",
    "image_attribution": "Wikimedia Commons",
    "body": article3_body
}


# ─────────────────────────────────────────────────────────
# Insert articles
# ─────────────────────────────────────────────────────────

articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
