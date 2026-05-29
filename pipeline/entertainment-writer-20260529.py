#!/usr/bin/env python3
"""Entertainment writer for The Videshi - May 29, 2026 run"""

import json
import os
import re
import sys
import time
import uuid
import requests
import subprocess
from datetime import datetime, timezone

# Load env
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            val = val.strip().strip('"').strip("'")
            os.environ[key.strip()] = val

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Load Pexels key
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                val = val.strip().strip('"').strip("'")
                if "PEXELS" in key.upper():
                    PEXELS_KEY = val

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
    """Fetch image from Pexels. Use curl approach."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key found")
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=5",
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        for photo in photos:
            url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
            if url:
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
        if fallback_query:
            return fetch_pexels_image(fallback_query)
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None

def validate_image(url):
    """Validate image URL returns HTTP 200 with image content type and reasonable size."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {content_type}, {content_length} bytes")
            return True
        else:
            print(f"  ⚠ Image validation failed: status={r.status_code}, type={content_type}, size={content_length}")
            return False
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
        return False

def publish_article(article):
    """Publish article to Supabase."""
    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(article["sources"]),
        "image_url": article.get("image_url"),
        "image_caption": article.get("image_caption"),
        "image_attribution": article.get("image_attribution"),
    }
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data["id"]
        print(f"  ✓ Published: {article['headline'][:60]}... (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Failed to publish: {r.status_code} - {r.text[:200]}")
        return None


# ============================================================
# ARTICLE 1: Jailer 2 - Hrithik Roshan cameo talks
# ============================================================
print("\n=== Article 1: Jailer 2 - Hrithik Roshan Cameo ===")

art1_headline = "Hrithik Roshan Is in Talks to Join Rajinikanth's Jailer 2. Shah Rukh Khan Was the First Choice."
art1_subheadline = "The makers of the most anticipated Tamil sequel of 2026 are reportedly in discussions with Hrithik after SRK stepped away due to King commitments. If confirmed, it would reunite Rajinikanth and Hrithik 40 years after Bhagwaan Dada."
art1_slug = "hrithik-roshan-jailer-2-cameo-rajinikanth-shah-rukh-khan-nelson-dilipkumar-nri-20260529"
art1_body = """The biggest casting rumour in Indian cinema this week doesn't involve a lead role. It involves a cameo — and the two names attached to it tell you everything about where the industry is heading.

## SRK Was the Plan. His Calendar Wasn't.

When Nelson Dilipkumar began assembling the sequel to his 2023 blockbuster *Jailer*, the playbook was clear: replicate the formula that turned the original into a ₹600-crore global phenomenon. That meant Rajinikanth as the anchor, Anirudh Ravichander on the score, and a roster of surprise appearances from stars across every Indian film industry.

Shah Rukh Khan was the centrepiece of that plan. According to multiple trade reports, including confirmations from veteran actor Mithun Chakraborty — who is also part of the sequel — both he and SRK were slated for pivotal cameos. The logic was bulletproof: after *Jawan* turned Khan into a mass favourite in the South Indian market, pairing him with Rajinikanth in a Nelson film would have been a theatrical event unto itself.

But *King* got in the way. Shah Rukh Khan's own production, which is targeting a Christmas 2026 release, demanded his full attention. Reports from Pinkvilla and Valai Pechu confirm that Khan "politely declined" the cameo, and portions planned with him remain unfilmed.

## Enter Hrithik Roshan

The makers have reportedly pivoted to Bollywood's other Greek god. According to reports from Bombay Times, MensXP, and Pinkvilla, the *Jailer 2* team is now in active discussions with Hrithik Roshan for the same high-profile cameo slot.

No official confirmation has come from Sun Pictures, the production house bankrolling the sequel. But if the talks materialise, the casting would carry emotional weight that goes far beyond box-office strategy.

## A 40-Year Reunion

Here is where the story gets interesting for anyone who grew up watching Hindi cinema in the 1980s. Hrithik Roshan made his screen debut as a child artist in the 1986 action drama *Bhagwaan Dada* — a film that starred Rajinikanth in the lead role. The seven-year-old Hrithik played Rajinikanth's young foster son on screen.

In interviews over the decades, Hrithik has spoken with warmth about what he learned from Rajinikanth on that set. A reunion four decades later, both as superstars in their own right, would be the kind of narrative arc that Bollywood couldn't script better if it tried.

## What Jailer 2 Already Has

Even without the cameo question resolved, the sequel is stacked. Rajinikanth returns as "Tiger" Muthuvel Pandian. The confirmed cast includes Vidya Balan, S.J. Suryah, Ramya Krishnan (reprising her role as Viji Pandian), Suraj Venjaramoodu, Jatin Sarna, and Mithun Chakraborty. Mohanlal and Shiva Rajkumar are expected to reprise their appearances from the first film. Vijay Sethupathi also has a confirmed cameo.

Principal photography wrapped in April 2026 after shoots across Chennai, Goa, and Kerala. Anirudh Ravichander is composing the music. The film is eyeing a June 12 theatrical release — just two weeks away.

## The Diaspora Angle

For NRI audiences, *Jailer* was a cultural event. The original collected over ₹150 crore overseas and became one of the highest-grossing Tamil films in international markets. Advance booking patterns for the sequel are expected to follow a similar trajectory, particularly in the US, UK, Canada, and the Gulf, where Rajinikanth retains a devoted fanbase that spans generations.

Adding Hrithik Roshan — whose *War* and *Fighter* performed strongly in overseas markets — would only amplify that pull. The real question isn't whether Nelson can get Hrithik. It's whether two weeks is enough time to shoot, edit, and integrate a cameo before the June 12 release date. In Kollywood, stranger things have happened."""

art1_sources = [
    {"name": "Pinkvilla", "url": "https://www.pinkvilla.com"},
    {"name": "Bombay Times", "url": "https://www.bombaytimes.com"},
    {"name": "MensXP", "url": "https://www.mensxp.com"},
    {"name": "Tupaki English", "url": "https://english.tupaki.com"}
]

# Image: Try Hrithik Roshan Wikipedia
img1 = fetch_wikipedia_person_image("Hrithik Roshan")
if not img1:
    img1 = fetch_wikipedia_person_image("Rajinikanth")
img1_valid = img1 and validate_image(img1)

art1 = {
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "slug": art1_slug,
    "sources": art1_sources,
    "image_url": img1 if img1_valid else None,
    "image_caption": "Hrithik Roshan is reportedly in talks for a cameo in Rajinikanth's Jailer 2" if img1_valid else None,
    "image_attribution": "Wikimedia Commons" if img1_valid else None,
}

id1 = publish_article(art1)

# ============================================================
# ARTICLE 2: Pankaj Bhadouria breast cancer diagnosis + surgery
# ============================================================
print("\n=== Article 2: Pankaj Bhadouria Cancer Diagnosis ===")

art2_headline = "India's First MasterChef Winner Has Breast Cancer. She Went Into Surgery on Friday Morning."
art2_subheadline = "Pankaj Bhadouria, who left a 16-year teaching career to win MasterChef India Season 1 in 2010, revealed her diagnosis from a hospital bed on Thursday. By Friday, she was headed for the operating room."
art2_slug = "pankaj-bhadouria-masterchef-india-breast-cancer-surgery-nri-20260529"
art2_body = """Pankaj Bhadouria posted a photograph from a hospital bed on Thursday afternoon, medical wires visible, patient gown on, and wrote seven words that stopped her millions of followers mid-scroll: "I have been diagnosed with Breast Cancer."

By Friday morning, she was recording another video — this time to say thank you, and to say she was going in for surgery.

## The Diagnosis

The announcement came on May 28 through Bhadouria's social media accounts. In a video message that followed the initial post, she addressed her audience directly, her voice steady but her eyes betraying the weight of the moment.

"I just wanted to share with you all that I have been diagnosed with breast cancer," she said. "Since all of you are like an extended family to me, I wanted to share this with you personally. Right now, I truly need your prayers and support. As they say, prayers work miracles. So please keep me in your prayers."

A separate Instagram story showed her undergoing a battery of medical tests, with the text overlay reading: "Going for tests and more tests… not a happy place to be."

## "I Know I Will Bounce Back"

On Friday morning — less than 24 hours after going public — Bhadouria shared a brief update confirming she was heading into surgery. "Thank you so much for all the love and support that you have showered on me," she said. "Today I am going for surgery and I know I will bounce back. So, once again keep me in your prayers."

The response from fans, fellow chefs, and the television industry has been immediate and overwhelming.

## From English Teacher to India's First MasterChef

For those who may not remember, Pankaj Bhadouria's story is one of the most remarkable career pivots in Indian television history. Before she ever appeared on camera, she spent 16 years as an English teacher in Lucknow. Cooking was a passion, not a profession — until she decided to audition for the very first season of *MasterChef India* in 2010.

The show, hosted by Akshay Kumar, was attempting to bring a proven international format to Indian television. Bhadouria won the inaugural season and became the country's first-ever MasterChef champion. The victory didn't just change her career. It created one.

What followed was a decade-plus run as one of India's most recognisable celebrity chefs. She hosted *Chef Pankaj Ka Zayka*, *Kifayati Kitchen*, *3 Course with Pankaj*, and *Rasoi Se — Pankaj Bhadouria Ke Saath*, among other shows. Her YouTube channel became a go-to destination for home cooks across India and the diaspora, with recipes that ranged from everyday dal to elaborate festive spreads.

## Why This Matters to the Diaspora

Bhadouria's reach extends well beyond India's borders. Her cooking videos have been a staple for Indian families abroad trying to recreate the flavours of home — particularly first-generation immigrants in the US, UK, and Canada who grew up watching her on Indian television and later followed her to YouTube and social media.

For many NRI households, her recipes became a bridge between homesickness and the kitchen. The news of her diagnosis has resonated deeply in diaspora communities where her face is synonymous with Indian home cooking.

## Breast Cancer in India: The Larger Context

Bhadouria's decision to go public with her diagnosis adds to a growing list of Indian public figures who have chosen transparency over silence when it comes to cancer. Actors Sonali Bendre, Manisha Koirala, Lisa Ray, and Tahira Kashyap have all spoken about their experiences, helping to destigmatise the conversation in a culture where health disclosures — particularly around cancer — have historically been kept private.

Breast cancer is the most common cancer among Indian women, with approximately 180,000 new cases diagnosed annually, according to the Indian Council of Medical Research. Early detection remains a critical challenge, particularly in smaller cities and rural areas.

## What Comes Next

No details about the type or stage of Bhadouria's cancer, or the specifics of her surgical procedure, have been shared publicly. What is clear is that she intends to fight — and that her community, both in India and abroad, is rallying behind her.

For now, she's asked for one thing: prayers. Given the outpouring that has followed, she has them in abundance."""

art2_sources = [
    {"name": "IANS via The Freedom Press", "url": "https://thefreedompress.in"},
    {"name": "Filmibeat", "url": "https://filmibeat.com"},
    {"name": "LatestLY", "url": "https://latestly.com"},
    {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"}
]

# Image: Try Wikipedia for Pankaj Bhadouria
img2 = fetch_wikipedia_person_image("Pankaj Bhadouria")
if not img2:
    img2 = fetch_wikipedia_person_image("Pankaj Bhadouria (chef)")
if not img2:
    # Try Pexels with a relevant query
    img2 = fetch_pexels_image("indian cooking kitchen", "chef kitchen india")
img2_valid = img2 and validate_image(img2)

art2 = {
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "slug": art2_slug,
    "sources": art2_sources,
    "image_url": img2 if img2_valid else None,
    "image_caption": "Pankaj Bhadouria, India's first MasterChef winner, has been diagnosed with breast cancer" if img2_valid else None,
    "image_attribution": "Wikimedia Commons" if (img2_valid and img2 and "wikimedia" in img2.lower()) else ("Pexels" if img2_valid else None),
}

id2 = publish_article(art2)


# ============================================================
# ARTICLE 3: Kangana Ranaut's Bharat Bhhagya Viddhaata motion poster + June 12 release
# ============================================================
print("\n=== Article 3: Kangana Ranaut Bharat Bhhagya Viddhaata ===")

art3_headline = "Kangana Ranaut's 26/11 Film Just Dropped Its First Motion Poster. It Opens June 12, the Same Day as Jailer 2."
art3_subheadline = "Bharat Bhhagya Viddhaata tells the story of hospital staff who saved nearly 400 lives during the 2008 Mumbai terror attacks. The motion poster is titled 'The Unseen Heroes.'"
art3_slug = "kangana-ranaut-bharat-bhhagya-viddhaata-26-11-mumbai-attacks-june-12-nri-20260529"
art3_body = """There are dozens of films about 26/11. Most of them focus on commandos, politicians, or terrorists. Kangana Ranaut's next film focuses on none of those people. It focuses on nurses.

## The Motion Poster

The makers of *Bharat Bhhagya Viddhaata* unveiled the film's first motion poster on Thursday, titled "The Unseen Heroes." It is not a teaser for an action sequence. It is a tribute to the hospital workers — nurses, ward boys, cleaners, lift operators, security guards, and administrators — who kept Cama and Albless Hospital running while Mumbai burned around them on the night of November 26, 2008.

The poster carries a deliberate stillness. No explosions. No gunfire. Just the faces of people who chose to stay.

## What Kangana Said

In a statement released with the poster, Kangana framed the film's thesis in characteristically blunt terms:

"Bharat Bhhagya Viddhaata is a salutation to those invisible souls who, when pushed into crisis, rise to stand as the ultimate shield of humanity and harmony. When disaster strikes, our collective instinct is to look toward armed uniforms or state authorities for salvation. But this film tributes the uniforms nobody notices until the world is burning — the blood-stained aprons, the sterile hospital scrubs, the frayed civilian clothes. True courage does not wait for a badge, permission, or the promise of a medal."

It is, arguably, the strongest creative statement she has made since *Emergency*.

## The Story Behind the Story

On the night of November 26, 2008, two Lashkar-e-Taiba terrorists — Ajmal Kasab and Abu Ismail — passed through the Cama Hospital compound during their rampage from the Chhatrapati Shivaji Terminus railway station. What happened inside that hospital has been overshadowed by the more widely covered sieges at the Taj Mahal Palace Hotel and the Oberoi Trident.

But the staff at Cama Hospital locked wards, hid patients, guided evacuations, and continued treating the injured even as gunfire echoed through the building. By some accounts, their actions helped save nearly 400 lives that night. Most of them have never been publicly identified or honoured.

*Bharat Bhhagya Viddhaata* wants to change that.

## The Team

The film is written and directed by Manoj Tapadia, making his directorial debut. Tapadia, a veteran of the advertising industry, described his creative ambition in terms that suggest this won't be a typical Bollywood retelling:

"In contemporary cinema, the easiest thing to capture on camera is the explosive loudness of the gunfire, the destruction, and the panic. From day one, I challenged our creative team to capture something infinitely more complex: the silence of bravery. We wanted to document that microscopic, split-second window where a common civilian looks at mortal danger, subdues their own survival instinct, and decides to become a human shield."

Marathi actress Girija Oak, known for her work in *Shor in the City*, *Qala*, and *Jawan*, co-stars. The film is produced by Eunoia Films and Floating Rocks Entertainment.

## June 12: A Loaded Release Date

Here is where the commercial calculus gets complicated. *Bharat Bhhagya Viddhaata* is scheduled for a June 12 theatrical release — the same date as Rajinikanth's *Jailer 2*, which is arriving with the force of a franchise juggernaut backed by Sun Pictures and Anirudh Ravichander's score.

On paper, the two films serve different audiences. *Jailer 2* is a Tamil-language action spectacle with pan-India crossover. *Bharat Bhhagya Viddhaata* is a Hindi-language drama rooted in historical realism. But in practice, they'll be competing for the same screens on the same weekend — and in the current theatrical market, screens are zero-sum.

## The Diaspora Connection

For Indians living abroad, the 2008 Mumbai attacks remain one of the most emotionally charged events in modern Indian history. Many NRIs watched the siege unfold in real-time on television, thousands of miles away, unable to do anything but watch. The Taj and the Oberoi became symbols of that helplessness.

A film that shifts the lens to the people who could do something — and did — may find a particularly receptive audience among diaspora viewers. Especially one that doesn't sensationalise the violence but instead honours the quiet, unglamorous heroism of hospital workers.

Whether the film delivers on that promise remains to be seen. But the motion poster, at least, suggests it is trying."""

art3_sources = [
    {"name": "Punjab Page", "url": "https://punjabpage.com"},
    {"name": "Sacnilk", "url": "https://sacnilk.com"},
    {"name": "KoiMoi", "url": "https://koimoi.com"},
    {"name": "Peeping Moon", "url": "https://peepingmoon.com"}
]

# Image: Try Kangana Ranaut Wikipedia
img3 = fetch_wikipedia_person_image("Kangana Ranaut")
img3_valid = img3 and validate_image(img3)

art3 = {
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "body": art3_body,
    "slug": art3_slug,
    "sources": art3_sources,
    "image_url": img3 if img3_valid else None,
    "image_caption": "Kangana Ranaut stars in Bharat Bhhagya Viddhaata, a film about hospital staff during the 26/11 attacks" if img3_valid else None,
    "image_attribution": "Wikimedia Commons" if img3_valid else None,
}

id3 = publish_article(art3)

# Summary
print("\n=== SUMMARY ===")
print(f"Article 1 (Jailer 2 Hrithik): {'✓ Published' if id1 else '✗ Failed'}")
print(f"Article 2 (Pankaj Bhadouria): {'✓ Published' if id2 else '✗ Failed'}")
print(f"Article 3 (Kangana 26/11 film): {'✓ Published' if id3 else '✗ Failed'}")
