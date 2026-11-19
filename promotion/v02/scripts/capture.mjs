import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {createServer} from 'node:http';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
const dir=fileURLToPath(new URL('../',import.meta.url)),root=path.resolve(dir,'../..');
const reviewDir=process.env.FRAME_REVIEW;
if(reviewDir)fs.mkdirSync(reviewDir,{recursive:true});
const require=createRequire(import.meta.url);
let playwright;
try {playwright=require('playwright-core');}
catch {playwright=require(path.join(root,'../assGame/prototype/web/node_modules/playwright-core'));}
const chrome=process.env.CHROME||path.join(process.env.HOME,'Library/Caches/ms-playwright/chromium_headless_shell-1217/chrome-headless-shell-mac-arm64/chrome-headless-shell');
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const directed=html.replace('camFocus.copy(surveyAnchor);\n    setFov',`// The virtual camera clears the right shoulder while still looking at Earth.
    const shoulder=T.MathUtils.smoothstep(radius,0,.36)*(1-T.MathUtils.smoothstep(radius,25,150));
    const lateral=shoulder*(1.12+.11*Math.min(radius,19));
    camera.position.x-=Math.cos(earthHeading)*lateral;
    camera.position.z+=Math.sin(earthHeading)*lateral;
    camera.position.y+=.18*shoulder;
    camFocus.copy(surveyAnchor);
    setFov`).replace('return {draw,reset,resize,beginSurfaceLook',`return {lens:{
  gaze(y,p){head=earthHeading+y;elevation=p;dirty=true;},
  view:setView,earthHeading,earthElevation,
  pull(range,p){if(!surfaceCamera)zoomFromSurface(1.001);wantedZoom=zoom=1+range/surfaceCamera.unit;pitch=p;dirty=true;},
  measure(){const pos=new T.Vector3(Math.sin(earthHeading)*Math.cos(earthElevation),Math.sin(earthElevation),Math.cos(earthHeading)*Math.cos(earthElevation)).multiplyScalar(3780);
    const projected=pos.project(camera);return {earthX:projected.x,earthY:projected.y,heading:mission.heading,earthHeading,range:spaceRange};}
},draw,reset,resize,beginSurfaceLook`).replace('requestAnimationFrame(tick);\n})();',`window.take={
  mission,world,reset,showLaunch,surfacePractice,makeSuitBreathBuffer,suitExertion,
  step(dt,action={}){const controls={...input(),...action};bodyTime+=dt;mission.step(dt,controls);world.surfaceStep(dt,controls);draw(dt);},
  frame(){return canvas.toDataURL('image/jpeg',.93).split(',')[1];}
};})();`);
if(!directed.includes('window.take=')||!directed.includes('return {lens:'))throw Error('Missing capture hooks');
const server=createServer((req,res)=>{res.setHeader('Content-Type','text/html;charset=utf-8');res.end(directed);});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const browser=await playwright.chromium.launch({executablePath:chrome,args:['--use-gl=angle','--use-angle=metal','--enable-unsafe-swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
 page.on('pageerror',e=>console.error(e));
 await page.goto('http://127.0.0.1:'+server.address().port,{timeout:150000});
 await page.waitForFunction(()=>window.take,null,{timeout:90000});
 const breath=await page.evaluate(()=>{
   const m=take.mission,w=take.world;take.reset();take.showLaunch(false);take.surfacePractice();
   while(m.phase==='egress')m.step(1/24,{});
   m.astronautX=58;m.astronautZ=-35;m.evaFloor=null;
   w.lens.view('helmet');w.lens.gaze(.52,-.24);
   for(let i=0;i<5;i++)take.step(1/24);
   const ctx=new OfflineAudioContext(1,1,24000);
   const buffer=take.makeSuitBreathBuffer(ctx);return Array.from(buffer.getChannelData(0),v=>Math.round(Math.max(-1,Math.min(1,v))*32767));
 });
 const pcm=new Int16Array(breath);
 const wav=spawn('ffmpeg',['-v','error','-y','-f','s16le','-ar','24000','-ac','1','-i','pipe:0',path.join(dir,'assets/breath.wav')],{stdio:['pipe','ignore','inherit']});
 const audioDone=once(wav,'exit');wav.stdin.end(Buffer.from(pcm.buffer));if((await audioDone)[0])throw Error('Breath export failed');
 const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate','24','-vcodec','mjpeg','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p',path.join(dir,'shots/surface.mp4')],{stdio:['pipe','ignore','inherit']});
 const done=once(ff,'exit');const log=[];
 for(let i=0;i<36*24;i++){
   const result=await page.evaluate(i=>{
     const t=i/24,w=take.world,m=take.mission;
     const clamp=v=>Math.min(1,Math.max(0,v)),s=v=>{v=clamp(v);return v*v*(3-2*v);};
     if(t<10.5){
        const turn=s((t-2.7)/4.2);
        w.lens.gaze(.52*(1-turn),-.24+(.24+w.lens.earthElevation)*turn);
     }else{
        // Slow near the suit, accelerating in log-distance only once it is small.
        const elapsed=t-10.5;
        const logRange=elapsed<12?Math.log(18)*Math.pow(elapsed/12,1.65):
          Math.log(18)+13.56*(.33*clamp((elapsed-12)/13)+.67*s((elapsed-12)/13));
        const range=Math.expm1(logRange);
        w.lens.pull(range,-.14+.13*s(elapsed/9)+.53*s((elapsed-12)/12));
     }
     take.step(1/24,{forward:t<5.35});
     return {frame:take.frame(),exertion:take.suitExertion(m),...w.lens.measure()};
   },i);
   const {frame,...state}=result;const bytes=Buffer.from(frame,'base64');log.push(state);
   if(i%48===0){
     if(reviewDir)fs.writeFileSync(path.join(reviewDir,'frame-'+String(i).padStart(4,'0')+'.jpg'),bytes);
     console.log(i,state);
   }
   if(!ff.stdin.write(bytes))await once(ff.stdin,'drain');
 }
 ff.stdin.end();if((await done)[0])throw Error('Surface encode failed');
 fs.writeFileSync(path.join(dir,'shots/surface-motion.json'),JSON.stringify(log));
}finally{await browser.close();server.close();}
