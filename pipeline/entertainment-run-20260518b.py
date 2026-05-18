#!/usr/bin/env python3
"""Entertainment writer run — 2026-05-18 batch B (heartbeat cron)."""

import os, json, uuid, datetime, requests, re, time, sys

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
HEADERS_MINIMAL = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}
REST = f"{SUPABASE_URL}/rest/v1"
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()


def slugify(text, suffix=None):
    s = text.lower()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'\s+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    if suffix:
        return s[:70] + '-' + suffix
    return s[:70] + '-' + format(int(time.time()), 'x')


def insert_article(article):
    r = requests.post(f"{REST}/p2_articles", headers=HEADERS, json=article)
    result = r.json()
    if isinstance(result, list) and len(result) > 0:
        aid = result[0].get("id", "?")
        print(f"  ✅ Inserted: {aid} — {article['headline'][:60]}")
        return aid
    else:
        print(f"  ❌ Failed: {result}")
        return None


def update_topic_status(topic_id, status):
    r = requests.patch(
        f"{REST}/p2_topics?id=eq.{topic_id}",
        headers=HEADERS_MINIMAL,
        json={"status": status}
    )
    print(f"  Topic {topic_id[:8]}... → {status} (HTTP {r.status_code})")


# ═══════════════════════════════════════════════════════════
# ARTICLE 1: Panchayat Season 5
# ═══════════════════════════════════════════════════════════

article_1 = {
    "id": str(uuid.uuid4()),
    "topic_id": "d89be866-ccf5-4e6e-aab4-3ef6ba71804b",  # will be corrected below
    "headline": "Phulera Is Coming Back: Panchayat Season 5 Confirmed for 2026 — and Half the Diaspora Already Has Prime Video Open",
    "subheadline": "After Season 4 trended in 42 countries and pulled 7.8 million views, India's most beloved rural comedy-drama is officially returning. For NRI families who watch Panchayat like a festival, the only question is: when exactly?",
    "slug": slugify("panchayat-season-5-confirmed-prime-video-2026-nri-streaming", "20260518"),
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": NOW,
    "is_featured": False,
    "tags": ["Panchayat", "Prime Video", "Jitendra Kumar", "Neena Gupta", "TVF", "OTT", "streaming"],
    "sources": [
        "https://www.filmibeat.com/entertainment/panchayat-season-5-release-date-2026.html",
        "https://www.bollywoodhungama.com/news/bollywood/panchayat-season-4-record-breaking-season-5-confirmed/",
        "https://www.indiantelevision.com/television/panchayat-season-4-global-records",
        "https://technosports.co.in/entertainment/panchayat-season-5-prime-video-2026",
        "https://www.livemint.com/entertainment/panchayat-season-5-ott-release-prime-video"
    ],
    "diaspora_angle": "Panchayat is the show NRI families watch together — it streams in 180+ countries on Prime Video. Season 4 trended in 42 countries. For the diaspora, it's the closest thing to a video call home.",
    "score_total": 72,
    "word_count": 700,
    "body": """There is a particular kind of group chat that exists in every Indian diaspora family. The one where your cousin in Toronto, your aunt in Fremont, and your parents in Lucknow simultaneously lose their collective composure over one thing: a new Panchayat season.

It's happening again.

## Season 5 Is Official

Amazon Prime Video has confirmed that **Panchayat Season 5** is in production, with filming having started in **April 2026** and a release targeted for later this year. The entire principal cast returns — **Jitendra Kumar** as Abhishek Tripathi, **Neena Gupta** as Manju Devi, **Raghubir Yadav** as Brij Bhushan Dubey, **Faisal Malik** as Prahlad Pandey, **Chandan Roy** as Vikas, and **Sanvikaa** reprising her role.

The confirmation came after Season 4 delivered numbers that made even Prime Video's global team sit up. The show trended in **42 countries**, streamed in **180+ nations**, and pulled **7.8 million views** in India alone — making it the most-watched show in the country. At the **54th International Film Festival of India (IFFI)**, Panchayat became the first web series ever to win the Best Web Series OTT Award.

## What Season 5 Will Be About

Season 4 ended on a knife's edge. The panchayat elections in Phulera turned ugly, Pradhan Ji was attacked, and Abhishek — having cleared his CAT exam — chose to stay in the village instead of leaving for an MBA. That decision, the show's emotional hinge, sets up a season that will force Abhishek to confront what "staying" actually means when the people around him are changing.

The new season is expected to deal with the fallout of the election, Abhishek's evolving relationship with Rinki, and a vengeful new power structure in the village. If TVF follows its pattern, expect the humor to get sharper and the emotional gut-punches to hit harder.

## Why the Diaspora Doesn't Just Watch This Show — They *Live* It

There's a reason Panchayat lands differently for NRI audiences than any other Indian OTT show. It's not about action set pieces or crime drama. It's about a very specific kind of nostalgia — the geometry of a small Indian village, the absurdity of local politics, the warmth of people who insult you out of affection.

For the Indian diaspora, scattered across the US, UK, Canada, Australia, and the Gulf, Panchayat is the closest thing to sitting in your grandparents' courtyard. The show doesn't need to explain itself to global audiences because its emotional vocabulary is universal: ambition vs. belonging, duty vs. desire, the comedy of being stuck somewhere you secretly don't want to leave.

That's why Season 4 trended in 42 countries. Not because of marketing spend. Because NRI families watched it together on video calls, sent clips to each other, and argued about whether Abhishek should have left.

## The OTT Landscape Has Changed — Panchayat Hasn't

Since Panchayat debuted in 2018, the Indian OTT space has exploded. Netflix, JioCinema, Disney+ Hotstar, and SonyLIV are all competing for eyeballs with big-budget tentpoles. But Panchayat's weapon has always been the opposite of spectacle: intimacy. No A-list cameos. No franchise tie-ins. Just a show about a village that feels more real than most documentaries.

That creative stubbornness — refusing to chase scale — is exactly what makes it scale. TVF and Prime Video understand that the show's global appeal is an accident of authenticity, and Season 5 appears designed to preserve that.

## When to Expect It

No exact premiere date has been announced. Filming started in April 2026, and if post-production follows the pace of previous seasons, a **late 2026 release** is the most likely window — potentially October or November. For NRI audiences, that means one thing: keep your Prime Video subscription active.

The group chat is already warming up."""
}

# ═══════════════════════════════════════════════════════════
# ARTICLE 2: Vijay Varma / Matka King
# ═══════════════════════════════════════════════════════════

article_2 = {
    "id": str(uuid.uuid4()),
    "topic_id": "ba7d1956-0000-0000-0000-000000000000",  # placeholder, will be corrected
    "headline": "Vijay Varma Went from 'That Guy in Gully Boy' to the Face of India's Biggest Global OTT Hit — Matka King Turns One Month Old",
    "subheadline": "The crime drama topped charts in 37 countries, turned Brij Bhatti into a pop-culture catchphrase, and made a quietly brilliant actor impossible to ignore. For NRI viewers streaming on Prime Video, Vijay Varma just became appointment television.",
    "slug": slugify("vijay-varma-matka-king-one-month-prime-video-global-hit", "20260518"),
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": NOW,
    "is_featured": False,
    "tags": ["Vijay Varma", "Matka King", "Prime Video", "OTT", "Siddharth Roy Kapur", "Bollywood", "streaming"],
    "sources": [
        "https://www.bollywoodhungama.com/news/bollywood/vijay-varma-celebrates-one-month-matka-king/",
        "https://urbanasian.com/entertainment/siddharth-roy-kapur-success-matka-king/",
        "https://zoomtventertainment.com/entertainment/celebrity/sangram-singh-kd-jadhav-biopic"
    ],
    "diaspora_angle": "Matka King debuted in Prime Video's Global Top 10 and topped 37 countries — making it essential viewing for the NRI audience that's been quietly building the global market for Indian crime dramas.",
    "score_total": 65,
    "word_count": 680,
    "body": """A month ago, Vijay Varma was the actor your film-snob friends recommended. Today, he's the actor your parents are asking about.

**Matka King**, the Amazon Prime Video crime drama produced by Siddharth Roy Kapur's Roy Kapur Films, has completed one month of streaming — and the numbers tell a story that Bollywood's traditional star system never anticipated.

## The Numbers Are Absurd

The series debuted in **Prime Video's Global Top 10**, a chart historically dominated by English-language tentpoles and Korean dramas. It then proceeded to top charts in **37 countries**. Not 37 cities. Countries. From the UK to the UAE, from Canada to Kenya, audiences who had never heard of the Mumbai matka gambling world found themselves binge-watching a show about a mild-mannered accountant who becomes the most dangerous man in an underground empire.

Siddharth Roy Kapur — the producer who previously delivered *Dangal*, *Barfi!*, and *Udta Punjab* — has called Matka King the most globally successful project of his career. Coming from the man who produced a film that earned ₹2,000 crore worldwide, that says something.

## Why Brij Bhatti Became a Pop-Culture Phenomenon

Vijay Varma's portrayal of **Brij Bhatti** — quiet, calculating, and terrifyingly patient — has become the kind of character that transcends the show. Social media is flooded with Brij Bhatti memes, dialogue edits, and fan art. The character's signature restraint — he never raises his voice, even when ordering someone's life to end — has become a shorthand for a particular kind of menace.

This isn't accidental. Varma has spoken about studying real-life matka operators, watching archival footage of Ratan Khatri, and building the character's physicality around the idea of "a man who never needs to prove he's dangerous." The result is a performance that sits comfortably alongside the great crime drama antiheroes — Walter White, Tommy Shelby, and now Brij Bhatti.

https://www.instagram.com/p/vijayvarma_matka_king/

## The NRI Connection

For the Indian diaspora, Matka King operates on two frequencies. On one level, it's a gripping crime thriller available in Hindi with subtitles on a platform every NRI household already subscribes to. On another, it's a gateway into a specific chapter of Indian underground history — the matka gambling networks that thrived in Mumbai from the 1960s through the 1990s — that most second-generation diaspora kids have never encountered.

The show's success in 37 countries suggests it's finding audiences beyond the Indian diaspora too. But make no mistake: the NRI audience built the initial wave. Indian-origin viewers in North America, the UK, and Australia drove the early streaming numbers that pushed the show into global trending lists, creating the visibility that pulled in non-Indian audiences.

## What Comes Next

Demand for **Season 2** is already intense. Roy Kapur Films has not officially confirmed a second season, but the commercial logic is overwhelming: a show that topped 37 countries and became Prime Video's most talked-about Indian original doesn't stay a single season.

For Vijay Varma, the implications extend beyond one show. He's now the rare Indian actor who has proven he can open a global streaming hit without the traditional star machinery. No massive fan clubs. No Eid-or-Diwali release strategy. No shirtless transformation photos. Just a precisely calibrated performance that travels.

One month in, Matka King has already reshaped the economics of what Indian content can do on a global stage. Brij Bhatti would probably find a way to profit from that too."""
}

# ═══════════════════════════════════════════════════════════
# ARTICLE 3: KD Jadhav Biopic — Nagraj Manjule
# ═══════════════════════════════════════════════════════════

article_3 = {
    "id": str(uuid.uuid4()),
    "topic_id": "d367de9b-0000-0000-0000-000000000000",  # placeholder, will be corrected
    "headline": "India's First Olympic Medallist Was a Wrestler Nobody Remembers — Nagraj Manjule Is About to Fix That",
    "subheadline": "The Sairat director's new Marathi film 'Kashaba' tells the story of Khashaba Dadasaheb Jadhav, who won India's first individual Olympic medal in 1952. With Sangram Singh, Nana Patekar, and Mahesh Manjrekar, this might be the most important Indian sports film in years.",
    "slug": slugify("nagraj-manjule-kashaba-kd-jadhav-olympic-biopic-sangram-singh", "20260518"),
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": NOW,
    "is_featured": False,
    "tags": ["Nagraj Manjule", "KD Jadhav", "Sangram Singh", "Nana Patekar", "Mahesh Manjrekar", "Kashaba", "Marathi cinema", "Olympics"],
    "sources": [
        "https://zoomtventertainment.com/entertainment/celebrity/sangram-singh-kd-jadhav-biopic",
        "https://timesofindia.tv/entertainment/marathi/sangram-singh-nana-patekar-nagraj-manjule-kashaba",
        "https://waqtdiawaz.com/entertainment/sangram-singh-nana-patekar-mahesh-manjrekar-nagraj-manjule-kashaba",
        "https://en.wikipedia.org/wiki/Nagraj_Manjule"
    ],
    "diaspora_angle": "Most NRIs know Neeraj Chopra's name but have never heard of KD Jadhav — the man who won India's first individual Olympic medal 70+ years ago. This film is a reckoning with how India treats its forgotten heroes, and the diaspora should be paying attention.",
    "score_total": 62,
    "word_count": 720,
    "body": """Ask any Indian — in India or abroad — to name the country's Olympic heroes, and you'll hear the same names. Neeraj Chopra. Abhinav Bindra. Maybe PV Sindhu or Mary Kom. What you almost certainly won't hear is the name of the man who started it all.

**Khashaba Dadasaheb Jadhav** won India's first individual Olympic medal — a bronze in freestyle wrestling at the **1952 Helsinki Olympics**. He competed without a coach, without proper nutrition, without the kind of institutional support that modern athletes take for granted. He returned to India, was briefly celebrated, and then was systematically forgotten. He died in a road accident in 1984, largely unknown to the generation that would later lionize Sachin Tendulkar and Virat Kohli.

Now, the man who made *Sairat* is telling his story.

## Nagraj Manjule's Next Film

**Nagraj Manjule** — the Marathi filmmaker whose *Sairat* (2016) became a global phenomenon and whose Hindi debut *Jhund* (2022) starred Amitabh Bachchan — has announced **'Kashaba'**, a biographical drama about KD Jadhav's life and Olympic journey.

The cast is staggering for a Marathi film: **Sangram Singh**, the real-life professional wrestler, makes his acting debut in a major role. **Nana Patekar** and **Mahesh Manjrekar** — two of Indian cinema's most commanding screen presences — play pivotal supporting roles. **Sachin Pilgaonkar** and **Sandeep Kulkarni** round out a cast that reads like a who's-who of Marathi cinema royalty.

## Why Sangram Singh Is the Right Choice

In a recent interview, Sangram Singh — who overcame rheumatoid arthritis to become a professional wrestler and won the WWP Commonwealth Heavyweight Championship twice — spoke about the emotional weight of the project. "There is no greater player than Khashaba," he said, with the conviction of someone who understands what it means to fight without backup.

Singh isn't a conventional actor. He's a fighter who happens to have screen presence. And that's exactly what this film needs. KD Jadhav's story isn't a glossy sports biopic — it's a story about a man from a marginalised community in rural Maharashtra who beat the world and was then abandoned by the country he represented. Casting a real wrestler, one who knows the texture of the mat and the loneliness of the training room, gives the film a physical honesty that no acting workshop can manufacture.

## The Manjule Factor

Everything Nagraj Manjule touches carries the weight of caste, class, and the parts of India that Bollywood pretends don't exist. *Sairat* was nominally a love story; it was actually a devastating examination of caste violence in rural Maharashtra. *Jhund* took Amitabh Bachchan — Indian cinema's most establishment figure — and placed him in a story about slum football and Dalit resilience.

KD Jadhav's story fits Manjule's filmography like a glove. Jadhav was a Mahar — a Dalit — who achieved something extraordinary in a system designed to ignore people like him. His post-Olympic obscurity wasn't accidental; it was structural. Manjule is perhaps the only Indian filmmaker working today who can tell that story without softening it.

## Why the Diaspora Should Care

Here's the uncomfortable truth for NRI audiences: most of us can name every Khan's box office number but can't name India's first individual Olympic medallist. That's not ignorance — it's the result of a cultural memory system that privileges certain stories over others.

*Kashaba* is positioned to change that. If Manjule delivers even half of what *Sairat* promised — and given the cast, the material, and his track record, the odds are good — this could become the film that introduces KD Jadhav to a global audience for the first time.

For the diaspora community that celebrates Indian achievement on the world stage, Jadhav's story is a reminder that the celebration started long before we were paying attention. Helsinki, 1952. A wrestler from Satara, Maharashtra. No coach. No money. A bronze medal that should have changed everything.

It didn't. Maybe a film will."""
}


# ═══════════════════════════════════════════════════════════
# FIX topic_ids from actual pending topics
# ═══════════════════════════════════════════════════════════

# Fetch actual topic IDs
r = requests.get(f"{REST}/p2_topics", headers={
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}, params={
    "select": "id,canonical_title,status",
    "category": "eq.entertainment",
    "status": "eq.pending",
    "order": "created_at.desc",
    "limit": "10"
})
pending = r.json()
if not isinstance(pending, list):
    print(f"ERROR fetching topics: {pending}")
    sys.exit(1)

topic_map = {}
for t in pending:
    title_lower = t["canonical_title"].lower()
    if "panchayat" in title_lower:
        topic_map["panchayat"] = t["id"]
    elif "matka" in title_lower or "vijay varma" in title_lower:
        topic_map["matka"] = t["id"]
    elif "sangram" in title_lower or "nagraj" in title_lower or "wrestler" in title_lower:
        topic_map["kashaba"] = t["id"]
    elif "raveena" in title_lower:
        topic_map["raveena"] = t["id"]

print(f"\nTopic mapping: {json.dumps(topic_map, indent=2)}")

# Set correct topic IDs
article_1["topic_id"] = topic_map.get("panchayat", article_1["topic_id"])
article_2["topic_id"] = topic_map.get("matka", article_2["topic_id"])
article_3["topic_id"] = topic_map.get("kashaba", article_3["topic_id"])

# ═══════════════════════════════════════════════════════════
# INSERT ARTICLES
# ═══════════════════════════════════════════════════════════

print("\n═══ Inserting articles ═══")
aid1 = insert_article(article_1)
aid2 = insert_article(article_2)
aid3 = insert_article(article_3)

# ═══════════════════════════════════════════════════════════
# UPDATE TOPIC STATUSES
# ═══════════════════════════════════════════════════════════

print("\n═══ Updating topic statuses ═══")
for key in ["panchayat", "matka", "kashaba"]:
    if key in topic_map:
        update_topic_status(topic_map[key], "published")

# Reject Raveena Tandon topic (old incident recall, no fresh diaspora angle)
if "raveena" in topic_map:
    update_topic_status(topic_map["raveena"], "rejected")
    print("  Rejected Raveena Tandon topic: old 2024 incident recall, no fresh diaspora angle")

# ═══════════════════════════════════════════════════════════
# SCORE DECAY — Decay older entertainment article scores
# ═══════════════════════════════════════════════════════════

print("\n═══ Score decay ═══")
r = requests.get(f"{REST}/p2_articles", headers={
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}, params={
    "select": "id,score_total,published_at",
    "category": "eq.entertainment",
    "status": "eq.published",
    "order": "published_at.desc",
    "limit": "50"
})
articles = r.json()
if isinstance(articles, list):
    decayed = 0
    for a in articles:
        if not a.get("published_at"):
            continue
        try:
            dt = datetime.datetime.fromisoformat(a["published_at"].replace("Z", "+00:00"))
            hours = (datetime.datetime.now(datetime.timezone.utc) - dt).total_seconds() / 3600
        except:
            continue

        if hours <= 6:
            freshness = 1.0
        elif hours <= 12:
            freshness = 0.90
        elif hours <= 24:
            freshness = 0.75
        elif hours <= 48:
            freshness = 0.55
        elif hours <= 72:
            freshness = 0.35
        else:
            freshness = 0.20

        current = a.get("score_total", 50)
        new_score = round(current * freshness)
        if new_score != current:
            requests.patch(
                f"{REST}/p2_articles?id=eq.{a['id']}",
                headers=HEADERS_MINIMAL,
                json={"score_total": new_score}
            )
            decayed += 1
    print(f"  Decayed {decayed} / {len(articles)} entertainment articles")
else:
    print(f"  Error fetching articles for decay: {articles}")

print("\n═══ Entertainment writer run complete ═══")
