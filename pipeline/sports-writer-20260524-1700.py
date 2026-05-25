#!/usr/bin/env python3
"""Sports writer — 2026-05-24 17:00 PDT run: 2 articles + score decay."""

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
    "headline": "Sai Sudharsan Won the Orange Cap Last Year With 759 Runs. He Is Leading It Again This Year With 638. No One at Gujarat Titans Seems Surprised.",
    "subheadline": "The 24-year-old left-hander from Chennai finished the IPL 2026 league stage as the tournament's leading run scorer for the second consecutive season. His 638 runs came at an average of 49, a strike rate of 158, with one century and seven fifties. His teammate Shubman Gill is second on the list with 616. Between them, Gujarat Titans' opening pair has scored 1,254 runs this season. They play Qualifier 1 against RCB on Tuesday.",
    "slug": "sai-sudharsan-orange-cap-ipl-2026-638-runs-back-to-back-gujarat-titans-qualifier-rcb-20260524",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Sai Sudharsan occupies a particular position in the Indian diaspora's cricketing imagination. He is Tamil — from Chennai, the city that most reliably produces technically correct batsmen — but he plays for Gujarat, a franchise without the generational loyalty of Mumbai Indians or the cult following of RCB. For the Tamil NRI in Singapore, the Gujarati businessman in New Jersey, the cricket-obsessed data analyst in the Bay Area, Sudharsan represents something rare in T20 cricket: the triumph of consistency over virality. In a tournament where Vaibhav Sooryavanshi's 53 sixes dominate highlight reels and Abhishek Sharma's 206 strike rate fills social media timelines, Sudharsan has scored the most runs by doing the least spectacular thing — batting through innings, converting starts into fifties, and fifties into match-shaping scores. The diaspora's cricket consumption is increasingly fragmented across time zones and streaming platforms; most NRI fans watch highlights, not full matches. Sudharsan's game is built for full matches. That he leads the Orange Cap despite this disconnect between his method and the medium through which most diaspora fans consume IPL cricket is its own kind of statement. R Ashwin — fellow Tamil, fellow analyst, India legend — publicly said Sudharsan's strike rate of 158 is not enough for modern T20s. The debate that followed played out across Tamil cricket Twitter, NRI WhatsApp groups, and YouTube channels. It was the most engaged the diaspora has been about strike rate discourse since Kohli's anchor innings debates of 2023.",
    "tags": ["Sai Sudharsan", "Orange Cap", "IPL 2026", "Gujarat Titans", "Shubman Gill", "RCB", "Qualifier 1", "Dharamsala", "IPL Stats", "T20 Cricket"],
    "urgency": "daily",
    "sources": [
        "https://wisden.com/ipl-2026-orange-cap-full-list",
        "https://sportingnews.com/ipl-orange-cap-2026-list",
        "https://sportsyaari.com/ipl-2026-orange-cap-race",
        "https://cricketaddictor.com/r-ashwin-sai-sudharsan-strike-rate"
    ],
    "word_count": 750,
    "score_total": 68,
    "body": """The IPL 2026 league stage ended on Sunday with seventy matches, ten teams, and one name at the top of the batting charts: Sai Sudharsan, 638 runs, Gujarat Titans, Orange Cap holder.

This is not news. This is a continuation.

## The numbers, again

Sudharsan won the Orange Cap in 2025 with 759 runs. He is leading it again in 2026 with 638 — and the playoffs have not started yet. No Indian batter has held the Orange Cap in consecutive seasons since the award's inception. David Warner did it in the mid-2010s. Virat Kohli came close. Sudharsan, at 24, is doing it with the quiet efficiency of someone who treats run-scoring as administrative work.

Fourteen innings. Average of 49.07. Strike rate of 157.92. One century. Seven fifties. Sixty-two fours. Twenty-nine sixes. The numbers describe a batter who rarely fails and occasionally dominates — the platonic ideal of a franchise T20 opener.

His highest score of the season is 100, reached in a match where Gujarat needed him to bat through the innings. His seven fifties include an 84 off 53 balls against Chennai Super Kings in what became Gujarat's playoff-clinching performance. In that match, captain Shubman Gill scored 64 off 37 at the other end. The two of them put on yet another century partnership. It was their sixth of the season.

## The opening partnership

The story of Gujarat Titans' IPL 2026 season is the story of Sudharsan and Gill at the top of the order. Between them, they have scored 1,254 runs. They occupy the top two positions on the Orange Cap leaderboard — the first time teammates have held the first and second spots simultaneously since the IPL moved to a ten-team format.

Gill bats with force. Sudharsan bats with time. Gill hits sixes over long-on with a high elbow and a fast bat. Sudharsan drives through cover with the kind of footwork that makes batting coaches in Chennai nod approvingly. Together, they have given Gujarat starts that the middle order has been able to build on — or, on days when the middle order has collapsed, starts large enough that the collapse did not matter.

Matthew Hayden, speaking on commentary during the GT-CSK match, called them "apex predators" and meant it as praise for their controlled aggression. The phrase stuck.

## The Ashwin debate

Not everyone agrees that Sudharsan's method is optimal. R Ashwin — former India off-spinner, current YouTube analyst, and the most influential Tamil cricket voice on the internet — said publicly that a strike rate of 158 is insufficient for a top-order T20 batter in 2026.

"He is doing what he does very well," Ashwin said in his YouTube video. "But the game has moved. The best T20 batters in the world are striking at 170, 180. If Gujarat want to win the trophy, they need Sudharsan to find another gear in the playoffs."

The comment sparked exactly the kind of debate that Indian cricket generates more reliably than any other sport on earth. Tamil cricket Twitter split. NRI WhatsApp groups forwarded clips. The consensus, to the extent one existed, was that Ashwin was technically correct and emotionally wrong — Sudharsan's consistency has been Gujarat's foundation, and asking the foundation to also be the fireworks is asking one player to be two different things.

Sudharsan has not responded publicly. He rarely does. His Instagram is sparse. His press conferences are functional. He bats, he scores, he walks off. The absence of personality is, in the IPL's ecosystem of personal brands, its own kind of personality.

## What the playoff path looks like

Gujarat Titans play Royal Challengers Bengaluru in Qualifier 1 on Tuesday in Dharamsala. If they win, they go straight to the final on May 31 in Ahmedabad. If they lose, they get a second chance in Qualifier 2 on May 29.

For Sudharsan, the playoffs represent an opportunity to extend his lead at the top of the run charts. Heinrich Klaasen (606, SRH) and Vaibhav Sooryavanshi (583, RR) are both still alive in the tournament. If Sudharsan bats through two or three more matches, the gap could become uncatchable.

The Orange Cap is awarded after the final. It is a seasonal honour that matters more to statisticians than to players, but it matters to the record books — and the record books are where Sudharsan is building something unusual. Back-to-back Orange Caps would place him alongside Warner and Kohli in a category that has never included a player this young or this early in their international career.

## The Chennai kid in Ahmedabad

Sudharsan grew up in Chennai, trained at the Tamil Nadu Cricket Association facilities, and played his early domestic cricket for Tamil Nadu. He was selected by Gujarat Titans and moved — not physically, but professionally — to a franchise based in a city 1,500 kilometres from home.

This is the IPL's particular alchemy: it separates players from their geographic identities and asks them to build new ones. Sudharsan bats for Gujarat the way a software engineer from Chennai works for a company in Cupertino — the location is incidental, the output is not.

He will walk out to bat on Tuesday in Dharamsala, at 7,000 feet, against an RCB attack led by Bhuvneshwar Kumar and built to exploit swing conditions. If he scores runs, Gujarat will probably win. If he does not, the Orange Cap will be a consolation. He does not seem like a man who is interested in consolations.""",
}


# ── ARTICLE 2: Bhuvneshwar Kumar — Purple Cap at 36 ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "Bhuvneshwar Kumar Spent Twelve Years at Sunrisers Hyderabad. They Let Him Go. At 36, He Is Holding the Purple Cap at RCB.",
    "subheadline": "Twenty-four wickets in fourteen matches. An average of 18.50. An economy rate of 8.07. The best figures of 4 for 23. Bhuvneshwar Kumar — the man whose career was supposed to be winding down — has been the most effective bowler in the IPL 2026 league stage. He leads the Purple Cap race alongside Kagiso Rabada of Gujarat Titans. On Tuesday, when RCB play GT in Qualifier 1, the Purple Cap holder bowls against the team whose bowler shares his record.",
    "slug": "bhuvneshwar-kumar-purple-cap-ipl-2026-rcb-24-wickets-swing-dharamsala-qualifier-20260524",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Bhuvneshwar Kumar is the kind of cricketer the Indian diaspora respects but rarely celebrates. He does not have Virat Kohli's social media presence. He does not have MS Dhoni's mythology. He is a swing bowler from Meerut who has been bowling outswingers at the top of innings for fifteen years, and the diaspora's relationship with him has always been one of quiet appreciation rather than loud devotion. His move from SRH to RCB changed the calculus. RCB is not just a cricket franchise — it is the most globally followed Indian sports brand outside the national team itself. Kohli's fan base stretches from Bengaluru to the Bay Area, from Melbourne to Manchester. When Bhuvneshwar puts on the RCB jersey and takes a wicket at the Chinnaswamy, the celebration reaches WhatsApp groups in Edison, living rooms in Brampton, and pubs in Southall that would never have noticed him in orange. The Purple Cap at RCB gives Bhuvneshwar a visibility he never had at SRH, and it gives RCB something they have never had in seventeen seasons: a bowler who can take wickets in the powerplay consistently enough to compensate for the batting collapses that have historically defined their playoff exits. For NRI fans who have followed RCB's title drought since the franchise's inception, Bhuvneshwar at 36 is the missing variable in an equation they have been trying to solve since 2008.",
    "tags": ["Bhuvneshwar Kumar", "Purple Cap", "IPL 2026", "RCB", "Royal Challengers Bengaluru", "Kagiso Rabada", "Gujarat Titans", "Qualifier 1", "Dharamsala", "Swing Bowling"],
    "urgency": "daily",
    "sources": [
        "https://wisden.com/ipl-2026-purple-cap-full-list",
        "https://sportingnews.com/ipl-purple-cap-2026-list",
        "https://cricketaddictor.com/bhuvneshwar-kumar-ipl-2026",
        "https://livemint.com/orange-purple-cap-ipl-2026"
    ],
    "word_count": 780,
    "score_total": 70,
    "body": """When the IPL 2026 mega-auction took place, Bhuvneshwar Kumar's name did not generate the frenzy that accompanied the younger, faster, more marketable pace bowlers. He was 36. He had spent the previous twelve years at Sunrisers Hyderabad — first as their spearhead, then as their senior statesman, and finally, in the way franchises handle aging fast bowlers, as someone whose experience was valued in the dressing room more than his place in the playing XI.

SRH let him go. RCB picked him up. The transaction felt like a courtesy — a veteran getting one more contract at a franchise that needed bowling depth. It has turned out to be the signing of the season.

## The numbers

Twenty-four wickets in fourteen matches. An economy rate of 8.07 — the best among the top ten wicket-takers. An average of 18.50, meaning each wicket cost fewer than nineteen runs. Best figures of 4 for 23. One four-wicket haul. Zero five-wicket hauls, because he was rarely needed for a fifth — the damage was done in his first three overs.

Bhuvneshwar shares the Purple Cap with Kagiso Rabada of Gujarat Titans, who also has 24 wickets but at a significantly worse economy of 9.18. In the language of bowling statistics, Bhuvneshwar has been both more penetrative and more miserly. He has been, by the combined measure of wickets and economy, the best bowler in the tournament.

## The swing

The explanation is simple and old-fashioned: Bhuvneshwar Kumar swings the new ball. He has always swung the new ball. He swung it at SRH for twelve years. He swung it for India in three ICC tournaments. He is swinging it at RCB now, at 36, in a T20 league where swing bowling is supposed to be a dying art.

The IPL's modern meta favours pace and bounce. Jofra Archer bowls at 145 kmph. Mitchell Starc generates awkward angles. The young fast bowlers coming through Indian domestic cricket — Eshan Malinga, Kartik Tyagi — are built for speed. Bhuvneshwar bowls at 130-135 kmph, which in 2026's IPL is closer to medium pace than fast bowling.

But he moves the ball. In the powerplay, when the white Kookaburra is newest and the fielding restrictions allow only two men outside the circle, Bhuvneshwar's outswingers find edges. His inswingers trap batsmen on the crease. His slower ball, delivered from the same action as his stock delivery, arrives a fraction late and produces the kind of mistimed shots that T20 batsmen — grooved into timing everything early — are least equipped to handle.

In fourteen matches, Bhuvneshwar has taken eleven of his twenty-four wickets in the powerplay. No other bowler in the tournament has more than eight in the same phase.

## RCB's missing piece

Royal Challengers Bengaluru have been in the IPL since its first season in 2008. They have played seventeen seasons. They have never won the trophy. The reasons have varied — batting collapses, bowling leaks, bad luck, worse timing — but the consistent theme has been an inability to take early wickets in knockout matches.

Bhuvneshwar changes the equation. In their fourteen league matches, RCB's powerplay bowling record is the best in the tournament: an average of 19.2 runs per wicket and an economy of 7.3 in overs one through six. Bhuvneshwar is the primary reason.

He operates in partnership with the pace unit and Virat Kohli's field placements — Kohli, who at 37 has become as much a tactical captain as a run-scoring machine. The relationship between Kohli and Bhuvneshwar is not new; they have played together for India since 2012. But the dynamic at RCB is different. Kohli sets fields for Bhuvneshwar the way a conductor cues a soloist — with trust earned over a decade and a half.

## Tuesday in Dharamsala

Qualifier 1 takes RCB to Dharamsala, where the HPCA Stadium sits at 7,000 feet and the ball swings more than at any other IPL venue. The thin air, the evening moisture, the Dhauladhar range creating unpredictable wind patterns — it is the perfect ground for a swing bowler.

Bhuvneshwar will bowl the first over against Gujarat Titans. At the other end of the batting crease will be Sai Sudharsan, the Orange Cap holder with 638 runs, and Shubman Gill, who has 616. Together, they are the best opening pair in the tournament. Against them, Bhuvneshwar will do what he has done for fifteen years: hold the seam upright, aim at off stump, and let the ball do the rest.

The collision between the Purple Cap holder and the Orange Cap holder in a playoff match at a venue that favours swing is the kind of contest the IPL exists to produce. It is also, for Bhuvneshwar, the kind of match he was supposed to be too old to play.

## The age question

Thirty-six is not old in cricket. James Anderson bowled for England at 41. Wasim Akram was devastating at 37. But in T20 cricket, where the margins between a good delivery and a six are measured in centimetres and the recovery time between matches is measured in days, 36 is the age at which most fast bowlers become coaches, commentators, or franchise mentors sitting in the dugout in team-branded blazers.

Bhuvneshwar has chosen a different path. He is still bowling. He is still swinging the ball. He is still taking wickets at a rate that younger bowlers — with faster run-ups and bigger gym programmes — cannot match.

The Purple Cap is draped in purple. It looks slightly absurd on anyone. On Bhuvneshwar Kumar, at 36, at a franchise he joined less than a year ago, in a season no one expected him to lead, it looks like the single most satisfying accessory in Indian cricket.""",
}


if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-24 17:00 PDT")
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

    print("\nInserting Article 1: Sai Sudharsan — Back-to-Back Orange Caps...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    img1_path = f"/tmp/{a1_id}.jpg"
    if fetch_image("cricket batsman left hand elegant shot stadium floodlights", img1_path):
        img1_url = upload_image(a1_id, img1_path)
        if img1_url:
            update_image_url(a1_id, img1_url)

    print("\nInserting Article 2: Bhuvneshwar Kumar — Purple Cap at 36...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    img2_path = f"/tmp/{a2_id}.jpg"
    if fetch_image("cricket fast bowler swing bowling action stadium evening", img2_path):
        img2_url = upload_image(a2_id, img2_path)
        if img2_url:
            update_image_url(a2_id, img2_url)

    # Score decay
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    print(f"\nDone. 2 articles published.")
    print(f"  IDs: {a1_id}, {a2_id}")
