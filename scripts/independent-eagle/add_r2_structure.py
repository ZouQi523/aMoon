"""R2 structures independently authored from NASA diagrams; no reference meshes."""
P.update({'aft_step_height':18*.0254,'aft_step_front_z':-.40,'aft_bulkhead_z':-1.55,'engine_cover_center_z':-.941,'engine_cover_top':.62,'tunnel_diameter':32*.0254,'tunnel_length':16*.0254,'overhead_hatch_diameter':33*.0254,'overhead_hatch_y':2.10})
# A real loft closes the round front-cabin / rectangular midsection interface.
# Profiles are authored approximations; the R1 shell and window vertices stay fixed.
height=(2.10-P['aft_step_height'])/2;mid_center=P['aft_step_height']+height
join_angles=sorted(set([a%(2*math.pi) for a in cabin_angles]+[math.atan2(y,x)%(2*math.pi) for x in [-.92,.92] for y in [-height,height]]))
fore_profile=[Vector((r*math.cos(a),r*math.sin(a))) for a in cabin_angles]
joinvs=[]
for aft in [False,True]:
 for a in join_angles:
  dx,dy=math.cos(a),math.sin(a)
  if aft:
   t=min(.92/max(abs(dx),1e-8),height/max(abs(dy),1e-8));x=dx*t;y=mid_center+dy*t;z=-.52
  else:
   pt=hit_polygon(Vector((dx,dy)),fore_profile);x=pt.x;y=cy+pt.y;z=-.40
  joinvs.append((x,y,z))
Njoin=len(join_angles)
mesh('Round cabin to midsection transition',joinvs,[(i,(i+1)%Njoin,(i+1)%Njoin+Njoin,i+Njoin) for i in range(Njoin)],'Cabin pale gray')
# Low midsection deck, connected to the published front flight-station deck.
box('Floor link to midsection',(0,-.045,(-.40+(.60-P['deck_depth']))/2),(P['deck_width'],.09,abs(-.40-(.60-P['deck_depth']))),'Deck Velcro')
box('18 inch midsection step',(0,P['aft_step_height']/2,(-.40-1.55)/2),(1.76,P['aft_step_height'],1.15),'Cabin pale gray')
box('Midsection step nonslip top',(0,P['aft_step_height']+.004,-.975),(1.76,.008,1.15),'Deck Velcro')
# Protective cover: broad low cylinder on the midsection deck, not a tall engine.
cz=P['engine_cover_center_z'];levels=[(.4572,.43),(.50,.425),(.60,.37),(.62,.35)];N=48
vs=[(rad*math.cos(2*math.pi*i/N),y,cz+rad*math.sin(2*math.pi*i/N)) for y,rad in levels for i in range(N)]
fs=[]
for j in range(len(levels)-1):
 for i in range(N):fs.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
fs.append(tuple(range((len(levels)-1)*N,len(levels)*N)))
mesh('Low ascent engine protective cover',vs,fs,'Cabin pale gray')
# Bolted circular service lid, broad handle and rim are silhouette-scale geometry.
rod('Engine cover service lid',(0,.6205,cz),(0,.628,cz),.325,'Frame aluminum',sides=48)
rod('Engine cover handle',(-.16,.65,cz),(.16,.65,cz),.013,'Panel charcoal')
for i in range(12):
 a=2*math.pi*i/12;rod('Engine cover lid fastener',(.338*math.cos(a),.623,cz+.338*math.sin(a)),(.338*math.cos(a),.632,cz+.338*math.sin(a)),.006,'Frame aluminum',sides=6)
# Midsection basic walls/box masses; no wiring or instrument-detail expansion.
box('Aft pressure bulkhead',(0,1.28,-1.575),(1.84,1.65,.05),'Cabin pale gray')
for side in [-1,1]:
 box('Midsection side pressure wall '+str(side),(side*.92,1.28,-1.0),(.045,1.65,1.10),'Cabin pale gray')
 box('Rear equipment mass '+str(side),(side*.69,1.05,-1.21),(.34,1.05,.48),'Panel charcoal')
 box('Rear storage face '+str(side),(side*.69,1.64,-1.30),(.34,.20,.30),'Cabin pale gray')
box('Aft central stowage panel',(0,1.29,-1.535),(.73,.49,.035),'Panel charcoal')
box('Aft stowage inner panel',(0,1.31,-1.505),(.62,.35,.025),'Cabin pale gray')
rod('Aft stowage handle',(-.18,1.10,-1.47),(.18,1.10,-1.47),.012,'Frame aluminum')
# Roof with a REAL separate circular hatch/tunnel aperture.
rr=P['tunnel_diameter']/2;roof_y=P['overhead_hatch_y'];tz=cz
phis=sorted(set([i*2*math.pi/64 for i in range(64)]+[math.atan2(z-tz,x)%(2*math.pi) for x in [-.92,.92] for z in [-1.55,-.4668]]))
inner=[];outer=[]
for a in phis:
 dx,dz=math.cos(a),math.sin(a);dist=[]
 for bound,component,origin in [(-.92,dx,0),(.92,dx,0),(-1.55,dz,tz),(-.4668,dz,tz)]:
  if abs(component)>1e-8 and (bound-origin)/component>0:dist.append((bound-origin)/component)
 t=min(dist);inner.append(((rr+.043)*dx,roof_y,tz+(rr+.043)*dz));outer.append((t*dx,roof_y,tz+t*dz))
ring('Midsection roof with open docking aperture',outer,inner,(0,-.045,0),'Cabin pale gray')
circle=lambda radius,y:[(radius*math.cos(a),y,tz+radius*math.sin(a)) for a in phis]
ring('32 inch clear docking tunnel',circle(rr+.043,roof_y),circle(rr,roof_y),(0,P['tunnel_length'],0),'Frame aluminum')
ring('Overhead hatch pressure seat',circle(rr+.045,roof_y-.037),circle(rr,roof_y-.037),(0,-.014,0),'Seal rubber')
ring('Docking ring upper lip',circle(rr+.075,roof_y+P['tunnel_length']),circle(rr,roof_y+P['tunnel_length']),(0,.024,0),'Frame aluminum')
for side in [-1,1]:rod('Tunnel handgrip '+str(side),(side*.37,2.19,cz-.13),(side*.37,2.19,cz+.13),.014,'Cabin pale gray')
# Overhead leaf opens down/inward. Its axis is separate from the forward door.
overhead=bpy.data.objects.new('Overhead inward hatch hinge',None);bpy.context.collection.objects.link(overhead);overhead.parent=ROOTOBJ;overhead.location=(0,roof_y-.055,cz-rr-.026)
# Geometry is local to the hinge, unlike fixed geometry in cabin coordinates.
leaf_center=rr+.026;lid_radius=P['overhead_hatch_diameter']/2
lid=[(lid_radius*math.cos(a),0,leaf_center+lid_radius*math.sin(a)) for a in phis]
slab('Overhead inward hatch leaf',lid,(0,-.032,0),'Cabin pale gray',overhead)
for i in range(6):
 a=2*math.pi*i/6;rod('Overhead radial stiffener',(0,-.05,leaf_center),(.36*math.cos(a),-.05,leaf_center+.36*math.sin(a)),.012,'Frame aluminum',overhead)
rod('Overhead off-center valve',(-.17,-.04,leaf_center-.07),(-.17,-.065,leaf_center-.07),.045,'Panel charcoal',overhead,sides=24)
rod('Overhead handle',(-.13,-.08,leaf_center+.13),(.13,-.08,leaf_center+.13),.012,'Frame aluminum',overhead)
OVERHEAD={'pivot':list(overhead.location),'axis':[1,0,0],'open_radians':math.pi/2,'tunnel_center':[0,roof_y,cz],'clear_radius':rr,'length':P['tunnel_length']}
# Main instrument glare shields visible in 69-H-134; bounded away from the eye rays.
for side in [-1,1]:
 vs=[(side*.32,1.20,.57),(side*.32,1.91,.57),(side*.32,1.90,.34),(side*.32,1.25,.34)]
 slab('Main instrument glare shield '+str(side),vs,(side*.014,0,0),'Panel charcoal')
 slab('Waist panel glare hood '+str(side),[(side*.28,1.135,.72),(side*.95,1.135,.72),(side*.95,1.16,.38),(side*.28,1.16,.38)],(0,-.012,0),'Panel charcoal')
