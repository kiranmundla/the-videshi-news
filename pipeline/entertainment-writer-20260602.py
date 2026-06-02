#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-06-02 batch."""

import json
import os
import re
import sys
import time
import uuid
import urllib.parse
from datetime import datetime, timezone

import requests

# ── Env ──────────────────────────────────────────────────────────────────────
env_file = os.path.expanduser("~/.env.supabase")
if os.path.exists(env_file):
    for line in open(env_file):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k, v)

pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k, v)

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


# ── Image helpers ────────────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels API using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                [
                    "curl", "-sS",
                    f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                    "-H", f"Authorization: {PEXELS_KEY}",
                ],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Validate image URL returns 200 with image content-type and > 5KB."""
    try:
        # Always use GET with stream for reliable validation
        r = requests.get(url, timeout=15, stream=True, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        if r.status_code == 200 and "image" in ct:
            # Read enough to check size
            chunk = r.raw.read(6000)
            if len(chunk) >= 5000:
                return True
            else:
                print(f"  ⚠ Image too small: {len(chunk)} bytes")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, timeout=15, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Download failed or too small: {len(r.content)} bytes")
            return None
        
        ct = r.headers.get("Content-Type", "image/jpeg")
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": ct,
                "x-upsert": "true",
            },
            data=r.content,
            timeout=30,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def source_image(person_name=None, pexels_query=None, pexels_fallback=None, slug=""):
    """Try Wikipedia first for person, then Pexels, upload to Supabase."""
    img_url = None
    attribution = "The Videshi"
    
    if person_name:
        img_url = fetch_wikipedia_person_image(person_name)
        if img_url:
            attribution = "Wikimedia Commons"
    
    if not img_url and pexels_query:
        img_url = fetch_pexels_image(pexels_query, pexels_fallback)
        attribution = "Pexels"
    
    if img_url:
        if validate_image(img_url):
            # Upload to Supabase for permanence
            ext = "jpg"
            if ".png" in img_url.lower():
                ext = "png"
            filename = f"{slug}.{ext}"
            uploaded = upload_to_supabase_storage(img_url, filename)
            if uploaded:
                return uploaded, attribution
            # Fallback: use direct URL if it's from permanent source
            if "upload.wikimedia.org" in img_url or "images.pexels.com" in img_url:
                return img_url, attribution
        else:
            print(f"  ⚠ Image validation failed for: {img_url[:80]}")
    
    return None, None


def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Inserted: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None


# ── Articles ─────────────────────────────────────────────────────────────────

articles = []

# ─── Article 1: Don 3 court case ─────────────────────────────────────────────
articles.append({
    "headline": "The Don 3 Fight Just Left Bollywood's Back Rooms. It's in a Bombay Courtroom Now.",
    "subheadline": "Veteran producer TP Aggarwal has filed a petition challenging FWICE's power to blacklist actors — and the case has implications far beyond Ranveer Singh.",
    "slug": "don-3-fwice-ban-ranveer-singh-court-tp-aggarwal-bollywood-legal-nri-20260602",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False,
    "is_featured": False,
    "tags": [],
    "sources": json.dumps([
        "Bollywood Hungama",
        "India Forums",
        "Zoom TV Entertainment",
        "Cinema Buzz USA"
    ]),
    "body": """The simmering dispute over Ranveer Singh's exit from *Don 3* has crossed a threshold that Bollywood rarely reaches: a formal legal challenge to the authority of its most powerful trade bodies.

On June 1, veteran producer TP Aggarwal filed a civil petition in the Bombay Civil Court at Dindoshi — not against Ranveer Singh, and not against Farhan Akhtar's Excel Entertainment, but against the Federation of Western India Cine Employees (FWICE) and the Indian Motion Picture Producers' Association (IMPPA) themselves. The petition asks a question that the Hindi film industry has danced around for decades: Does any trade body have the legal right to tell its members not to work with a specific individual?

## What Led Here

The controversy traces back to early 2026, when Ranveer Singh walked away from *Don 3*, the third instalment in the franchise that Shah Rukh Khan made iconic. Excel Entertainment, Farhan Akhtar's production house, reportedly sought ₹40 crore in compensation for pre-production losses. Ranveer's camp disputed the figure, and informal mediation through the Producers Guild failed. The situation escalated sharply on May 25, when FWICE issued a non-cooperation directive against the actor — effectively instructing its thousands of members across the Hindi film industry to refuse work with him until the dispute was resolved.

That directive is what Aggarwal's petition targets. His argument: such bans exceed the legal authority of voluntary trade associations and directly threaten the livelihoods and creative freedom of industry professionals.

## Why TP Aggarwal Matters

This isn't a fringe complaint. Aggarwal served as President of IMPPA for 17 years and was elected President of the Film Federation of India on four occasions. He currently holds the title of Patron at both FFI and IMPPA. When someone with that institutional history files a petition challenging the system, it carries weight that a first-time litigant's case would not.

"The film industry thrives on collaboration," Aggarwal said in a statement accompanying the filing. "Any attempt to discourage people from working with an individual should not be taken lightly. Such actions can have far-reaching consequences for livelihoods and creative freedom, and therefore must be dealt with in a fair, transparent, and lawful manner."

The court has issued notices to both FWICE and IMPPA, requiring formal responses.

## The Diaspora Angle

For NRI audiences who grew up watching the *Don* franchise — from Amitabh Bachchan's original to Shah Rukh Khan's reboot — this legal battle represents something larger than a contractual dispute. It's a window into Bollywood's informal power structures: the guild politics, the verbal agreements, the trade body directives that can make or break careers without any court ever being involved.

The Cine and TV Artistes' Association (CINTAA) has offered formal support to Ranveer. Vice-president Padmini Kolhapure confirmed the association would stand by him as a member, though she noted that neither Singh, Excel Entertainment, nor FWICE had approached CINTAA for mediation.

## What Happens Next

The petition doesn't seek to resolve the underlying *Don 3* compensation dispute. Instead, it challenges the broader principle: whether FWICE or any similar body can enforce a boycott. If the court rules in Aggarwal's favour, it could fundamentally reshape how Bollywood's labour disputes are handled — pushing them from backroom negotiations and public pressure campaigns into formal legal proceedings.

For now, Ranveer Singh remains under the non-cooperation directive. His next major release, alongside the *Dhurandhar* franchise's continued cultural impact, keeps him among the most discussed actors in Indian cinema. But the courtroom — not the box office — may determine what his next few years look like.""",
    "person": "Ranveer Singh",
    "pexels_query": "Indian court gavel legal",
    "pexels_fallback": "courtroom law justice",
})

# ─── Article 2: Governor – Manoj Bajpayee as RBI Governor ────────────────────
articles.append({
    "headline": "Manoj Bajpayee Plays the Man Who Pawned India's Gold to Save the Economy. Governor Releases June 12.",
    "subheadline": "The 1991 balance-of-payments crisis created the India that millions of NRIs emigrated to build careers in. Now it's a film — and Bajpayee says the math terrified him.",
    "slug": "governor-manoj-bajpayee-rbi-1991-crisis-gold-reserves-june-12-nri-20260602",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False,
    "is_featured": False,
    "tags": [],
    "sources": json.dumps([
        "Bollywood Hungama",
        "Filmfare",
        "The Daily Jagran",
        "NewKerala",
        "TechnoSports"
    ]),
    "body": """There is a specific date that shaped the lives of nearly every Indian professional living abroad, and most of them have never heard of the man behind it. In 1991, India's foreign exchange reserves had fallen to a level that could cover barely two weeks of imports. The country was days away from defaulting on its sovereign debt. The Reserve Bank of India, under Governor S. Venkitaramanan, made a decision that economists still debate and nationalists still flinch at: India shipped 47 tonnes of gold to the Bank of England and the Union Bank of Switzerland as collateral, raising approximately $405 million to keep the country solvent.

That emergency action — and the economic liberalisation it enabled — is the subject of *Governor: The Silent Saviour*, a political drama releasing in theatres on June 12. Manoj Bajpayee plays Venkitaramanan.

## The Story Behind the Film

Director Chinmay Mandlekar and producer Vipul Amrutlal Shah have built the film around the weeks of crisis in 1991, when Iraq's invasion of Kuwait had spiked oil prices, remittances from the Gulf had collapsed, and India's credit rating was in freefall. The film follows Venkitaramanan as he navigates the political pressure, institutional resistance, and personal stakes of a decision that would either save the economy or become the greatest humiliation in independent India's financial history.

Bajpayee has spoken candidly about the challenge. "When we talk about heroes, we usually make films on army officers or politicians," he told IANS. "But I felt that for the first time, we are talking about a man who was working behind the curtain from a new sector, from such a department which drives the policy of a very crucial part of the country."

The actor also admitted that the role demanded more homework than most. "I didn't come from an economics background, and I'm not very skilled at maths," he said. "But this would add to my knowledge about the world and educate me." The Southern dialect of Venkitaramanan — who was Tamil — added another layer. "I was scared and nervous about getting the dialect right. It's not just about the language but the culture behind it."

## Why This Matters to the Diaspora

The 1991 crisis and its aftermath didn't just restructure India's economy. It created it. The liberalisation policies that followed — dismantling the License Raj, opening India to foreign investment, unleashing the IT sector — are the direct reason millions of Indians found career paths that led them to Silicon Valley, Wall Street, the City of London, and corporate offices across North America.

Every H-1B petition filed from an Indian IT company traces its institutional lineage to what happened in those desperate weeks. Every NRI who wires money home through liberalised banking channels is benefiting from reforms that Venkitaramanan's crisis management made politically possible.

The man himself passed away on November 18, 2023, at 92. He never became a household name — not even close. The film's subtitle, "The Silent Saviour," is an acknowledgement of that obscurity.

## The Production

The film features a screenplay by Suvendu Bhattacharyjee, Saurabh Bharat, Ravi Asrani, and Vipul Shah. Music is by Amit Trivedi, with lyrics by Javed Akhtar — a pairing that signals the makers are aiming for emotional resonance, not just procedural drama. Adah Sharma and Madhoo Shah round out the cast.

Vipul Amrutlal Shah, whose production house previously delivered *The Kerala Story*, appears to be building a slate around stories pulled from India's recent institutional history — unglamorous subjects that carry national weight.

## What to Expect

If *Governor* works, it will join a small but growing category of Hindi films that treat India's economic and bureaucratic machinery as worthy of cinematic drama — alongside *Scam 1992* (the Harshad Mehta series) and portions of *Rocket Boys*. If it doesn't, the subject matter alone makes it required viewing for anyone who wants to understand why modern India exists in its current form.

For NRIs, this is personal history dressed as a political thriller. The gold went across the ocean so that, eventually, they could too.""",
    "person": "Manoj Bajpayee",
    "pexels_query": "Reserve Bank India building",
    "pexels_fallback": "gold bars vault",
})

# ─── Article 3: Masoom: The New Generation ────────────────────────────────────
articles.append({
    "headline": "Shekhar Kapur and A.R. Rahman Are Remaking Masoom. The New Version Is About Migration.",
    "subheadline": "The 1983 classic about a family secret gets a contemporary reimagining — with Naseeruddin Shah, Shabana Azmi, Manoj Bajpayee, and Nithya Menen — and themes that hit the diaspora where it lives.",
    "slug": "masoom-new-generation-shekhar-kapur-ar-rahman-migration-identity-nri-20260602",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False,
    "is_featured": False,
    "tags": [],
    "sources": json.dumps([
        "Cinema Express",
        "Zoom TV Entertainment",
        "Bollywood Hungama",
        "Devdiscourse"
    ]),
    "body": """The original *Masoom* — Shekhar Kapur's 1983 debut, adapted from Erich Segal's novel — was about an illegitimate child who arrives at a seemingly stable family's doorstep and upends everything. It starred Naseeruddin Shah and Shabana Azmi. It featured "Lakdi Ki Kaathi," one of the most recognisable children's songs in Hindi cinema. And it dealt with guilt, parenthood, and the lies families tell themselves, with a directness that still holds up four decades later.

Now Kapur is returning to that emotional territory, but with a rewrite that reflects a world the 1983 film never imagined.

## What's Changed

*Masoom: The New Generation* is billed as a "contemporary reimagining" rather than a direct sequel. According to the filmmakers, the new version will explore "evolving themes of family, love, migration, and identity through a contemporary lens." That word — migration — is doing significant work. The original *Masoom* was a domestic drama set entirely within the architecture of an Indian joint family. The new film appears to be expanding those boundaries.

Kapur explained: "For a long time, I have felt that the themes of *Masoom* deserved to be revisited through the lens of today's world. Families, relationships, identity — these ideas have evolved so much, and cinema must evolve with them."

The cast bridges the 1983 original and the present. Naseeruddin Shah and Shabana Azmi return — the first time both original leads have reprised roles in a reimagining of their own film. They're joined by Manoj Bajpayee, Nithya Menen, and Kaveri Kapur (Shekhar Kapur's daughter, who has been building a career as both an actress and singer-songwriter).

## The Rahman Factor

The headline creative reunion is between Kapur and A.R. Rahman, who are working together for the first time since *Elizabeth: The Golden Age* (2007) and their theatre collaborations *Bombay Dreams* and *Why? The Musical*. Rahman isn't just composing — he's co-producing the film, a role that signals deeper creative involvement than a standard music commission.

"Working with Shekhar has always been a deeply enriching experience — he has been a mentor and a creative force in many ways," Rahman said. "When he shared the vision for this film, I felt compelled to be involved beyond the music. There's something timeless about *Masoom*, and reinterpreting that emotional world for a new generation feels both exciting and necessary."

For diaspora audiences, Rahman's involvement is its own draw. His soundtrack for *Dil Se..* (1998) — which Kapur produced — remains one of the defining albums of '90s Bollywood, and tracks like "Chaiyya Chaiyya" are cultural touchstones for an entire generation of NRIs.

## The Diaspora Angle

The explicit inclusion of "migration" among the film's themes positions *Masoom: The New Generation* as potentially the rare mainstream Hindi film that addresses the Indian diaspora experience as a central narrative element rather than a backdrop for song sequences shot in Switzerland.

Family secrets — the engine of the original — take on different textures when set against the dislocations of migration: the identities that shift, the relationships that strain across time zones, the children who grow up between cultures, the truths that families suppress not out of malice but out of the exhaustion of reinvention.

Whether Kapur and his team land that complexity remains to be seen. The film is currently in pre-production and is expected to begin filming later this year, with a theatrical release anticipated before the end of 2026.

## A Note on Vaibhav Sooryavanshi

In a charming aside, Kapur took to X after the announcement to praise 15-year-old IPL sensation Vaibhav Sooryavanshi, writing: "If Sooryavanshi wasn't such a sensational cricketer, I could have cast him in Masoom, the film." The original *Masoom* turned child actor Jugal Hansraj into a household name. Kapur appears to still have an eye for young talent — he's just competing with the IPL for it now.""",
    "person": "Shekhar Kapur",
    "person_alt": "A. R. Rahman",
    "pexels_query": "Indian family reunion airport",
    "pexels_fallback": "family drama emotional",
})


# ── Main execution ───────────────────────────────────────────────────────────
def main():
    print(f"\n{'='*60}")
    print(f"Entertainment Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}\n")
    
    success_count = 0
    
    for i, art in enumerate(articles, 1):
        print(f"\n--- Article {i}/{len(articles)}: {art['headline'][:60]}... ---")
        
        # Extract image sourcing params
        person = art.pop("person", None)
        person_alt = art.pop("person_alt", None)
        pexels_q = art.pop("pexels_query", None)
        pexels_fb = art.pop("pexels_fallback", None)
        
        # Source image
        print("  Sourcing image...")
        img_url, attribution = source_image(
            person_name=person,
            pexels_query=pexels_q,
            pexels_fallback=pexels_fb,
            slug=art["slug"],
        )
        
        # If primary person didn't yield, try alternate
        if not img_url and person_alt:
            print(f"  Trying alternate person: {person_alt}")
            img_url, attribution = source_image(
                person_name=person_alt,
                slug=art["slug"],
            )
        
        if img_url:
            art["image_url"] = img_url
            art["image_attribution"] = attribution
            print(f"  ✓ Image set: {img_url[:60]}...")
        else:
            print("  ⚠ No image found — inserting without image")
        
        # Validate article quality
        body_words = len(art["body"].split())
        print(f"  Body: {body_words} words")
        if body_words < 400:
            print(f"  ✗ REJECTED: body too short ({body_words} words)")
            continue
        if len(art["headline"]) > 200:
            print(f"  ✗ REJECTED: headline too long ({len(art['headline'])} chars)")
            continue
        if len(art.get("subheadline", "")) < 15:
            print(f"  ✗ REJECTED: subheadline too short")
            continue
        
        # Insert
        art_id = insert_article(art)
        if art_id:
            success_count += 1
        
        time.sleep(1)  # Rate limit courtesy
    
    print(f"\n{'='*60}")
    print(f"Done. {success_count}/{len(articles)} articles published.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
