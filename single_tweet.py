from dotenv import load_dotenv
from requests_oauthlib import OAuth1
import os
import json
import requests

load_dotenv() 


consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')
access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')


oauth = OAuth1(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret
)


object_id = 2019


object_url = f'https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}'
object_data = requests.get(object_url).json()


if object_data['primaryImage']:
    image_url = object_data['primaryImage']

    image_response = requests.get(image_url, stream=True)
    with open('art_image.jpg', 'wb') as file:
        file.write(image_response.content)
else:
    print("No image available for this object.")
    exit()


media_upload_url = "https://upload.twitter.com/1.1/media/upload.json"
image_path = "art_image.jpg"

with open(image_path, 'rb') as image_file:
    files = {
        'media': image_file
    }

    media_response = requests.post(
        media_upload_url,
        auth=oauth,  
        files=files
    )

    if media_response.status_code == 200:
        media_id = media_response.json()['media_id_string']
        print(f"Media uploaded successfully. Media ID: {media_id}")
    else:
        print(f"Failed to upload media: {media_response.text}")
        exit()


tweet_url = "https://api.twitter.com/2/tweets"
tweet_text = f"Here is today's artwork: {object_data['title']} by {object_data['artistDisplayName']} ({object_data['objectDate']})"


tweet_data = {
    "text": tweet_text,
    "media": {
        "media_ids": [media_id]  
    }
}

tweet_response = requests.post(
    tweet_url,
    auth=oauth, 
    headers={"Content-Type": "application/json"},
    data=json.dumps(tweet_data)
)


if tweet_response.status_code == 201:
    print("Tweet posted successfully!")
else:
    print(f"Failed to post tweet: {tweet_response.text}")