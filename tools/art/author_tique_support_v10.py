"""V10 support whole-pose grid tracing and enumerated native cleanup.

Official canonical CLI extraction is retained as evidence. Two sources with
incorrect automatic pitch receive explicitly authored whole-uniform grid imports
using sprite_gen.frames.extract.grid_snap_downscale, never part-specific scaling.
"""
from __future__ import annotations
import hashlib
import json
import re
import sys
from pathlib import Path

from PIL import Image
import author_tique_jump_v10 as native

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT/'art/return-v10-spritegen'
RUN = ART/'support'
SPRITE_GEN = ROOT.parent/'sprite-gen-reference'
sys.path.insert(0,str(SPRITE_GEN))
from sprite_gen.frames.extract import grid_snap_downscale, _best_phase, apply_palette

PALETTE, COLORS = native.PALETTE, native.COLORS
ORIGINAL = native.ORIGINAL
BASE = native.original
HAND = json.loads((ART/'round-hand.json').read_text(encoding='utf-8'))['rows']


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def uniform_import(key: str, pitch: float, bottom: int) -> tuple[Image.Image,dict]:
    path = RUN/'raw'/f'{key}.png'
    raw = Image.open(path).convert('RGBA')
    bbox = raw.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox()
    crop = raw.crop(bbox)
    phase = _best_phase(crop,(pitch,pitch))
    snapped = apply_palette(grid_snap_downscale(crop,pitch,detail_bias=True,phase=phase),PALETTE)
    tight = snapped.crop(snapped.getbbox())
    assert tight.width<=64 and tight.height<=64
    placed = Image.new('RGBA',(64,64))
    position = ((64-tight.width)//2,bottom-tight.height)
    placed.paste(tight,position)
    directory=RUN/'manual-grid';directory.mkdir(parents=True,exist_ok=True)
    placed.save(directory/f'{key}-uniform-import.png')
    note = {'key':key,'method':'EXPLICIT AUTHORED WHOLE-UNIFORM GRID IMPORT; not the automatic CLI canonical extract','raw':str(path.relative_to(RUN)).replace('\\','/'),'rawSha256':sha(path),'opaqueCrop':list(bbox),'uniformPitch':[pitch,pitch],'measuredPhase':list(phase),'officialFunction':'sprite_gen.frames.extract.grid_snap_downscale(sourcecrop,pitch,detail_bias=True,phase=measured)','palette':'original pinned13','nativeSizeBeforePlacement':list(tight.size),'wholeIntegerPlacement':list(position),'partSpecificResize':False,'automaticExtractPreserved':f'frames/{key}/frame-0.png'}
    return placed,note


def key_input(key: str) -> tuple[Image.Image,dict]:
    if key=='pushdown-depth':return uniform_import(key,19.0,60)
    if key=='pushside-contact':return uniform_import(key,19.6,56)
    path=RUN/'frames'/key/'frame-0.png'
    return Image.open(path).convert('RGBA'),{'key':key,'method':'official sprite-gen canonical whole-pose extraction','canonicalExtract':str(path.relative_to(RUN)).replace('\\','/'),'sha256':sha(path),'partSpecificResize':False}


def put(im: Image.Image,xy: tuple[int,int],value: int|None) -> None:
    native.assign(im,xy,value)


def clear(im: Image.Image,rectangle: tuple[int,int,int,int]) -> None:
    x0,y0,x1,y1=rectangle
    for y in range(y0,y1):
        for x in range(x0,x1):put(im,(x,y),None)


def circle(im: Image.Image,center: tuple[int,int]) -> None:
    x0,y0=center[0]-2,center[1]-2
    for y,row in enumerate(HAND):
        for x,c in enumerate(row):put(im,(x0+x,y0+y),None if c=='.' else int(c))


def authored_key(key: str) -> tuple[Image.Image,dict]:
    decoded,note=key_input(key)
    im=decoded.copy()
    shift=(4,0) if key=='pushside-contact' else (0,0)
    im=native.translate(im,shift)
    aligned=im.copy()
    hands=[]
    if key=='pushside-contact':
        # Both complete-source palms align before edits. The shared cap center
        # moves only1px forward from the imported source hand, with its wrist.
        clear(im,(46,33,53,40));clear(im,(46,41,53,48))
        hands=[(50,37),(50,44)]
        for c in hands:circle(im,c)
        for xy,code in {(46,37):4,(47,37):2,(46,38):2,(47,38):1,(46,43):4,(47,43):2,(46,44):2,(47,44):1}.items():put(im,xy,code)
        # Original full-source shoes had two dark bottom rows after grid import.
        # Native metal faces restore a single outline, not a rescaled shoe part.
        for x in range(19,25):put(im,(x,54),3 if x in (19,24) else 2)
        for x in range(39,45):put(im,(x,54),3 if x in (39,44) else 2)
    elif key=='pushup-contact':
        # Actual StateArt battery-moving is30x32, not36px high. The earlier
        # root-requested top24 left4px of air. Restore the source-height palms
        # to top20. Original palms sit beyond the real30px crate corners, so
        # bend the caps inward2/3px over the existing ear edge and restore
        # metal inside source wrist alpha; source forearm length is unchanged.
        clear(im,(11,20,18,28));clear(im,(47,20,54,28))
        hands=[(16,22),(47,22)]
        for c in hands:circle(im,c)
        for xy,code in {(16,25):2,(17,25):1,(16,26):2,(17,26):2,(15,27):1,(16,27):4,
                        (46,25):2,(47,25):1,(46,26):2,(47,26):2,(47,27):2,(48,27):4}.items():
            assert aligned.getpixel(xy)[3],('up wrist outside source alpha',xy)
            put(im,xy,code)
        for xy,code in {(15,29):4,(16,29):2,(49,29):4,(48,29):2}.items():put(im,xy,code)
        # Remove the generator's unapproved round back vent. This is a local
        # semantic-detail deletion on the same bronze shell, not a chest patch.
        for y in range(34,46):
            for x in range(26,41):
                if ((x-33)/7.2)**2+((y-39.5)/6.3)**2<=1:
                    put(im,(x,y),2 if x<=30 and y<=40 else 1)
    elif key=='pushdown-depth':
        clear(im,(25,54,33,60));clear(im,(40,54,49,60))
        hands=[(28,57),(44,57)]
        for c in hands:circle(im,c)
        for xy,code in {(27,54):2,(28,54):4,(44,54):4,(45,54):2}.items():put(im,xy,code)
        # Direct trace of the crouched rear shoes: compact four/three row
        # contours, heels at56, palms forward at60. No forearm elongation.
        clear(im,(18,52,24,58))
        for y,row in enumerate(('.0000.','064220','024330','.0000.')):
            for x,c in enumerate(row):put(im,(18+x,52+y),None if c=='.' else int(c))
        clear(im,(33,52,38,57))
        for y,row in enumerate(('.000.','06420','03230','.000.')):
            for x,c in enumerate(row):put(im,(33+x,52+y),None if c=='.' else int(c))
    elif key=='hurt':
        hands=[(22,44),(49,39)]
        clear(im,(19,41,26,48));clear(im,(46,36,52,43))
        for c in hands:circle(im,c)
        for xy,code in {(25,43):4,(25,42):2,(46,38):4}.items():put(im,xy,code)
        for xy in ((47,35),(48,35)):put(im,xy,None)
    elif key=='hurt-settle':
        hands=[(20,45),(45,45)]
        clear(im,(17,43,24,48));clear(im,(42,43,49,48))
        for c in hands:circle(im,c)
        for xy,code in {(21,42):4,(22,42):2,(44,42):4}.items():put(im,xy,code)
        native.semantic_glow_cleanup(im,0)
    note.update(wholePoseRegistration=list(shift),handCenters=[list(c) for c in hands],handDesign='shared5x5 compact fingerless sphere',nativePixelDelta=native.delta(aligned,im),nativeBBox=list(im.getbbox()),headChestRectangleOverwrite=False,addedLongArmRig=False,review='Actual selected whole-source images, final complete nativekeys and all48exported exposures reviewed as contacts. Runtime/user naturalness remains unverified.')
    return im,note


def stance_variants(key: str,im: Image.Image) -> tuple[list[Image.Image],list[dict]]:
    # Complete-native small stagger steps. Upper pose/contact silhouette stays
    # traced; only a few knee/heel contour pixels change, no foot crop shifting.
    if key=='side':
        specs=[{}, {(22,51):2,(23,51):5,(21,52):4,(22,52):2,(24,53):2,(25,54):0}, {(39,51):1,(40,51):5,(40,52):4,(41,52):2,(38,54):0}, {(22,51):1,(23,51):2,(39,52):4,(40,52):2,(23,54):1}]
    elif key=='up':
        specs=[{}, {(23,50):1,(24,50):2,(25,51):4,(26,51):2,(28,54):2}, {(39,50):1,(40,50):2,(41,51):4,(42,51):2,(43,54):2}, {(24,50):2,(25,50):5,(40,50):2,(41,50):5}]
    else:
        specs=[{}, {(19,52):0,(20,53):4,(21,53):2,(35,54):2}, {(20,54):2,(21,54):3,(34,53):4,(35,53):2}, {(20,53):2,(21,53):4,(35,54):3,(36,54):1}]
    frames=[native.variant(im,edits) for edits in specs]
    notes=[{'stance':i,'wholePoseSource':key,'method':'explicit complete-native knee/heel pixel drawing; no translated foot pieces','pixelDelta':native.delta(im,f)} for i,f in enumerate(frames)]
    return frames,notes


def export(name: str,frames: list[Image.Image],durations: list[int]) -> dict:
    folder=ART/name;folder.mkdir(parents=True,exist_ok=True)
    for i,im in enumerate(frames):
        path=folder/f'{i:02}.png'
        if name=='hurt-pose' and i==2:path.write_bytes(ORIGINAL.read_bytes())
        else:im.save(path)
    native.contact([(f'{name} {i:02}',im) for i,im in enumerate(frames)],folder/'contact-4x.png',7,4)
    clip={'name':name,'frameCount':len(frames),'durations':durations,'totalDurationMs':sum(durations)}
    (folder/'clip.json').write_text(json.dumps(clip,indent=2)+'\n',encoding='utf-8')
    return clip


def check_keys(keys: dict[str,Image.Image],notes: list[dict]) -> dict:
    result={'technicalStatus':'candidate technical validation; not a naturalness or actual-runtime pass','keys':[]}
    for key,im in keys.items():
        assert im.size==(64,64)
        assert set(im.getchannel('A').get_flattened_data())<={0,255}
        assert all(p[:3] in PALETTE for p in im.get_flattened_data() if p[3])
        source_note=next(n for n in notes if n['key']==key)
        hands=source_note['handCenters']
        for cx,cy in hands:
            for y,row in enumerate(HAND):
                for x,c in enumerate(row):
                    assert im.getpixel((cx-2+x,cy-2+y))==(native.TRANSPARENT if c=='.' else COLORS[int(c)]),(key,'hand sphere',cx,cy,x,y)
        contact = {'rightPlane':53} if key=='pushside-contact' else {'palmsTop':20,'boxBottom':20,'boxHorizontalExtent':[17,47],'topRowTouchesUndersideAtX':[17,46]} if key=='pushup-contact' else {'palmsBottom':60,'boxTop':60,'rearSoles':56} if key=='pushdown-depth' else {}
        result['keys'].append({'key':key,'native64':True,'binaryAlpha':True,'canonicalPalette13':True,'twoSharedRoundHands':True,'bbox':list(im.getbbox()),'contactGeometry':contact,'handCenters':hands})
    (RUN/'native-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result


def main() -> None:
    directory=RUN/'native-keys';directory.mkdir(exist_ok=True)
    keys={};notes=[]
    for key in ('pushside-contact','pushup-contact','pushdown-depth','hurt','hurt-settle'):
        im,note=authored_key(key);im.save(directory/f'{key}.png');keys[key]=im;notes.append(note)
    native.contact([('original',BASE)]+list(keys.items()),RUN/'authored-keys-contact-5x.png',3,5)
    (RUN/'native-trace-record.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    clips={};stances=[]
    times=next(c['durations'] for c in json.loads((ROOT/'unity/TiqueReturnPrototype/Assets/Resources/Return/clips.json').read_text(encoding='utf-8'))['clips'] if c['name']=='Walk')
    gait=[0,0,1,1,1,3,0,0,2,2,2,3,0,0]
    for direction,key in [('side','pushside-contact'),('up','pushup-contact'),('down','pushdown-depth')]:
        states,state_notes=stance_variants(direction,keys[key]);stances.extend(state_notes)
        clips['push-'+direction]=export('push-'+direction,[states[i] for i in gait],times)
        clips['push-brace-'+direction]=export('push-brace-'+direction,[keys[key]],[1000])
    clips['hurt-pose']=export('hurt-pose',[keys['hurt'],keys['hurt-settle'],BASE],[40,50,60])
    (RUN/'native-stance-record.json').write_text(json.dumps(stances,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (RUN/'timing-manifest.json').write_text(json.dumps(clips,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    check_keys(keys,notes)
    print(json.dumps({'wholePoseKeys':len(keys),'exportedFrames':sum(c['frameCount'] for c in clips.values()),'contact':str(RUN/'authored-keys-contact-5x.png')},ensure_ascii=False))


if __name__=='__main__':main()
