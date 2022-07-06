import os
import json
from datetime import datetime, timedelta
from urllib.parse import urlparse
from pydantic import Json
from typing import Optional, List, Any, Dict, Union
from fastapi import APIRouter, Depends, Query, Path,  Form, File, UploadFile, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from starlette.status import HTTP_403_FORBIDDEN
from .core import  deps, schema, crud, tables, jwt
from.core.config import settings
from .services import cognito

router = APIRouter()

## User Authetication Routes

@router.post("/register", tags=["Auth"])
async def register():
    """
    Registers a new user
    """
    #token = 'eyJraWQiOiJBcnhnMGExY1czMWMzbjhpUVdhYzZ1NldRMkNSa2VxOFYrZzY1eWsrZ1NVPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI5MDA0ZmY1ZS0yMGJkLTQ5ZGMtYmEwMC0yZjRkYWZhYzk5NDAiLCJjb2duaXRvOmdyb3VwcyI6WyJvbWljLmFpIl0sImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtd2VzdC0yLmFtYXpvbmF3cy5jb21cL3VzLXdlc3QtMl9nWTRWQ1NYTGkiLCJjb2duaXRvOnVzZXJuYW1lIjoiamltbXlvbWljbWQuY29tIiwiZ2l2ZW5fbmFtZSI6ImppbW15Iiwib3JpZ2luX2p0aSI6ImYxNDQ5YTA3LTllNWUtNDM5OS1hNmNmLTczNjY3ZWRkODNjZSIsImF1ZCI6IjFvZmRqMTk3NDhyazl2MGFwNjBobnEzODVyIiwiZXZlbnRfaWQiOiI3MDBjNDgyZC03NGRjLTRmMzctOGQxZC01M2UyOGIwYTIyNWYiLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTY1NzA1Mzg4MSwiZXhwIjoxNjU3MDU3NDgxLCJpYXQiOjE2NTcwNTM4ODEsImZhbWlseV9uYW1lIjoiY2xpZmYiLCJqdGkiOiJmM2ZhMzg1OC1hN2EyLTQ1ZWItOTE5MS03MDlkYzJjYmI2NTYiLCJlbWFpbCI6ImppbW15QG9taWNtZC5jb20ifQ.HlyGVOe55QvMlha8t7jF1vi8Djsn4fZYnNqaPg2-xVEo8g7qvUCyl4GvaEO-q-oa_ojU7m2Phea5yYHzr-g8VcODIpkyW6cJ43FqAInH67_nL_X3JmxfSQeaF05imVrPoUqbJ854yypLC7fgiku5LsZmOiovbj_HYqBJKE-E3XBBHL5brotd1vfHm-BwwvO26toQ32p-Gu3T-f9yWZvFXyHtdFUYjty0uuoN6CGVSsf4SMKFEASxOrYsz--3A1cLB61dtzny-TsyPVE_4XC0HScP8dT93cqqA9b93TKtMIy0voNWqqb27bkltkjw66n0xTH6-upJSCGwXlvvMq_HaQ'
    #res, err = jwt.decode_cognito_token(token)
    #print(res, err)
    return None

@router.post("/login", tags=["Auth"])
async def login(
    username: str = Form(..., description="username or email"), #  ie, jimmy@omicmd.com
    #callback_url: str = Form('http://nucleus.omic.ai:9001', description="the url that will be used in the verify email where verification code will be appended to."), # ie, http://nucleus.omic.ai:9001/
):
    """
    Initiates a user authetication flow
    """
    ## implemenation links:
    ##   - https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-authentication-flow.html#amazon-cognito-user-pools-server-side-authentication-flow
    ##   - https://github.com/boto/boto3/issues/2745#issuecomment-773021989
    res, err = cognito.initiate_auth(username)
    print(res, err)
    username = res['ChallengeParameters']['USERNAME']
    session = res['Session']
    resp = {
        'username': username,
        'session': session,
    }
    return resp

@router.post("/verify", tags=["Auth"])
async def verify(
    username: str = Form(..., description="the actual username"), 
    code: str = Form(..., description="the verification code in the email"), 
    session: str = Form(..., description="the session response retrieved from login"), 
):
    """
    Finalizes user authetication flow  by verifying the login-link code sent to user email.
    It returns an Id token on success
    """
    res, err = cognito.respond_auth_challenge(username, code, session)
    print(res, err)
    if err :
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='error verifying code')
    id_token = res['AuthenticationResult']['IdToken']
    refresh_token = res['AuthenticationResult']['RefreshToken']
    claims, err = jwt.decode_cognito_token(id_token)
    if err :
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='error decoding token')
    expires_delta = settings.passport_token_expire_mins
    now = datetime.utcnow()
    expire = now + timedelta(minutes=expires_delta)
    data = schema.PassportVisaToken(
        iss = 'omic:duri',
        sub = claims['sub'],
        email = claims['email'],
        iat = now,
        exp = expire,
    )
    token = jwt.encode_passport_token(data.dict())
    return {
        'access_token': token,
        'refresh_token': refresh_token,
    }

