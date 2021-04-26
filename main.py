from flask import Flask, render_template, request, redirect, url_for, g
import boto3
from boto3.dynamodb.conditions import Key, Attr
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
db = boto3.resource('dynamodb')
login_table = db.Table('login')
music_table = db.Table('music')
current_user = None

@app.route('/', methods=['POST', 'GET'])
def index():
    global current_user
    g.current_user = current_user
    queried_music = []
    made_query = False
    if request.method == 'POST':
        if request.form['post_type'] == "subscribe":
            update_subscription("add", current_user, request.form['song_to_subscribe'])
        elif request.form['post_type'] == "remove":
            update_subscription("remove", current_user, request.form['song_to_remove'])
        elif request.form['post_type'] == "query":
            query_title = request.form['title']
            query_year = request.form['year']
            query_artist = request.form['artist']
            queried_music = query_music(title = query_title, year = query_year, artist = query_artist)  
            made_query = True  
    if current_user != None:
        user_subscriptions = get_subscriptions_details(current_user['subscriptions'])
        return render_template('index.html', user_subscriptions=user_subscriptions, queried_music=queried_music, made_query=made_query)
    else:
        return render_template('index.html',queried_music=queried_music, made_query=made_query)

@app.route('/login', methods=['POST', 'GET'])
def login():
    global current_user
    g.current_user = current_user
    login_success = True
    if request.method=='POST':
        entered_email = request.form['email']
        entered_pass = request.form['pass']
        if(login_valid(entered_email, entered_pass)):
            current_user = get_user_by_email(entered_email)
            g.current_user = current_user
            return redirect(url_for('index'))
        else:
            login_success=False

    return render_template('login.html', login_success=login_success)

@app.route('/register', methods=['POST', 'GET'])
def register():
    global current_user
    g.current_user = current_user
    register_success = True
    if request.method == 'POST':
        entered_email = request.form['email']
        entered_username = request.form['username']
        entered_pass = request.form['pass']
        if(get_user_by_email(entered_email)!= None):
            register_success = False
        else:
            register_user(entered_email, entered_username, entered_pass)
            return redirect(url_for('login'))
    return render_template('register.html', register_success=register_success)

@app.route('/logout')
def logout():
    global current_user
    current_user = None
    g.current_user = None

    return redirect(url_for('login'))

def login_valid(email, password):
    valid = False
    user = get_user_by_email(email)
    if user != None and email == user['email'] and password == user['password']:
        valid = True     

    return valid

def query_music(**kwargs):
    query_filter_list = []
    for key, value in kwargs.items():
        if value != "":
            query_filter_list.append("Attr('{}').eq('{}')".format(key,value))
    query_filter_expression = " & ".join(f for f in query_filter_list)
    try:
        music_response = music_table.scan(
            FilterExpression=eval(query_filter_expression)
        )
        music = music_response['Items']
    except:
        app.logger.warning("music query failed. returning empty result")
        music = []

    return music

def get_user_by_email(email):
    try:
        user_response = login_table.get_item(Key={'email':email})
        user = user_response['Item']
    except:
        user = None

    return user

def get_subscriptions_details(subscriptions):
    song_details_list = []
    try:
        for song in subscriptions:
            song_details_response = music_table.get_item(Key={'title':song})
            song_details = song_details_response['Item']
            song_details_list.append(song_details)
    except:
        print("Error getting subscriptions")

    return song_details_list

def update_subscription(addremove, user, song):
    user_subscriptions = user['subscriptions']
    if(addremove=="add"):
        user_subscriptions.append(song)
    elif(addremove=="remove"):
        user_subscriptions.remove(song)
    try:
        login_table.update_item(
            Key={
                'email':current_user['email']
            },
            UpdateExpression='SET subscriptions = :val',
            ExpressionAttributeValues={':val': user_subscriptions}
        )
    except:
        app.logger.warning("updating subscription (add/remove) failed.")

def register_user(email, username, password):
    success = True
    try:
        login_table.put_item(
            Item={
                'email': email,
                'user_name': username,
                'password': password,
                'subscriptions': []
            }
        )
    except:
        success = False
        print("Error registering user.")
    return success

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)
 