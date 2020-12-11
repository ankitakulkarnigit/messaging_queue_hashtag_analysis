from flask import Flask, request, jsonify
import sqlite3
from flask import g, json
import hashlib
import requests
from datetime import datetime, timedelta
import time
from redis import Redis
from rq import Queue
from rq import Retry
import redis


queue = Queue(connection=Redis())
redisClient = redis.StrictRedis(host='localhost', port=6379, db=0)


######################
# API USAGE
# Web server route for this API: localhost:6100
# --------------------
# Get user timeline: Send a GET request to route of getUserTimeline() fn
# Example request:
#   curl -i -X GET -H 'Content-Type:application/json' -d '{"usernameAPI":"ankita"}' http://localhost:6100/getUserTimeline;
# --------------------
# Get public timeine: Send a GET request to route of getPublicTimeline() fn
# Example request:
#   curl -i -X GET http://localhost:6100/getPublicTimeline;
# --------------------
# Get a home timeline: Send a GET request to route of getHomeTimeline() fn
# Example request:
#   curl -i -X GET -H 'Content-Type:application/json' -d '{"usernameAPI":"ankita"}' http://localhost:6100/getHomeTimeline;
# --------------------
# Post a tweet: Send a POST request to route of postTweet() fn
# Example request:
#   curl -i -X POST -H 'Content-Type:application/json' -d '{"usernameAPI":"ankita", "tweetAPI":"#COVID-19 vaccine: #UK regulators warn people with history of 'significant' allergic reactions not to have #Pfizer"}' http://localhost:6100/postTweet;
# --------------------

######################
# Database
# db_name: UsersMicroservice.db

# table1: Users
# username
# email
# pass

# table2: Followers
# username
# usernamefollowing

# table3: Tweets
# username
# tweet
# timestamp


# config variables
app = Flask(__name__)
DATABASE = 'UsersMicroservice.db'

@app.teardown_appcontext
def close_connection(exception=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# helper function to generate a response with status code and message
def get_response(status_code, message):
    return {"status_code": str(status_code), "message": str(message)}

# get db from flask g namespace
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# function to execute a single query at once
def query_db(query, args=(), one=False):
    with app.app_context():
        db = get_db()
        cur = db.execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv

# funstion to initialize db
@app.cli.command('init')
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# function to get user timeline
@app.route("/getUserTimeline", methods=['GET'])
def getUserTimeline():
    params = request.get_json()
    user_name = params.get('usernameAPI')
    if not user_name:
        return jsonify(get_response(status_code=409, message="username is not in request")), 409
    else:
        TweetsList = query_db('select * from Tweets where username = ? order by time_stamp desc limit 25', [user_name])
        response = jsonify(get_response(status_code=201, message=TweetsList))
        response.status_code = 201
        response.autocorrect_location_header = False
        return response

#function to get public timeline
@app.route("/getPublicTimeline", methods=['GET'])
def getPublicTimeline():
    recentTweets = query_db('select * from Tweets order by time_stamp desc limit 25')
    response = jsonify(get_response(status_code=201, message=recentTweets))
    #if response.last_modified < 5:
    response.status_code = 201
    response.autocorrect_location_header = False
    return response

# function to get home timeline
@app.route("/getHomeTimeline", methods=['GET'])
def getHomeTimeline():
    params = request.get_json()
    user_name = params.get('usernameAPI')
    tweets = []
    if not user_name:
        return jsonify(get_response(status_code=409, message="Username is not in request")), 409
    else:
        tweets = query_db('select tweet from Tweets where username in (select usernamefollowing from Followers where username = ?) order by time_stamp desc limit 25', [user_name])
        response = jsonify(get_response(status_code=201, message=tweets))
        response.status_code = 201
        response.autocorrect_location_header = False
        return response

# function to post a tweet
# curl -i -X POST -H 'Content-Type:application/json' -d '{"usernameAPI":"ankita", "tweetAPI":"#COVID-19 vaccine: #UK regulators warn people with history of 'significant' allergic reactions not to have #Pfizer"}' http://localhost:6100/postTweet;
@app.route("/postTweet", methods=['POST'])
def postTweet():
    params = request.get_json()
    user_name = params.get('usernameAPI')
    tweet_text = params.get('tweetAPI')
    if not user_name or not tweet_text:
        return jsonify(get_response(status_code=409, message="username / tweet is not in request")), 409
    else:
        if query_db('select username from Users where username = ?', [user_name]):
            with sqlite3.connect("UsersMicroservice.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO Tweets (username, tweet) VALUES (?,?)", (user_name, tweet_text))
                con.commit()
            response = jsonify(get_response(status_code=201, message="Tweet Posted Successfully!!"))
            response.status_code = 201
            response.autocorrect_location_header = False
            return response
        else:
            return jsonify(get_response(status_code=409, message="Username does not exist. Create a user first to proceed")), 409

if __name__ == "__main__":
    app.run(debug = True) 
