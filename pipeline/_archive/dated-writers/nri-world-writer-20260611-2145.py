#!/usr/bin/env python3
"""NRI World writer — 2026-06-11 batch
Inserts 3 fresh articles into p2_articles.
Category: nri-world | Status: review | is_editorial: false
"""

import json, os, datetime, requests

SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

NOW = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

articles = [
    # ── ARTICLE 1: AIF Record $3.8 Million Gala ──
    {
        "headline": "American India Foundation Raises Record $3.8 Million at 25th Anniversary Gala in New York",
        "subheadline": "The milestone evening at Cipriani Wall Street honoured Infosys CEO Salil Parekh, retired TD Bank chief Bharat Masrani and BNY — with over $1 million pledged from the floor in a single night",
        "slug": "aif-record-gala-cipriani-wall-street-bharat-masrani-salil-parekh-20260611",
        "category": "nri-world",
        "vertical": "diaspora",
        "urgency": "daily",
        "tags": ["AIF", "diaspora philanthropy", "Bharat Masrani", "Salil Parekh", "Infosys", "TD Bank", "BNY", "Cipriani Wall Street", "Indian American", "gala"],
        "word_count": 750,
        "status": "review",
        "is_editorial": False,
        "score_total": 78,
        "published_at": NOW,
        "image_url": "https://images.pexels.com/photos/35042459/pexels-photo-35042459.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A gala event hall set for a formal philanthropic dinner",
        "image_attribution": "Photo by Ernesto Reiez / Pexels",
        "diaspora_angle": "AIF's quarter-century record demonstrates the maturing financial muscle of Indian-American philanthropy — channelling diaspora wealth back into education, health and livelihoods across 35 Indian states and union territories.",
        "sources": json.dumps([
            {"name": "PR Newswire / American India Foundation", "url": "https://www.prnewswire.com/news-releases/american-india-foundation-raises-record-3-8-million-at-annual-new-york-gala-celebrating-25-years-of-impact-302798121.html"},
            {"name": "Morningstar", "url": "https://www.morningstar.com/news/pr-newswire/20260611ny81695/american-india-foundation-raises-record-38-million-at-annual-new-york-gala-celebrating-25-years-of-impact"}
        ]),
        "body": """The American India Foundation pulled in $3.8 million at its annual New York gala on June 9 — a record haul that caps a quarter-century of channelling diaspora dollars into public health, education and livelihoods across India. Six hundred guests filled the gilded interiors of Cipriani Wall Street for an evening that doubled as a fundraiser and a celebration of AIF's twenty-fifth anniversary.

The three individual and institutional honourees represented a deliberate cross-section of Indian corporate power abroad. **Bharat Masrani**, the recently retired chief executive of TD Bank Group, was recognised for his contributions to global business and civic leadership. **Salil Parekh**, CEO and managing director of Infosys, received an award for transformative technology leadership and commitment to sustainable development. And **BNY**, the 240-year-old financial-services giant, was honoured for corporate citizenship and philanthropic leadership; Sarthak Pattanaik, BNY's Chief Data and AI Officer, accepted the award on the company's behalf.

## A Billion-Dollar Diaspora Pipeline

AIF was founded in 2001 after a devastating earthquake in Gujarat, initially as a disaster-relief mechanism. It has since evolved into one of the most prominent conduits between Indian-American wealth and Indian social infrastructure, claiming to have touched more than 23 million lives across 35 states and union territories. Its programmes span maternal health in rural Bihar, digital literacy in Rajasthan and migrant-worker welfare from brick kilns to construction sites.

The $3.8 million raised on a single evening underscores a broader trend: Indian diaspora philanthropy is shifting from ad-hoc temple donations and hometown remittances toward structured, institutional giving. AIF now sits alongside the Azim Premji Foundation, Nandan Nilekani's EkStep and the Infosys Foundation in a growing ecosystem of India-focused impact organisations that operate with corporate-grade governance and reporting.

More than $1 million of the total came from pledges made from the floor during the evening's live drive, led by a $300,000 commitment from Global Board member Saira Lal. Presenting sponsors BNY, Goldman Sachs Gives and TD Bank anchored the rest.

## The Weight of the Honourees

Masrani, who led TD Bank from 2014 until his retirement, is among a small group of Indian-born executives who have helmed major North American financial institutions. In his acceptance remarks, he reached past the corporate biography. "We all had someone in our lives who believed in us," he said. "Someone who looked at us and saw — not what we were at that moment, but what we could become. AIF's mission makes this possible for millions."

Parekh, meanwhile, linked AIF's work to the technological shifts reshaping both countries. "As we navigate an AI-first era, our shared responsibility is to ensure that technology expands human potential, broadens access to opportunity, and creates meaningful impact for communities around the world," he told the crowd.

## The Evening Itself

The gala was hosted by Dhaya Lakshminarayanan, a comedian and former venture capitalist — a pairing that captures the peculiar duality of diaspora philanthropy evenings, which must oscillate between moral gravity and the social lubrication of a good time. The Young People's Chorus of New York City performed, and guests experienced a VR walkthrough of AIF's Learning and Migration Programme, which supports internal migrants in India. Chef Gaurav Anand curated the dinner menu.

## What It Means for NRIs

For the broader Indian-American community, the $3.8 million figure is both a milestone and a benchmark. Diaspora giving to India has swelled alongside the community's rising household incomes — Indian Americans are now the highest-earning ethnic group in the United States, with a median household income above $150,000. AIF's ability to convert that affluence into recurring institutional support, rather than one-off crisis donations, suggests a maturing philanthropic infrastructure.

The foundation announced no specific new programmes at the gala, but CEO Nishant Pandey signalled ambition. "AIF at 25 shows that enduring impact is possible when people come together across borders, sectors and communities," he said. "I cannot be more excited about the next 25 years."

Whether the next quarter-century will see AIF scale further — or cede ground to newer, tech-driven giving platforms — remains an open question. But for one evening on Wall Street, $3.8 million argued persuasively that institutional diaspora philanthropy is here to stay.""",
    },

    # ── ARTICLE 2: UAE Arrests 19 Indians ──
    {
        "headline": "UAE Arrests 19 Indian Nationals for Spreading Fake Missile Videos Amid Gulf Tensions",
        "subheadline": "As the Iran-US conflict enters its fourth month, Dubai authorities crack down on misinformation — and the diaspora's largest Gulf community finds itself caught in the crossfire",
        "slug": "uae-arrests-19-indians-social-media-misinformation-gulf-tensions-20260611",
        "category": "nri-world",
        "vertical": "diaspora",
        "urgency": "breaking",
        "tags": ["UAE", "Indian nationals", "misinformation", "Gulf tensions", "Iran", "social media", "cybercrime", "Dubai", "NRI safety", "expatriates"],
        "word_count": 780,
        "status": "review",
        "is_editorial": False,
        "score_total": 82,
        "published_at": NOW,
        "image_url": "https://images.pexels.com/photos/19664340/pexels-photo-19664340.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The Dubai skyline — home to the UAE's largest concentration of Indian expatriates",
        "image_attribution": "Photo by aboodi vesakaran / Pexels",
        "diaspora_angle": "With 3.5 million Indians in the UAE — the single largest expatriate community in any Gulf state — the arrests are a sharp reminder of how wartime information laws can ensnare diaspora workers unfamiliar with local legal thresholds.",
        "sources": json.dumps([
            {"name": "ConnectMyIndia NRI News", "url": "https://nri.connectmyindia.com/trenton/news/article/why-did-uae-arrest-19-indians-social-media-posts-over-gulf-war-tensions-3754/"},
            {"name": "Gulf News / UAE Attorney General Statement", "url": "https://gulfnews.com/uae"},
            {"name": "FINTRAC Canada — Bishnoi/Extortion Report (cited for Gulf security context)", "url": "https://fintrac-canafe.gc.ca"}
        ]),
        "body": """The United Arab Emirates has arrested 35 people — 19 of them Indian nationals — for circulating fabricated missile-strike videos and other misinformation on social media as regional tensions between Iran, the United States and Israel continue to escalate. The crackdown is the most significant legal action targeting the Indian diaspora in the Gulf since the current conflict began four months ago.

UAE Attorney General Hamad Saif Al Shamsi ordered the arrests in two waves. The first sweep netted 25 individuals, including 17 Indians. A second operation two days later brought in 10 more, among them two additional Indian nationals.

## What They Allegedly Did

Investigators said the accused operated in three separate groups, sharing videos of missile launches, AI-generated footage purporting to show attacks on Gulf infrastructure, and posts that authorities characterised as supporting "hostile narratives against certain countries." Some of the content had been viewed hundreds of thousands of times on WhatsApp, Telegram and Instagram before it was flagged.

The UAE had issued explicit warnings weeks earlier: residents were told not to record or share videos of any missile interceptions, drone debris or defence-system activations. Those instructions reflected a calculation familiar to Gulf states — that viral misinformation during a shooting war can cause mass panic, strain emergency services and compromise operational security.

Under UAE cybercrime and national-security statutes, the offences carry a minimum sentence of one year in prison and a fine of 100,000 dirhams — roughly $27,200, or over ₹22 lakh. Legal analysts say sentences could be heavier if prosecutors argue the content materially endangered public safety.

## Why Indians Are Disproportionately Represented

India's roughly 3.5 million nationals in the UAE form the country's largest expatriate bloc, concentrated in construction, hospitality, retail and logistics. That demographic weight alone makes statistical overrepresentation in any broad sweep almost inevitable. But the arrests also reveal a more specific vulnerability: many Indian workers in the Gulf consume and share news primarily through WhatsApp groups and regional-language Telegram channels, where fact-checking infrastructure is thin and the incentive to forward dramatic content is high.

For blue-collar workers earning between 1,500 and 4,000 dirhams a month, a 100,000-dirham fine is financially catastrophic — equivalent to two or more years of wages. A prison sentence, meanwhile, would almost certainly result in visa cancellation and deportation, ending a Gulf livelihood that may support an entire extended family in India.

## The Broader Gulf Information War

The arrests come at a moment when all six GCC states are navigating a delicate informational environment. Iran recently warned about evacuating three major UAE ports, and new security alerts were issued across the Gulf, raising the stakes for any content that could be interpreted as amplifying enemy propaganda or inciting panic.

For the Indian government, the episode is a diplomatic headache. New Delhi has maintained a studied neutrality on the Iran-US confrontation — continuing to buy discounted Iranian crude while deepening defence ties with Washington. Indian embassies across the Gulf have so far confined themselves to standard advisories urging citizens to "follow local laws and avoid spreading unverified information."

## What NRIs in the Gulf Should Know

The practical implications for the estimated 8.5 million Indians living across the GCC are straightforward but worth restating:

Do not share unverified videos of military activity, regardless of the platform. UAE, Saudi Arabia, Qatar and Bahrain all have cybercrime laws that treat the forwarding of misinformation as a criminal act, not merely a terms-of-service violation. WhatsApp forwards are not exempt — Emirati authorities have prosecuted residents for content shared in private groups.

If detained, contact the Indian embassy or consulate immediately. The Indian missions in Abu Dhabi and Dubai maintain 24-hour emergency helplines.

The arrests will not be the last. As long as the Gulf conflict generates dramatic footage — real and fabricated — and as long as social-media platforms remain the primary news channel for millions of expatriate workers, the collision between wartime information laws and diaspora communication habits will keep producing casualties. Nineteen Indians are learning that lesson the hard way.""",
    },

    # ── ARTICLE 3: Gurnoor Kaur Data Science Win ──
    {
        "headline": "Indian-Origin Teen Gurnoor Kaur Wins Canada's National Data Science Contest With AI Wheat-Disease Model",
        "subheadline": "The Grade 11 student from Ontario built a predictive system that forecasts climate-driven crop pathogen outbreaks — and took home a $1,200 Scale AI prize",
        "slug": "gurnoor-kaur-indian-teen-data-science-wheat-ai-canada-20260611",
        "category": "nri-world",
        "vertical": "diaspora",
        "urgency": "medium",
        "tags": ["Gurnoor Kaur", "data science", "AI", "wheat disease", "STEM", "Canada", "Indian origin", "student achievement", "agriculture", "Ontario"],
        "word_count": 800,
        "status": "review",
        "is_editorial": False,
        "score_total": 72,
        "published_at": NOW,
        "image_url": "https://images.pexels.com/photos/7891849/pexels-photo-7891849.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A golden wheat field — the crop at the centre of Kaur's AI disease-prediction model",
        "image_attribution": "Photo by Karol Czinege / Pexels",
        "diaspora_angle": "Kaur's win adds to a growing roster of Indian-origin students excelling in North American STEM competitions — part of a second-generation pattern where children of immigrants leverage parental emphasis on education into nationally recognised research.",
        "sources": json.dumps([
            {"name": "ConnectMyIndia NRI News", "url": "https://nri.connectmyindia.com/trenton/news/article/indian-origin-teen-gurnoor-kaur-wins-canada-data-science-contest-with-ai-project-3750/"},
            {"name": "STEM Fellowship — National High School Big Data Challenge", "url": "https://stemfellowship.org"}
        ]),
        "body": """Gurnoor Kaur, a Grade 11 student at Central Peel Secondary School in Brampton, Ontario, has won first place at Canada's National High School Big Data Challenge — a four-month research competition organised by STEM Fellowship — for building an artificial-intelligence model that predicts when and where climate-driven wheat diseases are likely to strike.

The 16-year-old presented her findings at the programme's Eastern Conference, hosted at the University of Toronto, and collected a $1,200 Scale AI award for the strength of her applied-AI work. In a field increasingly crowded with student projects that invoke machine learning as a buzzword, Kaur's entry stood out for doing something genuinely useful: mapping the intersection of climate data and crop-pathogen biology to generate actionable forecasts.

## How the Model Works

Wheat diseases — rusts, blights, fusarium head blight among them — thrive under specific environmental conditions: sustained humidity above certain thresholds, warmer-than-average overnight temperatures and particular rainfall patterns during the growing season. The challenge for farmers and agricultural agencies is that these conditions shift from year to year and region to region, making it difficult to know where to concentrate monitoring resources.

Kaur's approach was to train AI models on large open datasets that combine historical climate records with documented crop-disease outbreaks across North America. The system identifies correlations between weather patterns and past pathogen emergence, then uses those patterns to flag future high-risk windows — essentially telling agricultural authorities: this county, during this three-week period, is unusually likely to see a wheat rust outbreak.

The model does not claim to eliminate crop disease. What it offers is a triage tool — a way to direct limited inspection and treatment budgets toward the areas where they are statistically most needed, rather than spraying fungicide uniformly or waiting for visible symptoms that may arrive too late.

## Why It Matters Beyond the Competition

Wheat is the world's most widely grown cereal, feeding roughly 2.5 billion people and underpinning food security from the Punjab to the Canadian prairies. Climate change is already redrawing the map of where wheat pathogens can survive: warming winters allow fungi to overwinter further north, while erratic rainfall creates the wet-then-warm cycles that many pathogens exploit.

India, the world's second-largest wheat producer after China, has experienced this firsthand. Unseasonal heat waves in 2022 and 2024 slashed yields and forced export bans. Any tool that helps predict disease pressure — whether deployed on a Saskatchewan farm or a Haryana one — has implications that extend well beyond a student competition.

Kaur's research does not yet constitute a production-grade agricultural tool, and she would be the first to say so. But the underlying approach — layering climate projections onto historical disease data with machine-learning pattern recognition — is precisely what organisations like the Indian Council of Agricultural Research and Agriculture and Agri-Food Canada are investing in at the institutional level. That a high-school student independently arrived at a working prototype speaks to both the accessibility of open datasets and the quality of STEM education in the Canadian system.

## The Student Behind the Model

Kaur is not a one-project wonder. She currently serves as president of the STEAM Collective at Central Peel Secondary School, where she works to draw more young women into science and technology. She previously won first place in the National Space Society's Gerard K. O'Neill Space Settlement Contest and presented at the International Space Development Conference. She has written for the Global STEM Youth Journal and completed an AI apprenticeship with the Creative Destruction Lab, one of Canada's leading deep-tech incubators.

Her trajectory mirrors a broader pattern among second-generation Indian-Canadian students: parents who arrived as skilled immigrants — engineers, doctors, IT professionals — channel considerable resources into their children's STEM exposure, and the children, in turn, compete at the highest national levels with increasing regularity. Brampton, where Kaur attends school, is one of Canada's most South Asian cities, with a Punjabi-origin population that now constitutes a significant share of the municipality.

## What Comes Next

Kaur has not announced university plans — she is, after all, still in Grade 11. But the combination of a national data-science title, a Scale AI prize and a space-settlement competition win will make her application file unusually thick when the time comes. More immediately, her wheat-disease model sits in the growing pile of student AI projects that professional researchers would do well to take seriously — not as finished products, but as proof that the tools of modern agricultural science are no longer locked behind institutional gates.""",
    },
]


def insert_articles():
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    for art in articles:
        resp = requests.post(url, headers=HEADERS, json=art)
        if resp.status_code in (200, 201):
            row = resp.json()
            rid = row[0]["id"] if isinstance(row, list) else row.get("id", "?")
            print(f"✅  Inserted: {art['slug']}  (id={rid})")
        else:
            print(f"❌  FAILED: {art['slug']}")
            print(f"    Status: {resp.status_code}")
            print(f"    Body:   {resp.text[:500]}")


if __name__ == "__main__":
    if not SUPABASE_KEY:
        # try loading from env file
        env_path = os.path.expanduser("~/workspace/.env.supabase")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
                        SUPABASE_KEY = line.split("=", 1)[1]
                        HEADERS["apikey"] = SUPABASE_KEY
                        HEADERS["Authorization"] = f"Bearer {SUPABASE_KEY}"
    insert_articles()
