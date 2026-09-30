"""V9 full-pose image tracing for Jump and DoubleJump.

User explicitly requested individual whole-character image references and native
tracing. After the latest uniformity correction, complete images define motion
only; native reference-pixel repair locks the original rigid head/chest/heart.
Source shoulders, bent forearms, hips, knees and feet define each pose. No limb
cut-and-paste, stretched arms or duplicate arm rig is used. Sources are immutable.
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
    '07-recovery': (313, 921, 160, 685, 1093, 20),
    '08-double-tuck': (295, 990, 155, 697, 1055, 17),
    '09-double-release': (317, 936, 156, 693, 1074, 19),
    '10-near-neutral': (318, 921, 191, 715, 1090, 20),
    '11-half-fold': (315, 924, 162, 680, 1068, 19),
    '12-half-open': (313, 922, 156, 684, 1106, 20),
    '13-land-rise': (314, 928, 176, 705, 1093, 19),
    '14-boost-settle': (332, 914, 179, 680, 1083, 19),
    '15-land-impact': (318, 920, 245, 764, 1045, 18),
}

# Hand centers were measured on each WHOLE generated image. The user clarified
# that Tique has no fingers or thumbs: every new pose uses a 4x4 round endcap.
WAIST = {'01-preload':970,'02-extension':925,'03-ascent':950,'04-apex':923,
    '05-descent':934,'06-impact':973,'07-recovery':976,'08-double-tuck':950,
    '09-double-release':958,'10-near-neutral':996,'11-half-fold':941,
    '12-half-open':976,'13-land-rise':973,'14-boost-settle':947,'15-land-impact':975}
SOURCE_HANDS = {
    '01-preload':[(436,887),(840,904)],'02-extension':[(353,835),(910,835)],
    '03-ascent':[(355,770),(900,770)],'04-apex':[(371,805),(885,805)],
    '05-descent':[(372,827),(881,848)],'06-impact':[(322,815),(931,828)],
    '07-recovery':[(383,904),(879,897)],'08-double-tuck':[(383,780),(894,790)],
    '09-double-release':[(321,798),(987,822)],'10-near-neutral':[(399,888),(874,898)],
    '11-half-fold':[(373,817),(885,819)],'12-half-open':[(360,883),(900,881)],
    '13-land-rise':[(394,893),(865,893)],'14-boost-settle':[(397,812),(895,808)],
    '15-land-impact':[(469,896),(825,896)],
}
AIR_KEYS={'03-ascent','04-apex','05-descent','08-double-tuck','09-double-release',
    '11-half-fold','12-half-open','14-boost-settle'}

def native_top(name):
    return 8 if name in AIR_KEYS else 56-27-LANDMARKS[name][-1]

def hands_for(name):
    left,right,top,neck,sole,body_h=LANDMARKS[name]
    hands=[(round(16+(x-left)*31/(right-left)-1.5),
        round(native_top(name)+27+(y-neck)*15/(WAIST[name]-neck)-1.5))
        for x,y in SOURCE_HANDS[name]]
    return [(min(hands[0][0],19),hands[0][1]),(max(hands[1][0],44),hands[1][1])]

def clean_native_key(im, name, out_top):
    # User correction: references define motion, the original Tique defines
    # identity. Native per-pixel repair locks one rigid head/chest/heart. No
    # clipped parts, pasted limb patches or duplicate procedural arm strokes.
    # The full reference trace still supplies shoulders/arms/hips/knees/feet.
    dy=out_top-8
    for box in ((0,8,64,35),(23,34,44,50)):
        for y in range(box[1],box[3]):
            for x in range(box[0],box[2]):
                im.putpixel((x,y+dy),BASE.getpixel((x,y)))
    for y in range(out_top+27,out_top+42):
        for x in range(64):
            c=im.getpixel((x,y))
            if not (23<=x<44) and c[3] and c[1]>c[0]*1.4 and c[2]>c[0]*1.4:
                im.putpixel((x,y),BRASS)
    for side,(x,y) in enumerate(hands_for(name)):
        # Fingerless sphere: 2/4/4/2 silhouette, two-tone metal interior. Delete
        # source thumb/finger spurs around the hand rather than keeping them.
        for yy in range(-1,5):
            for xx in range(-1,5):
                if 0<=x+xx<64 and 0<=y+yy<64:
                    im.putpixel((x+xx,y+yy),CLEAR)
        rows=['.00.','0110','0110','.00.']
        colors={'0':INK,'1':GOLD}
        for yy,row in enumerate(rows):
            for xx,symbol in enumerate(row):
                im.putpixel((x+xx,y+yy),CLEAR if symbol=='.' else colors[symbol])
        # Reconnect only the immediately adjacent wrist pixels already present
        # in the full trace; never manufacture an extended arm.
        if side==1:
            for dx in (-1,-2):
                for dy_w in (1,2):im.putpixel((x+dx,y+dy_w),BRASS)
        elif name in ('03-ascent','08-double-tuck','09-double-release'):
            for dx in (4,5):
                for dy_w in (1,2):im.putpixel((x+dx,y+dy_w),BRASS)
        else:
            for dy_w in (-1,-2):
                for dx in (1,2):im.putpixel((x+dx,y+dy_w),BRASS)
    # Simplify isolated limb highlights into the same warm gold color.
    for y in range(out_top+28,56):
        for x in range(8,56):
            c=im.getpixel((x,y))
            if 23<=x<44 and out_top+26<=y<out_top+42:continue
            if c not in (LIGHT,WHITE) or any(hx<=x<hx+4 and hy<=y<hy+4 for hx,hy in hands_for(name)):
                continue
            around=[im.getpixel((x+dx,y+dy)) for dx,dy in ((-1,0),(1,0),(0,-1),(0,1))]
            if sum(q in (LIGHT,WHITE,GOLD) for q in around)==0:
                im.putpixel((x,y),GOLD)
    # Native repair is deliberately repeated after hand/limb cleanup so no
    # wrist can alter the fixed shell or heart at an overlap boundary.
    for box in ((0,8,64,35),(23,34,44,50)):
        for y in range(box[1],box[3]):
            for x in range(box[0],box[2]):im.putpixel((x,y+dy),BASE.getpixel((x,y)))
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
        metal=sum(im.getpixel((x+xx,y+yy)) in (GOLD,BRASS) for yy in range(4) for xx in range(4))
        attached=all((x+xx,y+yy) in main for yy in range(1,3) for xx in range(1,3))
        hands.append({'box':[x,y,x+4,y+4],'metalInteriorPixels':metal,'connectedToBody':attached,'shape':'fingerless 4x4 sphere, 2/4/4/2'})
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
        if len(group)<=3:
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
        elif y<out_top+head_h+15:
            sy0=neck+(y-out_top-head_h)*(WAIST[name]-neck)/15
            sy1=neck+(y-out_top-head_h+1)*(WAIST[name]-neck)/15
        else:
            sy0=WAIST[name]+(y-out_top-head_h-15)*(sole-WAIST[name])/(body_h-15)
            sy1=WAIST[name]+(y-out_top-head_h-14)*(sole-WAIST[name])/(body_h-15)
        for x in range(64):
            sx0=left+(x-16)*step_x
            sx1=sx0+step_x
            im.putpixel((x,y),source_vote(src,sx0,sy0,sx1,sy1))
    im=remove_strays(im)
    im.save(SOURCE/(name+'-trace-raw.png'))
    raw_pixels=list(im.getdata())
    im=clean_native_key(im,name,out_top)
    im.save(SOURCE/(name+'-native.png'))
    return im, {'name':name,'source':str((SOURCE/(name+'.png')).relative_to(ROOT)).replace('\\','/'),
        'sourceSha256':sha(SOURCE/(name+'.png')),'sourceSize':list(src.size),
        'sourceHeadBounds':[left,top,right,neck],'sourceSole':sole,
        'nativeHeadBounds':[16,out_top,47,out_top+27],'nativeBodyRows':body_h,
        'nativeSole':out_top+head_h+body_h,'pivotPixels':[32,56],
        'sourceWaist':WAIST[name],'handBounds':[[x,y,x+4,y+4] for x,y in hands_for(name)],
        'sourceHandCenters':SOURCE_HANDS[name],
        'nativeRepairChangedPixels':sum(a!=b for a,b in zip(raw_pixels,im.getdata())),
        'canonicalHeadChangedPixels':sum(im.getpixel((x,y+out_top-8))!=BASE.getpixel((x,y)) for y in range(8,35) for x in range(64)),
        'canonicalChestChangedPixels':sum(im.getpixel((x,y+out_top-8))!=BASE.getpixel((x,y)) for y in range(34,50) for x in range(23,44)),
        'canonicalHeartChangedPixels':sum(im.getpixel((x,y+out_top-8))!=BASE.getpixel((x,y)) for y in range(37,47) for x in range(30,43)),
        'registration':'head top8 and folded feet above pivot' if name in AIR_KEYS else 'soles fixed at56',
        'method':'complete source pose traced on head/waist/sole landmarks; per-native-pixel canonical head/chest/core repair; source limbs retained without duplicate arm lines; fingerless round hand contour repair'}

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
        top=8 if key_name=='idle' else native_top(key_name)
        dy=top-8
        invariant_deltas={label:sum(im.getpixel((x,y+dy))!=BASE.getpixel((x,y))
            for y in range(box[1],box[3]) for x in range(box[0],box[2]))
            for label,box in {'wholeHead':(0,8,64,35),'chest':(23,34,44,50),'heart':(30,37,43,47)}.items()}
        assert all(v==0 for v in invariant_deltas.values()),(name,i,'model drift')
        rows.append({'index':i,'file':path.name,'durationMs':TIMES[name][i],
            'sourceKey':key_name,'sha256':sha(path),'bounds':im.getbbox(),
            'opaquePixels':sum(c[3]>0 for c in pixels),'colors':len(colors),
            'headTop':top,'canonicalPixelDeltas':invariant_deltas})
        images.append((f'{i:02d} {key_name}',im))
    assert len(rows)==len(TIMES[name])
    (dest/'timing-manifest.json').write_text(json.dumps({'clip':name,'frameCount':len(rows),
        'durationsMs':TIMES[name],'durationMs':sum(TIMES[name]),'cell':[64,64],
        'pivotPixels':[32,56],'palette':PAL,'alpha':'binary','frames':rows},indent=2))
    contact(images,dest/'contact-3x.png')
    transitions=[]
    for i in range(1,len(images)):
        previous=images[i-1][1];current=images[i][1]
        transitions.append({'from':i-1,'to':i,
            'headVerticalShiftPixels':rows[i]['headTop']-rows[i-1]['headTop'],
            'wholeFrameChangedPixels':sum(a!=b for a,b in zip(previous.getdata(),current.getdata())),
            'headChestHeartModelChangedPixels':0,
            'sourceTransition':[rows[i-1]['sourceKey'],rows[i]['sourceKey']]})
    (dest/'transition-audit.json').write_text(json.dumps(transitions,indent=2))
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
    # Review the actual complete source images together, never a generated sheet.
    raw_contact=Image.new('RGBA',(4*256,((len(keys)+3)//4)*280),(19,27,34,255))
    raw_draw=ImageDraw.Draw(raw_contact)
    for i,name in enumerate(keys):
        src=Image.open(SOURCE/(name+'.png')).convert('RGBA')
        bounds=src.getchannel('A').point(lambda a:255 if a>=192 else 0).getbbox()
        sample=src.crop(bounds);sample.thumbnail((240,240),Image.Resampling.NEAREST)
        x=i%4*256;y=i//4*280
        raw_draw.text((x+8,y+4),name,fill=(255,231,163))
        raw_contact.alpha_composite(sample,(x+(256-sample.width)//2,y+28+(240-sample.height)//2))
    raw_contact.save(SOURCE/'generated-reference-contact.png')
    (SOURCE/'trace-provenance.json').write_text(json.dumps({'sources':provenance,
        'rejectedSources':[{'file':'01-preload-rejected-long-arms.png','reason':'left arm read as an extended rail; replaced with independently generated compact bent-arm preload'},
            {'file':'06-impact.png','reason':'source arms sit too high around head; independently regenerated compact landing with rigid torso and low round hands'}],
        'userAuthorization':'whole pose references for motion; original Tique identity fixed per latest user correction; no fingers, only small round ball hands',
        'generatedSingleImages':16,'activeFullPoseKeys':14,'newImagesForDeformationFix':6,
        'canonicalRanges':{'head':[0,8,64,35],'chest':[23,34,44,50],'heart':[30,37,43,47]},
        'handModel':'4x4 2/4/4/2 silhouette; INK outline plus GOLD face; wrist only, no thumb or fingers',
        'repairMethod':'whole-pose native trace followed by explicit original-reference pixel corrections; no limb cut-and-paste, no stretched arm, no added parallel arm rig',
        'beforeSnapshot':'JumpSource/BeforeDeformationFix',
        'neutralEndpoint':'exact original Idle/00.png','neutralSha256':sha(ORIGINAL/'Idle/00.png')},indent=2))
    (SOURCE/'pixel-audit.json').write_text(json.dumps(audit,indent=2))
    assert all(len(row['componentSizes'])==1 for row in audit), 'detached visible source pixels'
    assert all(h['connectedToBody'] and h['metalInteriorPixels']>=4 for row in audit for h in row['hands'])
    assert all(row['canonicalHeadChangedPixels']==0 and row['canonicalChestChangedPixels']==0 and row['canonicalHeartChangedPixels']==0 for row in provenance)
    expected_hand=[2,4,4,2]
    for name,key in keys.items():
        for hx,hy in hands_for(name):
            assert [sum(key.getpixel((hx+x,hy+y))[3]>0 for x in range(4)) for y in range(4)]==expected_hand,(name,'hand silhouette')
            assert {key.getpixel((hx+x,hy+y)) for y in range(4) for x in range(4) if key.getpixel((hx+x,hy+y))[3]}<={INK,GOLD},(name,'hand colors')
    write_clip('Jump',['idle','10-near-neutral','01-preload','02-extension','11-half-fold',
        '03-ascent','04-apex','12-half-open','05-descent','05-descent','15-land-impact',
        '13-land-rise','07-recovery','10-near-neutral','idle'],keys)
    write_clip('DoubleJump',['idle','11-half-fold','08-double-tuck','09-double-release',
        '14-boost-settle','03-ascent','04-apex','12-half-open','05-descent','15-land-impact',
        '13-land-rise','10-near-neutral','idle'],keys)
    print(json.dumps({'Jump':15,'DoubleJump':13,'completePoseSources':len(keys),
        'binaryAlpha':True,'original13ColorPalette':True,'pivotPixels':[32,56],
        'handAudit':audit}))

if __name__=='__main__':main()
