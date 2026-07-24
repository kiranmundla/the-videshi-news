#!/usr/bin/env python3
"""Sports writer — 2026-05-24 11:00 PDT run: 2 articles + score decay + IPL standings refresh."""

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


def fetch_image(query: str, dest_path: str) -> bool:
    pexels_key = ""
    try:
        with open(os.path.expanduser("~/workspace/.env.pexels")) as f:
            for line in f:
                if line.startswith("PEXELS_API_KEY="):
                    pexels_key = line.strip().split("=", 1)[1].strip('"').strip("'")
    except Exception:
        pass
    if not pexels_key:
        print("  WARN: No Pexels key found")
        return False
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": pexels_key},
            params={"query": query, "per_page": 1, "orientation": "landscape"},
            timeout=15,
        )
        if r.status_code == 200 and r.json().get("photos"):
            img_url = r.json()["photos"][0]["src"]["large2x"]
            img_r = requests.get(img_url, timeout=30)
            if img_r.status_code == 200:
                with open(dest_path, "wb") as f:
                    f.write(img_r.content)
                print(f"  Image downloaded: {dest_path}")
                return True
    except Exception as e:
        print(f"  WARN: Pexels fetch failed: {e}")
    return False


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
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=18)).isoformat().replace("+00:00", "Z")
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


# ── ARTICLE 1: PBKS Eliminated Despite Winning Their Last Match ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Shreyas Iyer Scored His First IPL Century on Saturday Night. On Sunday Afternoon, Punjab Kings Were Eliminated Anyway.",
    "subheadline": "Punjab Kings won their final league match. They ended the season on 15 points from 14 games, with seven wins, six losses, and one no-result. It was not enough. Rajasthan Royals' 30-run victory over Mumbai Indians at the Wankhede Stadium on Sunday took the Royals to 16 points and sent Punjab home. For a franchise that has never won the IPL in 18 seasons, the cruelty was not new. The timing was.",
    "slug": "punjab-kings-eliminated-ipl-2026-playoffs-shreyas-iyer-century-not-enough-rr-qualify-20260524",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Punjab Kings are the IPL franchise most deeply tied to the Punjabi diaspora. The team's identity — its name, its fan base, the cultural DNA of its support — maps directly onto the global Sikh and Punjabi community that stretches from Brampton to Southall to Fremont. When PBKS play well, Punjabi WhatsApp groups in Canada and the UK light up. When they lose, the jokes arrive before the scorecard is final. This elimination is particularly cruel for NRI fans because it happened while they were watching. Shreyas Iyer's century on Saturday night was a rare moment of uncomplicated joy for a fan base conditioned to expect disappointment. Many NRI fans would have gone to bed on Saturday thinking their team had done enough. They woke up on Sunday to find out that doing enough is never enough for Punjab Kings. The parallel to the immigrant experience — work harder than everyone, produce results, and still watch someone else get the opportunity — is one PBKS fans don't need spelled out.",
    "tags": ["Punjab Kings", "PBKS", "IPL 2026", "Shreyas Iyer", "Rajasthan Royals", "Playoffs", "IPL Heartbreak", "Prabhsimran Singh", "Wankhede Stadium", "Mumbai Indians"],
    "urgency": "daily",
    "sources": [
        "https://cricketaddictor.com/ipl-2026-playoffs-race-rr-kkr-and-pbks-qualification-scenarios-explained/",
        "https://inshorts.com/en/news/rr-seal-final-ipl-2026-playoff-spot-pbks-and-kkr-eliminated",
        "https://crictracker.com/news/just-hoping-to-support-mi-shreyas-iyer-backs-five-time-champions-to-beat-rr-to-boost-pbks-chances-of-qualification/",
        "https://thesportstak.com/cricket/shreyas-iyer-maiden-ipl-hundred-keeps-pbks-alive/"
    ],
    "word_count": 780,
    "score_total": 70,
    "body": """On Saturday evening in Lucknow, Shreyas Iyer played the innings of his IPL career. An unbeaten 101 off 51 balls — 11 fours, five sixes — that chased down 197 with seven wickets in hand and two overs to spare. It ended a six-match losing streak. It kept Punjab Kings alive in the playoff race. It was his first century in nine years of IPL cricket, and he hit the winning six to get there.

Twenty hours later, Punjab Kings were eliminated from the tournament.

## How 15 points became not enough

The arithmetic was straightforward. Punjab Kings finished the league stage on 15 points from 14 matches — seven wins, six losses, and one no-result. Before Sunday's matches, they sat fourth on the table, needing just one of two results to go their way: either Rajasthan Royals losing to Mumbai Indians at the Wankhede, or Kolkata Knight Riders failing to overhaul Delhi Capitals at Eden Gardens.

Neither result came. RR beat MI by 30 runs. DC beat KKR by 40 runs. Rajasthan's victory took them to 16 points and the fourth playoff spot. Punjab, at 15, were out.

The mechanism of elimination was almost designed for maximum pain. PBKS had finished their campaign. They could not play another ball. Their fate was in the hands of a Mumbai Indians team that had won just four matches all season and had nothing to play for. Iyer, speaking after Saturday's win, had said from his hometown Mumbai: "Just hoping to support MI."

Mumbai did not support them.

## The anatomy of a cruel exit

Iyer's century was not a standalone moment of brilliance. It was the crescendo of a turbulent season that encapsulated everything Punjab Kings have been for 18 years: good enough to hope, never quite good enough to qualify without needing favours.

They started the tournament well. Then they lost six consecutive matches — a slide so severe that the dressing room, by Brad Haddin's admission, was questioning itself. The losing streak dropped them from third to the edge of elimination.

Then came Lucknow. Prabhsimran Singh scored 69 off 39 at the top to give PBKS the platform, surviving a dropped catch by Rishabh Pant on 20 and making LSG pay. When Prabhsimran fell with 35 still needed, Iyer took charge. He attacked Mohammed Shami for three sixes in an over. He brought up his century with the shot that won the match.

The problem with fairytale innings is that they don't control what happens next.

## The broader pattern

This is not a new story for Punjab Kings. The franchise formerly known as Kings XI Punjab has never won the IPL. Not in 2008, when the tournament began. Not in 2014, when they finished as runners-up under George Bailey. Not in any of the 18 seasons since.

They have come close repeatedly. In 2014, they lost the final. In 2020, they lost five matches by the narrowest of margins — including a Super Over and a short-run controversy — and missed the playoffs. In 2024, they rebuilt from scratch with a record mega-auction spend, hired Iyer as captain, and failed to qualify.

This year, they spent over ₹110 crore on their squad and produced moments of genuine quality. Iyer's 498 runs this season placed him among the top run-scorers. Prabhsimran Singh became the first uncapped Indian to score 500-plus runs in two separate IPL seasons. The bowling had its days. The talent was undeniable.

The consistency was not. Six consecutive defeats in the middle of the season is not a blip — it is a structural failure that no single century can repair, no matter how spectacular.

## What stays and what changes

Punjab Kings will enter the 2027 season with the same questions they have carried into every season for nearly two decades. The squad has pieces. Iyer, if retained, gives them a captain who has now proven he can produce under the most extreme pressure. Prabhsimran gives them an opener who deserves an India cap. The overseas slots need work. The bowling lacks a reliable death option.

But those are technical assessments, and technical assessments do not capture what Sunday felt like. What Sunday felt like was this: a franchise did everything it could on a Saturday night, and then sat on a couch on Sunday afternoon and watched someone else take their place.

## What the numbers say

The final league standings tell the story in a single line:

| Team | P | W | L | NR | Pts |
|------|---|---|---|----|----|
| RCB | 14 | 9 | 5 | 0 | 18 |
| GT | 14 | 9 | 5 | 0 | 18 |
| SRH | 14 | 9 | 5 | 0 | 18 |
| **RR** | **14** | **8** | **6** | **0** | **16** |
| PBKS | 14 | 7 | 6 | 1 | 15 |

One point. One win. The distance between playing in the Eliminator and watching the Eliminator from home.

The IPL 2026 playoffs begin on Tuesday with RCB vs Gujarat Titans in Qualifier 1 at Dharamsala. On Wednesday, Sunrisers Hyderabad face Rajasthan Royals in the Eliminator at New Chandigarh. Punjab Kings will watch both matches. They will have opinions. They will have regrets. They will have a six-match losing streak and one magnificent century, and neither will matter anymore.""",
}


# ── ARTICLE 2: Mumbai Indians' Worst Season — 4 Wins, 10 Losses ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "Mumbai Indians Have Five IPL Titles, Four World Cup Winners in Their Squad, and Just Finished With Four Wins and Ten Losses.",
    "subheadline": "Rohit Sharma was dismissed for a duck in his final match of the season. Suryakumar Yadav fought alone with 60 off 42 in a losing cause. Jasprit Bumrah missed most of the tournament. Hardik Pandya's captaincy produced the franchise's joint-worst record in 18 seasons. Mumbai Indians finished ninth in IPL 2026 — the same team that won the title five times in seven years.",
    "slug": "mumbai-indians-ipl-2026-worst-season-four-wins-ten-losses-rohit-sharma-duck-hardik-pandya-20260524",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Mumbai Indians are the IPL's most globally followed franchise, and for the Indian diaspora that connection runs deeper than cricket. MI is the team NRI fans default to in sports bars from Edison to Hounslow to Scarborough. Rohit Sharma is the player whose highlights are shared in family WhatsApp groups before anyone asks. For diaspora cricket fans who set 4 AM alarms in US time zones to watch IPL matches, this season has been a test of loyalty. MI's collapse from five-time champions to a team that wins four games in an entire campaign is the kind of decline that forces NRI fans to confront a question they rarely face: how long do you keep watching? The franchise's global brand — built on Rohit's elegance, Bumrah's hostility, and a decade of winning — is intact in jerseys and merchandise but increasingly disconnected from what is happening on the pitch. For the Indian-origin kid in New Jersey who chose MI as their team because everyone in the family did, this season offered no reward. Suryakumar Yadav's lone 60 on the final day was the closest thing to a highlight in a campaign defined by collapse, injury, and the uncomfortable question of whether the dynasty is over.",
    "tags": ["Mumbai Indians", "IPL 2026", "Rohit Sharma", "Hardik Pandya", "Suryakumar Yadav", "Jasprit Bumrah", "Wankhede Stadium", "IPL Dynasty", "MI Season Review", "Cricket"],
    "urgency": "daily",
    "sources": [
        "https://mykhel.com/cricket/mumbai-indians-coach-jayawardene-ipl-2026-exit-rohit-sharma-fitness/",
        "https://thesportstak.com/cricket/mi-announce-replacements-quinton-de-kock-rr-ipl-2026/",
        "https://crictracker.com/live-scores/mi-vs-rr-match-69-t20-indian-premier-league-24-may-2026/full-scorecard/",
        "https://ianslive.in/ipl-2026-bumrah-rohit-injuries-mi-jayawardene/"
    ],
    "word_count": 750,
    "score_total": 62,
    "body": """On Sunday afternoon at the Wankhede Stadium, Jofra Archer dismissed Rohit Sharma for a duck. It was the fourth ball of the match. Rohit edged behind to Dhruv Jurel. He walked back to the pavilion, unclipped his helmet, and sat down. The Wankhede was quiet.

It was Mumbai Indians' last match of the IPL 2026 league stage, and it ended the way much of their season had: in defeat. Rajasthan Royals scored 205 for 8, MI managed 175 for 9, and the 30-run loss sealed a campaign that will rank alongside 2022 as the worst in the franchise's 18-year history.

Four wins. Ten losses. Ninth place in a ten-team league. The five-time champions have become the team other teams use to climb the table.

## The numbers that define a disaster

Mumbai Indians finished with eight points from 14 matches. They were eliminated from playoff contention weeks before the season ended. Their net run rate of -0.510 told a story of matches lost by margins too wide to excuse as bad luck.

Rohit Sharma, their most decorated player and arguably the greatest T20 batter in history, played just eight matches. A hamstring injury kept him out of several games. In the matches he did play, he scored 283 runs at an average of 40 — respectable numbers that masked the fact that he was frequently used as an impact substitute rather than a fixture in the starting eleven. His final act of the season was that duck against Archer.

Jasprit Bumrah, the bowler who makes MI's attack world-class, did not get enough recovery time after India's T20 World Cup campaign, according to coach Mahela Jayawardene. His absence for large stretches of the tournament left MI's bowling attack without its primary weapon, and the results were visible in powerplay after powerplay where opposition batters scored freely.

Hardik Pandya, the captain, had a mixed season with bat and ball. On Sunday he scored 34 off 15 balls — a cameo that briefly threatened to make the chase interesting before Archer had him caught at the boundary. But isolated cameos do not compensate for ten losses.

## One man's fight

The only genuinely bright spot on Sunday was Suryakumar Yadav. Walking in at 12 for 3 after MI's top order had been dismantled by Archer's opening spell, Yadav played the kind of innings that reminded everyone why he is one of the world's best T20 batters.

He scored 60 off 42 balls — three fours, four sixes — on a pitch where the rest of MI's batting lineup collectively failed to build sustained pressure. When Nandre Burger finally dismissed him with a brilliant caught and bowled, MI were effectively done. Yadav's dismissal at 17.3 overs left the tail with too much to do and too few overs to do it in.

Will Jacks provided some entertainment with 33 off 18, and Pandya's 34 off 15 added late fireworks. But the damage had been done in the first three overs, when Archer removed Rohit, Naman Dhir, and sent Rickelton back to the pavilion via Burger, reducing MI to 12 for 3.

## Jayawardene's post-mortem

Head coach Mahela Jayawardene's assessment before the match had been blunt. MI's players, he said, had "failed to turn talent into performances, both individually and as a unit." The squad included four members of India's 2024 T20 World Cup-winning team. None of them could arrest the slide.

The injury list compounded the problems. Quinton de Kock and Raj Angad Bawa were both ruled out during the tournament, replaced by Mahipal Lomror and Ruchit Ahir. Rohit's hamstring issues limited his availability. Bumrah's workload management meant he was either absent or underpowered.

But injuries are explanations, not excuses. Every IPL team deals with injuries. Not every IPL team loses ten matches.

## The dynasty question

Mumbai Indians won five IPL titles between 2013 and 2020. That run of dominance — five championships in eight years — is the benchmark against which every IPL dynasty is measured. Since 2020, they have won one title (2024, under different circumstances) and produced two seasons of four wins and ten losses.

The 2022 campaign was supposed to be the anomaly — the one bad season in an otherwise excellent decade. The 2026 season suggests it might have been the preview. The mega-auction rebuild that brought in Pandya as captain and reshuffled the squad around a core of Rohit, Yadav, and Bumrah has not produced the returns MI expected.

The franchise's wealth, brand, and scouting infrastructure remain among the best in cricket. Their ability to attract talent in the transfer market is unmatched. But talent without health, form, and cohesion produces eight points and a long summer of questions.

## What comes next

MI's immediate future involves watching the IPL 2026 playoffs from the outside. RCB face Gujarat Titans in Qualifier 1 at Dharamsala on Tuesday. Sunrisers Hyderabad face Rajasthan Royals in the Eliminator on Wednesday. The final is in Ahmedabad on May 31.

For Mumbai Indians, the offseason will be defined by decisions. Does Pandya continue as captain? Can Bumrah be managed to full fitness? Will Rohit, approaching his late thirties, remain a starter or transition into an elder statesman role? And can a franchise built on winning deal with the unfamiliar experience of irrelevance?

Four wins. Ten losses. The Wankhede was quiet when Rohit walked back on Sunday. It may stay quiet for a while.""",
}


if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-24 11:00 PDT")
    print("=" * 60)

    # Check for duplicate slugs first
    for slug in [a1["slug"], a2["slug"]]:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id",
            headers=HEADERS,
        )
        if r.status_code == 200 and r.json():
            print(f"  SKIP: slug already exists: {slug}")
            sys.exit(0)

    print("\nInserting Article 1: PBKS Eliminated Despite Winning...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    img1_path = f"/tmp/{a1_id}.jpg"
    if fetch_image("cricket team disappointed dugout stadium IPL", img1_path):
        img1_url = upload_image(a1_id, img1_path)
        if img1_url:
            update_image_url(a1_id, img1_url)

    print("\nInserting Article 2: Mumbai Indians Worst Season...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    img2_path = f"/tmp/{a2_id}.jpg"
    if fetch_image("empty cricket stadium night lights Mumbai", img2_path):
        img2_url = upload_image(a2_id, img2_path)
        if img2_url:
            update_image_url(a2_id, img2_url)

    # Score decay
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    print(f"\nDone. 2 articles published.")
    print(f"  IDs: {a1_id}, {a2_id}")
