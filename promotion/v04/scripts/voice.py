from pathlib import Path
import sys,json
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro
base=Path(__file__).resolve().parents[1]
model=Path(sys.argv[1])
tts=Kokoro(str(model/'kokoro.onnx'),str(model/'voices.bin'))
# New lines are the maker's voice. Mission radio retains the separate crew voices.
rows=[
 ('dustline',55.45,'Look down. A footprint in the dust.','低头看。月尘里，有一枚脚印。','bm_george',.88),
 ('onemark',61.6,'It took thousands of hands to leave that one mark.','留下这一枚脚印，靠的是千千万万双手。','bm_george',.90),
 ('call',96.7,'Columbia, Eagle. Are you still there?','哥伦比亚号，这里是鹰号。你还在吗？','af_heart',.90),
 ('answer',104.5,'Still here, Eagle.','我一直都在，鹰号。','bm_george',.89),
 ('lighton',109.65,"I left the light on for you.",'我给你们留着灯。','bm_george',.90)]
output=base/'assets/voice';output.mkdir(exist_ok=True)
for key,start,en,zh,voice,speed in rows:
    wave,sr=tts.create(en,voice=voice,speed=speed,lang='en-gb' if voice.startswith('b') else 'en-us')
    ids=np.flatnonzero(abs(wave)>.004)
    wave=wave[max(0,ids[0]-960):min(len(wave),ids[-1]+2500)]
    sf.write(output/(key+'.wav'),wave,sr)
manifest=[dict(id=k,start=t,en=en,zh=zh,voice=v,duration=round(sf.info(output/(k+'.wav')).duration,3)) for k,t,en,zh,v,_ in rows]
(base/'cues.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
