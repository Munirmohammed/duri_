import os
import json
from datetime import datetime
from urllib.parse import urlparse
from pydantic import Json
from typing import Optional, List, Any, Dict, Union
from fastapi import APIRouter, Depends, Query, Path,  Form, File, UploadFile, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from .core import  deps, schema, crud, tables

router = APIRouter()

## Basic Routes

@router.get("/service-info", response_model=schema.ServiceInfo, tags=["discovery"])
async def service_info():
    """
    Show information about this service.
    """
    return schema.service_info_response

