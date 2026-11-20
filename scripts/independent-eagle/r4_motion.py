"""Check actual deformed vertices for direction consistency and IK flips (QA needs numpy)."""
from pathlib import Path
import json,numpy as np
r=Path(__file__).resolve().parents[2]/'docs/independent-eagle/r4/dense';f=json.loads((r/'audit/frames.json').read_text())['frames'];previous=None;top=[];lookup={};pair=0
for q in f:
 a=np.fromfile(r/'audit'/q['file'],dtype='<f4').reshape(-1,3)
 if q['label']=='outbound':lookup[round(q['ladderTime']*1e6)]=q['file']
 elif round(q['ladderTime']*1e6) in lookup:
  b=np.fromfile(r/'audit'/lookup[round(q['ladderTime']*1e6)],dtype='<f4').reshape(-1,3);pair=max(pair,float(np.max(np.linalg.norm(a-b,axis=1))))
 if previous is not None and previous[0]['label']==q['label']:top.append((float(np.max(np.linalg.norm(a-previous[1],axis=1))),q['ladderTime'],q['label']))
 previous=(q,a)
largest=sorted(top,reverse=True)[:12];result={'sampleHz':30,'maxPairedVertexDistanceMeters':pair,'largestFrameDisplacements':largest,'limits':{'pairedVertexMeters':1e-6,'singleFrameVertexMeters':.06},'pass':pair<1e-6 and largest[0][0]<.06}
(r.parent/'motion-continuity.json').write_text(json.dumps(result,indent=2)+'\n');print(result);assert result['pass'],'Direction mismatch or IK jump; do not accept this candidate'
