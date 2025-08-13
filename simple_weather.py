
# simple_weather.py
import 
import time

# List of sample cities and weather conditions
cities = ["Tehran", "Shiraz", "Mashhad", "Isfahan", "Tabriz"]
conditions = ["☀ Sunny", "🌧 Rainy", "⛅ Cloudy", "🌩 Stormy", "❄ Snowy"]

print("🌍 Simple Weather Forecast Program\n")

for city in cities:
    weather = random.choice(conditions)
    temp = random.randint(-5, 40)
    print(f"{city}: {weather} | 🌡 Temp: {temp}°C")
    time.sleep(0.5)
