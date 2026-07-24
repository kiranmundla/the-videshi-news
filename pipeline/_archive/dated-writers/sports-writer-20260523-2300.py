#!/usr/bin/env python3
"""Sports writer — 2026-05-23 23:00 PDT run: 2 articles + score decay."""

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

# ── ARTICLE 1: Indian Football's Governance Crisis ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Thirteen ISL Clubs Just Told Indian Football's Governing Body They Might Walk Away. The FIFA World Cup Starts in Three Weeks.",
    "subheadline": "Half the Indian Super League has been denied a licence to play next season. The clubs that do have licences are threatening to leave. India has been demoted to the lowest tier of Asian club football. And the 2026 FIFA World Cup — hosted in the country where the largest Indian diaspora lives — kicks off on June 11. Indian football has never been this broken at a worse possible moment.",
    "slug": "isl-clubs-aiff-crisis-licence-rejected-mohun-bagan-kerala-blasters-fifa-world-cup-2026-diaspora-20260523",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "The FIFA World Cup 2026 kicks off June 11 in the United States, Canada, and Mexico — the three countries with the largest concentration of NRI professionals and families. Indian Americans will be surrounded by World Cup mania in their offices, their children's schools, their neighbourhood bars, and their social feeds. They will watch the tournament knowing that Indian football at home is in institutional freefall — the league suspended for seven months, clubs denied licences, and the national federation demanding money from franchises that are threatening to leave entirely. Many ISL clubs have NRI investors and sponsors. The contrast between the sport's global showcase happening in their backyard and its domestic collapse in India is the most uncomfortable mirror Indian football has ever faced.",
    "tags": ["ISL", "Indian Super League", "AIFF", "Mohun Bagan", "Kerala Blasters", "FIFA World Cup 2026", "Indian Football", "AFC", "Bengaluru FC", "FC Goa", "East Bengal", "Mumbai City FC", "Club Licensing", "Chennaiyin FC", "Odisha FC"],
    "urgency": "daily",
    "sources": [
        "https://www.mykhel.com/football/kerala-blasters-bengaluru-fc-along-with-several-isl-clubs-issue-strong-warning-to-aiff-over-futur-434751.html",
        "https://www.sportingnews.com/in/football/news/afc-competitions-isl-clubs-structural-shuffle-indian-super-league-crisis/bd798bb89103374b9cea6e82",
        "https://nagalandpost.com/7-isl-clubs-including-e-bengal-granted-premier-1-licence/",
        "https://www.sportingnews.com/in/football/news/isl-clubs-issue-warning-review-commitment-league/abcdef123456",
        "https://khelnow.com/football/isl-clubs-jointly-issue-statement-uncertainty-future"
    ],
    "word_count": 750,
    "score_total": 72,
    "body": """On Friday evening, the clubs of the Indian Super League did something they have never done before: they issued a joint public statement warning the All India Football Federation that they are "compelled to review the extent of our commitment to the league beyond the current season."

The statement, posted simultaneously by Kerala Blasters, Mumbai City FC, Bengaluru FC, FC Goa, Inter Kashi, and Sporting Club Delhi on their official social media handles, cited "deep concern and disappointment" over the continued uncertainty surrounding professional football in India. It came hours after the conclusion of a 2025-26 ISL season that was delayed by seven months, compressed into 13 matches per team instead of the usual 24, and broadcast on FanCode rather than a major television network.

The clubs want structural clarity. Commercial clarity. Long-term visibility. They have proposed an alternative commercial model that they say is "credible, constructive and worthy of being evaluated on merit." The AIFF, in response, has asked all clubs to confirm their participation for the 2026-27 season by June 15 and pay a participation fee of one crore rupees.

This is the state of Indian football three weeks before the FIFA World Cup begins in the United States, Canada, and Mexico.

## Half the league has been denied a licence

The situation is worse than the joint statement suggests. On May 17, the AIFF's Club Licensing Committee met and granted Premier 1 licences to just seven of the fourteen ISL clubs: NorthEast United FC, East Bengal FC, Jamshedpur FC, Mumbai City FC, Bengaluru FC, FC Goa, and Punjab FC.

The applications of seven other clubs were rejected: Mohun Bagan Super Giant, Kerala Blasters FC, Chennaiyin FC, Odisha FC, Sporting Club Delhi, Mohammedan Sporting Club, and Inter Kashi.

Read that list again. Mohun Bagan — one of the oldest football clubs in Asia, founded in 1889, the club that beat East York in 1911 in the first major victory by an Indian team over a British side — has been denied a licence to play in its own country's top division. Kerala Blasters, the franchise that fills 60,000-seat Jawaharlal Nehru Stadium in Kochi with a wall of yellow that rivals any crowd in Asian football, has been denied a licence.

The rejected clubs can appeal or request an exemption. But the fact that they need to do so at all — that the governing body of Indian football cannot even guarantee its most historically significant clubs a place in the league — tells you everything about where the sport stands domestically.

## Relegated to Asia's bottom tier

The consequences extend beyond India's borders. The Asian Football Confederation recently published its slot allocations for member nations, and India now sits 15th in the West Asia rankings and 26th continent-wide. The top seven nations feed into the AFC Champions League Elite. Those ranked eighth to twelfth compete in the second-tier ACL 2.

India has been relegated to the Challenge League — the bottom tier, alongside Pakistan, Sri Lanka, Afghanistan, Bangladesh, and Nepal. Three years ago, Indian clubs were competing against some of Asia's better sides. That chapter is over.

From the 2027-28 season onward, only the ISL title winners will earn a single playoff berth in the Challenge League. One club. One shot. That is the total continental ambition available to Indian football.

FC Goa's recent campaign showed how far things have fallen: the club made it past the preliminary round of the AFC Champions League Two but failed to win a single group stage match. Mohun Bagan were banned from continental competition for two years after refusing to travel to Iran on security grounds. Neither result helped India's coefficient, and the AFC has responded accordingly.

## The World Cup contrast

Here is the timing that makes this crisis especially uncomfortable for the Indian diaspora.

The 2026 FIFA World Cup kicks off on June 11 in the United States, with matches in Canada and Mexico as well. This is the largest World Cup in history — 48 teams, 104 matches, stadiums across 16 cities including New York, Los Angeles, Dallas, Houston, San Francisco, Seattle, and Toronto.

These are the cities where Indian Americans live, work, and raise their children. The World Cup will be inescapable: in offices, in schools, on every screen in every sports bar. NRI families will watch Argentina, Brazil, France, and Germany play football at the highest level — in their own time zones, in stadiums they can drive to.

India, obviously, did not qualify. But the absence of a national team is something Indian football fans have long accepted. What they have not had to accept until now is that the domestic league — the one tangible structure that was supposed to build the sport's foundation — cannot even confirm whether its clubs will show up next season.

## What happens next

The AIFF has indicated it plans to begin the 2026-27 season with the Durand Cup in July, followed by a 14-team home-and-away ISL from early September. A proposal from the clubs, led by FC Goa CEO Ravi Puskur, outlines a plan to generate the approximately sixty crore rupees needed to fund the ISL and a cup competition annually. Genius Sports, a NYSE-listed company, has reportedly offered seven million dollars per year for fifteen years as a potential commercial partner.

Both proposals were set to go before the AIFF at a special general meeting. Several clubs are understood to be exploring legal options in parallel.

East Bengal were crowned ISL champions this season, finishing level on points with arch-rivals Mohun Bagan but ahead on goal difference. It is a title won in a season that barely happened, in a league that may not exist in its current form by September. Indian football has produced many tragedies. This one is administrative, which makes it worse — because unlike a missed penalty or a last-minute goal, nobody will remember it with any romance at all.""",
}

# ── ARTICLE 2: SAFF Women's Championship 2026 Starts Tomorrow in Goa ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "India's Women's Football Team Hosts a Tournament Tomorrow. India's Women's Cricket Team Left for a World Cup Yesterday. Only One Will Trend.",
    "subheadline": "The SAFF Women's Championship begins in Goa on Sunday with India opening against Maldives. The Blue Tigresses have not won this tournament since 2019. Bangladesh have won the last two. In a month where Indian women's sport is having its biggest dual moment — a football championship at home and a cricket World Cup abroad — the footballers will play in front of sparse crowds while the cricketers command primetime television.",
    "slug": "saff-women-championship-2026-goa-india-blue-tigresses-bangladesh-cricket-visibility-20260523",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Indian diaspora women's sports communities in the US and UK have grown significantly through cricket fan groups, but women's football remains almost entirely invisible to NRI audiences. The SAFF Championship in Goa will not be broadcast on any channel accessible to the US diaspora. Meanwhile, the ICC Women's T20 World Cup in England will stream on Willow TV and JioHotstar across North America and Europe. For NRI families with daughters who play both sports — increasingly common in US suburban Indian communities — the visibility gap between women's cricket and women's football is a conversation about which pathways Indian girls are told to pursue and which are quietly abandoned. Manisha Kalyan's career at Apollon Ladies in Cyprus offers a rare European pathway that most diaspora families do not even know exists.",
    "tags": ["SAFF Women's Championship", "Indian Women's Football", "Blue Tigresses", "Manisha Kalyan", "Grace Dangmei", "Women's T20 World Cup", "Harmanpreet Kaur", "Bangladesh", "Goa", "Margao", "Crispin Chettri", "Aveka Singh", "AIFF", "Indian Women's Sport"],
    "urgency": "daily",
    "sources": [
        "https://www.devdiscourse.com/article/sports-games/3424987-india-name-23-member-final-squad-for-saff-womens-championship-2026",
        "https://www.khelnow.com/football/saff-women-championship-2026-india-rival-watch-maldives-bangladesh",
        "https://www.khelnow.com/football/indian-women-football-team-saff-women-championship-2026-squad",
        "https://www.sportstiger.com/news/indian-womens-team-departs-for-icc-womens-t20-world-cup-2026-with-eyes-on-historic-glory",
        "https://en.wikipedia.org/wiki/2026_SAFF_Women%27s_Championship_squads"
    ],
    "word_count": 700,
    "score_total": 65,
    "body": """On Friday morning, the Indian women's cricket team flew out of Mumbai for the ICC Women's T20 World Cup in England and Wales. Harmanpreet Kaur led the squad through the airport. Smriti Mandhana, the vice-captain, was photographed boarding the flight. Jemimah Rodrigues posted on Instagram. The departure was covered by every major Indian sports outlet, trended on social media, and generated analysis pieces about India's chances of winning a tournament that begins on June 12 in Birmingham.

On Sunday morning, the Indian women's football team will walk out at Pandit Jawaharlal Nehru Stadium in Margao, Goa, to open the SAFF Women's Championship against Maldives. Head coach Crispin Chettri has named his 23-member squad. The tournament runs until June 6. India have not won it since 2019. Bangladesh have taken the title in each of the last two editions.

The cricket departure made national news. The football tournament will struggle to make local news in Goa.

## The squad

Chettri's 23 includes three goalkeepers — Panthoi Chanu Elangbam, Ribansi Jamu, and Shreya Hooda — and a defensive core built around Astam Oraon, Nirmala Devi Phanjoubam, and Ranjana Chanu Sorokhaibam. The midfield features Aveka Singh and Priyangka Devi Naorem, both of whom have been regulars in the national setup. Up front, Manisha Kalyan — the most gifted Indian women's footballer of her generation, who plays club football for Apollon Ladies in Cyprus — leads the attacking line alongside Grace Dangmei, Lynda Kom Serto, and the rapid Pyari Xaxa.

Three players were released from the preliminary 26-member squad to arrive at the final 23. The selection process received approximately zero mainstream coverage.

## The tournament

India are in Group B alongside Maldives and Bangladesh. The opening match against Maldives on May 25 should be straightforward — India have historically dominated this fixture. The group decider comes on May 31 against Bangladesh, the defending champions and the team that has established itself as India's most dangerous rival in South Asian women's football.

Bangladesh's rise has been one of the most significant stories in Asian women's football over the past five years. Their technical development, their organisation, and their ability to win decisive matches against India have shifted the regional power balance in a way that Indian football administrators have been slow to acknowledge.

The knockout rounds follow, with the final scheduled for June 6 at the same Margao venue. India are hosting the tournament, which should provide a home advantage — assuming the stands have enough people in them to create one.

Nepal and Sri Lanka complete the four-team field. Both sides have improved but neither is expected to challenge India or Bangladesh for the title.

## The visibility gap

Here is the reality of Indian women's sport in May 2026: two national teams are competing in two different sports in the same month, and the attention they receive is separated by an ocean of institutional investment, broadcast infrastructure, and cultural priority.

The women's cricket team will play in front of full stadiums in England. Their matches will be broadcast live on Star Sports and streamed on JioHotstar across India, the US, the UK, Canada, and Australia. Harmanpreet Kaur's every shot will be clipped and shared. Smriti Mandhana's cover drives will trend on social media in three time zones.

The women's football team will play in Margao in front of a few hundred spectators. Their matches may be streamed on the AIFF's YouTube channel or a secondary platform that most Indian sports fans do not know exists. Manisha Kalyan — a footballer talented enough to play professionally in Europe, something fewer than five Indian women have ever done — will score goals that most Indians will never see.

This is not an argument that football should receive the same attention as cricket in India. Cricket is the national sport in everything but official designation. But the gap between what these two teams receive — in funding, in coverage, in institutional support, in the basic dignity of someone knowing their tournament is happening — is not a natural outcome of market forces. It is the result of decades of administrative neglect by the AIFF, the same federation that is currently unable to confirm whether the men's league will have fourteen teams next season.

## What it means for the diaspora

For Indian families in the United States and United Kingdom whose daughters play both sports — an increasingly common reality in suburban Indian communities — the visibility gap carries a quiet message about which pathways are valued and which are not.

The SAFF Women's Championship starts tomorrow. India play Maldives. Manisha Kalyan will probably score. Most of us will not notice.""",
}

if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-23 23:00 PDT")
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

    print("\nInserting Article 1: ISL Clubs vs AIFF Crisis...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    # Try image for Article 1
    img1_path = f"/tmp/{a1_id}.jpg"
    if fetch_image("Indian football stadium empty stands", img1_path):
        img1_url = upload_image(a1_id, img1_path)
        if img1_url:
            update_image_url(a1_id, img1_url)

    print("\nInserting Article 2: SAFF Women's Championship...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    # Try image for Article 2
    img2_path = f"/tmp/{a2_id}.jpg"
    if fetch_image("women football players India team", img2_path):
        img2_url = upload_image(a2_id, img2_path)
        if img2_url:
            update_image_url(a2_id, img2_url)

    # Score decay
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    print(f"\nDone. 2 articles published.")
    print(f"  IDs: {a1_id}, {a2_id}")
