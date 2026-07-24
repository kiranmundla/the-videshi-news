#!/usr/bin/env python3
"""Sports writer — 2026-05-22 evening run (20:00 PDT): 2 articles + score decay + data refresh.
Topics:
1. FIFA World Cup 2026 — India has no broadcaster, 3 weeks before kickoff
2. CSK eliminated for 3rd straight year + Dhoni's uncertain future
"""

import json, os, re, uuid, subprocess, sys, requests
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Supabase config ──
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

now = datetime.now(timezone.utc).isoformat()

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(headline, date_suffix="20260522"):
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: FIFA World Cup 2026 — India Has No Broadcaster
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "The FIFA World Cup Starts in 20 Days. India — 1.4 Billion People, the World's Largest Sports Market — Has No Broadcaster.",
    "subheadline": "Prasar Bharati told the Delhi High Court it's 'not responsible.' FIFA wanted $100 million, came down to $35 million, and Indian bids topped out at $20 million. The World Cup might be dark in India for the first time in living memory.",
    "body": """The 2026 FIFA World Cup kicks off on June 11 in Mexico City, when the host nation faces a yet-to-be-decided opponent in the tournament's expanded 48-team format. It will be the biggest World Cup in history — 104 matches across the United States, Mexico, and Canada over 39 days.

India will not be watching. Not legally, at least.

As of May 22, three weeks before the opening match, no Indian broadcaster — public or private — has acquired the rights to telecast the World Cup. The country that produces more cricket viewers than any tournament on earth, that filled stadiums for the Premier League and La Liga during the football boom of the 2010s, that has the fastest-growing football fan base among all major economies, has been locked out of the world's most-watched sporting event by a pricing dispute that no one seems willing to resolve.

## How We Got Here

The crisis has been building for months but escalated this week when Prasar Bharati — India's public service broadcaster, the entity that operates Doordarshan — told the Delhi High Court that acquiring FIFA World Cup rights is "not our responsibility."

The statement came during a hearing on a public interest petition seeking free-to-air telecast of the tournament. The petitioner argued that the failure to secure broadcast rights would deprive Indian citizens of their fundamental right to receive information. Prasar Bharati's response was blunt: it is a content provider that broadcasts on free-to-air channels, but it is not obligated to purchase international sports rights at any price.

The subtext is financial. FIFA initially valued the Indian media rights at $100 million — a figure that was greeted with disbelief by the Indian broadcasting industry. India has never been a premium football market in FIFA's rights framework. The previous World Cups were broadcast by Sony (2018) and Viacom18/JioHotstar (2022) at significantly lower fees. FIFA's $100 million ask was calibrated to the ambitions of the expanded tournament and the general inflation in global sports rights, not to the Indian market's actual willingness to pay.

Negotiations brought the price down to $35 million. Indian broadcasters countered at $20 million. The gap — $15 million — has remained unbridged. Doordarshan formally withdrew from negotiations earlier this month. Sony, Star (Disney), Zee, and Viacom18 have all passed. No regional broadcaster has stepped forward.

## Why It Matters for the Diaspora

For Indians living in the United States, the broadcast situation creates an unusual asymmetry. The World Cup is happening in their time zone, in their cities — matches will be played in New York, Houston, Dallas, San Francisco, and a dozen other metros with large Indian populations. Fox, Peacock, and Telemundo have US rights. Catching a match at a sports bar in Edison or Fremont will be straightforward.

But their families in India cannot watch. Parents, siblings, friends — the group chats that come alive during every major sporting event — will go dark. The shared experience that makes a World Cup a World Cup, the simultaneous joy across time zones, doesn't work when one end of the connection has no signal.

This is particularly acute for the football-following segment of the Indian diaspora, which tends to skew younger, urban, and globally connected. These are fans who grew up watching Messi and Ronaldo on Star Sports, who stayed up for Champions League nights, who tracked the Premier League table with the same intensity their parents tracked the Ranji Trophy. For them, the World Cup is the event that bridges their dual cultural identities — Indian by heritage, global by inclination.

## The Structural Problem

The broader issue is the economics of football broadcasting in India. Cricket generates massive viewership — IPL rights sold for $6.4 billion over five years. Football, despite growing interest, delivers a fraction of those numbers. The 2022 World Cup averaged 2-3 million viewers per match in India on JioCinema, compared to 30-40 million for an average IPL match.

For broadcasters, the math doesn't work at $35 million for a month-long tournament that generates a fraction of the ad revenue that cricket delivers. The timing compounds the problem: matches in the US and Mexico will kick off between 11:30 PM and 4:30 AM IST. Late-night viewership in India is structurally lower, which further depresses ad rates.

FIFA's counter-argument is that the World Cup is a tentpole event that builds brand equity and drives subscription growth. That logic works in markets where a broadcaster's survival depends on football — think BeIN Sports in the Middle East or DAZN in Europe. In India, where cricket is the currency, the World Cup is a nice-to-have, not an existential asset.

## What Happens Now

Three scenarios remain:

**A last-minute deal.** FIFA has historically been willing to negotiate aggressively close to the tournament. With 20 days to go, the price could drop further, potentially into the $20-25 million range where an Indian broadcaster might bite. JioHotstar, flush with IPL subscription revenue, is the most likely candidate. Alternatively, a digital-only deal with YouTube or a free streaming platform could materialize — FIFA has already partnered with YouTube for certain markets.

**A government intervention.** The Sports Broadcasting Signals (Mandatory Sharing with Prasar Bharati) Act, 2007 allows the government to designate sporting events of national importance and mandate sharing of broadcast signals. The World Cup could theoretically be brought under this provision, but it requires someone to hold the rights first.

**A blackout.** India goes dark. Fans resort to VPNs, pirate streams, and social media clips. The world's largest democracy doesn't see the world's largest sporting event. FIFA loses $20+ million in unrealized revenue. Indian football fans lose the one event that brings the sport into the mainstream conversation every four years.

For the diaspora, the blackout scenario has a particular sting. They will be watching the World Cup in 4K, in their time zone, possibly in the stadium — while India, the country they carry with them in every conversation about home, can't see a thing.

The World Cup starts June 11. The clock is ticking. And no one in India is picking up the phone.""",
    "diaspora_angle": "NRI fans in the US will watch the World Cup in their cities, their time zone, their language — but their families in India may have no legal way to see a single match. The broadcast blackout severs the shared viewing experience that connects diaspora sports fans to home.",
    "vertical": "sports",
    "tags": ["FIFA World Cup 2026", "India Broadcasting", "Prasar Bharati", "Doordarshan", "FIFA", "Football", "Sports Broadcasting"],
    "urgency": "high",
    "sources": json.dumps([
        {"url": "https://www.barandbench.com/news/prasar-bharati-delhi-high-court-fifa-world-cup-2026", "name": "Bar and Bench — Prasar Bharati HC Statement"},
        {"url": "https://www.bharathorizon.com/fifa-world-cup-2026-india-broadcast-limbo", "name": "Bharath Horizon — Broadcast Limbo"},
        {"url": "https://www.inshorts.com/en/news/prasar-bharati-delhi-hc-fifa-world-cup", "name": "Inshorts — Prasar Bharati Statement"},
        {"url": "https://www.govtserviceinfo.com/fifa-world-cup-2026-india-no-broadcaster", "name": "GovtServiceInfo — No Broadcaster"},
        {"url": "https://www.latestly.com/sports/football/prasar-bharati-fifa-world-cup-2026-broadcast-rights", "name": "LatestLY — Prasar Bharati Clarification"}
    ]),
    "slug": make_slug("fifa-world-cup-2026-india-no-broadcaster-blackout"),
    "word_count": 870,
    "status": "published",
    "is_featured": False,
    "category": "Sports",
    "published_at": now,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
    "score_total": 84
})


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: CSK's Three-Year Drought & Dhoni's Uncertain Exit
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "Chennai Super Kings Have Missed the Playoffs for Three Straight Years. Even Their Dressing Room Doesn't Know If Dhoni Is Coming Back.",
    "subheadline": "CSK were bowled out for 140 in 13.4 overs by Gujarat Titans — their heaviest defeat in IPL history. Captain Ruturaj Gaikwad says there's 'no clarity' on MS Dhoni's IPL future. For the diaspora, a franchise built on certainty has never been more uncertain.",
    "body": """Gujarat Titans posted 229 for 4 at the Narendra Modi Stadium on Wednesday night. Sai Sudharsan, immaculate in his timing, made 84. Shubman Gill contributed 64. The total was imposing but not unprecedented — this was a batting surface, and 229 was within the range of a competitive chase.

Chennai Super Kings were bowled out for 140 in 13.4 overs. Not chasing, exactly. More like folding. Mohammed Siraj, Kagiso Rabada, and Rashid Khan dismantled the batting order with the clinical efficiency of a team that had already secured a playoff spot and was simply passing time. CSK couldn't even occupy 20 overs.

The defeat — by 89 runs — is the heaviest in Chennai Super Kings' IPL history. It is also the largest margin of victory Gujarat Titans have ever recorded. For a franchise that defines itself through poise under pressure, that made MS Dhoni's composure its operating mythology, the numbers are jarring.

## Three Straight Years Without Playoffs

Chennai Super Kings finished seventh with 12 points from 14 matches — five wins, nine defeats. This is the third consecutive season without a playoff appearance, a drought that would have been unthinkable during the dynasty years when CSK's annual presence in the top four was as reliable as income tax.

The numbers since 2024 tell a story of institutional decline:

- **2024**: Finished sixth. 7 wins, 7 losses. NRR of -0.060.
- **2025**: Finished eighth. 5 wins, 9 losses. Last place.
- **2026**: Finished seventh. 5 wins, 9 losses. Bowled out for 140 in their final match.

Over three seasons, CSK have won 17 and lost 25. The trajectory is downward, and the reasons are structural — an ageing core, auction strategies that prioritized loyalty over capability, and the absence of the one man who made everything work.

## The Dhoni Question

MS Dhoni did not play a single match in IPL 2026. Multiple injuries — knee and back issues that have accumulated over a 20-year professional career — kept him out of the squad from the start. He was present at team meetings. He was seen in the dugout occasionally. He was not on the field.

After the GT defeat, captain Ruturaj Gaikwad was asked the question that every CSK press conference has been building towards: will Dhoni play in IPL 2027?

"Even in our dressing room, we don't have clarity on what's going to happen," Gaikwad said. "People will come to know next year."

The statement is remarkable for its honesty and its implication. The captain of CSK — a player who shares a dressing room with Dhoni, who has been groomed as his successor — does not know if the greatest finisher in IPL history will return. The franchise that once operated on the certainty of Dhoni's presence now operates on ambiguity.

## What Dhoni's Absence Means

Dhoni's influence on CSK was never purely statistical. His IPL batting average in the final five overs was among the highest in history. His stumping rate and DRS success rate were legendary. But the real value was architectural — he built the team culture, managed the bowling rotations, decided the match-ups, and provided the psychological anchor that allowed young players to perform beyond their natural capability.

Without him, CSK in 2026 looked like a franchise still organized around his ghost. The batting lineup lacked a middle-order anchor. The bowling rotations felt mechanical rather than intuitive. Gaikwad, a fine top-order batter, was left to carry burdens that Dhoni had shouldered effortlessly — leadership decisions under pressure that require experience, not just talent.

The comparison to GT's performance in the same match is instructive. Gujarat Titans, a franchise built by Hardik Pandya and now captained by Shubman Gill, have the youngest core in the IPL and the most forward-looking squad construction. CSK, by contrast, spent their 2024 mega-auction building a team around nostalgia — retaining Gaikwad and Ravindra Jadeja, buying back familiar faces, hoping that the culture would compensate for the absence of the culture's creator.

It didn't.

## The Diaspora Angle

For the Indian diaspora, CSK's decline is personal in a way that other franchise struggles are not. Dhoni is the most universally loved cricketer of his generation among NRIs — more than Kohli (who divides opinion), more than Rohit (who inspires less emotional attachment), more than Tendulkar (who belongs to an earlier generation of emigrants).

The "Whistle Podu" culture — CSK's fan identity, built on South Indian pride and Dhoni's unflappable demeanour — travels particularly well among the Tamil and South Indian diaspora. CSK shirts are the most commonly spotted cricket merchandise at Indian grocery stores in Edison, Devon Avenue, and Sunnyvale. The franchise's IPL matches are appointment viewing for families in the US who don't follow any other team.

Watching that franchise get bowled out for 140, and then hearing that even the captain doesn't know if Dhoni is coming back — that's not just a sports result. For the diaspora, it's the potential end of a shared ritual that has defined IPL viewing for 18 years.

The 2027 IPL mega-auction will tell us whether CSK can rebuild. The months before it will tell us whether Dhoni shows up. Until then, the franchise that never blinked is blinking.

*CSK's 2026 season is over. IPL 2026 playoffs begin May 27 with Qualifier 1 between RCB and Gujarat Titans.*""",
    "diaspora_angle": "Dhoni is the NRI favourite — the most universally loved cricketer among the diaspora. CSK's Whistle Podu culture is identity for the South Indian diaspora. The franchise's decline and Dhoni's uncertain exit mark the potential end of a shared ritual for diaspora IPL viewing.",
    "vertical": "sports",
    "tags": ["Chennai Super Kings", "MS Dhoni", "IPL 2026", "Ruturaj Gaikwad", "Gujarat Titans", "CSK", "IPL Playoffs", "Sai Sudharsan", "Shubman Gill"],
    "urgency": "daily",
    "sources": json.dumps([
        {"url": "https://www.mykhel.com/cricket/ipl-2026-news-digest-may-22-csk-eliminated-hardik-pandya-sanctioned-ms-dhoni-future-in-dark-434449.html", "name": "myKhel — CSK Eliminated, Dhoni Future"},
        {"url": "https://www.cricketworld.com/ipl-2026-match-67-bengaluru-end-on-top-spot/98218.htm", "name": "CricketWorld — Match 67 Summary"},
        {"url": "https://www.insidesport.in/cricket/srh-vs-rcb-ipl-2026-match-67", "name": "InsideSport — SRH vs RCB"},
        {"url": "https://www.mykhel.com/cricket/ipl-2026-points-table-standings-after-srh-vs-rcb-match-67", "name": "myKhel — Updated Points Table"}
    ]),
    "slug": make_slug("csk-three-year-drought-dhoni-uncertain-future-ipl"),
    "word_count": 810,
    "status": "published",
    "is_featured": False,
    "category": "Sports",
    "published_at": now,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
    "score_total": 80
})


# ══════════════════════════════════════════════════════════════
# INSERT ARTICLES
# ══════════════════════════════════════════════════════════════

print(f"=== Sports Writer — 2026-05-22 Evening (20:00 PDT) ===\n")
print(f"Publishing {len(articles)} sports articles...\n")
success = 0
for article in articles:
    try:
        result = sb_post("p2_articles", article)
        if isinstance(result, (list, dict)):
            print(f"  ✅ {article['headline'][:80]}...")
            success += 1
        else:
            print(f"  ⚠️  Unexpected: {json.dumps(result)[:200]}")
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ Error: {e}")
        print(f"     {e.response.text[:300]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print(f"\n📰 Articles: {success}/{len(articles)} published")


# ══════════════════════════════════════════════════════════════
# SCORE DECAY — age-based decay for older articles
# ══════════════════════════════════════════════════════════════

print("\n── Score Decay ──")
try:
    # Fetch all published articles with their scores
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?status=eq.published&select=id,score_total,published_at&order=published_at.desc",
        headers={**HEADERS, "Prefer": ""},
        timeout=30
    )
    r.raise_for_status()
    all_articles = r.json()
    now_dt = datetime.now(timezone.utc)
    decayed = 0
    for art in all_articles:
        if not art.get("published_at") or not art.get("score_total"):
            continue
        pub = datetime.fromisoformat(art["published_at"].replace("Z", "+00:00"))
        age_hours = (now_dt - pub).total_seconds() / 3600
        if age_hours < 6:
            continue  # Don't decay recent articles
        # Decay formula: lose 2 points per 6 hours after first 6h, min 10
        decay_amount = int(age_hours / 6) * 2
        new_score = max(10, art["score_total"] - decay_amount)
        if new_score < art["score_total"]:
            requests.patch(
                f"{SB_URL}/rest/v1/p2_articles?id=eq.{art['id']}",
                headers={**HEADERS, "Prefer": "return=minimal"},
                json={"score_total": new_score},
                timeout=10
            )
            decayed += 1
    print(f"  ✅ {decayed} articles decayed (of {len(all_articles)} total published)")
except Exception as e:
    print(f"  ❌ Score decay error: {e}")


# ══════════════════════════════════════════════════════════════
# REFRESH MARKET DATA
# ══════════════════════════════════════════════════════════════

print("\n── Markets Refresh ──")
try:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "videshi-markets.py")],
        capture_output=True, text=True, timeout=60,
        cwd=str(PROJECT_ROOT)
    )
    if result.returncode == 0:
        print(f"  ✅ Markets refreshed")
        # Print last few lines of output
        for line in result.stdout.strip().split("\n")[-4:]:
            print(f"     {line}")
    else:
        print(f"  ❌ Markets failed: {result.stderr[:200]}")
except Exception as e:
    print(f"  ❌ Markets error: {e}")


# ══════════════════════════════════════════════════════════════
# REFRESH MARKET CHARTS
# ══════════════════════════════════════════════════════════════

print("\n── Market Charts Refresh ──")
try:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "videshi-market-charts.py")],
        capture_output=True, text=True, timeout=120,
        cwd=str(PROJECT_ROOT)
    )
    if result.returncode == 0:
        print(f"  ✅ Market charts refreshed")
    else:
        print(f"  ❌ Market charts failed: {result.stderr[:200]}")
except Exception as e:
    print(f"  ❌ Market charts error: {e}")


# ══════════════════════════════════════════════════════════════
# REFRESH IPL STANDINGS
# ══════════════════════════════════════════════════════════════

print("\n── IPL Standings Refresh ──")
try:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "videshi-ipl.py")],
        capture_output=True, text=True, timeout=60,
        cwd=str(PROJECT_ROOT)
    )
    if result.returncode == 0:
        print(f"  ✅ IPL standings refreshed")
        for line in result.stdout.strip().split("\n")[-5:]:
            print(f"     {line}")
    else:
        print(f"  ❌ IPL standings failed: {result.stderr[:200]}")
except Exception as e:
    print(f"  ❌ IPL standings error: {e}")

# Update IPL standings JSON with recent results and upcoming
try:
    ipl_path = PROJECT_ROOT / "public" / "data" / "ipl-standings.json"
    if ipl_path.exists():
        ipl_data = json.loads(ipl_path.read_text())
        ipl_data["recent_results"] = [
            {"match": "Match 67", "date": "May 22", "teams": "SRH vs RCB", "result": "SRH won by 55 runs", "venue": "Hyderabad"},
            {"match": "Match 66", "date": "May 21", "teams": "GT vs CSK", "result": "GT won by 89 runs", "venue": "Ahmedabad"},
            {"match": "Match 65", "date": "May 20", "teams": "KKR vs MI", "result": "KKR won by 4 wickets", "venue": "Kolkata"},
            {"match": "Match 64", "date": "May 19", "teams": "RR vs DC", "result": "RR won by 29 runs", "venue": "Jaipur"},
            {"match": "Match 63", "date": "May 18", "teams": "PBKS vs CSK", "result": "PBKS won by 6 wickets", "venue": "Dharamsala"},
        ]
        ipl_data["upcoming"] = [
            {"match": "Match 68", "date": "May 23", "teams": "LSG vs PBKS", "time": "7:30 PM IST", "venue": "Lucknow"},
            {"match": "Match 69", "date": "May 24", "teams": "MI vs RR", "time": "3:30 PM IST", "venue": "Mumbai"},
            {"match": "Match 70", "date": "May 24", "teams": "KKR vs DC", "time": "7:30 PM IST", "venue": "Kolkata"},
        ]
        ipl_data["stage"] = "League stage complete for top 3. 3 matches remain for 4th playoff spot."
        ipl_data["last_updated"] = now
        ipl_path.write_text(json.dumps(ipl_data, indent=2))
        print(f"  ✅ IPL recent_results + upcoming + stage updated")
except Exception as e:
    print(f"  ⚠️  IPL JSON update error: {e}")


# ══════════════════════════════════════════════════════════════
# GIT PUSH
# ══════════════════════════════════════════════════════════════

print("\n── Git Push ──")
try:
    os.chdir(str(PROJECT_ROOT))
    subprocess.run(["git", "add", "public/data/"], capture_output=True, timeout=15)
    commit_result = subprocess.run(
        ["git", "commit", "-m", "data: sports writer + markets + IPL refresh (May 22 evening)"],
        capture_output=True, text=True, timeout=15
    )
    if "nothing to commit" in commit_result.stdout + commit_result.stderr:
        print("  ℹ️  No data changes to push")
    else:
        push_result = subprocess.run(
            ["git", "push", "origin", "main"],
            capture_output=True, text=True, timeout=30
        )
        if push_result.returncode == 0:
            # Extract commit hash
            log = subprocess.run(["git", "log", "--oneline", "-1"], capture_output=True, text=True, timeout=5)
            print(f"  ✅ Pushed: {log.stdout.strip()}")
        else:
            print(f"  ❌ Push failed: {push_result.stderr[:200]}")
except Exception as e:
    print(f"  ❌ Git error: {e}")


print("\n✅ Sports writer run complete.")
