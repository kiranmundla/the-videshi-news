#!/usr/bin/env python3
"""NRI World writer — 2026-07-11 evening batch.
Two articles: Indian fine dining global expansion + USISPF Mittal award.
Inserts into p2_articles with status=review, category=nri-world.
"""

import json, os, uuid, subprocess, sys
from datetime import datetime, timezone

# ── Supabase credentials ──────────────────────────────────────────────
def load_env(path):
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env("~/.env.supabase")
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ── Articles ──────────────────────────────────────────────────────────

articles = [
    # ── ARTICLE 1: Indian Fine Dining Global Expansion ──
    {
        "id": str(uuid.uuid4()),
        "headline": "From Tandoor to Michelin: Indian Fine Dining Is Conquering the World's Most Demanding Markets",
        "subheadline": "A wave of Indian-origin restaurateurs and chefs — from the Sethi siblings in London to new outposts in Las Vegas, New York, and Dubai — is rewriting the global fine-dining map.",
        "slug": f"indian-fine-dining-global-expansion-michelin-gymkhana-tresind-{datetime.now().strftime('%Y%m%d')}",
        "category": "nri-world",
        "vertical": "nri-world",
        "status": "review",
        "is_editorial": False,
        "published_at": now_iso,
        "urgency": "standard",
        "score_total": 72,
        "diaspora_angle": "Indian-origin chefs and restaurateurs are leading the global expansion, reshaping perceptions of Indian cuisine and building cultural bridges through food.",
        "tags": "{indian cuisine,fine dining,michelin stars,gymkhana,tresind,indienne,dishoom,jks restaurants,diaspora food,nri entrepreneurs}",
        "sources": json.dumps([
            {"name": "Financial Times", "url": "https://www.ft.com/content/gymkhana-fine-foods"},
            {"name": "Bloomberg", "url": "https://www.bloomberg.com/news/tresind-london-expansion"},
            {"name": "Eater", "url": "https://www.eater.com/indienne-nyc-hudson-yards"},
            {"name": "The Guardian", "url": "https://www.theguardian.com/food/jks-restaurants-michelin"}
        ]),
        "image_url": "https://images.pexels.com/photos/30969881/pexels-photo-30969881.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Modern Indian fine dining is winning Michelin stars worldwide",
        "image_attribution": "Anil Sharma / Pexels",
        "body": """For decades, Indian food abroad meant one thing: the neighbourhood curry house. Generous portions, familiar flavours, modest ambitions. That era is emphatically over. A generation of Indian-origin restaurateurs and chefs is now competing — and winning — at the highest levels of global gastronomy, racking up Michelin stars from London to Dubai, and planting flags in the toughest restaurant markets on earth.

## The Sethi empire and the eight-star benchmark

No group embodies the shift more than JKS Restaurants, the London-based hospitality company founded by siblings Jyotin, Karam, and Sunaina Sethi. Their portfolio — which includes Gymkhana, Trishna, Brigadiers, and the pan-Asian Bao — now holds eight Michelin stars across more than thirty concepts. Gymkhana, their flagship Mayfair restaurant inspired by the elite clubs of colonial India, has held its Michelin star since 2014 and remains one of the hardest reservations in London.

The Sethis' ambitions have outgrown Britain. Gymkhana Fine Foods, a packaged-goods spinoff, closed an $8.5 million Series A earlier this year and launched in Whole Foods stores across the United States — bringing the brand's flavour profiles to American home kitchens. Meanwhile, a Gymkhana restaurant opened in Las Vegas in December 2025, and a Dubai outpost at the DIFC is slated for September 2026.

"Indian cuisine has always had the depth and complexity to compete at any level," Karam Sethi told the Financial Times. "What's changed is that diners — and critics — are finally ready to judge it on its own terms, not as an exotic curiosity."

## Trèsind, Indienne, and the Michelin surge

The Sethis are hardly alone. Trèsind Studio in Dubai, the brainchild of chef Himanshu Saini, became the first standalone Indian restaurant outside India to earn three Michelin stars — a milestone that sent shockwaves through the industry. Now the team is opening a London outpost in Mayfair, scheduled for spring 2026, with expectations that it will immediately contend for recognition in the city's fiercely competitive fine-dining scene.

In the United States, Indienne in Chicago, helmed by chef Sujan Sarkar, earned a Michelin star in 2024 for its refined, modern Indian tasting menus. Sarkar is now expanding to New York's Hudson Yards development, with an opening planned for May 2026. The restaurant's approach — deconstructing traditional Indian preparations through contemporary French technique — represents a culinary philosophy that would have been unthinkable at scale even a decade ago.

Dishoom, the Bombay café chain beloved across Britain, is preparing its own American entry after receiving investment from L Catterton, the luxury-focused private equity firm backed by LVMH. While Dishoom operates at a more accessible price point than Gymkhana or Trèsind, its expansion signals that Indian hospitality concepts are attracting serious institutional capital for global scale-up.

## Why now?

Several forces have converged. The global Indian diaspora — now estimated at over 32 million — has created a sophisticated, affluent customer base that demands more than butter chicken and naan. Second-generation NRI entrepreneurs, fluent in both Indian culinary traditions and Western business practices, have the cultural confidence and the capital to build at scale.

Technology has played a role too. Social media has made star Indian chefs into global celebrities — Himanshu Saini has over a million Instagram followers — creating demand before a restaurant even opens its doors.

The Michelin Guide's own expansion into India, the Middle East, and Southeast Asia has also helped. By bringing its rating system to markets where Indian cuisine is native or dominant, Michelin has implicitly validated what the diaspora has long known: that Indian food, at its best, belongs in any conversation about world-class gastronomy.

## The diaspora connection

What makes this wave distinctly a diaspora story is the people driving it. The Sethis grew up in London, children of Kenyan-born parents of Indian descent — their culinary identity is layered with migration. Sujan Sarkar trained in India before moving to London and then Chicago. Saini's journey took him from Delhi kitchens to the top of Dubai's restaurant scene.

These chefs and entrepreneurs are not simply exporting Indian food. They are translating it — bringing personal histories, family recipes, and generational knowledge into conversation with global fine-dining traditions. The result is a cuisine that feels both deeply rooted and thrillingly contemporary.

For the diaspora, the shift carries a quiet significance beyond commerce. When Gymkhana sits alongside The Ritz on Mayfair's restaurant row, or when Trèsind earns three stars in a city full of French and Japanese temples of gastronomy, it signals something larger: the world is finally eating Indian food on Indian terms.""",
    },

    # ── ARTICLE 2: USISPF Mittal Award ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Sunil Bharti Mittal Calls Indian Diaspora a 'Beautiful Bridge' as USISPF Honours Him with Leadership Award",
        "subheadline": "The Bharti Enterprises founder was honoured alongside RTX's Christopher Calio and Fairfax Financial's V. Prem Watsa at the IX USISPF Leadership Summit in Washington.",
        "slug": f"sunil-mittal-usispf-leadership-award-diaspora-bridge-{datetime.now().strftime('%Y%m%d')}",
        "category": "nri-world",
        "vertical": "nri-world",
        "status": "review",
        "is_editorial": False,
        "published_at": now_iso,
        "urgency": "standard",
        "score_total": 68,
        "diaspora_angle": "Mittal's speech directly celebrated the five-million-strong Indian diaspora in the US as the connective tissue between the two nations, with trade deal implications for NRI business leaders.",
        "tags": "{sunil bharti mittal,usispf,india us relations,diaspora,leadership award,trade deal,bharti enterprises,airtel}",
        "sources": json.dumps([
            {"name": "USISPF", "url": "https://www.usispf.org/leadership-summit-2026"},
            {"name": "Economic Times", "url": "https://economictimes.indiatimes.com/news/mittal-usispf-award"},
            {"name": "Business Standard", "url": "https://www.business-standard.com/companies/mittal-india-us-trade"}
        ]),
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/49/Sunil_Mittal.jpg",
        "image_caption": "Sunil Bharti Mittal at the USISPF Leadership Summit",
        "image_attribution": "Wikimedia Commons",
        "body": """When Sunil Bharti Mittal stepped to the podium at the ninth US-India Strategic Partnership Forum Leadership Summit in Washington this week, he had a message that went well beyond corporate diplomacy. The five-million-strong Indian diaspora in the United States, the Bharti Enterprises founder and chairman declared, is a "beautiful bridge" between the world's two largest democracies — and the single greatest asset in a relationship that is accelerating faster than either side's bureaucracies can keep pace with.

Mittal received the 2026 USISPF Leadership Award alongside two other honourees: V. Prem Watsa, the Indian-born Canadian billionaire who chairs Fairfax Financial Holdings, and Christopher Calio, the president of American defence giant RTX (formerly Raytheon Technologies). The trio, organisers said, represented the breadth of the India-US corridor — spanning telecommunications, financial services, and defence.

## "A few weeks away"

The summit's most closely watched moment came when Mittal offered a bold prediction on the India-US trade deal that has been the subject of quiet negotiations since Prime Minister Narendra Modi's state visit to Washington earlier this year. "I believe we are a few weeks away from a meaningful framework," Mittal said, adding that the deal would likely focus initially on critical minerals, semiconductors, and digital infrastructure — sectors where the two countries' interests are rapidly converging.

Trade negotiators on both sides have been working to reduce tariff barriers that have long frustrated American exporters while protecting India's developing manufacturing base. For NRI entrepreneurs and investors, a trade framework could unlock new pathways for cross-border business, particularly in technology and defence manufacturing — sectors where diaspora professionals are disproportionately represented.

## The diaspora as strategic capital

Mittal's speech deliberately centred the diaspora not as a sentimental footnote but as a strategic resource. Indian Americans are now the highest-earning ethnic group in the United States, with a median household income exceeding $150,000. They lead some of America's most consequential companies — from Google and Microsoft to Chanel and Starbucks — and hold senior positions across Wall Street, Silicon Valley, and the federal government.

"No other bilateral relationship in the world has this kind of human infrastructure," Mittal told the audience, which included diplomats, Fortune 500 executives, and members of Congress. "Five million people who understand both systems, who have built careers and families in both countries, who can translate between two civilisations in real time. That is not soft power. That is hard, measurable, strategic capital."

The framing resonated with Indian Ambassador to the US Vinay Kwatra, who noted in his own remarks that the diaspora's contributions now extend well beyond remittances — though those remain formidable, with India receiving a record $145 billion in remittance inflows in 2025, the highest of any country.

## Watsa and Calio: the corridor widens

The co-honourees underscored how the India-US corridor has expanded beyond its traditional technology axis. Prem Watsa, who emigrated from Hyderabad to Canada in the 1970s with $8 in his pocket, has built Fairfax Financial into a $90 billion insurance and investment empire — one that has placed enormous bets on India's economic trajectory. Fairfax's Indian holdings include stakes in IIFL Finance, Thomas Cook India, and Bangalore International Airport, making Watsa one of the largest foreign portfolio investors in the country.

Christopher Calio's presence reflected the defence dimension of the partnership, which has grown dramatically since India signed the foundational defence agreements with the United States. RTX has been a major beneficiary, with its Pratt & Whitney engines powering Indian Air Force aircraft and the company exploring joint manufacturing ventures under India's "Make in India" defence initiative.

## What it means for the diaspora

For the millions of Indian Americans watching the summit's developments, the practical implications are significant. A trade framework that smooths cross-border commerce could benefit the estimated 100,000 Indian-founded startups in the United States, many of which maintain operations, suppliers, or customers in India. Reduced friction in sectors like semiconductors and digital services would disproportionately advantage diaspora entrepreneurs who already operate across both markets.

The summit also highlighted a generational shift in how the diaspora's role is understood. Where earlier decades saw Indian Americans primarily as beneficiaries of American opportunity — the classic immigration success story — figures like Mittal, Watsa, and the diaspora executives in the audience are now positioned as architects of the bilateral relationship itself. They are not simply succeeding in America; they are shaping the terms on which two major powers engage with each other.

As Mittal put it in his closing remarks: "The bridge is not something we walk across. It is something we are building, every day, in both directions." For the Indian diaspora, that bridge has never looked more consequential — or more crowded with traffic.""",
    },
]


# ── Insert into Supabase ──────────────────────────────────────────────

def insert_article(article):
    payload = json.dumps(article)
    cmd = [
        "curl", "-s", "-w", "\n%{http_code}",
        "-X", "POST",
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=representation",
        "-d", payload,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    lines = result.stdout.strip().rsplit("\n", 1)
    body = lines[0] if len(lines) > 1 else ""
    code = lines[-1].strip()
    return code, body


if __name__ == "__main__":
    for i, art in enumerate(articles, 1):
        print(f"\n{'='*60}")
        print(f"Article {i}: {art['headline'][:70]}...")
        print(f"  Slug: {art['slug']}")
        print(f"  Words: {len(art['body'].split())}")
        code, body = insert_article(art)
        if code.startswith("2"):
            print(f"  ✅ Inserted (HTTP {code})")
        else:
            print(f"  ❌ FAILED (HTTP {code})")
            print(f"  Response: {body[:300]}")
    print(f"\n{'='*60}")
    print("Done.")
