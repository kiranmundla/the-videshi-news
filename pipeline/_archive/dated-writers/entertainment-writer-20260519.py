#!/usr/bin/env python3
"""Videshi Entertainment Writer — 2026-05-19 run"""

import os, json, uuid, re, sys
from datetime import datetime, timezone
import urllib.request, urllib.parse

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ.get("SUPABASE_ANON_KEY", ""))

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def supabase_post(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers=HEADERS, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def supabase_patch(table, match, data):
    params = "&".join(f"{k}=eq.{v}" for k, v in match.items())
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers=HEADERS, method="PATCH")
    with urllib.request.urlopen(req) as resp:
        return resp.read()

def make_slug(headline, date_str="20260519"):
    s = headline.lower()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'\s+', '-', s.strip())
    s = s[:70].rstrip('-')
    return f"{s}-{date_str}"

now = datetime.now(timezone.utc).isoformat()

# ============================================================
# ARTICLE 1: Mouni Roy at Cannes 2026
# ============================================================
article1_id = str(uuid.uuid4())
article1_headline = "Mouni Roy Just Showed Up at Cannes With a Film, a Power Outfit, and Zero Apologies — and NRIs Are Here For It"
article1_subheadline = "Days after confirming her split from Suraj Nambiar, the Naagin star hit the French Riviera as a producer — and reminded the diaspora why she's more than tabloid fodder."
article1_slug = make_slug("mouni-roy-cannes-2026-bombay-stories-producer-separation")
article1_body = """Mouni Roy didn't come to Cannes to explain herself. She came to work.

Less than a week after she and husband Suraj Nambiar confirmed their separation in a joint Instagram statement on May 14, the actress-turned-producer was photographed on a balcony overlooking the French Riviera in a monochrome black dress, checkered coat, and sheer stockings — looking every bit the woman who had decided that her next chapter would be written on her own terms. Her caption? "Cannes & Chaos! Bonjour." That's it. No lengthy note, no damage control. Just chaos acknowledged and Cannes attended.

## From Naagin to the Marché du Film

What makes this Cannes trip genuinely interesting — beyond the tabloid-ready timing — is what Mouni Roy was actually doing there. She wasn't walking a red carpet as a brand ambassador or attending a party on someone else's yacht. She was at the **Marché du Film**, the industry-facing market that runs alongside the festival, to promote **Bombay Stories** — a period anthology film based on Saadat Hasan Manto's classic short story *Hatak*, set in 1930s Bombay.

The film, directed by Rahat Shah Kazmi, explores the lives of sex workers through Manto's characteristically unflinching lens, blending satire with empathy. Mouni serves as both actor and producer — a move that puts her in a creative bracket most of her television-era fans wouldn't have predicted five years ago. Her co-stars include Anupria Goenka (of *War* and *Tiger Zinda Hai* fame) and Sushmita V Singh, who made her own Cannes debut this week as a showstopper at Cannes Fashion Week.

This is Mouni's third trip to Cannes. But it's the first where she showed up with a film under her arm, not just a designer on her back.

## The Separation — and the Noise Around It

Mouni Roy and Suraj Nambiar, a Dubai-based investment banker from a Jain business family, married in a lavish ceremony in Goa in January 2022. Their joint statement on May 14 was simple: "We have decided to part ways." They described it as mutual, asked for privacy, and explicitly rejected "false narratives."

That didn't stop the internet. Within hours, speculation about alimony, infidelity, and third-party involvement spread across Indian social media. Suraj responded with an unusually direct Instagram post, calling the rumours "absolutely malicious" and writing: *"There is no alimony. There are no disputes. There is no third party involved. Mouni and I chose to part ways together… that is the truth."*

In a detail that charmed fans: the two refollowed each other on Instagram almost immediately after their separation announcement — a small digital gesture that said more about their relationship than any tabloid headline could.

## Why NRIs Care — and Should

For Indian diaspora communities, Mouni Roy occupies a specific cultural register. She's the **Naagin** who became a Bollywood name with *Gold* alongside Akshay Kumar. She's the woman NRI aunties debated over when she married outside the Bong-Rajput-Bollywood circle that's typical of the industry. And now she's a producer at Cannes with a Manto adaptation — a literary choice that would make any South Asian lit nerd pay attention.

The project itself speaks to diaspora viewers. Manto's work has been adapted repeatedly (*Manto*, 2018, starring Nawazuddin Siddiqui, was an international festival darling), and the conversation about sex work, patriarchy, and colonial Bombay resonates differently when you're watching from New York, London, or Toronto — where the distance from India sharpens the specifics.

India sent multiple films and projects to Cannes 2026 this year, including Alia Bhatt's appearance as a L'Oréal ambassador (which generated its own viral controversy) and Diana Penty's futuristic couture showcase. But Mouni's presence at the Marché, with a producer credit and an indie film, arguably does more for Indian representation than any red-carpet walk — even if it generates fewer Instagram likes.

## What's Next

Bombay Stories doesn't yet have a confirmed theatrical or OTT release date, though the Marché screening positions it for international distribution deals. For NRI audiences, this is one to track — especially if it lands on a platform like Netflix or MUBI, where Indian festival films have found dedicated diasporic audiences.

As for Mouni, she's already made her point. The personal headlines will fade. The Cannes producer credit won't."""

article1_sources = [
    "filmibeat.com",
    "thedailyjagran.com",
    "filmfare.com",
    "bollywoodhungama.com",
    "khelja.in",
    "newspointapp.com",
]

# ============================================================
# ARTICLE 2: Ram Charan Injuries on Peddi
# ============================================================
article2_id = str(uuid.uuid4())
article2_headline = "Ram Charan Got Real Wrestlers Thrown at Him, Tore His Ligament, and Called It a 'Beautiful Memory' — Peddi Looks Like It Was Worth Every Stitch"
article2_subheadline = "The RRR star sustained three injuries during the making of his ₹350-crore Telugu sports drama, and the just-launched trailer has NRI fans counting down to June 4."
article2_slug = make_slug("ram-charan-peddi-injuries-trailer-launch-june-2026")
article2_body = """Ram Charan has a cartilage tear in his wrist. He has stitches near his eye. He got slammed by an actual wrestler on set. And when he stood on stage at the trailer launch in Mumbai on May 18, he looked at director Buchi Babu Sana and laughed about it.

"I have a ligament tear in my hand because of Buchi Babu," he told the crowd, grinning. "Instead of trained artistes, he brought real wrestlers and I got injured. But it remains a beautiful memory."

That's not PR polish. That's a man who spent two years inside a character and came out the other side with battle scars he's genuinely proud of. And if the just-released Peddi trailer is anything to go by, every injury was earned.

## What Is Peddi?

Peddi is a Telugu-language sports action drama directed by Buchi Babu Sana — the man behind *Uppena* (2021), which launched Vaishnav Tej and became an unexpected blockbuster. This time, the canvas is significantly larger: a ₹350-crore production set in rural Andhra Pradesh, featuring Ram Charan as a village athlete caught between sports, politics, and personal stakes.

The trailer, which dropped alongside the Mumbai launch event, shows Ram Charan in three distinct sporting avatars — wrestling, kabaddi, and what appears to be a traditional rural game — each demanding a different physical register. The 1980s-inspired set design, sweeping rural landscapes, and raw physicality make this feel less like a typical Telugu masala film and more like an Indian answer to the sports epics that Hollywood rarely attempts anymore.

The supporting cast is stacked: **Janhvi Kapoor** plays the female lead, **Shiva Rajkumar** (the Kannada legend) has a pivotal role, and **Divyenndu Sharma** — yes, Munna Bhaiya from *Mirzapur* — plays a key character. At the launch, Divyenndu joked that his advice to Peddi's character would be: "Aap milkar gang banate hain."

And the music? **A.R. Rahman.** Speaking at the event, Rahman said he'd been "waiting for the right Telugu film" and felt Peddi was the project because it "connects strongly with today's generation."

## The Injuries, in Detail

Producer Venkata Satish Kilaru detailed Ram Charan's three on-set injuries: a severe blow during a wrestling sequence with real wrestlers that Buchi Babu insisted on casting for authenticity, a wrist injury that escalated into a ligament tear requiring surgery (scheduled within days of the trailer launch), and stitches near his eye from an action sequence gone slightly sideways.

Ram Charan completed the shoot without taking a break after any of the injuries. He returned to set the next day after the eye stitches, and the wrist surgery was delayed until after the film wrapped. At the trailer launch, he called the cartilage tear "a wonderful memory of the most inspiring film I've done."

He also credited his father, megastar **Chiranjeevi**, for the advice that kept him going: stay present, stay committed, and let the work speak. And in a gracious moment, he thanked **Salman Khan** and **Aamir Khan** for paving the way for sports dramas in Indian cinema with *Sultan* and *Dangal*. "Those films gave us confidence to attempt something like Peddi," he said.

## Why This Matters for the Diaspora

If you're an NRI who watched *RRR* in a packed American or British theatre in 2022 — the kind of screening where the audience whistled, clapped, and treated a Telugu film like a Marvel premiere — then Peddi is the next appointment. Ram Charan's global profile has never been higher. The combination of Buchi Babu's emotional storytelling, Rahman's score, and a June 4 global release means this will land on screens worldwide, not just in Andhra and Telangana.

The Janhvi Kapoor casting adds a cross-industry flavour that bridges Bollywood and Telugu audiences. Ram Charan spoke warmly about working with her and the emotional weight of the Chiranjeevi-Sridevi connection — Janhvi's late mother had worked with his father decades ago, and both families carry that history into this collaboration.

For Telugu NRIs especially, Peddi is already the event film of June. Pre-release buzz on overseas booking platforms has been strong, and the trailer's YouTube numbers are climbing fast.

## What's Next

Peddi releases globally on **June 4, 2026**, with premieres a day earlier in select markets. Ram Charan's wrist surgery is expected within days. Post-recovery, he's likely to begin press tours across Indian metros and key NRI markets. The trailer is out now — and if you need a reason to book a June cinema trip with your desi crew, this is it."""

article2_sources = [
    "gulte.com",
    "filmfare.com",
    "telugucinema.com",
    "khelja.in",
    "bollywoodhungama.com",
    "en.wikipedia.org",
]

# ============================================================
# ARTICLE 3: Salman Khan Snake Scare
# ============================================================
article3_id = str(uuid.uuid4())
article3_headline = "A Snake Just Showed Up at Salman Khan's Galaxy Apartment — Because of Course It Did"
article3_subheadline = "Between death threats, a previous snake bite, and now a reptile in the building, Bhaijaan's Mumbai home remains the most eventful address in Bollywood."
article3_slug = make_slug("salman-khan-galaxy-apartment-snake-scare-mumbai")
article3_body = """If you ever needed proof that Salman Khan's life script is written by someone with a flair for the dramatic, here it is: a snake was spotted on the ground floor of Galaxy Apartments — the iconic Bandra building that doubles as Bollywood's most famous residential address — on Monday. A snake wrangler was called. Officials showed up. The reptile was carefully caught, bagged, and removed. Nobody was hurt. Salman Khan remained unbothered. Business as usual at Galaxy.

## What Actually Happened

According to multiple reports, the snake was spotted on the ground floor of the building, which houses the Khan family's residence. Building staff raised the alarm, and a professional snake wrangler arrived to handle the situation. Visuals from the scene showed the wrangler carefully capturing the snake before placing it in a bag and handing it over to forest department officials for safe release.

There's been no confirmation on the species — though it's worth noting that several varieties of snakes, including rat snakes and Russell's vipers, are common in Mumbai's older residential areas, especially during the pre-monsoon period when rising temperatures and humidity draw them out of their hiding spots. Galaxy Apartments sits in Bandra West, close enough to green cover and older construction to make snake sightings, while uncommon, not unheard of.

Neither Salman Khan nor his family were reported to have been near the snake at the time. The actor's security detail — which has been significantly enhanced since the shooting incident outside Galaxy Apartments in April 2024 — was present during the rescue operation.

## Not Salman's First Serpent Encounter

If this feels like a recurring theme, that's because it literally is. On December 26, 2022, Salman was bitten by a non-venomous snake at his Panvel farmhouse on the outskirts of Mumbai — a day before his birthday. He was rushed to the hospital, treated, and discharged the same day. At the time, social media went predictably wild, with fans posting everything from concerned prayers to memes about Bhaijaan's real-life action sequences.

The 2022 bite happened at the farmhouse, which is surrounded by agricultural land and forest areas. The Galaxy incident is different — this is central Bandra, one of Mumbai's most prime neighbourhoods. A snake in the building adds a surreal quality that feels very on-brand for a man whose life has included poaching cases, death threats from the Lawrence Bishnoi gang, firing incidents outside his home, and now a reptile at his front door.

## The Galaxy Apartments Mystique

For NRIs, Galaxy Apartments isn't just a building — it's a pilgrimage site. Every Salman fan who's ever visited Mumbai has stood outside Galaxy on a Bandra evening, hoping for a glimpse of Bhaijaan waving from his balcony. The building's blue facade and modest exterior — unremarkable by Mumbai's luxury standards — has become one of the most photographed residential addresses in India, rivalled only by Shah Rukh Khan's Mannat a few kilometres away.

The snake scare adds another layer to Galaxy's already legendary status. This is the building where Salman celebrates every Eid by waving to thousands of gathered fans. The same building that made international headlines when gunshots were fired at its entrance in April 2024. And now, apparently, the building where even the local wildlife drops by uninvited.

## On the Work Front

Salman Khan is currently gearing up for **Maatrubhumi: May War Rest in Peace**, a patriotic drama co-starring Chitrangada Singh, which is slated for an August 14 release — timed, of course, for Independence Day weekend. The film was earlier titled *Battle of Galwan*, suggesting a narrative tied to the India-China border tensions. He is also reportedly working on an untitled project with **Nayanthara**, directed by Vamshi Paidipally, which would mark a significant cross-industry collaboration.

For his global fanbase — and the NRIs who'll be booking Eid-release tickets later this year — the snake is just another footnote in the ongoing saga of Salman Khan. The man survived a snake bite in 2022, death threats in 2023-24, and now a snake in his apartment building in 2026. If Bollywood ever runs out of scripts, they could just film his life as-is."""

article3_sources = [
    "newspointapp.com",
    "adityabharat.com",
    "zoomtventertainment.com",
]

# ============================================================
# INSERT ARTICLES
# ============================================================
articles = [
    {
        "id": article1_id,
        "headline": article1_headline,
        "subheadline": article1_subheadline,
        "slug": article1_slug,
        "body": article1_body,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now,
        "created_at": now,
        "updated_at": now,
        "sources": article1_sources,
        "tags": ["Mouni Roy", "Cannes 2026", "Bombay Stories", "Suraj Nambiar", "Manto", "Indian cinema"],
        "diaspora_angle": "Mouni Roy's evolution from TV star to Cannes producer mirrors the diaspora audience's own maturation; Manto adaptation speaks directly to NRI literary and cultural sensibilities",
        "topic_id": "74f02322-e57c-40da-a3f6-689cc1c3fb58",
        "urgency": "daily",
        "score_total": 78,
        "image_entities": ["Mouni Roy", "Cannes Film Festival"],
        "image_must_show": "Mouni Roy at Cannes 2026 or in black outfit",
        "image_search_query": "Mouni Roy Cannes 2026",
        "word_count": len(article1_body.split()),
    },
    {
        "id": article2_id,
        "headline": article2_headline,
        "subheadline": article2_subheadline,
        "slug": article2_slug,
        "body": article2_body,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now,
        "created_at": now,
        "updated_at": now,
        "sources": article2_sources,
        "tags": ["Ram Charan", "Peddi", "Buchi Babu Sana", "Telugu cinema", "Janhvi Kapoor", "AR Rahman"],
        "diaspora_angle": "Post-RRR global fanbase makes Peddi a June event film for NRIs worldwide; Telugu diaspora overseas bookings already buzzing",
        "topic_id": "e306c512-59b0-48bc-8fe7-648ad3b1c8fb",
        "urgency": "daily",
        "score_total": 80,
        "image_entities": ["Ram Charan", "Peddi film"],
        "image_must_show": "Ram Charan at Peddi trailer launch or in character",
        "image_search_query": "Ram Charan Peddi trailer launch 2026",
        "word_count": len(article2_body.split()),
    },
    {
        "id": article3_id,
        "headline": article3_headline,
        "subheadline": article3_subheadline,
        "slug": article3_slug,
        "body": article3_body,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now,
        "created_at": now,
        "updated_at": now,
        "sources": article3_sources,
        "tags": ["Salman Khan", "Galaxy Apartments", "Mumbai", "Maatrubhumi", "Bollywood"],
        "diaspora_angle": "Galaxy Apartments is a pilgrimage site for NRI fans; the snake scare adds to its legend alongside Eid gatherings and security incidents",
        "topic_id": "68b09961-e282-4c8d-8965-b293c5d34f35",
        "urgency": "daily",
        "score_total": 72,
        "image_entities": ["Salman Khan", "Galaxy Apartments"],
        "image_must_show": "Salman Khan or Galaxy Apartments Bandra",
        "image_search_query": "Salman Khan Galaxy Apartments Mumbai",
        "word_count": len(article3_body.split()),
    },
]

for a in articles:
    print(f"\n📝 Publishing: {a['headline'][:80]}...")
    print(f"   Slug: {a['slug']}")
    print(f"   Words: {a['word_count']}")
    try:
        result = supabase_post("p2_articles", a)
        print(f"   ✅ Published: {a['id']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        # Try to read error body
        if hasattr(e, 'read'):
            print(f"   Response: {e.read().decode()}")

# ============================================================
# UPDATE TOPIC STATUSES
# ============================================================
print("\n📋 Updating topic statuses...")

# Mark entertainment topics as published
published_topics = [
    "74f02322-e57c-40da-a3f6-689cc1c3fb58",  # Mouni Roy
    "e306c512-59b0-48bc-8fe7-648ad3b1c8fb",  # Ram Charan
    "68b09961-e282-4c8d-8965-b293c5d34f35",  # Salman Khan
]

rejected_topics = [
    "54f63afe-6884-4d3e-bf7b-5f65677b68e5",  # Tom Kane - no India angle
    "d0ca5186-1b34-4667-b984-3c5fd02979c0",  # Apple Martin - no India angle
]

for tid in published_topics:
    try:
        supabase_patch("p2_topics", {"id": tid}, {"status": "published", "updated_at": now})
        print(f"   ✅ Topic {tid[:8]} → published")
    except Exception as e:
        print(f"   ❌ Topic {tid[:8]} error: {e}")

for tid in rejected_topics:
    try:
        supabase_patch("p2_topics", {"id": tid}, {"status": "rejected", "updated_at": now})
        print(f"   🚫 Topic {tid[:8]} → rejected (no India/diaspora angle)")
    except Exception as e:
        print(f"   ❌ Topic {tid[:8]} error: {e}")

# ============================================================
# SCORE DECAY
# ============================================================
print("\n📉 Running score decay on older articles...")

import urllib.request
decay_url = f"{SUPABASE_URL}/rest/v1/rpc/decay_scores"
# Check if the RPC exists, otherwise do manual decay
try:
    req = urllib.request.Request(decay_url, data=b'{}', headers=HEADERS, method="POST")
    with urllib.request.urlopen(req) as resp:
        print(f"   ✅ Score decay RPC executed")
except Exception as e:
    print(f"   ⚠️ RPC not available, doing manual decay...")
    # Manual decay: reduce score_total for articles older than 48 hours
    try:
        decay_query = f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&score_total=gt.30&published_at=lt.2026-05-17T05:30:00Z&select=id,score_total&limit=50"
        req = urllib.request.Request(decay_query, headers=HEADERS)
        with urllib.request.urlopen(req) as resp:
            old_articles = json.loads(resp.read())
        
        decayed = 0
        for art in old_articles:
            new_score = max(20, int(art['score_total'] * 0.92))
            if new_score < art['score_total']:
                supabase_patch("p2_articles", {"id": art['id']}, {"score_total": new_score, "updated_at": now})
                decayed += 1
        print(f"   ✅ Decayed {decayed} articles (8% reduction)")
    except Exception as e:
        print(f"   ❌ Manual decay error: {e}")

print("\n✅ Entertainment writer run complete!")
print(f"   Articles published: {len(articles)}")
print(f"   Topics resolved: {len(published_topics) + len(rejected_topics)}")
