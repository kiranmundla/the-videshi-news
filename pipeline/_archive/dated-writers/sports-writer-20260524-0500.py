#!/usr/bin/env python3
"""Sports writer — 2026-05-24 05:00 PDT run: 2 articles + score decay."""

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

# ── ARTICLE 1: Prabhsimran Singh — First Uncapped Indian With 500+ Runs in Two IPL Seasons ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "He Has Never Worn an India Cap. He Has 541 Runs This Season, 549 Last Season, and a Record No Uncapped Indian Has Ever Held.",
    "subheadline": "Prabhsimran Singh scored 69 off 39 balls on Saturday in Lucknow to become the first uncapped Indian player to aggregate 500-plus runs in two separate IPL seasons. He opens the batting, keeps wicket, hits at a strike rate above 167, and has been doing this for Punjab Kings since he was 19 years old. India's selectors have watched every innings. They have not called.",
    "slug": "prabhsimran-singh-first-uncapped-indian-500-runs-two-ipl-seasons-punjab-kings-2026-20260524",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Prabhsimran Singh's story is a mirror for every Indian-origin professional abroad who has watched the meritocracy question play out in their own career. In India's cricket system, the IPL is supposed to be the great equaliser — performance in a transparent, televised, statistically dense tournament should lead to international recognition. Prabhsimran has now produced two seasons of elite output and remains uncapped, raising the same question NRI families debate at dinner tables: does the Indian system reward performance or pedigree? For diaspora cricket fans who follow the IPL from living rooms in New Jersey, Houston, and London, Prabhsimran is the archetype of the player they root for — the one doing everything right in public and still waiting for the phone to ring. His partnership with Priyansh Arya, another uncapped batter, at the top of the PBKS order this season has been one of the IPL's most electric opening acts, yet neither has an India cap. The IPL's promise to NRI fans has always been that it democratises Indian cricket. Prabhsimran's record tests whether that promise holds.",
    "tags": ["Prabhsimran Singh", "Punjab Kings", "IPL 2026", "Uncapped Indian", "Cricket Records", "Shreyas Iyer", "Priyansh Arya", "Indian Cricket", "BCCI Selectors", "Wicketkeeper Batter"],
    "urgency": "daily",
    "sources": [
        "https://mykhel.com/cricket/prabhsimran-singh-scripts-ipl-history-first-uncapped-indian-to-create-stellar-record.html",
        "https://crictracker.com/cricket-stats/ipl-2026-lsg-vs-pbks-match-68-stats-review/",
        "https://cricbuzz.com/cricket-news/ipl-pulse-the-streak-ends-the-wait-begins",
        "https://iplt20.com/news/tata-ipl-2026-match-68-lsg-vs-pbks-match-report"
    ],
    "word_count": 750,
    "score_total": 65,
    "body": """On Saturday evening in Lucknow, with Punjab Kings two wickets down for 22 in the third over of a chase that would define their season, Prabhsimran Singh walked to the middle and played an innings that was simultaneously unsurprising and historic.

He scored 69 off 39 balls. Seven fours. Two sixes. He put on 140 for the third wicket with his captain Shreyas Iyer, who went on to score his first IPL century. Punjab chased down 197 with seven wickets in hand. They broke a six-match losing streak and kept their playoff hopes alive.

None of that was the headline. The headline was a line in the post-match stats sheet: Prabhsimran Singh became the first uncapped Indian player to score 500-plus runs in two separate IPL seasons.

## What the numbers say

In 2025, Prabhsimran scored 549 runs for Punjab Kings. He struck at over 155, played 14 matches, and finished as one of the most consistent openers in the tournament. India's selectors did not pick him.

In 2026, through 14 matches and Saturday's knock in Lucknow, he has 541 runs at a strike rate above 167. He has been one half of the most dangerous opening partnership in the IPL alongside Priyansh Arya, who is also uncapped. In their first seven innings together this season, the pair accumulated 323 runs at an average of 53.83 and a combined strike rate of 248.46, including two fifty-plus stands and a century partnership.

India's selectors have watched. They have not called.

## The uncapped question

The "uncapped" label in Indian cricket carries a specific weight that outsiders rarely understand. India produces more professional cricketers than any country on earth. The pathway from domestic cricket to the IPL is brutally competitive. The pathway from IPL excellence to an India cap is even more so.

Prabhsimran is 24 years old. He has played 62 IPL matches and scored 1,729 runs at an average of 28.82 and a career strike rate of 156. He keeps wicket. He opens the batting. He scored his maiden IPL century — 103 against Delhi Capitals — in the 2023 season, when he was 21. He has three Player of the Match awards.

The only other uncapped player to reach the 500-run mark for Punjab in a single season was Shaun Marsh, who is Australian and was therefore always going to be uncapped for India. Prabhsimran is the first Indian to do it. And he has done it twice.

The conversation around his non-selection is not new. After the 2025 season, when he finished with 549 runs, the question of why he had not been picked for at least one of India's bilateral T20I series was raised by commentators, former players, and thousands of fans on social media. The BCCI's selection committee, led by Ajit Agarkar, has historically favoured players who perform in domestic first-class cricket and who fit specific tactical profiles. Prabhsimran's domestic record is solid but not spectacular. His IPL record is.

The tension between these two pathways — domestic grind versus IPL spectacle — is one of the defining debates in Indian cricket, and Prabhsimran sits directly at its centre.

## What Saturday's innings meant

Punjab Kings entered the Lucknow match on a six-game losing streak. They had slipped from third in the table to the edge of elimination. Their captain, Shreyas Iyer, had been under scrutiny for his own lean run.

What happened next was a masterclass in pressure batting. When Prabhsimran came in at 22 for 2, the required rate was already climbing. He attacked immediately. He took down the Lucknow spinners, finding the boundary seven times through conventional strokes before launching two sixes that settled the contest. His partnership with Iyer — 140 runs for the third wicket — turned a potential collapse into a controlled chase.

Iyer, who went on to score 101 not out off 57 balls for his first IPL hundred, later credited Prabhsimran for shifting the momentum. "He came in and just played his game. No panic. That's what he does — he doesn't change for the situation, the situation changes because of him."

The victory, achieved with two overs to spare, pulled Punjab Kings to 15 points and kept them alive in the playoff race.

## The bigger pattern

Prabhsimran is not an anomaly. He is part of a broader pattern in Indian cricket where the IPL increasingly produces players whose statistics demand international recognition but whose selection is delayed or denied by factors that are harder to quantify: domestic pedigree, positional competition, timing, and the sheer depth of Indian batting talent.

Riyan Parag waited years between his IPL debut and his India call-up. Tilak Varma was similarly patient. Abhishek Sharma, another PBKS-adjacent talent, had to produce multiple IPL seasons of dominance before the selectors took notice.

The difference with Prabhsimran is the keeper-batter dimension. India's wicketkeeper hierarchy has been congested for years — Rishabh Pant, KL Rahul, Ishan Kishan, Sanju Samson, and Dhruv Jurel have all occupied slots at various points. Adding another keeper-batter to the conversation requires not just runs but timing, and the timing has never aligned for Prabhsimran.

Yet the record now stands on paper, uncomplicated by context: no uncapped Indian has ever done what he has done across two IPL seasons. Whether that record becomes an India debut or a footnote depends on decisions made in rooms where the numbers alone do not always decide.""",
}

# ── ARTICLE 2: FIFA World Cup Squads — The World Picks 26 Names. India Picks a Viewing Schedule. ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "England Just Dropped Phil Foden From Their World Cup Squad. Brazil Brought Back Neymar. India — 1.4 Billion People — Is Choosing Which Pub to Watch From.",
    "subheadline": "The FIFA World Cup starts in 18 days across 16 cities in the United States, Canada, and Mexico. Forty-eight nations have named or are naming their squads. India, the world's most populous country and the home of the largest sports market on earth, is not among them. For the Indian diaspora in the host countries, the tournament will happen in their cities, in their stadiums, on their streets — and without their flag.",
    "slug": "fifa-world-cup-2026-squads-india-absent-diaspora-nri-england-brazil-foden-neymar-20260524",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "This story is written for the diaspora. The FIFA World Cup 2026 will be played in MetLife Stadium in New Jersey (home to one of America's largest Indian communities), at AT&T Stadium in Dallas (booming Indian tech population), at SoFi in Los Angeles (Bollywood-meets-Hollywood Indian corridor), and in cities from Toronto to Houston to Miami where Indian-Americans, Indian-Canadians, and Indian-Brits form some of the fastest-growing demographic groups. NRIs in the US will walk past FIFA Fan Zones on their commute. They will be asked by colleagues which team they support. They will watch the tournament in sports bars surrounded by fans in national jerseys — Mexican, American, English, Brazilian — and have no jersey of their own to wear. Meanwhile, India has just agreed to pay $30-35 million for broadcast rights to a tournament its team did not qualify for. The diaspora's relationship with the World Cup is an annual reminder of the gap between India's cricket infrastructure and its football neglect: a country that can fill 130,000 seats for an IPL final cannot produce a men's football team capable of competing in Asia's qualifying rounds. For NRI parents who enrolled their children in youth soccer leagues in Texas and New Jersey and California — leagues where Indian-origin kids now outnumber several other demographics — the absence stings differently. Their children play the sport. Their country does not.",
    "tags": ["FIFA World Cup 2026", "India Football", "NRI Diaspora", "England Squad", "Phil Foden", "Neymar", "Brazil", "Thomas Tuchel", "Indian Football", "AIFF", "MetLife Stadium", "World Cup USA"],
    "urgency": "daily",
    "sources": [
        "https://khelnow.com/football/thomas-tuchel-names-england-fifa-world-cup-2026-squad",
        "https://livemint.com/sports/england-fifa-world-cup-2026-squad-thomas-tuchel-names-final-26-man-list",
        "https://livemint.com/sports/where-to-watch-fifa-world-cup-2026-in-india-shaji-prabhakaran-big-update",
        "https://new7tv.com/fifa-set-to-strike-world-cup-2026-broadcasting-deal-with-india-worth-usd-30-35-million"
    ],
    "word_count": 780,
    "score_total": 62,
    "body": """On Friday, Thomas Tuchel stood in front of a camera and read out 26 names. They were the players who will represent England at the 2026 FIFA World Cup. Harry Kane. Jude Bellingham. Bukayo Saka. Declan Rice. Marcus Rashford, back from Barcelona. Cole Palmer and Phil Foden — two of the most talented attacking players in the Premier League — were left out.

The squad announcement crashed the England football app. Millions tried to log on simultaneously. Phone-ins erupted. Every pundit in Britain had an opinion about whether Tuchel had lost his mind or found it.

In Brazil, Carlo Ancelotti had already named his 26. Neymar, at 34, was included — a comeback narrative that has consumed South American football for months. Vinícius Jr., Rodrygo, Estêvão. The squad read like a greatest-hits album with a few debut tracks.

South Africa named 32 for a preliminary camp. Canada announced its pre-tournament training squad in Charlotte. Ghana's coach submitted his provisional list to FIFA.

Across the world, countries are making the most consequential selection decisions in their sporting calendars. Squad announcements are national events. Entire media cycles are built around who is in and who is out.

India's squad announcement is not coming. It was never going to.

## The arithmetic of absence

India is ranked 126th in the FIFA men's world rankings. The Blue Tigers were eliminated in the second round of Asian World Cup qualifying in June 2024, losing to Qatar and Afghanistan in a group where they needed to finish in the top two. They did not come close.

The 2026 World Cup is the first to feature 48 teams, expanded from 32. Asia received 8.5 qualifying slots — the most in the confederation's history. Japan, South Korea, Australia, Iran, Saudi Arabia, Iraq, Uzbekistan, Qatar, and Indonesia are the nine Asian teams that will be in the United States, Canada, and Mexico next month. India could not finish in the top half of a preliminary group.

This is not a new failure. India has qualified for the FIFA World Cup exactly once, in 1950, and withdrew before playing. In 75 years since, the country that has built the world's richest cricket league, that fills Narendra Modi Stadium's 132,000 seats for an IPL final, that produces elite athletes in cricket, badminton, wrestling, and shooting, has never played a World Cup match.

## The diaspora paradox

The paradox lands hardest on the diaspora. The World Cup will be played in their neighbourhoods.

MetLife Stadium in East Rutherford, New Jersey — 20 minutes from Edison, home to one of the largest Indian-American populations in the United States — will host group matches and a semifinal. AT&T Stadium in Dallas serves a metro area with over 200,000 Indian-origin residents. SoFi Stadium in Los Angeles, NRG Stadium in Houston, Hard Rock Stadium in Miami — every major host venue sits in a city where the Indian diaspora is a significant and growing community.

In Canada, BMO Field and BC Place will host matches in Toronto and Vancouver, two cities where Indo-Canadians are among the largest visible minority groups. In the UK, where millions of British Indians follow football as closely as cricket, the tournament will dominate every pub, office, and school playground for a month.

NRI families in these cities will experience the World Cup at close range. They will walk past FIFA Fan Zones. They will be asked by colleagues and neighbours which team they are supporting. They will watch from sports bars surrounded by fans draped in the colours of Mexico, the United States, England, and Brazil.

They will not have a jersey of their own.

## The broadcast bill

India has agreed to pay an estimated $30-35 million for the broadcast rights to a tournament its team did not qualify for. The Delhi High Court sought assurances that the World Cup would be accessible on free-to-air platforms including Doordarshan and DD Sports. Former AIFF General Secretary Shaji Prabhakaran confirmed this week that the deal is finalised and an official announcement is expected imminently.

The market logic is straightforward. India's football viewership has grown significantly over the past decade, driven by the Premier League, La Liga, and the Champions League. The 2022 World Cup final between Argentina and France drew an estimated 100 million Indian viewers. FIFA knows the audience exists. The audience simply does not have a team to follow.

## The youth soccer question

For diaspora families, the disconnect extends beyond television. Indian-origin children in the United States are among the fastest-growing demographics in youth soccer. Travel leagues in New Jersey, Texas, California, and the DMV are filled with Indian-American kids who play competitive football at a level that their parents' country cannot match at the national stage.

These children watch the Premier League. They wear Kane shirts and Bellingham shirts and Mbappé shirts. When the World Cup comes to their home stadiums this June, some will attend matches. None will see India play.

The question this raises is not new, but the proximity makes it sharper: why has a country with 1.4 billion people and a $30-35 million broadcast cheque not produced a football infrastructure capable of qualifying for a 48-team tournament?

The AIFF's governance crisis — 13 ISL clubs threatened to walk away from the federation just last week — provides part of the answer. The rest lies in decades of underfunding, administrative dysfunction, and a sporting culture that channels its best athletes and its best money toward cricket.

The World Cup starts on June 11. Forty-eight teams will march. India will watch. In the host countries, the diaspora will be close enough to hear the anthems — and far enough from having one of their own to sing.""",
}

if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-24 05:00 PDT")
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

    print("\nInserting Article 1: Prabhsimran Singh — Uncapped 500+ Record...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    # Try image for Article 1
    img1_path = f"/tmp/{a1_id}.jpg"
    if fetch_image("cricket batsman celebrating stadium IPL", img1_path):
        img1_url = upload_image(a1_id, img1_path)
        if img1_url:
            update_image_url(a1_id, img1_url)

    print("\nInserting Article 2: FIFA World Cup Squads — India Absent...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    # Try image for Article 2
    img2_path = f"/tmp/{a2_id}.jpg"
    if fetch_image("FIFA World Cup stadium football fans flags", img2_path):
        img2_url = upload_image(a2_id, img2_path)
        if img2_url:
            update_image_url(a2_id, img2_url)

    # Score decay
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    print(f"\nDone. 2 articles published.")
    print(f"  IDs: {a1_id}, {a2_id}")
