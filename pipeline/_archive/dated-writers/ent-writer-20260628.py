#!/usr/bin/env python3
"""Entertainment writer — June 28, 2026. Two articles: Supergirl BO + Mirzapur Movie teaser."""
import json, os, subprocess, sys, re

# Load env
env_path = os.path.expanduser("~/workspace/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

def insert_article(article: dict) -> dict:
    """Insert article via curl POST, return response dict."""
    payload = json.dumps(article)
    cmd = [
        "curl", "-s", "-X", "POST",
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=representation",
        "-d", payload
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"  ✗ curl error: {result.stderr}", file=sys.stderr)
        return {}
    try:
        data = json.loads(result.stdout)
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        elif isinstance(data, dict):
            if "message" in data or "error" in data:
                print(f"  ✗ API error: {data}", file=sys.stderr)
                return {}
            return data
        return {}
    except json.JSONDecodeError:
        print(f"  ✗ JSON parse error: {result.stdout[:200]}", file=sys.stderr)
        return {}


# ── ARTICLE 1: SUPERGIRL ──────────────────────────────────────────────

supergirl_body = """The cracks in the cape are showing.

DC Studios' *Supergirl*, the second theatrical chapter of James Gunn's rebooted DC Universe, crash-landed at the North American box office this weekend with a projected $38 million opening — less than a third of *Superman*'s $125 million debut in 2025. The result marks the DCU's first genuine box office disappointment, raising uncomfortable questions about the franchise's trajectory just two films in.

The numbers tell a grim story. After earning $7.8 million in Thursday previews (combining Wednesday IMAX fan events and Thursday showtimes), *Supergirl* managed approximately $18 million on Friday before settling into what *The Wrap* projects as a $38 million weekend across 3,602 screens. The film opened at No. 2, decisively outpaced by Disney-Pixar's *Toy Story 5*, which held the top spot with an estimated $72.5 million in its second weekend.

For context, *Supergirl*'s opening puts it in the company of *Morbius* ($39 million) and below *The Flash* ($55 million) — two films widely regarded as superhero misfires. A B- CinemaScore from opening-night audiences, the lowest for any DC film and on par with *X-Men: Dark Phoenix*, suggests word-of-mouth won't be riding to the rescue.

## Indian Audiences Aren't Biting Either

Indian moviegoers, who have warmed to Hollywood spectacles this year — from *Project Hail Mary* to *The Devil Wears Prada 2* — have been lukewarm at best. *Supergirl* opened to roughly ₹2 crore gross on Day 1, with Day 2 holding flat at approximately ₹1.40 crore net, bringing the two-day total to around ₹2.80 crore net. Pinkvilla projects the opening weekend at ₹7 to 9 crore gross — a fraction of what *Superman* managed in the same market.

The film is also caught in a brutal competitive squeeze. Akshay Kumar's *Welcome to the Jungle* crossed ₹39 crore net in just two days, commanding the Hindi-language audience. With *Alpha* arriving July 3 and *Dhamaal 4* on July 10, multiplex real estate for a mid-performing Hollywood import will only shrink.

## Milly Alcock Deserves Better

The cruelest irony of *Supergirl*'s stumble is that its lead actress is the best thing in it — and most critics agree. Milly Alcock, who became a global breakout as young Rhaenyra Targaryen in *House of the Dragon*, delivers what Empire called a performance of "hungover hero" charm. Filmfare gave the film 3 out of 5 stars, noting it "could have been a 3.5 or 4 star film" if not for its screenplay problems.

Based on Tom King and Bilquis Evely's acclaimed *Supergirl: Woman of Tomorrow* comic run, the film follows Kara Zor-El on a quest across alien worlds with a grieving alien girl named Ruthye (Eve Ridley) and a riotously chaotic Lobo (Jason Momoa). The source material was widely regarded as one of DC's best recent comics — intimate, character-driven, with a wry sense of humor. Director Craig Gillespie (*I, Tonya*, *Cruella*) seemed like an inspired choice.

But Ana Nogueira's screenplay, per Variety, "barely gives Supergirl a chance to wear the iconic costume," and the film's 108-minute runtime feels both rushed and meandering — a neat trick of bad structure. Matthias Schoenaerts' villain Krem registers as a non-entity, and the much-anticipated David Corenswet Superman cameo, while charming, only reminds audiences of the stronger film that preceded this one.

## The Math Doesn't Add Up

With a reported production budget of $170 million (some estimates peg the net figure at $186 million), *Supergirl* needs to gross somewhere between $300 million and $425 million worldwide to break even. Warner Bros. has reportedly told insiders it would consider anything above $300 million globally a "victory" — a notably lowered bar.

Given that international markets have historically been unkind to DC properties — *Superman* earned the bulk of its $619 million total domestically — that target feels optimistic at best.

The bigger concern for DC Studios isn't one film's underperformance. It's the pattern it could set. *Superman* proved James Gunn could build goodwill. *Supergirl* needed to prove the DCU could sustain it. Right now, the cape is dragging.

## Playing Near You

*Supergirl* is in theaters across the US, UK, Canada, and India. If you're on the fence: go for Milly Alcock. She is, genuinely, spectacular — a future megastar stuck in a film that doesn't quite know what to do with her. Just temper your expectations for everything around her."""

supergirl_article = {
    "headline": "Supergirl Stumbles With $38M Opening Weekend as DCU Faces Its First Box Office Misfire",
    "subheadline": "Milly Alcock's star turn couldn't save Craig Gillespie's uneven superhero saga from landing well below Superman's $125 million debut — and Indian audiences aren't biting either",
    "slug": "supergirl-2026-dcu-box-office-milly-alcock-38-million-opening-weekend",
    "body": supergirl_body,
    "category": "entertainment",
    "vertical": "entertainment",
    "is_editorial": False,
    "status": "review",
    "image_url": "",
    "sources": [
        "The Wrap",
        "Variety",
        "Screen Rant",
        "Pinkvilla",
        "comicbookmovie.com",
        "Filmfare",
        "Empire"
    ]
}

# ── ARTICLE 2: MIRZAPUR THE MOVIE ────────────────────────────────────

mirzapur_body = """The gaddi of Mirzapur is moving to the big screen. And it's bringing everyone — alive or dead — along for the ride.

Amazon MGM Studios and Excel Entertainment dropped the teaser for *Mirzapur: The Movie* on June 25, confirming what fans have speculated about for over a year: the franchise that redefined Indian OTT is making the leap to theatrical release. The film arrives in cinemas on September 4, 2026, in Hindi and Telugu — and if the teaser is anything to go by, it plans to be louder, bloodier, and more operatic than anything the three-season series delivered.

## The Band Is Back — With a Twist

The teaser reunites the holy trinity of Mirzapur fandom: Ali Fazal as the unhinged, grief-powered Guddu Pandit, Pankaj Tripathi as the terrifyingly calm Kaleen Bhaiya, and — in a move that sent the internet into meltdown — Divyenndu as Munna Bhaiya, whose apparent death in Season 2's finale was supposed to be definitive. His return has already sparked furious speculation about the film's timeline and narrative direction.

The most intriguing new addition is Jitendra Kumar stepping into the role of Bablu Pandit, previously played by Vikrant Massey. For fans of *Panchayat* and *Kota Factory*, seeing TVF's beloved "Jeetu bhaiya" in Mirzapur's world of carpet and carnage is a cognitive dissonance that might just work brilliantly. Ravi Kishan joins in an undisclosed role that the teaser hints could be the film's wild card.

The returning ensemble is stacked: Shweta Tripathi as Golu, Rasika Dugal, Abhishek Banerjee, Shriya Pilgaonkar, and Harshita Shekhar Gaur all appear. New faces include Sonal S. Chauhan and Sushant Singh.

## OTT to Theatres: A High-Stakes Gamble

The move from streaming to cinema is not without risk. Mirzapur's identity is inseparable from the binge-watch — the late-night, can't-stop-scrolling, one-more-episode pull that made it Amazon Prime Video's most-watched Indian original. Its audience knows these characters from their couches, not from multiplex seats. Converting that intimacy into a theatrical event requires the film to offer something the series couldn't: scale.

The teaser suggests director Gurmmeet Singh, who helmed the original series, understands this. The narrative reportedly expands beyond Purvanchal into the deserts of Rajasthan, promising a visual and geographical scope that three seasons of tight, claustrophobic power plays never attempted. Writer Puneet Krishna, who crafted the series' razor-sharp dialogue, returns — a crucial continuity in a franchise where language is as much a weapon as any firearm.

Producers Ritesh Sidhwani and Farhan Akhtar, through Excel Entertainment, have form with this kind of calculated risk. The production house built *Dil Chahta Hai*, *Zindagi Na Milegi Dobara*, and *Gully Boy* — films that understood their audience deeply enough to expand a niche into the mainstream. Mirzapur is already mainstream. The question is whether its fans will pay for a ticket to something they associate with free-with-subscription viewing.

## Why the Diaspora Should Care

Here's what anyone who's ever hosted a Mirzapur watch party in their Bay Area apartment or Wembley flat already knows: this franchise travels. Mirzapur was never just a Hindi-belt phenomenon. It became the show desi kids abroad recommended to their non-Indian friends, the gateway to understanding UP's cultural and political textures through entertainment rather than news.

The film's September 4 release — a Thursday, cleverly positioned before the US Labor Day weekend — suggests the makers are thinking globally. A Hindi and Telugu dual-language release also signals ambitions beyond the Hindi heartland, tapping into the South Indian theatrical market that has driven some of the decade's biggest box office numbers.

## The OTT-to-Cinema Pipeline

Mirzapur joins a growing list of Indian streaming properties attempting the reverse migration to theaters. The results have been mixed globally — Netflix's *Glass Onion* had a limited theatrical window before streaming, and the *Sacred Games* franchise explored and ultimately abandoned the idea. But Mirzapur has an advantage most don't: genuine cultural velocity.

"Bhaukaal" entered the lexicon. Munna's lines became meme templates. Kaleen Bhaiya's quiet menace inspired an entire generation of dramatic WhatsApp display pictures. If any Indian OTT property has earned the right to ask audiences to leave their homes and sit in a dark room together, it's this one.

September 4. Save the date. Bhaukaal is coming to the big screen."""

mirzapur_article = {
    "headline": "Mirzapur: The Movie Teaser Drops — Guddu, Kaleen Bhaiya and Munna Are Coming to the Big Screen This September",
    "subheadline": "From India's most binged web series to theatrical release — Excel Entertainment bets that Purvanchal's bloodiest saga can pack cinema halls on September 4",
    "slug": "mirzapur-the-movie-teaser-ali-fazal-pankaj-tripathi-september-2026-theatrical-release",
    "body": mirzapur_body,
    "category": "entertainment",
    "vertical": "entertainment",
    "is_editorial": False,
    "status": "review",
    "image_url": "",
    "sources": [
        "Bollywood Hungama",
        "Hauterrfly",
        "MensXP",
        "iDiva",
        "Amazon MGM Studios"
    ]
}

# ── INSERT ────────────────────────────────────────────────────────────

articles = [
    ("Supergirl", supergirl_article),
    ("Mirzapur", mirzapur_article),
]

results = []
for label, art in articles:
    print(f"\n{'='*60}")
    print(f"Inserting: {label}")
    print(f"  Headline: {art['headline']}")
    print(f"  Slug: {art['slug']}")
    print(f"  Words: {len(art['body'].split())}")
    resp = insert_article(art)
    if resp and resp.get("id"):
        print(f"  ✓ Inserted — ID: {resp['id']}")
        results.append((label, resp["id"], art["slug"]))
    else:
        print(f"  ✗ FAILED")
        results.append((label, None, art["slug"]))

print(f"\n{'='*60}")
print("SUMMARY:")
for label, aid, slug in results:
    status = f"ID={aid}" if aid else "FAILED"
    print(f"  {label}: {status} | slug={slug}")
