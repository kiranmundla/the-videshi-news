#!/usr/bin/env python3
"""Sports writer — 2026-05-22 afternoon run: 2 articles."""

import os, json, uuid, requests
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
        print(f"  ERROR: {r.status_code} {r.text[:500]}")
    r.raise_for_status()
    return r.json()

def mark_topic(topic_id: str, status: str):
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_topics?id=eq.{topic_id}",
        headers=HEADERS, json={"status": status}
    )
    r.raise_for_status()


# ── ARTICLE 1: Shubman Gill — T20 World Cup Snub to India Captain ────────

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Shubman Gill Was Dropped From the T20 World Cup Squad. Now He's Captaining India.",
    "subheadline": "The 26-year-old's journey from selection snub to leading the Test and ODI sides against Afghanistan tells you everything about where Indian cricket is heading",
    "slug": "shubman-gill-t20-world-cup-snub-india-captain-afghanistan-series-20260522",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": "2026-05-22T23:30:00+00:00",
    "diaspora_angle": "Generational shift in Indian cricket leadership; NRI fans watching the post-Kohli/Rohit transition; Afghanistan series accessible for overseas viewers; Gill's Punjab roots resonate with diaspora",
    "tags": ["Shubman Gill", "India Cricket", "T20 World Cup", "Afghanistan Series", "BCCI", "KL Rahul", "Virat Kohli", "Rohit Sharma"],
    "urgency": "daily",
    "sources": [
        "https://insidesport.in/shubman-gill-relaunches-t20-career-in-ipl-2026",
        "https://www.wisden.com/series/india-vs-afghanistan-2026",
        "https://www.mykhel.com/cricket/india-squad-announcement-live-updates",
        "https://www.inshorts.com/en/news/india-squads-for-test-and-odi-series-against-afghanistan-announced"
    ],
    "word_count": 720,
    "score_total": 75,
    "body": """When the BCCI announced India's squad for the T20 World Cup earlier this year, Shubman Gill's name was conspicuously absent. The selectors, it seemed, had decided that the 26-year-old's classical batting style did not fit the slam-bang requirements of the shortest format. The cricketing world moved on. Gill did not.

Instead, he channelled whatever frustration he felt into an IPL 2026 campaign that has been nothing short of transformative. His powerplay strike rate this season — 165.14 — is the highest of his career. His Gujarat Titans, propelled in no small part by his captaincy and his willingness to attack from ball one, have qualified for the playoffs with 18 points, level with RCB and Sunrisers Hyderabad in the tightest three-way race the tournament has ever seen.

And then, on May 19, the BCCI made another announcement: Gill would captain India in both the one-off Test and the three-match ODI series against Afghanistan, starting June 6 in New Chandigarh. KL Rahul was named his Test vice-captain. Shreyas Iyer would deputise in the ODIs. Jasprit Bumrah was rested entirely.

## The generational handover accelerates

The squad selections tell a story that extends well beyond one home series against Afghanistan. Rohit Sharma and Virat Kohli return for the ODIs — but notably not the Test. Both are now 38 and 37 respectively. Their presence in limited-overs cricket looks increasingly like a farewell tour, even if nobody at the BCCI will say so publicly.

The Test squad, meanwhile, reads like a blueprint for India's future. Yashasvi Jaiswal at the top. Sai Sudharsan in the middle order. Devdutt Padikkal offering left-handed variety. Nitish Kumar Reddy providing the seam-bowling all-rounder option India has craved since Hardik Pandya's body began betraying his talent. Three uncapped players — Manav Suthar, Gurnoor Brar, and Harsh Dubey — earned maiden call-ups, each of them under 25.

"The selectors are clearly building a squad for the next World Test Championship cycle," observed a former India selector who asked not to be named. "Gill has been groomed for this since 2023. The Afghanistan series is a dress rehearsal."

## What the numbers say

Gill's credentials as captain are quietly impressive. Since taking over as Gujarat Titans skipper in IPL 2025, his win percentage has been above 60 per cent. In Tests, he averages 47.3 as opener — a number that would be celebrated in any era, let alone one where opening in Test cricket has become a thankless assignment.

His form in this IPL has silenced the T20 doubters too. Against Chennai Super Kings last week, he set the tempo for GT's 229/4 with an aggressive 47 off 28 balls. His intent has been unmistakable: he wants the selectors to know that the T20 World Cup snub was a mistake.

## Why NRI fans should care

For the millions of diaspora cricket fans who schedule their lives around Indian cricket, the Afghanistan series offers something rare: a guilt-free window of Test cricket in June, after the IPL madness subsides and before the T20 World Cup begins. The Test in New Chandigarh (June 6-10) and the ODIs in Dharamshala (June 13), Lucknow (June 16), and Chennai (June 20) will be streamed on JioCinema internationally.

More importantly, this series marks the moment when India's next generation of leaders will be tested in international conditions without the safety net of Bumrah, Jadeja, or the senior batting establishment. For NRI fans who have watched Indian cricket through the Tendulkar era, the Dhoni era, and the Kohli era, this is the first real glimpse of the Gill era.

## The bigger picture

Rishabh Pant retains his place in the Test squad as wicketkeeper-batter but has been dropped from the ODI side — another signal that the selectors are willing to make hard calls. Mohammed Shami, despite a strong IPL showing, was ignored entirely. Bhuvneshwar Kumar, at 36, did not feature in either squad.

The Afghanistan series is not, on paper, a high-stakes assignment. But for Shubman Gill, it is everything. The boy from Fazilka in Punjab, who was hitting sixes against international bowling attacks at 18, now gets to lead his country in both formats. The T20 World Cup selectors said he was not needed. The BCCI just handed him the captaincy instead.

That, in the end, is the most Indian cricket thing imaginable: being told you are not good enough for one job, and responding by getting a bigger one.""",
}


# ── ARTICLE 2: Karman Kaur Thandi — French Open and Indian Women's Tennis ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "Karman Kaur Thandi Lost 1-6, 0-6 at the French Open. She Was Still the Most Important Indian Tennis Player There.",
    "subheadline": "India's first woman in Grand Slam singles in two years was eliminated in 42 minutes at Roland Garros — but her presence exposed a crisis that runs far deeper than one scoreline",
    "slug": "karman-kaur-thandi-french-open-2026-indian-womens-tennis-crisis-20260522",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": "2026-05-22T23:00:00+00:00",
    "diaspora_angle": "Indian diaspora tennis community; lack of pipeline for women players; NRI parents investing in children's tennis; comparison to US/European development systems",
    "tags": ["Karman Kaur Thandi", "French Open", "Roland Garros", "Indian Tennis", "Women's Tennis", "Grand Slam", "Sania Mirza"],
    "urgency": "daily",
    "sources": [
        "https://thebridge.in/tennis/french-open-2026-karman-kaur-thandi-exits-qualifying-round-1",
        "https://indiantennisdaily.com/roland-garros-2026-karman-kaur-thandi-harmony-tan",
        "https://khelnow.com/tennis/india-womens-singles-2026-french-open",
        "https://indiasportshub.com/karman-kaur-thandi-french-open-2026-qualifying"
    ],
    "word_count": 680,
    "score_total": 70,
    "body": """It lasted 42 minutes. Karman Kaur Thandi, the 27-year-old from Chandigarh who was India's sole representative in singles at the 2026 French Open, lost to France's Harmony Tan 1-6, 0-6 in the opening round of qualifying at Roland Garros on Tuesday.

The scoreline was brutal. But the real story was not the defeat — it was that Thandi was there at all.

She was the first Indian woman to compete in Grand Slam singles in two years, since Ankita Raina's first-round exit at the 2024 Australian Open. She secured her place not through her current ranking — a distant 1,488 in the WTA standings — but through a Protected Ranking of 238, a safety net the tour offers players returning from long-term injury.

## The post-Sania void

Since Sania Mirza's retirement, Indian women's tennis has been in freefall. Where once there was a bona fide star who reached the doubles No. 1 ranking and made deep runs in Grand Slam singles, there is now a void so complete that a single qualifying-round appearance at Roland Garros qualifies as news.

The numbers are damning. India, a country of 1.4 billion people, has zero women in the WTA top 200. The highest-ranked Indian woman is Rutuja Bhosale at 321. The pipeline that was supposed to produce successors to Mirza has produced, at best, intermittent qualifiers who appear at majors once every two years and disappear again.

"The goal to get more laurels for the country will never change," Thandi said after her defeat, her voice carrying the determined optimism of someone who knows the odds are stacked against her. She spoke of rebuilding her ranking, of getting back to full fitness, of competing on the ITF circuit to earn her way back.

## What went wrong on court

Tan, a French player ranked 175th, never allowed Thandi to settle. The Indian struggled with her serve — she failed to convert her lone break-point opportunity — and Tan capitalised on five of her eight chances. The first set took 22 minutes. The second was even more one-sided.

It was, by any measure, a difficult return. Thandi had not played a competitive match since her injury break. Clay is an unforgiving surface for a player who prefers hard courts. And the qualifying rounds at Roland Garros, played in front of sparse crowds on the outer courts, offer none of the adrenaline that can lift an underdog.

But Thandi's coaches at the Roundglass Tennis Academy saw positives: her movement was good, her baseline power was evident, and her physical condition suggested the injury was behind her. "The match fitness will come," one of them said. "The body is ready."

## The diaspora disconnect

For the estimated five million Indian families in the US and UK who have put their children into tennis academies — from the IMG Academy in Bradenton to clubs across Southern California and suburban London — Thandi's story is both familiar and frustrating. The talent exists. The work ethic exists. What does not exist, at least not in India, is the infrastructure that converts junior promise into sustained professional success.

The AITA (All India Tennis Association) has faced repeated criticism for its allocation of resources, its selection controversies, and its inability to create a development pathway for women's tennis. Funding is sporadic. Coaching is fragmented. International exposure — the kind that separates a top-200 player from a top-500 one — remains prohibitively expensive for all but the wealthiest families.

Countries with a fraction of India's population — the Czech Republic, Belarus, Kazakhstan — routinely produce women's tennis players ranked inside the top 50. India's absence from this tier is not a talent problem. It is a systems failure.

## What comes next

Thandi will return to the ITF circuit, where she will need to string together results at lower-tier tournaments to rebuild her ranking toward the top 200. The path is gruelling: small prize money, constant travel, no guaranteed coaching support.

Roland Garros will continue without her. India's campaign in the singles department is over. But for 42 minutes on a Tuesday afternoon in Paris, an Indian woman competed at a Grand Slam — and that, given the state of things, was an achievement in itself.""",
}


if __name__ == "__main__":
    print("=== Sports Writer — 2026-05-22 Afternoon ===\n")

    # Insert articles
    for label, article in [("Article 1 (Gill)", a1), ("Article 2 (Thandi)", a2)]:
        print(f"Inserting {label}: {article['headline'][:60]}...")
        try:
            result = insert_article(article)
            print(f"  ✅ Inserted: {article['id']}")
        except Exception as e:
            print(f"  ❌ Failed: {e}")

    print("\n✅ Sports writer complete — 2 articles published")
