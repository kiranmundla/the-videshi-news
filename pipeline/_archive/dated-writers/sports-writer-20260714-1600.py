#!/usr/bin/env python3
"""Sports writer — 2026-07-14 16:00 PT run. Two articles."""

import os, json, subprocess, sys
from datetime import datetime, timezone

def load_env():
    env_file = os.path.expanduser("~/.env.supabase")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k] = v.strip().strip('"').strip("'")

def supabase_insert(article):
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    endpoint = f"{url}/rest/v1/p2_articles"
    payload = json.dumps(article)
    result = subprocess.run(
        [
            "curl", "-sS", "-X", "POST", endpoint,
            "-H", f"apikey: {key}",
            "-H", f"Authorization: Bearer {key}",
            "-H", "Content-Type: application/json",
            "-H", "Prefer: return=representation",
            "-d", payload,
        ],
        capture_output=True, text=True
    )
    return result.stdout

load_env()

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

articles = []

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 1: India's Sports Passport Proposal
# ─────────────────────────────────────────────────────────────────────
articles.append({
    "headline": "28 Diaspora Footballers, One Proposal. India's Sports Passport Idea Reaches the PM's Office.",
    "subheadline": "The AIFF has identified overseas-born players of Indian origin who could bolster the Blue Tigers — if the government agrees to let them keep their foreign passports.",
    "slug": "india-sports-passport-proposal-pmo-aiff-28-diaspora-footballers-blue-tigers-nri-july-2026",
    "category": "sports",
    "vertical": "football",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/9b/Salt_Lake_Stadium_Indian_Super_League_Opener.jpg",
    "image_caption": "Salt Lake Stadium packed for an Indian Super League opener in Kolkata",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "Could directly enable NRI athletes in the US, UK, Australia, and Canada to represent India without renouncing their citizenship — the single biggest barrier keeping diaspora talent off Indian national teams.",
    "score_total": 8,
    "sources": json.dumps([
        {"name": "Khel Now", "url": "https://khelnow.com/football/sports-passport-pio-oci-athletes-india"},
        {"name": "Inside The Games", "url": "https://www.insidethegames.biz"},
        {"name": "Reuters", "url": "https://www.reuters.com"}
    ]),
    "body": """India is not at the 2026 FIFA World Cup. Forty-eight nations are competing across North America, and the Blue Tigers are not among them. The men's team has also failed to qualify for the AFC Asian Cup for the first time in nearly a decade, marking a low point in an already underwhelming trajectory for Indian football.

But here is the uncomfortable subplot: while India sits at home, at least three players of Indian origin are playing at the World Cup — for other countries. Sarpreet Singh represented New Zealand. Samuel Moutoussamy suited up for DR Congo. And Tahsin Jamshid, who still holds an Indian passport, played for Qatar through their own sports passport system.

It is a maddening irony that has finally forced a policy response.

## A Proposal on Modi's Desk

The Ministry of Youth Affairs and Sports, led by Mansukh Mandaviya, has formally submitted a Sports Passport proposal to the Prime Minister's Office. The framework, if approved, would create a legal pathway for Persons of Indian Origin (PIO) and Overseas Citizens of India (OCI) to represent India in international sport — without surrendering their foreign citizenship.

"Sports Ministry has sent a detailed proposal to the Government of India to consider a Sports Passport framework to boost India's performance in global sports such as football, basketball and tennis," a source close to the developments told Khel Now. "It is likely to take six to eight months before the Government of India makes a decision on the subject."

The All India Football Federation (AIFF), under President Kalyan Chaubey, has been the loudest voice pushing this initiative. Chaubey has urged ISL clubs to sign PIO and OCI players, and the federation has already identified a pool of 28 footballers of Indian origin who could enter the national team pipeline if the regulatory pathway opens.

## The Ryan Williams Route — and Why It Rarely Works

Under current Indian law, dual citizenship is not permitted. Anyone who wants to represent India must renounce their foreign passport and acquire Indian citizenship — a process that is lengthy, bureaucratically draining, and demands significant personal sacrifice.

Bengaluru FC forward Ryan Williams went through exactly that. Born in Australia, Williams renounced his Australian citizenship, obtained an Indian passport, and made his debut for the Blue Tigers under coach Khalid Jamil earlier this year. He scored against Hong Kong. Before him, Japan-born Arata Izumi followed the same route in 2012.

But these cases remain extraordinarily rare. Most diaspora athletes are unwilling to give up citizenship in countries where they were raised, educated, and built careers. The renunciation requirement has functioned as an effective wall keeping overseas talent out of Indian sport.

## What a Sports Passport Would Actually Change

The proposed framework would not grant full Indian citizenship. Instead, it would create a limited sporting eligibility instrument — allowing athletes to compete for India through their heritage without losing their primary nationality.

Several countries already use similar models. Qatar is the best-known example, having used sports naturalization across football, athletics, and handball to build competitive national teams, including the squad that won the 2019 AFC Asian Cup. Bahrain has recruited East African distance runners. Turkey fast-tracks wrestlers and weightlifters. Spain has used exceptional citizenship provisions for basketball players.

The Sports Passport concept extends beyond football. The proposal covers basketball, tennis, and potentially other disciplines — making it the first cross-sport eligibility framework to reach this level of government in India.

## The 2036 Olympics Factor

The proposal's timing is not accidental. India is actively pursuing a bid to host the 2036 Olympic Games, with Ahmedabad as the primary venue city. Hosting the Olympics while fielding uncompetitive teams in most sports would be embarrassing. Tapping the diaspora — Indian-Americans in basketball, Indo-Canadians in wrestling, British-Indians in football — could meaningfully improve India's medal prospects.

India has already announced plans to host 29 international sporting events over the next two years as part of its infrastructure build-up. A sports passport would complement that hardware investment with a talent acquisition strategy.

## What NRIs Should Know

For the estimated 32 million members of the Indian diaspora worldwide, this is personal. Young athletes of Indian descent in the US, UK, Canada, and Australia have long faced an impossible choice: compete for the country that raised them, or surrender their passport to play for India. Most chose the former without a second thought.

If approved, the Sports Passport would eliminate that binary. An Indian-American basketball player at a Division I program, a British-Indian footballer in the Championship, or a Canadian-Indian wrestler on the national circuit could potentially represent India while keeping the citizenship they grew up with.

The PMO and the Ministry of Home Affairs will both weigh in on the final decision. The six-to-eight-month timeline means a resolution could come by early 2027, possibly in time to shape India's preparations for the 2028 Asian Games.

For now, the conversation has formally moved from the margins to the center of Indian sports policy. Whether it moves from paper to practice will determine whether the next World Cup — or the next Olympics — includes Indian athletes who were born abroad but never stopped being Indian."""
})

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 2: MLC Playoffs Preview
# ─────────────────────────────────────────────────────────────────────
articles.append({
    "headline": "MLC Playoffs Kick Off Wednesday. Unicorns Face Knight Riders as American Cricket's Championship Week Begins.",
    "subheadline": "Four weeks of regular season cricket are done. San Francisco, LA, New York, and Washington now battle across Texas and Virginia for the 2026 MLC title.",
    "slug": "mlc-2026-playoffs-preview-unicorns-knight-riders-freedom-mi-new-york-grand-prairie-nri-july-2026",
    "category": "sports",
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Grand_Prairie_Stadium_seating%2C_April_2024.jpg/1280px-Grand_Prairie_Stadium_seating%2C_April_2024.jpg",
    "image_caption": "Grand Prairie Stadium in Texas, host venue for MLC 2026 playoff matches",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "MLC brings world-class T20 cricket to American doorsteps — NRI fans in Texas and the DC metro area can watch playoff cricket live this week, no 3 AM alarms required.",
    "score_total": 8,
    "sources": json.dumps([
        {"name": "Sportscafe", "url": "https://sportscafe.in/cricket/points-table/leagues/t20/major-league-cricket"},
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
        {"name": "Sportradar", "url": "https://sportradar.com"}
    ]),
    "body": """The group stage is done. After 60 matches spread across venues from New York to Grand Prairie, Major League Cricket's third season has produced its final four — and the first playoff matches are on Wednesday.

Two games, two venues, one day. The San Francisco Unicorns face the Los Angeles Knight Riders at Grand Prairie Stadium in Texas at 2:30 PM PT, while Washington Freedom take on Mi New York at George Mason Stadium in Fairfax, Virginia at 6:30 PM PT.

For the Indian diaspora in America, this is the week where the experiment matters most. Can American cricket hold attention when the stakes are real?

## The Final Standings

The regular season delivered a clear hierarchy. San Francisco Unicorns dominated with 12 points from 10 matches — six wins, just one loss, and three draws. The LA Knight Riders finished second with eight points, having lost only once all season. Mi New York scraped through at third on six points, while Washington Freedom grabbed the final playoff spot with four points.

Seattle Orcas and Texas Super Kings were eliminated, both finishing on four points but behind Freedom on tiebreakers.

## Unicorns vs Knight Riders: The Marquee Clash

San Francisco are the team to beat, and it has not been particularly close. Lhuan-dre Pretorius has been the breakout star, hammering a sensational 102 off 52 balls against Mi New York on July 9 — ten fours, five sixes, a strike rate pushing 200. The South African has been the most destructive middle-order bat in the competition.

The Unicorns' depth has been their calling card. No team batted more consistently through the order, and their bowling attack held opponents below 180 more often than any other side.

The Knight Riders, though, arrive with momentum. They have won three of their last four completed matches, including a clinical chase of 172 against the Texas Super Kings on July 13. They lost only once all season — to Mi New York in early July — and their draw-heavy record (five ties or no-results) suggests a team that plays tight cricket and rarely gets blown out.

The Unicorns will be favored. But a T20 playoff at a neutral venue in the Texas heat is anybody's game.

## Freedom vs Mi New York: Stars Against Underdogs

The second match pits the tournament's most star-studded roster against its grittiest overachievers.

Mi New York's lineup reads like a fantasy draft: Kieron Pollard, Trent Boult, Quinton de Kock, Shakib Al Hasan, Nicholas Pooran. Add USA captain Monank Patel and all-rounder Romario Shepherd, and this is a squad built to win tournaments. They have the firepower. What they have lacked is consistency — three wins and three losses in the group stage, plus four draws that papered over shaky performances.

Washington Freedom are the opposite model. Built around collective effort rather than superstar power, they qualified with just two wins. But those wins came when it mattered. Andries Gous smashed 96 off 54 balls in their most recent outing against Mi New York on July 12, with Rachin Ravindra contributing a blistering 60 off 30. Lockie Ferguson and Marco Jansen give them genuine pace, and the bowling unit has been tighter than the win-loss record suggests.

Freedom's problem is simple: in a do-or-die T20, experience wins. And Mi New York have played in more pressure situations — across IPL, CPL, BBL, and international cricket — than any other MLC squad combined.

## The Indian-American Thread

MLC's pitch to the diaspora has always been about proximity. For NRIs who grew up setting alarms for IPL matches at 3 AM Eastern, the league puts world-class T20 cricket in their time zone, at venues they can drive to.

This playoff week is the proof of concept. Grand Prairie Stadium, tucked into the Dallas-Fort Worth sprawl, seats close to 7,000 and has become MLC's spiritual home. George Mason Stadium in Fairfax sits in the heart of Northern Virginia's massive Indian-American community — one of the densest concentrations of South Asian families in the United States.

Several players on the rosters have direct ties to the American desi community. Monank Patel, the USA captain playing for Mi New York, grew up in New Jersey and represents the bridge between diaspora cricket culture and professional sport. Saiteja Mukkamalla, who has appeared for the Texas Super Kings, is an Indian-American who came through the domestic US cricket pipeline.

## What Happens Next

The winners of Wednesday's two matches advance closer to the final, which is scheduled for Saturday, July 18. The season concludes that day.

For a league that is only three seasons old, the stakes feel genuinely significant. MLC has attracted IPL-level talent, broadcast deals, and growing attendance. What it still needs is a playoff run that captures the imagination — a match that families in Edison, Fremont, or Plano talk about at dinner, not just a result that flickers across a CricInfo scorecard.

Wednesday's double-header is the chance. Two matches, two time zones, four teams loaded with international talent, and a community of millions waiting to see if American cricket can deliver when it counts."""
})

# ─────────────────────────────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────────────────────────────
for i, article in enumerate(articles, 1):
    print(f"\n{'='*60}")
    print(f"ARTICLE {i}: {article['headline']}")
    print(f"{'='*60}")
    resp = supabase_insert(article)
    try:
        data = json.loads(resp)
        if isinstance(data, list) and len(data) > 0:
            print(f"✅ Inserted: slug={data[0].get('slug','?')}, id={data[0].get('id','?')}")
        elif isinstance(data, dict) and data.get("message"):
            print(f"❌ Error: {data['message']}")
            if data.get("details"):
                print(f"   Details: {data['details']}")
        else:
            print(f"Response: {resp[:500]}")
    except json.JSONDecodeError:
        print(f"Raw response: {resp[:500]}")

print("\nDone.")
