#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-28 17:00 PT run"""

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

# ─────────────────────────────────────────────────────
# ARTICLE 1: India-US Fable 5 diplomacy
# ─────────────────────────────────────────────────────

article1_body = """India's IT Secretary S. Krishnan walked into the Pax Silica Summit in Washington last week carrying a pointed question for his American counterparts: can India actually depend on US-built AI, or is access a privilege that gets yanked without warning?

The question was not theoretical. On 12 June, the US Commerce Department issued an export control directive ordering Anthropic to disable its newly launched Claude Fable 5 and Mythos 5 models for all foreign nationals — including the company's own non-American employees. Within hours, developers across India, Europe, and Asia lost access to what many considered the most capable general-purpose AI model on the market. Indian startups building on Claude's API scrambled for alternatives. TCS, which had just signed an enterprise AI partnership with Anthropic, watched a cornerstone of its next-generation offerings disappear overnight.

Two weeks later, the crisis appears to be resolving. Jacob Helberg, the US Under Secretary for Economic Growth, confirmed that Washington and New Delhi are in "ongoing conversations" about restoring access. "Both sides really understand each other's perspectives," Helberg told reporters on the sidelines of the summit. "Our intention is very much to continue a gradual, measured approach to how we release Anthropic's models in a way that is safe."

Axios reported on Friday that the US government is now close to allowing Anthropic to restore Fable 5 access, potentially as early as this week. The model would return under a new verification framework that distinguishes trusted partners from adversarial actors — a system Anthropic had already been developing when the Commerce Department's directive blindsided it.

## What actually happened

The shutdown traced back to Anthropic's own positioning. The company had built Fable 5 on top of Mythos, an unreleased model so powerful that it could identify zero-day vulnerabilities in every major operating system and browser. Rather than release Mythos publicly, Anthropic ran a controlled pilot called Project Glasswing with about 50 vetted organisations, using the model for defensive cybersecurity. Fable 5 was the consumer-safe version — guardrails intact, designed to revert to an earlier, less capable iteration if anyone tried to use it for hacking or weapons development.

The Commerce Department's directive reportedly cited an instance where those guardrails were bypassed. Whether that jailbreak represented a genuine national security threat or an overreaction by officials unfamiliar with standard AI red-teaming remains contested. Anthropic has disputed the government's characterisation, arguing the action should not have been taken.

## India's diplomatic card

Krishnan's presence at the Pax Silica Summit was itself a statement. India's MeitY secretary does not typically attend US technology summits unless there is a message to deliver. His was blunt: "We sought an understanding of how exactly the US is looking at this particular aspect. If this technology is to be used and made available, we can't have abrupt cutoffs."

The framing was deliberate. India was not asking for special treatment. It was asking whether the US considers India a reliable AI partner — and whether Indian enterprises can build long-term strategies on American AI infrastructure without risk of sudden disconnection.

## The wider scramble

India is not the only country reading this episode as a warning. On Saturday, Austria's State Secretary for Digitalization Alexander Proell wrote to the EU Technology Commissioner proposing that the bloc explore "the strategic establishment and participation of Anthropic within the European Union." The letter argued that Europe cannot afford to be "mere administrators of decisions made elsewhere."

The episode has also strengthened the hand of India's sovereign AI advocates. Anand Mahindra, chairman of Mahindra and Mahindra, wrote in a letter to shareholders published the same week: "Frontier AI is not just a commercial technology. It is a strategic capability, increasingly being shaped by questions of trust, regulation, national interest and sovereignty. India cannot be only a consumer of intelligence built elsewhere."

## What this means for NRIs

For Indian-origin engineers and founders in the US, the Fable 5 episode crystallised an uncomfortable reality: the AI tools they build with at work can be weaponised as diplomatic leverage against the country they come from. An Indian-American developer at a San Francisco startup using Claude's API had uninterrupted access; their colleague on a TCS project in Bengaluru did not.

The near-restoration of Fable 5 eases the immediate crisis. But the deeper question — whether India should build redundancy into its AI stack rather than depend on any single foreign provider — has moved from academic debate to boardroom priority. India's AI Mission has backed 12 startups with over ₹2,194 crore in GPU grants and cash. BharatGen has released Param-2, a 17-billion-parameter model trained from scratch. Tech Mahindra is developing a one-trillion-parameter sovereign LLM.

None of these match Claude or GPT-5.6 in raw capability. But the Fable 5 shutdown demonstrated that capability is meaningless if access can be revoked by a government you did not elect. For India's tech ecosystem, the lesson is clear: use the best available tools, but never build a house on someone else's foundation."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Washington Is About to Unlock Anthropic's Fable 5. India's Quiet Diplomacy Helped.",
    "subheadline": "After two weeks of backdoor negotiations at the Pax Silica Summit, the US is close to restoring access to the AI model it abruptly shut down — and India's IT Secretary forced the conversation.",
    "slug": make_slug("india-pax-silica-anthropic-fable-5-restore-diplomacy"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian developers and IT companies like TCS that were cut off from Claude Fable 5 on June 12 are about to regain access — but the episode has forced a reckoning over whether India can safely build its tech future on American AI platforms.",
    "tags": ["ai", "anthropic", "india-us-relations", "sovereign-ai", "claude", "export-controls", "pax-silica"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Inc42", "url": "https://inc42.com/buzz/india-in-talks-with-us-to-access-anthropics-fable-5-model/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/artificial-intelligence/us-close-allowing-anthropic-restore-fable-5-model-axios-reports-2026-06-27/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/us-says-in-talks-with-india-on-anthropic-fable-model-rollout/article69740123.ece"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/15/anthropic-suspends-access-india-debates-ai-future/"},
        {"name": "Livemint", "url": "https://www.livemint.com/technology/india-must-build-foundational-ai-models-or-risk-becoming-a-mere-consumer-bharatgen-11750959513792.html"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4508751/pexels-photo-4508751.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Server infrastructure in a modern data center — the physical backbone of the AI models at the centre of the US-India access dispute",
    "image_attribution": "Pexels",
    "body": article1_body.strip()
}

# ─────────────────────────────────────────────────────
# ARTICLE 2: India deep tech VC boom
# ─────────────────────────────────────────────────────

article2_body = """For a decade, Indian venture capital had a reliable formula: find a consumer app with hockey-stick growth, fund it until it either IPO'd or immolated, repeat. Zomato, Swiggy, Paytm, CRED — the portfolio of India's top VCs read like a food delivery and fintech catalogue. Hardware was something China made. Defence was something the government funded. Deep tech was something you discussed at conferences and invested in somewhere else.

That is changing, and the numbers are hard to argue with. Indian deep tech startups have raised $1.23 billion in the first half of 2026 alone, according to Tracxn data cited by Accel partner Subrata Mitra in a recent interview. That figure is already approaching the $1.5 billion raised in all of 2025, and closing in on 2024's record of $1.6 billion. The money is going where Indian VCs have historically refused to look: drones, electric aircraft, gas turbines, semiconductor networking, and sovereign AI chips.

Accel, the Silicon Valley firm that backed Facebook and Flipkart, is leading the shift. Its eighth India fund — $650 million, raised in January 2025 — is deploying 10 to 15 per cent of capital into manufacturing and hardware. "It's not a lot, but it is significant," Mitra told Livemint. "Historically, we don't like to allocate more than 20 per cent to one area."

## Who's getting funded

The deals tell the story. Unmannd, an autonomous drone manufacturer, is building inspection and surveillance systems that Indian defence procurement has struggled to source domestically. Sarla Aviation is developing an electric vertical take-off and landing (eVTOL) aircraft — India's answer to Joby Aviation, targeting both urban air mobility and last-mile military logistics. Nabhdrishti Aerospace makes micro gas turbines for power generation and aviation, a category where India currently imports virtually everything.

These are not the kind of startups that scale by acquiring users with discounted biryani deliveries. They require capital-intensive prototyping, regulatory certifications, defence procurement cycles, and years of development before revenue appears. The fact that marquee VCs are willing to wait speaks to a broader confidence that India's industrial and defence ecosystem is ready to absorb domestic deep tech at scale.

Upscale AI, the networking infrastructure firm founded by Indian-origin entrepreneurs, illustrates the trajectory. In January, it raised $200 million in a Series A led by Tiger Global and Premji Invest. By June, it had added another $190 million — with Nvidia, Salesforce Ventures, and Temasek joining the cap table — at a $2 billion valuation. The company builds hardware, systems, and software that connect AI chips across fast networks, helping large models train with fewer delays. Five years ago, this company would have been founded in, and funded from, Santa Clara. Its Indian roots are part of the pitch now, not something to be downplayed.

## Why now

Three forces are converging.

First, India's defence procurement is finally opening up to startups. The government's iDEX programme and recent policy changes allowing private companies to supply the armed forces have created a domestic buyer for technologies that previously had no Indian market. When your customer is the Indian Army, you do not need a Series B deck explaining your go-to-market strategy.

Second, India's semiconductor ambitions are pulling hardware investment with them. The $11 billion Tata-PSMC fab in Dholera, Micron's assembly facility in Gujarat, and CG Semi's packaging plant have created an ecosystem that needs supporting technology — from precision instruments to speciality chemicals to testing equipment. Deep tech startups are positioning themselves along this emerging supply chain.

Third, the Anthropic Fable 5 shutdown has sharpened the sovereign technology argument. If the US can switch off frontier AI models with a Commerce Department letter, then building domestic alternatives is not ideological posturing — it is supply chain risk management. India's AI Mission has committed ₹2,194 crore in GPU grants and cash to 12 startups building foundational models. The money is modest by OpenAI standards, but it has attracted serious engineers.

## The NRI calculus

For Indian-origin professionals in Silicon Valley, the deep tech boom presents an unusual set of options. Historically, returning to India meant joining a services company or starting a consumer app. Now, a defence drone startup in Bengaluru or a semiconductor equipment company in Hyderabad offers the kind of technical challenge — and the kind of equity upside — that used to require staying in the Bay Area.

Accel's Mitra frames it in ecosystem terms. "We feel like India is at a point where, from the defence tech side or sophisticated engineering products coming out of the country, we are probably going to see them reach scale very soon." For a fund that made its India reputation backing Flipkart and Freshworks, that is not a casual observation.

The risk, of course, is that deep tech is unforgiving. Consumer apps fail fast and cheap. A gas turbine prototype that does not work costs millions and years. Indian VCs have limited experience managing hardware timelines, and the regulatory environment for defence and aerospace exports remains opaque. Not every deep tech bet will work. But the capital allocation has shifted, and with it, the signal about what kind of technology India believes it can build.

For NRI investors watching from abroad, the question is no longer whether India can produce world-class software engineers. It is whether those engineers — and the VCs backing them — can build things that fly, defend, and compute at the physical layer. The first $1.23 billion suggests the answer is being tested in real time."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's VCs Just Poured $1.2 Billion into Deep Tech in Six Months. They're Not Funding Apps.",
    "subheadline": "Drones, electric aircraft, gas turbines, and AI chips — India's venture capital scene is shifting from consumer apps to defence tech and hardware, and the money is moving fast.",
    "slug": make_slug("india-deep-tech-vc-funding-boom-defence-hardware"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "For NRIs in Silicon Valley, India's deep tech boom is creating the kind of technical challenge and equity upside that used to require staying in the Bay Area — defence drones, eVTOL aircraft, and sovereign AI chips are now fundable in Bengaluru.",
    "tags": ["deep-tech", "venture-capital", "defence-tech", "accel", "startups", "hardware", "sovereign-ai", "semiconductors"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Livemint", "url": "https://www.livemint.com/technology/india-can-still-build-ai-winners-despite-us-china-lead-says-accels-subrata-mitra-11750946553012.html"},
        {"name": "Reuters — Upscale AI", "url": "https://www.reuters.com/technology/upscale-ai-valued-2-billion-after-funding-extension-2026-06-22/"},
        {"name": "YourStory", "url": "https://yourstory.com/2025/11/tech-mahindra-sovereign-llm-1-trillion-parameters-indiaai-mission"},
        {"name": "Livemint — BharatGen", "url": "https://www.livemint.com/technology/india-must-build-foundational-ai-models-or-risk-becoming-a-mere-consumer-bharatgen-11750959513792.html"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/3665442/pexels-photo-3665442.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Close-up of a microchip on a printed circuit board — the kind of hardware India's VCs are now willing to fund",
    "image_attribution": "Pexels",
    "body": article2_body.strip()
}

# ─────────────────────────────────────────────────────
# Insert articles
# ─────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
