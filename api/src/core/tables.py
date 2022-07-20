from datetime import datetime
from email.policy import default
from sqlalchemy import Table, Column, Integer, BigInteger, String, ForeignKey, DateTime, JSON, TEXT, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
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
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True)

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

class Team(Base):
    __tablename__ = 'team'
    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid4)
    name = Column(String, nullable=False)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace.id'), nullable=True)
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

class UserTeam(Base):
    __tablename__ = 'user_team'
    user_id = Column(UUID(as_uuid=True),  ForeignKey('user.id'), primary_key=True, nullable=False)
    workspace_id = Column(UUID(as_uuid=True),  ForeignKey('workspace.id'), primary_key=True, nullable=False)
    team_id = Column(UUID(as_uuid=True),  ForeignKey('team.id'), primary_key=True, nullable=False)
    membership = Column(String, nullable=True, default='contributor')
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)