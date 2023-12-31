from pydantic import  BaseModel
from typing import Optional, List, Type, NewType, Any, Dict, Union
from redis_om import (
    EmbeddedJsonModel,
    JsonModel,
    Field,
    Migrator
)
from datetime import datetime
from src.services.redis import redis_conn


## redis schemas
class AssistantBase(BaseModel):
    """Assistant agent object."""
    role: str
    scope: str

class GoalBase(BaseModel):
    """Goal-Basse object."""
    index: str = Field(index=True)
    goal: str = Field(index=True)
    status: str = Field(index=True, default='pending')

class ResearchBase(BaseModel):
    """Research-Basse model."""
    project_id: str = Field(index=True)
    name: Optional[str] = Field(index=True)
    objective: str = Field(index=True)
    status: str = Field(index=True, default='pending')
    workdir: Optional[str] = Field(default=None)
    created: Optional[datetime] = Field(default=datetime.now())

class Goal(GoalBase):
    """Goal object."""
    assistant: AssistantBase
    collaborator: Optional[AssistantBase] = None

### REDIS DATA MODELS
class AssistantBaseModel(EmbeddedJsonModel, AssistantBase):
    class Meta:
        global_key_prefix = "biogpt"
        model_key_prefix = "assistant"
        database = redis_conn

class PlannerModel(AssistantBaseModel):
    class Meta:
        global_key_prefix = "biogpt"
        model_key_prefix = "assistant"
        database = redis_conn

class AssistantModel(AssistantBaseModel):
    goal_id: str = Field(index=True)
    collaborator: Optional[AssistantBaseModel] = None
    class Meta:
        global_key_prefix = "biogpt"
        model_key_prefix = "assistant"
        database = redis_conn

class GoalModelMini(EmbeddedJsonModel, GoalBase):
    class Meta:
        global_key_prefix = "biogpt"
        model_key_prefix = "goal"
        database = redis_conn

class GoalModel(EmbeddedJsonModel, GoalBase):
    steps: Optional[List[str]]
    class Meta:
        global_key_prefix = "biogpt"
        model_key_prefix = "goal"
        database = redis_conn

class ResearchModel(EmbeddedJsonModel, ResearchBase):
    agents: Optional[List[str]]
    goals: Optional[List[GoalModelMini]]
    class Meta:
        global_key_prefix = "biogpt"
        model_key_prefix = "research"
        database = redis_conn

class ProjectModel(JsonModel):
    name: Optional[str] = Field(index=True)
    workdir: Optional[str] = Field(default=None)
    objective:  str = Field(index=True)
    goals: Optional[List[GoalModel]]
    project_manager: Optional[PlannerModel]
    assistants: Optional[List[AssistantModel]]
    class Meta:
        global_key_prefix = "biogpt"
        model_key_prefix = "project"
        database = redis_conn

Migrator().run()