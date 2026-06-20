#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-20 10:30 UTC run.

Story: NEET-UG 2026 re-test on Sunday, June 21, 2026. After India cancelled
the May 3 exam over a paper leak (2.3 million results scrapped), the NTA is
re-running the medical entrance test nationwide tomorrow. Two diaspora-specific
hooks the feed has NOT covered in the news category:
  1. India closed ALL 14 overseas NEET centres (Dubai, Abu Dhabi, Sharjah,
     Kuwait City, Doha, Muscat, Manama, Riyadh, Bangkok, Colombo, Kathmandu,
     Kuala Lumpur, Lagos, Singapore) — forcing Gulf-based NRI families to fly
     their children to India to sit the exam. Coaching centres in the UAE call
     it a "complete shock"; working parents must take leave, book flights and
     accommodation, and some students have no relatives in India to stay with.
  2. India imposed an UNPRECEDENTED nationwide block on Telegram (June 16-22)
     after the NTA said cheating rackets used the app to defraud candidates
     ahead of the re-test. Founder Pavel Durov said it punishes 150M+ ordinary
     Indian users, "not the insiders who leaked the exam materials."

Supreme Court (Friday) refused urgent hearings on re-test pleas; all NEET
matters are before Justice PS Narasimha's bench. CBI probe ongoing, arrests in
several states. ~1,600 candidates flagged anxiety over admit-card centre
changes. ISRO ex-chief K Radhakrishnan's committee questioned by the court.

Dedup: verified NO news-category article on NEET, the June 21 re-test, the
overseas-centre closure, or the Telegram ban in the last 7 days. Fresh.

Diaspora angle: tens of thousands of Gulf-resident Indian families with NEET
aspirants must now uproot to India for a single exam day after the overseas
centres were scrapped — direct cost, stress, and logistics landing on exactly
the NRI households The Videshi serves.

Sources: Reuters ("India temporarily blocks Telegram app over medical exam
fraud"); Reuters ("India med school hopefuls beset with anxiety before they
retake scandal-tainted exam"); LiveLaw ("Supreme Court Refuses To Hear Pleas
Concerning NEET-UG 2026 Ahead Of June 21 Retest"); Khaleej Times / EdArabia
("UAE Students Under Pressure After India Closes International Centres").
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

# Hero: guardians and families gathered outside an Indian entrance-examination
# centre (West Bengal Joint Entrance Examination, Howrah). Wikimedia Commons,
# CC BY-SA. Downloaded from Commons and re-hosted on Supabase storage for
# permanence. Verified HTTP 200, image/jpeg, 801,276 bytes, 2048x1536.
HERO_URL = ("https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/"
            "public/article-images/news-neet-retest-overseas-centres-20260620.jpg")


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
    print("\n=== Article: NEET-UG 2026 re-test, overseas centres closed ===")

    slug = ("neet-ug-2026-retest-june-21-overseas-centres-closed-"
            "gulf-nri-families-telegram-ban-20260620")

    body = """Sometime before dawn on Sunday, in a school courtyard in Kerala, a mother from Abu Dhabi will hand her daughter a bottle of water, a transparent admit card, and a hug — the same scene that will repeat across more than 5,000 centres in India as roughly **2.3 million** young people sit the most scrutinised exam of their lives for a second time.

This is **NEET-UG 2026**, the single national gateway to every medical seat in India. It was first held on May 3. Then, after authorities said its question paper had leaked through organised cheating networks, the government did something it had never done at this scale: it **cancelled the results of all 2.3 million candidates** and ordered a nationwide re-test. That re-examination falls on **June 21**.

## For Gulf families, the exam moved 2,000 miles

For the diaspora, the cruellest twist is geographic. Since 2021, Indian students living abroad could sit NEET at one of **14 overseas centres** — Dubai, Abu Dhabi and Sharjah in the UAE, plus Kuwait City, Doha, Muscat, Manama, Riyadh, Bangkok, Colombo, Kathmandu, Kuala Lumpur, Lagos and Singapore. This year, all of them were quietly scrapped. Every international candidate must now travel to India to write the test.

In the Gulf, where lakhs of Indian families have settled and where a medical seat back home is a generational ambition, the decision landed like a thunderclap. "We had been petitioning the Indian Embassy in the UAE for years to have a test centre in Dubai, and we finally had one just a couple of years ago," said Alka Malik, who runs the Ascentria coaching centre. "The removal of this international test centre came suddenly and was a complete shock."

The cost is not only money, though that is real — flights, hotels near the centre, leave from work. It is logistics layered on a teenager already carrying two years of preparation. "I have two younger children in Grade 8 and Grade 2," said Sherin Shafeeq, an Abu Dhabi parent whose daughter Riya is appearing. "One of us will have to stay in the UAE to look after them while the other travels to India. Moreover, we must pay for the tickets back home and find accommodation near the centres." Some students, coaches note, have no first-degree relatives in India at all and must arrange a place to stay in an unfamiliar city, days before the most important morning of their academic lives.

## India pulls the plug on Telegram

To secure the re-test, India reached for an unprecedented lever. On June 16, the National Testing Agency announced a temporary nationwide block on **Telegram**, in effect until June 22, "in response to the organised use of the platform by cheating rackets to defraud candidates." It was the first time India has blocked the messaging app outright.

Telegram founder Pavel Durov pushed back hard. The ban, he argued, punishes more than **150 million ordinary Indian users**, "not the insiders who leaked the exam materials." He added that the leaks had simply migrated: "the ban hasn't stopped anything. The leaks just moved to other apps." A multi-agency investigation, including a CBI probe, is under way, with arrests reported across several states and officials promising tougher penalties for exam malpractice.

## The courts step back

Students hoping for last-minute relief from the judiciary found little. On Friday, the Supreme Court **refused to entertain urgent pleas** tied to the June 21 re-test, with Chief Justice Surya Kant directing that all NEET matters go before the bench of Justice P.S. Narasimha. One counsel told the court that around 1,600 candidates were under "tremendous pressure and anxiety," with some unable to download admit cards and others receiving cards listing different exam centres than they had chosen. The court declined to intervene, noting the matters were already being handled.

Earlier pleas to switch the re-test to a secure computer-based format were also turned down; the exam stays pen-and-paper. The court has separately pressed the NTA — and the K. Radhakrishnan committee set up after the 2024 NEET controversy — on why, despite monitoring, a leak recurred, signalling that a permanent fix for India's exam machinery is overdue.

## Why the diaspora is watching

For Non-Resident Indians, NEET is not an abstract policy story. It is the exam that decides whether a child raised in Sharjah or Doha can become a doctor in the country their parents left. This year it asks those families to absorb a cancelled paper, a re-test, a shuttered local centre, and a cross-continental journey — all for one three-hour sitting on a Sunday morning.

When the bell rings on June 21, the question will not only be how the students perform. It will be whether the agency that runs India's highest-stakes exam can finally guarantee that, this time, the paper stays sealed.
"""

    return {
        "headline": "India Scrapped the Gulf's NEET Centres. Now Diaspora Families Are Flying Their Kids Home for Sunday's Re-Test.",
        "subheadline": "After a paper leak forced India to cancel 2.3 million NEET results, the medical entrance exam is being re-run on June 21 — with every overseas centre closed and Telegram blocked nationwide to stop cheating rackets.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-education",
        "status": "review",
        "is_editorial": False,
        "image_url": HERO_URL,
        "image_caption": "Families and guardians wait outside an entrance-examination centre in India as candidates sit the test.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "India closed all 14 overseas NEET-UG centres for the June 21 re-test, forcing thousands of Gulf-resident Indian families to book flights, take leave and arrange accommodation in India so their children can sit a single three-hour medical-entrance exam.",
        "sources": [
            "Reuters \u2014 'India temporarily blocks Telegram app over medical exam fraud' (re-test June 21, 2.3 million results cancelled, Durov response)",
            "Reuters \u2014 'India med school hopefuls beset with anxiety before they retake scandal-tainted exam' (CBI probe, arrests, tightened security)",
            "LiveLaw \u2014 'Supreme Court Refuses To Hear Pleas Concerning NEET-UG 2026 Ahead Of June 21 Retest' (1,600 candidates, admit-card centre changes, Justice P.S. Narasimha bench)",
            "Khaleej Times / EdArabia \u2014 'UAE Students Under Pressure After India Closes International Centres for Medical Exam' (overseas centres scrapped, Gulf-parent accounts)",
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
