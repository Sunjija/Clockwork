"""V10 native tracing of individual whole-character imagegen pose sources.

The sprite-gen extracted complete pose is the drawing source. Changes below
are explicit native pixel annotations; there is no region resize, rectangular
head/chest restoration, old-sprite part composite, or photometric interpolation.
The approved original neutral is copied byte-for-byte at clip endpoints.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import shutil
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'art/return-v10-spritegen'
RUN = ART / 'actions'
ORIGINAL = ROOT / 'unity/TiqueReturnPrototype/Assets/Resources/Return/Tique'
BASE = Image.open(ORIGINAL / 'Idle/00.png').convert('RGBA')
PAL = [c for c, n in Counter(BASE.getdata()).most_common() if c[3]]
CLEAR = (0, 0, 0, 0)
INK, BRASS, GOLD, SHADE, LIGHT, MID, WHITE = PAL[:7]
SYMBOLS = '0123456789abc'
TO_COLOR = dict(zip(SYMBOLS, PAL)) | {'.': CLEAR}
TO_SYMBOL = dict(zip(PAL, SYMBOLS)) | {CLEAR: '.'}
KEYS = ('windup', 'strike', 'recoil', 'dashload', 'dashtravel', 'dashbrake', 'extension', 'withdraw', 'dashalternate')
TIMES = {c['name']: c['durations'] for c in json.loads((ORIGINAL.parent / 'clips.json').read_text())['clips']}
HAND_ROWS = json.loads((ART / 'round-hand.json').read_text())['rows']

# Source-visible fingertip-free ball envelopes. These annotations remove the
# larger source hand outline, then trace the one shared 5x5 round-hand model.
HANDS = {
 'windup': [((18,36,25,42),(19,36)),((44,41,49,48),(44,42))],
 'strike': [((44,30,53,39),(46,32)),((43,41,49,48),(43,42))],
 'recoil': [((21,40,27,45),(22,40)),((43,43,49,48),(44,43))],
 'dashload': [((17,42,24,48),(18,43)),((44,42,51,48),(44,42))],
 'dashtravel': [((11,35,19,43),(12,36)),((44,44,51,50),(44,45))],
 'dashbrake': [((14,37,22,44),(15,38)),((43,42,50,48),(43,43))],
 'extension': [((33,33,40,39),(34,34)),((43,41,49,48),(43,43))],
 'withdraw': [((25,37,32,44),(26,38)),((43,44,49,50),(43,45))],
 'dashalternate': [((10,37,18,44),(12,37)),((45,40,52,48),(46,42))],
}
WRISTS = {
 'windup':[(24,37),(25,37),(24,38),(25,38),(24,39),(43,43),(43,44)],
 'strike':[(43,34),(44,34),(45,34),(43,35),(44,35),(45,35),(41,43),(42,43),(41,44),(42,44)],
 'recoil':[(23,39),(24,39),(42,44),(43,44),(43,45)],
 'dashload':[(19,42),(20,42),(42,43),(43,43),(42,44),(43,44),(42,45),(43,45)],
 'dashtravel':[(17,37),(18,37),(17,38),(18,38),(19,37),(19,38),(20,36),(20,37),(21,35),(21,36),(42,45),(43,45),(42,46),(43,46),(42,47),(43,47)],
 'dashbrake':[(20,39),(21,39),(20,40),(21,40),(42,42),(42,43),(42,44),(42,45)],
 'extension':[(32,35),(33,35),(32,36),(33,36),(42,43),(42,44),(42,45)],
 'withdraw':[(27,37),(28,37),(42,46),(42,47)],
 'dashalternate':[(17,38),(18,38),(17,39),(18,39),(19,37),(19,38),(20,36),(20,37),(44,43),(45,43),(44,44),(45,44)],
}
# The original has a five-pixel zigzag mouth. Register that semantic feature
# to each source's left pupil; do not replace the head rectangle or lens rim.
OLD_MOUTH = {
 'windup':[(36,27),(37,27),(39,27),(35,28),(38,28)],
 'strike':[(33,26),(35,26),(37,26),(34,27),(36,27)],
 'recoil':[(35,28),(37,28),(39,28),(36,29),(38,29)],
 'dashload':[(37,30),(39,30),(41,30),(38,31),(40,31)],
 'dashtravel':[(37,29),(39,29),(41,29),(38,30),(40,30)],
 'dashbrake':[(36,28),(38,28),(40,28),(37,29),(39,29)],
 'extension':[(34,27),(36,27),(38,27),(35,28),(37,28)],
 'withdraw':[(34,28),(36,28),(38,28),(35,29),(37,29)],
 'dashalternate':[(38,30),(40,30),(42,30),(39,31),(41,31)],
}
MOUTH_OFFSET = {'windup':(0,-2),'strike':(-2,-2),'recoil':(1,0),
 'dashload':(3,2),'dashtravel':(2,0),'dashbrake':(2,0),
 'extension':(0,-1),'withdraw':(0,0),'dashalternate':(5,2)}
MOUTH = [(34,28),(36,28),(38,28),(35,29),(37,29)]
# Only individual cyan and warm glow pixels are traced from the reference.
# All plate outlines, bronze shell, waist and arms remain source-derived.
HEART_AT = {'windup':(32,37),'strike':(28,37),'recoil':(30,37),
 'dashload':(30,39),'dashtravel':(29,38),'dashbrake':(30,37),
 'extension':(29,37),'withdraw':(30,37),'dashalternate':(28,38)}
HEART_COLORS = set(PAL[7:12])
GLOW_COLORS = HEART_COLORS | {LIGHT, WHITE}
HEART_FEATURE = [(x-30,y-37,BASE.getpixel((x,y)))
 for y in range(37,47) for x in range(30,43)
 if BASE.getpixel((x,y)) in GLOW_COLORS]
# Native hand-source remnants outside the measured round sphere are erased
# point by point. These are the former flat cap's lower/left nubs, not torso.
NUBS = {
 'strike':[(41,45,'0'),(42,45,'0'),(41,46,'.'),(42,46,'.'),(41,47,'.'),(42,47,'.')],
 'dashload':[(41,43,'0'),(41,44,'0'),(41,45,'0'),(41,46,'.'),(42,46,'0'),(43,46,'0'),(41,47,'.'),(42,47,'.')],
 'dashtravel':[(41,45,'0'),(41,46,'0'),(41,47,'0'),(41,48,'.'),(42,48,'0'),(43,48,'0'),(41,49,'.'),(42,49,'.'),(43,49,'.')],
 'dashalternate':[(42,45,'0'),(43,45,'0'),(44,45,'0'),(42,46,'.'),(43,46,'.'),(44,46,'.'),(42,47,'.'),(43,47,'.'),(44,47,'.')],
}

def semantic_features(im, name):
 for p in OLD_MOUTH[name]:
  if im.getpixel(p)==INK:im.putpixel(p,GOLD)
 dx,dy=MOUTH_OFFSET[name]
 for x,y in MOUTH:im.putpixel((x+dx,y+dy),INK)
 # Erase old cyan only. Warm source metal around the feature remains intact.
 for y in range(35,50):
  for x in range(24,44):
   if im.getpixel((x,y)) in HEART_COLORS:im.putpixel((x,y),GOLD)
 hx,hy=HEART_AT[name]
 for x,y,c in HEART_FEATURE:
  p=(hx+x,hy+y)
  # Preserve the whole-pose shell: a glow highlight may not grow a detached
  # plate nub outside an already visible source surface.
  if c in HEART_COLORS or im.getpixel(p)[3]:im.putpixel(p,c)

def digest(path):
 return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def changes(before, after):
 return [{'x':x,'y':y,'before':TO_SYMBOL.get(before.getpixel((x,y)),list(before.getpixel((x,y)))),
          'after':TO_SYMBOL.get(after.getpixel((x,y)),list(after.getpixel((x,y))))}
         for y in range(64) for x in range(64) if before.getpixel((x,y)) != after.getpixel((x,y))]

def hand(im, at):
 x,y=at
 for yy,row in enumerate(HAND_ROWS):
  for xx,s in enumerate(row): im.putpixel((x+xx,y+yy),TO_COLOR[s])

def patch(im, x, y, rows):
 """An explicit native artist annotation, including its transparent contour."""
 assert len({len(row) for row in rows}) == 1
 for yy,row in enumerate(rows):
  for xx,s in enumerate(row): im.putpixel((x+xx,y+yy),TO_COLOR[s])

def native_key(name):
 source = RUN / 'frames' / name / 'frame-0.png'
 before = Image.open(source).convert('RGBA')
 im=before.copy()
 for clear_box,at in HANDS[name]:
  for y in range(clear_box[1],clear_box[3]):
   for x in range(clear_box[0],clear_box[2]): im.putpixel((x,y),CLEAR)
  hand(im,at)
 for x,y,s in NUBS.get(name,[]):im.putpixel((x,y),TO_COLOR[s])
 semantic_features(im,name)
 for p in WRISTS[name]: im.putpixel(p,GOLD)
 for _,at in HANDS[name]:hand(im,at)
 if name=='windup':
  for p in ((17,37),(17,38)):im.putpixel(p,CLEAR)
 # Two generated domes carried one extra top contour row. Re-trace only that
 # visible one-pixel contour; no body/head region is rescaled or overwritten.
 if name in ('dashload','dashtravel'):
  for x in range(64):
   if im.getpixel((x,8))[3]: im.putpixel((x,8),CLEAR)
   if im.getpixel((x,9))[3]: im.putpixel((x,9),INK)
 assert set(c for c in im.getdata() if c[3]).issubset(set(PAL))
 out=RUN/'native-keys';out.mkdir(parents=True,exist_ok=True)
 im.save(out/(name+'.png'))
 record={'key':name,'source':str(source.relative_to(ROOT)).replace('\\','/'),
  'sourceSha256':digest(source),'nativeSha256':digest(out/(name+'.png')),
  'method':'whole extracted pose plus individually recorded native round hands, 2px metallic wrists, registered 5-dot mouth and cyan/glow semantic tracing',
  'pixelEdits':changes(before,im),'hands':[list(at) for _,at in HANDS[name]],
  'noPartResizing':True,'noRectangularIdentityOverwrite':True}
 (out/(name+'-pixel-edits.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
 return im

def contact(images,path,columns=4,scale=5):
 cell=64*scale;row_h=cell+24
 out=Image.new('RGBA',(columns*cell,((len(images)+columns-1)//columns)*row_h),(19,27,34,255))
 d=ImageDraw.Draw(out)
 for n,(name,im) in enumerate(images):
  x=n%columns*cell;y=n//columns*row_h
  d.text((x+8,y+4),name,fill=(255,231,163),font=ImageFont.load_default())
  out.alpha_composite(im.resize((cell,cell),Image.Resampling.NEAREST),(x,y+20))
  d.line((x,y+20+56*scale,x+cell-1,y+20+56*scale),fill=(65,81,90))
 out.save(path)

def variant(keys, source, label, moves=(), wrist=(), pixels=(), painted=()):
 """Explicit pose-specific native hand/joint/sole edits, no pasted body parts.

 Each hand annotation changes its end effector and visible wrist volume. It
 does not move/resample an old sprite component or interpolate image colours.
 The complete generated source still supplies the body's pose and contour.
 """
 before=keys[source];im=before.copy();at=[p for box,p in HANDS[source]]
 for index,new_at in moves:
  x,y=at[index]
  for yy in range(5):
   for xx in range(5):im.putpixel((x+xx,y+yy),CLEAR)
  at[index]=new_at
 for p in wrist:im.putpixel(p,GOLD)
 for x,y,s in pixels:im.putpixel((x,y),TO_COLOR[s])
 for x,y,rows in painted:patch(im,x,y,rows)
 # Hand spheres are painted last, so a wrist can connect but never create a
 # thumb or destroy a sphere's measured 5x5 contour.
 for p in at:hand(im,p)
 return {'label':label,'source':source,'image':im,'hands':at,
         'edits':changes(before,im),'motionAnnotation':{'handMoves':moves,'wristPoints':wrist,'nativeSolePatches':len(painted)}}

def key_frame(keys, source):
 return {'label':source,'source':source,'image':keys[source],
         'hands':[p for box,p in HANDS[source]],'edits':[],'motionAnnotation':'complete generated keypose'}

def neutral_frame():
 return {'label':'original-neutral','source':'original','image':BASE.copy(),'hands':[],
         'edits':[],'motionAnnotation':'approved original, byte-identical endpoint'}

def near_neutral():
 im=BASE.copy()
 # Recovery into the exact endpoint, traced from the original relaxed stance.
 for box in [(17,42,23,49),(42,42,48,49)]:
  for y in range(box[1],box[3]):
   for x in range(box[0],box[2]):im.putpixel((x,y),CLEAR)
 for p in [(20,41),(21,41),(42,43),(42,44)]:im.putpixel(p,BRASS)
 positions=[(17,42),(43,42)]
 for p in positions:hand(im,p)
 return {'label':'recovery-near-neutral','source':'original','image':im,'hands':positions,
  'edits':changes(BASE,im),'motionAnnotation':'original full stance; relaxed hands finish a one-pixel return'}

def sequences(keys):
 attack=[neutral_frame(),
  variant(keys,'windup','windup-begin',moves=[(0,(19,38))],wrist=[(24,39),(25,39),(24,40),(25,40)]),
  key_frame(keys,'windup'),key_frame(keys,'extension'),key_frame(keys,'strike'),
  variant(keys,'strike','strike-follow-through',moves=[(0,(47,33))],wrist=[(46,34),(46,35),(46,36)]),
  variant(keys,'extension','early-withdrawal',moves=[(0,(35,35))],wrist=[(33,36),(34,36),(34,37)]),
  key_frame(keys,'withdraw'),key_frame(keys,'recoil'),
  variant(keys,'recoil','recoil-settle',moves=[(0,(21,41))],wrist=[(22,40),(23,40)]),
  near_neutral(),neutral_frame()]
 # A separately generated second dash pose supplies the stride change. Small
 # native edits define entry/exit joint angles and a readable trailing sole.
 trailing_sole=['...00..','...120.','...0460','...0420','...0150','....00.','.......','.......']
 dash=[neutral_frame(),
  variant(keys,'dashload','dash-preload-begin',moves=[(0,(18,44)),(1,(43,43))],wrist=[(19,43),(20,43),(42,44),(42,45)]),
  key_frame(keys,'dashload'),
  variant(keys,'dashtravel','dash-entry',moves=[(0,(14,38)),(1,(44,44))],wrist=[(19,39),(20,39),(19,40),(20,40),(43,45),(43,46)],painted=[(15,48,trailing_sole)]),
  key_frame(keys,'dashtravel'),key_frame(keys,'dashalternate'),
  variant(keys,'dashalternate','dash-stride-settle',moves=[(0,(13,38)),(1,(45,43))],wrist=[(18,39),(19,39),(18,40),(19,40),(44,44),(44,45)],pixels=[(31,54,'2'),(32,54,'0')]),
  variant(keys,'dashtravel','dash-exit',moves=[(0,(14,37)),(1,(44,44))],wrist=[(19,38),(20,38),(19,39),(20,39),(43,45),(43,46)],pixels=[(34,54,'2'),(35,54,'0')]),
  key_frame(keys,'dashbrake'),
  variant(keys,'dashbrake','brake-settle',moves=[(0,(16,39)),(1,(43,44))],wrist=[(21,40),(22,40),(21,41),(22,41),(42,45),(42,46)]),
  near_neutral(),neutral_frame()]
 return {'Attack':attack,'Dash':dash}

def components(im):
 left={(x,y) for y in range(64) for x in range(64) if im.getpixel((x,y))[3]};groups=[]
 while left:
  q=left.pop();todo=[q];group=[]
  while todo:
   x,y=todo.pop();group.append((x,y))
   for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
    p=(x+dx,y+dy)
    if p in left:left.remove(p);todo.append(p)
  groups.append(group)
 return sorted(groups,key=len,reverse=True)

def gif_frame(im,scale=4):
 colors=[0,0,0]+[v for c in PAL for v in c[:3]]
 p=Image.new('P',(64,64),0);p.putpalette(colors+[0]*(768-len(colors)))
 indices={c:i+1 for i,c in enumerate(PAL)}
 p.putdata([indices.get(c,0) if c[3] else 0 for c in im.getdata()])
 p.info['transparency']=0
 return p.resize((64*scale,64*scale),Image.Resampling.NEAREST)

def preview_gif(frames,ms,path):
 # GIF timing is in 10ms units. Cumulative rounding retains the original full
 # duration instead of losing 20ms from Dash's four 35ms frames.
 t=0;previous=0;encoded=[]
 for d in ms:
  t+=d;now=round(t/10)*10;encoded.append(now-previous);previous=now
 p=[gif_frame(row['image']) for row in frames]
 p[0].save(path,save_all=True,append_images=p[1:],duration=encoded,transparency=0,disposal=2,optimize=False)
 return encoded

def write_clip(name,frames):
 dest=ART/name;dest.mkdir(parents=True,exist_ok=True)
 edits_dir=RUN/'native-frame-edits'/name;edits_dir.mkdir(parents=True,exist_ok=True)
 rows=[]
 for i,row in enumerate(frames):
  im=row['image'];path=dest/f'{i:02}.png'
  if row['label']=='original-neutral':shutil.copyfile(ORIGINAL/'Idle/00.png',path)
  else:im.save(path)
  assert im.size==(64,64)
  assert all(c[3] in (0,255) for c in im.getdata())
  assert set(c for c in im.getdata() if c[3]).issubset(set(PAL))
  for at in row['hands']:
   for yy,rs in enumerate(HAND_ROWS):
    for xx,s in enumerate(rs):assert im.getpixel((at[0]+xx,at[1]+yy))==TO_COLOR[s],(name,i,at,xx,yy,'hand shape drift')
  gs=components(im)
  assert len(gs)==1,(name,i,'disconnected opaque pixels')
  rows.append({'index':i,'file':path.name,'duration_ms':TIMES[name][i],
   'source_key':row['source'],'pose':row['label'],'sha256':digest(path),'bounds':im.getbbox(),
   'hands':[list(p) for p in row['hands']],'components4':[len(g) for g in gs],
   'motionAnnotation':row['motionAnnotation']})
  (edits_dir/f'{i:02}.json').write_text(json.dumps({'frame':i,'source_key':row['source'],
   'pose':row['label'],'pixelEdits':row['edits'],'motionAnnotation':row['motionAnnotation']},ensure_ascii=False,indent=2),encoding='utf-8')
 assert len(frames)==len(TIMES[name])==12
 assert (dest/'00.png').read_bytes()==(ORIGINAL/'Idle/00.png').read_bytes()
 assert (dest/'11.png').read_bytes()==(ORIGINAL/'Idle/00.png').read_bytes()
 contact([(f'{i:02} '+row['label'],row['image']) for i,row in enumerate(frames)],dest/'contact-3x.png',scale=3)
 contact([('original',BASE)]+[(f'{i:02} '+row['label'],row['image']) for i,row in enumerate(frames)],dest/'identity-contact-5x.png',scale=5)
 encoded=preview_gif(frames,TIMES[name],dest/'preview-4x.gif')
 manifest={'clip':name,'frame_count':len(frames),'frame_size':[64,64],'pixel_pivot':[32,56],
  'durations_ms':TIMES[name],'duration_ms':sum(TIMES[name]),'gif_durations_ms':encoded,
  'palette':PAL,'binary_alpha':True,'neutral_endpoints_original_bytes':True,
  'method':'single whole-body images; real sprite-gen extraction/pixel-unfake; recorded native pose/hand contour tracing',
  'motion_review':'PNG/contact and decoded GIF exposure review; actual runtime naturalness remains independent review',
  'frames':rows}
 (dest/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 asset={'kind':'sprite-gen-asset','version':1,'anchor':[32,56],
        'frames':[{'file':f'{i:02}.png','duration':TIMES[name][i]/1000} for i in range(len(frames))]}
 (dest/'asset.json').write_text(json.dumps(asset,indent=2),encoding='utf-8')
 return manifest

def write_ghost(frames):
 dest=ART/'dash-ghost';dest.mkdir(parents=True,exist_ok=True);rows=[]
 for i,row in enumerate(frames):
  src=row['image'];im=Image.new('RGBA',(64,64))
  im.putdata([PAL[7] if c[3] else CLEAR for c in src.getdata()])
  assert im.getchannel('A').tobytes()==src.getchannel('A').tobytes()
  p=dest/f'{i:02}.png';im.save(p)
  rows.append({'index':i,'file':p.name,'duration_ms':TIMES['Dash'][i],'sha256':digest(p),'alpha_matches_dash':True})
 (dest/'manifest.json').write_text(json.dumps({'frame_count':12,'frame_size':[64,64],'pixel_pivot':[32,56],
  'durations_ms':TIMES['Dash'],'frames':rows,'method':'Dash silhouette byte-exact alpha; cyan recolor only'},indent=2),encoding='utf-8')

def main():
 keys={name:native_key(name) for name in KEYS}
 contact([('original',BASE)]+list(keys.items()),RUN/'native-keys-identity-5x.png')
 clips=sequences(keys);manifests={n:write_clip(n,rows) for n,rows in clips.items()}
 write_ghost(clips['Dash'])
 print(json.dumps({'nativeKeys':list(keys),'clips':{n:{'count':m['frame_count'],'duration_ms':m['duration_ms'],
  'components4':[f['components4'] for f in m['frames']]} for n,m in manifests.items()}},ensure_ascii=False))

if __name__=='__main__':main()
