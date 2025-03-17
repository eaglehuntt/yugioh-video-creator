
import requests
import os
import json
from urllib.parse import urlparse, parse_qs, urlencode
from yugioh_video_maker import YugiohVideoMaker  

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

def create_videos():
    # API URL for fetching cards
    web_db_url = input("Paste the Yu-Gi-Oh Database URL here: ")
    api_url_prefix = "https://db.ygoprodeck.com/api/v7/cardinfo.php?"
    api_url = api_url_prefix + strip_ygoprodeck_url(web_db_url)
    print(f"Fetching data from: {api_url}")

    response = requests.get(api_url).json()

    # Check if the response contains data
    if "data" in response:
        for card in response["data"]:

            card_name = card["name"]
            card_effect = card["desc"]
            card_readable_type = card["humanReadableCardType"]
            card_type = card["type"]
            card_name = card["name"]
            image_url = card["card_images"][0]  # Get first image set
        
            # Create a YuGiOhVideoMaker object and generate a video
            video_maker = YugiohVideoMaker(
                card_name=card_name,
                card_effect=card_effect,
                card_readable_type=card_readable_type,
                card_img=image_url,
            )
            
            video_maker.create_video()  # Assuming this method exists

    else:
        print("No data found or API request failed.")
