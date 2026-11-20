"""R3 actual-avatar gate: generated game copy only. Default and R2 assets untouched."""
from pathlib import Path
import hashlib,json
r=Path(__file__).resolve().parents[2];s=(r/'index.html').read_text();digest=hashlib.sha256(s.encode()).hexdigest();assert digest=='ea644b64430c0108c86adca450f1abfe7187d5fd08e2787977434926dc75f3fe'
p='return {refreshInstruments(){dirty=true;},draw,reset,resize,beginSurfaceLook';assert s.count(p)==1
s=s.replace(p,'return {qa:{scene,camera,renderer,lander,astronaut,museumSuit,collisionParts,ground,view:setView},refreshInstruments(){dirty=true;},draw,reset,resize,beginSurfaceLook')
p='mission.egress();clearInput();draw(0);update(true);focusView();';assert p in s;s=s.replace(p,'clearInput();draw(0);update(true);focusView();')
p='  requestAnimationFrame(tick);\n})();';assert s.count(p)==1
s=s.replace(p,'window.eagleReview={mission,world,reset,showLaunch,surfacePractice,step(dt,input={}){mission.step(dt,input);world.surfaceStep(dt,input);window.beforeEgressDraw?.(mission,world);bodyTime+=dt;world.refreshInstruments();draw(dt);update(true);},draw(dt=0){window.beforeEgressDraw?.(mission,world);bodyTime+=dt;world.refreshInstruments();draw(dt);update(true);}};})();')
p='body.rotation.set(1.23*crawl+.55*climb*(1-crawl),0,-lean);';assert s.count(p)==1
s=s.replace(p,'body.rotation.set(Number.isFinite(ladderPose.trunkPitch)?ladderPose.trunkPitch:1.23*crawl+.55*climb*(1-crawl),0,-lean);')
s=s.replace('</body>','<script src="/scripts/independent-eagle/review.js"></script><script src="/scripts/independent-eagle/egress_review.js"></script></body>')
out=r/'web-release/independent-egress';out.mkdir(parents=True,exist_ok=True);(out/'index.html').write_text(s)
protected=['index.html','assets/models/independent-eagle/front-cabin.json','assets/models/independent-eagle/front-cabin.glb','assets/models/independent-eagle/front-cabin.blend','scripts/independent-eagle/review.js','scripts/independent-eagle/add_lpd.py']
(r/'docs/independent-eagle/r3/baseline.json').write_text(json.dumps({'scope':'actual suited avatar + PLSS through R2 hatch, porch, ladder and return; isolated only','protectedSHA256':{p:hashlib.sha256((r/p).read_bytes()).hexdigest() for p in protected},'preview':'http://127.0.0.1:8000/web-release/independent-egress/'},indent=2)+'\n');print(out)
