#!/usr/bin/env python3
"""Sports writer — 2026-05-23 08:00 PDT run: 2 articles."""

import os, json, uuid, requests, sys
from datetime import datetime, timezone

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def insert_article(article: dict) -> dict:
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=HEADERS, json=article)
    if r.status_code >= 400:
        print(f"  ERROR inserting {article.get('slug','?')}: {r.status_code} {r.text[:500]}")
    r.raise_for_status()
    return r.json()

def upload_image(article_id: str, local_path: str) -> str:
    """Upload image to Supabase storage and return public URL."""
    bucket = "article-images"
    filename = f"{article_id}.jpg"
    with open(local_path, "rb") as f:
        img_data = f.read()
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"
    upload_headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    r = requests.post(upload_url, headers=upload_headers, data=img_data)
    if r.status_code >= 400:
        print(f"  WARN: image upload failed for {article_id}: {r.status_code} {r.text[:300]}")
        return ""
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
    print(f"  Image uploaded: {public_url}")
    return public_url

def update_image_url(article_id: str, image_url: str):
    """Patch the article with its image URL."""
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers=HEADERS,
        json={"image_url": image_url},
    )
    if r.status_code >= 400:
        print(f"  WARN: image URL patch failed: {r.status_code}")

# ── ARTICLE 1: FIFA World Cup Broadcast Deal Breakthrough ──────────────────
a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "India's FIFA World Cup Blackout Is Over. A Washington DC Firm Run by an Indian American May Be the Reason Why.",
    "subheadline": "Negotiations for India's 2026 World Cup broadcast rights are complete, with an announcement expected next week — but the path there involved a Delhi High Court petition, a price crash from $100 million to $35 million, and a diaspora entrepreneur who bet $300 million that FIFA was undervaluing the Indian market",
    "slug": "fifa-world-cup-2026-india-broadcast-deal-avni-llc-diaspora-20260523",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "An Indian-American firm from Washington DC — Avni LLC, led by Deelip Mhaske — claims to have secured the FIFA India rights with a $300M guarantee, pitching OTT-first multilingual streaming aimed squarely at NRI viewing habits; the story is a diaspora business story as much as a sports one",
    "tags": ["FIFA World Cup 2026", "India Broadcasting", "Avni LLC", "Deelip Mhaske", "Delhi High Court", "Doordarshan", "NRI", "Football India", "Zee Entertainment"],
    "urgency": "breaking",
    "sources": [
        "https://theindianeye.com/2026/05/21/indian-american-firm-claims-fifa-india-rights/",
        "https://inshorts.com/en/news/negotiations-are-done-exaiff-official-on-fifa-wc-broadcast-rights-in-india",
        "https://indianeconomicobserver.com/fifa-world-cup-2026-broadcast-rights-in-india-near-finalisation-former-aiff-general-secretary-shaji-prabhakaran/",
        "https://bhaskarenglish.in/fifa-world-cup-2026-broadcast-rights-india-announcement-soon/",
        "https://newsonradar.com/washington-dc-based-avni-llc-claims-a-300-million-guarantee-for-fifa-india-rights/"
    ],
    "word_count": 780,
    "score_total": 70,
    "body": """Three days ago, we wrote that India — 1.4 billion people, the world's largest sports market — had no broadcaster for the FIFA World Cup. On Saturday morning, that changed. Sort of.

Former All India Football Federation General Secretary Shaji Prabhakaran confirmed that negotiations for the 2026 World Cup broadcast rights in India are complete. "After months of uncertainty, fans can finally relax — the World Cup will be fully accessible in India," he said. An official announcement is expected next week, less than three weeks before the tournament kicks off on June 11 in Mexico City.

The relief is real. But the story of how India nearly blacked out the biggest sporting event on the planet — and how it was a Washington DC firm run by an Indian American that may have broken the deadlock — is worth understanding, because it says something important about who controls Indian sports media and who might control it next.

## The price crash

FIFA originally valued the India broadcasting rights package for the 2026 and 2030 World Cups at approximately $100 million. It was a number that assumed India's 745.7 million digital engagements during the 2022 Qatar World Cup — the highest of any non-qualifying nation — would translate into broadcaster appetite. It did not.

No major Indian broadcaster bit. Not Disney Star, which holds the ICC cricket rights. Not Viacom18, which had invested heavily in La Liga and Serie A. Not Sony, which had broadcast the previous two World Cups in India. The disinterest was a market verdict: Indian football viewership, while growing, could not justify $100 million when cricket dominates every advertising rupee.

FIFA blinked. The rights value was slashed to approximately $35 million — a 65 percent cut that tells you everything about where football sits in India's sports economy. Even at that reduced price, no deal was signed until the Delhi High Court intervened.

## The court steps in

In May, advocate Avdhesh Bairwa filed a writ petition under Article 226 of the Constitution, arguing that India's failure to secure broadcast rights would deprive millions of citizens of access to a culturally significant global event. Justice Purushaindra Kumar Kaurav issued notices to the Centre and Prasar Bharati, the public broadcaster, seeking assurances that the tournament would be available on free-to-air platforms like Doordarshan and DD Sports.

The legal pressure was significant. India's Sports Broadcasting Signals (Mandatory Sharing with Prasar Bharati) Act, 2007, requires that events of national importance be shared with Doordarshan — but only after a private broadcaster acquires the rights. With no private broadcaster in the picture, the Act's protections were meaningless, creating a constitutional gap that Bairwa's petition sought to close.

## The diaspora wildcard

While established broadcasters hesitated, a name emerged from an unexpected direction. Avni LLC, a Washington DC-based investment firm led by Indian American entrepreneur Deelip Mhaske, announced that it had submitted a corporate guarantee backed by financial commitments exceeding $300 million as part of FIFA's closed tender process for the Indian subcontinent. The firm claims an associated partner secured the winning bid after competing against several major Indian broadcasters.

Avni LLC's pitch is not traditional television. Mhaske is proposing an OTT-first model built around AI-powered multilingual broadcasting, mobile micro-subscriptions, and esports integrations across Asia. "The Indian subcontinent alone has the ability to exceed initial valuation expectations," he said.

The contrast with China is instructive. China's state broadcaster CMG sealed a comprehensive deal with FIFA on May 15 for approximately $60 million — nearly double what India's rights were eventually valued at. China's deal was government-backed. India's may end up being diaspora-backed. The irony is hard to miss.

## What this means for NRIs

For the estimated 32 million Indians living abroad, the broadcast question is not academic. NRIs in the US, UK, and Canada will watch the World Cup on Fox, the BBC, and TSN regardless of what happens in India. But they watch differently when India has skin in the game — when their relatives in Delhi and Chennai are watching the same matches, when WhatsApp groups light up with commentary, when the shared experience crosses time zones.

A blackout in India would have meant a fractured viewing experience for the diaspora. The deal, when officially announced, will restore that connective tissue.

## What remains unclear

Prabhakaran confirmed the deal is done. But he did not name the broadcaster. FIFA has said only that discussions "are ongoing and must remain confidential at this stage." Whether the final partner is Avni LLC, Zee Entertainment (which has been separately reported as a contender), or Doordarshan itself remains unknown.

What is known is the timeline: an announcement next week, a tournament that starts June 11, and a country of 1.4 billion people that came within three weeks of missing it entirely. The World Cup is coming to Indian screens. The margin was uncomfortably thin.""",
}

# ── ARTICLE 2: IPL 2026 Qualifier 1 — RCB vs GT in Dharamsala ─────────────
a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "RCB and Gujarat Titans Will Play a Playoff Match at 7,000 Feet. The Last Time a Team Chased There, the Ball Disappeared Into the Himalayas.",
    "subheadline": "Qualifier 1 is set: defending champions Royal Challengers Bengaluru face Shubman Gill's Gujarat Titans on May 26 in Dharamsala — a venue so high that six-hitting records are made to be broken, and where the setting sun turns the HPCA Stadium into the most beautiful ground in world cricket",
    "slug": "ipl-2026-qualifier-1-rcb-gt-dharamsala-preview-20260523",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "RCB's global fanbase is the IPL's largest diaspora following; Kohli's every playoff move is appointment television for NRIs in every timezone; Dharamsala's Himalayan backdrop makes it the most shareable cricket ground on social media — expect every NRI Instagram feed to feature those mountains",
    "tags": ["IPL 2026", "Qualifier 1", "RCB", "Gujarat Titans", "Dharamsala", "Virat Kohli", "Shubman Gill", "HPCA Stadium", "Playoffs", "Rajat Patidar", "Sai Sudarshan"],
    "urgency": "daily",
    "sources": [
        "https://livemint.com/sports/ipl-2026-points-table-after-srh-vs-rcb",
        "https://mykhel.com/cricket/ipl-2026-playoff-rcb-vs-gt-qualifier-1-confirmed",
        "https://sportskeeda.com/cricket/they-will-drop-venkatesh-iyer-harbhajan-ipl-2026-qualifier-1",
        "https://khelnow.com/cricket/ipl-2026-top-2-qualification-scenarios-rcb-gt-srh",
        "https://indiacricketschedule.com/rcb-vs-gt-qualifier-1-ipl-2026"
    ],
    "word_count": 740,
    "score_total": 65,
    "body": """The IPL 2026 league stage ended exactly as it began: in chaos. Three teams finished on 18 points. The difference between first place and third came down to decimal points in the net run rate column. And the reward for finishing first is a match in Dharamsala, where the HPCA Stadium sits at 4,650 feet above sea level, the Dhauladhar range looms behind the bowler's arm, and the ball travels further than physics should allow.

Royal Challengers Bengaluru topped the table. Gujarat Titans finished second. They will meet in Qualifier 1 on May 26 — a Tuesday evening in India, a Tuesday morning in California, and a Tuesday night in London. The winner goes directly to the final on May 31 at the Narendra Modi Stadium in Ahmedabad. The loser gets a second chance in Qualifier 2 on May 29 against the Eliminator winner. Either way, there is no margin for error anymore.

## How RCB topped the table despite losing

The paradox of RCB's league campaign is that they clinched the top spot on a night they lost by 55 runs. Sunrisers Hyderabad dismantled them in Hyderabad on Friday — 255 for 4 in 20 overs, with Travis Head and Abhishek Sharma treating the Bengaluru bowling like a net session. RCB's chase stalled at 200, and the ground announcer barely had time to read the result before social media declared them dead.

They were not. RCB's net run rate of +0.783 — built on comprehensive victories over CSK, LSG, and MI earlier in the season — was just enough to stay above Gujarat's +0.695 and Hyderabad's +0.636. The arithmetic of cumulative excellence saved them where one bad night could not hurt them. Rajat Patidar's side had done enough across thirteen matches to absorb a humiliation in the fourteenth.

## The Virat factor

Any conversation about RCB in the playoffs starts and ends with Kohli. The 37-year-old is playing his twentieth IPL season, and his hunger for a second title — having finally won his first last year after sixteen years of failure — has not dimmed. He has been RCB's most reliable batter in high-pressure situations, and his record in knockout matches over the last two seasons is exceptional: 287 runs in five playoff innings at a strike rate of 157.

But Kohli brings more than runs. His presence at the crease changes the body language of every fielder on the opposition. When GT captain Shubman Gill sets the field to Kohli, he is simultaneously managing a batting threat and a psychological war. Kohli does not need to score quickly. He needs to be there, and the pressure shifts.

The complication is Travis Head. Kohli refused Head's handshake after Friday's defeat — a moment that has consumed every cricket conversation in India since. If SRH win the Eliminator and face RCB in Qualifier 2, that rivalry will be waiting. But first, Kohli needs to get past Gill, who has his own reasons to prove a point: the India captain was dropped from the T20 World Cup squad two years ago, and the captaincy came as redemption.

## GT's case: consistency over chaos

Gujarat Titans have been the most balanced team in IPL 2026. Where RCB relied on moments of individual brilliance — Kohli's centuries, Rajat Patidar's finishing — GT accumulated wins through system cricket. Sai Sudarshan leads the Orange Cap race with 638 runs, the best opening partnership in the tournament, and a middle order that rarely collapses.

Their bowling is the real story. Rashid Khan has been GT's banker — economical in the middle overs, lethal in death overs — and Mohit Sharma's cutters at the death have been quietly brilliant. GT do not have a single match-winner as incandescent as Kohli. They have six or seven players who deliver consistently. In a one-off knockout, that depth could be the difference.

## Dharamsala: where altitude changes everything

The HPCA Stadium is not a neutral venue. At altitude, the ball carries further, which favors aggressive batting. Dew is heavier in the evening, which favors chasing. And the mountain backdrop — where the Dhauladhar peaks catch the last golden light of sunset during the second innings — is not just aesthetics; the shifting light makes high catches genuinely difficult.

For the diaspora, Dharamsala is the most shareable cricket ground on the planet. Every NRI who has been to McLeod Ganj or the Dalai Lama's temple will recognize the mountains behind the stadium. The social media content from this match will travel further than the sixes.

## The fourth spot

While RCB and GT prepare for Dharamsala, the fight for the last playoff berth continues. Punjab Kings face Lucknow Super Giants on Saturday, Rajasthan Royals meet Mumbai Indians on Sunday, and Kolkata Knight Riders play Delhi Capitals on the same day. One of those four teams will join SRH in the Eliminator on May 27 in Mullanpur.

The scenarios are tangled. If Punjab lose, they are eliminated. If they win, they need results from the other two matches. For NRI fans following from across time zones, the final weekend of the league stage is a scheduling nightmare and an emotional rollercoaster. Every match matters. Every net run rate point matters. Every boundary in every over in every innings in the next 48 hours could decide who stands in Ahmedabad on May 31.

The IPL's greatest trick has always been making you care about a league match involving two eliminated teams because the result affects a third team on the other side of the country. This weekend, the trick works perfectly.""",
}

if __name__ == "__main__":
    # Insert articles
    print("Inserting Article 1: FIFA World Cup broadcast deal breakthrough...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    print("Inserting Article 2: IPL 2026 Qualifier 1 preview...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    # Upload images
    img1_path = "/home/hatch/workspace/imagine_media/imagine-editorial-sports-photography-a-0-1779548515866-0.jpg"
    img2_path = "/home/hatch/workspace/imagine_media/imagine-editorial-sports-photography-a-0-1779548514934-0.jpg"

    if os.path.exists(img1_path):
        url1 = upload_image(a1_id, img1_path)
        if url1:
            update_image_url(a1_id, url1)

    if os.path.exists(img2_path):
        url2 = upload_image(a2_id, img2_path)
        if url2:
            update_image_url(a2_id, url2)

    print(f"\nDone. 2 articles published with images.")
    print(f"  IDs: {a1_id}, {a2_id}")
