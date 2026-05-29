#!/usr/bin/env python3
"""Entertainment writer — 2026-05-29 evening batch (3 articles)"""

import json, os, re, time, subprocess, urllib.parse, uuid
from datetime import datetime, timezone

# --- Supabase config (load from .env file) ---
def load_env(path):
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env("~/.env.supabase")
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

PEXELS_API_KEY = None
try:
    with open(os.path.expanduser("~/.env.pexels")) as f:
        for line in f:
            if "PEXELS_API_KEY" in line:
                PEXELS_API_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
except Exception:
    pass

import requests

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
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:100]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels as fallback. Returns URL or None."""
    if not PEXELS_API_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_API_KEY}",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate image URL returns 200 with image content-type and >5KB."""
    if not url:
        return False
    # Block banned sources
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat=", "ccb="]
    for b in banned:
        if b in url:
            print(f"  ✗ Banned source detected: {b}")
            return False
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {ct}, {cl} bytes")
            return True
        # Some servers don't return Content-Length on HEAD, try GET
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: {len(chunk)}+ bytes")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def publish_article(article):
    """Insert article into Supabase."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=headers,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        title = article["headline"][:60]
        print(f"  ✓ Published: {title}...")
        return True
    else:
        print(f"  ✗ Publish failed ({r.status_code}): {r.text[:200]}")
        return False

# ==========================================
# ARTICLES
# ==========================================

articles = []

# --- ARTICLE 1: Peddi (Ram Charan) ---
print("\n=== Article 1: Peddi ===")

# Image sourcing: Ram Charan from Wikipedia
img1 = fetch_wikipedia_person_image("Ram Charan")
if not validate_image(img1):
    img1 = fetch_wikipedia_person_image("Ram Charan (actor)")
    if not validate_image(img1):
        img1 = fetch_pexels_image("Indian cricket wrestling sport rural", "Indian village sports")
        if not validate_image(img1):
            img1 = None

articles.append({
    "headline": "Ram Charan's ₹350 Crore Telugu Epic Peddi Opens June 4. It Has A.R. Rahman, a 189-Minute Runtime, and the Widest Indian Release of the Year.",
    "subheadline": "Set in 1980s Andhra Pradesh, the sports action drama reunites the RRR star with A.R. Rahman and releases across IMAX, Dolby, 4DX, and 3D formats in 50+ countries — making it the most anticipated Indian theatrical event of early summer.",
    "slug": "ram-charan-peddi-350-crore-ar-rahman-june-4-release-imax-telugu-nri-20260529",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img1,
    "sources": json.dumps([
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Peddi"},
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com/news/features/ram-charan-opens-up-about-getting-into-the-skin-of-peddi/"},
        {"name": "Sacnilk", "url": "https://sacnilk.com/movies/Peddi"}
    ]),
    "body": """Ram Charan has not had a solo theatrical release since RRR turned him into a global name in 2022. That four-year wait ends on June 4, when Peddi — a Telugu-language sports action drama budgeted at ₹350 crore — arrives in cinemas worldwide.

## The Biggest Indian Release Window of Early Summer

Peddi will open across IMAX, Dolby Cinema, 4DX, ScreenX, D-Box, MX4D, and standard 3D and 2D formats. That premium-format footprint is wider than any Indian film has managed in 2026 so far. The Hindi-dubbed version will run simultaneously, targeting the north Indian market that embraced Ram Charan after RRR's crossover success.

The film's theatrical rollout covers over 50 countries, with significant advance booking activity already visible in the United States, United Kingdom, Australia, Canada, and the Gulf states — the core NRI markets.

## A Story Rooted in Rural Andhra Pradesh

Directed by Buchi Babu Sana, Peddi is set in 1980s rural Andhra Pradesh. Ram Charan plays the titular character — a spirited villager who rallies his community through sport to stand up against a powerful local rival. The film blends cricket, wrestling, and village politics into an action drama that the director has described as deeply personal.

The supporting cast is stacked. Kannada superstar Shiva Rajkumar plays a key role, making this a cross-industry event. Janhvi Kapoor stars opposite Ram Charan. Jagapathi Babu, Divyenndu (of Mirzapur fame), and Boman Irani round out the ensemble. Shruti Haasan appears in a special song sequence.

## A.R. Rahman Returns to the Big Screen

The original score and soundtrack are composed by A.R. Rahman — his first major Telugu film collaboration in years. The music has already made an impact: the first single, Chikiri Chikiri, has crossed 200 million views across platforms, while the second track, Rai Rai Raa Raa, has surpassed 47 million views on YouTube. A promotional musical event held on May 23 in Bhopal, attended by the full cast and Rahman himself, drew massive crowds.

The Budapest Scoring Orchestra recorded the film's orchestral arrangements — the kind of international production scale that was once reserved for Bollywood's biggest tentpoles.

## What NRIs Should Know

At 189 minutes, Peddi is a full-scale theatrical experience. For the diaspora, the film carries extra weight: Ram Charan is one of the few Indian actors with genuine global recognition after RRR's Oscar-adjacent success, and this is his first chance to prove that audience wasn't a one-time phenomenon.

Advance ticket sales in the US are already running ahead of projections. The June 4 date puts Peddi in a relatively clear window, arriving a week before the Jailer 2 and Bharat Bhhagya Viddhaata releases crowd the market on June 12.

## The Telangana Theater Deal

In a separate development that affects the film's domestic economics, a new agreement between producers and exhibitors in Telangana has cleared the way for Peddi's release under the existing rental model. Starting July 3, Telangana will shift permanently to a percentage-sharing system for all films. Peddi will be among the last major releases under the old structure — a detail that matters for its box office tracking.

The production is backed by Mythri Movie Makers and Sukumar Writings, two of the most powerful production houses in Telugu cinema. Vriddhi Cinemas and IVY Entertainment co-produce."""
})

# --- ARTICLE 2: Shakti Shalini Wrap ---
print("\n=== Article 2: Shakti Shalini ===")

# Image sourcing: Aneet Padda from Wikipedia
img2 = fetch_wikipedia_person_image("Aneet Padda")
if not validate_image(img2):
    img2 = fetch_pexels_image("Indian temple ancient mystical", "Rajasthan village celebration")
    if not validate_image(img2):
        img2 = None

articles.append({
    "headline": "Maddock's Shakti Shalini Has Wrapped Filming. Aneet Padda Plays Both the Goddess and the Ghost.",
    "subheadline": "The sixth entry in India's most profitable horror-comedy franchise finished shooting across Madhya Pradesh, Rajasthan, and Mumbai — with Nana Patekar and Seema Biswas joining for the climax. Christmas 2026 release confirmed.",
    "slug": "shakti-shalini-wrapped-aneet-padda-double-role-maddock-horror-universe-christmas-2026-nri-20260529",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img2,
    "sources": json.dumps([
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com/news/bollywood/aneet-padda-starrer-shakti-shalini-wrapped-up-in-mumbai-report/"},
        {"name": "Filmfare", "url": "https://www.filmfare.com/news/bollywood/report-aneet-padda-to-play-double-role-in-shakti-shalini"},
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Aneet_Padda"}
    ]),
    "body": """The Maddock Horror Comedy Universe — the franchise that turned Stree, Bhediya, and Munjya into some of Bollywood's most reliable box office properties — has quietly wrapped production on its sixth installment.

## Shakti Shalini: From March to May

Shakti Shalini finished filming on May 27 at Chitrath Studio in Powai, Mumbai, according to a report by Mid-Day. The shoot began in March 2026 and spanned locations across Madhya Pradesh (Chambal, Datia, Antri, Panihar, Gwalior, Morena), Rajasthan (Dholpur, Barkhandi), and Mumbai.

The production's final stretch involved elaborate sets depicting a Rajasthani village and house interiors, built for a large-scale climax sequence. A source close to the production described the sequence as showing "village people, especially women, celebrating the defeat of evil."

## The Double Role That Could Define the Film

Aneet Padda, who broke out with the 2025 blockbuster Saiyaara (₹5.79 billion worldwide), plays both lead roles. Director Aditya Sarpotdar has crafted two opposing characters for her: Shakti, the divine protector inspired by Goddess Kali, and Shalini, a vengeful female ghost who punishes men after being betrayed and killed.

The narrative is rooted in Bengali folklore and mythology. The story revolves around the eternal battle between these two forces — good and evil occupying the same screen, played by the same actor. It is an ambitious structural gamble for a franchise that has typically relied on ensemble comedy with horror elements.

Padda was confirmed as the lead through a post-credit reveal in Thamma (Diwali 2025), where her character was introduced as "the creator, the destroyer, and the mother of all." She replaced Kiara Advani, who was initially attached to the project.

## A Heavyweight Supporting Cast

The film has quietly assembled a cast that goes beyond the franchise's usual formula. Viineet Kumar Singh — who earned acclaim in Chhaava alongside Vicky Kaushal — plays the main antagonist. Vishal Jethwa takes a lead role. And in a significant addition, veteran actors Nana Patekar and Seema Biswas joined the unit in May for the climax portions.

Nana Patekar's involvement, in particular, signals that the film may have dramatic ambitions beyond the horror-comedy template. Patekar has not appeared in a major franchise film in years.

## Where Shakti Shalini Sits in the Universe

The Maddock Horror Comedy Universe launched with Stree (2018) and has since expanded through Bhediya (2022), Munjya (2024), Stree 2 (2024 — the highest-grossing Bollywood film ever), and Thamma (2025). The franchise has collectively grossed well over ₹2,000 crore.

Shakti Shalini is the sixth film. Three more are confirmed in the pipeline: Chamunda, Bhediya 2, and eventually Stree 3 in 2027. The saga is planned to culminate in 2028 with Maha Munjya, Pehla Mahayudh, and Doosara Mahayudh — a multi-film crossover event that Maddock has been seeding since Munjya.

## The Diaspora Calendar

Shakti Shalini is locked for December 24, 2026 — a Christmas release that will compete for the holiday audience. For NRI moviegoers, the date matters: it falls right before the year-end break, when Indian theatrical releases in the US, UK, and Canada historically perform well.

Director Aditya Sarpotdar, who previously helmed Munjya and Thamma, has now directed three films in this universe. With production wrapped and seven months until release, the post-production runway is unusually generous for a Bollywood film — a sign that the VFX-heavy double-role work will get the time it needs."""
})

# --- ARTICLE 3: Salman Khan Mediates Don 3 ---
print("\n=== Article 3: Don 3 Salman Mediation ===")

# Image sourcing: Salman Khan from Wikipedia
img3 = fetch_wikipedia_person_image("Salman Khan")
if not validate_image(img3):
    img3 = fetch_wikipedia_person_image("Salman Khan (actor)")
    if not validate_image(img3):
        img3 = fetch_pexels_image("Bollywood film production set", "Indian movie industry")
        if not validate_image(img3):
            img3 = None

articles.append({
    "headline": "Salman Khan Called Both Ranveer Singh and Farhan Akhtar. He Wants the Don 3 War Settled Without Lawyers.",
    "subheadline": "With FWICE's non-cooperation directive still active and ₹45 crore in claimed losses, Salman has stepped in as an unofficial mediator — urging both sides to think as one industry and resolve the dispute privately.",
    "slug": "salman-khan-mediates-don-3-ranveer-singh-farhan-akhtar-fwice-ban-peace-nri-20260529",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img3,
    "sources": json.dumps([
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com/news/bollywood/scoop-salman-khan-turns-cupid-ranveer-singh-farhan-akhtar-don-3-war/"},
        {"name": "Filmfare", "url": "https://www.filmfare.com/news/bollywood/salman-khan-intervenes-in-don-3-fallout"},
        {"name": "Mint", "url": "https://www.livemint.com/entertainment/bollywood/salman-khan-steps-up-to-mediate-between-ranveer-singh-and-farhan-akhtar"}
    ]),
    "body": """The Don 3 dispute between Ranveer Singh and Farhan Akhtar has consumed Bollywood's attention for two weeks. Now Salman Khan has inserted himself into the middle of it — not with a public statement, but with private phone calls to both parties.

## What Salman Actually Said

According to Bollywood Hungama, Salman reached out to both Ranveer and Farhan separately. The message to each was the same: resolve this without hurting each other's careers, without involving film bodies, and without lawyers.

A source told the publication: "Salman Khan is fond of Ranveer Singh, and is equally fond of the Akhtars too. He picked up the call on both the stakeholders, and has asked them to resolve their issues without hurting the future of their respective projects. He explained to Farhan about creative differences being a common thing in the industry for decades, and he also had a long chat with Ranveer, understanding his stance."

The source added that Salman explicitly told both parties to "think as one industry" — and suggested they work together on a different project once the tensions cool down. Notably, Salman asked to be kept out of the formal mediation process himself. He does not want to be a third-party arbitrator. He wants them to talk directly.

## The Dispute: A Quick Recap

The conflict started when Ranveer Singh exited Don 3 — reportedly just three weeks before shooting was scheduled to begin. The reasons, according to multiple reports, were creative differences: Ranveer wanted a darker, more violent version of the Don character with stronger language, while Farhan preferred to stay closer to his original vision for the franchise.

There were also reports that Ranveer was frustrated by repeated production delays and the absence of a locked final script.

Farhan and his production partner Ritesh Sidhwani (Excel Entertainment) claimed ₹45 crore in pre-production losses and took the complaint to the Indian Film & Television Director's Association, which referred it to FWICE.

On May 25, FWICE issued a non-cooperation directive against Ranveer — essentially an industry-wide recommendation that producers and filmmakers refuse to work with the actor. The federation said Ranveer had ignored multiple invitations to present his version of events.

## Why This Matters Beyond Gossip

The Don 3 situation is not just celebrity drama. It has surfaced a real structural tension in the Indian film industry: what happens when a top-tier actor exits a major production at the last minute, and what enforcement mechanisms actually exist?

FWICE's non-cooperation directive is technically a recommendation, not a binding legal order. Its real power is reputational. For Ranveer — fresh off the historic success of Dhurandhar (₹1,800 crore worldwide) — the timing is especially awkward. He is currently the industry's biggest commercial draw, and any prolonged dispute could disrupt his ability to capitalize on that momentum.

Salman's intervention is significant precisely because of who he is in the industry's informal hierarchy. He has long played the role of peacemaker in Bollywood disputes, and both Ranveer and Farhan are said to have taken his words seriously.

## What Happens Next

Reports suggest both parties are now open to an amicable resolution. Ranveer's team released a statement saying the actor "believes that professional discussions and personal equations are best handled with dignity, maturity and mutual respect" — careful language that stops short of an apology but signals willingness to de-escalate.

Meanwhile, AI-generated photos of a supposed "airport meeting" between Ranveer and Farhan went viral, but were quickly debunked. No in-person meeting has taken place yet.

For the diaspora audience watching this unfold, the practical question is whether Don 3 will ever get made — and if so, with whom. The franchise, which began with Shah Rukh Khan in 2006, has been through multiple iterations. Whether Ranveer returns to the role or Farhan recasts entirely may depend on what happens in the next few weeks.

## The Bigger Picture

Salman Khan pushing Ranveer to "start a new project to capitalize on Dhurandhar's success" is pragmatic advice. Dhurandhar 2 just crossed ₹1,000 crore net in Hindi alone — a number no Bollywood film had achieved before. The window to leverage that goodwill is finite.

The Don 3 dispute will eventually be resolved, one way or another. The more interesting question is whether Bollywood's informal mediation culture — where a phone call from Salman Khan carries more weight than a federation directive — is sustainable as the industry grows into a corporate, multi-billion-dollar business."""
})

# ==========================================
# PUBLISH ALL ARTICLES
# ==========================================
print("\n=== Publishing ===")
success = 0
for i, article in enumerate(articles):
    print(f"\nArticle {i+1}: {article['headline'][:60]}...")
    if article.get("image_url"):
        print(f"  Image: {article['image_url'][:80]}...")
    else:
        print("  ⚠ No image — publishing without image")
    
    if publish_article(article):
        success += 1
    time.sleep(1)

print(f"\n=== Done: {success}/{len(articles)} articles published ===")
