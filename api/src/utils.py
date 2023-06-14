import string
import random
import docker 
import re
import json
import hashlib

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	""" https://stackoverflow.com/a/2257449/1226748  """
	return ''.join(random.choice(chars) for _ in range(size))

def generate_id(text:str) -> str:
	""" generate a unique id of a given text, 
	the id will always be the same for the same exact text """
	_id = hashlib.md5(text.encode()).hexdigest()
	return _id

def wait_for_container(container):
	"""
	Waits for a Docker container to complete.
	"""
	container.reload()  # Refresh container information
	while container.status == 'running':
		container.reload()
	return container.status

def get_container(container_id):
	client = docker.from_env()
	try:
		container = client.containers.get(container_id)
		return container
	except docker.errors.NotFound:
		return False
	
def check_container_status(container_id):
	client = docker.from_env()
	try:
		container = client.containers.get(container_id)
		if container.status == 'running':
			return True
		else:
			return False
	except docker.errors.NotFound:
		return False
	
def stop_container(container_id):
	client = docker.from_env()
	try:
		container = client.containers.get(container_id)
		if container.status == 'running':
			container.stop()
		return
	except docker.errors.NotFound:
		return

class Dict2Obj(object):
	"""
	Turns a dictionary into a class
	"""
	def __init__(self, dictionary):
		for key in dictionary:
			setattr(self, key, dictionary[key])

def snake_case(text):
	# Replace non-alphanumeric characters with underscores
	snake_string = re.sub('[^a-zA-Z0-9]', '_', text)
	# Convert to lowercase and remove consecutive underscores
	snake_string = re.sub('_+', '_', snake_string).lower()
	# Remove underscores at the beginning and end of the string
	snake_string = snake_string.strip('_')
	return snake_string

def preprocess_json_input(input_str: str) -> str:
    # Replace single backslashes with double backslashes,
    # while leaving already escaped ones intact
    corrected_str = re.sub(
        r'(?<!\\)\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', r"\\\\", input_str
    )
    return corrected_str

def parse_agent_doc(doc):
	try:
		parsed = json.loads(doc, strict=False)
	except json.JSONDecodeError:
		preprocessed_text = preprocess_json_input(doc)
		try:
			parsed = json.loads(preprocessed_text, strict=False)
		except Exception:
			parsed = None
	return parsed
	