#!/usr/bin/env python3
"""News writer for The Videshi — June 3, 2026 evening run."""

import json, os, sys, uuid, re, time, urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

import subprocess

def sb_headers():
    return {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }

def curl_json(method, url, data=None, extra_headers=None):
    """Use curl for Supabase requests."""
    cmd = ['curl', '-sS', '-X', method, url]
    headers = sb_headers()
    if extra_headers:
        headers.update(extra_headers)
    for k, v in headers.items():
        cmd.extend(['-H', f'{k}: {v}'])
    if data:
        cmd.extend(['-d', json.dumps(data)])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"  ✗ curl error: {result.stderr}")
        return None
    try:
        return json.loads(result.stdout) if result.stdout.strip() else None
    except:
        print(f"  ✗ parse error: {result.stdout[:200]}")
        return None

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    cmd = ['curl', '-sS', '-H', 'User-Agent: TheVideshi/1.0 (thevideshi.com)',
           f'https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if result.returncode == 0 and result.stdout.strip():
        try:
            data = json.loads(result.stdout)
            # Prefer originalimage (higher res), fall back to thumbnail
            img = data.get('originalimage', {}).get('source') or data.get('thumbnail', {}).get('source')
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
        except:
            pass
    print(f"  ⚠ No Wikipedia image for '{person_name}'")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = urllib.parse.urlencode({
        'action': 'query',
        'generator': 'search',
        'gsrsearch': search_query,
        'gsrnamespace': '6',
        'gsrlimit': str(limit),
        'prop': 'imageinfo',
        'iiprop': 'url|size|mime',
        'iiurlwidth': '1200',
        'format': 'json'
    })
    url = f'https://commons.wikimedia.org/w/api.php?{params}'
    cmd = ['curl', '-sS', '-H', 'User-Agent: TheVideshi/1.0 (thevideshi.com)', url]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if result.returncode == 0 and result.stdout.strip():
        try:
            data = json.loads(result.stdout)
            pages = data.get('query', {}).get('pages', {})
            results = []
            for pid, page in pages.items():
                ii = page.get('imageinfo', [{}])[0]
                mime = ii.get('mime', '')
                if not mime.startswith('image/') or mime == 'image/svg+xml':
                    continue
                if ii.get('width', 0) < 300:
                    continue
                results.append({
                    'url': ii.get('thumburl') or ii.get('url', ''),
                    'original_url': ii.get('url', ''),
                    'title': page.get('title', ''),
                    'width': ii.get('width', 0),
                    'height': ii.get('height', 0),
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
                return results
        except:
            pass
    print(f"  ⚠ No Wikimedia Commons results for '{search_query}'")
    return []

def fetch_pexels_image(query):
    """Search Pexels for an image. Returns URL or None."""
    if not PEXELS_KEY:
        return None
    cmd = ['curl', '-sS',
           '-H', f'Authorization: {PEXELS_KEY}',
           f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if result.returncode == 0 and result.stdout.strip():
        try:
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0]['src']['large2x']
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
        except:
            pass
    print(f"  ⚠ No Pexels image for '{query}'")
    return None

def download_and_upload_image(img_url, slug):
    """Download image, compress, upload to Supabase storage."""
    # Download
    cmd = ['curl', '-sS', '-L', '-o', f'/tmp/{slug}.jpg',
           '-H', 'User-Agent: TheVideshi/1.0 (thevideshi.com)',
           img_url]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"  ✗ Download failed for {img_url[:80]}")
        return None
    
    # Check file size
    fpath = f'/tmp/{slug}.jpg'
    if not os.path.exists(fpath) or os.path.getsize(fpath) < 5000:
        print(f"  ✗ Downloaded file too small or missing")
        return None
    
    file_size = os.path.getsize(fpath)
    print(f"  ✓ Downloaded {file_size} bytes")
    
    # Compress with PIL
    try:
        from PIL import Image
        import io
        img = Image.open(fpath)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > 1200:
            ratio = 1200 / img.width
            img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80, optimize=True)
        compressed = buf.getvalue()
        with open(fpath, 'wb') as f:
            f.write(compressed)
        print(f"  ✓ Compressed to {len(compressed)} bytes ({img.width}x{img.height})")
    except ImportError:
        print("  ⚠ PIL not available, uploading as-is")
    except Exception as e:
        print(f"  ⚠ Compression failed: {e}, uploading as-is")
    
    # Upload to Supabase storage
    upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{slug}.jpg"
    cmd = ['curl', '-sS', '-X', 'POST', upload_url,
           '-H', f'Authorization: Bearer {SUPABASE_KEY}',
           '-H', 'Content-Type: image/jpeg',
           '-H', 'x-upsert: true',
           '--data-binary', f'@{fpath}']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{slug}.jpg"
    
    # Verify upload
    verify_cmd = ['curl', '-sS', '-o', '/dev/null', '-w', '%{http_code}', public_url]
    verify = subprocess.run(verify_cmd, capture_output=True, text=True, timeout=10)
    if verify.stdout.strip() == '200':
        print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
        return public_url
    else:
        print(f"  ✗ Upload verification failed (HTTP {verify.stdout.strip()})")
        return None

def validate_image_url(url):
    """Verify an image URL returns HTTP 200 with image content."""
    cmd = ['curl', '-sS', '-o', '/dev/null', '-w', '%{http_code}|%{content_type}|%{size_download}',
           '-H', 'User-Agent: TheVideshi/1.0 (thevideshi.com)', '-L', url]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if result.returncode == 0:
        parts = result.stdout.strip().split('|')
        if len(parts) >= 3:
            code, ctype, size = parts[0], parts[1], float(parts[2])
            if code == '200' and 'image' in ctype and size > 5000:
                return True
    return False

# ============ ARTICLES ============

articles = [
    {
        "headline": "A Fire in a Delhi Hotel Killed 21 People, Most of Them Foreign Nationals Who Came for Medical Treatment.",
        "subheadline": "The Flourish Stay B&B in Malviya Nagar operated 25 rooms on a licence that allowed six. The owner is on the run, and the building had no fire safety clearance.",
        "slug": "delhi-malviya-nagar-hotel-fire-21-dead-foreign-nationals-medical-tourism-20260603",
        "category": "news",
        "vertical": "news",
        "sources": ["Reuters", "Livemint", "PTI", "NDTV", "AP News"],
        "person_search": "Malviya Nagar Delhi",
        "commons_search": ["Delhi fire", "Delhi hotel fire", "Malviya Nagar New Delhi"],
        "pexels_search": "fire building India emergency",
        "body": """A fire that started before 9 AM on Wednesday in a ground-floor restaurant in south Delhi's Malviya Nagar tore through a six-storey building above it, killing at least 21 people and injuring more than 40 others. Seventeen of the dead were foreign nationals — nine from African countries including Liberia, Nigeria and Mozambique, two from Turkmenistan, and others from Bangladesh and Central Asian nations. Most had come to Delhi for medical treatment at nearby Max Hospital and were staying at the budget accommodation upstairs.

The blaze at the Flourish Stay B&B in Hauz Rani, a congested urban village wedged between upscale malls and major hospitals, was reported to Delhi Fire Services at approximately 8:48 AM. Flames from the Lemon Green restaurant on the ground floor raced through the narrow stairwell and up five floors, smoke-locking dozens of guests in their rooms. Survivors described waking to thick black smoke with no visible exit.

## A Building That Should Not Have Been a Hotel

Investigations have already revealed that the B&B operated 25 rooms despite holding a licence for only six. The building lacked a fire No Objection Certificate (NOC), a mandatory requirement for any commercial accommodation in Delhi. Local BJP MLA Satish Upadhyay confirmed that the establishment appeared to have operated without basic fire safety provisions, including emergency exits and fire extinguishers on upper floors.

Delhi Fire Services deployed 10 to 12 fire tenders as the situation worsened. Rescue teams evacuated between 40 and 47 people, three of whom were pulled from the basement. Many of the survivors were found clinging to windows or jumping from upper floors onto mattresses that local residents had laid on the street below.

## Owner on the Run, Lookout Circular Issued

Delhi Police identified the building's co-owner as Lovkesh Bajaj and registered a First Information Report under culpable homicide and other relevant sections of the Bhartiya Nyaya Sanhita. When officers arrived at Bajaj's residence, he was not there. Police have since issued a lookout circular to prevent him from leaving the country, and multiple teams are conducting raids across the capital.

Authorities are also examining links between Bajaj and other commercial properties he reportedly owns, to determine whether a pattern of safety violations exists.

## A Medical Tourism Trap

The tragedy has thrown a harsh light on a parallel accommodation economy that has grown up around Delhi's premier hospitals. Budget hotels, B&Bs and paying-guest arrangements in areas like Malviya Nagar, Saket and Hauz Khas routinely house patients' families — often for weeks at a time — while relatives undergo treatment. Many of these properties operate in regulatory grey zones, with licences that do not match their actual scale.

Max Healthcare Group Medical Director Dr Sandeep Budhiraja said eight patients remain on ventilator support, most suffering from severe smoke inhalation. One patient with burns covering more than 25 per cent of the body was transferred to Safdarjung Hospital's burn ward. Several others sustained fractures from jumping.

## Government Response

Prime Minister Narendra Modi called the incident "tragic" and announced an ex gratia payment of ₹2 lakh from the PM National Relief Fund for the next of kin of each person who died, and ₹50,000 for the injured. Delhi Chief Minister Rekha Gupta said fire services, police and disaster response teams had been mobilised immediately, but stopped short of announcing a broader audit of similar establishments.

The Ministry of External Affairs confirmed it is coordinating with embassies of the affected countries. Most of the foreign victims' families were already in Delhi — the very reason they were staying in the building.

For a city that markets itself as a global medical tourism destination, the Malviya Nagar fire raises an uncomfortable question: who is responsible for ensuring that the thousands of foreign patients and their families who come to Delhi each year for affordable healthcare are not housed in deathtraps?"""
    },
    {
        "headline": "Russia's Biggest Bank Just Asked India to Send More Workers. Moscow's Construction Sites Cannot Function Without Them.",
        "subheadline": "Sberbank called for simplified immigration at the St. Petersburg Economic Forum. Indian work permits in Russia jumped from 5,000 to 72,000 in four years, and the country still needs 789,000 more construction workers by 2030.",
        "slug": "russia-sberbank-indian-workers-construction-labor-shortage-st-petersburg-forum-20260603",
        "category": "news",
        "vertical": "news",
        "sources": ["Reuters", "DevDiscourse", "European Interest"],
        "person_search": None,
        "commons_search": ["St. Petersburg International Economic Forum", "Sberbank Russia", "Indian workers Russia construction"],
        "pexels_search": "construction workers building site",
        "body": """Russia's largest bank, Sberbank, on Wednesday called for India to send significantly more workers to help fill a construction labour shortage that has become one of the most pressing constraints on the Russian economy. The appeal came at the St. Petersburg International Economic Forum, where the bank's deputy CEO, Anatoly Popov, told reporters that Indian migrants are critical to keeping Russian building projects on track.

"We work together with partners to develop solutions to simplify the process of entry for prospective foreign workers with the required competencies," Popov said. "Labour migrants from India are well known across many countries and on numerous construction projects."

The numbers tell the story of a labour market in freefall. In 2021, the year before Russia sent its troops into Ukraine, Moscow approved roughly 5,000 work permits for Indian nationals. By last year, that number had surged to nearly 72,000 — accounting for almost a third of Russia's total annual quota for migrant workers on visas. Even so, Sberbank says it is not enough.

## A War-Shaped Labour Crisis

Russia's construction sector alone will need an additional 789,000 workers by 2030, according to the country's Labour Ministry. The broader economy faces an immediate shortage of at least 2.3 million workers across manufacturing, services and construction — a deficit that has deepened as the war in Ukraine has pulled hundreds of thousands of working-age men into military service or driven them out of the country entirely.

An estimated 300,000 Russians were mobilised for military service, another 500,000 signed defence contracts, and between 600,000 and one million left Russia altogether since the full-scale invasion began in February 2022. The combined effect has hollowed out entire industries. Construction, retail and the service sector have been hit hardest.

Central Asian workers, historically the backbone of Russia's migrant labour force, can no longer fill the gap. Countries like Uzbekistan, Tajikistan and Kyrgyzstan — which have sent millions of workers to Russia over the past two decades — are themselves experiencing tighter labour markets and have begun redirecting workers toward Gulf states and South Korea, where wages are often higher and working conditions are better documented.

## The Modi-Putin Pact

The Sberbank appeal follows a bilateral agreement signed by President Vladimir Putin and Prime Minister Narendra Modi in December 2025 to streamline the immigration process for Indian workers heading to Russia. At the time, Russia's First Deputy Prime Minister Denis Manturov said the country could accept an "unlimited number" of Indian workers.

For India, the arrangement carries both opportunity and risk. Russian construction wages average roughly 60 per cent more than equivalent jobs in India, making the proposition financially attractive for workers from states like Uttar Pradesh, Bihar, Rajasthan and Punjab, which have historically supplied the bulk of India's outbound labour force.

But the conditions are fraught. Reports from Indian workers already in Russia describe language barriers, extreme cold, delayed payments and limited consular support. The Indian Embassy in Moscow has handled a growing number of complaints from workers who arrived on contracts that did not match the conditions they encountered. Unlike the Gulf states, where India has decades of institutional experience managing large migrant worker populations, Russia is largely unfamiliar territory.

## What It Means for the Diaspora

Sberbank's statement signals that the demand for Indian labour in Russia is not temporary. The bank also announced plans to increase its commercial presence in India, including additional offices — a clear indication that it views the labour pipeline as a long-term strategic relationship rather than a stopgap.

For the Indian government, the challenge is twofold: facilitating the economic opportunity while ensuring that the workers who go are protected. The December agreement included provisions for streamlined visa processing and worker welfare, but implementation details remain thin.

The irony is hard to miss. As the United States tightens H-1B visa rules and the Gulf states automate parts of their construction sectors, Russia — whose economy is under sweeping Western sanctions — is emerging as one of the largest new destinations for Indian blue-collar labour. Whether that turns into a success story or a cautionary tale will depend on the safeguards Delhi insists on before the pipeline widens further."""
    },
    {
        "headline": "58 Rebel MLAs Just Broke Away From Mamata Banerjee's Party. The TMC Has Never Faced a Crisis Like This.",
        "subheadline": "Expelled leaders Ritabrata Banerjee and Sandipan Saha claim the Speaker has recognised their faction as the official opposition. The party dissolved all its committees in response. Mamata blames the BJP and police for engineering the split.",
        "slug": "tmc-trinamool-congress-58-rebel-mlas-split-mamata-abhishek-banerjee-bengal-20260603",
        "category": "news",
        "vertical": "news",
        "sources": ["The Hindu BusinessLine", "DevDiscourse", "India Today", "ANI", "Livemint"],
        "person_search": "Mamata Banerjee",
        "commons_search": ["Mamata Banerjee", "Trinamool Congress rally", "West Bengal Assembly"],
        "pexels_search": None,
        "body": """The Trinamool Congress, which dominated West Bengal politics for 15 years under Mamata Banerjee, is facing an existential split. On Wednesday, a rebel faction claiming the support of 58 out of 80 TMC MLAs formally broke with the party's official leadership, declared itself the legitimate Trinamool legislature party, and staked claim to the Leader of Opposition post in the state assembly — a role the party's high command had assigned to a loyalist.

The rebellion is led by Ritabrata Banerjee and Sandipan Saha, both of whom were expelled from the TMC in recent weeks. Speaking at a press conference on Wednesday, Ritabrata Banerjee said the Speaker of the West Bengal Assembly had officially recognised their faction and accepted their claim to LoP status, a development that, if confirmed, would represent the most significant split in the party since its founding in 1998.

## The Target: Abhishek Banerjee

The rebels have not turned their fire on Mamata Banerjee herself. Instead, the anger is directed squarely at her nephew, Abhishek Banerjee, the party's national general secretary, who has been the de facto organisational head of the TMC for the past several years.

Ritabrata Banerjee told reporters that the rebel MLAs want Mamata Banerjee to serve as their "chief advisor" — a carefully calibrated gesture that separates loyalty to the party founder from rejection of her chosen successor. "We recognise Mamata Banerjee as our leader," he said. "But the question is whether the party will be run by the people or by one family."

The criticism of Abhishek Banerjee has been building for months. He currently faces summons from the Enforcement Directorate in connection with a teachers' recruitment scam that has dogged the TMC since 2022. Several rebel leaders have publicly questioned why the party's organisational machinery — and its political future — should be controlled by someone facing serious legal scrutiny.

## A Party That Lost and Then Fractured

The immediate trigger for the crisis was the TMC's crushing defeat in the recent West Bengal assembly elections, where the BJP swept to power. In the aftermath, Mamata Banerjee called a meeting of TMC MLAs on May 31. Only 20 of the 80 elected legislators showed up. Sixty stayed away — a signal that the party's internal cohesion had already collapsed.

The party's official spokesperson attributed the poor attendance to logistical issues following an attack on Abhishek Banerjee on May 30, when slippers and eggs were thrown at him at a public event. The next day, TMC leader Kalyan Banerjee was attacked in Hooghly district. The party has alleged that at least 15 to 20 TMC workers have been murdered since the election results, and that police and administration are working at the behest of the BJP.

But the rebel faction paints a different picture. They argue that the TMC's electoral collapse was a direct consequence of Abhishek Banerjee's centralised control, which alienated grassroots workers and local leaders. The rebellion, they say, is not about defecting to the BJP but about reclaiming the party from what they describe as dynastic capture.

## Anti-Defection and the Two-Thirds Threshold

The numbers matter. Under India's anti-defection law, a split is not legally recognised unless at least two-thirds of a legislature party's members break away. With 58 out of 80 MLAs — more than 72 per cent — the rebel faction appears to have crossed that threshold, which would protect its members from disqualification.

The TMC responded on Wednesday by dissolving all its committees and frontal organisations in Bengal, describing the move as "introspection" ahead of a comprehensive restructuring. The party's official line is that some of the signatures on the rebel petition were forged — a claim that Leader of the Opposition in the Assembly Suvendu Adhikari has asked the CID to investigate.

## What Comes Next

BJP leaders, including cabinet minister Dilip Ghosh, have seized on the crisis, framing it as the collapse of "family rule" in Indian politics. Ghosh predicted that the TMC would soon be reduced to its top echelon — "Mamata Banerjee and her nephew, and nobody else."

For Mamata Banerjee, the stakes could not be higher. The TMC was never just a political party — it was a personality-driven movement built on her image as a street fighter who took on the Communist establishment. If the rebel faction formalises its separation and aligns with the BJP or operates independently, Mamata's ability to mount a political comeback in Bengal will be severely diminished.

The TMC's crisis also carries a wider message for Indian politics: that electoral defeat, when combined with internal resentment over dynastic succession, can unravel even the most dominant regional parties faster than anyone expected."""
    }
]

# ============ MAIN ============
def main():
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    for i, article in enumerate(articles):
        print(f"\n{'='*60}")
        print(f"ARTICLE {i+1}: {article['headline'][:70]}...")
        print(f"{'='*60}")
        
        # 1. Source images
        print("\n--- Image sourcing ---")
        img_url = None
        attribution = None
        
        # Try Wikipedia for person articles
        if article.get('person_search'):
            wiki_img = fetch_wikipedia_person_image(article['person_search'])
            if wiki_img and validate_image_url(wiki_img):
                uploaded = download_and_upload_image(wiki_img, article['slug'])
                if uploaded:
                    img_url = uploaded
                    attribution = "Wikimedia Commons"
        
        # Try Wikimedia Commons
        if not img_url and article.get('commons_search'):
            for query in article['commons_search']:
                commons = fetch_wikimedia_commons_images(query)
                if commons:
                    for c in commons:
                        if validate_image_url(c['url']):
                            uploaded = download_and_upload_image(c['url'], article['slug'])
                            if uploaded:
                                img_url = uploaded
                                attribution = "Wikimedia Commons"
                                break
                if img_url:
                    break
        
        # Try Pexels
        if not img_url and article.get('pexels_search'):
            pexels_img = fetch_pexels_image(article['pexels_search'])
            if pexels_img and validate_image_url(pexels_img):
                uploaded = download_and_upload_image(pexels_img, article['slug'])
                if uploaded:
                    img_url = uploaded
                    attribution = "Pexels"
        
        if img_url:
            print(f"  ✓ Final image: {img_url[:80]}...")
        else:
            print(f"  ⚠ No image found — publishing without image")
        
        # 2. Build article payload
        art_id = str(uuid.uuid4())
        
        # Word count check
        word_count = len(article['body'].split())
        print(f"\n--- Article quality ---")
        print(f"  Words: {word_count}")
        print(f"  Headline: {len(article['headline'])} chars")
        print(f"  Subheadline: {len(article['subheadline'])} chars")
        
        if word_count < 400:
            print(f"  ✗ REJECTED: Body too short ({word_count} words)")
            continue
        
        payload = {
            "id": art_id,
            "headline": article['headline'],
            "subheadline": article['subheadline'],
            "slug": article['slug'],
            "body": article['body'],
            "category": article['category'],
            "vertical": article['vertical'],
            "status": "published",
            "published_at": now,
            "sources": json.dumps(article['sources']),
            "is_editorial": False,
        }
        
        if img_url:
            payload["image_url"] = img_url
            payload["image_attribution"] = attribution
        
        # 3. Insert into Supabase
        print(f"\n--- Publishing ---")
        insert_url = f"{SUPABASE_URL}/rest/v1/p2_articles"
        result = curl_json('POST', insert_url, payload)
        
        if result and isinstance(result, list) and len(result) > 0:
            print(f"  ✓ Published: {result[0].get('slug', 'unknown')}")
        elif result and isinstance(result, dict) and result.get('code'):
            print(f"  ✗ Error: {result.get('message', result.get('code', 'unknown'))}")
        else:
            print(f"  ✓ Insert completed (response: {str(result)[:100]})")
        
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"Writer run complete. {len(articles)} articles processed.")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
