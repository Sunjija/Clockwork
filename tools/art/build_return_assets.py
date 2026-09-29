"""Native pixel props explicitly requested by the user; Tique pixels are copied unchanged."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, shutil, hashlib, random, math, wave, struct

ROOT=Path(__file__).resolve().parents[2]
PROJECT=ROOT/'unity/TiqueReturnPrototype'
OUT=PROJECT/'Assets/Resources/Return'
ART=OUT/'Art';ART.mkdir(parents=True,exist_ok=True)
PALETTE=['#10191e','#1b292e','#293c42','#3d5359','#657c7d','#a3b1a0','#3b312b','#69533b','#a88454','#d2b777','#e5d7a0','#2e7b83','#64d4ca','#c0fff0','#793a38','#da6657']
def canvas(w,h):
 im=Image.new('RGBA',(w,h));return im,ImageDraw.Draw(im)
def plate(d,box,base=2,edge=0,highlight=4):
 x,y,r,b=box;d.rectangle(box,fill=PALETTE[edge]);d.rectangle((x+1,y+1,r-1,b-1),fill=PALETTE[base]);d.line((x+2,y+2,r-2,y+2),fill=PALETTE[highlight]);d.line((x+2,y+3,x+2,b-2),fill=PALETTE[highlight])
def bolt(d,x,y):d.rectangle((x,y,x+2,y+2),fill=PALETTE[0]);d.point((x,y),fill=PALETTE[5])
def mark(d,x,y,c=12):
 d.line((x,y,x,y+7,x+7,y+7,x+7,y),fill=PALETTE[c],width=2);d.rectangle((x-1,y-2,x+1,y),fill=PALETTE[5]);d.rectangle((x+6,y-2,x+8,y),fill=PALETTE[5])
def save(im,name):im.save(ART/(name+'.png'))

# Brass-rimmed machinery; integer rectangles/lines only, binary alpha, 16 authored colors.
im,d=canvas(32,44);plate(d,(3,1,28,42),7,0,9);plate(d,(6,5,25,24),1,0,3)
d.rectangle((10,10,21,14),fill=PALETTE[12]);d.rectangle((8,29,23,36),fill=PALETTE[2]);d.line((13,33,23,27),fill=PALETTE[9],width=3)
for x in [5,25]:
 for y in [3,38]:bolt(d,x,y)
save(im,'console')
im,d=canvas(40,36);plate(d,(2,2,37,32),3,0,4);plate(d,(8,7,31,26),7,0,9)
d.rectangle((16,8,23,22),fill=PALETTE[0]);d.rectangle((5,26,13,34),fill=PALETTE[12]);d.rectangle((26,26,34,34),fill=PALETTE[12]);mark(d,16,12)
for x in [4,32]:bolt(d,x,5)
save(im,'magnet')
im,d=canvas(32,30);plate(d,(0,0,31,29),2,0,4);plate(d,(4,4,27,25),3,0,5);mark(d,12,10)
for x in [2,27]:
 for y in [2,24]:bolt(d,x,y)
save(im,'weight')
im,d=canvas(54,12);plate(d,(0,1,53,11),7,0,9);d.rectangle((4,0,49,3),fill=PALETTE[5]);mark(d,23,2,11);save(im,'pressure')
im,d=canvas(64,112);plate(d,(0,0,63,111),7,0,9);plate(d,(6,6,57,110),1,0,3)
for x in [9,25,41]:plate(d,(x,11,x+12,106),2,0,4)
d.rectangle((29,12,33,104),fill=PALETTE[9])
for y in range(13,105,16):d.rectangle((3,y,5,y+6),fill=PALETTE[12]);d.rectangle((58,y,60,y+6),fill=PALETTE[12])
save(im,'gate')
im,d=canvas(28,26);plate(d,(1,1,26,25),7,0,9);d.line((7,18,20,5),fill=PALETTE[4],width=4);d.rectangle((17,3,24,9),fill=PALETTE[9]);save(im,'rail-handle')

# Stationary guardian: integrated gate chassis, heavy service arm and separate low wrist terminal.
im,d=canvas(128,160)
plate(d,(8,16,119,158),2,0,4);plate(d,(17,27,110,144),3,0,4)
for x in [3,110]:
 plate(d,(x,46,x+14,121),7,0,9)
 for y in range(50,118,8):d.line((x+3,y,x+10,y),fill=PALETTE[6])
plate(d,(29,9,99,65),7,0,9);plate(d,(34,17,94,57),1,0,4)
d.rectangle((39,29,89,40),fill=PALETTE[0]);d.rectangle((44,31,57,37),fill=PALETTE[15]);d.rectangle((73,31,86,37),fill=PALETTE[15])
d.rectangle((61,29,68,43),fill=PALETTE[3]);d.rectangle((47,47,80,49),fill=PALETTE[9])
plate(d,(30,75,98,118),1,0,4)
for x in range(36,95,10):d.rectangle((x,81,x+4,110),fill=PALETTE[7]);d.line((x+1,82,x+1,104),fill=PALETTE[9])
for x in [19,105]:
 for y in [31,70,130]:bolt(d,x,y)
plate(d,(44,124,85,143),6,0,8);mark(d,61,130,15)
save(im,'guardian')
im,d=canvas(54,54)
plate(d,(15,0,38,20),3,0,5);plate(d,(5,15,48,49),7,0,9)
for x in [7,18,29,40]:plate(d,(x,29,x+8,53),2,0,4)
plate(d,(16,20,37,34),1,0,3);mark(d,23,24,15)
for x in [8,42]:bolt(d,x,19)
save(im,'fist')
im,d=canvas(18,24);plate(d,(0,0,17,23),2,0,4)
for y in range(3,23,5):d.line((3,y,14,y),fill=PALETTE[7]);d.line((3,y+1,14,y+1),fill=PALETTE[9])
save(im,'arm-link')
im,d=canvas(40,32);plate(d,(2,1,37,31),2,0,4);plate(d,(10,6,29,26),14,0,15);d.rectangle((17,11,22,20),fill=PALETTE[10]);save(im,'practice')
im,d=canvas(32,16);plate(d,(0,0,31,15),2,0,4)
for x in range(3,30,7):d.rectangle((x,2,x+3,4),fill=PALETTE[9])
save(im,'platform')

# Reuse the existing Limbus concept. Only downsample/quantize for the native grid, do not repaint Tique.
bg=Image.open(ROOT/'prototypes/tique-playground/Scene/limbus.png').convert('RGB').resize((640,360),Image.Resampling.NEAREST)
bg=bg.quantize(colors=64,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGBA');save(bg,'limbus')
dark=Image.new('RGBA',bg.size,(9,18,23,105));bg2=Image.alpha_composite(bg,dark);save(bg2,'inspection')

meta=json.loads((ROOT/'prototypes/tique-playground/Revisions/10/data.json').read_text(encoding='utf8'))
clips=[]
for name,clip in meta['clips'].items():
 folder=OUT/'Tique'/name;folder.mkdir(parents=True,exist_ok=True)
 for i,src in enumerate(clip['frames']):shutil.copy2(ROOT/'prototypes/tique-playground'/src,folder/f'{i:02}.png')
 clips.append({'name':name,'durations':clip['durations']})
(OUT/'clips.json').write_text(json.dumps({'clips':clips}),encoding='utf8')

# Short original synthesized sound cues (no downloaded/licensed recordings).
audio=OUT/'Audio';audio.mkdir(exist_ok=True)
for name,freq,seconds in [('switch',360,.09),('jump',510,.12),('dash',170,.14),('hit',95,.14),('hurt',150,.22),('warning',260,.3),('land',75,.09),('success',660,.5)]:
 with wave.open(str(audio/(name+'.wav')),'wb') as w:
  w.setparams((1,2,22050,0,'NONE','not compressed'))
  data=[]
  for n in range(int(seconds*22050)):
   t=n/22050;env=(1-t/seconds)**2;f=freq*(1+t/seconds*.4)
   v=math.sin(2*math.pi*f*t)*.55+math.sin(2*math.pi*f*2*t)*.2
   data.append(struct.pack('<h',int(14000*env*v)))
  w.writeframes(b''.join(data))
manifest={'status':'prototype','artMethod':'Original native pixel props hand-authored through integer drawing commands, as explicitly authorized by user. No AI generation used.','palette':PALETTE,'tique':'revision 10 frames copied byte-exact','background':'Existing Clockwork Limbus concept nearest resized to 640x360 and quantized to 64 colors','audio':'Original synthesized cues','files':[]}
for p in sorted(OUT.rglob('*')):
 if p.is_file():manifest['files'].append({'path':str(p.relative_to(PROJECT)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(PROJECT/'asset-provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print('Prepared',len(manifest['files']),'assets at',PROJECT)
