#!/usr/bin/env python3
"""Sports writer — 2026-05-23 05:00 PDT run: 2 articles."""

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
        print(f"  ERROR inserting {article.get('slug','?')}: {r.status_code} {r.text[:500]}")
    r.raise_for_status()
    return r.json()

# ── ARTICLE 1: Rishabh Pant's demotion ──────────────────────────────────────
a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Rishabh Pant Was India's Most Expensive IPL Player. The Selectors Just Told Him That Counts for Nothing.",
    "subheadline": "Stripped of Test vice-captaincy, dropped from ODIs, and now the subject of a social-media conspiracy involving his own sister — Pant's fall from the inner circle has been swift and public",
    "slug": "rishabh-pant-dropped-odi-vice-captaincy-stripped-india-afghanistan-20260523",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Pant's comeback from a near-fatal car accident in 2022 made him a deeply emotional figure for NRIs worldwide; his ₹27 crore IPL price tag was celebrated as vindication; the demotion is dominating every diaspora cricket group chat",
    "tags": ["Rishabh Pant", "India Cricket", "Afghanistan Series", "Shubman Gill", "KL Rahul", "BCCI", "IPL 2026", "Test Vice-Captain", "Ajit Agarkar"],
    "urgency": "daily",
    "sources": [
        "https://www.sportsyaari.com/cricket/ajit-agarkar-explains-why-rishabh-pant-lost-his-odi-place-and-test-vice-captaincy-ahead-of-india-vs-afghanistan-series-27149/",
        "https://cricketaddictor.com/cricket-news/shubman-gill-accused-of-playing-politics-to-get-rishabh-pant-removed-as-india-test-vice-captain-454591/",
        "https://www.sportskeeda.com/cricket/former-india-cricketer-brutally-criticises-rishabh-pant-after-vice-captaincy-sack-for-ind-vs-afg-2026-test",
        "https://www.cricketworld.com/india-rest-jasprit-bumrah-for-one-off-afghanistan-test-ahead-of-busy-schedule/110641.htm",
        "https://www.sportskeeda.com/cricket/it-almost-like-keeping-someone-on-notice-aakash-chopra-on-rishabh-pant-removal-as-vice-captain"
    ],
    "word_count": 750,
    "score_total": 62,
    "body": """On December 30, 2022, Rishabh Pant's car somersaulted off a highway divider on the Delhi-Dehradun expressway and burst into flames. He crawled out through a shattered windshield with torn ligaments, a fractured knee, and burns across his body. When he returned to competitive cricket fifteen months later, the standing ovation at the Arun Jaitley Stadium lasted longer than some innings. The narrative was irresistible: the boy who cheated death was back, and Indian cricket would never take him for granted again.

On May 19, 2026, Indian cricket took him for granted again.

Chief selector Ajit Agarkar announced that Pant had been dropped from India's ODI squad for the three-match series against Afghanistan and stripped of the Test vice-captaincy. KL Rahul, the man Pant had effectively replaced in the leadership hierarchy two years ago, now replaces him. The one-off Test is in Mullanpur on June 6. The ODIs follow in Dharamsala, Lucknow, and Chennai. Pant will be in Mullanpur. He will not be in the dressing room for any of the white-ball matches.

## The numbers that ended the argument

Agarkar was direct. "Rishabh is an incredible Test player. We want him to become the best Test player that he has always been. As far as ODI cricket is concerned, at this point we have gone with two different options."

Translation: your IPL season did not help your case, and we are done waiting.

The numbers make the selector's point for him. Pant scored 251 runs in 11 IPL 2026 innings for Lucknow Super Giants at an average of 27.88 and a strike rate under 140. For context, Pant was bought by LSG at the 2024 mega-auction for ₹27 crore — the most expensive acquisition in IPL history at the time. The team finished bottom of the table with four wins from thirteen matches, the worst record in IPL 2026.

He had not played an ODI since 2024. The Afghanistan series was supposed to be his re-entry point. Instead, Ishan Kishan — who has been recalled after a strong IPL campaign with SRH — takes the second wicketkeeper slot behind Rahul. Pant was not merely overlooked. He was actively replaced by a player who had been out of India's plans for even longer.

## The vice-captaincy: a signal, not a gesture

Aakash Chopra, the former India opener turned commentator, called it what it is. "It's almost like keeping someone on notice. They are telling him that he needs to bat well and keep well to retain his place in the side."

Pant had served as Shubman Gill's vice-captain during India's Test tour of England earlier this year, where both men scored heavily in a drawn series. But it was the South Africa debacle that changed the calculus. When Gill was ruled out with a freak injury, Pant stepped up as captain — and India lost a home Test series to the Proteas for the first time in nearly two decades. The defeat has put India's World Test Championship final hopes in serious jeopardy.

The selectors' logic is straightforward: India needs a deputy who can lead in Gill's absence without the side collapsing. Rahul led India to an ODI series win against South Africa during that same tour. The contrast was impossible to ignore.

## The conspiracy theory India cannot stop discussing

If the selection decisions generated debate, what happened on social media poured accelerant on the fire.

Within hours of the squad announcement, conspiracy theories emerged alleging that Gill had actively lobbied the selectors to remove Pant from the vice-captaincy. The theories intensified when Pant's sister liked an Instagram reel that explicitly accused Gill of conspiring against the wicketkeeper. The action was small — a double-tap on a screen — but in Indian cricket's hyper-connected ecosystem, it was treated as a family endorsement of the conspiracy.

The episode echoes a similar social-media incident involving Shreyas Iyer's sister, which had generated its own cycle of headlines and hand-wringing. The BCCI has no mechanism to police the Instagram activity of players' relatives, but the effect is the same: what might have been a straightforward selection call now carries the weight of a palace intrigue narrative that will follow Gill and Pant into every press conference for months.

## What this means for the diaspora

For NRI fans, Pant occupies a unique emotional space. His accident, his recovery, and his return were followed in real time across continents. The ₹27 crore price tag was celebrated in living rooms from Edison to Southall as proof that talent and resilience are rewarded. The demotion lands differently when it happens to a player whose story transcends cricket statistics.

The counterargument is equally simple: sentiment cannot pick a cricket team. Pant averaged 27 in the IPL while his team finished last. Ishan Kishan averaged 80 in a single match-winning innings. KL Rahul has been consistently excellent all season. Selection committees exist to make uncomfortable decisions, and Agarkar made his without apology.

## The road back

Pant remains in the Test squad. He will keep wicket in Mullanpur. But the ODI door is shut for now, and no white-ball internationals are scheduled for India before the end of 2026, which means Pant's path back runs through domestic cricket and overseas leagues — formats where selectors will watch but crowds will not.

The boy who crawled out of a burning car and made a nation cry with his courage now faces a different kind of test: proving, with no one watching, that he still deserves to be watched by everyone.""",
}

# ── ARTICLE 2: India's four new faces for Afghanistan ──────────────────────
a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "Four Cricketers You Have Probably Never Heard Of Just Got Called Up to Play for India. Their Numbers Say You Should Pay Attention.",
    "subheadline": "Harsh Dubey, Gurnoor Brar, Manav Suthar, and Prince Yadav earned maiden India call-ups for the Afghanistan series — the product of a domestic cricket system that churns out international-quality talent at a rate no other nation can match",
    "slug": "india-afghanistan-series-new-faces-dubey-brar-suthar-yadav-20260523",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Indian domestic cricket is largely invisible to NRIs; these call-ups reveal the depth of the Ranji Trophy and Syed Mushtaq Ali systems that produce world-class players from small cities — a pipeline the diaspora funds through IPL viewership but rarely sees up close",
    "tags": ["Harsh Dubey", "Gurnoor Brar", "Prince Yadav", "Manav Suthar", "India Cricket", "Afghanistan Series", "BCCI", "Ranji Trophy", "Domestic Cricket"],
    "urgency": "daily",
    "sources": [
        "https://www.icccricketschedule.com/bcci-unveils-young-india-squad-for-afghanistan-series-as-several-senior-stars-miss-out/",
        "https://www.crickettimes.com/2026/05/who-is-gurnoor-brar-meet-the-domestic-pace-sensation-picked-for-indias-squad-for-afghanistan-series/",
        "https://www.sportsyaari.com/cricket/ajit-agarkar-explains-why-rishabh-pant-lost-his-odi-place-and-test-vice-captaincy-ahead-of-india-vs-afghanistan-series-27149/",
        "https://www.insidesport.in/cricket/how-could-india-line-up-against-afghanistan-in-test-no-sai-sudharsan-debut-for-gurnoor-brar-likely-433757"
    ],
    "word_count": 710,
    "score_total": 55,
    "body": """When the BCCI announced India's squads for the one-off Test and three-match ODI series against Afghanistan, the headlines went to the names that were missing — Rishabh Pant from the ODIs, Ravindra Jadeja from both formats, Jasprit Bumrah rested entirely. But the real story is in the names that appeared for the first time.

Four cricketers — Harsh Dubey, Gurnoor Brar, Manav Suthar, and Prince Yadav — received maiden India call-ups. None of them play for Mumbai or Delhi in the Ranji Trophy. None of them have massive social media followings. One of them was discovered because his school cricket coach noticed he could not stop bowling left-arm spin during lunch breaks. Together, they represent the most aggressive youth injection Indian cricket has attempted since the 2018 Nidahas Trophy squad.

## Harsh Dubey: 69 Ranji wickets and counting

The Vidarbha left-arm spinner is the headline selection. Dubey claimed 69 wickets in the 2024-25 Ranji Trophy season — a number that would be remarkable in any domestic competition anywhere in the world. His overall first-class record reads 133 wickets in 27 matches with a best of 6/36. He has been selected for both the Test and ODI squads.

What makes Dubey unusual is his adaptability. Left-arm spinners often struggle to translate red-ball methods into white-ball effectiveness, but Dubey took 34 wickets in 38 domestic T20s and 13 in 11 IPL matches, suggesting he can vary his pace and trajectory to survive in both formats.

The selectors view him as a potential long-term successor to Jadeja — not as an all-rounder, but as the primary left-arm spin option who can hold down an end in Tests and provide control in the middle overs of ODIs.

## Gurnoor Brar: six feet five inches of pace from Punjab

Brar's story begins with a List A debut against Goa in December 2022 that went almost unnoticed. Three years later, the 25-year-old is in India's Test and ODI squads, and the predicted Test XI from multiple analysts has him starting ahead of Mohammed Siraj.

At 6'5", Brar generates uncomfortable bounce from a length that most Indian pacers cannot reach. His first-class numbers — 52 wickets in 18 matches with a best of 5/14 — are strong, but his trajectory has been steeper than the statistics suggest. He was mentored by Shubman Gill at Punjab and picked up by Gujarat Titans in the IPL, where his death-bowling accuracy caught the eye of national selectors.

Brar is not a tearaway. He bowls in the mid-130s with precise seam position and the ability to nip the ball both ways. For a Test in Mullanpur — a ground with historically low, slow surfaces that reward accuracy over raw speed — he may be the perfect selection.

## Manav Suthar: the quiet left-armer with 129 first-class wickets

Suthar's selection for the Test squad is less surprising to anyone who has watched Rajasthan's Ranji Trophy matches over the past three years. The left-arm spinner has 129 first-class wickets in 29 matches with a best of 8/33 — figures that placed him in the same statistical tier as Dubey but with a slightly longer track record.

He first gained national attention during the 2022-23 Ranji season and reinforced his credentials with IPL appearances for Gujarat Titans. The selectors see him as a red-ball specialist: someone who can be trusted on turning surfaces at home and who has the patience to bowl long spells that the shortest format does not demand.

With Jadeja rested and Axar Patel absent, the Afghanistan Test could feature two debutant spinners if Dubey and Suthar both play — an experiment that tells you exactly how seriously the selectors are taking the 2027 ODI World Cup planning cycle.

## Prince Yadav: Delhi's death-bowling answer

The only one of the four selected exclusively for ODIs, Yadav earned his call-up through an outstanding Syed Mushtaq Ali Trophy campaign where he took 11 wickets for Delhi while maintaining an economy of 7.54 — exceptional numbers in T20 cricket that translate to serious death-bowling credentials.

His List A record of 29 wickets in 14 matches and 19 IPL wickets in 18 matches for LSG suggest a bowler who is comfortable under pressure. He is fast enough to be awkward, accurate enough to be trusted, and young enough to be developed.

## Why the diaspora should care

For most NRI cricket fans, Indian domestic cricket is invisible. IPL highlights stream on JioHotstar. Ranji Trophy scorecards do not. The result is a knowledge gap: the diaspora watches Kohli and Bumrah but has no idea who is coming next.

These four selections are the answer. Indian cricket's greatest competitive advantage is not its star players but its production line — a system that can lose Jadeja, Bumrah, and Axar Patel from a squad and replace them with domestic performers who have first-class records that would headline any other nation's selection meeting.

The Afghanistan series, starting June 6 in Mullanpur, is where the next generation introduces itself. It will not be glamorous. It will not trend on Instagram. But it will matter — because the depth of Indian cricket is what keeps it at the top, and the depth starts with names like Dubey, Brar, Suthar, and Yadav.""",
}

if __name__ == "__main__":
    print("Inserting Article 1: Pant demotion...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    print("Inserting Article 2: India's four new faces...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    print(f"\nDone. 2 articles published.")
    print(f"  IDs: {a1_id}, {a2_id}")
