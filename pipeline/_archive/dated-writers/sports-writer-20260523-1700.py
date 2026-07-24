#!/usr/bin/env python3
"""Sports writer — 2026-05-23 17:00 PDT run: 2 articles + score decay."""

import os, json, uuid, requests, subprocess, sys
from datetime import datetime, timezone, timedelta

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
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers=HEADERS,
        json={"image_url": image_url},
    )
    print(f"  Image URL patch: {r.status_code}")

def decay_scores():
    """Decay score_total by 5 for articles published > 18h ago, flooring at 0."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=18)).isoformat()
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&published_at=lt.{cutoff}&score_total=gt.0&select=id,score_total",
        headers={**HEADERS, "Prefer": "return=representation"},
    )
    if r.status_code >= 400:
        print(f"  Decay fetch error: {r.status_code}")
        return 0
    articles = r.json()
    count = 0
    for a in articles:
        new_score = max(0, a["score_total"] - 5)
        rp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{a['id']}",
            headers=HEADERS,
            json={"score_total": new_score},
        )
        if rp.status_code < 400:
            count += 1
    return count

# ── ARTICLE 1: Federation Cup Day 2 — Record-shattering Saturday ──────────────
a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Three National Records. One Afternoon. Ranchi Just Produced the Greatest Day in Indian Athletics History.",
    "subheadline": "Gurindervir Singh ran 10.09 seconds to become the fastest Indian ever. Vishal TK broke the sub-45 barrier in the 400 metres. Tejaswin Shankar crossed 8,000 points in the decathlon. All three happened at the Federation Cup on a single Saturday afternoon in Ranchi, and all three are headed to Glasgow.",
    "slug": "federation-cup-2026-day-2-gurindervir-10-09-vishal-tk-sub-45-tejaswin-8057-ranchi-20260523",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Gurindervir Singh's 10.09 will trend in every Indian WhatsApp group worldwide — India has never been taken seriously as a sprinting nation, and this time puts the country second in Asia this season; diaspora sports fans who follow athletics through the Commonwealth Games finally have a medal contender in the glamour event; Tejaswin Shankar trained at Kansas State University and is among the most prominent US-trained Indian athletes in Olympic-adjacent sports; the CWG qualification stories resonate with NRI communities in the UK, where Glasgow 2026 will draw significant Indian diaspora attendance",
    "tags": ["Gurindervir Singh", "Vishal TK", "Tejaswin Shankar", "Federation Cup 2026", "National Record", "100m Sprint", "400m", "Decathlon", "Commonwealth Games 2026", "Glasgow", "Ranchi", "Animesh Kujur", "Indian Athletics", "Birsa Munda Stadium"],
    "urgency": "breaking",
    "sources": [
        "https://mykhel.com/cricket/federation-cup-2026-live-gurindervir-10-09-vishal-sub-45-tejaswin-8057",
        "https://inshorts.com/en/news/25yearold-gurindervir-singh-becomes-indias-fastest-man-runs-100m-in-1009-seconds",
        "https://devdiscourse.com/article/sports-games/gurindervir-snatches-100m-national-record",
        "https://inshorts.com/en/news/vishal-tk-becomes-1st-indian-to-clock-under-45-seconds-in-400m",
        "https://inshorts.com/en/news/tejaswin-shankar-becomes-1st-indian-ever-to-cross-8000-points-in-decathlon"
    ],
    "word_count": 750,
    "score_total": 74,
    "body": """Something happened at the Birsa Munda Stadium in Ranchi on Saturday afternoon that Indian athletics has been waiting decades to witness. Three national records fell. Three athletes produced the single best performances of their lives. And all three did it within two hours of each other, on the same track, in the same sweltering Jharkhand heat.

This was the Federation Cup 2026, Day 2. It was supposed to be a routine Commonwealth Games qualifier. It turned into the most significant day in the history of Indian track and field.

## The fastest Indian who ever lived

Gurindervir Singh lined up for the men's 100-metre final knowing that his rival, Animesh Kujur, had stolen the national record from him just twenty-four hours earlier. Kujur ran 10.15 seconds in Friday's semi-final, snatching the mark that Gurindervir had briefly held at 10.17. The Punjab sprinter had slept on that knowledge for one night.

On Saturday evening, he answered it with 10.09 seconds.

Ten-point-zero-nine. The first time an Indian has broken the 10.10-second barrier. The second fastest time by any Asian sprinter this season, behind only Japan's 19-year-old prodigy Fukuto Komuro, who ran 10.08 in May. Gurindervir, 25, from Jalandhar — a city known for producing hockey players and kabaddi wrestlers, not sprinters — comfortably breached the Commonwealth Games qualification standard of 10.16 seconds.

Kujur, the man who had held the record for less than 24 hours, managed only 10.20 in the final. The drama of their rivalry — record set, record broken, record reclaimed, all within a single Friday-Saturday cycle — is the kind of narrative that Indian athletics has never generated before.

"Indian genes tagde hain," Gurindervir told reporters, grinning — a Punjabi phrase that roughly translates to "Indian genes are strong enough." It was a pointed response to the decades-old assumption that Indians simply cannot sprint.

## The sub-45 barrier, shattered

Thirty minutes after Gurindervir's run, Vishal TK walked to the starting blocks for the men's 400-metre final. The 22-year-old from Tamil Nadu held the national record of 45.12 seconds, set at the Inter-State Championships in Chennai last year. No Indian had ever broken the 45-second barrier.

Vishal ran 44.98.

The first Indian sub-45. The best 400-metre time in Asia this season. A national record by fourteen hundredths of a second — an eternity in a one-lap sprint.

And then the cruelest detail: the Commonwealth Games qualification standard for the 400 metres is 44.96 seconds. Vishal missed it by two hundredths of a second. 0.02. The time it takes to blink. He broke a barrier that generations of Indian quartermilers had failed to breach, and it was not quite enough for Glasgow.

He will almost certainly get another chance at the Asian Championships later this summer, and 44.98 is the kind of time that suggests 44.90 is not far away. But the fact that his historic run — the fastest 400 metres ever run by an Indian — came with a footnote of heartbreak rather than celebration tells you something about how razor-thin the margins are at this level.

## The 8,000-point man

The decathlon is the loneliest event in athletics. Ten disciplines across two days, with no crowd energy between events and no rivals visible on the scoreboard until the final 1,500 metres. Tejaswin Shankar, 26, had been grinding through it since Friday morning.

By Saturday afternoon, when the final event concluded, Shankar had accumulated 8,057 points. No Indian decathlete had ever crossed 8,000. The previous national record — also his — was 7,826, set in 2025. He improved it by 231 points in a single competition.

Shankar's story is particularly resonant for the diaspora. He trained at Kansas State University, competed in the NCAA, and returned to India to pursue multi-event athletics at a time when most Indian athletes with American training backgrounds were gravitating toward more commercially viable sports. He won a high jump bronze at the 2022 Commonwealth Games in Birmingham and has since reinvented himself as a decathlete — a transition that requires learning four entirely new disciplines.

His 8,057 cleared the Commonwealth Games qualification standard comfortably. He is going to Glasgow.

## What it means

Three athletes. Three national records. Three barrier-breaking performances. All on the same afternoon, at the same stadium, in a city that most Indian sports fans associate with MS Dhoni rather than track and field.

The Federation Cup has historically been a mid-tier domestic meet, a box-ticking exercise for athletes trying to qualify for international competitions. What happened on Saturday in Ranchi — Gurindervir's sub-10.10, Vishal's sub-45, Tejaswin's 8,000-plus — was not box-ticking. It was a collective breakthrough.

India sends athletes to the Commonwealth Games every four years with modest expectations: a medal in javelin if Neeraj Chopra is healthy, perhaps something in wrestling or boxing, nothing in the track events that define the sport globally. Glasgow 2026, which begins on July 23, may be different. For the first time, India is sending sprinters who are competitive by international standards, a quartermiler who has broken a barrier that stood for the entire history of Indian athletics, and a decathlete who can score with the best in the Commonwealth.

Saturday in Ranchi was the day Indian athletics stopped apologising for itself.""",
}

# ── ARTICLE 2: Bethell ruled out of IPL — RCB enter playoffs without overseas opener ──────────────
a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "RCB Finished Top of the Table. Now They Enter the Playoffs Without the Overseas Opener Who Got Them There.",
    "subheadline": "Jacob Bethell has been ruled out of IPL 2026 with a left ring finger injury and sent home to England. Phil Salt is recovering from his own finger problem. Royal Challengers Bengaluru, who finished first with 18 points, will face Gujarat Titans in Qualifier 1 on Monday with an opening partnership held together by duct tape.",
    "slug": "jacob-bethell-ruled-out-ipl-2026-rcb-playoffs-injury-finger-phil-salt-20260523",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "RCB have the largest NRI fanbase of any IPL franchise — their playoff fortunes are followed intensely in the US, UK, and Middle East; Bethell's return to England for Test preparation ties into the broader ECB-IPL tension that diaspora cricket fans debate endlessly; Virat Kohli's form in the playoffs without a settled opening partner will dominate Indian-American and British-Indian cricket conversations this week",
    "tags": ["Jacob Bethell", "RCB", "Royal Challengers Bengaluru", "IPL 2026", "Injury", "Phil Salt", "Venkatesh Iyer", "Qualifier 1", "Gujarat Titans", "Virat Kohli", "Rajat Patidar", "Michael Vaughan", "ECB", "England Test"],
    "urgency": "daily",
    "sources": [
        "https://cricketaddictor.com/ipl/jacob-bethell-ruled-out-rcb-opener-returns-to-england",
        "https://khelnow.com/cricket/ipl/jacob-bethell-ruled-out-ipl-2026-rcb-blow",
        "https://mykhel.com/cricket/ipl-2026-rcb-player-ruled-out-finger-injury-playoffs",
        "https://insidesport.in/cricket/phil-salt-injured-jacob-bethell-ruled-out-rcb-pickle-ipl-2026-playoffs",
        "https://inshorts.com/en/news/rcbs-jacob-bethell-to-return-to-england-after-finger-injury"
    ],
    "word_count": 680,
    "score_total": 67,
    "body": """Royal Challengers Bengaluru have done something only three other teams in IPL history have managed: finish the league stage in first place despite losing their final match. They won nine of fourteen games. Their net run rate of +0.783 was the best in the tournament. They qualified for the playoffs before the final weekend even began.

And now, three days before the most important match of their season, their overseas opening batsman has been sent home with a broken finger.

## What happened

Jacob Bethell sustained an injury to his left ring finger during RCB's match against Punjab Kings earlier this week. The 22-year-old English all-rounder, who had scored 163 runs across nine matches this season, was ruled out of Thursday's final league game against Sunrisers Hyderabad.

On Saturday, RCB confirmed the worst. Bethell will not play in the playoffs. He is returning to England, where the ECB's medical team will assess whether he is fit for the first Test against New Zealand, which begins at Lord's on June 4.

"Jacob Bethell has sustained an injury to his left ring finger during Royal Challengers Bengaluru's match against Punjab Kings," the franchise said in a statement. "Following medical assessment, Jacob will return to England for further evaluation ahead of England's upcoming Test series."

Michael Vaughan, the former England captain, had already been public about what he thought should happen. "He should be on the next plane home to England," Vaughan said on commentary. "Baz McCullum arrives in the UK on Sunday morning. The training camp starts Monday. Bethell should be back."

## The Phil Salt complication

Bethell's departure would be manageable if RCB had their other overseas opener available. They do not — at least not fully. Phil Salt, who was the first-choice opener before Bethell replaced him, has been nursing his own finger injury. Salt was rested for the SRH match as a precaution and is expected to return for Qualifier 1, but "expected" is doing significant work in that sentence.

RCB's depth at the top of the order is suddenly paper-thin. Against Hyderabad on Thursday, Venkatesh Iyer was promoted to open alongside Virat Kohli and scored a blazing 44 off 19 balls. It was an entertaining innings, but Venkatesh Iyer is a middle-order batter who was improvising, not an opener executing a role he has trained for.

If Salt is fit, he walks back into the XI and the problem is solved — at least for the top of the order. If Salt is not fit, Rajat Patidar, who returned to the team for the SRH game and captained the side to a 200/4 total (56 off 39 balls), may need to move up, which reshuffles the entire middle order in a knockout match.

## The broader tension

Bethell's situation highlights a friction that has simmered beneath the IPL for years: English cricket's schedule and the IPL's playoff timing are fundamentally incompatible. The IPL playoffs run through the last week of May. England's Test summer begins in the first week of June. For English players in IPL playoff teams, there is a ten-day window between the IPL final and the first Test in which they are supposed to switch formats, fly home, decompress, and prepare.

For a player with a finger injury, that window shrinks to nothing. Bethell's return is not just about RCB's Qualifier 1 — it is about whether he can hold a bat in time for Lord's. The ECB and the IPL franchise agreed, without apparent friction, that Bethell should leave. The ease of that agreement tells you where the priorities lie.

## What RCB have left

Even without Bethell, RCB remain the most balanced team in the tournament. Kohli is Kohli. Patidar has been their most consistent performer. Krunal Pandya scored an unbeaten 41 against SRH in a game that did not matter, which suggests his form is intact. Devdutt Padikkal is available as a top-order option.

Their bowling, led by Rasikh Salam Dar and Bhuvneshwar Kumar, was penetrating throughout the league stage. They have home-crowd advantage at virtually every ground they play at — the RCB travelling support is, by any measure, the most committed in the IPL.

But playoffs are won and lost in the first six overs. The powerplay is where the opening partnership sets the tone, where overseas batsmen earn their contracts, where the difference between a settled pair and a makeshift arrangement can be 30 runs. RCB finished first because their top order functioned. They enter the playoffs hoping it can function without the man who made it work.""",
}

if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-23 17:00 PDT")
    print("=" * 60)

    print("\nInserting Article 1: Federation Cup Day 2 — Record-shattering Saturday...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    print("\nInserting Article 2: Bethell ruled out of IPL playoffs...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    # Score decay
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    print(f"\nDone. 2 articles published (images pending).")
    print(f"  IDs: {a1_id}, {a2_id}")
