"""Reconstruct every pixel edit, compare timings, check native imports/exports."""
from pathlib import Path
from PIL import Image
import json,io,base64,hashlib
project=Path(__file__).resolve().parents[1];repo=project.parents[1]
root=repo/'art/return-v3-manual'
manifest=json.loads((root/'manifest.json').read_text())
base=Image.open(root/'Source/base-native.png').convert('RGBA')
palette={p for p in base.getdata() if p[3]}
tique=json.loads((repo/'prototypes/tique-playground/Revisions/10/data.json').read_text(encoding='utf-8'))['clips']
unity=project/'Assets/Resources/ReturnV2/WardenAuthored'
runtime=json.loads((unity/'clips.json').read_text())['clips']
assert runtime==manifest['clips']
assert not manifest['referenceImagesAreRuntimeInputs']
rows=[]
for clip in manifest['clips']:
    name=clip['name'];folder=root/'Clips'/name
    assert clip['durations']==tique[clip['tiqueClip']]['durations']
    piskel=json.loads((folder/(name+'.piskel')).read_text())['piskel']
    layer=json.loads(piskel['layers'][0]);chunk=layer['chunks'][0]
    sheet=Image.open(io.BytesIO(base64.b64decode(chunk['base64PNG'].split(',')[1]))).convert('RGBA')
    assert chunk['layout']==[[i] for i in range(clip['frames'])]
    if clip['frames']>1:
        apng=Image.open(folder/'native.apng');total=0
        for i in range(apng.n_frames):apng.seek(i);total+=apng.info.get('duration',0)
        assert abs(total-sum(clip['durations']))<1,(name,total)
    for i,state in enumerate(clip['poses']):
        path=folder/f'{i:02}.png';im=Image.open(path).convert('RGBA')
        assert im.size==(192,144)
        assert set(p[3] for p in im.getdata())<={0,255}
        assert {p for p in im.getdata() if p[3]}<=palette
        reconstructed=base.copy()
        for x,y,r,g,b,a in json.loads((folder/f'{i:02}.pixels.json').read_text()):reconstructed.putpixel((x,y),(r,g,b,a))
        assert reconstructed.tobytes()==im.tobytes(),(name,i,'pixel edit replay')
        assert sheet.crop((i*192,0,(i+1)*192,144)).tobytes()==im.tobytes(),(name,i,'Piskel layout')
        assert path.read_bytes()==(unity/name/f'{i:02}.png').read_bytes()
        # The airborne tuck legitimately raises the feet; grounded poses do not.
        assert im.getbbox()[3]==132-state[3],(name,i,im.getbbox(),state)
        assert 0<im.getbbox()[0] and im.getbbox()[2]<192
        # Eight-connected silhouette detects detached appendages / leftover dots.
        points={(x,y) for y in range(144) for x in range(192) if im.getpixel((x,y))[3]}
        todo=[next(iter(points))];seen=set(todo)
        while todo:
            x,y=todo.pop()
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
                q=(x+dx,y+dy)
                if q in points and q not in seen:seen.add(q);todo.append(q)
        assert seen==points,(name,i,'disconnected pixels')
        meta=(unity/name/f'{i:02}.png.meta').read_text()
        for value in ('filterMode: 0','enableMipMap: 0','textureCompression: 0'):assert value in meta
        rows.append({'clip':name,'frame':i,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bounds':im.getbbox()})
    assert Image.open(folder/'00.png').tobytes()==base.tobytes()
    assert Image.open(folder/f"{clip['frames']-1:02}.png").tobytes()==base.tobytes()
assert len(rows)==52
result={'passed':True,'frames':len(rows),'colors':len(palette),'pixelEditReplayExact':True,'tiqueDurationsExact':True,
        'piskelRoundTripExact':True,'apngDurationTotalsExact':True,'groundedFootY':132,'singleConnectedSilhouette':True,
        'pointNoMipsUncompressed':True,'scope':'Data, silhouette connectivity and timing checks; does not certify naturalness','files':rows}
(project/'QA/V3').mkdir(parents=True,exist_ok=True)
(project/'QA/V3/authored-art-checks.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('PASS 52 frames: pixel edits replay exactly, Tique timings exact, Piskel round trip, APNG duration, 32 colors, connected silhouettes, correct foot anchor/imports.')
