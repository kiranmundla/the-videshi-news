#!/usr/bin/env python3
"""
Entertainment writer run - 2026-05-18 evening
Articles: Desi Bling (Netflix), System (Prime Video), KKK15 Harsh Gujral
"""
import os, json, uuid, requests, sys
from datetime import datetime, timezone

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ["SUPABASE_ANON_KEY"])
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def insert_article(article):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=HEADERS, json=article)
    if r.status_code in (200, 201):
        data = r.json()
        aid = data[0]["id"] if isinstance(data, list) else data["id"]
        print(f"  ✓ Inserted: {aid} — {article['headline'][:60]}...")
        return aid
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return None

def update_topic(topic_id, status):
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_topics?id=eq.{topic_id}",
        headers=HEADERS,
        json={"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}
    )
    if r.status_code in (200, 204):
        print(f"  ✓ Topic {topic_id[:8]}... → {status}")
    else:
        print(f"  ✗ Topic update failed: {r.text[:200]}")

now = datetime.now(timezone.utc).isoformat()

# ══════════════════════════════════════════════════════════════════
# ARTICLE 1: Desi Bling
# ══════════════════════════════════════════════════════════════════
print("\n=== ARTICLE 1: Desi Bling ===")

desi_bling_body = """Netflix's newest reality export lands on May 20 — and for once, it is not about a mansion in the Hollywood Hills or a dating island in Fiji. *Desi Bling* plants its cameras squarely inside Dubai's wealthiest Indian social circle, turning the lens on a community that NRIs in the Gulf, the US, and the UK know intimately but have never seen on a global streaming platform.

## The Premise

Karan Kundrra and Tejasswi Prakash — fresh off *Laughter Chefs* and individually two of Indian television's most-followed faces — arrive in Dubai as newcomers trying to crack the city's most exclusive desi social tier. The series follows them as they navigate brunches that cost more than a month's rent in most Indian cities, negotiate friendships with billionaire heirs, and juggle their own very public relationship under the scrutiny of people who consider seven-figure Diwali parties a low-key affair.

## The Cast

Beyond Karan and Tejasswi, the lineup reads like a who's-who of the Indian business elite in the Emirates. Rizwan Sajan — chairman of the Danube Group and one of the UAE's most prominent Indian entrepreneurs — appears alongside Satish Sanpal, whose name is familiar to anyone who has bought property or insurance through the Dubai desi network. Netflix is also billing cameos from Tiger Shroff and Shilpa Shetty, both of whom have deep Dubai connections through endorsements and property investments.

The show's real star, though, may be Dubai itself — or rather, the particular version of Dubai that the Indian diaspora has built over decades. The UAE is home to roughly 3.5 million Indian nationals, making it the largest overseas Indian population in any single country. *Desi Bling* is the first major production to dramatise their social ecosystem for a global audience.

## Why NRIs Should Pay Attention

For years, the reality TV conversation around Indian wealth has been limited to Fabulous Lives of Bollywood Wives and its Hyderabad spin-off — both firmly anchored in Mumbai's film industry. *Desi Bling* shifts that geography and that economy. The Dubai-based Indian community is built on trade, construction, gold, and tech — not box-office numbers. The social codes are different. The money often comes from family empires that started with a single shop in Deira in the 1970s. For NRIs watching from New Jersey or Birmingham, this is closer to their uncle's story than anything happening on *Bigg Boss*.

Netflix's decision to make this a global release — available simultaneously in every market, including India, the US, the UK, Canada, and the Middle East — signals that the platform sees diaspora content as a genuine commercial category, not a subtitled afterthought.

## The Streaming Angle

The show drops just days after Netflix reported a 14 per cent subscriber increase in the India and APAC region. Indian reality content has been a consistent growth driver for the platform, with *The Great Indian Kapil Show* regularly appearing in the global top ten. *Desi Bling* is a calculated bet that NRI-focused luxury content can replicate that success.

If it works, expect more shows centred on Indian communities in London, Toronto, and Silicon Valley. If it does not, it will still be the most entertaining look at a Dubai pool party since every uncle's WhatsApp status from their last Emirates vacation.

*Desi Bling* premieres May 20 on Netflix. All episodes available globally at launch."""

article1 = {
    "headline": "Netflix Just Pointed a Camera at Dubai's Richest Desi Circle — and Every NRI Uncle's WhatsApp Group Is Already Buzzing",
    "subheadline": "'Desi Bling' premieres May 20 with Karan Kundrra, Tejasswi Prakash, and a cast of Indian billionaires who make the Fabulous Wives look like they're on a budget",
    "body": desi_bling_body.strip(),
    "diaspora_angle": "The show centres on the Indian diaspora community in Dubai — 3.5 million strong — and streams globally on Netflix, making it the first major reality series to dramatise the social world that NRIs in the Gulf, US, and UK know firsthand.",
    "vertical": "culture",
    "category": "entertainment",
    "tags": ["Netflix", "Desi Bling", "Karan Kundrra", "Tejasswi Prakash", "Dubai", "NRI", "reality TV", "Indian diaspora", "Tiger Shroff", "Shilpa Shetty", "OTT"],
    "urgency": "developing",
    "sources": ["Netflix", "Bollywood Hungama", "Filmibeat", "Filmfare", "Gadgets 360"],
    "slug": "desi-bling-netflix-dubai-indian-billionaires-nri-20260518",
    "word_count": 680,
    "status": "published",
    "published_at": now,
    "score_total": 88
}

a1_id = insert_article(article1)

# ══════════════════════════════════════════════════════════════════
# ARTICLE 2: System
# ══════════════════════════════════════════════════════════════════
print("\n=== ARTICLE 2: System ===")

system_body = """Four days from now, Sonakshi Sinha will walk into a courtroom — and for the first time in her career, she will not be waiting for a hero to rescue anyone. In *System*, premiering May 22 on Amazon Prime Video, she plays Neha Rajvansh, a privileged public prosecutor whose life collides with Sarika Rawat, a stenographer played by Jyotika in her Hindi-language comeback. Directed by Ashwiny Iyer Tiwari — the filmmaker behind *Bareilly Ki Barfi* and *Nil Battey Sannata* — the film is a legal thriller that uses the courtroom as a mirror for the class divide running through modern India.

## The Setup

Neha is everything Indian legal dramas have taught us to expect from the prosecution: polished, English-speaking, the kind of woman who grew up in the right colony and went to the right law school. Sarika is everything those dramas tend to ignore — the invisible machinery of the system, a government employee who sees injustice from the inside but lacks the credentials to challenge it. When their paths cross over a case that neither can afford to lose, the film asks a question that resonates far beyond the courtroom: who does the system actually serve?

Ashutosh Gowariker rounds out the principal cast in a role that the trailer positions as the establishment figure both women must navigate around.

## Why This Matters for NRI Audiences

Prime Video is releasing *System* in Hindi across 240-plus countries simultaneously — which means the Indian legal system, with all its contradictions and class markers, will be streaming in living rooms from Sunnyvale to Southall on the same day it reaches Mumbai.

For NRIs, courtroom dramas carry a particular weight. Many in the diaspora left India partly because of the system's inefficiencies — delayed justice, corruption, the sense that outcomes depend on connections rather than evidence. Ashwiny Iyer Tiwari has built a reputation for making those structural inequalities feel personal rather than preachy, and the trailer suggests *System* follows that template.

## The Cast Angle

Sonakshi Sinha's presence guarantees eyeballs, but the real curiosity is Jyotika. One of Tamil cinema's most respected actors — with a filmography that includes *Chandramukhi*, *36 Vayadhinile*, and *Ponmagal Vandhal* — she has rarely worked in Hindi. Her casting signals that *System* is aiming for pan-Indian appeal, not just the Hindi belt.

For Telugu and Tamil audiences streaming with subtitles, Jyotika's name alone is a draw. For Hindi audiences, she is a discovery. That kind of cross-pollination has become Prime Video's signature play in India, and it is exactly the kind of casting that works internationally, where NRI audiences consume content across all four southern languages plus Hindi.

## The Director's Track Record

Ashwiny Iyer Tiwari does not make escapist cinema. *Nil Battey Sannata* was about a single mother fighting for her daughter's education. *Bareilly Ki Barfi* was a romantic comedy, but one grounded in small-town class anxiety. *Panga* followed a woman returning to sport against the weight of domestic expectations. *System* fits that arc — structural inequality examined through individual stories.

The streaming release also means no box-office pressure, which historically has allowed Prime Video originals to take creative risks that theatrical releases cannot. For a film tackling the Indian justice system, that freedom matters.

*System* streams May 22 on Amazon Prime Video across 240+ countries."""

article2 = {
    "headline": "Sonakshi Sinha's First Courtroom Role Arrives May 22 — and It Streams in 240 Countries the Same Day It Hits Mumbai",
    "subheadline": "'System' pairs Sonakshi with Tamil superstar Jyotika for a legal thriller about class, privilege, and who the Indian justice system actually works for",
    "body": system_body.strip(),
    "diaspora_angle": "Streaming simultaneously in 240+ countries on Prime Video, making it instantly accessible to NRIs. The film's exploration of India's class divide and justice system resonates with diaspora audiences who left partly because of those structural issues.",
    "vertical": "culture",
    "category": "entertainment",
    "tags": ["System", "Sonakshi Sinha", "Jyotika", "Prime Video", "Ashwiny Iyer Tiwari", "courtroom drama", "OTT", "legal thriller", "Indian cinema", "NRI streaming"],
    "urgency": "developing",
    "sources": ["Amazon Prime Video", "Bollywood Hungama", "Filmfare", "The Daily Jagran"],
    "slug": "system-sonakshi-sinha-jyotika-prime-video-courtroom-nri-20260518",
    "word_count": 700,
    "status": "published",
    "published_at": now,
    "score_total": 82
}

a2_id = insert_article(article2)

# ══════════════════════════════════════════════════════════════════
# ARTICLE 3: Harsh Gujral & KKK15
# ══════════════════════════════════════════════════════════════════
print("\n=== ARTICLE 3: Harsh Gujral & KKK15 ===")

kkk_body = """Harsh Gujral built his career by making people laugh at the absurdity of being a regular guy from a small town trying to survive in India's big cities. Now he is trying to survive something more literal: jumping out of helicopters and swimming through crocodile-infested waters in Cape Town, South Africa, for *Khatron Ke Khiladi 15*.

The comedian — whose YouTube specials and Instagram reels have made him one of India's most-watched stand-up acts — is part of a 13-member cast that includes Bigg Boss 19 winner Gaurav Khanna, Rubina Dilaik making a return appearance, Jasmin Bhasin, Avika Gor, and Rithvik Dhanjani. The season, hosted by Rohit Shetty, is filming in Cape Town and set to premiere on Colors TV and JioHotstar in July 2026.

## Why a Stand-Up Comic on a Stunt Show Matters

Indian stand-up comedy has spent a decade building itself into a genuine entertainment category — from basement shows at Canvas Laugh Club to Netflix specials and sold-out arena tours. But comedians have historically stayed in their lane: stage, podcasts, maybe a web series. Harsh Gujral's crossover into stunt-based reality TV is a signal that the Indian comedy ecosystem has matured enough for its stars to be cast alongside television's biggest names as equals, not comic relief.

In a pre-show interview with Bollywood Bubble, Gujral said stand-up is "as risky as performing stunts" — a comparison that any comedian who has workshopped a new five-minute set in front of a hostile audience at 11 PM would quietly agree with. He also admitted to pausing his live tour entirely to commit to the Cape Town shoot, which for a touring comic represents a significant income sacrifice.

## The NRI Watch

KKK has always had a diaspora following, but the dynamics have shifted. JioHotstar's international rollout means NRIs can now watch episodes the same day they air in India — no more waiting for YouTube clips or dodgy streaming sites. For Indian students and young professionals abroad who grew up watching Rohit Shetty blow up cars in *Golmaal* and *Singham*, KKK is comfort television with an adrenaline upgrade.

Harsh Gujral's inclusion specifically resonates with the NRI comedy circuit. His material — middle-class ambitions, family pressure, the gap between Indian expectations and modern reality — plays just as well in a New Jersey community centre as it does in a Mumbai auditorium. The diaspora audience that discovered Indian stand-up through YouTube and podcasts during the pandemic now gets to see one of their favourites attempt something completely outside his skill set. That is either inspiring or hilarious, and probably both.

## The Full Cast

Beyond Gujral, the confirmed contestants include Gaurav Khanna (fresh off his Bigg Boss 19 win), Rubina Dilaik (returning for a second round), Jasmin Bhasin, Avika Gor, Rithvik Dhanjani, Farrhana Bhatt, Karan Wahi, and Orry (Orhan Awatramani, the social media personality whose presence on any reality show guarantees at least three trending hashtags). The mix of television veterans, social media stars, and a stand-up comedian suggests Colors is trying to broaden KKK's appeal beyond the traditional TV audience.

The show is expected to wrap filming by late May and premiere in the first week of July. Given Rohit Shetty's track record, expect at least one contestant to question their life choices while dangling from a bridge in the Western Cape.

*Khatron Ke Khiladi 15* will air on Colors TV and stream on JioHotstar. International streaming schedule to be confirmed."""

article3 = {
    "headline": "Harsh Gujral Traded Punchlines for Parachutes — Here's Why India's Funniest Stand-Up Comic Is Now Dangling Off a Bridge in Cape Town",
    "subheadline": "The comedian joins 'Khatron Ke Khiladi 15' alongside Gaurav Khanna, Rubina Dilaik, and Orry — and the NRI comedy fanbase is already placing bets on how long he lasts",
    "body": kkk_body.strip(),
    "diaspora_angle": "Harsh Gujral's stand-up material resonates strongly with NRI audiences who discovered Indian comedy through YouTube during the pandemic. JioHotstar's international rollout means diaspora viewers can now watch KKK same-day.",
    "vertical": "culture",
    "category": "entertainment",
    "tags": ["Khatron Ke Khiladi 15", "Harsh Gujral", "Rohit Shetty", "stand-up comedy", "reality TV", "Colors TV", "JioHotstar", "Cape Town", "Indian television", "NRI"],
    "urgency": "standard",
    "sources": ["Possible11", "Bollywood Bubble", "Bombay Times", "Bhaskar English"],
    "slug": "harsh-gujral-khatron-ke-khiladi-15-stand-up-reality-tv-20260518",
    "word_count": 660,
    "status": "published",
    "published_at": now,
    "score_total": 72,
    "topic_id": "a478d380-35ca-411e-bb42-19c8f2a7e6b2"
}

a3_id = insert_article(article3)

# ══════════════════════════════════════════════════════════════════
# MARK TOPICS
# ══════════════════════════════════════════════════════════════════
print("\n=== MARKING TOPICS ===")

# KKK15 topic → published
update_topic("a478d380-35ca-411e-bb42-19c8f2a7e6b2", "published")

# Raaj Kumar nostalgia → reject (low news value, no fresh angle)
update_topic("fd71214d-7e42-4c5f-abbe-e134b0ff61d7", "rejected")

# HBO Lanterns → reject (Western, no India angle)
update_topic("64e82d6e-17f4-4981-a113-d9d6c6ced7f9", "rejected")

# The Mummy → reject (Western, no India angle)
update_topic("19a8b673-7b30-414b-94be-70e1a0675222", "rejected")

# South Korean 'Hope' at Cannes → reject (no India angle)
update_topic("c6dfff03-1782-46e1-b893-254f74370eda", "rejected")

# ══════════════════════════════════════════════════════════════════
# SCORE DECAY
# ══════════════════════════════════════════════════════════════════
print("\n=== SCORE DECAY ===")
# Decay scores for entertainment articles older than 48h
r = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?category=eq.entertainment&status=eq.published&select=id,score_total,published_at",
    headers={k: v for k, v in HEADERS.items() if k != "Prefer"}
)
if r.status_code == 200:
    articles = r.json()
    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
    decayed = 0
    for a in articles:
        if not a.get("published_at"):
            continue
        pub = datetime.fromisoformat(a["published_at"].replace("Z", "+00:00"))
        if pub < cutoff and a.get("score_total", 0) > 30:
            age_days = (datetime.now(timezone.utc) - pub).days
            decay = min(age_days * 3, 30)  # max 30-point decay
            new_score = max(a["score_total"] - decay, 20)
            if new_score != a["score_total"]:
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{a['id']}",
                    headers=HEADERS,
                    json={"score_total": new_score}
                )
                decayed += 1
    print(f"  Decayed {decayed} articles")
else:
    print(f"  Decay query failed: {r.status_code}")

print("\n=== DONE ===")
print(f"Articles created: {[a1_id, a2_id, a3_id]}")
