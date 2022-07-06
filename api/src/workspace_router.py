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

@router.get("/workspace", response_model=List[schema.Workspace], tags=["Workspace"])
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
