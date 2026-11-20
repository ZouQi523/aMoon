"""Copy an explicit shareable allowlist to a NEW isolated delivery working tree.
Does not touch the source checkout's Git, existing files, remotes or private research.
"""
from pathlib import Path
import sys,json,hashlib,shutil
r=Path(__file__).resolve().parents[2];out=Path(sys.argv[1]).resolve();assert not out.exists() or {p.name for p in out.iterdir()}=={'.git'},f'Destination must be new or an empty orphan worktree: {out}'
files=['index.html','scripts/build_web.py',
 'scripts/independent-eagle/build_r4_preview.py','scripts/independent-eagle/build_r4_release.py',
 'scripts/independent-eagle/package_r4.py','scripts/independent-eagle/r4_verify.py','scripts/independent-eagle/r4_review.js','scripts/independent-eagle/r4_audit.mjs','scripts/independent-eagle/r4_check.py','scripts/independent-eagle/r4_motion.py','scripts/independent-eagle/r4_smoke.mjs','scripts/independent-eagle/r4_rig_test.mjs','scripts/independent-eagle/r4_capture.mjs','scripts/independent-eagle/r4_compose.py',
 'scripts/independent-eagle/build_egress_preview.py','scripts/independent-eagle/egress_review.js','scripts/independent-eagle/review.js',
 'scripts/independent-eagle/build_model.py','scripts/independent-eagle/add_r2_structure.py','scripts/independent-eagle/add_lpd.py',
 'assets/models/independent-eagle/front-cabin.json','assets/models/independent-eagle/front-cabin.glb','assets/models/independent-eagle/front-cabin.blend','assets/models/independent-eagle/LICENSE.txt','assets/models/independent-eagle/r1/front-cabin.json',
 'references/independent-eagle/r2/references-r2.json',
 'docs/independent-eagle/r3/baseline.json',
 'docs/independent-eagle/r4/README.md','docs/independent-eagle/r4/baseline.json','docs/independent-eagle/r4/verification.json','docs/independent-eagle/r4/production-smoke.json','docs/independent-eagle/r4/rig-preservation.json','docs/independent-eagle/r4/motion-continuity.json','docs/independent-eagle/r4/dense/collision-report.json']
assert all((r/p).is_file() for p in files)
assert all('.local-eagle' not in p and '/audit/' not in p and '.env' not in p and 'Apollo11' not in p for p in files)
out.mkdir(parents=True,exist_ok=True)
for p in files:
 dest=out/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/p,dest)
(out/'README.md').write_text('# aMoon R4 — isolated hatch/porch delivery\n\nThis is an isolated, owner-authorized runnable snapshot on an orphan delivery branch. Original default and R3 are retained. The bundle contains no original project Git history or remote configuration.\n\n```sh\npython3 scripts/independent-eagle/build_r4_release.py\npython3 -m http.server 8000 --bind 127.0.0.1\n```\n\nOpen http://127.0.0.1:8000/web-release/r4-play/ . Space plays/pauses, F reverses, and the visible controls select views and poses.\n\nScope, measured checks, environment, known limitations and full reproduction: [R4 record](docs/independent-eagle/r4/README.md). Third-party asset credits remain in the original game flight manual. The independently redrawn cabin has its own CC0 license under assets/models/independent-eagle. No restricted print-model derivatives, secrets, dependencies, large temporary frames or build outputs are included.\n')
(out/'.gitignore').write_text('/web-release/\nnode_modules/\n__pycache__/\n*.py[cod]\n.env\n.env.*\n*.bundle\n/docs/independent-eagle/r4/**/audit/\n/docs/independent-eagle/r4/movie-frames/\n/docs/independent-eagle/r4/evidence/\n')
manifest={p:hashlib.sha256((out/p).read_bytes()).hexdigest() for p in files}
(out/'delivery-source-manifest.json').write_text(json.dumps({'scope':'Shareable default runtime snapshot + independent R4 and retained R3; no source checkout mutation','files':manifest},indent=2)+'\n')
print(out);print('Copied',len(files),'explicit files; no private research or history')
