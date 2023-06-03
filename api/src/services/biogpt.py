import docker
import tempfile
import json
from src.core.config import settings
from src.services.redis import ProjectModel
from redis_om import NotFoundError

class Biogpt():
	image_name: str = settings.biogpt_image
	network_name: str = 'duri_api'
	redis_hosturl: str = 'redis:6379'

	def __init__(self):
		pass

	def set_workdir(self) -> dict:
		self.workdir = tempfile.mkdtemp(dir=settings.biogpt_workdir)
		return self.workdir

	def get_project(self, objective) -> dict:
		""" get a project from redis  """
		try:
			project = ProjectModel.find(ProjectModel.objective == objective).first()
			#print(project)
			return project
		except NotFoundError as e:
			#print(e)
			return None

	def init(self, objective) -> ProjectModel:
		""" get or starts an ai project. returns a unique id of that project objective provided """
		project = self.get_project(objective)
		if project:
			return project
		cmds = [ "init", "-o", objective]
		self.set_workdir()
		response = self.call(cmds, detach=False)
		#print(response)
		#resp_dict = json.loads(response).get("project_id", None)
		#project_id = resp_dict.get("project_id", None)
		project = self.get_project(objective)
		return project

	def run(self, objective) -> dict:
		workdir = self.workdir
	
	def call(self, cmd, detach=True) -> dict:
		client = docker.from_env()
		workdir = self.workdir
		envs = self.get_env()
		container = client.containers.run(
			image=self.image_name,
			detach=detach,
			#privileged=True, ## for headless browser
			#auto_remove=True,
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