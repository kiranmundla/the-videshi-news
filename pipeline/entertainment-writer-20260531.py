#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-31 batch (curl-based)"""

import json, os, re, subprocess, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:]
            k, _, v = line.partition('=')
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k.strip(), v)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SB_URL = os.environ['SUPABASE_URL']
SB_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

# ── curl-based Supabase helpers ──────────────────────────────────────
def sb_insert(table, row):
    """Insert via curl to avoid IncompleteRead."""
    result = subprocess.run(
        ['curl', '-sS', '-X', 'POST',
         f'{SB_URL}/rest/v1/{table}',
         '-H', f'apikey: {SB_KEY}',
         '-H', f'Authorization: Bearer {SB_KEY}',
         '-H', 'Content-Type: application/json',
         '-H', 'Prefer: return=representation',
         '-d', json.dumps(row)],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"  ✗ curl insert failed: {result.stderr[:300]}")
        return None
    try:
        data = json.loads(result.stdout)
        return data
    except:
        print(f"  ✗ Parse error: {result.stdout[:300]}")
        return None

def sb_patch(table, filters, patch):
    """Patch via curl."""
    qs = '&'.join(f"{k}={v}" for k, v in filters.items())
    subprocess.run(
        ['curl', '-sS', '-X', 'PATCH',
         f'{SB_URL}/rest/v1/{table}?{qs}',
         '-H', f'apikey: {SB_KEY}',
         '-H', f'Authorization: Bearer {SB_KEY}',
         '-H', 'Content-Type: application/json',
         '-d', json.dumps(patch)],
        capture_output=True, text=True, timeout=30
    )

# ── Image helpers ────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        req = urllib.request.Request(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}
        )
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
        if img:
            print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
            return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage using curl."""
    tmp_path = f"/tmp/{filename}"
    try:
        # Download
        dl = subprocess.run(
            ['curl', '-sS', '-L', '-o', tmp_path,
             '-H', 'User-Agent: TheVideshi/1.0 (thevideshi.com)',
             image_url],
            capture_output=True, text=True, timeout=20
        )
        if not os.path.exists(tmp_path) or os.path.getsize(tmp_path) < 5000:
            print(f"  ⚠ Downloaded image too small or missing")
            return None

        # Upload
        ul = subprocess.run(
            ['curl', '-sS', '-X', 'POST',
             f'{SB_URL}/storage/v1/object/article-images/{filename}',
             '-H', f'apikey: {SB_KEY}',
             '-H', f'Authorization: Bearer {SB_KEY}',
             '-H', 'Content-Type: image/jpeg',
             '-H', 'x-upsert: true',
             '--data-binary', f'@{tmp_path}'],
            capture_output=True, text=True, timeout=30
        )

        public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
        os.remove(tmp_path)
        return public_url
    except Exception as e:
        print(f"  ⚠ Upload failed: {e}")
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return None

# ── Articles ─────────────────────────────────────────────────────────
articles = [
    {
        "headline": "FWICE Just Banned Ranveer Singh From Working in Bollywood. The Don 3 Fallout Is Now an Industry Crisis.",
        "subheadline": "A ₹45 crore dispute, a non-cooperation directive, and Ram Gopal Varma calling the trade body a 'kangaroo court' — the Don 3 controversy has split the film industry into two camps.",
        "slug": "ranveer-singh-fwice-ban-don-3-controversy-industry-crisis-nri-20260531",
        "category": "entertainment",
        "sources": [{"name": "Bollywood Hungama"}, {"name": "The Indian Eye"}, {"name": "Indulge Express"}, {"name": "Zoom TV Entertainment"}],
        "person_for_image": "Ranveer Singh",
        "body": """Ranveer Singh's name is now on a blacklist — not from a court order, not from a government body, but from the Federation of Western India Cine Employees, which has issued a non-cooperation directive telling every union member in the Hindi film industry to refuse to work with him.

The ban stems from his abrupt exit from Don 3. Farhan Akhtar and Ritesh Sidhwani's Excel Entertainment claim they lost ₹45 crore in pre-production costs after Ranveer walked away three weeks before shooting was scheduled to begin. The actor's camp maintains that the film lacked a finalized script after years of development and that no advance payment had been made.

## A Dispute That Escalated Fast

FWICE sent multiple notices to Ranveer. His legal team responded by questioning the federation's jurisdiction — arguing that this was a private commercial contract between a star and a producer, not a matter for an industry body. FWICE went ahead with the directive anyway.

The ban is not legally binding. Chief Adviser Ashoke Pandit has clarified that it's an "industry body-level action," but in practice, it means most technicians, crew members, and below-the-line workers will refuse to collaborate on any Ranveer Singh project until the matter is resolved.

## The Industry Splits

Ram Gopal Varma was the first major voice to push back. "BAN 'FWICE' and not Ranveer Singh," he posted on X, calling the directive a "performative muscle-flex" by an "extremely outdated union system." He argued that FWICE was operating as a "kangaroo court" with no legal authority to adjudicate private contracts.

CINTAA — the Cine and TV Artistes' Association — also broke ranks. Vice-President Padmini Kolhapure publicly stated that the organization stands with Ranveer, suggesting the directive was overreach.

Behind the scenes, Salman Khan has stepped in as a mediator. He enjoys a cordial relationship with both Ranveer and Farhan, and has reportedly urged both sides to settle privately without involving legal proceedings or industry organizations. Both parties are believed to be following his advice, though Excel Entertainment insists that any settlement talks must happen with Farhan and Ritesh personally present.

## What Started as a Creative Disagreement

The roots go deeper than a scheduling conflict. According to Indulge Express, Ranveer wanted the Don character to be portrayed with more sinister overtones, while Farhan was insistent on keeping the franchise's established tone. After nearly two years of creative deadlock, Ranveer exited. His team reportedly offered a ₹35 crore settlement — ₹10 crore upfront plus a ₹25 crore discount on a future project — but Excel rejected it and held firm at ₹45 crore.

## What NRIs Should Know

For diaspora audiences who grew up with Amitabh Bachchan's Don and watched Shah Rukh Khan reinvent it, the franchise carries cultural weight. Ranveer was announced as the new Don in 2023, inheriting a legacy that spans nearly five decades of Indian cinema.

The real question is whether the FWICE ban has any teeth. India's film industry operates on relationships, not union mandates. If a major studio wants to work with Ranveer — and his upcoming film Pralay is still in active development — the directive may prove to be more symbolic than substantive.

But it sets a precedent. If trade bodies can effectively blackball an A-list star over a contract dispute, the power dynamics between stars, studios, and unions will shift in ways the industry hasn't seen since the underworld era of the 1990s.

This also marks Ranveer's second major controversy in six months. In December 2025, he faced backlash and a police complaint after mimicking Rishab Shetty's Kantara Daiva scene at IFFI Goa, calling the sacred Chamundi Daiva a "female ghost." He apologized, but the pattern of high-profile public clashes is becoming hard to ignore.

Ranveer's next move will determine whether this becomes a footnote or a turning point. For now, the man who once told Karan Johar on Koffee With Karan that all he wanted was a fair chance is learning that the industry's definition of fairness depends heavily on who's asking.

*Sources: Bollywood Hungama, The Indian Eye, Indulge Express, Zoom TV Entertainment*"""
    },
    {
        "headline": "Main Vaapas Aaunga Just Topped IMDb's Most Anticipated Indian Film of 2026. It's Imtiaz Ali's Partition Love Story.",
        "subheadline": "Diljit Dosanjh, Vedang Raina, Sharvari, and Naseeruddin Shah star in a film about love and separation during the bloodiest chapter of Indian history. It opens June 12.",
        "slug": "main-vaapas-aaunga-imdb-most-anticipated-imtiaz-ali-partition-june-12-nri-20260531",
        "category": "entertainment",
        "sources": [{"name": "IMDb"}, {"name": "Bollywood Hungama"}, {"name": "Zoom TV Entertainment"}, {"name": "IWM Buzz"}],
        "person_for_image": "Imtiaz Ali",
        "body": """IMDb has spoken, and the numbers confirm what the trailer already suggested: Main Vaapas Aaunga is the most anticipated Indian film of 2026.

Imtiaz Ali's upcoming release has topped IMDb's annual survey of Most Anticipated Indian Films and Shows, beating out every Bollywood blockbuster, every regional tentpole, and every streaming original on the platform's radar. The film opens in theatres on June 12.

## A Partition Story Through Imtiaz Ali's Lens

The film is set against the backdrop of the 1947 Partition — the event that divided British India into India and Pakistan, displaced 15 million people, and killed between one and two million. It's the foundational trauma of the Indian diaspora, the wound that echoes through every NRI family's generational memory.

Imtiaz Ali, the filmmaker behind Jab We Met, Highway, and Rockstar, is not typically associated with historical epics. His films live in the intimate, the personal — lovers on trains, wanderers in the mountains, musicians drowning in their own excess. Setting that sensibility against the scale of Partition is either a masterstroke or a miscalculation. The trailer suggests the former.

## The Cast

Diljit Dosanjh — who has become a global touring phenomenon and one of Punjabi cinema's most bankable stars — headlines alongside Vedang Raina, the young actor from The Archies who Imtiaz has already compared to Alia Bhatt in Highway. "Some newcomers unexpectedly bring a certain depth of emotion," Ali said in a recent interview. "There is a certain maturity that these people possess."

Sharvari, coming off the buzz from her upcoming Alpha alongside Alia Bhatt, rounds out the younger cast. And Naseeruddin Shah — at this point less an actor and more a national institution — anchors the film's older timeline.

The music comes from A.R. Rahman, reuniting with Imtiaz after the Rockstar and Highway soundtracks that defined a generation of Bollywood music. Songs from Main Vaapas Aaunga are already dominating streaming playlists weeks before release.

## Why It Matters for the Diaspora

Every Indian family abroad carries a Partition story. Some know it in detail — the village they lost, the train they barely survived, the relatives who ended up on the other side. Others carry it as a vague inheritance, a heaviness their grandparents never fully explained.

Imtiaz Ali has said this is a story of love and longing, not a political history lesson. That's exactly what makes it potentially powerful for NRI audiences. The diaspora doesn't need another documentary about Partition. It needs a film that makes the personal loss feel present — the kind of storytelling Imtiaz does better than almost anyone in Indian cinema.

Main Vaapas Aaunga opens June 12. It will face a crowded release window — Governor (with Manoj Bajpayee as the RBI chief who saved India from bankruptcy) and Bharat Bhhagya Vidhaata (Kangana Ranaut's 26/11 film) are also opening around the same date. But IMDb's ranking suggests it has the early audience advantage.

The title translates roughly to "I Will Come Back." For a Partition story, that's either a promise or a prayer.

*Sources: IMDb, Bollywood Hungama, Zoom TV Entertainment, IWM Buzz*"""
    },
    {
        "headline": "Harvard Just Named Mean Girls Star Avantika Vandanapu Its South Asian Person of the Year. She's 19.",
        "subheadline": "The Telugu-origin actress who broke through in Hollywood's biggest teen franchise is now being recognized by America's oldest university for her impact on global representation.",
        "slug": "avantika-vandanapu-harvard-south-asian-person-of-year-mean-girls-nri-20260531",
        "category": "entertainment",
        "sources": [{"name": "The Indian Eye"}, {"name": "Harvard University"}],
        "person_for_image": "Avantika Vandanapu",
        "body": """Avantika Vandanapu has been named the South Asian Person of the Year by Harvard University — and at 19, she might be the youngest person to receive the honor.

The Indian-American actress, best known for playing Karen Shetty in the 2024 Mean Girls musical adaptation, was recognized for her impact on both international and Indian entertainment industries. "Being honored by such a prestigious institution as Harvard University is truly humbling and incredibly motivating," Vandanapu said in her acceptance remarks.

## The Hyderabad-to-Hollywood Pipeline

Vandanapu was born into a Telugu family from Hyderabad. Her path to Hollywood started with a second-place finish on Dance India Dance L'il Masters, the children's dance reality competition that has launched dozens of Indian entertainment careers. She crossed over into Telugu cinema with Brahmotsavam before making the jump to American productions.

Disney took notice first. She starred in Spin alongside Meera Syal and Abhay Deol, playing an Indian-American teenager navigating her identity through DJ culture. Then came Big Girls Don't Cry, the Indian OTT series that established her as a cross-market talent. But it was Mean Girls — Paramount's musical reimagining of Tina Fey's 2004 classic — that made her a household name.

Karen Shetty, her character, was the first South Asian lead in the Mean Girls franchise. The character wasn't defined by her ethnicity; she was simply Karen, one of the Plastics, written into the story without the usual "immigration subplot" or "identity crisis" arc that Hollywood typically assigns to brown characters.

## The Tangled Controversy

The recognition comes at an interesting moment. Vandanapu has recently faced backlash over rumors that she was being considered for the role of Rapunzel in Disney's live-action adaptation of Tangled. Multiple Disney fan communities took to social media to express displeasure at a South Asian actress potentially portraying the blonde, European fairy-tale princess.

The casting was never confirmed, but the discourse was revealing. It exposed the limits of Hollywood's representation progress — audiences celebrate diversity in original roles but resist it when applied to established characters. For NRI parents watching their children navigate American pop culture, it was a familiar tension.

## What Harvard's Honor Signals

Harvard's South Asian Person of the Year recognition isn't just about entertainment. It signals that institutions at the highest level of American society are beginning to acknowledge the cultural impact of South Asian creatives, not just South Asian technologists and business leaders.

For decades, the diaspora's most celebrated figures in America were CEOs — Sundar Pichai, Satya Nadella, Indra Nooyi. The Spelling Bee champions. The doctors. Vandanapu represents a different kind of diaspora success: creative, visible, and unapologetically mainstream.

"My journey is just beginning," she said, "and this recognition ignites my determination to continue contributing positively through my work."

She's 19. The journey is indeed just beginning. But for every Telugu kid in Hyderabad watching Dance India Dance and dreaming of Hollywood, and for every Indian-American teenager who saw Karen Shetty in Mean Girls and finally felt like the popular girl could look like them — the impact is already substantial.

*Sources: The Indian Eye, Harvard University*"""
    }
]

# ── Main loop ────────────────────────────────────────────────────────
now = datetime.now(timezone.utc).isoformat()

# First, check if article 1 was already inserted from previous run
check = subprocess.run(
    ['curl', '-sS',
     f'{SB_URL}/rest/v1/p2_articles?select=id&slug=eq.ranveer-singh-fwice-ban-don-3-controversy-industry-crisis-nri-20260531',
     '-H', f'apikey: {SB_KEY}',
     '-H', f'Authorization: Bearer {SB_KEY}'],
    capture_output=True, text=True, timeout=15
)
existing = json.loads(check.stdout) if check.stdout.strip() else []
skip_first = len(existing) > 0
if skip_first:
    print(f"⚠ Article 1 already exists (id={existing[0]['id']}), skipping insert")
    articles[0]['_existing_id'] = existing[0]['id']

for i, art in enumerate(articles, 1):
    print(f"\n{'='*60}")
    print(f"Article {i}/{len(articles)}: {art['headline'][:70]}...")
    print('='*60)

    # ── Image sourcing ───────────────────────────────────────────
    img_url = None
    img_attribution = None

    if art.get('person_for_image'):
        img_url = fetch_wikipedia_person_image(art['person_for_image'])
        if img_url:
            img_attribution = "Wikimedia Commons"

    # ── Insert article ───────────────────────────────────────────
    if art.get('_existing_id'):
        art_id = art['_existing_id']
        print(f"  → Using existing article: {art_id}")
    else:
        row = {
            "headline": art["headline"],
            "subheadline": art["subheadline"],
            "slug": art["slug"],
            "category": art["category"],
            "vertical": art["category"],
            "body": art["body"].strip(),
            "sources": json.dumps(art["sources"]),
            "status": "published",
            "published_at": now,
            "image_attribution": img_attribution,
        }

        result = sb_insert("p2_articles", row)
        if isinstance(result, list) and result:
            art_id = result[0].get('id')
            print(f"  ✓ Inserted article: {art_id}")
        else:
            print(f"  ✗ Insert failed: {result}")
            continue

    # ── Upload image to Supabase storage ─────────────────────────
    if img_url and art_id:
        filename = f"{art_id}.jpg"
        final_url = upload_to_supabase_storage(img_url, filename)
        if final_url:
            sb_patch("p2_articles", {"id": f"eq.{art_id}"}, {"image_url": final_url})
            print(f"  ✓ Image set: {final_url[:70]}...")
        else:
            # Try Wikipedia URL directly (permanent)
            if 'upload.wikimedia.org' in (img_url or ''):
                sb_patch("p2_articles", {"id": f"eq.{art_id}"}, {"image_url": img_url})
                print(f"  ✓ Using Wikipedia URL directly")
            else:
                print(f"  ⚠ No valid image for this article")
    else:
        print(f"  ⚠ No image sourced for this article")

    time.sleep(1)

print(f"\n✅ Done! Published {len(articles)} entertainment articles.")
