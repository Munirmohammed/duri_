from typing import Optional, List, Any, Dict, Union
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.services import cognito
from src.core import tables, deps, crud, schema


def get_user(db: Session, user_id: str) -> tables.User:
    crud_user = crud.User(tables.User, db)
    user = crud_user.get(user_id)
    if not user:
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
        user = crud_user.create(db_obj)
    if not user:
        raise HTTPException(status_code=400, detail="user not exists")
    return user

def get_user_workspaces(user: tables.User) -> List[schema.UserWorkspaceAssoc]:
    workspaces = []
    ## convert sqlchemy model to pydantic , see https://pydantic-docs.helpmanual.io/usage/models/#orm-mode-aka-arbitrary-class-instances
    for k in user.user_workspaces:
        w = schema.WorkspaceBase.from_orm(k.workspace).dict()
        w['membership']=k.membership
        workspaces.append(w)
    #print(workspaces)
    return workspaces

def get_user_teams(user: tables.User) -> List[schema.UserTeamAssoc]:
    active_team_id = user.active_team_id
    ## convert sqlchemy model to pydantic , see https://pydantic-docs.helpmanual.io/usage/models/#orm-mode-aka-arbitrary-class-instances
    teams = []
    for k in user.user_teams:
        t = schema.TeamMini.from_orm(k.team).dict()
        t['membership']=k.membership
        t['is_active']= str(t['id']) == str(active_team_id)
        t['workspace'] = k.team.workspace.name
        teams.append(t)
    return teams