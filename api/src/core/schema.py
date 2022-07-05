from fastapi import Form, Depends
from pydantic import validator, BaseModel, Field, Json, UUID4
from typing import Optional, List, Type, NewType, Any, Dict, Union
from enum import Enum
from datetime import datetime
from .config import settings

class Organization(BaseModel):
    name: str
    url: str

class InfoOrgType(BaseModel):
    group: str
    artifact: str
    version: str

class ServiceInfo(BaseModel):
    id: str
    name: str
    type: InfoOrgType
    description: str
    organization: Organization
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
