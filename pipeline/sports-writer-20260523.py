#!/usr/bin/env python3
"""Sports writer — 2026-05-23 02:00 PDT run: 2 articles."""

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

# ── ARTICLE 1: Kohli refuses Head's handshake ──────────────────────────────
a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Virat Kohli Looked Straight Ahead and Walked Past Travis Head's Outstretched Hand. The IPL's Biggest Rivalry Just Got Personal.",
    "subheadline": "A 55-run defeat, a mocking substitution gesture, and a post-match snub — the Kohli-Head feud spilled beyond the boundary at Hyderabad",
    "slug": "virat-kohli-travis-head-handshake-refused-ipl-2026-rivalry-20260523",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "India-Australia cricket rivalry is deeply felt among NRIs; Kohli is arguably the most followed Indian sportsperson in the diaspora; the snub will dominate every NRI WhatsApp group and watch party",
    "tags": ["Virat Kohli", "Travis Head", "IPL 2026", "SRH vs RCB", "Cricket Controversy", "Handshake", "India Australia Rivalry"],
    "urgency": "breaking",
    "sources": [
        "https://www.reuters.com/sports/cricket/kohli-refuses-handshake-with-head-after-heated-verbal-spat-during-ipl-clash-2026-05-23/",
        "https://www.sportskeeda.com/cricket/virat-kohli-outrightly-snubs-travis-head-handshake-offer-srh-rcb-ipl-2026-match",
        "https://www.cricketworld.com/ipl-2026-match-67-bengaluru-end-on-top-spot-to-set-up-gujarat-clash-hyderabad-finish-third/110653.htm",
        "https://www.sportstiger.com/virat-kohli-ignores-travis-head-post-game-handshake/"
    ],
    "word_count": 720,
    "score_total": 68,
    "body": """The post-match handshake line is one of cricket's small courtesies — a vestige of the sport's insistence that what happens on the field stays on the field. On Friday night in Hyderabad, Virat Kohli decided the tradition could wait.

As Sunrisers Hyderabad and Royal Challengers Bengaluru players filed past each other after SRH's 55-run victory in the final league match, Travis Head held out his right hand toward Kohli. The former India captain looked straight ahead, walked past, and shook hands with Pat Cummins, Abhishek Sharma, and the rest of the Hyderabad squad as if Head were invisible.

The video, predictably, went viral within minutes. By the time the stadium lights dimmed at Rajiv Gandhi International, the clip had millions of views across social media, and "Kohli Head" was trending in India, Australia, the UK, and the United States.

## The fuse was lit in the fourth over

The incident did not arrive from nowhere. The friction had been building since RCB's run chase, when Kohli opened the batting against a target of 256.

During the fourth over, with Venkatesh Iyer smashing young SRH spinner Shivang Kumar for 23 runs — three sixes and a boundary — Kohli turned to Head at mid-wicket and gestured for the Australian to come and bowl. The invitation was dripping with sarcasm. "Come, bowl some off-spin," commentators interpreted, though Kohli's words were inaudible on the stump microphone.

Then came the more pointed barb. Kohli mimicked the "impact player" substitution signal — a pointed reference to the fact that Head, a specialist batter, is routinely substituted out by SRH after his batting innings so a specialist bowler can take his place. The implication was clear: Head does not bowl, Head is not a complete cricketer, Head should stay in his lane.

Head, to his credit, did eventually bowl an over later in the match. He also dismissed RCB captain Rajat Patidar. But by then, the damage — or the entertainment, depending on your perspective — was done.

## A rivalry that runs deeper than the IPL

This is not the first time Kohli and Head have clashed. The two have history that stretches back to the 2023 World Test Championship final, the 2023 ODI World Cup final at Ahmedabad, and the bruising 2024-25 Border-Gavaskar Trophy where Head's 140 in the second Test at Adelaide helped Australia take a 2-1 series lead.

For Indian fans — and particularly for the millions of NRIs who plan their weekends around IPL matches — Head has become the most effective antagonist in Indian cricket. He performs when it matters most, in finals and must-win matches, and does so with a body language that Kohli seems to find personally provocative.

The handshake refusal distills a decade of India-Australia cricket tension into a single, shareable clip. In NRI WhatsApp groups from New Jersey to Melbourne, the debate was already raging before the players had left the ground: Was Kohli justified in standing up for himself, or had he crossed a line of sportsmanship?

## What it means for the playoffs

The good news for both camps is that the result barely matters on the table. RCB, despite losing by 55 runs, finished top of the IPL 2026 standings with a superior net run rate. They had shrewdly managed their run chase — Patidar and Krunal Pandya added 84 runs to ensure RCB crossed the 178-mark needed to stay above Gujarat Titans on NRR. RCB will face GT in Qualifier 1 at Dharamsala on May 26.

SRH, powered by fifties from Abhishek Sharma (56 off 22), Ishan Kishan (79 off 46), and Heinrich Klaasen (51 off 24), finished third on 18 points. They will face the fourth-placed team — still to be decided from a tight race involving Punjab Kings, Rajasthan Royals, KKR, and Delhi Capitals — in the Eliminator at New Chandigarh on May 27.

If form holds, Kohli and Head could meet again in the knockout rounds. Given Friday's temperature, the rematch would be appointment viewing for every cricket fan on the planet.

## The bigger picture

Cricket's administrators have historically been squeamish about on-field hostility. But the sport's most compelling storylines — Waugh vs Ambrose, Tendulkar vs McGrath, Kohli vs Anderson — have always been forged in precisely this kind of heat. The IPL, which generates more than 60% of its viewership from overseas markets, understands that rivalry sells.

For the diaspora, Kohli is not merely a cricketer. He is a cultural proxy — the embodiment of a certain unapologetic Indian confidence that resonates from Silicon Valley to Southall. When he refuses a handshake, it is not just a personal slight. It is a statement, decoded in real time by millions of fans who see their own battles for respect refracted through his.

Whether that is admirable or excessive is a question that will sustain debate long after the playoffs are settled. What is certain is that the next time these two cross paths on a cricket field, no one will be looking at the scoreboard.""",
}

# ── ARTICLE 2: Federation Cup / CWG qualification ──────────────────────────
a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "India's Road to Glasgow Runs Through Ranchi. Five Key Athletes Won't Be on the Starting Blocks.",
    "subheadline": "The Federation Cup doubles as the sole Commonwealth Games selection trial, but injuries and overseas training camps have thinned the field at Birsa Munda Stadium",
    "slug": "federation-cup-2026-ranchi-commonwealth-games-glasgow-selection-trial-20260523",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "Glasgow CWG 2026 matters deeply to UK-based NRIs; Indian athletes training in the US (Gulveer Singh); CWG is the one multi-sport event where India consistently medals and diaspora communities organize watch parties",
    "tags": ["Federation Cup 2026", "Commonwealth Games", "Glasgow 2026", "Indian Athletics", "Avinash Sable", "Gulveer Singh", "Parul Chaudhary", "Birsa Munda Stadium"],
    "urgency": "daily",
    "sources": [
        "https://www.mykhel.com/more-sports/federation-cup-2026-five-major-indian-athletics-stars-missing-ranchi-meet-434427.html",
        "https://revsportz.in/93741-2/",
        "https://revsportz.in/animesh-tejaswin-sreeshankar-headline-federation-cup/"
    ],
    "word_count": 680,
    "score_total": 52,
    "body": """While the rest of Indian sport fixates on IPL playoffs and World Cup broadcast blackouts, a quieter but arguably more consequential competition opened in Ranchi on Thursday. The National Senior Athletics Federation Cup 2026, running from May 22 to 25 at Birsa Munda Stadium, is the sole selection trial for India's Commonwealth Games squad — and the absences may prove as revealing as the performances.

Glasgow 2026 kicks off on July 23. India's track and field contingent has roughly two months to be named, and this four-day meet in Jharkhand is where they must earn their seats.

## Who is running

The entry list is not short on talent. Long jumper Murali Sreeshankar, javelin thrower Annu Rani, high jumper Tejaswin Shankar, and 400m sprinter Sachin Yadav headline a deep domestic field. Shot putter Tajinderpal Singh Toor, who won gold at the 2018 Asian Games, is also competing. For athletes on the fringe of selection, these four days are everything.

Animesh Kashyap, India's newest sprint sensation, will be closely watched in the men's 100m after an impressive season that has seen him emerge as a genuine medal contender for Glasgow.

## Who is missing — and why it matters

The story of this Federation Cup, however, is the five notable absentees.

**Manikanta Hoblidhar**, India's second-fastest 100m sprinter of all time and a World University Games bronze medallist, is sidelined with a hamstring injury sustained during the National Open Relay Competition in Chandigarh. His season has been cursed: he was also disqualified in his opener at the Asian Indoor Championships in Tianjin. He is targeting the Interstate Championships for his return.

**Avinash Sable**, the 3000m steeplechase national record holder who made history at the 2022 Birmingham CWG, is still recovering from a knee injury suffered during a fall at the Monaco Diamond League last year. The injury also cost him the World Athletics Championships in Tokyo. He has returned to training and recently completed a high-altitude camp in Ooty, but Ranchi comes too soon.

**Amoj Jacob**, one of India's premier 400m runners, appears to be dealing with a fitness concern after pulling up with an apparent cramp during a recent relay. He had opened his season with a 45.99s at the Indian Open in Trivandrum — a time that makes him India's sixth-fastest this year — but the relay incident raised alarms.

**Gulveer Singh** is the absence that tells the most interesting story. India's only sub-13 5000m runner is skipping Ranchi because he is training in the United States under coach Scott Simmons, preparing specifically for Glasgow. He has already cleared the CWG qualification standard in both the 5000m and 10000m (27:24.18 at The TEN in the US). The Athletics Federation of India may grant him an exemption, but nothing is guaranteed.

**Parul Chaudhary**, who narrowly missed her own national record at the Shanghai Diamond League last week with a 9:12.84 in the women's 3000m steeplechase, has also cleared her CWG qualification mark (the standard is 9:27.41). She finished seventh in a world-class field — her best Diamond League showing — and is likely banking on that performance to secure selection without the Ranchi trial.

## The exemption question

The AFI has said exemptions may be granted to athletes who miss Ranchi, provided they have prior written approval from the federation. But the policy is discretionary, not automatic. Having a qualifying time does not guarantee a ticket to Glasgow.

This creates a peculiar tension: India's best athletes in certain events are training overseas or recovering from injuries, while the athletes actually on the track in Ranchi are fighting for spots the absent stars may ultimately claim anyway.

## Why diaspora fans should care

The Commonwealth Games remains the one major multi-sport event where India consistently delivers. From Neeraj Chopra's javelin to PV Sindhu's badminton, the CWG has been a reliable source of Indian medal joy — and Glasgow's large South Asian community virtually guarantees passionate crowds.

For NRIs in the UK, Glasgow 2026 is a home Games. Indian flags will be everywhere in the stands. The question being decided in Ranchi this weekend — under far less attention than an IPL double-header — is who exactly will carry those flags on the track.

The Federation Cup may not trend on social media. But its results will echo all the way to Glasgow.""",
}

if __name__ == "__main__":
    print("Inserting Article 1: Kohli-Head handshake...")
    res1 = insert_article(a1)
    print(f"  Inserted: {a1['slug']}")

    print("Inserting Article 2: Federation Cup / CWG...")
    res2 = insert_article(a2)
    print(f"  Inserted: {a2['slug']}")

    print(f"\nDone. 2 articles published.")
    print(f"  IDs: {a1_id}, {a2_id}")
