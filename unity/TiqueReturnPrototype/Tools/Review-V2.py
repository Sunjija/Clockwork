"""Checks preserved Tique bytes and native export constraints, not visual quality."""
from pathlib import Path
import json,hashlib
from PIL import Image
project=Path(__file__).resolve().parents[1]
repo=project.parents[1]
source=repo/'prototypes/tique-playground'
clips=json.loads((source/'Revisions/10/data.json').read_text(encoding='utf-8'))['clips']
count=0
for name,clip in clips.items():
    for i,path in enumerate(clip['frames']):
        a=(source/path).read_bytes();b=(project/f'Assets/Resources/Return/Tique/{name}/{i:02}.png').read_bytes()
        assert a==b,(name,i)
        count+=1
assert count==67,count
timings=json.loads((project/'Assets/Resources/Return/clips.json').read_text())['clips']
for c in timings:assert c['durations']==clips[c['name']]['durations']
root=project/'Assets/Resources/ReturnV2/Art'
palette=set();files=[]
for p in sorted(root.rglob('*.png')):
    im=Image.open(p).convert('RGBA');pixels=list(im.getdata())
    assert set(a for _,_,_,a in pixels).issubset({0,255}),p
    opaque={pixel[:3] for pixel in pixels if pixel[3]}
    if 'Warden' in p.parts:
        assert im.size==(192,144),p
        assert im.getbbox()[3]==132,(p,im.getbbox())
        assert im.getbbox()[0]>0 and im.getbbox()[2]<192,p
        assert len(opaque)<=32,p
        palette.update(opaque)
    if p.stem in ['arena','workshop']:assert im.size==(640,360) and len(opaque)<=48,p
    meta=p.with_suffix('.png.meta').read_text()
    for setting in ['filterMode: 0','enableMipMap: 0','textureCompression: 0']:assert setting in meta,(p,setting)
    files.append({'file':p.relative_to(project).as_posix(),'size':im.size,'colors':len(opaque),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
assert len(palette)<=32,len(palette)
assert len(files)==24,len(files)
result={'passed':True,'tiqueFramesByteExact':count,'tiqueTimingExact':True,'nativeAssetCount':len(files),'wardenSharedColors':len(palette),'binaryAlpha':True,'footBaseline':132,'pointNoMipsUncompressed':True,'scope':'File/metadata checks; does not certify visual animation quality','files':files}
(project/'QA/V2/asset-checks.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('PASS 67 Tique frames and timing exact; 24 native assets, shared boss palette, binary alpha, baseline and Unity import settings.')
