"""Breakdown Recovery Mode (Ch 8.4): triggered by phrases like "broke down."
Safety guidance first, then towing options only - never DIY repair instructions."""
from backend.tools.service_center_tools import find_service_centers

SAFETY_GUIDANCE = [
    "Move the vehicle to the roadside or a safe shoulder if it's still able to move.",
    "Turn on hazard lights immediately.",
    "Stay inside the vehicle if on a busy road or highway; exit only on the side away from traffic.",
    "Place a warning triangle or reflective marker behind the vehicle if you have one.",
    "If anyone is injured or the situation feels unsafe, call local emergency services first.",
]


def breakdown_recovery(location: str) -> dict:
    towing = find_service_centers(location, "towing")
    return {
        "safety_guidance": SAFETY_GUIDANCE,
        "towing_options": towing["results"],
        "note": "This mode only surfaces safety steps and towing contacts - it never provides DIY repair instructions.",
    }
