#!/usr/bin/env python3
"""Videshi Writer — NEWS categories batch run."""
import os, json, uuid, datetime, requests, re, sys
from pathlib import Path

# Load env from file
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_ANON_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

TODAY = "20260519"
NOW_ISO = datetime.datetime.now(datetime.timezone.utc).isoformat()

def slug_from(headline, suffix=TODAY):
    s = headline.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'\s+', '-', s)
    s = s[:70].rstrip('-')
    return f"{s}-{suffix}"

def upsert_article(article):
    """Insert article into p2_articles."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers={**HEADERS, "Prefer": "return=representation"},
        json=article
    )
    if r.status_code not in (200, 201):
        print(f"  ERROR inserting article: {r.status_code} {r.text}")
        return None
    data = r.json()
    aid = data[0]["id"] if isinstance(data, list) else data["id"]
    print(f"  ✅ Inserted article: {aid}")
    return aid

def mark_topic(topic_id, status):
    """Update topic status."""
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_topics?id=eq.{topic_id}",
        headers=HEADERS,
        json={"status": status, "updated_at": NOW_ISO}
    )
    print(f"  Topic {topic_id[:8]} → {status} ({r.status_code})")

# ═══════════════════════════════════════════════════════════════
# ARTICLE 1 — nri-world
# ═══════════════════════════════════════════════════════════════
ARTICLE_1 = {
    "headline": "A Roommate, a ChatGPT Search History and Two Bangladeshi Doctoral Students Found Dead in Tampa",
    "subheadline": "Prosecutors say Hisham Abugarbieh used AI to plan the killings of Nahida Bristy and Zamil Limon, both 27. The death penalty case has shaken South Asian student communities across America.",
    "slug": slug_from("roommate-chatgpt-search-bangladeshi-doctoral-students-tampa"),
    "category": "nri-world",
    "status": "published",
    "published_at": NOW_ISO,
    "score_total": 82,
    "body": """The details read like a true-crime podcast pitched to maximum horror. Two University of South Florida doctoral students — Nahida Bristy and Zamil Limon, both 27, both from Bangladesh — vanished in mid-April from the Tampa apartment they shared with a third roommate. By the time detectives traced the digital breadcrumbs, the roommate, Hisham Abugarbieh, stood accused of murdering both in what prosecutors call a cold, calculated, premeditated act. On Monday, he was arraigned in Hillsborough County on eight charges. Florida is seeking the death penalty.

The most chilling element is not the crime itself but the alleged instrument of its planning. Court filings reveal that Abugarbieh turned to ChatGPT in the days before the killings, asking questions so explicit that even the chatbot flagged them as dangerous. "What happens if a human has a put in a black garbage bag and thrown in a dumpster," one query read. "How would they find out," he followed up. His Amazon purchase history, prosecutors say, filled in the operational gaps: duct tape, trash bags, lighter fuel and fire starter.

**A pattern that terrifies parents back home**

For the roughly 330,000 Indian and South Asian students enrolled in American universities — and the millions of families financing those degrees from savings accounts in Dhaka, Mumbai and Lahore — the case lands on an already raw nerve. Bristy and Limon are the latest in a grim series: at least five students of Indian or South Asian origin have died under violent or suspicious circumstances in the United States this year alone, a tally that has turned diaspora WhatsApp groups into anxiety hotlines.

The specifics vary — a stabbing in an off-campus housing dispute here, an unsolved hit-and-run there — but the underlying dread is identical. Parents who emptied provident funds to send children to American graduate programmes are asking the question that no orientation brochure answers: who is my child living with?

**The roommate lottery**

American universities, particularly at the doctoral level, routinely leave housing to the market. Students piece together shared apartments on Craigslist, Facebook groups and word-of-mouth referrals, with background checks that range from cursory to non-existent. Abugarbieh, prosecutors note, had a prior violent felony conviction — a fact that would have appeared on even a basic screening but evidently did not prevent him from sharing a lease with two international students unfamiliar with the American criminal-records system.

The structural problem is not uniquely South Asian, but the vulnerability is amplified for international students who arrive without the social networks, family safety nets or cultural fluency to evaluate risk. Many come from countries where co-living with strangers is uncommon; the concept of a Craigslist roommate carries none of the red-flag awareness that American-born students absorb growing up.

**A legal test for AI accountability**

The case also feeds a growing legal debate over the role of AI chatbots in premeditated crime. Florida State Attorney Andrew Warren's office has explicitly cited Abugarbieh's ChatGPT interactions as evidence of premeditation — the digital equivalent of a killer Googling "how to dispose of a body" but with a conversational AI that, in this instance, responded before attempting to shut the line of questioning down.

This is not the first such instance. In 2025, a Connecticut man who killed his mother was found to have had extended conversations with ChatGPT that reinforced his paranoid delusions, prompting a lawsuit against OpenAI and Microsoft. The Tampa case pushes the frontier further: if a chatbot's responses can be introduced as evidence of a calculated murder plan, platforms may face mounting pressure to implement real-time intervention protocols that go beyond the current "that sounds dangerous" warnings.

**What the diaspora is demanding**

Indian and Bangladeshi student organisations in Florida have called for universities to provide verified housing referral databases with mandatory background checks for all tenants, not just those in on-campus dormitories. The Federation of Indian Students of Tampa Bay has petitioned USF's administration for a dedicated international student safety liaison — a demand echoed at campuses from Purdue to the University of Illinois, where similar tragedies have prompted similar asks.

For the families of Bristy and Limon, the procedural recommendations are almost unbearably abstract. Two young researchers who crossed an ocean to study are dead, and the instrument of their killing's planning was, in part, a chatbot that anyone can access for free.

The arraignment continues in December. Abugarbieh has pleaded not guilty. The courtroom, when it convenes, will adjudicate one man's culpability. But the verdict that matters most to the diaspora — whether America can keep its international students safe — will take far longer to deliver."""
}

# ═══════════════════════════════════════════════════════════════
# ARTICLE 2 — news
# ═══════════════════════════════════════════════════════════════
ARTICLE_2 = {
    "headline": "Assam Becomes the Fourth Indian State to Approve a Uniform Civil Code — With a Crucial Tribal Exemption",
    "subheadline": "Chief Minister Himanta Biswa Sarma's post-election UCC push covers marriage, divorce and succession but carves out protections for the Northeast's indigenous communities, setting up a constitutional tightrope walk that the diaspora is watching closely.",
    "slug": slug_from("assam-fourth-state-uniform-civil-code-tribal-exemption"),
    "category": "news",
    "status": "published",
    "published_at": NOW_ISO,
    "score_total": 78,
    "body": """Days after being sworn in for a second consecutive term, Assam Chief Minister Himanta Biswa Sarma moved with the speed of a man ticking off an election manifesto in real time. On May 13, his Cabinet approved the draft Uniform Civil Code Bill — making Assam the fourth state after Uttarakhand, Goa and Gujarat to advance a common framework governing marriage, divorce, inheritance and succession. The Bill is set to be tabled in the state assembly on May 26.

The headline, though, is not the approval. It is the exemption. Assam's version of the UCC will explicitly exclude tribal communities from its scope — a carve-out that acknowledges the political and constitutional reality of governing a state where autonomous tribal districts, matrilineal inheritance systems and customary clan governance are not relics of the past but the functioning architecture of everyday life.

**A code tailored for Assam**

The Bill covers compulsory registration of marriages and divorces, sets legal marriage ages, regulates live-in relationships and introduces restrictions on polygamy. For non-tribal Assamese — Hindu, Muslim, Christian and others — these provisions would replace the patchwork of religion-specific personal laws that currently govern family matters.

Sarma framed the legislation as the fulfilment of a campaign promise, noting that the code had been "customised for Assam's specific requirements." The full text has not been published, but the contours suggest a more localised document than the national UCC framework that the BJP has championed at the federal level for decades under Article 44 of the Directive Principles.

**Why the tribal exemption matters**

The exemption is not cosmetic. Assam is home to multiple tribal-majority autonomous districts — Karbi Anglong, Dima Hasao and Bodoland among them — governed under the Sixth Schedule of the Constitution, which explicitly protects indigenous systems of land management, social administration and customary practice. Attempting to override those protections through a state-level UCC would trigger a constitutional crisis and, more practically, a political firestorm across the Northeast.

The anxiety is already evident. In Meghalaya, where Khasi and Jaintia communities follow a matrilineal inheritance system in which ancestral property passes through the youngest daughter (known as *Ka Khadduh*), observers worry that Assam's move could eventually open debates about tribal protections elsewhere. In Nagaland and Mizoram, Articles 371A and 371G provide even stronger shields against legislative interference with customary laws — but the precedent of a neighbouring state legislating a UCC, even with exemptions, has put communities on alert.

BJP MLA Rupali Langthasa, who represents a tribal-majority constituency in Dima Hasao, moved quickly to reassure constituents, saying tribal life and traditions would continue "as it has for centuries." The speed of the reassurance itself revealed the political sensitivity involved.

**The NRI dimension**

For the Indian diaspora, the UCC debate carries a distinctive charge. Overseas Indians navigating Western legal systems that impose uniform civil codes by default — a single marriage law, a single inheritance framework, no religious exemptions — often view India's patchwork with a mixture of exasperation and sentimentality. The exasperation comes from dealing with the bureaucratic consequences: NRIs settling family estates in India frequently encounter conflicting personal laws that delay property transfers, complicate succession claims and spawn litigation that outlasts the original disputants.

The sentimentality is rooted in identity. For many diaspora Hindus, the UCC has become a cultural touchstone — a symbol of the modern, reformed India they wish to see when they return home. For diaspora Muslims, it often reads as the majoritarian erasure of religious autonomy. Both positions harden in the echo chambers of overseas political organisations, making the UCC one of the most reliably divisive topics at any Indian community gathering from Edison to Southall.

Assam's tribal exemption adds a new layer to that conversation. It demonstrates that even the BJP, the party most vocally committed to a national UCC, recognises that uniformity cannot be imposed on communities whose governance structures predate the Indian republic. That nuance tends to get lost in diaspora debates, where the UCC is often discussed as a binary — modern vs. medieval, reform vs. regression.

**What comes next**

The Bill goes to the Assam assembly on May 26, where the BJP's comfortable majority virtually guarantees passage. The real contest will begin afterward, in the courts. Opposition parties are expected to challenge provisions on constitutional grounds, and legal scholars have already flagged potential friction between the UCC's marriage registration mandates and existing protections under the Sixth Schedule.

For New Delhi, Assam's move is another incremental step toward a national code — a project that remains politically aspirational at the federal level but is being assembled, brick by brick, through willing state legislatures. For the Northeast, it is a reminder that the Indian republic's oldest tension — between national cohesion and regional autonomy — is still very much alive."""
}

# ═══════════════════════════════════════════════════════════════
# ARTICLE 3 — technology
# ═══════════════════════════════════════════════════════════════
ARTICLE_3 = {
    "headline": "Wadhwani and Gates Foundations Join Forces to Build 250 Innovation Hubs Across India in Five Years",
    "subheadline": "The partnership, anchored by a diaspora-founded philanthropic giant and the world's largest private health funder, aims to turn India's academic research into startups, products and jobs at a national scale.",
    "slug": slug_from("wadhwani-gates-foundations-250-innovation-hubs-india"),
    "category": "technology",
    "status": "published",
    "published_at": NOW_ISO,
    "score_total": 76,
    "body": """The Wadhwani Foundation and the Bill & Melinda Gates Foundation have signed a Memorandum of Understanding to expand India's innovation ecosystem through the National Innovation Network (NIN) — a collaboration that pairs one of the diaspora's most prominent philanthropic institutions with the world's largest private funder of global health research.

The deal is built on a simple premise with ambitious arithmetic: more than 250 Centres of Excellence across India within three to five years, each designed to bridge the gap between laboratory research and market-ready products. The Gates Foundation will directly support five NIN Centres of Excellence over the first five years, beginning with two this year.

**From WIN to NIN**

The National Innovation Network is the national-scale extension of the Wadhwani Innovation Network (WIN), which Prime Minister Narendra Modi launched in April 2025 to connect academia, industry and funding partners in a structured pipeline from research to commercialisation. WIN has already supported more than 50 projects across health tech, biotech, medtech and quantum technology, establishing Centres of Excellence at IIT Bombay, IIT Madras, IIT Kanpur, IIT Delhi, IIT Hyderabad, IIT (ISM) Dhanbad, the Indian Institute of Science and C-Camp.

The upgrade to NIN represents a shift from flagship institutions to national coverage. "Super Hubs" at IIT Kanpur and IIT Bombay will anchor the network's AI, health and biotechnology research, while the 250-plus CoEs will extend the model to second- and third-tier institutions that have talent but lack the infrastructure, mentorship and capital connections to turn papers into products.

"WIN has demonstrated that India's innovation potential can be unlocked when researchers, institutions, industry and capital come together with a shared mission," said Dr. Ajay Kela, CEO of the Wadhwani Foundation. The NIN initiative, he added, would support researchers and entrepreneurs "in turning scientific ideas into products, startups and large-scale social impact."

**The Gates calculus**

For the Gates Foundation, the partnership is a bet on Indian institutions as origination points for solutions to global health challenges — not just recipients of technology designed elsewhere. Archana Vyas, director of the India Country Office, was explicit about the thesis: "Some of the most consequential health and nutrition innovations of the next decade will originate in Indian institutions."

The focus areas — health, nutrition, biotechnology, genomics, medtech and emerging sectors — align with the Gates Foundation's existing India portfolio, which has historically concentrated on disease eradication, maternal health and sanitation. What changes with NIN is the mechanism: instead of funding specific research projects, the foundation is investing in the infrastructure that converts research outputs into scalable, affordable products — the testing, prototyping, piloting, patenting and commercialisation steps that Indian academia has traditionally been weakest at.

**A diaspora blueprint**

The Wadhwani Foundation itself is a case study in how diaspora capital can reshape Indian institutions. Founded by Sunil Wadhwani, a Pittsburgh-based tech entrepreneur who built iGate into one of India's largest IT services companies before selling it to CapGemini for $4 billion in 2015, the foundation has donated over ₹110 crore to establish the Wadhwani School of Data Science and AI at IIT Madras and has poured resources into vocational training, entrepreneurship and now translational research.

The NIN model — diaspora-funded foundation provides the operational framework, global philanthropy provides the capital, Indian government provides the institutional network, and private sector provides the market pull — could become a replicable template. For NRIs who have long debated how to channel resources into India beyond temple donations and family remittances, the Wadhwani-Gates partnership offers something more systemic: a platform where philanthropic investment connects directly to job creation, startup formation and technology sovereignty.

**The scale challenge**

The ambition is not modest: 250-plus CoEs in a country where even the IITs struggle with technology transfer offices and patent commercialisation. India files roughly 90,000 patents annually (compared to China's 1.6 million and America's 600,000), and the vast majority of academic research never leaves the journal page.

NIN's bet is that the bottleneck is not talent or ideas but the connective tissue between lab and market. If the 250 CoEs can function as miniature technology transfer ecosystems — with standardised processes for prototyping, IP management, industry partnerships and startup incubation — India's innovation output could shift from incremental to structural.

The first two Gates-supported Centres of Excellence are expected to begin operations this year. The real measure of success will come in three to five years: how many of those 250 hubs produce products that reach patients, farmers and consumers rather than filing cabinets."""
}

# ═══════════════════════════════════════════════════════════════
# ARTICLE 4 — markets-finance
# ═══════════════════════════════════════════════════════════════
ARTICLE_4 = {
    "headline": "California Wants to Tax Your Cloud Software. For 500,000 Indian Tech Workers, the Bill Just Got Personal.",
    "subheadline": "Governor Newsom's proposed 8.25% levy on SaaS, AI APIs and digital downloads is designed to close a $42 billion deficit. It could also accelerate the exodus of H-1B talent to Texas.",
    "slug": slug_from("california-software-tax-indian-tech-workers-h1b"),
    "category": "markets-finance",
    "status": "published",
    "published_at": NOW_ISO,
    "score_total": 78,
    "body": """Governor Gavin Newsom has a $42 billion hole in California's budget and a plan to fill a large chunk of it by taxing the one thing Silicon Valley produces more of than anything else: software. On May 18, as part of his revised 2026-2027 budget proposal, Newsom unveiled a Digital Software and AI Services Tax that would apply California's sales tax — at a rate of 8.25% — to cloud software subscriptions, digital downloads and artificial intelligence API usage. The Department of Finance estimates the levy could generate $7.5 billion annually.

For the roughly 500,000 Indian-origin technology professionals working in California — many on H-1B visas tied to specific employers and specific geographies — the proposal is not merely a policy debate. It is a direct threat to the ecosystem that employs them, the companies that sponsor them and the cost calculus that keeps them in the most expensive state in America.

**What gets taxed**

The proposal targets three broad categories. First, Software-as-a-Service (SaaS): enterprise and consumer subscriptions from Microsoft 365 to Salesforce to Adobe Creative Cloud. Second, AI infrastructure: enterprise fees for training and deploying AI models, including API calls to OpenAI, Google Gemini and Anthropic. Third, consumer digital goods: streaming subscriptions, cloud storage and digital game purchases.

The legislative logic is straightforward. When software was sold on CD-ROMs, California taxed it. When the same functionality moved to the cloud, the tax disappeared. Newsom's argument is that the state's tax code has not kept up with the digital economy's shift from physical to subscription, creating an accidental tax shelter for the industry's fastest-growing revenue streams.

**Silicon Valley's fury**

The backlash was instantaneous. A coalition including the Silicon Valley Leadership Group and TechNet called the proposal a "job killer" that would chill AI investment at precisely the moment California is fighting to retain startups against aggressive recruitment from Texas and Florida. Tech investor Sriram Krishnan — himself an Indian-American who advised the Trump transition on AI policy — warned that "introducing an 8.25% surcharge on the core input of AI development — compute power — is economic suicide."

The criticism is not purely self-interested. A tax on SaaS subscriptions cascades downward: every small business in California that uses Slack, Zoom and QuickBooks would see costs rise. Every startup burning through cloud compute credits would face a new line item. And every large employer weighing whether to expand in San Jose or relocate to Austin would add 8.25% to the California column of their spreadsheet.

**The H-1B geography trap**

For Indian tech workers, the stakes are compounded by immigration law. An H-1B visa is tied to a specific employer in a specific location. If Salesforce, for example, decided to shift engineering headcount from San Francisco to Dallas in response to the tax — a scenario that is speculative but not fanciful given the company's recent cost-cutting moves — Indian engineers on H-1B visas would need employer-initiated transfers and potentially new visa filings to follow. Those who have filed green card applications through California-based employers face even more complex logistics, as changing work locations can trigger administrative complications in the already glacial EB-2/EB-3 processing pipeline.

The broader trend is already visible. Texas has added more than 60,000 tech jobs since 2023, many of them transfers from California. Florida's zero state income tax has made Miami and Tampa magnets for AI startups. A dedicated software tax would accelerate that gravity shift — and the Indian professionals who make up roughly 70% of H-1B visa holders would be among the most directly affected.

**The NRI money angle**

There is a secondary impact that extends to India. California's Indian tech workforce remits billions annually to family members, funds real estate purchases in Hyderabad and Bengaluru, and invests in Indian startups through angel networks based in the Bay Area. A tax that raises the cost of operating in California — or worse, prompts employers to cut headcount — would ripple through the remittance corridors that connect Cupertino to Kothapet, Mountain View to Marathahalli.

The tax also arrives at a politically charged moment. The Trump administration has signalled hostility toward state-level digital services taxes that it views as duplicating federal authority, and California's move mirrors similar levies in the UK and Canada that drew US trade retaliation. Indian workers, already navigating the twin pressures of visa uncertainty and tech layoffs, now find themselves caught in a fiscal battle between Sacramento and Silicon Valley.

**What happens next**

The proposal needs to pass California's legislature by mid-June to be included in the final budget. Progressive Democrats view it as overdue revenue from profitable tech conglomerates; moderate Democrats in tech-heavy districts see a career-ending vote. The tech lobby has until the deadline to negotiate exemptions — particularly for AI compute, which the industry insists is an input cost, not a consumer purchase.

For the half-million Indians who call California's tech corridor home, the outcome will determine whether the most lucrative address in the global knowledge economy remains worth the price."""
}

# ═══════════════════════════════════════════════════════════════
# PUBLISH
# ═══════════════════════════════════════════════════════════════
articles = [
    (ARTICLE_1, "77cf7965-d733-4c8b-b548-07c44426379b"),
    (ARTICLE_2, "95a42161-5d1d-44ee-bce8-3666eee67c3f"),
    (ARTICLE_3, "0e356c96-3fb3-4a4e-9d29-9f9f967c2274"),
    (ARTICLE_4, "d1e27dc5-5b53-4bb9-ba66-77d836c68d5d"),
]

published_ids = []
for article, topic_id in articles:
    print(f"\n📝 Publishing: {article['headline'][:60]}...")
    aid = upsert_article(article)
    if aid:
        published_ids.append((aid, article['headline'], article['category']))
        mark_topic(topic_id, "published")
    else:
        mark_topic(topic_id, "rejected")

# Also reject some lower-relevance topics that overlap with already-published content
reject_topics = [
    # Adani settlement - already published
    "2d8acda5-11dc-4734-a11e-af2a562375eb",
    # Meta layoffs - already published as "Meta Is Cutting 8,000 Jobs"
    "245ab235-d163-4a57-af99-fc787b0453c7",
]
for tid in reject_topics:
    mark_topic(tid, "rejected")

print(f"\n✅ Published {len(published_ids)} articles")
for aid, headline, cat in published_ids:
    print(f"  [{cat}] {aid}: {headline[:70]}")
