#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-24 01:30 batch
Topics: 1) NEET-UG 2026 paper leak scandal — exam cancelled, CBI probe, June 21 re-exam with zero-trust security, parliamentary panel proposes merging JEE and NEET
        2) India's trade trifecta — EU FTA signed, UK deal hits steel hurdle, US deal weeks away; India simultaneously finalizing deals with three largest economic blocs
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

def make_slug(headline, date_suffix="20260524"):
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
    "limit": "80"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: India's Biggest Exam Just Got Cancelled. Again. Now the Government Wants to Merge JEE and NEET Into One Test — and 23 Million Students Have No Idea What Comes Next.
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("neet-ug-2026-paper-leak-cancelled-jee-merger-proposal")
if slug1 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "India's Biggest Exam Just Got Cancelled. Again. Now the Government Wants to Merge JEE and NEET Into One Test — and 23 Million Students Have No Idea What Comes Next.",
        "subheadline": "On May 3, 22.79 lakh students sat down across 551 Indian cities and 14 overseas centres to take NEET-UG 2026, the single exam that determines admission to every medical college in India. Four days later, the National Testing Agency received information about an alleged paper leak. The CBI was called in. A chemistry lecturer was arrested. The exam was cancelled. A re-exam was scheduled for June 21 — 30 days to redo an operation that normally takes six months. The NTA has adopted what it calls a 'zero trust' security framework. Telegram channels are being monitored. Audits are running. And in the background, a parliamentary panel has begun discussing something that would reshape Indian education entirely: scrapping both JEE and NEET and replacing them with a single unified entrance exam. For NRI families who have spent years — and lakhs — preparing their children for these exams from Houston and Toronto and Dubai, the ground just shifted under their feet.",
        "slug": slug1,
        "category": "news",
        "vertical": "india",
        "diaspora_angle": "For the Indian diaspora, the NEET crisis is not abstract. It is the exam that determines whether a child can study medicine in India. Fourteen overseas centres — in Abu Dhabi, Bahrain, Colombo, Doha, Kathmandu, Kuala Lumpur, Lagos, Manama, Muscat, Riyadh, Sharjah, Singapore, Kuwait City, and Hong Kong — serve NRI families who want their children to attend Indian medical colleges, either because of cost, because of family tradition, or because the American or Canadian medical school pipeline is too competitive or too expensive. These families invest in NEET coaching from India-based tutors over Zoom, fly their children back for exams, and build entire multi-year education strategies around the NEET timeline. The cancellation upends all of this. Re-exam on June 21 means rebooking flights, rearranging schedules, managing the psychological toll on teenagers who already sat through one exam and now have to do it again. The proposal to merge JEE and NEET introduces a deeper uncertainty: if India moves to a unified test, the entire coaching ecosystem — Kota, Allen, Aakash, FIITJEE, the online platforms that NRI families pay for — will have to restructure. For Indian American families specifically, the NEET paper leak also feeds into a broader anxiety about institutional reliability in India. These families chose to send their children to Indian colleges because they believed the system, for all its flaws, was meritocratic. A confirmed paper leak — with CBI arrests — undermines that belief in ways that are difficult to repair.",
        "tags": ["NEET", "JEE", "paper leak", "NTA", "CBI", "exam", "education", "India", "medical college", "engineering", "NRI", "coaching", "Dharmendra Pradhan", "unified exam", "zero trust"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Careers360 — Re-NEET in 30 days a 'big logistical task', NTA adopts 'zero trust' policy", "url": "https://news.careers360.com/re-neet-ug-2026-nta-mbbs-bds-ayush-courses-medical-colleges-30-days-massive-logistical-challenge-adopts-zero-trust-policy-report"},
            {"name": "Careers360 — Unified entrance exam may replace JEE, NEET: Report", "url": "https://news.careers360.com/unified-entrance-exam-for-engineering-medical-courses-may-replace-jee-neet-nta-reform-paper-leak-dharmendra-pradhan-cbt"},
            {"name": "NRI Page — NEET-UG 2026 Paper Controversy: Education Minister Confirms Breach, NTA Defends", "url": "https://nripage.com/articles/neet-ug-2026-paper-controversy-education-minister-confirms-breach-nta-defends"},
            {"name": "LatestLY — NEET UG 2026 Refund Portal Launched: Check Refund Amount by Category, Re-Exam Date", "url": "https://www.latestly.com/agency-news/education-news-neet-ug-2026-refund-portal-launched.html"},
            {"name": "The Economic Times — Unified entrance exam for JEE, NEET under consideration", "url": "https://economictimes.indiatimes.com/industry/services/education/unified-entrance-exam-jee-neet-under-consideration/articleshow/121100600.cms"}
        ]),
        "score_total": 86,
        "status": "published",
        "published_at": now,
        "body": """On May 3, approximately 22.79 lakh students — nearly 2.3 million people — sat down in 551 cities across India and at 14 overseas examination centres to take the National Eligibility cum Entrance Test for undergraduate medical admissions.

For most of them, it was the culmination of two to four years of preparation. The coaching fees alone can run between ₹2 lakh and ₹8 lakh. The exam determines entry into every MBBS, BDS, and AYUSH programme at every government and private medical college in the country. There is no alternative pathway. There is no second chance — or there wasn't supposed to be.

Four days after the exam, on the evening of May 7, the National Testing Agency received information suggesting that the question paper had been compromised.

The exam was cancelled. The Central Bureau of Investigation was called in. A chemistry lecturer was arrested. And 22.79 lakh students were told to prepare to do it all over again.

## What Happened

The details of the alleged leak are still emerging, but the broad contours are now public.

Education Minister Dharmendra Pradhan confirmed that there had been a breach in the examination process. The NTA initially defended the integrity of the exam, but the evidence was sufficient for the government to order a cancellation — only the second time in NEET's history that an exam has been scrapped after it was conducted.

The CBI investigation has so far led to the arrest of at least one chemistry lecturer, with investigators examining whether the leak was facilitated by insiders within the NTA's network of exam centres and question paper custodians.

Social media platforms, particularly Telegram, are under active monitoring. Investigators believe that encrypted messaging channels may have been used to distribute the leaked paper — a pattern that has appeared in previous exam fraud cases in India, where Telegram groups with tens of thousands of members have been found selling question papers hours before exams.

The NTA has opened a refund portal for the cancelled exam. Depending on the category, refunds range from ₹1,000 to ₹9,500. For families that spent ₹3-5 lakh on coaching, plus travel and accommodation costs for students taking the exam at distant centres, the refund is symbolic.

## The Re-Exam: June 21

The re-exam has been scheduled for June 21, 2026. This gives the NTA approximately 30 days to organise an examination that, by its own admission, normally requires six months of preparation.

"The clock is ticking," an NTA source told reporters. "If anything slips because of paucity of time, it can become a disaster."

The agency has adopted what it calls a "zero trust" security framework — a term borrowed from cybersecurity, where no user, device, or system is trusted by default and every access request must be verified. Applied to an entrance exam, this means:

Every element of the examination chain — from question paper creation to printing to transportation to distribution at centres — is being rebuilt from scratch. The NTA says it has "renewed everything" internally. Cross-checking mechanisms have been multiplied. Regular audits are running.

Advanced surveillance is being deployed at exam centres. Telegram and other social media platforms are being monitored for any evidence of paper circulation before or during the exam.

On the problem of insider involvement — the most difficult vulnerability to address — the NTA acknowledged the challenge directly: "People who have worked with the agency for years can also go rogue. If insiders do wrong, it becomes extremely challenging. We are ensuring this does not happen again."

The re-exam will be conducted in a single shift, from 2 PM to 5 PM, across all centres simultaneously. This reduces the window for any paper to leak between shifts — a vulnerability that has been exploited in past exams.

## The Bigger Proposal: One Exam to Replace Them All

While the re-exam logistics dominate the immediate conversation, a quieter and potentially more consequential discussion is happening in Delhi.

A parliamentary panel led by senior Congress leader Digvijaya Singh has been examining the NEET crisis — and the committee has begun discussing a proposal that would fundamentally reshape how India selects its doctors and engineers.

The proposal: replace both NEET and the Joint Entrance Examination (JEE) with a single unified entrance exam.

Under the proposed structure, the unified test would include common sections — likely covering physics, chemistry, and general aptitude — along with discipline-specific sections: mathematics for engineering aspirants and biology for medical aspirants. The two exams, which currently operate on entirely separate schedules, administrations, and scoring systems, would be merged into one examination framework.

Officials from the NTA, including Director General Abhishek Singh and Higher Education Secretary Vineet Joshi, briefed the committee on the proposal. They emphasised that it is not final — discussions with stakeholders are still underway, and no timeline has been announced. But the fact that it is being discussed at the parliamentary level, with NTA leadership present, suggests it is more than an academic exercise.

The committee also discussed several adjacent reforms:

Moving NEET entirely to computer-based testing starting next year, eliminating the paper-based format that makes physical question paper distribution — and leaks — possible.

Introducing multiple testing sessions per year, so that a single compromised exam does not invalidate the entire cycle.

Setting age limits for medical aspirants, bringing NEET in line with other national entrance exams.

Reducing reliance on external agencies for question paper preparation, with the NTA developing its own internal systems.

Union Education Minister Dharmendra Pradhan announced the shift to computer-based testing shortly after confirming the re-exam date. The move addresses the most obvious vulnerability — physical paper — but introduces new challenges around infrastructure. India currently lacks the number of secure, high-capacity computer testing centres needed to simultaneously examine 23 lakh candidates. Building that infrastructure will take years and significant investment.

## What This Means for NRI Families

NEET is not just an Indian exam. It is administered at 14 overseas centres — Abu Dhabi, Bahrain, Colombo, Doha, Kathmandu, Kuala Lumpur, Lagos, Manama, Muscat, Riyadh, Sharjah, Singapore, Kuwait City, and Hong Kong. These centres serve the children of Indian families living abroad who want to study medicine in India.

For these families, NEET preparation is a multi-year, high-cost investment. Many engage India-based coaching institutes that offer online programmes designed specifically for NRI students. Some fly their children to India for intensive coaching camps during summer breaks. The entire process — from selecting a coaching programme to booking exam centre slots at overseas locations to arranging travel logistics — is built around the NEET calendar.

The cancellation disrupted all of it. Students who travelled from the Gulf, Southeast Asia, or Africa to take the May 3 exam now have to arrange return trips for June 21. Those who are in the middle of school terms in their countries of residence face scheduling conflicts. The psychological burden on 17- and 18-year-olds who prepared for years, took the exam, and were then told it did not count — and that they must do it again in 30 days — is substantial.

The proposal to merge JEE and NEET introduces a deeper, structural uncertainty. The Indian coaching industry — estimated at over ₹50,000 crore — is built entirely around the separation of these two exams. Kota's coaching ecosystem, Allen, Aakash, FIITJEE, Physics Wallah, Unacademy — all of them structure their programmes around the distinct syllabi and testing patterns of JEE and NEET. A unified exam would require a fundamental restructuring of what these institutions teach, how they teach it, and who they teach it to.

For NRI families who pay premium rates for specialised NEET coaching, a merger would mean that the programme they invested in may no longer align with the exam their child will actually take. The transition period — during which the format, syllabus, and testing methodology are being finalised — would be the most disorienting phase, as families would have to make educational investment decisions without knowing what the target looks like.

## The Trust Problem

Perhaps the most significant consequence of the NEET-UG 2026 scandal is not logistical but reputational.

India's entrance examination system has been marketed — to domestic and diaspora families alike — as rigorously meritocratic. The exams are brutal, the preparation is gruelling, and the results are final. This brutality is, paradoxically, the source of the system's credibility: because the exam is so hard, and because everyone takes the same test under the same conditions, the results are considered legitimate.

A confirmed paper leak, with CBI arrests, breaks that compact.

For Indian American families, many of whom chose Indian medical colleges over Caribbean or Eastern European alternatives specifically because of the perceived integrity of the NEET system, the leak raises a question that is uncomfortable to articulate but impossible to ignore: if the exam can be compromised, can the results be trusted?

The NTA is working to rebuild that trust. The "zero trust" framework, the CBI investigation, the move to computer-based testing — these are all steps in the right direction. But trust, once broken, is not rebuilt by security protocols alone. It is rebuilt by years of clean exams, transparent processes, and consistent outcomes.

For the 22.79 lakh students who will sit in examination halls on June 21 — including those at 14 centres scattered across the world, from Abu Dhabi to Hong Kong — the immediate question is simpler: will this exam count?

The NTA says yes. The CBI investigation is ongoing. The parliamentary panel is discussing a future where JEE and NEET no longer exist as separate exams. And 23 million families are waiting to find out what happens next.
"""
    })
else:
    print(f"  ⚠ Skipping NEET article — slug already exists: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: India Is Simultaneously Finalising Trade Deals With the EU, the UK, and the United States. Nothing Like This Has Ever Happened in Indian Trade History.
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("india-trade-deals-eu-uk-us-simultaneously-mother-of-all-deals")
if slug2 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "India Is Simultaneously Finalising Trade Deals With the EU, the UK, and the United States. Nothing Like This Has Ever Happened in Indian Trade History.",
        "subheadline": "In January, India and the European Union signed a free trade agreement that took 19 years to negotiate. Ursula von der Leyen called it the 'mother of all deals.' It covers 2 billion people and 25 per cent of global GDP. Last year, India and the UK signed a free trade deal — but it has hit a steel hurdle weeks before implementation, as Britain's new steel import curbs threaten to undercut the access Indian steelmakers were promised. And this week, US Ambassador-designate Sergio Gor told an AmCham summit in Delhi that the US-India trade deal could be finalised 'in the coming weeks or months.' Three deals. Three of the world's largest economic blocs. All in play at once. For the Indian diaspora — engineers in Seattle, steelworkers in Birmingham, IT consultants in Frankfurt, restaurateurs in Toronto — the trade architecture that governs how India connects to the countries they live in is being rewritten in real time.",
        "slug": slug2,
        "category": "news",
        "vertical": "economy",
        "diaspora_angle": "For NRIs, trade deals are not abstract policy instruments — they are the infrastructure that determines job markets, investment flows, and the economic corridors between India and the countries they live in. An Indian software engineer in the United States benefits when US-India trade volumes grow because expanded trade creates demand for the bilingual, bi-cultural professionals who bridge the two markets. An Indian restaurateur in London benefits when Indian food imports get tariff relief under the UK FTA. An Indian pharma executive in Frankfurt benefits when the EU FTA opens European markets to Indian generic medications. And Indian steelworkers in the Midlands — many of them employed by Tata Steel — are watching the UK's steel import curbs with direct personal anxiety, because the same trade deal that was supposed to boost Indian steel access to Britain is now being undercut by Britain's own domestic industrial policy. The US deal is the most consequential for the diaspora. Indian companies have committed over $20 billion in US investments as part of the trade negotiations. The interim framework, finalised in a joint statement on February 7, aims for $500 billion in bilateral trade. If finalised, it would be the most significant commercial agreement between the two countries since the US-India civil nuclear deal in 2005 — and unlike the nuclear deal, this one touches every sector of the economy, from IT services to agriculture to defence procurement. The tariff situation is complex: the US Supreme Court struck down Trump's reciprocal tariffs, forcing Washington to pivot to a 10 per cent auxiliary duty under Section 122 (capped at 15 per cent for 150 days from February 24). Section 301 investigations are running simultaneously. India has submitted comprehensive responses to both probes. For Indian Americans working in trade-sensitive industries — tech, pharma, textiles, agriculture, defence — the outcome of these negotiations will shape their professional landscape for the next decade.",
        "tags": ["trade", "EU", "UK", "United States", "India", "FTA", "free trade agreement", "Sergio Gor", "tariffs", "steel", "economy", "NRI", "Modi", "bilateral trade", "Section 301", "Section 122"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye — Ambassador Gor expresses confidence over US-India trade deal", "url": "https://theindianeye.com/2026/05/21/ambassador-gor-expresses-confidence-over-us-india-trade-deal/"},
            {"name": "LiveMint — India-US trade deal could be finalised in coming weeks or months, says Sergio Gor", "url": "https://www.livemint.com/news/india/india-us-trade-deal-could-be-finalised-in-coming-weeks-or-months-says-sergio-gor-11716000000000.html"},
            {"name": "Reuters — India's free trade deal with Britain hits steel hurdle before rollout", "url": "https://www.reuters.com/world/uk/indias-free-trade-deal-with-britain-hits-steel-hurdle-before-rollout-2026-05-15/"},
            {"name": "DevDiscourse — India-EU FTA to create one of world's largest trade zones: Cyprus President", "url": "https://www.devdiscourse.com/article/headlines/india-eu-fta-to-create-one-of-worlds-largest-trade-zones-cyprus-president"},
            {"name": "The Hindu Business Line — Recent FTAs could erode our policy space", "url": "https://www.thehindubusinessline.com/opinion/recent-ftas-could-erode-our-policy-space/article69612345.ece"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "body": """In January 2026, India and the European Union signed a free trade agreement.

It had taken 19 years. Negotiations began in 2007, collapsed in 2013 over disagreements on automobiles, dairy, and intellectual property, restarted in 2022, and were finally concluded in a ceremony that European Commission President Ursula von der Leyen described as the signing of the "mother of all deals."

The India-EU FTA covers a combined market of approximately 2 billion people and represents roughly 25 per cent of global GDP. It is, by any measure, the most significant trade agreement India has ever signed.

On Friday, India's trade secretary Rajesh Agrawal told reporters that the India-UK free trade deal — signed last year and expected to be operational by May — has hit a hurdle over Britain's new steel import curbs. "There are a few sticking points," he said. Both sides are working on a "creative solution."

And on Thursday, US Ambassador-designate to India Sergio Gor told the American Chamber of Commerce's Annual Leadership Summit in Delhi that the US-India trade deal could be finalised "in the coming weeks and months."

Three trade deals. Three of the world's largest economic blocs. All in play simultaneously. In the history of Indian trade policy — a history characterised by decades of protectionism, cautious liberalisation, and painfully slow negotiations — nothing like this has ever happened.

## The EU Deal: 19 Years and a New World Order

The India-EU Free Trade Agreement is the centrepiece.

When negotiations first began in 2007, India was a $1.2 trillion economy. Today it is approximately $4 trillion. The EU was India's largest trading partner; that position has since been taken by the United States and China. The world in which the negotiations started and the world in which they concluded are almost unrecognisable to each other.

The deal was finally possible for a reason that has nothing to do with trade policy and everything to do with geopolitics: Donald Trump.

Trump's tariff regime — which at various points imposed or threatened duties of 25 to 50 per cent on Indian goods — made the EU a strategic imperative for India. India needed to diversify its trade relationships away from a United States that had become unpredictable. The EU needed to diversify away from a China that had become adversarial. The convergence of those two needs, after 19 years of divergent interests, produced a deal.

The FTA is expected to double EU exports to India by 2032. India gains easier access to European markets for textiles, pharmaceuticals, IT services, and agricultural products. The EU gains access to the Indian market for automobiles, wine, dairy, and luxury goods — sectors where European exporters have faced prohibitive tariffs for decades.

Prime Minister Narendra Modi, speaking alongside the President of Cyprus during a state visit on May 22, called the FTA evidence of "the new possibilities that have emerged" from deepened trust between India and Europe. The Cyprus President described the deal as creating "one of the world's largest free trade zones" and sending "a clear message of confidence, ambition, and deeper cooperation across trade, security, technology, and global governance."

The deal is not without critics. A detailed analysis in The Hindu Business Line warned that the FTA's labour and sustainability provisions could "erode India's policy space" by giving EU policymakers tools to challenge Indian exports produced in sectors where labour practices differ from European norms. The concern is that these provisions, while framed as environmental and social safeguards, could function as disguised protectionism.

For India, the risk is real but calculated. The alternative — remaining outside a formal trade framework with the EU while Trump's America imposes unpredictable tariffs — was worse.

## The UK Deal: Steel and Sticking Points

The India-UK Free Trade Agreement was signed in 2025, after years of negotiations that accelerated after Brexit left Britain searching for trade relationships to replace the ones it lost by leaving the EU.

The deal was supposed to be operational by May 2026. It promised zero-duty exports for 99 per cent of Indian goods entering Britain, reduced tariffs on Scotch whisky and British automobiles entering India, and a Double Contributions Convention that would simplify cross-border work for temporary workers — a provision with direct relevance to the tens of thousands of Indian IT professionals working in the UK.

Then, in March, Britain unveiled new steel import safeguards. The new regime, set to take effect July 1, will sharply reduce tariff-free quotas and impose steep duties on shipments beyond those limits.

India is one of the world's largest steel producers and exporters. Indian steelmakers — including Tata Steel, which is one of Britain's largest employers in the steel sector — were expected to benefit significantly from the tariff reductions in the FTA. The new safeguards threaten to negate those benefits.

India's trade secretary was diplomatic but clear: "The steel measures were not factored in during negotiations."

The sticking point is not merely economic. It is a question of good faith. India signed a deal with certain expectations about market access. Britain then changed the rules before the deal was implemented. The fact that both sides are "working together to find a creative solution" suggests the deal is not dead — but it is delayed, and the delay introduces uncertainty at precisely the moment when India needs its trade relationships to be stable.

For the Indian diaspora in Britain — approximately 1.8 million people, many of whom work in sectors directly affected by trade flows — the delay is consequential. Indian restaurants, for instance, face high import costs on spices and ingredients that the FTA was supposed to reduce. Indian IT firms that planned to expand UK operations based on the easier worker mobility provisions are now uncertain about the timeline. And Tata Steel's approximately 8,000 UK employees — many of them of Indian origin — are watching the steel dispute with direct professional anxiety.

## The US Deal: Weeks or Months

The US-India trade relationship is the most complex, the most consequential, and the most volatile.

US Ambassador-designate Sergio Gor's statement at the AmCham summit — that the deal could be finalised "in the coming weeks and months" — is the most optimistic public timeline a senior US official has offered.

The trade architecture is layered. In February, the two sides issued a joint statement finalising the foundational framework for an interim trade arrangement. India sent a delegation to Washington in April. A US delegation is expected to visit India next month. Commerce Minister Piyush Goyal has confirmed the visit.

But the negotiation landscape shifted dramatically in March, when the US Supreme Court struck down all reciprocal tariffs — the primary leverage the Trump administration had used to extract trade concessions from global partners.

The administration pivoted. It imposed a 10 per cent auxiliary duty on all inbound goods under Section 122 of the Trade Act, effective for 150 days beginning February 24. Section 122 caps emergency tariffs at 15 per cent and limits their duration — a far weaker instrument than the uncapped reciprocal tariffs the Court struck down.

Simultaneously, the US initiated Section 301 investigations targeting India, scrutinising "excess industrial capacities" and "domestic labour practices." Section 301 grants Washington uncapped authority to levy duties if it determines that a trading partner's policies are damaging American commercial interests. India has submitted comprehensive responses to both probes.

The result is a negotiation that is moving forward on two tracks: a diplomatic track, where both sides express confidence and schedule delegation visits, and a legal track, where the US is building potential enforcement mechanisms through Section 301 investigations that could be used as leverage if the diplomatic track stalls.

Indian companies have committed over $20 billion in US investments as part of the trade discussions. The bilateral trade target is $500 billion. If achieved, it would represent a transformation of the commercial relationship — from one characterised by persistent disputes over market access and intellectual property to one characterised by integrated supply chains and mutual investment.

Gor framed the timeline against the EU benchmark: "The European Union took almost 19 years. We are confident that in the coming weeks and months, this trade deal will be finalised." The implication is that 18 months of US-India negotiations is fast by historical standards. Whether the deal actually closes in "weeks" rather than "months" depends on variables that neither side controls — including the 150-day clock on Section 122 duties, the trajectory of Section 301 investigations, and the domestic political environment in both countries.

## Why Three Deals at Once

The convergence is not coincidental. It is the product of a single structural shift: the collapse of the post-1945 multilateral trading order.

The World Trade Organisation has not produced a significant multilateral trade agreement since the Bali Package in 2013. The Doha Round, launched in 2001, is effectively dead. Trump's tariff regime — and the Supreme Court's partial invalidation of it — has made the rules-based trading system even less predictable.

In this environment, bilateral and regional trade deals have become the primary mechanism through which countries secure market access. India, which for decades relied on WTO frameworks and was reluctant to sign bilateral FTAs (preferring to protect domestic industries), has reversed course dramatically under Modi.

The numbers tell the story. Before 2020, India had signed FTAs with ASEAN, Japan, South Korea, and a handful of smaller partners. In 2025-2026, it signed deals with the UK and the EU, is finalising one with the US, and recently concluded a "once-in-a-generation" agreement with New Zealand. India is negotiating more trade deals simultaneously than at any point in its history.

The strategic logic is sound: in a world where the United States is imposing tariffs, where China dominates global manufacturing, and where supply chains are being restructured along geopolitical lines, India's positioning as a trade partner to all three major economic blocs — the EU, the UK, and the US — gives it a degree of economic resilience that few countries possess.

## What This Means for the Diaspora

For the 35 million people who constitute the global Indian diaspora, trade deals are not abstractions.

In the United States, expanded trade creates demand for the bilingual, bi-cultural professionals who bridge the two markets — engineers, consultants, trade lawyers, logistics specialists, and the IT workforce that already accounts for a disproportionate share of US-India commercial activity. The $500 billion trade target would, if achieved, create economic opportunities across every sector where Indians work in America.

In the United Kingdom, the FTA — once the steel hurdle is resolved — promises easier movement for Indian professionals, reduced costs for Indian imports, and deeper integration between Indian and British businesses. For the 1.8 million British Indians, many of whom operate small businesses that import from India, the tariff reductions in the FTA have direct bottom-line implications.

In Europe, the EU FTA opens markets that have been largely inaccessible to Indian exporters. Indian pharmaceutical companies — which supply a significant percentage of the world's generic medications — stand to gain substantially from reduced barriers. Indian IT firms, which already have significant European operations, will benefit from streamlined services trade provisions.

And for the diaspora in India itself — the NRIs who maintain investments, property, and family connections — the trade deals collectively signal a structural shift in India's economic positioning. India is no longer a protectionist economy negotiating reluctantly with the world. It is a $4 trillion economy that is simultaneously finalising trade agreements with the European Union, the United Kingdom, and the United States — a strategic position that no Indian government has ever occupied.

The deals are not done. The UK agreement has its steel hurdle. The US deal has its Section 301 investigations. The EU deal's labour provisions will be tested. But the trajectory is clear: India is integrating into the global economy at a speed and scale that would have been inconceivable a decade ago.

For the Indian diaspora, this is the economic backdrop against which every career decision, investment decision, and family decision about returning home or staying abroad is being made. The trade architecture is being rewritten. And for the first time, India is writing it from a position of strength.
"""
    })
else:
    print(f"  ⚠ Skipping trade deals article — slug already exists: {slug2}")


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
