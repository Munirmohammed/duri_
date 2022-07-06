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

def initiate_auth(username:str, callback_url: str = 'http://nucleus.omic.ai:9001'):
    """ 
        Initiate Login flow. (AdminInitiateAuth)

        Ref: https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_AdminInitiateAuth.html 
        TODO:
            - find a way to mitigate cognito trigger not passing ClientMetadata to DefineAuthChallenge , 
              so that we can dynamically pass callbackUrl, 
              perhaps we can use oauth2.0 Authorization-code flow https://github.com/JinlianWang/aws-lambda-authentication-python/blob/master/app.py
    """
    client = boto3.client('cognito-idp', region_name=USER_POOL_REGION)
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
                        'url': callback_url
                    }
                    #, ContextData = {
                    #    'IpAddress': '154.159.254.180',
                    #    'ServerName': callback_url,
                    #    'ServerPath': '/login',
                    #    'HttpHeaders': [
                    #        {
                    #            'headerName': 'string',
                    #            'headerValue': 'string'
                    #        },
                    #    ],
                    #}
                )
    except client.exceptions.NotAuthorizedException:
        return None, "The username or password is incorrect"
    except client.exceptions.UserNotConfirmedException:
        return None, "User is not confirmed"
    except Exception as e:
        return None, e.__str__()
    return resp, None

def respond_auth_challenge(username, code, session):
    """ 
        respond to congito custom-auth challenge. (AdminRespondToAuthChallenge)

        Ref: https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_AdminInitiateAuth.html 
        TODO:
            - find a way to mitigate cognito trigger not passing ClientMetadata to DefineAuthChallenge , 
              so that we can dynamically pass callbackUrl, 
              perhaps we can use oauth2.0 Authorization-code flow https://github.com/JinlianWang/aws-lambda-authentication-python/blob/master/app.py
    """
    client = boto3.client('cognito-idp', region_name=USER_POOL_REGION)
    challenge_name = 'CUSTOM_CHALLENGE'
    #username = 'jimmyomicmd.com'
    #session = 'AYABeB5s1Jyc9ZjuTlJQHjaZbQEAHQABAAdTZXJ2aWNlABBDb2duaXRvVXNlclBvb2xzAAEAB2F3cy1rbXMAS2Fybjphd3M6a21zOnVzLXdlc3QtMjowMTU3MzY3MjcxOTg6a2V5LzI5OTFhNGE5LTM5YTAtNDQ0Mi04MWU4LWRkYjY4NTllMTg2MQC4AQIBAHilsueaVjl36QFS7NU43bur4uuZPopOR6FzLxgbQ6B97gHZiFxvPjBb4GjYeBHhOiL4AAAAfjB8BgkqhkiG9w0BBwagbzBtAgEAMGgGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMjfi0ncYrAZBPVEKNAgEQgDu-PFfwgnScQDEmBPlo1B01L5_mJBcQWYCdS7CkgUR1gT5XvWaDVlLJEkQDzZnGO7AjELcHW8DYa3_SSAIAAAAADAAAEAAAAAAAAAAAAAAAAADx4mA3aji_6iNdF64W5PMl_____wAAAAEAAAAAAAAAAAAAAAEAAAEE_drkpgswvFU5yckNApX-ji3bA2N_RCO1rChvKQvzskk-8a2T-tqFFpVC5qMBIgVJhstAAcv1THUTicCDqOZaH-_C_FuACB7lgI2SXYRpYHe_9sUZXBsWyRwfsf2drW5SigLnWZogil_OfW7he-gmYOmdi7DO3uGDHWM4fCSDzm6pGNXT7dCNx1rZjKLhehfQUSmBg0_QuSEnR6oSBB_SQHtOKKei-2JmsexaO4PS_hVRj4Vu6uIioer6JgkyxSgSPMDocxpQkFP9xmlf2iXvvldZoVM778gWhjXUkGHu6Wjh8uKAMxzRGzm2wLZ2cpPv1YNbFzVemjOvgcpdfL-q5HDuEut4ScGAOMGvw3YD0Zfw794y' 
    secret_hash = get_secret_hash(username)
    try:
        resp = client.admin_respond_to_auth_challenge(
                    UserPoolId = USER_POOL_ID,
                    ClientId = CLIENT_ID,
                    ChallengeName = challenge_name,
                    ChallengeResponses = {
                        'USERNAME': username,
                        'SECRET_HASH': secret_hash,
                        'ANSWER': code,
                    },
                    Session = session
                )
    except Exception as e:
        return None, e.__str__()
    return resp, None

def create_user(username, email):
    """ 
        Register a new user. (AdminCreateUser) 

        Ref: https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_AdminCreateUser.html
        
    """
    client = boto3.client('cognito-idp', region_name=USER_POOL_REGION)
    try:
        resp = client.admin_respond_to_auth_challenge(
                    UserPoolId = USER_POOL_ID,
                    #ClientId = CLIENT_ID,
                    Username = username,
                    UserAttributes = [
                        { 'Name': 'email', 'Value': email},
                        #{ 'Name': 'phone_number', 'Value': phone_number},
                    ],
                    DesiredDeliveryMediums = ['email'],
                    ClientMetadata = {
                        'string': 'string'
                    }
                )
    except Exception as e:
        return None, e.__str__()
    return resp, None

def create_group(name, description):
    """ 
        creates a new cognito group. (CreateGroup) 

        Groups map to workspaces in this api

        Ref: https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_CreateGroup.html
        
    """
    client = boto3.client('cognito-idp', region_name=USER_POOL_REGION)
    try:
        resp = client.create_group(
                    UserPoolId = USER_POOL_ID,
                    GroupName = name,
                    Description=description
                )
    except Exception as e:
        return None, e.__str__()
    return resp, None

def list_groups():
    """ 
        List all groups of a cognito-pool. (ListGroups) 

        Groups map to workspaces in this api

        Ref: https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_ListGroups.html
        
    """
    client = boto3.client('cognito-idp', region_name=USER_POOL_REGION)
    try:
        resp = client.list_groups(
                    UserPoolId = USER_POOL_ID,
                )
    except Exception as e:
        return None, e.__str__()
    return resp, None

