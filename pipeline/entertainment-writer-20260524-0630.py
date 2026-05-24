#!/usr/bin/env python3
"""Entertainment writer — May 24 2026, 06:30 PDT batch:
1. Ramayana — AR Rahman + Hans Zimmer score, Comic-Con trailer, Oct 30 release eye
2. Farhan Akhtar vs Ranveer Singh — Don 3 FWICE dispute, ₹40Cr damages claim
3. Akshay Kumar's 'Samuk' — India's first alien sci-fi thriller with Hollywood creature team
+ Score decay for old entertainment articles
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
# ARTICLE 1: Ramayana — AR Rahman + Hans Zimmer, Comic-Con Trailer, Oct 30
# ══════════════════════════════════════════════════════════════
slug1 = "ramayana-ar-rahman-hans-zimmer-score-comic-con-trailer-oct-30-release-20260524"
if not check_duplicate(slug1):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "AR Rahman and Hans Zimmer Are Scoring the Same Film. It Stars Ranbir Kapoor as Lord Ram. The Trailer May Drop at San Diego Comic-Con. NRIs, This Is Your Diwali Blockbuster.",
        "subheadline": "Nitesh Tiwari's ₹4,000-crore Ramayana is eyeing an October 30 release — a week before Diwali — with a live orchestral event in October showcasing the historic Rahman-Zimmer collaboration. The teaser already has 18 million YouTube views.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "developing",
        "status": "published",
        "published_at": now,
        "score_total": 82,
        "tags": ["Ramayana", "AR Rahman", "Hans Zimmer", "Ranbir Kapoor", "Nitesh Tiwari", "Sai Pallavi", "Yash", "Comic-Con", "Diwali 2026"],
        "diaspora_angle": "For NRIs who grew up on Doordarshan's Ramayana and AR Rahman's soundtracks, this is a once-in-a-generation cultural event. A ₹4,000-crore Indian epic scored by both Rahman and Zimmer, debuting its trailer at San Diego Comic-Con — the same stage that launches Marvel and DC tentpoles — signals that Indian cinema is done asking for a seat at the global table. It's building its own.",
        "sources": [
            {"url": "https://www.sacnilk.com/news/_Nitesh_Tiwaris_Ramayana_Eyes_July_Trailer_Debut_At_San_Diego_ComicCon_Huge_Update_On_Ranbir_Kapoor_Yash_Sai_Pallavi_Starrer", "name": "Sacnilk"},
            {"url": "https://www.bollywoodhungama.com/news/bollywood/ramayana-part-1-eyes-october-30-2026-release/", "name": "Bollywood Hungama"},
            {"url": "https://www.midday.com/entertainment/bollywood/ramayana-comic-con-trailer-launch", "name": "Mid-Day"},
            {"url": "https://www.sacnilk.com/news/Ranbir_Kapoors_Rama_Teaser_From_Ramayana_Hits_18_Million_Views_On_YouTube_In_First_24_Hours", "name": "Sacnilk"}
        ],
        "image_search_query": "Ramayana 2026 Ranbir Kapoor teaser poster Nitesh Tiwari",
        "image_entities": ["Ranbir Kapoor", "Ramayana", "AR Rahman", "Hans Zimmer"],
        "image_must_show": "Ranbir Kapoor as Lord Ram from the Ramayana teaser, or AR Rahman/Hans Zimmer at a musical event",
        "word_count": 780,
        "topic_id": "fd48cb9b-964b-4a98-856e-7cbcc68de70e",
        "body": """Two Academy Award winners. One ancient epic. A trailer launch at the same convention that debuts Marvel tentpoles. And a budget that makes most Hollywood blockbusters look modest.

Nitesh Tiwari's *Ramayana* — the most expensive Indian film ever made at a reported ₹4,000 crore across two parts — is barrelling toward its release with a marketing strategy that screams global ambition. And at its heart is a musical collaboration that, on paper, shouldn't exist: AR Rahman and Hans Zimmer, composing together.

## The Rahman-Zimmer Score

Let that combination sink in. Rahman — the man who gave the world *Jai Ho*, *Roja*, and the soundtrack to every NRI's childhood — alongside Zimmer, the architect of *Inception*, *Interstellar*, and *The Dark Knight*. Together, scoring a cinematic retelling of the Ramayana.

According to multiple industry reports, the makers are planning a live orchestral event in October to unveil the score before the film's release. This isn't just a background music reveal — it's being positioned as a standalone cultural event, the kind of spectacle that turns a film soundtrack into a global moment.

For the Indian diaspora, this pairing carries enormous emotional weight. Rahman's music is the sound of home for millions of NRIs. Zimmer's is the sound of the biggest cinematic experiences of their adopted countries. Hearing them merge on a Ramayana score is the kind of cross-cultural moment that only happens once.

## Comic-Con and the Global Play

Here's where the ambition gets audacious. Producer Namit Malhotra and director Nitesh Tiwari are reportedly in advanced talks to premiere the full trailer at San Diego Comic-Con this July. If confirmed, *Ramayana* would share a stage with the biggest franchises in global entertainment.

This follows a successful focus group screening in Los Angeles, where an early cut reportedly received strong positive reactions from a diverse audience. The feedback has apparently convinced the team that the film can travel far beyond Indian audiences — that this is, in their view, India's answer to *Lord of the Rings*.

For NRIs in the US, a Comic-Con trailer launch means something specific: it means the studio believes American audiences will care. That's a bet worth watching.

## The Cast and Scale

The film stars Ranbir Kapoor as Lord Ram, Sai Pallavi as Sita, and KGF star Yash as Ravana — a casting combination that spans Bollywood, South Indian cinema, and the streaming generation. Sunny Deol plays Hanuman. Ravie Dubey is Laxman. Ranbir is reportedly playing a dual role: Lord Ram and Lord Parashurama.

The teaser, released on April 2, crossed 18 million YouTube views in 24 hours. Ranbir has confirmed both parts will have a combined runtime exceeding six hours, with Part 2 shooting already 50% complete.

The production is being handled by DNEG — the visual effects house behind *Dune*, *Tenet*, and *Blade Runner 2049*. The OTT rights for both parts were reportedly offered at ₹700 crore and rejected; the makers believe the film deserves at least ₹1,000 crore in digital alone.

## October 30: A Week Before Diwali

The latest reports suggest an October 30 release date — a strategic move to build word-of-mouth before the Diwali holiday window kicks in. No other major Indian release is expected to compete during this period, giving *Ramayana* a clear runway for what could be a historic box office run.

For diaspora audiences, this means planning your Diwali around a cinema visit. In cities with significant Indian populations — the Bay Area, New Jersey, London, Toronto, Sydney — expect premium-format screenings and community events.

## Why This Matters Beyond Entertainment

*Ramayana* isn't just a film. It's a test case for whether Indian cinema can produce a truly global spectacle on its own terms — not a Bollywood film hoping for crossover appeal, but a production conceived from day one as a worldwide event.

The fact that it's built on a story that billions already know, scored by composers who speak to both Indian and Western audiences, and debuting on a platform as American as Comic-Con, suggests the makers understand exactly what they're doing.

Whether it delivers remains to be seen. But the setup is historic. And for NRIs who've spent decades watching Indian cinema aspire to this level of global ambition, *Ramayana* feels like the moment it might actually arrive.

The trailer is expected at San Diego Comic-Con in July. The score event is planned for October. The film targets theatres worldwide on October 30, 2026."""
    })
else:
    print(f"⚠️  Skipping duplicate: {slug1}")

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Farhan Akhtar vs Ranveer Singh — Don 3 FWICE Dispute
# ══════════════════════════════════════════════════════════════
slug2 = "farhan-akhtar-ranveer-singh-don-3-fwice-dispute-40-crore-20260524"
if not check_duplicate(slug2):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Farhan Akhtar Has Filed a Formal Complaint Against Ranveer Singh Over Don 3. The Claim Is ₹40 Crore. FWICE Rules on Monday. Here's What Happened to the Most Cursed Franchise in Bollywood.",
        "subheadline": "Ranveer was announced as the new Don in 2023. He never filmed a scene. Now Farhan wants ₹40 crore in damages, Ranveer is reportedly offering a stake in his next film instead, and the entire industry is choosing sides.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "breaking",
        "status": "published",
        "published_at": now,
        "score_total": 78,
        "tags": ["Farhan Akhtar", "Ranveer Singh", "Don 3", "FWICE", "Bollywood dispute", "Excel Entertainment", "Kiara Advani"],
        "diaspora_angle": "The Don franchise is cultural currency for NRIs — from Amitabh's 1978 original to SRK's stylish reboot. Every Indian abroad has an opinion on who should play Don next. This public feud, with ₹40 crore on the line and a FWICE ruling expected tomorrow, is the kind of Bollywood drama that will dominate diaspora WhatsApp groups and dinner-table arguments.",
        "sources": [
            {"url": "https://www.zoomtventertainment.com/bollywood/farhan-akhtar-fwice-don-3-case-ranveer-singh-exit-article-154386645", "name": "Zoom TV"},
            {"url": "https://bharathorizon.com/entertainment/farhan-akhtar-files-complaint-against-ranveer-singh-over-don-3-exit/", "name": "Bharat Horizon"},
            {"url": "https://globalindiabroadcastnews.com/entertainment/farhan-akhtar-don-3-ranveer-singh-fwice", "name": "GIBN"},
            {"url": "https://www.hollywoodreporterindia.com/film/farhan-akhtar-don-3-interview-nothing-taken-for-granted", "name": "Hollywood Reporter India"}
        ],
        "image_search_query": "Farhan Akhtar Ranveer Singh Don 3 Bollywood",
        "image_entities": ["Farhan Akhtar", "Ranveer Singh", "Don 3"],
        "image_must_show": "Farhan Akhtar or Ranveer Singh, preferably in a formal or promotional setting",
        "word_count": 750,
        "topic_id": "60d8cc94-8819-4c0b-acb7-a8f6b5dc2f02",
        "body": """The Don franchise has always been about power, betrayal, and people making moves behind each other's backs. Turns out, the off-screen version is just as dramatic.

Farhan Akhtar — director of *Don* (2006) and *Don 2* (2011), and co-producer under Excel Entertainment — has filed a formal complaint with the Federation of Western India Cine Employees (FWICE) against Ranveer Singh, seeking ₹40 crore in damages after the actor walked away from *Don 3* before filming a single scene. FWICE has confirmed it will announce its decision at a press conference on Monday, May 25.

This is now officially the most expensive breakup in Bollywood that doesn't involve a wedding.

## How We Got Here

*Don 3* was announced in 2023 with Ranveer Singh replacing Shah Rukh Khan as the new Don — a casting choice that divided fans but excited the industry. Kiara Advani was confirmed as the female lead in 2024. Vikrant Massey was reportedly set to play the antagonist. The film was shaping up as one of Bollywood's most anticipated projects.

Then nothing happened. Shooting schedules were delayed repeatedly. By late 2025, reports began surfacing of creative differences between Ranveer and the filmmakers. In December 2025, Ranveer reportedly stepped away from the project entirely, choosing instead to prioritise his next film, tentatively titled *Pralay*.

The fallout was immediate. Kiara was reportedly replaced by Kriti Sanon due to personal circumstances. Rumours swirled that the makers had approached Hrithik Roshan as a replacement — which was swiftly denied, adding fuel to the speculation.

## The ₹40 Crore Question

Excel Entertainment's position is straightforward: they signed Ranveer, built a production around him, and his departure caused significant financial damage. The ₹40 crore figure reportedly accounts for pre-production costs, opportunity costs, and contractual obligations.

Ranveer's camp has reportedly countered with a different proposal: rather than a cash settlement, Singh has offered Farhan and Ritesh Sidhwani a stake in *Pralay*, his upcoming film. The exact percentage hasn't been disclosed. An earlier report in the Free Press Journal suggested Ranveer had returned approximately ₹10 crore, but Excel's demand remains at the full ₹40 crore.

The complaint was filed through the Indian Film and Television Directors' Association (IFTDA), of which Farhan is a member. FWICE has taken it up and will review both sides before issuing its verdict.

## Why This Matters Beyond the Money

This isn't just a contract dispute. It's a test of how Bollywood handles star power versus producer rights in an era where actors increasingly control their careers.

For years, Indian stars have walked in and out of projects with minimal consequences. The informal nature of Bollywood deal-making — where announcements are made before contracts are fully locked — has meant that exits are messy but rarely litigated. Farhan taking this to FWICE signals a shift: producers are no longer willing to absorb the cost of a star's change of heart.

For NRI audiences who follow Bollywood closely, this also raises a nostalgic question: what happens to the Don franchise? The series — from Amitabh Bachchan's 1978 original to SRK's slick modern reboot — is one of Bollywood's most iconic properties. Every Indian abroad has an opinion on who should play Don. Ranveer seemed like a bold, exciting choice. His exit leaves the franchise in limbo.

Speaking to *The Hollywood Reporter India*, Farhan was philosophical: "Nothing can be taken for granted until you actually have it on film." He also hinted that the *Don 3* script isn't dead — just waiting for the right circumstances.

## What Happens Monday

FWICE's decision won't be legally binding in the way a court ruling would be, but it carries significant industry weight. Bollywood's informal power structures mean that a FWICE recommendation can influence future collaborations, studio relationships, and an actor's standing with producers.

If FWICE sides with Farhan, the pressure on Ranveer to settle increases substantially. If it sides with Ranveer — or proposes a compromise — it could set a precedent for how similar disputes are handled going forward.

Either way, Monday's announcement will be the most-watched press conference in Bollywood this year. And for NRIs following from abroad, it's a reminder that the real drama in Indian cinema isn't always on screen.

*FWICE is expected to announce its decision at a press conference on Monday, May 25, 2026.*"""
    })
else:
    print(f"⚠️  Skipping duplicate: {slug2}")

# ══════════════════════════════════════════════════════════════
# ARTICLE 3: Akshay Kumar's Samuk — India's First Alien Thriller
# ══════════════════════════════════════════════════════════════
slug3 = "akshay-kumar-samuk-india-first-alien-thriller-hollywood-crew-20260524"
if not check_duplicate(slug3):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Akshay Kumar Is Fighting Aliens Now. The Creature Designer Did the Alien Franchise. The Stunt Coordinator Did Mission: Impossible. India's First Sci-Fi Alien Thriller Is Called 'Samuk.'",
        "subheadline": "The film reunites Akshay with producer Vipul Amrutlal Shah after 12 years, features Oscar-nominated creature effects artist Alec Gillis and MI: Reckoning stunt coordinator Luke Timber, and promises practical aliens — no CGI shortcuts.",
        "slug": slug3,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "developing",
        "status": "published",
        "published_at": now,
        "score_total": 76,
        "tags": ["Akshay Kumar", "Samuk", "alien thriller", "sci-fi", "Alec Gillis", "Luke Timber", "Kanishk Varma", "Vipul Shah"],
        "diaspora_angle": "For NRIs who watch both Bollywood and Hollywood, Samuk is a fascinating collision. Indian cinema has never seriously attempted alien horror — and now it's doing so with the actual creature designer from the Alien franchise and the stunt coordinator from Mission: Impossible. It's the kind of film that could either be a landmark or a spectacular misfire, and diaspora audiences will be the toughest judges.",
        "sources": [
            {"url": "https://globalindiabroadcastnews.com/entertainment/akshay-kumar-confirms-first-indian-space-thriller-samuk-a-completely-new-genre-for-me-and-also-for-our-films-very-excited", "name": "GIBN"},
            {"url": "https://aihustlehq.com/bollywood/exclusive-samuk-akshay-kumar-india-first-alien-thriller/", "name": "AI Hustle HQ"},
            {"url": "https://movietalkies.com/big-news-akshay-kumar-samuk-india-first-sci-fi-alien-thriller/", "name": "Movie Talkies"},
            {"url": "https://www.hindustantimes.com/entertainment/bollywood/akshay-kumar-samuk-sci-fi-thriller", "name": "Hindustan Times"}
        ],
        "image_search_query": "Akshay Kumar Samuk alien thriller 2026",
        "image_entities": ["Akshay Kumar", "Samuk", "Kanishk Varma"],
        "image_must_show": "Akshay Kumar in an action or sci-fi context, or a Samuk promotional still",
        "word_count": 720,
        "topic_id": "84c43a5b-db33-44e6-b8c2-ba4f30d9a3d2",
        "body": """Indian cinema has given us everything. Romance, revenge, cricket biopics, partition dramas, dance-offs in Swiss meadows. One thing it has never given us? A serious alien movie.

Akshay Kumar is about to change that.

*Samuk* — India's first large-scale sci-fi alien thriller — has been confirmed by the actor himself, with a creative team that reads like it was assembled specifically to make people take notice: Oscar-nominated creature effects artist Alec Gillis (the *Alien* franchise, *Alien: Romulus*, *Predator*) and Hollywood stunt coordinator Luke Timber (*Mission: Impossible – The Final Reckoning*, *No Time to Die*, *Star Wars: The Rise of Skywalker*).

"The space sci-fi thriller is a completely new genre for me and for our films as well," Akshay told Hindustan Times. "I am very excited about it."

## The Hollywood Muscle Behind the Monsters

The most intriguing detail about *Samuk* isn't its star — it's who's building the alien. Alec Gillis has spent decades creating practical creature effects for some of Hollywood's most iconic monsters. His credits include multiple entries in the *Alien* and *Predator* franchises, *Smile 2*, and the cult classic *Tremors*.

Gillis has confirmed that *Samuk*'s alien will be "a truly unique space horror," created entirely through practical effects rather than CGI. In an era where most Hollywood films default to digital creatures, that's a bold creative choice — and one that suggests the filmmakers want their monster to feel physically real.

"Kanishk and I together designed the title character," Gillis told the press. "In the age of CGI and AI, it's pleasing that directors and audiences still appreciate traditional, hand-crafted, man-made monsters."

He also had remarkably specific praise for Akshay: "He has the physicality of Jason Statham and the resemblance of Tom Cruise." Whether or not you agree with that comparison, it suggests Gillis sees the film as a genuine action-horror hybrid, not a Bollywood experiment.

## Luke Timber and the Action Design

On the stunt side, Luke Timber — a former Royal Marines commando turned Hollywood stunt coordinator — is designing the action sequences. His work on the latest *Mission: Impossible* speaks for itself.

"This project represents an exciting blend of global stunt expertise, visionary filmmaking, and authentic action cinema," Timber said. "Together, we aim to deliver a film that combines powerful storytelling with cutting-edge live-action sequences that will resonate with audiences internationally."

That phrase — "internationally" — is key. This isn't being positioned as a Hindi-language genre experiment. It's being built for global audiences from the ground up.

## Akshay and Vipul: The Reunion

*Samuk* marks the reunion of Akshay Kumar and producer Vipul Amrutlal Shah after 12 years. The duo previously collaborated on hits like *Namastey London* and *Waqt: The Race Against Time*. Directed by Kanishk Varma, the film is co-produced by Akshay himself alongside Vipul and Ashin Shah.

For Akshay, *Samuk* represents yet another genre pivot in a career that's covered everything from patriotic actioners to comedy franchises to prestige biopics. His recent box office record has been mixed — but a genuinely new kind of Indian film could be exactly the reset he needs.

## The NRI Angle: Why Diaspora Audiences Are the Toughest Test

Here's the thing about NRI audiences and genre films: they're bilingual consumers. They watch the MCU on Friday and Bollywood on Saturday. They know what a good alien movie looks like because they've seen *Alien*, *Arrival*, and *Nope*. They'll be thrilled that India is finally attempting this genre — and merciless if it doesn't deliver.

*Samuk*'s secret weapon is its commitment to practical effects. In a landscape where CGI fatigue is real and audiences crave tactile, physical filmmaking, a hand-crafted alien designed by the man who built the Xenomorph could give this film a texture that sets it apart from both Bollywood and Hollywood fare.

No release date has been announced, but production is expected to begin soon. For now, NRIs can add *Samuk* to the short list of Indian films that are trying something genuinely unprecedented — and hope it's as weird and wonderful as it sounds.

*Samuk is directed by Kanishk Varma, produced by Akshay Kumar, Vipul Amrutlal Shah, and Ashin Shah.*"""
    })
else:
    print(f"⚠️  Skipping duplicate: {slug3}")


# ── Insert articles ──
print(f"\n📝 Inserting {len(articles)} articles...")
for a in articles:
    if a.get("topic_id") is None:
        del a["topic_id"]
    try:
        result = sb_post("p2_articles", a)
        print(f"  ✅ {a['slug'][:60]}")
    except Exception as e:
        print(f"  ❌ {a['slug'][:40]}: {e}")

# ── Mark topics published ──
topic_ids_published = [
    "fd48cb9b-964b-4a98-856e-7cbcc68de70e",  # Ramayana AR Rahman Hans Zimmer
    "60d8cc94-8819-4c0b-acb7-a8f6b5dc2f02",  # Farhan Akhtar Don 3 FWICE
    "84c43a5b-db33-44e6-b8c2-ba4f30d9a3d2",  # Akshay Kumar Samuk
]
# Also mark related topics that overlap
topic_ids_also = [
    "e4b2ff23-bc39-49d5-a6f1-fc40dd2e8e78",  # Nitesh Tiwari Ramayana directing (covered in article 1)
]
print("\n📋 Marking topics as published...")
for tid in topic_ids_published + topic_ids_also:
    code = sb_patch("p2_topics", f"id=eq.{tid}", {"status": "published"})
    print(f"  {'✅' if code < 300 else '⚠️'} {tid[:12]} -> published (HTTP {code})")

# ── Reject stale/weak entertainment topics ──
reject_ids = [
    "3badea5d-463e-4daa-b49d-a2e40cc7edea",  # David Dhawan retirement — already covered in today's articles
    "9897e135-0c09-423c-8b34-48fe17386e71",  # Karan Johar on David Dhawan — same story, already covered
]
print("\n🚫 Rejecting duplicate/covered topics...")
for tid in reject_ids:
    code = sb_patch("p2_topics", f"id=eq.{tid}", {"status": "rejected"})
    print(f"  {'✅' if code < 300 else '⚠️'} {tid[:12]} -> rejected (HTTP {code})")

# ── Score decay for entertainment articles older than 48h ──
print("\n📉 Running score decay on old entertainment articles...")
cutoff = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
r = requests.get(
    f"{SB_URL}/rest/v1/p2_articles?category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff}&score_total=gt.45&select=id,score_total,headline&order=score_total.desc&limit=30",
    headers=HEADERS, timeout=30
)
if r.status_code == 200:
    old_articles = r.json()
    decayed = 0
    for oa in old_articles:
        new_score = max(40, int(oa["score_total"] * 0.92))
        if new_score < oa["score_total"]:
            sb_patch("p2_articles", f"id=eq.{oa['id']}", {"score_total": new_score})
            decayed += 1
    print(f"  Decayed {decayed}/{len(old_articles)} old entertainment articles")
else:
    print(f"  ⚠️  Failed to fetch old articles: HTTP {r.status_code}")

print("\n✅ Entertainment writer 0630 batch complete!")
