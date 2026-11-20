"""Isolated R4 rig-pose review; protected default and R3 stay untouched."""
from pathlib import Path
import hashlib,json
r=Path(__file__).resolve().parents[2];s=(r/'index.html').read_text()
assert hashlib.sha256(s.encode()).hexdigest()=='ea644b64430c0108c86adca450f1abfe7187d5fd08e2787977434926dc75f3fe'
p='return {refreshInstruments(){dirty=true;},draw,reset,resize,beginSurfaceLook';assert s.count(p)==1
s=s.replace(p,'return {qa:{scene,camera,renderer,lander,astronaut,museumSuit,collisionParts,ground,view:setView},refreshInstruments(){dirty=true;},draw,reset,resize,beginSurfaceLook')
p='mission.egress();clearInput();draw(0);update(true);focusView();';assert s.count(p)==1;s=s.replace(p,'clearInput();draw(0);update(true);focusView();')
p='  requestAnimationFrame(tick);\n})();';assert s.count(p)==1
s=s.replace(p,'window.eagleReview={mission,world,reset,showLaunch,surfacePractice,draw(dt=0){world.refreshInstruments();draw(dt);update(true);}};})();')
s=s.replace('</body>','<script src="/scripts/independent-eagle/review.js"></script><script src="/scripts/independent-eagle/r4_review.js"></script></body>')
out=r/'web-release/independent-egress-r4';out.mkdir(parents=True,exist_ok=True);(out/'index.html').write_text(s)
d=r/'docs/independent-eagle/r4';d.mkdir(exist_ok=True)
protected=['index.html','assets/models/independent-eagle/front-cabin.json','assets/models/independent-eagle/front-cabin.glb','assets/models/independent-eagle/front-cabin.blend','scripts/independent-eagle/review.js','scripts/independent-eagle/add_lpd.py','scripts/independent-eagle/egress_review.js','scripts/independent-eagle/build_egress_preview.py']
baseline=d/'baseline.json'
if not baseline.exists():baseline.write_text(json.dumps({'scope':'Actual rig key poses, hatch/porch ONLY. No ladder rhythm. Candidate pending verification.','protectedSHA256':{p:hashlib.sha256((r/p).read_bytes()).hexdigest() for p in protected}},indent=2)+'\n')
print(out)
