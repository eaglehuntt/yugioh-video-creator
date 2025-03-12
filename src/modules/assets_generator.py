import requests
import os
from openai import OpenAI
import json
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from elevenlabs import VoiceSettings

class AssetsGenerator:
    def __init__(self, card_name=None) -> None:
        self.card_effect = None
        self.card_readable_type = None
        self.prompt = None
        self.script = None

        self.voice_ids = {
            "PRESTIGED" : "ijEuPMqoI2gEEA41kGv3"
        }

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

        load_dotenv()

        self.elevenlabs_client = ElevenLabs(
            api_key = self.secrets["elevenlabs_api_key"],
        )

        self.load_card_details(card_name)

    def load_card_details(self, card_name=None):
        card = self.get_card(card_name)
        
        if card == None: 
            return
        
        self.card_name = card["name"]
        self.card_readable_type = card["humanReadableCardType"]
        self.card_effect = card["desc"]
        self.card_type = card["type"]

        self.prompt = f"Write me an engaging YouTube short script based on this YuGiOh card, explaining what it does. Follow this formula exactly, do not add any extra text beyond what I specifically ask for, and write at least three sentences: [Name] is a [Card Type] that {{summarize the [Effect]}} at the end make a closing remark like 'subscribe for more videos like this'. Stay semi-neutral in nature, but be engaging. Avoid being corny. Rules: Replace all numbers with their fully spelled-out form. Example: {{four}} instead of {{4}}. If a card says {{ATK}} replace it with {{attack}} or {{DEF}} replace it with {{defense}} Stick to the structure given without adding extra commentary. Card details: Name = {self.card_name} Card Type = {self.card_readable_type} Effect = {self.card_effect}"

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


    def get_card_script(self): 
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

    def text_to_speech(self):
        audio_stream = self.elevenlabs_client.text_to_speech.convert(
        voice_id=self.voice_ids["PRESTIGED"],
        output_format="mp3_44100_128",
        text=self.script,
        model_id=self.voice_models["flash"],
        voice_settings=VoiceSettings(
            stability=0.30,
            similarity_boost=1.0,
            speed=0.95
        )
    )
        output_path = f"{self.card_name}.mp3"
        with open(output_path, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)

        print(f"✅ Audio saved as {output_path}")



yugioh = AssetsGenerator("armory arm")
yugioh.get_card_script()
yugioh.text_to_speech()
# print(yugioh.script)

