import datetime
import jwt
import os
from dotenv import load_dotenv
import boto3
load_dotenv()

def checkToken(request):
    auth_header = request.headers.get('Authorization')
    print(auth_header)
    if auth_header:
        try:
            auth_token = auth_header.split(" ")[1]
            decoded_token = jwt.decode(auth_token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
            now = datetime.datetime.utcnow()
            if decoded_token['exp'] < datetime.datetime.timestamp(now):
                return {
                    "message": "Token expired",
                    "success": False
                }
            else:
                return {
                    "message": "Token is valid",
                    "success": True,
                    "data": decoded_token
                }
        except Exception as e:
            return {
                "message": "Invalid token becauser of exception",
                "success": False
            }
    else:
        return {
            "message": "There is no token",
            "success": False
        }

def sendInvitationEmail(email, subject, message, username, invitationLink):
    sesClient = boto3.client('ses', region_name='us-east-1', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
    #Send invitation email
    header = "<html><head></head><body><center><h1></h1>"

    body = """
        <html>
        <head>Google Meet Clone!</head>
        <body>
        <p>Hola,</p>
        <p>Has sido invitado a una reunion, por: {}</p>
        <p>Puedes unirte a la reunion dando click en el siguiente enlace:</p>
        <p><a href="{}">Unirte</a></p>
        <p>Mensaje:</p>
        <p>{}</p>
        <p>Saludos</p>
        <img src='https://meet-clone-bucket.s3.amazonaws.com/pictures/188268641_169855451752565_4378491616271669482_n.jpg' alt='this is fine gifs'/>
        </body>
        </html>
    """.format(username, invitationLink, message)
    response = sesClient.send_email(
        Destination={
            'ToAddresses': [
                email,
            ],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': body
                }
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': subject
            },
        },
        Source=os.getenv('SENDER_EMAIL'),
        ReplyToAddresses=[
            os.getenv('SENDER_EMAIL')
        ],
    )
    return response