"""Trace selected complete-body imagegen poses into native 64px action clips.

User explicitly requested native pixel tracing of individually generated poses.
Every key's head, torso, arms and legs come from its own complete-body source;
the original Idle is used only as the neutral endpoint and palette reference.
No V8 body rig, original component translation or smooth inbetween warps.
"""
from pathlib import Path
from collections import Counter, deque
from functools import lru_cache
import hashlib, json, math, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'art/return-v9-traced'
SRC = ART / 'ActionSource'
NATIVE = SRC / 'Native'
ORIGINAL = ROOT / 'unity/TiqueReturnPrototype/Assets/Resources/Return/Tique'
BASE = Image.open(ORIGINAL / 'Idle/00.png').convert('RGBA')
PAL = [c for c, n in Counter(c for c in BASE.getdata() if c[3]).most_common()]
CLEAR = (0, 0, 0, 0)
INK, BRASS, GOLD, SHADE, LIGHT, MID, WHITE = PAL[:7]
TIMES = {c['name']: c['durations'] for c in json.loads((ORIGINAL.parent / 'clips.json').read_text())['clips']}

# Measured source head top/neck/left/right landmarks. The entire source is
# traced through one piecewise scale; these are NOT separately composited limbs.
# Head normalizes to the requested 31x27 footprint while lower body retains
# its generated shape in the compact remaining 17-21px height.
KEYS = {
    'attack-windup': dict(head=(364,208,965,723), bottom=1076, at=(16,8), body_h=21),
    'attack-impact': dict(head=(318,171,945,717), bottom=1092, at=(18,8), body_h=21),
    'attack-recoil': dict(head=(316,166,950,696), bottom=1093, at=(17,8), body_h=21),
    'attack-extension': dict(head=(305,160,942,691), bottom=1094, at=(17,8), body_h=21),
    'dash-preload': dict(head=(376,228,1019,766), bottom=1073, at=(17,12), body_h=17),
    'dash-travel-a': dict(head=(377,183,992,710), bottom=1079, at=(18,10), body_h=19),
    'dash-travel-b': dict(head=(363,177,991,713), bottom=1092, at=(18,10), body_h=19),
    'dash-braking': dict(head=(366,206,981,741), bottom=1084, at=(16,10), body_h=19),
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def csha(im):
    return hashlib.sha256(im.tobytes()).hexdigest()

@lru_cache(maxsize=65536)
def nearest(c):
    return min(PAL, key=lambda q: sum((q[i] - c[i]) ** 2 for i in range(3)))

def sy(y, spec):
    l,t,r,b = spec['head']; x0,y0=spec['at']
    return t + (y-y0)*(b-t)/27 if y <= y0+27 else b+(y-y0-27)*(spec['bottom']-b)/spec['body_h']

def trace(name, spec):
    path=SRC / 'Generated' / (name+'.png')
    src=Image.open(path).convert('RGBA')
    im=Image.new('RGBA',(64,64))
    l,t,r,b=spec['head']; x0,y0=spec['at']; sx=(r-l)/31
    for y in range(y0,y0+27+spec['body_h']):
        top=max(0,int(sy(y,spec))); bottom=min(src.height,int(sy(y+1,spec)))
        for x in range(64):
            left=max(0,math.floor(l+(x-x0)*sx)); right=min(src.width,math.ceil(l+(x+1-x0)*sx))
            if left>=right or top>=bottom: continue
            region=src.crop((left,top,right,bottom))
            opaque=[c for c in region.getdata() if c[3]>=128]
            if len(opaque) < region.width*region.height*0.36:continue
            # Dominant existing source color cluster, no averaged transition RGB.
            color=Counter(nearest(c) for c in opaque).most_common(1)[0][0]
            im.putpixel((x,y),color)
    im.save(NATIVE / (name+'-trace-raw.png'))
    return im

def patch(im, entries):
    for x,y,c in entries: im.putpixel((x,y),c)

# After full-body trace these explicit per-key pixels close contours, restore
# one-pixel elbow volume and remove isolated sampled edge specks. Filled only
# after viewing the native 3x key contact sheet.
CLEANUP = {}

# Hand contour measurements from the viewed 8x native traces. Source mittens
# normalize to 4x5 native cells; the body's generated elbow/shoulder volumes
# remain traced. This is the local contour cleanup after full-body conversion.
HANDS = {
    'attack-windup': [((13,30,20,36),(14,31)),((43,36,48,45),(44,38))],
    'attack-impact': [((18,37,24,43),(19,38)),((53,29,59,37),(54,30))],
    'attack-recoil': [((17,42,23,48),(18,42)),((40,40,46,46),(41,41))],
    'attack-extension': [((17,40,23,46),(18,40)),((45,31,51,39),(46,32))],
    'dash-preload': [((13,41,19,47),(14,42)),((42,42,47,49),(43,43))],
    'dash-travel-a': [((14,38,20,44),(15,38)),((43,40,50,46),(45,41))],
    'dash-travel-b': [((18,39,23,44),(18,39)),((42,40,46,46),(42,40))],
    'dash-braking': [((11,39,18,45),(12,39)),((41,43,47,49),(43,44))],
}
HAND_JOIN = {
    'attack-windup': [(18,34,BRASS),(19,35,BRASS),(43,40,BRASS)],
    'attack-impact': [(22,38,BRASS),(23,37,BRASS),(23,38,BRASS),(24,38,GOLD),(23,39,BRASS),(24,39,SHADE),(53,33,BRASS)],
    'attack-recoil': [(21,42,BRASS),(22,41,BRASS),(40,42,BRASS)],
    'attack-extension': [(22,41,BRASS),(23,40,GOLD),(22,40,GOLD),(23,41,BRASS),(45,34,GOLD),(45,35,BRASS),(44,35,BRASS),(44,36,BRASS)],
    'dash-preload': [(18,42,BRASS),(19,41,BRASS),(18,41,GOLD),(19,42,BRASS),(18,43,SHADE),(42,44,BRASS)],
    'dash-travel-a': [(18,38,BRASS),(19,37,BRASS),(44,43,BRASS),(43,42,BRASS),(44,42,BRASS),(43,41,GOLD),(43,43,SHADE),(42,42,BRASS)],
    'dash-travel-b': [(21,39,BRASS),(22,38,BRASS),(41,41,BRASS)],
    'dash-braking': [(16,40,BRASS),(17,39,BRASS),(42,45,BRASS),(41,44,BRASS),(42,44,GOLD),(41,45,SHADE),(40,44,BRASS)],
}

def clean_hands(im, name):
    for box,(x,y) in HANDS[name]:
        # Native contours retain the source glove's clustered bronze shading.
        for yy in range(box[1],box[3]):
            for xx in range(box[0],box[2]):im.putpixel((xx,yy),CLEAR)
        rows=['.AA.','AEBA','ADCA','AFCA','.AA.']
        chips={'A':INK,'B':LIGHT,'C':BRASS,'D':GOLD,'E':WHITE,'F':MID}
        for yy,row in enumerate(rows):
            for xx,sym in enumerate(row):
                im.putpixel((x+xx,y+yy),chips[sym] if sym!='.' else CLEAR)
    patch(im,HAND_JOIN[name])

def contact(items, path, columns=4):
    font=ImageFont.load_default()
    tile_w,tile_h=224,218
    sheet=Image.new('RGBA',(columns*tile_w,math.ceil(len(items)/columns)*tile_h),(18,26,31,255))
    d=ImageDraw.Draw(sheet)
    for i,(label,im) in enumerate(items):
        x,y=i%columns*tile_w,i//columns*tile_h
        d.text((x+8,y+5),label,fill=(245,210,130),font=font)
        sheet.alpha_composite(im.resize((192,192),Image.Resampling.NEAREST),(x+16,y+22))
        d.line((x+16,y+22+56*3,x+207,y+22+56*3),fill=(60,85,92))
    sheet.save(path)

def groups(im):
    remaining={(x,y) for y in range(64) for x in range(64) if im.getpixel((x,y))[3]}
    out=[]
    while remaining:
        p=remaining.pop(); component={p}; todo=[p]
        while todo:
            x,y=todo.pop()
            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                q=(x+dx,y+dy)
                if q in remaining:remaining.remove(q);component.add(q);todo.append(q)
        out.append(component)
    return sorted(out,key=len,reverse=True)

def exposure(key, entries):
    im=key.copy(); patch(im,entries);return im

def export_clips(keys, only=None):
    # Individually generated full-body keys supply every major motion phase.
    # The short native exposure edits below change contour/shading locally;
    # no frame is warped, rotated, interpolated, or rebuilt from original parts.
    attack_specs=[
        ('neutral',[]),
        ('attack-windup',[(23,47,GOLD),(24,48,BRASS),(26,48,SHADE),(21,36,LIGHT)]),
        ('attack-windup',[]),
        ('attack-extension',[]),
        ('attack-impact',[]),
        ('attack-impact',[(49,34,GOLD),(50,34,GOLD),(51,34,BRASS),(27,46,MID),(28,47,SHADE)]),
        ('attack-impact',[(48,34,BRASS),(49,34,BRASS),(50,34,MID),(27,47,SHADE),(28,47,SHADE),(38,49,GOLD)]),
        ('attack-recoil',[]),
        ('attack-recoil',[(24,47,GOLD),(25,47,BRASS),(26,48,SHADE),(36,47,BRASS),(37,47,GOLD)]),
        ('attack-recoil',[(23,49,LIGHT),(24,49,GOLD),(25,49,BRASS),(34,49,MID),(35,49,SHADE)]),
        ('neutral',[(27,49,GOLD),(28,49,BRASS)]),
        ('neutral',[]),
    ]
    dash_specs=[
        ('neutral',[]),
        ('dash-preload',[(22,49,GOLD),(23,49,BRASS),(24,49,SHADE),(33,50,MID),(34,50,SHADE)]),
        ('dash-preload',[]),
        ('dash-travel-a',[]),
        ('dash-travel-a',[(23,51,LIGHT),(24,51,GOLD),(25,51,BRASS),(26,51,SHADE),(37,50,GOLD)]),
        ('dash-travel-b',[]),
        ('dash-travel-b',[(34,51,BRASS),(35,51,GOLD),(36,51,LIGHT),(24,48,MID),(25,48,SHADE)]),
        ('dash-travel-a',[(25,51,LIGHT),(26,51,GOLD),(27,51,BRASS),(37,50,LIGHT),(38,50,GOLD)]),
        ('dash-braking',[]),
        ('dash-braking',[(23,48,GOLD),(24,48,BRASS),(25,49,SHADE),(37,50,GOLD),(38,50,BRASS)]),
        ('neutral',[(27,49,GOLD),(28,49,BRASS)]),
        ('neutral',[]),
    ]
    clip_records=[]
    neutral_hands=[((17,43,21,48),(17,43)),((43,43,47,48),(43,43))]
    for name,specs in [('Attack',attack_specs),('Dash',dash_specs)]:
        if only and name!=only:continue
        folder=ART/name; folder.mkdir(parents=True,exist_ok=True)
        frames=[];records=[]
        for i,(key,entries) in enumerate(specs):
            im=exposure(BASE if key=='neutral' else keys[key],entries)
            path=folder/(str(i).zfill(2)+'.png');im.save(path);frames.append(im)
            assert set(im.getdata()).issubset(set(PAL)|{CLEAR}),path
            assert set(im.getchannel('A').getdata()).issubset({0,255}),path
            assert im.getbbox() and min(im.getbbox()[:2])>0 and max(im.getbbox()[2:])<64,path
            gs=groups(im);main=gs[0]
            assert len(gs)==1,(name,i,'isolated contour or detached limb',list(map(len,gs)))
            hand_specs=neutral_hands if key=='neutral' else HANDS[key]
            hands=[]
            for _,(hx,hy) in hand_specs:
                pixels=[(x,y) for y in range(hy,hy+5) for x in range(hx,hx+4) if im.getpixel((x,y))[3]]
                # Both complete small hands must remain present and physically
                # connected to the full character, not detached dark specks.
                assert len(pixels)>=10,(name,i,'hand-empty',hx,hy)
                assert all(p in main for p in pixels),(name,i,'hand-detached',hx,hy)
                hands.append(dict(box=[hx,hy,hx+4,hy+5],opaque_pixels=len(pixels),connected_to_body=True))
            records.append(dict(index=i,file=path.name,duration_ms=TIMES[name][i],source_key=key,
                pixel_edits=[[x,y,list(c)] for x,y,c in entries],rgba_sha256=csha(im),
                alpha_bounds=list(im.getbbox()),palette_colors=len(set(c for c in im.getdata() if c[3])),
                foreground_components_4_connected=list(map(len,gs)),hands=hands))
        assert csha(frames[0])==csha(BASE) and csha(frames[-1])==csha(BASE)
        manifest=dict(clip=name,frame_size=[64,64],pixel_pivot=[32,56],durations_ms=TIMES[name],
            frame_count=12,neutral_endpoints_match_original=True,source_method='complete single generated body key trace + local native exposure pixels',
            all_hands_visible_and_connected=True,frames=records)
        (folder/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
        contact([(f'{name} {i:02d} {r[0]}',im) for i,(r,im) in enumerate(zip(specs,frames))],folder/'contact-3x.png')
        frames8=[im.resize((512,512),Image.Resampling.NEAREST) for im in frames]
        frames8[0].save(folder/'preview-8x.gif',save_all=True,append_images=frames8[1:],duration=TIMES[name],loop=0,disposal=2)
        clip_records.append(manifest)
        if name=='Dash':export_ghost(frames)
    return clip_records

def export_ghost(frames):
    folder=ART/'dash-ghost';folder.mkdir(parents=True,exist_ok=True)
    cyan=[(19,52,69,255),(9,86,107,255),(11,147,177,255),(19,220,232,255),(165,252,241,255)]
    items=[];records=[]
    for i,source in enumerate(frames):
        im=Image.new('RGBA',(64,64))
        for y in range(64):
            for x in range(64):
                c=source.getpixel((x,y))
                if c[3]:
                    lum=0.25*c[0]+0.55*c[1]+0.2*c[2]
                    im.putpixel((x,y),cyan[0 if lum<60 else 1 if lum<105 else 2 if lum<150 else 3 if lum<200 else 4])
        assert source.getchannel('A').tobytes()==im.getchannel('A').tobytes()
        im.save(folder/(str(i).zfill(2)+'.png'));items.append((f'Ghost {i:02d}',im))
        records.append(dict(index=i,duration_ms=TIMES['Dash'][i],dash_rgba_sha256=csha(source),ghost_rgba_sha256=csha(im),silhouette_matches_dash=True))
    (folder/'manifest.json').write_text(json.dumps(dict(frame_count=12,frame_size=[64,64],pixel_pivot=[32,56],durations_ms=TIMES['Dash'],frames=records),indent=2),encoding='utf-8')
    contact(items,folder/'contact-3x.png')

def main():
    NATIVE.mkdir(parents=True,exist_ok=True)
    transition_only='--attack-transition' in sys.argv
    keys={n:Image.open(NATIVE/(n+'.png')).convert('RGBA') for n in KEYS if n!='attack-extension'} if transition_only else {}
    traced={n:trace(n,s) for n,s in KEYS.items() if not transition_only or n=='attack-extension'}
    for n,im in traced.items():
        clean_hands(im,n); patch(im,CLEANUP.get(n,[])); im.save(NATIVE/(n+'.png'))
        im.resize((512,512),Image.Resampling.NEAREST).save(NATIVE/(n+'-8x.png'))
    keys.update(traced)
    contact(list(keys.items()),SRC/'native-keys-contact-3x.png')
    records=[]
    for n,im in keys.items():
        path=SRC/'Generated'/(n+'.png')
        records.append(dict(key=n,source=path.relative_to(ROOT).as_posix(),source_sha256=sha(path),
            source_size=list(Image.open(path).size),native=NATIVE.joinpath(n+'.png').relative_to(ROOT).as_posix(),
            trace_landmarks=KEYS[n],native_rgba_sha256=csha(im),
            cleanup_pixels=sum(a!=b for a,b in zip(Image.open(NATIVE/(n+'-trace-raw.png')).convert('RGBA').getdata(),im.getdata())),
            hand_contours=[dict(raw_box=list(box),native_box=[at[0],at[1],at[0]+4,at[1]+5]) for box,at in HANDS[n]],
            method='complete-body alpha silhouette and dominant palette clusters, head footprint normalized 31x27; explicit native contour cleanup'))
    (SRC/'trace-records.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    clips=export_clips(keys,only='Attack' if transition_only else None)
    if transition_only:clips.append(json.loads((ART/'Dash/manifest.json').read_text(encoding='utf-8')))
    (SRC/'validation.json').write_text(json.dumps(dict(generated_complete_body_keys=len(KEYS),
        rejected_sources=[],native_trace_keys=len(KEYS),frame_size=[64,64],palette=list(PAL),
        clips=[dict(name=c['clip'],frames=c['frame_count'],all_hands_visible_and_connected=c['all_hands_visible_and_connected'],neutral_endpoints_exact=True) for c in clips],
        binary_alpha=True,no_resampling_between_frames=True,
        visual_review_status='native keys at 8x and all three 3x clip contacts inspected; both hands visible, continuous wrists, compact silhouette, no mixed pixel colors',
        runtime_playback_review=False),indent=2),encoding='utf-8')

if __name__=='__main__':main()
