#!/usr/bin/env python3
"""Insert a V3 article into p2_articles using curl for reliability."""
import json, os, sys, subprocess

BASE = os.environ['SUPABASE_URL']
KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

def supabase_post_curl(table, data):
    body = json.dumps(data)
    result = subprocess.run([
        'curl', '-s', '-X', 'POST',
        f'{BASE}/rest/v1/{table}',
        '-H', f'apikey: {KEY}',
        '-H', f'Authorization: Bearer {KEY}',
        '-H', 'Content-Type: application/json',
        '-H', 'Prefer: return=representation',
        '-d', body
    ], capture_output=True, text=True)
    if result.returncode == 0 and result.stdout:
        return json.loads(result.stdout)
    print(f"curl error: {result.stderr}")
    return None

def supabase_patch_curl(path, data):
    body = json.dumps(data)
    result = subprocess.run([
        'curl', '-s', '-X', 'PATCH',
        f'{BASE}/rest/v1/{path}',
        '-H', f'apikey: {KEY}',
        '-H', f'Authorization: Bearer {KEY}',
        '-H', 'Content-Type: application/json',
        '-H', 'Prefer: return=representation',
        '-d', body
    ], capture_output=True, text=True)
    if result.returncode == 0 and result.stdout:
        return json.loads(result.stdout)
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: v3-insert.py <article.json>")
        sys.exit(1)
    
    with open(sys.argv[1]) as f:
        article = json.load(f)
    
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    
    insert_data = {
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': article['slug'],
        'category': article['category'],
        'vertical': article.get('vertical', article['category']),
        'tags': article.get('tags', []),
        'sources': article.get('sources', []),
        'image_url': article.get('image_url', ''),
        'image_caption': article.get('image_caption', ''),
        'image_attribution': article.get('image_attribution', ''),
        'word_count': article.get('word_count', 0),
        'diaspora_angle': article.get('diaspora_angle', ''),
        'topic_id': article.get('topic_id', ''),
        'published_at': now,
        'status': 'published',
        'article_type': article.get('article_type', 'breaking')
    }
    
    result = supabase_post_curl('p2_articles', insert_data)
    if result:
        aid = result[0]['id'] if isinstance(result, list) else result['id']
        print(f"OK Article inserted: {article['headline'][:70]}")
        print(f"   ID: {aid}")
        
        if article.get('topic_id'):
            supabase_patch_curl(
                f"p2_topics?id=eq.{article['topic_id']}",
                {'status': 'published', 'last_article_id': aid}
            )
            print(f"   Topic updated")
        return aid
    else:
        print(f"FAIL: {article['headline'][:70]}")
        return None

if __name__ == '__main__':
    main()
