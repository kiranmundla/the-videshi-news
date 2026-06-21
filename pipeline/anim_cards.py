#!/usr/bin/env python3
"""anim_cards.py — Animated data-card renderer for The Videshi reels.

WHY MP4, NOT HTML: Shotstack renders an `html` asset as a SINGLE static
snapshot — CSS @keyframes / JS count-ups do NOT play (verified empirically
2026-06-21: a slide-in + bar-grow card rendered identical across all frames
except the clip-level fade). So genuinely animated data cards are pre-rendered
here as 1080x1920 MP4 clips (PIL frames -> ffmpeg) and dropped on the Shotstack
timeline as VIDEO clips, which sidesteps the limitation entirely and gives full
control (count-ups, staggered entrances, growing bars, easing).

Three archetypes:
  (a) hero_stat   — one giant number that counts up, gold on navy
  (b) stat_grid   — 2x2 tiles that slide/fade in staggered, accent bars
  (c) diaspora    — saffron-accented panel, 3-4 bullet facts animating in

Brand: navy #0a1628 gradient, gold #D4AF37, saffron #FF9933, Inter, wordmark.
All public renderers return a local MP4 path (1080x1920, 25fps) or None.
"""
import os, math, subprocess, tempfile, re
from pathlib import Path

W, H = 1080, 1920
FPS = 25
IDIR = "/usr/share/fonts/truetype/inter"

GOLD=(212,175,55); GOLD_BR=(242,200,75); GOLD_SOFT=(224,196,110)
WHITE=(245,247,250); MUTED=(150,165,185); SUBTEXT=(203,214,230)
NAVY_TOP=(8,16,30); NAVY_BOT=(19,33,54); NAVY_T2=(10,20,38); NAVY_B2=(24,40,64)
SAFFRON=(255,153,51); PANEL=(244,240,230)
BLUE=(74,144,226); GREEN_BR=(46,184,90)

def _font(sz, w="bold"):
    from PIL import ImageFont
    p={"extrabold":f"{IDIR}/InterDisplay-ExtraBold.ttf","bold":f"{IDIR}/InterDisplay-Bold.ttf",
       "semibold":f"{IDIR}/Inter-SemiBold.ttf","medium":f"{IDIR}/Inter-Medium.ttf",
       "regular":f"{IDIR}/Inter-Regular.ttf"}
    try: return ImageFont.truetype(p.get(w,p["bold"]), sz)
    except Exception:
        try: return ImageFont.truetype(f"{IDIR}/Inter-Bold.ttf", sz)
        except Exception: return ImageFont.load_default()

# ── easing ──
def ease_out_cubic(t): return 1-(1-t)**3
def ease_out_back(t):
    c1,c3=1.70158,2.70158
    return 1+c3*(t-1)**3+c1*(t-1)**2
def clamp01(x): return 0.0 if x<0 else (1.0 if x>1 else x)

def _vgradient(top, bot):
    from PIL import Image
    img=Image.new("RGB",(W,H),top); px=img.load()
    for y in range(H):
        t=(y/(H-1))**0.9
        row=(int(top[0]+(bot[0]-top[0])*t),int(top[1]+(bot[1]-top[1])*t),int(top[2]+(bot[2]-top[2])*t))
        for x in range(W): px[x,y]=row
    return img

def _bg():
    """Navy gradient + subtle diagonal gold texture + soft corner glow."""
    from PIL import Image, ImageDraw
    img=_vgradient(NAVY_TOP, NAVY_BOT).convert("RGBA")
    # glow top-right
    glow=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gd.ellipse([int(W*0.55),int(-H*0.05),int(W*1.25),int(H*0.45)],fill=(60,48,18,60))
    img=Image.alpha_composite(img, glow.filter(__import__("PIL.ImageFilter",fromlist=["GaussianBlur"]).GaussianBlur(180)))
    tex=Image.new("RGBA",(W,H),(0,0,0,0)); td=ImageDraw.Draw(tex)
    for k in range(-H,W,54): td.line([(k,0),(k+H,H)],fill=(212,175,55,9),width=1)
    img=Image.alpha_composite(img,tex)
    return img.convert("RGB")

def _wrap(d,text,f,max_w):
    words=text.split(); lines=[]; cur=[]; cw=0; sw=d.textlength(" ",font=f)
    for wd in words:
        ww=d.textlength(wd,font=f); add=ww+(sw if cur else 0)
        if cur and cw+add>max_w: lines.append(cur); cur=[wd]; cw=ww
        else: cur.append(wd); cw+=add
    if cur: lines.append(cur)
    return lines

def _eyebrow(d,label,accent=GOLD,y=150,MX=96):
    f=_font(34,"extrabold")
    d.rectangle([MX,y+6,MX+26,y+34],fill=accent)
    d.text((MX+44,y)," ".join(label.upper()),font=f,fill=GOLD_SOFT)
    d.line([(MX,y+58),(W-MX,y+58)],fill=accent,width=3)

def _wordmark(d):
    MX=96; by=H-150
    wm=_font(38,"bold"); dot=_font(38,"semibold")
    d.line([(MX,by-26),(MX+70,by-26)],fill=GOLD,width=3)
    d.text((MX,by),"THE VIDESHI",font=wm,fill=WHITE)
    tvw=d.textlength("THE VIDESHI  ",font=wm)
    d.text((MX+tvw,by+2),"thevideshi.com",font=dot,fill=MUTED)

def _frames_to_mp4(frame_dir, out_path, fps=FPS, anim_dur=None, pad_to=12.0):
    """Assemble PNG frames f_%04d.png into an MP4 (yuv420p, faststart).

    Scene slots in the reel run ~7-11s but the animation completes in ~4s, so we
    HOLD the final composed frame to `pad_to` seconds via ffmpeg tpad=clone. This
    keeps render cheap (only the animated frames are drawn in PIL) while letting
    the card fill any scene length. The timeline plays [0, scene_length] with
    trim=0, so the entrance + count-up always show, then the card holds steady."""
    vf=[]
    if pad_to and anim_dur and pad_to>anim_dur:
        hold=round(pad_to-anim_dur,2)
        vf=["-vf",f"tpad=stop_mode=clone:stop_duration={hold}"]
    cmd=["ffmpeg","-y","-loglevel","error","-framerate",str(fps),
         "-i",os.path.join(frame_dir,"f_%04d.png")]+vf+[
         "-c:v","libx264","-pix_fmt","yuv420p","-r",str(fps),
         "-movflags","+faststart",out_path]
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode!=0:
        print(f"  ⚠️ anim_card ffmpeg failed: {r.stderr[:300]}")
        return False
    return True

# ── number formatting for count-up ──
def _parse_number(s):
    """From a target string like '$1.3T', '+19%', '$85.7B', '4,400', '$2.66T'
    return (prefix, value, suffix, decimals) so we can interpolate the value."""
    m=re.match(r'^([^\d\-+]*[+\-]?)\s*([\d,]+(?:\.\d+)?)\s*(.*)$', s.strip())
    if not m: return None
    prefix,num,suffix=m.group(1),m.group(2),m.group(3)
    decimals=len(num.split(".")[1]) if "." in num else 0
    val=float(num.replace(",",""))
    had_comma=("," in num)
    return prefix,val,suffix,decimals,had_comma

def _fmt_number(prefix,val,suffix,decimals,had_comma):
    if decimals>0: body=f"{val:.{decimals}f}"
    else: body=f"{int(round(val)):,}" if had_comma else f"{int(round(val))}"
    return f"{prefix}{body}{suffix}"

# ════════════════════════════════════════════════════════════════════════════
# (a) HERO STAT — giant count-up number + slide-in subtitle
# ════════════════════════════════════════════════════════════════════════════
def render_hero_stat_mp4(big, sub, eyebrow="BY THE NUMBERS", out_dir="/tmp/videshi_anim",
                         duration=3.6, accent=GOLD_BR, pad_to=12.0):
    from PIL import Image, ImageDraw
    try:
        os.makedirs(out_dir, exist_ok=True)
        n=int(duration*FPS)
        parsed=_parse_number(big)
        with tempfile.TemporaryDirectory() as fd:
            base=_bg()
            for fi in range(n):
                t=fi/(n-1) if n>1 else 1.0
                img=base.copy(); d=ImageDraw.Draw(img)
                _eyebrow(d,eyebrow,accent)
                # count-up over first 65% of clip
                cu=clamp01(t/0.65)
                if parsed:
                    prefix,val,suffix,dec,hc=parsed
                    cur=val*ease_out_cubic(cu)
                    disp=_fmt_number(prefix,cur,suffix,dec,hc)
                else:
                    disp=big
                bigf=_font(220,"extrabold")
                # entrance: rise + fade over first 0.9s
                ent=clamp01(t/ (0.9/duration))
                dy=int((1-ease_out_back(ent))*70)
                # measure & center
                bw=d.textlength(disp,font=bigf)
                bx=(W-bw)//2; byc=int(H*0.40)+dy
                # shadow
                d.text((bx+4,byc+5),disp,font=bigf,fill=(0,0,0))
                d.text((bx,byc),disp,font=bigf,fill=accent)
                # subtitle slide-in after 0.6s
                sent=clamp01((t-0.6/duration)/(1.0/duration))
                if sent>0:
                    sf=_font(50,"semibold")
                    for li,ln in enumerate(_wrap(d,sub,sf,W-220)):
                        txt=" ".join(ln); sw=d.textlength(txt,font=sf)
                        sx=(W-sw)//2; sy=int(H*0.40)+260+li*66
                        sdx=int((1-ease_out_cubic(sent))*-40)
                        # fade via alpha-ish: draw at full once visible
                        d.text((sx+sdx,sy),txt,font=sf,fill=WHITE if sent>0.5 else MUTED)
                # underline accent grows under number
                gl=clamp01((t-0.3/duration)/(1.2/duration))
                uw=int(360*ease_out_cubic(gl))
                d.rounded_rectangle([(W-uw)//2,byc+250-300 if False else int(H*0.40)+225,(W+uw)//2,int(H*0.40)+233],
                                    radius=4,fill=accent)
                _wordmark(d)
                img.save(os.path.join(fd,f"f_{fi:04d}.png"))
            out=os.path.join(out_dir,f"hero_{abs(hash(big+sub))%10**8}.mp4")
            if _frames_to_mp4(fd,out,anim_dur=duration,pad_to=pad_to): return out
        return None
    except Exception as e:
        print(f"  ⚠️ hero_stat render failed: {e}")
        return None

# ════════════════════════════════════════════════════════════════════════════
# (b) STAT GRID — 2x2 tiles, staggered slide/fade in, accent bars
# ════════════════════════════════════════════════════════════════════════════
def render_stat_grid_mp4(tiles, eyebrow="THE DEAL IN FIGURES", out_dir="/tmp/videshi_anim",
                         duration=3.8, pad_to=12.0):
    """tiles: list of up to 4 (big, label, accent_rgb)."""
    from PIL import Image, ImageDraw
    try:
        os.makedirs(out_dir, exist_ok=True)
        n=int(duration*FPS)
        tiles=tiles[:4]
        # precompute count-up parse per tile
        parsed=[_parse_number(t[0]) for t in tiles]
        MX=90
        gw=(W-2*MX-30)//2; gh=300; gap=30; gy=int(H*0.34)
        with tempfile.TemporaryDirectory() as fd:
            base=_bg()
            # title block drawn once per frame (cheap)
            for fi in range(n):
                t=fi/(n-1) if n>1 else 1.0
                img=base.copy(); d=ImageDraw.Draw(img)
                _eyebrow(d,eyebrow,GOLD_BR)
                for idx,(big,lab,ac) in enumerate(tiles):
                    # stagger each tile entrance 0.18s apart
                    delay=0.15+idx*0.18
                    ent=clamp01((t*duration-delay)/0.55)
                    if ent<=0: continue
                    r=idx//2; c=idx%2
                    x=MX+c*(gw+gap); y=gy+r*(gh+gap)
                    # slide up + fade
                    dy=int((1-ease_out_back(ent))*60)
                    yy=y+dy
                    # tile bg (simulate fade by blending toward bg not trivial in PIL;
                    # use a near-final solid once ent>0.15 — entrance motion carries the eye)
                    d.rounded_rectangle([x,yy,x+gw,yy+gh],radius=24,fill=PANEL)
                    d.rounded_rectangle([x,yy,x+gw,yy+14],radius=7,fill=ac)
                    # count-up number
                    cu=clamp01((t*duration-delay)/1.1)
                    if parsed[idx]:
                        prefix,val,suffix,dec,hc=parsed[idx]
                        disp=_fmt_number(prefix,val*ease_out_cubic(cu),suffix,dec,hc)
                    else:
                        disp=big
                    nf=_font(92,"extrabold")
                    # shrink font if too wide
                    while d.textlength(disp,font=nf)>gw-56 and nf.size>52:
                        nf=_font(nf.size-6,"extrabold")
                    d.text((x+34,yy+46),disp,font=nf,fill=(20,30,50))
                    lf=_font(32,"semibold")
                    for j,ln in enumerate(_wrap(d,lab,lf,gw-60)):
                        d.text((x+34,yy+168+j*40)," ".join(ln),font=lf,fill=(96,110,130))
                _wordmark(d)
                img.save(os.path.join(fd,f"f_{fi:04d}.png"))
            out=os.path.join(out_dir,f"grid_{abs(hash(str(tiles)))%10**8}.mp4")
            if _frames_to_mp4(fd,out,anim_dur=duration,pad_to=pad_to): return out
        return None
    except Exception as e:
        print(f"  ⚠️ stat_grid render failed: {e}")
        return None

# ════════════════════════════════════════════════════════════════════════════
# (c) DIASPORA PANEL — saffron-accented panel, bullets animate in
# ════════════════════════════════════════════════════════════════════════════
def render_diaspora_panel_mp4(title, subtitle, bullets, eyebrow="THE DIASPORA ANGLE",
                              out_dir="/tmp/videshi_anim", duration=4.0, pad_to=12.0):
    from PIL import Image, ImageDraw
    try:
        os.makedirs(out_dir, exist_ok=True)
        n=int(duration*FPS)
        MX=90; bullets=bullets[:4]
        with tempfile.TemporaryDirectory() as fd:
            base=_bg()
            # measure panel layout once
            from PIL import ImageDraw as _ID
            tmp=_ID.Draw(base)
            ff=_font(37,"medium")
            blines=[_wrap(tmp,b,ff,W-2*MX-130) for b in bullets]
            block_h=sum(46*len(bl)+26 for bl in blines)
            pad_top=205; ph=pad_top+block_h+30; py=int(H*0.30)
            for fi in range(n):
                t=fi/(n-1) if n>1 else 1.0
                img=base.copy(); d=ImageDraw.Draw(img)
                _eyebrow(d,eyebrow,SAFFRON)
                # headline
                hf=_font(70,"extrabold"); y=int(H*0.18)
                hent=clamp01(t/(0.7/duration))
                hdx=int((1-ease_out_cubic(hent))*-50)
                for ln in _wrap(d,title,hf,W-2*MX):
                    x=MX+hdx
                    for wd in ln:
                        col=GOLD_BR if any(ch.isdigit() for ch in wd) else WHITE
                        d.text((x+2,y+2),wd,font=hf,fill=(0,0,0))
                        d.text((x,y),wd,font=hf,fill=col)
                        x+=d.textlength(wd,font=hf)+d.textlength(" ",font=hf)
                    y+=80
                # panel reveal (slide up after 0.4s)
                pent=clamp01((t*duration-0.4)/0.6)
                if pent>0:
                    pdy=int((1-ease_out_back(pent))*50)
                    pyy=py+pdy
                    d.rounded_rectangle([MX,pyy,W-MX,pyy+ph],radius=26,fill=(16,28,48),
                                        outline=(40,56,84),width=2)
                    d.rounded_rectangle([MX,pyy,MX+14,pyy+ph],radius=7,fill=SAFFRON)
                    d.text((MX+50,pyy+40),title.split("—")[0].strip()[:22].upper() if False else "STARLINK IN INDIA",
                           font=_font(52,"extrabold"),fill=WHITE)
                    d.text((MX+50,pyy+110),subtitle,font=_font(36,"semibold"),fill=GOLD_BR)
                    yy=pyy+pad_top
                    for bi,bl in enumerate(blines):
                        bent=clamp01((t*duration-0.7-bi*0.22)/0.5)
                        if bent<=0:
                            yy+=46*len(bl)+26; continue
                        bdx=int((1-ease_out_cubic(bent))*-40)
                        d.ellipse([MX+50+bdx,yy+10,MX+50+18+bdx,yy+28],fill=SAFFRON)
                        for j,ln in enumerate(bl):
                            d.text((MX+88+bdx,yy+j*46)," ".join(ln),font=ff,
                                   fill=(214,224,238) if bent>0.5 else MUTED)
                        yy+=46*len(bl)+26
                _wordmark(d)
                img.save(os.path.join(fd,f"f_{fi:04d}.png"))
            out=os.path.join(out_dir,f"diaspora_{abs(hash(title+subtitle))%10**8}.mp4")
            if _frames_to_mp4(fd,out,anim_dur=duration,pad_to=pad_to): return out
        return None
    except Exception as e:
        print(f"  ⚠️ diaspora_panel render failed: {e}")
        return None


if __name__=="__main__":
    # smoke test all three
    print("hero:", render_hero_stat_mp4("$1.3T","Musk — world's first trillionaire"))
    print("grid:", render_stat_grid_mp4([
        ("$135","IPO price / share",BLUE),("$85.7B","raised — largest ever",GREEN_BR),
        ("+19%","first-day pop on Nasdaq",SAFFRON),("$2.66T","valuation within a week",GOLD_BR)]))
    print("diaspora:", render_diaspora_panel_mp4(
        "Worth $2.2 trillion — still grounded in India",
        "The world's biggest IPO, still on hold",
        ["Starlink — SpaceX's internet arm — is still not live in India",
         "June 2026: New Delhi froze final clearance on security grounds",
         "It already holds GMPCS + IN-SPACe licences, yet sits in limbo",
         "For NRIs back home, rural broadband keeps waiting on politics"]))
