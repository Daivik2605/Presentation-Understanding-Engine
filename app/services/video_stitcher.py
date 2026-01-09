import subprocess
import uuid
from pathlib import Path

VIDEO_DIR = Path("data/videos")
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

def stitch_videos(video_paths: list[str]) -> str:
    if len(video_paths) == 1:
        return video_paths[0]

    list_file = VIDEO_DIR / f"{uuid.uuid4()}.txt"
    output_video = VIDEO_DIR / f"{uuid.uuid4()}.mp4"

    # Create concat file
    with open(list_file, "w") as f:
        for path in video_paths:
            f.write(f"file '{Path(path).absolute()}'\n")

    # Run ffmpeg concat
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(output_video)
    ], check=True)
    print("Final video path:", output_path)
    return str(output_video)
