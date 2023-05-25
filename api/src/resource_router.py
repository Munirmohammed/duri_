import os
import json
from datetime import datetime
from urllib.parse import urlparse
from pydantic import Json
from typing import Optional, List, Any, Dict, Union
from fastapi import APIRouter, Depends, Query, Path, Header, Form, HTTPException, BackgroundTasks
from starlette.status import HTTP_403_FORBIDDEN
from sqlalchemy.orm import Session
from .core import  deps, schema, crud, tables
from .core.config import settings
from .services import cognito

router = APIRouter()

@router.get("/resource", response_model=List[schema.Resource])
async def list_resources(
    auth_user: schema.UserProfile = Depends(deps.user_from_header),
    db: Session = Depends(deps.get_db),
):
    """
    List all available resources of the user workspace
    """
    workspace = auth_user.workspace
    crud_resource = crud.Resource(tables.Resource, db)
    resources = crud_resource.filter_by(workspace_id=workspace.id)
    return resources

@router.post("/resource", response_model=schema.Resource)
async def create_resource(
    auth_user: schema.UserProfile = Depends(deps.user_from_header),
    name: str = Form(..., description="name of resource"),
    type: str = Form(..., description="type of resource"),
    provider: str = Form(..., description="provider of resource"),
    cred_type: str = Form(..., description="type of credential"),
    cred: Json[Dict[str, Any]] = Form(..., description='key-value pair of cred values'),
    meta: Json[Dict[str, Any]] = Form(..., description='key-value pair'),
    db: Session = Depends(deps.get_db),
):
    """
    create a resource of the user workspace
    """
    workspace = auth_user.workspace
    crud_resource = crud.Resource(tables.Resource, db)
    crud_credential = crud.Credential(tables.Credential, db)
    # resources = crud_resource.filter_by(workspace_id=workspace.id)
    obj = schema.ResourceForm(
        name= name,
        type= type,
        provider= provider,
        meta= meta
    )
    resource = crud_resource.create(obj)
    if resource:
        cred_obj = {
            "resource_id": resource.id,
            "type": cred_type,
            "store": cred
        }
        crud_credential.create(cred_obj)
    return None

@router.post("/resource/{id}", response_model=schema.Resource)
async def create_resource(
    id: str = Path(..., description="resource id"),
    auth_user: schema.UserProfile = Depends(deps.user_from_header),
    db: Session = Depends(deps.get_db),
):
    """
    create a resource of the user workspace
    """
    return None
    workspace = auth_user.workspace
    crud_resource = crud.Resource(tables.Resource, db)
    resources = crud_resource.filter_by(workspace_id=workspace.id)
    return resources