#!/usr/bin/env python3
"""Sports writer — 2026-05-23 14:00 PDT run: 2 articles + score decay."""

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

# ── ARTICLE 1: Shreyas Iyer maiden IPL century ──────────────
a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Shreyas Iyer Waited Nine Years for His First IPL Hundred. He Hit the Winning Six to Get There.",
    "subheadline": "The Punjab Kings captain scored 101 not out off 51 balls — 11 fours, 5 sixes, strike rate 198 — to chase down 197 against Lucknow Super Giants in a do-or-die match at Ekana Stadium. His teammate Suryansh Shedge deliberately refused singles so Iyer could reach the landmark. Punjab are back in the top four.",
    "slug": "shreyas-iyer-maiden-ipl-century-punjab-kings-beat-lsg-playoff-alive-20260523",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Shreyas Iyer is among the most followed Indian cricketers in the NRI market; Punjab Kings' ₹26.75 crore bet on him at auction is the kind of IPL business story that trends in Indian WhatsApp groups globally; Arjun Tendulkar's LSG debut — Sachin's son playing IPL in a dead rubber — is a generational touchpoint for diaspora families who grew up worshipping his father",
    "tags": ["Shreyas Iyer", "Punjab Kings", "IPL 2026", "Maiden IPL Century", "LSG vs PBKS", "Arjun Tendulkar", "Rishabh Pant", "Prabhsimran Singh", "Yuzvendra Chahal", "IPL Playoffs", "Ekana Stadium"],
    "urgency": "breaking",
    "sources": [
        "https://www.yardbarker.com/cricket/articles/shreyas_iyer_gets_his_maiden_ipl_century_as_punjab_kings_defeats_lucknow_super_giants_by_7_wickets/s1_17726_43875157",
        "https://www.insidesport.in/cricket/lsg-vs-pbks-ipl-2026-shreyas-hits-ton-as-punjab-win-big",
        "https://www.khelja.in/shreyas-iyer-maiden-ipl-century-vs-lsg",
        "https://www.livemint.com/sports/arjun-tendulkar-makes-lucknow-super-giants-debut-lsg-vs-pbks-ipl-2026",
        "https://www.crictracker.com/cricket-news/lsg-vs-pbks-ipl-2026-match-68/"
    ],
    "word_count": 730,
    "score_total": 75,
    "body": """Shreyas Iyer has played 115 IPL matches across three franchises since his debut in 2015. He has captained the Delhi Capitals to a final. He has led the Kolkata Knight Riders to a title. He has hit sixes that cleared stadiums and played innings that won games single-handedly. Through all of it — 115 matches, 11 seasons, three cities — he had never scored a hundred.

On Friday evening at the Ekana Cricket Stadium in Lucknow, needing three runs to win and three runs for his century with one ball to face, Iyer deposited Mohammed Shami over long-on for six. The ball disappeared into the stands. Iyer stood in the middle of the pitch, helmet off, arms spread, grinning like a man who had set down something very heavy.

One hundred and one not out. Fifty-one balls. Eleven fours. Five sixes. A strike rate of 198.03. And Punjab Kings lived to fight another day.

## The chase

It did not begin well. Priyansh Arya was bowled by Shami for a duck off the first ball of the innings. Cooper Connolly fell for 18. At 27 for 2 in the powerplay, Punjab were chasing 197 with their season on the line and their two openers back in the dugout.

What followed was a 142-run partnership between Iyer and Prabhsimran Singh that effectively killed the contest. Prabhsimran scored 60 off 39 balls — a compact, muscular innings full of pulls through midwicket and drives through cover — and gave Iyer the platform to accelerate.

Iyer started slowly by his standards. He was 30 off 25 balls at one stage, feeling his way in, respecting the pace of Mohsin Khan and the turn of Digvesh Singh Rathi. Then something switched. Between overs 12 and 18, Iyer scored 71 runs off 26 balls. He hit Shami back over his head for six. He slapped Arjun Tendulkar through point for four. He reverse-swept Prince Yadav for another boundary. The Lucknow bowlers, defending a total that had felt competitive twenty minutes earlier, had no answers.

The most telling moment came in the final over. Suryansh Shedge, Iyer's batting partner, deliberately turned down singles to keep the captain on strike. Iyer needed 11 off 6 balls and reached his hundred with the winning blow — a statement that was part celebration, part relief, and entirely Shreyas Iyer.

"I've waited a long time," Iyer said in the post-match presentation, his voice breaking slightly. "I've always wanted to win games for my team, and a hundred just… it's been on my mind, I won't lie."

## LSG's consolation: Inglis, Badoni, and a debut

Lucknow Super Giants, already eliminated and playing for pride under overcast Lucknow skies, posted a competitive 196 for 6 built on Josh Inglis's 72 off 44 balls. The Australian wicketkeeper was imperious — sweeping Yuzvendra Chahal over square leg, driving Marco Jansen through the covers — until Shashank Singh held a sharp catch off his own bowling to end the innings's best knock.

Ayush Badoni contributed a blistering 43 off 18 balls, and Abdul Samad's late cameo added useful runs. But it was the debut of Arjun Tendulkar that drew the loudest cheers from a crowd that had little else to celebrate.

Tendulkar, the 26-year-old left-arm pacer and son of Sachin, was introduced in the 18th over. His first ball was driven for two. His second drifted down leg and was called a wide. He finished with figures of 0 for 17 off one over — modest, unremarkable, and entirely beside the point. Arjun Tendulkar played an IPL match. For every Indian family — in Lucknow, in London, in San Jose — that watched Sachin bat through the nineties, that sentence carries its own weight.

Rishabh Pant's lean season continued: 26 off 22 balls before Chahal foxed him with a googly. Chahal, who had been expensive in recent matches, finished with 2 for 25 from his four overs — his best figures since mid-April.

## What it means for the playoff race

Punjab Kings' seven-wicket win moves them back into the top four with 15 points and a net run rate of +0.309. Crucially, Delhi Capitals are now mathematically eliminated — KKR's match against DC at Eden Gardens tomorrow is a dead rubber for Delhi but a season-defining game for Kolkata.

The scenario for PBKS is simple but depends on others: they need the Rajasthan Royals to lose to the Mumbai Indians at the Wankhede Stadium on Sunday afternoon. If RR win, Punjab go home despite Iyer's century, despite the comeback from six consecutive defeats, despite everything.

"We'll support MI tomorrow," Iyer said with a laugh. "But we've done our job. Whatever happens now, we've given ourselves a chance."

Tomorrow is Super Sunday — the final day of the league stage. Two matches, three teams still alive for one remaining playoff spot. The IPL has saved its most chaotic day for last.""",
}

# ── ARTICLE 2: Super Sunday Preview — The Final Day ──────────────
a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "Three Teams. One Spot. Two Matches. The IPL's Final League Day Is Going to Be Chaos.",
    "subheadline": "On Super Sunday, Mumbai Indians play Rajasthan Royals at the Wankhede and Kolkata Knight Riders face Delhi Capitals at Eden Gardens. Only one of PBKS, RR, and KKR will claim the last playoff berth — and the scenarios are absurd enough that net run rate may decide everything",
    "slug": "ipl-2026-super-sunday-final-league-day-playoff-scenarios-pbks-rr-kkr-20260523",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "The IPL's final league day is the most-watched single day of the tournament among NRI audiences — desi WhatsApp groups globally will be tracking two simultaneous matches and doing NRR maths; Wankhede and Eden Gardens are emotional home venues for two of the largest NRI fanbases (Mumbai and Kolkata); the KKR angle resonates with Kolkata diaspora who are the most sentimental fanbase in the IPL",
    "tags": ["IPL 2026", "Super Sunday", "Playoff Race", "Mumbai Indians", "Rajasthan Royals", "Kolkata Knight Riders", "Delhi Capitals", "Punjab Kings", "Wankhede", "Eden Gardens", "Net Run Rate", "Sooryavanshi"],
    "urgency": "daily",
    "sources": [
        "https://www.latestly.com/socially/sports/cricket/ipl-2026-points-table-with-net-run-rate-pbks-playoff-hopes-alive-dc-eliminated",
        "https://m.cricbuzz.com/cricket-news/ipl-2026",
        "https://www.crictracker.com/cricket-news/ipl-2026-points-table-after-match-68/",
        "https://www.yardbarker.com/cricket/articles/lsg_vs_pbks_live_score_ipl_2026/",
        "https://www.insidesport.in/cricket/drs-may-23-srh-beat-rcb-angkrish-raghuvanshi-ruled-out-ipl-2026"
    ],
    "word_count": 700,
    "score_total": 68,
    "body": """The final day of the IPL league stage always produces something. A team that needed a miracle gets one. A team that thought they were safe watches the calculators turn against them. A net run rate swing of 0.002 sends one franchise into the playoffs and another into the off-season.

Super Sunday, May 24, will be all of that and more. Two matches. Three teams still in the hunt for one remaining spot. And a set of scenarios complicated enough to make a spreadsheet weep.

## The standings entering the final day

The top three are settled. Royal Challengers Bengaluru finished first despite losing their final match to Sunrisers Hyderabad. Gujarat Titans secured second place. Hyderabad are third and will play the Eliminator.

Below them, it's carnage. Punjab Kings sit fourth with 15 points and a net run rate of +0.309 after Shreyas Iyer's century against Lucknow on Friday. Rajasthan Royals are fifth, also on 15 points, with a slightly inferior NRR. Kolkata Knight Riders are sixth with 13 points — they need a win and significant help.

Delhi Capitals, once in the top four, are mathematically eliminated. Their season ended when Punjab beat Lucknow.

## Match 1: Mumbai Indians vs Rajasthan Royals — Wankhede Stadium

This is the one that matters most to Punjab Kings.

If Rajasthan lose, PBKS qualify regardless of what happens in Kolkata. If Rajasthan win, they leapfrog Punjab into the top four — unless KKR also win and leap above both on NRR, which would require a colossal margin at Eden Gardens.

For Mumbai Indians, there is nothing at stake in the table — they are mid-table, their season over — but there is everything at stake in reputation. The Wankhede is their fortress. Losing the final home game of the season, with 33,000 people watching, is not something any Mumbai Indians player wants on their record.

Rajasthan's batting will revolve around their extraordinary 15-year-old opener, Vaibhav Sooryavanshi, who has hit 53 sixes this season and is six away from breaking Chris Gayle's all-time single-season record. Sooryavanshi's presence gives this match a subplot that transcends the playoff race: a teenager chasing a record held by one of T20 cricket's most legendary figures, in a knockout match at the Wankhede, with his team's season depending on the outcome.

RR's bowling — led by Trent Boult and Sandeep Sharma — is experienced enough to defend most totals. But the Wankhede pitch has been a batting paradise this season, and MI's own lineup, particularly Rohit Sharma in his final home game of the tournament, can be devastating when there is nothing left to lose.

## Match 2: Kolkata Knight Riders vs Delhi Capitals — Eden Gardens

KKR's equation is simple in theory and nearly impossible in practice. They must beat Delhi Capitals — who have nothing to play for — and do so by a margin large enough to vault their net run rate above both PBKS and RR.

The maths is brutal. KKR's NRR currently sits well below Punjab's +0.309. Even a 100-run victory might not be enough depending on what happens at the Wankhede. This is the kind of scenario that exists in IPL playoff calculations every year and almost never actually materialises.

Compounding KKR's problems: Angkrish Raghuvanshi, their explosive young batter, has been ruled out of the match after sustaining injuries during their recent win over Mumbai Indians. His absence thins an already stretched batting lineup.

For Delhi, the match is a dead rubber — but dead rubbers at Eden Gardens, in front of the most emotionally invested fanbase in the IPL, rarely feel dead. Kolkata's crowd will treat this like a final. Whether the team can match that energy, with their playoff hopes hanging on calculators and other results, is the question.

## What NRIs will be watching

The IPL's final league day is, by viewing data, the most-watched single day of the group stage among overseas Indian audiences. It is the day when diaspora WhatsApp groups become real-time commentary streams, when Indian restaurants in Edison and Southall have the match on every screen, when the phrase "what's the NRR now?" is typed more often than any other sentence in the Indian internet.

Sunday's two matches start at different times — MI vs RR at 3:30 PM IST, KKR vs DC at 7:30 PM IST — which means the first result will be known before the second match begins. If Rajasthan lose in the afternoon, the evening match becomes academic for the playoff race. If they win, Eden Gardens will be electric.

This is what the IPL does better than any other cricket tournament: it takes the final day and turns it into a referendum on luck, margins, and mathematics. Three teams enter Sunday. One survives.""",
}

if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-23 14:00 PDT")
    print("=" * 60)

    print("\nInserting Article 1: Shreyas Iyer maiden IPL century...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    print("\nInserting Article 2: Super Sunday playoff preview...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    # Score decay
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    print(f"\nDone. 2 articles published (images pending).")
    print(f"  IDs: {a1_id}, {a2_id}")
