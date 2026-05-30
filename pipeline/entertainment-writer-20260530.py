#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-30 batch"""

import os, json, requests, urllib.parse, uuid, re, time
from datetime import datetime, timezone

# ── Supabase config ──────────────────────────────────────────────────────────
SB_URL  = os.environ["SUPABASE_URL"]
SB_KEY  = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS  = os.environ.get("PEXELS_API_KEY", "")
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Image helpers ────────────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels using curl (Python urllib gets 403)."""
    if not PEXELS:
        print("  ⚠ No Pexels key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            cmd = [
                "curl", "-sS",
                f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5",
                "-H", f"Authorization: {PEXELS}",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Check if image URL returns 200 with image content-type and >5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD didn't give Content-Length
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def is_banned_url(url):
    """Check if URL is from a banned source."""
    if not url:
        return True
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "scontent-"]
    banned_params = ["_nc_ht=", "_nc_cat=", "ccb="]
    for b in banned:
        if b in url:
            return True
    for p in banned_params:
        if p in url:
            return True
    return False


def get_image(person_name=None, pexels_query=None, pexels_fallback=None):
    """Get image URL using the hierarchy: Wikipedia → Pexels → None."""
    img = None
    attribution = None

    if person_name:
        img = fetch_wikipedia_person_image(person_name)
        if img and not is_banned_url(img) and validate_image(img):
            return img, "Wikimedia Commons"
        # Try alternate forms
        for alt in [f"{person_name} (actor)", f"{person_name} (actress)", f"{person_name} (filmmaker)"]:
            img = fetch_wikipedia_person_image(alt)
            if img and not is_banned_url(img) and validate_image(img):
                return img, "Wikimedia Commons"

    if pexels_query:
        img = fetch_pexels_image(pexels_query, pexels_fallback)
        if img and not is_banned_url(img) and validate_image(img):
            return img, "The Videshi"

    return None, None


# ── Supabase helpers ─────────────────────────────────────────────────────────
def sb_insert(article):
    """Insert article into p2_articles."""
    r = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Published: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return None


# ── Articles ─────────────────────────────────────────────────────────────────
def build_articles():
    articles = []
    now = datetime.now(timezone.utc).isoformat()

    # ──────────────────────────────────────────────────────────────────────────
    # ARTICLE 1: Cocktail 2 Trailer Postponed
    # ──────────────────────────────────────────────────────────────────────────
    articles.append({
        "headline": "Cocktail 2 Trailer Pushed to June 2. The Film Still Opens June 19, But Nobody's Saying Why.",
        "subheadline": "Maddock Films delays Shahid Kapoor, Kriti Sanon, and Rashmika Mandanna's trailer launch at the last minute, opting for a tighter marketing window",
        "slug": "cocktail-2-trailer-postponed-june-2-shahid-kapoor-kriti-sanon-rashmika-maddock-nri-20260530",
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now,
        "sources": json.dumps([
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "Filmibeat", "url": "https://www.filmibeat.com"},
            {"name": "Sacnilk", "url": "https://www.sacnilk.com"}
        ]),
        "body": """The first real promotional beat of Cocktail 2 has been delayed. Maddock Films was scheduled to unveil the trailer on May 29 at a dedicated event in Mumbai, but the launch was pulled at the last moment. The new date is June 2, pushing the reveal closer to the film's theatrical opening on June 19.

The production house confirmed that the postponement applies only to the trailer. The film's release date remains unchanged. No detailed explanation was offered for the shift, though industry sources describe the decision as part of a broader strategy to compress the marketing cycle into a tighter window leading directly into the theatrical release.

## A Sequel Fourteen Years in the Making

The original Cocktail, released in 2012, became a cultural touchstone for urban Indian audiences. Directed by Homi Adajania, the film starred Saif Ali Khan, Deepika Padukone, and Diana Penty in a story about friendship, love, and the messy complications that arise when the two collide. Its soundtrack, anchored by "Tumhi Ho Bandhu" and "Angrezi Beat," became defining songs of that era.

Cocktail 2 is positioned as a spiritual successor rather than a direct sequel. It carries the franchise's DNA — contemporary romance, urban settings, emotional complexity — but arrives with an entirely new cast and story. The film brings together Shahid Kapoor, Kriti Sanon, and Rashmika Mandanna, a combination designed for maximum pan-India reach.

## The Cast Factor

Shahid Kapoor and Kriti Sanon are reuniting after their 2024 film Teri Baaton Mein Aisa Uljha Jiya, which performed well at the box office. Their chemistry is a known quantity. Rashmika Mandanna, meanwhile, brings a growing pan-India appeal that cuts across language barriers — she's one of the few actresses equally comfortable headlining Telugu and Hindi releases.

The production team is stacked too. Adajania returns to direct, producers Dinesh Vijan and Luv Ranjan are co-producing, and Pritam Chakraborty is handling the music. At an earlier press event in Mumbai, the team previewed two unreleased tracks — Mashooka, an energetic romantic number reportedly shot in Sicily, and Tujhko, an emotional ballad sung by Arijit Singh.

## What the Delay Signals

Trailer launches in Bollywood are rarely delayed without reason. The most common explanation is a strategic one: the makers may have concluded that three weeks of promotional buildup is more effective than four. In a market where audience attention spans are fragmented across platforms, a compressed campaign can maintain intensity without fatigue.

The other possibility is more practical. June 2 places the trailer squarely at the start of the month, giving it clean digital real estate without competing with the end-of-May content rush from multiple streaming platforms.

## The NRI Angle

For diaspora audiences who grew up with the original Cocktail, the sequel arrives with built-in nostalgia. The 2012 film captured a particular moment in urban Indian life — the tensions between traditional expectations and modern relationships — that resonated deeply with NRIs navigating similar cultural dualities abroad. Whether Cocktail 2 can recapture that lightning in a bottle with a new generation of stars remains the central question.

The film opens in theatres worldwide on June 19. The trailer drops June 2. Between now and then, the music is doing the heavy lifting.""",
        "person_name": "Shahid Kapoor",
        "pexels_query": None,
    })

    # ──────────────────────────────────────────────────────────────────────────
    # ARTICLE 2: Ishaan Khatter Biarritz Jury
    # ──────────────────────────────────────────────────────────────────────────
    articles.append({
        "headline": "Ishaan Khatter Is the Only Indian on the Biarritz Film Festival Jury. Kristen Stewart Is Chairing It.",
        "subheadline": "The actor joins an international jury panel alongside Whitney Peak, Raphaël Quenard, and emerging European filmmakers for the festival's fourth edition in June",
        "slug": "ishaan-khatter-biarritz-film-festival-jury-kristen-stewart-india-nri-20260530",
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now,
        "sources": json.dumps([
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "ANI", "url": "https://www.aninews.in"},
            {"name": "Biarritz Film Festival", "url": "https://www.biarritzfilmfestival.com"}
        ]),
        "body": """Ishaan Khatter has been invited to serve on the jury at the Biarritz Film Festival – Nouvelles Vagues 2026, which takes place from June 23 to June 28 in the French coastal city of Biarritz. He is the only Indian actor on this year's panel.

The jury will be chaired by Kristen Stewart, the American actress and filmmaker who has moved between blockbuster franchises and arthouse cinema with uncommon ease. The rest of the panel includes Canadian actress Whitney Peak, French actor-director Raphaël Quenard, French filmmaker Nathan Ambrosioni, actress Suzy Bemba, Italian director Carolina Cavalli, and British actress Esmé Creed-Miles.

## A Festival Built for the Next Generation

The Biarritz Film Festival – Nouvelles Vagues is now in its fourth edition and has carved a specific niche: cinema centered on younger generations and emerging voices. Unlike Cannes, which trades on prestige and industry commerce, Biarritz focuses on spotlighting the future of global storytelling. Its programming leans toward contemporary narratives and new creative talent from across the world.

For an Indian actor to sit on this jury is not unprecedented, but it remains rare. Indian presence at European film festivals has historically been concentrated among directors — Satyajit Ray at Cannes, Mira Nair at Venice, Anurag Kashyap at various festivals. Actors on jury duty represent a different kind of recognition: an acknowledgement of cultural fluency and international standing beyond any single film.

## Ishaan's Quiet International Build

Ishaan Khatter's path to this invitation has been deliberate rather than explosive. His breakout role in Majid Majidi's Beyond the Clouds (2017) gave him an early international platform. The Mira Nair-directed A Suitable Boy, a BBC/Netflix co-production, introduced him to global audiences in a literary adaptation that required classical restraint rather than Bollywood energy.

More recently, The Royals expanded his digital presence, and Homebound earned attention in festival and critical circles. His approach has been to build range rather than rely on any single commercial formula — a strategy that may explain why a European festival known for championing new voices invited him to judge their selections.

Earlier this year, Ishaan was featured on the Gold House Gold 100 list, becoming the only Indian male actor in this year's lineup. The list recognizes influential Asian and Pacific figures across industries and is closely watched in Asian American cultural circles.

## What This Means for the Diaspora

For the Indian diaspora, particularly in Europe, Ishaan's jury appointment at Biarritz registers on multiple levels. It confirms that Indian cinema and Indian actors are being evaluated as part of the global conversation, not adjacent to it. When a jury chaired by Kristen Stewart includes an Indian actor alongside European and American peers, the message is structural: the boundaries between film industries are dissolving.

Ishaan's next project is Jugaadu, a comic caper that also marks his first venture into production. He shared his first look from the film on Instagram earlier this month, signaling that even as his international profile grows, he isn't abandoning the Hindi commercial space.

The festival runs for six days in late June. For Ishaan, it's another data point in an argument he seems to be making through his career: that an Indian actor can occupy both spaces at once — domestic commercial cinema and the international festival circuit — without treating either as a compromise.""",
        "person_name": "Ishaan Khatter",
        "pexels_query": None,
    })

    # ──────────────────────────────────────────────────────────────────────────
    # ARTICLE 3: Dhurandhar 2 OTT Release
    # ──────────────────────────────────────────────────────────────────────────
    articles.append({
        "headline": "Dhurandhar 2 Hits JioHotstar on June 4. It's Already on Netflix Abroad. Here's Why India Is Getting It Last.",
        "subheadline": "The ₹1,800-crore spy thriller gets a unique dual-platform OTT rollout — JioHotstar in India, Netflix internationally — after the makers re-auctioned rights mid-run",
        "slug": "dhurandhar-2-jiohotstar-june-4-netflix-ranveer-singh-ott-india-nri-20260530",
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now,
        "sources": json.dumps([
            {"name": "Cinema Express", "url": "https://www.cinemaexpress.com"},
            {"name": "Digit", "url": "https://www.digit.in"},
            {"name": "Bollywood Life", "url": "https://www.bollywoodlife.com"}
        ]),
        "body": """Dhurandhar 2: The Revenge, the second-biggest Indian grosser of all time at ₹1,800 crore worldwide, is finally heading to Indian living rooms. JioHotstar will begin streaming the Ranveer Singh spy thriller on June 4 at 7 PM IST. But if you're reading this from the US, UK, or Canada, you might already have watched it — the film has been available on Netflix internationally since May 14.

The staggered rollout is not a mistake. It's the result of one of the most unusual OTT rights battles in Indian film history.

## The Rights Shuffle

The original Dhurandhar's streaming rights were sold to Netflix before the film released theatrically in December 2025. When the first installment became a historic blockbuster, the makers reopened negotiations for the sequel's digital rights. The bidding war that followed was won by JioHotstar for the Indian market.

Netflix, however, retained international streaming rights for the sequel — a split arrangement that explains the current situation. NRIs in the US, UK, and Middle East got Dhurandhar 2 on Netflix three weeks ago. Indian viewers are still waiting.

The dual-platform strategy extends to the first film as well. A new version titled "Dhurandhar: Raw and Undekha" — billed as an uncut edition — premiered simultaneously on both Netflix and JioHotstar on May 22. The new version doesn't add scenes or extend the runtime (it remains 3 hours and 25 minutes), but it includes modifications to dialogue and visual censorship that fans have noted are subtle rather than dramatic.

## Why This Matters for the Industry

The Dhurandhar franchise has fundamentally altered how Indian films negotiate OTT deals. The traditional model was simple: one platform buys all digital rights, domestic and international. The split-rights approach pioneered here allows makers to maximize revenue by leveraging the strengths of different platforms in different markets.

JioHotstar dominates the Indian streaming landscape with its bundled telecom model. Netflix commands the international Indian diaspora audience. By selling to both, the makers captured two separate revenue pools instead of one.

Industry trackers believe this model will become standard for future blockbusters. The question is whether it creates confusion for audiences or simply reflects the reality of a fragmented global streaming market.

## The Legal Cloud

The OTT release arrives under an unusual legal shadow. The Delhi High Court is examining a public interest litigation filed by an SSB head constable alleging that the film depicts confidential information related to army operations. The court has directed the Ministry of Information and Broadcasting and the CBFC to investigate, noting that even if the film is fictional, concerns raised by security personnel cannot be ignored.

The legal proceedings have not affected the streaming release schedule, but they add an unusual dimension to a film that has otherwise been celebrated as a commercial triumph.

## What NRIs Should Know

If you're in the US, UK, Canada, or Middle East with a Netflix subscription, you've likely already had access to Dhurandhar 2 since mid-May. The JioHotstar release is relevant if you have family in India who haven't seen it yet, or if you prefer JioHotstar's interface and its Hindi-Tamil-Telugu language options.

For the Indian audience, the June 4 premiere means the wait is finally over. Directed by Aditya Dhar, the film stars Ranveer Singh as undercover intelligence officer Jaskirat Singh Rangi alongside R. Madhavan, Sanjay Dutt, Arjun Rampal, Sara Arjun, and Rakesh Bedi. Netflix India gets it two weeks later on June 19 — another staggered window within the same market.""",
        "person_name": "Ranveer Singh",
        "pexels_query": None,
    })

    # ──────────────────────────────────────────────────────────────────────────
    # ARTICLE 4: August Box Office War
    # ──────────────────────────────────────────────────────────────────────────
    articles.append({
        "headline": "Four South Indian Superstars Are Releasing Films Within Eight Days in August. Theatre Owners Are Sweating.",
        "subheadline": "Suriya, Nani, Dulquer Salmaan, and Prithviraj Sukumaran will compete for screens in the most crowded South Indian box office window of the year",
        "slug": "august-2026-south-indian-box-office-clash-suriya-nani-dulquer-prithviraj-nri-20260530",
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now,
        "sources": json.dumps([
            {"name": "Sacnilk", "url": "https://www.sacnilk.com"},
            {"name": "Filmibeat", "url": "https://www.filmibeat.com"}
        ]),
        "body": """August 2026 is shaping up to be the most congested — and potentially the most consequential — box office window South Indian cinema has seen in years. Within a span of just eight days, four major superstars are bringing highly anticipated projects to theatres. The lineup creates a feast for moviegoers and a logistical nightmare for exhibitors.

## The Collision Course

The sequence begins on August 14 with Suriya's Vishwanath and Sons. Directed by Venky Atluri, the film is a family drama and sports romance in which Suriya plays an international pistol-shooting champion. It's a bilingual, shot simultaneously in Tamil and Telugu, and stands out from the rest of the lineup as the only non-action-genre entry. The two-day head start gives it a window to build word-of-mouth before the real storm hits.

That storm arrives on August 20, when three films collide on the same day.

Nani's The Paradise has been generating international buzz since reports emerged that Hollywood star Ryan Reynolds was approached for a collaborative role. The film targets a multilingual global release with visual language and tone designed to appeal across Eastern and Western audiences. If confirmed, the Reynolds connection could mark one of the most high-profile Indo-Hollywood collaborations in recent memory.

On the same day, Dulquer Salmaan's I'm Game hits screens. Directed by Nahas Hidayath, it's a pan-Indian action-thriller set in the world of cricket betting and fantasy gaming — a subject with obvious relevance to Indian audiences worldwide.

And completing the triple collision is Prithviraj Sukumaran's Khalifa: The Bloodline, an underworld saga that features an extended cameo by Mohanlal. The pairing of Prithviraj and Mohanlal has already sent expectations through the roof in Kerala and the Middle East, where both actors command enormous diaspora followings.

## What This Means for Exhibitors

The fundamental tension is screen allocation. South Indian cinema operates across multiple language markets — Tamil, Telugu, Malayalam, Kannada — each with its own exhibition ecosystem. When four major releases compete simultaneously, theatre owners must make impossible choices about which films get premium showtimes and which get squeezed.

For single-screen theatres, the challenge is existential. They can show one film at a time. For multiplexes, the math is slightly more forgiving, but even an eight-screen multiplex can only dedicate so many slots to South Indian releases when Hindi and Hollywood titles also compete for space.

Industry analysts are divided on whether this clustering is healthy. Some argue that a concentrated release window generates collective excitement and drives overall footfall — a rising tide that lifts all boats. Others worry that all four films will cannibalize each other's opening weekends, and that at least one or two will underperform relative to their potential.

## The NRI Market Factor

For diaspora audiences, particularly in the US, UK, Canada, and the Middle East, the August clash has specific implications. International screens allocated to Indian films are limited. A typical US metro might have five to ten screens showing Indian films on any given weekend. When four major South Indian releases compete for those slots, some films will inevitably get fewer shows or delayed starts in overseas markets.

The counterargument is that the diaspora audience for each of these stars is somewhat distinct. Suriya and Nani draw primarily from Tamil and Telugu markets; Dulquer and Prithviraj command Kerala and pan-South Indian audiences. There may be less direct competition than the calendar suggests.

## The Bigger Question

August 2026 will serve as a stress test for the South Indian exhibition ecosystem. If all four films perform well, it validates the industry's confidence in its audience base. If the window produces casualties, it will strengthen the argument for more coordinated release planning — a conversation that has been simmering since the post-pandemic theatrical recovery began.

For now, the stars are locked in. The countdown has started. Theatre owners are doing the math.""",
        "person_name": "Nani (actor)",
        "pexels_query": "Indian cinema theatre crowd",
        "pexels_fallback": "movie theatre India",
    })

    # ──────────────────────────────────────────────────────────────────────────
    # ARTICLE 5: CINTAA vs FWICE Union War
    # ──────────────────────────────────────────────────────────────────────────
    articles.append({
        "headline": "CINTAA Has Officially Backed Ranveer Singh. FWICE Wants Him Blacklisted. Bollywood's Biggest Union War Just Got Personal.",
        "subheadline": "Two of the film industry's most powerful bodies are now on opposite sides over the Don 3 dispute, raising fundamental questions about who governs Bollywood's labor disputes",
        "slug": "cintaa-fwice-ranveer-singh-don-3-union-war-bollywood-nri-20260530",
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now,
        "sources": json.dumps([
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "BlazeT rends", "url": "https://www.blazetrends.com"},
            {"name": "Madhyamam Online", "url": "https://www.madhyamamonline.com"}
        ]),
        "body": """What started as a casting dispute over Don 3 has escalated into the most significant institutional confrontation in Bollywood's labor ecosystem in years. Two of the film industry's most powerful bodies — the Cine and TV Artistes' Association (CINTAA) and the Federation of Western India Cine Employees (FWICE) — are now publicly and irreconcilably on opposite sides over Ranveer Singh.

## The Fault Lines

FWICE, which represents workers across 30 crafts in the western Indian film industry, issued a non-cooperation directive against Ranveer Singh after filmmaker Farhan Akhtar filed a formal complaint alleging that the actor's sudden exit from Don 3 caused financial losses of approximately ₹45 crore. The complaint, submitted on April 11, detailed pre-production expenses, location scouting costs, and development investments that were rendered moot by the withdrawal.

FWICE issued three notices to Ranveer asking him to appear and explain his position. When his legal team responded by challenging the federation's jurisdiction over what they described as an independent commercial agreement between an actor and a production company, FWICE escalated. The non-cooperation directive instructs members across all departments of the film industry not to work on Ranveer Singh's future projects or commercial advertisements until the matter is resolved.

Then CINTAA entered the picture.

## The Counter-Move

CINTAA Vice-President and veteran actress Padmini Kolhapure made the association's position unambiguous: "CINTAA is proud to have Ranveer Singh as our member. We stand by him and for him whenever he needs us." CINTAA President Poonam Dhillon went further, calling FWICE's unilateral action "strange," particularly since neither the actor nor the producers had consulted the artistes' association before the directive was issued.

The jurisdictional question at the heart of this dispute is fundamental. FWICE governs craft workers — technicians, crew, production staff. CINTAA represents actors. When FWICE issues a directive that effectively restricts an actor's ability to work, it encroaches on territory that CINTAA considers its own.

## Ranveer's Calculated Silence

Throughout the escalation, Ranveer Singh has maintained a deliberate silence. His spokesperson released a single statement: "Ranveer Singh holds the highest regard for the film fraternity and for everyone associated with the Don franchise. He has consciously chosen to maintain silence, believing that professional discussions and personal equations are best handled with dignity, maturity and mutual respect."

The statement is notable for what it doesn't say. It doesn't acknowledge FWICE's authority. It doesn't dispute the ₹45 crore figure. It doesn't explain why he exited Don 3. The silence itself has become a strategy — by refusing to engage with FWICE's process, Ranveer's team is implicitly arguing that the federation has no standing in this matter.

## The Industry Implications

The CINTAA-FWICE divide exposes a structural vulnerability in Bollywood's self-governance. Unlike Hollywood, where the Screen Actors Guild and other unions have clearly delineated jurisdictions backed by decades of labor law, India's film industry operates through a patchwork of voluntary associations with overlapping and sometimes contradictory mandates.

If FWICE can blacklist an actor, and CINTAA can override that blacklist, the question becomes: whose writ runs? The practical answer, at least for a star of Ranveer Singh's stature, is that no federation can meaningfully prevent him from working. Producers will cast whoever they believe will sell tickets. But for mid-tier and emerging actors, the precedent matters enormously. A non-cooperation directive from FWICE could end a career that CINTAA's verbal support alone cannot save.

## What NRIs Are Watching

For the diaspora audience, this dispute is a window into how Bollywood actually works behind the glamour. The Don 3 saga — which began as a simple question of whether Ranveer Singh would play Don — has become a case study in the industry's governance gaps. The resolution, whenever it comes, will say a great deal about whether Bollywood can modernize its institutional framework or remains governed by the loudest voice in the room.""",
        "person_name": "Padmini Kolhapure",
        "pexels_query": "Bollywood film industry",
        "pexels_fallback": "Indian cinema industry",
    })

    return articles


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    articles = build_articles()
    published = 0

    for i, art in enumerate(articles, 1):
        print(f"\n{'='*60}")
        print(f"Article {i}/{len(articles)}: {art['headline'][:60]}...")
        print(f"{'='*60}")

        # Image sourcing
        person = art.pop("person_name", None)
        pq = art.pop("pexels_query", None)
        pf = art.pop("pexels_fallback", None)

        img_url, attribution = get_image(
            person_name=person,
            pexels_query=pq,
            pexels_fallback=pf,
        )

        if img_url:
            art["image_url"] = img_url
            art["image_attribution"] = attribution
            print(f"  ✓ Image set: {img_url[:60]}...")
        else:
            print(f"  ⚠ No image found — publishing without image")

        # Validate article
        body_words = len(art["body"].split())
        if body_words < 400:
            print(f"  ✗ Body too short ({body_words} words) — skipping")
            continue

        if len(art["headline"]) > 200:
            print(f"  ⚠ Headline too long ({len(art['headline'])} chars) — truncating")
            art["headline"] = art["headline"][:197] + "..."

        if len(art.get("subheadline", "")) < 15:
            print(f"  ✗ Subheadline too short — skipping")
            continue

        print(f"  Body: {body_words} words")
        print(f"  Slug: {art['slug']}")

        # Publish
        art_id = sb_insert(art)
        if art_id:
            published += 1
        
        time.sleep(1)  # Brief pause between inserts

    print(f"\n{'='*60}")
    print(f"Done. Published {published}/{len(articles)} articles.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
