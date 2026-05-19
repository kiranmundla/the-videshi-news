#!/usr/bin/env python3
"""Sports writer — 2026-05-19 run: 3 articles."""

import os, json, uuid, requests
from datetime import datetime, timezone

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
        print(f"  ERROR: {r.status_code} {r.text[:500]}")
    r.raise_for_status()
    return r.json()

def mark_topic(topic_id: str, status: str):
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_topics?id=eq.{topic_id}",
        headers=HEADERS, json={"status": status}
    )
    r.raise_for_status()

# ── ARTICLE 1: Aaron Rai PGA Championship ──────────────────────────────────
a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "From Wolverhampton to the Wanamaker: Aaron Rai's Historic PGA Championship Victory",
    "subheadline": "The Indian-origin golfer ends a 107-year English drought at Aronimink, claiming $3.69 million and a place in major championship history",
    "slug": "aaron-rai-pga-championship-indian-origin-golfer-20260519",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": "2026-05-19T12:00:00+00:00",
    "diaspora_angle": "Indian-origin golfer's historic major win; representation for South Asians in golf; inspiration for diaspora youth",
    "tags": ["Aaron Rai", "PGA Championship", "Golf", "Indian Diaspora", "Aronimink", "Wanamaker Trophy"],
    "urgency": "daily",
    "sources": [
        "https://www.golfchannel.com/pga-of-america/live/pga-championship-2026-live-updates-leaderboard-scores-highlights-and-news-from-final-round",
        "https://www.devdiscourse.com/article/sports-games/3370822-aaron-rais-historic-triumph-at-the-2026-pga-championship",
        "https://www.latestly.com/sports/ties-to-indian-culture-and-family-support-propel-golfers-of-indian-origin-to-pga-tour-success-6636241.html",
        "https://www.pgatour.com/news/2024/08/11/things-go-a-rai-at-wyndham-as-englishman-rallies-for-first-tour-title"
    ],
    "word_count": 750,
    "score_total": 72,
    "body": """When Aaron Rai sank a 70-foot birdie putt on the 17th hole at Aronimink Golf Club on Sunday, he did not merely seal a golf tournament. He wrote himself into sporting history and delivered a powerful message to every South Asian kid who has ever picked up a club.

Rai's final-round 65 — his best-ever score in a major — propelled the 31-year-old Englishman to a nine-under total and a commanding three-stroke victory over Jon Rahm at the 108th PGA Championship. The $3.69 million winner's cheque was handsome, but the symbolism was richer: Rai became the first Englishman to lift the Wanamaker Trophy since Jim Barnes in 1919, ending a 107-year drought.

## The eagle that changed everything

Heading into the back nine on Sunday, the leaderboard at Aronimink was a scrum. Matti Schmid held the solo lead, with Justin Thomas lurking in the clubhouse at five under and Rory McIlroy, Jon Rahm, and Cameron Smith all within striking distance.

Then came the par-5 ninth hole. Rai's eagle there vaulted him into contention, and he never looked back. Three birdies on the back nine — including a stunning long-range conversion on the 17th — opened up a gap that not even Rahm, who finished at six under, could close. Alex Smalley shared second place, while Thomas's clubhouse 65 ultimately proved three strokes short.

"Golf teaches you so many things — humility, discipline, absolute hard work," Rai said in the aftermath, his voice carrying the quiet composure that teammates and opponents alike have come to admire. "Nothing is ever given in this game. It's an absolute dream come true."

## Roots in the subcontinent

Rai was born in Wolverhampton, in England's West Midlands, to a family with deep Indian roots. His father introduced him to golf at a young age, and the sport became an unlikely obsession for a kid from a community where cricket and football reign supreme. He turned professional at just 17 — too early, by his own admission — and spent years grinding through Europe's Challenge Tour before establishing himself on the DP World Tour with victories at the 2020 Scottish Open and the Kenya Open (his mother is Kenyan, adding another strand to his multicultural identity).

His first PGA Tour win came at the 2024 Wyndham Championship, where he rallied with a final-round 64. But a major? At 150-1 odds entering the week, few outside his inner circle would have predicted this.

Jon Rahm, the runner-up, captured the mood in the locker room: "Anybody that uses head covers on his irons because he coveted them as a kid, and still does it to this day — that tells you a lot about the person. I've heard nothing but great things about Aaron Rai."

McIlroy was equally effusive: "You won't find one person on property who's not happy for him."

## What it means for South Asian golf

Rai joins a small but growing cohort of golfers with Indian heritage making waves on the PGA Tour. Sahith Theegala, an Indian-American who has become a fan favourite, and Akshay Bhatia, another Indian-origin rising star, have shown that the sport's demographics are shifting. But a major championship win — golf's ultimate validation — is a different magnitude of achievement.

For the estimated five million NRIs in the United States and millions more across the UK and Canada, Rai's victory carries a pride that transcends sport. In a discipline long associated with exclusive country clubs and overwhelmingly white leaderboards, an Indian-origin golfer hoisting one of the four most coveted trophies is a watershed moment.

## What Rai wins beyond the cheque

The PGA Championship victory brings a cascade of privileges: lifetime exemption into the PGA Championship, five-year exemptions into the Masters, US Open, The Open, and The Players Championship, plus five years of guaranteed PGA Tour membership and seven years on the DP World Tour. Rai also earns an automatic spot in the 2026 US Open at Shinnecock Hills, despite not being in the field before this week.

At 31, Rai is entering what should be the prime of his career. If Sunday at Aronimink was the start of something bigger, the game of golf — and the diaspora watching from thousands of miles away — will be all the richer for it.""",
}

# ── ARTICLE 2: Bumrah Rested, KL Rahul VC ──────────────────────────────────
a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "Bumrah Rested as India Unveil Refreshed Squad for Afghanistan Series",
    "subheadline": "KL Rahul named Test vice-captain while Manav Suthar and Gurnoor Brar earn maiden call-ups for June's home assignment",
    "slug": "bumrah-rested-india-afghanistan-test-squad-kl-rahul-vc-20260519",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": "2026-05-19T12:00:00+00:00",
    "diaspora_angle": "NRI-friendly series timing; accessible for overseas viewers; new faces in Indian cricket",
    "tags": ["Jasprit Bumrah", "KL Rahul", "India Cricket", "Afghanistan", "BCCI", "Test Cricket"],
    "urgency": "daily",
    "sources": [
        "https://www.cricketcountry.com/news/india-announce-squads-for-afghanistan-series-bumrah-rested-kl-rahul-named-test-vice-captain-1343438/",
        "https://www.techwordnews.com/all-eyes-are-on-jasprit-bumrahs-workload-ahead-of-the-afghanistan-series/",
        "https://www.cricketaddictor.com/cricket/shubman-gill-jasprit-bumrah-out-of-afghanistan-test-reason-schedule-squad-news/"
    ],
    "word_count": 700,
    "score_total": 68,
    "body": """The Board of Control for Cricket in India has drawn the curtain on weeks of speculation, announcing squads for the one-off Test and three-match ODI series against Afghanistan — and the most notable name is the one missing from the red-ball list.

Jasprit Bumrah, India's spearhead fast bowler, has been rested as part of the BCCI's workload management programme. In his absence, KL Rahul has been elevated to Test vice-captain, replacing Rishabh Pant in the leadership hierarchy. Shubman Gill will captain both the Test and ODI sides.

## A new-look Test squad

The 15-man Test squad carries a distinctly forward-looking feel. Left-arm spinning all-rounder Manav Suthar and left-arm pacer Gurnoor Brar have earned maiden call-ups, signalling the selectors' intent to build depth ahead of a punishing 2026-27 international calendar. Harsh Dubey, another left-arm spinner, adds further variety to the bowling attack.

**India's Test squad:** Shubman Gill (c), Yashasvi Jaiswal, KL Rahul (vc), Sai Sudharsan, Rishabh Pant, Devdutt Padikkal, Nitish Kumar Reddy, Washington Sundar, Kuldeep Yadav, Mohammed Siraj, Prasidh Krishna, Manav Suthar, Gurnoor Brar, Dhruv Jurel, Harsh Dubey.

Beyond Bumrah, the absentees from India's last Test squad are telling: Ravindra Jadeja, Axar Patel, and Akash Deep have all been left out. With India's last Test having ended in a sobering 2-0 home series defeat to South Africa in November, the selectors appear to be turning the page.

## The Rahul factor

KL Rahul's appointment as vice-captain is a significant signal. The 34-year-old was part of the furniture in India's Test middle order but had slipped in the pecking order during the South Africa series. His elevation suggests the selectors — and captain Gill — value his experience and composure in conditions where India will be overwhelming favourites.

It also raises questions about Rishabh Pant's standing in the leadership group, though Pant remains in the squad as the first-choice wicketkeeper-batsman.

## ODI squad brings back the big guns

The ODI squad tells a different story. Rohit Sharma and Virat Kohli return, alongside Hardik Pandya and Shreyas Iyer (who has been named ODI vice-captain). Arshdeep Singh and Prince Yadav bolster the pace contingent. Rohit and Pandya's inclusion is, however, subject to fitness clearance.

**India's ODI squad:** Shubman Gill (c), Rohit Sharma, Virat Kohli, Shreyas Iyer (vc), KL Rahul, Ishan Kishan, Hardik Pandya, Nitish Kumar Reddy, Washington Sundar, Kuldeep Yadav, Arshdeep Singh, Prasidh Krishna, Prince Yadav, Gurnoor Brar, Harsh Dubey.

## Schedule and what's at stake

The one-off Test is scheduled for June 6-10 in New Chandigarh — a fresh venue that will host its inaugural international match. The three ODIs follow in Dharamsala (June 14), Lucknow (June 17), and Chennai (June 20).

India and Afghanistan have met only once before in Tests — in Bengaluru in 2018, where the hosts dismantled the visitors by an innings and 262 runs inside two days. Afghanistan's red-ball programme has improved since then, but India remain prohibitive favourites at home.

## The diaspora viewing angle

For NRI cricket fans scattered across time zones, the series scheduling is more forgiving than winter tours to Australia or England. The June dates mean matches will overlap with summer evenings in North America and reasonable hours in the UK, making it one of the more accessible home series for overseas viewers. With India's squad carrying several exciting young names, it promises to be a worthwhile watch — even without Bumrah's thunderbolts.""",
}

# ── ARTICLE 3: IPL 2026 Playoff Picture ────────────────────────────────────
a3_id = str(uuid.uuid4())
a3 = {
    "id": a3_id,
    "headline": "IPL 2026 Playoff Picture: Three Teams Through, Seven Matches to Settle the Final Spot",
    "subheadline": "RCB, Gujarat Titans and Sunrisers Hyderabad have qualified, but five teams remain in a frantic scramble for the fourth berth",
    "slug": "ipl-2026-playoff-race-rcb-gt-srh-qualified-20260519",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": "2026-05-19T12:00:00+00:00",
    "diaspora_angle": "NRI fans following IPL climax overseas; streaming availability; time-zone-friendly scheduling",
    "tags": ["IPL 2026", "Playoffs", "RCB", "Gujarat Titans", "Sunrisers Hyderabad", "Mumbai Indians", "Cricket"],
    "urgency": "daily",
    "sources": [
        "https://www.durhamccc.co.uk/ipl-2026-points-table/",
        "https://www.mykhel.com/cricket/ipl-2026-playoff-scenario-how-can-teams-qualify-dc-beat-rr-may-17-638281.html",
        "https://www.crictracker.com/cricket-news/mumbai-indians-quinton-de-kock-raj-angad-bawa-ruled-out-ipl-2026/",
        "https://www.latestly.com/sports/ipl-2026-points-table-with-net-run-rate-srh-gt-qualify-for-playoffs-6657813.html"
    ],
    "word_count": 720,
    "score_total": 65,
    "body": """With seven league matches remaining and the IPL 2026 final less than a fortnight away, the tournament's familiar late-season drama is delivering on cue. Three teams have booked playoff berths; five are fighting for one remaining spot; and two have already begun planning for next year's auction.

## The confirmed three

**Royal Challengers Bengaluru** sit atop the table with 18 points from 13 matches (9 wins, 4 losses) and a formidable net run rate of +1.065. The defending champions have been the most consistent side this season, and a finish in the top two — which earns a second chance through the qualifier route — looks all but assured.

**Gujarat Titans** (16 points, +0.400 NRR) and **Sunrisers Hyderabad** (16 points, +0.350 NRR) have both qualified with a game to spare. SRH's clinical five-wicket victory over Chennai Super Kings on May 18 clinched their spot, while GT secured theirs on the back of an impressive campaign that saw them win eight of 13 matches. The battle between these two for second place — and the advantage that comes with it — will be resolved over the remaining fixtures.

## The battle for fourth

The race for the final playoff berth is spectacularly tight. Punjab Kings (13 points, one match remaining), Rajasthan Royals (12 points, two matches left), Chennai Super Kings (12 points, done for the league stage), Delhi Capitals (12 points, one remaining), and Kolkata Knight Riders (11 points, two matches left) are all mathematically in contention.

Punjab Kings, at 13 points with a positive NRR of +0.227, hold the inside track. But with CSK, RR, DC, and KKR all capable of leapfrogging on points or run rate, nothing is settled. Rajasthan Royals face Lucknow Super Giants tonight in Jaipur — a must-win fixture if they are to keep their campaign alive.

## Mumbai Indians' miserable finish

For Mumbai Indians, the 2026 campaign has been one to forget. Already eliminated from playoff contention at 8 points from 12 matches, the franchise was dealt a further blow when Quinton de Kock and Raj Angad Bawa were ruled out of the remainder of the season with injuries.

De Kock sustained a left wrist tendon injury before the April 29 match against Sunrisers Hyderabad and has been playing through pain. Bawa, the promising all-rounder, tore a ligament in his right thumb during the May 14 match against Punjab Kings. Both will undergo rehabilitation at home under the team's medical supervision.

MI face Kolkata Knight Riders and then Rajasthan Royals in their final two matches — dead rubbers for them, but potentially season-defining results for their opponents.

Lucknow Super Giants (8 points) have also been eliminated, leaving the tournament's final week as a contest between the ambitious middle order of the table.

## Key remaining fixtures

| Date | Match | Significance |
|------|-------|-------------|
| May 19 | RR vs LSG (Jaipur) | Must-win for Rajasthan |
| May 20 | KKR vs MI (Kolkata) | KKR need both remaining wins |
| May 21 | CSK vs GT (Chennai) | GT can seal 2nd place |
| May 22 | SRH vs RCB (Hyderabad) | Top-two shootout |
| May 23 | LSG vs PBKS (Lucknow) | PBKS's last chance |
| May 24 | MI vs RR (Mumbai) | Could decide RR's fate |
| May 24 | KKR vs DC (Kolkata) | Loser likely eliminated |

## Watching from abroad

For the millions of NRI fans following the tournament's climax across North America, the UK, and the Gulf, the scheduling gods have been relatively kind. Evening IST start times translate to morning and early afternoon in the Americas, while UK-based fans get a reasonable 3 PM start. Streaming platforms Willow TV (US/Canada) and Sky Sports (UK) carry every match live, with JioCinema available for viewers with VPN access.

The IPL's annual capacity to compress a season's worth of tension into its final ten days is, once again, in full effect. Seven matches. One spot. Five teams dreaming.""",
}

# ── Insert all articles ─────────────────────────────────────────────────────
for label, art in [("Article 1 (Aaron Rai)", a1), ("Article 2 (Bumrah/Afghanistan)", a2), ("Article 3 (IPL Playoff)", a3)]:
    result = insert_article(art)
    print(f"✅ {label} inserted: {result[0]['id']}")

# ── Mark topics ─────────────────────────────────────────────────────────────
topic_marks = [
    ("a503164e-e40b-4f1c-9486-f1dce49c3001", "published"),   # Aaron Rai PGA
    ("77a35958-0f28-4116-99b7-11ea7cf419cd", "published"),   # Bumrah rested
    ("ec33e022-158d-48b3-a69e-b59eb54280b2", "published"),   # Hyderabad IPL playoffs
    ("c3a25d43-a941-4801-a7dc-c25c62e765cd", "published"),   # MI de Kock/Bawa (dup 1)
    ("00e7c377-6754-462f-b7ef-f8889748d99b", "published"),   # MI de Kock/Bawa (dup 2)
    ("b148dc02-308f-498d-a59d-f612565f3e10", "rejected"),    # IPL bigger window — separate story
]
for tid, status in topic_marks:
    mark_topic(tid, status)
    print(f"  → Topic {tid[:8]} marked {status}")

print(f"\n✅ All 3 articles inserted, 6 topics processed.")
print(f"Article IDs:\n  1: {a1_id}\n  2: {a2_id}\n  3: {a3_id}")
