#!/usr/bin/env python3
"""Batch article writer for videshi-writer-news cron — 2026-05-17 evening run."""

import json
import subprocess
import os
import sys

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(PIPELINE_DIR)

def insert_article(article_json):
    result = subprocess.run(
        ["python3", "videshi-db.py", "insert-article", json.dumps(article_json)],
        capture_output=True, text=True, env={**os.environ}
    )
    print(result.stdout.strip())
    if result.stderr:
        print(f"STDERR: {result.stderr.strip()}", file=sys.stderr)
    return json.loads(result.stdout.strip()) if result.stdout.strip() else {}

def update_topic_status(topic_id, status):
    result = subprocess.run(
        ["python3", "videshi-db.py", "update-topic-status", topic_id, status],
        capture_output=True, text=True, env={**os.environ}
    )
    print(f"  topic {topic_id[:12]}... → {status}")

# ═══════════════════════════════════════════════════════
# ARTICLE 1 — news: India-Pakistan One Year After Sindoor
# ═══════════════════════════════════════════════════════

article1 = {
    "headline": "'Geography or History': India's Army Chief Draws the Sharpest Red Line Yet for Pakistan",
    "subheadline": "A year after Operation Sindoor, General Dwivedi's ultimatum, a suspended water treaty, and Pakistan's defiant sabre-rattling suggest the subcontinent's most dangerous equilibrium since 1971.",
    "category": "news",
    "vertical": "geopolitics",
    "urgency": "daily",
    "score_total": 82,
    "slug": "india-army-chief-warns-pakistan-geography-history-sindoor-20260517",
    "diaspora_angle": "For the 4.5 million-strong Indian diaspora in the US, UK, and Canada, India-Pakistan tensions shape family travel plans, property decisions, and an ever-present anxiety about the homeland. The Indus Waters suspension also threatens agriculture in Punjab — where many NRI families trace their roots.",
    "tags": ["India-Pakistan", "Operation Sindoor", "General Dwivedi", "Indus Waters Treaty", "Rajnath Singh", "Indian military", "Pakistan terrorism", "NRI homeland security"],
    "sources": [
        {"name": "Kashmir Examiner", "url": "https://kashmirexaminer.com/army-chief-warns-pakistan-geography-history/"},
        {"name": "India Tribune", "url": "https://indiatribune.com/india-adhered-indus-waters-treaty-65-years/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/pakistan-backs-terror-india-suspends-indus-water-treaty/"},
        {"name": "DevDiscourse", "url": "https://devdiscourse.com/article/army-chief-challenges-pakistan/"},
        {"name": "Latestly", "url": "https://latestly.com/world/indian-army-chief-warns-pakistan-cross-border-terrorism/"}
    ],
    "image_entities": ["General Upendra Dwivedi", "Indian Army", "Operation Sindoor"],
    "image_must_show": "Indian Army Chief General Upendra Dwivedi or Indian military forces",
    "image_search_query": "Indian Army Chief General Upendra Dwivedi 2026",
    "body": """One year ago this week, Indian fighter jets struck targets inside Pakistan in what New Delhi called Operation Sindoor — the most significant cross-border military action since the 1999 Kargil conflict. The operation, launched in retaliation for the Pahalgam terrorist attack, lasted 88 hours, ended with a ceasefire that Pakistan reportedly requested, and left the subcontinent's security architecture permanently altered.

On the anniversary, India's Army Chief General Upendra Dwivedi made certain nobody mistook the calm for closure. Speaking at the annual Sena Samvad event, he delivered what may be the most unambiguous warning an Indian military commander has issued to Islamabad in decades: "You have to decide whether you want to remain in geography or end up in history."

## The Calculus Has Changed

The statement was not rhetorical flourish. Dwivedi outlined a new Indian military doctrine that treats Pakistan's support infrastructure for cross-border terrorism — training camps, logistics networks, command channels — as legitimate targets for pre-emptive action. During Operation Sindoor, India confirmed shooting down 13 Pakistani aircraft and striking 11 airfields, a scale of engagement that would have been unthinkable even five years ago.

Defence Minister Rajnath Singh reinforced the message in Parliament, stating that India's defence systems "completely foiled" Pakistan's retaliatory attack. Jammu and Kashmir Lieutenant Governor Manoj Sinha went further: "Nothing in Pakistan is beyond the reach of the Indian Army."

Pakistan's response has been a volatile mix of defiance and diplomacy. The country's Defence Minister Khawaja Asif warned of "deep incursions" into Indian territory — a threat Indian analysts dismissed as bluster, pointing to the operational results of Sindoor as evidence of a widening capability gap. Pakistan's military spokesperson criticised General Dwivedi's remarks as "provocative," while simultaneously signalling openness to renewed dialogue through back channels.

## The Water Weapon

Perhaps more consequential than the military rhetoric is New Delhi's decision to suspend the 1960 Indus Waters Treaty, the six-decade-old water-sharing agreement that survived three wars and a nuclear standoff. India's Ministry of External Affairs framed the suspension as a response to Pakistan's "corrosion" of the treaty's spirit through state-sponsored terrorism.

The treaty governs the flow of six rivers — the Indus, Jhelum, Chenab, Ravi, Beas, and Sutlej — that irrigate millions of hectares of farmland in both countries. India had adhered to its terms for 65 years despite, as the MEA pointedly noted, "so many provocations." The suspension gives India leverage over Pakistan's agricultural heartland in a way that military strikes cannot replicate.

Pakistan has sought recourse through an international Court of Arbitration, but India has rejected the tribunal's jurisdiction, calling it a "Pakistan-backed" mechanism that lacks legitimacy. The standoff leaves the treaty in a constitutional grey zone — technically alive, practically frozen.

## What the Diaspora Is Watching

For the millions of Indians abroad who track these developments with a mix of patriotic pride and genuine anxiety, the current moment is charged with contradictions. NRI families with roots in Punjab and Jammu — regions directly affected by both military operations and river politics — find themselves navigating conversations that their parents' generation could not have imagined.

Travel advisories remain a practical concern. Property investments in border states carry new risk premiums. And the question that every Indian abroad asks during these episodes — "How close is this to something bigger?" — has no comfortable answer when both countries possess nuclear arsenals estimated at 170 and 140 warheads respectively.

## What Comes Next

The anniversary has passed without fresh escalation, but the underlying dynamics are accelerating. India is modernising its military at a pace that increasingly outstrips Pakistan's capacity to keep up. General Dwivedi's emphasis on "tech-driven future warfare" and the Army's 100,000 internship applications from young Indians suggest a force that is becoming simultaneously more lethal and more popular.

For Pakistan, the strategic choices are narrowing. Its defence budget, already stretched under an IMF-backed austerity programme, cannot sustain an arms race with an economy eight times its size. The geography-or-history ultimatum may be the most honest articulation of a reality that diplomats on both sides have long danced around.

The ceasefire holds. But one year after Sindoor, it holds on India's terms — and everyone in New Delhi, Islamabad, and the diaspora knows it."""
}

# ═══════════════════════════════════════════════════════
# ARTICLE 2 — nri-world: USCIS Signature Rule
# ═══════════════════════════════════════════════════════

article2 = {
    "headline": "A Wrong Signature Could Now Kill Your Green Card Application. Here's What Changed.",
    "subheadline": "USCIS's new interim rule lets officers deny petitions — even already-approved ones — over invalid signatures. The July 10 deadline is eight weeks away.",
    "category": "nri-world",
    "vertical": "immigration",
    "urgency": "daily",
    "score_total": 78,
    "slug": "uscis-signature-rule-h1b-green-card-denial-july-2026-20260517",
    "diaspora_angle": "Indians file more H-1B petitions than any other nationality — roughly 70% of all applications. The signature rule adds a procedural tripwire to an already hostile immigration environment, and the financial stakes are enormous given the new $100,000 filing fee for fresh H-1B applications.",
    "tags": ["USCIS", "H-1B visa", "green card", "immigration policy", "NRI", "signature rule", "US immigration 2026", "Indian diaspora"],
    "sources": [
        {"name": "VisaHQ", "url": "https://www.visahq.com/newsroom/uscis-issues-interim-final-rule-allowing-denial-approved-petitions-over-invalid-signatures"},
        {"name": "AInvest", "url": "https://ainvest.com/uscis-interim-rule-tightening-signature-requirements-h1b/"},
        {"name": "AI Hustle HQ", "url": "https://aihustlehq.com/uscis-signature-rule-h1b-green-card/"},
        {"name": "Tafapolsky & Smith LLP", "url": "https://tandslaw.com/uscis-interim-final-rule-valid-signatures/"},
        {"name": "The Local Report", "url": "https://articles.thelocalreport.in/new-uscis-signature-error-rules-h1b-green-card/"}
    ],
    "image_entities": ["USCIS", "US immigration office", "visa application"],
    "image_must_show": "USCIS office or immigration documents",
    "image_search_query": "USCIS office immigration petition 2026",
    "body": """On May 11, the United States Citizenship and Immigration Services published an interim final rule that, in the bureaucratic way of things, could upend hundreds of thousands of immigration cases with a single definitional change. The rule clarifies — or, depending on your perspective, weaponises — what counts as a "valid signature" on petitions for immigration benefits.

The bottom line: if your H-1B petition, green card application, or family-based immigration filing carries a signature that USCIS officers deem invalid, they can now reject it outright, deny it after initial acceptance, or reopen an already-approved case to revoke it. The rule takes full effect on July 10, 2026.

## What Counts as Invalid

USCIS has formalised a requirement that may surprise applicants and employers who have filed thousands of petitions without incident: only original handwritten ("wet ink") signatures are definitively valid. The rule explicitly flags several commonly used alternatives as potentially invalid.

Electronic signatures, including those generated by DocuSign or Adobe Sign. Copy-and-paste signatures transplanted from other documents. Scanned signature images inserted into forms. Typed names in signature fields, even when accompanied by a "/s/" designation.

The agency stopped short of banning all electronic signatures in every context — some online-filed forms have their own authentication mechanisms — but the rule gives individual USCIS officers broad discretion to determine whether a particular signature meets the standard.

## The Financial Sting

Under previous practice, a petition rejected for a technical deficiency like a signature issue would typically receive a Request for Evidence, giving the applicant a window to cure the defect. The new rule removes that cushion in many cases. An officer can deny the petition outright, and crucially, USCIS retains the filing fees.

For employers sponsoring H-1B workers, the stakes have escalated dramatically. A fresh H-1B application now carries a $100,000 filing fee under the rules that took effect earlier this year. A denial over a signature technicality does not trigger a refund. For Indian IT firms and tech companies that file hundreds of petitions annually, the exposure runs into millions of dollars.

"This is a compliance trap," one New York-based immigration attorney said. "You're asking employers to guarantee that every signature on every form in a multi-document filing was applied with a physical pen on the original page. That's not how modern business works."

## The Reopening Power

The most alarming provision for existing visa holders is USCIS's explicit assertion that it can reopen and revoke already-approved petitions if it later determines that a signature was invalid. This means an H-1B worker who has been employed for years on an approved petition could theoretically face revocation proceedings if the original filing is audited and found to contain a non-compliant signature.

Immigration lawyers note that this power existed in theory before, but the interim rule formalises it as settled policy — removing any ambiguity that might have protected applicants in administrative hearings.

## Why It Matters for the Diaspora

Indians represent approximately 70% of all H-1B petition beneficiaries, according to USCIS data. The community is also the largest single national group in the employment-based green card backlog, where wait times stretch beyond a decade. Every additional procedural hurdle — however minor it may seem on paper — compounds the uncertainty that defines the Indian immigrant experience in America.

The timing is also significant. The rule arrives in an immigration climate already shaped by the $100,000 H-1B fee, a beneficiary-centric lottery system designed to reduce duplicate filings, FBI vetting for green card applicants, and a federal court ruling in April that struck down USCIS's practice of placing indefinite "adjudicative holds" on applications from nationals of 39 countries.

For the estimated 1.2 million Indians currently in the US on temporary work visas, the signature rule is one more reason to double-check every page of every filing — and to ensure their employer's immigration counsel is aware of the change before July 10.

## What to Do Now

Immigration attorneys recommend three immediate steps. First, audit all pending petitions filed since January to verify that original wet-ink signatures were used on every required form. Second, establish a firm-wide policy that prohibits electronic or scanned signatures on USCIS filings, regardless of past practice. Third, for petitions being prepared now, build in extra processing time to accommodate physical signature collection — especially for remote workers or executives travelling internationally.

The rule is "interim final," which means it takes effect without a prior public comment period but invites comments after publication. Whether any comments will soften the policy before July 10 remains to be seen. In the current Washington climate, immigration attorneys are not holding their breath."""
}

# ═══════════════════════════════════════════════════════
# ARTICLE 3 — markets-finance: Rupee at 96
# ═══════════════════════════════════════════════════════

article3 = {
    "headline": "The Rupee Just Breached 96. For NRIs, That's a Remittance Windfall — and an Alarm Bell.",
    "subheadline": "India's currency hit a record low of 96.14 against the dollar on May 16, squeezed by surging oil prices, fleeing foreign investors, and a Hormuz crisis with no end date.",
    "category": "markets-finance",
    "vertical": "finance",
    "urgency": "daily",
    "score_total": 80,
    "slug": "rupee-96-dollar-record-low-nri-remittance-oil-crisis-20260517",
    "diaspora_angle": "NRIs sending money home are getting the best exchange rate in history — every $1,000 now converts to nearly Rs 96,000 versus Rs 83,000 two years ago. But the same forces weakening the rupee also erode the purchasing power of those rupees once they land in India.",
    "tags": ["Indian rupee", "USD/INR", "RBI", "oil prices", "Hormuz crisis", "FII outflows", "NRI remittances", "Indian markets", "inflation"],
    "sources": [
        {"name": "Asha News Network", "url": "https://ashanewsnetwork.com/rupee-hits-record-low-of-96-14-dollar/"},
        {"name": "FX News 24", "url": "https://fxnews24.co.uk/rupee-breaches-96-rbi-intervention/"},
        {"name": "Informist Media", "url": "https://informistmedia.com/india-rupee-review-96-rbi-help/"},
        {"name": "Mint", "url": "https://www.livemint.com/news/india/rupee-hits-new-lows-deep-reset-experts/"},
        {"name": "Exim Guru", "url": "https://eximguru.com/india-steps-to-mobilise-dollar-inflows-rupee-slides/"}
    ],
    "image_entities": ["Indian Rupee", "Reserve Bank of India", "forex market"],
    "image_must_show": "Indian rupee currency or RBI building",
    "image_search_query": "Indian rupee currency notes coins",
    "body": """On the morning of May 16, the Indian rupee crossed a line that currency traders had been watching for months. It breached 96 against the US dollar, touching an intraday low of 96.14 before the Reserve Bank of India stepped in with what dealers described as aggressive dollar sales. By the close of trading, the currency had recovered slightly to 95.86 — a fresh closing low, but at least on the right side of 96.

The breach was not a single-day accident. It was the culmination of a five-month slide that has seen the rupee weaken more than 5.5% since the escalation of Middle Eastern hostilities in late 2025. The Strait of Hormuz — the narrow waterway through which roughly 60-65% of India's crude oil imports transit — remains a flashpoint, with Brent crude holding above $114 a barrel.

## Three Forces, One Direction

The rupee's decline is being driven by three reinforcing pressures that the RBI can slow but not reverse.

**Oil.** India imports approximately 85% of its crude requirements. With Brent above $114, the country's oil import bill has surged, widening the current account deficit and creating persistent dollar demand from refiners. Every $10 increase in crude prices adds roughly $15 billion to India's annual import bill — money that has to be paid in dollars, draining the domestic currency.

**Capital flight.** Foreign portfolio investors have withdrawn over Rs 2.6 lakh crore (approximately $27 billion) from Indian equities in 2026, the most sustained outflow since the taper tantrum of 2013. Rising US interest rates and geopolitical risk have made emerging markets broadly unattractive, but India's energy vulnerability has made it a particular target. The FII selling is self-reinforcing: as the rupee weakens, foreign investors face additional currency losses on their Indian holdings, incentivising further exits.

**The dollar.** The US dollar index has climbed to 99.15, boosted by sticky inflation and expectations that the Federal Reserve will hold rates higher for longer. A strong dollar mechanically pressures all emerging market currencies, but the rupee's energy import dependence amplifies the effect.

## What the RBI Can — and Cannot — Do

The central bank is not passive. On May 16 alone, dealers estimated that the RBI sold $3-4 billion from its foreign exchange reserves to defend the 96 level. India's reserves, while substantial at approximately $580 billion, have declined from their peak of $642 billion a year ago — a drawdown that limits the RBI's ammunition.

The RBI is also exploring structural measures to attract dollar inflows. According to reports, options under consideration include reviving a deposit scheme similar to the one used during the 2013 currency crisis, which offered NRIs premium interest rates on dollar and pound deposits in Indian banks. The central bank may also remove withholding taxes on overseas bond purchases to make Indian debt more attractive to foreign investors.

But economists are increasingly blunt about the limits of intervention. "The rupee needs a deep reset, not a quick fix," one chief economist told Mint. Structural reforms — reducing oil import dependency, boosting manufactured exports, accelerating domestic energy production — are the only lasting solutions, and none of them operate on the timeline of a forex crisis.

## The NRI Paradox

For the Indian diaspora, the rupee's weakness creates a peculiar paradox. Dollar-earners sending money to India are getting historically favourable exchange rates. A software engineer in Sunnyvale remitting $2,000 a month now delivers nearly Rs 192,000 to family in India — compared to Rs 166,000 at the same rate two years ago. That is a meaningful difference for parents' medical bills, siblings' education fees, or property EMIs.

But the purchasing power of those rupees is being eroded by the same inflationary forces that are weakening the currency. Petrol and diesel prices, while officially "stable," face mounting pressure from the oil import bill. Food prices remain elevated. And the six consecutive months of rising inflation that preceded the rupee's breach of 96 mean that the extra rupees buy less than the headline number suggests.

For NRIs with property investments in India, the calculus is more favourable — assets denominated in rupees become cheaper in dollar terms, making this an attractive entry point. But the same logic applies to risk: a currency that has fallen 5.5% in five months can fall further.

## Where It Goes From Here

Analysts predict the rupee will trade in a 95.60-96.20 range in the near term, with the RBI defending the 96 level as a psychological and practical barrier. If crude oil prices remain elevated and FII outflows continue, however, forecasters warn that the currency could test 98-100 by year-end.

The RBI's next monetary policy decision will be closely watched. A rate cut — which the domestic economy arguably needs — would widen the interest rate differential with the US and put further pressure on the rupee. A hold would support the currency but risk slowing growth. It is the kind of impossible choice that central bankers in energy-importing nations face when the world's most important shipping lane is under threat.

For now, the rupee has retreated from its worst levels. But 96 is no longer uncharted territory — it is the new floor from which the next chapter begins."""
}

# ═══════════════════════════════════════════════════════
# INSERT ALL ARTICLES
# ═══════════════════════════════════════════════════════

print("\n══════════ INSERTING ARTICLES ══════════\n")
results = []
for i, article in enumerate([article1, article2, article3], 1):
    print(f"\n--- Article {i}: {article['headline'][:60]}...")
    r = insert_article(article)
    results.append(r)

# ═══════════════════════════════════════════════════════
# MARK TOPICS PUBLISHED
# ═══════════════════════════════════════════════════════

print("\n══════════ UPDATING TOPIC STATUSES ══════════\n")

# Article 1 topics (India-Pakistan)
a1_topic_ids = [
    "58e0de45-2db4-4962-886a-b494191506c3",
    "d8311a48-0544-4cba-af93-0bffca659eba",
    "b57e16f5-7a27-49d9-9ee3-65b7cd23947a",
    "6e9aab87-ab18-40a1-bce9-f16e8b4a9db7",
    "278e3666-9d34-4081-b7fb-73d15037bd36",
    "2f31e8c8-6b9d-48dc-891e-59b235c08259",
    "0a7c8090-4381-4439-847f-da437526afb0",
]

# Article 2 topics (USCIS)
a2_topic_ids = [
    "dfba732b-6104-4323-80ca-86b55c564603",
    "2724e566-fe57-4f09-bad0-28afe2252ea9",
]

# Article 3 topics (Rupee)
a3_topic_ids = [
    "34bed60e-41a7-43b9-803c-8d5c81d0fe50",
    "54517ca0-c25c-4bab-8790-032d10ea8340",
    "5e1d344e-bcc7-4deb-bde2-f7a08735a60c",
    "b0d20f43-10b0-4058-95d4-1522786a7abb",
    "1f4fbe3f-71b4-4245-99aa-b26cff5a1dbc",
    "ecf97a12-47fc-4e22-aba4-85308a4ed057",
    "59599150-2276-4111-b241-ae0402b1298e",
]

print("Article 1 (India-Pakistan) topics:")
for tid in a1_topic_ids:
    update_topic_status(tid, "published")

print("\nArticle 2 (USCIS) topics:")
for tid in a2_topic_ids:
    update_topic_status(tid, "published")

print("\nArticle 3 (Rupee) topics:")
for tid in a3_topic_ids:
    update_topic_status(tid, "published")

print("\n══════════ DONE ══════════")
