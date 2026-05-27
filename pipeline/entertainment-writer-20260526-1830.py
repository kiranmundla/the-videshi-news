#!/usr/bin/env python3
"""Entertainment writer — May 26 2026, 18:30 PDT batch:
1. FWICE issues Non-Cooperation Directive (ban) against Ranveer Singh over Don 3 exit — ₹45 crore pre-production losses, Farhan Akhtar complaint, Ranveer's silence statement.
2. Divyanka Tripathi & Vivek Dahiya welcome twin baby boys — "Mere Karan Arjun Aa Gaye!" — 10 years of marriage, 6 months secret pregnancy.
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
# ARTICLE 1: FWICE bans Ranveer Singh — Non-Cooperation Directive issued
# ─────────────────────────────────────────────────────────────────────
slug1 = "fwice-bans-ranveer-singh-non-cooperation-directive-don-3-farhan-akhtar-45-crore-20260526"
if not check_duplicate(slug1):
    art1_id = str(uuid.uuid4())
    articles.append(
        {
            "id": art1_id,
            "headline": "It's Official: FWICE Has Banned Ranveer Singh. The Non-Cooperation Directive Means No Producer, Director, or Crew in the Federation Can Work With Him Until He Shows Up and Explains Himself.",
            "subheadline": "The Federation of Western India Cine Employees issued the directive after Ranveer ignored three notices over two months. Farhan Akhtar and Ritesh Sidhwani told FWICE they spent ₹45 crore on Don 3 pre-production before Ranveer walked out three weeks before the shoot. Ranveer's team responded with a statement about 'dignity, maturity and mutual respect.' He has not appeared before the federation. The ban stands.",
            "slug": slug1,
            "category": "Entertainment",
            "vertical": "entertainment",
            "urgency": "standard",
            "status": "published",
            "published_at": now_iso,
            "score_total": 82,
            "tags": [
                "Ranveer Singh",
                "FWICE",
                "Don 3",
                "Farhan Akhtar",
                "Ritesh Sidhwani",
                "Excel Entertainment",
                "Bollywood",
                "Non-Cooperation Directive",
                "ban",
                "Shah Rukh Khan",
            ],
            "diaspora_angle": "The Don franchise is woven into NRI identity the way few Hindi film properties are. Shah Rukh Khan's Don (2006) was the film that NRI college students quoted in hostels from London to Toronto to the Bay Area. Don 2 was one of the first Bollywood films to open wide in German theaters. When Ranveer Singh was announced as the new Don, diaspora fans were divided but curious — the man who made Khilji iconic could plausibly make Don unpredictable. Now the franchise is in legal limbo, its star is banned by the industry's apex body, and ₹45 crore of pre-production money is being argued over in federation meetings that Ranveer has refused to attend. For NRIs who bought tickets to every Don screening at AMC and Cineplex, this is the slow-motion collapse of a franchise they assumed was invincible. The FWICE directive also matters because it reveals how Bollywood's informal power structures work — something diaspora audiences rarely see. The industry does not have binding contracts enforced by courts the way Hollywood does. It has federations, phone calls, and reputation. When FWICE bans you, no law forces producers to comply. But everyone does.",
            "sources": [
                {
                    "url": "https://www.livemint.com/entertainment/fwice-bans-ranveer-singh-amid-don-3-fallout-and-dispute-with-farhan-akhtar-11779722131684.html",
                    "name": "Mint",
                },
                {
                    "url": "https://www.mensxp.com/entertainment/bollywood/ranveer-singh-banned-by-filmmakers-amid-don-3-row-as-farhan-asks-for-rs-45-crore.html",
                    "name": "MensXP",
                },
                {
                    "url": "https://www.latestly.com/entertainment/bollywood/fwice-issues-non-cooperation-directive-ranveer-singh-don-3.html",
                    "name": "LatestLY",
                },
                {
                    "url": "https://www.bollywoodhungama.com/news/bollywood/ranveer-singh-team-reacts-fwice-ban-don-3-controversy/",
                    "name": "Bollywood Hungama",
                },
            ],
            "person_name": "Ranveer Singh",
            "image_search_query": "Ranveer Singh actor Bollywood",
            "word_count": 780,
            "body": """The Federation of Western India Cine Employees has done what it warned it would do. On Monday, FWICE issued a formal **Non-Cooperation Directive** against Ranveer Singh — the most consequential disciplinary action the federation can take against an actor, and one that effectively freezes him out of any production whose crew is affiliated with the organization.

That is most of Bollywood.

## What the directive means

A Non-Cooperation Directive is not a court order. It is not legally binding in the way a Hollywood studio's breach-of-contract lawsuit would be. But in an industry that runs on relationships, reputation, and the implicit understanding that federations protect workers, it functions as a ban in all but name.

No FWICE-affiliated crew member — and that includes cameramen, assistant directors, spot boys, makeup artists, light men, and virtually every below-the-line worker in Mumbai's film industry — is expected to work on a Ranveer Singh project while the directive is active. Producers who want to cast him would need to staff their entire crew outside the federation's membership. In practice, that is nearly impossible.

The directive remains in effect until Ranveer Singh appears before FWICE, presents his side of the story, and a "fair, balanced, and just resolution" is reached.

## How it got here

The sequence is straightforward, and FWICE has laid it out in clinical detail.

On **April 11, 2026**, filmmaker **Farhan Akhtar** filed a complaint with the Indian Film & Television Directors' Association (IFTDA), which referred it to FWICE. The complaint alleged that Ranveer Singh withdrew from **Don 3** — the next installment of the franchise Akhtar inherited from his father Javed Akhtar and Salim Khan — just **three weeks** before the crew was scheduled to depart for the shoot.

Farhan Akhtar and producer **Ritesh Sidhwani** told FWICE that Excel Entertainment had already spent approximately **₹45 crore** on pre-production. Locations had been locked. Crew had been hired. Schedules had been blocked. The sudden withdrawal, they argued, exposed them to "severe financial losses" and was "contrary to industry ethics."

FWICE then did what any federation would do: it sent notices to Ranveer Singh asking him to come in and explain.

Three notices. Three reminders. **April 22. April 30. May 13.**

No response.

When FWICE publicly announced that it would address the matter, Ranveer's team finally replied — but not in the way the federation wanted. His lawyers wrote that FWICE was "not the appropriate forum" and that the issues were "contractual in nature" requiring "adjudication before the appropriate legal forum."

FWICE took that as a rejection of its authority and issued the directive.

## The creative disagreement

The backstory that industry insiders have been discussing for months is less procedural and more personal.

Ranveer Singh reportedly wanted to take the Don character darker — a grittier, more aggressive interpretation that would distinguish his version from Shah Rukh Khan's suave, ironic take on the role. Farhan Akhtar's vision was to retain the franchise's established tone: stylish, playful, and commercially safe.

When the creative gap could not be bridged, Ranveer pushed for script revisions. When those revisions did not materialize to his satisfaction, he walked.

Reports also suggest that Ranveer agreed to return his **₹10 crore signing amount** to Excel Entertainment, but the production house is seeking the full ₹45 crore in pre-production costs. Neither side has confirmed the financial details on the record.

## Ranveer's response

Ranveer's official spokesperson released a statement that is a masterclass in saying nothing while sounding dignified:

*"Ranveer Singh holds the highest regard for the film fraternity and for everyone associated with the Don franchise. Throughout the recent developments surrounding Don 3, he has consciously chosen to maintain silence, believing that professional discussions and personal equations are best handled with dignity, maturity and mutual respect."*

The statement continued: *"His focus remains firmly on his work and the commitments ahead. He continues to hold deep respect and goodwill for all those involved and sincerely wishes the franchise continued success."*

Translation: he is not coming to the meeting.

## What happens next

FWICE Chief Advisor **Ashoke Pandit** has left the door open. The federation's statement explicitly says it "remains open to meeting with Mr. Ranveer Singh to hear his side." This is not a permanent exile — it is a pressure tactic designed to bring a star to the table.

The question is whether Ranveer blinks. He has **Dhurandhar** behind him, which was a blockbuster. He has brand endorsements that do not depend on FWICE membership. He has a Deepika Padukone-level social media following that insulates him from industry gossip.

But he also needs crews. He needs directors willing to work with an actor the federation has flagged. He needs producers who will absorb the reputational risk.

Previous FWICE actions against artists — **Diljit Dosanjh** and **Mika Singh** both faced similar directives in earlier years — were eventually resolved through negotiation. The pattern suggests this too will end with a meeting, possibly a financial settlement, and a quiet lifting of the directive.

Until then, Bollywood's most electric actor is officially persona non grata in his own industry.""",
        }
    )

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 2: Divyanka Tripathi & Vivek Dahiya welcome twin boys
# ─────────────────────────────────────────────────────────────────────
slug2 = "divyanka-tripathi-vivek-dahiya-twin-baby-boys-karan-arjun-ten-years-marriage-20260526"
if not check_duplicate(slug2):
    art2_id = str(uuid.uuid4())
    articles.append(
        {
            "id": art2_id,
            "headline": "Divyanka Tripathi and Vivek Dahiya Just Had Twin Boys. They Named the Announcement 'Mere Karan Arjun Aa Gaye.' If You Don't Get the Reference, You Didn't Grow Up in an Indian Household.",
            "subheadline": "The couple — married for nearly 10 years, together through Yeh Hai Mohabbatein, Nach Baliye, and Khatron Ke Khiladi — kept the pregnancy secret for six months. The twins arrived before their mid-June due date. The Instagram caption was peak NRI nostalgia: a Bollywood punchline that every Indian mother has used at least once.",
            "slug": slug2,
            "category": "Entertainment",
            "vertical": "entertainment",
            "urgency": "standard",
            "status": "published",
            "published_at": now_iso,
            "score_total": 72,
            "tags": [
                "Divyanka Tripathi",
                "Vivek Dahiya",
                "twins",
                "Indian television",
                "Yeh Hai Mohabbatein",
                "Karan Arjun",
                "parenthood",
                "NRI",
            ],
            "diaspora_angle": "Indian television stars occupy a peculiar space in the diaspora. They are not Bollywood. They do not walk red carpets at Cannes or headline IIFA in New Jersey. But in NRI living rooms — especially among first-generation immigrants and their parents — they are more famous than most film actors. Divyanka Tripathi is Ishita Bhalla from Yeh Hai Mohabbatein. That show aired on Star Plus and streamed on Hotstar in every Indian household in America, Canada, the UK, and the Gulf from 2013 to 2019. Aunties in Edison and Surrey and Hounslow know Divyanka's face the way they know their neighbor's. When she announces twin boys with a Karan Arjun reference — the 1995 Salman-SRK film about a mother whose sons return to avenge her — every NRI WhatsApp group lights up with the same message: 'Mere Karan Arjun aa gaye!' It is peak diaspora culture: a Bollywood quote repurposed as a birth announcement, shared on Instagram, screenshot-forwarded on WhatsApp, and understood instantly by anyone who grew up hearing their mother say it whenever two siblings walked into the room together.",
            "sources": [
                {
                    "url": "https://www.filmibeat.com/bollywood/news/divyanka-tripathi-twin-babies-name-2026-379729.html",
                    "name": "Filmibeat",
                },
                {
                    "url": "https://www.indulgexpress.com/entertainment/bollywood/divyanka-tripathi-vivek-dahiya-become-parents-twin-boys/article69636612.ece",
                    "name": "Indulge Express",
                },
                {
                    "url": "https://www.iwmbuzz.com/television/celebrity/divyanka-tripathi-vivek-dahiya-welcome-twin-boys-karan-arjun/",
                    "name": "IWMBuzz",
                },
                {
                    "url": "https://www.latestly.com/entertainment/tv/divyanka-tripathi-vivek-dahiya-twin-baby-boys.html",
                    "name": "LatestLY",
                },
            ],
            "person_name": "Divyanka Tripathi",
            "image_search_query": "Divyanka Tripathi actress",
            "word_count": 680,
            "body": """On May 26, 2026, Divyanka Tripathi posted an image on Instagram. Two tiny babies in blue outfits. A caption that required zero explanation for anyone who has ever been inside an Indian household:

**"Mere Karan Arjun aa gaye!"**

The line — from the 1995 Rakesh Roshan film in which Rakhee's character waits a lifetime for her two sons to return — has transcended its source material. It is no longer a movie dialogue. It is what every Indian mother says when her two sons walk into the room. It is what every NRI aunty texts in the family WhatsApp group when someone has twins. It is, in the most specific and untranslatable way possible, the only acceptable Indian birth announcement for twin boys.

Divyanka Tripathi and Vivek Dahiya knew this. Their announcement was not just news. It was a cultural callback so precise it could only have been written by people who grew up in it.

## Ten years

The couple married on July 8, 2016. Divyanka was at the peak of her television career — **Yeh Hai Mohabbatein** had made her one of the most recognizable faces on Indian television, and Vivek Dahiya had his own following from **Kavach** and later **Qayamat Ki Raat**.

For nearly a decade, they were one of Indian TV's most visible couples. They competed on **Nach Baliye 8** together. They did **Khatron Ke Khiladi** separately. They posted anniversary photos. They gave joint interviews. And through it all, the question that Indian media — and Indian aunties — kept asking was the question that Indian couples are always asked: *when are you having kids?*

Divyanka addressed it openly, saying in interviews that she and Vivek were focused on their careers and would start a family when the time was right.

The time, it turns out, was six months ago. They kept the pregnancy entirely secret.

## The secrecy

In an industry where pregnancy announcements are managed by publicists, released through exclusive interviews with Filmfare or Bombay Times, and accompanied by professionally shot maternity photoshoots, Divyanka and Vivek did the opposite.

They told no one. For six months.

No baby shower photos on Instagram. No maternity fashion posts. No "source close to the couple" leaking the news to entertainment reporters. In a media ecosystem that tracks celebrity pregnancies with the intensity of a stock ticker, the Dahiyas managed to keep their twins entirely private until the boys had already arrived.

The babies came before their mid-June due date. Both mother and babies are healthy. The names have not been revealed — though the internet has already decided that "Karan" and "Arjun" would be the only acceptable choice given the announcement caption.

## Why this matters more than it should

Divyanka Tripathi is not a Bollywood star. She has never headlined a theatrical film. She has never been to Cannes. Her name does not appear in the same headlines as Alia Bhatt or Deepika Padukone.

But in the ecosystem that actually reaches Indian households — daytime and primetime television on Star Plus, Colors, and Zee TV — she is royalty. **Yeh Hai Mohabbatein** ran for six years and 1,887 episodes. It was the show that NRI grandmothers watched on Hotstar while their grandchildren did homework. It was the show that played in living rooms in Fremont and Brampton and Wembley, a daily constant that Bollywood films could never be.

When Divyanka announces twin boys, the reaction is not the polished admiration that greets a Bollywood pregnancy announcement. It is personal. The comments on her Instagram are not from fans. They are from people who feel like they watched her grow up.

## The Karan Arjun of it all

The genius of the announcement is its specificity. "Mere Karan Arjun aa gaye" is not a generic Bollywood reference. It is a generational shibboleth. If you understand it instantly — if you hear Rakhee's voice in your head when you read it — you are from a specific time, a specific culture, a specific living room where that film played on a VCR or a pirated DVD or a Sunday afternoon Doordarshan slot.

Divyanka and Vivek did not explain the reference. They did not need to. Their audience — the aunties, the NRI parents, the people who grew up on Star Plus — already knew.

Congratulations to the Dahiyas. And to Karan and Arjun, whatever their real names turn out to be.""",
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
