#!/usr/bin/env python3
"""Sports writer — 2026-05-23 11:00 PDT run: 2 articles + score decay + IPL refresh + markets."""

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
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=18)).isoformat()
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

# ── ARTICLE 1: Federation Cup 100m Record Falls Twice ──────────────
a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "India's 100-Metre National Record Fell Twice in Five Minutes. Both Sprinters Train at the Same Facility Funded by an Indian Billionaire.",
    "subheadline": "Animesh Kujur clocked 10.15 seconds at the Federation Cup in Ranchi on Friday evening — three minutes after Gurindervir Singh had broken his record with 10.17. Both train at Reliance Foundation's athletics programme, and the man who runs it says Saturday's final could go below 10.10",
    "slug": "federation-cup-100m-national-record-animesh-kujur-gurindervir-singh-ranchi-20260523",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Reliance Foundation's athletics program — bankrolled by Mukesh Ambani — is producing India's fastest humans; the CWG Glasgow qualification means Indian sprinters will compete on British soil where 1.9 million NRIs will be watching; Indian sprinting breakthrough is a story of diaspora-scale capital meeting homegrown talent",
    "tags": ["Federation Cup 2026", "Animesh Kujur", "Gurindervir Singh", "100m National Record", "Reliance Foundation", "Commonwealth Games Glasgow", "Indian Athletics", "Ranchi", "Birsa Munda Stadium", "Ancy Sojan"],
    "urgency": "breaking",
    "sources": [
        "https://www.mykhel.com/more-sports/federation-cup-2026-day-1-round-up-animesh-kujur-rewrites-national-record-twice-as-ancy-sojan-seem-434603.html",
        "https://revsportz.in/federation-cup-2026-national-record-falls-twice-in-five-minutes-in-mens-100m-semifinals/",
        "https://khelnow.com/other-sports/animesh-kujur-gurindervir-singh-100m-national-record-federation-cup-2026",
        "https://indiasportshub.com/animesh-kujur-reclaims-national-record-federation-cup-2026",
        "https://newsdive.net/gurindervir-and-animesh-clash-in-ranchi-as-100m-national-record-is-set-twice/"
    ],
    "word_count": 750,
    "score_total": 72,
    "body": """The Birsa Munda Stadium in Ranchi sits in a part of India that rarely makes the sports pages. Jharkhand's capital is cricket territory — MS Dhoni territory, specifically — and the synthetic athletics track at the stadium usually draws modest crowds for domestic meets. On Friday evening, under a breezy reddish-pink sky, it produced the most extraordinary five minutes in Indian sprinting history.

At 5:47 PM, Gurindervir Singh lined up for the first semifinal of the men's 100 metres at the Federation Cup 2026. The Punjab sprinter exploded out of the blocks and crossed the line in 10.17 seconds — one hundredth faster than the existing national record of 10.18 held by Animesh Kujur since 2025. The stadium erupted. Gurindervir Singh was India's fastest man.

He held the title for approximately three minutes.

## The response

In the very next semifinal heat, Animesh Kujur — the 22-year-old from Odisha whose record had just been taken — stepped onto the same track, in the same lane markings, under the same fading light. He ran 10.15 seconds. The national record changed hands twice before the evening session was half over.

"They're both in very good shape… probably in the best shape of their lives right now," said James Hillier, Athletics Director at Reliance Foundation, where both Kujur and Gurindervir train. Hillier added that neither sprinter was chasing a record in the semifinal. "What I told both the guys was simple — run the race you want to run in the final. Treat the semifinal as practice for that race."

The final is on Saturday. Both men will line up again. Hillier believes 10.10 is within reach.

## What the numbers mean

To understand why 10.15 matters, you need context. India has never been a sprinting nation. The men's 100m has historically been dominated by Jamaica, the United States, and increasingly West African nations. Indian sprinters were running 10.30 as recently as 2022. The gap between 10.30 and 10.15 — fifteen hundredths of a second — represents a generational leap in a discipline where improvements are typically measured in single hundredths.

Kujur's 10.15 also breaches the Athletics Federation of India's qualification standard of 10.16 seconds for the Commonwealth Games in Glasgow this July. He is now officially selected. Gurindervir's 10.17 puts him just one hundredth outside the standard, though his semifinal time is likely sufficient for selection consideration given the depth of Indian sprinting on display.

The previous meet record at the Federation Cup was 10.25, set by Manikanta Hoblidhar in 2025. Both men obliterated it.

## The Reliance Foundation pipeline

The fact that India's two fastest men train at the same facility is not a coincidence. Reliance Foundation's athletics programme, funded by Mukesh Ambani's sports infrastructure investment, has quietly assembled India's most talented sprinters and quarter-milers under one coaching setup. The programme provides international-standard coaching, sports science, and competition exposure — resources that were simply unavailable to Indian sprinters a decade ago.

The results are showing across distances. On the same Friday evening in Ranchi, five Indian quarter-milers ran sub-46 seconds in the men's 400m semifinals — the first time that has ever happened on a single day of domestic competition. Tamil Nadu's Vishal TK led the way with 45.27 seconds, the second-fastest domestic time of 2026, followed by veteran Rajesh Ramesh (45.40), rising star Jay Kumar (45.47), Manu TS (45.57), and Dharamveer Chaudhary (45.68).

The pipeline is real. The talent pool is deepening. And the results are arriving faster than anyone expected.

## Beyond the track

The women's long jump produced its own drama. Ancy Sojan, the 2023 Asian Games silver medallist, leapt a personal best of 6.75 metres — the third-best jump by an Indian woman in history and a new Federation Cup meet record. She narrowly missed the Commonwealth Games qualification mark of 6.84 metres by just nine centimetres, but her consistency across six attempts (6.47, 6.56, 6.69, 6.75, 6.68, 6.57) suggests the mark is within reach before Glasgow.

"I sacrificed a lot this year," said Ancy, who missed much of 2025 with injuries and hormonal issues. "6.84 will come soon. Today, I gave my heart out."

In the decathlon, national record holder Tejaswin Shankar amassed 4,511 points on Day 1 — his best opening day ever — with personal bests in the 100m (10.76) and long jump (7.67m). He needs the remaining five events on Saturday to push past 8,000 points, which would be a landmark for Indian multi-event athletics.

## What this means for Glasgow — and for the diaspora

The Commonwealth Games in Glasgow start on July 23, and India's athletics contingent is looking stronger than it has in years. For the estimated 1.9 million people of Indian origin living in the United Kingdom, Glasgow will be the rare major multi-sport event where Indian athletes compete on British soil. The Birsa Munda Stadium is 4,800 miles from Hampden Park, but Friday evening's record-breaking session brought them closer.

The 100m final is Saturday evening. If Kujur and Gurindervir produce anything close to their semifinal form, Indian sprinting will have announced itself to the world — not from a global championship, but from a domestic meet in Ranchi, on a track that most of the country didn't know existed.""",
}

# ── ARTICLE 2: India Women Depart for T20 World Cup ────────────────
a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "India's Women Left Mumbai This Morning With One World Cup Trophy in Their Cabinet and an Empty Space Where Another Should Be.",
    "subheadline": "Harmanpreet Kaur's squad flew to England on Saturday for the ICC Women's T20 World Cup — the one title that has eluded them despite winning the ODI crown last year. Four players will experience their first global tournament, and the opener against Pakistan in Bristol on June 14 is already sold out",
    "slug": "india-women-t20-world-cup-2026-departure-england-harmanpreet-kaur-20260523",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "The tournament is in England — home to the UK's 1.9 million-strong Indian diaspora; India vs Pakistan in Bristol guarantees NRI crowds; Smriti Mandhana's WPL form makes her cricket's most marketable woman in the diaspora; NRI families who followed the ODI World Cup win will now have a home tournament to attend in person",
    "tags": ["India Women Cricket", "T20 World Cup 2026", "Harmanpreet Kaur", "Smriti Mandhana", "ICC", "England", "Pakistan", "Nandani Sharma", "WPL", "Women's Cricket", "Bristol"],
    "urgency": "daily",
    "sources": [
        "https://www.insidesport.in/cricket/this-team-is-very-hungry-smriti-mandhana-on-india-women-ahead-of-icc-womens-t20-world-cup-2026hungry-india-eye-womens-t20-world-cup-title-after-odi-glory-smriti-mandhana-sheds-light-on-teams-mind/",
        "https://www.icc-cricket.com/news/kaur-led-india-chase-another-world-cup-dream-women-t20-wc-2026",
        "https://wisden.com/stories/news-stories/womens-t20-world-cup-2026-squads",
        "https://cricket.com.au/news/all-the-womens-t20-world-cup-2026-squads-as-they-drop",
        "https://newkerala.com/news/india-team-leaves-for-england-t20-wc-2026"
    ],
    "word_count": 720,
    "score_total": 65,
    "body": """At 7:30 on Saturday morning, the Indian women's cricket team walked through the departure gates at Chhatrapati Shivaji Maharaj International Airport in Mumbai, rolling their kit bags toward a flight to London. They were photographed by ANI, waved at by a small group of fans, and barely covered by the morning sports bulletins — which were, predictably, consumed by the IPL playoff race.

This is the paradox of Indian women's cricket in 2026. The team that won India's first-ever ICC Women's ODI World Cup last year — beating Australia in the final — boards a plane to defend that momentum at the T20 World Cup, and the nation barely notices because Virat Kohli refused a handshake 18 hours earlier.

They notice. They always have. And this squad is built to make sure the noise follows them to England.

## The squad

Harmanpreet Kaur leads the 15-member squad as captain, with Smriti Mandhana as vice-captain. The core is experienced and battle-tested: Shafali Verma's power hitting at the top, Jemimah Rodrigues' ability to rotate strike in the middle overs, Deepti Sharma's all-round reliability, and Richa Ghosh's finishing behind the stumps.

The bowling attack is led by Renuka Singh, whose swing in English conditions could be devastating, and Arundhati Reddy, who has been consistently hostile in the WPL. Shreyanka Patil provides the spin option alongside Radha Yadav, whose left-arm variety was crucial in the ODI World Cup campaign.

Four players — Bharti Fulmali, Nandani Sharma, Shree Charani, and Kranti Gaud — will experience their first ICC event. All four earned their places through the Women's Premier League, a tournament that has done more for the depth of Indian women's cricket in three seasons than any development programme managed in the previous two decades.

"What excites me about this squad is the balance we have," Harmanpreet said. "There is talent, fearlessness, and a good mix of experience and youth."

## The missing trophy

India have never won the Women's T20 World Cup. They came agonisingly close in 2020, reaching the final in Melbourne before Australia dismantled them in front of 86,174 people at the MCG. They have reached the semifinal stage multiple times since. The tournament has been their white whale.

The ODI World Cup victory in 2025 changed the psychological equation. This is no longer a team that freezes in knockout stages. Harmanpreet's squad won three consecutive high-pressure matches to lift the 50-over trophy — including the final against Australia, which required chasing down 268 at home in Mumbai with two wickets in hand. That experience, more than any net session, is what this T20 campaign will draw on.

"In cricket, it is always about how you start fresh," Mandhana said before departure. "But more than anything, I feel this team is really hungry. Everyone seems very hungry to do the right things."

## England conditions and the schedule

India will play three T20Is against England from May 28 to June 2 as preparation before the World Cup begins on June 12. The bilateral series gives them time to adjust to English conditions — the lateral movement, the longer twilights, the Dukes-ball-adjacent white-ball behaviour — before the stakes become existential.

In the World Cup, India are in Group B alongside Pakistan, Netherlands, South Africa, and Bangladesh. The opener against Pakistan on June 14 in Bristol is the headline fixture. India-Pakistan in any format, in any gender, on English soil — where both diasporas are enormous — is the kind of event that transcends the sport.

The group is navigable but not simple. South Africa, led by Laura Wolvaardt, have been one of the most improved teams in women's cricket over the past two years. Bangladesh, under Nigar Sultana, upset India in the Asia Cup last year. There are no easy matches at a World Cup.

## Why this matters for NRI cricket fans

The Women's T20 World Cup in England is a rare opportunity for the Indian diaspora in the UK to watch their team compete in a global tournament without adjusting to subcontinental time zones. Bristol, Birmingham, Manchester, and London — all host cities — have significant Indian populations. The India-Pakistan match in Bristol will draw NRI families from across the southwest, and the semifinal and final at The Oval in London will be walking distance from some of the largest South Asian communities in Europe.

For years, the women's game was something Indian families followed on muted television screens in the background of weekend lunches. The ODI World Cup victory changed that. The T20 World Cup in England will test whether the change sticks — whether the diaspora shows up not just for the final, but for the group stage, the warm-ups, the moments when the cameras aren't pointing.

The team boarded the flight on Saturday morning. The IPL trended above them. That will change if they bring the trophy home.""",
}

if __name__ == "__main__":
    # Insert articles
    print("=" * 60)
    print("Sports Writer — 2026-05-23 11:00 PDT")
    print("=" * 60)

    print("\nInserting Article 1: Federation Cup 100m record drama...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    print("\nInserting Article 2: India Women depart for T20 World Cup...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    # Upload images
    img1_path = "/home/hatch/workspace/imagine_media/imagine-editorial-sports-photography-a-0-1779559293406-0.jpg"
    img2_path = "/home/hatch/workspace/imagine_media/imagine-editorial-sports-photography-t-0.jpg"

    print("\nUploading images...")
    if os.path.exists(img1_path):
        url1 = upload_image(a1_id, img1_path)
        if url1:
            update_image_url(a1_id, url1)
    else:
        print(f"  WARN: img1 not found at {img1_path}")

    if os.path.exists(img2_path):
        url2 = upload_image(a2_id, img2_path)
        if url2:
            update_image_url(a2_id, url2)
    else:
        print(f"  WARN: img2 not found at {img2_path}")

    # Score decay
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    print(f"\nDone. 2 articles published.")
    print(f"  IDs: {a1_id}, {a2_id}")
