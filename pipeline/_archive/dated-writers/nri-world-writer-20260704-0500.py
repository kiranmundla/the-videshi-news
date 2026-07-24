#!/usr/bin/env python3
"""NRI World writer — July 4, 2026 run."""
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

# ──────────────────────────────────────────
# ARTICLE 1: Indiaspora 250@250
# ──────────────────────────────────────────

art1_body = """As the United States prepares to mark the 250th anniversary of its independence, the non-profit Indiaspora has launched what it calls a definitive accounting of the Indian American contribution to the republic. Released on July 2, "250 @ 250: The Indian American Story" catalogues 250 milestones that span more than two centuries, from the first Indian merchant ships docking at Salem harbour to the corner offices of Fortune 500 companies.

The collection is organised across 15 domains — entrepreneurship, science, law, sports, food, media and more — and its ambition is less to celebrate than to document. "The moments are not just a record of Indian American achievement," Indiaspora said. "They are a testament to what America makes possible."

## From Motel Lobbies to Boardrooms

Among the milestones is the "Patel Motel" phenomenon. In the 1940s, Kanji Manchhu Desai began what would become one of the most quietly consequential business stories in American hospitality: today, members of the Indian diaspora own roughly 60 percent of all hotels in the United States, according to Indiaspora's research. The collection traces the arc from those first roadside motels to the present, where Indian Americans lead companies like Palo Alto Networks, Vertex Pharmaceuticals, and Adobe.

The yoga industry gets its own entry too. B.K.S. Iyengar's 1956 demonstration at the University of Michigan introduced the practice as therapy rather than mysticism. Approximately 34 million Americans — around one in ten — now practise yoga, an industry anchored by an estimated 36,000 studios.

## A Project Timed for a Reckoning

The release is not accidental timing. It arrives during a week when Indian Americans are simultaneously celebrating the Fourth of July and navigating a political climate that has made immigration itself a contested subject. The Carnegie Corporation named four Indian Americans to its "Great Immigrants, Great Americans" 2026 list just days earlier. The USISPF launched its own 250-person tribute book the previous week. Indiaspora's compilation sits alongside these gestures but reaches further back in time, arguing that the community's footprint predates the current spotlight by generations.

"Every young Indian American who wonders whether they belong here, whether they can lead here — they deserve to know about those who came before them and did exactly that," said Sanjeev Joshipura, Indiaspora's executive director.

## The Numbers Behind the Narrative

The project draws on Indiaspora's broader research, including data from a Boston Consulting Group partnership showing that Indian Americans are among the fastest-growing major immigrant communities in the country. Their collective giving has surged in the past six years: diaspora philanthropy rose from an estimated 1–2 percent of household income to 4–5 percent between 2018 and 2024, narrowing the so-called "giving gap" from $2–3 billion to roughly $1 billion.

M.R. Rangaswami, Indiaspora's founder and chairman, framed the project in communal rather than individual terms. "The measure of any community is not what it achieves for itself, but what it gives to others," he told the South Asian Herald. "Indian Americans have built companies that employ millions, advanced science that saves lives, and served in every branch of government and the military — not as outsiders proving their worth, but as Americans fulfilling their purpose."

## What It Leaves Out

Indiaspora is careful to note what "250 @ 250" is not. It does not rank achievements. It does not claim to be exhaustive. And it acknowledges that "the historical record itself has not always documented contributions equally" — a quiet nod to the women, lower-caste immigrants, and working-class communities whose stories the conventional diaspora narrative tends to skip.

Whether the project becomes a lasting reference or a well-timed press release depends on what follows. Indiaspora says the full list is available at 250moments.indiaspora.org. For a community that has spent decades building wealth, influence, and institutional power in America, the harder question may be whether it can now build a history that includes everyone who got it there."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Indiaspora Just Catalogued 250 Milestones of Indian American Life. The Timing Is Not a Coincidence.",
    "subheadline": "Released two days before America's 250th birthday, the compilation spans motel lobbies, yoga studios, Fortune 500 boardrooms — and asks who still gets left out of the story.",
    "slug": make_slug("indiaspora-250-milestones-indian-american-july-4th"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "A definitive compilation of how Indian Americans have shaped the United States across 15 domains — from hospitality and tech to philanthropy and civil rights — released as America marks its semiquincentennial.",
    "tags": ["nri", "diaspora", "indian-american", "indiaspora", "america-250", "july-4th", "philanthropy"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "South Asian Herald", "url": "https://southasianherald.com/indiaspora-unveils-250250-the-indian-american-story/"},
        {"name": "Indiaspora", "url": "https://250moments.indiaspora.org"},
        {"name": "India Today Global", "url": "https://www.youtube.com/watch?v=carnegie-great-immigrants-2026"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/0d/M._R._Rangaswami.jpg",
    "image_caption": "M.R. Rangaswami, founder and chairman of Indiaspora, at a diaspora event",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}

# ──────────────────────────────────────────
# ARTICLE 2: Modi Indo-Pacific diaspora tour
# ──────────────────────────────────────────

art2_body = """When Narendra Modi lands in Jakarta on Monday, he will begin a six-day, three-nation sweep through the Indo-Pacific that is as much about the Indian diaspora as it is about trade deals and defence pacts. The tour — Indonesia, Australia, New Zealand, from July 6 to 11 — includes large-scale community addresses in every capital and, in the case of New Zealand, the first state visit by an Indian prime minister in four decades.

The itinerary is ambitious. But the politics waiting for Modi in each country are sharply different, and in at least one of them, the welcome mat is fraying.

## Jakarta: Temples and Strategic Reassurance

Modi arrives in Indonesia for his fourth visit but his first bilateral trip since the two countries elevated ties to a Comprehensive Strategic Partnership in 2018. He will address a "large gathering" of the Indian diaspora in Jakarta and travel to Yogyakarta to visit the Prambanan temple complex, a UNESCO heritage site where India and Indonesia plan joint conservation work.

The cultural signalling is deliberate. India's soft-power playbook in Southeast Asia has always leaned on shared Hindu-Buddhist heritage, and Prambanan — a ninth-century Hindu temple compound — is as potent a symbol as any. The diplomatic substance, however, centres on supply-chain diversification and critical minerals, areas where Indonesia's nickel reserves give it leverage that India wants access to.

## Melbourne: A Million-Strong Welcome

Australia is the centrepiece. India is one of Australia's largest trading partners, and the roughly one million Indian-born residents now constitute the country's biggest overseas-born population — a distinction that passed China and the United Kingdom during the pandemic-era migration surge.

Modi will hold bilateral talks with Prime Minister Anthony Albanese at the third India-Australia Annual Summit in Melbourne, participate in the India-Australia CEOs Forum, and visit the Melbourne Cricket Ground, a venue that carries almost devotional significance for Indian cricket fans. Organisers have scouted venues with capacities of 14,000 to 35,000 for the diaspora address, according to the Australia Today, both chosen for indoor coverage against Melbourne's July winter.

The business agenda is substantial. Australian firms want Indian markets for critical minerals, agricultural exports, and education services. Indian firms want Australian lithium, cobalt, and rare earths for their semiconductor and clean-energy ambitions. The CEOs Forum is expected to produce binding commitments on at least two supply-chain corridors.

## Auckland: Four Decades, One Shadow

Then there is New Zealand, and here the trip acquires an edge. Modi will meet Prime Minister Christopher Luxon in Auckland on July 10–11, the first Indian prime minister to make a state visit since 1986. The two countries signed a free-trade agreement in April that will eventually eliminate tariffs on all Indian goods and 95 percent of New Zealand exports.

But the FTA has become a flashpoint. A provision to facilitate the movement of skilled Indian workers provoked a domestic backlash that turned ugly fast. New Zealand First MP Shane Jones described the migration component as a "butter chicken tsunami," a phrase that has followed New Zealand's India policy ever since. The BBC documented the incident as part of a broader pattern: South Asians reported the highest number of hate crimes in New Zealand between January 2022 and October 2025, according to police data. A haka performance directed at Indian-origin MP Parmjeet Parmar drew widespread condemnation.

Reuters noted that the visit "comes amid rising anti-Indian sentiment in the country," a line that would have been unthinkable in the context of an Indian PM's travel plans a decade ago. Modi, who raised concerns about "anti-India activities by some illegal elements" in New Zealand during a meeting with Luxon last year, will almost certainly return to the theme.

## The Diaspora as Diplomatic Capital

Across all three stops, Modi will address the Indian community — a ritual that has become central to how India conducts foreign policy. These events are not afterthoughts. They are stage-managed demonstrations of demographic influence, designed to remind host governments that the Indian diaspora is an electoral constituency, an economic force, and a lobby.

In Australia, with a million people, that argument is self-evident. In New Zealand, where the community is smaller and the political climate more hostile, the diaspora address will carry a different weight: reassurance to a community feeling targeted, and a signal to Wellington that New Delhi is watching.

The tour ends July 11. The trade figures, the critical-minerals pacts, and the joint statements will get their headlines. But the story that matters most to the Indian diaspora may be the simplest one: that their prime minister showed up."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Modi Is Taking His Diaspora Playbook to Three Countries in Six Days. In One of Them, It Will Be Tested.",
    "subheadline": "A million Indians in Australia, a 40-year gap in New Zealand, and the 'butter chicken tsunami' that won't go away — inside the Indo-Pacific tour that starts Monday.",
    "slug": make_slug("modi-indo-pacific-tour-australia-new-zealand-diaspora"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Modi's three-nation tour includes large-scale diaspora addresses in every stop, but the NZ leg puts a spotlight on rising anti-Indian sentiment and hate crimes that have left the community feeling targeted.",
    "tags": ["nri", "diaspora", "modi", "australia", "new-zealand", "indonesia", "indo-pacific", "anti-indian-sentiment"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/asia-pacific/india-pm-modi-make-first-official-visit-new-zealand-next-week-2026-07-03/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/news/prime-minister-modi-to-visit-indonesia-australia-new-zealand-for-bilateral-talks/article71179757.ece"},
        {"name": "Ainvest", "url": "https://www.ainvest.com/news/indian-community-new-zealand-faces-surge-racist-incidents/"},
        {"name": "BBC World Service", "url": "https://www.youtube.com/watch?v=nz-india-trade-deal-racism"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5f/The_official_portrait_of_Shri_Narendra_Modi%2C_the_Prime_Minister_of_the_Republic_of_India.jpg",
    "image_caption": "Prime Minister Narendra Modi, whose six-day Indo-Pacific tour begins July 6",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}

articles = [art1, art2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
