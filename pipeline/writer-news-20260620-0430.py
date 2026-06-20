#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-20 04:30 UTC run.

Story: The Federation of Indian Pilots (FIP) held a press conference (reported
~16 hrs ago) challenging the official AAIB narrative on Air India Flight AI171,
which crashed seconds after takeoff from Ahmedabad on June 12, 2025, killing 241
of 242 aboard plus people on the ground. The interim report attributed the crash
to a deliberate manual fuel cutoff (read by many as a pilot-suicide pact). FIP
President Capt. C.S. Randhawa says new simulator tests replicating the flight's
exact weight, balance and weather show a manual cutoff would take ~18 seconds to
drop the ram air turbine (RAT) — not the 4 seconds in the official timeline —
which he argues is "physically and technically impossible" under a manual
shutdown and instead points to a catastrophic systemic electrical failure that
tripped the engine switches. FIP cites the lone survivor's account of cabin
lights flickering, a documented history of unresolved electrical faults on the
airframe, and alleges India's top 787 expert (Capt. R.S. Sandhu) was sidelined.
FIP has submitted its data to Boeing and authorities and demands the final
report be halted until discrepancies are resolved.

Distinct from prior coverage: the feed has no article on the AI171 crash
investigation, the FIP simulator challenge, or the pilot-suicide-vs-electrical-
failure dispute. This is a fresh, forward-looking accountability story.

Diaspora angle: AI171 was a London-bound flight carrying many British-Indian and
NRI passengers; the diaspora has a direct stake in whether the dead Indian
captain is wrongly blamed versus a Boeing/787 systemic flaw that could affect
the global Dreamliner fleet NRIs fly on every week.

Sources: Madhyamam / IANS (FIP press conference, June 19, 2026); ANI (Randhawa's
earlier glitch claims, July 2025); The Sun (whistleblower electrical-failure
evidence, lawyers' petition); Wikipedia (AAIB investigation timeline).
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

# Hero: the actual accident aircraft, Air India Boeing 787-8 VT-ANB, photographed
# at London Heathrow (the airframe's regular route — AI171 was Ahmedabad→Gatwick).
# CC BY 2.0, Steve Knight (Flickr). Downloaded, resized to 1600px, uploaded to
# Supabase storage. Verified HTTP 200, image/jpeg, ~140KB.
HERO_URL = ("https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/"
            "public/article-images/news-air-india-ai171-electrical-failure-20260620.jpg")


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
    print("\n=== Article: FIP challenges AI171 crash narrative ===")

    slug = ("air-india-ai171-crash-pilots-body-electrical-failure-simulator-"
            "challenges-suicide-theory-20260620")

    body = """A year after Air India Flight AI171 fell out of the sky seconds after lifting off from Ahmedabad, the most charged question of India's deadliest aviation disaster in decades remains unsettled: did the men in the cockpit kill 241 people, or did the aircraft? This week, the country's largest pilots' body delivered its sharpest answer yet \u2014 and it points the finger squarely at the machine.

The Federation of Indian Pilots (FIP) held a press conference challenging the official account of the June 12, 2025 crash, which killed 241 of the 242 people on board the London-bound Boeing 787-8, along with people on the ground when it came down on a medical college hostel. Citing fresh simulator data, FIP President Captain C.S. Randhawa argued that a "massive systemic electrical failure," not a deliberate act by the crew, brought the Dreamliner down.

## The four-second problem

The dispute turns on a single, brutal number. The official interim report from India's Aircraft Accident Investigation Bureau (AAIB) found that the engine fuel-control switches moved from RUN to CUTOFF one after another, starving both engines, and that the aircraft's ram air turbine \u2014 a backup propeller that drops automatically when the plane loses power \u2014 deployed about four seconds later. Read alongside a cockpit recording in which one pilot asks the other why he cut off the fuel, many interpreted the report as describing a manual, even deliberate, shutdown.

Randhawa says that timeline collapses under testing. "Our simulator tests prove that a manual fuel cut-off takes a full 18 seconds to drop that backup turbine," he told reporters. "The official timeline of four seconds is physically and technically impossible under a manual shutdown scenario." The FIP says it recreated the flight's exact weight, balance and weather conditions, and that the turbine deployed far too quickly to fit the manual-cutoff story.

If the backup turbine dropped in four seconds, the federation argues, it is because the aircraft had already suffered a catastrophic electrical failure \u2014 one that crippled the systems, tripped the engine switches on its own, and left the crew as bystanders rather than culprits.

## A survivor's flickering lights

The pilots' body says its theory lines up with the physical evidence. The lone survivor of Flight 171 reported seeing the cabin lights flicker and dim moments before the aircraft began its terminal descent \u2014 exactly what a sudden, massive power loss would produce. The FIP also said the specific airframe had a "documented history of unresolved electrical problems" in the period leading up to the fatal flight.

The federation's argument echoes concerns raised independently by lawyers and aviation engineers. Petitioners who have submitted evidence to India's Supreme Court have pointed to the aircraft's final satellite transmissions as showing serious technical faults, and have questioned why the emergency locator beacon never activated and why the tail-section flight recorder showed signs of internal electrical arcing rather than simple fire damage.

## "Blame the dead pilots"

Beyond the physics, the FIP leveled a pointed institutional charge: that investigators sidelined the people best placed to disprove the official theory. Randhawa alleged that Captain R.S. Sandhu, widely regarded as India's foremost Boeing 787 expert, was kept out of the actual investigative testing.

"They are ignoring the input of our most experienced pilot because his knowledge would completely disprove their 'pilot suicide' theory," Randhawa said. "It is easier to blame dead pilots who cannot defend themselves than to confront a major mechanical or software flaw." The federation noted that the captain, Sumeet Sabharwal, and his co-pilot cannot answer for themselves, and that a finding of crew suicide carries lasting stigma for their families.

The FIP says it has formally submitted its simulator data and findings to both Boeing and Indian aviation authorities, and is demanding that publication of the final accident report be halted until the discrepancies over the turbine timing are fully investigated. It has also called for Captain Sandhu's immediate reinstatement to the investigation team.

## Why it matters to NRIs

AI171 was bound for London, and its passenger manifest read like a map of the diaspora \u2014 British-Indian families, students, and dual nationals heading home or abroad. For millions of NRIs who board a Dreamliner several times a year to cross between India and the West, the stakes of this fight are not abstract. If a dead Indian crew is wrongly blamed, two families carry an unjust verdict; if a systemic electrical or software flaw is being papered over, it is a flaw that still sits in the global 787 fleet the diaspora flies on.

The pressure also has an international dimension. The aircraft was American-designed and built, and the US National Transportation Safety Board is a party to the probe; how India handles a finding that could implicate Boeing rather than its own pilots will be watched far beyond Ahmedabad. For a community that lives in the air between two countries, the credibility of that final report is personal."""

    return {
        "headline": "India's Pilots Reject the AI171 'Suicide' Verdict. Their Simulator Says the Plane Failed, Not the Crew.",
        "subheadline": "The Federation of Indian Pilots says new tests show the official four-second timeline is 'physically impossible' \u2014 and points to a catastrophic electrical failure on the London-bound Boeing 787 that killed 241.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "aviation-safety",
        "status": "review",
        "is_editorial": False,
        "image_url": HERO_URL,
        "image_caption": "Air India Boeing 787-8 VT-ANB, the aircraft that operated Flight AI171, at London Heathrow.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "AI171 was a London-bound flight full of British-Indian and NRI passengers, and the diaspora flies the same Boeing 787 fleet weekly \u2014 so whether the crash is blamed on dead Indian pilots or a systemic Dreamliner flaw is a question with direct personal stakes.",
        "sources": [
            "Madhyamam / IANS \u2014 'Electric failure led to Air India Boeing crash in Ahmedabad: Pilots\u2019 body' (June 19, 2026)",
            "ANI \u2014 'Fuel switches moved without input, points to possible glitch: Federation of Indian Pilots Chief on AI171 crash report' (July 13, 2025)",
            "The Sun \u2014 'My wife died in the Air India crash\u2026 these questions need to be answered' (whistleblower electrical-failure evidence, June 2026)",
            "Wikipedia \u2014 'Air India Flight 171' (AAIB investigation timeline, EAFR recovery)",
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
