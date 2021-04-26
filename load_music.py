import json
import boto3
with open("static/a2.json") as f:
    data = json.load(f)

db = boto3.resource('dynamodb')
try:
    music_table = db.Table('music')
    for i in range(len(data["songs"])):
        music_table.put_item(
        Item={
            'title': data["songs"][i]["title"],
            'artist': data["songs"][i]["artist"],
            'year': data["songs"][i]["year"],
            'web_url': data["songs"][i]["web_url"],
            'image_url': data["songs"][i]["img_url"]
            }
        )
        print("Added song {} | {} | {}".format(data["songs"][i]["title"], data["songs"][i]["artist"],data["songs"][i]["year"]))
    print("Added {} songs to music_table".format(len(data["songs"])))
except:
    print("music table does not exist, please run create_music_table.py")