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
    

settings = Settings()