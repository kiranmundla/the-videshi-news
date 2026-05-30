#!/usr/bin/env python3
"""Entertainment writer for The Videshi – 2026-05-30 batch"""

import os, json, requests, urllib.parse, uuid, time
from datetime import datetime, timezone

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                key, val = line.split('=', 1)
                val = val.strip().strip('"').strip("'")
                os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
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
    """Fetch image from Pexels API using curl (Python urllib gets 403)."""
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            cmd = [
                'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                photos = data.get('photos', [])
                if photos:
                    url = photos[0].get('src', {}).get('large2x') or photos[0].get('src', {}).get('large')
                    if url:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Validate that image URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get('Content-Type', '')
        content_length = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in content_type and content_length > 5000:
            return True
        # Some servers don't return Content-Length on HEAD
        if r.status_code == 200 and 'image' in content_type:
            return True
    except:
        pass
    return False

def publish_article(article):
    """Publish article to Supabase."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    payload = {
        'id': art_id,
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
        'image_attribution': article.get('image_attribution', ''),
    }

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=30
    )
    if r.status_code in (200, 201):
        print(f"  ✅ Published: {article['headline'][:60]}...")
        return art_id
    else:
        print(f"  ❌ Failed to publish: {r.status_code} {r.text[:200]}")
        return None


# ===================== ARTICLES =====================

articles = []

# --- ARTICLE 1: Karan Johar Instagram mass unfollow ---
print("\n📝 Article 1: Karan Johar Instagram unfollow...")
img1 = fetch_wikipedia_person_image("Karan Johar")
if not validate_image_url(img1):
    img1 = fetch_pexels_image("Instagram social media phone")
    
articles.append({
    'headline': "Karan Johar Unfollowed Shah Rukh Khan, Alia Bhatt, and Nearly Everyone on Instagram. Then He Told India to Calm Down.",
    'subheadline': "The filmmaker's mass unfollow triggered a national meltdown. His explanation was three sentences long.",
    'slug': 'karan-johar-unfollows-srk-alia-kareena-instagram-digital-detox-nri-20260530',
    'image_url': img1 or '',
    'image_attribution': 'Wikimedia Commons' if img1 and 'wikipedia' in str(img1).lower() or 'wikimedia' in str(img1).lower() else '',
    'sources': [
        {"name": "Filmfare", "url": "https://filmfare.com"},
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
        {"name": "Zoom TV", "url": "https://zoomtventertainment.com"}
    ],
    'body': """On Thursday night, eagle-eyed Instagram users noticed something strange on Karan Johar's profile. The filmmaker — who follows over 17 million people but more importantly, *is* followed by the entirety of Bollywood's inner circle — had quietly unfollowed nearly everyone.

Shah Rukh Khan: gone. Alia Bhatt: gone. Kareena Kapoor Khan, Varun Dhawan, Sidharth Malhotra, Manish Malhotra, Gauri Khan, Aryan Khan, Suhana Khan, Ananya Panday, Malaika Arora, Kartik Aaryan — all vanished from his following list. By Friday morning, Karan was following just 74 accounts out of a previous count that stretched well into the hundreds.

Naturally, India lost its mind.

## The Internet Wrote the Script Before Karan Could

Within hours, Reddit threads were dissecting screenshots. Twitter was awash with theories — professional fallouts, personal feuds, a secret rift with SRK stretching back decades. The fact that Priyanka Chopra Jonas remained on the list while virtually every other A-lister was removed only added fuel. Why *her*? What did she know? Was this a coded message?

Entertainment portals ran it as breaking news. Fan armies mobilized. "KARAN JOHAR UNFOLLOWS SRK" trended nationally.

## Three Sentences. That's All He Needed.

Karan, to his credit, moved fast. He posted an Instagram Story that read: "It's a DIGITAL DETOX!!!! Am unfollowing everyone to reduce my time and energy spent on the gram!!! This can't be national news for gods sake... please clickbait something else! This is irrelevant!"

A source close to the filmmaker confirmed to Filmfare that the mass unfollow was a social media strategy, not a personal statement. "It has nothing to do with any particular star, page, or person," the source said.

## The Man Who Made Instagram Into a Career Move

For a filmmaker who has turned social media into a second career — his *Koffee with Karan* franchise is essentially a curated Instagram feed brought to life — the move is both ironic and oddly fitting. Karan Johar has spent years cultivating the most visible social circle in Indian entertainment. His following list was practically a cast sheet for Dharma Productions.

But even by Bollywood standards, the idea that a man unfollowing accounts on Instagram could dominate a national news cycle for 12 hours says something about the parasocial relationship between India and its film industry. The "who follows whom" metric has become its own gossip column, and KJo's list was the most-read one in the business.

## Why This Matters to the Diaspora

For NRIs who grew up on *Kuch Kuch Hota Hai* and *Kabhi Khushi Kabhie Gham*, the KJo-SRK friendship is practically cultural infrastructure. The idea that it might be in trouble — even for a few hours — felt destabilizing in a way that says more about our emotional investment in Bollywood's inner circle than about any actual relationship dynamics.

Karan, meanwhile, is back to posting Stories. His latest film, *Chand Mera Dil*, is navigating a modest box office run. And Instagram's algorithm, one suspects, will not miss the 400-odd accounts he just shed.

The friendships, by all accounts, remain intact. The follow button, apparently, was the only casualty.

*Karan Johar recently became India's first filmmaker to attend the Met Gala, wearing a custom Manish Malhotra ensemble inspired by Raja Ravi Varma's paintings.*"""
})

# --- ARTICLE 2: Ishaan Khatter Biarritz Film Festival jury ---
print("\n📝 Article 2: Ishaan Khatter Biarritz jury...")
img2 = fetch_wikipedia_person_image("Ishaan Khatter")
if not validate_image_url(img2):
    img2 = fetch_wikipedia_person_image("Ishaan Khattar")
if not validate_image_url(img2):
    img2 = fetch_pexels_image("film festival red carpet")

articles.append({
    'headline': "Ishaan Khatter Is the Only Indian on a Film Festival Jury Led by Kristen Stewart. The Festival Is in France.",
    'subheadline': "The Biarritz Film Festival's jury panel places the Dhadak star alongside filmmakers from five countries. He also just made the Gold House 100 list.",
    'slug': 'ishaan-khatter-biarritz-film-festival-jury-kristen-stewart-france-nri-20260530',
    'image_url': img2 or '',
    'image_attribution': 'Wikimedia Commons' if img2 and ('wikipedia' in str(img2).lower() or 'wikimedia' in str(img2).lower()) else '',
    'sources': [
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
        {"name": "ANI", "url": "https://aninews.in"}
    ],
    'body': """Ishaan Khatter has been invited to serve on the jury of the Biarritz Film Festival — Nouvelles Vagues 2026, scheduled for June 23–28 in the French coastal city. He is the only Indian on the panel, which will be chaired by American actress and filmmaker Kristen Stewart.

The rest of the jury reads like a casting call for global independent cinema: Canadian actress Whitney Peak, French actor-director Raphaël Quenard, French filmmaker Nathan Ambrosioni, actress Suzy Bemba, Italian director Carolina Cavalli, and British actress Esmé Creed-Miles.

## A Festival Built for the Next Generation

The Biarritz Film Festival isn't Cannes. It doesn't have 70 years of old-guard tradition or red carpets that require three hours of fashion diplomacy. What it does have is a sharp editorial eye for cinema centered around younger generations and emerging voices — exactly the kind of platform that's starting to matter more than legacy festivals for artists building international careers in real time.

Now in its fourth edition, the festival has quietly become one of Europe's most closely watched incubators for contemporary storytelling. Having an Indian voice at the juror's table — particularly one who has straddled both Bollywood spectacle and international prestige — is a statement about where Indian cinema sits in the global conversation right now.

## Ishaan's International Trajectory

The invitation arrives during what is turning into a breakout international phase for Ishaan. His trajectory has been deliberate: *A Suitable Boy* for Mira Nair opened BBC doors; *The Royals* expanded his streaming footprint; and *Homebound* earned festival circuit appreciation. Each project has extended his visibility beyond the traditional Bollywood audience.

Earlier this year, Ishaan became the only Indian male actor featured on the Gold House Gold 100 list, an annual recognition of influential Asian and Pacific figures across industries. That kind of cross-industry visibility — where you're not just "Bollywood actor in an international project" but genuinely part of the global cultural conversation — is rare for Indian actors who didn't come through Hollywood first.

## What This Means for Indian Representation

For the diaspora, Ishaan's jury appointment signals something that goes beyond one actor's career milestone. Indian actors have historically appeared at international festivals as guests, presenters, or red-carpet ornaments. Being asked to judge — to have a say in which films win, which voices get elevated — is fundamentally different. It implies curatorial authority, not just star power.

The last few years have seen a slow but significant shift: Deepika Padukone at Cannes as a jury member, AR Rahman's continued global presence, and now Ishaan at Biarritz. The pattern suggests Indian talent is being integrated into the infrastructure of global cinema, not just invited to its parties.

## What's Next

On the work front, Ishaan will next be seen in *Jugaadu*, a comic caper that marks his first production venture. He shared the first look from the film on Instagram earlier this month.

The Biarritz Film Festival runs from June 23 to 28, bringing together filmmakers and emerging creative voices from across the world. Ishaan will be the one deciding which of them deserves the spotlight.

*Not bad for a kid from Mumbai who made his debut dancing on the streets in a Majid Majidi film.*"""
})

# --- ARTICLE 3: Anushka Sharma + One8 Yoga ---
print("\n📝 Article 3: Anushka Sharma + One8 Yoga...")
img3 = fetch_wikipedia_person_image("Anushka Sharma")
if not validate_image_url(img3):
    img3 = fetch_pexels_image("yoga activewear fashion")

articles.append({
    'headline': "Anushka Sharma Just Joined Virat Kohli's Sportswear Company. Together They're Launching a Yoga Line on International Yoga Day.",
    'subheadline': "The actor has acquired a minority stake in Agilitas Sports and will co-create the One8 Yoga activewear line. The June 21 launch targets a $22 billion market.",
    'slug': 'anushka-sharma-agilitas-sports-one8-yoga-virat-kohli-activewear-nri-20260530',
    'image_url': img3 or '',
    'image_attribution': 'Wikimedia Commons' if img3 and ('wikipedia' in str(img3).lower() or 'wikimedia' in str(img3).lower()) else '',
    'sources': [
        {"name": "Inc42", "url": "https://inc42.com"},
        {"name": "Economic Times", "url": "https://economictimes.indiatimes.com"},
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"}
    ],
    'body': """Anushka Sharma has acquired a minority stake in Agilitas Sports, the startup that owns Virat Kohli's One8 sportswear brand. As part of the deal, she will co-create One8 Yoga — a yoga-focused activewear line set to launch on June 21, International Day of Yoga.

The financial details of Sharma's investment remain undisclosed, but the strategic move is anything but quiet. It places cricket's most prominent power couple at the center of India's booming athleisure market, projected to reach $22.4 billion by 2034.

## The Agilitas Story

Agilitas Sports was founded in 2023 by former Puma India managing director Abhishek Ganguly, along with ex-Puma executives Atul Bajaj and Amit Prabhu. The company is vertically integrated — spanning product design, manufacturing, distribution, and retail — a rarity in India's sportswear landscape, where most brands rely on third-party sourcing.

Kohli joined Agilitas in 2025 after ending his eight-year, ₹110-crore partnership with Puma. He invested approximately ₹40 crore and brought the One8 brand into Agilitas's portfolio. Now, with Anushka on board, the company is expanding from performance sportswear into the wellness and lifestyle segment.

"By building the category thoughtfully from the ground up, the focus will remain on comfort, movement, functionality, and versatility, while ensuring the products seamlessly integrate into daily routines," Sharma said in a statement.

## Why Yoga Wear, and Why Now

India's relationship with yoga apparel is paradoxical. The country invented yoga but imports most of its premium yoga wear — Lululemon, Alo Yoga, Nike — from brands that learned about downward dog from a studio in Santa Monica. A homegrown line backed by two of India's most recognized global faces fills a gap that's been oddly overlooked.

For the Indian diaspora, this is particularly interesting. NRIs have been disproportionate consumers of Western athleisure brands, partly because quality Indian alternatives simply didn't exist in the premium segment. One8 Yoga could change that calculus, especially if it can nail the fit-and-fabric equation that Western brands have dominated.

The June 21 launch date is deliberately symbolic — International Yoga Day draws global attention to India's wellness heritage, and attaching a product launch to it signals that One8 Yoga is positioning itself as more than athleisure. It's a cultural statement.

## Anushka's Quiet Pivot

For those tracking Anushka Sharma's career, the Agilitas investment is the latest in a deliberate pivot away from acting and toward entrepreneurship. Her last theatrical release was *Zero* alongside Shah Rukh Khan. While fans have speculated endlessly about her return to the screen, Sharma has focused on her production company Clean Slate Filmz and, increasingly, business investments that align with the lifestyle she's been building publicly — wellness, fitness, mindful living.

The fact that she's not just endorsing a brand but investing capital and co-creating a product line suggests this isn't a celebrity endorsement dressed up as a partnership. She has skin in the game.

## The Business Case

Agilitas is backed by Convergent Finance and Nexus Venture Partners. The company has also acquired long-term Lotto licensing rights across several markets and purchased footwear manufacturer Mochiko Shoes. With the Virat-Anushka one-two punch, Agilitas now has arguably the strongest celebrity co-founder bench in Indian sportswear.

The athleisure market in India is no longer niche. It's being driven by the same forces that made it massive in the West: remote work, fitness culture, and a generation that refuses to dress differently for the gym and the grocery store. Whether One8 Yoga can compete with established global players will depend on product quality, pricing, and distribution — but the launch story writes itself.

*One8 Yoga drops on June 21. Set a reminder.*"""
})

# --- ARTICLE 4: Salman Khan Maatrubhumi screening ---
print("\n📝 Article 4: Salman Khan Maatrubhumi screening...")
img4 = fetch_wikipedia_person_image("Salman Khan")
if not validate_image_url(img4):
    img4 = fetch_pexels_image("Indian soldiers border patrol")

articles.append({
    'headline': "Salman Khan Screened Maatrubhumi for Bollywood's Most Powerful Directors. Subhash Ghai Called It a 'Must-Watch.'",
    'subheadline': "Sooraj Barjatya, Kabir Khan, David Dhawan, and Riteish Deshmukh were among those who watched the rough cut of the Galwan Valley war drama. The film still has no release date.",
    'slug': 'salman-khan-maatrubhumi-rough-cut-screening-subhash-ghai-kabir-khan-nri-20260530',
    'image_url': img4 or '',
    'image_attribution': 'Wikimedia Commons' if img4 and ('wikipedia' in str(img4).lower() or 'wikimedia' in str(img4).lower()) else '',
    'sources': [
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
        {"name": "IANS", "url": "https://ianslive.in"},
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Maatrubhumi:_May_War_Rest_in_Peace"}
    ],
    'body': """Salman Khan hosted a private screening of the rough cut of *Maatrubhumi: May War Rest in Peace* on May 28, inviting a room full of filmmakers who collectively account for some of the biggest box office hits in Hindi cinema history. The verdict, at least from the room, appears to be strongly positive.

Veteran filmmaker Subhash Ghai shared a group photograph from the screening that read like a Bollywood power summit: Salman Khan, Chitrangda Singh, director Apoorva Lakhia, Sooraj Barjatya, Kabir Khan, David Dhawan, Riteish Deshmukh, Rumy Jafry, and producer Siddharth Roy Kapur — all gathered at what Ghai described as "food square."

## Ghai's Verdict

"It was so beautiful to see my favourite directors together at food square today to watch a rough cut of Apoorva Lakhia's film Maatrubhumi with lead stars Salman Khan and Chitrangda, based on a touching story of soldiers of India and China with their respective emotions for their nations and their families with a theme of mutual peace and respect," Ghai wrote on social media. He added that the film was "truly a must-watch."

Coming from a filmmaker who has directed some of Hindi cinema's most commercially successful dramas — *Taal*, *Pardes*, *Ram Lakhan* — the endorsement carries weight, even if private screenings for friends are not exactly known for producing scathing reviews.

## The Film That Changed Its Name and Lost Its Date

*Maatrubhumi* has had one of the more complicated journeys to the screen in recent Bollywood memory. Originally titled *Battle of Galwan*, the film is reportedly inspired by the 2020 Galwan Valley clash between Indian and Chinese troops — an incident that left 20 Indian soldiers dead and remains one of the most sensitive military confrontations in recent India-China relations.

The teaser, released on Salman's birthday in December 2025, drew immediate backlash from Chinese state-backed media, including the *Global Times*, which characterized the film as provocative. Reports subsequently suggested that the filmmakers were advised to soften the political tone and reduce direct references that could escalate diplomatic sensitivities.

The result: a title change from *Battle of Galwan* to the broader *Maatrubhumi: May War Rest in Peace*, approximately 40 days of reshoots to revise certain portions, and an indefinite postponement of the original April 17, 2026 release date. The film is now reportedly targeting an Independence Day weekend release, though nothing has been officially confirmed.

## Why Salman Screened It for This Specific Group

The guest list wasn't random. Sooraj Barjatya directed Salman in *Maine Pyar Kiya*, *Hum Aapke Hain Koun*, and *Prem Ratan Dhan Payo*. Kabir Khan gave him *Bajrangi Bhaijaan* and *Ek Tha Tiger*. David Dhawan directed *Judwaa*, *Biwi No. 1*, and *Partner*. These are the directors who know what works for Salman on screen — and their collective nod carries more industry credibility than any marketing campaign.

Siddharth Roy Kapur's presence is also notable. The former head of UTV and current independent producer is one of the sharpest distribution minds in the business. If he's in the room watching the rough cut, the business side of the release is likely being planned in parallel.

## The Diaspora Angle

For NRIs, *Maatrubhumi* sits at the intersection of nationalism, geopolitics, and Bollywood spectacle — three things that reliably generate strong opinions in the diaspora. The Galwan Valley incident resonated deeply with Indians abroad, many of whom followed the crisis through WhatsApp forwards and news alerts in real time. A Salman Khan blockbuster built around that moment — repackaged now as a peace-themed narrative — will inevitably be one of the most-discussed films of the year in Indian communities worldwide.

Whether the tonal shift from "Battle" to "May War Rest in Peace" satisfies audiences who wanted a more assertive narrative remains to be seen. But Subhash Ghai's "must-watch" verdict and the caliber of the room that witnessed the rough cut suggest the film has substance behind the spectacle.

*No release date has been announced. The wait continues.*"""
})

# --- ARTICLE 5: Aditya Seal & Anushka Ranjan pregnancy ---
print("\n📝 Article 5: Aditya Seal & Anushka Ranjan pregnancy...")
img5 = fetch_pexels_image("baby shoes maternity pregnancy announcement", "maternity photoshoot sunset")

articles.append({
    'headline': "Aditya Seal Wore a T-Shirt That Said 'Baap' in Hindi. That's How He Announced He's Going to Be a Father.",
    'subheadline': "The Student of the Year 2 actor and actress Anushka Ranjan are expecting their first child, four years after their star-studded Mumbai wedding.",
    'slug': 'aditya-seal-anushka-ranjan-pregnancy-announcement-first-child-bollywood-nri-20260530',
    'image_url': img5 or '',
    'image_attribution': 'Pexels' if img5 and 'pexels' in str(img5).lower() else '',
    'sources': [
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
        {"name": "Pinkvilla", "url": "https://pinkvilla.com"},
        {"name": "ANI", "url": "https://aninews.in"}
    ],
    'body': """Actor Aditya Seal and actress-producer Anushka Ranjan have announced they are expecting their first child together. The couple shared the news on May 28 through a joint Instagram post featuring maternity photographs that managed to be both tender and perfectly on-brand.

In the photos, Anushka wears a fitted black outfit while Aditya twins in a matching black ensemble — except for one detail that became the most talked-about element of the announcement. His T-shirt had the word "Baap" printed in Hindi across the chest.

No elaborate gender reveal party. No drone show. Just the Hindi word for "dad" on a T-shirt, and the internet understood.

## The Caption That Hit Different

The couple's shared caption read: "I've waited a hundred years, But I'd wait a million more for you. Nothing prepared me for, What the privilege of being yours would do."

The sunset-lit maternity shoot, captured against a natural backdrop, showed Aditya holding Anushka close — the kind of intimate, warm imagery that felt deliberately personal rather than produced for maximum virality. Which, ironically, made it go more viral.

## Bollywood's Response

The congratulations poured in fast. Ananya Panday wrote, "Aw yay! Congratulations." Sonakshi Sinha dropped an "Omgggggg congratulationsssss guyyyysss." Bhumi Pednekar delivered a message that was essentially one long "OMG" with heart emojis. Rakul Preet Singh, Mouni Roy, Vaani Kapoor, Manish Malhotra, Neil Nitin Mukesh, Sonal Chauhan, Huma Qureshi, Pulkit Samrat, and Kushal Tandon all added their wishes.

The industry support reflects the couple's well-liked status within Bollywood circles. Anushka Ranjan's family has deep industry ties — her father, Shashi Ranjan, is a prominent producer and entertainment industry figure — and the couple's 2021 wedding was itself a Bollywood event, attended by Alia Bhatt, Vaani Kapoor, and Athiya Shetty, among others.

## From On-Screen Villainy to Real-Life Romance

Aditya Seal entered the public consciousness as Manav, the slick antagonist in *Student of the Year 2*. Since then, he has built a steady career across both theatrical and streaming projects, including *Tum Bin II*, *The Empire*, and *Khel Khel Mein*. His upcoming slate includes *Sundar Poonam* alongside Sanya Malhotra.

Anushka Ranjan's credits include *Wedding Pullav* and *Batti Gul Meter Chalu*, though she has increasingly focused on production. The couple first met at a family event, dated for four years, and Aditya proposed in Paris on Anushka's birthday — a detail that would be too scripted for a Bollywood film but works perfectly in real life.

## Why Bollywood Baby Announcements Matter to the Diaspora

There's a specific genre of joy that NRIs experience when Bollywood couples announce pregnancies. It's the same parasocial warmth that drives people to forward wedding photos in family WhatsApp groups and send congratulatory messages to strangers on Instagram. Bollywood's couples aren't just celebrities — for the diaspora, they're proxies for cultural continuity, markers of "our people" doing well and building families.

The "Baap" T-shirt, in particular, hits a chord. In a world of elaborate English-language pregnancy announcements designed for global consumption, there's something satisfying about a Hindi word on a T-shirt doing all the heavy lifting. No translation needed.

*Congratulations to the couple. The countdown to the "Mini Seal" Instagram account begins.*"""
})


# ===================== PUBLISH ALL =====================

print("\n" + "="*60)
print("Publishing articles...")
print("="*60)

for i, article in enumerate(articles, 1):
    print(f"\n--- Article {i}/{len(articles)} ---")
    result = publish_article(article)
    if result:
        print(f"  ID: {result}")
    time.sleep(1)

print("\n✅ Entertainment writer batch complete!")
