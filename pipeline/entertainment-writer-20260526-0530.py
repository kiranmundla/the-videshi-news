#!/usr/bin/env python3
"""Entertainment writer — May 26 2026, 05:30 UTC batch (22:30 PDT May 25):
1. Mammootty skipped his own Padma Bhushan ceremony to receive a third honorary
   doctorate in Kerala — rootedness over national ceremony
2. David Dhawan cried at his own trailer launch — Hai Jawani Toh Ishq Hona Hai,
   father-son Bollywood dynasty, Biwi No. 1 song rights dispute
+ Score decay for older entertainment articles
"""

import json, os, uuid, requests, urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Supabase config ──
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
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{filters}", headers={**HEADERS, "Prefer": "return=minimal"}, json=data, timeout=30)
    return r.status_code

def sb_get(table, filters, select="*"):
    r = requests.get(f"{SB_URL}/rest/v1/{table}?{filters}&select={select}", headers=HEADERS, timeout=15)
    return r.json() if r.status_code == 200 else []

def check_duplicate(slug):
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id",
        headers=HEADERS, timeout=15
    )
    return len(r.json()) > 0 if r.status_code == 200 else False


# ── Wikipedia person image (MANDATORY per IMAGE-SOURCING-RULES.md) ──
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


# ── Pexels fallback ──
PEXELS_KEY = None
pexels_env = Path.home() / "workspace/.env.pexels"
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if k.strip() == "PEXELS_API_KEY":
                PEXELS_KEY = v.strip()

def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": q, "per_page": 5, "orientation": "landscape"},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                return photos[0]["src"]["large2x"]
    return None


# ── Supabase image upload ──
def upload_image_to_supabase(img_url, filename):
    """Download image and upload to Supabase article-images bucket."""
    try:
        img_data = requests.get(img_url, timeout=15,
                                headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}).content
        content_type = "image/jpeg"
        if img_url.lower().endswith(".png"):
            content_type = "image/png"
        elif img_url.lower().endswith(".svg"):
            content_type = "image/svg+xml"

        upload_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        r = requests.post(upload_url, headers=upload_headers, data=img_data, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded {filename}")
            return public_url
        else:
            print(f"  ⚠ Upload failed HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


now = datetime.now(timezone.utc)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S")
articles = []


# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Mammootty — Skipped Padma Bhushan Ceremony,
# Chose Kerala Doctorate Instead
# ══════════════════════════════════════════════════════════════
slug1 = "mammootty-skipped-padma-bhushan-ceremony-third-honorary-doctorate-mahatma-gandhi-university-kerala-20260525"
if not check_duplicate(slug1):
    art1_id = str(uuid.uuid4())
    articles.append({
        "id": art1_id,
        "headline": "Mammootty Was Supposed to Receive India's Third-Highest Civilian Honour Today. He Was in Kottayam Instead, Accepting His Third Doctorate from a Kerala University.",
        "subheadline": "On the same day President Droupadi Murmu conferred 66 Padma Awards at Rashtrapati Bhavan — including his own Padma Bhushan — Mammootty was at Mahatma Gandhi University's convocation, receiving an honorary D.Litt. from the Governor of Kerala. He posted 'humbled' on social media. He did not explain why he was not in Delhi. He did not need to.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 76,
        "tags": ["Mammootty", "Padma Bhushan", "Padma Awards 2026", "Mahatma Gandhi University", "Kerala", "Malayalam cinema", "Kottayam", "honorary doctorate", "D.Litt", "Rajendra Arlekar", "Indian cinema", "diaspora", "NRI"],
        "diaspora_angle": "For the Indian diaspora, Mammootty's decision carries a weight that does not translate easily to non-Indians. The Padma Awards are not just national honours — they are social currency. For NRIs who explain Indian cinema to their Western friends, the phrase 'he has a Padma Bhushan' is a shortcut that eliminates the need for further justification. That Mammootty chose a convocation hall in Kottayam over the ballroom at Rashtrapati Bhavan is the kind of quiet statement that resonates across Malayali communities in the Gulf, in the United States, in Canada, and in the United Kingdom. It says: I know where I come from. For Malayali NRIs in particular — the largest non-resident community from any Indian state relative to the state's population — Mammootty's rootedness is not a quaint character trait. It is a mirror. Every Malayali abroad who has turned down a promotion in another city because their parents live in Kottayam or Thrissur or Ernakulam understands the logic. The national stage will always be there. The university where your people taught will not always have a convocation to invite you to.",
        "sources": [
            {"url": "https://www.cinemaexpress.com/malayalam/news/2026/May/25/mammootty-receives-honorary-doctorate-from-mahatma-gandhi-university-says-humbled-in-emotional-note", "name": "Cinema Express"},
            {"url": "https://www.latestly.com/entertainment/padma-awards-2026-hema-malini-mammootty-alka-yagnik", "name": "LatestLY"},
            {"url": "https://www.newspointapp.com/mammootty-third-doctorate-padma-bhushan-ceremony", "name": "NewsPoint"},
            {"url": "https://www.zoomtventertainment.com/mammootty-third-doctorate", "name": "Zoom TV"}
        ],
        "image_search_query": "Mammootty actor",
        "image_entities": ["Mammootty"],
        "image_must_show": "Mammootty, the Malayalam cinema actor",
        "word_count": 780,
        "body": """On May 25, 2026, President **Droupadi Murmu** conferred 66 Padma Awards at the first Civil Investiture Ceremony of the year at **Rashtrapati Bhavan** in New Delhi. Among the recipients was **Mammootty** — born Muhammad Kutty Ismail Panaparambil, now 74 — who was announced as a **Padma Bhushan** awardee for his contribution to Indian cinema. It is India's third-highest civilian honour.

Mammootty was not in Delhi to receive it.

He was in **Kottayam**, at the convocation ceremony of **Mahatma Gandhi University**, accepting an honorary **Doctor of Letters (D.Litt.)** from **Rajendra Arlekar**, the Governor of Kerala.

## The Third Doctorate

This was Mammootty's third honorary doctorate. The first came from the **University of Calicut** in 2010. The second from the **University of Kerala**, also in 2010. Now, fifteen years later, Mahatma Gandhi University added its name to the list, recognising what the citation described as his "remarkable contribution to Indian cinema over a career spanning more than five decades."

The ceremony was attended by senior university officials, members of the academic council, and Kerala's Higher Education Minister **Roji M. John**. Alongside Mammootty, noted nadaswaram artiste **Thiruvizha Jayashankar** received an honorary D.Litt., while vascular surgeon **N. Radhakrishnan** received a Doctor of Science.

After the ceremony, Mammootty posted a single message on social media: "Humbled to have received the Honorary D.Litt. from Mahatma Gandhi University today, presented by the Honourable Governor of Kerala. My gratitude to each and every one of you who stood by my side throughout this memorable journey."

He did not mention the Padma Bhushan. He did not explain his absence from Delhi. There was no statement about scheduling conflicts or regret about missing the ceremony. The silence was the statement.

## The Delhi Ceremony He Missed

At Rashtrapati Bhavan, the Padma Awards ceremony proceeded without him. **Hema Malini** accepted the posthumous **Padma Vibhushan** on behalf of her late husband **Dharmendra**. **Alka Yagnik** received her Padma Bhushan — the singer who has been unable to perform since 2024 due to a rare hearing condition. **R. Madhavan**, **Satish Shah** (posthumously), and others were honoured across the ceremony's two Padma Bhushan and 58 Padma Shri presentations.

Mammootty's award will be presented at a subsequent ceremony. The Padma protocol allows for this. But the optics — one of India's most celebrated actors choosing a university in his home state over the Presidential palace on the same day — carry their own meaning.

## The Career That Made Both Honours Inevitable

Mammootty has appeared in more than **400 films** across five languages: **Malayalam, Tamil, Telugu, Kannada, and Hindi**. He has won **three National Film Awards for Best Actor** — for *Mathilukal* (1990), *Ponthan Mada* (1994), and *Dr. Babasaheb Ambedkar* (2000). He has won **14 Kerala State Film Awards**. He received the Padma Shri in 1998.

His filmography since 2020 alone would constitute a complete career for most actors. *Bheeshma Parvam* (2022), *Rorschach* (2022), *Kaathal: The Core* (2023) — in which he played a closeted gay municipal chairman, a role that no actor of his generation and stature in Indian cinema had previously taken — and *Bramayugam* (2024), a black-and-white period horror film that became one of the most critically acclaimed Malayalam films of the decade.

Most recently, he appeared in Mahesh Narayanan's spy thriller ***Patriot***, alongside **Mohanlal**, **Fahadh Faasil**, **Kunchacko Boban**, and **Nayanthara**. His upcoming slate includes **Adoor Gopalakrishnan's *Padayaatra***, **Khalid Rahman's *Mattancherry Mafia*** (co-starring Naslen and Asif Ali), a film with *Falimy* director **Nithish Sahadev**, and a return to Tamil cinema with **Rajkumar Periasamy** — the director of *Amaran* — in a film led by **Dhanush**.

## Why He Was in Kottayam

There is no official explanation for why Mammootty chose the university ceremony over the Padma ceremony. None is needed for anyone who has followed his career.

Mammootty has lived in Kochi for the entirety of his career. He has never relocated to Mumbai, despite the fact that doing so would have given him earlier access to Hindi cinema's commercial machinery. He has never publicly expressed regret about this decision. His production house, **Mammootty Kampany**, operates out of Kerala. His charitable work — including his decade-long association with the **Pain and Palliative Care Society** — is rooted in the state.

In Kottayam, Mammootty was not accepting a lesser honour. He was accepting a **local** honour, from a university in his home state, conferred by the governor who lives in the same state, attended by the education minister who governs the same state. Every person in that convocation hall knew exactly who he was. Not because of a Wikipedia page or a Padma citation, but because they had watched his films in theatres that were a short drive from that hall.

The Padma Bhushan recognises a career. A university doctorate in Kottayam recognises where that career began and where it remains anchored. Mammootty, characteristically, chose the anchor.

## The Quiet Lesson

For an industry that increasingly measures itself in pan-India grosses and overseas box-office numbers, Mammootty's absence from Delhi is a reminder that the most significant choices in a career are sometimes the ones you make about where to be, not what to accept. He will receive his Padma Bhushan at a later date, in a quieter ceremony, with less media coverage.

He will probably post "humbled" again.""",
    })
    print(f"✅ Article 1 prepared: {slug1}")
else:
    print(f"⚠️ DUPLICATE: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: David Dhawan Cried at His Own Trailer Launch —
# The Father-Son Story Behind Hai Jawani Toh Ishq Hona Hai
# ══════════════════════════════════════════════════════════════
slug2 = "david-dhawan-varun-dhawan-hai-jawani-toh-ishq-hona-hai-trailer-tears-biwi-no-1-song-rights-june-5-20260525"
if not check_duplicate(slug2):
    art2_id = str(uuid.uuid4())
    articles.append({
        "id": art2_id,
        "headline": "David Dhawan Cried at His Own Trailer Launch. Varun Sang a Song to Lighten the Mood. Then Asked the Producer If They Had the Rights to That Song.",
        "subheadline": "The trailer for Hai Jawani Toh Ishq Hona Hai — the fourth Varun-David Dhawan collaboration, releasing June 5 — dropped days after a legal dispute forced the cancellation of its original launch event. The film recreates 'Chunari Chunari' and the title track from Biwi No. 1 (1999). The original producer says nobody asked his permission. The current producer says everything is 'sorted.' The original producer says nobody has called him.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 72,
        "tags": ["David Dhawan", "Varun Dhawan", "Hai Jawani Toh Ishq Hona Hai", "Mrunal Thakur", "Pooja Hegde", "Biwi No 1", "Vashu Bhagnani", "Ramesh Taurani", "Tips Industries", "Chunari Chunari", "Bollywood comedy", "song rights", "copyright", "father son", "diaspora", "NRI"],
        "diaspora_angle": "For NRIs, David Dhawan is not a director. He is a Saturday afternoon. He is the stack of pirated VCDs your uncle brought from Lamington Road. He is Govinda in a yellow shirt doing something that made no sense but made everyone in the room laugh. Coolie No. 1, Hero No. 1, Biwi No. 1, Haseena Maan Jaayegi — these are not films for the diaspora. They are the definition of Bollywood that the diaspora carried abroad in the 1990s and 2000s, before Bollywood became self-conscious about being 'world cinema.' That David Dhawan, now in his seventies, is still making these films with his own son — and crying at the trailer launch because his son takes care of him in the hospital — is the kind of immigrant-family emotional frequency that every NRI recognises. The joke about song rights is funnier when you know that the songs being disputed are from Biwi No. 1, a film that every Indian family abroad has watched at least twice. The legal drama is Bollywood. The tears are home.",
        "sources": [
            {"url": "https://www.bollywoodhungama.com/news/bollywood/hai-jawani-toh-ishq-hona-hai-trailer-launchs-most-emotional-moment-david-dhawan-gets-teary-eyed/", "name": "Bollywood Hungama"},
            {"url": "https://www.thedailyjagran.com/entertainment/news/hai-jawani-toh-ishq-hona-hai-trailer-varun-dhawan-10313372", "name": "The Daily Jagran"},
            {"url": "https://www.filmfare.com/news/bollywood/hai-jawani-toh-ishq-hona-hai-trailer-varun-dhawan", "name": "Filmfare"},
            {"url": "https://www.bollywoodhungama.com/news/bollywood/vashu-bhagnani-hai-jawani-toh-ishq-hona-hai/", "name": "Bollywood Hungama (Bhagnani)"}
        ],
        "image_search_query": "David Dhawan director",
        "image_entities": ["David Dhawan", "Varun Dhawan"],
        "image_must_show": "David Dhawan, Bollywood director",
        "word_count": 800,
        "body": """On May 23, 2026, at a trailer launch in Mumbai for the film **Hai Jawani Toh Ishq Hona Hai**, the 73-year-old director **David Dhawan** began talking about his son. He had been talking about the film — about the comedy, about the music, about the return to the kind of full-throttle entertainer that had made him one of the most commercially successful directors in Bollywood history. But then someone asked about Varun, and David Dhawan's voice changed.

"He has been a great son," David said. "He has always looked after me and my health. For everything and anything, he's always there standing by me. Even in the hospital, he used to sleep there with me. What more do you want?"

Then he said: **"As a father, I feel that everybody should have a son like him."**

David Dhawan's eyes filled with tears. The room went quiet. **Varun Dhawan**, standing beside him, tried to break the tension by joking: "Like me and Rohit." It worked. David smiled and said, "Yeah. My other son, too. Both of them." Varun leaned over and kissed his father on the cheek.

A journalist said David Dhawan should not retire. David did not deny the speculation. He said: *"Aap apni health mujhe de do."* Give me your health.

## The Film

**Hai Jawani Toh Ishq Hona Hai** is the fourth collaboration between David and Varun Dhawan, following *Main Tera Hero* (2014), *Judwaa 2* (2017), and *Coolie No. 1* (2020). It stars **Varun Dhawan**, **Mrunal Thakur**, and **Pooja Hegde**, with supporting roles from **Maniesh Paul**, **Chunky Panday**, **Rakesh Bedi**, **Jimmy Shergill**, **Mouni Roy**, **Rajesh Kumar**, and **Ali Asgar**. The screenplay is by **Rumy Jafry**. The cinematographer is **Ayananka Bose**.

The three-minute trailer opens in a courtroom, where Varun and Mrunal's characters are seeking a divorce. The reason: she complains that he only wants romance. He explains that he simply wants to become a father. After their separation, Varun's character meets Pooja Hegde's character at a nightclub, claims he is single, and falls for her. The twist: both women reveal they are pregnant with his child at the same time.

The rest of the trailer follows the lead character's panicked double life — hiding handbags, inventing alibis, running between two households — in a style that reviewers immediately compared to David Dhawan's own *Biwi No. 1* (1999) and Priyadarshan's *Garam Masala* (2005).

The film takes its title from a song in *Biwi No. 1* and features recreated versions of **"Chunari Chunari"** and **"Ishq Sona Hai"** from that 1999 soundtrack.

It releases in theatres on **June 5, 2026**.

## The Songs That Started a War

The problem is that the songs from *Biwi No. 1* were produced by **Vashu Bhagnani** under his banner **Pooja Entertainment**. The music rights were later acquired by **Tips Industries**, owned by **Ramesh Taurani**. When the makers of *Hai Jawani Toh Ishq Hona Hai* decided to recreate the tracks, Bhagnani objected.

On May 22 — the day before the trailer launch — Bhagnani held a virtual press conference from **Dubai** with selected media. His claim: the songs and, potentially, the story of the new film constitute his intellectual property. He stated that the makers had initially approached him about producing *Biwi No. 1 Part 2*, asked him to hold the song rights, and then proceeded to make a different film using the same songs.

"If *Hai Jawani Toh Ishq Hona Hai* hasn't used scenes and songs from *Biwi No. 1*, I'll apologise and back off," Bhagnani said. He estimated his IP value at **₹10 crore** or more. He said the matter could be "settled in 15 minutes" if anyone called him.

At the rescheduled trailer launch on May 23, **Ramesh Taurani** addressed the dispute: "There's no problem. We are handling it."

Varun Dhawan then picked up a microphone, sang a few lines of **"Jeena Laga Hoon"** — another Tips-owned track — and turned to Taurani: **"Ramesh ji, iss gaane ke rights hai na?"** The room laughed.

Hours later, Bhagnani posted a video response: "No one has called me yet." He described Taurani's claim that the matter was "sorted" as misleading, and warned that using or distributing the disputed content could constitute **contempt of court**.

## The Dynasty Effect

The David-Varun dynamic is one of Bollywood's most visible father-son collaborations. But it is also one of the industry's most scrutinised.

David Dhawan directed **45 films** between 1992 and 2014, creating an entire genre of Hindi comedy built around physical gags, mistaken identities, romantic chaos, and wall-to-wall songs. His collaborations with **Govinda** — *Coolie No. 1*, *Hero No. 1*, *Partner*, *Bade Miyan Chote Miyan* — defined Bollywood comedy for a generation. When Govinda's commercial viability declined, David Dhawan's output slowed. When Varun debuted in 2014, the dynasty became the revival strategy.

*Main Tera Hero* earned ₹63 crore. *Judwaa 2* earned ₹138 crore. *Coolie No. 1* released during the pandemic on Amazon Prime to mixed reviews. *Hai Jawani Toh Ishq Hona Hai* is the test of whether the formula still works in 2026 — a year when the highest-grossing Bollywood film (*Dhurandhar 2*, ₹1,184 crore) is a Ranveer Singh action franchise, not a family comedy.

At the trailer launch, David Dhawan acknowledged the uncertainty. "We are living in times when every Friday, we question cinema," Varun said, speaking for both of them. "All I want to say is that this is a David Dhawan film. If my family has had one motto, it is to make people laugh. My father just wants to make people laugh."

David Dhawan added: "He's improving a lot, and it's visible. He's taking care of me also at this age." Then he noted, about the speculation regarding retirement: "My son is making a film. He's also working. I am standing behind them. Whenever they need me for any scene, I am there for them always."

The sentence is about cinema. It is also not about cinema at all.""",
    })
    print(f"✅ Article 2 prepared: {slug2}")
else:
    print(f"⚠️ DUPLICATE: {slug2}")


# ══════════════════════════════════════════════════════════════
# INSERT ARTICLES
# ══════════════════════════════════════════════════════════════
print(f"\n📝 Inserting {len(articles)} articles...")
for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ Inserted: {art['slug'][:60]} → {result[0]['id'][:8] if result else '?'}")
    except Exception as e:
        print(f"❌ Insert failed for {art['slug'][:40]}: {e}")


# ══════════════════════════════════════════════════════════════
# IMAGE SOURCING — Wikipedia first (mandatory), Pexels fallback
# ══════════════════════════════════════════════════════════════
print("\n── Image Sourcing ──")

# Check image skip list
skip_list = []
skip_file = Path.home() / "workspace/the-videshi-news/pipeline/image-skip-list.json"
if skip_file.exists():
    try:
        skip_list = json.loads(skip_file.read_text())
    except:
        pass

image_tasks = []
for art in articles:
    if art["slug"] in skip_list:
        print(f"  ⏭ Skipping (in skip list): {art['slug'][:50]}")
        continue
    image_tasks.append(art)

for art in image_tasks:
    slug = art["slug"]
    art_id = art["id"]
    img_url = None
    attribution = None

    # Step 1: Try Wikipedia for person images
    person_names = art.get("image_entities", [])
    for person in person_names:
        print(f"  🔍 Wikipedia lookup: '{person}'")
        img_url = fetch_wikipedia_person_image(person)
        if img_url:
            attribution = "Wikimedia Commons"
            break

    # Step 2: Pexels fallback only if Wikipedia failed
    if not img_url:
        query = art.get("image_search_query", "")
        if query:
            print(f"  🔍 Pexels fallback: '{query[:50]}'")
            img_url = fetch_pexels_image(query)
            if img_url:
                attribution = "The Videshi"

    # Step 3: Upload and patch
    if img_url:
        filename = f"{art_id}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        if final_url:
            patch_data = {"image_url": final_url}
            if attribution:
                patch_data["image_attribution"] = attribution
            status = sb_patch("p2_articles", f"id=eq.{art_id}", patch_data)
            print(f"  ✅ Image set for {slug[:50]} → HTTP {status}")
        else:
            print(f"  ⚠️ Upload failed for {slug[:50]}, setting direct URL")
            sb_patch("p2_articles", f"id=eq.{art_id}", {"image_url": img_url})
    else:
        print(f"  ⚠️ No image found for: {slug[:50]} (no image > wrong image)")


# ══════════════════════════════════════════════════════════════
# SCORE DECAY — entertainment articles
# ══════════════════════════════════════════════════════════════
print("\n── Score Decay ──")

cutoff_7d = (now - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
status_7d = sb_patch(
    "p2_articles",
    f"category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff_7d}&score_total=gt.35",
    {"score_total": 35}
)
print(f"7d+ decay → HTTP {status_7d}")

cutoff_3d = (now - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")
status_3d = sb_patch(
    "p2_articles",
    f"category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff_3d}&published_at=gte.{cutoff_7d}&score_total=gt.50",
    {"score_total": 50}
)
print(f"3-7d decay → HTTP {status_3d}")


print("\n✅ Entertainment writer batch complete.")
