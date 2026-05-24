#!/usr/bin/env python3
"""Sports writer — 2026-05-24 14:00 PDT run: 2 articles + score decay."""

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


# ── ARTICLE 1: KKR's Season Ends — From 96/2 to 163 All Out ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Kolkata Knight Riders Were 96 for 2 and Needed 108 From 54 Balls. They Were All Out for 163. Their Season Is Over.",
    "subheadline": "Kuldeep Yadav took 3 for 29. Lungi Ngidi took 3 wickets. Mitchell Starc took 2 wickets. Between the three of them, they dismantled KKR from a position of comfort to a 40-run defeat at Eden Gardens on Sunday night. KL Rahul had earlier scored 60 off 30 balls to power Delhi Capitals to 203 for 5. KKR finished on 12 points, seventh in the table, eliminated alongside Punjab Kings and five other teams. The defending champions of 2024 did not defend.",
    "slug": "kkr-eliminated-ipl-2026-collapsed-163-all-out-kuldeep-yadav-dc-eden-gardens-kl-rahul-60-20260524",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Kolkata Knight Riders occupy a unique emotional space for the Bengali diaspora. KKR is not just a cricket franchise — it is Kolkata's proxy in the IPL, the only way the city competes against Mumbai, Delhi, and Bengaluru in the only domestic tournament the global Indian diaspora follows religiously. For the Bengali NRI in Edison, the Kolkata expat in London, the second-generation kid in Toronto whose parents still send Durga Puja sweets, KKR's season is a thread that connects them to home from March to May. Shah Rukh Khan's ownership adds another layer — SRK is arguably the single most recognised Indian face in the global diaspora, and his team's failures feel personal in a way that other franchise collapses do not. The 2024 title was supposed to be the beginning of a new era. Instead, it was an outlier. KKR's collapse from 96/2 — a position from which any top-four team would have won — mirrors the particular frustration of diaspora fandom: you invest the emotion, set the alarm, clear the morning, and watch it fall apart in real time across time zones. Ajinkya Rahane's post-match comments about heading back to play his local league in Mumbai will resonate with NRI fans who understand the particular loneliness of a season ending not with a final, but with an interview about what comes next.",
    "tags": ["Kolkata Knight Riders", "KKR", "IPL 2026", "Delhi Capitals", "Kuldeep Yadav", "KL Rahul", "Ajinkya Rahane", "Lungi Ngidi", "Mitchell Starc", "Eden Gardens", "IPL Elimination"],
    "urgency": "daily",
    "sources": [
        "https://timesofindia.indiatimes.com/sports/cricket/match-center-scorecard/delhi-capitals-vs-kolkata-knight-riders-live-score-update-match-70-indian-premier-league-2026/krdd05242026270341",
        "https://cricketaddictor.com/kkr-vs-dc-full-scorecard-match-70-ipl-2026/",
        "https://hiindia.com/ipl-2026-kl-rahul-top-scores-30-ball-60-dc-203-5-kkr/",
        "https://bhaskarenglish.in/sports/cricket/ipl-2026-kkr-vs-dc-live-score/"
    ],
    "word_count": 770,
    "score_total": 65,
    "body": """The scorecard will show that Kolkata Knight Riders lost to Delhi Capitals by 40 runs at Eden Gardens on Sunday night. What the scorecard will not show is the specific cruelty of the collapse — the way a chase that was perfectly set up at 96 for 2 after 10 overs disintegrated into 163 all out in 18.4 overs.

The Knight Riders needed 108 runs from 54 balls with eight wickets in hand. Ajinkya Rahane had just completed his fifty. Rinku Singh was at the other end. Eden Gardens was loud. The arithmetic was comfortable. Then Kuldeep Yadav bowled to Rinku.

## The spell that ended a season

Kuldeep finished with 3 for 29 from four overs, and the numbers do not capture the damage. He dismissed Rinku Singh with a ball that gripped and turned past the bat — the kind of delivery that reminds you Kuldeep was once the most feared wrist spinner in T20 cricket, and that his quiet season had been a matter of rhythm, not ability.

After Rinku fell, the dressing room's mood shifted. Cameron Green went cheaply. Manish Pandey — who reached the milestone of 4,000 IPL career runs during this match — fell before he could convert the moment into something match-defining. From 96 for 2, KKR stumbled to 129 for 6 in the space of four overs.

Rovman Powell tried. He scored 29 off 21 balls with the power and intent that had defined his better days this season. But when Mitchell Starc dismissed Anukul Roy with a caught-and-bowled and then had Kartik Tyagi caught at mid-off in the same over, the match was effectively over. A direct-hit run-out of Powell — caught short by a substitute fielder's throw from long-off — made it emphatic.

Lungi Ngidi cleaned up the tail, finishing with three wickets of his own. The final wicket fell in the 19th over. KKR were bowled out with eight balls unbowled.

## KL Rahul's statement innings

The foundation for DC's 203 for 5 was laid by KL Rahul, who played the kind of innings that makes franchise cricket infuriating for the team on the wrong end. He scored 60 off 30 balls — six fours, three sixes — and did it with the languid elegance that has defined his career and the controlled aggression that has sometimes been missing from it.

Rahul attacked from the start. He took on the KKR spinners when they were ineffective early and continued when they found some purchase later. By the time he fell in the 14th over, DC were past 140 and the platform was set.

Axar Patel contributed a brisk cameo lower down, and David Miller's 28 off 19 balls ensured the death overs were productive. DC finished on a total that was above par on an Eden Gardens surface that slowed as the evening progressed.

## Rahane's honest assessment

Ajinkya Rahane's post-match interview was the most honest assessment a losing captain could give. He acknowledged that the season had been disappointing. He praised his players individually. He said they gave it everything. And then, asked about his plans after the tournament, he said he would take a couple of days off and go back to playing his local league cricket in Mumbai.

There was no talk of mega-auction strategy. No promises about next year. Just a man who captained a team that finished seventh saying he was happy as long as he was playing cricket.

## The 2024 hangover

When KKR won the IPL title in 2024, it was supposed to mark the franchise's return to the top tier. They had rebuilt smartly around Rinku Singh, brought in Green for firepower, and found consistency under Rahane's steady captaincy during the latter stages of that tournament.

The 2026 season told a different story. KKR won six and lost eight of their 14 league matches. They never built momentum — every winning streak of two was followed by a losing run of three. Sunil Narine, the most transformative overseas player in the franchise's history, had his quietest IPL season in a decade. Finn Allen's explosive starts were too infrequent. The bowling attack lacked a death specialist.

The result was a team that could beat anyone on its day and lose to anyone the day after. In a 14-game league, inconsistency is indistinguishable from mediocrity.

## Six teams go home

KKR's elimination, combined with Rajasthan Royals' 30-run victory over Mumbai Indians in the afternoon, confirmed the final four for the IPL 2026 playoffs: RCB (18 points), Gujarat Titans (18), Sunrisers Hyderabad (18), and Rajasthan Royals (16).

Six teams were eliminated: Punjab Kings (15 points), KKR (12), Chennai Super Kings, Delhi Capitals, Lucknow Super Giants, and Mumbai Indians. Among them are five former champions. The IPL does not care about history.

For KKR fans at Eden Gardens on Sunday night, the season ended not with a knockout punch but with a slow deflation — a chase that was alive at 96/2, dying at 129/6, and dead at 163 all out. The stands emptied before the final wicket fell. The quieting of Eden Gardens is one of cricket's saddest sounds. On Sunday, it happened earlier than anyone expected.""",
}


# ── ARTICLE 2: IPL 2026 Playoffs Preview — The Final Four ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "Four Teams. Three Cities. Seven Days. The IPL 2026 Playoffs Start Tuesday in the Mountains of Dharamsala.",
    "subheadline": "RCB face Gujarat Titans in Qualifier 1. Sunrisers Hyderabad face Rajasthan Royals in the Eliminator. The winner of the Final on May 31 in Ahmedabad gets the trophy. The road to get there passes through Dharamsala, New Chandigarh, and the most condensed stretch of high-stakes cricket the calendar year offers.",
    "slug": "ipl-2026-playoffs-preview-rcb-gt-qualifier-dharamsala-srh-rr-eliminator-chandigarh-final-ahmedabad-20260524",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "The IPL playoffs are the single week of the year when the Indian diaspora's cricket obsession reaches its highest intensity. For NRI fans across North America, the UK, and the Gulf, the next seven days will involve alarm clocks set to improbable hours, work meetings joined with one AirPod streaming commentary, and group chats that spike to hundreds of messages per match. Dharamsala as the venue for Qualifier 1 adds a particular dimension — the HPCA Stadium is the most visually stunning cricket ground in the world, set against the Dhauladhar range, and it is the ground that NRI fans most frequently save as their phone wallpaper without ever having visited. For the RCB diaspora — which is enormous, fuelled by two decades of Virat Kohli fandom and a global fan base that spans Bengaluru, Sydney, London, and the Bay Area — this is the year the narrative is supposed to change. They have 18 points, the joint-highest in the league, and a team that looks complete for the first time in memory. GT's diaspora following is newer but fervent, built around the Ahmedabad business community and the team's Cinderella 2022 title. SRH and RR bring their own continental followings. The final in Ahmedabad at the Narendra Modi Stadium — the world's largest cricket ground — will be watched by more people globally than any single domestic sporting event this year. Many of those viewers will be in living rooms in Edison, Fremont, Brampton, Southall, and Dubai, watching at hours that make no logical sense, because the IPL in May is not a logical thing. It is an emotional one.",
    "tags": ["IPL 2026 Playoffs", "RCB", "Gujarat Titans", "Sunrisers Hyderabad", "Rajasthan Royals", "Dharamsala", "New Chandigarh", "Ahmedabad", "Qualifier 1", "Eliminator", "IPL Final", "Virat Kohli"],
    "urgency": "daily",
    "sources": [
        "https://sportingnews.com/ipl-2026-playoffs-qualified-teams-eliminated",
        "https://sportsdigest.in/ipl-2026-playoffs-schedule-dates-venues/",
        "https://media-lab.top/ipl-2026-playoffs-schedule-rr-final-push/",
        "https://techwordnews.com/ipl-2026-playoffs-schedule-rcb-gt-qualifier/"
    ],
    "word_count": 810,
    "score_total": 72,
    "body": """The league stage is over. Seventy matches across 58 days. Ten teams. Two hundred and eleven hours of broadcast cricket. All of it distilled into four teams and four matches spread across seven days that will produce one champion.

Here is what the next week looks like.

## The schedule

**Qualifier 1 — Tuesday, May 26**
Royal Challengers Bengaluru vs Gujarat Titans
HPCA Stadium, Dharamsala | 7:30 PM IST (10:00 AM ET, 7:00 AM PT)

**Eliminator — Wednesday, May 27**
Sunrisers Hyderabad vs Rajasthan Royals
PCA Stadium, New Chandigarh | 7:30 PM IST (10:00 AM ET, 7:00 AM PT)

**Qualifier 2 — Friday, May 29**
Loser of Qualifier 1 vs Winner of Eliminator
Venue TBC | 7:30 PM IST

**Final — Sunday, May 31**
Narendra Modi Stadium, Ahmedabad | 7:30 PM IST (10:00 AM ET, 7:00 AM PT)

The format: Qualifier 1's winner goes straight to the final. Qualifier 1's loser gets a second chance in Qualifier 2. The Eliminator is sudden death — lose and you are out.

## Qualifier 1: RCB vs GT

This is the match the IPL wanted. Royal Challengers Bengaluru — the most followed franchise in cricket, powered by Virat Kohli, and carrying 16 years of title drought — against Gujarat Titans, the newest franchise with the most efficient recent record.

RCB finished on 18 points, level with GT and SRH, and earned the top spot through a superior net run rate. Their season has been defined by consistency rather than dominance: nine wins, five losses, zero no-results. Kohli has had a productive campaign without a defining knockout innings in the knockouts yet. The bowling, led by the overseas quicks and a vastly improved spin department, has been the difference.

GT have been the tournament's most clinical team in run chases. Their middle order — built around a restructured batting lineup after the 2026 auction — has bailed them out repeatedly. Rashid Khan's economy rate of 6.8 runs per over remains the best among frontline spinners. The question for GT is whether their batting holds against RCB's new-ball attack in Dharamsala's thin air, where the ball swings more and carries further.

Dharamsala is a neutral venue for both teams, but the HPCA Stadium's dimensions and altitude favour teams that bowl first. Whoever wins the toss will likely bowl — and whoever bats first will need to score more than they expect.

## Eliminator: SRH vs RR

The Eliminator is the pressure match. One team survives. The other drives home.

Sunrisers Hyderabad finished on 18 points with the same won-loss record as RCB and GT. Their Net Run Rate of +0.437 is the second best among qualifiers, powered by a batting lineup that has crossed 200 six times this season. Travis Head and Heinrich Klaasen have been devastating in the powerplay and middle overs respectively. If both fire on the same day, no total is safe.

Rajasthan Royals, by contrast, squeezed into the playoffs on the last day of the league stage. They finished on 16 points — two fewer than the other three qualifiers — and needed their own victory over Mumbai Indians combined with KKR's loss to DC to secure the fourth spot. They are the team with the most to prove and the least margin for error.

RR's strength is their bowling. Jofra Archer's return to full fitness in the second half of the season has transformed their attack. His 3 for 17 against MI on Sunday was the spell that got RR here. Yuzvendra Chahal and Ravindra Jadeja provide spin options on a New Chandigarh surface that will turn.

The risk for RR is batting depth. Their top three — Yashasvi Jaiswal, Riyan Parag, and Dhruv Jurel — are all capable of match-winning innings, but none has the experience of playoff cricket that SRH's top order brings. In sudden death, experience is not a cliché. It is the difference between backing yourself at 40 for 2 and panicking at 40 for 2.

## The stakes

For RCB, this is the year. Seventeen seasons without a title. The most passionate fan base in cricket. Kohli in what could be his last or second-to-last IPL season. If RCB win on May 31, it will be the single most celebrated moment in Indian franchise sports history. If they lose, it will be another year of waiting for a fan base that has done nothing but wait.

For GT, a second title in four seasons of existence would cement them as the IPL's model franchise — proof that smart analytics and recruitment can outperform legacy and star power.

For SRH, the equation is simpler: they have the firepower and they know it. Head, Klaasen, and a deep pace battery give them the highest ceiling of any team in the playoffs.

For RR, it is a bonus. They were nearly out on Saturday night. They are here because Jofra Archer bowled four overs of controlled hostility at the Wankhede. Anything they achieve from here is profit — and teams playing with house money are the most dangerous teams in knockout cricket.

## The numbers to know

| Team | League Pts | Wins | NRR | Playoff Path |
|------|-----------|------|------|-------------|
| RCB | 18 | 9 | +0.512 | Qualifier 1 → Final or Q2 |
| GT | 18 | 9 | +0.489 | Qualifier 1 → Final or Q2 |
| SRH | 18 | 9 | +0.437 | Eliminator → Q2 or out |
| RR | 16 | 8 | +0.215 | Eliminator → Q2 or out |

The IPL 2026 playoffs begin in Dharamsala on Tuesday. The trophy is lifted in Ahmedabad on Sunday. Everything between is elimination cricket — the format where records are forgotten, favourites fall, and the team that handles pressure best wins.

Seven days. Four matches. One trophy. Set your alarms.""",
}


if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-24 14:00 PDT")
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

    print("\nInserting Article 1: KKR Eliminated — Collapsed from 96/2...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    img1_path = f"/tmp/{a1_id}.jpg"
    if fetch_image("cricket stadium empty seats night Eden Gardens Kolkata", img1_path):
        img1_url = upload_image(a1_id, img1_path)
        if img1_url:
            update_image_url(a1_id, img1_url)

    print("\nInserting Article 2: IPL 2026 Playoffs Preview...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    img2_path = f"/tmp/{a2_id}.jpg"
    if fetch_image("cricket stadium mountains Dharamsala HPCA himalaya", img2_path):
        img2_url = upload_image(a2_id, img2_path)
        if img2_url:
            update_image_url(a2_id, img2_url)

    # Score decay
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    print(f"\nDone. 2 articles published.")
    print(f"  IDs: {a1_id}, {a2_id}")
