# import sys
from flask import Flask, jsonify
from flask_cors import cross_origin

# import pymongo
# from flask_pymongo import PyMongo

app = Flask(__name__)

# mongodb_client = PyMongo(app, uri="mongodb://localhost:27017/todo_db")
# db = mongodb_client.db

# db_client = pymongo.MongoClient("mongodb://localhost:27017/")
# if not "agrogasm" in db_client.list_database_names():
# print("db does not exist")
# sys.exit()

data = {
    "posts": [
        {
            "pid": 0,
            "author": "taj",
            "title": "November: Time for spinach.",
            "description": "Time for spinach is november",
            "upvote": 420, "downvote": 0,
            "reliability": "reliable",
            "comments": {
                "author": "nishoy",
                "description": "This is an informative post and it'll surely help in my cultivation.",
                "upvote": 1, "downvote": 3
            }
        },
        {
            "pid": 1,
            "author": "nishoy",
            "title": "Free tomato seeds distribution",
            "description": "Tomato seeds distribution at KB",
            "upvote": 69, "downvote": 17,
            "reliability": "unsure",
            "comments": {
                "author": "rashid",
                "description": "Dude this is boring af.",
                "upvote": 4, "downvote": 0
            }
        },
        {
            "pid": 2,
            "author": "aflah",
            "title": "A third Title",
            "description": "Probably a nice description.",
            "upvote": 8, "downvote": 23,
            "reliability": "unreliable",
            "comments": {
                "author": "taj",
                "description": "Fake news",
                "upvote": 4, "downvote": 0
            }
        },
    ],
    "global": {
        "threshold": 10
    }
}

@app.route("/", methods=["GET"])
@cross_origin()
def get_init_data():
    return jsonify(data=data)

@app.route("/community/new", methods=["GET"])
@cross_origin()
def add():
    return jsonify(message="Done")
