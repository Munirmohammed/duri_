import string
import docker
import tempfile
import json
import time
from redis_om import NotFoundError
from src.utils import wait_for_container
from src.core.config import settings
from src.schema.redis import ProjectModel

class Biogpt():
	image_name: str = settings.biogpt_image
	network_name: str = 'duri_api'
	redis_hosturl: str = 'redis:6379'
	workdir: str = None
	project: str = None

	def __init__(self):
		pass

	def set_workdir(self) -> dict:
		if self.workdir:
			return self.workdir
		self.workdir = tempfile.mkdtemp(dir=settings.biogpt_workdir)
		return self.workdir

	def get_project(self, objective) -> dict:
		""" get a project from redis  """
		objective = objective.strip()
		try:
			project = ProjectModel.find(ProjectModel.objective == objective).first()
			if not project:
				return None
			print('project.workdir: ', project.workdir)
			if project.workdir:
				self.workdir = project.workdir
			else:
				project.workdir = self.set_workdir()
				project.save()
			#print(project)
			project.name = project.name.strip().replace("\\n", "").replace('\"', "").strip(string.punctuation).strip()
			project.save()
			self.project = project
			return project
		except NotFoundError as e:
			#print(e)
			return None
		except Exception:
			#print(e)
			return None

	def init(self, objective, name:str=None) -> ProjectModel:
		""" get or starts an ai project. returns a unique id of that project objective provided """
		project = self.get_project(objective)
		if project and project.name:
			return project
		self.workdir = self.set_workdir()
		cmds = [ "init", "-o", objective]
		container = self.call(cmds, wait=True)
		#print(response)
		#resp_dict = json.loads(response).get("project_id", None)
		#project_id = resp_dict.get("project_id", None)
		while True:
			time.sleep(1)
			project = self.get_project(objective)
			if project:
				break
		project = self.get_project(objective)	
		#print(project)
		if name:
			project.name = name
			project.save()
		self.project = project
		return project

	def run(self, objective, max_count=50) -> dict:
		project = self.get_project(objective)
		if not project:
			raise NotFoundError()
		cmds = [ "run", "-o", str(objective), '-c', str(max_count)]
		container = self.call(cmds, wait=False, auto_remove=True)
		return container
	
	def call(self, cmd, wait=False, auto_remove=True) -> dict:
		client = docker.from_env()
		assert self.workdir
		workdir = self.workdir
		envs = self.get_env()
		container = client.containers.run(
			image=self.image_name,
			detach=True,
			#privileged=True, ## for headless browser
			auto_remove=auto_remove,
			environment=envs,
			network=self.network_name,
			volumes={
				f'{workdir}/outputs': {
					"bind": '/app/outputs',
					"mode": "rw"
				}
			},
			command=cmd
		)
		print(container)
		if wait:
			while wait_for_container(container) == 'running':
				time.sleep(1)
		print(container)
		#status = container.status
		#container_id = str(container.id)[:12]
		#container_id = container.shortid
		return container

	def get_env(cls):
		return {
			"OPENAI_API_KEY": settings.openai_key,
			"SERPER_API_KEY": settings.serper_key,
			"WEAVIATE_URL": settings.weaviate_url,
			"REDIS_HOST": settings.redis_host,
		}