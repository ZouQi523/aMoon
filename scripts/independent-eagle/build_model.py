"""Independent Apollo LM front cabin. Only public NASA sources in references.json.
Run with Blender --background --python ... . No print mesh, tracing or private input.
Own geometry and code: CC0-1.0. Units metres; X world right, Y up, Z forward. Cabin screen-right is -X while looking +Z.
"""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'assets/models/independent-eagle';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
P={'cabin_diameter':92*.0254,'cabin_depth':42*.0254,'hatch_clear':32*.0254,'deck_width':55*.0254,'deck_depth':36*.0254,'station_spacing':44*.0254,'window_clear_area':2*.3048**2,'window_width':.70,'window_yaw_degrees':17,'window_down_degrees':23,'window_center_height':1.50,'glass_outer_thickness':.004,'glass_inner_thickness':.006,'glass_separation':.035,'wall_depth':.065,'eye_height':1.65,'eye_z':.19,'hatch_front_z':.60,'hatch_leaf_thickness':.036,'hatch_open_degrees':100,'hatch_frame_depth':.12,'game_offset':[0,3.25,.941]}
# Numeric angles, pane thickness and eye height are authored approximations; see references.json.
MAT={}
def mat(n,c,metal=0,rough=.5,alpha=1):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,alpha);m.use_nodes=True
 bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) or m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');out=next((n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL'),None) or m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(bs.outputs['BSDF'],out.inputs['Surface']);bs.inputs['Base Color'].default_value=(*c,alpha);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;bs.inputs['Alpha'].default_value=alpha
 if alpha<1:bs.inputs['Transmission Weight'].default_value=.3
 MAT[n]=m;return m
mat('Exterior silver',(.59,.61,.59),.78,.4);mat('Thermal black',(.045,.05,.052),.12,.77);mat('Cabin pale gray',(.56,.58,.56),.15,.6);mat('Frame aluminum',(.37,.40,.40),.72,.34);mat('Seal rubber',(.022,.025,.026),0,.85);mat('Glass thermal pane',(.24,.38,.42),.1,.12,.13);mat('Glass structural pane',(.32,.43,.44),.05,.1,.09);mat('Panel charcoal',(.105,.12,.13),.2,.58);mat('Deck Velcro',(.16,.17,.17),0,.98);mat('Ivory legends',(.84,.82,.72),.1,.6);mat('Amber display',(.72,.48,.13),.1,.4);mat('Suit reference',(.77,.76,.66),0,.8)
ROOTOBJ=bpy.data.objects.new('Independent NASA-reference front cabin',None);bpy.context.collection.objects.link(ROOTOBJ)
ROOTOBJ['license']='CC0-1.0; independently authored';ROOTOBJ['source_policy']='Public NASA documents only; no A11D inputs'
def mesh(name,vs,fs,material,parent=ROOTOBJ):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.data.materials.append(MAT[material]);ob.parent=parent;return ob
def box(n,c,s,m,parent=ROOTOBJ):
 x,y,z=c;a,b,d=[v/2 for v in s];vs=[(x+u*a,y+v*b,z+w*d) for u,v,w in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 return mesh(n,vs,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],m,parent)
def rod(n,a,b,r,m,parent=ROOTOBJ,sides=10):
 a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,1,0)))
 if u.length<.01:u=axis.cross(Vector((1,0,0)))
 u.normalize();v=axis.cross(u);vs=[tuple(p+r*(math.cos(i*2*math.pi/sides)*u+math.sin(i*2*math.pi/sides)*v)) for p in [a,b] for i in range(sides)]
 fs=[tuple(range(sides-1,-1,-1)),tuple(range(sides,sides*2))]+[(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)]
 return mesh(n,vs,fs,m,parent)
def ring(n,outer,inner,depth,m,parent=ROOTOBJ):
 # Shared inner loop defines every aperture, glass and retaining lip.
 N=len(inner);dv=Vector(depth);vs=[tuple(v) for v in outer+inner]+[tuple(Vector(v)+dv) for v in outer+inner]
 fs=[]
 for i in range(N):
  j=(i+1)%N;fs += [(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(N+i,N+j,3*N+j,3*N+i),(i,2*N+i,2*N+j,j)]
 return mesh(n,vs,fs,m,parent)
def slab(n,loop,delta,m,parent=ROOTOBJ):
 N=len(loop);vs=loop+[tuple(Vector(v)+Vector(delta)) for v in loop];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 return mesh(n,vs,fs,m,parent)
def text(n,t,pos,size=.014,parent=ROOTOBJ):
 cu=bpy.data.curves.new(n,'FONT');cu.body=t;cu.size=size;cu.align_x='CENTER';cu.extrude=0
 ob=bpy.data.objects.new(n,cu);bpy.context.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(math.pi/2,0,math.pi);ob.data.materials.append(MAT['Ivory legends']);ob.parent=parent
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False);return ob
# Side and roof facets form a hollow front compartment, open aft for inspection.
r=P['cabin_diameter']/2;cy=math.sqrt(r*r-(P['deck_width']/2)**2);rear=-.40;front=.55
# Floor chord matches the published 55-inch deck width inside a 92-inch circle.
start=math.asin(-cy/r);angles=[start+(math.pi-2*start)*i/20 for i in range(21)]
cabin_angles=angles.copy()
for i in range(len(angles)-1):
 a,b=angles[i:i+2];edge=[(r*math.cos(t),cy+r*math.sin(t),z) for z in [rear,front] for t in [a,b]]
 mesh('Pressure shell facet %02d'%i,edge,[(0,1,3,2)],'Cabin pale gray')
# Authored faceted forward face: each triangle has the SAME actual 2 sqft opening inside/out.
windows=[]
for side in [-1,1]:
 name='CDR left' if side>0 else 'LMP right';yaw=math.radians(side*P['window_yaw_degrees']);down=math.radians(P['window_down_degrees'])
 n=Vector((math.sin(yaw)*math.cos(down),-math.sin(down),math.cos(yaw)*math.cos(down)));u=Vector((math.cos(yaw),0,-math.sin(yaw)));v=n.cross(u).normalized();c=Vector((side*.5588,P['window_center_height'],.87))
 w=P['window_width'];h=2*P['window_clear_area']/w
 raw=[Vector((-w/2,h/3)),Vector((0,-2*h/3)),Vector((w/2,h/3))];uv=[]
 for j,pt in enumerate(raw):
  start=pt.lerp(raw[j-1],.07);end=pt.lerp(raw[(j+1)%3],.07)
  for k in range(7):
   t=k/6;uv.append(start*(1-t)**2+pt*(2*t*(1-t))+end*t*t)
 area=abs(sum(uv[i].x*uv[(i+1)%len(uv)].y-uv[(i+1)%len(uv)].x*uv[i].y for i in range(len(uv)))/2)
 scale=math.sqrt(P['window_clear_area']/area);uv=[p*scale for p in uv]
 # Radial correspondence to an outer rectangular wall adds corner rays to the
 # SAME rounded clear loop. No solid face or photograph lies behind the opening.
 angles=sorted(set([math.atan2(p.y,p.x) for p in uv]+[math.atan2(y,x) for x in [-.50,.50] for y in [-.64,.62]]))
 def hit_polygon(d,poly):
  hits=[]
  for j,a in enumerate(poly):
   b=poly[(j+1)%len(poly)];edge=b-a;det=d.x*edge.y-d.y*edge.x
   if abs(det)<1e-10:continue
   t=(a.x*edge.y-a.y*edge.x)/det;f=(a.x*d.y-a.y*d.x)/det
   if t>=0 and -.000001<=f<=1.000001:hits.append(t)
  return d*min(hits)
 rectangle=[Vector((-.50,-.64)),Vector((.50,-.64)),Vector((.50,.62)),Vector((-.50,.62))]
 clear_uv=[hit_polygon(Vector((math.cos(a),math.sin(a))),uv) for a in angles]
 outer_uv=[hit_polygon(Vector((math.cos(a),math.sin(a))),rectangle) for a in angles]
 loop=[tuple(c+u*p.x+v*p.y) for p in clear_uv];outer=[tuple(c+u*p.x+v*p.y) for p in outer_uv]
 ring(name+' forward skin with real opening',outer,loop,tuple(-n*P['wall_depth']),'Thermal black')
 for label,scale,offset,dep,material in [('outer bezel',1.12,.012,.012,'Frame aluminum'),('outer seal',1.025,.016,.009,'Seal rubber'),('inner bezel',1.10,-P['wall_depth']-.018,.010,'Cabin pale gray')]:
  oo=[tuple(c+(Vector(p)-c)*scale+n*offset) for p in loop];ii=[tuple(c+(Vector(p)-c)*(1.035 if label=='outer bezel' else 1)+n*offset) for p in loop];ring(name+' '+label,oo,ii,tuple(n*dep),material)
 for label,offset,thick,material in [('thermal outer',-.009,P['glass_outer_thickness'],'Glass thermal pane'),('structural inner',-.009-P['glass_separation'],P['glass_inner_thickness'],'Glass structural pane')]:
  ob=slab(name+' '+label,[tuple(Vector(p)+n*offset) for p in loop],tuple(-n*thick),material);ob['glass']=True
 for k in range(3):
  a,b=c+u*raw[k].x*1.14+v*raw[k].y*1.14,c+u*raw[(k+1)%3].x*1.14+v*raw[(k+1)%3].y*1.14;
  for f in [.16,.38,.62,.84]:
   p=a.lerp(b,f)*.965+c*.035+n*.014;rod(name+' bezel fastener',p,p+n*.006,.005,'Frame aluminum',sides=6)
 windows.append({'name':name,'center':list(c),'normal':list(n),'u':list(u),'v':list(v),'clear_loop':loop,'clear_area_m2':P['window_clear_area']})
# Central pressure wall bridges the two independently inclined window facets.
seam=[]
for side in [-1,1]:
 yaw=math.radians(side*P['window_yaw_degrees']);d=math.radians(P['window_down_degrees']);n=Vector((math.sin(yaw)*math.cos(d),-math.sin(d),math.cos(yaw)*math.cos(d)));u=Vector((math.cos(yaw),0,-math.sin(yaw)));v=n.cross(u).normalized();c=Vector((side*.5588,1.50,.87))
 seam.extend([tuple(c+u*(-side*.50)+v*t) for t in [-.64,.62]])
slab('Central forward pressure wall',[seam[0],seam[2],seam[3],seam[1]],(0,0,-.055),'Exterior silver')
# Roof brow, central spine, lower cheek panels. No closed face behind windows.
box('Upper brow',(0,2.025,.64),(1.32,.18,.19),'Exterior silver')
box('Central avionics spine',(0,1.49,.79),(.18,.78,.19),'Cabin pale gray')
box('Upper face roof seam',(0,2.16,.46),(1.0,.10,.31),'Thermal black')
H=P['hatch_clear'];hz=P['hatch_front_z'];door_y=H/2
# Rounded corners intentionally conservative authored approximation.
def rounded_square(w,h,r,yc,z):
 pts=[]
 for cx,cyy,start in [(w/2-r,yc+h/2-r,0),(-w/2+r,yc+h/2-r,90),(-w/2+r,yc-h/2+r,180),(w/2-r,yc-h/2+r,270)]:
  for j in range(5):
   a=math.radians(start+j*90/4);pts.append((cx+r*math.cos(a),cyy+r*math.sin(a),z))
 return pts
inner=rounded_square(H,H,.055,door_y,hz);outer=rounded_square(H+.15,H+.15,.10,door_y,hz)
ring('Forward hatch pressure frame 32 inch clear',outer,inner,(0,0,-P['hatch_frame_depth']),'Frame aluminum')
ring('Forward hatch elastomer seal',rounded_square(H+.016,H+.016,.063,door_y,hz+.005),inner,(0,0,.009),'Seal rubber')
# Side faces join hatch frame to the cylindrical side envelope; upper sill supports instruments.
for side in [-1,1]:
 box('Lower cheek silver '+str(side),(side*.76,.48,.48),(.56,.94,.16),'Exterior silver')
box('Hatch header',(0,.89,.55),(.96,.105,.18),'Cabin pale gray')
box('Hatch flush threshold',(0,-.015,.56),(.95,.03,.17),'Frame aluminum')
# Door at screen-right (-X) when viewed from inside looking +Z. Positive Y rotation swings inward.
pivot=bpy.data.objects.new('Inward hatch hinge LMP side',None);bpy.context.collection.objects.link(pivot);pivot.parent=ROOTOBJ;pivot.location=(-H/2-.012,door_y,hz-P['hatch_frame_depth']-.006)
leaf=rounded_square(H-.007,H-.007,.053,0,0);leaf=[(x+H/2+.012,y,z) for x,y,z in leaf]
slab('Inward opening hatch leaf',leaf,(0,0,-P['hatch_leaf_thickness']),'Cabin pale gray',pivot)
# Inner door ribs and latch are visible when open; no fake cabin photograph behind it.
for x in [H*.86,H*.15]:box('Door inside vertical rib',(x,0,-.054),(.025,H*.76,.03),'Frame aluminum',pivot)
for y in [-H*.36,H*.36]:box('Door inside horizontal rib',(H/2,y,-.054),(H*.78,.025,.03),'Frame aluminum',pivot)
rod('Cabin relief valve',(H*.64,-.19,-.05),(H*.64,-.19,-.075),.055,'Panel charcoal',pivot,sides=24)
rod('Inside latch handle',(H*.36,.035,-.09),(H*.36,-.085,-.09),.013,'Frame aluminum',pivot)
rod('Outside latch',(H*.36,-.02,.035),(H*.36,-.12,.035),.014,'Frame aluminum',pivot)
for y in [-H*.34,H*.34]:rod('Hatch hinge barrel',(0,y-.035,0),(0,y+.035,0),.012,'Frame aluminum',pivot)
# NASA news reference deck 36 x 55 in; nonflammable Velcro finish and recessed grips.
# Four genuinely recessed grip wells; the door bottom no longer hits raised bars.
xs=[-P['deck_width']/2,-.33,-.17,.17,.33,P['deck_width']/2];zs=[.60-P['deck_depth'],.229,.271,.419,.461,.60];deck=[]
for x0,x1 in zip(xs,xs[1:]):
 for z0,z1 in zip(zs,zs[1:]):
  if (abs((x0+x1)/2)<.34 and abs((x0+x1)/2)>.16) and (abs((z0+z1)/2-.25)<.025 or abs((z0+z1)/2-.44)<.025):continue
  deck.append(box('Deck segment',((x0+x1)/2,-.045,(z0+z1)/2),(x1-x0,.09,z1-z0),'Deck Velcro'))
# Join structural deck cells for a compact runtime mesh, retaining generator parameters.
bpy.ops.object.select_all(action='DESELECT')
for o in deck:o.select_set(True)
bpy.context.view_layer.objects.active=deck[0];bpy.ops.object.join();deck[0].name='Crew deck 36 by 55 inch recessed grips';deck[0].select_set(False)
for z in [.25,.44]:
 for x in [-.25,.25]:
  box('Recessed floor grip pocket',(x,-.034,z),(.16,.012,.042),'Panel charcoal');rod('Recessed floor grip bar',(x-.066,-.012,z),(x+.066,-.012,z),.008,'Frame aluminum')
# Front panels: layout follows NASA A11 press-kit left/right cabin diagrams.
# This is an approximate equipment massing study, not a functional instrument overhaul.
for side in [-1,1]:
 x=side*.61
 box(('CDR' if side>0 else 'LMP')+' lower control panel',(x,1.01,.57),(.68,.22,.22),'Panel charcoal')
 box(('CDR' if side>0 else 'LMP')+' upper instrument wall',(side*.20,1.55,.60),(.22,.52,.13),'Panel charcoal')
 for row in range(2):
  for col in range(6):
   xx=x+(col-2.5)*.075;yy=.955+row*.09
   rod('Switch bezel',(xx,yy,.445),(xx,yy,.426),.012,'Frame aluminum',sides=8)
   rod('Switch toggle',(xx,yy,.424),(xx,yy+.018,.408),.004,'Ivory legends',sides=6)
 for k in range(2):
  px=side*.20;py=1.43+k*.21
  rod('Gauge bezel',(px,py,.527),(px,py,.514),.066,'Frame aluminum',sides=24)
  rod('Gauge face',(px,py,.512),(px,py,.507),.054,'Panel charcoal',sides=24)
  rod('Gauge pointer',(px,py,.502),(px+.025,py+.027,.502),.003,'Ivory legends',sides=6)
 box('Side circuit breaker rack '+str(side),(side*.91,1.50,.01),(.16,.55,.38),'Panel charcoal')
 for row in range(5):
  for col in range(3):
   xx=side*(.824);yy=1.29+row*.095;zz=-.13+col*.13
   rod('Circuit breaker',(xx,yy,zz),(xx-side*.014,yy,zz),.009,'Ivory legends',sides=8)
 # Independent approximate hand controllers/armrests.
 box('Armrest '+str(side),(side*.77,.86,.06),(.14,.075,.27),'Cabin pale gray')
 rod('Attitude controller '+str(side),(side*.75,.93,.24),(side*.75,1.06,.21),.022,'Panel charcoal')
box('Central DSKY approximate enclosure',(0,1.10,.36),(.26,.28,.25),'Panel charcoal')
for y in [1.13,1.18]:box('DSKY inactive readout',(0,y,.232),(.19,.025,.004),'Amber display')
for x in [-.07,0,.07]:
 for y in [1.01,1.045,1.08]:box('DSKY key',(x,y,.226),(.042,.025,.01),'Ivory legends')
exec((Path(__file__).parent/'add_r2_structure.py').read_text(),globals())
exec((Path(__file__).parent/'add_lpd.py').read_text(),globals())
# Authored reference human; hidden by default. Eye is measured from its floor contact.
human=bpy.data.objects.new('Reference standing human 1.78m',None);bpy.context.collection.objects.link(human);human.parent=ROOTOBJ
for side in [-1,1]:
 x=P['station_spacing']/2+side*.10
 box('Reference boot',(x,.055,(P['eye_z']-.105)),(.11,.11,.24),'Suit reference',human)
 rod('Reference leg',(x,.14,(P['eye_z']-.105)),(x,.86,(P['eye_z']-.105)),.075,'Suit reference',human)
box('Reference torso',(P['station_spacing']/2,1.18,(P['eye_z']-.105)),(.37,.56,.22),'Suit reference',human)
rod('Reference head',(P['station_spacing']/2,1.55,(P['eye_z']-.105)),(P['station_spacing']/2,1.78,(P['eye_z']-.105)),.105,'Suit reference',human,sides=16)
rod('Reference eye marker',(P['station_spacing']/2,P['eye_height'],P['eye_z']-.008),(P['station_spacing']/2,P['eye_height'],P['eye_z']+.012),.014,'Amber display',human,sides=12)
# Export JSON meshes in authoring Y-up coordinates plus node parents; GLB by axis conversion.
bpy.context.view_layer.update();parts=[]
for ob in list(bpy.data.objects):
 if ob.type!='MESH':continue
 me=ob.data;me.calc_loop_triangles();vs=[list(ob.matrix_world@v.co) for v in me.vertices];ix=[int(k) for t in me.loop_triangles for k in t.vertices]
 parts.append({'name':ob.name,'positions':[round(c,7) for p in vs for c in p],'indices':ix,'material':ob.data.materials[0].name,'moving_hatch':ob.parent==pivot,'moving_overhead':ob.parent==overhead,'lpd_ink':bool(ob.get('lpd_ink',False)),'reference_person':ob.parent==human,'glass':bool(ob.get('glass',False))})
manifest={'schema':1,'license':'CC0-1.0','parameters':P,'materials':{n:{'color':list(m.diffuse_color[:3]),'alpha':m.diffuse_color[3],'metalness':next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Metallic'].default_value,'roughness':next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Roughness'].default_value} for n,m in MAT.items()},'windows':windows,'hatch':{'pivot':list(pivot.location),'clear_loop':inner,'axis':[0,1,0],'open_radians':math.radians(P['hatch_open_degrees'])},'eyes':{'CDR':[P['station_spacing']/2,P['eye_height'],P['eye_z']],'LMP':[-P['station_spacing']/2,P['eye_height'],P['eye_z']]},'parts':parts,'stage':'R2','overhead':OVERHEAD,'lpd':LPD}
(OUT/'front-cabin.json').write_text(json.dumps(manifest,separators=(',',':'))+'\n')
# Authoring scene has floor and eye empties for native editing.
for label,pos in manifest['eyes'].items():
 ob=bpy.data.objects.new(label+' eye 1.65m above deck',None);bpy.context.collection.objects.link(ob);ob.location=pos;ob.empty_display_type='SPHERE';ob.empty_display_size=.025
# Blender uses Z up; convert complete hierarchy once for a correctly oriented GLB.
axis=bpy.data.objects.new('Metres Y-up authoring to Blender Z-up',None);bpy.context.collection.objects.link(axis);ROOTOBJ.parent=axis;axis.rotation_euler=(math.pi/2,0,0)
for ob in bpy.data.objects:
 if ' eye 1.65m' in ob.name:ob.parent=axis
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'front-cabin.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'front-cabin.glb'),export_format='GLB',export_yup=True,export_extras=True)
print('INDEPENDENT FRONT CABIN',len(parts),'meshes',sum(len(p['indices'])//3 for p in parts),'triangles')
