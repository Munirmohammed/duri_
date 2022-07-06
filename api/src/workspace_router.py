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

@router.get("/workspace", tags=["Workspace"])
async def list_workspace():
    """
    List all available workspaces
    """
    res, err = cognito.list_groups()
    if err :
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='workspace retrival failed.')
    resp = res['Groups']
    return resp

@router.post("/workspace", tags=["Workspace"])
async def create_workspace(
    name: str = Form(..., description="the workspace name"),
    description: str = Form(..., description="the workspace description"),
):
    """
    Creates a new workspace
    """
    res, err = cognito.create_group(name, description)
    if err :
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='workspace creation failed.')
    resp = {
        'workspace': res['Group']['GroupName']
    }
    return resp
