from . import app
import os
import json
import pymongo
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401
from pymongo import MongoClient
from bson import json_util
from pymongo.errors import OperationFailure
from pymongo.results import InsertOneResult
from bson.objectid import ObjectId
import sys


SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "songs.json")
songs_list: list = json.load(open(json_url))

# client = MongoClient(
#     f"mongodb://{app.config['MONGO_USERNAME']}:{app.config['MONGO_PASSWORD']}@localhost")
mongodb_service = os.environ.get('MONGODB_SERVICE')
mongodb_username = os.environ.get('MONGODB_USERNAME')
mongodb_password = os.environ.get('MONGODB_PASSWORD')
mongodb_port = os.environ.get('MONGODB_PORT')

print(f'The value of MONGODB_SERVICE is: {mongodb_service}')

if mongodb_service == None:
    app.logger.error('Missing MongoDB server in the MONGODB_SERVICE variable')
    # abort(500, 'Missing MongoDB server in the MONGODB_SERVICE variable')
    sys.exit(1)

if mongodb_username and mongodb_password:
    url = f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_service}"
else:
    url = f"mongodb://{mongodb_service}"


print(f"connecting to url: {url}")

try:
    client = MongoClient(url)
except OperationFailure as e:
    app.logger.error(f"Authentication error: {str(e)}")

db = client.songs
db.songs.drop()
db.songs.insert_many(songs_list)

def parse_json(data):
    return json.loads(json_util.dumps(data))

######################################################################
# INSERT CODE HERE
######################################################################

@app.route("/health")
def health():
    return {"status":"OK"}, 200


@app.route("/count")
def count():
    count = db.songs.count_documents({})
    return {"count": f"{count}"}, 200

# @app.route("/song", methods=['GET'])
# def songs():
#     songs = db.songs.find({})
#     songs_list = []
#     for song in songs:
#         song['_id'] = str(song['_id'])
#         songs_list.append(song)
#     response = {"songs": songs_list}
#     return (response), 200

@app.route("/song", methods=['GET'])
def songs():
    songs = list(db.songs.find({}))
    return {"songs": parse_json(songs)}, 200

@app.route("/song/<int:id>")
def get_song_by_id(id):

    docs = db.songs.find_one({"id": id})
    if not docs:
        return {"message": f"song with {id} not found"}
    return parse_json(docs), 200


@app.route("/song", methods=['POST'])
def create_song():
    post_data = request.json
    song = db.songs.find_one({"id": post_data["id"]})
    if song:
        return {"Message": f"song with id {song['id']} already present"}, 302
    Result = db.songs.insert_one(post_data)
    #return {"inserted id":parse_json(post_data)}
    return {"inserted id": parse_json(insert_one.inserted_id)}, 201

@app.route("/song/<int:id>", methods=['PUT'])
def update_songs(id):
    updated_song = request.json
    song = db.songs.find_one({"id":id})
    if not song:
        return {"message": "song not found"}, 404
    
    Result = db.songs.update_one({"id": id}, {"$set": updated_song})
    return {"_id": parse_json(updated_song)}, 200

@app.route("/song/<int:id>", methods=['DELETE'])
def delete_song(id):
    id = request.json.get('id')
    print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
    print(id)
