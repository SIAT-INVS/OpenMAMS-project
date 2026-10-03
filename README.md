# OpenMAMS Project Page

Standalone project website for [SIAT-INVS/OpenMAMS](https://github.com/SIAT-INVS/OpenMAMS).

The video fills the first screen using cover cropping and has no overlaid title or tagline. Below it, the page preserves the original repository README wording, section order, results, and citations. `source/README.md` and `source/assets/README.md` are the original source documents; `source/assets/` preserves every original research figure and animation. The code repository can therefore retain a short README and remove its presentation assets.

## Preview

```sh
node tools/preview.mjs
```

Open http://127.0.0.1:8000/OpenMAMS-project/ . No package installation is needed.

## Publish

Create a separate public GitHub repository named `SIAT-INVS/OpenMAMS-project`, then push the contents of this directory to its `main` branch. In **Settings → Pages**, select **Deploy from a branch**, **main**, and **/(root)**.

Expected URL: https://siat-invs.github.io/OpenMAMS-project/

Publishing the existing HTML requires no build tools, Python installation, or GitHub Actions configuration.

## Files

- `index.html`: the complete original README content, with a responsive layout.
- `assets.html`: original asset descriptions and links to the original files.
- `project.css`, `project.js`: layout, visible-media autoplay, and citation copying.
- `assets/`: optimized WebP figures, MP4 animations, and poster images for web display.
- `source/`: the original README and original research media, preserved without modification.
- `tools/`: optional content regeneration, media preparation, and local preview tools.

Demonstrations automatically loop silently when visible. The header has no visible playback controls; inline demos retain native pause and seek controls. Playback stops when a demo leaves the viewport or the browser tab is hidden. Reduced-motion visitors see a still header and can play inline demos manually. The displayed MP4s are derived from the original animations; the original GIF/WebP files remain available through `assets.html`.

## Update content

Edit `source/README.md`, then regenerate:

```sh
python -m pip install markdown beautifulsoup4
python tools/build_page.py
```

The generator omits the Code heading, module introduction, and module table, which remain in the code repository, and promotes Demos to its own section. It applies the requested Results heading, verifies the remaining research text after whitespace normalization, then removes the duplicate navigation and paper-link rows below the affiliations as requested. Navigation labels and their order are maintained in NAV_ITEMS in tools/build_page.py. The source snapshot remains intact. Navigation labels, video fallback links, and citation-copy controls are interface elements.

To regenerate optimized media from the preserved originals:

```sh
python -m pip install pillow imageio-ffmpeg
python tools/prepare_project_media.py
```

The website layout is independently implemented, with the full-width animated cover of https://metaslam.github.io/ and the academic presentation style of https://hanruihua.github.io/srl_mpc_project/ as references.

The user-supplied Robot Dog demo follows Town05 in Demos. Its original is preserved as `source/assets/robot-dog.mp4`; `assets/robot-dog.mp4` is the 720p web version, with original audio retained and playback muted by default. Its caption and placement are maintained in `tools/build_page.py`.
