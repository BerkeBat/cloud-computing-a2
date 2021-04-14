import json
import boto3
with open("static/a2.json") as f:
    data = json.load(f)

db = boto3.resource('dynamodb')
print("Creating Table...")
music_table = db.create_table(
    TableName='music',
    KeySchema=[
        {
            'AttributeName':'title',
            'KeyType':'HASH'
    }],
    AttributeDefinitions=[
        {
            'AttributeName': 'title',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)
music_table.meta.client.get_waiter('table_exists').wait(TableName='music')
print("music_table created. Loading songs.")
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