from flask import Blueprint, jsonify, request
import os
from dotenv import load_dotenv
load_dotenv()
import jwt
import pymongo
import datetime
import functions as ftn
user = Blueprint('user', __name__)

mongo_user = os.getenv('MONGO_USER')
mongo_password = os.getenv('MONGO_PASSWORD')
mongo_connection_string = f'mongodb+srv://{mongo_user}:{mongo_password}@myowdatabase.zzqvy.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
mongoClient = pymongo.MongoClient(mongo_connection_string)
mongoDB = mongoClient["GoogleMeetClone"]

def checkToken(request):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
        decoded_token = jwt.decode(auth_token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
        now = datetime.datetime.utcnow()
        if decoded_token['exp'] < datetime.datetime.timestamp(now):
            return False
        else:
            return decoded_token
    else:
        return False

@user.route('/image', methods=['POST'])
def image():
    data = request.get_json()
    print(data)
    if checkToken(request):
        decoded_token = checkToken(request)
        mongoCollection = mongoDB["users"]
        mongoCollection.update_one(
            {'username': decoded_token['username']},
            {'$set': {'avatar': data['image']}}
        )
        return jsonify({
            "message": "Successfully updated image"
        }), 200
    else:
        return jsonify({
            "message": "Invalid token"
        }), 401
    

@user.route('/check', methods=['GET'])
def check():
    #get bearer token
    print("Checking")
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
        decoded_token = jwt.decode(auth_token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
        print(decoded_token)
        now = datetime.datetime.utcnow()
        if decoded_token['exp'] < datetime.datetime.timestamp(now):
            return jsonify({ "message": "Token expired" }), 401
        else:
            print("Token is valid")
            mongoCollection = mongoDB["users"]
            myquery = { "username": decoded_token['username'] }
            if mongoCollection.count_documents(myquery) != 0:
                res = mongoCollection.find_one(myquery)
                jwt_token = jwt.encode({'userId': res['_id'].__str__(),'username': decoded_token['username'], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=600)}, os.getenv('SECRET_KEY'), algorithm='HS256')
                return jsonify({
                    "username": decoded_token['username'],
                    "userId": res['_id'].__str__(),
                    "token": jwt_token,
                    "avatar": res['avatar'],
                    "name": res['name'],
                    "email": res['email']
                    }), 200
    else:
        return jsonify({ "message": "Token not found" }), 401

@user.route('/profilePicture/<username>', methods=['GET'])
def profilePicture(username):
    res = ftn.checkToken(request)
    print(res)
    if res['success']:
        mongoCollection = mongoDB["users"]
        myquery = { "username": username }
        if mongoCollection.count_documents(myquery) != 0:
            res = mongoCollection.find_one(myquery)
            return jsonify({
                "avatar": res['avatar']
            }), 200
        else:
            return jsonify({
                "message": "User does not exist"
            }), 404
    else:
        return jsonify({
            "message": res['message']
        }), 401

@user.route('/sendEmail', methods=['POST'])
def email():
    data = request.get_json()
    print(data)
    res = ftn.checkToken(request)
    if res['success']:
        decoded_token = checkToken(request)
        print(decoded_token)
        try:
            email_response = ftn.sendInvitationEmail(data['email'], 'Invitation for meeting!', data['message'], data['username'], data['roomLink'])
            print(email_response)
            return jsonify({
                "message": "Successfully sent email",
                'success': True
            }), 200
        except Exception as e:
            print(e)
            return jsonify({
                "message": e.__str__(),
                'success': False
            }), 201
    return jsonify({
        "message": "Successfully sent email"
    }), 200

@user.route('/check/available/<username>', methods=['GET'])
def checkAvailable(username):
    query = { "username": username }
    mongoCollection = mongoDB["users"]
    if mongoCollection.count_documents(query) != 0:
        return jsonify({
            "message": "Nombre de usuario no disponible",
            "available": False
        }), 200
    else:
        return jsonify({
            "message": "Nombre de usuario disponible",
            "available": True
        }), 200