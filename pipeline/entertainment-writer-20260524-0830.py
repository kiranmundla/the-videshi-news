#!/usr/bin/env python3
"""Entertainment writer — May 24 2026, 08:30 PDT batch:
1. Peddi — Ram Charan, CBFC censors 'Rajasthan', AR Rahman, June 4 worldwide release
2. Chand Mera Dil — Lakshya + Ananya Panday's quiet romance is connecting with youth
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

def sb_get(table, filters, select="*"):
    r = requests.get(f"{SB_URL}/rest/v1/{table}?{filters}&select={select}", headers=HEADERS, timeout=15)
    return r.json() if r.status_code == 200 else []

def check_duplicate(slug):
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id",
        headers=HEADERS, timeout=15
    )
    return len(r.json()) > 0 if r.status_code == 200 else False

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Peddi — Ram Charan, CBFC censorship, June 4
# ══════════════════════════════════════════════════════════════
slug1 = "peddi-ram-charan-cbfc-censors-rajasthan-ar-rahman-june-4-worldwide-20260524"
if not check_duplicate(slug1):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "India's Censor Board Just Banned the Word 'Rajasthan' From Ram Charan's New Film. The State's Name. Deleted.",
        "subheadline": "Peddi — a ₹200-crore sports epic with AR Rahman's score, a 3-hour-9-minute runtime, and a real pehelwan who gave Ram Charan a cartilage tear — releases worldwide on June 4. But it's the CBFC's censorship that's making headlines.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "developing",
        "status": "published",
        "published_at": now,
        "score_total": 78,
        "tags": ["Ram Charan", "Peddi", "CBFC", "Janhvi Kapoor", "AR Rahman", "Buchi Babu Sana", "Telugu cinema", "censorship"],
        "diaspora_angle": "Peddi releases in IMAX and standard theatres worldwide on June 4, making it immediately accessible to NRI audiences across the US, UK, Canada, and Australia. For the Telugu diaspora — one of the largest and most cinema-devoted NRI communities — this is a tentpole event. But the CBFC's decision to censor the name of an Indian state raises questions that resonate globally: when does film regulation become political sanitisation?",
        "sources": [
            {"url": "https://www.bollywoodhungama.com/news/bollywood/breaking-cbfc-censors-rajasthan-mr-cd-middle-finger-visuals-in-ram-charan-janhavi-kapoor-starrer-peddi/", "name": "Bollywood Hungama"},
            {"url": "https://www.zoomtventertainment.com/entertainment/peddi-censor-certificate-details", "name": "Zoom TV"},
            {"url": "https://blazetrends.com/peddi-censor-cuts-cbfc-rajasthan", "name": "Blaze Trends"},
            {"url": "https://nripage.com/peddi-hellallallo-promo-ram-charan", "name": "NRI Page"}
        ],
        "image_search_query": "Ram Charan Peddi 2026 sports film wrestling",
        "image_entities": ["Ram Charan", "Janhvi Kapoor", "AR Rahman", "Peddi"],
        "image_must_show": "Ram Charan in his wrestler/sports avatar from Peddi, or the Peddi film poster",
        "word_count": 850,
        "body": """The Central Board of Film Certification has made some peculiar decisions over the decades. It has muted profanity, trimmed kissing scenes, and forced filmmakers to add disclaimers about smoking. But banning the name of an Indian state? That's a new one.

Ram Charan's *Peddi* — a sports action drama about a wrestler from rural Andhra Pradesh — was granted a U/A 16+ certificate on May 22. But the certificate came with conditions that have raised eyebrows across the industry. The CBFC ordered the deletion of the word "Rajasthan" from the film's second half, along with a reference to a specific community. No explanation was offered publicly.

Six Telugu-language words and phrases — *Loudesh*, *Bokka*, *Lambdi kodaka*, *Dongamunda kodaka*, *Kalchi padi denguta*, and one Hindi expletive — were ordered muted or modified. A lyric in the song *Chikiri Chikiri* was altered. A middle finger gesture was covered with CGI. But it's the state-name deletion that has become the story.

## Why "Rajasthan" Is the Real Headline

India's film censorship has always been politically sensitive. References to specific states, communities, and political figures have been cut from films before — *Udta Punjab* fought a public battle to keep "Punjab" in its title. But the quiet deletion of "Rajasthan" from a Telugu sports drama suggests that the CBFC's political calculus remains as opaque as ever.

What context the word appeared in remains unclear. Was it a plot point? A throwaway line? A reference to a wrestling tradition? The CBFC's order doesn't specify, and the filmmakers haven't commented publicly. What we do know is that Rajasthan, which goes to state elections later this year, is politically contested territory — and India's censorship apparatus has a documented history of treating state names as politically inconvenient.

For NRI audiences watching from abroad, this kind of censorship feels especially jarring. Indian cinema markets itself globally as a medium of unfiltered cultural expression — the industry that gave the world *Gangs of Wasseypur*, *Article 15*, and *Jai Bhim*. State-name deletions undermine that narrative.

## The Film Itself Is Enormous

Set aside the censorship debate, and *Peddi* is one of the biggest Indian films of 2026. Directed by Buchi Babu Sana — whose debut *Uppena* (2021) was a sleeper hit — the film follows a young wrestler's rise through India's *akhada* circuit. Ram Charan, who committed to months of physical training, suffered a cartilage tear during a shoot with real *pehelwans* that the director insisted on casting instead of trained actors.

"I asked our director to get trained artists, but he got real pehelwans," Ram Charan said at the trailer launch, laughing about his injury. "It's worth it. It's a beautiful memory of *Peddi*."

The cast is stacked across industries. Janhvi Kapoor plays the female lead in her most physically demanding role yet. Kannada superstar Shiva Rajkumar plays a pivotal role, marking a rare Telugu appearance. Jagapathi Babu, Divyenndu (*Mirzapur*'s Munna Bhaiya), and Boman Irani round out a cast designed to pull audiences from every language market.

## AR Rahman's Score

Oscar and Grammy winner AR Rahman has composed the music — and his involvement alone changes the film's cultural register. The promotional song *Hellallallo*, launched at a live concert in Bhopal on May 23 featuring Shruti Haasan in a special appearance, has already gone viral. Rahman's ability to marry folk textures with cinematic grandeur makes him the ideal composer for a story rooted in rural wrestling culture.

For NRIs who grew up on Rahman's *Roja*, *Dil Se*, and *Slumdog Millionaire*, his name on a project is still the single most reliable quality signal in Indian film music.

## Why NRIs Should Mark June 4

*Peddi* releases worldwide on June 4 in Telugu, Hindi, Tamil, Kannada, and Malayalam — the full pan-Indian treatment. IMAX screens globally will carry the film, with Jio Studios handling North India distribution.

At 3 hours and 9 minutes, this is Ram Charan's longest film, and it's arriving with the kind of pre-release momentum that Telugu tentpoles have perfected: stadium-sized trailer launches, city-by-city music events, and a social media campaign that treats the release like a sporting event.

The Telugu diaspora in the US — concentrated in the Bay Area, Dallas-Fort Worth, New Jersey, and Chicago — reliably drives opening-weekend numbers that rival domestic metros. *Peddi* is the kind of film that will fill NRI screening rooms on opening night.

## The Bigger Picture

The CBFC's censorship of *Peddi* arrives at a moment when India's relationship with creative freedom is under global scrutiny. Netflix and Amazon have faced pressure over content choices. Stand-up comedians have been arrested for jokes. And now, the name of one of India's 28 states has been deemed unsuitable for a movie screen.

*Peddi* will almost certainly be a commercial hit regardless. Ram Charan's fan base is enormous, the film's scale is undeniable, and AR Rahman's involvement gives it cross-demographic appeal. But the censorship story will follow it — because in 2026, the question of what India allows its own stories to say is no longer just an industry issue. It's a cultural one."""
    })
else:
    print(f"⚠️ Skipping duplicate: {slug1}")

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Chand Mera Dil — Bollywood romance revival
# ══════════════════════════════════════════════════════════════
slug2 = "chand-mera-dil-lakshya-ananya-panday-bollywood-romance-box-office-weekend-20260524"
if not check_duplicate(slug2):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "A Small Bollywood Romance With No Stars, No Sequel Number, and No Franchise — Just Opened to the Best Word-of-Mouth of the Year.",
        "subheadline": "Chand Mera Dil stars Lakshya (from Kill) and Ananya Panday as college sweethearts whose relationship collapses under family pressure. It's earning less than ₹5 crore a day. And it might be the most important Hindi film of the summer.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now,
        "score_total": 74,
        "tags": ["Chand Mera Dil", "Lakshya", "Ananya Panday", "Bollywood romance", "box office", "Vivek Soni", "Sachin-Jigar"],
        "diaspora_angle": "For NRI millennials and Gen-Z who grew up on Bollywood love stories — Dilwale Dulhania Le Jayenge, Jab We Met, 2 States — the genre has felt dead for years, replaced by action franchises and OTT thrillers. Chand Mera Dil is a reminder that the Bollywood romance isn't gone. It just needed to stop trying to be everything else.",
        "sources": [
            {"url": "https://www.bollywoodhungama.com/movie/chand-mera-dil/critic-review/", "name": "Bollywood Hungama"},
            {"url": "https://boxofficeworldwide.com/chand-mera-dil-saturday-growth", "name": "Box Office Worldwide"},
            {"url": "https://www.bollywoodlife.com/box-office/chand-mera-dil-day-3", "name": "Bollywood Life"},
            {"url": "https://en.wikipedia.org/wiki/Chand_Mera_Dil", "name": "Wikipedia"}
        ],
        "image_search_query": "Chand Mera Dil 2026 Lakshya Ananya Panday romantic film",
        "image_entities": ["Lakshya", "Ananya Panday", "Chand Mera Dil"],
        "image_must_show": "Lakshya and Ananya Panday in a romantic scene or the film's poster",
        "word_count": 780,
        "body": """Here are the numbers that matter. *Chand Mera Dil* opened on May 22 to ₹3.31 crore. By Saturday, it had jumped 21% to ₹4.15 crore. The Sunday estimate is ₹5.25 crore — a continued upward trajectory that, in today's Bollywood, is rarer than a ₹100-crore opening.

This isn't a film that was supposed to dominate. It has no franchise IP, no established action hero, no extended universe. It's a love story set in a Hyderabad engineering college, directed by a filmmaker most people haven't heard of, starring two actors who have exactly one proven hit between them.

And it might be exactly what Hindi cinema needs right now.

## What's Actually Working

Vivek Soni's film follows Aarav (Lakshya) and Chandni (Ananya Panday) through the full arc of a modern Indian relationship: the meet-cute, the courtship, the family interference, the implosion, and the question of whether love survives the real world. Bollywood Hungama gave it 3.5 out of 5. BookMyShow audiences rated it 8.6 out of 10 — a number that matters more than any critic's verdict, because it represents the people actually buying tickets.

What's driving the word-of-mouth isn't spectacle. It's recognition. Viewers are seeing their own relationships on screen: the controlling parent who discovers the truth, the couple that loses contact at the worst possible moment, the ending that's sweet but predictable — because real love stories often are.

Lakshya, who broke out as a cold-blooded killer in *Kill* (2024), proves he's not a one-note actor. Bollywood Hungama's review specifically highlights his non-verbal performance: "Watch out for him in scenes where he has no dialogues. The way he expresses his sadness through his expressions is seen to be believed." Ananya Panday, long dismissed as a star-kid placeholder, delivers what multiple critics are calling her most mature work. She handles a challenging, multi-layered role with surprising ease.

## The Sachin-Jigar Factor

If you've been hearing *Chand Mera Dil*'s title track everywhere — at Indian grocery stores in Edison, in Uber rides in the Bay Area, hummed at desi house parties in London — that's not an accident. Sachin-Jigar's soundtrack is the kind of Bollywood music album that doesn't get made anymore: a full collection of songs that are woven into the narrative rather than inserted as promotional vehicles.

*Khasiyat*, *Aitbaar*, *Phir Ajnabi*, and *Priya Madhuri* each serve a distinct emotional beat. The choreography for *Priya Madhuri* has drawn specific praise for its inventiveness. In an era where Hindi film songs are increasingly afterthoughts, *Chand Mera Dil*'s music is carrying the film's emotional weight — and its box office.

## Why This Matters Beyond Numbers

Let's put ₹12-13 crore in three days in context. *Dhurandhar 2* opened to over ₹100 crore. *Border 2* crossed ₹50 crore on Day 1. Against those numbers, *Chand Mera Dil* looks modest.

But Bollywood's crisis isn't that big films don't work — it's that *only* big films work. The mid-range has collapsed. Original stories, non-franchise dramas, films that cost ₹30-40 crore and need ₹80 crore to succeed — these have been systematically abandoned by studios chasing ₹500-crore blockbusters and ₹30-crore OTT deals.

*Chand Mera Dil* is proof that the audience for these films still exists. It just needs the right story, told with genuine craft, marketed honestly, and priced accessibly. The film launched with discounted tickets — a strategy that's becoming standard for mid-range releases — and the economics work: lower ticket prices mean more footfalls, which mean stronger word-of-mouth, which mean better weekday holds.

## The NRI Angle

For diaspora audiences, the Bollywood romance occupies a specific emotional register. *DDLJ*, *Jab We Met*, *2 States*, *Yeh Jawaani Hai Deewani* — these are the films NRI families watch on flights home, quote at weddings, and stream on lazy Sunday afternoons. The genre isn't just entertainment; it's comfort food.

*Chand Mera Dil* isn't trying to be the next *DDLJ*. But it's doing something almost more valuable: reminding audiences that Bollywood still knows how to tell a love story that feels real, looks beautiful, and doesn't need a car chase or a post-credits sequence to earn its runtime.

With a clear two-week window before *Hai Jawani Toh Ishq Hona Hai* opens on June 5, the film has room to build — and the trajectory suggests it will. Shot beautifully in Hyderabad (a rare choice for Hindi cinema), with performances that have surprised even skeptics, and a soundtrack that's already living outside the film, *Chand Mera Dil* is the kind of quiet hit that Bollywood needs to remember how to make."""
    })
else:
    print(f"⚠️ Skipping duplicate: {slug2}")

# ══════════════════════════════════════════════════════════════
# INSERT ARTICLES
# ══════════════════════════════════════════════════════════════
print(f"\n📝 Inserting {len(articles)} articles...")
inserted = []
for article in articles:
    try:
        result = sb_post("p2_articles", article)
        art = result[0] if isinstance(result, list) else result
        inserted.append(art)
        print(f"  ✅ Inserted: {article['headline'][:70]}...")
    except Exception as e:
        print(f"  ❌ Failed to insert {article['slug']}: {e}")

# ══════════════════════════════════════════════════════════════
# SCORE DECAY — older entertainment articles
# ══════════════════════════════════════════════════════════════
print("\n📉 Applying score decay...")
now_dt = datetime.now(timezone.utc)

# Articles > 7 days old: score → 35
cutoff_7d = (now_dt - timedelta(days=7)).isoformat()
status_7d = sb_patch(
    "p2_articles",
    f"vertical=eq.entertainment&status=eq.published&published_at=lt.{cutoff_7d}&score_total=gt.35",
    {"score_total": 35}
)
print(f"  7d+ decay → HTTP {status_7d}")

# Articles 3-7 days old: score → 50
cutoff_3d = (now_dt - timedelta(days=3)).isoformat()
status_3d = sb_patch(
    "p2_articles",
    f"vertical=eq.entertainment&status=eq.published&published_at=lt.{cutoff_3d}&published_at=gte.{cutoff_7d}&score_total=gt.50",
    {"score_total": 50}
)
print(f"  3-7d decay → HTTP {status_3d}")

print(f"\n✅ Entertainment writer complete! {len(inserted)} articles published.")
for a in inserted:
    print(f"  • {a.get('slug', 'unknown')}")
