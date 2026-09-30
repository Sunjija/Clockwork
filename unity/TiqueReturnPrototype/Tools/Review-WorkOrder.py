"""Checks immutable originals, exact pixel exports, OFL glyph atlas and integer captures."""
from pathlib import Path
import json,hashlib,sys
from PIL import Image
P=Path(__file__).resolve().parents[1];R=P.parents[1];Q=P/'QA/WorkOrderV01';F=P/'Assets/Resources/ReturnV2/Feedback'
old=json.loads((Q/'original-sha256.json').read_text(encoding='utf-8'))
changed=[n for n,h in old.items() if hashlib.sha256((R/n).read_bytes()).hexdigest()!=h]
assert not changed,changed
clips=json.loads((F/'clips.json').read_text(encoding='utf-8'))['clips'];frames=0
artRoot=R/'art/return-v5-feedback'
imageMap=json.loads((artRoot/'source-image-map.json').read_text(encoding='utf-8'))
for row in imageMap:
    source=artRoot/'Source/Concepts'/row['source']
    assert source.exists() and hashlib.sha256(source.read_bytes()).hexdigest()==row['sourceSha256']
clipMap=json.loads((artRoot/'clip-source-map.json').read_text(encoding='utf-8'))
assert set(clipMap)=={c['name'] for c in clips}
def connected(im):
    a=im.getchannel('A');remaining={(x,y) for y in range(im.height) for x in range(im.width) if a.getpixel((x,y))};count=0
    while remaining:
        count+=1;todo=[remaining.pop()]
        while todo:
            x,y=todo.pop()
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    p=(x+dx,y+dy)
                    if p in remaining:remaining.remove(p);todo.append(p)
    return count
for name in ['push-side','push-up','push-down']:
    for i in range(14):
        im=Image.open(F/name/f'{i:02}.png').convert('RGBA');base=Image.open(P/f'Assets/Resources/Return/Tique/Walk/{i:02}.png').convert('RGBA')
        assert im.crop((0,0,64,33)).tobytes()==base.crop((0,0,64,33)).tobytes(),(name,i,'head changed')
        assert im.crop((0,48,64,64)).tobytes()==base.crop((0,48,64,64)).tobytes(),(name,i,'feet changed')
        assert connected(im)==1,(name,i,'detached pixel component')
for c in clips:
    assert len(c['durations'])==len(list((F/c['name']).glob('*.png')))
    for i in range(len(c['durations'])):
        im=Image.open(F/c['name']/f'{i:02}.png').convert('RGBA');assert im.size==(c['width'],c['height']);assert set(im.getchannel('A').getdata())<={0,255};frames+=1
    source=R/'art/return-v5-feedback/Clips'/c['name'];assert (source/(c['name']+'.piskel')).exists()
    if len(c['durations'])>1:assert (source/'native.apng').exists()
f=json.loads((F/'font.json').read_text(encoding='utf-8'));atlas=Image.open(F/'font.png');assert len(set(f['characters']))==len(f['characters'])
for i,c in enumerate(f['characters']):
    if c==' ':continue
    box=atlas.crop((i%32*16,i//32*16,(i%32+1)*16,(i//32+1)*16));assert box.getbbox(),repr(c)
assert 'SIL OPEN FONT LICENSE Version 1.1' in (F/'FONT-LICENSE.txt').read_text(encoding='utf-8')
captures=[]
for folder in ['Runtime720Accepted','Runtime1080','RuntimeNonInteger']:
    directory=Q/folder
    if not (directory/'result.json').exists():continue
    result=json.loads((directory/'result.json').read_text(encoding='utf-8'));assert result['passed'],folder
    for file in directory.glob('*.png'):
        im=Image.open(file).convert('RGB');w,h=im.size;s=min(w//640,h//360);ox=(w-640*s)//2;oy=(h-360*s)//2
        # Nearest integer viewport: all pixels in each scaled native block match.
        a=im.crop((ox,oy,ox+640*s,oy+360*s));small=a.resize((640,360),Image.Resampling.NEAREST).resize(a.size,Image.Resampling.NEAREST)
        from PIL import ImageChops
        assert ImageChops.difference(a,small).getbbox() is None, str(file)+' is not an integer pixel grid'
        captures.append(str(file.relative_to(Q)))
report={'passed':True,'immutableSourceFiles':len(old),'staticImageConversions':len(imageMap),'clipsWithSourceMap':len(clipMap),'originalHeadAndFeetPushFrames':42,'detachedPushComponents':0,'newClips':len(clips),'newFrames':frames,'glyphs':len(f['characters']),'missingGlyphs':0,'integerGridCaptures':captures,'humanMotionApproval':False,'highDpiDifferentMonitorVerified':False}
(Q/'asset-checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('PASS',len(old),'originals preserved;',frames,'binary-alpha frames;',len(f['characters']),'glyphs;',len(captures),'integer captures')
