#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-05-30 batch B)
Publishes 3 news articles:
1. India's Naxal insurgency in death throes (CNN investigation)
2. Vinesh Phogat's Asian Games dream ends in semifinal heartbreak
3. US drops criminal charges against Gautam Adani
"""

import json, os, sys, time, uuid, re
import requests, urllib.parse
from datetime import datetime, timezone

# ── Supabase config ──────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

# ── Image helpers ────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
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
    """Fetch an image from Pexels. Returns URL or None."""
    if not PEXELS_API_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_API_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Check that image URL returns valid image > 5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD didn't return content-length
        if r.status_code == 200 and "image" in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
        print(f"  ⚠ Image validation failed: status={r.status_code} ct={ct} cl={cl}")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        r = requests.get(image_url, timeout=15, 
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Download failed: status={r.status_code} size={len(r.content)}")
            return None
        
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if ";" in content_type:
            content_type = content_type.split(";")[0].strip()
        
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        up = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            data=r.content,
            timeout=30,
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

def sb_insert(table, data):
    """Insert a row into Supabase and return the response."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=data,
        timeout=30,
    )
    if r.status_code in (200, 201):
        rows = r.json()
        return rows[0] if rows else data
    else:
        print(f"  ✗ Insert error: {r.status_code} {r.text[:300]}")
        return None

def sb_patch(table, match, data):
    """Update rows matching conditions."""
    params = "&".join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{params}",
        headers=HEADERS,
        json=data,
        timeout=30,
    )
    if r.status_code in (200, 204):
        return True
    else:
        print(f"  ✗ Patch error: {r.status_code} {r.text[:300]}")
        return False

# ── Articles ─────────────────────────────────────────────────────────
articles = [
    # ── Article 1: Naxal insurgency death throes ──
    {
        "headline": "India's Last Maoist Rebels Are Surrendering. A CNN Investigation Went to the Jungle to Watch.",
        "subheadline": "Papa Rao emerged from the forests of Chhattisgarh with a $26,000 bounty on his head and 17 comrades in tow. After nearly six decades, India's Naxal insurgency is in its death throes.",
        "slug": "india-naxal-maoist-insurgency-death-throes-cnn-chhattisgarh-papa-rao-surrender-20260530",
        "category": "news",
        "vertical": "news",
        "body": """Outgunned, outnumbered, and on borrowed time, a column of rebels emerged from the jungles of central India's Chhattisgarh state in March 2026. They carried decades-old Lee-Enfield and L1A1 rifles, wore scuffed sports shoes, and lugged Puma-branded backpacks. Their leader, a man known as Papa Rao, had a ₹22 lakh bounty on his head. He was there to surrender.

A CNN investigative team was waiting.

The resulting report — published Saturday — offers one of the most detailed looks yet at the final chapter of India's Naxal insurgency, a Maoist rebellion that once controlled a "Red Corridor" stretching across 20 of India's 28 states and was described by a sitting prime minister as the country's gravest internal security threat.

## The Surrender Ceremony

At a staged ceremony after their emergence, each former insurgent was handed a rose and a copy of the Indian constitution. Their antiquated weapons were laid out on tables like museum exhibits. Clips of ammunition were arranged to spell out the Hindi word for "sacred vow." Local politicians made speeches. Security forces posed for photographs.

Papa Rao and his 17 comrades were among the latest in a cascade of surrenders that has accelerated since late 2025. According to the Wikipedia-maintained timeline of the insurgency, which tracks government and media reports, mass surrenders have become near-weekly events: 86 cadres in Telangana in April, 44 more in Bijapur and Sukma in March, and a steady stream of smaller groups across Chhattisgarh, Odisha, and Jharkhand.

## "Double Digits" Remain

In Jagdalpur, the district capital of Bastar — once the epicenter of Naxal violence — Inspector General of Police Sundarraj Pattilingam told CNN the number of active Naxals in the district was down to "double digits." He reeled off a list of commanders killed in recent months, kills that he says have shattered the rebels' operational capacity.

The state has deployed its District Reserve Guard (DRG), a force formed in 2008 and largely composed of former Maoists and Adivasis — indigenous tribal people familiar with the terrain and Naxal tactics. CNN accompanied a DRG patrol into the thick forests, rivers, and hills of Bastar, where some squad members held their assault rifles with one hand, letting them dangle — a sign, perhaps, of growing confidence.

India's Home Minister Amit Shah officially declared the end of the Naxal insurgency in a parliamentary address in March, telling the Lok Sabha that the central structure of the Communist Party of India (Maoist) had been "almost completely dismantled." All state committee members in Madhya Pradesh, Maharashtra, and Chhattisgarh have surrendered, he said. In Telangana, "not a single one remains."

## Mineral Wealth and Modi's Ambitions

The Naxals' shrinking domain sits atop rich veins of coal, iron, and bauxite — resources essential to India's modernization and energy ambitions. Prime Minister Narendra Modi has pledged to bring electricity to every household and transform India into a developed nation. The clearing of insurgent-held territory opens these deposits to extraction and infrastructure development.

But the story is not one of pure military triumph. Academic Nandini Sundar, quoted in the CNN report, warned that a Naxal threat — real or imagined — provides a convenient way for the government to suppress local protests against mine openings. "This artificial deadline the government has given itself to eradicate Naxalism — it's never going to be full," she told CNN. "Because if anyone protests against the mines, they'll say, 'Oh, you know the Maoists are still there.'"

The Naxal movement, born from a 1967 peasant uprising in the village of Naxalbari in West Bengal, drew its ideology from Mao Zedong's doctrine of rural revolution. At its peak, the Communist Party of India (Maoist), formed from a 2004 merger of the two dominant wings, had an estimated 10,000 to 20,000 fighters. Thousands of security personnel, militants, and civilians have been killed over the decades.

## The End of an Era — On Every Front

In a detail that CNN frames as symbolic of a broader shift, communists are now losing not just in the jungle but at the ballot box. In state elections this month, the Left Democratic Front was voted out of Kerala — the first time in decades that Marxist political parties hold power in none of India's states or territories. The Congress-led UDF won 102 of 140 seats in a historic landslide.

For the former rebels now in government rehabilitation facilities, the transition is abrupt. Sukhmati, a former Maoist who surrendered in October 2025, told CNN — in the presence of government officials — that "our struggle became weary in the new situation and taking the movement forward was difficult."

The DRG patrols continue. The forests of Bastar remain thick. But the banner hanging over the highway into the region now advertises a public health campaign — not a security warning. The revolution, CNN concludes, is over.""",
        "sources": json.dumps([
            {"name": "CNN", "url": "https://www.cnn.com/2026/05/30/india/india-maoist-naxal-insurgency-death-throes/"},
            {"name": "Nagaland Post", "url": "https://nagalandpost.com/amit-shah-declares-india-free-from-naxals/"},
            {"name": "Wikipedia - Timeline of Naxalite-Maoist insurgency", "url": "https://en.wikipedia.org/wiki/Timeline_of_the_Naxalite%E2%80%93Maoist_insurgency"},
            {"name": "LatestLY - Kerala Election Result 2026", "url": "https://www.latestly.com/india/politics/kerala-election-result-2026/"}
        ]),
        "image_person": "Naxalite",  
        "image_search": "Indian jungle forest Chhattisgarh",
        "image_search_fallback": "dense tropical forest India patrol",
    },
    # ── Article 2: Vinesh Phogat semifinal loss ──
    {
        "headline": "Vinesh Phogat's Comeback Ends in the Semifinals. The Supreme Court Could Not Save Her on the Mat.",
        "subheadline": "A day after the Supreme Court intervened to let her compete, the Olympic wrestler lost 4-6 to Meenakshi Goyat in the Asian Games selection trials. Her dream of Aichi-Nagoya is over.",
        "slug": "vinesh-phogat-loses-asian-games-trials-semifinal-meenakshi-goyat-wrestling-20260530",
        "category": "news",
        "vertical": "news",
        "body": """The Supreme Court of India could get Vinesh Phogat to the mat. It could not keep her on it.

On Saturday, the Olympic wrestler and Haryana MLA lost 4-6 to Meenakshi Goyat in the women's 53kg semifinal at the Asian Games 2026 selection trials, ending a 48-hour saga that had involved the Supreme Court, the Wrestling Federation of India, and the kind of off-mat drama that has shadowed Indian wrestling for years.

## The Backstory

Phogat, 31, had been at the center of a bitter eligibility dispute all week. The WFI had initially restricted her to the 50kg category, a weight class she felt was unsuitable. Phogat challenged the decision. The Delhi High Court intervened to allow her participation. The WFI appealed. The Supreme Court heard the case on Friday and ruled in her favor: "Had it been someone else, the matter would have been different. She has made the country proud."

But the bench also issued a warning that would prove prophetic in more ways than one: "This is not a medical college admission matter. These are national and international sporting events. Courts should not intervene in such cases in a manner that disrupts the entire schedule."

## Saturday's Trials

By Saturday morning, the legal battles were over. WFI president Sanjay Singh confirmed Phogat's entry. She weighed in at 53.9 kg and was cleared for the 53kg bracket.

Her first bout was clinical. Against Jyoti, Phogat opened cautiously in the standing position, then turned a right-leg attack into a takedown and scored two more quick points to build a 7-0 lead. Jyoti managed a late push-out to avoid the shutout, making the final score 7-1.

The quarterfinal against Nishu was harder. The match seesawed until the closing moments, with Phogat drawing on her experience to edge a 7-6 decision. She was two wins from the Asian Games.

Then came Meenakshi Goyat.

## The Loss

The semifinal started competitively. Phogat took an early lead but Goyat, a younger and aggressive wrestler, began to find her rhythm. Counter-attacks and a takedown shifted the momentum. By the end of the second period, Goyat had built a 6-4 advantage. Phogat could not claw back.

The 4-6 scoreline ended everything: the Supreme Court intervention, the weigh-in controversy, the comeback narrative. Phogat will not represent India at the 2026 Asian Games in Aichi-Nagoya, Japan.

## What It Means

This was supposed to be the next chapter for one of India's most storied wrestlers — a woman who won bronze at the 2018 Asian Games, gold at the Commonwealth Games, and reached the final of the Tokyo Olympics before the infamous weigh-in disqualification that became a national controversy.

Since then, Phogat has been as much a political figure as an athletic one. She was elected to the Haryana assembly from Julana on a Congress ticket. She was a face of the wrestlers' protest against the WFI and former chief Brij Bhushan Sharan Singh. Her every competitive appearance carries weight beyond the sport.

Antim Panghal, who had demolished Tannu in 34 seconds in the opening round by technical superiority, is now the frontrunner in the 53kg category for the Asian Games berth.

The Supreme Court had one more observation worth recalling. Addressing Phogat directly on Friday, Justice PS Narasimha said: "You are a brilliant athlete, but the nation comes first."

On the mat in New Delhi on Saturday, the nation moved on without her.""",
        "sources": json.dumps([
            {"name": "Mint", "url": "https://www.livemint.com/sports/vinesh-phogat-fails-asian-games-2026-trials"},
            {"name": "IANS", "url": "https://ianslive.in/vinesh-phogat-fails-asian-games-semifinal-defeat-trials"},
            {"name": "Punjab Newsline", "url": "https://punjabnewsline.com/supreme-court-vinesh-phogat-asian-games-trials/"}
        ]),
        "image_person": "Vinesh Phogat",
        "image_search": "Indian wrestling competition mat",
        "image_search_fallback": "wrestling competition India",
    },
    # ── Article 3: US drops Adani charges ──
    {
        "headline": "The US Just Dropped Criminal Charges Against Gautam Adani. His Stock Surged 22% in a Month.",
        "subheadline": "The DOJ moved to dismiss the bribery case. The SEC settled for $18 million. Adani Enterprises paid $275 million to resolve Iran sanctions allegations. The legal cloud that once wiped $150 billion off the Adani empire is lifting.",
        "slug": "us-doj-drops-adani-criminal-charges-sec-settlement-stock-surge-20260530",
        "category": "news",
        "vertical": "news",
        "body": """Six months after a federal indictment in Brooklyn accused Gautam Adani of orchestrating a $250 million bribery scheme, the United States government is walking away from the case.

The Department of Justice moved on May 19 to drop criminal charges against Asia's richest man, his nephew Sagar Adani, and former Adani Green Energy chief executive Vneet Jaain. The Securities and Exchange Commission settled its parallel civil fraud case for $18 million. And Adani Enterprises agreed to pay $275 million to resolve a separate Treasury Department probe into alleged Iran sanctions violations.

The combined effect was swift. Adani Enterprises surged 22% in May, making it the best-performing stock on the BSE Sensex in a month when the benchmark itself fell 2.8%.

## What the Original Case Alleged

The indictment, unsealed in November 2024, accused Adani, his nephew, and Jaain of conspiring to pay approximately $265 million in bribes to Indian government officials to secure solar energy contracts worth billions of dollars. The arrangement involved Adani Green Energy's deal to supply 12 gigawatts of solar power to the Indian government — enough to power millions of homes.

Prosecutors painted a picture of two-faced dealmaking: the defendants allegedly told Wall Street investors the contracts were above-board while, behind the scenes in India, they were paying or promising to pay government officials. A $750 million bond offering in 2021 was allegedly marketed on the basis of materially false and misleading statements.

The charges landed like a bomb. Shares across the Adani Group plunged. Credit agencies downgraded Adani Green bonds. International banks paused lending. The conglomerate's market capitalization, which had already been battered by the Hindenburg Research short-seller report in January 2023, took another massive hit.

## How It Unraveled

The resolution came in stages over the past two weeks. The SEC settlement — $18 million without admitting or denying wrongdoing — came first. The DOJ's motion to dismiss the criminal charges followed. Then came the $275 million OFAC settlement, resolving allegations that Adani Enterprises had purchased liquefied petroleum gas originating from Iran in violation of US sanctions.

The combined $293 million in settlements is substantial. But for a conglomerate with a market capitalization exceeding $250 billion, it is manageable. More importantly, it removes what analysts had called the single largest regulatory overhang on the group.

"This removes a big regulatory overhang on the Adani Group," said Shriram Subramanian, founder of InGovern Research Services, a proxy advisory firm based in India. "More importantly, it paves the way for settlement of other regulatory scrutiny."

## The Geopolitical Backdrop

The reversal has not gone unnoticed as a signal of the broader US-India relationship under the Trump administration. When the charges were first filed under the Biden administration, they strained diplomatic ties at a moment when Washington was actively courting New Delhi as a counterweight to China.

Forbes published an article calling the original indictment "a strategic blunder" that "risks damaging India-US relations at a time when Washington is actively seeking stronger alliances." Indian commentators noted that the dismissal came months after Prime Minister Modi's state visit to Washington and amid expanding US-India defense cooperation.

The Adani Group has not commented publicly on the settlements beyond confirming them. Gautam Adani, 63, remains chairman of the conglomerate and is worth approximately $60.6 billion, ranking 30th worldwide according to Forbes.

## What Remains

While the US legal actions are resolved, questions linger. The underlying bribery allegations — that Indian government officials were paid or promised money to secure solar contracts — have not been adjudicated on the merits. The DOJ's motion to dismiss does not constitute an exoneration; it means prosecutors chose not to pursue the case.

In India, opposition parties have called for a domestic investigation. The ruling BJP has dismissed the original charges as politically motivated interference by a foreign government.

For investors, the resolution is unambiguous. The 22% May surge in Adani Enterprises reflects a market that has decided the worst is over. International bond markets are reopening. Lending pipelines are resuming. The $150 billion in value that was erased between Hindenburg and the DOJ indictment is being rebuilt, one settlement at a time.""",
        "sources": json.dumps([
            {"name": "Reuters / I3investor", "url": "https://klse.i3investor.com/us-seeks-to-drop-criminal-charges-adani"},
            {"name": "FCPA Professor", "url": "https://fcpaprofessor.com/adanis-to-seek-dismissal/"},
            {"name": "Reuters - Indian equity benchmarks", "url": "https://www.reuters.com/markets/india-equity-benchmarks-monthly-losses/"},
            {"name": "India Tribune / Forbes", "url": "https://indiatribune.com/us-doj-indictment-adani-strategic-blunder/"}
        ]),
        "image_person": "Gautam Adani",
        "image_search": "Adani Group headquarters India",
        "image_search_fallback": "Indian business corporate headquarters",
    },
]

# ── Publish ──────────────────────────────────────────────────────────
published = 0
for i, art in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Article {i+1}: {art['headline'][:70]}...")
    
    # Image sourcing
    img_url = None
    img_attribution = None
    
    # Try Wikipedia for person articles
    person = art.get("image_person")
    if person and person != "Naxalite":  # Skip generic terms
        img_url = fetch_wikipedia_person_image(person)
        if img_url:
            img_attribution = "Wikimedia Commons"
    
    # Try Pexels fallback
    if not img_url:
        img_url = fetch_pexels_image(art["image_search"], art.get("image_search_fallback"))
        if img_url:
            img_attribution = "Pexels"
    
    # Validate and upload
    final_image_url = None
    if img_url:
        if validate_image(img_url):
            art_id = str(uuid.uuid4())
            ext = "jpg"
            filename = f"{art_id}.{ext}"
            final_image_url = upload_to_supabase_storage(img_url, filename)
            if not final_image_url:
                # Try direct URL if upload fails
                final_image_url = img_url if "upload.wikimedia.org" in img_url or "images.pexels.com" in img_url else None
        else:
            print(f"  ⚠ Image failed validation, trying direct URL")
            if "upload.wikimedia.org" in img_url or "images.pexels.com" in img_url:
                final_image_url = img_url
    
    if not final_image_url:
        print(f"  ⚠ No image found — publishing without image")
    
    # Build article record
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    record = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "category": art["category"],
        "vertical": art["vertical"],
        "body": art["body"],
        "sources": json.loads(art["sources"]),
        "image_url": final_image_url,
        "image_attribution": img_attribution,
        "status": "published",
        "published_at": now,
    }
    
    result = sb_insert("p2_articles", record)
    if result:
        print(f"  ✓ Published: {art['slug']}")
        published += 1
    else:
        print(f"  ✗ FAILED to publish: {art['slug']}")
    
    time.sleep(1)  # Rate limit

print(f"\n{'='*60}")
print(f"Done. Published {published}/{len(articles)} articles.")
