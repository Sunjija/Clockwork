from pathlib import Path
from PIL import Image
import json, sys
p=Path(__file__).resolve().parents[1]
new=p/'Assets/Resources/ReturnV2/TiqueV9'
base=Image.open(p/'Assets/Resources/Return/Tique/Idle/00.png').convert('RGBA')
head=base.crop((16,8,47,35)).tobytes()
heart=base.crop((30,37,43,47)).tobytes()
bad=[]; results=[]
for clip in json.loads((new/'clips.json').read_text())['clips']:
 if clip['name'] in ['Walk','dash-ghost','push-up','push-brace-up']: continue
 for i in range(len(clip['durations'])):
  im=Image.open(new/clip['name']/f'{i:02d}.png').convert('RGBA')
  hs=[(x,y) for y in range(7,23) for x in range(10,29) if im.crop((x,y,x+31,y+27)).tobytes()==head]
  cs=[(x,y) for y in range(33,44) for x in range(23,39) if im.crop((x,y,x+13,y+10)).tobytes()==heart]
  results.append({'clip':clip['name'],'frame':i,'head':hs,'heart':cs})
  if not hs or not cs: bad.append((clip['name'],i,bool(hs),bool(cs)))
print(json.dumps({'checkedFrames':len(results),'bad':bad}))
(p/'QA/V9/identity-registration.json').write_text(json.dumps({'passed':not bad,'scope':'Actual runtime PNG head31x27 and heart13x10 exact RGBA against one original model; approved Walk is separately byte-preserved; back-facing push and blue ghosts use their directional/palette checks','frames':results},indent=2))
sys.exit(2 if bad else 0)
