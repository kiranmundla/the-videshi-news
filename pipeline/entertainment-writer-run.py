#!/usr/bin/env python3
"""Entertainment writer for The Videshi — batch run."""

import json, os, re, sys, uuid, datetime, requests, urllib.parse, time

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

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
    """Fetch a relevant image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5',
                 '-H', f'Authorization: {PEXELS_KEY}'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate image URL returns 200 with image content type and >5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Some servers don't support HEAD, try GET with range
        if r.status_code != 200:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            ct2 = r2.headers.get('Content-Type', '')
            if r2.status_code == 200 and 'image' in ct2:
                chunk = r2.raw.read(6000)
                if len(chunk) > 5000:
                    return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def publish_article(article):
    """Publish article to Supabase."""
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')
    payload = {
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': article['slug'],
        'category': 'entertainment',
        'vertical': 'entertainment',
        'status': 'published',
        'published_at': now,
        'sources': json.dumps(article['sources']),
        'image_url': article.get('image_url', ''),
    }
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=15
    )
    if r.status_code in (200, 201):
        print(f"  ✓ Published: {article['headline'][:60]}...")
        return True
    else:
        print(f"  ✗ Failed ({r.status_code}): {r.text[:200]}")
        return False


# ============================================================
# ARTICLES
# ============================================================

articles = []

# --- ARTICLE 1: Vicky Kaushal & Katrina Kaif introduce baby Vihaan ---
print("\n📰 Article 1: Vicky-Katrina introduce baby Vihaan")
img1 = fetch_wikipedia_person_image("Vicky Kaushal")
if not img1 or not validate_image(img1):
    img1 = fetch_wikipedia_person_image("Katrina Kaif")
if not img1 or not validate_image(img1):
    img1 = fetch_pexels_image("Mumbai airport celebrities")

articles.append({
    'headline': "Vicky Kaushal and Katrina Kaif Introduced Baby Vihaan to Paparazzi at Mumbai Airport. No Photos Were Allowed.",
    'subheadline': "The couple let photographers meet their seven-month-old son in person but drew a firm line on cameras — a boundary more Bollywood parents are now choosing to set.",
    'slug': 'vicky-kaushal-katrina-kaif-baby-vihaan-airport-no-photos-privacy-nri-20260530',
    'sources': [
        {"name": "Bombay Times", "url": "https://bombaytimes.com"},
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
        {"name": "Radio City India", "url": "https://radiocity.in"}
    ],
    'image_url': img1 or '',
    'body': """Bollywood's most private power couple just set a new template for celebrity parenthood in India.

Vicky Kaushal and Katrina Kaif were spotted at Mumbai International Airport earlier this week, boarding a flight out of the city with their infant son, Vihaan Kaushal. What made the outing unusual wasn't the sighting itself — it was what happened next. The couple walked up to the press pool stationed at the airport and introduced seven-month-old Vihaan to the photographers in person. Then they asked them not to take a single photograph.

## A Boundary Set With Grace

According to photojournalists present at the airport, Katrina stepped forward carrying Vihaan in her arms and politely but firmly requested that no pictures or videos be captured. "Katrina was with Vicky, but she asked not to be photographed with the baby and introduced the baby to the paparazzi," one photographer confirmed to media outlets. Vicky posed solo for a few frames, then the couple spent several minutes in conversation with the press pool before heading to their gate.

The interaction earned praise across social media for its unusual blend of warmth and firmness. Rather than dodging cameras or covering the child's face — the usual celebrity playbook — Vicky and Katrina chose to acknowledge the photographers' professional presence while drawing an explicit line around their son's image rights.

## The Name That Connects Two Worlds

Vihaan Kaushal was born in November 2025, though the couple waited until January 7 to publicly reveal his name. The name carries a quiet significance: Vihaan was the character name Vicky Kaushal played in *Uri: The Surgical Strike*, the 2019 blockbuster that cemented his status as a leading man in Hindi cinema. The film grossed over ₹340 crore worldwide and turned "How's the Josh?" into a national catchphrase.

Katrina, who was last seen in Sriram Raghavan's *Merry Christmas* alongside Vijay Sethupathi, has been largely away from the spotlight since becoming a mother. Vicky, meanwhile, delivered one of India's highest-grossing films of 2025 with *Chhaava*, his historical drama about Chhatrapati Sambhaji Maharaj.

## A Growing Trend Among Bollywood Parents

The Kaushal approach mirrors a broader shift in how Indian celebrities are managing their children's exposure to media. Virat Kohli and Anushka Sharma have been similarly protective of daughter Vamika and son Akaay, requesting that media outlets not publish their children's photos. Priyanka Chopra and Nick Jonas have shared only selective, carefully controlled images of daughter Malti Marie. Alia Bhatt and Ranbir Kapoor have taken a similar stance with daughter Raha, though they eventually shared her face publicly on their own terms.

For diaspora audiences watching from overseas, the conversation resonates differently. Many NRI parents navigate similar boundaries around their children's digital footprint — deciding what to post, what to share, and how much of their kids' lives belongs on the internet. The difference is scale: when your airport outing involves a hundred camera lenses, the stakes of those decisions are exponentially higher.

## What It Signals

The airport introduction was ultimately a brief moment — a few minutes of conversation, a request, and a departure gate. But it communicated something larger about how Bollywood's newest generation of parents is redefining the rules of engagement with India's aggressive paparazzi culture.

Vicky and Katrina didn't hide. They didn't run. They didn't issue a statement through a publicist. They showed up, said hello, set a boundary, and left. In an industry where baby reveals are often elaborately staged social media events timed for maximum engagement, the simplicity of the gesture was its own kind of statement.

Vihaan Kaushal's face remains unphotographed. His name is public. His parents are famous. And for now, that's all the world gets to know."""
})


# --- ARTICLE 2: Governor — Manoj Bajpayee's 1991 Economic Crisis Film ---
print("\n📰 Article 2: Governor trailer — Manoj Bajpayee")
img2 = fetch_wikipedia_person_image("Manoj Bajpayee")
if not img2 or not validate_image(img2):
    img2 = fetch_pexels_image("Reserve Bank India building", "Indian economy gold")

articles.append({
    'headline': "Manoj Bajpayee Is Playing the RBI Governor Who Secretly Airlifted 60 Tonnes of Gold to Save India From Bankruptcy. The Film Opens June 12.",
    'subheadline': "Governor revisits the terrifying summer of 1991, when India had two weeks of foreign exchange left and pawned its gold reserves to avoid sovereign default. Every NRI who lived through it remembers.",
    'slug': 'governor-manoj-bajpayee-1991-economic-crisis-rbi-gold-airlift-june-12-nri-20260530',
    'sources': [
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
        {"name": "Bollywood Life", "url": "https://bollywoodlife.com"},
        {"name": "YouTube (Official Trailer)", "url": "https://youtube.com"}
    ],
    'image_url': img2 or '',
    'body': """There is a chapter in India's modern history that every Indian who was alive in 1991 remembers with a visceral clarity — the summer the country nearly went bankrupt. Now Manoj Bajpayee is bringing that chapter to the big screen.

*Governor*, directed by Chinmay Mandlekar and produced by Vipul Amrutlal Shah, tells the story of the RBI Governor who orchestrated the secret airlift of 60 tonnes of India's gold reserves to the Bank of England and the Union Bank of Switzerland as collateral for emergency loans. The film opens in Indian cinemas on June 12, 2026.

## The Real Crisis Behind the Film

In the summer of 1991, India's foreign exchange reserves had plummeted to under $1 billion — barely enough to cover two weeks of imports. The Gulf War had sent oil prices soaring. Remittances from Indian workers in the Middle East had dried up. The country was days away from defaulting on its international obligations.

What happened next was one of the most dramatic financial operations in post-independence Indian history. Under the supervision of RBI Governor S. Venkitaramanan, India secretly pledged 46.91 tonnes of gold to the Bank of England, physically airlifting the bullion out of the country in a covert operation. A separate tranche of 20 tonnes was pledged to the Union Bank of Switzerland. The gold-backed loans bought India the breathing room it needed to avoid a sovereign default and eventually paved the way for the economic liberalisation of 1991 under Finance Minister Manmohan Singh.

## Bajpayee's Most Consequential Role

At the trailer launch, Manoj Bajpayee spoke about how long the project had been in development. "4.5 years back, Vipul got in touch with me for this film," he said. "I found the first drafts so exciting and kept talking after that." The trailer shows Bajpayee in a restrained, pressure-cooker performance — a bureaucrat carrying the weight of a nation's survival on his shoulders, with a single line that lands like a punch: "If I fail… India fails."

The film also stars Adah Sharma as a journalist and features music by Amit Trivedi with lyrics by the legendary Javed Akhtar. The direction is handled by Chinmay Mandlekar, the Marathi filmmaker best known for *Dharmaveer* and its sequel, who is making his Hindi directorial debut with *Governor*.

## Why This Story Matters to the Diaspora

For the Indian diaspora — particularly those who emigrated during the 1980s and 1990s — the 1991 crisis is not abstract history. It was the moment that reshaped the India they had left behind. The liberalisation that followed the crisis opened India's economy to the world, creating the IT boom, the outsourcing revolution, and the infrastructure expansion that transformed the country.

Many first-generation NRIs remember the crisis in deeply personal terms: the panic over family finances back home, the uncertainty about whether India could sustain itself, and the eventual relief when the liberalisation reforms began to take hold. For their children — the second generation who grew up hearing about "the India that was" — the story is foundational to understanding why their parents left and why the India of today looks nothing like the India of 1990.

*Governor* is not an action film or a political thriller in the conventional Bollywood sense. It's a story about a bureaucrat with a briefcase making decisions in conference rooms that determined whether 850 million people would wake up to a functioning economy or a collapsed one. That's a different kind of tension — quieter, more cerebral, and for the right audience, far more gripping than any car chase.

## The June 12 Battlefield

*Governor* faces serious competition on its release date. June 12 also sees the release of Kangana Ranaut's *Bharat Bhhagya Viddhaata*, a 26/11 Mumbai attacks film, and Rajinikanth's *Jailer 2*. When asked about the crowded release window, producer Vipul Shah joked at the trailer launch, "Main boxing gloves pehen ke baitha hoon!" (I'm sitting here with boxing gloves on.)

The competition is fierce, but Bajpayee has a track record of finding audiences for intelligent, story-driven cinema. *Governor* may not need a ₹200 crore opening weekend to succeed — it needs the right audience to find it. And for millions of Indians at home and abroad who lived through 1991, the right audience already knows this story by heart."""
})


# --- ARTICLE 3: Dhurandhar Production Designer POSH Verdict ---
print("\n📰 Article 3: Dhurandhar POSH verdict")
img3 = fetch_pexels_image("Bollywood film production set", "Indian film set crew")

articles.append({
    'headline': "Dhurandhar's Production Designer Was Found Guilty of Sexual Harassment by the Film's Own POSH Committee. His Credit Has Been Removed.",
    'subheadline': "A six-month internal investigation by B62 Studios concluded Saini S Johray was guilty on two counts — sexual molestation and tampering of evidence. His name no longer appears on the franchise.",
    'slug': 'dhurandhar-posh-committee-saini-johray-guilty-sexual-harassment-credit-removed-nri-20260530',
    'sources': [
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
        {"name": "Mid-Day (via Zoom TV)", "url": "https://zoomtventertainment.com"},
        {"name": "The Times of Bengal", "url": "https://thetimesofbengal.com"}
    ],
    'image_url': img3 or '',
    'body': """The production designer of *Dhurandhar* — the Ranveer Singh-led two-part blockbuster that has grossed over ₹1,850 crore worldwide — has been found guilty of sexual harassment by the film's own internal committee.

Saini S Johray, who designed the visual world of both *Dhurandhar* and its sequel *Dhurandhar: The Revenge*, was the subject of a six-month investigation by B62 Studios' Prevention of Sexual Harassment (POSH) Committee. According to a report first published by Mid-Day, the committee found Johray guilty on two separate counts: sexual molestation and tampering of evidence.

## How It Unfolded

The complaint was filed with B62 Studios — the production house founded by filmmaker Aditya Dhar and producer Lokesh Dhar — in October 2025. The studio activated its POSH Committee immediately. "The POSH committee did a thorough investigation, given the sensitivity of the matter and the production house's no-tolerance policy towards harassment," a source told Mid-Day.

The investigation ran for approximately six months, concluding around March-April 2026. "He was found guilty on two counts — sexual molestation and tampering of evidence. The committee communicated the findings to the complainant," the source added.

Separately, an FIR was registered against Johray at Chandigarh's Sector-17 police station on April 20, 2026. According to India Today, the complainant — a woman from New Delhi — alleged that Johray summoned her to a room at the Taj Hotel in Chandigarh, where she claimed he sexually harassed her, physically assaulted her, and wrongfully confined her. The complainant also alleged that an intoxicating substance had been mixed into her drink.

## The Credit Erasure

The most visible consequence of the POSH findings has been the removal of Johray's name from the *Dhurandhar* franchise. While his credit appeared in the original OTT version of *Dhurandhar* that released on January 30, 2026, it was reportedly scrubbed from the "Raw and Undekha" extended version that debuted on May 22. His name is also absent from *Dhurandhar: The Revenge*'s IMDb page, though it remains unclear whether he was credited in its theatrical release.

The decision to remove a crew member's credit is rare in Indian cinema and signals a meaningful shift in how production houses are responding to harassment findings. Historically, Indian film industry responses to such allegations have been inconsistent at best — public statements of concern followed by quiet reinstatement once the news cycle moves on.

## The Broader Pattern

The Johray case has emerged alongside another crediting controversy in Bollywood. YRF cinematographer Pratik Shah, who faced accusations from filmmaker Abhinav Singh of being "highly manipulative" and "emotionally abusive" toward women, was reportedly removed from the Sourav Ganguly biopic earlier this year. Several crew members on Shah's subsequent projects have reportedly raised concerns about his continued presence on sets.

These cases arrive years after the initial #MeToo wave hit Bollywood in 2018, when allegations against prominent figures like director Vikas Bahl, actor Alok Nath, and filmmaker Sajid Khan generated headlines but produced limited institutional change. What is different now is the mechanism: a formal POSH Committee investigation with documented findings, conducted by the production house itself, resulting in concrete professional consequences.

## What This Means for the Industry

For diaspora audiences who follow Bollywood from afar, the *Dhurandhar* POSH case offers a complicated picture. The franchise itself remains one of the most successful in Indian cinema history. Ranveer Singh's star turn is untouched by the controversy. But the visual world that audiences consumed — the sets, the production design, the physical environment of the film — was created by someone who has now been found guilty of workplace sexual harassment by his own employer.

B62 Studios' decision to investigate, find guilty, and remove credit sets a precedent. Whether other production houses follow that precedent when their own POSH findings are inconvenient will determine whether this moment represents genuine institutional change or another exception that proves the rule.

*Dhurandhar 2: The Revenge* arrives on JioHotstar on June 4 for Indian audiences. International viewers can find it on Netflix. Johray's name will not appear in the credits of either version."""
})


# --- ARTICLE 4: KD: The Devil hits ZEE5 ---
print("\n📰 Article 4: KD: The Devil OTT release")
img4 = fetch_wikipedia_person_image("Dhruva Sarja")
if not img4 or not validate_image(img4):
    img4 = fetch_wikipedia_person_image("Sanjay Dutt")
if not img4 or not validate_image(img4):
    img4 = fetch_pexels_image("Kannada cinema gangster", "Indian action movie")

articles.append({
    'headline': "Kannada Gangster Epic KD: The Devil Hits ZEE5 on June 5. It Has Sanjay Dutt, Shilpa Shetty, and a Sudeepa Cameo.",
    'subheadline': "The Dhruva Sarja-led action thriller flopped in theatres but arrives on streaming in five languages — just in time for a diaspora audience that might give it a second life.",
    'slug': 'kd-the-devil-zee5-june-5-ott-dhruva-sarja-sanjay-dutt-shilpa-shetty-nri-20260530',
    'sources': [
        {"name": "Pinkvilla", "url": "https://pinkvilla.com"},
        {"name": "Zoom TV Entertainment", "url": "https://zoomtventertainment.com"},
        {"name": "The Cinema Post", "url": "https://thecinemapost.com"}
    ],
    'image_url': img4 or '',
    'body': """*KD: The Devil* had everything a Kannada blockbuster is supposed to have — a massive star in Dhruva Sarja, a Bollywood crossover cast led by Sanjay Dutt and Shilpa Shetty, a cameo from Sudeepa, and a period gangster storyline dripping with style. What it didn't have was a box office audience willing to show up.

Now the film gets a second chance. ZEE5 has confirmed that *KD: The Devil* will begin streaming on June 5, 2026, available in Kannada, Tamil, Telugu, Malayalam, and Hindi. For a film that struggled to find its footing in single-screen theatres, the multi-language OTT premiere may reach the wider audience it was always designed for.

## A Film Built for Scale

Directed by Prem and produced by Venkat K. Narayana under the KVN Productions banner, *KD: The Devil* follows Kaalidasa — a carefree, uneducated young man whose blind admiration for a feared underworld don named Dhak Deva (Sanjay Dutt) pulls him into a dangerous web of betrayal, violence, and reckoning. When Kali discovers that the man he idolised has been destroying innocent lives, he transforms from a wide-eyed follower into an unlikely warrior.

The cast is stacked. Dhruva Sarja anchors the film as Kali. Sanjay Dutt plays the menacing Dhak Deva. Shilpa Shetty appears in a key role. V. Ravichandran and Ramesh Aravind add veteran gravitas. Reeshma Nanaiah plays Kali's love interest, Macchu Lakshmi. Nora Fatehi makes a special appearance, and Sudeepa delivers a cameo that the film's marketing leaned on heavily.

The technical team matches the ambition: William David handled cinematography, Arjun Janya composed the music (the soundtrack generated significant buzz before release), and Sanketh Achar edited the 141-minute film. Visual effects were managed by Phoenix Prem Studio.

## Why Theatres Didn't Work

Despite the star power and production scale, *KD: The Devil* received largely negative reviews during its theatrical run, which began on April 30. Critics pointed to pacing issues, an overstuffed narrative, and a disconnect between the film's sweeping visual ambitions and its storytelling execution. The box office numbers reflected the reception — disappointing against what was clearly a significant production budget.

The theatrical failure wasn't for lack of trying. The film had been in development for years, surviving multiple production delays before finally reaching screens. But in a year where Kannada cinema has produced genuine theatrical hits, *KD: The Devil* couldn't compete on word-of-mouth.

## June 5: A Crowded Streaming Day

The ZEE5 premiere lands on an unusually busy day in Indian OTT. The same platform is also releasing *Patriot* — the Mammootty-Mohanlal spy thriller that cost ₹140 crore and is available in five languages. Over on JioHotstar, *Dhurandhar 2: The Revenge* arrives for Indian audiences after its international Netflix debut.

For diaspora viewers juggling multiple streaming subscriptions, June 5 presents a genuine embarrassment of riches. *KD: The Devil*'s best chance may be its availability across five languages — a Tamil-speaking viewer in Toronto or a Telugu-speaking family in Dallas can access it without waiting for a dubbed release.

## The OTT Second Life

South Indian cinema has repeatedly proven that theatrical performance doesn't determine streaming success. Films that struggled in cinemas have found massive audiences on platforms, where the pressure of a ₹200 ticket and a three-hour time commitment is replaced by the low-friction convenience of a couch and a remote.

*KD: The Devil* has the ingredients for an OTT hit: a recognisable Bollywood cast that extends its reach beyond the Kannada market, a gangster genre that plays well on streaming, and a runtime that's manageable for home viewing. Whether the storytelling issues that sank its theatrical run will matter less on a small screen remains to be seen.

The devil, as they say, is in the details. And starting June 5, those details will be available to judge from home."""
})


# ============================================================
# PUBLISH
# ============================================================

print("\n" + "="*60)
print("Publishing articles...")
print("="*60)

success = 0
for i, article in enumerate(articles):
    print(f"\n[{i+1}/{len(articles)}] {article['headline'][:70]}...")
    if article.get('image_url') and not validate_image(article['image_url']):
        print(f"  ⚠ Image failed validation, clearing: {article['image_url'][:60]}")
        article['image_url'] = ''
    if publish_article(article):
        success += 1
    time.sleep(1)

print(f"\n{'='*60}")
print(f"Done. Published {success}/{len(articles)} articles.")
print(f"{'='*60}")
