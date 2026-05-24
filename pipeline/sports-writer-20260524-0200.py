#!/usr/bin/env python3
"""Sports writer — 2026-05-24 02:00 PDT run: 2 articles + score decay."""

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

# ── ARTICLE 1: Krishna Jayasankar — Shot Put Gold via Jamaica and the NCAA ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "She Left Chennai for Jamaica at 17, Trained at a US University Most Indians Have Never Heard Of, and Just Won India's Shot Put Gold.",
    "subheadline": "Krishna Jayasankar threw 17.35 metres at the Federation Cup in Ranchi on Saturday — her personal best, the best outdoor mark by an Indian woman this season, and the culmination of the most unconventional path any Indian female thrower has ever taken. Her parents played basketball for India. She went to Jamaica to get noticed. She ended up at UNLV in Las Vegas. Now she throws for Reliance Foundation in Mumbai and is 27 centimetres away from the Commonwealth Games.",
    "slug": "krishna-jayasankar-federation-cup-2026-shot-put-gold-jamaica-ncaa-unlv-reliance-diaspora-20260524",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Krishna Jayasankar's career was built almost entirely within the Indian diaspora's American infrastructure. She moved to Jamaica as a teenager to access the scouting pipeline that feeds into US college athletics. She competed on the NCAA Division I circuit at UNLV, where Indian-origin students make up one of the fastest-growing international cohorts. Her parents — both former India basketball players — understood what Indian sports infrastructure could not provide and sent her abroad to get it. Her story is the women's version of the pipeline that produced Tejaswin Shankar at Kansas State and is now producing a generation of Indian athletes who leave home to learn how to throw, jump, and sprint at world-class facilities, then return to represent the country at national championships. For NRI families in the US who push their children toward cricket or academics, Krishna's story rewrites the map of what's possible: an Indian woman, trained in the American system, throwing past 17 metres in a discipline that has fewer than five serious Indian practitioners in any given year.",
    "tags": ["Krishna Jayasankar", "Federation Cup 2026", "Shot Put", "NCAA", "UNLV", "Reliance Foundation", "Indian Athletics", "Commonwealth Games", "Jamaica", "Indian Women Athletes", "Ranchi", "Track and Field"],
    "urgency": "daily",
    "sources": [
        "https://indiasportshub.com/articles/from-chennai-to-ranchi-via-usa-krishna-jayasankar-s-shotput-gold",
        "https://ianslive.in/news/federation_cup_athletics_gurvindervir_vishal_tk_set_new_records_tejaswin_crosses_8000_points_in_decathlon-1146529/SPORTS/3",
        "https://mykhel.com/athletics/federation-cup-2026-live-gurindervirs-10-09s-vishal-sub-45-tejaswin-8057-headline-historic-day-315507.html",
        "https://mykhel.com/athletics/gurindervir-singh-smashes-100m-national-record-with-historic-10-09s-sprint-at-federation-cup-2026-qualifies-for-cwg-2026-315531.html"
    ],
    "word_count": 720,
    "score_total": 62,
    "body": """On Saturday afternoon at Birsa Munda Stadium in Ranchi, while the track was still buzzing from Gurindervir Singh's 10.09-second sprint and Vishal TK's sub-45 quarter mile, a 23-year-old woman stepped into the throwing circle for the women's shot put final and produced the quietest breakthrough of the entire Federation Cup.

Krishna Jayasankar Menon threw 17.35 metres on her fourth attempt. It was her personal best. It was the best outdoor mark by an Indian woman in the event this season. It won her gold by 53 centimetres over Yogita of Haryana, who threw 16.82 metres for silver.

The number does not break a national record. It does not meet the Commonwealth Games qualifying standard of 17.62 metres. By the headline-grade arithmetic this Federation Cup has produced, a 17.35-metre throw can read like the quiet event of the weekend.

It is anything but.

## The Chennai-to-Jamaica pipeline

Krishna's parents, Prasanna and Jayasankar Menon, both played basketball for India. Sport was the family language. But Krishna's event was chosen by accident: a physical education teacher in Chennai noticed her during a recess throwing session and asked her to try the shot put. "The moment I released it for the first time, something within me unlocked," she has said.

What happened next was strategically sharp in a way that almost no Indian throwing athlete has attempted. Recognising that the infrastructure for women's throwing events in India — coaching depth, competition density, access to technical analysis — does not exist at the level a developing shot putter needs, Krishna's family sent her abroad. Not to the United States directly. To Jamaica.

The logic was specific. American college coaches in the throwing events frequently travel to Jamaica to scout. Establishing herself in the Jamaican training ecosystem would put Krishna in front of the right eyes and give her a pathway into the NCAA — the American college sports circuit that allows athletes to train, compete, and study simultaneously at the university level.

The plan worked. Krishna moved to the United States, joined the University of Nevada, Las Vegas, and began competing on a calendar built around back-to-back indoor and outdoor seasons, multiple meets per month, and the kind of competitive volume that throwers in India rarely experience. The training was harder. The technique was finer. The throws started moving.

## Four indoor national records in twelve months

In March 2025, at the Mountain West Indoor Championships in Albuquerque, Krishna became the first Indian woman to cross 16 metres in indoor shot put, throwing 16.03 and breaking a national record that had stood since 2023.

Then 2026 happened. In February, she threw 16.63 metres at the New Mexico Team Open. Weeks later, at the Don Kirby Elite Invitational, she pushed it to 16.83. On 28 February, at the Mountain West Conference Championships in Reno, she threw 17.09 metres — extending her own indoor national record for the fourth time in twelve months and becoming the first Indian woman to throw past 17 metres indoors.

She has been working a secondary event in parallel. At this same Federation Cup, two days before her shot put gold, Krishna threw 55.00 metres to take bronze in the women's discus. World Athletics currently ranks her 107th in the world in shot put and 207th in discus.

## The Reliance Foundation bridge

Krishna now trains at the Reliance Foundation Athletics High Performance Centre in Mumbai under an Olympic gold medal-winning throws coach when she is in India, and continues to compete on the NCAA circuit when she is in the United States. The arrangement — part Indian, part American, connected by a corporate-funded training centre — is the same pipeline that produced Gurindervir Singh's 10.09 on the same Ranchi track hours earlier. Reliance Foundation athletes won gold in the men's 100 metres, the men's decathlon, and the women's shot put at this Federation Cup.

Her father has said the family wants one thing beyond the records. "She's waiting to represent India. Very passionate. Very hungry."

## The 27-centimetre gap

The Commonwealth Games qualifying mark of 17.62 metres sat 27 centimetres beyond Krishna's best throw on Saturday. In an event measured in inches, that gap is real but bridgeable. Whether the Athletics Federation of India selects her on form, on trajectory, or strictly on the standard will be decided in the next few weeks.

Her series in Ranchi read 16.32, 17.01, 16.25, 17.35, foul, pass. Two throws past 17 metres in the same competition. That is a kind of consistency at that range that no Indian woman has shown this season.

The barrier above her on the all-time list is 18.41 metres. The journey from a school playground in Chennai to a training base in Jamaica to NCAA podiums in the American Southwest, and now to a Reliance Foundation gold in Ranchi, suggests Krishna Jayasankar is not the kind of athlete who stops at one breakthrough.

For Indian families in the United States and the Caribbean who push their children toward the sports pathways they know — cricket, tennis, maybe swimming — Krishna's route offers an entirely different map. The throwing events have no Indian tradition to inherit. She is building one from scratch, three continents at a time.""",
}

# ── ARTICLE 2: Tejaswin Shankar's 8057-Point Decathlon — Kansas State to Ranchi ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "He Won Two NCAA Titles at Kansas State, Worked at Deloitte, Quit, and Just Became the First Indian to Score 8,000 Points in the Decathlon.",
    "subheadline": "Tejaswin Shankar scored 8,057 points at the Federation Cup in Ranchi on Saturday — a national record that shattered his previous best by 231 points, qualified him for the Commonwealth Games, and confirmed that India's most versatile male athlete was built in Manhattan, Kansas. He co-founded a company to send the next generation of Indian athletes to the same American system that made him.",
    "slug": "tejaswin-shankar-8057-decathlon-national-record-federation-cup-2026-kansas-state-ncaa-deloitte-kings-sports-group-diaspora-20260524",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Tejaswin Shankar is the most complete product of the Indian-to-American-college pipeline in Indian athletics. He arrived at Kansas State University in 2017 on a four-year athletics scholarship, studied accounting, won two NCAA Division I high jump championships, worked at Deloitte in the United States after graduating, and then quit corporate America to become a full-time athlete. His wife, former Indian sprinter Siddhi Hiray, is his business partner. In 2024 they co-founded King's Sports Group — a company built explicitly to help talented Indian student-athletes secure sports scholarships and opportunities in the US collegiate system. That company is the diaspora angle made operational: an NRI-trained athlete building an institutional bridge between Indian talent and American training infrastructure. For every Indian parent in New Jersey or Texas or the Bay Area wondering whether their child's track-and-field ability could lead somewhere, King's Sports Group exists because Tejaswin Shankar walked that path first and decided it should not be a one-off.",
    "tags": ["Tejaswin Shankar", "Decathlon", "Federation Cup 2026", "Kansas State", "NCAA", "National Record", "Commonwealth Games", "Indian Athletics", "Ranchi", "Deloitte", "Kings Sports Group", "Reliance Foundation", "High Jump", "Track and Field"],
    "urgency": "daily",
    "sources": [
        "https://en.wikipedia.org/wiki/Tejaswin_Shankar",
        "https://kstatesports.com/sports/mens-track-and-field/roster/tejaswin-shankar/10327",
        "https://mykhel.com/athletics/federation-cup-2026-live-gurindervirs-10-09s-vishal-sub-45-tejaswin-8057-headline-historic-day-315507.html",
        "https://inshorts.com/en/news/tejaswin-shankar-becomes-1st-indian-ever-to-cross-8000-points-in-decathlon-1748016088023",
        "https://indianexpress.com/article/sports/athlete-couple-siddhi-hiray-and-tejaswin-shankar-chart-a-course-for-indias-ncaa-aspirants/"
    ],
    "word_count": 750,
    "score_total": 68,
    "body": """On Saturday evening in Ranchi, on a day when Indian athletics produced three national records in the space of an hour, the one that may matter most in ten years was the quietest to arrive.

Tejaswin Shankar — TJ to everyone who has watched him since he was a high school high jumper in Delhi — finished the decathlon at the Federation Cup with 8,057 points. It is a national record, smashing his previous best of 7,826 set in Poland last July. It is the first time any Indian has crossed the 8,000-point threshold. It qualifies him for the 2026 Commonwealth Games in Glasgow by a comfortable margin. And it was produced by an athlete whose career was built, almost in its entirety, at a university in Manhattan, Kansas, that most Indians cannot place on a map.

## From Saket to Manhattan

Shankar was born in 1998 in Saket, New Delhi, into a Tamil Brahmin family. He played cricket until eighth grade at Sardar Patel Vidyalaya. Then a PE teacher suggested he try high jump. He broke the national junior record at seventeen. He was bedridden with a slipped disc for six months at eighteen.

In 2017, at a point when most Indian athletes were navigating the domestic federation system and hoping for a national camp call-up, Shankar did something that almost no Indian track and field athlete had done before: he accepted a four-year athletics scholarship at Kansas State University.

What followed was one of the most successful careers by any international athlete in NCAA Division I history. He won the NCAA outdoor high jump championship in 2018 as a freshman. He won it again in 2022 as a fifth-year senior, clearing 2.27 metres in a sudden-death jump-off that remains one of the most dramatic moments in recent collegiate athletics. He earned six All-American honours. He held Big 12 conference records. He studied accounting and finance.

Then he graduated and went to work at Deloitte.

## The Deloitte interlude

Most athletes who leave their sport for a corporate career do not come back. Shankar, who is six foot four and spent five years as one of the best high jumpers in American college athletics, sat at a desk in the United States and decided he was not finished.

He quit Deloitte to become a full-time athlete again. He already had a Commonwealth Games bronze medal in high jump from Birmingham 2022 — a medal he had to go to court to win, after the Athletics Federation of India initially left him out of the squad despite qualifying. Now he wanted to do something different. He wanted to do all ten events.

## The decathlon switch

The high jump is one event. The decathlon is ten, spread over two days: 100 metres, long jump, shot put, high jump, 400 metres on day one; 110-metre hurdles, discus, pole vault, javelin, and 1,500 metres on day two. It requires not just talent in each discipline but the ability to accumulate points across events where you are, by definition, not a specialist.

Shankar's high jump gave him a head start. His 2.19 metres in the high jump alone earned 982 points — nearly a thousand-point advantage over most decathletes in that single event. But the rest had to be built from scratch. He learned the hurdles. He learned the throws. He learned to pole vault. He trained the 1,500 metres, which for a high jumper is roughly the equivalent of asking a chess grandmaster to run a mile at the end of a tournament.

At the 2023 Asian Games in Hangzhou, he won a silver medal with 7,576 points. At the 2025 Asian Championships in Gumi, another silver. Each competition, the point total climbed. On Saturday in Ranchi, it broke through.

His day-two performance was the key. Four personal bests across the ten events, the kind of all-round improvement that only comes when an athlete's training has matured across every discipline simultaneously. The 8,057-point total puts him among the top decathletes in Asian history and within range of world championship scoring.

## King's Sports Group

In 2024, Shankar married Siddhi Hiray, a former Indian sprinter. They had been partners for years — in life and, increasingly, in a project that may outlast his competitive career.

Together they co-founded King's Sports Group, a company built explicitly to help talented Indian student-athletes secure sports scholarships in the American collegiate system. The idea is personal. Shankar's own journey from Delhi to Kansas State transformed his career. He knows what the American system can provide — world-class coaching, competitive volume, nutritional infrastructure, biomechanical analysis — that the Indian system, for most non-cricket athletes, simply cannot.

King's Sports Group is the pipeline made institutional. For every promising shot putter in Tamil Nadu, every pole vaulter in Kerala, every hurdler in Jharkhand who cannot find the training density they need at home, the company offers a pathway that Shankar walked first.

## The Ranchi meaning

On a single Saturday evening in Ranchi, three Reliance Foundation athletes set national records. Gurindervir Singh ran 10.09 in the 100 metres. Vishal TK ran 44.98 in the 400 metres. Tejaswin Shankar scored 8,057 in the decathlon.

All three were produced, at least in part, by the intersection of Indian talent and foreign infrastructure — whether that infrastructure was the American collegiate system, international competition circuits, or corporate-funded training centres that bring world-class coaching to Indian soil.

For the Indian diaspora, the message is becoming hard to ignore. The pathway out and back works. The question is no longer whether India can produce world-class athletes outside of cricket. It is whether India can produce enough institutions — enough King's Sports Groups, enough Reliance centres, enough scholarship pipelines — to catch the talent before it stops trying.""",
}

if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-24 02:00 PDT")
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

    print("\nInserting Article 1: Krishna Jayasankar Shot Put...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    # Try image for Article 1
    img1_path = f"/tmp/{a1_id}.jpg"
    if fetch_image("female athlete shot put throw stadium", img1_path):
        img1_url = upload_image(a1_id, img1_path)
        if img1_url:
            update_image_url(a1_id, img1_url)

    print("\nInserting Article 2: Tejaswin Shankar Decathlon...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    # Try image for Article 2
    img2_path = f"/tmp/{a2_id}.jpg"
    if fetch_image("decathlon athlete high jump track field", img2_path):
        img2_url = upload_image(a2_id, img2_path)
        if img2_url:
            update_image_url(a2_id, img2_url)

    # Score decay
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    print(f"\nDone. 2 articles published.")
    print(f"  IDs: {a1_id}, {a2_id}")
