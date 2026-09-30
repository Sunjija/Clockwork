"""V5: single concept references -> explicit native pixel edits -> timed exposures.
Never samples a generated animation strip. Original 67/52/187 frames are read only.
"""
from pathlib import Path
import json, io, base64, shutil, hashlib, urllib.request
from PIL import Image, ImageDraw, ImageFont
R=Path(__file__).resolve().parents[2]; P=R/'unity/TiqueReturnPrototype'
A=R/'art/return-v5-feedback'; O=P/'Assets/Resources/ReturnV2/Feedback'
O.mkdir(parents=True,exist_ok=True); (A/'Source/Font').mkdir(parents=True,exist_ok=True)
colors={'ink':'#101921','steel':'#567482','dim':'#293943','gold':'#b58b46','light':'#ffcf7a','cyan':'#51e0df','white':'#eaffed','red':'#f47846','dust':'#887d68'}
clips=[]; audit=[]
def export(name,frames,times):
    folder=A/'Clips'/name; folder.mkdir(parents=True,exist_ok=True); dest=O/name;dest.mkdir(exist_ok=True)
    w,h=frames[0].size; sheet=Image.new('RGBA',(w*len(frames),h)); baseline=frames[0]
    for i,im in enumerate(frames):
        assert set(im.getchannel('A').getdata())<={0,255}
        im.save(folder/f'{i:02}.png'); shutil.copyfile(folder/f'{i:02}.png',dest/f'{i:02}.png');sheet.alpha_composite(im,(i*w,0))
        delta=[[x,y,*im.getpixel((x,y))] for y in range(h) for x in range(w) if im.getpixel((x,y))!=baseline.getpixel((x,y))]
        (folder/f'{i:02}.pixels.json').write_text(json.dumps(delta,separators=(',',':')))
        audit.append({'clip':name,'frame':i,'pixels':len(delta),'sha256':hashlib.sha256(im.tobytes()).hexdigest()})
    sheet.save(folder/'sheet.png')
    if len(frames)>1: frames[0].save(folder/'native.apng',save_all=True,append_images=frames[1:],duration=times,loop=0,disposal=0,blend=0)
    b=io.BytesIO();sheet.save(b,format='PNG');layer={'name':name,'opacity':1,'frameCount':len(frames),'chunks':[{'layout':[[i] for i in range(len(frames))],'base64PNG':'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()}]}
    (folder/(name+'.piskel')).write_text(json.dumps({'modelVersion':2,'piskel':{'name':name,'description':'Native pixel patches; variable timing in clips.json and APNG.','fps':20,'width':w,'height':h,'layers':[json.dumps(layer)]}}))
    clips.append({'name':name,'durations':times,'width':w,'height':h})
def canvas(w,h):
    im=Image.new('RGBA',(w,h));return im,ImageDraw.Draw(im)
# All new silhouettes start as converted SINGLE design images. This stage only
# edits native pixels/exposures; it never draws a substitute from polygons.
N=A/'Source/Native'; derivations={}
def native(name):return Image.open(N/(name+'.png')).convert('RGBA')
def expose(name,source,count,timing,ground=False):
    key=native(source);w,h=key.size;frames=[];cx=w//2;cy=h-3 if ground else h//2
    for f in range(count):
        im=Image.new('RGBA',(w,h))
        # Explicit integer radial spacing and particle deletion on the key image.
        # Ground pixels rise/spread; sparks expand/disperse. No alpha tween.
        for y in range(h):
            for x in range(w):
                c=key.getpixel((x,y))
                if not c[3]:continue
                if f>=count-2 and (x*3+y*5)%count<f:continue
                dx=-1 if x<cx else 1 if x>cx else 0
                dy=-1 if y<cy else 1 if y>cy else 0
                xx=x+dx*(f//2);yy=y-(f//2) if ground else y+dy*(f//2)
                if 0<=xx<w and 0<=yy<h:
                    if f==0 and max(c[:3])>170:c=(234,255,246,255)
                    im.putpixel((xx,yy),c)
        frames.append(im)
    derivations[name]=source;export(name,frames,timing)
for name,source,count,ms in [('hit','hit',5,[25,30,35,40,40]),('hurt','hurt',4,[30,40,45,55]),('armor','armor',3,[40,45,55]),('air','air',3,[30,40,40]),('boost','boost',4,[35,40,45,50]),('pylon-impact','hit',5,[20,25,30,35,40])]:
    if name=='pylon-impact':
        key=native('hit');key.putdata([(239,183,88,255) if a and g>r else (r,g,b,a) for r,g,b,a in key.getdata()]);key.save(N/'pylon-impact.png');source='pylon-impact'
    expose(name,source,count,ms)
for name,source,n in [('dust','dust',5),('slam-dust','slam-dust',6),('friction','dust',4),('wall-brake','dust',4)]:
    expose(name,source,n,[40]*n,ground=True)
for name in ['protect','heart-full','heart-empty','iron-full','iron-empty','panel','button','button-selected','button-pressed','button-disabled']:
    im=native(name)
    if name=='panel' or name.startswith('button'):
        # Repair the 9x9 slice on the converted metal design. Samples come from
        # its color palette, with 1px borders so resizing cannot blur corners.
        dark=(35,35,39,255);metal=(121,83,51,255);light=(239,183,88,255)
        if name=='panel':metal=(86,116,130,255);light=(121,143,153,255)
        if name=='button-selected':metal=(25,193,209,255);light=(167,249,241,255)
        if name=='button-pressed':metal=(239,183,88,255);light=(255,241,197,255)
        if name=='button-disabled':metal=(60,76,87,255);light=(86,116,130,255)
        # Native pixel cleanup of a sampled base, recorded in the patch file.
        for y in range(9):
            for x in range(9):
                if 1<=x<=7 and 1<=y<=7:im.putpixel((x,y),dark)
                if (y in (1,7) and 2<=x<=6) or (x in (1,7) and 2<=y<=6):im.putpixel((x,y),metal)
        for x,y in [(2,2),(6,2),(2,6),(6,6)]:im.putpixel((x,y),light)
        for x,y in [(0,0),(8,0),(0,8),(8,8)]:im.putpixel((x,y),(0,0,0,0))
    derivations[name]=name;export(name,[im],[1000])
for name,src in [('heart-ghost','heart-empty'),('iron-ghost','iron-empty')]:
    im=native(src);im.putdata([(86,116,130,255) if a else (0,0,0,0) for r,g,b,a in im.getdata()]);derivations[name]=src;export(name,[im],[1000])
for kind in ['full','empty','ghost']:
    src='iron-full' if kind=='full' else 'iron-empty'
    im=native(src).resize((8,10),Image.Resampling.NEAREST)
    im.putdata([(81,224,223,255) if a and r>g*1.2 and kind=='full' else (86,116,130,255) if a and kind=='ghost' else (r,g,b,a) for r,g,b,a in im.getdata()])
    derivations['tique-cell-'+kind]=src;export('tique-cell-'+kind,[im],[1000])
for n in ['undo','reset','hint','locked','circuit','jump','dash','attack','interact','pause']:
    derivations['icon-'+n]='icon-'+n;export('icon-'+n,[native('icon-'+n)],[1000])
derivations['chute']='chute';export('chute',[native('chute')],[1000])
base=Image.open(P/'Assets/Resources/Return/Tique/Idle/00.png').convert('RGBA')
# Eyes only: edit cyan eye interior, preserve head outline/body/feet exactly.
for n,height in [('blink-half',2),('blink-closed',1)]:
    im=base.copy()
    for x0,x1,y0,y1 in [(28,33,18,26),(40,44,19,27)]:
        for y in range(y0,y1+1):
            for x in range(x0,x1+1):
                r,g,b,a=base.getpixel((x,y))
                if a and b>r*1.25 and g>r*1.25:im.putpixel((x,y),(16,40,46,255) if abs(y-(y0+y1)//2)>=height else (81,224,223,255))
    export(n,[im],[1000])
# Single generated key-pose image -> native palette correction was reviewed first.
# Animation exposures are authored from approved Walk PNGs, with only arm patches.
walk=json.loads((P/'Assets/Resources/Return/clips.json').read_text(encoding='utf-8'))['clips']
walktimes=next(c['durations'] for c in walk if c['name']=='Walk')
def heart_center(im):
    pts=[(x,y) for y in range(34,47) for x in range(26,44) if (lambda c:c[3] and c[1]>c[0]*1.4 and c[2]>c[0]*1.4)(im.getpixel((x,y)))]
    return (round(sum(x for x,y in pts)/len(pts)),round(sum(y for x,y in pts)/len(pts)))
bx,by=heart_center(base)
for n in ['push-side','push-up','push-down','hurt-pose']:
    pose=Image.open(A/f'Source/Native/{n}-v3.png').convert('RGBA')
    regions=[(16,34,55,48)]
    frames=[]
    for f in range(3 if n=='hurt-pose' else 14):
        im=base.copy() if n=='hurt-pose' else Image.open(P/f'Assets/Resources/Return/Tique/Walk/{f:02}.png').convert('RGBA')
        cx,cy=heart_center(im);dx,dy=cx-bx,cy-by
        for x0,y0,x1,y1 in regions:
            # Exact pixel patch, same native grid, no skeleton or interpolated rotation.
            for y in range(y0,y1):
                for x in range(x0,x1):
                    xx,yy=x+dx,y+dy
                    if 0<=xx<64 and 0<=yy<48:
                        # Original heart and torso interior stay locked except
                        # where the two arms explicitly occlude the shoulders.
                        arm=x<25 or x>=43 or y<=38 or n=='push-down' and y>=43
                        c=im.getpixel((xx,yy));cyan=c[3] and c[1]>c[0]*1.4 and c[2]>c[0]*1.4
                        if arm and not cyan:im.putpixel((xx,yy),pose.getpixel((x,y)))
        # Return to the unchanged approved base on the final hurt exposure.
        if n=='hurt-pose' and f==2:im=base.copy()
        frames.append(im)
    export(n,frames,[40,50,60] if n=='hurt-pose' else walktimes)
for direction in ['side','up','down']:
    name='push-brace-'+direction;im=native('push-'+direction+'-v3')
    derivations[name]='push-'+direction+'-v3';export(name,[im],[1000])
power=[]
for f in range(3):
    im=base.copy()
    for y in range(10,46):
        for x in range(24,46):
            r,g,b,a=base.getpixel((x,y))
            if a and b>r*1.25 and g>r*1.25:
                im.putpixel((x,y),[(38,126,139,255),(26,69,82,255),(18,41,51,255)][f])
    power.append(im)
export('power-down',power,[80,100,120])
off=Image.open(P/'Assets/Resources/ReturnV2/WardenAuthored/idle/00.png').convert('RGBA')
boot=[]
for f in range(4):
    im=off.copy()
    for y in range(im.height):
        for x in range(im.width):
            r,g,b,a=off.getpixel((x,y))
            if a and r>g*1.4 and r>b*1.4 and (f==0 or f<3 and y>45+f*24):im.putpixel((x,y),(40,43,46,255))
    boot.append(im)
export('warden-boot',boot,[600]*4)
shut=[];down=Image.open(P/'Assets/Resources/ReturnV2/WardenAuthored/stagger/06.png').convert('RGBA')
for f in range(4):
    im=down.copy()
    for y in range(im.height):
        for x in range(im.width):
            r,g,b,a=down.getpixel((x,y))
            if a and r>g*1.4 and r>b*1.4 and y>f*34:im.putpixel((x,y),(40,43,46,255))
    shut.append(im)
export('warden-shutdown',list(reversed(shut)),[60]*4)
expose('bridge','bridge',3,[30,35,35])
expose('orb-stop','orb-stop',3,[40,45,55])
expose('orb-release','orb-stop',3,[40,45,55])
expose('weight-settle','dust',3,[40,45,55],ground=True)
# Derivative solid silhouettes for ghost/protection: no fractional alpha.
for clip in ['Dash']:
    times=json.loads((P/'Assets/Resources/Return/clips.json').read_text())['clips'];timing=next(c['durations'] for c in times if c['name']==clip)
    frames=[]
    for f in range(len(timing)):
        im=Image.open(P/f'Assets/Resources/Return/Tique/{clip}/{f:02}.png').convert('RGBA');im.putdata([(41,92,101,255) if a else (0,0,0,0) for r,g,b,a in im.getdata()]);frames.append(im)
    export('dash-ghost',frames,timing)
# One provenance chain for every output, including reused approved PNGs.
for n in ['blink-half','blink-closed','power-down']:derivations[n]='approved Tique Idle image / eye or core palette pixel edit'
for n in ['push-side','push-up','push-down','hurt-pose']:derivations[n]='single '+n+' reference / native '+n+'-v3 + approved Walk feet'
for n in ['warden-boot','warden-shutdown']:derivations[n]='approved WardenAuthored single pose / existing image-first source'
derivations['dash-ghost']='approved Dash PNGs / binary palette silhouette'
(A/'clip-source-map.json').write_text(json.dumps(derivations,indent=2),encoding='utf-8')
assert set(derivations)=={c['name'] for c in clips}
(O/'clips.json').write_text(json.dumps({'clips':clips},indent=2));(A/'clips.json').write_text(json.dumps({'clips':clips},indent=2));(A/'pixel-audit.json').write_text(json.dumps(audit,indent=2))
# Official freely redistributable SIL OFL pixel Hangul font, baked to a binary atlas.
fontpath=A/'Source/Font/neodgm.ttf';licensepath=A/'Source/Font/LICENSE.txt'
if not fontpath.exists():fontpath.write_bytes(urllib.request.urlopen('https://github.com/neodgm/neodgm/releases/download/v1.601/neodgm.ttf').read())
if not licensepath.exists():licensepath.write_bytes(urllib.request.urlopen('https://raw.githubusercontent.com/neodgm/neodgm/main/LICENSE.txt').read())
font=ImageFont.truetype(str(fontpath),16)
corpus=''.join(p.read_text(encoding='utf-8-sig') for p in (P/'Assets/Scripts').glob('*.cs'))+''.join(chr(c) for c in range(32,127))+'↑↓←→◆●…·'
chars=''.join(sorted(set(c for c in corpus if not c.isspace() or c==' ')))
# Check cmap instead of silently rendering replacement glyphs.
from fontTools.ttLib import TTFont
cmap=TTFont(str(fontpath)).getBestCmap();custom={'←','↑','→','↓'};missing=[c for c in chars if ord(c) not in cmap and ord(c)>127 and c not in custom]
assert not missing,repr(missing)
cols=32;atlas=Image.new('RGBA',(cols*16,((len(chars)+cols-1)//cols)*16))
for i,c in enumerate(chars):
    glyph=Image.new('L',(16,16));gd=ImageDraw.Draw(glyph)
    if c in custom:
        if c in {'←','→'}:
            gd.line((2,8,13,8),fill=255);end=2 if c=='←' else 13;sign=1 if c=='←' else -1;gd.line((end+4*sign,4,end,8,end+4*sign,12),fill=255)
        else:
            gd.line((8,2,8,13),fill=255);end=2 if c=='↑' else 13;sign=1 if c=='↑' else -1;gd.line((4,end+4*sign,8,end,12,end+4*sign),fill=255)
    else:gd.text((0,0),c,font=font,fill=255,stroke_width=0)
    mask=glyph.point(lambda p:255 if p>=128 else 0);tile=Image.new('RGBA',(16,16),'white');tile.putalpha(mask);atlas.alpha_composite(tile,(i%cols*16,i//cols*16))
atlas.save(O/'font.png');(O/'font.json').write_text(json.dumps({'characters':chars,'columns':cols,'cell':16},ensure_ascii=False),encoding='utf-8')
shutil.copyfile(licensepath,O/'FONT-LICENSE.txt')
(A/'Source/Font/provenance.json').write_text(json.dumps({'family':'NeoDunggeunmo','version':'1.601','license':'SIL OFL 1.1','url':'https://github.com/neodgm/neodgm/releases/tag/v1.601','sha256':hashlib.sha256(fontpath.read_bytes()).hexdigest(),'glyphCount':len(chars),'missingGlyphs':missing},indent=2))
contact=Image.new('RGBA',(640,320),(12,22,30,255));x=y=0
for c in clips:
    im=Image.open(O/c['name']/'00.png');w,h=im.size
    if x+w+8>640:x=0;y+=80
    contact.alpha_composite(im,(x,y));x+=max(28,w)+8
contact.save(A/'contact.png');print('PASS',len(clips),'clips,',sum(len(c['durations']) for c in clips),'native frames;',len(chars),'font glyphs')
