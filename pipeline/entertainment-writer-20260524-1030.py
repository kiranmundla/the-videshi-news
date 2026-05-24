#!/usr/bin/env python3
"""Entertainment writer — May 24 2026, 10:30 PDT batch:
1. Drishyam 3 crosses ₹112 crore worldwide in 3 days — Mohanlal's biggest international opening
2. Cannes 2026 wraps — Payal Kapadia as jury president, FTII short, Aishwarya's closing look, but no Indian feature in competition
+ Score decay for old entertainment articles
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
# ARTICLE 1: Drishyam 3 crosses ₹112 crore worldwide in 3 days
# ══════════════════════════════════════════════════════════════
slug1 = "drishyam-3-mohanlal-112-crore-worldwide-3-days-nri-box-office-record-20260524"
if not check_duplicate(slug1):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Mohanlal's Drishyam 3 Crossed ₹100 Crore in 58 Hours. It Just Passed ₹112 Crore. And the Biggest Number Isn't From India.",
        "subheadline": "Drishyam 3 has earned ₹65 crore overseas — more than its entire India gross — making it Mohanlal's highest-grossing international film ever. The NRI audience isn't just watching Malayalam cinema anymore. They're funding it.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "developing",
        "status": "published",
        "published_at": now,
        "score_total": 80,
        "tags": ["Drishyam 3", "Mohanlal", "Jeethu Joseph", "Malayalam cinema", "box office", "NRI audience", "Georgekutty", "overseas collection"],
        "diaspora_angle": "Drishyam 3's overseas haul — ₹65 crore in three days — is the headline. For the first time in Mohanlal's career, his international collections have outpaced domestic. This isn't an anomaly; it's confirmation that the NRI Malayalam-speaking audience has become the financial backbone of Kerala's biggest releases. Every sold-out screening from Dallas to Dubai isn't just a ticket — it's a vote for the kind of cinema the diaspora wants to see made.",
        "sources": [
            {"url": "https://sacnilk.com/box_office/drishyam-3-collection", "name": "Sacnilk"},
            {"url": "https://www.zoomtventertainment.com/entertainment/drishyam-3-100-crore-58-hours", "name": "Zoom TV"},
            {"url": "https://www.filmibeat.com/drishyam-3-worldwide-collection", "name": "Filmibeat"},
            {"url": "https://www.hollywoodreporterindia.com/drishyam-3-day-1", "name": "Hollywood Reporter India"}
        ],
        "image_search_query": "Drishyam 3 Mohanlal 2026 film Georgekutty",
        "image_entities": ["Mohanlal", "Drishyam 3", "Jeethu Joseph"],
        "image_must_show": "Mohanlal in his Georgekutty avatar from Drishyam 3, or the Drishyam 3 film poster",
        "word_count": 820,
        "body": """There is a number buried inside Drishyam 3's box office report that tells you more about the future of Indian cinema than any collection total can.

₹65 crore.

That's Drishyam 3's overseas gross in just three days. It's more than the film's entire India gross of ₹47 crore. It's more than Mohanlal's previous film *Patriot* earned overseas in its entire theatrical run. And it means that for one of the biggest Malayalam stars of all time, the diaspora audience has officially become the primary market.

## The Numbers Tell a New Story

Drishyam 3 opened on May 21 to ₹43 crore worldwide — one of the largest opening days in Malayalam cinema history. By Day 2, the film had crossed ₹76 crore globally despite a softer Friday in India. On Saturday, it roared back: the worldwide cume hit ₹112.17 crore, with the ₹100 crore milestone reached in just 58 hours.

In India, the film earned ₹15.85 crore net on Day 1, dipped to ₹11.05 crore on Day 2 (a 30% drop, typical for a Wednesday release), then climbed to ₹13.70 crore on Saturday with 50.2% occupancy across 5,185 shows. Sunday is expected to beat the opening day — a pattern that suggests strong word-of-mouth despite mixed critical reception.

But here's what matters: the overseas numbers didn't follow the Indian pattern. They climbed every single day. The NRI audience for Malayalam cinema doesn't experience the same midweek dip because screenings in the US, UK, Canada, and the Gulf are clustered around evenings and weekends regardless of the Indian release day.

## Mohanlal's International Transformation

To understand what ₹65 crore overseas means, consider the context. Mohanlal's *Patriot*, a spy thriller with Mammootty released earlier this year, earned ₹43.25 crore overseas in its entire run. Drishyam 3 surpassed that in two days.

The Drishyam franchise has always been Mohanlal's most globally resonant property. The character of Georgekutty — a cable TV operator who outsmarts the police to protect his family — translates across cultures. The Hindi remake starring Ajay Devgn proved it. The Chinese remake proved it again. But there's a difference between global cultural resonance and global box office power. Drishyam 3 has crossed both thresholds.

Director Jeethu Joseph, who has shepherded all three films, understands something that many Indian filmmakers still don't: the NRI audience isn't watching out of nostalgia. They're watching because they want to see Malayalam storytelling at its sharpest — complex moral dilemmas, ordinary people in extraordinary situations, films that respect their intelligence.

## The Overseas Engine

Where is the money coming from? The US and the Gulf lead, as they always do for Malayalam releases. The Bay Area, Dallas-Fort Worth, New Jersey, and Chicago are the American strongholds for Kerala cinema. In the Gulf — Dubai, Abu Dhabi, Bahrain, Kuwait — the Malayali diaspora is enormous and cinema-devoted. The UK, Canada, and Australia round out the top markets.

What's changed isn't the geography — it's the scale. Five years ago, a ₹20 crore overseas total was exceptional for a Malayalam film. *2018* managed it. *Lucifer* came close. Now ₹65 crore in three days is reality. The audience has grown, the theatrical infrastructure has expanded (more screens, more showtimes, better marketing), and the streaming era has paradoxically made theatrical releases more event-like, not less.

## Mixed Reviews, Maximum Business

Drishyam 3 has received mixed critical reviews. Some feel the third instalment stretches a story that was perfectly resolved in Part 2. Others argue that Mohanlal's performance remains magnetic enough to carry a weaker script. The audience has decided the question with their wallets.

This is a pattern NRIs know well: Indian cinema franchises rarely end at the perfect creative moment. The market decides when a story is done, not the screenwriter. But Drishyam 3's audience reception suggests that people aren't watching for narrative surprise — they're watching for the experience of seeing Georgekutty think his way out of trouble one more time, preferably on the biggest screen available, preferably with a theatre full of people who gasp at the same moments.

## What ₹112 Crore in Three Days Means

Drishyam 3 is now the third-highest-grossing Malayalam film of 2026, behind only *L2: Empuraan* and *Karuppu* in worldwide totals. With Sunday's numbers expected to push the cume past ₹130 crore, it could challenge for second place before the first week ends.

But the real significance is structural. When a Malayalam film earns more overseas than domestically, it changes the economics of the industry. Budgets can go up. Marketing can go global from day one. And the stories that get greenlit start to account for diaspora tastes — not just Kerala's.

For NRI audiences who've spent years watching Malayalam cinema evolve from a regional industry to a global one, Drishyam 3's numbers aren't just impressive. They're a receipt for their influence. The money you spend at the AMC in Fremont or the Reel in Dubai doesn't just buy a ticket — it buys the next generation of Malayalam films that take your taste seriously."""
    })
else:
    print(f"⚠️ Skipping duplicate: {slug1}")

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Cannes 2026 wraps — Indian presence, what it means
# ══════════════════════════════════════════════════════════════
slug2 = "cannes-2026-payal-kapadia-aishwarya-rai-ftii-india-no-competition-film-20260524"
if not check_duplicate(slug2):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Cannes 2026 Is Over. India Had a Jury President, a Closing Ceremony Icon, and a Film School Entry. It Had Zero Films in Competition.",
        "subheadline": "Payal Kapadia presided over the Critics' Week jury. Aishwarya Rai owned the closing ceremony red carpet. An FTII student film screened in Cinéfondation. A 1986 Malayalam classic was restored. And yet — for the second year running — no Indian feature competed for the Palme d'Or.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now,
        "score_total": 76,
        "tags": ["Cannes 2026", "Payal Kapadia", "Aishwarya Rai", "FTII", "Indian cinema", "Palme d'Or", "Cristian Mungiu", "Cannes Film Festival"],
        "diaspora_angle": "For NRIs who follow Indian cinema's global profile, Cannes 2026 is a mixed signal. India's soft power at the festival — through fashion, jury appointments, and film school representation — has never been higher. But the hard metric that matters — a feature film selected for the main competition — remains elusive. In a year when India's film industry is spending ₹200-700 crore on individual productions, the absence from Cannes's most prestigious slate raises an uncomfortable question: is India making the world's most expensive films, or its most important ones?",
        "sources": [
            {"url": "https://en.wikipedia.org/wiki/2026_Cannes_Film_Festival", "name": "Wikipedia"},
            {"url": "https://www.pinkvilla.com/cannes-2026-aishwarya-rai", "name": "Pinkvilla"},
            {"url": "https://www.filmibeat.com/cannes-2026-ahsaas-channa-gudgudi", "name": "Filmibeat"},
            {"url": "https://www.latestly.com/cannes-2026-winners", "name": "LatestLY"}
        ],
        "image_search_query": "Cannes 2026 film festival closing ceremony Aishwarya Rai red carpet",
        "image_entities": ["Aishwarya Rai Bachchan", "Cannes 2026", "Payal Kapadia"],
        "image_must_show": "Aishwarya Rai at Cannes 2026 closing ceremony, or the Cannes Film Festival 2026 venue/red carpet",
        "word_count": 850,
        "body": """The 79th Cannes Film Festival closed on May 23 with Romanian filmmaker Cristian Mungiu winning the Palme d'Or for *Fjord* — his second career win after *4 Months, 3 Weeks and 2 Days* in 2007. Andrey Zvyagintsev's *Minotaur* took the Grand Prix. Virginie Efira and Tao Okamoto shared Best Actress for Ryusuke Hamaguchi's *All of a Sudden*. Honorary Palme d'Or awards went to Peter Jackson, Barbra Streisand, and John Travolta.

India's presence at the festival was significant — but pointedly not in the places that matter most.

## What India Had

**Payal Kapadia as Critics' Week Jury President.** This is arguably the most consequential Indian appointment at Cannes in years. Kapadia, whose *All We Imagine as Light* won the Grand Prix in 2024, was invited to preside over the jury for the Critics' Week — the section dedicated to first and second films. She helped select *La Gradiva* by Marine Atlan as the Grand Prize winner. For an Indian filmmaker to sit in judgement at Cannes is a milestone that signals Kapadia's permanent arrival in the global auteur class.

**Aishwarya Rai Bachchan's closing ceremony appearance.** After 24 years of Cannes red carpets, Aishwarya remains the festival's most photographed Indian presence. This year, she attended with daughter Aaradhya and wore a custom white Cheney Chan pantsuit with a dramatic feather boa to the closing ceremony. A blue gown with a ₹5 crore necklace at the *Birthday Party* premiere earned viral coverage. Fans chanted her name on the streets. Pinkvilla called her "the undisputed queen." But Aishwarya's Cannes appearances are now almost entirely fashion events — she hasn't premiered a film at the festival in over a decade.

**Mehar Malhotra's *Shadows of the Moonless Nights* in Cinéfondation.** A Punjabi-language short film from the Film and Television Institute of India (FTII) was selected among 19 student films from 15 countries. It didn't win a prize — the top award went to *Laser-Cat*, a film from NYU — but the selection itself matters. FTII has a long Cannes history, and each selection keeps the pipeline visible.

**Ahsaas Channa's *Gudgudi* at the Short Film Corner.** The actress, known for web series like *Kota Factory* and *Hostel Daze*, attended the Rendez-vous Industry Screening for her short film. It was screened at the Marché du Film segment — the industry marketplace rather than a competitive section — but it marked a personal milestone and generated considerable Indian media coverage.

**The restoration of *Amma Ariyan* (1986).** John Abraham's landmark Malayalam film about political consciousness and student activism was screened in the Cannes Classics section with a new restored print. For the Malayali diaspora, this is a cultural reclamation — a film that helped define Kerala's independent cinema tradition, given a global stage nearly 40 years after its release.

## What India Didn't Have

No Indian feature film in the main competition. No Indian film in Un Certain Regard. No Indian film in the Directors' Fortnight competition.

This isn't an aberration — it's a pattern. Since Kapadia's *All We Imagine as Light* broke through in 2024, India has struggled to maintain a presence in Cannes's competitive sections. The festival's artistic director Thierry Frémaux reviewed 2,541 feature submissions for this year's lineup. Twenty-two made the main competition. None were Indian.

The question this raises isn't whether India makes good films — it clearly does. It's whether the films India is investing the most money and attention in are the ones Cannes wants to show. The answer, consistently, is no. India's ₹200-crore tentpoles and franchise sequels are built for domestic and diaspora box offices, not for art-house festival circuits. The independent filmmakers who could compete at Cannes — the successors to Satyajit Ray, Mani Ratnam's art-house period, and Kapadia herself — operate on shoestring budgets with limited international distribution infrastructure.

## What Cannes 2026 Looked Like Without India

Park Chan-wook's jury awarded prizes to films from Romania, Russia, Germany, Spain, Poland, Japan, Belgium, and France. Nepal's *Elephants in the Fog* won the Un Certain Regard Jury Prize — a Nepali film achieving what no Indian film managed this year. Rwanda's *Ben'Imana* won the Caméra d'Or for best debut feature. The Critics' Week Grand Prize went to a French-Italian co-production.

The festival's overall slate was dominated by European and East Asian cinema, with strong representation from Latin America and Africa. India — the world's largest film producer by volume — was represented by a jury president, a fashion icon, a student short, an industry screening, and a 40-year-old restoration.

## The Uncomfortable Question

For NRI cinephiles, Cannes is the festival where Indian cinema's global ambitions get tested against the world's highest standards. This year, the test results are mixed. India's influence at Cannes has never been greater — Kapadia's jury presidency alone proves that. But influence and competition aren't the same thing.

Cannes 2027 will arrive in 12 months. India's film pipeline includes Rajamouli's *Varanasi*, Shah Rukh Khan's *King*, and whatever Kapadia herself makes next. The question isn't whether India can produce a Palme d'Or contender — it's whether the industry's economic incentives will ever align with the kind of filmmaking that Cannes rewards. Based on 2026, the answer is: not yet."""
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
