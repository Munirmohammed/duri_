from typing import Generator
from .db import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Query, Header, HTTPException, Depends
from . import crud_utils
from .schema import UserBase, UserProfile

class MySuperContextManager:
    def __init__(self):
        self.db = SessionLocal()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()

def get_db():
    with MySuperContextManager() as db:
        yield db
    """ try:
        db = SessionLocal()
        yield db
    finally:
        db.close() """
    
def user_from_query(
	userid: str = Query(None, description="The omic user-id."),
	db: Session = Depends(get_db),
)->UserProfile:
	if not userid:
		raise HTTPException(status_code=500, detail="require userid query param  ")
	user = crud_utils.get_user(db, userid)
	user_profile = UserBase.from_orm(user).dict()
	team = user.active_team
	user_profile['team'] = team
	user_profile['workspace'] = team.workspace
	return user_profile

def user_from_header(
	x_omic_userid: str = Header(None, description="The omic user-id."),
	db: Session = Depends(get_db),
)->UserProfile:
	user_id = x_omic_userid
	if not user_id:
		raise HTTPException(status_code=500, detail="require x_omic_userid query param  ")
	user = crud_utils.get_user(db, user_id)
	user_profile = UserBase.from_orm(user).dict()
	team = user.active_team
	user_profile['team'] = team
	user_profile['workspace'] = team.workspace
	return UserProfile(**user_profile)