#!/usr/bin/env python3
"""Entertainment writer — May 23 2026, 06:30 PDT batch:
1. Sonakshi Sinha + Jyotika's 'System' on Amazon Prime — courtroom thriller getting excellent reviews
   (Jyotika's husband Suriya has Karuppu at ₹200Cr simultaneously — rare husband-wife domination week)
2. Score decay for old entertainment articles
"""

import json, os, re, uuid, requests
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
# ARTICLE 1: System — Sonakshi Sinha + Jyotika courtroom drama
# ══════════════════════════════════════════════════════════════

a1_id = str(uuid.uuid4())

articles.append({
    "id": a1_id,
    "headline": "Sonakshi Sinha and Jyotika Just Made a Legal Thriller Together. It's Being Called One of the Best Hindi OTT Films of the Year.",
    "subheadline": "While Jyotika's husband Suriya is crossing ₹200 crore at the box office with Karuppu, she's quietly dominating Amazon Prime Video with a courtroom drama about two women dismantling a broken system from the inside.",
    "slug": "system-sonakshi-sinha-jyotika-amazon-prime-courtroom-thriller-review-20260523",
    "category": "Entertainment",
    "vertical": "entertainment",
    "urgency": "standard",
    "status": "published",
    "published_at": now,
    "score_total": 78,
    "tags": ["System", "Sonakshi Sinha", "Jyotika", "Amazon Prime Video", "courtroom drama", "Ashwiny Iyer Tiwari", "OTT", "streaming", "legal thriller"],
    "diaspora_angle": "For NRI audiences who grew up on Jyotika's Tamil films in the 2000s and Sonakshi Sinha's Bollywood blockbusters, System is a rare crossover event: a Hindi-language film starring one of South India's most beloved actresses alongside a Bollywood star, streaming globally on Amazon Prime Video. It's also the kind of film that diaspora audiences increasingly prefer — a two-hour, tightly written legal drama available on demand, no multiplex required. With Jyotika's husband Suriya simultaneously dominating the box office with Karuppu (₹200 crore worldwide), this is the rare week where one Tamil cinema couple is winning in both theaters and streaming, across languages.",
    "sources": [
        {"url": "https://www.iwmbuzz.com/digital/editorial-digital/system-review-a-thought-provoking-legal-drama-packed-with-emotions-dilemmas-twists/2026/05/22", "name": "IWMBuzz"},
        {"url": "https://www.zoomtventertainment.com", "name": "Zoom TV"},
        {"url": "https://popnewsblend.com", "name": "PopNewsBlend"},
        {"url": "https://www.filmfare.com", "name": "Filmfare"},
        {"url": "https://www.bollywoodhungama.com", "name": "Bollywood Hungama"}
    ],
    "image_search_query": "courtroom drama Indian film gavel law justice 2026",
    "word_count": 820,
    "body": """There's something quietly thrilling about the timing. On the same week that Suriya's *Karuppu* crossed ₹200 crore worldwide to become his biggest-ever box office hit, his wife Jyotika dropped a Hindi-language legal thriller on Amazon Prime Video that critics are calling one of the best OTT films of the year.

*System*, directed by Ashwiny Iyer Tiwari (*Bareilly Ki Barfi*, *Nil Battey Sannata*), premiered on May 22 and stars Sonakshi Sinha as a young lawyer and Jyotika as a courtroom stenographer. It's a two-hour film — not a series — and it's available globally. For anyone who's been waiting for a Hindi film that respects both its audience's intelligence and its runtime, this is it.

## Two Women, One Courtroom, No Easy Answers

The setup is deceptively simple. Neha Rajvansh (Sonakshi Sinha) is the daughter of a celebrated advocate, Ravi (Ashutosh Gowariker, in a rare acting role). But Ravi refuses to let nepotism define his daughter's career. His condition: win 10 cases on your own, without his name or his connections. Only then can they work together.

Enter Sarika (Jyotika), a courtroom stenographer who single-handedly supports her wheelchair-bound husband while navigating the unglamorous machinery of the Indian legal system. She has no pedigree, no connections, and no illusions about how the system works — because she's watched it from the inside for years.

Neha recruits Sarika to help build her cases. They form an unlikely alliance — the privileged daughter learning to fight without her father's armor, and the working-class observer who knows where every institutional skeleton is buried. Together, they start winning.

Then comes the case that pits Neha against her own father. The film doesn't flinch.

## What the Critics Are Saying

The early reviews have been strikingly positive. IWMBuzz rated it 3.5 out of 5, calling it "a thought-provoking legal drama packed with emotions, dilemmas, and twists." PopNewsBlend went further, calling it "one of the best Hindi OTT films of the year." Zoom TV praised the performances, noting that Jyotika "shines as Sarika, effectively conveying the character's quiet determination and the burdens she carries."

The consensus is clear: Ashwiny Iyer Tiwari has crafted something that feels genuinely different from Bollywood's usual courtroom fare. There are no theatrics, no dramatic objections screamed at a judge. Instead, the film builds its tension through the moral compromises both women are forced to make — and the institutional rot they discover once they start looking too closely.

Sonakshi Sinha delivers what critics are calling one of her best performances, channeling ambition and vulnerability in equal measure. But it's Jyotika who emerges as the film's quiet powerhouse. Her naturalistic acting style — honed across two decades of Tamil cinema — brings an understated intensity that Bollywood's courtroom dramas rarely achieve.

## A Remarkable Coincidence — or Something More

The timing is extraordinary. Jyotika's husband Suriya has been the talk of Indian cinema this week as *Karuppu* crossed ₹200 crore worldwide — his first film to reach that milestone, after 30 years and 45 films. Jyotika herself posted a public message praising both the film and Suriya's performance.

Now, on the same weekend, she's the co-lead of a film that's generating its own critical acclaim on the biggest global streaming platform. It's the kind of week that rarely happens in Indian cinema: a married couple simultaneously dominating theaters and streaming, in different languages, in entirely different genres.

Jyotika has been on a quiet but deliberate second-act career path since returning to acting in 2019 after a lengthy break to raise her children. She's chosen roles that lean into the kind of grounded, socially conscious storytelling that Tamil cinema has always done well — and *System* marks her most prominent Hindi-language role to date.

## What NRI Audiences Should Know

*System* is available globally on Amazon Prime Video as a single feature film (not a series — no episodes, no cliffhangers, just a clean two-hour watch). It's available in Hindi with subtitles.

For diaspora viewers who've been frustrated with the quality of mainstream Bollywood's OTT output — the rushed web series, the bloated episodes, the stories stretched thin across eight installments — *System* is a corrective. It's tight, well-acted, and treats its subject matter with the seriousness it deserves.

It's also a film that resonates with anyone who's navigated India's institutional systems — legal, bureaucratic, or otherwise — and wondered whether the system was designed to be broken, or simply broke along the way. For NRIs who return to India and encounter that particular frustration, *System* will feel uncomfortably familiar.

Ashwiny Iyer Tiwari continues to prove that she's one of Hindi cinema's most reliable directors when it comes to films about ordinary people fighting extraordinary systems. *Bareilly Ki Barfi* was a quiet masterpiece. *Nil Battey Sannata* was a gut-punch about educational inequality. *System* fits squarely in that lineage — and it might be her most ambitious film yet."""
})

# ── Insert articles ──
for a in articles:
    result = sb_post("p2_articles", a)
    print(f"✅ Published: {a['id'][:8]} — {a['headline'][:80]}")

# ── Score decay ──
cutoff = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
decay_r = requests.get(
    f"{SB_URL}/rest/v1/p2_articles?status=eq.published&category=eq.Entertainment&published_at=lt.{cutoff}&score_total=gt.30&select=id,score_total&limit=200",
    headers=HEADERS, timeout=30
)
decayed = 0
for art in decay_r.json():
    new_score = max(30, int(art["score_total"] * 0.95))
    if new_score < art["score_total"]:
        sb_patch("p2_articles", f"id=eq.{art['id']}", {"score_total": new_score})
        decayed += 1
print(f"📉 Score decay: {decayed} articles decayed (of {len(decay_r.json())} eligible)")

print("\n✅ Entertainment writer batch complete.")
