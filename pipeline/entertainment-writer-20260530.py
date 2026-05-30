#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-30 batch"""

import json, os, requests, time, uuid, re
from datetime import datetime, timezone

# Load Supabase config
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                key, _, val = line.partition('=')
                val = val.strip('"').strip("'")
                env[key.strip()] = val
    return env

env = load_env('~/.env.supabase')
SUPABASE_URL = env['SUPABASE_URL']
SUPABASE_KEY = env['SUPABASE_SERVICE_ROLE_KEY']

# Load Pexels key
pexels_env = load_env('~/workspace/.env.pexels')
PEXELS_KEY = pexels_env.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
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

def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels using curl (urllib gets 403)."""
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=3&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0]['src']['large2x']
                print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Check image URL returns 200 with image content-type and reasonable size."""
    if not url:
        return False
    # Block Meta CDN
    blocked = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com']
    if any(b in url for b in blocked):
        print(f"  ✗ Blocked Meta CDN URL: {url[:60]}")
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Some servers don't support HEAD, try GET
        if r.status_code in (405, 403):
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            ct2 = r2.headers.get('Content-Type', '')
            if r2.status_code == 200 and 'image' in ct2:
                chunk = r2.raw.read(6000)
                if len(chunk) > 5000:
                    return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def sb_insert(table, record):
    """Insert a record into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=record
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            return data[0].get('id')
        return None
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
    return None

def sb_patch(table, filters, updates):
    """Patch a record in Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?{filters}"
    r = requests.patch(url, headers=HEADERS, json=updates)
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch failed ({r.status_code}): {r.text[:200]}")
    return False

# ─── Articles ───

articles = []

# ── Article 1: ₹400 Crore Song Rights War ──
articles.append({
    "headline": "Vashu Bhagnani Just Filed a ₹400 Crore Lawsuit to Stop Varun Dhawan's New Film From Releasing. It's Over Two Songs From 1999.",
    "subheadline": "The fight over 'Chunari Chunari' and 'Ishq Sona Hai' from Biwi No 1 has exploded into one of Bollywood's biggest copyright battles — and it could delay a June 5 release.",
    "slug": "vashu-bhagnani-400-crore-lawsuit-biwi-no-1-songs-hai-jawani-varun-dhawan-nri-20260530",
    "category": "entertainment",
    "vertical": "entertainment",
    "topic_id": None,
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
        {"name": "The CSR Journal", "url": "https://thecsrjournal.in"},
        {"name": "Dainik Bhaskar English", "url": "https://bhaskarenglish.in"}
    ]),
    "image_url": None,
    "image_attribution": None,
    "person_image": "Vashu Bhagnani",
    "pexels_query": "Bollywood film court legal dispute",
    "pexels_fallback": "Mumbai film industry",
    "body": """If you grew up rewinding the cassette tape to hear 'Chunari Chunari' one more time, this story is about to hit differently.

Vashu Bhagnani's production house, Puja Entertainment, has filed a ₹400 crore lawsuit before the Bombay High Court against Tips Industries Limited, producers Ramesh and Kumar S. Taurani, and filmmaker David Dhawan. The allegation: they used two iconic songs from the 1999 blockbuster *Biwi No 1* in the upcoming Varun Dhawan-starrer *Hai Jawani Toh Ishq Hona Hai* without permission.

The songs in question — 'Chunari Chunari' and 'Ishq Sona Hai' — are two of the most recognizable tracks of late-90s Bollywood. For millions of NRIs, they are the soundtrack of wedding sangeets, college farewells, and childhood living rooms. The fact that they are now at the center of a legal war worth ₹400 crore tells you exactly how valuable Bollywood's musical nostalgia has become.

## What Bhagnani Is Claiming

According to Puja Entertainment's legal filing, Tips Industries only ever held audio rights to the songs from *Biwi No 1*. The visual rights — the ability to use the songs in a film — were never formally transferred. Bhagnani's lawyer told ANI that in 2018, Tips sent an email requesting visual rights, but no agreement was ever reached between the two parties.

Puja Entertainment is now seeking an urgent injunction to restrain the release, distribution, exhibition, and streaming of *Hai Jawani Toh Ishq Hona Hai* and all its promotional material containing the disputed songs. They also want the film's title changed, arguing it derives directly from the song lyrics. And if Tips and the makers proceed regardless, Bhagnani is demanding an additional ₹100 crore in damages.

The Bombay High Court has accepted the filing and is expected to schedule a hearing soon. The film, starring Varun Dhawan alongside Pooja Hegde and Mrunal Thakur, is directed by David Dhawan and currently slated for a June 5 release.

## Why This Matters Beyond the Courtroom

This case could set a significant precedent for how Bollywood song rights are handled going forward. In the 1990s and early 2000s, song rights deals were often structured through informal agreements and handshakes. Audio rights and visual rights were treated as separate categories, but the boundaries were rarely tested in court because remakes and recreations weren't the dominant creative strategy they are today.

Now they are. Bollywood's reliance on recreated songs — from 'Masakali 2.0' to 'Saki Saki' — has turned every old hit into a potential goldmine. And with that value comes the question: who actually owns what?

## The Diaspora Angle

For NRIs who grew up in the Govinda-David Dhawan comedy era, 'Chunari Chunari' isn't just a song. It's a cultural artifact. The recreation trend has been a source of both nostalgia and frustration for the diaspora — there's a thrill in hearing a familiar beat in a new film, but a growing sense that studios are strip-mining the catalogue of a generation's childhood.

This lawsuit, regardless of its outcome, is forcing the industry to put a price tag on that nostalgia. And ₹400 crore says it's not cheap.

Tips Industries has called the allegations baseless, but with a June 5 release date looming and the court moving to hear the case, the next few days will determine whether *Hai Jawani Toh Ishq Hona Hai* makes it to theaters on time — or becomes the most expensive song dispute in Indian entertainment history.

*The court hearing date has not yet been publicly confirmed. The Videshi will update this story as proceedings develop.*"""
})

# ── Article 2: Desi Bling + TejRan Engagement ──
articles.append({
    "headline": "Netflix's Desi Bling Is the Guilty Pleasure the Indian Diaspora Didn't Know It Needed. And Yes, TejRan Are Officially Engaged.",
    "subheadline": "Dubai's ultra-rich Indian social scene gets its own reality show — and Karan Kundrra's proposal to Tejasswi Prakash in Punjabi became the internet's most-watched desi moment this week.",
    "slug": "desi-bling-netflix-tejran-engaged-karan-kundrra-tejasswi-dubai-nri-20260530",
    "category": "entertainment",
    "vertical": "entertainment",
    "topic_id": None,
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
        {"name": "Pinkvilla", "url": "https://www.pinkvilla.com"},
        {"name": "Livemint", "url": "https://www.livemint.com"},
        {"name": "The Tab", "url": "https://thetab.com"}
    ]),
    "image_url": None,
    "image_attribution": None,
    "person_image": "Karan Kundrra",
    "pexels_query": "Dubai luxury lifestyle Indian",
    "pexels_fallback": "Dubai skyline night luxury",
    "body": """Netflix looked at *Dubai Bling*, looked at the Indian diaspora, and decided: why not both?

*Desi Bling*, which premiered on May 20, follows Dubai's ultra-rich Indian socialites as they navigate beach clubs, wellness sanctuaries, luxury golf spots, and the kind of interpersonal drama that makes WhatsApp groups look tame. The cast includes television stars Karan Kundrra and Tejasswi Prakash, real estate mogul Satish Sanpal and his wife Tabinda, former beauty queen Pamala Serena, and entrepreneur Rizwan Sajan, among others. Shilpa Shetty rounds out the ensemble.

The internet's verdict has been polarized — and perfectly predictable. On X and Reddit, reactions range from "the whole vibe" to "second-hand embarrassment," which, if we're being honest, is exactly where a good reality show should live. You don't watch people argue at J1 Beach over AED 120 salads for the intellectual nourishment. You watch it because you can't stop.

## The TejRan Engagement

But the undeniable highlight of the first season has nothing to do with Dubai's property market or luxury cooking classes. In one of the most viral scenes from the show, Karan Kundrra went down on one knee, delivered a heartfelt speech in Punjabi, and proposed to Tejasswi Prakash with a "Yes or a Yes?" line that broke the internet.

Tejasswi was visibly overwhelmed. "You are my everything to me. I love you so much," she told him, hands shaking as he slipped the ring on her finger. The clip racked up millions of views within hours.

For TejRan fans — the massive fandom born from their relationship on *Bigg Boss 15* in 2021 — this was the payoff after four years of dating rumors, wedding speculation, and fan edits. Former Bigg Boss contestant Rajiv Adatia confirmed the engagement was real, sharing a screenshot from a video call with the couple where Tejasswi showed off her diamond ring. "The love story that drove me crazy in BB is finally leading to marriage!" he wrote. He also predicted twins.

## Why NRIs Are Watching

What makes *Desi Bling* genuinely interesting for the diaspora isn't the lifestyle porn — though there's plenty of it. It's the mirror. Dubai's Indian community is one of the most visible, affluent, and culturally distinct diasporic populations in the world. The show captures the specific social dynamics of Indians abroad: the code-switching between Indian and Western sensibilities, the pressure to perform success, the layered relationships between business, family, and social status.

It also doesn't shy away from the uncomfortable parts. Karan's candid admission that he felt like he was "parenting" Tejasswi sparked genuine debate online. His parents' on-camera concerns about the relationship's balance gave the show a rawness that most Indian reality television avoids.

The show films at locations including J1 Beach, Top Chef Dubai, Sohum Wellness Sanctuary, and the kind of restaurants where cocktails cost more than a family dinner in Chandni Chowk. For Indian viewers in the Gulf, it's local. For NRIs in the US, UK, and Canada, it's aspirational voyeurism with a familiar accent.

Seven episodes. One season. One engagement. And enough drama to sustain the group chat until Season 2."""
})

# ── Article 3: Jolly LLB 3 Hits OTT ──
articles.append({
    "headline": "Jolly LLB 3 Is Now Streaming on JioHotstar. Here's Why the Diaspora Should Care About This One.",
    "subheadline": "Akshay Kumar and Arshad Warsi finally share a courtroom — and a cause — in a franchise film that's smarter than it has any right to be.",
    "slug": "jolly-llb-3-jiohotstar-ott-release-akshay-kumar-arshad-warsi-diaspora-nri-20260530",
    "category": "entertainment",
    "vertical": "entertainment",
    "topic_id": None,
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        {"name": "Livemint", "url": "https://www.livemint.com"},
        {"name": "Bombay Times", "url": "https://www.bombaytimes.com"},
        {"name": "Bollywood Life", "url": "https://www.bollywoodlife.com"}
    ]),
    "image_url": None,
    "image_attribution": None,
    "person_image": "Akshay Kumar",
    "pexels_query": None,
    "pexels_fallback": None,
    "body": """The courtroom drama that Indian cinema does better than anyone else is back — and this time, both Jollys are in the same room.

*Jolly LLB 3*, which completed a strong theatrical run earning over ₹170 crore worldwide, is now streaming on JioHotstar as of May 29. For NRIs who couldn't catch it in theaters during its original run, this is the version that's been worth waiting for.

## The Setup

The third installment in the *Jolly LLB* franchise does something its predecessors didn't: it brings together Arshad Warsi's Jagdish "Jolly" Tyagi from the original 2013 film and Akshay Kumar's Jagdishwar "Jolly" Mishra from the 2017 sequel. Both actors reprise their roles, joined by the irreplaceable Saurabh Shukla as the presiding judge, alongside Amrita Rao and Huma Qureshi.

The plot is inspired by the 2011 Bhatta-Parsaul land protests — a real-life case of farmers being displaced from their land by development projects. Warsi's Jolly takes up the case of a grieving widow whose father-in-law died by suicide after a land scam destroyed his family. Kumar's Jolly, a mercenary lawyer who defends whoever pays, is initially hired by the industrialist on the other side — the powerful Haribhai Khaitan, played by Gajraj Rao.

The twist: when Kumar's Jolly realizes the extent of the injustice, he switches sides. The two Jollys — rivals by temperament, allies by conscience — unite to expose the fraud.

## Why It Works

Director Subhash Kapoor has always understood that the *Jolly LLB* franchise works because it sits at the intersection of entertainment and outrage. Indian courtroom dramas aren't just procedurals — they're about the gap between the law as it's written and the law as it's experienced by ordinary people. The franchise has consistently used humor to make that gap bearable, and genuine anger to make it feel urgent.

*Jolly LLB 3* raises the stakes by grounding its fictional case in a real historical wound. The Bhatta-Parsaul protests were one of the defining land rights conflicts of the early 2010s, and the film doesn't flinch from showing how development can become a euphemism for displacement.

## The Diaspora Connection

For NRIs, the *Jolly LLB* films have always been a particular kind of comfort — the fantasy that somewhere in India's vast, creaking legal system, a scrappy lawyer with bad suits and good instincts is fighting the good fight. It's aspirational not in the lifestyle sense but in the moral one.

The film's arrival on JioHotstar also makes it accessible to diaspora viewers who may have missed its theatrical run or who live in markets where Hindi films get limited screen time. JioHotstar's international availability means this one is now a weekend plan away.

Saurabh Shukla's judge, as always, steals every scene he's in. The two Jollys sparring — and then collaborating — gives the film an energy that neither previous installment had alone. And Gajraj Rao, playing a villain who is menacing precisely because he's polite, is a reminder that Bollywood's best antagonists are the ones who never raise their voices.

If you've been following the franchise, this is the one that ties it together. If you haven't, JioHotstar just made it easy to start."""
})

# ── Article 4: Spider-Noir on Prime Video ──
articles.append({
    "headline": "Nicolas Cage Is a 62-Year-Old Spider-Man in 1930s New York. Spider-Noir Is Exactly as Weird and Wonderful as That Sounds.",
    "subheadline": "Prime Video's noir-flavored Marvel series can be watched in black and white or color — and Nicolas Cage wants you to start with the black and white.",
    "slug": "spider-noir-nicolas-cage-prime-video-marvel-1930s-noir-review-nri-20260530",
    "category": "entertainment",
    "vertical": "entertainment",
    "topic_id": None,
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "USA Today", "url": "https://www.usatoday.com"},
        {"name": "Decider", "url": "https://www.decider.com"},
        {"name": "People", "url": "https://www.people.com"}
    ]),
    "image_url": None,
    "image_attribution": None,
    "person_image": "Nicolas Cage",
    "pexels_query": "1930s noir detective city",
    "pexels_fallback": "vintage noir film",
    "body": """Nicolas Cage, at 62, has finally become Spider-Man. But not the Spider-Man you're thinking of.

*Spider-Noir*, now streaming all eight episodes on Prime Video, is a live-action Marvel series set in 1930s New York that casts Cage as Ben Reilly — an aging private investigator who gave up his superhero identity as "The Spider" five years ago. When a new case pulls him back into the orbit of crime boss Silvermane (Brendan Gleeson), a nightclub singer with secrets (Li Jun Li), and a group of ex-soldiers with superpowers, Ben has to dust off the mask and fedora one more time.

The twist that makes this show genuinely distinctive: you can watch it in either "True-Hue Full Color" or "Authentic Black & White." Cage himself recommends starting with black and white, calling the dual-format release "a little revolutionary."

## The Noir That Bites

Created by Oren Uziel and produced by Phil Lord and Christopher Miller — the team behind Sony's animated *Spider-Verse* films — *Spider-Noir* isn't an action spectacle. It's a detective show that happens to feature a protagonist who can climb walls. The 1930s setting is meticulously realized: filmed on soundstages in LA, the backlots of Warner Bros. and Universal Studios, and in LA's historic old bank district, the show's cinematographer Sean Bobbitt drew inspiration from Australian-born artist Martin Lewis's charcoal drawings of 1920s and '30s Manhattan street scenes.

"Even though we're portraying a comic book character, we wanted to be set in a bit more realism," Bobbitt said, noting that Warren Beatty's *Dick Tracy* was explicitly not an influence.

Cage, meanwhile, is doing what Cage does best: being simultaneously funny, crusty, and unexpectedly moving. His Ben Reilly is bruised, bitter, and getting his butt handed to him in fights more often than he'd like. "There's a lot of us getting older here, and we're not moving the same way we were when we were 18," Cage said. "He's a Spider-Man for aging adults."

## The Supporting Cast

Brendan Gleeson's Silvermane is a sharp-tongued Irish mob boss who treats his rivalry with Ben Reilly like a chess match. "Even if I had to kill you, I love you to bits," is how Gleeson describes the dynamic. Lamorne Morris plays newspaper editor Robbie Robertson, one of the few who knows Ben's secret identity, serving as both conscience and comedic foil.

Li Jun Li's nightclub singer Cat Hardy is the show's wild card — a character whose loyalties shift with every episode, keeping both Ben and the audience guessing.

## Should You Watch It?

If you're tired of Marvel's formula — if you find the CGI spectacles exhausting and the quippy heroes interchangeable — *Spider-Noir* is the antidote. It moves slowly, it rewards patience, and it trusts its audience to care about character more than action sequences. The black-and-white version, in particular, feels like a genuine experiment in superhero television — not a gimmick, but a creative choice that changes how you experience the story.

Cage almost played the Green Goblin in Sam Raimi's original 2002 *Spider-Man*. He passed, and Willem Dafoe got the role. Twenty-four years later, he's finally in the Spider-Man universe, just not in any way anyone could have predicted. That feels exactly right for Nicolas Cage."""
})

# ── Article 5: Rajamouli's Varanasi Update ──
articles.append({
    "headline": "Rajamouli's ₹1,400 Crore Varanasi Is Nearing Completion. Priyanka Chopra Is in Hyderabad Eating Mangoes Between Takes.",
    "subheadline": "The most expensive Indian film ever made features IMAX Ramayana battle sequences, Antarctic footage, and a globetrotting adventure set to release April 2027. Here's everything we know.",
    "slug": "rajamouli-varanasi-update-priyanka-chopra-mahesh-babu-imax-1400-crore-nri-20260530",
    "category": "entertainment",
    "vertical": "entertainment",
    "topic_id": None,
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        {"name": "Pinkvilla", "url": "https://www.pinkvilla.com"},
        {"name": "IANS via Bollywood Bubble", "url": "https://www.bollywoodbubble.com"},
        {"name": "Filmfare", "url": "https://www.filmfare.com"},
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Varanasi_(film)"}
    ]),
    "image_url": None,
    "image_attribution": None,
    "person_image": "S. S. Rajamouli",
    "pexels_query": "Varanasi India ancient city temple",
    "pexels_fallback": "Indian epic cinema filmmaking",
    "body": """S.S. Rajamouli doesn't make films. He makes events. And *Varanasi* might be his most ambitious one yet.

The Telugu-language epic action-adventure — starring Mahesh Babu, Priyanka Chopra Jonas, and Prithviraj Sukumaran — is now deep into its final stretch of filming, with Rajamouli reportedly aiming to wrap principal photography by August 2026. Priyanka, who plays a character named Mandakini, is currently shooting in Hyderabad, where she recently shared Instagram stories of herself eating Himayat mangoes between takes. "Mango love," she wrote, in what might be the most relatable content to come out of a ₹1,400 crore production.

## The Scale

Let's talk numbers, because the numbers are staggering.

*Varanasi* carries an estimated budget of ₹1,400 crore (approximately $165 million), making it the most expensive Indian film ever produced. It is the first Indian film — and only the fourth film globally — to shoot in Antarctica. It is the first Indian film to be shot in the 1.43:1 IMAX format. And it will run over three hours.

The plot follows Rudhra (Mahesh Babu), a Shiva devotee who embarks on a mission to retrieve an ancient cosmic artefact, traveling across continents and timelines as the city of Varanasi faces the arrival of an asteroid. Along the way, he discovers that the person who sent him on this quest is an evil mastermind. The narrative spans multiple historical eras, featuring Ramayana battle sequences filmed in IMAX.

Rajamouli has confirmed that Mahesh Babu will also appear as Lord Rama in one of the film's episodes, in addition to his primary role as Rudhra. Prithviraj Sukumaran plays the primary antagonist, Kumbha — described as a vicious supervillain shown in a futuristic wheelchair in the first-look poster.

## One Film, Not Two

Putting an end to months of speculation, Rajamouli has clarified that *Varanasi* will be a single film, not a two-part release. "We briefly considered it, but dropped the idea," he said. The film is written by Rajamouli along with his father V. Vijayendra Prasad and S.S. Kanchi, with music by M.M. Keeravani, cinematography by P.S. Vinod, and visual effects by V. Srinivas Mohan.

## Priyanka's Return to Indian Cinema

For the diaspora, the most compelling subplot of *Varanasi* is what it represents for Priyanka Chopra Jonas. This is her return to a major Indian theatrical release after years in Hollywood — from *Citadel* on Prime Video (Season 2 just premiered in May) to *Judgment Day* opposite Will Ferrell and Zac Efron. She's also attached to *Krrish 4*, marking Hrithik Roshan's directorial debut, and a survival thriller called *Reset* alongside Orlando Bloom.

But *Varanasi* is the one she's talked about with the most personal investment. "This is unlike anything I've ever done," she told Variety, describing it as a time-traveling epic and her first Telugu-language film in over a decade. She specifically requested a dance number — "I have to do a dance song. We haven't shot it yet. That's one of the last things I'm really looking forward to."

## The Release

*Varanasi* is scheduled for theatrical release on April 7, 2027, coinciding with the Telugu festival of Ugadi. Given Rajamouli's track record — *Baahubali* redefined Indian box office economics, and *RRR* won an Oscar — this is one of the most anticipated film releases in global cinema, not just Indian cinema.

For NRIs, Rajamouli films have become appointment viewing — the kind of event that fills up IMAX screens in New Jersey, the Bay Area, Dallas, and London on opening weekend. *Varanasi* is shaping up to be the biggest one yet. And Priyanka eating mangoes in Hyderabad means we're closer than ever."""
})

# ─── Publish articles ───

print(f"\n{'='*60}")
print(f"Entertainment Writer — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"{'='*60}")

published_count = 0

for i, article in enumerate(articles):
    print(f"\n--- Article {i+1}/{len(articles)} ---")
    print(f"  Headline: {article['headline'][:80]}...")

    # Image sourcing
    img_url = None
    person = article.pop('person_image', None)
    pexels_q = article.pop('pexels_query', None)
    pexels_fb = article.pop('pexels_fallback', None)

    if person:
        print(f"  Looking up Wikipedia image for: {person}")
        img_url = fetch_wikipedia_person_image(person)
        if img_url and not validate_image_url(img_url):
            print(f"  ⚠ Wikipedia image failed validation, clearing")
            img_url = None

    if not img_url and pexels_q:
        print(f"  Falling back to Pexels: {pexels_q}")
        img_url = fetch_pexels_image(pexels_q, pexels_fb)
        if img_url and not validate_image_url(img_url):
            print(f"  ⚠ Pexels image failed validation, clearing")
            img_url = None

    if img_url:
        article['image_url'] = img_url
        if 'wikipedia' in img_url or 'wikimedia' in img_url or 'upload.wikimedia' in img_url:
            article['image_attribution'] = 'Wikimedia Commons'
        else:
            article['image_attribution'] = 'The Videshi'
        print(f"  ✓ Image set: {img_url[:80]}...")
    else:
        print(f"  ⚠ No image found — publishing without image")
        article.pop('image_url', None)
        article.pop('image_attribution', None)

    # Insert
    art_id = sb_insert('p2_articles', article)
    if art_id:
        print(f"  ✓ Published: {article['slug']} (id: {art_id})")
        published_count += 1
    else:
        print(f"  ✗ FAILED to publish: {article['slug']}")

    time.sleep(0.5)

print(f"\n{'='*60}")
print(f"Done. Published {published_count}/{len(articles)} articles.")
print(f"{'='*60}")
