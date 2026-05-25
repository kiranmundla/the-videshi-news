#!/usr/bin/env python3
"""Entertainment writer — May 25 2026, 01:30 UTC batch:
1. Star Wars: The Mandalorian and Grogu crashed in India — ₹3.15 Cr in 3 days vs $81M in the US
2. Vashu Bhagnani vs David Dhawan/Tips legal war — Supreme Court, vendor debts, Biwi No. 1 allegations
+ Score decay for older entertainment articles
"""

import json, os, uuid, requests
from datetime import datetime, timezone, timedelta
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

def sb_get(table, filters, select="*"):
    r = requests.get(f"{SB_URL}/rest/v1/{table}?{filters}&select={select}", headers=HEADERS, timeout=15)
    return r.json() if r.status_code == 200 else []

def check_duplicate(slug):
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id",
        headers=HEADERS, timeout=15
    )
    return len(r.json()) > 0 if r.status_code == 200 else False

now = datetime.now(timezone.utc)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S")

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Star Wars: The Mandalorian and Grogu India flop
# ══════════════════════════════════════════════════════════════
slug1 = "mandalorian-grogu-star-wars-india-flop-3-crore-drishyam-3-cultural-divide-20260525"
if not check_duplicate(slug1):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Star Wars Just Opened in India. It Made ₹3 Crore in Three Days. Drishyam 3 Made That in Three Hours. The Cultural Divide Between the Diaspora and the Homeland Has Never Been This Visible at the Box Office.",
        "subheadline": "The Mandalorian and Grogu opened to $81 million in the United States over its first three days. In India — across 2,800 shows in every major multiplex chain — it collected ₹3.15 crore. That's roughly $375,000. The most dominant franchise in Western pop culture can't fill a screen in Kochi. And the film that's packing those screens — Drishyam 3 — barely exists in the American consciousness. For the diaspora, this isn't just a box office story. It's a mirror.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "trending",
        "status": "published",
        "published_at": now_iso,
        "score_total": 78,
        "tags": ["Star Wars", "The Mandalorian and Grogu", "Drishyam 3", "India box office", "Hollywood in India", "cultural divide", "Mohanlal", "Pedro Pascal", "Jon Favreau"],
        "diaspora_angle": "Every NRI household in America knows this split intimately. Your kids are watching Ahsoka and debating lightsaber lore on the school bus. Your parents are streaming Mohanlal films on their iPad. You live in both worlds — and this weekend's box office numbers quantify that divide more precisely than any cultural study ever could. Star Wars made $81 million in 3 days in the US. Drishyam 3 made ₹58 crore in India but barely registered here. The franchises that define your two countries don't even overlap. For NRIs raising children in the US, this isn't trivia — it's the daily negotiation of which stories your family shares.",
        "sources": [
            {"url": "https://www.sacnilk.com/movies/Star_Wars_The_Mandalorian_and_Grogu_3D/box_office_collection_day_3", "name": "Sacnilk"},
            {"url": "https://www.pinkvilla.com/entertainment/box-office/star-wars-the-mandalorian-and-grogu-india-box-office", "name": "Pinkvilla"},
            {"url": "https://technosports.co.in/star-wars-mandalorian-grogu-india-opening", "name": "TechnoSports"},
            {"url": "https://screenrant.com/mandalorian-grogu-opening-weekend-box-office", "name": "Screen Rant"},
            {"url": "https://tracktollywood.com/box-office-collection/drishyam-3-malayalam/", "name": "TrackTollywood"}
        ],
        "image_search_query": "Star Wars The Mandalorian and Grogu movie poster 2026 Pedro Pascal",
        "image_entities": ["Star Wars", "The Mandalorian", "Grogu", "Pedro Pascal"],
        "image_must_show": "The Mandalorian and Grogu movie imagery or empty Indian cinema hall",
        "word_count": 780,
        "body": """On the same weekend, in the same country, two films played in the same multiplexes.

One is the latest chapter of the most commercially successful film franchise in history — a $4 billion brand that has shaped Western childhoods for nearly five decades. The other is the third installment of a Malayalam thriller about a man who buries a body and dares the police to find it.

The Malayalam thriller won. It wasn't close.

## The Numbers That Tell the Story

**Star Wars: The Mandalorian and Grogu** opened in India on May 22 across approximately 2,800 shows in 3D and IMAX formats. Here's what happened:

- **Day 1**: ₹0.70 crore net (2,806 shows)
- **Day 2** (Saturday): ₹1.35 crore net (2,770 shows)
- **Day 3** (Sunday): ₹1.10 crore net (2,481 shows)
- **3-day India total**: ₹3.15 crore net (~$375,000)

For context, that same weekend in the United States, the film opened to **$81 million** in three days. The disparity isn't a rounding error — it's a civilisational one.

Meanwhile, **Drishyam 3** collected ₹15.03 crore on Sunday alone — roughly five times what Star Wars made in its entire opening weekend. Mohanlal's thriller had crossed ₹58 crore in India by Day 4. In Kerala, it was running at 85% occupancy. In Thalassery, 98%.

Star Wars, in its best Indian market (Bengaluru), managed occupancy rates below 30%.

## Why Star Wars Doesn't Work Here

This isn't new. Barring Star Wars: The Force Awakens in 2015, which did modestly decent business riding a decade of anticipation, no Star Wars film has ever cracked the Indian market. The franchise's mythology — Jedi, Sith, the Force, a galactic senate — simply doesn't have the same cultural infrastructure in India that it does in the West.

**Indian audiences prefer stories rooted in recognisable emotional architecture**: family, revenge, honour, religious mythology, class. Drishyam works because Georgekutty's dilemma — a father protecting his family from the law — is legible anywhere in India. The Mandalorian's bond with Grogu is sweet, but it doesn't carry the same weight.

The numbers bear this out year after year. In 2026 alone, Indian box office has been dominated by **Dhurandhar 2** (₹1,184 crore), **Border 2** (₹362 crore), and **Bhooth Bangla** (₹189 crore) — all rooted in Indian narrative traditions. Hollywood's biggest hit in India this year has been **The Mummy** (a Lee Cronin horror film), not any franchise property.

## The Diaspora Mirror

For NRIs, this weekend's box office tells a more personal story.

In the United States, Star Wars is inescapable. Your children know every character. Memorial Day weekend — the weekend Mandalorian and Grogu opened — is a family movie event in American culture. Your co-workers are discussing it at the water cooler on Monday.

But call your parents in Kochi, and they'll tell you about Drishyam 3. They've seen it twice. They know the twist. They have opinions about Jeethu Joseph's direction. Star Wars? They wouldn't recognise the poster.

This cultural split isn't abstract for the diaspora — it's the daily texture of raising children between two worlds. The franchises that matter to your American life and the franchises that matter to your Indian identity don't overlap. They exist in parallel, and this weekend, the gap between them was measured in crores and dollars.

## What Happens Next

The Mandalorian and Grogu will likely finish its India run somewhere around ₹8-10 crore — perfectly forgettable. Drishyam 3, by contrast, is tracking toward ₹150-200 crore worldwide and has already broken records as the second-highest opening in Malayalam cinema history.

The lesson isn't that Hollywood is failing. It's that India has developed its own blockbuster economy — one that serves its audience's tastes more precisely than any imported franchise can. For the Indian viewer, Georgekutty's silence is more thrilling than any lightsaber.

For the diaspora, the lesson is different and more intimate: **the two halves of your cultural world are moving further apart, not closer together.** The films that unite your American friends have never mattered less to the country you come from. And the films that unite your Indian family have never mattered more.""",
    })
    print(f"✅ Article 1 prepared: {slug1}")
else:
    print(f"⚠️ DUPLICATE: {slug1}")

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Vashu Bhagnani vs David Dhawan/Tips legal war
# ══════════════════════════════════════════════════════════════
slug2 = "vashu-bhagnani-david-dhawan-tips-supreme-court-hai-jawani-biwi-no-1-legal-war-20260525"
if not check_duplicate(slug2):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Vashu Bhagnani Called a Press Conference to Destroy David Dhawan's New Film. The Supreme Court Dismissed His Case the Same Day. Now Both Sides Are Talking — and the Numbers Don't Add Up.",
        "subheadline": "Producer Vashu Bhagnani claims David Dhawan was paid ₹70 crore for Coolie No 1, that Hai Jawani Toh Ishq Hona Hai is a Biwi No. 1 remake, and that the Dhawans owe him a sequel. The Dhawan camp says the ₹70 crore figure is fiction, Bhagnani left vendors unpaid on Coolie No 1, and the Dhawans covered ₹16 crore of those debts from their own pocket. The Supreme Court has already ruled. The trailer is out. The film releases June 5. This is Bollywood's ugliest producer war of the year.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "developing",
        "status": "published",
        "published_at": now_iso,
        "score_total": 76,
        "tags": ["Vashu Bhagnani", "David Dhawan", "Varun Dhawan", "Hai Jawani Toh Ishq Hona Hai", "Biwi No 1", "Coolie No 1", "Supreme Court", "Tips Films", "Ramesh Taurani", "Bollywood legal dispute", "Chunari Chunari"],
        "diaspora_angle": "For NRIs who grew up on David Dhawan comedies — renting Coolie No 1 and Biwi No 1 on VHS from the local Indian grocery store — this feud hits different. These aren't abstract Bollywood names. These are the films that defined weekend family viewing for a generation of diaspora kids. The fact that the creators of those films are now publicly accusing each other of fraud, unpaid debts, and broken promises says something uncomfortable about the business behind the nostalgia. And with Hai Jawani releasing on June 5, NRIs planning to see it in US theatres are now watching a film shadowed by a very public legal war.",
        "sources": [
            {"url": "https://www.bollywoodhungama.com/news/bollywood/exclusive-vashu-bhagnani-vs-tips-dhawans-row-gets-uglier/", "name": "Bollywood Hungama"},
            {"url": "https://www.bollywoodhungama.com/news/bollywood/vashu-bhagnani-press-conference-coolie-no-1-david-dhawan/", "name": "Bollywood Hungama"},
            {"url": "https://www.bollywoodhungama.com/news/bollywood/hai-jawani-toh-ishq-hona-hai-trailer-launch-david-dhawan/", "name": "Bollywood Hungama"},
            {"url": "https://stat5.bollywoodhungama.in/news/", "name": "Bollywood Hungama News"}
        ],
        "image_search_query": "Vashu Bhagnani press conference Bollywood 2026 David Dhawan Varun Dhawan legal dispute",
        "image_entities": ["Vashu Bhagnani", "David Dhawan", "Varun Dhawan", "Hai Jawani Toh Ishq Hona Hai"],
        "image_must_show": "Vashu Bhagnani at press conference or David Dhawan and Varun Dhawan together",
        "word_count": 800,
        "body": """On May 22, producer Vashu Bhagnani held a press conference in Mumbai with select media members. His target: the David Dhawan-directed comedy Hai Jawani Toh Ishq Hona Hai, starring Varun Dhawan, which is set for a worldwide release on June 5.

His allegations were explosive. The response was equally sharp. And the Supreme Court had already weighed in — dismissing his case on the same day.

Here's what both sides are saying, and why none of the numbers add up.

## Bhagnani's Allegations

Vashu Bhagnani, founder of Puja Entertainment, made several claims during his press conference:

**1. Hai Jawani is essentially Biwi No. 1 Part 2.** He alleged that the new film's story — produced by Ramesh Taurani's Tips Films and directed by David Dhawan — is connected to his 1999 hit Biwi No. 1, and that the Dhawans were contractually committed to making a sequel with him.

**2. "Chunari Chunari" belongs to him.** The iconic song from Biwi No. 1 appears in the new film. Bhagnani claimed Tips doesn't have the right to use it.

**3. He paid David Dhawan ₹70 crore for Coolie No 1 (2020).** He claimed he was "just a namesake producer" on the pandemic-era remake and that David ran the production entirely, at massive cost.

**4. He lost ₹27 crore on Coolie No 1.** The film, which released directly on Amazon Prime Video during COVID lockdowns, was a commercial disaster.

## The Dhawan Camp's Response

A source close to the Dhawan-Tips side hit back through Bollywood Hungama with a point-by-point rebuttal:

**"The Supreme Court dismissed his case today."** They pointed out that the timing of Bhagnani's press conference coincided with his legal defeat — if his claims had merit, the court wouldn't have thrown them out.

**"Hai Jawani has NOTHING to do with Biwi No. 1."** The source stated that Biwi No. 1 was about a married man's extramarital affair. Hai Jawani Toh Ishq Hona Hai is about a double pregnancy. "The two stories are poles apart."

**"₹70 crore is fiction."** The source called the payment claim "laughable," noting that if it were true, David Dhawan would have been the highest-paid director in the country at the time. "Can Mr. Bhagnani show any document? Let him release the agreement."

**"The Dhawans paid ₹16 crore from their own pocket."** The source's most damaging claim: that vendors on Coolie No 1 were never paid by Bhagnani's production house, and the Dhawans covered ₹16 crore of those debts themselves — out of personal reputation concerns, not contractual obligation.

**"He knew about Chunari Chunari for months."** The source noted that the song's inclusion in the new film had been publicly known for months, but Bhagnani only filed his case a month before release. "Why wait till the last minute? The timing itself raises questions."

## What Makes This Different

Bollywood has producer feuds routinely. What makes this one notable is the scale of the claims and the personal nature of the accusations.

Vashu Bhagnani was once one of Bollywood's most visible producers — the man behind No Entry, Bade Miyan Chote Miyan, and the Coolie No 1 remake. But his production house, Puja Entertainment, has faced financial struggles in recent years. His son Jackky Bhagnani, who produced the action film Bade Miyan Chote Miyan (2024) with Akshay Kumar, saw that film become one of the biggest flops of the year.

David Dhawan, by contrast, is in a late-career resurgence. The trailer for Hai Jawani — his 46th film and fourth with son Varun — received an emotional response at its Mumbai launch on May 23. The elder Dhawan broke down in tears on stage, saying, "Everybody should have a son like Varun."

The court ruling, the emotional trailer launch, and the aggressive press conference all happened within 48 hours. For the industry, it was whiplash.

## What Happens Now

The film releases on June 5. The legal challenge has been dismissed by the Supreme Court. Bhagnani's allegations are now a matter of public record but carry no judicial weight.

For audiences — particularly NRIs planning to catch the film in US theatres — the question is whether this controversy will shadow what's being positioned as a nostalgic return to David Dhawan's 90s comedy DNA. The trailer features Anu Malik and Sameer's music, Jimmy Shergill, Chunky Panday, and the kind of multistarrer energy that defined a generation of diaspora VHS nights.

The filmmakers are betting that nostalgia is stronger than controversy. Given the Supreme Court's ruling, they're probably right.""",
    })
    print(f"✅ Article 2 prepared: {slug2}")
else:
    print(f"⚠️ DUPLICATE: {slug2}")


# ══════════════════════════════════════════════════════════════
# INSERT ARTICLES
# ══════════════════════════════════════════════════════════════
for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ Inserted: {art['slug'][:60]} → {result[0]['id'][:8] if result else '?'}")
    except Exception as e:
        print(f"❌ Insert failed for {art['slug'][:40]}: {e}")


# ══════════════════════════════════════════════════════════════
# SCORE DECAY — entertainment articles
# ══════════════════════════════════════════════════════════════
print("\n── Score Decay ──")

# 7+ days old → score 35
cutoff_7d = (now - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
status_7d = sb_patch(
    "p2_articles",
    f"category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff_7d}&score_total=gt.35",
    {"score_total": 35}
)
print(f"7d+ decay → HTTP {status_7d}")

# 3-7 days old → score 50
cutoff_3d = (now - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")
status_3d = sb_patch(
    "p2_articles",
    f"category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff_3d}&published_at=gte.{cutoff_7d}&score_total=gt.50",
    {"score_total": 50}
)
print(f"3-7d decay → HTTP {status_3d}")

print("\n✅ Entertainment writer batch complete.")
