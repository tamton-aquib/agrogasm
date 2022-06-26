# import sys
from flask import Flask, jsonify
from flask_cors import cross_origin

# import pymongo

app = Flask(__name__)

# db_client = pymongo.MongoClient("mongodb://localhost:27017/")
# 
# if not "agrogasm" in db_client.list_database_names():
# print("db does not exist")
# sys.exit()

data = {
    "post": {
        "author": "taj",
        "title": "A Title",
        "description": "A nice description.",
        "upvote": 14, "downvote": 3,
        "comments": {
            "author": "nishoy",
            "description": "This is an informative post and it'll surely help in my cultivation.",
            "upvote": 1, "downvote": 3
        }
    },
    "global": {
        "threshold": 10
    }
}

@app.route("/", methods=["GET"])
@cross_origin()
def get_example():
    return jsonify(data=data)

