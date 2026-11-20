"""Physical LPD strokes on BOTH CDR panes, projected from one authored eye.
Layout reference: NASA TM X-58040 Fig4 (lower cross at 40deg), 0..60 scale.
No copied texture, HUD, guidance or autopilot. Font is our own simple stroke digits.
"""
mat('LPD inner amber',(.74,.63,.34),0,.8);mat('LPD outer amber',(.62,.49,.26),0,.8)
eye=Vector((.52,1.64,.50));w=next(w for w in windows if w['name']=='CDR left');c=Vector(w['center']);n=Vector(w['normal']);u=Vector(w['u']);v=Vector(w['v']);clear=[Vector(p) for p in w['clear_loop']]
segments=[]
def line(a,b,tag):segments.append((a,b,tag))
# Each coordinate is (look-down angle, screen-right azimuth), in nominal degrees.
for a in range(60):line((a,0),(a+1,0),'vertical')
for a in range(0,61,2):
 width=.82 if a%10==0 else .45
 line((a,-width),(a,width),'vertical tick')
for row in [0,40]:
 for b in range(-10,10):line((row,b),(row,b+1),'horizontal')
 for b in range(-10,11):
  h=.50 if b%5==0 else .22
  line((row-h,b),(row+h,b),'horizontal tick')
# Seven-segment digits, locally authored straight strokes, upright while looking out.
digit_segments={'a':((-.23,.44),(.23,.44)),'b':((.25,.40),(.25,.03)),'c':((.25,-.03),(.25,-.40)),'d':((-.23,-.44),(.23,-.44)),'e':((-.25,-.40),(-.25,-.03)),'f':((-.25,.03),(-.25,.40)),'g':((-.23,0),(.23,0))}
digits=['abcdef','bc','abged','abgcd','fgbc','afgcd','afgecd','abc','abcdefg','abfgcd']
def label(value,a,b,height=1.15):
 text=str(value);pitch=height*.72
 for i,ch in enumerate(text):
  bc=b+(i-(len(text)-1)/2)*pitch
  for seg in digits[int(ch)]:
   p,q=digit_segments[seg];line((a-p[1]*height,bc+p[0]*height),(a-q[1]*height,bc+q[0]*height),'digit '+text)
for a in range(10,61,10):label(a,a-1.20 if a==40 else a,1.65)
for row in [0,40]:
 for b in [-10,-5,5,10]:label(abs(b),row-1.20,b,height=1.0)
label(0,-1.20,1.65)
def project(a,b,offset):
 ar,br=math.radians(a),math.radians(b);direction=Vector((-math.sin(br)*math.cos(ar),-math.sin(ar),math.cos(br)*math.cos(ar)));origin=c+n*offset;t=n.dot(origin-eye)/n.dot(direction);return eye+direction*t
poly=[Vector(((p-c).dot(u),(p-c).dot(v))) for p in clear]
def inside(p):
 pt=Vector(((p-c).dot(u),(p-c).dot(v)));cs=[]
 for i,a in enumerate(poly):
  e=poly[(i+1)%len(poly)]-a;d=pt-a;cs.append(e.x*d.y-e.y*d.x)
 return min(cs)>-1e-7 or max(cs)<1e-7
registration=[];counts={};clipped=[]
for layer,offset,material in [('inner',-.0502,'LPD inner amber'),('outer',-.0132,'LPD outer amber')]:
 vs=[];fs=[]
 for a,b,tag in segments:
  pa,pb=project(*a,offset),project(*b,offset);side=n.cross(pb-pa).normalized()*.00042;quad=[pa-side,pb-side,pb+side,pa+side]
  if not all(inside(p) for p in quad):clipped.append({'layer':layer,'tag':tag,'a':a,'b':b});continue
  j=len(vs);vs.extend([tuple(p) for p in quad]);fs.append((j,j+1,j+2,j+3))
 ob=mesh('LPD CDR '+layer+' pane scribed geometry',vs,fs,material);ob['lpd_ink']=True;counts[layer]=len(fs)
for a in [0,10,20,30,40,50,58]:registration.append({'angle':a,'inner':list(project(a,0,-.0502)),'outer':list(project(a,0,-.0132))})
LPD={'reference_eye':list(eye),'axis_zero':[0,0,1],'vertical_degrees':[0,60],'lower_horizontal_degrees':40,'horizontal_range_degrees':[-10,10],'ink_surfaces':{'inner':-.0502,'outer':-.0132},'registration':registration,'segments':counts,'clipped':clipped,'history_status':'Nominal body-axis angles; authored lean eye and R1 window attitude not historically certified. Fig4 lower cross40 differs from photo sample50.'}
