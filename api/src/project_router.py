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
from src.services import Biogpt, RedisClient
from src import utils
#from src.services.redis import ProjectModel
#from redis_om import NotFoundError

router = APIRouter()

@router.get("/project", response_model=List[project_schema.ProjectMini])
def list_projects(
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
def create_project(
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
	crud_agent = crud.Agent(tables.Agent, db)
	crud_user = crud.User(tables.User, db)
	#project = crud_project.filter_by(workspace_id=workspace_id, limit=1)
	biogpt = Biogpt()
	proj = biogpt.init(objective, name)
	project_id = proj.pk
	goals = proj.goals
	name = proj.name
	project_manager = proj.project_manager
	assistants = proj.assistants
	project = crud_project.get(project_id)
	if project:
		#crud_project.remove(project_id) ## for testing
		# return project ## for testing
		raise HTTPException(status_code=500, detail="similar project already exist")
	project = crud_project.create({
		'id': project_id,
		'name': name,
		'status': 'created',
		'creator_id': user_id,
		'objective': objective,
		'workspace_id': workspace_id,
	})
	#print(project)
	## add project manager agent
	if project_manager:
		crud_agent.create({
			"id": project_manager.pk,
			"role": project_manager.role,
			"scope": project_manager.scope,
			"project_id": project_id,
		})
	## insert goals and assistant agent
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
	#if not auth_user.project:
	user = crud_user.get(user_id)
	user.active_project_id = project_id
	db.commit()
	return project

@router.get("/project/{id}", response_model=project_schema.Project)
def get_project(
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
	if not project:
		raise HTTPException(status_code=404, detail="project not exist")
	return project

@router.post("/project/{id}/run", response_model=project_schema.Project)
def run_project(
	auth_user: schema.UserProfile = Depends(deps.user_from_header),
	id: str = Path(..., description="the project id"),
	db: Session = Depends(deps.get_db),
):
	"""
	run a project
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
		if utils.check_container_status(container_id):
			raise HTTPException(status_code=500, detail="project already running")
	max_count = 5
	biogpt = Biogpt()
	container = biogpt.run(objective, max_count)
	#print(container)
	project.status = 'running' ## container.status.lower()
	container_id = str(container.id)[:12]
	project.meta = {
		'container_id': container_id
	}
	db.commit()
	return project

@router.post("/project/{id}/switch", response_model=project_schema.Project)
def switch_project(
	auth_user: schema.UserProfile = Depends(deps.user_from_header),
	id: str = Path(..., description="the project id"),
	db: Session = Depends(deps.get_db),
):
	"""
	make this project as active project
	"""
	workspace_id = auth_user.workspace.id
	user_id = auth_user.id
	crud_project = crud.Project(tables.Project, db)
	crud_user = crud.User(tables.User, db)
	project = crud_project.get(id)
	if not project:
		raise HTTPException(status_code=500, detail="project not exist")
	project_id = project.id
	user = crud_user.get(user_id)
	user.active_project_id = project_id
	db.commit()
	return project

@router.post("/project/{id}/stop", response_model=project_schema.Project)
def stop_project(
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
	project_id = project.id
	#crud_project.remove(project_id) ## for testing
	return project

@router.get("/project/{id}/agent", response_model=List[project_schema.Agent])
def list_agents(
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

@router.get("/project/{id}/activity")
def get_activity(
	auth_user: schema.UserProfile = Depends(deps.user_from_header),
	id: str = Path(..., description="the project id"),
	db: Session = Depends(deps.get_db),
):
	"""
	Get project activity
	"""
	workspace_id = auth_user.workspace.id
	crud_project = crud.Project(tables.Project, db)
	project = crud_project.get(id)
	if not project:
		raise HTTPException(status_code=500, detail="project not exist")
	project_id = project.id
	redis_client = RedisClient()
	project_index_key = f"doc:{project_id}:index:activity"
	#agent_index_key = f"doc:{project_id}:{role_name}:index:activity"
	keys = redis_client.get_set_keys(project_index_key)
	docs = []
	for k in keys:
		role = k.replace(f"doc:{project_id}:", "").split(":")[0]
		print(role)
		data = redis_client.get_hash(k)
		content = data['content']
		message = utils.parse_agent_doc(content)
		#print(type(message))
		if not isinstance(message, dict):
			continue
		message_type = message['type']
		message_data = message['data']
		if not isinstance(message_data, dict):
			continue
		message_data['role'] = role
		""" r = {
			'role': role,
			'content': message_data
		} """
		docs.append(message_data)
	return docs

@router.get("/project/{id}/agent/{agent_id}", response_model=project_schema.Agent)
def get_agent(
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

@router.get("/project/{id}/agent/{agent_id}/chat", response_model=List[project_schema.ChatMessage])
def get_agent_chat(
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
	project_id = project.id
	agent_role = agent.role
	agent_role_name = utils.snake_case(agent_role)
	redis_client = RedisClient()
	key_pattern = f"doc:{project_id}:{agent_role_name}:agent:index:"
	keys = redis_client.get_set_keys(key_pattern)
	#print(keys)
	docs = []
	for k in keys:
		data = redis_client.get_hash(k)
		#parsed = utils.parse_agent_doc(content)
		content = data['content']
		message = utils.parse_agent_doc(content)
		message_type = message['type']
		message_data = message['data']
		message_role = message_data['role'] if message_type == 'chat' else message_type
		message_content = message_data['content']
		r = {
			'role': message_role,
			'content': message_content
		}
		docs.append(r)
	#print(docs)
	return docs
