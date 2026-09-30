"""Inspect the already authored native files; never alter animation PNGs."""
from PIL import Image, ImageDraw
from pathlib import Path
from collections import Counter
import json, hashlib

run = Path(__file__).resolve().parent
art = run.parent
root = art.parents[1]
original = root/'unity/TiqueReturnPrototype/Assets/Resources/Return/Tique/Idle/00.png'
base = Image.open(original).convert('RGBA')
palette = [c for c,n in Counter(base.getdata()).most_common() if c[3]]
metals = set(palette[1:3]+palette[4:7])
cyan = set(palette[7:12])
rows, tiles, close, gifrows = [], [], [], []
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))

for clip in ['Attack','Dash']:
    manifest = read(art/clip/'manifest.json')
    frames = []
    for f in manifest['frames']:
        path = art/clip/f['file']
        im = Image.open(path).convert('RGBA')
        frames.append(im)
        assert im.size == (64,64)
        assert all(c[3] in (0,255) for c in im.getdata())
        assert set(c for c in im.getdata() if c[3]).issubset(set(palette))
        assert f['sha256'] == sha(path) and len(f['components4']) == 1
        if f['index'] in [0,11]: assert path.read_bytes() == original.read_bytes()
        heart = [(x,y) for y in range(35,50) for x in range(24,44) if im.getpixel((x,y)) in cyan]
        handinfo = []
        for hx,hy in f['hands']:
            cap = {(hx+x,hy+y) for y in range(5) for x in range(5) if im.getpixel((hx+x,hy+y))[3]}
            wrist = set()
            for x,y in cap:
                for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                    p = x+dx,y+dy
                    inside = hx <= p[0] < hx+5 and hy <= p[1] < hy+5
                    if p not in cap and not inside and im.getpixel(p) in metals: wrist.add(p)
            assert len(cap) == 21 and len(wrist) >= 2, (clip,f['index'],hx,hy,wrist)
            handinfo.append({'at':[hx,hy],'opaquePixels':21,'metalWristNeighbors':sorted(wrist)})
            close.append((f'{clip} {f["index"]:02} {len(handinfo)}', im.crop((hx-5,hy-5,hx+10,hy+10)).resize((120,120),Image.Resampling.NEAREST)))
        rows.append({'clip':clip,'frame':f['index'],'sha256':sha(path),'cyanHeartVisiblePixels':len(heart),
                     'cyanHeartBounds':[min(x for x,y in heart),min(y for x,y in heart),max(x for x,y in heart)+1,max(y for x,y in heart)+1], 'hands':handinfo})
        tiles.append((f'{clip} {f["index"]:02}',im.resize((320,320),Image.Resampling.NEAREST)))
    gif = Image.open(art/clip/'preview-4x.gif')
    assert gif.n_frames == 12
    actual = []
    for i in range(gif.n_frames):
        gif.seek(i)
        assert gif.convert('RGBA').tobytes() == frames[i].resize((256,256),Image.Resampling.NEAREST).tobytes(), (clip,i,'GIF pixel drift')
        actual.append(gif.info['duration'])
        if clip == 'Dash':
            ghost = Image.open(art/'dash-ghost'/f'{i:02}.png').convert('RGBA')
            assert ghost.getchannel('A').tobytes() == frames[i].getchannel('A').tobytes()
    gifrows.append({'clip':clip,'frameCount':12,'durations_ms':actual,'duration_ms':sum(actual),'pixelsExactlyMatchPngAt4x':True})
    assert actual == manifest['gif_durations_ms'] and sum(actual) == manifest['duration_ms']
    out = Image.new('RGBA',(1024,3*280),(19,27,34,255))
    d = ImageDraw.Draw(out)
    for i in range(gif.n_frames):
        gif.seek(i); x=i%4*256; y=i//4*280
        d.text((x+4,y+4),f'{clip} GIF {i:02} {gif.info["duration"]}ms',fill=(255,231,163))
        out.alpha_composite(gif.convert('RGBA'),(x,y+24))
    out.save(run/f'{clip.lower()}-decoded-gif-4x.png')

for name,items,w,h,columns,bg in [
    ('all-actual-frames-5x.png',tiles,320,344,4,(19,27,34,255)),
    ('hands-final-8x.png',close,120,144,8,(185,193,197,255))]:
    out=Image.new('RGBA',(columns*w,((len(items)+columns-1)//columns)*h),bg)
    d=ImageDraw.Draw(out)
    for n,(label,im) in enumerate(items):
        x=n%columns*w;y=n//columns*h
        d.text((x+4,y+4),label,fill=(255,231,163) if name.startswith('all') else (0,0,0))
        out.alpha_composite(im,(x,y+24))
    out.save(run/name)

provenance=read(run/'generation-provenance.json')
for rec in provenance['records']:
    p=run/rec['preserved_file'];rec['preserved_sha256']=sha(p)
    assert sha(Path(rec['generated_file'])) == sha(p)
provenance['canonical_reference_sha256']=sha(art/'canonical-reference-16x.png')
provenance['palette_lock_sha256']=sha(run/'palette.lock.json')
(run/'generation-provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf-8')
checks={'frames':rows,'gifExposureChecks':gifrows,'assertions':[
    '24 PNGs: 64x64, binary alpha, original13-color subset, single4-neighborcomponent',
    '40 new hands: shared5x5/21-pixel round sphere, >=2 directly adjacent metal wristpixels',
    '4 neutral endpoints: originalfile byte equal',
    '12 ghostalphas: exactcorrespondingDashalphas',
    'Both decodedGIFs:12exposures pixelidentical tocorresponding4xPNG, full originalduration'],
    'heartNote':'Canonical41-pixelcyan/8x7mask. Attack06 shows38pixels because roundhand/forearm intentionally occludes3topcyan points. Other23frames show41. No chestrectangle replacement.',
    'runtimeNaturalness':'pending root runtime review'}
(run/'native-checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
freeze={'status':'PNG freeze; QA document updates may follow','clips':{'Attack':{'frames':12,'duration_ms':460},'Dash':{'frames':12,'duration_ms':440}},
        'frameFingerprints':[{k:q[k] for k in ['clip','frame','sha256']} for q in rows],
        'ghostFingerprints':[{'frame':i,'sha256':sha(art/'dash-ghost'/f'{i:02}.png')} for i in range(12)],
        'authorScriptSha256':sha(root/'tools/art/author_tique_actions_v10.py')}
(run/'png-freeze.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
print(json.dumps({'PNGfreeze':True,'frameCount':len(rows),'newHands':len(close),
    'heartVisibleCounts':[q['cyanHeartVisiblePixels'] for q in rows],
    'minimumMetalWristNeighbors':min(len(h['metalWristNeighbors']) for q in rows for h in q['hands']),
    'GIF':gifrows}))
