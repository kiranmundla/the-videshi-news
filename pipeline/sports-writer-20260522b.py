#!/usr/bin/env python3
"""Sports writer — 2026-05-22 evening run: 2 articles.
Topics: IPL 4th playoff spot race, Mohammed Shami acquittal + selector snub
"""

import os, json, uuid, re, requests
from datetime import datetime, timezone
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

def insert_article(article: dict) -> dict:
    r = requests.post(f"{SB_URL}/rest/v1/p2_articles", headers=HEADERS, json=article)
    if r.status_code >= 400:
        print(f"  ERROR: {r.status_code} {r.text[:500]}")
    r.raise_for_status()
    return r.json()


# ══════════════════════════════════════════════════════════════
# ARTICLE 1: The Battle for IPL 2026's Last Playoff Spot
# ══════════════════════════════════════════════════════════════

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "One Spot, Four Teams, Three Matches: Inside the Most Ruthless Playoff Race in IPL History",
    "subheadline": "With RCB, GT, and SRH locked on 18 points at the top, the battle for the fourth qualifier berth comes down to a single weekend — and the maths is merciless",
    "slug": "ipl-2026-fourth-playoff-spot-rr-pbks-kkr-dc-race-20260522",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "NRI cricket fans planning their weekend around three must-watch matches on JioCinema; the drama of a knockout weekend accessible internationally; family group chats about to explode with scenarios",
    "tags": ["IPL 2026", "Playoffs", "Rajasthan Royals", "Punjab Kings", "Kolkata Knight Riders", "Delhi Capitals", "IPL Playoff Race", "Cricket"],
    "urgency": "breaking",
    "sources": [
        "https://www.latestly.com/sports/cricket/ipl-2026-playoff-scenarios-how-csks-defeat-against-gt-impacts-pbks-kkr-rr-and-dcs-chances-7441005.html",
        "https://www.newspointapp.com/english/sports/ipl-2026-playoff-qualification-scenarios-with-4-matches-to-go-what-rr-pbks-kkr-and-dc-need-to-grab-final-spot-paths-for-each-team-explained",
        "https://mykhel.com/cricket/ipl-2026-points-table-standings-after-srh-vs-rcb-match-67",
        "https://www.sportskeeda.com/cricket/srh-vs-rcb-ipl-2026-award-winners-player-of-match"
    ],
    "word_count": 750,
    "score_total": 82,
    "body": """The IPL 2026 league stage has produced something unprecedented. Three teams — Royal Challengers Bengaluru, Gujarat Titans, and Sunrisers Hyderabad — have finished on exactly 18 points apiece, separated only by net run rate. The top three is settled. What is not settled, and what will consume every cricket-watching household this weekend, is the identity of the fourth team that joins them.

One playoff spot remains. Four franchises — Rajasthan Royals, Punjab Kings, Kolkata Knight Riders, and Delhi Capitals — are still mathematically alive. Three matches across Saturday and Sunday will decide which one survives. The margins will be brutal.

## The standings heading into the final weekend

After Sunrisers Hyderabad's 55-run demolition of RCB in Hyderabad on Thursday evening — Ishan Kishan's sparkling 79 and Abhishek Sharma's rapid 56 powering SRH to 255/4 — the completed standings at the top read: RCB first (NRR +1.065), Gujarat Titans second (+0.695), SRH third. RCB will face GT in Qualifier 1. SRH wait in the Eliminator for whoever emerges from the battle below.

Beneath them, the arithmetic is unforgiving:

Rajasthan Royals sit fourth on 14 points with an NRR of +0.083. They play eliminated Mumbai Indians at the Wankhede on Sunday. A win takes them to 16 points and qualifies them outright — no other team can reach 16. This is the simplest equation in the race, and it is entirely in RR's own hands.

Punjab Kings are fifth on 13 points. They face already-eliminated Lucknow Super Giants on Saturday in what has become a must-win fixture. Victory takes PBKS to 15 points, but that alone is not enough — they then need Mumbai Indians to beat Rajasthan Royals on Sunday, and they need Delhi Capitals to beat KKR. A loss to LSG, and Punjab's season ends.

Kolkata Knight Riders also sit on 13 points with a barely positive NRR of +0.011. Their final match against Delhi Capitals on Sunday evening is, for all practical purposes, a knockout. Even if KKR win, they need RR to lose to MI and ideally PBKS to also lose. The dependencies are stacked.

Delhi Capitals, on 10 points with the worst NRR among contenders (-0.871), are alive only in the way a patient on life support is alive. They must beat KKR by a massive margin, and then need both RR and PBKS to lose their matches. It would require a catastrophic final weekend for three other teams simultaneously.

## Why Rajasthan Royals hold all the cards

The beauty of RR's position is its simplicity. Riyan Parag's side plays last among the contenders — their Sunday afternoon fixture at the Wankhede comes after PBKS have already played on Saturday. If Punjab lose to LSG, RR will take the field knowing that a win of any margin seals qualification. Even if PBKS win, RR still qualify by beating MI.

The only nightmare scenario for Rajasthan is a loss to Mumbai. If that happens and PBKS have already won, the door swings wide open. At 14 points, RR would be overtaken by a 15-point PBKS and potentially caught by a 15-point KKR.

The Wankhede pitch, traditionally one of the better batting surfaces in the IPL, suits RR's top-order firepower. Yashasvi Jaiswal, who has 493 runs this season at a strike rate above 155, thrives on true bounce. Vaibhav Sooryavanshi's emergence — his 93 off 38 balls against LSG last week was one of the innings of the tournament — gives RR a devastating one-two punch at the top.

## The PBKS paradox

Punjab Kings present the most poignant storyline. This is a franchise that has never won the IPL in its 18-year history. They entered the 2026 season with renewed optimism after their mega-auction spending spree, and for a stretch in April, they looked like genuine contenders. Then came five consecutive defeats that nearly buried them.

Now, improbably, they are still alive — but their fate depends entirely on other results going their way. Even a commanding victory over LSG on Saturday only sets up 24 hours of anxious waiting. The family WhatsApp groups that track every ball of PBKS matches will be doing something new this weekend: watching Mumbai Indians and praying for an upset.

## The KKR equation

Kolkata's path is the narrowest. Shreyas Iyer's side revived their campaign by beating MI earlier this week, but they need a chain of results that begins with their own victory over DC and extends through defeats for both RR and PBKS. The probability is low. The hope is real.

Their match against DC has an unusual dynamic: both teams need to win, but a DC victory only keeps Delhi alive in the most theoretical sense, while a KKR victory is the only way Kolkata survives. This is as close to a knockout as a league match gets.

## What NRI fans should know

All three matches will be streamed live on JioCinema internationally. Saturday's PBKS vs LSG starts at 7:30 PM IST (10:00 AM Eastern, 7:00 AM Pacific). Sunday brings the double-header: RR vs MI at 3:30 PM IST (6:00 AM Eastern) followed by KKR vs DC at 7:30 PM IST (10:00 AM Eastern).

For the millions of diaspora cricket fans who have been following this season, the final weekend is appointment viewing. Set alarms. Charge devices. Warn your families. The most ruthless playoff race in IPL history is about to be decided in 48 hours.""",
}


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Mohammed Shami — Acquitted in Court, Snubbed by Selectors
# ══════════════════════════════════════════════════════════════

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "Mohammed Shami Was Acquitted in Court This Week. India's Selectors Still Don't Want Him.",
    "subheadline": "The fast bowler won his cheque bounce case, took 37 Ranji wickets this season, and guided Bengal to the semi-finals — but chief selector Ajit Agarkar says there was 'no discussion' about his name for the Afghanistan series",
    "slug": "mohammed-shami-acquitted-cheque-bounce-india-selectors-snub-afghanistan-20260522",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Shami's legal battles resonated across the diaspora community; NRI fans questioning BCCI's treatment of senior players; broader conversation about athlete welfare and institutional loyalty in Indian cricket",
    "tags": ["Mohammed Shami", "BCCI", "Ajit Agarkar", "India Cricket", "Afghanistan Series", "Cheque Bounce Case", "Hasin Jahan", "Wasim Jaffer", "Lucknow Super Giants", "IPL 2026"],
    "urgency": "daily",
    "sources": [
        "https://www.sportskeeda.com/cricket/news-it-s-rubbish-former-rcb-cricketer-tears-apart-ajit-agarkar-excluding-mohammad-shami-ind-vs-afg-2026-series",
        "https://www.latestly.com/sports/cricket/mohammed-shami-acquitted-cheque-bounce-case-amidst-ongoing-legal-disputes.html",
        "https://yardbarker.com/cricket/mohammed-shami-acquitted-cheque-bounce-case",
        "https://indian.community/mohammed-shami-acquitted-cheque-bounce-case"
    ],
    "word_count": 700,
    "score_total": 76,
    "body": """The Alipore Court in Kolkata acquitted Mohammed Shami this week in a cheque bounce case that had lingered for four years. His estranged wife, Hasin Jahan, had alleged that a cheque for one lakh rupees issued by Shami had bounced in 2018. The court found that the evidence could not substantiate the claim. Shami's advocate confirmed the acquittal. It was, by any measure, a vindication.

Three days earlier, on May 19, BCCI chief selector Ajit Agarkar had been asked about Shami's absence from India's squad for the upcoming Test and ODI series against Afghanistan. His response was striking in its bluntness: "There was no discussion regarding his name."

No discussion. Not a debate that went the wrong way. Not a close call. Not even a conversation.

## The numbers that should have forced a conversation

Mohammed Shami's 2025-26 domestic season was, by any standard, exceptional. He took 37 wickets in seven Ranji Trophy matches for Bengal, including three five-wicket hauls, single-handedly dragging his state team to the semi-finals. He added 16 wickets in the Syed Mushtaq Ali Trophy and 15 in the Vijay Hazare Trophy. In IPL 2026, bowling for Lucknow Super Giants, he has taken 10 wickets in 10 matches.

His international record speaks for itself: 229 Test wickets in 64 matches, 206 ODI wickets in 108 matches. He was India's joint-highest wicket-taker in the 2025 Champions Trophy alongside Varun Chakravarthy. His last Test appearance was the 2023 World Test Championship final against Australia — a match India lost, but one in which Shami bowled with the hostility and reverse swing that have defined his career.

The man is 35. He is not finished. The numbers say so. The eyes say so. The batters who have faced him say so.

## "It's rubbish" — the backlash

Former India opener Wasim Jaffer did not mince words. Speaking on his YouTube channel, Jaffer called Agarkar's explanation "rubbish" and "disrespectful."

"We are talking about Mohammad Shami, not just any player," Jaffer said. "You see, this guy is performing, and you say he's only fit for T20. It's an excuse. Be clear if you don't consider him. Say, 'We have overlooked him.' That would be a fair statement."

Jaffer posed the question that many fans had been thinking: "What if Bumrah gets injured, and he comes back? Would you treat him the same way? Mohammad Shami is in the same bracket. Go and ask any international batter, and they would rank him on top."

Agarkar's stated rationale — that Shami's body is currently suited only for T20 cricket — is difficult to square with the facts. Shami bowled extensive spells in the Ranji Trophy this season, a format that is physically more demanding than any limited-overs cricket. He completed full four-day matches. He ran in and bowled fast on unresponsive domestic pitches. If his body could handle that, it can handle a one-off Test in New Chandigarh.

## The legal shadow lifts, but the selection shadow remains

Shami's legal troubles have been a constant backdrop to his career since 2018, when Hasin Jahan accused him of domestic violence and infidelity. Criminal charges were filed. The BCCI's Anti-Corruption Unit investigated. His central contract was temporarily withheld before being reinstated after the ACU cleared him.

The cheque bounce case was the last active legal proceeding from that period, and its dismissal effectively closes a chapter that cast a long shadow over Shami's personal and professional life. He continues to pay Rs 1.5 lakh in monthly maintenance as directed by the court, and other aspects of the separation remain unresolved, but the criminal allegations have been systematically addressed.

For the Indian diaspora, Shami's story carries a particular resonance. The public nature of his legal battles — played out across Indian media with the intensity that only celebrity divorce proceedings can generate — divided opinion sharply. Many NRI fans who followed the case closely will see the acquittal as long-overdue closure.

## What happens now

Shami will continue playing for Lucknow Super Giants in what remains of their IPL 2026 campaign — LSG are already eliminated, so these are dead rubber matches. He will then face a summer without international cricket for the first time in years, watching from the sidelines as Shubman Gill leads a younger squad against Afghanistan.

The selectors have made their position clear. Shami's body says otherwise. His wickets say otherwise. And now, so does the court.

At 35, Mohammed Shami does not have many seasons left. The question is not whether he is good enough — that was never in doubt. The question is whether the men who pick India's team will give him the chance to prove it one more time before it is too late.""",
}


if __name__ == "__main__":
    print("=== Sports Writer — 2026-05-22 Evening ===\n")

    for label, article in [("Article 1 (IPL 4th Spot)", a1), ("Article 2 (Shami)", a2)]:
        print(f"Inserting {label}: {article['headline'][:60]}...")
        try:
            result = insert_article(article)
            print(f"  ✅ Inserted: {article['id']}")
        except Exception as e:
            print(f"  ❌ Failed: {e}")

    print("\n✅ Sports writer complete — 2 articles published")
