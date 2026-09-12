🌦️ Weather App

A Python desktop weather application that allows users to search for a city and view its current weather and 3-day forecast.

✨ Features

🌍 Search weather by city name
🌡️ Current temperature
☁️ Current weather condition
💧 Humidity
 💨 Wind speed
 📅 3-day weather forecast
 🌡️ Celsius / Fahrenheit selection
 ⚡ 10-minute data caching
 ❌ Error handling for network and API errors
 🖥️ Graphical user interface built with Tkinter

🛠️ Built With

- Python
- Tkinter — GUI
- Requests — HTTP requests
- Open-Meteo Geocoding API — City coordinates
- Open-Meteo Weather API — Weather data

⭕ How to run on your system

Prerequisites
Make sure Python is installed on your system.

Installation

1. Clone the repository:

git clone <https://github.com/Henil9727/Weather-App.git>
cd Weather-App

2. Install the required dependency:

pip install -r requirements.txt

3. Run the application:

python Weather_checker.py


🔑 API Key

No API key is required.
This project uses the public Open-Meteo Geocoding and Weather APIs.


⚙️ How It Works

1. The user enters a city name.
2. The application sends the city name to the Open-Meteo Geocoding API.
3. The API returns the city's latitude and longitude.
4. These coordinates are sent to the Open-Meteo Weather API.
5. The application processes the returned weather data.
6. The current weather and 3-day forecast are displayed in the Tkinter interface.
7. Retrieved data is cached for 10 minutes to reduce repeated API requests.


⚠️ Notes

- An active internet connection is required.
- Weather data depends on the Open-Meteo service.
- Cached weather data may be up to 10 minutes old.