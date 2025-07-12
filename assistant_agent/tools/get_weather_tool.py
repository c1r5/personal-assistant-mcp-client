import urllib.request
import json

# @title Define the get_weather Tool
def get_weather(city: str, days: int = 3) -> dict:
    """Retrieves the current weather report and a forecast for a specified city.

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").
        days (int): The number of days to forecast (e.g., 1, 2, 3). Defaults to 3.

    Returns:
        dict: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    print(f"--- Tool: get_weather called for city: {city} for {days} days ---")  # Log tool execution
    try:
        # Use wttr.in's JSON format for easier parsing
        url = f"https://wttr.in/{city.replace(' ', '%20')}?format=j1"
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                weather_data = json.loads(response.read().decode('utf-8'))
                
                # Current condition
                current_condition = weather_data.get('current_condition', [{}])[0]
                temp_c = current_condition.get('temp_C')
                feels_like_c = current_condition.get('FeelsLikeC')
                weather_desc = current_condition.get('weatherDesc', [{}])[0].get('value')
                humidity = current_condition.get('humidity')

                report = (
                    f"The current weather in {city} is {weather_desc.lower()} "
                    f"with a temperature of {temp_c}°C (feels like {feels_like_c}°C) "
                    f"and humidity of {humidity}%\n\n"
                )

                # Forecast
                report += "Forecast for the next few days:\n"
                forecast = weather_data.get('weather', [])
                for i in range(min(days, len(forecast))):
                    daily_forecast = forecast[i]
                    date = daily_forecast.get('date')
                    avg_temp_c = daily_forecast.get('avgtempC')
                    min_temp_c = daily_forecast.get('mintempC')
                    max_temp_c = daily_forecast.get('maxtempC')
                    hourly_desc = daily_forecast.get('hourly', [{}])[0].get('weatherDesc', [{}])[0].get('value')
                    
                    report += (
                        f"- {date}: {hourly_desc.lower()}, "
                        f"Avg Temp: {avg_temp_c}°C, "
                        f"Min: {min_temp_c}°C, "
                        f"Max: {max_temp_c}°C\n"
                    )

                return {
                    "status": "success",
                    "report": report,
                }
            else:
                error_message = f"Failed to retrieve weather data for '{city}'. Status code: {response.status}"
                if response.status == 404:
                    error_message = f"Sorry, I don't have weather information for '{city}'."
                return {
                    "status": "error",
                    "error_message": error_message,
                }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"An error occurred while fetching weather for '{city}': {e}",
        }