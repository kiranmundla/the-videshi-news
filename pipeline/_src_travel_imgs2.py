#!/usr/bin/env python3
import os, io, requests, subprocess, tempfile
from pathlib import Path
from PIL import Image

for envf in [".env.supabase", ".env.pexels"]:
    p = Path.home() / "workspace" / envf
    if p.exists():
        for line in p.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip())

SB_URL=os.environ["SUPABASE_URL"]; SB_KEY=os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS=os.environ.get("PEXELS_API_KEY",""); UA={"User-Agent":"TheVideshi/1.0 (thevideshi.com)"}
BAD_EXT=(".djvu",".svg",".pdf",".tif",".tiff",".gif")

def commons(q,limit=8):
    params={"action":"query","generator":"search","gsrsearch":q,"gsrnamespace":"6","gsrlimit":str(limit),
            "prop":"imageinfo","iiprop":"url|size|mime","iiurlwidth":"1280","format":"json"}
    try:
        r=requests.get("https://commons.wikimedia.org/w/api.php",params=params,headers=UA,timeout=20); out=[]
        if r.status_code==200:
            for pid,page in r.json().get("query",{}).get("pages",{}).items():
                ii=page.get("imageinfo",[{}])[0]; mime=ii.get("mime",""); title=page.get("title","")
                if mime not in ("image/jpeg","image/png"): continue
                if any(title.lower().endswith(e) for e in BAD_EXT): continue
                if ii.get("width",0)<700: continue
                out.append({"url":ii.get("thumburl") or ii.get("url"),"title":title,"w":ii.get("width")})
        return out
    except Exception as e: print("commons err",e); return []

def pexels(q,n=6):
    if not PEXELS: return []
    try:
        r=requests.get("https://api.pexels.com/v1/search",headers={"Authorization":PEXELS},
                       params={"query":q,"per_page":n,"orientation":"landscape"},timeout=20)
        if r.status_code==200:
            return [{"url":p["src"]["large2x"],"title":p.get("alt","") or q} for p in r.json().get("photos",[])]
    except Exception as e: print("pexels err",e)
    return []

def download(url):
    try:
        r=requests.get(url,headers=UA,timeout=40)
        if r.status_code==200 and len(r.content)>5000: return r.content
    except Exception: pass
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
    if r.status_code in (200,201): return f"{SB_URL}/storage/v1/object/public/article-images/{fn}"
    print("upload fail",r.status_code,r.text[:150]); return None

jobs=[
 ("india-river-cruise-boom-ganga-brahmaputra-nri-2026",
   ["Kerala backwaters houseboat Alleppey","Alappuzha backwaters houseboat Kerala","Brahmaputra river Assam boat","Ganges river boat Varanasi"],
   ["kerala backwaters houseboat","river cruise boat sunset"]),
 ("india-evisa-new-categories-transit-mountaineering-film-entry-nri-2026",
   ["Stok Kangri mountaineering Ladakh","mountaineers Himalaya India summit","Himalaya trekking expedition India","Nanda Devi mountaineering"],
   ["mountaineer himalaya snow summit","himalaya climbing expedition"]),
]
import json; results={}
for slug,cq,pq in jobs:
    print("\n===",slug,"===")
    cands=[]
    for q in cq:
        for c in commons(q,5):
            print("  cand:",c["title"][:65]); cands.append((c["url"],c["title"],"Wikimedia Commons"))
        if cands: break
    if not cands:
        for q in pq:
            for c in pexels(q,5): cands.append((c["url"],c["title"],"Pexels"))
            if cands: break
    picked=None
    for url,title,attr in cands:
        b=download(url)
        if not b: continue
        try: b=compress(b)
        except Exception as e: print("  compress err",e); continue
        # save locally for review, do not upload yet
        lp=f"/tmp/REVIEW_{slug}.jpg"; open(lp,"wb").write(b)
        picked={"url":url,"attr":attr,"title":title,"kb":round(len(b)/1024),"local":lp}
        print("  CANDIDATE SAVED:",lp,f"({picked['kb']}KB) <-",title[:55])
        break
    results[slug]=picked
print("\n=== REVIEW THESE BEFORE UPLOAD ===")
print(json.dumps(results,indent=2))
