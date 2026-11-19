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
const directed=html.replace('return {step,reset,touch,tread,scour,pressPad','return {onRock,step,reset,touch,tread,scour,pressPad').replace('return {draw,reset,resize,beginSurfaceLook',`return {lens:{
  view:setView,earthHeading,
  groundGaze(t){
    const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);};
    const prints=mission.footprints.filter(q=>!regolith.onRock(q.x,q.z));const p=prints.at(-1);
    if(!p)throw Error('No print left by walker');
    const bearing=earthHeading, cam=camera.clone(),y=ground.heightAt(p.x,p.z);
    cam.clearViewOffset();
    const nod=smooth((t-1.15)/5.20),lean=smooth((t-4.0)/4.9);
    const distance=.72-.48*lean;
    const x=p.x-distance*Math.sin(bearing),z=p.z-distance*Math.cos(bearing);
    cam.position.set(x,ground.heightAt(x,z)+1.61-.77*lean,z);
    const low=Math.atan2(y-cam.position.y,distance);
    const tilt=earthElevation+(low-earthElevation)*nod;
    cam.up.set(0,1,0);cam.fov=47-15*lean;cam.updateProjectionMatrix();
    cam.lookAt(cam.position.clone().add(v(Math.sin(bearing)*Math.cos(tilt),Math.sin(tilt),Math.cos(bearing)*Math.cos(tilt))));
    const visible=astronaut.group.visible;
    astronaut.group.visible=false;sky.position.copy(cam.position);
    try{renderer.render(scene,cam);}finally{astronaut.group.visible=visible;}
  },
  padAngle(t=0){const u=Math.min(1,t/8);yaw=2.1+.06*u;pitch=.16;zoom=wantedZoom=1.59-.15*u;dirty=true;}
},draw,reset,resize,beginSurfaceLook`).replace('requestAnimationFrame(tick);\n})();',`window.take={
  mission,world,reset,showLaunch,surfacePractice,
  step(dt,controls={}){
    bodyTime+=dt;
    if(['ascent','transfer','docking'].includes(mission.phase))world.orbit.update(dt,mission,controls);
    else mission.step(dt,controls);
    world.surfaceStep(dt,controls);draw(dt);
  },
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
 if(!fs.existsSync(path.join(dir,'assets/score.wav'))){
 const pcm=await page.evaluate(async()=>{
   const rate=32000,n=rate*134,ctx=new OfflineAudioContext(2,n,rate);makeDistanceScore(ctx).start();
   const music=await ctx.startRendering(),bytes=new Uint8Array(n*4),dv=new DataView(bytes.buffer);
   for(let ch=0;ch<2;ch++){const data=music.getChannelData(ch);for(let i=0;i<n;i++)dv.setInt16(i*4+2*ch,Math.round(Math.max(-1,Math.min(1,data[i]))*32767),true);}
   let s='';for(let i=0;i<bytes.length;i+=8192)s+=String.fromCharCode(...bytes.subarray(i,i+8192));return btoa(s);
 });
 const wav=spawn('ffmpeg',['-v','error','-y','-f','s16le','-ac','2','-ar','32000','-i','pipe:0',path.join(dir,'assets/score.wav')],{stdio:['pipe','ignore','inherit']});
 const wd=once(wav,'exit');wav.stdin.end(Buffer.from(pcm,'base64'));if((await wd)[0])throw Error('Score export failed');
 }
 for(const [shot,duration] of [['gaze',8],['bridge',12]]){
   if(process.env.SHOT&&process.env.SHOT!==shot)continue;
   await page.evaluate(shot=>{
     const f=take,m=f.mission,w=f.world;
     f.reset();f.showLaunch(false);f.surfacePractice();
     while(m.phase==='egress')m.step(1/24,{});
     w.lens.view('external');
     if(shot==='gaze'){
       m.astronautX=58;m.astronautZ=-35;m.evaFloor=null;w.lens.view('helmet');for(let i=0;i<4;i++)f.step(1/24);w.lens.view('external');
       for(let i=0;i<110;i++){const c={forward:true,cameraYaw:0};m.step(1/24,c);w.surfaceStep(1/24,c);}
       f.step(1/24);
     }else{
       m.phase='aboard';m.crewStation='eagle';m.hatchOpen=0;
       for(let i=0;i<55;i++){w.lens.padAngle();f.step(1/24);}
     }
   },shot);
   const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate','24','-vcodec','mjpeg','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p',path.join(dir,'shots',shot+'.mp4')],{stdio:['pipe','ignore','inherit']});
   const done=once(ff,'exit');
   for(let i=0;i<duration*24;i++){
     const data=await page.evaluate(({i,shot})=>{
       const f=take,m=f.mission,w=f.world;
       if(shot==='gaze')w.lens.groundGaze(i/24*1.25);
       else{
         if(i===114&&!w.orbit.start(m))throw Error('Launch failed');
         w.lens.padAngle(i/24);f.step(1/24);
       }
       return f.frame();
     },{i,shot});
     const frame=Buffer.from(data,'base64');
     if(i%48===0){console.log(shot,i);if(reviewDir)fs.writeFileSync(path.join(reviewDir,shot+'-'+String(i).padStart(3,'0')+'.jpg'),frame);}
     if(!ff.stdin.write(frame))await once(ff.stdin,'drain');
   }
   ff.stdin.end();if((await done)[0])throw Error('Encode failed: '+shot);
 }
}finally{await browser.close();server.close();}
