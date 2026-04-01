from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from db import client
from routes.auth import router as auth_router
from routes.jobs import router as jobs_router
from routes.coffre import router as coffre_router
from routes.observatoire import router as observatoire_router
from routes.evolution import router as evolution_router
from routes.passport import router as passport_router
from routes.cv import router as cv_router
from routes.explorer import router as explorer_router
from routes.ubuntoo import router as ubuntoo_router
from routes.seed import router as seed_router
from routes.emerging import router as emerging_router
from routes.siret import router as siret_router
from routes.scraper import router as scraper_router
from routes.dclic import router as dclic_router
from routes.partenaires import router as partenaires_router
from routes.workflow import router as workflow_router
from routes.trajectory import router as trajectory_router
from routes.coach import router as coach_router

app = FastAPI(title="Re'Actif Pro API")

cors_origins = os.environ.get("CORS_ORIGINS", "*")
if cors_origins == "*":
    origins = ["*"]
else:
    origins = [o.strip() for o in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(jobs_router)
api_router.include_router(coffre_router)
api_router.include_router(observatoire_router)
api_router.include_router(evolution_router)
api_router.include_router(passport_router)
api_router.include_router(cv_router)
api_router.include_router(explorer_router)
api_router.include_router(ubuntoo_router)
api_router.include_router(seed_router)
api_router.include_router(emerging_router)
api_router.include_router(siret_router)
api_router.include_router(scraper_router)
api_router.include_router(dclic_router)
api_router.include_router(partenaires_router)
api_router.include_router(workflow_router)
api_router.include_router(trajectory_router)
api_router.include_router(coach_router)

app.include_router(api_router)


@app.on_event("startup")
async def startup_init():
    try:
        from storage import init_storage
        init_storage()
    except Exception as e:
        import logging
        logging.warning(f"Storage init at startup: {e}")

# Serve frontend static build if present (for OVH single-server deployment)
frontend_build = os.path.join(os.path.dirname(__file__), "..", "frontend", "build")
frontend_static = os.path.join(frontend_build, "static")
if os.path.isdir(frontend_build) and os.path.isdir(frontend_static):
    from fastapi.responses import FileResponse

    app.mount("/static", StaticFiles(directory=frontend_static), name="static")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_build, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_build, "index.html"))


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
