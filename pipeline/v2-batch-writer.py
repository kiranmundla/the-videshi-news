#!/usr/bin/env python3
"""V2 Batch Writer for The Videshi"""
import json, os, re, subprocess, sys, time, urllib.parse
from datetime import datetime, timezone

def load_env(path):
    path = os.path.expanduser(path)
    if not os.path.exists(path): return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line: continue
            k, v = line.split('=', 1)
            k = k.strip().lstrip('export').strip()
            os.environ[k] = v.strip().strip('"').strip("'")

load_env("~/workspace/.env.supabase")
load_env("~/workspace/.env.openai")
load_env("~/workspace/.env.pexels")

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
OAI_KEY = os.environ.get("OPENAI_API_KEY", "")
PXL_KEY = os.environ.get("PEXELS_API_KEY", "")
UA = "TheVideshi/1.0 (thevideshi.com)"
CATS = ["immigration","technology","news","entertainment","sports","markets-finance","nri-world","food","travel","lifestyle-health"]
CAT_VERT = {"immigration":"immigration","technology":"tech","news":"geopolitics","entertainment":"entertainment","sports":"sports","markets-finance":"markets","nri-world":"diaspora","food":"food-culture","travel":"aviation","lifestyle-health":"lifestyle"}

def curl_json(method, url, data=None, headers=None, timeout=60):
    cmd = ["curl","-sS","--max-time",str(timeout),"-X",method,url]
    if headers:
        for k,v in headers.items(): cmd += ["-H",f"{k}: {v}"]
    if data: cmd += ["-d", json.dumps(data)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+10)
        if r.stdout: return json.loads(r.stdout)
    except: pass
    return None

def sb_rest(method, table, params="", data=None):
    return curl_json(method, f"{SB_URL}/rest/v1/{table}{params}", data=data, headers={
        "apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}","Content-Type":"application/json","Prefer":"return=representation"})

def make_slug(headline):
    slug = re.sub(r'[^\w\s-]','',headline.lower().strip())
    slug = re.sub(r'[\s_]+','-',slug)
    slug = re.sub(r'-+','-',slug).strip('-')
    parts = slug.split('-'); result=[]; ln=0
    for p in parts:
        if ln+len(p)>80: break
        result.append(p); ln+=len(p)+1
    return ('-'.join(result) if result else slug[:80]) + '-' + datetime.now(timezone.utc).strftime('%Y%m%d')

def fetch_text(url):
    try:
        import trafilatura
        r = subprocess.run(["curl","-sS","--max-time","15","-L","-A",UA,url], capture_output=True, text=True, timeout=20)
        if not r.stdout or len(r.stdout)<500: return None
        t = trafilatura.extract(r.stdout, include_comments=False, include_tables=True, favor_precision=True)
        return t[:5000] if t and len(t)>200 else None
    except: return None

def get_sources(cand):
    sources = []
    for u in cand.get('source_urls',[]):
        if 'news.google.com' not in u:
            t = fetch_text(u)
            if t: sources.append((t,u))
    desc = cand.get('description','')
    sigs = '\n'.join(f"- {s.get('title','')} ({s.get('source','')})" for s in cand.get('all_signals',[]) if s.get('title'))
    if desc or sigs: sources.append((f"{desc}\n\nRelated:\n{sigs}", 'signals'))
    return sources

def call_openai(prompt, max_tokens=4096):
    if not OAI_KEY: return None
    r = curl_json("POST","https://api.openai.com/v1/chat/completions",
        data={"model":"gpt-4o-mini","messages":[{"role":"user","content":prompt}],"temperature":0.3,"max_tokens":max_tokens,"response_format":{"type":"json_object"}},
        headers={"Authorization":f"Bearer {OAI_KEY}","Content-Type":"application/json"}, timeout=120)
    if not r: return None
    try: return json.loads(r["choices"][0]["message"]["content"])
    except: return None

PROMPT = """You are a senior journalist at The Videshi, a news site for Indians living abroad.
Write a comprehensive article from the source material below. Write ONLY from sources — no invented facts.

REQUIREMENTS:
- headline: Clear, engaging, 8-15 words. No source names.
- subheadline: 1-2 sentences expanding the headline
- body: 400-700 words with ## subheadings. Include diaspora angle where natural. For markets: Bloomberg-style tone.
- vertical: short topic descriptor like "h1b-visas", "geopolitics", "cricket", "ai", "streaming", "aviation", "markets", etc.
- key_takeaways: 3-5 bullet points
- image_search_query: 2-4 word Pexels search query

SOURCES:
{sources}

CANDIDATE: {title}
Category: {cat}
Importance: {reason}

Return JSON: {{"headline":"...","subheadline":"...","body":"...","key_takeaways":["..."],"category":"{cat}","vertical":"...","tags":["..."],"newsworthiness":<1-35>,"diaspora_impact":<1-20>,"prominence":<1-25>,"image_search_query":"..."}}"""

def write_article(cand, sources):
    src_text = ""
    for t,l in sources:
        src_text += f"\n--- {l} ---\n{t[:3000]}\n"
    if not src_text.strip(): src_text = cand['title'] + '\n' + cand.get('description','')
    r = call_openai(PROMPT.format(sources=src_text[:8000], title=cand['title'], cat=cand['category'], reason=cand.get('llm_reason','')))
    if not r: return None
    body = r.get('body','')
    tks = r.get('key_takeaways',[])
    if tks:
        items = ''.join(f'<li>{t}</li>' for t in tks)
        body = f'<!-- data-card -->\n<div class="vdc-takeaways"><div class="vdc-takeaways-title">Key Takeaways</div><ul class="vdc-takeaways-list">{items}</ul></div>\n\n' + body
    cat = r.get('category',cand['category'])
    if cat not in CATS: cat = cand['category']
    if cat not in CATS: cat = 'news'
    return {
        'headline': r.get('headline',cand['title'][:120]),
        'subheadline': r.get('subheadline',''),
        'body': body, 'slug': make_slug(r.get('headline',cand['title'][:120])),
        'category': cat, 'vertical': r.get('vertical',CAT_VERT.get(cat,'general')),
        'tags': r.get('tags',[]), 'status': 'published',
        'word_count': len(body.split()),
        'newsworthiness': min(35,max(1,r.get('newsworthiness',20))),
        'diaspora_impact': min(20,max(1,r.get('diaspora_impact',10))),
        'prominence': min(25,max(1,r.get('prominence',15))),
        'sources': [u for _,u in sources if u!='signals'][:5],
        'llm_score': cand.get('llm_score',3),
        'signal_count': cand.get('signal_count',1),
        'key_takeaways': tks,
        'published_at': datetime.now(timezone.utc).isoformat(),
        'image_search_query': r.get('image_search_query',''),
    }

def pexels_image(query):
    if not PXL_KEY: return None
    r = curl_json("GET",f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape",
        headers={"Authorization":PXL_KEY})
    if r and r.get('photos'):
        p = r['photos'][0]
        return p['src'].get('large2x',p['src'].get('large','')), f"Photo by {p.get('photographer','Unknown')} on Pexels"
    return None

def add_hero(article):
    q = article.pop('image_search_query','') or ' '.join(article['headline'].split()[:4])
    img = pexels_image(q)
    if not img: img = pexels_image(' '.join(q.split()[:2]))
    if img:
        article['image_url'] = img[0]
        article['image_attribution'] = img[1]
    return article

def is_dup(cand, recent):
    tw = set(w for w in re.findall(r'\w+',cand['title'].lower()) if len(w)>3)
    for a in recent:
        hw = set(w for w in re.findall(r'\w+',a.get('headline','').lower()) if len(w)>3)
        if len(tw & hw) >= max(3, min(4, len(tw)//3)): return True, a['headline']
    return False, None

def main():
    print(f"\n{'='*60}\nV2 Batch Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n{'='*60}")
    with open("/tmp/v2-candidates.json") as f: candidates = json.load(f).get('candidates',[])
    print(f"📋 {len(candidates)} candidates")
    recent = sb_rest("GET","p2_articles","?select=headline,slug,category&status=eq.published&order=published_at.desc&limit=80") or []
    print(f"🔍 {len(recent)} recent articles")

    # Internal dedup
    seen={}; unique=[]
    for c in candidates:
        fp = ' '.join(sorted(set(w.lower() for w in re.findall(r'\w+',c['title']) if len(w)>4))[:6])
        skip = any(len(set(sfp.split())&set(fp.split()))>=3 for sfp in seen)
        if skip:
            print(f"  ⏭ dup: {c['title'][:50]}")
        else:
            seen[fp]=c; unique.append(c)
    print(f"📋 {len(unique)} after dedup")

    published=[]; skipped=0; failed=0
    for i,c in enumerate(unique,1):
        title = c['title'][:80]
        print(f"\n[{i}/{len(unique)}] [{c['category']}] {title}")
        dup, dup_of = is_dup(c, recent)
        if dup:
            print(f"  ⏭ Already covered: {dup_of[:60]}")
            skipped+=1; continue
        sources = get_sources(c)
        real = len([1 for _,u in sources if u!='signals'])
        print(f"  📡 {real} direct source(s)")
        art = write_article(c, sources)
        if not art: print(f"  ✗ Write failed"); failed+=1; continue
        print(f"  📰 {art['headline'][:70]}")
        print(f"  📊 {art['word_count']}w N:{art['newsworthiness']} D:{art['diaspora_impact']} P:{art['prominence']}")
        art = add_hero(art)
        print(f"  🖼 {'✓' if art.get('image_url') else '⚠ none'}")
        r = sb_rest("POST","p2_articles",data=art)
        if r and isinstance(r,list) and r:
            print(f"  ✓ Published ({r[0].get('id','?')[:8]})")
            published.append({'headline':art['headline'],'category':art['category'],'slug':art['slug'],'id':r[0].get('id','')})
            recent.append({'headline':art['headline'],'slug':art['slug'],'category':art['category']})
        else:
            err = json.dumps(r)[:200] if r else 'no response'
            print(f"  ✗ Insert error: {err}")
            if r and isinstance(r,dict) and ('23505' in str(r.get('code','')) or 'duplicate' in str(r).lower()):
                art['slug']+= '-v2'
                r2 = sb_rest("POST","p2_articles",data=art)
                if r2 and isinstance(r2,list) and r2:
                    print(f"  ✓ Published with -v2")
                    published.append({'headline':art['headline'],'category':art['category'],'slug':art['slug'],'id':r2[0].get('id','')})
                    recent.append({'headline':art['headline'],'slug':art['slug'],'category':art['category']})
                else: failed+=1
            else: failed+=1

    print(f"\n{'='*60}\n✅ {len(published)} published | ⏭ {skipped} skipped | ❌ {failed} failed\n{'='*60}")
    for p in published: print(f"  [{p['category']}] {p['headline'][:70]}")
    with open('/tmp/v2-results.json','w') as f: json.dump({'published':published,'skipped':skipped,'failed':failed},f,indent=2)
    return len(published)

if __name__=='__main__': main()
