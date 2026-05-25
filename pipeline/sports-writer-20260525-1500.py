#!/usr/bin/env python3
"""Sports writer — 2026-05-25 15:00 UTC run (08:00 PDT): 2 articles + score decay."""

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


# ── ARTICLE 1: Pathirana — ₹18 Crore for 8 Deliveries ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Matheesha Pathirana Cost Kolkata Knight Riders Eighteen Crore Rupees. He Bowled Eight Deliveries. Then His Season Was Over.",
    "subheadline": "The Sri Lankan fast bowler arrived late due to a calf injury, played one match, bowled 1.2 overs, pulled his hamstring, and was replaced by a twenty-five-year-old Karnataka wicketkeeper-batter signed for thirty lakh rupees. KKR's most expensive overseas acquisition in IPL 2026 will be remembered as one of the most costly eight balls in the tournament's history.",
    "slug": "matheesha-pathirana-kkr-18-crore-8-deliveries-hamstring-injury-ipl-2026-20260525",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Every Indian family in the diaspora has a version of this story. The cousin who was sent to America on a student visa that cost the family everything — twenty lakh, thirty lakh, sometimes more — and came back within a semester because the programme did not work out, or the job market collapsed, or the body gave way under the pressure of working two shifts while attending classes. The investment was not foolish. The logic was sound. Everyone agreed it was the right decision at the time. And yet the money was spent and the outcome was eight deliveries' worth of cricket. Eighteen crore rupees is not real money in the way that a family's savings are real money. It is franchise money, auction money, money that exists in a different economy. But the principle — that you can do everything right and still watch your biggest bet collapse before it has a chance to prove itself — translates across every Indian household that has ever pooled resources for a single opportunity. The NRI parent who invested in a relative's business back home and watched it fold within months. The H-1B worker who paid a lawyer fifteen thousand dollars for a case that was denied on a technicality. The family that bought a flat in Hyderabad or Pune for a son who decided, two years later, that he was not coming back. Pathirana did nothing wrong. His body failed him. KKR did nothing wrong. Their scouting was correct. The auction price was market rate for a bowler of his calibre. And yet: eighteen crore for eight deliveries. Some investments do not fail because the thesis was wrong. They fail because the world does not care about your thesis.",
    "tags": ["Matheesha Pathirana", "KKR", "Kolkata Knight Riders", "IPL 2026", "Hamstring Injury", "Calf Injury", "Luvnith Sisodia", "Sri Lanka", "IPL Auction", "18 Crore"],
    "urgency": "daily",
    "sources": [
        "https://www.livemint.com/sports/cricket-news/matheesha-pathirana-maiden-ipl-stint-kkr-8-deliveries-luvnith-sisodia",
        "https://www.insidesport.in/cricket/kkr-forced-to-sign-replacement-as-matheesha-pathirana-lasts-just-8-deliveries-in-ipl-2026",
        "https://www.iplt20.com/news/kkr-suffer-huge-blow-as-matheesha-pathirana-ruled-out-of-ipl-2026",
        "https://www.yardbarker.com/cricket/articles/ipl-2026-matheesha-pathirana-ruled-out-kkr-sign-luvnith-sisodia-as-replacement"
    ],
    "word_count": 790,
    "score_total": 68,
    "body": """The arithmetic is simple. Kolkata Knight Riders paid eighteen crore rupees for Matheesha Pathirana at the IPL 2026 mega auction. Over the course of the entire season, Pathirana bowled eight deliveries. That is 2.25 crore rupees per ball. It is, by any reasonable measure, the most expensive eight balls in the history of the Indian Premier League.

The story of how this happened is a story about bodies, timing, and the particular cruelty of a tournament that does not wait for anyone.

## The acquisition

Pathirana was, on paper, exactly what KKR needed. A right-arm fast bowler with a slingy action modelled on Lasith Malinga's — his childhood hero and, later, his mentor at Chennai Super Kings. At twenty-three, Pathirana had already won a T20 World Cup with Sri Lanka, taken 13 wickets for CSK in IPL 2023 at an economy of 7.5, and developed a yorker that, when it landed, was virtually unplayable. The sling-arm release made the ball skid onto the batsman faster than the speed gun suggested. He was not a mystery bowler. He was a precision instrument.

KKR's auction strategy in the mega auction was built around Pathirana. They wanted a death bowler who could close matches. They wanted an overseas fast bowler who could operate in the powerplay and at the death — the two phases where matches are won and lost. They paid eighteen crore. It was the highest price paid for a Sri Lankan cricketer in IPL auction history.

## The first delay

Pathirana did not arrive in India when the tournament began on March 28. He had a calf injury — sustained during Sri Lanka's pre-season training — and Sri Lanka Cricket initially withheld clearance. The injury was described as minor. Recovery time: two to three weeks. KKR's management said publicly that they expected him to be available by mid-April. The team played their first six matches without him.

They lost all six.

The losses were not solely about the absence of one bowler. KKR's batting was inconsistent, their fielding was poor, and the captaincy — under Shreyas Iyer, who would later say he never considered stepping down — was reactive rather than proactive. But the absence of their most expensive signing hung over the camp like an unpaid bill.

Pathirana arrived in mid-April. He began bowling in the nets. The reports were cautiously optimistic. His calf had healed. His pace was back. The sling-arm action was unchanged. KKR, who had by then won two of their next four matches and were showing signs of recovery, waited for the right moment to bring him into the eleven.

## The eight deliveries

The moment came. Pathirana was named in the playing eleven. He opened the bowling. First over: six deliveries. His pace was 142, 143, 145 kilometres per hour. The action was smooth. The ball was swinging. Then, in his second over, on the second delivery — ball number eight of his IPL 2026 career — he pulled up.

The left hamstring. Not the calf that had kept him out for three weeks. A different muscle, a different injury, the same result. He walked off the field. He did not return. The medical staff assessed him that evening. The verdict: ruled out for the remainder of the tournament.

In total: 1.2 overs. Eight deliveries. Zero wickets. Season over.

## The replacement

KKR signed Luvnith Sisodia as Pathirana's replacement. Sisodia is a twenty-five-year-old wicketkeeper-batter from Karnataka with 124 runs in 15 T20 matches. He was signed for thirty lakh rupees — the minimum possible price for a replacement signing. He was not a like-for-like replacement. He was not even a bowler. He was a body to fill a squad spot so that KKR could meet the tournament's minimum roster requirements.

The contrast is mathematical: eighteen crore for the player who left, thirty lakh for the player who replaced him. A ratio of six hundred to one.

## The wider wreckage

Pathirana's injury was not the only blow KKR absorbed this season. Harshit Rana, their Indian fast bowler, required knee surgery before the tournament and never played. Angkrish Raghuvanshi, the young batter, suffered a season-ending injury mid-tournament. Varun Chakaravarthy, their primary spinner, played through a fractured toe for the final weeks of the league stage.

By the time KKR played their final match — against Delhi Capitals at Eden Gardens on May 24, a match they needed to win by an impossible margin to qualify for the playoffs — they were held together by adhesive tape and stubbornness. They lost by 40 runs. They finished seventh with 13 points. Their season, which began with six consecutive losses and ended with a rally that fell one win short, is over.

## The economics of faith

Eighteen crore rupees is approximately 2.15 million US dollars. For that amount, KKR received 1.2 overs of fast bowling. The per-over cost — roughly 1.07 million dollars — exceeds the annual salary of most professional cricketers in the world.

This is not a story about waste. KKR's decision to bid eighteen crore was rational. Pathirana's talent is real. His injury history, while concerning, was not disqualifying — many fast bowlers manage calf and hamstring issues throughout their careers. The auction is a market, and the market priced Pathirana at eighteen crore because multiple franchises believed he was worth it.

But the IPL is also a tournament of twelve weeks and fourteen matches. There is no time to wait for a body to heal. There is no second half of the season to make up for a poor first half. Every match is a quarter of your season. Every injury is a percentage of your investment walking off the field.

Pathirana's eight deliveries will appear as a footnote in the IPL 2026 statistics. In KKR's accounting, they will appear as an eighteen-crore line item with no return. In the broader story of the IPL's escalating auction prices, they will appear as a cautionary tale — or, more accurately, as a reminder that caution has no place in a tournament built on the principle that fortune favours the bold.

The bold, this season, were not favoured. They were injured.""",
}


# ── ARTICLE 2: Kuldeep Yadav Returns to Eden Gardens ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "Kuldeep Yadav Spent Seven Years at KKR. They Let Him Go. On Saturday Night He Came Back to Eden Gardens and Took Three Wickets to End Their Season.",
    "subheadline": "The left-arm wrist spinner, who played for Kolkata Knight Riders from 2014 to 2021 before being traded to Delhi Capitals, returned to the ground where he grew up as a cricketer. He took 3 for 29 in 4 overs. KKR collapsed from 126 for 3 to 163 all out. The season's final league match became, for Kuldeep, a quiet reckoning.",
    "slug": "kuldeep-yadav-kkr-eden-gardens-three-wickets-dc-final-league-match-ipl-2026-20260525",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "The diaspora understands departures that become returns. Every NRI who has gone back to the office they once worked at, the school they once attended, the city they once lived in — not as a visitor, not as a nostalgist, but as someone who has become something different since they left — understands what Kuldeep Yadav did at Eden Gardens on Saturday night. It is the particular satisfaction of returning to a place that decided you were not necessary and demonstrating, without saying a word, that the decision was theirs to regret. Indian families in America know this feeling intimately. The engineer who was laid off from a company in Sunnyvale and, three years later, joined a competitor that acquired his former employer. The daughter who was told by relatives in India that her decision to study literature instead of engineering was a waste, and who now writes for a publication those relatives read. The son who left a family business in Mumbai because he was not given a seat at the table, and who built something in Houston that his cousins now ask to invest in. These are not revenge stories. They are competence stories. The person who was let go does not return with anger. They return with three wickets for twenty-nine runs in four overs. They return with the quiet confidence of someone who knows that the place they left has not improved since they departed.",
    "tags": ["Kuldeep Yadav", "KKR", "Kolkata Knight Riders", "Delhi Capitals", "Eden Gardens", "IPL 2026", "Wrist Spinner", "KL Rahul", "Lungi Ngidi", "Ajinkya Rahane"],
    "urgency": "daily",
    "sources": [
        "https://www.crickettimes.com/2026/05/ipl-2026-fans-erupt-as-kl-rahul-and-kuldeep-yadav-shine-bright-dc-kkr",
        "https://nationpress.com/ipl-2026-kuldeep-yadavs-double-strike-turned-dc-vs-kkr-match-says-doull",
        "https://www.sportsmintmedia.com/ipl-2026-kkr-vs-dc-kl-rahul-kuldeep-yadav-star-dc-demolish-kkr-eden",
        "https://iplt20.com/match-report/kkr-v-dc-match-70-ipl-2026"
    ],
    "word_count": 810,
    "score_total": 70,
    "body": """The facts of the match can be stated briefly. Delhi Capitals posted 203 for 5 in 20 overs at Eden Gardens on May 24. KL Rahul scored 60 off 30 balls. Kolkata Knight Riders, chasing 204 to win, were 126 for 3 in the fourteenth over with Ajinkya Rahane set on 63 and the required run rate still within reach. Then Kuldeep Yadav bowled.

The facts of the history require more space.

## Seven years at Eden Gardens

Kuldeep Yadav was selected by Kolkata Knight Riders in the 2014 IPL auction. He was eighteen years old. He was a left-arm wrist spinner from Kanpur — a city that produces batsmen and medium-pacers, not chinaman bowlers. His action was unusual. His wrist position was extreme. His googly was, for the first two years, better than his stock ball.

He played his first IPL match at Eden Gardens in 2016. Over the next five seasons, he became one of the most recognisable spinners in the tournament. In 2017, he took the IPL's first hat-trick by a spinner — three wickets in three balls against Sunrisers Hyderabad, at Eden Gardens, in front of sixty thousand people. He played for India, became the first Indian to take two hat-tricks in international cricket, and was described by Shane Warne as "the best young wrist spinner in the world."

He was a KKR player for seven years. Eden Gardens was his home ground. The crowd knew his name.

## The departure

In the 2022 mega auction, KKR did not buy Kuldeep back. The franchise's strategy had shifted. They invested in Varun Chakaravarthy's mystery spin and a pace-heavy bowling attack. Kuldeep, who had struggled with form and a knee injury in 2020 and 2021, was not part of the plan.

Delhi Capitals signed him. He went to a new franchise, a new city, a new dressing room. The move was not acrimonious — there were no public statements, no social media commentary, no visible bitterness. But in the economy of professional cricket, being released by the franchise that raised you is a statement that does not require words. It says: we have assessed your future and decided it exists somewhere else.

Kuldeep responded the way professionals respond. He took 21 wickets for DC in IPL 2023. He was India's Player of the Tournament at the 2023 World Cup. He won a second World Cup with India in 2024. The knee that had troubled him was surgically repaired, and the wrist that had always been his instrument was, by 2025, operating with more control and more deception than at any point in his career.

## The return

IPL 2026 brought Kuldeep back to Eden Gardens on Saturday, May 24 — the final league match of the season. It was, for KKR, a match of desperation. They needed to beat DC by a margin large enough to overtake Punjab Kings on net run rate. By the time the match began, the scenario was already nearly impossible: Rajasthan Royals had beaten Mumbai Indians at the Wankhede, meaning KKR were mathematically eliminated before the first ball was bowled. But the scoreboard does not know the points table. The match was played.

KL Rahul set the target. His innings — 60 off 30 balls — was an exercise in controlled violence. He hit three sixes over midwicket in the space of eight deliveries during the powerplay. David Miller contributed 28 off 19 at the death. DC posted 203, a total that was, against a KKR side playing for nothing, theoretically gettable.

Ajinkya Rahane made it look gettable. His 63 — unhurried, technically correct, the innings of a man who has been scoring runs in Indian cricket for fifteen years — brought KKR to 126 for 3 in the fourteenth over. The required rate was climbing but not yet impossible. The Eden Gardens crowd, knowing their team was already eliminated, was cheering for something smaller than a playoff spot: they were cheering for a fight.

## The spell

Kuldeep Yadav came on in the fifteenth over. His first delivery was the stock chinaman — turning away from the right-hander, pitched on middle stump, drifting towards leg. The second was the googly.

What happened next was described by commentator Simon Doull as "the moment that turned the match." Kuldeep's double strike in the space of six balls — both batsmen beaten in the flight, both dismissed playing across the line — collapsed the KKR chase. From 126 for 3, they were suddenly 140 for 5. The middle order, which had been rebuilding, was gone.

Lungi Ngidi finished the job from the other end, taking three wickets of his own. KKR were bowled out for 163 in 18.4 overs. DC won by 40 runs. The season — IPL 2026, 70 matches, ten teams, twelve weeks — was over.

Kuldeep's figures: 4 overs, 0 maidens, 29 runs, 3 wickets. At the ground where he took his first IPL hat-trick. Against the team that decided, four years ago, that his future was somewhere else.

## The silence after

There was no celebration. Kuldeep did not gesture towards the KKR dugout. He did not point to the Eden Gardens stands. He did not seek out his former teammates for a moment of symbolic triumph. He took his cap from the umpire, walked back to his mark, and bowled the next delivery.

This is the detail that matters. Professional athletes who return to their former teams and perform well are expected, by the conventions of sports narrative, to produce a moment — a stare, a finger to the lips, a pointed acknowledgement that this meant something. Kuldeep produced nothing of the kind. His face, throughout the spell, was the face of a man doing his job. The satisfaction, if it existed, was internal.

The Delhi Capitals dressing room embraced him after the match. KL Rahul, who had set up the victory with his 60, gave Kuldeep a hug that lasted longer than the standard post-match embrace. The Man of the Match award was given to Kuldeep. He accepted it quietly.

KKR finished seventh. Delhi finished sixth. Neither team made the playoffs. But the final match of the league stage, played at Eden Gardens on a Saturday night in May, belonged to a man who had spent seven years at that ground and was told, one day, that his services were no longer required.

He came back. He bowled. He took three wickets. He said nothing. The match said everything.""",
}


if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-25 15:00 UTC (08:00 PDT)")
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

    print("\nInserting Article 1: Pathirana — ₹18 Crore for 8 Deliveries...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    img1_path = f"/tmp/{a1_id}.jpg"
    if fetch_image("cricket fast bowler injury walking off field night stadium", img1_path):
        img1_url = upload_image(a1_id, img1_path)
        if img1_url:
            update_image_url(a1_id, img1_url)

    print("\nInserting Article 2: Kuldeep Yadav Returns to Eden Gardens...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    img2_path = f"/tmp/{a2_id}.jpg"
    if fetch_image("cricket spinner bowling celebration night stadium floodlights", img2_path):
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
            ["git", "commit", "-m", "sports-writer: pathirana-18cr + kuldeep-eden-gardens (2026-05-25 15:00 UTC)"],
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
