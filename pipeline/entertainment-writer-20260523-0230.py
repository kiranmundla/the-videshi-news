#!/usr/bin/env python3
"""Entertainment writer — May 23 2026, 02:30 PDT batch:
1. Payal Kapadia: From Grand Prix Winner to Cannes Critics' Week Jury President
2. Nepal's "Elephants in the Fog" — First Nepali Film to Win at Cannes
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
# ARTICLE 1: Payal Kapadia — Cannes Critics' Week Jury President
# ══════════════════════════════════════════════════════════════

a1_id = str(uuid.uuid4())

articles.append({
    "id": a1_id,
    "headline": "Two Years Ago, Payal Kapadia Won the Grand Prix at Cannes. This Year, She Ran the Jury.",
    "subheadline": "The Indian filmmaker behind 'All We Imagine as Light' became the first Indian to preside over a Cannes jury section — Critics' Week — and handed out prizes to debut filmmakers from France, Spain, and Kosovo.",
    "slug": "payal-kapadia-cannes-2026-critics-week-jury-president-indian-cinema-20260523",
    "category": "Entertainment",
    "vertical": "entertainment",
    "urgency": "developing",
    "status": "published",
    "published_at": now,
    "score_total": 78,
    "tags": ["Payal Kapadia", "Cannes 2026", "Critics' Week", "All We Imagine as Light", "Indian cinema", "FTII"],
    "diaspora_angle": "Payal Kapadia's trajectory — from FTII student protests to Grand Prix winner to Cannes jury president — represents the kind of Indian creative excellence that diaspora communities have championed but rarely seen recognised at this level. Her presence in the jury chair, not just in the audience, signals a structural shift in how Indian filmmakers are positioned in global cinema's power hierarchy.",
    "sources": [
        {"url": "https://www.festival-cannes.com", "name": "Festival de Cannes"},
        {"url": "https://www.screendaily.com", "name": "Screen Daily"},
        {"url": "https://www.wownews24x7.com/payal-kapadia-steps-into-spotlight-as-cannes-critics-week-jury-head", "name": "WowNews"},
        {"url": "https://www.yourstory.com", "name": "YourStory"}
    ],
    "image_search_query": "Payal Kapadia filmmaker Cannes 2026",
    "word_count": 720,
    "body": """In 2021, Payal Kapadia won the Golden Eye at Cannes for her documentary *A Night of Knowing Nothing*, a film she made about love, protest, and institutional suffocation at the Film and Television Institute of India. In 2024, she returned with *All We Imagine as Light* and won the Grand Prix — the second-highest honour at the festival — becoming the first Indian filmmaker to compete in the main Competition section in 30 years. The film received an eight-minute standing ovation.

In May 2026, Kapadia walked the Croisette again. But this time, she wasn't there to be judged. She was the one doing the judging.

## The First Indian to Chair a Cannes Jury

Kapadia was named President of the Critics' Week jury at the 79th Cannes Film Festival — the first Indian filmmaker to preside over any jury section at Cannes. Critics' Week, or *Semaine de la Critique*, is one of the festival's most important parallel sections, dedicated exclusively to debut and second feature films. It is where careers begin.

For five days, Kapadia and her four fellow jurors — actor Théodore Pellerin, producer Ama Ampadu, French singer Oklou, and Thai film critic Donsaron Kovitvanitcha — watched seven debut features and seven short films competing for the section's prizes.

## What She Awarded

On May 20, the Critics' Week jury announced its winners. Marine Atlan's *La Gradiva*, a film about French teenagers confronting the ancient dead during a school trip to Naples, took the AMI Paris Grand Prix — the section's top prize. The Rising Star Award went to Catalan actress Aina Clotet for her debut film *Alive*. The SACD screenwriting prize went to Blerta Basholli and Nicole Borgeat for *Dua*, while the Canal+ short film award went to Berthold Wahjudi's *"Vaterland" or a Bule Named Yanto*.

These are not household names. That's the point. Critics' Week exists to find filmmakers before the world knows them. And this year, it was an Indian filmmaker deciding who those future voices would be.

## Why This Matters for the Diaspora

Kapadia's ascent from FTII graduate to Cannes jury president is not just a personal milestone — it represents a structural shift in how Indian cinema is positioned globally. For decades, India's relationship with Cannes was defined by either spectacle (Aishwarya Rai on the red carpet, India as "Country of Honour" in 2022) or absence (no Indian film in the main Competition between 1994 and 2024). Kapadia has changed the calculus entirely.

Her trajectory matters to NRIs because it validates a different model of Indian success — one built not on commercial box office muscle but on artistic ambition, institutional struggle, and international peer recognition. She was arrested during the 2015 FTII student protests. She spent years making documentaries that no major Indian distributor would have touched. And now she sits in the room where global cinema's gatekeepers sit.

*All We Imagine as Light*, the film that made this possible, is itself a story about migration — about Malayali nurses displaced in Mumbai, about the distance between where you come from and where you end up. It resonated with diaspora audiences who saw their own uprootedness reflected in Kapadia's poetic, unhurried frames.

## What Comes Next

Kapadia is reportedly working on a new film, the third in a planned triptych of Mumbai-based stories. She has spoken about wanting to continue blending fiction and documentary styles — the approach that has made her work distinctive at a festival that has seen everything.

For now, the fact that stands: in 2026, when Cannes needed someone to identify the future of cinema, they asked an Indian filmmaker. That has never happened before.

And for the NRI film community — the one that has spent years arguing that Indian cinema deserves more than a "foreign language" category at the Oscars, more than a "Bollywood pavilion" at Cannes — Payal Kapadia's jury presidency is evidence that the argument is being heard. Not in words. In chairs."""
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Nepal's "Elephants in the Fog" wins at Cannes
# ══════════════════════════════════════════════════════════════

a2_id = str(uuid.uuid4())

articles.append({
    "id": a2_id,
    "headline": "A Nepali Film About Trans Women Just Won at Cannes. It's the First Time Nepal Has Ever Won Anything There.",
    "subheadline": "Abinash Bikram Shah's 'Elephants in the Fog' took the Un Certain Regard Jury Prize and the Best Sound Creation award — making it the most decorated South Asian debut feature at this year's festival.",
    "slug": "nepal-elephants-in-the-fog-cannes-2026-un-certain-regard-jury-prize-abinash-bikram-shah-20260523",
    "category": "Entertainment",
    "vertical": "entertainment",
    "urgency": "developing",
    "status": "published",
    "published_at": now,
    "score_total": 76,
    "tags": ["Elephants in the Fog", "Cannes 2026", "Nepal cinema", "Abinash Bikram Shah", "Un Certain Regard", "Kinnar", "South Asian cinema"],
    "diaspora_angle": "The Kinnar/hijra community depicted in the film is a shared cultural reality across South Asia — in India, Nepal, Bangladesh, and Pakistan. For Indian diaspora audiences, this film's recognition at Cannes validates narratives about South Asian marginalised communities that mainstream Bollywood has largely ignored or caricatured. It also signals that South Asian cinema beyond India is finding its own voice on the global stage.",
    "sources": [
        {"url": "https://aihustlehq.com/nepals-elephants-in-the-fog-creates-history-at-cannes-wins-un-certain-regard-jury-prize/", "name": "AiHustleHQ"},
        {"url": "https://en.wikipedia.org/wiki/Elephants_in_the_Fog", "name": "Wikipedia"},
        {"url": "https://www.festival-cannes.com", "name": "Festival de Cannes"},
        {"url": "https://amilcarmagazine.com", "name": "Amilcar Magazine"},
        {"url": "https://cosmosjourney.com", "name": "Cosmos Journey"}
    ],
    "image_search_query": "Nepal Cannes film festival 2026 Elephants in the Fog",
    "word_count": 700,
    "body": """When Abinash Bikram Shah walked onto the stage at the Palais des Festivals on May 22 to accept the Un Certain Regard Jury Prize, he carried with him the weight of a country that had never won anything at Cannes before. Behind him stood his cast — mostly non-professional actors drawn from Nepal's Kinnar community, the people whose lives had become the film.

"For so long, the lives of Pirati and her daughters have been kept invisible," Shah said in his acceptance speech. "By bringing our story here, we have pulled those margins into the light. We have made the invisible visible."

## The Film

*Elephants in the Fog* is set in Thori, a forested village in Nepal's southern Terai plains where wild elephants drift through morning mist and the Kinnar community — transgender women known as hijras across the subcontinent — live on the margins of village life. The story follows Pirati, a matriarch torn between her dream of escaping to live with the man she loves and her duty to investigate when one of her community's daughters goes missing.

It is Shah's debut feature film, shot with a cast that includes Pushpa Thing Lama, Deepika Yadav, Jasmine Bishwakarma, and Shanti Giri. The film is a co-production between Nepali companies Underground Talkies Nepal and Jayanthi Creations, with partners from France, Germany, Brazil, and Norway.

## Two Prizes, Not One

The Un Certain Regard Jury Prize would have been enough to make history. But *Elephants in the Fog* also won the Prix de la Meilleure Création Sonore — the Best Sound Creation award at Cannes — for its immersive audio design. The jury, which included French singer Barbara Pravi and composer Laurent Couson, praised the film's ability to make sound a character in its own right. The fog, the elephants, the forest — you don't just see them. You hear them closing in.

It was also the first Nepali film ever selected for Un Certain Regard, the section that runs parallel to the main Competition and is dedicated to distinctive, formally adventurous filmmaking. Recent Un Certain Regard winners have included films from Romania, Kenya, and Japan.

## Why Indian Audiences Should Care

The Kinnar community depicted in *Elephants in the Fog* is not a Nepali phenomenon. Hijras — transgender women who live in organised communities under a matriarchal structure — are found across India, Bangladesh, and Pakistan. They have been recognised by India's Supreme Court as a third gender since 2014. They appear in Bollywood, occasionally, usually as comic relief or tragic spectacle. What they rarely get is the kind of patient, immersive, structurally complex filmmaking that Shah has given them here.

For NRI audiences who have followed the global rise of Indian cinema — Payal Kapadia's Grand Prix, the FTII student film in La Cinef this year, Anasuya Sengupta's Best Actress win in 2024 — *Elephants in the Fog* adds a crucial dimension: South Asian cinema's global moment is not only India's moment. Nepal, with a film industry that produces roughly 100 films a year compared to India's 2,000, has produced a debut feature that won two prizes at the world's most competitive festival.

## The Director

Shah is no stranger to Cannes. His 2022 short film *Lori* received a Special Mention at the 75th edition of the festival — the first Nepali short to earn any recognition there. His writing credits include *Kalo Pothi*, *Highway*, and *Tatini*, all screened at international festivals. He has spoken about wanting to move cinema's gaze "from 'them' to 'us'" — to stop treating marginalised communities as subjects of anthropological curiosity and start treating them as protagonists of their own stories.

With *Elephants in the Fog*, he has done exactly that. And Cannes noticed.

For the growing community of South Asian cinephiles abroad — the ones who organise screening clubs in London, who queue for South Asian Shorts at TIFF, who subscribe to MUBI for the films their parents' generation never watched — this is a landmark worth marking. Nepal made a film. It went to Cannes. It won. Twice."""
})

# ── Insert articles ──
for a in articles:
    result = sb_post("p2_articles", a)
    print(f"✅ Published: [{a['id'][:8]}] {a['headline'][:80]}")

print(f"\n📝 Total articles published: {len(articles)}")
