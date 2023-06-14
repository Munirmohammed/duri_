from fastapi import Form, Depends
from pydantic import Field, validator, BaseModel, Json, UUID4
from typing import Optional, List, Type, NewType, Any, Dict, Union
from enum import Enum
from datetime import datetime
from src.schema.redis import GoalBase

class ResearchBase(BaseModel):
	id: str = Field(..., description="research id")
	name: str = Field(..., description="research name")
	objective: str = Field(..., description="research objective")
	#project_id: Union[str, UUID4] = Field(..., description="project id")
	status: str = Field(..., description="the research run status")
	created_at: datetime = Field(..., description="the creation date")
	updated_at: Optional[datetime] = Field(None, description="the update date")

	class Config:
		orm_mode = True
		

class ResearchGoal(GoalBase):
    pk: str

class ResearchMini(ResearchBase):
    pass

class Research(ResearchBase):
    goals: Optional[List[ResearchGoal]]