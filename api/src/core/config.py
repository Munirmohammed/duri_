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
    

settings = Settings()