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

## Workspaces management Routes

@router.get("/workspace", tags=["Workspace"])
async def list_workspace():
    """
    List all available workspaces
    """
    return None

@router.post("/workspace", tags=["Workspace"])
async def create_workspace():
    """
    Creates a new workspace
    """
    return None
