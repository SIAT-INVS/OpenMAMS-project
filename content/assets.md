# Assets

## Panoramic multi-agent system header

| Asset | Duration | Resolution | FPS | Purpose |
| --- | --- | --- | ---: | --- |
| [pmas-semantic-map.mp4](pmas-semantic-map.mp4) | 24 s | 1280 × 720 | 24 | H.264 video with fast-start playback |

The camera rotates around the measured COLMAP point cloud, recorded three-UAV
trajectories, and semantic observation anchors. This is not a synchronized flight
replay. Labels mark supporting UAV observation poses, not reconstructed object
centers; the COLMAP reconstruction has arbitrary scale, not calibrated meters.

The display uses UAV1 from Pose 50 onward, excludes the isolated UAV2 Pose 105,
and retains UAV3 unchanged (56, 175, and 123 trajectory points). The 58 semantic
labels share exactly the same display mask. These are visualization-only filters;
raw observations and the QA benchmark evidence are unchanged. The map is enlarged
1.4×, and the only footer reads `Panoramic multi-agent system` (32 px at 1080p).

The website MP4 is a compressed 720p version of the original 24-second render, retaining its frame rate and playback duration.

## Captioned demos

| Animation | Duration | Resolution | FPS | Size |
| --- | --- | --- | ---: | ---: |
| [Town05, K=10](town05_10uavs.mp4) | 15 s | 1600 × 360 | 10 | 3.78 MB |

The Town05 captioned demo loops automatically and is 15 seconds long at 10 FPS.
It uses a 5 × 2 view layout and is served as a compressed MP4 video.

## Panoramic three-UAV demos

| Video | Duration | Resolution | FPS | Size |
| --- | --- | --- | ---: | ---: |
| [CARLA panoramas, K=3](carla-panorama-3uavs.mp4) | 15 s | 1920 × 1080 | 30 | 4.73 MB |
| [Real-world panoramas, K=3](real-panorama-3uavs.mp4) | 15 s | 1920 × 1080 | 30 | 7.83 MB |

Each video uses three columns, with a 360° panorama above a rectified 90° FPV view for each UAV. Qwen3-VL 8B captions are generated offline from the FPV images and update every four seconds of playback.

The website clips retain the first 15 seconds of the original 20-second videos at the same 2× playback speed: 30 seconds of source footage per clip. The CARLA clip covers simulation seconds 0–30 in Town05; the real-world clip covers source-video seconds 50–80 for each UAV. Panorama and FPV views use the same frame within each UAV; the real-world sources are aligned by video-relative time, not a verified shared clock.

Both clips are compressed H.264 MP4s with fast-start playback, 8-bit YUV 4:2:0 pixel format, and no audio. The original 20-second master videos are preserved locally. Sizes above use decimal MB.

## Robot Dog demo

[Robot Dog video](robot-dog.mp4): 15.9 seconds, 1280 × 720, 30 FPS. The robot navigates to a basketball court, with first-person, third-person, and point-cloud views. Playback is muted by default; the native controls can enable the original audio.

## MemNTN paper figures

Figures from *Memory-Native Non-Terrestrial Networks for Embodied Intelligence*,
IEEE Communications Standards Magazine, 2026.

| Asset | Figure |
| --- | --- |
| [memntn_fig1.webp](memntn_fig1.webp) | Satellite-enabled perception and remote question answering |
| [memntn_fig4.webp](memntn_fig4.webp) | Simulation setup and evaluation |

Figure 1 geographic data sources: OpenStreetMap, LEOPath, and Mega-NeRF/Mill-19.
