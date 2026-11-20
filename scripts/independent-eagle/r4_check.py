"""Blender triangle BVH intersections for the actual deformed, suited game mesh.
No approximate capsule is used. Intersections are FAIL evidence, not clearance proof.
"""
import json, math, struct, sys
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];d=root/'docs/independent-eagle/r4'/('dense/audit' if '--dense' in sys.argv else 'audit')
t=json.loads((d/'topology.json').read_text());manifest=json.loads((d/'frames.json').read_text())
def make(points):
    verts=[Vector(points[i:i+3]) for i in range(0,len(points),3)]
    return BVHTree.FromPolygons(verts,[(i,i+1,i+2) for i in range(0,len(verts),3)],all_triangles=True,epsilon=0)
fixed=[];moving=[]
# Verify that BVH overlap is testing surfaces, not just triangle bounding boxes.
fixture=make([0,0,0,1,0,0,0,1,0])
assert not fixture.overlap(make([.8,.8,0,1,.8,0,.8,1,0]))
assert fixture.overlap(make([.2,.2,-1,.2,.2,1,.5,.2,0]))
for c in t['colliders']:
    if c['moving']:moving.append(c)
    else:fixed.append((c,make(c['points'])))
supportPoints=[]
for c in t['colliders']:
    if c['source']=='legacy' or c['name'] in ['Midsection step nonslip top','Crew deck 36 by 55 inch recessed grips']:supportPoints.extend(c['points'])
support=make(supportPoints)
regions=t['regions'];contactSets=[[i for i,r in enumerate(regions) if r['actor']==side] for side in [0,1]]+[[i for i,r in enumerate(regions) if r['bone']==bone and r['restY']<1.0] for bone in [5,10]]
report=[]
for frame in manifest['frames']:
    if not frame['visible']:
        report.append({**frame,'hits':[],'excluded':'Avatar hidden after transition to aboard'});continue
    raw=(d/frame['file']).read_bytes();f=struct.unpack('<'+'f'*(len(raw)//4),raw);verts=[Vector(f[i:i+3]) for i in range(0,len(f),3)]
    actor=BVHTree.FromPolygons(verts,t['triangles'],all_triangles=True,epsilon=0)
    pivot=Vector(t['hatchPivot']);rot=Matrix.Rotation(math.radians(100)*frame['hatchOpen'],3,'Y')
    current=fixed[:]
    for c in moving:
        p=c['points'];points=[]
        for i in range(0,len(p),3):points.extend(pivot+rot@(Vector(p[i:i+3])-pivot))
        current.append((c,make(points)))
    hits=[]
    for c,bvh in current:
        pairs=actor.overlap(bvh)
        if not pairs:continue
        by={};bounds=[]
        for a,b in pairs:
            owner=t['owners'][a];by[owner]=by.get(owner,0)+1
            for v in t['triangles'][a]:bounds.append(verts[v])
        hits.append({'collider':c['name'],'source':c['source'],'pairs':len(pairs),'actorTriangles':sorted({a for a,b in pairs}),'parts':[{'name':t['entries'][k]['name'],'pairs':v} for k,v in by.items()], 'intersectionTriangleBounds':[[min(v[i] for v in bounds) for i in range(3)],[max(v[i] for v in bounds) for i in range(3)]]})
    distances=[min(support.find_nearest(verts[i])[3] for i in ids) for ids in contactSets]
    report.append({**frame,'hits':hits,'actualSupportDistancesMeters':dict(zip(['bootR','bootL','gloveR','gloveL'],distances))})
result={'sampleStepSeconds':manifest['sampleStepSeconds'],'simulationStepSeconds':manifest['simulationStepSeconds'],'method':'Actual rendered suit CPU skinning + visible PLSS/helmet/overshoes, triangle BVH against full R2 meshes including hidden cutaway walls and original descent geometry; Sampling intervals recorded in this report. Triangle intersections prove a conflict; absence is not continuous collision certification.','board':manifest['board'],'pageErrors':manifest['errors'],'actor':t['entries'],'frames':report}
(d.parent/'collision-report.json').write_text(json.dumps(result,indent=2)+'\n')
print('audited',len(report),'frames; intersection frames',sum(bool(f['hits']) for f in report),'board',manifest['board'])
for name in sorted({h['collider'] for f in report for h in f['hits']}):
    a=[f for f in report if any(h['collider']==name for h in f['hits'])]
    print(name, len(a),'first',a[0]['label'],round(a[0]['ladderTime'],3))
