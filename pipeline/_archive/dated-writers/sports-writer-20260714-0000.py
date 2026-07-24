#!/usr/bin/env python3
"""Sports writer — July 14, 2026 midnight run. Two articles."""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

# ── Load env ──────────────────────────────────────────────────────────────────
env_path = os.path.expanduser("~/workspace/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

def supabase_insert(article: dict) -> dict:
    """Insert a single article via Supabase REST API."""
    payload = json.dumps(article)
    cmd = [
        "curl", "-sS", "-X", "POST",
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=representation",
        "-d", payload,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return json.loads(result.stdout)

# ── Article 1: France vs Spain World Cup Semifinal ────────────────────────────

article1 = {
    "headline": "Best Attack Meets Best Defence. France and Spain Collide in Arlington for a Place in the World Cup Final.",
    "subheadline": "Mbappé's eight-goal France faces a Spain side that has conceded once all tournament — and hasn't lost in 37 straight. Something has to break.",
    "slug": "france-spain-world-cup-2026-semifinal-mbappe-yamal-dembele-dallas-nri-july-2026",
    "category": "sports",
    "vertical": "world-cup",
    "status": "review",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "image_url": "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/wc-social/ig-fifaworldcup-980dd69bbaba.jpg",
    "image_caption": "France celebrate reaching a third consecutive World Cup semifinal after beating Morocco 2-0 in the quarterfinal",
    "image_attribution": "@fifaworldcup / Instagram",
    "diaspora_angle": "Indian Americans are among the World Cup's most passionate neutral viewers; Dallas-Fort Worth's massive desi community makes this semifinal a local event as much as a global one.",
    "score_total": 8,
    "sources": json.dumps([
        {"name": "Fox Sports", "url": "https://www.foxsports.com"},
        {"name": "NBC Sports", "url": "https://www.nbcsports.com"},
        {"name": "Sky Sports", "url": "https://www.skysports.com"},
        {"name": "USA Today", "url": "https://www.usatoday.com"}
    ]),
    "body": """The first semifinal of the 2026 FIFA World Cup kicks off on Tuesday at AT&T Stadium in Arlington, Texas, and it is, by any metric, the match of the tournament. France — the competition's most prolific attacking side with 16 goals in six matches — face a Spain team that has conceded exactly once in the entire tournament. Something, by definition, has to give.

## The Numbers That Define This Matchup

France arrive in Dallas riding a wave of goals and momentum that has been building since the group stage. Kylian Mbappé has scored eight times, putting him within touching distance of the all-time single-tournament record. But the more revealing story of France's campaign is Ousmane Dembélé, the reigning Ballon d'Or winner who entered this World Cup with zero goals in major international tournaments. He now has five, along with two assists. Les Bleus have not trailed in a single match.

Spain, meanwhile, have been the tournament's defensive fortress. La Roja conceded their first goal only in the quarterfinal against Belgium — and still won 2-1, with Mikel Merino scoring a late winner that extended Spain's unbeaten run to 37 matches. One more win ties Italy's all-time international record. Where France overwhelm with firepower, Spain suffocate with possession, pressing, and the kind of tactical discipline that Didier Deschamps will have studied obsessively.

## Yamal vs. Mbappé: The Marquee Duel

At 18, Lamine Yamal is already one of the most decorated teenagers in football history. His role in Spain's Euro 2024 triumph and last year's Nations League semifinal — where he scored twice in a wild 5-4 win over France — has made him the player every neutral wants to see in a big moment. Mbappé, at 27, is in his prime and chasing the one trophy that has eluded him since 2018: a second World Cup winner's medal.

Their last three meetings tell the story. In the Euro 2024 semifinal, Spain edged France 2-1 in Munich. In the 2025 Nations League semifinal, Spain led 5-1 before France mounted a furious comeback that fell agonisingly short at 5-4. Before that, France won the 2021 Nations League final 2-1 with a Mbappé winner. Nothing separates these sides — and that is what makes Tuesday's match special.

## Why France Are Favourites — Barely

Bookmakers give France a slight edge at roughly 39% to win the whole tournament, against Spain's 21%. The main reason is Dembélé's form. Prior to this World Cup, there was a genuine question about whether he could perform on the international stage when it mattered most. That question has been buried. France's 2-0 dismantling of Morocco in the quarterfinal was their most complete performance of the tournament — controlled, clinical, and ruthless on the counter.

But Spain should not be underestimated. They have a tournament-best defence, Rodri anchoring the midfield, Pedri orchestrating possession, and a squad depth that allowed Luis de la Fuente to rotate freely without dropping a result. Their 37-match unbeaten streak isn't a statistical curiosity; it reflects a team that simply does not make mistakes.

"I'm sure France are just as concerned about us as we are about them," de la Fuente said in his pre-match press conference. He is probably right.

## The Bigger Picture

The winner of this semifinal faces either England or Argentina in Sunday's final at MetLife Stadium in New Jersey. That match takes place on Wednesday in Atlanta — but first, Arlington.

## How NRIs Can Watch

The match kicks off at 3:00 p.m. ET / 12:00 p.m. PT on Tuesday, July 14. It is live on FOX, with Spanish-language coverage on Telemundo and streaming options on Peacock and Fubo. FIFA+ will also carry select free streams.

For the Indian diaspora across the United States, this World Cup has been a shared experience in a way few sporting events manage. Dallas-Fort Worth alone is home to one of the largest Indian-American populations in the country, and watch parties at desi restaurants and community centres have become a fixture of the tournament's social calendar. Whoever emerges from Arlington on Tuesday will carry the hopes — or the heartbreak — of millions of neutrals who simply want to see the best football the sport can produce.""",
}


# ── Article 2: India vs England 1st ODI at Edgbaston ──────────────────────────

article2 = {
    "headline": "Kohli, Bumrah, and 50 Overs to Salvage a Tour. India's ODI Campaign Opens at Edgbaston.",
    "subheadline": "After a 4-0 T20 whitewash and six consecutive defeats, India's biggest names return for the first ODI in Birmingham — a ground where they have written comebacks before.",
    "slug": "india-england-first-odi-edgbaston-kohli-bumrah-rohit-gill-redemption-nri-july-2026",
    "category": "sports",
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/0f/Edgbaston_-_view_of_new_stand_from_the_north.jpg",
    "image_caption": "Edgbaston Cricket Ground in Birmingham, venue for the first ODI between England and India",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "The UK's two-million-strong Indian diaspora turns Edgbaston into a virtual home ground for India — and after six straight T20 defeats, the community is desperate for a statement win.",
    "score_total": 8,
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
        {"name": "ESPN Cricinfo", "url": "https://www.espncricinfo.com"},
        {"name": "SportsCafe", "url": "https://www.sportscafe.in"}
    ]),
    "body": """India's white-ball tour of England has been, by any measure, a disaster. Six consecutive T20 International defeats — two against Ireland, four against England — have left the reigning T20 World Champions looking like a team in crisis. The batting has been brittle, the body language poor, and the captaincy under Shreyas Iyer scrutinised at every turn.

Now comes the reset. The three-match ODI series begins on Tuesday at Edgbaston in Birmingham, and it brings with it a different format, a different captain, and — crucially — a different set of players. Virat Kohli, Rohit Sharma, and Jasprit Bumrah walk back into a squad that suddenly looks like India's strongest available XI. Shubman Gill takes the captaincy.

## A Different Team, A Different Format

The T20 squad that was whitewashed was experimental by design — Kohli and Rohit were rested, Bumrah held back for the ODIs. The logic was sound: give younger players a chance in the shorter format while preserving the big three for the 50-over matches that carry ICC Championship points and serve as preparation for the 2027 World Cup.

The execution, though, was painful. India's batting collapsed repeatedly. Dinesh Karthik, commentating for Cricbuzz, said the middle order "looks wobbly, not confident" and asked where the fear factor that opponents used to feel had gone. Sunil Gavaskar was blunter: "The batting has to come to the party."

The ODI squad answers that call with experience. Kohli averages over 48 in ODIs in England with four centuries. Rohit Sharma, in his last 20 ODI innings in England, has three scores above 80. And Bumrah, at his best, remains the most difficult bowler in world cricket to face in the first ten overs.

## Why Edgbaston Matters

This is not a neutral venue for India. Edgbaston has been the site of some of their most memorable English comebacks. In 2022, Rishabh Pant's extraordinary 146 powered India to a record fourth-innings chase of 378, turning a Test series on its head. The Birmingham crowd — significantly bolstered by the city's large Indian-origin population — made it feel like a home match.

That atmosphere will return on Tuesday. The UK is home to over two million people of Indian heritage, and cricket remains the most direct sporting connection between the diaspora and the motherland. After six straight defeats, the community wants a statement — and ODIs at Edgbaston, historically, have delivered.

## The Key Battles

**Bumrah vs. Brook.** Harry Brook has been England's most dangerous white-ball batter this summer. In three T20 innings, he averaged 67 at a strike rate of 216. Bumrah, who did not play the T20 series, is the one bowler in the world who can neutralise Brook's aggression with pace, accuracy, and the ability to swing the new ball both ways. Their contest in the first powerplay could set the tone for the series.

**Kohli vs. Archer.** Jofra Archer is England's strike weapon, generating pace and bounce that troubled India's batters throughout the T20s. But Kohli's record against high-pace bowling in ODIs is a different story entirely — he thrives on the extra time that 50-over cricket provides and has historically scored heavily against England's pace attack in bilateral series.

**Kuldeep vs. England's Middle Order.** Left-arm wrist spin in English conditions is a combination that can be devastatingly effective, as Kuldeep Yadav has proven before. England's middle order, buoyed by T20 confidence, will face a different challenge reading Kuldeep over 10 overs rather than four.

## Squad and Conditions

India's final squad reads: Shubman Gill (captain), Rohit Sharma, Virat Kohli, Shreyas Iyer, KL Rahul, Ishan Kishan (wk), Washington Sundar, Axar Patel, Shivam Dube, Kuldeep Yadav, Jasprit Bumrah, Prasidh Krishna, Arshdeep Singh, Gurnoor Brar, and Prince Yadav — the last a late replacement for the hamstring-injured Harshit Rana.

Birmingham in mid-July should offer decent batting conditions with a hint of lateral movement for the seamers early on. Edgbaston's boundaries are not the largest, which suits India's power-hitting depth. The pitch has traditionally offered something for both batters and bowlers, making the toss less decisive than at some English grounds.

## How to Watch from the US

The 1st ODI starts at 6:00 a.m. ET / 3:00 a.m. PT on Tuesday, July 14 — early morning viewing for NRIs on the East Coast, pre-dawn for the West. Coverage is on Willow TV in the US.

The series continues with the 2nd ODI at Cardiff's Sophia Gardens on July 16 (a day-night affair starting at 1:00 p.m. BST) and concludes at Lord's on July 19 — a fitting venue for the final word on a tour that India needs to rescue.""",
}


# ── Insert Articles ───────────────────────────────────────────────────────────

articles = [article1, article2]
results = []

for i, art in enumerate(articles, 1):
    print(f"\n{'='*60}")
    print(f"Article {i}: {art['headline'][:70]}...")
    print(f"  Slug:     {art['slug']}")
    print(f"  Category: {art['category']}")
    print(f"  Vertical: {art['vertical']}")
    print(f"  Status:   {art['status']}")
    print(f"  Image:    {art['image_url'][:80]}...")
    print(f"  Body len: {len(art['body'].split())} words")
    print(f"  Inserting...")

    try:
        resp = supabase_insert(art)
        if isinstance(resp, list) and len(resp) > 0:
            print(f"  ✅ Inserted! ID: {resp[0].get('id', 'N/A')}")
            results.append({"slug": art["slug"], "status": "inserted", "id": resp[0].get("id")})
        elif isinstance(resp, dict) and resp.get("code"):
            print(f"  ❌ Error: {resp.get('message', resp)}")
            results.append({"slug": art["slug"], "status": "error", "error": resp.get("message")})
        else:
            print(f"  ⚠️ Unexpected response: {json.dumps(resp)[:200]}")
            results.append({"slug": art["slug"], "status": "unknown", "resp": str(resp)[:200]})
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        results.append({"slug": art["slug"], "status": "exception", "error": str(e)})

print(f"\n{'='*60}")
print("SUMMARY")
for r in results:
    status_icon = "✅" if r["status"] == "inserted" else "❌"
    print(f"  {status_icon} {r['slug']}: {r['status']}")
