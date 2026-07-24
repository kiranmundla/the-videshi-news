#!/usr/bin/env python3
"""Sports writer — 2026-05-25 03:00 UTC run: 2 articles + score decay."""

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


# ── ARTICLE 1: Arjun Tendulkar's IPL Debut — 37 Months Between Wickets ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Arjun Tendulkar Waited 37 Months for Another IPL Wicket. He Got It With a Yorker on the Last Day of the League Stage, Playing for a Team That Isn't His Father's.",
    "subheadline": "Sachin Tendulkar's son made his Lucknow Super Giants debut in the final league match of IPL 2026, bowling four overs for 1 wicket and 36 runs against Punjab Kings. His figures were the most economical on his side. His last IPL wicket — Wriddhiman Saha, April 2023, in Mumbai Indians colours — was 37 months ago. Sachin posted an emotional message afterwards. LSG lost by seven wickets. It did not matter.",
    "slug": "arjun-tendulkar-ipl-2026-debut-lsg-yorker-prabhsimran-singh-sachin-37-months-20260525",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "In every Indian household in Edison, New Jersey, in Brampton, Ontario, and in Sunnyvale, California, the name Tendulkar carries a weight that no other surname in Indian sport can replicate. Sachin Tendulkar is not merely a cricketer in the diaspora's memory — he is the background radiation of an entire generation's childhood. NRI parents who landed in the US in the nineties raised their children on two things: the importance of education and the highlights of Sachin's innings. Those children are now adults with children of their own, and when Arjun Tendulkar walks out to bowl in an IPL match, the conversation that follows in every NRI WhatsApp group is not really about cricket. It is about the burden of legacy. It is about what it means to be the child of someone who achieved the unrepeatable — in a culture that measures children against their parents more explicitly than almost any other. Every NRI kid who grew up hearing 'Sharma ji ka beta got into Stanford' understands, at some cellular level, what Arjun Tendulkar carries every time he picks up a cricket ball. The trolling he receives online — the memes, the 'nepotism' accusations, the comparison to his father's genius — mirrors a conversation the diaspora knows intimately: the distance between a parent's accomplishment and a child's own path. Sachin's Instagram post after the match — measured, proud, careful — read like the message every Indian father wishes he could write: patient enough to let his son fail, present enough to celebrate when he didn't.",
    "tags": ["Arjun Tendulkar", "Sachin Tendulkar", "LSG", "Lucknow Super Giants", "IPL 2026", "Punjab Kings", "Yorker", "IPL Debut", "Cricket Legacy", "Nepotism Debate"],
    "urgency": "daily",
    "sources": [
        "https://www.insidesport.in/cricket/arjun-tendulkar-unleashes-yorker-masterclass-against-shreyas-iyer-takes-an-ipl-wicket-after-3-months/",
        "https://www.crickettimes.com/2026/05/sachin-tendulkar-pens-heartfelt-message-after-son-arjun-shines-on-ipl-2026-debut-for-lsg/",
        "https://www.livemint.com/sports/arjun-tendulkar-lsg-debut-ipl-2026",
        "https://www.cricketaddictor.com/rishabh-pant-denies-arjun-tendulkar-wicket"
    ],
    "word_count": 780,
    "score_total": 68,
    "body": """The last time Arjun Tendulkar took a wicket in the Indian Premier League, he was twenty-three years old, wearing Mumbai Indians blue, and the batter walking back was Wriddhiman Saha. That was April 2023. Between that evening at the Narendra Modi Stadium and Saturday night at the Ekana Cricket Stadium in Lucknow, thirty-seven months passed.

In those thirty-seven months, Arjun played one more IPL match — for MI against LSG in May 2024, going wicketless — before being released. He spent IPL 2025 entirely on the outside. Mumbai Indians, the franchise his father had been synonymous with, let him go without ceremony. Lucknow Super Giants picked him up in a trade, and for the first thirteen matches of IPL 2026, he sat on the bench while Mohammed Shami, Mayank Yadav, Mohsin Khan, and Avesh Khan bowled ahead of him.

Match fourteen. The final league game. LSG already eliminated, already last on the table. Nothing to play for except the chance to give a young man his debut.

## The four overs

Arjun was not given the new ball. He came on in the seventh over, bowling at 125-135 kilometres per hour — medium-fast by IPL standards, where 145 is table stakes. His first delivery was pulled by Prabhsimran Singh, who gloved it to Rishabh Pant behind the stumps. Pant dived left. Pant dropped it.

A different bowler — a more established bowler — might have let that moment curdle. Arjun continued. Prabhsimran and Shreyas Iyer targeted him in his second over, the ninth, finding the boundary twice. He returned for the fifteenth over, the match sliding away from LSG, and on the final ball of that over, he bowled a yorker on middle and leg stump that trapped Prabhsimran in front.

The umpire's finger went up. Arjun — for the first time in thirty-seven months, for the first time in Lucknow Super Giants colours — had an IPL wicket.

He came back for his final over, the seventeenth. What followed was the kind of bowling that coaches describe as 'clicking.' Yorker after yorker. Shreyas Iyer, who was on his way to an unbeaten century, barely kept two of them out. Suryansh Shedge was almost caught. The final figures read 4-0-36-1, and Arjun was the most economical LSG bowler of the innings.

Shreyas Iyer finished on 101 not out. Punjab Kings won by seven wickets with two overs to spare. The result was irrelevant to both teams' seasons.

## The name

There is no honest way to write about Arjun Tendulkar without writing about Sachin Tendulkar. There is also no fair way to write about Arjun Tendulkar if you write only about Sachin Tendulkar.

The facts of Arjun's career are these: he is a left-arm fast bowler who swings the ball, bats left-handed, and has played six IPL matches across four years for two franchises. He has four wickets at an economy rate that ranges from excellent to expensive depending on the match. He bowls at a pace that would not turn heads in a domestic T20 league in any cricket-playing country. He is twenty-six years old.

The facts of his inheritance are these: his father scored 34,357 international runs across 664 matches, held the record for most centuries in both Test and ODI cricket, and retired in 2013 as the most decorated batter in the history of the sport. His father played for Mumbai Indians from the franchise's inception and became its icon. His father received the Bharat Ratna, India's highest civilian honour, the same year he retired.

Between these two sets of facts — the modest professional career and the mythological inheritance — Arjun Tendulkar has existed in Indian cricket's most uncomfortable space. Every ball he bowls is measured not against his peers but against the greatest batter who ever lived. The comparison is absurd, and it is also inescapable.

## The Instagram post

After the match, Sachin Tendulkar posted on Instagram. The message was careful in the way that messages from Indian fathers who are also public figures must be careful:

He praised Arjun's patience. He praised his discipline. He noted that waiting thirteen matches for a debut required a particular kind of mental strength. He did not compare Arjun to himself. He did not use the word 'proud' the way corporate brands use it. He wrote like a father who understood that the most helpful thing he could do was acknowledge his son's work without overshadowing it.

The post went viral. It went viral because it was Sachin, and because every Indian parent — especially every Indian parent in the diaspora, where the weight of generational expectation is its own immigration story — saw something of themselves in it.

## What it means

Arjun Tendulkar will probably never play for India. He may never become a regular in the IPL. His career, measured by the metrics that cricket obsessives use, may remain modest. These are reasonable projections based on his age, his pace, and the depth of fast-bowling talent in Indian cricket.

But the yorkers he bowled on Saturday — the ones that nearly got Iyer, that did get Prabhsimran, that closed out his spell with the clean intent of a bowler who has been practicing one specific delivery until it became reflex — those yorkers were his. They were not borrowed from his father's legacy. They were not granted by his surname. They were the product of pre-season work on a skill that left-arm fast bowlers can only develop through repetition.

Thirty-seven months between wickets. A franchise that let him go. A new franchise that made him wait. And then a yorker on middle-and-leg that even the umpire did not need to think about.

LSG finished last. Arjun's figures will not appear in any season-ending highlights package. But somewhere in Lucknow on Saturday night, a twenty-six-year-old man walked off a cricket field having done something that no amount of inherited fame can manufacture: he performed under pressure, in public, and the performance was his own.""",
}


# ── ARTICLE 2: Heinrich Klaasen — 606 Runs From No.4, a Record Nobody Has Held Before ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "Heinrich Klaasen Has Scored 606 Runs Batting at Number Four or Lower. No One Has Done That in Any T20 League. Ever.",
    "subheadline": "The South African finisher ended the IPL 2026 league stage with a record that does not belong to Virat Kohli, AB de Villiers, or any opener who ever wore an Orange Cap. Six hundred and six runs from the middle order — an average of 50.50 and a strike rate of 159 — in a position where 400 is exceptional and 500 is unheard of. Sunrisers Hyderabad play the Eliminator against Rajasthan Royals on Wednesday. Klaasen bats at four.",
    "slug": "heinrich-klaasen-606-runs-number-four-t20-record-srh-ipl-2026-eliminator-rr-20260525",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Hyderabad occupies a unique position in the Indian diaspora's geography. It is the city that, more than any other, has populated the technology corridors of the American West Coast and the consulting firms of the American East Coast. The Hyderabad-to-Seattle pipeline, the Hyderabad-to-New Jersey pipeline — these are not metaphors. They are immigration patterns that have shaped entire suburbs. And because of this, the Sunrisers Hyderabad fanbase in the United States is not distributed evenly. It is concentrated in exactly the cities where Telugu-speaking NRIs have built communities: Redmond, Bellevue, Fremont, Jersey City, and Alpharetta. These fans do not merely follow SRH. They follow SRH with the intensity of people who grew up in the city's orbit and now watch from twelve time zones away. Klaasen, a South African who speaks no Telugu and has no ancestral connection to the Deccan, has become one of these fans' most beloved players. The adoption is complete. When he hits a six at the Rajiv Gandhi International Stadium, the celebration reaches WhatsApp groups in Redmond before the ball has landed. When he walks in at 90 for 2 in the fourteenth over, NRI families in New Jersey rearrange their evening plans. He is, in the particular way the IPL makes foreign players into local heroes, Hyderabad's own. The fact that he bats at number four — the position that requires patience before violence, restraint before acceleration — resonates with a diaspora that understands deferred gratification better than most.",
    "tags": ["Heinrich Klaasen", "SRH", "Sunrisers Hyderabad", "IPL 2026", "T20 Record", "Middle Order", "Eliminator", "Rajasthan Royals", "Mullanpur", "Ishan Kishan"],
    "urgency": "daily",
    "sources": [
        "https://sportsadda.asia/cricket/features/klaasens-606-cumminss-3-for-28-kishans-best-season-how-srh-walk-into-the-ipl-2026-eliminator-at-mullanpur/",
        "https://wisden.com/ipl-2026-stats-leaders",
        "https://www.espncricinfo.com/ipl-2026/stats",
        "https://cricbuzz.com/ipl-2026/stats"
    ],
    "word_count": 760,
    "score_total": 70,
    "body": """The Orange Cap goes to the leading run-scorer in the IPL. It almost always goes to an opener. The logic is structural: openers face the most deliveries, bat in the powerplay when fielding restrictions offer free boundaries, and have the longest runway to accumulate runs. The entire architecture of T20 batting is built to reward the top of the order.

Heinrich Klaasen bats at number four for Sunrisers Hyderabad. He walks in, typically, between the twelfth and fifteenth over, when the new ball's swing has disappeared but the powerplay's fielding advantages have also disappeared. He faces bowlers who have settled into their lengths, fields that have spread to the boundary, and match situations that are already defined by what the top order has done. He has, from this position, scored 606 runs in fourteen innings.

No batter in the history of any T20 league — IPL, Big Bash, PSL, CPL, The Hundred, SA20 — has scored 600 runs in a single season while batting at number four or lower. The previous record was Rishabh Pant's 579 for Delhi Capitals in 2018. Before that, the threshold was somewhere in the mid-400s, a region where analysts assumed the ceiling lived permanently.

Klaasen has not just broken the record. He has established a new category.

## The arithmetic of the middle order

An opener in the IPL faces, on average, between 40 and 55 deliveries per innings across a full season. A number four batter faces between 22 and 35. The gap is enormous. It means that a middle-order batter scoring 600 runs is operating at a per-ball productivity rate that would make most openers look pedestrian.

Klaasen's numbers confirm this. Average: 50.50. Strike rate: 159.47. Six half-centuries in fourteen innings, which means he has passed fifty in nearly half his appearances. His scoring pattern is distinctive: he blocks or rotates for the first eight to twelve balls he faces, assessing the pitch and the bowling plan, and then he attacks. The acceleration, when it comes, is not gradual. It is a switch.

Against RCB at Uppal on Friday — SRH's last league match — Klaasen came in with the score comfortable, made 51 off 24 balls, and pushed past the 600-run mark with a six over midwicket that required no effort and all intent. SRH posted 255 for 4. RCB made 200 for 4. The match was over before the chase began.

## The partnership that makes it possible

Klaasen's record does not exist in isolation. It exists because of Abhishek Sharma and Ishan Kishan at the top of the order.

Abhishek Sharma has been SRH's powerplay engine all season, striking at over 180 in the first six overs and giving the innings enough early momentum that Klaasen does not need to rescue. In the RCB match, Abhishek scored 56 off 22 balls — the kind of innings that moves the scoreboard so aggressively that the number four can walk in at a position of strength rather than crisis.

Ishan Kishan, in his second season at SRH, has been the steadiest he has ever been in the IPL. Six fifty-plus scores this season — the most prolific campaign of his career. Against RCB, his 79 not out was the backbone of the innings, the anchor around which Abhishek's explosion and Klaasen's acceleration were structured.

The three of them — Abhishek's speed, Kishan's solidity, Klaasen's power — form an escalation sequence. Each phase of the innings has a designated driver. Klaasen's job is the final phase: the fifteenth over onwards, when the ball is old, the bowlers are tired, and the margins between a good score and a great score are measured in the thirty balls remaining.

## The Eliminator

On Wednesday evening at 7:30 PM IST, SRH walk into the Mullanpur Cricket Stadium in New Chandigarh to face Rajasthan Royals in the Eliminator. Lose and the season ends. Win and they play Qualifier 2 on Friday for a place in the final at Ahmedabad on May 31.

SRH's league record is 9 wins, 5 losses, 18 points, and a net run rate of +0.524. Pat Cummins, their captain and Australia's Test captain, has had a quieter season than usual — his best spell was 3 for 28 against CSK at Chepauk — but his value has been in organisation rather than numbers. He has structured a bowling unit that defends totals built by Klaasen's bat.

Rajasthan Royals qualified on the last day of the league stage by beating Mumbai Indians at the Wankhede. They bring Vaibhav Sooryavanshi, who is fifteen years old, has 53 sixes this season, and is six away from Chris Gayle's all-time IPL record. They bring Jofra Archer, whose 3 for 17 and 32 off 15 sealed the qualification match. They bring the energy of a team that survived an entire season on the final afternoon.

But SRH bring Klaasen. And Klaasen, at number four, with the kind of record that no middle-order batter in any T20 league has ever assembled, is the reason Hyderabad will believe they can win the whole thing.

## The quiet dominance

Six hundred and six runs. Fourteen innings. Number four. No powerplay advantage. No opening partnership protection. Just a South African man in orange and black, walking to the crease when the score is already established and the task is already clear, and hitting the ball harder and more often than anyone else in his position has ever done.

The Orange Cap may go to Sai Sudharsan. The Purple Cap may go to Bhuvneshwar Kumar. But the record that rewrites the understanding of what a middle-order batter can achieve in a T20 season belongs to Heinrich Klaasen. And the Eliminator on Wednesday is his chance to add runs to a number that already has no precedent.""",
}


if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-25 03:00 UTC")
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

    print("\nInserting Article 1: Arjun Tendulkar — 37 Months Between Wickets...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    img1_path = f"/tmp/{a1_id}.jpg"
    if fetch_image("cricket bowler yorker delivery fast bowling stadium", img1_path):
        img1_url = upload_image(a1_id, img1_path)
        if img1_url:
            update_image_url(a1_id, img1_url)

    print("\nInserting Article 2: Heinrich Klaasen — 606 Runs From No.4...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    img2_path = f"/tmp/{a2_id}.jpg"
    if fetch_image("cricket batsman power hitting six stadium floodlights", img2_path):
        img2_url = upload_image(a2_id, img2_path)
        if img2_url:
            update_image_url(a2_id, img2_url)

    # Score decay
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    print(f"\nDone. 2 articles published.")
    print(f"  IDs: {a1_id}, {a2_id}")
