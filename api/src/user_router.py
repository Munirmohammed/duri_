import os
import json
from datetime import datetime
from urllib.parse import urlparse
from pydantic import Json
from typing import Optional, List, Any, Dict, Union
from fastapi import APIRouter, Depends, Query, Path,  Form, File, UploadFile, HTTPException, BackgroundTasks
from starlette.status import HTTP_403_FORBIDDEN
from sqlalchemy.orm import Session
from .core import  deps, schema, crud, tables
from .services import cognito

router = APIRouter()

## User management Routes

@router.post("/user/workspace", tags=["User"])
async def add_user_to_workspace(
    user: str = Form(..., description="the user-id"),
    workspace: str = Form(..., description="the workspace name"),
    team: str = Form(..., description="a team name for a team within the workspace"),
    membership: str = Form('contributor', description="a the membership of the user in that workspace team. Only users with `admin` membership to a workspace can add members to that workspace."),
    db: Session = Depends(deps.get_db),
):
    """
    Add user to a workspace and team
    """
    ## TODO: 
    ##  - add user to team too
    crud_user = crud.User(tables.User, db)
    crud_workspace = crud.Workspace(tables.Workspace, db)
    crud_team = crud.Team(tables.Team, db)
    crud_user_workspace = crud.UserWorkspace(tables.UserWorkspace, db)
    workspace_obj = crud_workspace.get_by_name(workspace)
    if not workspace_obj:
        raise HTTPException(status_code=400, detail="workspace not exists")
    user_obj = crud_user.get(user)
    if not user_obj:
        ## TODO: check for user existance in cognito "sub = \"{user}\""
        attr = ['email', 'sub']
        res, err = cognito.list_users(f'sub = "{user}"', attr)
        print(res, err)
        if err:
            raise HTTPException(status_code=400, detail="user not exists")
        cognito_user = res['Users'][0] if len(res['Users']) > 0 else None
        if not cognito_user:
            raise HTTPException(status_code=400, detail="user not exists")
        attributes = { cognito_user['Attributes'][i]['Name'] : cognito_user['Attributes'][i]['Value'] for i in range(0, len(cognito_user['Attributes']) ) } 
        print(attributes)
        db_obj = {
            'id': attributes['sub'] ,
            'email': attributes['email'] ,
            'username': cognito_user['Username'] ,
            'created_at': cognito_user['UserCreateDate'] ,
            'updated_at': cognito_user['UserLastModifiedDate'] ,
        }
        user_obj = crud_user.create(db_obj)
    user_id = user_obj.id
    username = user_obj.username
    workspace_id = workspace_obj.id
    workspace_name = workspace_obj.name
    res, err = cognito.list_user_groups(username)
    if err:
        raise HTTPException(status_code=400, detail="server error")
    user_groups = [x['GroupName'] for x in res['Groups']]
    if workspace_name not in user_groups:
        res, err = cognito.add_user_to_group(username, workspace_name)
        print(res, err)
        if err:
            raise HTTPException(status_code=400, detail="server error")
    team_obj = crud_team.filter_by(workspace_id=workspace_id, name=team, limit=1)
    if not team_obj:
        raise HTTPException(status_code=400, detail="team not exists")
    team_id = team_obj.id
    user_workspace = crud_user_workspace.filter_by(user_id, workspace_id, team_id=team_id, limit=1)
    if user_workspace:
        raise HTTPException(status_code=400, detail="user exists in this workspace")
    db_obj = {
        'user_id': user_id,
        'workspace_id': workspace_id,
        'team_id': team_id,
        'membership': membership,
    }
    user_workspace = crud_user_workspace.create(db_obj)
    #print(user_workspace)
    return db_obj

@router.get("/user/workspace", tags=["User"])
async def get_user_workspaces(
    user: str = Form(..., description="the user-id"),
    db: Session = Depends(deps.get_db),
):
    """
    Get workspaces a user belongs to
    """
    ## TODO:
    return None