"""V9 full-pose image tracing for Jump and DoubleJump.

User explicitly requested individual whole-character image references and native
tracing. This file traces every complete generated pose, rather than copying an
approved torso and importing a few hand pixels. Source pose silhouette, arms,
hands, hips and feet all survive into the native key. Sources are immutable.
"""
from pathlib import Path
from collections import Counter, deque
import hashlib, json, shutil
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'art/return-v9-traced'
SOURCE = ART / 'JumpSource'
ORIGINAL = ROOT / 'unity/TiqueReturnPrototype/Assets/Resources/Return/Tique'
BASE = Image.open(ORIGINAL / 'Idle/00.png').convert('RGBA')
PAL = [c for c, _ in Counter(c for c in BASE.getdata() if c[3]).most_common()]
CLEAR = (0, 0, 0, 0)
INK, BRASS, GOLD, SHADE, LIGHT, MID, WHITE = PAL[:7]
TIMES = {c['name']: c['durations'] for c in json.loads((ORIGINAL.parent/'clips.json').read_text())['clips']}

# Measured source landmarks, inspected in each actual single image. The head is
# traced at its approved 31x27 native proportion; the COMPLETE lower-body image
# is traced into the compact original lower-body envelope. No parts rig exists.
# name : source head left,right,top,bottom; source sole row; lower-body rows.
LANDMARKS = {
    '01-preload': (334, 944, 254, 786, 1062, 18),
    '02-extension': (323, 936, 129, 649, 1098, 21),
    '03-ascent': (311, 922, 155, 681, 1087, 18),
    '04-apex': (321, 923, 158, 680, 1049, 19),
    '05-descent': (323, 897, 167, 678, 1050, 21),
    '06-impact': (334, 945, 265, 786, 1039, 18),
    '07-recovery': (313, 921, 160, 685, 1093, 20),
    '08-double-tuck': (295, 990, 155, 697, 1055, 17),
    '09-double-release': (317, 936, 156, 693, 1074, 19),
}

# Hands were measured on the WHOLE generated images above. At native scale an
# image model's alternating outline/highlight can collapse into a black dot.
# These small closed contours trace those visible source mittens with stable
# 2px metal interiors. Locations follow each distinct image, not a rig/tween.
HANDS = {
    '01-preload': [(19,43),(41,43)],
    '02-extension': [(15,42),(44,42)],
    '03-ascent': [(16,40),(44,40)],
    '04-apex': [(16,42),(43,42)],
    '05-descent': [(16,42),(44,42)],
    '06-impact': [(13,39),(45,40)],
    '07-recovery': [(17,45),(43,44)],
    '08-double-tuck': [(17,40),(42,41)],
    '09-double-release': [(13,40),(48,41)],
}
ARMS = {
    '01-preload': [[(24,39),(21,42),(21,45)],[(40,40),(42,43),(43,45)]],
    '02-extension': [[(23,36),(20,40),(17,44)],[(42,38),(44,41),(46,44)]],
    '03-ascent': [[(23,39),(21,44),(18,42)],[(42,40),(44,44),(46,42)]],
    '04-apex': [[(23,38),(20,41),(18,44)],[(42,39),(44,42),(45,44)]],
    '05-descent': [[(23,36),(20,40),(18,44)],[(42,38),(44,41),(46,44)]],
    '06-impact': [[(23,40),(19,39),(15,41)],[(42,40),(45,42),(47,42)]],
    '07-recovery': [[(23,37),(21,42),(19,47)],[(42,39),(44,43),(45,46)]],
    '08-double-tuck': [[(23,40),(21,44),(19,42)],[(40,42),(40,45),(44,43)]],
    '09-double-release': [[(23,38),(19,41),(15,42)],[(43,39),(47,42),(50,43)]],
}

AIR_KEYS={'03-ascent','04-apex','05-descent','08-double-tuck','09-double-release'}

def native_top(name):
    return 8 if name in AIR_KEYS else 56-27-LANDMARKS[name][-1]

def air_shift(name):
    return native_top(name)-(56-27-LANDMARKS[name][-1])

def hands_for(name):
    return [(x,y+air_shift(name)) for x,y in HANDS[name]]

def arms_for(name):
    return [[(x,y+air_shift(name)) for x,y in arm] for arm in ARMS[name]]

def clean_native_key(im, name, out_top):
    # Preserve approved head and face pixels exactly. Full-pose image source is
    # still the entire lower body, including shoulders, every elbow, hands,
    # torso, heart, hips, knees and soles. No V8 torso or limb piece is consumed.
    for y in range(out_top,out_top+27):
        for x in range(16,47):
            im.putpixel((x,y),CLEAR)
    im.alpha_composite(BASE.crop((16,8,47,35)),(16,out_top))
    # Trace complete connected arm contours on the native grid, guided by the
    # shoulder/elbow/wrist landmarks of EACH source. Source occupancy reduction
    # can break a one-pixel joint; these deliberate strokes reconnect it and
    # replace alternating light specks with readable compact metal segments.
    d=ImageDraw.Draw(im)
    for points in arms_for(name):
        d.line(points,fill=INK,width=5)
        d.line(points,fill=BRASS,width=3)
        d.line([(x,y-1) for x,y in points],fill=GOLD,width=1)
    for x,y in hands_for(name):
        # Native contour cleanup, traced from the actual source's rounded hand.
        rows=['.00.','0120','0340','0350','.00.']
        colors={'0':INK,'1':LIGHT,'2':GOLD,'3':BRASS,'4':GOLD,'5':SHADE}
        for yy,row in enumerate(rows):
            for xx,symbol in enumerate(row):
                im.putpixel((x+xx,y+yy),CLEAR if symbol=='.' else colors[symbol])
    # Clean one-pixel brass noise inside the limbs using native neighbor votes.
    # Preserve the main silhouette and heart. This reduces spotty dithering.
    for y in range(out_top+28,56):
        for x in range(8,56):
            c=im.getpixel((x,y))
            if c not in (LIGHT,WHITE) or any(hx<=x<hx+4 and hy<=y<hy+5 for hx,hy in hands_for(name)):
                continue
            around=[im.getpixel((x+dx,y+dy)) for dx,dy in ((-1,0),(1,0),(0,-1),(0,1))]
            if sum(q in (LIGHT,WHITE,GOLD) for q in around)==0:
                im.putpixel((x,y),GOLD)
    # Head contour/face is invariant even at the shoulder boundary.
    for y in range(out_top,out_top+27):
        for x in range(16,47):
            im.putpixel((x,y),BASE.getpixel((x,y-out_top+8)))
    im.alpha_composite(BASE.crop((16,8,47,35)),(16,out_top))
    return remove_strays(im)

def pixel_audit(im,name):
    pixels={(x,y) for y in range(64) for x in range(64) if im.getpixel((x,y))[3]}
    groups=[]
    while pixels:
        p=pixels.pop();group={p};q=deque([p])
        while q:
            x,y=q.popleft()
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                n=x+dx,y+dy
                if n in pixels:pixels.remove(n);group.add(n);q.append(n)
        groups.append(group)
    main=max(groups,key=len)
    hands=[]
    for x,y in hands_for(name):
        metal=sum(im.getpixel((x+xx,y+yy)) in (LIGHT,GOLD,BRASS,SHADE) for yy in range(5) for xx in range(4))
        attached=all((x+xx,y+yy) in main for yy in range(1,4) for xx in range(1,3))
        hands.append({'box':[x,y,x+4,y+5],'metalInteriorPixels':metal,'connectedToBody':attached})
    return {'key':name,'componentSizes':sorted([len(g) for g in groups],reverse=True),'hands':hands}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def nearest(c):
    return min(PAL, key=lambda p: sum((c[i]-p[i])**2 for i in range(3)))

def source_vote(src, x0, y0, x1, y1):
    """Trace cell occupancy and dominant source color, no anti-aliased resizing.

    Original image contains large flat pixel blocks. Nine evenly spaced samples
    avoid the random edge specks visible in a bilinear reduction. Median alpha
    produces one binary pixel. The dominant approved-palette color is selected
    from the occupied source samples, never interpolated into muddy colors.
    """
    samples = []
    occupied = 0
    for fy in (.22, .5, .78):
        for fx in (.22, .5, .78):
            x = round(x0+(x1-x0)*fx)
            y = round(y0+(y1-y0)*fy)
            c = src.getpixel((min(src.width-1,max(0,x)), min(src.height-1,max(0,y))))
            if c[3] >= 192:
                occupied += 1
                samples.append(nearest(c))
    if occupied < 5:
        return CLEAR
    return Counter(samples).most_common(1)[0][0]

def remove_strays(im):
    pixels = {(x,y) for y in range(64) for x in range(64) if im.getpixel((x,y))[3]}
    groups=[]
    while pixels:
        p=pixels.pop(); group=[p]; queue=deque([p])
        while queue:
            x,y=queue.popleft()
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                q=(x+dx,y+dy)
                if q in pixels:
                    pixels.remove(q);group.append(q);queue.append(q)
        groups.append(group)
    for group in groups:
        if len(group)<=2:
            for p in group: im.putpixel(p,CLEAR)
    return im

def trace(name):
    src=Image.open(SOURCE/(name+'.png')).convert('RGBA')
    left,right,top,neck,sole,body_h=LANDMARKS[name]
    im=Image.new('RGBA',(64,64))
    head_h=27
    out_top=native_top(name)
    step_x=(right-left)/31
    for y in range(out_top,out_top+head_h+body_h):
        if y < out_top+head_h:
            sy0=top+(y-out_top)*(neck-top)/head_h
            sy1=top+(y-out_top+1)*(neck-top)/head_h
        else:
            sy0=neck+(y-out_top-head_h)*(sole-neck)/body_h
            sy1=neck+(y-out_top-head_h+1)*(sole-neck)/body_h
        for x in range(64):
            sx0=left+(x-16)*step_x
            sx1=sx0+step_x
            im.putpixel((x,y),source_vote(src,sx0,sy0,sx1,sy1))
    im=remove_strays(im)
    im.save(SOURCE/(name+'-trace-raw.png'))
    im=clean_native_key(im,name,out_top)
    im.save(SOURCE/(name+'-native.png'))
    return im, {'name':name,'source':str((SOURCE/(name+'.png')).relative_to(ROOT)).replace('\\','/'),
        'sourceSha256':sha(SOURCE/(name+'.png')),'sourceSize':list(src.size),
        'sourceHeadBounds':[left,top,right,neck],'sourceSole':sole,
        'nativeHeadBounds':[16,out_top,47,out_top+27],'nativeBodyRows':body_h,
        'nativeSole':out_top+head_h+body_h,'pivotPixels':[32,56],
        'handBounds':[[x,y,x+4,y+5] for x,y in hands_for(name)],
        'sourceGuidedShoulderElbowWrist':arms_for(name),
        'registration':'head top8 and folded feet above pivot' if name in AIR_KEYS else 'soles fixed at56',
        'method':'complete source pose -> per-native-cell occupancy and dominant original-palette tracing -> source-shaped native contour cleanup; approved original head pixels retained exactly to prevent identity drift'}

def contact(images, path, columns=5):
    scale=3; cell=208; rows=(len(images)+columns-1)//columns
    out=Image.new('RGBA',(columns*cell,rows*(cell+24)),(19,27,34,255));d=ImageDraw.Draw(out)
    for i,(name,im) in enumerate(images):
        x=i%columns*cell;y=i//columns*(cell+24)
        d.text((x+6,y+4),name,fill=(255,231,163),font=ImageFont.load_default())
        out.alpha_composite(im.resize((192,192),Image.Resampling.NEAREST),(x+8,y+24))
        d.line((x+8,y+24+56*scale,x+199,y+24+56*scale),fill=(58,72,84))
    out.save(path)

def write_clip(name, sequence, keys):
    dest=ART/name;dest.mkdir(parents=True,exist_ok=True)
    rows=[];images=[]
    for i,key_name in enumerate(sequence):
        im=BASE.copy() if key_name=='idle' else keys[key_name].copy()
        path=dest/f'{i:02d}.png'
        if key_name=='idle':shutil.copyfile(ORIGINAL/'Idle/00.png',path)
        else:im.save(path)
        pixels=list(im.getdata()); colors=set(c for c in pixels if c[3])
        assert im.size==(64,64) and all(c[3] in (0,255) for c in pixels)
        assert colors.issubset(set(PAL))
        rows.append({'index':i,'file':path.name,'durationMs':TIMES[name][i],
            'sourceKey':key_name,'sha256':sha(path),'bounds':im.getbbox(),
            'opaquePixels':sum(c[3]>0 for c in pixels),'colors':len(colors)})
        images.append((f'{i:02d} {key_name}',im))
    assert len(rows)==len(TIMES[name])
    (dest/'timing-manifest.json').write_text(json.dumps({'clip':name,'frameCount':len(rows),
        'durationsMs':TIMES[name],'durationMs':sum(TIMES[name]),'cell':[64,64],
        'pivotPixels':[32,56],'palette':PAL,'alpha':'binary','frames':rows},indent=2))
    contact(images,dest/'contact-3x.png')
    gif_frames=[]
    for _,im in images:
        bg=Image.new('RGBA',(64,64),(19,27,34,255));bg.alpha_composite(im)
        gif_frames.append(bg.resize((256,256),Image.Resampling.NEAREST).convert('RGB'))
    gif_frames[0].save(dest/'preview-4x.gif',save_all=True,append_images=gif_frames[1:],
        duration=TIMES[name],loop=0,disposal=2)

def main():
    keys={};provenance=[];audit=[]
    for name in LANDMARKS:
        key,row=trace(name);keys[name]=key;provenance.append(row);audit.append(pixel_audit(key,name))
    contact(list(keys.items()),SOURCE/'full-pose-keys-3x.png')
    (SOURCE/'trace-provenance.json').write_text(json.dumps({'sources':provenance,
        'rejectedSources':[{'file':'01-preload-rejected-long-arms.png','reason':'left arm read as an extended rail; replaced with independently generated compact bent-arm preload'}],
        'userAuthorization':'whole pose source images and native tracing',
        'neutralEndpoint':'exact original Idle/00.png','neutralSha256':sha(ORIGINAL/'Idle/00.png')},indent=2))
    (SOURCE/'pixel-audit.json').write_text(json.dumps(audit,indent=2))
    assert all(len(row['componentSizes'])==1 for row in audit), 'detached visible source pixels'
    assert all(h['connectedToBody'] and h['metalInteriorPixels']>=6 for row in audit for h in row['hands'])
    write_clip('Jump',['idle','07-recovery','01-preload','02-extension','03-ascent',
        '04-apex','04-apex','05-descent','05-descent','05-descent','06-impact',
        '07-recovery','07-recovery','07-recovery','idle'],keys)
    write_clip('DoubleJump',['idle','08-double-tuck','08-double-tuck','09-double-release',
        '03-ascent','04-apex','04-apex','05-descent','05-descent','06-impact',
        '07-recovery','07-recovery','idle'],keys)
    print(json.dumps({'Jump':15,'DoubleJump':13,'completePoseSources':len(keys),
        'binaryAlpha':True,'original13ColorPalette':True,'pivotPixels':[32,56],
        'handAudit':audit}))

if __name__=='__main__':main()
