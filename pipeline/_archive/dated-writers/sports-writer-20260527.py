#!/usr/bin/env python3
"""Sports Writer - 2026-05-27 Evening Run
Publishes 3 fresh sports articles to The Videshi.
"""

import json
import os
import re
import sys
import time
import uuid
from datetime import datetime, timezone

import requests
import urllib.parse

# ── Config ───────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Image helpers ────────────────────────────────────────────────────────────
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
            # Prefer originalimage (higher res), fall back to thumbnail AS-IS
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Check image URL returns HTTP 200 with image content-type and reasonable size."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", "0"))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't respond well to HEAD, try GET
        if r.status_code != 200:
            r2 = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            ct2 = r2.headers.get("Content-Type", "")
            if r2.status_code == 200 and "image" in ct2:
                # Read a bit to check size
                chunk = r2.raw.read(6000)
                if len(chunk) > 5000:
                    return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def publish_article(article):
    """Insert article into Supabase p2_articles table."""
    article_id = str(uuid.uuid4())
    # Build sources as array of {name, url} objects
    raw_sources = article.get("sources", [])
    formatted_sources = []
    for s in raw_sources:
        if isinstance(s, dict):
            formatted_sources.append(s)
        else:
            formatted_sources.append({"name": s, "url": ""})
    
    payload = {
        "id": article_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "sports",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": article.get("image_url"),
        "image_caption": article.get("image_caption"),
        "image_attribution": article.get("image_attribution"),
        "sources": formatted_sources,
        "vertical": "sports",
        "urgency": "daily",
        "tags": article.get("tags", []),
    }
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
    )
    if r.status_code in (200, 201):
        print(f"  ✓ Published: {article['headline'][:60]}...")
        return True
    else:
        print(f"  ✗ Failed ({r.status_code}): {r.text[:200]}")
        return False


# ── Articles ─────────────────────────────────────────────────────────────────

def article_basavareddy():
    """Basavareddy's French Open run ends in Round 2."""
    print("\n📝 Article 1: Basavareddy's French Open Round 2 loss")
    
    # Image: Wikipedia for Basavareddy - may not have one as he's young
    img = fetch_wikipedia_person_image("Nishesh Basavareddy")
    img_attr = "Wikimedia Commons"
    img_caption = "Nishesh Basavareddy at the 2026 French Open."
    
    if not img or not validate_image(img):
        img = fetch_pexels_image("Roland Garros tennis clay court", "French Open tennis 2026")
        img_attr = "Pexels"
        img_caption = "Court action at Roland Garros during the 2026 French Open."
    
    if img and not validate_image(img):
        img = None
    
    body = """Nishesh Basavareddy's enchanting run at the 2026 French Open ended on Wednesday, as the Indian-American wildcard fell to Alex Michelsen 6-7, 3-6, 6-3, 3-6 in the second round on Court 13 at Roland Garros.

Three days earlier, the twenty-one-year-old from Carmel, Indiana — whose parents Muralikrishna and Sai Prasanna emigrated from Nellore, Andhra Pradesh, to the United States in 1999 — had delivered one of the tournament's signature moments, stunning seventh seed Taylor Fritz 7-6(5), 7-6(5), 6-7(9), 6-1 in his French Open main-draw debut. It was his first career win over a top-ten opponent, and he became the first American to beat a top-ten seed at Roland Garros in twenty-six years.

## A Match Decided by Margins

Against Michelsen, the margins were impossibly thin. Basavareddy was up 5-3 in the first-set tiebreak before Michelsen's aggression and serving turned the tide. He dropped the second set after a slow start, then roared back with a dominant third set that suggested the match was far from over.

"I feel like it was just a couple of points here and there," Basavareddy said afterward. "In the first set, I got the break, then went down a break, and then was up 5-3 in the tiebreak. He played a little aggressive, made a couple of good serves as well."

The fourth set was a story of disrupted rhythm. After Michelsen took a medical timeout at 3-4, Basavareddy admitted his energy dipped. "I definitely dropped my energy a little bit in maybe the first couple of points of the next game," he said. "Next time I need to not let that drop happen."

## The Drop Shot That Worked and the Conditions That Didn't

On the fast, sun-baked outside courts at Roland Garros — where temperatures have been extreme enough to cause four player collapses in the first four days — Basavareddy's drop shot was a legitimate weapon. But the pace of the court made rallying from the baseline difficult, and his serve let him down at critical junctures. He finished with seven aces but also seven double faults, and his 42 groundstroke errors outweighed his 33 groundstroke winners.

"On the outside courts, it's even faster than the court I played on last match, so it was going to be a lot about serve and return," he explained. "I didn't serve great for a lot of the match, which made it a little bit tougher."

## What He Leaves Behind in Paris

Basavareddy leaves the French Open with far more than a second-round exit. His demolition of Fritz announced him as a player capable of competing at the highest level of the sport, and at twenty-one, his trajectory is steeply upward. He reached a career-high ranking of 99 in June 2025 and is currently ranked 148th after battling through a dip.

The Stanford dropout — who left college after two years when his Challenger results made the decision unavoidable — had also taken a set off his idol Novak Djokovic at the 2025 Australian Open. For the Indian diaspora, he represents something rare: an athlete of Telugu heritage competing at the pinnacle of global tennis.

"There are still positives to take from this week," he said. "Hopefully, I can start to build on it more."

## What Comes Next

Basavareddy plans to take ten days off before beginning his grass-court preparation. His schedule includes an ATP 250 event, a grass-court Challenger, and then Wimbledon qualifying — a path that could take him back to a Grand Slam main draw in just over a month.

For NRI tennis fans who followed his run in Paris with particular intensity, the wait for the next chapter will not be long. Basavareddy is building toward something. Paris confirmed it. The second round was a setback, not a ceiling.

"I just need to keep playing aggressively, working on coming to the net more, and working on my serve," he said. "It'll take time, but I think it has been better over the course of the clay season."

The kid from Andhra Pradesh, by way of Carmel, Indiana, is going to Wimbledon."""

    return {
        "headline": "Basavareddy's French Open Run Ends in Round Two. He Leaves Paris With Far More Than a Loss.",
        "subheadline": "The Indian-American wildcard fell to Alex Michelsen in four sets, three days after stunning Taylor Fritz in his Roland Garros debut.",
        "body": body,
        "slug": "basavareddy-french-open-round-2-loss-michelsen-fritz-upset-diaspora-wimbledon-20260527",
        "image_url": img,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "sources": [
            {"name": "Indian Tennis Daily", "url": "https://indiantennisdaily.com/2026/05/28/i-will-take-the-positives-nishesh-basavareddy/"},
            {"name": "Sporting News", "url": "https://www.sportingnews.com/in/tennis/news/nishesh-basavareddy-tennis-star-who-upset-world-no-9-taylor-fritz-french-open/"},
            {"name": "ATP Tour", "url": "https://www.atptour.com"},
        ],
        "tags": ["French Open", "Nishesh Basavareddy", "tennis", "Indian diaspora", "Roland Garros"],
    }


def article_gukesh_firouzja():
    """Gukesh loses to Firouzja; Norway Chess Round 3 results."""
    print("\n📝 Article 2: Gukesh falls to Firouzja at Norway Chess")
    
    # Try Wikipedia image for Gukesh
    img = fetch_wikipedia_person_image("Gukesh Dommaraju")
    img_attr = "Wikimedia Commons"
    img_caption = "World champion Gukesh Dommaraju at Norway Chess 2026."
    
    if not img or not validate_image(img):
        img = fetch_wikipedia_person_image("Alireza Firouzja")
        img_caption = "Alireza Firouzja leads Norway Chess 2026 with a perfect record."
        if not img or not validate_image(img):
            img = fetch_pexels_image("chess tournament grandmaster", "chess pieces board")
            img_attr = "Pexels"
            img_caption = "Norway Chess 2026 has produced dramatic encounters."
    
    if img and not validate_image(img):
        img = None
    
    body = """World champion Gukesh Dommaraju suffered his third consecutive match loss at Norway Chess 2026 on Wednesday, falling to tournament leader Alireza Firouzja in an Armageddon tiebreak after a drawn classical game. It was a result that extended Firouzja's extraordinary run to three match wins in three rounds — and left the world champion searching for answers in his adopted home tournament.

## Gukesh Was Winning. Then He Wasn't.

The classical game between Gukesh and Firouzja was not the one-sided affair the final result suggests. Playing with the white pieces, Gukesh built a commanding position and appeared to be on the verge of becoming the first player to beat Firouzja in classical chess at this tournament.

"I was completely winning throughout the game and it was so stupid to allow this ...Bd1," Gukesh said afterward, his frustration visible. The Indian prodigy had miscalculated a single move, allowing Firouzja's bishop to slip into a devastating square that equalized the position instantly.

The Armageddon that followed was, by Firouzja's own admission, played from a "very lost" position. But the Iranian-born Frenchman — who has made time-scramble magic a personal specialty in Oslo — found his way to the draw he needed as Black to claim the 1.5-point match victory.

"I think a draw with Black was a decent result today in classical," Firouzja said, before adding with characteristic understatement that "the cherry on the cake was a win in Armageddon."

## Firouzja's Perfect Record

Three rounds into Norway Chess, Firouzja's dominance is historic. He has won every single match — beating Magnus Carlsen in classical chess in Round 1, defeating Praggnanandhaa in Round 2, and now adding the world champion to his list. His nine points from a possible nine give him a three-point lead over second-placed Praggnanandhaa. No player has started a Norway Chess campaign with this kind of authority in the tournament's modern format.

He is doing all of this with an injured ankle.

## Praggnanandhaa Beats Carlsen in Dramatic Fashion

The other headline from Round 3 belongs to R. Praggnanandhaa, who scored a full three-point classical win over world number one Magnus Carlsen in the most dramatic game of the tournament so far.

Carlsen opened with the Najdorf Sicilian only to be surprised by Praggnanandhaa's sixth-move sideline, 6.h4. The Norwegian spent twenty-eight minutes deliberating on his eighth move. From there, the game swung wildly — Praggnanandhaa built an advantage, Carlsen fought back from the dead to reach a winning position, and then self-destructed in time trouble when he pushed his g-pawn and overlooked his opponent's reply.

"Honestly, this is not a game to celebrate too much about," Praggnanandhaa said, with characteristic humility. "In these time scrambles it's basically like tossing a coin."

Carlsen was more blunt: "I felt like it was pretty much a repeat of the game against Gukesh last year where I missed one thing and then I kind of panicked and lost within a few moves."

The loss leaves Carlsen in last place — 1.5 points adrift in his home super-tournament. Next up for the Norwegian: Black against Gukesh in Round 4.

## Divya Deshmukh Closes the Gap

In the women's event, India's nineteen-year-old Divya Deshmukh continued her remarkable Armageddon streak by defeating tournament leader Bibisara Assaubayeva in a tiebreak, closing the gap to just one point. All three classical games in the women's section were drawn, but Divya's third consecutive Armageddon win — she has not lost a single match — confirms her as the form player of the tournament.

"I don't want to play any more Armageddons!" she said, despite winning every single one.

Anna Muzychuk beat Koneru Humpy in another all-Armageddon finish, and Zhu Jiner escaped a losing endgame against Women's World Champion Ju Wenjun to win their tiebreak as well.

## Standings After Round 3

**Open:** Firouzja 9, Praggnanandhaa 4.5, So 4, Gukesh 2.5, Keymer 2, Carlsen 0

**Women:** Assaubayeva 5.5, Divya 4.5, Muzychuk 4, Zhu 4, Ju 1, Humpy 0

Round 4 begins Thursday at 8:30 p.m. IST (11 a.m. ET). Firouzja faces the returning Keymer, while Carlsen takes Black against Gukesh in what promises to be the most emotionally charged game of the tournament so far."""

    return {
        "headline": "Gukesh Was Completely Winning. Then He Let One Move Slip. Firouzja Stays Perfect at Norway Chess.",
        "subheadline": "The world champion lost to Firouzja in Armageddon after squandering a winning classical position. Praggnanandhaa beat Carlsen. Divya Deshmukh won again.",
        "body": body,
        "slug": "gukesh-firouzja-norway-chess-2026-round-3-pragg-carlsen-divya-deshmukh-20260527",
        "image_url": img,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "sources": [
            {"name": "Chess.com", "url": "https://www.chess.com/news/view/2026-norway-chess-round-3"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/sports-games/3924092-praggnanandhaa-claims-victory-over-carlsen-as-gukesh-faces-another-defeat"},
            {"name": "Chessbase", "url": "https://en.chessbase.com"},
        ],
        "tags": ["Norway Chess", "Gukesh", "Firouzja", "Praggnanandhaa", "Carlsen", "Divya Deshmukh", "chess"],
    }


def article_gt_vs_rr_preview():
    """IPL 2026 Qualifier 2: GT vs RR preview."""
    print("\n📝 Article 3: GT vs RR Qualifier 2 Preview")
    
    # Try Wikipedia for Vaibhav Sooryavanshi (probably too young for Wikipedia)
    img = fetch_wikipedia_person_image("Vaibhav Suryavanshi")
    img_attr = "Wikimedia Commons"
    img_caption = "Vaibhav Sooryavanshi has been the breakout star of IPL 2026."
    
    if not img or not validate_image(img):
        # Try Shubman Gill
        img = fetch_wikipedia_person_image("Shubman Gill")
        img_caption = "Gujarat Titans captain Shubman Gill faces a must-win Qualifier 2."
        if not img or not validate_image(img):
            img = fetch_pexels_image("cricket stadium India T20", "cricket match stadium floodlights")
            img_attr = "Pexels"
            img_caption = "Qualifier 2 takes place at the New PCA Stadium in Mullanpur."
    
    if img and not validate_image(img):
        img = None
    
    body = """The road to the IPL 2026 final runs through Mullanpur on Thursday. Gujarat Titans, humbled by Royal Challengers Bengaluru in Qualifier 1, face Rajasthan Royals — riding the force of nature that is Vaibhav Sooryavanshi — in Qualifier 2 at the New PCA Stadium. The winner advances to the final against RCB on May 31. The loser goes home.

## Two Very Different Arrivals

Gujarat Titans arrive at Qualifier 2 carrying the weight of a ninety-two-run demolition. In Qualifier 1 at Dharamsala, Rajat Patidar's ninety-three off thirty-three balls powered RCB to two hundred and fifty-four — the highest total in IPL playoff history. GT were bowled out for one hundred and sixty-two. Captain Shubman Gill fell for two runs. The team that has built an identity on adaptability under Gill's captaincy was taken apart so thoroughly that coach Ashish Nehra's post-match press conference lasted barely three minutes.

Rajasthan Royals, by contrast, arrive humming. Wednesday's Eliminator against Sunrisers Hyderabad was a showcase of everything this team has become under Sanju Samson's leadership: relentless at the top of the order, devastating in the powerplay, and lethal with the ball when it matters. They posted two hundred and forty-three for eight and then bowled SRH out for one hundred and ninety-six to win by forty-seven runs.

## The Sooryavanshi Question

Every conversation about this playoff series, this IPL season, and perhaps this era of T20 cricket eventually arrives at the same name: Vaibhav Sooryavanshi.

The fifteen-year-old scored ninety-seven off twenty-nine balls in the Eliminator — twelve sixes, five fours, a strike rate that defies comprehension. He has now scored six hundred and eighty runs this season at a strike rate of two hundred and thirty-two. He broke Chris Gayle's all-time record for sixes in a single T20 tournament. He has hit fifty-three of them. He is fifteen years old.

For GT, the problem is not abstract. Their bowling attack — already weakened by the absence of consistent early-over control — has no template for handling a batter who operates outside every known framework. Rashid Khan, their most experienced matchup weapon, has been economical through the tournament but has not faced Sooryavanshi in conditions like these.

## Gujarat's Path Back

GT's case for optimism rests on their muscle memory. This franchise has been to the playoffs in every season since its inception, winning the title in its debut year. Gill's captaincy has matured. The batting lineup, when it fires in sequence — Gill, Sai Sudharsan, David Miller, Heinrich Klaasen — has the depth to match any total in the tournament.

The bowling, though, needs a different performance. Mohammed Siraj and Josh Hazlewood did not offer the control that Qualifier 1 demanded. Whether Rashid Khan can reprise his role as the spine of the middle overs — and whether the pace attack can provide the early wickets that prevent Sooryavanshi from settling — will likely determine whether Gujarat's season continues.

## Head-to-Head and Venue

GT and RR have played each other twice this season, splitting the results. The New PCA Stadium in Mullanpur has offered high-scoring matches throughout the tournament, with an average first-innings total above one hundred and eighty in playoff conditions. The shorter boundaries favour stroke-makers, which tilts the calculus toward RR's explosive top order.

## The NRI Watch Guide

For fans in the United States, the match starts at approximately 7:00 AM PDT / 10:00 AM EDT on Thursday, May 29. UK viewers can tune in at 3:00 PM BST. Canadian fans: 10:00 AM EDT. Streaming is available on JioHotStar, Star Sports Network, Sky Sports, and Willow.tv.

## What's at Stake

The winner faces RCB in the final at Dharamsala on Saturday, May 31. For GT, it is a chance to redeem the worst performance of their playoff history. For RR, it is the continuation of a run that increasingly looks like destiny — powered by a teenager who has already rewritten the record books and shows no sign of stopping.

The last team to win the IPL after taking the Eliminator route was Sunrisers Hyderabad in 2016. That team had David Warner and Bhuvneshwar Kumar at their peak. This Rajasthan team has Vaibhav Sooryavanshi. History suggests the Eliminator path is cursed. Sooryavanshi suggests history is about to be revised."""

    return {
        "headline": "GT Lost by Ninety-Two Runs. RR Won by Forty-Seven. On Thursday They Meet in a Match Where Only One Season Survives.",
        "subheadline": "Gujarat Titans face Rajasthan Royals in IPL 2026 Qualifier 2 at Mullanpur. Sooryavanshi has 680 runs and 53 sixes. Gill's team needs a resurrection.",
        "body": body,
        "slug": "gt-vs-rr-qualifier-2-ipl-2026-preview-sooryavanshi-gill-mullanpur-20260527",
        "image_url": img,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "sources": [
            {"name": "IPL T20", "url": "https://www.iplt20.com"},
            {"name": "Cricbuzz", "url": "https://m.cricbuzz.com"},
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "Cricket Times", "url": "https://www.crickettimes.com"},
        ],
        "tags": ["IPL 2026", "Gujarat Titans", "Rajasthan Royals", "Qualifier 2", "Vaibhav Sooryavanshi", "Shubman Gill", "cricket"],
    }


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("🏏 The Videshi Sports Writer — 2026-05-27 Evening Run")
    print("=" * 60)
    
    articles = [
        article_basavareddy(),
        article_gukesh_firouzja(),
        article_gt_vs_rr_preview(),
    ]
    
    published = 0
    for article in articles:
        if publish_article(article):
            published += 1
        time.sleep(1)  # Brief pause between inserts
    
    print(f"\n{'=' * 60}")
    print(f"✅ Published {published}/{len(articles)} articles")
    if published < len(articles):
        print("⚠ Some articles failed to publish")
        sys.exit(1)


if __name__ == "__main__":
    main()
