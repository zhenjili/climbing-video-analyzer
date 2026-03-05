from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import tasks

settings.upload_dir.mkdir(exist_ok=True)
settings.output_dir.mkdir(exist_ok=True)

app = FastAPI(title="Climbing Video Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory=str(settings.output_dir)), name="outputs")

app.include_router(tasks.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
