import os
import json
import httpx

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Icy fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow", 77: "Snow grains",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}


def geocode(city, timeout=15):
    with httpx.Client(timeout=timeout) as c:
        r = c.get(GEO_URL, params={"name": city, "count": 1, "language": "en", "format": "json"})
        if r.status_code >= 400:
            raise Exception(f"Geocoding API error {r.status_code}: {r.text[:300]}")
        data = r.json()
        results = data.get("results")
        if not results:
            raise Exception(f"City not found: '{city}'. Try a different spelling or add the country (e.g. 'Paris, France').")
        loc = results[0]
        return {
            "lat": loc["latitude"],
            "lon": loc["longitude"],
            "name": loc.get("name", city),
            "country": loc.get("country", ""),
            "timezone": loc.get("timezone", "UTC"),
        }


def fetch_weather(params, timeout=20):
    with httpx.Client(timeout=timeout) as c:
        r = c.get(WEATHER_URL, params=params)
        if r.status_code >= 400:
            raise Exception(f"Weather API error {r.status_code}: {r.text[:300]}")
        return r.json()


def do_current(inp):
    city = inp.get("city", "").strip()
    if not city:
        return {"error": "Provide a city name (e.g. 'London')"}

    loc = geocode(city)
    params = {
        "latitude": loc["lat"],
        "longitude": loc["lon"],
        "timezone": loc["timezone"],
        "current": [
            "temperature_2m", "apparent_temperature", "relative_humidity_2m",
            "wind_speed_10m", "wind_direction_10m", "weather_code",
            "uv_index", "visibility", "precipitation",
        ],
    }
    data = fetch_weather(params)
    cur = data.get("current", {})
    units = data.get("current_units", {})

    wmo = cur.get("weather_code", 0)
    return {
        "city": loc["name"],
        "country": loc["country"],
        "local_time": cur.get("time", ""),
        "condition": WMO_CODES.get(wmo, f"Code {wmo}"),
        "temperature_c": cur.get("temperature_2m"),
        "feels_like_c": cur.get("apparent_temperature"),
        "humidity_pct": cur.get("relative_humidity_2m"),
        "wind_speed_kmh": cur.get("wind_speed_10m"),
        "wind_direction_deg": cur.get("wind_direction_10m"),
        "precipitation_mm": cur.get("precipitation"),
        "uv_index": cur.get("uv_index"),
        "visibility_m": cur.get("visibility"),
    }


def do_forecast(inp):
    city = inp.get("city", "").strip()
    if not city:
        return {"error": "Provide a city name (e.g. 'Tokyo')"}
    days = max(1, min(int(inp.get("days", 7)), 16))

    loc = geocode(city)
    params = {
        "latitude": loc["lat"],
        "longitude": loc["lon"],
        "timezone": loc["timezone"],
        "forecast_days": days,
        "daily": [
            "weather_code", "temperature_2m_max", "temperature_2m_min",
            "apparent_temperature_max", "apparent_temperature_min",
            "precipitation_sum", "wind_speed_10m_max",
            "sunrise", "sunset",
        ],
    }
    data = fetch_weather(params)
    daily = data.get("daily", {})

    dates = daily.get("time", [])
    codes = daily.get("weather_code", [])
    t_max = daily.get("temperature_2m_max", [])
    t_min = daily.get("temperature_2m_min", [])
    feels_max = daily.get("apparent_temperature_max", [])
    feels_min = daily.get("apparent_temperature_min", [])
    precip = daily.get("precipitation_sum", [])
    wind = daily.get("wind_speed_10m_max", [])
    sunrise = daily.get("sunrise", [])
    sunset = daily.get("sunset", [])

    forecast_days = []
    for i, date in enumerate(dates):
        wmo = codes[i] if i < len(codes) else 0
        forecast_days.append({
            "date": date,
            "condition": WMO_CODES.get(wmo, f"Code {wmo}"),
            "temp_max_c": t_max[i] if i < len(t_max) else None,
            "temp_min_c": t_min[i] if i < len(t_min) else None,
            "feels_max_c": feels_max[i] if i < len(feels_max) else None,
            "feels_min_c": feels_min[i] if i < len(feels_min) else None,
            "precipitation_mm": precip[i] if i < len(precip) else None,
            "wind_speed_max_kmh": wind[i] if i < len(wind) else None,
            "sunrise": sunrise[i] if i < len(sunrise) else None,
            "sunset": sunset[i] if i < len(sunset) else None,
        })

    return {
        "city": loc["name"],
        "country": loc["country"],
        "timezone": loc["timezone"],
        "forecast_days": days,
        "forecast": forecast_days,
    }


try:
    inp = json.loads(os.environ.get("INPUT_JSON", "{}"))
    action = inp.get("action", "")

    if action == "current":
        result = do_current(inp)
    elif action == "forecast":
        result = do_forecast(inp)
    else:
        result = {"error": f"Unknown action: '{action}'. Choose from: current, forecast"}

    print(json.dumps(result))
except Exception as e:
    print(json.dumps({"error": str(e)}))