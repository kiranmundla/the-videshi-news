#!/usr/bin/env python3
"""Insert article into p2_articles from a JSON file. Usage: python3 insert-article.py <path-to-json>"""
import json, sys, subprocess, os, re
from datetime import datetime, timezone

def main():
    path = sys.argv[1]
    with open(path) as f:
        article = json.load(f)
    
    # Ensure required fields
    required = ['headline', 'subheadline', 'body', 'slug', 'category', 'tags', 'sources', 'word_count', 'topic_id', 'llm_score']
    for r in required:
        if r not in article:
            print(f"ERROR: Missing required field: {r}", file=sys.stderr)
            sys.exit(1)

    # ≥2-source publish gate (Kiran, approved 2026-10-14). See
    # pipeline/source_gate.py.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import source_gate
    _gate_reason = source_gate.gate_failure(article.get('sources'))
    if _gate_reason is not None:
        print(f"🚫 HELD by ≥2-source gate — NOT inserted: {article.get('headline')}", file=sys.stderr)
        print(f"   {_gate_reason}", file=sys.stderr)
        sys.exit(2)

    # Pre-publish content gate (ROOT-CAUSE PROGRAM part 2, 2026-10-30)
    # — same rule as v3-insert-article.py. See pipeline/content_gate.py.
    import content_gate
    _content_failures = content_gate.check_article(article)
    if _content_failures:
        print(f"🚫 HELD by content gate — NOT inserted: {article.get('headline')}", file=sys.stderr)
        for _f in _content_failures:
            print(f"   - {_f}", file=sys.stderr)
        sys.exit(2)

    # Set defaults
    article.setdefault('vertical', article['category'])
    article.setdefault('image_url', None)
    article.setdefault('image_caption', None)
    article.setdefault('image_attribution', None)
    article.setdefault('diaspora_angle', '')
    article.setdefault('status', 'published')
    article.setdefault('article_type', 'breaking')
    article['published_at'] = datetime.now(timezone.utc).isoformat()
    
    url = os.environ['SUPABASE_URL']
    key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
    
    payload = json.dumps(article)
    
    result = subprocess.run([
        'curl', '-sS', f'{url}/rest/v1/p2_articles',
        '-H', f'apikey: {key}',
        '-H', f'Authorization: Bearer {key}',
        '-H', 'Content-Type: application/json',
        '-H', 'Prefer: return=representation',
        '-d', payload
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: curl failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    try:
        resp = json.loads(result.stdout)
        if isinstance(resp, list) and len(resp) > 0:
            art = resp[0]
            print(f"SUCCESS: id={art['id']} slug={art['slug']} headline={art['headline']}")
            # Write ID to a sidecar file
            with open(path + '.id', 'w') as f:
                f.write(art['id'])
            return art['id']
        else:
            print(f"ERROR: Unexpected response: {result.stdout[:500]}", file=sys.stderr)
            sys.exit(1)
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON response: {result.stdout[:500]}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
