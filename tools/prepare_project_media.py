"""Prepare web assets from the original research figures and demonstrations.

Optional regeneration: pip install pillow imageio-ffmpeg
Then: python tools/prepare_project_media.py
The published website needs no Python dependencies.
"""
from pathlib import Path
import subprocess
from PIL import Image, ImageSequence
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "source" / "assets"
DEST = ROOT / "assets"
DEST.mkdir(parents=True, exist_ok=True)
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

for source in SOURCE.glob("*.png"):
    if source.stem in {"memntn_fig2", "memntn_fig3"}:
        continue
    with Image.open(source) as im:
        im.convert("RGB").save(DEST / f"{source.stem}.webp", quality=92, method=6)

for name in ("town04_4uavs", "town05_10uavs", "pmas-semantic-map"):
    extension = ".gif" if name == "town04_4uavs" else ".webp"
    with Image.open(SOURCE / f"{name}{extension}") as im:
        first = im.convert("RGB")
        first.thumbnail((1280, 720))
        first.save(DEST / f"{name}-poster.jpg", quality=90)
        if name == "pmas-semantic-map":
            continue
        frame_count = im.n_frames
        duration_ms = sum(frame.info.get("duration", 100) for frame in ImageSequence.Iterator(im))
        fps = frame_count * 1000 / duration_ms
        im.seek(0)
        command = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-vcodec", "rawvideo",
                   "-pix_fmt", "rgb24", "-s", f"{im.width}x{im.height}", "-r", str(fps), "-i", "-",
                   "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p",
                   "-movflags", "+faststart", str(DEST / f"{name}.mp4")]
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        for frame in ImageSequence.Iterator(im):
            process.stdin.write(frame.convert("RGB").tobytes())
        process.stdin.close()
        if process.wait() != 0:
            raise RuntimeError(f"Could not encode {name}")
        print(f"Prepared {name}: {frame_count} frames, {duration_ms / 1000:.1f} s")

subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(SOURCE / "pmas-semantic-map.mp4"),
                "-vf", "scale=1280:-2", "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "30",
                "-maxrate", "1600k", "-bufsize", "3200k",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(DEST / "pmas-semantic-map.mp4")], check=True)
subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(SOURCE / "robot-dog.mp4"),
                "-vf", "scale=1280:-2", "-c:v", "libx264", "-preset", "slow", "-crf", "23",
                "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart",
                str(DEST / "robot-dog.mp4")], check=True)
subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-ss", "1", "-i", str(DEST / "robot-dog.mp4"),
                "-frames:v", "1", "-q:v", "3", "-update", "1",
                str(DEST / "robot-dog-poster.jpg")], check=True)
print("Web media ready in assets.")
