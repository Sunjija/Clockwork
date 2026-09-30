"""State art: generated key-state references -> locked native bases -> pixel edits.

User explicitly requested pixel-authored state/transition frames. New core and
door bases are converted once from individual concepts. Existing prop geometry
is reused. No AI strips, optical flow, smooth transforms or runtime tint states.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import json,io,base64,hashlib,shutil

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'art/return-v4-states'
OLD=REPO/'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2/Art'
OUT=OLD.parent/'StateArt'
TIQUE=json.loads((REPO/'prototypes/tique-playground/Revisions/10/data.json').read_text(encoding='utf-8'))['clips']
NAMES=['battery','orb','amber-socket','cyan-socket','pylon','gear']
BASE={n:Image.open(OLD/f'{n}.png').convert('RGBA') for n in NAMES}
INK=(13,23,30,255);DARK=(30,58,66,255);CYAN=(81,226,221,255);WHITE=(223,249,228,255)
GOLD=(246,186,66,255);RED=(236,74,48,255);BRASS=(129,92,42,255);STEEL=(82,107,116,255)
PAL=sorted({p[:3] for im in BASE.values() for p in im.getdata() if p[3]}|{c[:3] for c in [INK,DARK,CYAN,WHITE,GOLD,RED,BRASS,STEEL]}|{(0,0,0)})
PALETTE=Image.new('P',(1,1));flat=[v for c in PAL for v in c];PALETTE.putpalette(flat+[0]*(768-len(flat)))
CLIPS=[];AUDIT=[]

def quant(im):
    a=im.getchannel('A').point(lambda p:255 if p>=128 else 0)
    im=im.convert('RGB').quantize(palette=PALETTE,dither=Image.Dither.NONE).convert('RGBA');im.putalpha(a)
    # Canonical transparent bytes simplify exact edit replay.
    im.putdata([p if p[3] else (0,0,0,0) for p in im.getdata()]);return im

def native_concept(name,size,visible,center=False):
    im=Image.open(ROOT/f'Source/Concepts/{name}.png').convert('RGBA')
    im.putalpha(im.getchannel('A').point(lambda p:255 if p>=128 else 0));im=im.crop(im.getbbox())
    scale=min(visible[0]/im.width,visible[1]/im.height)
    im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.BOX)
    out=Image.new('RGBA',size);out.alpha_composite(quant(im),((size[0]-im.width)//2,(size[1]-im.height)//2 if center else size[1]-im.height));return out

def dim_region(im,box,kind):
    im=im.copy();p=im.load()
    for y in range(box[1],box[3]):
        for x in range(box[0],box[2]):
            r,g,b,a=p[x,y]
            energy=(g>r*1.15 and b>r*1.15) if kind=='cyan' else (r>g*1.18 and g>b*1.35)
            if a and energy:p[x,y]=(round(r*.38),round(g*.40),round(b*.50),255)
    return im

def socket(kind,level=0,wrong=False):
    original=BASE[kind+'-socket'];glow=GOLD if kind=='amber' else CYAN
    im=original.copy() if level>=4 else dim_region(original,(7,7,29,29),'cyan' if kind=='cyan' else 'amber');d=ImageDraw.Draw(im)
    if level:
        # Connected tracks remain visible around a 30x32 box on a 36x36 plate.
        for n,pts in enumerate([[(3,13),(3,3),(13,3)],[(23,3),(32,3),(32,13)],[(32,23),(32,32),(23,32)],[(13,32),(3,32),(3,23)]]):
            d.line(pts,fill=glow if n<level else DARK,width=2)
        if level>=4:
            for x,y in [(2,15),(30,15),(15,2),(15,30)]:
                d.rectangle((x,y,x+3,y+3),fill=BRASS,outline=GOLD)
            d.point((17,17),fill=WHITE)
    else:
        for x,y in [(3,3),(31,3),(3,31),(31,31)]:d.rectangle((x,y,x+1,y+1),fill=DARK)
    if wrong:
        for x,y in [(2,2),(28,2),(2,28),(28,28)]:
            d.line((x,y,x+5,y+5),fill=RED,width=2);d.line((x+5,y,x,y+5),fill=RED,width=2)
    return quant(im)

def battery(mode,frame=0):
    im=BASE['battery'].copy();d=ImageDraw.Draw(im)
    if mode=='docked':
        d.line([(3,29),(9,29),(9,25),(10,24)],fill=GOLD,width=2)
        d.line([(27,29),(22,29),(22,25),(21,24)],fill=GOLD,width=2)
        d.polygon([(15,9),(17,11),(15,13),(13,11)],fill=GOLD);d.point((15,11),fill=WHITE)
        d.line((11,4,19,4),fill=STEEL,width=2)
    elif mode=='moving':
        # Moving contact foot/latch, no resizing the heavy cube.
        shift=[0,0,1,1,1,0,-1,-1,0,0,0,0][frame]
        d.line((10+shift,4,18+shift,4),fill=STEEL,width=2)
        d.line((3+frame%3,30,7+frame%3,30),fill=GOLD,width=1)
    return quant(im)

def orb(mode,frame=0):
    im=BASE['orb'].copy();d=ImageDraw.Draw(im)
    if mode=='docked':
        d.arc((5,5,20,20),15,160,fill=WHITE,width=1)
        for x,y in [(2,11),(22,11),(11,2),(11,22)]:d.rectangle((x,y,x+1,y+1),fill=CYAN)
        d.point((12,12),fill=WHITE)
    elif mode=='moving':
        # Integer-edited internal meridian changes while the enclosing sphere
        # and point of ground contact stay stable (14 Tique Walk exposures).
        xx=[9,10,11,13,15,16,17,16,15,13,11,10,9,9][frame]
        d.line([(xx,7),(xx-2,12),(xx,19)],fill=BRASS,width=1)
        d.point((min(19,xx+2),8),fill=WHITE)
    return quant(im)

def pylon(level=0,arc=0,shutter=False,warning=False,fins=0):
    im=Image.new('RGBA',(42,60));base=dim_region(BASE['pylon'],(0,0,34,46),'cyan');im.alpha_composite(base,(4,8));d=ImageDraw.Draw(im)
    if level>0:
        fill=GOLD if warning else CYAN
        d.ellipse((17,17,25,25),fill=fill);d.rectangle((19,18,21,19),fill=WHITE)
        # Three separately authored capacitor windows fill upward.
        for j in range(3):d.rectangle((19,43-j*5,23,45-j*5),fill=fill if j<level else DARK)
    if shutter:
        d.rectangle((18,32,24,46),fill=BRASS,outline=GOLD)
        for y in (34,38,42):d.line((19,y,23,y),fill=INK)
    if fins:
        d.polygon([(8,48),(8-fins,55),(3,56),(11,56),(13,50)],fill=BRASS,outline=GOLD)
        d.polygon([(34,48),(34+fins,55),(39,56),(31,56),(29,50)],fill=BRASS,outline=GOLD)
    if arc:
        # Discrete sparks above the tips; stable whole-prop pivot.
        points=[(9,9),(14,6+arc%2),(19,10),(24,5+arc%3),(32,9)]
        d.line(points,fill=CYAN,width=2);d.line(points,fill=WHITE,width=1)
    return quant(im)

def core(mode,frame=0):
    im=BASE['core'].copy();d=ImageDraw.Draw(im)
    if mode=='off':
        p=im.load()
        for y in range(im.height):
            for x in range(im.width):
                r,g,b,a=p[x,y]
                if a and r>g*1.5:p[x,y]=(round(r*.22),round(g*.40),round(b*.65),255)
        d=ImageDraw.Draw(im)
        d.line((13,14,18,19),fill=INK,width=1);d.line((18,19,15,23),fill=INK,width=1)
    if mode=='hit':
        r=[0,2,4,6,7,6,5,4,3,2,1,0][frame]
        if r:d.line((16-r,18,16+r,18),fill=WHITE,width=1);d.line((16,18-r,16,18+r),fill=GOLD,width=1)
    return quant(im)

def door(gap=0):
    im=BASE['exit'].copy();d=ImageDraw.Draw(im)
    # Geometry is locked to a SINGLE converted door. Generated open state is
    # reference only, avoiding frame/jamb drift between independent images.
    if gap:
        region=(17,21,48,91);d.rectangle((17,21,47,90),fill=INK)
        d.rectangle((21,24,43,88),fill=DARK)
        d.rectangle((23,24,41,77),fill=INK)
        for y in (79,84,89):d.line((19,y,45,y),fill=STEEL)
        d.line((18,24,18,89),fill=CYAN);d.line((46,24,46,89),fill=CYAN)
        layer=Image.new('RGBA',im.size)
        layer.alpha_composite(BASE['exit'].crop((17,21,32,91)),(17-gap,21))
        layer.alpha_composite(BASE['exit'].crop((32,21,48,91)),(32+gap,21))
        im.alpha_composite(layer.crop(region),region[:2]);d=ImageDraw.Draw(im)
    else:
        d.rectangle((25,52,39,55),fill=BRASS,outline=INK);d.rectangle((30,52,33,55),fill=RED)
    # The lamp changes locally, not the entire gate tint.
    d.polygon([(31,7),(34,10),(31,13),(28,10)],fill=CYAN if gap>=15 else GOLD)
    return quant(im)

def warning(kind,frame):
    w,h={'charge':(32,8),'wave':(24,8),'slam':(136,16)}[kind]
    im=Image.new('RGBA',(w,h));d=ImageDraw.Draw(im);lit=frame in (3,4,5,6,7)
    tone=RED if kind!='wave' else GOLD
    if kind=='charge':
        d.line((0,7,31,7),fill=RED)
        for x in (3,13,23):d.line([(x,1),(x+4,4),(x,6)],fill=WHITE if lit else tone,width=1)
    elif kind=='wave':
        d.line([(1,7),(4,3),(7,7),(10,3),(13,7),(16,3),(20,7)],fill=tone,width=2)
        if lit:d.point((4,2),fill=WHITE);d.point((16,2),fill=WHITE)
    else:
        d.line((0,15,135,15),fill=RED,width=2)
        d.line([(0,15),(0,0),(7,0)],fill=RED,width=2);d.line([(135,15),(135,0),(128,0)],fill=RED,width=2)
        for x in (28,62,96):d.line([(x,7),(x+5,12),(x+10,7)],fill=WHITE if lit else tone,width=2)
    return im

def background(kind,power):
    im=Image.open(OLD/f'{kind}.png').convert('RGBA');d=ImageDraw.Draw(im)
    if kind=='workshop':
        # Three fixed relay indicators under the upper structure, in the clear
        # band between HUD and board. The factory stays dark; no geometry moves.
        for i in range(3):
            x=282+i*32;d.rectangle((x,53,x+14,60),fill=INK,outline=BRASS)
            d.rectangle((x+3,55,x+11,58),fill=CYAN if i<power else DARK)
            if i<power:d.line((x+4,55,x+10,55),fill=WHITE)
    elif power:
        for x,y in [(62,82),(220,143),(420,143),(578,83),(77,171),(562,173)]:
            d.rectangle((x-2,y-4,x+2,y+5),fill=BRASS)
            d.rectangle((x-1,y-3,x+1,y+3),fill=GOLD);d.point((x,y-2),fill=WHITE)
        for x in (285,319,352):d.line((x,261,x,279),fill=CYAN,width=2)
        for x in (244,306,368):d.line((x,281,x+20,281),fill=CYAN,width=1)
    return im

def export(name,frames,tique=None,loop=False,source='existing native prop + pixel edits'):
    times=TIQUE[tique]['durations'] if tique else [1000]
    assert len(frames)==len(times),(name,len(frames),len(times))
    dest=OUT/name;dest.mkdir(parents=True,exist_ok=True)
    art=ROOT/'Clips'/name;art.mkdir(parents=True,exist_ok=True)
    w,h=frames[0].size;sheet=Image.new('RGBA',(w*len(frames),h));base=frames[0]
    edits=[]
    for i,im in enumerate(frames):
        assert im.size==base.size
        im.save(art/f'{i:02}.png');shutil.copyfile(art/f'{i:02}.png',dest/f'{i:02}.png');sheet.alpha_composite(im,(i*w,0))
        delta=[[x,y,*im.getpixel((x,y))] for y in range(h) for x in range(w) if im.getpixel((x,y))!=base.getpixel((x,y))]
        edits.append({'frame':i,'changedPixels':len(delta),'bounds':im.getbbox(),'sha256':hashlib.sha256(im.tobytes()).hexdigest()})
        (art/f'{i:02}.pixels.json').write_text(json.dumps(delta,separators=(',',':')),encoding='utf-8')
    sheet.save(art/'sheet.png')
    if len(frames)>1:
        frames[0].save(art/'native.apng',format='PNG',save_all=True,append_images=frames[1:],duration=times,loop=0,disposal=0,blend=0)
        buf=io.BytesIO();sheet.save(buf,format='PNG')
        layer={'name':name,'opacity':1,'frameCount':len(frames),'chunks':[{'layout':[[i] for i in range(len(frames))],'base64PNG':'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()}]}
        p={'modelVersion':2,'piskel':{'name':name,'description':'Pixel-authored state transition; exact times in clips.json/APNG, uniform 20fps edit preview.','fps':20,'width':w,'height':h,'layers':[json.dumps(layer)]}}
        (art/(name+'.piskel')).write_text(json.dumps(p),encoding='utf-8')
    CLIPS.append({'name':name,'durations':times,'width':w,'height':h,'loop':loop,'tiqueTiming':tique,'source':source})
    AUDIT.append({'name':name,'frames':edits})

def main():
    (ROOT/'Source/Native').mkdir(parents=True,exist_ok=True)
    BASE['core']=native_concept('core-exposed',(32,36),(30,30),True)
    BASE['exit']=native_concept('exit-closed',(64,96),(60,94))
    for n,im in BASE.items():im.save(ROOT/f'Source/Native/{n}.png')
    for mode in ('idle','moving','docked'):
        export('battery-'+mode,[battery(mode,i) for i in range(12 if mode=='moving' else 1)],'Dash' if mode=='moving' else None,mode=='moving')
        export('orb-'+mode,[orb(mode,i) for i in range(14 if mode=='moving' else 1)],'Walk' if mode=='moving' else None,mode=='moving')
    for kind in ('amber','cyan'):
        export(kind+'-slot-empty',[socket(kind)])
        export(kind+'-slot-filled',[socket(kind,4)])
        export(kind+'-slot-wrong',[socket(kind,0,True)])
        export(kind+'-slot-connect',[socket(kind,n) for n in [0,0,1,1,2,2,3,3,4,4,4,4]],'Attack')
    export('pylon-idle',[pylon()]);export('pylon-armed',[pylon(3,1,False,False,3)])
    export('pylon-cooldown',[pylon(shutter=True)])
    export('pylon-charging',[pylon(l,a,False,False,f) for l,a,f in [(0,0,0),(0,0,0),(1,0,0),(1,1,0),(1,1,1),(2,2,1),(2,2,2),(3,3,2),(3,2,3),(3,1,3),(3,1,3),(3,1,3)]],'Attack')
    export('pylon-expiring',[pylon(3,1+i%3,False,i in (3,4,5,6,7),3) for i in range(12)],'Attack',True)
    export('pylon-discharge',[pylon(l,a,s,False,f) for l,a,s,f in [(3,1,False,3),(3,3,False,3),(3,2,False,3),(2,3,False,3),(2,2,False,2),(1,1,False,2),(1,0,False,1),(0,0,False,1),(0,0,True,0),(0,0,True,0),(0,0,True,0),(0,0,True,0)]],'Attack')
    export('core-exposed',[core('exposed')],source='single generated core -> native base')
    export('core-off',[core('off')]);export('core-hit',[core('hit',i) for i in range(12)],'Attack')
    disabled=Image.open(REPO/'art/return-v3-manual/Clips/stagger/06.png').convert('RGBA')
    steel=[p for p in set(disabled.getdata()) if p[3] and max(p[:3])-min(p[:3])<25 and sum(p[:3])<210]
    pixels=[]
    for r,g,b,a in disabled.getdata():
        if a and r>g*1.4 and r>b*1.4:
            target=(r*.23,g*.35,b*.5)
            pixels.append(min(steel,key=lambda p:sum((p[i]-target[i])**2 for i in range(3))))
        else:pixels.append((r,g,b,a))
    disabled.putdata(pixels)
    export('warden-powered-down',[disabled],source='unchanged v3 stagger 06 geometry; furnace/vent pixels extinguished using its own 32-color palette')
    spin=[]
    for i in range(14):
        angle=[0,0,0,1,1,1,2,2,2,3,3,3,0,0][i]
        im=BASE['gear'].copy()
        if angle:im=im.transpose([Image.Transpose.ROTATE_90,Image.Transpose.ROTATE_180,Image.Transpose.ROTATE_270][angle-1])
        spin.append(quant(im))
    export('wave-spin',spin,'Walk',True,'existing gear, exact 90-degree integer pixel permutations')
    export('exit-locked',[door()],source='single closed gate concept -> locked native base')
    export('exit-open',[door(15)])
    export('exit-opening',[door(g) for g in [0,0,1,2,4,6,8,10,12,14,15,15,15,15,15]],'Jump')
    for name in ('charge','wave','slam'):export('warning-'+name,[warning(name,i) for i in range(12)],'Attack',True,'pixel-authored danger marks using generated red gear / power circuit motifs')
    for i in range(4):export('workshop-power-'+str(i),[background('workshop',i)],source='original workshop native + fixed relay indicators')
    export('arena-dark',[background('arena',0)],source='unchanged original native arena')
    export('arena-restored',[background('arena',1)],source='generated restored room reference -> local lamp/conduit pixel edits on unchanged geometry')
    (OUT/'clips.json').write_text(json.dumps({'clips':CLIPS},indent=2),encoding='utf-8')
    (ROOT/'manifest.json').write_text(json.dumps({'status':'proposal; implemented for in-game review','method':'state concept images then explicit native pixel state/transition edits','generatedAnimationStripsUsed':False,'palette':PAL,'clips':CLIPS},indent=2),encoding='utf-8')
    (ROOT/'pixel-edit-audit.json').write_text(json.dumps(AUDIT,indent=2),encoding='utf-8')
    # One review image with a labeled representative frame for every state.
    small=[c for c in CLIPS if c['width']<640];cols=6;cw=220;ch=300
    contact=Image.new('RGB',(cols*cw,((len(small)+cols-1)//cols)*ch),(17,27,36));d=ImageDraw.Draw(contact)
    for i,c in enumerate(small):
        f=len(c['durations'])//2;im=Image.open(OUT/c['name']/f'{f:02}.png').convert('RGBA');scale=max(1,min(4,190//im.width,245//im.height))
        im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST);x=i%cols*cw;y=i//cols*ch
        contact.paste(im,(x+(cw-im.width)//2,y+245-im.height),im);d.text((x+8,y+258),c['name'],fill=(212,229,238));d.text((x+8,y+278),f"{len(c['durations'])} frames / {c['width']}x{c['height']}",fill=(146,170,185))
    (ROOT/'QA').mkdir(exist_ok=True);contact.save(ROOT/'QA/state-contact.png')
    print(f'Exported {len(CLIPS)} states / {sum(len(c["durations"]) for c in CLIPS)} frames / {len(PAL)} prop colors.')

if __name__=='__main__':main()
