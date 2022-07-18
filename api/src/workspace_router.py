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
    db: Session = Depends(deps.get_db),
    name: str = Form(..., description="the workspace name"),
    description: str = Form(..., description="the workspace description"),
):
    """
    Creates a new workspace
    """
    crud_workspace = crud.Workspace(tables.Workspace, db)
    workspace = crud_workspace.get_by_name(name)
    res, err = cognito.get_group(name)
    if res and workspace:
        raise HTTPException(status_code=400, detail="workspace exists")
    if not res and not err:
        ## group name does not exists, create it.
        res, err = cognito.create_group(name, description)
        if err :
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='workspace creation failed.')
    group = res['Group'] #['GroupName']
    workspace = crud_workspace.get_by_name(group['GroupName'])
    if not workspace:
        db_obj = {
            'name': group['GroupName'],
            'creator_id':'9004ff5e-20bd-49dc-ba00-2f4dafac9940', ## TODO: replace with user-sub from token , the caller of this endpoint 
            'description': group['Description'],
            'created_at':group['CreationDate'],
            'updated_at':group['LastModifiedDate'],
        }
        workspace = crud_workspace.create(db_obj)
    
    return workspace

@router.get("/workspace/{name}", response_model=schema.Workspace, tags=["Workspace"])
async def get_workspace(
    name: str = Path(..., description="workspace name"),
    db: Session = Depends(deps.get_db),
):
    """
    Get a Workspace 
    """
    ## TODO: check group exist in cognito groups
    crud_workspace = crud.Workspace(tables.Workspace, db)
    workspace = crud_workspace.get_by_name(name)
    return workspace

@router.post("/workspace/{workspace_name}/team", response_model=schema.TeamBase, tags=["Workspace"])
async def create_team(
    workspace_name: str = Path(..., description="the workspace name"),
    name: str = Form(..., description="the team name"),
    description: str = Form(..., description="the team description"),
    db: Session = Depends(deps.get_db),
):
    """
    Create Team in a workspace
    """
    ## TODO: check group exist in cognito groups
    crud_workspace = crud.Workspace(tables.Workspace, db)
    crud_team = crud.Team(tables.Team, db)
    workspace_obj = crud_workspace.get_by_name(workspace_name)
    if not workspace_obj:
        raise HTTPException(status_code=400, detail="workspace not exists")
    workspace_id = workspace_obj.id
    team = crud_team.filter_by(workspace_id=workspace_id, name=name, limit=1)
    if team:
        raise HTTPException(status_code=400, detail="team already exists")
    team_obj = schema.TeamInsert(
        name=name,
        workspace_id=workspace_id,
        description=description,
        active=True,
        creator_id='9004ff5e-20bd-49dc-ba00-2f4dafac9940', ## TODO: replace with user-sub from token , the caller of this endpoint 
    )
    team = crud_team.create(team_obj.dict(exclude_unset=True))
    
    return team

@router.get("/workspace/{workspace_name}/team/{team_name}/users", response_model=List[schema.UserWorkspace], tags=["Workspace"])
async def get_team_users(
    workspace_name: str = Path(..., description="the workspace name"),
    team_name: str = Path(..., description="the team name"),
    db: Session = Depends(deps.get_db),
):
    """
    Get users of a workspace
    """
    crud_workspace = crud.Workspace(tables.Workspace, db)
    crud_team = crud.Team(tables.Team, db)
    crud_user_workspace = crud.UserWorkspace(tables.UserWorkspace, db)
    workspace_obj = crud_workspace.get_by_name(workspace_name)
    if not workspace_obj:
        raise HTTPException(status_code=400, detail="workspace not exists")
    workspace_id = workspace_obj.id
    team = crud_team.filter_by(workspace_id=workspace_id, name=team_name, limit=1)
    if not team:
        raise HTTPException(status_code=400, detail="team not exists")
    team_id = team.id
    workspace_users = crud_user_workspace.filter_by(workspace_id=workspace_id, team_id=team_id)
    print(workspace_users)
    return workspace_users