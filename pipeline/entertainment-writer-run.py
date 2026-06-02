#!/usr/bin/env python3
"""Entertainment writer for The Videshi — June 2, 2026 run.

Publishes 3 articles:
1. Delhi HC protects Varun Dhawan's personality rights against AI deepfakes
2. IMAX returns to Hyderabad after a decade with AMB Cinemas
3. Bobby Deol's personal redemption story — Aap Ki Adalat interview
"""

import json, os, sys, uuid, re, time
import requests, urllib.parse
from datetime import datetime, timezone

# --- ENV ---
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# --- HELPERS ---

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
    """Fetch an image from Pexels using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Check that image URL returns a valid image > 5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD, try GET
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error for {url[:60]}: {e}")
    return False


def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30,
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data["id"]
        print(f"  ✓ Inserted article: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# === ARTICLE 1: Delhi HC protects Varun Dhawan's personality rights ===

def write_article_1():
    print("\n--- Article 1: Delhi HC / Varun Dhawan personality rights ---")
    
    img_url = fetch_wikipedia_person_image("Varun Dhawan")
    if not img_url or not validate_image(img_url):
        img_url = fetch_pexels_image("Indian court law gavel", "Delhi High Court")
    
    body = """The Delhi High Court has granted interim protection to actor Varun Dhawan against the unauthorized commercial exploitation of his personality rights — a ruling that arrives at a moment when AI-generated deepfakes and face-morphing tools have made digital identity theft trivially easy, and not just in India.

## What the Court Ordered

Justice Jyoti Singh, hearing a suit filed by Dhawan, passed an ex parte ad interim injunction on May 29, restraining multiple websites, social media accounts, e-commerce platforms, and online intermediaries from using the actor's name, image, voice, likeness, or any other identifiable element of his persona without explicit authorization.

The restraint specifically covers technologies including artificial intelligence, generative AI, machine learning, deepfakes, AI chatbots, and face-morphing tools. The Court directed Google, Meta Platforms, and X Corporation to provide Basic Subscriber Information of infringing users. All three intermediaries must take down newly reported content within 36 hours.

"Plaintiff is entitled to protection against dissemination of pornographic content as well as AI-generated images portraying him in an inappropriate scenario," Justice Singh observed. "Such distasteful content is harming and damaging the reputation of the Plaintiff and may mislead the public into believing what is depicted may be true."

## What Triggered the Suit

Dhawan's legal team, led by Senior Advocate Sandeep Sethi, flagged three categories of abuse: online e-commerce sellers misusing his personality traits to sell unauthorized merchandise, booking agencies falsely claiming to arrange his appearances at events, and — most disturbingly — the circulation of AI-generated pornographic deepfakes showing the actor in fabricated intimate scenarios with female co-stars.

The Court noted that Dhawan has secured trademark registrations over his name and signature, and that these attributes are exclusively associated with him.

## Why This Matters for the Diaspora

For NRIs who navigate multiple digital ecosystems across countries, this ruling has implications that reach far beyond Bollywood gossip. AI deepfake tools are now accessible to anyone with a laptop. The technology that can fabricate a convincing video of Varun Dhawan can do the same to any public figure, any professional, any person.

India's courts have been building a body of personality rights jurisprudence in recent years. Naga Chaitanya obtained a similar order from the Delhi High Court in May after AI-manipulated content linked him to allegations involving his former wife Samantha Ruth Prabhu. Anil Kapoor secured a landmark personality rights order in 2023.

What makes the Dhawan order notable is its explicit scope over AI, generative AI, machine learning, deepfakes, and chatbots — a comprehensive list that acknowledges the full toolkit now available to bad actors. The 36-hour takedown mandate for intermediaries sets a practical enforcement timeline.

## The Bigger Picture

For Indian professionals abroad, the case raises a question that extends beyond celebrity culture: what legal protections exist when someone creates a deepfake of you? In the United States, deepfake laws remain a patchwork of state-level legislation. The EU's AI Act introduces some provisions, but enforcement mechanisms are still evolving. India's approach through personality rights jurisprudence, while not legislated in a single statute, is producing court orders with teeth.

The film industry, predictably, has its own concerns. With AI tools capable of generating convincing actor likenesses, the commercial model of star power — the thing that drives casting decisions, brand endorsements, and box office numbers — faces an existential question. If anyone can put Varun Dhawan's face on any body in any scenario, what exactly is his image worth?

For now, the Delhi High Court has drawn a line. The next hearing will determine whether the interim protection becomes permanent. The deepfake industry is unlikely to notice."""

    article = {
        "headline": "Delhi High Court Draws a Line on AI Deepfakes. Varun Dhawan's Personality Rights Order Covers Everything from Chatbots to Face-Morphing.",
        "subheadline": "Justice Jyoti Singh's ruling mandates a 36-hour takedown window for AI-generated content — and names every tool in the deepfake arsenal.",
        "body": body.strip(),
        "slug": "delhi-hc-varun-dhawan-personality-rights-ai-deepfakes-order-nri-20260602",
        "category": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            "https://barandbench.com/news/delhi-high-court-protects-personality-rights-varun-dhawan-ai-deepfakes",
            "https://latestly.com/agency-news/india-news-delhi-hc-restrains-ai-deepfakes-unauthorised-merchandise-and-online-exploitation-of-varun-dhawans-personality-rights-6895017.html",
            "https://devdiscourse.com/article/headlines/3300981-delhi-hc-grants-varun-dhawan-protection-against-unauthorized-use-of-persona"
        ]),
        "image_url": img_url,
        "image_attribution": "Wikimedia Commons" if img_url and ("wikipedia" in img_url or "wikimedia" in img_url) else "The Videshi",
        "vertical": "entertainment",
        "is_editorial": False,
    }
    
    art_id = insert_article(article)
    return art_id


# === ARTICLE 2: IMAX Returns to Hyderabad ===

def write_article_2():
    print("\n--- Article 2: IMAX returns to Hyderabad ---")
    
    # Try Mahesh Babu (AMB Cinemas partner)
    img_url = fetch_wikipedia_person_image("Mahesh Babu")
    if img_url and not validate_image(img_url):
        print(f"  ⚠ Wikipedia image failed validation, trying Pexels")
        img_url = None
    if not img_url:
        img_url = fetch_pexels_image("IMAX cinema theater", "movie theater screen")
        if img_url and not validate_image(img_url):
            img_url = None
    
    body = """Hyderabad is getting IMAX back. After a decade-long absence that left the home of Tollywood without a single premium large-format screen, IMAX Corporation and Asian Cinemas have announced a partnership for three new IMAX with Laser locations through the AMB Cinemas brand. The first screen opens before the end of 2026.

## The Deal

Two of the three new locations will be in Hyderabad. The first, at AMB Classic, is targeted for a late-2026 opening. The remaining two locations are planned for 2028. All three will feature IMAX with Laser technology — the company's top-tier projection and sound system.

AMB Cinemas is Asian Cinemas' flagship "superplex" brand, launched in partnership with Telugu superstar Mahesh Babu. The brand has built a reputation for premium movie-going in the Telugu market.

"Hyderabad's appetite and love for cinema is unparalleled, and bringing back the prestigious IMAX format to Hyderabad is a matter of great honour and pride for AMB Cinemas," said Managing Directors Sunil Narang and Bharat Narang.

IMAX CEO Rich Gelfond called India's cinema culture "vibrant" and noted that 2025 was IMAX's best year ever at the Indian box office, powered by both Hollywood and Indian films.

## Why It Took a Decade

The last IMAX screen in Hyderabad was at Prasads, one of India's first IMAX theaters. It closed around 2015, leaving a city that produces some of the world's most visually ambitious cinema without the screen format designed to show it.

The irony was not lost on the industry. S.S. Rajamouli, whose RRR and Baahubali: The Conclusion rank among the highest-grossing Indian films ever shown in IMAX, publicly expressed frustration that Hyderabad — the production hub behind these spectacles — lacked an IMAX theater.

During the recent launch event for his upcoming film Varanasi, starring Mahesh Babu, Rajamouli had openly called for an IMAX screen in the city. The timing of this announcement, just ahead of Varanasi's release, is hard to read as coincidental.

## What This Means for Telugu Cinema's Global Ambitions

Telugu cinema has undergone a tectonic shift in the past five years. Films like RRR, Pushpa, KGF, and Kalki 2898 AD have redefined what Indian cinema can achieve at the global box office. The domestic market now regularly produces films that gross ₹500+ crore worldwide.

For NRIs who grew up watching Telugu films in modest single-screen theaters, the IMAX announcement carries symbolic weight. The Telugu film industry is no longer a regional curiosity — it is the factory floor for India's biggest cinematic spectacles. An IMAX partnership validates that status within the exhibition infrastructure.

Several upcoming projects stand to benefit immediately. Ram Charan's Peddi releases on June 4 in IMAX across available markets. Rajamouli's Varanasi, reportedly mounted on a massive scale, was conceived for IMAX-scale viewing. Projects like Raaka and the rumored God of War adaptation from Indian filmmakers would also find a natural home on these screens.

## The Business Logic

IMAX has been aggressively expanding in India. The company now operates over 50 screens across the country, with Delhi, Mumbai, Bengaluru, and Chennai among the major markets. Hyderabad's absence was a conspicuous gap.

The Telugu-speaking diaspora is one of the most active movie-going communities in North America, the UK, and the Gulf. NRI audiences in these markets already watch Telugu films in IMAX — Peddi's advance booking in the US has crossed $700K. The domestic market lagging behind its overseas audience in screen technology was an anomaly that this deal corrects.

For Asian Cinemas, the partnership strengthens AMB's positioning as a premium brand. For IMAX, it secures a foothold in a market that produces the kind of films their technology was built to show.

The first screen opens by December 2026. Hyderabad has waited long enough."""

    article = {
        "headline": "IMAX Returns to Hyderabad After a Decade. Tollywood's Biggest Filmmakers Finally Get the Screen They Deserve.",
        "subheadline": "Three new IMAX with Laser locations through AMB Cinemas — the first opens by December 2026, just in time for Rajamouli's Varanasi.",
        "body": body.strip(),
        "slug": "imax-hyderabad-amb-cinemas-rajamouli-telugu-cinema-decade-nri-20260602",
        "category": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            "https://www.businesswire.com/news/home/20260601463827/en/Asian-Cinemas-and-IMAX-Launch-Partnership-With-Three-New-IMAX-With-Laser-Locations-In-India",
            "https://www.bollywoodhungama.com/news/bollywood/imax-returns-to-hyderabad-after-a-decade-with-three-new-amb-cinemas-locations/",
            "https://www.gulte.com/news/finally-its-official-imax-returns-to-hyderabad/396862"
        ]),
        "image_url": img_url,
        "image_attribution": "Wikimedia Commons" if img_url and ("wikipedia" in img_url or "wikimedia" in img_url) else "The Videshi",
        "vertical": "entertainment",
        "is_editorial": False,
    }
    
    art_id = insert_article(article)
    return art_id


# === ARTICLE 3: Bobby Deol's Redemption Story ===

def write_article_3():
    print("\n--- Article 3: Bobby Deol's personal redemption ---")
    
    img_url = fetch_wikipedia_person_image("Bobby Deol")
    if img_url and not validate_image(img_url):
        print(f"  ⚠ Wikipedia image failed validation, trying Pexels")
        img_url = None
    if not img_url:
        img_url = fetch_pexels_image("Bollywood actor portrait", "Indian cinema actor")
        if img_url and not validate_image(img_url):
            img_url = None
    
    body = """Bobby Deol sat across from Rajat Sharma on Aap Ki Adalat and said the thing that most Bollywood actors spend entire careers avoiding. He said he gave up.

"When you hit rock bottom, self-pity takes over," Deol told Sharma in the interview that has since been clipped, shared, and discussed across every Indian social media platform. "You feel the world has ended for you. Nobody likes you anymore. And you get into addictions — to sedate yourself."

## The Drinking, the Silence, the Disappearance

The facts of Bobby Deol's career hiatus are well-documented but rarely articulated by the man himself. After a string of box office failures in the 2000s and early 2010s, work dried up. The son of Dharmendra and younger brother of Sunny Deol — a man who had debuted to a blockbuster opening with Barsaat in 1995 — found himself at home while the industry moved on.

He started drinking. His father, Dharmendra, had a well-known relationship with alcohol, and Bobby found himself following the same path. "My father always liked to drink, and I just got addicted to it," he said. "The thing about alcohol is that first you drink it, and then it drinks you."

What happened next is the part that has struck a nerve.

## "She Is My Spine"

Bobby's wife Tanya Deol started working. She ran the household finances. She managed the family. She did not leave.

"Usne ghar sambhala, kharch woh karti thi," Bobby said, switching between Hindi and English with the ease of a man who has rehearsed this truth in his head many times. "She works. She never made me feel that way. She always told me — why do you think about yourself like this?"

The turning point came from their children. "It was when my children started asking why I was always sitting at home and their mother would go to the office that something snapped within me," Bobby said. "I decided to work on myself."

He addressed the persistent rumor that Tanya had left him during his lowest period. "It's amusing to hear such claims. Women possess incredible strength, and my wife never abandoned me. She did threaten to leave if I didn't quit drinking, but she stood by me."

## The Comeback That Became a Meme, Then Became Real

Bobby Deol's career resurrection is one of the stranger second-act stories in Hindi cinema. A supporting role in Salman Khan's Race 3 (2018) broke the drought. Then came Aashram on MX Player, where he played a morally bankrupt godman with unsettling conviction. Class of 83 followed.

But it was Animal (2023) that turned Bobby Deol into an internet phenomenon. His near-silent performance as the antagonist Abrar — cold, measured, terrifying — spawned the "Lord Bobby" meme. For a man who had spent years as a punchline in Bollywood joke threads, the transformation was jarring.

Now comes Bandar, directed by Anurag Kashyap, releasing on June 5. Bobby plays a fading television star falsely accused of rape — a role that requires him to channel vulnerability, desperation, and rage. The film premiered at TIFF to strong notices. The cast includes Sanya Malhotra, Raj B Shetty, and Saba Azad.

## Why This Resonates with the Diaspora

Bobby Deol's story is not really about Bollywood. It is about the specific shame that Indian families know intimately: the man who is supposed to provide, sitting at home while his wife works. The children who notice. The relatives who talk. The silence that fills a house when purpose disappears.

For NRI families who have watched their own members struggle with career setbacks, addiction, or the suffocating weight of expectations in a new country, Bobby's candor on national television is disarming. He did not blame the industry, his genes, or his circumstances. He credited his wife. He credited his children's innocent question.

"Change only happens when it comes from within you," he said. And then he went quiet for a moment, which is the most Bobby Deol thing in the world — letting the silence say what words cannot.

Bandar releases in theaters on June 5. This time, the audience is not laughing at him. They are watching."""

    article = {
        "headline": "Bobby Deol Told Rajat Sharma He Gave Up on Himself. Then He Explained Who Pulled Him Back.",
        "subheadline": "The Aap Ki Adalat interview ahead of Bandar's release is the most candid Bobby Deol has ever been about addiction, disappearance, and the wife who stayed.",
        "body": body.strip(),
        "slug": "bobby-deol-aap-ki-adalat-addiction-tanya-comeback-bandar-nri-20260602",
        "category": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            "https://www.newsdive.net/bobby-deol-sons-alcohol-struggle-wife-handling-everything/",
            "https://www.saartaj.com/bobby-deol-opens-up-on-alcohol-addiction-wife-tanya-deol/",
            "https://inshorts.com/en/news/kids-asked-why-i-was-at-home-while-mother-worked-bobby-on-alcohol-addiction"
        ]),
        "image_url": img_url,
        "image_attribution": "Wikimedia Commons" if img_url and ("wikipedia" in img_url or "wikimedia" in img_url) else "The Videshi",
        "vertical": "entertainment",
        "is_editorial": False,
    }
    
    art_id = insert_article(article)
    return art_id


# === MAIN ===
if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi — Entertainment Writer Run")
    print(f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    results = []
    
    art1 = write_article_1()
    results.append(("Varun Dhawan AI deepfakes", art1))
    
    art2 = write_article_2()
    results.append(("IMAX Hyderabad", art2))
    
    art3 = write_article_3()
    results.append(("Bobby Deol redemption", art3))
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    for name, art_id in results:
        status = f"✓ {art_id}" if art_id else "✗ FAILED"
        print(f"  {name}: {status}")
    
    failures = sum(1 for _, a in results if not a)
    print(f"\nPublished: {len(results) - failures}/{len(results)}")
    if failures:
        sys.exit(1)
    print("Done.")
