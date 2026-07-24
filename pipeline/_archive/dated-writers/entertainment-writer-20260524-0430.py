#!/usr/bin/env python3
"""Entertainment writer — May 24 2026, 04:30 PDT batch:
1. Bobby Deol's Bandar — Anurag Kashyap's TIFF-premiered crime thriller, June 5 release
2. Patriot — Mammootty + Mohanlal's spy thriller heads to ZEE5 June 5 after ₹80Cr box office
3. Score decay for old entertainment articles
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

def check_duplicate(slug):
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id",
        headers=HEADERS, timeout=15
    )
    return len(r.json()) > 0 if r.status_code == 200 else False

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Bandar — Bobby Deol + Anurag Kashyap Crime Thriller
# ══════════════════════════════════════════════════════════════
slug1 = "bobby-deol-bandar-anurag-kashyap-tiff-crime-thriller-june-5-20260524"
if not check_duplicate(slug1):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Bobby Deol Plays a Fading Star Accused of Rape in Anurag Kashyap's 'Bandar.' It Premiered at TIFF. It Releases June 5. NRIs Who Grew Up on His 90s Films Won't Recognise Him.",
        "subheadline": "The film — inspired by a real-life event, written by Sudip Sharma, and featuring Sanya Malhotra and Saba Azad — marks Bobby Deol's first solo theatrical lead in 17 years. The internet calls him 'Lord Bobby.' Kashyap is about to show you why.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "developing",
        "status": "published",
        "published_at": now,
        "score_total": 80,
        "tags": ["Bobby Deol", "Bandar", "Anurag Kashyap", "TIFF", "Sanya Malhotra", "Saba Azad", "Zee Studios", "crime thriller"],
        "diaspora_angle": "For NRIs who grew up watching Bobby Deol in Soldier and Gupt, his transformation from 90s heartthrob to internet meme to genuinely terrifying screen presence is one of the great redemption arcs in Indian pop culture. Bandar, which premiered at TIFF in September 2025 and releases worldwide on June 5, is the culmination of that arc — a film where the actor the diaspora remembers as a harmless romantic lead plays a morally compromised man accused of sexual assault.",
        "sources": [
            {"url": "https://www.bollywoodhungama.com/news/bollywood/exclusive-bobby-deol-takes-a-break-from-uk-for-bandar-promotions-ahead-of-release/", "name": "Bollywood Hungama"},
            {"url": "https://en.wikipedia.org/wiki/Bandar_(film)", "name": "Wikipedia"},
            {"url": "https://variety.com/2025/film/news/anurag-kashyaps-monkey-in-a-cage-metoo-bobby-deol-1236167895/", "name": "Variety"},
            {"url": "https://www.filmfare.com/news/bobby-deol-bandar-anurag-kashyap-trailer", "name": "Filmfare"}
        ],
        "image_search_query": "Bobby Deol Bandar Anurag Kashyap 2026 trailer poster",
        "image_entities": ["Bobby Deol", "Anurag Kashyap", "Bandar"],
        "image_must_show": "Bobby Deol from the Bandar trailer or poster, or at a promotional event",
        "word_count": 780,
        "body": """There is an alternate timeline where Bobby Deol's career ended sometime around 2010. The 90s heartthrob, the man who made an entire generation of Indian women lose their composure in *Soldier* and *Gupt*, had faded so completely that he became an internet punchline. 'Lord Bobby' memes. Bobby Deol DJ sets played to empty rooms. Bobby Deol as the answer to the question: what happens when Bollywood forgets you?

Then *Animal* happened. And suddenly, Bobby Deol — silent, menacing, utterly unrecognisable — was the most talked-about villain in Indian cinema. Now, with *Bandar*, he goes even further.

## What 'Bandar' Is About

Directed by Anurag Kashyap and written by Sudip Sharma and Abhishek Banerjee, *Bandar* (the international title is *Monkey in a Cage*) follows Sameer Mehra, a fading television star whose fame is slipping. He's in a new relationship with a younger woman named Khushi, played by Saba Azad, when his ex-girlfriend Gayatri — played by Sapna Pabbi — re-enters his life. Instead of engaging, Sameer cuts off all contact and blocks her.

Then Gayatri accuses him of rape.

What follows, according to both the trailer and the TIFF screening reviews, is a deeply uncomfortable film about power, consent, entitlement, and a legal system that may or may not be interested in the truth. This is not a film that tells you who to root for. This is Anurag Kashyap at his most morally corrosive.

The ensemble cast includes Sanya Malhotra as Sameer's sister, Indrajith Sukumaran, Raj B. Shetty, Jitendra Joshi, Riddhi Sen, and Joju George. The film is distributed by Zee Studios and produced by Nikhil Dwivedi's Saffron Magicworks.

## The TIFF Factor

*Bandar* premiered in the Special Presentations programme at the 2025 Toronto International Film Festival on September 6. Variety's review noted that Bobby Deol "totally put his whole vulnerable self out there" — a remarkable sentence about an actor who spent two decades being dismissed as the least talented Deol brother.

TIFF premieres carry weight in the diaspora. For NRIs in Toronto, New York, London, and the Bay Area, a TIFF stamp means a film has been vetted by the world's most discerning festival audience. It's also the reason many diaspora viewers will walk into *Bandar* with higher expectations than a typical Bollywood release — and Kashyap, whose *Gangs of Wasseypur* remains a cult classic among NRIs, knows exactly how to meet them.

## Bobby Deol's First Solo Lead in 17 Years

Here's a statistic that puts Bobby Deol's career in perspective: *Bandar* is his first solo theatrical lead since *Naqaab* in 2007. Seventeen years. In that time, he appeared in forgettable multi-starrers, did a few OTT projects, and was essentially written off by an industry that runs on opening weekends.

What changed everything was his willingness to play villains — and not the moustache-twirling kind. In *Animal*, he barely spoke. His menace came from stillness. In *Bandar*, the threat is different: it's a man who might be guilty, might be innocent, and is definitely incapable of understanding why the world has changed around him.

Bobby flew back from a UK shoot specifically for *Bandar* promotions. His brother Sunny Deol posted a hyped Instagram reaction to the trailer. The entire Deol family machinery is behind this one.

## Why This Film Matters Beyond the Box Office

*Bandar* is inspired by a real-life event — the film doesn't specify which one, but the parallels to India's ongoing reckoning with #MeToo in the entertainment industry are impossible to ignore. Kashyap himself was accused during India's #MeToo wave in 2018 (the case was closed after investigation). That he's now making a film about a celebrity accused of sexual assault is either extraordinary courage or extraordinary provocation. Probably both.

For NRI audiences, this resonates differently. The diaspora watched India's #MeToo movement unfold at a distance — close enough to care, far enough to feel helpless. A film that interrogates the mechanics of accusation, fame, and justice, made by a filmmaker with skin in the game and starring an actor whose entire career is a meditation on second chances, is the kind of work that generates conversation long after the credits roll.

## Mark Your Calendar

*Bandar* releases in theatres worldwide on June 5, 2026. It runs 140 minutes. The songs feature Amit Trivedi and Vishal Mishra. The score is by Shivahari Varma. And Bobby Deol, at 57, is about to remind the world that the most dangerous actors in Indian cinema aren't the ones who shout the loudest.

They're the ones who went quiet for 17 years and came back with something to prove."""
    })
else:
    print(f"⏭️  Skipping duplicate: {slug1}")

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Patriot — Mammootty + Mohanlal's Spy Thriller Heads to ZEE5
# ══════════════════════════════════════════════════════════════
slug2 = "patriot-mammootty-mohanlal-spy-thriller-zee5-june-5-box-office-disaster-20260524"
if not check_duplicate(slug2):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Mammootty and Mohanlal Made a ₹140 Crore Spy Thriller Together. It Lost Money in Theatres. Now It's Coming to ZEE5 on June 5 — and the Diaspora Might Be Its Real Audience.",
        "subheadline": "Patriot reunited Malayalam cinema's two biggest legends after 18 years. The box office didn't care. But Mahesh Narayanan's surveillance thriller — starring Fahadh Faasil, Nayanthara, and Kunchacko Boban — might find the global audience it always deserved on streaming.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "developing",
        "status": "published",
        "published_at": now,
        "score_total": 78,
        "tags": ["Patriot", "Mammootty", "Mohanlal", "ZEE5", "Malayalam cinema", "Mahesh Narayanan", "Fahadh Faasil", "Nayanthara", "spy thriller", "OTT"],
        "diaspora_angle": "The Kerala diaspora — spread across the Gulf, the US, the UK, Canada, and Australia — is arguably the most cinema-literate immigrant community in the world. For Malayali NRIs, a Mammootty-Mohanlal reunion isn't just a film event; it's a cultural event on the scale of a festival. Many diaspora viewers couldn't catch Patriot during its theatrical run. The ZEE5 release on June 5 gives them a second chance — and for a film about government surveillance, digital privacy, and whistleblowing, the global streaming audience might be more receptive than the Kerala multiplex crowd.",
        "sources": [
            {"url": "https://www.filmfare.com/news/south/mammootty-and-mohanlals-patriot-locks-ott-release-following-theatrical-run-84074.html", "name": "Filmfare"},
            {"url": "https://en.wikipedia.org/wiki/Patriot_(film)", "name": "Wikipedia"},
            {"url": "https://www.pinkvilla.com/entertainment/south/patriot-ott-release-when-and-where-to-watch-mammootty-mohanlals-spy-action-drama-online", "name": "Pinkvilla"},
            {"url": "https://sacnilk.com/movies/patriot-2026-review-rating-box-office", "name": "Sacnilk"}
        ],
        "image_search_query": "Patriot Malayalam film Mammootty Mohanlal 2026 poster",
        "image_entities": ["Mammootty", "Mohanlal", "Patriot", "Fahadh Faasil"],
        "image_must_show": "Patriot film poster or Mammootty and Mohanlal from the film",
        "word_count": 800,
        "body": """On paper, *Patriot* should have been the biggest Malayalam film of the decade. Mammootty and Mohanlal — the two titans of Kerala cinema, the men whose rivalry defined an entire generation of Indian moviegoing — reuniting on screen after 18 years. Directed by Mahesh Narayanan, who made *Take Off*, *CU Soon*, *Malik*, and *Ariyippu*. A cast that reads like a Malayalam cinema hall of fame: Fahadh Faasil, Kunchacko Boban, Nayanthara, Revathi.

Budget: ₹125-140 crore. The most expensive Malayalam film ever made.

Box office: approximately ₹75-80 crore worldwide. A disaster by any measure.

On June 5, *Patriot* begins streaming on ZEE5. And there's a strong argument that streaming is where this film was always meant to live.

## What Went Wrong in Theatres

*Patriot* released on May 1, 2026, and opened strongly — the Mammootty-Mohanlal reunion alone guaranteed packed houses on opening weekend across Kerala and in overseas markets with significant Malayali populations. The excitement was real. The two biggest superstars in the same frame, for the first time since *Twenty:20* in 2008.

But as word of mouth spread, the reception split. Critics gave it 3 to 3.5 stars. *The Indian Express* praised Narayanan for "not being intimidated by the superstardom" but noted that "the script ultimately falls flat." *The Hindu* called it "engaging and even brave" but "predictable." *India Today* gave it 3.5 stars, saying it was "spy cinema done right — minor shortcomings and all."

The problem wasn't quality. The problem was expectations. Audiences who walked in expecting a mass entertainer — two superstars trading punchlines and beating up villains — got a three-hour surveillance thriller about government spyware, digital privacy, and whistleblowing. The pacing was deliberate. The politics were layered. The action, when it came, served the plot rather than the stars.

For a ₹140 crore film, that's a fatal mismatch between what was sold and what was delivered.

## Why Streaming Changes Everything

Here's the thing about *Patriot*: it's exactly the kind of film that plays better on a screen in your living room than in a multiplex on a Friday night. Its three-hour runtime, which felt punishing in a theatre with interval snack expectations, becomes a binge session on a Saturday afternoon. Its dense plot — involving a spyware programme called Periscope, a defence scientist played by Mammootty who becomes a YouTube whistleblower, and a tech billionaire played by Fahadh Faasil whose father orchestrated a military accident for political gain — rewards the pause-and-rewind viewer.

Mahesh Narayanan's previous film, *CU Soon*, was literally made for OTT. It was shot during COVID lockdown, told entirely through screens, and became one of the most acclaimed Indian films of 2020 on Amazon Prime Video. He understands how streaming audiences engage with complexity.

## The Cast Deserves a Second Look

Lost in the box office noise was the fact that *Patriot* contains several genuinely remarkable performances. Mammootty plays Dr. Daniel James with a restraint that's become rare in his filmography — no thundering dialogue, no heroic posturing, just a man slowly realising that the system he served has turned against him. Mohanlal, in what's essentially an extended cameo as Colonel Rahim Naik, brings quiet gravitas to a bedridden former military instructor who becomes the resistance's moral centre.

But the revelation is Fahadh Faasil as Shakthi Sundaram. He plays the tech billionaire villain as charming, intelligent, and deeply wounded — a man whose entire life was shaped by his father's political manipulation. It's the kind of antagonist performance that Indian cinema rarely allows: a villain you understand, even as you despise what he's doing.

Kunchacko Boban as Michael Devassy, Nayanthara as Daniel's ex-wife, Darshana Rajendran, and Revathi all contribute to what is genuinely one of the most stacked ensembles in Indian cinema this year.

## The Diaspora Angle Is Real

The Kerala diaspora is everywhere — the Gulf, Silicon Valley, the NHS, Toronto, Melbourne. And Malayali NRIs are, per capita, probably the most dedicated cinema audience in the world. They follow box office numbers the way other communities follow cricket scores.

Many of them missed *Patriot* in theatres. Malayalam films get limited screens in most US and UK cities, and a three-hour thriller with mixed word of mouth isn't an easy sell for a weeknight viewing. But on ZEE5, with subtitles, on their own schedule, in the comfort of their homes? That's a different proposition entirely.

There's also the subject matter. A film about government surveillance, abuse of digital infrastructure, and the courage required to blow the whistle on state power plays differently when you're watching from a democracy that's having its own conversations about data privacy, AI surveillance, and tech accountability. The Periscope spyware in *Patriot* is fictional. The anxieties it represents are not.

## The Streaming Date

*Patriot* begins streaming on ZEE5 on June 5, 2026, in Malayalam with subtitles in Hindi, English, Tamil, Telugu, and Kannada. If you have a ZEE5 subscription and three hours, this is worth your time — not because it's perfect, but because it's ambitious in ways that Indian cinema rarely attempts, and the performances alone justify the investment.

The box office said no. Streaming might say otherwise."""
    })
else:
    print(f"⏭️  Skipping duplicate: {slug2}")

# ══════════════════════════════════════════════════════════════
# INSERT ARTICLES
# ══════════════════════════════════════════════════════════════
inserted = 0
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ Inserted: {art['headline'][:80]}...")
        inserted += 1
    except Exception as e:
        print(f"❌ Failed to insert {art['slug']}: {e}")

print(f"\n📝 Inserted {inserted}/{len(articles)} articles")

# ══════════════════════════════════════════════════════════════
# SCORE DECAY — drop old entertainment articles
# ══════════════════════════════════════════════════════════════
print("\n📉 Running score decay for entertainment articles...")
cutoff_3d = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
cutoff_7d = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

# Articles older than 7 days: drop score significantly
code = sb_patch(
    "p2_articles",
    f"category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff_7d}&score_total=gt.40",
    {"score_total": 35}
)
print(f"  7d+ decay: HTTP {code}")

# Articles older than 3 days: moderate decay
code = sb_patch(
    "p2_articles",
    f"category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff_3d}&published_at=gte.{cutoff_7d}&score_total=gt.55",
    {"score_total": 50}
)
print(f"  3-7d decay: HTTP {code}")

print("\n✅ Entertainment writer batch complete!")
