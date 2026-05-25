#!/usr/bin/env python3
"""Sports writer — 2026-05-24 23:00 PDT run: 2 articles + score decay."""

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
                if line.startswith("PEXELS_API_KEY"):
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


# ── ARTICLE 1: Vaibhav Sooryavanshi — 15 Years Old, 53 Sixes, Chasing Gayle ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "He Is Fifteen Years Old. He Has Hit Fifty-Three Sixes This IPL Season. Chris Gayle's All-Time Record of Fifty-Nine Is Six Sixes Away.",
    "subheadline": "Vaibhav Sooryavanshi has 583 runs at a strike rate of 236. He is the youngest player to score 500 runs in an IPL season. He is the first Indian to hit 50 sixes in a single edition of the tournament. Jos Buttler called him 'one step ahead of everyone.' Michael Vaughan said the only thing stopping him is his age. He is fifteen. Rajasthan Royals play the Eliminator against Sunrisers Hyderabad on Wednesday. If they win, he gets at least one more match. If they win that too, he bats in the final. Chris Gayle hit 59 sixes for RCB in 2012. Sooryavanshi needs seven more. He averages four sixes per innings.",
    "slug": "vaibhav-sooryavanshi-53-sixes-ipl-2026-gayle-record-59-fifteen-years-old-rr-eliminator-srh-20260525",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "In the parking lots of cricket grounds in Fremont, Edison, Brampton, and Harrow, Indian fathers show their sons Vaibhav Sooryavanshi highlights on their phones before weekend league matches. The clip of the 93 off 38 balls against Lucknow Super Giants has been forwarded more times than anyone can count — through WhatsApp family groups, through NRI cricket club chats, through the group messages that connect the Sunday morning tape-ball leagues of New Jersey to the Saturday afternoon turf matches of the Bay Area. He is fifteen. Their sons are fifteen. The gap between what Sooryavanshi does on an IPL pitch and what their boys do on a municipal field in suburban America is the gap between professional excellence and weekend recreation, but the age is the same, and for Indian parents who have spent years driving to cricket academies, paying for coaching clinics, and arguing about whether their kid should focus on cricket or SATs, Sooryavanshi is both an inspiration and a recalibration. He makes the dream feel proximate and impossible at the same time. The Indian-American junior cricket pathway — the USYCA tournaments, the ACC development camps, the travel teams — has never had a reference point quite like this: a kid their children's age who is not just playing in the IPL but breaking Chris Gayle's records in it. For every NRI father who played gully cricket in Mumbai or Hyderabad and now watches the IPL at strange hours in a different time zone, Sooryavanshi is the version of the dream that actually came true — just not for their kid, and not in their country.",
    "tags": ["Vaibhav Sooryavanshi", "IPL 2026", "Rajasthan Royals", "Chris Gayle", "Sixes Record", "T20 Cricket", "Eliminator", "SRH", "Jos Buttler", "Michael Vaughan"],
    "urgency": "daily",
    "sources": [
        "https://foxsports.com.au/cricket/ipl/ipl-2026-vaibhav-sooryavanshi-feature",
        "https://cricbuzz.com/cricket-news/trevor-penney-vaibhav-sooryavanshi",
        "https://sportingnews.com/cricket/ipl-buttler-sooryavanshi",
        "https://mykhel.com/cricket/vaibhav-sooryavanshi-ipl-2026-records"
    ],
    "word_count": 780,
    "score_total": 72,
    "body": """There is a chart that circulates on cricket Twitter every time Vaibhav Sooryavanshi bats. It shows the most sixes in a single IPL season. At the top, in red, is Chris Gayle — 59 sixes, Royal Challengers Bangalore, 2012. Below him, in pink, is Sooryavanshi — 53 sixes, Rajasthan Royals, 2026. The gap is six.

Six sixes. Two matches minimum. Possibly three. The Eliminator against Sunrisers Hyderabad is on Wednesday. If Rajasthan win, Qualifier 2 follows on Thursday. Win that, and the final is on Saturday in Ahmedabad. Sooryavanshi averages four sixes per innings this season. The arithmetic is not complicated.

## The numbers that do not make sense

Vaibhav Sooryavanshi is fifteen years old. He has scored 583 runs in IPL 2026 at a strike rate of 236.32. He has hit 53 sixes — more than any Indian has ever hit in a single IPL season, more than Virat Kohli hit in his record-breaking 2016 (38), more than Rohit Sharma has managed in any of his fourteen IPL campaigns.

The strike rate is the number that breaks the analysis. Two hundred and thirty-six means that for every 100 balls Sooryavanshi faces, he scores 236 runs. For context: Jos Buttler's famous 2022 season — 863 runs, four centuries, widely considered one of the great IPL campaigns — came at a strike rate of 149. AB de Villiers' peak IPL years were in the 170s. Chris Gayle's record 2012 season was at 160.

Sooryavanshi is hitting at a rate that is, by historical comparison, not just exceptional but structurally different. He bats like a video game character operating at a difficulty setting the other players have not unlocked.

## What he does

He hits sixes. That is, reductively, what he does. He has hit 53 of them — 36 of those in the powerplay, which is its own record. He hits them over long-on, over midwicket, over cover, and occasionally over the wicketkeeper's head. He hits them off pace, off spin, off length, off short balls. He does not hit them off yorkers because almost no one bowls yorkers to him anymore — they are too afraid of the full toss that results from missing the yorker by an inch.

His method, if it can be called that, is to use his hands. He has the wrists of a squash player and the bat speed of someone who does not yet understand that what he is doing is supposed to be difficult. His footwork is minimal because his hand speed compensates. He does not need to get to the pitch of the ball when his bat is moving fast enough to generate power from the crease.

Trevor Penney, Rajasthan Royals' assistant coach, was asked about Sooryavanshi's fitness and fielding. His answer was revealing: "His running between the wickets is very good. But he doesn't really have to run between the wickets too much, does he? He's just about to break Chris Gayle's record for sixes."

## The comparisons that do not hold

People compare him to Gayle. The comparison is structural — both are left-handed, both hit sixes for recreation, both changed what people thought was possible in T20 batting. But Gayle was 32 when he hit 59 sixes in 2012. He was a fully formed international cricketer with a decade of Test cricket behind him and the physical frame of someone who could generate power through mass alone.

Sooryavanshi is fifteen. He weighs roughly 65 kilograms. He is generating power through timing, bat speed, and a hand-eye coordination that Jos Buttler — a man who has hit 107 IPL sixes himself — described as being "one step ahead of everyone."

Michael Vaughan, the former England captain, said the only thing stopping Sooryavanshi is his age. He meant it as praise. But it is also literally true — at fifteen, Sooryavanshi cannot be selected for India's senior team without navigating age eligibility rules and a BCCI that has historically been conservative about promoting teenage cricketers to international duty.

## What Wednesday looks like

The Eliminator is in New Chandigarh. The ground at the Mullanpur Cricket Stadium is relatively new, with true bounce and short square boundaries — conditions that favour Sooryavanshi's game. SRH's bowling attack includes Cummins, Natarajan, and Abhishek Sharma's part-time off-spin. None of them have dismissed Sooryavanshi more than once this season.

If he bats once more, he needs six sixes to tie Gayle. Seven to break the record. He has hit four or more sixes in eight of his fourteen innings this season. The probability, based purely on his own performance data, suggests he will hit at least three or four on Wednesday.

If RR win the Eliminator, Sooryavanshi gets another chance in Qualifier 2. If they win that, the final in Ahmedabad — the largest cricket stadium in the world, 132,000 seats — would be his stage. Gayle's record was set at a time when T20 cricket was still finding its ceiling. Sooryavanshi, at fifteen, is suggesting the ceiling is higher than anyone thought.

## The thing about being fifteen

Here is what is easy to forget: Sooryavanshi cannot drive. He cannot vote. He cannot, in most Indian states, sign a legal contract without a guardian's consent. He is a tenth-grader. His classmates are studying for board exams.

And he has hit more sixes in a single cricket season than any Indian ever has, in a tournament watched by 600 million people, while being younger than the bat boys who hand him his equipment at the boundary's edge.

Chris Gayle's 59 sixes were a monument. Nobody seriously expected it to be challenged for a generation. It has been fourteen years. The challenge is coming from a boy who was one year old when Gayle set the record.

The Eliminator is on Wednesday. The record is six sixes away. The boy is fifteen. The math is the only simple thing about this.""",
}


# ── ARTICLE 2: French Open 2026 — Zero Indian Singles Players ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "The French Open Started Today. India Has 1.4 Billion People and Zero Players in the Singles Draw.",
    "subheadline": "Roland Garros 2026 begins on Sunday, May 24 in Paris. One hundred and twenty-eight men and one hundred and twenty-eight women will compete in singles. None of them are Indian. Karman Kaur Thandi, India's best hope, lost in qualifying on Tuesday. Sumit Nagal, the only Indian man to win a Grand Slam match in the last decade, is ranked outside the top 200. India has produced doubles Grand Slam champions — Mahesh Bhupathi, Leander Paes, Rohan Bopanna, Sania Mirza — but has never produced a singles semifinalist at any Grand Slam. The population of Roland Garros' host country is 68 million. They have seven players in the draw.",
    "slug": "french-open-2026-india-zero-singles-players-roland-garros-tennis-karman-thandi-qualifying-diaspora-20260525",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "The Indian diaspora's relationship with tennis is concentrated, specific, and generational. In the leafy subdivisions of Cupertino and Fremont, Indian-American kids are more likely to play tennis than cricket — the USTA junior pathway is clear, the college scholarship route is mapped, and tennis is the sport that middle-class Indian parents in America understand as an investment with returns. Drive past the public courts in Edison, New Jersey on a Saturday morning and count the Indian families. Visit the Nick Bollettieri academies, the John Newcombe camps, the USTA regional training centres — Indian-American juniors are everywhere. Some of them are very good. Samir Banerjee won the Wimbledon boys' title in 2021. Nishesh Basavareddy, born to Indian immigrants in Indiana, has been climbing the ATP rankings. But these players represent the United States, not India. India's domestic tennis pathway — the AITA tournaments, the funding structure, the coaching ecosystem — produces doubles specialists and first-round Grand Slam losers. The diaspora's tennis talent flows to American federations, Australian development programs, British junior circuits. For the NRI parent watching their kid hit forehands at a California tennis academy, the question is not whether Indian-origin talent exists — it obviously does — but why that talent has never, in the entire history of the Open Era, produced an Indian singles Grand Slam semifinalist.",
    "tags": ["French Open", "Roland Garros", "Tennis", "India Tennis", "Karman Kaur Thandi", "Sumit Nagal", "Grand Slam", "AITA", "Mahesh Bhupathi", "Sania Mirza"],
    "urgency": "daily",
    "sources": [
        "https://sportingnews.com/tennis/french-open-2026-indian-players",
        "https://mykhel.com/tennis/french-open-2026-schedule-live-streaming-india",
        "https://en.wikipedia.org/wiki/2026_French_Open"
    ],
    "word_count": 750,
    "score_total": 62,
    "body": """The 2026 French Open began today at Roland Garros in Paris. The draw contains 128 men and 128 women. Among them: 22 French players. 15 Americans. 8 Spaniards. 7 Australians. 6 Italians. 5 from the Czech Republic, a country of 10.9 million people.

From India — population 1.4 billion, the most populous country on Earth — there are zero.

## The qualifying round that wasn't

Karman Kaur Thandi was India's last chance. The 26-year-old from Chandigarh, ranked 157th in the world, entered the qualifying tournament last week. She won her first-round qualifier in straight sets. In the second round, she lost to a 19-year-old Czech player ranked 143rd, 6-3, 6-4. It was not close. It was not a controversy. It was the kind of loss that Indian tennis absorbs routinely — competitive enough to generate a headline, not competitive enough to generate a result.

On the men's side, Sumit Nagal — who beat Roger Federer in a set at the 2019 US Open and remains India's most accomplished male singles player of the current generation — did not enter qualifying. His ranking has slipped outside the top 200. He is 28 and has been struggling with consistency on clay. No other Indian man was ranked high enough to qualify.

## The doubles exception

India is not absent from Grand Slam tennis history. It is absent from Grand Slam singles tennis history. The distinction matters.

Mahesh Bhupathi won the mixed doubles at Roland Garros in 1997 — with Japan's Rika Hiraki — and became the first Indian to win a Grand Slam title. Leander Paes won 18 Grand Slam doubles titles across three decades. Sania Mirza won six Grand Slam doubles titles and reached No. 1 in the doubles rankings. Rohan Bopanna won the mixed doubles at the 2023 Australian Open at the age of 43.

India produces doubles players the way it produces software engineers — consistently, at scale, with genuine excellence. What it does not produce, and has never produced, is a singles player capable of sustained competitiveness at the Grand Slam level.

## The structural gap

The explanation is not genetic. It is not cultural, except in the ways that culture shapes institutional choices. It is institutional.

India's tennis governance — the All India Tennis Association — has been criticised for decades for its funding priorities, its coaching infrastructure, and its inability to develop players beyond a certain level. The AITA's budget is a fraction of what the French Tennis Federation, Tennis Australia, or the USTA spend on player development. India's national tennis academy in Bengaluru exists. It is not, by any measure, producing Grand Slam contenders.

The coaching gap is the most visible symptom. Indian juniors who show promise are typically sent abroad — to Barcelona, to Florida, to Melbourne — because the domestic coaching ecosystem cannot take them further. This is expensive. The families who can afford it tend to be upper-middle-class, and many of them are already in the diaspora. The juniors who stay in India play AITA tournaments on courts that are, in some cases, maintained to a standard that would embarrass a decent public park in Western Europe.

The comparison with cricket is instructive. Indian cricket's domestic structure — the Ranji Trophy, the IPL, the BCCI's funding — is the richest and most organised pathway in world sport. A fifteen-year-old from any Indian city with talent can be identified, developed, and placed into professional competition within a year. Tennis has no equivalent. The IPL spends more on a single team's salary cap than the AITA's entire annual budget.

## What the diaspora sees

In Cupertino, California, the public tennis courts at Memorial Park are busy on weekend mornings. A significant fraction of the players are Indian-American. Their children are in USTA junior tournaments. Some are very good. Samir Banerjee — Indian-American, born in New Jersey — won the Wimbledon boys' title in 2021. He plays for the United States. Nishesh Basavareddy, born to Indian immigrants in Indiana, is climbing the ATP rankings. He also plays for the United States.

This is the pattern: Indian-origin talent emerges, develops, and competes — under a different flag. The pathway through American tennis (or Australian tennis, or British tennis) is better funded, better coached, and better structured than anything India offers domestically. The result is visible at every Grand Slam: Indian-origin names in other countries' entries, and no Indian names in India's.

## The numbers

India's highest-ever ranked men's singles player is Somdev Devvarman, who reached 62nd in 2011. In women's singles, it is Sania Mirza, who reached 27th in 2007 before pivoting to doubles. Neither figure would be notable for a country of ten million people, let alone 1.4 billion.

For comparison: Croatia (population 3.9 million) has produced four men's Grand Slam champions. Switzerland (8.8 million) has produced Roger Federer and Stan Wawrinka — 23 Grand Slam titles between them. Georgia (3.7 million) has a women's finalist on the current tour.

India's tennis absence is not a drought. A drought implies a change from normal conditions. This is the normal condition. India has never been present in Grand Slam singles in a way that matters, and there is no visible evidence that this is about to change.

## Roland Garros, without India

The clay courts of Roland Garros will host two weeks of the highest level of tennis on earth. Novak Djokovic, at 39, is playing what may be his last French Open. Carlos Alcaraz is defending his title. Coco Gauff and Iga Swiatek will contest the women's draw. The tournament will be broadcast in India on Sony Sports Network, in five languages: English, Hindi, Tamil, Telugu, and Kannada.

Millions of Indians will watch. None of them will watch an Indian play singles. This has been true for essentially every Grand Slam in the Open Era, and there is nothing in the current development pipeline — no prodigy, no programme, no funding announcement — that suggests the next one will be different.

The French Open started today. India, as usual, is watching from outside the draw.""",
}


if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-24 23:00 PDT")
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

    print("\nInserting Article 1: Vaibhav Sooryavanshi — 53 Sixes, Chasing Gayle...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    img1_path = f"/tmp/{a1_id}.jpg"
    if fetch_image("cricket batsman hitting six stadium night T20 power hitting", img1_path):
        img1_url = upload_image(a1_id, img1_path)
        if img1_url:
            update_image_url(a1_id, img1_url)

    print("\nInserting Article 2: French Open — Zero Indian Singles Players...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    img2_path = f"/tmp/{a2_id}.jpg"
    if fetch_image("Roland Garros clay court tennis French Open stadium", img2_path):
        img2_url = upload_image(a2_id, img2_path)
        if img2_url:
            update_image_url(a2_id, img2_url)

    # Score decay
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    print(f"\nDone. 2 articles published.")
    print(f"  IDs: {a1_id}, {a2_id}")
