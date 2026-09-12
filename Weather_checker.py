import tkinter as tk
from tkinter import ttk, messagebox
import requests
import time


# SETTINGS 
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

CACHE_DURATION = 600  # 10 minutes

cache = {}


#  WEATHER CODES 

WEATHER_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    56: "Light Freezing Drizzle",
    57: "Dense Freezing Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    66: "Light Freezing Rain",
    67: "Heavy Freezing Rain",
    71: "Slight Snow",
    73: "Moderate Snow",
    75: "Heavy Snow",
    77: "Snow Grains",
    80: "Slight Rain Showers",
    81: "Moderate Rain Showers",
    82: "Violent Rain Showers",
    85: "Slight Snow Showers",
    86: "Heavy Snow Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Slight Hail",
    99: "Thunderstorm with Heavy Hail"
}


# API FUNCTIONS

def get_city_coordinates(city):
    """Find the coordinates of a city."""

    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    try:
        response = requests.get(
            GEOCODING_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("results"):
            return None

        location = data["results"][0]

        return {
            "name": location.get("name", city),
            "country": location.get("country", "Unknown"),
            "latitude": location["latitude"],
            "longitude": location["longitude"]
        }

    except requests.exceptions.Timeout:
        raise Exception("The location request timed out.")

    except requests.exceptions.ConnectionError:
        raise Exception("Network error. Please check your internet connection.")

    except requests.exceptions.RequestException:
        raise Exception("Unable to contact the location service.")

    except (ValueError, KeyError, TypeError):
        raise Exception("Received an invalid response from the location service.")


def get_weather(location, temperature_unit):
    """Get current weather and 3-day forecast."""

    unit = "celsius" if temperature_unit == "C" else "fahrenheit"

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],

        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "weather_code,"
            "wind_speed_10m"
        ),

        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min"
        ),

        "temperature_unit": unit,
        "wind_speed_unit": "kmh",
        "timezone": "auto",
        "forecast_days": 3
    }

    try:
        response = requests.get(
            WEATHER_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if "current" not in data or "daily" not in data:
            raise Exception("Weather service returned incomplete data.")

        return data

    except requests.exceptions.Timeout:
        raise Exception("Weather request timed out.")

    except requests.exceptions.ConnectionError:
        raise Exception("Network error. Please check your internet connection.")

    except requests.exceptions.HTTPError:
        raise Exception("Weather service returned an error.")

    except requests.exceptions.RequestException:
        raise Exception("Unable to contact the weather service.")

    except (ValueError, KeyError, TypeError):
        raise Exception("Received an invalid weather response.")


# CACHE

def get_cached_weather(city, temperature_unit):
    """Return cached weather if it is still valid."""

    key = (city.lower(), temperature_unit)

    if key not in cache:
        return None

    cached_data, cached_time = cache[key]

    if time.time() - cached_time < CACHE_DURATION:
        return cached_data

    del cache[key]

    return None


def save_to_cache(city, temperature_unit, data):
    """Save weather data in cache."""

    key = (city.lower(), temperature_unit)

    cache[key] = (data, time.time())


# WEATHER CONDITION

def get_weather_condition(code):
    """Convert weather code into readable text."""

    return WEATHER_CODES.get(code, "Unknown")


# GUI

def clear_weather():
    """Clear weather information."""

    location_label.config(text="Search for a city to see its weather.")

    temperature_label.config(text="--")
    condition_label.config(text="--")
    humidity_label.config(text="--")
    wind_label.config(text="--")

    for label in forecast_labels:
        label.config(text="--")


def display_weather(location, data, temperature_unit):
    """Display weather information in the GUI."""

    current = data["current"]
    daily = data["daily"]

    symbol = "°C" if temperature_unit == "C" else "°F"

    location_label.config(
        text=f"{location['name']}, {location['country']}"
    )

    temperature_label.config(
        text=f"{current['temperature_2m']}{symbol}"
    )

    condition_label.config(
        text=get_weather_condition(current["weather_code"])
    )

    humidity_label.config(
        text=f"{current['relative_humidity_2m']}%"
    )

    wind_label.config(
        text=f"{current['wind_speed_10m']} km/h"
    )

    for i in range(3):
        date = daily["time"][i]

        maximum = daily["temperature_2m_max"][i]
        minimum = daily["temperature_2m_min"][i]

        condition = get_weather_condition(
            daily["weather_code"][i]
        )

        forecast_text = (
            f"{date}\n"
            f"{condition}\n"
            f"↑ {maximum}{symbol}   ↓ {minimum}{symbol}"
        )

        forecast_labels[i].config(text=forecast_text)


def search_weather():
    """Search for weather when the Search button is clicked."""

    city = city_entry.get().strip()

    if not city:
        messagebox.showwarning(
            "Missing City",
            "Please enter a city name."
        )
        return

    temperature_unit = unit_var.get()

    search_button.config(state="disabled")
    status_label.config(text="Fetching weather data...")
    root.update_idletasks()

    try:
        # Check cache
        cached_data = get_cached_weather(
            city,
            temperature_unit
        )

        if cached_data:
            location = cached_data["location"]
            weather = cached_data["weather"]

            display_weather(
                location,
                weather,
                temperature_unit
            )

            status_label.config(
                text="Showing cached data."
            )

            return

        # Find city
        location = get_city_coordinates(city)

        if location is None:
            messagebox.showerror(
                "City Not Found",
                f"Could not find '{city}'.\n"
                "Please check the city name."
            )

            status_label.config(
                text="City not found."
            )

            return

        # Get weather
        weather = get_weather(
            location,
            temperature_unit
        )

        # Save to cache
        save_to_cache(
            city,
            temperature_unit,
            {
                "location": location,
                "weather": weather
            }
        )

        # Display result
        display_weather(
            location,
            weather,
            temperature_unit
        )

        status_label.config(
            text="Weather updated successfully."
        )

    except Exception as error:
        messagebox.showerror(
            "Weather Error",
            str(error)
        )

        status_label.config(
            text="Unable to retrieve weather."
        )

    finally:
        search_button.config(state="normal")


# WINDOW

root = tk.Tk()

root.title("Weather App")
root.geometry("700x650")
root.resizable(False, False)


# STYLES

style = ttk.Style()

style.configure(
    "Title.TLabel",
    font=("Arial", 24, "bold")
)

style.configure(
    "Location.TLabel",
    font=("Arial", 18, "bold")
)

style.configure(
    "Temperature.TLabel",
    font=("Arial", 36, "bold")
)

style.configure(
    "Info.TLabel",
    font=("Arial", 12)
)

style.configure(
    "Forecast.TLabel",
    font=("Arial", 10),
    justify="center"
)


# TITLE

title_label = ttk.Label(
    root,
    text="🌦️ WEATHER APP",
    style="Title.TLabel"
)

title_label.pack(pady=(25, 10))


subtitle_label = ttk.Label(
    root,
    text="Check current weather anywhere in the world"
)

subtitle_label.pack(pady=(0, 20))


# SEARCH AREA

search_frame = ttk.Frame(root)

search_frame.pack(pady=5)


ttk.Label(
    search_frame,
    text="City:"
).grid(row=0, column=0, padx=5)


city_entry = ttk.Entry(
    search_frame,
    width=30
)

city_entry.grid(row=0, column=1, padx=5)


unit_var = tk.StringVar(value="C")


ttk.Radiobutton(
    search_frame,
    text="°C",
    variable=unit_var,
    value="C"
).grid(row=0, column=2, padx=5)


ttk.Radiobutton(
    search_frame,
    text="°F",
    variable=unit_var,
    value="F"
).grid(row=0, column=3, padx=5)


search_button = ttk.Button(
    search_frame,
    text="Search",
    command=search_weather
)

search_button.grid(row=0, column=4, padx=10)


# STATUS

status_label = ttk.Label(
    root,
    text="Enter a city and click Search."
)

status_label.pack(pady=10)


# WEATHER INFORMATION

weather_frame = ttk.LabelFrame(
    root,
    text="Current Weather",
    padding=20
)

weather_frame.pack(
    fill="x",
    padx=40,
    pady=10
)


location_label = ttk.Label(
    weather_frame,
    text="Search for a city to see its weather.",
    style="Location.TLabel"
)

location_label.grid(
    row=0,
    column=0,
    columnspan=2,
    pady=(0, 10)
)


temperature_label = ttk.Label(
    weather_frame,
    text="--",
    style="Temperature.TLabel"
)

temperature_label.grid(
    row=1,
    column=0,
    rowspan=2,
    padx=30
)


ttk.Label(
    weather_frame,
    text="Condition:"
).grid(row=1, column=1, sticky="w")


condition_label = ttk.Label(
    weather_frame,
    text="--",
    style="Info.TLabel"
)

condition_label.grid(row=1, column=2, sticky="w", padx=10)


ttk.Label(
    weather_frame,
    text="Humidity:"
).grid(row=2, column=1, sticky="w")


humidity_label = ttk.Label(
    weather_frame,
    text="--",
    style="Info.TLabel"
)

humidity_label.grid(row=2, column=2, sticky="w", padx=10)


ttk.Label(
    weather_frame,
    text="Wind Speed:"
).grid(row=3, column=1, sticky="w")


wind_label = ttk.Label(
    weather_frame,
    text="--",
    style="Info.TLabel"
)

wind_label.grid(row=3, column=2, sticky="w", padx=10)


# FORECAST

forecast_frame = ttk.LabelFrame(
    root,
    text="3-Day Forecast",
    padding=15
)

forecast_frame.pack(
    fill="x",
    padx=40,
    pady=10
)


forecast_labels = []


for i in range(3):

    label = ttk.Label(
        forecast_frame,
        text="--",
        style="Forecast.TLabel",
        width=25
    )

    label.grid(
        row=0,
        column=i,
        padx=5
    )

    forecast_labels.append(label)


# START

city_entry.focus()

root.bind(
    "<Return>",
    lambda event: search_weather()
)

root.mainloop()