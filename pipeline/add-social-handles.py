#!/usr/bin/env python3
"""Add social follow links to entertainment articles that don't have them."""

import json, os, re, requests, sys

SB = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

# Load registry
with open(os.path.join(os.path.dirname(__file__), "social-embed-registry.json")) as f:
    reg = json.load(f)

# Build name→handles lookup across ALL categories
handles = {}
for cat_key, cat_val in reg.items():
    if not isinstance(cat_val, dict):
        continue
    for person in cat_val.get("persons", []):
        name = person["name"]
        handles[name.lower()] = {
            "name": name,
            "instagram": person.get("instagram"),
            "x": person.get("x"),
        }

def find_celebrities(headline, body):
    """Find registry celebrities mentioned in article. Full name match only."""
    text = (headline + " " + body).lower()
    found = []
    # Prioritize headline mentions
    headline_lower = headline.lower()
    for key, info in handles.items():
        if key in text:
            # Score: headline mention > body mention
            in_headline = key in headline_lower
            found.append((info, in_headline))
    # Sort: headline mentions first
    found.sort(key=lambda x: (not x[1], x[0]["name"]))
    return [f[0] for f in found]

def build_follow_line(celebs):
    """Build markdown follow line. Max 2 celebrities, prefer IG."""
    links = []
    for c in celebs[:2]:  # Max 2 celebrities
        if c["instagram"]:
            links.append(f'[@{c["instagram"]}](https://instagram.com/{c["instagram"]})')
        if c["x"]:
            links.append(f'[@{c["x"]}](https://x.com/{c["x"]})')
    if not links:
        return None
    return "**Follow:** " + " · ".join(links)

def process_articles(dry_run=True, limit=50, article_id=None):
    """Find entertainment articles without follow links and add them."""
    if article_id:
        url = f'{SB}/rest/v1/p2_articles?id=eq.{article_id}&select=id,headline,body'
    else:
        url = (f'{SB}/rest/v1/p2_articles?select=id,headline,body'
               f'&category=eq.entertainment&status=eq.published'
               f'&order=published_at.desc&limit={limit}')
    
    r = requests.get(url, headers=H, timeout=15)
    articles = r.json()
    
    updated = 0
    skipped = 0
    
    for a in articles:
        body = a["body"]
        
        # Skip if already has follow links
        if "**Follow:**" in body or "**Follow**:" in body:
            skipped += 1
            continue
        
        celebs = find_celebrities(a["headline"], body)
        if not celebs:
            print(f'  ⚪ No celebrities found: {a["headline"][:60]}')
            continue
        
        follow_line = build_follow_line(celebs)
        if not follow_line:
            continue
        
        new_body = body.rstrip() + "\n\n" + follow_line
        
        if dry_run:
            print(f'  📝 Would add to: {a["headline"][:60]}')
            print(f'     {follow_line}')
        else:
            patch = requests.patch(
                f'{SB}/rest/v1/p2_articles?id=eq.{a["id"]}',
                headers=H,
                json={"body": new_body},
                timeout=10
            )
            if patch.status_code < 300:
                print(f'  ✅ {a["headline"][:60]}')
                print(f'     {follow_line}')
            else:
                print(f'  ❌ Failed: {patch.status_code} {patch.text[:100]}')
        updated += 1
    
    print(f'\n{"Would update" if dry_run else "Updated"}: {updated} | Skipped (already has links): {skipped}')

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Actually update (default: dry run)")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--article-id", help="Process single article")
    args = parser.parse_args()
    
    process_articles(dry_run=not args.apply, limit=args.limit, article_id=args.article_id)
