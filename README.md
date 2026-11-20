# aMoon R4 — isolated hatch/porch delivery

This is an isolated, owner-authorized runnable snapshot on an orphan delivery branch. Original default and R3 are retained. The bundle contains no original project Git history or remote configuration.

```sh
python3 scripts/independent-eagle/build_r4_release.py
python3 -m http.server 8000 --bind 127.0.0.1
```

Open http://127.0.0.1:8000/web-release/r4-play/ . Space plays/pauses, F reverses, and the visible controls select views and poses.

Scope, measured checks, environment, known limitations and full reproduction: [R4 record](docs/independent-eagle/r4/README.md). Third-party asset credits remain in the original game flight manual. The independently redrawn cabin has its own CC0 license under assets/models/independent-eagle. No restricted print-model derivatives, secrets, dependencies, large temporary frames or build outputs are included.
