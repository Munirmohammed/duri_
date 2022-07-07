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
    db: Session = Depends(deps.get_db),
):
    """
    Add user to a workspace
    """
    ## TODO: - check user if pre-exists in the cognito group
    ##       - add user to cognito group
    crud_workspace = crud.Workspace(tables.Workspace, db)
    crud_user = crud.User(tables.User, db)
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
    workspace_id = workspace_obj.id
    user_workspace = crud_user_workspace.filter_by(user_id, workspace_id, limit=1)
    if user_workspace:
        raise HTTPException(status_code=400, detail="user exists in this workspace")
    db_obj = {
        'user_id': user_obj.id,
        'workspace_id': workspace_obj.id,
    }
    user_workspace = crud_user_workspace.create(db_obj)
    #print(user_workspace)
    return db_obj
    
