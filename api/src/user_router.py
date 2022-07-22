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
from .core.config import settings
from .services import cognito

router = APIRouter()

## User management Routes

@router.post("/user/{user}/workspace", tags=["User"])
async def add_user_to_workspace_team(
    user: str = Path(..., description="the user-id"),
    workspace: str = Form(..., description="the workspace name"),
    team: Optional[str] = Form(settings.default_team, description="a team name within the workspace"),
    membership: str = Form(settings.default_membership_type, description="a the membership of the user in that team. ."),
    db: Session = Depends(deps.get_db),
):
    """
    Add user to a workspace and team.

    NOTE:
    Only users with `admin` membership to a workspace can add members to that workspace
    """
    ## TODO: 
    ##  - only admin workspace user can add a user to workspace
    crud_user = crud.User(tables.User, db)
    crud_workspace = crud.Workspace(tables.Workspace, db)
    crud_team = crud.Team(tables.Team, db)
    crud_user_workspace = crud.UserWorkspace(tables.UserWorkspace, db)
    crud_user_team = crud.UserTeam(tables.UserTeam, db)
    workspace_obj = crud_workspace.get_by_name(workspace)
    if not workspace_obj:
        raise HTTPException(status_code=400, detail="workspace not exists")
    user_obj = crud_user.get(user)

    if not user_obj:
        ## checks cognito for this user and create if not exists
        ## NOTE: to check for user existance in cognito-group use: "sub = \"{user}\""
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
    team_obj = crud_team.filter_by(workspace_id=workspace_id, name=team, limit=1)
    team_id = team_obj.id
    if not team_obj:
        ## ensure that the team exists before procedeeing
        raise HTTPException(status_code=400, detail="team not exists")
    res, err = cognito.list_user_groups(username)
    if err:
        raise HTTPException(status_code=400, detail="server error")
    user_groups = [x['GroupName'] for x in res['Groups']]
    if workspace_name not in user_groups:
        ## Adds user to that cognito-group if not added yet
        res, err = cognito.add_user_to_group(username, workspace_name)
        print(res, err)
        if err:
            raise HTTPException(status_code=400, detail="server error")
    user_workspace = crud_user_workspace.filter_by(user_id, workspace_id, limit=1)
    if user_workspace:
        raise HTTPException(status_code=400, detail="user exists in this workspace")
    db_obj = {
        'user_id': user_id,
        'workspace_id': workspace_id,
        #'team_id': team_id,
        'membership': settings.default_membership_type, ## by default a user is added as a contributor to a workspace
    }
    user_workspace = crud_user_workspace.create(db_obj)
    user_team = crud_user_team.filter_by(user_id, workspace_id, team_id=team_id, limit=1)
    if user_team:
        raise HTTPException(status_code=400, detail="user exists in this team")
    team_db_obj = {
        'user_id': user_id,
        'workspace_id': workspace_id,
        'team_id': team_id,
        'membership': membership,
    }
    user_team = crud_user_team.create(team_db_obj)
    #print(user_workspace)
    return team_db_obj

@router.get("/user/{user_id}/workspace", response_model=List[schema.UserWorkspaceAssoc], tags=["User"])
async def list_user_workspaces(
    user_id: str = Path(..., description="the user-id"),
    db: Session = Depends(deps.get_db),
):
    """
    List workspaces a user belongs to
    """
    ## TODO:
    crud_user = crud.User(tables.User, db)
    user = crud_user.get(user_id)
    print(user.workspaces)
    print(type(user.workspaces))
    res = []
    ## convert sqlchemy model to pydantic , see https://pydantic-docs.helpmanual.io/usage/models/#orm-mode-aka-arbitrary-class-instances
    for k, v in user.workspaces.items():
        print(k, v)
        w = schema.WorkspaceBase.from_orm(v).dict()
        w['membership']=k
        print(w)
        res.append(w)
    #res = list(user.workspaces)
    print(res)
    return res

@router.get("/user/{user_id}/team", response_model=List[schema.UserTeamAssoc], tags=["User"])
async def get_user_teams(
    user_id: str = Path(..., description="the user-id"),
    db: Session = Depends(deps.get_db),
):
    """
    List teams a user belongs to
    """
    ## TODO:
    crud_user = crud.User(tables.User, db)
    user = crud_user.get(user_id)
    #print(user.teams)
    res = []
    ## convert sqlchemy model to pydantic , see https://pydantic-docs.helpmanual.io/usage/models/#orm-mode-aka-arbitrary-class-instances
    for k, v in user.teams.items():
        print(k, v)
        w = schema.Team.from_orm(v).dict()
        w['membership']=k
        print(w)
        res.append(w)
    #res = list(user.teams)
    #print(type(res))
    return res