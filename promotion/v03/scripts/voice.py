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
 ('year',5.3,'In twenty twenty-six, I built a way back to the Moon.','2026 年，我做了这个游戏，想再回一次月球。','bm_george',.89),
 ('quiet',10.7,'I wanted somewhere quiet enough to see home.','我想找个安静的地方，回头看看家。','bm_george',.89),
 ('blue',48.25,'Everyone I love lives on that fleck of blue.','我爱的人，都住在那一点蓝色里。','bm_george',.88),
 ('boots',55.9,'Look down. Just one pair of boots.','低头看，只有一双靴子。','bm_george',.86),
 ('hands',61.6,'It took thousands of hands to get them here.','把这双靴子送到这里的，是千千万万双手。','bm_george',.90),
 ('screen',77.2,'Once, the whole world leaned toward a little screen.','曾经，全世界的人都凑近了一方小小的荧屏。','bm_george',.90),
 ('feeling',84.8,'I came back for that feeling.','我想找回的，就是那种在一起的感觉。','bm_george',.87),
 ('farther',91.7,'I still believe we can go farther together.','我依然相信，我们可以一起走得更远。','bm_george',.86),
 ('sail',126.35,'From our blue Earth, we sail into eternity.','以蓝色出发，驶向永恒。','bm_george',.83)]
output=base/'assets/voice';output.mkdir(exist_ok=True)
for key,start,en,zh,voice,speed in rows:
    wave,sr=tts.create(en,voice=voice,speed=speed,lang='en-gb' if voice.startswith('b') else 'en-us')
    ids=np.flatnonzero(abs(wave)>.004)
    wave=wave[max(0,ids[0]-960):min(len(wave),ids[-1]+2500)]
    sf.write(output/(key+'.wav'),wave,sr)
manifest=[dict(id=k,start=t,en=en,zh=zh,voice=v,duration=round(sf.info(output/(k+'.wav')).duration,3)) for k,t,en,zh,v,_ in rows]
(base/'cues.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
