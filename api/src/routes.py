import os
import json
from datetime import datetime
from urllib.parse import urlparse
from pydantic import UUID4
from typing import Optional, List, Any, Dict, Union
from fastapi import APIRouter, Depends, Request, Query, Path,  Form, File, UploadFile, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from .core import  deps, schema, common, tables
from .core.config import settings
import aio_pika
import asyncio
from sse_starlette.sse import EventSourceResponse

router = APIRouter()

async def generate_sse(request,user):
    connection = await aio_pika.connect_robust(
        settings.duri_ampq
    )
    channel = await connection.channel()
    result = await channel.declare_queue('', exclusive=True)
    exchange_name = user['workspace']['id']
    exchange = await channel.declare_exchange(str(exchange_name), aio_pika.ExchangeType.TOPIC)
    await result.bind(exchange, routing_key="notification")
    async with result.iterator() as queue_iter:
        while True:
            if await request.is_disconnected():
                break
            async for message in queue_iter:
                if message:
                    yield f"data: {message.body.decode()}\n\n"
                else:
                    await asyncio.sleep(1)
    await channel.close()
    await connection.close()
## Basic Routes

@router.get("/service-info", response_model=schema.ServiceInfo, tags=["discovery"])
async def service_info():
    """
    Show information about this service.
    """
    return schema.service_info_response

@router.get("/stream")
async def stream_mess(
    request: Request,
    user: schema.UserProfile = Depends(common.user_from_query)
):
    return EventSourceResponse(generate_sse(request, user))