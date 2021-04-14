import json
import boto3
import requests
import os
from boto3 import s3
from time import sleep
s3 = boto3.client('s3')
with open("static/a2.json") as f:
    data = json.load(f)

for i in range(len(data["songs"])):
    image_reponse = requests.get(data["songs"][i]['img_url'])
    artist_filepath = os.path.join("artist_images", data["songs"][i]['artist'] + ".jpg")
    image_file = open(artist_filepath, "wb")
    image_file.write(image_reponse.content)
    try:
        s3.upload_file(artist_filepath, 'cc-assignment2-berke-artist-images', data["songs"][i]['artist'] + ".jpg")
        print("Downloading and uploading image for artist: " + data["songs"][i]['artist'] + " from img_url: " + data["songs"][i]['img_url'] )
    except:
        print("Could not upload image for artist: " + data["songs"][i]['artist'])
    image_file.close()
    sleep(0.5)