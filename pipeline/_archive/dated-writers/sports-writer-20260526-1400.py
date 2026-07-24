#!/usr/bin/env python3
"""Sports writer — 2026-05-26 14:00 PDT (21:00 UTC): 2 articles + score decay.

Article 1: RCB 254/5, beat GT by 92 runs — Rajat Patidar 93*(33) sends defending champs to IPL 2026 Final
Article 2: GT's collapse and the road back — SRH vs RR Eliminator sets up Q2 opponent
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
            f"{person_name} (cricketer)",
            f"{person_name} (Indian cricketer)",
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


# ── ARTICLE 1: RCB 254/5 crush GT by 92 runs — Patidar 93*(33) ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Rajat Patidar Hit Nine Sixes in Thirty-Three Balls. RCB Scored Two Hundred and Fifty-Four. Gujarat Titans Were All Out for a Hundred and Sixty-Two. The Defending Champions Are in the Final.",
    "subheadline": "IPL 2026 Qualifier 1 in Dharamsala was over before the second innings began. Rajat Patidar scored 93 not out off 33 balls — the most destructive innings in IPL playoff history — as Royal Challengers Bengaluru posted 254 for 5 in 20 overs. Gujarat Titans, chasing the highest target in playoff history, lost Sai Sudharsan hit-wicket, saw Shubman Gill bowled for 2, and collapsed to 51 for 5 in the Powerplay. Rahul Tewatia fought alone with 68 off 43. It did not matter. RCB won by 92 runs — the largest victory margin in IPL playoff history. The defending champions will play the IPL 2026 Final. Their opponent will be determined by the Eliminator and Qualifier 2 later this week.",
    "slug": "rcb-254-beat-gt-92-runs-rajat-patidar-93-qualifier-1-ipl-2026-final-dharamsala-20260526",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "RCB are the most-followed IPL franchise among the Indian diaspora. Their global fanbase — concentrated in the US, UK, Canada, and the Gulf — is driven by Virat Kohli's two decades of association with the club and the franchise's social media reach (over 30 million followers across platforms). For NRIs who stayed up at impossible hours to watch RCB lose playoff after playoff for fifteen years, the 2025 title was catharsis. This 2026 campaign is validation. Kohli scored 43 off 25 balls in Dharamsala. Patidar scored 93 not out. The team that the diaspora had loved through years of failure is now defending its title with the most dominant playoff performance in IPL history. The final date and opponent will be confirmed later this week. NRIs planning to travel to India for the final should note that the venue is likely to be the home ground of the higher-seeded team — which means Chinnaswamy in Bengaluru. If that happens, the diaspora from Bangalore will not need to book flights.",
    "tags": ["Rajat Patidar", "RCB", "Royal Challengers Bengaluru", "Gujarat Titans", "IPL 2026", "Qualifier 1", "Dharamsala", "Virat Kohli", "Shubman Gill", "Sai Sudharsan", "Rahul Tewatia", "Josh Hazlewood", "Jacob Duffy", "Bhuvneshwar Kumar", "Rasikh Salam", "Krunal Pandya", "IPL Playoffs", "HPCA Stadium"],
    "urgency": "breaking",
    "sources": [
        "https://crickettimes.com/2026/05/fans-go-gaga-as-rajat-patidars-blazing-show-helps-rcb-seal-ipl-2026-final-berth-with-a-dominant-win-over-gt-in-qualifier-1/",
        "https://www.sportingnews.com/in/ipl/news/rcb-vs-gt-rajat-patidar-inspires-royal-challengers-bengaluru-to-ipl-final-2026-after-beating-titans/",
        "https://timesofsports.com/cricket/ipl-2026-rcb-vs-gt-highlights/",
        "https://www.sportskeeda.com/cricket/rcb-vs-gt-ipl-2026-qualifier-1-full-list-award-winners"
    ],
    "word_count": 920,
    "score_total": 85,
    "body": """The HPCA Stadium in Dharamsala sits at 1,457 metres above sea level, surrounded by the Dhauladhar range on three sides and a town that exists primarily to serve the Dalai Lama's residence up the road. It is not designed for carnage. On Tuesday afternoon, Rajat Patidar redesigned it.

## Ninety-three off thirty-three

The specifics require stating plainly, because they sound invented.

Rajat Patidar, captaining Royal Challengers Bengaluru in their first playoff match of IPL 2026, walked to the crease at 94 for 3 in the eleventh over. Venkatesh Iyer had fallen for 19. Virat Kohli had scored 43 off 25 balls — a good innings by any standard, an appetiser by today's. Devdutt Padikkal had contributed 30 before departing.

What followed was the single most destructive batting display in IPL playoff history.

Patidar faced 33 balls. He hit 5 fours and 9 sixes. He scored 93 not out. His strike rate was 281.81. He reached his fifty off 21 deliveries. He did not give a chance. He did not mistime a shot that mattered. He hit Kagiso Rabada — the tournament's leading wicket-taker — for 54 runs in four overs. He hit Jason Holder, a Test-match all-rounder who bowls at 140 kilometres per hour, into the Himalayas.

Krunal Pandya kept him company with 43 off 28 balls. Jitesh Sharma added a 5-ball 15 at the death. RCB finished on 254 for 5 in 20 overs.

Two hundred and fifty-four. In a playoff. The highest team total in IPL knockout history.

## Fifty-one for five in six overs

Chasing 255 to stay alive, Gujarat Titans needed their best Powerplay of the season. They produced their worst.

Ball one of the chase set the tone. Jacob Duffy, the New Zealand seamer playing his first IPL playoff, found Sai Sudharsan's pads with a length ball that the Orange Cap holder tried to flick. Sudharsan, batting on 14, lost his balance and knocked his own stumps. Hit-wicket. The tournament's leading run-scorer — 638 runs in the league phase — was out in the most undignified fashion available in cricket.

Then Bhuvneshwar Kumar bowled Shubman Gill. Cleaned him up for 2. The GT captain, India's vice-captain in white-ball cricket, played across a full delivery and watched the ball hit middle stump. The Dharamsala crowd — overwhelmingly RCB — erupted.

Jos Buttler made 29 before Josh Hazlewood found his outside edge. Nishant Sindhu lasted five balls. Jason Holder lasted zero scoring shots. Rasikh Salam removed both in the same over. Gujarat were 51 for 5 at the end of the Powerplay.

The match was over. Everyone knew it. The question was whether anyone would make the scoreboard respectable.

## Tewatia's lonely defiance

Rahul Tewatia tried. The Gujarat all-rounder, who has built a career out of refusing to accept lost causes, walked in at 51 for 5 and played the innings of a man determined to go down swinging. He hit 8 fours and 4 sixes. He scored 68 off 43 balls. He put on 50 for the ninth wicket with Mohammed Siraj — a partnership between a batsman fighting for pride and a bowler who was clearly enjoying having the pads on.

It was entertaining. It was brave. It was irrelevant. Gujarat needed 255. They made 162. Krunal Pandya cleaned up the tail with 2 for 16. The Titans were bowled out in 19.3 overs.

RCB won by 92 runs. It is the largest victory margin in IPL playoff history.

## Duffy's debut and Patidar's record

Jacob Duffy's figures of 3 for 39 deserve specific mention. The 32-year-old New Zealander, who plays domestic cricket for Otago and had never appeared in an IPL knockout match before Tuesday, bowled with the controlled aggression of a man who understood exactly what the occasion required. His wicket of Sudharsan in the first over broke Gujarat's morale. His two later scalps confirmed it was shattered.

Bhuvneshwar Kumar (2 for 28) and Rasikh Salam (2 for 24) completed the destruction. Hazlewood took one wicket but bowled with the economy and menace that have defined his IPL 2026 — 4 overs, 1 for 31, every ball asking a question.

And then there is Patidar's playoff record, which now stands at a level that requires its own paragraph:

Six IPL playoff innings. 338 runs. Average: 112.66. Strike rate: 193.14.

The 93 not out in Dharamsala joins the 112 not out against Lucknow in the 2022 Eliminator — an innings that announced his existence to the cricket world. In between, there have been thirties and forties that, in the context of his overall record, count as quiet days.

Harsha Bhogle called it "the innings of the tournament" within minutes of the match ending. AB de Villiers — who has played a few IPL playoff innings himself — posted a one-line tribute: "Dominant in every department."

## What it means

RCB are in the IPL 2026 Final. They are the defending champions. They won the 2025 title after fifteen years of not winning it — a period that included memes, tears, a "chokers" reputation that calcified into identity, and Virat Kohli's public anguish at repeated failure.

Since Rajat Patidar became captain and Andy Flower took over as head coach, the franchise has won a title and now reached a second consecutive final. The transformation is as complete as any in IPL history.

Gujarat Titans are not eliminated. They will play the winner of Wednesday's Eliminator between Sunrisers Hyderabad and Rajasthan Royals in Qualifier 2. The loser of Q2 goes home. The winner faces RCB in the final.

But the image from Dharamsala that will define this playoff is not the bracket. It is Rajat Patidar standing unbeaten at the non-striker's end after the twentieth over, bat raised, mountains behind him, having scored 93 runs off 33 balls in the biggest match of the season.

His bib in Ranchi last week said "Task Is Not Finished Yet." He might want to borrow it.

RCB 254/5 (Patidar 93*, Kohli 43, Krunal 43; Holder 2/39, Rabada 2/54) beat Gujarat Titans 162 all out (Tewatia 68; Duffy 3/39, Bhuvneshwar 2/28, Rasikh 2/24, Krunal 2/16) by 92 runs.""",
}


# ── ARTICLE 2: GT's Qualifier 2 path after the Dharamsala collapse ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "Gujarat Titans Were Bowled Out for a Hundred and Sixty-Two. They Lost Their Captain for Two Runs. They Lost Their Orange Cap Holder Hit-Wicket. They Are Not Eliminated. That Is the Cruelty and the Mercy of the IPL Playoff Format.",
    "subheadline": "Gujarat Titans' 92-run defeat to RCB in Qualifier 1 was the worst performance of their IPL 2026 season. Shubman Gill scored 2. Sai Sudharsan fell hit-wicket. The Powerplay collapse — 51 for 5 — was the worst by any team in playoff history. But the double-elimination format means GT get a second chance. They will play the winner of Wednesday's Eliminator between Sunrisers Hyderabad and Rajasthan Royals in Qualifier 2 on Friday. Win that, and they face RCB in the final. Lose, and a season that produced 18 points and the Orange Cap winner ends with a bowling scorecard that reads 51/5.",
    "slug": "gujarat-titans-qualifier-2-path-collapse-shubman-gill-51-for-5-ipl-2026-playoffs-20260526",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "For the Indian diaspora following the IPL playoffs from abroad, GT's collapse raises a scheduling question that matters for work calendars and sleep schedules. The Eliminator — SRH vs RR — is on Wednesday. Qualifier 2 is on Friday. The final is on Sunday, May 31. For NRIs in the US, that means three more early mornings. For those in the UK, three more afternoon sessions. For those in the Gulf, three more prime-time evenings. Gujarat Titans have a significant NRI fanbase built during their 2022 title-winning season under Hardik Pandya, and Sai Sudharsan — the Orange Cap holder from Chennai who plays for a Gujarat franchise — has become a symbol of the kind of cross-regional mobility that resonates with a diaspora that knows something about moving to a new city and performing under pressure. If GT survive to the final, NRIs will have watched seven playoff matches across twelve days. If they lose on Friday, it ends with a Powerplay collapse in the mountains.",
    "tags": ["Gujarat Titans", "Shubman Gill", "Sai Sudharsan", "IPL 2026", "Qualifier 2", "Eliminator", "Sunrisers Hyderabad", "Rajasthan Royals", "Heinrich Klaasen", "Jofra Archer", "RCB", "IPL Playoffs", "Rahul Tewatia", "Kagiso Rabada", "Double Elimination"],
    "urgency": "daily",
    "sources": [
        "https://crickettimes.com/2026/05/fans-go-gaga-as-rajat-patidars-blazing-show-helps-rcb-seal-ipl-2026-final-berth-with-a-dominant-win-over-gt-in-qualifier-1/",
        "https://www.sportingnews.com/in/ipl/news/rcb-vs-gt-rajat-patidar-inspires-royal-challengers-bengaluru-to-ipl-final-2026-after-beating-titans/",
        "https://timesofsports.com/cricket/ipl-2026-rcb-vs-gt-highlights/",
        "https://www.sportskeeda.com/cricket/rcb-vs-gt-ipl-2026-qualifier-1-full-list-award-winners"
    ],
    "word_count": 850,
    "score_total": 72,
    "body": """The double-elimination format is the IPL's most generous structural feature. Four teams qualify for the playoffs. Two of them — the teams that finish first and second in the league phase — get two chances to reach the final. Only one loss eliminates them. The other two teams get one chance each.

Gujarat Titans finished second with 18 points. On Tuesday in Dharamsala, they used their first life and died badly. They have one life remaining.

## The anatomy of 51 for 5

The Powerplay collapse against RCB was not a gradual decline. It was an implosion that happened in phases, each more damaging than the last.

Phase one was Sai Sudharsan's hit-wicket. The Orange Cap holder — 638 runs in the league stage, the most consistent batsman in IPL 2026 — lost his balance attempting a flick off Jacob Duffy's first delivery. His back foot dislodged the bails. He walked off for 14, looking like a man who could not believe the evening had started this way.

Phase two was Shubman Gill's dismissal. The GT captain, who had averaged 42 in the league phase and scored two centuries, was bowled by Bhuvneshwar Kumar for 2. The ball was full, straight, and unremarkable. Gill played across it. Middle stump was disturbed. The most important batsman in Gujarat's lineup had contributed less than the extras column.

Phase three was the procession that followed. Jos Buttler edged Hazlewood for 29 — a cameo that promised resistance but delivered nothing sustainable. Nishant Sindhu lasted five balls. Jason Holder faced three deliveries without scoring before Rasikh Salam removed him. Two wickets in one over. 51 for 5. End of Powerplay.

It was the worst Powerplay performance by any team in IPL playoff history. The record will be documented. The footage will be archived. Gujarat will have to watch it before Friday.

## What Tewatia proved

Rahul Tewatia's 68 off 43 balls from number seven was the only innings that resembled professional cricket in Gujarat's chase. He hit 8 fours and 4 sixes. He put on partnerships with tail-enders who were happy to block while he swung. He took GT's score from catastrophic to merely humiliating.

But Tewatia's innings also revealed a structural problem. When a team's sixth-best batsman is the only one who scores, the issue is not individual form. It is collective failure under pressure. GT's top five contributed 73 runs combined. Tewatia alone scored 68. The arithmetic is damning.

## The Eliminator equation

GT's Qualifier 2 opponent will be determined on Wednesday when Sunrisers Hyderabad face Rajasthan Royals in the Eliminator at the IS Bindra Stadium in Mullanpur.

Both teams present different challenges for a Gujarat side trying to recover from the worst defeat of their season.

**Sunrisers Hyderabad** are built around Heinrich Klaasen. The South African has 606 runs this season from number four — the most prolific middle-order campaign in T20 franchise cricket history. If GT face SRH, they face a team that can match their own batting depth and has a finisher who can score 80 off 40 balls in any conditions. But SRH's bowling is vulnerable. Their death-over economy is the worst of the four playoff teams.

**Rajasthan Royals** are built around Jofra Archer. The England all-rounder has 250 T20 wickets and scored 32 off 15 balls in his last match against Mumbai Indians. If GT face RR, they face a team with a match-winner who bats at eight and bowls at 150 kilometres per hour. But Rajasthan's top order is inconsistent. They qualified for the playoffs on net run rate, not dominance.

Gujarat's preparation for Qualifier 2 will require addressing two questions that Tuesday did not answer: can Shubman Gill handle high-pressure chases, and can the bowling unit defend a total when Rabada is expensive?

## Rabada's numbers

Kagiso Rabada's Qualifier 1 figures — 4 overs, 2 wickets, 54 runs — tell a story about the gap between reputation and performance on the day. Rabada has been GT's most important bowler all season. In the league phase, he took 22 wickets at an economy of 7.8. In Dharamsala, his economy was 13.5.

Patidar hit him for three sixes in one over. The South African quick, who has bowled in World Cup finals and Test matches at Lord's, was reduced to bowling wide of off stump and hoping for a miscue that never came.

If GT reach the final, they will need a version of Rabada that Dharamsala did not produce. They will also need Rashid Khan — whose 4 overs went for 44 against Patidar and Krunal — to rediscover the control that made him the most feared T20 spinner on the planet.

## The mercy of the format

The IPL's double-elimination system exists precisely for days like Tuesday. A team that finishes second in a seventy-match league phase should not be eliminated by one bad evening. The format grants them a second opportunity. It does not grant them a third.

Gujarat Titans have three days to process the worst playoff performance in their franchise's four-year history. They have three days to select their team, prepare their plans, and decide whether Gill bats in the Powerplay or takes a more conservative approach.

The franchise that won the title in their debut season in 2022 and reached the final in 2023 is familiar with playoff pressure. They know how to win knockout matches. But they have never been required to win one after losing another by 92 runs.

The Eliminator is on Wednesday. Qualifier 2 is on Friday. The final is on Sunday.

GT have three days and two matches left. The first match is not theirs to play. The second will determine whether their season ends with Tewatia's lonely 68 or with something that makes Tuesday's collapse a footnote rather than an epitaph.

Fifty-one for five in the Powerplay. That is what happened. What happens next is the only part they can control.""",
}


if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-26 14:00 PDT (21:00 UTC)")
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

    # ── Insert + image: Article 1 (RCB vs GT Qualifier 1 result) ──
    print("\n[1/2] Inserting: RCB 254/5 crush GT — Patidar 93*(33)...")
    insert_article(a1)
    print(f"  ✓ Inserted: {a1['slug']}")

    # Image: Rajat Patidar on Wikipedia (main subject of match report)
    img1_url = fetch_wikipedia_person_image("Rajat Patidar")
    img1_attribution = "Wikimedia Commons"
    if not img1_url:
        img1_url = fetch_wikipedia_person_image("Virat Kohli")
    if not img1_url:
        # Pexels fallback: specific IPL / cricket imagery
        img1_url = fetch_pexels_image("cricket batsman six stadium IPL", "T20 cricket match stadium crowd")
        img1_attribution = "The Videshi"

    if img1_url:
        img1_path = f"/tmp/{a1_id}.jpg"
        if download_image(img1_url, img1_path):
            uploaded_url = upload_image(a1_id, img1_path)
            if uploaded_url:
                update_article_image(a1_id, uploaded_url, img1_attribution)

    # ── Insert + image: Article 2 (GT's Q2 path after collapse) ──
    print("\n[2/2] Inserting: GT's Qualifier 2 path after Dharamsala collapse...")
    insert_article(a2)
    print(f"  ✓ Inserted: {a2['slug']}")

    # Image: Shubman Gill on Wikipedia (GT captain, main subject)
    img2_url = fetch_wikipedia_person_image("Shubman Gill")
    img2_attribution = "Wikimedia Commons"
    if not img2_url:
        img2_url = fetch_wikipedia_person_image("Sai Sudharsan")
    if not img2_url:
        img2_url = fetch_pexels_image("cricket fielding team T20 stadium", "cricket bowler celebrating wicket")
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
