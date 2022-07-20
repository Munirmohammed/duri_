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
async def register(
    username: str = Form(..., description="a username"),
    email: str = Form(..., description="an email"),
    first_name: str = Form(..., description="user first name"),
    last_name: str = Form(..., description="user last name"),
    bio: Optional[str] = Form(None, description="user last name"),
):
    """
    Registers a new user
    """
    res, err = cognito.create_user(username, email, first_name, last_name)
    print(res, err)
    if err :
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='registration error')
    return res

@router.post("/login", tags=["Auth"])
async def login(
    username: str = Form(..., description="email or username"), #  ie, jimmy@omicmd.com
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
    if err :
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='signin error')
    username = res['ChallengeParameters']['USERNAME']
    session = res['Session']
    resp = {
        'username': username,
        'session': session,
    }
    return resp

@router.post("/verify", tags=["Auth"])
async def verify(
    db: Session = Depends(deps.get_db),
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
    cognito_id_token = res['AuthenticationResult']['IdToken']
    refresh_token = res['AuthenticationResult']['RefreshToken']
    claims, err = jwt.decode_cognito_token(cognito_id_token)
    print('claims', claims)
    if err :
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='error decoding token')
    crud_user = crud.User(tables.User, db)
    crud_workspace = crud.Workspace(tables.Workspace, db)
    crud_team = crud.Team(tables.Team, db)
    crud_user_workspace = crud.UserWorkspace(tables.UserWorkspace, db)
    crud_user_team = crud.UserTeam(tables.UserTeam, db)
    username = claims['cognito:username']
    user_id = claims['sub']
    email = claims['email']
    groups = claims.get('cognito:groups', [])
    user = crud_user.get(user_id)
    if not user:
        attrs = ['email', 'sub']
        res, err = cognito.list_users(f'sub = "{user_id}"', attrs)
        cognito_user = res['Users'][0] if res and len(res['Users']) > 0 else None
        if cognito_user:
            #attr_dict = { cognito_user['Attributes'][i]['Name'] : cognito_user['Attributes'][i]['Value'] for i in range(0, len(cognito_user['Attributes']) ) } 
            db_obj = {
                'id': user_id ,
                'email': email ,
                'username': username ,
                'created_at': cognito_user['UserCreateDate'] ,
                'updated_at': cognito_user['UserLastModifiedDate'] ,
            }
            user = crud_user.create(db_obj)
    
    if  len(groups) == 0:
        ## add user to default group/workspace.
        cognito.add_user_to_group(username, settings.default_workspace)
        groups = [settings.default_workspace]
    ## sync cognito-user-groups with workspaces
    for group in groups:
        workspace = crud_workspace.get_by_name(group)
        if not workspace:
            res, err = cognito.get_group(group)
            if err:
                continue
            if res:
                cog_group = res['Group']
                db_obj = {
                    'name': cog_group['GroupName'],
                    'creator_id':settings.super_admin, ## TODO: replace with user-sub from token , the caller of this endpoint 
                    'description': cog_group['Description'],
                    'created_at':cog_group['CreationDate'],
                    'updated_at':cog_group['LastModifiedDate'],
                }
                workspace = crud_workspace.create(db_obj)
                team_obj = schema.TeamInsert(
                    name=settings.default_team,
                    workspace_id=workspace.id,
                    description=settings.default_team_description,
                    active=True,
                    creator_id=settings.super_admin, ## TODO
                )
                team = crud_team.create(team_obj.dict(exclude_unset=True))
        workspace_id = workspace.id
        user_workspace = crud_user_workspace.filter_by(user_id, workspace_id, limit=1)
        if not user_workspace:
            db_obj = {
                'user_id': user_id,
                'workspace_id': workspace_id,
                'membership': settings.default_membership_type,
            }
            user_workspace = crud_user_workspace.create(db_obj)
            default_team = crud_team.filter_by(workspace_id=workspace_id, name=settings.default_team, limit=1)
            team_id = default_team.id
            team_db_obj = {
                'user_id': user_id,
                'workspace_id': workspace_id,
                'team_id': team_id,
                'membership': settings.default_membership_type,
            }
            user_team = crud_user_team.create(team_db_obj)
    expires_delta = settings.passport_token_expire_mins
    now = datetime.utcnow()
    expire = now + timedelta(minutes=expires_delta)
    print(expire)
    data = schema.PassportVisaToken(
        iss = 'omic:duri',
        sub = claims['sub'],
        email = claims['email'],
        iat = claims['iat'], #now,
        exp = claims['exp'], # int(expire),
    )
    id_token = jwt.encode_passport_token(data.dict())
    resp = {
        'id_token': id_token,
        'token_type': 'bearer',
        'refresh_token': refresh_token,
        'user_attributes': {
            'sub': claims['sub'], 
            'email': claims['email'], 
            'username': username, 
            #email_verified: '', 
            #phone_number: ''
        }
    }
    return resp

@router.post("/token/renew", tags=["Auth"])
async def renew_token(
    db: Session = Depends(deps.get_db), 
):
    """
    renew a refresh token to get new  access_token
    """
    ## TODO:
    ##   - user provides the cognito refresh-token , use it to renew cognito login session and return DURI id-token 
    return None