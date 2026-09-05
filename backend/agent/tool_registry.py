"""Tool schemas (OpenAI/OpenRouter function-calling format), tier tags, and dispatch."""
from backend.modules.health_score import compute_health_score
from backend.modules.trip_prep import prepare_trip
from backend.tools import (
    action_tools,
    document_tools,
    expense_tools,
    maintenance_tools,
    recall_tools,
    service_center_tools,
    vehicle_tools,
    weather_tools,
)

TOOL_TIERS = {
    "get_vehicle_profile": "GREEN",
    "update_odometer": "GREEN",
    "get_preferences": "GREEN",
    "check_maintenance_due": "GREEN",
    "check_tyre_age": "GREEN",
    "check_battery_age": "GREEN",
    "check_documents": "GREEN",
    "check_recalls": "GREEN",
    "get_weather": "GREEN",
    "find_service_centers": "GREEN",
    "calculate_expenses": "GREEN",
    "compute_health_score": "GREEN",
    "prepare_trip": "GREEN",
    "create_service_appointment": "YELLOW",
    "add_expense": "YELLOW",
    "schedule_reminder": "YELLOW",
}

_DISPATCH = {
    "get_vehicle_profile": vehicle_tools.get_vehicle_profile,
    "update_odometer": vehicle_tools.update_odometer,
    "get_preferences": vehicle_tools.get_preferences,
    "check_maintenance_due": maintenance_tools.check_maintenance_due,
    "check_tyre_age": maintenance_tools.check_tyre_age,
    "check_battery_age": maintenance_tools.check_battery_age,
    "check_documents": document_tools.check_documents,
    "check_recalls": recall_tools.check_recalls,
    "get_weather": weather_tools.get_weather,
    "find_service_centers": service_center_tools.find_service_centers,
    "calculate_expenses": expense_tools.calculate_expenses,
    "compute_health_score": compute_health_score,
    "prepare_trip": prepare_trip,
    "create_service_appointment": action_tools.create_service_appointment,
    "add_expense": action_tools.add_expense,
    "schedule_reminder": action_tools.schedule_reminder,
}


def is_yellow_tier(name: str) -> bool:
    return TOOL_TIERS.get(name) == "YELLOW"


def dispatch_tool(name: str, args: dict):
    fn = _DISPATCH.get(name)
    if fn is None:
        return {"error": f"Unknown tool: {name}"}
    call_args = {k: v for k, v in args.items() if k != "confirmed"}
    try:
        return fn(**call_args)
    except TypeError as e:
        return {"error": f"Invalid arguments for {name}: {e}"}


ALL_TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_vehicle_profile",
            "description": "Get the full profile of a vehicle: make, model, year, odometer, service/tyre/battery dates.",
            "parameters": {
                "type": "object",
                "properties": {"vehicle_id": {"type": "string"}},
                "required": ["vehicle_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_odometer",
            "description": "Update the vehicle's current odometer reading in kilometers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vehicle_id": {"type": "string"},
                    "km": {"type": "integer"},
                },
                "required": ["vehicle_id", "km"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_preferences",
            "description": "Get the owner's stored preferences for this vehicle (preferred service center type, max amount to auto-approve, preferred days). Use these to tailor recommendations.",
            "parameters": {
                "type": "object",
                "properties": {"vehicle_id": {"type": "string"}},
                "required": ["vehicle_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_maintenance_due",
            "description": "Check whether the vehicle's next general service is overdue, due soon, or ok, based on odometer.",
            "parameters": {
                "type": "object",
                "properties": {"vehicle_id": {"type": "string"}},
                "required": ["vehicle_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_tyre_age",
            "description": "Check the age of the vehicle's tyres and whether they are worth inspecting or overdue for replacement.",
            "parameters": {
                "type": "object",
                "properties": {"vehicle_id": {"type": "string"}},
                "required": ["vehicle_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_battery_age",
            "description": "Check the age of the vehicle's battery and whether it is worth inspecting or overdue for replacement.",
            "parameters": {
                "type": "object",
                "properties": {"vehicle_id": {"type": "string"}},
                "required": ["vehicle_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_documents",
            "description": "Check expiry status (valid/expiring_soon/expired) of all documents (insurance, PUC, RC) for the vehicle.",
            "parameters": {
                "type": "object",
                "properties": {"vehicle_id": {"type": "string"}},
                "required": ["vehicle_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_recalls",
            "description": "Check for possible recalls matching this make/model/year via NHTSA. Model-level match only, never VIN-confirmed - always describe results as 'possible recalls'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "make": {"type": "string"},
                    "model": {"type": "string"},
                    "model_year": {"type": "integer"},
                },
                "required": ["make", "model", "model_year"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the weather forecast for a location on a specific date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "date": {"type": "string", "description": "YYYY-MM-DD"},
                },
                "required": ["location", "date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_service_centers",
            "description": "Find nearby service centers offering a given service type (e.g. general_service, tyre, battery, towing).",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "service_type": {"type": "string"},
                },
                "required": ["location", "service_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_expenses",
            "description": "Calculate total and by-category expenses for a vehicle over a period ('month', 'year', or 'all').",
            "parameters": {
                "type": "object",
                "properties": {
                    "vehicle_id": {"type": "string"},
                    "period": {"type": "string", "enum": ["month", "year", "all"]},
                },
                "required": ["vehicle_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compute_health_score",
            "description": "Compute the vehicle's overall health score (0-100, weighted composite of maintenance/tyres/battery/documents/recall) with a breakdown. Frame as 'worth inspecting', never a mechanical diagnosis.",
            "parameters": {
                "type": "object",
                "properties": {"vehicle_id": {"type": "string"}},
                "required": ["vehicle_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prepare_trip",
            "description": "Combine maintenance, tyre, document, and (if location given) weather checks into a trip readiness percentage and checklist for a planned drive.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vehicle_id": {"type": "string"},
                    "distance_km": {"type": "number"},
                    "date": {"type": "string", "description": "YYYY-MM-DD"},
                    "location": {"type": "string", "description": "Optional. Needed to include a weather check."},
                },
                "required": ["vehicle_id", "distance_km", "date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_service_appointment",
            "description": "YELLOW TIER. Book a service appointment. Requires explicit user confirmation (confirmed=true) before it will actually execute.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vehicle_id": {"type": "string"},
                    "provider": {"type": "string"},
                    "date": {"type": "string", "description": "YYYY-MM-DD or ISO datetime"},
                    "service": {"type": "string"},
                    "cost": {"type": "number"},
                    "confirmed": {"type": "boolean", "description": "Must be true, set only after explicit user confirmation."},
                },
                "required": ["vehicle_id", "provider", "date", "service"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_expense",
            "description": "YELLOW TIER. Record a new expense for the vehicle. Requires explicit user confirmation (confirmed=true) before it will actually execute.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vehicle_id": {"type": "string"},
                    "date": {"type": "string", "description": "YYYY-MM-DD"},
                    "category": {"type": "string"},
                    "amount": {"type": "number"},
                    "description": {"type": "string"},
                    "confirmed": {"type": "boolean", "description": "Must be true, set only after explicit user confirmation."},
                },
                "required": ["vehicle_id", "date", "category", "amount"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_reminder",
            "description": "YELLOW TIER. Schedule a future maintenance reminder for the vehicle. Requires explicit user confirmation (confirmed=true) before it will actually execute.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vehicle_id": {"type": "string"},
                    "task": {"type": "string"},
                    "due_km": {"type": "integer"},
                    "due_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "confirmed": {"type": "boolean", "description": "Must be true, set only after explicit user confirmation."},
                },
                "required": ["vehicle_id", "task"],
            },
        },
    },
]
