#!/usr/bin/env python3
"""Test the inline image + pull quote enrichment logic."""
import os, sys, re

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PIPELINE_DIR)

import requests
from urllib.parse import quote

_session = requests.Session()
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
_session.mount("https://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.5)))

# ── Import functions from enrich-articles.py ──
def fetch_wikipedia_image(subject):
    try:
        encoded = quote(subject.replace(" ", "_"))
        r = _session.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                return img
    except:
        pass
    return None


_SKIP_ENTITIES = {
    "india", "us", "usa", "america", "united states", "uk", "china", "world",
    "government", "court", "congress", "parliament", "supreme court",
    "the", "this", "what", "how", "why", "new", "breaking", "report",
}


def extract_entities(headline, body):
    paras = (headline + "\n\n" + "\n\n".join(body.split("\n\n")[:4])).split("\n")
    text_lines = [l.strip() for l in paras if l.strip()]
    entities = []
    seen = set()
    _STRIP_TRAILING = {
        "confirms", "unveils", "launches", "announces", "reveals", "says", "joins",
        "signs", "wins", "loses", "beats", "enters", "leaves", "faces", "leads",
        "hits", "crosses", "blocks", "delivers", "opens", "returns", "plays",
        "film", "movie", "show", "series", "game", "match", "deal", "plan",
        "new", "big", "top", "first", "next", "last", "old",
    }
    for line in text_lines:
        for m in re.finditer(r'\b([A-Z][a-z]+(?:\s+(?:(?:de|von|van|al|el|bin|the|of)\s+)?[A-Z][a-z]+){1,3})\b', line):
            name = m.group(1).strip()
            words = name.split()
            while len(words) > 1 and words[-1].lower() in _STRIP_TRAILING:
                words.pop()
            name = " ".join(words)
            if name.lower() in _SKIP_ENTITIES or len(name) < 4 or len(name.split()) < 2:
                continue
            key = name.lower()
            if key not in seen:
                seen.add(key)
                entities.append(name)
    full_text = "\n".join(text_lines)
    for m in re.finditer(r'\b(New Delhi|Washington D\.?C\.?|Silicon Valley|Wall Street|Bollywood|Hollywood|Mumbai|Chennai|Hyderabad|Bangalore|Bengaluru)\b', full_text, re.IGNORECASE):
        name = m.group(1).strip()
        key = name.lower()
        if key not in seen:
            seen.add(key)
            entities.append(name)
    return entities[:6]


def find_inline_images(headline, body, hero_url=""):
    entities = extract_entities(headline, body)
    results = []
    hero_norm = (hero_url or "").split("?")[0].lower()
    for entity in entities:
        if len(results) >= 3:
            break
        img_url = fetch_wikipedia_image(entity)
        if not img_url:
            continue
        if hero_norm and img_url.split("?")[0].lower() == hero_norm:
            continue
        if img_url.endswith(".svg") or img_url.endswith(".png"):
            continue
        caption = f"{entity} — Photo: Wikimedia Commons"
        results.append((entity, img_url, caption))
        print(f"    ✓ Inline image for '{entity}'")
    return results


def extract_pull_quote(body):
    sentences = re.split(r'(?<=[.!?])\s+', body)
    if len(sentences) < 5:
        return None
    scored = []
    for i, sent in enumerate(sentences):
        if len(sent) < 40 or len(sent) > 200:
            continue
        if i == 0:
            continue
        if sent.startswith(">") or sent.startswith("!["):
            continue
        score = 0
        if '"' in sent or '\u201c' in sent:
            score += 5
        if re.search(r'\d+[%$]|\$\d|billion|million|crore|lakh', sent, re.IGNORECASE):
            score += 3
        strong_words = ["historic", "unprecedented", "first-ever", "record", "landmark",
                       "stunning", "massive", "crucial", "breakthrough", "revolutionary",
                       "shocking", "dramatic", "critical"]
        if any(w in sent.lower() for w in strong_words):
            score += 2
        relative_pos = i / max(len(sentences), 1)
        if 0.2 < relative_pos < 0.6:
            score += 1
        if score > 0:
            scored.append((score, i, sent))
    if not scored:
        return None
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][2]


# ── Test ──
headline = "Shah Rukh Khan Confirms New Rajkumar Hirani Film at Mumbai Press Conference"
body = """Shah Rukh Khan has confirmed his next big-screen outing will be directed by Rajkumar Hirani, the filmmaker behind blockbusters like 3 Idiots and PK.

The announcement came at a packed press conference in Mumbai's Bandra suburb on Friday, where Khan was joined by producer Vidhu Vinod Chopra.

The film, tentatively titled Homecoming, will explore themes of identity and belonging — a narrative deeply relevant to the Indian diaspora worldwide.

Shah Rukh Khan said at the event: "This is a story that every Indian who has ever lived abroad will connect with. It's about what home really means."

Production is expected to begin in September 2026, with shooting planned across Mumbai, London, and New York City.

The Bollywood superstar, who last appeared in Dunki, has been selective about his projects. Industry insiders suggest this collaboration could be unprecedented in terms of scale and storytelling ambition.

Rajkumar Hirani is known for his mastery of socially relevant commercial cinema, having delivered some of Bollywood's highest-grossing films.

The project represents a massive $50 million investment and marks Hirani's first collaboration with Khan after years of speculation."""

print("=== Entity Extraction ===")
entities = extract_entities(headline, body)
print(f"Entities: {entities}")

print("\n=== Inline Image Lookup ===")
images = find_inline_images(headline, body)
print(f"\nFound {len(images)} images:")
for entity, url, caption in images:
    print(f"  {entity}: {url[:100]}")

print("\n=== Pull Quote ===")
quote = extract_pull_quote(body)
if quote:
    print(f'"{quote[:120]}"')
else:
    print("No pull quote found")

# Test 2 — News article
print("\n\n=== Test 2: News Article ===")
h2 = "Sundar Pichai Unveils Google AI Push at Annual Developer Conference"
b2 = """Google CEO Sundar Pichai unveiled a sweeping set of artificial intelligence upgrades at the company's annual I/O developer conference in Mountain View on Wednesday.

The tech giant announced Gemini Ultra, its most advanced AI model to date, along with new integrations across Gmail, Google Maps, and the Chrome browser.

Alphabet's stock price surged 7% in after-hours trading, pushing the company's market capitalization past $2.5 trillion for the first time.

"We are at a historic inflection point for computing," Pichai told the crowd of 7,000 developers. "AI will be more transformative than fire, electricity, or the internet."

The announcements position Google in direct competition with Microsoft and OpenAI, which launched GPT-5 earlier this month.

India-born Pichai, who grew up in Chennai before attending Stanford University, has led Google through its most ambitious AI transformation since its founding."""

entities2 = extract_entities(h2, b2)
print(f"Entities: {entities2}")
images2 = find_inline_images(h2, b2)
print(f"Found {len(images2)} images:")
for entity, url, caption in images2:
    print(f"  {entity}: {url[:100]}")
quote2 = extract_pull_quote(b2)
if quote2:
    print(f'Pull quote: "{quote2[:120]}"')
