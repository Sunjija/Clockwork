"""Trace selected complete-body imagegen poses into native 64px action clips.

User explicitly requested individually generated complete-body pose guides,
then native tracing. The later uniformity correction fixes every key's entire
head/chest/core to the original model through explicit native pixel deltas.
Generated complete bodies guide limb actions, not alternate character designs.
No V8 rig, image crop composition, body-band resizing or smooth inbetween warp
is used to define the final canonical identity.
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

# Initial coarse trace landmarks for the complete generated pose image. Source
# identity from this draft is explicitly rejected below: correct_identity()
# restores the final exact original head/chest/core before exporting any clip.
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

# Original model identity. Imagegen sources now guide the action only; their
# face/chest variations are explicitly corrected in the native full-body raster.
# This is per-pixel correction data, not crop/part composition or body-band warp.
HEAD_BASE=(16,8,47,35)
BODY_BASE=(23,34,44,50)
CORE_BASE=(30,37,43,47)
IDENTITY_AT={
    'attack-windup':(16,8), 'attack-extension':(17,8),
    'attack-impact':(18,8), 'attack-recoil':(17,8),
    'dash-preload':(17,10), 'dash-travel-a':(18,10),
    'dash-travel-b':(18,10), 'dash-braking':(16,10),
}
OLD_TORSO={
    'attack-windup':(21,34,43,50),'attack-impact':(24,34,44,50),
    'attack-extension':(22,34,43,50),'attack-recoil':(24,35,43,50),
    'dash-preload':(21,38,43,52),'dash-travel-a':(23,35,43,51),
    'dash-travel-b':(24,36,44,51),'dash-braking':(20,35,41,51),
}

def identity_boxes(name):
    hx,hy=IDENTITY_AT[name];dx,dy=hx-16,hy-8
    return (hx,hy,hx+31,hy+27),(23+dx,34+dy,44+dx,50+dy),(30+dx,37+dy,43+dx,47+dy)

def inside(x,y,box):
    return box[0]<=x<box[2] and box[1]<=y<box[3]

# These measured limb regions belong to the generated complete-body native
# trace. Integer pixel corrections lower the windup/impact arm below the fixed
# head and move support hands outside the fixed chest. No original limb donor.
ARM_TRACE_CORRECTIONS={
    'attack-windup':[((13,30,24,40),(0,4)),((42,36,50,46),(0,0))],
    'attack-impact':[((17,33,25,44),(0,0)),((43,29,60,39),(0,5))],
    'attack-extension':[((17,35,24,47),(0,0)),((42,30,52,40),(3,3))],
    'attack-recoil':[((16,35,24,49),(0,0)),((40,39,47,48),(4,0))],
    'dash-preload':[((12,36,24,49),(0,0)),((42,40,50,50),(3,0))],
    'dash-travel-a':[((13,33,25,46),(0,1)),((43,39,51,47),(2,0))],
    'dash-travel-b':[((16,34,25,46),(0,0)),((41,38,49,48),(5,0))],
    'dash-braking':[((10,33,23,47),(0,0)),((41,41,49,51),(2,0))],
}
ROUND_AT={
    'attack-windup':[(14,35),(44,38)], 'attack-impact':[(19,38),(54,35)],
    'attack-extension':[(18,40),(49,35)],'attack-recoil':[(18,42),(45,41)],
    'dash-preload':[(14,42),(46,43)],'dash-travel-a':[(15,39),(47,41)],
    'dash-travel-b':[(18,39),(47,40)],'dash-braking':[(12,39),(45,44)],
}
WRIST_CLEANUP={
    'attack-windup':[(18,38,CLEAR),(16,39,BRASS),(17,39,BRASS),(18,39,BRASS),(19,39,BRASS),(43,40,BRASS)],
    'attack-impact':[(23,39,BRASS),(24,39,GOLD),(53,37,BRASS),(52,37,BRASS)],
    'attack-extension':[(22,42,BRASS),(23,42,BRASS),(48,37,BRASS),(47,37,GOLD),(45,35,CLEAR)],
    'attack-recoil':[(22,43,BRASS),(23,43,BRASS),(44,43,BRASS)],
    'dash-preload':[(18,44,BRASS),(19,43,BRASS),(23,39,BRASS),(45,45,BRASS)],
    'dash-travel-a':[(19,41,BRASS),(20,40,BRASS),(24,38,BRASS),(46,43,BRASS),(24,52,BRASS),(25,52,BRASS),(26,52,BRASS)],
    'dash-travel-b':[(22,41,BRASS),(23,40,BRASS),(24,39,BRASS),(46,42,BRASS)],
    'dash-braking':[(16,41,BRASS),(17,40,CLEAR),(22,39,BRASS),(44,46,BRASS)],
}

def correct_identity(raw,name):
    im=raw.copy();head_box,body_box,core_box=identity_boxes(name)
    old_hx,old_hy=KEYS[name]['at']
    # Remove source identity drift including its one-pixel sampled fringe.
    erase=[(old_hx-1,old_hy-1,old_hx+33,old_hy+28),OLD_TORSO[name]]
    erase += [region for region,offset in ARM_TRACE_CORRECTIONS[name]]
    for box in erase:
        for y in range(max(0,box[1]),min(64,box[3])):
            for x in range(max(0,box[0]),min(64,box[2])):im.putpixel((x,y),CLEAR)
    dx,dy=head_box[0]-16,head_box[1]-8
    # Each changed native cell is recorded below for inspection/replay. The
    # source whole-body image is retained; no crop is pasted or alpha-composited.
    for refbox,target in [(BODY_BASE,body_box),(HEAD_BASE,head_box)]:
        for y in range(target[1],target[3]):
            for x in range(target[0],target[2]):im.putpixel((x,y),BASE.getpixel((x-dx,y-dy)))
    for region,(mx,my) in ARM_TRACE_CORRECTIONS[name]:
        for y in range(region[1],region[3]):
            for x in range(region[0],region[2]):
                if any(inside(x,y,box) for box,at in HANDS[name]):continue
                tx,ty=x+mx,y+my
                if not(0<=tx<64 and head_box[3]<=ty<64):continue
                if inside(tx,ty,head_box) or inside(tx,ty,body_box):continue
                c=raw.getpixel((x,y))
                if c[3]:im.putpixel((tx,ty),c)
    for x,y,c in WRIST_CLEANUP[name]:
        if not inside(x,y,head_box) and not inside(x,y,body_box):im.putpixel((x,y),c)
    # Fingerless 4x4 round balls, 2/4/4/2 silhouette, exactly two colors.
    for x,y in ROUND_AT[name]:
        for yy,row in enumerate(['.II.','IGGI','IGGI','.II.']):
            for xx,s in enumerate(row):im.putpixel((x+xx,y+yy),INK if s=='I' else GOLD if s=='G' else CLEAR)
    delta=[]
    for y in range(64):
        for x in range(64):
            a,b=raw.getpixel((x,y)),im.getpixel((x,y))
            if a!=b:delta.append(dict(x=x,y=y,before=list(a),after=list(b)))
    return im,delta

# Measured rejected source hand regions. Their thumb-like bumps are removed
# during whole-body native correction; final hands use ROUND_AT, not this shape.
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

def exposure(key, entries,name='neutral'):
    im=key.copy()
    boxes=identity_boxes(name)[:2] if name!='neutral' else [HEAD_BASE,BODY_BASE]
    for x,y,c in entries:
        if not any(inside(x,y,b) for b in boxes) and im.getpixel((x,y))[3]:im.putpixel((x,y),c)
    return im

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
            im=exposure(BASE if key=='neutral' else keys[key],entries,key)
            path=folder/(str(i).zfill(2)+'.png');im.save(path);frames.append(im)
            assert set(im.getdata()).issubset(set(PAL)|{CLEAR}),path
            assert set(im.getchannel('A').getdata()).issubset({0,255}),path
            assert im.getbbox() and min(im.getbbox()[:2])>0 and max(im.getbbox()[2:])<64,path
            gs=groups(im);main=gs[0]
            assert len(gs)==1,(name,i,'isolated contour or detached limb',list(map(len,gs)))
            hand_specs=neutral_hands if key=='neutral' else [(None,at) for at in ROUND_AT[key]]
            hands=[]
            for _,(hx,hy) in hand_specs:
                hand_h=5 if key=='neutral' else 4
                pixels=[(x,y) for y in range(hy,hy+hand_h) for x in range(hx,hx+4) if im.getpixel((x,y))[3]]
                # Both complete small hands must remain present and physically
                # connected to the full character, not detached dark specks.
                assert len(pixels)>=10,(name,i,'hand-empty',hx,hy)
                assert all(p in main for p in pixels),(name,i,'hand-detached',hx,hy)
                if key!='neutral':
                    assert len(pixels)==12,(name,i,'round hand shape',len(pixels))
                    assert set(im.getpixel(p) for p in pixels)=={INK,GOLD}
                hands.append(dict(box=[hx,hy,hx+4,hy+hand_h],opaque_pixels=len(pixels),connected_to_body=True,
                    shape='original neutral' if key=='neutral' else 'fingerless round ball 2/4/4/2',colors=2 if key!='neutral' else None))
            head_box,body_box,core_box=(HEAD_BASE,BODY_BASE,CORE_BASE) if key=='neutral' else identity_boxes(key)
            signatures={}
            for label,actual,reference in [('head',head_box,HEAD_BASE),('body',body_box,BODY_BASE),('heart',core_box,CORE_BASE)]:
                actual_pixels=im.crop(actual);reference_pixels=BASE.crop(reference)
                assert actual_pixels.tobytes()==reference_pixels.tobytes(),(name,i,label,'canonical identity drift')
                signatures[label]=dict(box=list(actual),rgba_sha256=csha(actual_pixels),reference_rgba_sha256=csha(reference_pixels),exact=True)
            records.append(dict(index=i,file=path.name,duration_ms=TIMES[name][i],source_key=key,
                pixel_edits=[[x,y,list(im.getpixel((x,y)))] for y in range(64) for x in range(64)
                    if im.getpixel((x,y))!=(BASE if key=='neutral' else keys[key]).getpixel((x,y))],rgba_sha256=csha(im),
                alpha_bounds=list(im.getbbox()),palette_colors=len(set(c for c in im.getdata() if c[3])),
                foreground_components_4_connected=list(map(len,gs)),hands=hands,identity=signatures))
        assert csha(frames[0])==csha(BASE) and csha(frames[-1])==csha(BASE)
        manifest=dict(clip=name,frame_size=[64,64],pixel_pivot=[32,56],durations_ms=TIMES[name],
            frame_count=12,neutral_endpoints_match_original=True,
            source_method='complete generated body action guide + source limb native tracing + explicit original head/body/core identity pixel correction + fingerless round hands',
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
        im,delta=correct_identity(im,n);traced[n]=im
        (NATIVE/(n+'-identity-delta.json')).write_text(json.dumps(dict(key=n,reference='unity/TiqueReturnPrototype/Assets/Resources/Return/Tique/Idle/00.png',
            corrections=delta,method='reference-restoring individual native pixels after full-body source trace; no band squeeze or crop composition'),indent=2),encoding='utf-8')
        patch(im,CLEANUP.get(n,[])); im.save(NATIVE/(n+'.png'))
        im.resize((512,512),Image.Resampling.NEAREST).save(NATIVE/(n+'-8x.png'))
    keys.update(traced)
    contact(list(keys.items()),SRC/'native-keys-contact-3x.png')
    qa=SRC/'DeformationReview';qa.mkdir(exist_ok=True)
    pairs=[]
    for n,im in keys.items():
        pairs.extend([('Original reference',BASE),(n+' fixed',im)])
    contact(pairs,qa/'original-vs-fixed-keys-3x.png',columns=4)
    records=[]
    for n,im in keys.items():
        path=SRC/'Generated'/(n+'.png')
        records.append(dict(key=n,source=path.relative_to(ROOT).as_posix(),source_sha256=sha(path),
            source_size=list(Image.open(path).size),native=NATIVE.joinpath(n+'.png').relative_to(ROOT).as_posix(),
            trace_landmarks=KEYS[n],native_rgba_sha256=csha(im),
            cleanup_pixels=sum(a!=b for a,b in zip(Image.open(NATIVE/(n+'-trace-raw.png')).convert('RGBA').getdata(),im.getdata())),
            source_hand_regions=[list(box) for box,at in HANDS[n]],
            hand_contours=[dict(native_box=[at[0],at[1],at[0]+4,at[1]+4],shape='fingerless round ball 2/4/4/2',colors=['INK','GOLD']) for at in ROUND_AT[n]],
            canonical_identity=dict(reference_head=HEAD_BASE,reference_body=BODY_BASE,reference_core=CORE_BASE,target_boxes=identity_boxes(n)),
            method='complete-body source pose trace, then original head/body/core restored by explicit native per-pixel correction and fingerless 4x4 hand contours'))
    (SRC/'trace-records.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    clips=export_clips(keys,only='Attack' if transition_only else None)
    if transition_only:clips.append(json.loads((ART/'Dash/manifest.json').read_text(encoding='utf-8')))
    (SRC/'validation.json').write_text(json.dumps(dict(generated_complete_body_keys=len(KEYS),
        rejected_sources=[],native_trace_keys=len(KEYS),frame_size=[64,64],palette=list(PAL),
        clips=[dict(name=c['clip'],frames=c['frame_count'],all_hands_visible_and_connected=c['all_hands_visible_and_connected'],neutral_endpoints_exact=True) for c in clips],
        binary_alpha=True,no_resampling_between_frames=True,
        original_identity_rgba_exact_in_all_frames=True,head_size=[31,27],body_size=[21,16],heart_size=[13,10],
        round_hands=dict(size=[4,4],silhouette=[2,4,4,2],colors=['INK','GOLD']),
        visual_review_status='pending strict final PNG/GIF exposure inspection after canonical identity correction',
        runtime_playback_review=False),indent=2),encoding='utf-8')

if __name__=='__main__':main()
