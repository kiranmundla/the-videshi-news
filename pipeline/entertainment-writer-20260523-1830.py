#!/usr/bin/env python3
"""Entertainment writer — May 23 2026, 18:30 PDT batch:
1. Mirzapur: The Film wraps shooting, going theatrical — OTT to cinema crossover
2. Akshay Kumar + Vidya Balan reunite for Sankranthiki Vasthunam Hindi remake
3. Score decay for old entertainment articles
"""

import json, os, uuid, requests
from datetime import datetime, timezone, timedelta
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

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Mirzapur: The Film wraps shooting — OTT to cinema
# ══════════════════════════════════════════════════════════════

a1_id = str(uuid.uuid4())

articles.append({
    "id": a1_id,
    "headline": "Mirzapur Is Going to Theaters. The Web Series That Taught India How to Binge Is Now a Film — and It Just Wrapped Shooting.",
    "subheadline": "Excel Entertainment has completed principal photography on Mirzapur: The Film, turning Amazon Prime Video's most-watched Indian series into a full theatrical release. For the NRI audience that made 'Kaleen Bhaiya' a global meme, this is the endgame.",
    "slug": "mirzapur-film-wraps-shooting-theatrical-release-pankaj-tripathi-ali-fazal-20260523",
    "category": "Entertainment",
    "vertical": "entertainment",
    "urgency": "standard",
    "status": "published",
    "published_at": now,
    "score_total": 80,
    "tags": ["Mirzapur", "Pankaj Tripathi", "Ali Fazal", "Shweta Tripathi", "Divyendu Sharma", "Excel Entertainment", "Farhan Akhtar", "Ritesh Sidhwani", "Amazon Prime Video", "OTT", "theatrical", "web series to film"],
    "diaspora_angle": "Mirzapur was, for many NRIs, the gateway drug to Indian OTT. It arrived at a time when the diaspora was starved for Indian content that wasn't melodramatic soap opera or three-hour Bollywood romance — gritty, violent, morally ambiguous, bingeable. The series became a communal viewing event in NRI households: Kaleen Bhaiya memes circulated in WhatsApp groups from New Jersey to Southall, 'Guddu Pandit' became a Diwali party costume, and Mirzapur watch parties replaced Sunday cricket screenings for an entire generation of 20-something Indians abroad. Now that same IP is going theatrical — which means diaspora audiences will have to coordinate with India's release schedule rather than streaming on their own time. The theatrical pivot is a bet that Mirzapur's fandom is large enough to fill cinemas in the US, UK, and Gulf — markets where Indian OTT originals have never been tested theatrically. If it works, it rewrites the playbook for how Indian streaming content reaches the diaspora.",
    "sources": [
        {"url": "https://www.sacnilk.com", "name": "Sacnilk"},
        {"url": "https://www.filmibeat.com", "name": "Filmibeat"},
        {"url": "https://district.in", "name": "District"},
        {"url": "https://trends.glance.com", "name": "Glance"}
    ],
    "image_search_query": "Mirzapur film 2026 Pankaj Tripathi Ali Fazal theatrical release",
    "word_count": 920,
    "body": """There is a particular category of Indian entertainment that the diaspora discovered during the pandemic and never let go of. Sacred Games was the first. Family Man was the second. But Mirzapur was the one that stuck — the show NRIs quoted at house parties, memed in group chats, and recommended to their non-Indian friends as proof that Indian storytelling could be genuinely great.

Now that show is becoming a film. And it just finished shooting.

## From Binge to Big Screen

Excel Entertainment — the production house founded by Farhan Akhtar and Ritesh Sidhwani — has completed principal photography on *Mirzapur: The Film*, the theatrical extension of the Amazon Prime Video crime saga that has run for three seasons since 2018. Directed by Gurmmeet Singh, who helmed earlier seasons of the series, the film features the core cast that made the show a cultural phenomenon: Pankaj Tripathi as Kaleen Bhaiya, Ali Fazal as Guddu Pandit, Shweta Tripathi as Golu, and Divyendu Sharma as the volatile Munna Bhaiya.

The film is set for a 2026 theatrical release, though an exact date has not been confirmed. What we know is that it will expand the series' narrative for a cinematic experience — which likely means a standalone story accessible to new audiences rather than a direct continuation that requires three seasons of homework.

## Why This Matters

The OTT-to-theatrical pipeline in India has been almost entirely one-directional until now. Films that underperform in theaters get a "second life" on streaming — Dhurandhar on Netflix, Drishyam 2 on JioHotstar, countless others. The reverse — a streaming series getting promoted to theatrical — is almost unprecedented in Indian entertainment.

There are reasons for that. OTT audiences and theatrical audiences overlap but don't perfectly align. Streaming watchers are used to 10 hours of plot development; cinema demands a complete story in two. Streaming allows you to pause, rewind, watch at 1.5x; cinema demands your undivided attention. The economics are different too: a streaming series earns its money from subscriptions and platform deals, while a theatrical film must sell individual tickets at scale.

Sacred Games was rumoured to get a film treatment that never materialised. Family Man's creators have discussed theatrical possibilities. Breathe and Paatal Lok remained firmly on their platforms. Mirzapur is the first Indian OTT original to actually cross the threshold.

## The Cast That Built It

Pankaj Tripathi's Kaleen Bhaiya became one of Indian entertainment's most iconic villains — a carpet exporter who moonlights as a crime lord, played with the kind of quiet menace that makes you forget the actor is the same man who played a bumbling bureaucrat in Stree. The character spawned a cottage industry of YouTube tributes, TikTok impressions, and WhatsApp sticker packs.

Ali Fazal's Guddu Pandit — the scrawny gym-obsessed college student turned vengeful gangster — gave the series its emotional spine. Fazal, who had already earned international recognition through Victoria & Abdul opposite Judi Dench, used Mirzapur to cement himself as one of India's most versatile actors.

Divyendu Sharma's Munna Tripathi was the show's wildcard — unpredictable, explosive, and darkly comic. Shweta Tripathi's Golu evolved from a studious college girl into one of Indian streaming's most compelling female antiheroes.

Moving this ensemble to a theatrical setting is a risk. Television actors can feel diminished on the big screen, and series characters sometimes lose their complexity when compressed into film format. But Excel Entertainment's track record — Dil Chahta Hai, Zindagi Na Milegi Dobara, Don — suggests they understand the medium well enough to make the transition work.

## The NRI Test

For the diaspora, Mirzapur's theatrical release poses an interesting question: will NRIs who binged the show at home actually go to a cinema to watch the next chapter?

The evidence from other Indian theatrical releases suggests they might. Drishyam 3 just collected ₹70 crore from overseas markets in three days — roughly 60% of its worldwide total. Dhurandhar 2 became the first Indian film to cross $25 million in North America. The NRI theatrical audience for Indian content has never been larger or more willing to spend.

But those are established film franchises. Mirzapur would be the first Indian streaming original to test the overseas theatrical waters. If it succeeds — if NRIs actually fill seats in AMC theaters in Edison and Cineworld screens in Wembley for a show they used to watch in bed — it could open a pipeline that transforms how Indian OTT content reaches the diaspora.

The alternative is that streaming audiences prefer streaming. That the intimacy of watching Kaleen Bhaiya scheme from your couch, at your own pace, is part of what made the show work — and that translating it to a darkened theater removes exactly the quality that made it special.

Either way, we're about to find out. Principal photography is done. Post-production is underway. And somewhere in a theater near you, Kaleen Bhaiya is about to expand his territory."""
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Akshay Kumar + Vidya Balan Sankranthiki Vasthunam remake
# ══════════════════════════════════════════════════════════════

a2_id = str(uuid.uuid4())

articles.append({
    "id": a2_id,
    "headline": "Akshay Kumar and Vidya Balan Are Reuniting for the First Time Since Mission Mangal. The Film Is a Hindi Remake of Telugu's Biggest 2025 Hit.",
    "subheadline": "Director Anees Bazmee has confirmed the cast for the Hindi adaptation of Sankranthiki Vasthunam — the Venkatesh blockbuster that earned over ₹300 crore. The South-to-Bollywood remake machine is running again, and this time it has Dil Raju producing.",
    "slug": "akshay-kumar-vidya-balan-sankranthiki-vasthunam-hindi-remake-anees-bazmee-20260523",
    "category": "Entertainment",
    "vertical": "entertainment",
    "urgency": "standard",
    "status": "published",
    "published_at": now,
    "score_total": 76,
    "tags": ["Akshay Kumar", "Vidya Balan", "Anees Bazmee", "Dil Raju", "Sankranthiki Vasthunam", "Hindi remake", "Telugu", "Raashii Khanna", "Vijay Raaz", "Bollywood", "South Indian cinema"],
    "diaspora_angle": "For NRIs who consume both Bollywood and South Indian cinema — which is an increasingly large overlap, thanks to streaming platforms that serve both — this remake raises an immediate question: why? Sankranthiki Vasthunam is already available with subtitles on multiple platforms. The Telugu original, starring Venkatesh Daggubati, was a massive hit during the 2025 Sankranthi season. Diaspora audiences in the US and UK have already watched it. The Hindi remake is betting that there remains a large Hindi-speaking audience — in India and abroad — that won't watch a Telugu film even with subtitles, but will pay for Akshay Kumar doing the same thing in Hindi. That bet has historically been correct (Drishyam, Bhool Bhulaiyaa, Simmba all proved it), but it's worth asking how long this arbitrage holds as the language barrier continues to shrink. Dil Raju producing both the original and the remake is the clearest sign of how industrialised this pipeline has become.",
    "sources": [
        {"url": "https://www.sacnilk.com", "name": "Sacnilk"},
        {"url": "https://trends.glance.com", "name": "Glance"},
        {"url": "https://www.bollywoodhungama.com", "name": "Bollywood Hungama"}
    ],
    "image_search_query": "Akshay Kumar Vidya Balan film announcement 2026",
    "word_count": 850,
    "body": """Akshay Kumar and Vidya Balan are about to share screen space for the first time in seven years. And the vehicle bringing them back together is, fittingly, a Telugu blockbuster that most of the Hindi-speaking audience has probably never heard of.

## The Confirmation

Director Anees Bazmee has officially confirmed the casting for the Hindi adaptation of *Sankranthiki Vasthunam*, the Venkatesh Daggubati-led action comedy that became one of Telugu cinema's biggest hits during the 2025 Sankranthi season. The film stars Akshay Kumar and Vidya Balan in the lead roles, alongside Raashii Khanna, Vijay Raaz, Zakir Hussain, and Sayaji Shinde.

The project is produced by Dil Raju under Sri Venkateswara Creations — the same banner that produced the Telugu original. Bazmee has described the Hindi version as a "reimagined narrative tailored for the national audience" rather than a shot-for-shot remake.

"All I can say is that our film is good," Bazmee said. "We've put in the work."

Principal filming is expected to begin immediately, with a target release window of late 2026 or early 2027.

## The Pairing

Akshay Kumar and Vidya Balan have a track record that few Bollywood pairings can match for consistency. Their collaborations read like a hit list:

- **Bhool Bhulaiyaa** (2007) — the horror comedy that became a franchise
- **Heyy Babyy** (2007) — the slapstick comedy that worked despite itself
- **Thank You** (2011) — directed by Anees Bazmee himself
- **Mission Mangal** (2019) — the ISRO space drama that became a Independence Day blockbuster

The gap since Mission Mangal has been seven years. In that time, Akshay Kumar has had a notoriously uneven run — some hits (Bhooth Bangla), many misses (Selfiee, Bade Miyan Chote Miyan, Khel Khel Mein). Vidya Balan, meanwhile, has been choosier but more consistent, with strong work in Jalsa and Sherni.

Reuniting them for a crowd-pleasing entertainer is a strategic play: it banks on nostalgia for the Bhool Bhulaiyaa-era chemistry while giving both actors a commercial vehicle they need at this point in their careers.

## The Original

*Sankranthiki Vasthunam*, directed by Anil Ravipudi, was a mass entertainer in the classic Telugu mold — high on comedy, heavy on action, and built around a star (Venkatesh) who audiences trust to deliver a good time. The film earned over ₹300 crore worldwide during its Sankranthi run, making it one of the year's biggest Telugu hits.

The plot blends action set-pieces with family comedy — the kind of hybrid that Telugu cinema does exceptionally well and Bollywood has historically struggled to replicate without making it feel forced. Ravipudi's direction kept the tone consistent; whether Bazmee can do the same in Hindi remains the key question.

## The Remake Machine

This film is the latest entry in what has become Indian cinema's most reliable production pipeline: take a South Indian hit, cast Bollywood stars, reshoot it in Hindi, and release it to a market that is — for cultural and linguistic reasons — still reluctant to watch dubbed or subtitled regional films.

The track record is extensive:

- *Drishyam* (Malayalam → Hindi) — ₹110 crore
- *Bhool Bhulaiyaa* (Malayalam → Hindi) — franchise that's earned ₹500+ crore across sequels
- *Kabir Singh* (Telugu → Hindi) — ₹379 crore
- *Simmba* (Telugu → Hindi) — ₹400 crore
- *Jersey* (Telugu → Hindi) — flopped, proving the pipeline isn't foolproof

What's different this time is the producer. Dil Raju producing both the Telugu original and the Hindi remake means the adaptation is sanctioned, not just licensed. He understands what made the original work and has financial incentive to ensure the remake doesn't dilute it.

## For NRIs: The Language Question

Here's the uncomfortable truth that the Hindi remake industry doesn't love discussing: the language barrier is shrinking. Streaming platforms serve Telugu, Tamil, Malayalam, and Kannada content to NRI audiences with professional subtitles. RRR became a global phenomenon in its original Telugu. Pushpa transcended language entirely. Baahubali was the template.

The NRI audience that would have been the core market for a Hindi remake of Sankranthiki Vasthunam may have already watched the original — in Telugu, with English subtitles, on their TVs in Fremont or Paramus or Harrow.

So the Hindi remake isn't really for the diaspora anymore. It's for the massive Hindi-speaking domestic audience that still won't cross the language threshold. And for Akshay Kumar, who needs a commercial hit badly enough to bet on someone else's proven material rather than trust his own instincts.

Filming begins soon. The South-to-Bollywood pipeline continues. And somewhere, Venkatesh Daggubati is probably smiling at the royalty checks."""
})

# ══════════════════════════════════════════════════════════════
# PUBLISH ARTICLES
# ══════════════════════════════════════════════════════════════

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✓ Published: {art['slug']} → {art['id']}")
    except Exception as e:
        print(f"✗ Failed: {art['slug']} → {e}")

# ══════════════════════════════════════════════════════════════
# SCORE DECAY — reduce scores for entertainment articles >48h old
# ══════════════════════════════════════════════════════════════

cutoff = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat().replace("+00:00", "Z")
decay_url = f"{SB_URL}/rest/v1/p2_articles?category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff}&score_total=gt.10&select=id,score_total,slug&order=published_at.desc&limit=50"
r = requests.get(decay_url, headers=HEADERS, timeout=30)
decay_candidates = r.json() if r.status_code == 200 else []

decayed = 0
for art in decay_candidates:
    old_score = art["score_total"]
    new_score = max(10, int(old_score * 0.92))
    if new_score < old_score:
        sc = sb_patch("p2_articles", f"id=eq.{art['id']}", {"score_total": new_score})
        if sc in (200, 204):
            decayed += 1

print(f"\nScore decay: {decayed} articles decayed out of {len(decay_candidates)} eligible")

print("\nDone!")
