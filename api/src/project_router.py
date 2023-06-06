import os
import json
from datetime import datetime
from urllib.parse import urlparse
from pydantic import Json
from typing import Optional, List, Any, Dict, Union
from fastapi import APIRouter, Depends, Query, Path, Header, Form, HTTPException, BackgroundTasks
from starlette.status import HTTP_403_FORBIDDEN
from sqlalchemy.orm import Session
from .core import deps, schema, crud, tables
from .core.config import settings
from .schema import project as project_schema
from src.services import Biogpt
#from src.services.redis import ProjectModel
#from redis_om import NotFoundError

router = APIRouter()

@router.get("/project", response_model=List[project_schema.ProjectMini])
async def list_projects(
	auth_user: schema.UserProfile = Depends(deps.user_from_header),
	db: Session = Depends(deps.get_db),
):
	"""
	List all projects of the user workspace
	"""
	workspace_id = auth_user.workspace.id
	crud_project = crud.Project(tables.Project, db)
	projects = crud_project.filter_by(workspace_id=workspace_id)
	return projects

@router.post("/project", response_model=project_schema.ProjectMini)
async def create_project(
	auth_user: schema.UserProfile = Depends(deps.user_from_header),
	objective: str = Form(..., description="the project objective"),
	name: Optional[str] = Form(None, description="the project name"),
	db: Session = Depends(deps.get_db),
):
	"""
	create a project
	"""
	workspace_id = auth_user.workspace.id
	user_id = auth_user.id
	crud_project = crud.Project(tables.Project, db)
	#project = crud_project.filter_by(workspace_id=workspace_id, limit=1)
	biogpt = Biogpt()
	proj = biogpt.init(objective)
	project_id = proj.pk
	goals = proj.goals
	name = proj.name
	assistants = proj.assistants
	project = crud_project.get(project_id)
	if project:
		#crud_project.remove(project_id) ## for testing
		# return project ## for testing
		raise HTTPException(status_code=500, detail="similar project already exist")
	project = crud_project.create({
		'id': project_id,
		'name': name,
		'creator_id': user_id,
		'objective': objective,
		'workspace_id': workspace_id,
	})
	print(project)
	for g in goals:
		goal_id = g.pk
		goal = tables.Goal(**{
			"id": goal_id,
			"description": g.goal,
			"tasks": []
		})
		assistant =  next(x for x in assistants if x.goal_id == goal_id )
		if assistant:
			assistant_id = assistant.pk
			collaborator = {}
			collab = assistant.collaborator
			if collab:
				collaborator = {'id': collab.pk, "role": collab.role, "scope": collab.scope}
			agent = tables.Agent(**{
				"id": assistant_id,
				"role": assistant.role,
				"scope": assistant.scope,
				"project_id": project_id,
				"collaborators":  collaborator,
			})
			goal.agent = agent
		project.goals.append(goal)
	db.commit()
	return project

@router.get("/project/{id}", response_model=project_schema.Project)
async def get_project(
	auth_user: schema.UserProfile = Depends(deps.user_from_header),
	id: str = Path(..., description="the project id"),
	db: Session = Depends(deps.get_db),
):
	"""
	get a project
	"""
	workspace_id = auth_user.workspace.id
	crud_project = crud.Project(tables.Project, db)
	project = crud_project.get(id)
	return project

@router.post("/project/{id}/run", response_model=project_schema.Project)
async def run_project(
	auth_user: schema.UserProfile = Depends(deps.user_from_header),
	id: str = Path(..., description="the project id"),
	db: Session = Depends(deps.get_db),
):
	"""
	run a project (todo)
	"""
	workspace_id = auth_user.workspace.id
	crud_project = crud.Project(tables.Project, db)
	project = crud_project.get(id)
	if not project:
		raise HTTPException(status_code=500, detail="project not exist")
	objective = project.objective
	#status = project.status
	if project.meta and project.meta.get('container_id', None):
		## todo: check if container is running
		container_id = project.meta.get('container_id', None)
		raise HTTPException(status_code=500, detail="project already running") 
	biogpt = Biogpt()
	container = biogpt.run(objective)
	print(container)
	project.status = 'running'
	project.meta = {
		'container_id': container.shortid
	}
	db.commit()
	return project

@router.post("/project/{id}/stop", response_model=project_schema.Project)
async def stop_project(
	auth_user: schema.UserProfile = Depends(deps.user_from_header),
	id: str = Path(..., description="the project id"),
	db: Session = Depends(deps.get_db),
):
	"""
	stop a project (todo)
	"""
	workspace_id = auth_user.workspace.id
	crud_project = crud.Project(tables.Project, db)
	project = crud_project.get(id)
	if not project:
		raise HTTPException(status_code=500, detail="project not exist")
	return project

@router.get("/project/{id}/agent", response_model=List[project_schema.Agent])
async def list_agents(
	auth_user: schema.UserProfile = Depends(deps.user_from_header),
	id: str = Path(..., description="the project id"),
	db: Session = Depends(deps.get_db),
):
	"""
	list agents
	"""
	workspace_id = auth_user.workspace.id
	crud_project = crud.Project(tables.Project, db)
	project = crud_project.get(id)
	if not project:
		raise HTTPException(status_code=500, detail="project not exist")
	return project.agents

@router.get("/project/{id}/agent/{agent_id}", response_model=project_schema.Agent)
async def get_agent(
	auth_user: schema.UserProfile = Depends(deps.user_from_header),
	id: str = Path(..., description="the project id"),
	agent_id: str = Path(..., description="the agent id"),
	db: Session = Depends(deps.get_db),
):
	"""
	get an agent
	"""
	workspace_id = auth_user.workspace.id
	crud_project = crud.Project(tables.Project, db)
	crud_agent = crud.Agent(tables.Agent, db)
	project = crud_project.get(id)
	if not project:
		raise HTTPException(status_code=500, detail="project not exist")
	agent = crud_agent.get(agent_id)
	if not agent:
		raise HTTPException(status_code=500, detail="agent of provided agent-id not exist")
	return agent
