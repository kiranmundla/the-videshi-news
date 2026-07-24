#!/usr/bin/env python3
"""Sports Writer for The Videshi - July 10, 2026 08:00 AM PT"""

import os
import json
import subprocess
import urllib.parse
from datetime import datetime, timezone

# Load env
env_path = os.path.expanduser("~/workspace/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]


def insert_article(article):
    """Insert an article into Supabase p2_articles."""
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
    print(f"  Response: {result.stdout[:300]}")
    if result.returncode != 0:
        print(f"  Stderr: {result.stderr[:200]}")
    return result.stdout


now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ============================================================
# ARTICLE 1: BCCI Performance Review — India's T20I Crisis
# ============================================================

article1 = {
    "headline": "Drawing Board Time. BCCI Orders Performance Review After India's Record T20I Losing Streak.",
    "subheadline": "Five consecutive defeats — two against Ireland, three against England — have triggered the board's first formal scrutiny of Gautam Gambhir's coaching tenure. The 'reset' has become a reckoning.",
    "slug": "bcci-performance-review-gambhir-india-t20i-five-losses-england-ireland-sanju-samson-nri-2026",
    "body": """India's T20I team is in free fall, and the suits at the BCCI have noticed.

After five consecutive defeats in completed Twenty20 internationals — a run that includes a historic 2-0 whitewash by Ireland and an ongoing humiliation in England where the tourists have lost three straight, including a record 125-run drubbing at Trent Bridge — the Board of Control for Cricket in India has initiated a formal performance review covering players, coaching staff, and the broader support setup.

Head coach **Gautam Gambhir** remains contracted until 2027, but the scrutiny is real. His appointment after the T20 World Cup triumph in March was supposed to herald a smooth transition. Instead, it has produced cricket's most uncomfortable paradox: a world champion team that can't win.

## The Numbers Don't Lie

In the five T20Is since lifting the trophy, India have been bowled out for 76 at Trent Bridge — their lowest-ever T20I score — and lost the 4th T20I at Bristol by nine wickets with 37 balls to spare. England, led by the irrepressible **Harry Brook** (79 off 35 balls) and **Phil Salt** (59 off 42), have now sealed their first-ever T20 series victory over India.

The pace axis of **Jofra Archer** and **Josh Tongue** has exposed a fundamental weakness: India's batters cannot play short, hostile fast bowling in English conditions. At Trent Bridge, seven wickets fell to pace, five inside the powerplay.

## Gambhir's 'Reset' Defence

Gambhir has leaned into a single word — *reset* — to explain the carnage. "If you see the playing XI of the World Cup final and the one today, there are a lot of changes," he said after the Trent Bridge debacle. "Whether you take the captain, the opening batters... Hardik Pandya is not there, Jasprit Bumrah is not there."

He pointed to the youth injection: 15-year-old **Vaibhav Sooryavanshi** opening the batting, **Prince Yadav** in his second T20I, **Harshit Rana** returning from injury. "When you push players into such a deep sea, give them a little time and they will eventually develop."

But the reset argument cuts both ways. **Sanju Samson**, the Player of the Tournament at the 2026 World Cup who averaged over 80 at a strike rate of nearly 200, has been dropped from the last two playing XIs. Gambhir acknowledged the decision drew scrutiny but was characteristically guarded: "Everyone needs to earn their place. There is no hard and fast rule that he cannot make a comeback."

## The Iyer Question

Captain **Shreyas Iyer**, who took over the T20I captaincy in June, has been India's lone consistent performer, scoring an unbeaten 80 at Bristol. But his leadership has been questioned. "Losing by such a big margin is definitely not acceptable," he admitted. "We've got to go back to the drawing board."

The fifth and final T20I in London on Saturday is all that remains — a dead rubber for the series, but a critical audition for the BCCI's reviewers.

## Why NRIs Should Care

For the millions of Indian cricket fans across the US, UK, and Canada who stayed up late or woke early to watch their team, this losing streak stings differently. India's T20I dominance had become a point of pride — a diaspora talking point. The World Cup triumph in March was a celebration that spanned from Jackson Heights to Wembley. Five straight losses later, the post-victory glow has curdled into genuine concern about the team's direction.

The BCCI review will likely conclude after the Zimbabwe T20I series that follows, but the questions it raises — about Gambhir's man-management, the treatment of proven match-winners like Samson, and whether youth development and results can coexist at the international level — will reverberate long after the Bristol floodlights go dark.""",
    "category": "sports",
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "CricTracker", "url": "https://www.crictracker.com"},
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
        {"name": "Sportskeeda", "url": "https://www.sportskeeda.com"}
    ]),
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e8/Gautam_Gambhir_3.jpg",
    "image_caption": "India head coach Gautam Gambhir at a cricket event",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "India's record T20I losing streak has deflated NRI cricket communities that celebrated the World Cup win just months ago, raising urgent questions about the team's post-triumph direction.",
    "score_total": 8,
}

# ============================================================
# ARTICLE 2: Ashwin's MLC Dream Cut Short
# ============================================================

article2 = {
    "headline": "Two Overs and Done. Ashwin's MLC Dream Ends as Knee Betrays Him Again.",
    "subheadline": "The first Indian international to play in Major League Cricket managed just 12 balls for the San Francisco Unicorns before a recurring knee injury forced him out. Peter Siddle, 41, takes his place.",
    "slug": "ashwin-mlc-2026-knee-injury-san-francisco-unicorns-peter-siddle-replacement-etpl-dublin-nri-july-2026",
    "body": """Ravichandran Ashwin's much-anticipated Major League Cricket debut lasted exactly two overs.

The 39-year-old spinner, who made history in March by becoming the first Indian international to sign for the US-based T20 league, has been ruled out of the remainder of the 2026 MLC season after suffering a right knee injury during the San Francisco Unicorns' match against the Texas Super Kings. He bowled two wicketless overs, conceding 24 runs, before the knee that has haunted his post-international career gave way once more.

"I'm disappointed to end the season early, but unfortunately this injury means that's the right decision," Ashwin said in a statement. "I've truly loved my time with the San Francisco Unicorns and will be cheering the boys on for the rest of the tournament."

## A Recurring Nightmare

The knee is not new territory. Ashwin was set to make his Big Bash League debut with the Sydney Thunder for the 2025-26 season, but the same injury forced him out before he could play a single match. The MLC was supposed to be his redemption arc — a chance to prove that India's second-highest Test wicket-taker, with 765 scalps in 287 international matches across all formats, could still compete in franchise cricket beyond the IPL.

That narrative lasted 12 deliveries.

## Siddle Steps In at 41

Veteran Australian seamer **Peter Siddle**, 41, has been approved as Ashwin's replacement. Siddle, who made an immediate impact, is proving to be more than a stop-gap — he took 3/36 in the Unicorns' victory over Texas Super Kings, striking with his very first ball to dismiss Saiteja Mukkamalla. The Unicorns won comfortably, chasing down 153 in the 18th over behind **Lhuan-dre Pretorius's** unbeaten 69.

The franchise remains the team to beat in Season 4, sitting atop the MLC standings. But Ashwin's absence will be felt beyond the scorecard.

## What's Next for Ashwin

The recovery timeline carries implications beyond MLC. Ashwin is set to captain and mentor the **Dublin Guardians** — the Rahul Dravid-owned franchise — in the inaugural **European T20 Premier League (ETPL)**, which begins in late August. Whether his knee will be ready for that commitment remains uncertain.

Since retiring from international cricket in December 2024 and ending his IPL career last year, Ashwin has spoken passionately about experiencing franchise cricket in new markets. "The fact that there is so much interest from kids and from people who have settled in America showing so much interest towards the game — I just wanted to come and experience what it's going to look like," he said when signing with the Unicorns.

## Why NRIs Should Care

For the Bay Area's massive Indian diaspora, Ashwin's signing was personal. Here was one of their own — a Chennai boy — playing professional cricket in their backyard. The San Francisco Unicorns have built a loyal following among NRI cricket fans, and Ashwin was the headliner. His departure after a single appearance is a blow to the league's ambitions of attracting top Indian talent.

MLC CEO Johnny Grave had called Ashwin's signing "a testament to how the league's developed over the last three years." The league's growth narrative remains intact — Season 4 has been its strongest — but the poster-child moment it was banking on has evaporated. The diaspora will have to wait for the next Indian international to make the leap, and Ashwin will have to hope his knee lets him try again, somewhere, soon.""",
    "category": "sports",
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "sources": json.dumps([
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
        {"name": "Cricket Addictor", "url": "https://www.cricketaddictor.com"},
        {"name": "Reuters", "url": "https://www.reuters.com"}
    ]),
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/The_Minister_of_State_for_Youth_Affairs_and_Sports_%28Independent_Charge%29%2C_Shri_Sarbananda_Sonowal_conferring_the_Arjuna_Award_on_cricketer_Ravichandran_Ashwin%2C_in_New_Delhi_on_July_31%2C_2015_cropped.jpg/330px-thumbnail.jpg",
    "image_caption": "Ravichandran Ashwin receiving the Arjuna Award in New Delhi",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "Ashwin was the first Indian international to join MLC — the US-based cricket league NRIs actually attend. His one-match exit is a setback for the league's Indian talent pipeline and Bay Area cricket fans.",
    "score_total": 8,
}

# ============================================================
# ARTICLE 3: BBL Coming to India — Chennai Opener
# ============================================================

article3 = {
    "headline": "Cricket Diplomacy. Australia's Big Bash League to Open Its Next Season in Chennai.",
    "subheadline": "PM Modi and PM Albanese jointly announced that Melbourne Renegades will face Perth Scorchers at Chepauk on December 12 — the first time any foreign domestic cricket league plays an official match in India.",
    "slug": "big-bash-league-bbl-chennai-chepauk-opener-modi-albanese-renegades-scorchers-december-2026-nri",
    "body": """The Big Bash League is coming to India, and Chennai is the stage.

In a joint announcement at the Melbourne Cricket Ground on Thursday, Indian Prime Minister **Narendra Modi** and Australian PM **Anthony Albanese** confirmed that the opening match of the BBL's 2026-27 season will be played at the **MA Chidambaram Stadium** — Chepauk — on December 12. The **Melbourne Renegades** will take on the **Perth Scorchers** in what will be the first official match of any foreign domestic cricket league to be held on Indian soil.

It is a moment that would have been unthinkable even five years ago. The BCCI has historically guarded its domestic cricket calendar — and its players — with fortress-like protectiveness. The IPL's gravitational pull made the board reluctant to let any rival T20 league gain a foothold. Now, the gates are open.

## Why Chennai, Why Now

The choice of Chepauk is deliberate. Chennai is India's cricket heartland — the city that lives and breathes the sport in a way that even Mumbai and Kolkata struggle to match. The MA Chidambaram Stadium, with its raucous stands and spinning pitches, is where visiting teams come to be tested. It is also home to one of the most passionate cricket-watching cultures in the world.

For Cricket Australia, the calculation is transparent. India is the world's most lucrative cricket market. Private investment in BBL franchises has lagged behind the IPL's billions, and exposure to the Indian audience — even through a single match — could unlock a new tier of commercial interest. The move also strengthens bilateral sports cooperation between the two nations at a time when diplomatic ties are at a historic high.

## What It Means for the BBL

The BBL's 2025-26 season was won by the Perth Scorchers, who dominated the competition with nine wins from 12 matches. Melbourne Renegades, by contrast, finished seventh with just three wins. The match-up may look lopsided on paper, but the occasion matters more than the form book.

The Renegades have been designated the home team for the Chennai fixture — an unusual arrangement that reflects the match's exhibition-meets-competitive nature. It will count as an official BBL match, with full points on the line.

For Australian players, it will be a crash course in subcontinental conditions — spinning pitches, heat, and a crowd energy unlike anything in the Big Bash's usual summer carnival. Several BBL stars, including **Aaron Hardie**, **Matt Short**, and **Finn Allen**, already have experience in Indian conditions through the IPL.

## A Two-Way Door

The announcement opens possibilities beyond a single match. Cricket Australia has hinted that this is a pilot — a proof of concept for a longer-term arrangement that could see multiple BBL matches played in India, or even a cross-league fixture between IPL and BBL franchises. The Champions League T20, which once pitted domestic champion teams from different countries against each other, was abandoned in 2014. This could be its spiritual successor.

## Why NRIs Should Care

For the Indian diaspora in Australia — one of the country's largest migrant communities — this is validation. The BBL has been a summer staple for NRIs in Melbourne, Sydney, and Perth, where community cricket leagues already thrive. An official BBL match in Chennai bridges two cricket worlds that diaspora fans have straddled for years.

For NRIs in the US and UK, it is another sign that cricket's global footprint is expanding. Between the MLC in America, the ETPL launching in Europe, and now the BBL opening in India, the sport's franchise ecosystem is becoming genuinely international. The days of the IPL as the only game in town are numbered — and that is good for everyone who loves cricket.""",
    "category": "sports",
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "sources": json.dumps([
        {"name": "Inshorts", "url": "https://www.inshorts.com"},
        {"name": "SportsCafe", "url": "https://www.sportscafe.in"},
        {"name": "SportsTiger", "url": "https://www.sportstiger.com"}
    ]),
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/M.A.Chidambaram_Stadium_before_IND_vs_AUS_3rd_ODI_2023.jpg/1200px-M.A.Chidambaram_Stadium_before_IND_vs_AUS_3rd_ODI_2023.jpg",
    "image_caption": "MA Chidambaram Stadium (Chepauk) in Chennai before an India vs Australia ODI",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "The BBL's Chennai debut bridges two cricket worlds NRIs have straddled — the sport's expansion beyond the IPL validates the diaspora's dual cricket identity in Australia and India.",
    "score_total": 8,
}

# ============================================================
# INSERT ALL ARTICLES
# ============================================================

articles = [article1, article2, article3]

for i, article in enumerate(articles, 1):
    print(f"\n{'='*60}")
    print(f"Inserting Article {i}: {article['headline']}")
    print(f"Slug: {article['slug']}")
    print(f"{'='*60}")
    result = insert_article(article)
    if '"id"' in result:
        print(f"  ✅ Article {i} inserted successfully!")
    else:
        print(f"  ⚠ Check response for Article {i}")

print("\n✅ Done! 3 sports articles written and inserted.")
