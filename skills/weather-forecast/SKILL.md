---
name: weather-forecast
display_name: "Weather Forecast"
description: "Fetch current weather conditions and multi-day forecasts for any city worldwide using the Open-Meteo API"
category: general
icon: cloud
skill_type: sandbox
catalog_type: addon
requirements: "httpx>=0.25"
tool_schema:
  name: weather-forecast
  description: "Fetch current weather conditions and multi-day forecasts for any city worldwide"
  parameters:
    type: object
    properties:
      action:
        type: "string"
        description: "Which operation to perform"
        enum: ["current", "forecast"]
      city:
        type: "string"
        description: "City name to get weather for (e.g. 'London', 'New York', 'Tokyo')"
        default: ""
      days:
        type: "integer"
        description: "Number of forecast days (1-16, only for forecast action)"
        default: 7
    required: [action, city]
---
# Weather Forecast

Get real-time weather conditions and multi-day forecasts for any city in the world. Uses the free Open-Meteo API — no API key required.

## Actions

### current
Get the current weather conditions for a city.
- **Parameters**: `action: "current"`, `city: "Paris"`
- **Returns**: temperature, feels-like, humidity, wind speed and direction, weather description, UV index, visibility, and local time.

### forecast
Get a daily weather forecast for up to 16 days.
- **Parameters**: `action: "forecast"`, `city: "Tokyo"`, `days: 7`
- **Returns**: daily high/low temperatures, precipitation sum, max wind speed, sunrise/sunset times, and weather description for each day.

## Usage Tips

- **Be Proactive**: If a user asks about weather without specifying a city, ask for their city or use context clues from the conversation.
- Always include temperature units (°C) and wind speed units (km/h) in your response for clarity.
- For forecast results, summarize the overall trend (e.g. "Rain expected Wednesday through Friday") rather than listing every day mechanically.
- If a city name is ambiguous (e.g. "Springfield"), use the most commonly known one and mention which country it resolved to.
- Pair weather info with helpful suggestions — e.g. umbrella advice for rain, SPF reminders for high UV, or coat suggestions for cold snaps.
---