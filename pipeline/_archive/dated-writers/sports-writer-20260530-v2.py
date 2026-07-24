#!/usr/bin/env python3
"""Sports writer for The Videshi — 2026-05-30 evening run (fixed)."""

import json, os, sys, time, uuid, re, subprocess
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
            # Prefer thumbnail (330px, always works), then originalimage
            thumb = data.get("thumbnail", {}).get("source")
            original = data.get("originalimage", {}).get("source")
            img = thumb or original  # Use thumbnail first — more reliable
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:100]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                [
                    "curl", "-sS",
                    f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                    "-H", f"Authorization: {PEXELS_KEY}",
                ],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:100]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_image_to_supabase(img_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Image download failed ({r.status_code}): {img_url[:80]}")
            # If it's a permanent source (Wikipedia, Pexels), use direct URL
            if "upload.wikimedia.org" in img_url or "images.pexels.com" in img_url:
                return img_url
            return None
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if not content_type.startswith("image/"):
            content_type = "image/jpeg"
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small ({len(r.content)} bytes), skipping upload")
            if "upload.wikimedia.org" in img_url or "images.pexels.com" in img_url:
                return img_url
            return None

        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        up = requests.post(
            upload_url,
            headers={
                "apikey": SB_KEY,
                "Authorization": f"Bearer {SB_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            data=r.content,
            timeout=30,
        )
        if up.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Supabase upload failed ({up.status_code}): {up.text[:200]}")
            # Fall back to direct URL for permanent sources
            if "upload.wikimedia.org" in img_url or "images.pexels.com" in img_url:
                return img_url
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        if "upload.wikimedia.org" in img_url or "images.pexels.com" in img_url:
            return img_url
        return None


def sb_insert(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30,
    )
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  ✓ Published: {article['headline'][:60]}... (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ── ARTICLES ────────────────────────────────────────────────────────────

articles = []
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ─── Article 1: Champions League Final Result ───────────────────────
print("\n═══ Article 1: Champions League Final — PSG Retain Title ═══")

art1_slug = "psg-retain-champions-league-penalties-arsenal-heartbreak-gabriel-miss-budapest-20260530"
art1_headline = "Gabriel's Penalty Sailed Over the Bar. PSG Have Won Back-to-Back Champions League Titles."
art1_subheadline = "Arsenal took the lead inside six minutes in Budapest but couldn't hold it. The first club to retain the Champions League since Real Madrid has done it from Paris."

art1_body = """Kai Havertz gave Arsenal the perfect start. Six minutes in, the German forward broke clear and beat Matvei Safonov with a composed finish at the Puskas Arena in Budapest. For a moment, the Premier League champions looked set to complete the domestic-European double that has eluded the club for its entire 138-year existence.

PSG absorbed the early blow. Luis Enrique's side dominated possession through the middle third, moving the ball with the patient, suffocating rhythm that has become their trademark under the Spanish coach. But Arsenal's defensive structure — marshalled by William Saliba and Gabriel Magalhães — held firm through the first half.

## Dembélé's Equaliser Changed Everything

The turning point came in the 65th minute. Ousmane Dembélé earned a penalty and converted it himself, sending David Raya the wrong way. At 1-1, the final shifted into a tense, tactical battle. Neither side could find a winner through the remaining 25 minutes of normal time, and extra time produced no goals despite both teams pushing cautiously forward.

## The Penalty Drama

The shootout was brutal. Gonçalo Ramos opened for PSG with a confident finish. Viktor Gyökeres replied for Arsenal. Then Désiré Doué made it 2-1 before Eberechi Eze, Arsenal's substitute, stuttered in his run-up and sent his kick wide. Raya kept Arsenal alive with a save from Nuno Mendes, and Declan Rice converted. Achraf Hakimi restored PSG's lead at 3-2. Gabriel Martinelli struck a superb penalty into the top corner to make it 3-3.

Then came the decisive moment. Lucas Beraldo, PSG's young Brazilian defender, slotted his kick into the corner. Gabriel — who had been magnificent across 120 minutes of defending — stepped up needing to score. He blasted it over the crossbar. The Puskas Arena erupted on one side and fell silent on the other.

## A Dynasty Is Forged

PSG are the first club to win back-to-back Champions League titles since Real Madrid completed their three-year reign from 2016 to 2018. For a club long dismissed as glamorous underachievers despite their Qatari-backed wealth, this is validation of the highest order.

"It's stronger than last year because we knew before the match just how difficult it would be to play against Arsenal," Luis Enrique said. "As a club and a city, it's incredible to win."

## The Diaspora Angle

For millions of NRI football fans who stayed up for the Saturday evening kickoff — prime-time IST, noon on the American east coast — this was a final worth every minute. Arsenal's run had captured the imagination of the Premier League's massive Indian following, but PSG's clinical nerve under pressure was the difference.

The players now scatter to their national teams. The 2026 FIFA World Cup kicks off in the United States on June 11, barely twelve days from now. For Arsenal's England contingent — Rice, Saka, Havertz — the transition from heartbreak to tournament football begins immediately. For PSG's multinational squad, including Marquinhos, Ramos, and Hakimi, the celebration will be brief before World Cup duty calls.

Arsenal manager Mikel Arteta did not speak to media immediately after the match. Rice, visibly emotional, offered perspective: "It's gutting. It's devastating to lose a Champions League final on penalties. But we try to take a lot of perspective from how far we've come as a group. It's been an incredible season."

Gabriel was comforted on the pitch by his Brazil teammate and PSG captain Marquinhos. He had been immense for 120 minutes. The last kick was the only thing that went wrong.

**Sources:** Reuters, Fox Sports, The Times, USA Today"""

# Image already uploaded to Supabase from first run
img1_final = f"{SB_URL}/storage/v1/object/public/article-images/{art1_slug}.jpg"

art1 = {
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "slug": art1_slug,
    "category": "sports",
    "status": "published",
    "published_at": now,
    "sources": "Reuters, Fox Sports, The Times, USA Today",
    "image_url": img1_final,
    "image_attribution": "Pexels",
}
articles.append(art1)


# ─── Article 2: Norway Chess — Pragg vs Gukesh ──────────────────────
print("\n═══ Article 2: Norway Chess — Pragg vs Gukesh ═══")

art2_slug = "norway-chess-2026-pragg-vs-gukesh-round-5-all-india-firouzja-leads-oslo"
art2_headline = "Pragg Against Gukesh in Oslo. India's Two Finest Chess Players Meet at Norway Chess Round 5."
art2_subheadline = "Praggnanandhaa is second. Gukesh is last. Firouzja leads by two and a half points. The world champion needs a result against his compatriot."

art2_body = """The fifth round of Norway Chess 2026 pits two Indians against each other in what has become the most compelling rivalry in contemporary chess. Praggnanandhaa Rameshbabu, twenty years old and sitting second in the standings, faces world champion Gukesh Dommaraju, who at twenty has endured a difficult tournament and sits last.

The contrast in their Norway Chess campaigns could not be starker. Pragg has won two Armageddon tiebreakers and drawn his classical games with composure, accumulating six points from four rounds. He has looked assured and tactically sharp, particularly in rapid play. Gukesh, meanwhile, has managed only 3.5 points after four rounds, his classical loss to Magnus Carlsen in Round 4 dropping him to the bottom of the six-player field.

## Carlsen's Victory Over Gukesh

Round 4 was the decisive blow to Gukesh's campaign. Playing black, Carlsen secured his first classical win of the tournament against the world champion — a result that continued the tournament's pattern of exactly one decisive classical game per round. For Carlsen, who had himself lost classical games to Firouzja and Pragg in earlier rounds, the victory was a crucial course correction.

"It was a good game from my side," Carlsen said simply. The seven-time Norway Chess champion climbed to fourth place with 4.5 points.

## Firouzja's Commanding Lead

The player both Indians are chasing is Alireza Firouzja of France. The 23-year-old leads with 8.5 points after four rounds — a commanding 2.5-point gap over Pragg. Firouzja suffered his first match loss of the tournament in Round 4, losing an Armageddon tiebreaker to Wesley So after their classical game was drawn, but his lead remains substantial.

Firouzja has been the most consistent performer, winning classical games in Rounds 1 and 2 and adding an Armageddon victory in Round 3. Even with the Round 4 setback, he needs just steady results to maintain his advantage.

## What This Means for Indian Chess

The Pragg-Gukesh matchup carries weight beyond Norway. Pragg qualified for the 2026 Candidates Tournament through the FIDE Circuit. His sister Vaishali won the Women's Candidates. The Rameshbabu family is having a remarkable year. A strong result against the world champion would further cement Pragg's credentials as the most dangerous challenger in the next world championship cycle.

For Gukesh, the stakes are different. The youngest undisputed world champion in history came to Norway after a strong start to 2026, but this tournament has exposed the challenge of defending the crown while facing elite opposition in every round. He cannot afford another loss. A classical win over Pragg would reinvigorate his campaign; a defeat would leave him needing significant results in the final rounds.

## Standings After Round 4

The full standings read: Firouzja 8.5, Pragg 6, So 5.5, Carlsen 4.5, Keymer 4, Gukesh 3.5. With six rounds remaining, the tournament is far from decided — but the all-Indian clash in Round 5 will shape the narrative for both players going forward.

## How NRIs Can Watch

Norway Chess streams all games live on its official YouTube channel and website, with commentary beginning at 5:00 PM local time (8:30 PM IST, 11:00 AM ET). The Pragg-Gukesh encounter will be the marquee matchup of the round.

**Sources:** ChessBase, Norway Chess, Checkmate Daily"""

# Try Wikipedia image for Praggnanandhaa with thumbnail (330px, more reliable)
time.sleep(1)  # brief delay to avoid rate limiting
img2 = fetch_wikipedia_person_image("Praggnanandhaa Rameshbabu")
if not img2:
    img2 = fetch_wikipedia_person_image("Gukesh Dommaraju")
if img2:
    img2_final = upload_image_to_supabase(img2, f"{art2_slug}.jpg")
    img2_attribution = "Wikimedia Commons"
else:
    img2_final = fetch_pexels_image("chess grandmaster tournament", "chess board competition")
    if img2_final:
        img2_final = upload_image_to_supabase(img2_final, f"{art2_slug}.jpg")
    img2_attribution = "Pexels" if img2_final else None

art2 = {
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "slug": art2_slug,
    "category": "sports",
    "status": "published",
    "published_at": now,
    "sources": "ChessBase, Norway Chess, Checkmate Daily",
    "image_url": img2_final,
    "image_attribution": img2_attribution,
}
articles.append(art2)


# ─── Article 3: SAFF Women's Championship — India vs Bangladesh ─────
print("\n═══ Article 3: SAFF Women's Championship ═══")

art3_slug = "india-vs-bangladesh-saff-women-championship-2026-goa-group-decider-sunday"
art3_headline = "India Have Not Beaten Bangladesh in Two Years. They Play Them in Goa Tomorrow With the Group on the Line."
art3_subheadline = "Bangladesh have scored six and conceded one in their last two matches against India's women. Sunday's SAFF Championship group match in Margao could decide who tops the group."

art3_body = """India's senior women's football team face Bangladesh at the Jawaharlal Nehru Stadium in Margao, Goa on Sunday evening in a match that will decide the Group B standings at the 2026 SAFF Women's Championship. The kickoff is at 7:30 PM IST, with the match streamed live on FanCode.

Both teams have won their opening group matches. India dismantled Maldives 11-0 on May 25, a result that was as comprehensive as it was expected. Bangladesh were equally efficient in their own Maldives fixture, winning 4-2 on May 28. With Maldives eliminated on zero points from two defeats, Sunday's match is effectively a group decider.

## The Bangladesh Problem

The statistic that hangs over this fixture is stark: Bangladesh have won their last two meetings against India's women, scoring six goals and conceding just one across those matches. For a programme that has long been the regional powerhouse — India have won the SAFF Women's Championship five times — the recent record against Bangladesh represents a genuine shift in the subcontinental balance of power.

Bangladesh's rise has been steady and well-coached. Their 4-2 win over Maldives showed clinical finishing from Siddiqui, Marma, Prity, and Kisku, with goals spread across different phases of the game. This is not a one-player team. Their defensive organisation has been the primary reason for India's struggles in recent encounters.

## India's Eleven-Goal Statement

India's 11-0 demolition of Maldives was built on collective ruthlessness. Pyari Xaxa, Anju Tamang, and the impressive Naorem all found the net, with Naorem opening the scoring inside eleven minutes. The margin was never in doubt, but manager and coaching staff will have noted that the real test was always going to be Bangladesh, not Maldives.

The Indian squad includes several players with European league experience and a core group that has been together through recent international windows. But execution against organised defences — rather than the overmatched Maldives — remains the question.

## More Than a Group Match

India are the highest-ranked team in the tournament at 69th in the FIFA World Rankings. Bangladesh are ranked considerably lower, but regional rankings have proven unreliable predictors of SAFF tournament results. The head-to-head record is the form guide that matters here.

A win for India would likely confirm them as group winners and set up a favourable knockout-stage path. A draw or defeat would hand Bangladesh the advantage and force India into a potentially harder route to the title.

## The NRI Connection

Women's football in South Asia has grown significantly in visibility over the past five years, and the SAFF Championship is one of the few tournaments where the Indian women's team plays in front of home crowds. For NRI fans following the team's progress, the Bangladesh match is the first genuine test of this campaign. India have not won the SAFF Women's Championship in six years — the longest drought in the tournament's history.

Sunday evening in Margao will reveal whether this squad has the quality to break both the Bangladesh jinx and the title drought.

## How to Watch

The match kicks off at 7:30 PM IST (10:00 AM ET, 7:00 AM PT) on Sunday, May 31. Live streaming is available on FanCode.

**Sources:** SAFF, Khel Now, AIFF"""

# Image already uploaded from first run
img3_final = f"{SB_URL}/storage/v1/object/public/article-images/{art3_slug}.jpg"

art3 = {
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "body": art3_body,
    "slug": art3_slug,
    "category": "sports",
    "status": "published",
    "published_at": now,
    "sources": "SAFF, Khel Now, AIFF",
    "image_url": img3_final,
    "image_attribution": "Pexels",
}
articles.append(art3)


# ── Publish all articles ────────────────────────────────────────────────
print("\n═══ Publishing ═══")
success = 0
for art in articles:
    # Validate essentials
    assert len(art["headline"]) >= 20, f"Headline too short: {art['headline']}"
    assert len(art["subheadline"]) >= 15, f"Subheadline too short: {art['subheadline']}"
    assert len(art["body"]) >= 400, f"Body too short ({len(art['body'])} chars): {art['headline'][:50]}"
    assert art["category"] == "sports", f"Wrong category: {art['category']}"
    
    word_count = len(art["body"].split())
    print(f"\n  📝 {art['headline'][:60]}...")
    print(f"     Words: {word_count} | Slug: {art['slug'][:50]}")
    print(f"     Image: {'✓' if art.get('image_url') else '✗ NONE'}")
    
    art_id = sb_insert(art)
    if art_id:
        success += 1

print(f"\n═══ Done: {success}/{len(articles)} articles published ═══")
