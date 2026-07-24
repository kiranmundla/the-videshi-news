#!/usr/bin/env python3
"""NRI World writer – 2026-07-13 09:00 PT
Two articles:
  1. Ro Khanna detained by Israeli settlers in West Bank
  2. Shrey Parikh wins 2026 Scripps Spelling Bee — Indian American dynasty continues
"""

import json, uuid, os, sys, re
from datetime import datetime, timezone

# ── Supabase setup ──────────────────────────────────────────────────────────

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser("~/workspace/.env.supabase"))

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
    sys.exit(1)

def make_slug(base):
    slug = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"{slug}-{today}"

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ══════════════════════════════════════════════════════════════════════════════
# Article 1: Ro Khanna detained by Israeli settlers
# ══════════════════════════════════════════════════════════════════════════════

art1_body = """\
When armed Israeli settlers surrounded a van carrying U.S. Congressman Ro Khanna near the demolished Palestinian village of Khirbet Zanuta on July 8, the Silicon Valley lawmaker became, by his own account, "probably the first American politician who's been detained by the IDF and Israeli settlers." For the Indian American community, the incident has thrown a spotlight on a figure who may yet become the first person of Indian descent to mount a serious bid for the White House.

## What Happened at Khirbet Zanuta

Khanna, a Democrat representing California's 17th congressional district, was visiting the southern West Bank as part of a delegation examining the aftermath of settler violence. According to Khanna and his aide Cameron Kasky, settlers carrying American-made M4 rifles blocked the group's vehicles, kicked the tyres of their van, and filmed the Americans while laughing and mocking them.

When Israel Defense Forces soldiers arrived, Khanna says they sided with the settlers rather than the American officials. "We were detained for about 20 minutes, fearful of our lives," he told NBC's *Meet the Press*. The IDF then kept the group blocked in for a further 55 minutes — roughly 75 minutes in total — before Israeli police intervened and cleared the road. The group had contacted the U.S. Embassy in Jerusalem during the ordeal.

The IDF has disputed Khanna's version of events, saying soldiers dispersed the Israeli civilians and allowed the vehicles to continue. Israeli Prime Minister Benjamin Netanyahu, appearing on the same programme, attributed the confrontation to "150 juvenile delinquents" who he said were not representative of the settler community.

"The IDF is lying," Khanna shot back. "What happened was unprecedented."

## An Indian American in the Arena

The incident has drawn particular attention because of who Khanna is — and what he may become. Born Rohit Khanna in Philadelphia in 1976 to Punjabi Hindu immigrants who had arrived from India in 1968, he is the grandson of Amarnath Vidyalankar, a journalist and freedom fighter who was imprisoned during India's independence movement.

Khanna's father studied engineering at the Indian Institute of Technology before earning a graduate degree at the University of Michigan. His mother was a schoolteacher. Their son went on to the University of Chicago and Yale Law School, served as a deputy assistant secretary in the Obama Commerce Department, and in 2016 won a congressional seat in the heart of Silicon Valley. He now co-chairs the Congressional Caucus on India and Indian Americans.

More recently, Khanna has been making trips to early-voting presidential states and holding town halls in Republican-held districts — moves that national outlets have interpreted as groundwork for a 2028 presidential run. If he enters the race, he would be among the most prominent Indian Americans ever to seek the presidency.

## The Broader Stakes

Khanna has positioned himself as a progressive voice on foreign policy, co-sponsoring a resolution that labelled Israel's military actions in Gaza a genocide. The West Bank detention has amplified his profile on that front, giving him a firsthand account that few American politicians can match.

For Indian Americans — a community of roughly 4.8 million that has produced tech CEOs, cabinet secretaries, and a vice president — the episode is a reminder that political visibility brings both opportunity and risk. Khanna's willingness to enter a volatile conflict zone, and his unsparing public response to the Israeli government, signals a kind of assertiveness that the community's political class has not always displayed.

Whether the incident accelerates or complicates his presidential ambitions remains to be seen. What it has already done is ensure that Ro Khanna — the grandson of an Indian freedom fighter, the son of IIT-educated immigrants, and a sitting congressman who was detained at gunpoint in the West Bank — is a name the American public will not easily forget.
"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Indian American Congressman Ro Khanna Detained at Gunpoint by Israeli Settlers in West Bank",
    "subheadline": "The Silicon Valley lawmaker — a potential 2028 presidential candidate and grandson of an Indian freedom fighter — says IDF soldiers sided with the armed settlers who held his group for 75 minutes.",
    "slug": make_slug("ro-khanna-detained-israeli-settlers-west-bank"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Khanna is among the most prominent Indian Americans in U.S. politics, a potential 2028 presidential candidate whose family story — from a freedom fighter's household in Punjab to Silicon Valley — embodies the trajectory of the Indian diaspora.",
    "tags": ["nri", "diaspora", "politics", "ro-khanna", "indian-american", "congress", "west-bank", "2028-election"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/us-democrat-ro-khanna-detained-by-israeli-settlers-during-west-bank-visit-2026-07-11/"},
        {"name": "Daily Caller", "url": "https://dailycaller.com/2026/07/12/ro-khanna-demands-israel-prosecute-detained-west-bank/"},
        {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/news/world/netanyahu-juvenile-delinquents-khanna-west-bank/"},
        {"name": "Fox News", "url": "https://www.foxnews.com/politics/house-democrat-ro-khanna-says-detained-armed-israeli-settlers-west-bank"},
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Ro_Khanna%2C_official_portrait%2C_115th_Congress_%283x4%29.jpg/1280px-Ro_Khanna%2C_official_portrait%2C_115th_Congress_%283x4%29.jpg",
    "image_caption": "Congressman Ro Khanna, who represents California's 17th congressional district in Silicon Valley",
    "image_attribution": "Wikimedia Commons / U.S. Congress",
    "body": art1_body.strip(),
}


# ══════════════════════════════════════════════════════════════════════════════
# Article 2: Shrey Parikh wins Scripps Spelling Bee
# ══════════════════════════════════════════════════════════════════════════════

art2_body = """\
When fourteen-year-old Shrey Parikh of Rancho Cucamonga, California, correctly spelled "bromocriptine" to clinch the 101st Scripps National Spelling Bee on May 28, he did more than win a trophy and a $50,000 cheque. He extended what has become one of the most extraordinary winning streaks in American competitive culture: 31 of the last 37 Scripps champions have been of Indian origin.

## A Record-Setting Finish

The competition at DAR Constitution Hall in Washington took three days to whittle 247 spellers down to a final showdown. After 18 rounds failed to produce a decisive winner, the Bee moved to its spell-off format — a 90-second sprint in which each finalist must correctly spell as many words as possible from a predetermined list.

Parikh, an eighth-grader at Day Creek Intermediate School in San Bernardino County, rattled off 32 correct spellings in the allotted time — a new record, surpassing the 29 set by Bruhat Soma in 2024. His opponent, twelve-year-old Ishaan Gupta of Jersey City, New Jersey, was formidable in his own right, correctly spelling 25 words. Third place went to Sarv Dharavane, a twelve-year-old from Dunwoody, Georgia, who finished third for the second consecutive year and has two more years of eligibility.

For Parikh, the victory capped a steady climb. He first appeared at the national competition in 2022, finishing tied for 89th. By 2024, he had risen to a tie for third. This year, he arrived as one of the favourites and delivered.

## The Indian American Dynasty

The numbers are now so lopsided that they have become their own story. Since Nupur Lala's victory in 1999 — immortalised in the documentary *Spellbound* — Indian American children have dominated the competition with a consistency that defies easy explanation. In 2019, seven of eight co-champions were of Indian descent. Last year, Faizan Zaki of Plano, Texas, continued the streak. With Parikh's win, the tally stands at 31 of the past 37 champions.

The phenomenon predates the current streak. Balu Natarajan became the first Indian American champion in 1985, when an Associated Press headline read simply, "Immigrants' son wins National Spelling Bee." Four decades later, the headline barely registers as news.

Researchers and journalists have offered several explanations. The North South Foundation, a nonprofit founded by Indian Americans, organises hundreds of regional spelling competitions across the country, creating a feeder system that channels talented young spellers toward the national stage. Marya Hannun, writing in *Foreign Policy*, has pointed to India's educational tradition of rote learning and memorisation, and to the tendency of highly skilled immigrant families to direct their children toward academically oriented pursuits.

There is also a network effect. Indian American families share information about enrichment activities, coaching resources, and competition strategies through community organisations, temples, and informal channels. Success breeds familiarity, which breeds more success. When a child from your community wins on national television, the competition stops being abstract.

## More Than a Spelling Contest

The Bee's Indian American dominance is often treated as a charming curiosity — a quirky statistic for sports-page trivia columns. But it reflects something more substantive about the Indian diaspora's place in American life.

Indian American households report a median income of $147,000, more than double the national median. Indians received 74 per cent of H-1B visas approved in fiscal 2021. There are roughly 4.8 million people of Indian origin in the United States, making them the country's second-largest immigrant group. The spelling bee dynasty is, in a sense, the most visible expression of a community that has invested heavily in its children's education and reaped conspicuous results.

But the dominance also carries a subtler cultural weight. For first-generation immigrant parents — many of whom arrived on student or work visas and built their American lives from scratch — a child on the national stage, spelling words most native English speakers have never encountered, is a form of arrival. It is proof that the bet paid off.

## What Comes Next

Parikh, for his part, is not done. His interests extend well beyond spelling, and at fourteen, he has the academic runway ahead of him. Gupta, at twelve, has years of eligibility remaining. Dharavane, also twelve, has already finished third twice and will almost certainly be back.

The safe bet, based on 25 years of evidence, is that many of them will have Indian surnames. The question is no longer whether Indian American children will dominate the Scripps National Spelling Bee. It is whether the rest of the field can figure out how to keep up.
"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Shrey Parikh Wins Scripps Spelling Bee With Record-Setting Performance — 31 of Last 37 Champions Are Indian American",
    "subheadline": "The fourteen-year-old from California spelled 32 words in 90 seconds, breaking the spell-off record and extending the Indian American community's remarkable quarter-century dominance of the competition.",
    "slug": make_slug("shrey-parikh-scripps-spelling-bee-indian-american-dynasty"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Indian American children have won 31 of the last 37 Scripps National Spelling Bees, a dynasty fuelled by community networks, immigrant-family educational investment, and organisations like the North South Foundation.",
    "tags": ["nri", "diaspora", "education", "spelling-bee", "scripps", "indian-american", "shrey-parikh", "achievement"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Scripps National Spelling Bee / GlobeNewswire", "url": "https://www.globenewswire.com/news-release/2026/05/29/scripps-national-spelling-bee-2026"},
        {"name": "LatestLY / IANS", "url": "https://www.latestly.com/india/shrey-parikh-wins-scripps-national-spelling-bee-2026/"},
        {"name": "Bleacher Report", "url": "https://bleacherreport.com/articles/scripps-national-spelling-bee-2026-results"},
        {"name": "Psychology Today", "url": "https://www.psychologytoday.com/us/blog/the-athletes-way/202506/why-indian-american-kids-dominate-the-national-spelling-bee"},
    ]),
    "score_total": 76,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/1b/Scrippsstage.jpg",
    "image_caption": "The stage at the Scripps National Spelling Bee, where Indian American contestants have dominated for a quarter century",
    "image_attribution": "Wikimedia Commons / Protobowladdict, CC BY 4.0",
    "body": art2_body.strip(),
}


# ── Insert into Supabase ────────────────────────────────────────────────────

import subprocess

def insert_article(article, label):
    payload = json.dumps(article, ensure_ascii=False)
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
        capture_output=True, text=True, timeout=30,
    )
    status_ok = '"id"' in result.stdout and '"headline"' in result.stdout
    if status_ok:
        print(f"✅ {label}: inserted — slug={article['slug']}")
    else:
        print(f"❌ {label}: FAILED")
        print(f"   stdout: {result.stdout[:500]}")
        print(f"   stderr: {result.stderr[:300]}")
    return status_ok


ok1 = insert_article(art1, "Art1 (Ro Khanna)")
ok2 = insert_article(art2, "Art2 (Spelling Bee)")

print(f"\nDone: {int(ok1) + int(ok2)}/2 articles inserted.")
if not (ok1 and ok2):
    sys.exit(1)
