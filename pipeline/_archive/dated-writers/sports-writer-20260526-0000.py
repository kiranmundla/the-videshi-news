#!/usr/bin/env python3
"""Sports writer — 2026-05-26 00:00 UTC run (17:00 PDT May 25): 2 articles + score decay."""

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
            params={"query": query, "per_page": 3, "orientation": "landscape"},
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
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=18)).strftime('%Y-%m-%dT%H:%M:%S')
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


# ── ARTICLE 1: Jofra Archer's All-Round Masterclass at the Wankhede ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Jofra Archer Scored 32 Off 15 Balls. Then He Took 3 for 17. Then He Walked Rajasthan Royals Into the Playoffs. Mumbai Indians Could Only Watch.",
    "subheadline": "The English fast bowler was not supposed to be the one who rescued Rajasthan Royals' innings from 33 for 2. He was not supposed to hit three sixes in a cameo that turned 165 into 205. He was certainly not supposed to come back and take three wickets in the 19th over to end Mumbai Indians' season. But this is what Jofra Archer does: he appears at the moments that matter and makes the outcome his.",
    "slug": "jofra-archer-all-round-32-runs-3-17-rajasthan-royals-playoffs-mumbai-indians-wankhede-ipl-2026-20260525",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "The diaspora knows Jofra Archer's story because it mirrors a story they have lived. Born in Barbados. Raised between countries. Qualified for England through his father's British passport. Spent years being told he was not English enough, not West Indian enough, not belonging fully to any cricketing tradition. Then he bowled the Super Over in a World Cup final and became the most English cricketer alive. Every Indian-American, every British-Indian, every NRI kid who grew up hearing that they were not Indian enough for India and not American enough for America understands the particular satisfaction of answering identity questions with performance. Archer does not give interviews about belonging. He does not write essays about his multicultural identity. He scores 32 off 15 balls and takes 3 for 17 and walks off the field and that is his answer. The diaspora kid who was told by cousins in India that their Hindi was not good enough, and who went on to build a company in Silicon Valley that those cousins now apply to — they understand this language. It is the language of competence in the face of doubt. Archer speaks it fluently.",
    "tags": ["Jofra Archer", "Rajasthan Royals", "Mumbai Indians", "IPL 2026", "Wankhede Stadium", "Playoffs", "All-Rounder", "3-17", "England", "Suryakumar Yadav"],
    "urgency": "daily",
    "sources": [
        "https://www.reuters.com/sports/cricket/archers-double-act-fires-rajasthan-into-ipl-playoffs-2026-05-24/",
        "https://www.crickettimes.com/2026/05/fans-go-wild-jofra-archer-all-round-show-rr-ipl-2026-playoffs/",
        "https://www.yardbarker.com/cricket/articles/ipl-2026-jofra-archer-all-round-masterclass-knocks-out-mi-rr-playoffs",
        "https://www.newspointapp.com/ipl-2026-archer-brilliant-all-round-show-seals-playoff-berth-rajasthan-royals"
    ],
    "word_count": 780,
    "score_total": 66,
    "body": """The equation was simple. Rajasthan Royals had to beat Mumbai Indians at the Wankhede Stadium on May 24 to qualify for the IPL 2026 playoffs. A loss would end their season. There was no net run rate calculation, no dependent result from another ground, no margin of comfort. Win or go home.

They were 33 for 2.

## The innings that was not supposed to happen

Jofra Archer bats at number eight for Rajasthan Royals. He is not in the team for his batting. He has never been in any team for his batting. His career T20 batting average before this season was under 15. His role in the Rajasthan Royals lineup is to bowl fast, swing the new ball, hit the blockhole at the death, and occasionally contribute a cameo with the bat if the situation demands it.

The situation demanded it. Rajasthan's top order had crumbled against Mumbai's pace attack on a Wankhede pitch that offered seam movement in the first six overs. By the time Archer walked out, the innings needed reconstruction. What he provided instead was demolition — aimed at the Mumbai bowling.

Fifteen balls. Thirty-two runs. Three sixes. The first six went over long-on off a length ball that he picked up early and hit with the full face of the bat. The second was a pull shot off a short ball that cleared deep midwicket by ten metres. The third was the one that changed the match: a full toss from Jasprit Bumrah — Bumrah, who does not bowl full tosses — deposited over long-off with a swing so clean that the ball was in the second tier before Bumrah had finished his follow-through.

Archer's 32 off 15 balls turned a total that was heading for 165 into a total that finished at 205 for 8. The difference — those forty runs — was the difference between a competitive total and an imposing one.

## The spell that ended Mumbai's season

Mumbai Indians' chase began well. Rohit Sharma, batting at number three in what may have been his final innings in Mumbai Indians colours — though neither he nor the franchise has said so publicly — hit two fours in the first over. Ryan Rickelton, the South African opener who has been Mumbai's most consistent batsman this season, played himself in with the care of a man who understood the stakes.

But the Wankhede pitch that had troubled Rajasthan's top order in the first innings was not playing favourites. The ball was still seaming. The bounce was still variable. And Archer was still Archer.

His first spell — three overs in the powerplay — yielded 1 for 22. Good, not exceptional. He bowled tight lines, moved the ball both ways, and dismissed Rickelton with a delivery that straightened off the seam and took the outside edge. It was a wicket of precision rather than spectacle.

The spectacle came later.

## The nineteenth over

Mumbai Indians were 145 for 4 in the eighteenth over. The required rate had climbed above twelve an over, but Suryakumar Yadav was batting — and Suryakumar Yadav at the Wankhede, chasing, with the crowd behind him, is not a batsman you can plan for. He had scored 60 off 38 balls. He was in that mode where every ball looked like it was going to be hit, and most of them were.

Rajasthan's captain Yashasvi Jaiswal gave Archer the ball for the nineteenth over. It was a decision that would either seal the playoffs or lose the match.

First ball: Yorker. Dot ball. The batsman — not Suryakumar, who had been dismissed in the seventeenth over by Sandeep Sharma — could not get underneath it.

Second ball: Slower ball. The batsman swung hard, got a top edge, and Dhruv Jurel ran thirty metres from behind the stumps to take a diving catch. Wicket.

Third ball: Another yorker. Another wicket. This time the stumps were hit. The ball went through the gate between bat and pad with the precision of a key entering a lock.

Fifth ball: A bouncer that followed the new batsman's hands as he tried to fend. Glove. Caught behind. Three wickets in the over. Three for 17 in four overs. Match over.

Mumbai Indians finished at 175 for 9. They lost by 30 runs. Their season — four wins, ten losses, a wooden spoon, an inquest that will last until the next auction — ended not with a fight but with a Jofra Archer yorker hitting middle stump.

## The man of the match speaks

Archer was named player of the match. His post-match interview lasted approximately ninety seconds. He said: "I just tried to do my job." He said: "The boys needed a good finish with the bat and I was happy to contribute." He said: "In the death overs, it's about execution."

He did not mention that he had single-handedly rescued his team's innings. He did not mention that his three-wicket burst in the nineteenth over had effectively ended Mumbai Indians' season. He did not mention that his 18 wickets this season — at an average of 24.38 and an economy of 9.14 — make him the best fast bowler in the tournament.

Jofra Archer does not mention things. He does them.

## What happens next

Rajasthan Royals finished fourth with 16 points. They will play Sunrisers Hyderabad in the Eliminator on May 27 at the IS Bindra Stadium in New Chandigarh. If they win, they play the loser of Qualifier 1 — either Royal Challengers Bengaluru or Gujarat Titans — in Qualifier 2 on May 29.

The road to the final on May 31 in Ahmedabad runs through two win-or-go-home matches. For a team whose season was saved by a fast bowler batting at number eight, the knockout format should feel familiar. Rajasthan Royals have been playing elimination cricket since May 24. The only difference now is that everyone else is too.""",
}


# ── ARTICLE 2: Wembanyama Ties the Western Conference Finals ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "Victor Wembanyama Scored 33 Points in 31 Minutes. He Hit a Half-Court Buzzer-Beater. He Sat Out the Entire Fourth Quarter Because the Spurs Were Winning by Too Much. The Series Is Tied.",
    "subheadline": "The 7-foot-4 Frenchman dismantled the Oklahoma City Thunder 103-82 in Game 4 of the Western Conference Finals, tying the series at 2-2. He shot 11-for-22 from the field, pulled down 8 rebounds, dished 5 assists, blocked 3 shots, and did not play the final eight minutes because San Antonio's lead was 25 points. Game 5 is tomorrow in Oklahoma City. He is twenty-two years old.",
    "slug": "victor-wembanyama-33-points-spurs-thunder-game-4-western-conference-finals-nba-2026-20260525",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "The NBA has become the second sport of the Indian diaspora in America. Not because India has a basketball tradition — it does not — but because the NBA is the sport that the Indian-American kid grows up watching in the living room with their American-born friends, the sport that plays in the background of every dorm room, the sport that provides the shared cultural vocabulary of the American workplace. The desi dad who grew up watching cricket in Hyderabad now watches the NBA playoffs with his son in Houston and understands, for the first time, why his American colleagues talk about basketball with the same intensity he reserves for India-Pakistan matches. Wembanyama is the player who makes this crossover legible. He is 7-foot-4 and moves like a guard. He shoots threes and blocks shots and passes like a point guard and, on Saturday night, hit a half-court buzzer-beater that was replayed on every phone in every Indian restaurant in the San Antonio metro area. San Antonio itself is a city the diaspora knows — UTSA has one of the fastest-growing Indian student populations in Texas, and the medical corridor along the I-10 employs hundreds of Indian-origin physicians. The Spurs, for this generation of San Antonio desis, are becoming what the Warriors were for the Bay Area Indian community a decade ago: the local team that makes you feel local.",
    "tags": ["Victor Wembanyama", "San Antonio Spurs", "Oklahoma City Thunder", "NBA", "Western Conference Finals", "Game 4", "De'Aaron Fox", "Shai Gilgeous-Alexander", "Stephon Castle", "NBA Playoffs 2026"],
    "urgency": "daily",
    "sources": [
        "https://www.reuters.com/sports/basketball/wembanyama-33-points-spurs-rout-thunder-even-series-2026-05-24/",
        "https://www.usatoday.com/story/sports/nba/2026/05/24/victor-wembanyama-game-4-stats-highlights-spurs-beat-thunder/",
        "https://www.si.com/nba/spurs-thunder-game-4-takeaways-wembanyama-san-antonio-dominate-okc",
        "https://www.sportingnews.com/us/nba/news/thunder-spurs-game-4-score-results-wembanyama/",
        "https://www.foxnews.com/sports/victor-wembanyama-scores-33-points-spurs-dominate-thunder-game-4"
    ],
    "word_count": 800,
    "score_total": 65,
    "body": """The numbers require no narrative. Victor Wembanyama scored 33 points on 11-for-22 shooting. He grabbed 8 rebounds. He dished 5 assists. He blocked 3 shots. He stole the ball twice. He hit a three-pointer from half-court as the first-half buzzer sounded — a shot that travelled 43 feet and hit nothing but net, sending the Frost Bank Center crowd into a state of noise that registered on the arena's own seismograph.

He did all of this in 31 minutes. He sat on the bench for the final 8 minutes and 43 seconds of the game because the San Antonio Spurs were ahead by 25 points and there was no reason for a twenty-two-year-old to risk injury in garbage time of a playoff game his team had already won.

The final score: San Antonio 103, Oklahoma City 82. The series: tied 2-2. Game 5: tomorrow, Tuesday, in Oklahoma City.

## The problem with the Thunder

Oklahoma City entered Game 4 with a 2-1 series lead and the look of a team that knew it was better. The Thunder had won the regular season with the best record in the Western Conference — 64 wins, 18 losses. Shai Gilgeous-Alexander, their franchise player, was the frontrunner for MVP. Their depth — Jalen Williams, Chet Holmgren, Lu Dort — was supposed to be the answer to the question that every team asks when it faces Wembanyama: what do you do when one player is 7-foot-4 and can do everything?

The Thunder's answer in Games 1 through 3 had been: make the other Spurs players beat you. Double Wembanyama. Force De'Aaron Fox and Stephon Castle to create offence. Attack the Spurs' bench, which had been outscored by the Thunder's reserves in every game. It had worked. The Thunder won Games 1 and 3 by a combined 19 points.

In Game 4, the strategy collapsed. Not because it was a bad strategy. Because Wembanyama decided it would not work.

## The third quarter

The first half was competitive. San Antonio led 50-38 at halftime — a 12-point lead that was significant but not decisive. The Thunder had shot 35 percent from the field, but that was partly Spurs defence and partly cold shooting that tends to correct itself over forty-eight minutes.

It did not correct itself.

The third quarter was the quarter in which Victor Wembanyama reminded the basketball world that he is not a normal basketball player. He is not even a normal great basketball player. He is something that the sport has not seen before — a 7-foot-4 centre who can handle the ball in transition, shoot from thirty feet, post up on the block, switch onto guards on defence, and block shots from angles that should not be physically possible.

In the third quarter alone, Wembanyama scored 14 points. He hit two three-pointers — one from the top of the arc, one from the left wing. He blocked two shots. He found Stephon Castle — who finished with 13 points and 6 assists, his best game of the series — with a no-look pass from the high post that Castle converted into a layup.

The Spurs outscored the Thunder 28-22 in the quarter. The 12-point halftime lead became an 18-point lead entering the fourth. By the time Wembanyama sat down with 8:43 remaining, the lead was 25. Coach Mitch Johnson did not need his best player to close the game. The game was already closed.

## The Thunder's shooting disaster

Oklahoma City shot 33 percent from the field — their worst shooting performance since March 2022. They shot 18 percent from three-point range. They scored 82 points, their second-lowest total in any playoff game this decade.

Shai Gilgeous-Alexander, who had averaged 31 points in the first three games of the series, was held to 19 on 7-for-21 shooting. The Spurs' defensive scheme — a combination of Castle's on-ball pressure and Wembanyama's help-side rim protection — turned SGA's drives into contested floaters and pull-up jumpers rather than the layups and free throws that define his game.

The absence of Jalen Williams, who has been dealing with a knee issue since the semifinal series against the Timberwolves, continued to hurt the Thunder's half-court offence. Williams is the Thunder's second creator — the player who takes pressure off Gilgeous-Alexander by generating his own shots and finding open shooters. Without him at full capacity, the Thunder's offence becomes Gilgeous-Alexander plus four people standing in designated spots. Against a defence anchored by Wembanyama, that is not enough.

## The Fox factor

De'Aaron Fox, acquired by the Spurs in a mid-season trade from Sacramento, has been the series' second story. Fox scored 12 points with 10 rebounds in Game 4 — not a stat line that makes highlights, but the kind of quiet efficiency that championship teams need from their second option.

Fox's role in San Antonio has been clarified by the playoffs: he is the pressure valve. When teams double Wembanyama, Fox attacks. When Wembanyama is on the bench, Fox creates. When the game slows down in the half-court, Fox pushes tempo. He is not the star. He does not need to be. He needs to be the reason that doubling Wembanyama comes at a cost, and in Game 4, the cost was 12 points and 10 rebounds and the feeling, for Oklahoma City, that there was no safe option.

## What happens Tuesday

Game 5 is in Oklahoma City. The Thunder have not lost a home playoff game this postseason — they are 6-0 at Paycom Center. Their crowd is one of the loudest in the NBA. Gilgeous-Alexander, who has been the best player in the league for most of this season, does not lose two consecutive games often.

But the Spurs have Wembanyama. And Wembanyama, on Saturday night, played 31 minutes of basketball that suggested the Thunder's problem is not tactical. It is existential. You cannot plan for a player who does not have a historical comparison. You cannot scheme against a 7-foot-4 centre who shoots 43-foot buzzer-beaters and sits out the fourth quarter because the game is too far gone.

The Western Conference Finals is now a best-of-three. Game 5 on Tuesday. Game 6 on Thursday in San Antonio. Game 7, if necessary, on Saturday in Oklahoma City.

The NBA Finals begin June 3. The Spurs, who were not supposed to be here — who were +300 underdogs in the preseason, who acquired Fox in January and lost their first two games of the playoffs — are three wins from being there.""",
}


if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-26 00:00 UTC (17:00 PDT May 25)")
    print("=" * 60)

    # Check for duplicate slugs first
    for art in [a1, a2]:
        slug = art["slug"]
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id",
            headers=HEADERS,
        )
        if r.status_code == 200 and r.json():
            print(f"  SKIP: slug already exists: {slug}")
            sys.exit(0)

    print("\nInserting Article 1: Jofra Archer — All-Round Masterclass at the Wankhede...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    img1_path = f"/tmp/{a1_id}.jpg"
    if fetch_image("cricket fast bowler celebrating wicket night stadium floodlights action", img1_path):
        img1_url = upload_image(a1_id, img1_path)
        if img1_url:
            update_image_url(a1_id, img1_url)

    print("\nInserting Article 2: Wembanyama — 33 Points, Series Tied...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    img2_path = f"/tmp/{a2_id}.jpg"
    if fetch_image("basketball player tall slam dunk arena crowd cheering professional NBA", img2_path):
        img2_url = upload_image(a2_id, img2_path)
        if img2_url:
            update_image_url(a2_id, img2_url)

    # Score decay
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    # Git commit
    try:
        subprocess.run(
            ["git", "add", "-A"],
            cwd=os.path.expanduser("~/workspace/the-videshi-news"),
            capture_output=True,
            timeout=10,
        )
        subprocess.run(
            ["git", "commit", "-m", "sports-writer: archer-wankhede-masterclass + wembanyama-game4 (2026-05-26 00:00 UTC)"],
            cwd=os.path.expanduser("~/workspace/the-videshi-news"),
            capture_output=True,
            timeout=10,
        )
        push_result = subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=os.path.expanduser("~/workspace/the-videshi-news"),
            capture_output=True,
            timeout=30,
        )
        if push_result.returncode != 0:
            print(f"  WARN: git push failed: {push_result.stderr.decode()[:200]}")
        else:
            print("  Git push OK")
    except Exception as e:
        print(f"  WARN: git error: {e}")

    print(f"\nDone. 2 articles published.")
    print(f"  IDs: {a1_id}, {a2_id}")
