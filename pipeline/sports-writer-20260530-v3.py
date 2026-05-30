#!/usr/bin/env python3
"""Sports writer for The Videshi — 2026-05-30 evening run (v3, complete)."""

import json, os, sys, time, uuid, subprocess
import requests
import urllib.parse
from datetime import datetime, timezone

# ── env ─────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser("~/workspace/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── helpers ─────────────────────────────────────────────────────────────
def fetch_pexels_image(query, fallback_query=None):
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            for p in data.get("photos", []):
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def upload_to_supabase(img_url, filename):
    try:
        r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Download issue ({r.status_code}, {len(r.content)} bytes)")
            # For permanent sources, use direct URL
            if any(d in img_url for d in ["upload.wikimedia.org", "images.pexels.com"]):
                return img_url
            return None
        ct = r.headers.get("Content-Type", "image/jpeg")
        if not ct.startswith("image/"):
            ct = "image/jpeg"
        up = requests.post(
            f"{SB_URL}/storage/v1/object/article-images/{filename}",
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                     "Content-Type": ct, "x-upsert": "true"},
            data=r.content, timeout=30,
        )
        if up.status_code in (200, 201):
            pub = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded: {pub[:80]}...")
            return pub
        print(f"  ⚠ Upload failed ({up.status_code})")
        if any(d in img_url for d in ["upload.wikimedia.org", "images.pexels.com"]):
            return img_url
        return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        if any(d in img_url for d in ["upload.wikimedia.org", "images.pexels.com"]):
            return img_url
        return None


def create_topic(canonical_title, category="sports", urgency="daily"):
    topic = {
        "canonical_title": canonical_title,
        "category": category,
        "vertical": "sport",
        "urgency": urgency,
        "status": "approved",
        "score_total": 70,
        "score_diaspora": 7,
        "score_significance": 7,
        "score_recency": 8,
        "score_source_avail": 7,
        "signal_count": 3,
    }
    r = requests.post(f"{SB_URL}/rest/v1/p2_topics", headers=HEADERS, json=topic, timeout=15)
    if r.status_code in (200, 201):
        result = r.json()
        tid = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  ✓ Topic created: {canonical_title[:50]}... (id={tid})")
        return tid
    print(f"  ✗ Topic failed ({r.status_code}): {r.text[:200]}")
    return None


def publish_article(art):
    word_count = len(art["body"].split())
    art["word_count"] = word_count
    r = requests.post(f"{SB_URL}/rest/v1/p2_articles", headers=HEADERS, json=art, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        aid = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  ✓ Published: {art['headline'][:60]}... (id={aid})")
        return aid
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
    return None


# ── ARTICLES ────────────────────────────────────────────────────────────
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
success = 0

# ═══════════════════════════════════════════════════════════════════════
# Article 1: Champions League Final Result
# ═══════════════════════════════════════════════════════════════════════
print("\n═══ Article 1: Champions League Final ═══")

tid1 = create_topic("PSG retain Champions League with penalty shootout win over Arsenal in Budapest")
img1_url = f"{SB_URL}/storage/v1/object/public/article-images/psg-retain-champions-league-penalties-arsenal-heartbreak-gabriel-miss-budapest-20260530.jpg"

art1 = {
    "topic_id": tid1,
    "headline": "Gabriel's Penalty Sailed Over the Bar. PSG Have Won Back-to-Back Champions League Titles.",
    "subheadline": "Arsenal took the lead inside six minutes in Budapest but couldn't hold it. The first club to retain the Champions League since Real Madrid has done it from Paris.",
    "slug": "psg-retain-champions-league-penalties-arsenal-heartbreak-gabriel-miss-budapest-20260530",
    "category": "sports",
    "vertical": "sport",
    "urgency": "daily",
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "is_featured": False,
    "sources": json.dumps(["Reuters", "Fox Sports", "The Times", "USA Today"]),
    "tags": ["Champions League", "PSG", "Arsenal", "Gabriel", "Penalty Shootout", "Budapest", "Luis Enrique", "Kai Havertz"],
    "diaspora_angle": "For millions of NRI football fans following the Premier League and European football, Arsenal's penalty heartbreak in Budapest and PSG's dynasty-forging back-to-back titles happened at prime-time IST. With the FIFA World Cup starting in America in twelve days, the stakes are personal for diaspora fans who will watch many of these players at venues across the US.",
    "image_url": img1_url,
    "image_attribution": "Pexels",
    "body": """Kai Havertz gave Arsenal the perfect start. Six minutes in, the German forward broke clear and beat Matvei Safonov with a composed finish at the Puskas Arena in Budapest. For a moment, the Premier League champions looked set to complete the domestic-European double that has eluded the club for its entire 138-year existence.

PSG absorbed the early blow. Luis Enrique's side dominated possession through the middle third, moving the ball with the patient, suffocating rhythm that has become their trademark under the Spanish coach. But Arsenal's defensive structure — marshalled by William Saliba and Gabriel Magalhães — held firm through the first half.

## Dembélé's Equaliser Changed Everything

The turning point came in the 65th minute. Ousmane Dembélé earned a penalty and converted it himself, sending David Raya the wrong way. At 1-1, the final shifted into a tense, tactical battle. Neither side could find a winner through the remaining 25 minutes of normal time, and extra time produced no goals despite both teams pushing cautiously forward.

## The Penalty Drama

The shootout was brutal. Gonçalo Ramos opened for PSG with a confident finish. Viktor Gyökeres replied for Arsenal. Then Désiré Doué made it 2-1 before Eberechi Eze, Arsenal's substitute, stuttered in his run-up and sent his kick wide. Raya kept Arsenal alive with a save from Nuno Mendes, and Declan Rice converted to level it at 2-2. Achraf Hakimi restored PSG's lead at 3-2. Gabriel Martinelli struck a superb penalty into the top corner to make it 3-3.

Then came the decisive moment. Lucas Beraldo, PSG's young Brazilian defender, slotted his kick into the corner. Gabriel — who had been magnificent across 120 minutes of defending — stepped up needing to score. He blasted it over the crossbar. The Puskas Arena erupted on one side and fell silent on the other.

## A Dynasty Is Forged

PSG are the first club to win back-to-back Champions League titles since Real Madrid completed their three-year reign from 2016 to 2018. For a club long dismissed as glamorous underachievers despite their Qatari-backed wealth, this is validation of the highest order.

"It's stronger than last year because we knew before the match just how difficult it would be to play against Arsenal," Luis Enrique said. "As a club and a city, it's incredible to win."

Joao Neves, PSG's young midfielder, called it "the best decision I've ever made in my life" — a reference to his summer transfer from Benfica. Marquinhos, the captain, spoke of the mentality his coach had instilled: "From the very first day of this season the coach said it's hard to win, and winning twice is even more difficult."

## The NRI Perspective

For millions of NRI football fans who stayed up or tuned in during the Saturday evening kickoff — prime-time IST, noon on the American east coast — this was a final worth every minute. Arsenal's run through the Champions League had captured the imagination of the Premier League's massive Indian following, but PSG's clinical nerve under pressure was the difference.

The players now scatter to their national teams. The 2026 FIFA World Cup kicks off in the United States on June 11, barely twelve days from now. For Arsenal's England contingent — Rice, Saka, Havertz — the transition from heartbreak to tournament football begins immediately. For PSG's multinational squad, including Marquinhos, Ramos, and Hakimi, the celebration will be brief before World Cup duty calls.

Arsenal manager Mikel Arteta did not speak to media immediately after the match. Rice, visibly emotional, offered perspective: "It's gutting. It's devastating to lose a Champions League final on penalties. But we try to take a lot of perspective from how far we've come as a group. An incredible season. Our 61st game in all competitions tonight."

On the missed penalties from Gabriel and Eze, Rice added: "We love them. We're with them. Without them two this season, we wouldn't have won the Premier League."

Gabriel was comforted on the pitch by his Brazil teammate and PSG captain Marquinhos. He had been immense for 120 minutes. The last kick was the only thing that went wrong.""",
}
if tid1:
    aid1 = publish_article(art1)
    if aid1:
        success += 1

# ═══════════════════════════════════════════════════════════════════════
# Article 2: Norway Chess — Pragg vs Gukesh
# ═══════════════════════════════════════════════════════════════════════
print("\n═══ Article 2: Norway Chess — Pragg vs Gukesh ═══")

tid2 = create_topic("Norway Chess Round 5: Praggnanandhaa faces Gukesh in all-Indian showdown")

# Wikipedia image — try with delay
time.sleep(2)
img2 = fetch_wikipedia_person_image("Praggnanandhaa Rameshbabu")
if not img2:
    time.sleep(1)
    img2 = fetch_wikipedia_person_image("Gukesh Dommaraju")
if img2:
    img2_final = upload_to_supabase(img2, "norway-chess-2026-pragg-vs-gukesh-round-5-all-india-firouzja-leads-oslo.jpg")
    img2_attr = "Wikimedia Commons"
else:
    img2_raw = fetch_pexels_image("chess grandmaster tournament", "chess board competition")
    img2_final = upload_to_supabase(img2_raw, "norway-chess-2026-pragg-vs-gukesh-round-5-all-india-firouzja-leads-oslo.jpg") if img2_raw else None
    img2_attr = "Pexels" if img2_final else None

art2 = {
    "topic_id": tid2,
    "headline": "Pragg Against Gukesh in Oslo. India's Two Finest Chess Players Meet at Norway Chess Round 5.",
    "subheadline": "Praggnanandhaa is second. Gukesh is last. Firouzja leads by two and a half points. The world champion needs a result against his compatriot.",
    "slug": "norway-chess-2026-pragg-vs-gukesh-round-5-all-india-firouzja-leads-oslo",
    "category": "sports",
    "vertical": "sport",
    "urgency": "daily",
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "is_featured": False,
    "sources": json.dumps(["ChessBase", "Norway Chess", "Checkmate Daily"]),
    "tags": ["Chess", "Norway Chess 2026", "Praggnanandhaa", "Gukesh", "Magnus Carlsen", "Firouzja", "Indian Chess", "World Champion"],
    "diaspora_angle": "Two Indians at the world's strongest chess tournament — Pragg in second place, world champion Gukesh in last — face each other in Round 5. India now has two elite players in the world's top ten, a generational shift that NRI chess fans are watching with pride. Pragg's sister Vaishali won the Women's Candidates earlier this year. The Rameshbabu family's remarkable year is reshaping how the world sees Indian chess.",
    "image_url": img2_final,
    "image_attribution": img2_attr,
    "body": """The fifth round of Norway Chess 2026 pits two Indians against each other in what has become the most compelling rivalry in contemporary chess. Praggnanandhaa Rameshbabu, twenty years old and sitting second in the standings, faces world champion Gukesh Dommaraju, who at twenty has endured a difficult tournament and sits last.

The contrast in their Norway Chess campaigns could not be starker. Pragg has won two Armageddon tiebreakers and drawn his classical games with composure, accumulating six points from four rounds. He has looked assured and tactically sharp, particularly in rapid play. Gukesh, meanwhile, has managed only 3.5 points after four rounds, his classical loss to Magnus Carlsen in Round 4 dropping him to the bottom of the six-player field.

## Carlsen's Victory Over Gukesh

Round 4 was the decisive blow to Gukesh's campaign. Playing black, Carlsen secured his first classical win of the tournament against the world champion — a result that continued the tournament's pattern of exactly one decisive classical game per round. For Carlsen, who had himself lost classical games to Firouzja and Pragg in earlier rounds, the victory was a crucial course correction. The seven-time Norway Chess champion climbed to fourth place with 4.5 points.

The remaining two games in Round 4 ended drawn in classical chess and were followed by Armageddon deciders. Wesley So handed Firouzja his first match loss of the tournament, winning their rapid-play decider. Pragg also won in Armageddon, defeating Vincent Keymer with the black pieces.

## Firouzja's Commanding Lead

The player both Indians are chasing is Alireza Firouzja of France. The 23-year-old leads with 8.5 points after four rounds — a commanding 2.5-point gap over Pragg. Firouzja suffered his first match loss of the tournament in Round 4, but his lead remains substantial after winning classical games in Rounds 1 and 2 and adding an Armageddon victory in Round 3.

Even with the Round 4 setback, Firouzja faces Keymer in Round 5 and needs just steady results to maintain his advantage heading into the second half of the tournament.

## What This Means for Indian Chess

The Pragg-Gukesh matchup carries weight beyond Norway. Pragg qualified for the 2026 Candidates Tournament through the FIDE Circuit. His sister Vaishali won the Women's Candidates earlier this year. The Rameshbabu family is having a remarkable year. A strong result against the world champion would further cement Pragg's credentials as the most dangerous challenger in the next world championship cycle.

For Gukesh, the stakes are different. The youngest undisputed world champion in history came to Norway after a strong start to 2026, but this tournament has exposed the challenge of defending the crown while facing elite opposition in every round. He cannot afford another loss. A classical win over Pragg would reinvigorate his campaign; a defeat would leave him with a mountain to climb in the remaining rounds.

Their head-to-head record in classical chess is competitive. Both have won games against each other in recent years, and both know each other's preparation deeply — a product of their shared training environment in Indian chess. This familiarity can make their encounters unpredictable.

## Standings After Round 4

The full standings read: Firouzja 8.5, Pragg 6, So 5.5, Carlsen 4.5, Keymer 4, Gukesh 3.5. With six rounds remaining, the tournament is far from decided — but the all-Indian clash in Round 5 will shape the narrative for both players going forward.

## How NRIs Can Watch

Norway Chess streams all games live on its official YouTube channel and website, with commentary beginning at 5:00 PM local time in Stavanger (8:30 PM IST, 11:00 AM ET). The Pragg-Gukesh encounter will be the marquee matchup of the round. Chess.com India provides Hindi commentary.""",
}
if tid2:
    aid2 = publish_article(art2)
    if aid2:
        success += 1

# ═══════════════════════════════════════════════════════════════════════
# Article 3: SAFF Women's Championship — India vs Bangladesh
# ═══════════════════════════════════════════════════════════════════════
print("\n═══ Article 3: SAFF Women's Championship ═══")

tid3 = create_topic("India face Bangladesh in SAFF Women's Championship group decider in Goa")
img3_url = f"{SB_URL}/storage/v1/object/public/article-images/india-vs-bangladesh-saff-women-championship-2026-goa-group-decider-sunday.jpg"

art3 = {
    "topic_id": tid3,
    "headline": "India Have Not Beaten Bangladesh in Two Years. They Play Them in Goa Tomorrow With the Group on the Line.",
    "subheadline": "Bangladesh have scored six and conceded one in their last two matches against India's women. Sunday's SAFF Championship group match in Margao could decide who tops the group.",
    "slug": "india-vs-bangladesh-saff-women-championship-2026-goa-group-decider-sunday",
    "category": "sports",
    "vertical": "sport",
    "urgency": "daily",
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "is_featured": False,
    "sources": json.dumps(["SAFF", "Khel Now", "AIFF"]),
    "tags": ["India Women Football", "SAFF Championship 2026", "Bangladesh", "Goa", "Margao", "Women's Football", "FanCode"],
    "diaspora_angle": "India's women's football team plays in front of home crowds at the SAFF Championship in Goa — one of the few opportunities for NRI fans to follow the team in a competitive home tournament. India have not won the SAFF Women's Championship in six years, and the Bangladesh match is the first genuine test of their campaign. The match streams on FanCode at 7:30 PM IST.",
    "image_url": img3_url,
    "image_attribution": "Pexels",
    "body": """India's senior women's football team face Bangladesh at the Jawaharlal Nehru Stadium in Margao, Goa on Sunday evening in a match that will decide the Group B standings at the 2026 SAFF Women's Championship. The kickoff is at 7:30 PM IST, with the match streamed live on FanCode.

Both teams have won their opening group matches. India dismantled Maldives 11-0 on May 25, a result that was as comprehensive as it was expected. Bangladesh were equally efficient in their own Maldives fixture, winning 4-2 on May 28. With Maldives eliminated on zero points from two defeats, Sunday's match is effectively a group decider.

## The Bangladesh Problem

The statistic that hangs over this fixture is stark: Bangladesh have won their last two meetings against India's women, scoring six goals and conceding just one across those matches. For a programme that has long been the regional powerhouse — India have won the SAFF Women's Championship five times — the recent record against Bangladesh represents a genuine shift in the subcontinental balance of power.

Bangladesh's rise has been steady and well-coached. Their 4-2 win over Maldives showed clinical finishing from Siddiqui, Marma, Prity, and Kisku, with goals spread across different phases of the game. This is not a one-player team. Their defensive organisation has been the primary reason for India's struggles in recent encounters.

## India's Eleven-Goal Statement

India's 11-0 demolition of Maldives was built on collective ruthlessness. Naorem opened the scoring inside eleven minutes and added another in the 17th. Pyari Xaxa extended the lead in the 28th minute. The goals kept coming — A. Singh scored a hat-trick, Dangmei, Shirvoikar, and Basfore all found the net. By the final whistle, eleven different phases of play had produced eleven goals. The margin was never in doubt, but the coaching staff will know that the real test was always going to be Bangladesh, not Maldives.

The Indian squad includes several players with experience in the Indian Women's League and exposure to competitive international windows. But execution against organised defences — rather than the overmatched Maldives — remains the question.

## More Than a Group Match

India are the highest-ranked team in the tournament at 69th in the FIFA World Rankings. Bangladesh are ranked considerably lower, but regional rankings have proven unreliable predictors of SAFF tournament results. The head-to-head record is the form guide that matters here.

A win for India would confirm them as group winners and set up a favourable knockout-stage path. A draw or defeat would hand Bangladesh the advantage and force India into a potentially harder route to the title.

## Six Years Without the Trophy

India have not won the SAFF Women's Championship since 2019 — the longest drought in the tournament's history for a team that once dominated the competition so thoroughly that the question was not whether India would win, but by how many goals.

The landscape has changed. Bangladesh's investment in women's football infrastructure, coaching development, and competitive fixtures has produced a team that is no longer content to be India's regional understudy. The Goan crowd will play its part — attendance was only 225 for the Maldives match, but a competitive India-Bangladesh fixture should draw more — but the result will come down to whether India can solve the defensive puzzle that Bangladesh have set in their last two meetings.

## How to Watch

The match kicks off at 7:30 PM IST (10:00 AM ET, 7:00 AM PT) on Sunday, May 31, at the Jawaharlal Nehru Stadium in Margao, Goa. Live streaming is available on FanCode.""",
}
if tid3:
    aid3 = publish_article(art3)
    if aid3:
        success += 1

print(f"\n═══ Done: {success}/3 articles published ═══")
