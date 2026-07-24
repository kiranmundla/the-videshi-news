#!/usr/bin/env python3
"""
Videshi Sports Writer — 2026-07-11 08:00 PDT
Two fresh sports articles for The Videshi.
"""

import json
import os
import subprocess
import re
from datetime import datetime, timezone

# ── Supabase setup ──────────────────────────────────────────────────────────
def load_env():
    env_path = os.path.expanduser("~/workspace/.env.supabase")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k] = v.strip().strip('"').strip("'")

load_env()
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]


def slugify(text, max_len=90):
    s = text.lower()
    s = re.sub(r"[''']", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    if len(s) > max_len:
        s = s[:max_len].rsplit("-", 1)[0]
    return s


def insert_article(article):
    payload = json.dumps(article, ensure_ascii=False)
    cmd = [
        "curl", "-sS", "-X", "POST",
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=representation",
        "-d", payload,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    resp = result.stdout
    try:
        data = json.loads(resp)
        if isinstance(data, list) and data:
            print(f"  ✅ Inserted: {data[0].get('slug', '?')}")
            return True
        elif isinstance(data, dict) and data.get("code"):
            print(f"  ❌ Error: {data.get('message', resp[:200])}")
            return False
        else:
            print(f"  ✅ Inserted: {article['slug']}")
            return True
    except json.JSONDecodeError:
        print(f"  ❌ Parse error: {resp[:300]}")
        return False


now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ════════════════════════════════════════════════════════════════════════════
# ARTICLE 1: India's Commonwealth Games Countdown
# ════════════════════════════════════════════════════════════════════════════

article1_headline = "Glasgow Calls. India Sends 124 Athletes to the Commonwealth Games — But Without Its Medal Machines."
article1_subheadline = "No cricket, no badminton, no wrestling, no hockey. With nine of its strongest sports axed from the programme, India heads to Glasgow with a leaner squad, bigger questions, and Neeraj Chopra's fitness on everyone's mind."

article1_body = """India's contingent for the 2026 Commonwealth Games received a grand send-off in New Delhi this week, complete with an official kit unveiling and speeches from Union Sports Minister Mansukh Mandaviya and Indian Olympic Association president P.T. Usha. The 124-member squad — a mix of able-bodied athletes and para-athletes — will head to Glasgow for the Games, which run from July 23 to August 2.

It sounds routine. It is anything but.

## A Very Different Games

The Glasgow edition of the Commonwealth Games has slashed nine sports from the programme, and the casualties read like India's medal factory manifest: **badminton, cricket, hockey, table tennis, wrestling, squash, triathlon, beach volleyball, and rugby sevens**. At the 2022 Birmingham Games, 98 of India's 210 athletes — nearly half the contingent — competed in sports that no longer exist on the Glasgow schedule.

That means no P.V. Sindhu bidding for another gold. No Indian wrestlers sweeping the podium as they did in Birmingham, where all twelve returned with medals. No Sharath Kamal adding to his thirteen Commonwealth Games table tennis medals. For a country that has historically leaned on these disciplines for its CWG medal hauls, Glasgow presents a fundamentally different challenge.

## Neeraj's Conditional Return

The biggest name in the 32-member athletics squad is Neeraj Chopra — but his inclusion comes with a caveat. The Athletics Federation of India listed the Olympic and world champion as "conditional," meaning he must meet selection fitness requirements before suiting up in Glasgow. Chopra has been nursing a back injury and recently completed a 47-day training camp at the Olympic Training Centre in Bienne, Switzerland, ending just days ago on July 10.

The timing was strategic: the camp's conclusion sits less than two weeks before the opening ceremony, giving Chopra a window to transition from rehabilitation to competition mode. He won gold at the 2018 Commonwealth Games and has dominated the Asian Games with consecutive golds in 2018 and 2022. A return to the Commonwealth podium would be his definitive signal that the body is ready for the road ahead — the Asian Games in Aichi-Nagoya in September, and ultimately, the 2028 Los Angeles Olympics.

## Weightlifting Carries India's Hopes

With traditional medal sources stripped away, India's strongest bet for hardware shifts to **weightlifting**, where Mirabai Chanu leads an 11-member squad. The Tokyo Olympic silver medallist and Birmingham CWG gold medallist will compete at 49kg, and she enters Glasgow as the clear favourite in her category. Lovepreet Singh, who won bronze in the heavyweight division in Birmingham, anchors the men's side.

India's weightlifters topped the CWG medal standings in Gold Coast 2018 (nine medals, five gold) and Birmingham 2022 (ten medals, three gold). If any discipline can cushion the blow of the nine axed sports, it is this one.

Beyond the weights, India will look to **judo** (14 athletes across men's and women's categories), **athletics** (the 32-member squad featuring M. Sreeshankar, Tejaswin Shankar, and Parul Chaudhary alongside Chopra), **swimming** (Srihari Nataraj leads five swimmers), and **track cycling** (six riders plus a para-athlete).

## Why NRIs Should Watch Closely

Glasgow is home to one of the United Kingdom's largest South Asian communities, and the Games will unfold in a city where the Indian flag needs no introduction. For NRIs across the UK, this is the rare chance to watch Indian athletes compete on what is essentially home turf.

There is also a bigger prize at stake. India's performances in Glasgow will feed directly into the country's bid to host the **2030 Commonwealth Games** — a prospect that IOA president Usha referenced at the send-off ceremony. "The 2030 Commonwealth Games are very important for us as India will host them," she said. "I am confident our athletes will put in strong performances."

And for the diaspora, that ambition carries a particular resonance. A Commonwealth Games on Indian soil would be the country's biggest multi-sport hosting since the 2010 Delhi edition — and a statement that India's sporting infrastructure has come of age.

The contingent departs for a pre-Games conditioning camp before arriving in Glasgow on July 23. The opening ceremony will be the easy part. What follows, in a Games stripped of India's safety-net sports, will be the real test."""

article1_slug = slugify("india-124-athletes-commonwealth-games-glasgow-2026-neeraj-chopra-no-cricket-badminton-nri")

article1 = {
    "headline": article1_headline,
    "subheadline": article1_subheadline,
    "body": article1_body,
    "slug": article1_slug,
    "category": "sports",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/fb/Neeraj_Chopra_Olympic_gold_medalist.jpg",
    "image_caption": "Neeraj Chopra, India's Olympic javelin champion, whose conditional inclusion headlines the Glasgow-bound squad",
    "image_attribution": "Wikimedia Commons",
    "published_at": now_iso,
    "vertical": "multi-sport",
    "diaspora_angle": "Glasgow's large South Asian community gives NRIs front-row access to Indian athletes at the CWG, while India's 2030 hosting bid makes this squad's performance a matter of national sporting ambition.",
    "sources": json.dumps([
        {"name": "RevSportz", "url": "https://revsportz.in"},
        {"name": "IANS", "url": "https://ianslive.in"},
        {"name": "IndiaSportsHub", "url": "https://indiasportshub.com"},
        {"name": "Female in Sports", "url": "https://femaleinsports.com"}
    ]),
    "score_total": 8,
}


# ════════════════════════════════════════════════════════════════════════════
# ARTICLE 2: MLC Playoff Scramble
# ════════════════════════════════════════════════════════════════════════════

article2_headline = "Three Teams. Four Points. One Playoff Spot. MLC's Brutal Bottom-Half Battle Enters Its Final Week."
article2_subheadline = "San Francisco's Unicorns have run away with the league. Below them, Seattle, Texas, and Washington are tied on four points each — and at least one will not survive."

article2_body = """With Major League Cricket's fourth season entering its final stretch, the top of the table looks settled. The San Francisco Unicorns have been the class of the tournament — five wins from nine matches, just one loss, ten points, and a four-point cushion over everyone else. Short of a collapse that would defy the arithmetic, they will finish first.

The drama is underneath.

## The Race for Second, Third, and Fourth

The MLC playoffs take the top four teams into a knockout bracket: a Qualifier (first versus second), an Eliminator (third versus fourth), and then a Challenger and Final. Finishing in the top two matters — the Qualifier offers a second chance, while the Eliminator is sudden death.

Right now, **Los Angeles Knight Riders and Mi New York are locked on six points each**, holding second and third. Behind them, **Seattle Orcas, Texas Super Kings, and Washington Freedom are all knotted at four points** — and with only one spot remaining in the top four, the math is merciless. At least one of these three, possibly two, will miss the playoffs entirely.

The Knight Riders have been the most improved side of the second half. After a slow start weighed down by five draws, they have won back-to-back matches — beating the Texas Super Kings on July 4 and the Washington Freedom on July 10 (chasing down 174 with 192). Their only loss all season came against Mi New York on July 5. LA's run rate and recent form give them the momentum.

Mi New York, meanwhile, steadied after losing two straight to the Unicorns in early July — coming back to beat Seattle on July 10. But their 3-3 win-loss record tells the story of a team that has been inconsistent when it matters.

## Pretorius Announces Himself

The individual performance of the week belonged to **Lhuan-dre Pretorius**, the South African batter who smashed a match-winning **102 not out off just 52 balls** — ten fours, five sixes — for the Unicorns against Mi New York on July 9. It was a knock that turned a tight chase (SFU won by three wickets, 146 to 143) into a statement. With Peter Siddle replacing the injured Ashwin and the bowling unit rotating around de Kock's captaincy, the Unicorns have found depth where other teams have found cracks.

## The Survival Math

Seattle's problem is results. Two wins from nine matches is the worst conversion rate in the league, and while the Orcas have drawn three (rain and weather have haunted the entire season), those non-results don't help when you need points. Dasun Shanaka's historic double hat-trick against Texas was the highlight of Seattle's season, but one magical over does not make a campaign.

Texas and Washington, both with eight matches played, have a game in hand on the rest — but both also have 2-4 win-loss records. Texas's batting has been brittle, while Washington's bowling has leaked runs at crucial moments.

The final week of the league stage will decide everything. Seattle faces the possibility of hosting a playoff at Marymoor Cricket Community Park Stadium in Redmond — or missing the knockout stage entirely. For the Knight Riders and Mi New York, the goal is simpler: stay ahead and avoid the Eliminator.

## Why NRIs Should Care

MLC remains the only major T20 league where Indian Americans can watch world-class cricket live, in their own cities, without a passport. Matches are played across **Grand Prairie (Texas), Marine Park (New York), Marymoor Park (Seattle), Great Park (California), and George Mason Stadium (Virginia)** — all within driving distance of the country's largest Indian communities.

With the IPL done, the England tour turning into a horror show, and the World Cup on a different continent, MLC is the one competition where NRI cricket fans are not just watching from afar. They are in the stands. And this final week, with everything still to play for at the bottom, might be the best argument yet for showing up."""

article2_slug = slugify("mlc-2026-playoff-race-three-teams-four-points-sf-unicorns-pretorius-century-nri-july")

article2 = {
    "headline": article2_headline,
    "subheadline": article2_subheadline,
    "body": article2_body,
    "slug": article2_slug,
    "category": "sports",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/67/QUINTON_DE_KOCK_%2815681398316%29.jpg",
    "image_caption": "Quinton de Kock, captain of the league-leading San Francisco Unicorns in MLC Season 4",
    "image_attribution": "Wikimedia Commons",
    "published_at": now_iso,
    "vertical": "cricket",
    "diaspora_angle": "MLC is the only major T20 league where Indian Americans can attend world-class cricket live in US cities — and the playoff race's final week offers the best reason yet to show up.",
    "sources": json.dumps([
        {"name": "SportsCafe", "url": "https://sportscafe.in"},
        {"name": "Cricbuzz", "url": "https://cricbuzz.com"},
        {"name": "Sporting News", "url": "https://sportingnews.com"}
    ]),
    "score_total": 8,
}


# ── Insert articles ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🏏 Videshi Sports Writer — 2026-07-11 08:00 PDT")
    print("=" * 60)

    articles = [article1, article2]
    success = 0
    for i, art in enumerate(articles, 1):
        print(f"\n📝 Article {i}: {art['headline'][:70]}...")
        print(f"   Slug: {art['slug']}")
        print(f"   Image: {art['image_url'][:80]}...")
        if insert_article(art):
            success += 1

    print(f"\n{'=' * 60}")
    print(f"✅ {success}/{len(articles)} articles inserted successfully.")
    if success < len(articles):
        print("⚠️  Some articles failed — check errors above.")
