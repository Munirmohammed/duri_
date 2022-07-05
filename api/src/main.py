#from mangum import Mangum
from fastapi import FastAPI
from starlette.responses import RedirectResponse
from .core.config import settings
from .routes import router as api_router

app = FastAPI(
    title=settings.api_name,
    description=settings.api_description,
    version=settings.api_version,
)

@app.on_event("startup")
async def startup():
    print('startup')

@app.on_event("shutdown")
async def shutdown():
    print('shutdown')

@app.get("/",)
def main():
    return RedirectResponse(url="/docs/")

app.include_router(api_router) # prefix=settings.API_V1_STR

handler = app
