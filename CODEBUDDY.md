# CODEBUDDY.md This file provides guidance to CodeBuddy when working with code in this repository.

## Common Commands

**Run the application:**
```bash
python main.py
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Migrate old config to new unified format:**
```bash
python scripts/migrate_config.py
```

**Run hardware acceleration detection (standalone test):**
```bash
python -m utils.hardware_detector
```

There are no automated tests, linting, or build steps in this project. Testing is done manually by launching the GUI and generating videos.

## Architecture Overview

Lrc2Video is a Python desktop application that synthesizes lyric videos from audio + LRC file pairs. It uses **Tkinter** for the GUI and **FFmpeg** (invoked via subprocess) as the video encoding engine. The application supports single-file and batch processing, AI-powered title generation, and hardware-accelerated encoding.

### Entry Point and Startup (`main.py`)

The `main.py` file:

1. Configures dual logging: console (INFO+) and file-based (DEBUG, written to `logs/` with timestamped filenames).
2. Prints system diagnostics: working directory, Python version, and key dependency availability (tkinter, openai, pysubs2).
3. Ensures required directories exist (`config/`, `output/`, `logs/`, `style_templates/`).
4. Creates the Tkinter root window, attempts to load an icon (`icon.ico` or `icon.png`), instantiates the `LyricsVideoGenerator` main window class from `gui.main_window`, and enters the Tkinter main loop.

### GUI Layer (`gui/`)

**`gui/main_window.py` — `LyricsVideoGenerator` class:**
The main window organizes the UI into three tabs via a `ttk.Notebook`:

- **File Selection tab (`setup_file_page`)**: Single-file mode (audio, LRC, background image pickers) and batch mode (folder picker + scan button that populates a Treeview with matched audio-LRC pairs). Output directory selection.
- **Style Settings tab (`setup_style_page`)**: Full subtitle styling controls organized in grid — font family (auto-detected from system via matplotlib), size, color; outline width/color; margin bottom; fade in/out timing; background color; video resolution; concurrency slider. Includes export/import of style configurations as JSON files.
- **Batch Processing tab (`setup_batch_page`)**: Generate single/batch buttons, stop button, dual progress bars (current file + total), status label, and a ScrolledText log view.

The class manages `Tkinter.StringVar`, `IntVar`, and `BooleanVar` objects that bind style parameters to UI controls. It also holds the `VideoGenerator` instance, file pair list, and user preferences loaded from `config/config.json` via the `ConfigManager`.

**`gui/ai_config_dialog.py` — `AIConfigDialog` class:**
A `Toplevel` dialog for configuring AI providers. Only Moonshot (Kimi) is currently supported. It allows setting the API key, base URL, model name, timeout, and retry count. Includes a "Test Connection" button that fires a threaded request to validate credentials.

**`gui/modern_theme.py`:**
Defines shared constants: `COLORS` dict (blue/white Material Design palette), `FONTS` dict (Segoe UI-based), `BUTTON_STYLES`, `ENTRY_STYLES`, `LABEL_STYLES`, `FRAME_STYLES`, `SCALE_STYLES`. Provides factory functions: `create_modern_button()`, `create_modern_entry()`, `create_modern_label()`, `create_modern_frame()`.

### Core Engine (`core/`)

**`core/video_generator.py` — `VideoGenerator` class:**
This is the heart of the application. The key method is `generate_video(audio_path, lrc_path, config, bg_image_path, output_path, use_ai_title)`:

1. **LRC Parsing**: Attempts `pysubs2.load()` with UTF-8 encoding. Falls back to `utils.file_utils.parse_lrc_manually()` which tries multiple encodings (UTF-8 → GBK → GB2312 → Latin-1 → CP1252).
2. **AI Title Generation**: If enabled, calls `generate_video_title()` from `utils.ai_title_generator` to produce a Chinese title (15-25 chars). Falls back to a formatted default.
3. **Subtitle Styling**: Calls `apply_subtitle_style()` which converts hex colors to ASS BGR format (via `hex_to_ass_color()`), sets font/size/alignment/margins/outline on the `pysubs2.SSAStyle`, and prepends `{\an2\fad(...)}` override tags to each subtitle event for bottom-center alignment and fade effects.
4. **Subtitle Output**: Saves styled subtitles as a temporary `.ass` file in `temp/` directory.
5. **Background Handling**: Extracts embedded cover art from audio via `ffmpeg` if no background image is provided. Otherwise uses a solid color background.
6. **FFmpeg Command Construction** (`build_ffmpeg_command`): Builds the ffmpeg command differently based on whether a background image exists:
   - **With image**: Uses `-loop 1` on the image, scales/crops to target resolution, applies subtitles via the `subtitles` filter, copies audio stream.
   - **Without image**: Creates a solid color canvas via `-f lavfi -i color=c=...`, applies subtitles.
   - **Encoder selection**: Checks `hwaccel` config to choose `h264_nvenc` (NVIDIA), `h264_qsv` (Intel), `h264_amf` (AMD), `h264_videotoolbox` (macOS), or `libx264` (software). Adjusts preset names accordingly since hardware encoders use different preset values.
7. **Progress Monitoring**: Parses FFmpeg's stderr output line-by-line in a loop, extracting `time=HH:MM:SS.ms` via regex to calculate percentage progress.
8. **Cleanup**: Deletes temporary `.ass` and cover image files on completion.

The class supports graceful cancellation: `set_stop_flag()` terminates the running FFmpeg subprocess. The `__del__` destructor ensures cleanup.

### Utilities (`utils/`)

**`utils/file_utils.py`:**
- `parse_lrc_manually(lrc_path)`: Fallback LRC parser that tries multiple encodings, extracts timestamps with regex `\[mm:ss.xx\]`, and creates `pysubs2.SSAEvent` objects. Each line gets a 3-second default duration, with end times cascaded from the next line's start time.
- `extract_cover_image(audio_path, cover_path)`: Runs `ffmpeg -an -vcodec copy` to extract embedded album art.
- `get_audio_duration(audio_path)`: Uses `ffprobe` to get audio duration in seconds. Defaults to 300s if the probe fails.
- `scan_folder_for_files(folder_path)`: Recursively finds audio files (mp3, flac, wav, m4a, aac) and matches them with `.lrc` files by stem name. Returns `(file_pairs, missing_files)`.

**`utils/config_manager.py` — `ConfigManager` class:**
A singleton configuration manager (accessed via `get_config()`) that reads/writes `config/config.json`. Supports dot-path access like `config.get('ai.enabled')` and `config.set('video.resolution', '1920x1080')`. Provides convenience accessors: `get_ai_config(provider)`, `get_video_config()`, `get_lyrics_config()`. If no config file exists, falls back to copying from `config.json.example` or generating a hardcoded default.

**`utils/ai_title_generator.py` — `AITitleGenerator` class:**
Uses the `openai` Python library to communicate with OpenAI-compatible APIs (currently configured for Moonshot Kimi). The `generate_title()` method builds a detailed Chinese prompt that instructs the model to act as a "professional music video title planner" and produce a 15-25 character viral-style Chinese title. Includes an `_analyze_music_style()` method with a hardcoded artist style database and keyword-based style inference. The module exposes a top-level `generate_video_title(song_name, artist, use_ai)` function that `VideoGenerator` calls directly. Retry logic: up to 2 attempts with 1-second delays.

**`utils/hardware_detector.py`:**
Detects available FFmpeg hardware encoders by parsing `ffmpeg -encoders` output. Also retrieves GPU info via platform-specific commands: `wmic` on Windows, `lspci` on Linux, `system_profiler` on macOS. `get_recommended_settings()` returns the best available hardware acceleration type.

### Scripts (`scripts/`)

**`scripts/migrate_config.py`:**
One-shot migration script for upgrading from the old multi-file config layout (`user_preferences.json`, `ai_config.json`) to the new unified `config/config.json`. It deep-merges old settings into the `config.json.example` template and backs up old files.

### Style Templates (`style_templates/`, `style.json`)

Style configurations are JSON files specifying font, color, outline, position, and effect parameters. `style.json` at the project root is the default user style. The `style_templates/` directory contains `default_style.json` (classic look) and `modern_style.json` (green-on-dark theme with wider strokes). These can be imported/exported via the GUI's Style Management section.

### Data Flow (Single File Generation)

```
User selects audio + LRC (+ optional background)
       ↓
LyricsVideoGenerator.get_config() → config dict
       ↓
LyricsVideoGenerator.generate_single_video()
       ↓ spawns thread
VideoGenerator.generate_video(audio, lrc, config, bg, output)
       ↓
1. parse LRC (pysubs2 → fallback manual parser)
2. optionally generate AI title → sanitize filename
3. apply_subtitle_style() → save .ass temp file
4. extract_cover_image() if no bg provided
5. build_ffmpeg_command() → subprocess.Popen
6. monitor FFmpeg stderr for progress
7. cleanup temp files
       ↓
Output .mp4 in output/ directory
```

### Batch Processing Data Flow

```
User selects folder → scan_folder_for_files()
       ↓ populates self.file_pairs
User clicks "Batch Generate"
       ↓ spawns thread
ThreadPoolExecutor(max_workers=N) dispatches process_single_file()
for each (audio, lrc) pair, each creating its own VideoGenerator instance
       ↓
Results collected via as_completed(), progress updated via root.after()
```

### Key Dependencies

- **pysubs2**: LRC parsing and ASS subtitle format manipulation
- **openai**: AI title generation client library (talks to Moonshot API)
- **FFmpeg/FFprobe**: External binaries required in system PATH for video encoding, cover extraction, and audio analysis
- **tkinter**: Python's bundled GUI toolkit
- **matplotlib** (optional): Used only for system font detection via `font_manager.findSystemFonts()`

### Threading Model

The GUI is single-threaded (Tkinter main loop). Video generation runs in background threads:
- Single file: One `threading.Thread` per generation.
- Batch: A `ThreadPoolExecutor` with configurable max workers (1–8). Each worker creates its own `VideoGenerator` instance. GUI updates are dispatched to the main thread via `root.after(0, callback)`.
- AI config test connection: Runs in a separate short-lived thread.

### Configuration File (`config/config.json`)

Created automatically on first run. Structured with sections: `app`, `ai`, `video`, `lyrics`, `paths`. The `ai.providers` dict maps provider names to their API credentials. Sensitive data (API keys) is stored in this file, which is excluded from version control via `.gitignore`.
