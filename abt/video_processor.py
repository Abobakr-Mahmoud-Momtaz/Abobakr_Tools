import subprocess
import urllib.request
import zipfile
import tempfile
import shutil

from pathlib import Path


FFMPEG_URL = (
    "https://github.com/Abobakr-Mahmoud-Momtaz/"
    "Abobakr_Tools/releases/download/ffmpeg-7.0/"
    "ffmpeg-7.0-full_build.zip"
)

ffmpeg_root = Path(__file__).parent / "ffmpeg-7.0-full_build"
ffmpeg_folder = ffmpeg_root / "bin"

apps_path = [
    ffmpeg_folder / app
    for app in ["ffmpeg.exe", "ffprobe.exe", "ffplay.exe"]
]

ffmpeg_exe, ffprobe_exe, ffplay_exe = apps_path


def ensure_ffmpeg():
    if all(map(Path.is_file, apps_path)):
        return

    try:
        with tempfile.TemporaryDirectory(
            dir=ffmpeg_root.parent
        ) as temp:

            temp = Path(temp)
            archive = temp / "ffmpeg.zip"
            extract_dir = temp / "extracted"

            extract_dir.mkdir()

            request = urllib.request.Request(
                FFMPEG_URL,
                headers={"User-Agent": "Abobakr-Tools"}
            )

            with urllib.request.urlopen(
                request, timeout=30
            ) as response:
                with open(archive, "wb") as file:
                    shutil.copyfileobj(response, file)

            with zipfile.ZipFile(archive) as zip_file:
                zip_file.extractall(extract_dir)

            candidates = [
                path for path in extract_dir.rglob("ffmpeg.exe")
                if path.parent.name.lower() == "bin"
                and (path.parent / "ffprobe.exe").is_file()
                and (path.parent / "ffplay.exe").is_file()
            ]

            if not candidates:
                raise RuntimeError("Invalid FFmpeg archive")

            source_folder = candidates[0].parent.parent

            if ffmpeg_root.exists():
                if ffmpeg_root.is_dir():
                    shutil.rmtree(ffmpeg_root)
                else:
                    ffmpeg_root.unlink()

            shutil.move(str(source_folder), str(ffmpeg_root))

    except PermissionError as error:
        raise PermissionError(
            "Cannot install FFmpeg: permission denied. "
            "Python cannot write to the library directory."
        ) from error

    if not all(map(Path.is_file, apps_path)):
        raise RuntimeError("FFmpeg installation failed")


def execut_ffprobe(cmd):
    return subprocess.run(
        [ffprobe_exe, *cmd],
        capture_output=True,
        text=True,
        check=True
    ).stdout


def build_filters(number_of_repetitions, practical_list):
    result = []

    for i in range(number_of_repetitions):
        cache = practical_list.replace("$i", str(i))
        result.append(cache)

    return result


def execut_ffmpeg(cmd, progress_interval, size_videos,
                  overwrite, output, on_progress):
    cmd = [
        ffmpeg_exe, "-filter_threads", "1", "-filter_complex_threads", "1", *cmd,
        "-c:v", "libx264",
        "-threads", "1",
        "-progress", "pipe:1",
        "-stats_period", str(progress_interval),
        "-y" if overwrite else "-n",
        str(output)
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )

    with process.stdout:
        for line in process.stdout:
            line = line.strip()
            if "=" not in line:
                continue

            key, value = line.split("=", 1)

            if key == "out_time_us" and value.isdigit():
                percentage = (
                    int(value) / (size_videos * 1_000_000)
                ) * 100

                if on_progress is not None:
                    on_progress(percentage)

    return_code = process.wait()

    if return_code != 0:
        raise subprocess.CalledProcessError(return_code, cmd)


class VideoEditor:
    def __init__(self, videos, output, overwrite=1,
                 progress_interval=1, on_progress=None):

        ensure_ffmpeg()

        self.videos = list(videos)
        self.output = output
        self.overwrite = overwrite
        self.progress_interval = progress_interval
        self.on_progress = on_progress

    def get_video_duration(self, video):
        return float(execut_ffprobe([
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video)
        ]).strip())

    def merge_videos(self, width, height):
        size_videos = 0
        vid_len = len(self.videos)

        if self.progress_interval <= 0:
            raise ValueError(
                "progress_interval must be greater than 0"
            )

        if not self.videos or vid_len == 1:
            raise ValueError(
                "videos cannot be empty or len(videos) == 1"
            )
        cmd = [item for video in self.videos for item in ["-i", str(video)]]
        for video in self.videos:
            size_videos += self.get_video_duration(video)

        video_filters = build_filters(
            vid_len,
            f"[$i:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1[v$i]"
        )

        audio_filters = build_filters(
            vid_len,
            "[$i:a]aresample=48000[a$i]"
        )

        concat_inputs = "".join(
            build_filters(vid_len, "[v$i][a$i]")
        )

        concat_filter = (
            f"concat=n={vid_len}:v=1:a=1[v][a]"
        )

        filter_complex = (
            ";".join(video_filters + audio_filters)
            + ";"
            + concat_inputs
            + concat_filter
        )

        cmd += [
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "[a]",
        ]

        execut_ffmpeg(
            cmd,
            self.progress_interval,
            size_videos,
            self.overwrite,
            self.output,
            self.on_progress
        )