#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-30 batch"""

import json, os, re, sys, time, uuid, requests, urllib.parse
from datetime import datetime, timezone

# ── Supabase config ─────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

PEXELS_KEY = None
pexels_env = os.path.expanduser("~/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

# ── Helpers ─────────────────────────────────────────────────────
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


def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels API. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Return True if URL returns an image with Content-Length > 5000."""
    if not url:
        return False
    # Reject Meta CDN URLs
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com"]
    if any(b in url for b in banned):
        print(f"  ✗ Banned CDN URL: {url[:60]}")
        return False
    if any(p in url for p in ["_nc_ht=", "_nc_cat=", "ccb="]):
        print(f"  ✗ Signed Meta URL: {url[:60]}")
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD
        if "image" in ct and cl == 0:
            return True
        print(f"  ✗ Image validation failed: CT={ct}, CL={cl}")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def sb_insert(table, payload):
    """Insert a row and return the response JSON (list)."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    if r.status_code not in (200, 201):
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return None
    return r.json()


# ── Articles ────────────────────────────────────────────────────
articles = [
    {
        "headline": "Aamir Khan Has Three Films Lined Up Back-to-Back. A Cricket Epic, a 3 Idiots Sequel, and a Superhero Movie With Lokesh Kanagaraj.",
        "subheadline": "The actor will shoot Ashutosh Gowariker's Lala Amarnath biopic from October, then roll straight into 3 Idiots 2 with Vicky Kaushal joining the original trio, and a superhero film with the Kaithi director after that.",
        "slug": "aamir-khan-three-films-lala-amarnath-3-idiots-sequel-lokesh-kanagaraj-superhero-nri-20260530",
        "image_people": ["Aamir Khan"],
        "pexels_fallback": ("Bollywood actor on set", "Indian cinema filming"),
        "body": """Aamir Khan is doing something he almost never does: stacking his calendar.

The actor who built a career on obsessive single-film focus — one release every two to three years, each meticulously prepared — has locked dates for three consecutive projects. For a generation of NRI moviegoers who grew up timing their India trips around Aamir releases, this is genuinely unprecedented.

## The Cricket Film Comes First

Starting October 2026, Aamir will shoot Ashutosh Gowariker's ambitious period sports drama based on the historic 1952 India-Pakistan Test series. The film centres on legendary cricketer Lala Amarnath and his friendship with Pakistan captain Abdul Hafeez Kardar during the partition era.

This isn't just a cricket film. It's a partition story told through sport — the kind of emotionally loaded, historically rooted narrative that plays differently when you're watching it 8,000 miles from home. For the Indian diaspora, partition narratives carry a particular weight; many NRI families trace their own migration stories back to exactly this period.

Interestingly, Rajkumar Hirani and his longtime writing partner Abhijat Joshi are believed to be creatively involved with the screenplay, despite Hirani not directing. That's a significant detail — it means the film is getting the same level of script attention that produced 3 Idiots and PK.

## Then, the Sequel Everyone Wanted

The 3 Idiots sequel will go on floors in mid-2027, after the Gowariker film wraps. Reports suggest the film will feature a significant time jump and reunite the original trio of Aamir Khan, R. Madhavan, and Sharman Joshi.

But the real headline is the casting addition: Vicky Kaushal is reportedly in talks for a prominent role — being described informally as the "fourth idiot." If confirmed, this is a collision of generations that could define the film's appeal for younger audiences who've grown up with both Aamir's legacy and Vicky's rise.

For NRIs, 3 Idiots holds a special place. It's the film that crossed language barriers at diaspora dinner parties, that became shorthand for conversations about the Indian education system, that every second-generation kid has been told to watch. A sequel doesn't just carry commercial weight — it carries cultural expectation.

## And Then, Something Entirely New

Aamir has also confirmed a superhero film with Tamil director Lokesh Kanagaraj, creator of the Kaithi universe and one of South Indian cinema's most commercially potent filmmakers. During a recent press interaction, Aamir said plainly: "It belongs to the superhero genre. It's a big-scale action film and will go on floors in the second half of 2026."

This is Aamir's first superhero project and his first collaboration with a South Indian director. It signals something broader about where Bollywood's biggest names are looking for creative partnerships — increasingly southward.

## What It Means for the Diaspora

The practical upside: NRI audiences who typically get one Aamir Khan theatrical event every few years may see three in relatively quick succession. The first could land in late 2027 or early 2028, with the other two following within 18 months.

The deeper signal: India's most deliberate actor has decided that the current moment — with mythological epics, franchise sequels, and cross-industry collaborations redefining the market — requires him to move faster than his instincts usually allow.

Whether all three land with the impact of his best work remains an open question. What's not in question is that Aamir Khan, at 61, is betting bigger on his next chapter than he has on any chapter before.""",
        "sources": json.dumps([
            {"name": "Sacnilk", "url": "https://sacnilk.com/articles/bollywood/aamir-khan-shoots-timeline-ashutosh-gowarikar-3-idiots-sequel"},
            {"name": "Sacnilk", "url": "https://sacnilk.com/articles/bollywood/aamir-khan-lokesh-kanagaraj-superhero-film-confirmed"},
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com/news/bollywood/aamir-khan-rajkumar-hirani-dadasaheb-phalke-biopic/"}
        ]),
    },
    {
        "headline": "David Dhawan Says Hai Jawani Toh Ishq Hona Hai Will Be His Last Film. Bollywood's Comedy King Just Got a Film Festival in His Honour.",
        "subheadline": "The veteran director behind Coolie No 1, Hero No 1, and Biwi No 1 hints at retirement due to health. PVR INOX launched a David Dhawan Film Festival. Salman Khan showed up. The film opens June 5.",
        "slug": "david-dhawan-retirement-hai-jawani-film-festival-pvr-salman-khan-varun-dhawan-nri-20260530",
        "image_people": ["David Dhawan"],
        "pexels_fallback": ("Bollywood comedy film set", "Indian cinema director"),
        "body": """David Dhawan's retirement announcement didn't arrive in a dramatic press conference. It came the way most real things do in Bollywood — in a quiet aside during a promotional interaction.

"I don't think I should do more," the 69-year-old director said recently. "This might be my last film. After this, I'll just be Varun's father."

The film in question is Hai Jawani Toh Ishq Hona Hai, a comedy starring his son Varun Dhawan alongside Mrunal Thakur and Pooja Hegde. It releases on June 5 — and if Dhawan means what he says, it closes a career that defined what mainstream Bollywood comedy looked and sounded like for an entire generation.

## The No. 1 Legacy

For NRIs of a certain vintage, David Dhawan's filmography isn't a list of movies — it's a soundtrack to childhood weekends. Coolie No 1. Hero No 1. Biwi No 1. Judwaa. Haseena Maan Jaayegi. These were the films that played on rented VHS tapes and pirated DVDs in living rooms from Edison to Southall to Brampton.

His formula was simple and unashamed: mistaken identities, family chaos, catchy songs, and Govinda. The Govinda-David Dhawan partnership alone produced 17 films — a run of mass comedy that has no parallel in Hindi cinema. When Karisma Kapoor joined the equation, the results were even more electric.

Modern sensibilities might question some of the humour. That's fair. But what's harder to argue with is Dhawan's instinct for what the broadest possible audience wanted to feel when they sat down in a theatre: entertained, relaxed, unburdened. In an industry now obsessed with looking premium and curated, that instinct has become alarmingly rare.

## The Film Festival Farewell

PVR INOX hosted a David Dhawan Film Festival in Mumbai ahead of the release, screening his classics across multiplexes. Salman Khan attended the launch event, where he and Varun Dhawan shared a stage celebrating the director's legacy.

The evening produced a perfectly Bollywood moment: Salman joked that Varun had "picked up another one" of his songs — a reference to the recreated version of Chunari Chunari from Biwi No 1 that features in the new film. Original composer Anu Malik gave his public blessing, calling Varun's performance outstanding.

The film itself is classic David Dhawan territory: a chaotic love triangle with Varun, Mrunal, and Pooja, supported by Jimmy Shergill, Mouni Roy, Chunky Panday, and Maniesh Paul. It's the fourth collaboration between father and son, after Main Tera Hero, Judwaa 2, and the 2020 Coolie No 1 reboot.

## A Diaspora Goodbye

For the diaspora, Dhawan's retirement means something specific. His films were gateway Bollywood — the ones you could show anyone without explanation, the ones that needed no subtitles beyond laughter. They were the films that made uncles quote dialogue at family gatherings and aunties hum songs while cooking.

Whether Hai Jawani Toh Ishq Hona Hai genuinely marks the end or becomes one of Bollywood's many "last films" that aren't, the acknowledgment matters. The industry is losing one of the last directors who truly understood that sometimes, the audience just wants to laugh for three hours and walk out feeling lighter.

Health concerns are reportedly a factor in the decision. Dhawan hasn't elaborated publicly, but his candour about stepping back — "I'll just be Varun's father" — suggests a man who has made his peace with the transition.

The film opens June 5. For fans who grew up on the No. 1 series, that's worth marking on the calendar.""",
        "sources": json.dumps([
            {"name": "Filmfare", "url": "https://www.filmfare.com/news/bollywood/david-dhawan-to-retire-post-hai-jawani-toh-ishq-hona-hai"},
            {"name": "Mirchi", "url": "https://www.mirchi.in/bollywood/salman-khan-varun-dhawan-david-dhawan-film-festival"},
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com/news/bollywood/david-dhawan-retirement-bollywood-comedy/"}
        ]),
    },
    {
        "headline": "Ranveer Singh's Pralay Will Start Filming in August. The FWICE Ban Doesn't Seem to Be Stopping Anything.",
        "subheadline": "While the Don 3 dispute rages on — with Salman Khan now playing peacemaker — Ranveer's next project, a survival drama, is moving forward on schedule. The actor isn't sitting still.",
        "slug": "ranveer-singh-pralay-august-filming-fwice-ban-don-3-salman-khan-peace-nri-20260530",
        "image_people": ["Ranveer Singh"],
        "pexels_fallback": ("Bollywood actor press conference", "Indian film industry"),
        "body": """The Federation of Western India Cine Employees issued a non-cooperation directive against Ranveer Singh on May 25. Five days later, his next film has locked a shooting start date.

Pralay, described as a survival drama, is set to begin filming in August 2026 — directly defying the implicit threat of industry isolation that the FWICE directive carries. If there was any ambiguity about whether the Don 3 fallout would derail Ranveer's career momentum, the answer appears to be: not yet.

## How We Got Here

The sequence of events is worth understanding, because it tells a story about how Bollywood's power structures work — and don't.

Ranveer was attached to Don 3, Farhan Akhtar's franchise reboot, since its announcement in August 2023. Reports indicate he exited just weeks before shooting was set to begin. His side says the script was never finalized and he had fundamental creative differences — he wanted a darker, more aggressive Don. Farhan's side says the script was shared in stages and approved by the actor, and that Excel Entertainment had already incurred massive pre-production costs.

Farhan's production house filed a formal complaint. FWICE issued its non-cooperation directive after claiming Ranveer failed to attend multiple meetings. Then CINTAA — a separate industry body — came out in Ranveer's support. Padmini Kolhapure, the CINTAA president, publicly backed his position.

So now there are two industry bodies on opposite sides of the same dispute. That kind of institutional split is rare and revealing.

## Salman Khan, Playing Cupid

In the middle of all this, Salman Khan stepped in as mediator. According to multiple reports confirmed by Bollywood Hungama, Salman personally called both Ranveer and Farhan.

The message was characteristically direct: resolve it between yourselves, don't involve third parties, don't let it damage the industry. A source quoted Salman as saying he explained to Farhan that creative differences are "a common thing in the industry for decades" while also having "a long chat with Ranveer, understanding his stance."

Both parties have reportedly taken the words seriously. There's talk of eventually working together again once tensions cool.

The mediation is significant beyond the gossip value. In an industry that's becoming increasingly corporatized and contract-driven, Salman's intervention represents the older power model — where relationships and personal authority matter more than legal frameworks. Whether that's a good or bad thing depends on your perspective. But it's clearly still effective.

## What Pralay Means

Pralay itself is a new genre territory for Ranveer. Details are thin, but it's described as a survival drama — a departure from the franchise action and historical epics that have defined his recent career. The fact that it's moving forward suggests that producers are willing to work with Ranveer despite the FWICE directive, which is technically a recommendation to its member technicians not to work with him.

The practical reality: FWICE directives carry weight with below-the-line crew but don't have legal enforcement power. Major producers with established relationships can work around them, especially when a competing industry body is publicly supporting the actor.

## The Diaspora Perspective

For NRI audiences, the Don 3 saga is one of those inside-Bollywood dramas that sounds exotic until you realize it's just a contract dispute dressed in celebrity clothing. But the underlying tensions — creative control versus producer investment, actor autonomy versus institutional power, the old handshake model versus Hollywood-style contracts — are genuinely interesting.

What matters commercially is simpler: Ranveer Singh, coming off the historic ₹1,800-crore worldwide success of Dhurandhar 2, is still making movies. The FWICE ban has not created the career crisis it might have in a less fragmented industry. And Pralay, whatever it turns out to be, will have one of the biggest stars in Indian cinema at its centre when cameras roll in August.""",
        "sources": json.dumps([
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com/news/bollywood/ranveer-singh-pralay-filming-august-fwice/"},
            {"name": "Filmfare", "url": "https://www.filmfare.com/news/bollywood/salman-khan-intervenes-don-3-ranveer-singh-farhan-akhtar"},
            {"name": "LatestLY", "url": "https://www.latestly.com/entertainment/bollywood/don-3-salman-khan-ranveer-singh-farhan-akhtar-dispute.html"},
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com/news/bollywood/cintaa-padmini-kolhapure-ranveer-singh-fwice/"}
        ]),
    },
]

# ── Publish ─────────────────────────────────────────────────────
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

for i, art in enumerate(articles, 1):
    print(f"\n{'='*60}")
    print(f"Article {i}/{len(articles)}: {art['headline'][:70]}...")

    # ── Image sourcing ──
    image_url = None
    image_attribution = None

    # Try Wikipedia for person articles
    for person in art.get("image_people", []):
        image_url = fetch_wikipedia_person_image(person)
        if image_url and validate_image_url(image_url):
            image_attribution = "Wikimedia Commons"
            break
        image_url = None

    # Pexels fallback
    if not image_url and art.get("pexels_fallback"):
        q1, q2 = art["pexels_fallback"]
        image_url = fetch_pexels_image(q1, q2)
        if image_url and validate_image_url(image_url):
            image_attribution = "Pexels"
        else:
            image_url = None

    if not image_url:
        print("  ⚠ No image found — publishing without image")

    # ── Insert article ──
    payload = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "body": art["body"],
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now,
        "sources": json.loads(art["sources"]),
        "image_url": image_url,
        "image_attribution": image_attribution,
    }

    result = sb_insert("p2_articles", payload)
    if result:
        art_id = result[0].get("id") if isinstance(result, list) else result.get("id")
        print(f"  ✓ Published: {art['slug']} (id: {art_id})")
    else:
        print(f"  ✗ Failed to publish: {art['slug']}")

    time.sleep(1)

print(f"\n{'='*60}")
print(f"Done. Published {len(articles)} entertainment articles.")
