from datetime import datetime
from email.policy import default
from sqlalchemy import Table, Column, Integer, BigInteger, String, ForeignKey, DateTime, JSON, TEXT, Boolean, Text
from sqlalchemy.orm import relationship, backref, synonym
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.dialects.postgresql import UUID, ENUM, ARRAY
from sqlalchemy.schema import Sequence
from sqlalchemy.sql import func
from uuid import uuid4
#from sqlalchemy.sql.sqltypes import Boolean
from .db import Base
#from .schema import Visibility, Nb_Category

""" 
	Notes:
		-  https://docs.sqlalchemy.org/en/14/orm/extensions/associationproxy.html#simplifying-association-objects
"""

class User(Base):
	__tablename__ = 'user'
	id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
	email = Column(String, unique=True, nullable=False)
	username = Column(String, unique=True, nullable=False)
	active_team_id = Column(UUID(as_uuid=True), ForeignKey('team.id'), nullable=True)
	active_project_id = Column(String, ForeignKey('project.id'), nullable=True)
	created_at = Column(DateTime(timezone=True), nullable=False)
	updated_at = Column(DateTime(timezone=True), nullable=True)
	active_team = relationship("Team")
	project = relationship("Project", backref="user", uselist=False)
	#teams = association_proxy("user_teams", "team")
	#workspaces = association_proxy("user_workspaces", "workspace")
	user_workspaces = relationship(
		"UserWorkspace",
		back_populates="user",
		#collection_class=attribute_mapped_collection("membership"),
		cascade="all, delete-orphan",
	)
	user_teams = relationship(
		"UserTeam",
		back_populates="user",
		#collection_class=attribute_mapped_collection("membership"),
		cascade="all, delete-orphan",
	)
	workspaces = association_proxy(
		"user_workspaces", 
		"workspace",
		#creator=lambda k, v: UserWorkspace(membership=k, workspace=v),
	)
	teams = association_proxy(
		"user_teams", 
		"team",
		#creator=lambda k, v: UserTeam(membership=k, team=v),
	)
	resources = relationship("Resource", backref="user", cascade="all, delete-orphan")
	#team = synonym('active_team')

class Workspace(Base):
	__tablename__ = 'workspace'
	id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid4)
	name = Column(String, unique=True, nullable=False)
	creator_id = Column(String, nullable=False)
	active = Column(Boolean, nullable=False, default=True)
	description = Column(String, nullable=True)
	tags = Column(ARRAY(String), nullable=True)
	avatar = Column(String, nullable=True)
	ui_customization = Column(JSON, nullable=True)
	created_at = Column(DateTime(timezone=True), nullable=False)
	updated_at = Column(DateTime(timezone=True), nullable=True)
	teams = relationship("Team", back_populates="workspace", cascade="all, delete-orphan")
	projects = relationship("Project", backref="workspace", cascade="all, delete-orphan")

class Team(Base):
	__tablename__ = 'team'
	id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid4)
	name = Column(String, nullable=False)
	workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'), nullable=False)
	creator_id = Column(String, nullable=False)
	active = Column(Boolean, nullable=False)
	description = Column(String, nullable=True)
	tags = Column(ARRAY(String), nullable=True)
	avatar = Column(String, nullable=True)
	ui_customization = Column(JSON, nullable=True)
	created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
	updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=True)
	workspace = relationship("Workspace", back_populates="teams")

class UserWorkspace(Base):
	__tablename__ = 'user_workspace'
	user_id = Column(UUID(as_uuid=True),  ForeignKey('user.id'), primary_key=True, nullable=False)
	workspace_id = Column(UUID(as_uuid=True),  ForeignKey('workspace.id'), primary_key=True, nullable=False)
	#team_id = Column(UUID(as_uuid=True),  ForeignKey('team.id'), nullable=True)
	membership = Column(String, nullable=True, default='contributor')
	created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
	#user = relationship(User, backref=backref("user_workspaces"))
	user = relationship(
		User,
		#backref=backref("user_workspaces")
		back_populates="user_workspaces",
	)
	workspace = relationship("Workspace")
	""" def __init__(self, user_id=None, workspace_id=None, membership=None, created_at=None):
		self.user_id = user_id
		self.workspace_id = workspace_id
		self.membership = membership
		self.created_at = created_at """

class UserTeam(Base):
	__tablename__ = 'user_team'
	user_id = Column(UUID(as_uuid=True),  ForeignKey('user.id'), primary_key=True, nullable=False)
	workspace_id = Column(UUID(as_uuid=True),  ForeignKey('workspace.id'), primary_key=True, nullable=False)
	team_id = Column(UUID(as_uuid=True),  ForeignKey('team.id'), primary_key=True, nullable=False)
	membership = Column(String, nullable=True, default='contributor')
	created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
	#user = relationship(User, backref=backref("user_teams"))
	user = relationship(
		User,
		back_populates="user_teams",
	)
	team = relationship("Team")
	""" def __init__(self, user_id=None, workspace_id=None, team_id=None, membership=None, created_at=None):
		self.user_id = user_id
		self.workspace_id = workspace_id
		self.team_id = team_id
		self.membership = membership
		self.created_at = created_at """

class Notification(Base):
	__tablename__ = "notification"
	id = Column(UUID(as_uuid=True), unique=True, nullable=False, primary_key=True,  default=uuid4)
	data = Column(JSON, nullable=False)
	workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'), nullable=False)
	created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

	
class Resource(Base):
	__tablename__ = "resource"
	id = Column(UUID(as_uuid=True), unique=True, nullable=False, primary_key=True,  default=uuid4)
	user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
	name = Column(String, nullable=False)
	type = Column(String, nullable=False)
	provider = Column("provider", String(), nullable=False)
	#subtype = Column(String, nullable=False)
	#subtype = Column(String, nullable=False)
	credential = relationship("Credential", uselist=False, back_populates="resource")
	meta = Column(JSON, nullable=False)
	created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
	updated_at = Column(DateTime(timezone=True), nullable=True)

class Credential(Base):
	__tablename__ = "credential"
	id = Column(UUID(as_uuid=True), unique=True, nullable=False, primary_key=True,  default=uuid4)
	resource_id = Column('resource_id', UUID(as_uuid=True), ForeignKey('resource.id'), nullable=False)
	resource = relationship("Resource", back_populates="credential")
	# workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'), nullable=False)
	# name = Column(String, nullable=False)
	type = Column(String, nullable=False)
	#config = Column(JSON, nullable=False)
	store = Column(Text, nullable=False)
	created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
	updated_at = Column(DateTime(timezone=True), nullable=True)
	
class Project(Base):
	__tablename__ = 'project'
	id = Column(String, primary_key=True, unique=True, nullable=False)
	name = Column(String, nullable=False)
	workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'), nullable=False)
	creator_id = Column(String, nullable=False)
	objective = Column(Text, nullable=False)
	meta = Column(JSON, nullable=False)
	status = Column(String, default='created')
	created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
	updated_at = Column(DateTime(timezone=True), nullable=True)
	goals = relationship("Goal", backref="project", cascade="all, delete-orphan")
	agents = relationship("Agent", backref="project", cascade="all, delete-orphan")

class Goal(Base):
	__tablename__ = 'goal'
	id = Column(String, unique=True, nullable=False, primary_key=True)
	description = Column(String, nullable=False)
	project_id = Column(String, ForeignKey('project.id'), nullable=False)
	status = Column(String, default='pending')
	tasks = Column(JSON, nullable=False)
	created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
	updated_at = Column(DateTime(timezone=True), nullable=True)
	agent = relationship("Agent", backref="goal", uselist=False)

class Agent(Base):
	__tablename__ = 'agent'
	id = Column(String, unique=True, nullable=False, primary_key=True)
	role = Column(String, nullable=False)
	scope = Column(String, nullable=True)
	project_id = Column(String, ForeignKey('project.id'), nullable=False)
	goal_id = Column(String, ForeignKey('goal.id'), nullable=True)
	collaborators = Column(JSON, nullable=False)
	created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
	updated_at = Column(DateTime(timezone=True), nullable=True)