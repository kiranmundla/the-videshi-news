#!/usr/bin/env python3
"""Sports writer — 2026-05-26 20:00 PDT (03:00 UTC May 27): 2 articles + score decay.

Article 1: Norway Chess Round 2 — Firouzja's perfect 6/6, Indian trio's struggles,
           Round 3 showdown (Firouzja vs Gukesh, Pragg vs Carlsen, Assaubayeva vs Divya)
Article 2: Knicks sweep Cavaliers 130-93 to reach first NBA Finals since 1999 —
           diaspora angle: NYC's massive Indian community, NBA India growth
"""

import os, json, uuid, requests, subprocess, sys, urllib.parse
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

    # Try alternate name forms with disambiguation
    alternates = []
    if "(" not in person_name:
        alternates = [
            f"{person_name} (chess player)",
            f"{person_name} (chess)",
            f"{person_name} (basketball)",
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


# ── ARTICLE 1: Norway Chess Round 2 — Firouzja's perfect 6/6, Indian trio ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Firouzja Has Won Every Point Available. He Beat Carlsen on Day One. He Beat Praggnanandhaa on Day Two. He Has a Three-and-a-Half-Point Lead. He Is Playing With an Injured Ankle. On Wednesday He Faces Gukesh.",
    "subheadline": "Alireza Firouzja has a perfect 6/6 score after two rounds of Norway Chess 2026 in Oslo — the only player to win both his classical games. On Monday he dismantled Praggnanandhaa Rameshbabu, who had seemed to be gaining an edge before losing his way and being smoothly dispatched in the endgame. World Champion Gukesh Dommaraju forced Wesley So into a queen sacrifice in a 116-move classical battle but could not convert, then lost in armageddon. Divya Deshmukh beat Koneru Humpy in armageddon to sit 1.5 points behind women's leader Bibisara Assaubayeva. Round three on Wednesday brings the pairings the tournament needed: Firouzja against Gukesh, Praggnanandhaa against Carlsen, and Assaubayeva against Divya.",
    "slug": "norway-chess-2026-round-2-firouzja-perfect-6-pragg-gukesh-divya-round-3-pairings-20260526",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Norway Chess is the strongest round-robin chess tournament in the world, and three of its twelve competitors — Gukesh Dommaraju, Praggnanandhaa Rameshbabu, and Divya Deshmukh — are Indian. For the chess-obsessed Indian diaspora, this tournament is appointment viewing. Round three starts at 5:00 PM CEST, which is 8:30 PM IST, 8:00 AM Pacific, 11:00 AM Eastern, and 4:00 PM BST. The pairings are electric: World Champion Gukesh plays the tournament leader Firouzja with the Black pieces, eighteen-year-old Praggnanandhaa faces Magnus Carlsen (both are winless), and Divya faces Assaubayeva for the women's lead. For NRIs in the US, these are morning matches — watchable over coffee before work. For the UK diaspora, they are late afternoon. Indian chess has produced the world champion and two of the game's brightest young talents, but in Oslo, all three are losing ground to a 23-year-old Frenchman playing through pain. Wednesday is where the Indian fightback begins — or the French coronation continues.",
    "tags": ["Norway Chess 2026", "Alireza Firouzja", "Gukesh Dommaraju", "Praggnanandhaa Rameshbabu", "Divya Deshmukh", "Magnus Carlsen", "Wesley So", "Vincent Keymer", "Koneru Humpy", "Bibisara Assaubayeva", "Anna Muzychuk", "Ju Wenjun", "Zhu Jiner", "Chess", "Oslo", "Round Robin", "Armageddon"],
    "urgency": "daily",
    "sources": [
        "https://www.chess.com/news/view/2026-norway-chess-round-2",
        "https://en.chessbase.com/post/norway-chess-firouzja-carlsen-win-2026",
        "https://chessbase.in/news/Norway-Chess-2026-Firouzja-Stuns-Carlsen-Indian-Trio-Wins-Armageddon",
        "https://en.wikipedia.org/wiki/Norway_Chess_2026"
    ],
    "word_count": 870,
    "score_total": 70,
    "body": """The Norway Chess scoring system is unusual. A classical win earns three points. A draw in classical leads to an armageddon game, where the winner gets 1.5 points and the loser gets 1. There are no zero-point results. Every round, every player collects something. The system rewards aggression and punishes draws, and through two rounds in Oslo, one player has treated it as a personal invitation.

Alireza Firouzja has 6 points from a possible 6. He beat Magnus Carlsen classically on Day One. He beat Praggnanandhaa Rameshbabu classically on Day Two. Nobody else has won a single classical game. His lead is 3.5 points — a margin that, in a six-round tournament, is already close to decisive.

He is doing this with an injured ankle.

## The Praggnanandhaa game

Monday's round-two match between Firouzja and Praggnanandhaa was not the straightforward domination that the 3-0 scoreline suggests. The opening was unremarkable — Firouzja himself dismissed any suggestion that preparation was involved. "Not today, for sure. It was a decent game, but I don't think the opening was something special."

The middle game was more complex. Praggnanandhaa appeared to be gaining ground, finding active piece placements that suggested the initiative was shifting. But he lost his way in the transition to the endgame, traded down into an inferior structure, and Firouzja converted with clinical precision. The Indian prodigy, who had drawn his Round 1 classical game against Carlsen and won the armageddon, was dispatched without a tiebreaker.

Asked about playing through pain, Firouzja offered a line that captures something essential about elite competition: "I don't know if it's a boost, but I'm trying to play chess. I have a lot of pain, but it's something that keeps me focused — it makes me not think about pain."

He is back in the world's top ten on the live rating list after undoing most of the damage from three losses in Bucharest the previous week. The trajectory is unmistakable.

## Gukesh's 116-move near-miss

World Champion Gukesh Dommaraju played 116 moves against Wesley So on Monday. It was, somehow, shorter than his 144-move draw against Vincent Keymer on Day One. Neither marathon produced a classical win.

Against So, Gukesh found a sequence that forced the American grandmaster into a queen sacrifice. The position was dangerous. So admitted it "got real scary, real quick." But Gukesh could not find the decisive continuation, and So held with a series of only moves — the kind of resourceful defense that earns points in armageddon but not in classical chess.

The armageddon was less dramatic. So won the opening battle and managed his clock efficiently while Gukesh's time management was, as So put it, "very poor." The World Champion lost the armageddon and collected a single point from the round.

After two rounds, Gukesh has 2.5 points — equal with So, but 3.5 behind Firouzja. He has yet to win a classical game. He has played 260 moves of classical chess. He has found positions that should have won. He has not won.

## Carlsen's udder embarrassment

Magnus Carlsen's Round 2 classical game against Vincent Keymer was, by the Norwegian's own description, chaotic. He put a knight on a7 in homage to Anatoly Karpov's famous positional masterpiece, joked in the confessional that the game was "an udder embarrassment" (a dad joke involving a cow), and then proceeded to miss a winning continuation on move 31.

"31...Ne8 shocked me, that was just a blunder, and then I should of course win the game," Carlsen said. But he squandered the advantage twice, Keymer found the equalizing queen trade, and the game fizzled into a draw. Carlsen won the armageddon to collect 1.5 points, but the frustration was evident. He has one classical win's worth of points from two rounds.

The defending champion and five-time Norway Chess winner is in last place alongside Praggnanandhaa on 2.5 points. In Round 3, those two play each other — a match between the bottom of the table that features a world number one and an eighteen-year-old who has already beaten Carlsen in armageddon this season.

## Divya's quiet ascent

In the women's tournament, Bibisara Assaubayeva leads with 4.5 points after surviving a scare against Zhu Jiner. The Kazakh grandmaster was losing, then winning, then losing again before drawing the classical game and winning an armageddon in which she blundered, in her own words, "everything that I can. First a piece, then a rook." She won anyway.

Divya Deshmukh is 1.5 points behind Assaubayeva after beating Koneru Humpy in armageddon. Divya's classical game featured an experimental 2.d3 followed by 4.g4 — the kind of ambitious opening choice that signals intent rather than caution. It did not work. Humpy equalized comfortably and was the one pressing by the end. But in the armageddon, Divya switched to the Four Knights, found an edge after Humpy's 18...dxe4, and converted the resulting queenside weaknesses.

When asked about the dried mangos she had been offered during Round 1, Divya laughed: "I think it's there, but I didn't eat it today. I was pretty busy in the game."

Anna Muzychuk completed the women's results by beating Ju Wenjun in armageddon after a deliberately riskless classical draw. Muzychuk admitted her strategy was to play safely in the classical and aggressively in the tiebreaker. It worked — she sacrificed a piece with 27.Nxd6 and delivered checkmate on the board.

## Round 3: the pairings that matter

Wednesday's Round 3 produces the most consequential matchups of the tournament so far.

Firouzja plays Gukesh. The Frenchman has Black. The World Champion needs a classical win to stay in the tournament mathematically; Firouzja needs only a point to extend a lead that may already be insurmountable. This is the match that will determine whether Norway Chess 2026 is a contest or a coronation.

Praggnanandhaa plays Carlsen. Both have 2.5 points. Both are in last place. Both are too good for where they are. One of them will leave Wednesday's session having beaten the other in at least armageddon, and the other will face the prospect of finishing last in a tournament they entered as contenders.

Assaubayeva plays Divya. The women's leader has White against her closest challenger. A classical win for Assaubayeva would put the title virtually beyond reach. A classical win for Divya would create a two-way race entering the tournament's second half.

Round 3 starts at 5:00 PM CEST on Wednesday — 8:30 PM in India, 8:00 AM on the American West Coast, 11:00 AM in New York, 4:00 PM in London. Set the alarm. This is the day that defines the rest of the tournament.""",
}


# ── ARTICLE 2: Knicks sweep Cavaliers, reach first NBA Finals since 1999 ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "The New York Knicks Have Not Played in the NBA Finals Since 1999. On Monday They Demolished the Cavaliers by Thirty-Seven Points to Complete a Four-Game Sweep. Madison Square Garden Will Host the Finals in June.",
    "subheadline": "Karl-Anthony Towns scored 19 points and grabbed 14 rebounds. OG Anunoby added 17 points. The final score was 130-93. The New York Knicks completed a four-game sweep of the Cleveland Cavaliers in the Eastern Conference Finals on Monday night at Rocket Arena — a series so one-sided that the Cavaliers never led in any of the four games by more than a handful of possessions. The Knicks are in the NBA Finals for the first time in twenty-seven years. They will face either the Oklahoma City Thunder or the San Antonio Spurs — that series is tied 2-2 — starting June 3 at Madison Square Garden. Jalen Brunson was named series MVP. The Knicks' eleven-game postseason winning streak is the longest active run in the NBA.",
    "slug": "knicks-sweep-cavaliers-130-93-nba-finals-27-years-madison-square-garden-june-2026-20260526",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "New York City has one of the largest and most established Indian diaspora communities in the world. The tri-state area — New York, New Jersey, and Connecticut — is home to more than one million Indian Americans. Many of them work in Manhattan, commute through Penn Station, and walk past Madison Square Garden every day. For this community, the Knicks' return to the NBA Finals is not just a sports story — it is a civic event. The NBA has invested heavily in India over the past decade, staging preseason games in Mumbai, launching the NBA India Games initiative, and building a fan base that now numbers over 200 million social media followers in the subcontinent. The Finals will air on Sports18 and JioCinema in India, with Game 1 on June 3 at 9:00 PM Eastern (June 4 at 6:30 AM IST). For NRIs in the Bay Area, Houston, Chicago, and the DC corridor — cities with large Indian populations and NBA teams — the Knicks' run has become a topic of group-chat conversation and office-watercooler debate. Basketball is the fastest-growing sport among Indian Americans under 30. A Knicks Finals appearance, at the Garden, against either the defending champion Thunder or the Wembanyama-led Spurs, is the kind of event that converts casual fans into invested ones.",
    "tags": ["New York Knicks", "NBA Finals", "Cleveland Cavaliers", "Karl-Anthony Towns", "OG Anunoby", "Jalen Brunson", "Madison Square Garden", "Eastern Conference Finals", "NBA Playoffs 2026", "Oklahoma City Thunder", "San Antonio Spurs", "Victor Wembanyama", "Kenny Atkinson", "Mike Brown", "Basketball"],
    "urgency": "daily",
    "sources": [
        "https://www.reuters.com/article/knicks-finish-sweep-of-cavs-make-first-nba-finals-since-1999/",
        "https://www.fox5ny.com/sports/knicks-reach-nba-finals-for-first-time-since-1999-after-130-93-sweep-of-cavs",
        "https://www.cnn.com/2026/05/26/sports/knicks-cavaliers-nba-eastern-conference-finals/",
        "https://www.sportingnews.com/us/nba/news/nba-playoffs-bracket-2026-schedule-scores/"
    ],
    "word_count": 860,
    "score_total": 62,
    "body": """The scoreboard at Rocket Arena in Cleveland read 130-93 when it ended. The Cavaliers' home fans had long since gone quiet. The Knicks' bench was standing. Jalen Brunson was being congratulated by teammates who knew, even before the final buzzer, that they were going to the NBA Finals.

Twenty-seven years. That is how long it has been since the New York Knicks played for the NBA championship. The last time was 1999, when Allan Houston and Latrell Sprewell led a number-eight seed to the Finals against the San Antonio Spurs. They lost in five games. Since then, the Knicks have been a punchline — the most valuable franchise in basketball, housed in the most famous arena in sports, and consistently incapable of contending for the title.

On Monday night, that era ended.

## The sweep

The Eastern Conference Finals between the Knicks and the Cleveland Cavaliers was supposed to be competitive. The Cavaliers won 52 games in the regular season. They had Donovan Mitchell, one of the five best scorers in basketball. They had Evan Mobley, a defensive anchor who can guard every position. They had home-court advantage through the first two rounds.

None of it mattered.

Game 1 in New York went to overtime before the Knicks pulled away, 115-104. Game 2 was more decisive: Knicks 109, Cavaliers 93. Game 3 in Cleveland was the first real blowout, 121-108. And Game 4 was annihilation. The Knicks led 38-26 after the first quarter, 68-49 at halftime, and 98-71 after three. The fourth quarter was garbage time played out by both benches.

The cumulative margin across the four games was 87 points. The Knicks' point differential in the playoffs — spanning sweeps of their first-round opponent and the Cavaliers — is plus-262. They have won eleven consecutive postseason games, the longest active streak in the league.

Karl-Anthony Towns was the engine of Game 4. His 19 points and 14 rebounds anchored the offense and the boards, and his ability to stretch the floor with three-point shooting created driving lanes that the Cavaliers could not close. OG Anunoby contributed 17 points with the quiet, efficient defense that has made him the Knicks' most indispensable two-way player. Jalen Brunson, named series MVP, orchestrated the offense with the controlled aggression that has defined his playoff career — never forcing, always probing, and always finding the right pass at the right time.

## What the sweep means

The Cavaliers were not a weak opponent. They were the second seed in the Eastern Conference for much of the season. They had a top-five defense. Mitchell is a legitimate superstar capable of scoring 40 on any given night. But the Knicks exposed a structural problem that the Cavaliers could not solve: when Towns and Anunoby anchored the defense, Mitchell's scoring efficiency plummeted, and without a secondary creator of Mitchell's caliber, Cleveland's offense stagnated.

The sweep also confirmed something that the analytics community had been arguing since February: the Knicks are not just a good team. They are a historically dominant postseason team. Their offensive rating in the playoffs is the highest in franchise history. Their defensive rating is in the top five of all playoff defenses this century. When both sides of the ball operate at this level simultaneously, no opponent has survived more than four games.

Mike Brown, coaching the Knicks in his first season after leaving Sacramento, has built a system that maximizes every player's strengths without sacrificing defensive identity. The Knicks switch everything on defense, force opponents into isolation possessions, and then punish those possessions with length and athleticism. It is not complicated. It is devastatingly effective.

## The Finals opponent

The Knicks will face either the Oklahoma City Thunder or the San Antonio Spurs in the NBA Finals starting June 3 at Madison Square Garden. The Western Conference Finals is tied 2-2, with Game 5 in Oklahoma City on Tuesday night.

If the Thunder advance, the Knicks face the defending champions — the team that won the title last year behind Shai Gilgeous-Alexander and Chet Holmgren. The Thunder have the best regular-season record in the NBA and home-court advantage throughout the playoffs, though the Finals would open in New York if the Knicks' conference-finals sweep gives them schedule priority.

If the Spurs advance, the matchup becomes generational: Brunson and Towns against Victor Wembanyama, the seven-foot-four French center who has already produced one of the most extraordinary individual seasons in NBA history. Wembanyama scored 33 points in 31 minutes in Game 4 of the Western Conference Finals and sat out the entire fourth quarter because the Spurs were winning by too much.

Either opponent presents a formidable challenge. But the Knicks, after eleven straight wins and a 37-point sweep-clinching victory, are not thinking about formidable challenges. They are thinking about what it means to play at the Garden in June.

## Madison Square Garden in June

The Knicks' arena is not just a building. It is the center of New York sports identity — the place where Willis Reed limped onto the court in 1970, where Patrick Ewing anchored a decade of near-misses, where every celebrity courtside seat is a cultural signifier. For two decades, the Garden has hosted playoff basketball that ended in disappointment. The conference semifinals were as far as the franchise could go.

Now the Finals come to Eighth Avenue. Game 1 is June 3. If the series goes seven, Game 7 is June 15. The tickets will be the most expensive in NBA Finals history. The atmosphere will be the loudest the Garden has produced since Ewing's era.

For the Indian diaspora in the New York metro area — one of the largest concentrations of Indian Americans anywhere in the world — the Knicks' Finals run arrives during a moment of peak basketball engagement. NBA India has built a fanbase of more than 200 million social media followers across the subcontinent. The league stages games in Mumbai. Youth basketball programmes in Delhi, Bangalore, and Hyderabad are producing competitive players.

The Finals will air on Sports18 and JioCinema in India. Game 1 tips off at 9:00 PM Eastern on June 3, which is 6:30 AM IST on June 4 — an early-morning watch for fans in India, a prime-time event for the diaspora in America.

The Knicks are in the Finals. The Garden is ready. Twenty-seven years of waiting end in eight days.""",
}


if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-26 20:00 PDT (03:00 UTC May 27)")
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

    # ── Insert + image: Article 1 (Norway Chess Round 2) ──
    print("\n[1/2] Inserting: Norway Chess Round 2 — Firouzja's perfect 6/6...")
    insert_article(a1)
    print(f"  ✓ Inserted: {a1['slug']}")

    # Image: Firouzja (central figure) on Wikipedia
    img1_url = fetch_wikipedia_person_image("Alireza Firouzja")
    img1_attribution = "Wikimedia Commons"
    if not img1_url:
        img1_url = fetch_wikipedia_person_image("Gukesh Dommaraju")
    if not img1_url:
        img1_url = fetch_wikipedia_person_image("Praggnanandhaa Rameshbabu")
    if not img1_url:
        img1_url = fetch_wikipedia_person_image("Divya Deshmukh")
    if not img1_url:
        # Pexels fallback: specific chess imagery
        img1_url = fetch_pexels_image("chess grandmaster tournament", "chess pieces tournament board")
        img1_attribution = "The Videshi"

    if img1_url:
        img1_path = f"/tmp/{a1_id}.jpg"
        if download_image(img1_url, img1_path):
            uploaded_url = upload_image(a1_id, img1_path)
            if uploaded_url:
                update_article_image(a1_id, uploaded_url, img1_attribution)

    # ── Insert + image: Article 2 (Knicks sweep to NBA Finals) ──
    print("\n[2/2] Inserting: Knicks sweep Cavaliers, reach first NBA Finals in 27 years...")
    insert_article(a2)
    print(f"  ✓ Inserted: {a2['slug']}")

    # Image: Madison Square Garden or Jalen Brunson on Wikipedia
    img2_url = fetch_wikipedia_person_image("Jalen Brunson")
    img2_attribution = "Wikimedia Commons"
    if not img2_url:
        img2_url = fetch_wikipedia_person_image("Karl-Anthony Towns")
    if not img2_url:
        img2_url = fetch_wikipedia_person_image("Madison Square Garden")
    if not img2_url:
        img2_url = fetch_pexels_image("basketball arena NBA game", "Madison Square Garden basketball")
        img2_attribution = "The Videshi"

    if img2_url:
        img2_path = f"/tmp/{a2_id}.jpg"
        if download_image(img2_url, img2_path):
            uploaded_url = upload_image(a2_id, img2_path)
            if uploaded_url:
                update_article_image(a2_id, uploaded_url, img2_attribution)

    # ── Score decay ──
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    print(f"\n{'=' * 60}")
    print(f"Done. 2 articles published.")
    print(f"  1: {a1['slug']}")
    print(f"  2: {a2['slug']}")
    print(f"  IDs: {a1_id}, {a2_id}")
