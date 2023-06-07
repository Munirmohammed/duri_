import string
import random

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	""" https://stackoverflow.com/a/2257449/1226748  """
	return ''.join(random.choice(chars) for _ in range(size))

def wait_for_container(container):
	"""
	Waits for a Docker container to complete.
	"""
	container.reload()  # Refresh container information
	while container.status == 'running':
		container.reload()
	return container.status


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