"""Assemble the two local review cuts from the 24 fps game captures."""
import json, math, os, subprocess, tempfile
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw,ImageFont,ImageOps

base=Path(__file__).resolve().parents[1]
os.chdir(base)
previous=base.parent/'v01'
v2=base.parent/'v02'
assets=previous/'assets'
out=base/'outputs'
out.mkdir(exist_ok=True)
scratch=tempfile.TemporaryDirectory(prefix='amoon-v03-edit-')
work=Path(scratch.name)
fontdir=Path('/System/Library/Fonts/Supplemental')
def font(name,size,index=0):
    return ImageFont.truetype(str(fontdir/name),size,index=index)
def ff(*args):
    subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-y',*map(str,args)],check=True)
def timed(t,ass):
    n=round(t*(100 if ass else 1000));sec,frac=divmod(n,100 if ass else 1000);mins,sec=divmod(sec,60);h,mins=divmod(mins,60)
    return f'{h}:{mins:02}:{sec:02}.{frac:02}' if ass else f'{h:02}:{mins:02}:{sec:02},{frac:03}'

enc=['-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p','-r','24','-an']
# The archive photograph leads into the moving, side-by-side gravity experiment.
paper=(10,13,15);ivory=(236,231,215);muted=(183,192,191);accent=(220,177,128)
photo=Image.open(assets/'apollo11-bootprint.jpg').convert('RGB')
photo=ImageOps.fit(photo,(3200,1800),centering=(.49,.53))
photo.save(work/'photo.jpg',quality=96)
tag=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(tag)
d.rounded_rectangle((71,70,683,171),radius=4,fill=(13,15,16,195))
d.text((94,79),'APOLLO 11    /    JULY 1969',font=font('Courier New Bold.ttf',28),fill=ivory)
d.text((95,125),'NASA  /  EDWIN ALDRIN  /  AS11-40-5878',font=font('Courier New.ttf',20),fill=muted)
tag.save(work/'tag.png')
ff('-loop','1','-framerate','24','-i',work/'photo.jpg','-i',work/'tag.png','-filter_complex',
   "[0:v]zoompan=z='1+.035*on/168':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1920x1080:fps=24[p];[p][1:v]overlay",'-t','7',*enc,work/'photo.mp4')
plate=Image.new('RGB',(1920,1080),paper);d=ImageDraw.Draw(plate)
for x,heading,label in [(78,'1971   /   APOLLO 15','NASA  /  HAMMER AND FEATHER'),(986,'2026   /   IN GAME','RETURN TO THE MOON  /  ROCK AND FEATHER')]:
    d.text((x,131),heading,font=font('Courier New Bold.ttf',33),fill=ivory)
    d.text((x,859),label,font=font('Courier New.ttf',26),fill=muted)
plate.save(work/'comparison.png')
ff('-loop','1','-framerate','24','-i',work/'comparison.png','-ss','59.05','-i',assets/'apollo15.m4v','-i',previous/'shots/experiment.mp4',
   '-filter_complex',"[1:v]fps=24,scale=856:642,setsar=1[l];[2:v]crop=1440:1080,scale=856:642,setsar=1[r];[0:v][l]overlay=78:198[p];[p][r]overlay=986:198",'-t','6',*enc,work/'experiment-pair.mp4')
ff('-ss','6','-i',previous/'shots/experiment.mp4','-t','2',*enc,work/'experiment-tail.mp4')

# Use the game's lunar globe as the last image.
ff('-ss','25.65','-i',previous/'shots/surface.mp4','-frames:v','1',work/'moon.jpg')
globe=Image.open(work/'moon.jpg').convert('RGB')
card=Image.new('RGB',(1920,1080),globe.getpixel((0,0)))
card.paste(globe.resize((2688,1512),Image.Resampling.LANCZOS),(14,-210))
d=ImageDraw.Draw(card)
d.text((150,286),'2 0 2 6',font=font('Courier New.ttf',39),fill=accent)
d.line((152,373,235,373),fill=accent,width=3)
d.text((143,406),'重返月球',font=font('Songti.ttc',135),fill=ivory)
d.text((151,600),'Return to the Moon',font=font('Baskerville.ttc',74),fill=ivory)
d.text((154,755),'宁舟游戏',font=font('Songti.ttc',32),fill=muted)
card.save(work/'title.jpg',quality=98)
ff('-loop','1','-framerate','24','-i',work/'title.jpg','-vf','fade=t=in:d=0.4,fade=t=out:st=3.65:d=0.35','-t','4',*enc,work/'title.mp4')
# The Earth seen in the visor returns at the end, using the same in-game globe.
end=Image.open(base/'assets/earth.jpg').convert('RGB')
ed=ImageDraw.Draw(end)
ed.text((119,405),'以蓝色出发，驶向永恒。',font=font('Songti.ttc',76),fill=ivory)
ed.text((124,540),'From our blue Earth,',font=font('Baskerville.ttc',56),fill=ivory)
ed.text((124,607),'we sail into eternity.',font=font('Baskerville.ttc',56),fill=ivory)
end.save(work/'end.jpg',quality=97)
ff('-loop','1','-framerate','24','-i',work/'end.jpg','-vf','fade=t=in:d=0.36,fade=t=out:st=5:d=0.5','-t','5.5',*enc,work/'end.mp4')
# Use the established NeoZou lockup with a low-luminance field before the lunar night.
brand=Image.open(v2/'assets/brand-source.png').convert('L')
bg=brand.getpixel((0,0))
matte=brand.point(lambda value:max(0,min(255,(bg-value)*255/(bg-34))))
night=Image.new('RGB',brand.size,(7,9,12))
night.paste(Image.new('RGB',brand.size,ivory),(0,0),matte)
night.save(work/'brand.png')
ff('-loop','1','-framerate','24','-i',work/'brand.png','-vf','fade=t=out:st=2.32:d=0.55','-t','3',*enc,work/'brand.mp4')
segments=[work/'brand.mp4',v2/'shots/surface.mp4',base/'shots/return.mp4',work/'photo.mp4',work/'experiment-pair.mp4',work/'experiment-tail.mp4',base/'shots/rover.mp4',previous/'shots/cabin.mp4',previous/'shots/dock.mp4',work/'title.mp4',work/'end.mp4']
(work/'list.txt').write_text(''.join("file '"+str(s)+"'\n" for s in segments))
ff('-f','concat','-safe','0','-i',work/'list.txt','-c','copy',work/'picture.mp4')
allcues=json.loads((previous/'cues.json').read_text())
timings={'gentle':19.2,'rage':30.8,'dark':17.3,'light':22.0,'stars':28.7,'night':34.2,
         'drop':69.25,'again':98.75,'contact':107.2,'latch':117.25,'welcome':119.05}
allcues=[{**row,'start':timings[row['id']]} for row in allcues if row['id'] in timings]
newcues=json.loads((base/'cues.json').read_text())
allcues.extend(newcues)
total=131.5
sr=48000
def read_audio(src,fx='anull'):
    b=subprocess.check_output(['ffmpeg','-v','error','-i',str(src),'-af',fx,'-ar',str(sr),'-ac','2','-f','f32le','-'])
    return np.frombuffer(b,np.float32).reshape(-1,2).copy()
rng=np.random.default_rng(721)
score=read_audio(base/'assets/score.wav')
styles='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: EN,Georgia,59,&H00F2F2EE,&H00FFFFFF,&H38080808,&H99000000,0,0,0,0,100,100,0.2,0,1,2.6,1.4,2,88,88,122,1
Style: ZH,Hiragino Sans GB,65,&H00FFFFFF,&H00FFFFFF,&H24080808,&H99000000,0,0,0,0,100,100,1.3,0,1,2.8,1.5,2,88,88,55,1
Style: Credit,Arial,24,&H00C9CCC7,&H00FFFFFF,&H70000000,&H70000000,0,0,0,0,100,100,0.7,0,1,1,0,1,153,30,63,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
def event(a,b,style,text):return f'Dialogue: 0,{timed(a,True)},{timed(b,True)},{style},,0,0,0,,{text}\n'
for version,title,excluded,credit in [
 ('thomas','良夜',{'dark','light','stars','night'},'Poetry   Dylan Thomas  ·  Do not go gentle into that good night'),
 ('williams','老天文学家',{'gentle','rage'},'Poetry   Sarah Williams  ·  The Old Astronomer  (1868)')]:
    cues=sorted([r for r in allcues if r['id'] not in excluded],key=lambda r:r['start'])
    mix=np.zeros((int(total*sr),2),np.float32)
    def add(t,audio):
        if audio.ndim==1:audio=np.repeat(audio[:,None],2,axis=1)
        at=round(t*sr);n=min(len(audio),len(mix)-at);mix[at:at+n]+=audio[:n]
    # The score enters after the helmet releases and fades under the incoming radio call.
    n=len(score);t=np.arange(n)/sr
    music_in=14.9
    curve=np.interp(t,[0,3.9,12,20,24,39,43,53,61,66,73,81,84,94,101,107,110,116.45],[0,.59,.97,1.12,.80,.48,.38,.7,.96,.70,.88,1.09,.56,.52,.57,.86,.80,0])
    add(music_in,score*curve[:,None])
    # Use the game's inhale/exhale buffer, tracking the actual captured locomotion.
    breath=read_audio(v2/'assets/breath.wav')[:,0]
    motion=json.loads((v2/'shots/surface-motion.json').read_text())
    effort=np.array([row['exertion'] for row in motion])
    bt=np.arange(8*sr)/sr
    level=np.interp(bt,np.arange(len(effort))/24,effort)
    last_motion=np.flatnonzero(effort>.08)[-1]/24
    envelope=np.interp(bt,[0,.28,last_motion,last_motion+.58,7.99],[0,1,1,0,0])
    speed=.90+.18*level
    samples=np.cumsum(speed)%len(breath)
    air=np.interp(samples,np.arange(len(breath)),breath)*(.32+.14*level)*envelope
    add(3,air)
    # The short airborne release also carries a breath via the suit microphone.
    add(54.7,breath[:3*sr]*.17*np.hanning(3*sr))
    add(70.0,breath[:int(1.45*sr)]*.24*np.minimum(1,np.arange(int(1.45*sr))[::-1]/(.3*sr)))
    for start in [.65,1.82,3.05,4.29,5.64]:
        t=np.arange(round(sr*.19))/sr
        add(3+start,.042*np.sin(2*np.pi*(57*t+12*t*t))*np.exp(-23*t)*(1-np.exp(-150*t)))
    t=np.arange(round(sr*.19))/sr
    for at,level in [(116.96,.095),(117.04,.054)]:
        add(at,level*np.sin(2*np.pi*133*t)*np.exp(-34*t)*(1-np.exp(-300*t)))
    ass=styles;srt=[]
    for i,r in enumerate(cues):
        radio=r['id'] in {'contact','welcome','latch','drop'}
        fx='highpass=f=285,lowpass=f=3200,acompressor=threshold=0.12:ratio=2' if radio else 'highpass=f=65,lowpass=f=12500'
        voice_source=base/'assets/voice'/(r['id']+'.wav')
        if not voice_source.exists():voice_source=assets/'voice'/(r['id']+'.wav')
        wav=read_audio(voice_source,fx)
        a=r['start'];b=a+len(wav)/sr
        wav*=.107/(np.sqrt(np.mean(wav**2))+.00001)
        add(a,wav)
        if radio:
            for pos in [a-.055,b-.016]:
                ns=rng.standard_normal(1900);add(pos,.015*ns*np.hanning(len(ns)))
        finish=min(b+.29,cues[i+1]['start']-.12 if i+1<len(cues) else total-.55)
        for lang,sty,baseline in [('en','EN',949),('zh','ZH',1025)]:
            if r['id']=='boots':baseline-=745
            if r['id']!='sail':ass+=event(a,finish,sty,r'{\an2\pos(960,'+str(baseline)+r')\fad(90,150)}'+r[lang])
        srt.append(f"{i+1}\n{timed(a,False)} --> {timed(finish,False)}\n{r['en']}\n{r['zh']}\n")
    ass+=event(122.50,125.6,'Credit',r'{\fad(350,350)}'+credit+r'\NGloves   Andriano Milanovic  ·  adapted under CC BY 4.0')
    assfile=work/(version+'.ass');assfile.write_text(ass)
    (out/(title+'-双语字幕.srt')).write_text('\n'.join(srt))
    sf.write(work/'mix.wav',mix,sr,subtype='FLOAT')
    final=out/('重返月球2026-v03-'+title+'.mp4')
    ff('-i',work/'picture.mp4','-i',work/'mix.wav','-map','0:v:0','-map','1:a:0','-vf',f'ass={assfile}','-af','loudnorm=I=-17:TP=-1.3:LRA=12','-ar','48000','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-movflags','+faststart','-t',str(total),final)
    print(final,flush=True)
