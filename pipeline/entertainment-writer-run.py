#!/usr/bin/env python3
"""Entertainment writer — scheduled run for The Videshi"""
import json, os, re, sys, time, uuid, urllib.parse
import requests
from datetime import datetime, timezone

# ── Load env ──
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.replace("export ", "").strip()
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ── Wikipedia image fetch ──
def fetch_wikipedia_person_image(person_name):
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
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:100]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

# ── Pexels fallback ──
def fetch_pexels_image(query):
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": query, "per_page": 3, "orientation": "landscape"},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image: {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

# ── Validate image ──
def validate_image(url):
    if not url:
        return False
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat=", "ccb="]
    for b in banned:
        if b in url:
            print(f"  ✗ Banned source: {b}")
            return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image valid: {ct}, {cl} bytes")
            return True
        print(f"  ✗ Image invalid: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Validate error: {e}")
    return False

# ── Insert article ──
def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if r.status_code in (200, 201):
        data = r.json()
        aid = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Published: {article['headline'][:60]}... (id={aid})")
        return aid
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ────────────────────────────────────────
# ARTICLE 1: Naga Chaitanya Delhi HC Case
# ────────────────────────────────────────

def article_naga_chaitanya():
    print("\n=== Article 1: Naga Chaitanya Delhi HC ===")
    slug = "naga-chaitanya-delhi-hc-deepfakes-ai-samantha-personality-rights-nri-20260601"

    img = fetch_wikipedia_person_image("Naga Chaitanya")
    if not img or not validate_image(img):
        img = fetch_wikipedia_person_image("Naga Chaitanya (actor)")
        if not img or not validate_image(img):
            img = fetch_pexels_image("Delhi High Court India")
            if not validate_image(img):
                img = None

    headline = "Naga Chaitanya Went to the Delhi High Court Over AI Deepfakes. The Allegations Link Back to Samantha."
    subheadline = "The Telugu star is fighting fabricated videos, cloned voices, and years of online speculation about his divorce — and the court is listening."

    body = """The intersection of celebrity, technology, and harassment has rarely been laid this bare in an Indian courtroom. On May 29, Telugu star Naga Chaitanya appeared through counsel before Justice Jyoti Singh of the Delhi High Court, seeking sweeping protection for what legal filings describe as a systematic assault on his personality rights across the internet.

The petition isn't about hurt feelings or negative reviews. It's about deepfake pornography, AI-generated videos depicting the actor in fabricated compromising situations, cloned voice recordings, and a sprawling cottage industry of websites that use his name alongside explicit search terms to drive traffic. His legal team, led by Senior Advocate Vaibhav Gaggar, told the court that this is "trolling, not fair criticism."

## The Samantha Connection

At the centre of the petition lies content that has dogged Chaitanya since his 2021 divorce from actress Samantha Ruth Prabhu. Despite both actors issuing a joint statement at the time requesting privacy, the internet has spent five years manufacturing narratives. Posts and videos circulating online allege — without evidence — that Chaitanya cheated on Samantha and systematically destroyed her career.

The allegations have never been substantiated. Samantha has not publicly supported these claims. Both actors have remarried — Chaitanya to actress Sobhita Dhulipala, and Samantha, per reports, to filmmaker Raj Nidimoru. Yet the content persists, now supercharged by generative AI tools that can produce convincing fake video and audio with minimal effort.

## What the Court Heard

Gaggar presented the court with evidence of manipulated audiovisual content, unauthorised merchandise bearing Chaitanya's likeness, and borderline-infringing links that use his identity for commercial gain. The advocate argued that advanced digital tools — including deepfake technology and voice cloning software — are being weaponised against his client for profit.

Justice Singh acknowledged the vulnerability. "You're in public life, and that makes you more vulnerable, but there's a line," she told the courtroom. The court has issued summons and indicated that interim orders protecting Chaitanya's personality rights will follow. The next hearing is scheduled for September 30.

## Why This Matters for the Diaspora

For the Telugu-speaking diaspora — particularly in the United States, Canada, and the Gulf — Tollywood celebrities occupy a cultural space that goes beyond entertainment. They are community touchstones, conversation starters at weekend gatherings, and reliable bridges to the culture back home.

The Naga-Samantha divorce was discussed in living rooms from Frisco to Fremont, from Mississauga to Dubai. Much of that conversation was fuelled by the very content Chaitanya is now asking the court to suppress. The case raises uncomfortable questions about what happens when diaspora audiences, often consuming content through algorithmically curated feeds, become unwitting amplifiers of fabricated narratives.

## The Bigger Picture

India's courts have been increasingly receptive to personality rights claims. Chaitanya's father, veteran actor Nagarjuna, previously secured similar protections from the Delhi High Court. The legal framework is evolving, but the technology is evolving faster.

Deepfake tools that once required significant technical expertise are now available as consumer apps. Voice cloning can be accomplished with a few minutes of publicly available audio. For public figures in the Indian entertainment industry — where parasocial relationships run deep and the line between legitimate gossip and fabricated defamation is razor-thin — the threat is existential.

The Chaitanya petition isn't just about one actor protecting his reputation. It's a test case for whether Indian courts can meaningfully police AI-generated harassment in an era when the tools to create it are freely available and the platforms hosting it are often beyond easy jurisdictional reach.

The hearing continues. The deepfakes, for now, do too.

*Sources: ANI, India Forums, Bollywood Bubble, IndulgeExpress, MovieTalkies*"""

    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img,
        "image_attribution": "Wikimedia Commons" if img and ("wikimedia" in (img or "").lower() or "wikipedia" in (img or "").lower()) else "The Videshi",
        "sources": json.dumps(["ANI", "India Forums", "Bollywood Bubble", "IndulgeExpress", "MovieTalkies"])
    }


# ────────────────────────────────────────
# ARTICLE 2: Hai Jawani Toh Ishq Hona Hai
# ────────────────────────────────────────

def article_hai_jawani():
    print("\n=== Article 2: Hai Jawani Toh Ishq Hona Hai ===")
    slug = "hai-jawani-toh-ishq-hona-hai-varun-dhawan-david-dhawan-june-5-nri-20260601"

    img = fetch_wikipedia_person_image("Varun Dhawan")
    if not img or not validate_image(img):
        img = fetch_pexels_image("Bollywood romantic comedy film")
        if not validate_image(img):
            img = None

    headline = "Varun Dhawan and His Father Are Betting ₹55 Crore on a Love Triangle. It Releases Thursday."
    subheadline = "Hai Jawani Toh Ishq Hona Hai is David Dhawan's fourth film with his son — and Bollywood's most expensive family-comedy gamble this summer."

    body = """David Dhawan built an empire on a simple formula: one hero, two heroines, a series of escalating misunderstandings, and an audience willing to laugh at all of it. From Govinda's anarchic energy in the 1990s to his son Varun's attempts to channel it in the 2010s, the elder Dhawan has directed more rom-com chaos than perhaps any other filmmaker in Hindi cinema.

On June 5, the father-son duo bets on that formula one more time. Hai Jawani Toh Ishq Hona Hai — a title that sounds like it was written on a Punjabi wedding invitation — stars Varun Dhawan alongside Mrunal Thakur and Pooja Hegde. The plot, as described by the filmmakers, follows Jass, who finds himself in love with both Baani and Preet. Complications arrive when both become pregnant simultaneously.

## The Numbers Behind the Nostalgia

The reported budget is ₹55 crore, a significant outlay for a genre that Indian cinema has increasingly abandoned in favour of action tentpoles and franchise sequels. Varun's fee alone is rumoured at ₹30 crore — more than half the production budget — making the economics precarious from the start.

Mrunal Thakur, who plays Baani, reportedly earned ₹5 crore. Pooja Hegde, fresh off a supporting role in Suriya's Retro earlier this year, took home an estimated ₹4 crore. The supporting cast — Mouni Roy (₹1.5 crore), Chunky Panday (₹90 lakh), Jimmy Shergill, Maniesh Paul, Rakesh Bedi, and Ali Asgar — suggests the makers are stacking the ensemble for maximum comic density.

The film is produced by Ramesh Taurani's Tips Films and Maximilian Films, and marks the fourth Varun-David collaboration after Main Tera Hero (2014), Judwaa 2 (2017), and Coolie No. 1 (2020). Of these, only Judwaa 2 was an unqualified commercial hit.

## Entering a Crowded Week

The timing is deliberate and dangerous. Hai Jawani lands one day after Ram Charan's Telugu sports drama Peddi (June 4), which has already crossed $733K in US premiere advance bookings. It also shares the June 5 slot with Bobby Deol's Anurag Kashyap-directed Bandar and the Hollywood imports He-Man and Scary Movie.

KVN Productions, the producers behind Yash's Toxic (which has been rescheduled multiple times), reportedly coordinated with Taurani to ensure both teams were aware of the scheduling proximity. Distributor Anil Thadani facilitated the conversation — a rare example of box-office diplomacy in an industry that usually prefers ambush marketing.

## The Diaspora Question

For NRI audiences, Hai Jawani represents a specific kind of comfort viewing — the sort of film that plays at house parties in Edison and gets quoted at Diwali gatherings in Hounslow. David Dhawan's comedies, at their best, are not cinema to be analysed. They're cinema to be survived, ideally while your uncle explains the joke to someone who already got it.

Whether that formula still works in 2026 — when the same NRI audience has access to every streaming platform and increasingly sophisticated South Indian blockbusters — is the ₹55 crore question. Varun has struggled commercially in recent years. His last full release, Sunny Sanskari Ki Tulsi Kumari, underperformed. His Thamma cameo reprising the Bhediya character was well-received, but a cameo doesn't carry a box-office.

The trailer, released at a Mumbai event, leans hard into the David Dhawan playbook: slapstick, double entendres, Varun mugging for the camera, and enough supporting actors to populate a small wedding. For those who grew up on Biwi No. 1 and Haseena Maan Jaayegi, the DNA is instantly recognisable.

For everyone else, the question is simpler: has Bollywood's most prolific comedy director still got it?

June 5 will answer.

*Sources: Sacnilk, ZoomTV Entertainment, Filmfare, MovieTalkies*"""

    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img,
        "image_attribution": "Wikimedia Commons" if img and ("wikimedia" in (img or "").lower() or "wikipedia" in (img or "").lower()) else "The Videshi",
        "sources": json.dumps(["Sacnilk", "ZoomTV Entertainment", "Filmfare", "MovieTalkies"])
    }


# ──────────────────────────────────────────────
# ARTICLE 3: Cocktail 2 — Shahid Kapoor Returns
# ──────────────────────────────────────────────

def article_cocktail_2():
    print("\n=== Article 3: Cocktail 2 ===")
    slug = "cocktail-2-shahid-kapoor-kriti-sanon-rashmika-mandanna-homi-adajania-june-19-nri-20260601"

    img = fetch_wikipedia_person_image("Shahid Kapoor")
    if not img or not validate_image(img):
        img = fetch_pexels_image("cocktail party Bollywood film")
        if not validate_image(img):
            img = None

    headline = "Cocktail 2 Rewrites the Cast, Keeps the Formula. Shahid Kapoor, Kriti Sanon, and Rashmika Mandanna Take Over on June 19."
    subheadline = "Homi Adajania returns to the franchise that turned Deepika Padukone into a star — fourteen years later, with an entirely new trio."

    body = """The original Cocktail, released in 2012, was supposed to be a frothy triangle about two women and a man in London. What it actually became was a Deepika Padukone showcase — her portrayal of the free-spirited Veronica was so magnetic that it reoriented her entire career trajectory and left co-stars Saif Ali Khan and Diana Penty playing support in their own film.

Fourteen years later, Cocktail 2 arrives on June 19 with director Homi Adajania back at the helm but an entirely new cast. Shahid Kapoor takes the lead, flanked by Kriti Sanon and Rashmika Mandanna. The replacement of every original cast member is both an acknowledgement of what made the first film work and a gamble that the Cocktail brand is bigger than any single actor.

## What We Know

Plot details remain thin — the makers have positioned this as a film about "love, friendship, and heartbreak with an upbeat soundtrack," which is marketing-speak for "we're not telling you anything yet." What is known is that the film was shot across multiple international locations and is being positioned as a summer tentpole for the June 19 release window.

Shahid Kapoor has been on an interesting trajectory. After the massive commercial failure of Jersey (the Hindi remake) and a relatively quiet period, he pivoted to streaming with Bloody Daddy and Farzi, both of which found substantial audiences on Prime Video. A return to the theatrical space with a big-budget rom-drama signals confidence — or necessity, depending on whom you ask.

Kriti Sanon, meanwhile, has quietly assembled one of the most consistent filmographies of her generation. Her work in Mimi, Adipurush (despite its controversies), and the action-comedy Crew demonstrated a range that few of her contemporaries can match. In Cocktail 2, she's expected to play the more grounded of the two female leads.

Rashmika Mandanna, who has spent the past three years becoming a pan-India phenomenon — from Pushpa to Animal to a growing presence in Bollywood — brings a Southern fan base that the franchise didn't previously have. Her casting is strategic: it positions Cocktail 2 as a pan-India play rather than a North Indian multiplex film.

## The Diaspora Connection

The original Cocktail was set in London, making it one of the few Bollywood films that directly depicted the NRI social milieu — the house parties, the casual mixing of cultures, the specific loneliness of being Indian abroad while trying not to be. It resonated particularly with British Indians and became a staple of diaspora movie nights.

Whether Cocktail 2 will attempt a similar NRI setting is unclear, but the franchise carries goodwill in overseas markets. The UK, US, and Canadian diaspora — audiences who turned the original into a sleeper hit internationally — will likely give this one its opening weekend regardless of reviews.

## June's Stacked Calendar

Cocktail 2 releases into a June calendar that is already straining under weight. By June 19, audiences will have had Peddi (June 4), Bandar (June 5), Hai Jawani Toh Ishq Hona Hai (June 5), Governor (June 12), and potentially Yash's delayed Toxic — all competing for multiplex screens and viewer attention.

The advantage for Cocktail 2 is positioning. It occupies a different genre space than the action dramas and political thrillers around it. For audiences looking for something lighter — a Friday evening watch rather than a Saturday morning spectacle — it might be the natural choice. The franchise name helps. In an era when Bollywood sequels are the closest thing the industry has to guaranteed IP, Cocktail carries enough cultural memory to get people through the door.

Getting them to stay is Homi Adajania's problem. He's done it before.

*Sources: Filmfare, Daily Jagran, ZoomTV Entertainment, Sacnilk*"""

    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img,
        "image_attribution": "Wikimedia Commons" if img and ("wikimedia" in (img or "").lower() or "wikipedia" in (img or "").lower()) else "The Videshi",
        "sources": json.dumps(["Filmfare", "Daily Jagran", "ZoomTV Entertainment", "Sacnilk"])
    }


# ── Main ──
if __name__ == "__main__":
    print(f"Entertainment writer starting at {datetime.now(timezone.utc).isoformat()}")
    print(f"Supabase URL: {SUPABASE_URL[:30]}..." if SUPABASE_URL else "⚠ No SUPABASE_URL")

    articles = [
        article_naga_chaitanya(),
        article_hai_jawani(),
        article_cocktail_2(),
    ]

    success = 0
    for art in articles:
        aid = insert_article(art)
        if aid:
            success += 1
        time.sleep(1)

    print(f"\n{'='*50}")
    print(f"Done: {success}/{len(articles)} articles published")
