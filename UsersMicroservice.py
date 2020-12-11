from flask import Flask, request, jsonify
import sqlite3
from flask import g
import hashlib
import datetime
import click
from flask.cli import with_appcontext

######################
# API USAGE
# Web server route for this API: localhost:6000
# --------------------
# Create a new user: Send a POST request to route of createUser() fn
# Example request:
#   curl -i -X POST -H 'Content-Type:application/json' -d '{"usernameAPI":"newuser", "emailAPI":"newuser@gmail.com", "passwordAPI":"newuser@123"}' http://localhost:6000/createUser;
# --------------------
# Authenticate an existing post: Send a GET request to route of authenticateUser() fn
# Example request:
#   curl -i -X GET -H 'Content-Type:application/json' -d '{"usernameAPI":"ankita", "passwordAPI":"ankita@123"}' http://localhost:6000/authenticateUser;
# --------------------
# Follow an existing user: Send a POST request to route of addFollower() fn
# Example request:
#   curl -i -X POST -H 'Content-Type:application/json' -d '{"usernameAPI":"om", "usernameFollowingAPI":"ankita"}' http://localhost:6000/addFollower;
# --------------------
# Remove an existing follower: Send a DELETE request to route of removeFollower() fn
# Example request:
#   curl -i -X DELETE -H 'Content-Type:application/json' -d '{"usernameAPI":"om", "usernameFollowingAPI":"ankita"}' http://localhost:6000/removeFollower;
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

# helper function to get hash of the password during user authentication
def hsh(txt):
    a = hashlib.md5()
    a.update(txt.encode('utf-8'))
    return a.hexdigest()

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

# initiate db with
# $FLASK_APP=post_api.py
# $flask init
@app.cli.command('init',with_appcontext=True)
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# home page
@app.route('/', methods=['GET'])
def home():
    return jsonify(get_response(status_code=200, message="Database Initialized and Populated!"))

# function to create a new user
@app.route("/createUser", methods=['POST'])
def createUser():
    params = request.get_json()
    username_ = params.get('usernameAPI')
    email_ = params.get('emailAPI')
    password_ = params.get('passwordAPI')
    if not username_ or not email_ or not password_:
        return jsonify(get_response(status_code=409, message="username / emails / password is not in request")), 409
    else:
        with sqlite3.connect("UsersMicroservice.db") as con:
            cur = con.cursor()
            cur.execute("INSERT OR IGNORE INTO Users (username, email, pass) VALUES (?,?,?)", (username_, email_, hsh(password_)))
            con.commit()

        for user in query_db('select * from Users'):
            print(user)

        response = jsonify(get_response(status_code=201, message="User created"))
        response.status_code = 201
        response.autocorrect_location_header = False
        return response

# function to authenticate an existing user
@app.route("/authenticateUser", methods=['GET'])
def authenticateUser():
    params = request.get_json()
    username = params.get('usernameAPI')
    password = params.get('passwordAPI')
    if not username or not password:
        return jsonify(get_response(status_code=409, message="username / password is not in request")), 409
    else:
        user = query_db('select * from users where username = ?', [username], one=True)
        userEnteredPasswordHash = hsh(password)
        dbPassword = user[2]
        if userEnteredPasswordHash == dbPassword:
            print("User Authentication Successful")
            response = jsonify(get_response(status_code=200, message="True"))
            response.status_code = 200
            return response
        else:
            print("User Authentication Error")
            response = jsonify(get_response(status_code=500, message="False"))
            response.status_code = 500
            return response

# function to add a follower to the following list
@app.route("/addFollower", methods=['POST'])
def addFollower():
    params = request.get_json()
    username = params.get('usernameAPI')
    username_following = params.get('usernameFollowingAPI')
    if not username or not username_following:
        return jsonify(get_response(status_code=409, message="username / username to following is not in request")), 409
    else:
        with sqlite3.connect("UsersMicroservice.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO Followers (username, usernamefollowing) VALUES (?,?)", (username, username_following))
            con.commit()
        msg = username+" started following "+username_following
        response = jsonify(get_response(status_code=201, message=msg))
        response.status_code = 201
        response.autocorrect_location_header = False
        return response

# function to remove a follower from folllowing list
@app.route("/removeFollower", methods=['DELETE'])
def removeFollower():
    params = request.get_json()
    username = params.get('usernameAPI')
    username_following = params.get('usernameFollowingAPI')
    if not username or not username_following:
        return jsonify(get_response(status_code=409, message="username / username to following is not in request")), 409
    else:    
        with sqlite3.connect("UsersMicroservice.db") as con:
            cur = con.cursor()
            cur.execute("DELETE FROM Followers WHERE username=? AND usernamefollowing=?", (username, username_following))
            con.commit()
        msg = username+" started unfollowing "+username_following
        response = jsonify(get_response(status_code=200, message=msg))
        response.status_code = 200
        response.autocorrect_location_header = False
        return response

if __name__ == "__main__":
    app.run(debug = True) 
