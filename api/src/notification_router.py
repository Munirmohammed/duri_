from typing import List
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from .core import  deps, schema, crud_utils, crud, tables

router = APIRouter()

@router.get("/notifications", response_model = List[schema.Notification], tags=['Notification'])
async def list_notifications(
    x_omic_userid: str = Header(..., description="the user-id from header"),
    db: Session = Depends(deps.get_db)
):
    auth_user = crud_utils.get_user(x_omic_userid)
    if not auth_user:
        raise HTTPException(status_code=400, detail="invalid authetication")
    crud_notification = crud.Notification(tables.Notification, db)
    notifications = crud_notification.get_latest()
    return notifications