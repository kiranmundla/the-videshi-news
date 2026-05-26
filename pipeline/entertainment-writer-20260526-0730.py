#!/usr/bin/env python3
"""Entertainment writer — May 26 2026, 07:30 UTC batch (00:30 PDT):
1. Ananya Panday's Bharatanatyam dance in Chand Mera Dil goes viral for all
   the wrong reasons — professional dancers call it robotic, netizens compare
   to Sridevi and Sai Pallavi, Congress spokesperson weighs in, choreography
   team defends it, film underperforms at box office (₹14.73 Cr weekend)
2. Imtiaz Ali apologises to Deepika Padukone after "good girl image" remark
   goes viral — reveals she was originally cast as Meera (not Veronica) in
   Cocktail, fans rally around Deepika, connects to Cocktail 2 releasing June 19
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

# ── Wikipedia image sourcing (MANDATORY per IMAGE-SOURCING-RULES.md) ──
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

def search_pexels(query, per_page=5):
    if not PEXELS_KEY:
        return []
    r = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": PEXELS_KEY},
        params={"query": query, "per_page": per_page, "orientation": "landscape"},
        timeout=10
    )
    if r.status_code == 200:
        return r.json().get("photos", [])
    print(f"  Pexels HTTP {r.status_code}")
    return []

# ── Image upload to Supabase ──
def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        img_data = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=15).content
        upload_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "image/jpeg",
        }
        r = requests.post(
            f"{SB_URL}/storage/v1/object/article-images/{filename}",
            headers=upload_headers,
            data=img_data,
            timeout=30
        )
        if r.status_code in (200, 201):
            return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
        elif r.status_code == 409:  # already exists, use upsert
            r2 = requests.put(
                f"{SB_URL}/storage/v1/object/article-images/{filename}",
                headers=upload_headers,
                data=img_data,
                timeout=30
            )
            if r2.status_code in (200, 201):
                return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ⚠ Upload failed ({r.status_code}): {filename}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return image_url  # fallback to original URL

# ── Check image skip list ──
skip_list_path = Path.home() / "workspace/the-videshi-news/pipeline/image-skip-list.json"
IMAGE_SKIP = set()
if skip_list_path.exists():
    try:
        IMAGE_SKIP = set(json.loads(skip_list_path.read_text()))
    except:
        pass

now = datetime.now(timezone.utc)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S")
articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Ananya Panday's Bharatanatyam Dance Controversy
# ══════════════════════════════════════════════════════════════
slug1 = "ananya-panday-bharatanatyam-chand-mera-dil-controversy-sridevi-sai-pallavi-bollywood-classical-dance-20260526"
if not check_duplicate(slug1):
    art1_id = str(uuid.uuid4())
    articles.append({
        "id": art1_id,
        "headline": "Ananya Panday Performed a Bharatanatyam Fusion in Chand Mera Dil. Bharatanatyam Dancers Called It Robotic. The Internet Pulled Up Sridevi and Sai Pallavi Videos. A Congress Spokesperson Said It Was an Insult. The Choreography Team Said She Nailed It. The Film Made ₹14.73 Crore.",
        "subheadline": "A dance sequence in Karan Johar's latest production has reignited one of Indian cinema's oldest debates: what happens when Bollywood borrows a classical art form and returns it in a form its practitioners do not recognise? The comparison videos — Sridevi in Chandni, Sai Pallavi in Maari 2 — have more views than the film's trailer. Chand Mera Dil, starring Ananya Panday and Lakshya, opened to ₹3 crore and finished its first weekend at ₹14.73 crore worldwide, underperforming against Drishyam 3, Karuppu, and a Marathi film about a locked temple.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 75,
        "tags": ["Ananya Panday", "Bharatanatyam", "Chand Mera Dil", "Sridevi", "Sai Pallavi", "classical dance", "Bollywood", "Karan Johar", "Dharma Productions", "Lakshya", "Vivek Soni", "dance controversy", "cultural appropriation", "box office", "diaspora", "NRI"],
        "diaspora_angle": "For NRIs who grew up watching Sridevi's feet trace precise Bharatanatyam mudras in Chandni or who forwarded Sai Pallavi's Rowdy Baby to non-Indian colleagues as proof that Indian cinema could dance, this controversy hits a specific nerve. The diaspora has a complicated relationship with how Bollywood represents classical Indian art forms — it is simultaneously the community most likely to defend Indian culture from external misrepresentation and the community most likely to cringe when that misrepresentation comes from within. Many NRIs learned Bharatanatyam at weekend classes in New Jersey or Fremont or Harrow, taught by instructors who insisted on years of training before performing. Watching a Bollywood actress perform a fusion version in a film sequence that took perhaps a few weeks of rehearsal, and then hearing the choreography team call it 'nailed it,' provokes a reaction that goes beyond aesthetic judgment. It touches on a deeper question: who gets to define what Bharatanatyam is when it leaves the sabha and enters the multiplex?",
        "sources": [
            {"url": "https://punjabkhabarnama.com/2026/05/25/bharatanatyam-dancers-criticise-ananya-pandays-viral-dance-in-chand-mera-dil-choreography-team-defends-performance/", "name": "Punjab Khabarnama"},
            {"url": "https://newz24india.in/ananya-panday-bharatnatyam-chand-mera-dil/", "name": "Newz24 India"},
            {"url": "https://hauterrfly.com/entertainment/internet-ananya-panday-bharatnatyam-chand-mera-dil/", "name": "Hauterrfly"},
            {"url": "https://www.hollywoodreporterindia.com/box-office/chand-mera-dil-box-office-opening-weekend", "name": "Hollywood Reporter India"}
        ],
        "image_search_query": "Bharatanatyam classical dance performance stage Indian traditional",
        "image_entities": ["Ananya Panday"],
        "image_must_show": "Classical Indian dance or Bharatanatyam performance",
        "word_count": 780,
        "body": """The clip is 47 seconds long. In it, **Ananya Panday** — playing a character named Chandni in the Karan Johar-produced romantic drama **Chand Mera Dil** — performs what the film calls a Bharatanatyam-inspired fusion dance at a college event. The movements combine classical hand gestures with contemporary hip-hop transitions, set to a modern arrangement with traditional percussion underneath.

Within 24 hours, the clip had been viewed millions of times. Not because people liked it.

## The Professional Response

Several Bharatanatyam dancers and choreographers responded publicly, and their criticism was specific rather than general.

The issue was not that a Bollywood film included Bharatanatyam. The issue was the execution. Professional dancers described the movements as "robotic," the posture as incorrect, and the transitions between classical and contemporary as jarring in a way that suggested neither form had been properly understood. The criticism was not about fusion as a concept — Bharatanatyam fusion has a long and celebrated history, from Chandralekha's experimental work to Akram Khan's collaborations — but about a specific performance that, in their view, lacked the foundational training that makes fusion coherent.

**Congress spokesperson Shama Mohamed** weighed in publicly, stating that classical forms like Bharatanatyam should not be "insulted" through poor representation. Whether a political spokesperson's opinion on a film's choreography constitutes relevant commentary is debatable. That the controversy was large enough to attract political attention is not.

## The Comparison Videos

The internet's response took a predictable but devastating form: side-by-side comparison videos.

**Sridevi** in *Chandni* (1989). **Sridevi** in *Mr. India* (1987). **Sai Pallavi** in *Maari 2* (2018). **Sai Pallavi** in *Rowdy Baby*, which has 1.7 billion views on YouTube and remains the most-watched South Indian song of all time.

The comparisons were not subtle. Sridevi, who trained in Bharatanatyam from childhood, performing the *Tandav* sequence in Chandni with a precision that made every gesture legible from the back row of a theatre. Sai Pallavi, who has no formal dance training but whose physical intelligence is so extraordinary that she makes choreography look like spontaneous expression. Between them, they define the two poles of what Bollywood audiences expect from classical dance on screen: technical mastery and intuitive grace.

Ananya Panday's performance, in the comparison videos, appeared to lack both.

## The Defence

Members of the choreography team pushed back strongly. The assistant choreographer associated with the sequence said Ananya "nailed it" and delivered exactly what the makers intended. Their argument was that the dance was never meant to be pure Bharatanatyam — it was a fusion designed for a character who is a college student performing at a campus event, not a professional dancer at a sabha. The informality was intentional. The hip-hop transitions were deliberate. The character's imperfection was the point.

This is a reasonable creative argument. It is also an argument that the audience has largely rejected. The distinction between "a character who dances imperfectly" and "an actress who dances imperfectly playing a character" is one that requires the audience to grant a level of intentionality that the execution did not communicate. When **Sai Pallavi** plays a college student who dances in *Premam*, the audience can see training underneath the character's casual spontaneity. When the training is not visible, the character explanation does not hold.

## The Box Office Context

The dance controversy is unfolding against the backdrop of **Chand Mera Dil**'s disappointing box office performance.

Directed by **Vivek Soni** and produced by **Dharma Productions**, the film opened to approximately **₹3 crore** on Thursday, May 22 — a discount-ticket day that should have pushed numbers higher. By Sunday, the India net stood at **₹11.10 crore**. The worldwide gross after the first weekend was **₹14.73 crore** against a reported budget of **₹28-35 crore**.

For context, the same weekend saw **Drishyam 3** (Malayalam) cross **₹112 crore worldwide** in three days, **Suriya's Karuppu** (Tamil) maintain momentum past **₹220 crore**, and **Deool Band 2** (Marathi) surprise with **₹15.75 crore** — a Marathi film about a village deity outgrossing a Dharma-backed Hindi romance.

By Monday (Day 4), Chand Mera Dil dropped to **₹1.75-2.25 crore**. Analyst **Taran Adarsh** noted the underperformance despite positive word-of-mouth, suggesting the film's CBFC-mandated modifications to its romantic content may have diluted its core appeal.

## Bollywood's Recurring Classical Dance Problem

The controversy is not new. Bollywood has a decades-long pattern of including classical dance sequences that range from meticulous (Madhuri Dixit's Kathak in *Devdas*, choreographed by Birju Maharaj himself) to careless (too many examples to list). The difference in 2026 is the speed and specificity of the response.

A generation ago, a dance sequence in a Hindi film would be judged by the audience in the theatre and perhaps discussed in a review column. In 2026, a 47-second clip is extracted, compared frame-by-frame with archival footage, analysed by professional dancers on Instagram Reels, amplified by political figures, and turned into a cultural debate — all before the film's first Monday earnings are reported.

Ananya Panday herself has not responded publicly. Neither has **Karan Johar** or director **Vivek Soni**. The silence is probably wise. The comparison videos will circulate regardless, and they have already outlasted the film's moment in the conversation.

## The Deeper Question

The debate, stripped of the memes and the political opportunism, comes down to a question that Indian cinema has never satisfactorily answered: **what does Bollywood owe to the classical traditions it borrows?**

Fusion is not the problem. Akram Khan fuses Kathak with contemporary dance and nobody objects, because the classical foundation is visible in every movement. AR Rahman fuses Carnatic music with electronic production and the result is celebrated, because the ragas are intact underneath the beats.

The problem arises when the classical element is used as aesthetic decoration — a costume, a pose, a gesture — without the structural understanding that makes it meaningful. When Bharatanatyam becomes a visual signifier for "Indian culture" rather than a living art form with specific technical requirements, the result is what the internet saw in that 47-second clip: something that looks like Bharatanatyam from a distance but dissolves under scrutiny.

For a film industry that regularly claims to represent Indian culture to the world, that gap between appearance and understanding is not a minor issue. It is the issue.""",
    })
    print(f"✅ Article 1 prepared: {slug1}")
else:
    print(f"⚠️ DUPLICATE: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Imtiaz Ali's "Good Girl" Remark About Deepika Padukone
# ══════════════════════════════════════════════════════════════
slug2 = "imtiaz-ali-deepika-padukone-good-girl-image-cocktail-veronica-casting-apology-cocktail-2-20260526"
if not check_duplicate(slug2):
    art2_id = str(uuid.uuid4())
    articles.append({
        "id": art2_id,
        "headline": "Imtiaz Ali Said Deepika Padukone Had a 'Good Girl Image' That Was a Facade. Then He Watched the Internet React. Then He Wrote Her an Apology. The Original Cocktail Made ₹120 Crore. Cocktail 2 Releases in 24 Days.",
        "subheadline": "In a viral interview promoting Cocktail 2 — the spiritual sequel starring Shahid Kapoor, Kriti Sanon, and Rashmika Mandanna — Imtiaz Ali revealed that Deepika Padukone was originally cast as Meera, the 'good girl,' before director Homi Adajania offered her Veronica instead. Ali's description of Deepika's off-screen personality as contradicting her public persona triggered a backlash from fans who accused him of being dismissive. He responded with a public clarification calling Deepika a 'pal' and saying being mean to her 'in this lifetime is impossible.'",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 72,
        "tags": ["Imtiaz Ali", "Deepika Padukone", "Cocktail", "Cocktail 2", "Veronica", "Meera", "Homi Adajania", "Shahid Kapoor", "Kriti Sanon", "Rashmika Mandanna", "Saif Ali Khan", "Diana Penty", "Bollywood", "casting", "good girl image", "diaspora", "NRI"],
        "diaspora_angle": "Cocktail (2012) holds a specific place in the NRI imagination because it was one of the first mainstream Bollywood films to depict the diaspora's social dynamics honestly — not as a fantasy of abroad but as a lived reality of identity negotiation. Veronica (Deepika) was the Indian woman who had fully assimilated into London's party culture; Meera (Diana Penty) was the one who hadn't. The film's genius was that it did not judge either. For NRIs who had watched themselves and their friends navigate that exact spectrum — the ones who went to Diwali puja and the ones who went to Fabric on Saturday nights, and the many who did both — Cocktail was the rare Bollywood film that understood them. Imtiaz Ali's revelation that Deepika was originally cast as Meera is fascinating precisely because it reveals how close the film came to being a completely different story. A Deepika-as-Meera Cocktail would have reinforced the good-girl narrative that Ali himself described. A Deepika-as-Veronica Cocktail — which is the one that exists — became a career-defining performance precisely because it contradicted expectations. For the diaspora, this casting decision was everything.",
        "sources": [
            {"url": "https://www.latestly.com/entertainment/bollywood/imtiaz-ali-clarifies-good-girl-image-remark-about-deepika-padukone-6891742.html", "name": "LatestLY"},
            {"url": "https://www.bollywoodhungama.com/news/bollywood/imtiaz-ali-clarification-deepika-padukone-good-girl-remark/", "name": "Bollywood Hungama"},
            {"url": "https://www.pinkvilla.com/entertainment/bollywood/deepika-padukone-gets-clarification-from-imtiaz-ali-1403517", "name": "Pinkvilla"},
            {"url": "https://www.mensxp.com/entertainment/bollywood/imtiaz-ali-apology-deepika-padukone-good-girl-statement", "name": "MensXP"}
        ],
        "image_search_query": "film director interview discussion Bollywood casting revelation",
        "image_entities": ["Imtiaz Ali", "Deepika Padukone"],
        "image_must_show": "Imtiaz Ali or Deepika Padukone",
        "word_count": 760,
        "body": """The interview was supposed to be a promotional conversation about **Cocktail 2**, which releases on **June 19, 2026**. Instead, filmmaker **Imtiaz Ali** — who did not direct the original Cocktail but is one of Bollywood's most prominent directors and a close friend of the franchise's creative team — said something about **Deepika Padukone** that the internet was not prepared to let go.

## The Remark

In the interview, Ali discussed the casting process behind the original **Cocktail** (2012), directed by **Homi Adajania** and starring **Saif Ali Khan**, **Deepika Padukone**, and **Diana Penty**.

He revealed that Deepika was originally considered for the role of **Meera** — the reserved, traditional, recently-arrived-in-London character that Diana Penty ultimately played. Homi Adajania, according to Ali, saw something in Deepika that contradicted her public persona and offered her **Veronica** instead — the party girl, the one who drank, danced, and wore clothes that no "good Indian girl" was supposed to wear in a Bollywood film.

Ali then described Deepika's off-screen personality in terms that, on paper, sound complimentary: she was wilder, more spontaneous, and less restrained than her "good girl image" suggested. He called it a facade — the kind of curated public persona that many actresses maintain.

The internet did not read it as complimentary.

## The Backlash

**Deepika Padukone's fanbase** — one of the most organised and vocal in Bollywood — responded within hours. The criticism had several layers.

First, the language. Describing a woman's public persona as a "facade" carries a specific implication: that she is performing respectability, that the real person underneath is somehow different from — and by implication less respectable than — the image she projects. Whether Ali intended this reading or not, it is the one that landed.

Second, the context. Deepika Padukone is not a newcomer being described by a senior figure. She is one of the highest-paid actresses in Indian cinema, a former Cannes jury member, a producer, and a person who has been publicly transparent about her struggles with depression. Describing her as having a "good girl facade" in 2026 felt reductive to fans who have watched her career evolve over 17 years.

Third, the timing. The remark came during a promotional interview for **Cocktail 2** — a sequel that does not feature Deepika. Discussing her persona while promoting a film she is not in felt, to many, like using her name for attention.

## The Clarification

Ali's response was swift, public, and notably warm. He issued a clarification — part apology, part explanation — directly addressing Deepika.

"You might misunderstand and be hurt, so I am telling you," he wrote, calling her a "pal" and stating that "being mean to her in this lifetime is impossible."

He clarified that his remarks were meant as an affectionate observation about how casting decisions work — that the best roles often come when directors see past an actor's public image to the person underneath. He said Deepika was unaware of the "emotional ground" he was describing and that his comments were never intended to diminish her.

The clarification was widely covered and appeared to defuse the immediate backlash. MensXP reported it as an apology. Pinkvilla framed it as a clarification. Deepika herself has not commented publicly, which is consistent with her general approach to industry controversies.

## The Cocktail Legacy

The original **Cocktail** earned **₹120 crore worldwide** — a strong number for 2012 — and became a cultural reference point that outlived its box office. Veronica became a costume staple for Halloween and Bollywood-themed parties across the diaspora. The film's soundtrack, including "Tumhi Ho Bandhu" and "Daaru Desi," remains in rotation at NRI gatherings a decade later.

But the film's real legacy is what it did for Deepika's career. Before Cocktail, she was the girl from *Om Shanti Om* and *Love Aaj Kal* — commercially successful but creatively limited by a certain type of role. Veronica broke that mould. Within two years, she would star in *Ram-Leela*, *Happy New Year*, and *Piku*, establishing the range that made her a definitive presence in Indian cinema.

The revelation that she was nearly cast as Meera — the exact type of role she had been playing — makes Cocktail's impact feel almost accidental. The career-defining performance happened because one director (Adajania) saw past the casting convention that another filmmaker (Ali, in his own telling) initially endorsed.

## What This Means for Cocktail 2

**Cocktail 2**, directed again by **Homi Adajania**, stars **Shahid Kapoor** as Kunal, **Kriti Sanon** as Ally, and **Rashmika Mandanna** as Divya. The trailer drops on **May 29**. The film releases on **June 19**.

It is a spiritual sequel — same director, same thematic territory (modern love, identity, London's Indian diaspora), entirely new characters. The Imtiaz Ali controversy has, inadvertently, made the original Cocktail trend on social media at exactly the moment when Cocktail 2's marketing campaign is ramping up.

Whether this was accidental or strategically convenient is a question the internet will debate until the trailer drops. What is less debatable is that Deepika Padukone's Veronica — the role she almost didn't get, the character that contradicted everything the industry thought it knew about her — remains more interesting than any promotional interview can capture.

The good girl image was never a facade. It was a casting assumption. Homi Adajania broke it. The internet, 14 years later, is still processing the implications.""",
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
# IMAGE SOURCING — Wikipedia first for person articles, Pexels fallback
# ══════════════════════════════════════════════════════════════
print("\n── Image Sourcing ──")

image_tasks = [
    {
        "slug": slug1,
        "art_id": art1_id if slug1 not in [a["slug"] for a in articles if False] else None,
        "person_names": ["Ananya Panday"],
        "pexels_query": "Bharatanatyam classical Indian dance performance stage",
        "pexels_fallback": "Indian classical dance traditional mudra",
        "attribution_wiki": "Wikimedia Commons",
    },
    {
        "slug": slug2,
        "art_id": art2_id if slug2 not in [a["slug"] for a in articles if False] else None,
        "person_names": ["Imtiaz Ali", "Deepika Padukone"],
        "pexels_query": "film director interview Bollywood",
        "pexels_fallback": "Indian cinema discussion creative meeting",
        "attribution_wiki": "Wikimedia Commons",
    },
]

for task in image_tasks:
    slug = task["slug"]

    # Skip if article wasn't inserted (duplicate)
    existing = sb_get("p2_articles", f"slug=eq.{slug}", "id,image_url")
    if not existing:
        print(f"  ⚠️ Article not found for {slug[:50]}, skipping image")
        continue

    art_id = existing[0]["id"]

    # Skip if in image skip list
    if art_id in IMAGE_SKIP or slug in IMAGE_SKIP:
        print(f"  ⚠️ In skip list: {slug[:50]}")
        continue

    # Skip if already has an image
    if existing[0].get("image_url"):
        print(f"  ℹ️ Already has image: {slug[:50]}")
        continue

    img_url = None
    attribution = None

    # Step 1: Try Wikipedia for each person
    for person in task["person_names"]:
        print(f"  Trying Wikipedia for '{person}'...")
        img_url = fetch_wikipedia_person_image(person)
        if img_url:
            attribution = task["attribution_wiki"]
            break

    # Step 2: Pexels fallback with SPECIFIC terms
    if not img_url:
        print(f"  Trying Pexels: '{task['pexels_query']}'...")
        photos = search_pexels(task["pexels_query"])
        if not photos and task.get("pexels_fallback"):
            print(f"  Trying Pexels fallback: '{task['pexels_fallback']}'...")
            photos = search_pexels(task["pexels_fallback"])
        if photos:
            photo = photos[0]
            img_url = photo["src"]["large2x"]
            attribution = "Pexels"
            print(f"  Pexels: photo {photo['id']}")

    # Step 3: Upload and patch
    if img_url:
        filename = f"{art_id}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        patch_data = {"image_url": final_url}
        if attribution:
            patch_data["image_attribution"] = attribution
        status = sb_patch("p2_articles", f"id=eq.{art_id}", patch_data)
        print(f"  ✅ Image set for {slug[:50]} → HTTP {status}")
    else:
        print(f"  ⚠️ No image found for: {slug[:50]} (no image > wrong image)")


# ══════════════════════════════════════════════════════════════
# SCORE DECAY — entertainment articles
# ══════════════════════════════════════════════════════════════
print("\n── Score Decay ──")

# 7+ days old → score 35
cutoff_7d = (now - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
status_7d = sb_patch(
    "p2_articles",
    f"category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff_7d}&score_total=gt.35",
    {"score_total": 35}
)
print(f"7d+ decay → HTTP {status_7d}")

# 3-7 days old → score 50
cutoff_3d = (now - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")
status_3d = sb_patch(
    "p2_articles",
    f"category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff_3d}&published_at=gte.{cutoff_7d}&score_total=gt.50",
    {"score_total": 50}
)
print(f"3-7d decay → HTTP {status_3d}")


print("\n✅ Entertainment writer batch complete.")
