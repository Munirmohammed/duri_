import os
import json
from datetime import datetime
from urllib.parse import urlparse
from pydantic import Json
from typing import Optional, List, Any, Dict, Union
from fastapi import APIRouter, Depends, Query, Path, Header,  Form, File, UploadFile, HTTPException, BackgroundTasks
from starlette.status import HTTP_403_FORBIDDEN
from sqlalchemy.orm import Session
from .core import  deps, schema, crud, tables
from .core.config import settings
from .services import cognito

router = APIRouter()

## Workspaces management Routes
##  - Workspaces map to cognito-groups

@router.get("/workspace", response_model=List[schema.WorkspaceMini], tags=["Workspace"])
async def list_workspace(
    db: Session = Depends(deps.get_db),
):
    """
    List all available workspaces
    """
    ## TODO: add a background task that syncs with cognito groups
    crud_workspace = crud.Workspace(tables.Workspace, db)
    workspaces = crud_workspace.get_multi()
    return workspaces
    

@router.post("/workspace", tags=["Workspace"], response_model=schema.Workspace)
async def create_workspace(
    name: str = Form(..., description="the workspace name"),
    description: str = Form(..., description="the workspace description"),
    x_omic_userid: Union[str, None] = Header(default=None),
    db: Session = Depends(deps.get_db),
):
    """
    Creates a new workspace. 
    Note: a default team called 'default' will be created for this workspace
    """
    ## TODO: - get userid from access-token , x_omic_userid used temporary for now
    user_id = x_omic_userid or '9004ff5e-20bd-49dc-ba00-2f4dafac9940'

    crud_workspace = crud.Workspace(tables.Workspace, db)
    crud_team = crud.Team(tables.Team, db)
    crud_user_workspace = crud.UserWorkspace(tables.UserWorkspace, db)
    crud_user_team = crud.UserTeam(tables.UserTeam, db)

    workspace = crud_workspace.get_by_name(name)
    res, err = cognito.get_group(name)
    if res and workspace:
        raise HTTPException(status_code=400, detail="workspace exists")
    if not res and not err:
        ## group name does not exists, create it (sync with cognito groups)
        res, err = cognito.create_group(name, description)
        if err :
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='workspace creation failed.')
    if workspace:
        ## now throw if was synced and existed in the db
        raise HTTPException(status_code=400, detail="workspace exists")
    ## if not exist in db now add it to db
    group = res['Group'] #['GroupName']
    group_name = group['GroupName']
    group_desc = group['Description']
    group_create_date = group['CreationDate']
    group_mod_date = group['LastModifiedDate']
    db_obj = {
        'name': group_name,
        'creator_id': user_id, 
        'description': group_desc,
        'created_at':group_create_date,
        'updated_at':group_mod_date,
    }
    workspace = crud_workspace.create(db_obj)
    workspace_id = workspace.id

    ## create 'default' Team for this workspace
    team_obj = schema.TeamInsert(
        name=settings.default_team,
        workspace_id=workspace_id,
        description=settings.default_team_description,
        active=True,
        creator_id=user_id, 
    )
    team = crud_team.create(team_obj.dict(exclude_unset=True))
    team_id = team.id
    ## now relate the user to the workspace and team , with admin role
    user_workspace = crud_user_workspace.filter_by(user_id, workspace_id, limit=1)
    if not user_workspace:
        user_ws_obj = {
            'user_id': user_id,
            'workspace_id': workspace_id,
            'membership': 'admin', ## by default a user is added as a contributor to a workspace
        }
        user_workspace = crud_user_workspace.create(user_ws_obj)
    user_team = crud_user_team.filter_by(user_id, workspace_id, team_id=team_id, limit=1)
    if not user_team:
        user_team_obj = {
            'user_id': user_id,
            'workspace_id': workspace_id,
            'team_id': team_id,
            'membership': 'admin',
        }
        user_team = crud_user_team.create(user_team_obj)
    return workspace

@router.get("/workspace/{name}", response_model=schema.Workspace, tags=["Workspace"])
async def get_workspace(
    name: str = Path(..., description="workspace name"),
    db: Session = Depends(deps.get_db),
):
    """
    Get a Workspace 
    """
    ## TODO: check workspace exist in cognito groups in the background
    crud_workspace = crud.Workspace(tables.Workspace, db)
    workspace = crud_workspace.get_by_name(name)
    return workspace

@router.post("/workspace/{workspace_name}/team", response_model=schema.TeamBase, tags=["Workspace"])
async def create_team(
    workspace_name: str = Path(..., description="the workspace name"),
    name: str = Form(..., description="the team name"),
    description: str = Form(..., description="the team description"),
    x_omic_userid: Union[str, None] = Header(default=None),
    db: Session = Depends(deps.get_db),
):
    """
    Create Team in a workspace
    """
    ## TODO: 
    # - check group exist in cognito groups
    # - get userid from access-token , x_omic_userid used temporary for now
    user_id = x_omic_userid or '9004ff5e-20bd-49dc-ba00-2f4dafac9940'

    crud_workspace = crud.Workspace(tables.Workspace, db)
    crud_team = crud.Team(tables.Team, db)
    crud_user_team = crud.UserTeam(tables.UserTeam, db)

    workspace = crud_workspace.get_by_name(workspace_name)
    if not workspace:
        raise HTTPException(status_code=400, detail="workspace not exists")
    workspace_id = workspace.id
    team = crud_team.filter_by(workspace_id=workspace_id, name=name, limit=1)
    if team:
        raise HTTPException(status_code=400, detail="team already exists")
    team_obj = schema.TeamInsert(
        name=name,
        workspace_id=workspace_id,
        description=description,
        active=True,
        creator_id=user_id,
    )
    team = crud_team.create(team_obj.dict(exclude_unset=True))
    team_id = team.id
    user_team_obj = {
        'user_id': user_id,
        'workspace_id': workspace_id,
        'team_id': team_id,
        'membership': 'admin',
    }
    crud_user_team.create(user_team_obj)
    return team

@router.get("/workspace/{workspace_name}/users", response_model=List[schema.UserWorkspace], tags=["Workspace"])
async def get_workspace_users(
    workspace_name: str = Path(..., description="the workspace name"),
    db: Session = Depends(deps.get_db),
):
    """
    Get workspace users
    """
    crud_workspace = crud.Workspace(tables.Workspace, db)
    crud_user_workspace = crud.UserWorkspace(tables.UserWorkspace, db)
    workspace_obj = crud_workspace.get_by_name(workspace_name)
    if not workspace_obj:
        raise HTTPException(status_code=400, detail="workspace not exists")
    workspace_id = workspace_obj.id
    workspace_users = crud_user_workspace.filter_by(workspace_id=workspace_id)
    print(workspace_users)
    return workspace_users

@router.get("/workspace/{workspace_name}/team/{team_name}/users", response_model=List[schema.UserTeam], tags=["Workspace"])
async def get_team_users(
    workspace_name: str = Path(..., description="the workspace name"),
    team_name: str = Path(..., description="the team name"),
    db: Session = Depends(deps.get_db),
):
    """
    Get team users
    """
    crud_workspace = crud.Workspace(tables.Workspace, db)
    crud_team = crud.Team(tables.Team, db)
    crud_user_team = crud.UserTeam(tables.UserTeam, db)
    workspace_obj = crud_workspace.get_by_name(workspace_name)
    if not workspace_obj:
        raise HTTPException(status_code=400, detail="workspace not exists")
    workspace_id = workspace_obj.id
    team = crud_team.filter_by(workspace_id=workspace_id, name=team_name, limit=1)
    if not team:
        raise HTTPException(status_code=400, detail="team not exists")
    team_id = team.id
    team_users = crud_user_team.filter_by(workspace_id=workspace_id, team_id=team_id)
    print(team_users)
    return team_users