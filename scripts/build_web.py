"""Make the same-origin edition from the standalone lunar game."""

import base64
import fcntl
import hashlib
import re
from pathlib import Path
from tempfile import TemporaryDirectory


def build(source, out):
    assets = out / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    page = source.read_text(encoding="utf-8")

    def save(data, name, extension):
        suffix = hashlib.sha256(data).hexdigest()[:16]
        dest = assets / f"{name}.{suffix}.{extension}"
        dest.write_bytes(data)
        return dest.name

    def graphics(text, prefix):
        def asset(match):
            extension, encoded = match.groups()
            return prefix + save(base64.b64decode(encoded, validate=True), "image", extension)

        return re.sub(r"data:image/(webp|jpeg|png);base64,([A-Za-z0-9+/=]+)", asset, text)

    def style(match):
        css = graphics(match[1], "./")
        css += '\n#launchStart:disabled{cursor:wait}\n'
        name = save(css.encode(), "moon", "css")
        return f'<link rel="stylesheet" href="./assets/{name}">'

    def code(match):
        js = graphics(match[1], "./assets/")

        def audio(clip):
            key, encoded = clip.groups()
            name = save(base64.b64decode(encoded, validate=True), "apollo-" + key, "mp3")
            return f'{key}:"./assets/{name}"'

        js, count = re.subn(r'(landing|step):"data:audio/mpeg;base64,([A-Za-z0-9+/=]+)"', audio, js)
        if count != 2:
            raise ValueError("expected two archive recordings")
        start = js.index('      const encoded=archiveClips[key].split(",")[1];')
        end = js.index('      buffers.set(key,decoding);', start)
        decoder = '''      const decoding=fetch(archiveClips[key]).then(response=>{
        if(!response.ok)throw new Error("录音载入失败 "+response.status);
        return response.arrayBuffer();
      }).then(bytes=>audioCtx.decodeAudioData(bytes)).catch(error=>{
        buffers.delete(key);throw error;
      });
'''
        js = js[:start] + decoder + js[end:]
        js = js.replace(
            'if(fallbackRadio.src!==archiveClips[key])',
            'if(fallbackRadio.getAttribute("src")!==archiveClips[key])',
        )
        needle = '$("launchStart").disabled=false;'
        if js.count(needle) != 1:
            raise ValueError("expected one game ready signal")
        js = js.replace(needle, '$("launchStart").firstElementChild.textContent="开始任务";' + needle)
        name = save(js.encode(), "moon", "js")
        return f'<script src="./assets/{name}"></script>'

    page = page.replace("</title>", '</title>\n<link rel="icon" type="image/svg+xml" href="/favicon.svg?v=2">', 1)
    page = page.replace('id="launchStart" disabled><span>开始任务', 'id="launchStart" disabled><span>正在载入…')
    page, nstyles = re.subn(r"<style>(.*?)</style>", style, page, flags=re.DOTALL)
    page, nscripts = re.subn(r"<script>(.*?)</script>", code, page, flags=re.DOTALL)
    if (nstyles, nscripts) != (1, 1):
        raise ValueError("expected one stylesheet and one game script")
    (out / "index.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    project = Path(__file__).resolve().parents[1]
    release = project / "web-release"
    play = release / "play"
    release.mkdir(exist_ok=True)
    with Path(__file__).open("rb") as lock, TemporaryDirectory(dir=release) as scratch:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        staged = Path(scratch)
        build(project / "index.html", staged)
        target = play / "assets"
        target.mkdir(parents=True, exist_ok=True)
        generated = {item.name for item in (staged / "assets").iterdir()}
        for item in (staged / "assets").iterdir():
            item.replace(target / item.name)
        (staged / "index.html").replace(play / "index.html")
        for item in target.iterdir():
            if item.name not in generated and re.fullmatch(r"(moon|image|apollo-landing|apollo-step)\.[a-f0-9]{16}\.(js|css|mp3|webp|jpeg|png)", item.name):
                item.unlink()
    print(f"Built {len(generated)} assets and {play / 'index.html'}")
