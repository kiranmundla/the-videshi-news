#!/usr/bin/env python3
"""Entertainment writer — May 23 2026 late-night batch (00:30 PDT):
1. Supriya Pathak's directorial debut "Our Story" at Cannes
2. FTII's "Shadows of the Moonless Nights" — one of 2 Indian films in Cannes official selection
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
# ARTICLE 1: Supriya Pathak's "Our Story" at Cannes
# ══════════════════════════════════════════════════════════════

a1_id = str(uuid.uuid4())

articles.append({
    "id": a1_id,
    "headline": "Supriya Pathak Just Announced Her Directorial Debut at Cannes. It's About Three Generations of Women in Her Own Family.",
    "subheadline": "The veteran actress behind Hansa from Khichdi and Ram-Leela's Dhankor Baa is making her first film — an Indo-Australian co-production co-written with her daughter Sanah Kapur. It's personal, it's cross-continental, and it already has distribution in Canada.",
    "slug": "supriya-pathak-our-story-cannes-directorial-debut-indo-australian-20260523",
    "category": "Entertainment",
    "vertical": "entertainment",
    "urgency": "developing",
    "status": "published",
    "published_at": now,
    "score_total": 72,
    "tags": ["Supriya Pathak", "Our Story", "Cannes 2026", "Sanah Kapur", "Indo-Australian cinema", "Dina Pathak"],
    "diaspora_angle": "Our Story is an Indo-Australian co-production with distribution already secured in Canada, Australia, and New Zealand through Forum Films. The film explores themes of memory, identity, and womanhood across cultures — and its Toronto International Film Festival market debut in September will be a direct touchpoint for the NRI film community.",
    "sources": [
        {"url": "https://www.zoomtventertainment.com/bollywood/supriya-pathak-kapur-directorial-debut-our-story-cannes-article-154371273", "name": "Zoom TV Entertainment"},
        {"url": "https://www.bombaytimes.com/entertainment/supriya-pathak-kapur-directorial-debut-cannes-2026", "name": "Bombay Times"},
        {"url": "https://www.latestly.com/entertainment/supriya-pathak-our-story-directorial-debut", "name": "LatestLY"},
        {"url": "https://cliqindia.com/entertainment/supriya-pathak-our-story-directorial-debut", "name": "Cliq India"}
    ],
    "image_search_query": "Supriya Pathak Cannes 2026 Our Story directorial debut",
    "image_entities": ["Supriya Pathak", "Sanah Kapur", "Cannes Film Festival 2026"],
    "image_must_show": "Supriya Pathak at Cannes 2026 or a still/poster related to Our Story",
    "word_count": 750,
    "body": """There are actors who retire into quiet dignity. There are actors who keep taking roles until they become furniture. And then there is Supriya Pathak Kapur, who after four decades of making other directors' visions unforgettable, has decided — at 63 — to finally tell her own story. Literally.

*Our Story*, announced at the 79th Cannes Film Festival this week, is Supriya Pathak's directorial debut. It is a loosely biographical feature about three generations of women in the Pathak Kapur family: her late mother, the legendary Dina Pathak; herself; and her daughter, Sanah Kapur. Sanah co-wrote the screenplay. Son Ruhaan Kapur is the associate director and creative producer. This is, in the most complete sense, a family film — made by the family, about the family, with the family.

## A Story That Spans Continents

What makes *Our Story* particularly interesting for diaspora audiences is its structure. This is not a Bollywood production. It is an Indo-Australian co-production, developed under Supriya's banner Rabasusah and the Australian company Films and Casting Temple. The lead producer is Anupam Sharma, an Australian-Indian filmmaker who previously directed *UnIndian* (2015) — the Brett Lee-Tannishtha Chatterjee romance that was itself a cross-cultural experiment.

Forum Films has already secured theatrical distribution rights in Australia, New Zealand, and Canada. The film will make its market debut at the Toronto International Film Festival in September 2026.

For NRIs in Canada, this means *Our Story* will likely be one of the first Indian indie films to get proper theatrical distribution in their market this year. For the broader diaspora, the Indo-Australian angle adds a dimension that purely Indian productions rarely have: the experience of being Indian across borders, of carrying memory and identity through migration.

## Who Is Dina Pathak?

If you are under 40 and grew up outside India, you may not know Dina Pathak's name — and that is part of what makes this project significant. Dina Pathak was one of Indian cinema and theatre's most respected character actresses, known for roles in *Gol Maal* (1979), *Umrao Jaan* (1981), and *Mirch Masala* (1987). She was a recipient of the Sangeet Natak Akademi Award, India's highest recognition for performing arts. She passed away in 2002.

For Supriya, this film is not just a tribute. "It reflects themes of memory, family, womanhood, and emotional legacy that have shaped our identities," she said at the Cannes announcement. The film traces how artistic temperament, emotional patterns, and the particular burdens of being a woman in Indian creative life pass from grandmother to mother to daughter — sometimes through love, sometimes through absence, sometimes through the roles they played on screen and the ones they could not play in life.

## Sanah Kapur: The Third Voice

Sanah Kapur — who appeared in *Shaandaar*, *Ramprasad Ki Tehrvi*, and *Saroj Ka Rishta* — is not just the third generation of the story but its co-author. Having her write alongside her mother creates an unusual dynamic: this is a film where the subject is also the writer, and where the personal and the fictional will blur by design.

For anyone who has watched Supriya Pathak bring impossible depth to characters like Hansa in *Khichdi* (India's most beloved sitcom matriarch) or Dhankor Baa in *Goliyon Ki Raasleela Ram-Leela* (one of the most terrifying mothers-in-law in Hindi cinema), the idea of her turning the lens on her own mother-daughter dynamics is irresistible.

## Why NRIs Should Pay Attention

India sends dozens of projects to Cannes every year — most of them seeking distribution, a few seeking validation, many seeking both. What sets *Our Story* apart is that it is not looking for a buyer. It already has one. The distribution in Canada, Australia, and New Zealand is locked. The Toronto market debut is scheduled. The Indo-Australian production structure means the film is built for international audiences from the ground up.

This matters because NRI film audiences have been asking for years: where are the Indian films that speak to our experience of straddling two worlds? *Our Story* — about a family whose creative legacy stretches across borders and generations — may be exactly that.

Supriya Pathak has spent 40 years making other people's stories resonate. It is about time she told her own."""
})


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: "Shadows of the Moonless Nights" — FTII at Cannes
# ══════════════════════════════════════════════════════════════

a2_id = str(uuid.uuid4())

articles.append({
    "id": a2_id,
    "headline": "An FTII Student Film Just Became One of Only Two Indian Entries in Cannes' Official Selection. It's 24 Minutes Long and in Punjabi.",
    "subheadline": "Mehar Malhotra's 'Shadows of the Moonless Nights' — about a factory worker who cannot sleep — was chosen from 2,750 entries worldwide for La Cinef. The director thought the selection email was spam.",
    "slug": "shadows-moonless-nights-ftii-cannes-la-cinef-punjabi-mehar-malhotra-20260523",
    "category": "Entertainment",
    "vertical": "entertainment",
    "urgency": "developing",
    "status": "published",
    "published_at": now,
    "score_total": 71,
    "tags": ["Cannes 2026", "FTII", "La Cinef", "Mehar Malhotra", "Indian cinema", "Punjabi film", "student film"],
    "diaspora_angle": "FTII is the film school that shaped the careers of directors NRIs grew up watching — from Adoor Gopalakrishnan to Rajkumar Hirani. A Punjabi-language student film about night-shift labour making it to Cannes' official selection represents the kind of Indian cinema the diaspora rarely gets to see — far from Bollywood spectacle, rooted in the working-class India many NRIs left behind.",
    "sources": [
        {"url": "https://www.hollywoodreporterindia.com/thr-video/thr-at-cannes/the-team-behind-shadows-of-the-moonless-nights-on-their-cannes-selection-thr-india-at-cannes-2026", "name": "The Hollywood Reporter India"},
        {"url": "https://en.wikipedia.org/wiki/2026_Cannes_Film_Festival", "name": "Wikipedia"}
    ],
    "image_search_query": "Shadows of the Moonless Nights Cannes 2026 FTII film",
    "image_entities": ["Mehar Malhotra", "FTII Pune", "Cannes Film Festival La Cinef"],
    "image_must_show": "A moody still of a factory worker at night or FTII/Cannes branding",
    "word_count": 730,
    "body": """While India's Cannes 2026 coverage was dominated by red carpet fashion, a 24-minute Punjabi-language film about a factory worker who cannot sleep quietly became the most significant Indian entry at the festival.

*Shadows of the Moonless Nights*, directed by Mehar Malhotra, was one of only two Indian films selected for official screening at the 79th Festival de Cannes — chosen from 2,750 entries worldwide for the prestigious La Cinef section, which showcases work from film schools around the globe. Malhotra made the film as her final project at FTII (Film and Television Institute of India) in Pune.

When the selection email arrived, she thought it was spam.

## A Film About the Workers Who Never Rest

The premise is deceptively simple: Rajan, a young Punjabi factory worker, is trapped in grinding night shifts and a volatile home life. He drifts through sleeplessness, searching for rest that never arrives. The character has almost no dialogue — his story is told through routine, silence, and an oppressive soundscape that includes a haunting factory tape sound that plays inside his head even when the machines have stopped.

Malhotra has spoken about the film's origins in personal memory: watching her own *maasi* (aunt) work brutal call-centre night shifts when she was a child, returning home hollow-eyed to a one-BHK apartment too small for sleep. That image — of a woman who worked all night and could not rest during the day because there was no space, no silence, no permission — became the seed of *Shadows*.

## The Making of a Cannes Selection

Lead actor Prayrak Mehta built the character of Rajan around routine rather than emotion — a deliberate choice that gives the film a documentary-like texture. Nikita Grover, who served as both casting director and plays Rajan's sister Anju, recalled learning about the Cannes selection at a party: "Naina and I were too drunk to register it properly."

The most discussed sequence in the film — a confrontation between Rajan and Anju — was shot largely on instinct in a cramped space, in what was essentially a single take. A Sony Venice camera and a cinematographer working miracles in tight quarters produced what early viewers have called one of the most visceral scenes in any Indian film at Cannes this year.

Malhotra and sound designer Sai Sanjay scripted the entire soundscape before a single frame was shot — a method inspired by Argentine filmmaker Lucrecia Martel, whose work treats sound as a narrative instrument rather than atmospheric decoration.

## Why This Matters for Indian Cinema Abroad

La Cinef is not a sidebar or a market screening. It is an official section of the Cannes Film Festival — the same festival where the Palme d'Or is awarded. Being selected from 2,750 entries places *Shadows of the Moonless Nights* in a category of recognition that most Indian films, regardless of budget, never achieve.

And yet, the film was made on a student budget. At FTII. In Punjabi. About a factory worker.

This is the India that does not appear in Bollywood trailers or streaming platform hype cycles. It is the India of night shifts, cramped housing, and the slow erosion of the body by labour. For the Indian diaspora, many of whom are one or two generations removed from exactly this kind of life, the film represents a mirror they rarely get to look into — not the India of *Dhurandhar* and NRI weekend screenings, but the India of the people who made the journey to Ludhiana and Surat and Coimbatore before some of their children made the journey to New York and London and Toronto.

## FTII's Legacy and What Comes Next

FTII has shaped some of Indian cinema's most important directors — Adoor Gopalakrishnan, Mani Kaul, John Abraham (the director, not the actor), Sanjay Leela Bhansali, Rajkumar Hirani. The institute has been in the news more often for controversies (the 2015 student strike, funding disputes) than for its artistic output. *Shadows of the Moonless Nights* is a reminder that the school continues to produce filmmakers who think about cinema differently than the industry does.

Malhotra, in her Cannes conversation with Anupama Chopra, ended with a note that lingers: "India is a nation of born storytellers. As long as human civilisation exists, people will always find a way to come together and celebrate the stories that matter most."

A 24-minute film about a man who cannot sleep. Selected by Cannes from 2,750 entries. The stories that matter most do not always come with trailers."""
})


# ══════════════════════════════════════════════════════════════
# INSERT ARTICLES
# ══════════════════════════════════════════════════════════════

print(f"\n📝 Inserting {len(articles)} entertainment articles...")

for i, art in enumerate(articles):
    try:
        result = sb_post("p2_articles", art)
        title_short = art["headline"][:70]
        print(f"  ✅ Article {i+1}: {title_short}...")
    except Exception as e:
        print(f"  ❌ Article {i+1} failed: {e}")

print(f"\n✅ Entertainment writer complete!")
print(f"  Article 1 ({articles[0]['id'][:8]}): {articles[0]['headline'][:60]}")
print(f"  Article 2 ({articles[1]['id'][:8]}): {articles[1]['headline'][:60]}")
