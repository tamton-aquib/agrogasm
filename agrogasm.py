from flask import Flask
import json

app = Flask(__name__)

def stringify(obj) -> str: return json.dumps(obj)

@app.route("/")
def hello_world():
    return stringify({"nice": "Noice"})
