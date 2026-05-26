#!/usr/bin/env python3
"""Sports writer — 2026-05-26 05:00 PDT: 2 articles + score decay.

Article 1: Federation Cup 2026 Days 3-4 — pole vault national record, CWG qualifications cascade
Article 2: India Women's Cricket Team departs for T20 World Cup 2026 in England — chasing 1983 moment at Lord's
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
            f"{person_name} (cricketer)",
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


# ── ARTICLE 1: Federation Cup 2026 Days 3-4 — The CWG Qualification Machine ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Two Men Cleared 5.45 Metres in the Same Pole Vault Final. India's National Record Fell Twice in Ninety Minutes. Sreeshankar Is Back. The Commonwealth Games Qualification List Grew by Seven Names in Two Days.",
    "subheadline": "The Federation Cup in Ranchi moved from sprints to field events on Days 3 and 4, and the results were extraordinary. Dev Kumar Meena and Kuldeep Kumar — training partners from Madhya Pradesh, pushing each other for years — both cleared 5.45 metres to break the national pole vault record. Murali Sreeshankar, the long jumper whose knee injury at the Paris Olympics devastated Indian athletics fans worldwide, jumped 8.08 metres to win gold and qualify for the Commonwealth Games in Glasgow. Sarvesh Kushare equalled the high jump meet record at 2.28 metres and tried — three times — to break the national record at 2.30. Praveen Chithravel crossed 17 metres in the triple jump. Ravina qualified in race walk. Tejas Shirse set a new meet record in the 110-metre hurdles. None of these athletes will be household names in the diaspora. All of them deserve to be.",
    "slug": "federation-cup-2026-ranchi-days-3-4-pole-vault-record-sreeshankar-cwg-qualification-kashare-chithravel-20260526",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Indian athletics exists in a strange space for the diaspora. NRIs know Neeraj Chopra. They might know Hima Das. But the field athletes who are quietly building India into a legitimate multi-event nation at the Commonwealth Games — pole vaulters clearing 5.45 metres, long jumpers flying past 8 metres, triple jumpers crossing 17 — are invisible outside the hardcore athletics community. The Federation Cup in Ranchi just produced seven Commonwealth Games qualifications in two days. That is not a coincidence. That is the result of systematic investment, the creation of training groups (Dev Kumar and Kuldeep train together and push each other), and a generation of athletes who grew up watching Neeraj's Paris gold and decided that field events were worth pursuing. For NRIs who follow Indian sport through IPL scores and Virat Kohli headlines, the Federation Cup results are a signal: India is building athletic depth, not just cricket depth. Glasgow 2026 will be the first Commonwealth Games where India sends a genuinely competitive athletics contingent across multiple field events. The pole vault national record — 5.45 metres — is higher than the bronze medal mark at the last two Commonwealth Games.",
    "tags": ["Dev Kumar Meena", "Kuldeep Kumar", "Murali Sreeshankar", "Sarvesh Kushare", "Praveen Chithravel", "Tejas Shirse", "Ravina", "Federation Cup 2026", "Ranchi", "Commonwealth Games 2026", "Glasgow", "Pole Vault", "Athletics", "India"],
    "urgency": "daily",
    "sources": [
        "https://www.mykhel.com/more-sports/federation-cup-2026-pole-vault-history-meena-kuldeep-sreeshankar-kushare-cwg-marks-435069.html",
        "https://indiasportshub.com/praveen-chithravel-crosses-17m-to-win-federation-cup-2026-eyes-commonwealth-games-glory/",
        "https://indiasportshub.com/tejas-shirse-defends-crown-with-meet-record-at-federation-cup-2026-as-indian-hurdling-continues-to-rise/",
        "https://revsportz.in/the-night-indian-athletics-touched-towering-heights-as-gurindervir-vishal-and-tejaswin-decimate-elusive-barriers/"
    ],
    "word_count": 850,
    "score_total": 65,
    "body": """Two days after Gurindervir Singh ran 10.09 seconds and Vishal TK broke the 45-second barrier in the 400 metres, the Federation Cup in Ranchi shifted from the track to the field. What happened next was, by any reasonable standard, the most productive two days in the history of Indian field athletics.

## The pole vault final nobody expected

Dev Kumar Meena and Kuldeep Kumar are both from Madhya Pradesh. They train together. They have pushed each other through the progression from club-level competitors to national record holders over a period that Indian athletics fans have watched with increasing disbelief.

On Sunday, at the Birsa Munda Stadium in Ranchi, they competed in the same pole vault final. Both cleared 5.45 metres. Both broke the national record of 5.41 metres that Kuldeep had set recently in Bhubaneswar. The previous Federation Cup meet record of 5.35 metres — set by Dev Kumar himself last year — was also erased.

Dev Kumar won gold on countback. Kuldeep settled for silver despite achieving the same height. After the event, Dev Kumar offered the only statement that mattered: "It was a good day for us and we will continue to push each other to further raise the bar in future."

Both have comfortably cleared the Commonwealth Games qualification standard of 5.25 metres. For context, 5.45 metres is higher than the bronze medal performance at the last two Commonwealth Games. India is no longer sending pole vaulters to Glasgow to participate. India is sending pole vaulters to Glasgow to medal.

Tamil Nadu's Reegan G finished third with 5.15 metres — a performance that, in any previous generation of Indian athletics, would have been the national record.

## Sreeshankar is back

The last time most Indian sports fans saw Murali Sreeshankar compete, he was being stretchered off at the Paris Olympics with a knee injury that looked career-threatening. The long jumper from Kerala — who had cleared 8.36 metres to win gold at the 2022 Commonwealth Games in Birmingham — disappeared from competition for more than a year.

On Sunday in Ranchi, Sreeshankar jumped 8.08 metres to win the Federation Cup gold. The distance cleared the Commonwealth Games qualification standard of 8.05 metres by a comfortable margin.

It was not 8.36. It was not a national record. It was something more valuable: proof that the knee works, the technique is intact, and the man who won gold in Birmingham four years ago can defend his title in Glasgow. S Lokesh finished second with 7.94 metres and Mohd Atta Sazid took bronze with 7.90 metres — a depth of performance in a single event that Indian long jump has never previously produced.

## Kushare's three attempts at history

Maharashtra's Sarvesh Anil Kushare won the high jump with a clearance of 2.28 metres, equalling the Federation Cup meet record previously set by Tejaswin Shankar — the same Tejaswin who broke the 8,000-point barrier in the decathlon on Day 2 of these championships.

The 2.28-metre jump cleared the CWG qualification standard of 2.22 metres with room to spare. Then Kushare raised the bar to 2.30 metres, attempting a new national record.

He missed on all three attempts. But the fact that he tried — that the bar was at 2.30 at all — tells you where Indian high jump is heading. Tamil Nadu's Aadarsh Ram cleared 2.22 metres for silver, also meeting the CWG qualification standard.

## Chithravel crosses 17 metres

In the triple jump, Praveen Chithravel produced a winning distance of 17.08 metres, surpassing the Commonwealth Games qualification mark and positioning himself as India's strongest medal contender in the event at Glasgow.

The jump was clinical rather than spectacular — a controlled approach, a measured hop-step-jump sequence, and a landing that left no doubt. Chithravel has been building towards this for two seasons, and the 17-metre barrier was as much a psychological threshold as a physical one.

## Shirse's hurdles, Ravina's walk

Tejas Ashok Shirse defended his 110-metre hurdles title in 13.50 seconds, improving his own meet record of 13.61. The performance narrowly missed the CWG qualification mark of 13.39 seconds — a gap of eleven hundredths that Shirse will spend the next three months trying to close. Krishik M finished second in 13.52, and the depth of Indian sprint hurdling is now genuinely startling: two men under 13.55 in the same final would have been unthinkable a decade ago.

In the morning session, Haryana's Ravina won the women's 10,000-metre race walk in 44 minutes 29.66 seconds, comfortably inside the CWG qualification standard of 44:44.58. It was a controlled, professional performance — the kind of race walk that does not make highlight reels but earns selection.

## What Glasgow means

The Commonwealth Games in Glasgow in September 2026 will be the first major multi-sport event where India sends a genuinely competitive athletics contingent across multiple field events. Previous Commonwealth Games campaigns relied on one or two medal hopes — Neeraj Chopra in javelin, Sreeshankar in long jump — surrounded by athletes who were there to gain experience.

The Federation Cup results suggest something different. India now has realistic medal contenders in pole vault (Dev Kumar and Kuldeep, both clearing heights that would have medalled at recent CWG), long jump (Sreeshankar, defending champion), high jump (Kushare, equalling 2.28), triple jump (Chithravel, crossing 17 metres), and the sprint events where Gurindervir and Vishal TK shattered barriers on Day 2.

Add Neeraj Chopra in javelin — whenever his injury status allows — and India could theoretically contend for athletics medals in six or seven events at Glasgow. For a country that has historically treated the Commonwealth Games athletics programme as a participation exercise with occasional surprises, this is a structural shift.

Ranchi's Birsa Munda Stadium is not the most glamorous athletics venue in the world. The Federation Cup is not the most prestigious meet. But what happened there over four days — five national records, seven-plus Commonwealth Games qualifications, a pole vault final where two men cleared 5.45 metres — is the clearest evidence yet that Indian athletics is no longer a one-man Neeraj Chopra operation.

The names are Dev Kumar Meena, Kuldeep Kumar, Murali Sreeshankar, Sarvesh Kushare, Praveen Chithravel, Gurindervir Singh, Vishal TK, Tejaswin Shankar, Tejas Shirse, and Ravina. They are not household names in the diaspora. They are about to become household names in Glasgow.""",
}


# ── ARTICLE 2: India Women depart for T20 World Cup 2026 in England ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "India's Women Just Won the ODI World Cup. Now They Have Flown to England to Chase the T20 Title. Their First Match Is Against Pakistan at Edgbaston. The Final Is at Lord's on July 5.",
    "subheadline": "Harmanpreet Kaur, Smriti Mandhana, Jemimah Rodrigues, and the squad that won the 2025 ODI World Cup departed Mumbai on Saturday for the ICC Women's T20 World Cup 2026 in England and Wales. India's campaign opens on June 14 against Pakistan at Edgbaston — Birmingham, a city where more than a hundred thousand people of Indian origin live. The group stage takes India to Manchester, Bristol, and Leeds. The final is at Lord's on July 5. Jemimah Rodrigues has said she wants India to have their own 1983 moment at Lord's — the ground where Kapil Dev lifted the men's World Cup forty-three years ago. Mandhana says the team is 'really hungry.' The squad includes Nandni Sharma, a 24-year-old pacer earning her first World Cup call-up after seventeen wickets in WPL 2026. New Zealand are the defending champions. India have never won a T20 World Cup.",
    "slug": "india-women-cricket-t20-world-cup-2026-england-pakistan-lords-harmanpreet-mandhana-jemimah-20260526",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "The ICC Women's T20 World Cup 2026 is being played in England and Wales from June 12 to July 5. For the Indian diaspora in the UK — an estimated 1.8 million people — this is the first time a major women's cricket tournament is being hosted on their doorstep with India as genuine contenders. India open against Pakistan at Edgbaston in Birmingham, where the Indian community is among the largest in the UK. The group stage takes them to Old Trafford in Manchester, the County Ground in Bristol, and Headingley in Leeds — cities with significant Indian populations. The final is at Lord's on July 5. Jemimah Rodrigues has explicitly referenced 1983 — the year Kapil Dev lifted the men's World Cup at Lord's in what remains the single most important moment in Indian cricket history. For NRIs in London, Birmingham, Manchester, and Leeds, this tournament offers something that rarely exists: the chance to watch India play live, in person, at grounds they can drive to, in a tournament India can realistically win. The ODI World Cup victory in 2025 was watched on screens. The T20 World Cup 2026 can be watched from the stands. That is a meaningful difference for a community that follows Indian cricket with religious devotion but almost never gets to be physically present for the biggest moments.",
    "tags": ["India Women's Cricket", "T20 World Cup 2026", "Harmanpreet Kaur", "Smriti Mandhana", "Jemimah Rodrigues", "Shafali Verma", "Nandni Sharma", "England", "Lord's", "Edgbaston", "Pakistan", "ICC", "1983", "UK Diaspora"],
    "urgency": "daily",
    "sources": [
        "https://www.livemint.com/sports/cricket-news/team-india-depart-for-icc-womens-t20-world-cup-2026-in-england-and-wales-11748001608568.html",
        "https://www.icc-cricket.com/news/jemimah-and-india-chase-their-own-1983-moment-at-lords-womens-t20-world-cup-2026",
        "https://www.icc-cricket.com/news/mandhana-certain-india-can-carry-winning-momentum-into-t20wc-womens-t20-world-cup-2026",
        "https://www.sportstiger.com/news/indian-womens-team-departs-for-icc-womens-t20-world-cup-2026-with-eyes-on-historic-glory",
        "https://www.cricbuzz.com/cricket-news/nandni-sharma-earns-call-up-for-t20-world-cup"
    ],
    "word_count": 830,
    "score_total": 68,
    "body": """The Indian women's cricket team boarded a flight from Mumbai to London on Saturday. Their luggage included the confidence of having won the ODI World Cup seven months ago, the memory of a T20I series victory over Australia in April, and the weight of never having won a T20 World Cup in the tournament's history.

The ICC Women's T20 World Cup 2026 begins on June 12 in England and Wales. India's first match is on June 14 — against Pakistan, at Edgbaston, in Birmingham.

## The squad

Harmanpreet Kaur leads. At thirty-seven, this is almost certainly her final World Cup as captain. The woman who scored 171 not out in the 2017 ODI World Cup semi-final — a knock that single-handedly made women's cricket visible in India — is now playing for a legacy that would make her the most successful captain in Indian women's cricket history.

Smriti Mandhana opens. She has been the most consistent batter in women's cricket for the better part of three years, and her confidence before departure bordered on conviction: "We are really hungry. We have been playing together for a long time and we know each other's game. The most fit and fresh team will win."

Jemimah Rodrigues bats in the middle order and carries the emotional weight of a generation. In the 2025 ODI World Cup semi-final, she scored 127 — a knock that turned a desperate chase into a procession. When asked about the T20 World Cup, she did not talk about strategy or matchups. She talked about Lord's.

"Our 1983 moment," she said. "That's what we're chasing. Lord's on July 5."

## The 1983 question

On June 25, 1983, Kapil Dev lifted the Prudential World Cup at Lord's after India beat the West Indies in a final that nobody outside the Indian dressing room believed India could win. It was the single most transformative moment in Indian cricket history — the event that turned cricket from a colonial pastime into a national religion.

Forty-three years later, the Indian women's team has the opportunity to create the same image at the same ground. The T20 World Cup final is at Lord's on July 5, 2026. India have never won a T20 World Cup. They reached the final in 2020, in Melbourne, and lost to Australia in front of 86,174 people.

The comparison is imperfect — the men's 1983 squad were rank outsiders, while this Indian women's team is among the favourites. But the symbolism is exact: an Indian team, at Lord's, lifting a World Cup trophy, in front of a crowd that will include tens of thousands of British Indians making the pilgrimage to St John's Wood.

## The group stage

India's group includes Pakistan, South Africa, Bangladesh, and the Netherlands. The matches are spread across English grounds that are, for the diaspora, comfortably accessible:

**June 14:** India vs Pakistan — Edgbaston, Birmingham. The biggest Indian community in the English Midlands. A rivalry that transcends cricket. The ground holds 25,000. It will be full.

**June 18:** India vs South Africa — a venue to be confirmed, likely Bristol or Headingley. South Africa are genuine contenders, and this match could determine group seedings.

**June 25:** India vs Bangladesh — Old Trafford, Manchester. A ground that Indian cricket fans associate with the 2019 men's World Cup semi-final, where India's tournament ended against New Zealand.

**June 22 or 28:** India vs Netherlands — a match India are expected to win comfortably, but the Dutch women have been improving rapidly.

## Nandni Sharma's call-up

The squad includes one first-timer who deserves attention. Nandni Sharma is a twenty-four-year-old fast bowler who took seventeen wickets in WPL 2026 — a tournament that has, in three seasons, fundamentally changed the pipeline for Indian women's cricket.

Before the WPL existed, a pacer like Nandni would have had to prove herself through domestic cricket that received almost no attention, no coaching infrastructure, and no broadcast coverage. The WPL gave her a platform, coaching from international-standard support staff, and the pressure of performing in front of television audiences.

Seventeen wickets later, she is in the World Cup squad. The pipeline works.

## What the diaspora gets

For the 1.8 million people of Indian origin in the United Kingdom, the T20 World Cup 2026 is the rarest of events: a major cricket tournament featuring India, played on grounds they can reach by train.

Birmingham, Manchester, Leeds, Bristol, and London — the five cities hosting matches — are home to significant Indian communities. The accessibility is not abstract. It is a question of whether you can take a half-day from work, buy a ticket for thirty pounds, and be in the ground by the time India bats.

The men's T20 World Cup in 2026 was in India. The 2025 ODI World Cup was in India. The 2023 men's ODI World Cup was in India. The 2024 men's T20 World Cup was in the Caribbean and the United States. For British Indians, watching India play live cricket has meant flights, visas, and annual leave.

The Women's T20 World Cup in England changes that equation entirely. India vs Pakistan at Edgbaston on June 14 is not a screen event for the Birmingham diaspora. It is a ten-minute drive.

## The hunger

Mandhana used the word "hungry" three times in her pre-departure press conference. Harmanpreet talked about "setting a new bar." Rodrigues talked about Lord's and 1983.

The message from the Indian camp is coherent and unambiguous: they believe they are the best team in the world, they believe the ODI World Cup victory in 2025 was a beginning rather than a culmination, and they want to win the one trophy that has eluded Indian women's cricket.

New Zealand are the defending champions. Australia are perennial favourites. England have home advantage. South Africa have the bowling attack.

India have the batting, the hunger, and the ghost of 1983 waiting at Lord's.

The flight from Mumbai landed in London. The World Cup begins in seventeen days. The final is at the most famous cricket ground on earth. For the diaspora in the UK, the tickets are already on sale.""",
}


if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-26 05:00 PDT")
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

    # ── Insert + image: Article 1 (Federation Cup field events) ──
    print("\n[1/2] Inserting: Federation Cup Days 3-4 — CWG Qualification Machine...")
    insert_article(a1)
    print(f"  ✓ Inserted: {a1['slug']}")

    # Wikipedia image: Murali Sreeshankar (most prominent athlete in article)
    img1_url = fetch_wikipedia_person_image("Murali Sreeshankar")
    img1_attribution = "Wikimedia Commons"
    if not img1_url:
        img1_url = fetch_wikipedia_person_image("Praveen Chithravel")
    if not img1_url:
        img1_url = fetch_wikipedia_person_image("Tejaswin Shankar")
    if not img1_url:
        # Pexels fallback — specific
        img1_url = fetch_pexels_image("pole vault athletics competition", "athletics track field events stadium")
        img1_attribution = "The Videshi"

    if img1_url:
        img1_path = f"/tmp/{a1_id}.jpg"
        if download_image(img1_url, img1_path):
            uploaded_url = upload_image(a1_id, img1_path)
            if uploaded_url:
                update_article_image(a1_id, uploaded_url, img1_attribution)

    # ── Insert + image: Article 2 (India Women T20 World Cup) ──
    print("\n[2/2] Inserting: India Women T20 World Cup 2026 — Chasing 1983 at Lord's...")
    insert_article(a2)
    print(f"  ✓ Inserted: {a2['slug']}")

    # Wikipedia image: Smriti Mandhana or Harmanpreet Kaur
    img2_url = fetch_wikipedia_person_image("Smriti Mandhana")
    img2_attribution = "Wikimedia Commons"
    if not img2_url:
        img2_url = fetch_wikipedia_person_image("Harmanpreet Kaur")
    if not img2_url:
        img2_url = fetch_wikipedia_person_image("Jemimah Rodrigues")
    if not img2_url:
        img2_url = fetch_wikipedia_person_image("India women's national cricket team")
    if not img2_url:
        # Pexels fallback — specific
        img2_url = fetch_pexels_image("women cricket match India blue jersey", "cricket stadium England")
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
