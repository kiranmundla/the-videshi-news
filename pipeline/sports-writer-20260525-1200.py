#!/usr/bin/env python3
"""Sports writer — 2026-05-25 12:00 UTC run (05:00 PDT): 2 articles + score decay."""

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


# ── ARTICLE 1: Suryakumar Yadav — T20I Captaincy in Limbo ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Suryakumar Yadav Won India the T20 World Cup Three Months Ago. Now the Selectors Are Not Sure He Should Be in the T20I XI at All.",
    "subheadline": "The India T20I captain scored 210 runs in twelve IPL 2026 innings at an average of 17.5. Even the most inexperienced pacers have found a plan against him: straight, hard lengths, no variation required. The national selectors are leaning towards a change. But Gautam Gambhir — the man who gave him the nickname 'SKY' at Kolkata Knight Riders — may be the only person standing between him and the end of his captaincy. The decision will shape India's T20 future through the Los Angeles 2028 Olympics.",
    "slug": "suryakumar-yadav-t20i-captaincy-selectors-gambhir-ipl-2026-form-india-20260525",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "In every Indian household in the United States that has a television and a Willow subscription, there is a version of this conversation happening right now. The father says Suryakumar Yadav won the World Cup, and that should buy him time. The son says 210 runs at 17.5 is 210 runs at 17.5, and sentimentality is not a selection criterion. The mother, who may or may not follow cricket but who recognises the dynamics of a workplace where one person's loyalty to another overrides performance metrics, says quietly that this is about Gambhir and Surya being friends, not about cricket at all. This conversation — about whether past glory earns future patience, about whether institutions should reward loyalty or results, about whether the person who brought you the trophy gets to keep the job even when the numbers say he shouldn't — is not a cricket conversation. It is the conversation every NRI professional has had about themselves, about their manager, about the H-1B colleague who was brilliant in the interview but has been coasting since the green card came through. The diaspora understands meritocracy not as an abstraction but as a daily condition of survival. You cannot coast in Cupertino. You cannot coast in Edison. You cannot coast on a work visa in a country that will send you home if your employer decides you are no longer essential. When Indian cricket debates whether Suryakumar Yadav should keep his captaincy on the strength of what he did three months ago rather than what he is doing now, every NRI in America recognises the question. It is the same question their performance review asks every quarter.",
    "tags": ["Suryakumar Yadav", "India T20I", "Captaincy", "Gautam Gambhir", "IPL 2026", "Mumbai Indians", "Tilak Varma", "Shubman Gill", "Shreyas Iyer", "BCCI", "Ajit Agarkar", "T20 World Cup", "Los Angeles 2028"],
    "urgency": "daily",
    "sources": [
        "https://www.sportsyaari.com/cricket/suryakumar-yadavs-india-t20i-captaincy-future-hangs-on-gautam-gambhirs-call-report-27432/",
        "https://cricketaddictor.com/cricket-news/suryakumar-yadav-refuses-to-quit-india-t20i-captaincy-no-wrist-issues-455525/",
        "https://insidesport.in/cricket/gautam-gambhir-holds-key-for-india-t20-captaincy-not-suryakumar-yadav-but-tilak-varma-in-race/",
        "https://www.sportsyaari.com/cricket/5-ipl-2026-breakout-stars-who-could-make-indias-t20i-squad-for-ireland-and-england-series-27332/"
    ],
    "word_count": 820,
    "score_total": 72,
    "body": """The numbers are the prosecution's case, and they do not require interpretation.

Suryakumar Yadav, India's T20I captain, played twelve innings in IPL 2026 for Mumbai Indians. He scored 210 runs. His average was 17.5. His strike rate — 148 — was below the tournament average for recognised batters. He did not score a single fifty in the entire campaign. Mumbai Indians finished with four wins and ten losses, their worst season in franchise history.

Three months ago, he lifted the T20 World Cup trophy.

## The bowler's plan

A senior BCCI source, speaking to PTI on condition of anonymity, identified the problem with the precision of someone who has watched it happen repeatedly and stopped being surprised.

"Even the rookiest of pacers are just bowling straight hard lengths and he has no answer."

That sentence, twelve words long, contains the entire crisis. Suryakumar Yadav's genius — the wristwork, the audacious scoops, the ability to manufacture angles that other batters cannot see — requires the bowler to offer width or pace on the stumps. A hard length on middle-and-off, back of a length, hitting the surface and holding its line: this is the delivery that every academy coach in India teaches in the first month. And it is the delivery that the T20 World Cup-winning captain of India currently cannot score off.

The source went further. "Selectors don't see him playing the Los Angeles 2028 Olympics. It is as simple as that."

The Los Angeles Olympics, where cricket returns to the Games for the first time since 1900, will be played in T20 format. India's planning horizon extends to that tournament. If the selectors do not see Suryakumar Yadav in the 2028 squad, the question of whether he should captain the 2026 series against Ireland and England becomes secondary.

## The Gambhir factor

And yet: the captaincy has not changed. The reason is one man.

Gautam Gambhir, India's head coach, gave Suryakumar Yadav the nickname "SKY" during their time together at Kolkata Knight Riders. Their bond is not recent or professional — it is old, personal, and complicated in the way that relationships between mentors and their proteges always are. Gambhir backed Yadav for the captaincy before the T20 World Cup. Yadav won the World Cup. The vindication was total.

Now the form has collapsed, and the selectors — led by chief selector Ajit Agarkar — are leaning towards change. But the BCCI hierarchy values the coach-captain equation. If Gambhir says he wants Suryakumar to continue, the selectors will have to weigh that preference against their own judgment.

"Ajit and Gautam Gambhir need to be on the same page," the BCCI source told PTI. The implication is clear: they are not currently on the same page.

## The succession

Three names circulate in the discussions about what comes next.

**Shreyas Iyer** brings tactical sharpness and IPL leadership experience. He captained Punjab Kings this season and led by example. But his working equation with Gambhir is delicate — after KKR's 2024 IPL title was widely projected as Gambhir's success as mentor rather than Iyer's as captain, the relationship cooled. Appointing Iyer would require Gambhir to accept a captain he may not fully trust.

**Shubman Gill** was previously viewed by Agarkar's panel as a long-term all-format leader before a dip in form slowed that plan. His IPL 2026 season — 616 runs as Gujarat Titans captain, the third captain in IPL history to cross 600 runs in back-to-back seasons, and a T20 captaincy runs tally that now surpasses Sachin Tendulkar's — has restored his candidacy entirely. He plays Qualifier 1 against RCB in Dharamshala on Tuesday.

**Tilak Varma** is the quiet outsider. At twenty-two, he has already been named captain of the India A side for a tri-nation series in Sri Lanka from June 9 to 21. The BCCI source said: "Don't rule out Tilak if Surya is sacked. There's a reason that Tilak has been made captain for tri-nation A series where selectors would get to see his leadership skills." Varma scored 356 runs for Mumbai Indians in IPL 2026 — more than any of his teammates — and did so in a side that was losing almost every match. Performing in a losing team, as any NRI professional who has been the lone performer in a struggling department knows, is its own form of audition.

## The timeline

India play two T20Is against Ireland on June 26 and 28, followed by a five-match series in England from July 1 to 11. The squads will be announced in early June. That gives the selectors and Gambhir approximately two weeks to resolve the captaincy question.

Suryakumar Yadav himself has made his position clear. He wants to tour. He told people close to him that he is fit, that his wrist — which was rumoured to be injured — is fine, and that he intends to play the Mumbai T20 League starting June 1 for the Triumph Knights at the Wankhede to stay match-ready. He is, by all accounts, a man who does not intend to step aside.

The question is not whether he wants to continue. The question is whether the numbers allow it. And the numbers, which are the only language that selection committees are supposed to speak, say 210 runs at 17.5 with no answer to a hard length on middle stump.

The World Cup trophy is three months old. In Indian cricket, three months is either a lifetime or nothing at all, depending on who is making the decision.""",
}


# ── ARTICLE 2: Mumbai Indians — Four Wins, Ten Losses, and the End of an Era ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "Mumbai Indians Had Four World Cup Winners, the Most Expensive Squad in IPL History, and Rohit Sharma on the Bench. They Won Four Matches.",
    "subheadline": "Jasprit Bumrah took four wickets in the entire tournament. Hardik Pandya scored 172 runs. Suryakumar Yadav averaged 17.5. Rohit Sharma played eight matches, missed the rest with a hamstring injury, and was used as an impact substitute when he returned. Head coach Mahela Jayawardene called it 'a combination of a lot of things.' The combination produced the worst season in the five-time champions' history.",
    "slug": "mumbai-indians-ipl-2026-worst-season-four-wins-ten-losses-rohit-bumrah-pandya-jayawardene-20260525",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Mumbai Indians are the franchise that every NRI defaults to when someone back home asks which IPL team they support. Not because of geography — most NRIs in the Bay Area or New Jersey are not from Mumbai — but because of brand. Mumbai Indians are the Apple of the IPL: polished, dominant, expensive, and assumed to be competent even when the evidence suggests otherwise. Supporting them is the safe choice. It is the choice that does not require explanation at an office watch party. It is the choice that, until this season, never required an apology. This IPL, in desi WhatsApp groups from Fremont to Edison to Brampton, Mumbai Indians supporters went quiet around the fourth consecutive loss and stayed quiet for the rest of the tournament. The group chats that used to feature Bumrah bowling figures and Rohit cover drives were reduced to forwarded memes — the coping mechanism of a fanbase that had never needed to cope. Four wins in fourteen matches. The franchise that won five titles in eleven years could not win five matches in two months. For the diaspora, which left India carrying certain certainties — that the rupee would always be weaker than the dollar, that Sachin would always score runs, that Mumbai Indians would always be in the playoffs — this season was the sporting equivalent of a certainty failing. The franchise they chose because it never lost has now lost in a way that cannot be explained by bad luck or scheduling. It lost because the players did not perform, the coach could not fix it, and the captain's frustration was visible to a camera that never looks away.",
    "tags": ["Mumbai Indians", "IPL 2026", "Hardik Pandya", "Rohit Sharma", "Jasprit Bumrah", "Suryakumar Yadav", "Tilak Varma", "Mahela Jayawardene", "Season Review", "Wankhede"],
    "urgency": "daily",
    "sources": [
        "https://www.mykhel.com/cricket/mumbai-indians-coach-mahela-jayawardene-on-ipl-2026-performance-and-squad-struggles-014-434801.html",
        "https://4conservative.com/mumbai-indians-may-sack-hardik-pandya-ipl-2026",
        "https://crictracker.com/ipl-2026-mi-bring-mahipal-lomror-ruchit-ahir-injury-replacements-rr-clash",
        "https://ianslive.in/ipl-2026-bumrah-rohit-recovery-jayawardene-royals-clash"
    ],
    "word_count": 810,
    "score_total": 68,
    "body": """The table does not lie. Mumbai Indians played fourteen matches in IPL 2026. They won four. They lost ten. They were eliminated from playoff contention before the final week of the league stage — a sentence that, for a franchise that has won five IPL titles, reads like a misprint.

It is not a misprint.

## The numbers that matter

Start with the names. Mumbai Indians fielded four members of India's 2026 T20 World Cup-winning squad: Suryakumar Yadav, Jasprit Bumrah, Hardik Pandya, and Tilak Varma. They also had Rohit Sharma, the former India and MI captain who led the franchise to five of its titles. On paper, this was the most accomplished Indian core in the tournament.

On the field, the numbers told a different story.

| Player | Matches | Runs | Wickets | Note |
|---|---|---|---|---|
| Jasprit Bumrah | — | — | 4 | Season-low wicket total |
| Hardik Pandya | 14 | 172 | 4 | Captain; visible frustration |
| Suryakumar Yadav | 12 | 210 | — | Average: 17.5 |
| Tilak Varma | 14 | 356 | — | Only consistent performer |
| Rohit Sharma | 8 | 283 | — | Hamstring; used as impact sub |

Tilak Varma's 356 runs were the highest by any Mumbai Indians batter. He is twenty-two years old. That he was the most reliable performer in a squad that included two of India's all-time greats is not a compliment to Varma — it is an indictment of everyone else.

## The coach's verdict

Mahela Jayawardene, the head coach, sat before reporters on the eve of Mumbai Indians' final match — a match against Rajasthan Royals that meant nothing in the standings — and delivered his assessment. He did not raise his voice. He did not name names. He spoke in the measured tones of a man who has spent two months watching talent refuse to become performance.

"It's not fair just to bring up those four guys. As a group, a lot of the guys haven't been able to consistently perform — that's how I see it."

The deflection was professional. The subtext was clear: if the group failed, the individuals within the group failed. And the individuals who were paid the most, expected to deliver the most, and had the most international experience delivered the least.

Jayawardene explained that past Mumbai Indians seasons had featured "individual players winning matches by themselves." This season, that never happened. "We tried some youngsters also, but they also struggled in the heat of the moment. It's that sort of a season and that's something that we have to reflect on."

## The Rohit question

The most uncomfortable element of Mumbai Indians' IPL 2026 was the handling of Rohit Sharma.

The facts are these: Rohit sustained a hamstring injury early in the tournament. He missed several matches. When he returned, he was used as an impact substitute — the tactical substitution rule that allows teams to replace one player during the innings break. The former India captain, who has 283 runs in eight matches this season, was not a guaranteed starter in his own franchise's playing eleven.

Jayawardene insisted the decision was tactical, not fitness-related. "With the medical team, everything is 100 per cent. We're not putting him on the field because of what we've done in the past as well — it's just the team combination."

Translation: Rohit Sharma was fit to play. Mumbai Indians chose not to play him.

The image of Rohit Sharma sitting in the dugout while Mumbai Indians lost — game after game, week after week — will define this season more than any scorecard. It is the image of a franchise that had the most decorated Indian cricketer of the last decade on its roster and could not find a place for him in the eleven.

## The Pandya question

Hardik Pandya captained Mumbai Indians through the wreckage. His personal returns — 172 runs, four wickets — were below the standard expected of a franchise captain and India all-rounder. His frustration was visible. After a dropped catch in the match against Kolkata Knight Riders, the cameras caught a reaction that Jayawardene later contextualised.

"It is hard not just for Hardik, but for all of us to go through a season where we know that we had the talent, we had the squad, but we were not able to execute and perform to the best of our ability."

Reports suggest that Mumbai Indians' ownership is considering replacing Pandya as captain ahead of the 2027 season. Nothing has been confirmed. But the conversation — about whether a captain who won four out of fourteen matches can continue to lead a franchise that expects trophies — is already happening.

## What remains

Mumbai Indians' season ended not with a dramatic final-over defeat or a rain-affected washout but with the quiet realisation, somewhere around the ninth or tenth loss, that this team was not good enough. The talent was present. The experience was present. The budget was present. What was absent was the quality that separates a list of good players from a good team: the ability to perform together, under pressure, when the match requires it.

Jayawardene called it "a combination of a lot of things." He was being diplomatic. The combination was simpler than he suggested: four World Cup winners who could not win matches, a former captain who could not find a place in the eleven, a current captain whose frustration was louder than his contributions, and a franchise that spent more than any other team in the auction and got less than any other team in the standings.

Four wins. Ten losses. Five titles on the wall and nothing in the present.

The five-time champions will spend the next ten months wondering how they got here. The answer is in the numbers. It always is.""",
}


if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-25 12:00 UTC (05:00 PDT)")
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

    print("\nInserting Article 1: Suryakumar Yadav — T20I Captaincy in Limbo...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    img1_path = f"/tmp/{a1_id}.jpg"
    if fetch_image("cricket batsman dejected walking back pavilion stadium lights", img1_path):
        img1_url = upload_image(a1_id, img1_path)
        if img1_url:
            update_image_url(a1_id, img1_url)

    print("\nInserting Article 2: Mumbai Indians — Worst Season...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    img2_path = f"/tmp/{a2_id}.jpg"
    if fetch_image("empty cricket stadium seats blue and gold team colors night", img2_path):
        img2_url = upload_image(a2_id, img2_path)
        if img2_url:
            update_image_url(a2_id, img2_url)

    # Score decay
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    print(f"\nDone. 2 articles published.")
    print(f"  IDs: {a1_id}, {a2_id}")
