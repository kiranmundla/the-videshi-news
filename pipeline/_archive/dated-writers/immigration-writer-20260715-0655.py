#!/usr/bin/env python3
"""Immigration writer — 2026-07-15 morning run."""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")


# ─────────────────────────────────────────────────────────────────
# ARTICLE 1
# ─────────────────────────────────────────────────────────────────

art1_body = """Congress has never been short on bills that tinker with the H-1B visa program — raising fees here, tightening eligibility there, adjusting the lottery mechanics. That is not what is happening now. A cluster of Republican lawmakers is no longer interested in reform. They want the program gone.

Rep. Riley Moore of West Virginia made that explicit in an interview with Fox News Digital published Tuesday. "I think the H-1B visa program is a scam, and it's one that has been perpetrated on the American worker for far too long," he said. Moore did not couch his position in the usual language of "reform" or "modernization." He used the word "abolish," and he claimed he is not alone.

"I'm certainly not the lone voice in this," Moore told Fox News. "I have had many, many of my colleagues here in Congress come up and talk with me since I've started talking about this and thank me for speaking up." He added that others are "starting to speak up as well."

## The Bills on the Table

The legislative pipeline is already stocked. At least three bills introduced this Congress would fundamentally dismantle or freeze the H-1B system:

**The End H-1B Visa Abuse Act of 2026**, introduced by Rep. Eli Crane of Arizona in April, would impose a three-year moratorium on all new H-1B visas. When the program resumes, the annual cap would drop from 65,000 to 25,000, the lottery would be replaced by a wage-based selection system with a $200,000 minimum salary, and H-1B holders would be barred from bringing dependents or pursuing permanent residency. The bill would also kill the Optional Practical Training program that lets international students work after graduation. Seven original cosponsors signed on, including Reps. Paul Gosar, Andy Ogles, and Wesley Hunt.

**The American White-Collar Worker Jobs Act**, introduced by Rep. Chip Roy of Texas in June, builds on Crane's framework. It would end "dual intent" — the longstanding policy that lets H-1B holders work temporarily while also pursuing a green card — and require visa holders to prove they maintain a residence abroad with no intention of staying permanently.

**The End H-1B Now Act**, introduced by Rep. Marjorie Taylor Greene in January, takes the bluntest approach: terminate the program outright.

## What Is Driving the Push

The proximate catalyst was Microsoft. The company laid off 4,800 workers — including 1,600 from its Xbox division — in the same period it was approved for 2,273 new H-1B visas. The optics ignited bipartisan fury online and gave restrictionist lawmakers a ready-made case study. Xbox CEO Asha Sharma, who is of Indian heritage but was born in Wisconsin, became a lightning rod for criticism that often blurred the line between policy objection and ethnic targeting.

Vice President JD Vance piled on last week, announcing a Department of Labor investigation into H-1B fraud involving "dozens of subpoenas." Labor Department Inspector General Anthony D'Esposito told Fox Business his team had whistleblowers "talking about some of the biggest companies," naming Cognizant specifically.

Moore's argument extends beyond fraud. He contends the entire premise of the program is flawed. "This is a rigged market against American workers," he said. "The American worker is the only worker on the planet that has to compete with labor from all over the world inside their own borders."

## What This Means for Indian Professionals

Indians hold approximately 73 percent of all H-1B visas, according to Pew Research Center data. The program is the primary legal pathway for Indian technology workers, engineers, and healthcare professionals to work in the United States — and, eventually, to seek permanent residency.

If any of these bills gained traction, the consequences would cascade. A three-year freeze would strand tens of thousands of Indian professionals mid-career, unable to renew visas or transition to green card applications. Ending dual intent would sever the connection between temporary work and permanent immigration that has defined the Indian professional pipeline for decades. Killing OPT would cut off the bridge that Indian students use between graduation and the H-1B lottery.

Immigration attorneys have pushed back hard. Doris Brosnan, an employment attorney at von Briesen & Roper with 27 years of practice, told the Milwaukee Journal Sentinel that abuse in the H-1B program is "quite rare." Reddy Neumann Brown, a Houston-based immigration law firm, called Crane's bill "an attempt to dismantle the high-skilled immigration system piece by piece."

The political math remains uncertain. None of these bills have advanced through committee, and the business lobby — led by the likes of Amazon, Google, and the hospital industry — retains significant influence. But the rhetorical shift matters. When a sitting congressman says "abolish" and claims growing support among colleagues, the Overton window has moved. For the roughly 440,000 Indian professionals currently on H-1B status, the ground beneath their feet just became a little less stable.
"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Word in Congress Is No Longer Reform. It Is Abolish",
    "subheadline": "At least three bills would freeze, gut, or kill the H-1B program entirely. A West Virginia congressman says the support behind them is growing fast.",
    "slug": make_slug("h1b-abolish-movement-congress-riley-moore-crane-roy"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "73 percent of H-1B holders are Indian — if any abolition bill gains traction, hundreds of thousands of Indian professionals face career disruption, visa limbo, and a severed pathway to permanent residency.",
    "tags": ["h1b", "congress", "riley-moore", "eli-crane", "chip-roy", "immigration-reform", "abolition"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Fox News Digital", "url": "https://foxnews.com/politics/demand-end-scam-visa-program-replacing-american-workers-surges-west-virginia-congressman-reveals"},
        {"name": "Rep. Eli Crane (official)", "url": "https://crane.house.gov/media/press-releases/rep-crane-introduces-legislation-pause-and-reform-broken-h-1b-visa-process"},
        {"name": "Rep. Chip Roy (official)", "url": "https://roy.house.gov/media/press-releases/rep-roy-introduces-legislation-end-h-1b-abuse-protect-american-tech-workers"},
        {"name": "Milwaukee Journal Sentinel / jsonline.com", "url": "https://www.jsonline.com/story/news/politics/2026/07/11/in-targeting-h-1b-visas-jd-vance-ties-fraud-to-immigration-rhetoric/84805210007/"},
        {"name": "Reddy Neumann Brown PC", "url": "https://www.rnlawgroup.com/the-end-h-1b-visa-abuse-act-a-political-attack-disguised-as-reform/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/16/Moore_Riley_119th_Congress_%28cropped2%29.jpg",
    "image_caption": "Rep. Riley Moore of West Virginia, who is leading the push to abolish the H-1B visa program",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}


# ─────────────────────────────────────────────────────────────────
# ARTICLE 2
# ─────────────────────────────────────────────────────────────────

art2_body = """Sen. Bernie Moreno of Ohio is about to put Democrats in an awkward position. The freshman Republican is circulating legislation modeled almost line-for-line on a 1993 immigration bill written by the late Senate Majority Leader Harry Reid — a Democrat so revered in Nevada that they named an airport after him.

Reid's original bill, introduced more than three decades ago, proposed slashing legal immigration levels, restricting birthright citizenship, capping refugee admissions at 50,000 per year, and streamlining deportations with limited judicial review. It never became law, but it reflected a bipartisan consensus on immigration restriction that has since vanished from the Democratic Party's platform.

Moreno is now weaponizing that history. "What it's going to do is highlight two things," he told Fox News Digital. "The Democrats of today are nothing like the Democrats of 1993 and, if they choose to reject a bill sponsored by their majority leader that they named an airport in Las Vegas after, then I think my Republican colleagues have no choice."

## The Birthright Citizenship Play

The bill arrives less than two weeks after the Supreme Court struck down President Trump's executive order restricting birthright citizenship in a 6-3 decision on June 30. Chief Justice John Roberts, writing for the majority, ruled that the 14th Amendment's Citizenship Clause protects children born on U.S. soil to unauthorized or temporarily present parents. "Citizenship, then and now, was the right to have rights," Roberts wrote.

Moreno's proposal would challenge that ruling through statute, reinterpreting the 14th Amendment's "subject to the jurisdiction" language to exclude certain categories of births. It joins Sen. Jim Banks' Citizenship Act of 2026, introduced July 13, which takes a similar approach by classifying unauthorized entry and "birth tourism" as part of an ongoing invasion.

The legislative pathway for either bill is steep — any statute that contradicts a Supreme Court constitutional ruling faces near-certain judicial invalidation. But the political signal is clear: the GOP is determined to keep birthright citizenship on the agenda, and it is willing to use Democrats' own legislative history as leverage.

## The Legal Immigration Cuts

For Indian Americans, the birthright citizenship provisions are less immediately relevant than the bill's legal immigration restrictions. Reid's 1993 framework proposed substantial reductions to the total number of visas issued annually. If Moreno's mirror version preserves that architecture, the implications for employment-based immigration could be severe.

The EB-2 category for India-born applicants already faces a wait of 11 to 17 years or more, with the Final Action Date stuck at January 15, 2015 as of the current Visa Bulletin. The EB-3 backlog is similarly crushing. Any legislative reduction in overall visa numbers would mechanically extend these waits even further — potentially pushing them past 20 years for applicants filing today.

The bill's refugee cap, set at 50,000 per year, is also notable. While refugees and employment-based immigrants draw from different visa pools, comprehensive immigration packages have historically linked the two. A cap on one category can create political cover for restrictions on others.

## The Deportation Fast Lane

The expedited removal provisions in the Moreno-Reid framework would limit judicial review of deportation orders, compressing the timeline for immigrants to challenge removal. For H-1B holders who fall out of status — whether due to a layoff, a processing delay, or an employer's failure to file paperwork on time — a narrower review window reduces the margin for error from weeks to days.

Immigration attorneys have warned that the current environment already creates "status traps" where workers lose authorization through no fault of their own. An expedited removal regime layered on top of existing enforcement priorities could turn a missed deadline into a deportation order with minimal opportunity to appeal.

## Why This Matters

The Moreno-Reid gambit is as much political theater as policy proposal. The odds of passing legislation that directly contradicts a Supreme Court ruling are slim. But the bill serves a purpose: it forces a vote, creates a record, and builds the case for a future constitutional amendment or a differently composed Court.

For Indian Americans watching the immigration landscape, the bill represents another data point in a pattern. The H-1B program faces abolition bills. Naturalization fees just jumped 75 percent. The $250 visa integrity fee from the reconciliation bill is now law. Green card applicants may soon need to leave the country to adjust status. Each policy individually is survivable. Taken together, they describe a system that is steadily raising the cost — in money, in time, and in uncertainty — of being a legal immigrant in the United States.

Moreno's bill may never become law. But the fact that a sitting senator can mirror a Democratic icon's immigration platform and call it radical tells you everything about how far the center of gravity has shifted.
"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "A Republican Senator Is Using Harry Reid's Own Immigration Bill Against Democrats. Legal Immigration Is in the Crossfire",
    "subheadline": "Sen. Bernie Moreno's proposal mirrors a 1993 Democratic bill nearly word for word — cutting legal immigration, restricting birthright citizenship, and fast-tracking deportations.",
    "slug": make_slug("moreno-reid-immigration-bill-legal-cuts-birthright"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Legal immigration cuts in the bill would mechanically extend EB-2 and EB-3 wait times for Indian applicants — already at 11-17 years — potentially past two decades for new filers.",
    "tags": ["legal-immigration", "bernie-moreno", "harry-reid", "birthright-citizenship", "visa-backlog", "eb2", "congress"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Fox News Digital", "url": "https://www.foxnews.com/politics/schumers-mentor-pushed-birthright-citizenship-crackdown-now-moreno-dares-democrats-reject-it"},
        {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/07/14/birthright-citizenship-fight-congress/90922168007/"},
        {"name": "Supreme Court ruling — Trump v. United States (birthright)", "url": "https://www.supremecourt.gov/"},
        {"name": "Khandelwal Law — EB-2 NIW Processing Times 2026", "url": "https://khandelwalaw.com/eb-2-niw-processing-time/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e0/Sen._Bernie_Moreno_official_photo%2C_119th_Congress_%28HR%29.jpg",
    "image_caption": "Sen. Bernie Moreno of Ohio, who is circulating immigration legislation modeled on Harry Reid's 1993 bill",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}


# ─────────────────────────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
