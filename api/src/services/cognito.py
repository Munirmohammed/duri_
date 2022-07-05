import boto3
import botocore.exceptions
import hmac
import hashlib
import base64
import json
from src.core.config import settings

boto3.set_stream_logger('')

USER_POOL_REGION = settings.user_pool_region
USER_POOL_ID = settings.user_pool_id
CLIENT_ID = settings.user_pool_client_id
CLIENT_SECRET = settings.user_pool_client_secret
PROVIDER = f'cognito-idp.{USER_POOL_REGION}.amazonaws.com/{USER_POOL_ID}'

def get_secret_hash(username):
    msg = username + CLIENT_ID
    dig = hmac.new(str(CLIENT_SECRET).encode('utf-8'),
    msg = str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
    d2 = base64.b64encode(dig).decode()
    return d2

def initiate_auth(username:str):
    """ 
        Initiate cognito Admin AdminInitiateAuth

        Ref: https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_AdminInitiateAuth.html
    """
    client = boto3.client(
        'cognito-idp',
        #aws_access_key_id="xxxxxxxxx",
        #aws_secret_access_key="xxxxxxxxx",
        #region_name="xxxxxxxxx"
    )
    secret_hash = get_secret_hash(username)
    try:
        resp = client.admin_initiate_auth(
                    UserPoolId = USER_POOL_ID,
                    ClientId = CLIENT_ID,
                    AuthFlow = 'CUSTOM_AUTH',
                    AuthParameters = {
                        'USERNAME': username,
                        'SECRET_HASH': secret_hash,
                    },
                    ClientMetadata = {
                        'username': username,
                    }
                )
    except client.exceptions.NotAuthorizedException:
        return None, "The username or password is incorrect"
    except client.exceptions.UserNotConfirmedException:
        return None, "User is not confirmed"
    except Exception as e:
        return None, e.__str__()
    return resp, None