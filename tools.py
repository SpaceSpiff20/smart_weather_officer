from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timedelta, timezone
import streamlit as st
import plotly.graph_objects as go
import pandas as pd


load_dotenv()
weather_api = os.getenv('openweather_api')

#current weather
def get_weather(city: str) -> dict:
    '''Takes a city name and returns associated current weather details.'''
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'appid': weather_api,
        'q': city,
        'units': 'metric'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        if response.status_code == 200:
            weather_data = response.json()
            report = (
                f"📍 CITY: {weather_data['name']}\n"
                f"🌡️ TEMPERATURE: {weather_data['main']['temp']}°C\n"
                f"🤗 FEELS LIKE: {weather_data['main']['feels_like']}°C\n"
                f"📈 PRESSURE: {weather_data['main']['pressure']} hPa\n"
                f"🌥️ CONDITIONS: {weather_data['weather'][0]['description'].capitalize()}\n"
                f"👁️ VISIBILITY: {weather_data['visibility']} m\n"
                f"💧 HUMIDITY: {weather_data['main']['humidity']}%\n"
                f"💨 WIND: {weather_data['wind']['speed']} km/h"
            )
            readable = (
                f"The current weather in {weather_data['name']} is {weather_data['weather'][0]['description'].capitalize()}, "
                f"with a temperature of {weather_data['main']['temp']}°C, feeling like {weather_data['main']['feels_like']}°C. "
                f"Humidity is at {weather_data['main']['humidity']}%, and the air pressure is {weather_data['main']['pressure']} hPa. "
                f"Visibility is around {int(weather_data['visibility'] / 1000)} km, and winds are blowing at "
                f"{weather_data['wind']['speed']} km/h."
            )
            return {
                "report": report,
                "readable": readable
            }
        else:
            st.error("error fetching current weather")
            return {"report": "error getting current weather"}
            
    except requests.exceptions.RequestException as e:
        print(f"Weather API error: {str(e)}")
        st.error("error fetching current weather")
        return {"report": "error getting current weather"}
    

#forecast
def get_forecast(city: str) -> dict:
    """
    Fetch 5-day forecast (3-hour intervals) for the specified city.
    Returns JSON dict or raises an exception.
    """
    url = 'http://api.openweathermap.org/data/2.5/forecast'
    params = {
        'appid': weather_api,
        'q': city,
        'units': 'metric'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        forecast_list = data.get("list", [])
        parsed_forecast = []
        readable_lines = []

        for entry in forecast_list:
            dt = datetime.fromtimestamp(entry['dt']).strftime("%a %d %b %I:%M %p")
            temp = entry['main']['temp']
            desc = entry['weather'][0]['description'].capitalize()
            wind = entry['wind']['speed']
            humidity = entry['main']['humidity']

            item = {
                "datetime": dt,
                "temp": temp,
                "description": desc,
                "wind": wind,
                "humidity": humidity
            }

            parsed_forecast.append(item)
            readable_lines.append(
                f"{dt}: {desc}, {temp}°C, Wind {wind} m/s, Humidity {humidity}%"
            )

        return {
            "raw": data,
            "parsed": parsed_forecast,
            "string": "\n".join(readable_lines)
        }
    except requests.exceptions.RequestException as e:
        print(f"Forecast API error: {str(e)}")
        st.error("error fetching forecast weather")
        return {}



#graph
def plot_forecast_graph(parsed_list, limit=40, key="forecast_plot"):
 

    df = pd.DataFrame(parsed_list[:limit])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["datetime"],
        y=df["temp"],
        mode='lines+markers',
        name='Temperature (°C)',
        line=dict(color='orange')
    ))

    fig.add_trace(go.Scatter(
        x=df["datetime"],
        y=df["humidity"],
        mode='lines',
        name='Humidity (%)',
        line=dict(color='blue', dash='dot')
    ))

    fig.add_trace(go.Scatter(
        x=df["datetime"],
        y=df["wind"],
        mode='lines',
        name='Wind Speed (m/s)',
        line=dict(color='green', dash='dash')
    ))

    fig.update_layout(
        title="📈 Weather Forecast Trends",
        xaxis_title="Date & Time",
        yaxis_title="Values",
        hovermode="x unified",
        template="plotly_white",
        autosize=True,
        margin=dict(l=20, r=20, t=40, b=20),
        height=450
    )

    st.markdown("### 📊 Forecast Graph")
    st.plotly_chart(fig, use_container_width=True, key=key)



#current date time
def get_time_and_date(city: str) -> str:
    """
    Returns the current local time and date for a given city 
    """
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api}"
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200 or "dt" not in data:
            return f"Sorry, I couldn't retrieve the time for {city}. Please check the city name."

        # UTC timestamp and timezone offset (in seconds)
        utc_timestamp = data["dt"]
        timezone_offset = data["timezone"]

        # Create UTC datetime (timezone-aware)
        utc_dt = datetime.fromtimestamp(utc_timestamp, tz=timezone.utc)

        # Add offset to get local time
        local_dt = utc_dt + timedelta(seconds=timezone_offset)
        formatted_time = local_dt.strftime("%A, %B %d, %Y at %I:%M %p")

        return f"The current date and time in {city} is {formatted_time}."
    
    except Exception as e:
        
        return f"An error occurred while fetching time and date for {city}: {str(e)}"
        