"""Validate state exports, exact replay, timing, fixed gates and background geometry."""
from pathlib import Path
from PIL import Image
import json,hashlib,io,base64
project=Path(__file__).resolve().parents[1];repo=project.parents[1]
root=repo/'art/return-v4-states';out=project/'Assets/Resources/ReturnV2/StateArt'
manifest=json.loads((root/'manifest.json').read_text());clips=manifest['clips'];palette={tuple(c) for c in manifest['palette']}
tique=json.loads((repo/'prototypes/tique-playground/Revisions/10/data.json').read_text(encoding='utf-8'))['clips']
assert json.loads((out/'clips.json').read_text())['clips']==clips
assert manifest['generatedAnimationStripsUsed'] is False
files=[]
for c in clips:
    folder=root/'Clips'/c['name'];base=Image.open(folder/'00.png').convert('RGBA');times=c['durations']
    if c['tiqueTiming']:assert times==tique[c['tiqueTiming']]['durations']
    for i in range(len(times)):
        path=folder/f'{i:02}.png';im=Image.open(path).convert('RGBA')
        assert im.size==(c['width'],c['height'])
        assert {p[3] for p in im.getdata()}<={0,255}
        opaque={p[:3] for p in im.getdata() if p[3]}
        if c['name']=='warden-powered-down':
            original=Image.open(repo/'art/return-v3-manual/Clips/stagger/06.png').convert('RGBA')
            assert opaque<={p[:3] for p in original.getdata() if p[3]}
            assert im.getchannel('A').tobytes()==original.getchannel('A').tobytes()
        elif im.width<640:assert opaque<=palette,(c['name'],i,opaque-palette)
        else:assert len(opaque)<=64
        replay=base.copy()
        for x,y,r,g,b,a in json.loads((folder/f'{i:02}.pixels.json').read_text()):replay.putpixel((x,y),(r,g,b,a))
        assert replay.tobytes()==im.tobytes(),(c['name'],i,'pixel replay')
        assert path.read_bytes()==(out/c['name']/f'{i:02}.png').read_bytes()
        if c['name'].startswith('pylon-'):assert im.getbbox()[3]==60
        if c['name'].startswith('exit-'):assert im.getbbox()[3]==96
        meta=(out/c['name']/f'{i:02}.png.meta').read_text()
        for value in ('filterMode: 0','enableMipMap: 0','textureCompression: 0'):assert value in meta
        files.append({'state':c['name'],'frame':i,'size':im.size,'colors':len(opaque),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    if len(times)>1:
        apng=Image.open(folder/'native.apng');total=0
        for i in range(apng.n_frames):apng.seek(i);total+=apng.info['duration']
        assert abs(total-sum(times))<1
        p=json.loads((folder/(c['name']+'.piskel')).read_text())['piskel'];layer=json.loads(p['layers'][0]);chunk=layer['chunks'][0]
        assert chunk['layout']==[[i] for i in range(len(times))]
        sheet=Image.open(io.BytesIO(base64.b64decode(chunk['base64PNG'].split(',')[1]))).convert('RGBA')
        for i in range(len(times)):
            assert sheet.crop((i*base.width,0,(i+1)*base.width,base.height)).tobytes()==Image.open(folder/f'{i:02}.png').convert('RGBA').tobytes()
# All opening frames keep the same jambs, threshold and alpha silhouette.
closed=Image.open(out/'exit-locked/00.png').convert('RGBA')
for path in (out/'exit-opening').glob('*.png'):
    im=Image.open(path).convert('RGBA');assert im.getchannel('A').tobytes()==closed.getchannel('A').tobytes()
    for box in [(0,0,17,96),(48,0,64,96),(0,91,64,96)]:assert im.crop(box).tobytes()==closed.crop(box).tobytes()
# Lighting changes only specified fixtures; neither geometry nor full-image tint changes.
old=project/'Assets/Resources/ReturnV2/Art'
for c in clips:
    name=c['name']
    if not (name.startswith('workshop-') or name.startswith('arena-')):continue
    im=Image.open(out/name/'00.png').convert('RGBA');original=Image.open(old/('workshop.png' if name.startswith('workshop') else 'arena.png')).convert('RGBA')
    changed=0
    for y in range(360):
        for x in range(640):
            if im.getpixel((x,y))==original.getpixel((x,y)):continue
            changed+=1
            if name.startswith('workshop'):allowed=53<=y<=60 and any(a<=x<=a+14 for a in (282,314,346))
            else:
                allowed=any(abs(x-a)<=2 and b-4<=y<=b+5 for a,b in [(62,82),(220,143),(420,143),(578,83),(77,171),(562,173)])
                allowed|=261<=y<=279 and any(a<=x<=a+1 for a in (285,319,352))
                allowed|=y==281 and any(a<=x<=a+20 for a in (244,306,368))
            assert allowed,(name,x,y,'unexpected background alteration')
    assert changed<700,(name,changed)
assert len(clips)==37 and len(files)==187
report={'passed':True,'states':37,'frames':187,'propPaletteColors':len(palette),'binaryAlpha':True,'pixelReplayExact':True,'timingsMatchTique':True,
        'piskelRoundTripExact':True,'apngTotalTimesExact':True,'doorJambsFixed':True,'backgroundChangesOnlyAtFixtures':True,'pointNoMipsUncompressed':True,
        'scope':'Native exports and structural/timing invariants; not subjective art approval','files':files}
(project/'QA/V4').mkdir(parents=True,exist_ok=True)
(project/'QA/V4/state-art-checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PASS 37 states / 187 frames: exact pixels/timing/Piskel/APNG, fixed gate/frame/background, native palette, alpha and imports.')
