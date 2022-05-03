from flask import Flask, jsonify, request
import os
from flask_cors import CORS
import pymongo
from dotenv import load_dotenv
load_dotenv()
import jwt
import datetime
from user.user import user
from picture.picture import picture
from room.room import room

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.register_blueprint(user, url_prefix='/user')
app.register_blueprint(picture, url_prefix='/picture')
app.register_blueprint(room, url_prefix='/room')
mongo_user = os.getenv('MONGO_USER')
mongo_password = os.getenv('MONGO_PASSWORD')
mongo_connection_string = f'mongodb+srv://{mongo_user}:{mongo_password}@myowdatabase.zzqvy.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
mongoClient = pymongo.MongoClient(mongo_connection_string)
mongoDB = mongoClient["GoogleMeetClone"]

@app.route('/', methods=['GET'] )
def index():
    return 'Greetings from Google Meet Clone API!'



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    mongoCollection = mongoDB["users"]
    myquery = { "username": data['username'] }
    if mongoCollection.count_documents(myquery) != 0:
        res = mongoCollection.find_one(myquery)
        if res['password'] == data['password']:
            jwt_token = jwt.encode({'userId': res['_id'].__str__(),'username': data['username'], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=600)}, os.getenv('SECRET_KEY'), algorithm='HS256')
            return jsonify({ 
                "username": data['username'], 
                "userId": res['_id'].__str__(),
                "token": jwt_token,
                "avatar": res['avatar'],
                "name": res['name'],
                "email": res['email']
                }), 200
        else:
            return jsonify({ "message": "Invalid password" }), 404
    else:
        return jsonify({ "message": "User not found" }), 404

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    mongoCollection = mongoDB["users"]
    myquery = { "username": data['username'] }
    if mongoCollection.count_documents(myquery) != 0:
        return jsonify({ "message": "User already exists" }), 404
    else:
        res = mongoCollection.insert_one({
            "username": data['username'],
            "password": data['password'],
            "avatar": None,
            "name": None,
            "email": None
        })
        if res.inserted_id:
            return jsonify({ "message": "User created" }), 200
        else:
            return jsonify({ "message": "User not created" }), 404

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    #get bearer token
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
        decoded_token = jwt.decode(auth_token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
        print(decoded_token)
        now = datetime.datetime.utcnow()
        if decoded_token['exp'] < datetime.datetime.timestamp(now):
            return jsonify({ "message": "Token expired" }), 401
        else:
            return jsonify({ "message": "Token valid" }), 200
    else:
        return jsonify({ "message": "Token not found" }), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT'), debug=True)