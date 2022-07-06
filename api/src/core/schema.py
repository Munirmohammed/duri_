from pydoc import describe
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


class PassportVisaToken(BaseModel):
    """
    see : 
        - https://github.com/ga4gh-duri/ga4gh-duri.github.io/blob/master/researcher_ids/ga4gh_passport_v1.md
        - https://github.com/ga4gh/data-security/blob/master/AAI/AAIConnectProfile.md#ga4gh-jwt-format
    """
    iss: str = Field(..., description='the issuer of this token')
    sub: str = Field(..., description='the user-id represented by this token')
    email: str = Field(..., description='the user email address')
    iat: int = Field(..., description='date-time when token was issued')
    exp: int = Field(..., description='date-time for token expiration')
    ga4gh_visa_v1: Optional[List[dict]] = Field(None, description='an list map of Passport Claims see https://github.com/ga4gh-duri/ga4gh-duri.github.io/blob/master/researcher_ids/ga4gh_passport_v1.md#passport-claim-format')
    
    