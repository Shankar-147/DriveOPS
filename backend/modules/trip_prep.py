"""Trip Preparation Sub-Agent (Ch 8.3): combines maintenance/tyres/documents/weather
into a readiness percentage and an actionable checklist for a planned trip."""
from backend.tools.document_tools import check_documents
from backend.tools.maintenance_tools import check_battery_age, check_maintenance_due, check_tyre_age
from backend.tools.weather_tools import get_weather

_HEAVY_RAIN_THRESHOLD = 60


def prepare_trip(vehicle_id: str, distance_km: float, date: str, location: str = None) -> dict:
    readiness = 100
    checklist = []

    maint = check_maintenance_due(vehicle_id)
    if maint.get("status") == "overdue":
        readiness -= 25
        checklist.append("Service is overdue - get it done before this trip.")
    elif maint.get("status") == "due_soon":
        readiness -= 10
        checklist.append(f"Only {maint.get('km_remaining')}km left before your next service - consider servicing before you go.")

    tyres = check_tyre_age(vehicle_id)
    if tyres.get("status") == "overdue":
        readiness -= 25
        checklist.append("Tyres are overdue for replacement - do not take a long trip without replacing them.")
    elif tyres.get("status") == "worth_inspecting":
        readiness -= 10
        checklist.append(f"Tyres are {tyres.get('tyre_age_years')} years old - worth inspecting tread depth and pressure before departure.")

    battery = check_battery_age(vehicle_id)
    if battery.get("status") == "overdue":
        readiness -= 10
        checklist.append("Battery is worth inspecting before a long trip - it may be nearing end of life.")

    for doc in check_documents(vehicle_id):
        if doc["status"] == "expired":
            readiness -= 20
            checklist.append(f"{doc['type']} has expired - resolve before driving.")
        elif doc["status"] == "expiring_soon":
            readiness -= 5
            checklist.append(f"{doc['type']} expires in {doc['days_remaining']} days - keep it valid for the trip.")

    weather = None
    if location:
        weather = get_weather(location, date)
        if "error" not in weather:
            if weather.get("precipitation_probability_max", 0) >= _HEAVY_RAIN_THRESHOLD:
                readiness -= 5
                checklist.append(
                    f"High chance of rain in {location} on {date} "
                    f"({weather['precipitation_probability_max']}%) - check wipers and tyre tread for wet grip."
                )
        else:
            checklist.append(f"Could not fetch weather for {location}: {weather['error']}")

    if not checklist:
        checklist.append("No pre-trip concerns found - vehicle looks ready.")

    readiness = max(0, min(100, readiness))

    return {
        "vehicle_id": vehicle_id,
        "distance_km": distance_km,
        "date": date,
        "readiness_percent": readiness,
        "checklist": checklist,
        "weather": weather,
    }
