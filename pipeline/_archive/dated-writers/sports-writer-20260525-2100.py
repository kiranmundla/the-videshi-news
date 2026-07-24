#!/usr/bin/env python3
"""Sports writer — 2026-05-25 21:00 UTC run (14:00 PDT): 2 articles + score decay."""

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


# ── ARTICLE 1: Sai Sudharsan — Back-to-Back Orange Caps ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Sai Sudharsan Used to Stand on the Road Watching the CSK Team Bus Pass His School. Now He Has 638 Runs, the Orange Cap, and a Record No Chennai Franchise Would Give Him.",
    "subheadline": "The twenty-four-year-old from Chennai won the Orange Cap in 2025 with 759 runs. He is winning it again in 2026 with 638. He did both for Gujarat Titans — a team based in a city he did not grow up in, playing for owners who paid three and a half crore for him when no one else would. He and Shubman Gill have both crossed 600 runs this season, the only opening pair in IPL history to do that in consecutive years. On Tuesday, they play Qualifier 1 against RCB in Dharamsala with a place in the final on the line. The Orange Cap holder bats first. The question is whether anyone in the country is watching closely enough.",
    "slug": "sai-sudharsan-orange-cap-638-runs-back-to-back-gujarat-titans-chennai-ipl-2026-20260525",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "In every NRI household that follows the IPL, the Orange Cap conversation goes like this: someone names Virat Kohli, someone names a big-hitting overseas player, and then someone — usually the person in the room who actually watches every match rather than just the highlights — says Sai Sudharsan. The room goes quiet. Not because they disagree, but because they do not know enough to respond. Sudharsan is the player the diaspora has not yet adopted. He does not have Kohli's Instagram following or Dhoni's mythology or Bumrah's YouTube compilations. He has 638 runs. He has seven fifties and a century. He has consecutive Orange Caps — 759 in 2025, 638 and counting in 2026 — and the distinction of being the only player in the history of the tournament to lead the run charts in back-to-back seasons while playing for a franchise based in a city that is not his own. This is a story the diaspora should recognise, because it is their story. You leave the place that raised you. You go to a city where nobody knows your name. You perform in a system that did not choose you first. And you become, by the numbers, the best at what you do — and still, somehow, the conversation is about someone else. Every NRI software engineer who quietly leads the sprint velocity charts while the team's standup conversation revolves around someone louder understands Sai Sudharsan. Every Indian doctor in a Houston hospital who has the best patient outcomes in the department but whose name never comes up when the chief of medicine is discussed understands this man. The Orange Cap is not a popularity contest. It is a count. And the count says 638.",
    "tags": ["Sai Sudharsan", "Orange Cap", "Gujarat Titans", "IPL 2026", "Shubman Gill", "Chennai", "Tamil Nadu", "RCB", "Qualifier 1", "Dharamsala", "R Ashwin", "Virat Kohli", "Back-to-Back"],
    "urgency": "daily",
    "sources": [
        "https://www.sportsyaari.com/cricket/sai-sudharsan-enters-elite-ipl-record-lists-featuring-virat-kohli-david-warner-and-chris-gayle/",
        "https://www.sportsdigest.in/cricket/ipl/600-plus-runs-for-a-team-in-a-single-ipl-edition-sai-sudharsan-and-shubman-gill-script-history-for-consecutive-2-seasons/",
        "https://www.sportskeeda.com/cricket/virat-kohli-vs-sai-sudharsan-comparing-their-stats-after-opening-in-32-ipl-matches",
        "https://khelja.in/r-ashwin-makes-bold-remark-about-sai-sudharsans-strike-rate-despite-having-orange-cap-in-ipl-2026/"
    ],
    "word_count": 830,
    "score_total": 72,
    "body": """The boy used to stand on the road outside his school in Chennai and watch the CSK team bus pass. He said this himself, in an interview earlier this season, without embarrassment or irony. He said it the way you say something that is simply true.

The bus carried Dhoni, Raina, Bravo, Jadeja — the men who made Chennai Super Kings the most emotionally owned franchise in Indian cricket. The boy watched it pass. He went home. He picked up a bat. He became, over the next decade, the best young batter Tamil Nadu had produced in a generation.

Chennai Super Kings did not buy him.

## The numbers

Sai Sudharsan has 638 runs in IPL 2026. He leads the Orange Cap standings. His average is 49.08. His strike rate is 157.92. He has scored one century and seven half-centuries in fourteen innings. He has been dismissed in single digits exactly twice this season.

Last year, in IPL 2025, he scored 759 runs and won the Orange Cap outright — the youngest player ever to do so.

He is doing it again.

The list of players who have won or led the Orange Cap in consecutive IPL seasons is short enough to recite from memory: Chris Gayle did it in 2011 and 2012. David Warner did it. Virat Kohli's 2016 season — 973 runs — remains the all-time record. Sudharsan is now in that company. He is twenty-four years old. He bats left-handed. He plays for Gujarat Titans, a franchise based in Ahmedabad, a city 1,500 kilometres from the school where he watched the bus.

## The partnership

The reason Sudharsan's Orange Cap dominance has not produced the national conversation it deserves is partly explained by the man at the other end.

Shubman Gill has 616 runs this season. He and Sudharsan are the only opening pair in IPL history to both cross 600 runs in a single season — and they have done it in consecutive years. In 2025, they combined for over 1,300 runs. In 2026, they have combined for 1,254 and counting, with the playoffs still to play.

Their partnership record tells the statistical story: 21 fifty-plus opening stands in 46 innings together across two seasons. Suresh Raina, not given to hyperbole about active players, called them the greatest opening pair in IPL history — above Gayle and Kohli at RCB, above Warner and Bairstow at SRH, above Rohit and Quinton de Kock at MI.

The difference is instructive. Gill scores with the flourish that makes highlight reels. Sudharsan scores with the consistency that makes run charts. In any partnership, the flashier player absorbs the attention. Sudharsan knows this. He has never once, in any interview this season, mentioned the Orange Cap before being asked about it.

## The criticism

R Ashwin — himself a Tamil Nadu cricketer, himself someone who understands what it means to be technically excellent in a format that rewards spectacle — made a pointed observation on his YouTube channel this week.

Sudharsan's strike rate of 157.92, Ashwin noted, is below the standard expected of a modern T20 opener in the death overs. "The finishing acceleration is not there yet," Ashwin said. "He gets to forty, fifty, sixty — and then the gear change doesn't always come."

The criticism is technically fair. The context makes it strange. Sudharsan has more runs than any other player in the tournament. He has more runs than Kohli (557), more than Klaasen (606), more than the fifteen-year-old Vaibhav Sooryavanshi whose strike rate of 232 is the number everyone quotes. Sooryavanshi has 583 runs at 232. Sudharsan has 638 runs at 158. The tournament's leading run-scorer is being told he does not score fast enough.

This is the paradox the modern game has created: a format where accumulation is insufficient, where the man with the most runs can be told he is not doing the job correctly. Sudharsan's response has been to keep scoring. The numbers are the numbers. Eight out of ten cricket fans, as one commentator noted, would dismiss his batting as insufficiently aggressive. The Orange Cap does not care about the opinions of eight out of ten fans.

## The Tuesday question

On Tuesday, Gujarat Titans play Royal Challengers Bengaluru in Qualifier 1 at Dharamsala. The HPCA Stadium sits at 1,457 metres above sea level, where the ball travels further in the thin air and the margins between a boundary and a catch shrink to a matter of inches. Kohli has 557 runs and the weight of a franchise that has never won the IPL. Sudharsan has 638 runs and the quiet confidence of a man who has won the Orange Cap before and knows exactly what it takes to win it again.

Gill will face Bhuvneshwar Kumar. Sudharsan will face the pressure of a knockout match in front of a crowd that is overwhelmingly there for Kohli. The Gujarat Titans opening pair — 1,254 runs between them — will walk out together the way they have walked out together forty-six times across two seasons: Gill with the swagger, Sudharsan with the stillness.

## The boy and the bus

The CSK team bus still passes through Chennai. The franchise has a different roster now — Sanju Samson keeps wicket, Ruturaj Gaikwad captains, the Dhoni era is memory — but the bus still drives the same routes, past the same schools, past the same roads where a boy once stood and watched.

The boy is not watching anymore. He is in Ahmedabad. He has 638 runs. He has the Orange Cap. He plays Qualifier 1 on Tuesday in a stadium in the Himalayas.

He never played for CSK. He may never play for CSK. The franchise that represented his city, his childhood, his first memory of professional cricket, looked at him and chose someone else. Three and a half crore in the auction. Gujarat Titans. A city he had no connection to, a franchise that had existed for exactly one year when they bought him.

And now he is the best batter in the tournament. Again.

The bus passes. The boy scores runs. The Orange Cap does not care where you are from. It cares how many you have made. The answer is 638, and counting.""",
}


# ── ARTICLE 2: SRH's Three-Headed Monster Walks Into the Eliminator ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "Heinrich Klaasen Has 606 Runs From Number Four. Nobody in the History of T20 Cricket Has Done That. On Wednesday, He Plays the Eliminator.",
    "subheadline": "Sunrisers Hyderabad posted 255 for 4 in their final league match. Ishan Kishan scored 79. Abhishek Sharma hit 56 off 22 balls. Klaasen added 51 off 24. They beat RCB by 55 runs. Now they wait at Mullanpur for the Eliminator on Wednesday — rested, in form, and carrying a middle-order record that no T20 league has ever seen. The opponent will be Rajasthan Royals, who played their last league match on Sunday and arrive with two fewer days of rest and Jofra Archer's right arm.",
    "slug": "srh-eliminator-klaasen-606-ishan-kishan-abhishek-sharma-mullanpur-ipl-2026-20260525",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "For the NRI watching the IPL Eliminator on Wednesday night — which, in California, means Wednesday morning, 7 AM on the West Coast if the start is 7:30 PM IST, the kind of time slot that requires either working from home or a manager who does not check Slack status closely — the SRH batting card presents a specific kind of problem. You cannot look away. You can mute the commentary and put the laptop on the kitchen counter while you make coffee. You can tell yourself you will check the score at lunch. But when Abhishek Sharma is 40 off 15 in the powerplay and the run rate is already past twelve, you are not making coffee. You are standing in your kitchen in Fremont or Jersey City or Brampton, watching a twenty-three-year-old hit sixes into a stadium you have never visited, in a city you could not locate on a map before the IPL put a franchise there, and you are late for your 8 AM standup because the powerplay has not ended yet. This is the condition of the NRI cricket fan in 2026. The time zones do not align. The work schedules do not accommodate. And the cricket is too good to miss. SRH's batting, specifically, is the kind of cricket that punishes the responsible decision to close the laptop and go to work. Nobody who watched Klaasen hit 51 off 24 on Friday night has the discipline to not watch the Eliminator on Wednesday. Nobody.",
    "tags": ["Sunrisers Hyderabad", "Heinrich Klaasen", "Ishan Kishan", "Abhishek Sharma", "Pat Cummins", "IPL 2026", "Eliminator", "Mullanpur", "Rajasthan Royals", "Jofra Archer", "Playoffs", "T20 Record"],
    "urgency": "daily",
    "sources": [
        "https://www.sportsadda.asia/cricket/features/klaasens-606-cumminss-3-for-28-kishans-best-season-how-srh-walk-into-the-ipl-2026-eliminator-at-mullanpur/",
        "https://www.wisden.com/stories/ipl/ipl-2026-purple-cap-full-list",
        "https://www.livemint.com/sports/cricket-news/updated-list-of-orange-cap-and-purple-cap-in-ipl-2026-after-srh-vs-rcb",
        "https://www.sportingnews.com/us/cricket/news/ipl-purple-cap-2026-list"
    ],
    "word_count": 840,
    "score_total": 70,
    "body": """The record did not exist before Heinrich Klaasen created it.

No batter in the history of professional T20 cricket — not in the IPL, not in the Big Bash, not in the PSL, not in the Hundred, not in any of the franchise leagues that have proliferated across forty countries in the last fifteen years — has scored 600 runs in a single season while batting at number four or lower. The previous record was Rishabh Pant's 579 for Delhi in 2018, itself a number that stood for eight years because the middle order in T20 cricket is not supposed to produce that volume.

Klaasen has 606. He did it in fourteen innings. His average is 50.50. His strike rate is 159.47. He has six half-centuries. He bats after the powerplay is over, against death-overs fields and bowlers who have had five overs to find their lengths. He faces used balls, tired surfaces, and the kind of bowling that most batting averages go to die against.

The number four slot in T20 cricket is a graveyard for aesthetics. You come in at 45 for 2 in the seventh over, or 120 for 2 in the fourteenth, or 8 for 1 in the second if the top order has collapsed. The situational range is enormous. You cannot play one tempo. You must read the game, read the bowler, read the field, and decide in the first three deliveries whether your job is to accumulate or to attack. Klaasen has done both, across fourteen matches, with a consistency that the position has never seen.

## The engine room

But Klaasen is not doing this alone, and the reason SRH walk into the Eliminator on Wednesday as the most dangerous lower-seed in the tournament is the three-man batting combination that has powered their season.

**Abhishek Sharma** opens. He has 563 runs at a strike rate of 206.22. That second number is the one that matters. Abhishek does not accumulate. He attacks from the first ball. His powerplay scoring rate this season has been the highest of any opener in the tournament, and the effect is structural: by the time the sixth over is bowled, SRH have either posted 60 or lost a wicket trying. There is no middle ground. The aggression is the point.

Against RCB on Friday — SRH's final league match — Abhishek scored 56 off 22 balls. He was out in the eighth over. By then, SRH were already past 80. The platform was set.

**Ishan Kishan** bats in the top three and has produced the most prolific IPL season of his career. His 569 runs across fourteen innings include six scores above fifty — a personal record. In his second year at SRH after the move from Mumbai Indians, Kishan has found the role he never consistently had at MI: the anchor who bats through the innings while the explosions happen around him. Against RCB, he scored 79 and batted until the seventeenth over, providing the spine of the innings while Abhishek and Klaasen provided the power.

The three of them — Abhishek's 563 at 206, Kishan's 569 at 178, Klaasen's 606 at 159 — have combined for 1,738 runs this season. That is more than most franchises' entire top six. It is more than Mumbai Indians' top seven combined. It is enough runs to win a tournament, if the bowling holds.

## The captain's quiet season

Pat Cummins has not had a vintage IPL with the ball. His wicket tally is modest by his standards. But the Australian Test captain's contribution has been in the matches SRH needed most. Against CSK at Chepauk on May 18, on a pitch the curator had prepared to neutralise pace, Cummins took 3 for 28 in four overs and SRH chased 181 with five wickets in hand. One spell. One match. One result that kept SRH in the top three.

The captaincy has been measured. The field placements have been conservative enough to contain and aggressive enough to take wickets in clusters. The bowling unit — Eshan Malinga with 19 wickets, the increasingly effective Cummins in the big moments — has not dominated the Purple Cap the way Bhuvneshwar Kumar (24 wickets) has for RCB, but it has done the job when the job was winning.

## Wednesday at Mullanpur

The Eliminator is at the Punjab Cricket Association IS Bindra Stadium in New Chandigarh on Wednesday, May 27, at 7:30 PM IST. SRH play Rajasthan Royals.

The advantage is SRH's. They played their last match on Friday. Rajasthan Royals played their last match on Sunday — the season-saving win over Mumbai Indians where Jofra Archer took 3 for 17. RR have two fewer days of rest. They arrive at Mullanpur having played a match that was, for them, an elimination game before the Eliminator. The emotional cost of a must-win league match is not zero.

Archer will be the difference for RR. His 21 wickets place him third in the Purple Cap standings, behind Bhuvneshwar (24) and Kagiso Rabada (24). Against SRH's top three, Archer's pace and bounce at Mullanpur — a ground where the evening dew can make the new ball do things it should not — could negate the batting advantage.

But the numbers favour SRH. Klaasen's 606 from number four is a record that exists because no one else in the history of T20 cricket could produce it. Kishan's six fifties are a career high. Abhishek's strike rate of 206 is not a statistic — it is a statement of intent.

## Win or go home

The Eliminator is exactly what it says. Lose and the season ends. The 9-5 record, the 18 points, the record-breaking middle order — all of it becomes a footnote. SRH have been here before. They won the title in 2016 with David Warner and Bhuvneshwar Kumar. They have not won it since.

Klaasen, Kishan, and Abhishek will walk out on Wednesday evening into a Mullanpur crowd that will be split between orange and pink. The floodlights will come on. The toss will happen. And somewhere — in Hyderabad, in Jaipur, in a kitchen in Fremont where the coffee is getting cold and the standup started five minutes ago — people will watch.

Six hundred and six runs from number four. The record that did not exist before this season. The question is whether it survives Wednesday night, or whether it becomes the most impressive set of numbers that did not win a trophy.""",
}


if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-25 21:00 UTC (14:00 PDT)")
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

    print("\nInserting Article 1: Sai Sudharsan — Orange Cap, 638 Runs...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    img1_path = f"/tmp/{a1_id}.jpg"
    if fetch_image("cricket batsman left handed elegant shot stadium floodlights", img1_path):
        img1_url = upload_image(a1_id, img1_path)
        if img1_url:
            update_image_url(a1_id, img1_url)

    print("\nInserting Article 2: SRH Eliminator — Klaasen 606...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    img2_path = f"/tmp/{a2_id}.jpg"
    if fetch_image("cricket stadium floodlights evening orange sunset crowd cheering", img2_path):
        img2_url = upload_image(a2_id, img2_path)
        if img2_url:
            update_image_url(a2_id, img2_url)

    # Score decay
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    print(f"\nDone. 2 articles published.")
    print(f"  IDs: {a1_id}, {a2_id}")
