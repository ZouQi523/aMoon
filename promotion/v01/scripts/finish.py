"""Assemble the two local review cuts from the 24 fps game captures."""
import json, math, os, subprocess, tempfile
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw,ImageFont,ImageOps

base=Path(__file__).resolve().parents[1]
os.chdir(base)
assets=base/'assets'
out=base/'outputs'
out.mkdir(exist_ok=True)
work=Path(tempfile.mkdtemp(prefix='amoon-edit-'))
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
ff('-loop','1','-framerate','24','-i',work/'comparison.png','-ss','59.05','-i',assets/'apollo15.m4v','-i','shots/experiment.mp4',
   '-filter_complex',"[1:v]fps=24,scale=856:642,setsar=1[l];[2:v]crop=1440:1080,scale=856:642,setsar=1[r];[0:v][l]overlay=78:198[p];[p][r]overlay=986:198",'-t','6',*enc,work/'experiment-pair.mp4')
ff('-ss','6','-i','shots/experiment.mp4','-t','2',*enc,work/'experiment-tail.mp4')

# Use the game's lunar globe as the last image.
ff('-ss','25.65','-i','shots/surface.mp4','-frames:v','1',work/'moon.jpg')
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
ff('-loop','1','-framerate','24','-i',work/'title.jpg','-vf','fade=t=in:d=0.65,fade=t=out:st=6.8:d=0.7','-t','7.5',*enc,work/'title.mp4')
segments=[base/'shots/surface.mp4',work/'photo.mp4',work/'experiment-pair.mp4',work/'experiment-tail.mp4',base/'shots/rover.mp4',base/'shots/cabin.mp4',base/'shots/dock.mp4',work/'title.mp4']
(work/'list.txt').write_text(''.join("file '"+str(s)+"'\n" for s in segments))
ff('-f','concat','-safe','0','-i',work/'list.txt','-c','copy',work/'picture.mp4')
allcues=json.loads(Path('cues.json').read_text())
total=79.5
sr=48000
def read_audio(src,fx='anull'):
    b=subprocess.check_output(['ffmpeg','-v','error','-i',str(src),'-af',fx,'-ar',str(sr),'-ac','2','-f','f32le','-'])
    return np.frombuffer(b,np.float32).reshape(-1,2).copy()
rng=np.random.default_rng(721)
score=read_audio(assets/'score.wav')
styles='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: EN,Baskerville,48,&H00F4F1E9,&H00FFFFFF,&H80090606,&H99000000,0,0,0,0,100,100,0.4,0,1,1.8,1,2,65,65,96,1
Style: ZH,Hiragino Sans GB,31,&H00E2E3DE,&H00FFFFFF,&H80090606,&H99000000,0,0,0,0,100,100,1.3,0,1,1.6,1,2,65,65,52,1
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
    curve=np.interp(t,[0,3.2,7,17,22,38,47.8,50,56,61,65,68.9],[0,.62,.99,1.15,.84,.95,1,.50,.51,1.06,.92,0])
    add(8.6,score*curve[:,None])
    # Quiet suit-conducted breathing and footsteps, followed by radio squelch and latch.
    for start in [.08,3.1,5.9]:
        t=np.arange(round(sr*1.15))/sr
        noise=rng.standard_normal(len(t))
        noise=np.convolve(noise,np.ones(33)/33,mode='same')-np.convolve(noise,np.ones(200)/200,mode='same')
        add(start,.061*np.sin(np.pi*t/1.15)**1.4*noise)
    for start in [.65,1.82,3.05,4.29,5.64]:
        t=np.arange(round(sr*.19))/sr
        add(start,.042*np.sin(2*np.pi*(57*t+12*t*t))*np.exp(-23*t)*(1-np.exp(-150*t)))
    t=np.arange(round(sr*.19))/sr
    for at,level in [(66.96,.095),(67.04,.054)]:
        add(at,level*np.sin(2*np.pi*133*t)*np.exp(-34*t)*(1-np.exp(-300*t)))
    ass=styles;srt=[]
    for i,r in enumerate(cues):
        radio=r['id'] in {'contact','welcome','latch','drop'}
        fx='highpass=f=285,lowpass=f=3200,acompressor=threshold=0.12:ratio=2' if radio else 'highpass=f=65,lowpass=f=12500'
        wav=read_audio(assets/'voice'/(r['id']+'.wav'),fx)
        a=r['start'];b=a+len(wav)/sr
        wav*=.107/(np.sqrt(np.mean(wav**2))+.00001)
        add(a,wav)
        if radio:
            for pos in [a-.055,b-.016]:
                ns=rng.standard_normal(1900);add(pos,.015*ns*np.hanning(len(ns)))
        finish=min(b+.29,cues[i+1]['start']-.12 if i+1<len(cues) else 72)
        for lang,sty in [('en','EN'),('zh','ZH')]:ass+=event(a,finish,sty,r'{\fad(90,150)}'+r[lang])
        srt.append(f"{i+1}\n{timed(a,False)} --> {timed(finish,False)}\n{r['en']}\n{r['zh']}\n")
    ass+=event(72.65,78.84,'Credit',r'{\fad(350,350)}'+credit+r'\NGloves   Andriano Milanovic  ·  adapted under CC BY 4.0')
    assfile=work/(version+'.ass');assfile.write_text(ass)
    (out/(title+'-双语字幕.srt')).write_text('\n'.join(srt))
    sf.write(work/'mix.wav',mix,sr,subtype='FLOAT')
    final=out/('重返月球2026-v01-'+title+'.mp4')
    ff('-i',work/'picture.mp4','-i',work/'mix.wav','-map','0:v:0','-map','1:a:0','-vf',f'ass={assfile}','-af','loudnorm=I=-17:TP=-1.3:LRA=12','-ar','48000','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-movflags','+faststart','-t',str(total),final)
    print(final,flush=True)
