import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from backend.routers import (  # noqa: E402
    appointments_router,
    chat_router,
    documents_router,
    expenses_router,
    vehicle_router,
)

app = FastAPI(title="DriveOps")

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


@app.get("/health")
def health():
    return {"status": "ok"}
