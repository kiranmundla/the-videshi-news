#!/usr/bin/env python3
"""
Writer run for 2026-06-28 — two news articles:
1. OpenAI appoints Prabhjeet Singh as India MD
2. India's sovereign AI push after Anthropic ban
"""
import os, sys, json, re, time, subprocess, urllib.parse, hashlib
from datetime import datetime, timezone

# ── env ──
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            k = k.replace('export ', '').strip()
            v = v.strip().strip('"').strip("'")
            os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
UA = "TheVideshi/1.0 (thevideshi.com)"

# ── helpers ──

def supabase_post(table, payload):
    """Insert a row via PostgREST."""
    import urllib.request
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('apikey', SUPABASE_KEY)
    req.add_header('Authorization', f'Bearer {SUPABASE_KEY}')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Prefer', 'return=representation')
    # Use curl to avoid proxy issues
    cmd = [
        'curl', '-sS', '-X', 'POST', url,
        '-H', f'apikey: {SUPABASE_KEY}',
        '-H', f'Authorization: Bearer {SUPABASE_KEY}',
        '-H', 'Content-Type: application/json',
        '-H', 'Prefer: return=representation',
        '-d', json.dumps(payload)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        print(f"  ✗ curl error: {r.stderr}")
        return None
    try:
        resp = json.loads(r.stdout)
        if isinstance(resp, list) and len(resp) > 0:
            print(f"  ✓ Inserted into {table}: {resp[0].get('slug', resp[0].get('id', '?'))}")
            return resp[0]
        elif isinstance(resp, dict) and 'message' in resp:
            print(f"  ✗ Supabase error: {resp}")
            return None
        return resp
    except Exception as e:
        print(f"  ✗ Parse error: {e} — raw: {r.stdout[:200]}")
        return None

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    cmd = [
        'curl', '-sS', '-A', UA,
        f'https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}'
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if r.returncode == 0:
        try:
            data = json.loads(r.stdout)
            img = data.get('originalimage', {}).get('source') or data.get('thumbnail', {}).get('source')
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
        except:
            pass
    print(f"  ✗ No Wikipedia image for '{person_name}'")
    return None

def fetch_wikimedia_commons(query, limit=5):
    """Search Wikimedia Commons for CC images."""
    params = urllib.parse.urlencode({
        'action': 'query',
        'generator': 'search',
        'gsrsearch': query,
        'gsrnamespace': '6',
        'gsrlimit': str(limit),
        'prop': 'imageinfo',
        'iiprop': 'url|size|mime',
        'iiurlwidth': '1200',
        'format': 'json'
    })
    url = f'https://commons.wikimedia.org/w/api.php?{params}'
    cmd = ['curl', '-sS', '-A', UA, url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if r.returncode != 0:
        return []
    try:
        data = json.loads(r.stdout)
        pages = data.get('query', {}).get('pages', {})
        results = []
        for pid, page in pages.items():
            ii = page.get('imageinfo', [{}])[0]
            mime = ii.get('mime', '')
            if not mime.startswith('image/') or mime == 'image/svg+xml':
                continue
            w = ii.get('width', 0)
            if w < 300:
                continue
            results.append({
                'url': ii.get('thumburl') or ii.get('url', ''),
                'original_url': ii.get('url', ''),
                'title': page.get('title', ''),
                'width': w,
                'height': ii.get('height', 0),
            })
        if results:
            print(f"  ✓ Commons: {len(results)} results for '{query}'")
        return results
    except:
        return []

def fetch_pexels(query, per_page=5):
    """Search Pexels for stock images."""
    pexels_key = os.environ.get('PEXELS_API_KEY', '')
    if not pexels_key:
        print("  ⚠ No PEXELS_API_KEY")
        return []
    q = urllib.parse.quote(query)
    url = f'https://api.pexels.com/v1/search?query={q}&per_page={per_page}'
    cmd = ['curl', '-sS', '-H', f'Authorization: {pexels_key}', url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if r.returncode != 0:
        return []
    try:
        data = json.loads(r.stdout)
        return [{'url': p.get('src', {}).get('large2x') or p.get('src', {}).get('original', ''),
                 'photographer': p.get('photographer', '')} for p in data.get('photos', [])]
    except:
        return []

def verify_image(url):
    """Check that image URL returns 200 and > 5KB."""
    cmd = ['curl', '-sS', '-o', '/dev/null', '-w', '%{http_code} %{size_download}', '-A', UA, url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if r.returncode != 0:
        return False
    parts = r.stdout.strip().split()
    if len(parts) < 2:
        return False
    code, size = parts[0], float(parts[1])
    ok = code == '200' and size > 5000
    if ok:
        print(f"  ✓ Image verified: {code}, {size:.0f} bytes")
    else:
        print(f"  ✗ Image check failed: {code}, {size:.0f} bytes")
    return ok

# ── COMMONS RELEVANCE GATE ──
_COMMONS_STOP = {
    "the","a","an","of","in","on","at","to","for","and","or","with","as","by","from","is",
    "are","was","were","be","new","says","after","over","amid","how","why","what","2024",
    "2025","2026","india","indian","us","usa","american","uk","first","more","than",
    "people","man","woman","group","day","year","top","big","set","get","make","makes",
    "made","you","your","they","them","this","that","social","media","using","use",
}

def _keywords(text):
    toks = re.findall(r"[A-Za-z][A-Za-z'-]+", text or "")
    return [t.lower() for t in toks if len(t) >= 4 and t.lower() not in _COMMONS_STOP]

def commons_relevance_ok(commons_title, headline, topic=""):
    kws = _keywords(headline + " " + topic)
    if not kws:
        return True
    title_lower = commons_title.lower()
    hits = sum(1 for k in kws if k in title_lower)
    return hits >= 1

# ── ARTICLE DEFINITIONS ──

def source_image_openai():
    """Source image for OpenAI/Prabhjeet Singh article."""
    # 1. Try Wikipedia for Prabhjeet Singh
    img = fetch_wikipedia_person_image("Prabhjeet Singh")
    if img and verify_image(img):
        return img, "Prabhjeet Singh", "Wikimedia Commons"

    # 2. Try Wikimedia Commons for OpenAI
    results = fetch_wikimedia_commons("OpenAI logo artificial intelligence")
    for r in results:
        if commons_relevance_ok(r['title'], "OpenAI artificial intelligence"):
            if verify_image(r['url']):
                return r['url'], f"Wikimedia Commons image: {r['title']}", "Wikimedia Commons"

    # 3. Try Wikimedia Commons for ChatGPT
    results = fetch_wikimedia_commons("ChatGPT OpenAI")
    for r in results:
        if verify_image(r['url']):
            return r['url'], f"Wikimedia Commons image: {r['title']}", "Wikimedia Commons"

    # 4. Pexels fallback — NOT for a named person, so generic AI office is OK
    results = fetch_pexels("artificial intelligence technology")
    for r in results:
        if verify_image(r['url']):
            return r['url'], "AI technology concept", "Pexels"

    return None, None, None


def source_image_ai_sovereignty():
    """Source image for India AI sovereignty article."""
    # 1. Try Wikimedia Commons
    for query in ["India AI Mission", "artificial intelligence India", "GPU data center", "artificial intelligence computing"]:
        results = fetch_wikimedia_commons(query)
        for r in results:
            if commons_relevance_ok(r['title'], "artificial intelligence India sovereign model"):
                if verify_image(r['url']):
                    return r['url'], f"Wikimedia Commons: {r['title']}", "Wikimedia Commons"

    # 2. Pexels fallback for abstract AI imagery
    results = fetch_pexels("artificial intelligence computing server")
    for r in results:
        if verify_image(r['url']):
            return r['url'], "AI computing infrastructure", "Pexels"

    return None, None, None


def build_article_openai():
    print("\n═══ Article 1: OpenAI appoints Prabhjeet Singh as India MD ═══")

    img_url, img_caption, img_attr = source_image_openai()
    if not img_url:
        print("  ✗ No image found — aborting")
        return None

    slug = "openai-prabhjeet-singh-uber-india-managing-director-chatgpt-ai-market-20260628"
    headline = "OpenAI Just Hired the Man Who Ran Uber India to Lead Its Biggest Bet Outside America"
    subheadline = "Prabhjeet Singh will become OpenAI's most senior leader in India, a market with 100 million weekly ChatGPT users and growing faster than any other outside the US."

    body = """When Sam Altman's OpenAI needed someone to run its single largest market outside the United States, it reached into the upper ranks of another American company that once bet everything on India — and won.

Prabhjeet Singh, who spent nearly eleven years at Uber and led its India and South Asia operations as President, has been appointed OpenAI's first Managing Director for India. He will join in September and report to Kiran Mani, the recently appointed Managing Director for Asia Pacific, the company confirmed on Friday.

The appointment is OpenAI's most significant leadership move in India to date. Singh will oversee consumer growth, enterprise adoption, strategic partnerships, regulatory engagement and overall operations — effectively running the company's India business as a standalone operation.

## Why India, Why Now

India is no longer an afterthought for AI companies. OpenAI has said the country is its second-largest market by weekly active ChatGPT users — roughly 100 million — and ranks among its top five markets for API usage by developers and enterprises. The appointment of a heavyweight operator like Singh signals that OpenAI sees India not merely as a consumer market but as a strategic pillar.

The timing is also telling. It comes weeks after the Trump administration's export control directive forced Anthropic to pull its latest models from foreign users, briefly rattling India's fast-growing AI ecosystem. While OpenAI navigated the restrictions more smoothly — allowing vetted partners early access to its GPT-5.6 — the episode underscored just how much India's tech economy depends on reliable access to frontier AI.

Singh's mandate goes beyond selling subscriptions. He is expected to deepen OpenAI's partnerships with Indian enterprises, startups, educational institutions and the public sector, and to engage with policymakers on AI regulation and data governance — areas where India is still writing the rulebook.

## The Man for the Job

Singh is an alumnus of IIT Kharagpur and IIM Ahmedabad, with earlier stints at McKinsey & Company and Lehman Brothers. He joined Uber in 2015 as General Manager and Head of Strategy, rising through the ranks to become President of India and South Asia in 2020.

At Uber, he oversaw the company's mobility business across India, Sri Lanka and Bangladesh, navigating regulatory battles, fierce local competition from Ola, and the pandemic's near-destruction of ride-hailing demand. The experience — scaling a global platform in a market that rewards deep local adaptation — is precisely what OpenAI needs as it moves from consumer curiosity to enterprise infrastructure.

"We thank Prabhjeet for his leadership and lasting contributions in his decade-long journey with Uber — we remain deeply committed to our next phase of growth in India," an Uber spokesperson said.

## A Crowded Race

OpenAI's India push comes against a backdrop of intensifying competition. Amazon committed $48 billion to India through 2030, with a major chunk earmarked for AI and cloud infrastructure. Google has pledged $15 billion for data centres in southern India. Microsoft has earmarked $17.5 billion.

Meanwhile, India's own AI ecosystem is maturing. The government-backed AI Mission has committed ₹2,194 crore to twelve startups building sovereign foundational models, including Sarvam AI (India's first AI unicorn), BharatGen and Tech Mahindra's Makers Lab. The message from Delhi is clear: India wants to consume AI, but also build it.

For the diaspora, Singh's appointment carries a familiar resonance. Another IIT-IIM alumnus reaching the top of a global technology company, joining a lineage that includes Sundar Pichai at Google, Satya Nadella at Microsoft and Arvind Krishna at IBM. The difference this time is that the job is not to run the world from California — it is to bring the world's most powerful AI home.

*Sources: OpenAI (official statement), Reuters, Outlook Business, The Hindu BusinessLine, Exchange4Media*"""

    return {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "news",
        "vertical": "tech",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            "https://openai.com",
            "https://www.reuters.com/technology/openai-taps-ex-uber-regional-chief-india-leadership-2026-06-27/",
            "https://www.outlookbusiness.com/corporate/openai-names-prabhjeet-singh-as-managing-director-for-india",
            "https://www.thehindubusinessline.com/info-tech/openai-appoints-prabhjeet-singh-as-india-managing-director/article69761234.ece"
        ]),
        "diaspora_angle": "IIT Kharagpur and IIM Ahmedabad alumnus leads OpenAI in India, joining a lineage of Indian-origin leaders at global tech giants — and India is now OpenAI's second-largest market after the US."
    }


def build_article_ai_sovereignty():
    print("\n═══ Article 2: India AI sovereignty after Anthropic ban ═══")

    img_url, img_caption, img_attr = source_image_ai_sovereignty()
    if not img_url:
        print("  ✗ No image found — aborting")
        return None

    slug = "india-sovereign-ai-anthropic-ban-bharatgen-param-openai-model-access-20260628"
    headline = "The US Banned Its Most Powerful AI From Leaving the Country. India Decided It Was Time to Build Its Own."
    subheadline = "After the Anthropic export ban exposed India's dependency on American AI, Delhi sent its IT secretary to Washington, partially won back access — and quietly accelerated a sovereign model that already speaks 22 languages."

    body = """For twelve days in June, India's fastest-growing technology sector ran into a wall that no amount of engineering talent could scale: the United States government decided, almost overnight, that the world's most powerful AI models were too dangerous to share.

On June 12, the Trump administration issued an export control directive ordering Anthropic to block all foreign nationals — including the company's own non-American employees — from accessing its newly launched Claude Fable 5 and Mythos 5 models. The company complied within hours, pulling both models offline globally.

The ban was brief. By June 27, the Commerce Department partially rolled it back, allowing trusted partners to access Mythos 5. But the damage to confidence was lasting — and nowhere more so than in India, where enterprises, government agencies and startups had begun weaving American AI into the fabric of their operations.

## Delhi Goes to Washington

India did not wait for the ban to be lifted. IT Secretary S. Krishnan flew to the United States to attend the second Pax Silica Summit, where he pressed American officials for answers.

"We sought an understanding of how exactly the US is looking at this particular aspect and what their concerns are," Krishnan said on the sidelines of the summit. "If it is something which is to be used and made available, we can't have abrupt cutoffs."

The message was diplomatic but unambiguous: India needs AI to be a reliable utility, not a geopolitical lever.

Jacob Helberg, the US Under Secretary for Economic Affairs, confirmed the talks were underway. "Both sides really understand each other's perspectives," he said, adding that the US intended "a gradual measured approach" to releasing frontier models to trusted partners.

India has since been told it is on track for Fable 5 access, though neither government has disclosed a timeline.

## The Real Wake-Up Call

But the Anthropic episode did something more consequential than disrupt access to a chatbot. It forced India's technology establishment to confront a question it had been deferring: what happens when the AI you depend on is controlled by a government that can switch it off?

"Frontier AI is not just a commercial technology — it is a strategic capability, increasingly being shaped by questions of trust, regulation, national interest and sovereignty," Anand Mahindra, chairman of Mahindra & Mahindra, wrote in a shareholder letter published the same week. "India cannot be only a consumer of intelligence built elsewhere. It must also be a creator, shaper and trusted deployer of intelligence for its own society and for the world."

He is not alone. A growing chorus of industry leaders, policymakers and researchers are now arguing that India's ₹10,372-crore AI Mission — launched to build sovereign foundational models using public funds — is not a luxury but a necessity.

## Building From Scratch

India's answer is already taking shape. BharatGen, a consortium anchored at IIT Bombay and IIT Madras under the AI Mission, has released Param-2, a 17-billion-parameter foundational model trained entirely from scratch on Indian data. It supports all 22 scheduled Indian languages and has spawned domain-specific variants for Ayurveda, agriculture and Indian law.

"We need people who understand, build and improve the technology itself," said BharatGen's Ramakrishnan. The consortium has received 1,400 GPUs through the AI Mission and is now scaling toward 70 to 100 billion parameters, with a trillion-parameter model on the horizon.

Alongside Param-2, BharatGen has built Sooktam2 for text-to-speech, Shrutam2 for speech-to-text and Patram for document understanding — a full-stack sovereign AI infrastructure that, while far from matching GPT-5 or Claude Fable, is designed to work in languages and contexts that American models barely serve.

In total, the AI Mission has backed twelve startups and consortia with ₹2,194 crore in committed GPUs and cash grants. Among them is Sarvam AI, which became India's first AI unicorn, and Fractal Analytics, a listed data firm. Their models are already available on the government's AIKosh platform for other developers to build upon.

## The Diaspora Dimension

For the millions of Indian-origin professionals working in American technology companies — the engineers and product managers who build, deploy and sell these very models — the Anthropic ban was personal. It raised uncomfortable questions about whether the tools they help create will remain accessible to the country they come from.

The answer, increasingly, is that India intends to have both: access to the best foreign models through diplomacy and trade, and a homegrown alternative for when that access proves unreliable. It is a dual-track strategy born not of confidence but of compulsion — and it may turn out to be the most consequential AI decision any developing country has made.

*Sources: Mint, The Hindu BusinessLine, Inc42, Barron's, Press Information Bureau, Analytics Insight*"""

    return {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "news",
        "vertical": "tech",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            "https://www.livemint.com/technology/india-must-build-foundational-ai-models-or-risk-becoming-a-mere-consumer-bharatgen",
            "https://www.thehindubusinessline.com/info-tech/us-says-in-talks-with-india-on-anthropic-fable-model-rollout/",
            "https://inc42.com/buzz/india-in-talks-with-us-to-access-anthropics-fable-5-model/",
            "https://www.barrons.com/articles/openai-limits-models-government-security-concerns-anthropic/",
            "https://pib.gov.in/PressReleasePage.aspx?PRID=2103441"
        ]),
        "diaspora_angle": "Indian-origin tech workers who build frontier AI models at US companies now face the question of whether those tools will stay accessible to India — the Anthropic ban made that risk real."
    }


# ── MAIN ──
if __name__ == '__main__':
    load_env(os.path.expanduser('~/.env.pexels'))
    
    articles = []

    a1 = build_article_openai()
    if a1:
        articles.append(a1)

    a2 = build_article_ai_sovereignty()
    if a2:
        articles.append(a2)

    print(f"\n{'='*60}")
    print(f"Built {len(articles)} articles")

    for art in articles:
        # Word count check
        word_count = len(art['body'].split())
        print(f"\n  [{art['slug']}]")
        print(f"  Words: {word_count}")
        print(f"  Headline: {art['headline'][:80]}")
        print(f"  Image: {art['image_url'][:60] if art['image_url'] else 'NONE'}...")

        if word_count < 400:
            print(f"  ✗ REJECTED — under 400-word floor ({word_count})")
            continue

        if not art['image_url']:
            print(f"  ✗ REJECTED — no image")
            continue

        # Insert
        result = supabase_post('p2_articles', art)
        if result:
            print(f"  ✓ INSERTED with status=review")
        else:
            print(f"  ✗ INSERT FAILED")

    print(f"\n{'='*60}")
    print("Writer run complete.")
