#!/usr/bin/env python3
"""Videshi Writer — 4 fresh NEWS articles for 2026-05-22 (evening batch)
Topics: Rubio India/Quad visit, Gabbard resigns DNI, Air India SFO lounge, Warsh Fed Chair
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

def sb_patch(table, filters, data):
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{filters}", headers={**HEADERS, "Prefer": "return=minimal"}, json=data, timeout=30)
    return r.status_code

def make_slug(headline, date_suffix="20260522"):
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Rubio India Visit + Quad Foreign Ministers Meeting
# Topic: 4e320520 (score 84) + 5468bb72, 72e767a5 (related)
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": "4e320520-74ba-4ca0-9c47-e3fe529f984c",
    "headline": "Marco Rubio Lands in India for a Four-Day Visit That Could Reshape the Entire US-India Relationship. The Quad Meeting Is Just the Beginning.",
    "subheadline": "The Secretary of State's first trip to India — spanning Kolkata, Agra, Jaipur, and New Delhi — comes as Washington and New Delhi navigate tariff tensions, a deepening defence partnership, and a Quad foreign ministers' meeting on Monday that will test whether the grouping can deliver on the Indo-Pacific.",
    "slug": make_slug("rubio-india-visit-quad-meeting-new-delhi"),
    "category": "news",
    "vertical": "politics",
    "diaspora_angle": "For the 4.4 million Indian Americans who watched Trump slap tariffs on Indian goods while simultaneously courting Modi as a strategic partner, Rubio's visit is the clearest signal yet of where the relationship is actually heading — and whether the diaspora's dual allegiances will get easier or harder to maintain.",
    "tags": ["Marco Rubio", "India", "Quad", "US-India relations", "Jaishankar", "trade", "defence", "Indo-Pacific", "NATO"],
    "urgency": "breaking",
    "sources": json.dumps([
        {"name": "Reuters — Rubio to visit Sweden for NATO meeting, then India", "url": "https://www.reuters.com/world/us/rubio-visit-sweden-nato-meeting-then-india-2026-05-19/"},
        {"name": "Madhyamam — Marco Rubio to visit India from May 23 for talks on trade, defence, and energy", "url": "https://madhyamamonline.com/india/marco-rubio-to-visit-india-from-may-23-for-talks-on-trade-defence-and-energy-1521556"},
        {"name": "Devdiscourse — US Secretary of State Marco Rubio to visit India from May 23-26", "url": "https://www.devdiscourse.com/article/politics/3354431-us-secretary-of-state-marco-rubio-to-visit-india-from-may-23-26"},
        {"name": "The Hindu Business Line — Marco Rubio to visit India for trade, defence and energy talks", "url": "https://www.thehindubusinessline.com/"},
        {"name": "US State Department — Secretary Rubio's Meeting with Indian EAM Jaishankar", "url": "https://www.state.gov/secretary-rubios-meeting-with-indian-external-affairs-minister-jaishankar/"}
    ]),
    "score_total": 90,
    "status": "published",
    "published_at": now,
    "body": """U.S. Secretary of State Marco Rubio touched down in India on Friday for what the State Department has billed as a four-day diplomatic marathon — his first visit to the country since taking office — that will take him from the ghats of Kolkata to the corridors of power in New Delhi. The trip culminates on Monday with a Quad Foreign Ministers' Meeting that could set the tone for Indo-Pacific strategy for the next two years.

The itinerary is deliberately symbolic. Rubio will visit Kolkata, Agra, and Jaipur before arriving in the capital for what officials describe as substantive discussions on energy security, trade, defence cooperation, and the fallout from the ongoing West Asia crisis. State Department spokesman Tommy Pigott confirmed the schedule, noting that the Secretary would hold meetings with "senior Indian officials" throughout.

## The Quad Meeting: More Than a Photo Op

The centrepiece of the visit is Monday's Quad gathering in New Delhi, where Rubio will join Australian Foreign Minister Penny Wong, Japanese Foreign Minister Motegi Toshimitsu, and Indian External Affairs Minister S. Jaishankar. The meeting is expected to focus on maritime security, freedom of navigation in the South China Sea, technology cooperation, and the coordinated response to the West Asia crisis that has disrupted global energy markets.

The Quad — comprising the United States, India, Japan, and Australia — has evolved from a loose consultative forum into what its members describe as the "premier partnership for a free and open Indo-Pacific." But critics, including Beijing, have called it a thinly disguised containment strategy aimed at China. Monday's meeting will test whether the grouping can move beyond statements of principle into concrete deliverables.

India's hosting role is significant. New Delhi has carefully positioned itself as the Quad's anchor in the Global South, balancing its partnerships with Washington and Tokyo against its energy dependence on Russia and its complex border dynamics with China. Jaishankar, who will preside over the discussions, has built a reputation as a diplomat who can navigate these contradictions — though the tariff dispute with Washington has tested even his legendary composure.

## Tariffs, Trade, and the Elephant in the Room

Rubio arrives in India at a moment of genuine tension. The Trump administration's tariff regime has hit Indian goods hard, and New Delhi's retaliatory measures have complicated what both sides describe as a "defining partnership of the 21st century." The Secretary's meetings with Indian officials are expected to address the stalled interim trade deal, critical mineral cooperation, and the thorny question of whether Washington will grant India the kind of preferential market access that its $3.5 trillion economy increasingly demands.

For Indian American professionals — many of whom work in the very technology and defence sectors where US-India cooperation is deepening — the trade dispute is not abstract. It affects the companies they work for, the supply chains their employers rely on, and in some cases, the businesses they own. When India's commerce ministry slaps retaliatory tariffs on American almonds, it is the Indian grocery stores in New Jersey and Texas that feel it first.

## Defence and Energy: Where the Real Action Is

The more consequential discussions are likely to happen in the defence and energy corridors. The United States has been pressing India to deepen its defence procurement from American manufacturers, and there are signals that a major nuclear energy partnership may be on the table. A U.S. envoy hinted this week at "significant movement" on civil nuclear cooperation, building on the landmark 123 Agreement signed in 2008 but never fully realised.

For India, the energy conversation is urgent. The West Asia conflict has sent oil prices spiralling, and India — which imports 85 per cent of its crude — needs stable, affordable energy sources. American LNG, nuclear technology, and defence platforms are all on the table, but so is the question of price. India has historically driven hard bargains, and Rubio will find that Jaishankar is no different.

## What This Means for the Diaspora

Indian Americans have watched the US-India relationship evolve from strategic indifference in the Cold War to what both governments now call a "comprehensive global strategic partnership." But the relationship has never been tested quite like this — simultaneously deepening in defence and technology while fraying on trade.

Rubio's visit is being closely watched in diaspora communities from the Bay Area to the Beltway. The Quad meeting on Monday will signal whether Washington is serious about treating India as a peer partner or whether the relationship remains transactional. For the millions of Indian Americans who navigate both identities — American taxpayers and Indian-origin citizens with family, investments, and emotional ties on both sides — the answer matters more than any communiqué.

## What's Next

The Quad Foreign Ministers' Meeting on May 26 is expected to produce a joint statement on Indo-Pacific security, supply chain resilience, and technology standards. Bilateral meetings between Rubio and Jaishankar may also yield announcements on critical mineral agreements and defence procurement. The real measure of success, however, will be whether the visit produces momentum on the trade dispute — or whether tariffs continue to cast a shadow over what both sides insist is an indispensable partnership."""
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Tulsi Gabbard Resigns as DNI
# Topic: 5980a733 (score 83), 3a2f78d2 (score 81)
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": "5980a733-2c81-490a-bd9f-bf896c226266",
    "headline": "Tulsi Gabbard Just Resigned as America's Intelligence Chief. Her Turbulent Tenure Changed the DNI — and the Debate Over What It Should Be.",
    "subheadline": "The former Hawaii congresswoman, who led all 18 U.S. intelligence agencies, is stepping down effective June 30 after her husband was diagnosed with a rare bone cancer. She leaves behind a legacy of declassified records, political warfare, and an intelligence community in transition.",
    "slug": make_slug("tulsi-gabbard-resigns-dni-intelligence-chief"),
    "category": "news",
    "vertical": "politics",
    "diaspora_angle": "Gabbard — born in American Samoa, raised Hindu, the first Hindu member of Congress — was a polarising figure for Indian Americans. Her resignation raises fresh questions about who leads American intelligence, and whether the next nominee will be chosen for competence or loyalty.",
    "tags": ["Tulsi Gabbard", "DNI", "intelligence", "resignation", "Trump administration", "Abraham Williams", "Aaron Lukas", "national security"],
    "urgency": "breaking",
    "sources": json.dumps([
        {"name": "USA Today — Trump intelligence chief Tulsi Gabbard resigns, cites husband's cancer", "url": "https://www.usatoday.com/story/news/politics/2026/05/22/tulsi-gabbard-resigns-dni/90217895007/"},
        {"name": "Reuters — Gabbard resigns as Trump's top US intelligence official", "url": "https://www.reuters.com/world/us/trump-spy-chief-gabbard-resign-citing-husbands-cancer-2026-05-22/"},
        {"name": "CNN — Tulsi Gabbard is resigning as director of national intelligence", "url": "https://www.cnn.com/2026/05/22/politics/tulsi-gabbard-resigns-dni/"},
        {"name": "Fox News — EXCLUSIVE: Tulsi Gabbard resigns from Trump Cabinet", "url": "https://www.foxnews.com/politics/tulsi-gabbard-resigns-trump-cabinet"},
        {"name": "New York Post — Read DNI Tulsi Gabbard's heartbreaking resignation letter to President Trump", "url": "https://nypost.com/2026/05/22/us-news/read-dni-tulsi-gabbards-heartbreaking-resignation-letter/"}
    ]),
    "score_total": 88,
    "status": "published",
    "published_at": now,
    "body": """Tulsi Gabbard, the Director of National Intelligence and one of the most polarising figures in American national security, announced her resignation on Thursday, citing her husband's diagnosis with a rare form of bone cancer. The departure, effective June 30, makes her the fourth Cabinet-level official to leave Donald Trump's second-term administration and opens a high-stakes vacancy atop the nation's intelligence apparatus.

"My husband, Abraham, has recently been diagnosed with an extremely rare form of bone cancer," Gabbard, 45, wrote in a resignation letter posted on X. "He faces major challenges in the coming weeks and months. At this time, I must step away from public service to be by his side and fully support him through this battle."

Calling Abraham Williams her "rock" through 11 years of marriage, overseas military deployments, and political campaigns, she added: "I cannot in good conscience ask him to face this fight alone while I continue in this demanding and time-consuming position."

## A Tenure That Divided Washington

Gabbard's 18-month stint as DNI was, by any measure, consequential. She led a sweeping transparency push that declassified more than 500,000 pages of records, including long-secret files on the assassinations of President John F. Kennedy, Robert F. Kennedy, and Martin Luther King Jr., as well as the disappearance of Amelia Earhart. She also released materials she said exposed the intelligence community's role in the first Trump impeachment proceedings.

She initiated "ODNI 2.0," a restructuring that cut the office's staffing by over 40 per cent — a move her team said saved taxpayers $700 million annually. The overhaul eliminated DEI programmes, targeted what she called waste and abuse, and refocused resources on cybersecurity and technology modernisation.

But her critics — and there were many — saw something darker. Democrats accused Gabbard of systematically politicising the intelligence community at Trump's direction. She revoked the security clearances of former Obama and Biden administration officials, established a "Weaponisation Working Group" to investigate Biden-era probes, and participated in a controversial FBI search of the Fulton County Elections Hub near Atlanta as part of a 2020 election probe.

## The Iran War and the Breaking Point

The sharpest crisis of Gabbard's tenure came during the Iran conflict. Intelligence assessments of Tehran's progress toward a nuclear weapon reportedly diverged from the administration's public justifications for military action. At a tense Senate Intelligence Committee hearing in March 2026, Gabbard notably declined to say whether Iran posed an "imminent" nuclear threat, arguing that such judgments "ultimately belonged to the president."

The testimony came a day after Joe Kent, the National Counterterrorism Centre director and one of Gabbard's closest allies, publicly resigned over the war. "Iran posed no imminent threat to our nation," Kent wrote in his resignation letter to Trump, "and it is clear that we started this war due to pressure from Israel and its powerful American lobby."

Gabbard's careful non-answer at the hearing was widely interpreted as an attempt to thread an impossible needle — supporting the president while refusing to contradict the intelligence community's own assessments. It earned her few friends on either side.

## What Happens Next

President Trump acknowledged Gabbard's departure on Truth Social, saying "Tulsi has done an incredible job, and we will miss her." He announced that Aaron Lukas, the principal deputy director of national intelligence, would serve as acting director.

The vacancy triggers an immediate political fight. Senate Minority Leader Chuck Schumer warned that "Trump must not treat this vacancy as another opportunity to reward loyalty over competence." Senator Adam Schiff of California was less diplomatic: "Tulsi Gabbard's only positive contribution to our nation's national security is her resignation."

## The Hindu Congresswoman Who Became America's Spy Chief

For Indian Americans, Gabbard has always occupied a complicated space. Born in American Samoa, raised in a Hare Krishna household in Hawaii, she became the first Hindu member of the U.S. Congress in 2013. Her election was celebrated across the Indian diaspora, and her early political career drew support from Hindu American organisations.

But her trajectory — from progressive Democratic congresswoman who challenged Hillary Clinton and met with Bashar al-Assad, to Trump convert and intelligence chief — has fractured that support. Her declassification campaign, her views on Russia and Ukraine, and her role in the Iran intelligence debate have made her a hero to some and an anathema to others.

Her departure leaves a void that extends beyond policy. The DNI leads all 18 U.S. intelligence agencies, and the choice of her successor will signal whether the administration wants a professional intelligence leader or a political loyalist. For the Indian American community, it is also a reminder of how quickly a trailblazing career can become a cautionary tale — or, depending on whom you ask, a profile in conscience."""
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 3: Air India Maharaja Lounge at SFO
# Topic: 81804f18 (score 80)
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": "81804f18-6d34-4f01-93e6-0890a5a827ea",
    "headline": "Air India Just Opened Its First International Lounge — and They Put It in San Francisco, Not London or Dubai.",
    "subheadline": "The 3,300-square-foot Maharaja Lounge at SFO features upcycled aircraft art, a speakeasy bar, and a private first-class enclave. It is the clearest signal yet that the Tata-owned airline is betting its premium transformation on the Bay Area's Indian diaspora.",
    "slug": make_slug("air-india-maharaja-lounge-sfo-san-francisco"),
    "category": "nri-world",
    "vertical": "diaspora",
    "diaspora_angle": "The choice of San Francisco — not London Heathrow or Dubai — tells you everything about where Air India sees its most valuable customers. The Bay Area is home to the densest concentration of high-income Indian professionals in the world, and the airline is building a lounge to match.",
    "tags": ["Air India", "Maharaja Lounge", "San Francisco", "SFO", "aviation", "Tata Group", "Campbell Wilson", "NRI", "Bay Area"],
    "urgency": "standard",
    "sources": json.dumps([
        {"name": "American Bazaar — San Francisco International Airport gets upgraded with Air India's new Maharaja lounge", "url": "https://americanbazaaronline.com/2026/05/22/san-francisco-international-airport-gets-upgraded-with-air-indias-new-maharaja-lounge-481406/"},
        {"name": "One Mile at a Time — New Air India Maharaja Lounge SFO Now Open", "url": "https://onemileatatime.com/news/air-india-maharaja-lounge-sfo/"},
        {"name": "Travel Trade Journal — Air India opens signature Maharaja Lounge at SFO", "url": "https://traveltradejournal.com/"},
        {"name": "Indian Eagle — Inside New Air India Lounge at SFO Airport", "url": "https://www.indianeagle.com/"},
        {"name": "Mainly Miles — Singapore Airlines now using Air India lounge in SFO", "url": "https://mainlymiles.com/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "body": """Air India has opened the doors to its first signature lounge outside India, and the location tells you everything about where the airline sees its future. The Maharaja Lounge, a 3,300-square-foot space in International Terminal A at San Francisco International Airport, began welcoming passengers on Friday — a calculated bet on the Bay Area's Indian diaspora that says more about the "New Air India" than any quarterly earnings report could.

The lounge, designed by the globally acclaimed hospitality firm Hirsch Bedner Associates, is a deliberate departure from what CEO Campbell Wilson diplomatically calls "legacy airline aesthetics." Translation: the old Air India lounges, with their faded carpets and perfunctory buffets, are being consigned to memory. In their place is a space that blends contemporary luxury with touches of Indian heritage — upcycled art fashioned from retired aircraft components, a speakeasy-inspired cocktail bar with hand-picked whiskies and wines, and a private "lounge within a lounge" for first-class passengers offering panoramic tarmac views.

## Why San Francisco, Not London or Dubai?

The choice of SFO as the first international Maharaja Lounge is strategic in ways that go beyond geography. San Francisco is the gateway to Silicon Valley, home to the densest concentration of high-income Indian technology professionals in the world. The Bay Area's Indian population — engineers, founders, venture capitalists, and their families — represents exactly the premium customer base that Air India needs to win over as it competes with Emirates, Singapore Airlines, and the Gulf carriers for the lucrative India-US corridor.

The numbers tell the story. India-US air traffic has been growing at double-digit rates, and SFO is one of the busiest corridors. Air India operates daily nonstop flights to multiple Indian cities from San Francisco, and the route is dominated by business and business-adjacent travellers who have historically chosen foreign carriers for the premium experience. The lounge is Air India's answer to that calculation.

The validation came almost immediately. Singapore Airlines has already designated the Maharaja Lounge as its partner lounge at SFO for eligible passengers, replacing the United Polaris Lounge. When your competitor's airline chooses your lounge over a Star Alliance flagship facility, it says something about the product.

## Inside the Lounge

The space is organised into curated zones. There is a main lounge area with 80 seats, dynamic live cooking stations offering a rotating menu that draws on Indian culinary traditions, and quiet corners for passengers who want to work or rest. The cocktail lounge features a dramatic custom architectural ceiling and a bar programme that goes well beyond the standard airline lounge gin-and-tonic.

The private first-class zone — the "lounge within a lounge" — offers elevated hospitality, dedicated service, and those tarmac views. It is the kind of space that Air India's competitors have offered for decades but that the Indian flag carrier never could, first because of government neglect and then because of the years of uncertainty that preceded the Tata Group's takeover in 2022.

## The Bigger Picture: Tata's $400 Billion Gamble

The Maharaja Lounge is one element of a transformation that the Tata Group — India's largest conglomerate — has been executing since it bought Air India back from the government for ₹18,000 crore. Under Wilson, a Singapore Airlines veteran, the airline has ordered 470 new aircraft, merged with Vistara, revamped its livery, and begun upgrading its product from nose to tail.

But lounges matter disproportionately in the premium segment. Business travellers — many of them Indian Americans flying between San Francisco, Delhi, Mumbai, and Bengaluru — make their airline choices based on the end-to-end experience. A competitive lounge at SFO addresses one of the most persistent criticisms of Air India: that its ground experience did not match its ambitions.

The airline says San Francisco is just the start. The flagship Maharaja Lounge at Delhi's Terminal 3, which opened in February, spans 16,000 square feet — nearly five times the size of the SFO facility. More international lounges are planned, though the airline has not disclosed locations. London Heathrow and New York JFK are obvious candidates.

## What It Means for NRI Travellers

For the tens of thousands of Indian Americans who fly between the Bay Area and India every year — for work, for family, for festivals — the Maharaja Lounge is a tangible sign that Air India is serious about earning their loyalty. The airline that was once a punchline in frequent-flyer forums is building a product that stands alongside the world's best.

The lounge is open daily from 6 a.m. to 11:55 p.m. and is accessible to Air India First and Business Class passengers, Maharaja Club Platinum and Gold members, and Star Alliance Gold card holders. For everyone else, it is a reason to reconsider which airline you book the next time you fly home."""
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 4: Kevin Warsh Sworn In as Fed Chair
# Topic: 63e93935 (score 81)
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": "63e93935-bd62-404c-83e8-f80c09f89dd7",
    "headline": "The New Federal Reserve Chair Is a Trump Ally Who Was Confirmed by One Vote. What That Means for Your Money, Your Mortgage, and the Indian Economy.",
    "subheadline": "Kevin Warsh, the 17th chair of the Federal Reserve, inherits an inflation rate of 3.8 per cent, a president who wants rate cuts, and a mandate that will test whether the world's most important central bank can remain independent.",
    "slug": make_slug("kevin-warsh-federal-reserve-chair-india-economy"),
    "category": "markets-finance",
    "vertical": "economy",
    "diaspora_angle": "For Indian Americans with mortgages, 401(k)s, and family money flowing across borders, the Fed chair is not an abstraction. Warsh's decisions on interest rates will move the dollar, shift capital flows to emerging markets, and directly affect the rupee-dollar exchange rate that governs every remittance home.",
    "tags": ["Kevin Warsh", "Federal Reserve", "interest rates", "inflation", "Trump", "Jerome Powell", "Indian economy", "rupee", "markets"],
    "urgency": "standard",
    "sources": json.dumps([
        {"name": "Reuters — Warsh takes the Fed's helm as inflation climbs, consumer sentiment dives", "url": "https://www.reuters.com/business/finance/warsh-takes-feds-helm-inflation-climbs-consumer-sentiment-dives-2026-05-16/"},
        {"name": "Reuters — Trump to swear in Warsh as Fed chair on Friday, White House says", "url": "https://www.reuters.com/business/finance/trump-swear-warsh-fed-chair-friday-white-house-says-2026-05-15/"},
        {"name": "The Motley Fool — 7 Words From New Fed Chair Kevin Warsh That Portend a Significant Shift", "url": "https://www.fool.com/investing/2026/05/17/7-words-new-fed-chair-kevin-warsh-portend-shift/"},
        {"name": "OilPrice.com — New Fed Chair Faces Pressure as Oil Prices Fuel Inflation", "url": "https://oilprice.com/"},
        {"name": "Reuters — Vanishing Fed rate cuts could buy time for Warsh", "url": "https://www.reuters.com/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "body": """The most consequential job change in the global economy happened last Friday, and if you blinked, you might have missed it. Kevin Warsh, a former Federal Reserve governor and close ally of President Donald Trump, was sworn in as the 17th chair of the Federal Reserve in a White House ceremony on May 15, replacing Jerome Powell after one of the most contentious confirmation battles in central banking history.

The U.S. Senate confirmed Warsh on a 54-45 vote — the slimmest margin ever for a Fed chair, with only Democratic Senator John Fetterman crossing party lines. The vote itself was a statement: the institution that controls the world's reserve currency, sets the interest rates that ripple through every economy on earth, and serves as the lender of last resort in a crisis is now led by a man whose appointment was decided on strictly partisan lines.

## What Warsh Inherits

The numbers are not kind. Annual U.S. consumer inflation hit 3.8 per cent in April — the highest in three years — driven by tariffs on imported goods and energy price spikes from the West Asia conflict. Consumer sentiment has plummeted to record lows. The stock market is volatile. And the president who appointed him has been publicly — and repeatedly — demanding interest rate cuts that most economists say would pour fuel on inflationary fire.

Warsh, 56, is not a stranger to crisis. As a Fed governor during the 2008 financial meltdown, he was in the room when the decisions that saved — or, critics argue, distorted — the global financial system were made. He has since positioned himself as a critic of the Fed's post-crisis monetary expansion and an advocate for market discipline. But the pressures he faces now are different: a president who views the Fed as a political tool, an inflation rate that makes rate cuts dangerous, and a global economy fractured by tariffs and conflict.

## Why Indian Americans Should Pay Attention

The Federal Reserve chair may seem like a distant Washington figure, but for Indian Americans, the appointment has direct financial consequences.

**Mortgages and housing:** Warsh's decisions on the federal funds rate will determine whether mortgage rates — currently hovering near 7 per cent — come down or stay elevated. For the hundreds of thousands of Indian American families who bought homes during the low-rate era or are trying to buy now, this is a kitchen-table issue.

**The rupee and remittances:** When the Fed holds rates high, the dollar strengthens. A strong dollar means fewer rupees per dollar remitted — which matters to every Indian American sending money home. The USD/INR exchange rate, currently around 95.68, is sensitive to Fed policy signals. If Warsh signals rate cuts, the rupee could strengthen; if he holds firm on inflation, the dollar stays elevated.

**Stock markets and retirement:** The S&P 500, Nasdaq, and Sensex all react to Fed guidance. Indian American professionals with 401(k)s, IRAs, and investments in Indian mutual funds are exposed on both sides of the Pacific. The Fed's June 16-17 meeting — Warsh's first as chair — will be the market's first real test of his policy direction.

**Capital flows to India:** When U.S. rates are high, global capital tends to flow toward dollar-denominated assets and away from emerging markets like India. Lower rates would reverse that flow, boosting foreign institutional investment in Indian equities and easing pressure on the Reserve Bank of India. Warsh's policy choices will shape these flows for years.

## The Independence Question

The deeper concern is not any single rate decision but whether the Federal Reserve can maintain its independence under Warsh. Trump has made no secret of his desire for lower rates, and his choice of Warsh — a personal friend and political ally — was widely interpreted as an attempt to install a sympathetic chair.

Warsh has pushed back gently, telling reporters after his swearing-in that the Fed "must make decisions based on data, not politics." But his confirmation along party lines, his personal ties to the president, and the broader pattern of Trump loyalty tests across the administration have left markets uneasy. The bond market, which prices in expectations about future inflation and Fed credibility, will be the ultimate judge.

Powell, notably, opted to remain on the Fed's Board of Governors even after being replaced as chair — an unusual move that some interpret as a check on his successor and others as a sign that he expects to be needed.

## What to Watch

The Fed's next policy meeting is June 16-17. Markets currently expect no rate change, but Warsh's post-meeting press conference — his first as chair — will be parsed word by word for signals about his priorities. Will he emphasise inflation fighting, signalling continuity with Powell's approach? Or will he hint at rate cuts, aligning with Trump's demands and potentially spooking the bond market?

For Indian Americans navigating mortgages, remittances, investments, and the broader economic relationship between the world's largest and fifth-largest economies, the answer will be felt in their bank accounts long before it appears in any policy statement."""
})


# ══════════════════════════════════════════════════════════════
# INSERT ARTICLES
# ══════════════════════════════════════════════════════════════
print(f"Inserting {len(articles)} articles...")
for a in articles:
    try:
        result = sb_post("p2_articles", a)
        print(f"  ✓ {a['headline'][:70]}...")
    except Exception as e:
        print(f"  ✗ {a['headline'][:50]}... — {e}")

# Mark topics as published
topic_ids = [
    "4e320520-74ba-4ca0-9c47-e3fe529f984c",  # Rubio Quad
    "5468bb72-3c0c-4b0c-acc9-e62dc22d605f",  # Rubio energy (related)
    "72e767a5-d76f-4503-976a-d353e26214d4",  # India-US nuclear (related)
    "5980a733-2c81-490a-bd9f-bf896c226266",  # Gabbard resigns
    "3a2f78d2-f2ff-4dd0-acbd-7494db3e2ca7",  # Gabbard duplicate
    "81804f18-6d34-4f01-93e6-0890a5a827ea",  # Air India SFO
    "63e93935-bd62-404c-83e8-f80c09f89dd7",  # Warsh Fed
    "186120bd-3b51-4741-9b94-5f8ba037702f",  # USCIS overlap (already published)
]
for tid in topic_ids:
    code = sb_patch("p2_topics", f"id=eq.{tid}", {"status": "published"})
    if code < 300:
        print(f"  Topic {tid[:8]} → published")

print("Done!")
