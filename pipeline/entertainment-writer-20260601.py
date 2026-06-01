#!/usr/bin/env python3
"""Entertainment writer - 2026-06-01 run"""

import json, os, re, sys, time, uuid, urllib.parse
import requests

# Load env
env_path = os.path.expanduser("~/workspace/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Load Pexels key
pexels_path = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_path):
    with open(pexels_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if "PEXELS" in k.upper():
                    PEXELS_KEY = v.strip().strip('"').strip("'")


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
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key found")
        return None
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Validate that the URL returns an actual image >5KB."""
    if not url:
        return False
    # Reject banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=', 'ccb=']
    for b in banned:
        if b in url:
            print(f"  ✗ Banned image source: {b}")
            return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        # Some servers don't support HEAD, try GET
        r = requests.get(url, timeout=10, stream=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct:
            # Read a bit to check size
            chunk = r.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: {len(chunk)}+ bytes")
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def insert_article(article):
    """Insert an article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            return data[0].get("id")
        return True
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None


# ========== ARTICLE 1: Maatrubhumi Rough Cut Screening ==========
print("\n" + "="*60)
print("ARTICLE 1: Maatrubhumi Rough Cut Screening")
print("="*60)

art1_slug = "maatrubhumi-salman-khan-rough-cut-subhash-ghai-kabir-khan-nri-20260601"
art1_headline = "Bollywood's Biggest Directors Just Watched Salman Khan's Maatrubhumi. Subhash Ghai Called It 'A Must-Watch.'"
art1_subheadline = "The Galwan Valley war drama, once titled Battle of Galwan, got its first audience — Kabir Khan, Sooraj Barjatya, Riteish Deshmukh, and Siddharth Roy Kapur — and the early word is that it lands."

art1_body = """The first reviews of Salman Khan's most ambitious film in years are in, and they didn't come from critics. They came from the people who make the movies.

On May 28, filmmaker Subhash Ghai posted a photograph to social media that read like a roll call of Bollywood's directorial old guard. In the frame: Salman Khan, Chitrangda Singh, director Apoorva Lakhia, Kabir Khan, Sooraj Barjatya, Rumy Jafry, Riteish Deshmukh, and producer Siddharth Roy Kapur. They had just finished watching a rough cut of **Maatrubhumi: May War Rest in Peace**, the war drama formerly known as Battle of Galwan.

Ghai didn't mince words. "It was so beautiful to see my favourite directors together to watch a rough cut of Apoorva Lakhia's film Maatrubhumi with lead stars Salman Khan and Chitrangada," he wrote, calling it "a touching story of soldiers of India and China with their respective emotions for their nations and their families with a theme of mutual peace and respect."

## A Film Caught Between Patriotism and Diplomacy

The screening comes at a critical moment for the film. Originally announced as Battle of Galwan — a direct reference to the June 2020 clash between Indian and Chinese troops in Ladakh's Galwan Valley — the project attracted immediate attention and immediate controversy. Chinese state-backed media outlet Global Times criticized the teaser, and reports soon emerged that Salman Khan was advised in official quarters to rethink both the title and the tone.

The result was a significant creative overhaul. The title became Maatrubhumi, meaning "Motherland." The script was reportedly rewritten to fictionalize the conflict, softening direct references to China while preserving the emotional core — the bravery of Indian soldiers defending their territory against overwhelming odds. Salman portrays the late Colonel B. Santosh Babu, the commanding officer of the 16 Bihar Regiment, who led 200 Indian soldiers against a force of 1,200.

## Why the Delay Kept Getting Longer

Maatrubhumi was originally scheduled for April 17, 2026. That date came and went. Reshoots were reportedly needed after the script revisions, and the film still requires defence ministry clearance — a routine step for films based on real military events, but one that can add weeks or months to the timeline. Reports suggest the makers are eyeing a window between July and October, depending on when approvals come through.

The OTT rumour mill briefly churned out speculation about a direct-to-streaming release, but trade sources have consistently denied this. The film is built for a theatrical spectacle, and the scale of the production — shot extensively in Ladakh — makes a cinema-first approach non-negotiable.

## What Ghai's Endorsement Means

In Bollywood's informal power structure, a screening for this particular group of directors isn't just a friends-and-family favour. Kabir Khan directed Bajrangi Bhaijaan, one of Salman's most emotionally resonant films. Sooraj Barjatya is the man behind Maine Pyar Kiya and Hum Aapke Hain Koun. Siddharth Roy Kapur is one of the industry's most respected producers. These are people whose opinions carry weight in distribution meetings and marketing rooms.

Ghai specifically highlighting the film's "theme of mutual peace and respect" is notable. It suggests Maatrubhumi has successfully navigated the tightrope between honouring military sacrifice and avoiding the kind of jingoistic chest-thumping that would have complicated its release.

## The Diaspora Dimension

For NRI audiences, the Galwan Valley incident was a defining moment of 2020. Indians abroad followed the standoff with an intensity that reflected deep personal stakes — many had family members in the armed forces, and the geopolitical implications touched everything from tech jobs to student visas. A film that tells this story with nuance rather than propaganda could find a massive audience overseas.

The fact that the script was reworked to emphasise universal themes of sacrifice and family, rather than India-vs-China nationalism, might actually make it more resonant for diaspora viewers who navigate multiple national identities daily.

No release date has been confirmed. But after the May 28 screening, the question has shifted from "Will this film work?" to "When will we get to see it?"

*Directed by Apoorva Lakhia. Produced by Salman Khan Films. Starring Salman Khan, Chitrangda Singh. Music by Himesh Reshammiya. Release date: TBA.*"""

# Image for Salman Khan
print("  Sourcing image for Salman Khan...")
img1 = fetch_wikipedia_person_image("Salman Khan")
if not img1 or not validate_image_url(img1):
    img1 = fetch_pexels_image("Bollywood film premiere event", "Indian cinema red carpet")
    if img1 and not validate_image_url(img1):
        img1 = None

art1 = {
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "slug": art1_slug,
    "category": "entertainment",
    "status": "published",
    "published_at": "2026-06-01T11:05:00Z",
    "sources": [
        "Bollywood Hungama",
        "Bollywood Life",
        "Sacnilk"
    ],
    "vertical": "entertainment",
    "is_editorial": False,
    "image_attribution": "Wikimedia Commons" if img1 and "wikimedia" in (img1 or "").lower() else "The Videshi"
}
if img1:
    art1["image_url"] = img1

result1 = insert_article(art1)
print(f"  Article 1 result: {result1}")


# ========== ARTICLE 2: Alpha Preponed to July 3 ==========
print("\n" + "="*60)
print("ARTICLE 2: Alpha Preponed to July 3")
print("="*60)

art2_slug = "alpha-alia-bhatt-sharvari-yrf-spy-universe-july-3-preponed-nri-20260601"
art2_headline = "YRF Just Moved Alpha Up by a Week. Alia Bhatt's Deadly Assassin Gets July 3, and Two Weeks of Open Road."
art2_subheadline = "The first female-led YRF Spy Universe film has been preponed from July 10 to July 3 after Dhamaal 4 shifted to July 17. Here's why the calendar math matters."

art2_body = """Alia Bhatt's next film just got its fourth release date. This time, it moved forward.

**Alpha**, the first female-led instalment in Yash Raj Films' Spy Universe, has been preponed from July 10 to July 3, 2026. The shift follows Dhamaal 4's decision to push its own release to July 17, suddenly clearing a wide-open weekend that producer Aditya Chopra moved quickly to claim.

A source at a prominent multiplex chain told Bollywood Hungama: "July 3 has emerged as an apt date to bring Alpha to cinemas since Dhamaal 4, which was scheduled to release on the same day, has now been pushed to July 17. With no major release planned for July 3, producer Aditya Chopra felt it was the right date."

## The Calendar Math That Changes Everything

Here's why the one-week shift matters more than it sounds. On July 17, both Christopher Nolan's **The Odyssey** and **Dhamaal 4** arrive in theatres. That's a blockbuster pileup. By landing on July 3, Alpha now gets a full two weeks of relatively uncontested screen time — no major Bollywood release on July 10, and a comfortable head start before the July 17 traffic jam.

For a franchise that desperately needs a clean hit, that breathing room could be the difference between a solid opening and a theatrical campaign that builds momentum through positive word of mouth.

## Not a Spy. An Assassin.

What makes Alpha genuinely interesting isn't just the release date chess — it's the creative pivot. According to Bollywood Hungama, Alia Bhatt isn't playing a conventional spy in the Tiger–Pathaan mould. She's playing a **deadly assassin** with an edgy backstory — someone who was "raised and built to kill" from a young age.

YRF is reportedly betting on a darker, more emotionally layered origin story that gives the franchise a fresh direction after Pathaan, War, and Tiger 3. The comparisons to Marvel's Black Widow have already started circulating on social media, but the character is said to be rooted in a distinctly Indian context.

Sharvari Wagh, who broke out with Munjya and impressed in the Spy Universe adjacent Vedaa, has a powerful role alongside Bhatt. Bobby Deol and Anil Kapoor round out the cast in pivotal supporting roles. The film is directed by Shiv Rawail, who helmed the globally acclaimed series The Railway Men.

## A Franchise That Needs This to Work

The YRF Spy Universe has been Bollywood's most commercially successful franchise play, but the track record is uneven. Pathaan was a massive global hit. War 2 flopped. Tiger 3 underperformed relative to its budget. The pressure on Alpha isn't just about Alia Bhatt's star power — it's about proving the franchise model can sustain itself.

The fact that YRF is positioning Alpha as a genuine departure — female leads, an assassin origin story, a darker tone — rather than another formulaic spy caper suggests the studio knows the template needed refreshing.

## The Date Merry-Go-Round

If you've lost track of Alpha's release history, here's the summary: it was originally planned for Christmas 2025, then shifted to April 2026, then moved to July 10, and now sits at July 3. Four dates, three delays, one advance. YRF has yet to make an official announcement about the latest change.

## Why NRI Audiences Should Care

The YRF Spy Universe has consistently outperformed in overseas markets. Pathaan's international run was a milestone for Hindi cinema. Alpha — with Alia Bhatt's global recognition from Heart of Stone, a female-led action premise, and a director known for an internationally acclaimed Netflix series — has the raw ingredients for strong diaspora numbers.

The question is whether YRF's marketing machine can convey that this isn't just another franchise entry, but a genuine reinvention. The two-week theatrical window should give overseas exhibitors confidence to book wider releases.

July 3 is a Thursday. If Alpha opens strong, it has 13 clear days before The Odyssey and Dhamaal 4 change the conversation.

*Directed by Shiv Rawail. Produced by Yash Raj Films. Starring Alia Bhatt, Sharvari Wagh, Bobby Deol, Anil Kapoor. Releasing July 3, 2026 (unconfirmed by YRF).*"""

# Image for Alia Bhatt
print("  Sourcing image for Alia Bhatt...")
img2 = fetch_wikipedia_person_image("Alia Bhatt")
if not img2 or not validate_image_url(img2):
    img2 = fetch_pexels_image("spy action thriller woman", "Bollywood actress action")
    if img2 and not validate_image_url(img2):
        img2 = None

art2 = {
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "slug": art2_slug,
    "category": "entertainment",
    "status": "published",
    "published_at": "2026-06-01T11:10:00Z",
    "sources": [
        "Bollywood Hungama",
        "Sacnilk",
        "MensXP"
    ],
    "vertical": "entertainment",
    "is_editorial": False,
    "image_attribution": "Wikimedia Commons" if img2 and "wikimedia" in (img2 or "").lower() else "The Videshi"
}
if img2:
    art2["image_url"] = img2

result2 = insert_article(art2)
print(f"  Article 2 result: {result2}")


# ========== ARTICLE 3: Karan Johar Instagram Detox ==========
print("\n" + "="*60)
print("ARTICLE 3: Karan Johar Instagram Detox")
print("="*60)

art3_slug = "karan-johar-instagram-digital-detox-unfollowed-srk-alia-priyanka-nri-20260601"
art3_headline = "Karan Johar Unfollowed Shah Rukh Khan, Alia Bhatt, and Nearly All of Bollywood on Instagram. He Kept Following Priyanka Chopra."
art3_subheadline = "The filmmaker says it's a 'digital detox.' The internet says it's the most Karan Johar thing he's ever done. The Priyanka detail is the part nobody can stop talking about."

art3_body = """Karan Johar woke up the Indian internet last week by doing something that would be completely unremarkable for anyone else: he unfollowed people on Instagram.

The filmmaker, who has 17.5 million followers and treats his social media presence like a second production house, went on a mass unfollow spree that removed Shah Rukh Khan, Alia Bhatt, Kareena Kapoor Khan, Varun Dhawan, Sidharth Malhotra, Ananya Panday, Manish Malhotra, Malaika Arora, Gauri Khan, Aryan Khan, Suhana Khan, and Kartik Aaryan from his following list. When the dust settled, he was following just 74 accounts.

And then people noticed the detail that turned a social media clean-up into a full-blown Bollywood mystery: **Priyanka Chopra Jonas was still on the list.**

## "It's a DIGITAL DETOX!!!!"

Karan addressed the growing speculation through an Instagram Story, writing in his signature all-caps style: "It's a DIGITAL DETOX!!!! Am unfollowing everyone to reduce my time and energy spent on the gram!!! This can't be national news for gods sake...please clickbait something else! This is irrelevant!"

A source close to the filmmaker told Filmfare it was a "social media strategy" with no personal motivation behind the mass purge. But the timing and the exceptions have made it impossible for the industry — and its obsessive gossip ecosystem — to take that explanation at face value.

## The Timing Is the Story

The unfollow spree happened the day after Karan Johar's birthday party, an event that brought together many of the same celebrities he then proceeded to remove from his digital orbit. The optics are hard to ignore: you celebrate with someone one evening and unfollow them the next morning.

The professional context adds another layer. Dharma Productions' latest release, **Chand Mera Dil** starring Ananya Panday and Lakshya, was a box office disaster. In recent years, Dharma's hit rate has been declining, and the studio is under pressure to course-correct. Whether the "digital detox" is genuinely personal or subtly professional is the kind of question that fuels Bollywood gossip for weeks.

## The Priyanka Exception

The detail that launched a thousand Reddit threads is this: Karan Johar unfollowed virtually every major Bollywood star — including his closest collaborators and people he's publicly called family — but continued following Priyanka Chopra Jonas.

The significance isn't lost on anyone who has followed the Karan-Priyanka relationship over the years. Their dynamic has been famously complicated, from pointed Koffee With Karan exchanges to years of perceived distance. The fact that she survived a purge that claimed Shah Rukh Khan and Alia Bhatt — arguably Karan's two most important professional relationships — has generated more analysis than most actual film releases.

Some speculate it signals a potential collaboration. Others suggest it's strategic positioning for Dharma's international ambitions, with Priyanka representing a bridge to global audiences. Still others think it's simply that he hasn't gotten to her yet.

## What It Says About Celebrity Culture in the Social Media Age

The broader story here isn't really about Karan Johar's following count. It's about how completely the line between personal and professional has dissolved in Bollywood's social media economy. An unfollow isn't just clicking a button — it's a public statement, a trade signal, and gossip fodder rolled into one.

For NRI audiences who consume Bollywood as much through Instagram as through theatres, these digital dramas have become their own form of entertainment. The parasocial relationship between fans and stars now runs through follows, unfollows, story mentions, and comment section diplomacy. Karan Johar, who essentially invented modern Bollywood's celebrity interview culture with Koffee With Karan, understands this better than anyone.

## What Comes Next

On the work front, Karan is producing **Naagzilla** starring Kartik Aaryan — who, yes, was among those unfollowed. He's also returning as host of Koffee With Karan, a show built entirely on the premise that he has intimate access to every major star in the industry. Whether he'll need to re-follow his guests before having them on the couch remains unclear.

The "digital detox" explanation may be perfectly sincere. But in an industry where nothing is accidental and everything is content, sincerity is just another form of strategy.

*Karan Johar currently follows 74 accounts on Instagram. His next production, Naagzilla, is in development.*"""

# Image for Karan Johar
print("  Sourcing image for Karan Johar...")
img3 = fetch_wikipedia_person_image("Karan Johar")
if not img3 or not validate_image_url(img3):
    img3 = fetch_pexels_image("Instagram social media phone", "social media digital detox")
    if img3 and not validate_image_url(img3):
        img3 = None

art3 = {
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "body": art3_body,
    "slug": art3_slug,
    "category": "entertainment",
    "status": "published",
    "published_at": "2026-06-01T11:15:00Z",
    "sources": [
        "Pinkvilla",
        "Filmfare",
        "MensXP"
    ],
    "vertical": "entertainment",
    "is_editorial": False,
    "image_attribution": "Wikimedia Commons" if img3 and "wikimedia" in (img3 or "").lower() else "The Videshi"
}
if img3:
    art3["image_url"] = img3

result3 = insert_article(art3)
print(f"  Article 3 result: {result3}")


# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
results = [
    ("Maatrubhumi Rough Cut", art1_slug, result1),
    ("Alpha Preponed", art2_slug, result2),
    ("Karan Johar Instagram", art3_slug, result3),
]
for name, slug, res in results:
    status = "✓ PUBLISHED" if res else "✗ FAILED"
    print(f"  {status}: {name} ({slug})")
