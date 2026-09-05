"""GREEN tool: find nearby service centers. Mock data in V1, shaped like a real API response."""

_MOCK_CENTERS = [
    {
        "name": "Hyundai Authorized Service - Anna Nagar",
        "type": "authorized",
        "distance_km": 3.2,
        "rating": 4.5,
        "services": ["general_service", "tyre", "battery", "towing"],
        "estimated_cost": 4800,
        "available_slots": ["2026-09-06T10:00", "2026-09-06T15:00", "2026-09-07T09:30"],
    },
    {
        "name": "QuickFix Multi-Brand Garage",
        "type": "independent",
        "distance_km": 1.8,
        "rating": 4.1,
        "services": ["general_service", "tyre", "battery"],
        "estimated_cost": 3200,
        "available_slots": ["2026-09-06T11:00", "2026-09-07T14:00"],
    },
    {
        "name": "Hyundai Authorized Service - Velachery",
        "type": "authorized",
        "distance_km": 7.6,
        "rating": 4.6,
        "services": ["general_service", "tyre", "battery", "towing"],
        "estimated_cost": 5100,
        "available_slots": ["2026-09-08T10:00"],
    },
]


def find_service_centers(location: str, service_type: str) -> dict:
    matches = [c for c in _MOCK_CENTERS if service_type in c["services"]]
    return {
        "location": location,
        "service_type": service_type,
        "results": matches,
    }
