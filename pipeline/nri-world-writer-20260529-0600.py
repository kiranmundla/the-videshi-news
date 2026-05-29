#!/usr/bin/env python3
"""NRI World Writer — 2026-05-29 06:00 UTC run"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load Supabase creds
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
    # ---------- ARTICLE 1 ----------
    {
        "id": str(uuid.uuid4()),
        "headline": "Gurinder Chadha Talked About Diaspora Cinema at London's India Week. It Was the Most Important Conversation Nobody in America Noticed.",
        "subheadline": "A UK-India Film Conclave, a new cultural cooperation pact, and Indian-American filmmakers at Cannes suggest diaspora cinema is entering a new phase — one where the stories are no longer about explaining yourself to the West.",
        "slug": make_slug("india-week-london-film-conclave-diaspora-cinema-chadha-cannes"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Diaspora filmmakers are moving from niche representation stories to mainstream co-production pipelines — a shift that could reshape how the Indian community abroad sees itself on screen.",
        "tags": ["nri", "diaspora", "cinema", "uk-india", "culture", "cannes"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Screen Daily", "url": "https://www.screendaily.com/news/gurinder-chadha-among-speakers-at-uks-india-week-co-production-market/5204689.article"},
            {"name": "UK Government - Cultural Cooperation Agreement", "url": "https://www.gov.uk/government/publications/memorandum-of-understanding-between-the-uk-and-india-on-cultural-cooperation"},
            {"name": "India Abroad", "url": "https://www.youtube.com/watch?v=ftp2rDCc1_A"},
            {"name": "Ticket Tailor - Film Conclave 2026", "url": "https://www.tickettailor.com/events/reelnltd/1234"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c9/Gurinder_Chadha.jpg",
        "body": """On May 26, while most of the Indian diaspora in America was still processing the Scripps Spelling Bee results, something arguably more consequential was happening across the Atlantic. At the Skyline London, a one-day event called Film Conclave brought together over 200 executives from Netflix, BBC, ITV, Bollywood studios, and independent production houses to discuss a specific question: what does UK-India co-produced cinema look like in 2026?

The headline act was Gurinder Chadha — the woman who, 24 years ago, made *Bend It Like Beckham* and essentially invented the genre of diaspora cinema that wasn't either Bollywood or a tragedy about arranged marriage. Her in-conversation session was billed as a discussion about "diasporic cinema, representation, and creative risk-taking." But the subtext was sharper: Chadha was there to talk about what comes next, now that the first generation of diaspora stories has been told.

## The infrastructure is finally catching up

Film Conclave wasn't just a panel discussion. It was the inaugural UK-India film co-production market — a structured venue where filmmakers could pitch projects, secure meetings with distributors, and explore funding pathways. The panels included sessions on increasing audience access and distribution, with speakers from the BFI, Moviegoers Entertainment, and the Australia India Film Council.

The timing was deliberate. Earlier this month, the UK and India operationalized their Free Trade Agreement, which eliminates tariffs on 90% of UK exports to India and is projected to boost bilateral trade by £25.5 billion annually. Underpinning the film event was a UK-India Cultural Cooperation Agreement signed in May 2025, a five-year pact (2025-2030) that specifically names "film, theatre and performing arts" as priority areas and commits both governments to supporting diaspora community cultural links.

This is not symbolic. The agreement, signed by India's Culture Minister Gajendra Singh Shekhawat and UK Culture Secretary Lisa Nandy, includes provisions for digital preservation, curatorial exchanges between the British Museum and Indian national institutions, and — critically for filmmakers — facilitated linkages between event organisers and cultural authorities. The British Council is the implementing body on the UK side.

## Meanwhile, at Cannes

Across the Channel, at the 79th Cannes Film Festival, Indian-American filmmakers Hemant M. Pandya and Nita Pednekar were representing independent cinema as officially accredited delegates. The duo, who run the New Jersey Indian International Film Festival and Friday Films LLC, attended world premieres, gala screenings, and Bharat Pavilion events while introducing their upcoming projects *Love, Loathe & Life* and *She Was…//?*.

Their presence at Cannes was modest compared to the Indian government's official delegation, but it represented something the diaspora film world has long lacked: independent filmmakers from the community showing up as producers and distributors, not just as subjects of someone else's documentary.

## Why this matters for NRIs

For the 5.2 million Indian Americans and the 1.8 million Indians in the UK, the cultural stakes are straightforward. The stories that get made about you shape how your neighbors, your employers, and your children's classmates understand you. For two decades, diaspora cinema oscillated between two modes: the Bollywood fantasy of NRI life (palatial London homes, helicopter weddings) and the earnest Western indie (identity crisis, disappointed parents, sari-wearing grandmothers dispensing wisdom).

What the Film Conclave and the Cannes presence suggest is a third phase — one driven by institutional pipelines rather than individual breakthroughs. When a government-backed co-production market exists, when BFI executives are in the room, when Netflix is sending representatives, the conditions for diaspora cinema change fundamentally. The stories no longer need to explain India to the West or explain the West to India. They can simply be stories, with budgets and distribution to match.

The UK-India FTA includes provisions for social security benefits for workers moving between countries — a detail that matters for film crews. The Double Contributions Convention means a cinematographer from Mumbai working on a London set won't pay into two pension systems. It's the kind of plumbing that makes sustained creative collaboration possible.

## The question nobody asked

Absent from the conversation, conspicuously, was the United States. Despite being home to the world's largest and wealthiest Indian diaspora, America has no equivalent of the UK-India Cultural Cooperation Agreement. There is no U.S.-India co-production treaty for film. Hollywood remains interested in Indian stories primarily as content for streaming platforms, not as co-production partnerships.

For now, London has positioned itself as the institutional home for diaspora cinema. Whether that leads to films that actually change how the community sees itself — or whether it simply creates a more efficient pipeline for the same stories — remains the open question. Gurinder Chadha, at least, has earned the right to ask it."""
    },

    # ---------- ARTICLE 2 ----------
    {
        "id": str(uuid.uuid4()),
        "headline": "Indians Are Sending 20% Less Money Abroad for Education. They're Sending 56% More to Foreign Stock Markets. The RBI Just Published the Numbers.",
        "subheadline": "India's outward remittances under the Liberalised Remittance Scheme fell for the first time in years. The decline in study-abroad spending tells one story. The surge in foreign equity investment tells another.",
        "slug": make_slug("rbi-lrs-fy26-education-remittance-drop-equity-investment-surge"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For NRI families whose relatives are deciding whether to send children abroad or invest in foreign markets instead, these numbers quantify a generational shift in how India's middle class thinks about going global.",
        "tags": ["nri", "diaspora", "remittance", "rbi", "education", "investment"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/money-and-banking/global-uncertainty-slows-overseas-remittances-under-lrs-in-fy26-rbi-bulletin/article71012041.ece"},
            {"name": "Finnovate", "url": "https://finnovate.in/indias-140-billion-remittance-record/"},
            {"name": "Reserve Bank of India - May 2026 Bulletin", "url": "https://rbi.org.in/"}
        ]),
        "score_total": 74,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7616700/pexels-photo-7616700.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "body": """The Reserve Bank of India's May bulletin contained a data set that, on the surface, looked like a routine statistical update. Total outward remittances under the Liberalised Remittance Scheme fell 2% year-on-year to $28.9 billion in FY26, down from $29.6 billion. The number barely made headlines in India.

But buried in the breakdown was a story about a generational shift in how India's aspiring middle class relates to the world — and it has direct implications for every NRI family fielding calls from relatives about whether to send the next generation abroad.

## The study-abroad dream is getting expensive and uncertain

The most dramatic number in the bulletin: remittances for studies abroad fell over 20%, from $2.9 billion to $2.3 billion. That's $600 million in education spending that simply didn't happen.

The reasons are structural, not cyclical. The United States has tightened visa norms under the second Trump administration. The UK, post-Brexit, has imposed stricter post-study work regulations. Canada, which was absorbing Indian students at record rates, has capped international student permits. Australia has raised financial threshold requirements for student visas.

For the Indian families who have historically seen a foreign degree as the single most reliable investment in their children's future, the calculus has shifted. A master's degree at a mid-tier American university now costs upward of $80,000 — and the path from F-1 visa to H-1B to green card has become less predictable than at any point in the last two decades. Analysts told *The Hindu Business Line* that weak global job markets, particularly for STEM roles, have compounded the problem. Students are increasingly opting for lower-cost destinations or staying home entirely.

## Where the money is going instead

Here's the counterpoint that makes the data genuinely interesting: while education and travel remittances fell, investment in foreign equity and debt surged 56% year-on-year to $2.7 billion. Indians who once would have sent their savings abroad in the form of tuition fees are now sending it to Nasdaq and London stock markets.

This is not a small shift. At $2.7 billion, foreign equity investment through LRS now exceeds education remittances for the first time. The Indian saver who once aspired to a Stanford admit letter for their child is, apparently, now comfortable with an S&P 500 index fund instead.

The rupee's depreciation — down roughly 6% since the West Asia conflict erupted in late February — has made dollar-denominated investments more expensive. But it has also made the returns, when converted back to rupees, more attractive. For an Indian investor buying into U.S. equities, a depreciating rupee functions as an additional return multiplier.

## The RBI is watching more closely

For the first time in its bulletin, the RBI provided a purpose-wise split of travel remittances — distinguishing between holiday spending, credit card settlements abroad, and education-related travel expenses. Out of $1.09 billion in March 2026 travel remittances, $620 million went to holidays and credit card bills, while $450 million covered education travel.

This new granularity signals something: the central bank is paying closer attention to where exactly India's dollars are flowing under LRS. The scheme, which allows resident Indians to remit up to $250,000 per year for specified purposes, has been a quiet pipeline for capital outflows. The government imposed a 20% TCS (Tax Collected at Source) on LRS remittances above ₹7 lakh in 2023 to discourage frivolous outflows. The Union Budget 2026 partially eased this for education, but the overall regulatory direction remains cautious.

## What NRIs should watch

For the diaspora, these numbers land differently. The 20% decline in education remittances means fewer Indian students arriving in American and British universities each year — which means smaller incoming cohorts of people who might eventually join the NRI community. The pipeline that has fed the Indian diaspora's growth for 30 years is narrowing.

At the same time, the surge in foreign equity investment suggests that India's upper-middle class is increasingly comfortable operating in global financial markets without physically relocating. They want the returns of being global without the friction of being an immigrant. It's a form of diaspora participation that doesn't require a visa.

The implications are paradoxical. India's outward remittance data says the country is becoming more globally connected financially — and less globally connected physically. For NRI communities that have relied on a steady stream of new arrivals to sustain Indian grocery stores, temple communities, and weekend language schools, the shift is worth paying attention to. The money is still flowing outward. The people, increasingly, are not."""
    },

    # ---------- ARTICLE 3 ----------
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Central Bank May Ask NRIs to Save the Rupee. It Worked in 2013. The World Was Different Then.",
        "subheadline": "With the rupee at record lows near ₹97 to the dollar, the RBI is reportedly considering a revival of NRI deposit schemes that raised $26 billion during the last currency crisis. Whether diaspora savers will answer the call again is the $26 billion question.",
        "slug": make_slug("rbi-nri-deposit-scheme-rupee-crisis-2013-revival-fcnr"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "NRIs could see preferential interest rates on rupee and dollar deposits — but the decision to park money in India during a currency crisis is as much about trust in the Indian economy as it is about rates.",
        "tags": ["nri", "diaspora", "rbi", "rupee", "deposits", "banking", "fcnr"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indian-banks-seek-hedging-cost-subsidy-rbi-raise-dollar-funding-sources-say-2026-05-22/"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/money-and-banking/to-attract-dollars-rbi-may-revive-the-2013-strategy-to-incentivise-banks-to-mop-up-non-resident-deposits/"},
            {"name": "Madhyama", "url": "https://madhyamamonline.com/rbi-evaluating-multiple-steps-check-rupee-decline/"},
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/nri-deposits-fall-by-nearly-19000-crore-in-march-amid-west-asia-crisis"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/14907377/pexels-photo-14907377.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "body": """Somewhere in the Reserve Bank of India's headquarters on Mint Road in Mumbai, officials are reportedly studying a playbook from 2013. That year, when the rupee was in freefall against the dollar, the RBI opened a special window for banks to raise Foreign Currency Non-Resident (FCNR-B) deposits at concessional swap rates. NRIs responded. Within three months, Indian banks had raised approximately $26 billion in fresh dollar deposits from the diaspora — enough to stabilize the currency and replenish reserves.

Thirteen years later, the RBI appears to be weighing the same play. Reuters reported earlier this month that the central bank is studying ways to mobilize dollar inflows, with NRI deposit schemes among the options under consideration. Sources told Madhyama Online that the RBI is evaluating the launch of FCNR deposits, NRI bonds, and additional rupee-dollar swap operations. No final decision has been taken.

The question is whether the 2013 playbook still works in 2026.

## The crisis, in numbers

The rupee hit a record low of ₹96.96 against the dollar on a single day in May, having depreciated roughly 6% since the West Asia conflict escalated on February 28. RBI Governor Sanjay Malhotra told the Mint newspaper that the currency "has become undervalued, both in nominal as well as in REER terms" — the kind of statement central bankers make when they're preparing the ground for intervention.

The RBI has already deployed conventional tools. State-run banks have been spotted selling dollars in the market — most likely on the central bank's behalf — with at least $2 billion in intervention on a single day. A $5 billion buy/sell swap auction was conducted on May 26, oversubscribed nearly twice over at $9.8 billion. The central bank holds nearly $700 billion in reserves, a formidable war chest by any standard.

But the NRI deposit picture has darkened at precisely the wrong moment. Outstanding NRI deposits fell by roughly $2 billion in March alone, from $167.58 billion to $165.65 billion. Annual NRI deposit inflows dropped to $14.41 billion in FY26 from $16.16 billion the previous year. The decline is concentrated in Gulf-origin deposits, where the West Asia conflict has disrupted remittance flows from the approximately 9 million Indians working in the region.

## What the 2013 scheme looked like

In September 2013, the RBI allowed banks to raise FCNR-B deposits of three years or more and swap the resulting dollars with the central bank at concessional rates — effectively subsidizing the hedging cost for banks and allowing them to offer NRIs attractive interest rates on dollar deposits without taking on currency risk.

The scheme was elegantly designed. Banks got cheap dollars. The RBI got reserve accretion. NRIs got above-market rates on safe deposits. The rupee stabilized. Within months, the currency recovered from its then-record low of around ₹68.

The catch came three years later, when approximately $20 billion in FCNR-B deposits matured simultaneously in September 2016. The RBI had to manage a massive dollar outflow in a compressed window — a challenge it navigated, but one that underscored the risks of time-bound deposit schemes.

## Why 2026 is different

Several factors make a 2013-style NRI deposit scheme harder to execute today.

First, interest rates. In 2013, U.S. interest rates were near zero, making Indian deposit rates look exceptionally attractive. In 2026, the Federal Reserve's benchmark rate sits meaningfully higher, compressing the spread that makes NRI deposits attractive relative to simply keeping money in an American savings account or Treasury bills.

Second, the rupee's trajectory. In 2013, the depreciation was driven primarily by the "taper tantrum" — a temporary market reaction to the Federal Reserve's signaling that it would reduce bond purchases. The underlying Indian economy was sound. In 2026, the depreciation is driven by a genuine geopolitical shock — the West Asia conflict — combined with persistent current account pressures and crude oil prices that show no sign of retreating.

Third, the NRI community itself has changed. The diaspora is wealthier, more financially sophisticated, and has access to more investment options than it did in 2013. An NRI in Silicon Valley or London making the decision to park dollars in an Indian bank will weigh not just the interest rate but the currency risk, the geopolitical outlook, and the opportunity cost of not investing in U.S. equities that have delivered strong returns.

## What NRIs should actually do

For the average NRI, the practical question is straightforward: if the RBI does launch a special deposit scheme, should you participate?

The answer depends on your rupee exposure. If you have significant expenses in India — elderly parents, property maintenance, children's education, planned return — locking in dollar-to-rupee conversion at current rates through an FCNR deposit could be rational. The rupee at ₹97 is, by the RBI's own assessment, undervalued. A three-year deposit initiated now would mature when the currency has presumably recovered.

If your life is entirely in dollars and you have no near-term rupee needs, the calculation is less compelling. You'd be taking on India-specific risk — however small — for a premium over U.S. rates that may not be dramatic.

The RBI has not confirmed any scheme. But the signals are clear enough that NRIs with significant liquid savings should be paying attention. The central bank is building toward something. The last time it did, diaspora savers earned attractive returns and helped stabilize their home country's currency in the process. Whether that alignment of incentives can be replicated in a harder macroeconomic environment is the real test."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
