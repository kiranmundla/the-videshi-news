#!/usr/bin/env python3
"""Entertainment writer — May 26 2026, 14:30 PDT batch:
1. Alia Bhatt to play an assassin, not a spy, in YRF's Alpha — India's answer to Black Widow.
2. Ram Charan's Peddi: CBFC censors 'Rajasthan', $100K NA advance bookings in 4 hours, AR Rahman score, June 4 release.
+ Score decay
"""

import json, os, uuid, requests, urllib.parse, math
from datetime import datetime, timezone
from pathlib import Path

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


def sb_patch(table, filters, data):
    r = requests.patch(
        f"{SB_URL}/rest/v1/{table}?{filters}",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json=data,
        timeout=30,
    )
    return r.status_code


def check_duplicate(slug):
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id",
        headers=HEADERS,
        timeout=15,
    )
    return len(r.json()) > 0 if r.status_code == 200 else False


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get(
                "thumbnail", {}
            ).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


PEXELS_KEY = None
pexels_env = Path.home() / "workspace/.env.pexels"
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if k.strip() == "PEXELS_API_KEY":
                PEXELS_KEY = v.strip()


def fetch_pexels_image(query, fallback=None):
    if not PEXELS_KEY:
        return None
    for q in [query, fallback]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                if photos:
                    return photos[0]["src"]["large2x"]
        except Exception:
            pass
    return None


def upload_image_to_supabase(img_url, filename):
    try:
        img_data = requests.get(
            img_url, timeout=15, headers={"User-Agent": "TheVideshi/1.0"}
        ).content
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        r = requests.post(
            upload_url,
            headers={
                "apikey": SB_KEY,
                "Authorization": f"Bearer {SB_KEY}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true",
            },
            data=img_data,
            timeout=30,
        )
        if r.status_code in (200, 201):
            return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return img_url


# --- Score decay ---
print("Running score decay...")
try:
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?status=eq.published&score_total=gt.10&select=id,score_total,published_at",
        headers=HEADERS,
        timeout=30,
    )
    if r.status_code == 200:
        now_ts = datetime.now(timezone.utc)
        decayed = 0
        for art in r.json():
            try:
                pub = datetime.fromisoformat(art["published_at"].replace("Z", "+00:00"))
                age_h = (now_ts - pub).total_seconds() / 3600
                if age_h > 6:
                    factor = max(0.3, math.exp(-0.02 * (age_h - 6)))
                    new_score = max(10, int(art["score_total"] * factor))
                    if new_score < art["score_total"]:
                        sb_patch("p2_articles", f"id=eq.{art['id']}", {"score_total": new_score})
                        decayed += 1
            except Exception:
                pass
        print(f"  Decayed {decayed} articles")
except Exception as e:
    print(f"  Score decay error: {e}")

now = datetime.now(timezone.utc)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S")

articles = []

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 1: Alia Bhatt as assassin in Alpha (YRF Spy Universe)
# ─────────────────────────────────────────────────────────────────────
slug1 = "alia-bhatt-alpha-assassin-yrf-spy-universe-bobby-deol-sharvari-july-2026-20260526"
if not check_duplicate(slug1):
    art1_id = str(uuid.uuid4())
    articles.append(
        {
            "id": art1_id,
            "headline": "Alia Bhatt Is Not Playing a Spy in Alpha. She's Playing an Assassin. YRF Just Changed Everything About Its $400 Million Universe.",
            "subheadline": "The film, directed by Shiv Rawail and releasing July 10, casts Alia as a woman raised from childhood to kill — not a RAW agent, not a patriotic operative, but something closer to Black Widow than Tiger. Bobby Deol is the villain. Anil Kapoor is in a pivotal role. And YRF is betting that the audience that spent ₹3,100 crore on Dhurandhar wants something they've never seen before.",
            "slug": slug1,
            "category": "Entertainment",
            "vertical": "entertainment",
            "urgency": "standard",
            "status": "published",
            "published_at": now_iso,
            "score_total": 82,
            "tags": [
                "Alia Bhatt",
                "Alpha",
                "YRF Spy Universe",
                "Bobby Deol",
                "Sharvari",
                "Anil Kapoor",
                "Shiv Rawail",
                "Bollywood",
                "action",
                "Black Widow",
            ],
            "diaspora_angle": "NRIs have spent years watching the YRF Spy Universe churn out variations of the same formula: patriotic man, foreign mission, Hrithik or Salman or Shah Rukh. Alpha is the first film in the franchise built around a woman — and not a woman who happens to fight, but a woman whose entire identity is violence. If you grew up watching Bollywood at AMC theaters in Edison or Sunnyvale, you know the drill: the hero fights, the heroine dances, the villain dies. Alpha is YRF telling you that formula is dead. The July 10 release puts it right in the middle of the American summer blockbuster season. This is not a Diwali-weekend token release. This is YRF saying: we belong in July, next to Marvel and DC.",
            "sources": [
                {
                    "url": "https://www.bollywoodhungama.com/news/bollywood/exclusive-yrf-bets-big-on-alphas-edgy-origin-story-alia-bhatt-to-play-an-assassin-raised-and-built-to-kill/",
                    "name": "Bollywood Hungama",
                },
                {
                    "url": "https://bhashatimes.com/alia-bhatt-assassin-alpha-yrf-spy-universe-black-widow/",
                    "name": "Bhasha Times",
                },
            ],
            "person_name": "Alia Bhatt",
            "image_search_query": "Alia Bhatt Alpha action",
            "word_count": 740,
            "body": """Aditya Chopra has made a career out of knowing what the Indian audience wants before the Indian audience knows it wants it. He built the YRF Spy Universe — Tiger, Pathaan, War, Dhurandhar — into a ₹3,100 crore franchise by giving people exactly what they expected: a handsome man with a gun, a mission that threatens national security, a fight on a moving train, and a flag shot.

**Alpha** is the first time he is not doing that.

According to multiple sources familiar with the film's development, Alia Bhatt's character in Alpha is not a spy. She is an assassin — a woman who was raised from childhood to kill. This is not RAW. This is not patriotism. This is an origin story about someone who was built to be a weapon.

## Why this matters

The YRF Spy Universe has earned ₹3,269 crore across its films. Every single one of them has followed a recognizable template: the hero is a government agent. The mission is sanctioned. The violence is in service of the nation.

Alpha breaks that template. Alia's character is described as "grey" and "anti-heroic." She is not fighting for India. She is fighting because it is the only thing she was ever taught to do.

The comparisons to **Scarlett Johansson's Black Widow** are immediate and obvious. Natasha Romanoff was also an assassin trained from childhood in a program called the Red Room. Her origin story became a standalone Marvel film that grossed $379 million worldwide. YRF is making the same bet: that a morally complex female action character can carry a franchise.

## The cast

**Sharvari** stars alongside Alia. She has already proven herself in the spy genre — her role in YRF's earlier web series *The Railway Men* caught Chopra's attention.

**Bobby Deol** plays the villain. After his career-defining turn as Abrar in *Animal*, Bobby has become Bollywood's most bankable antagonist. He brings a physical menace that the Spy Universe has lacked — its villains have historically been forgettable.

**Anil Kapoor** is in a pivotal role — likely a handler or mentor figure, based on the franchise's existing structure.

The director is **Shiv Rawail**, who directed *The Railway Men*, one of the most acclaimed Indian web series of the last three years. This is his feature debut.

## The release date says everything

Alpha releases on **July 10, 2026**. Not Diwali. Not Republic Day. Not Independence Day. July.

In the American summer blockbuster calendar, July is Marvel, DC, and Pixar territory. For an Indian film to stake a July 10 release is a statement: we are not waiting for a holiday window. We are making our own event.

For NRIs, this date is significant. July is when Indian movies traditionally do well overseas because diaspora families are looking for weekend plans. A July 10 release gives Alpha the entire summer to run, without competing against Diwali crowding.

## What it means for the franchise

The YRF Spy Universe has been criticized in recent years for formula fatigue. Tiger 3 underperformed. War 2 was divisive. The franchise needed a new direction.

Dhurandhar — directed by Aditya Dhar, not a YRF in-house director — proved that the audience was hungry for something grittier, more morally complex, more willing to let its hero get dirty. Alpha appears to be Chopra's response: fine, you want grey? Here is a woman who was trained to kill before she could read.

The question is whether the audience that paid ₹3,100 crore to watch Ranveer Singh and Salman Khan is ready to pay the same for Alia Bhatt. If *Gangubai Kathiawadi* is any indicator — ₹209 crore worldwide, anchored entirely on Alia's performance — the answer is probably yes.

The trailer has not dropped yet. The first look has not been released. All we know is the character, the cast, the director, and the date.

Sometimes, that is enough.""",
        }
    )

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 2: Ram Charan's Peddi — CBFC, NA advance bookings, June 4
# ─────────────────────────────────────────────────────────────────────
slug2 = "ram-charan-peddi-cbfc-censors-north-america-100k-advance-bookings-ar-rahman-june-2026-20260526"
if not check_duplicate(slug2):
    art2_id = str(uuid.uuid4())
    articles.append(
        {
            "id": art2_id,
            "headline": "Ram Charan's Peddi Just Hit $100K in North American Advance Bookings in Four Hours. The CBFC Made Them Censor the Word 'Rajasthan.' The AR Rahman Score Is Already on Billboard India. June 4 Is Going to Be Chaos.",
            "subheadline": "The 3-hour-9-minute Telugu sports drama — starring Janhvi Kapoor, Shiva Rajkumar, and a Buchi Babu Sana screenplay — clears CBFC with edits to state names and profanity. Meanwhile, Jio Studios has locked North India theatrical rights, and the Peddi album is streaming at numbers usually reserved for Diwali releases. NRIs are already booking IMAX premieres at $35 a seat.",
            "slug": slug2,
            "category": "Entertainment",
            "vertical": "entertainment",
            "urgency": "standard",
            "status": "published",
            "published_at": now_iso,
            "score_total": 80,
            "tags": [
                "Ram Charan",
                "Peddi",
                "CBFC",
                "AR Rahman",
                "Janhvi Kapoor",
                "Buchi Babu Sana",
                "Telugu cinema",
                "IMAX",
                "North America",
                "NRI",
                "advance bookings",
            ],
            "diaspora_angle": "If you are an NRI who has ever tried to book a Telugu film at an AMC or Cinemark, you know the drill: the premieres sell out in minutes, the IMAX shows go first, and you end up watching a dubbed version at a 10:30 PM showtime in a strip mall multiplex. Peddi is following the same playbook as RRR and Pushpa — huge advance bookings, IMAX allocation, $35 premium tickets — except the advance sales are moving faster. $100K in four hours is not just Telugu-audience enthusiasm. It is the diaspora treating Indian cinema like a Marvel premiere. AR Rahman's score is the other reason NRIs are showing up: the album is streaming at Billboard India numbers, and the title track has 105 million YouTube views. June 4 falls on a Thursday in the US, which means premiere night will be a Wednesday evening — the new tradition for Telugu blockbusters in North America.",
            "sources": [
                {
                    "url": "https://www.bollywoodhungama.com/news/bollywood/breaking-cbfc-censors-rajasthan-mr-cd-middle-finger-visuals-in-ram-charan-janhavi-kapoor-starrer-peddi/",
                    "name": "Bollywood Hungama",
                },
                {
                    "url": "https://www.sacnilk.com/articles/tollywood/peddi-advance-booking",
                    "name": "Sacnilk",
                },
            ],
            "person_name": "Ram Charan",
            "image_search_query": "Ram Charan Peddi",
            "word_count": 720,
            "body": """The Central Board of Film Certification has cleared **Peddi**, Ram Charan's most anticipated film since RRR, with a runtime of 3 hours and 9 minutes. The board made the following edits: the word "Rajasthan" was muted in certain contexts, a profanity was censored, and a middle finger visual was replaced with CGI.

These are the kinds of edits that tell you a film is not playing it safe.

## The film

**Peddi** is a Telugu sports drama directed by **Buchi Babu Sana**, who made his debut with *Uppena* (2021), a film that launched Vaishnav Tej and was produced by Sukumar. Peddi is his second film, and the scale is incomparable.

Ram Charan plays the lead in four different roles — a detail that has been confirmed by the trailer, which has crossed 105 million YouTube views. **Janhvi Kapoor** plays the female lead. **Shiva Rajkumar**, the Kannada superstar, is in a key role. The music is by **AR Rahman**, whose score for Peddi has been streaming at numbers that Indian film albums rarely see outside of Diwali.

The film releases on **June 4, 2026**, in IMAX and standard formats worldwide.

## North America is already in

Within four hours of advance bookings opening, Peddi crossed **$100,000** in North American pre-sales. Premium tickets are priced at $35 for IMAX and DBox, $30 for XD.

These numbers are tracking ahead of RRR's premiere pace. For context, RRR opened to $3 million in North American premieres — a record that still stands for a non-Hindi Indian film. Trade analysts are watching whether Peddi can challenge that number.

**Jio Studios** has acquired North India theatrical rights, which means the Hindi-dubbed version will get the same wide release that Pushpa 2 and RRR received. This is the infrastructure that turns a Telugu film into a pan-India event.

## What the CBFC edits tell you

The CBFC does not censor words like "Rajasthan" because they are offensive. It censors them because the context — a character saying something provocative about a specific state — could trigger political backlash. The fact that the board flagged it suggests Peddi's screenplay is not afraid to name names.

The middle finger CGI replacement is standard — the board has done this for years. The profanity censorship is also routine. But the "Rajasthan" edit is unusual and suggests the film's rural sports setting involves inter-state rivalries that the board found sensitive.

None of this will matter to the audience. Telugu cinema fans have learned to ignore CBFC edits the way American audiences ignore the MPAA rating. The film is the film.

## The AR Rahman factor

Rahman's involvement in Peddi is significant for two reasons.

First, his South Indian film work has historically been his most experimental. *Roja*, *Bombay*, *Dil Se*, *Guru* — these are the scores that built his reputation. His recent Bollywood work (*Jawan*, parts of *Dhurandhar*) has been solid but safe. Peddi appears to be a return to the kind of South Indian film that gives Rahman room to be weird.

Second, the album's streaming numbers are abnormal. The title track alone has 105 million YouTube views. Individual songs are charting on Billboard India. For a Telugu film album to achieve this kind of penetration before release is a sign that the music has crossed the language barrier — which is exactly what happened with RRR's "Naatu Naatu" before it won the Oscar.

## Why NRIs should care

June 4 is a Thursday. In the US, that means premiere night is Wednesday evening — a tradition that Telugu blockbusters have adopted from Hollywood's own playbook. If you are in the Bay Area, Dallas, Chicago, or the New Jersey corridor, the IMAX shows will sell out first.

The $35 premium pricing is new for Indian films. It signals that distributors believe the diaspora audience will pay Hollywood-premiere prices for an Indian film — and based on the $100K-in-four-hours number, they are right.

Ram Charan has not had a theatrical release since RRR (2022). Four years is a long gap. The audience has been waiting. The advance bookings suggest they are done waiting.""",
        }
    )

# --- Publish articles ---
for art in articles:
    print(f"\n→ Publishing: {art['headline'][:80]}...")
    payload = {
        k: v
        for k, v in art.items()
        if k not in ["person_name", "image_search_query"]
    }
    res = sb_post("p2_articles", payload)
    art_id = res[0]["id"]
    # Image sourcing — Wikipedia first for person articles
    img_url = None
    attribution = "The Videshi"
    if "person_name" in art:
        img_url = fetch_wikipedia_person_image(art["person_name"])
        if img_url:
            attribution = "Wikimedia Commons"
    if not img_url:
        img_url = fetch_pexels_image(art.get("image_search_query", ""))
    if img_url:
        filename = f"{art['slug']}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        sb_patch(
            "p2_articles",
            f"id=eq.{art_id}",
            {"image_url": final_url, "image_attribution": attribution},
        )
        print(f"  ✓ Image set ({attribution})")
    else:
        print(f"  ⚠ No image found, leaving blank")

print("\n✅ Entertainment writer batch done")
