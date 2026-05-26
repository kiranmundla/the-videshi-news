#!/usr/bin/env python3
"""Sports writer — 2026-05-26 09:00 UTC (02:00 PDT May 26): 2 articles + score decay.

Article 1: Federation Cup 2026 — India's athletics revolution in Ranchi (3 national records in 48 hours)
Article 2: Gukesh vs Sindarov — World Championship 2026 bidding deadline in 5 days
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
            f"{person_name} (athlete)",
            f"{person_name} (sprinter)",
            f"{person_name} (chess player)",
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


# ── ARTICLE 1: Federation Cup 2026 — India's Athletics Revolution in Ranchi ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Three National Records in Forty-Eight Hours. The Fastest Indian Man Ever. The First Indian to Cross 8,000 Decathlon Points. None of Them Are Neeraj Chopra.",
    "subheadline": "The Federation Cup 2026 in Ranchi produced the most extraordinary weekend in Indian athletics history. Gurindervir Singh ran 10.09 seconds in the men's 100 metres — faster than any Indian has ever run — to qualify for the Commonwealth Games. Vishal TK ran 44.98 seconds in the men's 400 metres — India's first-ever sub-45 — and missed Commonwealth Games qualification by two hundredths of a second. Tejaswin Shankar scored 8,057 points in the decathlon — the first Indian ever to cross the 8,000-point barrier — breaking the national record and qualifying for Glasgow. The country's most famous track and field athlete, Olympic champion Neeraj Chopra, was not there. He is in Switzerland, rehabilitating a back injury. India's athletics revolution happened without him. The Commonwealth Games are in Glasgow from July 23 to August 2. For the Indian diaspora in Britain, these athletes are about to become household names.",
    "slug": "federation-cup-2026-ranchi-gurindervir-singh-vishal-tk-tejaswin-shankar-national-records-cwg-glasgow-20260526",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "The Commonwealth Games 2026 will be held in Glasgow from July 23 to August 2. For the 800,000 people of Indian origin in Scotland and England, this is the one major global multi-sport event they can attend in person without booking flights to India, Tokyo, or Paris. When Gurindervir Singh lines up in the 100-metre final at Hampden Park, the Indian sections of the crowd in Glasgow will include families from Edinburgh, Leicester, Birmingham, and Southall who have never had the opportunity to watch an Indian sprinter live. When Tejaswin Shankar competes in the decathlon, the same audience will see an Indian athlete competing in the most demanding event in athletics — an event that India has never previously been competitive in at the Commonwealth level. The practical significance for British Indians is that tickets for athletics at Glasgow 2026 are available now, the venues are accessible by public transport, and India is sending athletes who are genuinely capable of winning medals. The emotional significance is deeper: Indian athletics is no longer Neeraj Chopra and nothing else. The Federation Cup in Ranchi just proved it. Glasgow will be where the diaspora sees it for themselves.",
    "tags": ["Gurindervir Singh", "Vishal TK", "Tejaswin Shankar", "Federation Cup 2026", "Ranchi", "Commonwealth Games 2026", "Glasgow", "Neeraj Chopra", "Indian Athletics", "100m", "400m", "Decathlon", "National Record", "Birsa Munda Stadium", "Animesh Kujur", "Praveen Chithravel"],
    "urgency": "daily",
    "sources": [
        "https://www.mykhel.com/more-sports/federation-cup-2026-live-updates-cwg-qualification-race-begins-in-ranchi-434529.html",
        "https://www.mykhel.com/more-sports/gurindervir-singh-smashes-100m-national-record-with-historic-10-09s-sprint-at-federation-cup-2026-qualifies-for-cwg-2026-434552.html",
        "https://revsportz.in/animesh-tejaswin-sreeshankar-and-sachin-headline-federation-cup-as-commonwealth-games-spots-go-on-the-line/",
        "https://femaleinsports.com/nikhat-zareen-losses-51kg-trial/"
    ],
    "word_count": 920,
    "score_total": 72,
    "body": """Birsa Munda Stadium in Ranchi does not look like a place where history gets made. It is a concrete oval in Morabadi, surrounded by the kind of institutional greenery that Indian municipal athletics facilities share nationwide. The running surface is adequate. The seating is functional. The facilities exist to serve, not to impress.

Over four days last week, the Federation Cup 2026 turned that adequate facility into the most important venue in Indian athletics history.

## The fastest Indian who ever lived

Gurindervir Singh arrived in Ranchi holding the men's 100-metre national record. He left Ranchi having broken it — again.

On Day 1, Animesh Kujur ran 10.15 seconds in the semi-final, snatching the national record from Gurindervir. The record lasted less than twenty-four hours.

On Day 2, in the final, Gurindervir exploded from the blocks and crossed the line in 10.09 seconds. His bib read: "Task Is Not Finished Yet."

The number itself is significant. 10.09 seconds is faster than any Indian man has ever run over 100 metres. It breaches the Commonwealth Games qualification standard of 10.16 seconds with room to spare. It places Gurindervir in a category that Indian sprinters have historically not occupied — the category of athletes who can compete in a major international 100-metre final and not be eliminated before the race begins.

Animesh Kujur finished second in 10.20 seconds. Pranav Pramod took bronze in 10.29 seconds. The entire top three broke 10.30 seconds in a domestic event. This has never happened in Indian athletics before.

## India's first sub-45

If Gurindervir's 10.09 was the loudest moment in Ranchi, Vishal TK's 44.98 seconds in the men's 400 metres was the most heartbreaking.

The Tamil Nadu runner produced the race of his life. He ran a negative split — the kind of sophisticated race execution that requires both talent and tactical maturity — and crossed the line in 44.98 seconds.

It was a national record. It was India's first-ever sub-45-second 400 metres. It was the performance that every Indian quarter-miler for the last three decades has chased.

It was also 0.02 seconds too slow.

The Commonwealth Games qualification standard for the men's 400 metres is 44.96 seconds. Vishal missed it by two hundredths of a second — the time it takes to blink half a blink. In athletics terms, it is the margin between Glasgow and home.

Rajesh Ramesh (45.31 seconds) and Jay Kumar (45.47 seconds) completed a podium where all three men ran sub-46. The depth is real.

## 8,057 points

Then there was Tejaswin Shankar.

The 2022 Commonwealth Games high jump bronze medallist arrived in Ranchi with a specific target: 8,000 points in the decathlon. No Indian man had ever reached that number. The decathlon — ten events across two days, testing every conceivable athletic attribute — is the most demanding competition in track and field. It rewards the complete athlete. India has never had one who could score 8,000 points.

Tejaswin's two days in Ranchi read like a list designed to make the point as emphatically as possible:

100m — 10.77 seconds (personal best). Long jump — 7.67 metres (personal best). Shot put — 13.31 metres. High jump — 2.25 metres. 400m — 49.34 seconds. 110m hurdles — 14.23 seconds. Discus throw — 37.90 metres. Pole vault — 4.20 metres. Javelin throw — 47.71 metres. 1500m — 4:29.02.

Total: 8,057 points.

The 2.25-metre high jump clearance alone is a mark achieved by only a handful of decathletes globally. Combined with a 10.77-second 100 metres and a 7.67-metre long jump, Tejaswin demonstrated the kind of multi-event excellence that India has simply never produced before.

He qualified for the Commonwealth Games. He broke the national record. He crossed 8,000 points. He did all three in the same competition.

## Where was Neeraj?

The question is inevitable. Neeraj Chopra — Olympic champion, the most famous Indian athlete of his generation, the man who made an entire country care about track and field — was not in Ranchi.

He is in Switzerland. The back injury that has troubled him intermittently since 2023 required another period of rehabilitation. He is working toward fitness for the Diamond League season and, eventually, the Commonwealth Games. But he was not at the Federation Cup, and his absence was conspicuous.

The significance of what happened in Ranchi is inseparable from that absence. India's three national records — in the 100 metres, the 400 metres, and the decathlon — were set while the country's biggest athletic star was in a Swiss clinic. The revolution was not about Neeraj. It happened alongside him, around him, independent of him.

Praveen Chithravel cleared 17.08 metres in the triple jump, qualifying for the Commonwealth Games. Baranica Elangovan, the women's pole vault national record holder, competed in Ranchi carrying form from her 4.22-metre clearance at the National Indoor Championships earlier this year.

The depth chart is no longer a single name.

## Glasgow is in Britain

The Commonwealth Games 2026 will be held in Glasgow from July 23 to August 2. The athletics events will take place at Hampden Park — the national football stadium, converted for track and field.

Glasgow is in Scotland. It is accessible by train from London, Birmingham, Leicester, Edinburgh, and every other city with a significant Indian diaspora population. It is not a fifteen-hour flight away. It is not behind a visa application. For the 1.8 million people of Indian origin in the United Kingdom, it is a day trip or an overnight stay.

The Athletics Federation of India is capped at sending 16 men and 16 women. The selection will be fierce. But Gurindervir Singh, Tejaswin Shankar, and Praveen Chithravel have already met their qualification standards. Others — including Vishal TK, who is 0.02 seconds away — will chase additional qualifying opportunities in the weeks ahead.

The Indian team that arrives in Glasgow will not be built around a single superstar. It will be built around depth — multiple athletes in multiple events who are capable of reaching finals and competing for medals.

## The number that matters

Three national records in forty-eight hours. At a domestic meet. In Ranchi. In May. With the country's most famous athlete on another continent.

Indian athletics has spent decades waiting for a generation that could compete beyond one event. The Federation Cup 2026 suggests that generation has arrived. Glasgow is two months away. The diaspora in Britain can buy their tickets.

Gurindervir Singh ran 10.09 seconds. His bib said: "Task Is Not Finished Yet."

He is correct.""",
}


# ── ARTICLE 2: Gukesh vs Sindarov — World Championship 2026 Bidding Deadline ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "Both Players Are Twenty Years Old. The Prize Fund Is Two and a Half Million Dollars. The Venue Bidding Closes on Saturday. Nobody Knows Where the Youngest World Chess Championship Match in History Will Be Played.",
    "subheadline": "FIDE opened bids for the 2026 World Chess Championship between defending champion D Gukesh and challenger Javokhir Sindarov. The match is scheduled from November 23 to December 17. The total budget is eight and a half million dollars. The prize fund is two and a half million. The bidding deadline is May 31 — five days from now. No city has been confirmed. Both players are twenty years old, making it the youngest World Championship match in the one hundred and forty year history of the game. Gukesh is currently playing Norway Chess 2026 in Oslo — his final classical test before defending his title. In Warsaw three weeks ago, Sindarov beat Gukesh in blitz. Gukesh beat him back in rapid. The rivalry is real and it has not yet found a home.",
    "slug": "gukesh-sindarov-world-chess-championship-2026-fide-bidding-venue-youngest-match-history-20260526",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "D Gukesh is from Chennai. He is nineteen years old and the reigning World Chess Champion — the youngest in the 140-year history of the game. His challenger, Javokhir Sindarov, is twenty years old and from Tashkent, Uzbekistan. For the Indian diaspora, Gukesh's title defence is one of the most significant Indian sporting events of 2026. If the match is held in a city with a significant Indian population — Singapore, Dubai, London — the diaspora will fill the venue. If it is held in Chennai, as many NRIs would prefer, it becomes a homecoming event of extraordinary emotional weight. But with the bidding deadline in five days, no city has been confirmed, and the diaspora's ability to plan travel, book hotels, and organise viewing events is dependent on FIDE's announcement. The $8.5 million budget requirement has narrowed the field of plausible host cities to perhaps a dozen worldwide. The venue will determine whether this becomes an event the Indian diaspora experiences in person or watches on a screen at 3 AM.",
    "tags": ["D Gukesh", "Javokhir Sindarov", "World Chess Championship 2026", "FIDE", "Chess", "Norway Chess", "Magnus Carlsen", "Chennai", "Venue Bidding", "India", "Uzbekistan", "Grand Chess Tour", "Warsaw"],
    "urgency": "daily",
    "sources": [
        "https://en.wikipedia.org/wiki/World_Chess_Championship_2026",
        "https://chessdom.com/gukesh-vs-sindarov-world-championship-match-2026-venue/",
        "https://gapim.uz/en/news/fide-opens-bidding-for-2026-world-chess-championship-gukesh-vs-sindarov",
        "https://sportsdigest.in/how-big-is-the-gukesh-vs-sindarov-world-championship-budget-fide-opens-bids/"
    ],
    "word_count": 880,
    "score_total": 68,
    "body": """Somewhere in the world, a city is putting together a bid to host the most consequential chess match of the decade. That city has five days left.

FIDE — the International Chess Federation — opened the bidding process for the 2026 World Chess Championship in early May. The match between defending champion D Gukesh and challenger Javokhir Sindarov is scheduled for November 23 to December 17. The total budget required from the host city is $8.5 million. The prize fund is $2.5 million. The deadline for proposals is May 31, 2026.

As of today, no host has been announced.

## The youngest match in history

The 2026 World Chess Championship will be the youngest title match ever played. Both players are twenty years old. Both achieved their status through tournament victories that stunned the chess world.

Gukesh became World Champion in December 2024 at the age of eighteen, defeating Ding Liren in Singapore in a match that ended with one of the most dramatic blunders in championship history. He became the youngest undisputed World Chess Champion, surpassing Garry Kasparov's record that had stood since 1985.

Sindarov qualified by winning the 2026 FIDE Candidates Tournament — the gruelling eight-player event that determines the challenger. The Uzbekistani grandmaster is the first player from Central Asia to earn the right to challenge for the world title. He won the 2025 Chess World Cup at nineteen, becoming the youngest World Cup winner in history.

Their combined age at the start of the match — forty — will be the lowest for any World Championship match since Wilhelm Steinitz and Johannes Zukertort played the first official championship in 1886.

## The budget

$8.5 million is a significant sum for a chess event. The requirement narrows the field of plausible host cities to major metropolitan areas with either sovereign wealth backing, corporate sponsorship capacity, or government sports investment.

Previous World Championship matches have been held in Singapore (2024), Astana (2023), Dubai (2021), and Chennai (2013). Each host provided the financial package through a combination of government funding and local corporate support.

The 2024 match in Singapore — where Gukesh won the title — was held at the Resorts World Sentosa with backing from the Singapore Tourism Board. The 2013 match in Chennai — the last time India hosted — was funded by the Tamil Nadu government and ONGC.

For 2026, the chess world's speculation centres on a handful of cities: Tashkent (Sindarov's home, and Uzbekistan has invested heavily in chess infrastructure), Singapore (which successfully hosted in 2024), Dubai (which has the financial capacity and recently hosted the FIDE World Rapid and Blitz), and Chennai (which would give Gukesh a home advantage and the Tamil Nadu government a global prestige event).

## The rivalry in Warsaw

Three weeks before the bidding deadline, Gukesh and Sindarov met at the Grand Chess Tour: Super Rapid and Blitz Poland 2026 in Warsaw. The encounter was the first significant preview of their championship dynamic.

In rapid — the format closest to classical chess in terms of strategic depth — Gukesh won. The defending champion's preparation was visible: he had studied Sindarov's recent games and exploited a specific weakness in the Uzbekistani's middlegame calculation. Gukesh celebrated with a fist pump that immediately went viral across Indian chess social media.

In blitz — the fastest, most chaotic format — Sindarov hit back. He outplayed Gukesh in a sharp tactical battle, demonstrating the speed of calculation that had carried him through the Candidates Tournament. After the win, Sindarov remained expressionless. The contrast in temperaments — Gukesh's visible emotion against Sindarov's composure — has become one of the defining narratives of the pre-match buildup.

The score between them is effectively level. Neither has established psychological dominance.

## Norway Chess: the final classical test

Gukesh is currently competing at Norway Chess 2026 in Oslo — a ten-round super-tournament that runs from May 25 to June 5. It is his final classical chess event before the World Championship match.

In Round 1, Gukesh survived a dramatic game against Vincent Keymer. He made an incorrect fifty-move draw claim during a time scramble — a procedural error that handed Keymer two extra minutes on the clock. Gukesh recovered, made a valid second claim, drew the classical game, and then won the Armageddon tiebreak.

The performance was characteristic: imperfect in execution, relentless in outcome. It is the quality that has defined Gukesh's career since he was fifteen — the ability to find a way to win from positions that should have been lost.

His most anticipated game at Norway Chess is against Magnus Carlsen, scheduled for May 28. Carlsen lost his Round 1 classical game to an injured Alireza Firouzja, and the five-time world champion's motivation for the tournament may have shifted. A Gukesh victory over Carlsen in classical chess would be a significant psychological statement before the championship match.

## The diaspora and the clock

For the Indian diaspora, the venue announcement is not an abstract concern. It determines whether this becomes an event they can attend.

If the match is held in Chennai, NRIs with family in Tamil Nadu can plan trips around the championship. If it is held in Singapore or Dubai, the large Indian communities in both cities can attend in person. If it is held in Tashkent, the practical barriers for Indian fans — visa requirements, flight connections, accommodation — become significant.

The diaspora's engagement with chess has transformed since Gukesh's championship victory in 2024. Chess.com reported a surge in Indian registrations after Singapore. Indian chess content on YouTube has grown into a category that rivals cricket analysis in engagement. The World Championship match is no longer a niche event followed by enthusiasts — it is a mainstream Indian sporting occasion.

Five days remain until the bidding closes. The match is six months away. Both players are twenty years old. The venue is unknown.

Somewhere, a city is writing a proposal. The city that wins the bid will host the youngest World Championship match in 140 years of chess. The $8.5 million question is which city it will be.""",
}


if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-26 09:00 UTC (02:00 PDT May 26)")
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

    # ── Insert + image: Article 1 (Federation Cup Athletics) ──
    print("\n[1/2] Inserting: Federation Cup 2026 — India's Athletics Revolution...")
    insert_article(a1)
    print(f"  ✓ Inserted: {a1['slug']}")

    # Image: Try Tejaswin Shankar (decathlon hero) on Wikipedia
    img1_url = fetch_wikipedia_person_image("Tejaswin Shankar")
    img1_attribution = "Wikimedia Commons"
    if not img1_url:
        img1_url = fetch_wikipedia_person_image("Gurindervir Singh")
    if not img1_url:
        img1_url = fetch_wikipedia_person_image("Neeraj Chopra")
    if not img1_url:
        # Pexels fallback: specific athletics imagery
        img1_url = fetch_pexels_image("sprinter running track finish line athletics", "athletics 100m race stadium")
        img1_attribution = "The Videshi"

    if img1_url:
        img1_path = f"/tmp/{a1_id}.jpg"
        if download_image(img1_url, img1_path):
            uploaded_url = upload_image(a1_id, img1_path)
            if uploaded_url:
                update_article_image(a1_id, uploaded_url, img1_attribution)

    # ── Insert + image: Article 2 (Gukesh vs Sindarov WC 2026) ──
    print("\n[2/2] Inserting: Gukesh vs Sindarov — World Championship 2026 Bidding...")
    insert_article(a2)
    print(f"  ✓ Inserted: {a2['slug']}")

    # Image: Gukesh on Wikipedia (main subject)
    img2_url = fetch_wikipedia_person_image("Gukesh Dommaraju")
    img2_attribution = "Wikimedia Commons"
    if not img2_url:
        img2_url = fetch_wikipedia_person_image("D. Gukesh")
    if not img2_url:
        img2_url = fetch_wikipedia_person_image("Javokhir Sindarov")
    if not img2_url:
        # Pexels fallback
        img2_url = fetch_pexels_image("chess grandmaster tournament classical game", "chess championship board pieces")
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
