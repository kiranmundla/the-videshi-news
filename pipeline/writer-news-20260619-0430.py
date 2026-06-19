#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-19 04:30 UTC run.

Story: The Fall 2026 US intake is collapsing in real time. Hyderabad education
consultants — the bellwether for India's largest study-abroad pipeline — report
a 70-80% drop in students opting for US universities this cycle, driven by the
ongoing freeze/scarcity of F-1 visa appointment slots, a spike in rejection
rates (~35%, a 10-year high), and unconfirmed bookings. In parallel, India's
Embassy and six consulates held an emergency virtual interaction with ~150
student-association office bearers from 90 US universities (reported ~20 hrs
ago) on safety and staying connected, and fresh sentiment data shows ~89% of
Indian students abroad now eyeing a move back / Indian employers, with Leap
data showing the US has slipped to a country students *compare* rather than
default to.

Distinct from prior coverage: the feed already has (1) "Indian Student Numbers
Fell 6.9%" (06-17, historical Open-Doors-style enrollment), (2) "Students
Crashed the Visa Portal on Day One" (06-15, the June 14 reopening rush), and
(3) "Biggest Change to US Student Visas in 30 Years" (06-18, the DHS Duration
of Status rule). THIS story is the forward-looking demand-destruction angle:
the actual Fall 2026 intake cratering on the ground in India + the diplomatic
response + the pivot away from the US. No existing article covers the 70-80%
consultant figure, the embassy's virtual student outreach, or the multi-country
shortlist shift.

Diaspora angle: Indian families in the US are the parents, relatives and
sponsors of these applicants; a collapsed Fall intake reshapes who joins the
diaspora, strains university towns built on Indian enrollment, and signals to
NRIs already here how welcoming (or not) the system has become.

Sources: The Indian Eye (Hyderabad consultants, 1 day ago; Embassy virtual
interaction, ~20 hrs ago), Reuters (US law schools int'l application drop,
India -23%), India Education Diary / Leap (multi-country shortlist data),
Tupaki (89% looking back to India sentiment).
"""

import os
from datetime import datetime, timezone
import requests

UA = "TheVideshi/1.0 (thevideshi.com)"


def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


load_env(os.path.expanduser("~/.env.supabase"))

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

HEADERS_SB = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# Hero: public-domain F-1 student visa interview photo (US Embassy, "Super
# Friday" visa workday), downloaded from Wikimedia Commons, resized to 1600px
# and uploaded to Supabase storage. Verified HTTP 200, image/jpeg, ~268KB.
HERO_URL = ("https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/"
            "public/article-images/news-india-student-visa-collapse-202606190430.jpg")


def validate_get(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20,
                         stream=True, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        chunk = r.raw.read(8000)
        r.close()
        return r.status_code == 200 and "image" in ct and len(chunk) > 5000
    except Exception as e:
        print("  validate err", e)
        return False


def insert_article(article):
    r = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB, json=article, timeout=25,
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  Inserted: {data[0].get('headline','?')[:80]}")
            return data[0]
        print(f"  Inserted (raw): {r.text[:120]}")
        return data
    print(f"  Insert failed ({r.status_code}): {r.text[:300]}")
    return None


def article():
    print("\n=== Article: Fall 2026 US intake collapse ===")

    slug = ("indian-students-us-fall-2026-intake-collapse-70-80-percent-drop-"
            "visa-slot-freeze-20260619")

    body = """For years, the rhythm was predictable. By mid-June, the bulk of India's US-bound students had cleared their visa interviews and were booking flights for an August start. This year, consultants in Hyderabad \u2014 the single biggest feeder city for Indian students heading to American campuses \u2014 say that rhythm has broken. They are reporting a **70 to 80 percent drop** in students opting for US universities this cycle, an intake collapse unfolding in real time as the Fall 2026 semester approaches.

The cause is not a lack of ambition. It is a lack of appointments. A prolonged freeze and scarcity of F-1 visa interview slots, paired with a sharp rise in rejection rates, has left thousands of admitted students unable to complete the one step that turns an offer letter into a boarding pass.

## "The worst in years"

The mood among India's study-abroad consultants \u2014 usually relentlessly upbeat \u2014 has turned grim. "By this time usually, most students are done with their visa interviews and are preparing to fly," said Sanjeev Rai of Hyderabad Overseas Consultant. "This year, we're still refreshing the portal every day hoping for a slot to open. It's the worst in years."

Arvind Manduva of the I20 Fever consultancy put the drop at around 80 percent and described daily panic calls. "If slots aren't released in the next few days, thousands of dreams will be shattered," he said. American authorities had promised to release appointment slots in phases after a June reopening, but students say confirmations have been thin and unpredictable \u2014 even those who managed to book have not always received confirmation.

The numbers behind the anxiety are stark: visa denial rates for international students have climbed to roughly **35 percent**, a 10-year high, and many applicants are simply running out of runway. "I really could not wait. I might just lose out on a year," one student said, explaining why they withdrew their application altogether.

## A diplomatic scramble

The disruption has been serious enough to pull India's diplomatic machinery into damage-control mode. In an unusual move, the Indian Embassy in Washington and its consulates in Atlanta, Chicago, Houston, New York, San Francisco and Seattle held a virtual interaction with Indian students from across the United States, led by Charg\u00e9 d'Affaires Ambassador Sripriya Ranganathan.

About 150 Indian Student Association office bearers from 90 US universities joined the session, which covered student well-being, safety, and ways to stay connected with the embassy and the larger diaspora. Officials urged students to register on consular websites and keep emergency contacts handy \u2014 outreach that gained urgency amid a spate of deaths of Indian and Indian-origin students on US campuses in recent months.

## The pivot away from America

What makes this cycle different from past visa crunches is that students now have alternatives \u2014 and they are using them. New analysis from Leap, one of South Asia's largest study-abroad platforms, found that **62 percent** of student conversations now involve comparing two or more destinations before deciding, rather than treating the US as the automatic default.

In that data, the United Kingdom led as the primary destination at 45.5 percent of discussions, with New Zealand, the UAE, Ireland and Canada all drawing serious interest. The US was referenced in nearly 61 percent of conversations \u2014 but increasingly as a country being *assessed against alternatives*, with students citing visa difficulty, H-1B costs and policy uncertainty as reasons to hedge.

Sentiment surveys point the same way. Recent reporting suggests as many as **89 percent** of Indian students abroad are now looking at Indian employers or contemplating a move back home, a remarkable reversal for a generation that long saw an American degree as the surest path to a global career. The fallout is visible at the graduate level too: Reuters reported that applications to US law schools' LL.M. programs from India fell **23 percent**, with admissions officers blaming the immigration crackdown and a sense that the US is "maybe not as welcoming to international students as it used to be."

## Why it matters to NRIs

For the Indian diaspora in America, this is not a distant statistic. These applicants are the younger siblings, cousins and children of families already settled in the US \u2014 the next wave of a community that has long renewed itself through student migration. A collapsed Fall intake means emptier campus desi associations, strained university towns whose economies lean on Indian enrollment, and fewer future H-1B workers and founders entering the pipeline.

It also sends a signal. The same families who built lives in the US over decades are now watching the door narrow for the people they hoped would follow. Whether this is a one-year shock or the start of a lasting redirection of Indian talent toward Britain, Canada and India itself may be one of the most consequential diaspora questions of the decade."""

    return {
        "headline": "India's US College Pipeline Is Cratering. Consultants Report a 70-80% Drop for This Fall.",
        "subheadline": "A freeze on F-1 visa appointment slots and a 10-year-high 35% denial rate have stalled the Fall 2026 intake \u2014 prompting an emergency embassy outreach to students and a growing pivot toward the UK, Canada and India.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": HERO_URL,
        "image_caption": "Students wait for F-1 student visa interviews during a special US Embassy visa workday.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "These stalled applicants are the younger relatives and children of Indian families already in the US, and a collapsed Fall intake reshapes who joins the diaspora while signaling to NRIs how welcoming the system has become.",
        "sources": [
            "The Indian Eye \u2014 'Visa crisis prompts a 70-80% drop in Indian students opting for US Universities' (June 18, 2026)",
            "The Indian Eye \u2014 'Indian Embassy and Consulates in the US hold virtual interaction with Indian students' (June 18, 2026)",
            "Reuters \u2014 'US law schools see sharp drop in international student applications' (India applications down 23%)",
            "India Education Diary / Leap \u2014 'Indian Students Are Building Multi-Country Study-Abroad Shortlists as ROI Becomes the Deciding Factor' (June 2026)",
        ],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    art = article()
    wc = len(art["body"].split())
    print(f"  word count: {wc}")
    print(f"  headline chars: {len(art['headline'])}")
    print(f"  subheadline chars: {len(art['subheadline'])}")
    if wc < 400:
        print("  word count below floor, aborting")
    elif len(art["headline"]) > 200:
        print("  headline too long, aborting")
    elif not validate_get(art["image_url"]):
        print("  hero image failed validation, aborting")
    else:
        insert_article(art)
