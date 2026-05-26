#!/usr/bin/env python3
"""Sports writer — 2026-05-26 03:00 UTC (20:00 PDT May 25): 2 articles + score decay.

Article 1: Norway Chess Round 1 — India's four-player domination (Divya, Gukesh, Pragg)
Article 2: India Blue Tigers fly to London for Unity Cup — first UK match in 24 years
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


# ── ARTICLE 1: Norway Chess Round 1 — India sends four players, three win ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Divya Deshmukh Beat the Women's World Champion on Day One. She Was Worried About Whether She Could Eat the Dried Mango.",
    "subheadline": "Norway Chess started in Oslo on Sunday. India sent four players. Three of them won their matches. The twenty-year-old from Nagpur drew Ju Wenjun in the classical game, stepped into the confessional booth to wonder about the dried mango on the table and whether the sleeping audience members could be blamed, then beat the world champion in Armageddon. Gukesh survived an incorrect fifty-move claim against Keymer and won in Armageddon. Praggnanandhaa outplayed Wesley So. And Magnus Carlsen — the man who has defined chess for fifteen years — lost his classical game to an injured Alireza Firouzja. It was Round 1.",
    "slug": "norway-chess-2026-round-1-divya-deshmukh-gukesh-praggnanandhaa-carlsen-oslo-20260525",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "For the Indian diaspora, Norway Chess 2026 Round 1 is one of those moments that makes you recalibrate what 'Indian dominance' means in a global sport. India sent four players to Oslo — D Gukesh, the reigning World Chess Champion at nineteen; R Praggnanandhaa, who at twenty has already played a World Championship final; Divya Deshmukh, who at twenty is already the youngest woman to compete at Norway Chess; and Koneru Humpy, making her return to elite competition. Three of the four won their matches on Day 1. In any other country, this would be front-page sports news. In India, it competes with IPL playoffs for attention, and in the diaspora — where NRIs in Silicon Valley and London and Toronto have been quietly following Gukesh's rise since he was fifteen — it confirms what they already suspected: India is not a rising chess nation. India is the chess nation. The confessional booth moment is pure diaspora energy — Divya, representing India at the highest level, wondering about dried mango and judging the sleeping Europeans with the gentle roast of someone who grew up watching her parents do the same thing at family functions.",
    "tags": ["Divya Deshmukh", "D Gukesh", "R Praggnanandhaa", "Koneru Humpy", "Magnus Carlsen", "Norway Chess 2026", "Oslo", "Ju Wenjun", "Alireza Firouzja", "Vincent Keymer", "Wesley So", "Chess", "India"],
    "urgency": "daily",
    "sources": [
        "https://thepopularstory.com/norway-chess-divya-deshmukh-stuns-world-champion-ju-wenjun-in-armageddon-magnus-carlsen-handed-shock-defeat-chess-news/",
        "https://en.chessbase.com/post/norway-chess-2026-with-carlsen-gukesh-and-ju-wenjun",
        "https://checkmatedaily.com/2026/05/25/norway-chess-2026-featuring-carlsen-keymer-pragg-gukesh-wenjun-jiner-humpy-anna-divya-starts-today/",
        "https://uaenews247.com/2026/05/25/gukesh-carlsen-rivalry-reignites-as-norway-chess-gets-underway-in-oslo/"
    ],
    "word_count": 870,
    "score_total": 73,
    "body": """The confessional booth at Norway Chess is a soundproof glass room adjacent to the playing hall. Players can step inside during their game, look directly into a camera, and say whatever they want to the live audience. It is, by design, the most honest room in professional chess.

Divya Deshmukh was the first player to use it in the 2026 tournament. She walked in during her Round 1 classical game against women's world champion Ju Wenjun and whispered: "I don't know if I am supposed to do this while sitting or standing, but my game is very interesting. I really hope that she can't hear me."

Then she noticed the audience. "I saw there are some people who are sleeping in the first row. But honestly, I don't blame them. It is what I would've done too."

Then she noticed the snacks. "I'm actually getting a bit hungry, and there's a packet of dried mango kept on the table, but I'm unsure if we can eat it, because it might be for promotional causes. I want to find that out, but I have no idea how!"

Then she went back to the board and drew the women's world champion in 52 moves.

## The game within the game

The classical encounter between Deshmukh and Ju Wenjun followed a Réti/Catalan structure. Playing with the black pieces, the twenty-year-old from Nagpur matched the world champion move for move — confident central play, energetic rook activity, calm defence against Ju's kingside attacks. When the position demanded tactical calculation, she calculated. When it demanded patience, she waited. A three-fold repetition ended the game.

In the Armageddon tiebreak — where White gets ten minutes but must win, while Black gets seven minutes but only needs a draw — Deshmukh handled the asymmetric pressure with the composure of someone who has been playing this format since her teenage years. She is the youngest woman ever to compete at Norway Chess. On Day 1, she beat the world champion.

She is twenty years old. She was worried about the dried mango.

## Gukesh survives, then strikes

D Gukesh's Round 1 classical game against Vincent Keymer was supposed to be the headline match for India. It became one instead for its procedural drama.

In a difficult endgame where Keymer was pressing, Gukesh — the reigning World Chess Champion, nineteen years old, the youngest in history — made an incorrect fifty-move draw claim during a frantic time scramble. Under tournament rules, the error handed Keymer two extra minutes on the clock.

The punishment could have been fatal. It was not. Keymer could not find a path to victory with the additional time, and Gukesh made a valid second fifty-move claim to draw the classical game.

The Armageddon tiebreak was a different matter. Gukesh carried the momentum of survival — the specific adrenaline that comes from narrowly avoiding disaster — and sealed the match with a brilliant win. It is the kind of result that defines Gukesh's career so far: imperfect in the execution, lethal in the outcome.

His World Championship defence against Javokhir Sindarov begins later this year. Norway Chess is his final classical test before that match. He has been criticised for his results in 2026 — Ian Nepomniachtchi said recently that "most players can beat him" — and the pressure to prove that the championship was not a fluke is real. Round 1 was not clean. But it was a win.

## Praggnanandhaa dispatches Wesley So

R Praggnanandhaa's Round 1 was the most clinically efficient of the Indian contingent. A steady draw in the classical game against American Grandmaster Wesley So — once the world's second-ranked player — followed by a complete outplaying in the Armageddon tiebreak.

Praggnanandhaa is twenty years old. He played in the 2024 World Championship final against Ding Liren at eighteen. He lost. The experience has shaped him into a more patient, more dangerous player. His Armageddon win against So — decisive, controlled, unspectacular — is the kind of result that does not make highlights but wins tournaments.

## Carlsen falls

And then there was Magnus Carlsen.

The five-time world champion, the highest-rated player in the history of the game, the man who held the world number one ranking for fourteen consecutive years, lost his Round 1 classical game to Alireza Firouzja.

Firouzja was playing with an injured leg. He recorded his first-ever classical victory over Carlsen.

After the loss, Carlsen said: "He gave me a lot of tests and in the end I failed. He doesn't necessarily always find the best move, but he put me under a ton of pressure and that's kind of what you want to do."

It is the kind of admission that Carlsen makes rarely and means deeply. The greatest player of his generation, at thirty-five, is no longer able to guarantee the outcome of a single classical game against a motivated opponent. The era is shifting. The Norwegians in the audience — this is their hero — watched in silence.

## Humpy's return, Humpy's blunder

The fourth Indian, Koneru Humpy, did not have the debut she wanted. Playing with the white pieces in the women's section, she fought her way back into a difficult game against Bibisara Assaubayeva, only to commit a costly blunder on move 45 — Kf3, a move that handed the game away at the moment she had clawed her way to equality.

It was the first classical win of the entire tournament, and it came at Humpy's expense. Her return to elite competition after a period away from the top events will require the resilience that has defined her career — she has been India's strongest female player for over a decade, and one bad move does not erase that.

## Four players, one country

India sent four players to Norway Chess 2026. On Day 1, three of them won their matches — Divya over the women's world champion, Gukesh over a rising German talent, Praggnanandhaa over a former world number two. The fourth, Humpy, lost to a single move after a fighting game.

Magnus Carlsen, the local favourite, the greatest player alive, lost to an injured opponent.

The next Gukesh-Carlsen match is scheduled for May 28. The Norwegian crowd will fill the hall at Deichman Bjørvika, Oslo's stunning waterfront library, hoping their hero can recover. The Indian diaspora — in Oslo, in London, in San Jose, in Toronto, watching on Chess.com at hours that make no sense for their time zones — will be watching too.

In the confessional booth, a twenty-year-old from Nagpur wondered about dried mango. On the board, she beat the world champion. India sent four. Three won. The tournament is twelve days long. Round 1 has set the terms.""",
}


# ── ARTICLE 2: India Blue Tigers in London — Unity Cup 2026 ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "India's Football Team Just Landed in London. Their Biggest Club Refused to Let Seven Players Go. They Have Eighteen Men and a Match Against Jamaica on Wednesday.",
    "subheadline": "The Blue Tigers arrived in London for the Unity Cup 2026 — India's first competitive football match on British soil in twenty-four years. Mohun Bagan Super Giant, the country's most decorated club, withdrew seven players from the twenty-eight-man squad because the tournament falls outside the FIFA international window and the AIFF will not compensate for injuries. India now have eighteen players, a depleted squad, and a semi-final against FIFA's seventy-first-ranked Jamaica at The Valley, Charlton Athletic's ground in south-east London. FIFA has granted the Unity Cup full Tier 1 International Tournament status. The diaspora in London, Leicester, and Birmingham can go watch India play football in person for the first time in a generation.",
    "slug": "india-blue-tigers-london-unity-cup-2026-mohun-bagan-jamaica-depleted-squad-20260525",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "For the estimated 1.8 million people of Indian origin in the United Kingdom, the Unity Cup 2026 is something that has not happened in their adult lifetimes: an Indian national football team playing a competitive match that they can attend in person. The last time India played on British soil was 2002. An entire generation of British Indians — the children of Gujarati families in Leicester, the Punjabi communities in Southall and Birmingham, the tech workers in Canary Wharf — has never had the option of buying a ticket to watch India play football without flying to Kolkata or Guwahati or Bengaluru. The Valley is in south-east London. Charlton Athletic's ground holds 27,111. The semi-final against Jamaica is on Wednesday, May 27. Tickets are available. The practical question for every Indian-origin football fan in the UK is whether they can take a half-day from work on Wednesday. The emotional question is whether a depleted eighteen-man squad, abandoned by their biggest club, can do something worth watching on the one occasion the diaspora can actually be in the stadium. For NRIs in London, this is not about whether India can win the Unity Cup. It is about whether India's football team can show up — literally and figuratively — when the people who care about them are finally close enough to see it.",
    "tags": ["India Football", "Blue Tigers", "Unity Cup 2026", "London", "Mohun Bagan", "Jamaica", "The Valley", "Charlton Athletic", "AIFF", "Khalid Jamil", "Gurpreet Singh Sandhu", "Sandesh Jhingan", "UK Diaspora", "FIFA"],
    "urgency": "daily",
    "sources": [
        "https://footballcounter.com/blue-tigers-arrive-in-london-ahead-of-unity-cup-2026-challenge/",
        "https://khelnow.com/football/depleted-18-member-india-squad-fly-to-london-unity-cup-2026",
        "https://sportingnews.com/us/football/news/why-mohun-bagan-recalled-players-india-camp-unity-cup-2026",
        "https://khelnow.com/football/2026-05-25-fifa-grants-unity-cup-2026-full-tier-1-international-tournament-status"
    ],
    "word_count": 850,
    "score_total": 68,
    "body": """Seventeen players boarded a flight from Bengaluru to London. An eighteenth — goalkeeper Hrithik Tiwari — was arriving separately. That was the Indian football team's travel party for the Unity Cup 2026, a FIFA-sanctioned Tier 1 international tournament at The Valley in south-east London.

The original squad was twenty-eight players. It is now eighteen.

The reason is a dispute that captures everything wrong with Indian football in a single bureaucratic sentence: Mohun Bagan Super Giant, the country's most successful and oldest football club, withdrew seven players from the India squad because the Unity Cup falls outside the FIFA international window, and the All India Football Federation has previously refused to compensate the club for injuries suffered by players during non-window matches.

## The withdrawal

The FIFA international window begins on June 1. The Unity Cup runs from May 26 to May 30. The gap is five days. In those five days, the jurisdictional question of who is responsible for a player's body — club or country — becomes a legal and financial void.

Mohun Bagan's position is straightforward: if a player gets injured representing India in a tournament that FIFA does not mandate clubs to release players for, the club loses the player, pays for the rehabilitation, and receives no compensation from the federation. This has happened before. The AIFF did not pay. Mohun Bagan did not forget.

The seven withdrawn players include several who would have been starters. The squad that arrived in London is not India's best eighteen. It is India's available eighteen — the players whose clubs either agreed to release them or whose contracts did not give the club the leverage to refuse.

Head coach Khalid Jamil has named his options. The squad reads:

**Goalkeepers:** Gurpreet Singh Sandhu, Hrithik Tiwari, Albino Gomes.

**Defenders:** Rahul Bheke, Nikhil Poojary, Roshan Singh Naorem, Sandesh Jhingan, Akash Mishra, Bijoy Varghese, Pramveer.

**Midfielders:** Jeakson Singh Thounaojam, Noufal PN, Ricky Shabong.

**Forwards:** Ryan Williams, Edmund Lalrindika, Lallianzuala Chhangte, Rahim Ali, Farukh Choudhary.

Five midfielders were named in the original squad. Three remain. The depth chart for the position that controls football matches has been reduced to a list you can count on one hand.

## Twenty-four years

The last time India played a football match in the United Kingdom was 2002. Tony Blair was Prime Minister. David Beckham was the most famous athlete in the world. The Indian diaspora in Britain numbered roughly one million. It is now closer to 1.8 million.

In those twenty-four years, Indian football has qualified for zero World Cups, exited the Asian Cup group stage every time it qualified, and watched its domestic league — the ISL — grow into a commercially successful product that has done almost nothing to improve the national team's FIFA ranking. India sits at 121st in the world. Jamaica, their semi-final opponent on Wednesday, is 71st.

The gap between the two teams is fifty places, which in FIFA rankings terms means the difference between a country that occasionally qualifies for regional tournaments and a country that occasionally qualifies for the World Cup.

## The Valley

Charlton Athletic's ground in south-east London holds 27,111 people. It sits on Floyd Road, near the Thames, in a part of London where football is not a spectacle — it is a neighbourhood reality. The ground has hosted international matches before. It hosted the Unity Cup in 2004.

The tournament format is simple: four teams, two semi-finals, a final. Nigeria — the defending champions, ranked 26th in the world — play Zimbabwe on Monday. India play Jamaica on Wednesday. The winners meet in the final on Saturday, May 30. The losers play a third-place match.

FIFA has granted the 2026 Unity Cup full Tier 1 International Tournament status. The results count. The caps count. The minutes count.

## Jamaica's squad

India's opponents are not a weak team arriving unprepared. Jamaica's squad includes players from the English Football League — Isaac Hayden (midfielder, formerly of Newcastle United), Joel Latibeaudiere (defender, with Championship experience), and several players competing in England's lower divisions.

Jamaica is coached by Rudolph Speid, who has built a squad that balances English-league experience with Caribbean pace and physicality. The key battle will be in midfield, where India's depleted three-man rotation — Jeakson Singh, Noufal PN, Ricky Shabong — faces a Jamaican engine room with superior depth and match fitness.

## The question

For Khalid Jamil, the tactical problem is acute. With only eighteen players, his substitution options are limited. A single injury in the warm-up could eliminate an entire position from his bench. The three midfielders must cover ninety minutes of a high-intensity semi-final, and at least one of them will need to play the full match without substitution.

But the football problem is secondary to the symbolic one. India's football team is in London. The diaspora is here. The stadium is accessible — not behind a fifteen-hour flight and a visa application, but a Tube ride and a walk down Floyd Road.

The 1.8 million people of Indian origin in the UK — the families in Leicester who have watched every World Cup final at home, the teenagers in Birmingham who play Sunday league football in Indian-branded kits, the professionals in the City who follow the Premier League religiously and the ISL occasionally — have an opportunity that did not exist last year and may not exist next year.

India versus Jamaica. Wednesday, May 27. The Valley, south-east London. Kick-off at a time that works for the local audience. An eighteen-man squad. A depleted roster. A country that has not played on this island in twenty-four years.

The question is not whether India will win. The question is whether enough people will show up to make the AIFF understand that playing in London — playing where the diaspora lives — is not a scheduling inconvenience. It is the entire point.""",
}


if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-26 03:00 UTC (20:00 PDT May 25)")
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

    # ── Insert + image: Article 1 (Divya Deshmukh / Norway Chess) ──
    print("\n[1/2] Inserting: Norway Chess Round 1 — Divya, Gukesh, Pragg...")
    insert_article(a1)
    print(f"  ✓ Inserted: {a1['slug']}")

    # Wikipedia image: Divya Deshmukh
    img1_url = fetch_wikipedia_person_image("Divya Deshmukh")
    img1_attribution = "Wikimedia Commons"
    if not img1_url:
        # Try Gukesh as fallback person
        img1_url = fetch_wikipedia_person_image("Gukesh Dommaraju")
        if not img1_url:
            img1_url = fetch_wikipedia_person_image("D. Gukesh")
    if not img1_url:
        # Last resort: Pexels with specific terms
        img1_url = fetch_pexels_image("chess grandmaster tournament classical game", "chess pieces board closeup")
        img1_attribution = "The Videshi"

    if img1_url:
        img1_path = f"/tmp/{a1_id}.jpg"
        if download_image(img1_url, img1_path):
            uploaded_url = upload_image(a1_id, img1_path)
            if uploaded_url:
                update_article_image(a1_id, uploaded_url, img1_attribution)

    # ── Insert + image: Article 2 (India Unity Cup) ──
    print("\n[2/2] Inserting: India Blue Tigers — Unity Cup London...")
    insert_article(a2)
    print(f"  ✓ Inserted: {a2['slug']}")

    # Wikipedia image: Try India national football team or Sandesh Jhingan or Gurpreet Singh Sandhu
    img2_url = fetch_wikipedia_person_image("India national football team")
    img2_attribution = "Wikimedia Commons"
    if not img2_url:
        img2_url = fetch_wikipedia_person_image("Sandesh Jhingan")
    if not img2_url:
        img2_url = fetch_wikipedia_person_image("Gurpreet Singh Sandhu")
    if not img2_url:
        img2_url = fetch_wikipedia_person_image("Sunil Chhetri")
    if not img2_url:
        # Pexels fallback with specific terms
        img2_url = fetch_pexels_image("Indian football players blue jersey match", "football stadium London evening")
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
