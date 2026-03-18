from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
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

app = FastAPI(title="Re'Actif Pro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

app.include_router(api_router)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
