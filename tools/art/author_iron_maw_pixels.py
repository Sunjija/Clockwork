"""Explicit integer-pixel key poses, per user's corrected workflow.

Inputs: ONE locked native base + Tique's approved timing JSON. Generated action
illustrations are drawing references only: this script never reads their pixels.
No AI strips, optical flow, rotations, interpolated/warped limbs or resampling.
Steel plates retain their pixel clusters; piston seams are redrawn at native size.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops
import base64, hashlib, io, json, shutil

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / 'art/return-v3-manual'
UNITY = REPO / 'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2/WardenAuthored'
BASE = Image.open(ROOT/'Source/base-native.png').convert('RGBA')
SIZE = BASE.size
TIQUE = json.loads((REPO/'prototypes/tique-playground/Revisions/10/data.json').read_text(encoding='utf-8'))['clips']
PALETTE = sorted({p[:3] for p in BASE.getdata() if p[3]})
def color(rgb):
    return (*min(PALETTE, key=lambda p: sum((p[i]-rgb[i])**2 for i in range(3))),255)
INK=color((9,13,18)); STEEL=color((137,150,157)); SHADOW=color((45,57,66))
LIGHT=color((182,192,198)); RED=color((143,40,23)); HOT=color((198,66,24))

def cut(poly):
    mask=Image.new('L',SIZE);ImageDraw.Draw(mask).polygon(poly,fill=255)
    im=BASE.copy();im.putalpha(ImageChops.multiply(BASE.getchannel('A'),mask));return im

# Native-pixel selections traced around lower leg plates; upper bearings stay
# in the chassis. The steel piston under each bearing is painted each pose.
LEG_POLYS=[[(29,119),(47,111),(55,104),(70,103),(76,108),(72,117),(67,120),(71,132),(29,132)],
           [(110,108),(119,103),(128,103),(133,108),(129,118),(134,131),(110,131)],
           [(79,123),(91,115),(95,108),(105,103),(113,99),(119,102),(120,112),(113,119),(124,128),(124,134),(79,134)],
           [(134,124),(140,115),(141,108),(148,102),(155,101),(161,104),(164,111),(160,120),(168,132),(134,132)]]
LEGS=[cut(p) for p in LEG_POLYS]
CHASSIS=BASE.copy()
for p in LEG_POLYS:ImageDraw.Draw(CHASSIS).polygon(p,fill=(0,0,0,0))
# Jaw plate selections follow the metal outline, not horizontal slice boundaries.
UP_POLY=[(27,43),(65,43),(69,59),(76,64),(78,70),(72,70),(49,62),(41,60),(39,68),(34,65),(29,64)]
LOW_POLY=[(26,73),(40,73),(44,79),(70,79),(77,77),(80,86),(77,91),(66,99),(46,100),(26,100)]
UPPER=cut(UP_POLY);LOWER=cut(LOW_POLY)
FRONT_BEARING=cut([(62,94),(72,89),(77,90),(76,96),(69,101),(60,100)])

def piston(draw,a,b,width=6):
    # Pixel-native connecting housing and steel rod. Both ends overlap plates.
    ax,ay=a;bx,by=b
    draw.polygon([(ax-width,ay-3),(ax+width,ay-3),(bx+width,by+3),(bx-width,by+3)],fill=INK)
    draw.line((ax,ay,bx,by),fill=STEEL,width=width)
    draw.line((ax-1,ay,bx-1,by),fill=LIGHT,width=2)

def pose(dx=0,dy=0,close=0,tuck=0,recoil=0,stride=0):
    if not any([dx,dy,close,tuck,recoil,stride]):return BASE.copy()
    out=Image.new('RGBA',SIZE);d=ImageDraw.Draw(out)
    offsets=[(tuck//3+stride,-tuck),(-tuck//4-stride,-tuck),
             (tuck//4-stride,-tuck),(-tuck//3+stride,-tuck)]
    # Bearings -> lower piston sockets, from rear to front. Feet remain fixed
    # during grounded compression; ONLY airborne poses tuck the feet upward.
    anchors=[(65,100),(123,103),(100,94),(143,94)]
    sockets=[(61,110),(122,111),(108,109),(153,110)]
    for idx,((ax,ay),(bx,by),(lx,ly)) in enumerate(zip(anchors,sockets,offsets)):
        if idx<2:
            d.line((ax+dx,ay+dy,bx+lx,by+ly),fill=INK,width=7)
            d.line((ax+dx,ay+dy,bx+lx,by+ly),fill=SHADOW,width=3)
        else:piston(d,(ax+dx,ay+dy),(bx+lx,by+ly),4)
    body=CHASSIS.copy();bd=ImageDraw.Draw(body)
    if close or recoil:
        bd.polygon(UP_POLY,fill=(0,0,0,0));bd.polygon(LOW_POLY,fill=(0,0,0,0))
        # Preserve the original furnace clusters instead of replacing them
        # with a flat rectangle. Extend only the rear hinge into exposed space.
        bd.polygon([(72,63),(78,66),(79,91),(70,95)],fill=INK)
        up_y=close//2-recoil;lo_y=-(close-close//2)-recoil
        body.alpha_composite(LOWER,(0,lo_y))
        body.alpha_composite(UPPER,(0,up_y))
        # Rear jaw rail: hand-placed rows of steel rejoin the translated plates.
        bd=ImageDraw.Draw(body)
        bd.line((75,68+up_y,76,85+lo_y),fill=INK,width=5)
        bd.line((75,68+up_y,76,85+lo_y),fill=SHADOW,width=3)
        bd.point((74,69+up_y),fill=STEEL)
        body.alpha_composite(FRONT_BEARING)
    out.alpha_composite(body,(dx,dy))
    for leg,(lx,ly) in zip(LEGS,offsets):out.alpha_composite(leg,(lx,ly))
    return out

# Explicitly authored exposure poses. Fields: body x/y, jaw closure, airborne
# foot tuck, jaw recoil, alternating lower-foot stride (all integer pixels).
# Every sequence ends at the same exact base; anticipation and recovery differ.
POSES={
 'idle':[(0,0,0,0,0,0)],
 'attack':[(0,0,0,0,0,0),(1,0,0,0,0,0),(2,2,0,0,0,0),
           (-1,1,6,0,0,0),(-3,1,13,0,0,0),(-2,1,13,0,0,0),
           (-1,1,10,0,0,0),(0,0,6,0,0,0),(1,-1,3,0,1,0),
           (1,0,1,0,0,0),(0,0,1,0,0,0),(0,0,0,0,0,0)],
 'charge':[(0,0,0,0,0,0),(1,1,3,0,0,0),(2,3,7,0,0,0),
           (-1,3,10,0,0,0),(-3,2,11,0,0,1),(-3,2,11,0,0,-1),
           (-2,2,10,0,0,1),(-1,3,9,0,0,0),(1,2,6,0,0,0),
           (1,1,3,0,0,0),(0,0,1,0,0,0),(0,0,0,0,0,0)],
 'slam':[(0,0,0,0,0,0),(0,2,1,0,0,0),(0,3,3,0,0,0),
         (0,-1,3,2,0,0),(0,-1,2,5,0,0),(0,0,1,8,0,0),
         (0,0,0,9,0,0),(0,0,1,7,0,0),(0,0,3,4,0,0),
         (0,1,5,1,0,0),(0,4,8,0,0,0),(0,3,6,0,0,0),
         (0,1,3,0,1,0),(0,0,1,0,0,0),(0,0,0,0,0,0)],
 'stagger':[(0,0,0,0,0,0),(-1,1,7,0,0,0),(2,1,3,0,1,0),
            (3,-1,0,0,2,0),(2,-2,0,0,3,0),(1,-1,0,0,3,0),
            (1,-1,0,0,2,0),(0,-1,0,0,2,0),(0,0,0,0,1,0),
            (0,0,0,0,1,0),(0,0,0,0,0,0),(0,0,0,0,0,0)]}
MAP={'idle':'Idle','attack':'Attack','charge':'Dash','slam':'Jump','stagger':'Attack'}
LABELS={
 'idle':['original base'],
 'attack':['base','coil','brace','snap','impact','hold','release','return','recoil','settle','jaw rest','base'],
 'charge':['base','lower','brace','launch','drive A','drive B','drive A','brake','absorb','settle','jaw rest','base'],
 'slam':['base','compress','brace','lift','tuck','apex in','apex','unfold','fall','reach','contact','absorb','head follows','recover','base'],
 'stagger':['base','collision','recoil','rise','overload','hold','open','settle','release','return','rest','base']}

def png_data(im):
    buf=io.BytesIO();im.save(buf,format='PNG');return base64.b64encode(buf.getvalue()).decode()

def main():
    result={'method':'explicit integer pixel cluster edits and native piston/jaw seam repaint',
            'base':'Source/base-native.png','baseSha256':hashlib.sha256((ROOT/'Source/base-native.png').read_bytes()).hexdigest(),
            'referenceImagesAreRuntimeInputs':False,'cell':list(SIZE),'anchor':[96,132],
            'timingSource':'prototypes/tique-playground/Revisions/10/data.json','clips':[]}
    audit=[]
    for name,states in POSES.items():
        folder=ROOT/'Clips'/name;folder.mkdir(parents=True,exist_ok=True)
        dest=UNITY/name;dest.mkdir(parents=True,exist_ok=True)
        times=TIQUE[MAP[name]]['durations'];assert len(times)==len(states)
        frames=[pose(*s) for s in states]
        sheet=Image.new('RGBA',(SIZE[0]*len(frames),SIZE[1]))
        contact=Image.new('RGB',(SIZE[0]*3*4,(SIZE[1]*3+30)*((len(frames)+3)//4)),(20,29,40))
        cd=ImageDraw.Draw(contact)
        changes=[]
        for i,(im,state,t) in enumerate(zip(frames,states,times)):
            im.save(folder/f'{i:02}.png');shutil.copyfile(folder/f'{i:02}.png',dest/f'{i:02}.png')
            sheet.alpha_composite(im,(i*SIZE[0],0))
            x=(i%4)*SIZE[0]*3;y=(i//4)*(SIZE[1]*3+30)
            contact.paste(im.resize((SIZE[0]*3,SIZE[1]*3),Image.Resampling.NEAREST),(x,y),im.resize((SIZE[0]*3,SIZE[1]*3),Image.Resampling.NEAREST))
            cd.text((x+12,y+SIZE[1]*3+6),f'{name} {i:02} | {t} ms | {LABELS[name][i]}',fill=(222,232,239))
            delta=[]
            for yy in range(SIZE[1]):
                for xx in range(SIZE[0]):
                    a=BASE.getpixel((xx,yy));b=im.getpixel((xx,yy))
                    if a!=b:delta.append([xx,yy,*b])
            changes.append({'frame':i,'changedPixels':len(delta),'pose':list(state),'bounds':im.getbbox()})
            # Reviewable coordinate edits; can reconstruct each frame without
            # the pose compositor. Transparent RGB is included for exact bytes.
            (folder/f'{i:02}.pixels.json').write_text(json.dumps(delta,separators=(',',':')),encoding='utf-8')
        sheet.save(folder/'sheet.png');contact.save(folder/'contact.png')
        frames[0].save(folder/'native.apng',format='PNG',save_all=True,append_images=frames[1:],duration=times,loop=0,disposal=0,blend=0)
        expanded=[im.resize((576,432),Image.Resampling.NEAREST) for im in frames]
        expanded[0].save(folder/'preview.apng',format='PNG',save_all=True,append_images=expanded[1:],duration=times,loop=0,disposal=0,blend=0)
        layer={'name':'pixel-authored frames','opacity':1,'frameCount':len(frames),
               'chunks':[{'layout':[[i] for i in range(len(frames))],'base64PNG':'data:image/png;base64,'+png_data(sheet)}]}
        piskel={'modelVersion':2,'piskel':{'name':'Iron Maw '+name,'description':'Native pixel-authored; exact durations in timing.json/APNG (Piskel uniform FPS preview only).',
                'fps':20,'height':SIZE[1],'width':SIZE[0],'layers':[json.dumps(layer)]}}
        (folder/(name+'.piskel')).write_text(json.dumps(piskel),encoding='utf-8')
        clip={'name':name,'durations':times,'names':LABELS[name],'tiqueClip':MAP[name],
              'poses':states,'frames':len(frames),'durationMs':sum(times),'loop':name=='idle'}
        (folder/'timing.json').write_text(json.dumps(clip,indent=2),encoding='utf-8')
        result['clips'].append(clip);audit.append({'clip':name,'frames':changes})
    (ROOT/'manifest.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (UNITY/'clips.json').write_text(json.dumps({'clips':result['clips']},indent=2),encoding='utf-8')
    (ROOT/'QA/pixel-edit-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    print('Exported',sum(len(s) for s in POSES.values()),'authored frames; generated action reference images were NOT read.')

if __name__=='__main__':main()
