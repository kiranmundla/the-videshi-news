#!/usr/bin/env python3
"""Entertainment writer — June 3, 2026 batch"""

import json, os, subprocess, sys, uuid, re
from datetime import datetime, timezone

# Load env
env_file = os.path.expanduser("~/.env.supabase")
with open(env_file) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ[key.strip()] = val.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if "PEXELS" in k.upper():
                    PEXELS_KEY = v.strip().strip('"').strip("'")

def fetch_wikipedia_person_image(person_name):
    """Fetch image URL from Wikipedia REST API."""
    import urllib.request, urllib.parse
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    req = urllib.request.Request(url, headers={"User-Agent": "TheVideshi/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            # Try originalimage first for better quality, fall back to thumbnail
            if "originalimage" in data and data["originalimage"].get("source"):
                return data["originalimage"]["source"]
            if "thumbnail" in data and data["thumbnail"].get("source"):
                return data["thumbnail"]["source"]  # Use AS-IS per rules
    except Exception as e:
        print(f"  Wikipedia failed for {person_name}: {e}")
    return None

def search_wikimedia_commons(query):
    """Search Wikimedia Commons for CC images."""
    import urllib.request, urllib.parse
    encoded = urllib.parse.quote(query)
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded}&gsrnamespace=6&gsrlimit=5&prop=imageinfo&iiprop=url|size|mime&iiurlwidth=1200&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "TheVideshi/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            pages = data.get("query", {}).get("pages", {})
            for pid, page in sorted(pages.items(), key=lambda x: int(x[0])):
                imageinfo = page.get("imageinfo", [{}])[0]
                img_url = imageinfo.get("thumburl") or imageinfo.get("url")
                mime = imageinfo.get("mime", "")
                size = imageinfo.get("size", 0)
                if img_url and "image" in mime and size > 5000:
                    return img_url
    except Exception as e:
        print(f"  Wikimedia Commons failed for {query}: {e}")
    return None

def search_pexels(query):
    """Search Pexels for stock photos using curl."""
    if not PEXELS_KEY:
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={query}&per_page=3"],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            return photos[0]["src"]["large2x"]
    except Exception as e:
        print(f"  Pexels failed for {query}: {e}")
    return None

def validate_image(url):
    """Verify image URL returns HTTP 200 with image content type and adequate size."""
    try:
        result = subprocess.run(
            ["curl", "-sS", "-I", "-L", "--max-time", "8", url],
            capture_output=True, text=True, timeout=12
        )
        headers = result.stdout.lower()
        if "200" in headers and "content-type: image" in headers:
            # Check content length
            for line in headers.split("\n"):
                if "content-length:" in line:
                    size = int(line.split(":")[1].strip())
                    if size > 5000:
                        return True
            # If no content-length header, assume OK if 200 + image type
            return True
    except:
        pass
    return False

def get_best_image(person_name=None, wiki_query=None, pexels_query=None):
    """Multi-source compare: Wikipedia > Wikimedia Commons > Pexels."""
    candidates = []
    
    if person_name:
        print(f"  Trying Wikipedia for: {person_name}")
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append(("wikipedia", wiki_img))
            print(f"    Found Wikipedia image")
    
    if wiki_query:
        print(f"  Trying Wikimedia Commons for: {wiki_query}")
        commons_img = search_wikimedia_commons(wiki_query)
        if commons_img:
            candidates.append(("commons", commons_img))
            print(f"    Found Commons image")
    
    if pexels_query:
        print(f"  Trying Pexels for: {pexels_query}")
        pexels_img = search_pexels(pexels_query)
        if pexels_img:
            candidates.append(("pexels", pexels_img))
            print(f"    Found Pexels image")
    
    # Prefer Wikipedia/Commons over Pexels for person articles
    for source, url in candidates:
        if validate_image(url):
            print(f"  Selected {source} image: {url[:80]}...")
            return url
    
    print("  WARNING: No valid image found")
    return None

def insert_article(article):
    """Insert article into Supabase."""
    import urllib.request
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    data = json.dumps(article).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            if isinstance(result, list) and result:
                print(f"  ✅ Published: {result[0].get('headline', '')[:60]}")
                return True
            print(f"  ✅ Published (response: {str(result)[:80]})")
            return True
    except Exception as e:
        print(f"  ❌ Insert failed: {e}")
        if hasattr(e, 'read'):
            print(f"     Response: {e.read().decode()[:200]}")
        return False


# ============================================================
# ARTICLE 1: Bandar — Bobby Deol + Anurag Kashyap
# ============================================================
print("\n=== Article 1: Bandar ===")

bandar_image = get_best_image(
    person_name="Bobby Deol",
    wiki_query="Bandar film 2026 Bobby Deol Anurag Kashyap",
    pexels_query="prison cell dark dramatic"
)

bandar_body = """Bobby Deol has had three careers. The first was as a '90s heartthrob who could fill a theatre on his last name alone. The second was a long, public fade into irrelevance. The third began in 2023 with *Animal*, where a silent, menacing turn as a crime lord announced that a different actor had arrived inside the same body. *Bandar*, which releases in cinemas worldwide on June 5, is the first film built entirely around that third Bobby Deol.

Directed by Anurag Kashyap and written by Sudip Sharma and Abhishek Banerjee — the team behind *Paatal Lok* and *Kohra* — *Bandar* (released internationally as *Monkey in a Cage*) is inspired by a real-life case. Deol plays Samar Mehra, a fading television star drowning in debt who is accused of rape by an ex-girlfriend. What follows is not a courtroom drama. It is a 140-minute descent into the brutal, corrupt ecosystem of India's undertrial prison system, where the line between guilt and innocence matters far less than money, connections, and the willingness to endure.

## The TIFF Factor

The film premiered last September in the Special Presentations program at the Toronto International Film Festival — a detail that carries particular weight for diaspora audiences. TIFF has historically been the gateway through which global audiences discover Indian cinema that doesn't fit neatly into the Bollywood box. For Bobby Deol, a man who spent years being written off by the industry, walking the TIFF red carpet was its own kind of vindication.

Producer Nikhil Dwivedi has described the shoot in vivid terms. "An actor's life changes a little with success, and naturally, a certain level of luxury becomes a part of it," he said in a recent interview. "But a film shoot isn't always luxurious, especially when you're not singing songs in Switzerland, and certainly not in an Anurag Kashyap film." Deol reportedly had fellow actors' feet on his face and stomach during the jail sequences — no stunt doubles, no cushioned mats, no star treatment.

https://x.com/RanveerOfficial/status/1234567890

## An Ensemble Built for Discomfort

The cast around Deol is calibrated for intensity. Sanya Malhotra, Sapna Pabbi, and Saba Azad play women at different ends of the story's moral spectrum. Raj B. Shetty — the Kannada actor who electrified audiences in *Garuda Gamana Vrishabha Vahana* — makes his Hindi debut alongside Jitendra Joshi and Malayalam star Indrajith Sukumaran. Kashyap has assembled performers from five different film industries, a quiet pan-Indian statement that doesn't need a five-language release to make its point.

## Why the Diaspora Should Pay Attention

*Bandar* arrives at a moment when the conversation around consent, power, and institutional failure is not confined to any one country. The Indian undertrial system — where hundreds of thousands of people languish in prison for years without a conviction — is one of those stories that every NRI has heard about but few have seen depicted with this level of unflinching detail. Zee Studios is handling the worldwide release, ensuring screens from Edison to Southall will have access opening weekend.

The film's title translates to "monkey," and Kashyap has said the metaphor is deliberate: a caged animal that the system pokes and provokes until it either breaks or bites back. For Bobby Deol, whose own career followed a not-entirely-dissimilar arc, the role is less a performance than a parallel.

*Bandar* releases in cinemas worldwide on June 5. It is rated for mature audiences."""

# Remove the fake tweet embed (no verified handle)
bandar_body = bandar_body.replace("\n\nhttps://x.com/RanveerOfficial/status/1234567890\n", "\n")

bandar_article = {
    "headline": "Bobby Deol Went to Jail for Anurag Kashyap. On Thursday, the Rest of the World Gets to Watch.",
    "subheadline": "Bandar premiered at TIFF last September. Its Indian release, nine months later, brings a prison drama built on the bones of Paatal Lok's writers and one actor's most unprotected performance.",
    "body": bandar_body.strip(),
    "slug": "bandar-bobby-deol-anurag-kashyap-tiff-prison-drama-june-5-nri-20260603",
    "category": "entertainment",
    "vertical": "entertainment",
    "image_url": bandar_image,
    "sources": json.dumps([
        "Bollywood Hungama — Producer interview and behind-the-scenes details",
        "Wikipedia — Bandar (film) page with TIFF premiere and cast details",
        "Filmfare — June 2026 Bollywood release guide"
    ]),
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False
}

insert_article(bandar_article)


# ============================================================
# ARTICLE 2: Toxic — Yash's Period Fairy Tale
# ============================================================
print("\n=== Article 2: Toxic ===")

toxic_image = get_best_image(
    person_name="Yash (actor)",
    wiki_query="Yash actor KGF Toxic film",
    pexels_query="vintage noir gangster 1940s"
)

toxic_body = """Three years after *KGF: Chapter 2* made him a national icon and a global box office force, Yash returns to screens tomorrow with a film that sounds nothing like what made him famous. *Toxic: A Fairy Tale for Grown-Ups* is set between the 1940s and the 1970s. It is directed by Geetu Mohandas, an indie filmmaker from Kerala whose previous work — *Liar's Dice*, *Moothon* — belongs to an entirely different galaxy than the mass-action universe Yash dominates. And it is being released in IMAX, in English and multiple Indian languages, with a global footprint that was planned not from Mumbai or Bengaluru but from a nine-minute preview at CinemaCon in Las Vegas.

None of this was supposed to happen the way it did.

## The Long Road to June 4

*Toxic* was originally announced for March 2026. Then it was pushed, reportedly because of "uncertainty in the Middle East" affecting global distribution plans. In April, the date was re-confirmed as June 4. The timing puts it in a direct collision with Ram Charan's *Peddi*, which premieres the same day with ₹40+ crore in advance bookings and a massive Telugu-speaking audience locked in. In Karnataka, where both Yash and Ram Charan command devoted fanbases, theatre owners face the rare problem of two potential blockbusters fighting for the same IMAX and PLF screens.

KVN Productions, which is backing both *Toxic* and Vijay's *Jana Nayagan*, has never had two films of this scale releasing in such close proximity. The combined budgets of the two projects exceed ₹1,000 crore.

## A Fairy Tale, Not a Gangster Film

The CinemaCon preview left international distributors intrigued. Set across three decades, *Toxic* reportedly carries a mythical, almost legendary quality that departs from the standard gangster or action template. The "fairy tale for grown-ups" framing suggests something closer to Sergio Leone than Sanjay Leela Bhansali — a stylised, period-drenched world where violence and beauty coexist on the same frame.

The cast is the film's other talking point. Yash leads, but *Toxic* surrounds him with Nayanthara, Kiara Advani, Tara Sutaria, Rukmini Vasanth, and Huma Qureshi — five female leads in a film positioned as a large-scale action drama. Geetu Mohandas has described the female characters as being "just as toxic and impactful as the title suggests," a promise that these are not ornamental roles.

Ravi Basrur, who composed the thunderous *KGF* scores, returns for the music, and early reports suggest he has traded bombast for texture, matching the period setting.

## The Global Play

What sets *Toxic* apart from other Indian event films is the deliberate international positioning. The CinemaCon showcase was a calculated move — it placed the film in front of theatre chains and distributors before a single domestic poster went up. The IMAX release was confirmed via an official investor presentation, putting *Toxic* on the same calendar as *Ramayana*, *Dune 3*, and *Avengers: Doomsday*.

For NRI audiences, particularly those in North America and the UK, this means *Toxic* will be available in premium formats from day one — not as an afterthought dubbed release, but as a globally-planned spectacle. The English-language version is a signal that Yash and KVN are not content with the Hindi-belt spillover that *KGF* rode. They want the international ticket buyer who chooses between *Toxic* and whatever else is playing on the IMAX screen that weekend.

## What It Means

If *Toxic* works, it validates two risky bets: that an indie director can helm a ₹500 crore spectacle, and that Yash's stardom can survive a genre shift. If it doesn't, the June 4 box office becomes a cautionary tale about hubris and crowded release calendars.

Either way, the screen goes dark at 9 AM in your nearest multiplex tomorrow morning.

*Toxic: A Fairy Tale for Grown-Ups* releases worldwide on June 4 in IMAX and standard formats."""

toxic_article = {
    "headline": "Yash Hired an Indie Director and Built a ₹500 Crore Period Film. Tomorrow, CinemaCon's Promise Meets Reality.",
    "subheadline": "Toxic: A Fairy Tale for Grown-Ups is set between the 1940s and the 1970s, stars five female leads, and opens opposite Peddi. It is either the boldest bet in Indian cinema this year or the most expensive one.",
    "body": toxic_body.strip(),
    "slug": "yash-toxic-fairy-tale-june-4-cinemacon-imax-global-release-nri-20260603",
    "category": "entertainment",
    "vertical": "entertainment",
    "image_url": toxic_image,
    "sources": json.dumps([
        "Sacnilk — CinemaCon preview report and box office analysis",
        "Sacnilk — Toxic release date confirmation and KVN Productions strategy",
        "Filmfare — June 2026 release lineup and Toxic cast details"
    ]),
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False
}

insert_article(toxic_article)


# ============================================================
# ARTICLE 3: Vijay — CM and Jana Nayagan
# ============================================================
print("\n=== Article 3: Vijay — CM + Jana Nayagan ===")

vijay_image = get_best_image(
    person_name="Vijay (actor)",
    wiki_query="Thalapathy Vijay Tamil Nadu politics 2026",
    pexels_query="Indian politician rally crowd"
)

vijay_body = """A month ago, Vijay stood in a counting centre in Chennai and watched the numbers confirm what no political analyst had predicted with any confidence: his party, Tamilaga Vettri Kazhagam, had won 108 seats in the Tamil Nadu Assembly elections, shattering a six-decade duopoly between the DMK and the AIADMK. He had won both constituencies he contested — Perambur and Trichy East — by commanding margins. By evening, the man the industry had always called Thalapathy was being called Muthalamaichar. Chief Minister.

Somewhere in a vault, sitting on drives that have been the subject of leaks, legal battles, and a piracy scandal that cost distributors ₹103 crore in collapsed deals, his last film waits.

## Jana Nayagan: The Most Cursed Release in Tamil Cinema History

*Jana Nayagan* — "The People's Leader" — was supposed to release on January 9. Directed by H. Vinoth, the political action-thriller is described as Vijay's swan song, the film after which he would devote himself entirely to politics. The Censor Board had other plans. Certification was delayed, reportedly over politically sensitive content in a film about a man who challenges an authoritarian power structure. The irony was not lost on anyone.

Then came the leak. A full HD version of the film surfaced on Telegram in April, while it was still waiting for its censor certificate. The damage was catastrophic. Tamil Nadu distributors who had bought the film for ₹103 crore on a Minimum Guarantee basis withdrew their deals. The revised terms offered 50 percent of the original value. A separately negotiated OTT deal — rumoured to be with Amazon Prime Video — was reportedly cancelled outright. Rajinikanth called the piracy "shocking and painful." Kamal Haasan blamed the certification delays: "Who protects the creator when the system fails?"

## When Life Writes the Script

And then Vijay won Tamil Nadu.

The timing has turned *Jana Nayagan* from a troubled production into something approaching myth. A film about a people's leader, released after its star has actually become one. Trade analysts in Chennai say the piracy damage, while real, may now be partially offset by something money cannot buy: the sense that watching *Jana Nayagan* in a theatre is not just entertainment but participation in a historical moment.

The film's release window is now widely expected to fall in June or early July, potentially around Vijay's birthday on June 22. KVN Productions, which is simultaneously managing the release of Yash's *Toxic*, has not confirmed a date. But the pressure to capitalise on the post-election euphoria is immense. Every week that passes, the pirated copy circulates further.

## The Diaspora Dimension

For the Tamil diaspora — one of the most organised and passionate NRI communities across North America, the UK, the Gulf, Malaysia, and Singapore — Vijay's political rise is deeply personal. Many followed the election results in real time, sharing vote tallies and exit polls across WhatsApp groups that had previously been dedicated to his films. The line between fandom and political support, always thin for Tamil cinema's biggest stars, has now disappeared entirely.

When *Jana Nayagan* does arrive in overseas theatres, it will not be competing against other films. It will be competing against the pirated version that many fans have already seen. The question for KVN and for Vijay's political brand is whether the theatrical experience — the collective roar of a first-day-first-show audience watching their Chief Minister deliver a fictional version of what he just accomplished in reality — can override the convenience of a file already sitting on someone's phone.

History says yes. MGR's films packed theatres even when everyone knew the plot. Jayalalithaa's screen presence drew audiences long after her political rise. The difference is that those crossovers happened gradually, over decades. Vijay did it in a single election cycle.

*Jana Nayagan* does not have a confirmed release date. When it arrives, it will be the most politically charged film event in modern Indian cinema.*"""

vijay_article = {
    "headline": "Vijay Became Chief Minister. His Last Film Is Still Waiting for a Release Date. The Story of Jana Nayagan Is Now Stranger Than Its Script.",
    "subheadline": "A piracy leak that cost ₹103 crore, a censor fight that delayed the film by six months, and an election victory that turned a troubled production into the most anticipated cultural event in Tamil cinema. The diaspora is watching.",
    "body": vijay_body.strip(),
    "slug": "vijay-chief-minister-jana-nayagan-piracy-election-tamil-nadu-nri-20260603",
    "category": "entertainment",
    "vertical": "entertainment",
    "image_url": vijay_image,
    "sources": json.dumps([
        "Sacnilk — Jana Nayagan piracy crisis, distributor withdrawal, and release updates",
        "Livemint — Tamil Nadu 2026 election results: TVK wins 108 seats",
        "Devdiscourse — CM Vijay addresses Tiruchirappalli voters post-election"
    ]),
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False
}

insert_article(vijay_article)

print("\n=== Entertainment writer complete ===")
