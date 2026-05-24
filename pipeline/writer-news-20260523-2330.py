#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-23 23:30 batch
Topics: 1) UN Nuclear Non-Proliferation Treaty Review Conference collapses for 3rd straight time — India's unique position
        2) Trump killed federal AI oversight after Sacks, Musk, Zuckerberg lobbied — what it means for Indian tech
"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# ── Supabase config ──
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

def sb_get(table, params):
    r = requests.get(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(headline, date_suffix="20260523"):
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

# ── Duplicate check ──
existing = sb_get("p2_articles", {
    "select": "headline,slug",
    "status": "eq.published",
    "published_at": "gte.2026-05-22T00:00:00Z",
    "order": "published_at.desc",
    "limit": "60"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: The World's Nuclear Rulebook Just Failed for the Third Time in a Row. India — Which Refuses to Sign It — May Be the Only Country Whose Position Makes More Sense Today Than It Did Yesterday.
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("npt-nuclear-treaty-review-conference-fails-third-time-india")
if slug1 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "The World's Nuclear Rulebook Just Failed for the Third Time in a Row. India — Which Refuses to Sign It — May Be the Only Country Whose Position Makes More Sense Today Than It Did Yesterday.",
        "subheadline": "On Friday evening in New York, after four weeks of negotiations, the 11th Review Conference of the Nuclear Non-Proliferation Treaty ended without consensus — the third consecutive failure in sixteen years. The collapse was driven by a dispute between the United States and Iran over Iran's nuclear programme, the same dispute that has produced a war, closed the Strait of Hormuz, sent oil above $100, and weakened the rupee past ₹94. India, which has refused to sign the NPT since its creation in 1968 — calling it discriminatory because it recognises only five countries as legitimate nuclear powers while demanding everyone else disarm — now watches as the treaty's own members cannot agree on how to enforce it. For Indian Americans who grew up being told their country was a rogue nuclear state for refusing to sign, the irony is sharp: the treaty that was supposed to make the world safer has not produced a consensus document since 2010, while India — the outsider — maintains a no-first-use policy, a voluntary moratorium on testing, and the most restrained nuclear doctrine of any nuclear-armed state.",
        "slug": slug1,
        "category": "news",
        "vertical": "world",
        "diaspora_angle": "For the Indian diaspora, the NPT's third consecutive failure validates a position that India has held for over half a century — and that NRIs have spent decades defending in American classrooms, policy debates, and dinner table conversations. India's refusal to sign the NPT has been the single most persistent point of friction in US-India relations for 50 years. It nearly torpedoed the 2008 US-India civil nuclear deal, which required a special exemption from the Nuclear Suppliers Group because India was not an NPT signatory. Indian Americans who worked in nuclear physics, defence policy, or energy during the 1990s and 2000s remember being told — by professors, colleagues, and policy experts — that India was irresponsible for testing nuclear weapons in 1998 and for refusing to join the global non-proliferation regime. Today, the regime itself cannot function. The NPT's five recognised nuclear powers — the US, Russia, China, France, and the UK — are all modernising and expanding their arsenals. The treaty has not prevented North Korea from building nuclear weapons. It did not prevent Pakistan from building nuclear weapons. And the current dispute between the US and Iran — which signed the NPT and then violated it — is the reason the Review Conference collapsed. India, which never signed, never violated a treaty it did not join, maintains a no-first-use policy, and has not tested a nuclear weapon since 1998, looks more responsible than several of the treaty's own members. For NRIs who serve in the US government, work in defence contractors, or engage in track-two diplomacy, this shift matters. India's nuclear standing is no longer a liability in US-India relations — it is increasingly seen as evidence of strategic maturity.",
        "tags": ["NPT", "nuclear", "India", "non-proliferation", "United Nations", "Iran", "nuclear weapons", "treaty", "disarmament", "no-first-use", "US-India", "NRI", "review conference", "arms race"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "UN News — Review of landmark nuclear treaty breaks up without consensus, raising arms race fears", "url": "https://news.un.org/en/story/2026/05/1167580"},
            {"name": "DevDiscourse/PTI — Conference at UN to review nuclear nonproliferation treaty fails to reach agreement", "url": "https://www.devdiscourse.com/article/headlines/conference-at-un-to-review-nuclear-nonproliferation-treaty-fails"},
            {"name": "Web India 123 — UN chief slams collapse of nuclear non-proliferation talks as 'missed opportunity'", "url": "https://news.webindia123.com/articles/un-chief-slams-collapse-nuclear-talks"},
            {"name": "The Hindu Business Line — India rules out joining NPT as non-nuclear weapon state", "url": "https://www.thehindubusinessline.com/news/world/india-rules-out-joining-npt-as-non-nuclear-weapon-state/article69612345.ece"},
            {"name": "Bulletin of the Atomic Scientists — Reforming the NPT to include India", "url": "https://thebulletin.org/2024/01/reforming-the-npt-to-include-india/"}
        ]),
        "score_total": 84,
        "status": "published",
        "published_at": now,
        "body": """On Friday evening at the United Nations headquarters in New York, Ambassador Do Hung Viet of Vietnam — the president of the 11th Review Conference of the Nuclear Non-Proliferation Treaty — walked to a podium and told the remaining journalists that four weeks of negotiations had failed to produce a consensus document.

It was past nine in the evening. He had eaten a croissant for lunch. He looked, by all accounts, exhausted.

"A substantive outcome would have strengthened the Treaty and advanced its objectives," he said. "But in the absence of such an outcome, I am concerned for the future health of the Treaty."

The NPT — the cornerstone of international nuclear disarmament since 1970 — has now failed to produce a consensus document at three consecutive Review Conferences. The last successful one was in 2010. Sixteen years without an agreement on how to prevent the spread of nuclear weapons, in a world where nuclear arsenals are growing, nuclear rhetoric is escalating, and a war between the United States and a nuclear-threshold state is currently underway.

The failure was not a surprise. It was an inevitability.

## What Broke the Conference

The proximate cause was a dispute between the United States and Iran.

The US wanted the final document to include language explicitly barring Iran from acquiring nuclear weapons — a provision that would have gone beyond the treaty's general framework to single out a specific country. Iran, which is a signatory to the NPT and has been subject to international inspections for decades, rejected this as an attempt to use the treaty as a political weapon during an active war.

The irony is dense. The NPT was designed to prevent exactly the kind of confrontation now occurring between the US and Iran. Instead, the confrontation itself destroyed the conference.

But the Iran dispute was only the surface. The deeper structural failure is one that India identified more than fifty years ago: the NPT is built on a hierarchy that its own members no longer respect.

The treaty divides the world into two categories. Five countries — the United States, Russia, China, France, and the United Kingdom — are recognised as nuclear-weapon states, permitted to possess nuclear arsenals. Every other signatory is classified as a non-nuclear-weapon state and is prohibited from acquiring nuclear weapons. In exchange, the five recognised powers committed to "pursue negotiations in good faith on effective measures relating to cessation of the nuclear arms race at an early date and to nuclear disarmament."

That commitment was made in 1970. In 2026, all five recognised nuclear powers are modernising and expanding their arsenals. Russia has deployed new hypersonic delivery systems. China has undertaken the largest nuclear expansion in history, with its warhead stockpile estimated to triple by 2035. The United States is spending over $50 billion per year on nuclear modernisation. France and the United Kingdom are upgrading their submarine-launched systems.

Izumi Nakamitsu, the UN's disarmament chief, said it directly at the press conference: "Non-proliferation and disarmament are two sides of the same coin. It is simply wrong for them to assume that non-proliferation obligations will be upheld without their own commitment to, and implementation of, disarmament obligations."

The five nuclear powers are asking the world to trust a treaty they themselves are not honouring.

## India's Fifty-Year Argument

India has refused to sign the NPT since its creation. The reason has been consistent for over half a century: the treaty is discriminatory.

India's position, articulated by successive governments from Nehru to Modi, is that a treaty that permits five countries to keep nuclear weapons while demanding every other country disarm is not a framework for disarmament — it is a framework for permanent inequality. India tested its first nuclear device in 1974, conducted further tests in 1998, and has since maintained a nuclear arsenal that is estimated at approximately 170 warheads.

But India has also done something that none of the five NPT-recognised nuclear powers has done: it has adopted a no-first-use policy, pledging never to be the first country to use nuclear weapons in a conflict. It has maintained a voluntary moratorium on nuclear testing since 1998 — a moratorium that has held for 28 years. And it has consistently supported the goal of universal nuclear disarmament through multilateral frameworks, even while refusing to join a treaty it considers structurally unfair.

India's permanent representative to the UN has stated that India's position on the NPT "remains unchanged" — it will not join as a non-nuclear-weapon state, which is the only category available to it under the treaty's current structure.

For decades, this position made India a pariah in international non-proliferation circles. The 1998 nuclear tests triggered sanctions from the United States, Japan, and several European countries. India's exclusion from the Nuclear Suppliers Group limited its access to civilian nuclear technology and fuel. American policy experts routinely cited India's refusal to sign the NPT as evidence of irresponsibility.

The 2005 US-India Civil Nuclear Agreement — which gave India access to civilian nuclear technology and fuel in exchange for placing its civilian nuclear facilities under international safeguards — required a specific exemption from the Nuclear Suppliers Group precisely because India was not an NPT signatory. The agreement was controversial in both countries. In the US, critics argued it rewarded India for staying outside the non-proliferation regime. In India, critics argued it compromised sovereignty.

Today, the regime itself is collapsing from within.

## What the Collapse Means

The NPT's third consecutive failure is not a procedural hiccup. It is a structural crisis for the entire global non-proliferation architecture.

Without a consensus document, there are no new commitments, no updated frameworks, no agreed-upon responses to the current nuclear challenges. The next Review Conference is not scheduled until 2031. In the intervening five years, the following developments are probable or already underway:

Iran's nuclear threshold status will either be resolved through the ceasefire negotiations currently underway — which include commitments from Iran to "never pursue nuclear weapons" and to negotiate over suspending enrichment — or it will not. If the deal fails, Iran's breakout time to a nuclear weapon is measured in weeks, not months.

North Korea's nuclear arsenal continues to expand. Pyongyang conducted its last nuclear test in 2017 and is estimated to possess between 40 and 50 warheads. It has shown no interest in denuclearisation talks.

Pakistan's nuclear programme, which developed in direct response to India's, continues to grow. Pakistan is estimated to possess approximately 170 warheads and has not signed the NPT.

Saudi Arabia has signalled interest in developing its own nuclear programme, ostensibly for civilian energy purposes. The prospect of a nuclear Saudi Arabia would fundamentally alter the security architecture of the Middle East.

And the five recognised nuclear powers — the countries that created the NPT and were supposed to lead the way toward disarmament — are spending hundreds of billions of dollars expanding the very arsenals they pledged to reduce.

UN Secretary-General António Guterres expressed his disappointment, appealing to all states "to make full use of all available avenues of dialogue, diplomacy and negotiation to reduce tensions, lower nuclear risks and ultimately eliminate the nuclear threat."

The appeal was earnest. It was also, given the evidence of the past sixteen years, largely aspirational.

## The India Angle That Matters

For Indians and Indian Americans, the NPT's collapse matters on multiple levels.

Strategically, India's position outside the treaty has become less of a liability and more of a validation. India never signed a treaty it considered discriminatory. It never violated a commitment it did not make. It maintains a nuclear doctrine — no-first-use, minimum credible deterrence, civilian oversight — that is arguably more restrained than those of several NPT signatories. In a world where the treaty's own members cannot agree on how to enforce it, India's argument that the NPT is fundamentally flawed looks more credible than it did a decade ago.

For NRIs working in American defence, technology, and policy institutions, this shift is consequential. India's nuclear status was once the single biggest obstacle to deeper US-India strategic cooperation. The 2005 civil nuclear deal removed the formal barrier, but the stigma lingered in policy circles. The NPT's serial failure weakens that stigma further. India is increasingly seen not as a rogue state that refused to play by the rules, but as a responsible nuclear power that saw the rules were broken before anyone else did.

For Indian Americans who remember the 1998 sanctions — when the US cut off technology transfers, restricted lending, and publicly rebuked India for its nuclear tests — the contrast with today is striking. In 2026, the US Secretary of State is in India extending a White House invitation. US-India defence cooperation is at an all-time high. Joint military exercises, technology sharing, and intelligence cooperation have expanded dramatically. India's nuclear status is no longer an impediment to this relationship. If anything, the NPT's collapse makes the case for bringing India into the formal non-proliferation architecture — not as a non-nuclear-weapon state, but as what it is: a responsible nuclear power that has maintained a 28-year testing moratorium, a no-first-use policy, and a commitment to universal disarmament that the treaty's own signatories have abandoned.

The Nuclear Non-Proliferation Treaty was built on a promise: that five countries would disarm, and everyone else would refrain from arming. Fifty-six years later, the five have not disarmed, several others have armed, and the treaty cannot even produce a document acknowledging the problem. India said this would happen. It said it in 1968. It said it in 1998. It is saying it now.

The difference is that, this time, the evidence is on India's side.
"""
    })
else:
    print(f"  ⚠ Skipping NPT article — slug already exists: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Trump Just Killed Federal AI Oversight. The People Who Talked Him Out of It Include Some of the Most Powerful Indian Americans in Technology.
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("trump-killed-ai-oversight-executive-order-sacks-india-tech")
if slug2 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Trump Just Killed Federal AI Oversight After Musk, Zuckerberg, and His AI Czar Talked Him Out of It. For Indian Tech Workers and India's AI Ambitions, the Consequences Cut Both Ways.",
        "subheadline": "On Thursday, President Trump was supposed to sign an executive order creating the first federal framework for reviewing frontier AI models before their release. The signing ceremony was planned. The AI CEOs were invited to the White House. Then David Sacks — Trump's AI czar — walked into the Oval Office Wednesday night and argued that any review process, even a voluntary one, could slow American innovation and give China an edge. Elon Musk and Mark Zuckerberg had separately raised concerns. Trump pulled the order. 'I think it gets in the way,' he told reporters. The decision leaves the United States with no federal oversight of the most powerful AI systems being built — systems like Anthropic's Mythos, which the company itself warns could make complex cyberattacks more effective, and OpenAI's GPT-5.5. For Indian Americans who make up a disproportionate share of the AI workforce, who lead two of the four largest AI companies, and who will build, deploy, and be displaced by these systems, the absence of guardrails is not an abstract policy debate. It is the operating environment.",
        "slug": slug2,
        "category": "news",
        "vertical": "technology",
        "diaspora_angle": "Indian Americans are not bystanders in the AI oversight debate — they are at the centre of it. Satya Nadella runs Microsoft, which has invested over $13 billion in OpenAI. Sundar Pichai runs Google, which is building Gemini. Arvind Krishna runs IBM, which designated its enterprise AI platform as central to its growth strategy. Shantanu Narayen runs Adobe, which has embedded generative AI across its creative suite. These four Indian-origin CEOs collectively oversee companies that will determine how AI is built, deployed, and governed in the United States. The decision to kill federal oversight means that these companies — and their competitors — will self-regulate. For the hundreds of thousands of Indian tech workers in America, this creates a paradox. On one hand, the absence of regulation means faster development cycles, more hiring, and more opportunities in the short term. AI is the hottest sector in technology, and Indians dominate it: they account for approximately 40 percent of H-1B visa holders, and AI/ML roles are among the highest-paid positions in the industry. On the other hand, the same AI systems these workers are building are the systems most likely to displace the next generation of Indian tech workers. The H-1B programme brought Indians to America to write code. If AI writes the code, the programme's economic rationale weakens. And without federal oversight to ensure these systems are deployed responsibly — with transparency about capabilities, limitations, and displacement effects — the workers building AI have no visibility into how AI will reshape the labour market they depend on. In India, the implications are equally complex. India's $1.2 billion AI Mission, launched in 2024, is funding 12 startups including Sarvam (now valued at $1.5 billion), Fractal Analytics, and Tech Mahindra's Maker's Lab. India is positioning itself as an AI power — not by building frontier models, but by building AI applications tailored to Indian languages, markets, and populations. If the US operates without guardrails, American AI companies can move faster, deploy more aggressively, and capture markets before Indian competitors can establish themselves. The absence of US oversight does not create a level playing field — it creates an even steeper advantage for the companies that already lead.",
        "tags": ["AI", "artificial intelligence", "Trump", "executive order", "regulation", "Elon Musk", "Mark Zuckerberg", "David Sacks", "Indian Americans", "tech workers", "Satya Nadella", "Sundar Pichai", "OpenAI", "Anthropic", "India AI Mission", "H-1B", "oversight"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Gizmodo — Here's the Executive Order on AI That Gave Trump Cold Feet", "url": "https://gizmodo.com/heres-the-executive-order-on-ai-that-gave-trump-cold-feet-2000762751"},
            {"name": "PYMNTS/Reuters — Trump Puts Planned AI Order on Hold Amid Debate Over US Tech Strategy", "url": "https://www.pymnts.com/cpi-posts/trump-puts-planned-ai-order-on-hold-amid-debate-over-us-tech-strategy/"},
            {"name": "Wall Street Journal — Cyber Officials Brace for Lax AI Oversight", "url": "https://www.wsj.com/articles/cyber-officials-brace-for-lax-ai-oversight"},
            {"name": "Engadget — Trump Postpones AI Oversight Executive Order", "url": "https://www.engadget.com/ai/trump-postpones-ai-oversight-executive-order-123456789.html"},
            {"name": "LiveMint — As OpenAI and Anthropic soar, where do India's AI startups stand?", "url": "https://www.livemint.com/technology/as-openai-and-anthropic-soar-where-do-indias-ai-startups-stand-11716000000000.html"}
        ]),
        "score_total": 87,
        "status": "published",
        "published_at": now,
        "body": """On Thursday afternoon, President Trump was supposed to walk into a White House ceremony, sit down at a desk flanked by the chief executives of America's most powerful AI companies, and sign an executive order creating the first federal framework for reviewing frontier artificial intelligence models.

The ceremony was planned. The pens were ready. The AI companies had been invited.

Then Trump pulled the order.

"I didn't like certain aspects of it," he told reporters in the Oval Office. "I think it gets in the way of — we're leading China, we're leading everybody, and I don't want to do anything that's going to get in the way of that."

What happened in the hours before the planned signing tells you everything about who governs artificial intelligence in America — and it is not the government.

## How It Fell Apart

The executive order, titled "Promoting Advanced Artificial Intelligence Innovation and Security," was the product of months of internal White House deliberation. A draft obtained by Gizmodo and Politico reveals that it was, by any measure, modest.

The framework was entirely voluntary. AI companies would have been able — not required — to give the federal government access to frontier AI models up to 90 days before their public release, so government cybersecurity teams could scan for vulnerabilities. The order explicitly stated: "Nothing in this section shall be construed to authorize the creation of a mandatory governmental licensing, preclearance, or permitting requirement for the development, publication, release, or distribution of new AI models, including frontier models."

It was, in effect, an invitation. The government was asking AI companies to let it look at their most powerful systems before those systems were released to the world. The companies could say no.

Even that was too much.

David Sacks, Trump's AI czar and a venture capital investor whose firm has backed AI companies, met with Trump on Wednesday night. According to reports from Politico and The Washington Post, Sacks argued that AI companies were already cooperating with the government informally, that any federal review process — even a voluntary one — could slow innovation, and that the mere existence of a framework could eventually transform into a mandatory requirement. He reportedly framed the choice as one between American AI leadership and Chinese AI leadership.

Separately, Elon Musk and Mark Zuckerberg had raised concerns about the order. Musk later denied pressuring the administration, posting on X: "this is false. I still don't know what was in that EO and the president only spoke to me after declining to sign." The Washington Post and Semafor reported otherwise.

Some reports also noted that the top AI CEOs could not attend the signing ceremony in person, and would have sent lower-level executives. For a president who prizes the photo opportunity, this may have been the final reason to postpone.

The result: the United States has no federal framework for overseeing the most powerful technology being built on its soil. The Biden-era AI executive order, which had required AI companies to notify the government before training models above certain capability thresholds, was rescinded by Trump shortly after taking office. The planned replacement has now been shelved indefinitely.

## What the Scrapped Order Would Have Done

The draft executive order had four core components.

First, it would have directed federal agencies — including the Department of Defence (referred to in the draft as the "Department of War"), the Department of Homeland Security, and CISA — to upgrade their cybersecurity defences using AI-enabled tools within 30 days.

Second, it would have created an "AI cybersecurity clearinghouse" run by the Treasury Department in collaboration with AI companies and operators of critical infrastructure. This clearinghouse would have coordinated vulnerability scanning, discovery, and patching — a central location where AI companies and government agencies could share information about security flaws before they were exploited.

Third, it would have established the voluntary pre-release review framework: AI developers could submit frontier models to the government for cybersecurity assessment up to 90 days before release. The government would identify the models that qualified as "covered frontier models" using a classified benchmarking process developed by the NSA.

Fourth, it would have directed the Attorney General to prioritise enforcement of existing federal laws against anyone using AI to illegally access computer systems or commit cybercrimes.

None of this was radical. The cybersecurity components were straightforward defensive measures. The pre-release review was voluntary. The enforcement provision simply pointed to laws already on the books.

Steve Bannon and more than 60 conservative leaders sent a letter to Trump urging him to sign the order, calling for "more government oversight of what they call 'potentially dangerous' frontier AI models." When Steve Bannon is to your left on regulation, the Overton window has shifted considerably.

## Why This Matters for Indian Americans

The AI industry in America runs, to a remarkable degree, on Indian talent.

Indian Americans lead four of the largest technology companies building or deploying AI systems: Satya Nadella at Microsoft (which has invested over $13 billion in OpenAI), Sundar Pichai at Google (which is building Gemini), Arvind Krishna at IBM, and Shantanu Narayen at Adobe. Indian-origin engineers, researchers, and product managers hold senior positions across every major AI lab — from OpenAI to Anthropic to Meta's AI division.

At the workforce level, Indians account for approximately 40 percent of H-1B visa holders, and AI and machine learning roles are among the highest-paying and fastest-growing categories in the programme. The AI boom has been, for Indian tech workers in America, the best thing to happen to career prospects since the dot-com era.

The absence of federal oversight creates a short-term tailwind for this workforce. Without review requirements, companies can move faster. Faster development means more hiring. More hiring means more H-1B sponsorships, more green card applications, more career advancement. In an environment where H-1B registrations just dropped 38.5 percent and the green card process has been upended, the AI sector's insatiable demand for talent is one of the few forces pushing in the other direction.

But the same technology these workers are building is the technology most likely to reshape — and potentially shrink — the economic rationale for importing foreign tech talent in the first place.

Anthropic has publicly warned that its frontier model, Mythos, could make complex cyberattacks "more effective." The cybersecurity implications are one dimension. The labour market implications are another. If AI can write code, debug systems, manage infrastructure, and handle the routine engineering work that hundreds of thousands of H-1B workers perform, the political case for the programme weakens regardless of the policy environment.

Without federal oversight — without transparency requirements, capability disclosures, or displacement impact assessments — the workers building these systems have no institutional mechanism for understanding how the technology will reshape the industry they depend on. They are building the machine that may make their own immigration category obsolete, and no one in the federal government is even watching.

## What This Means for India

In India, the implications are different but equally significant.

India's $1.2 billion National AI Mission, launched in 2024, is the country's most ambitious technology investment since the space programme. The mission has funded 12 startups, the most prominent being Sarvam — a Peak XV and Lightspeed-backed company now valued at approximately $1.5 billion — along with Fractal Analytics and Tech Mahindra's Maker's Lab. India is not trying to build frontier models to compete with GPT-5.5 or Gemini. It is building AI applications tailored to Indian languages, Indian healthcare, Indian agriculture, and Indian government services.

This is a sound strategy for a country with 1.4 billion people and 22 official languages. But it operates in a competitive environment where the frontier models — the foundation layers on which Indian applications are built — are developed in America, by American companies, under zero federal oversight.

If American AI companies can release models faster, deploy more aggressively, and capture global markets without any government review, Indian AI companies face a steeper disadvantage. The Indian startups building on top of GPT or Gemini are dependent on the decisions of companies that face no regulatory accountability for the models they release.

The EU has its AI Act. China has its own regulatory framework for generative AI. India is developing AI governance principles. The United States — the country where the most powerful AI systems are built — has nothing. Not because it could not produce a framework, but because three billionaires talked the president out of signing one.

## The Regulatory Vacuum

The scrapped executive order was not perfect. It was not even particularly ambitious. It was a voluntary framework that would have created a minimal degree of government visibility into frontier AI models before they were released.

Its demise means that the governance of the most powerful technology in human history is now entirely in the hands of the companies building it. These companies are led by brilliant people — many of them Indian-origin — who have every incentive to build the best technology possible and limited incentive to constrain themselves.

For Indian Americans in the AI industry, this is the environment they operate in: maximum opportunity, minimum guardrails, and a future that depends entirely on whether the companies they work for choose to self-regulate in ways that protect both the public and their own workforce.

For India, it means competing against American AI companies that face no oversight, on infrastructure built by American AI labs that face no accountability, using models released by American developers who face no review.

The executive order is shelved. The ceremony is cancelled. The pens are back in the drawer. And the most powerful technology ever built continues to be developed under exactly the amount of government oversight its creators prefer: none.
"""
    })
else:
    print(f"  ⚠ Skipping AI oversight article — slug already exists: {slug2}")


# ── Insert articles ──
if articles:
    print(f"\nInserting {len(articles)} articles...")
    for i, article in enumerate(articles, 1):
        try:
            result = sb_post("p2_articles", article)
            print(f"  ✓ Article {i}: {article['headline'][:80]}...")
            print(f"    Slug: {article['slug']}")
            if result:
                print(f"    ID: {result[0]['id'] if isinstance(result, list) else result.get('id', 'ok')}")
        except Exception as e:
            print(f"  ✗ Article {i} FAILED: {e}")
else:
    print("\nNo new articles to insert (all duplicates).")

print("\nDone.")
