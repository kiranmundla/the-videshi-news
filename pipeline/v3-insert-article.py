#!/usr/bin/env python3
"""Insert a V3 article into p2_articles and update the topic."""
import json, os, sys, ssl, subprocess, urllib.request, urllib.parse
from datetime import datetime, timezone

ctx = ssl.create_default_context()
BASE = os.environ['SUPABASE_URL']
KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

def supabase_post(path, data):
    url = f"{BASE}/rest/v1/{path}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method='POST', headers={
        'apikey': KEY, 'Authorization': f'Bearer {KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    })
    resp = urllib.request.urlopen(req, context=ctx)
    return json.loads(resp.read())

def supabase_patch(path, data):
    url = f"{BASE}/rest/v1/{path}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method='PATCH', headers={
        'apikey': KEY, 'Authorization': f'Bearer {KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    })
    resp = urllib.request.urlopen(req, context=ctx)
    return json.loads(resp.read())

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
    
    result = supabase_post('p2_articles', insert_data)
    if result:
        article_id = result[0]['id'] if isinstance(result, list) else result['id']
        print(f"✅ Article inserted: {article['headline']}")
        print(f"   ID: {article_id}")
        
        # Update topic status
        if article.get('topic_id'):
            topic_path = f"p2_topics?id=eq.{article['topic_id']}"
            supabase_patch(topic_path, {
                'status': 'published',
                'last_article_id': article_id
            })
            print(f"   Topic updated: {article['topic_id']}")
        
        return article_id
    else:
        print(f"❌ Failed to insert: {article['headline']}")
        return None

if __name__ == '__main__':
    main()
