# YouTube Audio Downloader

A Python tool to download audio from YouTube videos with robust error handling and user-friendly features.

## Features

- Download high-quality audio from YouTube videos
- Automatic conversion to M4A format
- URL validation for YouTube links
- File overwrite confirmation
- Comprehensive error handling
- Support for multiple YouTube URL formats

## Installation

### 1. Install UV (Python Package Manager)

**Windows:**
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone/Download the Project

```bash
git clone <repository-url>
cd audio_downloader
```

### 3. Install Dependencies

```bash
uv pip install yt-dlp
```

## Usage

### Command Line with URL

```bash
uv run main.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Command Line with Custom Directory

```bash
uv run main.py "https://www.youtube.com/watch?v=VIDEO_ID" "C:\Downloads\Music"
```

### Interactive Mode

```bash
uv run main.py
```
Then enter the YouTube URL and save path when prompted.

## Supported URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/v/VIDEO_ID`

## CLI Examples

**Download to current directory:**
```bash
uv run main.py "https://youtu.be/dQw4w9WgXcQ"
```

**Download to specific folder:**
```bash
uv run main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" "C:\Music"
```

**Interactive mode:**
```bash
uv run main.py
# Enter URL: https://youtu.be/dQw4w9WgXcQ
# Enter path: C:\Music (or press Enter for current directory)
```

## Output

- Audio files are saved in M4A format
- Original video title is used as filename
- File location is displayed after successful download
- Confirmation required before overwriting existing files

## Error Handling

The tool handles various scenarios:
- Invalid YouTube URLs
- Network connection issues
- Permission errors
- Age-restricted content
- Private/deleted videos
- Insufficient disk space

## Requirements

- Python 3.7+
- UV package manager
- Internet connection
- Write permissions to output directory