import os
import subprocess
import cv2
import time
import mass_video_maker
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

def convert_to_short(input_path, output_path):
    """Converts the video to a vertical short (1080x1920) using FFmpeg with GPU acceleration (NVENC)."""
    try:
        # Get video resolution using OpenCV
        cap = cv2.VideoCapture(input_path)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        cap.release()

        # Check if the video is in 16:9 aspect ratio
        if width / height != 16 / 9:
            print(f"Warning: The video is not in 16:9 aspect ratio. It is {width}:{height}.")

        # Calculate the crop dimensions for a 9:16 aspect ratio (vertical)
        crop_w = int(height * 9 / 16)  # Set the crop width to maintain 9:16 aspect ratio
        crop_x = int((width - crop_w) / 2)  # Center crop horizontally
        
        # Construct FFmpeg command
        command = [
            'ffmpeg',
            '-i', input_path,  # Input file
            '-vf', f'crop={crop_w}:{height}:{crop_x}:0,scale=1080:1920',  # Crop to 9:16 and scale to 1080x1920
            '-preset', 'fast',  # Quick encoding
            '-c:v', 'h264_nvenc',  # Use NVIDIA GPU for H.264 encoding (NVENC)
            '-b:v', '5M',  # Set the video bitrate (optional)
            output_path  # Output file
        ]
        
        # Run the FFmpeg command and capture errors
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ FFmpeg error for {input_path}: {result.stderr}")
            return False
        else:
            print(f"✅ Created short: {output_path}")
            return True
    except Exception as e:
        print(f"❌ Error processing {input_path}: {str(e)}")
        return False

def process_video(args):
    """Process a single video file"""
    input_path, drive_shorts_path, posted_shorts_path = args
    
    # Check if the file already exists in either location
    if os.path.exists(drive_shorts_path) or os.path.exists(posted_shorts_path):
        print(f"⚠️ Short for {os.path.basename(input_path)} already exists in Google Drive. Skipping.")
        return True
    
    # If the short doesn't exist in either location, create it
    print(f"🎬 Converting {os.path.basename(input_path)} to a short...")
    return convert_to_short(input_path, drive_shorts_path)

def process_videos(video_paths):
    """Processes specific videos to create Shorts using parallel processing."""
    
    if not video_paths:
        print("No videos to process.")
        return False

    # Prepare arguments for parallel processing
    process_args = []
    videos_to_create = []
    for input_path in video_paths:
        # Get the base filename without extension
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        # Create the short filename with the new naming scheme
        short_name = f"{base_name}_short.mp4"
        
        drive_shorts_path = os.path.join("G:\\My Drive\\Prestiged\\Shorts", short_name)
        posted_shorts_path = os.path.join("G:\\My Drive\\Prestiged\\Posted Shorts", short_name)
        
        # Only add to process_args if the short doesn't exist
        if not (os.path.exists(drive_shorts_path) or os.path.exists(posted_shorts_path)):
            process_args.append((input_path, drive_shorts_path, posted_shorts_path))
            videos_to_create.append(short_name)

    if not videos_to_create:
        print("All shorts already exist. Nothing to process.")
        return True

    # Show confirmation with number of videos to be created
    print(f"\n📊 Summary of shorts to be created:")
    print(f"Total videos to process: {len(videos_to_create)}")
    print("\nVideos to be created:")
    for video in videos_to_create:
        print(f"- {video}")
    
    # Get user confirmation
    confirm = input("\nWould you like to proceed with creating these shorts? (y/n) ").strip().lower()
    if confirm != 'y':
        print("❌ Operation cancelled by user")
        return False

    # Determine number of processes to use (leave one CPU core free)
    num_processes = max(1, multiprocessing.cpu_count() - 1)
    print(f"\nUsing {num_processes} processes for parallel short creation")

    # Process videos in parallel
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        results = list(executor.map(process_video, process_args))

    # Count successful and failed conversions
    successful = results.count(True)
    failed = results.count(False)
    print(f"\nShort creation completed:")
    print(f"✅ Successfully created: {successful}")
    print(f"❌ Failed: {failed}")

    return successful > 0

def create_shorts():
    """Create videos and then convert them to shorts"""
    # Get list of newly created videos
    new_videos = mass_video_maker.create_videos()
    
    if new_videos:
        print("\nStarting short conversion process...")
        process_videos(new_videos)
        print("✅ Shorts creation process completed")
    else:
        print("❌ No videos were created, skipping short conversion")

if __name__ == "__main__":
    create_shorts_command = input("Would you like to create shorts? (y/n) ").strip().lower()

    if create_shorts_command == "y":
        create_shorts()
    else:
        print("❌ No videos will be created or processed")
