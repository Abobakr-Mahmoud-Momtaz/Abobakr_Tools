# Abobakr Tools

**Abobakr Tools** is a Python library that provides reusable programming utilities designed to simplify common tasks and reduce development effort.

## Features

The library provides two main modules:

### 1. Core (`core.py`)

A collection of general-purpose programming utilities.

#### String & List Manipulation

| Function | Description |
|---|---|
| `remove_all_occurrences(items, item)` | Returns a new list with all occurrences of the specified item removed. |
| `contains_digit(text)` | Checks whether a string contains at least one digit. Returns `True` or `False`. |
| `is_number(text, type_number)` | Checks whether a string represents an integer or a decimal number. `type_number` accepts `"int"` or `"float"`. |
| `insert_text_after_in_file(file_path, insert_text, target_text)` | Reads a file and returns its contents with the specified text inserted after matching occurrences of the target text. It does not modify the original file. |
| `text_replace(text, index, replacement_text, placeholder_text)` | Replaces a section of a string, starting at the specified index, with replacement text. The removed section has the same length as `placeholder_text`. |

#### Input Helpers

| Function | Description |
|---|---|
| `read_integer(message)` | Prompts the user until a valid integer is entered. Returns an `int`. |
| `read_float(message)` | Prompts the user until a valid floating-point number is entered. Returns a `float`. |
| `read_non_numeric_string(message)` | Prompts the user until a non-empty string that is not composed entirely of digits is entered. |

#### Random Number Generation

| Function | Description |
|---|---|
| `get_pseudo_random_int(start, stop)` | Generates a pseudo-random integer within the inclusive range from `start` to `stop`. |

This function uses a custom digit pool to generate its values. It is not intended for cryptographic or security-sensitive applications.

#### SOC Analyst

| Function | Description |
|---|---|
| `analyze_events(events_file_path)` | Monitors and analyzes security events stored in a JSON file, tracking user activity and login attempts over time. Results are recorded using Python's logging system. |

The event records are expected to contain:

- `username`: The username associated with the event.
- `event_type`: The type of event.
- `timestamp`: A timestamp in the format `%Y-%m-%dT%H:%M:%S.%f%z`.

The analyzer groups events into five-second time windows and classifies user activity based on the number of occurrences of the following event types:

- `authentication_success`
- `invalid_login`

Other event types are excluded from severity classification but remain included in the activity logs.

The severity levels are:

- **INFO:** No user has 2 or more matching events.
- **WARNING:** At least one user has 2–4 matching events.
- **CRITICAL:** At least one user has 5 or more matching events.

The log file is created as `soc_analyst.log` in the same directory as the events JSON file.

### 2. Video Processor (`video_processor.py`)

Provides video-processing utilities using FFmpeg.

#### VideoEditor Class

The `VideoEditor` class provides video-processing operations.

**Constructor:**

```python
VideoEditor(
    videos,
    output,
    overwrite=1,
    progress_interval=1,
    on_progress=None
)
```

| Parameter | Description |
|---|---|
| `videos` | An iterable containing the paths of the input video files. |
| `output` | The output video file path. |
| `overwrite` | Determines whether an existing output file can be overwritten. Defaults to `1` (enabled). |
| `progress_interval` | The interval, in seconds, between FFmpeg progress updates. Must be greater than zero. |
| `on_progress` | An optional callback function that receives the processing progress as a percentage. |

**Methods:**

| Method | Description |
|---|---|
| `get_video_duration(video)` | Returns the duration of a video in seconds. |
| `merge_videos(width, height)` | Merges the input videos into one output video using the specified width and height. |

**Example:**

```python
import abt

editor = abt.VideoEditor(
    videos=["video1.mp4", "video2.mp4"],
    output="merged.mp4",
    overwrite=1,
    progress_interval=1,
    on_progress=lambda percentage: print(f"{percentage:.2f}%")
)

editor.merge_videos(width=1920, height=1080)
```

#### FFmpeg Installation

FFmpeg is downloaded and configured automatically when a `VideoEditor` instance is created.

**Installation behavior:**

- FFmpeg is downloaded automatically if its required executable files are missing.
- The download is performed from an external GitHub release.
- The downloaded ZIP archive is extracted automatically.
- The FFmpeg files are stored inside the library directory.
- Existing FFmpeg files are reused when all required executables are available.
- If any required executable is missing, FFmpeg is downloaded and installed again.

**Required executables:**

- `ffmpeg.exe`
- `ffprobe.exe`
- `ffplay.exe`

**FFmpeg Version:** 7.0 Full Build

**Download URL:**

https://github.com/GyanD/codexffmpeg/releases/download/7.0/ffmpeg-7.0-full_build.zip

**Requirements:**

- An active internet connection for the initial download or reinstallation.
- Write permission in the library directory.
- Windows operating system.

FFmpeg is executed as an independent external process using Python's `subprocess` module.

### Third-Party Licenses

Abobakr Tools uses **FFmpeg**, an external multimedia framework developed by the FFmpeg project.

The version used by this library is FFmpeg 7.0 Full Build, obtained from GyanD's GitHub releases.

The downloaded FFmpeg build reports that it is distributed under the **GNU General Public License v3.0 or later (GPL-3.0-or-later)**.

**FFmpeg Information:**

| Item | Details |
|---|---|
| Project | FFmpeg |
| Version | 7.0 Full Build |
| Distributor | GyanD |
| License | GPL-3.0-or-later |
| Download | [FFmpeg 7.0 Full Build](https://github.com/GyanD/codexffmpeg/releases/download/7.0/ffmpeg-7.0-full_build.zip) |
| Official Website | https://ffmpeg.org/ |
| Upstream Source Code | https://github.com/FFmpeg/FFmpeg/tree/n7.0 |
| License Text | https://www.gnu.org/licenses/gpl-3.0.html |

**Important Notes:**

- FFmpeg is a third-party project and is not developed by the author of Abobakr Tools.
- FFmpeg is not modified by Abobakr Tools.
- FFmpeg is executed as an independent external process.
- FFmpeg and its included third-party components remain subject to their respective licenses.
- The GPL license and applicable source-code distribution requirements must be respected when redistributing FFmpeg.

For additional information about FFmpeg licensing:

https://ffmpeg.org/legal.html

## Requirements

- Python 3.8 or newer.
- Windows for the current `VideoEditor` implementation.
- An internet connection for the initial FFmpeg download.

## Installation

```bash
python -m pip install abobakr-tools
```

## Importing

```python
import abt
```

All the documented public functions and the `VideoEditor` class can be accessed through the `abt` package.

## Support Abobakr Tools

Thank you for using **Abobakr Tools**!

I created this library to make development tasks easier and more accessible. I am continuously working hard to maintain, improve, and expand it.

If Abobakr Tools has helped you earn money through freelance work, professional services, or commercial projects, I encourage you to consider supporting the project with a voluntary contribution of any amount.

Your support helps me dedicate more time and effort to maintaining the library, fixing bugs, adding new features, and making it even more useful for developers.

Every contribution, no matter how small, is greatly appreciated. Whether you choose to contribute or simply use the library, thank you for being part of this project!

☕ **Support the Project:**

[Support Abobakr Tools](https://abobakrmahmoad.gumroad.com/coffee)

## Contributing

Suggestions, bug reports, and contributions are welcome.

Feel free to open an issue or submit a pull request to help improve the project.