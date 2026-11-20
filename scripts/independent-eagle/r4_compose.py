from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,hashlib
r=Path(__file__).resolve().parents[2];d=r/'docs/independent-eagle/r4';e=d/'evidence';im=Image.new('RGB',(1200,3110),'#10191c');draw=ImageDraw.Draw(im);font='/System/Library/Fonts/STHeiti Medium.ttc';inputs=[]
def tx(x,y,s,size=26,color='#e8ede7'):draw.text((x,y),s,font=ImageFont.truetype(font,size),fill=color)
def photo(n,b):
 p=e/(n+'.jpg');inputs.append(p);a=Image.open(p).convert('RGB');im.paste(ImageOps.fit(a,(b[2]-b[0],b[3]-b[1]),method=Image.Resampling.LANCZOS),(b[0],b[1]))
def pair(a,b,y):photo(a,(30,y,585,y+390));photo(b,(615,y,1170,y+390))
tx(34,26,'EAGLE R4 · 过门、平台与返舱',46);tx(34,91,'同一个真实着装角色／背包 · 保留 R2 舱体和 32 in 净口',27,'#b6d6c3')
tx(34,145,'本轮结构通行通过；默认入口、LPD、月球车与喷尘未改。',26)
tx(34,209,'01  相同舱体局部机位 · 起点',32);tx(34,261,'R3：躯干绕脚底，起始穿入低盖',25);tx(620,261,'R4：骨盆枢轴，站旁等待开门',25)
pair('r3-start','r4-start',306)
tx(34,751,'02  相同机位 · 低姿过门（时序已重排）',32);tx(34,803,'R3 t=3 s：身体／手臂穿插',25);tx(620,803,'R4 过门中段：抬头，收臂通过',25)
pair('r3-through','r4-through',848)
tx(34,1259,'剖视只改显示；检查始终包含完整舱壁、门扇、门框及平台。',25)
tx(34,1320,'03  实际开门和返舱收门 · 完整舱壁',32);tx(34,1372,'舱内门闭，角色已在安全站位',25);tx(620,1372,'先开门，再低姿移动到门口',25)
pair('r4-closed','r4-open',1417)
tx(34,1867,'04  全身到平台，停在扶栏低姿；不接下梯',32)
photo('r4-porch',(30,1922,1170,2724))
tx(34,2745,'验证：60 Hz 模拟、30 Hz 网格导出；双向 1,322 姿态无三角面交叉。',24,'#b6d6c3')
tx(34,2790,'实际靴底距支承面约 6 mm；平台双手距真实扶栏约 3.7–4.4 mm。',24)
tx(34,2835,'角色和舱体未缩放；网格顶点未改，新增有限颈部骨骼和接触目标。',24)
tx(34,2880,'已跑生产构建、按钮／空格／F／滑条、完整出返舱及默认启动回归。',24)
tx(34,2925,'范围：运动学接触，非人体受力认证；未做下梯或移动端性能认证。',24,'#efc99b')
tx(34,2980,'独立可分享素材＋原游戏；无 A11D 衍生、无公开部署／推送。',24,'#a7bfba')
tx(34,3030,'短片约 28.9 s（1.5×），含完整出舱到平台及返舱收门。',24,'#a7bfba')
out=d/'Eagle-R4-phone-comparison.png';im.save(out,optimize=True)
(d/'image-provenance.json').write_text(json.dumps({'privatePrintInputs':False,'sameLocalCamera':{'eye':[3.8,4.30,1.7],'target':[0,3.75,1.7],'fov':48},'comparisonTimesDiffer':True,'inputs':[{'path':str(p.relative_to(r)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in inputs]},indent=2)+'\n');print(out,out.stat().st_size)
