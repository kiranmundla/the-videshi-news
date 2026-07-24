#!/usr/bin/env python3
"""Sports writer — 2026-05-25 09:00 UTC run (02:00 PDT): 2 articles + score decay."""

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


# ── ARTICLE 1: Riyan Parag — "I Was Not Supposed to Play Today" ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Riyan Parag Said He Was Not Supposed to Play. He Played Anyway. His Team Made the Playoffs. Now He Says He Will Play the Eliminator Too.",
    "subheadline": "The Rajasthan Royals captain, twenty-four years old and carrying a hamstring injury that kept him out of the previous match, returned to lead his side to a 30-run victory over Mumbai Indians at the Wankhede. After the match, he admitted he was 'definitely not fit' and was 'not supposed to play another game.' When asked whether he would play the Eliminator against Sunrisers Hyderabad on Wednesday, his answer was two words: 'Yeah, of course.'",
    "slug": "riyan-parag-not-supposed-to-play-hamstring-injury-rr-mi-playoffs-eliminator-ipl-2026-20260525",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "There is a particular kind of stubbornness that Indian parents in the diaspora recognise instantly. It is the stubbornness of the child who was told to rest and refused. The child who went to school with a fever because missing a day felt like losing ground. The child who stayed up past midnight finishing a project that could have waited until morning, because something in them — something inherited, something cultural, something that does not translate neatly into English — insisted that showing up was more important than being comfortable. Riyan Parag's decision to play through a hamstring injury at the Wankhede on Saturday night belongs to this lineage. It is not recklessness. It is the particular Indian conviction that leadership is physical — that the captain must be present, must be visible, must be in pain alongside everyone else. Every NRI family that has watched a father work through illness because the restaurant could not close, or a mother drive to a parent-teacher conference with a migraine because absence would be noticed, understands what Parag did without needing it explained. At twenty-four, leading a franchise worth hundreds of crores, playing in a match that would determine whether his team's season ended or continued — he chose to be on the field when his body told him not to be. The diaspora, which has built entire communities on the principle that you show up even when it costs you something, did not need the post-match interview to understand why.",
    "tags": ["Riyan Parag", "Rajasthan Royals", "IPL 2026", "Hamstring Injury", "Mumbai Indians", "Wankhede", "Eliminator", "SRH", "Jofra Archer", "Captain", "Playoffs"],
    "urgency": "daily",
    "sources": [
        "https://thesportstak.com/cricket/riyan-parags-big-confession-on-his-fitness-after-rr-reach-ipl-2026-playoffs",
        "https://mykhel.com/cricket/ipl-news-bulletin-may-25-rr-reach-playoffs-dc-beat-kkr",
        "https://crictracker.com/ipl-2026-riyan-parag-reflects-rr-tactical-calls-playoff-qualification",
        "https://iplt20.com/match-report/mi-v-rr-match-69-ipl-2026"
    ],
    "word_count": 780,
    "score_total": 70,
    "body": """The sequence of events requires recounting in order, because the order is the point.

On May 20, Rajasthan Royals played Lucknow Super Giants in Match 64 of IPL 2026. Riyan Parag was not in the playing eleven. The team announcement listed Yashasvi Jaiswal as captain. Parag's hamstring — injured days earlier — had been assessed by the medical staff. The verdict: rest. Do not play. Let the muscle heal.

Rajasthan Royals won that match. They did not need Parag. Jaiswal captained competently, the bowling held, and the result put Rajasthan in a position where one more win — in their final league match, against Mumbai Indians at the Wankhede — would guarantee a playoff spot.

Four days later, Parag walked out at the Wankhede in RR colours. He had overruled the medical recommendation. He was in the playing eleven. He was captain.

## The match that mattered

Mumbai Indians won the toss and chose to bowl. Rajasthan Royals batted first, and the innings followed the pattern of a team that needed to win but could not quite relax into fluency. Yashasvi Jaiswal contributed at the top. Dhruv Jurel, who has had an understated but effective tournament behind the stumps, scored 38 in the middle order. Ravindra Jadeja — himself returning from a knee flare-up — provided stability in a partnership that steadied the innings after early movement.

Then Jofra Archer walked in at number eight.

Parag had promoted Archer up the order — a tactical decision that required either supreme confidence in his bowler's batting ability or the particular desperation of a captain who knew his middle order was not producing enough. Archer scored 32 off 17 balls. Two sixes cleared the midwicket boundary with the effort of someone swatting a fly off a table. Rajasthan posted 205 for 8.

The chase never materialised. Suryakumar Yadav made 60 — the kind of innings that, in a different match, would have been enough to build a chase around. But Archer, having done his work with the bat, returned with the ball and took 3 for 17. Nandre Burger and Brijesh Sharma closed out the middle overs. Mumbai were bowled out for 175. Rajasthan won by 30 runs. The season continued.

## The confession

In the post-match interview, with the playoff qualification confirmed and the cameras still running, Parag said the words that will follow him for the rest of this tournament and possibly longer:

"I'm definitely not fit. I was not supposed to play today. I'm not supposed to play another game."

The interviewer, perhaps expecting a more celebratory tone from a captain who had just led his team to the playoffs, paused. Then came the follow-up: would he play the Eliminator on Wednesday, against Sunrisers Hyderabad?

"Yeah, of course."

Two words. No elaboration. The kind of answer that reveals more about a person's relationship with their own body than any medical bulletin could.

## The context of twenty-four

Riyan Parag was born on November 10, 2001. He is twenty-four years old. He won the Under-19 World Cup with India in 2018, scored a half-century in the IPL at seventeen, and spent the next several years occupying the frustrating middle ground of Indian cricket: too talented to be ignored, too inconsistent to be indispensable.

The captaincy of Rajasthan Royals — given to him ahead of the 2026 season — was either a statement of faith or a gamble, depending on which commentator you asked. At twenty-four, he became one of the youngest captains in IPL history. The franchise paid fourteen crore rupees for him. The expectation was not merely that he would bat well. It was that he would lead.

The season has been uneven. Rajasthan lost six consecutive matches between late April and mid-May. Their qualification came on the final day of the league stage, in the final league match, with three other teams still mathematically alive for the same spot. It was the least comfortable path to the playoffs that a franchise could have taken.

And yet: they are in the playoffs. And their captain, who was not supposed to be on the field, was on the field. And their captain, who is not supposed to play another game, will play another game.

## What Wednesday means

The Eliminator is at the IS Bindra Stadium in New Chandigarh on May 27. Sunrisers Hyderabad, who finished third in the table, bring Heinrich Klaasen's 606 runs, Pat Cummins's captaincy, and a bowling unit that includes Bhuvneshwar Kumar. They are, on paper, the stronger side.

Rajasthan bring Parag's hamstring, Archer's form, Sooryavanshi's 53 sixes, and whatever Jadeja's knee will allow him to contribute. They bring the energy of a team that should have been eliminated two weeks ago and refused.

The loser goes home. The winner plays Qualifier 2 on Friday for a place in the final at Ahmedabad.

Parag will bat. Parag will field. Parag will set the field and rotate his bowlers and make the decisions that determine whether his team's season lasts three more hours or three more matches. He will do this on a hamstring that his medical staff advised him not to use.

He was not supposed to play. He played. And when asked if he would do it again, he did not hesitate.

"Yeah, of course."

Some answers do not need to be longer than two words.""",
}


# ── ARTICLE 2: Qualifier 1 Preview — Kohli vs Gill at Dharamshala ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "Virat Kohli Has 557 Runs and 9,203 Career IPL Runs. Shubman Gill Has 616 Runs and Just Passed Sachin Tendulkar's T20 Captaincy Record. They Play Each Other Tomorrow for a Place in the Final.",
    "subheadline": "RCB and Gujarat Titans meet in Qualifier 1 at Dharamshala on Tuesday evening. The winner goes directly to the IPL 2026 final at Ahmedabad on May 31. The loser plays the Eliminator winner on Friday. At the centre of the match are two batters separated by eleven years, 8,587 career IPL runs, and the complicated inheritance of Indian cricket's most scrutinised succession plan.",
    "slug": "virat-kohli-shubman-gill-rcb-gt-qualifier-1-dharamshala-ipl-2026-final-20260525",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "In every Indian household in the diaspora, there is a generation that grew up with Virat Kohli and a generation that is growing up with Shubman Gill. The dividing line is not clean — it never is with cricket — but it exists. The parents who landed in the US between 2005 and 2015, who watched Kohli's 82 off 51 balls in the 2016 World T20 semi-final on a laptop stream at 2 AM EST, who felt something primal when he chased down 188 against Australia in 2022 — these are the Kohli generation. Their children, who care more about strike rates than averages, who follow IPL highlights on Instagram before they follow Test matches on television, who think of cricket as entertainment first and tradition second — these are the Gill generation. Tomorrow's Qualifier 1 at Dharamshala is, for the diaspora, a match between these two versions of Indian cricket fandom. When Kohli walks out to bat, NRI living rooms in Edison and Fremont and Brampton will feel something that they have felt for nearly two decades — the particular electricity of knowing that the best version of Indian batting might be about to happen. When Gill walks out to bat, a different current will run through those same living rooms — the current of recognition, of seeing in a twenty-six-year-old opener the future that Indian cricket has been promising since Kohli's reflexes first began to slow. The mentorship between them is real. Gill has spoken publicly about Kohli's advice. The viral video of Kohli checking out Gill's new beard in the Dharamshala team hotel — affectionate, teasing, entirely unguarded — went viral precisely because it showed the relationship behind the rivalry. But tomorrow, the relationship pauses. Tomorrow, one of them eliminates the other from the tournament. The diaspora will watch from twelve time zones away, and every family will be split: the father rooting for the man who defined his cricket, the son rooting for the man who will define his.",
    "tags": ["Virat Kohli", "Shubman Gill", "RCB", "Gujarat Titans", "Qualifier 1", "Dharamshala", "IPL 2026", "IPL Final", "Sai Sudharsan", "Bhuvneshwar Kumar", "Rashid Khan", "Jos Buttler"],
    "urgency": "daily",
    "sources": [
        "https://mykhel.com/cricket/virat-kohli-ipl-2026-stats-runs-highest-score",
        "https://storyboard18.com/cricket/ipl-2026-shubman-gill-surpasses-sachin-tendulkar-t20-captaincy-runs",
        "https://sportskeeda.com/cricket/virat-kohli-hilariously-checks-shubman-gill-beard-rcb-gt-ipl-2026-qualifier-1",
        "https://khaspress.com/rcb-vs-gt-qualifier-1-match-prediction-ipl-2026-final",
        "https://sportingnews.com/cricket/virat-kohli-ipl-2026-rcb-stats"
    ],
    "word_count": 800,
    "score_total": 72,
    "body": """The numbers, first, because the numbers are the foundation on which everything else is built.

Virat Kohli: 557 runs in 14 innings. Average 50.64. Strike rate 163.82. Four half-centuries. One century — an unbeaten 105 off 60 balls against Kolkata Knight Riders that was, even by his standards, an innings of controlled fury. Career IPL runs: 9,203 across 280 matches and eighteen seasons. Nine centuries. Sixty-six half-centuries. The all-time leading run-scorer in the history of the tournament, by a margin that no active player is likely to close.

Shubman Gill: 616 runs in 14 innings. Average 47.38. Strike rate 161.28. The third captain in IPL history to cross 600 runs in back-to-back seasons. He surpassed Sachin Tendulkar's career T20 captaincy runs tally — 1,874 to Tendulkar's 1,871 — during Gujarat Titans' final league match against Chennai Super Kings. He reached 6,000 career T20 runs in 185 innings, the second-fastest Indian behind KL Rahul. He is twenty-six years old.

Between these two sets of numbers, a match will be played tomorrow evening in the Himalayan foothills.

## The venue

Dharamshala's Himachal Pradesh Cricket Association Stadium sits at 1,457 metres above sea level. The ball swings here. The air is thinner than at sea level, which means the ball carries further when hit, but the lateral movement off the seam in the first six overs is more pronounced than at most IPL venues. The evening dew — which rolls in after sunset and coats the outfield in moisture — makes the ball harder to grip for bowlers in the second innings. Teams batting second have historically preferred Dharamshala. The toss will matter.

RCB have played at Dharamshala before. Kohli has batted here before. But this is not RCB's regular home ground — they play most home matches at the M. Chinnaswamy Stadium in Bengaluru. The BCCI assigned Dharamshala as the Qualifier 1 venue. It is, for both teams, something close to neutral territory.

## The batting comparison

Kohli bats at the top of the order. He opens for RCB. He has done this for the majority of the last decade, and his method has not changed in its essentials: he takes the first over carefully, identifies the bowler he wants to attack, and then accelerates through the middle overs with a combination of wristwork through the leg side and drives through the covers that make fast bowlers reconsider their line.

This season, he has added something. His strike rate — 163.82 — is the highest of any IPL season in his career. At thirty-seven, he is hitting the ball harder and more often than he did at thirty-two. The explanation is partly tactical — RCB have asked him to be more aggressive in the powerplay — and partly physical. He is, by all accounts, in exceptional condition for a man approaching forty.

Gill also opens. He also takes the first over carefully. But where Kohli's acceleration is gradual — building from rotation to boundaries to occasional sixes — Gill's is sudden. His fifty against CSK in the last league match came off twenty-three deliveries. He went from 12 off 14 balls to 50 off 23. The transition had no warning. One over he was nudging singles. The next he was clearing midwicket.

Their opening partners matter. Kohli has batted with Phil Salt and Venkatesh Iyer this season — the debate over who should open alongside him in the Qualifier is still unresolved. Gill bats with Sai Sudharsan, and together they have formed the most prolific opening partnership in this IPL. Ten century stands as a pair across T20s. Fifteen fifty-plus partnerships. The Gill-Sudharsan combination is not merely productive. It is, in terms of sustained output, historically significant.

## The bowling matchups

RCB's attack is built around Bhuvneshwar Kumar. The veteran seamer has 24 wickets this season — co-leading the Purple Cap race — and his ability to swing the new ball in Dharamshala's conditions makes him the most dangerous bowler in the Qualifier. If the ball moves even slightly in the first three overs, Gill and Sudharsan will face the most searching examination of their technique that the tournament has offered.

Gujarat Titans bring Kagiso Rabada, Rashid Khan, and Mohammed Siraj. Rabada's pace — consistently above 145 kilometres per hour — and Rashid's leg-spin create a combination that can attack both left-handed and right-handed batters through the middle overs. Siraj, bowling for the franchise he was traded to before the season, has had a quietly effective campaign. Against CSK, he took 3 wickets. Against Kohli — whom he has bowled to in RCB nets for years — he knows the weaknesses that only a former teammate can know.

Jos Buttler provides Gujarat's finishing power. His unbeaten 57 off 27 balls against CSK demonstrated that, at thirty-five, his ability to clear boundaries in the death overs remains elite. If the match reaches the seventeenth over with Gujarat still in the hunt, Buttler will be the reason.

## The succession

Cricket does not do clean handovers. There was no moment when Tendulkar handed the baton to Kohli — they overlapped for years, played in the same teams, and the transition happened gradually, noticed only in retrospect. The same is happening now. Kohli and Gill are not opponents in a generational war. They are contemporaries who happen to be at different stages of the same journey.

But tomorrow, one of them will bat his team into the IPL 2026 final. The other will watch from the dugout as the season narrows without him.

Qualifier 1. Dharamshala. Tuesday, May 26. 7:30 PM IST. The winner goes to Ahmedabad. The loser gets one more chance on Friday. Both will bat as if there is no Friday.

The Himalayas will not care who wins. The diaspora, watching from the other side of the world, will care enormously.""",
}


if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-25 09:00 UTC (02:00 PDT)")
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

    print("\nInserting Article 1: Riyan Parag — 'I Was Not Supposed to Play Today'...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    img1_path = f"/tmp/{a1_id}.jpg"
    if fetch_image("cricket captain leading team celebrating victory stadium night", img1_path):
        img1_url = upload_image(a1_id, img1_path)
        if img1_url:
            update_image_url(a1_id, img1_url)

    print("\nInserting Article 2: Kohli vs Gill — Qualifier 1 at Dharamshala...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    img2_path = f"/tmp/{a2_id}.jpg"
    if fetch_image("cricket stadium himalayan mountains sunset evening match floodlights", img2_path):
        img2_url = upload_image(a2_id, img2_path)
        if img2_url:
            update_image_url(a2_id, img2_url)

    # Score decay
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    print(f"\nDone. 2 articles published.")
    print(f"  IDs: {a1_id}, {a2_id}")
