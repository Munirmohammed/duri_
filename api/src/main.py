#from mangum import Mangum
from fastapi import FastAPI, Depends
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from .core import  deps, migrate
from .core.config import settings
from .routes import router as api_router
from .auth_router import router as auth_router
from .workspace_router import router as workspace_router
from .user_router import router as user_router


app = FastAPI(
    title=settings.api_name,
    description=settings.api_description,
    version=settings.api_version,
)

@app.on_event("startup")
def startup():
    print('startup')
    migrate.migrate_workspaces() ## NOTE: activate this function when deploying
    

@app.on_event("shutdown")
async def shutdown():
    print('shutdown')

@app.get("/",)
def main():
    return RedirectResponse(url="/docs/")

app.include_router(api_router) # prefix=settings.API_V1_STR
app.include_router(auth_router)
app.include_router(workspace_router)
app.include_router(user_router)

handler = app
