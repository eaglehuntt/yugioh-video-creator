import subprocess
import sys
import os

def convert_to_short(input_path, output_path):
    """Converts the video to a vertical short (1080x1920) using FFmpeg."""
    try:
        # Construct FFmpeg command
        # This will crop the center portion to 9:16 ratio and scale to 1080x1920
        command = [
            r'C:\Program Files\ffmpeg-2025-03-13-git-958c46800e-full_build\bin\ffmpeg.exe',
            '-i', input_path,
            '-vf', 'crop=ih*9/16:ih,scale=1080:1920',  # Crop width to match 9:16 ratio of height
            '-preset', 'fast',
            '-c:v', 'h264_nvenc',
            '-b:v', '5M',
            '-y',
            output_path
        ]
        
        print("Running FFmpeg command:")
        print(" ".join(command))
        
        # Run the FFmpeg command and capture errors
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ FFmpeg error: {result.stderr}")
            return False
        else:
            print(f"✅ Created short: {output_path}")
            return True
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python crop_to_short.py <input_video_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    input_dir = os.path.dirname(input_path)
    input_filename = os.path.basename(input_path)
    name, ext = os.path.splitext(input_filename)
    output_path = os.path.join(input_dir, f"{name}_short{ext}")
    
    print(f"Input file: {input_path}")
    print(f"Output will be saved as: {output_path}")
    
    convert_to_short(input_path, output_path)
    