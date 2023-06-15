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
from .schema import project as project_schema
from src.services import Biogpt, RedisClient
from src import utils
from src.schema.redis import ResearchModel
from src.util.migrate_projects import sync_outputs
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
	background_tasks: BackgroundTasks,
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
	research_obj = ResearchModel.get(id)
	research_obj.status = research.status
	research.name = research_obj.name
	if research_obj.workdir:
		research.workdir = research_obj.workdir
		background_tasks.add_task(sync_outputs, research_obj)
	db.commit()
	research_obj.save()
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
	max_count = 150
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
	research_id = research.id
	#research_obj = ResearchModel.get(research_id)
	#if not research_obj.agents or len(research_obj.agents) == 0 :
	#	raise HTTPException(status_code=500, detail="research not fully initialized retry after 10 seconds")
	#agent = research_obj.agents[0]
	redis_client = RedisClient()
	index_key = f"doc:{research_id}:index:activity"
	#agent_index_key = f"doc:{project_id}:{role_name}:index:activity"
	keys = redis_client.get_set_keys(index_key, withscores=True)
	docs = []
	for k, score in keys:
		role = k.replace(f"doc:{research_id}:", "").split(":")[0]
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
		message_data['date'] = datetime.fromtimestamp(score)
		docs.append(message_data)
	return docs

@router.get("/research/{id}/output", 
	#response_model=List[Union[project_schema.OutputFile, None]]
)
def list_research_output(
	auth_user: schema.UserProfile = Depends(deps.user_from_header),
	id: str = Path(..., description="the research id"),
	db: Session = Depends(deps.get_db),
):
	"""
	list research output
	"""
	workspace_id = auth_user.workspace.id
	project_id = auth_user.project.id
	crud_research = crud.Research(tables.Research, db)
	research = crud_research.get(id)
	if not research:
		raise HTTPException(status_code=404, detail="research not exist")
	research_id = research.id
	print(research.workdir)
	results = []
	try:
		output_key  = f'outputs:{research_id}:'
		redis_client = RedisClient().client
		results = redis_client.json().get(output_key, '$.*')
		print(results)
		results = [project_schema.OutputFile(**r) for r in results]
		#results = [e for sublist in results for e in sublist]
	except Exception:
		results = []
	return results

@router.get(
	"/research/{id}/output/{file_path:path}", 
	response_model=Union[List[project_schema.OutputFile], project_schema.FileContent]
)
def get_research_output(
	auth_user: schema.UserProfile = Depends(deps.user_from_header),
	id: str = Path(..., description="the research id"),
	file_path: str = Path(..., description="the file path"),
	db: Session = Depends(deps.get_db),
):
	"""
	get research output
	"""
	workspace_id = auth_user.workspace.id
	crud_research = crud.Research(tables.Research, db)
	research = crud_research.get(id)
	if not research:
		raise HTTPException(status_code=404, detail="research not exist")
	research_id = research.id
	redis_client = RedisClient().client
	output_key  = f'outputs:{research_id}:'
	file_paths = file_path.split("/")
	#print(len(file_paths))
	def get_file(key, file_id):
		#print(file_id)
		try:
			json_path = f'.[?(@.id == "{file_id}")]'
			result = redis_client.json().get(key, json_path)
			filepath = result['path']
			research = ResearchModel.get(research_id)
			#print(proj.workdir)
			workdir = research.workdir + "/outputs"
			real_path = os.path.join(workdir, filepath)
			file = pathlib.Path(real_path)
			content = file.read_text()
			b4_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
			return {
				"id": file_id,
				"path": filepath,
				"content": b4_content,
			}
		except Exception as e:
			print(e)
			return None
	def get_dir(key):
		try:
			results = redis_client.json().get(key, '$.*')
			#print(results)
			return results
		except Exception:
			return None
	if len(file_paths) == 1:
		## root paths
		file_id = utils.generate_id(file_path)
		result = get_file(output_key, file_id)
		return result
	else:
		#print('nestd path', file_path)
		if file_path.endswith('/'):
			path_id = utils.generate_id(file_path)
			#print('path_id', path_id)
			output_key = output_key + path_id
			result = get_dir(output_key)
		else:
			#file_path = "/" + file_paths[-1]
			#print(file_path)
			parent_path = "/".join(file_paths[:-1] + [""])
			#print(parent_path)
			file_id = utils.generate_id(file_path)
			#print("file_id", file_id)
			path_id = utils.generate_id(parent_path)
			#print("path_id", path_id)
			output_key = output_key + path_id
			result = get_file(output_key, file_id)
		return result