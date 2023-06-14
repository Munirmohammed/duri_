import os
import json
import base64
import pathlib
from datetime import datetime
from urllib.parse import urlparse
from pydantic import Json
from typing import Optional, List, Any, Dict, Union
from fastapi import APIRouter, Depends, Query, Path, Header, Form, HTTPException, BackgroundTasks
from starlette.status import HTTP_403_FORBIDDEN
from sqlalchemy.orm import Session
from .core import deps, schema, crud, tables
from .core.config import settings
from .schema import research as research_schema
from src.services import Biogpt, RedisClient
from src import utils
from src.schema.redis import ProjectModel
from src.util.migrate_projects import sync_outputs
#from src.services.redis import ProjectModel
#from redis_om import NotFoundError

router = APIRouter()

@router.get("/research", response_model=List[research_schema.ResearchMini])
def list_research(
	auth_user: schema.UserProfile = Depends(deps.user_from_header),
	db: Session = Depends(deps.get_db),
):
	"""
	List all research of the user workspace
	"""
	workspace_id = auth_user.workspace.id
	crud_research = crud.Research(tables.Research, db)
	researches = crud_research.filter_by(workspace_id=workspace_id)
	return researches

@router.post("/research", response_model=research_schema.Research)
def create_research(
	auth_user: schema.UserProfile = Depends(deps.user_from_header),
	objective: str = Form(..., description="the research objective"),
	name: Optional[str] = Form(None, description="the research name"),
	db: Session = Depends(deps.get_db),
):
	"""
	create a research
	"""
	objective = objective.strip()
	user_id = auth_user.id
	workspace_id = auth_user.workspace.id
	project_id = auth_user.project.id
	
	crud_research = crud.Research(tables.Research, db)
	
	#research = crud_research.filter_by(workspace_id=workspace_id, limit=1)
	biogpt = Biogpt()
	research_model = biogpt.init_research(project_id, objective, name)
	research_id = research_model.pk
	name = research_model.name
	workdir = research_model.workdir
	goals = research_model.goals
	research = crud_research.get(research_id)
	if research:
		#crud_project.remove(project_id) ## for testing
		# return project ## for testing
		raise HTTPException(status_code=500, detail="similar research already exist")
	research = crud_research.create({
		'id': research_id,
		'workspace_id': workspace_id,
		'project_id': project_id,
		'name': name,
		'status': 'pending',
		'creator_id': user_id,
		'workdir': workdir,
		'goals': goals,
		'objective': objective,
	})
	
	return research

@router.get("/research/{id}", response_model=research_schema.Research)
def get_research(
	auth_user: schema.UserProfile = Depends(deps.user_from_header),
	id: str = Path(..., description="the research id"),
	db: Session = Depends(deps.get_db),
):
	"""
	get a research
	"""
	workspace_id = auth_user.workspace.id
	crud_research = crud.Research(tables.Research, db)
	research = crud_research.get(id)
	if not research:
		raise HTTPException(status_code=404, detail="research not exist")
	if research.meta and research.meta.get('container_id', None):
		container_id = research.meta.get('container_id', None)
		print('container_id', container_id)
		container = utils.get_container(container_id)
		if container:
			running = utils.check_container_status(container_id)
			research.status = 'running' if running else 'paused'
			if not running:
				research.meta = None
		else:
			if research.status != 'pending':
				research.status = 'paused'
				research.meta = None
		db.commit()
	return research

@router.post("/research/{id}/run", response_model=research_schema.Research)
def run_research(
	auth_user: schema.UserProfile = Depends(deps.user_from_header),
	id: str = Path(..., description="the research id"),
	db: Session = Depends(deps.get_db),
):
	"""
	run a research
	"""
	user_id = auth_user.id
	workspace_id = auth_user.workspace.id
	project_id = auth_user.project.id
	
	crud_research = crud.Research(tables.Research, db)
	research = crud_research.get(id)
	if not research:
		raise HTTPException(status_code=500, detail="research not exist")
	objective = research.objective
	#status = project.status
	if research.meta and research.meta.get('container_id', None):
		## todo: check if container is running
		container_id = research.meta.get('container_id', None)
		if utils.check_container_status(container_id):
			raise HTTPException(status_code=500, detail="research already running")
	max_count = 5
	biogpt = Biogpt()
	container = biogpt.run_research(project_id, objective, max_count)
	#print(container)
	research.status = 'running' ## container.status.lower()
	container_id = str(container.id)[:12]
	research.meta = {
		'container_id': container_id
	}
	db.commit()
	return research

@router.post("/research/{id}/stop", response_model=research_schema.Research)
def stop_research(
	auth_user: schema.UserProfile = Depends(deps.user_from_header),
	id: str = Path(..., description="the research id"),
	db: Session = Depends(deps.get_db),
):
	"""
	stop a research
	"""
	workspace_id = auth_user.workspace.id
	crud_research = crud.Research(tables.Research, db)
	research = crud_research.get(id)
	if not research:
		raise HTTPException(status_code=404, detail="research not exist")
	if not (research.meta and research.meta.get('container_id', None)):
		research.status = 'paused'
		research.meta = None
		db.commit()
		raise HTTPException(status_code=404, detail="research not running")
	container_id = research.meta.get('container_id', None)
	if container_id and utils.check_container_status(container_id):
		utils.stop_container(container_id)
	research.status = 'paused'
	research.meta = None
	db.commit()
	return research

'''@router.post("/research/{id}/restart", response_model=research_schema.Research)
def restart_research(
	auth_user: schema.UserProfile = Depends(deps.user_from_header),
	id: str = Path(..., description="the research id"),
	db: Session = Depends(deps.get_db),
):
	"""
	restart a research
	"""
	workspace_id = auth_user.workspace.id
	project_id = auth_user.project.id
	crud_research = crud.Research(tables.Research, db)
	research = crud_research.get(id)
	if not research:
		raise HTTPException(status_code=404, detail="research not exist")
	if research.meta and research.meta.get('container_id', None):
		container_id = research.meta.get('container_id', None)
		container = utils.get_container(container_id)
		if container and utils.check_container_status(container_id):
				research.status = 'running'
				db.commit()
				return research
	objective = research.objective
	max_count = 5
	biogpt = Biogpt()
	container = biogpt.run_research(project_id, objective, max_count)
	#print(container)
	research.status = 'running' ## container.status.lower()
	container_id = str(container.id)[:12]
	research.meta = {
		'container_id': container_id
	}
	db.commit()
	return research '''

@router.get("/research/{id}/activity")
def get_research_activity(
	auth_user: schema.UserProfile = Depends(deps.user_from_header),
	id: str = Path(..., description="the research id"),
	db: Session = Depends(deps.get_db),
):
	"""
	Get research activity
	"""
	workspace_id = auth_user.workspace.id
	project_id = auth_user.project.id
	crud_research = crud.Research(tables.Research, db)
	research = crud_research.get(id)
	if not research:
		raise HTTPException(status_code=404, detail="research not exist")
	
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