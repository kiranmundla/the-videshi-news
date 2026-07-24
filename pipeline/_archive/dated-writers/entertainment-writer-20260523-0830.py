#!/usr/bin/env python3
"""Entertainment writer — May 23 2026, 08:30 PDT batch:
1. Drishyam 3 box office weekend update — ₹76 Cr worldwide in 2 days, on track for ₹100 Cr
2. Chand Mera Dil opening — Dharma's romantic gamble opens soft at ₹3 Cr
3. Delete duplicate article deee67df (System/Sonakshi, duplicates 9dc842e8)
4. Score decay for old entertainment articles
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

def sb_delete(table, filters):
    r = requests.delete(f"{SB_URL}/rest/v1/{table}?{filters}", headers={**HEADERS, "Prefer": "return=minimal"}, timeout=30)
    return r.status_code

now = datetime.now(timezone.utc).isoformat()

# ══════════════════════════════════════════════════════════════
# CLEANUP: Delete duplicate System/Sonakshi article
# ══════════════════════════════════════════════════════════════

dup_status = sb_delete("p2_articles", "id=eq.deee67df-c0ff-4623-9b1a-b7df36b152d4")
print(f"🗑️  Deleted duplicate article deee67df: HTTP {dup_status}")

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Drishyam 3 — ₹76 Cr worldwide in 2 days
# ══════════════════════════════════════════════════════════════

a1_id = str(uuid.uuid4())

articles.append({
    "id": a1_id,
    "headline": "Drishyam 3 Just Hit ₹76 Crore Worldwide in Two Days. Mohanlal Hasn't Had a Weekend Like This in 30 Years.",
    "subheadline": "The franchise that made a Kerala family man India's most beloved criminal is now on track to cross ₹100 crore worldwide before Sunday — and the overseas numbers suggest the diaspora is carrying this film harder than anyone expected.",
    "slug": "drishyam-3-76-crore-worldwide-2-days-mohanlal-box-office-weekend-20260523",
    "category": "Entertainment",
    "vertical": "entertainment",
    "urgency": "standard",
    "status": "published",
    "published_at": now,
    "score_total": 82,
    "tags": ["Drishyam 3", "Mohanlal", "box office", "Malayalam cinema", "weekend collection", "diaspora", "OTT", "Georgekutty", "N Venugopal"],
    "diaspora_angle": "Drishyam 3's overseas performance is the headline within the headline. Of the ₹76 crore worldwide total, roughly ₹45 crore came from overseas markets in just two days — a staggering ratio for a Malayalam-language film. The franchise has always punched above its weight internationally because Georgekutty's story resonates with diaspora audiences who understand what it means to protect a family at any cost, in a system that wasn't designed to protect them. The Hindi remake starring Ajit Devi made the character a national icon, but the original Mohanlal version remains the preferred cut for Malayali NRIs worldwide. With screenings selling out across the Gulf, the UK, and North America, Drishyam 3 is confirming what the industry has suspected for years: Malayalam cinema's diaspora audience is now a primary revenue stream, not a bonus.",
    "sources": [
        {"url": "https://sacnilk.com", "name": "Sacnilk"},
        {"url": "https://www.zoomtventertainment.com", "name": "Zoom TV"},
        {"url": "https://www.filmibeat.com", "name": "Filmibeat"},
        {"url": "https://www.bollywoodlife.com", "name": "Bollywood Life"},
        {"url": "https://nripage.com", "name": "NRI Page"}
    ],
    "image_search_query": "Malayalam cinema audience theater crowd India 2026",
    "word_count": 780,
    "body": """Two days in, and Drishyam 3 is doing something that almost no Malayalam film has done before: it's making the rest of the Indian film industry pay attention to the box office numbers coming out of Kerala, the Gulf, and the global Malayali diaspora.

Mohanlal's third outing as Georgekutty — the cable TV operator who buried a body and built a cathedral of lies to protect his family — has grossed ₹76 crore worldwide in its first 48 hours. That includes ₹26.90 crore net in India (₹31.18 crore gross) and an estimated ₹45 crore from overseas markets. For context, that overseas-to-domestic ratio is extraordinary for any Indian film, let alone one that's primarily in Malayalam.

## The Numbers Tell Two Different Stories

The India numbers are strong but show the expected pattern. Day 1 delivered ₹15.85 crore net — the biggest opening day for a Malayalam film this year. Day 2 dropped roughly 30% to ₹11.05 crore, which is standard for a Thursday-to-Friday transition. The film played across 4,886 shows on Day 2, with Kerala predictably dominating at ₹8.85 crore gross. Karnataka (₹1.5 crore) and Tamil Nadu (₹1 crore) held steady, confirming the franchise's pan-South appeal.

But the real story is overseas. The ₹45 crore international gross in two days makes Drishyam 3 the fastest Malayalam film to reach that milestone. The Gulf region, home to the largest concentration of Malayali diaspora workers in the world, accounted for the lion's share. The UK, US, Canada, and Australia all reported strong numbers, with several evening shows running at near-full occupancy.

Critics have noted that the film is tracking to cross ₹100 crore worldwide before Sunday night — a milestone that only a handful of Malayalam films have ever achieved, and none this fast.

## Why the Diaspora Is Carrying This Film

The Drishyam franchise has always been a diaspora story disguised as a crime thriller. Georgekutty is a self-made man operating in a system rigged against people like him — a narrative that resonates viscerally with NRI audiences who've navigated visa offices, immigration systems, and institutional indifference in countries that weren't built for them.

The original 2013 film became a cultural touchstone for Malayali families abroad. The Hindi remake brought Georgekutty to a national audience, but for the diaspora, Mohanlal's version has always been the definitive one. There's a reason the GCC numbers are this high: families are going together, in groups, the way they used to watch films in Kerala before they left.

The third film picks up where the second left off, with Georgekutty facing the consequences of his increasingly elaborate deceptions. Director N. Venugopal has reportedly maintained the franchise's signature tension — the slow-burn domestic thriller where every conversation could be the one that unravels everything.

## The Weekend Will Decide Everything

Drishyam 3's trajectory now depends entirely on Saturday and Sunday. If the weekend holds — and early morning occupancy data for Saturday suggests it will, with 25-30% morning shows and the expectation of 60%+ evening fills — the film could finish its first weekend at ₹130-150 crore worldwide.

That would put it in conversation with the biggest Malayalam films ever made, alongside Lucifer, Empuraan, and Patriot. It would also confirm something the industry has been slow to acknowledge: Malayalam cinema's box office ceiling has permanently shifted upward, driven by a diaspora audience that's larger, wealthier, and more enthusiastic than the domestic market expected.

For Mohanlal, 67 years old and more than four decades into a career that has produced over 400 films, this is the vindication of a franchise that other actors tried to claim. Ajay Devgn made the Hindi Drishyam. Venkatesh made the Telugu version. Kamal Haasan reportedly wanted the Tamil rights. But the audience knows who Georgekutty really is.

The ₹100 crore milestone isn't a question anymore. The question is whether Drishyam 3 can sustain its pace through the second week — and whether it can hold its screens against the approaching Ramayana hype cycle that's already consuming every other conversation in Indian cinema.

For now, Mohanlal's phone is probably ringing. And knowing Georgekutty, he's not going to answer it."""
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Chand Mera Dil — Dharma's romantic gamble
# ══════════════════════════════════════════════════════════════

a2_id = str(uuid.uuid4())

articles.append({
    "id": a2_id,
    "headline": "Karan Johar Bet ₹149 Movie Tickets Could Save Bollywood Romance. Chand Mera Dil Just Opened to ₹3 Crore. He Might Be Right.",
    "subheadline": "Dharma Productions' latest pairing of Ananya Panday and Lakshya opened soft on Friday — but the strategy behind the film reveals more about Bollywood's romance crisis than the numbers suggest.",
    "slug": "chand-mera-dil-opening-day-box-office-ananya-panday-lakshya-dharma-20260523",
    "category": "Entertainment",
    "vertical": "entertainment",
    "urgency": "standard",
    "status": "published",
    "published_at": now,
    "score_total": 72,
    "tags": ["Chand Mera Dil", "Ananya Panday", "Lakshya", "Karan Johar", "Dharma Productions", "box office", "romantic drama", "Bollywood romance", "Vivek Soni"],
    "diaspora_angle": "For NRIs who grew up on Dharma's romantic universe — Kuch Kuch Hota Hai, Kal Ho Naa Ho, Kabhi Khushi Kabhie Gham — the performance of Chand Mera Dil is a data point in a larger question: can Bollywood still make romances that work in theaters? The genre that once defined Bollywood for the global diaspora has been in decline for years, replaced by action franchises and horror-comedies. The ₹149 ticket strategy is notable because it acknowledges what NRI families already know: the theatrical romance experience has been priced out for casual viewers. Whether Chand Mera Dil can hold through the weekend will tell Dharma — and the industry — whether the audience for love stories still exists in cinemas, or whether it's permanently migrated to streaming.",
    "sources": [
        {"url": "https://www.mensxp.com", "name": "MensXP"},
        {"url": "https://www.zoomtventertainment.com", "name": "Zoom TV"},
        {"url": "https://www.bollywoodhungama.com", "name": "Bollywood Hungama"},
        {"url": "https://www.pinkvilla.com", "name": "Pinkvilla"},
        {"url": "https://www.filmibeat.com", "name": "Filmibeat"}
    ],
    "image_search_query": "Bollywood cinema theater romantic film India couple 2026",
    "word_count": 750,
    "body": """Chand Mera Dil, Karan Johar's latest attempt to prove that Bollywood romance isn't dead, opened on Friday to somewhere between ₹2.75 crore and ₹3.75 crore — depending on which tracking service you trust. The makers claim ₹3.31 crore from 4,944 shows. The independent trackers say it's closer to ₹2.75-3 crore. Either way, it's a soft opening for a Dharma production, but it's not the disaster the early dismissals would have you believe.

Here's why.

## The ₹149 Strategy

Before the film opened, Dharma made a decision that tells you everything about where Bollywood romance stands in 2026: they priced opening-day tickets at ₹149. That's roughly the cost of a month of JioCinema. It's the price of two cups of decent coffee in a Delhi mall.

The logic is straightforward. Bollywood's romance genre has been dying in theaters because the audience that loves love stories — young couples, families, college groups — has been priced out of the multiplex experience. A family of four watching a matinee in a Mumbai PVR can easily spend ₹2,500 before popcorn. For a romantic drama without spectacle or action set pieces, that's a tough sell when the same family can watch it on streaming six weeks later.

By dropping the price to ₹149, Dharma is essentially buying sampling. Get people into theaters. Let word of mouth do the rest. If the film is good enough, Saturday and Sunday should see a significant jump as organic buzz spreads through WhatsApp groups and Instagram stories.

## What the Film Actually Is

Directed by Vivek Soni (Meenakshi Sundareshwar, Aap Jaisa Koi), Chand Mera Dil stars Ananya Panday and Lakshya Lalwani as young lovers navigating what's been described as a "dark romantic twist" — not the standard Dharma fairy tale. The first review on social media called it "watchable" with a 2.5-star rating, which in Bollywood terms means it's not terrible but it's not going to set the world on fire.

For Ananya Panday, this is a critical moment. She's coming off the success of Badass of Bollywood and trying to establish herself as someone who can open a film on her name alone. For Lakshya, it's even more important — his debut film Kill opened to roughly ₹1 crore, making Chand Mera Dil's ₹3 crore start a 300% improvement.

The early reviews highlight the chemistry between the leads and a script that takes some unexpected turns. Bollywood Hungama noted that the first day "lays a platform for reasonable results over the weekend with jumps on Saturday and Sunday," while also cautioning that Monday stability is crucial for long-term success.

## The Bigger Picture: Is Bollywood Romance Dead?

The question isn't really whether Chand Mera Dil will be a hit — with controlled costs, it needs roughly ₹30-40 crore to break even. The question is whether it can prove that the genre still has theatrical viability.

Consider the evidence from 2026 so far. Bollywood's biggest hits have been an action franchise sequel (Dhurandhar 2, ₹1,183 crore), a war epic (Border 2, ₹362 crore), and a horror-comedy (Bhooth Bangla, ₹187 crore). The last pure romantic drama to meaningfully perform at the box office was... it's hard to even name one.

Karan Johar built his empire on romance. Dharma Productions defined the aesthetic vocabulary of Bollywood love stories for an entire generation of NRI audiences. KKHH, K3G, SOTY — these were the films that played at Indian grocery stores in New Jersey, at community hall screenings in London, at every diaspora wedding where the DJ needed a slow song.

If that genre is truly dead in theaters, it has implications for how Bollywood tells stories going forward. It means the industry has permanently bifurcated: spectacle films for theaters, intimate stories for streaming. And Dharma, the studio most associated with the theatrical romance, would need to fundamentally rethink its identity.

Chand Mera Dil has a two-week clear runway before its next competition arrives on June 5. If Saturday shows even a 30% jump — which the ₹149 sampling strategy is designed to produce — the narrative around the film changes completely.

The weekend will tell us. Not just about Chand Mera Dil, but about whether an entire genre has a future outside your phone screen."""
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

print("\n✅ Entertainment writer 08:30 batch complete.")
