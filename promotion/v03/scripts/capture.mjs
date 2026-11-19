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
const directed=html.replace('return {step,interact,nearest,camera,reset,locations',`return {stageDrive(m){
      // Scout a continuous drive using the game's normal wheel and slope constraints.
      for(const x of [58,-80,105,35,50,72,-28,-56,96])for(const z of [-85,75,-110,24,-27,54,-60,90])for(const bearing of [.78,1.7,2.6,3.55,4.6,5.7]){
        function start(){roverX=x;roverZ=z;heading=bearing;speed=steering=wheelAngle=stepDistance=0;}
        start();let clear=true;
        for(let i=-12;i<528;i++){
          const t=i/24;
          const input={forward:true,left:t>3&&t<3.65||t>11.5&&t<12.15,right:t>17.3&&t<18};
          travel(1/45,m,input);travel(1/24-1/45,m,input);
          if(t>3.4&&speed<2){clear=false;break;}
        }
        if(clear){start();bodyReady=false;driveCam=false;synchronize(m);return;}
      }
      throw Error('No clear rover route');
    },step,interact,nearest,camera,reset,locations`)
.replace('if(position.getY(i)>1.436)return false;', 'if(position.getY(i)>.68)return false;')
.replace("const equipment=body.getObjectByName('EVA remote control unit, hoses, oxygen pack and antenna');", "const equipment=null;")
.replace('dst.visible=ladder;if(dst.visible)', 'dst.visible=ladder||(m.phase==="eva"&&forward.y<-.65);if(dst.visible)')
.replaceAll('aim.set(Math.sin(lookYaw)*Math.cos(tilt)',`if(mission.filmLean){
        camera.position.x+=Math.sin(lookYaw)*.29*mission.filmLean;
        camera.position.z+=Math.cos(lookYaw)*.29*mission.filmLean;
        tilt-=.48*mission.filmLean;
      }
      aim.set(Math.sin(lookYaw)*Math.cos(tilt)`)
.replace('if(current==="eva"&&mission.roverDriving){\n      field.truck.camera',`if(current==="eva"&&mission.roverDriving&&mission.trackShot){
      const shot=mission.trackShot, vehicle=field.truck.position;
      const h=mission.roverHeading,side=shot.side,back=shot.back;
      const x=vehicle.x+Math.cos(h)*side-Math.sin(h)*back;
      const z=vehicle.z-Math.sin(h)*side-Math.cos(h)*back;
      camera.position.set(x,Math.max(ground.heightAt(x,z)+2,vehicle.y+shot.height),z);
      camera.up.set(0,1,0);camera.lookAt(vehicle.x+Math.sin(h)*3.4,vehicle.y+1.25,vehicle.z+Math.cos(h)*3.4);
      setFov(42);camera.updateMatrixWorld();sky.position.copy(camera.position);return;
    }
    if(current==="eva"&&mission.roverDriving){
      field.truck.camera`)
.replace('camFocus.copy(surveyAnchor);\n    setFov',`// The virtual camera clears the right shoulder while still looking at Earth.
    const shoulder=T.MathUtils.smoothstep(radius,0,.36)*(1-T.MathUtils.smoothstep(radius,25,150));
    const lateral=shoulder*(1.12+.11*Math.min(radius,19));
    camera.position.x-=Math.cos(earthHeading)*lateral;
    camera.position.z+=Math.sin(earthHeading)*lateral;
    camera.position.y+=.18*shoulder;
    camFocus.copy(surveyAnchor);
    setFov`).replace('return {draw,reset,resize,beginSurfaceLook',`return {lens:{
  gaze(y,p){head=earthHeading+y;elevation=p;dirty=true;},
  blueFrame(){
    const cam=new T.PerspectiveCamera(3.15,1920/1080,1,5000);cam.position.copy(sky.position);
    const globe=sky.getObjectByName('Earth over the lunar horizon');
    cam.lookAt(globe.getWorldPosition(v()));cam.setViewOffset(1920,1080,-435,0,1920,1080);
    renderer.render(scene,cam);
  },view:setView,earthHeading,earthElevation,
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
 if(!fs.existsSync(path.join(dir,'assets/score.wav'))){
 const pcm=await page.evaluate(async()=>{
   const rate=32000,n=rate*119,ctx=new OfflineAudioContext(2,n,rate);makeDistanceScore(ctx).start();
   const music=await ctx.startRendering(),bytes=new Uint8Array(n*4),dv=new DataView(bytes.buffer);
   for(let ch=0;ch<2;ch++){const data=music.getChannelData(ch);for(let i=0;i<n;i++)dv.setInt16(i*4+2*ch,Math.round(Math.max(-1,Math.min(1,data[i]))*32767),true);}
   let s='';for(let i=0;i<bytes.length;i+=8192)s+=String.fromCharCode(...bytes.subarray(i,i+8192));return btoa(s);
 });
 const wav=spawn('ffmpeg',['-v','error','-y','-f','s16le','-ac','2','-ar','32000','-i','pipe:0',path.join(dir,'assets/score.wav')],{stdio:['pipe','ignore','inherit']});
 const wd=once(wav,'exit');wav.stdin.end(Buffer.from(pcm,'base64'));if((await wd)[0])throw Error('Score export failed');
 }
 for(const [shot,duration] of [['return',22],['rover',22]]){
   if(process.env.SHOT&&process.env.SHOT!==shot)continue;
   await page.evaluate(shot=>{
     const f=take,m=f.mission,w=f.world;f.reset();f.showLaunch(false);f.surfacePractice();
     while(m.phase==='egress')m.step(1/24,{});
     m.astronautX=shot==='return'?58:4;m.astronautZ=shot==='return'?-35:12;m.evaFloor=null;
     w.lens.view('helmet');w.lens.gaze(.52,-.24);
     for(let i=0;i<5;i++)f.step(1/24);
     if(shot==='return'){
       for(let i=0;i<=252;i++){
         const t=i/24,p=Math.max(0,Math.min(1,(t-2.7)/4.2)),u=p*p*(3-2*p);
         w.lens.gaze(.52*(1-u),-.24+(.24+w.lens.earthElevation)*u);f.step(1/24,{forward:t<5.35});
       }
       w.lens.pull(Math.expm1(Math.log(18)+13.56),.52);f.step(1/24);
     }else{
       const approach=key=>{const p=w.field.truck.locations(m)[key];m.astronautX=p.x;m.astronautZ=p.z;m.evaFloor=null;};
       approach('bay');if(!w.fieldInteract('deploy'))throw Error('Deploy failed');
       for(let i=0;i<2200&&m.roverDeployment;i++){m.step(1/24,{});w.surfaceStep(1/24,{});}
       approach('seat');if(!w.fieldInteract('enter'))throw Error('Seat unavailable');w.field.truck.stageDrive(m);
       w.lens.view('external');for(let i=0;i<12;i++)f.step(1/24,{forward:true});
     }
   },shot);
   const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate','24','-vcodec','mjpeg','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p',path.join(dir,'shots',shot+'.mp4')],{stdio:['pipe','ignore','inherit']});
   const done=once(ff,'exit');
   for(let i=0;i<duration*24;i++){
     const result=await page.evaluate(({shot,i})=>{
       const t=i/24,w=take.world,m=take.mission;
       const clamp=v=>Math.max(0,Math.min(1,v)),s=v=>{v=clamp(v);return v*v*(3-2*v);};
       let controls={};
       if(shot==='return'){
         if(i<380){
           const u=s(t/15.8),lr=(Math.log(18)+13.56)*(1-u);
           w.lens.pull(Math.max(.002,Math.expm1(lr)),.52-.65*s(u));
         }else{
           if(i===380)w.lens.view('helmet');
           m.filmLean=s((t-16.4)/3.2);
           w.lens.gaze(0,w.lens.earthElevation-1.12*s((t-16.0)/2.9));
         }
       }else{
         controls={forward:true,left:t>3.0&&t<3.65||t>11.5&&t<12.15,right:t>17.3&&t<18.0};
         if(i===108)w.lens.view('helmet');
         if(i===198)w.lens.view('external');
         if(t>=8.25){const u=s((t-8.25)/10);m.trackShot={side:11+26*u,back:8+7*u,height:4.5+12*u};}
       }
       take.step(1/24,controls);
       return {data:take.frame(),distance:m.roverDistance,mode:w.mode};
     },{shot,i});
     const frame=Buffer.from(result.data,'base64');
     if(i%48===0){console.log(shot,i,result.mode,result.distance);if(reviewDir)fs.writeFileSync(path.join(reviewDir,shot+'-'+String(i).padStart(3,'0')+'.jpg'),frame);}
     if(!ff.stdin.write(frame))await once(ff.stdin,'drain');
   }
   ff.stdin.end();if((await done)[0])throw Error('Encode failed: '+shot);
   if(shot==='return'){
     const earth=await page.evaluate(()=>{take.world.lens.blueFrame();return take.frame();});
     fs.writeFileSync(path.join(dir,'assets/earth.jpg'),Buffer.from(earth,'base64'));
   }
 }
}finally{await browser.close();server.close();}
