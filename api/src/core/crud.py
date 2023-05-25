from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.dialects import postgresql as pg
from . import schema, tables
from .crud_base import CRUDBase
from sqlalchemy import desc

class User(CRUDBase):
	def get_by_username(self, username: str) -> tables.User:
		db = self.db
		return db.query(self.model).filter(self.model.username == username).first()
		
	def get_by_email(self, email: str) -> tables.User:
		db = self.db
		return db.query(self.model).filter(self.model.email == email).first()
	
	def set_active_team(self, user_id: str, team_id: str) -> tables.User:
		db = self.db
		user = self.get(user_id)
		user.active_team_id = team_id
		db.add(user)
		db.commit()
		db.refresh(user)
		return user

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
			query = query.order_by(db_model.created_at.asc()).offset(skip)
			return query.limit(limit).all()
class UserTeam(CRUDBase):
	def filter_by(self, user_id: str = None, workspace_id: str = None, team_id: str = None, skip: int = 0, limit: int = 50) -> Optional[List]:
		db = self.db
		db_model = self.model
		query = db.query(db_model)
		if user_id:
			query = query.filter(db_model.user_id == user_id)
		
		if workspace_id:
			query = query.filter(db_model.workspace_id == workspace_id)

		if team_id:
			query = query.filter(db_model.team_id == team_id)
		
		if limit == 1:
			return query.first()
		else:
			query = query.order_by(db_model.created_at.asc()).offset(skip)
			return query.limit(limit).all()
	
class Notification(CRUDBase):
	def get_latest(self):
		db = self.db
		db_model = self.model
		return db.query(db_model).order_by(desc(db_model.created_at)).limit(20).all()

class Resource(CRUDBase):
	def filter_by(self, workspace_id: str = None, skip: int = 0, limit: int = 50) -> Optional[List]:
		db = self.db
		db_model = self.model
		query = db.query(db_model)
		if workspace_id:
			query = query.filter(db_model.workspace_id == workspace_id)
			
		if limit == 1:
			return query.first()
		else:
			query = query.order_by(db_model.created_at.asc()).offset(skip)
			return query.limit(limit).all()


class Credential(CRUDBase):
	pass