/* R3 diagnostic rehearsal. Uses actual game rig, scan, PLSS and mission states. */
(async()=>{
 while(!window.independentReview)await new Promise(r=>setTimeout(r,25));
 const review=window.independentReview,R=window.eagleReview,q=review.q,m=R.mission,T=THREE,host=q.lander.group;
 document.getElementById('independent-review-controls').style.display='none';
 const nav=document.createElement('div');nav.id='egress-review-controls';nav.style.cssText='position:fixed;z-index:1000;left:12px;right:12px;top:12px;background:#10191def;padding:10px;color:#e9eee8;font:13px system-ui;border:1px solid #74807c;border-radius:8px;display:flex;gap:8px;flex-wrap:wrap';
 nav.innerHTML='<strong>R3 实际宇航服／背包 · 通行未验收</strong><button id="baseline">原动作</button><button id="candidate">小幅避让试验</button><button id="restart">重放出舱</button><button id="play">播放／暂停</button><button id="board">返舱</button><button data-camera="section">侧剖视</button><button data-camera="inside">舱内观察</button><button data-camera="outside">舱口外侧</button><button data-camera="ladder">梯子与脚垫</button><button id="cutaway">剖开舱壁</button><button data-time="0.6">门扫掠 0.6s</button><button data-time="4">门框 4s</button><button data-time="8">梯中段 8s</button><span id="egress-status"></span>';
 document.body.appendChild(nav);nav.querySelectorAll('button').forEach(e=>e.style.cssText='color:#e9eee8;background:#29383a;border:1px solid #667875;padding:5px 9px;border-radius:4px;cursor:pointer');
 let camera='section',cutaway=true,playing=false,last=0,direction='outbound',cycleTime=0,candidate=new URLSearchParams(location.search).get('candidate')==='clearance1';
 // Bounded path/pose trial only: no scale, mesh, default route or contact rhythm change.
 window.beforeEgressDraw=m=>{const p=m.ladderPose;if(!p||!candidate)return;
  const raw=p._r3Base||(p._r3Base={z:p.frontZ,y:p.soleY}),s=(a,b)=>T.MathUtils.smoothstep(p.time,a,b);
  const dz=-.18*(1-s(1.18,3.48)),dy=-.08*s(2.28,3.48)*(1-s(3.48,4.60));
  p.frontZ=raw.z+dz;p.soleY=raw.y+dy;m.astronautZ=m.z+p.frontZ;m.astronautHeight=p.soleY;
  p.trunkPitch=1.23*p.crawl+.55*p.climb*(1-p.crawl)-.23*(1-s(1.6,3.4));
 };
 const body=q.astronaut.limbs[0].hip.parent;
 const vec=a=>new T.Vector3(...a);
 // The same full cabin remains in collision auditing. Cutaway changes visibility only.
 const visualOriginal=new Map();for(const o of review.models.independent.root.children)if(o.isMesh)visualOriginal.set(o,o.material);
 function render(){review.set({model:'independent',view:'front',open:m.hatchOpen,overheadOpen:false,person:false,headOffset:0});
  for(const [o,mat]of visualOriginal){const shell=/Pressure shell|forward skin|pressure wall|pressure bulkhead|Upper brow|Upper face roof|Central forward|roof with open|transition/.test(o.name);o.visible=!(cutaway&&shell);}
  const poses={section:[[3.8,4.30,1.7],[0,3.75,1.7],48],inside:[[.9,4.7,-.1],[0,3.85,1.9],77],outside:[[2.5,4.4,4.6],[0,3.80,1.45],48],ladder:[[4.5,2.8,5.9],[0,1.65,3.75],52]};const [a,b,fov]=poses[camera]||poses.section;q.camera.position.copy(host.localToWorld(vec(a)));q.camera.up.set(0,1,0);q.camera.fov=fov;q.camera.aspect=innerWidth/innerHeight;q.camera.updateProjectionMatrix();q.camera.lookAt(host.localToWorld(vec(b)));q.camera.updateMatrixWorld(true);q.renderer.render(q.scene,q.camera);document.getElementById('egress-status').textContent=(candidate?'避让试验（未通过）':'原动作基线')+' · '+direction+' · '+m.phase+' · t='+m.ladderTime.toFixed(2)+' s · '+(cutaway?'剖视（检查仍含全舱）':'完整舱壁');
 }
 function restart(){playing=false;R.reset();R.showLaunch(false);R.surfacePractice();m.phase='landed';m.ladderPose=null;q.view('external');for(let i=0;i<30;i++)R.step(1/30);m.egress();R.draw(0);direction='outbound';cycleTime=0;render();}
 function step(dt=1/30){R.step(dt);cycleTime+=dt;render();return state();}
 function state(){return{phase:m.phase,direction,ladderTime:m.ladderTime,cycleTime,hatchOpen:m.hatchOpen,bodyPosition:host.worldToLocal(body.getWorldPosition(new T.Vector3())).toArray(),astronautRoot:host.worldToLocal(q.astronaut.group.getWorldPosition(new T.Vector3())).toArray(),bodyEuler:body.rotation.toArray(),visible:q.astronaut.group.visible};}
 function board(){const ok=m.ingress();if(ok){direction='inbound';R.draw(0);render();}return ok;}
 nav.onclick=e=>{const b=e.target.closest('button');if(!b)return;if(b.id==='baseline'||b.id==='candidate'){candidate=b.id==='candidate';restart();}if(b.id==='restart')restart();if(b.id==='play')playing=!playing;if(b.id==='board'&&board())playing=true;if(b.dataset.camera)camera=b.dataset.camera;if(b.id==='cutaway')cutaway=!cutaway;if(b.dataset.time){restart();for(let i=0;i<Math.round(Number(b.dataset.time)*20);i++)step(.05);}render();};
 function tick(now){if(playing){const dt=last?Math.min(.04,(now-last)/1000):1/60;step(dt);if(m.phase==='aboard'||m.phase==='eva')playing=false;}last=now;requestAnimationFrame(tick);}requestAnimationFrame(tick);
 window.egressReview={R,review,q,body,step,restart,board,render,state,set(o={}){if(o.camera)camera=o.camera;if(o.cutaway!==undefined)cutaway=o.cutaway;playing=false;render();},get playing(){return playing;}};restart();
})().catch(e=>console.error(e));
