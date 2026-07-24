#!/usr/bin/env python3
"""Sports writer for The Videshi - June 10, 2026"""

import json, subprocess, os, datetime, sys

# Load env
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            # Handle export VAR=val and VAR=val
            if line.startswith('export '):
                line = line[7:]
            key, _, val = line.partition('=')
            # Strip quotes
            val = val.strip('"').strip("'")
            os.environ[key.strip()] = val

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

def insert_article(payload):
    """Insert an article into Supabase."""
    payload_json = json.dumps(payload)
    result = subprocess.run(
        [
            "curl", "-sS", "-w", "\nHTTP_CODE:%{http_code}",
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            "-X", "POST",
            "-H", f"apikey: {SUPABASE_KEY}",
            "-H", f"Authorization: Bearer {SUPABASE_KEY}",
            "-H", "Content-Type: application/json",
            "-H", "Prefer: return=representation",
            "-d", payload_json
        ],
        capture_output=True, text=True
    )
    
    lines = result.stdout.strip().split('\n')
    http_line = [l for l in lines if l.startswith('HTTP_CODE:')]
    http_code = http_line[0].split(':')[1] if http_line else "unknown"
    response_body = '\n'.join(l for l in lines if not l.startswith('HTTP_CODE:'))
    
    try:
        data = json.loads(response_body)
        if isinstance(data, list) and len(data) > 0:
            return True, data[0].get('id'), data[0].get('slug'), http_code
        elif isinstance(data, dict) and 'message' in data:
            return False, None, data.get('message', 'unknown error'), http_code
        else:
            return False, None, response_body[:200], http_code
    except:
        return False, None, response_body[:200], http_code


# ============================================================
# ARTICLE 1: Praggnanandhaa wins Norway Chess 2026
# ============================================================

article1_body = """R Praggnanandhaa has won Norway Chess 2026. The 20-year-old from Chennai is the first Indian to claim the title since the tournament's inception in 2013, and he did it by producing one of the most remarkable comebacks the event has ever seen.

After six rounds, Praggnanandhaa was in last place. He had lost a classical game to Alireza Firouzja in the second round and was trailing the field in an event so strong that every player was rated above 2700. Wesley So led the standings. Firouzja was close behind. World Champion Gukesh Dommaraju had two classical wins. Praggnanandhaa was staring at a forgettable tournament.

Then he won four games in a row.

## The Streak That Changed Everything

In round seven, Praggnanandhaa beat Firouzja in classical chess. In round eight, he beat Magnus Carlsen — the world number one, the seven-time Norway Chess champion — in their classical encounter. In round nine, he did it again against World Champion Gukesh, completing what chess commentators called a hat trick. And in the tenth and final round, he defeated Germany's Vincent Keymer to finish with 18 points, one clear of So.

"I'm super happy with the result, and especially to do it in this manner, to win four games in a row and to come back from the last place is something that you never imagine four days back," Praggnanandhaa told ANI after his victory. "This is a special tournament win and this will top all my wins so far."

The detail that made the achievement extraordinary was the field. All six players in the open section were rated above 2700. Carlsen was at 2840. There were no easy points.

https://www.instagram.com/reel/DZQLMpsOKXu/

## Two Wins Over Carlsen

In 11 editions of Norway Chess, only five players have ever won the tournament. Carlsen has won seven of them. Praggnanandhaa became the first to defeat Carlsen twice in classical chess within a single Norway Chess campaign — a feat that would have been headline news on its own even without the title.

Chess.com's coverage noted that Carlsen lost 18 rating points during the tournament, his worst showing at the event that bears his country's name. The Norwegian acknowledged the poor result. "This is now the fourth Norway Chess tournament that I've had a really bad result," Carlsen said. "A lot of people are going to have the takeaway that I did really poorly, which is fair."

For Praggnanandhaa, the triumph built on his 2025 Tata Steel Chess victory in Wijk Aan Zee, the Netherlands. But this was different. "You have some 2600s at Wijk Aan Zee," he said. "Here it's just the top players. Winning this is more special, and adding to it, Magnus was there."

## The Gukesh Contrast

The tournament laid bare a striking contrast in Indian chess. While Praggnanandhaa surged to the title, World Champion Gukesh finished last — for the second time in recent months after a poor showing earlier in the year. Gukesh's form since winning the World Championship has been a source of concern, with commentator David Howell noting: "He's taking so much risk every game, even when he's not in form. When you're not in form, that's when to go back to basics."

Gukesh must defend his title later this year, and the question of whether the world champion's crown has become a burden — as it seemingly was for Ding Liren before him — is now firmly on the table.

## What It Means for the Diaspora

Indian chess has never had so many contenders at the top. Praggnanandhaa, Gukesh, and Arjun Erigaisi are all in the world's top 10. The NRI chess community, from Fremont to London to Singapore, has watched the rise of Indian chess over the past decade with growing pride. This win puts another marker down.

Prime Minister Narendra Modi tweeted his congratulations. Tamil Nadu Chief Minister C. Joseph Vijay went further, awarding Praggnanandhaa Rs 50 lakh (approximately $52,000) and describing the achievement as "a moment of pride for Tamil Nadu and the nation."

Praggnanandhaa is now a frontrunner for India in the 2026-27 FIDE Circuit standings, which will determine qualification for the next Candidates Tournament in 2028. Having gone from last place to champion in the span of four rounds, the Chennai prodigy has signalled that the best might still be ahead."""

article1 = {
    "headline": "He Was in Last Place After Six Rounds. Four Wins Later, He Was Champion.",
    "subheadline": "R Praggnanandhaa became the first Indian to win Norway Chess, beating Magnus Carlsen twice in a dramatic comeback that earned a call from the Prime Minister.",
    "slug": "praggnanandhaa-first-indian-norway-chess-champion-carlsen-comeback-2026-nri",
    "body": article1_body,
    "category": "sports",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/85/Praggnanandhaa_in_2025.jpg",
    "image_caption": "R Praggnanandhaa at a chess tournament in 2025",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps([
        "Chess.com - Norway Chess 2026 conclusions and round-by-round coverage",
        "The Hindu BusinessLine - Praggnanandhaa post-win interview",
        "ANI - Praggnanandhaa quotes after Norway Chess victory",
        "NewKerala - Tamil Nadu CM Vijay congratulates Praggnanandhaa"
    ]),
    "status": "review",
    "is_editorial": False,
    "published_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
}


# ============================================================
# ARTICLE 2: Animesh Kujur & Indian athletics at Saudi Grand Prix
# ============================================================

article2_body = """Five years ago, an Indian sprinter running under 21 seconds in the 200 metres was front-page news. Last week in Riyadh, Animesh Kujur won the Saudi Athletics Grand Prix with a time of 20.77 seconds and barely anyone blinked. That is how far Indian sprinting has come.

Kujur, the 22-year-old national record holder from Odisha, beat Britain's David Harrison (20.87s) and Olympic bronze medallist relay runner Toby Harries (21.01s) to take the 200m title at the Riyadh meet. It was only his second 200m race of the season — he had opened with 20.74 seconds at Indian Series-3 — and his consistency below the 21-second barrier is now a feature, not a fluke.

Last year, Kujur rewrote Indian sprint history by breaking the national record twice and bringing it down to 20.32 seconds. At the Federation Cup in April this year, he pushed it further to 20.40 seconds — a mark that stood as his season best until the Indian Grand Prix 2 in Trivandrum, where he clocked 20.55 seconds alongside a 10.31-second 100m victory. The Saudi Grand Prix was another confirmation that India's fastest man is not slowing down.

## Afsal and Krishik Add Depth

Kujur was not India's only winner in Riyadh. Mohammed Afsal, the middle-distance national record holder, secured his event title. Hurdler Krishik M continued his rapid development, adding another strong international result after recently becoming India's second-fastest 110m hurdler with a personal best of 13.44 seconds. India's men's 4x100m relay team also came first, completing a sweep across sprinting, hurdles, middle distance, and relay events.

The relay win was particularly significant. India has struggled historically to field a competitive sprint relay unit, and the improvement tracks directly with the emergence of a deeper sprint talent pool — Kujur among them.

## From Outlier to System

Indian athletics is no longer a story told through individual stars. The Saudi Grand Prix revealed something more structural: a generation of athletes trained through the Athletics Federation of India's revamped domestic circuit, tested at meets like the Indian Grand Prix series, and now delivering at the international level.

At the Indian Grand Prix 2 in Trivandrum in May, Olympian Vithya Ramraj won the 400m hurdles in 57.45 seconds — the same event where she equalled PT Usha's legendary national record of 55.42 seconds at the 2023 Asian Games. Rajesh Ramesh, part of the 4x400m relay squad that set a national record at the 2023 World Athletics Championships in Budapest, won the 400m in 45.77 seconds. Baranica Elangovan bettered her own pole vault national record with a clearance of 4.23 metres in Bhubaneswar.

These are not isolated results. They represent a generation arriving at once.

## The Asian Games Horizon

Everything is building towards the 2026 Asian Games in Japan later this year. The Saudi Grand Prix, modest in competition depth in some events, still served its purpose: race sharpness, international timing data, and exposure to pressure outside the domestic circuit.

For the Indian diaspora, the track-and-field story resonates differently from cricket. There is no IPL contract waiting at the end. These athletes train on government stipends and federation support. When Kujur runs 20.77 in Riyadh, he does it without the commercial infrastructure that cushions cricketers.

The difference now is that there are enough of them — Kujur, Afsal, Krishik, Ramraj, Ramesh, Elangovan — to suggest something systemic is working. Indian sprinting went from one-off performers to a pipeline. That pipeline just had a very good week in the desert."""

article2 = {
    "headline": "He Broke the National Record Last Year. In Riyadh, He Won Again.",
    "subheadline": "Animesh Kujur won the 200m at the Saudi Grand Prix as Indian sprinters and distance runners delivered a sweep that signals a shift in Indian athletics.",
    "slug": "animesh-kujur-200m-saudi-grand-prix-indian-athletics-sprint-revolution-nri",
    "body": article2_body,
    "category": "sports",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/51/Animesh_Kujur_%28born_2003%29_at_the_Rhine-Ruhr_2025_FISU_World_University_Games.png",
    "image_caption": "Animesh Kujur at the Rhine-Ruhr 2025 FISU World University Games",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps([
        "IndiaSportsHub - Indian athletes impress at Saudi Grand Prix 2026",
        "The State Line - Indian Grand Prix: Animesh Kujur excels in 100m, 200m",
        "Athletics Federation of India - 2026 domestic series results"
    ]),
    "status": "review",
    "is_editorial": False,
    "published_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
}


# Insert both articles
print("=" * 60)
print("INSERTING ARTICLE 1: Praggnanandhaa Norway Chess")
print("=" * 60)
ok1, id1, info1, code1 = insert_article(article1)
if ok1:
    print(f"  ✓ SUCCESS — ID: {id1}, Slug: {info1}, HTTP: {code1}")
else:
    print(f"  ✗ FAILED — {info1}, HTTP: {code1}")

print()
print("=" * 60)
print("INSERTING ARTICLE 2: Animesh Kujur Saudi Grand Prix")
print("=" * 60)
ok2, id2, info2, code2 = insert_article(article2)
if ok2:
    print(f"  ✓ SUCCESS — ID: {id2}, Slug: {info2}, HTTP: {code2}")
else:
    print(f"  ✗ FAILED — {info2}, HTTP: {code2}")

print()
print("=" * 60)
print(f"SUMMARY: {int(ok1) + int(ok2)}/2 articles inserted successfully")
print("=" * 60)
