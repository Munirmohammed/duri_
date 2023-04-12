import os
#from starlette.datastructures import CommaSeparatedStrings, Secret
from pydantic import BaseSettings

class Settings(BaseSettings):
    api_version: str = "0.0.1"
    api_name: str = "duri"
    org_name: str = "omic.ai"
    api_description: str = "user identity and management"
    user_pool_client_secret: str
    user_pool_client_id: str
    user_pool_id: str
    user_pool_region: str
    passport_secret_key: str = 'deff1952d59f883ece260e8683fed21ab0ad9a53323eca4f'
    passport_algorithm: str = 'HS256'
    passport_token_expire_mins: int = 1440 ## 24 hours
    default_workspace: str = 'omic.ai'
    default_team: str = 'default'
    default_team_description: str = ''
    default_membership_type: str = 'contributor'
    super_admin: str = '9004ff5e-20bd-49dc-ba00-2f4dafac9940'
    deployment: str = 'local'
    duri_api_host:str="http://nucleus.omic.ai:9041"
    duri_ampq:str = 'amqp://rabbitmq:rabbitmq@duri_rabbitmq:5672'
settings = Settings()