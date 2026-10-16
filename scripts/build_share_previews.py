#!/usr/bin/env python3
"""Regenerate four social images and locale pages from the canonical index.html."""
import html
import re
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent.parent
BASE="https://vadym9083.github.io/gpt/"
D={
 "uk":dict(path="",html="uk",og="uk_UA",title="Таргет LB — Meta Ads для бізнесу | Vadym",desc="Реклама Facebook та Instagram для клінінгу й локального бізнесу. Реальні кейси, креативи та результати.",brand="ТАРГЕТ",hero="ДЛЯ БІЗНЕСУ",line="КЛІНІНГ  •  ЛОКАЛЬНИЙ БІЗНЕС",proof="РЕАЛЬНІ КЕЙСИ  •  РЕЗУЛЬТАТИ"),
 "ru":dict(path="ru/",html="ru",og="ru_RU",title="Таргет LB — Meta Ads для бизнеса | Vadym",desc="Реклама Facebook и Instagram для клининга и локального бизнеса. Реальные кейсы, креативы и результаты.",brand="ТАРГЕТ",hero="ДЛЯ БИЗНЕСА",line="КЛИНИНГ  •  ЛОКАЛЬНЫЙ БИЗНЕС",proof="РЕАЛЬНЫЕ КЕЙСЫ  •  РЕЗУЛЬТАТЫ"),
 "en":dict(path="en/",html="en",og="en_US",title="Target LB — Meta Ads for Local Businesses | Vadym",desc="Facebook and Instagram ads for cleaning companies and local businesses. Real case studies, ad creatives and results.",brand="TARGET",hero="FOR BUSINESS",line="CLEANING  •  LOCAL BUSINESSES",proof="REAL CASE STUDIES  •  RESULTS"),
 "es":dict(path="es/",html="es",og="es_ES",title="Target LB — Meta Ads para negocios | Vadym",desc="Publicidad en Facebook e Instagram para empresas de limpieza y negocios locales. Casos reales, anuncios y resultados.",brand="TARGET",hero="PARA NEGOCIOS",line="LIMPIEZA  •  NEGOCIOS LOCALES",proof="CASOS REALES  •  RESULTADOS"),
}
font_b="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font_r="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def make_image(code,x):
    im=ImageOps.fit(Image.open(ROOT/"assets/site/hero-marketing-workspace-20260929.webp").convert("RGB"),(1200,630),Image.Resampling.LANCZOS)
    veil=Image.new("RGBA",im.size,(0,0,0,0)); p=veil.load()
    for i in range(760):
        opacity=136 if i<545 else int(136*(760-i)/215)
        for j in range(630): p[i,j]=(5,9,15,opacity)
    im=Image.alpha_composite(im.convert("RGBA"),veil)
    d=ImageDraw.Draw(im,"RGBA")
    ivory=(244,242,238,255); gold=(217,181,128,255); muted=(211,213,212,255)
    def text(px,py,value,sz,maxw,color,bold=True):
        f=ImageFont.truetype(font_b if bold else font_r,sz)
        while d.textbbox((0,0),value,font=f)[2]>maxw and sz>14:
            sz-=1;f=ImageFont.truetype(font_b if bold else font_r,sz)
        d.text((px,py),value,font=f,fill=color)
    text(76,64,x["brand"],31,230,ivory);text(275,64,"LB",31,100,gold)
    text(77,124,"VADYM   /   PERFORMANCE MARKETER",16,485,muted,False)
    d.rounded_rectangle((77,175,146,179),radius=2,fill=gold)
    text(70,215,"META ADS",80,535,ivory)
    text(73,328,x["hero"],52,540,ivory)
    text(78,424,x["line"],19,530,gold,False)
    d.rounded_rectangle((70,514,576,581),radius=13,fill=(13,20,30,226),outline=(216,180,125,100),width=2)
    text(91,530,x["proof"],21,466,ivory)
    fn=f"og-target-lb-{code}-20261017.jpg"; dest=ROOT/"assets/site"/fn
    im.convert("RGB").save(dest,format="JPEG",quality=89,optimize=True,progressive=True,subsampling=0)
    assert Image.open(dest).size==(1200,630) and dest.stat().st_size<450000
    print("IMAGE",code,dest.stat().st_size)
    return BASE+"assets/site/"+fn

source=(ROOT/"index.html").read_text(encoding="utf8")
assert source==(ROOT/"cleaning-canada.html").read_text(encoding="utf8")
assert 'applyLanguage(requestedLang==="ru"?"ru":"uk",true);' in source
assert source.count('function applyLanguage(lang,force=false)')==1
assert "https://lively-elf-ba1204.netlify.app/.netlify/functions/lead" in source
# Shared resources must resolve identically at /gpt/ and /gpt/{locale}/
source=source.replace('"assets/','"/gpt/assets/').replace("'assets/","'/gpt/assets/")
helper='''  const languagePaths={uk:"/gpt/",ru:"/gpt/ru/",en:"/gpt/en/",es:"/gpt/es/"};
  function syncLanguageUrl(lang){
    const next=new URL(window.location.href);
    next.pathname=languagePaths[lang]||languagePaths.uk;
    next.searchParams.delete("lang");
    const locationString=next.pathname+next.search+next.hash;
    if(locationString!==location.pathname+location.search+location.hash)
      history.replaceState(history.state,"",locationString);
  }

'''
source=source.replace('  function applyLanguage(lang,force=false){',helper+'  function applyLanguage(lang,force=false){',1)
source=source.replace(
  '    updateSwitcherUi(lang);\n    document.dispatchEvent(new CustomEvent("siteLanguageChanged",{detail:{lang}}));',
  '    updateSwitcherUi(lang);\n    syncLanguageUrl(lang);\n    document.dispatchEvent(new CustomEvent("siteLanguageChanged",{detail:{lang}}));',1)
source=source.replace(
  '  applyLanguage(requestedLang==="ru"?"ru":"uk",true);',
  '''  const routeMatch=window.location.pathname.match(/^\\/gpt\\/(uk|ru|en|es)\\/(?:index\\.html)?$/);
  const initialLang=requestedLang&&langCode[requestedLang]?requestedLang:(routeMatch?routeMatch[1]:"uk");
  applyLanguage(initialLang,true);''',1)
assert source.count("syncLanguageUrl(lang);")==1
og_regex=r'<meta property="og:type" content="website">.*?<meta name="twitter:image" content="[^"]+">'
alternate_regex=r'<link rel="alternate" hreflang="uk" href="[^"]+">\s*<link rel="alternate" hreflang="x-default" href="[^"]+">'
assert re.search(og_regex,source,re.S) and re.search(alternate_regex,source)
bs=[]
for code,x in D.items():
    pic=make_image(code,x)
    url=BASE+x["path"]
    esc=lambda v:html.escape(v,quote=True)
    alts="\n".join('<link rel="alternate" hreflang="%s" href="%s">'%(lang,BASE+item["path"]) for lang,item in D.items())
    alts+='\n<link rel="alternate" hreflang="x-default" href="'+BASE+'">'
    tags="\n".join([
      '<meta property="og:type" content="website">',
      '<meta property="og:url" content="'+url+'">',
      '<meta property="og:site_name" content="Target LB">',
      '<meta property="og:title" content="'+esc(x["title"])+'">',
      '<meta property="og:description" content="'+esc(x["desc"])+'">',
      '<meta property="og:image" content="'+pic+'">',
      '<meta property="og:image:type" content="image/jpeg">',
      '<meta property="og:image:width" content="1200">',
      '<meta property="og:image:height" content="630">',
      '<meta property="og:image:alt" content="'+esc(x["title"])+'">',
      '<meta property="og:locale" content="'+x["og"]+'">',
      *['<meta property="og:locale:alternate" content="'+v["og"]+'">' for l,v in D.items() if l!=code],
      '<meta name="twitter:card" content="summary_large_image">',
      '<meta name="twitter:title" content="'+esc(x["title"])+'">',
      '<meta name="twitter:description" content="'+esc(x["desc"])+'">',
      '<meta name="twitter:image" content="'+pic+'">'
    ])
    page=source.replace('<html lang="uk">','<html lang="'+x["html"]+'">',1)
    page=re.sub(r'<title>[^<]*</title>','<title>'+esc(x["title"])+'</title>',page,count=1)
    page=re.sub(r'<meta name="description" content="[^"]+">','<meta name="description" content="'+esc(x["desc"])+'">',page,count=1)
    page=re.sub(r'<link rel="canonical" href="[^"]+">','<link rel="canonical" href="'+url+'">',page,count=1)
    page,n=re.subn(alternate_regex,lambda _:alts,page,count=1);assert n==1
    page,n=re.subn(og_regex,lambda _:tags,page,count=1,flags=re.S);assert n==1
    assert page.count('<meta property="og:image"')==1
    assert '<meta property="og:locale" content="'+x["og"]+'">' in page
    assert "src=\"assets/" not in page
    file=ROOT/x["path"]/"index.html"
    file.parent.mkdir(exist_ok=True,parents=True)
    file.write_text(page,encoding="utf8")
    if code=="uk":(ROOT/"cleaning-canada.html").write_text(page,encoding="utf8")
    bs.append(page.split('</head>',1)[1])
    print("HTML",code,url,len(page))
assert len(set(bs))==1,"Language pages have differing body and scripts"
assert (ROOT/"index.html").read_bytes()==(ROOT/"cleaning-canada.html").read_bytes()
print("FOUR_LOCALIZED_OG_PAGES=PASS")
