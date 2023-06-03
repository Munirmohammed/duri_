#from mangum import Mangum
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from .core import  deps ##, migrate
from .core.config import settings
from .routes import router as api_router
from .auth_router import router as auth_router
from .workspace_router import router as workspace_router
from .user_router import router as user_router
from .notification_router import router as notification_router
from .resource_router import router as resource_router
from .project_router import router as project_router
import asyncio
import aio_pika
from .events import consume

app = FastAPI(
	title=settings.api_name,
	description=settings.api_description,
	version=settings.api_version,
)

origins = [
	"*",
]

app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_methods=["GET", "POST"],
	allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
	pass
	""" connection = await aio_pika.connect_robust(
        settings.duri_ampq
    )
	app.state.rabbitmq_connection = connection
	channel = await connection.channel()
	result = await channel.declare_queue('', exclusive=True)
	exchange_name = 'aeb8b025-73db-4fd7-bb3e-d2bda0fddad6'
	exchange = await channel.declare_exchange(str(exchange_name), aio_pika.ExchangeType.TOPIC)
	await result.bind(exchange, routing_key="notification")
	asyncio.create_task(consume(result)) """

@app.on_event("shutdown")
async def shutdown():
	pass

@app.get("/",)
def main():
	return RedirectResponse(url="/docs/")

app.include_router(api_router) # prefix=settings.API_V1_STR
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(workspace_router)
app.include_router(project_router, tags=["projects"])
app.include_router(notification_router)
app.include_router(resource_router, tags=["resources"])

handler = app
