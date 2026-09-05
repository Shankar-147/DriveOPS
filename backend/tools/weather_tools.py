"""GREEN tool: weather forecast via Open-Meteo (geocoding + forecast)."""
import httpx

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(location: str, date: str) -> dict:
    try:
        geo_resp = httpx.get(GEOCODING_URL, params={"name": location, "count": 1}, timeout=15)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()
    except httpx.HTTPError as e:
        return {"error": f"Geocoding lookup failed: {e}"}

    results = geo_data.get("results")
    if not results:
        return {"error": f"Could not find location: {location}"}

    lat, lon = results[0]["latitude"], results[0]["longitude"]

    try:
        forecast_resp = httpx.get(
            FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode",
                "start_date": date,
                "end_date": date,
                "timezone": "auto",
            },
            timeout=15,
        )
        forecast_resp.raise_for_status()
        forecast_data = forecast_resp.json()
    except httpx.HTTPError as e:
        return {"error": f"Forecast lookup failed: {e}"}

    daily = forecast_data.get("daily", {})
    if not daily.get("time"):
        return {"error": f"No forecast available for {location} on {date}"}

    return {
        "location": location,
        "date": date,
        "temp_max_c": daily["temperature_2m_max"][0],
        "temp_min_c": daily["temperature_2m_min"][0],
        "precipitation_probability_max": daily["precipitation_probability_max"][0],
        "weathercode": daily["weathercode"][0],
    }
