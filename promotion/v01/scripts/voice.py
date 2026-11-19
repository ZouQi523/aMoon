from pathlib import Path
import sys,json
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro
base=Path(__file__).resolve().parents[1]
model=Path(sys.argv[1])
tts=Kokoro(str(model/'kokoro.onnx'),str(model/'voices.bin'))
# The narrator speaks from inside Columbia. The surface crew answers on the return leg.
rows=[
 ('listen',1.65,'I knew their footsteps by the sound of their breathing.','听着他们的呼吸，我就知道他们又迈出了一步。','bm_george',.91),
 ('dark',10.65,'Though my soul may set in darkness,','纵使我的灵魂沉入黑暗，','bm_george',.84),
 ('light',14.45,'it will rise in perfect light.','它终将在澄澈的光中升起。','bm_george',.84),
 ('stars',19.10,'I have loved the stars too truly','我如此真切地爱过繁星，','bm_george',.86),
 ('night',22.85,'to be fearful of the night.','又怎会畏惧黑夜。','bm_george',.85),
 ('print',28.10,'Someone stood here once.','曾经，有人站在这里。','bm_george',.91),
 ('drop',35.25,'Ready? Let go.','准备好了？松手。','af_heart',.93),
 ('again',48.65,'Alone up here, I kept one eye on the needles.','独自留在舱里，我的目光总回到那些指针上。','bm_george',.91),
 ('contact',57.20,'Columbia, this is Eagle. We have you in sight.','哥伦比亚号，这里是鹰号。我们看见你了。','af_heart',.98),
 ('latch',67.25,'Hard dock.','对接锁定。','bm_george',.95),
 ('welcome',69.05,'Welcome back aboard.','欢迎归舱。','bm_george',.86)]
rows.extend([
 ('gentle',11.6,'Do not go gentle into that good night.','不要温顺地走进那个良夜。','bm_george',.81),
 ('rage',20.75,'Rage, rage against the dying of the light.','怒吼吧，怒吼吧，抗拒那渐熄的光。','bm_george',.79)])
output=base/'assets/voice';output.mkdir(exist_ok=True)
for key,start,en,zh,voice,speed in rows:
    wave,sr=tts.create(en,voice=voice,speed=speed,lang='en-gb' if voice.startswith('b') else 'en-us')
    ids=np.flatnonzero(abs(wave)>.004)
    wave=wave[max(0,ids[0]-960):min(len(wave),ids[-1]+2500)]
    sf.write(output/(key+'.wav'),wave,sr)
manifest=[dict(id=k,start=t,en=en,zh=zh,voice=v,duration=round(sf.info(output/(k+'.wav')).duration,3)) for k,t,en,zh,v,_ in rows]
(base/'cues.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
