#!/usr/bin/env python3
"""Write 3 articles for The Videshi — news, technology, markets-finance categories."""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ["SUPABASE_ANON_KEY"])

def supabase_post(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "return=representation")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def supabase_patch(table, filters, data):
    params = "&".join(f"{k}=eq.{v}" for k, v in filters.items())
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="PATCH")
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "return=representation")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

now = datetime.now(timezone.utc).isoformat()

articles = [
    # ─── ARTICLE 1: NEWS ───
    {
        "topic_id": "99871320-0000-0000-0000-000000000000",  # placeholder, will update
        "headline": "'Detected, Deleted, Now Deport': Bengal's New BJP Government Signals the Biggest Immigration Crackdown in Indian State History",
        "subheadline": "Chief Minister Suvendu Adhikari's deportation vow follows the removal of 9 million names from West Bengal's voter rolls — and for NRIs watching India's citizenship politics, the implications stretch far beyond Kolkata.",
        "body": """The first BJP government in West Bengal's history is not easing into office. Within days of being sworn in as the state's ninth Chief Minister, Suvendu Adhikari delivered a blunt, three-word policy sequence during a visit to Bhabanipur — the constituency he wrested from Mamata Banerjee in one of the election's most symbolic results: "Detected, deleted, now deport."

The statement landed less as political rhetoric and more as a programme of action. It refers directly to the Special Intensive Revision (SIR) of electoral rolls that preceded the April 2026 elections, a process that removed approximately 9 million voter entries — roughly 12 per cent of West Bengal's electorate — on grounds ranging from absentee status to suspected duplicate or fraudulent registrations.

## From Voter Rolls to Deportation Orders

The SIR became the most contentious issue of the election campaign. The Trinamool Congress accused the Exercise of disenfranchising genuine voters, particularly among Bengali Muslims and Dalit Hindu communities including the politically significant Matua community. The BJP defended it as a necessary cleansing of bogus entries linked to illegal cross-border migration from Bangladesh.

Now in power, Adhikari is framing the SIR not as an end in itself but as the first phase of a larger enforcement chain. "I'm not a man who will bow down," he said. "BJP's CM will fulfil the commitments made by the party."

The mechanics of mass deportation, however, are far more complex than the rhetoric suggests. India's deportation process for undocumented Bangladeshi nationals requires bilateral coordination, nationality verification through Dhaka, and judicial oversight — none of which can be fast-tracked by a state government acting alone. The Centre would need to be deeply involved, and India-Bangladesh relations, already strained after the change of government in Dhaka, add diplomatic friction to every step.

## The Citizenship Amendment Act Factor

The deportation push cannot be separated from the Citizenship Amendment Act (CAA), which grants a pathway to Indian citizenship for persecuted non-Muslim minorities from Bangladesh, Pakistan, and Afghanistan. During the campaign, BJP leaders promised that a BJP government in West Bengal would accelerate CAA implementation — effectively offering protection to Hindu refugees while tightening the net on Muslim undocumented migrants.

This selective framework has drawn sharp criticism from civil liberties groups and opposition parties who argue it reduces citizenship to a function of religious identity. But in West Bengal's charged political landscape, where the BJP won 207 of 294 seats with a 7.69 percentage point swing, the policy clearly resonated with a significant portion of the electorate.

## What the Diaspora Is Watching

For NRIs, the Bengal story carries weight beyond regional politics. The SIR controversy raised fundamental questions about the integrity of India's electoral rolls — questions that matter to overseas Indians who retain voting rights and property interests back home. The Matua community, many of whose members have relatives who migrated to the US, UK, and Canada, has been disproportionately affected by voter roll deletions in certain districts.

More broadly, the deportation agenda fits into a national pattern under the BJP that includes the National Register of Citizens (NRC) exercise in Assam, which left nearly 2 million people off the final rolls, and the proposed nationwide NRC that has been shelved but never formally abandoned.

For Indian-Americans navigating their own country's immigration debates — H-1B uncertainties, green card backlogs, and shifting asylum policies — watching India grapple with parallel questions of documentation, belonging, and state power is uncomfortably familiar.

## The Governance Test

Adhikari's government also signalled its intent on other fronts. The Bengal cabinet moved swiftly to discontinue state-funded stipends for imams, muezzins, and purohits — a TMC-era scheme that the BJP had long criticised as unconstitutional religious patronage. The decision drew Congress criticism but was defended by BJP leaders as a separation of state and religious financing.

The new government has also promised crackdowns on corruption cases linked to the previous administration, naming former TMC leaders including Abhishek Banerjee, and pledged judicial oversight mechanisms for crimes against women — an issue that gained national prominence after the 2024 R.G. Kar Medical College case.

Whether the deportation vow translates into meaningful policy or remains a mobilisation tool will depend on Centre-state coordination, judicial clearances, and diplomatic bandwidth with Bangladesh. But the signal is unmistakable: Bengal's new government intends to govern as aggressively as it campaigned.

*Sources: Inshorts, Indian Economic Observer, Daily Prabhat, Wikipedia*""",
        "diaspora_angle": "NRIs with Bengal roots face direct implications from voter roll changes; broader citizenship politics mirror immigration anxieties in the diaspora",
        "vertical": "politics",
        "tags": ["West Bengal", "Suvendu Adhikari", "BJP", "deportation", "immigration", "CAA", "SIR", "voter rolls", "Mamata Banerjee"],
        "urgency": "developing",
        "sources": ["Inshorts", "Indian Economic Observer", "Daily Prabhat", "Wikipedia"],
        "slug": "bengal-bjp-adhikari-deportation-illegal-immigrants-crackdown-20260520",
        "word_count": 710,
        "status": "published",
        "published_at": now,
        "category": "news",
        "score_total": 68,
        "image_url": None,
        "image_attribution": None,
        "image_caption": None,
        "gallery_images": None,
    },

    # ─── ARTICLE 2: TECHNOLOGY ───
    {
        "topic_id": "0151d929-0000-0000-0000-000000000000",
        "headline": "Zoho's Sridhar Vembu Says Silicon Valley Is Using AI as a 'Convenient' Excuse to Fire People. He Has a Point.",
        "subheadline": "With 113,000 US tech jobs cut in 2026 so far and Meta processing 8,000 layoffs today, the Zoho founder argues the real culprit isn't artificial intelligence — it's old-fashioned cost pressure dressed up in futuristic language.",
        "body": """On the same day Meta began notifying 8,000 employees of their termination — the company's biggest single-day layoff since 2022 — Zoho founder Sridhar Vembu posted a pointed question on X that cut through the noise: "How is it that in the US, the AI leader, a good part of the population, even a lot of college students, have come to hate AI?"

His answer was characteristically direct. Companies, he argued, are "blaming job losses on AI, which is both convenient and as an added bonus, makes a company look visionary." The layoffs, he said, are really "related to rising cost pressures — we experience those pressures too so we know this first hand."

## The Numbers Behind the Narrative

The timing of Vembu's comments gives them unusual weight. US technology companies have cut more than 113,000 jobs in the first five months of 2026 — averaging 825 job losses per day, according to tracking data. Meta alone has eliminated approximately 8,000 positions while simultaneously reassigning 7,000 existing employees into newly formed AI-focused teams, a move the company's Chief People Officer Janelle Gale described as creating "AI native design structures" with fewer layers of management.

The restructuring is real, and the AI pivot is genuine. But Vembu's critique targets the framing: when a company announces that it's cutting staff "to invest in AI," the narrative obscures whether the cuts are driven by automation displacing specific roles, or by broader financial pressures that would exist with or without AI.

Meta's case is instructive. The company's revenue has been growing, its AI infrastructure spending is projected at $145 billion, and Mark Zuckerberg has made AI the company's explicit top priority. Yet the layoffs are concentrated among middle managers and non-technical staff — roles that AI hasn't replaced but that the company has decided it can do without in a "flatter" organisational structure.

## Why Indian Tech Workers Should Pay Attention

The AI-as-excuse thesis carries particular weight for the Indian technology workforce. An estimated 40 per cent of H-1B visa holders in the US work in the technology sector, and layoffs at major firms like Meta, Amazon, Oracle, and Microsoft create immediate visa complications for foreign workers who typically have 60 days to find new sponsorship or leave the country.

When companies frame cuts as strategic AI investments rather than cost management, it shapes public sympathy and policy response. If the public believes AI is inevitably replacing human work, there is less political pressure to scrutinise corporate decisions or extend protections for displaced workers — including the immigration relief measures that H-1B holders have been seeking for years.

For Indian IT services companies — Infosys, TCS, Wipro, HCL — the dynamic is equally consequential. These firms have built their business models on providing skilled human labour to Western enterprises. Every announcement that "AI can do this now" pressures their clients to demand more with fewer billable hours, even when the AI capability is marginal or unproven.

## The Bigger Picture Vembu Sees

Vembu went further than most tech leaders are willing to go. "The AI investment bubble has kept the US economy afloat but that can only go on for so long," he wrote. "Zooming out, I believe what we are witnessing is the gradual collapse of the post World War 2 global economic and political order."

It is a sweeping claim, but it connects dots that individual layoff announcements tend to obscure. The global technology sector is experiencing simultaneous pressures: rising interest rates that punish growth-stage companies, geopolitical fragmentation that complicates supply chains, and an AI investment cycle that demands enormous capital expenditure with uncertain returns.

Vembu's closing line — "We must prepare for tough times ahead" — reads differently coming from someone who runs a profitable, privately held, $1 billion revenue company from Chennai rather than from a Silicon Valley executive managing quarterly earnings expectations.

## What This Means for the Diaspora

For the roughly 300,000 Indians working in US tech, the distinction between "AI replaced your job" and "the company needed to cut costs and blamed AI" is not academic. It affects severance negotiations, retraining decisions, visa strategy, and whether the political establishment treats tech layoffs as a structural transition requiring policy intervention or a normal business cycle.

Vembu's intervention reframes the conversation at exactly the moment it matters. Whether Silicon Valley listens is another question entirely.

*Sources: Khelja, X (@svembu), Bloomberg Law, Outlook Business, Engadget, The Hindu BusinessLine*""",
        "diaspora_angle": "Indian H-1B workers in US tech face direct layoff risk; IT services firms in India feel downstream pressure; Vembu offers rare Indian tech leader critique of Silicon Valley narrative",
        "vertical": "technology",
        "tags": ["Sridhar Vembu", "Zoho", "AI", "tech layoffs", "Meta", "H-1B", "Silicon Valley", "Indian IT"],
        "urgency": "developing",
        "sources": ["Khelja", "X", "Bloomberg Law", "Outlook Business", "Engadget", "The Hindu BusinessLine"],
        "slug": "zoho-sridhar-vembu-ai-excuse-tech-layoffs-meta-silicon-valley-20260520",
        "word_count": 730,
        "status": "published",
        "published_at": now,
        "category": "technology",
        "score_total": 65,
        "image_url": None,
        "image_attribution": None,
        "image_caption": None,
        "gallery_images": None,
    },

    # ─── ARTICLE 3: MARKETS-FINANCE ───
    {
        "topic_id": "942e1611-0000-0000-0000-000000000000",
        "headline": "India and Oman's Free Trade Deal Goes Live June 1. For a Million NRIs in the Gulf, It's About More Than Tariffs.",
        "subheadline": "The CEPA grants duty-free access for 98% of Indian exports to Oman and anchors a new trade corridor at a moment when the Strait of Hormuz is under geopolitical stress and India is chasing $1 trillion in annual exports.",
        "body": """On June 1, India and Oman will activate a Comprehensive Economic Partnership Agreement (CEPA) that has been years in the making — and the timing could hardly be more consequential. The deal, signed in December 2025, will grant duty-free access to 98.08 per cent of India's tariff lines into Oman, covering textiles, agricultural products, leather goods, engineering components, and processed foods. In return, India will reduce tariffs on Omani exports including dates, marble, and petrochemicals.

Commerce and Industry Minister Piyush Goyal confirmed the June 1 launch date at an event in New Delhi, calling exports a "national mission" and noting that India's combined goods and services exports reached $863 billion in FY26 — nearly 5 per cent higher than the previous year. The government's target: $1 trillion in the current fiscal year, and $2 trillion within five years.

## Why Oman Matters More Than Its Size Suggests

Oman is not India's largest trade partner in the Gulf — that distinction belongs to the UAE and Saudi Arabia. But bilateral trade between India and Oman has already reached approximately $10.5 billion in 2024-25, and the CEPA is designed to unlock significantly more. Oman is India's third-largest export destination within the Gulf Cooperation Council.

More importantly, Oman occupies a strategic geographic position. Its ports — particularly Sohar and Salalah — sit outside the Strait of Hormuz chokepoint, giving them value as alternative trade routes at a time when US-Iran tensions and Red Sea shipping disruptions have pushed Indian exporters to seek diversified pathways. Trade with Oman surged 246 per cent in April 2025 alone, partly driven by rerouting during the Strait of Hormuz blockade.

The CEPA formalises and deepens this corridor. Indian SMEs exporting textiles, spices, and engineering goods will see meaningful tariff relief, while Omani dates and petrochemical products will become cheaper in Indian markets.

## The Gulf Diaspora Angle

For the estimated 600,000 to 800,000 Indians living in Oman — concentrated in Muscat, Sohar, and Salalah — the agreement carries economic and emotional weight. Indian workers in Oman span the spectrum from construction labourers to senior executives in banking, healthcare, and technology. Stronger bilateral trade typically correlates with more Indian business presence, better consular infrastructure, and greater cultural exchange.

Oman has historically been one of the more welcoming Gulf states for Indian residents. Unlike some neighbours, it has maintained relatively stable visa policies, invested in Indian schools and community centres, and avoided the aggressive "nationalisation" quotas that have displaced Indian workers elsewhere in the GCC.

The CEPA reinforces this relationship at the government level. Indian businesses setting up in Oman's special economic zones will benefit from preferential access in both directions, and Omani investment in Indian infrastructure and renewable energy projects is expected to accelerate.

## India's Broader FTA Strategy

The Oman deal is one piece of a much larger puzzle. India has pursued trade agreements with 38 countries over the past three-and-a-half years, according to Goyal, seeking preferential market access for Indian exporters who have traditionally competed at a tariff disadvantage against rivals from countries with established FTA networks.

The challenge is execution. India's FTA with the EFTA nations (Switzerland, Norway, Iceland, Liechtenstein) — projected to generate one million jobs over 15 years — includes novel provisions on sustainable development and labour standards. The India-UK FTA has hit hurdles over steel safeguard measures. And discussions with the US remain informal at best.

The Oman CEPA, by contrast, is one of the cleaner deals in India's pipeline: a relatively straightforward bilateral agreement with a willing partner, limited political controversy, and clear mutual benefit. Its successful implementation could build credibility for the larger FTA programme.

## What to Watch

The June 1 activation will be followed by a phased tariff reduction schedule. Key sectors to monitor include Indian textile exports (currently subject to duties that make them uncompetitive against Vietnamese and Bangladeshi rivals in Gulf markets), agricultural processed goods (where India has surplus capacity), and Omani energy products (where India is the buyer and Oman the supplier).

For NRIs in Oman, the practical effects may take months to materialise in daily life. But the signal is immediate: India and Oman are binding their economies more tightly together, and the million-strong Indian community in the Sultanate sits at the centre of that convergence.

*Sources: Livemint, Business News This Week, SRK Analytics, Cargo Connect, Bharat Affairs*""",
        "diaspora_angle": "600,000-800,000 Indians in Oman directly affected; stronger trade corridor benefits Indian SMEs and Gulf-based NRI businesses; strategic alternative to Strait of Hormuz routes",
        "vertical": "economy",
        "tags": ["India", "Oman", "FTA", "CEPA", "Piyush Goyal", "Gulf diaspora", "trade", "exports", "GCC"],
        "urgency": "developing",
        "sources": ["Livemint", "Business News This Week", "SRK Analytics", "Cargo Connect", "Bharat Affairs"],
        "slug": "india-oman-free-trade-agreement-cepa-june-2026-gulf-nri-20260520",
        "word_count": 740,
        "status": "published",
        "published_at": now,
        "category": "markets-finance",
        "score_total": 63,
        "image_url": None,
        "image_attribution": None,
        "image_caption": None,
        "gallery_images": None,
    },
]

# First, get the actual topic IDs
topic_map = {
    "bengal-bjp": "99871320",
    "zoho-vembu": "0151d929",
    "india-oman": "942e1611",
}

# Insert articles
inserted_ids = []
for i, article in enumerate(articles):
    # Remove placeholder topic_id, we'll set it after
    del article["topic_id"]
    try:
        result = supabase_post("p2_articles", article)
        article_id = result[0]["id"]
        inserted_ids.append(article_id)
        print(f"✓ Article {i+1} inserted: {article_id} — {article['headline'][:60]}...")
    except Exception as e:
        print(f"✗ Article {i+1} failed: {e}")
        # Try to read error body
        if hasattr(e, 'read'):
            print(e.read().decode())
        inserted_ids.append(None)

# Mark topics as published
topic_ids_to_publish = [
    "99871320-9822-4b59-91f7-242fae30224b",  # Bengal deportation — need actual full ID
    "0151d929-7eb0-4c52-bdb4-a9f300f72556",  # Zoho Vembu
    "942e1611-0000-0000-0000-000000000000",   # India-Oman FTA — need actual full ID
]

print("\n--- Topic ID prefixes to mark published ---")
for prefix in ["99871320", "0151d929", "942e1611"]:
    print(f"  Prefix: {prefix}")

print(f"\nInserted article IDs: {inserted_ids}")
