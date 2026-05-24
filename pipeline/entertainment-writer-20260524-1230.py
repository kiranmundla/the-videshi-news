#!/usr/bin/env python3
"""Entertainment writer — May 24 2026, 12:30 PDT batch:
1. Ansiba Hassan's AMMA resignation / Tiny Tom communal abuse controversy (timed with Drishyam 3's massive run)
2. Hai Jawani Toh Ishq Hona Hai trailer launch — David Dhawan's emotional comeback, June 5 worldwide release
+ Score decay for older entertainment articles
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

def sb_get(table, filters, select="*"):
    r = requests.get(f"{SB_URL}/rest/v1/{table}?{filters}&select={select}", headers=HEADERS, timeout=15)
    return r.json() if r.status_code == 200 else []

def check_duplicate(slug):
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id",
        headers=HEADERS, timeout=15
    )
    return len(r.json()) > 0 if r.status_code == 200 else False

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Ansiba Hassan AMMA Controversy
# ══════════════════════════════════════════════════════════════
slug1 = "ansiba-hassan-amma-resignation-tiny-tom-communal-abuse-drishyam-3-20260524"
if not check_duplicate(slug1):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Drishyam 3's Onscreen Daughter Just Accused a Fellow Actor of Calling Her a 'Jihadi.' The Film Made ₹140 Crore While No One in the Industry Said a Word.",
        "subheadline": "Ansiba Hassan — who plays Mohanlal's eldest daughter Anju in the franchise — resigned from AMMA after alleging that actor Tiny Tom spread communal slurs, fabricated police complaints, and engaged in character assassination. The Malayalam industry's biggest weekend of the year coincided with its ugliest backstage story.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "developing",
        "status": "published",
        "published_at": now,
        "score_total": 79,
        "tags": ["Ansiba Hassan", "Drishyam 3", "AMMA", "Tiny Tom", "Mohanlal", "Malayalam cinema", "communal abuse", "Shweta Menon"],
        "diaspora_angle": "For NRIs who grew up watching Drishyam — the franchise that became a global cultural export — Ansiba Hassan's allegations expose a deeply uncomfortable fault line. The same industry celebrating its biggest-ever overseas numbers is allegedly harboring communal abuse within its own actors' association. Malayalam cinema's soft power abroad depends on its reputation as India's most progressive film industry. That reputation is now being tested by one of its most recognizable young actresses.",
        "sources": [
            {"url": "https://www.zoomtventertainment.com/entertainment/ansiba-hassan-amma-resignation-revelations", "name": "Zoom TV"},
            {"url": "https://cinemaexpress.com/article/entertainment/ansiba-hassan-left-amma-due-to-tiny-tom", "name": "Cinema Express"},
            {"url": "https://devdiscourse.com/article/entertainment/drishyam-actress-ansiba-hassan-tiny-tom-character-assassination", "name": "Devdiscourse"},
            {"url": "https://madhyamamonline.com/actor-ansiba-accuses-tiny-tom-amma-communal-abuse", "name": "Madhyamam"},
            {"url": "https://newsdive.net/ansiba-hassan-tiny-tom-amma-tensions", "name": "News Dive"}
        ],
        "image_search_query": "Ansiba Hassan actress Drishyam 3 2026 AMMA Kerala",
        "image_entities": ["Ansiba Hassan", "Mohanlal", "Drishyam 3", "AMMA"],
        "image_must_show": "Ansiba Hassan portrait or Ansiba Hassan at a Drishyam 3 event",
        "word_count": 830,
        "body": """Here is a story about timing.

On May 21, Drishyam 3 opened worldwide to ₹43 crore — one of the biggest opening days in Malayalam cinema history. By Day 4, the franchise had crossed ₹140 crore globally. Mohanlal's Georgekutty had, once again, outsmarted everyone. NRI audiences from Fremont to Dubai were booking out screens. The Malayalam film industry was celebrating its most commercially dominant weekend of the year.

Two days into that celebration, on May 23, the actress who plays Georgekutty's eldest daughter went public with allegations that should make every celebrant uncomfortable.

## What Ansiba Hassan Said

Ansiba Hassan — who has played Anju George across all three Drishyam films — resigned from AMMA (the Association of Malayalam Movie Artists) back in February. On Saturday, she revealed why.

In interviews with Mathrubhumi and other Malayalam outlets, Ansiba made six specific allegations:

**1. Tiny Tom called her a "Jihadi."** The actor-impersonator allegedly labelled her with the communal slur and attempted to link her with religious conversion activities — an accusation that carries particularly toxic weight in Kerala's current political climate.

**2. Fabricated stories about illicit relationships.** Ansiba says Tom spread false narratives about her personal life within industry circles, amounting to what she calls "character assassination."

**3. A false police complaint.** She alleges that another AMMA executive committee member filed a police complaint against her, which led to inquiries that caused severe mental distress. She says the complaint had no basis.

**4. She informed Mammootty and Mohanlal before resigning.** Both Malayalam superstars — who serve in AMMA's leadership — were reportedly told of her decision. Neither has made a public statement.

**5. AMMA's leadership provided "insufficient support."** Despite being a joint secretary of the organization, Ansiba says she received no institutional backing when the allegations against her mounted.

**6. The cumulative impact was prolonged mental harassment.** Ansiba has framed her departure not as a professional disagreement but as the result of sustained, targeted abuse within the industry's own governing body.

## The Silence Around the Story

Tiny Tom has denied the allegations, calling them "hearsay." Actress Lakshmipriya has publicly defended him. AMMA president Shweta Menon confirmed that Ansiba's resignation was received and that a complaint was indeed filed — but only after media reports surfaced, not in response to Ansiba's initial claims.

What's notable is what hasn't happened. No major Malayalam star has spoken in support of Ansiba. No AMMA investigation has been announced. The story broke on the same day that Drishyam 3 crossed ₹100 crore worldwide — and the box office headlines completely swallowed it.

This isn't unusual. Indian film industries have a documented pattern of letting institutional controversies disappear into the noise of commercial success. The Malayalam industry specifically went through this cycle with the 2017 actress assault case, the subsequent Justice Hema Committee report, and the mass resignations from AMMA that followed. Each time, attention spiked and then dissipated.

## Why This Matters for the Diaspora

Malayalam cinema has built its international reputation on a specific brand: intelligent, progressive, artistically ambitious. It's the industry that produced *All We Imagine as Light*, that sent Payal Kapadia to preside over a Cannes jury, that regularly outperforms its domestic size at the global box office.

That brand is real — and it's commercially powerful. Drishyam 3's overseas collections (₹65 crore in three days) are proof that NRI audiences trust Malayalam cinema in a way they don't trust most Indian film industries.

But brand and reality aren't the same thing. When an actress who has been part of the biggest Malayalam franchise of the century says she was subjected to communal slurs and forced out of the industry's main professional body — and the response is effectively nothing — it raises questions about what progressive actually means.

For NRIs who fill those overseas screens, the question is personal: does your ticket money support an industry that protects its own, or one that protects its biggest names and lets the rest fend for themselves?

## Where It Stands

As of Sunday, there is no indication that AMMA will conduct a formal inquiry. Tiny Tom has not retracted or apologized. Mohanlal and Mammootty have not commented. Ansiba Hassan continues to promote Drishyam 3 through press appearances — the professional obligation of an actress whose franchise is having its biggest moment, even as her allegations against the industry go unanswered.

Drishyam 3, meanwhile, is projected to cross ₹175 crore worldwide by Monday. Georgekutty will keep outwitting the system. Whether the industry around him can be outwitted quite so easily is a different story."""
    })
else:
    print(f"⚠️ Skipping duplicate: {slug1}")

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Hai Jawani Toh Ishq Hona Hai trailer
# ══════════════════════════════════════════════════════════════
slug2 = "hai-jawani-toh-ishq-hona-hai-trailer-david-dhawan-varun-june-5-worldwide-20260524"
if not check_duplicate(slug2):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "David Dhawan Cried at His Own Trailer Launch. His Son Varun Was Standing Next to Him. Their Film Releases Worldwide on June 5. NRIs Who Grew Up on 'Coolie No. 1' Know Exactly Why This Matters.",
        "subheadline": "The Hai Jawani Toh Ishq Hona Hai trailer dropped on May 23 — David Dhawan's 46th film, his fourth with Varun, and a deliberate throwback to the era when Bollywood rom-coms were the only thing NRI families watched together.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "developing",
        "status": "published",
        "published_at": now,
        "score_total": 74,
        "tags": ["Hai Jawani Toh Ishq Hona Hai", "David Dhawan", "Varun Dhawan", "Mrunal Thakur", "Pooja Hegde", "Bollywood", "romantic comedy", "June 5"],
        "diaspora_angle": "David Dhawan's films — Coolie No. 1, Hero No. 1, Judwaa, Biwi No. 1 — aren't just movies for the Indian diaspora. They're the shared vocabulary of every NRI living room in the 90s and 2000s. The VHS tapes. The family movie nights. The songs you heard at every wedding. Hai Jawani Toh Ishq Hona Hai, releasing worldwide June 5, is an explicit bet that this nostalgia still sells — and that Varun Dhawan can inherit what Govinda and Salman Khan built.",
        "sources": [
            {"url": "https://www.filmfare.com/news/bollywood/trailer-varun-dhawan-hai-jawani-toh-ishq-hona-hai", "name": "Filmfare"},
            {"url": "https://www.bollywoodhungama.com/news/bollywood/hai-jawani-toh-ishq-hona-hai-trailer-david-dhawan", "name": "Bollywood Hungama"},
            {"url": "https://www.zoomtventertainment.com/entertainment/hai-jawani-toh-ishq-hona-hai-trailer-varun-dhawan", "name": "Zoom TV"},
            {"url": "https://www.koimoi.com/hai-jawani-toh-ishq-hona-hai-trailer-review", "name": "Koimoi"}
        ],
        "image_search_query": "Hai Jawani Toh Ishq Hona Hai trailer launch Varun Dhawan David Dhawan 2026",
        "image_entities": ["Varun Dhawan", "David Dhawan", "Mrunal Thakur", "Pooja Hegde"],
        "image_must_show": "Varun Dhawan and David Dhawan at the trailer launch event, or the Hai Jawani Toh Ishq Hona Hai movie poster",
        "word_count": 780,
        "body": """There is a moment in the Hai Jawani Toh Ishq Hona Hai trailer launch — held in Mumbai on May 23 — that has nothing to do with the film itself.

David Dhawan, 68 years old, 46 films deep, the man who defined Bollywood's 90s comedy template, is standing on stage. His son Varun is next to him. Every cast member — Mrunal Thakur, Pooja Hegde, Jimmy Shergill, Chunky Panday, Rakesh Bedi, Ali Asgar — has just spent the event praising him. And David Dhawan starts crying.

"Everybody should have a son like Varun," he said, wiping his eyes.

This is not a normal Bollywood trailer launch. And Hai Jawani Toh Ishq Hona Hai is not a normal Bollywood film. It's a father and son trying to prove that the kind of cinema they both love — loud, warm, unapologetically commercial romantic comedies — still has a place in an industry obsessed with dark thrillers and cinematic universes.

## What the Trailer Shows

The trailer, which was supposed to drop on May 21 but was delayed due to a "technical issue" (likely strategic repositioning after the Drishyam 3 and Star Wars openings), finally arrived on May 23 to immediate viral response.

The setup is classic David Dhawan chaos: Varun Dhawan plays a young man caught between two women (Mrunal Thakur and Pooja Hegde), two pregnancies, and an escalating series of lies that threaten to collapse his entire life. There's mistaken identity. There's slapstick. There's a scene involving what appears to be a very angry Jimmy Shergill. There's Chunky Panday being Chunky Panday.

If you grew up on *Judwaa*, *Coolie No. 1*, or *Hero No. 1*, the DNA is unmistakable. David Dhawan has not reinvented himself. He has doubled down.

The music, composed by Anu Malik with lyrics by Sameer — the same team behind many of David Dhawan's biggest hits — has already started gaining traction. At the launch, lyricist Sameer and writer Rumy Jafry explained the signature "situation gayi tel lagane" formula: songs that have nothing to do with the literal plot but capture the energy of the scene. "There was no baap in 'Tere Baap Ke Darr Se,'" Sameer joked. "The heroine lived in a bungalow, yet we had 'Oonchi Hai Building.'"

## The June 5 Gamble

Hai Jawani Toh Ishq Hona Hai releases worldwide on June 5 — a date the team has changed multiple times. Originally set for April 10, it was pushed to May 22, then to June 12 (to avoid Yash's *Toxic*), and finally settled on June 5 when *Toxic* was postponed due to geopolitical tensions.

The date puts it directly after Drishyam 3's run and just before what's expected to be a crowded summer. The bet is that there's a specific audience — families, couples, older viewers — who haven't been served by the current slate of dark thrillers and South Indian action films.

For NRI audiences, the June 5 worldwide release matters. This is the kind of film that used to pack out the old single-screen cinemas in Edison, Artesia, and Southall. The question is whether it can do the same in the multiplex era, when competition for the diaspora audience includes not just other Hindi films but Telugu blockbusters, Malayalam thrillers, and Hollywood tentpoles.

## A Father-Son Story Behind a Father-Son Industry

David Dhawan's career is inseparable from the NRI experience. His films with Govinda — *Coolie No. 1*, *Hero No. 1*, *Bade Miyan Chote Miyan*, *Partner* — were the VHS tapes that traveled from India to every Indian household abroad. They were the films playing on loop at Diwali parties, the songs at sangeet nights, the dialogue that uncles quoted at family gatherings.

That era ended. Govinda's box office appeal faded. Salman Khan moved to action franchises. The David Dhawan comedy seemed to become a relic.

Then Varun Dhawan started working with his father. Their first three collaborations — *Main Tera Hero*, *Judwaa 2*, and *Coolie No. 1* (2020) — ranged from hit to disaster. *Coolie No. 1*'s pandemic-era release on Amazon Prime was widely considered one of the worst Hindi films of its year. It felt like the end.

Hai Jawani Toh Ishq Hona Hai feels like a response to that failure. The trailer is tighter, funnier, and more confident than anything David Dhawan has made in a decade. Varun's comic timing — always his strongest skill — is sharper than his dramatic work. And the supporting cast (Jimmy Shergill, in particular, looks like he's having the time of his life) suggests a film where everyone understood the assignment.

## What to Know Before June 5

The film arrives with strong advance buzz from the trailer, genuine emotional goodwill from the launch event, and a release window that's relatively clear. It's a David Dhawan romantic comedy releasing in a market that hasn't had one in years.

For the diaspora: this is a bet on your nostalgia. David Dhawan is betting that you miss what Bollywood used to be. He cried at his own trailer launch because he knows this might be one of his last chances to prove it. June 5. Worldwide."""
    })
else:
    print(f"⚠️ Skipping duplicate: {slug2}")

# ══════════════════════════════════════════════════════════════
# INSERT ARTICLES
# ══════════════════════════════════════════════════════════════
print(f"\n📝 Inserting {len(articles)} articles...")
inserted = []
for article in articles:
    try:
        result = sb_post("p2_articles", article)
        art = result[0] if isinstance(result, list) else result
        inserted.append(art)
        print(f"  ✅ Inserted: {article['headline'][:70]}...")
    except Exception as e:
        print(f"  ❌ Failed to insert {article['slug']}: {e}")

# ══════════════════════════════════════════════════════════════
# SCORE DECAY — older entertainment articles
# ══════════════════════════════════════════════════════════════
print("\n📉 Applying score decay...")
now_dt = datetime.now(timezone.utc)

# Articles > 7 days old: score → 35
cutoff_7d = (now_dt - timedelta(days=7)).isoformat()
status_7d = sb_patch(
    "p2_articles",
    f"vertical=eq.entertainment&status=eq.published&published_at=lt.{cutoff_7d}&score_total=gt.35",
    {"score_total": 35}
)
print(f"  7d+ decay → HTTP {status_7d}")

# Articles 3-7 days old: score → 50
cutoff_3d = (now_dt - timedelta(days=3)).isoformat()
status_3d = sb_patch(
    "p2_articles",
    f"vertical=eq.entertainment&status=eq.published&published_at=lt.{cutoff_3d}&published_at=gte.{cutoff_7d}&score_total=gt.50",
    {"score_total": 50}
)
print(f"  3-7d decay → HTTP {status_3d}")

print(f"\n✅ Entertainment writer complete! {len(inserted)} articles published.")
for a in inserted:
    print(f"  • {a.get('slug', 'unknown')}")
