#!/usr/bin/env python3
"""Entertainment writer — May 25 2026, 07:30 UTC batch:
1. Ramayana preponed to October 30 + ₹450Cr distribution rights war
2. Aryan Khan's 'The Ba***ds of Bollywood' wins at Screenwriters Association Awards 2026
3. Rashmika Mandanna presents at Crunchyroll Anime Awards 2026 in Tokyo
+ Score decay for older entertainment articles
"""

import json, os, uuid, requests
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

now = datetime.now(timezone.utc)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S")
articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Ramayana Preponed + ₹450 Crore Distribution War
# ══════════════════════════════════════════════════════════════
slug1 = "ramayana-prepone-october-30-diwali-450-crore-distribution-rights-ranbir-kapoor-20260525"
if not check_duplicate(slug1):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Ramayana Won't Release on Diwali. It's Coming a Week Earlier. And the Fight Over Its Distribution Rights Has Become the Biggest Deal in Hindi Cinema History.",
        "subheadline": "Producer Namit Malhotra wants ₹450 crore for the Hindi theatrical rights alone — a number that has left veteran distributors stunned. The plan: release October 30, let word-of-mouth build, and let Diwali do the rest. For NRIs, the trailer drops at San Diego Comic-Con in July.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "developing",
        "status": "published",
        "published_at": now_iso,
        "score_total": 82,
        "tags": ["Ramayana", "Ranbir Kapoor", "Yash", "Sai Pallavi", "Sunny Deol", "Nitesh Tiwari", "Namit Malhotra", "Diwali 2026", "Hans Zimmer", "AR Rahman", "DNEG", "distribution rights", "Comic-Con"],
        "diaspora_angle": "The Ramayana isn't just a film for the Indian diaspora — it's a cultural event. For NRIs who have spent years explaining the epic to friends and colleagues abroad, a $200 million Hollywood-grade production starring Ranbir Kapoor as Lord Ram is both validation and anxiety: will it do the story justice? The trailer debuts at San Diego Comic-Con in July, making it the first Indian film to use that global stage. The October 30 release means NRIs can watch it opening weekend and discuss it over Diwali gatherings. And the ₹450 crore distribution ask signals that the makers believe this can be the biggest Indian film ever made.",
        "sources": [
            {"url": "https://www.bollywoodhungama.com/news/bollywood/namit-malhotra-contemplating-a-masterstroke-to-prepone-ramayana-to-october-30-2026-a-week-before-diwali/", "name": "Bollywood Hungama"},
            {"url": "https://www.mensxp.com/entertainment/bollywood/183845-namit-malhotra-seeks-rs-450-crore-for-ramayana-distributions.html", "name": "MensXP"},
            {"url": "https://sacnilk.com/articles/Nitesh-Tiwaris-Ramayana-Eyes-July-Trailer-Debut-At-San-Diego-Comic-Con", "name": "Sacnilk"},
            {"url": "https://www.iwmbuzz.com/movies/news-movies/vying-validation-why-does-namit-malhotra-need-so-much-pr-for-ramayana/2026/05/23", "name": "IWMBuzz"}
        ],
        "image_search_query": "Ramayana film 2026 Ranbir Kapoor Sai Pallavi Nitesh Tiwari teaser",
        "image_entities": ["Ranbir Kapoor", "Ramayana", "Nitesh Tiwari", "Yash"],
        "image_must_show": "Ramayana film poster or Ranbir Kapoor as Lord Ram",
        "word_count": 800,
        "body": """The most anticipated Indian film in a generation won't arrive on the date everyone expected. It's coming earlier.

Namit Malhotra, the producer behind *Ramayana: Part One*, is planning to release the Nitesh Tiwari-directed epic on **October 30, 2026** — a full week before Diwali — in what industry insiders are calling a strategic masterstroke designed to let the film build unstoppable word-of-mouth before India's biggest festival weekend.

And the business side? It's already historic. Malhotra is reportedly seeking **₹450 crore** for the Hindi theatrical distribution rights alone — a figure that would shatter every previous record in Indian cinema and has left some of the industry's most experienced distributors publicly hesitant.

## The October 30 Strategy

The logic is elegant. Most Diwali releases depend on a massive opening day fuelled by holiday footfall. Malhotra wants something different: a film that opens strong in its first week, generates overwhelming positive word-of-mouth, and then *peaks* during the Diwali holiday period in its second week.

"Namit Malhotra wants the film to establish itself before the Diwali period," a source told Bollywood Hungama. "He wants the word of mouth to spread all across, so that the business peaks in the second week."

If it works, *Ramayana* wouldn't just be a Diwali release — it would *own* Diwali. The strategy mirrors what the biggest Hollywood tentpoles do: open before a holiday, let the holiday amplify the wave.

## ₹450 Crore: The Number That Stunned the Industry

The distribution rights negotiation has become its own drama. According to Variety India and multiple trade sources, Malhotra is seeking approximately ₹450 crore solely for the Hindi theatrical rights — a figure being described as unprecedented.

For context, the biggest known Hindi distribution deal to date is Shah Rukh Khan's *King*, whose rights were reportedly acquired by Pen Marudhar for approximately ₹250 crore. The *Ramayana* ask is nearly double that.

Major distributors including Dharma Productions, AA Films, and Pen Studios are reportedly in discussions. But industry veterans like Anil Thadani and Jayantilal Gada are said to have reservations about the commercial viability of such a deal, advising the makers to reconsider.

Malhotra, however, is reportedly standing firm — believing the figure accurately reflects the film's scale, its global appeal, and the cultural event it represents. Industry insiders suggest negotiations may accelerate after the next major promotional reveal.

## The Cast and the Scale

The numbers behind *Ramayana* are staggering by any standard:

- **Ranbir Kapoor** as Lord Ram
- **Yash** as Ravana
- **Sai Pallavi** as Goddess Sita
- **Sunny Deol** as Lord Hanuman
- Directed by **Nitesh Tiwari** (*Dangal*, *Chhichhore*)
- Score by **Hans Zimmer** and **A.R. Rahman**
- VFX by 8-time Oscar-winning **DNEG** (Christopher Nolan's go-to studio)
- Budget reportedly exceeding **₹1,600 crore** for both parts
- Produced by Malhotra's Prime Focus Studios with Yash's Monster Mind Creations

The two-part structure mirrors global franchise strategy: Part 1 hits Diwali 2026, Part 2 targets Diwali 2027.

## Comic-Con and the Global Play

Here's where it gets interesting for the diaspora: *Ramayana* is reportedly eyeing a **full trailer debut at San Diego Comic-Con in July 2026**. If confirmed, it would be the first Indian film to use that global pop-culture stage for a major reveal — placing it alongside Marvel, DC, and Star Wars in the conversation.

For NRIs, Comic-Con isn't an obscure industry event. It's where your American colleagues and friends discover what they'll be watching for the next year. An Indian mythological epic standing shoulder-to-shoulder with Hollywood's biggest franchises on that stage would be a cultural moment the diaspora has been waiting for.

## Why NRIs Should Pay Attention Now

The October 30 release date means something specific for the diaspora: *Ramayana* will be in theatres during the week NRI families are already gathering for Diwali. It transforms from a film you go see into a film your family experiences together — the kind of shared cultural moment that defines how the diaspora relates to India.

The Hans Zimmer and A.R. Rahman collaboration alone is designed for global audiences. Zimmer's involvement signals that this isn't being positioned as an Indian film that happens to play abroad — it's being built as a global event that happens to be Indian.

## What Could Go Wrong

The ₹450 crore ask is a double-edged sword. If distributors balk and the deal closes significantly lower, it could be read as a vote of no-confidence from the very people who know the market best. The IWMBuzz editorial asking "Why does Namit Malhotra need so much PR for Ramayana?" reflects a growing undercurrent of scepticism about whether the film's marketing has outpaced its substance.

The teaser, while visually impressive, drew mixed reactions for its VFX quality. Malhotra publicly acknowledged the feedback and promised adjustments — but in the age of social media, first impressions linger.

Still, no one in the industry doubts the film's commercial potential. The question is whether it can match the nearly impossible expectations it has set for itself. October 30 is five months away. The countdown has begun.""",
    })
    print(f"✅ Article 1 prepared: {slug1}")
else:
    print(f"⚠️ DUPLICATE: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Aryan Khan Wins at Screenwriters Association Awards
# ══════════════════════════════════════════════════════════════
slug2 = "aryan-khan-bastards-bollywood-screenwriters-association-awards-2026-srk-20260525"
if not check_duplicate(slug2):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Shah Rukh Khan's Son Just Won Two Screenwriting Awards. Not for Being Shah Rukh Khan's Son. For Writing the Sharpest Satire Bollywood Has Produced in Years.",
        "subheadline": "Aryan Khan's Netflix debut 'The Ba***ds of Bollywood' took Best Screenplay and Best Dialogue at the Screenwriters Association Awards 2026. The show that mocks the film industry just got validated by the film industry's own writers.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 74,
        "tags": ["Aryan Khan", "Shah Rukh Khan", "The Bastards of Bollywood", "Netflix", "Screenwriters Association Awards", "Bobby Deol", "Lakshya", "Bilal Siddiqi", "Black Warrant"],
        "diaspora_angle": "For NRIs, Aryan Khan's story carries a weight that goes beyond industry gossip. This is the kid who was arrested in a drugs case in 2021 — an event that dominated NRI WhatsApp groups and dinner table debates for months. Three years later, he's winning writing awards. The show itself — a satire about Bollywood's power structures, nepotism, and manipulation — is streaming on Netflix internationally, and its self-aware treatment of exactly the privilege Aryan was born into has made it one of the most-discussed Hindi shows among diaspora audiences.",
        "sources": [
            {"url": "https://www.devdiscourse.com/article/politics/3920112-black-warrant-aryan-khans-the-bads-of-bollywood-win-big-at-saa-2026", "name": "Devdiscourse"},
            {"url": "https://en.wikipedia.org/wiki/The_Ba***ds_of_Bollywood", "name": "Wikipedia"},
            {"url": "https://www.whosthat360.com/influencer-news/samay-raina-praises-aryan-khans-the-bastards-of-bollywood", "name": "WhosThat360"}
        ],
        "image_search_query": "Aryan Khan The Bastards of Bollywood Netflix 2026",
        "image_entities": ["Aryan Khan", "Shah Rukh Khan", "Bobby Deol", "The Ba***ds of Bollywood"],
        "image_must_show": "Aryan Khan or The Bastards of Bollywood series poster",
        "word_count": 720,
        "body": """At the 7th Screenwriters Association Awards held Saturday in Mumbai, the show that won Best Screenplay and Best Dialogue in the Web Comedy/Musical/Romance category wasn't a safe, crowd-pleasing comedy. It was a razor-sharp satire about everything wrong with the Bollywood industry — written by the son of its biggest star.

*The Ba***ds of Bollywood*, Aryan Khan's directorial and writing debut on Netflix, took home two of the ceremony's most prestigious writing awards. The Best Screenplay award was shared by Khan, Bilal Siddiqi, and Manav Chauhan. The Best Dialogue award went to Aryan Khan alone.

## What the Show Is About

Released on Netflix in 2025, *The Ba***ds of Bollywood* follows Aasmaan Singh (played by Lakshya), a young actor navigating Bollywood's treacherous landscape of producers, power brokers, and family dynasties. Bobby Deol plays the charismatic but ruthless producer Freddy Sodawallah, and the plot revolves around the collision between Aasmaan's ambitions and the industry's entrenched power structures.

The show is, in essence, a satire of the very world Aryan Khan was born into. It doesn't flinch from depicting nepotism, manipulation, the casting couch culture, and the toxic dynamics between talent and money. That it was written by someone who grew up inside those dynamics gives it an authenticity that outsiders couldn't replicate.

## The Awards Night

The Screenwriters Association Awards, while not as flashy as Filmfare or IIFA, carry a different kind of weight. These are awards given by writers to writers — the people who understand craft, structure, and dialogue at a technical level. The ceremony was attended by some of Bollywood's most respected creative minds: Sooraj Barjatya, Sriram Raghavan, Shoojit Sircar, Ashutosh Gowariker, Sujoy Ghosh, Tigmanshu Dhulia, Ramesh Sippy, Kiran Rao, and R. Balki, among others.

Other winners included Vikramaditya Motwane's *Black Warrant*, which won Web Drama Best Screenplay (Satyanshu Singh and Arkesh Ajay) and TV/Web Best Lyrics (Anvita Dutt for "Naseeba"). Sudip Sharma and Abhishek Banerjee's *Paatal Lok Season 2* won Web Drama Best Screenplay alongside others.

## The Aryan Khan Arc

It's impossible to discuss Aryan Khan's career without acknowledging the 2021 drugs-on-a-cruise case that dominated headlines for months. He was eventually cleared — the NCB found no drugs on him, no evidence of consumption, and all charges were dropped. But the damage to public perception was real, especially in NRI communities where the case was debated endlessly on WhatsApp groups and at dinner tables.

The pivot from that moment to this one — winning peer-voted writing awards for a show that satirises the very industry that treated his arrest as entertainment content — is a narrative arc that fiction would struggle to improve upon.

And the reviews back it up. Comedian Samay Raina publicly praised the show, calling it "so edgy and funny" and "pure menace." The audience response on Netflix has been strong enough to generate conversation about a second season.

## What NRIs Are Watching

For diaspora audiences, *The Ba***ds of Bollywood* works on multiple levels. On the surface, it's a slick, entertaining industry satire with Bobby Deol delivering another villainous turn. Beneath that, it's a show written by someone who understands the absurdity of Bollywood's power dynamics from the inside — and has the audacity to put it on screen.

The fact that the industry's own writers' body has now validated that work is significant. It's one thing for Netflix viewers to enjoy the show. It's another for the screenwriting community — people who know what good dialogue sounds like, who understand structure, who can tell the difference between sharp writing and celebrity branding — to hand it two awards.

## The Bigger Picture

Aryan Khan is 28. This is his first project. If the writing awards are any indication, he has inherited something more valuable than his father's fame: an ability to observe the world he grew up in with honesty and convert that observation into compelling storytelling.

For NRIs who watched the 2021 case unfold with a mix of sympathy and judgement, this is worth noting: the story didn't end where the headlines stopped. It continued, quietly, into a writers' room — and now it's on a stage, holding two awards.""",
    })
    print(f"✅ Article 2 prepared: {slug2}")
else:
    print(f"⚠️ DUPLICATE: {slug2}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 3: Rashmika Mandanna at Crunchyroll Anime Awards
# ══════════════════════════════════════════════════════════════
slug3 = "rashmika-mandanna-crunchyroll-anime-awards-2026-tokyo-india-global-soft-power-20260525"
if not check_duplicate(slug3):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Rashmika Mandanna Just Presented an Award at Tokyo's Anime Awards Ceremony. Next to The Weeknd, RZA, and Winston Duke. Nobody in India Is Talking About What This Actually Means.",
        "subheadline": "The Crunchyroll Anime Awards 2026 invited India's biggest pan-cinema star to present alongside global pop culture icons. For the diaspora, this is the soft power crossover moment Indian entertainment has been waiting for.",
        "slug": slug3,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 72,
        "tags": ["Rashmika Mandanna", "Crunchyroll", "Anime Awards 2026", "Tokyo", "The Weeknd", "RZA", "Winston Duke", "Prabal Gurung", "soft power", "pan-India", "anime", "DAN DA DAN", "Demon Slayer"],
        "diaspora_angle": "For NRI parents, this is the intersection they didn't see coming: Indian cinema and anime culture. Their kids watch DAN DA DAN and Demon Slayer. They watch Rashmika in Pushpa. Now both worlds share a stage. Rashmika wearing Indian-diaspora designer Prabal Gurung while presenting at a Japanese ceremony alongside The Weeknd is the kind of cross-cultural moment that makes the diaspora's position between cultures feel like a superpower, not a compromise.",
        "sources": [
            {"url": "https://bleedingcool.com/tv/crunchyroll-anime-awards-2026-your-viewing-guide-to-animes-big-night/", "name": "Bleeding Cool"},
            {"url": "https://bleedingcool.com/tv/crunchyroll-anime-awards-2026-my-hero-academia-demon-slayer-score/", "name": "Bleeding Cool"},
            {"url": "https://www.crunchyroll.com/animeawards", "name": "Crunchyroll"}
        ],
        "image_search_query": "Rashmika Mandanna Anime Awards 2026 Tokyo Prabal Gurung gown",
        "image_entities": ["Rashmika Mandanna", "Crunchyroll Anime Awards", "Tokyo"],
        "image_must_show": "Rashmika Mandanna at the Crunchyroll Anime Awards ceremony in Tokyo",
        "word_count": 740,
        "body": """On May 23, at the Grand Prince Hotel Shin Takanawa in Tokyo, Rashmika Mandanna walked onto a stage alongside The Weeknd, Wu-Tang Clan founder RZA, *Black Panther* star Winston Duke, and K-pop artist BamBam. She was there to present an award at the 10th annual Crunchyroll Anime Awards — the biggest night in global anime culture.

The Indian entertainment industry barely noticed. Social media covered the Prabal Gurung gown. Almost nobody covered what the invitation itself signifies.

## What the Anime Awards Actually Are

The Crunchyroll Anime Awards are anime's Oscars equivalent — voted on by a global panel of judges and millions of fans worldwide, broadcast live from Tokyo across Twitch, TikTok, and YouTube. This year's ceremony featured the Tokyo Philharmonic Orchestra performing symphonic anime suites, a 30th anniversary tribute to *Neon Genesis Evangelion*, and winners including *DAN DA DAN*, *Demon Slayer: Infinity Castle*, *Solo Leveling*, and *My Hero Academia*.

The presenters list reads like a cultural power index: **The Weeknd** (one of the world's biggest musicians), **RZA** (legendary hip-hop producer and filmmaker), **Winston Duke** (M'Baku from Marvel's *Black Panther*), **BamBam** (Thai K-pop star), and **Rashmika Mandanna** — described by Crunchyroll as a "prominent pan-India star."

That description alone is worth parsing. Crunchyroll didn't invite a Bollywood star. They invited a pan-India star — someone whose appeal crosses Telugu, Kannada, and Hindi markets. The distinction matters because anime's global audience doesn't map neatly onto Bollywood's traditional overseas market. It maps onto the broader Indian cultural consumer: younger, multilingual, platform-agnostic.

## Why Rashmika?

Rashmika Mandanna is, at this point, one of the most commercially successful actresses working in Indian cinema. *Pushpa: The Rise* and *Animal* made her a household name across language markets. She has a massive social media following that spans demographics. And crucially, she's associated with the kind of mass-appeal, high-energy storytelling that anime fans instinctively recognise.

The invitation suggests that Crunchyroll's audience strategy team identified India as a key growth market — and chose a representative who embodies the overlap between Indian blockbuster culture and anime's global fanbase.

## The Soft Power Nobody Is Discussing

Here's what makes this moment significant beyond celebrity appearances: **Indian pop culture representation on the global anime stage is new.** Anime's cultural ecosystem has traditionally been dominated by Japanese creators, American consumers, and K-pop crossover. The inclusion of an Indian star as a presenter — not as a guest, not as a brand ambassador, but as a peer alongside RZA and The Weeknd — is a signal that India's entertainment industry is being recognised as part of the global pop-culture conversation in spaces beyond traditional film.

This is the kind of soft power that doesn't show up in box office numbers or streaming metrics. It shows up in cultural legitimacy — in the idea that an Indian actress belongs on the same stage as a Grammy-winning artist at a ceremony celebrating Japanese animation in a Tokyo hotel.

For the diaspora, this matters in ways that are hard to quantify but easy to feel. NRI kids who watch anime and Indian cinema often experience those as separate cultural identities. Seeing Rashmika on the Anime Awards stage — in a Prabal Gurung gown, no less (Gurung is Nepali-American, another South Asian diaspora story) — collapses that distance.

## The Prabal Gurung Detail

The fashion choice deserves its own paragraph. Prabal Gurung is a Nepali-born, New York-based designer who has dressed Michelle Obama, Kamala Harris, and countless red-carpet regulars. He is one of the most prominent South Asian designers in Western fashion. Rashmika wearing Gurung at a Japanese ceremony signals something deliberate: this was a moment curated for global impact, not domestic PR.

## What's Next

Rashmika's Anime Awards appearance comes as India's anime market is expanding rapidly. Crunchyroll has been investing in Hindi dubbing for top titles, and anime conventions in India are growing in attendance. The next *Demon Slayer* film and *DAN DA DAN Season 3* will likely have significant Indian theatrical runs.

For Indian cinema, the opportunity is to reciprocate: bring anime sensibilities into Indian storytelling, collaborate across industries, and build on the cultural bridge that Rashmika just walked across in a Prabal Gurung gown in Tokyo.

The diaspora is already living in that intersection. The industry is just catching up.""",
    })
    print(f"✅ Article 3 prepared: {slug3}")
else:
    print(f"⚠️ DUPLICATE: {slug3}")


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
# UPDATE TOPIC STATUSES
# ══════════════════════════════════════════════════════════════
print("\n── Updating Topic Statuses ──")

# Mark Aryan Khan topic as published
sb_patch("p2_topics", "id=eq.0bbb6a93-0eb1-4217-b360-bd4ce8b562cc", {"status": "published"})
print("✅ Aryan Khan SAA topic → published")

# Mark Rashmika Anime Awards topic as published
sb_patch("p2_topics", "id=eq.0a70c76d-8d93-4afc-a478-33b11ddf1fd5", {"status": "published"})
print("✅ Rashmika Anime Awards topic → published")

# Mark Aishwarya Cannes look topic as rejected (too many Cannes articles already)
sb_patch("p2_topics", "id=eq.13943308-c8a1-4461-9512-27e733e8cef7", {"status": "rejected"})
print("✅ Aishwarya Cannes look → rejected (coverage saturation)")

# Mark Ahsaas Channa Gudgudi Cannes topic as rejected (too niche)
sb_patch("p2_topics", "id=eq.f1ecc67d-832e-4ce8-a096-1d768f945f2f", {"status": "rejected"})
print("✅ Gudgudi Cannes → rejected (niche)")


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
