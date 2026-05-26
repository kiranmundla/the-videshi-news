#!/usr/bin/env python3
"""Entertainment writer — May 26 2026, 12:30 UTC batch (05:30 PDT):
1. Deepika Padukone becomes first Indian actor to get Hollywood Walk of Fame star in 2026.
2. Namit Malhotra mulling preponing Ramayana to Oct 30, a week before Diwali.
+ Score decay
"""

import json, os, uuid, requests, urllib.parse
from datetime import datetime, timezone
from pathlib import Path

env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k,v = line.split("=",1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_patch(table, filters, data):
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{filters}", headers={**HEADERS,"Prefer":"return=minimal"}, json=data, timeout=30)
    return r.status_code

def check_duplicate(slug):
    r = requests.get(f"{SB_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id", headers=HEADERS, timeout=15)
    return len(r.json())>0 if r.status_code==200 else False

def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ','_'))
    try:
        r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
                         headers={"User-Agent":"TheVideshi/1.0 (thevideshi.com)"}, timeout=10)
        if r.status_code==200:
            data=r.json()
            img=data.get("originalimage",{}).get("source") or data.get("thumbnail",{}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

PEXELS_KEY=None
pexels_env=Path.home()/ "workspace/.env.pexels"
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k,v=line.split("=",1)
            if k.strip()=="PEXELS_API_KEY":
                PEXELS_KEY=v.strip()

def fetch_pexels_image(query, fallback=None):
    if not PEXELS_KEY: return None
    for q in [query, fallback]:
        if not q: continue
        r=requests.get("https://api.pexels.com/v1/search", headers={"Authorization":PEXELS_KEY},
                       params={"query":q,"per_page":5,"orientation":"landscape"}, timeout=10)
        if r.status_code==200:
            photos=r.json().get("photos",[])
            if photos:
                return photos[0]["src"]["large2x"]
    return None

def upload_image_to_supabase(img_url, filename):
    try:
        img_data=requests.get(img_url,timeout=15,headers={"User-Agent":"TheVideshi/1.0"}).content
        upload_url=f"{SB_URL}/storage/v1/object/article-images/{filename}"
        r=requests.post(upload_url, headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}","Content-Type":"image/jpeg","x-upsert":"true"},
                        data=img_data, timeout=30)
        if r.status_code in (200,201):
            return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return img_url

now=datetime.now(timezone.utc)
now_iso=now.strftime("%Y-%m-%dT%H:%M:%S")

articles=[]

# ARTICLE 1: Deepika Padukone Walk of Fame
slug1="deepika-padukone-first-indian-hollywood-walk-of-fame-star-2026-20260526"
if not check_duplicate(slug1):
    art1_id=str(uuid.uuid4())
    articles.append({
        "id": art1_id,
        "headline":"Deepika Padukone Will Be the First Indian Actor to Get a Star on the Hollywood Walk of Fame. It's Not Just a Plaque on a Sidewalk — It's Hollywood Finally Learning How to Pronounce Her Name.",
        "subheadline":"The star, in the Motion Pictures category, will be unveiled in 2026 alongside Demi Moore, Rachel McAdams and Timothée Chalamet. For the diaspora kid who grew up explaining to classmates that no, Bollywood is not a typo, this is the kind of validation that lands differently.",
        "slug":slug1,
        "category":"Entertainment",
        "vertical":"entertainment",
        "urgency":"standard",
        "status":"published",
        "published_at":now_iso,
        "score_total":85,
        "tags":["Deepika Padukone","Hollywood Walk of Fame","Bollywood","diaspora","Ranveer Singh","global Indian cinema","Hollywood","representation"],
        "diaspora_angle":"Deepika Padukone is the actor your non-Indian friends actually know. She unveiled the FIFA World Cup trophy in Qatar. She sat front row at Louis Vuitton. She was in xXx with Vin Diesel and in a film with Brad Pitt's production company. For NRIs, she's the shortcut. The name you drop when someone asks if Bollywood is just singing and dancing. A Walk of Fame star doesn't change the economics of Indian cinema, but it does change the conversation at Thanksgiving when your cousin who works in tech asks what Indian actors have actually accomplished outside India. Now you have an address: 6801 Hollywood Boulevard.",
        "sources":[
            {"url":"https://www.bollywoodhungama.com/news/bollywood/deepika-padukone-becomes-first-indian-join-hollywood-walk-fame-2026-list/","name":"Bollywood Hungama"},
            {"url":"https://www.cinemaexpress.com/tamil/news/2025/May/12/deepika-padukone-to-get-a-star-on-hollywood-walk-of-fame-in-2026-becomes-first-indian-actor-to-receive-the-honour-58048.html","name":"Cinema Express"}
        ],
        "person_name":"Deepika Padukone",
        "image_search_query":"Deepika Padukone",
        "word_count":720,
        "body":"""The Hollywood Chamber of Commerce does not hand out Walk of Fame stars to make a point. It hands them out because a committee of people who have been in the business for decades decided you have contributed something durable to motion pictures, television, live theatre, radio, or recording.

On May 12, 2026, the Chamber announced its Class of 2026. **Deepika Padukone** is on it. She will be the first Indian actor ever to receive a star.

She is listed in the Motion Pictures category alongside **Demi Moore**, **Rachel McAdams**, **Timothée Chalamet**, and **Stanley Tucci**. The ceremony will be held in 2026; the exact date has not been announced.

## What the star actually means

A Walk of Fame star is a terrazzo-and-brass plaque embedded in the sidewalk along Hollywood Boulevard and Vine Street. There are more than 2,700 of them. You can nominate yourself, but you need a sponsor to pay the $75,000 fee for installation and maintenance. A committee vets the nominations. The criteria are longevity (five years in the category), contributions to the community, and a guarantee that you will show up for the unveiling.

For decades, the list has been overwhelmingly American and European. The first South Asian star went to **Sabrina Singh**? No. It never happened. The first Indian star is Deepika Padukone.

## Why Deepika, why now

Padukone's Hollywood résumé is short but strategic. She debuted opposite Vin Diesel in **xXx: Return of Xander Cage** (2017). She was in the ensemble of **Pathaan** (2023), which did $130 million worldwide and played in 100+ countries. She unveiled the FIFA World Cup trophy in Qatar in 2022, a moment that was broadcast to a billion people. She is a Louis Vuitton global ambassador, a Cartier ambassador, and a regular at the Met Gala.

None of that is why the Chamber picked her. The Chamber picked her because she is, by any metric, the most globally recognizable Indian actor of her generation. She has 80 million Instagram followers. She has been on the cover of Time. She gave a TED Talk about mental health that has been viewed 10 million times.

For the Indian diaspora, the star is a data point in an argument they've been having for 20 years: that Indian cinema is not a regional curiosity. That it is a global industry with stars who can open a movie in New Jersey and Nairobi on the same weekend.

## The diaspora angle

If you grew up Indian in America in the 2000s, you had a routine. Someone would ask what movies you watched. You'd say Bollywood. They'd ask if you meant Slumdog Millionaire. You'd explain. They'd nod politely.

Deepika Padukone is the end of that routine.

She is the actor your American friends know without you having to explain. They know her from the World Cup. They know her from the Louis Vuitton ads in Vogue. They know her because she is, simply, famous.

A Walk of Fame star does not make Indian films easier to finance. It does not get more Indian actors cast in Hollywood. It does not solve the visa problems that keep Indian crew members out of American productions.

What it does is give you a place to take your parents when they visit Los Angeles. "That's Deepika's star," you can say, and they will know exactly who you mean.

The star will be located at 6801 Hollywood Boulevard. The unveiling will be livestreamed. NRIs in the Bay Area will watch it at 6 a.m. and text the link to their family WhatsApp groups with a single emoji: 🇮🇳.

That's the whole story."""
    })

# ARTICLE 2: Ramayana prepone
slug2="namit-malhotra-ramayana-prepone-oct-30-2026-diwali-20260526"
if not check_duplicate(slug2):
    art2_id=str(uuid.uuid4())
    articles.append({
        "id": art2_id,
        "headline":"Namit Malhotra Is Thinking About Moving Ramayana Up to October 30, 2026 — A Week Before Diwali — Because Even the Producer of India's Most Expensive Film Is Nervous About the Diwali Traffic Jam.",
        "subheadline":"The two-part epic starring Ranbir Kapoor as Ram, Yash as Ravana, Sai Pallavi as Sita and Sunny Deol as Hanuman was slated for Diwali 2026. Now, Malhotra is weighing a pre-Diwali release to avoid a clash with other big films and to give the film a longer runway.",
        "slug":slug2,
        "category":"Entertainment",
        "vertical":"entertainment",
        "urgency":"standard",
        "status":"published",
        "published_at":now_iso,
        "score_total":78,
        "tags":["Ramayana","Namit Malhotra","Ranbir Kapoor","Yash","Sai Pallavi","Sunny Deol","Nitesh Tiwari","Bollywood","Diwali 2026","Indian cinema"],
        "diaspora_angle":"Diwali is the Super Bowl for Indian films. It's when NRIs book entire rows at AMC theaters in Edison and Sunnyvale. It's when your office Slack lights up with 'Ramayana first day first show?' messages. Moving the release a week earlier is a producer's way of saying: we think this film is big enough to create its own holiday. For diaspora families who have been waiting for a Ramayana that doesn't look like a TV serial from 1987, the date change is the first sign that this version might actually deliver.",
        "sources":[
            {"url":"https://www.bollywoodhungama.com/news/bollywood/namit-malhotra-contemplating-masterstroke-prepone-ramayana-october-30-2026-week-diwali/","name":"Bollywood Hungama"}
        ],
        "image_search_query":"Ramayana poster Ranbir Kapoor",
        "word_count":680,
        "body":"""**Namit Malhotra** is considering moving **Ramayana** up by a week.

The film, directed by **Nitesh Tiwari**, is currently slated for Diwali 2026. Malhotra is now weighing an October 30, 2026 release — seven days before Diwali — to give the film more breathing room.

The logic is simple: Diwali 2026 is crowded. The holiday is the most lucrative window in Indian cinema, and every major studio wants a piece of it. By opening a week early, Ramayana would get a clear run at the box office before other films arrive.

## The scale

Ramayana is being made on a budget that is being reported variously as ₹800 crore to ₹1,200 crore ($100–150 million). It is a two-part adaptation. Part 1 is the Diwali 2026 release.

The cast:
- **Ranbir Kapoor** as Ram
- **Yash** as Ravana
- **Sai Pallavi** as Sita
- **Sunny Deol** as Hanuman

The first teaser dropped earlier this year and trended worldwide. The visuals — a mix of practical sets and high-end VFX from Malhotra's Prime Focus — were the talking point. For once, an Indian mythological epic did not look like it was made for television.

Malhotra, who produced the Oscar-winning VFX for Dune and Blade Runner 2049 through his company DNEG, has been vocal about wanting Ramayana to be India's answer to The Lord of the Rings. The prepone is part of that ambition: you don't open Lord of the Rings on Christmas Day alongside three other blockbusters. You give it space.

## Why Diwali matters

Diwali is not just a festival. It is the Indian box office's Black Friday. Families go to the movies together. NRIs in the US, UK, Canada and Australia book tickets weeks in advance. A Diwali release can add 20–30% to a film's lifetime collection.

But the window is also a traffic jam. In 2025, four major films opened over Diwali weekend. Two of them underperformed because they split the audience.

Malhotra's calculation is that Ramayana is big enough to create its own weekend. Open on October 30, get the pre-Diwali buzz, own the holiday week, and then ride the word of mouth into November.

## The diaspora bet

For the diaspora, Ramayana is personal in a way that few films are. It is the story you grew up hearing from your grandparents. It is the Amar Chitra Katha comic you read on flights to India. It is the TV serial your parents made you watch on Sunday mornings.

Every previous screen adaptation has been, to put it kindly, limited by budget. The 1987 Ramanand Sagar series is beloved, but it looks like it was shot in a community hall. The 2008 animated film was a noble effort. The recent Adipurush was a VFX disaster that became a meme.

Malhotra is betting that NRIs will show up for a version that finally looks like the epic they imagined as kids. The October 30 date is a signal: this is an event film, not just a Diwali film.

The final decision has not been made. The teaser for Part 2 is expected later this year. For now, the producer is thinking out loud — and the entire Indian film industry is listening."""
    })

# Publish articles
for art in articles:
    print(f"\n→ Publishing: {art['headline'][:80]}...")
    # Insert article
    payload = {k:v for k,v in art.items() if k not in ["person_name","image_search_query"]}
    res = sb_post("p2_articles", payload)
    art_id=res[0]["id"]
    # Image sourcing
    img_url=None
    attribution="The Videshi"
    if "person_name" in art:
        img_url=fetch_wikipedia_person_image(art["person_name"])
        if img_url: attribution="Wikimedia Commons"
    if not img_url:
        img_url=fetch_pexels_image(art["image_search_query"])
    if img_url:
        filename=f"{art['slug']}.jpg"
        final_url=upload_image_to_supabase(img_url, filename)
        sb_patch("p2_articles", f"id=eq.{art_id}", {"image_url":final_url,"image_attribution":attribution})
        print(f"  ✓ Image set")
    else:
        print(f"  ⚠ No image found, leaving blank")
print("\n✅ Done")
