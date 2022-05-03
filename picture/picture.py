from flask import Blueprint, jsonify, request
from dotenv import load_dotenv
import os
import boto3
load_dotenv()

picture = Blueprint('picture', __name__)
s3_client = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
bucket = os.getenv('AWS_BUCKET')

@picture.route('/collection', methods=['GET'])
def get_collection():
    #Get files from folder of bucket
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix='pictures/')
    data = []
    for obj in response['Contents']:
        if obj['Key'] != 'pictures/':
            data.append({
                "url" : f'https://meet-clone-bucket.s3.amazonaws.com/{obj["Key"]}',
                "name" : 'asuna'
            })
    return jsonify({
        "data" : data
    }), 200