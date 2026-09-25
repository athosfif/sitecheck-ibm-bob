#!/usr/bin/env python3
"""Build the 1080p silent SiteCheck demo from local, reproducible assets."""

from pathlib import Path
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCENES = ROOT / "docs" / "video-scenes"
BUILD = ROOT / "video-build"
DELIVERABLES = ROOT.parent / "DELIVERABLES"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
AUDIO_PARTS = [
    ROOT.parents[1] / "NARRAÇÃO DO VIDEO EXPLICATIVO" / "part 1.mp3",
    ROOT.parents[1] / "NARRAÇÃO DO VIDEO EXPLICATIVO" / "part 2.mp3",
    ROOT.parents[1] / "NARRAÇÃO DO VIDEO EXPLICATIVO" / "part 3.mp3",
]


def run(*args: str) -> None:
    print("+", " ".join(map(str, args)))
    subprocess.run(list(map(str, args)), check=True)


def screenshot(source: Path, output: Path, size: str = "1920,1080") -> None:
    run(
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--allow-file-access-from-files",
        f"--window-size={size}",
        f"--screenshot={output}",
        source.resolve().as_uri(),
    )


def still_clip(ffmpeg: str, image: Path, output: Path, duration: int, mode: str = "hold") -> None:
    if mode == "pan-down":
        vf = f"scale=1920:-1,crop=1920:1080:0:'min((ih-oh)*t/{duration},ih-oh)',fps=30,format=yuv420p"
    elif mode == "zoom":
        frames = duration * 30
        vf = f"scale=2048:-1,zoompan=z='min(zoom+0.00018,1.035)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080:fps=30,format=yuv420p"
    else:
        vf = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=yuv420p"
    run(ffmpeg, "-y", "-loop", "1", "-i", image, "-t", str(duration), "-vf", vf,
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", output)


def main() -> None:
    if not CHROME.exists():
        raise SystemExit("Google Chrome was not found.")
    runtime_python = Path("/Users/athvs/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3")
    probe = subprocess.run(
        [runtime_python, "-c", "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"],
        check=True, capture_output=True, text=True,
    )
    ffmpeg = probe.stdout.strip()

    if BUILD.exists():
        # External APFS volumes can expose transient AppleDouble files while
        # deleting. They are disposable build artifacts, so tolerate races.
        shutil.rmtree(BUILD, ignore_errors=True)
    BUILD.mkdir()
    DELIVERABLES.mkdir(exist_ok=True)

    captures = {
        "01-demo": (ROOT / "demo-site" / "index.html", "1920,1080"),
        "02-before": (ROOT / "sitecheck-output" / "before" / "report.html", "1920,2160"),
        "03-code": (SCENES / "code-fix.html", "1920,1080"),
        "04-comparison": (ROOT / "sitecheck-output" / "comparison" / "comparison.html", "1920,2160"),
        "05-tests": (SCENES / "tests.html", "1920,1080"),
        "06-bob": (SCENES / "bob-sessions.html", "1920,1080"),
        "07-end": (SCENES / "end-card.html", "1920,1080"),
    }
    for name, (source, size) in captures.items():
        screenshot(source, BUILD / f"{name}.png", size)

    # Pacing follows the actual three-part voice recording (about 90 seconds).
    plan = [
        ("01-demo", 6, "zoom"),
        ("02-before", 30, "pan-down"),
        ("03-code", 10, "hold"),
        ("04-comparison", 13, "pan-down"),
        ("05-tests", 7, "hold"),
        ("06-bob", 17, "zoom"),
        ("07-end", 9, "hold"),
    ]
    clips = []
    for index, (name, duration, mode) in enumerate(plan, 1):
        clip = BUILD / f"clip-{index:02}.mp4"
        still_clip(ffmpeg, BUILD / f"{name}.png", clip, duration, mode)
        clips.append(clip)

    concat = BUILD / "concat.txt"
    concat.write_text("".join(f"file '{clip}'\n" for clip in clips), encoding="utf-8")
    raw_master = BUILD / "silent-unbranded.mp4"
    run(ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", concat, "-c", "copy", raw_master)

    # One official Figueira symbol. The current scenes are light, so the black
    # transparent version gives the cleanest contrast; a white companion asset
    # is retained for future dark-background edits.
    badge = SCENES / "figueira-symbol.png"
    badge_white = SCENES / "figueira-symbol-white.png"
    master = DELIVERABLES / "SiteCheck-silent-demo-1080p.mp4"
    run(
        ffmpeg, "-y", "-i", raw_master, "-i", badge, "-i", badge_white,
        "-filter_complex",
        (
            "[1:v]scale=-1:40[black];[2:v]scale=-1:40[white];"
            "[0:v][black]overlay=20:7:format=auto:enable='between(t,0,6)'[branded];"
            "[branded][white]overlay=20:7:format=auto:enable='between(t,6,92)',format=yuv420p[v]"
        ),
        "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-movflags", "+faststart", master,
    )

    missing = [str(path) for path in AUDIO_PARTS if not path.exists()]
    if missing:
        print("Voice parts not found; silent master is ready:", master)
        return

    # Normalize each take, keep a short editorial pause between recordings, and preserve mono voice.
    voice = DELIVERABLES / "SiteCheck-voiceover-master.wav"
    filter_graph = (
        "anullsrc=r=48000:cl=mono,atrim=0:0.4[intro];"
        "[0:a]highpass=f=70,lowpass=f=14000,loudnorm=I=-16:LRA=7:TP=-1.5,aresample=48000[a0];"
        "anullsrc=r=48000:cl=mono,atrim=0:0.25[p1];"
        "[1:a]highpass=f=70,lowpass=f=14000,loudnorm=I=-16:LRA=7:TP=-1.5,aresample=48000[a1];"
        "anullsrc=r=48000:cl=mono,atrim=0:0.25[p2];"
        "[2:a]highpass=f=70,lowpass=f=14000,loudnorm=I=-16:LRA=7:TP=-1.5,aresample=48000[a2];"
        "anullsrc=r=48000:cl=mono,atrim=0:0.5[outro];"
        "[intro][a0][p1][a1][p2][a2][outro]concat=n=7:v=0:a=1[voice]"
    )
    run(
        ffmpeg, "-y", "-i", AUDIO_PARTS[0], "-i", AUDIO_PARTS[1], "-i", AUDIO_PARTS[2],
        "-filter_complex", filter_graph, "-map", "[voice]", "-c:a", "pcm_s24le", voice,
    )

    final = DELIVERABLES / "SiteCheck-final-voice-1080p.mp4"
    run(
        ffmpeg, "-y", "-i", master, "-i", voice, "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart", final,
    )

    captioned = DELIVERABLES / "SiteCheck-final-captioned-1080p.mp4"
    run(
        ffmpeg, "-y", "-i", final,
        "-vf", "subtitles=docs/sitecheck-captions.ass:fontsdir=/Users/athvs/Library/Fonts,format=yuv420p",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "copy",
        "-movflags", "+faststart", captioned,
    )
    print(f"\nREADY: {master}\nREADY: {voice}\nREADY: {final}\nREADY: {captioned}")


if __name__ == "__main__":
    main()
