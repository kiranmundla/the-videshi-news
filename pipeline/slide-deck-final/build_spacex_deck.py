#!/usr/bin/env python3
"""SpaceX IPO deck — clean layout, verified data, photo backgrounds.
SpaceX-only: slide 3 is a SpaceX-native diaspora angle (Starlink in India),
no Cursor/Aman Sanger. Outputs 3 PNGs (IG carousel) into slide-deck-final/."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance

W, H = 1080, 1920
IDIR = "/usr/share/fonts/truetype/inter"
GOLD=(212,175,55); GOLD_BR=(242,200,75); WHITE=(245,247,250); MUTED=(176,189,209)
NAVY_TOP=(8,16,30); NAVY_BOT=(20,34,56)
PANEL=(244,240,230); GREEN_BR=(46,184,90); BLUE=(74,144,226); SAFFRON=(255,153,51)

def font(sz,w="bold"):
    p={"extrabold":f"{IDIR}/InterDisplay-ExtraBold.ttf","bold":f"{IDIR}/InterDisplay-Bold.ttf",
       "semibold":f"{IDIR}/Inter-SemiBold.ttf","medium":f"{IDIR}/Inter-Medium.ttf","regular":f"{IDIR}/Inter-Regular.ttf"}
    try: return ImageFont.truetype(p.get(w,p["bold"]),sz)
    except Exception: return ImageFont.load_default()

def cover_fit(im,w,h): return ImageOps.fit(im,(w,h),Image.LANCZOS)
def vscrim(w,h,top_a,bot_a):
    s=Image.new("L",(1,h))
    for y in range(h): s.putpixel((0,y),int(top_a+(bot_a-top_a)*(y/(h-1))))
    return s.resize((w,h))
def navy_bg():
    img=Image.new("RGB",(W,H),NAVY_TOP); px=img.load()
    for y in range(H):
        t=(y/(H-1))**0.9
        row=(int(NAVY_TOP[0]+(NAVY_BOT[0]-NAVY_TOP[0])*t),int(NAVY_TOP[1]+(NAVY_BOT[1]-NAVY_TOP[1])*t),int(NAVY_TOP[2]+(NAVY_BOT[2]-NAVY_TOP[2])*t))
        for x in range(W): px[x,y]=row
    tex=Image.new("RGBA",(W,H),(0,0,0,0)); td=ImageDraw.Draw(tex)
    for k in range(-H,W,56): td.line([(k,0),(k+H,H)],fill=(212,175,55,8),width=1)
    return Image.alpha_composite(img.convert("RGBA"),tex).convert("RGB")
def wrap(d,text,f,max_w):
    words=text.split(); lines=[]; cur=[]; cw=0; sw=d.textlength(" ",font=f)
    for wd in words:
        ww=d.textlength(wd,font=f); add=ww+(sw if cur else 0)
        if cur and cw+add>max_w: lines.append(cur); cur=[wd]; cw=ww
        else: cur.append(wd); cw+=add
    if cur: lines.append(cur)
    return lines
def eyebrow(d,label,accent,y=120):
    MX=90; f=font(30,"extrabold"); tw=d.textlength(label,font=f)
    d.rounded_rectangle([MX,y,MX+tw+56,y+58],radius=29,fill=accent)
    d.text((MX+28,y+13),label,font=f,fill=(12,20,34))
def dots(d,idx,total):
    cy=H-110; gap=34; cx0=W//2-(total-1)*gap//2
    for i in range(total):
        c=GOLD_BR if i==idx else (110,124,150); r=9 if i==idx else 7
        d.ellipse([cx0+i*gap-r,cy-r,cx0+i*gap+r,cy+r],fill=c)
    if idx<total-1:
        f=font(28,"bold"); t="swipe →"
        d.text((W-90-d.textlength(t,font=f),cy-16),t,font=f,fill=MUTED)
def wordmark(d):
    f=font(26,"extrabold")
    d.text((90,H-172),"THE VIDESHI",font=f,fill=GOLD)
    f2=font(24,"medium")
    d.text((90+d.textlength("THE VIDESHI",font=f)+16,H-170),"·  thevideshi.com",font=f2,fill=MUTED)

OUT=os.path.expanduser("~/workspace/the-videshi-news/pipeline/slide-deck-final")
os.makedirs(OUT,exist_ok=True)
MX=90

def slide1():
    img=cover_fit(Image.open("/tmp/spacex_v.jpg").convert("RGB"),W,H)
    img=ImageEnhance.Color(img).enhance(1.08); img=ImageEnhance.Contrast(img).enhance(1.05)
    img=Image.composite(Image.new("RGB",(W,H),(4,8,18)),img,vscrim(W,H,70,235))
    img=Image.composite(Image.new("RGB",(W,H),(4,8,18)),img,vscrim(W,H,150,0))
    d=ImageDraw.Draw(img)
    eyebrow(d,"MARKETS · TECH",GOLD_BR)
    f=font(96,"extrabold"); y=1060
    for ln in wrap(d,"SPACEX JUST PULLED OFF THE BIGGEST IPO EVER",f,W-2*MX):
        x=MX
        for wd in ln:
            col=GOLD_BR if wd in ("BIGGEST","IPO","EVER") else WHITE
            d.text((x+3,y+3),wd,font=f,fill=(0,0,0)); d.text((x,y),wd,font=f,fill=col)
            x+=d.textlength(wd,font=f)+d.textlength(" ",font=f)
        y+=104
    sf=font(44,"semibold"); y+=18
    for ln in wrap(d,"$75 billion raised. A record that beats Saudi Aramco.",sf,W-2*MX):
        d.text((MX,y)," ".join(ln),font=sf,fill=(225,232,242)); y+=58
    dots(d,0,3); wordmark(d); img.save(f"{OUT}/slide1.png")

def slide2():
    img=navy_bg()
    photo=cover_fit(Image.open("/tmp/spacex_pad.jpg").convert("RGB"),W,700)
    img.paste(photo,(0,0))
    img.paste(Image.new("RGB",(W,260),NAVY_TOP),(0,440),vscrim(W,260,0,255))
    d=ImageDraw.Draw(img)
    eyebrow(d,"BY THE NUMBERS",GOLD_BR)
    d.text((MX,640),"The deal, in figures",font=font(66,"extrabold"),fill=WHITE)
    d.line([(MX,728),(W-MX,728)],fill=GOLD,width=3)
    tiles=[("$135","IPO price per share",BLUE),("$75B","total raised — largest ever",GREEN_BR),
           ("+19%","first-day pop on Nasdaq",SAFFRON),("$2.2T","valuation after day one",GOLD_BR)]
    gw=(W-2*MX-30)//2; gh=300; gap=30; gy=780
    for i,(big,lab,ac) in enumerate(tiles):
        r=i//2; c=i%2; x=MX+c*(gw+gap); y=gy+r*(gh+gap)
        d.rounded_rectangle([x,y,x+gw,y+gh],radius=24,fill=PANEL)
        d.rounded_rectangle([x,y,x+gw,y+14],radius=7,fill=ac)
        d.text((x+34,y+50),big,font=font(96,"extrabold"),fill=(20,30,50))
        for j,ln in enumerate(wrap(d,lab,font(33,"semibold"),gw-60)):
            d.text((x+34,y+170+j*40)," ".join(ln),font=font(33,"semibold"),fill=(96,110,130))
    dots(d,1,3); wordmark(d); img.save(f"{OUT}/slide2.png")

def slide3():
    img=navy_bg(); d=ImageDraw.Draw(img)
    eyebrow(d,"THE DIASPORA ANGLE",SAFFRON)
    f=font(74,"extrabold"); y=240
    for ln in wrap(d,"Worth $2.2 trillion — but still grounded in India",f,W-2*MX):
        x=MX
        for wd in ln:
            col=GOLD_BR if wd.strip(".") in ("$2.2","trillion") else WHITE
            d.text((x+2,y+2),wd,font=f,fill=(0,0,0)); d.text((x,y),wd,font=f,fill=col)
            x+=d.textlength(wd,font=f)+d.textlength(" ",font=f)
        y+=84
    facts=["Starlink — SpaceX's internet arm — is still not live in India",
           "June 2026: New Delhi froze final clearance on security grounds",
           "It already holds GMPCS + IN-SPACe licences, yet sits in limbo",
           "For NRIs back home, rural broadband keeps waiting on politics"]
    ff=font(37,"medium"); fact_lines=[wrap(d,ft,ff,W-2*MX-130) for ft in facts]
    block_h=sum(46*len(fl)+24 for fl in fact_lines)
    pad_top=200
    ph=pad_top+block_h+30
    py=y+30
    d.rounded_rectangle([MX,py,W-MX,py+ph],radius=26,fill=(16,28,48),outline=(40,56,84),width=2)
    d.rounded_rectangle([MX,py,MX+14,py+ph],radius=7,fill=SAFFRON)
    d.text((MX+50,py+40),"STARLINK IN INDIA",font=font(54,"extrabold"),fill=WHITE)
    d.text((MX+50,py+112),"The world's biggest IPO, still on hold",font=font(38,"semibold"),fill=GOLD_BR)
    yy=py+pad_top
    for fl in fact_lines:
        d.ellipse([MX+50,yy+10,MX+50+18,yy+28],fill=SAFFRON)
        for j,ln in enumerate(fl):
            d.text((MX+88,yy+j*46)," ".join(ln),font=ff,fill=(214,224,238))
        yy+=46*len(fl)+24
    cy=py+ph+50
    d.rounded_rectangle([MX,cy,W-MX,cy+108],radius=26,fill=GOLD)
    cf=font(44,"extrabold"); t="Read the full story → thevideshi.com"
    d.text((MX+(W-2*MX-d.textlength(t,font=cf))//2,cy+28),t,font=cf,fill=(14,22,38))
    dots(d,2,3); wordmark(d); img.save(f"{OUT}/slide3.png")

slide1(); slide2(); slide3()
print("done",OUT)
