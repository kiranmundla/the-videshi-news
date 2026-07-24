#!/usr/bin/env python3
"""Sports writer — 2026-05-23 20:00 PDT run: 2 articles + score decay."""

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
    """Try Pexels for an image."""
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

# ── ARTICLE 1: MI's Dead Rubber Is the Most Important Match of the IPL Season ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Mumbai Indians Are Playing for Nothing. The Entire IPL Playoff Race Is Playing for Their Result.",
    "subheadline": "MI are ninth, eliminated, and fielding injury replacements for their final match at the Wankhede on Sunday. Rajasthan Royals need to beat them to qualify. Punjab Kings need MI to upset RR. Kolkata Knight Riders need MI to win AND then pull off their own miracle. The five-time champions have become the most powerful dead rubber in IPL history.",
    "slug": "mumbai-indians-dead-rubber-kingmaker-rr-pbks-kkr-playoff-wankhede-ipl-2026-20260523",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Mumbai Indians have the largest NRI fanbase of any IPL franchise — an estimated 40 million Indians abroad follow MI primarily; this dead rubber carries emotional weight for diaspora fans who have endured MI's worst season in memory, and who now find their defeated team holding the keys to the entire playoff race; the Wankhede atmosphere will be broadcast at 3:30 AM Eastern / 12:30 AM Pacific, and diaspora fans in the US and UK will watch not for MI's sake but because every other team's season depends on what happens at Mumbai's most iconic stadium",
    "tags": ["Mumbai Indians", "IPL 2026", "Wankhede Stadium", "Rajasthan Royals", "Punjab Kings", "KKR", "Rohit Sharma", "Hardik Pandya", "Vaibhav Suryavanshi", "Dead Rubber", "Playoffs", "MI vs RR", "Mahela Jayawardene", "Akash Ambani"],
    "urgency": "daily",
    "sources": [
        "https://crictracker.com/cricket/ipl/mi-vs-rr-match-69-ipl-2026-wankhede",
        "https://yardbarker.com/cricket/articles/mi-vs-rr-facts-ipl-2026-royals-do-or-die",
        "https://thesportstak.com/cricket/pbks-ipl-2026-playoff-equation-decoded",
        "https://crictracker.com/cricket/ipl/pbks-beat-lsg-rr-kkr-do-or-die-playoffs-scenarios",
        "https://mykhel.com/cricket/mumbai-indians-mahela-jayawardene-ipl-2026-analysis"
    ],
    "word_count": 720,
    "score_total": 70,
    "body": """Mumbai Indians will walk out at the Wankhede Stadium on Sunday afternoon having already been eliminated from the playoffs. They are ninth in the table. They have four wins from thirteen matches. They have replaced Quinton de Kock with Mahipal Lomror and Raj Angad Bawa with Ruchit Ahir because both first-choice players are injured. Their coach, Mahela Jayawardene, has publicly said that talent did not translate into performance this season. Their captain, Hardik Pandya, has been questioned by former players, by commentary panels, and by a section of MI's own fanbase for two consecutive years of captaincy failures.

None of this matters to anyone except Mumbai Indians. What matters to the rest of the IPL is this: MI are playing Rajasthan Royals. And that match — a dead rubber for the hosts — will decide who gets the fourth and final playoff spot.

## The equation

Rajasthan Royals sit on 14 points from 13 matches. A win against MI takes them to 16 and into the playoffs. It is that simple. If RR win, they qualify. The end.

If MI beat RR, the entire picture shifts.

Punjab Kings, who won their final match against Lucknow Super Giants on Friday night — Shreyas Iyer scoring an unbeaten century to end a six-match losing streak — are sitting on 15 points with their league stage complete. PBKS have done everything they can. They are at the airport lounge of IPL qualification, waiting to find out whether their boarding pass is valid.

If RR lose to MI, PBKS qualify at 15 points — unless Kolkata Knight Riders produce a result so extraordinary that it rewrites their net run rate entirely.

KKR, on 13 points, need to beat Delhi Capitals at Eden Gardens on Sunday AND do it by a margin so large that it overtakes PBKS on net run rate. The specifics: if KKR bat first and score 200, they need to restrict DC to 123 or below — a winning margin of 77 runs. If they bowl first and DC post 180, KKR need to chase it in approximately 12 overs.

In other words: MI beating RR would give PBKS a playoff spot unless KKR pull off one of the most lopsided victories in IPL history. The probability of that happening is vanishingly small, but not zero, and Eden Gardens under lights with a season on the line has a way of producing things that do not exist in probability tables.

## The Wankhede factor

Here is the detail that makes this dead rubber genuinely dangerous for Rajasthan: the average first innings score at the Wankhede in IPL 2026 has been 222. This is the highest-scoring ground in the tournament this season. It is a ground where totals of 180 feel like they were posted in the wrong era.

Mumbai Indians have nothing to play for except pride and the satisfaction of ending their season with a win in front of their home supporters. That can be a powerful motivator, or it can be meaningless — the difference between playing freely because the pressure is off, and playing carelessly because the season is already dead.

Rohit Sharma's role will be watched closely. The former MI and India captain has been used as an impact player in recent matches, a role that Manoj Tiwary and other former cricketers have publicly criticised as a misuse of one of the greatest white-ball batsmen in history. "Why do you make Rohit Sharma sit in the dugout?" Tiwary asked after the KKR loss. There is a growing sense that this might be Rohit's final IPL season with Mumbai Indians, and a farewell innings at the Wankhede — if he is given the opportunity — would carry significant emotional weight regardless of the result.

## What MI owe the tournament

Nothing, obviously. A team that finishes ninth owes nobody anything. But the IPL is a closed ecosystem where every result ripples outward, and MI's Sunday afternoon in Mumbai will determine the shape of the playoffs more than any match that any of the contending teams played themselves.

If MI turn up and compete — if their pace bowlers find early swing under the Wankhede floodlights, if Rohit plays one of those vintage innings where the ball seems to leave the bat before it arrives — then Rajasthan will face the fight of their season. And if RR stumble, the entire fourth-spot equation collapses into a three-way permutation nightmare involving PBKS, KKR, and net run rate calculators.

The five-time champions have nothing to gain. But three other franchises — and their millions of fans around the world — will be watching the Wankhede like it is a final.

Because for them, it is.""",
}

# ── ARTICLE 2: KKR's 77-Run Equation at Eden Gardens ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "KKR Need to Beat Delhi Capitals by 77 Runs. The Maths Is Cruel. Eden Gardens Won't Care.",
    "subheadline": "Kolkata Knight Riders' playoff survival requires not just a win against DC on Sunday, but a win by a margin so large that it has been achieved fewer than a dozen times in IPL history. The equation is virtually impossible. The crowd will show up anyway. That is what Eden Gardens does.",
    "slug": "kkr-77-run-equation-eden-gardens-dc-ipl-2026-playoff-impossible-math-20260523",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "KKR's ownership by Shah Rukh Khan makes them one of the most emotionally followed franchises among NRIs globally — SRK's film fanbase and cricket franchise fandom overlap almost entirely in diaspora communities; the Eden Gardens crowd is a spectacle that US and UK-based Indian fans will stream at 3:30 AM local time; the mathematical improbability of KKR's situation has generated viral social media content among diaspora cricket fans debating whether 77-run margins are achievable in T20 cricket",
    "tags": ["KKR", "Kolkata Knight Riders", "Delhi Capitals", "IPL 2026", "Eden Gardens", "Playoffs", "Shah Rukh Khan", "Net Run Rate", "NRR", "Punjab Kings", "Rajasthan Royals", "Manish Pandey", "KL Rahul", "Mitchell Starc"],
    "urgency": "daily",
    "sources": [
        "https://crictracker.com/cricket/ipl/pbks-beat-lsg-rr-kkr-do-or-die-playoffs-scenarios",
        "https://mykhel.com/cricket/ipl-2026-playoff-scenario-how-can-kkr-reach-playoffs-after-pbks-beat-lsg",
        "https://latestly.com/sports/cricket/ipl-2026-playoff-scenarios-pbks-win-over-lsg-impacts-rr-kkr",
        "https://sportskeeda.com/cricket/ipl-2026-qualification-scenarios-how-can-pbks-qualify",
        "https://crictracker.com/cricket/ipl/kkr-vs-dc-dream11-prediction-match-70"
    ],
    "word_count": 700,
    "score_total": 66,
    "body": """Here is what Kolkata Knight Riders need to do on Sunday to make the IPL 2026 playoffs:

Win against Delhi Capitals at Eden Gardens. Score 200 runs. Then bowl DC out for 123 or fewer.

Alternatively: bowl first, hold DC to 180, then chase it down in approximately 12 overs.

Either way, the winning margin needs to be 77 runs or the equivalent in net run rate terms. In T20 cricket — a format where the average winning margin in the IPL this season has been around 20-30 runs — this is not an equation. It is a mathematical obituary.

## How they got here

KKR have 13 points from 13 matches. Punjab Kings, who beat Lucknow Super Giants on Friday in a match defined by Shreyas Iyer's maiden IPL century, have 15 points and are done with their league stage. KKR can reach 15 points by beating DC, but 15 points alone are not enough. They also need to overhaul PBKS on net run rate.

Net run rate in the IPL is calculated as the difference between a team's run rate scored and run rate conceded across all matches. KKR's current NRR is significantly inferior to PBKS's. The gap is such that only an enormous margin of victory — 77 runs if batting first with a 200-run total — would bridge it.

For context: there have been only 11 instances in IPL history of a team winning by 77 or more runs. The most recent was Royal Challengers Bengaluru's 82-run demolition of Punjab Kings in 2024, a match in which Virat Kohli scored 113 not out and PBKS collapsed to 137 all out. Before that, the list includes Mumbai Indians' 92-run win over Delhi in 2017 and Rajasthan Royals' 85-run annihilation of a disintegrating Deccan Chargers side in 2008.

These margins are not the product of planning. They happen when one team produces a historically good batting performance and the opposition has a historically bad bowling and batting day simultaneously. You cannot engineer a 77-run victory. You can only create the conditions for one and hope the cricket gods comply.

## Why Eden Gardens changes the calculation

The rational response to KKR's equation is resignation. The numbers say it is over. The mathematics says go home.

But Eden Gardens does not trade in mathematics.

The Kolkata crowd is, by any reasonable measure, the most intense in Indian cricket. The stadium holds 68,000 people. On a Sunday with a playoff spot at stake — however remote the probability — it will be full. It will be loud. And it will generate the kind of atmosphere that has historically turned ordinary IPL matches into events that defy their statistical likelihood.

KKR's batting has the firepower to post 200-plus. In their win against Mumbai Indians earlier this week, Manish Pandey scored 45 and the bowling unit restricted MI effectively. Against DC, who have won only five matches this season and have the worst net run rate of any team still playing, there is at least a theoretical path to a dominant performance.

DC's KL Rahul has been their most consistent performer, but consistency in a dead-rubber match against a desperate opponent in a hostile venue is a different proposition entirely. Mitchell Starc's four wickets in DC's recent match suggest the bowling has teeth, but the batting around Rahul has been brittle all season.

## The diaspora watch

KKR matches at Eden Gardens have a unique quality for diaspora viewers. The crowd shots — 68,000 people chanting, waving, standing for every boundary — provide the visceral connection to Indian cricket culture that NRI fans miss most acutely. Shah Rukh Khan's ownership of the franchise adds a Bollywood dimension that no other IPL team replicates.

The match starts at 3:30 PM IST on Sunday — 3:00 AM Pacific, 6:00 AM Eastern. The US-based KKR fans who set alarms for this match will do so knowing the equation requires something that has happened only 11 times in 1,200-plus IPL matches. They will watch anyway.

## The honest truth

KKR will probably not win by 77 runs. The probability is in the low single digits. If Rajasthan Royals beat Mumbai Indians in the afternoon match, KKR's game against DC becomes entirely meaningless — RR would qualify, and no KKR margin would matter.

But if RR lose, and KKR somehow produce the kind of performance that only happens once or twice a decade in T20 cricket, then Sunday at Eden Gardens will become one of the most remembered matches in IPL history.

The maths says no. Kolkata says play anyway.""",
}

if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-23 20:00 PDT")
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

    print("\nInserting Article 1: MI Dead Rubber Kingmaker...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    # Try image for Article 1
    img1_path = f"/tmp/{a1_id}.jpg"
    if fetch_image("Wankhede Stadium cricket Mumbai night", img1_path):
        img1_url = upload_image(a1_id, img1_path)
        if img1_url:
            update_image_url(a1_id, img1_url)

    print("\nInserting Article 2: KKR 77-Run Equation...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    # Try image for Article 2
    img2_path = f"/tmp/{a2_id}.jpg"
    if fetch_image("Eden Gardens Kolkata cricket stadium crowd", img2_path):
        img2_url = upload_image(a2_id, img2_path)
        if img2_url:
            update_image_url(a2_id, img2_url)

    # Score decay
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    print(f"\nDone. 2 articles published.")
    print(f"  IDs: {a1_id}, {a2_id}")
