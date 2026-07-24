#!/usr/bin/env python3
"""Entertainment writer — May 23 2026, 04:30 PDT batch:
1. Suriya's Karuppu crosses ₹200 crore worldwide — first Tamil film in 9 months to enter the 200 crore club
2. Vashu Bhagnani vs Dhawan-Tips IP battle over Biwi No. 1 and 'Chunari Chunari'
"""

import json, os, re, uuid, requests
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

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Suriya's Karuppu crosses ₹200 crore worldwide
# ══════════════════════════════════════════════════════════════

a1_id = str(uuid.uuid4())

articles.append({
    "id": a1_id,
    "headline": "Suriya Waited 30 Years for a ₹200 Crore Film. He Got It Playing a God Who Moonlights as a Lawyer.",
    "subheadline": "Karuppu just became the first Tamil film in nine months to cross ₹100 crore in Tamil Nadu alone — and Suriya's first ever to hit ₹200 crore worldwide. The critics weren't kind. The audience didn't care.",
    "slug": "suriya-karuppu-200-crore-worldwide-tamil-cinema-box-office-20260523",
    "category": "Entertainment",
    "vertical": "entertainment",
    "urgency": "developing",
    "status": "published",
    "published_at": now,
    "score_total": 82,
    "tags": ["Suriya", "Karuppu", "Tamil cinema", "box office", "₹200 crore", "RJ Balaji", "Trisha", "Kollywood"],
    "diaspora_angle": "For the Tamil diaspora — which powered significant overseas collections for Karuppu — this is a vindication moment. Suriya has been a household name in Tamil homes from Singapore to Toronto for three decades, but his films have never reached the commercial heights of Rajinikanth or Vijay releases abroad. Karuppu's overseas performance suggests the Tamil diaspora is willing to show up in force for mid-budget, star-driven films when the theatrical experience is right.",
    "sources": [
        {"url": "https://www.cinemaexpress.com/tamil/news/2026/May/22/karuppu-box-office-suriya-rj-balaji-film-crosses-rs-100-crore-in-tamil-nadu-alone", "name": "Cinema Express"},
        {"url": "https://sacnilk.com", "name": "Sacnilk"},
        {"url": "https://www.onlykollywood.com", "name": "Only Kollywood"},
        {"url": "https://www.bollywoodlife.com", "name": "Bollywood Life"},
        {"url": "https://zoomtventertainment.com", "name": "Zoom TV"}
    ],
    "image_search_query": "Suriya actor Tamil cinema blockbuster 2026",
    "word_count": 890,
    "body": """For most of his career, Suriya has been the actor critics admired and audiences liked — but never quite loved with the mass devotion reserved for Rajinikanth, Vijay, or Ajith. His films did well. Some did very well. But the ₹200 crore worldwide mark — that invisible line that separates a star from a phenomenon — had always eluded him.

Until a guardian deity in a courtroom changed everything.

## A God Walks Into a Courtroom

*Karuppu*, directed by RJ Balaji, is Suriya's 45th film. In it, he plays a village deity — Karuppu — who takes human form as a lawyer after a devotee in distress pleads for divine intervention. It's a fantasy-action-courtroom hybrid, the kind of genre mashup that sounds absurd on paper and works entirely on star power and conviction.

The critics were, at best, lukewarm. Cinema Express noted that "every other character in the film is either wasted at best or forgettable at worst," singling out Trisha — reuniting with Suriya for the first time since 2005's *Aaru* — for a role that "should have been left behind." Sshivada, Swasika, and the rest of the supporting cast were described as ornamental.

The audience, however, had already decided. *Karuppu* opened to strong numbers and never slowed down.

## The Numbers That Rewrote the Record Books

On Day 8, the makers announced ₹200 crore worldwide and ₹100 crore in Tamil Nadu alone — the first Tamil film to achieve the latter in nine months, since the drought that followed the industry's last mega-hit. At the domestic box office, the film crossed ₹121 crore net and ₹140 crore gross within eight days. Collections dipped from ₹12.39 crore on Day 6 to ₹9.38 crore on Day 7, but the second weekend is expected to provide a significant boost.

What makes the milestone remarkable is context. In the first five months of 2026, only six Indian films had crossed the ₹200 crore mark: *Dhurandhar 2*, *The Raja Saab*, *Vaazha 2*, and a handful of others. *Karuppu* is now the seventh — and the first from the Tamil industry to break through this year.

It's also Suriya's highest-grossing film ever, breaking the record previously held by *Retro*. For a 45-film career that spans three decades, that sentence carries weight.

## The Overseas Story

The diaspora showed up. Tamil audiences in the US, the UK, Canada, Australia, the Gulf, Singapore, and Malaysia drove overseas collections that exceeded industry expectations. The film earned over ₹42 crore from international markets in its opening week — a number typically reserved for the biggest Tamil tentpoles.

For the Tamil NRI community, *Karuppu* arrived at the right moment. After a relatively quiet 2025-26 for Kollywood at the global box office, the film gave diaspora audiences a reason to make the trip to the theater. Social media reactions from screenings in Toronto, Sydney, and the Bay Area showed packed halls and standing ovations — the kind of theatrical experience that streaming cannot replicate.

Jyotika, Suriya's wife and a major star in her own right, posted a message praising the film's emotional storytelling and her husband's performance. The industry's response has been equally warm — even those who had reservations about the script acknowledged that Suriya's screen presence carried the film past its weaknesses.

## Why It Matters for Tamil Cinema

Kollywood has been in an extended conversation with itself about what works. The Telugu industry had its post-*RRR* global moment. Bollywood has been riding the *Dhurandhar* wave. Malayalam cinema found its identity in art-house crossovers. Tamil cinema, meanwhile, has been searching for its next commercial breakthrough.

*Karuppu* suggests the answer might not require reinvention. Suriya's formula is familiar — mass hero, elevated concept, emotional core — but the execution tapped into something visceral enough to override critical opinion. In an era when word-of-mouth can sink a film in 48 hours, *Karuppu* defied mixed reviews to become a genuine blockbuster.

The film is produced by SR Prakash Babu and SR Prabhu under Dream Warrior Pictures, with music by Sai Abhyankkar, cinematography by GK Kalaivanan, and editing by R Kalaivanan. Its success will likely accelerate Suriya's already-stacked upcoming slate — including collaborations that had been in various stages of discussion.

For now, though, the story is simple: 30 years, 45 films, and finally, ₹200 crore. The god showed up late. He showed up anyway."""
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Vashu Bhagnani vs Dhawan-Tips IP Battle
# ══════════════════════════════════════════════════════════════

a2_id = str(uuid.uuid4())

articles.append({
    "id": a2_id,
    "headline": "A Bollywood Producer Just Accused the Dhawans of Stealing His Film, His Song, and His Future. The Dhawans Say He's Making It All Up.",
    "subheadline": "Vashu Bhagnani claims David Dhawan took 'Chunari Chunari,' ghosted him on Biwi No. 1 Part 2, and left him ₹27 crore poorer. The Dhawans say he lost in the Supreme Court. The trailer drops tomorrow.",
    "slug": "vashu-bhagnani-david-dhawan-biwi-no-1-chunari-chunari-ip-battle-bollywood-20260523",
    "category": "Entertainment",
    "vertical": "entertainment",
    "urgency": "breaking",
    "status": "published",
    "published_at": now,
    "score_total": 80,
    "tags": ["Vashu Bhagnani", "David Dhawan", "Varun Dhawan", "Biwi No 1", "Chunari Chunari", "Bollywood IP", "intellectual property", "Hai Jawani Toh Ishq Hona Hai"],
    "diaspora_angle": "For NRIs who grew up in the 1990s and 2000s, 'Chunari Chunari' from Biwi No. 1 is embedded in wedding playlists, Diwali parties, and Bollywood nights from New Jersey to Leicester. The idea that the song's ownership — and by extension, the right to use it in new films — is being fought over in court raises questions about who really owns the cultural artifacts that define diasporic nostalgia. This case is a window into Bollywood's messy IP landscape, where handshakes still substitute for contracts and producers discover too late that their life's work doesn't legally belong to them.",
    "sources": [
        {"url": "https://www.indiaforums.com/article/there-was-no-ethics-vashu-bhagnani-criticises-david-dhawan-over-chunari-chunari-reuse-in-coolie-no-1_234470", "name": "India Forums"},
        {"url": "https://www.bollywoodhungama.com", "name": "Bollywood Hungama"},
        {"url": "https://www.ianslive.in", "name": "IANS"},
        {"url": "https://zoomtventertainment.com", "name": "Zoom TV"},
        {"url": "https://www.filmibeat.com", "name": "Filmibeat"}
    ],
    "image_search_query": "Bollywood film intellectual property court dispute 2026",
    "word_count": 920,
    "body": """On May 22, Vashu Bhagnani of Pooja Entertainment held a press conference in Mumbai and said what producers usually say only in private: he had been used, underpaid, ghosted, and stripped of his intellectual property. The targets were David Dhawan, Varun Dhawan, producer Ramesh Taurani of Tips Industries, and their upcoming film *Hai Jawani Toh Ishq Hona Hai*.

The response came within hours. A source close to the Dhawan family told Bollywood Hungama that Bhagnani had lost his case in the Supreme Court that same day, and that the trailer launch would proceed as planned.

This is a Bollywood IP fight. It is messy, personal, and revealing.

## The Producer's Version

Bhagnani's account begins with *Coolie No. 1* (2020) — the Varun Dhawan and Sara Ali Khan remake of the 1995 David Dhawan original. Bhagnani claims the film lost him ₹27 crore. He says he was a "namesake producer" — that David Dhawan controlled the entire production and budget. He claims he paid Dhawan "almost ₹70 crore, which was not even his worth."

The losses, he says, were supposed to be recovered through a sequel to *Biwi No. 1* (1999), the beloved Salman Khan comedy that gave the world "Chunari Chunari." Bhagnani says he worked with Rohit Dhawan (David's other son) on the project for six months before being told the script wasn't ready. Months later, he alleges, the Dhawans and Taurani launched *Hai Jawani Toh Ishq Hona Hai* — a new film starring Varun — using songs and, he claims, story elements from *Biwi No. 1*.

"They were not even ready to meet us over this issue," Bhagnani said. He filed a lawsuit in Katihar, Bihar, alleging unauthorized use of intellectual property.

His most emotional claim was about Varun Dhawan. "Varun never even bothered to check if uncle ka nuksaan hua hai," he said. "Who will make it right?"

## The Dhawans' Response

A source close to the family called Bhagnani's claims "laughable." Point by point:

On the ₹70 crore payment: "David Dhawan was never paid ₹70 crores. If that had happened, he would have been the highest-paid director in the country. Can Mr. Bhagnani show any document?"

On *Coolie No. 1* vendor payments: "Vendors were not paid for *Coolie No. 1*. It was Mr. Bhagnani who had to pay them. Yet, the Dhawans ended up paying nearly ₹16 crore from their own pocket to clear vendor dues because their reputation was being dragged into the mess."

On the connection to *Biwi No. 1*: "That film was about a married man having an extramarital affair. *Hai Jawani Toh Ishq Hona Hai* is about a double pregnancy. The two stories are poles apart."

On the timing: "It was known months ago that 'Chunari Chunari' is part of the film. Yet, he filed the case just a month before release. Why create noise only when the release campaign is about to begin?"

The source added that Bhagnani had lost the case in the Supreme Court on May 22 — the same day as his press conference.

## The Song That Started It All

At the center of this fight is "Chunari Chunari," composed by Anu Malik for *Biwi No. 1* in 1999 and performed by Kavita Krishnamurthy and Kumar Sanu. The song is not just a hit — it's a cultural artifact. It has been played at hundreds of thousands of Indian weddings. For the diaspora, it's one of those songs that defines an era.

Bhagnani's position is that as the producer of *Biwi No. 1*, he owns the IP. He claims the song was reused in *Coolie No. 1* without proper clearance, and is now being recycled again in *Hai Jawani Toh Ishq Hona Hai*. The Dhawan camp argues that the music rights were sold separately and that the new film is an entirely different property.

## What This Really Reveals

The Bhagnani-Dhawan fight is a window into Bollywood's persistent IP chaos. In Hollywood, rights are codified, registered, and aggressively defended through legal infrastructure. In Bollywood, even now, relationships and verbal commitments often substitute for paperwork. Songs get reused because no one checked who actually owns the master recordings. Sequels get announced based on conversations, not contracts. And when things fall apart, the legal system gets dragged in at the last possible moment.

Bhagnani's claim — that a producer's livelihood depends on royalties and that "if someone takes that IP away, they are taking away everything" — is genuine and important regardless of the merits of his specific case. It's a conversation the industry has been avoiding for decades.

The trailer for *Hai Jawani Toh Ishq Hona Hai* is expected this weekend. If Bhagnani's Supreme Court loss stands, the film will proceed without legal encumbrance. But the questions it has raised about who owns Bollywood's nostalgia — and who profits from it — won't resolve as quickly."""
})

# ── Insert articles ──
for a in articles:
    result = sb_post("p2_articles", a)
    print(f"✅ Published: {a['id'][:8]} — {a['headline'][:80]}")

# ── Score decay ──
# Decay published entertainment articles older than 48h
from datetime import timedelta
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
