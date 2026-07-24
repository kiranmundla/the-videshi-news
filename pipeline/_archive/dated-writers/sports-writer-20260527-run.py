#!/usr/bin/env python3
"""Sports writer — 2026-05-27 06:05 UTC: 3 articles + score decay.

Article 1: RCB crush GT by 92 runs in IPL 2026 Qualifier 1 — Patidar 93* off 33 balls,
           highest IPL playoff total (254/5), RCB reach 2nd consecutive final.
Article 2: Thunder beat Spurs 127-114 in Game 5 — SGA 32 points, OKC takes 3-2 lead,
           one win from NBA Finals vs Knicks.
Article 3: Three footballers of Indian origin heading to FIFA World Cup 2026 —
           Sarpreet Singh (NZ), Tahsin Mohammed Jamshid (Qatar), Niall Mason (Qatar).
"""

import os, json, uuid, requests, subprocess, sys, urllib.parse, time
from datetime import datetime, timezone, timedelta

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


# ── Image sourcing: Wikipedia first (MANDATORY for person articles) ──

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")

    alternates = []
    if "(" not in person_name:
        alternates = [
            f"{person_name} (cricketer)",
            f"{person_name} (basketball)",
            f"{person_name} (footballer)",
        ]
    for alt in alternates:
        encoded_alt = urllib.parse.quote(alt.replace(' ', '_'))
        try:
            r2 = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_alt}",
                headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
                timeout=10,
            )
            if r2.status_code == 200:
                data2 = r2.json()
                img2 = data2.get("originalimage", {}).get("source") or data2.get("thumbnail", {}).get("source")
                if img2:
                    print(f"  ✓ Wikipedia image found for '{alt}': {img2[:80]}...")
                    return img2
        except Exception:
            pass
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels — ONLY as fallback when Wikipedia returns nothing."""
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
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": pexels_key},
                params={"query": q, "per_page": 1, "orientation": "landscape"},
                timeout=15,
            )
            if r.status_code == 200 and r.json().get("photos"):
                img_url = r.json()["photos"][0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{q}': {img_url[:60]}...")
                return img_url
        except Exception as e:
            print(f"  WARN: Pexels fetch failed for '{q}': {e}")
    return None


def download_image(url, dest_path):
    """Download an image URL to a local path."""
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code == 200 and len(r.content) > 1000:
            with open(dest_path, "wb") as f:
                f.write(r.content)
            print(f"  Image downloaded: {dest_path} ({len(r.content)} bytes)")
            return True
        else:
            print(f"  WARN: Download failed or too small: {r.status_code}, {len(r.content)} bytes")
    except Exception as e:
        print(f"  WARN: Download error: {e}")
    return False


def upload_image(article_id, local_path):
    """Upload image to Supabase storage."""
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


def update_article_image(article_id, image_url, attribution="Wikimedia Commons"):
    """Patch article with image URL and attribution."""
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers=HEADERS,
        json={"image_url": image_url, "image_attribution": attribution},
    )
    print(f"  Image URL + attribution patch: {r.status_code}")


def insert_article(article):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=HEADERS, json=article)
    if r.status_code >= 400:
        print(f"  ERROR inserting {article.get('slug','?')}: {r.status_code} {r.text[:500]}")
    r.raise_for_status()
    return r.json()


def slug_exists(slug):
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id",
        headers=HEADERS,
    )
    return r.status_code == 200 and len(r.json()) > 0


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


# ═══════════════════════════════════════════════════════════════════
# ARTICLE 1: RCB crush GT by 92 runs in IPL 2026 Qualifier 1
# ═══════════════════════════════════════════════════════════════════

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Rajat Patidar Scored Ninety-Three off Thirty-Three Balls. RCB Posted the Highest Total in IPL Playoff History. Gujarat Titans Were Bowled Out for One Hundred and Sixty-Two. The Defending Champions Are in Their Second Consecutive Final.",
    "subheadline": "Royal Challengers Bengaluru demolished Gujarat Titans by 92 runs in the IPL 2026 Qualifier 1 at Dharamshala on Monday night, storming into their fifth IPL final and second in a row. Captain Rajat Patidar's unbeaten 93 off 33 deliveries — nine sixes, five fours, a strike rate of 281.82 — powered RCB to 254 for 5, the highest team total in IPL playoff history. Virat Kohli contributed 43 off 25 balls before Jason Holder removed him. Krunal Pandya made 43 off 28 with both bat and ball, later taking 2 for 16. In reply, Gujarat's top order collapsed catastrophically — Sai Sudharsan out hit-wicket, Shubman Gill bowled by Bhuvneshwar Kumar for 2, Jos Buttler dismissed after a quick 29 off 11. Jacob Duffy took 3 for 39 as the Titans crumbled to 162 all out in 19.3 overs. Only Rahul Tewatia resisted with 68 off 43 balls. RCB will face the winner of the Eliminator between Sunrisers Hyderabad and Rajasthan Royals in the IPL 2026 final.",
    "slug": "rcb-crush-gt-92-runs-qualifier-1-patidar-93-off-33-ipl-2026-final-dharamshala-20260527",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "For the millions of RCB fans in the Indian diaspora — and they are millions, because Virat Kohli's global following makes RCB the most-watched IPL franchise outside India — this is the match that confirms the team's transformation from perennial heartbreak to genuine dynasty. RCB won their first-ever IPL title in 2025 after 17 years of waiting. Now they are in their second consecutive final, having demolished Gujarat by the widest margin in playoff history. The Qualifier 1 was broadcast live across the US, UK, Canada, and the Middle East, and for NRIs watching from living rooms in New Jersey, Fremont, and Brampton, Patidar's 93 off 33 balls was appointment viewing — a knock that will be replayed on every WhatsApp family group and Instagram story across the diaspora. Kohli's 43 before his dismissal carried its own weight: at 37, he remains India's most bankable sporting figure, and every innings he plays for RCB carries the subtext of a career winding down. The IPL final date is yet to be confirmed but is expected within the next week. With matches broadcast on Willow TV and JioCinema in the US, and on Sky Sports and SuperSport internationally, the diaspora will be watching.",
    "tags": ["IPL 2026", "Royal Challengers Bengaluru", "RCB", "Gujarat Titans", "Rajat Patidar", "Virat Kohli", "Krunal Pandya", "Jacob Duffy", "Shubman Gill", "Bhuvneshwar Kumar", "Qualifier 1", "IPL Playoffs", "Dharamshala", "Rahul Tewatia", "Jos Buttler", "Sai Sudharsan", "IPL Final"],
    "urgency": "breaking",
    "sources": [
        "https://www.iplt20.com/news/4374/tata-ipl-2026-qualifier-1-rcb-vs-gt-match-report",
        "https://www.cricketworld.com/ipl-2026-qualifier-1-royal-challengers-bengaluru-storm-into-final-beating-gujarat-titans-by-92-runs/",
        "https://www.reuters.com/sports/cricket/gujarat-still-have-room-improve-despite-top-two-finish-says-rashid-2026-05-25/",
        "https://www.sportingnews.com/us/cricket/news/rcb-vs-gt-rajat-patidar-inspires-royal-challengers-bengaluru-to-ipl-final-2026/"
    ],
    "word_count": 870,
    "score_total": 72,
    "body": """On a cold night in Dharamshala, with the Himalayas as a backdrop and 23,000 packed into the HPCA Stadium, Royal Challengers Bengaluru did what they have spent most of their 18-year existence being unable to do: they made a knockout match look easy.

The final margin — 92 runs — does not capture how one-sided this was. RCB posted 254 for 5, the highest team total in IPL playoff history. Gujarat Titans were bowled out for 162 in 19.3 overs. By the 10th over of the chase, the contest was effectively over.

The defending champions are in their second consecutive IPL final. For a franchise that went 17 years without a title, back-to-back final appearances would have been unthinkable as recently as 2023.

## Patidar's masterclass

Rajat Patidar has always been a big-match player. His unbeaten 112 in the 2022 Eliminator against Lucknow Super Giants announced him. His captaincy this season has been measured and tactical. But what he did on Monday night in Dharamshala was something else entirely.

Coming in at 104 for 3 in the 12th over, with the momentum briefly shifting after Jason Holder had dismissed both Virat Kohli and Devdutt Padikkal in quick succession, Patidar took the Gujarat attack apart with a violence that was almost serene.

He reached his fifty in 21 balls. He finished on 93 not out off 33 deliveries. Nine sixes. Five fours. A strike rate of 281.82. Every boundary was timed, every six was muscled, and the Titans' bowlers — Kagiso Rabada, Mohammed Siraj, Jason Holder, Rashid Khan — had no answers.

The knock was the highest individual score in an IPL playoff match this season and the joint-second highest in playoff history. It was also the innings of a captain who knew his team needed a statement, not just a win.

"When I went in, the situation demanded aggression," Patidar said after the match. "Krunal and I had a plan — take down the pace in the middle overs, then go after the death."

## Kohli's contribution

Before Patidar's assault, Virat Kohli had set the tone. After Venkatesh Iyer's explosive 19 off 7 balls at the top — dismissed by Rabada in the second over — Kohli and Padikkal launched a counter-attack that took RCB to 76 for 1 at the end of the Powerplay.

Kohli made 43 off 25 balls, hitting five fours and a six with the kind of controlled aggression that has defined his T20 batting for over a decade. His dismissal — caught in the deep off Holder — brought Patidar to the crease. Padikkal followed soon after for 30 off 19.

At 37, Kohli's every IPL innings carries a subtext that the diaspora feels acutely: how many more of these are left? On Monday, he showed that the answer is still enough.

## Krunal's double act

Krunal Pandya's contribution was the kind of all-round performance that wins playoff matches without making highlight reels. With the bat, he scored 43 off 28 deliveries — five fours, two sixes — in a 95-run partnership with Patidar that broke the game open.

With the ball, he was even better. Coming on in the middle overs with Gujarat already reeling, Krunal took 2 for 16, cleaning up the lower order with his left-arm spin. The combination of runs and wickets made him arguably the most influential player on the field after his captain.

## Gujarat's collapse

The Titans needed 255 to win. What they produced instead was a capitulation.

The damage began immediately. Sai Sudharsan, Gujarat's most consistent batsman this season, was dismissed hit-wicket for 14 — backing away from a Jacob Duffy short ball and dislodging a bail with his foot. It was the kind of dismissal that sets a tone, and not a good one.

Shubman Gill, Gujarat's captain and their most important player, was bowled by Bhuvneshwar Kumar for just 2. The veteran seamer found a length that nipped back through the gate, and Gill could only watch the off-stump cartwheel.

Jos Buttler provided the only real resistance from the top order, smashing 29 off 11 balls — four fours, two sixes — in a cameo that suggested a different outcome was possible. But Josh Hazlewood removed him, and the innings collapsed: 65 for 6 at the end of the Powerplay.

Washington Sundar made 8. Nishant Sindhu made 5. Jason Holder was dismissed for a duck. The only meaningful batting came from Rahul Tewatia, who scored a defiant 68 off 43 balls — eight fours, four sixes — but by the time he was in full flow, the required rate was beyond 20 an over.

Duffy finished with 3 for 39. Rasikh Salam took 2 for 24. Bhuvneshwar Kumar's figures did not do justice to his impact — the Gill wicket was the one that broke Gujarat's spine.

## What it means

RCB are in their fifth IPL final and their second in a row. They won the 2025 title — their first ever — and are now the favourites to become only the third franchise after Chennai Super Kings and Mumbai Indians to win consecutive titles.

Gujarat Titans are not eliminated. They will play the winner of Tuesday's Eliminator between Sunrisers Hyderabad and Rajasthan Royals in Qualifier 2, with the winner of that match advancing to the final against RCB.

But the message from Dharamshala was unmistakable: RCB are the team to beat. Their batting lineup — Kohli, Patidar, Padikkal, Krunal, Venkatesh Iyer — can post 250 in a playoff match. Their bowling — Bhuvneshwar, Duffy, Hazlewood, Rasikh, Krunal — can bowl out the opposition inside 20 overs. And their captain can score 93 off 33 balls on the biggest stage.

The IPL final date and venue are yet to be confirmed. Whenever it happens, wherever it is played, RCB will walk in as the team with the highest playoff total in history and a captain who just played one of the greatest innings the tournament has ever seen.""",
}


# ═══════════════════════════════════════════════════════════════════
# ARTICLE 2: Thunder 127, Spurs 114 — SGA leads OKC to 3-2 lead
# ═══════════════════════════════════════════════════════════════════

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "Shai Gilgeous-Alexander Scored Thirty-Two Points. Jared McCain Made His First Playoff Start and Scored Twenty in the Second Half. Alex Caruso Had Twenty-Two off the Bench. The Thunder Beat the Spurs by Thirteen and Are One Win From the Finals.",
    "subheadline": "The Oklahoma City Thunder beat the San Antonio Spurs 127-114 in Game 5 of the Western Conference Finals at Paycom Center on Tuesday night, taking a 3-2 series lead. Shai Gilgeous-Alexander led all scorers with 32 points and 9 assists, though he shot just 7-for-19 from the field — making up for it by going 16-of-17 from the free throw line. Jared McCain, making his first playoff start in place of the injured Jalen Williams, scored 20 points — 18 of them in the second half. Alex Caruso added 22 points, 6 assists and 3 steals off the bench. Chet Holmgren contributed 16 points and 11 rebounds. Victor Wembanyama was held to 20 points on 4-of-15 shooting with 6 rebounds. Stephon Castle led the Spurs with 24 points. The Thunder led by 11 at halftime and scored the first nine points of the third quarter. The series shifts to San Antonio for Game 6 on Thursday. The New York Knicks, who swept the Cavaliers 4-0 on Sunday, are resting and waiting.",
    "slug": "thunder-beat-spurs-127-114-game-5-sga-32-mccain-caruso-3-2-lead-nba-finals-20260527",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "The NBA Finals are set to begin June 3 at Madison Square Garden, and the New York Knicks already know they will be there. For the Indian diaspora in America — particularly the one million-plus Indian Americans in the New York tri-state area — this is the week that determines the shape of June. Basketball is the fastest-growing sport among Indian Americans under 30. The NBA's India investment (preseason games in Mumbai, 200 million social media followers in India, JioCinema and Sports18 broadcasts) means the Finals will reach audiences from Jersey City to Juhu. Game 6 is Thursday at 5:30 PM Pacific, 8:30 PM Eastern, and 6:00 AM IST on Friday — another early morning for fans in India, a prime-time event for the diaspora.",
    "tags": ["Oklahoma City Thunder", "San Antonio Spurs", "Shai Gilgeous-Alexander", "Jared McCain", "Victor Wembanyama", "Chet Holmgren", "Alex Caruso", "Jalen Williams", "Stephon Castle", "NBA Playoffs 2026", "Western Conference Finals", "New York Knicks", "NBA Finals", "Paycom Center", "Mark Daigneault", "Mitch Johnson"],
    "urgency": "daily",
    "sources": [
        "https://www.reuters.com/sports/shai-gilgeous-alexander-pushes-thunder-past-spurs-3-2-edge--flm-2026-05-27/",
        "https://www.oklahoman.com/story/sports/nba/thunder/2026/05/26/thunder-spurs-score-live-updates-nba-playoffs-game-5-western-conference-finals-injury-report-wcf/",
        "https://www.sportingnews.com/us/nba/news/nba-playoffs-bracket-2026-schedule-scores/"
    ],
    "word_count": 800,
    "score_total": 60,
    "body": """Two days ago, the Oklahoma City Thunder scored 82 points in the worst offensive game of their season. They shot 33 percent from the field. Victor Wembanyama blocked everything near the rim. The Spurs won by 21 and tied the series at 2-2.

On Tuesday night at Paycom Center, the Thunder scored 40 points in the second quarter alone.

The final score was 127-114. OKC leads the Western Conference Finals 3-2. One more win — on Thursday in San Antonio or, if necessary, on Saturday back in Oklahoma City — and they return to the NBA Finals for the second consecutive year. The New York Knicks, who completed a sweep of the Cavaliers on Sunday, are resting and waiting at Madison Square Garden.

## SGA's rough start, dominant finish

Shai Gilgeous-Alexander, the back-to-back MVP, missed his first four shots and committed three turnovers in the opening quarter. It was the kind of start that would have buried most players.

"If it was four or five me's out there, we would've been down 20 after the first quarter," Gilgeous-Alexander said afterward. "Probably should never start like that again."

But even with those early struggles, the Thunder led after the first period — in part because Gilgeous-Alexander scored seven points in the final two minutes of the quarter. He then caught fire in the second and third, scoring 12 points in OKC's 40-point second quarter and 11 more in the third.

He finished with 32 points on 7-of-19 shooting from the field, but made up for the mediocre percentage by going 16-of-17 from the free throw line. He added 9 assists.

"That's one of the things that I always marvel at with him — his ability to course-correct inside of a game," coach Mark Daigneault said. "He obviously didn't have his fastball early."

## McCain's breakout, Caruso's resurgence

The most surprising contribution came from Jared McCain, who was inserted into the starting lineup for the first time in his playoff career. With both Jalen Williams (hamstring) and Ajay Mitchell (calf) out for the second consecutive game, Daigneault chose McCain over Cason Wallace.

"We just thought he could give us some good stuff with that unit," Daigneault said. "He's got great moxie and confidence, and he showed that."

McCain's first half was quiet — just two points on 1-of-5 shooting. But the 22-year-old erupted after the break, scoring 18 of his 20 points in the second half without committing a single turnover.

Alex Caruso, who had been held scoreless on just one shot attempt in Game 4, got going early and finished with 22 points, 6 assists and 3 steals off the bench.

"He's one of, if not the best, competitor in the NBA night in and night out," Gilgeous-Alexander said of Caruso. "He's huge for us."

In Game 4, the trio of Holmgren, Caruso and McCain had combined for just 14 points on 4-of-19 shooting. In Game 5, they combined for 58 points on 18-of-38.

## Holmgren delivers

Chet Holmgren, who had been criticised for his passivity in Games 3 and 4, was aggressive from the start. He finished with 16 points and 11 rebounds, providing the interior presence that the Thunder's offence needed.

The Thunder shot 48.2 percent from the floor as a team after managing just 33 percent in the Game 4 loss.

## Wembanyama contained again

Victor Wembanyama, the 7-foot-4 French centre who was the most dominant individual performer of the 2026 playoffs entering Tuesday, was limited to 20 points on 4-of-15 shooting with just 6 rebounds. After averaging 20.5 rebounds per game in the first two games of the series, Wembanyama has collected just 18 total over the last three.

Spurs coach Mitch Johnson acknowledged the problem directly: "He's going to have to take more than 15 shots even with the free throws. He's going to have to score more than 20 points for sure."

Stephon Castle led the Spurs with 24 points but expressed frustration with the officiating. The Thunder attempted 38 free throws, six more than San Antonio.

"I just think with the way they guard, how physical they are, we don't get that same luxury to be able to play as physical on the other end at times," Castle said.

## What happens next

The Thunder carried an 11-point lead into halftime and scored the first nine points of the third quarter to push the advantage to 20. San Antonio cut the deficit to eight twice late in the third but could never pull closer.

Game 6 is Thursday night at the Frost Bank Center in San Antonio (8:30 PM Eastern, 5:30 PM Pacific, 6:00 AM IST Friday). If the Spurs win, the series returns to Paycom Center for a decisive Game 7 on Saturday. If the Thunder close it out, the NBA Finals begin June 3 at Madison Square Garden.

The Knicks, who swept Cleveland in four games, will have been resting for more than a week by the time the Finals start. They will have home-court advantage.

For the Thunder, the equation is simple: one more win. They have Gilgeous-Alexander. They have a supporting cast that proved on Tuesday it can absorb the loss of Williams and Mitchell and still score 127 points. They have home court if it goes to seven.

For the Spurs, the equation is equally straightforward: they must win two consecutive games, starting in their own building. Wembanyama must be more aggressive. Castle must sustain the 24-point standard. And the entire team must find an answer for the Thunder's 40-point quarters.

Game 6 tips off Thursday. The Finals are eight days away.""",
}


# ═══════════════════════════════════════════════════════════════════
# ARTICLE 3: Three Indian-origin footballers heading to FIFA WC 2026
# ═══════════════════════════════════════════════════════════════════

a3_id = str(uuid.uuid4())
a3 = {
    "id": a3_id,
    "headline": "India Did Not Qualify for the World Cup. Three Footballers of Indian Origin Will Play in It Anyway. One Was Born in Auckland and Once Played for Bayern Munich. One Is a Nineteen-Year-Old Forward Whose Parents Are from Kannur, Kerala. One Trained at Real Madrid's Academy.",
    "subheadline": "The FIFA World Cup 2026 begins June 11 in North America. India is not among the 48 teams. But at least three footballers of Indian heritage will be there. Sarpreet Singh, a 27-year-old attacking midfielder born in Auckland to Punjabi parents, has been confirmed in New Zealand's squad — the same player who became the first person of Indian origin to play for FC Bayern Munich in the Bundesliga. Tahsin Mohammed Jamshid, a 19-year-old forward whose parents come from Kannur district in Kerala, is in Qatar's squad. Niall Mason, a defender with an Indian mother who trained at Real Madrid, Aston Villa, and Southampton's academies, is also in Qatar's squad. New Zealand are in Group G alongside Belgium, Egypt, and Iran. Qatar are in Group B alongside Canada, Bosnia and Herzegovina, and Switzerland. For the four million Indian Americans who will be watching the World Cup in their own country, these three players offer something India's football establishment has not: representation at the sport's biggest stage.",
    "slug": "three-indian-origin-footballers-world-cup-2026-sarpreet-singh-tahsin-jamshid-niall-mason-20260527",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "The 2026 FIFA World Cup will be played in 16 cities across the United States, Canada, and Mexico — the three countries where the largest populations of the Indian diaspora outside India live. Matches will be held in New York, Los Angeles, Houston, the Bay Area, Seattle, Dallas, Philadelphia, Miami, and Boston — every one of which has a significant Indian American community. For the first time in history, millions of NRIs will be able to attend a World Cup match without leaving their home country. New Zealand play Iran on June 15 at SoFi Stadium in Inglewood, California — a short drive from the largest South Asian community on the West Coast. Qatar face Switzerland on June 13 at Levi's Stadium in Santa Clara, in the heart of the Bay Area, and Canada on June 18 at BC Place in Vancouver. For the Malayali diaspora in particular — concentrated in the Gulf states, the UK, Canada, and the US — Tahsin Jamshid's potential World Cup appearance would be seismic. If he plays, he becomes the first Malayali footballer at a World Cup, a fact that will reverberate through every WhatsApp group in the Mallu diaspora. India is absent from the pitch. Indian roots are on it.",
    "tags": ["FIFA World Cup 2026", "Sarpreet Singh", "Tahsin Mohammed Jamshid", "Niall Mason", "New Zealand Football", "Qatar Football", "Indian Diaspora", "Indian Football", "Kerala", "Kannur", "Bayern Munich", "Al Duhail SC", "AIFF", "Wellington Phoenix", "FIFA", "World Cup North America", "Group G", "Group B"],
    "urgency": "daily",
    "sources": [
        "https://khelnow.com/football/fifa-world-cup-2026-indian-origin-players-squads",
        "https://en.wikipedia.org/wiki/Sarpreet_Singh",
        "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup",
        "https://globalindian.com/sarpreet-singh-makes-fifa-2026-history-with-new-zealand/",
        "https://latestly.com/sports/football/tahsin-mohammed-jamshid-becomes-first-indian-origin-footballer-to-be-picked-in-qatar-national-team/"
    ],
    "word_count": 880,
    "score_total": 62,
    "body": """The 2026 FIFA World Cup begins June 11 in Mexico City. The final will be played July 19 at MetLife Stadium in East Rutherford, New Jersey — across the Hudson River from Manhattan, in a stadium that seats 82,500, in a metropolitan area that is home to more than one million Indian Americans.

India will not be at the tournament. India has qualified for one World Cup in its history — 1950, when it withdrew before playing a match. The gap between Indian football and the rest of the world remains vast. The AIFF's governance crises, the lack of grassroots infrastructure, and the inconsistency of the Indian Super League as a development pathway are problems that have been discussed for decades and solved for none.

But at least three footballers of Indian origin will be at the World Cup. Their stories are different from each other, and different from anything Indian football has produced on its own.

## Sarpreet Singh — the one who could have played for India

Sarpreet Singh is 27 years old. He was born in Auckland to Punjabi parents who had immigrated to New Zealand. He grew up playing football in New Zealand's youth system, and in 2019 he did something no person of Indian origin had done before: he signed for FC Bayern Munich and played in the Bundesliga, Germany's top division.

That achievement alone should have made him one of the most celebrated figures in Indian sport. It did not — because Sarpreet chose New Zealand, the country of his birth, over India.

He was technically eligible to represent India during the early stages of his career, before committing to the All Whites. Whether the AIFF made a serious approach, whether the scouting infrastructure existed to identify him — these are questions the Indian football establishment has never answered satisfactorily.

Since Bayern, Sarpreet's club career has taken him to FK TSC Backa Topola in Serbia and back to the A-League with Wellington Phoenix FC, where he dealt with a knee injury this season. But he recovered in time to earn his place in New Zealand's World Cup squad.

New Zealand are in Group G alongside Belgium, Egypt, and Iran. They face Iran on June 15 at SoFi Stadium in Inglewood, California, and Egypt on June 22 at BC Place in Vancouver. For Indian Americans on the West Coast, the Iran match in LA offers a chance to watch a player with Indian roots on the World Cup stage — a 30-minute drive from the South Asian communities of Artesia and Cerritos.

## Tahsin Mohammed Jamshid — the one from Kannur

If Sarpreet Singh's story is about a path not taken, Tahsin Mohammed Jamshid's story is about a path that did not exist until he made it.

Tahsin is 19 years old — he turns 20 during the tournament. He plays as a forward for Al Duhail SC in the Qatar Stars League. Both his parents are from Kannur district in Kerala — his roots are in Thalassery and Valapattanam, two towns that any Malayali will recognise instantly. He is the first footballer of Indian origin to play in the Qatar Stars League. He progressed through Qatar's youth national teams, trained at the Aspire Football Academy, and made his senior debut during the World Cup qualifiers.

If he makes Qatar's final squad and takes the field, he will become the first Malayali footballer ever to participate in a FIFA World Cup.

That sentence carries weight that statistics cannot capture. Kerala is the most football-obsessed state in India. The ISL's Kerala Blasters have one of the largest fanbases in Indian football. Every village in Malabar has a football ground and a tournament. The idea that a boy whose parents left Kannur could play on the World Cup stage — not for India, but for Qatar — is the kind of story that will travel through every WhatsApp family group, every NRI gathering, every Malayali association in the Gulf, the UK, and North America.

Qatar are in Group B alongside Canada, Bosnia and Herzegovina, and Switzerland. They open against Switzerland on June 13 at Levi's Stadium in Santa Clara, California — in the heart of Silicon Valley, where the Indian American tech workforce is concentrated. Qatar then face Canada on June 18 at BC Place in Vancouver.

## Niall Mason — the one from the academies

The third player is Niall Mason, a defender with an Indian mother who developed within some of the most prestigious academy systems in European football — Real Madrid, Aston Villa, and Southampton. That pedigree gave him a defensive foundation built on elite coaching and competitive pressure.

Mason entered Qatar's football ecosystem and received his senior national team call-up earlier this year. His inclusion in Qatar's squad signals the coaching staff's faith in his versatility and readiness for the World Cup stage.

Mason's story speaks less to Indian football's failures and more to the globalisation of talent. Players with Indian heritage are developing in academy systems across Europe, the Middle East, and Oceania. The pipeline exists. What India lacks is the ability to identify, attract, and integrate that talent — or to produce it domestically at the same level.

## What this means for the diaspora

The 2026 World Cup is the first to be hosted by three nations — the United States, Canada, and Mexico — and the first with 48 teams and 104 matches. It is also the first World Cup where millions of Indian Americans can attend matches in person, in their own cities, without international travel.

Matches will be played at MetLife Stadium in New Jersey, SoFi Stadium in Los Angeles, Levi's Stadium in the Bay Area, NRG Stadium in Houston, AT&T Stadium in Dallas, Lincoln Financial Field in Philadelphia, Hard Rock Stadium in Miami, Lumen Field in Seattle, Gillette Stadium in Boston, and more. Every single one of those cities has a significant Indian American community.

India's absence from the pitch is a failure of administration, not of interest. India has 1.4 billion people and one of the world's most passionate sporting cultures. But its football federation has produced zero World Cup appearances in 76 years.

Sarpreet Singh, Tahsin Mohammed Jamshid, and Niall Mason did not wait for the AIFF. They found football in Auckland, Doha, and European academies. They will represent New Zealand and Qatar, not India. But for the Indian diaspora watching from SoFi Stadium and Levi's Stadium — for the Malayali families in Santa Clara, the Punjabi communities in Vancouver, the Gujarati households in New Jersey — they are the closest thing to seeing India at the World Cup.

The tournament starts in sixteen days. India is not on the team sheet. Indian roots are on the pitch.""",
}


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-27 06:05 UTC (May 26 23:05 PDT)")
    print("3 articles: RCB Qualifier 1, Thunder Game 5, World Cup diaspora")
    print("=" * 60)

    articles = [
        ("RCB crush GT by 92 runs in Qualifier 1", a1, a1_id, ["Rajat Patidar", "Rajat Patidar (cricketer)", "Virat Kohli"]),
        ("Thunder beat Spurs 127-114 in Game 5", a2, a2_id, ["Shai Gilgeous-Alexander", "Shai Gilgeous-Alexander (basketball player)", "Victor Wembanyama"]),
        ("Indian-origin footballers at World Cup 2026", a3, a3_id, ["Sarpreet Singh", "Sarpreet Singh (footballer)", "Tahsin Mohammed Jamshid"]),
    ]

    published = 0
    for idx, (label, art, art_id, wiki_people) in enumerate(articles, 1):
        slug = art["slug"]
        if slug_exists(slug):
            print(f"\n[{idx}/{len(articles)}] SKIP (slug exists): {slug}")
            continue

        print(f"\n[{idx}/{len(articles)}] Inserting: {label}...")
        try:
            insert_article(art)
            print(f"  ✓ Inserted: {slug}")
            published += 1
        except Exception as e:
            print(f"  ✗ Insert failed: {e}")
            continue

        # Image sourcing — Wikipedia first
        img_url = None
        img_attribution = "Wikimedia Commons"
        for person in wiki_people:
            img_url = fetch_wikipedia_person_image(person)
            if img_url:
                break

        if not img_url:
            # Pexels fallback with specific terms
            if "RCB" in label:
                img_url = fetch_pexels_image("IPL cricket stadium India", "cricket match India")
            elif "Thunder" in label:
                img_url = fetch_pexels_image("NBA basketball arena playoffs", "basketball game crowd arena")
            elif "World Cup" in label:
                img_url = fetch_pexels_image("FIFA World Cup football stadium", "soccer match stadium international")
            if img_url:
                img_attribution = "The Videshi"

        if img_url:
            img_path = f"/tmp/{art_id}.jpg"
            if download_image(img_url, img_path):
                uploaded_url = upload_image(art_id, img_path)
                if uploaded_url:
                    update_article_image(art_id, uploaded_url, img_attribution)
        else:
            print(f"  No image found — article published without image (better than wrong image)")

        time.sleep(1)

    # Score decay
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    print(f"\n{'=' * 60}")
    print(f"Done. {published} articles published.")
    for idx, (label, art, art_id, _) in enumerate(articles, 1):
        print(f"  {idx}: {art['slug']}")
    print(f"{'=' * 60}")
