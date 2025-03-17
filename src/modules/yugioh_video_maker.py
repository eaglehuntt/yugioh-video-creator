import requests
import os
from openai import OpenAI
import json
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from elevenlabs import VoiceSettings
from moviepy import *
import random
import numpy as np
from PIL import Image
from io import BytesIO
import math

from functools import partial
import cv2

class YugiohVideoMaker:
    def __init__(self, card_name=None, voice_id="PRESTIGED", bg_audio:int=None, card_effect=None, card_readable_type=None, card_img=None, card_type=None) -> None:
        self.card_name = card_name
        self.card_effect = card_effect
        self.card_readable_type = card_readable_type
        self.card_img = card_img
        self.card_type = card_type
        self.prompt = None
        self.script = None
        self.audio = None
        self.bg_audio = bg_audio

        self.voice_ids = {
            "PRESTIGED" : "ijEuPMqoI2gEEA41kGv3"
        }

        if voice_id not in self.voice_ids:
            self.voice_id = self.voice_ids["PRESTIGED"]
        else:
            self.voice_id = self.voice_ids[voice_id]

        self.voice_models = {
            "flash" : "eleven_flash_v2_5",
            "expensive" : "eleven_multilingual_v2"
        }

        # open our secrets json and load OpenAI api key
        with open('src\modules\secrets.json', 'r') as file:
            self.secrets = json.load(file)

        self.client = OpenAI(
            api_key = self.secrets["openai_api_key"]
        )

        self.elevenlabs_client = ElevenLabs(
            api_key = self.secrets["elevenlabs_api_key"],
        )

        self.load_card_details(card_name)

    def load_card_details(self, card_name=None):

        existing_audio = os.path.join('src','audio', f"{self.card_name}.mp3")
        if os.path.isfile(existing_audio):
            print(f"🟡 {self.card_name} audio already exists.")
            cont = input("❓ Would you like to reuse details with that audio? (y/n) ")
            if cont == "y":
                print("✅ Continuing with existing data")
            else:
                if self.card_name and self.card_img and self.card_type and self.card_readable_type and self.card_effect:
                    print("✅ Details already loaded")
                    self.card_img = Image.open(BytesIO(requests.get(self.card_img).content))
                else:
                    self.prompt = f"Write me an engaging YouTube short script based on this YuGiOh card, explaining what it does. Follow this formula exactly, do not add any extra text beyond what I specifically ask for, and write at least three sentences: [Name] is a [Card Type] that {{summarize the [Effect]}} Stay semi-neutral in nature, but be engaging. Avoid being corny. Also, keep vocabulary failry basic and easy to understand, do not use words like 'formidable' instead opt for words like 'strong', etc. Rules: Replace all numbers with their fully spelled-out form. Example: {{four}} instead of {{4}}. If a card says {{ATK}} replace it with {{attack}} or {{DEF}} replace it with {{defense}} Stick to the structure given without adding extra commentary. Card details: Name = {self.card_name} Card Type = {self.card_readable_type} Effect = {self.card_effect}"
                    self.get_script()

        card = self.get_card(card_name)
        self.card_name = card["name"]
        self.card_readable_type = card["humanReadableCardType"]
        self.card_effect = card["desc"]
        self.card_type = card["type"]
        card_img = Image.open(BytesIO(requests.get(card["card_images"][0]["image_url"]).content))
        self.card_img = np.array(card_img)

        print(f"✅ Loaded card: {self.card_name}")

    def get_card(self, card_name=None):

        if card_name == None:
            url = "https://db.ygoprodeck.com/api/v7/randomcard.php"
            response = requests.get(url).json()
            return response["data"][0]
        else:
            url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?fname={card_name}"
            response = requests.get(url).json()

            if len(response["data"]) < 1:
                print(f"❌ No results matching {card_name}")
                return -1

            for i in range(len(response)):
                if response["data"][i]["name"].upper() == card_name.upper():
                    return response["data"][i]
            
            print(f"🟡 No results matching {card_name}. The first result is {response['data'][0]['name']}")

            cont = input(f"Would you like to continue with {response['data'][0]['name']}? (y/n) ")

            if cont == "y":
                return response["data"][0]
            else:
                return None


    def get_script(self, background_audio=None): 
        print(f"🔃 Getting script for {self.card_name}")
        if self.card_name == None or self.card_effect == None or self.card_readable_type == None or self.prompt == None: 
            raise Exception("Error, make sure card data is retrieved before function call")
        
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role" : "user",
                    "content" : self.prompt
                }
            ], model="gpt-4o-mini",
        )
        script = chat_completion.choices[0].message.content
        self.script = script
        print("✅ Script received from ChatGPT")

        # print_script = input("Would you like to print the script? (y/n) ")

        # if print_script == "y":
        #     print(self.script)

    def get_audio(self):
        audio_stream = self.elevenlabs_client.text_to_speech.convert(
        voice_id=self.voice_ids["PRESTIGED"],
        output_format="mp3_44100_128",
        text=self.script,
        model_id=self.voice_models["flash"],
        voice_settings=VoiceSettings(
            stability=0.70,
            similarity_boost=0.99,
            speed=0.95
        )
    )
        
        if not os.path.exists('assets'):
            os.makedirs('assets')

        output_path = os.path.join('src', 'audio', f"{self.card_name}.mp3")

        with open(output_path, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)

        print(f"✅ Audio saved as {output_path}")
        self.audio = output_path
        return output_path

    def create_video(self, rotation_start=90, flip_axis='x',  
    rotation_end=0, flip_duration_ratio=0.03, start_scale=0.4,            # card starts at 30% of full size
    end_scale=0.7
    ):
        existing_audio = os.path.join('src','audio', f"{self.card_name}.mp3")
        if os.path.isfile(existing_audio):
            print(f"🟡 {self.card_name} audio already exists.")
            cont = input("❓ Would you like to continue and make a video with that audio? (y/n) ")
            if cont == "y":
                script_audio = existing_audio
            else:
                print("❌ Exiting")
                return -1
        else:
            script_audio = self.get_audio()

        script_audio = AudioFileClip(script_audio)
        video_duration = script_audio.duration

        # get background video
        bg_video = VideoFileClip(os.path.join('src', 'assets', 'background.mp4')).with_duration(video_duration)

        # get background audio
        if self.bg_audio == None:
            choice = random.randint(1, 5)
            bg_audio_path = os.path.join('src', 'assets', 'music', f"{choice}.mp3")
            print(f"🟡 No background audio selected, using {choice}")
        else:
            bg_audio_path = os.path.join('src', 'assets', 'music', f"{self.bg_audio}.mp3")

        bg_audio = AudioFileClip(bg_audio_path).with_effects([afx.MultiplyVolume(0.1)])
        bg_audio = bg_audio.with_duration(video_duration)

        sfx = AudioFileClip(os.path.join('src', 'assets', 'sfx', 'sfx.mp3')).with_effects([afx.MultiplyVolume(0.7)])

        full_audio = CompositeAudioClip([script_audio, bg_audio, sfx])
        
        T = video_duration
        T_flip = T * flip_duration_ratio  # duration over which the flip happens

        def flip_and_grow(get_frame, t):
            frame = get_frame(t).copy()
            if t <= T_flip:
                # Flip phase: apply a flip transformation only.
                fraction = t / T_flip  # goes from 0 to 1 during the flip phase
                angle = rotation_start + fraction * (rotation_end - rotation_start)
                if flip_axis == 'y':
                    rad = math.radians(angle)
                    # Simulate a flip about the y-axis by scaling the width by |cos(angle)|
                    flip_scale_x = abs(math.cos(rad))
                    flip_scale_y = 1.0
                elif flip_axis == 'x':
                    rad = math.radians(angle)
                    # Flip about the x-axis by scaling the height by |cos(angle)|
                    flip_scale_y = abs(math.cos(rad))
                    flip_scale_x = 1.0
                elif flip_axis == 'z':
                    # For a 2D in-plane rotation, we will perform a full rotation transformation.
                    flip_scale_x = 1.0
                    flip_scale_y = 1.0
                else:
                    # Default to y-axis
                    rad = math.radians(angle)
                    flip_scale_x = abs(math.cos(rad))
                    flip_scale_y = 1.0

                # During the flip phase, we keep the zoom factor fixed at start_scale.
                current_scale = start_scale
                new_width = max(int(frame.shape[1] * flip_scale_x * current_scale), 1)
                new_height = max(int(frame.shape[0] * flip_scale_y * current_scale), 1)
                resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

                if flip_axis == 'z':
                    # For z-axis, apply an in-plane rotation
                    center = (new_width // 2, new_height // 2)
                    M = cv2.getRotationMatrix2D(center, angle, 1.0)
                    rotated_frame = cv2.warpAffine(resized_frame, M, (new_width, new_height))
                    return rotated_frame
                else:
                    return resized_frame

            else:
                # Zoom phase: the flip is complete (the card remains at its final orientation).
                # Apply a zoom that linearly scales the image from start_scale to end_scale over the time from T_flip to T.
                fraction_zoom = (t - T_flip) / (T - T_flip) if (T - T_flip) > 0 else 1.0
                zoom_factor = start_scale + fraction_zoom * (end_scale - start_scale)
                new_width = max(int(frame.shape[1] * zoom_factor), 1)
                new_height = max(int(frame.shape[0] * zoom_factor), 1)
                return cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

        # Pre-fill `duration` using functools.partial
        # grow_with_duration = partial(grow, duration=video_duration)
        grow_with_duration = partial(flip_and_grow)


        card_clip = ImageClip(self.card_img).with_position('center').with_duration(video_duration).transform(grow_with_duration)

        comp = CompositeVideoClip([bg_video, card_clip], size=(1920, 1080)
                                  ).with_audio(full_audio)

        # comp.preview(fps=30, audio=True, audio_fps=22050, audio_buffersize=3000, audio_nbytes=2)

        comp.write_videofile(f"./src/videos/{self.card_name}.mp4", codec="libx264",  # H.264 codec
            audio_codec="aac",  # Audio codec
            threads=4,  # Set number of threads (optional)
            ffmpeg_params=[
                "-c:v", "h264_nvenc",  
                "-preset", "p4",  
                "-gpu", "0",  
                "-b:a", "192k"  # Explicitly set audio bitrate
            ]  # Use NVENC for H.264 encoding)
        )

        print(f"✅ Video created for {self.card_name}")
