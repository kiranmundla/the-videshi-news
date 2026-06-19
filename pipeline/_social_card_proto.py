#!/usr/bin/env python3
"""Prototype: render a 'social post card' reel scene (1080x1920) from a real X post.
Brand-styled (navy/gold) frame around the post photo, with avatar, name, handle,
platform badge, and a 'via @handle on X' attribution line. Read-only test."""
import os, json, subprocess, textwrap
from io import BytesIO
from requests_oauthlib import OAuth1Session
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

def load_env(p):
    p=os.path.expanduser(p)
    if os.path.exists(p):
        for line in open(p):
            line=line.strip()
            if line and not line.startswith('#') and '=' in line:
                k,v=line.split('=',1); os.environ.setdefault(k.strip(),v.strip())
load_env('~/workspace/.env.twitter')

CK,CS=os.environ['TWITTER_CONSUMER_KEY'],os.environ['TWITTER_CONSUMER_SECRET']
AT,ATS=os.environ['TWITTER_ACCESS_TOKEN'],os.environ['TWITTER_ACCESS_TOKEN_SECRET']
S=OAuth1Session(CK,CS,AT,ATS)

GOLD=(212,175,55); GOLD_SOFT=(224,196,110)
NAVY_TOP=(8,16,30); NAVY_BOT=(19,33,54)
WHITE=(245,247,250); MUTED=(150,165,185)
IDIR="/usr/share/fonts/truetype/inter"

def font(sz,w="bold"):
    paths={"extrabold":f"{IDIR}/InterDisplay-ExtraBold.ttf","bold":f"{IDIR}/InterDisplay-Bold.ttf",
           "semibold":f"{IDIR}/Inter-SemiBold.ttf","regular":f"{IDIR}/Inter-Regular.ttf"}
    try: return ImageFont.truetype(paths.get(w,paths["bold"]),sz)
    except Exception: return ImageFont.load_default()

def vgrad(W,H,top,bot):
    base=Image.new("RGB",(W,H),top); px=base.load()
    for y in range(H):
        t=(y/max(H-1,1))**0.85
        r=int(top[0]+(bot[0]-top[0])*t); g=int(top[1]+(bot[1]-top[1])*t); b=int(top[2]+(bot[2]-top[2])*t)
        for x in range(W): px[x,y]=(r,g,b)
    return base

def dl(url):
    out=subprocess.run(["curl","-sL","-A","Mozilla/5.0",url],capture_output=True).stdout
    return Image.open(BytesIO(out)).convert("RGB")

def circle(img,size):
    img=ImageOps.fit(img,(size,size),Image.LANCZOS)
    mask=Image.new("L",(size,size),0); ImageDraw.Draw(mask).ellipse([0,0,size,size],fill=255)
    out=Image.new("RGBA",(size,size),(0,0,0,0)); out.paste(img,(0,0),mask); return out

def clean_text(t):
    import re
    t=re.sub(r'https?://t\.co/\S+','',t)        # strip t.co links
    t=re.sub(r'https?://\S+','',t)              # strip any other urls
    # strip emoji / non-BMP + symbol blocks the font can't render
    t=''.join(ch for ch in t if ord(ch)<0x2190 or (0x2C00<=ord(ch)<0x2E00))
    return ' '.join(t.split())

def draw_x_badge(d,img,x,y,s):
    """Paste the real X logo (white) centered in a rounded black square of side s."""
    d.rounded_rectangle([x,y,x+s,y+s],radius=int(s*0.22),fill=(0,0,0))
    try:
        logo=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "assets","x-logo-white.png")).convert("RGBA")
        gw=int(s*0.50); gh=int(gw*logo.height/logo.width)
        logo=logo.resize((gw,gh),Image.LANCZOS)
        img.paste(logo,(x+(s-gw)//2,y+(s-gh)//2),logo)
    except Exception as e:
        print("  x-logo paste failed:",e)

def fetch_post(handle):
    u=S.get(f'https://api.twitter.com/2/users/by/username/{handle}',
            params={'user.fields':'profile_image_url,name,verified'},timeout=20).json()['data']
    uid=u['id']
    t=S.get(f'https://api.twitter.com/2/users/{uid}/tweets',
            params={'max_results':20,'tweet.fields':'created_at,attachments,text',
                    'expansions':'attachments.media_keys','media.fields':'type,url',
                    'exclude':'retweets,replies'},timeout=20).json()
    media={m['media_key']:m for m in t.get('includes',{}).get('media',[])}
    for tw in t.get('data',[]):
        ph=[media[k]['url'] for k in tw.get('attachments',{}).get('media_keys',[])
            if media.get(k,{}).get('type')=='photo']
        if ph:
            return {'name':u['name'],'handle':handle,'avatar':u['profile_image_url'].replace('_normal','_400x400'),
                    'verified':u.get('verified',False),'text':tw['text'],'photo':ph[0]}
    return None

def render(post,out="/tmp/social_card_demo.png"):
    W,H=1080,1920
    img=vgrad(W,H,NAVY_TOP,NAVY_BOT).convert("RGBA")
    # subtle diagonal texture
    tex=Image.new("RGBA",(W,H),(0,0,0,0)); td=ImageDraw.Draw(tex)
    for k in range(-H,W,54): td.line([(k,0),(k+H,H)],fill=(212,175,55,9),width=1)
    img=Image.alpha_composite(img,tex)
    d=ImageDraw.Draw(img)
    MX=96
    # eyebrow
    y=150
    d.rectangle([MX,y+6,MX+26,y+32],fill=GOLD)
    d.text((MX+44,y)," ".join("ON THE FEED"),font=font(34,"extrabold"),fill=GOLD_SOFT)
    y+=64; d.line([(MX,y),(W-MX,y)],fill=GOLD,width=3); y+=70

    # the post photo, rounded, framed
    photo=dl(post['photo'])
    pw=W-2*MX; ph=int(pw*0.62)
    photo=ImageOps.fit(photo,(pw,ph),Image.LANCZOS)
    rc=Image.new("L",(pw,ph),0); ImageDraw.Draw(rc).rounded_rectangle([0,0,pw,ph],radius=28,fill=255)
    # gold frame
    d.rounded_rectangle([MX-4,y-4,MX+pw+4,y+ph+4],radius=32,outline=GOLD,width=3)
    img.paste(photo,(MX,y),rc)
    y+=ph+46

    # author row: avatar + name + handle
    av=circle(dl(post['avatar']),104)
    img.paste(av,(MX,y),av)
    d.ellipse([MX,y,MX+104,y+104],outline=GOLD,width=3)
    nx=MX+128
    d.text((nx,y+8),post['name'],font=font(46,"extrabold"),fill=WHITE)
    d.text((nx,y+62),f"@{post['handle']}",font=font(34,"semibold"),fill=MUTED)
    # platform badge top-right (X) — drawn with strokes, not a font glyph
    bs=84
    draw_x_badge(d,img,W-MX-bs,y+10,bs)
    y+=140

    # post text (cleaned: no urls, no emoji/tofu)
    txt=clean_text(post['text'])
    if len(txt)>150: txt=txt[:150].rsplit(' ',1)[0]+"…"
    tf=font(40,"semibold")
    for line in textwrap.wrap(txt,width=42)[:4]:
        d.text((MX,y),line,font=tf,fill=(228,233,240)); y+=54

    # attribution footer
    fy=H-150
    d.line([(MX,fy),(W-MX,fy)],fill=(60,72,92),width=2)
    d.text((MX,fy+24),f"via @{post['handle']} on X",font=font(34,"semibold"),fill=GOLD_SOFT)
    d.text((W-MX-260,fy+24),"thevideshi.com",font=font(34,"extrabold"),fill=WHITE)

    img.convert("RGB").save(out,quality=92)
    print("saved",out)

p=fetch_post(os.environ.get("H","imVkohli"))
print(json.dumps({k:v for k,v in p.items() if k!='text'},indent=2) if p else "no post")
if p: render(p)
