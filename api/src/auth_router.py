import os
import json
from datetime import datetime
from urllib.parse import urlparse
from pydantic import Json
from typing import Optional, List, Any, Dict, Union
from fastapi import APIRouter, Depends, Query, Path,  Form, File, UploadFile, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from .core import  deps, schema, crud, tables
from .services import cognito

router = APIRouter()

## User Authetication Routes

@router.post("/register", tags=["Auth"])
async def register():
    """
    Registers a new user
    """
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
    return None

