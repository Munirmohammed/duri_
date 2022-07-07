from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.dialects import postgresql as pg
from . import schema, tables
from .crud_base import CRUDBase


class User(CRUDBase):
    pass

class Workspace(CRUDBase):
    pass

class Team(CRUDBase):
    def filter_by(self, workspace_id: str = None, name: str = None, skip: int = 0, limit: int = 50) -> Optional[List]:
        db = self.db
        db_model = self.model
        query = db.query(db_model)
        if workspace_id:
            query = query.filter(db_model.workspace_id == workspace_id)
        if name:
            query = query.filter(db_model.name == name)
        if limit == 1:
            return query.first()
        else:
            query = query.order_by(db_model.name.asc()).offset(skip)
            return query.limit(limit).all()

class UserWorkspace(CRUDBase):
    def filter_by(self, user_id: str = None, workspace_id: str = None, skip: int = 0, limit: int = 50) -> Optional[List]:
        db = self.db
        db_model = self.model
        query = db.query(db_model)
        if user_id:
            query = query.filter(db_model.user_id == user_id)
        
        if workspace_id:
            query = query.filter(db_model.workspace_id == workspace_id)
        
        if limit == 1:
            return query.first()
        else:
            query = query.order_by(db_model.name.asc()).offset(skip)
            return query.limit(limit).all()