#!/usr/bin/env python3
"""
Sports writer – 2026-07-14 15:14 PT
Two articles:
1. Spain 2-0 France World Cup semifinal result
2. India beat England in first ODI at Edgbaston
"""

import os, json, subprocess, datetime, re, uuid

def load_env():
    env_path = os.path.expanduser("~/workspace/.env.supabase")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

def slugify(text, max_len=80):
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s[:max_len].rstrip("-")

def insert_article(article):
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    payload = json.dumps(article, ensure_ascii=False)
    result = subprocess.run(
        [
            "curl", "-sS", "-w", "\n%{http_code}",
            f"{url}/rest/v1/p2_articles",
            "-X", "POST",
            "-H", f"apikey: {key}",
            "-H", f"Authorization: Bearer {key}",
            "-H", "Content-Type: application/json",
            "-H", "Prefer: return=representation",
            "-d", payload,
        ],
        capture_output=True, text=True
    )
    output = result.stdout.strip()
    lines = output.split("\n")
    http_code = lines[-1] if lines else "000"
    body = "\n".join(lines[:-1])
    if http_code.startswith("2"):
        try:
            resp = json.loads(body)
            if isinstance(resp, list) and resp:
                return resp[0].get("slug", "OK")
            return "OK"
        except Exception:
            return "OK"
    else:
        print(f"  ERROR {http_code}: {body[:500]}")
        return None


def build_articles():
    now = datetime.datetime.now(datetime.timezone.utc)

    articles = []

    # ─────────────────────────────────────────────
    # Article 1: Spain 2-0 France World Cup Semifinal
    # ─────────────────────────────────────────────

    spain_body = """Spain are through to the World Cup final for only the second time in their history — and on this evidence, they might just win it.

In a semifinal that was billed as the clash of the tournament, Luis de la Fuente's side suffocated France from the opening whistle, winning 2-0 at AT&T Stadium in Arlington, Texas, to book a date with either England or Argentina in Sunday's final at MetLife Stadium.

The European champions were ruthless where it mattered and resolute everywhere else, restricting the most lethal attack in world football to just two shots on target across 90 minutes. For the tens of thousands of Indian-origin fans across North America who have been following this tournament from watch parties in Dallas, Edison, and Fremont, this was a masterclass in what happens when tactical discipline meets raw talent.

## Yamal Draws First Blood

The breakthrough came in the 22nd minute. Marc Cucurella swung a deep cross into the French box that Lucas Digne brought down on his chest. As the veteran left-back attempted to clear, 19-year-old Lamine Yamal stepped across him and was caught by the follow-through. Referee Ivan Barton pointed to the spot without hesitation.

Mikel Oyarzabal stepped up and drilled the penalty high into the net. Mike Maignan guessed right but the strike was too clean, too precise. It was Oyarzabal's fifth goal of the tournament and the first time France had trailed at this World Cup.

The blow was compounded minutes later when centre-back William Saliba limped off with an injury, replaced by Crystal Palace's Maxence Lacroix — a forced change that weakened the spine of Didier Deschamps' defence at the worst possible moment.

## Porro Seals It

France emerged for the second half with Manu Koné replacing the booked Adrien Rabiot, but Spain's grip only tightened. On the hour mark, Pedro Porro and Dani Olmo exchanged a series of quick, intricate passes on the right side of the French box. When Olmo was fouled, the referee played advantage, and Porro — already in stride — collected the loose ball and side-footed past Maignan. 2-0. Game over in all but name.

Porro, named Man of the Match, was typically understated afterward. "It's a dream come true," he said. "From the start to the end we played a great game. This is a team effort, it's not about me."

## Mbappé Neutralised

The strangest part of this result was the near-total disappearance of Kylian Mbappé. The France captain — eight goals in the tournament coming in — was smothered by Spain's collective defensive organisation. Michael Olise was a spectator, harried into irrelevance by Cucurella. Ousmane Dembélé offered flickers and nothing more. By the time Mbappé was booked for frustration in the 83rd minute, the olés were ringing around the stadium. A frustrated France had been reduced to long balls and hope.

It was a performance that recalled Spain's Euro 2024 semifinal demolition of France in Munich — and their Nations League victory last summer. Three consecutive tournament knockouts of the same opponent is a statement bordering on psychological dominance.

## Deschamps' Farewell, Spain's Coronation Bid

For Deschamps, this was the end. The longest-serving France manager has confirmed he will step down after this tournament, and his final match will not be a final. France's attempt to reach three consecutive World Cup finals — last achieved by Brazil across 1994, 1998, and 2002 — is over.

Spain, meanwhile, head to New Jersey to await the winner of Wednesday's England-Argentina semifinal in Atlanta. La Roja's unbeaten run now extends beyond 36 matches. Their last defeat? A distant memory.

## Why NRIs Should Care

For diaspora sports fans, this World Cup has been a once-in-a-generation event. With matches played in Dallas, Houston, Miami, New York, and Atlanta — cities with massive Indian-American populations — the proximity has been unprecedented. Spain's final will be at MetLife Stadium on July 19, a short drive from the heart of the New Jersey Indian community. If you can get tickets, this is the biggest sporting event on American soil this year.

Spain's style of play — patient, technical, built on a philosophy rather than individual brilliance — has always resonated with cricket-loving audiences who appreciate the art of domination through control. On Tuesday in Arlington, they delivered the definitive version of it."""

    articles.append({
        "headline": "Spain Smother France 2-0 in Dallas. La Roja Head to Their First World Cup Final in 16 Years.",
        "subheadline": "Oyarzabal's penalty and Porro's cool finish silence Mbappé and end Deschamps' era as Spain book a date at MetLife Stadium on July 19.",
        "slug": slugify("spain-smother-france-2-0-world-cup-semifinal-dallas-porro-oyarzabal-yamal-final-nri-july-2026"),
        "body": spain_body.strip(),
        "category": "sports",
        "status": "review",
        "is_editorial": False,
        "vertical": "world-cup-2026",
        "diaspora_angle": "With the final at MetLife Stadium in the heart of NJ's Indian community, NRI fans have an unprecedented chance to witness a World Cup final on home turf.",
        "image_url": "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/wc-social/ig-brfootball-614c9e1c9b16.jpg",
        "image_caption": "Pedro Porro celebrates scoring for Spain at the 2026 FIFA World Cup",
        "image_attribution": "@brfootball / Instagram",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "Fox News Sports", "url": "https://www.foxnews.com"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com"},
            {"name": "USA Today", "url": "https://www.usatoday.com"}
        ]),
        "score_total": 8,
        "published_at": now.isoformat(),
    })

    # ─────────────────────────────────────────────
    # Article 2: India beat England in 1st ODI at Edgbaston
    # ─────────────────────────────────────────────

    india_body = """After four games of T20I humiliation, India walked into Edgbaston on Tuesday with something to prove. They walked out with a six-wicket victory and a reminder of why, when the big names show up, this team is still a force.

Chasing 259 on a pitch that had tormented England's own batters earlier in the day, captain Shubman Gill struck an imperious 80 before retiring hurt, and Axar Patel delivered one of the great all-round performances in recent ODI memory — 4-62 with the ball, 57 with the bat — as India romped home with 28 balls to spare.

For the diaspora fans who endured the 4-0 T20I whitewash over the past two weeks, it was a collective exhale. The cavalry has arrived.

## England Collapse Under Their Own Ambition

England won the toss and batted under grey Birmingham skies, but what began as a confident opening stand of 61 between Ben Duckett (43) and Jacob Bethell (14) quickly unravelled. Gurnoor Brar — the young left-arm seamer earning his place in the squad — dismissed Bethell with a diving catch from Washington Sundar, and Duckett fell three balls later, caught by Jasprit Bumrah on the boundary.

Then Bumrah happened. Harry Brook, the captain, lasted exactly one delivery of Bumrah's second spell — caught at slip by Rohit Sharma for one. Jos Buttler, playing his 200th ODI, managed just five. Sam Curran went for a duck. From 64-3, England collapsed to 80-5 in the blink of an eye.

Only Joe Root and Liam Dawson salvaged respectability, grinding out a 121-run partnership that dragged England to 258 all out. Root, dropped on seven by Shivam Dube, finished unbeaten on 76. Dawson hit a career-best 68 off 83 balls. But Axar Patel had the last word, ripping through the tail with four wickets in his final five overs — Dawson, Archer (12 off 6 balls), Rashid (1), and Tongue (0) all falling to his guile.

## Gill's Edgbaston Love Affair Continues

The chase was supposed to be complicated by the loss of Rohit Sharma (11) and Virat Kohli (5). Rohit was caught off Gurnoor Brar — irony not lost — and Kohli fell lbw to a Jofra Archer delivery that nipped back and trapped him in front. At 29-2, the ghosts of the T20 series lingered.

Gill swatted them away. The 26-year-old captain, who made 430 runs during India's Test series at this ground last year, looked utterly at home. He punched drives through the covers with the timing of a man who treats Edgbaston like his backyard, pulling and cutting anything short with contempt. His 80 came at better than a run-a-ball before he retired hurt with the target within reach — India needing 110 from 24.2 overs with seven wickets in hand.

## Patel and Sundar: The Unbreakable Partnership

What followed was a clinic in controlled aggression. Axar Patel, batting at number six, and Washington Sundar, at seven, put on an unbroken 102-run partnership that took the game away from England entirely. Patel, continuing his outstanding day, struck 57 at a strike rate above 100. Sundar, in a touch of theatre, reached his fifty with a straight six — the shot that also brought up the century stand and won the match.

India finished on 262-4 in 45.2 overs, and suddenly the 4-0 T20 whitewash feels like a different tour. Which, in many ways, it is. The T20 squad was India's second string. This — with Kohli, Rohit, Bumrah, and Gill — is the first team.

## Scoreboard

**England 258 all out (47.5 overs)**: Root 76*, Dawson 68, Duckett 43; Patel 4-62, Prasidh Krishna 2-50, Brar 2-61, Bumrah 1-31.

**India 262-4 (45.2 overs)**: Gill 80 (retired hurt), Patel 57*, Sundar 52*; Archer 1-52.

*India won by 6 wickets (28 balls remaining). India lead 1-0 in 3-match series.*

## Why NRIs Should Care

The ODI series is a direct audition for the Champions Trophy squad later this year, and it is being broadcast on Willow TV and JioStar across the US. For the thousands of Indian Americans who treated the T20 whitewash like a personal insult — and the WhatsApp groups have been merciless — this was vindication. The big guns are back, and they mean business.

The second ODI is on Thursday at Sophia Gardens in Cardiff, with the series finale at Lord's on Sunday. After Edgbaston, India look primed to wrap it up."""

    articles.append({
        "headline": "Patel's All-Round Masterclass Powers India Past England in First ODI. The Big Guns Answer the Call.",
        "subheadline": "Axar Patel takes 4-62 and scores 57 as India chase down 259 with ease at Edgbaston, erasing the 4-0 T20I whitewash in one decisive afternoon.",
        "slug": slugify("axar-patel-all-round-india-beat-england-first-odi-edgbaston-gill-80-six-wicket-nri-july-2026"),
        "body": india_body.strip(),
        "category": "sports",
        "status": "review",
        "is_editorial": False,
        "vertical": "cricket",
        "diaspora_angle": "The ODI squad is India's first team with Kohli, Rohit, and Bumrah — NRI fans who suffered through the T20 whitewash can finally breathe again, with Willow TV and JioStar streaming every ball.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Edgbaston_-_view_of_new_stand_from_the_north.jpg/1280px-Edgbaston_-_view_of_new_stand_from_the_north.jpg",
        "image_caption": "Edgbaston Cricket Ground in Birmingham, the venue for the first ODI between England and India",
        "image_attribution": "Wikimedia Commons",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "The Times", "url": "https://www.thetimes.com"},
            {"name": "CricketNMore", "url": "https://www.cricketnmore.com"}
        ]),
        "score_total": 8,
        "published_at": now.isoformat(),
    })

    return articles


def main():
    load_env()
    articles = build_articles()
    print(f"\n📝 Writing {len(articles)} sports articles...\n")

    for i, article in enumerate(articles, 1):
        print(f"[{i}] {article['headline']}")
        print(f"    slug: {article['slug']}")
        print(f"    category: {article['category']}")
        print(f"    image: {article['image_url'][:80]}...")

        result = insert_article(article)
        if result:
            print(f"    ✅ Inserted → {result}")
        else:
            print(f"    ❌ FAILED")
        print()

    print("Done.")


if __name__ == "__main__":
    main()
