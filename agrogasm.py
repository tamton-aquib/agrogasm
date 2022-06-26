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
    "posts": [
        {
            "pid": 0,
            "author": "taj",
            "title": "A Title",
            "description": "A nice description.",
            "upvote": 420, "downvote": 0,
            "comments": {
                "author": "nishoy",
                "description": "This is an informative post and it'll surely help in my cultivation.",
                "upvote": 1, "downvote": 3
            }
        },
        {
            "pid": 1,
            "author": "nishoy",
            "title": "A second Title",
            "description": "Another nice description.",
            "upvote": 69, "downvote": 17,
            "comments": {
                "author": "rashid",
                "description": "Dude this is boring af.",
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
def get_example():
    return jsonify(data=data)

