import requests

from src.tts.tts import speak
from src.core.config import settings


def weather(city: str = "Стамбул"):
    city = city.replace(' ', '').replace('.', '')
    
    url = "https://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "q": city,
        "units": "metric",
        "lang": "ru",
        "appid": settings.WEATHER_API_KEY,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        desc = data["weather"][0]["description"]

        speak(
            f"В городе {city} сейчас {temp:.0f} градусов. "
            f"Ощущается как {feels_like:.0f}. "
            f"На улице {desc}."
        )

    else:
        speak("Город не найден")