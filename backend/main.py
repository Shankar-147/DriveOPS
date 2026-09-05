import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from backend import db_access  # noqa: E402
from backend.routers import (  # noqa: E402
    appointments_router,
    chat_router,
    documents_router,
    expenses_router,
    vehicle_router,
)
from backend.scheduler import start_scheduler  # noqa: E402

app = FastAPI(title="DriveOps")
_scheduler_handle = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS_ORIGIN", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vehicle_router.router)
app.include_router(chat_router.router)
app.include_router(documents_router.router)
app.include_router(expenses_router.router)
app.include_router(appointments_router.router)


@app.on_event("startup")
def on_startup():
    global _scheduler_handle
    vehicle_ids = db_access.list_vehicle_ids()
    if vehicle_ids:
        _scheduler_handle = start_scheduler(vehicle_ids)


@app.on_event("shutdown")
def on_shutdown():
    if _scheduler_handle:
        _scheduler_handle.shutdown(wait=False)


@app.get("/health")
def health():
    return {"status": "ok"}
