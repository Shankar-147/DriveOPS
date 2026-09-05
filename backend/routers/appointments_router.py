from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend import db_access
from backend.tools import action_tools
from backend.tools.service_center_tools import find_service_centers

router = APIRouter(tags=["appointments"])


class AppointmentCreate(BaseModel):
    provider: str
    date: str
    service: str
    cost: float | None = None


@router.get("/api/vehicle/{vehicle_id}/appointments")
def get_appointments(vehicle_id: str):
    return db_access.get_appointments(vehicle_id)


@router.get("/api/vehicle/{vehicle_id}/service-centers")
def get_service_centers(vehicle_id: str, service_type: str = "general_service", location: str = "Chennai"):
    return find_service_centers(location, service_type)


@router.post("/api/vehicle/{vehicle_id}/appointments")
def create_appointment(vehicle_id: str, body: AppointmentCreate):
    # YELLOW tier: the website's confirm modal must have already gotten user
    # sign-off before this fires (Ch 6.1) - this endpoint performs the
    # write-then-verify pattern (Ch 6.2) itself.
    return action_tools.create_service_appointment(vehicle_id, body.provider, body.date, body.service, body.cost)


@router.get("/api/appointments/{appointment_id}")
def get_appointment(appointment_id: int):
    appt = db_access.get_appointment(appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt
