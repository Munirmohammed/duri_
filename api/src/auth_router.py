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

## User Authetication Routes

@router.post("/register", tags=["Auth"])
async def register():
    """
    Registers a new user
    """
    return None

@router.post("/login", tags=["Auth"])
async def login():
    """
    Initiates a user authetication flow
    """
    return None

@router.get("/verify", tags=["Auth"])
async def verify():
    """
    Finalizes user authetication flow  by verifying the login-link code sent to user email.
    It returns an Id token on success
    """
    return None

