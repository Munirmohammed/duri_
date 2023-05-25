
from typing import Optional, Dict, Any, Union, Tuple
import requests
from src.core.config import settings
from src import utils


class Gitea():
    token = settings.gitea_token
    url = 'http://trs_gitea:9049/api/v1'

    def __init__(self, auth: tuple = None):
        if auth:
            self.auth = auth

    def request(
            self,
            method: str,
            path: str,
            params: Optional[Dict[str, Any]] = None,
            json: Any = None,
            data: Optional[str] = None,
            headers: Optional[Dict[str, Any]] = None,
            auth: Optional[Tuple[str, str]] = None,
            # timeout: Optional[int] = None,
            stream: bool = False,
    ):
        try:
            # params_auth = {'token': self.token}
            # req_params = params_auth.update(params)
            if not headers:
                headers = {'Authorization': f'token {self.token}'}
            print('headers', headers)
            if auth:
                headers = None
            _resp = requests.request(
                method,
                f"{self.url}{path}",
                params=params,
                json=json,
                data=data,
                headers=headers,
                auth=auth,
                # timeoout=timeout,
                stream=stream,
            )
            _resp.raise_for_status()
            return _resp
        except requests.exceptions.HTTPError as err:
            print(err)
            raise err

    def get_org(self, name):
        r = self.request('GET', f'/orgs/{name}')
        return r.json()

    def create_org(self, name, visibility: str = 'private', description: str = None, with_webhook: bool = True):
        """ 
                Params:
                        name: str =  the org name
                        visibility: enum = [ public, limited, private ]
        """
        payload = {
            "full_name": name,
            "username": name,
            "visibility": visibility,
            "description": description,
            "repo_admin_change_team_access": True
        }
        req = self.request('POST', f'/orgs', json=payload)
        # addtional org actions
        org = req.json()
        if with_webhook:
            self.get_or_create_org_hook(org['name'])
        return org

    def get_or_create_org(self, name, **kwargs):
        try:
            org = self.get_org(name)
        except Exception as e:
            org = self.create_org(name, **kwargs)
        return org

    def list_org_hooks(self, org):
        r = self.request('GET', f'/orgs/{org}/hooks')
        return r.json()

    def create_org_hook(self, org, endpoint=None, events: list = ["*"]):
        url = endpoint or f'{self.webhook_endpoint}/webhook'
        payload = {
            'type': 'gitea',
            'config': {
                    'url': url,
                'content_type': 'json'
            },
            'events': events,
            'active': True
        }
        print('create_org_hook', payload)
        r = self.request('POST', f'/orgs/{org}/hooks', json=payload)
        return r.json()

    def get_or_create_org_hook(self, org, endpoint=None):
        endpoint = endpoint or f'{self.webhook_endpoint}/webhook'
        hooks = self.list_org_hooks(org)
        hook = next((h for h in hooks if h['config']['url'] == endpoint), None)
        if not hook:
            hook = self.create_org_hook(org, endpoint)
        return hook

    def list_org_teams(self, org):
        req = self.request('GET', f'/orgs/{org}/teams')
        return req.json()

    def team_exists(self, org, name):
        teams = self.list_org_teams(org)
        team = next((t for t in teams if t['name'] == name), False)
        return team

    def get_team(self, id):
        req = self.request('GET', f'/teams/{id}')
        return req.json()

    def list_team_members(self, id):
        req = self.request('GET', f'/teams/{id}/members')
        return req.json()

    def get_team_member(self, id, username):
        req = self.request('GET', f'/teams/{id}/members/{username}')
        return req.json()

    def add_team_member(self, id, username):
        req = self.request('PUT', f'/teams/{id}/members/{username}')
        return req.status_code

    def create_team(self, org, name, description=None):
        """ create a org team , [ref](http://localhost:9049/api/swagger#/organization/orgCreateTeam) """
        create_team_data = {
            "name": name,
            "can_create_org_repo": True,
            "description": description,
            "includes_all_repositories": True,
            "permission": 'read',  # enaum of  [read, write, admin]
            "units": ["repo.code", "repo.issues", "repo.ext_issues", "repo.wiki", "repo.pulls", "repo.releases", "repo.projects", "repo.ext_wiki"],
            "units_map": {"repo.code": "read", "repo.ext_issues": "none", "repo.ext_wiki": "none", "repo.issues": "write", "repo.projects": "none", "repo.pulls": "owner", "repo.releases": "none", "repo.wiki": "admin"}
        }
        req = self.request('POST', f'/orgs/{org}/teams', json=create_team_data)
        return req.json()

    def get_or_create_team(self, org, name, *args, **kwargs):
        self.get_or_create_org(org)
        team = self.team_exists(org, name)
        if not team:
            team = self.create_team(org, name, *args, **kwargs)
        return team

    def add_user_to_team(self, team_id, username):
        try:
            self.get_team_member(team_id, username)
        except Exception as err:
            if err.response.status_code == 404:
                self.add_team_member(team_id, username)

    def list_users(self):
        r = self.request('GET', f'/admin/users')
        return r.json()

    def get_user(self, email):
        # r = self.request('GET', f'/admin/users/email/{email}') ## not seem to be suported
        # return r.json()
        users = self.list_users()
        user = list(filter(lambda obj: obj['email'] == email, users))
        if len(user) == 0:
            return None
        return user[0]

    def create_user(self, email, username, password, name: str = None):
        data = {
            "email": email,
            "username": username,
            'password': password,
            # 'full_name': name,
            "must_change_password": False
        }
        if name:
            data['full_name'] = name
        r = self.request('POST', f'/admin/users', json=data)
        return r.json()

    def create_user_token(
            self,
            username,
            password,
            name: str = 'default',
            # scopes: list = ["repo","user"],
    ):
        data = {
            "name": name,
            # "scopes":scopes
        }
        auth = (username, password)
        r = self.request(
            'POST', f'/users/{username}/tokens', json=data, auth=auth)
        t = r.json()
        return utils.Dict2Obj(t)

    def get_or_create_user(self, email, username, password, name: str = None):
        user = self.get_user(email)
        if user:
            return user
        user = self.create_user(email, username, password, name)
        return user


gitea = Gitea()
