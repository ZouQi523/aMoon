import fs from 'node:fs';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {createServer} from 'node:http';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
const dir=fileURLToPath(new URL('../',import.meta.url)), root=path.resolve(dir,'../..');
const req=createRequire(import.meta.url);
let playwright;
try {playwright=req('playwright-core');}
catch {playwright=req(path.join(root,'../assGame/prototype/web/node_modules/playwright-core'));}
const {chromium}=playwright;
const localChrome=path.join(process.env.HOME,'Library/Caches/ms-playwright/chromium_headless_shell-1217/chrome-headless-shell-mac-arm64/chrome-headless-shell');
const chrome=process.env.CHROME||(fs.existsSync(localChrome)?localChrome:null);
const reviewDir=process.env.FRAME_REVIEW || '/tmp/amoon-film';
fs.mkdirSync(reviewDir,{recursive:true});
const fps=24,W=1920,H=1080;
const original=fs.readFileSync(path.join(root,'index.html'),'utf8');
// Add controls only to the copy delivered by the local recording server.
const pageSource=original.replace('return {draw,reset,resize,beginSurfaceLook',`return {film:{
  footprint(t){
    const p=mission.footprints.at(-3);
    if(!p)throw Error('No planted boot available for the archive comparison');
    const y=ground.heightAt(p.x,p.z);
    const cam=camera.clone();cam.clearViewOffset();cam.fov=38;cam.updateProjectionMatrix();
    cam.position.set(p.x+.10+.032*t,y+.67-.016*t,p.z+.25);
    cam.up.set(Math.sin(p.heading),0,Math.cos(p.heading));cam.lookAt(p.x,y,p.z);renderer.render(scene,cam);
  },
  eye(h,e){head=h;elevation=e; dirty=true;},view:setView,
  pull(r,p){if(!surfaceCamera)zoomFromSurface(1.001);wantedZoom=zoom=1+r/surfaceCamera.unit;pitch=p;dirty=true;},
  cabin(y,p,z){cabinYaw=y;cabinPitch=p;panelZoom=z;dirty=true;},
  orbitAngle(y,p){review.yaw=y;review.pitch=p;dirty=true;}
},draw,reset,resize,beginSurfaceLook`)
.replace('requestAnimationFrame(tick);\n})();',`window.film={mission,world,practice,surfacePractice,showLaunch,reset,resize,draw,
  step(dt,extra={}){const controls={...input(),...extra};bodyTime+=dt;
    if(["ascent","transfer","docking"].includes(mission.phase))world.orbit.update(dt,mission,controls);
    else if(mission.phase!=="complete")mission.step(dt,controls);
    world.surfaceStep(dt,controls);draw(dt);},
  frame(){return canvas.toDataURL("image/jpeg",.93).split(",")[1];}};
})();`);
if(!pageSource.includes('window.film='))throw Error('Game capture hook missing');
const server=createServer((q,r)=>{r.setHeader('Content-Type','text/html;charset=utf-8');r.end(pageSource);});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=metal','--enable-unsafe-swiftshader'],...(chrome?{executablePath:chrome}:{})});
const page=await browser.newPage({viewport:{width:W,height:H},deviceScaleFactor:1});
page.on('pageerror',e=>console.error('PAGE',e.message));
const shots={surface:27,experiment:8,cabin:12,dock:12,print:7,rover:6};
try {
 await page.goto('http://127.0.0.1:'+server.address().port,{timeout:150000});
 await page.waitForFunction(()=>window.film,{},{timeout:90000});
 console.log('Game ready');
 if(!fs.existsSync(path.join(dir,'assets/score.wav'))){
 const audio=await page.evaluate(async()=>{
   const sr=44100,n=sr*69,ctx=new OfflineAudioContext(2,n,sr);
   makeDistanceScore(ctx).start();const mix=await ctx.startRendering();
   const out=new Uint8Array(n*4),a=new DataView(out.buffer);
   for(let ch=0;ch<2;ch++){const s=mix.getChannelData(ch);for(let i=0;i<n;i++)a.setInt16(4*i+2*ch,Math.round(Math.min(1,Math.max(-1,s[i]))*32767),true);}
   let b='';for(let i=0;i<out.length;i+=8192)b+=String.fromCharCode(...out.subarray(i,i+8192));return btoa(b);
 });
 const pcm=Buffer.from(audio,'base64'),head=Buffer.alloc(44);head.write('RIFF');head.writeUInt32LE(36+pcm.length,4);head.write('WAVEfmt ',8);head.writeUInt32LE(16,16);head.writeUInt16LE(1,20);head.writeUInt16LE(2,22);head.writeUInt32LE(44100,24);head.writeUInt32LE(176400,28);head.writeUInt16LE(4,32);head.writeUInt16LE(16,34);head.write('data',36);head.writeUInt32LE(pcm.length,40);fs.writeFileSync(path.join(dir,'assets/score.wav'),Buffer.concat([head,pcm]));
 }
 for(const [shot,duration] of Object.entries(shots)){
 if(process.env.SHOT && !process.env.SHOT.split(',').includes(shot))continue;
 await page.evaluate(shot=>{
 const f=film,m=f.mission,w=f.world;f.reset();f.showLaunch(false);
 if(['surface','experiment','print','rover'].includes(shot)){
    f.surfacePractice();while(m.phase==='egress')m.step(1/24,{});
    m.astronautX=shot==='surface'?-7:4;m.astronautZ=shot==='surface'?18:12;
    m.evaFloor=null;w.film.view('helmet');w.film.eye(2.81,-.18);
    for(let i=0;i<4;i++)f.step(1/24);
    if(shot==='print'){
       w.film.view('external');
       for(let i=0;i<110;i++){const c={forward:true,cameraYaw:0};m.step(1/24,c);w.surfaceStep(1/24,c);}
    }
    if(shot==='rover'){
       const approach=key=>{const pt=w.field.truck.locations(m)[key];m.astronautX=pt.x;m.astronautZ=pt.z;m.evaFloor=null;};
       approach('bay');if(!w.fieldInteract('deploy'))throw Error('Deploy failed');
       for(let i=0;i<2200&&m.roverDeployment;i++){m.step(1/24,{});w.surfaceStep(1/24,{});}
       approach('seat');if(!w.fieldInteract('enter'))throw Error('Enter failed: '+m.roverState);
       w.film.view('external');
    }
    if(shot==='experiment'){m.gear.experiment=true;w.selectTool('experiment');}
 }else{
    f.practice('columbia');m.dock.x=0;m.dock.y=0;m.dock.gap=shot==='dock'?1.85:12;
    if(shot==='dock')w.film.view('external');
    f.step(1/24);
 }
 },shot);
 if(shot==='cabin'||shot==='dock')await page.waitForFunction(()=>film.world.orbit.scanState==='ready',null,{timeout:90000});
 const test=process.env.PROBE==='1',out=path.join(dir,'shots',shot+'.mp4');
 let ff,done;
 if(!test){
 ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate','24','-vcodec','mjpeg','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p',out],{stdio:['pipe','ignore','inherit']});done=once(ff,'exit');
 }
 for(let i=0;i<duration*fps;i++){
 const keep=!test||i%48===0;
 const result=await page.evaluate(({i,shot,keep})=>{
   const t=i/24,f=film,m=f.mission,w=f.world;
   const sat=v=>Math.min(1,Math.max(0,v)),smooth=x=>{x=sat(x);return x*x*(3-2*x);};
   let controls={};
   if(shot==='surface'){
     if(t<7){w.film.eye(2.81+.16*smooth(t/7),-.29+.31*smooth(t/4));controls.forward=t<5.8;}
     else{const p=sat((t-7)/19.7),r=Math.expm1(16.45*(.64*p+.36*smooth(p)));w.film.pull(r,.19+.40*smooth(p));}
   }else if(shot==='print'){
     // The macro lens follows a footprint left by simulated locomotion.
   }else if(shot==='rover'){
     controls.forward=true;controls.left=t>2.5&&t<3.1;
   }else if(shot==='experiment'){
     controls.jump=t>=2&&t<2.1;
     if(i===59)w.field.drop.release(m);
   }else if(shot==='cabin'){
     if(i===34)w.glanceAtPanel();
     w.film.cabin(-.18*smooth((t-2)/5)+.16*smooth((t-7)/4),.045*smooth(t/5),1+.63*smooth((t-1.6)/5));
     if(i===209)w.aimRendezvous(true);
   }else{
     controls.thrust=true;if(m.dock.captureReady)w.orbit.capture(m);
     if(m.phase==='complete')w.film.orbitAngle(1.23+.08*Math.max(0,t-7),.32);
   }
   f.step(1/24,controls);if(shot==='print')w.film.footprint(t);
   return {data:keep?f.frame():null,phase:m.phase,drop:m.experimentState,scan:w.orbit.scanState,range:m.dock?.gap};
 },{i,shot,keep});
 if(keep){
 const frame=Buffer.from(result.data,'base64');
 if(i%48===0){fs.writeFileSync(reviewDir+'/'+shot+'-'+String(i).padStart(3,'0')+'.jpg',frame);console.log(shot,i,result.phase,result.drop,result.range);}
 if(ff&&!ff.stdin.write(frame))await once(ff.stdin,'drain');
 }
 }
 if(ff){ff.stdin.end();if((await done)[0])throw Error('Encoding failed');}
 }
}finally{await browser.close();server.close();}
