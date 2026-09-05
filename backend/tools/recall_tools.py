"""GREEN tool: possible recalls via NHTSA (model-level match only, never VIN-confirmed)."""
import httpx

NHTSA_RECALLS_URL = "https://api.nhtsa.gov/recalls/recallsByVehicle"


def check_recalls(make: str, model: str, model_year: int) -> dict:
    try:
        resp = httpx.get(
            NHTSA_RECALLS_URL,
            params={"make": make, "model": model, "modelYear": model_year},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as e:
        return {"error": f"NHTSA recall lookup failed: {e}", "match_level": "model"}

    results = data.get("results", [])
    recalls = [
        {
            "component": r.get("Component"),
            "summary": r.get("Summary"),
            "consequence": r.get("Consequence"),
            "remedy": r.get("Remedy"),
            "report_date": r.get("ReportReceivedDate"),
        }
        for r in results
    ]

    return {
        "match_level": "model",
        "possible_recall_count": len(recalls),
        "recalls": recalls,
    }
