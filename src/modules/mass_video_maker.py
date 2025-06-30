import requests
import os
import json
from urllib.parse import urlparse, parse_qs, urlencode
from yugioh_video_maker import YugiohVideoMaker
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import time

def strip_ygoprodeck_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Remove unnecessary parameters
    ignored_params = {"num", "offset"}
    filtered_params = {k: v for k, v in query_params.items() if k not in ignored_params}
    filtered_params = {'fname' if k == 'name' else k: v for k, v in filtered_params.items()}

    # Reconstruct the stripped query string
    stripped_query = urlencode(filtered_params, doseq=True)
    return stripped_query

def process_card(card_data):
    """Process a single card and create its video"""
    try:
        card_name = card_data["name"]
        card_effect = card_data["desc"]
        card_readable_type = card_data["humanReadableCardType"]
        card_type = card_data["type"]
        image_url = card_data["card_images"][0]["image_url"]
        
        if "Monster" in card_readable_type:
            card_atk = card_data["atk"]
            card_def = card_data["def"]
        else:
            card_atk = None
            card_def = None

        # Create a YuGiOhVideoMaker object
        video_maker = YugiohVideoMaker(
            card_name=card_name,
            card_effect=card_effect,
            card_readable_type=card_readable_type,
            card_img=image_url,
            card_type=card_type,
            card_atk=card_atk,
            card_def=card_def
        )
        
        # Get the script using ChatGPT
        prompt = video_maker.get_prompt()
        script = video_maker.get_script_from_chatgpt(prompt)
        video_maker.set_script(script)
        
        # Create the video
        video_maker.create_video()
        
        # Return the path of the created video
        video_name = card_name.replace(' ', '_')
        video_path = os.path.join('src', 'videos', f"{video_name}.mp4")
        return (True, video_path)
    except Exception as e:
        print(f"Error processing card {card_data.get('name', 'Unknown')}: {str(e)}")
        return (False, None)

def create_videos():
    # API URL for fetching cards
    web_db_url = input("Paste the Yu-Gi-Oh Database URL here: ")
    api_url_prefix = "https://db.ygoprodeck.com/api/v7/cardinfo.php?"
    api_url = api_url_prefix + strip_ygoprodeck_url(web_db_url)
    print(f"Fetching data from: {api_url}")

    response = requests.get(api_url).json()

    # Check if the response contains data
    if "data" in response:
        # Determine number of processes to use (leave one CPU core free)
        num_processes = max(1, multiprocessing.cpu_count() - 1)
        print(f"Using {num_processes} processes for parallel video creation")

        # Create a process pool and process cards in parallel
        with ProcessPoolExecutor(max_workers=num_processes) as executor:
            results = list(executor.map(process_card, response["data"]))
        
        # Separate successful and failed results
        successful_videos = [path for success, path in results if success and path]
        failed = len([r for r in results if not r[0]])
        
        print(f"\nVideo creation completed:")
        print(f"✅ Successfully created: {len(successful_videos)}")
        print(f"❌ Failed: {failed}")
        
        return successful_videos
    else:
        print("No data found or API request failed.")
        return []

if __name__ == "__main__":
    create_videos()
