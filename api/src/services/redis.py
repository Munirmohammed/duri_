from pydantic import  BaseModel
from typing import Optional, List, Type, NewType, Any, Dict, Union
from redis_om import (
    EmbeddedJsonModel,
    JsonModel,
    Field,
    Migrator
)
from redis_om import get_redis_connection
from src.core.config import settings

redis_conn = get_redis_connection(url=f"redis://{settings.redis_host}", decode_responses=True)

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

class Goal(GoalBase):
    """Goal object."""
    assistant: AssistantBase
    collaborator: Optional[AssistantBase] = None

### REDIS DATA MODELS
class AssistantBaseModel(EmbeddedJsonModel, AssistantBase):
    pass

class AssistantModel(AssistantBaseModel):
    goal_id: str = Field(index=True)
    collaborator: Optional[AssistantBaseModel] = None

class GoalModel(EmbeddedJsonModel, GoalBase):
    steps: Optional[List[str]]
    

class ProjectModel(JsonModel):
    objective:  str = Field(index=True)
    goals: Optional[List[GoalModel]]
    assistants: Optional[List[AssistantModel]]
    class Meta:
        global_key_prefix = "biogpt"
        model_key_prefix = "project"
        database = redis_conn

Migrator().run()