#!/usr/bin/env python3
"""Sports writer — 2026-05-24 08:00 PDT run: 2 articles + score decay."""

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

# ── ARTICLE 1: Rajasthan Royals Qualify — Jofra Archer's 3/17 Seals the Fourth Playoff Spot ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Jofra Archer Took 3 for 17. Rohit Sharma Made Zero. And Rajasthan Royals Are in the IPL 2026 Playoffs.",
    "subheadline": "At Wankhede Stadium on Sunday afternoon — his home ground, in his home city, in front of his home crowd — Rohit Sharma walked out to bat and was dismissed for a golden duck by Jofra Archer in the fourth over. By the time Mumbai Indians finished their innings at 175 for 9, Rajasthan Royals had already sealed the fourth and final playoff spot with a 30-run win. The IPL 2026 semifinal picture is now complete: RCB vs GT in Qualifier 1, SRH vs RR in the Eliminator.",
    "slug": "rajasthan-royals-qualify-ipl-2026-playoffs-jofra-archer-mi-rohit-sharma-wankhede-20260524",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "For NRI cricket fans who set alarms for 3 AM Pacific or 6 AM Eastern to watch IPL matches, the playoff picture is the payoff — the reason they endured two months of sleep deprivation and spoiler-dodging on WhatsApp groups. Rajasthan Royals' qualification has particular diaspora resonance: this is the franchise that was built on the promise of the IPL's original fairytale (Shane Warne's 2008 team of unknowns), has cycled through years of underperformance and ownership drama, and now returns to the playoffs behind a squad that features Jofra Archer — a global T20 mercenary whose availability has been the single biggest variable in RR's planning for three years — and Vaibhav Sooryavanshi, a 15-year-old who has become the tournament's breakout story. For Indian-Americans, Indian-Brits, and Indian-Canadians who follow the IPL as their primary connection to Indian sports culture, the playoff bracket (RCB vs GT, SRH vs RR) is already dominating group chats, office cricket pools, and the bar-watching schedules that diaspora communities organise in every major city from Edison to Fremont to Brampton.",
    "tags": ["Rajasthan Royals", "IPL 2026", "Jofra Archer", "Rohit Sharma", "Mumbai Indians", "IPL Playoffs", "Wankhede Stadium", "Suryakumar Yadav", "Vaibhav Sooryavanshi", "RCB vs GT"],
    "urgency": "breaking",
    "sources": [
        "https://crictracker.com/live-scores/mi-vs-rr-match-69-t20-indian-premier-league-24-may-2026/full-scorecard/",
        "https://khelnow.com/cricket/mumbai-indians-175-9-vs-rajasthan-royals-205-8-result-ipl-2026",
        "https://insidesport.in/cricket/ipl-2026-playoffs-qualification-scenarios-dc-knocked-out-pbks-rr-kkr-remain-hunt",
        "https://mykhel.com/cricket/ipl-2026-points-table-may-23-pbks-beat-lsg"
    ],
    "word_count": 780,
    "score_total": 72,
    "body": """At 3:30 PM on a hot Sunday in Mumbai, Jofra Archer ran in from the Tata End at Wankhede Stadium and bowled the delivery that effectively ended Mumbai Indians' season and began Rajasthan Royals' playoff campaign.

The ball was fast, full, and angled into the stumps. Rohit Sharma, batting at home for what might have been the last time this IPL season, offered a tentative push. The edge carried to Dhruv Jurel behind the stumps. Rohit walked off for zero — his fourth duck of the tournament — and Wankhede fell quiet in the particular way it does when the home crowd knows the match is already gone.

It was gone. Rajasthan Royals posted 205 for 8 batting first, then bowled Mumbai Indians out for 175 in 20 overs. Archer finished with 3 for 17 from four overs — the most economical spell of the match by a margin so wide it looked like a different pitch. Rajasthan won by 30 runs, and the fourth playoff spot was theirs.

## The scorecard tells the story

Rajasthan's 205 was not built by one innings. It was assembled in pieces: Yashasvi Jaiswal's rapid 27 off 17 balls set the tempo. Dhruv Jurel contributed a composed 38 off 26 in the middle overs. Dasun Shanaka hit three sixes in a cameo of 29 off 15. And then Archer, batting at number eight, smashed 32 off 15 balls — including three sixes — to push the total past 200 in the final overs.

It was a complete batting card. No single player crossed 40, but seven Rajasthan batters reached double figures. Against a Mumbai attack that has leaked runs all season, the total felt par-plus on a Wankhede pitch that traditionally favours batters.

Mumbai's chase started catastrophically. Rohit's golden duck in the fourth over left them reeling, and when Naman Dhir fell to Archer for 6 in the same spell, the home side was 20 for 2 in the powerplay.

What followed was a rescue act that came close but never quite arrived. Suryakumar Yadav played the best innings of the match — 60 off 42 balls, including four sixes — and briefly made the contest feel alive. When he was caught-and-bowled by Nandre Burger in the 14th over, Mumbai still needed 80 off 38 balls with five wickets in hand.

Hardik Pandya attacked from the first ball he faced, scoring 34 off just 15 deliveries at a strike rate of 226. But his dismissal — caught at deep midwicket off Archer's third wicket — ended the chase as a realistic proposition. From there, Mumbai's tail wagged briefly but never threatened.

## What it means for the playoffs

The IPL 2026 playoff bracket is now set. Royal Challengers Bengaluru and Gujarat Titans, who finished first and second on the table with 18 points apiece (separated by net run rate), will meet in Qualifier 1 at Dharamsala on Monday, May 26. The winner goes directly to the final on May 31.

Sunrisers Hyderabad, who also finished on 18 points but with an inferior NRR, will face Rajasthan Royals in the Eliminator on Tuesday, May 27. The loser goes home. The winner faces the loser of Qualifier 1 in Qualifier 2 for the second spot in the final.

For Rajasthan, the Eliminator assignment means they take the longer road — win three matches to win the title. But after a season in which they lost six of their first eight matches and appeared headed for an early exit, qualifying at all is an achievement that their supporters will not undervalue.

## Archer's quiet dominance

The Player of the Match award went to Archer, and the numbers alone justified it: 3 for 17 with the ball, 32 off 15 with the bat. But the award understated his influence.

Archer bowled the powerplay overs that broke Mumbai's top order. He bowled at the death when Pandya was threatening to steal the match. His economy rate of 4.25 in a game where every other bowler on either side conceded more than 6.50 per over was the statistical outlier that decided the contest.

For Rajasthan, Archer's fitness has been the single most important variable in their season planning. The England fast bowler has battled recurring injuries since 2021, and his availability for the full IPL 2026 campaign was never guaranteed. That he has played 14 of Rajasthan's 14 league matches — and produced match-winning performances in the two that mattered most (today and the previous win over Lucknow) — is the reason they are in the playoffs.

## Rohit's forgettable farewell

For Rohit Sharma and Mumbai Indians, the season ends not with a playoff run but with a ninth-place finish — their worst in IPL history. Rohit's personal tournament has been a study in decline: 287 runs in 14 innings at an average below 22, with four ducks. The golden duck on Sunday, in what was likely his final innings at Wankhede this season, was a fitting but cruel summary.

Mumbai rested Jasprit Bumrah for the match — a decision that acknowledged the game's meaninglessness for their campaign but denied the Wankhede crowd a proper send-off from their best player.

The IPL's four-team playoff bracket is complete. The conversation now shifts to Dharamsala and the knockout matches that begin on Monday. For Rajasthan Royals, the season that nearly ended in April continues into late May. For Mumbai Indians, it ended on a quiet Sunday afternoon, in front of a crowd that came hoping for something different and left with the sound of Jofra Archer's yorker still ringing.""",
}

# ── ARTICLE 2: Kohli Refuses Head's Handshake — The IPL Rivalry That the Diaspora Cannot Look Away From ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "Kohli Walked Past Head's Outstretched Hand. The Video Has 40 Million Views. The India-Australia Rivalry Just Found Its IPL Chapter.",
    "subheadline": "On Friday night in Hyderabad, after Sunrisers crushed Bengaluru by 55 runs to close the league stage, the players lined up for the customary handshakes. Travis Head extended his hand. Virat Kohli looked straight ahead and kept walking. The clip is now the most-watched moment of the IPL 2026 season — and it carries the weight of a cricketing rivalry that runs deeper than any single tournament.",
    "slug": "virat-kohli-travis-head-handshake-snub-ipl-2026-srh-rcb-india-australia-rivalry-20260524",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "The Kohli-Head incident has ripped through every WhatsApp group, office cricket chat, and family dinner table in the Indian diaspora — not because it is unusual for Kohli, but because it happened against an Australian, and for NRIs, the India-Australia cricket rivalry carries a specific emotional charge that transcends the sport. Indian-Americans who grew up watching the 2001 Kolkata Test, the 2003 World Cup final, and the 2020-21 Gabba miracle understand that India-Australia matches are where Indian cricket defines itself against Western sporting power. The rivalry has always been about more than runs and wickets — it is about respect, pedigree, and whether Indian cricketers will accept the Australian model of sledging culture or push back on their own terms. Kohli has been the central figure in this dynamic for a decade. For diaspora cricket fans watching from Melbourne, Sydney, London, or New York, the handshake refusal is a Rorschach test: some see it as unsporting pettiness from a player who should know better at 37; others see it as the unapologetic intensity that made Kohli the diaspora's avatar of Indian sporting aggression. Either way, every NRI cricket fan has an opinion, and the debate is louder than the match itself.",
    "tags": ["Virat Kohli", "Travis Head", "IPL 2026", "SRH vs RCB", "Handshake Controversy", "India Australia Rivalry", "Royal Challengers Bengaluru", "Sunrisers Hyderabad", "Cricket Controversy", "IPL Playoffs"],
    "urgency": "daily",
    "sources": [
        "https://reuters.com/sports/cricket/kohli-refuses-handshake-with-head-after-heated-verbal-spat-during-ipl-clash-2026-05-23/",
        "https://livemint.com/sports/kohli-travis-head-handshake-srh-rcb-ipl-2026",
        "https://sportskeeda.com/cricket/virat-kohli-snubs-travis-head-handshake-srh-rcb-ipl-2026",
        "https://cricketaddictor.com/virat-kohli-travis-head-handshake-controversy-explained"
    ],
    "word_count": 750,
    "score_total": 68,
    "body": """The sequence lasted four seconds. It has been replayed forty million times.

On Friday evening at the Rajiv Gandhi International Stadium in Hyderabad, Sunrisers Hyderabad beat Royal Challengers Bengaluru by 55 runs in the final league match for both teams. SRH posted 255 for 4 — a total that was always going to be difficult to chase under lights — and bowled Bengaluru out for 200, with Travis Head's own over claiming the wicket of RCB captain Rajat Patidar.

After the final ball, the teams lined up for the customary post-match handshakes. Kohli greeted Pat Cummins and the other Sunrisers players without incident. Then Head stepped forward, hand extended. Kohli looked straight ahead, walked past, and did not break stride.

The cameras caught every frame. Social media did the rest.

## What happened during the match

The confrontation did not begin at the handshake line. It started in the sixth over of Bengaluru's chase.

Kohli, opening the batting for RCB, was facing Sunrisers' pace attack when he and Head began exchanging words. The stump microphones caught fragments — enough to confirm the conversation was not friendly. Kohli was seen gesturing towards Head and then making the "impact player" substitution signal with his hands — a mocking reference to the IPL rule that Sunrisers frequently use to replace Head, primarily a batter, with a specialist bowler after his innings is done.

The implication was clear: you do not bowl, so why are you talking?

Head did not respond verbally in the moment. He did not need to. Kohli fell three overs later, caught for 15 off 11 balls — a scratchy, frustrated innings that ended his league-stage campaign with a soft dismissal. As Kohli walked off, Head reportedly said something along the lines of: "Mate, you got out before I even came on to bowl."

Later in the innings, Head did bowl — one over of part-time left-arm spin. He dismissed Patidar. The symbolism was not lost on anyone in the stadium or watching on television.

## The history behind the moment

Kohli and Head have history that predates the IPL. Head scored a century in the 2023 World Cup final at Ahmedabad — the match where India, playing at home in front of 130,000 people, lost the trophy to Australia. That innings is still raw in Indian cricket's collective memory. For many Indian fans, Head became the symbol of a defeat that was supposed to be impossible.

The two also clashed during the Border-Gavaskar Trophy series, where the India-Australia rivalry plays out in its purest form — five Tests, hostile crowds, sledging that crosses the line between competitive and personal. Kohli's history of confrontations with Australian players stretches back to the 2014-15 series against Mitchell Johnson and David Warner. It is a feature, not a bug, of how he plays cricket.

What made Friday's handshake refusal different was the context. This was not a Test match between nations. This was the IPL — a franchise league where Kohli and Head are colleagues in the broader cricketing ecosystem, where they share dressing rooms with each other's compatriots, where the convention is to leave national rivalries at the door.

Kohli chose not to.

## The reaction split

Former Indian all-rounder Irfan Pathan said the snub "could be avoided." Former off-spinner Harbhajan Singh, who has his own history of on-field confrontations with Australians, offered a more nuanced view: competitive intensity is part of what makes Kohli great, but the handshake line is supposed to be the reset.

On social media, the split was predictable and absolute. Indian fans who worship Kohli's aggression celebrated the moment as authenticity — the refusal to perform sportsmanship he did not feel. Australian cricket media and a significant portion of neutral observers called it petty, pointing out that Head had offered the handshake first and that Kohli's behaviour was directed at a player whose only offence was scoring runs and sledging back.

The diaspora's reaction sat somewhere in between but leaned heavily toward understanding Kohli. In Indian cricket culture, the refusal to be intimidated by Australians carries generational weight. It connects to Sourav Ganguly taking his shirt off at Lord's, to Harbhajan's confrontation with Andrew Symonds, to Kohli's own 2018 series in Australia where he averaged 60 and sledged the entire home team. For NRIs who grew up watching India lose to Australia and then watching Kohli refuse to accept that dynamic, the handshake refusal is not about manners — it is about posture.

## What comes next

Both teams have qualified for the playoffs. RCB finished first on the table; SRH finished third. They cannot meet again until the final, which means the next Kohli-Head encounter — if it happens — would be the biggest match of the tournament.

That possibility is now the subplot that every broadcaster, every pundit, and every WhatsApp cricket group is tracking. The handshake lasted four seconds. The narrative it created will last the rest of the tournament.

The IPL has always sold itself as cricket's most entertaining spectacle. On Friday night in Hyderabad, two of the world's best players reminded everyone that entertainment in cricket is not always about runs and wickets. Sometimes it is about a hand that was offered and a man who walked past it.""",
}

if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-24 08:00 PDT")
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

    print("\nInserting Article 1: RR Qualify for IPL 2026 Playoffs...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    # Try image for Article 1
    img1_path = f"/tmp/{a1_id}.jpg"
    if fetch_image("cricket celebration victory stadium night", img1_path):
        img1_url = upload_image(a1_id, img1_path)
        if img1_url:
            update_image_url(a1_id, img1_url)

    print("\nInserting Article 2: Kohli-Head Handshake Controversy...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    # Try image for Article 2
    img2_path = f"/tmp/{a2_id}.jpg"
    if fetch_image("cricket players intense rivalry confrontation", img2_path):
        img2_url = upload_image(a2_id, img2_path)
        if img2_url:
            update_image_url(a2_id, img2_url)

    # Score decay
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    print(f"\nDone. 2 articles published.")
    print(f"  IDs: {a1_id}, {a2_id}")
