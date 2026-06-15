#!/usr/bin/env python3
import os, json, subprocess, urllib.parse, requests, time

def load_env(path):
    if not os.path.exists(path): return
    for line in open(path):
        line=line.strip()
        if line and not line.startswith('#') and '=' in line:
            k,_,v=line.partition('='); os.environ[k.strip().replace('export ','')]=v.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))
SB=os.environ['SUPABASE_URL']; KEY=os.environ['SUPABASE_SERVICE_ROLE_KEY']; PX=os.environ.get('PEXELS_API_KEY','')
UA={"User-Agent":"TheVideshi/1.0 (thevideshi.com)"}
H={"apikey":KEY,"Authorization":f"Bearer {KEY}","Content-Type":"application/json","Prefer":"return=representation"}

def commons(q,limit=8):
    p={"action":"query","generator":"search","gsrsearch":q,"gsrnamespace":"6","gsrlimit":str(limit),
       "prop":"imageinfo","iiprop":"url|size|mime","iiurlwidth":"1200","format":"json"}
    try:
        r=requests.get("https://commons.wikimedia.org/w/api.php",params=p,headers=UA,timeout=15)
        out=[]
        if r.status_code==200:
            for pid,page in r.json().get("query",{}).get("pages",{}).items():
                ii=page.get("imageinfo",[{}])[0]
                u=ii.get("thumburl") or ii.get("url"); m=ii.get("mime","")
                if u and "image" in m and ii.get("width",0)>300:
                    out.append({"url":u,"title":page.get("title","")})
        return out
    except Exception as e:
        print("commons err",e); return []

def pexels(q):
    try:
        r=subprocess.run(["curl","-sS","-H",f"Authorization: {PX}",
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape"],
            capture_output=True,text=True,timeout=15)
        for ph in json.loads(r.stdout).get("photos",[]):
            u=ph.get("src",{}).get("large2x") or ph.get("src",{}).get("large")
            if u: return u
    except Exception as e: print("pexels err",e)
    return None

def valid(u):
    try:
        r=requests.get(u,timeout=12,stream=True,allow_redirects=True,headers=UA)
        ct=r.headers.get("Content-Type",""); c=r.raw.read(12000)
        ok=r.status_code==200 and "image" in ct and len(c)>5000
        print(f"   {'OK' if ok else 'FAIL'} {r.status_code} {ct} {len(c)}b  {u[:70]}")
        return ok
    except Exception as e:
        print("   valid err",e); return False

def patch(slug,url,cap,attr):
    r=requests.patch(f"{SB}/rest/v1/p2_articles?slug=eq.{slug}",headers=H,
        json={"image_url":url,"image_caption":cap,"image_attribution":attr},timeout=20)
    print(f"  PATCH {slug}: {r.status_code}")
    return r.status_code in (200,204)

jobs=[
 ("germany-scraps-airport-transit-visa-indian-travellers-frankfurt-munich-20260615",
  [("Frankfurt Airport terminal interior",["frankfurt","airport","terminal","flughafen"])],
  "airport terminal departure international",
  "An international airport transit terminal","Frankfurt Airport, a major transit hub for Indians flying onward"),
 ("delhi-malviya-nagar-bnb-fire-23-dead-inspector-sacked-building-violations-20260615",
  [("Delhi Fire Service",["fire","delhi","brigade","service"]),("New Delhi street Malviya",["delhi","street","india"])],
  "fire truck firefighter emergency",
  "Firefighters respond to a blaze","Delhi Fire Service personnel respond to a fire (illustrative)"),
]

for slug,cqs,pxq,pxcap,cap in jobs:
    print("==>",slug)
    chosen=None
    for q,kws in cqs:
        for img in commons(q,8):
            tl=img["title"].lower()
            if any(k in tl for k in kws) and valid(img["url"]):
                chosen=(img["url"],cap,"Wikimedia Commons"); break
        if chosen: break
        time.sleep(2)
    if not chosen:
        u=pexels(pxq)
        if u and valid(u): chosen=(u,pxcap,"Pexels")
    if chosen:
        patch(slug,*chosen)
    else:
        print("  !! no image found")
