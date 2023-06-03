from fastapi import Form, Depends
from pydantic import validator, BaseModel, Field, Json, UUID4
from typing import Optional, List, Type, NewType, Any, Dict, Union
from enum import Enum
from datetime import datetime
from .config import settings

class Ga4ghOrganization(BaseModel):
	name: str
	url: str

class Ga4ghServiceType(BaseModel):
	group: str
	artifact: str
	version: str

class ServiceInfo(BaseModel):
	id: str
	name: str
	type: Ga4ghServiceType
	description: str
	organization: Ga4ghOrganization
	contactUrl: str
	documentationUrl: str
	environment: str
	version: str
	class Config:
		schema_extra = {
			"example": {
				"id": "org.ga4gh.omic",
				"name": "omic",
				"type": {
						"group": "org.ga4gh",
						"artifact": "beacon",
						"version": "1.0.0"
				},
				"description": "user identity and management",
				"organization": {
					"name": "omic",
					"url": "https://omic.ai"
				},
				"organization": {
					"name": "omic",
					"url": "https://omic.ai"
				},
				"contactUrl": "mailto:support@omic.ai",
				"documentationUrl": "https://omic.ai",
				"environment": "production",
				"version": "2.0.0"
			}
		}

service_info_response = {
	"id": "org.ga4gh.omic",
	"name": "omic",
	"type": {
			"group": "org.ga4gh",
			"artifact": "beacon",
			"version": "1.0.0"
	},
	"description": "machine learning registry",
	"organization": {
		"name": "omic",
		"url": "https://omic.ai"
	},
	"organization": {
		"name": "omic",
		"url": "https://omic.ai"
	},
	"contactUrl": "mailto:support@omic.ai",
	"documentationUrl": "https://omic.ai",
	"environment": "production",
	"version": "2.0.0"
}

class WorkspaceBaseMini(BaseModel):
	id: Union[UUID4, str] = Field(..., description="id of the workspace")
	name: str = Field(..., description="name of the workspace")
	description: Optional[str] = Field(None, description="description of the workspace")
	active: bool = Field(...,description="if the workspace is active or disabled")
	class Config:
		orm_mode = True

class WorkspaceBase(WorkspaceBaseMini):
	# active: bool = Field(..., description="if the workspace is active or disabled")
	# description: Optional[str] = Field(None, description="description of the workspace")
	avatar: Optional[str] = Field(None, description="link to the workspace logo image")
	tags: Optional[List[str]] = Field(None, description="tag lebels")
	ui_customization: Optional[Dict[str, Any]] = Field(None, description="an object of ui customizable items for ui ie. the object would have entry `background_image` for background image of the cards")
	# created_at: Optional[datetime] = Field(None, description="the actual creation date")
	# updated_at: Optional[datetime] = Field(None, description="last update date")

class TeamBase(BaseModel):
	id: Union[UUID4, str] = Field(..., description="id of the team")
	name: str = Field(..., description="name of the team")
	active: bool = Field(..., description="if the team is active or disabled")
	description: Optional[str] = Field(None, description="description of the team")
	avatar: Optional[str] = Field(None, description="link to the team logo image")
	tags: Optional[List[str]] = Field(None, description="tag lebels")
	ui_customization: Optional[Dict[str, Any]] = Field(None, description="an object of ui customizable items for ui ie. the object would have entry `background_image` for background image of the cards")
	created_at: Optional[datetime] = Field(None, description="the actual creation date")
	updated_at: Optional[datetime] = Field(None, description="last update date")
	class Config:
		orm_mode = True

class UserBase(BaseModel):
	id: Union[UUID4, str] = Field(..., description="id of the user")
	email: str = Field(..., description="user email")
	username: str = Field(..., description="user username")
	# active_team_id: Optional[Union[UUID4, str]] = Field(None, description="the current active team id")
	created_at: Optional[datetime] = Field(None, description="the actual creation date")
	updated_at: Optional[datetime] = Field(None, description="last update date")
	class Config:
		orm_mode = True

class TeamInsert(BaseModel):
	name: str = Field(..., description="name of the team")
	workspace_id: Union[UUID4, str] = Field(..., description="workspace id")
	creator_id: Union[UUID4, str] = Field(..., description="the owner user-id")
	active: bool = Field(..., description="if the team is active or disabled")
	description: Optional[str] = Field(None, description="description of the team")
	avatar: Optional[str] = Field(None, description="link to the team logo image")
	tags: Optional[List[str]] = Field(None, description="tag lebels")
	ui_customization: Optional[Dict[str, Any]] = Field(None, description="an object of ui customizable items for ui ie. the object would have entry `background_image` for background image of the cards")
	class Config:
		orm_mode = True

class WorkspaceMini(WorkspaceBase):
	created_at: Optional[datetime] = Field(None, description="the actual creation date")
	updated_at: Optional[datetime] = Field(None, description="last update date")

class Workspace(WorkspaceBase):
	teams: List[TeamBase] = Field(None, description="this workspace teams")
	created_at: Optional[datetime] = Field(None, description="the actual creation date")
	updated_at: Optional[datetime] = Field(None, description="last update date")

class TeamMini(TeamBase):
	created_at: Optional[datetime] = Field(None, description="the actual creation date")
	updated_at: Optional[datetime] = Field(None, description="last update date")

class Team(TeamMini):
	workspace: WorkspaceBaseMini = Field(None, description="the workspace")

class UserWorkspace(BaseModel):
	user_id: Union[UUID4, str] = Field(None, description="the user_id")
	workspace_id: Union[UUID4, str] = Field(None, description="the workspace id")
	membership: str = Field(None, description="the workspace membership")
	created_at: Optional[datetime] = Field(None, description="the creation date")
	class Config:
		orm_mode = True

class UserTeam(BaseModel):
	user_id: Union[UUID4, str] = Field(None, description="the user_id")
	workspace_id: Union[UUID4, str] = Field(None, description="the workspace id")
	team_id: Union[UUID4, str] = Field(None, description="the team id")
	membership: str = Field(None, description="the team membership")
	created_at: Optional[datetime] = Field(None, description="the creation date")
	class Config:
		orm_mode = True

class UserWorkspaceAssoc(WorkspaceBase):
	membership: str = Field(None, description="the membership type")

class UserTeamAssoc(TeamBase):
	is_active: bool = Field(False, description="if this team is the current active user team")
	membership: str = Field(None, description="the membership type")
	workspace: str = Field(None, description="the workspace name")
	created_at: Optional[datetime] = Field(None, description="the actual creation date")
	updated_at: Optional[datetime] = Field(None, description="last update date")
	# workspace : WorkspaceMini = Field(None, description="the workspace")

# class GetUserWorkspace(UserWorkspace):
#    pass

class UserProfile(UserBase):
	team: TeamBase = Field(None, description="the current active team")
	workspace: WorkspaceBase = Field(None, description="the current active workspace")
	# teams: List[UserTeamAssoc] = Field(..., description="the user teams")

class PassportVisaToken(BaseModel):
	"""
	see : 
		- https://github.com/ga4gh-duri/ga4gh-duri.github.io/blob/master/researcher_ids/ga4gh_passport_v1.md
		- https://github.com/ga4gh/data-security/blob/master/AAI/AAIConnectProfile.md#ga4gh-jwt-format
		- (inspirational implementation: https://auth.nih.gov/docs/RAS/serviceofferings.html#AppendixA)
	"""
	iss: str = Field(..., description='the issuer of this token')
	sub: str = Field(..., description='the user-id represented by this token')
	email: str = Field(..., description='the user email address')
	iat: int = Field(..., description='date-time when token was issued')
	exp: int = Field(..., description='date-time for token expiration')
	# ga4gh_visa_v1: Optional[List[Dict[str, Any]]] = Field(None, description='an list map of Passport Claims see https://github.com/ga4gh-duri/ga4gh-duri.github.io/blob/master/researcher_ids/ga4gh_passport_v1.md#passport-claim-format')

class Notification(BaseModel):
	data: Dict[str, Any] = Field(..., description="message")
	workspace_id: Union[UUID4, str] = Field(..., description="workspace id")
	created_at: Optional[datetime] = Field(None, description="the actual creation date")

	class Config:
		orm_mode = True

class ResourceBase(BaseModel):
	id: Union[UUID4, str] = Field(..., description="resource id")
	name: str = Field(..., description="resource name")
	type: str = Field(..., description="resource type")
	provider: str = Field(..., description="resource provider")  # premi
	# name: Dict[str, Any] = Field(..., description="message")
	created_at: Optional[datetime] = Field(None, description="the creation date")

	class Config:
		orm_mode = True

class CredentialBase(BaseModel):
    id: Union[UUID4, str] = Field(..., description="resource id")
    resource_id: Union[UUID4, str] = Field(..., description="resource id")
    type: str
    store: str
    created_at: Optional[datetime] = Field(
        None, description="the creation date")
    
    class Config:
        orm_mode = True
    
class Resource(ResourceBase):
	pass

class ResourceCred(ResourceBase):
    credential: CredentialBase
    
class ResourceForm(BaseModel):
	name: str
	type: str
	provider: str
	user_id: Union[str,UUID4]
	meta: Dict[str, Any]

class CredentialsForm(BaseModel):
	resource_id: Union[str, UUID4]
	type: str
	store: bytes

class ComputeType(str, Enum):
	service = 'service'
	compute = 'compute'

class ProviderType(str, Enum):
	aws = 'aws'
	k8s = 'k8s'
	gitlab = 'gitlab'
	github = 'github'

class GitCredsDataSchema(BaseModel):
	access_token: str

class AwsSecretDataSchema(BaseModel):
	access_key: str
	secret_key: str

class AwsCrossAccountDataSchema(BaseModel):
	external_id: str
	role_arn: str
