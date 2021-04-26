import json
import boto3
with open("static/a2.json") as f:
    data = json.load(f)

db = boto3.resource('dynamodb')
print("creating table...")
try:
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
    print("music_table created.")
except:
    print("error creating music_table")