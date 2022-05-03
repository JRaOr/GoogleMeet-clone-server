from flask import Blueprint, jsonify, request
from dotenv import load_dotenv
import os
import boto3
from functions import checkToken
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
import random
import string

load_dotenv()

room = Blueprint('room', __name__)

twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
twilio_api_key_sid = os.environ.get('TWILIO_API_KEY_SID')
twilio_api_key_secret = os.environ.get('TWILIO_API_KEY_SECRET')

@room.route('/create', methods=['GET'])
def create():
    res = checkToken(request)
    if res['success']:
        #Generate random room name
        room_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        return jsonify({
            "message": "Successfully created room",
            "room_name": room_name
        }), 200
    else:
        return jsonify({
            "message": res['message'] 
        }), 401

@room.route('/join/<roomId>', methods=['GET'])
def join(roomId):
    print(roomId)
    res = checkToken(request)
    if res['success']:
        token = AccessToken(twilio_account_sid, twilio_api_key_sid,
                        twilio_api_key_secret, identity=res['data']['username'],
                        ttl=3600)
        token.add_grant(VideoGrant(room=roomId))
        return jsonify({
            "message": "Successfully joined room",
            "token": token.to_jwt()
        }), 200
    else:
        return jsonify({
            "message": res['message'] 
        }), 401