# Yu-Gi-Oh Video Creator

An automated video creation tool that generates engaging YouTube Shorts about Yu-Gi-Oh! cards. The tool uses AI to create scripts, text-to-speech for narration, and video editing to produce professional-looking card showcase videos.

## Features

- **AI-Powered Scripts**: Uses ChatGPT to generate engaging card descriptions
- **Text-to-Speech**: ElevenLabs integration for high-quality voice narration
- **Video Generation**: Creates videos with card animations and background music
- **Batch Processing**: Mass video creation from Yu-Gi-Oh database URLs
- **Short Conversion**: Automatically converts videos to vertical format for YouTube Shorts
- **Parallel Processing**: Multi-core processing for faster video creation

## Project Structure

```
yugioh-video-creator/
├── src/
│   ├── modules/
│   │   ├── yugioh_video_maker.py    # Main video creation class
│   │   ├── mass_video_maker.py      # Batch video processing
│   │   ├── mass_shorts_maker.py     # Short conversion utility
│   │   └── chatts.py                # Alternative TTS implementation
│   ├── utils/
│   │   └── crop_to_short.py         # Video cropping utility
│   ├── assets/
│   │   ├── background.mp4           # Background video
│   │   ├── background_large.mp4     # High-res background
│   │   ├── breaker_test.jpg         # Test image
│   │   ├── music/                   # Background music tracks
│   │   │   ├── 1.mp3
│   │   │   ├── 2.mp3
│   │   │   ├── 3.mp3
│   │   │   ├── 4.mp3
│   │   │   └── 5.mp3
│   │   └── sfx/
│   │       └── sfx.mp3              # Sound effects
│   ├── videos/                      # Generated videos (created automatically)
│   ├── audio/                       # Generated audio files (created automatically)
│   └── shorts/                      # Generated shorts (created automatically)
├── venv/                            # Python virtual environment
└── README.md
```

## Prerequisites

### System Requirements

- **Python 3.8+**
- **FFmpeg** (for video processing)
- **NVIDIA GPU** (recommended for faster video encoding)
- **Windows 10/11** (tested on Windows)

### External Dependencies

- **OpenAI API Key** (for ChatGPT script generation)
- **ElevenLabs API Key** (for text-to-speech)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd yugioh-video-creator
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install openai
pip install elevenlabs
pip install moviepy
pip install opencv-python
pip install pillow
pip install numpy
pip install requests
pip install torch
pip install torchaudio
pip install ChatTTS
```

### 4. Install FFmpeg

1. Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract to `C:\Program Files\ffmpeg-<version>-full_build\`
3. Add FFmpeg to your system PATH or update the path in `src/utils/crop_to_short.py`

### 5. Create Configuration Files

#### Create `src/modules/secrets.json`:

```json
{
  "openai_api_key": "your-openai-api-key-here",
  "elevenlabs_api_key": "your-elevenlabs-api-key-here"
}
```

**Important**: Never commit this file to version control. Add `secrets.json` to your `.gitignore`.

### 6. Create Required Directories

```bash
mkdir src\videos
mkdir src\audio
mkdir src\shorts
```

## Usage

### Single Card Video Creation

```python
from src.modules.yugioh_video_maker import YugiohVideoMaker

# Create a video for a specific card
video_maker = YugiohVideoMaker(card_name="Blue-Eyes White Dragon")
video_maker.setup_video()
video_maker.create_video()
```

### Batch Video Creation

```bash
cd src/modules
python mass_video_maker.py
```

This will prompt you for a Yu-Gi-Oh database URL and create videos for all cards in the search results.

### Create Shorts from Videos

```bash
cd src/modules
python mass_shorts_maker.py
```

This will convert all generated videos to vertical format suitable for YouTube Shorts.

### Manual Video Cropping

```bash
cd src/utils
python crop_to_short.py "path/to/input/video.mp4"
```

## API Keys Setup

### OpenAI API Key

1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add it to `secrets.json`

### ElevenLabs API Key

1. Go to [https://elevenlabs.io/](https://elevenlabs.io/)
2. Sign up and get your API key
3. Add it to `secrets.json`

## Configuration

### Voice Settings

The default voice ID is "PRESTIGED" (ElevenLabs voice). You can modify voice settings in `yugioh_video_maker.py`:

```python
self.voice_ids = {
    "PRESTIGED": "ijEuPMqoI2gEEA41kGv3"
}
```

### Video Settings

Adjust video parameters in the `create_video()` method:

- `rotation_start/end`: Card rotation animation
- `start_scale/end_scale`: Card size scaling
- `flip_duration_ratio`: Animation timing

## Output

- **Videos**: Generated in `src/videos/` directory
- **Audio**: Generated in `src/audio/` directory
- **Shorts**: Generated in `src/shorts/` directory

## Troubleshooting

### Common Issues

1. **FFmpeg not found**: Update the FFmpeg path in `crop_to_short.py`
2. **API key errors**: Verify your API keys in `secrets.json`
3. **Memory issues**: Reduce the number of parallel processes in mass processing scripts
4. **GPU encoding errors**: Fall back to CPU encoding by removing `h264_nvenc` parameter

### Performance Tips

- Use an NVIDIA GPU for faster video encoding
- Adjust `num_processes` in mass processing scripts based on your CPU cores
- Consider using SSD storage for faster file I/O

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and personal use. Please respect the terms of service for OpenAI and ElevenLabs APIs.

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the code comments
3. Create an issue in the repository
