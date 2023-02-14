import os
import json
from datetime import datetime
from urllib.parse import urlparse
from pydantic import Json
from typing import Optional, List, Any, Dict, Union
from fastapi import APIRouter, Depends, Query, Header, Path,  Form, File, UploadFile, HTTPException, BackgroundTasks
from starlette.status import HTTP_403_FORBIDDEN
from sqlalchemy.orm import Session
from .core import  deps, schema, crud, tables, crud_utils
from .core.config import settings
from .services import cognito

router = APIRouter()

## User management Routes
@router.post("/user/profile", response_model=schema.UserProfile, tags=["User"])
async def get_user_profile(
    x_omic_userid: Union[str, None] = Header(default=None, description="the user-id from header (temporary)"),
):
    """
    Get user profile
    """
    user_id = x_omic_userid
    user = crud_utils.get_user(user_id)
    #teams = crud_utils.get_user_teams(user)
    #user_profile = schema.UserBase.from_orm(user).dict()
    user_profile = schema.UserBase.from_orm(user).dict()
    team = user.active_team
    user_profile['team'] = team
    user_profile['workspace'] = team.workspace
    return user_profile

@router.post("/user/workspace", tags=["User"])
async def switch_user_workspace_team(
    #user_id: str = Path(..., description="the user-id"),
    x_omic_userid: Union[str, None] = Header(default=None, description="the user-id from header (temporary)"),
    workspace: str = Form(..., description="the workspace name"),
    team: Optional[str] = Form(settings.default_team, description="a team name within the workspace"),
    membership: Optional[str] = Form(settings.default_membership_type, description="a the membership of the user in that team. ."),
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

    # some defaults
    if not team:
        team = settings.default_team
    if not membership:
        team = settings.default_membership_type

    user = crud_utils.get_user(x_omic_userid)
    user_id = user.id
    username = user.username
    workspace_obj = crud_workspace.get_by_name(workspace)
    if not workspace_obj:
        raise HTTPException(status_code=400, detail="workspace not exists")
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
    if not user_workspace:
        #raise HTTPException(status_code=400, detail="user exists in this workspace")
        db_obj = {
            'user_id': user_id,
            'workspace_id': workspace_id,
            #'team_id': team_id,
            'membership': settings.default_membership_type, ## by default a user is added as a contributor to a workspace
        }
        user_workspace = crud_user_workspace.create(db_obj)
    user_team = crud_user_team.filter_by(user_id, workspace_id, team_id=team_id, limit=1)
    if not user_team:
        #raise HTTPException(status_code=400, detail="user exists in this team")
        team_db_obj = {
            'user_id': user_id,
            'workspace_id': workspace_id,
            'team_id': team_id,
            'membership': membership,
        }
        user_team = crud_user_team.create(team_db_obj)
    #if not user.active_team_id:
    # set as active team
    user = crud_user.set_active_team(user_id, team_id)
    #print(user_workspace)
    return team_db_obj

@router.get("/user/workspaces", response_model=List[schema.UserWorkspaceAssoc], tags=["User"])
async def list_user_workspaces(
    x_omic_userid: Union[str, None] = Header(default=None, description="the user-id from header (temporary)"),
    db: Session = Depends(deps.get_db),
):
    """
    List workspaces a user belongs to
    """
    user = crud_utils.get_user(x_omic_userid)
    user_workspaces = crud_utils.get_user_workspaces(user)
    return user_workspaces
    

@router.get("/user/teams", response_model=List[schema.UserTeamAssoc], tags=["User"])
async def get_user_teams(
    x_omic_userid: Union[str, None] = Header(default=None, description="the user-id from header (temporary)"),
    db: Session = Depends(deps.get_db),
):
    """
    List teams a user belongs to
    """
    user = crud_utils.get_user(x_omic_userid)
    user_teams = crud_utils.get_user_teams(user)
    return user_teams