#!/usr/bin/env python3
"""Sports writer - June 4 2026 evening run (fixed)"""

import json, os, subprocess, datetime

# Load env
env_lines = open(os.path.expanduser("~/workspace/.env.supabase")).readlines()
for line in env_lines:
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        key, val = line.split("=", 1)
        os.environ[key.strip()] = val.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S+00:00")

articles = []

# ============================================================
# ARTICLE 1: Indian-Origin Players at FIFA World Cup 2026
# ============================================================
article1_body = """India will not be at the 2026 FIFA World Cup. That much has been true for 76 years, ever since the team withdrew from the 1950 tournament in Brazil and never found its way back. But when the tournament kicks off on June 11 across the United States, Canada, and Mexico, four men with roots in India will be on the pitch — representing four different nations, carrying four different passports, connected by a heritage that stretches from Punjab to Kerala to Tamil Nadu.

It is the largest representation of Indian-origin players at a single World Cup in history. And it arrives twenty years after Vikash Dhorasoo, whose ancestors migrated from Vizianagaram in Andhra Pradesh to Mauritius and then France, became the first and, until now, the only player of Indian descent to appear at the tournament.

## Sarpreet Singh — New Zealand

The most recognizable name on the list belongs to a 27-year-old midfielder from Auckland whose parents emigrated from Jalandhar in Punjab. Sarpreet Singh made history in 2019 when he signed with Bayern Munich, becoming the first player of Indian heritage to represent the German giants. He wore the number 10 shirt. He trained alongside Robert Lewandowski and Thomas Müller.

Singh's career since Munich has been itinerant — loan spells at Nürnberg and Regensburg, a return to Wellington Phoenix in the A-League — but his standing in New Zealand football has never been in doubt. He played in two FIFA U-20 World Cups, scored against Kenya and assisted a goal against India in the 2018 Intercontinental Cup in Mumbai, and was a central figure in New Zealand's qualifying campaign for 2026. It is the All Whites' first World Cup appearance since 2010.

New Zealand have been drawn into a group with Iran and Egypt. Their opening match is on June 16 at SoFi Stadium in Los Angeles — a city with one of the largest Punjabi diaspora communities in the United States.

## Tahsin Mohammed — Qatar

The youngest of the four is a 19-year-old who was born in Doha to parents from Kannur in northern Kerala. Tahsin Mohammed Jamshid grew up in Qatar's Aspire Academy, the same institution that produced much of the team that won the 2019 Asian Cup. His father, Jamshid, played football at Calicut University. His mother, Shaima, comes from Valapattanam.

At 17, Tahsin became the first player of Indian origin to appear in the Qatar Stars League. He rose through Qatar's youth teams at every level before earning a place in Julen Lopetegui's 26-man senior squad for the World Cup. Qatar are in Group B alongside Switzerland, Canada, and Bosnia and Herzegovina.

For the Malayali diaspora — one of the largest Indian communities in the Gulf — Tahsin's selection carries enormous symbolic weight. Kerala is India's most football-obsessed state, the place where club loyalties to Barcelona and Real Madrid run deeper than anywhere else in Asia. That a Keralite family's son will represent a nation at the World Cup, even if not India, is a source of fierce, complicated pride.

## Nishan Velupillay — Australia

The 25-year-old Melbourne Victory winger traces his roots to Tamil and Anglo-Indian heritage. Velupillay is one of 17 players in Australia's 26-member squad making their World Cup debut, part of a generational turnover that coach Graham Arnold has engineered since the 2022 tournament in Qatar.

Velupillay's path to the Socceroos was built through the A-League system, a reminder that the Australian domestic league has become one of the most reliable pathways in the Asian Football Confederation for young talent. Australia are in Group D alongside the United States and Paraguay. For Indian-Australian families in Melbourne and Sydney — communities that have grown rapidly in the past decade — his presence in the squad is a first.

## Samuel Moutoussamy — DR Congo

The fourth player's connection to India runs through a more circuitous route. Samuel Moutoussamy was born in France to a Congolese mother and an Indo-Guadeloupean father of Tamil origin. The Indo-Guadeloupeans are descendants of workers who migrated from South India, predominantly Tamil Nadu, to the French Caribbean islands in the late 19th century — part of the same indentured labour system that carried Indians to Mauritius, Fiji, Trinidad, and South Africa.

Moutoussamy, 29, is a defensive midfielder who spent several seasons at FC Nantes, where he made over 140 appearances and won the Coupe de France in 2022. He currently plays for Atromitos in the Greek Super League. Since his debut for DR Congo in 2019, he has earned over 57 international caps. Congo open their World Cup campaign against Portugal.

## What It Means for Indian Football

The presence of four Indian-origin players at the World Cup is a milestone, but it is also a mirror. Each of these men developed in a football ecosystem that India does not yet have — professional academies, competitive youth leagues, club structures that can identify and nurture talent from age six.

Singh had the Wellington Phoenix academy and the New Zealand Football development pathway. Tahsin had Aspire, one of the most lavishly funded sports academies on earth. Velupillay came through the A-League's youth system. Moutoussamy was shaped by the French football pyramid, arguably the most productive talent factory in world football.

India, for all its billion-plus population and its passion for the sport — viewership numbers for the Premier League and La Liga in the country are among the highest globally — still struggles with the basics. The I-League and Indian Super League have produced international-calibre players, but the pathway from grassroots to global remains fractured.

The 2026 World Cup will be watched by hundreds of millions of Indians. Some of them will be cheering for the four men who carry their heritage onto the biggest stage in sport. The hope, as always, is that one day they will be cheering for India itself."""

articles.append({
    "headline": "They Were Born in Auckland, Doha, Melbourne, and Paris. All Four Trace Their Roots to India. All Four Are Going to the World Cup.",
    "subheadline": "Sarpreet Singh, Tahsin Mohammed, Nishan Velupillay, and Samuel Moutoussamy will represent four different nations at the 2026 FIFA World Cup — the largest group of Indian-origin players at a single tournament in history.",
    "slug": "indian-origin-players-fifa-world-cup-2026-sarpreet-tahsin-velupillay-moutoussamy-nri",
    "body": article1_body,
    "category": "sports",
    "vertical": "sports",
    "diaspora_angle": "Four players of Indian origin — from Punjab, Kerala, Tamil Nadu, and Indo-Guadeloupean Tamil roots — represent New Zealand, Qatar, Australia, and DR Congo at the 2026 FIFA World Cup, the largest Indian-heritage presence at the tournament since Vikash Dhorasoo in 2006.",
    "tags": ["sports", "fifa", "world-cup-2026", "football", "nri", "diaspora", "sarpreet-singh", "tahsin-mohammed"],
    "urgency": "high",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/b/bd/Sarpreet_Singh_Training_2019-07-28_FC_Bayern_Munich.png",
    "image_caption": "Sarpreet Singh during training with FC Bayern Munich in 2019",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps([
        {"name": "MensXP", "url": "https://www.mensxp.com"},
        {"name": "RevSportz", "url": "https://revsportz.in"},
        {"name": "Inshorts", "url": "https://inshorts.com"},
        {"name": "AInvest", "url": "https://ainvest.com"},
        {"name": "Kolkata Today", "url": "https://kolkatatoday.com"}
    ]),
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "score_total": 85,
})

# ============================================================
# ARTICLE 2: Norway Chess - Praggnanandhaa
# ============================================================
article2_body = """In the eighth round of Norway Chess 2026, R Praggnanandhaa sat down across from Magnus Carlsen for the second time in the tournament. He had the black pieces. The five-time world champion had the white pieces and every reason to impose himself — he was fifth in the standings, his tournament had been mediocre by his standards, and he needed a win.

Praggnanandhaa beat him anyway.

It was the second time in the same tournament that the 20-year-old from Chennai defeated the highest-rated player in chess history in a classical game. He had already beaten Carlsen with white in an earlier round. Now he had done it with black. Only one other Indian — Viswanathan Anand — has ever recorded two classical victories over Carlsen in the same calendar year. Praggnanandhaa has done it in the same event.

## The Standings

With the tournament entering its final stretch, the race for the title has narrowed to two players. Wesley So of the United States leads with 15.5 points. Praggnanandhaa is half a point behind at 15. France's Alireza Firouzja sits third on 14.5. Germany's Vincent Keymer is fourth on 11, Carlsen is fifth on 10, and world champion Gukesh Dommaraju is last on 8.

The tournament concludes on June 5. Praggnanandhaa faces Keymer in his remaining game. So faces Firouzja. The arithmetic is clear: if Praggnanandhaa wins and So stumbles, the Indian grandmaster takes the title.

Norway Chess is one of the strongest round-robin tournaments on the calendar. It features a unique format — if a classical game ends in a draw, the players contest an Armageddon tiebreaker, with the classical draw winner receiving 1.5 points and the loser 1 point. A classical win is worth 3 points. This format rewards decisive play, and Praggnanandhaa has been the most decisive player in the field.

## The Carlsen Factor

Beating Carlsen once in a classical game is an achievement that most grandmasters never experience in their careers. Beating him twice in ten days is something else entirely.

Carlsen's dominance of chess is so complete that even now, two years after he relinquished the world championship title, he remains the world's top-rated player at 2840. His games draw the largest audiences. His opinions shape the sport's governance. His presence at a tournament elevates every other player's scalp.

Praggnanandhaa first announced himself to the world in 2022, when he beat Carlsen in an online rapid tournament. The reaction — from Carlsen himself, who immediately resigned his camera on and walked away — became one of chess's most viral moments. Since then, the two have developed a rivalry that is less about bitterness and more about generational transfer. Carlsen, 35, is not declining but he is no longer the force of nature he was at 28. Praggnanandhaa, 20, is not yet at his peak but his trajectory suggests he is headed somewhere remarkable.

## Gukesh's Difficult Tournament

At the other end of the table, the man who holds the title Carlsen gave up is having a tournament to forget. Gukesh Dommaraju, who became the youngest-ever world champion in December 2024, has won just 8 points from his eight games in Norway. He suffered a classical defeat against Firouzja in Round 8, his third classical loss of the tournament.

The 19-year-old world champion has struggled to maintain consistency since winning the title. He has a title defence against Uzbekistan's Javokhir Sindarov scheduled for later this year, and his form in Norway will have done little to boost confidence ahead of that match.

But Gukesh's struggles should be viewed in context. Norway Chess features the strongest field he has faced since the world championship. Adjustment periods are normal for young champions — Carlsen himself had uneven results in the year after he won the title in 2013. Gukesh is 19. His career is measured in decades, not tournaments.

## What It Means for Indian Chess

India has three players in this tournament — Praggnanandhaa in the open section, and Divya Deshmukh and Koneru Humpy in the women's section. In the women's event, Kazakhstan's Bibisara Assaubayeva leads with 16.5 points, with China's Zhu Jiner second on 13. Deshmukh is fifth on 10 points and Humpy sixth on 9, both having shown flashes of brilliance against significantly higher-rated opposition.

The broader picture is unmistakable. Indian chess is in a golden era that Anand began and that players like Praggnanandhaa, Gukesh, Arjun Erigaisi, and Divya Deshmukh are extending. India won the Chess Olympiad in 2022. It has the reigning world champion. It has a player — Praggnanandhaa — who has now beaten the world's best player twice in a single super-tournament. And it has a pipeline of young talent that no other country except China can match.

For NRI chess fans who grew up watching Anand's battles with Kasparov and Kramnik, Praggnanandhaa's Norway Chess campaign is a reminder that the next generation has not just arrived — it is winning."""

articles.append({
    "headline": "He Beat Carlsen With White. Then He Beat Carlsen With Black. Praggnanandhaa Is Half a Point Behind the Leader With One Round to Go.",
    "subheadline": "Only Viswanathan Anand had done it before. The 20-year-old from Chennai now has two classical wins over the world's number one in the same tournament at Norway Chess 2026.",
    "slug": "praggnanandhaa-beats-carlsen-twice-norway-chess-2026-so-leads-title-race-nri",
    "body": article2_body,
    "category": "sports",
    "vertical": "sports",
    "diaspora_angle": "Indian chess is in a golden era — Praggnanandhaa becomes only the second Indian after Anand to beat Carlsen twice in one event, while the world champion Gukesh and women's players Divya Deshmukh and Koneru Humpy also compete at Norway Chess.",
    "tags": ["sports", "chess", "norway-chess", "praggnanandhaa", "carlsen", "gukesh", "nri", "india"],
    "urgency": "high",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/85/Praggnanandhaa_in_2025.jpg",
    "image_caption": "R Praggnanandhaa, the 20-year-old Indian grandmaster competing at Norway Chess 2026",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps([
        {"name": "Bizzbuzz", "url": "https://bizzbuzz.news"},
        {"name": "NewspointApp", "url": "https://newspointapp.com"},
        {"name": "The Brighter World", "url": "https://thebrighterworld.com"},
        {"name": "IndiaSportsHub", "url": "https://indiasportshub.com"},
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Norway_Chess_2026"}
    ]),
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "score_total": 88,
})

# ============================================================
# INSERT INTO SUPABASE
# ============================================================
for i, article in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Inserting article {i+1}: {article['headline'][:80]}...")
    
    payload = json.dumps(article)
    
    result = subprocess.run(
        [
            "curl", "-sS", "-w", "\n%{http_code}",
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            "-H", f"apikey: {SUPABASE_KEY}",
            "-H", f"Authorization: Bearer {SUPABASE_KEY}",
            "-H", "Content-Type: application/json",
            "-H", "Prefer: return=representation",
            "-d", payload
        ],
        capture_output=True, text=True, timeout=30
    )
    
    output = result.stdout.strip()
    lines = output.split("\n")
    http_code = lines[-1] if lines else "???"
    response_body = "\n".join(lines[:-1])
    
    if http_code.startswith("2"):
        try:
            resp = json.loads(response_body)
            if isinstance(resp, list) and len(resp) > 0:
                print(f"  ✓ Published! ID: {resp[0].get('id', 'unknown')}")
                print(f"  ✓ Slug: {resp[0].get('slug', 'unknown')}")
                print(f"  ✓ Category: {resp[0].get('category', 'unknown')}")
            else:
                print(f"  ✓ Published! Response: {response_body[:200]}")
        except:
            print(f"  ✓ Published! HTTP {http_code}")
    else:
        print(f"  ✗ FAILED! HTTP {http_code}")
        print(f"  Response: {response_body[:500]}")

print("\n\nDone! All articles processed.")
