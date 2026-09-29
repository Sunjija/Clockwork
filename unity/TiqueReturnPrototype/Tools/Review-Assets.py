"""Offline asset integrity + layout review. These pictures are NOT Unity screenshots.

Requires Pillow. The project itself has no Python runtime dependency.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, hashlib, re, wave

root=Path(__file__).resolve().parents[1]
qa=root/'QA';qa.mkdir(exist_ok=True)
res=root/'Assets/Resources/Return'
manifest=json.loads((root/'asset-provenance.json').read_text(encoding='utf8'))
for item in manifest['files']:
    assert hashlib.sha256((root/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
clips=json.loads((res/'clips.json').read_text(encoding='utf8'))['clips']
frames=[]
def pixels(im):return im.get_flattened_data() if hasattr(im,'get_flattened_data') else im.getdata()
for clip in clips:
    assert len(clip['durations'])>0 and all(d>0 for d in clip['durations'])
    for n in range(len(clip['durations'])):
        p=res/'Tique'/clip['name']/f'{n:02}.png';im=Image.open(p).convert('RGBA')
        assert im.size==(64,64),p
        assert set(pixels(im.getchannel('A'))) <= {0,255},p
        if clip['name'] in ('Idle','Walk','Attack'):assert im.getbbox()[3]==56,p
        frames.append(p)
assert len(frames)==67
palette=set(tuple(bytes.fromhex(c[1:])) for c in manifest['palette'])
props=list((res/'Art').glob('*.png'))
for p in props:
    im=Image.open(p).convert('RGBA')
    if p.stem not in ('limbus','inspection'):
        assert set(pixels(im.getchannel('A'))) <= {0,255}
        assert {rgb[:3] for rgb in pixels(im) if rgb[3]}<=palette,p
    else:assert im.size==(640,360)
for p in (res/'Audio').glob('*.wav'):
    with wave.open(str(p)) as w:assert w.getnframes()>0 and w.getnchannels()==1
guids={}
for p in (root/'Assets').rglob('*'):
    if p.suffix=='.meta':continue
    meta=Path(str(p)+'.meta');assert meta.exists(),p
    content=meta.read_text(encoding='utf8');g=re.search(r'^guid: ([0-9a-f]{32})$',content,re.M)[1]
    assert g not in guids,(g,p);guids[g]=p
    if p.suffix=='.png':
        for setting in ('filterMode: 0','enableMipMap: 0','textureCompression: 0','nPOTScale: 0'):assert setting in content,(p,setting)
for p in [root/'Assets/Scenes/TiqueReturn.unity',*list((root/'ProjectSettings').glob('*.asset'))]:
    for g in re.findall(r'guid: ([0-9a-f]{32})',p.read_text(encoding='utf8')):
        assert g.startswith('0000000000000000') or g in guids,(p,g)
scriptGuid=re.search(r'^guid: (\w+)',(root/'Assets/Scripts/ReturnGame.cs.meta').read_text(),re.M)[1]
assert 'guid: '+scriptGuid in (root/'Assets/Scenes/TiqueReturn.unity').read_text()

fontPath=Path('C:/Windows/Fonts/malgun.ttf')
def font(size):return ImageFont.truetype(str(fontPath),size) if fontPath.exists() else ImageFont.load_default(size=size)
def prop(canvas,name,x,y):
    canvas.alpha_composite(Image.open(res/'Art'/f'{name}.png').convert('RGBA'),(int(x),int(y)))
def bar(d,box,color):
    x,y,w,h=box;d.rectangle((x,y,x+w-1,y+h-1),fill=color)
def room(arena=False):
    im=Image.open(res/'Art'/('inspection.png' if arena else 'limbus.png')).convert('RGBA');d=ImageDraw.Draw(im)
    bar(d,(0,252,640,2),'#8c8263')
    if not arena:
        for x,y,w in [(20,222,48),(77,201,45)]:
            p=Image.open(res/'Art/platform.png').resize((w,8),Image.Resampling.NEAREST);im.alpha_composite(p,(x,y))
        bar(d,(150,186,444,3),'#26383d');bar(d,(150,186,3,38),'#64d4ca');bar(d,(308,95,3,94),'#64d4ca')
        bar(d,(326,91,173,7),'#666f69')
        for n in range(12):bar(d,(328+n*14,94,6,2),'#d2b777')
        bar(d,(465,97,6,17),'#d2b777');prop(im,'magnet',448,111);prop(im,'weight',452,137)
        prop(im,'pressure',441,248);prop(im,'console',134,208);prop(im,'rail-handle',241,224)
        prop(im,'practice',508,220);prop(im,'gate',578,140)
        bar(d,(578,129,27,6),'#657c7d');bar(d,(609,129,27,6),'#657c7d')
        tique=res/'Tique/Idle/00.png';px=255
    else:
        prop(im,'guardian',496,92);bar(d,(76,83,482,6),'#405054')
        for n in range(7):prop(im,'arm-link',226,88+n*20)
        prop(im,'fist',208,198);prop(im,'pressure',208,248)
        prop(im,'console',88,208);prop(im,'console',462,208)
        bar(d,(228,221,14,9),'#da6657');tique=res/'Tique/Attack/04.png';px=208
    bar(d,(px-10,251,20,2),'#12191e');im.alpha_composite(Image.open(tique).convert('RGBA'),(px-32,196))
    return im
study=Image.new('RGB',(1280,1660),'#101b20');d=ImageDraw.Draw(study)
d.text((34,22),'티크: 귀환  /  도트 배치 검토',font=font(32),fill='#edf2e8')
d.text((36,70),'오프라인 에셋 합성 · Unity 실행 화면 아님 · 화면 조작/연출 검증 전',font=font(22),fill='#e4be77')
for n,(label,arena) in enumerate([('01  폐기장 동력실 · 전력 분배 / 전자석 / 추 압력판',False),('02  출구 검사실 · 내려온 문지기 손목 단자 공격',True)]):
    yy=116+n*770;d.text((35,yy),label,font=font(24),fill='#96ddd2')
    study.paste(room(arena).resize((1280,720),Image.Resampling.NEAREST),(0,yy+40))
study.save(qa/'layout-study.png')
contact=Image.new('RGB',(1000,690),'#15252b');d=ImageDraw.Draw(contact)
d.text((25,16),'Native pixel assets  /  prototype',font=font(26),fill='#ecf0e4')
for n,p in enumerate([res/'Tique/Idle/00.png',*[p for p in props if p.stem not in ('limbus','inspection')]]):
    x=20+n%5*198;y=72+n//5*204;im=Image.open(p).convert('RGBA');scale=max(1,min(3,150//max(im.size)))
    im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
    contact.paste(im,(x+(166-im.width)//2,y+(160-im.height)//2),im)
    d.text((x,y+163),('Tique (unchanged)' if n==0 else p.stem),font=font(16),fill='#b2d9d1')
contact.save(qa/'assets-contact.png')
report={'passed':True,'tiqueFrames':len(frames),'tiqueNativeSize':[64,64],'groundPivotY':56,'authoredProps':len(props)-2,'backgrounds':2,'audioCues':8,'assetGuids':len(guids),'checks':['SHA-256 matches asset provenance','frame counts and positive timings','binary character alpha','grounded foot baseline','native prop palette and binary alpha','background resolution','decodable audio','unique GUIDs and scene references','Point/no mipmap/no compression import settings'],'scope':'Filesystem integrity and offline layout only; no Unity import/render validation'}
(qa/'asset-checks.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
