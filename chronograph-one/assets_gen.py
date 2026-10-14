#!/usr/bin/env python3
"""Generate offline resource-only premium chronograph assets for Wear OS WFF."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
from math import cos,sin,pi
import random
random.seed(23)
D=Path("watchface/src/main/res/drawable-nodpi"); D.mkdir(parents=True,exist_ok=True)
S=2; W=H=450
def sc(v): return round(v*S)
def rect(b): return tuple(sc(z) for z in b)
def font(n,b=False):
    a="/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf"
    return ImageFont.truetype(a,sc(n))
def ellipse(draw,b,fill=None,outline=None,width=1):
    draw.ellipse(rect(b),fill=fill,outline=outline,width=sc(width))
im=Image.new("RGBA",(sc(W),sc(H)),(0,0,0,255)); d=ImageDraw.Draw(im)
# Polished graphite bezel, dark radial brushing, polished rim
for r in range(225,179,-1):
    k=225-r; c=19+int(0.6*k)+int(6*sin(k*.33))
    ellipse(d,(225-r,225-r,225+r,225+r),fill=(c,c+1,c+3,255))
for r,w,c in [(221,3,(140,147,150)),(216,2,(18,22,24)),(208,3,(68,74,77)),(199,2,(122,125,124)),(194,2,(20,22,24)),(184,2,(106,111,112))]:
    ellipse(d,(225-r,225-r,225+r,225+r),outline=(*c,255),width=w)
# Fine scale marks: dark enamel / platinum insets
for i in range(120):
    a=(i/120)*2*pi-pi/2
    inn=205 if i%5==0 else 211
    out=217 if i%5==0 else 215
    d.line((sc(225+inn*cos(a)),sc(225+inn*sin(a)),sc(225+out*cos(a)),sc(225+out*sin(a))),
           fill=(201,206,209,230) if i%5==0 else (77,82,84,210),width=sc(1.7 if i%5==0 else .8))
# Main brushed-steel dial surface, fine radial machine texture
ellipse(d,(47,47,403,403),fill=(33,36,38,255),outline=(149,154,157,255),width=2)
for r in range(177,51,-3):
    base=34+round((r-52)*.075)
    ellipse(d,(225-r,225-r,225+r,225+r),outline=(base,base+2,base+4,255),width=.65)
ellipse(d,(59,59,391,391),fill=(20,22,24,255))
# LCD
d.rounded_rectangle(rect((110,86,340,181)),radius=sc(34),fill=(4,6,9,255),outline=(108,119,125,255),width=sc(2))
d.rounded_rectangle(rect((114,90,336,177)),radius=sc(30),outline=(52,60,64,255),width=sc(1))
d.line((sc(128),sc(132),sc(322),sc(132)),fill=(88,99,105,180),width=sc(1))
d.text((sc(296),sc(154)),"BPM",font=font(8),fill=(153,160,164,255),anchor="mm")
d.text((sc(117),sc(154)),"°C",font=font(8),fill=(150,158,163,255),anchor="mm")
# Three raised subdials with black inner enamel and concentric grooves
for x,y,r,label in [(128,265,68,"STEPS"),(322,265,68,"KCAL"),(225,352,61,"BATTERY")]:
    for radius,c,sw in [(r+4,(163,168,170,255),2),(r+2,(57,65,70,255),1.6),(r,(8,10,13,255),2),(r-5,(76,81,84,255),1.5),(r-9,(13,16,18,255),1)]:
        ellipse(d,(x-radius,y-radius,x+radius,y+radius),outline=c,width=sw)
    ellipse(d,(x-r+11,y-r+11,x+r-11,y+r-11),fill=(9,11,14,255))
    for ir in range(15):
        rr=r-16-ir*1.5
        ellipse(d,(x-rr,y-rr,x+rr,y+rr),outline=(20+ir//2,23+ir//2,25+ir//2,255),width=.5)
    for j in range(12):
        a=j*pi/6-pi/2
        inn=r-15 if j%3 else r-18
        out=r-10
        d.line((sc(x+inn*cos(a)),sc(y+inn*sin(a)),sc(x+out*cos(a)),sc(y+out*sin(a))),
          fill=(130,135,138,255),width=sc(1.1 if j%3 else 1.8))
    ly=y+25 if y<300 else y+26
    d.text((sc(x),sc(ly)),label,font=font(10),fill=(207,210,210,255),anchor="mm")
# Month and date pods
for coords in [(66,320,156,374),(294,320,384,374)]:
    d.rounded_rectangle(rect(coords),radius=sc(16),fill=(6,8,12,255),outline=(104,110,114,255),width=sc(2))
d.text((sc(106),sc(356)),"MONTH",font=font(9),fill=(157,167,173,255),anchor="mm")
d.text((sc(336),sc(356)),"DATE",font=font(9),fill=(157,167,173,255),anchor="mm")
# Screw details: only a little engineered texture
for x,y in [(80,184),(371,184),(162,326),(289,326)]:
    ellipse(d,(x-5,y-5,x+5,y+5),fill=(80,83,85,255),outline=(175,179,181,255))
    d.line((sc(x-3),sc(y+2),sc(x+3),sc(y-2)),fill=(13,17,20,255),width=sc(1.5))
# Accent layer, purely tintable in WFF
ac=Image.new("RGBA",im.size,(255,255,255,0)); a=ImageDraw.Draw(ac)
def arc(box,start,end,width=2,fill=(255,255,255,210)):
    a.arc(rect(box),start,end,fill=fill,width=sc(width))
for r in [188,178]:
    arc((225-r,225-r,225+r,225+r),194,346,1.6)
    arc((225-r,225-r,225+r,225+r),15,163,1.6)
for x,y,r in [(128,265,70),(322,265,70),(225,352,63)]:
    arc((x-r,y-r,x+r,y+r),195,350,2)
    for j in range(7):
        aa=(-155+j*20)*pi/180
        rr=r-6
        xx=x+rr*cos(aa); yy=y+rr*sin(aa)
        ellipse(a,(xx-1.4,yy-1.4,xx+1.4,yy+1.4),fill=(255,255,255,200))
a.rounded_rectangle(rect((111,87,339,180)),radius=sc(35),outline=(255,255,255,165),width=sc(2))
a.rounded_rectangle(rect((69,323,153,371)),radius=sc(15),outline=(255,255,255,170),width=sc(1))
a.rounded_rectangle(rect((297,323,381,371)),radius=sc(15),outline=(255,255,255,170),width=sc(1))
# 12 bright ceramic indices
for i in range(12):
    angle=2*pi*i/12-pi/2
    cx,cy=225+190*cos(angle),225+190*sin(angle)
    a.line((sc(cx),sc(cy),sc(cx+7*cos(angle)),sc(cy+7*sin(angle))),fill=(255,255,255,220),width=sc(4))
# Hour/minute metallic hands as elongated glyphs, separate resources for rotation
def make_hand(w,h,out):
    hand=Image.new("RGBA",(sc(w),sc(h)),(0,0,0,0))
    g=ImageDraw.Draw(hand)
    pts=[(w*.5,0),(w*.84,11),(w*.72,h*.79),(w*.6,h*.88),(w*.5,h*.92),(w*.4,h*.88),(w*.28,h*.79),(w*.16,11)]
    pts=[(sc(x),sc(y)) for x,y in pts]
    g.polygon(pts,fill=(165,175,180,255))
    g.line(pts+[pts[0]],fill=(240,242,239,255),width=sc(1.2),joint="curve")
    g.polygon([(sc(w*.49),sc(15)),(sc(w*.58),sc(22)),(sc(w*.55),sc(h*.73)),(sc(w*.45),sc(h*.73)),(sc(w*.42),sc(22))],fill=(229,245,237,255))
    hand.save(D/out)
make_hand(30,138,"hour.png");make_hand(24,176,"minute.png")
im.convert("RGB").save(D/"background.webp","WEBP",quality=86,method=6)
ac.save(D/"accent.png")
# Representative preview of the design, not used for live values
prev=Image.alpha_composite(im,Image.new("RGBA",im.size,(0,0,0,0)))
prev=Image.alpha_composite(prev,Image.blend(Image.new("RGBA",ac.size,(31,196,171,0)),ac,0.72))
p=ImageDraw.Draw(prev)
p.text((sc(225),sc(112)),"10:10",font=font(33,True),fill=(245,246,242),anchor="mm")
p.text((sc(128),sc(256)),"10 000",font=font(17,True),fill=(235,235,230),anchor="mm")
p.text((sc(322),sc(256)),"450",font=font(21,True),fill=(235,235,230),anchor="mm")
p.text((sc(225),sc(345)),"82%",font=font(22,True),fill=(235,235,230),anchor="mm")
p.text((sc(106),sc(342)),"OCT",font=font(14,True),fill=(235,235,230),anchor="mm")
p.text((sc(336),sc(342)),"14",font=font(14,True),fill=(235,235,230),anchor="mm")
p.text((sc(225),sc(150)),"23°C         ♥ 71",font=font(13),fill=(210,217,216),anchor="mm")
prev.convert("RGB").save(D/"preview.png",optimize=True)
print("Generated",[(p.name,p.stat().st_size) for p in D.iterdir()])
