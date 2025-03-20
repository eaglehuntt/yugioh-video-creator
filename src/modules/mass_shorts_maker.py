import os
import subprocess
import cv2
import time
import mass_video_maker

def convert_to_short(input_path, output_path):
    """Converts the video to a vertical short (1080x1920) using FFmpeg with GPU acceleration (NVENC)."""
    
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
        print(f"❌ FFmpeg error: {result.stderr}")
    else:
        print(f"✅ Created short: {output_path}")

def process_videos():
    """Processes all videos in the input folder to create Shorts."""
    
    video_folder = os.path.join('src', 'videos')
    # Ensure the local shorts folder exists (even though final output is in Google Drive)
    local_shorts_folder = os.path.join('src', 'shorts')
    os.makedirs(local_shorts_folder, exist_ok=True)

    for filename in os.listdir(video_folder):
        if filename.lower().endswith(".mp4"):
            input_path = os.path.join(video_folder, filename)

            # Define the two Google Drive paths to check for an existing short.
            drive_shorts_path = os.path.join("G:\\My Drive\\Prestiged\\Shorts", filename)
            posted_shorts_path = os.path.join("G:\\My Drive\\Prestiged\\Posted Shorts", filename)

            # Check if the file already exists in either location.
            if os.path.exists(drive_shorts_path) or os.path.exists(posted_shorts_path):
                print(f"⚠️ Short for {filename} already exists in Google Drive. Skipping.")
                continue
            
            # If the short doesn't exist in either location, create it.
            print(f"🎬 Converting {filename} to a short...")
            convert_to_short(input_path, drive_shorts_path)

            # Delay to account for potential Google Drive sync issues.
            time.sleep(2)

def create_shorts():
    mass_video_maker.create_videos()

if __name__ == "__main__":
    create_shorts_command = input("Would you like to create shorts? (y/n) ").strip().lower()

    if create_shorts_command == "y":
        create_shorts()
        process_videos()
        print("✅ Shorts created")
    else:
        just_process = input("Would you like to just process videos? (y/n) ").strip().lower()
        if just_process == "y":
            process_videos()
            print("✅ Videos processed")
