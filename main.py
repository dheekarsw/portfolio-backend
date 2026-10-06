from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import init_database
from routers.profile import router as profile_router
from routers.experience import router as experience_router
from routers.project import router as project_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database()
    yield


app = FastAPI(
    title="Portfolio API",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {
        "message": "Portfolio API is running"
    }


app.include_router(profile_router)
app.include_router(experience_router)
app.include_router(project_router)