"""
Live Weather Information Module for ArnavSharma_Task1.
Integrates OpenWeatherMap API to fetch real-time weather, temperature, humidity,
and atmospheric conditions with graceful error and credential handling.
"""

import os
from typing import Any, Dict, Optional, Tuple
import requests

from utils.logger import get_logger

logger = get_logger("Weather")


class WeatherService:
    """Fetches real-time weather information from OpenWeatherMap API."""

    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_city: str = "Kolkata",
        units: str = "metric",
    ):
        # Prefer parameter, then environment variable
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY", "").strip()
        self.default_city = default_city
        self.units = units

    def set_api_key(self, api_key: str) -> None:
        """Dynamically updates the OpenWeatherMap API key."""
        self.api_key = api_key.strip()

    def get_weather(self, city: Optional[str] = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Retrieves real-time weather for the requested city.

        Args:
            city: Name of the city (optional; falls back to default_city).

        Returns:
            Tuple of (success, spoken_response_string, data_dictionary)
        """
        target_city = (city or self.default_city).strip()

        # Handle missing or placeholder API key
        if not self.api_key or self.api_key == "your_openweathermap_api_key_here":
            msg = (
                f"OpenWeatherMap API key is not configured. "
                f"To get live weather for {target_city}, please obtain a free API key "
                f"from openweathermap.org and add it as OPENWEATHER_API_KEY in your .env file."
            )
            logger.warning("Weather requested but OPENWEATHER_API_KEY is not configured.")
            return False, msg, None

        params = {
            "q": target_city,
            "appid": self.api_key,
            "units": self.units,
        }

        try:
            logger.info(f"Querying weather for '{target_city}'...")
            response = requests.get(self.BASE_URL, params=params, timeout=6.0)

            if response.status_code == 200:
                data = response.json()
                weather_info = self._parse_weather_response(data, target_city)
                logger.info(f"Weather fetched successfully for '{target_city}'.")
                return True, weather_info["speech"], weather_info

            elif response.status_code == 404:
                msg = f"I could not find weather information for '{target_city}'. Please verify the city name."
                logger.info(f"Weather city not found: {target_city}")
                return False, msg, None

            elif response.status_code == 401:
                msg = (
                    "The OpenWeatherMap API key appears to be invalid or unauthorized. "
                    "Please check your API key in the .env file."
                )
                logger.error("Invalid OpenWeatherMap API key (401 Unauthorized).")
                return False, msg, None

            else:
                msg = f"Weather service returned an unexpected status code {response.status_code}."
                logger.error(msg)
                return False, msg, None

        except requests.Timeout:
            msg = f"The weather request for {target_city} timed out. Please try again in a moment."
            logger.error(f"Weather request timeout for {target_city}")
            return False, msg, None

        except requests.RequestException as req_err:
            msg = "Unable to connect to the weather service. Please check your internet connection."
            logger.error(f"Weather connection error: {req_err}")
            return False, msg, None

        except Exception as err:
            msg = f"An unexpected error occurred while fetching the weather: {err}"
            logger.error(msg)
            return False, msg, None

    def _parse_weather_response(self, data: Dict[str, Any], requested_city: str) -> Dict[str, Any]:
        """Parses raw OpenWeatherMap JSON response into structured summary and natural speech."""
        main_data = data.get("main", {})
        weather_list = data.get("weather", [{}])
        wind_data = data.get("wind", {})
        sys_data = data.get("sys", {})

        city_name = data.get("name", requested_city)
        country = sys_data.get("country", "")

        temp = round(main_data.get("temp", 0.0), 1)
        feels_like = round(main_data.get("feels_like", 0.0), 1)
        humidity = main_data.get("humidity", 0)
        pressure = main_data.get("pressure", 0)

        # Weather description
        description = weather_list[0].get("description", "clear") if weather_list else "clear"

        # Wind speed (m/s converted to km/h for metric)
        wind_speed_ms = wind_data.get("speed", 0.0)
        wind_speed_kmh = round(wind_speed_ms * 3.6, 1) if self.units == "metric" else wind_speed_ms

        unit_symbol = "degrees Celsius" if self.units == "metric" else "degrees Fahrenheit"
        wind_unit = "kilometers per hour" if self.units == "metric" else "miles per hour"

        # Natural conversational readout matching prompt requirements:
        # "The current weather in Kolkata is 27 degrees Celsius with clear skies."
        speech = (
            f"The current weather in {city_name} is {temp} {unit_symbol} with {description}. "
            f"It feels like {feels_like} {unit_symbol}, with a humidity of {humidity} percent "
            f"and wind speed of {wind_speed_kmh} {wind_unit}."
        )

        return {
            "city": city_name,
            "country": country,
            "temp": temp,
            "feels_like": feels_like,
            "description": description,
            "humidity": humidity,
            "pressure": pressure,
            "wind_speed": wind_speed_kmh,
            "speech": speech,
        }

