import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "db", "driveops.db"))

from backend.tools import (  # noqa: E402
    document_tools,
    expense_tools,
    maintenance_tools,
    service_center_tools,
    vehicle_tools,
)
from backend.agent import tool_registry  # noqa: E402


def test_get_vehicle_profile():
    result = vehicle_tools.get_vehicle_profile("VH001")
    assert result["make"] == "Hyundai"
    assert result["model"] == "i20"


def test_check_maintenance_due():
    result = maintenance_tools.check_maintenance_due("VH001")
    assert result["status"] in ("ok", "due_soon", "overdue")
    assert result["km_remaining"] == result["next_service_km"] - result["odometer_km"]


def test_check_tyre_age():
    result = maintenance_tools.check_tyre_age("VH001")
    assert "tyre_age_years" in result
    assert result["status"] in ("ok", "worth_inspecting", "overdue")


def test_check_battery_age():
    result = maintenance_tools.check_battery_age("VH001")
    assert "battery_age_years" in result


def test_check_documents():
    docs = document_tools.check_documents("VH001")
    assert len(docs) == 3
    for d in docs:
        assert d["status"] in ("valid", "expiring_soon", "expired")


def test_calculate_expenses():
    result = expense_tools.calculate_expenses("VH001", period="all")
    assert result["count"] == 12
    assert result["total"] > 0
    assert "fuel" in result["by_category"]


def test_find_service_centers():
    result = service_center_tools.find_service_centers("Chennai", "general_service")
    assert len(result["results"]) > 0


def test_tool_registry_dispatch():
    assert tool_registry.is_yellow_tier("add_expense") is True
    assert tool_registry.is_yellow_tier("get_vehicle_profile") is False
    result = tool_registry.dispatch_tool("get_vehicle_profile", {"vehicle_id": "VH001"})
    assert result["make"] == "Hyundai"


def test_tool_registry_unknown_vehicle():
    result = tool_registry.dispatch_tool("get_vehicle_profile", {"vehicle_id": "NOPE"})
    assert "error" in result


def test_detect_expense_anomalies_via_registry():
    assert tool_registry.is_yellow_tier("detect_expense_anomalies") is False
    result = tool_registry.dispatch_tool("detect_expense_anomalies", {"vehicle_id": "VH001"})
    assert "anomalies" in result
    assert isinstance(result["anomalies"], list)


def test_breakdown_recovery_via_registry():
    assert tool_registry.is_yellow_tier("breakdown_recovery") is False
    result = tool_registry.dispatch_tool("breakdown_recovery", {"location": "Chennai"})
    assert "safety_guidance" in result and len(result["safety_guidance"]) > 0
    assert "towing_options" in result


if __name__ == "__main__":
    test_get_vehicle_profile()
    test_check_maintenance_due()
    test_check_tyre_age()
    test_check_battery_age()
    test_check_documents()
    test_calculate_expenses()
    test_find_service_centers()
    test_tool_registry_dispatch()
    test_tool_registry_unknown_vehicle()
    test_detect_expense_anomalies_via_registry()
    test_breakdown_recovery_via_registry()
    print("All tool tests passed.")
