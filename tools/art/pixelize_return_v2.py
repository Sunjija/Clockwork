"""Deterministic export of imagegen concepts to native pixel assets. Never draws source art."""
from pathlib import Path
from PIL import Image
import hashlib, json, shutil, statistics

ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'art/return-v2'
OUT=ROOT/'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2/Art'
GEN=Path.home()/'.codex/generated_images/01a09050-86c6-7823-86fb-2f0f3077af1e'
SOURCES={
 'workshop':'exec-20b89460-1773-4d90-aba8-67de2c3bc2fb.png',
 'arena':'exec-1b816799-5e1c-40f4-beee-8691f73fee27.png',
 'props':'exec-8ac42b5c-0222-4b7f-bf42-fe584e3ca979.png',
}
def alpha_key(im):
    im=im.convert('RGBA')
    data=[]
    for r,g,b,a in im.getdata():
        if r>g+65 and b>g+65: data.append((0,0,0,0))
        else: data.append((r,g,b,255 if a>=128 else 0))
    im.putdata(data)
    return im
def quantize(im, colors=40, palette=None):
    alpha=im.convert('RGBA').getchannel('A').point(lambda x:255 if x>=128 else 0)
    rgb=im.convert('RGB')
    if palette is None: rgb=rgb.quantize(colors=colors,dither=Image.Dither.NONE)
    else: rgb=rgb.quantize(palette=palette,dither=Image.Dither.NONE)
    rgb=rgb.convert('RGBA');rgb.putalpha(alpha);return rgb
def components(im):
    """Extract complete connected silhouettes; no body part is transformed separately."""
    w,h=im.size;mask=im.getchannel('A').point(lambda a:255 if a>128 else 0).tobytes()
    visited=bytearray(w*h);result=[]
    for start,a in enumerate(mask):
        if not a or visited[start]:continue
        todo=[start];visited[start]=1;pixels=[];left=w;right=0;top=h;bottom=0
        while todo:
            p=todo.pop();pixels.append(p);x=p%w;y=p//w
            left=min(left,x);right=max(right,x);top=min(top,y);bottom=max(bottom,y)
            for q in ((p-1 if x else -1),(p+1 if x<w-1 else -1),(p-w if y else -1),(p+w if y<h-1 else -1)):
                if q>=0 and mask[q] and not visited[q]:visited[q]=1;todo.append(q)
        if len(pixels)>100:result.append((left,top,right+1,bottom+1,len(pixels),pixels))
    return sorted(result)
def main():
    OUT.mkdir(parents=True,exist_ok=True);(ART/'concepts').mkdir(exist_ok=True)
    for name,filename in SOURCES.items():
        src=GEN/filename
        dest=ART/'concepts'/f'{name}.png'
        if src.exists():shutil.copy2(src,dest)
        im=Image.open(dest)
        if name=='props':
            names=['floor','wall','battery','orb','amber-socket','cyan-socket','pylon','gear']
            sizes=[(36,36),(36,38),(30,32),(26,26),(36,36),(36,36),(34,52),(24,24)]
            palette=alpha_key(im).convert('RGB').quantize(colors=40,dither=Image.Dither.NONE)
            for i,(prop,size) in enumerate(zip(names,sizes)):
                x=i%4;y=i//4
                tile=alpha_key(im.crop((round(x*im.width/4),round(y*im.height/2),round((x+1)*im.width/4),round((y+1)*im.height/2))))
                tile=tile.crop(tile.getbbox()).resize(size,Image.Resampling.BOX)
                quantize(tile,palette=palette).save(OUT/f'{prop}.png')
        else:
            # The concept's drawn floor was at y=680. Match its top edge to collision y=282.
            if name=='arena':
                top=im.crop((0,0,im.width,680)).resize((640,282),Image.Resampling.BOX)
                bottom=im.crop((0,680,im.width,im.height)).resize((640,78),Image.Resampling.BOX)
                frame=Image.new('RGB',(640,360));frame.paste(top);frame.paste(bottom,(0,282));im=frame
            else:im=im.resize((640,360),Image.Resampling.BOX)
            quantize(im,48).save(OUT/f'{name}.png')
    # Skill extraction separately fits poses to a cell. For game export use raw connected poses
    # with ONE scale per source strip, so a crouch is not enlarged back to standing height.
    decoded=ART/'iron-warden/decoded';raw=[];motion=[]
    for clip,count in [('idle',4),('attack',6),('stagger',4)]:
        path=decoded/f'{clip}.png'
        if not path.exists():continue
        im=Image.open(path).convert('RGBA');boxes=components(im)
        boxes=sorted(sorted(boxes,key=lambda b:b[4],reverse=True)[:count])
        assert len(boxes)==count,(clip,len(boxes))
        scale=min(136/statistics.median(b[2]-b[0] for b in boxes),188/max(b[2]-b[0] for b in boxes),126/max(b[3]-b[1] for b in boxes))
        motion.append({'clip':clip,'source_bboxes':[b[:5] for b in boxes],'uniform_scale':scale,'feet_y':132,'canvas':[192,144]})
        for i,b in enumerate(boxes):
            # Bounding boxes can overlap in a tightly packed strip. Copy only this silhouette's pixels.
            pose=Image.new('RGBA',(b[2]-b[0],b[3]-b[1]));dst=pose.load();src=im.load()
            for p in b[5]:
                x=p%im.width;y=p//im.width;dst[x-b[0],y-b[1]]=src[x,y]
            pose=pose.resize((round(pose.width*scale),round(pose.height*scale)),Image.Resampling.BOX)
            frame=Image.new('RGBA',(192,144));frame.alpha_composite(pose,((192-pose.width)//2,132-pose.height));raw.append((clip,i,frame))
    if raw:
        sample=Image.new('RGB',(192*len(raw),144))
        for i,(_,_,im) in enumerate(raw):sample.paste(im.convert('RGB'),(192*i,0))
        pal=sample.quantize(colors=32,dither=Image.Dither.NONE)
        native={}
        for clip,i,im in raw:
            frame=quantize(im,palette=pal);native[(clip,i)]=frame
        # Idle frame 4 narrows its chassis. Return to the stable first whole pose instead.
        if ('idle',3) in native:native[('idle',3)]=native[('idle',0)].copy()
        contact=Image.new('RGBA',(192*6,144*3),(18,27,38,255))
        for (clip,i),frame in native.items():
            target=OUT/'Warden'/clip/f'{i:02}.png';target.parent.mkdir(parents=True,exist_ok=True);frame.save(target)
            contact.alpha_composite(frame,(i*192,['idle','attack','stagger'].index(clip)*144))
        (ART/'qa').mkdir(exist_ok=True);contact.resize((2304,864),Image.Resampling.NEAREST).save(ART/'qa/native-contact.png')
        for clip,count in [('idle',4),('attack',6),('stagger',4)]:
            if (clip,0) not in native:continue
            frames=[native[(clip,i)] for i in range(count)]
            display=[]
            for frame in frames:
                bg=Image.new('RGBA',frame.size,(18,27,38,255));bg.alpha_composite(frame);display.append(bg.resize((576,432),Image.Resampling.NEAREST).convert('RGB'))
            timing={'idle':[400,140,300,600],'attack':[200,250,80,100,140,200],'stagger':[100,100,180,500]}[clip]
            display[0].save(ART/'qa'/f'{clip}.gif',save_all=True,append_images=display[1:],duration=timing,loop=0,disposal=2)
        (ART/'native-motion-export.json').write_text(json.dumps({'rows':motion,'idle_selection':[0,1,2,0],'note':'Constant scale per strip; body parts never split. Runtime attack frames follow telegraph/active/recovery state, not constant fps.'},indent=2),encoding='utf-8')
    report=[]
    for p in sorted(OUT.rglob('*.png')):
        im=Image.open(p).convert('RGBA');alpha=set(im.getchannel('A').getdata())
        assert alpha.issubset({0,255}),p
        report.append({'file':str(p.relative_to(OUT)).replace('\\','/'),'size':im.size,'colors':len(set(im.getdata())), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'binary_alpha':True})
    (ART/'pixel-export.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(f'Exported and checked {len(report)} native assets.')
if __name__=='__main__':main()
