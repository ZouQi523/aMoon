"""Self-contained R4 static build. Default release and original sources are untouched."""
from pathlib import Path
import importlib.util,runpy,json,hashlib
r=Path(__file__).resolve().parents[2]
runpy.run_path(str(r/'scripts/independent-eagle/build_r4_preview.py'),run_name='__main__')
spec=importlib.util.spec_from_file_location('build_web',r/'scripts/build_web.py');web=importlib.util.module_from_spec(spec);spec.loader.exec_module(web)
out=r/'web-release/r4-play';out.mkdir(parents=True,exist_ok=True)
web.build(r/'web-release/independent-egress-r4/index.html',out)
p=out/'index.html';s=p.read_text().replace('/scripts/independent-eagle/review.js','./review.js').replace('/scripts/independent-eagle/r4_review.js','./r4_review.js').replace('/favicon.svg?v=2','./favicon.svg');p.write_text(s)
(out/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><circle cx="16" cy="16" r="14" fill="#dad7c9"/></svg>')
model=r/'assets/models/independent-eagle';models=out/'models';models.mkdir(exist_ok=True)
for src,dest in [(model/'front-cabin.json','front-cabin.json'),(model/'r1/front-cabin.json','r1-front-cabin.json'),(model/'LICENSE.txt','LICENSE.txt')]: (models/dest).write_bytes(src.read_bytes())
review=(r/'scripts/independent-eagle/review.js').read_text().replace('/assets/models/independent-eagle/front-cabin.json','./models/front-cabin.json').replace('/assets/models/independent-eagle/r1/front-cabin.json','./models/r1-front-cabin.json')
(out/'review.js').write_text(review);(out/'r4_review.js').write_bytes((r/'scripts/independent-eagle/r4_review.js').read_bytes())
print('R4 production:',out,'assets',len(list((out/'assets').iterdir())))
