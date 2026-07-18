#!/usr/bin/env python3
"""Insert a single article into p2_articles via Supabase REST API."""
import json, os, subprocess, sys

def supabase_post(endpoint, payload):
    url = f"{os.environ['SUPABASE_URL']}/rest/v1/{endpoint}"
    data = json.dumps(payload)
    r = subprocess.run([
        'curl', '-s', '-X', 'POST', url,
        '-H', f'apikey: {os.environ["SUPABASE_SERVICE_ROLE_KEY"]}',
        '-H', f'Authorization: Bearer {os.environ["SUPABASE_SERVICE_ROLE_KEY"]}',
        '-H', 'Content-Type: application/json',
        '-H', 'Prefer: return=representation',
        '-d', data
    ], capture_output=True, text=True)
    return json.loads(r.stdout)

def supabase_patch(endpoint, payload):
    url = f"{os.environ['SUPABASE_URL']}/rest/v1/{endpoint}"
    data = json.dumps(payload)
    r = subprocess.run([
        'curl', '-s', '-X', 'PATCH', url,
        '-H', f'apikey: {os.environ["SUPABASE_SERVICE_ROLE_KEY"]}',
        '-H', f'Authorization: Bearer {os.environ["SUPABASE_SERVICE_ROLE_KEY"]}',
        '-H', 'Content-Type: application/json',
        '-H', 'Prefer: return=minimal',
        '-d', data
    ], capture_output=True, text=True)
    return r.stdout

def main():
    article_file = sys.argv[1]
    with open(article_file) as f:
        article = json.load(f)
    
    topic_id = article.pop('topic_id', None)
    
    result = supabase_post('p2_articles', article)
    if isinstance(result, list) and len(result) > 0:
        art_id = result[0]['id']
        print(f"SUCCESS: id={art_id}")
        print(f"Headline: {result[0]['headline']}")
        
        # Update topic status
        if topic_id:
            supabase_patch(
                f'p2_topics?id=eq.{topic_id}',
                {"status": "published", "last_article_id": art_id}
            )
            print(f"Topic {topic_id} marked published")
    else:
        print(f"ERROR: {json.dumps(result)[:500]}")
        sys.exit(1)

if __name__ == '__main__':
    main()
