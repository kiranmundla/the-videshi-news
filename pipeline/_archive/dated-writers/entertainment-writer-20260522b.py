#!/usr/bin/env python3
"""Entertainment writer — May 22 2026 batch 2 (16:30 PDT):
Karuppu ₹200cr, Dhurandhar Revenge OTT dominance, Star Wars flops in India."""

import json, os, re, uuid, requests, subprocess
from datetime import datetime, timezone
from pathlib import Path

# ── Supabase config ──
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
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
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{filters}", headers={**HEADERS, "Prefer": "return=minimal"}, json=data, timeout=30)
    return r.status_code

def make_slug(headline, date_suffix="20260522"):
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Karuppu — Suriya's First ₹200 Crore Film
# ══════════════════════════════════════════════════════════════

a1_headline = "Suriya Just Got His First ₹200 Crore Film. It Took 29 Years, a Guardian Deity, and a Courtroom — and Tamil Cinema's Diaspora Just Made It Possible."
a1_id = str(uuid.uuid4())

articles.append({
    "id": a1_id,
    "headline": a1_headline,
    "subheadline": "RJ Balaji's 'Karuppu' crossed ₹200 crore worldwide in under a week, becoming the highest-grossing Tamil film of 2026 and Suriya's biggest hit in a 29-year career. The overseas numbers tell a story of Tamil cinema's expanding global footprint.",
    "body": """Suriya has been a star for nearly three decades. He's carried franchises (*Singam*), earned critical praise (*Jai Bhim*), and survived the cyclical cruelty of Tamil cinema's box office, where one Friday can erase a decade of goodwill. What he'd never done, until this week, was deliver a ₹100 crore net film in India. Or a ₹200 crore film worldwide.

*Karuppu* changed that in six days.

RJ Balaji's devotional fantasy — in which Suriya plays a guardian deity who disguises himself as a lawyer to dismantle a corrupt court — crossed ₹200 crore worldwide by Day 7, with ₹131.82 crore India net and ₹57 crore overseas. It became the first Tamil film to breach the ₹100 crore India net mark in nine months, reviving a Kollywood box office that had been clinically quiet since early 2025.

**The Numbers Behind the Deity**

The film opened to 700,000 BookMyShow tickets on Day 1 — the fourth-highest opening for any Tamil film on the platform. The first weekend was relentless: ₹82 crore India net in four days, with Tamil Nadu alone contributing roughly ₹60 crore of the domestic gross. By Day 6, it had overtaken *Singam 2* to become the highest-grossing film of Suriya's career.

But the overseas number — ₹57 crore in a week — deserves separate attention. Tamil cinema's international business has historically been smaller than Hindi or Telugu cinema's diaspora markets. The Gulf, Singapore, and Malaysia have always been reliable, driven by the massive Tamil populations in those regions. What *Karuppu* demonstrated is that the US, UK, and Canadian markets are catching up. The film opened in over 600 screens internationally, with strong showings in the Bay Area, Houston, New Jersey, and London — cities with established but growing Tamil communities.

In Kerala, *Karuppu* set a Suriya record. In the Telugu states, it earned ₹43 crore — an extraordinary crossover number for a Tamil-language film not starring a pan-India name. The combined impact suggests that the audience for *Karuppu* wasn't just Tamil-speaking — it was South Indian in the broadest sense.

**Why a Deity Film Worked**

Indian cinema has a long tradition of devotional films. What made *Karuppu* different is that RJ Balaji — who also wrote and directed — wrapped the devotional premise in a courtroom drama and a corruption investigation. Suriya's deity isn't performing miracles for the faithful. He's filing motions, cross-examining witnesses, and dismantling an institutional rot from within the system. The divine intervention is bureaucratic.

This approach allowed the film to function simultaneously as a mass entertainer (the deity reveal, the action sequences, the Sai Abhyankkar soundtrack) and as a social commentary about India's judicial delays and institutional corruption. It's a trick that RJ Balaji has refined since *LKG* — using genre packaging to smuggle in political critique.

For Suriya, the film also marks a creative recalibration. After *Jai Bhim* positioned him as a serious dramatic actor and *Kanguva* underperformed commercially, *Karuppu* found the middle ground: a performance that required restraint (playing a deity who must conceal his nature) without sacrificing the mass appeal that fills opening-weekend seats.

**The Diaspora Lens**

For the Tamil diaspora, *Karuppu*'s success is validating in a specific way. The film's themes — institutional corruption, divine justice, the idea that the system can be reformed from within — carry particular weight for a community that left India partly because those institutions failed them.

More practically, *Karuppu*'s overseas performance is evidence that the Tamil theatrical market outside India is maturing. A decade ago, a ₹57 crore overseas week would have been unthinkable for a non-Rajinikanth Tamil film. Today, Suriya, Vijay, and an expanding roster of Kollywood stars can open to meaningful numbers in Edison, Fremont, and Harrow. The exhibition infrastructure — screens, distributors, marketing — has caught up with the audience demand.

Tamil cinema's diaspora isn't just watching anymore. It's opening weekends.

*Karuppu* is now playing in Tamil, with dubbed versions in Telugu and Kannada.""",
    "diaspora_angle": "Tamil cinema's overseas market matured this week. Karuppu earned ₹57 crore internationally in 7 days — a Suriya record and a signal that the US/UK/Canada Tamil theatrical market is catching up to Gulf strongholds. For the diaspora, the film's themes of institutional corruption and divine justice resonate personally.",
    "vertical": "entertainment",
    "tags": ["Karuppu", "Suriya", "RJ Balaji", "Tamil cinema", "box office", "Kollywood", "200 crore"],
    "urgency": "high",
    "sources": json.dumps([
        {"url": "https://cinemaexpress.com/suriya-rj-balajis-karuppu-crosses-rs-200-crores-worldwide", "name": "Cinema Express — ₹200 Crore Worldwide"},
        {"url": "https://sacnilk.com/karuppu-box-office-day-8", "name": "Sacnilk — Day 8 Box Office"},
        {"url": "https://koimoi.com/karuppu-box-office-day-6", "name": "Koimoi — First 100 Crore in India"},
        {"url": "https://filmibeat.com/karuppu-box-office-day-5-nears-100-cr", "name": "Filmibeat — Day 5 Collection"},
        {"url": "https://en.wikipedia.org/wiki/Karuppu_(film)", "name": "Wikipedia — Karuppu (film)"}
    ]),
    "slug": make_slug("suriya-karuppu-200-crore-tamil-cinema-diaspora"),
    "word_count": 780,
    "status": "published",
    "is_featured": False,
    "category": "entertainment",
    "published_at": now,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
    "score_total": 85
})


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Dhurandhar Revenge OTT + Album Historic Numbers
# ══════════════════════════════════════════════════════════════

a2_headline = "The Dhurandhar Franchise Is Now Worth ₹1,800 Crore. Its Sequel Just Hit #5 on Netflix Globally — Without Even Streaming in India."
a2_id = str(uuid.uuid4())

articles.append({
    "id": a2_id,
    "headline": a2_headline,
    "subheadline": "Dhurandhar: The Revenge earned 1.8 million views in its first Netflix weekend outside India, while the franchise's album debuted at #5 on the US Top Albums chart. For NRIs who helped build these numbers, the spy universe is a cultural export on a scale Bollywood hasn't seen since the 2000s.",
    "body": """The numbers for the Dhurandhar franchise have reached a point where they require a moment of calibration. So here it is: *Dhurandhar: The Revenge* — Aditya Dhar's spy sequel starring Ranveer Singh — has grossed ₹1,799 crore worldwide in nine weeks of theatrical release. That makes it the second highest-grossing Indian film of all time globally. The first Dhurandhar crossed ₹1,300 crore. Combined, the franchise is worth over ₹3,000 crore at the theatrical box office alone.

And now it's conquering streaming without even being available in its home market.

**The Netflix Paradox**

In its debut week on Netflix (May 11–17), *Dhurandhar: The Revenge — Raw & Undekha* landed at #5 on the platform's Global Top 10 for Non-English Movies, earning 1.8 million views and 6.8 million hours viewed. It hit #1 in nine countries and appeared in the Top 10 across 17 nations — spanning Europe, Africa, and Oceania.

The paradox: the sequel is not streaming in India. Netflix holds international digital rights only. The Indian OTT premiere is scheduled for June 4 on JioHotstar (which holds domestic digital rights), with Netflix getting Indian access at a later date. So the 1.8 million views represent purely international audiences — diasporic and non-Indian viewers who chose a three-hour-fifty-two-minute Hindi spy epic over everything else on the platform.

For context, the film that topped the same chart — *My Dearest Assassin* — had 6.2 million views. Dhurandhar 2, released weeks after its theatrical run in most international markets, still captured a fifth of that leading film's viewership despite the majority of its core audience having already seen it in cinemas.

**The Album That Broke Spotify**

The streaming dominance extends beyond video. The *Dhurandhar: The Revenge* soundtrack, composed by National Award-winner Shashwat Sachdev, debuted at #2 on Spotify's Global Top Albums chart and #5 on the US Top Albums chart — with all 11 tracks charting simultaneously on the Spotify Global Top 200.

The lead single — *Aari Aari* — is the most culturally loaded track on the album. It features Bombay Rockers, the Danish-Indian duo whose 2003 original *Ari Ari* defined an era of Indipop for a generation of diaspora kids. Lead vocalist Navtej Singh Rehal reprises the iconic Punjabi chant alongside Jasmine Sandlas, Khan Saab, and rappers Reble and Token. The remix is doing what the best Bollywood music has always done for NRIs: connecting a childhood memory to a current cultural moment.

The album's American chart performance is unprecedented for an Indian film soundtrack. Bollywood albums have charted internationally before — *RRR* and *Pathaan* had moments — but no Indian film has placed an entire album in the US Top 5 with every track simultaneously on the global charts. The Dhurandhar franchise is operating at a scale that the Indian film industry hasn't seen since the early 2000s, when Bollywood was a curiosity in the West rather than a commercial force.

**What ₹1,800 Crore Means**

At ₹1,799 crore worldwide, *Dhurandhar: The Revenge* sits behind only *Baahubali 2* in the all-time Indian box office. It has outpaced the original Dhurandhar (which itself held records), outrun *Pushpa 2* and *Stree 2*, and survived nine weeks in theatres — outlasting every modern Bollywood blockbuster's theatrical window.

The overseas contribution of ₹427 crore tells the diaspora story in hard numbers. In North America alone, the film became the highest-grossing Indian film ever, surpassing *Baahubali 2*'s decade-long record. Texas led advance bookings. The tri-state area, Bay Area, and Houston rounded out the top markets — the same cities where NRI audiences have been building India's parallel box office for years.

**The Export Economy of Desi Cinema**

For the Indian diaspora, the Dhurandhar phenomenon is bigger than one franchise. It's proof of concept that Indian cinema can function as a global entertainment export — not as art-house fare that plays at festivals, but as mass commercial product that competes on Netflix charts and Billboard rankings.

The question the industry is now asking is whether the spy universe is an outlier or a template. Can other Hindi franchises replicate this scale? Can Tamil and Telugu cinema — which already have strong diaspora markets — build their own ₹1,000 crore global franchises?

For now, the answer is being written in streaming data and Billboard entries. And the audience writing it is, increasingly, watching from abroad.

*Dhurandhar: The Revenge* streams internationally on Netflix. Indian OTT premiere on JioHotstar is scheduled for June 4.""",
    "diaspora_angle": "The diaspora built this franchise. ₹427 crore overseas, the highest-grossing Indian film in North American history, a US Top 5 album, and 1.8 million Netflix views from outside India. For NRIs, Dhurandhar represents Bollywood functioning as a genuine global cultural export.",
    "vertical": "entertainment",
    "tags": ["Dhurandhar", "Ranveer Singh", "Netflix", "box office", "Bollywood", "Bombay Rockers", "Aari Aari", "Spotify", "OTT"],
    "urgency": "high",
    "sources": json.dumps([
        {"url": "https://sacnilk.com/dhurandhar-2-the-revenge-week-9-box-office", "name": "Sacnilk — Week 9 Box Office"},
        {"url": "https://sacnilk.com/dhurandhar-the-revenge-ott-views-sequel-1-8m-views", "name": "Sacnilk — Netflix 1.8M Views"},
        {"url": "https://sacnilk.com/dhurandhar-the-revenge-aari-aari-song", "name": "Sacnilk — Aari Aari Song Release"},
        {"url": "https://sacnilk.com/dhurandhar-2-beats-baahubali-2-north-america", "name": "Sacnilk — North America Record"},
        {"url": "https://bollywoodhungama.com/kartavya-takes-over-netflix", "name": "Bollywood Hungama — Netflix India Charts"}
    ]),
    "slug": make_slug("dhurandhar-revenge-1800-crore-netflix-global-billboard"),
    "word_count": 800,
    "status": "published",
    "is_featured": False,
    "category": "entertainment",
    "published_at": now,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
    "score_total": 87
})


# ══════════════════════════════════════════════════════════════
# ARTICLE 3: Star Wars Opens in India to ₹0.70 Crore
# ══════════════════════════════════════════════════════════════

a3_headline = "Star Wars Just Opened in India to ₹0.70 Crore. On the Same Day, Drishyam 3 Earned Twenty Times That. Hollywood Has an India Problem."
a3_id = str(uuid.uuid4())

articles.append({
    "id": a3_id,
    "headline": a3_headline,
    "subheadline": "The Mandalorian and Grogu managed 7% theatre occupancy on its opening day in India — while Mohanlal's Malayalam thriller packed houses at 64%. For the Indian audience in America, these numbers tell two different stories about the movies they watch.",
    "body": """*Star Wars: The Mandalorian and Grogu* — the franchise's first theatrical release in seven years, directed by Jon Favreau, projected to earn $85–115 million over Memorial Day weekend in North America — opened in India on Friday to ₹0.70 crore.

Seven-tenths of a crore. About $82,000.

On the same day, *Drishyam 3* — Mohanlal's Malayalam thriller playing in its second day — earned ₹11.05 crore. *Karuppu* continued its march past ₹130 crore in its second week. Even *Chand Mera Dil*, Karan Johar's modest romance, had a better opening day in absolute terms.

The Mandalorian and Grogu's Indian occupancy stood at 7.2%. The English version managed 10% in select metros; the Hindi dub came in at 5%. Drishyam 3, by comparison, ran at 64.92% occupancy in evening shows.

**The Structural Disconnect**

This isn't a story about one bad opening. It's the continuation of a pattern that has been accelerating since the pandemic: Hollywood's commercial relevance in India is collapsing outside of the Marvel and Avatar franchises, and even Marvel's grip is weakening.

The reasons are both cultural and industrial. Indian cinema — across Hindi, Tamil, Telugu, Malayalam, and Kannada — is producing more expensive, more technically polished, and more narratively ambitious films than it was five years ago. The production gap that once made Hollywood feel like a premium product has narrowed to the point where an average Tollywood VFX spectacle looks no worse (and sometimes better) than a mid-tier Hollywood franchise entry.

More fundamentally, Indian audiences don't have a generational relationship with Star Wars. The franchise's cultural DNA — the hero's journey filtered through American postwar mythology, the Cold War allegory of Empire vs. Rebellion — doesn't carry the same emotional weight in a market where the equivalent mythological archetypes are Ramayana and Mahabharata. Suriya literally plays a deity fighting corruption in *Karuppu*. That is India's Star Wars.

**The Diaspora Split**

For Indians in the United States, the picture is more complicated. Many NRIs consume both ecosystems — catching *The Mandalorian and Grogu* at the AMC on Friday evening and streaming *Drishyam 3* from BookMyShow Stream on Saturday. The American theatrical market, where the Star Wars film is projected to earn $90–100 million domestically, doesn't have the same structural problem.

But the Indian box office data reveals something about where cultural gravity is shifting. A decade ago, a new Star Wars film would have been a modest event in India — perhaps ₹5–8 crore on opening day, with strong metro play. Today, it can't buy attention at any price. The ₹0.70 crore opening represents not just indifference but active rejection: Indian audiences chose not to see Star Wars when it was sitting right next to Drishyam 3 on the multiplex screen.

This has downstream consequences for how Hollywood studios think about India. Disney has been investing in localized marketing, Hindi dubbing, and premium format releases (IMAX, 4DX) for Star Wars in India. If the market response is ₹0.70 crore, the return on that investment is effectively zero — and the next Star Wars film may not receive even this level of Indian promotional support.

**What It Means for Indian Exhibition**

The multiplex chains — PVR INOX, Cinepolis — have been quietly rebalancing their screen allocations over the past two years. Hollywood titles that once commanded 40–50% of screens on opening weekend are increasingly being compressed to 25–30%, with the freed-up screens going to regional-language films that deliver better per-screen averages.

*The Mandalorian and Grogu* will be fine globally. Its Memorial Day weekend will likely clear $100 million in North America. But India — the world's largest film market by ticket sales — has sent a clear message: the franchise that once defined global cinema doesn't even register as competition anymore.

On Friday, the competition was Mohanlal, Suriya, and Karan Johar. Star Wars didn't even qualify for the undercard.

*Star Wars: The Mandalorian and Grogu* is in theatres in English, Hindi, and Tamil.""",
    "diaspora_angle": "NRIs consume both Hollywood and Indian cinema — but the India box office reveals a cultural gravity shift. Star Wars can't compete with Drishyam 3 or Karuppu in their home market. For the diaspora watching both in American theatres, the two ecosystems that define their cultural consumption are diverging.",
    "vertical": "entertainment",
    "tags": ["Star Wars", "Mandalorian", "Drishyam 3", "Hollywood", "India box office", "Karuppu", "multiplex"],
    "urgency": "standard",
    "sources": json.dumps([
        {"url": "https://sacnilk.com/star-wars-mandalorian-grogu-box-office-day-1-india", "name": "Sacnilk — Mandalorian India Day 1"},
        {"url": "https://boxofficepro.com/mandalorian-grogu-memorial-day-weekend", "name": "Box Office Pro — Weekend Preview"},
        {"url": "https://filmibeat.com/drishyam-3-day-2-box-office", "name": "Filmibeat — Drishyam 3 Day 2"},
        {"url": "https://screenrant.com/mandalorian-grogu-cost-box-office-success", "name": "Screen Rant — Budget Analysis"}
    ]),
    "slug": make_slug("star-wars-india-70-lakh-drishyam-3-hollywood-problem"),
    "word_count": 750,
    "status": "published",
    "is_featured": False,
    "category": "entertainment",
    "published_at": now,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
    "score_total": 82
})


# ══════════════════════════════════════════════════════════════
# INSERT ALL ARTICLES
# ══════════════════════════════════════════════════════════════

print(f"Publishing {len(articles)} entertainment articles...")
success = 0
for article in articles:
    try:
        result = sb_post("p2_articles", article)
        if isinstance(result, (list, dict)):
            print(f"  ✅ {article['headline'][:80]}...")
            success += 1
        else:
            print(f"  ⚠️  Unexpected response: {json.dumps(result)[:200]}")
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ Error: {e}")
        print(f"     Response: {e.response.text[:300]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print(f"\nDone: {success}/{len(articles)} articles published.")
