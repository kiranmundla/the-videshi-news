#!/usr/bin/env python3
import os, io, requests
from pathlib import Path
from PIL import Image

for envf in [".env.supabase", ".env.pexels"]:
    p = Path.home() / "workspace" / envf
    if p.exists():
        for line in p.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS = os.environ.get("PEXELS_API_KEY", "")
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

def commons(q, limit=6):
    params = {"action":"query","generator":"search","gsrsearch":q,"gsrnamespace":"6",
              "gsrlimit":str(limit),"prop":"imageinfo","iiprop":"url|size|mime","iiurlwidth":"1280","format":"json"}
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params, headers=UA, timeout=20)
        out=[]
        if r.status_code==200:
            for pid,page in r.json().get("query",{}).get("pages",{}).items():
                ii=page.get("imageinfo",[{}])[0]; mime=ii.get("mime","")
                if not mime.startswith("image/") or mime=="image/svg+xml" or ii.get("width",0)<600: continue
                out.append({"url":ii.get("thumburl") or ii.get("url"),"title":page.get("title"),"w":ii.get("width"),"h":ii.get("height")})
        return out
    except Exception as e:
        print("commons err",e); return []

def pexels(q, n=5):
    if not PEXELS: return []
    try:
        r=requests.get("https://api.pexels.com/v1/search",headers={"Authorization":PEXELS},
                       params={"query":q,"per_page":n,"orientation":"landscape"},timeout=20)
        if r.status_code==200:
            return [{"url":p["src"]["large2x"],"title":p.get("alt","") or q} for p in r.json().get("photos",[])]
    except Exception as e:
        print("pexels err",e)
    return []

def download(url):
    try:
        r=requests.get(url,headers=UA,timeout=40)
        if r.status_code==200 and len(r.content)>5000: return r.content
        print("   dl bad",r.status_code,len(r.content) if r.ok else "")
    except Exception as e:
        print("   dl err",e)
    # curl fallback for wikimedia 429
    import subprocess, tempfile
    tf=tempfile.mktemp(suffix=".img")
    subprocess.run(["curl","-sS","-A",UA["User-Agent"],"-o",tf,url],timeout=60)
    if os.path.exists(tf) and os.path.getsize(tf)>5000:
        b=open(tf,"rb").read(); os.remove(tf); return b
    return None

def compress(b,max_w=1200,q=80):
    img=Image.open(io.BytesIO(b))
    if img.mode in ("RGBA","P"): img=img.convert("RGB")
    if img.width>max_w:
        ratio=max_w/img.width; img=img.resize((max_w,int(img.height*ratio)),Image.LANCZOS)
    buf=io.BytesIO(); img.save(buf,format="JPEG",quality=q,optimize=True); return buf.getvalue()

def upload(b,fn):
    r=requests.post(f"{SB_URL}/storage/v1/object/article-images/{fn}",
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}","Content-Type":"image/jpeg","x-upsert":"true"},
        data=b,timeout=60)
    if r.status_code in (200,201):
        return f"{SB_URL}/storage/v1/object/public/article-images/{fn}"
    print("   upload fail",r.status_code,r.text[:200]); return None

# (slug, [commons queries], [pexels queries])
jobs = [
  ("india-tourist-visa-on-arrival-180-countries-nri-2026",
    ["Indira Gandhi International Airport immigration","Chhatrapati Shivaji International Airport terminal arrivals","airport immigration counter India"],
    ["airport immigration arrival hall","passport control airport queue"]),
  ("india-river-cruise-boom-ganga-brahmaputra-nri-2026",
    ["MV Ganga Vilas cruise","Brahmaputra river cruise ship","Kerala backwaters houseboat Alappuzha"],
    ["river cruise boat India","kerala backwaters houseboat"]),
  ("india-evisa-new-categories-transit-mountaineering-film-entry-nri-2026",
    ["mountaineering Himalaya India climber","Himalayas mountaineering expedition India","Stok Kangri climbers Ladakh"],
    ["mountaineering himalaya climber","himalaya expedition tent"]),
]

results={}
for slug,cq,pq in jobs:
    print("\n===",slug,"===")
    cands=[]
    for q in cq:
        for c in commons(q,4):
            cands.append((c["url"],c["title"],"Wikimedia Commons"))
        if cands: break
    if not cands:
        for q in pq:
            for c in pexels(q,4):
                cands.append((c["url"],c["title"],"Pexels"))
            if cands: break
    picked=None
    for url,title,attr in cands:
        print("  try:",attr,"|",title[:60])
        b=download(url)
        if not b: continue
        try: b=compress(b)
        except Exception as e: print("   compress err",e); continue
        fn=f"{slug}.jpg"
        final=upload(b,fn)
        if final:
            picked={"url":final,"attr":attr,"title":title,"kb":round(len(b)/1024)}
            print("  PICKED:",final,f"({picked['kb']}KB)")
            break
    results[slug]=picked

print("\n\n=== SUMMARY ===")
import json
print(json.dumps(results,indent=2))
