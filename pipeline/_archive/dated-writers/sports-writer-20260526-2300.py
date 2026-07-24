#!/usr/bin/env python3
"""Sports writer — 2026-05-26 23:00 PDT (06:00 UTC May 27): 2 articles + score decay.

Article 1: Thunder beat Spurs 127-114 in Game 5 — SGA 32 points, OKC takes 3-2 lead,
           one win from NBA Finals vs Knicks; Wembanyama limited to 20 points.
Article 2: Three footballers of Indian origin heading to FIFA World Cup 2026 —
           Sarpreet Singh (NZ), Tahsin Mohammed Jamshid (Qatar/Kerala), Niall Mason (Qatar);
           India absent but diaspora represented at football's biggest stage.
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
            f"{person_name} (basketball)",
            f"{person_name} (footballer)",
            f"{person_name} (soccer)",
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


# ── ARTICLE 1: Thunder 127, Spurs 114 — SGA leads OKC to 3-2 lead ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Shai Gilgeous-Alexander Scored Thirty-Two Points. Jared McCain Made His First Playoff Start and Hit Two Clutch Threes. The Thunder Beat the Spurs by Thirteen. They Are One Win From the Finals. The Knicks Are Waiting.",
    "subheadline": "The Oklahoma City Thunder beat the San Antonio Spurs 127-114 in Game 5 of the Western Conference Finals at Paycom Center on Tuesday night, taking a 3-2 series lead. Shai Gilgeous-Alexander led all scorers with 32 points and 9 assists. Jared McCain, making his first postseason start in place of the injured Jalen Williams, scored 20 points and hit two critical three-pointers in the fourth quarter that broke the game open. Alex Caruso added 22 off the bench. Chet Holmgren contributed 16 points and 11 rebounds. Victor Wembanyama was limited to 20 points and 6 rebounds. The Thunder led by as many as 20 and overcame the absence of both Jalen Williams (hamstring) and Ajay Mitchell (calf). The series shifts to San Antonio for Game 6 on Thursday. The New York Knicks, who swept the Cavaliers on Monday, are resting and waiting at Madison Square Garden.",
    "slug": "thunder-beat-spurs-127-114-game-5-sga-32-mccain-clutch-3-2-lead-nba-finals-knicks-wait-20260527",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "The NBA Finals are set to begin June 3 at Madison Square Garden, and the New York Knicks already know they will be there. What they do not know is whether they will face Shai Gilgeous-Alexander and the defending champion Thunder or Victor Wembanyama and the Spurs. For the Indian diaspora in America — particularly the one million-plus Indian Americans in the New York tri-state area — this is the week that determines the shape of June. Basketball is the fastest-growing sport among Indian Americans under 30. The NBA's India investment (preseason games in Mumbai, 200 million social media followers in India, JioCinema and Sports18 broadcasts) means the Finals will reach audiences from Jersey City to Juhu. A Thunder-Knicks series would feature the two best players in basketball: SGA and Jalen Brunson. A Spurs-Knicks series would give the Finals a generational spectacle in Wembanyama. Either way, Madison Square Garden in June is appointment viewing for every NRI in New York. Game 6 is Thursday at 5:30 PM Pacific, 8:30 PM Eastern, and 6:00 AM IST on Friday — another early morning for fans in India, a prime-time event for the diaspora.",
    "tags": ["Oklahoma City Thunder", "San Antonio Spurs", "Shai Gilgeous-Alexander", "Jared McCain", "Victor Wembanyama", "Chet Holmgren", "Alex Caruso", "Jalen Williams", "De'Aaron Fox", "Stephon Castle", "Julian Champagnie", "NBA Playoffs 2026", "Western Conference Finals", "New York Knicks", "NBA Finals", "Madison Square Garden", "Mark Daigneault", "Mitch Johnson"],
    "urgency": "daily",
    "sources": [
        "https://www.reuters.com/article/shai-gilgeous-alexander-pushes-thunder-past-spurs-for-3-2-edge/",
        "https://www.oklahoman.com/story/sports/nba/thunder/2026/05/26/thunder-spurs-score-live-updates-nba-playoffs-game-5-western-conference-finals-injury-report-wcf/",
        "https://www.usatoday.com/story/sports/nba/playoffs/2026/05/27/thunder-vs-spurs-game-5-takeaways/",
        "https://www.sportingnews.com/us/nba/news/nba-playoffs-bracket-2026-schedule-scores/"
    ],
    "word_count": 850,
    "score_total": 62,
    "body": """Two days ago, the Oklahoma City Thunder scored 82 points in the worst offensive game of their season. They shot 6 for 33 from three-point range. Victor Wembanyama blocked everything near the rim. The Spurs won by 21 and tied the series at 2-2.

On Tuesday night at Paycom Center, the Thunder scored 69 points in the first half alone.

The final score was 127-114. OKC leads the Western Conference Finals 3-2. One more win — on Thursday in San Antonio or, if necessary, on Saturday back in Oklahoma City — and they return to the NBA Finals for the second consecutive year. The New York Knicks, who swept the Cavaliers on Monday, are resting and waiting at Madison Square Garden.

## The SGA game

Shai Gilgeous-Alexander has been the best player in basketball for two seasons. On nights when he decides to be aggressive from the opening minute, the Thunder are nearly impossible to beat. Tuesday was one of those nights.

He finished with 32 points on efficient shooting, 9 assists, and the kind of controlled orchestration that makes OKC's motion offense hum. When the Spurs cut a 20-point lead to single digits in the third quarter — a 14-2 San Antonio run capped by Devin Vassell and Stephon Castle threes — Gilgeous-Alexander responded by drawing fouls, getting to the line, and converting a three-point play that pushed the lead back to 13.

He committed six turnovers, more than his usual standard, but it hardly mattered. The Thunder's offensive engine was running on all cylinders.

"Game 4 was our worst offensive game by a mile from a process standpoint," head coach Mark Daigneault had said before tip-off. "But we were a game removed from 120 points in back-to-back games. Nothing from Game 4 carries over to tonight. It's a blank canvas."

The blank canvas turned into a masterpiece.

## McCain's moment

The most surprising performance of the night came from Jared McCain, who was making his first postseason start. With Jalen Williams out for the third consecutive game due to a left hamstring strain and backup guard Ajay Mitchell sidelined with a calf injury, Daigneault inserted McCain into the starting five alongside Gilgeous-Alexander, Lu Dort, Chet Holmgren, and Isaiah Hartenstein.

McCain responded with 20 points, including two three-pointers in the fourth quarter that effectively ended the game. The first came off a Gilgeous-Alexander kick-out — a deep triple from the right wing that pushed OKC's lead to 112-99 with six minutes remaining. McCain grabbed the ball, pounded it against the floor, and waved his hand at the Paycom Center crowd.

The second was even deeper, a transition pull-up that landed with 3:48 left and put the Thunder up 17. San Antonio called timeout. The arena was as loud as it has been all postseason.

McCain is 22 years old. He was acquired in a trade earlier this season. He has never started a playoff game before Tuesday. He played like a veteran who had done it a hundred times.

## Caruso and Holmgren

Alex Caruso, OKC's most valuable bench player, had the kind of night that justifies the Thunder's decision to trade for him last summer. He scored 22 points on efficient shooting, added 6 assists, and provided the defensive intensity that kept the Spurs' second unit in check. During a stretch midway through the second quarter when the Thunder opened a 16-8 run with Gilgeous-Alexander on the bench, Caruso was the engine — scoring 6 points and orchestrating the offense like a secondary point guard.

Chet Holmgren, who had been criticised for his passivity in Games 3 and 4, was aggressive from the first possession. He finished with 16 points and 11 rebounds, going 4-for-4 in the first quarter. On one fastbreak in the fourth quarter, Holmgren kept the ball himself, drove at the smaller Keldon Johnson, drew the foul, and converted both free throws. After Game 4, he had said he would "do everything to take advantage of his opportunities." On Tuesday, he delivered.

## Wembanyama contained

Victor Wembanyama, the 7-foot-4 French centre who has been the most spectacular individual performer of the 2026 playoffs, was limited to 20 points and 6 rebounds — well below his series averages. The Thunder's defensive scheme, which rotates multiple bodies at him and concedes perimeter shots to less dangerous shooters, worked to near-perfection.

Stephon Castle had 24 points. Julian Champagnie, who opened the game with two quick three-pointers and had 13 first-quarter points, finished with 22. De'Aaron Fox contributed 18 but was hounded by Dort and Caruso on the perimeter.

The Spurs' problem is not a lack of talent. It is that Wembanyama cannot carry the scoring load alone against a defence designed to make everyone else beat you — and on Tuesday, "everyone else" was not quite enough.

## What happens next

Game 6 is Thursday night at the Frost Bank Center in San Antonio. If the Spurs win, the series returns to Paycom Center for a decisive Game 7 on Saturday. If the Thunder close it out, the NBA Finals begin June 3 in New York.

The Knicks, who have won 11 consecutive postseason games, will have been resting for more than a week by the time the Finals start. They will have home-court advantage. They will have Madison Square Garden. And they will know exactly who they are facing.

For the Thunder, the equation is simple: one more win. They have Gilgeous-Alexander. They have a supporting cast that showed on Tuesday it can fill the gaps left by Williams and Mitchell. They have home court if it goes to seven.

For the Spurs, the equation is equally simple: they must win two consecutive games, starting in front of their own fans. Wembanyama must be better. Fox must be more assertive. And someone — Castle, Champagnie, Vassell — must provide the secondary scoring that was present in Games 1 and 4 but absent in Games 2, 3, and 5.

The NBA's two remaining teams will play at least once more. The Knicks will watch from afar. The Finals are eight days away.

Game 6 tips off at 8:30 PM Eastern on Thursday — 5:30 PM Pacific, 6:00 AM IST on Friday. For the Indian diaspora in the US, it is a prime-time event. For fans in India, it is another early-morning alarm. The NBA has made both audiences matter.""",
}


# ── ARTICLE 2: Three Indian-origin footballers heading to FIFA World Cup 2026 ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "India Did Not Qualify for the World Cup. Three Footballers of Indian Origin Will Play in It Anyway. One Was Born in Auckland to Indian Parents and Once Played for Bayern Munich. One Is a Nineteen-Year-Old Winger Whose Parents Are from Kannur, Kerala. One Trained at Real Madrid's Academy.",
    "subheadline": "The FIFA World Cup 2026 begins June 11 in the United States, Canada, and Mexico. India is not in the 48-team tournament. But three footballers of Indian heritage will be. Sarpreet Singh, a 25-year-old attacking midfielder born in Auckland to Indian parents, has been confirmed in New Zealand's final 26-man squad — the same player who in 2019 became the first person of Indian origin to play for FC Bayern Munich in the Bundesliga. Tahsin Mohammed Jamshid, a 19-year-old winger whose parents come from Thalassery and Valapattanam in Kannur district, Kerala, is in Qatar's preliminary 34-man squad — if he survives the final cut, he will become the first Malayali footballer ever to play in a World Cup. Niall Mason, a defender with an Indian mother who trained at Real Madrid, Aston Villa, and Southampton's academies, is also in Qatar's preliminary squad. For the four million Indian Americans who will be watching the World Cup in their own country, these three players offer something India's football establishment has not: representation at the sport's biggest stage.",
    "slug": "three-indian-origin-footballers-world-cup-2026-sarpreet-singh-tahsin-jamshid-niall-mason-diaspora-20260527",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "The 2026 FIFA World Cup will be played in 16 cities across the United States, Canada, and Mexico — the three countries where the largest populations of the Indian diaspora outside India live. Matches will be held in New York, Los Angeles, Houston, the Bay Area, Seattle, Dallas, Philadelphia, Miami, and Boston — every one of which has a significant Indian American community. For the first time in history, millions of NRIs will be able to attend a World Cup match without leaving their home country. India's men's football team is not there. The AIFF's failures in development, qualification, and infrastructure are well documented. But three players of Indian heritage — Sarpreet Singh for New Zealand, and Tahsin Mohammed Jamshid and Niall Mason for Qatar — carry Indian stories onto the World Cup stage. Sarpreet, whose parents immigrated to New Zealand from India, could have represented India before committing to the All Whites. Tahsin's parents are from Kerala — if he plays, he becomes the first Malayali at a World Cup, a fact that will reverberate through every chai kadai in Kannur, every WhatsApp group in the Mallu diaspora, and every ISL watch party from Kochi to Kozhikode. Broadcast rights for India are still being finalised — Zee Entertainment is in active negotiations with FIFA — but with matches in US time zones (morning IST, prime-time in America), the World Cup is structurally designed for diaspora viewing. This is the tournament the NRI community will experience live, in person, in their own cities. India is absent from the pitch. Indian roots are not.",
    "tags": ["FIFA World Cup 2026", "Sarpreet Singh", "Tahsin Mohammed Jamshid", "Niall Mason", "New Zealand Football", "Qatar Football", "Indian Diaspora", "Indian Football", "Kerala", "Kannur", "Bayern Munich", "Al Duhail SC", "AIFF", "Wellington Phoenix", "FIFA", "World Cup North America"],
    "urgency": "daily",
    "sources": [
        "https://www.indiasportshub.com/articles/three-footballers-of-indian-origin-set-for-fifa-world-cup-2026-spotlight",
        "https://en.wikipedia.org/wiki/Sarpreet_Singh",
        "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup",
        "https://qncnews.com/zee-entertainment-pursues-streaming-rights-for-2026-fifa-world-cup-in-india/"
    ],
    "word_count": 880,
    "score_total": 65,
    "body": """The 2026 FIFA World Cup begins June 11 in Mexico City. The final will be played July 19 at MetLife Stadium in East Rutherford, New Jersey — across the Hudson River from Manhattan, in a stadium that seats 82,500, in a metropolitan area that is home to more than one million Indian Americans.

India will not be at the tournament. India has qualified for one World Cup in its history — 1950, when it withdrew before playing a match. The gap between Indian football and the rest of the world remains vast. The AIFF's governance crises, the lack of grassroots infrastructure, and the inconsistency of the Indian Super League as a development pathway are problems that have been discussed for decades and solved for none.

But three footballers of Indian origin will be at the World Cup. Their stories are different from each other, and different from anything Indian football has produced on its own.

## Sarpreet Singh — the one who could have played for India

Sarpreet Singh is 25 years old. He was born in Auckland to Indian parents. He grew up playing football in New Zealand's youth system, and by 2019 he had done something no person of Indian origin had done before: he played for FC Bayern Munich in the Bundesliga, Germany's top division, one of the most competitive football leagues on Earth.

That sentence alone should have made him one of the most celebrated figures in Indian sports. It did not. Because Sarpreet chose New Zealand — the country of his birth, the country whose passport he holds, the country whose youth teams developed him — over India.

He was technically eligible to represent India during the early stages of his career, before he committed to the All Whites. The possibility never materialised. Whether the AIFF made a serious approach, whether the scouting infrastructure existed to identify him, whether the bureaucratic machinery of Indian football was capable of reaching across the Pacific — these are questions that the Indian football establishment has never satisfactorily answered.

Sarpreet's club career since Bayern has been uneven. Injuries and inconsistent playing time slowed his momentum. He returned to the A-League with Wellington Phoenix FC and dealt with a knee injury this season. But he recovered in time to earn his place in New Zealand's final 26-man World Cup squad. He is a creative attacking midfielder with technical quality that remains among the best of any player with Indian heritage anywhere in the world.

New Zealand are in Group D alongside France, Peru, and Saudi Arabia. They open against Peru on June 15 in Los Angeles. For Indian Americans on the West Coast — the Bay Area, LA, Seattle — this is a match they can attend and know that a player with Indian roots is on the pitch.

## Tahsin Mohammed Jamshid — the one from Kannur

If Sarpreet Singh's story is about a path not taken, Tahsin Mohammed Jamshid's story is about a path that did not exist until he made it.

Tahsin is 19 years old. He plays as a winger for Al Duhail SC in the Qatar Stars League. Both his parents are from Kannur district in Kerala — his roots are in Thalassery and Valapattanam, two towns that any Malayali will recognise instantly. He is the first footballer of Indian origin to play in the Qatar Stars League. He progressed through Qatar's youth national teams and made his senior debut during the World Cup qualifiers.

He is in Qatar's preliminary 34-man squad, announced by head coach Julen Lopetegui. If he survives the final cut to 26, he will become the first Malayali footballer ever to participate in a FIFA World Cup.

That sentence carries weight that statistics cannot capture. Kerala is the most football-obsessed state in India. The ISL's Kerala Blasters have one of the largest fanbases in Indian football. Every village in Malabar has a football ground and a tournament. The idea that a boy whose parents left Kannur could play on the World Cup stage — not for India, but for Qatar — is the kind of story that will travel through every WhatsApp family group, every NRI gathering, every Malayali association in the Gulf and the United States.

Qatar are in Group A alongside the United States, Senegal, and Chile. They open against Chile on June 12 in Houston — a city with one of the largest Indian American populations in the US. If Tahsin plays, the Kerala community in Houston will be in the stands.

## Niall Mason — the one from the academies

The third player is Niall Mason, a defender with an Indian mother who brings a very different football background to the conversation. Mason spent time developing within some of the most prestigious academy systems in European football — Real Madrid, Aston Villa, and Southampton. That pedigree gave him a defensive foundation built on elite coaching and competitive pressure from a young age.

He eventually entered Qatar's football ecosystem and received his first senior national team call-up earlier this year. He is in Qatar's preliminary 34-man squad, and while competition for defensive spots is intense, his inclusion signals the faith Qatar's coaching staff have in his versatility and experience.

Mason's story is less about Indian football's failures and more about the globalisation of talent. Players with Indian heritage are developing in academy systems across Europe, the Middle East, and Oceania. The pipeline exists. What India lacks is the ability to identify, attract, and integrate that talent — or to produce it domestically at the same level.

## What this means for the diaspora

The 2026 World Cup is the first to be held across three countries — the US, Canada, and Mexico — and the first with 48 teams and 104 matches. It is also the first World Cup where millions of Indian Americans can attend matches in person, in their own cities, without a long-haul flight.

Games will be played in MetLife Stadium (New York), SoFi Stadium (Los Angeles), Levi's Stadium (Bay Area), NRG Stadium (Houston), AT&T Stadium (Dallas), Lincoln Financial Field (Philadelphia), Hard Rock Stadium (Miami), Lumen Field (Seattle), Gillette Stadium (Boston), and others. Every single one of those cities has a significant Indian American community.

India's absence from the pitch is a failure of administration, not of interest. India has 1.4 billion people and one of the world's most passionate sporting cultures. But its football federation has produced zero World Cup appearances in 76 years.

Sarpreet Singh, Tahsin Mohammed Jamshid, and Niall Mason did not wait for the AIFF. They found football in Auckland, Doha, and European academies. They will represent New Zealand and Qatar, not India. But for the Indian diaspora watching from MetLife, SoFi, and NRG Stadium — for the Malayali families in Houston, the Punjabi communities in Vancouver, the Gujarati households in New Jersey — they are the closest thing to seeing India at the World Cup.

The tournament starts in sixteen days. India is not on the team sheet. Indian roots are on the pitch. For now, that will have to be enough.""",
}


if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-26 23:00 PDT (06:00 UTC May 27)")
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

    # ── Insert + image: Article 1 (Thunder 127, Spurs 114 — Game 5) ──
    print("\n[1/2] Inserting: Thunder beat Spurs 127-114, take 3-2 lead...")
    insert_article(a1)
    print(f"  ✓ Inserted: {a1['slug']}")

    # Image: SGA (central figure) on Wikipedia
    img1_url = fetch_wikipedia_person_image("Shai Gilgeous-Alexander")
    img1_attribution = "Wikimedia Commons"
    if not img1_url:
        img1_url = fetch_wikipedia_person_image("Victor Wembanyama")
    if not img1_url:
        img1_url = fetch_wikipedia_person_image("Chet Holmgren")
    if not img1_url:
        img1_url = fetch_wikipedia_person_image("Paycom Center")
    if not img1_url:
        # Pexels fallback: specific basketball imagery
        img1_url = fetch_pexels_image("NBA basketball arena playoffs", "basketball game crowd arena")
        img1_attribution = "The Videshi"

    if img1_url:
        img1_path = f"/tmp/{a1_id}.jpg"
        if download_image(img1_url, img1_path):
            uploaded_url = upload_image(a1_id, img1_path)
            if uploaded_url:
                update_article_image(a1_id, uploaded_url, img1_attribution)

    # ── Insert + image: Article 2 (Indian-origin World Cup footballers) ──
    print("\n[2/2] Inserting: Three Indian-origin footballers heading to World Cup 2026...")
    insert_article(a2)
    print(f"  ✓ Inserted: {a2['slug']}")

    # Image: Sarpreet Singh (most prominent) on Wikipedia
    img2_url = fetch_wikipedia_person_image("Sarpreet Singh")
    img2_attribution = "Wikimedia Commons"
    if not img2_url:
        img2_url = fetch_wikipedia_person_image("Sarpreet Singh (footballer)")
    if not img2_url:
        # Try World Cup venue or general football
        img2_url = fetch_wikipedia_person_image("MetLife Stadium")
    if not img2_url:
        img2_url = fetch_pexels_image("FIFA World Cup football stadium", "soccer match stadium international")
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
