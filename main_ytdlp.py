# main_ytdlp.py - Alternative version using yt-dlp
import os
import sys
import re
import yt_dlp

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
    Downloads the audio from a YouTube video using yt-dlp.

    Args:
        video_url (str): The URL of the YouTube video.
        output_path (str): The directory where the audio file will be saved.
                           Defaults to the current directory.
    """
    try:
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',  # Download best audio quality
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),  # Output filename template
            'extractaudio': True,  # Extract audio
            'audioformat': 'm4a',  # Convert to m4a format
            'audioquality': 0,  # Best audio quality
            'noplaylist': True,  # Don't download playlists
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info first
            print(f"Connecting to YouTube with URL: {video_url}")
            info = ydl.extract_info(video_url, download=False)
            
            # Display video details
            print("\n" + "="*40)
            print(f"Title: {info.get('title', 'Unknown')}")
            print(f"Uploader: {info.get('uploader', 'Unknown')}")
            duration = info.get('duration', 0)
            if duration:
                print(f"Duration: {duration // 60}:{duration % 60:02d} minutes")
            print(f"Views: {info.get('view_count', 'Unknown'):,}" if info.get('view_count') else "Views: Unknown")
            print("="*40 + "\n")

            # Check if file already exists
            expected_filename = ydl.prepare_filename(info)
            base_name = os.path.splitext(expected_filename)[0]
            final_filename = base_name + '.m4a'
            
            if os.path.exists(final_filename):
                print(f"File '{os.path.basename(final_filename)}' already exists.")
                response = input("Do you want to overwrite it? (y/N): ").strip().lower()
                if response not in ['y', 'yes']:
                    print("Download cancelled. File not overwritten.")
                    return
                os.remove(final_filename)

            # Download the audio
            print(f"Downloading '{info.get('title', 'Unknown')}'...")
            ydl.download([video_url])
            print("Download completed successfully!")
            
            # Find the downloaded file and rename if necessary
            for file in os.listdir(output_path):
                if file.startswith(os.path.splitext(os.path.basename(expected_filename))[0]):
                    downloaded_file = os.path.join(output_path, file)
                    if not file.endswith('.m4a'):
                        new_file_path = os.path.splitext(downloaded_file)[0] + '.m4a'
                        os.rename(downloaded_file, new_file_path)
                        downloaded_file = new_file_path
                    
                    print(f"File successfully saved as: {os.path.basename(downloaded_file)}")
                    print(f"File location: {os.path.abspath(downloaded_file)}")
                    break

    except yt_dlp.DownloadError as e:
        error_msg = str(e).lower()
        if "video unavailable" in error_msg or "private video" in error_msg:
            print(f"Error: The video is unavailable. It may be private, deleted, or region-restricted.")
        elif "age-restricted" in error_msg:
            print(f"Error: This video is age-restricted and cannot be downloaded.")
        elif "live" in error_msg:
            print(f"Error: Live streams cannot be downloaded.")
        else:
            print(f"Download error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

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
