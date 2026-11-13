import json
import shutil
import subprocess
from pathlib import Path

from django.conf import settings


# --- Rendition ladder -------------------------------------------------------
# (name, width, height, video_bitrate, audio_bitrate)
# FFmpeg will scale to fit within (width, height) preserving aspect ratio.
RENDITIONS = [
    ("360p",  640,  360,  "800k",  "96k"),
    ("720p",  1280, 720,  "2800k", "128k"),
    ("1080p", 1920, 1080, "5000k", "160k"),
]

HLS_SEGMENT_DURATION = 6   # seconds per .ts segment
HLS_PLAYLIST_TYPE = "vod"

# Hard ceiling for a single FFmpeg invocation (matches Celery soft limit).
FFMPEG_TIMEOUT_SECONDS = 50 * 60


class TranscodeError(Exception):
    pass


def _probe_source(source_path: Path) -> dict:
    """Return basic info about the source (duration, resolution). Raises on failure."""
    cmd = [
        "ffprobe", "-v", "error",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(source_path),
    ]
    try:
        out = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60, check=True
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        raise TranscodeError(f"ffprobe failed on {source_path.name}: {e}") from e
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError as e:
        raise TranscodeError(f"ffprobe returned invalid JSON: {e}") from e


def _pick_renditions(source_info: dict) -> list[tuple[str, int, int, str, str]]:
    """
    Drop renditions the source can't natively fill (upscaling is wasteful and
    produces poor quality). E.g. a 720p source gets 360p + 720p, not 1080p.
    """
    video_stream = next(
        (s for s in source_info.get("streams", []) if s.get("codec_type") == "video"),
        None,
    )
    if video_stream is None:
        raise TranscodeError("Source has no video stream.")
    src_height = int(video_stream.get("height") or 0)
    if src_height <= 0:
        raise TranscodeError("Source video stream has no height (corrupt file?).")

    chosen = [r for r in RENDITIONS if r[2] <= src_height]
    if not chosen:
        # Source smaller than the smallest rendition — include the smallest anyway.
        chosen = [RENDITIONS[0]]
    return chosen


def _build_ffmpeg_command(source: Path, out_dir: Path, rendition) -> list[str]:
    name, width, height, vbitrate, abitrate = rendition
    variant_dir = out_dir / name
    variant_dir.mkdir(parents=True, exist_ok=True)
    playlist = variant_dir / "index.m3u8"
    segment_pattern = variant_dir / "seg_%03d.ts"

    return [
        "ffmpeg",
        "-y",                       # overwrite
        "-i", str(source),
        # Video: scale to fit box, preserve aspect ratio, pad if needed to even dims
        "-vf", f"scale=w={width}:h={height}:force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-profile:v", "main",
        "-crf", "20",
        "-maxrate", vbitrate,
        "-bufsize", vbitrate,        # bufsize == maxrate is common for HLS
        "-g", str(HLS_SEGMENT_DURATION * 25),  # ~keyframe every 6s @ 25fps
        "-keyint_min", str(HLS_SEGMENT_DURATION * 25),
        "-sc_threshold", "0",        # disable scene-cut keyframes for consistent segments
        # Audio
        "-c:a", "aac",
        "-b:a", abitrate,
        "-ac", "2",
        # HLS muxer
        "-f", "hls",
        "-hls_time", str(HLS_SEGMENT_DURATION),
        "-hls_playlist_type", HLS_PLAYLIST_TYPE,
        "-hls_segment_filename", str(segment_pattern),
        str(playlist),
    ]


def _run_ffmpeg(cmd: list[str]) -> None:
    """Run FFmpeg, raising TranscodeError with stderr tail on failure."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=FFMPEG_TIMEOUT_SECONDS, check=False,
        )
    except subprocess.TimeoutExpired as e:
        raise TranscodeError(f"FFmpeg timed out after {FFMPEG_TIMEOUT_SECONDS}s") from e
    if result.returncode != 0:
        tail = "\n".join((result.stderr or "").splitlines()[-30:])
        raise TranscodeError(f"FFmpeg exited {result.returncode}\n{tail}")


def _write_master_manifest(out_dir: Path, renditions: list[tuple]) -> Path:
    """
    Write master.m3u8 referencing each variant playlist with BANDWIDTH/RESOLUTION hints.
    """
    lines = ["#EXTM3U", "#EXT-X-VERSION:3"]
    for name, width, height, vbitrate, abitrate in renditions:
        # Approximate bandwidth in bits/sec: video + audio + 10% muxing overhead.
        vb = int(vbitrate.rstrip("k")) * 1000
        ab = int(abitrate.rstrip("k")) * 1000
        bandwidth = int((vb + ab) * 1.1)
        lines.append(
            f'#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},'
            f'AVERAGE-BANDWIDTH={bandwidth},RESOLUTION={width}x{height}'
        )
        lines.append(f"{name}/index.m3u8")
    master_path = out_dir / "master.m3u8"
    master_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return master_path


def transcode(source_path: Path, out_dir: Path) -> Path:
    """
    Transcode `source_path` to HLS in `out_dir`. Returns the master.m3u8 path.
    Raises TranscodeError on any failure.
    """
    if not source_path.exists():
        raise TranscodeError(f"Source file missing: {source_path}")

    if out_dir.exists():
        # Idempotency for retries: if a complete previous run exists, reuse it.
        existing_master = out_dir / "master.m3u8"
        if existing_master.exists():
            return existing_master
        # Partial run: clean and restart.
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    info = _probe_source(source_path)
    renditions = _pick_renditions(info)

    for rendition in renditions:
        _run_ffmpeg(_build_ffmpeg_command(source_path, out_dir, rendition))

    return _write_master_manifest(out_dir, renditions)
