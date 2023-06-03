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
	# name: Dict[str, Any] = Field(..., description="message")
	created_at: datetime = Field(..., description="the creation date")
	updated_at: Optional[datetime] = Field(None, description="the creation date")

	class Config:
		orm_mode = True
		
class ProjectMini(ProjectBase):
	pass

