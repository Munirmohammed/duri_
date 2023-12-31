from fastapi import Form, Depends
from pydantic import Field, validator, BaseModel, Json, UUID4
from typing import Optional, List, Type, NewType, Any, Dict, Union
from enum import Enum
from datetime import datetime

class ProjectBase(BaseModel):
	id: str = Field(..., description="project id")
	name: str = Field(..., description="project name")
	objective: str = Field(..., description="project objective")
	workspace_id: Union[str, UUID4] = Field(..., description="workspace id")
	status: str = Field(..., description="the project run status")
	# name: Dict[str, Any] = Field(..., description="message")
	created_at: datetime = Field(..., description="the creation date")
	updated_at: Optional[datetime] = Field(None, description="the update date")

	class Config:
		orm_mode = True

class GoalBase(BaseModel):
	id: str = Field(..., description="goal id")
	description: str = Field(..., description="goal description")
	status: str = Field(..., description="goal run status")
	created_at: datetime = Field(..., description="the creation date")
	updated_at: Optional[datetime] = Field(None, description="the update date")
	class Config:
		orm_mode = True

class CollaboratorBase(BaseModel):
    """Assistant agent object."""
    id: Optional[str] = Field(None, description="collaborator id")
    role: Optional[str] = Field(None, description="collaborator role")
    scope: Optional[str] = Field(None, description="collaborator scope")
    
class AgentBase(BaseModel):
	id: str = Field(..., description="agent id")
	role: str = Field(..., description="agent role")
	#status: str = Field(..., description="agent active status")
	scope: str = Field(..., description="agent task scope")
	collaborators: Optional[CollaboratorBase] = Field(None, description="agent collaborators")
	created_at: datetime = Field(..., description="the creation date")
	updated_at: Optional[datetime] = Field(None, description="the update date")
	class Config:
		orm_mode = True

class Agent(AgentBase):
	pass

class ProjectMini(ProjectBase):
	pass

class Project(ProjectBase):
	goals: List[GoalBase]
	agents: List[AgentBase]


class ChatMessage(BaseModel):
	role: str = Field(..., description="the speaker")
	content: str = Field(..., description="the content")

class OutputFile(BaseModel):
	id: str = Field(..., description="the file id")
	name: str = Field(..., description="the file name")
	path: str = Field(..., description="the file path")
	type: str = Field(..., description="the file type  one of `file` or `dir`")
	size: str = Field(..., description="the file size  in bytes")
	created: datetime = Field(..., description="the file creation date")
	modified: Optional[str] = Field(None, description="the file modified date")

class FileContent(BaseModel):
	id: str = Field(..., description="the file id")
	path: str = Field(..., description="the file path")
	content: str = Field(..., description="the file content in base64")
	

