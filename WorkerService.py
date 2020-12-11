from flask import Flask, request, jsonify
import sqlite3
from flask import g
import hashlib
import requests

from datetime import datetime, timedelta
import time
from redis import Redis
from rq import Queue
import redis
import logging

######################
# API USAGE
# Web server route for this API: localhost:6200
# --------------------
# Post a tweet: Send a POST request to route of postTweet() fn
# Example request:
#   curl -i -X POST -H 'Content-Type:application/json' -d '{"usernameAPI":"ankita", "tweetAPI":"#COVID-19 vaccine: #UK regulators warn people with history of 'significant' allergic reactions not to have #Pfizer"}' http://localhost:6200/postTweet;
# --------------------
# Query Tweets DB: Send a GET request to route of queryTable() fn
# Example request:
#   curl -i -X GET http://localhost:6200/query;
# --------------------
# Hashtag Analysis: Send a GET request to route of show_trending() fn
# Example request:
#   curl -i -X GET http://localhost:6200/trending;
# --------------------

app = Flask(__name__)
DATABASE = 'UsersMicroservice.db'
q = Queue(connection=Redis())
redisClient = redis.StrictRedis(host='localhost', port=6379, db=0)
logging.basicConfig(level=logging.DEBUG)

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
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# worker function for rq update to db while posting
def updateTable(user, tweet):
    with app.app_context():
        if query_db('select username from Users where username = ?', [user]):
            with sqlite3.connect("UsersMicroservice.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO Tweets (username, tweet) VALUES (?,?)", (user, tweet))
                con.commit()
            return jsonify(get_response(status_code=201, message="Tweet Successfully Posted through Worker!!"))
        else:
            return jsonify(get_response(status_code=409, message="Username does not exist. Create a user first to proceed")), 409

# worker function for hashtag analysis
def hastagAnalysis(tweet):
    text_list = tweet.split(' ')
    res = []
    for sub in text_list: 
        # splitting phrases 
        temp = sub.split() 
        for ele in temp: 
            # checking for matching elements 
            if ele[0].lower() == '#'.lower(): 
                res.append(ele) 
    
    # printing result  
    #print("The filtered elements : " + str(res)) 

    # Retrieve all keys
    trending = {}
    TrendingList = redisClient.zrevrange('trendings', 0,-1,'withscores')
    dict(TrendingList)
    for k,v in TrendingList:
        trending[k.decode("utf-8")] = int(v)
    
    # Remove elemets from Redis Sorted List
    #redisClient.zrem("[\"['#trending']\", \"['#trending', '#new']\", \"'\", '#trending', '#onTwitter', '#incr', '#attempt']")
    
    # make dict
    newDict = dict()
    for tag in res:
        newDict[tag] = 1
    
    # Add the keys with scores    
    newTag = {} 
    for tag, score in newDict.items():
        if tag in trending:
            newTag[tag] = 1.0
            redisClient.zincrby('trendings',1,tag)
        else:
            newTag[tag] = 1.0
            redisClient.zadd('trendings', newTag)

    return newTag
    
# function to post a tweet
# curl -i -X POST -H 'Content-Type:application/json' -d '{"usernameAPI":"ankita", "tweetAPI":"#COVID-19 vaccine: #UK regulators warn people with history of 'significant' allergic reactions not to have #Pfizer"}' http://localhost:6200/postTweet;
@app.route("/postTweet", methods=['POST'])
def postTweet():
    params = request.get_json()
    user_name = params.get('usernameAPI')
    tweet_text = params.get('tweetAPI')
    if not user_name or not tweet_text:
        return jsonify(get_response(status_code=409, message="username / tweet is not in request")), 409
    else:
        job1 = q.enqueue(updateTable, user_name, tweet_text)
        q.enqueue(hastagAnalysis, tweet_text, depends_on=job1)
        return jsonify(get_response(status_code=201, message="Tweet Posted Successfully!!",))

# helper function to query Tweets table
# curl -i -X GET http://localhost:6200/query;
@app.route("/query")
def queryTable():
    result = query_db('select * from Tweets')
    response = jsonify(get_response(status_code=200, message=result))
    return response

# Function for getting top 25 trends
# curl -i -X GET http://localhost:6200/trending;
@app.route('/trending')
def showTrending():
    topTrending = {}
    TrendingList = redisClient.zrevrange('trendings', 0,25,'withscores')
    dict(TrendingList)
    for k,v in TrendingList:
        topTrending[k.decode("utf-8")] = int(v)

    return jsonify(get_response(status_code=200, message=topTrending))

if __name__ == '__main__':
   app.run(debug=True)