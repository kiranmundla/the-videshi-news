#!/usr/bin/env python3
"""
Videshi Sports Writer — July 13, 2026 (08:00 PT)
Two articles:
1. India Women's historic victory at Lord's (270-run win, first women's Test at Lord's)
2. India ODI series preview — Kohli, Rohit, Bumrah return after T20I whitewash
"""

import os, json, subprocess, sys
from datetime import datetime, timezone

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

def supabase_insert(article: dict) -> dict:
    payload = json.dumps(article)
    result = subprocess.run(
        ["curl", "-sS", "-X", "POST",
         f"{SUPABASE_URL}/rest/v1/p2_articles",
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=representation",
         "-d", payload],
        capture_output=True, text=True
    )
    return json.loads(result.stdout) if result.stdout else {"error": result.stderr}


# ── Article 1: India Women's Historic Victory at Lord's ──────────

article1_body = """It took Lord's Cricket Ground 142 years to host a women's Test match. It took India's women exactly four days to make sure nobody would forget the first one.

India demolished England by 270 runs on Monday, bowling the hosts out for 186 while chasing an improbable 457. The margin of victory was emphatic, but the numbers alone don't capture the scale of what happened at St John's Wood. Three women walked onto Lord's famous honours board — a board that has carried men's names since 1884 — and a 16-year career ended mid-match, Ben Stokes-style, with a quiet announcement and a long ovation.

## Kranti Gaud: The Name That Goes First

The 22-year-old medium-pacer from Maharashtra became the first woman in history to have her name inscribed on the Lord's Test honours board when she ripped through England's first innings with figures of 5 for 37. That haul — which reduced England from a cautious 63 for 2 to a paltry 170 all out — gave India a 115-run first-innings lead and set the tone for everything that followed.

Gaud wasn't done. In the second innings, she struck twice in the first five overs, dismissing Tamsin Beaumont and Heather Knight to leave England reeling at 34 for 4 and any hope of a miraculous chase dead on the outfield. She finished the match with seven wickets, but it's the five in that first innings — and the permanent line of calligraphy that comes with them — that will define her Lord's debut.

## Yastika Bhatia's Quiet Masterclass

If Gaud was the sword, Yastika Bhatia was the shield. The 24-year-old wicketkeeper-batter scored 113 in India's second innings, a maiden Test century compiled with the patience and shot selection of someone twice her experience. Batting alongside Smriti Mandhana's fluent second-innings contribution and Harmanpreet Kaur's rapid 40, Bhatia built India's lead past 450 before the declaration came at 341 for 7.

Her century earned her a spot on that same honours board — the second woman to be inscribed, within a day of the first. For a player who made her international debut only in 2021, it was a statement that her best years are ahead of her.

## Sophie Ecclestone Writes Her Own Record

Even in defeat, England's left-arm spinner had a match to remember. Ecclestone's five-wicket haul in India's second innings (5-118) made her England Women's all-time leading wicket-taker across formats, surpassing Katherine Sciver-Brunt's 335 with a tally that now sits at 338. She also took 3-68 in the first innings, cleaning up India's tail efficiently. On another day, her eight-wicket match haul would have been the headline.

## Knight Falls: A Career Ends at Cricket's Cathedral

The emotional centrepiece of the match came on Day 2, when Heather Knight — England's most-capped women's cricketer with 320 appearances — announced her retirement from international cricket mid-game, echoing Ben Stokes' departure from Test cricket at the same ground last month.

Knight, 35, captained England to the 2017 World Cup title at Lord's and led the side on 199 occasions. Her departure leaves a leadership vacuum that the ECB will need to address, but her timing — choosing the ground where she lifted the trophy, in the first women's Test ever played there — was characteristically deliberate.

## Why This Matters for the Diaspora

For the thousands of Indian-origin families in the UK who packed into Lord's over the four days, this was more than a cricket match. Women's cricket in the South Asian diaspora has long operated in the shadow of the men's game, with community leagues and girls' academies struggling for visibility and funding. A 270-run demolition at the most famous cricket ground on earth — led by a 22-year-old pacer and a 24-year-old centurion — is the kind of result that changes the conversation.

It matters in the US and Canada too, where MLC and community cricket have expanded the sport's footprint. The next generation of diaspora girls who pick up a bat or mark out their run-up now have a fresher, fiercer set of role models.

India's women came to Lord's and didn't just make history. They rewrote the guest book."""


article1 = {
    "headline": "270 Runs and a Place on the Honours Board. India's Women Make Lord's History.",
    "subheadline": "Kranti Gaud becomes the first woman inscribed on Lord's famous honours board, Yastika Bhatia hits a maiden Test century, and Heather Knight retires mid-match as India demolish England in the ground's first-ever women's Test.",
    "slug": "india-women-historic-270-run-victory-lords-first-womens-test-kranti-gaud-honours-board-yastika-century-knight-retires-nri-july-2026",
    "body": article1_body.strip(),
    "category": "sports",
    "vertical": "women-cricket",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Lords-Cricket-Ground-Pavilion-06-08-2017.jpg/330px-Lords-Cricket-Ground-Pavilion-06-08-2017.jpg",
    "image_caption": "The Lord's Cricket Ground Pavilion, home to cricket's most famous honours board",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "India's 270-run demolition at Lord's — led by a 22-year-old pacer and a 24-year-old centurion — changes the conversation for diaspora girls playing cricket in community leagues across the US, UK, and Canada.",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "The Times", "url": "https://www.thetimes.com"},
        {"name": "ESPN Cricinfo", "url": "https://www.espncricinfo.com"}
    ]),
    "tags": ["India Women", "England Women", "Lords", "Kranti Gaud", "Yastika Bhatia", "Heather Knight", "Sophie Ecclestone", "Test cricket", "honours board", "womens cricket"],
    "published_at": datetime.now(timezone.utc).isoformat(),
    "score_total": 9
}

# ── Article 2: India ODI Series Preview ──────────────────────────

article2_body = """The last time Virat Kohli wore India's blue in England, he scored 149 runs in three ODI innings at a strike rate of 104. The last time Jasprit Bumrah bowled with the new Kookaburra in English conditions, batters looked like they'd rather be anywhere else. And the last time Rohit Sharma walked out to open in an ODI series with something to prove, he averaged 71.

All three return on Tuesday when India play England in the first of three ODIs at Edgbaston, Birmingham (11 AM BST, 5:30 AM ET, 2:30 AM PT). For a squad that just watched its T20I unit get whitewashed 4-0 from the comfort of the team hotel, this is a very personal rescue mission.

## The T20I Wreckage

Let's not sugarcoat it. India's T20I tour of England was a disaster. A young squad captained by Shreyas Iyer — without Kohli, Rohit, or Bumrah — lost the first T20I at Durham, the second at Manchester by four wickets, the third at Nottingham by 125 runs (their heaviest T20I defeat ever), and the fourth at Bristol by nine wickets. The fifth match at Southampton completed a 4-0 whitewash after Jos Buttler's brutal 131 powered England past India's total with overs to spare.

The performance was bad enough that the BCCI ordered a performance review, and India lost their No. 1 ICC T20I ranking to England. It was India's first-ever bilateral T20I series whitewash, and a particularly bitter one given that they've won the last two T20 World Cups.

## Enter the Adults

The ODI squad reads like a very different team. Shubman Gill captains, but the power sits behind him: Rohit Sharma and Kohli slot into the top order with the comfort of players who have faced Jofra Archer before and lived. KL Rahul adds middle-order steel. And Bumrah — the one bowler in world cricket who can make a 2 AM alarm clock worth setting — leads the attack alongside Kuldeep Yadav, Prasidh Krishna, and Arshdeep Singh.

The only disruption: Harshit Rana's hamstring injury from the third T20I ruled him out, with Prince Yadav — who impressed in the T20 series — staying on as his replacement. Washington Sundar and Axar Patel provide spin depth, while Ishan Kishan keeps wicket.

## The Matchups That Matter

**Bumrah vs. Salt**: Phil Salt has been England's most explosive white-ball batter this summer. Bumrah's ability to move the new ball both ways at 90 mph is the acid test for Salt's aggressive intent.

**Kohli at Edgbaston**: Kohli averages 56 in ODIs in England and has a special relationship with Edgbaston, where he scored a famous Test century in 2018. At 37, these tours are numbered. Every innings carries weight.

**Kuldeep vs. England's middle order**: England's weakness against wrist-spin in 50-over cricket is well-documented. Kuldeep Yadav took 6 for 25 against England in 2025, and if the Edgbaston surface offers any turn, he's India's trump card.

**Gill's captaincy under pressure**: This is the 26-year-old's biggest test as ODI captain. The T20 debacle happened on someone else's watch, but the ODI series is his responsibility. A clean sweep would cement his credentials; a repeat of the T20 performance would raise uncomfortable questions.

## The Diaspora Viewing Guide

The scheduling is brutal for North American fans. The first ODI starts at 5:30 AM ET (2:30 AM PT) on Tuesday, July 14. The second ODI at Cardiff is on July 16 at the same time. The series finale at Lord's is on July 19 at 11 AM BST (6 AM ET).

If you're setting that alarm, here's the consolation: this is the India team you actually want to watch. The T20 squad was an experiment. This is the finished product — the same core that reached the 2023 World Cup final and the same bowling attack that can dismantle any lineup on its day.

## Schedule

| Match | Date | Venue | Start (ET) |
|-------|------|-------|------------|
| 1st ODI | July 14 | Edgbaston, Birmingham | 5:30 AM |
| 2nd ODI | July 16 | Sophia Gardens, Cardiff | 5:30 AM |
| 3rd ODI | July 19 | Lord's, London | 6:00 AM |

India's white-ball record in England since 2022 is W-L-W-L, a stubborn alternation that suggests nothing is predetermined. But after four consecutive T20I losses, the men in the ODI squad know exactly what's at stake. This isn't about rankings or preparation cycles. It's about proving that the 4-0 scoreline was an aberration, not a trend."""


article2 = {
    "headline": "Kohli, Rohit, Bumrah Walk In. India's ODI Squad Arrives to Rescue a Tour Gone Wrong.",
    "subheadline": "After watching India's young T20I side get whitewashed 4-0, the men who've carried Indian cricket for a decade return for three ODIs starting Tuesday at Edgbaston.",
    "slug": "india-odi-series-preview-kohli-rohit-bumrah-return-england-edgbaston-t20i-whitewash-redemption-nri-july-2026",
    "body": article2_body.strip(),
    "category": "sports",
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Virat_Kohli_in_PMO_New_Delhi.jpg/330px-Virat_Kohli_in_PMO_New_Delhi.jpg",
    "image_caption": "Virat Kohli, who returns to the ODI squad for the three-match series in England",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "NRIs frustrated by the T20I whitewash get the India team they actually want to watch — Kohli, Rohit, and Bumrah — back for three ODIs with early-morning viewing from the US.",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Sky Sports", "url": "https://www.skysports.com"},
        {"name": "ESPN Cricinfo", "url": "https://www.espncricinfo.com"},
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"}
    ]),
    "tags": ["India", "England", "ODI", "Virat Kohli", "Rohit Sharma", "Jasprit Bumrah", "Shubman Gill", "Edgbaston", "T20I whitewash", "cricket"],
    "published_at": datetime.now(timezone.utc).isoformat(),
    "score_total": 8
}

# ── Insert ───────────────────────────────────────────────────────

if __name__ == "__main__":
    for i, article in enumerate([article1, article2], 1):
        print(f"\n{'='*60}")
        print(f"INSERTING ARTICLE {i}: {article['headline']}")
        print(f"Slug: {article['slug']}")
        print(f"Image: {article['image_url']}")
        print(f"Word count: {len(article['body'].split())}")
        print(f"{'='*60}")

        result = supabase_insert(article)
        if isinstance(result, list) and len(result) > 0:
            print(f"✅ SUCCESS — ID: {result[0].get('id', 'unknown')}")
        elif isinstance(result, dict) and result.get("id"):
            print(f"✅ SUCCESS — ID: {result['id']}")
        else:
            print(f"❌ FAILED — Response: {json.dumps(result, indent=2)[:500]}")

    print("\n✅ Sports writer run complete.")
