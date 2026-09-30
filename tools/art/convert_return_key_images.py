"""Convert independently generated STATIC key images, never generated animation frames.

The grid boards contain different component designs. Each native base records its
own crop and hash. Exposure animation happens later in author_return_feedback.py.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, shutil

R=Path(__file__).resolve().parents[2]; A=R/'art/return-v5-feedback'
C=A/'Source/Concepts'; N=A/'Source/Native'; N.mkdir(parents=True,exist_ok=True)
P=R/'unity/TiqueReturnPrototype'; base=Image.open(P/'Assets/Resources/Return/Tique/Idle/00.png').convert('RGBA')
palette=[(16,25,33),(35,35,39),(55,46,43),(84,62,48),(121,83,51),(164,110,57),(199,144,69),(239,183,88),(255,214,133),(255,241,197),(32,64,72),(41,94,108),(50,146,169),(25,193,209),(81,224,223),(167,249,241),(234,255,246),(60,76,87),(86,116,130),(121,143,153),(136,125,104),(182,161,126),(229,208,170)]
records=[]
def quantize(im,pal=palette):
    out=Image.new('RGBA',im.size)
    out.putdata([(*min(pal,key=lambda q:sum((q[i]-c[i])**2 for i in range(3))),255) if c[3]>=128 else (0,0,0,0) for c in im.getdata()])
    return out
def convert(name,source,crop,size,ground=False,rotate=False):
    src=Image.open(C/source).convert('RGBA'); w,h=src.size
    box=tuple(round(v*(w if i%2==0 else h)) for i,v in enumerate(crop)); component=src.crop(box)
    if source.startswith('misc-'):
        # The generated reference contains unwanted bloom. Remove its dim
        # background before conversion; final assets have no glow or soft alpha.
        component.putdata([c if max(c[:3])>=70 else (0,0,0,0) for c in component.getdata()])
    # Remove only transparent padding around this independent static design.
    mask=component.getchannel('A').point(lambda v:255 if v>=160 else 0)
    b=mask.getbbox(); assert b,(name,box)
    component=component.crop(b)
    if rotate:component=component.transpose(Image.Transpose.ROTATE_90)
    maxw,maxh=size[0]-2,size[1]-2; s=min(maxw/component.width,maxh/component.height)
    dw,dh=max(1,round(component.width*s)),max(1,round(component.height*s))
    small=quantize(component.resize((dw,dh),Image.Resampling.BOX)); im=Image.new('RGBA',size)
    im.alpha_composite(small,((size[0]-dw)//2,size[1]-2-dh if ground else (size[1]-dh)//2))
    im.save(N/(name+'.png'))
    records.append({'name':name,'source':source,'sourceSha256':hashlib.sha256((C/source).read_bytes()).hexdigest(),'cropPixels':box,'contentBounds':b,'nativeSize':size,'method':'static component -> BOX area sample -> fixed palette -> binary alpha -> native pixel cleanup','nativeSha256':hashlib.sha256((N/(name+'.png')).read_bytes()).hexdigest()})
    return im

if __name__=='__main__':
    for name,col,row,size,ground in [('hit',0,0,(24,24),False),('armor',1,0,(20,16),False),('hurt',2,0,(24,24),False),('dust',3,0,(32,16),True),('boost',0,1,(24,24),False),('slam-dust',1,1,(96,24),True),('bridge',2,1,(32,32),False),('orb-stop',3,1,(24,16),False)]:
        bounds=(col/4,row/2,(col+1)/4,(row+1)/2)
        if name=='slam-dust':bounds=(.23,.5,.54,1)
        convert(name,'feedback-components-v3.png',bounds,size,ground)
    ui=['heart-full','heart-empty','iron-full','iron-empty','panel','button','button-selected','button-pressed','button-disabled','icon-undo','icon-reset','icon-hint','icon-jump','icon-attack','icon-dash','icon-interact']
    for i,name in enumerate(ui):
        size=(16,16) if 'heart' in name else (10,12) if 'iron' in name else (9,9) if name=='panel' or name.startswith('button') else (12,12)
        convert(name,'ui-components-v3.png',(i%4/4,i//4/4,(i%4+1)/4,(i//4+1)/4),size,rotate=name.startswith('iron'))
    if (C/'misc-components-v3.png').exists():
        for i,(name,size) in enumerate([('protect',(24,24)),('icon-locked',(12,12)),('icon-circuit',(12,12)),('chute',(48,40)),('icon-pause',(12,12)),('air',(20,16))]):
            convert(name,'misc-components-v3.png',(i%3/3,i//3/2,(i%3+1)/3,(i//3+1)/2),size)
    # Poses keep the approved head, heart, torso and feet. Only arm pixels from
    # each single image enter the native base; no generated full-frame reskin.
    nativepal=list({c[:3] for c in base.getdata() if c[3]})
    for name in ['push-side','push-up','push-down','hurt-pose']:
        file=C/(name+('-v4.png' if name=='push-down' else '-v3.png' if name!='hurt-pose' else '-v2.png'))
        if not file.exists():continue
        src=quantize(Image.open(file).convert('RGBA').resize((64,64),Image.Resampling.BOX),nativepal)
        src.save(N/(name+'-converted.png'))
        im=base.copy()
        # Remove original hanging arms, keeping the approved chest silhouette.
        for y in range(34,48):
            for x in list(range(16,24))+list(range(43,50)):
                im.putpixel((x,y),(0,0,0,0))
        # Two distinct arms: far arm ABOVE the heart; near arm at its right.
        # Include shoulder occlusion, but never replace cyan heart pixels.
        for y in range(33,46):
            for x in range(24,54):
                c=src.getpixel((x,y)); old=base.getpixel((x,y))
                cyan=old[3] and old[1]>old[0]*1.4 and old[2]>old[0]*1.4
                arm=(y<=38 and x>=25) or (x>=40 and y<=44)
                if name=='push-down':arm=(x<28 and y>=35) or (x>=41 and y>=35) or (y>=43 and 28<=x<=42)
                if arm and not cyan and c[3]: im.putpixel((x,y),c)
        # Pixels connecting original shoulders to sampled forearms are repairs
        # on the converted pose, not a replacement parametric skeleton.
        if name=='push-side':
            # Align both sampled palms with the next tile's near face (21px
            # from actor center for a weight, 23px for an orb). Their size is
            # unchanged; only the short connected extension gains 6 pixels.
            upper=im.crop((44,33,49,39));lower=im.crop((44,39,49,45))
            for y in range(33,45):
                for x in range(44,55):im.putpixel((x,y),(0,0,0,0))
            im.alpha_composite(upper,(50,33));im.alpha_composite(lower,(50,39))
            for y in [35,36,37,41,42,43]:
                for x in range(43,51):im.putpixel((x,y),(199,144,69,255) if y in [35,41] else (121,83,51,255))
            for y in [34,38,40,44]:
                for x in range(44,50):im.putpixel((x,y),(35,35,39,255))
            im.putpixel((49,39),(0,0,0,0))
        if name=='push-down':
            for y in range(46,48):
                for x in range(28,43):
                    c=src.getpixel((x,y))
                    if c[3]:im.putpixel((x,y),c)
            # Separate the two sampled small mittens from the heart outline.
            # Their scale stays 4x4 pixels; no fingers or enlarged gloves.
            for crop,dest in [((30,43,34,47),(25,44)),((36,43,40,47),(41,44))]:
                im.alpha_composite(src.crop(crop),dest)
            for x,y in [(26,43),(42,43)]:im.putpixel((x,y),(121,83,51,255))
        im.save(N/(name+'-v3.png'))
        records.append({'name':name,'source':file.name,'sourceSha256':hashlib.sha256(file.read_bytes()).hexdigest(),'nativeSize':[64,64],'method':'single pose downsample; original body/heart/head/feet locked; short connected arm patches','nativeSha256':hashlib.sha256((N/(name+'-v3.png')).read_bytes()).hexdigest()})
    (A/'source-image-map.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    contact=Image.new('RGBA',(640,400),(12,22,30,255)); d=ImageDraw.Draw(contact)
    for i,r in enumerate(records):
        name=r['name']; file=N/(name+('-v3' if name.startswith('push') or name=='hurt-pose' else '')+'.png')
        im=Image.open(file); scale=3 if im.width>32 else 4
        x=i%8*80;y=i//8*100;im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
        if im.width>76: im=Image.open(file).resize((min(76,Image.open(file).width),Image.open(file).height),Image.Resampling.NEAREST)
        contact.alpha_composite(im,(x,y+12));d.text((x,y),name,fill='white')
    contact.save(A/'native-key-images-review.png')
    print('Converted',len(records),'independent static images')
