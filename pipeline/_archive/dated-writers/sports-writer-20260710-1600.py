#!/usr/bin/env python3
"""Videshi Sports Writer — 2026-07-10 16:00 PT run. 3 articles."""

import json
import os
import subprocess
from datetime import datetime, timezone

# Load env
env_path = os.path.expanduser("~/workspace/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

def insert_article(article):
    """Insert an article into p2_articles via Supabase REST API using curl."""
    payload = json.dumps(article)
    result = subprocess.run(
        [
            "curl", "-sS", "-X", "POST",
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            "-H", f"apikey: {SUPABASE_KEY}",
            "-H", f"Authorization: Bearer {SUPABASE_KEY}",
            "-H", "Content-Type: application/json",
            "-H", "Prefer: return=representation",
            "-d", payload,
        ],
        capture_output=True, text=True
    )
    resp = result.stdout
    try:
        data = json.loads(resp)
        if isinstance(data, list) and len(data) > 0:
            print(f"✅ Inserted: {article['headline']}")
            print(f"   slug: {article['slug']}")
            return True
        else:
            print(f"❌ Failed: {article['headline']}")
            print(f"   Response: {resp[:500]}")
            return False
    except json.JSONDecodeError:
        print(f"❌ JSON error: {resp[:500]}")
        return False


now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

articles = []

# ─────────────────────────────────────────────
# ARTICLE 1: Spain 2-1 Belgium — World Cup QF
# ─────────────────────────────────────────────

articles.append({
    "headline": "Merino Does It Again. Spain's Late Hero Sinks Belgium to Set Up a Semifinal Showdown With France.",
    "subheadline": "Mikel Merino's 87th-minute winner at SoFi Stadium breaks Belgium's hearts and ends Spain's record-breaking shutout streak in style.",
    "slug": "spain-2-1-belgium-world-cup-quarterfinal-merino-late-winner-courtois-injury-france-semifinal-nri-2026",
    "body": """If you looked away from your screen after the 85th minute at SoFi Stadium on Friday, you missed it. Again.

Mikel Merino — the same man who buried Portugal in the Round of 16 — needed precisely 106 seconds after coming off the bench to do the same to Belgium. A speculative shot from teenage defender Pau Cubarsí wasn't held by substitute goalkeeper Senne Lammens, and Merino, lurking like a predator at the back post, hammered the loose ball into the roof of the net. Spain 2, Belgium 1. Quarterfinal over. Semifinal booked.

It was the kind of moment that defines tournaments. And for the millions of Indian diaspora fans watching from living rooms in Los Angeles, New Jersey, and London, it arrived at a venue many of them drive past on their daily commute — SoFi Stadium in Inglewood, barely 30 minutes from LA's Little India on Pioneer Boulevard.

## Spain's Record Falls, But They Don't

For five matches and a World Cup-record 649 minutes, Spain's goalkeeper Unai Simón had not conceded a single goal. The streak surpassed every previous World Cup record, stretching back to the group stage. Belgium's Charles De Ketelaere ended it in the 41st minute, muscling past Cubarsí to head home a cross from Timothy Castagne. It was the first goal Spain had conceded in open play in a World Cup knockout match since Zinedine Zidane scored against them in the 2006 Round of 16.

But Spain are not the kind of team that crumbles when their aura cracks. They had already taken the lead through Fabián Ruiz in the 30th minute — a scruffy but decisive goal, smashed home on the rebound after Thibaut Courtois saved Dani Olmo's initial effort. Ruiz, making his first start since the tournament opener in a surprise tactical call by coach Luis de la Fuente, repaid the faith in full.

Belgium, to their credit, fought back hard. De Ketelaere's equalizer was a moment of genuine quality, and for a stretch of the second half, the Red Devils looked like they might pull off an upset. But two blows broke them. First, captain Youri Tielemans was ruled out before kickoff with a warm-up injury, joining the already-sidelined Amadou Onana. Then, in the 71st minute, Courtois — their most important player — went down with what appeared to be a serious injury and was replaced by the relatively untested Lammens.

Kevin De Bruyne, brought back into the starting lineup after sitting out the Round of 16, picked up a yellow card and was substituted in the 85th minute. It may have been his final act in a World Cup. He's 35 now, and Belgium's golden generation, for all their talent, will end this cycle without a major trophy.

## What's Next — And Why NRIs Should Care

The semifinal bracket is set: Spain versus France, Tuesday, July 14, at AT&T Stadium in Arlington, Texas. It is a clash of European titans — the reigning European champions against the two-time World Cup holders — and it will be broadcast live on FOX and Telemundo at 3 PM ET.

For the Indian American community, this World Cup on home soil has been a once-in-a-generation event. Tens of thousands of NRIs attended group stage matches across the country. With the semifinal in Dallas — home to one of the largest South Asian populations in the United States — expect another massive desi turnout. Watch parties have already been announced at venues in Frisco, Plano, and Irving.

Saturday brings the remaining two quarterfinals: Norway versus England in Miami (5 PM ET) and Argentina versus Switzerland in Kansas City (9 PM ET). Messi's Argentina, riding the wave of that extraordinary comeback against Egypt, remain the sentimental favorite. But Spain, with Merino's knack for the dramatic, may be the team nobody wants to face.""",
    "category": "sports",
    "vertical": "world-cup",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/7a/Spain_football_team_in_2025_Mikel_Merino.jpg",
    "image_caption": "Mikel Merino in Spain's national team colors, the hero of two knockout-round winners at the 2026 World Cup",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "The World Cup quarterfinal was played at SoFi Stadium near LA's Little India, and the semifinal heads to Dallas — home to one of America's largest South Asian communities.",
    "sources": json.dumps([
        {"name": "NBC Sports", "url": "https://www.nbcsports.com"},
        {"name": "USA Today", "url": "https://www.usatoday.com"},
        {"name": "Fox Sports", "url": "https://www.foxsports.com"},
        {"name": "The Times UK", "url": "https://www.thetimes.com"}
    ]),
    "score_total": 8
})


# ─────────────────────────────────────────────
# ARTICLE 2: Shanaka double hat-trick in MLC
# ─────────────────────────────────────────────

articles.append({
    "headline": "Four Wickets. Four Balls. Shanaka's Last-Over Miracle Writes the Wildest Chapter in MLC History.",
    "subheadline": "Sri Lanka's Dasun Shanaka becomes the first bowler to take a double hat-trick in Major League Cricket, defending 15 runs in the final over for the Seattle Orcas.",
    "slug": "dasun-shanaka-double-hat-trick-mlc-2026-seattle-orcas-texas-super-kings-four-wickets-four-balls-nri",
    "body": """Fifteen runs needed. Five wickets in hand. One over to bowl. Every number said the Texas Super Kings were going to win.

Dasun Shanaka didn't care about the numbers.

The Sri Lankan all-rounder, bowling the final over for the Seattle Orcas at the Knight Riders Cricket Ground in Pomona, California, produced what may be the single greatest over in the short but explosive history of Major League Cricket. Four wickets in four consecutive deliveries — a double hat-trick — to turn a seemingly lost cause into a famous nine-run victory.

It was the first double hat-trick in MLC history, and only the second time a Sri Lankan has achieved the feat in professional T20 cricket after the great Lasith Malinga.

## How It Unfolded

The match itself was a low-scoring grind. Batting first, the Orcas were restricted to a modest 121 for 9 in their 20 overs, with Sri Lanka's Amshi de Silva claiming three wickets for just 15 runs. Adam Milne chipped in with two wickets conceding only 10 runs across his four overs. It looked like a straightforward chase for the Super Kings.

In reply, the Super Kings never truly found momentum, losing wickets at steady intervals. But Donovan Ferreira and Shubham Ranjane had stitched together a crucial 43-run partnership, and with 15 needed off the final over and five wickets in hand, the arithmetic was firmly in their favor.

The first two balls of Shanaka's over yielded five runs — Ranjane smashed a boundary before taking a single, leaving the Super Kings needing 10 off four balls. Still gettable. Then the script flipped.

Ball three: Shanaka bowled a slower delivery that skidded through Ferreira's defenses and shattered his stumps. Ball four: Calvin Savage, the new man, mistimed a slower ball and found Shimron Hetmyer at long-on. Ball five: Adam Milne edged behind to wicketkeeper Tim Seifert. Hat-trick. Ball six: Amshi de Silva swung wildly, the ball looped to Hetmyer at long-on again. Double hat-trick. Match over.

The crowd at the Knight Riders Cricket Ground erupted. Shanaka's teammates mobbed him. Social media went into meltdown.

## "It Feels Amazing" — Shanaka

"Is that your first ever hat-trick? Of course, indeed it is. All in my cricket career," Shanaka said in his post-match interview, grinning. "One and only great Lasith Malinga, my captain. It feels amazing to get a double hat-trick. It's a different stage, but really happy."

The 30-year-old former Sri Lanka captain had previously been handed the final over after fellow all-rounder Marcus Stoinis had already bowled his full quota. With Ferreira — a dangerous finisher — on strike, it was a high-pressure ask. Shanaka delivered four slower balls and four wickets, conceding just five runs.

## The MLC Picture — And Why It Matters to NRIs

With all six teams having played eight matches, the standings paint a clear picture. The San Francisco Unicorns lead the table with 10 points from five wins, looking dominant. The Los Angeles Knight Riders and MI New York share second with six points each, while Seattle, Texas, and Washington are locked on four points apiece.

But the broader story is what MLC represents for cricket in America. Now in its fourth season, the league has become a genuine sporting product in the United States. Matches are played at purpose-built venues in cities with significant South Asian populations — Pomona, Redmond, Grand Prairie, New York. Weekend matches regularly attract thousands of Indian American families who show up in team jerseys, bringing their own food, their own energy, and their own brand of cricket fandom.

For the diaspora, MLC is more than a T20 league. It is validation — the sport they grew up with, played in parking lots and parks across the American suburbs, now has a professional home. Shanaka's moment of magic is exactly the kind of highlight that gets shared in family WhatsApp groups from Seattle to Hyderabad, reminding NRIs that cricket's American chapter is being written in real time.""",
    "category": "sports",
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Knight_Riders_Cricket_Field_aerial_view.png/1280px-Knight_Riders_Cricket_Field_aerial_view.png",
    "image_caption": "Aerial view of the Knight Riders Cricket Field in Pomona, California, where Shanaka's historic double hat-trick unfolded",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "MLC's fourth season is being played in cities with large NRI populations — Pomona, Redmond, New York — and Shanaka's viral moment is the kind of cricket highlight shared across diaspora WhatsApp groups.",
    "sources": json.dumps([
        {"name": "Wisden", "url": "https://www.wisden.com"},
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
        {"name": "Sportskeeda", "url": "https://www.sportskeeda.com"},
        {"name": "CricTracker", "url": "https://www.crictracker.com"}
    ]),
    "score_total": 8
})


# ─────────────────────────────────────────────
# ARTICLE 3: Chennai Grand Masters + Indian chess
# ─────────────────────────────────────────────

articles.append({
    "headline": "World Champion Gukesh Headlines India's Strongest Chess Tournament as Chennai Rolls Out the Red Carpet.",
    "subheadline": "The Quantbox Chennai Grand Masters returns for its fourth edition with a ₹75 lakh prize pool, a field featuring Gukesh, Erigaisi, Firouzja, and Niemann, and FIDE Circuit points on the line.",
    "slug": "chennai-grand-masters-2026-gukesh-erigaisi-firouzja-niemann-pragg-gct-india-chess-dominance-nri",
    "body": """Chennai has always been Indian chess's spiritual home. On July 16, when the Quantbox Chennai Grand Masters begins its fourth edition at The Westin Chennai Velachery, the city will stake a fresh claim to being one of the world's elite chess capitals.

The Masters field reads like a who's who of modern chess: reigning World Champion Gukesh Dommaraju, India's number-two Arjun Erigaisi, former World Rapid Champion Nodirbek Abdusattorov, two-time Grand Chess Tour champion Alireza Firouzja, 2026 Bullet Chess champion Nihal Sarin, former Candidates challenger Dmitry Andreikin, controversial American Grandmaster Hans Niemann, and last year's Challengers champion Pranesh M, who earned his promotion the hard way.

The combined prize pool stands at ₹75 lakh (approximately $90,000), with ₹25 lakh for the winner. But for several players, the real prize is the FIDE Circuit points that count toward qualification for the next Candidates Tournament — the gateway to a World Championship shot.

## A Tournament That Launched a World Champion

The Chennai Grand Masters has already proved it can be a career launchpad. In its inaugural 2023 edition, Gukesh won the title and earned enough FIDE Circuit points to qualify for the 2024 Candidates Tournament. He went on to defeat Ding Liren for the World Championship that December, becoming the youngest world champion in history at 18. Gukesh returns to Chennai as the defending world champion and the tournament's most decorated alumnus.

Last year, Aravindh Chithambaram used his Chennai Grand Masters victory to catapult himself into the world's top 10. The pattern is clear: this tournament identifies India's next chess superstar before the rest of the world catches on.

## Praggnanandhaa's Spectacular Run

While Gukesh and Erigaisi prepare for Chennai, their compatriot R. Praggnanandhaa has been on a tear across the international circuit. The 20-year-old won Norway Chess 2026 — beating Magnus Carlsen twice in the process — and followed it with a strong joint-third finish at the Grand Chess Tour's Croatia leg, tying on 21.5 points with France's Maxime Vachier-Lagrave.

In the GCT's Croatia event, Firouzja claimed the title in dramatic fashion, defeating Uzbekistan's Abdusattorov in an Armageddon tiebreak after both ended on 23.5 points. Gukesh finished sixth after a rocky start that included a first-round loss to Vachier-Lagrave, though he recovered with wins over Ivan Šarić and Praggnanandhaa.

In the overall GCT tour standings, Fabiano Caruana leads with 20 points, followed by Germany's Vincent Keymer on 19 and Firouzja on 18. Praggnanandhaa sits sixth on 11.5 points with two events remaining — the Saint Louis Rapid & Blitz and the Sinquefield Cup — both in late July and August.

## India's Chess Golden Age — And What It Means for the Diaspora

The numbers tell a story that would have seemed fantastical a decade ago. India now has the reigning World Champion (Gukesh), the reigning Norway Chess champion (Praggnanandhaa), and two players — Erigaisi and Praggnanandhaa — ranked in the world's top 10. At the 2024 Chess Olympiad, India won gold in both the Open and Women's sections. Vaishali Rameshbabu, Praggnanandhaa's sister, won the 2026 Women's Candidates Tournament.

For the Indian American community, this chess renaissance carries a particular resonance. Chess clubs in the Bay Area, New Jersey, and Dallas — regions with significant NRI populations — are overflowing with young Indian American players inspired by Gukesh and Pragg. The Chennai Grand Masters itself is accessible via live streams on popular chess YouTube channels, making it appointment viewing for diaspora families.

Tamil Nadu's Deputy Chief Minister Udhayanidhi Stalin recently honored Gukesh, Praggnanandhaa, and Chithambaram for their performances at international events — a sign of how chess has moved from a niche pursuit to a source of national and state pride.

The tournament runs from July 16 to 22, with live commentary available on ChessBase India and other platforms. For NRIs who grew up watching Viswanathan Anand carry Indian chess alone, the current generation is delivering something extraordinary: a depth of talent that suggests India's dominance is not a flash in the pan, but a structural shift in the sport's global power map.""",
    "category": "sports",
    "vertical": "chess",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/6d/Gukesh_in_2025_%28cropped%29.jpg",
    "image_caption": "Reigning World Chess Champion D. Gukesh, who headlines the 2026 Quantbox Chennai Grand Masters field",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "India's chess golden age — with Gukesh as world champion, Pragg winning Norway Chess, and multiple top-10 players — is inspiring a wave of young Indian American chess players across the US.",
    "sources": json.dumps([
        {"name": "RevSportz", "url": "https://www.revsportz.in"},
        {"name": "Dainik Bhaskar English", "url": "https://www.bhaskarenglish.in"},
        {"name": "Chess.com", "url": "https://www.chess.com"},
        {"name": "Wikipedia - Grand Chess Tour 2026", "url": "https://en.wikipedia.org/wiki/Grand_Chess_Tour_2026"}
    ]),
    "score_total": 8
})


# ─────────────────────────────────────────────
# INSERT ALL ARTICLES
# ─────────────────────────────────────────────

print(f"\n{'='*60}")
print(f"Videshi Sports Writer — {now}")
print(f"{'='*60}\n")

success_count = 0
for article in articles:
    if insert_article(article):
        success_count += 1
    print()

print(f"{'='*60}")
print(f"Results: {success_count}/{len(articles)} articles inserted successfully")
print(f"{'='*60}")
