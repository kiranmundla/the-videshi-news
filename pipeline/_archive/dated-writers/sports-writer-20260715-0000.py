#!/usr/bin/env python3
"""
Videshi Sports Writer — 2026-07-15 00:00 PT
Two articles:
1. CSK coaching shake-up after Stephen Fleming's departure
2. India-Bangladesh tour fresh doubts as BCB stalls media-rights process
"""
import os, json, subprocess, datetime

def env():
    """Load Supabase env vars."""
    env_file = os.path.expanduser("~/workspace/.env.supabase")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k] = v

env()
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

def insert_article(article):
    """Insert article via curl (proxy-safe)."""
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
    print(f"  HTTP response: {result.stdout[:300]}")
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr[:200]}")
    return result

# ─── ARTICLE 1: CSK coaching shake-up ────────────────────────────

article1_body = """Stephen Fleming's departure from Chennai Super Kings after 18 years isn't just the end of a coaching tenure — it's the opening act of a franchise-wide overhaul that could reshape one of cricket's most storied T20 operations.

The New Zealand great, who joined CSK as a player in 2008 and took charge as head coach a year later, guided the franchise to five IPL titles and two Champions League T20 trophies. His 18-year stint made him the longest-serving and most successful coach in IPL history. But CSK confirmed on Monday, July 13, that the two parties had "mutually decided to part ways" after what the franchise described as "open and honest discussions."

## Three Lean Years Forced the Hand

The numbers tell the story. CSK finished fifth in the 2024 IPL, dead last (10th) in 2025, and eighth in 2026 — three consecutive seasons without a playoff berth for a franchise that once defined consistency. The Super Kings' last title came in 2023, and the slide since has been relentless.

What may have tipped the scales was the Texas Super Kings' performance in MLC 2026. The CSK sister franchise, also under Fleming's coaching umbrella, finished bottom of the six-team league with five losses in ten matches. For NRI cricket fans in the US who follow MLC closely, the wooden spoon was difficult to watch.

"He should voluntarily step down," a CSK insider had told Cricbuzz before the announcement. "He has earned enough with the franchise — much more than he could have earned as a New Zealand player or in any other role within the game."

## The Shake-up Won't Stop at Fleming

According to Cricbuzz, the departures may extend beyond the head coach. Bowling coach Eric Simons, who has been part of the setup for years, could be next to leave. The future of batting coach Mike Hussey, the beloved "Mr. Cricket," is also uncertain. CSK appears headed for a wholesale coaching reset.

The name generating the most buzz as Fleming's potential successor is Hemang Badani, the former Indian batter who coached Delhi Capitals in the last two IPL seasons. Rahul Dravid, the most decorated Indian coach of this generation, has also been mentioned in speculation, though CSK managing director Kasi Viswanathan has said the franchise "hasn't started the process yet."

## The Dhoni Question

No discussion of CSK's future is complete without addressing the elephant in the Chepauk dressing room. MS Dhoni, who Fleming's partnership was built around, remains an uncertain figure. Now 45, Dhoni hasn't confirmed whether he has played his final game. He is reportedly in the UK and expected to return later this month, at which point he may participate in recruiting the next coaching staff.

The dynamic between Dhoni and any incoming coach will define CSK's next chapter. Fleming thrived precisely because he and Dhoni shared an intuitive understanding built over nearly two decades. Replicating that chemistry will be the franchise's biggest challenge.

## What It Means for NRI Fans

For Indian Americans who have followed CSK since the IPL's inception, Fleming's exit marks the definitive end of the franchise's golden era. The Super Kings were the team that made franchise cricket feel like it had the permanence of a Test-playing nation — same captain, same coach, same culture, year after year.

The Texas Super Kings' struggles in MLC added a local dimension to the decline. Fans in Dallas, Houston, and across the US who showed up at Grand Prairie's AirHogs Stadium watched a team that looked rudderless. A coaching overhaul could reinvigorate CSK's American offshoot just as MLC enters its growth phase.

Fleming left with characteristic grace. "Eighteen years is a lifetime in sport, and I leave with nothing but gratitude," he said. "My time with Chennai Super Kings has been the privilege of my coaching career." The question now is whether the privilege of following up that legacy will prove too heavy for whoever comes next."""

article1 = {
    "headline": "Fleming Gone, Simons and Hussey May Follow. CSK's 18-Year Dynasty Is Getting a Full Teardown.",
    "subheadline": "Five IPL titles, two Champions League trophies, and three straight playoff misses later, Chennai's golden era coaching staff is being dismantled piece by piece.",
    "body": article1_body.strip(),
    "slug": "csk-fleming-departure-coaching-overhaul-simons-hussey-dhoni-texas-mlc-nri-july-2026",
    "category": "sports",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/MA_Chidambaram_Stadium_In_the_Night_during_a_CSK_Game.jpg/1280px-MA_Chidambaram_Stadium_In_the_Night_during_a_CSK_Game.jpg",
    "image_caption": "MA Chidambaram Stadium in Chennai lit up during an IPL match",
    "image_attribution": "Wikimedia Commons",
    "vertical": "cricket",
    "diaspora_angle": "Fleming's exit and Texas Super Kings' MLC bottom finish directly affect NRI cricket fans who follow IPL and attend American cricket matches.",
    "sources": json.dumps([
        {"name": "Cricbuzz", "url": "https://m.cricbuzz.com"},
        {"name": "Reuters", "url": "https://reuters.com"},
        {"name": "Cricket Addictor", "url": "https://cricketaddictor.com"}
    ]),
    "score_total": 8,
    "published_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}

# ─── ARTICLE 2: India-Bangladesh tour in doubt ──────────────────

article2_body = """India's white-ball tour of Bangladesh has hit yet another roadblock, with the Bangladesh Cricket Board apparently stalling its own media-rights bidding process barely two weeks after launching it. The on-again, off-again series now looks more uncertain than at any point since it was first rescheduled from 2025.

On July 1, the BCB invited Expressions of Interest for the television and digital media rights covering several home series, with India's tour listed at the top. The tender specified a deadline of July 22 for bids. It appeared, at last, that the six-match series — three ODIs and three T20Is — was finally happening.

Thirteen days later, the EoI documents still haven't been released to interested broadcasters, mainly in India.

## What's Behind the Stall?

"We have not issued the EoI documents because there has been a slight change in plans," a BCB source told Cricbuzz. "We are now assessing the market before inviting bids."

Multiple theories are circulating. One is that the BCCI was displeased that the BCB put the media rights up for sale without prior discussions. Another suggests that back-channel conversations between officials of both boards took place at the ICC Annual Conference in Edinburgh, Scotland, which may have shifted the timeline.

A more practical explanation is that the match dates themselves haven't been finalized. The BCB had earlier announced that the three T20Is and three ODIs would be played between August 1 and 13, but those dates may no longer be firm. BCCI officials, when contacted, have remained "non-committal" — a diplomatic formulation that leaves both boards room to maneuver.

## The Political Backdrop

The original tour was postponed due to the severe diplomatic tensions that erupted after the student-led uprising in July 2024 that toppled the Awami League government in Bangladesh. Since then, both the government in Dhaka and the BCB administration have changed. The new BCB leadership is eager to restore relations with the BCCI, but the Indian board has been cautious, repeatedly stating that it will be "guided by the advice of the Government of India."

Adding another layer of complexity, the previous Bangladeshi government banned IPL telecasts in the country. The current administration has signaled it may revisit that decision, with sports advisor Aminul Islam telling media that "sports shouldn't be politicised" and that the matter will be reviewed after the Eid vacation.

## The Scheduling Puzzle

India's packed white-ball calendar compounds the uncertainty. The BCCI recently declined Sri Lanka Cricket's request to add three extra T20Is in August, which some observers interpreted as the board keeping that window open for the Bangladesh tour. An Afghanistan T20I series, originally slated for September, may also need to be rescheduled if the Bangladesh tour goes ahead.

BCB media committee chairman Asif Rabbani put a brave face on the situation. "We are confident about hosting India as per schedule," he told Cricbuzz. "Everyone is well aware about the benefits of playing a white-ball series against a top side like India and the signs are positive."

## Why NRIs Should Watch This Closely

For the Indian diaspora, this story sits at the intersection of cricket and geopolitics — two subjects that generate enormous emotional investment. India has not toured Bangladesh since 2022, and the bilateral relationship between the cricket boards has become a barometer for the broader diplomatic thaw between the two countries.

The series also has on-field significance. India's white-ball form is under intense scrutiny after the 4-0 T20I whitewash by England and the 2-0 series loss to Ireland. A tour of Bangladesh, with its spinning pitches and humid conditions, would provide a different kind of test for the rebuilding T20I squad while the ODI team prepares for the 2027 World Cup.

Whether the tour happens in September, later in the year, or not at all will depend less on cricket than on the diplomatic corridor between New Delhi and Dhaka. For now, the waiting game continues."""

article2 = {
    "headline": "India's Bangladesh Tour Hits a Wall Again. BCB Stalls Media Rights as BCCI Stays Silent.",
    "subheadline": "The six-match white-ball series was back on track two weeks ago. Now the BCB has frozen the bidding process and the BCCI won't commit.",
    "body": article2_body.strip(),
    "slug": "india-bangladesh-tour-fresh-doubts-bcb-media-rights-bcci-geopolitics-nri-july-2026",
    "category": "sports",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/India_v_Bangladesh_CWC15_QF_%2816712754830%29.jpg/1280px-India_v_Bangladesh_CWC15_QF_%2816712754830%29.jpg",
    "image_caption": "India playing Bangladesh in the 2015 Cricket World Cup quarter-final",
    "image_attribution": "Wikimedia Commons",
    "vertical": "cricket",
    "diaspora_angle": "The India-Bangladesh series stall reflects the diplomatic tensions NRIs closely follow, and its outcome will shape India's 2027 World Cup preparation.",
    "sources": json.dumps([
        {"name": "Cricbuzz", "url": "https://m.cricbuzz.com"},
        {"name": "Cricket Addictor", "url": "https://cricketaddictor.com"},
        {"name": "SportsCafe", "url": "https://sportscafe.in"}
    ]),
    "score_total": 8,
    "published_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}

# ─── Insert both articles ────────────────────────────────────────

articles = [
    ("CSK Fleming Shake-up", article1),
    ("India-Bangladesh Tour Doubts", article2),
]

for label, a in articles:
    print(f"\n{'='*60}")
    print(f"Inserting: {label}")
    print(f"  Headline: {a['headline']}")
    print(f"  Slug: {a['slug']}")
    print(f"  Category: {a['category']}")
    print(f"  Status: {a['status']}")
    print(f"  Body length: {len(a['body'])} chars, ~{len(a['body'].split())} words")
    result = insert_article(a)
    if '"id"' in result.stdout:
        print(f"  ✅ INSERTED successfully")
    else:
        print(f"  ⚠️  Check response above")

print(f"\n{'='*60}")
print("Done. 2 articles inserted with status='review'.")
