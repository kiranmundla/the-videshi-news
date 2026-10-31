#!/usr/bin/env python3
"""Insert a V3 article into p2_articles and update the topic."""
import json, os, sys, ssl, subprocess, urllib.request, urllib.parse
from datetime import datetime, timezone

ctx = ssl.create_default_context()
BASE = os.environ['SUPABASE_URL']
KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

def _curl(method, path, data):
    """Supabase REST via curl — urllib/requests fail through this server's proxy (403/ProxyError/RemoteDisconnected). AGENTS.md documents the curl-only rule."""
    url = f"{BASE}/rest/v1/{path}"
    result = subprocess.run([
        'curl', '-sS', '-X', method, url,
        '-H', f'apikey: {KEY}',
        '-H', f'Authorization: Bearer {KEY}',
        '-H', 'Content-Type: application/json',
        '-H', 'Prefer: return=representation',
        '--data', json.dumps(data)
    ], capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"curl {method} {path} failed: {result.stderr[:300]}")
    out = result.stdout.strip()
    return json.loads(out) if out else []

def supabase_post(path, data):
    return _curl('POST', path, data)

def supabase_patch(path, data):
    return _curl('PATCH', path, data)

# Domain -> publication name for source labels. Falls back to a title-cased
# domain root (scoopfeeds.com -> Scoopfeeds) so the Sources footer never shows
# a raw URL (2026-10-07: most articles stored bare URLs as source names).
_DOMAIN_NAMES = {
    "reuters.com": "Reuters", "bloomberg.com": "Bloomberg",
    "apnews.com": "Associated Press", "bbc.com": "BBC", "bbc.co.uk": "BBC",
    "cnn.com": "CNN", "nytimes.com": "The New York Times", "usatoday.com": "USA Today",
    "washingtonpost.com": "The Washington Post", "wsj.com": "The Wall Street Journal",
    "forbes.com": "Forbes", "theguardian.com": "The Guardian",
    "economictimes.indiatimes.com": "The Economic Times",
    "timesofindia.indiatimes.com": "The Times of India",
    "indiatimes.com": "IndiaTimes", "thehindu.com": "The Hindu",
    "thehindubusinessline.com": "The Hindu BusinessLine",
    "hindustantimes.com": "Hindustan Times", "indianexpress.com": "The Indian Express",
    "livemint.com": "Mint", "moneycontrol.com": "Moneycontrol",
    "ndtv.com": "NDTV", "news18.com": "News18", "firstpost.com": "Firstpost",
    "theprint.in": "ThePrint", "scroll.in": "Scroll", "thewire.in": "The Wire",
    "deccanchronicle.com": "Deccan Chronicle", "deccanherald.com": "Deccan Herald",
    "tribuneindia.com": "The Tribune", "dnaindia.com": "DNA India",
    "business-standard.com": "Business Standard", "financialexpress.com": "Financial Express",
    "outlookindia.com": "Outlook", "indiatoday.in": "India Today",
    "aajtak.in": "Aaj Tak", "zeenews.india.com": "Zee News",
    "abplive.com": "ABP News", "etvbharat.com": "ETV Bharat",
    "espncricinfo.com": "ESPNcricinfo", "cricbuzz.com": "Cricbuzz",
    "fide.com": "FIDE", "olympics.com": "Olympics.com",
    "techcrunch.com": "TechCrunch", "theverge.com": "The Verge",
    "wired.com": "Wired", "arstechnica.com": "Ars Technica",
    "gsmarena.com": "GSMArena", "9to5mac.com": "9to5Mac",
    "cointelegraph.com": "Cointelegraph", "coindesk.com": "CoinDesk",
    "pib.gov.in": "Press Information Bureau", "india.gov.in": "Government of India",
    "rbi.org.in": "Reserve Bank of India", "sebi.gov.in": "SEBI",
    "uscis.gov": "USCIS", "state.gov": "US State Department",
    "dhs.gov": "US Homeland Security", "whitehouse.gov": "The White House",
    "federalreserve.gov": "Federal Reserve", "sba.gov": "US Small Business Admin",
    "youtube.com": "YouTube", "x.com": "X", "twitter.com": "X",
    "instagram.com": "Instagram", "facebook.com": "Facebook",
    "wikipedia.org": "Wikipedia", "commons.wikimedia.org": "Wikimedia Commons",
}

def _name_from_url(url):
    try:
        host = urllib.parse.urlparse(url).netloc.lower()
    except Exception:
        return None
    host = host.split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    if host in _DOMAIN_NAMES:
        return _DOMAIN_NAMES[host]
    parts = host.split(".")
    # strip common TLD/ccTLD tails: economictimes.indiatimes.com -> handled
    # above; generic fallback uses the registrable-ish root
    core = parts[-2] if len(parts) >= 2 and len(parts[-1]) <= 3 else parts[0]
    core = core.replace("-", " ").replace("_", " ").strip()
    return core.title() if core else None

def normalize_sources(sources):
    """Ensure every source has a human-readable name, never a raw URL."""
    out = []
    for s in sources or []:
        if not isinstance(s, dict):
            s = {"name": str(s), "url": str(s)}
        name = (s.get("name") or "").strip()
        url = (s.get("url") or "").strip()
        if not name or name.startswith("http"):
            derived = _name_from_url(url or name)
            if derived:
                name = derived
        if not name:
            name = "Source"
        s = dict(s)
        s["name"] = name
        out.append(s)
    return out

def upload_image(local_path, slug):
    """Upload compressed image to Supabase storage."""
    storage_path = f"article-images/{slug}.jpg"
    url = f"{BASE}/storage/v1/object/article-images/{slug}.jpg"
    
    with open(local_path, 'rb') as f:
        img_data = f.read()
    
    result = subprocess.run([
        'curl', '-s', '-X', 'POST', url,
        '-H', f'apikey: {KEY}',
        '-H', f'Authorization: Bearer {KEY}',
        '-H', 'Content-Type: image/jpeg',
        '-H', 'x-upsert: true',
        '--data-binary', '@' + local_path
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        public_url = f"{BASE}/storage/v1/object/public/article-images/{slug}.jpg"
        return public_url
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: v3-insert-article.py <article.json>")
        sys.exit(1)
    
    with open(sys.argv[1]) as f:
        article = json.load(f)

    # ≥2-source publish gate (Kiran, approved 2026-10-14): no article may
    # be published with fewer than 2 legitimate sources. The staged JSON
    # stays on disk and the topic is NOT marked published — supply a
    # second legitimate source and re-run. Never pad with an irrelevant
    # or fabricated source. See pipeline/source_gate.py.
    import source_gate
    normalized_sources = normalize_sources(article.get('sources', []))
    _gate_reason = source_gate.gate_failure(normalized_sources)
    if _gate_reason is not None:
        print(f"🚫 HELD by ≥2-source gate — NOT inserted: "
              f"{article.get('headline')}", file=sys.stderr)
        print(f"   {_gate_reason}", file=sys.stderr)
        print("   Add a second legitimate source to the staged JSON and "
              "re-run. Do NOT pad with an irrelevant source.",
              file=sys.stderr)
        sys.exit(2)

    # Pre-publish content gate (ROOT-CAUSE PROGRAM part 2, 2026-10-30):
    # deterministic failure-case checks — unknown-value comparisons,
    # inferred free admission, sub-event start-time invention,
    # unestablished superlative ledes, estimates stated as fact. Same
    # hold semantics as the source gate. See pipeline/content_gate.py.
    import content_gate
    _content_failures = content_gate.check_article(article)
    if _content_failures:
        print(f"🚫 HELD by content gate — NOT inserted: "
              f"{article.get('headline')}", file=sys.stderr)
        for _f in _content_failures:
            print(f"   - {_f}", file=sys.stderr)
        print("   Fix the flagged claim(s) in the staged JSON and "
              "re-run. Do NOT rephrase to dodge the check — verify the "
              "claim against the sources.", file=sys.stderr)
        sys.exit(2)

    # Rung 0 intent (image rebuild, 2026-10-30): state what the
    # article's image must show, at insert, in the schema's intent
    # columns. Writer-supplied values win; derivation fills gaps.
    # Records only — never holds or alters the article. See
    # pipeline/image_ledger.py.
    try:
        import image_ledger
        _intent = image_ledger.intent_columns(article)
    except Exception:
        _intent = {}

    now = datetime.now(timezone.utc).isoformat()

    # Insert article
    insert_data = {
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': article['slug'],
        'category': article['category'],
        'vertical': article.get('vertical', article['category']),
        'tags': article.get('tags', []),
        'sources': normalized_sources,
        'image_url': article.get('image_url') or None,
        'image_caption': article.get('image_caption', ''),
        'image_attribution': article.get('image_attribution', ''),
        'image_entities': _intent.get('image_entities'),
        'image_must_show': _intent.get('image_must_show'),
        'image_search_query': _intent.get('image_search_query'),
        'word_count': article.get('word_count', 0),
        'diaspora_angle': article.get('diaspora_angle', ''),
        'llm_score': article.get('llm_score', 0),
        'topic_id': article.get('topic_id') or None,
        'kids_relevant': bool(article.get('kids_relevant', False)),
        'published_at': now,
        'status': 'published',
        'article_type': article.get('article_type', 'breaking'),
        'data_cards': article.get('data_cards') or None,
    }
    
    result = supabase_post('p2_articles', insert_data)
    if result:
        article_id = result[0]['id'] if isinstance(result, list) else result['id']
        print(f"✅ Article inserted: {article['headline']}")
        print(f"   ID: {article_id}")

        # Rung 0 provenance: a writer-supplied hero is a placement.
        if article.get('image_url'):
            try:
                import image_ledger
                image_ledger.record_provenance(
                    article_id=article_id, slug=article.get('slug'),
                    surface="hero", producer="v3-insert-article",
                    source_route=image_ledger.route_for_url(
                        article['image_url']),
                    image_url=article['image_url'],
                    attribution=article.get('image_attribution'))
            except Exception:
                pass

        # Update topic status
        if article.get('topic_id'):
            topic_path = f"p2_topics?id=eq.{article['topic_id']}"
            supabase_patch(topic_path, {
                'status': 'published',
                'last_article_id': article_id
            })
            print(f"   Topic updated: {article['topic_id']}")
        
        # Related coverage: link 2-3 related articles at the end of the body
        try:
            import related_coverage
            n = related_coverage.append_related_block(article_id)
            if n:
                print(f"   Related coverage: linked {n} articles")
        except Exception as e:
            print(f"   Related coverage skipped: {e}")

        return article_id
    else:
        print(f"❌ Failed to insert: {article['headline']}")
        return None

if __name__ == '__main__':
    main()
