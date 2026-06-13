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
        "headline": "India's Sports Ministry Has Sent a 'Sports Passport' Proposal to the PM's Office. For Diaspora Athletes, It Changes Everything.",
        "subheadline": "If approved, the framework could let PIO and OCI athletes represent India in international competition without surrendering foreign citizenship — a first in Indian sports history, and a potential game-changer ahead of the 2036 Olympics bid.",
        "slug": make_slug("india-sports-passport-proposal-pmo-pio-oci-diaspora-athletes"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Millions of Indian-origin athletes who grew up playing football, tennis, and basketball in the US, UK, Canada, and Australia have been legally barred from representing India. The Sports Passport proposal directly addresses the diaspora's exclusion from Indian national teams.",
        "tags": ["nri", "diaspora", "sports", "oci", "pio", "football", "olympics", "india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Khel Now", "url": "https://khelnow.com/football/sports-ministry-sends-sports-passport-proposal-to-pm-modi-office"},
            {"name": "RevSportz", "url": "https://revsportz.in/sports-passport-proposal-could-open-new-era-for-indian-sports/"},
            {"name": "India Sports Hub", "url": "https://indiasportshub.com/leveraging-the-diaspora-why-an-india-overseas-xi-could-transform-indian-football/"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/47/India_vs_Pakistan%2C_2018_SAFF_Championship.png",
        "image_caption": "India's national football team in action during the 2018 SAFF Championship",
        "image_attribution": "Wikimedia Commons",
        "body": """For decades, a single bureaucratic fact has kept some of the most talented athletes of Indian heritage off India's national teams: you cannot represent the country unless you hold an Indian passport. No exceptions. No workarounds. No matter how many goals you score for Bayern Munich's reserves or how deep your family's roots in Punjab run.

That may be about to change. In an exclusive report by Khel Now on June 12, the Ministry of Youth Affairs and Sports has formally submitted a "Sports Passport" proposal to the Prime Minister's Office and the Ministry of Home Affairs. If approved, it would create a legal pathway for Persons of Indian Origin and Overseas Citizens of India to represent India in international sports competitions — without requiring them to renounce their foreign citizenship first.

The proposal is still at an early stage. Sources indicate the government could take six to eight months to arrive at a decision. But the fact that it has reached the PMO at all represents a tectonic shift in Indian sports policy, and for the 35-million-strong global Indian diaspora, the implications are enormous.

## The wall that kept talent out

India's Citizenship Act of 1955 enforces single citizenship. Anyone who voluntarily acquires another country's passport automatically ceases to be Indian. A 2008 circular from the Ministry of Youth Affairs and Sports went further, mandating that only holders of a valid Indian passport could represent the country in international competition.

The result has been a slow, visible bleed of diaspora talent to other flags. Sarpreet Singh, born to Punjabi parents in New Zealand, became the first player of Indian descent to play in the Bundesliga — for Bayern Munich. He represents New Zealand. Samuel Moutoussamy, of Indian heritage, plays for DR Congo. Tahsin Jamshid represents Qatar. Danny Batth, Adrian Pereira, Yan Dhanda — all players with Indian roots who built careers in European football leagues that India could never access.

The most dramatic recent case was Ryan Williams, an Australian-born footballer who gave up his Australian citizenship entirely to play for India. It worked, but the sacrifice was extreme. Most athletes — established in their careers, with families and livelihoods built abroad — are not willing to make that trade.

## Why now

Two forces are converging. First, India is preparing a bid for the 2036 Olympics, and the government knows that its medal counts and team sport performances need dramatic improvement if the bid is to be credible. Second, India's football ranking has stagnated in the 130s despite the visibility boost from the Indian Super League, and officials have watched with growing frustration as Indian-origin talent thrives elsewhere.

The Khelo Bharat Niti — India's new National Sports Policy unveiled in July 2025 — already signalled the shift, stating that "promising and prominent Indian-origin athletes living abroad may be encouraged to come back and play for India at the international level." The Sports Passport proposal operationalises that language into a formal framework.

## What it could look like

Details remain sparse. The proposal would need to define eligibility criteria — how many generations back, which sports, what residency or training requirements — and navigate FIFA, the IOC, and individual sport federations' own nationality rules. Countries like Qatar, Bahrain, Turkey, and Spain already use fast-track citizenship or special eligibility pathways to strengthen their national teams, so there are models to draw from.

For NRI families in the US, UK, Canada, and Australia, the implications go beyond elite sport. Weekend football leagues, tennis academies, and basketball camps across diaspora communities have produced a generation of kids who are technically and tactically far ahead of their peers in India's domestic system. The Sports Passport could give those young athletes a reason to look eastward — and give India's national teams a talent pipeline they have never had.

## The bigger picture

The proposal sits within a broader pattern of India recalibrating its relationship with its diaspora. OCI card reforms, the Bihar global diaspora portal, the sixth-generation OCI extension for Trinidad and Tobago's Indian community — all signal a government that increasingly sees its overseas population as a strategic asset rather than a bureaucratic complication.

Whether the Sports Passport survives the PMO's review and the Home Ministry's scrutiny is another matter. But the conversation has formally begun, and for millions of Indian-origin athletes who grew up dreaming of wearing the Blue Tigers jersey but never had a legal path to it, that alone is a milestone."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Three Decades at MIT Press, and Now She Runs Columbia's. Meet Gita Manaktala.",
        "subheadline": "Columbia University has appointed the Indian American publishing leader as Executive Director of one of the nation's oldest and most respected university presses — a quiet milestone in a field where South Asian representation at the top remains rare.",
        "slug": make_slug("gita-manaktala-columbia-university-press-indian-american"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Manaktala's appointment adds to the growing but still thin ranks of Indian Americans leading major American academic and cultural institutions — a quieter form of diaspora achievement than tech CEO headlines, but one that shapes what knowledge gets published, who gets heard, and which ideas reach global audiences.",
        "tags": ["nri", "diaspora", "academia", "publishing", "columbia", "indian-american"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Columbia University Press", "url": "https://cup.columbia.edu/"},
            {"name": "American Bazaar", "url": "https://americanbazaaronline.com/2026/06/11/manaktala-named-executive-director-columbia-university-press/"},
            {"name": "Publishers Lunch", "url": "https://lunch.publishersmarketplace.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Columbia_University_New_York_November_2016_002.jpg/1280px-Columbia_University_New_York_November_2016_002.jpg",
        "image_caption": "Columbia University's Morningside Heights campus in New York City",
        "image_attribution": "Wikimedia Commons",
        "body": """When the Indian diaspora's achievements in America make headlines, the stories tend to follow a familiar script: tech CEO appointed, startup unicorn founded, medical breakthrough led. The narrative favours scale, speed, and spectacle. It rarely pauses for the kind of institution-building that happens in quieter rooms — the ones where decisions about which ideas get published, which scholarship reaches the world, and whose voices shape intellectual life are made every day.

Gita Manaktala's appointment as Executive Director of Columbia University Press, announced this week, is that kind of story. It will not trend. It should.

## Thirty years of building

Manaktala joins Columbia after more than three decades at MIT Press, where she helped transform one of the world's leading academic publishers from the inside. She started as an acquiring editor and rose to editorial director, overseeing the expansion of the Press's publishing programme from roughly 200 to 300 titles annually. She pioneered digital publishing and open-access initiatives at a time when most university presses were still debating whether e-books would last. She strengthened relationships with scholarly communities across disciplines, and she served on the board of directors of the Association of University Presses.

In a field where the path to the top often runs through editorial instinct, institutional knowledge, and the slow accumulation of trust, Manaktala's career reads like a masterclass. Her appointment at Columbia, following a national search, places her at the helm of one of the oldest university presses in the United States — founded in 1893, with a catalogue spanning the humanities, social sciences, and sciences.

"Gita is an accomplished publishing leader whose career has been defined by intellectual curiosity, editorial excellence, and a deep commitment to expanding access to knowledge," said Angela V. Olinto, Columbia's Provost. "I am confident that she will build on Columbia University Press's extraordinary legacy and help shape its future with creativity, ambition, and purpose."

Manaktala will assume her role on September 8, 2026, succeeding Jennifer Crewe, who led the Press for over a decade.

## Why this matters beyond the campus

University presses occupy a peculiar position in the knowledge economy. They are too small to attract the attention that commercial publishers or tech platforms command, but their influence on what gets researched, debated, and taught is disproportionate. A university press decides which first-time scholars get a book contract, which interdisciplinary experiments get backed, and which ideas cross from academic journals into public discourse.

For the Indian diaspora, the appointment carries a significance that goes beyond personal achievement. South Asian Americans have reached the top of technology companies, financial institutions, and medical centres. But their presence in the leadership of America's cultural and intellectual institutions — museums, foundations, publishing houses, libraries — remains notably thin. Manaktala's appointment chips away at that gap.

Her own words at the announcement suggested she sees the role in those terms. "At a time when the world faces complex social, scientific, technological, and political questions, university presses play a vital role in bringing rigorous research into the public conversation," she said. "I look forward to working with the Press's talented staff, authors, faculty partners, and supporters to champion exceptional scholarship and bring it to wider audiences around the globe."

## The open-access question

Manaktala inherits Columbia University Press at a moment of significant tension in academic publishing. The open-access movement — which argues that publicly funded research should be freely available to anyone — has accelerated rapidly. Traditional university presses, which rely on book sales and institutional subscriptions, are being forced to rethink their business models. Manaktala's experience at MIT Press, which was among the earliest to experiment with open-access monographs and digital-first publishing, positions her well for this transition.

Columbia's announcement also came with an unusual footnote: the Press recently submitted contact information for all its authors listed in the Anthropic copyright settlement, a reminder that the intersection of AI and academic publishing is no longer theoretical.

## A quieter kind of milestone

The Indian American community now counts 16 Fortune 500 CEOs of Indian origin, 72 unicorn co-founders, and a growing bench of elected officials at every level of government. These are important markers. But the full measure of a diaspora's integration into its adopted country includes the less visible positions of influence — the ones that determine what stories get told, what research gets funded, and what ideas shape the next generation.

Gita Manaktala's career has been spent doing exactly that work, one book at a time. At Columbia, she will do it on a larger stage."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
