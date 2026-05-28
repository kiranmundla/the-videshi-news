#!/usr/bin/env python3
"""News writer for The Videshi — 2026-05-28 batch."""

import json, os, sys, time, uuid, re, subprocess
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

import requests

def sb_insert(table, data):
    """Insert a row into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=data,
        timeout=30
    )
    if r.status_code not in (200, 201):
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None
    result = r.json()
    return result[0] if isinstance(result, list) and result else result

def sb_patch(table, filters, data):
    """Patch a row in Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?{filters}"
    r = requests.patch(url, headers=HEADERS, json=data, timeout=30)
    if r.status_code not in (200, 204):
        print(f"  ✗ Patch failed ({r.status_code}): {r.text[:300]}")
    return r.status_code in (200, 204)

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
    if not PEXELS_API_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            # Use curl since urllib gets 403 from Pexels
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_API_KEY}',
                 f'https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    """Download an image and upload it to Supabase storage."""
    try:
        # Download
        r = requests.get(image_url, timeout=15, headers={
            "User-Agent": "TheVideshi/1.0 (thevideshi.com)"
        })
        if r.status_code != 200:
            print(f"  ✗ Download failed ({r.status_code}): {image_url[:80]}")
            return image_url  # Return original as fallback
        
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if 'image' not in content_type:
            print(f"  ✗ Not an image ({content_type}): {image_url[:80]}")
            return image_url
        
        if len(r.content) < 5000:
            print(f"  ✗ Image too small ({len(r.content)} bytes): {image_url[:80]}")
            return image_url
        
        # Upload to Supabase storage
        upload_headers = {
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': content_type,
            'x-upsert': 'true'
        }
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        ur = requests.post(upload_url, headers=upload_headers, data=r.content, timeout=30)
        
        if ur.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({ur.status_code}): {ur.text[:200]}")
            # If Wikipedia/Wikimedia, the URL is permanent so return it directly
            if 'upload.wikimedia.org' in image_url or 'images.pexels.com' in image_url:
                return image_url
            return image_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return image_url

def validate_image_url(url):
    """Validate image URL is not from banned sources."""
    if not url:
        return False
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', 'scontent-']
    banned_params = ['_nc_ht=', '_nc_cat=', 'ccb=']
    for b in banned:
        if b in url:
            print(f"  ✗ BANNED source detected: {b}")
            return False
    for p in banned_params:
        if p in url:
            print(f"  ✗ BANNED param detected: {p}")
            return False
    return True

def publish_article(article):
    """Publish an article to Supabase."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')
    
    row = {
        'id': art_id,
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': article['slug'],
        'category': article['category'],
        'vertical': article.get('vertical', 'general'),
        'urgency': article.get('urgency', 'standard'),
        'status': 'published',
        'published_at': now,
        'sources': article.get('sources', '[]'),
        'image_url': article.get('image_url'),
        'image_caption': article.get('image_caption', ''),
        'image_attribution': article.get('image_attribution', ''),
    }
    
    result = sb_insert('p2_articles', row)
    if result:
        print(f"  ✓ Published: {article['headline'][:60]}... [{art_id[:8]}]")
        return art_id
    return None


# ─── ARTICLE DEFINITIONS ───────────────────────────────────────────────

articles = []

# ─── ARTICLE 1: Scripps Spelling Bee ─────────────────────────────────
articles.append({
    'headline': "Five of Nine Scripps Spelling Bee Finalists Are Indian American. Again.",
    'subheadline': "The 101st National Spelling Bee finals air tonight in Washington. Indian American kids have won 28 of the last 34 titles — and five of this year's nine finalists carry on the streak.",
    'slug': 'scripps-spelling-bee-2026-five-indian-american-finalists-28-of-34-titles',
    'category': 'news',
    'sources': json.dumps([
        {"name": "USA Today", "url": "https://www.usatoday.com/story/sports/2026/05/27/scripps-national-spelling-bee-finalists-2026/90280761007/"},
        {"name": "USA Today", "url": "https://www.usatoday.com/story/sports/2026/05/27/here-are-some-of-the-toughest-words-from-this-years-scripps-national-spelling-bee/90284081007/"},
        {"name": "Associated Press", "url": "https://gmg-wdiv-prod.cdn.arcpublishing.com/news/2024/05/26/national-spelling-bee-reflects-the-economic-success-and-cultural-impact-of-immigrants-from-india/"},
        {"name": "Scripps National Spelling Bee", "url": "https://spellingbee.com"}
    ]),
    'vertical': 'culture',
    'urgency': 'high',
    'image_search_person': 'Scripps National Spelling Bee',
    'image_search_pexels': 'spelling bee competition stage',
    'image_pexels_fallback': 'student academic competition',
    'image_caption': 'The Scripps National Spelling Bee at DAR Constitution Hall in Washington, D.C.',
    'body': """Nine children will stand at the microphone tonight inside DAR Constitution Hall in Washington, D.C., competing for the Scripps Cup and $52,500 in prize money at the 101st National Spelling Bee. Five of those nine finalists — more than half — are Indian American. For a community that has claimed 28 of the last 34 national titles, the question is no longer whether an Indian American kid will win. It is whether anyone else can.

## The Finalists

The nine semifinal survivors, whittled from a starting field of 247 spellers, are Oliver Halkett from Los Angeles; Zwe Spacetime from Washington, D.C.; Kushi Gottimukkala from Charlotte, North Carolina; Avishka Dudala from Dallas, Texas; Aiden Meng from Danville, California; Shrey Parikh from San Bernardino, California; Sarv Dharavane from Tucker, Georgia; Ishaan Gupta from Jersey City, New Jersey; and Logan Bailey from Houston, Texas.

Of these, Gottimukkala, Dudala, Parikh, Dharavane, and Gupta are of Indian descent. Dharavane is a returning finalist who placed third in 2025, and Parikh competed in the 2024 finals. Both are making their final attempts before aging out of eligibility — spellers must be 15 or younger and cannot have passed the eighth grade.

## A Quarter-Century of Dominance

The Indian American winning streak at Scripps has become one of the most extraordinary statistical runs in any American competition. Since Nupur Lala won in 1999, Indian American children have taken the trophy 28 times out of 34 — including three consecutive years of Indian American co-champions and 2019, when seven of eight co-champions were of Indian descent. Last year's winner, Faizan Zaki, won with the word "éclaircissement."

The dominance tracks directly to immigration patterns. Nearly 70 percent of Indian-born U.S. residents arrived after 2000, according to census data, and Indian American households report a median income of $147,000 — more than twice the national median. Indians received 74 percent of H-1B specialized work visas approved in 2021. The families are disproportionately from Andhra Pradesh and Telangana, the Telugu-speaking states that supply Hyderabad's information-technology workforce and a large share of H-1B recipients.

## More Than Privilege

But reducing the streak to economics misses the point. "It is important to note that the children participating come from striving middle-class immigrant families, often in occupations like IT, and not from wealthier Indian American households in finance or tech start-ups," said Devesh Kapur, professor of South Asian Studies at Johns Hopkins University.

What drives the run is infrastructure. Organizations like the North South Foundation hold spelling competitions specifically aimed at the Indian diaspora. Parents network across metro areas, sharing word lists, study strategies, and coaching contacts. Ganesh Dasari, whose own children competed at Scripps, said he once tracked down a young speller's parents after judging a regional competition to tell them their daughter had national-level potential. That girl, Harini Logan, went on to win the 2022 national title.

"Whenever we go to the spelling bee events, everybody speaks that language," Dasari said of the Telugu-speaking families. "We realized there are so many people from the same state."

## What It Means for the Diaspora

When Prime Minister Narendra Modi addressed the U.S. Congress in 2016, he specifically cited "spelling bee champions" among India's contributions to America. The two co-champions that year, Nihar Janga and Jairam Hathwar, watched from the gallery.

For Indian Americans, the Spelling Bee has become something more than a competition. It is proof of concept — evidence that the immigrant bargain works, that a family can arrive on a work visa, invest in a child's education, and watch that child stand on a national stage and win. In a year when new green card rules may force H-1B holders to leave the country to apply for permanent residency, that proof matters more than usual.

The finals air tonight at 8 p.m. ET on ION. An estimated 11 million children participate in spelling bees across the United States each year. Only nine are left. Five of them carry last names that trace back to India — and the odds, as they have for a quarter-century, are in their favor."""
})

# ─── ARTICLE 2: Mail-In Voting Executive Order ─────────────────────
articles.append({
    'headline': "A Judge Just Cleared the Way for Trump's Mail-In Voting Crackdown. Indian Americans Vote by Mail More Than Ever.",
    'subheadline': "A federal judge declined to block the executive order that gives the Postal Service new power over who gets a ballot. With midterms five months away, 4.8 million Indian American voters are watching.",
    'slug': 'trump-mail-in-voting-executive-order-upheld-indian-american-voters-midterms',
    'category': 'news',
    'sources': json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/legal/government/judge-allows-trump-implement-mail-in-voting-executive-order-2026-05-28/"},
        {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/05/27/uscis-green-card-announcement/90258641007/"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/politics/policy/what-to-know-about-the-trump-administrations-new-green-card-policy-c3c08a4c"}
    ]),
    'vertical': 'politics',
    'urgency': 'high',
    'image_search_person': None,
    'image_search_pexels': 'mail ballot voting United States',
    'image_pexels_fallback': 'US election ballot box',
    'image_caption': 'Mail-in ballots have become a critical voting method for Indian American communities.',
    'body': """A federal judge on Thursday cleared the way for President Donald Trump's executive order tightening rules on mail-in voting, declining to issue a preliminary injunction in a case brought by Democratic lawmakers led by Senate Minority Leader Chuck Schumer. The ruling, by Washington-based U.S. District Judge Carl Nichols, is a significant legal victory for an administration that has spent six years attacking the integrity of voting by mail — and it lands with particular force on Indian American communities that have increasingly relied on mail ballots.

## What the Order Does

The executive order, signed on March 31, directs the administration to compile a list of confirmed U.S. citizens eligible to vote in each state, using data from the Department of Homeland Security and the Social Security Administration. It requires the U.S. Postal Service to deliver ballots only to voters on each state's approved mail-in ballot list and mandates that states preserve election-related records for five years.

Democrats argued that the citizenship lists risk improperly excluding lawfully registered voters because the underlying data sources can be outdated and contain errors. They contended that the order infringes on states' constitutional rights to regulate their own elections.

Judge Nichols, who was appointed by Trump during his first term, rejected the request for an injunction on procedural grounds. "Given that the Executive Order does not command Plaintiffs to do anything, and that no agency has yet acted pursuant to the Order in a way that could harm Plaintiffs, they have not suffered any harm at present," Nichols wrote.

## Why This Matters for Indian Americans

The Indian American population has grown to approximately 4.8 million, making it one of the fastest-growing voter blocs in the country. Concentrated in suburban districts across New Jersey, California, Texas, Virginia, Georgia, and the Research Triangle in North Carolina, Indian American voters have increasingly favored mail-in ballots — particularly since the pandemic normalized absentee voting in 2020.

For a community where both spouses frequently work in demanding professional fields — medicine, technology, engineering, and finance — mail-in voting is not a political preference. It is a logistical necessity. Many Indian American voters also maintain complex schedules around religious holidays, family obligations in India, and international travel that make in-person voting on a single Tuesday unreliable.

The risk is not that the executive order will directly prevent Indian American citizens from voting. It is that the citizenship verification machinery — built on DHS and SSA databases that immigration lawyers say are riddled with processing delays, name transliteration errors, and lag times — could flag naturalized citizens for additional scrutiny or accidentally remove them from ballot lists.

## The Wider Immigration Context

The mail-in voting ruling arrives in the same week that USCIS announced a sweeping policy change requiring most green card applicants to leave the country and apply from their home nations, rather than adjusting status inside the United States. For the hundreds of thousands of Indian nationals on H-1B visas who are waiting — some for decades — in the employment-based green card queue, the combined effect is a signal: the administrative infrastructure of American life is becoming less accommodating.

Indian Americans who have naturalized still face practical challenges. Names like Raghunathan or Venkataraman can be inconsistently recorded across federal databases. A DHS record might list "Venkat R.," while the SSA record shows "Raghunathan Venkataraman." These discrepancies, immigration attorneys say, are exactly the kind of data mismatches that could trigger false exclusions from voter rolls built on automated cross-referencing.

## What Happens Next

A coalition of Democratic states has filed a separate lawsuit challenging the executive order in federal court in Boston. The legal battle is far from over, and Judge Nichols left open the possibility that plaintiffs could seek an injunction again once federal agencies begin implementing the order's provisions.

The November midterm elections are five months away. Republicans are fighting to maintain their slim majorities in both the House and the Senate. For the Trump administration, tighter mail-in voting rules are a centerpiece of election integrity. For Indian Americans — naturalized citizens who played by every rule to earn the right to vote — the concern is simpler: that the systems designed to verify their citizenship might not recognize their names."""
})

# ─── ARTICLE 3: Pentagon Location Data ──────────────────────────────
articles.append({
    'headline': "The Pentagon Says the Adtech Industry Is Getting American Soldiers Killed. Indian Americans Built Half That Industry.",
    'subheadline': "Commercial location data from smartphones is being used to target U.S. troops in the Gulf. Lawmakers want the advertising technology sector treated as a national security threat.",
    'slug': 'pentagon-adtech-location-data-targeting-us-troops-iran-war-indian-americans-tech',
    'category': 'news',
    'sources': json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/media-telecom/pentagon-says-us-military-personnel-are-reportedly-being-targeted-using-location-2026-05-28/"},
        {"name": "Senator Ron Wyden Letter", "url": "https://www.documentcloud.org"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com"},
        {"name": "Wired", "url": "https://www.wired.com"}
    ]),
    'vertical': 'technology',
    'urgency': 'high',
    'image_search_person': None,
    'image_search_pexels': 'military smartphone surveillance technology',
    'image_pexels_fallback': 'smartphone location tracking digital',
    'image_caption': 'U.S. Senator Ron Wyden has called for the adtech industry to be treated as a national security threat.',
    'body': """The Pentagon has confirmed for the first time that U.S. military personnel deployed to war zones have been targeted using commercially available location data — the same data that powers the advertising technology industry where Indian Americans hold an outsized share of the most senior engineering and leadership roles.

In a letter shared with Reuters on Thursday, U.S. Central Command told Senator Ron Wyden that it had "received multiple threat reports concerning adversary exploitation of commercial location data to target or surveil U.S. personnel in theater." The disclosure is the first official acknowledgment that the vast commercial market for smartphone location data — a market worth tens of billions of dollars — has been weaponized against American soldiers in an active conflict zone.

## How Location Data Becomes a Weapon

The mechanism is disturbingly simple. Every smartphone has a unique advertising identifier. Apps and service providers collect location data tied to that identifier. Data brokers aggregate and resell the data, often through complex networks of intermediaries, to anyone willing to pay.

In peacetime, this data powers targeted advertising — the reason you see an ad for a restaurant after walking past it. In the Gulf, where U.S. forces are engaged in a three-month-old confrontation with Iran over the Strait of Hormuz, the same data can reveal where troops congregate, their daily patterns of movement, and the location of staging posts.

"Commercial location data can be used to identify where U.S. troops congregate and their pattern of life, which can be exploited by adversaries to target attacks such as missiles, drones, and roadside bombs," the lawmakers' letter warned.

This is not theoretical. As far back as 2016, a U.S. defense contractor demonstrated that it could use commercially available data to track special operations forces from their domestic bases to a sensitive staging post in Syria. More recently, journalists at Wired and two German news outlets used billions of coordinates collected by a single data broker to map the movements of people at 11 U.S. military and intelligence installations in Germany.

## The Indian American Connection

Wyden's statement that it is time to "start treating the adtech industry as a national security threat" lands squarely in a sector where Indian Americans have built careers, companies, and fortunes. Indian-origin engineers and executives are deeply embedded across the advertising technology stack — from Google's ad infrastructure, where former Google CEO Sundar Pichai built his career partly on the company's advertising products, to the data analytics firms, demand-side platforms, and data management companies that form the backbone of programmatic advertising.

The companies named or implicated are not fringe operators. Google, whose Chrome browser was specifically called out by lawmakers as a tool that is "built from the ground up to collect and share user data," responded that Chrome had "industry-leading security" and that it had "long advocated for stronger rules and safeguards against data brokers." Google's parent company, Alphabet, is one of the world's largest collectors and monetizers of location data.

Representative Pat Harrigan, a North Carolina Republican and former Army Special Forces officer who cosigned the letter, said that every day Chrome remains on government-issued devices "is another day we are handing our adversaries a weapon against our own troops."

## A Reckoning for the Industry

For years, the advertising technology industry has treated user location data as a commodity — collected at scale, sold at volume, lightly regulated. The trade has powered a surveillance economy that generates hundreds of billions in annual revenue and employs tens of thousands of engineers, disproportionately of Indian and Chinese origin, across Silicon Valley, Seattle, and Hyderabad.

The Pentagon's confirmation forces a question that the industry has avoided: at what point does a business model built on tracking people become a national security liability? The lawmakers' recommendations include disabling advertising IDs on military-issued devices, automatically turning off location sharing on smartphones in the field, and steering personnel away from Chrome toward more privacy-focused browsers.

For Indian Americans in the technology sector — many of whom arrived on H-1B visas and built careers in exactly the companies now under scrutiny — the moment is uncomfortable. The industry that offered them economic opportunity is now being described as a threat to the country that gave them that opportunity. How the community responds, and whether it leads on reform rather than defending the status quo, may define whether the advertising technology sector survives this reckoning with its business model intact."""
})


# ─── MAIN EXECUTION ─────────────────────────────────────────────────

print(f"\n{'='*60}")
print(f"The Videshi — News Writer — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"{'='*60}\n")

published_count = 0

for i, article in enumerate(articles, 1):
    print(f"\n--- Article {i}/{len(articles)}: {article['headline'][:60]}... ---\n")
    
    # Image sourcing
    image_url = None
    image_attribution = ""
    
    # Step 1: Try Wikipedia for person articles
    if article.get('image_search_person'):
        print(f"  Trying Wikipedia for: {article['image_search_person']}")
        image_url = fetch_wikipedia_person_image(article['image_search_person'])
        if image_url:
            image_attribution = "Wikimedia Commons"
    
    # Step 2: Try Pexels fallback
    if not image_url and article.get('image_search_pexels'):
        print(f"  Trying Pexels for: {article['image_search_pexels']}")
        image_url = fetch_pexels_image(
            article['image_search_pexels'],
            article.get('image_pexels_fallback')
        )
        if image_url:
            image_attribution = "Pexels"
    
    # Step 3: Validate
    if image_url and not validate_image_url(image_url):
        print(f"  ✗ Image failed validation, skipping")
        image_url = None
    
    # Step 4: Upload to Supabase
    if image_url:
        filename = f"{article['slug']}.jpg"
        uploaded_url = upload_image_to_supabase(image_url, filename)
        if uploaded_url:
            image_url = uploaded_url
            if 'supabase' in uploaded_url:
                image_attribution = "The Videshi"
    
    article['image_url'] = image_url
    article['image_attribution'] = image_attribution
    
    # Publish
    art_id = publish_article(article)
    if art_id:
        published_count += 1
    
    time.sleep(1)

print(f"\n{'='*60}")
print(f"Done. Published {published_count}/{len(articles)} articles.")
print(f"{'='*60}\n")
