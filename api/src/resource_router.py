import os
import json
from datetime import datetime
from urllib.parse import urlparse
from pydantic import Json
from typing import Optional, List, Any, Dict, Union
from fastapi import APIRouter, Depends, Query, Path, Header, Form, HTTPException, BackgroundTasks
from starlette.status import HTTP_403_FORBIDDEN
from sqlalchemy.orm import Session
from .core import deps, schema, crud, tables
from .core.config import settings
from .services import cognito, iam
import hashlib

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


@router.post("/resource")
async def create_resource(
    auth_user: schema.UserProfile = Depends(deps.user_from_header),
    name: str = Form(..., description="name of resource"),
    type: schema.ComputeType = Form(..., description="type of resource"),
    provider: schema.ProviderType = Form(
        schema.ProviderType.gitlab, description="provider of resource"),
    data: Json[Dict[str, Any]] = Form(...,
                                           description="if the resource is gitlab/github include a 'git_creds' key in the data and an 'access_token' key inside the 'git_creds' if the resource is aws include an 'aws_secret' key in data and specify the options as 'client_secret' and 'cross_account', if 'client_secret' make sure to pass 'access_key' and 'secret_key' and if 'cross_account' pass 'external_id' and 'role_arn'"),
    meta: Json[Dict[str, Any]] = Form(..., description='key-value pair'),
    db: Session = Depends(deps.get_db),
):
    """
    create a resource of the user workspace
    if the resource is gitlab/github include a "git_creds" key in the data and an "access_token" key inside the "git_creds"
    if the resource is aws include an "aws_secret" key in data and specify the option 
    as "client_secret" and "cross_account", if "client_secret" make sure to pass "access_key" and "secret_key"
    and if "cross_account" pass "external_id" and "role_arn"
    """
    workspace = auth_user.workspace
    crud_resource = crud.Resource(tables.Resource, db)
    crud_credential = crud.Credential(tables.Credential, db)
    cred = {}
    if "git_creds" in data:
        cred['access_token'] = data['git_creds']['access_token']
    if "aws_secret" in data:
        if data["aws_secret"]["aws_options"] is not None:
            aws_options = data["aws_secret"]["aws_options"]
        else:
            aws_options = 'client_secret'
        if aws_options == 'client_secret':
            if data["aws_secret"]["aws_key"] is None:
                raise HTTPException(
                    status_code=500, detail=f"please provide an aws_access_key and secret")
            services = iam.get_services(data["aws_secret"]["access_key"], data["aws_secret"]["secret_key"])
            hash_object = hashlib.sha256()
            hash_object.update(data["aws_secret"]["secret_key"].encode('utf-8'))
            hashed_secret = hash_object.hexdigest()
            cred['secret_key'] = hashed_secret
        if aws_options == 'cross_account':
            if data["aws_secret"]["external_id"] is None or data["aws_secret"]["role_arn"] is None:
                raise HTTPException(
                    status_code=500, detail=f"please provide external_id or role arn")
            access_key_id, secret_access_key, session_token = iam.assume_role(
                data["aws_secret"]["external_id"], data["aws_secret"]["role_arn"])
            services = iam.get_services(
                access_key_id, secret_access_key, session_token)
        meta['services'] = services
    # resources = crud_resource.filter_by(workspace_id=workspace.id)
    obj = schema.ResourceForm(
        name=name,
        type=type.value,
        user_id = auth_user.id,
        provider=provider.value,
        meta=meta
    )
    resource = crud_resource.create(obj)
    if resource:
        cred_obj = schema.CredentialsForm(
            resource_id= resource.id,
            type= type.value,
            store= cred
        )
        crud_credential.create(cred_obj)
    return resource.id


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
