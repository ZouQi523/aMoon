/* R4: original suit/rig, pelvis pivot, unscaled geometry, explicit hand/foot targets. */
(async()=>{
 while(!window.independentReview)await new Promise(r=>setTimeout(r,25));
 const review=independentReview,R=eagleReview,q=review.q,T=THREE,H=q.lander.group,A=q.astronaut,B=A.limbs[0].hip.parent;
 R.mission.phase='landed';R.draw();H.attach(A.group);A.group.position.set(0,0,0);A.group.rotation.set(0,Math.PI,0);A.group.visible=true;
 const v=a=>new T.Vector3(...a),world=a=>H.localToWorld(v(a));
 // Add the missing neck degree of freedom; all source vertex positions stay unchanged.
 const skin=q.museumSuit.object,neck=new T.Group();neck.name='R4 bounded neck articulation';neck.position.set(0,1.46,0);B.add(neck);H.updateWorldMatrix(true,true);
 const helmet=B.children.find(o=>o.name==='Apollo LEVA fixed transparent shell and retractable sun visor');if(!helmet)throw Error('R4 requires original complete LEVA assembly');neck.attach(helmet);
 skin.geometry=skin.geometry.clone();const originalWeights=skin.geometry.attributes.skinWeight,floatWeights=new Float32Array(originalWeights.count*4);for(let j=0;j<originalWeights.count;j++)for(let k=0;k<4;k++)floatWeights[j*4+k]=originalWeights.getComponent(j,k);skin.geometry.setAttribute('skinWeight',new T.Float32BufferAttribute(floatWeights,4));
 const si=skin.geometry.attributes.skinIndex,sw=skin.geometry.attributes.skinWeight,positions=skin.geometry.attributes.position;
 const headBone=new T.Bone();headBone.name='R4 neck, original head geometry';neck.add(headBone);const headIndex=skin.skeleton.bones.length;
 for(let j=0;j<positions.count;j++){const f=T.MathUtils.smoothstep(positions.getY(j),1.35,1.47);if(!f)continue;for(let k=0;k<4;k++){const offset=j*4+k;if(si.array[offset]!==0||sw.array[offset]===0)continue;const weight=sw.array[offset];if(f===1){si.array[offset]=headIndex;}else{const free=[0,1,2,3].find(n=>sw.array[j*4+n]===0);if(free!==undefined){sw.array[offset]=weight*(1-f);si.array[j*4+free]=headIndex;sw.array[j*4+free]=weight*f;}}break;}}
 skin.bind(new T.Skeleton([...skin.skeleton.bones,headBone],[...skin.skeleton.boneInverses,new T.Matrix4().makeTranslation(0,-1.46,0)]),new T.Matrix4());
 const soles=A.limbs.map(l=>{const m=l.ankle.children.find(o=>o.name==='Lunar overshoe, molded tread'),p=m.geometry.attributes.position;let y=Infinity;for(let i=0;i<p.count;i++)y=Math.min(y,p.getY(i));return new T.Vector3(0,y,.065);});
 function arm(index,worldTarget){const l=A.limbs[index],target=B.worldToLocal(worldTarget.clone()),line=target.clone().sub(l.shoulder.position),a=l.elbow.position.length(),b=l.grip.position.length(),length=line.length(),span=T.MathUtils.clamp(length,Math.abs(a-b)+.0001,a+b-.0001);line.normalize();
  const normal=v([1,0,0]).transformDirection(B.matrixWorld.clone().invert().multiply(H.matrixWorld));normal.addScaledVector(line,-normal.dot(line)).normalize();const bend=new T.Vector3().crossVectors(normal,line).normalize(),along=(a*a-b*b+span*span)/(2*span),joint=l.shoulder.position.clone().addScaledVector(line,along).addScaledVector(bend,Math.sqrt(Math.max(0,a*a-along*along))),upper=joint.clone().sub(l.shoulder.position).normalize(),fore=target.clone().sub(joint).normalize();
  const upperY=upper.clone().negate();l.shoulder.quaternion.setFromRotationMatrix(new T.Matrix4().makeBasis(normal,upperY,new T.Vector3().crossVectors(normal,upperY)));
  const foreB=new T.Quaternion().setFromRotationMatrix(new T.Matrix4().makeBasis(normal,fore,new T.Vector3().crossVectors(normal,fore))).multiply(l.grip.quaternion.clone().invert());l.elbow.quaternion.copy(l.shoulder.quaternion.clone().invert().multiply(foreB));l.grip.updateWorldMatrix(true,false);
 }
 function leg(index,sole){const l=A.limbs[index],target=B.worldToLocal(world(sole)),rot=new T.Quaternion();B.getWorldQuaternion(rot).invert().multiply(H.getWorldQuaternion(new T.Quaternion()).multiply(new T.Quaternion().setFromAxisAngle(v([0,1,0]),Math.PI)));const ankle=target.sub(soles[index].clone().applyQuaternion(rot)),a=l.knee.position.length(),b=l.ankle.position.length(),dir=ankle.clone().sub(l.hip.position),length=dir.length(),span=Math.min(a+b-.0001,Math.max(Math.abs(a-b)+.0001,length));dir.normalize();
  const pole=v([index===0?.20:-.20,0,-1]).transformDirection(B.matrixWorld.clone().invert().multiply(H.matrixWorld));pole.addScaledVector(dir,-pole.dot(dir)).normalize();const along=(a*a-b*b+span*span)/(2*span),joint=l.hip.position.clone().addScaledVector(dir,along).addScaledVector(pole,Math.sqrt(Math.max(0,a*a-along*along)));
  l.hip.quaternion.setFromUnitVectors(l.knee.position.clone().normalize(),joint.clone().sub(l.hip.position).normalize());l.knee.quaternion.setFromUnitVectors(l.ankle.position.clone().normalize(),ankle.clone().sub(joint).normalize().applyQuaternion(l.hip.quaternion.clone().invert()));l.ankle.quaternion.copy(l.hip.quaternion.clone().multiply(l.knee.quaternion).invert().multiply(rot));return{requested:sole,reach:length,limit:a+b};
 }
 // h=[hipX,hipY,hipZ], pitch; sole/grip positions are in the unchanged lander coordinates.
 const keys=[
  {t:0,h:[.40,4.06,.73],p:.05,feet:[[.511,3.256,.73],[.289,3.256,.73]],hands:[[.29,4.34,.65],[.22,4.34,.65]],open:0},
  {t:2,h:[.40,4.06,.73],p:.05,feet:[[.511,3.256,.73],[.289,3.256,.73]],hands:[[.29,4.34,.65],[.22,4.34,.65]],open:1},
  {t:2.6,h:[.40,4.06,.88],p:.05,feet:[[.511,3.256,.88],[.289,3.256,.88]],hands:[[.29,4.34,.80],[.22,4.34,.80]],open:1},
  {t:3.4,h:[.35,3.80,.95],p:.90,feet:[[.461,3.256,1.10],[.239,3.256,1.10]],hands:[[.58,3.80,.48],[-.20,3.80,.63]],open:1},
  {t:4.2,h:[.20,3.80,1.05],p:1.02,feet:[[.31,3.256,1.25],[.09,3.256,1.25]],hands:[[.48,3.80,.46],[-.25,3.80,.62]],open:1},
  {t:5,h:[0,3.76,1.28],p:1.18,feet:[[.14,3.256,1.50],[-.14,3.256,1.50]],hands:[[.43,3.85,.46],[-.43,3.85,.46]],open:1},
  {t:6,h:[0,3.67,1.48],p:1.33,feet:[[.14,3.256,1.50],[-.14,3.256,1.50]],hands:[[.23,3.33,.96],[-.23,3.33,.96]],open:1},
  {t:8,h:[0,3.64,1.86],p:1.48,feet:[[.14,3.1825,1.92],[-.14,3.1825,1.92]],hands:[[.23,3.33,1.15],[-.23,3.33,1.15]],open:1},
  {t:11,h:[0,3.68,2.40],p:1.48,feet:[[.14,3.1825,1.94],[-.14,3.1825,1.94]],hands:[[.24,3.37,1.60],[-.24,3.37,1.60]],open:1},
  {t:12.2,h:[0,3.58,2.52],p:1.48,feet:[[.14,3.1825,1.96],[-.14,3.1825,1.96]],hands:[[.25,3.77,1.85],[-.25,3.77,1.85]],open:1},
  {t:13.8,h:[0,3.52,2.66],p:1.48,feet:[[.14,3.1825,1.98],[-.14,3.1825,1.98]],hands:[[.43,3.60,1.88],[-.43,3.60,1.88]],open:1},
  {t:16.2,h:[0,3.52,2.66],p:1.48,feet:[[.14,3.1825,1.98],[-.14,3.1825,1.98]],hands:[[.43,3.60,1.88],[-.43,3.60,1.88]],open:1},
 ];
 const sp=skin.geometry.attributes.position;
 const handSamples=[31613,40676].map((id,side)=>{const c=new T.Vector3().fromBufferAttribute(sp,id),ids=[],ix=skin.geometry.attributes.skinIndex,w=skin.geometry.attributes.skinWeight;for(let j=0;j<sp.count;j++){let weight=0;for(let k=0;k<4;k++)if(ix.array[j*4+k]===(side===0?5:10))weight+=w.array[j*4+k];if(weight>.5&&sp.getY(j)<1.0&&new T.Vector3().fromBufferAttribute(sp,j).distanceToSquared(c)<.20**2)ids.push(j);}return ids;});
 const PLAY_RATE=.75; // Careful suited movement: 16.2 pose units take 21.6 real seconds.
 let time=0,direction='outbound',phase='review',camera='inside',cutaway=false,playing=false,last=0,contacts=[],handContacts=[];
 function pose(t){let i=0;while(i<keys.length-2&&t>keys[i+1].t)i++;const a=keys[i],b=keys[i+1],u=T.MathUtils.smoothstep(t,a.t,b.t),blend=(x,y)=>x.map((v,i)=>T.MathUtils.lerp(v,y[i],u));const out={h:blend(a.h,b.h),p:T.MathUtils.lerp(a.p,b.p,u),feet:a.feet.map((p,i)=>blend(p,b.feet[i])),hands:a.hands.map((p,i)=>blend(p,b.hands[i])),open:T.MathUtils.lerp(a.open,b.open,u)};
  // Cross the 73.5 mm threshold one boot at a time, lifting clear before lowering.
  if(t>=5&&t<=8)for(let side=0;side<2;side++){const start=5+side*1.4,end=start+1.4,u=T.MathUtils.smoothstep(t,start,end);out.feet[side]=[side===0?.14:-.14,T.MathUtils.lerp(3.256,3.1825,u)+.12*Math.sin(Math.PI*u),T.MathUtils.lerp(1.50,1.92,u)];}
  if(t>=5&&t<=8){const path=[[5,.43,3.85,.46],[5.5,.34,3.98,.75],[6.5,.23,3.40,1.07],[8,.23,3.33,1.15]];let j=0;while(j<path.length-2&&t>path[j+1][0])j++;const a=path[j],b=path[j+1],u=T.MathUtils.smoothstep(t,a[0],b[0]);out.hands=[1,-1].map(sign=>[sign*T.MathUtils.lerp(a[1],b[1],u),T.MathUtils.lerp(a[2],b[2],u),T.MathUtils.lerp(a[3],b[3],u)]);}
  return out;}
 function render(){const p=pose(time);review.set({model:'independent',view:'front',open:p.open,overheadOpen:false,person:false,headOffset:0});
  phase=time===16.2?'porch':time===0?(direction==='inbound'?'aboard':'review'):'passage';
  for(const o of review.models.independent.root.children)if(o.isMesh)o.visible=!(cutaway&&/Pressure shell|forward skin|pressure wall|pressure bulkhead|Upper brow|Upper face roof|Central forward|roof with open|transition/.test(o.name));
  A.group.visible=true;A.group.position.set(0,0,0);A.group.rotation.set(0,Math.PI,0);B.rotation.set(p.p,0,0);neck.rotation.x=-.45*T.MathUtils.smoothstep(time,3,4.5)*(1-T.MathUtils.smoothstep(time,7,9));B.position.copy(v(p.h).applyAxisAngle(v([0,1,0]),-Math.PI).sub(v([0,.86,0]).applyEuler(B.rotation)));
  for(const l of A.limbs){l.shoulder.position.copy(l.shoulderBase);l.shoulder.rotation.set(0,0,0);l.elbow.rotation.set(0,0,0);}H.updateWorldMatrix(true,true);
  contacts=p.feet.map((s,i)=>leg(i,s));H.updateWorldMatrix(true,true);
  handContacts=[];
  for(let i=0;i<2;i++){
   const target=p.hands[i].slice(),pole=A.limbs[i].shoulder.getWorldPosition(new T.Vector3()).add(v([i===0?-.35:.35,.6,0]).transformDirection(H.matrixWorld));let correction=0,minGap=Infinity;
   for(let n=0;n<5;n++){
    arm(i,world(target));H.updateWorldMatrix(true,true);skin.updateMatrixWorld(true);skin.skeleton.update();const mat=H.matrixWorld.clone().invert().multiply(skin.matrixWorld),sample=new T.Vector3();minGap=Infinity;
    for(const id of handSamples[i]){sample.fromBufferAttribute(sp,id);skin.applyBoneTransform(id,sample).applyMatrix4(mat);let floor=T.MathUtils.lerp(3.7153,3.25,T.MathUtils.smoothstep(time,5.8,6.8));
     floor=T.MathUtils.lerp(floor,3.584,T.MathUtils.smoothstep(time,11.8,12.2));
     minGap=Math.min(minGap,sample.y-floor);
    }
    const dy=.003-minGap;if(dy<=.0005)break;target[1]+=dy;correction+=dy;
   }
   // Fit the actual curved rail after the conservative plane approach.
   // Move the hand target, never scale/translate glove vertices independently.
   const planeTarget=target.slice(),railBlend=T.MathUtils.smoothstep(time,12.2,13.5);
   if(railBlend>0)for(let n=0;n<8;n++){
    arm(i,world(target));H.updateWorldMatrix(true,true);skin.updateMatrixWorld(true);skin.skeleton.update();const mat=H.matrixWorld.clone().invert().multiply(skin.matrixWorld),point=new T.Vector3();let nearest=null;minGap=Infinity;
    for(const id of handSamples[i]){point.fromBufferAttribute(sp,id);skin.applyBoneTransform(id,point).applyMatrix4(mat);if(point.z<1.50||point.z>2.0)continue;const dx=point.x-(i===0?.43:-.43),dy=point.y-3.56,r=Math.hypot(dx,dy),gap=r-.024;if(gap<minGap){minGap=gap;nearest=[dx/r,dy/r];}}
    if(!nearest||Math.abs(minGap-.003)<.0003)break;const shift=T.MathUtils.clamp(minGap-.003,-.02,.02);target[0]-=nearest[0]*shift;target[1]-=nearest[1]*shift;
   }
   if(railBlend>0){for(let k=0;k<3;k++)target[k]=T.MathUtils.lerp(planeTarget[k],target[k],railBlend);arm(i,world(target));H.updateWorldMatrix(true,true);}
   const actual=H.worldToLocal(A.limbs[i].grip.getWorldPosition(new T.Vector3()));handContacts.push({target,actual:actual.toArray(),reachError:actual.distanceTo(v(target)),minSupportGap:minGap,correction});
  }H.updateWorldMatrix(true,true);q.museumSuit.update(1,true);
  const views={section:[[3.6,4.35,1.55],[0,3.9,1.5],49],inside:[[-.35,4.9,.2],[0,3.65,1.6],74],outside:[[2.8,4.8,4.8],[0,3.95,1.55],48],porch:[[2.7,4.5,3.8],[0,3.7,1.95],45]};const [eye,target,fov]=views[camera];q.camera.position.copy(world(eye));q.camera.up.set(0,1,0);q.camera.lookAt(world(target));q.camera.fov=fov;q.camera.aspect=innerWidth/innerHeight;q.camera.updateProjectionMatrix();q.camera.updateMatrixWorld(true);q.renderer.render(q.scene,q.camera);
  document.getElementById('r4status').textContent='舱口／平台 · '+(direction==='outbound'?'出舱':'返舱')+' · t='+(time/PLAY_RATE).toFixed(2)+' s · '+phase;
  document.getElementById('r4time').value=time;
 }
 const oldControls=document.getElementById('independent-review-controls'),controls=document.createElement('div');controls.id='r4-controls';controls.style.cssText=oldControls.style.cssText;oldControls.style.display='none';document.body.append(controls);controls.innerHTML='<strong>R4 独立试玩 · 仅舱口／平台</strong><button id="r4reset">起点</button><button id="r4play">播放／暂停</button><button id="r4return">反向检查</button><button data-cam="section">侧剖</button><button data-cam="inside">舱内</button><button data-cam="outside">舱外</button><button data-cam="porch">平台</button><button id="r4cut">完整／剖视</button><input id="r4time" type="range" min="0" max="16.2" step="0.05" value="0"><span id="r4status"></span>';
 function state(){return{phase,direction,ladderTime:time,poseParameter:time,cycleTime:time/PLAY_RATE,hatchOpen:pose(time).open,bodyPosition:H.worldToLocal(B.getWorldPosition(new T.Vector3())).toArray(),astronautRoot:A.group.position.toArray(),bodyEuler:B.rotation.toArray(),visible:A.group.visible,contacts,handContacts};}
 function step(dt=.05){time=T.MathUtils.clamp(time+(direction==='outbound'?dt:-dt)*PLAY_RATE,0,16.2);if(time<1e-9)time=0;if(time>16.2-1e-9)time=16.2;phase=time===16.2?'porch':time===0?(direction==='inbound'?'aboard':'review'):'passage';render();return state();}
 function restart(){time=0;direction='outbound';phase='review';playing=false;render();}
 function board(){direction='inbound';phase='passage';return true;}
 function toggle(){if(time===0)direction='outbound';if(time===16.2)direction='inbound';playing=!playing;}
 controls.onclick=e=>{const b=e.target.closest('button');if(!b)return;if(b.id==='r4reset')restart();if(b.id==='r4play')toggle();if(b.id==='r4return'){board();playing=true;}if(b.id==='r4cut')cutaway=!cutaway;if(b.dataset.cam)camera=b.dataset.cam;render();};controls.querySelector('#r4time').oninput=e=>{playing=false;time=+e.target.value;render();};
 const help=document.createElement('span');help.textContent='空格：播放／暂停；F：换向；滑条：逐姿态检查。';controls.append(help);
 addEventListener('keydown',e=>{if(e.target.matches('input'))return;if(e.code==='Space'){e.preventDefault();toggle();}if(e.code==='KeyF'){direction=direction==='outbound'?'inbound':'outbound';playing=true;}if(e.code==='KeyR')restart();});
 function tick(now){if(playing){step(Math.min(.04,last?(now-last)/1000:1/60));if(time===0||time===16.2)playing=false;}last=now;requestAnimationFrame(tick);}requestAnimationFrame(tick);
 window.egressReview={R,review,q,body:B,step,restart,board,render,state,keys,set(o={}){if(o.camera)camera=o.camera;if(o.cutaway!==undefined)cutaway=o.cutaway;if(o.time!==undefined)time=o.time;playing=false;render();},pose};restart();
})().catch(console.error);
