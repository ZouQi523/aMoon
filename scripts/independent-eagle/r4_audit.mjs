// Export the actual deformed visible game avatar, not an envelope or proxy rig.
import fs from 'node:fs';import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);let chromium;try{({chromium}=require('playwright-core'));}catch{({chromium}=require('/tmp/amoon-tools/node_modules/playwright-core'));}
const candidate=false,dense=process.argv.includes('--dense'),dt=dense?1/60:.05,sampleEvery=dense?2:4;const dir='docs/independent-eagle/r4'+(dense?'/dense':'');fs.mkdirSync(dir+'/audit',{recursive:true});
const browser=await chromium.launch({executablePath:process.env.CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--use-gl=angle','--use-angle=metal']});
try{
 const page=await browser.newPage({viewport:{width:1400,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('http://127.0.0.1:8000/web-release/independent-egress-r4/'+(candidate?'?candidate=clearance1':''),{waitUntil:'domcontentloaded',timeout:90000});await page.waitForFunction(()=>window.egressReview);
 const topology=await page.evaluate(()=>{
  const E=egressReview,T=THREE,H=E.q.lander.group;H.updateWorldMatrix(true,true);
  const visible=o=>{for(let p=o;p;p=p.parent)if(!p.visible)return false;return true;};
  const actors=[];E.q.astronaut.group.traverse(o=>{if(o.isMesh&&visible(o))actors.push(o);});
  const entries=[],triangles=[],owners=[],regions=[];let n=0;
  for(const [id,o]of actors.entries()){
   const g=o.geometry,ix=g.index,order=ix?Array.from(ix.array):Array.from({length:g.attributes.position.count},(_,i)=>i),used=[...new Set(order)],remap=new Map(used.map((v,i)=>[v,n+i]));
   for(const v of used){const g=o.geometry,ix=g.attributes.skinIndex,w=g.attributes.skinWeight;let bone=-1,best=-1;if(ix)for(let k=0;k<4;k++)if(w.array[v*4+k]>best){best=w.array[v*4+k];bone=ix.array[v*4+k];}regions.push({actor:id,bone,original:v,restY:g.attributes.position.getY(v)});}const polys=[];for(let i=0;i<order.length;i+=3){polys.push(order.slice(i,i+3).map(k=>remap.get(k)));owners.push(id);}
   triangles.push(...polys);entries.push({name:o.name||o.parent.name||'helmet face detail',vertices:used.length,triangles:polys.length,skinned:!!o.isSkinnedMesh});
   o.userData.egressExport={used,offset:n};n+=used.length;
  }
  const colliders=[];const add=(o,source)=>{if(!o.isMesh)return;const g=o.geometry,ix=g.index,p=g.attributes.position,v=new T.Vector3(),mat=H.matrixWorld.clone().invert().multiply(o.matrixWorld),points=[];for(let i=0;i<(ix?ix.count:p.count);i++){v.fromBufferAttribute(p,ix?ix.getX(i):i).applyMatrix4(mat);points.push(v.x,v.y,v.z);}if(source==='legacy'&&!points.some((_,i)=>i%3===2&&points[i]>1))return;colliders.push({name:o.name||'legacy porch/rail/ladder',source,moving:!!E.review.models.independent.hinge.children.includes(o),points});};
  const model=E.review.models.independent;for(const o of [...model.solid,...model.panes])add(o,'R2');E.q.lander.descentGroup.traverse(o=>add(o,'legacy'));
  window.egressAuditExport={actors,vertexCount:n,colliders,frame(){H.updateWorldMatrix(true,true);const data=new Float32Array(n*3),v=new T.Vector3(),inv=H.matrixWorld.clone().invert();for(const o of actors){o.updateWorldMatrix(true,false);if(o.isSkinnedMesh)o.skeleton.update();const {used,offset}=o.userData.egressExport,mat=inv.clone().multiply(o.matrixWorld);for(let j=0;j<used.length;j++){v.fromBufferAttribute(o.geometry.attributes.position,used[j]);if(o.isSkinnedMesh)o.applyBoneTransform(used[j],v);v.applyMatrix4(mat);data.set([v.x,v.y,v.z],(offset+j)*3);}}let binary='';const bytes=new Uint8Array(data.buffer);for(let i=0;i<bytes.length;i+=32768)binary+=String.fromCharCode(...bytes.subarray(i,i+32768));return{state:E.state(),base64:btoa(binary)};}};
  return{entries,triangles,owners,regions,vertexCount:n,colliders,hatchPivot: model.data.hatch.pivot.map((v,i)=>v+model.data.parameters.game_offset[i])};
 });fs.writeFileSync(dir+'/audit/topology.json',JSON.stringify(topology));console.log('topology',topology.vertexCount,topology.triangles.length,topology.colliders.length);
 const frames=[];let index=0;
 async function sample(label){const f=await page.evaluate(()=>egressAuditExport.frame());const name=String(index++).padStart(4,'0');fs.writeFileSync(dir+'/audit/'+name+'.f32',Buffer.from(f.base64,'base64'));frames.push({file:name+'.f32',label,...f.state});}
 await sample('outbound');for(let i=1;i<=Math.round(22/dt);i++){await page.evaluate(dt=>egressReview.step(dt),dt);if(i%sampleEvery===0||i===Math.round(22/dt))await sample('outbound');}
 const board=await page.evaluate(()=>egressReview.board());console.log('board',board);if(board){await sample('inbound');for(let i=1;i<=Math.round(22/dt);i++){await page.evaluate(dt=>egressReview.step(dt),dt);if(i%sampleEvery===0||i===Math.round(22/dt))await sample('inbound');}}
 fs.writeFileSync(dir+'/audit/frames.json',JSON.stringify({frames,errors,board,sampleStepSeconds:dt*sampleEvery,simulationStepSeconds:dt},null,2));console.log('frames',frames.length,'end',frames.at(-1).phase,'errors',errors);
}finally{await browser.close();}
