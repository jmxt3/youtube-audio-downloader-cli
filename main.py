# main.py
import os
import sys
import re
try:
    from pytubefix import YouTube
    from pytubefix.exceptions import RegexMatchError
except ImportError:
    from pytube import YouTube
    from pytube.exceptions import RegexMatchError

def is_valid_youtube_url(url):
    """
    Validates if the provided URL is a valid YouTube URL.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL is a valid YouTube URL, False otherwise.
    """
    youtube_patterns = [
        r'^https?://(www\.)?youtube\.com/watch\?v=[\w-]+',
        r'^https?://(www\.)?youtube\.com/embed/[\w-]+',
        r'^https?://youtu\.be/[\w-]+',
        r'^https?://(www\.)?youtube\.com/v/[\w-]+',
        r'^https?://(www\.)?youtube\.com/watch\?.*v=[\w-]+',
    ]

    return any(re.match(pattern, url) for pattern in youtube_patterns)

def validate_save_path(path):
    """
    Validates if the save path is accessible and writable.

    Args:
        path (str): The path to validate.

    Returns:
        bool: True if the path is valid and writable, False otherwise.
    """
    try:
        # Check if path exists and is a directory
        if os.path.exists(path) and not os.path.isdir(path):
            print(f"Error: '{path}' exists but is not a directory.")
            return False

        # Check if we can write to the directory (or its parent if it doesn't exist)
        test_path = path if os.path.exists(path) else os.path.dirname(os.path.abspath(path))
        if not os.access(test_path, os.W_OK):
            print(f"Error: No write permission for directory '{test_path}'.")
            return False

        return True
    except Exception as e:
        print(f"Error validating save path: {e}")
        return False

def download_youtube_audio(video_url, output_path='.'):
    """
    Downloads the audio from a YouTube video.

    Args:
        video_url (str): The URL of the YouTube video.
        output_path (str): The directory where the audio file will be saved.
                           Defaults to the current directory.
    """
    try:
        # Create a YouTube object
        print(f"Connecting to YouTube with URL: {video_url}")
        yt = YouTube(video_url)

        # --- Display video details ---
        print("\n" + "="*40)
        print(f"Title: {yt.title}")
        print(f"Author: {yt.author}")
        print(f"Duration: {yt.length // 60}:{yt.length % 60:02d} minutes")
        print(f"Views: {yt.views:,}")
        print("="*40 + "\n")

        # --- Filter for audio-only streams ---
        # Get the best audio stream available (highest bitrate)
        print("Searching for the best audio stream...")
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()

        if not audio_stream:
            print("No audio-only streams found for this video.")
            return

        print(f"Found audio stream with bitrate: {audio_stream.abr}")

        # --- Download the audio stream ---
        print(f"Downloading '{yt.title}'...")
        # Pytube downloads the file with the video title as the filename.
        # We'll get the downloaded file path to rename it later.
        downloaded_file_path = audio_stream.download(output_path=output_path)
        print("Download completed successfully!")

        # --- Rename the file to have an .m4a extension ---
        # The file downloaded is an audio file (AAC audio in MP4 container)
        # Using .m4a extension to accurately represent the audio format.
        if not isinstance(downloaded_file_path, str):
            print("Error: Downloaded file path is not a valid string.")
            return

        base, _ = os.path.splitext(downloaded_file_path)
        new_file_path = base + '.m4a'

        # Check if the new file already exists (and is different from downloaded file)
        if os.path.exists(new_file_path) and new_file_path != downloaded_file_path:
            print(f"File '{os.path.basename(new_file_path)}' already exists.")
            response = input("Do you want to overwrite it? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("Download cancelled. File not overwritten.")
                return
            os.remove(new_file_path)

        # Only rename if the file doesn't already have the correct extension
        if downloaded_file_path != new_file_path:
            if downloaded_file_path:
                os.rename(downloaded_file_path, new_file_path)
            else:
                print("Error: Downloaded file path is None. Cannot rename the file.")
                return
        else:
            # File already has the correct extension
            new_file_path = downloaded_file_path
        print(f"File successfully saved as: {os.path.basename(new_file_path)}")
        print(f"File location: {os.path.abspath(new_file_path)}")

    except RegexMatchError:
        print(f"Error: Invalid YouTube URL: '{video_url}'")
        print("Please provide a valid YouTube video URL.")
    except Exception as e:
        error_msg = str(e).lower()
        if "video unavailable" in error_msg:
            print(f"Error: The video is unavailable. It may be private, deleted, or region-restricted.")
        elif "age-restricted" in error_msg:
            print(f"Error: This video is age-restricted and cannot be downloaded.")
        elif "live stream" in error_msg:
            print(f"Error: Live streams cannot be downloaded.")
        elif "network" in error_msg or "connection" in error_msg:
            print(f"Error: Network connection issue. Please check your internet connection and try again.")
        else:
            print(f"An error occurred: {e}")
            print("This could be due to a network issue or a change in the YouTube platform.")
            print("Try updating pytube with: pip install --upgrade pytube")
    except PermissionError:
        print(f"Error: Permission denied when trying to save the file.")
        print("Please check your permissions for the output directory.")
    except OSError as e:
        print(f"Error: File system error: {e}")
        print("This could be due to insufficient disk space or invalid file names.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print("Please try again or report this issue if it persists.")

if __name__ == "__main__":
    # --- Check for command-line arguments ---
    if len(sys.argv) > 1:
        youtube_url = sys.argv[1]
        # The second argument is an optional save path
        save_path = sys.argv[2] if len(sys.argv) > 2 else '.'
    else:
        # --- Fallback to user input if no arguments are provided ---
        print("No command-line arguments found. Asking for user input.")
        youtube_url = input("Enter the YouTube video URL: ")
        save_path = input("Enter the save path (press Enter for current directory): ")
        if not save_path:
            save_path = '.'

    # --- Validate YouTube URL ---
    if not is_valid_youtube_url(youtube_url):
        print(f"Error: Invalid YouTube URL: '{youtube_url}'")
        print("Please provide a valid YouTube video URL.")
        print("Supported formats:")
        print("  - https://www.youtube.com/watch?v=VIDEO_ID")
        print("  - https://youtu.be/VIDEO_ID")
        print("  - https://www.youtube.com/embed/VIDEO_ID")
        sys.exit(1)

    # --- Validate save path ---
    if not validate_save_path(save_path):
        sys.exit(1)

    # --- Create directory if it doesn't exist ---
    if not os.path.isdir(save_path):
        print(f"Creating directory: {save_path}")
        try:
            os.makedirs(save_path)
        except PermissionError:
            print(f"Error: Permission denied. Cannot create directory '{save_path}'.")
            print("Please check your permissions or choose a different directory.")
            sys.exit(1)
        except OSError as e:
            print(f"Error: Cannot create directory '{save_path}': {e}")
            sys.exit(1)

    # --- Run the downloader ---
    download_youtube_audio(youtube_url, save_path)
