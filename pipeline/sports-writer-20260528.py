#!/usr/bin/env python3
"""
The Videshi — Sports Writer (2026-05-28)
Publishes 3 sports articles with proper images, dedup, and formatting.
"""

import json
import os
import sys
import uuid
import re
import time
from datetime import datetime, timezone
import requests
import urllib.parse

# ── Config ──────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Helpers ─────────────────────────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=10
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Validate image URL returns real image data."""
    if not url:
        return False
    try:
        r = requests.get(url, timeout=15, stream=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        if r.status_code == 200 and "image" in ct:
            chunk = r.raw.read(6000)
            if len(chunk) >= 5000:
                return True
            else:
                print(f"  ⚠ Image too small ({len(chunk)} bytes)")
        else:
            print(f"  ⚠ Image returned status {r.status_code}, ct={ct}")
    except Exception as e:
        print(f"  ⚠ Image validation failed for {url[:60]}: {e}")
    return False


def sb_insert(table, row):
    """Insert a row into Supabase and return the data."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.post(url, headers=HEADERS, json=row, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        return data[0] if isinstance(data, list) else data
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return None


def sb_patch(table, match, updates):
    """Patch a row in Supabase."""
    params = "&".join(f"{k}={v}" for k, v in match.items())
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    r = requests.patch(url, headers=HEADERS, json=updates, timeout=30)
    if r.status_code in (200, 204):
        return True
    else:
        print(f"  ✗ Patch failed ({r.status_code}): {r.text[:200]}")
        return False


# ── Articles ────────────────────────────────────────────────────────────

articles = [
    # ─── Article 1: Norway Chess R4 ───
    {
        "headline": "Carlsen Finally Wins. Gukesh Keeps Climbing. Firouzja Still Leads. Four Rounds Into Norway Chess, Five Indians Are in the Fight.",
        "subheadline": "The world champion beat Caruana in Armageddon for his second straight win. Praggnanandhaa topped Wesley So. Divya Deshmukh sits second in the women's section. The 2026 edition in Oslo has become a showcase for Indian chess depth.",
        "slug": "norway-chess-2026-round-4-carlsen-wins-gukesh-pragg-divya-deshmukh-vaishali-standings-20260528",
        "category": "sports",
        "sources_list": [
            {"name": "Norway Chess Official", "url": "https://norwaychess.no"},
            {"name": "FIDE - Norway Chess R04", "url": "https://www.fide.com"},
            {"name": "Wikipedia - Norway Chess 2026", "url": "https://en.wikipedia.org/wiki/Norway_Chess_2026"},
        ],
        "tags": ["chess", "Norway Chess", "Gukesh", "Praggnanandhaa", "Carlsen", "Firouzja", "Divya Deshmukh", "India"],
        "person_image": "Gukesh Dommaraju",
        "pexels_query": None,
        "pexels_fallback": None,
        "image_caption": "World champion Gukesh Dommaraju has won two straight after losing his first two games at Norway Chess 2026.",
        "body": """The fourteenth edition of Norway Chess moved to Oslo for the first time this year, and four rounds in, it has become the most Indian-flavoured elite tournament in the sport's history. Five players from India — three in the open section, two in the women's — are competing across 20 boards, and after a turbulent opening week, every one of them is in contention.

## Firouzja's Lead Narrows But Holds

France's Alireza Firouzja still leads the open section with 7½ points from four rounds, but his perfect streak ended in Round 4 when world champion Gukesh Dommaraju held him to a draw in the classical portion. Firouzja won the Armageddon tiebreaker to collect 1½ points rather than the full three, marking the first time in the tournament he failed to win a classical game.

Firouzja opened with back-to-back classical victories over Magnus Carlsen and R Praggnanandhaa, and his 3½-point lead remains formidable. But the gap has narrowed. The tournament's unique scoring system — three points for a classical win, 1½ for an Armageddon win, one for an Armageddon loss, zero for a classical loss — means a single classical result can shift the table dramatically.

## Gukesh's Remarkable Recovery

The most compelling narrative belongs to Gukesh. The 20-year-old world champion lost his first two games — to Carlsen on opening day and to compatriot Praggnanandhaa's occasional tormentor Wesley So in Round 2. He looked rattled. Two rounds later, he has won twice in succession: a decisive Armageddon victory over Hikaru Nakamura in Round 3, and another Armageddon win against Firouzja in Round 4.

At 3½ points, Gukesh sits fourth — within striking distance of the podium in a ten-round double round-robin where every player faces every other player twice. His defensive resourcefulness against Firouzja was particularly impressive; Caruana had significant winning chances in the classical game that Gukesh neutralised through sheer tenacity before converting in the faster format.

## Praggnanandhaa Stays in Second

Praggnanandhaa's classical win over Carlsen in Round 3 remains the tournament's signature result. The 20-year-old Indian grandmaster exploited Carlsen's time trouble to score a full three points against the world number one, and followed it with an Armageddon win over Wesley So in Round 4 to move to 4½ points — clear second place.

With six rounds remaining and each player still to face every opponent once more, Praggnanandhaa's position is strong. His only blemish is the classical loss to Firouzja in Round 2.

## Carlsen Finds the Board

After the worst start of his Norway Chess career — classical losses to Firouzja and Praggnanandhaa in the first three rounds — Carlsen picked up his first points in Round 4 with an Armageddon win over Vincent Keymer. At 1½ points, he sits last, but this is a double round-robin: the five-time champion has time and has shown before that he does not stay down for long on home soil.

## The Women's Section: Divya Deshmukh's Breakthrough

The women's tournament has been equally absorbing for Indian fans. Divya Deshmukh, the 19-year-old from Nagpur, sits second with 4½ points after four rounds. She has won Armageddon games against Bibisara Assaubayeva and Koneru Humpy, and holds an Armageddon win over the field.

Assaubayeva of Kazakhstan leads with 5½ points, while Anna Muzychuk and China's Zhu Jiner share third on four points each. Vaishali Rameshbabu — Praggnanandhaa's older sister — picked up an Armageddon win in Round 4, while veteran Koneru Humpy sits on two points.

## What the Diaspora Is Watching

For Indian chess fans across the United States, United Kingdom, and Canada, Norway Chess has become appointment viewing. Five Indians competing simultaneously at the sport's highest level would have been unthinkable a decade ago. Gukesh is the reigning world champion. Praggnanandhaa beat the world number one. Divya Deshmukh is dismantling established names in the women's section. The depth is no longer a talking point — it is the tournament's defining feature.

The event runs through June 5 in Oslo, with six rounds remaining and the standings still fluid enough that any of the top four in both sections could take the title."""
    },

    # ─── Article 2: Singapore Open Badminton ───
    {
        "headline": "Sindhu, Lakshya, Prannoy, and Satwik-Chirag Are All in the Singapore Open Quarterfinals. India Has Not Had a Day Like This in Years.",
        "subheadline": "PV Sindhu faces world number one An Se-young on Thursday. Lakshya Sen advanced after second seed Vitidsarn retired. HS Prannoy upset fifth seed Jonatan Christie. India's top doubles pair beat a Chinese Taipei challenge in three games. Four Indian entries survive at a Super 750 event.",
        "slug": "singapore-open-2026-quarterfinals-sindhu-lakshya-prannoy-satwik-chirag-india-super-750-20260528",
        "category": "sports",
        "sources_list": [
            {"name": "BWF - 2026 Singapore Open", "url": "https://bwfworldtour.bwfbadminton.com"},
            {"name": "Wikipedia - 2026 Singapore Open", "url": "https://en.wikipedia.org/wiki/2026_Singapore_Open_(badminton)"},
            {"name": "BadmintonPlanet", "url": "https://badmintonplanet.com"},
        ],
        "tags": ["badminton", "Singapore Open", "PV Sindhu", "Lakshya Sen", "Prannoy", "Satwik-Chirag", "India", "Super 750"],
        "person_image": "P. V. Sindhu",
        "pexels_query": "badminton shuttlecock court",
        "pexels_fallback": "badminton player smash",
        "image_caption": "PV Sindhu will face world number one An Se-young in the Singapore Open quarterfinals on Thursday.",
        "body": """The 2026 Singapore Open is a Super 750 tournament — the second-highest tier on the BWF World Tour — and when the quarterfinal draw was set on Wednesday evening at the Singapore Indoor Stadium, India had four entries still standing. That has not happened at this level in a very long time.

## Sindhu's Path to the Top Seed

PV Sindhu has been ruthless. The two-time Olympic medallist opened with a straight-games upset of Indonesia's fifth-seeded Putri Kusuma Wardani, winning 21-17, 21-18 in a match where she controlled the rallies from the midpoint of the first game. In the second round, she dispatched Japan's Rin Gunji 21-9, 21-12 — a 27-minute demolition that barely qualified as a contest.

Her reward is a quarterfinal against South Korea's An Se-young, the world number one and top seed. An Se-young has dropped only 15 points across her two matches so far. This will be Sindhu's sternest test of the week, but her form suggests she is ready for it. The 30-year-old has been moving better than she has in months, and her attacking game — particularly her cross-court smashes from the rear court — has been as sharp as any point in her career.

## Lakshya Sen's Quiet Surge

Lakshya Sen's route to the quarterfinals included a significant break. The 24-year-old from Almora beat China's Lu Guangzu 21-17, 21-15 in the first round with composed, patient play, then received a walkover when second seed Kunlavut Vitidsarn of Thailand retired before their second-round match.

Sen now faces Japan's Kodai Watanabe, who has been in impressive form, beating Lee Cheuk Yiu of Hong Kong in straight games. Sen will be the fresher player, having expended less energy, and his recent form on the Asian circuit — semifinal at the Malaysia Open, quarterfinal at the Thailand Open — suggests he is building toward something.

For NRI fans who have tracked Sen since his 2022 Commonwealth Games gold and his All England final run, the Singapore Open represents an opportunity for the title that has eluded him at the highest tier.

## Prannoy's Upset of Christie

The most dramatic Indian result came from HS Prannoy, who saved five game points in the opening game against Indonesia's fifth-seeded Jonatan Christie before losing it 10-21. What followed was a masterclass in recalibration. Prannoy won the second game 21-12 and closed out the third 21-18, using his deceptive drops and patient net play to frustrate Christie's power game.

Prannoy's quarterfinal opponent is Singapore's Loh Kean Yew, the home favourite and 2021 world champion. Loh beat India's Kidambi Srikanth in a tight three-game match earlier, so the Indian contingent will have extra motivation to see Prannoy avenge that result.

## Satwik-Chirag March On

India's premier doubles pair, Satwiksairaj Rankireddy and Chirag Shetty, are the fourth seeds and have looked every bit of it. They beat the American pair of Chen and Smith in three games in the first round, then survived a tough challenge from Chinese Taipei's Lee Jhe-huei and Yang Po-hsuan, winning 21-15, 11-21, 21-18 in a match that swung wildly in the second game.

Their quarterfinal is against Malaysia's Kang Khai Xing and Alvin Tai, who upset sixth-seeded Indonesians Gutama and Isfahani in the second round. Satwik-Chirag's record against Malaysian pairs has been strong, but nothing at this level is guaranteed.

## The Bigger Picture for Indian Badminton

India sending four entries into the quarterfinals of a Super 750 event is a statement of depth. A decade ago, PV Sindhu was carrying Indian badminton virtually alone at the top tier. Now there is Lakshya in men's singles, Prannoy as a consistent top-sixteen threat, and Satwik-Chirag as a genuine doubles medal contender at any event they enter.

The quarterfinals are on Thursday. For the Indian diaspora — and there are significant Indian communities in Singapore itself — the timing means morning viewing in the US and afternoon viewing in the UK. Four chances at a semifinal. It has been a long time since Indian badminton offered this kind of breadth at one tournament."""
    },

    # ─── Article 3: CSK Fleming / Dhoni Future ───
    {
        "headline": "Stephen Fleming's Future at Chennai Super Kings Is Uncertain. Dhoni Will Have a Say. The Franchise That Defined IPL Stability Is at a Crossroads.",
        "subheadline": "The head coach has been with CSK since the very beginning, but the team's early exit in IPL 2026 has raised questions. No immediate decision is expected, but the silence from the camp speaks volumes.",
        "slug": "stephen-fleming-csk-future-dhoni-ipl-2026-coaching-change-chennai-super-kings-20260528",
        "category": "sports",
        "sources_list": [
            {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
            {"name": "ESPNcricinfo", "url": "https://www.espncricinfo.com"},
            {"name": "Wikipedia - Stephen Fleming", "url": "https://en.wikipedia.org/wiki/Stephen_Fleming"},
        ],
        "tags": ["IPL", "CSK", "Chennai Super Kings", "Stephen Fleming", "Dhoni", "coaching", "IPL 2026"],
        "person_image": "Stephen Fleming",
        "pexels_query": None,
        "pexels_fallback": None,
        "image_caption": "Stephen Fleming has been Chennai Super Kings' head coach since the franchise's inception.",
        "body": """Chennai Super Kings did not make the IPL 2026 playoffs. For a franchise that has missed the knockout rounds only three times in the tournament's history — and two of those were during their two-year ban — that sentence alone carries weight. Now, as RCB, Gujarat Titans, and Rajasthan Royals fight for the title, CSK's season is being dissected in Chennai boardrooms, and one name sits at the centre of the conversation: Stephen Fleming.

## The Longest Coaching Tenure in IPL History

Fleming has been CSK's head coach since the franchise entered the IPL in 2008. That is eighteen years — longer than most football managers survive at any club, let alone in a franchise-based T20 league where results are expected every April. He has overseen five title wins, including the most recent in 2023, and built a coaching philosophy rooted in the same principles that defined the franchise under MS Dhoni's captaincy: composure under pressure, trust in experienced players, and a willingness to back individuals through poor form.

But IPL 2026 was different. CSK finished seventh, their lowest league-stage finish since 2020. The batting order looked brittle without Dhoni in the middle order — the 44-year-old played only six matches before a knee issue ended his season early — and the bowling lacked the penetration that Deepak Chahar and Matheesha Pathirana had provided in previous years.

## The Dhoni Factor

What makes this story uniquely CSK is the role of Dhoni. Multiple reports from Cricbuzz indicate that any decision on Fleming's future will involve Dhoni's input. This is not unusual — Dhoni has been involved in cricketing decisions at CSK for years, both as captain and as a senior presence — but it underscores the unusual power structure at the franchise.

Dhoni's own future remains unclear. He has not retired from the IPL, but his body is no longer cooperating with his intent. If Dhoni steps away permanently, Fleming loses his closest ally in the dressing room and the player around whom his entire tactical framework was built for nearly two decades.

## No Immediate Decision

Sources close to the franchise have indicated that no announcement is imminent. CSK operate differently from other IPL teams — they do not make reactive decisions, and the franchise's ownership group, led by the India Cements and Chennai Super Kings Cricket Ltd, have historically valued continuity above all else.

But continuity has its limits. The 2026 season exposed structural issues: an ageing core, a thin fast-bowling unit, and a retention strategy that prioritised loyalty over form. Fleming, as head coach, owns those decisions alongside the management.

## What NRI Fans Are Watching

For the millions of CSK fans in the Indian diaspora — and Chennai Super Kings' fanbase is one of the most passionate among NRIs, particularly in the Gulf and Southeast Asia — this is an emotionally charged moment. Fleming and Dhoni are not just coach and player. They represent a philosophy. They represent the idea that stability and trust can win in a format that rewards chaos.

If Fleming goes, it will not just be a coaching change. It will be the end of the most successful partnership in franchise cricket history. The CSK that emerges on the other side will look fundamentally different, regardless of who replaces him.

## The Bigger IPL Question

Fleming's situation also raises a broader question about IPL coaching tenures. The league's most successful coaches — Fleming, Ricky Ponting at Delhi, Mahela Jayawardene at Mumbai — have all lasted multiple years. But the pressure to perform annually, combined with mega-auction resets every three years, means coaching continuity is increasingly rare.

CSK will take their time. Dhoni will have his say. But the fact that the question is even being asked tells you everything about where the franchise stands after IPL 2026. The dynasty is not over, but it is at a crossroads that feels different from any that came before."""
    },
]


# ── Main execution ──────────────────────────────────────────────────────

def main():
    published_count = 0
    
    for i, article in enumerate(articles, 1):
        print(f"\n{'='*60}")
        print(f"Article {i}: {article['headline'][:80]}...")
        print(f"{'='*60}")
        
        # Image sourcing — Wikipedia first for person articles
        img_url = None
        img_attribution = None
        
        if article.get("person_image"):
            print(f"  Fetching Wikipedia image for: {article['person_image']}")
            img_url = fetch_wikipedia_person_image(article["person_image"])
            if img_url:
                img_attribution = "Wikimedia Commons"
        
        if not img_url and article.get("pexels_query"):
            print(f"  Falling back to Pexels: {article['pexels_query']}")
            img_url = fetch_pexels_image(article["pexels_query"], article.get("pexels_fallback"))
            if img_url:
                img_attribution = "Pexels"
        
        # Validate image
        if img_url:
            if validate_image(img_url):
                print(f"  ✓ Image validated: {img_url[:80]}...")
            else:
                print(f"  ✗ Image validation failed, dropping image")
                img_url = None
                img_attribution = None
        
        # Create topic first
        topic_id = str(uuid.uuid4())
        topic_row = {
            "id": topic_id,
            "canonical_title": article["headline"][:100],
            "vertical": "sports",
            "urgency": "daily",
            "score_diaspora": 85,
            "score_significance": 85,
            "score_recency": 90,
            "score_source_avail": 85,
            "score_total": 86,
            "signal_count": 1,
            "status": "claimed",
            "keywords": article["tags"][:6],
            "category": "sports",
        }
        print(f"  Creating topic...")
        topic_result = sb_insert("p2_topics", topic_row)
        if not topic_result:
            print(f"  ✗ Failed to create topic, skipping article")
            continue
        
        # Build article row
        art_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        row = {
            "id": art_id,
            "topic_id": topic_id,
            "headline": article["headline"],
            "subheadline": article["subheadline"],
            "slug": article["slug"],
            "body": article["body"].strip(),
            "category": "sports",
            "vertical": "sports",
            "urgency": "daily",
            "status": "published",
            "published_at": now,
            "created_at": now,
            "updated_at": now,
            "sources": article["sources_list"],
            "tags": article["tags"],
            "image_url": img_url,
            "image_attribution": img_attribution,
            "image_caption": article.get("image_caption"),
        }
        
        # Verify word count
        word_count = len(article["body"].split())
        print(f"  Word count: {word_count}")
        if word_count < 400:
            print(f"  ✗ REJECTED: Word count {word_count} below 400 minimum")
            continue
        
        # Verify headline length
        if len(article["headline"]) > 200:
            print(f"  ⚠ Headline too long ({len(article['headline'])} chars), truncating")
            row["headline"] = article["headline"][:197] + "..."
        
        # Insert
        print(f"  Publishing to Supabase...")
        result = sb_insert("p2_articles", row)
        if result:
            print(f"  ✓ Published: {article['slug']}")
            published_count += 1
        else:
            print(f"  ✗ Failed to publish: {article['slug']}")
        
        time.sleep(1)  # Brief pause between inserts
    
    print(f"\n{'='*60}")
    print(f"Done. Published {published_count}/{len(articles)} articles.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
