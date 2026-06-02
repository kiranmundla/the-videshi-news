#!/usr/bin/env python3
"""News writer for The Videshi — June 2, 2026 batch"""

import json, os, sys, uuid, re, time
from datetime import datetime, timezone

import requests

# ── Env ──────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY   = os.environ.get("PEXELS_API_KEY", "")
HEADERS      = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Helpers ──────────────────────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
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
    """Fetch a relevant image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                    if url:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        resp = requests.get(image_url, timeout=15, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if resp.status_code != 200:
            print(f"  ⚠ Image download failed: HTTP {resp.status_code}")
            return None
        content_type = resp.headers.get("Content-Type", "image/jpeg")
        if not content_type.startswith("image/"):
            print(f"  ⚠ Not an image: {content_type}")
            return None
        if len(resp.content) < 5000:
            print(f"  ⚠ Image too small: {len(resp.content)} bytes")
            return None

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        up = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            data=resp.content,
            timeout=20,
        )
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {up.status_code} {up.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def validate_image(url):
    """Quick HTTP HEAD to validate an image URL."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD didn't return Content-Length
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            r2.close()
            if len(chunk) > 5000:
                return True
    except Exception:
        pass
    return False


def insert_article(article):
    """Insert an article into p2_articles."""
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=15,
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Inserted article: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {resp.status_code} {resp.text[:300]}")
        return None


# ── Articles ─────────────────────────────────────────────────────────

now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

articles = []

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 1: India-US Trade Deal 99% Complete
# ═══════════════════════════════════════════════════════════════════

articles.append({
    "headline": "India and the US Are Now in the Final Hours of a Trade Deal. The Ambassador Says It Is 99% Done.",
    "subheadline": "A three-day negotiating round in New Delhi could produce the first bilateral trade agreement between the world's largest and fifth-largest economies. The sticking point is Section 301.",
    "slug": "india-us-trade-deal-99-percent-done-section-301-brendan-lynch-delhi-june-20260602",
    "category": "news",
    "status": "published",
    "published_at": now_iso,
    "is_editorial": False,
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com"},
        {"name": "Devdiscourse", "url": "https://www.devdiscourse.com"},
        {"name": "Dainik Bhaskar English", "url": "https://bhaskarenglish.in"}
    ]),
    "body": """India and the United States are closer to signing a bilateral trade agreement than they have ever been. Union Commerce Minister Piyush Goyal confirmed on Monday that the framework of the interim deal is complete, and US Ambassador to India Sergio Gor said that 99 percent of the terms have been settled.

## The Final Round Begins in Delhi

A high-level American delegation led by Chief Negotiator Brendan Lynch arrived in New Delhi on Sunday for a four-day visit running from June 1 to 4. The Indian team is headed by Additional Secretary Darpan Jain, the country's chief trade negotiator.

The objective of this round is to give the interim agreement its final legal shape. The framework was agreed in a Joint Statement on February 7, when both nations committed to a first-tranche deal covering reciprocal market access, non-tariff measures, customs facilitation, investment promotion, and economic security alignment.

"Technical issues remain, but the framework is complete," Goyal said at the launch of the India-Oman CEPA on Monday. "The US team is part of this crucial three-day discussion."

## The Section 301 Problem

The deal nearly fell apart in March when the US Supreme Court struck down Trump's sweeping reciprocal tariff measures. The administration then launched Section 301 investigations under the Trade Act of 1974 into several countries, including India, over excess capacity and forced labour in supply chains.

India has firmly rejected the allegations and is now seeking tariff relief from any measures that emerge from the probe. A senior Indian trade official told reporters that New Delhi wants "a competitive tariff rate versus direct competition" and expects preferential treatment compared with Bangladesh, Pakistan, and Sri Lanka — rival manufacturing hubs that compete for the same orders.

India currently faces a blanket 10 percent tariff on exports to the United States after the court ruling left that baseline levy in place.

## What India Is Offering

Under the agreed framework, India has proposed to eliminate or reduce tariffs on all US industrial goods and a wide range of food and agricultural products, including dried distillers' grains, red sorghum for animal feed, tree nuts, fresh fruit, soybean oil, wine, and spirits.

New Delhi has also committed to purchasing $500 billion worth of American energy products, aircraft and aircraft parts, precious metals, technology products, and coking coal over the next five years — a staggering figure that underscores how much India is willing to invest in the relationship.

## A Relationship That Has Grown Tenfold

Bilateral trade in goods and services has surged from $20 billion to over $220 billion in the past two decades, making the US India's second-largest trading partner. India's exports to the US stood at $87.3 billion in fiscal 2025-26, while imports grew 16 percent to $52.9 billion. India's trade surplus narrowed to $34.4 billion from $40.9 billion the previous year.

US Trade Representative Jamieson Greer could visit India once the broad contours are finalized, signalling that a signing is imminent.

## What This Means for the Diaspora

For the roughly 4.5 million Indian Americans and the broader NRI community, this deal is about more than tariff schedules. A strengthened economic relationship means more business opportunities, easier movement of goods and capital, and a deeper strategic alignment between the two countries they call home.

The deal also arrives at a sensitive moment. With the Iran war pushing oil prices above $90 a barrel and India scrambling to diversify its energy sources, a formal commitment to purchase American energy at preferential terms could help stabilize the country's import bill — and, by extension, the rupee.

If both sides can settle the Section 301 question, a signing could come within weeks. If they cannot, the talks will continue — but the window may not stay open for long.""",
    "vertical": "trade",
    "diaspora_angle": "A strengthened India-US trade corridor means more business opportunities, easier capital flows, and deeper strategic alignment for the 4.5 million Indian Americans. India's $500 billion purchase commitment over five years — covering energy, aircraft, and tech — could reshape job markets and investment patterns on both sides of the Pacific.",
    "tags": ["india-us-trade", "section-301", "bilateral-trade-agreement", "piyush-goyal", "brendan-lynch", "tariffs"],
    "image_search_person": None,
    "image_search_pexels": ("India US trade agreement handshake diplomacy", "diplomatic negotiation conference room"),
    "image_attribution": "Pexels",
})

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 2: Dave Fiji — Indian-Origin Delta Pilot Killed in Crash
# ═══════════════════════════════════════════════════════════════════

articles.append({
    "headline": "A 25-Year-Old Keralite Delta Pilot Was Killed in a Helicopter Crash Hours After His Wedding. His Bride Survived.",
    "subheadline": "Dave Fiji, a first officer at Delta Air Lines, had warned the pilot about zero visibility before takeoff. His wife Jesni was trapped in the wreckage for six hours.",
    "slug": "dave-fiji-indian-origin-delta-pilot-killed-helicopter-crash-wedding-georgia-20260602",
    "category": "news",
    "status": "published",
    "published_at": now_iso,
    "is_editorial": False,
    "sources": json.dumps([
        {"name": "WSB-TV / Atlanta News First", "url": "https://www.wsbtv.com"},
        {"name": "PEOPLE Magazine", "url": "https://people.com"},
        {"name": "FOX 5 Atlanta", "url": "https://www.fox5atlanta.com"},
        {"name": "Livemint", "url": "https://www.livemint.com"},
        {"name": "New York Post", "url": "https://nypost.com"}
    ]),
    "body": """Dave Fiji had dreamt of flying since he was ten years old. By 25, the son of Keralite immigrants had become a first officer at Delta Air Lines — one of the youngest pilots at the carrier. On Friday evening, at a wedding venue in Dawsonville, Georgia, he married Jesni in front of roughly 400 guests.

Hours later, he was dead.

## A Perfect Wedding, a Devastating Exit

The ceremony at The Revere, a wedding and events venue in the foothills north of Atlanta, was by all accounts a joyous affair. "We could say it was the perfect wedding," Dave's father, George Fiji, told WSB-TV. "We couldn't ask for anything more."

A special helicopter departure had been arranged for the newlyweds. The couple boarded a Robinson R66 helicopter around 9:30 p.m., bound for DeKalb-Peachtree Airport in Chamblee, from where they planned to begin their honeymoon.

But by that point, dense fog and rain had rolled into the area. Visibility had dropped to near zero.

## He Knew It Was Dangerous

Dave Fiji was not only a passenger — he was an experienced pilot. And he flagged the danger before takeoff.

"Since my son was a pilot, he told the pilot that there is zero visibility, and when there is zero visibility like this, we never fly," George Fiji said.

Jesni later told her father-in-law that the helicopter pilot said they would fly at a higher altitude to clear the fog. The couple decided to go ahead.

Within minutes, the Robinson R66 struck tall trees and crashed into a heavily wooded area on a 10,000-acre tract owned by the City of Atlanta, managed by the state as a wildlife management area. The crash occurred around 10:30 p.m., not far from the wedding venue.

## Trapped for Six Hours

Both Dave and the helicopter pilot were killed on impact. Jesni survived.

"She said when she woke up she saw my son, Dave, resting on her bosom," George Fiji recalled. "She saw blood on him, but by then, his body was completely cold. She's a nurse, so she knew he was gone."

Jesni remained trapped in the wreckage for nearly six hours before rescuers located the crash site and extracted her. She suffered cuts and bruises but no broken bones. She is recovering at a metro Atlanta hospital.

"She's devastated, but she's recovering," George Fiji said.

## A Keralite Family's American Dream

Dave's parents, George and Pheba Fiji, emigrated to the United States from Muvattupuzha in Ernakulam district, Kerala. Jesni's family also hails from Alappuzha district in Kerala. The two families had ties through church communities in South Carolina and Georgia.

Dave and Jesni first met through their church about ten years ago. Their friendship grew into love, and they decided to build a life together. Family members described Dave as disciplined, selfless, and deeply passionate about aviation.

"He was kind, he was gentle, he was selfless. Those were her words," said Dave's mother, Pheba. "We have the confidence that God perfected the work that he started in his life."

## The Investigation

The National Transportation Safety Board is leading the investigation. In a statement, the NTSB said that initial impact signatures show the helicopter struck tall trees followed by an impact with terrain in a heavily wooded area. There was no post-impact fire.

NTSB meteorologists are conducting a weather study to understand the role conditions may have played. Preliminary data shows the potential for rain showers, low-level clouds, and thunderstorms in the vicinity at the time of the crash.

The helicopter belonged to Prestige Helicopters, which operates out of DeKalb-Peachtree Airport and provides chartered flights for wedding venues around the Atlanta area. All major pieces of the aircraft have been recovered.

The identity of the helicopter pilot has not yet been released.

## A Community in Mourning

The Keralite diaspora in the Atlanta area and across the United States has been shaken by the tragedy. For a community that celebrates ambition, faith, and family, Dave Fiji's story — a boy from an immigrant household who achieved his dream of flying, only to be taken on the happiest day of his life — carries a particular weight.

Jesni, who now carries the title of wife and widow within the span of a single evening, faces a recovery that goes far beyond the physical.""",
    "vertical": "nri-world",
    "diaspora_angle": "Dave Fiji's parents emigrated from Muvattupuzha in Ernakulam, Kerala. His wife Jesni's family hails from Alappuzha. The couple met through the Keralite church community in Georgia. The tragedy has shaken the Indian American community in Atlanta and beyond — a story of an immigrant family's American dream cut short on the happiest day of their son's life.",
    "tags": ["indian-american", "keralite-diaspora", "delta-air-lines", "helicopter-crash", "georgia", "dave-fiji"],
    "image_search_person": None,
    "image_search_pexels": ("helicopter crash wooded area emergency", "Robinson R66 helicopter aviation"),
    "image_attribution": "Pexels",
})

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 3: Iran Reviewing Deal Text — Fresh Update
# ═══════════════════════════════════════════════════════════════════

articles.append({
    "headline": "Iran Is Now Reviewing the Text of a Deal to End the War. Trump Says It Will Be Done Within a Week.",
    "subheadline": "After freezing talks on Monday, Tehran reversed course within hours. Oil prices fell 1% on Tuesday, but the IEA warns global inventories could hit historic lows.",
    "slug": "iran-reviewing-deal-text-hormuz-reopen-trump-one-week-oil-india-20260602",
    "category": "news",
    "status": "published",
    "published_at": now_iso,
    "is_editorial": False,
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "NBC Palm Springs", "url": "https://nbcpalmsprings.com"},
        {"name": "Fox News", "url": "https://www.foxnews.com"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com"},
        {"name": "Investopedia", "url": "https://www.investopedia.com"}
    ]),
    "body": """Iran is reviewing a proposed agreement with the United States to halt the war between the two countries, Iran's semi-official Mehr news agency reported on Tuesday. The development came less than 24 hours after Tehran said it was freezing all communications with Washington.

## The Whiplash

The speed of the reversal has been dizzying. On Monday morning, Iran's IRGC-affiliated Tasnim news agency announced that Tehran was suspending all talks with the US, ostensibly over Israel's expanding military operations against Hezbollah in Lebanon. Iran's Parliament Speaker Mohammad Bagher Qalibaf warned of "direct confrontation" if Israeli aggression continued.

By Monday evening, President Trump had intervened. He said he spoke with Israeli Prime Minister Netanyahu and asked him not to carry out a planned strike on Beirut's southern suburbs. He also said he had communicated with Hezbollah through intermediaries — the first time a US president has done so, even indirectly, with the group Washington designates as a terrorist organization.

A partial ceasefire was announced by Lebanon: Israel would refrain from strikes on Beirut and Hezbollah-controlled suburbs, while the Iran-aligned group would halt attacks on Israel. Lebanon said it would seek to expand the arrangement in talks with Israel in Washington on Wednesday.

By Tuesday, Iran had pivoted from threatening to "completely block" the Strait of Hormuz to reviewing the proposed text of a deal.

## What Iran Wants

According to Mehr, Iran is taking a "stern" approach to the proposed final text, citing a history of US non-compliance and deep institutional mistrust. Tehran is pushing for a limited interim agreement that would ease economic pressure without requiring major concessions on its nuclear programme.

Iran's demands include an end to hostilities across all fronts including Lebanon, access to billions of dollars in frozen oil revenues, waivers on crude exports, a lifting of the US blockade on its ports, and continued leverage over the Strait of Hormuz.

Trump, for his part, wants the strait reopened immediately, followed by a 60-day window for talks on Iran's nuclear programme and its enriched uranium stockpiles — much of which was destroyed by US strikes earlier this year. Secretary of State Marco Rubio said the strait needs to be "open, unimpeded, without tolls, and obviously that needs to happen immediately."

## The Oil Market Exhales — Barely

Oil prices fell more than 1 percent on Tuesday, paring Monday's sharp gains. Brent crude slipped from around $97 to roughly $96 a barrel. But the relief is fragile.

A senior International Energy Agency official warned that global oil inventories could hit historically low levels within weeks. An ExxonMobil executive said at a conference last week that prices could soar to $160 a barrel once stockpile buffers are exhausted.

Goldman Sachs expects refined fuel margins to remain two to three times above historical averages through the rest of 2026, with diesel margins exceeding pre-war forecasts by $19 to $26 per barrel.

## What This Means for India

India's Finance Ministry has identified the Hormuz disruption as the single most consequential variable for the country's external balance and price outlook. Gulf oil imports have fallen 34 percent since the war began in February, and Indian refiners have scrambled to secure alternative supplies from Venezuela, Brazil, Angola, and Nigeria.

Even a best-case scenario is grim for Indian consumers. Analysts at Societe Generale estimate that even if a deal is ratified immediately, physical flows through the strait would not resume until late August, and crude would not reach Asian end-consumers until late October at the earliest.

Meanwhile, India's current account deficit is widening, the rupee is under pressure, and the RBI meets this week facing calls to raise interest rates purely to defend the currency — a step most economists believe the central bank will resist.

## The Clock Is Ticking

Trump said on Monday that a deal to reopen the Strait of Hormuz would come within a week. He has said this before — repeatedly, since mid-March. Each time, the timeline has slipped.

What has changed is the domestic political pressure. Congress is closing in on a war powers resolution that would end the Iran conflict without Trump's authorization. Rubio will testify publicly before the Senate Foreign Relations Committee and House Foreign Affairs Committee this week — his first public testimony on the war.

Even Trump's own Republicans want the gasoline prices down before November. Representative Thomas Massie of Kentucky put it in plain terms: "The farmers here in Kentucky can't afford the fertilizer to put on their fields, so heck yes, I would support it."

For India, for the diaspora, and for the 80 percent of Asian oil that used to flow through the strait, the question is no longer whether a deal will happen. It is whether it will happen in time.""",
    "vertical": "geopolitics",
    "diaspora_angle": "India's Finance Ministry has called the Hormuz disruption the single most consequential variable for the country's external balance. Gulf oil imports are down 34%. Even a best-case deal would not deliver relief to Indian consumers until late October. The RBI faces pressure to raise rates to defend the rupee, and the current account deficit is widening. For NRIs sending money home, the rupee's trajectory is directly tied to this conflict.",
    "tags": ["iran-war", "hormuz", "oil-prices", "india-oil", "ceasefire", "trump-iran-deal", "rbi"],
    "image_search_person": None,
    "image_search_pexels": ("Strait of Hormuz oil tanker shipping", "oil tanker Persian Gulf"),
    "image_attribution": "Pexels",
})


# ── Main Loop ────────────────────────────────────────────────────────

def main():
    success_count = 0
    for i, art in enumerate(articles):
        print(f"\n{'='*60}")
        print(f"Article {i+1}: {art['headline'][:80]}...")
        print(f"{'='*60}")

        # ── Image sourcing ──
        image_url = None

        # Try Wikipedia for person articles
        if art.get("image_search_person"):
            image_url = fetch_wikipedia_person_image(art["image_search_person"])

        # Fall back to Pexels
        if not image_url and art.get("image_search_pexels"):
            q1, q2 = art["image_search_pexels"]
            image_url = fetch_pexels_image(q1, q2)

        # Upload to Supabase for permanence
        final_image_url = None
        if image_url:
            filename = f"{art['slug']}.jpg"
            final_image_url = upload_image_to_supabase(image_url, filename)
            if not final_image_url:
                # If upload fails, use Pexels/Wikipedia URL directly if it's permanent
                if "images.pexels.com" in image_url or "upload.wikimedia.org" in image_url:
                    if validate_image(image_url):
                        final_image_url = image_url
                        print(f"  ℹ Using direct permanent URL: {image_url[:80]}...")

        # ── Build insert payload ──
        payload = {
            "headline": art["headline"],
            "subheadline": art["subheadline"],
            "slug": art["slug"],
            "category": art["category"],
            "status": art["status"],
            "published_at": art["published_at"],
            "is_editorial": False,
            "sources": art["sources"],
            "body": art["body"],
        }
        if final_image_url:
            payload["image_url"] = final_image_url
            payload["image_attribution"] = art.get("image_attribution", "The Videshi")

        # Add vertical, diaspora_angle, tags
        if art.get("vertical"):
            payload["vertical"] = art["vertical"]
        if art.get("diaspora_angle"):
            payload["diaspora_angle"] = art["diaspora_angle"]
        if art.get("tags"):
            payload["tags"] = art["tags"]

        # Remove helper fields that aren't DB columns
        for key in ["image_search_person", "image_search_pexels"]:
            payload.pop(key, None)

        art_id = insert_article(payload)
        if art_id:
            success_count += 1

            # If we uploaded to Supabase and have an art_id, update image
            if final_image_url and final_image_url.startswith(SUPABASE_URL):
                # Rename with article ID for consistency
                pass  # already uploaded with slug name, that's fine

        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Done. {success_count}/{len(articles)} articles published.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
