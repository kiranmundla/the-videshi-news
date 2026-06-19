#!/usr/bin/env python3
"""Cross-article HERO dedup detector for Videshi.
Perceptual-hashes every published hero image (last N days), groups near-identical
photos that are used as the hero on DIFFERENT articles (same photo, any host/size).
Report only — does not modify anything."""
import json, time, io, sys
from pathlib import Path
from collections import defaultdict
import requests
from PIL import Image
import imagehash

def load_env(p):
    env={}
    for line in (Path.home()/p).read_text().splitlines():
        line=line.strip()
        if not line or line.startswith('#') or '=' not in line: continue
        k,v=line.split('=',1); env[k.strip()]=v.strip().strip('"').strip("'")
    return env
env=load_env('workspace/.env.supabase')
URL=env['SUPABASE_URL']; KEY=env.get('SUPABASE_SERVICE_ROLE_KEY') or env.get('SUPABASE_KEY')
H={'apikey':KEY,'Authorization':f'Bearer {KEY}'}
DAYS=int(sys.argv[1]) if len(sys.argv)>1 else 3
THRESH=6

since=time.strftime('%Y-%m-%dT%H:%M:%S',time.gmtime(time.time()-DAYS*86400))
r=requests.get(f"{URL}/rest/v1/p2_articles",headers=H,
  params={'select':'id,slug,image_url,category,published_at','published_at':f'gte.{since}','status':'eq.published','order':'published_at.desc','limit':'2000'},timeout=60)
arts=r.json()
print(f"published last {DAYS}d: {len(arts)}")

# hash unique urls
uniq=defaultdict(list)
for a in arts:
    if a.get('image_url'): uniq[a['image_url']].append(a)
print(f"unique hero URLs: {len(uniq)}")

UA={'User-Agent':'TheVideshi/1.0 (thevideshi.com)'}
hashes={}
failed=0
for i,u in enumerate(uniq):
    try:
        rr=requests.get(u,timeout=20,headers=UA)
        if rr.status_code!=200:
            failed+=1; continue
        img=Image.open(io.BytesIO(rr.content)).convert('RGB')
        hashes[u]=imagehash.phash(img)
    except Exception:
        failed+=1
print(f"hashed {len(hashes)} urls ({failed} failed)\n")

# group urls by perceptual closeness
urls=list(hashes.keys())
used=set()
groups=[]
for i in range(len(urls)):
    if urls[i] in used: continue
    grp=[urls[i]]; used.add(urls[i])
    for j in range(i+1,len(urls)):
        if urls[j] in used: continue
        if hashes[urls[i]]-hashes[urls[j]] <= THRESH:
            grp.append(urls[j]); used.add(urls[j])
    # collect all articles across the urls in this group
    artlist=[]
    for u in grp: artlist.extend(uniq[u])
    if len(artlist)>1:
        groups.append((grp,artlist))

groups.sort(key=lambda g:-len(g[1]))
print(f"=== {len(groups)} groups of the SAME PHOTO used as hero on multiple articles ===\n")
for grp,artlist in groups:
    multihost = len(grp)>1
    tag = "  [CROSS-HOST/SIZE]" if multihost else ""
    print(f"x{len(artlist)} articles{tag}")
    for u in grp:
        print(f"    url: {u.split('/')[-1][:60]}")
    for a in sorted(artlist,key=lambda x:x['published_at'],reverse=True):
        print(f"      {a['published_at'][:16]} {a['category'][:11]:11} {a['slug'][:55]}")
    print()
