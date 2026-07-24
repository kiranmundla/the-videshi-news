#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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
    {
        "id": str(uuid.uuid4()),
        "headline": "India and Canada Agreed to Share Intelligence in Real Time. For 1.8 Million Indians in Canada, the Stakes Are Personal.",
        "subheadline": "NSA Ajit Doval's meeting with his Canadian counterpart marks a shift from diplomatic estrangement to active security cooperation — with direct implications for the diaspora caught between extremism accusations and everyday life.",
        "slug": make_slug("india-canada-doval-drouin-intelligence-sharing-diaspora-khalistani"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The 1.8 million Indians living in Canada — the majority of them Sikh — have been caught in the crossfire of a diplomatic crisis since 2023. The new intelligence-sharing framework directly affects how Canadian authorities surveil, investigate, and engage with diaspora communities, raising both security hopes and civil liberties questions.",
        "tags": ["nri", "diaspora", "canada", "india-canada-relations", "khalistani-extremism", "intelligence-sharing", "ajit-doval"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "India Tribune", "url": "https://www.indiatribune.com/public/india-and-canada-work-on-disrupting-transnational-ecosystem-sustaining-khalistani-extremism"},
            {"name": "IANS", "url": "https://ianslive.in/news/indian-canadian-nsas-discuss-counterterrorism-security-cooperation-mea-20250920"},
            {"name": "The CSR Journal", "url": "https://thecsrjournal.in/canada-flags-khalistani-extremist-threat-csis-warns-of-ongoing-security-risk/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/63/Ajit_Kumar_Doval.jpg",
        "is_editorial": False,
        "body": """National Security Advisor Ajit Doval's recent visit to Ottawa was not the kind of trip that makes headlines for handshakes and communiqués. It was, by most accounts, a working session — the sort where intelligence officials compare notes, delineate red lines, and agree on protocols that will matter far more in practice than in press releases. His counterpart was Nathalie Drouin, Canada's National Security and Intelligence Advisor, and the agenda was blunt: Khalistani extremism, drug trafficking, cyber threats, and cross-border smuggling.

The meeting comes after nearly two years of diplomatic frost between New Delhi and Ottawa, triggered by Canadian Prime Minister Justin Trudeau's 2023 allegation that Indian agents were involved in the killing of Khalistani separatist Hardeep Singh Nijjar on Canadian soil. India denied the charge. Diplomats were recalled. Trade talks stalled. And caught in the wreckage were 1.8 million people of Indian origin in Canada — the vast majority of them going about entirely ordinary lives.

## What Changed

The shift began after Trudeau's departure from office. Under Prime Minister Mark Carney, Canada signalled a willingness to reset. The Doval-Drouin meeting formalised that signal into four specific intelligence-sharing domains: Khalistani extremist networks, narcotics trafficking (particularly the fentanyl and heroin corridor that links Pakistan, Punjab, and British Columbia), cyber-enabled radicalisation, and smuggling of arms and personnel.

The key word is "real-time." Previous cooperation, such as it was, involved periodic exchanges of curated intelligence — useful but slow. The new framework envisions live data flows: flagging of operatives, tracking of financial transfers, and coordination of surveillance across jurisdictions. For India, this means potential access to information on Khalistani fundraisers and organisers who have operated from Toronto and Vancouver with relative impunity. For Canada, it means a more nuanced picture of what constitutes legitimate diaspora activism versus separatist mobilisation.

## The CSIS Report That Gave New Delhi Ammunition

A month before Doval's visit, Canada's own intelligence agency laid the groundwork. The Canadian Security Intelligence Service's annual report to Parliament, released in early May, stated plainly that "Khalistani extremists continue to use Canada as a base for the promotion, fundraising or planning of violence primarily in India." It was the first time the agency used the word "extremism" in connection with Khalistani activity — a terminological shift that validated what India had been arguing for years.

The report went further, noting that the politically motivated violent extremism (PMVE) threat in Canada "has manifested primarily through Canada-based Khalistani extremists" since the mid-1980s, when the Air India Flight 182 bombing killed 329 people. That attack remains the deadliest act of terrorism in Canadian history.

## What It Means for the Diaspora

For ordinary Indian Canadians — the engineers in Brampton, the restaurateurs in Surrey, the university students in Waterloo — the security reset carries a double edge. On one hand, it promises a crackdown on extremist elements that many in the community have quietly resented for years: the fringe groups that hijack gurdwara politics, the fundraisers who exploit community loyalty, the propagandists who conflate Sikh identity with separatism.

On the other hand, expanded surveillance always raises questions. Who decides which community organisations are "legitimate" and which are "extremist"? How will intelligence-sharing affect visa processing, travel, and banking for Canadian Sikhs who have family in Punjab? Will moderate community voices be consulted, or will the security apparatus operate over their heads?

These are not hypothetical concerns. Since 2023, Indian Canadians have reported increased scrutiny at borders, delayed consular services, and a general sense of being caught between two governments using them as proxies in a geopolitical argument.

## The Pakistan Factor

The Doval-Drouin meeting also has a third-party dimension that neither government has been eager to publicise. Intelligence assessments shared between the two sides reportedly flagged Pakistan's Inter-Services Intelligence (ISI) as actively attempting to revive Khalistani militancy in Punjab, using Canadian-based operatives for planning and Canadian-routed drug money for funding. The narco-terror nexus — drugs from Pakistan flowing through Punjab, profits laundered through Canadian real estate and cryptocurrency — is one area where both countries' interests align without ambiguity.

If the intelligence-sharing framework delivers on its promise, the immediate indicators will be tangible: arrests, asset freezes, drug seizures, and disruption of recruitment networks. The medium-term test will be whether Ottawa can sustain the cooperation through election cycles, where the Sikh diaspora vote in key Ontario and British Columbia ridings has historically given politicians incentives to look the other way.

## The Bigger Picture

For India's broader diaspora strategy, the Canada reset matters beyond the bilateral. If New Delhi can demonstrate that security cooperation yields results without alienating the mainstream community, it establishes a template for similar arrangements with the UK, Australia, and the United States — all countries where Khalistani networks maintain some presence.

The challenge, as always, is calibration. Heavy-handed surveillance will push moderates toward the very grievance narratives that extremists exploit. Genuine community engagement — of the kind that distinguishes between a farmer's protest and a separatist rally — requires the kind of local knowledge that intelligence agencies rarely excel at acquiring.

For now, the Doval-Drouin meeting represents a bet: that professional intelligence cooperation can achieve what diplomatic tantrums could not. Whether 1.8 million Indian Canadians end up as beneficiaries or collateral will depend on the implementation details that never make it into the press conference."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "London Mahotsav Is Turning the Bengali Diaspora's Nostalgia Into an Actual Institution. It Took Three Years.",
        "subheadline": "The UK's largest Indian-Bengali cultural carnival returns to Wembley this June with Kolkata's top artists, Aminia's biryani, and a mother-pageant flown in from Bengal. Behind it is a diaspora community quietly building something that lasts.",
        "slug": make_slug("london-mahotsav-2026-bengali-diaspora-wembley-cultural-institution"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Bengali diaspora in the UK has historically lacked the institutional visibility of Gujarati, Punjabi, or Tamil communities. London Mahotsav represents a deliberate effort to build a recurring cultural anchor — not just a one-off event — that asserts Bengali identity in Britain's multicultural landscape.",
        "tags": ["nri", "diaspora", "uk", "bengali-diaspora", "london-mahotsav", "cultural-festival", "wembley"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Business News for Profit", "url": "https://businessnewsforprofit.com/news/london-mahotsav-2026-uks-largest-indian-bengali-cultural-carnival-announces-grand-3rd-edition-in-london/"},
            {"name": "London Mahotsav Official", "url": "https://londonmahotsav.co.uk"},
            {"name": "Eventbrite Listings", "url": "https://www.eventbrite.co.uk/d/united-kingdom--london/bengali-festival/"}
        ]),
        "score_total": 70,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5648258/pexels-photo-5648258.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "is_editorial": False,
        "body": """When Sayantan Das Adhikari launched the first London Mahotsav in 2024, the pitch was simple: give Britain's Bengalis a cultural gathering that felt like Kolkata, not like a corporate diversity checkbox. Two years later, the festival has grown into something its organisers now describe, without irony, as an institution. The third edition takes over the Sattavis Patidar Centre in Wembley on June 27-28, and the lineup reads like a who's who of contemporary Bengali culture.

Rupankar Bagchi will perform. So will Shrabani Sen, Poushali Banerjee, Sidhu of Cactus, and Soumitra of Bhoomi. Tathagata Sengupta is preparing a tribute to R.D. Burman — the kind of set that could fill a Kolkata auditorium on its own. The Mayor of Brent will inaugurate the event. Over 3,500 visitors are expected across two days.

## More Than Music

What distinguishes London Mahotsav from the dozens of Indian cultural events that dot the UK calendar every year is its deliberate breadth. This is not a Durga Puja committee that happens to book a singer. The programme spans music, theatre, literature, fashion, sport, entrepreneurship, and food — each curated as a standalone attraction.

The theatre segment features "Prothom Partha," a dramatic presentation that will bring together actors Kaushik Sen and Debshankar Haldar on a UK stage for the first time. They will be joined by director Arindam Sil, actress Anjana Basu, and elocutionist Raya Bhattacharya. For the Bengali diaspora, who consume Bengali theatre primarily through YouTube clips and WhatsApp forwards, seeing it performed live in Wembley carries a weight that is difficult to overstate.

Then there is "Banglar Derby" — a talk show reuniting former Mohun Bagan and East Bengal footballers from the 1970s and 1980s. Prasanta Banerjee and Manas Bhattacharya will represent the green-and-maroon; Bhaskar Ganguly and Chima Okorie will carry East Bengal's red-and-gold. For a community that measures time partly by football seasons in the Maidan, this is not nostalgia — it is identity work.

## The Food Strategy

The culinary ambition this year is notable. Aminia, Kolkata's legendary biryani institution, is sending its own chefs across the Atlantic with spices, utensils, and traditional biryani containers — a logistical operation that tells you how seriously the organisers take authenticity. The signature mutton and chicken biryanis will be prepared on site, alongside Aminia's firni. Kolkata's Hindustan Sweets will provide the mishti.

A Food Talk session will pair celebrity chef Asma Khan — the Darjeeling-born, London-based restaurateur who was the first British-Indian chef featured on Netflix's "Chef's Table" — with Indrajit Lahiri, the food vlogger known as Foodka, alongside the Aminia proprietors. The implicit argument: Bengali cuisine is not a subcategory of "Indian food." It is its own tradition, with its own grammar, and it deserves its own platform in Britain.

## Why Bengalis, Why Now

Britain's Indian community is not monolithic, but its institutional infrastructure has historically been dominated by certain regional groups. Gujaratis have the Patidar centres and business networks. Punjabis have the gurdwaras and political organisations. Tamils have the temple circuit. Bengalis, despite being one of the larger Indian sub-communities in the UK, have been comparatively underrepresented in the institutional landscape — a gap that London Mahotsav is explicitly trying to fill.

The festival is organised by Candid Communication UK, founded by Das Adhikari, who splits his time between Kolkata and London. The business model is part cultural enterprise, part community infrastructure: sponsorships from SBI UK, Vicco, and Top-Op Foods anchor the finances, while ticketed events and exhibitions generate additional revenue. The goal is sustainability — an annual fixture that the community can point to and say, "This is ours."

## The Matrimaa Experiment

Perhaps the most unexpected addition to this year's programme is Matrimaa, a beauty pageant for mothers curated by Tuhinaa Pandey. Finalists from Kolkata will fly to London for the grand finale at the Mahotsav. It is, depending on your perspective, either a celebration of motherhood that challenges conventional pageant demographics, or a shrewd bit of programming that ensures at least one segment goes viral on Bengali social media. Probably both.

## What the Diaspora Is Building

The larger story of London Mahotsav is about what happens when a diaspora community decides to stop waiting for recognition and starts building its own cultural infrastructure. The Bengalis in Britain — estimated at over 500,000, including Bangladeshi-origin Bengalis — have the numbers. What they have lacked is a recurring, high-profile, unapologetically Bengali platform that operates at scale.

Three editions in, London Mahotsav is not yet the Bengali equivalent of the Notting Hill Carnival or the Chinese New Year celebrations in Trafalgar Square. But it is building in the right direction: bigger each year, more ambitious in programming, more deliberate in its claim on public space. The Sattavis Patidar Centre in Wembley — a Gujarati-built venue hosting a Bengali festival — is itself a small metaphor for how diasporas share infrastructure even as they assert distinct identities.

The festival runs June 27-28. Tickets are available through the London Mahotsav website. If you are in London and have never tasted Aminia's biryani, this would be the time."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "One in Five of India's Ultra-Rich Wants to Move Abroad. The Rest Are Trying to Figure Out How to Sell the House They Left Behind.",
        "subheadline": "A Kotak Bank report reveals a quiet exodus of wealthy Indians who plan to emigrate while keeping their passports. Meanwhile, NRIs already abroad face a thicket of tax, documentation, and fraud risks when they try to liquidate ancestral property.",
        "slug": make_slug("ultra-hni-migration-nri-property-selling-kotak-bank-report"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The two ends of the NRI wealth spectrum are converging on the same problem: how to manage assets across borders. Ultra-HNIs are acquiring property abroad as part of migration strategies, while existing NRIs are struggling to sell inherited property in India — creating a cross-border real estate headache that affects millions of diaspora families.",
        "tags": ["nri", "diaspora", "real-estate", "ultra-hni", "migration", "property-fraud", "kotak-bank", "wealth"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2024/12/04/20-of-ultra-rich-indians-plans-to-settle-abroad-while-retaining-citizenship/"},
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/invest/things-nris-should-keep-in-mind-while-selling-property-in-india"},
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/invest/the-hidden-cost-of-going-global-why-indian-hnis-often-misprice-mobility"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/30608874/pexels-photo-30608874.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "is_editorial": False,
        "body": """There are two kinds of NRI property stories, and they tend to circulate in different WhatsApp groups. The first is aspirational: a tech executive in the Bay Area buying a ₹15 crore flat in Gurugram as an investment and a hedge against eventual return. The second is exhausting: a family in New Jersey spending three years trying to sell an ancestral home in Jalandhar, navigating forged Power of Attorney documents, missing encumbrance certificates, and a legal system that moves at the speed of geological erosion.

Both stories are getting more common. And a new report from Kotak Bank suggests they are part of the same phenomenon — a massive, messy restructuring of wealth across borders as India's rich get richer and its diaspora gets more entrenched.

## The Kotak Numbers

One in five ultra-high-net-worth individuals (Ultra-HNIs) in India — those with assets exceeding ₹25 crore — is either in the process of migrating abroad or planning to do so, according to the Kotak Wealth report. Most intend to settle permanently in their chosen destination while retaining Indian citizenship. Among them, professionals show a higher migration tendency than entrepreneurs or inheritors, and the 36-40 and 61-plus age brackets are disproportionately represented.

The numbers are projected to grow. India's Ultra-HNI population is expected to reach 4.3 lakh by 2028, with a combined wealth of ₹359 trillion. Nearly one-third already hold global assets, with residential real estate in Dubai, London, Singapore, and the United States being the preferred categories.

What is new is not the migration itself — Indians have been moving abroad for decades — but the sophistication of the planning. This is not brain drain in the traditional sense. These are individuals who maintain Indian citizenship, keep NRE and NRO accounts active, retain business interests in India, and view overseas property as part of a diversified portfolio that includes Indian assets. They are not leaving India. They are straddling it.

## The Property Problem for Those Already Abroad

At the other end of the spectrum, the 32 million NRIs and PIOs who already live overseas face a different challenge: disposing of Indian property they have inherited or purchased years ago. The Outlook Money guide published this week lays out the obstacle course in clinical detail.

First, documentation. NRIs selling property must ensure that the sale deed, title documents, property tax receipts, occupancy certificates, and society clearances are all current and in order. For properties inherited from parents or grandparents — often in smaller cities with patchy land records — this can take months of coordination with local lawyers, municipal offices, and housing societies.

Second, taxation. NRIs face higher Tax Deducted at Source (TDS) rates than resident sellers — 20% on long-term capital gains plus applicable surcharges. The funds cannot simply be transferred abroad; they must flow through RBI-compliant channels, typically an NRO account, with repatriation capped at USD 1 million per financial year after tax clearance. For properties worth more than that, the paperwork multiplies.

Third, and most troubling, fraud. The Punjab and Haryana High Court has flagged what it now calls a "pattern" of NRI property fraud — cases where ancestral homes are sold using forged documents while the actual owners are abroad and unaware. Impersonation, fake Power of Attorney, and collusion between local agents and sub-registrar offices have become common enough that the court has called for systemic reforms.

## The Hidden Costs of Going Global

A separate analysis by wealth advisor Dhruv Chopra, published in Outlook Money, argues that most Indian HNIs underestimate the true cost of global mobility. A Dubai property may appear tax-efficient on paper, but the calculation changes when you factor in currency risk, liquidity constraints, cross-border compliance obligations, and the layers of regulation that apply when moving capital between jurisdictions.

"Global mobility is often approached as a portfolio extension, when in reality it represents something far more consequential — a restructuring of the investor's balance sheet and future cash-flow architecture," Chopra writes. The implication is that many NRIs — even wealthy ones — are making cross-border financial decisions based on headline returns rather than realised outcomes.

## The Regulatory Patchwork

The Union Budget 2026 made some concessions. NRIs are now exempt from minimum alternative tax under presumptive taxation. Small, undisclosed foreign assets under ₹20 lakh will not trigger criminal prosecution. The TCS rate on overseas tour packages and education remittances under the Liberalised Remittance Scheme has been cut from 5% to 2%. Filing deadlines have been extended, and compliance forms have been simplified.

But these are incremental fixes to a structural problem. The fundamental challenge for NRIs — whether they are Ultra-HNIs strategising their next move or middle-class families trying to sell a flat in Pune — is that India's property, tax, and banking systems were not designed for people who live in two countries simultaneously. FEMA regulations, FBAR and FATCA reporting requirements, RBI repatriation rules, and state-level land revenue procedures each operate according to their own logic. Navigating all of them simultaneously requires professional help that many NRIs either cannot afford or do not know they need.

## The Convergence

What the Kotak report and the Outlook Money analysis reveal, when read together, is a diaspora whose relationship with Indian property is growing both more ambitious and more complicated. The ultra-rich are acquiring assets abroad as part of deliberate migration strategies. The established diaspora is struggling to manage or exit Indian assets acquired by their parents. And the regulatory environment, despite recent reforms, remains a patchwork that rewards those who can afford chartered accountants and penalises those who cannot.

For the 32 million Indians living abroad, the house back home — whether it is a penthouse in Gurugram or a plot in a Punjab village — remains both the most tangible connection to the country they left and the most persistent source of administrative grief. India will need to do considerably more than simplify Form 15G if it wants to keep that connection from fraying."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
