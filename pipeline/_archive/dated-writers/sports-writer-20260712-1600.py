#!/usr/bin/env python3
"""
Sports writer — 2026-07-12 16:00 PT
Two articles:
1. India Women's Test at Lord's Day 3 — Yastika Bhatia's maiden century, Heather Knight's farewell, India on brink of historic win
2. MLC 2026 Final Stretch — Unicorns pull clear at 12 points, race for 2nd and 3rd between LAKR and MI New York
"""
import os, json, subprocess, sys, re, uuid
from datetime import datetime, timezone

# ── Load env ──────────────────────────────────────────────────────────────
env_path = os.path.expanduser("~/workspace/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

def insert_article(article: dict) -> dict:
    """Insert article via Supabase REST API using curl."""
    payload = json.dumps(article)
    cmd = [
        "curl", "-sS", "-X", "POST",
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=representation",
        "-d", payload,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return json.loads(result.stdout)


# ═══════════════════════════════════════════════════════════════════════════
# ARTICLE 1 — India Women's Test at Lord's: Day 3
# ═══════════════════════════════════════════════════════════════════════════

article1_body = """India's women wrote another chapter of history at Lord's on Saturday as Yastika Bhatia struck her maiden Test century, India declared at a commanding 341 for 7 in their second innings, and England limped to 130 for 6 at stumps — still needing 327 runs with just one day remaining.

If India complete the job on Day 4, it will mark the first victory by any women's team in a Test match at the 212-year-old "Home of Cricket," a ground that hosted its first-ever women's Test only this week.

## Bhatia's Breakthrough

The 24-year-old left-hander from Vadodara resumed Day 3 unbeaten on 39 and batted with growing authority, reaching her century off 158 balls to emphatic applause from a packed Lord's pavilion. It was a patient, intelligent innings — her first three-figure score in the longest format — studded with elegant drives and decisive pulls. Sophie Ecclestone, England's all-time leading wicket-taker, finished with five for 118 from 33.3 overs but even her probing left-arm spin could not stem the tide.

Smriti Mandhana, who had scored 83 in the first innings, added 69 before falling, while Jemimah Rodrigues and captain Harmanpreet Kaur chipped in with useful cameos. India's declaration set England a daunting 457 to win — the highest-ever fourth-innings target in women's Test cricket.

## Knight's Last Stand

The day began with emotion and ended with pathos for England. Heather Knight, the 35-year-old former captain who had led the side on 199 occasions across 320 international appearances, announced mid-match that she would retire from international cricket after this Test. In a poignant echo of Ben Stokes's own mid-series retirement announcement last month, Knight chose Lord's as the stage for her farewell.

Knight walks away with nearly 8,000 international runs and six centuries, including the captaincy that guided England to their 2017 World Cup triumph — a final that was itself held at Lord's. Her departure, alongside Tammy Beaumont's last Test, signals the end of an era for England Women.

## England's Collapse

If Knight's retirement was the emotional blow, Kranti Gaud's first-innings five-wicket haul on Day 2 — the first time an Indian woman had her name inscribed on the Lord's honours board — was the tactical one. Gaud's 5 for 37 had bundled England out for 170 in reply to India's 285, creating the deficit that India ruthlessly exploited.

In the fourth innings, Amy Jones fought valiantly for her second fifty of the match, making 52 off 72 balls, but Sayali Satghare's economical spell of 2 for 19 in eight overs kept England's scoring rate suppressed. England need to survive 60 overs on the final day, or conjure the most improbable chase in the history of women's Tests.

## What It Means for the Diaspora

For the British-Indian community, seeing India's women dominate at Lord's carries a layered significance. The ground has been contested terrain — a symbol of cricketing establishment that, until this week, had never hosted a women's Test in its entire history. Mandhana's elegance, Bhatia's resolve, and Gaud's historic five-for are moments that resonate well beyond the scorecard.

For NRIs in the US, the match has attracted unusual attention. The highlights have trended on social media, and the narrative — India's women thriving while the men endure a T20I whitewash in the same country — has become a talking point at diaspora cricket clubs from New Jersey to the Bay Area.

Day 4 begins Monday at 10:30 AM BST (5:30 AM ET, 2:30 AM PT). England need 327 more runs with four wickets in hand. India need four wickets. History, almost certainly, awaits."""

article1 = {
    "headline": "Yastika Bhatia's Maiden Test Century Puts India One Day From a Historic Lord's Victory.",
    "subheadline": "The 24-year-old from Vadodara scored 113 as India declared at 341/7 and left England needing 327 more to survive. Heather Knight announced her retirement mid-match.",
    "slug": "yastika-bhatia-maiden-test-century-113-india-women-lords-day-3-historic-victory-knight-retirement-nri-july-2026",
    "body": article1_body.strip(),
    "category": "sports",
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "score_total": 8,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/69/Yastika_Bhatia.jpg",
    "image_caption": "Yastika Bhatia, who scored her maiden Test century of 113 at Lord's",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps([
        {"name": "Wikipedia — India women's cricket team in England in 2026", "url": "https://en.wikipedia.org/wiki/India_women%27s_cricket_team_in_England_in_2026"},
        {"name": "The Times — Heather Knight retires mid-game", "url": "https://www.thetimes.com/sport/cricket/article/heather-knight-retires-mid-game-kranti-gaud-lords-board"},
        {"name": "SportsTak — Day 2 recap", "url": "https://thesportstak.com/cricket/ind-vs-eng-after-kranti-gauds-heroics-smriti-mandhana-yastika-bhatia-power-india-on-day-2-at-lords-as-india-women-lead-by-269-runs"},
        {"name": "Sportradar — Live match data", "url": "https://sportradar.com"}
    ]),
    "diaspora_angle": "India's women dominating at Lord's — a ground that never hosted a women's Test in 212 years — resonates deeply with the British-Indian community and NRI cricket fans worldwide.",
}


# ═══════════════════════════════════════════════════════════════════════════
# ARTICLE 2 — MLC 2026's Final Stretch: Unicorns in Command
# ═══════════════════════════════════════════════════════════════════════════

article2_body = """With one week left in Major League Cricket's regular season, the San Francisco Unicorns have all but clinched the top spot — and the real drama is unfolding behind them.

After Saturday's results, the Unicorns sit atop the standings at 12 points from 10 matches, six clear of their nearest rivals. LA Knight Riders and MI New York are locked at six points apiece. The bottom three — Seattle Orcas, Texas Super Kings, and Washington Freedom — are all stranded at four points with time running out.

## Saturday's Double-Header

The Unicorns made light work of the Seattle Orcas at Marymoor Cricket Community Park Stadium in Redmond, Washington, chasing down 191 in just 19 overs for the loss of four wickets. Seattle had posted a competitive 190 for 7, but San Francisco's batting lineup — bolstered by consistent contributions throughout the order — proved too deep.

Earlier in the day, Washington Freedom pulled off a gutsy chase against the Texas Super Kings at AirHogs Stadium in Grand Prairie, overhauling 166 with seven wickets down in the final over. It was a result that kept Freedom's slim mathematical hopes alive but effectively killed the Super Kings' playoff aspirations. Faf du Plessis's side, once the crowd favourites at their raucous Dallas home games, now face elimination unless results swing dramatically in their favour.

## The Race for Second and Third

The real battle is between LA Knight Riders and MI New York. Both teams have nine matches played and six points. With two to three matches remaining for each side, every game is effectively a knockout.

MI New York looked dominant on Sunday against Washington Freedom at Marine Park, posting 187 for 8 on the back of a stunning unbeaten 66 off 27 balls by Tajinder Singh and a captain's knock of 54 from Kieron Pollard. Meanwhile, the Knight Riders — fresh off handing the Unicorns their only loss of the season — face the struggling Texas Super Kings later Sunday.

The equation is straightforward: win your remaining games, and you are likely through. Lose, and the net run rate tiebreakers become brutal.

## What the Standings Mean

| Team | M | W | L | NR | Pts |
|------|---|---|---|----|----|
| SF Unicorns | 10 | 6 | 1 | 3 | 12 |
| LA Knight Riders | 9 | 3 | 1 | 5 | 6 |
| MI New York | 9 | 3 | 3 | 3 | 6 |
| Seattle Orcas | 10 | 2 | 5 | 3 | 4 |
| Texas Super Kings | 9 | 2 | 4 | 3 | 4 |
| Washington Freedom | 9 | 2 | 4 | 3 | 4 |

The season concludes on July 18, with the playoffs immediately following. The Unicorns have been the story of Season 4 — their only defeat came against the Knight Riders in a match that now looks more like a blip than a turning point.

## Cricket's American Moment

For NRIs, MLC's fourth season has been the most compelling yet. The league's expansion into new cities and dedicated cricket venues — including the Knight Riders' new purpose-built field and the Unicorns' temporary home at various Bay Area locations — has given diaspora cricket fans something they never had before: live, high-quality cricket they can attend on a summer weekend without flying to the Caribbean or crossing the Atlantic.

Crowd numbers have been growing, particularly in the Bay Area and Dallas, where the desi community has turned MLC matches into something between a sporting event and a cultural reunion. The Unicorns' dominance, powered by a mix of international stars and US-developed talent like left-arm seamer Saurabh Netravalkar, has given the league a bona fide flagship franchise.

The final week promises decisive action. Five of the six teams still have matches to play, and at least two must be eliminated before the playoffs begin. For fans in the US, every ball counts."""

article2 = {
    "headline": "Unicorns in Command, Three at Four Points. MLC 2026's Final Week Is a Reckoning.",
    "subheadline": "San Francisco leads by six points after beating Seattle. MI New York and LA Knight Riders are locked at six each. Three teams are staring at elimination.",
    "slug": "mlc-2026-final-week-standings-unicorns-command-knight-riders-mi-new-york-playoff-race-nri-july-2026",
    "body": article2_body.strip(),
    "category": "sports",
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "score_total": 8,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Knight_Riders_Cricket_Field_aerial_view.png/1280px-Knight_Riders_Cricket_Field_aerial_view.png",
    "image_caption": "Aerial view of Knight Riders Cricket Field, the new MLC venue in Los Angeles",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps([
        {"name": "Sportradar — MLC live match data", "url": "https://sportradar.com"},
        {"name": "SportsCafe — MLC 2026 standings", "url": "https://sportscafe.in/cricket/major-league-cricket-2026/points-table"},
        {"name": "Bhaskar English — MI New York beats Seattle", "url": "https://bhaskarenglish.in"},
        {"name": "CricTracker — Knight Riders Cricket Field hosts first match", "url": "https://crictracker.com"}
    ]),
    "diaspora_angle": "MLC gives NRIs in the US live, high-quality cricket they can attend on a summer weekend — the Bay Area and Dallas desi communities have turned matches into cultural reunions.",
}


# ═══════════════════════════════════════════════════════════════════════════
# Insert articles
# ═══════════════════════════════════════════════════════════════════════════

for i, article in enumerate([article1, article2], 1):
    print(f"\n{'='*60}")
    print(f"ARTICLE {i}: {article['headline']}")
    print(f"  slug: {article['slug']}")
    print(f"  image_url: {article['image_url']}")
    print(f"  image_caption: {article['image_caption']}")
    print(f"  category: {article['category']}")
    print(f"  vertical: {article['vertical']}")
    print(f"  status: {article['status']}")
    print(f"  body length: {len(article['body'])} chars / ~{len(article['body'].split())} words")
    print(f"{'='*60}")

    try:
        resp = insert_article(article)
        if isinstance(resp, list) and len(resp) > 0:
            print(f"  ✅ Inserted: id={resp[0].get('id','?')}, slug={resp[0].get('slug','?')}")
        elif isinstance(resp, dict) and resp.get("message"):
            print(f"  ❌ Error: {resp.get('message','unknown')}")
            print(f"     Details: {resp.get('details','')}")
            print(f"     Hint: {resp.get('hint','')}")
        else:
            print(f"  ⚠️ Unexpected response: {json.dumps(resp)[:300]}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")

print("\nDone.")
