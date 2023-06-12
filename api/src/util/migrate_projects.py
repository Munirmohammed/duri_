import os
import json
from pathlib import Path
from datetime import datetime
from src.services import RedisClient
from src.utils import generate_id

def sync_outputs(project):
	results = []
	redis_client = RedisClient().client
	if not project.workdir:
		return results
	workdir = f"{project.workdir}/outputs"
	if not Path(workdir).exists():
		print('workdir not exist', workdir)
		return results
	project_id = project.pk
	base_key = f'outputs:{project_id}:'
	
	for root, dirs, files in os.walk(workdir):
		#print(root, dirs, files)
		root_path = os.path.normpath(root)
		root_rel_path = os.path.relpath(root_path, workdir)
		#print('root_rel_path', root_rel_path)
		if root_rel_path != '.':
			for n in root_rel_path.split('/'):
				#print(n)
				id = generate_id(n)
				base_key = base_key + f"{id}:"
		#print('base_key', base_key)
		if not redis_client.exists(base_key):
			print('create a list-key ', base_key)
			#redis_client.lpush(base_key, '')
			redis_client.json().set(base_key, '$', [])
		results.append(base_key)
		ids = redis_client.json().get(base_key, '$..id')
		for filename in files:
			realpath = os.path.join(root_path, filename)
			rel_path = os.path.relpath(realpath, workdir)
			#print('file.rel_path' , rel_path)
			id = generate_id(rel_path)
			if id in ids:
				continue
			file = Path(realpath)
			file_stat = file.stat()
			file_size = file_stat.st_size
			file_time = file_stat.st_ctime
			creation_date = datetime.fromtimestamp(file_time)
			#exist = redis_client.json().get(base_key, '.id == "{}"'.format(id))
			#exist = redis_client.json().get(base_key, '$..id')
			_obj = {
				'id': id,
				'name': filename,
				'path': rel_path,
				'type': 'file',
				'size': file_size,
				'created': creation_date.strftime('%Y-%m-%d %H:%M:%S'),
				'modified': None
			}
			#redis_client.rpush(base_key, json.dumps(_obj))
			redis_client.json().arrappend(base_key, '.', _obj)
			
		for dir in dirs:
			realpath = os.path.join(root_path, dir)
			rel_path = os.path.relpath(realpath, workdir)
			#print('dir.rel_path' , rel_path)
			id = generate_id(rel_path)
			if id in ids:
				continue
			file = Path(realpath)
			file_stat = file.stat()
			file_size = file_stat.st_size
			file_time = file_stat.st_ctime
			creation_date = datetime.fromtimestamp(file_time)
			#exist = redis_client.json().get(base_key, '.id == "{}"'.format(id))
			
			_obj = {
				'id': id,
				'name': dir,
				'path': rel_path,
				'type': 'dir',
				'size': file_size,
				'created': creation_date.strftime('%Y-%m-%d %H:%M:%S'),
				'modified': None
			}
			#redis_client.rpush(base_key, json.dumps(_obj))
			redis_client.json().arrappend(base_key, '.', _obj)
	return results
		
		